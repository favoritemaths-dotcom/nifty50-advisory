import yfinance as yf

def fetch_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        info = ticker.info
        fin = ticker.financials
        bs = ticker.balance_sheet

        fundamentals = {}

        # ======================
        # Primary Yahoo metrics
        # ======================
        fundamentals["PE"] = info.get("trailingPE")
        fundamentals["PB"] = info.get("priceToBook")
        fundamentals["EV_EBITDA"] = info.get("enterpriseToEbitda")
        fundamentals["ROE"] = info.get("returnOnEquity")
        fundamentals["ROCE"] = info.get("returnOnAssets")
        fundamentals["NetMargin"] = info.get("profitMargins")
        fundamentals["DebtEquity"] = info.get("debtToEquity")
        fundamentals["InterestCover"] = info.get("interestCoverage")
        fundamentals["RevenueGrowth"] = info.get("revenueGrowth")
        fundamentals["EPSGrowth"] = info.get("earningsGrowth")

        # ======================
        # FALLBACK CALCULATIONS
        # ======================

        # ROE fallback
        if fundamentals["ROE"] is None:
            try:
                net_income = fin.loc["Net Income"].iloc[0]
                equity = bs.loc["Total Stockholder Equity"].iloc[0]
                fundamentals["ROE"] = net_income / equity if equity else None
            except:
                pass

        # Debt/Equity fallback
        if fundamentals["DebtEquity"] is None:
            try:
                debt = bs.loc["Total Debt"].iloc[0]
                equity = bs.loc["Total Stockholder Equity"].iloc[0]
                fundamentals["DebtEquity"] = debt / equity if equity else None
            except:
                pass

        # Net Margin fallback
        if fundamentals["NetMargin"] is None:
            try:
                net_income = fin.loc["Net Income"].iloc[0]
                revenue = fin.loc["Total Revenue"].iloc[0]
                fundamentals["NetMargin"] = net_income / revenue if revenue else None
            except:
                pass

        return fundamentals

    except Exception:
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
