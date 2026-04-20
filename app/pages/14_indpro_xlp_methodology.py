"""Pair 14 — Methodology: INDPRO → XLP Technical Appendix.

Covers data sources, stationarity tests, econometric methods,
tournament design, signal universe (ECON-SD), and analyst suggestions (ECON-AS).
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

st.set_page_config(
    page_title="INDPRO × XLP Methodology | AIG-RLIC+",
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

PAIR_ID = "indpro_xlp"
render_breadcrumb("Methodology", PAIR_ID)
_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS_DIR = _REPO_ROOT / "results" / PAIR_ID

# Load winner summary for OOS period
_winner = {}
_winner_path = _RESULTS_DIR / "winner_summary.json"
if _winner_path.exists():
    with open(_winner_path) as f:
        _winner = json.load(f)

_oos_start = _winner.get("oos_start", "2019-01-31")[:7]
_is_end = _winner.get("is_end", "2018-12-31")[:7]
_oos_n = _winner.get("oos_n", "N/A")
_total_combos = _winner.get("total_combos", "N/A")
_valid_combos = _winner.get("valid_combos", "N/A")

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
st.title("Methodology: Technical Appendix")
st.markdown("*For reproducibility and peer scrutiny.*")
st.markdown("---")

# ===================== SAMPLE =====================
st.markdown("### Sample Period")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Full Sample", "1998-01 to 2025-12", delta="336 monthly observations")
with col2:
    st.metric("In-Sample", f"1998-01 to {_is_end}", delta="Model estimation (21 years)")
with col3:
    st.metric("Out-of-Sample", f"{_oos_start} to 2025-12",
              delta=f"Strategy evaluation ({_oos_n} months)")

st.caption(
    "What this shows: OOS window determined by formula: "
    "OOS = min(max(36, round(N×0.25)), 120) = min(max(36, 84), 120) = 84 months. "
    "XLP IPO was December 1998; the sample starts January 1998 to capture "
    "full-year INDPRO context for derived signals."
)

st.markdown("---")

# ===================== DATA SOURCES =====================
st.markdown("### Data Sources")

st.markdown("""
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **Industrial Production** | FRED | INDPRO | Monthly |
| **Consumer Staples ETF** | Yahoo Finance | XLP | Daily → Monthly |
| **S&P 500 (benchmark)** | Yahoo Finance | SPY | Daily → Monthly |
| **Volatility** | Yahoo Finance | ^VIX | Daily → Monthly |
| **Treasury yields** | FRED | DGS10, DTB3 | Daily → Monthly |
| **Fed Funds Rate** | FRED | DFF | Daily → Monthly |
| **Unemployment** | FRED | UNRATE | Monthly |
| **Capacity Utilization** | FRED | TCU | Monthly |
""")

st.caption(
    "What this shows: INDPRO and control variables were sourced from the validated "
    "indpro_spy_monthly parquet (already QA'd in that pair's pipeline). "
    "XLP was downloaded fresh from Yahoo Finance. Monthly values = last close of the month."
)

st.markdown("---")

# ===================== SIGNAL UNIVERSE (ECON-SD) =====================
st.markdown("### Signal Universe (ECON-SD)")

_scope_path = _RESULTS_DIR / "signal_scope.json"
if _scope_path.exists():
    with open(_scope_path) as f:
        scope = json.load(f)

    in_scope = scope.get("in_scope", {})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**In-scope: INDPRO Derivatives**")
        for s in in_scope.get("indicator_derivatives", []):
            st.markdown(f"- `{s}`")
    with col2:
        st.markdown("**In-scope: XLP Derivatives**")
        for s in in_scope.get("target_derivatives", []):
            st.markdown(f"- `{s}`")

    st.caption(
        "What this shows: per ECON-SD (Signal Discipline), only INDPRO and XLP derivatives "
        "are eligible as primary tournament signals. Controls (VIX, yield spread, UNRATE, CAPUT) "
        "are used only in regression controls, not as trading signals."
    )
else:
    st.info("Signal scope file not found.")

st.markdown("---")

# ===================== STATIONARITY =====================
st.markdown("### Stationarity Tests")

stat_path = _RESULTS_DIR / "stationarity_tests_20260420.csv"
if stat_path.exists():
    stat_df = pd.read_csv(stat_path)
    st.dataframe(
        stat_df.style.format({"statistic": "{:.4f}", "p_value": "{:.4f}"}),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "What this shows: ADF (Augmented Dickey-Fuller) and KPSS tests. "
        "ADF: reject null (p<0.05) = stationary. "
        "KPSS: fail to reject null (p>0.05) = stationary. "
        "INDPRO level is non-stationary (as expected); YoY and MoM transforms are stationary."
    )
else:
    st.info("Stationarity tests not found.")

st.markdown("---")

# ===================== METHODS =====================
st.markdown("### Econometric Methods")

st.markdown("""
| Method | Purpose | Key Detail |
|:-------|:--------|:-----------|
| Granger causality | Linear predictive relationship (both directions) | Up to 6 monthly lags |
| Predictive OLS | Baseline regression with HC3 robust SEs | 3 signals × 4 horizons = 12 regressions |
| Local projections (Jorda) | Impulse response at multiple horizons | HAC (Newey-West) standard errors |
| Regime-dependent LP | Interaction with contraction dummy | Tests asymmetric countercyclical effect |
| Markov-Switching regression | 2-state regime identification | Switching variance, 500 EM iterations |
| Quantile regression | Distributional effects | 7 quantiles (0.05 to 0.95) |
| Johansen cointegration | Long-run equilibrium test | Log levels, det_order=1 |
| PELT change-point detection | Structural breaks in IP YoY | RBF kernel, penalty=10 |
| Random Forest | Walk-forward feature importance | 200 trees, max_depth=5 |
""")

st.markdown("---")

# ===================== TOURNAMENT DESIGN =====================
st.markdown("### Tournament Design")

st.markdown(f"""
| Dimension | Values |
|:----------|:-------|
| **Signals (9)** | IP level, YoY%, MoM%, deviation from trend, z-score, 3M momentum, 6M momentum, acceleration, contraction dummy |
| **Threshold methods (5)** | Fixed IS percentile (p25/p50/p75), rolling percentile (p25/p50/p75), rolling z-score (±1.0/±1.5/±2.0), zero-crossing |
| **Strategies (3×2)** | Long/Cash, Signal-Strength, Long/Short — each in pro-cyclical and counter-cyclical orientation |
| **Lead times (5)** | 0, 1, 2, 3, 6 months |
| **Total grid** | ~1,665 raw; {_total_combos:,} results (including both orientations) |
| **Valid strategies** | {_valid_combos:,} (OOS Sharpe > 0, turnover < 24×/yr, OOS N ≥ 12) |
| **OOS period** | {_oos_start} to 2025-12 ({_oos_n} months) |
""" if isinstance(_total_combos, int) else """
| Dimension | Values |
|:----------|:-------|
| **Signals (9)** | IP level, YoY%, MoM%, deviation from trend, z-score, 3M momentum, 6M momentum, acceleration, contraction dummy |
| **Threshold methods (5)** | Fixed IS percentile, rolling percentile, rolling z-score, zero-crossing |
| **Strategies (3×2)** | Long/Cash, Signal-Strength, Long/Short — each in pro-cyclical and counter-cyclical orientation |
| **Lead times (5)** | 0, 1, 2, 3, 6 months |
| **Orientation** | Both pro-cyclical and countercyclical tested for each combo |
""")

with st.expander("Countercyclical orientation — how it works"):
    st.markdown(
        "Because XLP is a defensive ETF, we expect IP acceleration to be **negatively** "
        "correlated with future XLP returns. Standard threshold strategies generate a "
        "'long when above threshold' rule (pro-cyclical). For XLP, the **counter-cyclical** "
        "orientation inverts this: *long XLP when the IP signal is BELOW the threshold* "
        "(i.e., when IP growth is slow or contracting). Both orientations were tested "
        "exhaustively; the counter-cyclical strategies dominated the leaderboard."
    )

st.markdown("---")

# ===================== DIAGNOSTICS =====================
st.markdown("### Diagnostic Tests")

diag_path = _RESULTS_DIR / "core_models_20260420" / "diagnostics_summary.csv"
if diag_path.exists():
    diag_df = pd.read_csv(diag_path)
    st.dataframe(
        diag_df.style.format({"statistic": "{:.4f}"}),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Diagnostics not found.")

st.markdown("---")

# ===================== ANALYST SUGGESTIONS (ECON-AS) =====================
st.markdown("### Analyst Suggestions for Future Work (ECON-AS)")

_sugg_path = _RESULTS_DIR / "analyst_suggestions.json"
if _sugg_path.exists():
    with open(_sugg_path) as f:
        sugg = json.load(f)

    candidates = sugg.get("candidates", [])
    if candidates:
        sugg_df = pd.DataFrame(candidates)
        st.dataframe(
            sugg_df[["series", "description", "pearson_r", "p_value", "rationale"]].style.format(
                {"pearson_r": "{:.4f}", "p_value": "{:.4f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: off-scope series that showed notable correlations with "
            "XLP 3M forward returns during exploratory analysis. These are candidates "
            "for separate pair analyses and are NOT used as trading signals in this pair "
            "(per ECON-SD). pearson_r < 0 = countercyclical with XLP returns (expected direction)."
        )
    else:
        st.info("No analyst suggestions logged for this pair.")
else:
    st.info("Analyst suggestions file not found.")

st.markdown("---")

# ===================== REFERENCES =====================
st.markdown("### Key References")

st.markdown("""
- Chen, N. F., Roll, R., & Ross, S. A. (1986). Economic forces and the stock market. *Journal of Business*, 59(3), 383–403.
- Fama, E. F., & French, K. R. (1989). Business conditions and expected returns on stocks and bonds. *Journal of Financial Economics*, 25(1), 23–49.
- Stock, J. H., & Watson, M. W. (1989). New indexes of coincident and leading economic indicators. *NBER Macroeconomics Annual*, 4, 351–394.
- Jorda, O. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357–384.
- Ang, A., & Bekaert, G. (2007). Stock return predictability: Is it there? *Review of Financial Studies*, 20(3), 651–707.
- Hahn, J., & Lee, H. (2006). Yield spreads as alternative risk factors for size and book-to-market. *Journal of Financial and Quantitative Analysis*, 41(2), 245–269.
""")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    "Pair: indpro_xlp | DATE_TAG: 20260420 | "
    "Pipeline: scripts/pair_pipeline_indpro_xlp.py | "
    "Charts: scripts/generate_charts_indpro_xlp.py"
)
