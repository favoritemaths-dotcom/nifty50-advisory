# logic_ai_explain.py

def ai_ask_why(
    question,
    recommendation,
    score,
    confidence,
    reasons,
    risk_profile,
    market,
    portfolio_mode=False
):
    """
    Deterministic AI-style explanation engine.
    Safe, rule-based, no hallucinations.
    """

    q = question.lower()
    response = []

    # ----------------------------------
    # WHY BUY / HOLD / AVOID
    # ----------------------------------
    if "why" in q and ("buy" in q or "hold" in q or "avoid" in q):
        response.append(
            f"The recommendation is **{recommendation}** with a score of **{score}/100** "
            f"and **{confidence}**."
        )

        if reasons:
            response.append("Key drivers behind this decision:")
            for r in reasons[:5]:
                response.append(f"• {r}")

    # ----------------------------------
    # RISK QUESTION
    # ----------------------------------
    elif "risk" in q:
        response.append("Primary risks identified:")

        risks = [r for r in reasons if "⚠️" in r or "risk" in r.lower()]
        if risks:
            for r in risks:
                response.append(f"• {r}")
        else:
            response.append("• No major red flags detected at this stage.")

        response.append(
            f"Market regime: **{market.get('regime', 'Neutral')}**"
        )

    # ----------------------------------
    # CONFIDENCE QUESTION
    # ----------------------------------
    elif "confidence" in q:
        response.append(
            f"The confidence level is **{confidence}**, based on score strength, "
            f"risk flags, and profile alignment."
        )

        if risk_profile == "Conservative" and recommendation == "BUY":
            response.append(
                "⚠️ Note: Conservative profile reduces conviction despite positive signals."
            )

    # ----------------------------------
    # PORTFOLIO MODE
    # ----------------------------------
    elif portfolio_mode:
        response.append(
            "This is a **portfolio-level decision**, considering diversification, "
            "sector exposure, and aggregate risk."
        )

    # ----------------------------------
    # FALLBACK
    # ----------------------------------
    else:
        response.append(
            "You can ask things like:\n"
            "• Why is this a BUY?\n"
            "• What are the risks?\n"
            "• How confident is this recommendation?"
        )

    return "\n".join(response)
