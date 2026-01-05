import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
import urllib.parse
from pypdf import PdfReader

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Nifty50 AI Portfolio Advisor",
    layout="wide"
)

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Private decision-support tool | Stable cached data")

# ==================================================
# LOAD NIFTY 50 DATA
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
# MAIN TABLE
# ==================================================
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")
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

def evaluate_metric(name, value):
    """
    Classify metric quality as Strong / Average / Weak
    """

    if value is None:
        return "—", "Neutral"

    # Profitability
    if name == "ROE":
        if value >= 0.18:
            return "✅ Strong", "green"
        elif value >= 0.12:
            return "⚠️ Average", "orange"
        else:
            return "❌ Weak", "red"

    # Leverage
    if name == "DebtEquity":
        if value <= 1:
            return "✅ Strong", "green"
        elif value <= 2:
            return "⚠️ Average", "orange"
        else:
            return "❌ Weak", "red"

    # Interest coverage
    if name == "InterestCover":
        if value >= 3:
            return "✅ Strong", "green"
        elif value >= 1.5:
            return "⚠️ Average", "orange"
        else:
            return "❌ Weak", "red"

    # Valuation
    if name == "PE":
        if value <= 25:
            return "✅ Reasonable", "green"
        elif value <= 40:
            return "⚠️ Expensive", "orange"
        else:
            return "❌ Very Expensive", "red"

    # Growth
    if name in ["RevenueGrowth", "EPSGrowth"]:
        if value >= 0.15:
            return "✅ Strong", "green"
        elif value >= 0.05:
            return "⚠️ Moderate", "orange"
        else:
            return "❌ Weak", "red"

    return "—", "Neutral"

def detect_red_flags(fund):
    """
    Detect high-risk financial red flags
    Returns a list of warning strings
    """
    flags = []

    debt = fund.get("DebtEquity")
    interest = fund.get("InterestCover")
    pe = fund.get("PE")
    eps_g = fund.get("EPSGrowth")
    rev_g = fund.get("RevenueGrowth")

    # Balance sheet stress
    if debt is not None and debt > 2.5:
        flags.append("Very high Debt/Equity (>2.5) indicates balance-sheet stress.")

    # Debt servicing risk
    if interest is not None and interest < 1.5:
        flags.append("Low interest coverage (<1.5) raises debt servicing risk.")

    # Valuation trap
    if pe is not None and pe > 40:
        if (eps_g is not None and eps_g < 0.05) or (rev_g is not None and rev_g < 0.05):
            flags.append("High valuation with weak growth suggests a valuation risk.")

    # Growth slowdown
    if eps_g is not None and eps_g < 0:
        flags.append("Negative EPS growth indicates earnings contraction.")

    return flags

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

# ==============================
# METRIC QUALITY FLAGS
# ==============================
st.markdown("### 🧪 Metric Quality Assessment")

quality_metrics = {
    "ROE": fund.get("ROE"),
    "DebtEquity": fund.get("DebtEquity"),
    "InterestCover": fund.get("InterestCover"),
    "PE": fund.get("PE"),
    "RevenueGrowth": fund.get("RevenueGrowth"),
    "EPSGrowth": fund.get("EPSGrowth"),
}

for metric, value in quality_metrics.items():
    label, color = evaluate_metric(metric, value)

    if value is None:
        display_value = "—"
    elif "Growth" in metric:
        display_value = f"{round(value*100,2)}%"
    else:
        display_value = round(value, 2)

    st.markdown(
        f"**{metric}**: {display_value} &nbsp;&nbsp; {label}"
    )

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
# SCORING ENGINE
# ==================================================
def score_stock(fund, news, annual_text, quarterly_text, risk):
    score = 50
    reasons = []

    if fund.get("PE") and fund["PE"] < 25:
        score += 5
        reasons.append("Reasonable valuation.")

    if fund.get("ROE") and fund["ROE"] > 0.15:
        score += 7
        reasons.append("Strong ROE.")

    if fund.get("NetMargin") and fund["NetMargin"] > 0.1:
        score += 5
        reasons.append("Healthy margins.")

    if fund.get("DebtEquity") and fund["DebtEquity"] < 1:
        score += 5
        reasons.append("Low leverage.")
    elif fund.get("DebtEquity") and fund["DebtEquity"] > 2:
        score -= 7
        reasons.append("High leverage risk.")

    if fund.get("RevenueGrowth") and fund["RevenueGrowth"] > 0.1:
        score += 5
        reasons.append("Revenue growth visible.")

    if news:
        score += 5
        reasons.append("Active recent news.")

    if "risk" in annual_text:
        score -= 5
        reasons.append("Risks mentioned in reports.")

    if risk == "Aggressive":
        score += 3

    # -----------------------------
    # RED FLAG OVERRIDES (D2)
    # -----------------------------
    red_flags = detect_red_flags(fund)

    if red_flags:
        penalty = min(15, 5 * len(red_flags))
        score -= penalty

        for f in red_flags:
            reasons.append(f"⚠️ {f}")

    # RED FLAG OVERRIDES (D2)
red_flags = detect_red_flags(fund)

if red_flags:
    penalty = min(15, 5 * len(red_flags))
    score -= penalty

    for f in red_flags:
        reasons.append(f"⚠️ {f}")

# ✅ THIS MUST COME AFTER D2
score = max(0, min(score, 100))

    score = max(0, min(score, 100))

    rec = "BUY" if score >= 70 else "HOLD" if score >= 50 else "AVOID"
    return score, rec, reasons

score, rec, reasons = score_stock(
    fund, news, annual_text, quarterly_text, risk_profile
)

# ==================================================
# ALLOCATION ENGINE
# ==================================================
def suggest_allocation(score, rec, risk_profile, total_investment):
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

    risk_caps = {
        "Conservative": 15,
        "Moderate": 25,
        "Aggressive": 40
    }

    alloc_pct = min(alloc_pct, risk_caps[risk_profile])
    alloc_pct = max(0, alloc_pct)

    alloc_amt = round(total_investment * alloc_pct / 100)
    return alloc_pct, alloc_amt

# ==================================================
# OUTPUT
# ==================================================
st.markdown("## 💼 Suggested Portfolio Allocation")

alloc_pct, alloc_amt = suggest_allocation(
    score, rec, risk_profile, investment_amount
)

st.metric("Suggested Allocation", f"{alloc_pct}%")
st.metric("Suggested Investment Amount", f"₹{alloc_amt:,}")

st.markdown("## 🧠 Advisory Summary")

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

st.caption("Prices may be delayed. For private analytical use only.")
