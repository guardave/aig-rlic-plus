"""Finding 5 — The Strategy: VIX/VIX3M → SPY Tournament Results."""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.metrics import kpi_row
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="VIX/VIX3M Strategy | AIG-RLIC+",
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
st.title("The Strategy: Translating VIX Term Structure Signals to Action")
st.markdown(
    "*We tested 916 strategy combinations to find the most robust way to trade on "
    "VIX/VIX3M term structure signals.*"
)
st.markdown("---")

# ===================== TOURNAMENT WINNER =====================
st.markdown("### Tournament Winner: Z-Score 126d, Rolling P75 Threshold, Long/Cash")

st.markdown(
    '<div class="spotlight-card">'
    "<b>Strategy Rule in Plain English:</b><br>"
    "Compute the VIX/VIX3M ratio's z-score over a trailing 126-day (6-month) window. "
    "When this z-score is below its rolling 75th percentile — meaning term structure "
    "stress is not extreme — stay long SPY. When the z-score exceeds the 75th "
    "percentile (acute backwardation / panic), move to cash. No leverage, no shorting. "
    "The signal exploits the massive return differential between contango and "
    "backwardation regimes."
    "</div>",
    unsafe_allow_html=True,
)

kpi_row([
    {"label": "OOS Sharpe Ratio", "value": "1.13", "delta": "+47% vs buy-and-hold"},
    {"label": "Buy-Hold Sharpe", "value": "0.77"},
    {"label": "Buy-Hold Max DD", "value": "-33.7%", "delta_color": "inverse"},
    {"label": "Combinations Tested", "value": "916"},
    {"label": "Valid Strategies", "value": "332"},
])

st.markdown("---")

# ===================== TOURNAMENT SCATTER =====================
st.markdown("### Tournament Results: All Combinations")

load_plotly_chart(
    "vix_vix3m_spy_tournament_scatter",
    fallback_text="Tournament scatter: OOS Sharpe vs turnover",
    caption=(
        "Each dot is one strategy combination. Color indicates max drawdown "
        "(green = shallow, red = deep). Stars mark the top 5. Diamond is buy-and-hold."
    ),
    pair_id="vix_vix3m_spy",
)

# ===================== LEADERBOARD =====================
st.markdown("### Tournament Leaderboard")

results_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..",
    "results", "vix_vix3m_spy", "tournament_results.csv"
)

# Try date-stamped variant if base name not found
if not os.path.exists(results_path):
    results_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..",
        "results", "vix_vix3m_spy",
    )
    if os.path.isdir(results_dir):
        for f in sorted(os.listdir(results_dir), reverse=True):
            if f.startswith("tournament_results") and f.endswith(".csv"):
                results_path = os.path.join(results_dir, f)
                break

if os.path.exists(results_path):
    tdf = pd.read_csv(results_path)
    valid = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
    top5 = valid.nlargest(5, "oos_sharpe")
    bh = tdf[tdf["signal"] == "BENCHMARK"]

    display_rows = []
    for rank, (_, r) in enumerate(top5.iterrows(), 1):
        display_rows.append({
            "Rank": rank,
            "Signal": r["signal"],
            "Threshold": r["threshold"],
            "Strategy": r["strategy"],
            "Lead": f"{int(r['lead_months'])}M" if "lead_months" in r.index else "L0",
            "OOS Sharpe": round(r["oos_sharpe"], 2),
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
        f"Ranked by out-of-sample Sharpe (2020-2025)"
    )
else:
    st.info("Tournament results CSV not found. Showing summary from analysis brief.")
    st.markdown(
        "**Top strategy:** Z-score 126d, rolling P75 threshold, Long/Cash, "
        "no lead — OOS Sharpe **1.13** vs buy-and-hold **0.77**."
    )

st.markdown("---")

# ===================== CAVEATS =====================
st.warning(
    """
    **Important Caveats**

    1. **VIX3M only available since 2007.** The sample is 18 years — shorter
       than for macro indicators with 30+ year histories. This limits the
       number of independent market cycles observed (essentially 2-3 full cycles).

    2. **COVID crash dominance in OOS window.** The out-of-sample period
       (2020-2025) includes the March 2020 crash, which is the most extreme
       VIX term structure event in the sample. The strategy's OOS performance
       is partly driven by correctly navigating this single event.

    3. **Structural changes in volatility markets.** The growth of VIX ETPs
       (VXX, UVXY, etc.) since 2009 and the XIV blow-up in 2018 have changed
       the dynamics of volatility term structure. Relationships calibrated
       on pre-2018 data may not fully capture post-Volmageddon dynamics.

    4. **Transaction cost sensitivity.** Daily-frequency signals can generate
       higher turnover than monthly indicators. The winning Long/Cash strategy
       mitigates this but investors should verify that execution costs do not
       erode the Sharpe advantage.
    """
)

# --- Transition ---
st.markdown("---")
st.page_link("pages/8_vix_vix3m_spy_methodology.py", label="Continue to Methodology", icon="📐")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 2007-01 to 2025-12"
    "</div>",
    unsafe_allow_html=True,
)
