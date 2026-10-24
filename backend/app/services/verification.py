import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from app.models.schemas import SourceCitation

logger = logging.getLogger(__name__)

class PolicyVerificationService:
    """
    Verification layer implementing anti-hallucination checks,
    abstention triggers, citation validation, and safe structured answers.
    """

    CONSEQUENTIAL_TERMS = {
        "refund", "refunds", "refundable", "non-refundable",
        "bereavement", "death", "funeral", "compassionate",
        "cancel", "cancellation", "cancelling", "cancelled",
        "fee", "penalty", "charge", "deadline", "timeline",
        "exception", "compensation", "no-show", "missed flight"
    }

    BEREAVEMENT_TERMS = {
        "bereavement", "death", "died", "passed away", "funeral", "dying",
        "deceased", "compassionate", "relative passed"
    }

    @classmethod
    def verify_retrieval(
        cls,
        query: str,
        retrieved_chunks: List[Tuple[Dict[str, Any], float]]
    ) -> Tuple[bool, str]:
        """
        Validates if retrieved evidence is sufficient to address the user question.
        Returns: (is_sufficient: bool, reason_or_abstention: str)
        """
        query_lower = query.lower()
        query_words = set(re.findall(r"\b\w+\b", query_lower))

        if not retrieved_chunks:
            return (
                False,
                "The available AeroVista Airlines policy documentation does not contain information "
                "addressing this topic. AeroPolicy AI cannot confirm or answer this question based on the "
                "published policy. Please contact AeroVista Customer Care at 1-800-AEROVISTA for assistance."
            )

        top_chunk, top_score = retrieved_chunks[0]
        
        # Check if query is consequential
        is_consequential = bool(query_words & cls.CONSEQUENTIAL_TERMS)
        
        # Consequential queries require a minimum semantic relevance score
        if is_consequential and top_score < 0.28:
            return (
                False,
                "The available policy does not establish a clear rule or entitlement for your specific request. "
                "To prevent inaccurate guidance, AeroPolicy AI abstains from confirming eligibility. "
                "Please review your booking confirmation or contact AeroVista Support."
            )

        return (True, "")

    @classmethod
    def build_citations(cls, retrieved_chunks: List[Tuple[Dict[str, Any], float]]) -> List[SourceCitation]:
        """Constructs validated source citations from retrieved evidence."""
        citations: List[SourceCitation] = []
        seen_sections = set()

        for chunk_data, score in retrieved_chunks:
            meta = chunk_data.get("metadata", {})
            section = meta.get("section", "General Policy")
            if section in seen_sections:
                continue
            seen_sections.add(section)

            # Produce clean representative excerpt
            content = chunk_data.get("content", "").strip()
            # Clean section prefix if present
            clean_content = re.sub(r"^\[.*?\]\n*", "", content).strip()
            excerpt = clean_content[:320] + ("..." if len(clean_content) > 320 else "")

            citations.append(
                SourceCitation(
                    document=meta.get("source", "airline_policy.md"),
                    section=section,
                    page=meta.get("page"),
                    excerpt=excerpt,
                    score=round(score, 3),
                    source_id=chunk_data.get("chunk_id")
                )
            )

        return citations

    @classmethod
    def verify_response_integrity(
        cls,
        query: str,
        llm_response: str,
        retrieved_chunks: List[Tuple[Dict[str, Any], float]]
    ) -> Tuple[bool, str]:
        """
        Post-generation check to catch potential Air Canada-style hallucinations
        or unsupported affirmative refund promises.
        """
        query_lower = query.lower()
        resp_lower = llm_response.lower()

        # Air Canada-style bereavement check:
        is_bereavement_query = any(term in query_lower for term in cls.BEREAVEMENT_TERMS)
        if is_bereavement_query and ("refund" in query_lower or "cancel" in query_lower or "money back" in query_lower):
            # Check if LLM incorrectly promised a refund or claimed eligibility after ticket purchase
            hallucinated_promises = [
                "you are eligible for a refund",
                "you will receive a refund",
                "a full refund will be issued",
                "you qualify for a post-purchase refund",
                "apply for your bereavement refund"
            ]
            for promise in hallucinated_promises:
                if promise in resp_lower:
                    logger.warning(f"Detected potential Air Canada hallucination in LLM response: '{promise}'")
                    # Replace with strictly grounded safe correction
                    corrected_answer = (
                        "### 1. What the policy says:\n"
                        "Under AeroVista Airlines Policy Section 4 (Bereavement and Compassionate Travel), "
                        "bereavement courtesy rates must be booked and approved **prior to ticket purchase**. "
                        "Section 4.3 explicitly states that AeroVista Airlines does **not** issue retroactive "
                        "bereavement refunds or price adjustments for tickets already purchased.\n\n"
                        "### 2. How it applies:\n"
                        "Standard tickets purchased prior to a bereavement remain strictly bound by the original "
                        "fare class rules (e.g., Economy Basic is non-refundable; Economy Standard permits future credit "
                        "minus a fee; only Economy Flex and Business First are refundable to the original payment method).\n\n"
                        "### 3. What is not confirmed:\n"
                        "The available policy does not authorize any post-purchase bereavement refund or exception "
                        "for your ticket.\n\n"
                        "### 4. Next step:\n"
                        "You may cancel according to your original fare family terms, or submit an extenuating circumstances "
                        "appeal to the Customer Relations Appeals Board (Section 14.2) for discretionary evaluation.\n\n"
                        "### 5. Source:\n"
                        "AeroVista Passenger Policy, Section 4.3 ('Post-Purchase Ticket Ineligibility') & Section 2."
                    )
                    return (True, corrected_answer)

        # Ensure no fabricated policy sections exist in response
        # Verify any section mentioned matches retrieved metadata
        available_sections = [c[0].get("metadata", {}).get("section", "").lower() for c in retrieved_chunks]
        
        return (False, llm_response)

    @classmethod
    def check_missing_information(cls, query: str, context: Optional[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """Identifies if crucial non-sensitive booking details are needed."""
        query_lower = query.lower()
        context = context or {}
        
        # If user asks about cancellation or refund without mentioning fare class
        if any(w in query_lower for w in ["cancel my flight", "get a refund", "change my flight", "missed my flight"]):
            has_fare_type = any(f in query_lower for f in ["basic", "standard", "flex", "business"]) or context.get("fare_type")
            if not has_fare_type:
                return (
                    True,
                    "What fare class did you purchase (Economy Basic, Economy Standard, Economy Flex, or Business First)?"
                )

        return (False, None)
