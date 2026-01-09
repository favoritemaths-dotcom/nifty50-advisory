def confidence_band(score, red_flags_count, profile_warnings_count):
    if score >= 75 and red_flags_count == 0:
        return "High Confidence"
    if score >= 60:
        return "Medium Confidence"
    return "Low Confidence"

def risk_triggers(fund, q_score):
    triggers = []
    if fund.get("DebtEquity") and fund["DebtEquity"] > 2:
        triggers.append("Reduce leverage levels")
    if q_score is not None and q_score < 0:
        triggers.append("Improve quarterly performance")
    return triggers
    
def conviction_label(rec, confidence, score):
    """
    Enhances base recommendation with conviction context
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
            return "HOLD (Weak Momentum)"

    return "AVOID (Unfavorable Risk)"
