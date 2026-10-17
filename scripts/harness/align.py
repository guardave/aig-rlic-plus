"""Timing: the only place where readings are matched to return windows.

A *reading frame* holds, on the indicator's own period stamps, every rule input of a pair (signal variables,
rolling thresholds, P2 range fractions). Lagging a reading frame to the rebalance index is done by exactly one
of three functions:

  lag_fixed     legacy replay only: frame.shift(lead) (the pre-Phase-B pipelines)
  lag_asof      revised / market track: _pit_align.pit_shift with the series' availability dates
  realtime_frames  real-time track: per row, the vintage published at the window open (after-close aware); the
                reading frame is recomputed inside that vintage. Equivalent to _pit_align.realtime_apply
                (tested), but caches one frame per distinct vintage and serves every lead in one pass.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _pit_align import (  # noqa: E402,F401  (re-exported: pipelines import timing helpers from here)
    after_close_rule, asof_lags, load_release, load_vintages, pit_shift, rule_release, take_lagged, vintage_asof,
    visible_on, window_open,
)

_LAGS: dict = {}


def release_for(series: str | None, index: pd.DatetimeIndex, harsh: bool = False) -> pd.Series:
    """Availability date per stamp: calendar series id, or 'rule:next_business_day' / 'rule:same_close'."""
    if series is None:
        raise ValueError("release series required for point-in-time alignment")
    if series == "rule:next_business_day":
        return rule_release(index, 1)
    if series == "rule:same_close":
        return rule_release(index, 0)
    return load_release(series, index, harsh=harsh)


def lag_fixed(frame: pd.DataFrame, lead: int) -> pd.DataFrame:
    """Legacy fixed-lag shift (replay of the published pre-harness rules only)."""
    return frame.shift(lead) if lead > 0 else frame


def lag_asof(frame: pd.DataFrame, lead: int, release: pd.Series, position_shift: int) -> pd.DataFrame:
    """As-of shift: row u uses the latest reading at or before index[u - lead] public at the window open
    (_pit_align.pit_shift). The per-row lags depend only on the index and the release dates, never on the values,
    so they are cached across null draws and leak-test rebuilds."""
    idx = frame.index
    rel = pd.Series(release).reindex(idx)
    key = (len(idx), idx[0], idx[-1], hash(idx.asi8.tobytes()), lead, position_shift,
           hash(rel.to_numpy(dtype="datetime64[ns]").tobytes()))
    if key not in _LAGS:
        _LAGS[key] = asof_lags(idx, lead, rel, position_shift)
    return take_lagged(frame, _LAGS[key])


def _vintage_key(rs: np.ndarray, re: np.ndarray, d: pd.Timestamp) -> tuple[int, int]:
    """Rows visible on d are those with realtime_start <= d <= realtime_end; their set is fixed by d's rank
    among the distinct start and end dates."""
    d64 = np.datetime64(d, "ns")
    return int(np.searchsorted(rs, d64, "right")), int(np.searchsorted(re, d64, "left"))


def _nominal(idx: pd.DatetimeIndex, u: int, lead: int, freq: str):
    """Stamp of the nominal reading for row u at `lead`: `lead` periods before index[u] on the period grid
    (monthly / quarterly), so rows near the start of the rebalance index still see earlier readings; on a
    trading-day index it is the row u - lead."""
    if freq in ("M", "Q"):
        return (pd.Period(idx[u], freq) - lead).to_timestamp(how="end").normalize()
    return idx[u - lead] if u - lead >= 0 else None


def realtime_frames(vint: pd.DataFrame, index: pd.DatetimeIndex, leads: Iterable[int],
                    frame_fn: Callable[[pd.Series], pd.DataFrame], position_shift: int = 0, freq: str = "M",
                    after_close=False) -> dict[int, pd.DataFrame]:
    """{lead: frame on `index`} where row u holds frame_fn(vintage visible at the window open of row u) at the
    latest period present in that vintage at or before the nominal reading (`lead` periods before index[u]).
    NaN when the window opens before the first vintage or no such period exists. Same rule as
    _pit_align.realtime_apply on every row u >= lead; rows u < lead, which realtime_apply leaves NaN, are filled
    from readings before the first rebalance row (as the revised track's as-of shift on the level grid does)."""
    idx = pd.DatetimeIndex(index)
    leads = list(leads)
    opn = window_open(idx, position_shift)
    first = vint.realtime_start.min()
    rs = np.sort(vint.realtime_start.unique().astype("datetime64[ns]"))
    re = np.sort(vint.realtime_end.unique().astype("datetime64[ns]"))
    cache: dict = {}
    cols = None
    out = {L: None for L in leads}
    rows = {L: {} for L in leads}
    for u, t in enumerate(idx):
        o = opn.iloc[u]
        if pd.isna(o) or o < first:
            continue
        d = visible_on(o, after_close)
        key = _vintage_key(rs, re, d)
        if key not in cache:
            v = vintage_asof(vint, d, freq)
            if v.empty:
                cache[key] = None
            else:
                full = pd.date_range(v.index.min(), v.index.max(), freq="QE" if freq == "Q" else "ME")
                f = frame_fn(v.reindex(full))
                f = f.to_frame() if isinstance(f, pd.Series) else f
                present = f.index.isin(v.index)
                cache[key] = (f, f.index[present])
        hit = cache[key]
        if hit is None:
            continue
        f, present_idx = hit
        cols = f.columns if cols is None else cols
        for L in leads:
            nominal = _nominal(idx, u, L, freq)
            if nominal is None:
                continue
            k = present_idx.searchsorted(nominal, "right") - 1
            if k >= 0:
                rows[L][t] = f.loc[present_idx[k]]
    for L in leads:
        df = pd.DataFrame(rows[L]).T if rows[L] else pd.DataFrame(columns=cols)
        out[L] = df.reindex(idx).astype(float)
    return out
