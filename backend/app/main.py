
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.router import api_router
from app.rag.engine import RAGEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("aeropolicy")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AeroPolicy AI backend service...")

    engine = RAGEngine()

    try:
        success = engine.initialize_on_startup()

        if success:
            logger.info("AeroVista Airlines policy index successfully initialized.")
        else:
            logger.warning(
                "Policy index initialization reported non-ready state. "
                "Check policy files."
            )
    except Exception:
        logger.exception("Startup indexing error")

    yield

    logger.info("Shutting down AeroPolicy AI backend service.")


app = FastAPI(
    title="AeroPolicy AI — Airline Policy Assistant",
    description=(
        "Production-grade policy assistant implementing "
        "strict anti-hallucination safeguards."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: explicitly allow the deployed Vercel frontend.
origins = [
    "https://aero-policy-ai.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Include the configured frontend origin if it is different.
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
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception during %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "An internal server error occurred. "
                "Please contact system administrator."
            )
        },
    )


app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "service": "AeroPolicy AI Backend",
        "brand": "AeroVista Airlines",
        "docs": "/docs",
        "health": "/api/health",
    }
