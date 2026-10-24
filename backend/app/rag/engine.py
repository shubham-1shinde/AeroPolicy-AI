import threading
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.core.config import settings
from app.rag.document_loader import PolicyDocumentLoader, DocumentChunk
from app.rag.text_splitter import SectionAwareTextSplitter
from app.rag.embeddings import LocalEmbeddingService
from app.rag.vectorstore import PersistentVectorStore
from app.rag.change_detector import ChangeDetector

logger = logging.getLogger(__name__)

class RAGEngine:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.policy_path = settings.policy_file_path
        self.metadata_dir = settings.metadata_dir
        self.vectorstore_dir = settings.vectorstore_dir
        
        self.loader = PolicyDocumentLoader()
        self.splitter = SectionAwareTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.detector = ChangeDetector(self.metadata_dir)
        self.vectorstore = PersistentVectorStore(self.vectorstore_dir)
        self.embedding_service = LocalEmbeddingService(settings.EMBEDDING_MODEL_NAME)
        self.is_indexing = False
        self._initialized = True

    def get_status(self) -> Dict[str, Any]:
        """Returns the current document hash, indexed hash, status, and chunk count."""
        needs_reindex, status, current_hash, indexed_hash = self.detector.check_index_status(
            self.policy_path,
            settings.EMBEDDING_MODEL_NAME,
            settings.INDEX_SCHEMA_VERSION
        )
        meta = self.detector.get_indexed_metadata()
        last_indexed_at = meta.get("last_indexed_at") if meta else None
        total_chunks = len(self.vectorstore.chunks) if self.vectorstore.chunks else (meta.get("total_chunks", 0) if meta else 0)

        return {
            "current_hash": current_hash,
            "indexed_hash": indexed_hash,
            "status": status,
            "last_indexed_at": last_indexed_at,
            "total_chunks": total_chunks,
            "policy_path": str(self.policy_path),
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "needs_reindex": needs_reindex
        }

    def initialize_on_startup(self) -> bool:
        """Called on FastAPI startup: reuses existing vector store if hash matches; indexes only if needed."""
        status_info = self.get_status()
        status = status_info["status"]
        
        logger.info(f"Startup RAG index verification. Current status: {status}")

        if status == "FILE_MISSING":
            logger.error(f"Policy file missing at {self.policy_path}. Backend running without active policy index.")
            return False

        if status == "READY":
            # Attempt to load persistent vectors
            if self.vectorstore.load():
                logger.info("Persistent vector store loaded successfully. Re-embedding skipped (hash unchanged).")
                return True
            else:
                logger.warning("Vector store files unreadable despite valid hash. Re-indexing required.")

        # If OUTDATED, NOT_INDEXED, or vectorstore load failed, re-index
        return self.reindex()

    def reindex(self) -> bool:
        """
        Reindexes the policy document with thread-safe atomic lock.
        Prevents concurrent requests from duplicating indexing work.
        """
        if not self._lock.acquire(blocking=False):
            logger.warning("Index operation already in progress. Ignoring duplicate trigger.")
            return False

        self.is_indexing = True
        try:
            logger.info(f"Starting policy indexing for: {self.policy_path}")
            
            # 1. Verify and read document
            if not self.policy_path.exists():
                raise FileNotFoundError(f"Policy document does not exist: {self.policy_path}")
            
            doc_hash = self.detector.compute_sha256(self.policy_path)
            raw_docs = self.loader.load_document(self.policy_path)

            # 2. Split into heading-aware chunks
            chunks = self.splitter.split_documents(raw_docs, doc_hash)
            if not chunks:
                raise ValueError("No text chunks generated from policy document.")

            logger.info(f"Generated {len(chunks)} chunks from policy document.")

            # 3. Generate embeddings locally
            texts = [c.page_content for c in chunks]
            embeddings = self.embedding_service.embed_documents(texts)

            # 4. Save FAISS index and chunk metadata atomically
            self.vectorstore.build_and_save(chunks, embeddings)

            # 5. Extract unique sections
            sections = list({c.metadata.get("section", "General") for c in chunks})

            # 6. Save metadata only upon successful build
            self.detector.save_index_metadata(
                document_hash=doc_hash,
                embedding_model=settings.EMBEDDING_MODEL_NAME,
                index_version=settings.INDEX_SCHEMA_VERSION,
                total_chunks=len(chunks),
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                sections=sections
            )

            logger.info(f"Policy indexing completed successfully. {len(chunks)} chunks indexed.")
            return True

        except Exception as e:
            logger.error(f"Policy indexing failed: {e}", exc_info=True)
            # Re-attempt loading prior index if available
            self.vectorstore.load()
            raise e
        finally:
            self.is_indexing = False
            self._lock.release()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieves top_k relevant chunks with similarity score above threshold."""
        k = top_k or settings.TOP_K_CHUNKS
        th = threshold or settings.SIMILARITY_THRESHOLD

        # If vectorstore is not loaded in memory, load it
        if not self.vectorstore.chunks:
            loaded = self.vectorstore.load()
            if not loaded:
                logger.warning("Vector store is not loaded. Returning empty retrieval results.")
                return []

        query_emb = self.embedding_service.embed_query(query)
        results = self.vectorstore.search(query_emb, top_k=k, threshold=th)
        return results
