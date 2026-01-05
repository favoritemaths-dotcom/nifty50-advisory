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
# FUNDAMENTALS (FULL SET)
# ==================================================
@st.cache_data(ttl=86400)
def fetch_fundamentals(symbol):
    try:
        info = yf.Ticker(symbol + ".NS").info
        return {
            # Valuation
            "PE": info.get("trailingPE"),
            "PB": info.get("priceToBook"),
            "EV_EBITDA": info.get("enterpriseToEbitda"),

            # Profitability
            "ROE": info.get("returnOnEquity"),
            "ROCE": info.get("returnOnAssets"),   # proxy
            "NetMargin": info.get("profitMargins"),

            # Financial Strength
            "DebtEquity": info.get("debtToEquity"),
            "InterestCover": info.get("interestCoverage"),
            "CurrentRatio": info.get("currentRatio"),

            # Growth
            "RevenueGrowth": info.get("revenueGrowth"),
            "EPSGrowth": info.get("earningsGrowth"),
        }
    except:
        return {}

fund = fetch_fundamentals(stock)

# ==================================================
# FUNDAMENTALS DISPLAY
# ==================================================
st.markdown("### 📊 Valuation & Profitability")

c1, c2, c3 = st.columns(3)
c1.metric("PE Ratio", round(fund.get("PE"), 2) if fund.get("PE") else "—")
c2.metric("PB Ratio", round(fund.get("PB"), 2) if fund.get("PB") else "—")
c3.metric("EV / EBITDA", round(fund.get("EV_EBITDA"), 2) if fund.get("EV_EBITDA") else "—")

c4, c5, c6 = st.columns(3)
c4.metric("ROE", f"{round(fund.get('ROE')*100,2)}%" if fund.get("ROE") else "—")
c5.metric("ROCE", f"{round(fund.get('ROCE')*100,2)}%" if fund.get("ROCE") else "—")
c6.metric("Net Margin", f"{round(fund.get('NetMargin')*100,2)}%" if fund.get("NetMargin") else "—")

st.markdown("### 🛡️ Financial Strength & Growth")

c7, c8, c9 = st.columns(3)
c7.metric("Debt / Equity", round(fund.get("DebtEquity"), 2) if fund.get("DebtEquity") else "—")
c8.metric("Interest Coverage", round(fund.get("InterestCover"), 2) if fund.get("InterestCover") else "—")
c9.metric("Current Ratio", round(fund.get("CurrentRatio"), 2) if fund.get("CurrentRatio") else "—")

c10, c11 = st.columns(2)
c10.metric("Revenue Growth (YoY)", f"{round(fund.get('RevenueGrowth')*100,2)}%" if fund.get("RevenueGrowth") else "—")
c11.metric("EPS Growth (YoY)", f"{round(fund.get('EPSGrowth')*100,2)}%" if fund.get("EPSGrowth") else "—")

# ==================================================
# NEWS
# ==================================================
@st.cache_data(ttl=1800)
def fetch_news(company):
    q = urllib.parse.quote(f"{company} stock India")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    return feed.entries[:5]

st.markdown("### 📰 Recent News & Events")
news = fetch_news(row["Company"])

if not news:
    st.write("No recent news found.")
else:
    for n in news:
        st.markdown(f"- [{n.title}]({n.link})")

# ==================================================
# REPORT UPLOAD
# ==================================================
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

# ==================================================
# SCORING ENGINE (USES FULL METRICS)
# ==================================================
def score_stock(fund, news, annual_text, quarterly_text, risk):
    score = 50
    reasons = []

    # Valuation
    if fund.get("PE") and fund["PE"] < 25:
        score += 5
        reasons.append("Valuation is reasonable (PE < 25).")

    # Profitability
    if fund.get("ROE") and fund["ROE"] > 0.15:
        score += 7
        reasons.append("Strong ROE indicates efficient capital use.")

    if fund.get("NetMargin") and fund["NetMargin"] > 0.1:
        score += 5
        reasons.append("Healthy net margins.")

    # Financial strength
    if fund.get("DebtEquity") and fund["DebtEquity"] < 1:
        score += 5
        reasons.append("Low leverage improves financial stability.")
    elif fund.get("DebtEquity") and fund["DebtEquity"] > 2:
        score -= 7
        reasons.append("High debt increases risk.")

    if fund.get("InterestCover") and fund["InterestCover"] < 2:
        score -= 5
        reasons.append("Low interest coverage is a risk.")

    # Growth
    if fund.get("RevenueGrowth") and fund["RevenueGrowth"] > 0.1:
        score += 5
        reasons.append("Healthy revenue growth.")

    if fund.get("EPSGrowth") and fund["EPSGrowth"] > 0.1:
        score += 5
        reasons.append("Earnings growth supports valuation.")

    # News & reports
    if news:
        score += 5
        reasons.append("Recent news flow present.")

    if "risk" in annual_text:
        score -= 5
        reasons.append("Risks highlighted in annual report.")

    # Risk profile adjustment
    if risk == "Conservative" and fund.get("DebtEquity") and fund["DebtEquity"] > 1:
        score -= 5
        reasons.append("Conservative profile penalizes leverage.")
    elif risk == "Aggressive":
        score += 3
        reasons.append("Aggressive profile allows higher risk.")

    score = max(0, min(score, 100))

    if score >= 70:
        rec = "BUY"
    elif score >= 50:
        rec = "HOLD"
    else:
        rec = "AVOID"

    return score, rec, reasons

def suggest_allocation(
    score,
    recommendation,
    risk_profile,
    total_investment
):
    """
    Suggest portfolio allocation % and amount
    """

    # Base allocation by recommendation
    if recommendation == "BUY":
        alloc_pct = 12
    elif recommendation == "HOLD":
        alloc_pct = 6
    else:
        alloc_pct = 2

    # Score adjustment
    if score >= 80:
        alloc_pct += 2
    elif score < 50:
        alloc_pct -= 2

    # UPDATED risk caps (as per your rule)
    risk_caps = {
        "Conservative": 15,
        "Moderate": 25,
        "Aggressive": 40
    }

    max_cap = risk_caps.get(risk_profile, 25)
    alloc_pct = min(alloc_pct, max_cap)
    alloc_pct = max(0, alloc_pct)

    alloc_amount = round(total_investment * alloc_pct / 100, 0)

    return alloc_pct, alloc_amount

# ==============================
# PORTFOLIO ALLOCATION
# ==============================
st.markdown("## 💼 Suggested Portfolio Allocation")

alloc_pct, alloc_amt = suggest_allocation(
    score,
    rec,
    risk_profile,
    investment_amount
)

st.metric("Suggested Allocation", f"{alloc_pct}%")
st.metric("Suggested Investment Amount", f"₹{int(alloc_amt):,}")

if alloc_pct == 0:
    st.warning("This stock is not recommended for allocation currently.")
elif alloc_pct <= 5:
    st.info("Small allocation suggested due to moderate risk.")
else:
    st.success("Allocation aligns with your risk profile.")

# ==================================================
# AI EXPLANATION
# ==================================================
def generate_ai_explanation(stock, score, rec, reasons, risk, horizon):
    text = f"""
### 🤖 AI Advisor View

Based on your **{risk.lower()}** risk profile and **{horizon.lower()}** horizon,
**{stock}** scores **{score}/100**.

**Recommendation:** **{rec}**

**Key Drivers:**
"""
    for r in reasons:
        text += f"\n• {r}"

    text += "\n\nThis is a decision-support tool, not financial advice."
    return text

# ==================================================
# OUTPUT
# ==================================================
st.markdown("## 🧠 Advisory Summary")

score, rec, reasons = score_stock(
    fund, news, annual_text, quarterly_text, risk_profile
)

st.metric("Stock Quality Score", f"{score}/100")

if rec == "BUY":
    st.success("🟢 BUY")
elif rec == "HOLD":
    st.warning("🟡 HOLD")
else:
    st.error("🔴 AVOID")

st.markdown("### Why this recommendation?")
for r in reasons:
    st.write(f"• {r}")

st.markdown("## 🤖 AI Advisor Explanation")
st.markdown(
    generate_ai_explanation(
        stock, score, rec, reasons, risk_profile, time_horizon
    )
)

st.caption("Prices may be delayed. For private analytical use only.")
