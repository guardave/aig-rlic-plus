"""Plotly JSON chart loader and helper functions."""

import json
import logging
import os
import uuid

import plotly.io as pio
import streamlit as st


_APP_DIR = os.path.dirname(os.path.dirname(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_APP_DIR, ".."))
CHART_DIR = os.path.join(_APP_DIR, "..", "output", "charts", "plotly")
METADATA_DIR = os.path.join(_APP_DIR, "..", "output", "charts", "metadata")

_LOGGER = logging.getLogger("app.components.charts")


@st.cache_resource
def _load_plotly_json(json_path: str):
    """Load and parse a Plotly JSON file (cached).

    Raises the underlying exception on failure rather than silently returning
    None; the outer loader is responsible for catching and logging. This lets
    the smoke test observe real parse errors instead of seeing a placeholder.
    """
    with open(json_path) as f:
        return pio.from_json(f.read())


def _resolve_history_zoom_paths(chart_name: str, pair_id: str | None) -> list[str]:
    """Resolve candidate paths for historical-episode zoom charts.

    Implements the META-ZI (Historical Episode Chart Strategy) loader contract
    as refined in Wave 6B per META-AL (Abstraction Layer Discipline):

      1. Per-pair rendered chart at
         ``output/charts/{pair_id}/plotly/history_zoom_{episode}.json`` only.
      2. If missing → caller renders the GATE-25 "chart pending" placeholder.

    There is NO canonical-rendered-chart fallback. The canonical layer is
    metadata only (``docs/schemas/history_zoom_events_registry.json`` — VIZ-V12
    — plus VIZ-V11 palette and VIZ-V2 NBER shading rules); each pair renders
    its own dual-panel chart (indicator + target) from the canonical events +
    pair-specific data. Making rendered pixels canonical was a META-AL
    category error because the chart depends on pair-specific inputs.

    Cross-reference: META-AL (supersedes override-fallback model), META-ZI
    (refined Wave 6B), VIZ-V1 (dual-panel mandate), VIZ-V12 (events registry),
    GATE-25 (placeholder at render time), GATE-28 (reference pairs must have
    zero placeholders so the missing-chart path is a drill, not a shipped
    state).
    """
    if not pair_id:
        return []
    return [
        os.path.normpath(
            os.path.join(
                _REPO_ROOT, "output", "charts", pair_id, "plotly", f"{chart_name}.json"
            )
        )
    ]


def load_plotly_chart(
    chart_name: str,
    fallback_text: str = "Chart will appear when visualization is complete.",
    caption: str = None,
    pair_id: str = None,
    chart_key: str = None,
):
    """Load a Plotly chart from JSON file and render it.

    Args:
        chart_name: Filename without extension (e.g., 'hero_spread_vs_spy').
        fallback_text: Message shown if chart JSON not found.
        caption: Optional caption displayed below the chart.
        pair_id: Optional pair subdirectory (e.g., 'indpro_spy').
                 If provided, looks in output/charts/{pair_id}/plotly/.
        chart_key: Unique Streamlit widget key. Auto-generated if None.

    Special routing — META-ZI (Historical Episode Chart Strategy, refined
    Wave 6B per META-AL):
        Chart names starting with ``history_zoom_`` resolve only to the
        per-pair rendered chart at
        ``output/charts/{pair_id}/plotly/history_zoom_{episode}.json``. There
        is no canonical-rendered-chart fallback; the canonical layer is the
        events registry (VIZ-V12), not pixels. See
        ``_resolve_history_zoom_paths``.
    """
    if chart_key is None:
        chart_key = f"plotly_{chart_name}_{uuid.uuid4().hex[:8]}"

    # META-ZI routing (Wave 6B): historical-episode zoom charts are strictly
    # per-pair. Bypass the regular per-pair chart_dir so we don't accidentally
    # fall back to a pair_id-prefix variant like the method charts do.
    if chart_name.startswith("history_zoom_"):
        candidates = _resolve_history_zoom_paths(chart_name, pair_id)
    else:
        if pair_id:
            chart_dir = os.path.join(_APP_DIR, "..", "output", "charts", pair_id, "plotly")
        else:
            chart_dir = CHART_DIR

        # VIZ-NM1 + APP-EP4: bare-name is canonical. Pair-prefix fallback removed
        # (Wave 10F item 6 — all active pairs migrated to bare-name by Vera,
        # commits 3c6bb50 + 27fb01f). A single candidate; genuinely-missing charts
        # fall through to the GATE-25 "chart pending" placeholder below.
        candidates = [
            os.path.normpath(os.path.join(chart_dir, f"{chart_name}.json")),
        ]

    json_path = None
    for candidate in candidates:
        if os.path.exists(candidate):
            json_path = candidate
            break

    fig = None
    if json_path:
        # Load + parse; no silent swallowing. If parsing fails we log a visible
        # warning (surfaced in both Streamlit and stderr) and fall through to
        # the GATE-25 placeholder so the user never sees a blank region.
        try:
            fig = _load_plotly_json(json_path)
        except Exception as exc:  # noqa: BLE001 — intentional broad catch at render edge
            _LOGGER.warning(
                "load_plotly_chart: failed to parse %s (chart=%s pair_id=%s): %s",
                json_path,
                chart_name,
                pair_id,
                exc,
            )
            st.warning(
                f"Chart '{chart_name}' failed to load: "
                f"{exc.__class__.__name__}. See application logs.\n\n"
                "Plain English: the JSON file for this chart was found "
                "on disk but could not be parsed by Plotly — usually "
                "because it was produced by a newer or older Plotly "
                "version than the one this portal runs. Regenerate the "
                "chart via the visualisation pipeline to fix it."
            )
            fig = None

    if fig is not None:
        st.plotly_chart(fig, use_container_width=True, key=chart_key)
    elif not json_path:
        # GATE-25: render an explicit "chart pending" placeholder rather than
        # silently substituting unrelated content.
        st.info(f"📊 {fallback_text}")

    if caption:
        st.markdown(f'<p class="chart-caption">{caption}</p>', unsafe_allow_html=True)

    # Return the Figure (or None on miss/failure) so smoke tests — and any
    # future callers — can assert successful load. Does not change rendering
    # behaviour; st.plotly_chart has already been invoked above.
    return fig


def load_chart_metadata(chart_name: str) -> dict:
    """Load chart metadata sidecar JSON.

    Returns:
        dict with keys like 'title', 'caption', 'source', 'insight'.
        Empty dict if metadata file doesn't exist.
    """
    meta_path = os.path.normpath(os.path.join(METADATA_DIR, f"{chart_name}_meta.json"))
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            return json.load(f)
    return {}


def chart_with_metadata(chart_name: str, default_caption: str = ""):
    """Load a chart and its metadata, rendering caption from metadata if available."""
    meta = load_chart_metadata(chart_name)
    caption = meta.get("caption", default_caption)
    load_plotly_chart(chart_name, caption=caption)
