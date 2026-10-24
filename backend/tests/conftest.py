import pytest
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.rag.engine import RAGEngine

@pytest.fixture(scope="session", autouse=True)
def ensure_indexed():
    """Ensure vector store is initialized for tests."""
    engine = RAGEngine()
    engine.initialize_on_startup()
    return engine
