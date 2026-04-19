"""HY-IG v2 -- The Strategy: Tournament Winner and Alternatives.

Wave 2B restructure (2026-04-19):
  - Ray's new "How the Signal is Generated" plain-English section rendered
    BEFORE the KPI cards (RES-7, closes S18-1 narrative side).
  - Execute / Performance / Confidence tab structure:
      * Execute: Strategy Summary + Probability Engine Panel (APP-SE1) +
        Position Adjustment Panel (APP-SE2) + Instructional Trigger Cards
        (APP-SE3)
      * Performance: equity curve + drawdown + trade log
      * Confidence: stress tests, signal decay, walk-forward — every
        artifact gets a 1-line takeaway caption (APP-SE5)
  - Future: Live Execution section appended at the bottom (APP-SE4).
  - Preserved: breadcrumb, Plain English expander, Execution Points table,
    How to Use This Indicator Manually, Explore Alternative Strategies,
    trade log + legend + "How to Read the Trade Log".
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
from components.direction_check import render_direction_check
from components.instructional_trigger_cards import render_instructional_trigger_cards
from components.live_execution_placeholder import render_live_execution_placeholder
from components.metrics import kpi_row
from components.narrative import render_glossary_sidebar
from components.position_adjustment_panel import render_position_adjustment_panel
from components.probability_engine_panel import render_probability_engine_panel
from components.sidebar import render_sidebar

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
_REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Breadcrumb navigation (N10, META-PWQ)
# ---------------------------------------------------------------------------
render_breadcrumb("Strategy", PAIR_ID)

# ---------------------------------------------------------------------------
# APP-DIR1: 3-way direction triangulation (Evan ↔ Dana ↔ Ray).
# Currently 2-way (Ray leg pending RES-17 narrative-frontmatter migration).
# Agreement → silent caption. Mismatch → st.error per APP-SEV1 L1.
# ---------------------------------------------------------------------------
render_direction_check(PAIR_ID)

# ---------------------------------------------------------------------------
# Plain English expander (N8 -- Ray's narrative addition)
# ---------------------------------------------------------------------------
with st.expander("🧒 Plain English version"):
    st.markdown(
        "Our computer looked at every possible combination of 'signal strength + "
        "threshold + trade rule' to find the one that would have made the most "
        "money (adjusted for risk) in past data. The winner is a strategy that "
        "reduces stock exposure when credit spread stress is high and adds back "
        "when stress fades. In this section we explain exactly what the strategy "
        "does, when to use it, and when it would have failed."
    )

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
# How the Signal is Generated (RES-7, closes S18-1 narrative side) — BEFORE
# KPI cards per Ray's Page-4 narrative ordering.
# ---------------------------------------------------------------------------
st.markdown("### How the Signal is Generated")

st.markdown(
    "The HMM (hidden Markov model) fits two hidden market states to the "
    "credit-spread data -- \"calm\" and \"stressed.\" Every day, it asks a simple "
    "question: given how the HY-IG spread and VIX moved today, is the market "
    "more likely to be in the calm state or the stressed state? The answer is "
    "a probability between 0 and 1 -- think of it as a continuously-updating "
    "\"stress meter\" built from the behaviour of the bond market itself, with "
    "no arbitrary thresholds imposed by the analyst."
)

st.markdown(
    "When that stress probability crosses 50%, the strategy reduces equity "
    "exposure; the higher the probability, the lower the target allocation to "
    "SPY. When the probability falls back below 50%, equity exposure is "
    "restored in the same proportional way. The strategy is not trying to "
    "predict the next crisis -- it is responding to the market's own "
    "indication that something is wrong, and acting before the equity market "
    "has fully priced it in."
)

st.markdown(
    "The key insight behind the rule is that credit markets price in "
    "deterioration earlier than equity markets. By the time equity volatility "
    "spikes, credit spreads have typically already widened. The HMM "
    "translates that widening into an actionable probability signal -- so the "
    "investor does not need to watch every spread tick themselves and does "
    "not need to judge \"how wide is wide enough\" on any given day. For the "
    "formal mathematical specification of the HMM, see the Methodology page."
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
        {
            "label": "OOS Return (arithmetic ann.)",
            "value": f"+{oos_return:.1f}%",
            "delta": "arithmetic mean x 252",
        },
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
    "Arithmetic annualized return; compounded CAGR (geometric) would be slightly "
    "different and is documented in the Methodology References."
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
# Execute / Performance / Confidence tabs
# ---------------------------------------------------------------------------
tab_execute, tab_performance, tab_confidence = st.tabs(
    ["Execute", "Performance", "Confidence"]
)

# ===========================================================================
# EXECUTE TAB — strategy summary + APP-SE1/SE2/SE3 panels
# ===========================================================================
with tab_execute:
    st.markdown("### Strategy Summary")

    _signal_name = _winner.get("signal_display_name", "HMM Stress Probability")
    _threshold_name = _winner.get("threshold_display_name", "HMM probability > 0.5")
    _strategy_name = _winner.get("strategy_display_name", "Signal Strength")
    _strategy_code = _winner.get("strategy_code", "P2")
    _lead_desc = _winner.get("lead_description", "No lead (same-period)")
    _direction = _winner.get("direction", "counter_cyclical").replace("_", " ")

    _col1, _col2 = st.columns(2)
    with _col1:
        st.markdown(f"**Signal:** {_signal_name}")
        st.markdown(f"**Threshold:** {_threshold_name}")
        st.markdown(f"**Strategy family:** {_strategy_name} ({_strategy_code})")
    with _col2:
        st.markdown(f"**Lead time:** {_lead_desc}")
        st.markdown(f"**Direction:** {_direction}")
        st.markdown(
            f"**Strategy description:** "
            f"{_winner.get('strategy_description', 'Scale position size proportionally to signal strength.')}"
        )

    st.markdown("---")

    # APP-SE1 — Probability Engine Panel (with pre-render validation).
    render_probability_engine_panel(PAIR_ID)

    st.markdown("---")

    # APP-SE2 — Position Adjustment Panel (gated on SE1 validation).
    render_position_adjustment_panel(PAIR_ID)

    st.markdown("---")

    # APP-SE3 — Instructional Trigger Cards.
    render_instructional_trigger_cards(PAIR_ID)

    st.markdown("---")

    # ----------------------------------------------------------
    # How to Use This Indicator Manually (N2/N4 -- Ray narrative)
    # ----------------------------------------------------------
    st.markdown("### How to Use This Indicator Manually")

    st.markdown(
        "If you want to use the HY-IG spread as a signal yourself -- with no "
        "automated system, no code, no broker API -- follow this 3-step routine. "
        "This is written for the stock investor who rebalances a long-only "
        "portfolio a few times a year, not for an algorithmic trader."
    )

    st.markdown("**1. Check the spread weekly.**")
    st.markdown(
        "- **Source:** FRED series `BAMLH0A0HYM2` (HY OAS) and `BAMLC0A0CM` (IG OAS) "
        "-- subtract IG from HY to get the spread. The free FRED charting page will "
        "plot the difference directly. Any Friday-afternoon reading is fine; you do "
        "not need intraday data.\n"
        "- **What to compute:** the current spread in **bps (basis points, where 100 "
        "bps = 1%)**, and where it sits inside the last **504 trading days** "
        "(roughly 2 years) of history. Most spreadsheet tools can compute a "
        "percentile rank; so can FRED's own download-and-chart interface."
    )

    st.markdown("**2. Interpret where you are.**")
    st.markdown(
        "- **Bottom 25% of the 504-day range -> calm regime.** Full equity exposure "
        "is reasonable. Historically this is where Sharpe runs well above 1 and "
        "drawdowns are shallow.\n"
        "- **Top 25% of the 504-day range -> stress regime.** Reduce equity exposure "
        "toward **0-50%**. Historically this is the band where SPY has produced "
        "annualised returns close to zero and drawdowns above 60%.\n"
        "- **Middle 50% -> ambiguous.** Hold your current allocation. The signal "
        "has no statistical edge in the middle of the distribution (this is why "
        "the median coefficient in the Quantile Regression block is essentially zero)."
    )

    st.markdown("**3. Act -- or consciously decide not to.**")
    st.markdown(
        "- The research shows the signal works best on a **63-day (3-month) forward "
        "horizon**, so do not overreact to week-to-week noise. One week in the top "
        "quartile is not a selling signal; two or three consecutive weeks is.\n"
        "- **Moving calm -> stress:** reduce exposure over 2-4 weeks, not in one "
        "day. The point of scaling is to avoid whipsaws when the signal oscillates "
        "around the 75th-percentile cutoff.\n"
        "- **Moving stress -> calm:** add back **gradually**. Historically the "
        "recovery is slower than the drop, so averaging in over several weeks rarely "
        "costs much."
    )

    with st.container(border=True):
        st.markdown("**Concrete example -- the 2020 COVID crash.**")
        st.markdown(
            "- On **2020-02-14**, the HY-IG spread was roughly **350 bps (3.50%)** "
            "-- firmly in the bottom quartile of its 504-day range. A manual user "
            "following this rule would have been fully invested.\n"
            "- Over the next four weeks the spread blew out to **1,100 bps (11.0%)** "
            "by **2020-03-16** -- far into the top quartile and still climbing.\n"
            "- A disciplined manual user, seeing the spread cross the 75th "
            "percentile of the 504-day range around **2020-02-24 to 2020-03-02**, "
            "would have started scaling down. In practice this probably means "
            "moving from 100% equity to roughly 50% over one to two weeks, then "
            "further down as the widening accelerated.\n"
            "- The spread compressed back below **500 bps (5.00%)** by "
            "**2020-06-08**, crossing back into the middle/lower quartiles. The "
            "manual user would then have started adding equity back, reaching full "
            "exposure over the following weeks.\n"
            "- This mechanical rule would not have timed the bottom perfectly -- "
            "no rule does -- but it would have avoided the worst of the -34% "
            "buy-and-hold drawdown and participated in the recovery from roughly "
            "July onward."
        )

    with st.expander("Caveats for manual use"):
        st.markdown(
            "- **Signals require patience.** This strategy works on weeks-to-months "
            "horizons, not days. If you check it daily and trade every wiggle, "
            "commissions and taxes will eat the edge.\n"
            "- **Transaction costs and taxes eat into gains.** The backtest charges "
            "5 bps (0.05%) round-trip; the real-world minimum for retail investors "
            "is often higher, and capital-gains taxes on a taxable account can "
            "dwarf commissions.\n"
            "- **This is one signal.** Combining with others -- volatility regime, "
            "yield-curve inversion, macro momentum -- likely improves robustness. "
            "See the separate analyses on **VIX x SPY** and **Yield Curve x SPY** "
            "in the portal for complementary signals.\n"
            "- **Never short-sell based on this rule.** The Quantile Regression "
            "evidence shows that stress-regime upside is dominated by violent "
            "relief rallies; a naive short would get run over by the same bars "
            "that make the right-tail coefficient positive."
        )

    st.markdown("---")

    # ----------------------------------------------------------
    # Execution Points — Actual Trigger Dates (N3 — Ray narrative)
    # ----------------------------------------------------------
    st.markdown("### Execution Points -- Actual Trigger Dates")

    st.markdown(
        "The winning strategy made many small position adjustments across the "
        "2000-2025 backtest -- 418 rows in `winner_trades_broker_style.csv`. The "
        "table below surfaces **eight inflection points** around major historical "
        "stress events, pulled directly from that log, so readers can tie the "
        "abstract HMM stress probability back to concrete history. Each row is "
        "reproducible: open the broker-style CSV, jump to the row number in the "
        "right-most column, and the exact commission, notional, price, and running "
        "cumulative P&L are all there."
    )

    _exec_points_md = (
        "| Date | Event | HMM Stress Prob | Position Change | Source Row |\n"
        "|:-----|:------|:----------------|:----------------|:-----------|\n"
        "| 2008-04-25 | March-2008 stress fades (Bear Stearns aftermath) | 0.415 -> 0.195 -> 0.117 -> 0.038 | Scale-up: 34.2% -> 58.5% -> 80.5% -> 88.3% -> 96.2% over 4 trading days | Rows 95-98 |\n"
        "| 2008-06-02 | Pre-Lehman credit deterioration builds | 0.443 -> 0.672 -> 0.813 -> 0.979 | Scale-down: 96.2% -> 55.7% -> 32.8% -> 18.7% -> 2.1% over 4 trading days | Rows 99-102 |\n"
        "| 2008-09-01 | Lehman week -- full stress-regime lock-in | 0.820 -> 0.931 -> 0.999 | Scale-down: 30.8% -> 18.0% -> 6.9% -> 0.1% over 3 trading days | Rows 111-113 |\n"
        "| 2009-12-21 | GFC recovery -- stress probability breaks below 0.5 | 0.932 -> 0.613 -> 0.433 -> 0.318 | Scale-up: 0.1% -> 6.8% -> 38.7% -> 56.7% -> 68.2% over 4 trading days | Rows 114-117 |\n"
        "| 2020-01-27 | Early COVID false alarm (reverted within two days) | 0.127 -> 0.998 -> 0.882 -> 0.080 | Oscillation: 95.3% -> 87.3% -> 0.2% -> 92.0% -> 98.4% -- noise the P2 Signal Strength smoothing contains | Rows 297-301 |\n"
        "| 2020-02-24 | COVID panic onset -- single-day collapse to cash | 0.086 -> 1.000 | Two-day move: 98.4% -> 91.4% -> 0.0% cash | Rows 302-303 |\n"
        "| 2022-01-13 | Rate-shock widening begins | 0.070 -> 0.268 -> 0.880 -> 0.995 | Scale-down: 98.8% -> 93.0% -> 73.2% -> 12.0% -> 0.5% over 5 trading days | Rows 344-347 |\n"
        "| 2022-08-12 | Mid-2022 recovery attempt (proved short-lived) | 0.911 -> 1.000 | Brief scale-up reversed: 0.5% -> 8.9% -> 0.0% | Rows 348-349 |"
    )
    st.markdown(_exec_points_md)

    st.caption(
        "The `reason` field in each row repeats the HMM stress probability and the "
        "before/after position weights, which is the auditable record of what the "
        "strategy saw and what it did. Because this is a P2 Signal Strength "
        "strategy, position changes are **proportional** to the HMM stress "
        "probability -- never all-or-nothing -- which is why many rows show "
        "fractional moves rather than 0%/100% flips."
    )

# ===========================================================================
# PERFORMANCE TAB — equity curve + drawdown + trade log
# ===========================================================================
with tab_performance:
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
    st.caption(
        "Takeaway: the winner participates in the upside and steps aside during "
        "the deepest equity drawdowns — most visible during 2020 and 2022."
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
    st.caption(
        f"Takeaway: the worst drawdown is {max_dd:.1f}% vs −33.7% for buy-and-hold "
        "— about one-third of the pain for comparable total return."
    )

    st.markdown("---")

    # --- Trade Log narrative + downloads ---
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
        st.caption(
            "Takeaway: each row shows a simulated scale-up or scale-down of SPY "
            "exposure driven by the HMM stress probability crossing key thresholds."
        )

# ===========================================================================
# CONFIDENCE TAB — validation artifacts (every one gets an APP-SE5 caption)
# ===========================================================================
with tab_confidence:
    st.markdown("### Validation: Stress Tests, Signal Decay, and Walk-Forward")

    # Status vocabulary legend (§3.12) — available/pending/validated.
    _glossary_path = _REPO_ROOT / "docs" / "portal_glossary.json"
    if _glossary_path.exists():
        with open(_glossary_path) as _gf:
            _glossary = json.load(_gf)
        _status = _glossary.get("status_labels", {})
        with st.expander(
            "What do status labels (*Available*, *Pending*, *Validated*) mean?",
            expanded=False,
        ):
            for label, definition in _status.items():
                if label.startswith("_"):
                    continue
                st.markdown(f"- **{label}** — {definition}")
            st.caption("Canonical source: `docs/portal_glossary.json` (Rule RES-10).")

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
            st.caption(
                "Takeaway: the strategy excels in credit-driven crises (GFC, COVID) "
                "but offers limited protection during pure rate-shock selloffs (2022)."
            )
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
            st.caption(
                "Takeaway: Sharpe declines monotonically as execution delay rises; "
                "delays beyond ~5 days materially erode the edge."
            )
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
            st.caption(
                "Takeaway: Sharpe stays positive across the majority of walk-forward "
                "windows — the edge is not concentrated in any single year."
            )
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
            st.caption(
                "Takeaway: the winning HMM Signal-Strength configuration sits at "
                "the top of the leaderboard; the next 19 rows show the breadth of "
                "the credit-signal edge across alternative signal transforms."
            )

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

    # ----------------------------------------------------------
    # Explore Alternative Strategies (N12, META-PWQ)
    # ----------------------------------------------------------
    st.markdown("### Explore Alternative Strategies")
    st.caption(
        "Beyond the #1 ranked strategy, here are other top performers. "
        "Understanding what these alternatives do -- and why they ranked lower -- "
        "can inform future strategy design."
    )

    if _tourn_path.exists():
        _alt_df = _tourn_df[
            (_tourn_df["valid"] == True) & (_tourn_df["signal"] != "BENCHMARK")
        ].copy()
        _top20_alt = _alt_df.nlargest(20, "oos_sharpe").reset_index(drop=True)

        _bench_row = _tourn_df[_tourn_df["signal"] == "BENCHMARK"]
        _bh_sharpe = float(_bench_row.iloc[0]["oos_sharpe"]) if len(_bench_row) else 0.90
        _bh_mdd = float(_bench_row.iloc[0]["max_drawdown"]) if len(_bench_row) else -33.7

        if len(_top20_alt) > 0:
            _labels = [
                f"#{i + 1}: {row['signal']} / {row['threshold']} / {row['strategy']} "
                f"(Sharpe {row['oos_sharpe']:.2f})"
                for i, row in _top20_alt.iterrows()
            ]
            _selected = st.selectbox(
                "Choose a strategy to inspect:", _labels, index=0,
                key="alt_strategy_explorer",
            )
            _idx = _labels.index(_selected)
            _row = _top20_alt.iloc[_idx]

            _alt_sharpe = float(_row["oos_sharpe"])
            _alt_mdd = float(_row["max_drawdown"])
            _alt_ret = float(_row["oos_ann_return"])
            _alt_to = float(_row["annual_turnover"])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("OOS Sharpe", f"{_alt_sharpe:.2f}",
                      delta=f"{_alt_sharpe - _bh_sharpe:+.2f} vs B&H")
            c2.metric("Max Drawdown", f"{_alt_mdd:.1f}%",
                      delta=f"{_alt_mdd - _bh_mdd:+.1f}% vs B&H",
                      delta_color="inverse")
            c3.metric("OOS Return (arithmetic ann.)", f"{_alt_ret:+.1f}%",
                      help="Arithmetic mean daily return x 252. CAGR (geometric) would be slightly different; see Methodology for comparison.")
            c4.metric("Annual Turnover", f"~{_alt_to:.1f}/yr")

            _strategy_desc = {
                "P1": "binary Long/Cash switch -- fully invested when signal is calm, 100% cash when signal is stressed",
                "P2": "continuous Signal Strength scaling -- position sizes proportionally to signal value",
                "P3": "Long/Short -- fully long in calm periods, fully short in stress",
            }.get(str(_row["strategy"]), str(_row["strategy"]))

            st.info(
                f"**What this strategy does:** Uses `{_row['signal']}` as the signal, "
                f"with threshold `{_row['threshold']}`, applying a {_strategy_desc}."
            )
            st.caption(
                "Takeaway: alternatives demonstrate the winning strategy family's "
                "robustness — the edge persists across related signal transforms."
            )
    else:
        st.info("Tournament results not available for alternative-strategy explorer.")

    st.markdown("---")

    # ----------------------------------------------------------
    # Where the Strategy Adds Value -- and Where It Does Not
    # ----------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Future: Live Execution section (APP-SE4)
# ---------------------------------------------------------------------------
st.markdown("---")
render_live_execution_placeholder(PAIR_ID)

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
