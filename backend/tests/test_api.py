import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_health_endpoint():
    # Test GET /api/health
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["policy_status"] == "READY"
    assert data["indexed_chunks"] > 0
    assert data["model"] == settings.GEMINI_MODEL

    # Test HEAD / and HEAD /health for Render health checks
    head_root = client.head("/")
    assert head_root.status_code == 200

    head_health = client.head("/health")
    assert head_health.status_code == 200

    head_api_health = client.head("/api/health")
    assert head_api_health.status_code == 200

def test_policy_status_endpoint():
    response = client.get("/api/policy/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert data["current_hash"] is not None
    assert data["total_chunks"] > 0

def test_policy_sections_endpoint():
    response = client.get("/api/policy/sections")
    assert response.status_code == 200
    sections = response.json()
    assert isinstance(sections, list)
    assert len(sections) > 0
    assert any("Cancellation" in s["title"] or "Bereavement" in s["title"] for s in sections)

def test_policy_source_detail_endpoint():
    # First get a valid chunk_id
    status_resp = client.get("/api/policy/status")
    assert status_resp.status_code == 200
    
    # Query a valid chunk id
    valid_source_resp = client.get("/api/policy/source/chunk_1")
    assert valid_source_resp.status_code == 200
    data = valid_source_resp.json()
    assert data["source_id"] == "chunk_1"
    assert data["document"] == "airline_policy.md"
    assert len(data["full_text"]) > 0

    # Query an invalid source id
    invalid_resp = client.get("/api/policy/source/non_existent_chunk_9999")
    assert invalid_resp.status_code == 404

def test_reindex_authorization_protection():
    # Without token -> 403 Forbidden
    unauthorized = client.post("/api/policy/reindex")
    assert unauthorized.status_code == 403

    # With invalid token -> 403 Forbidden
    invalid_token = client.post("/api/policy/reindex", headers={"X-Admin-Token": "wrong-token"})
    assert invalid_token.status_code == 403

    # With valid token -> 200 OK
    authorized = client.post("/api/policy/reindex", headers={"X-Admin-Token": settings.ADMIN_API_TOKEN})
    assert authorized.status_code in [200, 409] # 200 or 409 if already locked

def test_chat_endpoint_validation():
    # Blank query
    empty_resp = client.post("/api/chat", json={"message": "   "})
    assert empty_resp.status_code == 400

    # Valid query
    chat_resp = client.post("/api/chat", json={"message": "What is the baggage allowance for Economy Basic?"})
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert "answer" in data
    assert data["grounded"] is True
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
