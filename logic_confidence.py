def confidence_band(score, red_flags, profile_warnings):
    if score>=75 and red_flags==0:
        return "High Confidence"
    if score>=60:
        return "Medium Confidence"
    return "Low Confidence"

def risk_triggers(fund, q_score=None):
    triggers=[]
    if fund.get("DebtEquity",0)>2:
        triggers.append("Reduce leverage")
    if q_score is not None and q_score<0:
        triggers.append("Quarterly improvement needed")
    return triggers
