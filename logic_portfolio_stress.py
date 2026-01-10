# ======================================================
# PORTFOLIO STRESS TEST ENGINE
# ======================================================

def portfolio_stress_test(portfolio, market):
    """
    Estimates portfolio drawdowns under stressed market conditions.

    Inputs:
        portfolio: list of dicts
            {
                "stock": str,
                "sector": str,
                "allocation_pct": float
            }
        market: dict from detect_market_regime()

    Returns:
        {
            "Correction Drawdown %": float,
            "Bear Market Drawdown %": float,
            "Stress Rating": str
        }
    """

    # -------------------------------
    # Defensive validation
    # -------------------------------
    if not portfolio:
        return {
            "Correction Drawdown %": 0,
            "Bear Market Drawdown %": 0,
            "Stress Rating": "UNKNOWN"
        }

    # -------------------------------
    # Stress assumptions
    # -------------------------------
    CORRECTION_IMPACT = 0.10   # 10% index correction
    BEAR_IMPACT = 0.25         # 25% bear market

    # Sector sensitivity (heuristic betas)
    sector_beta = {
        "IT": 1.10,
        "Finance": 1.00,
        "Energy": 0.90,
        "FMCG": 0.60,
        "Pharma": 0.70,
        "Metals": 1.20,
        "Auto": 1.10,
        "Infrastructure": 1.15,
        "Default": 1.00
    }

    correction_loss = 0.0
    bear_loss = 0.0

    # -------------------------------
    # Portfolio weighted stress calc
    # -------------------------------
    for p in portfolio:
        weight = p.get("allocation_pct", 0) / 100
        sector = p.get("sector", "Default")

        beta = sector_beta.get(sector, sector_beta["Default"])

        correction_loss += weight * beta * CORRECTION_IMPACT
        bear_loss += weight * beta * BEAR_IMPACT

    correction_pct = round(correction_loss * 100, 1)
    bear_pct = round(bear_loss * 100, 1)

    # -------------------------------
    # Stress severity classification
    # -------------------------------
    if bear_pct < 15:
        stress = "LOW"
    elif bear_pct < 25:
        stress = "MEDIUM"
    else:
        stress = "HIGH"

    # Market regime overlay
    if market and market.get("regime") in ["Bear Market", "Risk-Off"]:
        if stress == "LOW":
            stress = "MEDIUM"
        elif stress == "MEDIUM":
            stress = "HIGH"

    return {
        "Correction Drawdown %": correction_pct,
        "Bear Market Drawdown %": bear_pct,
        "Stress Rating": stress
    }
