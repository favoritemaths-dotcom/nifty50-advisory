from logic_ai_memory import load_memory, save_to_memory
from logic_ai_provider import get_ai_provider


def ai_ask_why(
    question: str,
    recommendation: str,
    score: int,
    confidence: str,
    reasons: list,
    risk_profile: str,
    market: str = None,
    portfolio_mode: bool = False,
    identifier: str = "default"
):
    """
    Senior-AI explanation layer.
    Acts as an independent advisor reviewing the rule-based engine.
    """

    provider = get_ai_provider()

    # -------------------------------
    # SYSTEM RULES (Revised Step 9)
    # -------------------------------
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

    # -------------------------------
    # MEMORY
    # -------------------------------
    mode = "portfolio" if portfolio_mode else "stock"
    memory = load_memory(mode, identifier)

    # -------------------------------
    # CONTEXT (Structured Thinking)
    # -------------------------------
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
        "analysis_mode": "portfolio" if portfolio_mode else "single_stock",
        "previous_questions": memory,
        "response_format": [
            "1. Rule-Based Summary",
            "2. Independent AI Assessment",
            "3. Risks Possibly Underestimated",
            "4. Signals Possibly Overlooked",
            "5. What I Would Watch Going Forward",
        ],
    }

    # -------------------------------
    # AI CALL
    # -------------------------------
    answer = provider.explain_recommendation(
        system_rules=SYSTEM_RULES,
        question=question,
        context=context,
    )

    # -------------------------------
    # SAVE MEMORY
    # -------------------------------
    save_to_memory(mode, identifier, question, answer)

    return answer


# -------------------------------------------------
# SAFE WRAPPER (used by app.py)
# -------------------------------------------------
def safe_ai_ask_why(**kwargs):
    try:
        return ai_ask_why(**kwargs)
    except Exception:
        return (
            "⚠️ AI explanation temporarily unavailable.\n\n"
            "Reason: External AI service error.\n\n"
            "You can rely on the rule-based analysis above."
        )
