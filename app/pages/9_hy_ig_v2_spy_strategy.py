"""HY-IG v2 — The Strategy: Tournament Winner and Alternatives."""

import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.metrics import kpi_row
from components.sidebar import render_sidebar
from components.narrative import render_narrative, render_glossary_sidebar
from components.execution_panel import render_execution_panel

st.set_page_config(
    page_title="HY-IG v2 Strategy | AIG-RLIC+",
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

PAIR_ID = "hy_ig_v2_spy"
_RESULTS_DIR = Path(__file__).resolve().parents[2] / "results" / PAIR_ID

# --- Load winner summary ---
_winner_path = _RESULTS_DIR / "winner_summary.json"
_winner = {}
if _winner_path.exists():
    with open(_winner_path) as f:
        _winner = json.load(f)

# --- Page Header ---
st.title("The Strategy: Translating Signals to Action")
st.markdown(
    "*So what should an investor do with this information? We tested hundreds of "
    "strategy combinations to find the most robust answer.*"
)
st.markdown("---")

# ===================== HOW THE SIGNAL TRANSLATES =====================
st.markdown("### How the Signal Translates to Action")

st.markdown(
    "The tournament identified the most robust credit-signal strategies for equity "
    "allocation. The winning strategies share a common logic:"
)

st.markdown(
    "**Core principle: Risk-off when credit stress exceeds a data-driven threshold.**"
)

st.markdown("""
The strategy rules in plain language:
- **When the credit stress indicator is below the threshold** (indicating normal market conditions): Stay fully invested in stocks (long SPY).
- **When the credit stress indicator crosses above the threshold** (indicating elevated credit stress): Reduce equity exposure proportionally to signal strength.
- **When the indicator drops back below the threshold:** Return to full equity exposure.
""")

st.markdown("---")

# ===================== TOURNAMENT WINNER SPOTLIGHT =====================
st.markdown("### Tournament Winner: HMM Signal Strength (v2)")

with st.container(border=True):
    st.markdown(
        "**Strategy Rule in Plain English:** "
        "When the Hidden Markov Model assigns a stress probability greater than 50%, "
        "scale equity exposure inversely to the stress probability. At 50% stress, "
        "hold 50% equity. At 100% stress, hold 0% equity (full cash). "
        "This proportional approach avoids the binary all-in/all-out transitions "
        "of the v1 Long/Cash strategy."
    )

st.markdown("")

# Winner KPI cards
oos_sharpe = _winner.get("oos_sharpe", 1.274)
oos_return = _winner.get("oos_ann_return", 11.33)
max_dd = _winner.get("max_drawdown", -10.2)
turnover = _winner.get("annual_turnover", 3.78)

kpi_row(
    [
        {"label": "OOS Sharpe", "value": f"{oos_sharpe:.2f}", "delta": "vs 0.90 B&H"},
        {"label": "OOS Return", "value": f"+{oos_return:.1f}%", "delta": "annualized"},
        {
            "label": "Max Drawdown",
            "value": f"{max_dd:.1f}%",
            "delta": "vs -33.7% B&H",
            "delta_color": "inverse",
        },
        {"label": "Turnover", "value": f"~{turnover:.0f}/yr"},
        {"label": "Breakeven Cost", "value": "50 bps"},
    ]
)

st.markdown("---")

# ===================== TOURNAMENT LEADERBOARD =====================
st.markdown("### Tournament Leaderboard (Top 20)")

_tourn_path = _RESULTS_DIR / "tournament_results_20260410.csv"
if _tourn_path.exists():
    _tourn_df = pd.read_csv(_tourn_path)
    _valid = _tourn_df[_tourn_df["valid"] == True].copy()
    _non_bench = _valid[_valid["signal"] != "BENCHMARK"].copy()

    total_count = len(_tourn_df)
    valid_count = int(_tourn_df["valid"].sum())

    st.markdown(
        f"**{total_count:,} combinations tested** | "
        f"**{valid_count:,} valid** (OOS Sharpe >= 0, turnover <= 24x/yr, >= 30 trades)"
    )

    if len(_non_bench) > 0:
        _top20 = _non_bench.nlargest(20, "oos_sharpe")[
            ["signal", "threshold", "strategy", "lead_days",
             "oos_sharpe", "oos_ann_return", "max_drawdown", "win_rate", "n_trades"]
        ].reset_index(drop=True)
        _top20.index = _top20.index + 1
        _top20.index.name = "Rank"

        st.dataframe(
            _top20,
            use_container_width=True,
            column_config={
                "oos_sharpe": st.column_config.NumberColumn("OOS Sharpe", format="%.2f"),
                "oos_ann_return": st.column_config.NumberColumn("OOS Return %", format="%.1f%%"),
                "max_drawdown": st.column_config.NumberColumn("Max DD %", format="%.1f%%"),
                "win_rate": st.column_config.NumberColumn("Win Rate", format="%.3f"),
            },
        )

    # Also show benchmark
    _bench = _valid[_valid["signal"] == "BENCHMARK"]
    if len(_bench) > 0:
        st.caption(
            f"Benchmark (Buy-and-Hold SPY): Sharpe {_bench.iloc[0]['oos_sharpe']:.2f}, "
            f"Return {_bench.iloc[0]['oos_ann_return']:.1f}%, "
            f"Max DD {_bench.iloc[0]['max_drawdown']:.1f}%"
        )
else:
    st.info("Tournament results not yet available.")

st.markdown("---")

# ===================== EQUITY CURVES + DRAWDOWN =====================
st.markdown("### Equity Curves: Top Strategies vs. Buy-and-Hold")

load_plotly_chart(
    "equity_curves",
    fallback_text=(
        "Equity curves for top strategies vs buy-and-hold SPY (2018-2025). "
        "Will appear when visualization is complete."
    ),
    caption=(
        "Cumulative returns for the tournament winner compared to buy-and-hold SPY. "
        "The signal-strength strategy avoids major drawdowns while capturing most upside."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

st.markdown("### Drawdown Comparison")

load_plotly_chart(
    "drawdown_comparison",
    fallback_text=(
        "Drawdown comparison chart -- will appear when visualization is complete."
    ),
    caption=(
        "Peak-to-trough drawdown profiles. The Signal Strength strategy limits "
        f"maximum drawdown to {max_dd:.1f}%, compared to -33.7% for buy-and-hold."
    ),
    pair_id=PAIR_ID,
)

st.markdown("---")

# ===================== VALIDATION =====================
st.markdown("### Validation: Stress Tests, Signal Decay, and Walk-Forward")

val_tab1, val_tab2, val_tab3 = st.tabs(["Stress Tests", "Signal Decay", "Walk-Forward"])

_validation_dir = _RESULTS_DIR / "tournament_validation_20260410"

with val_tab1:
    st.markdown("#### Performance Across Stress Episodes")

    _stress_path = _validation_dir / "stress_tests.csv"
    if _stress_path.exists():
        _stress_df = pd.read_csv(_stress_path)
        st.dataframe(_stress_df, use_container_width=True, hide_index=True)
    else:
        st.info("Stress test results pending.")

    st.markdown(
        "**Honest assessment:** The HMM strategy excels at credit-driven crises (GFC) "
        "but does not protect against rate-driven selloffs (2022) where credit spreads "
        "widen alongside equities for different reasons."
    )

with val_tab2:
    st.markdown("#### Signal Decay with Execution Delay")

    _decay_path = _validation_dir / "signal_decay.csv"
    if _decay_path.exists():
        _decay_df = pd.read_csv(_decay_path)
        st.dataframe(_decay_df, use_container_width=True, hide_index=True)
    else:
        st.info("Signal decay results pending.")

    st.markdown(
        "Execution speed matters. The signal degrades with delay, reflecting the speed "
        "at which credit information is priced into equities. Same-day or next-day "
        "execution is recommended."
    )

with val_tab3:
    st.markdown("#### Walk-Forward Sharpe Ratio Over Time")

    _wf_path = _validation_dir / "walk_forward.csv"
    if _wf_path.exists():
        _wf_df = pd.read_csv(_wf_path)
        st.dataframe(_wf_df, use_container_width=True, hide_index=True)
    else:
        st.info("Walk-forward validation results pending.")

    st.markdown(
        "Walk-forward validation confirms that the strategy's outperformance is not "
        "an artifact of a single favorable period. The Sharpe ratio varies year to year "
        "but remains positive across the majority of test windows."
    )

st.markdown("---")

# ===================== DOWNLOAD TRADE LOG =====================
st.markdown("### Download Trading History")

_trade_log_path = _RESULTS_DIR / "winner_trade_log.csv"
if _trade_log_path.exists():
    _trade_df = pd.read_csv(_trade_log_path)
    if len(_trade_df) > 0:
        st.dataframe(_trade_df, use_container_width=True, hide_index=True)
        st.download_button(
            label="Download CSV",
            data=_trade_df.to_csv(index=False),
            file_name="hy_ig_v2_spy_trade_log.csv",
            mime="text/csv",
        )
        st.caption(f"{len(_trade_df):,} trades total")
    else:
        st.info("Trade log is empty -- re-run the pipeline.")
else:
    st.info("Trade log not yet generated -- run the pipeline.")

st.markdown("---")

# ===================== CAVEATS =====================
st.warning(
    """
**Important Caveats**

1. **Transaction costs matter.** All strategy metrics include 5 bps per round-trip trade. Breakeven cost is 50 bps -- robust, but not infinite.

2. **Execution delay degrades performance.** A 1-day delay reduces Sharpe by ~0.2. Timely execution is essential.

3. **The 2022 episode is a genuine weakness.** The strategy's credit signal widened modestly during 2022, but not enough to trigger a full risk-off position. This bear market was driven by rate hikes and valuation compression, not credit deterioration.

4. **Past performance is not indicative of future results.** Regime shifts, changes in market microstructure, or new central bank tools could alter the credit-equity relationship going forward.

5. **This is a risk management tool, not an alpha generator.** The primary value is in reducing drawdowns during stress periods rather than generating excess returns during calm periods.
    """
)

# ===================== EXECUTION PANEL =====================
render_execution_panel(PAIR_ID)

# --- Transition ---
st.markdown("---")
st.markdown(
    "For readers who want to understand exactly how we reached these conclusions -- "
    "or who want to replicate and extend the analysis -- the methodology section "
    "provides full details on data, methods, and diagnostics."
)

st.page_link(
    "pages/9_hy_ig_v2_spy_methodology.py",
    label="Continue to Methodology",
    icon="📐",
)

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 2000-01 to 2025-12"
    "</div>",
    unsafe_allow_html=True,
)
