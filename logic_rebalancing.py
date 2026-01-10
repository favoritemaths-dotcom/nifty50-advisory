# ======================================================
# PORTFOLIO REBALANCING ENGINE
# ======================================================

def portfolio_rebalancing_signal(
    portfolio_result,
    market,
    confidence
):
    """
    Determines whether portfolio needs rebalancing.

    Inputs:
        portfolio_result: dict from analyze_portfolio()
        market: dict from detect_market_regime()
        confidence: str (High / Medium / Low Confidence)

    Returns:
        action: str
        reasons: list[str]
    """

    action = "NO ACTION"
    reasons = []

    risk_score = portfolio_result.get("risk_score", 0)
    warnings = portfolio_result.get("warnings", [])
    regime = market.get("regime", "Neutral")

    # ----------------------------------
    # High portfolio risk
    # ----------------------------------
    if risk_score >= 6:
        action = "REBALANCE NOW"
        reasons.append("Portfolio risk score is elevated.")

    # ----------------------------------
    # Structural warning overload
    # ----------------------------------
    if len(warnings) >= 2:
        action = "REBALANCE NOW"
        reasons.append("Multiple portfolio-level warnings detected.")

    # ----------------------------------
    # Market regime deterioration
    # ----------------------------------
    if regime in ["Bear Market", "Risk-Off", "High Volatility"]:
        if action != "REBALANCE NOW":
            action = "MONITOR"
        reasons.append("Market regime has turned defensive.")

    # ----------------------------------
    # Confidence downgrade
    # ----------------------------------
    if "Low" in confidence:
        if action == "NO ACTION":
            action = "MONITOR"
        reasons.append("Low confidence band suggests caution.")

    # ----------------------------------
    # Default healthy case
    # ----------------------------------
    if not reasons:
        reasons.append("Portfolio remains aligned with risk and market conditions.")

    return action, reasons
