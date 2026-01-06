import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
import urllib.parse
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
    ["All"] + sorted(df["Sector"].unique())
)

if sector != "All":
    df = df[df["Sector"] == sector]

stock = st.sidebar.selectbox("Select Stock", df["Symbol"].tolist())

st.sidebar.markdown("---")
st.sidebar.header("Investor Profile")

investment_amount = st.sidebar.number_input(
    "Investment Amount (₹)", min_value=10000, step=10000, value=100000
)

time_horizon = st.sidebar.selectbox(
    "Time Horizon", ["Short-term", "Medium-term", "Long-term"]
)

risk_profile = st.sidebar.selectbox(
    "Risk Profile", ["Conservative", "Moderate", "Aggressive"]
)

# ==================================================
# PRICE
# ==================================================
YAHOO_MAP = {"M&M": "MM"}

def get_cmp(symbol):
    try:
        sym = YAHOO_MAP.get(symbol, symbol)
        return round(yf.Ticker(sym + ".NS").fast_info.get("lastPrice"), 2)
    except:
        return None

df["CMP (₹)"] = df["Symbol"].apply(get_cmp)

# ==================================================
# TABLE
# ==================================================
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")
st.dataframe(df, use_container_width=True, hide_index=True)

# ==================================================
# SELECTED STOCK
# ==================================================
st.markdown("---")
row = df_all[df_all["Symbol"] == stock].iloc[0]
cmp = get_cmp(stock)

st.header(f"{row['Company']} ({stock})")
st.write(f"**Sector:** {row['Sector']}")
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
            "EV_EBITDA": info.get("enterpriseToEbitda"),
            "ROE": info.get("returnOnEquity"),
            "ROCE": info.get("returnOnAssets"),
            "NetMargin": info.get("profitMargins"),
            "DebtEquity": info.get("debtToEquity"),
            "InterestCover": info.get("interestCoverage"),
            "CurrentRatio": info.get("currentRatio"),
            "RevenueGrowth": info.get("revenueGrowth"),
            "EPSGrowth": info.get("earningsGrowth"),
        }
    except:
        return {}

fund = fetch_fundamentals(stock)

# ==================================================
# FAIR VALUE (B1) – FIXED
# ==================================================
def estimate_fair_value(stock, fund):
    try:
        eps = yf.Ticker(stock + ".NS").info.get("trailingEps")
    except:
        return None, None, None

    pe = fund.get("PE")
    if eps is None or pe is None:
        return None, None, None

    fair_pe = 18 if pe <= 15 else 22 if pe <= 25 else 25
    fair_value = round(eps * fair_pe)

    cmp = get_cmp(stock)
    upside = round((fair_value - cmp) / cmp * 100, 1) if cmp else None

    if cmp and cmp <= 0.85 * fair_value:
        zone = "🟢 Attractive"
    elif cmp and cmp <= fair_value:
        zone = "🟡 Reasonable"
    else:
        zone = "🔴 Expensive"

    return fair_value, upside, zone

fair_value, upside_pct, entry_zone = estimate_fair_value(stock, fund)

st.markdown("### 💰 Fair Value & Entry Zone")
c1, c2, c3 = st.columns(3)
c1.metric("Estimated Fair Value", f"₹{fair_value}" if fair_value else "—")
c2.metric("Upside / Downside", f"{upside_pct}%" if upside_pct is not None else "—")
c3.metric("Entry Zone", entry_zone if entry_zone else "—")

# ==================================================
# NEWS
# ==================================================
@st.cache_data(ttl=1800)
def fetch_news(company):
    q = urllib.parse.quote(f"{company} stock India")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    return feedparser.parse(url).entries[:5]

st.markdown("### 📰 Recent News")
news = fetch_news(row["Company"])
for n in news:
    st.markdown(f"- [{n.title}]({n.link})")

# ==================================================
# REPORTS
# ==================================================
st.markdown("### 📑 Company Reports")

annual_pdf = st.file_uploader("Upload Annual Report", type=["pdf"])
quarterly_pdf = st.file_uploader("Upload Quarterly Report", type=["pdf"])

def extract_text(pdf):
    if not pdf:
        return ""
    reader = PdfReader(pdf)
    return " ".join([p.extract_text() or "" for p in reader.pages[:5]]).lower()

annual_text = extract_text(annual_pdf)
quarterly_text = extract_text(quarterly_pdf)

# ==================================================
# SCORING ENGINE
# ==================================================
def score_stock(fund, news, annual_text, risk):
    score = 50
    reasons = []

    if fund.get("PE") and fund["PE"] < 25:
        score += 5; reasons.append("Reasonable valuation.")
    if fund.get("ROE") and fund["ROE"] > 0.15:
        score += 7; reasons.append("Strong ROE.")
    if fund.get("DebtEquity") and fund["DebtEquity"] > 2:
        score -= 7; reasons.append("High leverage risk.")
    if fund.get("RevenueGrowth") and fund["RevenueGrowth"] > 0.1:
        score += 5; reasons.append("Revenue growth visible.")
    if news:
        score += 5; reasons.append("Active news flow.")

    score = max(0, min(score, 100))
    rec = "BUY" if score >= 70 else "HOLD" if score >= 50 else "AVOID"
    return score, rec, reasons

score, rec, reasons = score_stock(fund, news, annual_text, risk_profile)

# ==================================================
# AI EXPLANATION
# ==================================================
def generate_explanation(stock, score, rec, reasons, risk, horizon):
    text = [
        f"### 🤖 AI Advisory View – {stock}",
        f"Score: **{score}/100** | Recommendation: **{rec}**",
        f"Risk Profile: **{risk}**, Horizon: **{horizon}**",
        "#### Key Drivers:"
    ]
    for r in reasons:
        text.append(f"• {r}")
    text.append("_Rule-based decision support, not financial advice._")
    return "\n\n".join(text)

st.markdown("## 🧠 AI Advisory Explanation")
st.markdown(generate_explanation(stock, score, rec, reasons, risk_profile, time_horizon))

# ==================================================
# ALLOCATION
# ==================================================
def suggest_allocation(score, rec, risk, amount):
    base = 12 if rec == "BUY" else 6 if rec == "HOLD" else 2
    cap = {"Conservative": 15, "Moderate": 25, "Aggressive": 40}[risk]
    pct = min(base, cap)
    return pct, round(amount * pct / 100)

alloc_pct, alloc_amt = suggest_allocation(score, rec, risk_profile, investment_amount)

st.markdown("## 💼 Suggested Portfolio Allocation")
st.metric("Allocation %", f"{alloc_pct}%")
st.metric("Investment Amount", f"₹{alloc_amt:,}")

st.caption("Prices may be delayed. For private analytical use only.")
