import requests
import urllib.parse
import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from datetime import datetime, timedelta
from pypdf import PdfReader

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(page_title="Nifty50 AI Portfolio Advisor", layout="wide")

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Private decision-support tool | Stable cached data")

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_nifty50():
    return pd.read_csv("data/nifty50_list.csv")

df_all = load_nifty50()
df = df_all.copy()

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.header("Filters")

sector = st.sidebar.selectbox(
    "Sector",
    ["All"] + sorted(df["Sector"].unique().tolist())
)

if sector != "All":
    df = df[df["Sector"] == sector]

stock = st.sidebar.selectbox("Select Stock", df["Symbol"].tolist())

st.sidebar.markdown("---")
st.sidebar.header("Investor Profile")

investment_amount = st.sidebar.number_input(
    "Investment Amount (₹)", 10000, step=10000, value=100000
)

time_horizon = st.sidebar.selectbox(
    "Time Horizon",
    ["Short-term", "Medium-term", "Long-term"]
)

risk_profile = st.sidebar.selectbox(
    "Risk Profile",
    ["Conservative", "Moderate", "Aggressive"]
)

# ==================================================
# PRICE FETCHING
# ==================================================
YAHOO_MAP = {"M&M": "MM"}

def get_cmp(symbol):
    try:
        sym = YAHOO_MAP.get(symbol, symbol)
        price = yf.Ticker(sym + ".NS").fast_info.get("lastPrice")
        return round(price, 2) if price else None
    except:
        return None

df["CMP (₹)"] = df["Symbol"].apply(get_cmp)

# ==================================================
# TABLE
# ==================================================
st.subheader(f"Showing {len(df)} stocks")
st.dataframe(df, use_container_width=True, hide_index=True)

# ==================================================
# STOCK DETAIL
# ==================================================
st.markdown("---")
row = df_all[df_all["Symbol"] == stock].iloc[0]

st.header(f"{row['Company']} ({stock})")
st.write(f"**Sector:** {row['Sector']}")

cmp = get_cmp(stock)
st.write(f"**CMP:** ₹{cmp if cmp else '—'} (Yahoo)")

# ==================================================
# FUNDAMENTALS
# ==================================================
@st.cache_data(ttl=86400)
def fetch_fundamentals(symbol):
    try:
        info = yf.Ticker(symbol + ".NS").info
        return {
            "PE": info.get("trailingPE"),
            "PB": info.get("priceToBook"),
            "ROE": info.get("returnOnEquity"),
            "DebtEquity": info.get("debtToEquity"),
            "NetMargin": info.get("profitMargins"),
            "RevenueGrowth": info.get("revenueGrowth")
        }
    except:
        return {}

fund = fetch_fundamentals(stock)

st.markdown("### 📊 Fundamentals")
c1, c2, c3 = st.columns(3)
c1.metric("PE", round(fund.get("PE"), 2) if fund.get("PE") else "—")
c2.metric("PB", round(fund.get("PB"), 2) if fund.get("PB") else "—")
c3.metric("ROE", f"{round(fund.get('ROE')*100,2)}%" if fund.get("ROE") else "—")

# ==================================================
# NEWS
# ==================================================
@st.cache_data(ttl=1800)
def fetch_news(company):
    q = urllib.parse.quote(f"{company} stock India")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    return feed.entries[:5]

st.markdown("### 📰 Recent News")
news = fetch_news(row["Company"])

if not news:
    st.write("No recent news.")
else:
    for n in news:
        st.markdown(f"- [{n.title}]({n.link})")

# ==================================================
# REPORT UPLOAD
# ==================================================
st.markdown("### 📑 Company Reports")

annual_pdf = st.file_uploader("Upload Annual Report", type=["pdf"])
quarterly_pdf = st.file_uploader("Upload Quarterly Report", type=["pdf"])

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

# ==================================================
# SCORING ENGINE
# ==================================================
def score_stock(fund, news, annual_text, quarterly_text, risk):
    score = 50
    reasons = []

    if fund.get("PE") and fund["PE"] < 25:
        score += 5
        reasons.append("Reasonable valuation")

    if fund.get("ROE") and fund["ROE"] > 0.15:
        score += 7
        reasons.append("Strong ROE")

    if fund.get("DebtEquity") and fund["DebtEquity"] > 2:
        score -= 7
        reasons.append("High debt risk")

    if news:
        score += 5
        reasons.append("Active news flow")

    if "risk" in annual_text:
        score -= 5
        reasons.append("Risks mentioned in annual report")

    if risk == "Aggressive":
        score += 3

    score = max(0, min(score, 100))

    if score >= 70:
        rec = "BUY"
    elif score >= 50:
        rec = "HOLD"
    else:
        rec = "AVOID"

    return score, rec, reasons

# ==================================================
# AI EXPLANATION
# ==================================================
def generate_ai_explanation(stock, score, rec, reasons, risk, horizon):
    text = f"""
### 🤖 AI Advisor View

Based on a **{risk.lower()}** risk profile and **{horizon.lower()}** horizon,
**{stock}** scores **{score}/100**.

**Recommendation:** **{rec}**

**Key drivers:**
"""
    for r in reasons:
        text += f"\n• {r}"

    text += "\n\nThis is a decision-support tool, not investment advice."
    return text

# ==================================================
# OUTPUT
# ==================================================
st.markdown("## 🧠 Advisory Summary")

score, rec, reasons = score_stock(
    fund, news, annual_text, quarterly_text, risk_profile
)

st.metric("Score", f"{score}/100")

if rec == "BUY":
    st.success("🟢 BUY")
elif rec == "HOLD":
    st.warning("🟡 HOLD")
else:
    st.error("🔴 AVOID")

st.markdown("### Explanation")
st.markdown(
    generate_ai_explanation(
        stock, score, rec, reasons, risk_profile, time_horizon
    )
)

st.caption("Prices may be delayed. For private analytical use only.")
