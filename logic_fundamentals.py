import yfinance as yf

# ======================================================
# SAFETY HELPERS
# ======================================================

def safe_num(val, default=None):
    try:
        if val is None:
            return default
        if isinstance(val, (int, float)):
            return val
        return float(val)
    except:
        return default


# ======================================================
# FUNDAMENTALS FETCH
# ======================================================

def fetch_fundamentals(symbol):
    """
    Fetches fundamentals from Yahoo Finance
    Returns ONLY numeric-safe values (float or None)
    """

    try:
        ticker = yf.Ticker(symbol + ".NS")
        info = ticker.info
    except:
        info = {}

    fund = {
        "PE": safe_num(info.get("trailingPE")),
        "PB": safe_num(info.get("priceToBook")),
        "EV_EBITDA": safe_num(info.get("enterpriseToEbitda")),
        "ROE": safe_num(info.get("returnOnEquity")),
        "ROCE": safe_num(info.get("returnOnCapitalEmployed")),
        "NetMargin": safe_num(info.get("profitMargins")),
        "DebtEquity": safe_num(info.get("debtToEquity")),
        "InterestCover": safe_num(info.get("interestCoverage")),
        "RevenueGrowth": safe_num(info.get("revenueGrowth")),
        "EPSGrowth": safe_num(info.get("earningsGrowth")),
    }

    return apply_fundamental_fallbacks(fund)


# ======================================================
# FALLBACK ESTIMATIONS
# ======================================================

def apply_fundamental_fallbacks(fund):
    """
    Conservative rule-based fallbacks
    Prevents None propagation into scoring & UI
    """

    # ROCE ↔ ROE inference
    if fund["ROCE"] is None and fund["ROE"] is not None:
        fund["ROCE"] = round(fund["ROE"] * 0.8, 3)

    if fund["ROE"] is None and fund["ROCE"] is not None:
        fund["ROE"] = round(fund["ROCE"] * 0.9, 3)

    # Net margin proxy
    if fund["NetMargin"] is None and fund["ROE"] is not None:
        fund["NetMargin"] = round(fund["ROE"] * 0.35, 3)

    # Interest coverage proxy
    if fund["InterestCover"] is None:
        if fund["DebtEquity"] is not None:
            fund["InterestCover"] = max(1.0, 5 - fund["DebtEquity"] * 2)
        else:
            fund["InterestCover"] = 2.0

    # Growth defaults (conservative)
    if fund["RevenueGrowth"] is None:
        fund["RevenueGrowth"] = 0.05

    if fund["EPSGrowth"] is None:
        fund["EPSGrowth"] = fund["RevenueGrowth"]

    return fund


# ======================================================
# METRIC QUALITY LABELING
# ======================================================

def evaluate_metric(metric, value):
    if value is None:
        return "⚪ Not Available"

    thresholds = {
        "ROE": (0.15, 0.10),
        "ROCE": (0.15, 0.10),
        "DebtEquity": (1.0, 2.0),
        "InterestCover": (3.0, 1.5),
        "PE": (25, 40),
        "RevenueGrowth": (0.10, 0.05),
        "EPSGrowth": (0.10, 0.05),
    }

    if metric not in thresholds:
        return "⚪ Neutral"

    good, weak = thresholds[metric]

    if metric in ["DebtEquity", "PE"]:
        if value <= good:
            return "🟢 Healthy"
        elif value <= weak:
            return "🟡 Watch"
        else:
            return "🔴 Risky"

    else:
        if value >= good:
            return "🟢 Healthy"
        elif value >= weak:
            return "🟡 Watch"
        else:
            return "🔴 Weak"


# ======================================================
# RED FLAG DETECTION (NUMERIC SAFE)
# ======================================================

def detect_red_flags(fund):
    flags = []

    if fund["InterestCover"] is not None and fund["InterestCover"] < 1.5:
        flags.append("Low interest coverage")

    if fund["DebtEquity"] is not None and fund["DebtEquity"] > 2:
        flags.append("High leverage")

    if fund["ROE"] is not None and fund["ROE"] < 0.10:
        flags.append("Weak ROE")

    if fund["NetMargin"] is not None and fund["NetMargin"] < 0.05:
        flags.append("Thin margins")

    if fund["RevenueGrowth"] is not None and fund["RevenueGrowth"] < 0:
        flags.append("Negative revenue growth")

    if fund["EPSGrowth"] is not None and fund["EPSGrowth"] < 0:
        flags.append("Negative earnings growth")

    return flags
