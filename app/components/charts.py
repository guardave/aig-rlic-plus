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
_COMPARISON_DIR = os.path.join(_REPO_ROOT, "output", "_comparison")

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
    """Resolve candidate paths for canonical historical-episode zoom charts.

    Implements the META-ZI (Historical Episode Chart Strategy) loader contract:
      1. Per-pair override at ``output/charts/{pair_id}/history_zoom_{episode}.json``
         (if a pair-specific variant is warranted by Ray's coherence review)
      2. Canonical baseline at ``output/_comparison/history_zoom_{episode}.json``
      3. Fallback to GATE-25 "chart pending" placeholder (handled by caller)

    Cross-reference: APP-SE1 loader-contract note (Gap 5 / META-ZI) and Viz SOP
    VIZ-V1 cross-agent contract. Ray flags override candidates in the narrative
    coherence check; this loader is the Ace-side wiring that consumes them.
    """
    candidates: list[str] = []
    if pair_id:
        # Pair-specific override tier (no /plotly/ subdir for these episodes)
        candidates.append(
            os.path.normpath(
                os.path.join(_REPO_ROOT, "output", "charts", pair_id, f"{chart_name}.json")
            )
        )
    candidates.append(
        os.path.normpath(os.path.join(_COMPARISON_DIR, f"{chart_name}.json"))
    )
    return candidates


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

    Special routing — META-ZI (Historical Episode Chart Strategy):
        Chart names starting with ``history_zoom_`` are resolved via the
        canonical + override fallback chain (per-pair override first,
        then ``output/_comparison/``). See ``_resolve_history_zoom_paths``.
    """
    if chart_key is None:
        chart_key = f"plotly_{chart_name}_{uuid.uuid4().hex[:8]}"

    # META-ZI routing: historical-episode zoom charts use the canonical+override
    # fallback chain (GATE-25 + VIZ-V1). Bypass the regular per-pair chart_dir.
    if chart_name.startswith("history_zoom_"):
        candidates = _resolve_history_zoom_paths(chart_name, pair_id)
    else:
        if pair_id:
            chart_dir = os.path.join(_APP_DIR, "..", "output", "charts", pair_id, "plotly")
        else:
            chart_dir = CHART_DIR

        # Try exact name first, then with pair_id prefix (agents may use either)
        candidates = [
            os.path.normpath(os.path.join(chart_dir, f"{chart_name}.json")),
        ]
        if pair_id:
            candidates.append(
                os.path.normpath(os.path.join(chart_dir, f"{pair_id}_{chart_name}.json"))
            )

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
