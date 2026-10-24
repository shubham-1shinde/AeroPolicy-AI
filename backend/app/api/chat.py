
import logging
import time

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ChatRequest, ChatResponse
from app.rag.engine import RAGEngine
from app.services.gemini_service import GeminiChatService

logger = logging.getLogger(__name__)

router = APIRouter()

rag_engine = RAGEngine()
gemini_service = GeminiChatService()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Answer customer airline policy question",
)
async def chat_endpoint(request: ChatRequest):
    request_start = time.perf_counter()

    user_query = request.message.strip()

    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be blank.",
        )

    # Do not process a chat until background initialization finishes.
    if not rag_engine.is_ready:
        logger.warning(
            "CHAT_DEBUG: Request received while policy index is not ready."
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The policy knowledge base is initializing or unavailable. "
                "Please try again shortly."
            ),
        )

    try:
        # Step 1: Retrieve policy evidence.
        logger.info("CHAT_DEBUG: Starting policy retrieval.")
        stage_start = time.perf_counter()

        retrieved_chunks = rag_engine.retrieve(user_query)

        logger.info(
            "CHAT_DEBUG: Retrieval finished in %.2fs; chunks=%d.",
            time.perf_counter() - stage_start,
            len(retrieved_chunks),
        )

        # Step 2: Generate a grounded response.
        logger.info("CHAT_DEBUG: Starting response generation.")
        stage_start = time.perf_counter()

        response = gemini_service.generate_grounded_response(
            query=user_query,
            retrieved_chunks=retrieved_chunks,
            context=request.context,
        )

        logger.info(
            "CHAT_DEBUG: Response generation finished in %.2fs.",
            time.perf_counter() - stage_start,
        )

        response.conversation_id = request.conversation_id

        logger.info(
            "CHAT_DEBUG: Request completed in %.2fs.",
            time.perf_counter() - request_start,
        )

        return response

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "CHAT_DEBUG: Request failed after %.2fs.",
            time.perf_counter() - request_start,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An error occurred while evaluating your policy question "
                "against the official terms."
            ),
        )
