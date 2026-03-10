import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="StarGate Dashboard", layout="wide", page_icon="🌉")
st.title("🌉 StarGate Dashboard")
st.caption("VeChain on-chain analytics")
st.divider()

# ── Fetch Data ───────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_vtho_generated(period="day", max_pages=5):
    all_data = []
    url = f"https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-generated/{period}"
    
    page = 0
    while page < max_pages:
        params = {"limit": 30, "offset": page * 30}
        r = requests.get(url, params=params)
        r.raise_for_status()
        result = r.json()
        all_data.extend(result["data"])
        
        if not result["pagination"]["hasNext"]:
            break
        page += 1

    df = pd.DataFrame(all_data)
    df["date"] = pd.to_datetime(df["blockTimestamp"], unit="s")
    df["vtho"] = df["total"].astype(float) / 1e18  # convert to readable VTHO
    df = df.sort_values("date")
    return df

# ── Period selector ──────────────────────────────────────
period = st.selectbox("Time period", ["day", "week", "month"], index=0)
df = fetch_vtho_generated(period)

# ── KPI Metrics ──────────────────────────────────────────
latest = df["vtho"].iloc[-1]
prev = df["vtho"].iloc[-2]
change = ((latest - prev) / prev) * 100
total = df["vtho"].sum()
avg = df["vtho"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Latest VTHO Generated", f"{latest:,.0f}", f"{change:.2f}%")
col2.metric("Total VTHO Generated", f"{total:,.0f}")
col3.metric(f"Avg per {period.capitalize()}", f"{avg:,.0f}")

st.divider()

# ── Area Chart ───────────────────────────────────────────
st.subheader("📈 VTHO Generated Over Time")
fig = px.area(
    df, x="date", y="vtho",
    labels={"vtho": "VTHO Generated", "date": "Date"},
    color_discrete_sequence=["#7C3AED"]
)
fig.update_layout(hovermode="x unified", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ── Bar Chart ────────────────────────────────────────────
st.subheader("📊 VTHO by Day")
fig2 = px.bar(
    df.tail(30), x="date", y="vtho",
    labels={"vtho": "VTHO Generated", "date": "Date"},
    color_discrete_sequence=["#7C3AED"]
)
st.plotly_chart(fig2, use_container_width=True)

# ── Data Table ───────────────────────────────────────────
with st.expander("📄 Raw Data"):
    st.dataframe(
        df[["date", "vtho", "blockNumber"]].sort_values("date", ascending=False),
        use_container_width=True
    )
