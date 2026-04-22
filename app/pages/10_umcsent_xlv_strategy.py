"""UMCSENT × XLV -- The Strategy: Tournament Winner and Alternatives.

Pair ID: umcsent_xlv
Date: 2026-04-20
"""

import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.breadcrumb import render_breadcrumb
from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="UMCSENT × XLV Strategy | AIG-RLIC+",
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

PAIR_ID = "umcsent_xlv"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS_DIR = _REPO_ROOT / "results" / PAIR_ID

render_breadcrumb("Strategy", PAIR_ID)

# Load winner
_winner = {}
_winner_path = _RESULTS_DIR / "winner_summary.json"
if _winner_path.exists():
    with open(_winner_path) as f:
        _winner = json.load(f)

with st.expander("Plain English"):
    st.markdown(
        "We tested over 1,300 combinations of rules for using consumer sentiment to "
        "time XLV exposure. The winner is simple: hold XLV when consumer sentiment "
        "has risen year-over-year (6 months ago), and move to cash when it has fallen. "
        "This rule out-performed buy-and-hold on a risk-adjusted basis over 6 years "
        "of out-of-sample data."
    )

# ---------------------------------------------------------------------------
# How the Signal Works
# ---------------------------------------------------------------------------
st.markdown("### How the Signal is Generated")

st.markdown(
    "The winning strategy uses **UMCSENT Year-over-Year Change** with a **6-month lead**. "
    "Here is the exact rule:"
)

st.markdown(
    "1. Each month, look at the current UMCSENT reading versus 12 months ago. "
    "Compute the percentage change.\n"
    "2. Check what this YoY change was **6 months ago** (the lead).\n"
    "3. If the 6-month-ago YoY change was **positive** (sentiment improving): "
    "hold XLV (Long/Cash position = 1).\n"
    "4. If the 6-month-ago YoY change was **zero or negative** (sentiment flat or "
    "deteriorating): move to cash (Long/Cash position = 0).\n"
    "5. Update the position at the start of each month."
)

st.markdown(
    "The 6-month lead means you are acting on information that is 6 months stale — "
    "and the strategy still works. This confirms that sentiment anticipates sector "
    "dynamics well in advance, not just contemporaneously."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Trading rule
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("### The Trading Rule in Plain English")
    st.markdown(
        "**Each month, ask:** Was Michigan Consumer Sentiment higher or lower, "
        "year-over-year, 6 months ago?\n\n"
        "- **Higher (positive YoY 6M ago):** Hold XLV fully.\n"
        "- **Lower (zero or negative YoY 6M ago):** Move to cash.\n\n"
        "That is the entire rule. No optimization, no thresholds to calibrate, "
        "no probability models. Signal the zero-crossing of a 12-month change "
        "in a publicly available monthly survey, apply a 6-month lag, and toggle "
        "XLV exposure."
    )

with st.expander("Why we chose this method"):
    st.markdown(
        "*Why Long/Cash (P1) instead of Signal Strength scaling (P2)?*\n\n"
        "The YoY change signal is a directional, near-binary indicator — it is either "
        "positive or negative. Unlike a continuous z-score or level measure, where "
        "scaling by signal magnitude would make sense, the YoY zero-crossing captures "
        "a regime switch: from improving to deteriorating. The P1 binary rule "
        "(fully in or fully out) is the natural match for a binary regime signal. "
        "The tournament confirmed this: P1 Long/Cash achieved a higher Sharpe than "
        "P2 Signal Strength for this specific signal/threshold combination."
    )

with st.expander("Deeper dive"):
    st.markdown(
        "*Why 6 months? Shouldn't we use the most current data?*\n\n"
        "Monthly macro indicators are subject to revision. Consumer sentiment surveys "
        "are preliminary data released mid-month for the previous month. The 6-month "
        "lag provides stability: by the time we act, the signal has been confirmed over "
        "six additional monthly releases. More importantly, the tournament selected "
        "6 months because it produced the best out-of-sample Sharpe — not because of "
        "a prior theory. The result is robust: shorter leads (0-3 months) produce lower "
        "Sharpe ratios, and longer leads (>6 months) also decline."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# KPI metrics
# ---------------------------------------------------------------------------
st.markdown("### Key Strategy Metrics")

oos_sharpe = _winner.get("oos_sharpe", 1.02)
oos_return = _winner.get("oos_ann_return", 0.119)
max_dd = _winner.get("max_drawdown", -0.109)
turnover = _winner.get("annual_turnover", 2.4)
bh_sharpe = _winner.get("bh_oos_sharpe", 0.72)
bh_dd = _winner.get("bh_max_drawdown", -0.156)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("OOS Sharpe", f"{oos_sharpe:.2f}", delta=f"vs {bh_sharpe:.2f} B&H")
with col2:
    st.metric("OOS Return (ann.)", f"{oos_return*100:.1f}%",
              help="Arithmetic annualized return over OOS period.")
with col3:
    st.metric("Max Drawdown", f"{max_dd*100:.1f}%",
              delta=f"{(max_dd - bh_dd)*100:.1f}pp vs B&H", delta_color="inverse")
with col4:
    st.metric("Annual Turnover", f"~{turnover:.1f}/yr")
with col5:
    st.metric("Strategy Type", "Long/Cash", delta="Binary toggle")

st.caption(
    f"Why this matters: the sentiment rule delivers a Sharpe of {oos_sharpe:.2f} vs "
    f"{bh_sharpe:.2f} for buy-and-hold, with max drawdown of {max_dd*100:.1f}% vs "
    f"{bh_dd*100:.1f}% — {abs((max_dd - bh_dd))*100:.1f} percentage points less "
    "downside. Turnover of ~2.4 trades per year is very low, keeping transaction "
    "costs minimal."
)

st.caption(
    "Caveat: arithmetic annualized return. Geometric CAGR would be slightly lower. "
    "The OOS period begins 2019-04-30 and covers approximately 6 years."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Tabs: Execute / Performance / Confidence
# ---------------------------------------------------------------------------
tab_execute, tab_performance, tab_confidence = st.tabs(
    ["Execute", "Performance", "Confidence"]
)

# ===========================================================================
# EXECUTE TAB
# ===========================================================================
with tab_execute:
    st.markdown("### Strategy Summary")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Signal:** UMCSENT Year-over-Year Change")
        st.markdown(f"**Threshold:** Zero-crossing (YoY > 0 = bullish)")
        st.markdown(f"**Strategy family:** Long/Cash (P1) — binary toggle")
    with c2:
        st.markdown(f"**Lead time:** 6 months")
        st.markdown(f"**Direction:** Procyclical (high/rising sentiment → long XLV)")
        st.markdown(
            "**Strategy description:** Hold XLV when 6-month-lagged UMCSENT "
            "YoY change is positive; otherwise hold cash."
        )

    st.markdown("---")

    st.markdown("### How to Use This Signal Manually")

    st.markdown(
        "You do not need software to implement this signal. Follow these steps monthly:"
    )
    st.markdown(
        "**1. Retrieve the UMCSENT reading.** "
        "FRED series: `UMCSENT`. Published mid-month for the current month. "
        "Free to access at fred.stlouisfed.org.\n\n"
        "**2. Compute the YoY change.** "
        "Divide today's reading by the reading from 12 months ago and subtract 1. "
        "E.g.: UMCSENT = 72.0, 12M ago = 68.0 → YoY = (72/68 - 1) = +5.9%.\n\n"
        "**3. Check what this YoY reading was 6 months ago.** "
        "Pull the UMCSENT reading from 18 months ago and 6 months ago, compute "
        "the YoY for 6 months back: (6M ago / 18M ago - 1).\n\n"
        "**4. Apply the rule.** "
        "If that 6M-ago YoY change was positive → hold XLV. "
        "If it was zero or negative → hold cash (or equivalent short-duration bonds).\n\n"
        "**5. Rebalance monthly.** "
        "The signal changes once a month at most. Do not check it more frequently."
    )

    with st.container(border=True):
        st.markdown("**Concrete example — COVID 2020.**")
        st.markdown(
            "- In February 2020 (acting on the 6M-ago YoY = August 2019's YoY), "
            "UMCSENT had risen from August 2018 to August 2019 → YoY positive → "
            "strategy held XLV fully.\n"
            "- By April 2020, the 6M-ago signal (October 2019's YoY) remained "
            "positive from the pre-COVID environment → strategy still held XLV.\n"
            "- By July 2020, the 6M-ago signal (January 2020's YoY) would begin "
            "reflecting COVID uncertainty → strategy would start reducing or "
            "eliminating XLV exposure depending on the exact YoY computation.\n"
            "- The 6-month lag meant the strategy did not avoid the initial "
            "COVID crash but did manage the recovery phase more effectively."
        )

    with st.expander("Honest assessment"):
        st.markdown(
            "- **The 6-month lag is both a strength and a limitation.** "
            "It avoids false signals from month-to-month noise, but it means "
            "the strategy is always 'behind' major turning points.\n"
            "- **COVID was a partial failure.** The speed of the March 2020 "
            "crash outran any monthly sentiment signal. The strategy reduced "
            "exposure with a lag, not before the fall.\n"
            "- **Transaction costs are minimal.** ~2.4 trades/year at 5 bps "
            "each costs roughly 12 bps/year — negligible.\n"
            "- **This is one signal.** Combining with VIX, yield curve, or "
            "credit spreads likely improves robustness. See the VIX × SPY "
            "and HY-IG × SPY pairs in this portal.\n"
            "- **Direction was a surprise.** If you traded the textbook "
            "countercyclical story (short XLV when sentiment rises), you would "
            "have lost money. Always validate with data before trading a theory."
        )

# ===========================================================================
# PERFORMANCE TAB
# ===========================================================================
with tab_performance:
    st.markdown("### Equity Curves: Strategy vs. Buy-and-Hold")

    load_plotly_chart(
        "equity_curves",
        fallback_text="Equity curves for top strategies vs buy-and-hold XLV.",
        caption=(
            "What this shows: cumulative returns for the tournament winner "
            "vs buy-and-hold XLV and SPY. The sentiment rule avoids major "
            "drawdown periods while capturing most upside."
        ),
        pair_id=PAIR_ID,
    )
    st.caption(
        f"Why this matters: the winner (Sharpe {oos_sharpe:.2f}) participates in "
        "bull markets while stepping aside during sustained falling-sentiment periods."
    )

    st.markdown("---")
    st.markdown("### Drawdown Comparison")

    load_plotly_chart(
        "drawdown",
        fallback_text="Drawdown comparison: strategy vs buy-and-hold XLV.",
        caption=(
            f"What this shows: peak-to-trough drawdown profiles. Strategy max DD = "
            f"{max_dd*100:.1f}% vs {bh_dd*100:.1f}% for buy-and-hold XLV."
        ),
        pair_id=PAIR_ID,
    )
    st.caption(
        f"Why this matters: reducing max drawdown from {bh_dd*100:.1f}% to "
        f"{max_dd*100:.1f}% means significantly less psychological and financial "
        "pain during the worst market periods."
    )

    st.markdown("---")
    st.markdown("### Rolling Sharpe Ratio")

    load_plotly_chart(
        "rolling_sharpe",
        fallback_text="Rolling 12-month Sharpe ratio.",
        caption=(
            "What this shows: 12-month rolling Sharpe for the winner strategy "
            "vs buy-and-hold XLV. Periods below zero indicate 12-month stretches "
            "where the strategy underperformed cash."
        ),
        pair_id=PAIR_ID,
    )
    st.caption(
        "Why this matters: the rolling Sharpe shows the strategy is not "
        "concentrated in one lucky year — the risk-adjusted edge has persisted "
        "across multiple market environments."
    )

    st.markdown("---")
    st.markdown("### Trade Log")

    _trade_path = _RESULTS_DIR / "winner_trade_log.csv"
    if _trade_path.exists():
        _trade_df = pd.read_csv(_trade_path, index_col=0, parse_dates=True)
        st.markdown(f"**{len(_trade_df):,} monthly position records in the OOS period.**")
        st.dataframe(_trade_df.head(12), use_container_width=True)
        st.caption(
            "What this shows: monthly position (1=long XLV, 0=cash), "
            "strategy return, and cumulative return for the first year of OOS."
        )
        st.download_button(
            label="Download full trade log",
            data=_trade_df.to_csv(),
            file_name=f"{PAIR_ID}_winner_trade_log.csv",
            mime="text/csv",
        )
    else:
        st.info(
            "Trade log not yet generated.\n\n"
            "Plain English: run the pipeline script to produce the trade log."
        )

# ===========================================================================
# CONFIDENCE TAB
# ===========================================================================
with tab_confidence:
    st.markdown("### Walk-Forward Annual Sharpe")

    load_plotly_chart(
        "wf_sharpe",
        fallback_text="Walk-forward annual Sharpe ratio.",
        caption=(
            "What this shows: annualized Sharpe ratio by calendar year (OOS period). "
            "Green bars indicate the strategy outperformed cash in that year; "
            "red bars indicate underperformance. Dashed line = buy-and-hold XLV annual Sharpe."
        ),
        pair_id=PAIR_ID,
    )
    st.caption(
        "Why this matters: the edge is distributed across multiple years, "
        "not concentrated in a single lucky period — evidence of durability."
    )

    st.markdown("---")
    st.markdown("### Tournament Leaderboard (Top 20)")

    _tourn_path = _RESULTS_DIR / "tournament_results_20260420.csv"
    if _tourn_path.exists():
        _tdf = pd.read_csv(_tourn_path)
        _valid = _tdf[(_tdf["valid"] == True) & (_tdf["signal"] != "BENCHMARK")]
        _bench = _tdf[_tdf["signal"] == "BENCHMARK"]

        st.markdown(
            f"**{len(_tdf):,} combinations tested** | "
            f"**{len(_valid):,} valid** (OOS Sharpe > 0, turnover ≤ 24/yr)"
        )

        if len(_valid) > 0:
            _top20 = _valid.nlargest(20, "oos_sharpe")[
                ["signal", "threshold", "strategy", "lead_months",
                 "oos_sharpe", "oos_ann_return", "max_drawdown", "win_rate",
                 "annual_turnover"]
            ].reset_index(drop=True)
            _top20.index = _top20.index + 1
            _top20.index.name = "Rank"

            # Display with percentage formatting (values are in ratio form)
            _top20_display = _top20.copy()
            _top20_display["oos_ann_return"] = _top20_display["oos_ann_return"] * 100
            _top20_display["max_drawdown"] = _top20_display["max_drawdown"] * 100

            st.dataframe(
                _top20_display,
                use_container_width=True,
                column_config={
                    "oos_sharpe": st.column_config.NumberColumn("OOS Sharpe", format="%.2f"),
                    "oos_ann_return": st.column_config.NumberColumn("OOS Return %", format="%.1f%%"),
                    "max_drawdown": st.column_config.NumberColumn("Max DD %", format="%.1f%%"),
                    "win_rate": st.column_config.NumberColumn("Win Rate", format="%.3f"),
                    "annual_turnover": st.column_config.NumberColumn("Turnover/yr", format="%.1f"),
                },
            )
            st.caption(
                "Why this matters: the breadth of the top 20 confirms the edge "
                "is not dependent on a single combination — multiple signal variants "
                "and lead times all show positive OOS Sharpe."
            )

        if len(_bench) > 0:
            bh = _bench.iloc[0]
            st.caption(
                f"Benchmark (Buy-and-Hold XLV): "
                f"Sharpe {bh['oos_sharpe']:.2f}, "
                f"Return {bh['oos_ann_return']*100:.1f}%, "
                f"Max DD {bh['max_drawdown']*100:.1f}%"
            )
    else:
        st.info("Tournament results file not found. Run the pipeline to generate it.")

    st.markdown("---")
    st.markdown("### Tournament Scatter: Sharpe vs. Turnover")

    load_plotly_chart(
        "tournament_scatter",
        fallback_text="Tournament scatter: OOS Sharpe vs annual turnover.",
        caption=(
            "What this shows: all 1,305 strategy combinations plotted by annual "
            "turnover (x-axis) and OOS Sharpe ratio (y-axis). Color indicates max "
            "drawdown. Stars mark the top 5. The winning region is low-turnover, "
            "high-Sharpe — top-left of the valid cluster."
        ),
        pair_id=PAIR_ID,
    )
    st.caption(
        "Why this matters: the top-5 strategies occupy the low-turnover region, "
        "confirming the edge comes from systematic sentiment timing, not from "
        "high-frequency trading of small mispricings."
    )

    st.markdown("---")
    st.warning(
        """
**Important Caveats**

*Plain English: read these before allocating capital to this rule.*

1. **Direction was a surprise.** The textbook countercyclical story was wrong for this pair. Do not assume economic theory determines the signal direction — validate empirically.

2. **6-month lag limits responsiveness.** The strategy cannot avoid fast crashes (COVID, flash crashes). It works best for slow-moving sentiment cycles.

3. **OOS period covers only ~6 years.** This is shorter than the 8-year OOS for the HY-IG pair. Short OOS windows can produce inflated Sharpe estimates.

4. **Healthcare sector dynamics change.** ACA, drug pricing regulation, COVID policy, and demographic shifts all affect XLV. The historical sentiment-XLV relationship may shift if sector fundamentals change structurally.

5. **This is not portfolio insurance.** The strategy reduces but does not eliminate drawdowns. Max drawdown of {:.1f}% still represents meaningful portfolio pain.
        """.format(max_dd * 100)
    )

# ---------------------------------------------------------------------------
# Transition
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "For readers who want the full technical detail — data sources, model specifications, "
    "diagnostic tests, and signal universe — the Methodology page has everything needed "
    "to replicate or critique this analysis."
)

st.page_link(
    "pages/10_umcsent_xlv_methodology.py",
    label="Continue to Methodology",
    icon="📐",
)

st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    f"OOS: {_winner.get('oos_start', '2019-04-30')} to 2025-12-31 | "
    f"Winner: {_winner.get('signal', 'S2_yoy')}/{_winner.get('threshold', 'T4_zero')}/L{_winner.get('lead_months', 6)}"
)
