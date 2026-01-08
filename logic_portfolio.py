def analyze_portfolio(portfolio, risk_profile):
    """
    portfolio: list of dicts
        [
          {
            "stock": "INFY",
            "sector": "IT",
            "allocation_pct": 18
          }
        ]
    risk_profile: Conservative / Moderate / Aggressive
    """

    insights = []
    warnings = []

    # -----------------------------
    # 1. Allocation sanity check
    # -----------------------------
    total_alloc = sum(p["allocation_pct"] for p in portfolio)

    if total_alloc < 90:
        warnings.append(f"High cash holding detected ({100-total_alloc:.1f}%)")
    elif total_alloc > 105:
        warnings.append("Portfolio allocation exceeds 100%")

    # -----------------------------
    # 2. Sector concentration
    # -----------------------------
    sector_map = {}
    for p in portfolio:
        sector_map[p["sector"]] = sector_map.get(p["sector"], 0) + p["allocation_pct"]

    max_sector = max(sector_map.items(), key=lambda x: x[1])

    if max_sector[1] > 40:
        warnings.append(
            f"High concentration in {max_sector[0]} sector ({max_sector[1]:.1f}%)"
        )

    # -----------------------------
    # 3. Diversification check
    # -----------------------------
    if len(portfolio) < 4:
        warnings.append("Portfolio may be under-diversified")
    elif len(portfolio) > 12:
        warnings.append("Portfolio may be over-diversified")

    # -----------------------------
    # 4. Risk profile alignment
    # -----------------------------
    if risk_profile == "Conservative" and max_sector[1] > 30:
        warnings.append("Sector exposure too high for Conservative profile")

    if risk_profile == "Aggressive" and max_sector[1] < 20:
        insights.append("Aggressive profile with well-spread exposure")

    # -----------------------------
    # 5. Portfolio risk score (simple)
    # -----------------------------
    risk_score = 100
    risk_score -= len(warnings) * 8
    risk_score = max(40, risk_score)

    return {
        "risk_score": risk_score,
        "sector_exposure": sector_map,
        "warnings": warnings,
        "insights": insights
    }
