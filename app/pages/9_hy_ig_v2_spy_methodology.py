"""HY-IG v2 — Methodology: Technical Appendix."""

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="HY-IG v2 Methodology | AIG-RLIC+",
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

PAIR_ID = "hy_ig_v2_spy"
_RESULTS_DIR = Path(__file__).resolve().parents[2] / "results" / PAIR_ID

# --- Page Header ---
st.title("Methodology: Technical Appendix")
st.markdown("*For reproducibility and scrutiny.*")
st.markdown("---")

# ===================== SAMPLE =====================
st.markdown("### Sample Period")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Full Sample", "2000-01 to 2025-12", delta="~6,500 daily observations")
with col2:
    st.metric("In-Sample", "2000-01 to 2017-12", delta="Model estimation (~4,500 obs)")
with col3:
    st.metric("Out-of-Sample", "2018-01 to 2025-12", delta="Strategy evaluation (~2,000 obs)")

st.markdown("---")

# ===================== DATA SOURCES =====================
st.markdown("### Data Sources")

st.markdown("""
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **Credit spreads** | FRED | BAMLH0A0HYM2 (HY OAS), BAMLC0A0CM (IG OAS) | Daily |
| **Quality spreads** | FRED | BAMLH0A1HYBB (BB OAS), BAMLH0A3HYC (CCC OAS), BAMLC0A4CBBB (BBB OAS) | Daily |
| **Equity prices** | Yahoo Finance | SPY (adjusted close) | Daily |
| **Volatility** | Yahoo Finance | ^VIX, ^VIX3M, ^MOVE | Daily |
| **Macro variables** | FRED | DGS10, DGS2, DTB3, NFCI, ICSA, DFF, SOFR, STLFSI2 | Daily/Weekly |
| **Cross-asset** | Yahoo Finance | GC=F, HG=F, DX-Y.NYB, HYG, KBE, IWM | Daily |
""")

st.markdown("---")

# ===================== INDICATOR CONSTRUCTION =====================
st.markdown("### Indicator Construction")

st.markdown(
    "The primary indicator is the HY-IG spread: BAMLH0A0HYM2 minus BAMLC0A0CM, "
    "measured in basis points. From this raw spread, we derive 20 transformed series "
    "including z-scores (252d and 504d rolling windows), percentile ranks (504d and "
    "1260d), rates of change (21d, 63d, 126d), momentum changes, acceleration, and "
    "the CCC-BB quality spread."
)

st.markdown("---")

# ===================== STATIONARITY =====================
st.markdown("### Stationarity Tests")

_stat_path = _RESULTS_DIR / "stationarity_tests_20260410.csv"
if _stat_path.exists():
    _stat_df = pd.read_csv(_stat_path)
    st.dataframe(_stat_df, use_container_width=True, hide_index=True)
    st.caption("ADF: reject null = stationary. KPSS: fail to reject null = stationary.")
else:
    st.info("Stationarity tests not found.")

st.markdown("---")

# ===================== METHODS =====================
st.markdown("### Econometric Methods")

st.markdown("""
| Method | Purpose | Key Parameter |
|:-------|:--------|:--------------|
| Toda-Yamamoto Granger causality | Linear causality in both directions | Augmented VAR, lags selected by BIC + d_max = 1 |
| Transfer entropy (Diks-Panchenko) | Nonlinear information flow | Bandwidth per Diks & Panchenko (2006) |
| Local projections (Jorda) | Impulse responses at multiple horizons | h = 1, 5, 10, 21, 42, 63 days; state-dependent |
| Markov-switching regression | Regime identification | 2-state and 3-state |
| Gaussian HMM | Joint regime identification on HY-IG + VIX | 2-state and 3-state |
| Quantile regression | Distributional effects on return tails | tau = 0.05, 0.10, 0.25, 0.50, 0.75, 0.90 |
| GJR-GARCH | Volatility dynamics with asymmetry | SPY returns with HY-IG exogenous |
| Random Forest + SHAP | Nonlinear feature importance | Walk-forward, 1-year test windows |
| Combinatorial tournament | Strategy optimization | ~1,000 combinations, OOS Sharpe ranking |
""")

st.markdown("---")

# ===================== DIAGNOSTICS =====================
st.markdown("### Diagnostic Tests")

st.markdown(
    "Every model undergoes: Jarque-Bera (normality), Breusch-Pagan "
    "(heteroskedasticity), Breusch-Godfrey (serial correlation), RESET "
    "(functional form), and stationarity confirmation (ADF + KPSS confirmatory "
    "approach). HC3 robust standard errors are reported by default."
)

_diag_path = _RESULTS_DIR / "core_models_20260410" / "diagnostics_summary.csv"
if _diag_path.exists():
    _diag_df = pd.read_csv(_diag_path)
    st.dataframe(_diag_df, use_container_width=True, hide_index=True)
else:
    st.info("Diagnostics summary not found.")

st.markdown("---")

# ===================== SENSITIVITY =====================
st.markdown("### Sensitivity Analysis")

st.markdown("""
- Full sample vs. excluding GFC (2007-2009)
- Full sample vs. excluding COVID (2020)
- Pre-2008 vs. post-2008 sub-samples
- Alternative lag structures (BIC, AIC, fixed 5/10/21)
- Alternative threshold levels and methods
- Walk-forward validation with rolling windows
""")

st.markdown("---")

# ===================== REVERSE CAUSALITY =====================
st.markdown("### Reverse Causality Check (G11 Requirement)")

st.markdown(
    "All lead-lag and predictive claims include a reverse-causality test: the same "
    "model is estimated with SPY -> HY-IG as well as HY-IG -> SPY. Both sets of "
    "results are reported side by side. Local projection impulse responses are compared "
    "in both directions. The finding of bidirectional causality is documented and its "
    "implications discussed -- specifically, that the credit-to-equity signal strengthens "
    "in stress regimes while the equity-to-credit signal dominates in calm regimes."
)

st.markdown("---")

# ===================== TOURNAMENT DESIGN =====================
st.markdown("### Tournament Design")

st.markdown("""
| Dimension | Values |
|:----------|:-------|
| **Signals (13)** | Spread level, z-scores (252d/504d), percentile ranks, RoC (21d/63d/126d), momentum, acceleration, quality spread (CCC-BB), HMM stress prob, Markov-switching prob |
| **Threshold methods (7)** | Fixed percentile (IS), rolling percentile, rolling z-score, Bollinger bands, zero-crossing, HMM prob, Markov-switching prob |
| **Strategies (4)** | Long/Cash, Signal-Strength, Long/Short, Inverse-Signal |
| **Lead times (9)** | 0, 1, 2, 3, 5, 10, 21, 42, 63 days |
| **Lookback windows (4)** | 126d, 252d, 504d, 1260d |
| **Total grid** | ~1,000+ after pruning |
""")

st.markdown("---")

# ===================== REFERENCES =====================
st.markdown("### Key References")

st.markdown("""
- Acharya, V. V., & Johnson, T. C. (2007). Insider trading in credit derivatives. *Journal of Financial Economics*, 84(1), 110-141.
- Adrian, T., Boyarchenko, N., & Giannone, D. (2019). Vulnerable Growth. *American Economic Review*, 109(4), 1263-1289.
- Gilchrist, S., & Zakrajsek, E. (2012). Credit spreads and business cycle fluctuations. *American Economic Review*, 102(4), 1692-1720.
- Guidolin, M., & Timmermann, A. (2007). Asset allocation under multivariate regime switching. *Journal of Economic Dynamics and Control*, 31(11), 3503-3544.
- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357-384.
- Jorda, O. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161-182.
- Merton, R. C. (1974). On the pricing of corporate debt: The risk structure of interest rates. *Journal of Finance*, 29(2), 449-470.
- Philippon, T. (2009). The bond market's Q. *Quarterly Journal of Economics*, 124(3), 1011-1056.
""")

st.markdown(
    "See the full analysis brief (`docs/analysis_brief_hy_ig_v2_spy_20260410.md`) "
    "for the complete list of academic citations."
)

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data: 2000-01 to 2025-12 | "
    "Analysis Brief: docs/analysis_brief_hy_ig_v2_spy_20260410.md"
    "</div>",
    unsafe_allow_html=True,
)
