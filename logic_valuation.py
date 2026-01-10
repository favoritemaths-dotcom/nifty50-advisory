import yfinance as yf

# ======================================================
# FAIR VALUE & VALUATION ENGINE
# ======================================================

def estimate_fair_value(symbol, fund, get_cmp):
    """
    Estimates fair value using a conservative PE-based approach.

    Inputs:
    - symbol: stock symbol (NIFTY format, without .NS)
    - fund: fundamentals dict from logic_fundamentals
    - get_cmp: callable to fetch current market price

    Returns:
    - fair_value (₹) or None
    - upside_pct (%) or None
    - valuation_zone (Attractive / Reasonable / Expensive) or None
    """

    # -----------------------------
    # EPS FETCH (SAFE)
    # -----------------------------
    try:
        info = yf.Ticker(symbol + ".NS").info
        eps = info.get("trailingEps")
    except Exception:
        eps = None

    pe = fund.get("PE")

    if eps is None or pe is None or eps <= 0:
        return None, None, None

    # -----------------------------
    # FAIR PE ASSUMPTION (CAPPED)
    # -----------------------------
    if pe <= 15:
        fair_pe = 18
    elif pe <= 25:
        fair_pe = 22
    else:
        fair_pe = 25   # optimism cap

    fair_value = round(eps * fair_pe, 2)

    # -----------------------------
    # CMP FETCH
    # -----------------------------
    cmp_price = get_cmp(symbol)
    if cmp_price is None or cmp_price <= 0:
        return fair_value, None, None

    # -----------------------------
    # UPSIDE / DOWNSIDE
    # -----------------------------
    upside_pct = round((fair_value - cmp_price) / cmp_price * 100, 1)

    # -----------------------------
    # VALUATION ZONE
    # -----------------------------
    if cmp_price <= 0.85 * fair_value:
        zone = "Attractive"
    elif cmp_price <= fair_value:
        zone = "Reasonable"
    else:
        zone = "Expensive"

    return fair_value, upside_pct, zone
