# ======================================================
# DECISION QUALITY ENGINE
# ======================================================

def quality_band(score):
    """
    Converts numeric decision quality score into a band
    """
    if score >= 80:
        return "High Quality Decision"
    elif score >= 60:
        return "Moderate Quality Decision"
    else:
        return "Low Quality Decision"


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
    Evaluates how logically sound a decision is across:
    - Fundamentals
    - Confidence alignment
    - Risk profile
    - Market regime
    - Behavioral biases

    Returns:
    {
        decision_quality_score: int (0–100),
        decision_quality_band: str,
        notes: list[str]
    }
    """

    quality = 100
    notes = []

    rec = recommendation.upper()
    regime = market.get("regime", "Neutral") if market else "Neutral"

    # --------------------------------------------------
    # 1️⃣ Weak fundamentals but aggressive action
    # --------------------------------------------------
    if score < 50 and rec == "BUY":
        quality -= 25
        notes.append("Buying despite weak underlying stock score.")

    # --------------------------------------------------
    # 2️⃣ High confidence not supported by score
    # --------------------------------------------------
    if "High" in confidence and score < 60:
        quality -= 15
        notes.append("High confidence not sufficiently supported by fundamentals.")

    # --------------------------------------------------
    # 3️⃣ Risk profile mismatch
    # --------------------------------------------------
    if rec == "BUY" and risk_profile == "Conservative":
        quality -= 15
        notes.append("Aggressive action does not align with conservative risk profile.")

    if rec == "AVOID" and risk_profile == "Aggressive" and score >= 60:
        quality -= 10
        notes.append("Avoiding despite reasonable score for aggressive profile.")

    # --------------------------------------------------
    # 4️⃣ Market regime contradiction
    # --------------------------------------------------
    if regime in ["Bear Market", "Risk-Off"] and rec == "BUY":
        quality -= 15
        notes.append("Buying into a defensive / risk-off market regime.")

    if regime in ["Bull Market", "Risk-On"] and rec == "AVOID":
        quality -= 10
        notes.append("Avoiding exposure during favorable market regime.")

    # --------------------------------------------------
    # 5️⃣ Time horizon mismatch
    # --------------------------------------------------
    if time_horizon == "Short-term" and regime in ["High Volatility", "Bear Market"]:
        quality -= 10
        notes.append("Short-term decision taken during volatile or bearish conditions.")

    if time_horizon == "Long-term" and rec == "AVOID" and score >= 65:
        quality -= 5
        notes.append("Long-term horizon may tolerate near-term volatility.")

    # --------------------------------------------------
    # 6️⃣ Behavioral penalty
    # --------------------------------------------------
    if behavioral_score is not None:
        if behavioral_score >= 60:
            quality -= 20
            notes.append("High behavioral risk significantly weakens decision quality.")
        elif behavioral_score >= 30:
            quality -= 10
            notes.append("Moderate behavioral biases detected.")

    # --------------------------------------------------
    # FINAL NORMALIZATION
    # --------------------------------------------------
    quality = max(0, min(100, quality))

    if not notes:
        notes.append("Decision is logically consistent across risk, fundamentals, and market context.")

    return {
        "decision_quality_score": quality,
        "decision_quality_band": quality_band(quality),
        "notes": notes
    }
