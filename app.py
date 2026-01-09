import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
import urllib.parse
from pypdf import PdfReader

# ==============================
# IMPORT LOGIC MODULES
# ==============================
from logic_fundamentals import (
    fetch_fundamentals,
    evaluate_metric,
    detect_red_flags,
    apply_fundamental_fallbacks
)
from logic_valuation import estimate_fair_value
from logic_news import analyze_news
from logic_quarterly import analyze_quarterly_text
from logic_scoring import score_stock, detect_profile_mismatch
from logic_explanation import generate_explanation
from logic_confidence import confidence_band, risk_triggers, conviction_label
from logic_market_regime import detect_market_regime
from logic_portfolio import (
    analyze_portfolio,
    build_portfolio,
    portfolio_final_recommendation,
    portfolio_confidence_band,
    portfolio_risk_triggers,
    adjust_for_market_regime
)

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Nifty50 AI Portfolio Advisor",
    layout="wide"
)

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Private decision-support tool | Rule-based AI engine")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_nifty50():
    return pd.read_csv("data/nifty50_list.csv")

df_all = load_nifty50()
df = df_all.copy()

# ==============================
# SIDEBAR – FILTERS
# ==============================
st.sidebar.header("Filters")

portfolio_mode = st.sidebar.checkbox("Enable Portfolio Mode", value=False)

sector = st.sidebar.selectbox(
    "Sector",
    ["All"] + sorted(df["Sector"].dropna().unique())
)

if sector != "All":
    df = df[df["Sector"] == sector]

if portfolio_mode:
    selected_stocks = st.sidebar.multiselect(
        "Select Stocks for Portfolio",
        df["Symbol"].tolist(),
        default=df["Symbol"].tolist()[:3]
    )
else:
    stock = st.sidebar.selectbox("Select Stock", df["Symbol"].tolist())
    selected_stocks = [stock]

st.sidebar.markdown("---")
st.sidebar.header("Investor Profile")

investment_amount = st.sidebar.number_input(
    "Investment Amount (₹)",
    min_value=10000,
    step=10000,
    value=100000
)

time_horizon = st.sidebar.selectbox(
    "Time Horizon",
    ["Short-term", "Medium-term", "Long-term"]
)

risk_profile = st.sidebar.selectbox(
    "Risk Profile",
    ["Conservative", "Moderate", "Aggressive"]
)

# ===============================
# MARKET REGIME (GLOBAL – REQUIRED)
# ===============================
market = detect_market_regime(
    index_trend="Neutral",
    volatility="Normal"
)

# ==============================
# PRICE FETCHING (CMP)
# ==============================
YAHOO_MAP = {
    "M&M": "MM",
    "TATAMOTORS": "TATAMOTORS",
    "RELIANCE": "RELIANCE"
}

@st.cache_data(ttl=300)
def get_cmp(symbol):
    sym = YAHOO_MAP.get(symbol, symbol)
    ticker = yf.Ticker(sym + ".NS")

    # 1️⃣ fast_info (fastest)
    try:
        price = ticker.fast_info.get("lastPrice")
        if price:
            return round(price, 2)
    except:
        pass

    # 2️⃣ info fallback
    try:
        price = ticker.info.get("regularMarketPrice")
        if price:
            return round(price, 2)
    except:
        pass

    # 3️⃣ historical fallback (most reliable)
    try:
        hist = ticker.history(period="1d")
        if not hist.empty:
            return round(hist["Close"].iloc[-1], 2)
    except:
        pass

    return None

# ==============================
# ADD CMP COLUMN (SAFE)
# ==============================
if "CMP (₹)" not in df.columns:
    df["CMP (₹)"] = df["Symbol"].apply(get_cmp)
# ==============================
# MAIN TABLE
# ==============================
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")
st.dataframe(df, use_container_width=True, hide_index=True)

# ==============================
# SINGLE STOCK ANALYSIS
# ==============================
if not portfolio_mode:
    st.markdown("---")
    row = df_all[df_all["Symbol"] == stock].iloc[0]

    st.header(f"{row['Company']} ({stock})")
    st.write(f"**Sector:** {row['Sector']}")
    st.write(f"**CMP:** ₹{get_cmp(stock) or '—'}")

    # ---------------------------------------------------
    # FUNDAMENTALS FETCH
    # ---------------------------------------------------
    fund = fetch_fundamentals(stock)
    fund = apply_fundamental_fallbacks(fund)

    # ---------------------------------------------------
    # FUNDAMENTALS DISPLAY
    # ---------------------------------------------------
    st.markdown("### 📊 Valuation & Profitability")
    def fmt(val, pct=False):
        if val is None:
            return "Not Available"
        if pct:
            return f"{round(val * 100, 2)}%"
        return round(val, 2)
        
    c1, c2, c3 = st.columns(3)
    c1.metric("PE Ratio", fmt(fund.get("PE")))
    c2.metric("PB Ratio", fmt(fund.get("PB")))
    c3.metric("EV / EBITDA", fmt(fund.get("EV_EBITDA")))

    c4, c5, c6 = st.columns(3)
    c4.metric("ROE", fmt(fund.get("ROE"), pct=True))
    c5.metric("ROCE", fmt(fund.get("ROCE"), pct=True))
    c6.metric("Net Margin", fmt(fund.get("NetMargin"), pct=True))
    
    # ---------------------------------------------------
    # METRIC QUALITY ASSESSMENT
    # ---------------------------------------------------
    st.markdown("### 🧪 Metric Quality Assessment")

    quality_metrics = [
        "ROE",
        "DebtEquity",
        "InterestCover",
        "PE",
        "RevenueGrowth",
        "EPSGrowth"
    ]

    for m in quality_metrics:
        val = fund.get(m)
        label = evaluate_metric(m, val)
        display = (
            f"{round(val*100,2)}%" if val and "Growth" in m else
            round(val, 2) if val is not None else "—"
        )
        st.write(f"**{m}:** {display} — {label}")

    # ---------------------------------------------------
    # FAIR VALUE & ENTRY ZONE
    # ---------------------------------------------------
    st.markdown("### 💰 Fair Value & Entry Zone")

    fair_value, upside_pct, entry_zone = estimate_fair_value(
        stock,
        fund,
        get_cmp
    )

    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Estimated Fair Value", f"₹{fair_value}" if fair_value else "—")
    fc2.metric("Upside / Downside", f"{upside_pct}%" if upside_pct is not None else "—")
    fc3.metric("Entry Zone", entry_zone if entry_zone else "—")

    # ---------------------------------------------------
    # NEWS
    # ---------------------------------------------------
    st.markdown("### 📰 Recent News")

    @st.cache_data(ttl=1800)
    def fetch_news(company):
        q = urllib.parse.quote(f"{company} stock India")
        url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        return feedparser.parse(url).entries[:5]

    news = fetch_news(row["Company"])
    news_summary = analyze_news(news)

    if not news:
        st.write("No recent news found.")
    else:
        n1, n2, n3 = st.columns(3)
        n1.metric("Positive", news_summary["positive"])
        n2.metric("Neutral", news_summary["neutral"])
        n3.metric("Negative", news_summary["negative"])
        st.info(f"**Overall News Bias:** {news_summary['overall']}")

        with st.expander("View Headlines"):
            for n in news:
                st.markdown(f"- [{n.title}]({n.link})")

    # ---------------------------------------------------
    # REPORT UPLOAD
    # ---------------------------------------------------
    st.markdown("### 📑 Company Reports")

    annual_pdf = st.file_uploader("Upload Annual Report (PDF)", type=["pdf"])
    quarterly_pdf = st.file_uploader("Upload Quarterly Report (PDF)", type=["pdf"])

    def extract_text(pdf):
        if not pdf:
            return ""
        reader = PdfReader(pdf)
        text = ""
        for p in reader.pages[:5]:
            text += p.extract_text() or ""
        return text.lower()

    annual_text = extract_text(annual_pdf)
    quarterly_text = extract_text(quarterly_pdf)

    # ---------------------------------------------------
    # QUARTERLY INTELLIGENCE
    # ---------------------------------------------------
    q_score, q_signals = analyze_quarterly_text(quarterly_text)

    # ---------------------------------------------------
    # SCORING ENGINE
    # ---------------------------------------------------
    score, rec, reasons = score_stock(
        fund,
        news_summary,
        annual_text,
        quarterly_text,
        risk_profile
    )

    if q_score:
        score = max(0, min(100, score + q_score))
        for s in q_signals:
            reasons.append(f"Quarterly insight: {s}")

    # ---------------------------------------------------
    # CONFIDENCE & TRIGGERS
    # ---------------------------------------------------
    red_flags_count = len(detect_red_flags(fund))
    profile_warnings_count = len(
        detect_profile_mismatch(fund, risk_profile)
    )

    confidence = confidence_band(
        score,
        red_flags_count,
        profile_warnings_count
    )

    # ==============================
    # FINAL RECOMMENDATION
    # ==============================
    st.markdown("## 📌 Final Recommendation")

    final_text = f"{rec} ({confidence})"

    if rec == "BUY":
        st.success(final_text)
    elif rec == "HOLD":
        st.warning(final_text)
    else:
        st.error(final_text)

    # ---------------------------------------------------
    # MARKET REGIME
    # ---------------------------------------------------
    market = detect_market_regime(
        index_trend="Neutral",
        volatility="Normal"
    )

    st.markdown("### 🌍 Market Regime Impact")
    st.info(f"{market['regime']} — {market['note']}")

    # ---------------------------------------------------
    # AI EXPLANATION
    # ---------------------------------------------------
    st.markdown("## 🧠 AI Advisory Explanation")
    st.markdown(
        generate_explanation(
            stock,
            score,
            rec,
            reasons,
            risk_profile,
            time_horizon
        )
    )
# ==============================
# THESIS INVALIDATION / RISK TRIGGERS (Single Stock Only)
# ==============================
st.markdown("### ⚠ What Could Change This Recommendation?")

if not portfolio_mode:
    from logic_risk_triggers import risk_triggers

    triggers = risk_triggers(
        fund=fund,
        score=score,
        market=market
    )

    st.markdown("### ⚠️ What Could Change This Recommendation?")
    if not triggers:
        st.success("No major downside triggers identified.")
    else:
        for t in triggers:
            st.write(f"• {t}")

    # ---------------------------------------------------
    # ALLOCATION ENGINE
    # ---------------------------------------------------
    def conviction_multiplier(confidence):
        if "High" in confidence:
            return 1.0
        if "Medium" in confidence:
            return 0.7
        return 0.4

    def suggest_allocation(
        score, rec, risk_profile, total_investment, confidence, regime_multiplier
    ):
        if rec == "BUY":
            alloc_pct = 12
        elif rec == "HOLD":
            alloc_pct = 6
        else:
            alloc_pct = 2

        if score >= 80:
            alloc_pct += 2
        elif score < 50:
            alloc_pct -= 2

        alloc_pct *= conviction_multiplier(confidence)
        alloc_pct *= market["risk_multiplier"]

        caps = {
            "Conservative": 15,
            "Moderate": 25,
            "Aggressive": 40
        }

        alloc_pct = min(alloc_pct, caps[risk_profile])
        alloc_pct = max(0, round(alloc_pct, 1))
        alloc_amt = round(total_investment * alloc_pct / 100)

        return alloc_pct, alloc_amt

    alloc_pct, alloc_amt = suggest_allocation(
        score,
        rec,
        risk_profile,
        investment_amount,
        confidence,
        market["risk_multiplier"]
    )

    st.markdown("## 💼 Suggested Allocation")
    st.metric("Allocation %", f"{alloc_pct}%")
    st.metric("Amount (₹)", f"₹{alloc_amt:,}")

# ===============================
# PORTFOLIO SUMMARY (CLEAN)
# ===============================
st.markdown("---")
st.markdown("## 📊 Portfolio Intelligence Summary")

from logic_portfolio import (
    build_portfolio,
    analyze_portfolio,
    portfolio_final_recommendation,
    portfolio_confidence_band,
    adjust_for_market_regime
)

portfolio = build_portfolio(df_all, selected_stocks)
portfolio_result = analyze_portfolio(portfolio, risk_profile)

st.metric("Portfolio Risk Score", portfolio_result["risk_score"])

for w in portfolio_result["warnings"]:
    st.warning(w)

for i in portfolio_result["insights"]:
    st.info(i)

# ==============================
# PORTFOLIO RISK TRIGGERS
# ==============================

if portfolio_mode:
    st.markdown("### ⚠️ Portfolio Risk Triggers")

    triggers = portfolio_risk_triggers(
        portfolio_result=portfolio_result,
        market=market
    )

    if not triggers:
        st.success("No major portfolio-level risk triggers detected.")
    else:
        for t in triggers:
            st.write(f"• {t}")
            
# -------------------------------
# FINAL PORTFOLIO RECOMMENDATION
# -------------------------------
portfolio_action, portfolio_reason = portfolio_final_recommendation(
    portfolio_result["risk_score"]
)

st.markdown("## 🧭 Portfolio Final Recommendation")
if portfolio_action == "BUY":
    st.success(f"BUY – {portfolio_reason}")
elif portfolio_action == "HOLD":
    st.warning(f"HOLD – {portfolio_reason}")
else:
    st.error(f"REDUCE – {portfolio_reason}")

# =====================================
# CAPITAL DEPLOYMENT PLAN
# =====================================
st.markdown("## 💰 Capital Deployment Plan")

from logic_capital_deployment import capital_deployment_plan

deployment = capital_deployment_plan(
    recommendation=portfolio_action,
    confidence=portfolio_result["risk_score"],
    time_horizon=time_horizon,
    investment_amount=investment_amount
)

st.dataframe(deployment, use_container_width=True)

# ----------------------------------------
# PORTFOLIO STRESS TEST
# ----------------------------------------
st.markdown("## 🚨 Portfolio Stress Test")

from logic_portfolio_stress import portfolio_stress_test

stress = portfolio_stress_test(portfolio, market)

col1, col2, col3 = st.columns(3)
col1.metric("📉 Correction Drawdown", f"{stress['Correction Drawdown %']}%")
col2.metric("🐻 Bear Market Drawdown", f"{stress['Bear Market Drawdown %']}%")
col3.metric("⚠️ Stress Rating", stress["Stress Rating"])

if stress["Stress Rating"] == "HIGH":
    st.error("High downside risk in severe market conditions.")
elif stress["Stress Rating"] == "MEDIUM":
    st.warning("Moderate drawdown risk. Position sizing matters.")
else:
    st.success("Portfolio shows defensive resilience.")
    
# ==================================
# PORTFOLIO PERFORMANCE SIMULATION
# ==================================

from logic_portfolio_performance import simulate_portfolio_performance

st.markdown("### 📈 Portfolio Performance Simulation")

performance = simulate_portfolio_performance(portfolio)

if performance:
    c1, c2, c3 = st.columns(3)

    c1.metric("Expected CAGR", f"{performance['cagr_pct']}%")
    c2.metric("Max Drawdown", f"-{performance['max_drawdown_pct']}%")
    c3.metric("Risk-Adjusted Score", performance["risk_adjusted_score"])

    if performance["risk_adjusted_score"] >= 1.2:
        st.success("Strong risk-adjusted portfolio performance expected")
    elif performance["risk_adjusted_score"] >= 0.8:
        st.warning("Moderate returns with manageable risk")
    else:
        st.error("High drawdown risk relative to expected return")
else:
    st.info("Portfolio performance simulation unavailable")
    
st.caption("Deployment plan is indicative and based on risk, conviction, and market conditions.")

# -------------------------------
# CONFIDENCE BAND
# -------------------------------
portfolio_confidence = portfolio_confidence_band(
    portfolio_result["risk_score"],
    len(portfolio_result["warnings"])
)

st.markdown("### 🎯 Portfolio Confidence")
st.info(portfolio_confidence)

# ==================================
# PORTFOLIO REBALANCING SIGNAL
# ==================================

from logic_rebalancing import portfolio_rebalancing_signal

st.markdown("### 🔄 Portfolio Rebalancing Signal")

rebalance_action, rebalance_reasons = portfolio_rebalancing_signal(
    portfolio_result=portfolio_result,
    market=market,
    confidence=portfolio_confidence
)

if rebalance_action == "REBALANCE NOW":
    st.error(f"🔄 {rebalance_action}")
elif rebalance_action == "MONITOR":
    st.warning(f"⏳ {rebalance_action}")
else:
    st.success(f"✅ {rebalance_action}")

for r in rebalance_reasons:
    st.write(f"• {r}")
    
# -------------------------------
# MARKET REGIME ADJUSTMENT
# -------------------------------
adjusted_action = adjust_for_market_regime(
    portfolio_action,
    market
)

st.markdown("### 🌍 Market Regime Adjustment")
if adjusted_action != portfolio_action:
    st.warning(
        f"⚠️ Market regime adjusted action\n\n"
        f"Original: **{portfolio_action}** → Adjusted: **{adjusted_action}**"
    )
else:
    st.success(f"✅ Portfolio action unchanged: **{portfolio_action}**")

st.info(f"**Market Regime:** {market.get('regime')} – {market.get('note')}")

# -------------------------------
# FINAL PORTFOLIO COMPOSITION
# -------------------------------
st.markdown("## 📋 Final Portfolio Composition")
st.dataframe(pd.DataFrame(portfolio), use_container_width=True)
# =====================================
# PORTFOLIO STRESS TEST
# =====================================
st.markdown("## 🧪 Portfolio Stress Test")

from logic_stress_test import stress_test_portfolio

scenario = st.selectbox(
    "Select Stress Scenario",
    [
        "Market Crash (-20%)",
        "Interest Rate Hike",
        "Commodity Spike",
        "Global Risk-Off",
        "Bull Run"
    ]
)

stress = stress_test_portfolio(portfolio_result, scenario)

st.metric(
    "Stressed Portfolio Risk Score",
    stress["stressed_score"]
)

if stress["action_bias"] == "BUY":
    st.success(f"Suggested Action Bias: {stress['action_bias']}")
elif stress["action_bias"] == "HOLD":
    st.warning(f"Suggested Action Bias: {stress['action_bias']}")
else:
    st.error(f"Suggested Action Bias: {stress['action_bias']}")

for w in stress["warnings"]:
    st.warning(w)
    
# ==============================
# FINAL REMARKS
# ==============================
st.markdown("### 🔍 Confidence Level")
st.info(confidence if not portfolio_mode else "Portfolio mode confidence")

st.markdown("### 🔁 What Could Change This Recommendation?")

st.markdown("### ⚠️ What Could Change This Recommendation")

if portfolio_mode:
    triggers = portfolio_risk_triggers(
        portfolio_result=portfolio_result,
        market=market
    )
else:
    from logic_risk_triggers import risk_triggers
    triggers = risk_triggers(
        fund=fund,
        score=score,
        market=market
    )

if not triggers:
    st.success("No major downside risk triggers identified.")
else:
    for t in triggers:
        st.write(f"• {t}")

if not triggers:
    st.success("No major downside triggers identified at this time.")
else:
    for t in triggers:
        st.write(f"• {t}")

st.caption("Prices may be delayed. For private analytical use only.")
