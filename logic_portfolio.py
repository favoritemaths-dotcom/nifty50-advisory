# logic_portfolio.py

def analyze_portfolio(portfolio, risk_profile):
    """
    Portfolio-level intelligence
    Works for single-stock or multi-stock portfolios
    """

    risk_score = 0
    warnings = []
    insights = []

    total_alloc = sum(p.get("allocation_pct", 0) for p in portfolio)

    # -------------------------
    # Allocation sanity check
    # -------------------------
    if total_alloc > 100:
        warnings.append(
            "Total allocation exceeds 100%. Consider reducing exposure."
        )

    # -------------------------
    # Sector concentration
    # -------------------------
    sector_map = {}
    for p in portfolio:
        sector = p.get("sector", "Unknown")
        sector_map.setdefault(sector, 0)
        sector_map[sector] += p.get("allocation_pct", 0)

    for sector, alloc in sector_map.items():
        if alloc > 50:
            warnings.append(
                f"High concentration in {sector} sector ({alloc}%)."
            )
            risk_score += 2

    # -------------------------
    # Risk profile alignment
    # -------------------------
    if risk_profile == "Conservative" and total_alloc > 60:
        warnings.append(
            "High overall equity exposure for a conservative profile."
        )
        risk_score += 2

    if risk_profile == "Aggressive" and total_alloc < 40:
        insights.append(
            "Portfolio exposure appears conservative for an aggressive profile."
        )

    # -------------------------
    # Normalize risk score
    # -------------------------
    risk_score = min(risk_score, 10)

    if risk_score <= 2:
        insights.append("Portfolio risk is well balanced.")
    elif risk_score <= 5:
        insights.append("Portfolio risk is moderate.")
    else:
        insights.append("Portfolio risk is elevated.")

    return {
        "risk_score": risk_score,
        "warnings": warnings,
        "insights": insights
    }
