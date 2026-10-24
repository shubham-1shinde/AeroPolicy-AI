import faiss
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from app.rag.document_loader import DocumentChunk

logger = logging.getLogger(__name__)

class PersistentVectorStore:
    """Persistent vector store using FAISS Inner Product for normalized cosine similarity."""

    def __init__(self, store_dir: Path):
        self.store_dir = store_dir
        self.index_file = store_dir / "faiss_index.bin"
        self.chunks_file = store_dir / "chunks_data.json"
        self.index: Optional[faiss.Index] = None
        self.chunks: List[Dict[str, Any]] = []

    def is_persisted(self) -> bool:
        return self.index_file.exists() and self.chunks_file.exists()

    def build_and_save(self, chunks: List[DocumentChunk], embeddings: np.ndarray) -> bool:
        """Builds FAISS index and persists it atomically along with chunk metadata."""
        if len(chunks) == 0 or embeddings.shape[0] == 0:
            raise ValueError("Cannot build vector store with 0 chunks or embeddings.")

        dim = embeddings.shape[1]
        # Using IndexFlatIP for cosine similarity on normalized vectors
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)

        self.store_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare chunk data
        chunks_data = [
            {
                "chunk_id": c.metadata.get("chunk_id", f"chunk_{i}"),
                "content": c.page_content,
                "metadata": c.metadata
            }
            for i, c in enumerate(chunks)
        ]

        # Save index to temp then atomic rename
        temp_index = self.store_dir / "faiss_index.tmp"
        temp_chunks = self.store_dir / "chunks_data.tmp"

        faiss.write_index(index, str(temp_index))
        with open(temp_chunks, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

        temp_index.replace(self.index_file)
        temp_chunks.replace(self.chunks_file)

        self.index = index
        self.chunks = chunks_data
        logger.info(f"Persisted FAISS index with {len(chunks_data)} chunks to {self.store_dir}")
        return True

    def load(self) -> bool:
        """Loads persistent FAISS index and chunks from disk."""
        if not self.is_persisted():
            logger.warning(f"Vector store files missing in {self.store_dir}")
            return False

        try:
            self.index = faiss.read_index(str(self.index_file))
            with open(self.chunks_file, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
            logger.info(f"Loaded FAISS index with {len(self.chunks)} chunks from {self.store_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to load vector store from disk: {e}")
            return False

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.25
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Executes similarity search on normalized vectors.
        Returns list of (chunk_dict, score) where score is cosine similarity in range [-1, 1].
        """
        if self.index is None or not self.chunks:
            if not self.load():
                return []

        # Ensure shape (1, dim)
        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)

        top_k = min(top_k, len(self.chunks))
        distances, indices = self.index.search(query_vector, top_k)

        results: List[Tuple[Dict[str, Any], float]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            score = float(dist)
            # Filter by relevance threshold
            if score >= threshold:
                results.append((self.chunks[idx], score))

        return results

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        if not self.chunks:
            self.load()
        for c in self.chunks:
            if c.get("chunk_id") == chunk_id:
                return c
        return None

    def get_sections(self) -> List[Dict[str, Any]]:
        """Returns unique sections and their chunk counts."""
        if not self.chunks:
            self.load()
        section_map: Dict[str, Dict[str, Any]] = {}
        for c in self.chunks:
            meta = c.get("metadata", {})
            sec = meta.get("section", "General")
            if sec not in section_map:
                section_map[sec] = {
                    "id": f"sec_{len(section_map) + 1}",
                    "title": sec,
                    "chunk_count": 0,
                    "preview": c.get("content", "")[:200] + "..."
                }
            section_map[sec]["chunk_count"] += 1

        return list(section_map.values())
