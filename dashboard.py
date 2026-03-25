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

# ── Fonts ─────────────────────────────────────────────────
st.markdown(
    '<link href="https://api.fontshare.com/v2/css?f[]=satoshi@700,500,400&display=swap" rel="stylesheet">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">',
    unsafe_allow_html=True
)

# ── CSS blocks ────────────────────────────────────────────
st.markdown("""<style>
:root { --vc-purple:#7266FF; --vc-dark:#0C0A1F; --vc-light-purple:#BDB8FF; --vc-cool-gray:#F1F1F4; --vc-white:#ffffff; --muted:#7B789A; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
#MainMenu, footer, header { visibility:hidden; }
.block-container, [data-testid="stMainBlockContainer"], .stMainBlockContainer,
.main .block-container, .appview-container .main .block-container { padding:0 !important; margin:0 !important; max-width:100% !important; }
[data-testid="stAppViewContainer"] { background:#F1F1F4; }
[data-testid="stMain"] { background:#F1F1F4; padding-top:0 !important; }
[data-testid="stMain"] > div, section[data-testid="stMain"] > div { padding-top:0 !important; }
[data-testid="stVerticalBlock"] > div:first-child,
[data-testid="stVerticalBlockBorderWrapper"]:first-child { margin-top:0 !important; padding-top:0 !important; }
</style>""", unsafe_allow_html=True)

st.markdown("""<style>
[data-testid="stSidebar"] { background:#0C0A1F !important; border-right:1px solid rgba(255,255,255,0.08); }
[data-testid="stSidebar"] * { color:rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label { color:rgba(189,184,255,0.6) !important; font-size:10px !important; letter-spacing:0.1em; text-transform:uppercase; }
[data-testid="collapsedControl"] { background:#0C0A1F !important; border-radius:0 8px 8px 0 !important; border:1px solid rgba(114,102,255,0.3) !important; border-left:none !important; }
[data-testid="collapsedControl"] svg { fill:#BDB8FF !important; color:#BDB8FF !important; }
</style>""", unsafe_allow_html=True)

st.markdown("""<style>
[data-testid="stHorizontalBlock"] { gap:24px !important; padding:24px 80px 56px 48px !important; background:transparent !important; }
[data-testid="stHorizontalBlock"] > div { padding:0 !important; min-width:0; }
[data-testid="stPlotlyChart"] { background:#ffffff; border:1px solid rgba(12,10,31,0.08); border-radius:12px; padding:24px 8px 8px 24px !important; box-shadow:0 2px 24px rgba(114,102,255,0.07); overflow:visible !important; box-sizing:border-box !important; }
[data-testid="stPlotlyChart"] > div { margin:0 !important; overflow:visible !important; }
[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container,
[data-testid="stPlotlyChart"] .plotly { overflow:visible !important; max-width:100% !important; }
.modebar-container { right:8px !important; top:8px !important; z-index:100 !important; }
[data-testid="stDataFrame"] { background:#ffffff; border:1px solid rgba(12,10,31,0.08); border-radius:12px; box-shadow:0 2px 24px rgba(114,102,255,0.07); }
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] { background:transparent !important; }
</style>""", unsafe_allow_html=True)

st.markdown("""<style>
.vc-header { background:#0C0A1F; padding:72px 80px 48px; margin-top:-10rem; border-bottom:1px solid rgba(255,255,255,0.08); position:relative; overflow:hidden; }
.vc-header::before { content:''; position:absolute; top:-160px; right:-160px; width:600px; height:600px; background:radial-gradient(circle,rgba(114,102,255,0.18) 0%,transparent 70%); pointer-events:none; }
.vc-header::after { content:''; position:absolute; bottom:-80px; left:200px; width:400px; height:400px; background:radial-gradient(circle,rgba(189,184,255,0.08) 0%,transparent 70%); pointer-events:none; }
.vc-header-tag { display:inline-flex; align-items:center; gap:8px; background:rgba(114,102,255,0.18); border:1px solid rgba(114,102,255,0.4); border-radius:100px; padding:6px 16px; font-size:11px; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:#BDB8FF; margin-bottom:20px; font-family:'Satoshi',sans-serif; }
.vc-header-tag::before { content:''; width:6px; height:6px; border-radius:50%; background:#BDB8FF; display:inline-block; animation:blink 2s ease-in-out infinite; }
.vc-header h1 { font-size:60px; font-weight:700; line-height:1.05; letter-spacing:-0.03em; margin-bottom:12px; background:linear-gradient(135deg,#ffffff 0%,#d0ccff 55%,#BDB8FF 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; font-family:'Satoshi',sans-serif; }
.vc-header-meta { display:flex; gap:40px; margin-top:36px; }
.vc-meta-item { display:flex; flex-direction:column; gap:4px; }
.vc-meta-label { font-size:10px; letter-spacing:0.12em; text-transform:uppercase; color:rgba(189,184,255,0.5); font-family:'Satoshi',sans-serif; }
.vc-meta-value { font-size:14px; font-weight:500; color:rgba(255,255,255,0.9); font-family:'Inter',sans-serif; }
</style>""", unsafe_allow_html=True)

st.markdown("""<style>
.vc-kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:rgba(12,10,31,0.08); border-bottom:1px solid rgba(12,10,31,0.08); }
.vc-kpi-card { background:#ffffff; padding:40px; position:relative; overflow:hidden; }
.vc-kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
.vc-kpi-card.a1::before, .vc-kpi-card.a4::before { background:#7266FF; }
.vc-kpi-card.a2::before, .vc-kpi-card.a3::before { background:#BDB8FF; }
.vc-kpi-label { font-size:10px; letter-spacing:0.12em; text-transform:uppercase; color:#7B789A; margin-bottom:14px; font-family:'Satoshi',sans-serif; }
.vc-kpi-value { font-size:44px; font-weight:700; line-height:1; letter-spacing:-0.025em; color:#7266FF; font-family:'Satoshi',sans-serif; }
</style>""", unsafe_allow_html=True)

st.markdown("""<style>
.vc-section-title-row { display:flex; align-items:center; justify-content:space-between; padding:56px 80px 0 48px; }
.vc-section-title { font-size:28px; font-weight:700; letter-spacing:-0.02em; color:#0C0A1F; font-family:'Satoshi',sans-serif; }
.vc-section-badge { padding:6px 14px; border-radius:6px; font-size:10px; font-weight:600; letter-spacing:0.09em; text-transform:uppercase; font-family:'Satoshi',sans-serif; background:rgba(114,102,255,0.08); color:#7266FF; border:1px solid rgba(114,102,255,0.2); white-space:nowrap; }
.vc-divider { height:1px; background:rgba(12,10,31,0.08); margin:0 80px 0 48px; }
.vc-footer { padding:40px 80px; background:#0C0A1F; display:flex; align-items:center; justify-content:space-between; margin-top:56px; }
.vc-footer-brand { font-size:13px; color:rgba(189,184,255,0.6); font-family:'Inter',sans-serif; }
.vc-footer-brand strong { color:#ffffff; font-family:'Satoshi',sans-serif; }
.vc-live-dot { display:inline-flex; align-items:center; gap:6px; font-size:11px; color:#BDB8FF; font-family:'Satoshi',sans-serif; }
.vc-live-dot::before { content:''; width:6px; height:6px; border-radius:50%; background:#7266FF; display:inline-block; animation:blink 2s ease-in-out infinite; }
</style>""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────
FROM_TS_FULL    = 1733702400
FROM_TS         = 1764547200
HEADERS         = {"accept": "*/*", "user-agent": "curl/8.0.1"}
SIZE            = 150
TIMEOUT         = 30
SLEEP_S         = 0.10
PRE_FORK_ANNUAL = 13_672_848_202.60

LEVEL_ORDER = ["Dawn","Lightning","Flash","VeThorX","Thunder","Strength",
               "ThunderX","StrengthX","Mjolnir","MjolnirX"]
LEVEL_COLORS = [
    "#BDB8FF","#A09AFF","#8E87FF","#7C75FF","#7266FF",
    "#6057E8","#4E45D1","#3C34BA","#2A23A3","#18128C"
]

# ── Consistent chart constants ────────────────────────────
CH        = 400          # universal chart height
TICK_FONT = dict(color="#7B789A", size=11, family="Inter")
TITLE_FONT= dict(color="#0C0A1F", size=14, family="Satoshi")
SUB_FONT  = dict(color="#7B789A", size=12, family="Inter")
LEG_FONT  = dict(color="#7B789A", size=11, family="Inter")
MARGINS   = dict(l=56, r=100, t=72, b=80)   # consistent on all charts
PIE_MARGINS = dict(l=60, r=60, t=72, b=80)

def section_title(title, badge):
    st.markdown(
        f'<div class="vc-section-title-row">'
        f'<div class="vc-section-title">{title}</div>'
        f'<div class="vc-section-badge">{badge}</div>'
        f'</div>', unsafe_allow_html=True)

def divider():
    st.markdown('<div class="vc-divider"></div>', unsafe_allow_html=True)

# ── Chart layout helpers ──────────────────────────────────
def base_layout(title, subtitle=None):
    return dict(
        title=dict(
            text=title,
            subtitle=dict(text=subtitle, font=SUB_FONT) if subtitle else None,
            font=TITLE_FONT, pad=dict(t=0, b=0)
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=MARGINS,
        height=CH,
        hovermode="x unified", showlegend=False,
        xaxis=dict(
            showgrid=False, tickfont=TICK_FONT, automargin=True,
            linecolor="rgba(12,10,31,0.1)", linewidth=1
        ),
        yaxis=dict(
            showgrid=False, tickfont=TICK_FONT,
            tickformat=".2s", automargin=True, rangemode="nonnegative",
            linecolor="rgba(12,10,31,0.1)", exponentformat="none"
        ),
    )

def legend_bottom():
    return dict(font=LEG_FONT, bgcolor="rgba(0,0,0,0)",
                orientation="h", yanchor="top", y=-0.28,
                xanchor="left", x=0)

def pie_layout(title, subtitle=None, entrywidth=40):
    """Shared layout for all pie/donut charts."""
    return dict(
        title=dict(
            text=title,
            subtitle=dict(text=subtitle, font=SUB_FONT) if subtitle else None,
            font=TITLE_FONT,
            x=0.04, xanchor="left"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=PIE_MARGINS,
        height=CH,
        showlegend=True,
        legend=dict(
            font=LEG_FONT, bgcolor="rgba(0,0,0,0)",
            orientation="h", yanchor="top", y=-0.22,
            xanchor="left", x=0.0,
            entrywidth=entrywidth,
            entrywidthmode="pixels"
        )
    )

def legend_bottom():
    return dict(font=LEG_FONT, bgcolor="rgba(0,0,0,0)",
                orientation="h", yanchor="top", y=-0.12,
                xanchor="left", x=0)

# ── Fetch helpers ─────────────────────────────────────────
def _fetch_daily(url, value_col, from_ts=None):
    if from_ts is None:
        from_ts = FROM_TS
    TO_TS   = int(pd.Timestamp.utcnow().timestamp())
    session = requests.Session(); session.headers.update(HEADERS)
    rows = []
    start_day = pd.to_datetime(from_ts, unit="s", utc=True).normalize()
    end_day   = pd.to_datetime(TO_TS,   unit="s", utc=True).normalize()
    for day_start in pd.date_range(start_day, end_day, freq="D", tz="UTC"):
        day_end     = day_start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        window_from = max(from_ts, int(day_start.timestamp()))
        window_to   = min(TO_TS,   int(day_end.timestamp()))
        if window_from > window_to: continue
        page = 0
        while True:
            params = {"from": window_from, "to": window_to,
                      "page": page, "size": SIZE, "direction": "ASC"}
            r = session.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json().get("data", []) or []
            rows.extend(data)
            if len(data) < SIZE: break
            page += 1; time.sleep(SLEEP_S)
    if not rows:
        return pd.DataFrame(columns=["blockNumber","blockTimestamp","gmtTime","date",value_col])
    df = pd.DataFrame(rows)[["blockNumber","blockTimestamp","total"]].copy()
    df["gmtTime"] = pd.to_datetime(df["blockTimestamp"], unit="s", utc=True)
    df["date"]    = df["gmtTime"].dt.date
    df[value_col] = pd.to_numeric(df["total"], errors="coerce") / 1e18
    df = df.drop_duplicates(subset=["blockNumber","blockTimestamp"])
    df = df.sort_values(["blockTimestamp","blockNumber"]).reset_index(drop=True)
    return df[["blockNumber","blockTimestamp","gmtTime","date",value_col]]

@st.cache_data(ttl=300)
def fetch_vtho_generated():
    return _fetch_daily("https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-generated/DAY","vtho_generated")

@st.cache_data(ttl=300)
def fetch_vtho_claimed():
    df = _fetch_daily("https://indexer.mainnet.vechain.org/api/v1/stargate/vtho-claimed/DAY","vtho_claimed")
    return df[df["vtho_claimed"] > 0].reset_index(drop=True)

@st.cache_data(ttl=300)
def fetch_vet_staked():
    df = _fetch_daily("https://indexer.mainnet.vechain.org/api/v1/stargate/vet-staked/DAY","vet_staked_delta",from_ts=FROM_TS_FULL)
    df["vet_staked_cumsum"] = df["vet_staked_delta"].cumsum()
    df = df.groupby("date").agg(vet_staked_delta=("vet_staked_delta","sum"),vet_staked_cumsum=("vet_staked_cumsum","last")).reset_index()
    dec1 = pd.to_datetime(FROM_TS, unit="s", utc=True).date()
    return df[df["date"] >= dec1].reset_index(drop=True)

@st.cache_data(ttl=300)
def fetch_vet_delegated():
    df = _fetch_daily("https://indexer.mainnet.vechain.org/api/v1/stargate/vet-delegated/DAY","vet_delegated_delta")
    df["vet_delegated_cumsum"] = df["vet_delegated_delta"].cumsum()
    df = df.groupby("date").agg(vet_delegated_delta=("vet_delegated_delta","sum"),vet_delegated_cumsum=("vet_delegated_cumsum","last")).reset_index()
    return df[["date","vet_delegated_delta","vet_delegated_cumsum"]]

@st.cache_data(ttl=300)
def fetch_total_vet_staked_snapshot():
    r = requests.get("https://indexer.mainnet.vechain.org/api/v1/stargate/total-vet-staked",headers=HEADERS,timeout=TIMEOUT)
    r.raise_for_status(); data = r.json()
    by_level = {k: int(v)/1e18 for k,v in data["byLevel"].items()}
    nft_by_level = data["nftCountByLevel"]
    df_level = pd.DataFrame({"level":list(by_level.keys()),"vet_staked":list(by_level.values()),"nft_count":[nft_by_level[k] for k in by_level]})
    df_level["order"] = df_level["level"].map({l:i for i,l in enumerate(LEVEL_ORDER)})
    return int(data["total"])/1e18, data["totalNftCount"], df_level.sort_values("order").reset_index(drop=True)

@st.cache_data(ttl=300)
def fetch_total_vet_delegated_snapshot():
    r = requests.get("https://indexer.mainnet.vechain.org/api/v1/stargate/total-vet-delegated",headers=HEADERS,timeout=TIMEOUT)
    r.raise_for_status(); data = r.json()
    by_level = {k: int(v)/1e18 for k,v in data["byLevel"].items()}
    nft_by_level = data["nftCountByLevel"]
    df_level = pd.DataFrame({"level":list(by_level.keys()),"vet_delegated":list(by_level.values()),"nft_count":[nft_by_level[k] for k in by_level]})
    df_level["order"] = df_level["level"].map({l:i for i,l in enumerate(LEVEL_ORDER)})
    return int(data["total"])/1e18, data["totalNftCount"], df_level.sort_values("order").reset_index(drop=True)

@st.cache_data(ttl=300)
def fetch_nft_holders_snapshot():
    r = requests.get("https://indexer.mainnet.vechain.org/api/v1/stargate/nft-holders",headers=HEADERS,timeout=TIMEOUT)
    r.raise_for_status(); data = r.json()
    df_h = pd.DataFrame({"level":list(data["byLevel"].keys()),"holders":list(data["byLevel"].values())})
    df_h["order"] = df_h["level"].map({l:i for i,l in enumerate(LEVEL_ORDER)})
    return data["total"], df_h.sort_values("order").reset_index(drop=True)

@st.cache_data(ttl=300)
def fetch_validators():
    rows, page = [], 0
    session = requests.Session(); session.headers.update(HEADERS)
    while True:
        r = session.get("https://indexer.mainnet.vechain.org/api/v1/validators",params={"page":page,"size":50,"direction":"ASC"},timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json().get("data",[]) or []
        rows.extend(data)
        if not r.json()["pagination"]["hasNext"]: break
        page += 1; time.sleep(SLEEP_S)
    df = pd.DataFrame(rows)
    active = df[df["status"]=="ACTIVE"].copy().reset_index(drop=True)
    apy_rows = []
    for _, row in active[active["delegatorVetStaked"]>0].iterrows():
        yields = row.get("nftYieldsNextCycle", {})
        if isinstance(yields, dict):
            for level, apy in yields.items():
                apy_rows.append({"level": level, "apy": float(apy)})
    apy_df = pd.DataFrame(apy_rows)
    tbl = []
    for level in LEVEL_ORDER:
        sub = apy_df[apy_df["level"]==level]["apy"]
        tbl.append({"NFT Level":level,"Min APY":round(sub.min(),1),"Avg APY":round(sub.mean(),1),"Max APY":round(sub.max(),1)})
    apy_table = pd.DataFrame(tbl)
    apy_table["Est. APY Range"] = apy_table["Min APY"].map("{:.1f}%".format)+" – "+apy_table["Max APY"].map("{:.1f}%".format)
    apy_table["Avg APY"] = apy_table["Avg APY"].map("{:.1f}%".format)
    return active, apy_table

# ── Load ──────────────────────────────────────────────────
with st.spinner("Fetching data from VeChain indexer..."):
    df      = fetch_vtho_generated()
    df_clm  = fetch_vtho_claimed()
    df_stk  = fetch_vet_staked()
    df_dlg  = fetch_vet_delegated()
    snap_vet, snap_nft, df_level             = fetch_total_vet_staked_snapshot()
    snap_dlg_vet, snap_dlg_nft, df_dlg_level = fetch_total_vet_delegated_snapshot()
    snap_holders, df_holders                 = fetch_nft_holders_snapshot()
    df_validators, df_apy_table              = fetch_validators()

if df.empty:
    st.error("No data returned from API."); st.stop()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Filters")
    period = st.selectbox("Aggregation", ["Daily","Weekly","Monthly"])
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.date_input("Date Range",
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date, max_value=max_date)

s = date_range[0] if len(date_range) >= 1 else min_date
e = date_range[1] if len(date_range) == 2 else max_date

filtered = df[(df["date"]>=s)&(df["date"]<=e)].copy()
if filtered.empty:
    st.warning("No data for selected range."); st.stop()

f_clm = df_clm[(df_clm["date"]>=s)&(df_clm["date"]<=e)].copy()
f_stk = df_stk[(df_stk["date"]>=s)&(df_stk["date"]<=e)].copy()
f_dlg = df_dlg[(df_dlg["date"]>=s)&(df_dlg["date"]<=e)].copy()

# ── Aggregate ─────────────────────────────────────────────
def aggregate(d, col, how="sum"):
    d = d.copy()
    d["gmtTime"] = pd.to_datetime(d["date"] if "gmtTime" not in d.columns else d["gmtTime"])
    if period == "Weekly":
        r = d.set_index("gmtTime").resample("W")[col].agg(how).reset_index()
    elif period == "Monthly":
        r = d.set_index("gmtTime").resample("ME")[col].agg(how).reset_index()
    else:
        return d[["date",col]].copy()
    r.columns = ["date",col]; return r

filtered["gmtTime"] = pd.to_datetime(filtered["gmtTime"])
f_clm["gmtTime"]    = pd.to_datetime(f_clm["gmtTime"])
f_stk["gmtTime"]    = pd.to_datetime(f_stk["date"])
f_dlg["gmtTime"]    = pd.to_datetime(f_dlg["date"])

chart_df  = aggregate(filtered,"vtho_generated","sum")
chart_clm = aggregate(f_clm,"vtho_claimed","sum")

if period in ["Weekly","Monthly"]:
    freq = "W" if period=="Weekly" else "ME"
    chart_stk = f_stk.set_index("gmtTime").resample(freq).agg(
        vet_staked_delta=("vet_staked_delta","sum"),
        vet_staked_cumsum=("vet_staked_cumsum","last")
    ).reset_index().rename(columns={"gmtTime":"date"})
    chart_dlg = f_dlg.set_index("gmtTime").resample(freq)["vet_delegated_cumsum"].last().reset_index()
    chart_dlg.columns = ["date","vet_delegated_cumsum"]
else:
    chart_stk = f_stk[["date","vet_staked_delta","vet_staked_cumsum"]].copy()
    chart_dlg = f_dlg[["date","vet_delegated_cumsum"]].copy()

# ── KPIs ──────────────────────────────────────────────────
vtho_gen_total = filtered["vtho_generated"].sum()
vtho_clm_total = f_clm["vtho_claimed"].sum() if not f_clm.empty else 0
validator_vet  = df_validators["validatorVetStaked"].sum()
tvl            = snap_vet + validator_vet

def fmt(v):
    if v >= 1e9: return f"{v/1e9:.2f}B"
    if v >= 1e6: return f"{v/1e6:.2f}M"
    if v >= 1e3: return f"{v/1e3:.2f}K"
    return f"{v:,.2f}"

last_updated = pd.Timestamp.utcnow().strftime("%-d %b %Y, %H:%M UTC")

# ════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════
st.markdown(f"""
<div class="vc-header">
  <div class="vc-header-tag">Live &middot; Post-Hayabusa Analysis</div>
  <h1>StarGate by VeChain<br>Performance Report</h1>
  <div class="vc-header-meta">
    <div class="vc-meta-item"><span class="vc-meta-label">Hard Fork</span><span class="vc-meta-value">Hayabusa</span></div>
    <div class="vc-meta-item"><span class="vc-meta-label">Key Change</span><span class="vc-meta-value">Fixed &#8594; Proportional VTHO Issuance</span></div>
    <div class="vc-meta-item"><span class="vc-meta-label">Data Source</span><span class="vc-meta-value">VeChain StarGate Indexer API</span></div>
    <div class="vc-meta-item"><span class="vc-meta-label">Last Updated</span><span class="vc-meta-value">{last_updated}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# KPI ROW
# ════════════════════════════════════════════════════
st.markdown(f"""
<div class="vc-kpi-row">
  <div class="vc-kpi-card a1"><div class="vc-kpi-label">Total Value Locked</div><div class="vc-kpi-value">{fmt(tvl)}</div></div>
  <div class="vc-kpi-card a2"><div class="vc-kpi-label">Total VTHO Generated</div><div class="vc-kpi-value">{fmt(vtho_gen_total)}</div></div>
  <div class="vc-kpi-card a3"><div class="vc-kpi-label">Total NFT Minted</div><div class="vc-kpi-value">{fmt(snap_nft)}</div></div>
  <div class="vc-kpi-card a4"><div class="vc-kpi-label">Unique NFT Holders</div><div class="vc-kpi-value">{fmt(snap_holders)}</div></div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# SECTION 1 — Staking Overview
# ════════════════════════════════════════════════════
section_title("Staking Overview", "Strong Growth Trend &uarr;")

col1, col2 = st.columns(2)
with col1:
    stk_line = chart_stk[["date","vet_staked_cumsum"]].copy()
    dlg_line = chart_dlg[["date","vet_delegated_cumsum"]].copy()
    stk_line["val_B"] = stk_line["vet_staked_cumsum"] / 1e9
    dlg_line["val_B"] = dlg_line["vet_delegated_cumsum"] / 1e9
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=stk_line["date"], y=stk_line["val_B"], name="Total VET Staked",
        fill="tozeroy", fillcolor="rgba(114,102,255,0.10)",
        line=dict(color="#7266FF",width=2.5), mode="lines",
        hovertemplate="%{x}<br><b>Staked: %{y:.2f}B VET</b><extra></extra>"
    ))
    fig1.add_trace(go.Scatter(
        x=dlg_line["date"], y=dlg_line["val_B"], name="Delegated Stake",
        fill="tozeroy", fillcolor="rgba(189,184,255,0.12)",
        line=dict(color="#BDB8FF",width=2.5,dash="dash"), mode="lines",
        hovertemplate="%{x}<br><b>Delegated: %{y:.2f}B VET</b><extra></extra>"
    ))
    if not stk_line.empty:
        fig1.add_annotation(x=stk_line["date"].iloc[-1], y=stk_line["val_B"].iloc[-1],
            text=f"<b>{stk_line['val_B'].iloc[-1]:.2f}B</b>",
            showarrow=False, xanchor="left", xshift=10,
            font=dict(size=11, color="#7266FF", family="Inter"))
    if not dlg_line.empty:
        fig1.add_annotation(x=dlg_line["date"].iloc[-1], y=dlg_line["val_B"].iloc[-1],
            text=f"<b>{dlg_line['val_B'].iloc[-1]:.2f}B</b>",
            showarrow=False, xanchor="left", xshift=10,
            font=dict(size=11, color="#BDB8FF", family="Inter"))
    l1 = base_layout("VET Staked vs. Delegated","Cumulative VET locked in StarGate staking and delegation")
    l1["showlegend"] = True
    l1["legend"] = dict(font=LEG_FONT, bgcolor="rgba(0,0,0,0)",
                        orientation="h", yanchor="top", y=-0.38,
                        xanchor="left", x=0)
    l1["yaxis"]["tickformat"] = ".2f"
    l1["yaxis"]["ticksuffix"] = "B"
    l1["yaxis"]["exponentformat"] = "none"
    l1["yaxis"]["rangemode"] = "normal"   # allow axis to start near data, not zero
    l1["yaxis"]["autorange"] = True
    l1["margin"] = dict(l=56, r=100, t=72, b=100)  # extra bottom for legend
    fig1.update_layout(**l1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Pie(
        labels=["Validator Stake","Delegated Stake","Undelegated Stake"],
        values=[validator_vet, snap_dlg_vet, max(snap_vet-snap_dlg_vet,0)],
        marker=dict(colors=["#7266FF","#BDB8FF","#E0DEFF"]),
        hole=0.48,
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} VET<br>%{percent}<extra></extra>",
        textfont=TICK_FONT, textposition="outside",
        texttemplate="%{percent:.2%}", sort=False,
        domain=dict(x=[0.1, 0.9], y=[0.15, 0.95])
    ))
    fig2.add_annotation(
        text=f"<b>{fmt(tvl)}</b><br><span style='font-size:11px;color:#7B789A;font-family:Inter'>Total TVL</span>",
        x=0.5, y=0.57, showarrow=False, align="center",
        font=dict(size=15, color="#0C0A1F", family="Satoshi"))
    l2 = pie_layout("Stake Composition","Validator · Delegated · Undelegated", entrywidth=150)
    fig2.update_layout(**l2)
    fig2.update_traces(pull=[0.03, 0.03, 0.03])  # slight pull on all slices for label room
    st.plotly_chart(fig2, use_container_width=True)

divider()

# ════════════════════════════════════════════════════
# SECTION 2 — VTHO Emission
# ════════════════════════════════════════════════════
section_title("VTHO Emission", "Key Mechanism Change")

col3, col4 = st.columns(2)
with col3:
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=chart_df["date"], y=chart_df["vtho_generated"] / 1e6,
        fill="tozeroy", fillcolor="rgba(114,102,255,0.08)",
        line=dict(color="#7266FF",width=2.5),
        hovertemplate="%{x}<br><b>%{y:.2f}M VTHO</b><extra></extra>"
    ))
    if not chart_df.empty:
        fig3.add_annotation(
            x=chart_df["date"].iloc[-1], y=chart_df["vtho_generated"].iloc[-1] / 1e6,
            text=f"<b>{chart_df['vtho_generated'].iloc[-1]/1e6:.2f}M</b>",
            showarrow=False, xanchor="left", xshift=10,
            font=dict(size=11, color="#7266FF", family="Inter"))
    l3 = base_layout("VTHO Generated","Emission rising proportionally as more VET gets staked")
    l3["yaxis"]["rangemode"] = "nonnegative"
    l3["yaxis"]["tickformat"] = ".2f"
    l3["yaxis"]["ticksuffix"] = "M"
    l3["yaxis"]["exponentformat"] = "none"
    fig3.update_layout(**l3)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    ann_df = filtered[["date","vtho_generated"]].copy()
    ann_df["ann_B"] = ann_df["vtho_generated"] * 365 / 1e9
    pre_B = PRE_FORK_ANNUAL / 1e9
    fig4 = go.Figure()
    fig4.add_shape(type="line",
        x0=ann_df["date"].iloc[0], x1=ann_df["date"].iloc[-1],
        y0=pre_B, y1=pre_B,
        line=dict(color="#7266FF",width=1.8,dash="dash"))
    fig4.add_annotation(x=ann_df["date"].iloc[-1], y=pre_B,
        text=f"<b>{pre_B:.2f}B</b>",
        showarrow=False, xanchor="left", xshift=10,
        font=dict(size=11, color="#7266FF", family="Inter"))
    fig4.add_trace(go.Scatter(
        x=ann_df["date"], y=ann_df["ann_B"], name="Post-Hayabusa",
        fill="tozeroy", fillcolor="rgba(114,102,255,0.10)",
        line=dict(color="#BDB8FF",width=2.5),
        mode="lines",
        hovertemplate="%{x}<br><b>%{y:.2f}B VTHO/yr</b><extra></extra>"
    ))
    if not ann_df.empty:
        fig4.add_annotation(
            x=ann_df["date"].iloc[-1], y=ann_df["ann_B"].iloc[-1],
            text=f"<b>{ann_df['ann_B'].iloc[-1]:.2f}B</b>",
            showarrow=False, xanchor="left", xshift=10,
            font=dict(size=11, color="#BDB8FF", family="Inter")
        )
    fig4.add_trace(go.Scatter(x=[None], y=[None], name="Pre-Hayabusa",
        mode="lines", line=dict(color="#7266FF",width=2,dash="dash")))
    l4 = base_layout("Annualised Emission Rate",f"Post-Hayabusa vs. {pre_B:.2f}B/yr pre-fork baseline")
    l4["showlegend"] = True
    l4["legend"] = legend_bottom()
    l4["yaxis"]["tickformat"] = ".2f"
    l4["yaxis"]["ticksuffix"] = "B"
    l4["yaxis"]["exponentformat"] = "none"
    l4["yaxis"]["autorange"] = False
    ann_y_min = max(0, ann_df["ann_B"].min() * 0.95)
    ann_y_max = max(ann_df["ann_B"].max(), pre_B) * 1.10
    l4["yaxis"]["range"] = [ann_y_min, ann_y_max]
    fig4.update_layout(**l4)
    st.plotly_chart(fig4, use_container_width=True)

divider()

# ════════════════════════════════════════════════════
# SECTION 3 — Staking by Level
# ════════════════════════════════════════════════════
section_title("Staking by Level", "Live Snapshot")

col5, col6 = st.columns(2)
with col5:
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=df_level["level"], y=df_level["vet_staked"],
        marker=dict(color=LEVEL_COLORS,line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>%{y:,.2f} VET<extra></extra>"
    ))
    l5 = base_layout("VET Staked by Level","Total VET locked per staking tier")
    l5["bargap"] = 0.25; l5["hovermode"] = "x"
    l5["yaxis"]["rangemode"] = "nonnegative"
    l5["yaxis"]["tickformat"] = ".2f"
    l5["yaxis"]["ticksuffix"] = "B"
    l5["yaxis"]["exponentformat"] = "none"
    # convert to billions for clean labels
    fig5.update_traces(y=df_level["vet_staked"] / 1e9)
    fig5.update_layout(**l5)
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    fig6 = go.Figure()
    total_nft_s3 = df_level["nft_count"].sum()
    fig6.add_trace(go.Pie(
        labels=df_level["level"], values=df_level["nft_count"],
        marker=dict(colors=LEVEL_COLORS), hole=0.45,
        hovertemplate="<b>%{label}</b><br>%{value:,} NFTs<br>%{percent}<extra></extra>",
        textfont=TICK_FONT, textposition="outside",
        texttemplate="%{percent:.2%}", sort=False,
        domain=dict(x=[0.1, 0.9], y=[0.15, 0.95])
    ))
    fig6.add_annotation(
        text=f"<b>{fmt(total_nft_s3)}</b><br><span style='font-size:11px;color:#7B789A;font-family:Inter'>Total NFTs</span>",
        x=0.5, y=0.57, showarrow=False, align="center",
        font=dict(size=14, color="#0C0A1F", family="Satoshi"))
    l6 = pie_layout("NFT Minted by Level","Share of total NFTs minted per staking tier", entrywidth=40)
    fig6.update_layout(**l6)
    st.plotly_chart(fig6, use_container_width=True)

divider()

# ════════════════════════════════════════════════════
# SECTION 4 — Delegation by Level
# ════════════════════════════════════════════════════
section_title("Delegation by Level", "Live Snapshot")

col7, col8 = st.columns(2)
with col7:
    fig7 = go.Figure()
    fig7.add_trace(go.Bar(
        x=df_dlg_level["level"], y=df_dlg_level["vet_delegated"] / 1e9,
        marker=dict(color=LEVEL_COLORS,line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>%{y:.2f}B VET<extra></extra>"
    ))
    l7 = base_layout("VET Delegated by Level","Total VET delegated per staking tier")
    l7["bargap"] = 0.25; l7["hovermode"] = "x"
    l7["yaxis"]["rangemode"] = "nonnegative"
    l7["yaxis"]["tickformat"] = ".2f"
    l7["yaxis"]["ticksuffix"] = "B"
    l7["yaxis"]["exponentformat"] = "none"
    fig7.update_layout(**l7)
    st.plotly_chart(fig7, use_container_width=True)

with col8:
    fig8 = go.Figure()
    total_nft_s4 = df_dlg_level["nft_count"].sum()
    fig8.add_trace(go.Pie(
        labels=df_dlg_level["level"], values=df_dlg_level["nft_count"],
        marker=dict(colors=LEVEL_COLORS), hole=0.45,
        hovertemplate="<b>%{label}</b><br>%{value:,} NFTs<br>%{percent}<extra></extra>",
        textfont=TICK_FONT, textposition="outside",
        texttemplate="%{percent:.2%}", sort=False,
        domain=dict(x=[0.1, 0.9], y=[0.15, 0.95])
    ))
    fig8.add_annotation(
        text=f"<b>{fmt(total_nft_s4)}</b><br><span style='font-size:11px;color:#7B789A;font-family:Inter'>Total NFTs</span>",
        x=0.5, y=0.57, showarrow=False, align="center",
        font=dict(size=14, color="#0C0A1F", family="Satoshi"))
    l8 = pie_layout("NFTs Delegating by Level","Share of delegating NFTs per staking tier", entrywidth=40)
    fig8.update_layout(**l8)
    st.plotly_chart(fig8, use_container_width=True)

divider()

# ════════════════════════════════════════════════════
# SECTION 5 — Holders & Yield
# ════════════════════════════════════════════════════
section_title("Holders &amp; Yield", "Live Snapshot")

col9, col10 = st.columns(2)
with col9:
    fig9 = go.Figure()
    fig9.add_trace(go.Pie(
        labels=df_holders["level"], values=df_holders["holders"],
        marker=dict(colors=LEVEL_COLORS), hole=0.45,
        hovertemplate="<b>%{label}</b><br>%{value:,} holders<br>%{percent}<extra></extra>",
        textfont=TICK_FONT, textposition="outside",
        texttemplate="%{percent:.2%}", sort=False,
        domain=dict(x=[0.1, 0.9], y=[0.15, 0.95])
    ))
    fig9.add_annotation(
        text=f"<b>{fmt(snap_holders)}</b><br><span style='font-size:11px;color:#7B789A;font-family:Inter'>Total Holders</span>",
        x=0.5, y=0.57, showarrow=False, align="center",
        font=dict(size=14, color="#0C0A1F", family="Satoshi"))
    l9 = pie_layout("Holders by Level","Unique holders per staking tier", entrywidth=40)
    fig9.update_layout(**l9)
    st.plotly_chart(fig9, use_container_width=True)

with col10:
    st.markdown(
        '<div style="font-size:14px;font-weight:700;color:#0C0A1F;'
        'font-family:Satoshi,sans-serif;margin-bottom:6px;padding-top:4px;">'
        'Est. APY Range by NFT Level</div>'
        '<div style="font-size:12px;color:#7B789A;font-family:Inter,sans-serif;margin-bottom:16px;">'
        'Validators accepting delegation only &middot; Next cycle</div>',
        unsafe_allow_html=True)
    st.dataframe(
        df_apy_table[["NFT Level","Est. APY Range","Avg APY"]],
        use_container_width=True, hide_index=True, height=360,
        column_config={
            "NFT Level":      st.column_config.TextColumn("NFT Level"),
            "Est. APY Range": st.column_config.TextColumn("Est. APY Range"),
            "Avg APY":        st.column_config.TextColumn("Avg APY"),
        })

# ════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════
st.markdown(
    '<div class="vc-footer">'
    '<div class="vc-footer-brand"><strong>VeChain StarGate</strong> &mdash; Post-Hayabusa Report</div>'
    '<div class="vc-live-dot">Live Data</div>'
    '</div>', unsafe_allow_html=True)
