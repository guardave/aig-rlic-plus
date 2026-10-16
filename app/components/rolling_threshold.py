"""Rolling-percentile threshold (``T2_rp<NN>``) description, derived from the pair's own artifacts.

The window is NEVER assumed: it comes from ``winner_summary.threshold_window_days`` (preferred) or is
parsed from the winner's ``threshold_note`` / ``threshold_display_name`` ("trailing-504-day ...",
"rolling 504d"). If neither says, ``window`` is None and callers must use neutral wording and must
not redraw the boundary (a wrong number is worse than none).
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

_CODE = re.compile(r"t2_rp(\d+)")
_WINDOW_PATTERNS = (
    re.compile(r"(\d+)[- ]?(?:trading[- ])?days?\b", re.I),   # "504-day", "504 day", "252 trading days"
    re.compile(r"\b(\d+)d\b", re.I),                           # "rolling 504d"
)


def _parse_window(winner: dict[str, Any]) -> int | None:
    w = winner.get("threshold_window_days")
    if isinstance(w, int) and not isinstance(w, bool) and w >= 2:
        return w
    for key in ("threshold_note", "threshold_display_name"):
        text = str(winner.get(key) or "")
        for pat in _WINDOW_PATTERNS:
            m = pat.search(text)
            if m and int(m.group(1)) >= 2:
                return int(m.group(1))
    return None


def rolling_pct_spec(winner: dict[str, Any]) -> dict[str, Any] | None:
    """None if the winner's threshold is not a ``T2_rp<NN>`` rolling percentile; else
    ``{pct, quantile, window, min_periods, label}`` (``window``/``min_periods`` None if unknown)."""
    m = _CODE.fullmatch(str(winner.get("threshold_code", "")).lower())
    if not m:
        return None
    pct = int(m.group(1))
    window = _parse_window(winner)
    mp = winner.get("threshold_min_periods")
    if window is not None and not (isinstance(mp, int) and not isinstance(mp, bool) and 1 <= mp <= window):
        mp = int(window * 0.8)
    if window is None:
        mp = None
    label = (f"trailing {window}-day {pct}th percentile" if window
             else f"rolling {pct}th percentile (window not recorded)")
    return {"pct": pct, "quantile": pct / 100, "window": window, "min_periods": mp, "label": label}


def latest_rolling_value(signal: pd.Series, spec: dict[str, Any], lead_days: int | None) -> float | None:
    """Latest value of the rolling percentile of the (lead-shifted) signal; None if not computable."""
    if not spec or not spec.get("window"):
        return None
    s = signal.shift(lead_days) if lead_days else signal
    q = s.rolling(spec["window"], min_periods=spec["min_periods"]).quantile(spec["quantile"]).dropna()
    return float(q.iloc[-1]) if len(q) else None
