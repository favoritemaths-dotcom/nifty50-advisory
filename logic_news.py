def analyze_news(entries):
    summary = {"positive": 0, "neutral": 0, "negative": 0}
    for e in entries:
        title = e.title.lower()
        if any(x in title for x in ["growth","profit","beat"]):
            summary["positive"] += 1
        elif any(x in title for x in ["loss","decline","warn"]):
            summary["negative"] += 1
        else:
            summary["neutral"] += 1

    if summary["negative"] > summary["positive"]:
        overall = "Negative"
    elif summary["positive"] > summary["negative"]:
        overall = "Positive"
    else:
        overall = "Neutral"

    summary["overall"] = overall
    return summary
