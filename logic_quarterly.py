def analyze_quarterly_text(text):
    """
    Rule-based quarterly intelligence
    Returns: (impact_score, signals)
    impact_score range: -10 to +10
    """

    if not text:
        return 0, []

    signals = []
    score = 0

    POSITIVE = [
        "revenue growth",
        "margin improvement",
        "order book strong",
        "guidance raised",
        "cost optimization",
        "capacity expansion"
    ]

    NEGATIVE = [
        "margin pressure",
        "input cost inflation",
        "guidance cut",
        "weak demand",
        "one-time loss",
        "slowdown"
    ]

    for p in POSITIVE:
        if p in text:
            score += 2
            signals.append(f"📈 {p}")

    for n in NEGATIVE:
        if n in text:
            score -= 2
            signals.append(f"📉 {n}")

    score = max(-10, min(score, 10))
    return score, signals
