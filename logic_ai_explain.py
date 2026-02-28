# logic_ai_explain.py
# --------------------------------------------
# AI Explanation Layer (Vertex Gemini + Fallback)
# --------------------------------------------

import streamlit as st
import json

from google.oauth2 import service_account
from google.cloud import aiplatform

from logic_ai_provider import get_ai_provider
from logic_ai_memory import load_memory, save_to_memory


# ==========================================
# Secure Vertex Initialization
# ==========================================
def _load_vertex_credentials():
    try:
        if "vertex_ai" not in st.secrets:
            return False

        raw_json = st.secrets["vertex_ai"]["json"]
        creds_dict = json.loads(raw_json)

        credentials = service_account.Credentials.from_service_account_info(
            creds_dict
        )

        aiplatform.init(
            project=creds_dict["project_id"],
            location="us-central1",
            credentials=credentials,
        )

        return True

    except Exception as e:
        print("Vertex init failed:", e)
        return False


VERTEX_READY = _load_vertex_credentials()


# ==========================================
# AI Explanation Engine
# ==========================================
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


# ==========================================
# Safe Wrapper
# ==========================================
def safe_ai_ask_why(**kwargs):
    try:
        if not VERTEX_READY:
            return "⚠️ Vertex AI not configured properly."

        return ai_ask_why(**kwargs)

    except Exception as e:
        return (
            "❌ AI ERROR:\n\n"
            f"{str(e)}\n\n"
            "You can still rely on the rule-based analysis above."
        )
