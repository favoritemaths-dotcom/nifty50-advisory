import yfinance as yf

def fetch_fundamentals(symbol):
    try:
        info = yf.Ticker(symbol + ".NS").info
        return {
            "PE": info.get("trailingPE"),
            "PB": info.get("priceToBook"),
            "EV_EBITDA": info.get("enterpriseToEbitda"),
            "ROE": info.get("returnOnEquity"),
            "ROCE": info.get("returnOnAssets"),
            "NetMargin": info.get("profitMargins"),
            "DebtEquity": info.get("debtToEquity"),
            "InterestCover": info.get("interestCoverage"),
            "CurrentRatio": info.get("currentRatio"),
            "RevenueGrowth": info.get("revenueGrowth"),
            "EPSGrowth": info.get("earningsGrowth"),
        }
    except:
        return {}

def evaluate_metric(name, value):
    if value is None:
        return "—"

    rules = {
        "ROE": [(0.18,"Strong"),(0.12,"Average"),(0,"Weak")],
        "DebtEquity": [(1,"Strong"),(2,"Average"),(10,"Weak")],
        "InterestCover": [(3,"Strong"),(1.5,"Average"),(0,"Weak")],
        "PE": [(25,"Reasonable"),(40,"Expensive"),(100,"Very Expensive")],
        "RevenueGrowth": [(0.15,"Strong"),(0.05,"Moderate"),(0,"Weak")],
        "EPSGrowth": [(0.15,"Strong"),(0.05,"Moderate"),(0,"Weak")]
    }

    for threshold,label in rules.get(name,[]):
        if value >= threshold:
            return label
    return "—"

def detect_red_flags(fund):
    flags = []
    if fund.get("DebtEquity",0) > 2.5:
        flags.append("Very high leverage")
    if fund.get("InterestCover",10) < 1.5:
        flags.append("Low interest coverage")
    if fund.get("EPSGrowth",1) < 0:
        flags.append("Negative earnings growth")
    return flags
