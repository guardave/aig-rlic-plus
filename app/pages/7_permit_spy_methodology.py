"""Finding 4 — Methodology: PERMIT → SPY Technical Appendix."""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="Permits Methodology | AIG-RLIC+",
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

# --- Page Header ---
st.title("Methodology: Technical Appendix")
st.markdown("*For reproducibility and scrutiny.*")
st.markdown("---")

# ===================== SAMPLE =====================
st.markdown("### Sample Period")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Full Sample", "1990-01 to 2025-12", delta="~420 monthly observations")
with col2:
    st.metric("In-Sample", "1990-01 to 2017-12", delta="Model estimation (28 years)")
with col3:
    st.metric("Out-of-Sample", "2018-01 to 2025-12", delta="Strategy evaluation (8 years)")

st.markdown("---")

# ===================== DATA SOURCES =====================
st.markdown("### Data Sources")

st.markdown("""
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **Building Permits** | FRED | PERMIT | Monthly (SAAR) |
| **Equity prices** | Yahoo Finance | SPY | Daily |
| **Volatility** | Yahoo Finance | ^VIX | Daily |
| **Treasury yields** | FRED | DGS10, DTB3 | Daily |
| **Fed Funds Rate** | FRED | DFF | Daily |
| **Unemployment** | FRED | UNRATE | Monthly |
| **Housing Starts** | FRED | HOUST | Monthly |
""")

st.markdown("---")

# ===================== STATIONARITY =====================
st.markdown("### Stationarity Tests")

stat_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..",
    "results", "permit_spy", "stationarity_tests.csv"
)
# Try date-stamped variant
if not os.path.exists(stat_path):
    stat_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..",
        "results", "permit_spy",
    )
    if os.path.isdir(stat_dir):
        for f in sorted(os.listdir(stat_dir), reverse=True):
            if f.startswith("stationarity_tests") and f.endswith(".csv"):
                stat_path = os.path.join(stat_dir, f)
                break

if os.path.exists(stat_path):
    stat_df = pd.read_csv(stat_path)
    st.dataframe(stat_df, use_container_width=True, hide_index=True)
    st.caption("ADF: reject null = stationary. KPSS: fail to reject null = stationary.")
else:
    st.info("Stationarity tests not found. Run the data pipeline to generate results.")

st.markdown("---")

# ===================== METHODS =====================
st.markdown("### Econometric Methods")

st.markdown("""
| Method | Purpose | Key Detail |
|:-------|:--------|:-----------|
| Pearson / Spearman correlations | Linear and rank-order association | 8 signal variants x 4 forward horizons |
| Granger causality | Linear predictive relationship (both directions) | Up to 6 monthly lags |
| Predictive OLS | Baseline regression with HC3 robust SEs | Multiple signals x multiple horizons |
| Local projections (Jorda) | Impulse response at multiple horizons | HAC (Newey-West) standard errors |
| Regime-dependent LP | Interaction with contraction dummy | Tests asymmetric effect |
| Markov-Switching regression | 2-state regime identification | Switching variance |
| Quantile regression | Distributional effects | 7 quantiles (0.05 to 0.95) |
| Johansen cointegration | Long-run equilibrium test | Log levels, det_order=1 |
| Random Forest | Walk-forward feature importance | 200 trees, max_depth=5 |
""")

st.markdown("---")

# ===================== DIAGNOSTICS =====================
st.markdown("### Diagnostic Tests")

diag_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..",
    "results", "permit_spy", "diagnostics_summary.csv"
)
# Try nested path variant
if not os.path.exists(diag_path):
    alt_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..",
        "results", "permit_spy",
    )
    if os.path.isdir(alt_dir):
        for sub in os.listdir(alt_dir):
            sub_path = os.path.join(alt_dir, sub)
            if os.path.isdir(sub_path):
                candidate = os.path.join(sub_path, "diagnostics_summary.csv")
                if os.path.exists(candidate):
                    diag_path = candidate
                    break

if os.path.exists(diag_path):
    diag_df = pd.read_csv(diag_path)
    st.dataframe(diag_df, use_container_width=True, hide_index=True)
else:
    st.info("Diagnostics not found. Run the core models pipeline to generate results.")

st.markdown("---")

# ===================== TOURNAMENT DESIGN =====================
st.markdown("### Tournament Design")

st.markdown("""
| Dimension | Values |
|:----------|:-------|
| **Signals** | Permits level, YoY%, MoM%, deviation from trend, z-score, 3M momentum, 6M momentum, acceleration, contraction dummy |
| **Threshold methods** | Fixed percentile (IS), rolling percentile, rolling z-score, zero-crossing, HMM prob, Markov-Switching prob |
| **Strategies (3)** | Long/Cash, Signal-Strength, Long/Short |
| **Lead times** | 0, 1, 2, 3, 6 months |
| **Lookback windows** | 3Y, 5Y, 10Y |
| **Total grid** | 856 combinations; 675 valid after pruning |
""")

st.markdown("---")

# ===================== REFERENCES =====================
st.markdown("### Key References")

st.markdown("""
- Leamer, E. E. (2007). Housing IS the business cycle. *Proceedings - Economic Policy Symposium - Jackson Hole*, Federal Reserve Bank of Kansas City, 149-233.
- Stock, J. H., & Watson, M. W. (1989). New indexes of coincident and leading economic indicators. *NBER Macroeconomics Annual*, 4, 351-394.
- Stock, J. H., & Watson, M. W. (2003). Forecasting output and inflation: The role of asset prices. *Journal of Economic Literature*, 41(3), 788-829.
- Jorda, O. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161-182.
- Fama, E. F., & French, K. R. (1989). Business conditions and expected returns on stocks and bonds. *Journal of Financial Economics*, 25(1), 23-49.
- Green, R. K. (1997). Follow the leader: How changes in residential and non-residential investment predict changes in GDP. *Real Estate Economics*, 25(2), 253-270.
""")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 1990-01 to 2025-12 | "
    "Analysis Brief: docs/analysis_brief_permit_spy.md"
    "</div>",
    unsafe_allow_html=True,
)
