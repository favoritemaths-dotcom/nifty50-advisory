# ======================================================
# PORTFOLIO STRESS TEST ENGINE
# ======================================================

def stress_test_portfolio(portfolio_result, scenario):
    """
    Simulates macro stress scenarios on portfolio risk.

    Inputs:
    - portfolio_result: output of analyze_portfolio()
    - scenario: selected stress scenario string

    Returns:
    - stressed_score (0–100)
    - action_bias (BUY / HOLD / REDUCE / SELECTIVE BUY)
    - warnings (list of strings)
    """

    base_score = portfolio_result.get("risk_score", 0)
    warnings = []

    score_impact = 0
    action_bias = "NEUTRAL"

    # -------------------------------
    # SCENARIO IMPACTS
    # -------------------------------
    if scenario == "Market Crash (-20%)":
        score_impact = -25
        warnings.append("Sharp market drawdown impacts all equities.")
        action_bias = "REDUCE"

    elif scenario == "Interest Rate Hike":
        score_impact = -15
        warnings.append("Rate-sensitive sectors may underperform.")
        action_bias = "HOLD"

    elif scenario == "Commodity Spike":
        score_impact = -10
        warnings.append("Input cost pressure may compress margins.")
        action_bias = "SELECTIVE BUY"

    elif scenario == "Global Risk-Off":
        score_impact = -20
        warnings.append("Global risk-off may compress valuation multiples.")
        action_bias = "REDUCE"

    elif scenario == "Bull Run":
        score_impact = +10
        warnings.append("Momentum-driven upside possible across equities.")
        action_bias = "BUY"

    else:
        warnings.append("Unknown scenario – stress impact assumed neutral.")
        action_bias = "HOLD"

    # -------------------------------
    # FINAL STRESSED SCORE
    # -------------------------------
    stressed_score = max(0, min(100, base_score + score_impact))

    return {
        "scenario": scenario,
        "stressed_score": stressed_score,
        "action_bias": action_bias,
        "warnings": warnings
    }
