import streamlit as st
import pandas as pd
import requests
import time
import urllib.parse

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Nifty50 AI Portfolio Advisor",
    layout="wide"
)

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Live prices | NSE public quotes | Private personal use")

# --------------------------------------------------
# Load stock list
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

# --------------------------------------------------
# NSE headers (mandatory)
# --------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/"
}

# --------------------------------------------------
# Fetch prices from NSE (ULTIMATE STABLE VERSION)
# --------------------------------------------------
@st.cache_data(ttl=300)
def fetch_nse_prices(symbols):
    cmp_list = []
    change_list = []

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=HEADERS, timeout=10)

    for symbol in symbols:
        try:
            encoded_symbol = urllib.parse.quote(symbol, safe="")
            url = (
                "https://www.nseindia.com/api/quote-equity"
                f"?symbol={encoded_symbol}&series=EQ"
            )

            response = session.get(url, headers=HEADERS, timeout=10)
            data = response.json()

            # -------- PRIMARY SOURCE --------
            price_info = data.get("priceInfo", {})
            last_price = price_info.get("lastPrice")
            change_pct = price_info.get("pChange")

            # -------- FALLBACK (CRITICAL FIX FOR TATAMOTORS) --------
            if last_price is None:
                trade_info = (
                    data.get("marketDeptOrderBook", {})
                        .get("tradeInfo", {})
                )
                last_price = trade_info.get("lastPrice")

                prev_close = price_info.get("previousClose")
                if last_price is not None and prev_close:
                    change_pct = ((last_price - prev_close) / prev_close) * 100

            cmp_list.append(last_price)
            change_list.append(
                round(change_pct, 2) if change_pct is not None else None
            )

            time.sleep(0.4)  # NSE-friendly delay

        except Exception:
            cmp_list.append(None)
            change_list.append(None)

    return cmp_list, change_list

symbols = df["Symbol"].tolist()
cmp, change = fetch_nse_prices(symbols)

df["CMP (₹)"] = cmp
df["Change %"] = change

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

st.caption("🟢 Source: NSE India (multi-field fallback) | Refresh every 5 minutes")
