# ============================================================
# AI EXPLANATION LOGIC (Provider-based)
# ============================================================

from logic_ai_provider import get_ai_provider


def ai_ask_why(
    question: str,
    recommendation: str,
    score: int,
    confidence: str,
    reasons: list,
    risk_profile: str,
    market: str = None,
    portfolio_mode: bool = False
):
    """
    Central AI explanation entry point.
    Uses provider abstraction (Mock for now).
    """

    provider = get_ai_provider()

    context = {
        "recommendation": recommendation,
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
        "risk_profile": risk_profile,
        "market": market,
        "portfolio_mode": portfolio_mode,
    }

    return provider.explain_recommendation(
        question=question,
        context=context
    )
