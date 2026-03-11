import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time
import os
from datetime import timedelta

st.set_page_config(
    page_title="VeChain StarGate Dashboard",
    layout="wide",
    page_icon="🌉",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@700,500,400&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --vc-purple:       #7266FF;
  --vc-dark:         #0C0A1F;
  --vc-light-purple: #BDB8FF;
  --vc-cool-gray:    #F1F1F4;
  --muted:           #7B789A;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] { background: var(--vc-cool-gray); }
[data-testid="stSidebar"] {
  background: var(--vc-dark) !important;
  border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label {
  color: rgba(189,184,255,0.6) !important;
  font-size: 10px !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.vc-header {
  background: var(--vc-dark);
  padding: 56px 64px 48px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  position: relative; overflow: hidden;
}
.vc-header::before {
  content: ''; position: absolute; top: -160px; right: -160px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(114,102,255,0.18) 0%, transparent 70%);
  pointer-events: none;
}
.vc-header-tag {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(114,102,255,0.18);
  border: 1px solid rgba(114,102,255,0.4);
  border-radius: 100px; padding: 6px 16px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--vc-light-purple);
  margin-bottom: 20px; font-family: 'Satoshi', sans-serif;
}
.vc-header-tag::before {
  content: ''; width: 6px; height: 6px; border-radius: 50%;
  background: var(--vc-light-purple); display: inline-block;
  animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.vc-header h1 {
  font-size: 56px; font-weight: 700; line-height: 1.05;
  letter-spacing: -0.03em; margin-bottom: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #d0ccff 55%, var(--vc-light-purple) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; font-family: 'Satoshi', sans-serif;
}
.vc-header-meta { display: flex; gap: 40px; margin-top: 36px; }
.vc-meta-item { display: flex; flex-direction: column; gap: 4px; }
.vc-meta-label {
  font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
  color: rgba(189,184,255,0.5); font-family: 'Satoshi', sans-serif;
}
.vc-meta-value {
  font-size: 14px; font-weight: 500;
  color: rgba(255,255,255,0.9); font-family: 'Inter', sans-serif;
}
.vc-kpi-row {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1px; background: rgba(12,10,31,0.08);
  border-bottom: 1px solid rgba(12,10,31,0.08);
}
.vc-kpi-card {
  background: #ffffff; padding: 36px 40px;
  position: relative; overflow: hidden;
}
.vc-kpi-card::before {
  content: ''; position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
}
.vc-kpi-card.a1::before, .vc-kpi-card.a4::before { background: var(--vc-purple); }
.vc-kpi-card.a2::before, .vc-kpi-card.a3::before { background: var(--vc-light-purple); }
.vc-kpi-label {
  font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 14px; font-family: 'Satoshi', sans-serif;
}
.vc-kpi-value {
  font-size: 40px; font-weight: 700; line-height: 1;
  letter-spacing: -0.025em; margin-bottom: 10px;
  color: var(--vc-purple); font-family: 'Satoshi', sans-serif;
}
.vc-kpi-card.a4 .vc-kpi-value { color: var(--vc-dark); }
.vc-kpi-delta {
  font-size: 13px; font-weight: 500;
  color: var(--vc-light-purple); font-family: 'Inter', sans-serif;
}
.vc-kpi-delta.up::before   { content: '↑ '; }
.vc-kpi-delta.down::before { content: '↓ '; }
.vc-section {
  padding: 56px 64px 0 64px;
  background: #ffffff;
  border-bottom: 1px solid rgba(12,10,31,0.08);
}
.vc-section-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 40px;
}
.vc-section-title {
  font-size: 26px; font-weight: 700; letter-spacing: -0.02em;
  color: var(--vc-dark); font-family: 'Satoshi', sans-serif;
}
.vc-section-badge {
  padding: 6px 14px; border-radius: 6px;
  font-size: 10px; font-weight: 600; letter-spacing: 0.09em;
  text-transform: uppercase; font-family: 'Satoshi', sans-serif;
  background: rgba(114,102,255,0.08); color: var(--vc-purple);
  border: 1px solid rgba(114,102,255,0.2);
}
[data-testid="stHorizontalBlock"] {
  gap: 24px !important;
  padding: 0 64px 56px !important;
  background: #ffffff;
}
[data-testid="stHorizontalBlock"] > div { padding: 0 !important; min-width: 0; }
[data-testid="stPlotlyChart"] {
  background: #ffffff;
  border: 1px solid rgba(12,10,31,0.08);
  border-radius: 12px;
  padding: 32px !important;
  box-shadow: 0 2px 24px rgba(114,102,255,0.07);
}
[data-testid="stPlotlyChart"] > div { margin: 0 !important; }
.vc-footer {
  padding: 36px 64px; background: var(--vc-dark);
  display: flex; align-items: center; justify-content: space-between;
}
.vc-footer-brand { font-size: 13px; color: rgba(189,184,255,0.6); font-family: 'Inter', sans-serif; }
.vc-footer-brand strong { color: #fff; font-family: 'Satoshi', sans-serif; }
.vc-live-dot {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; color: var(--vc-light-purple); font-family: 'Satoshi', sans-serif;
}
.vc-live-dot::before {
  content: ''; width: 6px; height: 6px; border-radius: 50%;
  background: var(--vc-purple); display: inline-block;
  animation: blink 2s ease-in-out infinite;
}
.vc-watermark {
  font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
  color: rgba(189,184,255,0.5); padding: 6px 14px;
  border: 1px solid rgba(114,102,255,0.3); border-radius: 100px;
  font-family: 'Satoshi', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────
FROM_TS_FULL = 1733702400  # July 2025 — for vet-staked baseline
FROM_TS      = 1764547200  # Dec 1 2025 — display start
HEADERS      = {"accept": "*/*", "user-agent": "curl/8.0.1"}
SIZE         = 150
TIMEOUT      = 30
SLEEP_S      = 0.10

# ── Fetch helpers ─────────────────────────────────────────
def _fetch_daily(url, value_col, from_ts=None):
    """Generic day-window paginator for stargate DAY endpoints."""
    if from_ts is None:
        from_ts = FROM_TS
    TO_TS = int(pd.Timestamp.utcnow().timestamp())
    session = requests.Session()
    session.headers.update(HEADERS)
    rows = []
    start_day = pd.to_datetime(from_ts, unit="s", utc=True).normalize()
    end_day   = pd.to_datetime(TO_TS,   unit="s", utc=True).normalize()
    for day_start in pd.date_range(start_day, end_day, freq="D", tz="UTC"):
        day_end     = day_start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        window_from = max(from_ts, int(day_start.timestamp()))
        window_to   = min(TO_TS,   int(day_end.timestamp()))
        if window_from > window_to:
            continue
        page = 0
        while True:
            params = {
                "from": window_from, "to": window_to,
                "page": page, "size": SIZE, "direction": "ASC"
            }
            r = session.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json().get("data", []) or []
            rows.extend(data)
            if len(data) < SIZE:
                break
            page += 1
            time.sleep(SLEEP_S)
    if not rows:
        return pd.DataFrame(columns=["blockNumber","blockTimestamp","gmtTime","date", value_col])
    df = pd.DataFrame(rows)[["blockNumber","blockTimestamp","total"]].copy()
    df["gmtTime"]   = pd.to_datetime(df["blockTimestamp"], unit="s", utc=True)
    df["date"]      = df["gmtTime"].dt.date
    df[value_col]   = pd.to_numeric(df["total"], errors="coerce") / 1e18
    df = df.drop_duplicates(subset=["blockNumber","blockTimestamp"])
    df = df.sort_values(["blockTimestamp","blockNumber"]).reset_index(drop=True)
    return df[["blockNumber","blockTimestamp","gmtTime","date", value_col]]

# ── Fetch functions ───────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_vtho_generated():
    return _fetch_daily(
        "https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-generated/DAY",
        "vtho_generated"
    )

@st.cache_data(ttl=300)
def fetch_vtho_claimed():
    df = _fetch_daily(
        "https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-claimed/DAY",
        "vtho_claimed"
    )
    return df[df["vtho_claimed"] > 0].reset_index(drop=True)

@st.cache_data(ttl=300)
def fetch_vet_staked():
    df = _fetch_daily(
        "https://indexer.mainnet.vechain.org/api/v1/stargate/vet-staked/DAY",
        "vet_staked_delta",
        from_ts=FROM_TS_FULL
    )
    df["vet_staked_cumsum"] = df["vet_staked_delta"].cumsum()
    df = df.groupby("date").agg(
        vet_staked_delta=("vet_staked_delta", "sum"),
        vet_staked_cumsum=("vet_staked_cumsum", "last")
    ).reset_index()
    dec1 = pd.to_datetime(FROM_TS, unit="s", utc=True).date()
    return df[df["date"] >= dec1].reset_index(drop=True)

@st.cache_data(ttl=300)
def fetch_vet_delegated():
    path = os.path.join(os.path.dirname(__file__), "vet-delegated 2025-2026.03.10.xlsx")
    df = pd.read_excel(path)
    df["date"] = pd.to_datetime(df["date"], origin="1899-12-30", unit="D").dt.date
    df = df.sort_values("date").reset_index(drop=True)
    return df[["date", "vet_delegated_cumsum"]]

# ── Load ──────────────────────────────────────────────────
with st.spinner("Fetching data from VeChain indexer..."):
    df     = fetch_vtho_generated()
    df_clm = fetch_vtho_claimed()
    df_stk = fetch_vet_staked()
    df_dlg = fetch_vet_delegated()

if df.empty:
    st.error("No data returned from API.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Filters")
    period   = st.selectbox("Aggregation", ["Daily", "Weekly", "Monthly"])
    min_date = df["date"].min()
    max_date = df["date"].max()
    date_range = st.date_input(
        "Date Range",
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date,
        max_value=max_date,
    )

# ── Filter ────────────────────────────────────────────────
s = date_range[0] if len(date_range) >= 1 else min_date
e = date_range[1] if len(date_range) == 2 else max_date

filtered = df[(df["date"] >= s) & (df["date"] <= e)].copy()
if filtered.empty:
    st.warning("No data for selected range.")
    st.stop()

f_clm = df_clm[(df_clm["date"] >= s) & (df_clm["date"] <= e)].copy()
f_stk = df_stk[(df_stk["date"] >= s) & (df_stk["date"] <= e)].copy()
f_dlg = df_dlg[(df_dlg["date"] >= s) & (df_dlg["date"] <= e)].copy()

# ── Aggregate ─────────────────────────────────────────────
def aggregate(df, col, how="sum"):
    df = df.copy()
    df["gmtTime"] = pd.to_datetime(df["date"] if "gmtTime" not in df.columns else df["gmtTime"])
    if period == "Weekly":
        r = df.set_index("gmtTime").resample("W")[col].agg(how).reset_index()
    elif period == "Monthly":
        r = df.set_index("gmtTime").resample("ME")[col].agg(how).reset_index()
    else:
        return df[["date", col]].copy()
    r.columns = ["date", col]
    return r

filtered["gmtTime"] = pd.to_datetime(filtered["gmtTime"])
f_clm["gmtTime"]    = pd.to_datetime(f_clm["gmtTime"])
f_stk["gmtTime"]    = pd.to_datetime(f_stk["date"])
f_dlg["gmtTime"]    = pd.to_datetime(f_dlg["date"])

chart_df  = aggregate(filtered, "vtho_generated", "sum")
chart_clm = aggregate(f_clm,    "vtho_claimed",   "sum")

if period in ["Weekly", "Monthly"]:
    freq = "W" if period == "Weekly" else "ME"
    chart_stk = f_stk.set_index("gmtTime").resample(freq).agg(
        vet_staked_delta=("vet_staked_delta", "sum"),
        vet_staked_cumsum=("vet_staked_cumsum", "last")
    ).reset_index().rename(columns={"gmtTime": "date"})
    chart_dlg = f_dlg.set_index("gmtTime").resample(freq)["vet_delegated_cumsum"].last().reset_index()
    chart_dlg.columns = ["date", "vet_delegated_cumsum"]
else:
    chart_stk = f_stk[["date","vet_staked_delta","vet_staked_cumsum"]].copy()
    chart_dlg = f_dlg[["date","vet_delegated_cumsum"]].copy()

# ── KPIs ──────────────────────────────────────────────────
vtho_gen_total = filtered["vtho_generated"].sum()
vtho_clm_total = f_clm["vtho_claimed"].sum() if not f_clm.empty else 0
vet_stk_latest = f_stk["vet_staked_cumsum"].iloc[-1] if not f_stk.empty else 0

latest     = filtered["vtho_generated"].iloc[-1]
prev       = filtered["vtho_generated"].iloc[-2] if len(filtered) > 1 else latest
change     = ((latest - prev) / prev * 100) if prev else 0
days_count = (pd.to_datetime(e) - pd.to_datetime(s)).days + 1

def fmt(v):
    if v >= 1e9: return f"{v/1e9:.2f}B"
    if v >= 1e6: return f"{v/1e6:.1f}M"
    return f"{v:,.0f}"

direction    = "up" if change >= 0 else "down"
change_abs   = abs(change)
last_updated = pd.Timestamp.utcnow().strftime("%-d %b %Y, %H:%M UTC")

# ── HEADER ────────────────────────────────────────────────
st.markdown(f"""
<div class="vc-header">
  <div class="vc-header-tag">Live · Post-Hayabusa Analysis</div>
  <h1>StarGate by VeChain<br>Performance Report</h1>
  <div class="vc-header-meta">
    <div class="vc-meta-item">
      <span class="vc-meta-label">Hard Fork</span>
      <span class="vc-meta-value">Hayabusa</span>
    </div>
    <div class="vc-meta-item">
      <span class="vc-meta-label">Key Change</span>
      <span class="vc-meta-value">Fixed → Proportional VTHO Issuance</span>
    </div>
    <div class="vc-meta-item">
      <span class="vc-meta-label">Data Source</span>
      <span class="vc-meta-value">VeChain StarGate Indexer API</span>
    </div>
    <div class="vc-meta-item">
      <span class="vc-meta-label">Last Updated</span>
      <span class="vc-meta-value">{last_updated}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI ROW ───────────────────────────────────────────────
st.markdown(f"""
<div class="vc-kpi-row">
  <div class="vc-kpi-card a1">
    <div class="vc-kpi-label">Total VTHO Generated</div>
    <div class="vc-kpi-value">{fmt(vtho_gen_total)}</div>
    <div class="vc-kpi-delta {direction}">{change_abs:.2f}% vs previous day</div>
  </div>
  <div class="vc-kpi-card a2">
    <div class="vc-kpi-label">Total VTHO Claimed</div>
    <div class="vc-kpi-value">{fmt(vtho_clm_total)}</div>
    <div class="vc-kpi-delta up">over selected range</div>
  </div>
  <div class="vc-kpi-card a3">
    <div class="vc-kpi-label">Total VET Staked</div>
    <div class="vc-kpi-value">{fmt(vet_stk_latest)}</div>
    <div class="vc-kpi-delta up">cumulative</div>
  </div>
  <div class="vc-kpi-card a4">
    <div class="vc-kpi-label">Days Tracked</div>
    <div class="vc-kpi-value">{days_count}</div>
    <div class="vc-kpi-delta">in selected range</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SECTION 1: VTHO Emission ──────────────────────────────
st.markdown("""
<div class="vc-section">
  <div class="vc-section-header">
    <div class="vc-section-title">VTHO Emission Dynamics</div>
    <div class="vc-section-badge">Key Mechanism Change</div>
  </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=chart_df["date"], y=chart_df["vtho_generated"],
        fill="tozeroy", fillcolor="rgba(114,102,255,0.08)",
        line=dict(color="#7266FF", width=2.5),
        hovertemplate="%{x}<br><b>%{y:,.0f} VTHO</b><extra></extra>"
    ))
    fig1.update_layout(
        title=dict(
            text="VTHO Generated Over Time",
            subtitle=dict(text="Emission rising proportionally as more VET gets staked", font=dict(size=12, color="#7B789A")),
            font=dict(family="Satoshi", size=14, color="#0C0A1F")
        ),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=40, r=24, t=64, b=40),
        hovermode="x unified", showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B789A", size=11)),
        yaxis=dict(gridcolor="rgba(12,10,31,0.05)", tickfont=dict(color="#7B789A", size=11), tickformat=".2s"),
        height=320
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=chart_df["date"], y=chart_df["vtho_generated"],
        marker=dict(color="rgba(114,102,255,0.55)", line=dict(width=0)),
        hovertemplate="%{x}<br><b>%{y:,.0f} VTHO</b><extra></extra>"
    ))
    fig2.update_layout(
        title=dict(
            text="Daily VTHO Breakdown",
            font=dict(family="Satoshi", size=14, color="#0C0A1F")
        ),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=40, r=24, t=48, b=40),
        hovermode="x unified", showlegend=False, bargap=0.2,
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B789A", size=11)),
        yaxis=dict(gridcolor="rgba(12,10,31,0.05)", tickfont=dict(color="#7B789A", size=11), tickformat=".2s"),
        height=320
    )
    st.plotly_chart(fig2, use_container_width=True)

with st.expander("📄 Raw Data — VTHO Generated"):
    st.dataframe(
        filtered[["date","vtho_generated","blockNumber"]]
        .sort_values("date", ascending=False),
        use_container_width=True
    )

# ── SECTION 2: VTHO Claimed ───────────────────────────────
st.markdown("""
<div class="vc-section">
  <div class="vc-section-header">
    <div class="vc-section-title">VTHO Claimed</div>
    <div class="vc-section-badge">Staker Rewards</div>
  </div>
</div>
""", unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=chart_clm["date"], y=chart_clm["vtho_claimed"],
        fill="tozeroy", fillcolor="rgba(189,184,255,0.10)",
        line=dict(color="#BDB8FF", width=2.5),
        hovertemplate="%{x}<br><b>%{y:,.0f} VTHO</b><extra></extra>"
    ))
    fig3.update_layout(
        title=dict(
            text="VTHO Claimed Over Time",
            subtitle=dict(text="Rewards claimed by stakers over time", font=dict(size=12, color="#7B789A")),
            font=dict(family="Satoshi", size=14, color="#0C0A1F")
        ),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=40, r=24, t=64, b=40),
        hovermode="x unified", showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B789A", size=11)),
        yaxis=dict(gridcolor="rgba(12,10,31,0.05)", tickfont=dict(color="#7B789A", size=11), tickformat=".2s"),
        height=320
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=chart_clm["date"], y=chart_clm["vtho_claimed"],
        marker=dict(color="rgba(189,184,255,0.7)", line=dict(width=0)),
        hovertemplate="%{x}<br><b>%{y:,.0f} VTHO</b><extra></extra>"
    ))
    fig4.update_layout(
        title=dict(
            text="Daily VTHO Claimed",
            subtitle=dict(text="Per-day claiming activity", font=dict(size=12, color="#7B789A")),
            font=dict(family="Satoshi", size=14, color="#0C0A1F")
        ),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=40, r=24, t=64, b=40),
        hovermode="x unified", showlegend=False, bargap=0.2,
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B789A", size=11)),
        yaxis=dict(gridcolor="rgba(12,10,31,0.05)", tickfont=dict(color="#7B789A", size=11), tickformat=".2s"),
        height=320
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Full width: Generated vs Claimed ─────────────────────
col5, _ = st.columns([1, 0.001])
with col5:
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=chart_df["date"], y=chart_df["vtho_generated"],
        fill="tozeroy", fillcolor="rgba(114,102,255,0.08)",
        line=dict(color="#7266FF", width=2.5),
        name="Generated",
        hovertemplate="%{x}<br><b>Generated: %{y:,.0f} VTHO</b><extra></extra>"
    ))
    fig5.add_trace(go.Scatter(
        x=chart_clm["date"], y=chart_clm["vtho_claimed"],
        fill="tozeroy", fillcolor="rgba(189,184,255,0.10)",
        line=dict(color="#BDB8FF", width=2.5),
        name="Claimed",
        hovertemplate="%{x}<br><b>Claimed: %{y:,.0f} VTHO</b><extra></extra>"
    ))
    fig5.update_layout(
        title=dict(
            text="VTHO Generated vs. Claimed",
            subtitle=dict(text="Generated supply vs. actual claiming activity", font=dict(size=12, color="#7B789A")),
            font=dict(family="Satoshi", size=14, color="#0C0A1F")
        ),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=40, r=24, t=64, b=40),
        hovermode="x unified", showlegend=True,
        legend=dict(font=dict(color="#7B789A", size=11), bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B789A", size=11)),
        yaxis=dict(gridcolor="rgba(12,10,31,0.05)", tickfont=dict(color="#7B789A", size=11), tickformat=".2s"),
        height=320
    )
    st.plotly_chart(fig5, use_container_width=True)

# ── SECTION 3: VET Staked ─────────────────────────────────
st.markdown("""
<div class="vc-section">
  <div class="vc-section-header">
    <div class="vc-section-title">VET Staking Growth</div>
    <div class="vc-section-badge">↑ Strong Growth Trend</div>
  </div>
</div>
""", unsafe_allow_html=True)

col6, _ = st.columns([1, 0.001])
with col6:
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=chart_stk["date"], y=chart_stk["vet_staked_cumsum"],
        fill="tozeroy", fillcolor="rgba(114,102,255,0.08)",
        line=dict(color="#7266FF", width=2.5),
        hovertemplate="%{x}<br><b>%{y:,.0f} VET</b><extra></extra>"
    ))
    fig6.update_layout(
        title=dict(
            text="Total VET Staked Over Time",
            subtitle=dict(text="Cumulative VET locked in StarGate staking", font=dict(size=12, color="#7B789A")),
            font=dict(family="Satoshi", size=14, color="#0C0A1F")
        ),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=40, r=24, t=64, b=40),
        hovermode="x unified", showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B789A", size=11)),
        yaxis=dict(gridcolor="rgba(12,10,31,0.05)", tickfont=dict(color="#7B789A", size=11), tickformat=".2s"),
        height=320
    )
    st.plotly_chart(fig6, use_container_width=True)

# ── SECTION 4: VET Delegated ─────────────────────────────
st.markdown("""
<div class="vc-section">
  <div class="vc-section-header">
    <div class="vc-section-title">VET Delegation Growth</div>
    <div class="vc-section-badge">↑ Growing Participation</div>
  </div>
</div>
""", unsafe_allow_html=True)

col7, _ = st.columns([1, 0.001])
with col7:
    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=chart_dlg["date"], y=chart_dlg["vet_delegated_cumsum"],
        fill="tozeroy", fillcolor="rgba(114,102,255,0.08)",
        line=dict(color="#7266FF", width=2.5),
        hovertemplate="%{x}<br><b>%{y:,.0f} VET</b><extra></extra>"
    ))
    fig7.update_layout(
        title=dict(
            text="Total VET Delegated Over Time",
            subtitle=dict(text="Cumulative VET delegated in StarGate", font=dict(size=12, color="#7B789A")),
            font=dict(family="Satoshi", size=14, color="#0C0A1F")
        ),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=40, r=24, t=64, b=40),
        hovermode="x unified", showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B789A", size=11)),
        yaxis=dict(gridcolor="rgba(12,10,31,0.05)", tickfont=dict(color="#7B789A", size=11), tickformat=".2s"),
        height=320
    )
    st.plotly_chart(fig7, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────
st.markdown(f"""
<div class="vc-footer">
  <div class="vc-footer-brand"><strong>VeChain StarGate</strong> — Post-Hayabusa Report</div>
  <div style="display:flex;align-items:center;gap:16px;">
    <div class="vc-live-dot">Live Data</div>
    <div class="vc-watermark">VeWorld Indexer API</div>
  </div>
</div>
""", unsafe_allow_html=True)
