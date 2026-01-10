import pandas as pd

# ======================================================
# CAPITAL DEPLOYMENT ENGINE
# ======================================================

def capital_deployment_plan(
    recommendation,
    confidence,
    time_horizon,
    investment_amount
):
    """
    Builds a phased capital deployment plan based on:
    - recommendation (BUY / HOLD / REDUCE)
    - confidence level
    - time horizon
    - total investment amount

    Returns a pandas DataFrame suitable for Streamlit display
    """

    # -------------------------------
    # Defensive guards
    # -------------------------------
    if investment_amount is None or investment_amount <= 0:
        return pd.DataFrame(
            [{"Phase": "N/A", "Allocation %": 0, "Amount (₹)": 0, "Rationale": "Invalid investment amount"}]
        )

    recommendation = recommendation.upper()

    # -------------------------------
    # Base allocation logic
    # -------------------------------
    if recommendation.startswith("BUY"):
        base_alloc = 1.0
    elif recommendation.startswith("HOLD"):
        base_alloc = 0.5
    else:  # REDUCE / AVOID
        base_alloc = 0.2

    # -------------------------------
    # Confidence adjustment
    # -------------------------------
    if "High" in confidence:
        confidence_mult = 1.0
    elif "Medium" in confidence:
        confidence_mult = 0.75
    else:
        confidence_mult = 0.5

    deployable_capital = investment_amount * base_alloc * confidence_mult
    deployable_capital = round(deployable_capital, 0)

    # -------------------------------
    # Time horizon phasing
    # -------------------------------
    horizon = time_horizon.lower()

    if horizon.startswith("short"):
        phases = [
            ("Immediate Entry", 0.60, "Favorable setup for near-term execution"),
            ("Confirmation Add-on", 0.40, "Add on strength / breakout confirmation")
        ]

    elif horizon.startswith("medium"):
        phases = [
            ("Initial Entry", 0.40, "Initial valuation comfort"),
            ("Dip Accumulation", 0.35, "Add on market weakness"),
            ("Momentum Confirmation", 0.25, "Add once trend confirms")
        ]

    else:  # Long-term
        phases = [
            ("Starter Allocation", 0.30, "Initiate long-term position"),
            ("Value Accumulation", 0.40, "Add on valuation comfort"),
            ("Long-term Scaling", 0.30, "Scale as fundamentals play out")
        ]

    # -------------------------------
    # Build deployment table
    # -------------------------------
    rows = []
    remaining = deployable_capital

    for i, (phase, pct, rationale) in enumerate(phases):
        if i == len(phases) - 1:
            amount = remaining  # avoid rounding drift
        else:
            amount = round(deployable_capital * pct, 0)
            remaining -= amount

        rows.append({
            "Phase": phase,
            "Allocation %": round(pct * 100, 1),
            "Amount (₹)": int(amount),
            "Rationale": rationale
        })

    # -------------------------------
    # Edge case: nothing deployable
    # -------------------------------
    if deployable_capital <= 0:
        rows = [{
            "Phase": "No Deployment",
            "Allocation %": 0,
            "Amount (₹)": 0,
            "Rationale": "Low conviction or unfavorable recommendation"
        }]

    return pd.DataFrame(rows)
