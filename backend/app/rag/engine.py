
import time
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
        self.vectorstore = PersistentVectorStore(
            self.vectorstore_dir
        )
        self.embedding_service = LocalEmbeddingService(
            settings.EMBEDDING_MODEL_NAME
        )

        self.is_indexing = False
        self.is_ready = False
        self._initialized = True

        logger.info(
            "RAG_ENGINE: Created instance_id=%s model=%s policy=%s",
            id(self),
            settings.EMBEDDING_MODEL_NAME,
            self.policy_path,
        )

    def get_status(self) -> Dict[str, Any]:
        needs_reindex, status, current_hash, indexed_hash = (
            self.detector.check_index_status(
                self.policy_path,
                settings.EMBEDDING_MODEL_NAME,
                settings.INDEX_SCHEMA_VERSION,
            )
        )

        meta = self.detector.get_indexed_metadata()
        last_indexed_at = (
            meta.get("last_indexed_at") if meta else None
        )

        total_chunks = (
            len(self.vectorstore.chunks)
            if self.vectorstore.chunks
            else (
                meta.get("total_chunks", 0)
                if meta
                else 0
            )
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
        started_at = time.perf_counter()
        self.is_ready = False

        logger.info(
            "RAG_INIT: START instance_id=%s policy=%s model=%s",
            id(self),
            self.policy_path,
            settings.EMBEDDING_MODEL_NAME,
        )

        try:
            status_info = self.get_status()
            index_status = status_info["status"]

            logger.info(
                "RAG_INIT: STATUS=%s needs_reindex=%s "
                "hashes_match=%s saved_chunks=%s",
                index_status,
                status_info.get("needs_reindex"),
                status_info.get("current_hash")
                == status_info.get("indexed_hash"),
                status_info.get("total_chunks"),
            )

            if index_status == "FILE_MISSING":
                logger.error(
                    "RAG_INIT: Policy file missing: %s",
                    self.policy_path,
                )
                return False

            if index_status == "READY":
                logger.info(
                    "RAG_INIT: STEP 1 loading persistent vector store."
                )

                step_started = time.perf_counter()
                loaded = self.vectorstore.load()

                logger.info(
                    "RAG_INIT: STEP 1 finished loaded=%s chunks=%d "
                    "elapsed=%.2fs",
                    loaded,
                    len(self.vectorstore.chunks),
                    time.perf_counter() - step_started,
                )

                if loaded and self.vectorstore.chunks:
                    logger.info(
                        "RAG_INIT: STEP 2 loading embedding model."
                    )

                    step_started = time.perf_counter()
                    self.embedding_service._ensure_loaded()

                    logger.info(
                        "RAG_INIT: STEP 2 finished elapsed=%.2fs",
                        time.perf_counter() - step_started,
                    )

                    self.is_ready = True

                    logger.info(
                        "RAG_INIT: SUCCESS instance_id=%s ready=%s "
                        "chunks=%d total_elapsed=%.2fs",
                        id(self),
                        self.is_ready,
                        len(self.vectorstore.chunks),
                        time.perf_counter() - started_at,
                    )
                    return True

                logger.warning(
                    "RAG_INIT: Existing index failed to load; "
                    "attempting rebuild."
                )

            logger.info("RAG_INIT: STEP 3 rebuilding index.")

            success = self.reindex()

            if success and self.vectorstore.chunks:
                self.is_ready = True

                logger.info(
                    "RAG_INIT: SUCCESS after reindex chunks=%d "
                    "elapsed=%.2fs",
                    len(self.vectorstore.chunks),
                    time.perf_counter() - started_at,
                )
                return True

            logger.error(
                "RAG_INIT: FAILED reindex_success=%s chunks=%d "
                "elapsed=%.2fs",
                success,
                len(self.vectorstore.chunks),
                time.perf_counter() - started_at,
            )
            return False

        except Exception:
            self.is_ready = False
            logger.exception(
                "RAG_INIT: STARTUP EXCEPTION instance_id=%s "
                "elapsed=%.2fs",
                id(self),
                time.perf_counter() - started_at,
            )
            return False

    def reindex(self) -> bool:
        """Build and persist a new policy index."""
        if not self._index_lock.acquire(blocking=False):
            logger.warning(
                "RAG_INDEX: Another indexing operation is running."
            )
            return False

        started_at = time.perf_counter()
        self.is_indexing = True
        self.is_ready = False

        try:
            logger.info(
                "RAG_INDEX: START policy=%s model=%s",
                self.policy_path,
                settings.EMBEDDING_MODEL_NAME,
            )

            if not self.policy_path.exists():
                raise FileNotFoundError(
                    f"Policy document does not exist: "
                    f"{self.policy_path}"
                )

            step_started = time.perf_counter()
            document_hash = self.detector.compute_sha256(
                self.policy_path
            )

            logger.info(
                "RAG_INDEX: Policy hash computed hash=%s elapsed=%.2fs",
                document_hash,
                time.perf_counter() - step_started,
            )

            step_started = time.perf_counter()
            raw_docs = self.loader.load_document(self.policy_path)

            logger.info(
                "RAG_INDEX: Documents loaded count=%d elapsed=%.2fs",
                len(raw_docs),
                time.perf_counter() - step_started,
            )

            step_started = time.perf_counter()
            chunks = self.splitter.split_documents(
                raw_docs,
                document_hash,
            )

            logger.info(
                "RAG_INDEX: Chunks generated count=%d elapsed=%.2fs",
                len(chunks),
                time.perf_counter() - step_started,
            )

            if not chunks:
                raise ValueError(
                    "No text chunks were generated from the policy."
                )

            texts = [chunk.page_content for chunk in chunks]

            logger.info(
                "RAG_INDEX: Generating embeddings for %d chunks.",
                len(texts),
            )

            step_started = time.perf_counter()
            embeddings = self.embedding_service.embed_documents(texts)

            logger.info(
                "RAG_INDEX: Embeddings generated shape=%s elapsed=%.2fs",
                getattr(embeddings, "shape", None),
                time.perf_counter() - step_started,
            )

            step_started = time.perf_counter()
            self.vectorstore.build_and_save(chunks, embeddings)

            logger.info(
                "RAG_INDEX: Vector store saved elapsed=%.2fs",
                time.perf_counter() - step_started,
            )

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
                "RAG_INDEX: SUCCESS chunks=%d ready=%s elapsed=%.2fs",
                len(chunks),
                self.is_ready,
                time.perf_counter() - started_at,
            )

            return True

        except Exception:
            self.is_ready = False
            logger.exception(
                "RAG_INDEX: FAILED elapsed=%.2fs",
                time.perf_counter() - started_at,
            )

            try:
                if self.vectorstore.load():
                    logger.warning(
                        "RAG_INDEX: Previous vector store restored."
                    )
                    self.is_ready = bool(
                        self.vectorstore.chunks
                    )
            except Exception:
                logger.exception(
                    "RAG_INDEX: Previous vector store restoration failed."
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
        started_at = time.perf_counter()

        logger.info(
            "RAG_RETRIEVE: START instance_id=%s ready=%s "
            "chunks=%d",
            id(self),
            self.is_ready,
            len(self.vectorstore.chunks),
        )

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
            logger.warning(
                "RAG_RETRIEVE: In-memory chunks empty; "
                "attempting vector store load."
            )

            if not self.vectorstore.load():
                raise RuntimeError(
                    "The policy vector store could not be loaded."
                )

        step_started = time.perf_counter()
        logger.info("RAG_RETRIEVE: Generating query embedding.")

        query_embedding = self.embedding_service.embed_query(query)

        logger.info(
            "RAG_RETRIEVE: Query embedding generated shape=%s "
            "elapsed=%.2fs",
            getattr(query_embedding, "shape", None),
            time.perf_counter() - step_started,
        )

        step_started = time.perf_counter()

        results = self.vectorstore.search(
            query_embedding,
            top_k=k,
            threshold=th,
        )

        logger.info(
            "RAG_RETRIEVE: Search completed results=%d elapsed=%.2fs "
            "total_elapsed=%.2fs",
            len(results),
            time.perf_counter() - step_started,
            time.perf_counter() - started_at,
        )

        return results
