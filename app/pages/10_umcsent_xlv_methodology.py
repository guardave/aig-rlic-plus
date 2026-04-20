"""UMCSENT × XLV -- Methodology: Technical Appendix.

ECON-UD: includes Signal Universe (from signal_scope.json)
ECON-AS: includes Analyst Suggestions (from analyst_suggestions.json, omit if empty)

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
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar
from components.signal_universe_table import render_signal_universe
from components.analyst_suggestions_table import render_analyst_suggestions

st.set_page_config(
    page_title="UMCSENT × XLV Methodology | AIG-RLIC+",
    page_icon="📐",
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

render_breadcrumb("Methodology", PAIR_ID)

with st.expander("Plain English"):
    st.markdown(
        "This section explains exactly how we did the analysis: which data we used, "
        "how we constructed each signal, which statistical tests we ran, and what "
        "could go wrong. Normal readers can skip it. Expert readers can use it to "
        "reproduce or criticise our work."
    )

st.title("Methodology: Technical Appendix")
st.markdown(
    "*This section provides the full methodological detail needed to replicate, "
    "challenge, or extend our analysis. Every claim in the preceding pages traces "
    "back to a specific method, dataset, and diagnostic described here.*"
)
st.markdown("---")

# ---------------------------------------------------------------------------
# Sample Period
# ---------------------------------------------------------------------------
st.markdown("### Sample Period")

_winner = {}
_winner_path = _RESULTS_DIR / "winner_summary.json"
if _winner_path.exists():
    with open(_winner_path) as f:
        _winner = json.load(f)

oos_start = _winner.get("oos_start", "2019-04-30")
is_end = _winner.get("is_end", "2019-03-31")
is_n = _winner.get("is_n", 243)
oos_n = _winner.get("oos_n", 81)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Full Sample", "1998-12 to 2025-12", delta="325 monthly obs")
with col2:
    st.metric("In-Sample", f"1998-12 to {is_end[:7]}", delta=f"~{is_n} obs (model estimation)")
with col3:
    st.metric("Out-of-Sample", f"{oos_start[:7]} to 2025-12", delta=f"~{oos_n} obs (strategy evaluation)")

st.caption(
    "Why this matters: the IS/OOS split is computed dynamically using ECON-OOS2 rule: "
    "OOS window = min(max(36, round(N × 0.25)), 120) months from end. With N=325 monthly "
    "observations, this yields 81 OOS months (~6.75 years). The split date is earlier "
    "than other pairs (2019) because XLV data starts later (1998-12, not 1990) and the "
    "25% OOS formula allocates proportionally."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Data Sources
# ---------------------------------------------------------------------------
st.markdown("### Data Sources")

st.markdown("""
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **Indicator (in scope)** | FRED | UMCSENT (Michigan Consumer Sentiment Index) | Monthly |
| **Target (in scope)** | Yahoo Finance | XLV (Health Care Select Sector SPDR, adjusted close) | Daily → Monthly |
| **Benchmark comparison** | Yahoo Finance | SPY (S&P 500 ETF, adjusted close) | Daily → Monthly |
| **Volatility (control only)** | Yahoo Finance | ^VIX (CBOE Volatility Index) | Daily → Monthly |
| **Macro controls** | FRED | UNRATE (Unemployment Rate), DGS10 (10Y Treasury Yield) | Monthly / Daily |

*Scope discipline (ECON-SD).* Only UMCSENT derivatives and XLV derivatives appear in the Signal Universe,
charts, and tournament for this pair. UNRATE, DGS10, and VIX are used as controls in regression models
only and are not traded signals. See the Signal Universe section below for the authoritative in-scope list.
""")

st.caption(
    "Data access: FRED series retrieved via direct CSV download "
    "(https://fred.stlouisfed.org/graph/fredgraph.csv). "
    "Yahoo Finance data retrieved via yfinance with auto_adjust=True."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Indicator Construction
# ---------------------------------------------------------------------------
st.markdown("### Indicator Construction")

st.markdown("**Michigan Consumer Sentiment (UMCSENT)**")
st.markdown(
    "FRED series UMCSENT: monthly index of consumer confidence published by the "
    "University of Michigan Survey of Consumers. Index baseline = 100 (November 1966). "
    "Released mid-month for the current survey month. Approximately 500 households "
    "surveyed. Not seasonally adjusted."
)

st.markdown("**Derived signals (in-scope per ECON-SD):**")
st.markdown("""
| Signal | Formula | Stationarity |
|:-------|:--------|:-------------|
| `umcsent` | Raw level | Non-stationary (use transformed) |
| `umcsent_yoy` | (umcsent / umcsent.shift(12) - 1) × 100 | Approximately stationary |
| `umcsent_mom` | (umcsent / umcsent.shift(1) - 1) × 100 | Approximately stationary |
| `umcsent_zscore` | (umcsent - 36M rolling mean) / 36M rolling std | Stationary by construction |
| `umcsent_3m_ma` | umcsent.rolling(3).mean() | Non-stationary (regime indicator) |
| `umcsent_direction` | sign(umcsent_mom) | Stationary by construction |
| `umcsent_dev_ma` | umcsent - umcsent_3m_ma | Approximately stationary |
""")

st.markdown("**XLV Target Construction:**")
st.markdown(
    "XLV daily adjusted closing prices (Yahoo Finance, `auto_adjust=True`) resampled to "
    "monthly last close. Return series: `xlv_ret = xlv.pct_change()`. Forward return "
    "series computed as `xlv.shift(-h) / xlv - 1` for h = 1, 3, 6, 12 months."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# IS/OOS Split
# ---------------------------------------------------------------------------
st.markdown("### IS/OOS Split (ECON-OOS2)")

st.markdown(
    "The IS/OOS split is computed dynamically using the ECON-OOS2 rule: "
    "`OOS_months = min(max(36, round(N × 0.25)), 120)` where N is the number of "
    f"valid monthly observations. With N = 325, OOS = min(max(36, 81), 120) = **81 months**. "
    f"IS ends: **{is_end}**. OOS starts: **{oos_start}**."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Tournament Design
# ---------------------------------------------------------------------------
st.markdown("### Tournament Design (5D Combinatorial Backtest)")

st.markdown("""
**Dimensions:**
- **Signals (7):** umcsent (level), umcsent_yoy, umcsent_mom, umcsent_zscore,
  umcsent_3m_ma, umcsent_direction, umcsent_dev_ma
- **Thresholds (varies per signal):** T1 fixed percentile (IS-based, 25th/50th/75th),
  T2 rolling percentile (60M window), T3 rolling z-score bands (±1.0, ±1.5, ±2.0 σ),
  T4 zero crossing (for change signals)
- **Strategies (3):** P1 Long/Cash (binary toggle), P2 Signal Strength (proportional
  scaling), P3 Long/Short (±1 position)
- **Lead times (5):** 0, 1, 2, 3, 6 months
- **Direction:** Procyclical applied (low signal → cash, high signal → long XLV),
  consistent with empirically observed direction

**Total combinations tested:** 1,305
**Valid strategies (OOS Sharpe > 0, turnover ≤ 24/yr, OOS n ≥ 12):** 1,196

**Ranking metric:** Out-of-sample (OOS) Sharpe ratio.
""")

st.markdown("---")

# ---------------------------------------------------------------------------
# Signal Universe (ECON-UD)
# ---------------------------------------------------------------------------
st.markdown("### Signal Universe (ECON-UD)")

st.caption(
    "What this shows: the authoritative list of in-scope signals per ECON-SD scope "
    f"discipline. Loaded from `results/{PAIR_ID}/signal_scope.json`."
)

render_signal_universe(PAIR_ID)

st.markdown("---")

# ---------------------------------------------------------------------------
# Stationarity Tests
# ---------------------------------------------------------------------------
st.markdown("### Stationarity Tests")

_stat_path = _RESULTS_DIR / "stationarity_tests_20260420.csv"
if _stat_path.exists():
    _stat_df = pd.read_csv(_stat_path)
    st.dataframe(_stat_df, use_container_width=True, hide_index=True)
    st.caption(
        "What this shows: ADF and KPSS test results for key variables. "
        "'Stationary' means the variable does not have a unit root. "
        "Level variables (umcsent, xlv) are typically non-stationary; "
        "transformed variables (yoy, mom, zscore) are approximately stationary."
    )
else:
    st.info("Stationarity tests CSV not found. Run the pipeline to generate.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Econometric Models
# ---------------------------------------------------------------------------
st.markdown("### Econometric Models")

st.markdown("""
The pipeline runs the following econometric analyses (all results in `results/umcsent_xlv/core_models_20260420/`):

| Model | Files | Purpose |
|:------|:------|:--------|
| **Granger Causality** | `granger_causality.csv` | Tests whether UMCSENT leads XLV (both directions, lags 1-6) |
| **Predictive Regressions (OLS, HC3)** | `predictive_regressions.csv` | Linear forecasting power at 1/3/6/12M horizons |
| **Local Projections (Jorda)** | `local_projections.csv` | HAC-robust impulse responses at each horizon |
| **Regime-Dependent LPs** | `regime_local_projections.csv` | Interaction with low-sentiment regime dummy |
| **Markov-Switching Regression** | `markov_switching_2state.csv` | 2-state regime identification |
| **Quantile Regression** | `quantile_regression.csv` | Effect at 5th/10th/.../95th return percentiles |
| **Johansen Cointegration** | `cointegration.csv` | Long-run level relationship between UMCSENT and XLV |
| **Random Forest Walk-Forward** | `rf_walk_forward.csv`, `rf_feature_importance.csv` | ML-based feature importance across time |
| **Diagnostics** | `diagnostics_summary.csv` | Jarque-Bera, Breusch-Pagan, Breusch-Godfrey, Durbin-Watson |
""")

# Show predictive regressions
_reg_path = _RESULTS_DIR / "core_models_20260420" / "predictive_regressions.csv"
if _reg_path.exists():
    _reg_df = pd.read_csv(_reg_path)
    st.markdown("#### Predictive Regressions (OLS, HC3 robust SEs)")
    st.dataframe(_reg_df, use_container_width=True, hide_index=True)
    st.caption(
        "What this shows: coefficient estimates from OLS regressions of XLV "
        "forward returns on UMCSENT signals. Positive coefficients = procyclical "
        "(consistent with observed direction). HC3 robust standard errors."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Direction Assessment
# ---------------------------------------------------------------------------
st.markdown("### Direction Assessment")

_interp_path = _RESULTS_DIR / "interpretation_metadata.json"
if _interp_path.exists():
    with open(_interp_path) as f:
        _interp = json.load(f)

    expected = _interp.get("expected_direction", "countercyclical")
    observed = _interp.get("observed_direction", "procyclical")
    consistent = _interp.get("direction_consistent", False)

    if consistent:
        st.success(
            f"**Direction consistent.** Expected: {expected}. "
            f"Observed: {observed}. Both agree."
        )
    else:
        st.warning(
            f"**Direction surprise.** Expected: *{expected}* "
            f"(textbook defensive-rotation hypothesis). "
            f"Observed: *{observed}* (empirical regression result).\n\n"
            "The tournament strategy is calibrated to the **observed** direction. "
            "All charts and narratives reflect the empirical result."
        )

st.markdown("---")

# ---------------------------------------------------------------------------
# Analyst Suggestions (ECON-AS)
# ---------------------------------------------------------------------------
st.markdown("### Analyst Suggestions for Future Work (ECON-AS)")

render_analyst_suggestions(PAIR_ID)

st.markdown("---")

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
st.markdown("### Reproducibility")

st.markdown("""
All analysis is fully scripted and reproducible:

```bash
# Regenerate pipeline results
python3 scripts/pair_pipeline_umcsent_xlv.py

# Regenerate charts
python3 scripts/generate_charts_umcsent_xlv.py
```

**Key files:**
- Pipeline: `scripts/pair_pipeline_umcsent_xlv.py`
- Charts: `scripts/generate_charts_umcsent_xlv.py`
- Results: `results/umcsent_xlv/`
- Data: `data/umcsent_xlv_monthly_19980101_20251231.parquet`
- Signal scope: `results/umcsent_xlv/signal_scope.json`
- Winner summary: `results/umcsent_xlv/winner_summary.json`
- Interpretation: `results/umcsent_xlv/interpretation_metadata.json`
""")

st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    "Pair ID: umcsent_xlv | "
    "Analysis date: 2026-04-20 | "
    "Script: scripts/pair_pipeline_umcsent_xlv.py"
)
