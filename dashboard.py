import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
from datetime import timedelta, date

st.set_page_config(page_title="StarGate Dashboard", layout="wide", page_icon="🌉")
st.title("🌉 StarGate Dashboard")
st.caption("VeChain on-chain analytics")
st.divider()

# ── Config ───────────────────────────────────────────────
FROM_TS = 1764547200
HEADERS = {"accept": "*/*", "user-agent": "curl/8.0.1"}
SIZE = 150
TIMEOUT = 30
SLEEP_S = 0.10

# ── Fetch ────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_vtho_generated():
    url = "https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-generated/DAY"
    TO_TS = int(pd.Timestamp.utcnow().timestamp())

    session = requests.Session()
    session.headers.update(HEADERS)

    rows = []
    start_day = pd.to_datetime(FROM_TS, unit="s", utc=True).normalize()
    end_day   = pd.to_datetime(TO_TS,   unit="s", utc=True).normalize()

    for day_start in pd.date_range(start_day, end_day, freq="D", tz="UTC"):
        day_end    = day_start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        window_from = max(FROM_TS, int(day_start.timestamp()))
        window_to   = min(TO_TS,   int(day_end.timestamp()))
        if window_from > window_to:
            continue

        page = 0
        while True:
            params = {
                "from": window_from,
                "to":   window_to,
                "page": page,
                "size": SIZE,
                "direction": "ASC",
            }
            r = session.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            payload = r.json()
            data = payload.get("data", []) or []
            rows.extend(data)
            if len(data) < SIZE:
                break
            page += 1
            time.sleep(SLEEP_S)

    if not rows:
        return pd.DataFrame(columns=["blockNumber", "blockTimestamp", "gmtTime", "vtho_generated"])

    df = pd.DataFrame(rows)[["blockNumber", "blockTimestamp", "total"]].copy()
    df["gmtTime"] = pd.to_datetime(df["blockTimestamp"], unit="s", utc=True)
    df["date"]    = df["gmtTime"].dt.date
    df["vtho_generated"] = pd.to_numeric(df["total"], errors="coerce") / 1e18
    df = df.drop_duplicates(subset=["blockNumber", "blockTimestamp"])
    df = df.sort_values(["blockTimestamp", "blockNumber"]).reset_index(drop=True)
    df = df[["blockNumber", "blockTimestamp", "gmtTime", "date", "vtho_generated"]]
    return df

# ── Load ─────────────────────────────────────────────────
with st.spinner("Fetching VTHO data..."):
    df, error = (lambda r: (r, None) if isinstance(r, pd.DataFrame) else (None, r))(
        fetch_vtho_generated()
    )

if df is None or df.empty:
    st.warning("No data returned from API.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filters")
    min_date = df["date"].min()
    max_date = df["date"].max()
    date_range = st.date_input(
        "Date range",
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date,
        max_value=max_date,
    )

# ── Filter ────────────────────────────────────────────────
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()
else:
    filtered = df.copy()

# ── KPIs ──────────────────────────────────────────────────
latest = filtered["vtho_generated"].iloc[-1]
prev   = filtered["vtho_generated"].iloc[-2] if len(filtered) > 1 else latest
change = ((latest - prev) / prev) * 100 if prev else 0
total  = filtered["vtho_generated"].sum()
avg    = filtered["vtho_generated"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Latest VTHO Generated", f"{latest:,.0f}", f"{change:.2f}%")
col2.metric("Total VTHO Generated",  f"{total:,.0f}")
col3.metric("Daily Average",         f"{avg:,.0f}")

st.divider()

# ── Area Chart ────────────────────────────────────────────
st.subheader("📈 VTHO Generated Over Time")
fig1 = px.area(
    filtered, x="date", y="vtho_generated",
    labels={"vtho_generated": "VTHO Generated", "date": "Date"},
    color_discrete_sequence=["#7C3AED"]
)
fig1.update_layout(hovermode="x unified", showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

# ── Bar Chart ─────────────────────────────────────────────
st.subheader("📊 Daily VTHO Breakdown")
fig2 = px.bar(
    filtered, x="date", y="vtho_generated",
    labels={"vtho_generated": "VTHO Generated", "date": "Date"},
    color_discrete_sequence=["#7C3AED"]
)
fig2.update_layout(hovermode="x unified")
st.plotly_chart(fig2, use_container_width=True)

# ── Table ─────────────────────────────────────────────────
with st.expander("📄 Raw Data"):
    st.dataframe(
        filtered[["date", "vtho_generated", "blockNumber"]]
        .sort_values("date", ascending=False),
        use_container_width=True
    )
