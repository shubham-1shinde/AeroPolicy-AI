from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    document: str = Field(..., description="Source policy filename")
    section: Optional[str] = Field(None, description="Policy section header")
    page: Optional[int] = Field(None, description="Page number if applicable")
    excerpt: str = Field(..., description="Relevant supporting policy text excerpt")
    score: Optional[float] = Field(None, description="Retrieval similarity score")
    source_id: Optional[str] = Field(None, description="Unique chunk/source identifier")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1500, description="User message or policy question")
    conversation_id: Optional[str] = Field(None, description="Optional session or conversation ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional non-sensitive booking context")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Response grounded strictly in airline policy")
    grounded: bool = Field(..., description="Whether sufficient verified policy evidence supports the answer")
    sources: List[SourceCitation] = Field(default_factory=list, description="List of validated supporting source citations")
    needs_clarification: bool = Field(default=False, description="Whether additional non-sensitive booking details are required")
    suggested_question: Optional[str] = Field(None, description="Optional suggested follow-up clarifying question")
    policy_version: Optional[str] = Field(None, description="Version of the governing policy document")
    conversation_id: Optional[str] = Field(None, description="Conversation session ID")

class PolicyStatusResponse(BaseModel):
    current_hash: Optional[str] = Field(None, description="SHA-256 hash of the current policy document on disk")
    indexed_hash: Optional[str] = Field(None, description="SHA-256 hash of the currently indexed vectorstore data")
    status: str = Field(..., description="Index status: READY, OUTDATED, NOT_INDEXED, FILE_MISSING, or ERROR")
    last_indexed_at: Optional[str] = Field(None, description="ISO timestamp of last successful index")
    total_chunks: int = Field(0, description="Total chunks in active vectorstore")
    policy_path: str = Field(..., description="Path to policy document")
    embedding_model: str = Field(..., description="Name of embedding model in use")

class ReindexResponse(BaseModel):
    success: bool
    message: str
    total_chunks: int
    document_hash: str
    indexed_at: str

class PolicySection(BaseModel):
    id: str
    title: str
    chunk_count: int
    preview: Optional[str] = None

class SourceDetailResponse(BaseModel):
    source_id: str
    document: str
    section: str
    page: Optional[int] = None
    full_text: str

class HealthResponse(BaseModel):
    status: str
    version: str
    policy_status: str
    indexed_chunks: int
    model: str
