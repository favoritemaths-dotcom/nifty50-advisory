import numpy as np

def simulate_portfolio_performance(portfolio, years=5):
    """
    Simulates portfolio CAGR & max drawdown using heuristic assumptions.
    """

    # Defensive defaults
    if not portfolio:
        return None

    # Heuristic assumptions
    base_return = 0.11        # 11% base CAGR
    volatility = 0.18        # 18% volatility

    # Adjust return based on diversification
    sectors = set(p.get("sector") for p in portfolio)
    diversification_bonus = min(len(sectors) * 0.005, 0.02)

    expected_cagr = base_return + diversification_bonus

    # Simulated drawdown logic
    max_drawdown = round(volatility * 1.5 * 100, 1)  # %

    risk_adjusted_score = round((expected_cagr * 100) / max_drawdown, 2)

    return {
        "cagr_pct": round(expected_cagr * 100, 2),
        "max_drawdown_pct": max_drawdown,
        "risk_adjusted_score": risk_adjusted_score
    }
