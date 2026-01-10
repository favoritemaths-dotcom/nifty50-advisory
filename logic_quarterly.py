# ======================================================
# QUARTERLY INTELLIGENCE ENGINE
# ======================================================

def analyze_quarterly_text(text):
    """
    Analyzes quarterly report text for directional signals.

    Inputs:
        text: str (lowercased or raw text from PDF)

    Returns:
        q_score: int (range roughly -10 to +10)
        signals: list[str] (human-readable insights)
    """

    # -------------------------------
    # Defensive checks
    # -------------------------------
    if not text or not isinstance(text, str):
        return 0, []

    score = 0
    signals = []

    t = text.lower()

    # -------------------------------
    # Positive signals
    # -------------------------------
    positive_keywords = [
        "growth",
        "margin expansion",
        "record revenue",
        "strong demand",
        "order book",
        "profitability improvement",
        "cost control",
        "capacity expansion"
    ]

    for kw in positive_keywords:
        if kw in t:
            score += 2
            signals.append(f"Positive quarterly signal: {kw}")

    # -------------------------------
    # Negative signals
    # -------------------------------
    negative_keywords = [
        "margin pressure",
        "slowdown",
        "weak demand",
        "loss",
        "cost inflation",
        "pricing pressure",
        "decline",
        "uncertainty"
    ]

    for kw in negative_keywords:
        if kw in t:
            score -= 2
            signals.append(f"Negative quarterly signal: {kw}")

    # -------------------------------
    # Risk disclosures (extra penalty)
    # -------------------------------
    risk_keywords = [
        "risk",
        "headwind",
        "litigation",
        "regulatory",
        "geopolitical",
        "currency volatility"
    ]

    for kw in risk_keywords:
        if kw in t:
            score -= 1
            signals.append(f"Risk disclosure noted: {kw}")

    # -------------------------------
    # Clamp score to safe range
    # -------------------------------
    score = max(-10, min(10, score))

    return score, signals
