# ======================================================
# PORTFOLIO CORE ANALYSIS
# ======================================================

def analyze_portfolio(portfolio, risk_profile):
    """
    Core portfolio risk analysis
    Input:
        portfolio: list of {stock, sector, allocation_pct}
        risk_profile: Conservative | Moderate | Aggressive
    Output:
        {
            risk_score: int (0–100, lower is better),
            warnings: list[str],
            insights: list[str]
        }
    """

    risk_score = 0
    warnings = []
    insights = []

    if not portfolio:
        return {
            "risk_score": 100,
            "warnings": ["Empty portfolio"],
            "insights": ["No stocks selected"]
        }

    total_alloc = sum(p.get("allocation_pct", 0) for p in portfolio)

    # -------------------------------
    # Allocation sanity check
    # -------------------------------
    if total_alloc > 100:
        warnings.append("Total allocation exceeds 100%")
        risk_score += 10

    if total_alloc < 50:
        warnings.append("Very low capital deployment")
        risk_score += 5

    # -------------------------------
    # Sector concentration analysis
    # -------------------------------
    sector_map = {}
    for p in portfolio:
        sector = p.get("sector", "Unknown")
        sector_map[sector] = sector_map.get(sector, 0) + p.get("allocation_pct", 0)

    for sector, alloc in sector_map.items():
        if alloc > 50:
            warnings.append(f"High concentration in {sector} sector ({alloc}%)")
            risk_score += 15
        elif alloc > 35:
            warnings.append(f"Moderate concentration in {sector} sector ({alloc}%)")
            risk_score += 8

    # -------------------------------
    # Risk profile alignment
    # -------------------------------
    if risk_profile == "Conservative" and total_alloc > 65:
        warnings.append("Equity exposure high for conservative profile")
        risk_score += 15

    if risk_profile == "Aggressive" and total_alloc < 50:
        insights.append("Aggressive profile with low equity exposure")

    # -------------------------------
    # Normalize risk score
    # -------------------------------
    risk_score = max(0, min(100, risk_score))

    # -------------------------------
    # Portfolio insights
    # -------------------------------
    if risk_score <= 25:
        insights.append("Portfolio risk is well controlled")
    elif risk_score <= 50:
        insights.append("Portfolio risk is moderate and manageable")
    else:
        insights.append("Portfolio risk is elevated and needs attention")

    return {
        "risk_score": risk_score,
        "warnings": warnings,
        "insights": insights
    }


# ======================================================
# PORTFOLIO CONSTRUCTION
# ======================================================

def build_portfolio(df_all, selected_stocks):
    """
    Builds a normalized equal-weight portfolio
    """

    portfolio = []

    if not selected_stocks:
        return portfolio

    alloc = round(100 / len(selected_stocks), 2)

    for s in selected_stocks:
        row = df_all[df_all["Symbol"] == s].iloc[0]
        portfolio.append({
            "stock": s,
            "sector": row.get("Sector", "Unknown"),
            "allocation_pct": alloc
        })

    return portfolio


# ======================================================
# PORTFOLIO FINAL RECOMMENDATION
# ======================================================

def portfolio_final_recommendation(portfolio_score):
    """
    Converts portfolio risk score into action
    """

    if portfolio_score <= 30:
        return "BUY", "Strong portfolio structure with controlled risk"
    elif portfolio_score <= 55:
        return "HOLD", "Balanced portfolio but monitor risks"
    else:
        return "REDUCE", "Portfolio risk elevated"


# ======================================================
# PORTFOLIO CONFIDENCE BAND
# ======================================================

def portfolio_confidence_band(portfolio_score, warning_count):
    """
    Confidence assessment based on score + warnings
    """

    if portfolio_score <= 30 and warning_count == 0:
        return "High Confidence"
    elif portfolio_score <= 55 and warning_count <= 2:
        return "Medium Confidence"
    else:
        return "Low Confidence"


# ======================================================
# MARKET REGIME ADJUSTMENT
# ======================================================

def adjust_for_market_regime(portfolio_action, market):
    """
    Adjust portfolio action based on market regime
    """

    regime = market.get("regime", "Neutral")

    if regime in ["Bear Market", "Risk-Off"]:
        if portfolio_action == "BUY":
            return "HOLD / SELECTIVE BUY"

    if regime in ["Bull Market", "Risk-On"]:
        if portfolio_action == "HOLD":
            return "BUY ON DIPS"

    return portfolio_action


# ======================================================
# PORTFOLIO RISK TRIGGERS
# ======================================================

def portfolio_risk_triggers(portfolio_result, market):
    """
    Portfolio-level downside risk triggers
    """

    triggers = []

    risk_score = portfolio_result.get("risk_score", 0)
    warnings = portfolio_result.get("warnings", [])

    if risk_score >= 60:
        triggers.append("Portfolio risk score is elevated")

    for w in warnings:
        triggers.append(w)

    regime = market.get("regime", "Neutral")

    if regime in ["Bear Market", "Risk-Off"]:
        triggers.append("Market regime has turned defensive")

    if not triggers:
        triggers.append("No major portfolio-level downside risks detected")

    return triggers
