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
