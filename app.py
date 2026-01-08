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
    detect_red_flags
)
from logic_valuation import estimate_fair_value
from logic_news import analyze_news
from logic_quarterly import analyze_quarterly_text
from logic_scoring import score_stock, detect_profile_mismatch
from logic_explanation import generate_explanation
from logic_confidence import confidence_band, risk_triggers
from logic_market_regime import detect_market_regime
from logic_portfolio import analyze_portfolio

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

portfolio_mode = st.sidebar.checkbox(
    "Enable Portfolio Mode",
    value=False
)
sector = st.sidebar.selectbox(
    "Sector",
    ["All"] + sorted(df["Sector"].unique())
)

if sector != "All":
    df = df[df["Sector"] == sector]

if not portfolio_mode:
    stock = st.sidebar.selectbox(
        "Select Stock",
        df["Symbol"].tolist()
    )
    selected_stocks = [stock]
else:
    selected_stocks = st.sidebar.multiselect(
        "Select Stocks for Portfolio",
        df["Symbol"].tolist(),
        default=df["Symbol"].tolist()[:3]
    )

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

st.sidebar.markdown("---")
portfolio_mode = st.sidebar.checkbox(
    "Enable Portfolio Mode",
    value=False
)

# ==============================
# PRICE FETCHING (CMP)
# ==============================
YAHOO_MAP = {"M&M": "MM"}

def get_cmp(symbol):
    try:
        sym = YAHOO_MAP.get(symbol, symbol)
        price = yf.Ticker(sym + ".NS").fast_info.get("lastPrice")
        return round(price, 2) if price else None
    except:
        return None

df["CMP (₹)"] = df["Symbol"].apply(get_cmp)

# ==============================
# MAIN TABLE
# ==============================
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")
st.dataframe(df, use_container_width=True, hide_index=True)

# ==============================
# STOCK DETAIL
# ==============================
st.markdown("---")
row = df_all[df_all["Symbol"] == stock].iloc[0]

st.header(f"{row['Company']} ({stock})")
st.write(f"**Sector:** {row['Sector']}")

cmp = get_cmp(stock)
st.write(f"**CMP:** ₹{cmp if cmp else '—'}")

# ==============================
# FUNDAMENTALS
# ==============================
fund = fetch_fundamentals(stock)

# ==============================
# FAIR VALUE & ENTRY ZONE
# ==============================
st.markdown("### 💰 Fair Value & Entry Zone")

fair_value, upside_pct, entry_zone = estimate_fair_value(
    stock,
    fund,
    get_cmp
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Estimated Fair Value",
    f"₹{fair_value}" if fair_value else "—"
)

c2.metric(
    "Upside / Downside",
    f"{upside_pct}%" if upside_pct is not None else "—"
)

c3.metric(
    "Entry Zone",
    entry_zone if entry_zone else "—"
)

# ==============================
# FUNDAMENTALS DISPLAY
# ==============================
st.markdown("### 📊 Valuation & Profitability")

c1, c2, c3 = st.columns(3)
c1.metric("PE Ratio", round(fund.get("PE"), 2) if fund.get("PE") else "—")
c2.metric("PB Ratio", round(fund.get("PB"), 2) if fund.get("PB") else "—")
c3.metric("EV / EBITDA", round(fund.get("EV_EBITDA"), 2) if fund.get("EV_EBITDA") else "—")

c4, c5, c6 = st.columns(3)
c4.metric("ROE", f"{round(fund.get('ROE')*100,2)}%" if fund.get("ROE") else "—")
c5.metric("ROCE", f"{round(fund.get('ROCE')*100,2)}%" if fund.get("ROCE") else "—")
c6.metric("Net Margin", f"{round(fund.get('NetMargin')*100,2)}%" if fund.get("NetMargin") else "—")

# ==============================
# METRIC QUALITY
# ==============================
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

# ==============================
# NEWS
# ==============================
@st.cache_data(ttl=1800)
def fetch_news(company):
    q = urllib.parse.quote(f"{company} stock India")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    return feed.entries[:5]

st.markdown("### 📰 Recent News")
news = fetch_news(row["Company"])
news_summary = analyze_news(news)

if not news:
    st.write("No recent news found.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Positive", news_summary["positive"])
    c2.metric("Neutral", news_summary["neutral"])
    c3.metric("Negative", news_summary["negative"])
    st.info(f"Overall News Bias: **{news_summary['overall']}**")

    with st.expander("View Headlines"):
        for n in news:
            st.markdown(f"- [{n.title}]({n.link})")

# ==============================
# REPORT UPLOAD
# ==============================
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

# ==============================
# QUARTERLY INTELLIGENCE
# ==============================
q_score, q_signals = analyze_quarterly_text(quarterly_text)

# ==============================
# SCORING ENGINE
# ==============================
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

# ==============================
# CONFIDENCE & TRIGGERS
# ==============================
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
# MARKET REGIME
# ==============================
market = detect_market_regime(
    index_trend="Down",
    volatility="High"
)

regime_multiplier = market["risk_multiplier"]

# ==============================
# AI EXPLANATION
# ==============================
st.markdown("## 🧠 AI Advisory Explanation")

explanation = generate_explanation(
    stock,
    score,
    rec,
    reasons,
    risk_profile,
    time_horizon
)

st.markdown(explanation)

st.markdown("### 🌍 Market Regime Impact")
st.info(f"{market['regime']} Market — {market['note']}")

# ==============================
# CONVICTION MULTIPLIER
# ==============================
def conviction_multiplier(confidence):
    if "High" in confidence:
        return 1.0
    if "Medium" in confidence:
        return 0.7
    return 0.4

# ==============================
# ALLOCATION ENGINE
# ==============================
def suggest_allocation(score, rec, risk_profile, total_investment, confidence, regime_multiplier):
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
    alloc_pct *= regime_multiplier

    risk_caps = {
        "Conservative": 15,
        "Moderate": 25,
        "Aggressive": 40
    }

    alloc_pct = min(alloc_pct, risk_caps[risk_profile])
    alloc_pct = max(0, round(alloc_pct, 1))

    alloc_amt = round(total_investment * alloc_pct / 100)
    return alloc_pct, alloc_amt

alloc_pct, alloc_amt = suggest_allocation(
    score,
    rec,
    risk_profile,
    investment_amount,
    confidence,
    regime_multiplier
)

# ==============================
# BUILD PORTFOLIO STRUCTURE
# ==============================

portfolio = []

equal_alloc = round(alloc_pct / len(selected_stocks), 2) if selected_stocks else 0

for s in selected_stocks:
    r = df_all[df_all["Symbol"] == s].iloc[0]

    portfolio.append({
        "stock": s,
        "sector": r.get("Sector", "Unknown"),
        "allocation_pct": equal_alloc
    })

# ==============================
# PORTFOLIO INTELLIGENCE
# ==============================

portfolio = [
    {
        "stock": stock,
        "sector": row.get("Sector", "Unknown"),
        "allocation_pct": alloc_pct
    }
]

portfolio_result = analyze_portfolio(
    portfolio,
    risk_profile
)

st.markdown("## 📊 Portfolio Intelligence")

st.metric("Portfolio Risk Score", portfolio_result["risk_score"])

if portfolio_result["warnings"]:
    for w in portfolio_result["warnings"]:
        st.warning(w)

for i in portfolio_result["insights"]:
    st.info(i)
st.markdown("## 💼 Suggested Portfolio Allocation")
st.metric("Allocation %", f"{alloc_pct}%")
st.metric("Investment Amount", f"₹{alloc_amt:,}")

st.markdown("### 📋 Portfolio Composition")

st.dataframe(
    pd.DataFrame(portfolio),
    use_container_width=True
)

# ==============================
# FINAL CONFIDENCE & TRIGGERS
# ==============================
st.markdown("### 🔍 Recommendation Confidence")
st.info(confidence)

st.markdown("### 🔁 What Could Change This Recommendation?")
for t in risk_triggers(fund, q_score):
    st.write(f"• {t}")

st.caption("Prices may be delayed. For private analytical use only.")
