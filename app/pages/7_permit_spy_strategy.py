"""Finding 4 — The Strategy: PERMIT → SPY Tournament Results."""

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
    page_title="Permits Strategy | AIG-RLIC+",
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
st.title("The Strategy: Translating Permits Signals to Action")
st.markdown(
    "*We tested 856 strategy combinations to find the most robust way to trade on "
    "building permits signals.*"
)
st.markdown("---")

# ===================== TOURNAMENT WINNER =====================
st.markdown("### Tournament Winner: MoM Momentum (Long/Short, Fixed P25, 6M Lead)")

st.markdown(
    '<div class="spotlight-card">'
    "<b>Strategy Rule in Plain English:</b><br>"
    "When the month-over-month change in Building Permits is above its historical "
    "25th percentile (i.e., not deeply negative), go long SPY. When permits momentum "
    "falls below the 25th percentile (sharp decline), go short. Apply the signal with "
    "a 6-month lead to exploit permits' role as a leading indicator."
    "</div>",
    unsafe_allow_html=True,
)

kpi_row([
    {"label": "OOS Sharpe Ratio", "value": "1.45", "delta": "+61% vs buy-and-hold"},
    {"label": "Buy-Hold Sharpe", "value": "0.90"},
    {"label": "Buy-Hold Max DD", "value": "-23.9%", "delta_color": "inverse"},
    {"label": "Combinations Tested", "value": "856"},
    {"label": "Valid Strategies", "value": "675"},
])

st.markdown("---")

# ===================== TOURNAMENT SCATTER =====================
st.markdown("### Tournament Results: All Combinations")

load_plotly_chart(
    "permit_spy_tournament_scatter",
    fallback_text="Tournament scatter: OOS Sharpe vs turnover",
    caption=(
        "Each dot is one strategy combination. Color indicates max drawdown "
        "(green = shallow, red = deep). Stars mark the top 5. Diamond is buy-and-hold."
    ),
    pair_id="permit_spy",
)

# ===================== LEADERBOARD =====================
st.markdown("### Tournament Leaderboard")

results_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..",
    "results", "permit_spy", "tournament_results.csv"
)

# Try date-stamped variant if base name not found
if not os.path.exists(results_path):
    results_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..",
        "results", "permit_spy",
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
            "Lead": f"{int(r['lead_months'])}M",
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
        f"Ranked by out-of-sample Sharpe (2018-2025)"
    )
else:
    st.info("Tournament results CSV not found. Showing summary from analysis brief.")
    st.markdown(
        "**Top strategy:** MoM momentum, fixed P25 threshold, Long/Short, "
        "6-month lead — OOS Sharpe **1.45** vs buy-and-hold **0.90**."
    )

st.markdown("---")

# ===================== CAVEATS =====================
st.warning(
    """
    **Important Caveats**

    1. **Housing bubble distortion (2003-2007).** Permits surged to unsustainable
       levels during the subprime boom. The signal was pro-cyclical during this
       period, but the subsequent crash was unprecedented in modern data.

    2. **COVID collapse (April 2020).** Permits plunged as construction halted
       nationwide. The V-shaped recovery was driven by unique policy responses
       (mortgage forbearance, stimulus) that may not repeat.

    3. **Post-COVID supply chain noise (2021-2022).** Lumber shortages, labor
       constraints, and zoning backlogs distorted the permits-to-construction
       pipeline, reducing signal reliability during this period.

    4. **Long/Short amplifies both gains and losses.** The winning strategy
       uses Long/Short, which doubles exposure compared to Long/Cash. The
       higher Sharpe comes with commensurately higher risk in adverse scenarios.
    """
)

# --- Transition ---
st.markdown("---")
st.page_link("pages/7_permit_spy_methodology.py", label="Continue to Methodology", icon="📐")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 1990-01 to 2025-12"
    "</div>",
    unsafe_allow_html=True,
)
