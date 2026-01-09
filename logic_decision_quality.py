def decision_quality_score(
    recommendation,
    score,
    confidence,
    risk_profile,
    time_horizon,
    market,
    behavioral_score=None
):
    """
    Returns a decision quality score (0–100) and explanations
    """

    quality = 100
    notes = []

    # 1️⃣ Weak fundamentals but strong action
    if score < 50 and recommendation == "BUY":
        quality -= 25
        notes.append("Buying despite weak underlying score.")

    # 2️⃣ High confidence but weak score
    if "High" in confidence and score < 60:
        quality -= 15
        notes.append("High confidence not supported by fundamentals.")

    # 3️⃣ Risk profile mismatch
    if recommendation == "BUY" and risk_profile == "Conservative":
        quality -= 15
        notes.append("Aggressive action for a conservative profile.")

    # 4️⃣ Market regime contradiction
    regime = market.get("regime", "Neutral")
    if regime in ["Bearish", "Risk-Off"] and recommendation == "BUY":
        quality -= 15
        notes.append("Buying into adverse market regime.")

    # 5️⃣ Time horizon mismatch
    if time_horizon == "Short Term" and regime in ["High Volatility"]:
        quality -= 10
        notes.append("Short-term decision in volatile conditions.")

    # 6️⃣ Behavioral penalty
    if behavioral_score is not None:
        if behavioral_score >= 60:
            quality -= 15
            notes.append("High behavioral risk impacting decision quality.")

    quality = max(0, quality)

    if not notes:
        notes.append("Decision is logically consistent across dimensions.")

    return {
        "decision_quality_score": quality,
        "decision_quality_band": quality_band(quality),
        "notes": notes
    }


def quality_band(score):
    if score >= 80:
        return "High Quality Decision"
    elif score >= 60:
        return "Moderate Quality Decision"
    else:
        return "Low Quality Decision"
