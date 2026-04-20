"""Pair 14 — The Strategy: INDPRO → XLP Tournament Results.

Presents the tournament winner, leaderboard, equity curves, and
trading history download for the INDPRO × XLP pair.
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="INDPRO × XLP Strategy | AIG-RLIC+",
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

PAIR_ID = "indpro_xlp"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS_DIR = _REPO_ROOT / "results" / PAIR_ID

# ---------------------------------------------------------------------------
# Load winner summary
# ---------------------------------------------------------------------------
_winner = {}
_winner_path = _RESULTS_DIR / "winner_summary.json"
if _winner_path.exists():
    with open(_winner_path) as f:
        _winner = json.load(f)

_oos_sharpe = _winner.get("oos_sharpe", "N/A")
_bh_sharpe = _winner.get("bh_sharpe", "N/A")
_oos_return_pct = round(_winner.get("oos_ann_return", 0) * 100, 1) if _winner else "N/A"
_oos_dd_pct = round(_winner.get("oos_max_drawdown", 0) * 100, 1) if _winner else "N/A"
_bh_dd_pct = round(_winner.get("bh_max_drawdown", 0) * 100, 1) if _winner else "N/A"
_total_combos = _winner.get("total_combos", "N/A")
_valid_combos = _winner.get("valid_combos", "N/A")
_winner_signal = _winner.get("winner_signal", "N/A")
_winner_threshold = _winner.get("winner_threshold", "N/A")
_winner_strategy = _winner.get("winner_strategy", "N/A")
_winner_lead = _winner.get("winner_lead_months", "N/A")
_oos_start = _winner.get("oos_start", "2019-01")[:7]
_oos_win_rate = _winner.get("oos_win_rate", "N/A")
_oos_turnover = _winner.get("oos_annual_turnover", "N/A")

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
st.title("The Strategy: Translating IP Signals into XLP Timing")
st.markdown(
    f"*We tested {_total_combos:,} strategy combinations to find the most robust "
    f"way to time consumer staples exposure using industrial production signals.*"
    if isinstance(_total_combos, int) else
    "*We tested thousands of strategy combinations to find the most robust "
    "way to time consumer staples exposure using industrial production signals.*"
)
st.markdown("---")

# ===================== TOURNAMENT WINNER =====================
st.markdown(f"### Tournament Winner: IP Acceleration (Counter-Cyclical, Long/Short, L{_winner_lead})")

st.markdown(
    '<div class="spotlight-card">'
    "<b>Strategy Rule in Plain English:</b><br>"
    "Monitor the acceleration of Industrial Production (how quickly the monthly "
    "growth rate is changing). When IP acceleration is in its <b>upper quartile</b> "
    "(economy speeding up fast), hold a <b>short / underweight position</b> in XLP. "
    "When IP acceleration is below that threshold (growth slowing or contracting), "
    "hold a <b>long position</b> in XLP. Apply the signal with a 3-month lead to "
    "account for the publication lag and the time markets take to react."
    "</div>",
    unsafe_allow_html=True,
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("OOS Sharpe", str(_oos_sharpe), delta=f"vs {_bh_sharpe} B&H")
with col2:
    st.metric("OOS Return", f"{_oos_return_pct}%", delta="annualized")
with col3:
    st.metric("Max Drawdown", f"{_oos_dd_pct}%", delta=f"vs {_bh_dd_pct}% B&H", delta_color="inverse")
with col4:
    st.metric("Combinations", f"{_total_combos:,}" if isinstance(_total_combos, int) else str(_total_combos))
with col5:
    st.metric("Valid", f"{_valid_combos:,}" if isinstance(_valid_combos, int) else str(_valid_combos))

st.markdown("---")

# ===================== TOURNAMENT SCATTER =====================
st.markdown("### Tournament Results: All Combinations")

load_plotly_chart(
    "indpro_xlp_tournament_scatter",
    fallback_text=(
        "Tournament scatter: OOS Sharpe vs annual turnover for all combinations. "
        "Expected at: output/charts/indpro_xlp/plotly/indpro_xlp_tournament_scatter.json"
    ),
    caption=(
        "What this shows: each dot is one strategy combination. Color indicates max "
        "drawdown (green = shallow, red = deep). Stars mark the top 5. "
        "Diamond is buy-and-hold XLP benchmark."
    ),
    pair_id=PAIR_ID,
)

# ===================== LEADERBOARD =====================
st.markdown("### Tournament Leaderboard")

_tourn_path = _RESULTS_DIR / f"tournament_results_20260420.csv"
if _tourn_path.exists():
    tdf = pd.read_csv(_tourn_path)
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
            "OOS Return": f"{r['oos_ann_return']:+.1f}%" if "oos_ann_return" in r.index else "—",
            "Max DD": f"{r['max_drawdown']:.1f}%",
            "Turnover": f"{r['annual_turnover']:.1f}/yr",
            "Win Rate": f"{r['win_rate']:.1%}",
        })
    if len(bh) > 0:
        b = bh.iloc[0]
        display_rows.append({
            "Rank": "—",
            "Signal": "Buy-and-Hold XLP",
            "Threshold": "—",
            "Strategy": "Benchmark",
            "Lead": "—",
            "OOS Sharpe": round(b["oos_sharpe"], 2),
            "OOS Return": f"{b['oos_ann_return']:+.1f}%" if "oos_ann_return" in b.index else "—",
            "Max DD": f"{b['max_drawdown']:.1f}%",
            "Turnover": "0/yr",
            "Win Rate": f"{b['win_rate']:.1%}",
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
        f"Ranked by out-of-sample Sharpe ({_oos_start}–2025). "
        f"Note: strategies ending in '_counter' use countercyclical orientation "
        f"(hold XLP when IP signal is LOW)."
    )
else:
    st.info("Tournament results not found. Run scripts/pair_pipeline_indpro_xlp.py to generate.")

st.markdown("---")

# ===================== EQUITY CURVES =====================
st.markdown("### Equity Curves: Top Strategies vs. Buy-and-Hold XLP")

load_plotly_chart(
    "indpro_xlp_equity_curves",
    fallback_text=(
        "Equity curves for top strategies vs buy-and-hold XLP. "
        "Expected at: output/charts/indpro_xlp/plotly/indpro_xlp_equity_curves.json"
    ),
    caption=(
        "What this shows: cumulative returns from $1 invested at start of OOS period. "
        "Top IP acceleration strategies in countercyclical orientation aim to "
        "hold XLP during defensive regimes and reduce exposure during expansions."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ===================== DRAWDOWN =====================
st.markdown("### Drawdown Comparison")

load_plotly_chart(
    "indpro_xlp_drawdown",
    fallback_text=(
        "Drawdown chart: winner strategy vs buy-and-hold XLP. "
        "Expected at: output/charts/indpro_xlp/plotly/indpro_xlp_drawdown.json"
    ),
    caption=(
        "What this shows: peak-to-trough drawdown during the OOS period. "
        "The green fill shows the winner strategy's drawdown; gray fill shows "
        "buy-and-hold XLP. Shallower drawdowns = more defensive positioning."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ===================== ROLLING SHARPE =====================
st.markdown("### Walk-Forward Rolling Sharpe")

load_plotly_chart(
    "indpro_xlp_walk_forward",
    fallback_text=(
        "Walk-forward rolling Sharpe: winner vs buy-and-hold XLP. "
        "Expected at: output/charts/indpro_xlp/plotly/indpro_xlp_walk_forward.json"
    ),
    caption=(
        "What this shows: 24-month rolling Sharpe ratio for the winner strategy "
        "and buy-and-hold XLP during the OOS period. Periods where the winner "
        "strategy (green) exceeds the benchmark (gray) confirm persistent edge."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ===================== DOWNLOAD TRADING HISTORY =====================
st.markdown("### Download Trading History")

_trade_path = _RESULTS_DIR / "winner_trade_log.csv"
if _trade_path.exists():
    trade_df = pd.read_csv(_trade_path)
    st.markdown(
        f"Download the monthly trading history for the tournament winner: "
        f"**{_winner_signal}** / **{_winner_threshold}** / **{_winner_strategy}** / "
        f"Lead {_winner_lead} months"
    )
    csv = trade_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="indpro_xlp_winner_trading_history.csv",
        mime="text/csv",
    )
    with st.expander("Preview (first 20 rows)"):
        st.dataframe(trade_df.head(20), use_container_width=True, hide_index=True)
else:
    st.info("Trading history not found. Run scripts/pair_pipeline_indpro_xlp.py to generate.")

st.markdown("---")

# ===================== CAVEATS =====================
st.warning(
    """
    **Important Caveats**

    1. **Countercyclical orientation.** The winning strategy bets *against* high IP
       acceleration — it holds XLP when factories are slowing down. This is the
       opposite of the INDPRO × SPY strategy. Investors must not mix the two signals.

    2. **Publication lag.** IP data is released ~6 weeks after the reference month.
       The 3-month lead in the winning strategy accounts for this delay.

    3. **Long/short implementation.** The winning strategy uses a long/short
       orientation. Short-selling XLP requires a brokerage account with margin
       privileges and incurs borrowing costs not reflected in these results.

    4. **High turnover (≈10x/yr).** Monthly rebalancing is required. Transaction
       costs and slippage will reduce net returns; verify robustness with the
       transaction cost sensitivity table.

    5. **COVID outlier.** April 2020 IP contraction (-12.7% MoM) is extreme.
       The model parameters may be distorted by this observation.

    6. **XLP sample starts 1998.** Only 27 years of history — less than the
       INDPRO × SPY pair's 35-year history. OOS period (84 months) is substantial
       but one full cycle remains desirable for confirmation.
    """
)

# ===================== TRANSITION =====================
st.markdown("---")
st.page_link(
    "pages/14_indpro_xlp_methodology.py",
    label="Continue to Methodology",
    icon="📐",
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    "Data: INDPRO (FRED) + XLP (Yahoo Finance) | "
    "OOS period: 2019-01 to 2025-12"
)
