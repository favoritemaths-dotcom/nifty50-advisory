from logic_fundamentals import detect_red_flags

def detect_profile_mismatch(fund, profile):
    warnings = []

    if profile == "Conservative":
        if fund.get("DebtEquity") and fund["DebtEquity"] > 1:
            warnings.append("High leverage for conservative profile")

        if fund.get("PE") and fund["PE"] > 30:
            warnings.append("High valuation reduces margin of safety")

    if profile == "Aggressive":
        if fund.get("EPSGrowth") and fund["EPSGrowth"] < 0:
            warnings.append("Aggressive valuation without growth")

    return warnings

def score_stock(
    fund,
    news_analysis,
    annual_text,
    quarterly_text,
    risk
):
    score = 50
    reasons = []

    # -----------------------------
    # Fundamentals
    # -----------------------------
    if fund.get("ROE") and fund["ROE"] > 0.15:
        score += 7
        reasons.append("Strong ROE")

    if fund.get("DebtEquity") is not None:
        if fund["DebtEquity"] < 1:
            score += 5
            reasons.append("Low leverage")
        elif fund["DebtEquity"] > 2:
            score -= 7
            reasons.append("High leverage risk")

    if fund.get("RevenueGrowth") and fund["RevenueGrowth"] > 0.1:
        score += 5
        reasons.append("Revenue growth visible")

    # -----------------------------
    # 📰 NEWS IMPACT (A3)
    # -----------------------------
    if news_analysis:
        pos = news_analysis.get("positive", 0)
        neg = news_analysis.get("negative", 0)

        news_delta = min(8, pos * 2) - min(10, neg * 3)
        score += news_delta

        if news_delta > 0:
            reasons.append("Positive recent news sentiment")
        elif news_delta < 0:
            reasons.append("Negative recent news sentiment")

    # -----------------------------
    # Report-based risks
    # -----------------------------
    if "risk" in annual_text:
        score -= 5
        reasons.append("Risks highlighted in annual report")

    if risk == "Aggressive":
        score += 3

    # -----------------------------
    # Red flags & profile mismatch
    # -----------------------------
    red_flags = detect_red_flags(fund)
    if red_flags:
        score -= min(15, 5 * len(red_flags))
        reasons += [f"⚠️ {f}" for f in red_flags]

    mismatches = detect_profile_mismatch(fund, risk)
    if mismatches:
        score -= min(10, 3 * len(mismatches))
        reasons += [f"⚠️ {m}" for m in mismatches]

    # -----------------------------
    # Finalize
    # -----------------------------
    score = max(0, min(score, 100))

    if score >= 70:
        rec = "BUY"
    elif score >= 50:
        rec = "HOLD"
    else:
        rec = "AVOID"

    return score, rec, reasons
