"""HY-IG v2 -- Methodology: Technical Appendix.

Wave 2B light-touch update (2026-04-19): status-vocabulary legend expander
added at the top of the page per §3.12 and Ray's `docs/portal_glossary.json`
canonical source (RES-10). Everything else on the page remains unchanged.
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

# ----------------------------------------------------------
# Breadcrumb navigation (N10, META-PWQ)
# ----------------------------------------------------------
render_breadcrumb("Methodology", PAIR_ID)

# ----------------------------------------------------------
# Plain English expander (N8 -- Ray narrative addition)
# ----------------------------------------------------------
with st.expander("Plain English"):
    st.markdown(
        "This section explains the technical details of how we did the "
        "analysis -- which data we used, which statistical methods, and "
        "what could go wrong. Normal readers can skip it. Expert readers "
        "can use it to criticise our work and suggest improvements."
    )

# ---------------------------------------------------------------------------
# Page Header -- address skepticism
# ---------------------------------------------------------------------------
st.title("Methodology: Technical Appendix")
st.markdown(
    "*For the skeptical reader: this section provides the full methodological "
    "detail needed to replicate, challenge, or extend our analysis. Every claim "
    "in the preceding pages traces back to a specific method, dataset, and "
    "diagnostic described here.*"
)
st.markdown("---")

# ---------------------------------------------------------------------------
# Status vocabulary legend (§3.12 + RES-10) — loaded from canonical glossary.
# ---------------------------------------------------------------------------
_GLOSSARY_PATH = Path(__file__).resolve().parents[2] / "docs" / "portal_glossary.json"
if _GLOSSARY_PATH.exists():
    with open(_GLOSSARY_PATH) as _gf:
        _glossary = json.load(_gf)
    _status = _glossary.get("status_labels", {})
    with st.expander(
        "What do status labels (*Available*, *Pending*, *Validated*, *Stale*, "
        "*Draft*, *Mature*, *Unknown*) mean?",
        expanded=False,
    ):
        for _label, _definition in _status.items():
            if _label.startswith("_"):
                continue
            st.markdown(f"- **{_label}** — {_definition}")
        st.caption(
            "What this shows: canonical source is "
            "`docs/portal_glossary.json` (Rule RES-10 / SOP §3.12)."
        )
    st.markdown("---")

# ---------------------------------------------------------------------------
# Sample Period  (Metric Interpretation Rule)
# ---------------------------------------------------------------------------
st.markdown("### Sample Period")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Full Sample", "2000-01 to 2025-12", delta="~6,500 daily observations")
with col2:
    st.metric("In-Sample", "2000-01 to 2017-12", delta="Model estimation (~4,500 obs)")
with col3:
    st.metric("Out-of-Sample", "2018-01 to 2025-12", delta="Strategy evaluation (~2,000 obs)")

st.caption(
    "Why this matters: the 70/30 in-sample/out-of-sample split provides a "
    "generous 8-year out-of-sample window that includes multiple distinct "
    "market episodes (2018 volatility spike, COVID crash, 2022 rate shock, "
    "2023-25 recovery), preventing the strategy from being validated on "
    "only one type of market environment."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Data Sources
# ---------------------------------------------------------------------------
st.markdown("### Data Sources")

st.markdown(
    "All data is sourced from publicly available databases accessible through our "
    "MCP server stack:"
)

st.markdown("""
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **Credit spreads (in scope)** | FRED | BAMLH0A0HYM2 (HY OAS), BAMLC0A0CM (IG OAS) | Daily |
| **Quality spreads (context only)** | FRED | BAMLH0A1HYBB (BB OAS), BAMLH0A3HYC (CCC OAS), BAMLC0A4CBBB (BBB OAS) | Daily |
| **Equity prices (in scope)** | Yahoo Finance | SPY (adjusted close) | Daily |
| **Volatility (context only)** | Yahoo Finance | ^VIX, ^VIX3M, ^MOVE | Daily |
| **Macro variables (context only)** | FRED | DGS10, DGS2, DTB3, NFCI, ICSA, DFF, SOFR, STLFSI2 | Daily/Weekly |
| **Cross-asset (context only)** | Yahoo Finance | GC=F, HG=F, DX-Y.NYB, HYG, KBE, IWM | Daily |

*Scope discipline (ECON-SD).* Only the **in-scope** rows above feed the Signal Universe,
regressions, and tournament for this pair. The **context only** rows are pulled by the
data pipeline for exploratory correlation work; any predictive signals they generated
(e.g., NFCI Momentum, Bank/Small-Cap Ratio, Yield Curve 10Y-3M, BBB-IG Spread, CCC-BB
Quality Spread) are logged in **Analyst Suggestions for Future Work** below and are
**not** part of this pair's analysis. The authoritative in-scope list is the Signal
Universe tables rendered from `signal_scope.json`.
""")

st.markdown("---")

# ---------------------------------------------------------------------------
# Indicator Construction
# ---------------------------------------------------------------------------
st.markdown("### Indicator Construction")

st.markdown(
    "The primary indicator is the HY-IG spread: BAMLH0A0HYM2 minus BAMLC0A0CM, "
    "measured in basis points. From this raw spread, we derive transformed series "
    "including z-scores (252-day and 504-day rolling windows), percentile ranks (504-day "
    "and 1260-day), rates of change (21-day, 63-day, 126-day), momentum changes, and "
    "acceleration. The authoritative list of in-scope derivatives is rendered from "
    "`signal_scope.json` in the **Signal Universe** section below. Related quality-spread "
    "signals (e.g., CCC-BB) were noted during exploration but are out of scope for this "
    "pair — see *Analyst Suggestions for Future Work* below."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Signal Universe (ECON-UD -- Wave 7B; rendered from signal_scope.json)
# ---------------------------------------------------------------------------
# Ray may later feed intro prose into this section via the narrative
# frontmatter (RES-17 anchor `signal_universe`). Until then, the section
# carries its own plain-English lead-in.
st.markdown("### Signal Universe")

st.markdown(
    "This section lists every derivative of the HY-IG spread (indicator axis) "
    "and of SPY (target axis) that was considered during the analysis. It is "
    "the single source of truth for what is **in scope** for this pair. "
    "Anything that is not in these two tables was deliberately excluded from "
    "the pair's charts, regressions, and tournament — and is instead logged "
    "in the sibling *Analyst Suggestions* section below."
)

render_signal_universe(PAIR_ID)

st.markdown("---")

# ---------------------------------------------------------------------------
# Analyst Suggestions for Future Work (ECON-AS -- Wave 7B)
# ---------------------------------------------------------------------------
# Narrative frontmatter anchor (Ray, RES-17): `analyst_suggestions`.
st.markdown("### Analyst Suggestions for Future Work")

st.markdown(
    "During the HY-IG × SPY analysis, the team occasionally observed signals "
    "outside this pair's formal scope that looked worth exploring in future "
    "work (a different pair, a variant family extension, or a regime "
    "overlay). Those observations are captured below — **for the record "
    "only**. They did not influence this pair's winning strategy, and the "
    "renderer carries an explicit disclaimer to reinforce the read-only, "
    "non-ticket nature of the list."
)

render_analyst_suggestions(PAIR_ID)

st.markdown("---")

# ----------------------------------------------------------
# Return Basis Note (N13 -- metric basis clarification)
# ----------------------------------------------------------
st.markdown("### Return Basis and Performance Metrics")

st.markdown(
    "All OOS return figures reported on the Story and Strategy pages "
    "(e.g. **+11.3% annualized**) are **arithmetic** annualized returns -- "
    "the mean daily return multiplied by 252 trading days. This matches the "
    "numerator of the OOS Sharpe ratio (mean divided by standard deviation). "
    "**Compounded CAGR** (geometric annualized return, "
    "(1 + total_return)^(1/years) - 1) would be slightly different because "
    "it accounts for path dependence and volatility drag; for the winning "
    "strategy the CAGR and arithmetic return differ by less than ~50 bps. "
    "We report the arithmetic figure throughout for consistency with the "
    "Sharpe ratio and tournament leaderboard."
)

st.markdown("---")

# ----------------------------------------------------------
# Stationarity Tests
# ----------------------------------------------------------
st.markdown("### Stationarity Tests")

_stat_path = _RESULTS_DIR / "stationarity_tests_20260410.csv"
if _stat_path.exists():
    _stat_df = pd.read_csv(_stat_path)
    st.dataframe(_stat_df, use_container_width=True, hide_index=True)
    st.caption(
        "How to read it: ADF — reject null = stationary. KPSS — fail to "
        "reject null = stationary."
    )
else:
    st.info(
        "Stationarity tests not found.\n\n"
        "Plain English: the CSV of ADF + KPSS stationarity-test results "
        "has not been produced yet. Stationarity tests tell us whether a "
        "time series has a stable long-run mean (required for many "
        "regression methods). Re-run the econometrics pipeline to "
        "generate this table."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Econometric Methods -- with "Why We Chose It" column
# ---------------------------------------------------------------------------
st.markdown("### Econometric Methods")

st.markdown(
    "Each method was chosen to answer a specific question about the credit-equity "
    "relationship. We used multiple methods deliberately: if a finding holds across "
    "techniques with different assumptions, we can be far more confident it is genuine."
)

st.markdown("""
| Method | Question It Answers | Why We Chose It |
|:-------|:-------------------|:----------------|
| Toda-Yamamoto Granger causality | Does credit lead equity, or vice versa? | Works correctly with non-stationary data (unlike standard Granger), which matters because spread levels contain trends. Augmented VAR, lags selected by BIC + d_max = 1. |
| Transfer entropy (Diks-Panchenko) | Is the information flow nonlinear? | Captures threshold effects and asymmetries that linear Granger tests miss -- important because the credit-equity link strengthens nonlinearly during stress. |
| Local projections (Jorda) | How does a credit shock affect stocks over time? | Does not require specifying the full system dynamics, making it robust to misspecification. h = 1, 5, 10, 21, 42, 63 days; state-dependent versions. |
| Markov-switching regression | Are there distinct regimes with different dynamics? | Lets the data find the regime boundaries rather than imposing arbitrary thresholds. 2-state and 3-state. |
| Gaussian HMM | What regime is the market in right now? | Jointly models HY-IG changes and VIX to infer the hidden state in real time -- powers the winning strategy. 2-state and 3-state. |
| Quantile regression | Does credit primarily warn of bad outcomes? | Estimates the effect at different points in the return distribution, confirming the signal is concentrated in the left tail. tau = 0.05 to 0.90. |
| GJR-GARCH | Does credit stress increase stock volatility asymmetrically? | Captures the leverage effect while including credit spreads as an external driver. SPY returns with HY-IG exogenous. |
| Random Forest + SHAP | Which signal transformations matter most? | Nonlinear, non-parametric check on the linear models. Walk-forward with 1-year test windows prevents lookahead bias. |
| Combinatorial tournament | Which strategy actually works out-of-sample? | Systematically tests ~1,000+ combinations on held-out data, then stress-tests the winners. OOS Sharpe ranking. |
""")

st.markdown("---")

# ---------------------------------------------------------------------------
# Diagnostics -- with "Why It Matters" column
# ---------------------------------------------------------------------------
st.markdown("### Diagnostic Tests")

st.markdown(
    "Every model undergoes a battery of diagnostic tests to ensure the results are "
    "trustworthy:"
)

st.markdown("""
| Test | What It Checks | Why It Matters |
|:-----|:---------------|:---------------|
| Jarque-Bera | Whether residuals follow a bell curve (normality) | If not, our confidence intervals may be wrong |
| Breusch-Pagan | Whether the scatter of residuals is even (homoskedasticity) | Uneven scatter means some predictions are more reliable than others |
| Breusch-Godfrey | Whether residuals are correlated with their own past values (serial correlation) | Correlated residuals inflate our confidence in results |
| RESET | Whether the model's functional form is correct (specification) | Catches cases where we should use a curve instead of a straight line |
| ADF + KPSS | Whether the data has trends that need to be removed (stationarity) | Using trended data in level regressions produces spurious results |
""")

# --- HAC justification inline ---
st.markdown(
    "**HC3 robust standard errors** are reported throughout. We use HC3 rather than "
    "conventional standard errors because our forward returns overlap in time -- a "
    "63-day return calculated today shares 62 days with tomorrow's 63-day return. "
    "Without this correction, we would systematically overstate our confidence in "
    "every result. For specifications with longer forecast horizons, we use "
    "**HAC (Newey-West) standard errors**, which additionally correct for the "
    "autocorrelation introduced by overlapping windows."
)

_diag_path = _RESULTS_DIR / "core_models_20260410" / "diagnostics_summary.csv"
if _diag_path.exists():
    _diag_df = pd.read_csv(_diag_path)
    st.dataframe(_diag_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Sensitivity Analysis
# ---------------------------------------------------------------------------
st.markdown("### Sensitivity Analysis")

st.markdown(
    "To ensure our results are not driven by any single time period or parameter "
    "choice, we tested:"
)

st.markdown("""
- Full sample vs. excluding GFC (2007-2009)
- Full sample vs. excluding COVID (2020)
- Pre-2008 vs. post-2008 sub-samples
- Alternative lag structures (BIC, AIC, fixed 5/10/21)
- Alternative threshold levels and methods
- Walk-forward validation with rolling windows
""")

st.markdown("---")

# ---------------------------------------------------------------------------
# Reverse Causality Check
# ---------------------------------------------------------------------------
st.markdown("### Reverse Causality Check")

st.markdown(
    "All lead-lag and predictive claims include a reverse-causality test: the same "
    "model is estimated with SPY leading HY-IG as well as HY-IG leading SPY. Both "
    "sets of results are reported side by side. Local projection impulse responses are "
    "compared in both directions. The finding of bidirectional causality is documented "
    "and its implications discussed -- specifically, that the credit-to-equity signal "
    "strengthens in stress regimes while the equity-to-credit signal dominates in calm "
    "regimes. This bidirectionality is not a problem for our strategy -- it is a feature "
    "that the regime-switching framework explicitly exploits."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Tournament Design
# ---------------------------------------------------------------------------
st.markdown("### Tournament Design")

st.markdown("""
| Dimension | Values |
|:----------|:-------|
| **Signals** | Spread level, z-scores (252d/504d), percentile ranks (504d/1260d), RoC (21d/63d/126d), momentum (21d/63d/252d), acceleration, HMM stress/calm probabilities, Markov-switching stress probability. Authoritative list: see **Signal Universe** rendered from `signal_scope.json`. |
| **Threshold methods (7)** | Fixed percentile (IS), rolling percentile, rolling z-score, Bollinger bands, zero-crossing, HMM prob, Markov-switching prob |
| **Strategies (4)** | Long/Cash, Signal-Strength, Long/Short, Inverse-Signal |
| **Lead times (9)** | 0, 1, 2, 3, 5, 10, 21, 42, 63 days |
| **Lookback windows (4)** | 126d, 252d, 504d, 1260d |
| **Total grid** | ~1,000+ after pruning |
""")

st.markdown("---")

# ----------------------------------------------------------
# References (N7 -- Ray narrative addition, 17 entries in 4 categories)
# ----------------------------------------------------------
st.markdown("### References")

st.markdown(
    "Below is the consolidated reference list cited by this narrative. Where "
    "an in-text reference uses `[AuthorYear]` notation (e.g. `[Merton1974]`), "
    "the entry here is the source. The full analysis brief "
    "(`docs/analysis_brief_hy_ig_v2_spy_20260410.md`) carries the extended "
    "25-citation list used during the background scoping phase."
)

st.markdown("#### Credit Spread & Equity Research")
st.markdown(
    "- `[Gilchrist2012]` Gilchrist, S. & Zakrajsek, E. (2012). \"Credit Spreads and Business Cycle Fluctuations,\" *American Economic Review* 102(4), 1692-1720.\n"
    "- `[Merton1974]` Merton, R.C. (1974). \"On the Pricing of Corporate Debt: The Risk Structure of Interest Rates,\" *Journal of Finance* 29(2), 449-470.\n"
    "- `[Merton1973]` Merton, R.C. (1973). \"Theory of Rational Option Pricing,\" *Bell Journal of Economics & Management Science* 4(1), 141-183.\n"
    "- `[Philippon2009]` Philippon, T. (2009). \"The Bond Market's q,\" *Quarterly Journal of Economics* 124(3), 1011-1056.\n"
    "- `[Acharya2007]` Acharya, V.V. & Johnson, T.C. (2007). \"Insider Trading in Credit Derivatives,\" *Journal of Financial Economics* 84(1), 110-141."
)

st.markdown("#### Methodology -- Time Series Econometrics")
st.markdown(
    "- `[Toda1995]` Toda, H.Y. & Yamamoto, T. (1995). \"Statistical Inference in Vector Autoregressions with Possibly Integrated Processes,\" *Journal of Econometrics* 66, 225-250.\n"
    "- `[Jorda2005]` Jorda, O. (2005). \"Estimation and Inference of Impulse Responses by Local Projections,\" *American Economic Review* 95(1), 161-182.\n"
    "- `[Koenker1978]` Koenker, R. & Bassett, G. (1978). \"Regression Quantiles,\" *Econometrica* 46(1), 33-50.\n"
    "- `[Koenker2001]` Koenker, R. & Hallock, K.F. (2001). \"Quantile Regression,\" *Journal of Economic Perspectives* 15(4), 143-156.\n"
    "- `[Hamilton1989]` Hamilton, J.D. (1989). \"A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle,\" *Econometrica* 57(2), 357-384.\n"
    "- `[Schreiber2000]` Schreiber, T. (2000). \"Measuring Information Transfer,\" *Physical Review Letters* 85(2), 461-464.\n"
    "- `[Diks2006]` Diks, C. & Panchenko, V. (2006). \"A new statistic and practical guidelines for nonparametric Granger causality testing,\" *Journal of Economic Dynamics & Control* 30, 1647-1669."
)

st.markdown("#### Regime Detection & Risk")
st.markdown(
    "- `[Guidolin2007]` Guidolin, M. & Timmermann, A. (2007). \"Asset allocation under multivariate regime switching,\" *Journal of Economic Dynamics & Control* 31, 3503-3544.\n"
    "- `[AngTimmermann2012]` Ang, A. & Timmermann, A. (2012). \"Regime Changes and Financial Markets,\" *Annual Review of Financial Economics* 4, 313-337.\n"
    "- `[Adrian2019]` Adrian, T., Boyarchenko, N. & Giannone, D. (2019). \"Vulnerable Growth,\" *American Economic Review* 109(4), 1263-1289."
)

st.markdown("#### HY-IG Specific")
st.markdown(
    "- `[Chen2007]` Chen, L., Lesmond, D.A. & Wei, J. (2007). \"Corporate Yield Spreads and Bond Liquidity,\" *Journal of Finance* 62(1), 119-149."
)

st.caption(
    "What this shows: the full analysis brief "
    "(`docs/analysis_brief_hy_ig_v2_spy_20260410.md`) "
    "carries the complete list of academic citations."
)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | Data: 2000-01 to 2025-12 | "
    "Analysis Brief: docs/analysis_brief_hy_ig_v2_spy_20260410.md."
)
