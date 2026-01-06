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
        return "Strong" if value >= 0.18 else "Average" if value >= 0.12 else "Weak"

    if name == "DebtEquity":
        return "Strong" if value <= 1 else "Average" if value <= 2 else "Weak"

    if name == "InterestCover":
        return "Strong" if value >= 3 else "Average" if value >= 1.5 else "Weak"

    if name == "PE":
        return "Reasonable" if value <= 25 else "Expensive" if value <= 40 else "Very Expensive"

    if name in ["RevenueGrowth", "EPSGrowth"]:
        return "Strong" if value >= 0.15 else "Moderate" if value >= 0.05 else "Weak"

    return "—"

def detect_red_flags(fund):
    flags = []

    if fund.get("DebtEquity") and fund["DebtEquity"] > 2.5:
        flags.append("Very high leverage")

    if fund.get("InterestCover") and fund["InterestCover"] < 1.5:
        flags.append("Weak interest coverage")

    if fund.get("EPSGrowth") and fund["EPSGrowth"] < 0:
        flags.append("Negative earnings growth")

    return flags
