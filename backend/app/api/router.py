from fastapi import APIRouter
from app.api.chat import router as chat_router
from app.api.policy import router as policy_router
from app.models.schemas import HealthResponse
from app.rag.engine import RAGEngine
from app.core.config import settings

api_router = APIRouter(prefix="/api")

rag_engine = RAGEngine()

@api_router.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse, summary="Service health check")
async def health_check():
    status_info = rag_engine.get_status()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        policy_status=status_info.get("status", "UNKNOWN"),
        indexed_chunks=status_info.get("total_chunks", 0),
        model=settings.GEMINI_MODEL
    )

api_router.include_router(chat_router, tags=["Chat"])
api_router.include_router(policy_router)
