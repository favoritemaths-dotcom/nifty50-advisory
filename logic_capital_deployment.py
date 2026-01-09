def capital_deployment_plan(
    recommendation,
    confidence,
    time_horizon,
    investment_amount
):
    """
    Suggests how to deploy capital over time based on conviction.
    """

    plan = []

    if recommendation == "BUY":
        if "High" in confidence:
            plan = [
                ("Now", 60),
                ("After 3 months", 20),
                ("After 6 months", 20),
            ]
        else:
            plan = [
                ("Now", 40),
                ("After 3 months", 30),
                ("After 6 months", 30),
            ]

    elif recommendation == "HOLD":
        plan = [
            ("Now", 20),
            ("After 3 months", 40),
            ("After 6 months", 40),
        ]

    else:  # REDUCE
        plan = [
            ("Hold Cash", 80),
            ("Opportunistic Buy", 20),
        ]

    deployment = []
    for phase, pct in plan:
        amount = round(investment_amount * pct / 100)
        deployment.append({
            "Phase": phase,
            "Allocation %": pct,
            "Amount (₹)": amount
        })

    return deployment
