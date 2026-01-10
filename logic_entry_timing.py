def entry_timing_engine(
    cmp_price,
    fair_value,
    recommendation,
    market,
    confidence,
    risk_profile
):
    """
    Determines entry timing based on valuation gap, market regime,
    confidence, and risk profile.
    """

    if cmp_price is None or fair_value is None or fair_value <= 0:
        return {
            "mos": None,
            "action": "INSUFFICIENT DATA",
            "reason": "Price or fair value unavailable"
        }

    mos = round((fair_value - cmp_price) / fair_value * 100, 2)

    regime = market.get("regime", "Neutral")
    volatility = market.get("volatility", "Normal")

    # Base decision
    if mos >= 25:
        action = "BUY AGGRESSIVELY"
    elif mos >= 10:
        action = "BUY / ACCUMULATE"
    elif mos >= 0:
        action = "ACCUMULATE IN PHASES"
    else:
        action = "WAIT / AVOID"

    # Market regime adjustment
    if volatility == "High" and action.startswith("BUY"):
        action = "ACCUMULATE IN PHASES"

    if regime in ["Risk-Off", "Bearish"] and action.startswith("BUY"):
        action = "WAIT / ACCUMULATE SLOWLY"

    # Risk profile adjustment
    if risk_profile == "Conservative" and mos < 15:
        action = "WAIT FOR BETTER MARGIN"

    # Confidence adjustment
    if "Low" in confidence and action.startswith("BUY"):
        action = "ACCUMULATE SLOWLY"

    reason = (
        f"Margin of Safety: {mos}% | "
        f"Market: {regime} | "
        f"Volatility: {volatility}"
    )

    return {
        "mos": mos,
        "action": action,
        "reason": reason
    }
