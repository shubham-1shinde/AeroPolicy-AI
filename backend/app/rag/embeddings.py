
import logging
import os
import threading
import time
from pathlib import Path
from typing import List

# Restrict multi-threading BEFORE torch/sentence_transformers is loaded.
# This prevents cloud containers (like Render 512MB RAM) from spawning
# thread pools for all 32/64 host cores and triggering immediate OOM (SIGKILL 137).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np

logger = logging.getLogger(__name__)


class LocalEmbeddingService:
    _instance = None
    _instance_lock = threading.Lock()
    _load_lock = threading.Lock()

    def __new__(cls, model_name="BAAI/bge-small-en-v1.5"):
        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
        return cls._instance

    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        if self._initialized:
            if self.model_name != model_name:
                raise ValueError(
                    f"Embedding model mismatch: existing={self.model_name}, "
                    f"requested={model_name}"
                )
            return

        self.model_name = model_name
        self._model = None
        self._initialized = True

        logger.info(
            "EMBED_INIT: Service created. model=%s",
            self.model_name,
        )

    def _ensure_loaded(self):
        if self._model is not None:
            logger.debug("EMBED_LOAD: Model already loaded; reusing it.")
            return

        with self._load_lock:
            if self._model is not None:
                return

            started = time.perf_counter()

            configured_path = os.getenv(
                "EMBEDDING_MODEL_PATH", ""
            ).strip()

            if configured_path:
                model_path = Path(configured_path)

                if not model_path.exists():
                    raise FileNotFoundError(
                        f"EMBEDDING_MODEL_PATH does not exist: {model_path}"
                    )

                model_source = str(model_path)
                local_only = True
            else:
                model_source = self.model_name
                local_only = (
                    os.getenv("HF_HUB_OFFLINE", "").lower()
                    in ("1", "true", "yes")
                )

            logger.info(
                "EMBED_LOAD: Starting model load. model=%s source=%s "
                "local_only=%s",
                self.model_name,
                model_source,
                local_only,
            )

            try:
                logger.info("EMBED_LOAD: Importing SentenceTransformer.")
                try:
                    import torch
                    torch.set_num_threads(1)
                    torch.set_num_interop_threads(1)
                except Exception:
                    pass
                from sentence_transformers import SentenceTransformer

                logger.info(
                    "EMBED_LOAD: Import completed. Creating model on CPU."
                )

                model = SentenceTransformer(
                    model_source,
                    device="cpu",
                    local_files_only=local_only,
                )

                logger.info(
                    "EMBED_LOAD: Model constructor completed in %.2fs.",
                    time.perf_counter() - started,
                )

                # Run a small test before marking the model ready.
                test_start = time.perf_counter()
                test_embedding = model.encode(
                    ["embedding startup test"],
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )

                test_embedding = np.asarray(
                    test_embedding, dtype=np.float32
                )

                if (
                    test_embedding.ndim != 2
                    or test_embedding.shape[0] != 1
                    or not np.isfinite(test_embedding).all()
                ):
                    raise RuntimeError(
                        f"Invalid test embedding shape or values: "
                        f"{test_embedding.shape}"
                    )

                self._model = model

                logger.info(
                    "EMBED_LOAD: Model READY. dimensions=%s "
                    "warmup=%.2fs total=%.2fs",
                    test_embedding.shape[1],
                    time.perf_counter() - test_start,
                    time.perf_counter() - started,
                )

            except Exception:
                logger.exception(
                    "EMBED_LOAD_FAILED: Model initialization failed "
                    "after %.2fs. model=%s",
                    time.perf_counter() - started,
                    self.model_name,
                )
                raise

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        started = time.perf_counter()

        logger.info(
            "EMBED_DOCS: Starting document embedding. count=%d",
            len(texts),
        )

        if not texts:
            logger.warning("EMBED_DOCS: Received an empty document list.")
            return np.empty((0, 384), dtype=np.float32)

        try:
            self._ensure_loaded()

            embeddings = self._model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            result = np.asarray(embeddings, dtype=np.float32)

            if result.ndim != 2 or result.shape[0] != len(texts):
                raise RuntimeError(
                    f"Unexpected document embedding shape: {result.shape}"
                )

            if not np.isfinite(result).all():
                raise RuntimeError(
                    "Document embeddings contain NaN or infinite values."
                )

            logger.info(
                "EMBED_DOCS: Completed. shape=%s elapsed=%.2fs",
                result.shape,
                time.perf_counter() - started,
            )
            return result

        except Exception:
            logger.exception(
                "EMBED_DOCS_FAILED: Document embedding failed "
                "after %.2fs.",
                time.perf_counter() - started,
            )
            raise

    def embed_query(self, text: str) -> np.ndarray:
        started = time.perf_counter()

        # Log the length, not the actual customer question.
        logger.info(
            "EMBED_QUERY: Starting. query_length=%d model=%s",
            len(text),
            self.model_name,
        )

        try:
            self._ensure_loaded()

            query = text
            if self.model_name == "BAAI/bge-small-en-v1.5":
                query = (
                    "Represent this sentence for searching relevant passages: "
                    + text
                )

            embedding = self._model.encode(
                query,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            result = np.asarray(embedding, dtype=np.float32)

            if result.ndim != 1 or result.shape[0] != 384:
                raise RuntimeError(
                    f"Unexpected query embedding shape: {result.shape}"
                )

            if not np.isfinite(result).all():
                raise RuntimeError(
                    "Query embedding contains NaN or infinite values."
                )

            logger.info(
                "EMBED_QUERY: SUCCESS. shape=%s elapsed=%.2fs",
                result.shape,
                time.perf_counter() - started,
            )
            return result

        except Exception:
            logger.exception(
                "EMBED_QUERY_FAILED: Query embedding failed "
                "after %.2fs.",
                time.perf_counter() - started,
            )
            raise
