# ======================================================
# INVESTOR BEHAVIORAL BIAS ANALYSIS
# ======================================================

def behavioral_bias_analysis(
    recommendation,
    risk_profile,
    time_horizon,
    market
):
    """
    Detects common investor behavioral biases based on:
    - recommendation
    - investor risk profile
    - time horizon
    - market regime

    Returns:
    {
        "biases": [list of strings],
        "behavior_score": int (0–100)
    }
    """

    biases = []
    score = 0

    regime = market.get("regime", "Neutral")

    # --------------------------------------------------
    # FOMO (Fear of Missing Out)
    # --------------------------------------------------
    if (
        recommendation.startswith("BUY")
        and regime in ["Bull Market", "Euphoria"]
        and risk_profile == "Aggressive"
    ):
        biases.append(
            "⚠️ FOMO Risk: Aggressive buying during euphoric market conditions."
        )
        score += 25

    # --------------------------------------------------
    # Loss Aversion
    # --------------------------------------------------
    if (
        recommendation.startswith("HOLD")
        and regime in ["Bear Market", "Risk-Off"]
    ):
        biases.append(
            "🐢 Loss Aversion: Holding positions despite adverse market conditions."
        )
        score += 20

    # --------------------------------------------------
    # Overconfidence
    # --------------------------------------------------
    if (
        recommendation.startswith("BUY")
        and risk_profile == "Conservative"
    ):
        biases.append(
            "🧠 Overconfidence: Action not aligned with conservative risk profile."
        )
        score += 20

    # --------------------------------------------------
    # Impatience / Short-termism
    # --------------------------------------------------
    if (
        time_horizon.lower().startswith("short")
        and regime in ["High Volatility", "Risk-Off"]
    ):
        biases.append(
            "⏳ Impatience Risk: Short-term decisions in volatile market conditions."
        )
        score += 15

    # --------------------------------------------------
    # Anchoring Bias
    # --------------------------------------------------
    if recommendation.startswith("HOLD") and regime == "Neutral":
        biases.append(
            "⚓ Anchoring Bias: Holding based on past price levels rather than fresh data."
        )
        score += 10

    # --------------------------------------------------
    # Default case
    # --------------------------------------------------
    if not biases:
        biases.append("✅ No major behavioral biases detected.")
        score = 0

    score = min(score, 100)

    return {
        "biases": biases,
        "behavior_score": score
    }


# ======================================================
# BEHAVIORAL RISK BAND
# ======================================================

def behavioral_risk_band(score):
    """
    Converts behavior score into a qualitative band
    """

    if score >= 60:
        return "High Behavioral Risk"
    elif score >= 30:
        return "Moderate Behavioral Risk"
    else:
        return "Low Behavioral Risk"


# ======================================================
# BEHAVIORAL NUDGES
# ======================================================

def behavioral_nudges(biases):
    """
    Converts detected biases into corrective nudges
    """

    nudges = []

    for b in biases:
        if "FOMO" in b:
            nudges.append(
                "Use staggered entry instead of lump-sum deployment."
            )

        if "Loss Aversion" in b:
            nudges.append(
                "Re-evaluate the investment thesis instead of anchoring to past prices."
            )

        if "Overconfidence" in b:
            nudges.append(
                "Align position sizing strictly with your stated risk profile."
            )

        if "Impatience" in b:
            nudges.append(
                "Reduce position size or extend the investment horizon."
            )

        if "Anchoring" in b:
            nudges.append(
                "Base decisions on updated fundamentals rather than historical prices."
            )

    if not nudges:
        nudges.append(
            "Maintain discipline and continue periodic portfolio review."
        )

    return nudges
