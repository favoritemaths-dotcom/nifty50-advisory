def analyze_quarterly_text(text):
    if not text:
        return 0,[]

    score=0
    signals=[]

    if "growth" in text:
        score+=5; signals.append("Growth mentioned")
    if "margin" in text:
        score+=3; signals.append("Margins discussed")
    if "risk" in text or "uncertain" in text:
        score-=5; signals.append("Risks highlighted")

    return score,signals
