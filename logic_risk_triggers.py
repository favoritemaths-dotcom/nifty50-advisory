# ======================================================
# THESIS INVALIDATION & RISK TRIGGERS ENGINE
# ======================================================

def risk_triggers(
    fund,
    score,
    market
):
    """
    Identifies conditions that could invalidate the investment thesis.

    Inputs:
        fund: dict from fetch_fundamentals()
        score: stock score (0–100)
        market: dict from detect_market_regime()

    Returns:
        triggers: list[str]
    """

    triggers = []

    # --------------------------------------------------
    # Growth deterioration
    # --------------------------------------------------
    if fund.get("RevenueGrowth") is not None and fund["RevenueGrowth"] < 0.08:
        triggers.append("Revenue growth weakens below 8%.")

    if fund.get("EPSGrowth") is not None and fund["EPSGrowth"] < 0.10:
        triggers.append("Earnings growth falls below 10%.")

    # --------------------------------------------------
    # Balance sheet stress
    # --------------------------------------------------
    if fund.get("DebtEquity") is not None and fund["DebtEquity"] > 1.5:
        triggers.append("Debt-to-equity rises beyond comfortable levels.")

    if fund.get("InterestCover") is not None and fund["InterestCover"] < 2:
        triggers.append("Interest coverage weakens below 2×.")

    # --------------------------------------------------
    # Profitability erosion
    # --------------------------------------------------
    if fund.get("ROCE") is not None and fund["ROCE"] < 0.12:
        triggers.append("Return on capital drops below 12%.")

    if fund.get("NetMargin") is not None and fund["NetMargin"] < 0.08:
        triggers.append("Net profit margin compresses below 8%.")

    # --------------------------------------------------
    # Valuation risk
    # --------------------------------------------------
    if fund.get("PE") is not None and fund["PE"] > 40:
        triggers.append("Valuation expands beyond reasonable PE levels.")

    # --------------------------------------------------
    # Score deterioration
    # --------------------------------------------------
    if score is not None and score < 50:
        triggers.append("Overall stock score deteriorates below 50.")

    # --------------------------------------------------
    # Market regime overlay
    # --------------------------------------------------
    regime = market.get("regime") if market else None

    if regime in ["Bear Market", "Risk-Off"]:
        triggers.append("Market regime turns risk-off or bearish.")

    # --------------------------------------------------
    # Default case
    # --------------------------------------------------
    if not triggers:
        triggers.append("No major downside risk triggers identified.")

    return triggers
