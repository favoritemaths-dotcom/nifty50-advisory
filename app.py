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
# FAIR VALUE ESTIMATION (B1)
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
    if not cmp:
        return fair_value, None, None

    upside_pct = round((fair_value - cmp) / cmp * 100, 1)

    if cmp <= 0.85 * fair_value:
        zone = "🟢 Attractive"
    elif cmp <= fair_value:
        zone = "🟡 Reasonable"
    else:
        zone = "🔴 Expensive"

    return fair_value, upside_pct, zone

fair_value, upside_pct, entry_zone = estimate_fair_value(stock, fund)

# ==================================================
# MAIN TABLE
# ==================================================
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")
st.dataframe(df, use_container_width=True, hide_index=True)

# ==================================================
# STOCK HEADER
# ==================================================
st.markdown("---")
row = df_all[df_all["Symbol"] == stock].iloc[0]

st.header(f"{row['Company']} ({stock})")
st.write(f"**Sector:** {row['Sector']}")
st.write(f"**CMP:** ₹{get_cmp(stock) if get_cmp(stock) else '—'} (Yahoo)")

# ==================================================
# FAIR VALUE UI
# ==================================================
st.markdown("### 💰 Fair Value & Entry Zone")
c1, c2, c3 = st.columns(3)

c1.metric("Estimated Fair Value", f"₹{fair_value}" if fair_value else "—")
c2.metric("Upside / Downside", f"{upside_pct}%" if upside_pct is not None else "—")
c3.metric("Entry Zone", entry_zone if entry_zone else "—")

# ==================================================
# FUNDAMENTAL METRICS DISPLAY
# ==================================================
st.markdown("### 📊 Valuation & Profitability")

a, b, c = st.columns(3)
a.metric("PE", round(fund.get("PE"), 2) if fund.get("PE") else "—")
b.metric("PB", round(fund.get("PB"), 2) if fund.get("PB") else "—")
c.metric("EV / EBITDA", round(fund.get("EV_EBITDA"), 2) if fund.get("EV_EBITDA") else "—")

d, e, f = st.columns(3)
d.metric("ROE", f"{round(fund.get('ROE')*100,2)}%" if fund.get("ROE") else "—")
e.metric("ROCE", f"{round(fund.get('ROCE')*100,2)}%" if fund.get("ROCE") else "—")
f.metric("Net Margin", f"{round(fund.get('NetMargin')*100,2)}%" if fund.get("NetMargin") else "—")

st.markdown("### 🛡️ Financial Strength & Growth")

g, h, i = st.columns(3)
g.metric("Debt / Equity", round(fund.get("DebtEquity"), 2) if fund.get("DebtEquity") else "—")
h.metric("Interest Coverage", round(fund.get("InterestCover"), 2) if fund.get("InterestCover") else "—")
i.metric("Current Ratio", round(fund.get("CurrentRatio"), 2) if fund.get("CurrentRatio") else "—")

j, k = st.columns(2)
j.metric("Revenue Growth", f"{round(fund.get('RevenueGrowth')*100,2)}%" if fund.get("RevenueGrowth") else "—")
k.metric("EPS Growth", f"{round(fund.get('EPSGrowth')*100,2)}%" if fund.get("EPSGrowth") else "—")

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

if not news:
    st.write("No recent news.")
else:
    for n in news:
        st.markdown(f"- [{n.title}]({n.link})")

# ==================================================
# PDF UPLOAD
# ==================================================
st.markdown("### 📑 Company Reports")
annual_pdf = st.file_uploader("Annual Report (PDF)", type=["pdf"])
quarterly_pdf = st.file_uploader("Quarterly Report (PDF)", type=["pdf"])

def extract_text(pdf):
    if not pdf:
        return ""
    reader = PdfReader(pdf)
    return " ".join(p.extract_text() or "" for p in reader.pages[:5]).lower()

annual_text = extract_text(annual_pdf)
quarterly_text = extract_text(quarterly_pdf)

# ==================================================
# RED FLAGS & PROFILE MISMATCH
# ==================================================
def detect_red_flags(f):
    flags = []
    if f.get("DebtEquity") and f["DebtEquity"] > 2.5:
        flags.append("Very high leverage")
    if f.get("InterestCover") and f["InterestCover"] < 1.5:
        flags.append("Weak interest coverage")
    return flags

def detect_profile_mismatch(f, profile):
    w = []
    if profile == "Conservative" and f.get("DebtEquity") and f["DebtEquity"] > 1:
        w.append("Leverage unsuitable for conservative profile")
    return w

# ==================================================
# SCORING ENGINE
# ==================================================
def score_stock(f, news, annual_text, quarterly_text, profile):
    score = 50
    reasons = []

    if f.get("ROE") and f["ROE"] > 0.15:
        score += 7
        reasons.append("Strong ROE")

    if f.get("DebtEquity") and f["DebtEquity"] < 1:
        score += 5
        reasons.append("Low leverage")

    if news:
        score += 5
        reasons.append("Recent news flow")

    red_flags = detect_red_flags(f)
    if red_flags:
        score -= 5 * len(red_flags)
        reasons.extend([f"⚠️ {x}" for x in red_flags])

    profile_warn = detect_profile_mismatch(f, profile)
    if profile_warn:
        score -= 5
        reasons.extend([f"⚠️ {x}" for x in profile_warn])

    score = max(0, min(score, 100))

    rec = "BUY" if score >= 70 else "HOLD" if score >= 50 else "AVOID"
    return score, rec, reasons

score, rec, reasons = score_stock(
    fund, news, annual_text, quarterly_text, risk_profile
)

# ==================================================
# AI EXPLANATION
# ==================================================
def generate_explanation(stock, score, rec, reasons, profile, horizon):
    text = [
        f"### 🤖 AI Advisory – {stock}",
        f"Score: **{score}/100** | Recommendation: **{rec}**",
        "",
        "Key Drivers:"
    ]
    text += [f"• {r}" for r in reasons]
    text.append("")
    text.append(f"Aligned with **{profile}** risk profile over **{horizon}** horizon.")
    return "\n".join(text)

st.markdown("## 🧠 AI Advisory Explanation")
st.markdown(generate_explanation(
    stock, score, rec, reasons, risk_profile, time_horizon
))

# ==================================================
# ALLOCATION
# ==================================================
def suggest_allocation(score, rec, profile, total):
    base = 12 if rec == "BUY" else 6 if rec == "HOLD" else 2
    caps = {"Conservative":15,"Moderate":25,"Aggressive":40}
    pct = min(base + (2 if score >= 80 else 0), caps[profile])
    return pct, round(total * pct / 100)

alloc_pct, alloc_amt = suggest_allocation(
    score, rec, risk_profile, investment_amount
)

st.markdown("## 💼 Suggested Allocation")
st.metric("Allocation %", f"{alloc_pct}%")
st.metric("Amount", f"₹{alloc_amt:,}")

st.caption("Prices may be delayed. Private analytical use only.")
