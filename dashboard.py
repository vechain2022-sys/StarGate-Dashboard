import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta, date

st.set_page_config(page_title="StarGate Dashboard", layout="wide", page_icon="🌉")
st.title("🌉 StarGate Dashboard")
st.caption("VeChain on-chain analytics")
st.divider()

# StarGate launch date
GENESIS_DATE = date(2025, 12, 1)

# ── Fetch Data ───────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_vtho_generated(period="day"):
    all_data = []
    url = f"https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-generated/{period}"

    offset = 0
    with st.spinner("Fetching data..."):
        while True:
            params = {"limit": 100, "offset": offset}
            r = requests.get(url, params=params)
            r.raise_for_status()
            result = r.json()
            all_data.extend(result["data"])

            if not result["pagination"]["hasNext"]:
                break
            offset += 100

    df = pd.DataFrame(all_data)
    df["date"] = pd.to_datetime(df["blockTimestamp"], unit="s").dt.date
    df["vtho"] = df["total"].astype(float) / 1e18
    df = df[df["date"] >= GENESIS_DATE]  # filter to StarGate launch
    df = df.sort_values("date").drop_duplicates(subset="date")
    return df

# ── Sidebar Controls ─────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filters")

    period = st.selectbox("Time period", ["day", "week", "month"], index=0)
    df = fetch_vtho_generated(period)

    max_date = df["date"].max()

    date_range = st.date_input(
        "Date range",
        value=(max_date - timedelta(days=30), max_date),
        min_value=GENESIS_DATE,
        max_value=max_date,
    )

# ── Filter by date range ─────────────────────────────────
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
else:
    filtered = df

# ── KPI Metrics ──────────────────────────────────────────
latest = filtered["vtho"].iloc[-1]
prev = filtered["vtho"].iloc[-2] if len(filtered) > 1 else latest
change = ((latest - prev) / prev) * 100
total = filtered["vtho"].sum()
avg = filtered["vtho"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Latest VTHO Generated", f"{latest:,.0f}", f"{change:.2f}%")
col2.metric("Total VTHO Generated", f"{total:,.0f}")
col3.metric(f"Avg per {period.capitalize()}", f"{avg:,.0f}")

st.divider()

# ── Area Chart ───────────────────────────────────────────
st.subheader("📈 VTHO Generated Over Time")
fig = px.area(
    filtered, x="date", y="vtho",
    labels={"vtho": "VTHO Generated", "date": "Date"},
    color_discrete_sequence=["#7C3AED"]
)
fig.update_layout(hovermode="x unified", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ── Bar Chart ────────────────────────────────────────────
st.subheader("📊 Daily VTHO Breakdown")
fig2 = px.bar(
    filtered, x="date", y="vtho",
    labels={"vtho": "VTHO Generated", "date": "Date"},
    color_discrete_sequence=["#7C3AED"]
)
st.plotly_chart(fig2, use_container_width=True)

# ── Data Table ───────────────────────────────────────────
with st.expander("📄 Raw Data"):
    st.dataframe(
        filtered[["date", "vtho", "blockNumber"]].sort_values("date", ascending=False),
        use_container_width=True
    )
