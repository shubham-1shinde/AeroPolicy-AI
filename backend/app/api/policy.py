import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_admin_token
from app.models.schemas import PolicyStatusResponse, ReindexResponse, PolicySection, SourceDetailResponse
from app.rag.engine import RAGEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/policy", tags=["Policy Management"])

rag_engine = RAGEngine()

@router.get("/status", response_model=PolicyStatusResponse, summary="Get policy vector index and hash status")
async def get_policy_status():
    """Returns current policy document SHA-256 hash, indexed hash, and status."""
    info = rag_engine.get_status()
    return PolicyStatusResponse(
        current_hash=info.get("current_hash"),
        indexed_hash=info.get("indexed_hash"),
        status=info.get("status", "UNKNOWN"),
        last_indexed_at=info.get("last_indexed_at"),
        total_chunks=info.get("total_chunks", 0),
        policy_path=info.get("policy_path", ""),
        embedding_model=info.get("embedding_model", "")
    )

@router.post("/reindex", response_model=ReindexResponse, summary="Trigger policy re-indexing")
async def trigger_reindex(authorized: bool = Depends(verify_admin_token)):
    """
    Manually forces re-indexing of the airline policy document.
    Requires administrative authorization header 'X-Admin-Token'.
    """
    try:
        success = rag_engine.reindex()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An indexing operation is already in progress."
            )
            
        info = rag_engine.get_status()
        return ReindexResponse(
            success=True,
            message="Policy document successfully re-indexed into persistent vector store.",
            total_chunks=info.get("total_chunks", 0),
            document_hash=info.get("indexed_hash", ""),
            indexed_at=info.get("last_indexed_at", "")
        )
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(fnf))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to reindex policy document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reindex policy document: {str(e)}"
        )

@router.get("/sections", response_model=List[PolicySection], summary="List available policy sections")
async def get_policy_sections():
    """Returns available structured policy sections with chunk count."""
    sections_data = rag_engine.vectorstore.get_sections()
    return [
        PolicySection(
            id=s["id"],
            title=s["title"],
            chunk_count=s["chunk_count"],
            preview=s.get("preview")
        )
        for s in sections_data
    ]

@router.get("/source/{source_id}", response_model=SourceDetailResponse, summary="Fetch specific policy chunk reference")
async def get_policy_source_detail(source_id: str):
    """
    Retrieves authorized source reference by chunk ID.
    Guards against unrestricted filesystem access by strictly querying indexed chunk store.
    """
    chunk = rag_engine.vectorstore.get_chunk_by_id(source_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source reference '{source_id}' not found in active policy index."
        )

    meta = chunk.get("metadata", {})
    return SourceDetailResponse(
        source_id=chunk.get("chunk_id", source_id),
        document=meta.get("source", "airline_policy.md"),
        section=meta.get("section", "General"),
        page=meta.get("page"),
        full_text=chunk.get("content", "")
    )
