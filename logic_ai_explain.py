import streamlit as st
import json
import os
from google.oauth2 import service_account
from google.cloud import aiplatform

# logic_ai_explain.py
# --------------------------------------------
# AI Explanation Layer (Vertex Gemini + Fallback)
# --------------------------------------------

import os
from logic_ai_provider import get_ai_provider
from logic_ai_memory import load_memory, save_to_memory

def _load_vertex_credentials():
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

def _validate_vertex_env():
    """
    Ensures required Vertex AI environment variables exist.
    This avoids silent fallback and gives clear errors.
    """
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    if not project:
        raise RuntimeError(
            "Missing GOOGLE_CLOUD_PROJECT environment variable. "
            "Set it to your GCP Project ID (e.g. gen-lang-client-0161334899)."
        )

    if not location:
        raise RuntimeError(
            "Missing GOOGLE_CLOUD_LOCATION environment variable. "
            "Recommended: us-central1."
        )


def ai_ask_why(
    question: str,
    recommendation: str,
    score: int,
    confidence: str,
    reasons: list,
    risk_profile: str,
    market: str = None,
    portfolio_mode: bool = False,
    identifier: str = "default",
):
    """
    Senior AI explanation layer.
    Uses Vertex Gemini if available, otherwise fallback.
    """

    # ✅ Validate environment early
    _validate_vertex_env()

    provider = get_ai_provider()

    SYSTEM_RULES = """
You are a senior investment advisor reviewing a rule-based investment engine.

This engine provides:
- Quantitative scores
- Valuation metrics
- Risk flags
- Portfolio logic

You are NOT bound to agree with it.

You MAY:
- Challenge the recommendation
- Highlight risks not fully captured in metrics
- Add macro, sector, or qualitative insights
- Identify blind spots or false confidence

You MUST:
- Clearly separate rule-based facts from your own judgement
- Never fabricate numbers or data
- State uncertainty explicitly when information is insufficient
- Remain conservative and risk-aware

Your goal is to help a disciplined investor avoid mistakes.
"""

    mode = "portfolio" if portfolio_mode else "stock"
    memory = load_memory(mode, identifier)

    context = {
        "system_rules": SYSTEM_RULES,
        "rule_based_summary": {
            "recommendation": recommendation,
            "score": score,
            "confidence": confidence,
            "reasons": reasons,
            "risk_profile": risk_profile,
            "market": market,
        },
        "investor_question": question,
        "analysis_mode": mode,
        "previous_questions": memory,
        "response_format": [
            "1. Rule-Based Summary",
            "2. Independent AI Assessment",
            "3. Risks Possibly Underestimated",
            "4. Signals Possibly Overlooked",
            "5. What I Would Watch Going Forward",
        ],
    }

    answer = provider.explain_recommendation(
        question=question,
        context=context,
    )

    save_to_memory(mode, identifier, question, answer)
    return answer


def safe_ai_ask_why(**kwargs):
    """
    Safe wrapper for Streamlit UI.
    """
    try:
        return ai_ask_why(**kwargs)
    except Exception as e:
        return (
            "❌ AI ERROR:\n\n"
            f"{str(e)}\n\n"
            "You can still rely on the rule-based analysis above."
        )
