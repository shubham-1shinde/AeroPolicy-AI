
import logging
import os
import threading
import time
from typing import List

import numpy as np
from google import genai

logger = logging.getLogger(__name__)


class LocalEmbeddingService:
    _instance = None
    _instance_lock = threading.Lock()
    _load_lock = threading.Lock()

    def __new__(cls, model_name="gemini-embedding-2"):
        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
        return cls._instance

    def __init__(self, model_name="gemini-embedding-2"):
        if self._initialized:
            if self.model_name != model_name:
                raise ValueError(
                    f"Embedding model mismatch: "
                    f"existing={self.model_name}, requested={model_name}"
                )
            return

        self.model_name = model_name
        self.dimensions = 768
        self._client = None
        self._initialized = True

        logger.info(
            "EMBED_INIT: model=%s dimensions=%d",
            self.model_name,
            self.dimensions,
        )

    def _ensure_loaded(self):
        if self._client is not None:
            return

        with self._load_lock:
            if self._client is not None:
                return

            started = time.perf_counter()
            api_key = os.getenv("GEMINI_API_KEY", "").strip()

            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY is missing from the environment."
                )

            try:
                self._client = genai.Client(api_key=api_key)

                logger.info(
                    "EMBED_LOAD: Client ready in %.2fs",
                    time.perf_counter() - started,
                )

            except Exception:
                logger.exception("EMBED_LOAD_FAILED")
                raise

    def _embed_one(self, text: str) -> np.ndarray:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Embedding input must be non-empty text.")

        self._ensure_loaded()

        response = self._client.models.embed_content(
            model=self.model_name,
            contents=text.strip(),
            config={
                "output_dimensionality": self.dimensions,
            },
        )

        if not response.embeddings:
            raise RuntimeError("Gemini returned no embeddings.")

        result = np.asarray(
            response.embeddings[0].values,
            dtype=np.float32,
        )

        if result.ndim != 1 or result.shape[0] != self.dimensions:
            raise RuntimeError(
                f"Unexpected embedding shape: {result.shape}; "
                f"expected ({self.dimensions},)"
            )

        if not np.isfinite(result).all():
            raise RuntimeError(
                "Embedding contains NaN or infinite values."
            )

        return result

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        started = time.perf_counter()

        logger.info(
            "EMBED_DOCS: Starting. count=%d",
            len(texts),
        )

        if not texts:
            return np.empty(
                (0, self.dimensions),
                dtype=np.float32,
            )

        try:
            embeddings = [
                self._embed_one(text)
                for text in texts
            ]

            result = np.stack(embeddings).astype(
                np.float32,
                copy=False,
            )

            logger.info(
                "EMBED_DOCS: Completed. shape=%s elapsed=%.2fs",
                result.shape,
                time.perf_counter() - started,
            )

            return result

        except Exception:
            logger.exception("EMBED_DOCS_FAILED")
            raise

    def embed_query(self, text: str) -> np.ndarray:
        started = time.perf_counter()

        logger.info(
            "EMBED_QUERY: Starting. query_length=%d model=%s",
            len(text),
            self.model_name,
        )

        try:
            result = self._embed_one(text)

            logger.info(
                "EMBED_QUERY: SUCCESS. shape=%s elapsed=%.2fs",
                result.shape,
                time.perf_counter() - started,
            )

            return result

        except Exception:
            logger.exception("EMBED_QUERY_FAILED")
            raise
