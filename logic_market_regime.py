# ======================================================
# MARKET REGIME DETECTION ENGINE
# ======================================================

def detect_market_regime(
    index_trend="Neutral",
    volatility="Normal"
):
    """
    Determines current market regime and risk posture.

    Parameters
    ----------
    index_trend : str
        One of ["Up", "Down", "Neutral"]
    volatility : str
        One of ["Low", "Normal", "High"]

    Returns
    -------
    dict with keys:
        - regime: Human-readable regime label
        - risk_multiplier: Allocation adjustment factor
        - volatility: Echoed volatility level
        - note: Explanation of regime
    """

    # Normalize inputs
    index_trend = (index_trend or "Neutral").title()
    volatility = (volatility or "Normal").title()

    # --------------------------------------------------
    # HIGH RISK REGIMES
    # --------------------------------------------------
    if index_trend == "Down" and volatility == "High":
        return {
            "regime": "Bear Market",
            "risk_multiplier": 0.70,
            "volatility": volatility,
            "note": "Sharp downtrend with high volatility – capital preservation is priority"
        }

    if index_trend == "Down":
        return {
            "regime": "Risk-Off",
            "risk_multiplier": 0.80,
            "volatility": volatility,
            "note": "Market trending down – defensive positioning advised"
        }

    # --------------------------------------------------
    # LOW RISK / EXPANSION REGIMES
    # --------------------------------------------------
    if index_trend == "Up" and volatility == "Low":
        return {
            "regime": "Bull Market",
            "risk_multiplier": 1.25,
            "volatility": volatility,
            "note": "Strong uptrend with low volatility – favorable risk-taking environment"
        }

    if index_trend == "Up":
        return {
            "regime": "Risk-On",
            "risk_multiplier": 1.15,
            "volatility": volatility,
            "note": "Uptrend intact – selective risk-taking supported"
        }

    # --------------------------------------------------
    # SIDEWAYS / UNCERTAIN REGIMES
    # --------------------------------------------------
    if volatility == "High":
        return {
            "regime": "High Volatility",
            "risk_multiplier": 0.90,
            "volatility": volatility,
            "note": "Uncertain market with elevated volatility – staggered entry preferred"
        }

    # --------------------------------------------------
    # DEFAULT / NEUTRAL
    # --------------------------------------------------
    return {
        "regime": "Neutral Market",
        "risk_multiplier": 1.00,
        "volatility": volatility,
        "note": "Balanced market conditions – fundamentals drive decisions"
    }
