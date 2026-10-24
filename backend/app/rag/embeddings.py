
import logging
import threading
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class LocalEmbeddingService:
    _instance = None
    _model = None
    _load_lock = threading.Lock()

    def __new__(
        cls,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        with cls._load_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.model_name = model_name
            elif cls._instance.model_name != model_name:
                raise ValueError(
                    "LocalEmbeddingService was initialized with a different model."
                )

        return cls._instance

    def _ensure_loaded(self):
        if self._model is None:
            with self._load_lock:
                if self._model is None:
                    logger.info(
                        "Loading local embedding model: %s",
                        self.model_name,
                    )
                    self._model = SentenceTransformer(self.model_name)
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
        return embeddings.astype(np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        self._ensure_loaded()
        embeddings = self._model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings[0].astype(np.float32)
