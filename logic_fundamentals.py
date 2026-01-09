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
    if name == "ROE":
        return "Strong" if value > 0.15 else "Average" if value > 0.08 else "Weak"
    if name == "DebtEquity":
        return "Low" if value < 1 else "Moderate" if value < 2 else "High"
    if name == "InterestCover":
        return "Good" if value > 2 else "Poor"
    if name == "PE":
        return "Reasonable" if value < 25 else "High"
    if name in ["RevenueGrowth", "EPSGrowth"]:
        return "Good" if value > 0.10 else "Moderate" if value > 0.05 else "Weak"
    return "—"

def detect_red_flags(fund):
    flags = []
    if fund.get("DebtEquity", 0) > 2.5:
        flags.append("Very high leverage")
    if fund.get("InterestCover", 0) < 1.5:
        flags.append("Low interest coverage")
    if fund.get("EPSGrowth", 0) < 0:
        flags.append("Negative earnings growth")
    return flags
