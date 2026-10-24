
import logging
import threading
from typing import List, Dict, Any, Optional, Tuple

from app.core.config import settings
from app.rag.document_loader import PolicyDocumentLoader
from app.rag.text_splitter import SectionAwareTextSplitter
from app.rag.embeddings import LocalEmbeddingService
from app.rag.vectorstore import PersistentVectorStore
from app.rag.change_detector import ChangeDetector

logger = logging.getLogger(__name__)


class RAGEngine:
    _instance = None
    _instance_lock = threading.Lock()
    _index_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.policy_path = settings.policy_file_path
        self.metadata_dir = settings.metadata_dir
        self.vectorstore_dir = settings.vectorstore_dir

        self.loader = PolicyDocumentLoader()
        self.splitter = SectionAwareTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.detector = ChangeDetector(self.metadata_dir)
        self.vectorstore = PersistentVectorStore(self.vectorstore_dir)
        self.embedding_service = LocalEmbeddingService(
            settings.EMBEDDING_MODEL_NAME
        )

        self.is_indexing = False
        self.is_ready = False
        self._initialized = True

    def get_status(self) -> Dict[str, Any]:
        needs_reindex, status, current_hash, indexed_hash = (
            self.detector.check_index_status(
                self.policy_path,
                settings.EMBEDDING_MODEL_NAME,
                settings.INDEX_SCHEMA_VERSION,
            )
        )

        meta = self.detector.get_indexed_metadata()
        last_indexed_at = meta.get("last_indexed_at") if meta else None

        total_chunks = (
            len(self.vectorstore.chunks)
            if self.vectorstore.chunks
            else (meta.get("total_chunks", 0) if meta else 0)
        )

        return {
            "current_hash": current_hash,
            "indexed_hash": indexed_hash,
            "status": status,
            "last_indexed_at": last_indexed_at,
            "total_chunks": total_chunks,
            "policy_path": str(self.policy_path),
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "needs_reindex": needs_reindex,
            "is_ready": self.is_ready,
            "is_indexing": self.is_indexing,
        }

    def initialize_on_startup(self) -> bool:
        """Load the existing index or rebuild it if necessary."""
        self.is_ready = False

        logger.info("RAG_INIT: Checking policy index status.")

        try:
            status_info = self.get_status()
            index_status = status_info["status"]

            logger.info(
                "RAG_INIT: Current policy index status: %s",
                index_status,
            )

            if index_status == "FILE_MISSING":
                logger.error(
                    "RAG_INIT: Policy file is missing: %s",
                    self.policy_path,
                )
                return False

            if index_status == "READY":
                if self.vectorstore.load():
                    logger.info(
                        "RAG_INIT: Persistent index loaded successfully."
                    )
                    self.is_ready = True
                    return True

                logger.warning(
                    "RAG_INIT: Index could not be loaded; rebuilding."
                )

            success = self.reindex()

            if success and self.vectorstore.chunks:
                self.is_ready = True
                logger.info("RAG_INIT: Policy index is ready.")
                return True

            logger.error("RAG_INIT: Policy index is not ready.")
            return False

        except Exception:
            self.is_ready = False
            logger.exception(
                "RAG_INIT: Policy index initialization failed."
            )
            return False

    def reindex(self) -> bool:
        """Build and persist a new policy index."""
        if not self._index_lock.acquire(blocking=False):
            logger.warning(
                "RAG_INIT: Another index operation is already running."
            )
            return False

        self.is_indexing = True
        self.is_ready = False

        try:
            logger.info(
                "RAG_INIT: Starting indexing for %s",
                self.policy_path,
            )

            if not self.policy_path.exists():
                raise FileNotFoundError(
                    f"Policy document does not exist: {self.policy_path}"
                )

            document_hash = self.detector.compute_sha256(
                self.policy_path
            )
            raw_docs = self.loader.load_document(self.policy_path)

            chunks = self.splitter.split_documents(
                raw_docs,
                document_hash,
            )

            if not chunks:
                raise ValueError(
                    "No text chunks were generated from the policy document."
                )

            logger.info(
                "RAG_INIT: Generated %d policy chunks.",
                len(chunks),
            )

            texts = [chunk.page_content for chunk in chunks]

            embeddings = self.embedding_service.embed_documents(texts)

            self.vectorstore.build_and_save(chunks, embeddings)

            sections = list({
                chunk.metadata.get("section", "General")
                for chunk in chunks
            })

            self.detector.save_index_metadata(
                document_hash=document_hash,
                embedding_model=settings.EMBEDDING_MODEL_NAME,
                index_version=settings.INDEX_SCHEMA_VERSION,
                total_chunks=len(chunks),
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                sections=sections,
            )

            if not self.vectorstore.chunks:
                raise RuntimeError(
                    "Index was saved, but no chunks are available."
                )

            self.is_ready = True

            logger.info(
                "RAG_INIT: Successfully indexed %d policy chunks.",
                len(chunks),
            )

            return True

        except Exception:
            self.is_ready = False
            logger.exception("RAG_INIT: Policy indexing failed.")

            # Preserve access to a previously saved index if it can be loaded.
            try:
                if self.vectorstore.load():
                    logger.warning(
                        "RAG_INIT: Previous index loaded after rebuild failure."
                    )
                    self.is_ready = True
            except Exception:
                logger.exception(
                    "RAG_INIT: Could not load the previous index."
                )

            raise

        finally:
            self.is_indexing = False
            self._index_lock.release()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieve policy chunks relevant to a query."""
        if not self.is_ready:
            raise RuntimeError(
                "The policy index is not ready. Try again shortly."
            )

        k = (
            top_k
            if top_k is not None
            else settings.TOP_K_CHUNKS
        )
        th = (
            threshold
            if threshold is not None
            else settings.SIMILARITY_THRESHOLD
        )

        if not self.vectorstore.chunks:
            if not self.vectorstore.load():
                raise RuntimeError(
                    "The policy vector store could not be loaded."
                )

        query_embedding = self.embedding_service.embed_query(query)

        return self.vectorstore.search(
            query_embedding,
            top_k=k,
            threshold=th,
        )
