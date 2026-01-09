from logic_fundamentals import detect_red_flags

def detect_profile_mismatch(fund, risk_profile):
    warnings = []
    if risk_profile == "Conservative" and fund.get("DebtEquity", 0) > 1:
        warnings.append("High leverage for conservative profile")
    return warnings

def score_stock(fund, news_summary, annual_text, quarterly_text, risk_profile):
    score = 50
    reasons = []
    if fund.get("PE") and fund["PE"] < 25:
        score += 5
        reasons.append("Reasonable valuation")
    if fund.get("ROE") and fund["ROE"] > 0.15:
        score += 7
        reasons.append("Strong ROE")
    if fund.get("DebtEquity") and fund["DebtEquity"] < 1:
        score += 5
        reasons.append("Low leverage")
    elif fund.get("DebtEquity") and fund["DebtEquity"] > 2:
        score -= 5
        reasons.append("High leverage risk")

    if news_summary.get("overall") == "Positive":
        score += 5
    elif news_summary.get("overall") == "Negative":
        score -= 5

    red_flags = detect_red_flags(fund)
    for f in red_flags:
        reasons.append(f"⚠️ {f}")
        score -= 3

    profile_warnings = detect_profile_mismatch(fund, risk_profile)
    for w in profile_warnings:
        reasons.append(f"⚠️ {w}")

    score = max(0, min(score, 100))
    if score >= 70:
        rec = "BUY"
    elif score >= 50:
        rec = "HOLD"
    else:
        rec = "AVOID"
    return score, rec, reasons
