def detect_market_regime(index_trend="Neutral", volatility="Normal"):
    if index_trend == "Down" or volatility == "High":
        return {
            "regime": "Bear Market",
            "risk_multiplier": 0.8,
            "note": "Market risk-off conditions"
        }
    if index_trend == "Up":
        return {
            "regime": "Bull Market",
            "risk_multiplier": 1.2,
            "note": "Market risk-on conditions"
        }
    return {
        "regime": "Neutral Market",
        "risk_multiplier": 1.0,
        "note": "Range-bound or balanced market"
    }
