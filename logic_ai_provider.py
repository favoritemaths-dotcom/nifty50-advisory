# =========================================================
# AI PROVIDER ABSTRACTION LAYER
# Gemini (FREE) + Mock fallback
# =========================================================

import os
import requests
from typing import Dict, Optional


# ---------------------------
# Base Interface
# ---------------------------
class AIProvider:
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        raise NotImplementedError


# ---------------------------
# SAFE FALLBACK PROVIDER
# ---------------------------
class MockAIProvider(AIProvider):
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        rb = context.get("rule_based_summary", {})

        return (
            "🧠 **AI Advisor (Rule-Based Fallback)**\n\n"
            "⚠️ External AI unavailable. Showing disciplined fallback analysis.\n\n"
            f"**Question:** {question}\n\n"
            f"**Recommendation:** {rb.get('recommendation', 'N/A')}\n"
            f"**Score:** {rb.get('score', 'N/A')}\n"
            f"**Confidence:** {rb.get('confidence', 'N/A')}\n"
            f"**Risk Profile:** {rb.get('risk_profile', 'N/A')}\n\n"
            "This response is generated from internal rule-based logic only."
        )


# ---------------------------
# GEMINI PROVIDER (WORKING)
# ---------------------------
class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-pro:generateContent"
        )

    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        system_rules = context.get("system_rules", "")
        rule_summary = context.get("rule_based_summary", {})

        prompt = f"""
{system_rules}

Investor Question:
{question}

Rule-Based Summary:
{rule_summary}

Respond clearly, conservatively, and structured.
"""

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        response = requests.post(
            f"{self.endpoint}?key={self.api_key}",
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Gemini API Error {response.status_code}: {response.text}"
            )

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


# ---------------------------
# PROVIDER SELECTOR (AUTO)
# ---------------------------
def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    gemini_key = os.getenv("GEMINI_API_KEY")

    if provider_name == "mock":
        return MockAIProvider()

    if provider_name == "gemini" and gemini_key:
        return GeminiAIProvider(gemini_key)

    # AUTO MODE
    if gemini_key:
        return GeminiAIProvider(gemini_key)

    return MockAIProvider()
