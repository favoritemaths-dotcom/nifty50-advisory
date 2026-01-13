# ============================================================
# AI PROVIDER ABSTRACTION LAYER
# Safe scaffold – no external API calls yet
# ============================================================

from typing import Dict, List, Optional


class AIProvider:
    """
    Base interface for AI providers (ChatGPT, Gemini, etc.)
    """

    def explain_recommendation(
        self,
        question: str,
        context: Dict
    ) -> str:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    """
    Default provider used until real AI is enabled.
    This keeps the app stable and deployable.
    """

    def explain_recommendation(
        self,
        question: str,
        context: Dict
    ) -> str:
        recommendation = context.get("recommendation", "N/A")
        score = context.get("score", "N/A")
        confidence = context.get("confidence", "N/A")
        risk_profile = context.get("risk_profile", "N/A")

        return (
            f"🔍 **AI Insight (Mock Mode)**\n\n"
            f"**Your Question:** {question}\n\n"
            f"**Recommendation:** {recommendation}\n"
            f"**Score:** {score}\n"
            f"**Confidence:** {confidence}\n"
            f"**Risk Profile:** {risk_profile}\n\n"
            f"This recommendation is derived from a combination of:\n"
            f"- Fundamentals quality\n"
            f"- Valuation comfort\n"
            f"- News sentiment\n"
            f"- Risk alignment\n\n"
            f"⚠️ This is a placeholder AI response. "
            f"Live AI reasoning (ChatGPT / Gemini) will be enabled soon."
        )


# ------------------------------------------------------------
# Provider selector (future-proof)
# ------------------------------------------------------------

def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Returns the active AI provider.
    Default = MockAIProvider
    """
    return MockAIProvider()
