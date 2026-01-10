# ======================================================
# NEWS SENTIMENT ANALYSIS (RULE-BASED, SAFE)
# ======================================================

def analyze_news(entries):
    """
    Analyzes recent news headlines and classifies sentiment.
    Input:
        entries → list of RSS feed entries (Google News)
    Output:
        {
            positive: int,
            neutral: int,
            negative: int,
            overall: "Positive" | "Neutral" | "Negative"
        }
    """

    summary = {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "overall": "Neutral"
    }

    if not entries:
        return summary

    positive_keywords = [
        "growth", "profit", "beat", "record", "expansion",
        "strong", "upgrade", "order win", "recovery", "margin improvement"
    ]

    negative_keywords = [
        "loss", "decline", "fall", "warning", "downgrade",
        "risk", "fraud", "probe", "litigation", "default",
        "margin pressure", "slowdown"
    ]

    for e in entries:
        try:
            title = (e.title or "").lower()
        except Exception:
            title = ""

        if any(word in title for word in positive_keywords):
            summary["positive"] += 1
        elif any(word in title for word in negative_keywords):
            summary["negative"] += 1
        else:
            summary["neutral"] += 1

    # --------------------------------------------------
    # OVERALL BIAS LOGIC
    # --------------------------------------------------
    if summary["negative"] > summary["positive"]:
        summary["overall"] = "Negative"
    elif summary["positive"] > summary["negative"]:
        summary["overall"] = "Positive"
    else:
        summary["overall"] = "Neutral"

    return summary
