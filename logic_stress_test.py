def stress_test_portfolio(portfolio_result, scenario):
    """
    Simulates macro stress scenarios on portfolio risk.
    Returns adjusted risk score, action bias, and warnings.
    """

    base_score = portfolio_result["risk_score"]
    warnings = []

    score_impact = 0
    action_bias = "NEUTRAL"

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
        warnings.append("Input cost pressure on margins.")
        action_bias = "SELECTIVE BUY"

    elif scenario == "Global Risk-Off":
        score_impact = -20
        warnings.append("Valuation multiples compress globally.")
        action_bias = "REDUCE"

    elif scenario == "Bull Run":
        score_impact = +10
        warnings.append("Momentum-driven upside possible.")
        action_bias = "BUY"

    stressed_score = max(0, min(100, base_score + score_impact))

    return {
        "scenario": scenario,
        "stressed_score": stressed_score,
        "action_bias": action_bias,
        "warnings": warnings
    }
