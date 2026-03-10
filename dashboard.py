import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="StarGate Dashboard", layout="wide", page_icon="🌉")
st.title("🌉 StarGate Dashboard")
st.divider()

PERIOD = "day"

@st.cache_data(ttl=300)
def fetch_vtho_generated(period):
    url = f"https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-generated/{period}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

# Raw preview — helps us see the data shape
data = fetch_vtho_generated(PERIOD)
st.subheader("Raw API Response (temp)")
st.json(data)
