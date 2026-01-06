def confidence_band(score, red_flag_count, mismatch_count):
    if score >= 75 and red_flag_count == 0:
        return "🟢 High Confidence"
    if score >= 60 and red_flag_count <= 1:
        return "🟡 Medium Confidence"
    return "🔴 Low Confidence"

def change_triggers(fund):
    triggers = []

    if fund.get("DebtEquity") and fund["DebtEquity"] > 2:
        triggers.append("Reduction in debt levels")

    if fund.get("EPSGrowth") and fund["EPSGrowth"] < 0.05:
        triggers.append("Sustained earnings growth")

    if fund.get("PE") and fund["PE"] > 35:
        triggers.append("Valuation correction")

    if not triggers:
        triggers.append("Material change in fundamentals or industry outlook")

    return triggers
