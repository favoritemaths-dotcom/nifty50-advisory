# ======================================================
# AI EXPLANATION ENGINE
# ======================================================

def generate_explanation(
    stock,
    score,
    recommendation,
    reasons,
    risk_profile,
    time_horizon
):
    """
    Generates a structured, human-readable explanation for the AI recommendation.

    Inputs:
    - stock: stock symbol
    - score: final stock score (0–100)
    - recommendation: BUY / HOLD / AVOID
    - reasons: list of textual reasons
    - risk_profile: Conservative / Moderate / Aggressive
    - time_horizon: Short-term / Medium-term / Long-term

    Output:
    - Markdown formatted explanation string
    """

    explanation = []

    # -----------------------------
    # HEADER
    # -----------------------------
    explanation.append(f"### 🤖 AI Advisory View – {stock}")
    explanation.append(f"**Overall Score:** {score}/100")
    explanation.append(f"**Recommendation:** **{recommendation}**")
    explanation.append(f"**Risk Profile:** {risk_profile}")
    explanation.append(f"**Investment Horizon:** {time_horizon}")

    # -----------------------------
    # INTERPRET SCORE
    # -----------------------------
    if score >= 75:
        score_view = "Strong overall fundamentals and risk alignment."
    elif score >= 60:
        score_view = "Balanced setup with manageable risks."
    elif score >= 50:
        score_view = "Mixed signals; caution warranted."
    else:
        score_view = "Weak setup with elevated downside risks."

    explanation.append(f"**Score Interpretation:** {score_view}")

    # -----------------------------
    # KEY FACTORS
    # -----------------------------
    if reasons:
        explanation.append("#### 🔍 Key Factors Considered")
        for r in reasons:
            explanation.append(f"• {r}")

    # -----------------------------
    # RISK PROFILE ALIGNMENT
    # -----------------------------
    profile_note = {
        "Conservative": "focuses on capital preservation and downside protection.",
        "Moderate": "balances growth potential with risk control.",
        "Aggressive": "prioritizes upside potential and growth."
    }

    explanation.append(
        f"This recommendation aligns with a strategy that "
        f"{profile_note.get(risk_profile, 'balances risk and reward')}."
    )

    # -----------------------------
    # TIME HORIZON CONTEXT
    # -----------------------------
    if time_horizon == "Short-term":
        explanation.append(
            "For a short-term horizon, valuation comfort and near-term risk control "
            "are especially important."
        )
    elif time_horizon == "Medium-term":
        explanation.append(
            "For a medium-term horizon, earnings visibility and balance-sheet strength "
            "play a critical role."
        )
    else:
        explanation.append(
            "For a long-term horizon, sustainable growth, capital efficiency, "
            "and financial resilience are key drivers of returns."
        )

    # -----------------------------
    # DISCLAIMER
    # -----------------------------
    explanation.append(
        "_This is a rule-based decision-support insight, not financial advice._"
    )

    return "\n\n".join(explanation)
