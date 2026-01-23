def market_kill_switch(
    market_regime: str,
    recommendation: str,
    risk_profile: str
):
    """
    Prevents aggressive actions during hostile market regimes.
    """

    # Normalize market regime safely
if isinstance(market_regime, str):
    regime = market_regime.lower()
elif isinstance(market_regime, dict):
    regime = str(market_regime.get("trend", "unknown")).lower()
else:
    regime = "unknown"
    if regime in ["crash", "risk-off", "extreme_volatility"]:
        if recommendation == "BUY":
            return {
                "allowed": False,
                "action": "BLOCKED",
                "reason": "Market regime is hostile. Capital preservation takes priority."
            }

    if regime in ["uncertain", "high_volatility"] and risk_profile == "Conservative":
        if recommendation == "BUY":
            return {
                "allowed": False,
                "action": "DOWNGRADED",
                "reason": "High uncertainty market not suitable for conservative risk profile."
            }

    return {
        "allowed": True,
        "action": recommendation,
        "reason": "Market regime permits action."
    }
