# ==========================================================
# AI PROVIDER ABSTRACTION LAYER
# Supports:
# - Gemini (FREE, active)
# - Mock fallback (safe)
# Future:
# - OpenAI (optional)
# ==========================================================

import os
import requests
from typing import Dict, Optional


# ==========================================================
# BASE INTERFACE
# ==========================================================
class AIProvider:
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        raise NotImplementedError


# ==========================================================
# MOCK PROVIDER (SAFE FALLBACK)
# ==========================================================
class MockAIProvider(AIProvider):
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        rb = context.get("rule_based_summary", {})

        return (
            "🧠 **AI Advisor (Rule-Based Fallback)**\n\n"
            "⚠️ External AI unavailable. Showing disciplined fallback analysis.\n\n"
            "**Rule-Based Summary**\n"
            f"- Recommendation: {rb.get('recommendation', 'N/A')}\n"
            f"- Score: {rb.get('score', 'N/A')}\n"
            f"- Confidence: {rb.get('confidence', 'N/A')}\n"
            f"- Risk Profile: {rb.get('risk_profile', 'N/A')}\n\n"
            "This response is generated using internal models only.\n"
            "Live AI reasoning (Gemini / OpenAI) will activate automatically when available."
        )


# ==========================================================
# GEMINI PROVIDER (FREE TIER)
# ==========================================================
class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = (
            "https://generativelanguage.googleapis.com/v1/models/"
            "gemini-1.5-flash:generateContent"
        )

    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        system_rules = context.get("system_rules", "")
        rb = context.get("rule_based_summary", {})

        prompt = f"""
{system_rules}

RULE-BASED FACTS
Recommendation: {rb.get('recommendation')}
Score: {rb.get('score')}
Confidence: {rb.get('confidence')}
Risk Profile: {rb.get('risk_profile')}
Market: {rb.get('market')}

Investor Question:
{question}

Instructions:
- Separate facts from judgement
- Highlight risks and blind spots
- Be conservative
- Do not fabricate data
"""

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ]
        }

        response = requests.post(
            f"{self.endpoint}?key={self.api_key}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        if not data.get("candidates"):
            return "⚠️ Gemini returned an empty response."

        return data["candidates"][0]["content"]["parts"][0]["text"]


# ==========================================================
# PROVIDER SELECTOR (AUTO MODE)
# ==========================================================
def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Auto-selects the best available AI provider.

    Priority:
    1. Explicit provider (future UI toggle)
    2. Gemini (if API key exists)
    3. Mock fallback (always safe)
    """

    # Explicit override (future use)
    if provider_name == "mock":
        return MockAIProvider()

    if provider_name == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key:
            return GeminiAIProvider(key)
        return MockAIProvider()

    # AUTO MODE (default)
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            return GeminiAIProvider(gemini_key)
    except Exception as e:
        print("[Gemini init failed]", e)

    return MockAIProvider()
