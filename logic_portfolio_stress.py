def portfolio_stress_test(portfolio, market):
    """
    Estimates portfolio drawdown under stress scenarios
    """
    # Assumptions
    correction_factor = 0.10
    bear_factor = 0.25

    beta_map = {
        "IT": 1.1,
        "Finance": 1.0,
        "Energy": 0.9,
        "FMCG": 0.6,
        "Pharma": 0.7,
        "Default": 1.0
    }

    correction_loss = 0
    bear_loss = 0

    for p in portfolio:
        sector = p.get("sector", "Default")
        weight = p.get("allocation_pct", 0) / 100
        beta = beta_map.get(sector, beta_map["Default"])

        correction_loss += weight * beta * correction_factor
        bear_loss += weight * beta * bear_factor

    correction_loss_pct = round(correction_loss * 100, 1)
    bear_loss_pct = round(bear_loss * 100, 1)

    if bear_loss_pct < 15:
        stress = "LOW"
    elif bear_loss_pct < 25:
        stress = "MEDIUM"
    else:
        stress = "HIGH"

    return {
        "Correction Drawdown %": correction_loss_pct,
        "Bear Market Drawdown %": bear_loss_pct,
        "Stress Rating": stress
    }
