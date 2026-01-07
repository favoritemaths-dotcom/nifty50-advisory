import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
import urllib.parse
from pypdf import PdfReader
from logic_news import analyze_news

# ==============================
# IMPORT LOGIC MODULES
# ==============================
from logic_fundamentals import (
    fetch_fundamentals,
    evaluate_metric,
    detect_red_flags
)

from logic_valuation import estimate_fair_value
from logic_scoring import score_stock, detect_profile_mismatch
from logic_explanation import generate_explanation
from logic_confidence import confidence_band, change_triggers

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
# SIDEBAR
# ==============================
st.sidebar.header("Filters")

sector = st.sidebar.selectbox(
    "Sector",
    ["All"] + sorted(df["Sector"].unique())
)

if sector != "All":
    df = df[df["Sector"] == sector]

stock = st.sidebar.selectbox(
    "Select Stock",
    df["Symbol"].tolist()
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

# ==============================
# PRICE FETCHING
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
    st.write(f"**{m}:** {evaluate_metric(m, val)}")

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

    c1.metric("Positive News", news_summary["positive"])
    c2.metric("Neutral News", news_summary["neutral"])
    c3.metric("Negative News", news_summary["negative"])

    st.info(f"**Overall Impact:** {news_summary['impact_label']}")

    with st.expander("View Headlines"):
        for n in news:
            st.markdown(f"- [{n.title}]({n.link})")

# ==============================
# REPORT UPLOAD
# ==============================
st.markdown("### 📑 Company Reports")

annual_pdf = st.file_uploader("Upload Annual Report (PDF)", type=["pdf"])

def extract_text(pdf):
    if not pdf:
        return ""
    reader = PdfReader(pdf)
    text = ""
    for p in reader.pages[:5]:
        text += p.extract_text() or ""
    return text.lower()

annual_text = extract_text(annual_pdf)

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

# ==============================
# ALLOCATION ENGINE
# ==============================
def suggest_allocation(score, rec, risk_profile, total):
    base = 12 if rec == "BUY" else 6 if rec == "HOLD" else 2

    if score >= 80:
        base += 2
    elif score < 50:
        base -= 2

    caps = {
        "Conservative": 15,
        "Moderate": 25,
        "Aggressive": 40
    }

    pct = min(base, caps[risk_profile])
    pct = max(0, pct)
    amt = round(total * pct / 100)

    return pct, amt

alloc_pct, alloc_amt = suggest_allocation(
    score,
    rec,
    risk_profile,
    investment_amount
)

st.markdown("## 💼 Suggested Portfolio Allocation")
st.metric("Allocation %", f"{alloc_pct}%")
st.metric("Investment Amount", f"₹{alloc_amt:,}")

# ==============================
# CONFIDENCE & TRIGGERS
# ==============================
st.markdown("### 🔍 Recommendation Confidence")
st.info(confidence)

st.markdown("### 🔁 What Could Change This Recommendation?")
for t in change_triggers(fund):
    st.write(f"• {t}")

# ==============================
# FINAL NOTE
# ==============================
st.caption("Prices may be delayed. For private analytical use only.")
