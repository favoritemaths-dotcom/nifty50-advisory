# logic_investment_plan.py

def generate_investment_plan(
    recommendation,
    confidence,
    score,
    risk_profile,
    time_horizon,
    market,
    is_portfolio=False
):
    """
    Generates a structured, actionable investment plan.
    Pure rule-based engine (NO AI, NO API).
    Safe for production use.
    """

    plan = []

    regime = market.get("regime", "Neutral")
    volatility = market.get("volatility", "Normal")

    # -------------------------------------------------
    # STRATEGY TYPE
    # -------------------------------------------------
    if recommendation == "BUY":
        if score >= 75 and "High" in confidence:
            strategy = "High-conviction accumulation"
        elif score >= 60:
            strategy = "Gradual accumulation"
        else:
            strategy = "Opportunistic buying only on dips"
    elif recommendation == "HOLD":
        strategy = "Hold and monitor closely"
    else:
        strategy = "Capital preservation / avoid exposure"

    plan.append(f"**Strategy:** {strategy}")

    # -------------------------------------------------
    # CAPITAL DEPLOYMENT
    # -------------------------------------------------
    if recommendation == "BUY":
        if risk_profile == "Conservative":
            deploy = "Deploy 20–30% now, rest only on corrections"
        elif risk_profile == "Moderate":
            deploy = "Deploy 30–40% now, stagger remaining capital"
        else:
            deploy = "Deploy 40–50% now with tactical adds"
    elif recommendation == "HOLD":
        deploy = "Avoid fresh allocation; deploy only after confirmation"
    else:
        deploy = "Do not deploy fresh capital"

    plan.append(f"**Capital Deployment:** {deploy}")

    # -------------------------------------------------
    # MARKET REGIME ADJUSTMENT
    # -------------------------------------------------
    if regime in ["Bear Market", "Risk-Off"]:
        plan.append(
            "**Market Overlay:** Defensive regime — prioritize capital protection"
        )
    elif regime in ["Bull Market", "Risk-On"]:
        plan.append(
            "**Market Overlay:** Risk-on regime — momentum supports exposure"
        )
    else:
        plan.append(
            "**Market Overlay:** Neutral regime — selective positioning advised"
        )

    # -------------------------------------------------
    # RISK MANAGEMENT RULES
    # -------------------------------------------------
    risk_rules = []

    if score < 50:
        risk_rules.append("Reduce exposure if score drops below 50")

    if "Low" in confidence:
        risk_rules.append("Limit position size due to low conviction")

    if regime in ["Bear Market", "Risk-Off"]:
        risk_rules.append("Avoid averaging down aggressively")

    if not risk_rules:
        risk_rules.append("Maintain existing risk controls")

    plan.append("**Risk Controls:**")
    for r in risk_rules:
        plan.append(f"- {r}")

    # -------------------------------------------------
    # REVIEW & MONITORING
    # -------------------------------------------------
    if time_horizon == "Short-term":
        review = "Review weekly or after major news/events"
    elif time_horizon == "Medium-term":
        review = "Review monthly or after earnings"
    else:
        review = "Review quarterly with fundamentals update"

    plan.append(f"**Review Frequency:** {review}")

    # -------------------------------------------------
    # EXIT / REDUCTION CONDITIONS
    # -------------------------------------------------
    exit_rules = []

    exit_rules.append("Exit or reduce if fundamentals deteriorate materially")

    if regime in ["Bear Market", "Risk-Off"]:
        exit_rules.append("Tighten exit discipline in adverse market regimes")

    if recommendation == "BUY" and score < 60:
        exit_rules.append("Reassess thesis if score remains below 60")

    plan.append("**Exit / Reduce Conditions:**")
    for e in exit_rules:
        plan.append(f"- {e}")

    # -------------------------------------------------
    # MODE TAG
    # -------------------------------------------------
    if is_portfolio:
        plan.append("_Plan generated at portfolio level_")
    else:
        plan.append("_Plan generated for individual stock_")

    return plan
