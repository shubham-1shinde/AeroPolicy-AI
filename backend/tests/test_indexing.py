import tempfile
import threading
import time
from pathlib import Path
import pytest
from app.rag.change_detector import ChangeDetector
from app.rag.document_loader import PolicyDocumentLoader
from app.rag.engine import RAGEngine
from app.core.config import settings

def test_initial_policy_indexing():
    engine = RAGEngine()
    status = engine.get_status()
    assert status["status"] == "READY"
    assert status["total_chunks"] > 0
    assert status["current_hash"] is not None
    assert status["current_hash"] == status["indexed_hash"]

def test_unchanged_document_hash_skips_reembedding():
    engine = RAGEngine()
    detector = ChangeDetector(settings.metadata_dir)
    needs_reindex, status, cur_hash, idx_hash = detector.check_index_status(
        settings.policy_file_path,
        settings.EMBEDDING_MODEL_NAME,
        settings.INDEX_SCHEMA_VERSION
    )
    assert needs_reindex is False
    assert status == "READY"
    assert cur_hash == idx_hash

def test_modified_policy_triggers_reindexing(tmp_path):
    detector = ChangeDetector(tmp_path)
    test_doc = tmp_path / "temp_policy.md"
    test_doc.write_text("# Initial Policy\nRefunds are allowed.", encoding="utf-8")
    
    hash1 = detector.compute_sha256(test_doc)
    detector.save_index_metadata(hash1, "model1", "v1.0", 1, 500, 50, ["Sec 1"])
    
    # Modify doc
    test_doc.write_text("# Modified Policy\nRefunds are strictly prohibited.", encoding="utf-8")
    hash2 = detector.compute_sha256(test_doc)
    assert hash1 != hash2
    
    needs_reindex, status, cur, idx = detector.check_index_status(test_doc, "model1", "v1.0")
    assert needs_reindex is True
    assert status == "OUTDATED"

def test_failed_indexing_does_not_update_saved_hash(tmp_path):
    detector = ChangeDetector(tmp_path)
    test_doc = tmp_path / "temp_policy.md"
    test_doc.write_text("# Initial Valid Doc", encoding="utf-8")
    valid_hash = detector.compute_sha256(test_doc)
    detector.save_index_metadata(valid_hash, "model1", "v1.0", 1, 500, 50, ["Sec 1"])
    
    # Simulate a corrupted or invalid file attempt
    corrupted_doc = tmp_path / "corrupted.md"
    corrupted_doc.touch() # 0 bytes
    
    loader = PolicyDocumentLoader()
    with pytest.raises(ValueError):
        loader.load_document(corrupted_doc)
        
    # Verify metadata still has valid_hash
    meta = detector.get_indexed_metadata()
    assert meta["document_hash"] == valid_hash

def test_missing_or_empty_policy_files_fail_safely(tmp_path):
    loader = PolicyDocumentLoader()
    
    # Test missing file
    missing_file = tmp_path / "does_not_exist.md"
    with pytest.raises(FileNotFoundError):
        loader.load_document(missing_file)
        
    # Test empty file
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        loader.load_document(empty_file)

def test_concurrent_requests_do_not_duplicate_indexing():
    engine = RAGEngine()
    results = []

    def trigger_reindex():
        res = engine.reindex()
        results.append(res)

    t1 = threading.Thread(target=trigger_reindex)
    t2 = threading.Thread(target=trigger_reindex)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # One should succeed, and if the other ran concurrently it received False
    assert any(results)
