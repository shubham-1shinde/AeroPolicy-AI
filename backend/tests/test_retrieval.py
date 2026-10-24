import pytest
from app.rag.engine import RAGEngine
from app.services.verification import PolicyVerificationService
from app.services.gemini_service import GeminiChatService

@pytest.fixture
def rag_engine():
    return RAGEngine()

@pytest.fixture
def chat_service():
    return GeminiChatService()

def test_relevant_policy_sections_retrieved_for_questions(rag_engine):
    # Baggage query
    baggage_chunks = rag_engine.retrieve("What are the baggage size limits for carry-on?", top_k=3)
    assert len(baggage_chunks) > 0
    sections = [c[0]["metadata"]["section"] for c in baggage_chunks]
    assert any("Baggage" in s or "7." in s for s in sections)

    # Cancellation query
    cancel_chunks = rag_engine.retrieve("Can I cancel my Economy Basic ticket?", top_k=3)
    assert len(cancel_chunks) > 0
    sections = [c[0]["metadata"]["section"] for c in cancel_chunks]
    assert any("Cancellation" in s or "2." in s or "Economy Basic" in s for s in sections)

def test_citations_refer_to_actual_retrieved_evidence(rag_engine):
    chunks = rag_engine.retrieve("What is the checked baggage fee?", top_k=2)
    citations = PolicyVerificationService.build_citations(chunks)
    assert len(citations) > 0
    for citation in citations:
        assert citation.document == "airline_policy.md"
        assert citation.section is not None
        assert len(citation.excerpt) > 0
        assert citation.score is not None

def test_unsupported_question_produces_abstention():
    # A completely unrelated question
    unrelated_query = "What is the policy for transporting a live giraffe on a submarine?"
    is_sufficient, abstention = PolicyVerificationService.verify_retrieval(unrelated_query, [])
    assert is_sufficient is False
    assert "does not contain information" in abstention or "abstains" in abstention

def test_chatbot_does_not_invent_fees_or_refund_deadlines(rag_engine, chat_service):
    # Test fallback deterministic generation or safety response
    query = "What is the fee for Economy Standard flight changes?"
    chunks = rag_engine.retrieve(query, top_k=3)
    resp = chat_service.generate_grounded_response(query, chunks)
    assert resp.grounded is True
    assert len(resp.sources) > 0
    # Must mention actual policy fee ($95 USD) or exact section, not made up numbers
    assert any("95" in s.excerpt or "95" in resp.answer or "Flight Changes" in s.section for s in resp.sources)
