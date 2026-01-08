import yfinance as yf

def detect_market_regime():
    """
    Detects overall market regime using NIFTY 50 trend & volatility
    """

    try:
        nifty = yf.Ticker("^NSEI").history(period="6mo")
        vix = yf.Ticker("^INDIAVIX").history(period="6mo")
    except Exception:
        return {
            "regime": "Unknown",
            "label": "Data unavailable",
            "risk_bias": "Neutral"
        }

    # -----------------------------
    # Trend detection
    # -----------------------------
    ma_50 = nifty["Close"].rolling(50).mean().iloc[-1]
    ma_200 = nifty["Close"].rolling(200).mean().iloc[-1]
    last_close = nifty["Close"].iloc[-1]

    # -----------------------------
    # Volatility
    # -----------------------------
    latest_vix = vix["Close"].iloc[-1]

    # -----------------------------
    # Regime logic
    # -----------------------------
    if last_close > ma_50 > ma_200 and latest_vix < 15:
        return {
            "regime": "Bull",
            "label": "🟢 Bull Market (Risk-On)",
            "risk_bias": "Positive"
        }

    if last_close < ma_50 < ma_200 and latest_vix > 20:
        return {
            "regime": "Bear",
            "label": "🔴 Bear Market (Risk-Off)",
            "risk_bias": "Negative"
        }

    if latest_vix > 22:
        return {
            "regime": "Volatile",
            "label": "🟠 High Volatility / Event Risk",
            "risk_bias": "Negative"
        }

    return {
        "regime": "Sideways",
        "label": "🟡 Range-bound / Uncertain Market",
        "risk_bias": "Neutral"
    }
