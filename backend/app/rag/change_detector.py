import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ChangeDetector:
    def __init__(self, metadata_dir: Path):
        self.metadata_dir = metadata_dir
        self.metadata_file = metadata_dir / "policy_index_meta.json"

    def compute_sha256(self, file_path: Path) -> str:
        """Computes the SHA-256 checksum of the target file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found for hash calculation: {file_path}")
            
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    def get_indexed_metadata(self) -> Optional[Dict[str, Any]]:
        """Reads stored metadata from disk."""
        if not self.metadata_file.exists():
            return None
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read index metadata file: {e}")
            return None

    def check_index_status(
        self,
        file_path: Path,
        expected_model: str,
        expected_schema: str
    ) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Returns:
            (needs_reindex: bool, status_code: str, current_hash: Optional[str], indexed_hash: Optional[str])
        """
        if not file_path.exists():
            return (False, "FILE_MISSING", None, None)
            
        try:
            current_hash = self.compute_sha256(file_path)
        except Exception as e:
            logger.error(f"Error computing file hash: {e}")
            return (False, "ERROR", None, None)

        meta = self.get_indexed_metadata()
        if not meta:
            return (True, "NOT_INDEXED", current_hash, None)

        indexed_hash = meta.get("document_hash")
        indexed_model = meta.get("embedding_model")
        indexed_schema = meta.get("index_version")

        if indexed_hash != current_hash:
            return (True, "OUTDATED", current_hash, indexed_hash)
            
        if indexed_model != expected_model or indexed_schema != expected_schema:
            return (True, "CONFIG_CHANGED", current_hash, indexed_hash)

        return (False, "READY", current_hash, indexed_hash)

    def save_index_metadata(
        self,
        document_hash: str,
        embedding_model: str,
        index_version: str,
        total_chunks: int,
        chunk_size: int,
        chunk_overlap: int,
        sections: list
    ):
        """Atomically saves index metadata after successful indexing."""
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "document_hash": document_hash,
            "embedding_model": embedding_model,
            "index_version": index_version,
            "total_chunks": total_chunks,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "sections": sections,
            "last_indexed_at": datetime.now(timezone.utc).isoformat()
        }
        
        temp_file = self.metadata_dir / "policy_index_meta.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        temp_file.replace(self.metadata_file)
        logger.info(f"Updated index metadata file successfully for hash: {document_hash}")
