# logic_ai_provider.py
# =================================================
# Vertex AI Gemini Provider (Production Ready)
# =================================================

from typing import Dict, Optional
import streamlit as st
from google.oauth2 import service_account
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel

# -------------------------------------------------
# Base Interface
# -------------------------------------------------
class AIProvider:
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        raise NotImplementedError


# -------------------------------------------------
# Mock / Fallback Provider
# -------------------------------------------------
class FallbackAIProvider(AIProvider):
    def explain_recommendation(self, *, question: str, context: Dict) -> str:
        rb = context.get("rule_based_summary", {})
        return (
            "🧠 **AI Advisor (Rule-Based Fallback)**\n\n"
            "⚠️ External AI unavailable.\n\n"
            f"**Question:** {question}\n\n"
            f"**Recommendation:** {rb.get('recommendation', 'N/A')}\n"
            f"**Score:** {rb.get('score', 'N/A')}\n"
            f"**Confidence:** {rb.get('confidence', 'N/A')}\n\n"
            "This response is generated purely from internal logic."
        )


# -------------------------------------------------
# Vertex Gemini Provider
# -------------------------------------------------
class GeminiVertexProvider(AIProvider):
    def __init__(self):
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


# -------------------------------------------------
# Vertex Credential Loader (SINGLE SOURCE OF TRUTH)
# -------------------------------------------------
def _load_vertex_credentials() -> bool:
    if "vertex_ai" not in st.secrets:
        return False

    creds_dict = dict(st.secrets["vertex_ai"])

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict
    )

    aiplatform.init(
        project=creds_dict["project_id"],
        location="us-central1",
        credentials=credentials,
    )

    return True


# 🔴 STEP 4 — THIS LINE WAS MISSING / CONFUSED BEFORE
VERTEX_READY = _load_vertex_credentials()


# -------------------------------------------------
# Provider Selector
# -------------------------------------------------
def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    if not VERTEX_READY:
        return FallbackAIProvider()

    return GeminiVertexProvider()
