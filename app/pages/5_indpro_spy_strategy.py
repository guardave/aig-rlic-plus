"""Finding 2 — The Strategy: INDPRO → SPY Tournament Results."""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.metrics import kpi_row
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar
from components.execution_panel import render_execution_panel

st.set_page_config(
    page_title="IP Strategy | AIG-RLIC+",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_sidebar()
render_glossary_sidebar()

# --- Page Header ---
st.title("The Strategy: Translating IP Signals to Action")
st.markdown(
    "*We tested 1,666 strategy combinations to find the most robust way to trade on "
    "industrial production signals.*"
)
st.markdown("---")

# ===================== TOURNAMENT WINNER =====================
st.markdown("### Tournament Winner: IP 3-Month Momentum (Long/Cash, 6M Lead)")

st.markdown(
    '<div class="spotlight-card">'
    "<b>Strategy Rule in Plain English:</b><br>"
    "When the 3-month change in Industrial Production is above its historical 75th "
    "percentile (strong momentum), stay fully invested in SPY. Otherwise, move to cash. "
    "Apply the signal with a 6-month lead to account for IP's publication lag and "
    "the time it takes for the economy to respond."
    "</div>",
    unsafe_allow_html=True,
)

kpi_row([
    {"label": "OOS Sharpe", "value": "1.10", "delta": "vs 0.90 B&H"},
    {"label": "OOS Return", "value": "+7.7%", "delta": "vs +14.8% B&H"},
    {"label": "Max Drawdown", "value": "-8.1%", "delta": "vs -23.9% B&H", "delta_color": "inverse"},
    {"label": "Combinations", "value": "1,666"},
    {"label": "Valid", "value": "1,150"},
])

st.markdown("---")

# ===================== TOURNAMENT SCATTER =====================
st.markdown("### Tournament Results: All Combinations")

load_plotly_chart(
    "indpro_spy_tournament_scatter",
    fallback_text="Tournament scatter: OOS Sharpe vs turnover",
    caption=(
        "Each dot is one strategy combination. Color indicates max drawdown "
        "(green = shallow, red = deep). Stars mark the top 5. Diamond is buy-and-hold."
    ),
    pair_id="indpro_spy",
)

# ===================== LEADERBOARD =====================
st.markdown("### Tournament Leaderboard")

results_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..",
    "results", "indpro_spy", "tournament_results_20260314.csv"
)

if os.path.exists(results_path):
    tdf = pd.read_csv(results_path)
    valid = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
    top10 = valid.nlargest(10, "oos_sharpe")
    bh = tdf[tdf["signal"] == "BENCHMARK"]

    display_rows = []
    for rank, (_, r) in enumerate(top10.iterrows(), 1):
        display_rows.append({
            "Rank": rank,
            "Signal": r["signal"],
            "Threshold": r["threshold"],
            "Strategy": r["strategy"],
            "Lead": f"{int(r['lead_months'])}M",
            "OOS Sharpe": round(r["oos_sharpe"], 2),
            "OOS Return": f"{r["oos_ann_return"]:+.1f}%" if "oos_ann_return" in r.index else "—",
            "Max DD": f"{r['max_drawdown']:.1f}%",
            "Turnover": f"{r['annual_turnover']:.1f}/yr",
        })
    if len(bh) > 0:
        b = bh.iloc[0]
        display_rows.append({
            "Rank": "-",
            "Signal": "Buy-and-Hold SPY",
            "Threshold": "-",
            "Strategy": "Benchmark",
            "Lead": "-",
            "OOS Sharpe": round(b["oos_sharpe"], 2),
            "OOS Return": f"{b["oos_ann_return"]:+.1f}%" if "oos_ann_return" in b.index else "—",
            "Max DD": f"{b['max_drawdown']:.1f}%",
            "Turnover": "0/yr",
        })

    st.dataframe(
        pd.DataFrame(display_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "OOS Sharpe": st.column_config.NumberColumn("OOS Sharpe", format="%.2f"),
        },
    )

    st.caption(
        f"**{len(tdf):,} combinations tested** | "
        f"**{len(valid):,} valid** (OOS Sharpe > 0, turnover < 24x/yr) | "
        f"Ranked by out-of-sample Sharpe (2018-2025)"
    )
else:
    st.info("Tournament results not found.")

st.markdown("---")

# ===================== EQUITY CURVES =====================
st.markdown("### Equity Curves: Top Strategies vs. Buy-and-Hold")

load_plotly_chart(
    "indpro_spy_equity_curves",
    fallback_text="Equity curves for top strategies vs buy-and-hold",
    caption=(
        "Cumulative returns from $1 invested at start of OOS period (2018). "
        "Top IP momentum strategies avoid the worst drawdowns while capturing most upside."
    ),
    pair_id="indpro_spy",
)

st.markdown("---")

# ===================== DOWNLOAD TRADING HISTORY =====================
st.markdown("### Download Trading History")

from components.trade_history import reconstruct_winner_history

history = reconstruct_winner_history("indpro_spy")
if history is not None:
    st.markdown(
        f"Download the daily trading history for the tournament winner: "
        f"**{history.attrs.get('winner_signal', '?')}** / "
        f"**{history.attrs.get('winner_threshold', '?')}** / "
        f"**{history.attrs.get('winner_strategy', '?')}** / "
        f"Lead {history.attrs.get('winner_lead', '?')}"
    )
    csv = history.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="indpro_spy_winner_trading_history.csv",
        mime="text/csv",
    )
    with st.expander("Preview (first 20 rows)"):
        st.dataframe(history.head(20), use_container_width=True, hide_index=True)
else:
    st.info("Trading history reconstruction not available for this pair.")

st.markdown("---")

# ===================== CAVEATS =====================
st.warning(
    """
    **Important Caveats**

    1. **Publication lag matters.** IP data is released ~6 weeks after the reference month.
       The 6-month lead in the winning strategy accounts for this delay.

    2. **Monthly frequency limits responsiveness.** IP signals update monthly;
       fast-moving markets can gap before the next data point.

    3. **COVID outlier.** The April 2020 IP drop (-12.7% MoM) is unprecedented
       and may distort model estimates.

    4. **This is a trend signal, not a timing tool.** IP momentum tells you about
       the direction of the economy, not about short-term market moves.
    """
)

# ===================== EXECUTION PANEL =====================
render_execution_panel("indpro_spy")

# --- Transition ---
st.markdown("---")
st.page_link("pages/5_indpro_spy_methodology.py", label="Continue to Methodology", icon="📐")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 1990-01 to 2025-12"
    "</div>",
    unsafe_allow_html=True,
)
