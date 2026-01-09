def risk_triggers(fund, score, market):
    """
    Identifies conditions that could invalidate the investment thesis.
    Returns a list of human-readable risk triggers.
    """

    triggers = []

    # Growth risks
    if fund.get("RevenueGrowth") is not None and fund.get("RevenueGrowth") < 0.08:
        triggers.append("Revenue growth falls below 8%")

    if fund.get("EPSGrowth") is not None and fund.get("EPSGrowth") < 0.10:
        triggers.append("Earnings growth weakens below 10%")

    # Leverage & balance sheet
    if fund.get("DebtEquity") is not None and fund.get("DebtEquity") > 1.5:
        triggers.append("Debt-to-equity rises above comfortable levels")

    if fund.get("InterestCover") is not None and fund.get("InterestCover") < 2:
        triggers.append("Interest coverage weakens below 2×")

    # Profitability pressure
    if fund.get("ROCE") is not None and fund.get("ROCE") < 12:
        triggers.append("Return on capital falls below 12%")

    if fund.get("NetMargin") is not None and fund.get("NetMargin") < 0.08:
        triggers.append("Net profit margin compresses below 8%")

    # Valuation risk
    if fund.get("PE") is not None and fund.get("PE") > 40:
        triggers.append("Valuation expands beyond reasonable PE levels")

    # Score deterioration
    if score < 50:
        triggers.append("Overall stock score deteriorates below 50")

    # Market regime risk
    if market and market.get("regime") in ["Risk-Off", "Bearish"]:
        triggers.append("Market regime turns risk-off or bearish")

    return triggers
