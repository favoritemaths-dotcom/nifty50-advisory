# ======================================================
# PORTFOLIO PERFORMANCE SIMULATION
# ======================================================

import math


def simulate_portfolio_performance(portfolio, years=5):
    """
    Simulates long-term portfolio performance using heuristic assumptions.

    Inputs:
        portfolio: list of dicts with keys:
            - stock
            - sector
            - allocation_pct
        years: simulation horizon (default 5)

    Returns:
        {
            cagr_pct: float,
            max_drawdown_pct: float,
            risk_adjusted_score: float
        }
        OR None if portfolio is invalid
    """

    # -------------------------------
    # Validation
    # -------------------------------
    if not portfolio or years <= 0:
        return None

    total_alloc = sum(p.get("allocation_pct", 0) for p in portfolio)
    if total_alloc <= 0:
        return None

    # -------------------------------
    # Base assumptions (India equity long-term)
    # -------------------------------
    BASE_CAGR = 0.11        # 11% long-term equity CAGR
    BASE_VOLATILITY = 0.18 # 18% annualized volatility

    # -------------------------------
    # Diversification benefit
    # -------------------------------
    sectors = set(p.get("sector", "Unknown") for p in portfolio)
    diversification_bonus = min(len(sectors) * 0.005, 0.025)  # max +2.5%

    expected_cagr = BASE_CAGR + diversification_bonus

    # -------------------------------
    # Concentration penalty
    # -------------------------------
    max_weight = max(p.get("allocation_pct", 0) for p in portfolio) / 100

    if max_weight > 0.40:
        expected_cagr -= 0.02
    elif max_weight > 0.30:
        expected_cagr -= 0.01

    expected_cagr = max(0.04, expected_cagr)

    # -------------------------------
    # Drawdown estimation
    # -------------------------------
    drawdown_multiplier = 1.5
    max_drawdown = round(BASE_VOLATILITY * drawdown_multiplier * 100, 1)

    # -------------------------------
    # Risk-adjusted score (Sharpe-like)
    # -------------------------------
    if max_drawdown > 0:
        risk_adjusted_score = round((expected_cagr * 100) / max_drawdown, 2)
    else:
        risk_adjusted_score = 0

    return {
        "cagr_pct": round(expected_cagr * 100, 2),
        "max_drawdown_pct": max_drawdown,
        "risk_adjusted_score": risk_adjusted_score
    }
