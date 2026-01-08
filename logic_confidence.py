def confidence_band(score, red_flags_count, profile_warnings_count):
    if score >= 75 and red_flags_count == 0:
        return "🟢 High Confidence"
    if score >= 60 and red_flags_count <= 1:
        return "🟡 Medium Confidence"
    return "🔴 Low Confidence"

def stabilize_confidence(prev_confidence, new_confidence, score_delta):
    """
    Prevents confidence from changing if score movement is small
    """
    if prev_confidence is None:
        return new_confidence

    # If score change is minor, freeze confidence
    if abs(score_delta) < 5:
        return prev_confidence

    return new_confidence
    
def risk_triggers(fund, q_score):
    """
    Conditions that could change the investment recommendation
    """
    triggers = []

    if fund.get("DebtEquity") and fund["DebtEquity"] > 2:
        triggers.append("Reduction in debt levels")

    if fund.get("EPSGrowth") and fund["EPSGrowth"] < 0.05:
        triggers.append("Sustained improvement in earnings growth")

    if fund.get("PE") and fund["PE"] > 35:
        triggers.append("Valuation correction or faster growth delivery")

    if q_score < 0:
        triggers.append("Stabilisation in quarterly performance")

    if not triggers:
        triggers.append("Material change in fundamentals or industry outlook")

    return triggers

def conviction_multiplier(confidence):
    if "High" in confidence:
        return 1.0
    if "Medium" in confidence:
        return 0.7
    return 0.4

def conviction_label(rec, confidence, score):
    """
    Enhances recommendation with conviction clarity
    """
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
            return "HOLD (Low Visibility)"

    return "SELL / AVOID"

def counter_case_analysis(fund, score, rec, news_summary, q_score):
    risks = []

    if fund.get("PE") and fund["PE"] > 30:
        risks.append("Valuation is elevated")

    if fund.get("DebtEquity") and fund["DebtEquity"] > 1.5:
        risks.append("High leverage increases financial risk")

    if q_score is not None and q_score < -5:
        risks.append("Recent quarterly performance deterioration")

    if news_summary.get("impact_label") == "Positive" and fund.get("ROE", 0) < 0.12:
        risks.append("Positive news may be masking weak profitability")

    if rec == "BUY" and score < 65:
        risks.append("Buy recommendation carries elevated downside risk")

    return risks

def thesis_invalidation(score, q_score, fund, news_summary):
    reasons = []

    if score < 45:
        reasons.append("Overall score has fallen below 45")

    if q_score is not None and q_score < -8:
        reasons.append("Severe quarterly performance deterioration")

    if fund.get("ROE") is not None and fund["ROE"] < 0.10:
        reasons.append("Return on Equity has dropped below acceptable levels")

    if fund.get("DebtEquity") is not None and fund["DebtEquity"] > 2:
        reasons.append("Leverage has increased beyond safe thresholds")

    if news_summary.get("impact_label") == "Negative":
        reasons.append("Sustained negative news flow impacting outlook")

    return reasons
