import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time
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

/* Header */
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

/* KPI Row */
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

/* Section */
.vc-section {
  padding: 56px 64px 0 64px;
  background: #ffffff;
  border-bottom: 1px solid rgba(12,10,31,0.08);
}
.vc-section.gray { background: var(--vc-cool-gray); }
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
.vc-section-badge.light {
  background: rgba(189,184,255,0.15); color: var(--vc-purple);
  border: 1px solid rgba(189,184,255,0.3);
}

/* Streamlit column + chart overrides */
[data-testid="stHorizontalBlock"] {
  gap: 24px !important;
  padding: 0 64px 56px !important;
  background: #ffffff;
}
[data-testid="stHorizontalBlock"].gray {
  background: var(--vc-cool-gray) !important;
}
[data-testid="stHorizontalBlock"] > div {
  padding: 0 !important;
  min-width: 0;
}
[data-testid="stPlotlyChart"] {
  background: #ffffff;
  border: 1px solid rgba(12,10,31,0.08);
  border-radius: 12px;
  padding: 32px !important;
  box-shadow: 0 2px 24px rgba(114,102,255,0.07);
}
[data-testid="stPlotlyChart"] > div { margin: 0 !important; }

/* Footer */
.vc-footer {
  padding: 36px 64px; background: var(--vc-dark);
  display: flex; align-items: center; justify-content: space-between;
}
.vc-footer-brand {
  font-size: 13px; color: rgba(189,184,255,0.6); font-family: 'Inter', sans-serif;
}
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
FROM_TS = 1764547200
HEADERS = {"accept": "*/*", "user-agent": "curl/8.0.1"}
SIZE    = 150
TIMEOUT = 30
SLEEP_S = 0.10

# ── Generic fetch ─────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_endpoint(path: str, value_col: str):
    url   = f"https://indexer.mainnet.vechain.org/api/v1/stargate/{path}"
    TO_TS = int(pd.Timestamp.utcnow().timestamp())
    session = requests.Session()
    session.headers.update(HEADERS)
    rows = []
    start_day = pd.to_datetime(FROM_TS, unit="s", utc=True).normalize()
    end_day   = pd.to_datetime(TO_TS,   unit="s", utc=True).normalize()
    for day_start in pd.date_range(start_day, end_day, freq="D", tz="UTC"):
        day_end     = day_start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        window_from = max(FROM_TS, int(day_start.timestamp()))
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
    df["gmtTime"]    = pd.to_datetime(df["blockTimestamp"], unit="s", utc=True)
    df["date"]       = df["gmtTime"].dt.date
    df[value_col]    = pd.to_numeric(df["total"], errors="coerce") / 1e18
    df = df.drop_duplicates(subset=["blockNumber","blockTimestamp"])
    df = df.sort_values(["blockTimestamp","blockNumber"]).reset_index(drop=True)
    return df[["blockNumber","blockTimestamp","gmtTime","date", value_col]]

# ── Load all endpoints ────────────────────────────────────
with st.spinner("Fetching data from VeChain indexer..."):
    df_vtho_gen  = fetch_endpoint("vtho-generated/DAY", "vtho_generated")
    df_vtho_clm  = fetch_endpoint("vtho-claimed/DAY",   "vtho_claimed")
    df_vet_stk   = fetch_endpoint("vet-staked/DAY",     "vet_staked")
    df_vet_dlg   = fetch_endpoint("vet-delegated/DAY",  "vet_delegated")

if df_vtho_gen.empty:
    st.error("No data returned from API.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Filters")
    period   = st.selectbox("Aggregation", ["Daily", "Weekly", "Monthly"])
    min_date = df_vtho_gen["date"].min()
    max_date = df_vtho_gen["date"].max()
    date_range = st.date_input(
        "Date Range",
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date,
        max_value=max_date,
    )

# ── Filter — always define s, e ───────────────────────────
s = date_range[0] if len(date_range) >= 1 else min_date
e = date_range[1] if len(date_range) == 2 else max_date

def filter_df(df, col):
    out = df[(df["date"] >= s) & (df["date"] <= e)].copy()
    out["gmtTime"] = pd.to_datetime(out["gmtTime"])
    return out

def aggregate(df, col):
    if period == "Weekly":
        r = df.set_index("gmtTime").resample("W")[col].sum().reset_index()
    elif period == "Monthly":
        r = df.set_index("gmtTime").resample("ME")[col].sum().reset_index()
    else:
        return df[["date", col]].copy()
    r.columns = ["date", col]
    return r

f_gen = filter_df(df_vtho_gen, "vtho_generated")
f_clm = filter_df(df_vtho_clm, "vtho_claimed")
f_stk = filter_df(df_vet_stk,  "vet_staked")
f_dlg = filter_df(df_vet_dlg,  "vet_delegated")

c_gen = aggregate(f_gen, "vtho_generated")
c_clm = aggregate(f_clm, "vtho_claimed")
c_stk = aggregate(f_stk, "vet_staked")
c_dlg = aggregate(f_dlg, "vet_delegated")

# ── KPI helpers ───────────────────────────────────────────
def fmt(v):
    if v >= 1e9: return f"{v/1e9:.2f}B"
    if v >= 1e6: return f"{v/1e6:.1f}M"
    return f"{v:,.0f}"

def kpi_delta(df, col):
    if len(df) < 2: return 0, "up"
    latest, prev = df[col].iloc[-1], df[col].iloc[-2]
    chg = ((latest - prev) / prev * 100) if prev else 0
    return abs(chg), "up" if chg >= 0 else "down"

days_count   = (pd.to_datetime(e) - pd.to_datetime(s)).days + 1
last_updated = pd.Timestamp.utcnow().strftime("%-d %b %Y, %H:%M UTC")

vtho_gen_total = f_gen["vtho_generated"].sum()
vtho_clm_total = f_clm["vtho_claimed"].sum()
vet_stk_latest = f_stk["vet_staked"].iloc[-1] if not f_stk.empty else 0
vet_dlg_latest = f_dlg["vet_delegated"].iloc[-1] if not f_dlg.empty else 0
dlg_pct        = (vet_dlg_latest / vet_stk_latest * 100) if vet_stk_latest else 0

gen_chg, gen_dir = kpi_delta(f_gen, "vtho_generated")
clm_chg, clm_dir = kpi_delta(f_clm, "vtho_claimed")
stk_chg, stk_dir = kpi_delta(f_stk, "vet_staked")
dlg_chg, dlg_dir = kpi_delta(f_dlg, "vet_delegated")

# ── Chart layout helper ───────────────────────────────────
CHART_H = 300

def base_layout(title):
    return dict(
        title=dict(text=title, font=dict(family="Satoshi", size=14, color="#0C0A1F")),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        margin=dict(l=40, r=24, t=48, b=40),
        hovermode="x unified", showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B789A", size=11)),
        yaxis=dict(gridcolor="rgba(12,10,31,0.05)",
                   tickfont=dict(color="#7B789A", size=11), tickformat=".2s"),
        height=CHART_H
    )

def area_chart(df, x, y, title, color="#7266FF", fill="rgba(114,102,255,0.08)"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y], fill="tozeroy",
        fillcolor=fill, line=dict(color=color, width=2.5),
        hovertemplate="%{x}<br><b>%{y:,.0f}</b><extra></extra>"
    ))
    fig.update_layout(**base_layout(title))
    return fig

def bar_chart(df, x, y, title, color="rgba(114,102,255,0.55)"):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[x], y=df[y],
        marker=dict(color=color, line=dict(width=0)),
        hovertemplate="%{x}<br><b>%{y:,.0f}</b><extra></extra>"
    ))
    fig.update_layout(**base_layout(title), bargap=0.2)
    return fig

# ═══════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════

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
    <div class="vc-kpi-delta {gen_dir}">{gen_chg:.2f}% vs previous day</div>
  </div>
  <div class="vc-kpi-card a2">
    <div class="vc-kpi-label">Total VTHO Claimed</div>
    <div class="vc-kpi-value">{fmt(vtho_clm_total)}</div>
    <div class="vc-kpi-delta {clm_dir}">{clm_chg:.2f}% vs previous day</div>
  </div>
  <div class="vc-kpi-card a3">
    <div class="vc-kpi-label">VET Staked (Latest)</div>
    <div class="vc-kpi-value">{fmt(vet_stk_latest)}</div>
    <div class="vc-kpi-delta {stk_dir}">{stk_chg:.2f}% vs previous day</div>
  </div>
  <div class="vc-kpi-card a4">
    <div class="vc-kpi-label">VET Delegated</div>
    <div class="vc-kpi-value">{fmt(vet_dlg_latest)}</div>
    <div class="vc-kpi-delta up">{dlg_pct:.1f}% of staked</div>
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
    st.plotly_chart(area_chart(c_gen, "date", "vtho_generated", "VTHO Generated Over Time"), use_container_width=True)
with col2:
    st.plotly_chart(bar_chart(c_clm, "date", "vtho_claimed", "VTHO Claimed"), use_container_width=True)

# ── SECTION 2: VET Staking ────────────────────────────────
st.markdown("""
<div class="vc-section gray">
  <div class="vc-section-header">
    <div class="vc-section-title">VET Staking Growth</div>
    <div class="vc-section-badge light">↑ Strong Growth Trend</div>
  </div>
</div>
""", unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(area_chart(c_stk, "date", "vet_staked", "Total VET Staked",
                               color="#7266FF", fill="rgba(114,102,255,0.08)"), use_container_width=True)
with col4:
    st.plotly_chart(area_chart(c_dlg, "date", "vet_delegated", "Total VET Delegated",
                               color="#BDB8FF", fill="rgba(189,184,255,0.10)"), use_container_width=True)

# ── SECTION 3: Combined ───────────────────────────────────
st.markdown("""
<div class="vc-section">
  <div class="vc-section-header">
    <div class="vc-section-title">VTHO Generated vs Claimed</div>
    <div class="vc-section-badge">Reward Flow</div>
  </div>
</div>
""", unsafe_allow_html=True)

col5, col6 = st.columns(2)
with col5:
    # Combined dual area
    fig_comb = go.Figure()
    fig_comb.add_trace(go.Scatter(
        x=c_gen["date"], y=c_gen["vtho_generated"],
        fill="tozeroy", fillcolor="rgba(114,102,255,0.08)",
        line=dict(color="#7266FF", width=2.5),
        name="Generated",
        hovertemplate="%{x}<br><b>Generated: %{y:,.0f}</b><extra></extra>"
    ))
    fig_comb.add_trace(go.Scatter(
        x=c_clm["date"], y=c_clm["vtho_claimed"],
        fill="tozeroy", fillcolor="rgba(189,184,255,0.12)",
        line=dict(color="#BDB8FF", width=2.5),
        name="Claimed",
        hovertemplate="%{x}<br><b>Claimed: %{y:,.0f}</b><extra></extra>"
    ))
    fig_comb.update_layout(
        **{**base_layout("VTHO Generated vs Claimed"), "showlegend": True},
        legend=dict(font=dict(color="#7B789A", size=11), bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig_comb, use_container_width=True)

with col6:
    # Raw data table
    combined = f_gen[["date","vtho_generated"]].merge(
        f_clm[["date","vtho_claimed"]], on="date", how="outer"
    ).merge(
        f_stk[["date","vet_staked"]], on="date", how="outer"
    ).merge(
        f_dlg[["date","vet_delegated"]], on="date", how="outer"
    ).sort_values("date", ascending=False)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    st.dataframe(combined, use_container_width=True, height=CHART_H)

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
