def analyze_quarterly_text(text):
    if not text:
        return 0, []
    score = 0
    signals = []
    lower = text.lower()
    if "growth" in lower:
        score += 5
        signals.append("Growth keywords detected")
    if "margin" in lower:
        score += 3
        signals.append("Margin keywords detected")
    if "risk" in lower:
        score -= 3
        signals.append("Risk keywords detected")
    return score, signals
