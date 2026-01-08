import yfinance as yf

def estimate_fair_value(symbol, fund, cmp_func):
    try:
        eps = yf.Ticker(symbol + ".NS").info.get("trailingEps")
    except:
        return None,None,None

    pe = fund.get("PE")
    if not eps or not pe:
        return None,None,None

    fair_pe = 18 if pe <= 15 else 22 if pe <= 25 else 25
    fair_value = round(eps * fair_pe)

    cmp = cmp_func(symbol)
    if not cmp:
        return fair_value,None,None

    upside = round((fair_value - cmp)/cmp*100,1)
    zone = "Attractive" if cmp <= 0.85*fair_value else "Reasonable" if cmp <= fair_value else "Expensive"
    return fair_value, upside, zone
