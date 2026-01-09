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
    """
    Detects fundamental red flags safely.
    Handles None / missing values gracefully.
    """
    red_flags = []

    # --- ROE ---
    roe = fund.get("ROE")
    if roe is not None and roe < 0.10:
        red_flags.append("Low Return on Equity")

    # --- ROCE ---
    roce = fund.get("ROCE")
    if roce is not None and roce < 0.10:
        red_flags.append("Low Return on Capital Employed")

    # --- Debt to Equity ---
    de = fund.get("DebtEquity")
    if de is not None and de > 2:
        red_flags.append("High debt-to-equity ratio")

    # --- Interest Coverage ---
    interest_cover = fund.get("InterestCover")
    if interest_cover is not None and interest_cover < 1.5:
        red_flags.append("Weak interest coverage")

    # --- Net Profit Margin ---
    net_margin = fund.get("NetMargin")
    if net_margin is not None and net_margin < 0.05:
        red_flags.append("Low net profit margin")

    # --- Revenue Growth ---
    rev_growth = fund.get("RevenueGrowth")
    if rev_growth is not None and rev_growth < 0:
        red_flags.append("Declining revenue growth")

    # --- EPS Growth ---
    eps_growth = fund.get("EPSGrowth")
    if eps_growth is not None and eps_growth < 0:
        red_flags.append("Negative earnings growth")

    # --- Free Cash Flow ---
    fcf = fund.get("FreeCashFlow")
    if fcf is not None and fcf < 0:
        red_flags.append("Negative free cash flow")

    # --- Promoter Holding ---
    promoter_holding = fund.get("PromoterHolding")
    if promoter_holding is not None and promoter_holding < 0.40:
        red_flags.append("Low promoter holding")

    return red_flags
