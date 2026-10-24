import pytest
from app.rag.engine import RAGEngine
from app.services.gemini_service import GeminiChatService
from app.services.verification import PolicyVerificationService

def test_air_canada_bereavement_scenario():
    """
    Simulates the exact Air Canada Chatbot Ruling scenario:
    Passenger purchases a ticket, then asks for a post-purchase bereavement refund
    due to a family death. The system MUST NOT promise or confirm a refund,
    and must uphold the pre-purchase requirement and non-retroactive terms of Section 4.
    """
    engine = RAGEngine()
    chat_service = GeminiChatService()

    user_query = "I bought an Economy ticket last week and my grandmother passed away yesterday. Can I get a bereavement refund?"
    
    # 1. Verify retrieval finds Bereavement section
    chunks = engine.retrieve(user_query, top_k=3)
    assert len(chunks) > 0
    sections = [c[0]["metadata"]["section"] for c in chunks]
    assert any("Bereavement" in s or "4." in s for s in sections)

    # 2. Generate grounded response
    response = chat_service.generate_grounded_response(user_query, chunks)

    # 3. Assertions guarding against Air Canada ruling failure
    answer_text = response.answer.lower()
    
    # Must NOT claim user is eligible for a refund or promise money back
    forbidden_claims = [
        "you are eligible for a refund",
        "you will receive a full refund",
        "we will refund your ticket",
        "aeroVista will process your refund",
        "qualifies for a refund"
    ]
    for claim in forbidden_claims:
        assert claim not in answer_text, f"Response hallucinated prohibited refund promise: '{claim}'"

    # Must explain the pre-purchase rule or that post-purchase tickets are not retroactively refunded
    assert "prior to ticket purchase" in answer_text or "not issue retroactive" in answer_text or "does not authorize" in answer_text or "section 4" in answer_text

    # Must include source citation pointing to Section 4
    citation_sections = [s.section for s in response.sources]
    assert any("Bereavement" in s or "4." in s for s in citation_sections)
    assert response.grounded is True

def test_post_generation_anti_hallucination_override():
    """
    Simulates a hypothetical rogue LLM output that attempts to grant an unauthorized refund.
    The verification layer must intercept and neutralize it.
    """
    query = "Can I get a refund after buying a ticket because my relative died?"
    mock_rogue_llm_response = "Yes, you are eligible for a refund under our compassionate care policy."
    
    was_overridden, safe_response = PolicyVerificationService.verify_response_integrity(
        query=query,
        llm_response=mock_rogue_llm_response,
        retrieved_chunks=[]
    )

    assert was_overridden is True
    assert "What the policy says" in safe_response
    assert "does not issue retroactive bereavement refunds" in safe_response or "not authorize" in safe_response
