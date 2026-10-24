import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.router import api_router
from app.rag.engine import RAGEngine

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("aeropolicy")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize RAG and verify document SHA-256 hash
    logger.info("Starting AeroPolicy AI backend service...")
    engine = RAGEngine()
    try:
        success = engine.initialize_on_startup()
        if success:
            logger.info("AeroVista Airlines policy index successfully initialized.")
        else:
            logger.warning("Policy index initialization reported non-ready state. Check policy files.")
    except Exception as e:
        logger.error(f"Startup indexing error: {e}", exc_info=True)
    yield
    # Shutdown
    logger.info("Shutting down AeroPolicy AI backend service.")

app = FastAPI(
    title="AeroPolicy AI — Airline Policy Assistant",
    description="Production-grade policy assistant implementing strict anti-hallucination safeguards.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Custom exception handler to sanitize internal errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact system administrator."}
    )

app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "service": "AeroPolicy AI Backend",
        "brand": "AeroVista Airlines",
        "docs": "/docs",
        "health": "/api/health"
    }
