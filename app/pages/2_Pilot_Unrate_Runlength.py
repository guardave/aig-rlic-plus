"""Pilot 260807 — run-length regime derivative on UNRATE × SPY (standalone evidence page).

A STANDALONE pilot-evidence page, mirroring 1_Statistical_Methods.py: page chrome only,
no pair/registry/``validate_or_die`` coupling. It surfaces the pilot artifacts that live
under ``docs/pilots/pilot260807_unrate_runlength/`` (two figures + two result tables + the
README) so the methodology pilot can be reviewed on Streamlit Cloud — the portal does not
otherwise render anything under ``docs/pilots/``.

This page exists on the pilot branch only; it is NOT part of the production pair fleet.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PILOT = os.path.join(REPO, "docs", "pilots", "pilot260807_unrate_runlength")


def _apply_page_config() -> None:
    st.set_page_config(
        page_title="Pilot: UNRATE run-length regime | AIG-RLIC+",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _img(name: str, caption: str) -> None:
    p = os.path.join(PILOT, name)
    if os.path.exists(p):
        st.image(p, caption=caption, use_container_width=True)
    else:
        st.warning(f"figure not found: {name}")


def _table(name: str, **read_kwargs) -> pd.DataFrame | None:
    p = os.path.join(PILOT, name)
    if not os.path.exists(p):
        st.warning(f"table not found: {name}")
        return None
    return pd.read_csv(p, **read_kwargs)


def render_page() -> None:
    _apply_page_config()
    render_sidebar()
    render_glossary_sidebar()

    st.title("🧪 Pilot 260807 — Run-length (3-up / 3-down) regime on UNRATE × SPY")
    st.caption("Methodology pilot (Q1 / deck Challenge 3). Evidence only — not a production "
               "pair page. Branch: `pilot260807_unrate_runlength_regime`.")

    st.error(
        "**Verdict: NEGATIVE under both framings.** A run-length regime rule on the "
        "unemployment rate does not beat the incumbent, the Sahm signal, or even "
        "buy-and-hold — but the signs are economically sensible, so the null is "
        "*too-small / too-noisy to trade*, not *no relationship*.",
        icon="🔎",
    )

    # ── Framing 1 ────────────────────────────────────────────────────────
    st.header("Framing 1 — latched signed regime state")
    st.markdown(
        "Design (fixed): **+1** after 3 consecutive monthly *rises* in unemployment "
        "(rising-unemployment regime), **−1** after 3 consecutive *falls*, latched with "
        "hysteresis; k = 3. The reproduction gate passes — the in-memory grid regenerates "
        "the live winner `chg_6m / L9 = 1.5510` exactly, so the pilot is comparable."
    )
    _img("unrate_runlen3_pilot260807.png",
         "A: unemployment + latched regime (note the wrong-regime lock-in 2016–20). "
         "B: verdict bars. C: per-lead Sharpe. D: OOS growth of $1.")

    df1 = _table("unrate_runlen3_pilot260807.csv")
    if df1 is not None:
        valid = df1[df1["valid"] == True].sort_values("oos_sharpe", ascending=False)
        st.markdown("**Best valid run-length combos** (vs incumbent 1.55 / Sahm 1.21 / B&H 0.99):")
        st.dataframe(
            valid[["direction", "strategy", "lead_months", "oos_sharpe", "max_drawdown", "oos_n"]]
            .head(8).reset_index(drop=True),
            use_container_width=True,
        )

    st.divider()

    # ── Framing 2 ────────────────────────────────────────────────────────
    st.header("Framing 2 — event study")
    st.markdown(
        "Treat the *completion* of a 3-run as a dated **event**, then ask which horizon "
        "`h` after the event has the best SPY forward performance. "
        "**Abnormal = conditional CAR(h) − unconditional CAR(h)** (removes the equity risk "
        "premium); 3-up and 3-down analysed separately; entry at event + 1-month publication "
        "lag; event-resample bootstrap 90% CI. Two event definitions: `strict` (monotonic) "
        "and `cum0.2` (rounding-aware, |3-month Δ| ≥ 0.2pp)."
    )
    _img("unrate_event_study_pilot260807.png",
         "Abnormal SPY CAR vs horizon. Signs are sensible (U-up → SPY underperforms, "
         "U-down → outperforms) but NO horizon's 90% CI clears zero; the lone h=8 down-hit "
         "is a multiple-testing artifact (1 of ~96 tests).")

    df2 = _table("unrate_event_study_pilot260807.csv")
    if df2 is not None:
        hits = df2[df2["ci_excludes_zero"] == True]
        st.markdown(
            f"Across {df2['event_def'].nunique()} definitions × 2 directions × "
            f"{int(df2['horizon_months'].max())} horizons, only **{len(hits)}** "
            "horizon(s) had a 90% CI excluding zero — consistent with noise at 90%."
        )
        st.dataframe(
            df2[["event_def", "direction", "n_events", "horizon_months",
                 "abnormal", "ci_lo", "ci_hi", "t_naive", "ci_excludes_zero"]]
            .round(4),
            use_container_width=True, height=280,
        )

    # ── Full README ──────────────────────────────────────────────────────
    readme = os.path.join(PILOT, "README.md")
    if os.path.exists(readme):
        with st.expander("Full pilot README"):
            with open(readme) as f:
                st.markdown(f.read())


render_page()
