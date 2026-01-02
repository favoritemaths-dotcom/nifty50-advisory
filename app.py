import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(
    page_title="Nifty50 AI Portfolio Advisor",
    layout="wide"
)

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Live prices | Private decision-support tool")

# ---------- Load Nifty 50 list ----------
@st.cache_data
def load_nifty50():
    return pd.read_csv("data/nifty50_list.csv")

df = load_nifty50()

# ---------- Sidebar filter ----------
st.sidebar.header("Filters")

sector = st.sidebar.selectbox(
    "Select Sector",
    ["All"] + sorted(df["Sector"].unique().tolist())
)

if sector != "All":
    df = df[df["Sector"] == sector]

# ---------- Fetch live prices ----------
@st.cache_data(ttl=300)  # refresh every 5 minutes
def fetch_prices(symbols):
    prices = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol + ".NS")
            data = stock.history(period="1d")
            if not data.empty:
                close = round(data["Close"].iloc[-1], 2)
                open_price = round(data["Open"].iloc[-1], 2)
                change_pct = round(((close - open_price) / open_price) * 100, 2)
            else:
                close, change_pct = None, None
        except:
            close, change_pct = None, None

        prices.append((close, change_pct))

    return prices

symbols = df["Symbol"].tolist()
price_data = fetch_prices(symbols)

df["CMP (₹)"] = [p[0] for p in price_data]
df["Change %"] = [p[1] for p in price_data]

# ---------- Styling ----------
def color_change(val):
    if pd.isna(val):
        return ""
    return "color: green" if val > 0 else "color: red"

st.subheader(f"Showing {len(df)} Nifty 50 Stocks")

st.dataframe(
    df.style.applymap(color_change, subset=["Change %"]),
    use_container_width=True,
    hide_index=True
)

st.caption("🟢 Prices from Yahoo Finance | Refreshes every 5 minutes")
