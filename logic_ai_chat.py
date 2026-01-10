# logic_ai_chat.py

"""
AI Conversational Explainability Layer (Rule-Based)

This module answers natural-language questions like:
- Why is this a BUY / HOLD / REDUCE?
- What are the main risks?
- What would change this recommendation?
- Which factor matters the most?
- Why is confidence high / low?

Later, this file can be replaced with ChatGPT / Gemini
using the SAME function signature.
"""


def ai_ask_why(
    question,
    *,
    stock=None,
    score=None,
    recommendation=None,
    confidence=None,
    reasons=None,
    risk_triggers=None,
    market=None,
    portfolio_result=None
):
    """
    Main conversational entry point

    Parameters are passed explicitly so the AI never hallucinates.
    """

    q = question.lower().strip()

    # -------------------------------
    # BASIC SANITY
    # -------------------------------
    if not q:
        return "Please ask a clear question about the investment decision."

    # -------------------------------
    # WHY THIS RECOMMENDATION?
    # -------------------------------
    if "why" in q and ("buy" in q or "hold" in q or "avoid" in q or "reduce" in q):
        text = []
        if stock:
            text.append(f"### Why {recommendation} for {stock}")
        else:
            text.append(f"### Why {recommendation}")

        if score is not None:
            text.append(f"• Overall score is **{score}/100**")

        if confidence:
            text.append(f"• Confidence level is **{confidence}**")

        if reasons:
            text.append("• Key drivers:")
            for r in reasons[:6]:
                text.append(f"  - {r}")

        return "\n".join(text)

    # -------------------------------
    # WHAT ARE THE RISKS?
    # -------------------------------
    if "risk" in q or "downside" in q or "what can go wrong" in q:
        if risk_triggers:
            text = ["### Key Risk Factors to Monitor:"]
            for t in risk_triggers:
                text.append(f"• {t}")
            return "\n".join(text)
        return "No major downside risks detected at this time."

    # -------------------------------
    # WHAT WOULD CHANGE THIS DECISION?
    # -------------------------------
    if "change" in q or "invalidate" in q:
        if risk_triggers:
            return (
                "### This recommendation would change if:\n"
                + "\n".join(f"• {t}" for t in risk_triggers)
            )
        return "No immediate invalidation triggers identified."

    # -------------------------------
    # CONFIDENCE QUESTION
    # -------------------------------
    if "confidence" in q or "sure" in q:
        if confidence:
            return (
                f"### Confidence Assessment\n"
                f"The recommendation has **{confidence}** based on:\n"
                f"• Strength of fundamentals\n"
                f"• Risk flags\n"
                f"• Profile alignment"
            )
        return "Confidence data not available."

    # -------------------------------
    # PORTFOLIO QUESTIONS
    # -------------------------------
    if portfolio_result:
        if "portfolio" in q:
            score = portfolio_result.get("risk_score")
            warnings = portfolio_result.get("warnings", [])

            text = ["### Portfolio-Level Insight"]
            if score is not None:
                text.append(f"• Portfolio risk score: **{score}**")

            if warnings:
                text.append("• Key portfolio concerns:")
                for w in warnings:
                    text.append(f"  - {w}")
            else:
                text.append("• Portfolio structure appears balanced")

            return "\n".join(text)

    # -------------------------------
    # MARKET REGIME QUESTIONS
    # -------------------------------
    if "market" in q or "regime" in q:
        if market:
            return (
                f"### Market Context\n"
                f"• Current regime: **{market.get('regime')}**\n"
                f"• Impact: {market.get('note')}"
            )
        return "Market regime data unavailable."

    # -------------------------------
    # FALLBACK RESPONSE
    # -------------------------------
    return (
        "I can help explain:\n"
        "• Why this recommendation was given\n"
        "• Key risks and invalidation triggers\n"
        "• Confidence level\n"
        "• Portfolio-level insights\n\n"
        "Try asking: *Why is this a BUY?* or *What risks should I monitor?*"
    )
