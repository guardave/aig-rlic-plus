"""Shared chart-layout primitives (single source of truth for fix260531).

Several chart generators were emitting the same two text elements below the
plot area — an X-axis title (``"Date"``, ``"Sharpe Ratio"``, etc.) and a small
grey source-note caption — at inconsistent vertical positions. Each generator
had its own hand-tuned ``y`` values, so the same layout class drifted across
chart families and pairs.

This module centralises the constants and exposes a single helper that
generators should call AFTER they have finished adding traces, annotations
and the x-axis title:

    from scripts._chart_layout import apply_caption_layout

    fig.update_layout(
        xaxis_title="Date",
        ...
    )
    apply_caption_layout(fig, "Pearson correlation between signal and ...")

The helper:

* sets ``xaxis.title.standoff`` so the title hugs the tick labels
* adds the caption as a paper-anchored grey annotation at ``CAPTION_Y``
* widens ``margin.b`` to ``MARGIN_B_WITH_CAPTION`` if it's smaller

The companion patcher ``scripts/patch_xaxis_caption_layout.py`` imports the
same constants from here, so the producer (generator) and the post-hoc
patcher are guaranteed to agree.

Why a separate module rather than inline constants in
``viz_cp_retro_apply.py``: several other generators (``generate_charts_*``)
also draw captioned charts. Putting the constants in any one generator
forces the others to either duplicate them (drift waiting to happen) or to
import from an unexpected place. A neutral ``_chart_layout`` module is the
obvious shared dependency.
"""

from __future__ import annotations

from typing import Iterable

# ─── Constants (canonical) ────────────────────────────────────────────────
#
# The caption is LEFT-ALIGNED to the chart container's left edge at a
# fixed pixel distance below the plot area. To land on the container
# edge (not the plot-area edge), the helper sets xshift = -margin.l
# per chart — Plotly's paper-x=0 is plot-area left, which sits
# margin.l pixels in from the chart container's left.
#
# Note on cross-chart alignment: charts with different widths (e.g.
# subperiod_sharpe w=700 vs rolling w=900) and centered in a Streamlit
# column will show captions starting at different page-x positions
# because the containers themselves don't align at the page level.
# Captions ARE flush-left within each chart container — that's the
# per-chart guarantee. Cross-chart visual alignment would require
# standardising chart widths (out of scope here).
#
# CAPTION_Y_SHIFT_PX leaves room for tick labels + axis title + gap.

CAPTION_Y_SHIFT_PX: int = -65    # 65 px below plot bottom

# Pull the X-axis title up against the tick labels so it doesn't drift
# down into the caption zone.
XAXIS_STANDOFF: int = 12

# Bottom margin large enough for: tick labels + axis title + caption + gap.
MARGIN_B_WITH_CAPTION: int = 120

# Caption font.
CAPTION_FONT: dict = {"size": 10, "color": "grey"}


# ─── Helpers ──────────────────────────────────────────────────────────────


def apply_caption_layout(fig, caption_text: str) -> None:
    """Apply the canonical X-axis title + caption layout to ``fig``.

    The caption is left-aligned to the chart container's left edge at a
    fixed pixel distance below the plot bottom.

    Recipe:
      x=0, xanchor="left"           → anchor at plot-area left edge
      xshift = -margin.l            → shift left to chart-container edge
      y=0, yshift=CAPTION_Y_SHIFT_PX, yanchor="top"
                                    → fixed pixel below plot bottom

    Idempotent: re-applying produces the same layout.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The figure to patch in place.
    caption_text : str
        The text to render as the grey source-note caption. HTML (<b>…</b>,
        <i>…</i>) is supported by Plotly.
    """
    fig.update_xaxes(title_standoff=XAXIS_STANDOFF)

    # Resolve margin.l so the caption lands at chart-container left edge,
    # not plot-area left edge. Default to 80 if margin.l is unset.
    margin = (fig.layout.margin or {}) if hasattr(fig.layout, "margin") else {}
    try:
        margin_l = int(margin.l) if margin.l is not None else 80
    except Exception:
        margin_l = 80

    fig.add_annotation(
        text=caption_text,
        xref="paper",
        yref="paper",
        x=0,
        y=0,
        xshift=-margin_l,
        yshift=CAPTION_Y_SHIFT_PX,
        xanchor="left",
        yanchor="top",
        showarrow=False,
        font=CAPTION_FONT,
        align="left",
    )

    # Bottom-margin floor.
    try:
        cur_b = int(margin.b) if margin.b is not None else 0
    except Exception:
        cur_b = 0
    if cur_b < MARGIN_B_WITH_CAPTION:
        fig.update_layout(margin=dict(b=MARGIN_B_WITH_CAPTION))


__all__: Iterable[str] = (
    "CAPTION_Y",
    "XAXIS_STANDOFF",
    "MARGIN_B_WITH_CAPTION",
    "CAPTION_FONT",
    "apply_caption_layout",
)
