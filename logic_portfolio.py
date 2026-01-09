def analyze_portfolio(portfolio, risk_profile):
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
