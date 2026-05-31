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

# Caption y-position (paper coordinates). Tuned for a ~400 px-tall chart
# with margin.b = MARGIN_B_WITH_CAPTION so the caption sits clearly below
# the X-axis title with a comfortable vertical gap.
CAPTION_Y: float = -0.58

# Pull the X-axis title up against the tick labels so it doesn't drift down
# into the caption zone.
XAXIS_STANDOFF: int = 12

# Bottom margin large enough for: tick labels + axis title + caption + gap.
MARGIN_B_WITH_CAPTION: int = 160

# Caption font.
CAPTION_FONT: dict = {"size": 10, "color": "grey"}


# ─── Helpers ──────────────────────────────────────────────────────────────


def apply_caption_layout(fig, caption_text: str) -> None:
    """Apply the canonical X-axis title + caption layout to ``fig``.

    Idempotent — re-applying produces the same layout, so it's safe to call
    from generators that may be re-run. Existing caption annotations (matched
    heuristically by font/text) are NOT removed; if you want to replace a
    previous caption, strip the old one before calling.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The figure to patch in place.
    caption_text : str
        The text to render as the grey source-note caption. HTML (<b>…</b>,
        <i>…</i>) is supported by Plotly.
    """
    # X-axis title standoff
    fig.update_xaxes(title_standoff=XAXIS_STANDOFF)

    # Caption annotation
    fig.add_annotation(
        text=caption_text,
        xref="paper",
        yref="paper",
        x=0,
        y=CAPTION_Y,
        xanchor="left",
        yanchor="top",
        showarrow=False,
        font=CAPTION_FONT,
        align="left",
    )

    # Bottom-margin floor
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
