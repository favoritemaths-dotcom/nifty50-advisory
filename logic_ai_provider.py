# ============================================================
# AI PROVIDER ABSTRACTION LAYER
# Supports: Mock (fallback), Gemini (active), OpenAI (future)
# ============================================================

import os
import requests
from typing import Dict, Optional


# ----------------------------
# Base Interface
# ----------------------------
class AIProvider:
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        raise NotImplementedError


# ----------------------------
# Mock Provider (SAFE FALLBACK)
# ----------------------------
class MockAIProvider(AIProvider):
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        rb = context.get("rule_based_summary", {})
        return (
            "🧠 **AI Advisor (Rule-Based Fallback)**\n\n"
            "⚠️ External AI unavailable. Showing disciplined fallback analysis.\n\n"
            f"**Recommendation:** {rb.get('recommendation', 'N/A')}\n"
            f"**Score:** {rb.get('score', 'N/A')}\n"
            f"**Confidence:** {rb.get('confidence', 'N/A')}\n"
            f"**Risk Profile:** {rb.get('risk_profile', 'N/A')}\n\n"
            "This response is generated from internal models only."
        )


# ----------------------------
# Gemini Provider (FREE TIER)
# ----------------------------
class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-pro:generateContent"
        )

    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        system_rules = context.get("system_rules", "")
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""
{system_rules}

Investor Question:
{question}

Context:
{context}
"""
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            f"{self.endpoint}?key={self.api_key}",
            json=payload,
            timeout=20,
        )

        response.raise_for_status()
        data = response.json()

        return (
            data["candidates"][0]["content"]["parts"][0]["text"]
        )


# ----------------------------
# Provider Selector (AUTO)
# ----------------------------
def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Auto-selects the best available AI provider.
    Priority:
    1. Gemini (if API key exists)
    2. Mock fallback
    """

    # Explicit override (future use)
    if provider_name == "mock":
        return MockAIProvider()

    if provider_name == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key:
            return GeminiAIProvider(key)
        return MockAIProvider()

    # AUTO MODE
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        return GeminiAIProvider(gemini_key)

    return MockAIProvider()
