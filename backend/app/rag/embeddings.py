import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

class LocalEmbeddingService:
    _instance = None
    _model = None

    def __new__(cls, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = super(LocalEmbeddingService, cls).__new__(cls)
            cls._instance.model_name = model_name
        return cls._instance

    def _ensure_loaded(self):
        if self._model is None:
            logger.info(f"Loading local embedding model: {self.model_name}")
            import os
            # Ensure transformers operates smoothly with cached model
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info("Local embedding model loaded successfully.")

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        self._ensure_loaded()
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.astype(np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        self._ensure_loaded()
        embedding = self._model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        return embedding[0].astype(np.float32)
