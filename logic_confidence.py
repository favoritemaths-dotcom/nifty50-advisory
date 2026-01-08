def confidence_band(score, red_flags_count, profile_warnings_count):
    if score >= 75 and red_flags_count == 0:
        return "🟢 High Confidence"
    if score >= 60 and red_flags_count <= 1:
        return "🟡 Medium Confidence"
    return "🔴 Low Confidence"


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

def thesis_invalidation(score, q_score, fund, news_summary):
    reasons = []

    if score < 45:
        reasons.append("Overall score dropped below 45")

    if q_score is not None and q_score < -8:
        reasons.append("Severe quarterly deterioration")

    if fund.get("ROE") is not None and fund["ROE"] < 0.10:
        reasons.append("ROE below acceptable threshold")

    if fund.get("DebtEquity") is not None and fund["DebtEquity"] > 2:
        reasons.append("Leverage risk increased materially")

    if news_summary.get("impact_label") == "Negative" and score < 60:
        reasons.append("Negative news flow with weakening fundamentals")

    return reasons
