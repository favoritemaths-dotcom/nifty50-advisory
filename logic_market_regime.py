def detect_market_regime(index_trend="Neutral", volatility="Normal"):
    if index_trend=="Down" or volatility=="High":
        return {"regime":"Bear","risk_multiplier":0.7,"note":"Bear market risk"}
    if index_trend=="Up":
        return {"regime":"Bull","risk_multiplier":1.2,"note":"Bull market tailwind"}
    return {"regime":"Neutral","risk_multiplier":1.0,"note":"Neutral market"}
