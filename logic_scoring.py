from logic_fundamentals import detect_red_flags

def detect_profile_mismatch(fund, risk):
    warnings=[]
    if risk=="Conservative" and fund.get("DebtEquity",0)>1:
        warnings.append("High leverage for conservative profile")
    return warnings

def score_stock(fund, news, annual_text, quarterly_text, risk):
    score=50; reasons=[]

    if fund.get("PE",99)<25: score+=5; reasons.append("Reasonable valuation")
    if fund.get("ROE",0)>0.15: score+=7; reasons.append("Strong ROE")
    if fund.get("DebtEquity",9)<1: score+=5; reasons.append("Low leverage")
    if fund.get("RevenueGrowth",0)>0.1: score+=5; reasons.append("Revenue growth")

    if news.get("overall")=="Positive": score+=5
    if news.get("overall")=="Negative": score-=5

    flags=detect_red_flags(fund)
    score-=5*len(flags)
    reasons+=flags

    if risk=="Aggressive": score+=3

    score=max(0,min(score,100))
    rec="BUY" if score>=70 else "HOLD" if score>=50 else "AVOID"
    return score,rec,reasons
