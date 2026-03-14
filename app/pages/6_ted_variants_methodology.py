"""Finding 3 — Methodology: TED Variants Technical Appendix."""

import os, sys
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(page_title="TED Methodology | AIG-RLIC+", page_icon="📐", layout="wide", initial_sidebar_state="expanded")
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
render_sidebar()
render_glossary_sidebar()

st.title("Methodology: TED Spread Variants — Technical Appendix")
st.markdown("*How we measured funding stress three different ways — and why it matters*")
st.markdown("---")

# --- Splice Analysis ---
st.markdown("### The Splice Problem")

st.markdown("""
The original indicator (SOFR minus 3M T-Bill) only exists since April 2018. To extend the history,
we investigated splicing with the classic LIBOR-based TED spread. The overlap analysis revealed:

| Comparison | Correlation | Verdict |
|:-----------|:--:|:--------|
| SOFR-DTB3 vs TEDRATE (overlap 2018-2022) | **-0.04** | Different risks — splice invalid |
| DFF-DTB3 vs TEDRATE (overlap 1993-2022) | **+0.63** | Good proxy — splice viable |

**Why the difference:** LIBOR measured *unsecured* interbank credit risk. SOFR measures *secured*
overnight repo rates. The Fed Funds rate (DFF) captures the same *funding premium* as LIBOR — what
banks pay above T-bills — making it a valid TED proxy.
""")

st.markdown("---")

# --- Variant Definitions ---
st.markdown("### Variant Definitions")

st.markdown("""
| Variant | Formula | Period | Obs | IS / OOS Split |
|:--------|:--------|:-------|:---:|:--------------|
| A: SOFR-DTB3 | `FRED:SOFR - FRED:DTB3` | 2018-04 to 2025-12 | 2,022 | 2018-04—2022-12 / 2023-01— |
| B: DFF-DTB3 | `FRED:DFF - FRED:DTB3` | 1993-01 to 2025-12 | 8,589 | 1993-01—2017-12 / 2018-01— |
| C: Spliced | `FRED:TEDRATE` (1993—2022) + affine-adjusted DFF-TED (2022—) | 1993-01 to 2025-12 | 8,589 | 1993-01—2017-12 / 2018-01— |

**Splice calibration (Variant C):** In the overlap period where both TEDRATE and DFF-TED exist,
we compute an affine adjustment: `adjusted = DFF_TED × scale + shift` where scale and shift
are fitted to match TEDRATE's mean and standard deviation.
""")

st.markdown("---")

# --- Data Sources ---
st.markdown("### Data Sources")

st.markdown("""
| Series | Source | FRED ID | Frequency | Notes |
|:-------|:-------|:--------|:----------|:------|
| SOFR | FRED | SOFR | Daily | Starts April 2018; occasional quarter-end spikes |
| 3M T-Bill (daily) | FRED | DTB3 | Daily | Secondary market rate |
| Fed Funds Rate | FRED | DFF | Daily | Effective rate; full history from 1954 |
| TED Spread (official) | FRED | TEDRATE | Daily | LIBOR-based; ends January 2022 |
| SPY | Yahoo Finance | SPY | Daily | Adjusted close |
| VIX | Yahoo Finance | ^VIX | Daily | Control variable |
| 10Y Treasury | FRED | DGS10 | Daily | For yield curve control |
""")

st.markdown("---")

# --- Stationarity ---
st.markdown("### Stationarity Tests")

st.markdown("""
All three spread variants are **stationary** (ADF p < 0.01):

| Variant | ADF Statistic | P-Value | Conclusion |
|:--------|:--:|:--:|:----------|
| SOFR-DTB3 | -5.116 | 0.0000 | Stationary |
| DFF-DTB3 | -3.908 | 0.0020 | Stationary |
| Spliced TED | -4.074 | 0.0011 | Stationary |

SPY price is non-stationary (ADF p ≈ 1.0), so forward returns (stationary) are used as the dependent variable.
""")

st.markdown("---")

# --- Methods ---
st.markdown("### Econometric Methods (Per Variant)")

st.markdown("""
| Method | Purpose | Key Parameters |
|:-------|:--------|:--------------|
| Granger causality | Test if spread predicts SPY returns (and reverse) | Up to 5 daily lags |
| Predictive OLS | Baseline regressions with HC3 robust SEs | 3 signals × 3 horizons |
| Local projections (Jorda) | Impulse response at 5d, 21d, 63d | HAC (Newey-West) SEs |
| Quantile regression | Tail risk effects | 7 quantiles (0.05 to 0.95) |
| Combinatorial tournament | 991 strategy combinations per variant | 5 leads × 6 thresholds × 3 strategies |
""")

st.markdown("---")

# --- Diagnostics per variant ---
st.markdown("### Diagnostics")

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")

for pid, label in [("sofr_ted_spy", "A: SOFR-DTB3"), ("dff_ted_spy", "B: DFF-DTB3"), ("ted_spliced_spy", "C: Spliced")]:
    diag_path = os.path.join(BASE, "results", pid, "core_models_20260314", "diagnostics_summary.csv")
    if os.path.exists(diag_path):
        st.markdown(f"**{label}**")
        st.dataframe(pd.read_csv(diag_path), use_container_width=True, hide_index=True)

st.markdown("---")

# --- Tournament Design ---
st.markdown("### Tournament Design")

st.markdown("""
| Dimension | Values |
|:----------|:-------|
| **Signals (10)** | Spread level, z-score (126d, 252d), RoC (21d, 63d), momentum (21d, 63d), percentile rank, realized vol, stress dummy |
| **Thresholds (6)** | Fixed percentile (IS) at 25th/50th/75th, Rolling percentile (252d) at 25th/50th/75th |
| **Strategies (3)** | P1 Long/Cash, P2 Signal-Strength, P3 Long/Short |
| **Lead times (5)** | 0, 1, 5, 10, 21 days |
| **Total per variant** | ~991 combinations |
| **Direction** | Counter-cyclical: BELOW threshold = bullish, ABOVE = bearish |
""")

st.markdown("---")

# --- References ---
st.markdown("### Key References")

st.markdown("""
- Brunnermeier, M. K. (2009). Deciphering the Liquidity and Credit Crunch 2007-2008. *Journal of Economic Perspectives*, 23(1), 77-100.
- Gilchrist, S., & Zakrajsek, E. (2012). Credit spreads and business cycle fluctuations. *American Economic Review*, 102(4), 1692-1720.
- ARRC (2017). *The ARRC selects a broad Repo rate as its preferred alternative reference rate.* Federal Reserve Bank of New York.
- Duffie, D., & Stein, J. C. (2015). Reforming LIBOR and other financial market benchmarks. *Journal of Economic Perspectives*, 29(2), 191-212.
""")

st.markdown("---")
st.markdown('<div class="portal-footer">Generated with AIG-RLIC+ | 3 TED variants analyzed</div>', unsafe_allow_html=True)
