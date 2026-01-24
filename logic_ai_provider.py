# ==========================================
# AI PROVIDER ABSTRACTION LAYER
# Supports: Gemini (FREE) + Mock fallback
# ==========================================

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
            "This response is generated purely from internal rule-based models."
        )


# ----------------------------
# Gemini Provider (FREE – AI Studio)
# ----------------------------
class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = (
            "https://generativelanguage.googleapis.com/v1/"
            "models/gemini-1.0-pro:generateContent"
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
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]


# ----------------------------
# Provider Selector (AUTO)
# ----------------------------
def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Auto-selects best available provider.
    Priority:
    1. Gemini (if API key exists)
    2. Mock fallback
    """

    gemini_key = os.getenv("GEMINI_API_KEY")

    if provider_name == "mock":
        return MockAIProvider()

    if provider_name == "gemini" and gemini_key:
        return GeminiAIProvider(gemini_key)

    # AUTO MODE
    if gemini_key:
        return GeminiAIProvider(gemini_key)

    return MockAIProvider()
