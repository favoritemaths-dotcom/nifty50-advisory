# logic_ai_provider.py
# ==========================================
# Vertex AI Gemini Provider (Production Ready)
# ==========================================

from typing import Dict, Optional
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel


# ==========================================
# Base Interface
# ==========================================
class AIProvider:
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        raise NotImplementedError


# ==========================================
# Mock Provider (Fallback)
# ==========================================
class MockAIProvider(AIProvider):
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        rb = context.get("rule_based_summary", {})

        return (
            "🧠 AI Advisor (Rule-Based Fallback)\n\n"
            "⚠️ External AI unavailable.\n\n"
            f"**Question:** {question}\n\n"
            f"**Recommendation:** {rb.get('recommendation', 'N/A')}\n"
            f"**Score:** {rb.get('score', 'N/A')}\n"
            f"**Confidence:** {rb.get('confidence', 'N/A')}\n\n"
            "This response is generated from internal logic only."
        )


# ==========================================
# Vertex AI Gemini Provider
# ==========================================
class GeminiVertexProvider(AIProvider):
    def __init__(self):
        # Assumes aiplatform.init() already called
        self.model = GenerativeModel("gemini-1.5-flash")

    def explain_recommendation(self, *, question: str, context: Dict) -> str:

        rb = context.get("rule_based_summary", {})
        system_rules = context.get("system_rules", "")

        prompt = f"""
{system_rules}

Investor Question:
{question}

Rule-Based Summary:
Recommendation: {rb.get('recommendation')}
Score: {rb.get('score')}
Confidence: {rb.get('confidence')}
Risk Profile: {rb.get('risk_profile')}
Reasons: {rb.get('reasons')}
Market: {rb.get('market')}
"""

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 512,
            },
        )

        return response.text


# ==========================================
# Provider Selector
# ==========================================
def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    try:
        return GeminiVertexProvider()
    except Exception:
        return MockAIProvider()