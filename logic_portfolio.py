# logic_portfolio.py

def analyze_portfolio(portfolio, risk_profile):
    """
    Core portfolio risk analysis
    """
    risk_score = 0
    warnings = []
    insights = []

    total_alloc = sum(p.get("allocation_pct", 0) for p in portfolio)

    if total_alloc > 100:
        warnings.append("Total allocation exceeds 100%.")

    sector_map = {}
    for p in portfolio:
        sector = p.get("sector", "Unknown")
        sector_map.setdefault(sector, 0)
        sector_map[sector] += p.get("allocation_pct", 0)

    for sector, alloc in sector_map.items():
        if alloc > 50:
            warnings.append(f"High concentration in sector {sector} ({alloc}%).")
            risk_score += 2

    if risk_profile == "Conservative" and total_alloc > 60:
        warnings.append("High equity exposure for conservative profile.")
        risk_score += 2

    if risk_profile == "Aggressive" and total_alloc < 40:
        insights.append("Consider increasing exposure for aggressive profile.")

    if risk_score <= 2:
        insights.append("Portfolio risk is balanced.")
    elif risk_score <= 5:
        insights.append("Portfolio risk is moderate.")
    else:
        insights.append("Portfolio risk is elevated.")

    return {
        "risk_score": risk_score,
        "warnings": warnings,
        "insights": insights
    }


# =========================================================
# NEW — PORTFOLIO DECISION & STRUCTURE LAYER
# =========================================================

def build_portfolio(df_all, selected_stocks):
    """
    Build normalized portfolio structure
    """
    portfolio = []
    n = len(selected_stocks)

    for s in selected_stocks:
        row = df_all[df_all["Symbol"] == s].iloc[0]
        portfolio.append({
            "stock": s,
            "sector": row["Sector"],
            "allocation_pct": round(100 / n, 2)
        })

    return portfolio


def portfolio_final_recommendation(portfolio_score):
    """
    Decide portfolio-level action
    """
    if portfolio_score >= 70:
        return "BUY", "Strong portfolio quality"
    elif portfolio_score >= 50:
        return "HOLD", "Balanced but risks exist"
    else:
        return "REDUCE", "Elevated portfolio risk"


def portfolio_confidence_band(portfolio_score, warning_count):
    """
    Confidence assessment based on score + warnings
    """
    if portfolio_score >= 70 and warning_count == 0:
        return "High Confidence"
    elif portfolio_score >= 50 and warning_count <= 2:
        return "Medium Confidence"
    else:
        return "Low Confidence"


def adjust_for_market_regime(portfolio_action, market):
    """
    Market regime-aware adjustment
    """
    regime = market.get("regime", "Neutral")
    adjusted_action = portfolio_action

    if regime in ["Risk-Off", "Bearish", "High Volatility"]:
        if portfolio_action == "BUY":
            adjusted_action = "HOLD / ACCUMULATE SLOWLY"

    elif regime in ["Risk-On", "Bullish", "Low Volatility"]:
        if portfolio_action == "HOLD":
            adjusted_action = "BUY ON DIPS"

    return adjusted_action
