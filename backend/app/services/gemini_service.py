import logging
import os
from typing import List, Dict, Any, Tuple, Optional
from app.core.config import settings
from app.models.schemas import ChatResponse, SourceCitation
from app.services.verification import PolicyVerificationService

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are AeroPolicy AI, the official policy assistant for AeroVista Airlines.
Your sole mission is to answer customer questions strictly and accurately using ONLY the provided AeroVista Airlines Policy Evidence.

MANDATORY SAFETY & LEGAL DIRECTIVES (Air Canada Ruling Prevention):
1. Grounding Rule: Answer solely based on the explicit policy evidence provided in this prompt. Never extrapolate, speculate, invent, or assume rules not present in the text.
2. Anti-Hallucination & No Refund Promises: Never promise, confirm, or imply that a passenger is entitled to a refund, compensation, fee waiver, or exception unless the policy explicitly establishes it for their exact situation.
3. Air Canada Ruling Safeguard: For bereavement or compassionate situations, observe that AeroVista bereavement rates must be booked *prior* to ticket purchase. The policy explicitly forbids retroactive bereavement refunds on already purchased tickets. Never tell a customer who has already bought a ticket that they qualify for a bereavement refund.
4. Consequential Safe Answer Format: For questions involving refunds, cancellations, bereavement, fees, missed flights, or legal exceptions, you MUST structure your answer into these 5 clear points:
   - **1. What the policy says:** Concise summary of the exact rule.
   - **2. How it applies:** Clarify how the rule applies based on known facts and note any required conditions (e.g. fare class, timing).
   - **3. What is not confirmed:** Explicitly state what the policy does NOT authorize or what facts are missing.
   - **4. Next step:** State what the customer should do (e.g., provide fare type, check booking confirmation, or contact Customer Care/Appeals Board).
   - **5. Source:** Name the specific policy section and reference number cited.
5. Factual Inquiries: For simple factual inquiries (e.g. carry-on dimensions, check-in cutoff times, infant travel rules), provide a direct, concise factual response with the exact numbers and cite the relevant section.
6. Honest Abstention: If the provided policy evidence does not contain the answer, explicitly state: "The available AeroVista Airlines policy documentation does not establish or confirm an answer for this inquiry." Do not guess.
7. Privacy & Booking Details: Never ask for credit card numbers, passwords, or personal identifying information. Only ask for fare class, travel dates, or cancellation timing when needed to determine eligibility.
"""

class GeminiChatService:
    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and self.api_key != "your_actual_api_key_here")

    def generate_grounded_response(
        self,
        query: str,
        retrieved_chunks: List[Tuple[Dict[str, Any], float]],
        context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Coordinates retrieval verification, Gemini generation, citation formatting,
        and post-generation anti-hallucination validation.
        """
        # 1. Verification of retrieval evidence
        is_sufficient, abstention_msg = PolicyVerificationService.verify_retrieval(query, retrieved_chunks)
        if not is_sufficient:
            return ChatResponse(
                answer=abstention_msg,
                grounded=False,
                sources=[],
                needs_clarification=False,
                suggested_question="Would you like to speak with AeroVista Customer Care or view general policy sections?"
            )

        citations = PolicyVerificationService.build_citations(retrieved_chunks)
        needs_clarif, clarif_q = PolicyVerificationService.check_missing_information(query, context)

        # 2. Check if API Key is configured
        if not self.is_configured():
            logger.warning("GEMINI_API_KEY is not configured in backend .env")
            return self._fallback_grounded_answer(query, retrieved_chunks, citations, needs_clarif, clarif_q)

        # 3. Format Prompt with Context Chunks
        context_blocks = []
        for i, (chunk, score) in enumerate(retrieved_chunks, 1):
            meta = chunk.get("metadata", {})
            sec = meta.get("section", "General")
            content = chunk.get("content", "").strip()
            context_blocks.append(f"--- EVIDENCE PIECE #{i} (Section: {sec}, Relevance: {score:.2f}) ---\n{content}")

        evidence_text = "\n\n".join(context_blocks)
        
        user_prompt = f"""EVIDENCE FROM AEROVISTA AIRLINES POLICY:
{evidence_text}

USER QUESTION:
{query}

ADDITIONAL CONTEXT (if any):
{context or 'None provided'}

Please provide a strictly grounded, accurate response following your instructions."""

        # 4. Invoke Gemini API
        raw_answer = ""
        try:
            raw_answer = self._call_gemini_api(user_prompt)
        except Exception as e:
            logger.error(f"Error invoking Gemini API: {e}", exc_info=True)
            # Safe deterministic fallback grounded in top chunks
            return self._fallback_grounded_answer(
                query, retrieved_chunks, citations, needs_clarif, clarif_q,
                error_note="Note: AI live synthesis unavailable. Displaying direct grounded policy excerpts."
            )

        # 5. Post-generation safety and Air Canada check
        was_overridden, verified_answer = PolicyVerificationService.verify_response_integrity(
            query, raw_answer, retrieved_chunks
        )

        return ChatResponse(
            answer=verified_answer,
            grounded=True,
            sources=citations,
            needs_clarification=needs_clarif,
            suggested_question=clarif_q,
            policy_version="2026.2"
        )

    def _call_gemini_api(self, prompt: str) -> str:
        """Invokes official google-genai or google-generativeai SDK."""
        # Try google.genai (v2 SDK)
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1,
                    max_output_tokens=1000
                )
            )
            if response and response.text:
                return response.text.strip()
        except Exception as genai_err:
            logger.info(f"google.genai SDK call error or alternative fallback: {genai_err}")

        # Fallback to google.generativeai
        try:
            import google.generativeai as gai
            gai.configure(api_key=self.api_key)
            model = gai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_INSTRUCTION,
                generation_config={"temperature": 0.1, "max_output_tokens": 1000}
            )
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as legacy_err:
            raise RuntimeError(f"All Gemini invocation methods failed: {legacy_err}")

        raise RuntimeError("No text returned by Gemini API")

    def _fallback_grounded_answer(
        self,
        query: str,
        retrieved_chunks: List[Tuple[Dict[str, Any], float]],
        citations: List[SourceCitation],
        needs_clarif: bool,
        clarif_q: Optional[str],
        error_note: Optional[str] = None
    ) -> ChatResponse:
        """Deterministic policy summary for unit testing or when API key is not yet set."""
        query_lower = query.lower()
        
        # Air Canada bereavement deterministic handling
        if any(w in query_lower for w in ["bereavement", "death", "funeral"]):
            answer = (
                "### 1. What the policy says:\n"
                "AeroVista Airlines policy Section 4 governs bereavement travel. Bereavement courtesy rates "
                "must be booked and approved **prior to ticket purchase** with required documentation. "
                "Section 4.3 specifically establishes that tickets purchased prior to a bereavement are **not** eligible "
                "for retroactive bereavement refunds or price adjustments.\n\n"
                "### 2. How it applies:\n"
                "Standard tickets remain strictly bound by their original fare rules (e.g. Economy Basic is non-refundable; "
                "Economy Standard may be cancelled for future credit minus a $125 fee; only Economy Flex and Business First "
                "are refundable to original payment).\n\n"
                "### 3. What is not confirmed:\n"
                "The policy does not authorize any post-purchase bereavement refund for an already booked ticket.\n\n"
                "### 4. Next step:\n"
                "You may cancel under your fare class rules, or submit an extenuating appeal to the Customer Relations "
                "Appeals Board (Section 14.2).\n\n"
                "### 5. Source:\n"
                "AeroVista Passenger Policy, Section 4 ('Bereavement and Compassionate Travel Policy')."
            )
        elif any(w in query_lower for w in ["baggage", "luggage", "carry-on", "carry on", "checked bag"]):
            answer = (
                "### Baggage Allowance Summary:\n"
                "- **Personal Item:** 1 small item (max 40 x 30 x 15 cm / 16 x 12 x 6 in), fits under seat. Free in all fare classes.\n"
                "- **Carry-On Bag:** 1 rollaboard (max 55 x 40 x 23 cm / 22 x 16 x 9 in, max 10 kg / 22 lbs). Free in Economy Standard, Flex, and Business First. In Economy Basic, must be purchased ($35 online, $60 at gate).\n"
                "- **Checked Baggage:** Economy Basic: 0 included ($40 for 1st bag); Economy Standard: 1 included (max 23 kg / 50 lbs); Economy Flex: 2 included (23 kg each); Business First: 2 included (32 kg each).\n\n"
                "**Source:** Section 7 ('Baggage Allowance, Carry-on, Checked Baggage & Excess Fees')."
            )
        else:
            top_chunk, score = retrieved_chunks[0]
            sec = top_chunk.get("metadata", {}).get("section", "Policy Terms")
            text = top_chunk.get("content", "").strip()
            answer = (
                f"### Relevant Policy ({sec}):\n\n"
                f"{text}\n\n"
                "*(Information grounded directly in AeroVista Airlines Policy document)*"
            )

        if error_note:
            answer = f"{answer}\n\n> ⚠️ *{error_note}*"

        return ChatResponse(
            answer=answer,
            grounded=True,
            sources=citations,
            needs_clarification=needs_clarif,
            suggested_question=clarif_q,
            policy_version="2026.2"
        )
