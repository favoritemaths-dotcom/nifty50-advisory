# logic_goal_based_advisor.py

from logic_scoring import score_stock
from logic_market_regime import detect_market_regime

# ======================================================
# GOAL-BASED INVESTMENT ADVISOR
# ======================================================

def recommend_stocks_for_goal(
    df,
    investment_amount,
    risk_profile,
    duration_months,
    expected_return_pref
):
    """
    Returns a ranked list of stocks suitable for a specific investment goal
    """

    recommendations = []

    # -----------------------------
    # Build required data maps
    # -----------------------------
    from logic_fundamentals import fetch_fundamentals

    fundamentals_map = {}
    news_map = {}
    annual_text_map = {}
    quarterly_text_map = {}

    for _, row in df.iterrows():
        symbol = row["Symbol"]

        try:
            fundamentals_map[symbol] = fetch_fundamentals(symbol)
        except:
            fundamentals_map[symbol] = None

        # Safe defaults (can enhance later)
        news_map[symbol] = None
        annual_text_map[symbol] = ""
        quarterly_text_map[symbol] = ""
    # -------------------------------
    # Determine investment style
    # -------------------------------
    if duration_months <= 6:
        style = "Short"
    elif duration_months <= 18:
        style = "Medium"
    else:
        style = "Long"

    market = detect_market_regime()

    # -------------------------------
    # Capital-based stock count limit
    # -------------------------------
    if investment_amount < 100000:
        max_stocks = 3
    elif investment_amount < 300000:
        max_stocks = 5
    else:
        max_stocks = 7

    # -------------------------------
    # Analyze each stock
    # -------------------------------
    for _, row in df.iterrows():
        symbol = row["Symbol"]

        fund = fundamentals_map.get(symbol)
        news = news_map.get(symbol)
        annual_text = annual_text_map.get(symbol, "")
        quarterly_text = quarterly_text_map.get(symbol, "")

        if not fund:
            continue

        score, rec, reasons = score_stock(
            fund=fund,
            news_summary=news,
            annual_text=annual_text,
            quarterly_text=quarterly_text,
            risk_profile=risk_profile
        )

        # -------------------------------
        # Goal suitability adjustments
        # -------------------------------
        goal_score = score

        # Time horizon logic
        if style == "Short":
            if fund.get("PE") and fund["PE"] > 30:
                goal_score -= 10
            if news and news.get("overall") == "Negative":
                goal_score -= 8

        elif style == "Medium":
            if fund.get("ROE") and fund["ROE"] >= 0.15:
                goal_score += 6
            if fund.get("DebtEquity") and fund["DebtEquity"] > 1.5:
                goal_score -= 6

        elif style == "Long":
            if fund.get("ROE") and fund["ROE"] >= 0.18:
                goal_score += 8
            if fund.get("RevenueGrowth") and fund["RevenueGrowth"] >= 0.12:
                goal_score += 6

        # Risk profile adjustment
        if risk_profile == "Conservative":
            if fund.get("DebtEquity") and fund["DebtEquity"] > 1:
                goal_score -= 10
        elif risk_profile == "Aggressive":
            if fund.get("RevenueGrowth") and fund["RevenueGrowth"] >= 0.15:
                goal_score += 5

        goal_score = max(0, min(100, goal_score))

        if goal_score >= 65:
            recommendations.append({
                "stock": symbol,
                "company": row["Company"],
                "sector": row["Sector"],
                "goal_score": goal_score,
                "base_score": score,
                "recommendation": rec,
                "reasons": reasons[:3]  # keep concise
            })

    # -------------------------------
    # Rank & allocate
    # -------------------------------
    recommendations = sorted(
        recommendations,
        key=lambda x: x["goal_score"],
        reverse=True
    )[:max_stocks]

    if not recommendations:
        return []

    allocation_pct = round(100 / len(recommendations), 1)

    for r in recommendations:
        r["allocation_pct"] = allocation_pct
        r["allocation_amount"] = round(
            investment_amount * allocation_pct / 100
        )

    return recommendations
