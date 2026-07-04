"""Portal-wide Statistical Methods reference page.

A STATIC reference page: it documents every statistical / econometric method
the portal uses and how to read each one. Unlike the pair pages it has no
pair/registry/``validate_or_die`` coupling — it renders the canonical content
module ``app/components/statistical_methods.py`` (authored by Evan) and nothing
pair-specific. Streamlit auto-discovers ``app/pages/*.py``; the ``1`` prefix
places it at the top of the sidebar, directly under the Dashboard landing page.

Chrome is reused for visual consistency with the pair pages (page config +
shared CSS, the global sidebar, and the glossary sidebar) but deliberately
WITHOUT the pair breadcrumb, which requires a ``pair_id`` this page does not
have.
"""

import os
import sys

# sys.path shim so `components` resolves from the sibling dir (matches the
# pattern used by every pair page, e.g. 5_indpro_spy_evidence.py).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar
from components.statistical_methods import (
    CATEGORIES,
    METHODS,
    methods_by_category,
)

# One-line, plain-English description of what each tier is for. Keyed by the
# canonical category label in CATEGORIES; a tier without an entry still renders
# (falls back to no sub-caption) so this stays robust if Evan adds a tier.
_TIER_BLURB: dict[str, str] = {
    "Level 1 — Basic": (
        "Descriptive, mostly-linear first-pass tools. They fix the sign and "
        "timing of the indicator→target relationship cheaply, before any "
        "heavier modelling."
    ),
    "Level 2 — Advanced": (
        "Regime, dynamic, distributional and machine-learning methods. They "
        "look for structure a linear average misses — thresholds, tails, "
        "hidden states and non-linear information flow."
    ),
    "Strategy validation": (
        "The scrutiny stage. These tests ask whether a searched-for edge "
        "actually survives out-of-sample, across sub-periods, and under "
        "resampling — the honest guard against overfitting."
    ),
}


def _apply_page_config() -> None:
    """Page config + shared CSS, mirroring page_templates._apply_page_config
    but with no pair coupling."""
    st.set_page_config(
        page_title="Statistical Methods — Reference | AIG-RLIC+",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _render_method_block(method: dict) -> None:
    """Render one method as an anchored subsection: name, subtle catalog
    reference, then the three stakeholder fields under bold labels."""
    # Anchored subheader so the top-of-page jump list can target it.
    st.subheader(method["name"], anchor=method["slug"])
    st.caption(f"Reference: {method['catalog_ref']}")

    st.markdown("**What it's for**")
    st.markdown(method["what_for"])

    st.markdown("**Why it's applicable**")
    st.markdown(method["why_applicable"])

    st.markdown("**How to interpret the results**")
    st.markdown(method["how_to_interpret"])

    st.markdown("---")


def render_page() -> None:
    _apply_page_config()
    render_sidebar()
    render_glossary_sidebar()

    st.title("Statistical Methods — Reference")
    st.markdown(
        "This page documents every statistical and econometric method used "
        "across the AIG-RLIC+ portal, and — in plain language — how to read "
        "what each one produces. The pair pages apply these methods to a "
        "specific indicator→target relationship; here we describe the tools "
        "themselves, once, in a single authoritative place. For every method "
        "you'll find three things: **what it's for**, **why it's applicable** "
        "to lead/lag research, and **how to interpret the results** (including "
        "the honest caveats — what a result does, and does not, prove)."
    )

    grouped = methods_by_category()

    # ------------------------------------------------------------------ #
    # Top-of-page jump list (table of contents), grouped by tier.
    # ------------------------------------------------------------------ #
    st.markdown("#### On this page")
    for category in CATEGORIES:
        methods = grouped.get(category)
        if not methods:
            continue
        # Emit each tier group as its OWN st.markdown block so the tier label
        # sits on its own line above its links (a single \n would soft-break
        # the label onto the previous tier's last bullet).
        bullets = "\n".join(
            f"- [{method['name']}](#{method['slug']})" for method in methods
        )
        st.markdown(f"**{category}**\n\n{bullets}")
    st.markdown("---")

    # ------------------------------------------------------------------ #
    # One section per tier, one anchored block per method.
    # ------------------------------------------------------------------ #
    for category in CATEGORIES:
        methods = grouped.get(category)
        if not methods:
            continue
        st.header(category)
        blurb = _TIER_BLURB.get(category)
        if blurb:
            st.caption(blurb)
        for method in methods:
            _render_method_block(method)

    st.caption(
        f"{len(METHODS)} methods documented. Source of truth: "
        "`app/components/statistical_methods.py`."
    )


render_page()
