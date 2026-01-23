def exit_rules_engine(
    recommendation: str,
    risk_profile: str,
    investment_horizon: str,
    conviction_status: str
):
    """
    Determines exit discipline based on risk profile & conviction.
    """

    # Default values
    stop_loss_pct = None
    review_period = None
    exit_reason = []

    # -----------------------------
    # STOP LOSS RULES
    # -----------------------------
    if risk_profile == "Conservative":
        stop_loss_pct = -8
    elif risk_profile == "Moderate":
        stop_loss_pct = -12
    else:  # Aggressive
        stop_loss_pct = -18

    # -----------------------------
    # TIME-BASED REVIEW
    # -----------------------------
    if investment_horizon == "Short-term":
        review_period = "30 days"
    elif investment_horizon == "Medium-term":
        review_period = "90 days"
    else:
        review_period = "180 days"

    # -----------------------------
    # CONVICTION OVERRIDE
    # -----------------------------
    if conviction_status.startswith("⚠️"):
        stop_loss_pct = min(stop_loss_pct, -6)
        exit_reason.append("Lower conviction — tighter stop-loss applied")

    if recommendation in ["AVOID", "REDUCE"]:
        exit_reason.append("Rule-based recommendation is weak")

    return {
        "stop_loss_pct": stop_loss_pct,
        "review_period": review_period,
        "exit_reasons": exit_reason
    }
