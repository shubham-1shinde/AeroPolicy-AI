
import logging
import threading
from typing import List

import numpy as np

logger = logging.getLogger(__name__)


class LocalEmbeddingService:
    _instance = None
    _instance_lock = threading.Lock()
    _load_lock = threading.Lock()
    _model = None

    def __new__(
        cls,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance.model_name = model_name
                cls._instance = instance
            elif cls._instance.model_name != model_name:
                raise ValueError(
                    "LocalEmbeddingService was already initialized "
                    f"with model {cls._instance.model_name!r}."
                )

        return cls._instance

    def _ensure_loaded(self):
        if self._model is not None:
            return

        with self._load_lock:
            if self._model is not None:
                return

            logger.info(
                "Loading local embedding model: %s",
                self.model_name,
            )

            # Import only when the embedding model is actually needed.
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(self.model_name)
            self._model = model

            logger.info("Local embedding model loaded successfully.")

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        self._ensure_loaded()

        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return np.asarray(embeddings, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        self._ensure_loaded()

        embeddings = self._model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return np.asarray(embeddings[0], dtype=np.float32)
