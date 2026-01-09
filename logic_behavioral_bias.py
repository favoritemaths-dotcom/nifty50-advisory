def behavioral_bias_analysis(
    recommendation,
    risk_profile,
    time_horizon,
    market
):
    biases = []
    score = 0

    regime = market.get("regime", "Neutral")

    # FOMO
    if recommendation == "BUY" and regime in ["Bullish", "Euphoria"] and risk_profile == "Aggressive":
        biases.append("⚠️ FOMO Risk: Aggressive buying during euphoric markets.")
        score += 25

    # Loss aversion
    if recommendation == "HOLD" and regime in ["Bearish", "Risk-Off"]:
        biases.append("🐢 Loss Aversion: Holding despite weak market conditions.")
        score += 20

    # Overconfidence
    if recommendation == "BUY" and risk_profile == "Conservative":
        biases.append("🧠 Overconfidence: Action not aligned with risk profile.")
        score += 20

    # Impatience
    if time_horizon == "Short Term" and regime in ["High Volatility", "Risk-Off"]:
        biases.append("⏳ Impatience Risk: Short-term horizon in volatile markets.")
        score += 15

    if not biases:
        biases.append("✅ No major behavioral biases detected.")

    score = min(score, 100)

    return {
        "biases": biases,
        "behavior_score": score
    }


def behavioral_risk_band(score):
    if score >= 60:
        return "High Behavioral Risk"
    elif score >= 30:
        return "Moderate Behavioral Risk"
    else:
        return "Low Behavioral Risk"


def behavioral_nudges(biases):
    nudges = []

    for b in biases:
        if "FOMO" in b:
            nudges.append("Consider staggered buying instead of lump-sum deployment.")
        if "Loss Aversion" in b:
            nudges.append("Re-evaluate the thesis instead of anchoring to past prices.")
        if "Overconfidence" in b:
            nudges.append("Align position sizing with your stated risk profile.")
        if "Impatience" in b:
            nudges.append("Reduce position size or extend your time horizon.")

    if not nudges:
        nudges.append("Maintain discipline and continue periodic review.")

    return nudges
