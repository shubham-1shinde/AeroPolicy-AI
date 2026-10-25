
import asyncio
import logging
import time
import uuid

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
    request_id = uuid.uuid4().hex[:10]
    started = time.perf_counter()

    logger.info(
        "CHAT[%s]: REQUEST_RECEIVED query_length=%d ready=%s",
        request_id,
        len(request.message or ""),
        rag_engine.is_ready,
    )

    try:
        user_query = (request.message or "").strip()

        if not user_query:
            logger.warning("CHAT[%s]: Rejected blank message.", request_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be blank.",
            )

        if not rag_engine.is_ready:
            logger.info(
                "CHAT[%s]: Policy index is still warming up. Waiting up to 35s...",
                request_id,
            )
            wait_start = time.perf_counter()
            while not rag_engine.is_ready and (time.perf_counter() - wait_start) < 35.0:
                await asyncio.sleep(0.5)

            if not rag_engine.is_ready:
                logger.warning(
                    "CHAT[%s]: Policy index initialization timed out after 35s.",
                    request_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="The policy knowledge base is still initializing. Please wait a moment and try again.",
                )
            else:
                logger.info(
                    "CHAT[%s]: Policy index became ready after %.2fs wait.",
                    request_id,
                    time.perf_counter() - wait_start,
                )

        # Stage 1: Retrieval and embeddings (run in threadpool to prevent blocking event loop)
        stage = time.perf_counter()
        logger.info("CHAT[%s]: RETRIEVAL_BEGIN", request_id)

        retrieved_chunks = await asyncio.to_thread(rag_engine.retrieve, user_query)

        logger.info(
            "CHAT[%s]: RETRIEVAL_SUCCESS chunks=%d elapsed=%.2fs",
            request_id,
            len(retrieved_chunks),
            time.perf_counter() - stage,
        )

        # Stage 2: Gemini generation and verification (run in threadpool)
        stage = time.perf_counter()
        logger.info(
            "CHAT[%s]: GENERATION_BEGIN model=%s",
            request_id,
            gemini_service.model_name,
        )

        response = await asyncio.to_thread(
            gemini_service.generate_grounded_response,
            query=user_query,
            retrieved_chunks=retrieved_chunks,
            context=request.context,
        )

        logger.info(
            "CHAT[%s]: GENERATION_SUCCESS elapsed=%.2fs",
            request_id,
            time.perf_counter() - stage,
        )

        response.conversation_id = request.conversation_id

        logger.info(
            "CHAT[%s]: REQUEST_SUCCESS total=%.2fs",
            request_id,
            time.perf_counter() - started,
        )
        return response

    except HTTPException as exc:
        logger.warning(
            "CHAT[%s]: HTTP_ERROR status=%s elapsed=%.2fs",
            request_id,
            exc.status_code,
            time.perf_counter() - started,
        )
        raise

    except Exception:
        logger.exception(
            "CHAT[%s]: REQUEST_FAILED elapsed=%.2fs",
            request_id,
            time.perf_counter() - started,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An error occurred while evaluating your policy question "
                "against the official terms."
            ),
        )
