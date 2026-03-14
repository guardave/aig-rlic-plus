"""Finding 5 — Methodology: VIX/VIX3M → SPY Technical Appendix."""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="VIX/VIX3M Methodology | AIG-RLIC+",
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
    st.metric("Full Sample", "2007-01 to 2025-12", delta="~4,500 daily observations")
with col2:
    st.metric("In-Sample", "2007-01 to 2019-12", delta="Model estimation (13 years)")
with col3:
    st.metric("Out-of-Sample", "2020-01 to 2025-12", delta="Strategy evaluation (6 years)")

st.markdown("---")

# ===================== DATA SOURCES =====================
st.markdown("### Data Sources")

st.markdown("""
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **VIX (30-day implied vol)** | Yahoo Finance | ^VIX | Daily |
| **VIX3M (3-month implied vol)** | Yahoo Finance | ^VIX3M | Daily |
| **Equity prices** | Yahoo Finance | SPY | Daily |
| **Treasury yields** | FRED | DGS10, DTB3 | Daily |
| **Fed Funds Rate** | FRED | DFF | Daily |
| **VIX/VIX3M ratio** | Derived | ^VIX / ^VIX3M | Daily |
""")

st.markdown(
    '<div class="narrative-block">'
    "<b>Note on VIX3M availability:</b> The CBOE began publishing the VIX3M index "
    "in 2007. This limits the sample to 18 years — shorter than macro indicators "
    "available since the 1960s-1990s. However, the daily frequency provides "
    "substantially more observations (~4,500) than monthly series (~420 over 35 years), "
    "which partially compensates for the shorter calendar span."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ===================== STATIONARITY =====================
st.markdown("### Stationarity Tests")

stat_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..",
    "results", "vix_vix3m_spy", "stationarity_tests.csv"
)
# Try date-stamped variant
if not os.path.exists(stat_path):
    stat_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..",
        "results", "vix_vix3m_spy",
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
| Pearson / Spearman correlations | Linear and rank-order association | Multiple signal variants x forward horizons |
| Granger causality | Linear predictive relationship (both directions) | Up to 10 daily lags |
| Predictive OLS | Baseline regression with HC3 robust SEs | Multiple signals x multiple horizons |
| Local projections (Jorda) | Impulse response at multiple horizons | HAC (Newey-West) standard errors |
| Regime-dependent LP | Interaction with backwardation dummy (ratio > 1) | Tests asymmetric effect |
| Markov-Switching regression | 2-state regime identification | Switching variance |
| Quantile regression | Distributional effects | 7 quantiles (0.05 to 0.95) |
| Random Forest | Walk-forward feature importance | 200 trees, max_depth=5 |
""")

st.markdown("---")

# ===================== DIAGNOSTICS =====================
st.markdown("### Diagnostic Tests")

diag_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "..",
    "results", "vix_vix3m_spy", "diagnostics_summary.csv"
)
# Try nested path variant
if not os.path.exists(diag_path):
    alt_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..",
        "results", "vix_vix3m_spy",
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
| **Signals** | VIX/VIX3M ratio level, z-score (63d, 126d, 252d), rolling percentile, ratio change, momentum, backwardation dummy |
| **Threshold methods** | Fixed percentile (IS), rolling percentile, rolling z-score, natural boundary (ratio = 1.0), HMM prob, Markov-Switching prob |
| **Strategies (3)** | Long/Cash, Signal-Strength, Long/Short |
| **Lead times** | 0, 1, 2, 5, 10, 21 days |
| **Lookback windows** | 63d, 126d, 252d |
| **Total grid** | 916 combinations; 332 valid after pruning |
""")

st.markdown("---")

# ===================== REFERENCES =====================
st.markdown("### Key References")

st.markdown("""
- Mixon, S. (2007). The implied volatility term structure of stock index options. *Journal of Empirical Finance*, 14(3), 333-354.
- Eraker, B. (2004). Do stock prices and volatility jump? Reconciling evidence from spot and option prices. *Journal of Finance*, 59(3), 1367-1404.
- Jorda, O. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161-182.
- Whaley, R. E. (2009). Understanding the VIX. *Journal of Portfolio Management*, 35(3), 98-105.
- Bekaert, G., & Hoerova, M. (2014). The VIX, the variance premium and stock market volatility. *Journal of Econometrics*, 183(2), 181-190.
- Simon, D. P. (2003). The Nasdaq volatility index during and after the bubble. *Journal of Derivatives*, 11(2), 9-24.
""")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 2007-01 to 2025-12 | "
    "Analysis Brief: docs/analysis_brief_vix_vix3m_spy.md"
    "</div>",
    unsafe_allow_html=True,
)
