import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
import urllib.parse
from pypdf import PdfReader
from logic_news import analyze_news
from logic_quarterly import analyze_quarterly_text
from logic_confidence import (
    confidence_band,
    risk_triggers,
    conviction_multiplier,
    conviction_label,
    counter_case_analysis,
    stabilize_confidence,
    thesis_invalidation
)

from logic_fundamentals import (
    fetch_fundamentals,
    evaluate_metric,
    detect_red_flags
)

from logic_valuation import estimate_fair_value
from logic_scoring import score_stock, detect_profile_mismatch
from logic_explanation import generate_explanation

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

    if val is None:
        st.write(f"**{m}:** Data unavailable")
    else:
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
# STEP 6 – NEWS INTELLIGENCE SIGNALS
# ==============================

news_bias = news_summary.get("impact_label", "Neutral")

if news_bias == "Positive":
    st.success("🟢 News sentiment supportive")
elif news_bias == "Negative":
    st.error("🔴 News sentiment adverse")
else:
    st.info("🟡 News sentiment neutral")

# ==============================
# STEP 6.1 – NEWS SCORE IMPACT
# ==============================

def news_score_adjustment(news_summary):
    """
    Converts news sentiment into a small score adjustment
    """
    impact = news_summary.get("impact_label", "Neutral")

    if impact == "Positive":
        return +3
    elif impact == "Negative":
        return -5
    return 0
    
# ==============================
# REPORT UPLOAD
# ==============================
st.markdown("### 📑 Company Reports")

annual_pdf = st.file_uploader("Upload Annual Report (PDF)", type=["pdf"])
quarterly_pdf = st.file_uploader(
    "Upload Quarterly Report (PDF)",
    type=["pdf"]
)

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
# SCORING ENGINE
# ==============================

q_score, q_signals = analyze_quarterly_text(quarterly_text)

# ==============================
# A4 – QUARTERLY INTELLIGENCE ADJUSTMENT
# ==============================

if q_score is not None:
    score_adjustment = min(10, max(-10, q_score))
else:
    score_adjustment = 0

quarterly_reasons = []

if q_signals:
    for s in q_signals:
        quarterly_reasons.append(f"📄 Quarterly insight: {s}")
        
score, rec, reasons = score_stock(
    fund,
    news_summary,
    annual_text,
    quarterly_text,
    risk_profile
)

# Apply news sentiment impact
news_adj = news_score_adjustment(news_summary)
score = max(0, min(100, score + news_adj))

if news_adj != 0:
    reasons.append(
        f"News sentiment adjustment: {news_summary['impact_label']} ({news_adj:+d})"
    )
    
# Apply quarterly score impact
score = max(0, min(100, score + score_adjustment))
reasons.extend(quarterly_reasons)

def adjust_for_time_horizon(score, fund, q_score, time_horizon):
    delta = 0
    reasons = []

    # SHORT TERM (3–6 months)
    if time_horizon == "Short-term":
        if q_score is not None and q_score < -5:
            delta -= 6
            reasons.append("Short-term outlook weakened by recent quarterly performance.")
        if fund.get("PE") and fund["PE"] > 30:
            delta -= 4
            reasons.append("High valuation increases short-term downside risk.")
        if fund.get("RevenueGrowth") and fund["RevenueGrowth"] > 0.15:
            delta += 3
            reasons.append("Strong growth momentum supports short-term optimism.")

    # MEDIUM TERM (6–18 months)
    elif time_horizon == "Medium-term":
        if fund.get("ROE") and fund["ROE"] > 0.18:
            delta += 4
            reasons.append("Healthy profitability supports medium-term holding.")
        if fund.get("DebtEquity") and fund["DebtEquity"] > 1.5:
            delta -= 4
            reasons.append("Elevated leverage may constrain medium-term returns.")

    # LONG TERM (3–5 years)
    elif time_horizon == "Long-term":
        if fund.get("ROE") and fund["ROE"] > 0.18:
            delta += 6
            reasons.append("Strong ROE supports long-term compounding.")
        if fund.get("RevenueGrowth") and fund["RevenueGrowth"] > 0.12:
            delta += 5
            reasons.append("Sustained growth supports long-term wealth creation.")
        if fund.get("DebtEquity") and fund["DebtEquity"] > 2:
            delta -= 6
            reasons.append("High leverage increases long-term balance-sheet risk.")

    return delta, reasons

# A11 – TIME HORIZON ADJUSTMENT
th_delta, th_reasons = adjust_for_time_horizon(
    score,
    fund,
    q_score,
    time_horizon
)

score = max(0, min(100, score + th_delta))
reasons.extend([f"⏳ {r}" for r in th_reasons])
# ==============================
# A5 – ANNUAL vs QUARTERLY CONTRADICTION CHECK
# ==============================

contradictions = []

# Annual strong signals
annual_positive = (
    fund.get("ROE") is not None and fund["ROE"] > 0.18
) or (
    fund.get("RevenueGrowth") is not None and fund["RevenueGrowth"] > 0.15
)

# Quarterly weak signals
quarterly_negative = q_score is not None and q_score < -5

if annual_positive and quarterly_negative:
    contradictions.append(
        "Strong annual fundamentals but recent quarterly performance shows weakness."
    )
if contradictions:
    reasons.extend([f"⚠️ {c}" for c in contradictions])
    confidence_penalty = 1
else:
    confidence_penalty = 0

# ==============================
# NEWS vs FUNDAMENTALS CONFLICT CHECK
# ==============================

news_conflicts = []

# Positive news but weak fundamentals
if news_summary["impact_label"] == "Positive":
    if fund.get("ROE") is not None and fund["ROE"] < 0.12:
        news_conflicts.append(
            "Positive news despite weak profitability (low ROE)."
        )
    if fund.get("DebtEquity") is not None and fund["DebtEquity"] > 1.5:
        news_conflicts.append(
            "Positive news but balance sheet leverage remains high."
        )

# Negative news but strong fundamentals
if news_summary["impact_label"] == "Negative":
    if fund.get("ROE") is not None and fund["ROE"] > 0.18:
        news_conflicts.append(
            "Negative news despite strong long-term profitability."
        )
    if fund.get("RevenueGrowth") is not None and fund["RevenueGrowth"] > 0.15:
        news_conflicts.append(
            "Negative news but revenue growth trend remains healthy."
        )

# Apply impact
if news_conflicts:
    reasons.extend([f"⚠️ {c}" for c in news_conflicts])
    confidence_penalty += 1
    
# ==============================
# STEP 5.2 – QUARTERLY SCORE ADJUSTMENT
# ==============================

red_flags_count = len(detect_red_flags(fund))
profile_warnings_count = len(
    detect_profile_mismatch(fund, risk_profile)
)

prev_confidence = confidence if 'confidence' in locals() else None

new_confidence = confidence_band(
    score,
    red_flags_count + confidence_penalty,
    profile_warnings_count
)

score_delta = score - prev_score if 'prev_score' in locals() else 10
confidence = (
    stabilize_confidence(prev_confidence, new_confidence, score_delta)
    if prev_confidence
    else new_confidence
)

prev_score = score
triggers = risk_triggers(fund, q_score)

counter_risks = counter_case_analysis(
    fund,
    score,
    rec,
    news_summary,
    q_score
)
if counter_risks:
    st.markdown("## ⚠️ Why You May Want to Be Cautious")
    for r in counter_risks:
        st.write(f"• {r}")
# ==============================
# A12 – CONVICTION-WEIGHTED RECOMMENDATION
# ==============================
final_rec = conviction_label(rec, confidence, score)
invalidation_reasons = thesis_invalidation(
    score,
    q_score,
    fund,
    news_summary
)

# ==============================
# AI EXPLANATION
# ==============================
st.markdown("## 🧠 AI Advisory Explanation")

explanation = generate_explanation(
    stock,
    score,
    final_rec,
    reasons,
    risk_profile,
    time_horizon
)

# ==============================
# A12.3 – FINAL RECOMMENDATION DISPLAY
# ==============================
st.markdown("## 📌 Final Recommendation")

if "BUY" in final_rec:
    st.success(final_rec)
elif "HOLD" in final_rec:
    st.warning(final_rec)
else:
    st.error(final_rec)
# ==============================
# A13 – THESIS INVALIDATION CHECK
# ==============================

if invalidation_reasons:
    st.markdown("### ❌ When This Recommendation Breaks")
    for r in invalidation_reasons:
        st.write(f"• {r}")
else:
    st.markdown("### ✅ Thesis Currently Intact")
# ==============================
# AI EXPLANATION
# ==============================
st.markdown("## 🧠 AI Advisory Explanation")

st.markdown(explanation)
st.markdown("### 🔁 What Could Change This Recommendation?")
for t in triggers:
    st.write(f"• {t}")

# ==============================
# ==============================
# ALLOCATION ENGINE
# ==============================
def suggest_allocation(score, rec, risk_profile, total_investment, confidence):
    # Base allocation by recommendation
    if rec == "BUY":
        alloc_pct = 12
    elif rec == "HOLD":
        alloc_pct = 6
    else:
        alloc_pct = 2

    # Score influence
    if score >= 80:
        alloc_pct += 2
    elif score < 50:
        alloc_pct -= 2

    # Apply conviction multiplier
    alloc_pct *= conviction_multiplier(confidence)

    # Risk caps
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
    score, rec, risk_profile, investment_amount, confidence
)

st.markdown("## 💼 Suggested Portfolio Allocation")
st.metric("Allocation %", f"{alloc_pct}%")
st.metric("Investment Amount", f"₹{alloc_amt:,}")

# ==============================
# CONFIDENCE & TRIGGERS
# ==============================
st.markdown("### 🔍 Recommendation Confidence")
st.info(confidence)

# ==============================
# FINAL NOTE
# ==============================
st.caption("Prices may be delayed. For private analytical use only.")
