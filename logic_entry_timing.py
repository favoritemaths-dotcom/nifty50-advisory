# ======================================================
# ENTRY TIMING & MARGIN OF SAFETY ENGINE
# ======================================================

def entry_timing_engine(
    cmp_price,
    fair_value,
    recommendation,
    market,
    confidence,
    risk_profile
):
    """
    Determines entry timing using:
    - Margin of Safety (MoS)
    - Market regime & volatility
    - Recommendation strength
    - Investor risk profile
    - Confidence band

    Returns:
    {
        mos: float | None,
        action: str,
        reason: str
    }
    """

    # --------------------------------------------------
    # DATA SAFETY CHECK
    # --------------------------------------------------
    if cmp_price is None or fair_value is None or fair_value <= 0:
        return {
            "mos": None,
            "action": "INSUFFICIENT DATA",
            "reason": "Current price or fair value is unavailable"
        }

    # --------------------------------------------------
    # MARGIN OF SAFETY
    # --------------------------------------------------
    mos = round((fair_value - cmp_price) / fair_value * 100, 2)

    regime = market.get("regime", "Neutral")
    volatility = market.get("volatility", "Normal")

    action = "WAIT"
    reason_parts = []

    # --------------------------------------------------
    # BASE ACTION FROM MOS
    # --------------------------------------------------
    if mos >= 30:
        action = "BUY AGGRESSIVELY"
        reason_parts.append("Very high margin of safety")
    elif mos >= 20:
        action = "BUY"
        reason_parts.append("High margin of safety")
    elif mos >= 10:
        action = "ACCUMULATE"
        reason_parts.append("Moderate margin of safety")
    elif mos >= 0:
        action = "ACCUMULATE SLOWLY"
        reason_parts.append("Limited margin of safety")
    else:
        action = "WAIT / AVOID"
        reason_parts.append("Stock trading above fair value")

    # --------------------------------------------------
    # MARKET REGIME ADJUSTMENT
    # --------------------------------------------------
    if regime in ["Bear Market", "Risk-Off"]:
        if action.startswith("BUY"):
            action = "ACCUMULATE IN PHASES"
            reason_parts.append("Defensive market regime")
    elif regime in ["Bull Market", "Risk-On"]:
        reason_parts.append("Supportive market regime")

    if volatility == "High" and action.startswith("BUY"):
        action = "ACCUMULATE IN PHASES"
        reason_parts.append("High volatility environment")

    # --------------------------------------------------
    # RISK PROFILE ADJUSTMENT
    # --------------------------------------------------
    if risk_profile == "Conservative":
        if mos < 20 and action.startswith("BUY"):
            action = "WAIT FOR BETTER PRICE"
            reason_parts.append("Conservative profile requires higher safety margin")

    if risk_profile == "Aggressive" and mos >= 10:
        reason_parts.append("Aggressive profile allows earlier entry")

    # --------------------------------------------------
    # CONFIDENCE ADJUSTMENT
    # --------------------------------------------------
    if "Low" in confidence and action.startswith("BUY"):
        action = "ACCUMULATE SLOWLY"
        reason_parts.append("Low confidence suggests staggered entry")

    if "High" in confidence and mos >= 20:
        reason_parts.append("High conviction supports stronger entry")

    # --------------------------------------------------
    # FINAL SANITY CHECK WITH RECOMMENDATION
    # --------------------------------------------------
    if recommendation == "AVOID":
        action = "AVOID / WAIT"
        reason_parts.append("Base recommendation is AVOID")

    # --------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------
    reason = (
        f"MoS: {mos}% | "
        f"Market: {regime} | "
        f"Volatility: {volatility} | "
        + "; ".join(reason_parts)
    )

    return {
        "mos": mos,
        "action": action,
        "reason": reason
    }
