"""Pair 14 — The Evidence: INDPRO → XLP Statistical Analysis.

Presents the full econometric evidence for the INDPRO-XLP relationship
across correlations, causality, regimes, and machine learning.
"""

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="INDPRO × XLP Evidence | AIG-RLIC+",
    page_icon="🔬",
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
_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS_DIR = _REPO_ROOT / "results" / PAIR_ID
_EXPLORE_DIR = _RESULTS_DIR / "exploratory_20260420"
_MODELS_DIR = _RESULTS_DIR / "core_models_20260420"

# ---------------------------------------------------------------------------
# Page Header
# ---------------------------------------------------------------------------
st.title("The Evidence: What the Data Shows")
st.markdown(
    "*We tested the INDPRO-XLP relationship with 9 econometric methods across "
    "27 years of data (1998-2025). Here is what we found.*"
)
st.markdown("---")

# ---------------------------------------------------------------------------
# Tab Layout
# ---------------------------------------------------------------------------
tab_corr, tab_cause, tab_regime, tab_ml = st.tabs(
    ["Correlations", "Causality & Projections", "Regimes", "Machine Learning"]
)

# ===================== CORRELATIONS TAB =====================
with tab_corr:
    st.markdown("### Rolling Correlation: IP Growth vs XLP Return")

    load_plotly_chart(
        "indpro_xlp_correlations",
        fallback_text=(
            "Rolling 12M and 36M correlations between INDPRO YoY growth and "
            "XLP monthly return. Expected at: "
            "output/charts/indpro_xlp/plotly/indpro_xlp_correlations.json"
        ),
        caption=(
            "What this shows: how the Pearson correlation between IP YoY growth and "
            "XLP monthly returns has evolved over time. A negative reading confirms "
            "countercyclical behavior. The dashed vertical line marks the OOS start."
        ),
        pair_id=PAIR_ID,
    )

    st.markdown("---")

    # Static correlation table from exploratory results
    corr_path = _EXPLORE_DIR / "correlations.csv"
    if corr_path.exists():
        corr_df = pd.read_csv(corr_path)
        pearson = corr_df[corr_df["method"] == "Pearson"].copy()

        st.markdown("### Pearson Correlations: IP Signals vs XLP Forward Returns")

        pivot = pearson.pivot(index="signal", columns="horizon", values="correlation")
        col_order = [c for c in ["xlp_fwd_1m", "xlp_fwd_3m", "xlp_fwd_6m", "xlp_fwd_12m"] if c in pivot.columns]
        if col_order:
            pivot = pivot[col_order]
            pivot.columns = [c.replace("xlp_fwd_", "").upper() for c in pivot.columns]
            pivot.index = [s.replace("indpro_", "IP ") for s in pivot.index]
            st.dataframe(
                pivot.style.format("{:.4f}").background_gradient(cmap="RdBu_r", vmin=-0.3, vmax=0.3),
                use_container_width=True,
            )
            st.caption(
                "What this shows: Pearson correlation between each IP signal variant and "
                "XLP forward returns at 1, 3, 6, and 12-month horizons. "
                "Negative values (blue) confirm countercyclical behavior. "
                "Strongest: IP z-score → 12M forward return (r=-0.187, p=0.002)."
            )

    st.markdown("---")

    st.markdown("### Cross-Correlation Function")

    load_plotly_chart(
        "indpro_xlp_ccf",
        fallback_text=(
            "Cross-correlation function: INDPRO YoY growth vs XLP monthly return "
            "at lags -12 to +12 months. Expected at: "
            "output/charts/indpro_xlp/plotly/indpro_xlp_ccf.json"
        ),
        caption=(
            "What this shows: CCF at lags -12 to +12 months. Red bars are "
            "statistically significant. Negative lags indicate IP leading XLP. "
            "Dashed lines are 95% confidence bands."
        ),
        pair_id=PAIR_ID,
    )

# ===================== CAUSALITY TAB =====================
with tab_cause:
    st.markdown("### Granger Causality: Does IP Information Predict XLP?")

    gc_path = _MODELS_DIR / "granger_causality.csv"
    if gc_path.exists():
        gc_df = pd.read_csv(gc_path)
        st.dataframe(
            gc_df.style.format({"f_statistic": "{:.3f}", "p_value": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: Granger causality tests in both directions, lags 1-6. "
            "Rows where p_value < 0.05 indicate statistically significant Granger causality. "
            "INDPRO is a coincident indicator, so evidence of predictive causality is mixed — "
            "the publication lag (6 weeks) is the practical source of tradable information."
        )
    else:
        st.info(
            "Granger causality results not found. "
            "Run scripts/pair_pipeline_indpro_xlp.py to generate."
        )

    st.markdown("---")

    st.markdown("### Local Projections: How Does the IP Effect Evolve?")

    lp_path = _MODELS_DIR / "local_projections.csv"
    if lp_path.exists():
        lp_df = pd.read_csv(lp_path)
        st.dataframe(
            lp_df[["horizon_months", "coef_indpro_yoy", "se", "t_stat", "p_value", "r_squared", "n"]].style.format(
                {"coef_indpro_yoy": "{:.6f}", "se": "{:.6f}", "t_stat": "{:.3f}", "p_value": "{:.4f}", "r_squared": "{:.4f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: Jorda (2005) local projections with HAC (Newey-West) standard errors. "
            "The coefficient represents the marginal effect of a 1pp increase in INDPRO YoY growth "
            "on XLP forward returns at horizons of 1, 3, 6, and 12 months. "
            "Negative coefficients confirm the countercyclical hypothesis."
        )
    else:
        st.info("Local projections not found.")

    st.markdown("---")

    st.markdown("### Regime-Dependent Local Projections")

    regime_lp_path = _MODELS_DIR / "regime_local_projections.csv"
    if regime_lp_path.exists():
        rlp_df = pd.read_csv(regime_lp_path)

        st.markdown(
            '<div class="narrative-block">'
            "<b>Interpretation:</b> The regime-dependent specification tests whether "
            "the IP-XLP relationship is stronger during industrial contractions "
            "(when the countercyclical defense thesis should be most powerful). "
            "A significant interaction coefficient would confirm asymmetric effects."
            "</div>",
            unsafe_allow_html=True,
        )

        st.dataframe(
            rlp_df[["horizon_months", "coef_indpro_yoy", "coef_contraction",
                     "coef_interaction", "p_indpro", "p_contraction", "p_interaction", "r_squared"]].style.format(
                {c: "{:.4f}" for c in ["coef_indpro_yoy", "coef_contraction", "coef_interaction",
                                        "p_indpro", "p_contraction", "p_interaction", "r_squared"]}
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: OLS with IP YoY, contraction dummy, and their interaction. "
            "coef_interaction > 0 means the countercyclical IP effect is amplified during contractions."
        )

# ===================== REGIMES TAB =====================
with tab_regime:
    st.markdown("### Quantile Regression: How Does the Effect Vary Across the Return Distribution?")

    qr_path = _MODELS_DIR / "quantile_regression.csv"
    if qr_path.exists():
        qr_df = pd.read_csv(qr_path)
        st.dataframe(
            qr_df[["quantile", "coef_indpro_yoy", "se", "p_value", "ci_lower", "ci_upper"]].style.format(
                {c: "{:.6f}" for c in ["coef_indpro_yoy", "se", "ci_lower", "ci_upper"]}
            ).format({"quantile": "{:.2f}", "p_value": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: quantile regression of 3M forward XLP return on INDPRO YoY growth, "
            "at quantiles 0.05 to 0.95. Each row answers: 'at this point in the XLP return "
            "distribution, what is the marginal effect of a 1pp increase in IP growth?' "
            "Negative coefficients across quantiles confirm pervasive countercyclical behavior."
        )
    else:
        st.info("Quantile regression results not found.")

    st.markdown("---")

    st.markdown("### Regime Descriptive Statistics")

    regime_path = _EXPLORE_DIR / "regime_descriptive_stats.csv"
    if regime_path.exists():
        regime_df = pd.read_csv(regime_path)
        st.dataframe(
            regime_df.style.format({
                "mean_monthly_ret_pct": "{:.3f}",
                "ann_return_pct": "{:.2f}",
                "ann_vol_pct": "{:.2f}",
                "sharpe": "{:.3f}",
                "skewness": "{:.3f}",
                "kurtosis": "{:.3f}",
                "min_monthly_pct": "{:.2f}",
                "max_monthly_pct": "{:.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: XLP annualized return, volatility, and Sharpe ratio by "
            "INDPRO YoY growth quartile. Q1=lowest IP growth, Q4=highest. "
            "Confirms that XLP earns higher risk-adjusted returns in Q1 and Q2 "
            "(low IP growth regimes), consistent with the defensive rotation hypothesis."
        )

    st.markdown("---")

    st.markdown("### Markov-Switching Regression")

    ms_path = _MODELS_DIR / "markov_switching_2state.csv"
    if ms_path.exists():
        ms_df = pd.read_csv(ms_path)
        st.markdown(
            '<div class="narrative-block">'
            "A 2-state Markov-Switching regression was estimated on XLP returns "
            "with INDPRO YoY as exogenous variable. The model identifies two latent "
            "regimes: a low-volatility expansion regime and a high-volatility "
            "contraction/stress regime. The switching variance specification captures "
            "the well-known volatility clustering in equity returns."
            "</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(
            ms_df.style.format({"value": "{:.6f}"}),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: estimated parameters for each regime. "
            "Regime 0 typically corresponds to the low-volatility (expansion) state, "
            "Regime 1 to high-volatility (contraction) state."
        )
    else:
        st.info("Markov-Switching results not found.")

# ===================== ML TAB =====================
with tab_ml:
    st.markdown("### Random Forest Feature Importance")

    fi_path = _MODELS_DIR / "rf_feature_importance.csv"
    if fi_path.exists():
        fi_df = pd.read_csv(fi_path).sort_values("importance", ascending=False)
        st.dataframe(
            fi_df.style.format({"importance": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: feature importance from the final walk-forward window "
            "of a Random Forest classifier predicting positive 3M XLP returns. "
            "Higher importance = more predictive of XLP direction."
        )
    else:
        st.info("RF feature importance not found.")

    st.markdown("---")

    wf_path = _MODELS_DIR / "rf_walk_forward.csv"
    if wf_path.exists():
        wf_df = pd.read_csv(wf_path)
        avg_acc = wf_df["accuracy"].mean()

        st.markdown(
            '<div class="narrative-block">'
            f"<b>Walk-forward accuracy: {avg_acc:.1%}</b> across {len(wf_df)} test windows "
            f"(10yr train / 3yr test). "
            "This is modest improvement over the 50% baseline — IP signals alone are "
            "insufficient for direction prediction. The RF confirms that IP provides "
            "some marginal information, but simple momentum-based threshold strategies "
            "outperform in the tournament. The yield spread and capacity utilization "
            "consistently rank as the most important features."
            "</div>",
            unsafe_allow_html=True,
        )

        st.dataframe(
            wf_df.style.format({"accuracy": "{:.4f}", "precision": "{:.4f}", "recall": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "What this shows: test-period accuracy, precision, and recall for each "
            "walk-forward window. Sustained accuracy above 60% would indicate genuine "
            "predictive power; results near 50% suggest noise."
        )

# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### Diagnostic Tests (Baseline Regression)")

diag_path = _MODELS_DIR / "diagnostics_summary.csv"
if diag_path.exists():
    diag_df = pd.read_csv(diag_path)
    st.dataframe(
        diag_df.style.format({"statistic": "{:.4f}"}),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "What this shows: diagnostic tests on the baseline OLS regression "
        "(INDPRO YoY → 3M forward XLP return). "
        "Heteroskedasticity and serial correlation diagnostics inform whether "
        "standard HC3 robust SEs are sufficient or whether more complex corrections are needed."
    )
else:
    st.info("Diagnostics not found.")

# ---------------------------------------------------------------------------
# Transition
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    '<div class="transition-text">'
    "The statistical evidence confirms a real but nuanced INDPRO-XLP relationship. "
    "The strongest signal is at the 12M horizon (IP z-score, r=-0.19, p=0.002). "
    "The practical question: can investors use IP signals to improve XLP timing?"
    "</div>",
    unsafe_allow_html=True,
)

st.page_link(
    "pages/14_indpro_xlp_strategy.py",
    label="Continue to The Strategy",
    icon="🎯",
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "What this shows: generated with AIG-RLIC+ | "
    "Data: INDPRO (FRED) + XLP (Yahoo Finance) | 1998-01 to 2025-12 | "
    "336 monthly observations"
)
