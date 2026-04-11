"""HY-IG v2 -- The Strategy: Tournament Winner and Alternatives."""

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

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
st.title("The Strategy: Translating Signals to Action")
st.markdown(
    "*So what should an investor do with this information? We tested hundreds of "
    "strategy combinations to find the most robust answer.*"
)
st.markdown("---")

# ---------------------------------------------------------------------------
# RULE-FIRST: Plain English rule IMMEDIATELY at top
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("### The Trading Rule in Plain English")
    st.markdown(
        "A Hidden Markov Model continuously estimates the probability that markets are "
        "in a \"stress\" regime. **When that stress probability exceeds 50%, the strategy "
        "scales down equity exposure proportionally to the severity of the signal** -- at "
        "50% stress probability it holds less stock; at 100% stress probability it would "
        "hold no stock at all. When stress probability drops back below 50%, the strategy "
        "returns to full equity exposure. This graduated approach (called **Signal Strength**, "
        "or P2) avoids the all-or-nothing whipsaw of a simple on/off switch."
    )

with st.expander("Why scale positions instead of switching all-in or all-out?"):
    st.markdown(
        "A simple on/off strategy (fully invested or fully in cash) can suffer from "
        "\"whipsaw\" -- rapidly alternating between in and out of the market when the "
        "signal hovers near its threshold. This generates transaction costs and tax events "
        "with no benefit.\n\n"
        "The Signal Strength (P2) approach scales the equity position proportionally to "
        "the signal: if the HMM says there is a 60% chance of stress, the strategy holds "
        "only 40% in stocks and 60% in cash. This smooths transitions, reduces turnover, "
        "and allows the strategy to partially capture upside even when some stress is present.\n\n"
        "The tournament tested four strategy types: (P1) Long/Cash -- fully in or fully out; "
        "(P2) Signal Strength -- proportional scaling; (P3) Long/Short -- shorting stocks "
        "during stress; and (P4) Collar -- using options to hedge. P2 won because it "
        "delivered the best risk-adjusted return after transaction costs."
    )

with st.expander("What is a z-score, and why do we use one?"):
    st.markdown(
        "A z-score measures how unusual a current value is compared to its recent history. "
        "A z-score of 0 means the spread is at its historical average. A z-score of +2 "
        "means the spread is 2 standard deviations above average -- a relatively rare "
        "condition that historically has occurred less than 5% of the time.\n\n"
        "We use z-scores rather than raw spread levels because the \"normal\" level of "
        "credit spreads changes over time. A 400 bps spread in 2005 (when spreads had been "
        "tightening for years) meant something different than a 400 bps spread in 2010 "
        "(when spreads were coming down from crisis peaks). The z-score adjusts for this by "
        "comparing today's spread to its recent window, providing a context-aware measure "
        "of stress."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Key Strategy Metrics  (Metric Interpretation Rule)
# ---------------------------------------------------------------------------
st.markdown("### Key Strategy Metrics")

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

st.caption(
    "The credit-signal strategy delivered comparable returns to buy-and-hold but with "
    "dramatically less pain. Its worst peak-to-trough decline was -10.2%, versus -34% "
    "for an investor who simply held SPY through the same period. The Sharpe ratio of "
    f"{oos_sharpe:.2f} (versus 0.90 for buy-and-hold) means each unit of risk taken was "
    "rewarded with roughly 40% more return. The strategy only needed about 4 trades per "
    "year, and it would remain profitable even if transaction costs were 10x higher than "
    "our 5 bps assumption."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Where the Strategy Adds Value -- and Where It Does Not
# ---------------------------------------------------------------------------
st.markdown("### Where the Strategy Adds Value -- and Where It Does Not")

st.markdown(
    "The primary value of the credit signal is **drawdown reduction during stress "
    "periods**, not alpha generation during calm markets. During the long stretches "
    "when credit conditions are normal, the strategy is fully invested and performs "
    "identically to buy-and-hold. Its edge comes from avoiding the worst of the "
    "drawdowns when credit markets signal stress."
)

st.markdown(
    "This means:\n"
    "- **It will underperform in V-shaped recoveries.** If the market crashes and "
    "bounces back quickly (as in COVID), the strategy may exit at or near the bottom "
    "and re-enter after some of the recovery has already occurred.\n"
    "- **It excels in prolonged bear markets.** The GFC lasted roughly 18 months "
    "peak-to-trough. A strategy that exited early captured most of the avoided "
    "drawdown.\n"
    "- **It is largely inert during calm periods.** This is a feature, not a bug -- "
    "the strategy avoids generating trading costs and tax events when the credit "
    "signal has little to say."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Tournament Leaderboard
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Equity Curves + Drawdown
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Validation: Stress Tests, Signal Decay, Walk-Forward
# ---------------------------------------------------------------------------
st.markdown("### Validation: Stress Tests, Signal Decay, and Walk-Forward")

val_tab1, val_tab2, val_tab3 = st.tabs(
    ["Stress Tests", "Signal Decay", "Walk-Forward"]
)

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
        "**Honest assessment:** The HMM strategy excels at credit-driven crises "
        "(GFC) but does not protect against rate-driven selloffs (2022) where credit "
        "spreads widen alongside equities for different reasons."
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
        "**What this means:** Execution speed matters. Performance decreases with "
        "longer delays, reflecting the speed at which credit information gets priced "
        "into equities. The maximum acceptable delay is approximately 5 days."
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
        "**What this means:** Walk-forward validation confirms that the strategy's "
        "outperformance is not an artifact of a single favourable period. The Sharpe "
        "ratio varies year to year but remains positive across the majority of test "
        "windows."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Important Caveats
# ---------------------------------------------------------------------------
st.warning(
    """
**Important Caveats**

1. **Transaction costs matter.** All strategy metrics include 5 bps per round-trip trade. Breakeven cost is 50 bps -- robust, but not infinite.

2. **Execution delay degrades performance.** A 1-day delay reduces Sharpe by ~0.2. Timely execution is essential.

3. **The 2022 episode is a genuine weakness.** The strategy's credit signal widened modestly during 2022, but not enough to trigger a full risk-off position. This bear market was driven by rate hikes and valuation compression, not credit deterioration.

4. **Past performance is not indicative of future results.** Regime shifts, changes in market microstructure, or new central bank tools could alter the credit-equity relationship going forward.

5. **This is a risk management tool, not an alpha generator.** The primary value is in reducing drawdowns during stress periods rather than generating excess returns during calm periods. Think of it as portfolio insurance that happens to be free (or slightly profitable) on average.
    """
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Trade Log: Narrative, Legend, Dual Downloads, Preview
# ---------------------------------------------------------------------------
st.markdown("### How to Read the Trade Log")

st.markdown(
    "**These are simulated trades from a backtest, not actual broker executions.** "
    "The strategy was never run with real money -- the trade log is the output of "
    "replaying the HMM stress signal against historical prices, assuming a $10,000 "
    "starting stake and 5 basis points (0.05%) of round-trip commission per trade."
)

st.markdown(
    "Two files are available below. The **broker-style log** "
    "(`winner_trades_broker_style.csv`) is the default, user-friendly view -- one "
    "row per execution, formatted the way a retail brokerage statement would look. "
    "The **position log** (`winner_trade_log.csv`) is the researcher/debugging view, "
    "with one row per position-weight change and additional diagnostic columns."
)

st.markdown("**Key columns in the broker-style log:**")
st.markdown(
    "- `trade_date` -- the date the trade would have been executed.\n"
    "- `side` -- BUY (scaling up equity exposure) or SELL (scaling down toward cash).\n"
    "- `quantity_pct` -- the *resulting* target equity exposure as a percentage of "
    "the portfolio, not the size of the trade itself. Because this is a P2 Signal "
    "Strength strategy, the position is sized proportionally to the HMM stress "
    "probability -- 100% long when stress is near zero, 0% (all cash) when stress "
    "is near one.\n"
    "- `price` / `notional_usd` -- SPY closing price and dollar value of the "
    "resulting position.\n"
    "- `commission_bps` / `commission_usd` -- transaction cost charged on the trade "
    "(5 bps, i.e. 0.05%).\n"
    "- `cum_pnl_pct` -- cumulative strategy return since inception, in percent.\n"
    "- `reason` -- human-readable signal value and the scale-up or scale-down step "
    "that triggered the row."
)

with st.container(border=True):
    st.markdown(
        "**Concrete example -- COVID 2020.** On **2020-02-24**, the HMM stress "
        "probability jumped from **0.086 to 1.000** in a single day as credit "
        "markets reacted to the unfolding pandemic. The broker-style log shows a "
        "SELL taking the target equity exposure from **91.4% down to 0%** (all "
        "cash) at an SPY price of $294.65. That row is immediately after "
        "2020-02-21 in the CSV. This single transition is what kept the "
        "strategy's maximum drawdown to -10.2%, versus roughly -34% for "
        "buy-and-hold SPY through the same period."
    )

st.markdown("#### Download Trading History")

with st.expander("📋 What do these columns mean?", expanded=False):
    st.markdown(
        "| Column | Type | Meaning | Example |\n"
        "|--------|------|---------|---------|\n"
        "| `trade_date` | date | Date the trade would have been executed | 2020-02-24 |\n"
        "| `side` | string | BUY (increase exposure) or SELL (decrease to cash) | SELL |\n"
        "| `instrument` | string | Target ticker -- the asset traded | SPY |\n"
        "| `quantity_pct` | 0-100 | Target portfolio allocation AFTER this trade | 0.0 |\n"
        "| `price` | USD | Close price of instrument on trade date | $294.65 |\n"
        "| `notional_usd` | USD | Dollar value of the resulting position (quantity_pct / 100 × $10,000 starting capital) | $0.00 |\n"
        "| `commission_bps` | int | Commission rate in basis points | 5 |\n"
        "| `commission_usd` | USD | Total commission for this trade | $0.00 |\n"
        "| `cum_pnl_pct` | % | Cumulative portfolio return since inception | 421.05 |\n"
        "| `reason` | string | Human-readable signal that triggered the trade | \"HMM stress prob 1.000 crossed threshold -- full risk-off\" |\n"
    )
    st.caption(
        "Note: This is a simulated trade record based on backtest signals. "
        "No real trades were executed."
    )

_broker_path = _RESULTS_DIR / "winner_trades_broker_style.csv"
_position_path = _RESULTS_DIR / "winner_trade_log.csv"

_broker_df = None
if _broker_path.exists():
    # Broker CSV has a leading "# ..." comment line; skip it.
    _broker_df = pd.read_csv(_broker_path, comment="#")

_position_df = None
if _position_path.exists():
    _position_df = pd.read_csv(_position_path)

_dl_col1, _dl_col2 = st.columns(2)

with _dl_col1:
    if _broker_df is not None and len(_broker_df) > 0:
        try:
            st.download_button(
                label="Download trade log (broker-style)",
                data=_broker_df.to_csv(index=False),
                file_name="hy_ig_v2_spy_trades_broker_style.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )
        except TypeError:
            st.download_button(
                label="Download trade log (broker-style)",
                data=_broker_df.to_csv(index=False),
                file_name="hy_ig_v2_spy_trades_broker_style.csv",
                mime="text/csv",
                use_container_width=True,
            )
        st.caption(f"{len(_broker_df):,} executions, one row per trade.")
    else:
        st.info("Broker-style trade log not yet generated.")

with _dl_col2:
    if _position_df is not None and len(_position_df) > 0:
        st.download_button(
            label="Download position log (researcher)",
            data=_position_df.to_csv(index=False),
            file_name="hy_ig_v2_spy_trade_log.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption(f"{len(_position_df):,} position-weight change rows.")
    else:
        st.info("Position log not yet generated.")

if _broker_df is not None and len(_broker_df) > 0:
    st.markdown("**Preview: first 10 rows of the broker-style log**")
    st.dataframe(_broker_df.head(10), use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Execution Panel
# ---------------------------------------------------------------------------
render_execution_panel(PAIR_ID)

# ---------------------------------------------------------------------------
# Transition
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Generated with AIG-RLIC+ | Data: 2000-01 to 2025-12"
)
