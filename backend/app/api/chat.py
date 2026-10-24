import logging
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.engine import RAGEngine
from app.services.gemini_service import GeminiChatService

logger = logging.getLogger(__name__)
router = APIRouter()

rag_engine = RAGEngine()
gemini_service = GeminiChatService()

@router.post("/chat", response_model=ChatResponse, summary="Answer customer airline policy question")
async def chat_endpoint(request: ChatRequest):
    """
    Retrieves grounded evidence from AeroVista Airlines policy and synthesizes
    a verified response via Gemini 2.5 Flash with Air Canada anti-hallucination safeguards.
    """
    user_query = request.message.strip()
    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be blank."
        )

    try:
        # Retrieve relevant chunks using semantic search
        retrieved_chunks = rag_engine.retrieve(user_query)
        
        # Synthesize and verify grounded response
        response = gemini_service.generate_grounded_response(
            query=user_query,
            retrieved_chunks=retrieved_chunks,
            context=request.context
        )
        response.conversation_id = request.conversation_id
        return response

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while evaluating your policy question against the official terms."
        )
