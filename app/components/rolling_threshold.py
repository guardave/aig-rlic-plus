"""Rolling-percentile threshold (``T2_rp<NN>``) description, derived from the pair's own artifacts.

The window is NEVER assumed: it comes from ``winner_summary.threshold_window_days`` (preferred) or is
parsed from the winner's ``threshold_note`` / ``threshold_display_name`` ("trailing-504-day ...",
"rolling 504d"). If neither says, ``window`` is None and callers must use neutral wording and must
not redraw the boundary (a wrong number is worse than none).
"""

from __future__ import annotations

import re
from pathlib import Path
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


# ---------------------------------------------------------------------------
# Period-based rolling quantile thresholds (``T_roll_p<NN>`` / ``T2_roll_p<NN>``).
#
# These are the monthly / quarterly (and phlxsox daily) pairs whose threshold is the rolling
# NN-th percentile of the (lead-shifted) signal over a pair-specific lookback. The window is
# read from the pair's own artifacts - winner_summary ``lookback`` ("LB36", "60m", "20q") or the
# ``threshold_display_name`` ("75th percentile (rolling 60-month)") - and is NEVER assumed.
# ---------------------------------------------------------------------------
_ROLL_CODE = re.compile(r"t2?_roll_p(\d+)")
_UNIT_BY_LEAD = {"months": "month", "quarters": "quarter", "days": "day"}
_UNIT_BY_SUFFIX = {"m": "month", "q": "quarter", "d": "day"}


def _ordinal(n: int) -> str:
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def rolling_quantile_spec(winner: dict[str, Any]) -> dict[str, Any] | None:
    """None unless the winner's threshold is a period-based rolling quantile; else
    ``{pct, quantile, window, unit, min_periods, label}``.

    ``window``/``unit``/``min_periods`` are None when the artifacts do not record the window, in
    which case ``label`` uses neutral wording (never a guessed window)."""
    m = _ROLL_CODE.fullmatch(str(winner.get("threshold_code", "")).lower())
    if not m:
        return None
    pct = int(m.group(1))
    window: int | None = None
    unit: str | None = None
    lb = str(winner.get("lookback") or "")
    mm = re.match(r"LB(\d+)\b", lb, re.I)
    if mm:
        window = int(mm.group(1))
        unit = _UNIT_BY_LEAD.get(str(winner.get("lead_unit") or "").lower())
    else:
        mm = re.match(r"(\d+)\s*([mqd])\b", lb, re.I)
        if mm:
            window, unit = int(mm.group(1)), _UNIT_BY_SUFFIX[mm.group(2).lower()]
    if window is None:
        for key in ("threshold_display_name", "threshold_note"):
            mm = re.search(r"(\d+)[- ](month|quarter|day)s?\b", str(winner.get(key) or ""), re.I)
            if mm:
                window, unit = int(mm.group(1)), mm.group(2).lower()
                break
    if window is not None and (window < 2 or unit is None):
        window, unit = None, None
    stat = "median" if pct == 50 else f"{_ordinal(pct)} percentile"
    label = (f"rolling {window}-{unit} {stat}" if window
             else f"rolling {stat} (window not recorded)")
    return {"pct": pct, "quantile": pct / 100, "window": window, "unit": unit,
            "min_periods": int(window * 0.6) if window else None, "label": label}


def active_rolling_spec(winner: dict[str, Any]) -> dict[str, Any] | None:
    """The rolling-threshold spec for either family (``T2_rp<NN>`` daily trailing percentile, or
    ``T_roll_p<NN>`` / ``T2_roll_p<NN>`` period rolling quantile); None for non-rolling thresholds."""
    return rolling_pct_spec(winner) or rolling_quantile_spec(winner)


def resolve_threshold(pair_id: str, winner: dict[str, Any], repo_root: Path | None = None) -> dict[str, Any]:
    """Single source of truth for how a pair's winner threshold is described on the page.

    Returns ``{spec, label, value, source}``:
      * ``spec``/``label``: the rolling spec and its wording (None for fixed thresholds);
      * ``value``: the numeric threshold (latest boundary value for a rolling rule), or None;
      * ``source``: "recorded" (winner_summary.threshold_value), "derived" (latest rolling boundary
        recomputed from the pair's signals parquet using the documented window and the winner's lead
        shift - only when the summary records no number and the window is known), or "none".
    Nothing is ever defaulted: a missing value stays None so callers use neutral wording.
    """
    spec = active_rolling_spec(winner)
    raw = winner.get("threshold_value")
    try:
        if raw is not None and not isinstance(raw, bool) and raw != "":
            return {"spec": spec, "label": spec["label"] if spec else None,
                    "value": float(raw), "source": "recorded", "raw": raw}
    except (TypeError, ValueError):
        pass
    value = None
    if spec and spec.get("window"):
        root = repo_root or Path(__file__).resolve().parents[2]
        if repo_root is None:
            from components.provenance import CurrentRunFileError, current_file
            try:
                cur = current_file(pair_id, "signals", "parquet")
            except CurrentRunFileError:
                cur = None
            files = [cur] if cur else []
        else:
            files = sorted((root / "results" / pair_id).glob("signals_*.parquet"))
        col = winner.get("signal_column")
        if files and col:
            try:
                lead = winner.get("lead_value")
                lead = lead if isinstance(lead, int) and not isinstance(lead, bool) and lead > 0 else None
                value = latest_rolling_value(pd.read_parquet(files[-1])[col], spec, lead)
            except Exception:
                value = None
    return {"spec": spec, "label": spec["label"] if spec else None, "value": value,
            "source": "derived" if value is not None else "none", "raw": None}
