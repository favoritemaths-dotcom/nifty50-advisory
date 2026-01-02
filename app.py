import streamlit as st
import pandas as pd
import yfinance as yf

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Nifty50 AI Portfolio Advisor",
    layout="wide"
)

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Live prices | Private decision-support tool (India)")

# --------------------------------------------------
# Yahoo Finance symbol overrides (NSE → Yahoo)
# --------------------------------------------------
YAHOO_SYMBOL_MAP = {
    "M&M": "MM",
    "RELIANCE": "RIL",
    "TATAMOTORS": "TATAMOTORS",
    "BAJAJ-AUTO": "BAJAJ-AUTO",
    "LTIM": "LTIM",
    "SBICARD": "SBICARD"
}

# --------------------------------------------------
# Load Nifty 50 list
# --------------------------------------------------
@st.cache_data
def load_nifty50():
    return pd.read_csv("data/nifty50_list.csv")

df = load_nifty50()

# --------------------------------------------------
# Sidebar – Sector Filter
# --------------------------------------------------
st.sidebar.header("Filters")

selected_sector = st.sidebar.selectbox(
    "Select Sector",
    ["All"] + sorted(df["Sector"].unique().tolist())
)

if selected_sector != "All":
    df = df[df["Sector"] == selected_sector]

# --------------------------------------------------
# Fetch live prices (ROBUST METHOD)
# --------------------------------------------------
@st.cache_data(ttl=300)
def fetch_prices(symbols):
    cmp_list = []
    change_list = []

    for symbol in symbols:
        yahoo_symbol = YAHOO_SYMBOL_MAP.get(symbol, symbol)
        ticker = yf.Ticker(yahoo_symbol + ".NS")

        close_price = None
        change_pct = None

        # --- Method 1: OHLC history (preferred) ---
        try:
            hist = ticker.history(period="2d")
            if not hist.empty:
                close_price = round(hist["Close"].iloc[-1], 2)
                open_price = round(hist["Open"].iloc[-1], 2)
                change_pct = round(
                    ((close_price - open_price) / open_price) * 100, 2
                )
        except:
            pass

        # --- Method 2: fast_info fallback (CRITICAL FIX) ---
        if close_price is None:
            try:
                fast = ticker.fast_info
                close_price = round(fast.get("lastPrice"), 2)
                prev_close = fast.get("previousClose")

                if close_price and prev_close:
                    change_pct = round(
                        ((close_price - prev_close) / prev_close) * 100, 2
                    )
            except:
                pass

        cmp_list.append(close_price)
        change_list.append(change_pct)

    return cmp_list, change_list

symbols = df["Symbol"].tolist()
cmp, change_pct = fetch_prices(symbols)

df["CMP (₹)"] = cmp
df["Change %"] = change_pct

# --------------------------------------------------
# Styling
# --------------------------------------------------
def color_change(val):
    if pd.isna(val):
        return ""
    return "color: green" if val > 0 else "color: red"

# --------------------------------------------------
# Display table
# --------------------------------------------------
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")

st.dataframe(
    df.style.applymap(color_change, subset=["Change %"]),
    use_container_width=True,
    hide_index=True
)

st.caption("🟢 Data source: Yahoo Finance (with fallback) | Refreshes every 5 minutes")
