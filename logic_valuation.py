import yfinance as yf

def estimate_fair_value(symbol, fund, get_cmp):
    try:
        info = yf.Ticker(symbol + ".NS").info
        eps = info.get("trailingEps")
    except:
        return None, None, None

    pe = fund.get("PE")
    if eps is None or pe is None:
        return None, None, None

    fair_pe = 18 if pe <= 15 else 22 if pe <= 25 else 25
    fair_value = round(eps * fair_pe)
    cmp = get_cmp(symbol)
    if cmp is None:
        return fair_value, None, None

    upside_pct = round((fair_value - cmp) / cmp * 100, 1)
    if cmp <= 0.85 * fair_value:
        zone = "Attractive"
    elif cmp <= fair_value:
        zone = "Reasonable"
    else:
        zone = "Expensive"
    return fair_value, upside_pct, zone
