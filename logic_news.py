def analyze_news(entries):
    summary = {"positive":0,"neutral":0,"negative":0}
    for e in entries:
        title = e.title.lower()
        if any(w in title for w in ["growth","profit","expansion","win"]):
            summary["positive"]+=1
        elif any(w in title for w in ["loss","decline","fraud","penalty"]):
            summary["negative"]+=1
        else:
            summary["neutral"]+=1

    if summary["negative"] > summary["positive"]:
        overall="Negative"
    elif summary["positive"] > summary["negative"]:
        overall="Positive"
    else:
        overall="Neutral"

    summary["overall"]=overall
    summary["impact_label"]=overall
    return summary
