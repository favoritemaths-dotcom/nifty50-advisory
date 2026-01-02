import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Nifty50 AI Portfolio Advisor",
    layout="wide"
)

st.title("📊 Nifty 50 – AI Portfolio Advisory")
st.caption("Private decision-support tool | Indian Equity Markets")

@st.cache_data
def load_nifty50():
    return pd.read_csv("data/nifty50_list.csv")

df = load_nifty50()

st.sidebar.header("Filters")

selected_sector = st.sidebar.selectbox(
    "Select Sector",
    ["All"] + sorted(df["Sector"].unique().tolist())
)

if selected_sector != "All":
    df = df[df["Sector"] == selected_sector]

st.subheader(f"Showing {len(df)} Nifty 50 Stocks")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
