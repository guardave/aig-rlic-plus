"""Canonical NBER recession periods + shading helper (DUP-4 consolidation).

Before fix260531 six chart scripts each hardcoded their own `RECESSIONS`
tuple list. They had drifted: five used 2020-04-01 as the COVID end,
generate_history_zoom_charts.py used 2020-04-30, and the latter also
included the 1990 recession that the others omitted.

This module is the single source of truth for NBER-dated US recessions
used as plot shading. The list is short and slow-changing — once per
business cycle — so a Python constant is cheaper than a runtime JSON
read. When the NBER announces a new recession the change goes here and
every consumer picks it up.

Usage:

    from scripts._nber import RECESSIONS, add_nber_shading

    add_nber_shading(fig, x_min=zoom_start, x_max=zoom_end)
"""

from __future__ import annotations

from typing import Iterable, Sequence

import pandas as pd

# ─── Canonical recession list (NBER, official) ────────────────────────────
#
# Source: National Bureau of Economic Research US Business Cycle
# Expansions and Contractions (https://www.nber.org/cycles.html).
# Listed back to 1990 — older cycles are rarely needed for portal charts.
# When NBER announces a new recession or revises a date, update this list.

RECESSIONS: list[tuple[str, str]] = [
    ("1990-07-01", "1991-03-31"),
    ("2001-03-01", "2001-11-30"),
    ("2007-12-01", "2009-06-30"),
    ("2020-02-01", "2020-04-30"),
]

# Default fill colour for the shading rectangle.
RECESSION_FILL = "rgba(150, 120, 120, 0.22)"


# ─── Helper ───────────────────────────────────────────────────────────────


def add_nber_shading(
    fig,
    x_min=None,
    x_max=None,
    *,
    xref: str = "x",
    yref: str = "paper",
    row: int | None = None,
    col: int | None = None,
    fillcolor: str = RECESSION_FILL,
    recessions: Sequence[tuple[str, str]] | None = None,
) -> None:
    """Add NBER recession shading rectangles to a Plotly figure.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        Figure to mutate.
    x_min, x_max : optional, accept anything convertible by ``pd.Timestamp``
        Clip recessions to this window. If ``None``, all recessions are
        rendered (Plotly will only show those within the chart's axis range).
    xref, yref : str
        Plotly axis references. Use ``"x"``/``"paper"`` for full-height
        shading on a single-panel chart; ``"x2"``/``"paper"`` for the
        second-panel x-axis on a dual-panel chart.
    row, col : int, optional
        For subplot figures, the row/col to add the shape to.
    fillcolor : str
        RGBA fill colour. Default ``RECESSION_FILL``.
    recessions : list of (start_iso, end_iso), optional
        Override the global ``RECESSIONS`` list. Used for tests; production
        code should leave this default.
    """
    rec = recessions if recessions is not None else RECESSIONS
    x_min_ts = pd.Timestamp(x_min) if x_min is not None else None
    x_max_ts = pd.Timestamp(x_max) if x_max is not None else None
    for start_iso, end_iso in rec:
        start = pd.Timestamp(start_iso)
        end = pd.Timestamp(end_iso)
        # Filter recessions entirely outside the window.
        if x_max_ts is not None and start > x_max_ts:
            continue
        if x_min_ts is not None and end < x_min_ts:
            continue
        # Clip to window edges (where defined) so the shape doesn't extend
        # off-chart.
        start_clipped = max(start, x_min_ts) if x_min_ts is not None else start
        end_clipped = min(end, x_max_ts) if x_max_ts is not None else end
        kwargs: dict = dict(
            type="rect",
            x0=start_clipped.isoformat(),
            x1=end_clipped.isoformat(),
            y0=0,
            y1=1,
            xref=xref,
            yref=yref,
            fillcolor=fillcolor,
            layer="below",
            line_width=0,
        )
        if row is not None and col is not None:
            fig.add_shape(row=row, col=col, **kwargs)
        else:
            fig.add_shape(**kwargs)


__all__: Iterable[str] = ("RECESSIONS", "RECESSION_FILL", "add_nber_shading")
