import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import load_data
from scorer import score_companies, get_display_columns
from lbo import run_lbo, irr_rating, moic_rating

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PE Deal Sourcing Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main-header { font-size:2.2rem; font-weight:700; color:#1a1a2e; letter-spacing:-0.5px; }
.sub-header  { font-size:1rem; color:#666; margin-top:-10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📊 PE Deal Sourcing Screener</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">S&P 500 Acquisition Target Ranking + LBO Returns Estimator</p>', unsafe_allow_html=True)
st.divider()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔧 Screening Filters")
    max_ev_ebitda    = st.slider("EV/EBITDA (max)", 5, 50, 20)
    min_ebitda_margin= st.slider("Min EBITDA Margin", 0, 50, 10, format="%d%%")
    min_rev_growth   = st.slider("Min Revenue Growth", -20, 50, 0, format="%d%%")
    cap_options = {"All":(0,10000),"Small Cap (<$2B)":(0,2),"Mid Cap ($2B–$10B)":(2,10),"Large Cap (>$10B)":(10,10000)}
    cap_sel          = st.selectbox("Market Cap", list(cap_options.keys()))
    cap_min, cap_max = cap_options[cap_sel]
    top_n            = st.slider("Show Top N", 10, 90, 30, 5)
    st.divider()
    st.caption("PE Deal Sourcing Screener v2.0")

# ─── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return score_companies(load_data())

df = get_data()

sectors        = ["All Sectors"] + sorted(df["sector"].dropna().unique().tolist())
selected_sector= st.sidebar.selectbox("Sector", sectors)

filtered = df.copy()
if selected_sector != "All Sectors":
    filtered = filtered[filtered["sector"] == selected_sector]
filtered = filtered[
    (filtered["ev_ebitda"].fillna(999)  <= max_ev_ebitda) &
    (filtered["ebitda_margin"].fillna(0)*100 >= min_ebitda_margin) &
    (filtered["revenue_growth"].fillna(-99)*100 >= min_rev_growth) &
    (filtered["market_cap"].fillna(0)/1e9 >= cap_min) &
    (filtered["market_cap"].fillna(0)/1e9 <= cap_max)
].head(top_n)

# ─── KPIs ─────────────────────────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
c1.metric("Companies in Universe", len(df))
c2.metric("Matching Targets", len(filtered))
c3.metric("Strong Buy Signals", len(filtered[filtered["rating"]=="🟢 Strong Buy"]))
c4.metric("Avg PE Score", f"{filtered['pe_score'].mean():.1f}/100" if len(filtered) else "—")
st.divider()

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🏆 Deal Screener", "📐 LBO Returns Estimator"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: DEAL SCREENER
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(f"🏆 Top {len(filtered)} Acquisition Targets")
    display_df = get_display_columns(filtered)
    st.dataframe(
        display_df, use_container_width=True, height=420, hide_index=True,
        column_config={"PE Score": st.column_config.ProgressColumn("PE Score", min_value=0, max_value=100, format="%d")},
    )
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Export to CSV", data=csv, file_name="pe_targets.csv", mime="text/csv")

    st.divider()
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Avg Score by Sector")
        if len(filtered):
            sect_avg = filtered.groupby("sector")["pe_score"].mean().reset_index().sort_values("pe_score")
            fig = px.bar(sect_avg, x="pe_score", y="sector", orientation="h",
                         color="pe_score", color_continuous_scale="Blues",
                         labels={"pe_score":"Avg PE Score","sector":"Sector"})
            fig.update_layout(showlegend=False, coloraxis_showscale=False, plot_bgcolor="white", height=340)
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🔍 EV/EBITDA vs EBITDA Margin")
        if len(filtered):
            pd2 = filtered.dropna(subset=["ev_ebitda","ebitda_margin"]).head(50)
            fig2 = px.scatter(pd2, x="ev_ebitda", y="ebitda_margin", size="pe_score",
                              color="rating", hover_name="name",
                              color_discrete_map={"🟢 Strong Buy":"#2ecc71","🟡 Watch List":"#f1c40f",
                                                  "🟠 Marginal":"#e67e22","🔴 Pass":"#e74c3c"},
                              labels={"ev_ebitda":"EV/EBITDA (x)","ebitda_margin":"EBITDA Margin"})
            fig2.update_layout(plot_bgcolor="white", height=340, legend_title="Rating")
            fig2.update_yaxes(tickformat=".0%")
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("🔬 Company Deep Dive")
    if len(filtered):
        sel = st.selectbox("Select company:",
                           options=filtered["ticker"].tolist(),
                           format_func=lambda t: f"{t} — {filtered[filtered['ticker']==t]['name'].values[0]}")
        comp = filtered[filtered["ticker"]==sel].iloc[0]
        d1,d2,d3 = st.columns(3)
        with d1:
            st.markdown(f"**{comp['name']}**")
            st.markdown(f"Sector: `{comp['sector']}`")
            st.markdown(f"Industry: `{comp['industry']}`")
        with d2:
            st.metric("PE Score", f"{comp['pe_score']}/100")
            st.metric("Rating", comp["rating"])
        with d3:
            st.metric("Market Cap", f"${comp['market_cap']/1e9:.1f}B")
            st.metric("EV/EBITDA", f"{comp['ev_ebitda']:.1f}x")

        radar_map = {"Valuation":"ev_ebitda_score","Profitability":"ebitda_margin_score",
                     "Growth":"revenue_growth_score","Cash Flow":"fcf_score","Low Debt":"debt_score"}
        avail = {k:v for k,v in radar_map.items() if v in comp.index}
        if avail:
            cats = list(avail.keys()); vals = [comp[v] for v in avail.values()]
            fig_r = go.Figure(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]],
                fill="toself", fillcolor="rgba(26,26,46,0.2)",
                line=dict(color="#1a1a2e", width=2)))
            fig_r.update_layout(polar=dict(radialaxis=dict(range=[0,100])),
                                 showlegend=False, height=350, title="Sub-Score Breakdown")
            st.plotly_chart(fig_r, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: LBO ESTIMATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📐 LBO Returns Estimator")
    st.caption("Model a leveraged buyout and estimate IRR & MOIC.")

    l1, l2 = st.columns(2)
    with l1:
        st.markdown("**Deal Parameters**")
        lbo_ebitda    = st.number_input("EBITDA ($M)", 10, 10000, 200, 10)
        entry_mult    = st.slider("Entry EV/EBITDA (x)", 5.0, 25.0, 10.0, 0.5, key="entry")
        debt_pct      = st.slider("Debt Financing (%)", 30, 80, 60, 5, key="debt") / 100
        interest_rate = st.slider("Interest Rate (%)", 4, 15, 7, 1, key="ir") / 100
    with l2:
        st.markdown("**Exit Assumptions**")
        exit_mult     = st.slider("Exit EV/EBITDA (x)", 5.0, 25.0, 12.0, 0.5, key="exit")
        hold_years    = st.slider("Holding Period (years)", 3, 7, 5, key="hold")
        ebitda_cagr   = st.slider("EBITDA Growth CAGR (%)", 0, 30, 10, 1, key="cagr") / 100
        paydown_pct   = st.slider("FCF → Debt Paydown (%)", 20, 100, 60, 10, key="pay") / 100

    res = run_lbo(lbo_ebitda, entry_mult, debt_pct, interest_rate, ebitda_cagr, exit_mult, hold_years, paydown_pct)

    st.divider()
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("IRR",          f"{res['irr']}%");     st.caption(irr_rating(res["irr"])) if False else None
    k2.metric("MOIC",         f"{res['moic']}x")
    k3.metric("Entry Equity", f"${res['entry_equity']:.0f}M")
    k4.metric("Exit Equity",  f"${res['exit_equity']:.0f}M")

    st.markdown(f"**{irr_rating(res['irr'])}** &nbsp;|&nbsp; **{moic_rating(res['moic'])}**")
    st.divider()

    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("**EBITDA & Debt Over Time**")
        fig_lbo = go.Figure()
        fig_lbo.add_trace(go.Bar(x=res["years"], y=res["ebitda_proj"],
                                  name="EBITDA ($M)", marker_color="#2ecc71"))
        fig_lbo.add_trace(go.Scatter(x=res["years"], y=res["debt_schedule"],
                                      name="Debt ($M)", line=dict(color="#e74c3c", width=3), mode="lines+markers"))
        fig_lbo.update_layout(xaxis_title="Year", yaxis_title="$M",
                               plot_bgcolor="white", height=320,
                               legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_lbo, use_container_width=True)

    with ch2:
        st.markdown("**Equity Value Build-up**")
        colors = ["#3498db"] * hold_years + ["#1a1a2e"]
        fig_eq = go.Figure(go.Bar(x=res["years"], y=res["equity_schedule"],
                                   marker_color=colors,
                                   text=[f"${v:.0f}M" for v in res["equity_schedule"]],
                                   textposition="outside"))
        fig_eq.update_layout(xaxis_title="Year", yaxis_title="Equity ($M)",
                              plot_bgcolor="white", height=320)
        st.plotly_chart(fig_eq, use_container_width=True)

    st.markdown("**📊 IRR Sensitivity Table (Exit Multiple vs EBITDA Growth)**")
    exit_mults  = [8, 10, 12, 14, 16]
    growths     = [0.05, 0.08, 0.10, 0.15, 0.20]
    sens = {}
    for g in growths:
        row = {}
        for em in exit_mults:
            r = run_lbo(lbo_ebitda, entry_mult, debt_pct, interest_rate, g, em, hold_years, paydown_pct)
            row[f"{em}x"] = f"{r['irr']}%"
        sens[f"{int(g*100)}% growth"] = row
    st.dataframe(pd.DataFrame(sens).T, use_container_width=True)
