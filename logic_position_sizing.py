def calculate_position_size(
    total_capital: float,
    recommendation: str,
    confidence: str,
    risk_profile: str,
    conviction_status: str
):
    """
    Determines position size based on rule confidence + AI conviction.
    Returns allocation percentage and amount.
    """

    # ----------------------------
    # BASE ALLOCATION BY RISK
    # ----------------------------
    base_alloc = {
        "Conservative": 0.05,
        "Moderate": 0.10,
        "Aggressive": 0.15
    }.get(risk_profile, 0.05)

    # ----------------------------
    # RECOMMENDATION FILTER
    # ----------------------------
    if recommendation == "AVOID":
        return {
            "allocation_pct": 0,
            "amount": 0,
            "note": "No capital allocated due to AVOID recommendation."
        }

    # ----------------------------
    # CONFIDENCE ADJUSTMENT
    # ----------------------------
    confidence_multiplier = {
        "High": 1.0,
        "Medium": 0.75,
        "Low": 0.5
    }.get(confidence, 0.5)

    # ----------------------------
    # AI CONVICTION ADJUSTMENT
    # ----------------------------
    if conviction_status.startswith("⚠️"):
        conviction_multiplier = 0.25
    elif conviction_status.startswith("🟡"):
        conviction_multiplier = 0.6
    else:  # 🟢
        conviction_multiplier = 1.0

    # ----------------------------
    # FINAL CALCULATION
    # ----------------------------
    final_pct = base_alloc * confidence_multiplier * conviction_multiplier
    final_amount = round(total_capital * final_pct, 2)

    return {
        "allocation_pct": round(final_pct * 100, 2),
        "amount": final_amount,
        "note": "Position size adjusted based on risk, confidence, and AI conviction."
    }
