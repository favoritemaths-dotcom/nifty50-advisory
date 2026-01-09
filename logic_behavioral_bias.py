def detect_behavioral_bias(
    recommendation,
    risk_profile,
    time_horizon,
    market
):
    biases = []

    regime = market.get("regime", "Neutral")

    if recommendation == "BUY" and regime in ["Bullish", "Euphoria"] and risk_profile == "Aggressive":
        biases.append("⚠️ FOMO Risk: Buying aggressively during euphoric markets.")

    if recommendation == "HOLD" and regime == "Bearish":
        biases.append("🐢 Loss Aversion: Holding despite weak market conditions.")

    if recommendation == "BUY" and risk_profile == "Conservative":
        biases.append("🧠 Overconfidence: Aggressive action not aligned with risk profile.")

    if time_horizon == "Short Term" and regime == "High Volatility":
        biases.append("⏳ Impatience Risk: Short horizon in volatile markets.")

    if not biases:
        biases.append("✅ No major behavioral biases detected.")

    return biases
