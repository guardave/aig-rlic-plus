"""Shared render logic for the Statistical Methods reference.

Single source of truth for the *content* of the portal-wide Statistical
Methods reference. It is deliberately chrome-free: it sets no page config,
renders no sidebar, and touches nothing pair-specific. It renders the canonical
pure-data content module ``app/components/statistical_methods.py`` (authored by
Evan) and nothing else.

Two entry points call ``render_statistical_methods()``:
  1. the standalone page ``app/pages/1_Statistical_Methods.py`` (which wraps it
     with page config + the global/glossary sidebars), and
  2. the "Statistical Methods" tab on the landing page ``app/app.py`` (inside a
     tab there is no page chrome to set — it just renders the content).

Keeping the render in one place means both entry points stay in lock-step.
"""

import streamlit as st

from components.charts import load_plotly_chart
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


def _render_method_example(method: dict, key_prefix: str = "") -> None:
    """Render the per-method illustrative example beneath the three text fields.

    The ``example`` field on each method is one of:
      * ``None`` (or a dict whose ``chart`` is ``None``) — no standalone chart
        exists for this method (e.g. ``bootstrap_significance``). We render the
        caption note only, with a graceful "no standalone chart" line if there
        is not even a caption.
      * ``{"pair": <pair_id>, "chart": <slug>, "caption": <how-to-read>}`` — we
        load the pair's rendered Plotly JSON via the portal's canonical loader
        (``components.charts.load_plotly_chart``) and render Ray's caption under
        it. The loader already guards a missing/unparseable file with the
        GATE-25 "chart pending" placeholder rather than a traceback.

    Everything is wrapped so a bad/missing example can never raise into the
    page: at worst the reader sees the caption note or a graceful placeholder.

    ``key_prefix`` disambiguates Streamlit widget keys so the SAME shared render
    function can drive both the standalone page and the landing-page tab in one
    session without duplicate-key collisions on ``st.plotly_chart``.
    """
    example = method.get("example")
    slug = method.get("slug", "unknown")

    # No example dict at all → nothing to show.
    if not example:
        return

    caption = example.get("caption")
    chart = example.get("chart")
    pair = example.get("pair")

    st.markdown("**Illustrative example**")

    # Methods with no standalone chart (e.g. bootstrap): caption note only.
    if not chart or not pair:
        st.caption(
            caption
            or "No standalone chart is produced for this method."
        )
        return

    # Load + render via the portal's canonical loader. It internally catches
    # parse/miss failures and renders a placeholder, but we still wrap the whole
    # call so nothing this method touches can raise into the surrounding page.
    key = f"methods_example_{key_prefix}_{slug}" if key_prefix else f"methods_example_{slug}"
    try:
        load_plotly_chart(
            chart,
            fallback_text=(
                "Illustrative chart will appear when the source pair's "
                "visualization is available."
            ),
            pair_id=pair,
            chart_key=key,
        )
    except Exception:  # noqa: BLE001 — render edge: never surface a traceback
        st.caption("Illustrative chart is temporarily unavailable.")

    if caption:
        st.caption(caption)
    st.caption(f"Source pair: `{pair}`.")


def _render_method_block(method: dict, key_prefix: str = "") -> None:
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

    # Real illustrative example chart (or graceful note) under the text fields.
    _render_method_example(method, key_prefix=key_prefix)

    st.markdown("---")


def render_statistical_methods(key_prefix: str = "") -> None:
    """Render the full Statistical Methods reference (title/intro + ToC +
    per-category/per-method blocks). Chrome-free: no page config, no sidebar.

    ``key_prefix`` is threaded through to every embedded example chart's
    Streamlit widget key. The standalone page passes ``"page"`` and the
    landing-page tab passes ``"tab"`` so the two instances can co-exist in one
    session without duplicate ``st.plotly_chart`` key collisions.
    """
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
            _render_method_block(method, key_prefix=key_prefix)

    st.caption(
        f"{len(METHODS)} methods documented. Source of truth: "
        "`app/components/statistical_methods.py`."
    )
