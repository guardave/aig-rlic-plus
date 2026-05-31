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
# The caption is positioned by PIXEL OFFSET (xshift/yshift) from the
# bottom-left corner of the plot area. This gives consistent visual
# placement regardless of the chart's plot-area height or left-margin
# width — both of which previously caused captions to land in
# different visual positions across chart types.
#
# CAPTION_X_SHIFT_PX is negative so the caption starts to the LEFT of
# the plot area (under the y-axis label region), aligning with the
# chart container's left edge. The exact value matches the smallest
# left margin in use (l=70 on most chart types). For charts with a
# wider left margin (e.g. subperiod_sharpe l=200), the caption still
# starts at the same horizontal pixel under the chart container, not
# under the plot area.
#
# CAPTION_Y_SHIFT_PX is the vertical pixel distance from the bottom of
# the plot area to the top of the caption text. Sized to leave room
# for tick labels (~18 px) + axis title (~25 px) + gap (~15 px).

CAPTION_X_SHIFT_PX: int = -70   # paper x=0 is plot-area left; this lands
                                # the caption flush with chart-container left
CAPTION_Y_SHIFT_PX: int = -65   # 65 px below the bottom of the plot area
                                # (≈ below the axis title)

# Pull the X-axis title up against the tick labels so it doesn't drift down
# into the caption zone.
XAXIS_STANDOFF: int = 12

# Bottom margin large enough for: tick labels + axis title + caption + gap.
MARGIN_B_WITH_CAPTION: int = 120

# Caption font.
CAPTION_FONT: dict = {"size": 10, "color": "grey"}


# Legacy alias for the patcher (which still uses paper-y coords on the
# already-shipped JSONs). When the patcher detects an existing paper-
# anchored caption, it normalises it to CAPTION_Y; the helper installs
# NEW annotations with xshift/yshift instead. Both end up in roughly
# the same place.
CAPTION_Y: float = -0.58


# ─── Helpers ──────────────────────────────────────────────────────────────


def apply_caption_layout(fig, caption_text: str) -> None:
    """Apply the canonical X-axis title + caption layout to ``fig``.

    The caption is positioned by PIXEL OFFSET from the bottom-left of the
    plot area (``xref="paper"`` with ``xshift``/``yshift``). This gives
    consistent visual placement across chart types — independent of
    ``margin.l`` (wide left margins for episode labels) and ``height``
    (different plot-area heights). Previously the caption used pure paper
    coords (``x=0, y=-0.58``) which scaled with the plot area and produced
    visually divergent placement.

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

    fig.add_annotation(
        text=caption_text,
        xref="paper",
        yref="paper",
        x=0,
        y=0,                       # anchor to bottom-left of plot area
        xshift=CAPTION_X_SHIFT_PX, # then shift by absolute pixels
        yshift=CAPTION_Y_SHIFT_PX,
        xanchor="left",
        yanchor="top",
        showarrow=False,
        font=CAPTION_FONT,
        align="left",
    )

    # Bottom-margin floor.
    margin = (fig.layout.margin or {}) if hasattr(fig.layout, "margin") else {}
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
