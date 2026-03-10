import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta, date

st.set_page_config(page_title="StarGate Dashboard", layout="wide", page_icon="🌉")
st.title("🌉 StarGate Dashboard")
st.caption("VeChain on-chain analytics")
st.divider()

GENESIS_DATE = date(2025, 12, 1)

@st.cache_data(ttl=300)
def fetch_vtho_generated(period="day"):
    all_data = []
    url = f"https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-generated/{period}"

    offset = 0
    while True:
        params = {"limit": 100, "offset": offset}
        r = requests.get(url, params=params)
        
        # Debug: show what went wrong
        if not r.ok:
            st.error(f"API error {r.status_code} at offset {offset}: {r.text}")
            break

        result = r.json()
        all_data.extend(result["data"])

        if not result["pagination"]["hasNext"]:
            break
        offset += 100

    if not all_data:
        return pd.DataFrame(columns=["date", "vtho", "blockNumber"])

    df = pd.DataFrame(all_data)
    df["date"] = pd.to_datetime(df["blockTimestamp"], unit="s").dt.date
    df["vtho"] = df["total"].astype(float) / 1e18
    df = df[df["date"] >= GENESIS_DATE]
    df = df.sort_values("date").drop_duplicates(subset="date")
    return df
