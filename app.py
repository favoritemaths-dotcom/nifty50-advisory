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
# Yahoo Finance symbol overrides (IMPORTANT)
# --------------------------------------------------
YAHOO_SYMBOL_MAP = {
    "M&M": "MM",                # Mahindra & Mahindra
    "RELIANCE": "RIL",          # Reliance Industries
    "TATAMOTORS": "TATAMOTORS", # Tata Motors
    "BAJAJ-AUTO": "BAJAJ-AUTO",
    "LTIM": "LTIM",
    "SBICARD": "SBICARD"
}

# --------------------------------------------------
# Load Nifty 50 stock list
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
# Fetch live prices from Yahoo Finance
# --------------------------------------------------
@st.cache_data(ttl=300)  # refresh every 5 minutes
def fetch_prices(symbols):
    cmp_list = []
    change_list = []

    for symbol in symbols:
        yahoo_symbol = YAHOO_SYMBOL_MAP.get(symbol, symbol)
        ticker = yf.Ticker(yahoo_symbol + ".NS")

        try:
            data = ticker.history(period="2d")
            if data.empty:
                cmp_list.append(None)
                change_list.append(None)
            else:
                close_price = round(data["Close"].iloc[-1], 2)
                open_price = round(data["Open"].iloc[-1], 2)
                change_pct = round(
                    ((close_price - open_price) / open_price) * 100, 2
                )

                cmp_list.append(close_price)
                change_list.append(change_pct)

        except Exception:
            cmp_list.append(None)
            change_list.append(None)

    return cmp_list, change_list

symbols = df["Symbol"].tolist()
cmp, change_pct = fetch_prices(symbols)

df["CMP (₹)"] = cmp
df["Change %"] = change_pct

# --------------------------------------------------
# Styling for % change
# --------------------------------------------------
def color_change(val):
    if pd.isna(val):
        return ""
    elif val > 0:
        return "color: green"
    else:
        return "color: red"

# --------------------------------------------------
# Display table
# --------------------------------------------------
st.subheader(f"Showing {len(df)} Nifty 50 Stocks")

st.dataframe(
    df.style.applymap(color_change, subset=["Change %"]),
    use_container_width=True,
    hide_index=True
)

st.caption("🟢 Data source: Yahoo Finance | Refreshes every 5 minutes")
