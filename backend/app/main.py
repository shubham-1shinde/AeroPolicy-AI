
import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.router import api_router
from app.rag.engine import RAGEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("aeropolicy")


async def initialize_policy_index(app: FastAPI):
    """Initialize the RAG engine in a background thread."""
    engine = RAGEngine()
    started_at = time.perf_counter()

    app.state.policy_initialization_finished = False
    app.state.policy_initialization_error = None

    logger.info(
        "BACKGROUND_INIT: START engine_id=%s model=%s",
        id(engine),
        settings.EMBEDDING_MODEL_NAME,
    )

    try:
        success = await asyncio.to_thread(
            engine.initialize_on_startup
        )

        if success and engine.is_ready:
            logger.info(
                "BACKGROUND_INIT: SUCCESS engine_id=%s "
                "ready=%s chunks=%d elapsed=%.2fs",
                id(engine),
                engine.is_ready,
                len(engine.vectorstore.chunks),
                time.perf_counter() - started_at,
            )
        else:
            message = (
                "Policy index initialization returned without "
                "a ready engine."
            )
            app.state.policy_initialization_error = message

            logger.error(
                "BACKGROUND_INIT: NOT_READY engine_id=%s "
                "ready=%s chunks=%d elapsed=%.2fs",
                id(engine),
                engine.is_ready,
                len(engine.vectorstore.chunks),
                time.perf_counter() - started_at,
            )

    except Exception as exc:
        app.state.policy_initialization_error = str(exc)

        logger.exception(
            "BACKGROUND_INIT: FAILED engine_id=%s elapsed=%.2fs",
            id(engine),
            time.perf_counter() - started_at,
        )

    finally:
        app.state.policy_initialization_finished = True

        logger.info(
            "BACKGROUND_INIT: FINISHED engine_id=%s ready=%s "
            "elapsed=%.2fs",
            id(engine),
            engine.is_ready,
            time.perf_counter() - started_at,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AeroPolicy AI backend service.")

    engine = RAGEngine()
    app.state.rag_engine = engine
    app.state.policy_initialization_finished = False
    app.state.policy_initialization_error = None

    logger.info(
        "APP_STARTUP: RAGEngine instance_id=%s ready=%s",
        id(engine),
        engine.is_ready,
    )

    initialization_task = asyncio.create_task(
        initialize_policy_index(app),
        name="policy-index-initialization",
    )
    app.state.policy_initialization_task = initialization_task

    try:
        yield
    finally:
        logger.info("Shutting down AeroPolicy AI backend service.")

        if not initialization_task.done():
            logger.warning(
                "APP_SHUTDOWN: Policy initialization is still running."
            )

            # Do not cancel asyncio.to_thread work and assume the
            # underlying thread has stopped.
            try:
                await initialization_task
            except Exception:
                logger.exception(
                    "APP_SHUTDOWN: Initialization task failed."
                )

        logger.info("APP_SHUTDOWN: Complete.")


app = FastAPI(
    title="AeroPolicy AI — Airline Policy Assistant",
    description=(
        "Production-grade policy assistant implementing "
        "strict anti-hallucination safeguards."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

origins = [
    "https://aero-policy-ai.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

configured_origin = settings.FRONTEND_ORIGIN.rstrip("/")

if configured_origin and configured_origin not in origins:
    origins.append(configured_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        "Unhandled exception during %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred."
        },
    )


app.include_router(api_router)


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "service": "AeroPolicy AI Backend",
        "brand": "AeroVista Airlines",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.api_route("/health", methods=["GET", "HEAD"])
async def root_health():
    """Direct root health check responding to both GET and HEAD for Render probes."""
    return {"status": "healthy"}


@app.get("/api/diagnostics/initialization")
async def initialization_diagnostics():
    """Report runtime initialization state without exposing secrets."""
    engine = app.state.rag_engine

    return {
        "engine_instance_id": id(engine),
        "is_ready": engine.is_ready,
        "is_indexing": engine.is_indexing,
        "chunks_loaded_in_memory": len(engine.vectorstore.chunks),
        "initialization_finished": (
            app.state.policy_initialization_finished
        ),
        "initialization_error": (
            app.state.policy_initialization_error
        ),
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
    }
