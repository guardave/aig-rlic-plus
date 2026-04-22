"""Page Template Abstraction for AIG-RLIC+ Portal Pages (Rule APP-PT1).

This module centralises the structural decisions for the four canonical pair
pages — Story / Evidence / Strategy / Methodology. New pairs should NOT
author page files from scratch; instead, they should write a pair-specific
config (`app/pair_configs/{pair_id}_config.py`) and then expose four thin
wrappers under `app/pages/{n}_{pair_id}_*.py` that do nothing but call the
corresponding template function here.

Why this exists (Wave 10D+ post-Evidence-layout drift):
    Prior to this module every pair's four pages were copy-pasted from the
    HY-IG v2 reference. That produced repeated bugs:
      - Breadcrumb missing on indpro_xlp pages (Wave 10D).
      - Evidence page flat 4-tab layout instead of Level-1 / Level-2
        hierarchy.
      - Signal Universe silently empty because the schema migrated under
        the reader (closed by APP-SS1).
      - Direction-check not invoked on Strategy pages.
    Each bug had to be retro-applied to N files. APP-PT1 fixes the class of
    bug by centralising structure here and forcing page files to be thin
    wrappers.

Public contract (Rule APP-PT1):
    render_story_page(pair_id: str) -> None
    render_evidence_page(pair_id: str, method_blocks: dict) -> None
    render_strategy_page(pair_id: str) -> None
    render_methodology_page(pair_id: str, config: MethodologyConfig) -> None

See also:
    - Rule APP-PT1 in `docs/agent-sops/appdev-agent-sop.md`
    - Rule APP-SEV1 (severity policy — loud-error / loud-warning / caption)
    - Rule APP-SS1 (signal_scope.json consumer contract)
    - Rule APP-WS1 (winner_summary.json consumer contract)
    - Rule APP-DIR1 (direction triangulation at page load)
    - Rule APP-CC1 (caption-prefix canonical vocabulary)
    - Rule APP-EX1 (expander-title canonical registry)
"""

from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from components.analyst_suggestions_table import render_analyst_suggestions
from components.breadcrumb import render_breadcrumb
from components.charts import load_plotly_chart
from components.direction_check import render_direction_check
from components.instructional_trigger_cards import render_instructional_trigger_cards
from components.live_execution_placeholder import render_live_execution_placeholder
from components.metrics import kpi_row
from components.narrative import (
    render_glossary_sidebar,
    render_narrative,
    render_transition,
)
from components.position_adjustment_panel import render_position_adjustment_panel
from components.probability_engine_panel import render_probability_engine_panel
from components.pair_registry import get_page_prefix
from components.sidebar import render_sidebar
from components.signal_universe_table import render_signal_universe


# ---------------------------------------------------------------------------
# Canonical palette (v1.0.0 — derived from HY-IG v2 reference pair).
# APP-PT1 §color-palette-in-one-place: this dict is the single source of
# truth for chart / metric coloring. Reference it; do not re-specify.
# ---------------------------------------------------------------------------
PALETTE: dict[str, str] = {
    # Winner / strategy accents
    "winner": "#2E7D32",            # reference-pair strategy-success green
    "benchmark": "#757575",          # grey for buy-and-hold comparison
    "stress": "#C62828",             # red for stress-regime bars / warnings
    "calm": "#1565C0",               # blue for calm-regime bars
    "neutral": "#455A64",            # dark slate for neutral captions

    # Indicator / target encoding
    "indicator": "#EF6C00",          # orange — used for INDPRO-style indicator series
    "target": "#283593",             # indigo — used for target equity series

    # Deltas / metric accent
    "delta_positive": "#2E7D32",
    "delta_negative": "#C62828",
    "delta_neutral": "#607D8B",
}


# ---------------------------------------------------------------------------
# Repo root resolver — components are imported from multiple working
# directories (page file, smoke harness, cloud build). The loader contract
# in `charts.py` already assumes three `parents[2]` levels from this module
# reach the repo root. Reuse that convention.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# MethodologyConfig dataclass — the structured content a pair config must
# provide for the Methodology page. The rest (signal universe, stationarity
# tests, analyst suggestions) is read from disk by the template.
# ---------------------------------------------------------------------------
@dataclass
class MethodologyConfig:
    """Pair-specific content required by ``render_methodology_page``.

    All fields are markdown-formatted strings or lists of markdown rows.
    Templates render them verbatim. Anything derivable from JSON / CSV
    artifacts (signal universe, stationarity tests, sample period) is NOT
    included here — the template reads those directly.
    """

    data_sources_table_md: str
    """A markdown table listing the pair's data sources. See
    `docs/agent-sops/appdev-agent-sop.md` Methodology-page spec for the
    canonical column set (Category / Source / Series / Frequency)."""

    indicator_construction_md: str
    """Markdown narrative describing how the pair's signals are constructed
    from the raw indicator column. Referenced from signal_scope.json but
    NOT derivable from it (prose explanation)."""

    methods_table_md: str
    """Markdown table listing every econometric method used (Method /
    Question It Answers / Why We Chose It) per the Methodology-page
    canonical layout."""

    tournament_design_md: str
    """Markdown table describing the tournament grid dimensions (Signals /
    Thresholds / Strategies / Lead times / etc.)."""

    references_md: str
    """Markdown reference list — citations grouped by topic (`#### Topic`
    subheadings allowed). Renderer appends a final canonical caption."""

    sample_period_note: str = ""
    """Optional caption under the sample-period metrics row. Empty falls
    back to the canonical wording."""

    plain_english: str = ""
    """Optional pair-specific Plain English expander content for the
    Methodology page. Empty falls back to the canonical generic blurb."""


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _apply_page_config(page_title: str, icon: str) -> None:
    """Apply page config + load shared CSS. Idempotent in practice — Streamlit
    accepts a single ``set_page_config`` per page file, and templates are called
    from thin page wrappers that execute top-to-bottom exactly once."""
    st.set_page_config(
        page_title=page_title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _load_winner_summary(pair_id: str) -> dict[str, Any] | None:
    """Load ``winner_summary.json`` for a pair.

    APP-SEV1 L1: if the file is missing or invalid JSON, surface an
    ``st.error(...)`` and return None. Callers MUST check for None and
    short-circuit rendering of downstream sections that depend on it.
    """
    path = _REPO_ROOT / "results" / pair_id / "winner_summary.json"
    if not path.exists():
        st.error(
            f"**winner_summary.json missing for `{pair_id}`** (APP-SEV1 L1).\n\n"
            "Plain English: this page's headline metrics, signal description, "
            "and strategy rule all come from `winner_summary.json`. Without "
            "that file the page cannot responsibly render — re-run the "
            "tournament pipeline to produce it."
        )
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        st.error(
            f"**winner_summary.json for `{pair_id}` is not valid JSON** "
            f"(APP-SEV1 L1): {exc}\n\n"
            "Plain English: the JSON file was found on disk but its contents "
            "could not be parsed. This is a producer-side bug — re-generate "
            "it via the tournament pipeline to fix."
        )
        return None


def _load_interpretation_metadata(pair_id: str) -> dict[str, Any]:
    """Load ``interpretation_metadata.json`` (soft load).

    Return empty dict if missing — the Story page degrades gracefully with
    an empty mechanism string rather than short-circuiting (this artifact
    carries narrative context, not page-critical data)."""
    path = _REPO_ROOT / "results" / pair_id / "interpretation_metadata.json"
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def _latest_dated_file(pair_id: str, prefix: str, ext: str = "csv") -> Path | None:
    """Return the latest file matching ``{prefix}_YYYYMMDD.{ext}`` under the
    pair's results dir, or None if no match. APP-PT1 §dated-file-globbing."""
    pattern = str(_REPO_ROOT / "results" / pair_id / f"{prefix}_*.{ext}")
    matches = sorted(glob.glob(pattern))
    if not matches:
        return None
    return Path(matches[-1])


def _indicator_target_display(pair_id: str, interp: dict[str, Any]) -> tuple[str, str, str]:
    """Resolve indicator / target / pair display names for page titles.

    Strategy: use the hard-coded display maps in `pair_registry.py` where
    available, else fall back to interpretation_metadata fields, else the
    raw pair_id.
    """
    # Mirror the maps in pair_registry.load_pair_registry() to avoid a
    # cyclic import. When a new pair is added, both places need the entry.
    indicator_names = {
        "indpro": "Industrial Production",
        "indpro_xlp": "Industrial Production",
        "permit_spy": "Building Permits",
        "vix_vix3m_spy": "VIX/VIX3M Ratio",
        "sofr_ted_spy": "SOFR - DTB3 (TED)",
        "dff_ted_spy": "DFF - DTB3 (Fed Funds TED)",
        "ted_spliced_spy": "Spliced TED Spread",
        "hy_ig_v2_spy": "HY-IG Credit Spread",
        "umcsent_xlv": "Michigan Consumer Sentiment",
    }
    target_names = {
        "spy": "S&P 500",
        "xlv": "Health Care Select Sector (XLV)",
        "xlp": "Consumer Staples Select Sector (XLP)",
    }
    indicator = indicator_names.get(pair_id) or indicator_names.get(
        interp.get("indicator", ""), interp.get("indicator", pair_id)
    )
    target = target_names.get(
        interp.get("target", ""), interp.get("target", "").upper()
    )
    pair_display = f"{indicator} × {target}"
    return indicator, target, pair_display


def _format_ratio_pct(value: Any, signed: bool = False, ndp: int = 1) -> str:
    """Format a ratio (0.1133) as a percent string (``+11.3%`` or ``11.3%``).

    Returns ``"N/A"`` if value is None or non-numeric. Mirrors META-UC
    (Wave 8B) unit-form conventions."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"
    fmt = f"{{:+.{ndp}%}}" if signed else f"{{:.{ndp}%}}"
    return fmt.format(v)


def _format_scalar(value: Any, ndp: int = 2, default: str = "N/A") -> str:
    try:
        return f"{float(value):.{ndp}f}"
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# STORY PAGE
# ---------------------------------------------------------------------------
def render_story_page(pair_id: str, config: Any | None = None) -> None:
    """Render the canonical Story page for ``pair_id``.

    The ``config`` argument is an optional pair-specific config module with
    attributes ``PLAIN_ENGLISH``, ``ONE_SENTENCE_THESIS``,
    ``NARRATIVE_SECTION_1``, ``NARRATIVE_SECTION_2``, ``HERO_CHART_NAME``,
    ``REGIME_CHART_NAME``, ``HERO_TITLE``, ``REGIME_TITLE``,
    ``HEADLINE_H2``. Missing attributes fall back to canonical defaults.

    Section order (frozen by APP-PT1):
      1. page config + CSS
      2. breadcrumb
      3. sidebar + glossary
      4. Plain English expander
      5. Page title + headline H2
      6. 5-column KPI cards (from winner_summary.json)
      7. Where-This-Fits container (from interpretation_metadata mechanism)
      8. One-sentence thesis
      9. Narrative section 1
     10. Hero chart
     11. Regime / regime_stats chart
     12. Narrative section 2
     13. Transition to Evidence
    """
    # ------ 1. Page config + CSS ------
    if config is None:
        config = _load_default_story_config(pair_id)

    interp = _load_interpretation_metadata(pair_id)
    indicator, target, pair_display = _indicator_target_display(pair_id, interp)

    _apply_page_config(f"{pair_display} Story | AIG-RLIC+", "📖")

    # ------ 3. Sidebar + glossary ------
    render_sidebar()
    render_glossary_sidebar()

    # ------ 2. Breadcrumb ------
    render_breadcrumb("Story", pair_id)

    # ------ 4. Plain English expander ------
    with st.expander("Plain English"):
        st.markdown(
            getattr(
                config,
                "PLAIN_ENGLISH",
                f"This page tells the economic story of how {indicator} "
                f"relates to {target} — in plain language, before the "
                "statistics."
            )
        )

    # ------ Load winner (page depends on it) ------
    winner = _load_winner_summary(pair_id)
    if winner is None:
        return  # APP-SEV1 L1 short-circuit

    # ------ 5. Page title + headline H2 ------
    page_title = getattr(config, "PAGE_TITLE", None)
    if page_title:
        st.title(page_title)
        page_subtitle = getattr(config, "PAGE_SUBTITLE", "")
        if page_subtitle:
            st.markdown(f"*{page_subtitle}*")
        st.markdown("---")

    headline = getattr(config, "HEADLINE_H2", None)
    if headline is None:
        oos_sharpe = winner.get("oos_sharpe", "N/A")
        headline = (
            f"## Sharpe {_format_scalar(oos_sharpe)} out-of-sample — "
            f"{indicator} as a signal for {target}"
        )
    st.markdown(headline)

    # ------ Key metrics bullets (from winner_summary.json) ------
    oos_sharpe = _format_scalar(winner.get("oos_sharpe"))
    bh_sharpe = _format_scalar(winner.get("bh_sharpe"))
    oos_return = _format_ratio_pct(winner.get("oos_ann_return"), signed=True)
    # Some pairs use "max_drawdown", others "oos_max_drawdown". Schema
    # guarantees one of them; prefer the OOS-scoped field.
    max_dd_val = winner.get("oos_max_drawdown", winner.get("max_drawdown"))
    max_dd = _format_ratio_pct(max_dd_val)
    bh_dd = _format_ratio_pct(winner.get("bh_max_drawdown"))

    oos_start = (winner.get("oos_period_start") or "")[:7]
    oos_end = (winner.get("oos_period_end") or "")[:7]
    oos_range_label = f"{oos_start}–{oos_end}" if oos_start and oos_end else "OOS window"

    st.markdown(
        f"**Key metrics (out-of-sample {oos_range_label}):**\n\n"
        f"- **Sharpe ratio: {oos_sharpe}** (vs {bh_sharpe} buy-and-hold {target})\n"
        f"- **Annualized return: {oos_return}** with risk-adjusted exposure\n"
        f"- **Max drawdown: {max_dd}** (vs {bh_dd} buy-and-hold {target})"
    )
    st.markdown("---")

    # ------ 7. Where-This-Fits container ------
    with st.container(border=True):
        st.markdown("### Where This Fits in the Portal")
        where_fits = getattr(config, "WHERE_THIS_FITS", None)
        if where_fits is None:
            mechanism = interp.get("mechanism", "")
            where_fits = (
                f"This is **one indicator-target analysis** — we ask whether "
                f"{indicator} can help time exposure to {target}. "
                + (f"\n\n{mechanism}" if mechanism else "")
            )
        st.markdown(where_fits)
        st.markdown(
            "**How to read the rest of this page pack.** You'll read the "
            "**Story** first (the economic logic), then the **Evidence** "
            "(statistical proofs), then the **Strategy** (the actual trading "
            "rule), then the **Methodology** (technical appendix). Each page "
            "stands alone."
        )

    # ------ 8. One-sentence thesis ------
    thesis = getattr(config, "ONE_SENTENCE_THESIS", None)
    if thesis:
        st.markdown("### One-Sentence Thesis")
        st.markdown(f"*{thesis}*")
        st.markdown("---")

    # ------ 6. KPI cards (5-column row) ------
    signal_code = winner.get("signal_code") or winner.get("signal_column") or "N/A"
    lead_months = winner.get("lead_months", winner.get("lead_days", "N/A"))
    lead_label = f"L{lead_months}" if isinstance(lead_months, (int, float)) else str(lead_months)
    oos_years = _story_kpi_oos_years(winner)

    kpi_row([
        {
            "label": "OOS Sharpe",
            "value": oos_sharpe,
            "delta": f"vs {bh_sharpe} B&H" if bh_sharpe != "N/A" else None,
        },
        {
            "label": "OOS Return",
            "value": oos_return,
            "delta": "annualized",
        },
        {
            "label": "Max Drawdown",
            "value": max_dd,
            "delta": f"vs {bh_dd} B&H" if bh_dd != "N/A" else None,
            "delta_color": "inverse",
        },
        {
            "label": "Signal",
            "value": str(signal_code),
            "delta": lead_label,
        },
        {
            "label": "OOS Period",
            "value": oos_years,
            "delta": oos_range_label,
        },
    ])

    kpi_caption = getattr(config, "KPI_CAPTION", None)
    if kpi_caption:
        st.caption(f"What this shows: {kpi_caption}")
    st.markdown("---")

    # ------ 9. Narrative section 1 ------
    narrative_1 = getattr(config, "NARRATIVE_SECTION_1", None)
    if narrative_1:
        render_narrative(narrative_1)
        st.markdown("---")

    # ------ 10. Hero chart ------
    hero_title = getattr(config, "HERO_TITLE", None)
    if hero_title:
        st.markdown(f"### {hero_title}")
    hero_chart = getattr(config, "HERO_CHART_NAME", "hero")
    load_plotly_chart(
        hero_chart,
        pair_id=pair_id,
        fallback_text=(
            f"Hero chart pending (expected at "
            f"output/charts/{pair_id}/plotly/{hero_chart}.json)."
        ),
        caption=getattr(config, "HERO_CAPTION", None) or (
            f"How to read it: time-series view of {indicator} and {target} "
            "on a shared time axis, with regime bands marked."
        ),
    )
    st.markdown("---")

    # ------ 11. Regime chart ------
    regime_title = getattr(config, "REGIME_TITLE", None)
    if regime_title:
        st.markdown(f"### {regime_title}")
    regime_chart = getattr(config, "REGIME_CHART_NAME", "regime_stats")
    load_plotly_chart(
        regime_chart,
        pair_id=pair_id,
        fallback_text=(
            f"Regime-statistics chart pending (expected at "
            f"output/charts/{pair_id}/plotly/{regime_chart}.json)."
        ),
        caption=getattr(config, "REGIME_CAPTION", None) or (
            f"What this shows: {target} performance stratified by "
            f"{indicator} regime. Reveals where the signal adds risk-adjusted value."
        ),
    )
    st.markdown("---")

    # ------ 11b. Crisis-episode zoom charts (Wave 10G.3) ------
    # Optional: HISTORY_ZOOM_EPISODES is a list of dicts with keys:
    #   slug, title, narrative, caption
    # Each episode loads output/charts/{pair_id}/plotly/history_zoom_{slug}.json
    # via load_plotly_chart. APP-SEV1 L2 severity if chart is missing.
    history_episodes = getattr(config, "HISTORY_ZOOM_EPISODES", None)
    if history_episodes:
        st.markdown("### How the Signal Performed in Past Crises")
        for ep in history_episodes:
            ep_slug = ep.get("slug", "")
            ep_title = ep.get("title", ep_slug)
            ep_narrative = ep.get("narrative", "")
            ep_caption = ep.get("caption", "")
            if ep_title:
                st.markdown(f"#### {ep_title}")
            if ep_narrative:
                st.markdown(ep_narrative)
            load_plotly_chart(
                f"history_zoom_{ep_slug}",
                pair_id=pair_id,
                fallback_text=(
                    f"History zoom chart pending (expected at "
                    f"output/charts/{pair_id}/plotly/history_zoom_{ep_slug}.json)."
                ),
                caption=ep_caption or None,
            )
        st.markdown("---")

    # ------ 12. Narrative section 2 ------
    narrative_2 = getattr(config, "NARRATIVE_SECTION_2", None)
    if narrative_2:
        render_narrative(narrative_2)
        st.markdown("---")

    # ------ Scope note ------
    scope_note = getattr(config, "SCOPE_NOTE", None)
    if scope_note:
        st.markdown(f"**Scope note.** {scope_note}")
        st.markdown("---")

    # ------ 13. Transition ------
    transition_text = getattr(
        config,
        "TRANSITION_TEXT",
        "History suggests a real connection — but anecdotes are not evidence. "
        "We subjected the data to a battery of statistical tests to separate "
        "genuine predictive power from coincidence.",
    )
    render_transition(transition_text)

    # Thin wrapper sets its own filename prefix; build the page_link target
    # from the pair_id + a prefix guess. Page files are named
    # ``{n}_{pair_id}_evidence.py``; the prefix lookup comes from
    # pair_registry's routing map.
    page_prefix = get_page_prefix(pair_id)
    st.page_link(
        f"{page_prefix}_evidence.py",
        label="Continue to The Evidence",
        icon="🔬",
    )

    # ------ Footer ------
    st.markdown("---")
    st.caption(
        f"What this shows: generated with AIG-RLIC+ | Pair: {pair_id}."
    )


def _load_default_story_config(pair_id: str) -> Any:
    """Return a trivial stand-in config if the caller does not pass one.

    This exists so `render_story_page(pair_id)` (signature) is the minimal
    call. The thin-wrapper pages pass no config and rely on the template's
    defaults. The template falls back to plain, no-content sections.
    """
    class _Empty:
        pass
    return _Empty()


def _story_kpi_oos_years(winner: dict[str, Any]) -> str:
    """Compute a years label from winner_summary.oos_n (monthly) or
    oos_period_start/end. Falls back to the raw oos_n when the dates are
    unavailable."""
    start = winner.get("oos_period_start")
    end = winner.get("oos_period_end")
    if start and end:
        try:
            s = pd.to_datetime(start)
            e = pd.to_datetime(end)
            years = (e - s).days / 365.25
            return f"{years:.1f} yrs"
        except (ValueError, TypeError):
            pass
    n = winner.get("oos_n")
    if isinstance(n, (int, float)):
        # Best effort: monthly series → years = n / 12; daily → n / 252.
        return f"{n:.0f} obs"
    return "OOS"


# APP-RL1: _page_prefix() removed. Use get_page_prefix() from pair_registry
# (imported at top of file) — single source of truth per APP-RL1.


# ---------------------------------------------------------------------------
# EVIDENCE PAGE
# ---------------------------------------------------------------------------
# 8-Element Template elements (Rule RES-EP1 via SOP 3.9). Missing any
# mandatory element is a render-time gate failure — block renders an
# `st.error` rather than a partial method write-up.
_EVIDENCE_REQUIRED_ELEMENTS = [
    "method_name",
    "method_theory",
    "question",
    "how_to_read",
    "observation",
    "interpretation",
    "key_message",
]


def _render_method_block(content: dict, pair_id: str) -> None:
    """Render a single 8-element method block. Inlined here (from the prior
    per-page copy-paste) so the template owns the canonical layout.

    Canonical structure (SOP 3.9 / RES-EP1):
      1. (opt.) "Why this matters" opener
      2. Method heading + theory body
      3. Question
      4. How to read
      5. Graph (or fallback warning)
      6. Observation
      7. (opt.) Deep dive
      8. Interpretation
      9. Key message (boxed)
    """
    missing = [k for k in _EVIDENCE_REQUIRED_ELEMENTS if not content.get(k)]
    if missing:
        st.error(
            "Method block incomplete: missing required element(s) "
            f"{missing}. Gate failure per SOP Rule 3.9.\n\n"
            "Plain English: this evidence block is missing required parts "
            "(method, question, how-to-read, observation, interpretation, "
            "or key message) and was not rendered to avoid showing an "
            "incomplete statistical write-up."
        )
        return

    method_name = content["method_name"]
    chart_status = content.get("chart_status", "ready")

    why = content.get("why_this_matters")
    if why:
        st.markdown(f"**Why this matters:** {why}")

    st.markdown(f"### {method_name}")
    st.markdown(content["method_theory"])

    # Optional regime_context callout (Wave 10G.3). When present, renders an
    # info callout between theory and chart for regime-conditional methods
    # (HMM, regime quartiles, etc.). APP-PT1 additive extension — absent in
    # existing pairs, no change to required structure.
    regime_context = content.get("regime_context")
    if regime_context:
        st.info(regime_context)

    st.markdown(f"> *{content['question']}*")
    st.markdown(f"**How to read it:** {content['how_to_read']}")

    chart_name = content.get("chart_name")
    if chart_status == "ready" and chart_name:
        load_plotly_chart(
            chart_name,
            pair_id=pair_id,
            caption=content.get("chart_caption", ""),
            fallback_text=(
                f"{method_name} chart — expected at "
                f"output/charts/{pair_id}/plotly/{chart_name}.json"
            ),
        )
    else:
        # APP-SEV1 L2 — optional chart missing, warn and continue.
        st.warning(
            "Chart pending — method block rendered from narrative only.\n\n"
            "Plain English: the chart for this analysis has not been "
            "generated yet. The interpretation below is based on the "
            "underlying statistics; the chart will appear once the "
            "visualisation pipeline produces it."
        )

    st.markdown(f"**What this shows:** {content['observation']}")

    deep_title = content.get("deep_dive_title")
    deep_content = content.get("deep_dive_content")
    if deep_title and deep_content:
        with st.expander("Deeper dive"):
            st.markdown(f"*{deep_title}*\n\n{deep_content}")

    st.markdown(f"**Why this matters:** {content['interpretation']}")
    st.info(f"**Key message:** {content['key_message']}")


def render_evidence_page(pair_id: str, method_blocks: dict) -> None:
    """Render the canonical Evidence page for ``pair_id``.

    ``method_blocks`` is a dict of the shape::

        {
            "level1": [<block_dict>, ...],
            "level2": [<block_dict>, ...],
            "level1_labels": ["Correlation", "Granger Causality"],
            "level2_labels": ["Regime Analysis"],
        }

    Level-1 / Level-2 tabs are the canonical Evidence structure (see
    `9_hy_ig_v2_spy_evidence.py`). Each inner tab renders one
    `_render_method_block(...)`. Label lists must have the same length as
    their block lists.

    Structure (frozen by APP-PT1):
      1. page config + CSS
      2. breadcrumb
      3. sidebar + glossary
      4. Plain English expander
      5. Title + overview
      6. Outer tabs: Level 1 / Level 2
      7. Inner tabs per level, one method block each
      8. Tournament pointer
      9. Transition to Strategy
    """
    interp = _load_interpretation_metadata(pair_id)
    _, target, pair_display = _indicator_target_display(pair_id, interp)

    _apply_page_config(f"{pair_display} Evidence | AIG-RLIC+", "🔬")
    render_sidebar()
    render_glossary_sidebar()
    render_breadcrumb("Evidence", pair_id)

    plain_english = method_blocks.get(
        "plain_english",
        "This section shows the statistical evidence for the relationship "
        "between the indicator and the target. Multiple methods converge on "
        "the same direction, raising our confidence the signal is genuine "
        "rather than a coincidence of one test."
    )
    with st.expander("Plain English"):
        st.markdown(plain_english)

    st.title(method_blocks.get("title", "The Evidence: What the Data Shows"))
    overview = method_blocks.get(
        "overview",
        "*We subjected the data to multiple complementary statistical methods. "
        "Each test is designed to stress a different weakness of the "
        "hypothesis. If one test flatters the result and the others reject "
        "it, the story is fragile. If they converge, we have real evidence.*"
    )
    st.markdown(overview)
    st.markdown("---")

    st.markdown(
        "Each method follows the same 8-part structure: what the method is, "
        "the question it answers, how to read the chart, what we observe, "
        "deeper technical detail, economic interpretation, and the key "
        "message. Read in order for the full picture, or skip to the "
        "**Key message** lines for a quick summary."
    )
    st.markdown("---")

    st.markdown(
        "Evidence is organized in two tiers. **Level 1** covers basic "
        "statistical relationships. **Level 2** adds regime analysis, tail "
        "risk, nonlinear dependence, or other advanced techniques."
    )
    st.markdown("")

    level1_blocks = method_blocks.get("level1", [])
    level2_blocks = method_blocks.get("level2", [])
    level1_labels = method_blocks.get(
        "level1_labels",
        [b.get("method_name", f"Method {i + 1}") for i, b in enumerate(level1_blocks)],
    )
    level2_labels = method_blocks.get(
        "level2_labels",
        [b.get("method_name", f"Method {i + 1}") for i, b in enumerate(level2_blocks)],
    )

    tier1, tier2 = st.tabs(
        ["Level 1 — Basic Analysis", "Level 2 — Advanced Analysis"]
    )

    with tier1:
        if not level1_blocks:
            st.info("No Level 1 method blocks configured for this pair.")
        else:
            sub_tabs = st.tabs(level1_labels)
            for sub, block in zip(sub_tabs, level1_blocks):
                with sub:
                    _render_method_block(block, pair_id)

    with tier2:
        if not level2_blocks:
            st.info("No Level 2 method blocks configured for this pair.")
        else:
            sub_tabs = st.tabs(level2_labels)
            for sub, block in zip(sub_tabs, level2_blocks):
                with sub:
                    _render_method_block(block, pair_id)

    # ------ Tournament pointer ------
    st.markdown("---")
    st.markdown("### The Combinatorial Tournament")
    tourn_path = _latest_dated_file(pair_id, "tournament_results")
    tourn_sub = method_blocks.get(
        "tournament_intro",
        f"We tested a grid of signal × threshold × strategy × lead-time "
        f"combinations on out-of-sample data. The full leaderboard is "
        f"available on the Strategy page.",
    )
    st.markdown(tourn_sub)
    if tourn_path:
        st.caption(
            f"What this shows: tournament results at "
            f"`results/{pair_id}/{tourn_path.name}`."
        )

    # ------ Transition ------
    st.markdown("---")
    transition = method_blocks.get(
        "transition",
        "**Transition:** Multiple statistical tests agree — the signal "
        "carries genuine predictive information. The practical question is "
        "whether an investor can use it to improve risk-adjusted returns, "
        "and at what cost.",
    )
    st.markdown(transition)

    page_prefix = get_page_prefix(pair_id)
    st.page_link(
        f"{page_prefix}_strategy.py",
        label="Continue to The Strategy",
        icon="🎯",
    )

    st.markdown("---")
    st.caption(
        f"What this shows: generated with AIG-RLIC+ | Pair: {pair_id}."
    )


# ---------------------------------------------------------------------------
# STRATEGY PAGE
# ---------------------------------------------------------------------------
def render_strategy_page(pair_id: str, config: Any | None = None) -> None:
    """Render the canonical Strategy page for ``pair_id``.

    Optional ``config`` carries pair-specific narrative text (plain English
    expander, signal-generation description, caveats). Missing attributes
    fall back to canonical defaults.

    Structure (frozen by APP-PT1):
      1. page config + CSS
      2. breadcrumb
      3. sidebar + glossary
      4. render_direction_check (APP-DIR1)
      5. Plain English expander
      6. Page title
      7. Tournament Winner spotlight card (from winner_summary.json)
      8. 5-column KPI row
      9. Execute / Performance / Confidence tabs
     10. Transition to Methodology
    """
    if config is None:
        class _Empty:
            pass
        config = _Empty()

    interp = _load_interpretation_metadata(pair_id)
    _, target, pair_display = _indicator_target_display(pair_id, interp)

    _apply_page_config(f"{pair_display} Strategy | AIG-RLIC+", "🎯")
    render_sidebar()
    render_glossary_sidebar()
    render_breadcrumb("Strategy", pair_id)

    # ------ 4. APP-DIR1 direction triangulation ------
    render_direction_check(pair_id)

    # ------ 5. Plain English expander ------
    with st.expander("Plain English"):
        st.markdown(
            getattr(
                config,
                "PLAIN_ENGLISH",
                "Our computer looked at every combination of 'signal + "
                "threshold + trade rule' to find the one that would have "
                "made the most money (adjusted for risk) in past data. This "
                "section explains what the winning strategy does, when to "
                "use it, and when it would have failed."
            )
        )

    winner = _load_winner_summary(pair_id)
    if winner is None:
        return

    # ------ 6. Page title ------
    st.title(
        getattr(
            config,
            "PAGE_TITLE",
            f"The Strategy: Translating {pair_display} into Trading Rules",
        )
    )
    st.markdown(
        f"*{getattr(config, 'PAGE_SUBTITLE', 'We tested many combinations to find the most robust timing rule.')}*"
    )
    st.markdown("---")

    # ------ 7. Tournament Winner spotlight ------
    _strategy_family = winner.get("strategy_family", "N/A")
    _direction = winner.get("direction", "N/A")
    _lead = winner.get("lead_months", winner.get("lead_days", "N/A"))
    st.markdown(
        f"### Tournament Winner: {winner.get('signal_code', 'N/A')} / "
        f"{_strategy_family} / L{_lead}"
    )

    signal_rule = getattr(config, "SIGNAL_RULE_MD", None) or (
        f"**Rule in plain English:** monitor {winner.get('signal_column', 'the indicator signal')}. "
        f"When the signal crosses {winner.get('threshold_value', 'its threshold')} "
        f"({winner.get('threshold_rule', 'the comparison rule')}), apply the "
        f"{_strategy_family} rule in the {_direction} direction. Lead time: L{_lead}."
    )
    with st.container(border=True):
        st.markdown(signal_rule)

    how_signal = getattr(config, "HOW_SIGNAL_IS_GENERATED_MD", None)
    if how_signal:
        st.markdown("### How the Signal is Generated")
        st.markdown(how_signal)
        st.markdown("---")

    # ------ 8. KPI row ------
    oos_sharpe = _format_scalar(winner.get("oos_sharpe"))
    bh_sharpe = _format_scalar(winner.get("bh_sharpe"))
    oos_return = _format_ratio_pct(winner.get("oos_ann_return"), signed=True)
    max_dd_val = winner.get("oos_max_drawdown", winner.get("max_drawdown"))
    max_dd = _format_ratio_pct(max_dd_val)
    bh_dd = _format_ratio_pct(winner.get("bh_max_drawdown"))
    turnover = winner.get("oos_annual_turnover", winner.get("annual_turnover"))

    kpi_row([
        {"label": "OOS Sharpe", "value": oos_sharpe,
         "delta": f"vs {bh_sharpe} B&H" if bh_sharpe != "N/A" else None},
        {"label": "OOS Return", "value": oos_return, "delta": "annualized"},
        {"label": "Max Drawdown", "value": max_dd,
         "delta": f"vs {bh_dd} B&H" if bh_dd != "N/A" else None,
         "delta_color": "inverse"},
        {"label": "Turnover", "value": f"~{float(turnover):.1f}/yr" if turnover else "N/A"},
        {"label": "Win Rate",
         "value": f"{float(winner.get('oos_win_rate', 0)):.0%}"
                   if winner.get('oos_win_rate') is not None else "N/A"},
    ])
    st.markdown("---")

    # ------ 9. Execute / Performance / Confidence tabs ------
    tab_execute, tab_performance, tab_confidence = st.tabs(
        ["Execute", "Performance", "Confidence"]
    )

    # --- Execute tab ---
    with tab_execute:
        st.markdown("### Strategy Summary")
        _col1, _col2 = st.columns(2)
        with _col1:
            st.markdown(f"**Signal code:** `{winner.get('signal_code', 'N/A')}`")
            st.markdown(f"**Signal column:** `{winner.get('signal_column', 'N/A')}`")
            st.markdown(f"**Threshold:** `{winner.get('threshold_rule', '')} {winner.get('threshold_value', '')}`")
        with _col2:
            st.markdown(f"**Strategy family:** `{_strategy_family}`")
            st.markdown(f"**Direction:** `{_direction}`")
            st.markdown(f"**Lead time:** L{_lead}")

        st.markdown("---")
        # APP-SE1 — Probability Engine Panel
        render_probability_engine_panel(pair_id)
        st.markdown("---")
        # APP-SE2 — Position Adjustment Panel
        render_position_adjustment_panel(pair_id)
        st.markdown("---")
        # APP-SE3 — Instructional Trigger Cards
        render_instructional_trigger_cards(pair_id)

        manual_use = getattr(config, "MANUAL_USE_MD", None)
        if manual_use:
            st.markdown("---")
            st.markdown("### How to Use This Indicator Manually")
            st.markdown(manual_use)

    # --- Performance tab ---
    with tab_performance:
        st.markdown("### Equity Curves vs. Buy-and-Hold")
        equity_chart = getattr(config, "EQUITY_CHART_NAME", "equity_curves")
        load_plotly_chart(
            equity_chart,
            pair_id=pair_id,
            fallback_text=(
                f"Equity curves pending — expected at "
                f"output/charts/{pair_id}/plotly/{equity_chart}.json"
            ),
            caption=(
                "What this shows: cumulative returns for the tournament "
                f"winner compared to buy-and-hold {target}."
            ),
        )
        st.markdown("---")
        st.markdown("### Drawdown Comparison")
        drawdown_chart = getattr(config, "DRAWDOWN_CHART_NAME", "drawdown")
        load_plotly_chart(
            drawdown_chart,
            pair_id=pair_id,
            fallback_text=(
                f"Drawdown chart pending — expected at "
                f"output/charts/{pair_id}/plotly/{drawdown_chart}.json"
            ),
            caption=(
                f"What this shows: peak-to-trough drawdown profile. "
                f"The strategy limits drawdown to {max_dd} vs {bh_dd} buy-and-hold."
            ),
        )
        st.markdown("---")
        st.markdown("### Trading History")
        _trade_path = _REPO_ROOT / "results" / pair_id / "winner_trade_log.csv"
        if _trade_path.exists():
            trade_df = pd.read_csv(_trade_path)
            csv_bytes = trade_df.to_csv(index=False)
            st.download_button(
                label="Download trading history (CSV)",
                data=csv_bytes,
                file_name=f"{pair_id}_winner_trade_log.csv",
                mime="text/csv",
            )
            with st.expander("Preview (first 20 rows)"):
                st.dataframe(trade_df.head(20), use_container_width=True, hide_index=True)
        else:
            st.warning(
                f"Trade log missing for `{pair_id}` — expected at "
                f"`results/{pair_id}/winner_trade_log.csv`. Re-run the "
                "pair pipeline to produce it."
            )

    # --- Confidence tab ---
    with tab_confidence:
        st.markdown("### Walk-Forward Rolling Sharpe")
        wf_chart = getattr(config, "WALK_FORWARD_CHART_NAME", "walk_forward")
        load_plotly_chart(
            wf_chart,
            pair_id=pair_id,
            fallback_text=(
                f"Walk-forward chart pending — expected at "
                f"output/charts/{pair_id}/plotly/{wf_chart}.json"
            ),
            caption=(
                "What this shows: rolling risk-adjusted performance. "
                "Periods where the winner strategy exceeds the benchmark "
                "confirm persistent edge."
            ),
        )
        st.markdown("---")
        st.markdown("### Tournament Scatter")
        scatter_chart = getattr(
            config, "TOURNAMENT_SCATTER_CHART_NAME", "tournament_scatter"
        )
        load_plotly_chart(
            scatter_chart,
            pair_id=pair_id,
            fallback_text=(
                f"Tournament scatter pending — expected at "
                f"output/charts/{pair_id}/plotly/{scatter_chart}.json"
            ),
            caption=(
                "What this shows: each point is one strategy combination. "
                "Stars mark the top 5; diamond is buy-and-hold."
            ),
        )
        st.markdown("---")
        st.markdown("### Tournament Leaderboard")
        if tourn_exists := _latest_dated_file(pair_id, "tournament_results"):
            _render_tournament_leaderboard(tourn_exists, target)
        else:
            st.warning(
                f"Tournament results missing for `{pair_id}` — re-run the "
                "pair pipeline to populate the leaderboard."
            )

        caveats = getattr(config, "CAVEATS_MD", None)
        if caveats:
            st.markdown("---")
            st.warning(caveats)

    # ------ 10. Transition ------
    st.markdown("---")
    try:
        render_live_execution_placeholder(pair_id)
    except Exception:
        # Live execution is a tolerant placeholder; do not block the page
        # if its dependencies fail to load.
        pass

    st.markdown("---")
    st.markdown(
        "For readers who want to understand exactly how we reached these "
        "conclusions — or who want to replicate and extend the analysis — "
        "the methodology section provides full details on data, methods, "
        "and diagnostics."
    )
    page_prefix = get_page_prefix(pair_id)
    st.page_link(
        f"{page_prefix}_methodology.py",
        label="Continue to Methodology",
        icon="📐",
    )

    st.markdown("---")
    st.caption(
        f"What this shows: generated with AIG-RLIC+ | Pair: {pair_id}."
    )


def _render_tournament_leaderboard(tourn_path: Path, target: str) -> None:
    """Render the tournament leaderboard + benchmark footnote from a CSV file.

    Units handling: drawdown / return columns may be stored as percent
    (e.g. -13.29) OR as ratio (e.g. -0.1329) depending on pair (META-UC
    migration is still partial — tracked BL-002). The heuristic: if absolute
    value > 1.5, assume percent form; otherwise ratio form and scale for
    display. This keeps leaderboard cells human-readable for every pair
    without reading producer-side schema_version flags.
    """
    try:
        tdf = pd.read_csv(tourn_path)
    except Exception as exc:
        st.warning(f"Failed to read tournament CSV: {exc}")
        return

    valid = tdf[(tdf.get("valid", False) == True) & (tdf.get("signal") != "BENCHMARK")]
    bh = tdf[tdf.get("signal") == "BENCHMARK"]

    if len(valid) == 0:
        st.info("No valid tournament strategies to display.")
        return

    top = valid.nlargest(10, "oos_sharpe").copy()

    # Normalise drawdown / return units for display.
    def _to_pct(v: Any) -> str:
        try:
            x = float(v)
        except (TypeError, ValueError):
            return "—"
        if abs(x) > 1.5:
            return f"{x:.1f}%"
        return f"{x * 100:.1f}%"

    display_rows = []
    for rank, (_, r) in enumerate(top.iterrows(), 1):
        display_rows.append({
            "Rank": rank,
            "Signal": r.get("signal", "—"),
            "Threshold": r.get("threshold", "—"),
            "Strategy": r.get("strategy", "—"),
            "Lead": f"{int(r['lead_months'])}M" if "lead_months" in r.index and pd.notna(r["lead_months"]) else "—",
            "OOS Sharpe": round(float(r["oos_sharpe"]), 2),
            "OOS Return": _to_pct(r.get("oos_ann_return")),
            "Max DD": _to_pct(r.get("max_drawdown")),
            "Turnover": f"{float(r['annual_turnover']):.1f}/yr" if "annual_turnover" in r.index and pd.notna(r["annual_turnover"]) else "—",
            "Win Rate": f"{float(r['win_rate']):.1%}" if "win_rate" in r.index and pd.notna(r["win_rate"]) else "—",
        })

    if len(bh) > 0:
        b = bh.iloc[0]
        display_rows.append({
            "Rank": "—",
            "Signal": f"Buy-and-Hold {target or ''}".strip(),
            "Threshold": "—",
            "Strategy": "Benchmark",
            "Lead": "—",
            "OOS Sharpe": round(float(b["oos_sharpe"]), 2),
            "OOS Return": _to_pct(b.get("oos_ann_return")),
            "Max DD": _to_pct(b.get("max_drawdown")),
            "Turnover": "0/yr",
            "Win Rate": f"{float(b['win_rate']):.1%}" if "win_rate" in b.index and pd.notna(b["win_rate"]) else "—",
        })

    st.dataframe(
        pd.DataFrame(display_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "OOS Sharpe": st.column_config.NumberColumn("OOS Sharpe", format="%.2f"),
        },
    )
    st.caption(
        f"**{len(tdf):,} combinations tested** | "
        f"**{len(valid):,} valid** (OOS Sharpe > 0)."
    )


# ---------------------------------------------------------------------------
# METHODOLOGY PAGE
# ---------------------------------------------------------------------------
def render_methodology_page(pair_id: str, config: MethodologyConfig) -> None:
    """Render the canonical Methodology page for ``pair_id``.

    Structure (frozen by APP-PT1):
      1. page config + CSS
      2. breadcrumb
      3. sidebar + glossary
      4. Plain English expander
      5. Title + overview
      6. Sample period metrics (from winner_summary.json)
      7. Data Sources table (from config)
      8. Indicator Construction (from config)
      9. Signal Universe (render_signal_universe — reads signal_scope.json)
     10. Stationarity Tests (latest `stationarity_tests_*.csv`)
     11. Econometric Methods table (from config)
     12. Tournament Design table (from config)
     13. Analyst Suggestions (render_analyst_suggestions)
     14. References (from config)
    """
    interp = _load_interpretation_metadata(pair_id)
    _, _, pair_display = _indicator_target_display(pair_id, interp)

    _apply_page_config(f"{pair_display} Methodology | AIG-RLIC+", "📐")
    render_sidebar()
    render_glossary_sidebar()
    render_breadcrumb("Methodology", pair_id)

    with st.expander("Plain English"):
        st.markdown(
            config.plain_english or (
                "This section explains the technical details of how we did "
                "the analysis — which data we used, which statistical "
                "methods, and what could go wrong. Normal readers can skip "
                "it. Expert readers can use it to criticise our work and "
                "suggest improvements."
            )
        )

    st.title("Methodology: Technical Appendix")
    st.markdown(
        "*For the skeptical reader: this section provides the full "
        "methodological detail needed to replicate, challenge, or extend our "
        "analysis. Every claim in the preceding pages traces back to a "
        "specific method, dataset, and diagnostic described here.*"
    )
    st.markdown("---")

    # ------ 6. Sample period ------
    winner = _load_winner_summary(pair_id)
    if winner is not None:
        start = (winner.get("oos_period_start") or "")[:7]
        end = (winner.get("oos_period_end") or "")[:7]
        oos_n = winner.get("oos_n", "N/A")
        st.markdown("### Sample Period")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Out-of-Sample Window",
                f"{start} to {end}" if start and end else "N/A",
                delta=f"{oos_n} obs" if oos_n != "N/A" else None,
            )
        with col2:
            st.metric("Total tournament combinations", f"{winner.get('total_combos', 'N/A'):,}"
                      if isinstance(winner.get("total_combos"), int) else "N/A")
        if config.sample_period_note:
            st.caption(f"What this shows: {config.sample_period_note}")
        st.markdown("---")

    # ------ 7. Data sources ------
    st.markdown("### Data Sources")
    st.markdown(config.data_sources_table_md)
    st.markdown("---")

    # ------ 8. Indicator construction ------
    st.markdown("### Indicator Construction")
    st.markdown(config.indicator_construction_md)
    st.markdown("---")

    # ------ 9. Signal Universe (ECON-UD / APP-SS1) ------
    st.markdown("### Signal Universe")
    st.markdown(
        "This section lists every derivative of the indicator and target "
        "considered during the analysis. It is the single source of truth "
        "for what is in scope for this pair. Anything not in these two "
        "tables was deliberately excluded — and is instead logged under "
        "Analyst Suggestions below."
    )
    render_signal_universe(pair_id)
    st.markdown("---")

    # ------ 10. Stationarity tests ------
    st.markdown("### Stationarity Tests")
    stat_path = _latest_dated_file(pair_id, "stationarity_tests")
    if stat_path and stat_path.exists():
        try:
            stat_df = pd.read_csv(stat_path)
            st.dataframe(stat_df, use_container_width=True, hide_index=True)
            st.caption(
                "How to read it: ADF — reject null = stationary. "
                "KPSS — fail to reject null = stationary."
            )
        except Exception as exc:
            st.warning(f"Failed to read stationarity CSV: {exc}")
    else:
        st.warning(
            f"Stationarity tests missing for `{pair_id}` — expected at "
            f"`results/{pair_id}/stationarity_tests_*.csv`."
        )
    st.markdown("---")

    # ------ 11. Econometric methods ------
    st.markdown("### Econometric Methods")
    st.markdown(config.methods_table_md)
    st.markdown("---")

    # ------ 12. Tournament design ------
    st.markdown("### Tournament Design")
    st.markdown(config.tournament_design_md)
    st.markdown("---")

    # ------ 13. Analyst suggestions ------
    st.markdown("### Analyst Suggestions for Future Work")
    st.markdown(
        "Signals flagged during analysis that look worth pursuing in future "
        "work (a different pair, a variant family extension, or a regime "
        "overlay). These are informational only — they did not influence "
        "this pair's winning strategy."
    )
    render_analyst_suggestions(pair_id)
    st.markdown("---")

    # ------ 14. References ------
    st.markdown("### References")
    st.markdown(config.references_md)

    st.markdown("---")
    st.caption(f"What this shows: generated with AIG-RLIC+ | Pair: {pair_id}.")
