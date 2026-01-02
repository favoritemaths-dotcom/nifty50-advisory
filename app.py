import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

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

df = load_nifty50()

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

# ==================================================
# Yahoo symbol normalization (minimal & stable)
# ==================================================
YAHOO_MAP = {
    "M&M": "MM",
    "TATAMOTORS": "TATAMOTORS",
    "RELIANCE": "RELIANCE"
}

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

df["CMP (₹)"] = df["Symbol"].apply(
    lambda x: st.session_state.price_cache.get(x)
)

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

stock_row = df[df["Symbol"] == selected_stock].iloc[0]

st.subheader(f"{stock_row['Company']} ({selected_stock})")
st.write(f"**Sector:** {stock_row['Sector']}")
st.write(f"**CMP:** ₹{stock_row['CMP (₹)']}")

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
