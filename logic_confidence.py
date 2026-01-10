# ======================================================
# CONFIDENCE, CONVICTION & RISK TRIGGERS
# ======================================================

# ------------------------------------------------------
# CONFIDENCE BAND (STOCK-LEVEL)
# ------------------------------------------------------

def confidence_band(score, red_flags_count, profile_warnings_count):
    """
    Determines confidence band for a single-stock recommendation
    """

    if score >= 75 and red_flags_count == 0 and profile_warnings_count == 0:
        return "High Confidence"

    if score >= 60 and red_flags_count <= 1:
        return "Medium Confidence"

    return "Low Confidence"


# ------------------------------------------------------
# CONVICTION LABEL (ENHANCED RECOMMENDATION TEXT)
# ------------------------------------------------------

def conviction_label(rec, confidence, score):
    """
    Enhances base recommendation with conviction context
    """

    rec = rec.upper()

    if rec == "BUY":
        if "High" in confidence and score >= 75:
            return "BUY (High Conviction)"
        elif "Medium" in confidence:
            return "BUY (Moderate Conviction)"
        else:
            return "BUY (Speculative)"

    if rec == "HOLD":
        if "High" in confidence:
            return "HOLD (Strong Fundamentals)"
        elif "Medium" in confidence:
            return "HOLD (Watch Closely)"
        else:
            return "HOLD (Weak Momentum)"

    return "AVOID (Unfavorable Risk)"


# ------------------------------------------------------
# STOCK-LEVEL RISK TRIGGERS (THESIS INVALIDATION)
# ------------------------------------------------------

def risk_triggers(fund, score, market=None):
    """
    Identifies conditions that could invalidate the investment thesis
    """

    triggers = []

    # -----------------------------
    # Growth risks
    # -----------------------------
    if fund.get("RevenueGrowth") is not None and fund["RevenueGrowth"] < 0.08:
        triggers.append("Revenue growth falls below 8%")

    if fund.get("EPSGrowth") is not None and fund["EPSGrowth"] < 0.10:
        triggers.append("Earnings growth weakens below 10%")

    # -----------------------------
    # Leverage & balance sheet
    # -----------------------------
    if fund.get("DebtEquity") is not None and fund["DebtEquity"] > 1.5:
        triggers.append("Debt-to-equity rises above comfortable levels")

    if fund.get("InterestCover") is not None and fund["InterestCover"] < 2:
        triggers.append("Interest coverage weakens below 2×")

    # -----------------------------
    # Profitability pressure
    # -----------------------------
    if fund.get("ROCE") is not None and fund["ROCE"] < 0.12:
        triggers.append("Return on capital falls below 12%")

    if fund.get("NetMargin") is not None and fund["NetMargin"] < 0.08:
        triggers.append("Net profit margin compresses below 8%")

    # -----------------------------
    # Valuation risk
    # -----------------------------
    if fund.get("PE") is not None and fund["PE"] > 40:
        triggers.append("Valuation expands beyond reasonable PE levels")

    # -----------------------------
    # Score deterioration
    # -----------------------------
    if score is not None and score < 50:
        triggers.append("Overall stock score deteriorates below 50")

    # -----------------------------
    # Market regime overlay (optional)
    # -----------------------------
    if market:
        regime = market.get("regime", "")
        if regime in ["Bear Market", "Risk-Off"]:
            triggers.append("Market regime turns risk-off or bearish")

    return triggers
