import requests
import urllib.parse
import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from datetime import datetime, timedelta

# ==================================================
# Page Configuration
# ==================================================
st.set_page_config(
    page_title="Nifty50 AI Portfolio Advisor",
    layout="wide"
)

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Private decision-support tool | Stable cached data")

# ==================================================
# Load Nifty 50 Stock List
# ==================================================
@st.cache_data
def load_nifty50():
    return pd.read_csv("data/nifty50_list.csv")

df_all = load_nifty50()
df = df_all.copy()

# ==================================================
# Sidebar – Filters
# ==================================================
st.sidebar.header("Filters")

selected_sector = st.sidebar.selectbox(
    "Select Sector",
    ["All"] + sorted(df["Sector"].unique().tolist())
)

if selected_sector != "All":
    df = df[df["Sector"] == selected_sector]

st.sidebar.markdown("---")

selected_stock = st.sidebar.selectbox(
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
    ["Short-term (<1 year)", "Medium-term (1–3 years)", "Long-term (3+ years)"]
)

risk_profile = st.sidebar.selectbox(
    "Risk Profile",
    ["Conservative", "Moderate", "Aggressive"]
)

# ==================================================
# Yahoo symbol normalization (minimal & stable)
# ==================================================
YAHOO_MAP = {
    "M&M": "MM",
    "TATAMOTORS": "TATAMOTORS",
    "RELIANCE": "RELIANCE"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/"
}

def get_cmp_from_yahoo(symbol):
    try:
        yahoo_symbol = YAHOO_MAP.get(symbol, symbol)
        ticker = yf.Ticker(yahoo_symbol + ".NS")
        price = ticker.fast_info.get("lastPrice")
        return round(price, 2) if price else None
    except Exception:
        return None


def get_cmp_from_nse(symbol):
    try:
        encoded = urllib.parse.quote(symbol, safe="")
        url = f"https://www.nseindia.com/api/quote-equity?symbol={encoded}"
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
        r = session.get(url, headers=HEADERS, timeout=5)
        data = r.json()
        return data.get("priceInfo", {}).get("lastPrice")
    except Exception:
        return None


def get_cmp(symbol):
    # 1️⃣ Yahoo (primary)
    price = get_cmp_from_yahoo(symbol)
    if price:
        return price, "Yahoo"

    # 2️⃣ NSE (fallback)
    price = get_cmp_from_nse(symbol)
    if price:
        return price, "NSE"

    # 3️⃣ Cached value
    cached = st.session_state.price_cache.get(symbol)
    if cached:
        return cached, "Cache"

    return None, "Unavailable"

# ==================================================
# Session Cache (Last Known Prices)
# ==================================================
if "price_cache" not in st.session_state:
    st.session_state.price_cache = {}

if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# ==================================================
# Fetch Prices (Best-effort, Cached)
# ==================================================
@st.cache_data(ttl=900)  # 15 minutes
def fetch_prices(symbols):
    prices = {}
    for sym in symbols:
        yahoo_sym = YAHOO_MAP.get(sym, sym)
        try:
            ticker = yf.Ticker(yahoo_sym + ".NS")
            fast = ticker.fast_info
            price = fast.get("lastPrice")
            if price:
                prices[sym] = round(price, 2)
        except Exception:
            pass
    return prices

symbols = df["Symbol"].tolist()
fresh_prices = fetch_prices(symbols)

for sym in symbols:
    if sym in fresh_prices:
        st.session_state.price_cache[sym] = fresh_prices[sym]

if fresh_prices:
    st.session_state.last_updated = datetime.now()

cmp_sources = {}

def resolve_cmp(symbol):
    price, source = get_cmp(symbol)
    if price:
        st.session_state.price_cache[symbol] = price
    cmp_sources[symbol] = source
    return price

df["CMP (₹)"] = df["Symbol"].apply(resolve_cmp)

# ==================================================
# MAIN TABLE – Nifty 50 List
# ==================================================
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# STOCK DETAIL VIEW
# ==================================================
st.markdown("---")
st.header("📌 Stock Detail View")

stock_row = df_all[df_all["Symbol"] == selected_stock].iloc[0]

st.subheader(f"{stock_row['Company']} ({selected_stock})")
st.write(f"**Sector:** {stock_row['Sector']}")
cmp_value = st.session_state.price_cache.get(selected_stock)
cmp_value, cmp_source = get_cmp(selected_stock)
st.write(
    f"**CMP:** ₹{cmp_value if cmp_value else '—'} "
    f"_(Source: {cmp_source})_"
)

# ==================================================
# Fetch Detailed Fundamentals (10 Metrics)
# ==================================================
@st.cache_data(ttl=86400)  # cache for 1 day
def fetch_fundamentals(symbol):
    yahoo_symbol = YAHOO_MAP.get(symbol, symbol)
    try:
        ticker = yf.Ticker(yahoo_symbol + ".NS")
        info = ticker.info

        return {
            # Valuation
            "PE": info.get("trailingPE"),
            "PB": info.get("priceToBook"),
            "EV_EBITDA": info.get("enterpriseToEbitda"),

            # Profitability
            "ROE": info.get("returnOnEquity"),
            "ROCE": info.get("returnOnAssets"),  # proxy
            "NetMargin": info.get("profitMargins"),

            # Financial Strength
            "DebtEquity": info.get("debtToEquity"),
            "InterestCover": info.get("interestCoverage"),
            "CurrentRatio": info.get("currentRatio"),

            # Growth
            "RevenueGrowth": info.get("revenueGrowth"),
            "EPSGrowth": info.get("earningsGrowth"),
        }

    except Exception:
        return {}

@st.cache_data(ttl=1800)  # cache for 30 minutes
def fetch_company_news(company_name):
    """
    Fetch recent company news using Google News RSS
    """
    query = f"{company_name} stock India"
encoded_query = urllib.parse.quote(query)

rss_url = (
    "https://news.google.com/rss/search?"
    f"q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
)

    feed = feedparser.parse(rss_url)

    news_items = []
    cutoff_date = datetime.now() - timedelta(days=7)

    for entry in feed.entries[:10]:
        published = (
            datetime(*entry.published_parsed[:6])
            if hasattr(entry, "published_parsed")
            else None
        )

        if published and published < cutoff_date:
            continue

        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "source": entry.source.title if hasattr(entry, "source") else "Unknown",
            "published": published.strftime("%d %b %Y") if published else ""
        })

    return news_items

fund = fetch_fundamentals(selected_stock)

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
# NEWS & EVENTS
# ==============================
st.markdown("### 📰 Recent News & Events")

news_items = fetch_company_news(stock_row["Company"])

if not news_items:
    st.write("No significant news found in the last 7 days.")
else:
    for item in news_items[:5]:
        st.markdown(
            f"• **{item['title']}**  \n"
            f"  _Source: {item['source']} | {item['published']}_  \n"
            f"  [Read article]({item['link']})"
        )

# ==================================================
# Footer
# ==================================================
if st.session_state.last_updated:
    st.caption(
        f"🟡 Prices may be delayed | Last updated: "
        f"{st.session_state.last_updated.strftime('%d %b %Y, %I:%M %p')}"
    )
else:
    st.caption("🟡 Prices loading…")
