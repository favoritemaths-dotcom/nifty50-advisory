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

def score_stock(fund, news, annual_text, profile):
    score = 50
    reasons = []

    if fund.get("ROE") and fund["ROE"] > 0.15:
        score += 7
        reasons.append("Strong ROE")

    if fund.get("DebtEquity") and fund["DebtEquity"] < 1:
        score += 5
        reasons.append("Low leverage")

    if news:
        score += 5
        reasons.append("Recent news flow")

    red_flags = detect_red_flags(fund)
    if red_flags:
        score -= 5 * len(red_flags)
        reasons += [f"⚠️ {f}" for f in red_flags]

    mismatches = detect_profile_mismatch(fund, profile)
    if mismatches:
        score -= 5
        reasons += [f"⚠️ {m}" for m in mismatches]

    score = max(0, min(score, 100))
    rec = "BUY" if score >= 70 else "HOLD" if score >= 50 else "AVOID"

    return score, rec, reasons
