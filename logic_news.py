from datetime import datetime, timezone

def news_weight(published):
    """
    Returns weight based on recency
    """
    try:
        published_dt = datetime(*published[:6], tzinfo=timezone.utc)
        days_old = (datetime.now(timezone.utc) - published_dt).days

        if days_old <= 1:
            return 1.0        # Today / yesterday
        elif days_old <= 7:
            return 0.7        # This week
        elif days_old <= 30:
            return 0.4        # This month
        else:
            return 0.2        # Old news
    except:
        return 0.5            # Safe fallback
        
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
    weight = news_weight(getattr(n, "published_parsed", None))

    if any(k in title for k in positive_keywords):
        positive += weight
    elif any(k in title for k in negative_keywords):
        negative += weight
    else:
        neutral += weight

positive = round(positive)
negative = round(negative)
neutral = round(neutral)

if positive > negative:
    impact_label = "Positive"
elif negative > positive:
    impact_label = "Negative"
else:
    impact_label = "Neutral"

return {
    "positive": positive,
    "negative": negative,
    "neutral": neutral,
    "impact_label": impact_label
}
