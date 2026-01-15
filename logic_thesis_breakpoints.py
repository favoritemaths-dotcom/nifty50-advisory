# ============================================================
# THESIS BREAKPOINT ENGINE
# ============================================================

def thesis_breakpoints(
    fund,
    score,
    market,
    risk_profile
):
    """
    Defines conditions that invalidate the investment thesis.
    Returns a list of breakpoint statements.
    """

    breakpoints = []

    # -------------------------------
    # Fundamental deterioration
    # -------------------------------
    if fund.get("ROE") is not None and fund["ROE"] < 0.12:
        breakpoints.append("ROE falls below 12%")

    if fund.get("DebtEquity") is not None and fund["DebtEquity"] > 2:
        breakpoints.append("Debt-to-Equity rises above 2")

    if fund.get("InterestCover") is not None and fund["InterestCover"] < 2:
        breakpoints.append("Interest coverage drops below 2×")

    if fund.get("RevenueGrowth") is not None and fund["RevenueGrowth"] < 0.05:
        breakpoints.append("Revenue growth slows below 5%")

    if fund.get("EPSGrowth") is not None and fund["EPSGrowth"] < 0:
        breakpoints.append("Earnings growth turns negative")

    # -------------------------------
    # Score deterioration
    # -------------------------------
    if score < 50:
        breakpoints.append("Overall stock score falls below 50")

    # -------------------------------
    # Market regime risk
    # -------------------------------
    regime = market.get("regime", "Neutral")

    if regime in ["Bear Market", "Risk-Off"]:
        breakpoints.append("Market regime turns risk-off or bearish")

    # -------------------------------
    # Risk profile specific
    # -------------------------------
    if risk_profile == "Conservative":
        if fund.get("PE") is not None and fund["PE"] > 30:
            breakpoints.append("Valuation exceeds conservative comfort zone")

    if not breakpoints:
        breakpoints.append("No immediate thesis invalidation signals detected")

    return breakpoints
