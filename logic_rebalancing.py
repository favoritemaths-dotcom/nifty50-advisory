def portfolio_rebalancing_signal(portfolio_result, market, confidence):
    """
    Determines whether portfolio needs rebalancing.
    """

    signals = []

    risk_score = portfolio_result.get("risk_score", 0)
    warnings = portfolio_result.get("warnings", [])

    if risk_score < 45:
        signals.append("High portfolio risk detected")

    if len(warnings) >= 2:
        signals.append("Multiple portfolio warnings present")

    if market.get("regime") in ["Risk-Off", "Bearish"]:
        signals.append("Market regime turning defensive")

    if "Low" in confidence:
        signals.append("Low confidence band")

    if signals:
        return "REBALANCE NOW", signals

    if market.get("regime") == "Neutral":
        return "MONITOR", ["No urgent risks, but monitor periodically"]

    return "NO ACTION", ["Portfolio aligned with current conditions"]
