
import logging
import os
import threading
from pathlib import Path
from typing import List

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
                    "LocalEmbeddingService already initialized "
                    "with a different model."
                )
            return

        self.model_name = model_name
        self._model = None
        self._initialized = True

    def _ensure_loaded(self):
        if self._model is not None:
            return

        with self._load_lock:
            if self._model is not None:
                return

            configured_path = os.getenv(
                "EMBEDDING_MODEL_PATH", ""
            ).strip()

            if configured_path:
                model_path = Path(configured_path)

                if not model_path.exists():
                    raise FileNotFoundError(
                        f"Embedding model path does not exist: "
                        f"{model_path}"
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
                "EMBED_DEBUG: Loading embedding model: %s",
                model_source,
            )

            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(
                model_source,
                device="cpu",
                local_files_only=local_only,
            )

            self._model = model

            logger.info(
                "EMBED_DEBUG: Embedding model loaded successfully."
            )

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        self._ensure_loaded()

        embeddings = self._model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return np.asarray(embeddings, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        self._ensure_loaded()

        # BGE recommends this prefix for short retrieval queries.
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

        return np.asarray(embedding, dtype=np.float32)
