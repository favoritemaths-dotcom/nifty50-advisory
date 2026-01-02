import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Nifty50 AI Portfolio Advisor",
    layout="wide"
)

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Stable cached prices | Private decision-support tool")

# --------------------------------------------------
# Load Nifty 50 list
# --------------------------------------------------
@st.cache_data
def load_nifty50():
    return pd.read_csv("data/nifty50_list.csv")

df = load_nifty50()

# --------------------------------------------------
# Sidebar filter
# --------------------------------------------------
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

# --------------------------------------------------
# Yahoo symbol normalization (minimal & stable)
# --------------------------------------------------
YAHOO_MAP = {
    "M&M": "MM",
    "RELIANCE": "RELIANCE",
    "TATAMOTORS": "TATAMOTORS"
}

# --------------------------------------------------
# Cached price store (session-level)
# --------------------------------------------------
if "price_cache" not in st.session_state:
    st.session_state.price_cache = {}

if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# --------------------------------------------------
# Fetch prices safely (NO BREAKING)
# --------------------------------------------------
@st.cache_data(ttl=900)  # 15 minutes
def fetch_prices(symbols):
    prices = {}
    for sym in symbols:
        yahoo_sym = YAHOO_MAP.get(sym, sym)
        try:
            ticker = yf.Ticker(yahoo_sym + ".NS")
            info = ticker.fast_info
            price = info.get("lastPrice")
            if price:
                prices[sym] = round(price, 2)
        except Exception:
            pass
    return prices

symbols = df["Symbol"].tolist()
fresh_prices = fetch_prices(symbols)

# --------------------------------------------------
# Update cache (only overwrite if data exists)
# --------------------------------------------------
for sym in symbols:
    if sym in fresh_prices:
        st.session_state.price_cache[sym] = fresh_prices[sym]

if fresh_prices:
    st.session_state.last_updated = datetime.now()

# --------------------------------------------------
# Apply cached prices to dataframe
# --------------------------------------------------
df["CMP (₹)"] = df["Symbol"].apply(
    lambda x: st.session_state.price_cache.get(x)
)

# --------------------------------------------------
# Display
# --------------------------------------------------
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
st.markdown("---")
st.header("📌 Stock Detail View")

stock_row = df[df["Symbol"] == selected_stock].iloc[0]

st.subheader(f"{stock_row['Company']} ({selected_stock})")
st.write(f"**Sector:** {stock_row['Sector']}")
st.write(f"**CMP:** ₹{stock_row['CMP (₹)']}")

# --------------------------------------------------
# Footer
# --------------------------------------------------
if st.session_state.last_updated:
    st.caption(
        f"🟡 Prices may be delayed | Last updated: "
        f"{st.session_state.last_updated.strftime('%d %b %Y, %I:%M %p')}"
    )
else:
    st.caption("🟡 Prices loading…")
