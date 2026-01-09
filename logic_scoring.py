# ======================================================
# CORE STOCK SCORING ENGINE
# ======================================================

def detect_profile_mismatch(fund, risk_profile):
    """
    Detect mismatch between stock risk and investor profile
    Returns list of warnings (NOT penalties)
    """

    warnings = []

    debt = fund.get("DebtEquity")
    pe = fund.get("PE")
    interest = fund.get("InterestCover")

    if risk_profile == "Conservative":
        if debt is not None and debt > 1:
            warnings.append("High leverage unsuitable for conservative profile")
        if interest is not None and interest < 2:
            warnings.append("Low interest coverage for conservative investor")
        if pe is not None and pe > 30:
            warnings.append("High valuation limits margin of safety")

    if risk_profile == "Moderate":
        if pe is not None and pe > 40:
            warnings.append("High valuation reduces risk–reward balance")

    if risk_profile == "Aggressive":
        if pe is not None and pe > 45:
            warnings.append("Extreme valuation even for aggressive profile")

    return warnings


# ======================================================
# MAIN SCORING FUNCTION
# ======================================================

def score_stock(
    fund,
    news_summary,
    annual_text,
    quarterly_text,
    risk_profile
):
    """
    Produces:
    - score (0–100)
    - recommendation (BUY / HOLD / AVOID)
    - reasons (list of strings)
    """

    score = 50
    reasons = []

    # --------------------------------------------------
    # FUNDAMENTAL QUALITY
    # --------------------------------------------------

    if fund.get("ROE") is not None:
        if fund["ROE"] >= 0.18:
            score += 8
            reasons.append("Strong return on equity")
        elif fund["ROE"] < 0.10:
            score -= 6
            reasons.append("Weak return on equity")

    if fund.get("DebtEquity") is not None:
        if fund["DebtEquity"] <= 1:
            score += 6
            reasons.append("Low leverage")
        elif fund["DebtEquity"] > 2:
            score -= 8
            reasons.append("High leverage risk")

    if fund.get("InterestCover") is not None:
        if fund["InterestCover"] >= 3:
            score += 4
            reasons.append("Comfortable interest coverage")
        elif fund["InterestCover"] < 1.5:
            score -= 7
            reasons.append("Debt servicing risk")

    # --------------------------------------------------
    # GROWTH QUALITY
    # --------------------------------------------------

    if fund.get("RevenueGrowth") is not None:
        if fund["RevenueGrowth"] >= 0.10:
            score += 5
            reasons.append("Healthy revenue growth")
        elif fund["RevenueGrowth"] < 0:
            score -= 6
            reasons.append("Revenue contraction")

    if fund.get("EPSGrowth") is not None:
        if fund["EPSGrowth"] >= 0.10:
            score += 5
            reasons.append("Strong earnings growth")
        elif fund["EPSGrowth"] < 0:
            score -= 6
            reasons.append("Earnings decline")

    # --------------------------------------------------
    # VALUATION DISCIPLINE
    # --------------------------------------------------

    if fund.get("PE") is not None:
        if fund["PE"] <= 25:
            score += 4
            reasons.append("Reasonable valuation")
        elif fund["PE"] > 40:
            score -= 7
            reasons.append("Expensive valuation")

    # --------------------------------------------------
    # NEWS INTELLIGENCE (SOFT SIGNAL)
    # --------------------------------------------------

    if news_summary:
        bias = news_summary.get("overall")

        if bias == "Positive":
            score += 3
            reasons.append("Positive news sentiment")
        elif bias == "Negative":
            score -= 4
            reasons.append("Negative news sentiment")

    # --------------------------------------------------
    # ANNUAL REPORT SIGNAL
    # --------------------------------------------------

    if annual_text:
        if "material risk" in annual_text or "litigation" in annual_text:
            score -= 4
            reasons.append("Risk disclosures noted in annual report")

    # --------------------------------------------------
    # RISK PROFILE ALIGNMENT (SOFT PENALTY)
    # --------------------------------------------------

    mismatches = detect_profile_mismatch(fund, risk_profile)

    if mismatches:
        score -= min(6, 2 * len(mismatches))
        for m in mismatches:
            reasons.append(f"⚠️ {m}")

    # --------------------------------------------------
    # FINAL NORMALIZATION
    # --------------------------------------------------

    score = max(0, min(100, round(score)))

    if score >= 70:
        rec = "BUY"
    elif score >= 50:
        rec = "HOLD"
    else:
        rec = "AVOID"

    return score, rec, reasons
