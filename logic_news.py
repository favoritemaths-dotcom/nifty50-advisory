def analyze_news(news_items):
    """
    Rule-based news sentiment analysis
    Returns counts + overall impact label
    """
   # Safety default: always return consistent structure
    if not news_items:
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "impact_label": "Neutral"
        } 
    positive_keywords = [
        "profit", "growth", "expansion", "order", "approval",
        "wins", "record", "strong", "upgrade", "acquisition"
    ]

    negative_keywords = [
        "loss", "decline", "fall", "drop", "weak", "downgrade",
        "probe", "penalty", "lawsuit", "resign", "debt"
    ]

    positive = 0
    negative = 0
    neutral = 0

    for n in news_items:
        title = n.title.lower()

        if any(k in title for k in positive_keywords):
            positive += 1
        elif any(k in title for k in negative_keywords):
            negative += 1
        else:
            neutral += 1

    if positive > negative:
    impact_label = "🟢 Positive"
elif negative > positive:
    impact_label = "🔴 Negative"
else:
    impact_label = "🟡 Neutral"

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "impact_label": impact
    }
