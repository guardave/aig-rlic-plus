"""Inputs of each track: pinned panels and vintages in, lagged reading frames on the rebalance index out.

Every track uses the full period grid (no dropped periods: a period that was never published, e.g. UNRATE
2025-10 during the shutdown, is a NaN reading, and the target return of the next period is a one-period return).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import align
from .candidates import reading_frame
from .engine import TrackInputs
from .spec import PairSpec

REPO = Path(__file__).resolve().parents[2]
PINNED = REPO / "data" / "phaseB_inputs"


def period_grid(start, end, freq: str) -> pd.DatetimeIndex:
    return pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq={"M": "ME", "Q": "QE"}[freq])


def load_pinned(name: str) -> pd.DataFrame:
    """A pinned input CSV under data/phaseB_inputs (first column = date index)."""
    return pd.read_csv(PINNED / name, index_col=0, parse_dates=True, float_precision="round_trip")


def latest_levels(series_id: str, freq: str, asof=None) -> pd.Series:
    """Today's revised values (the latest vintage in the pinned ALFRED file), on the full period grid."""
    vint = align.load_vintages(series_id)
    d = pd.Timestamp(asof) if asof is not None else vint.realtime_start.max()
    v = align.vintage_asof(vint, d, freq)
    return v.reindex(period_grid(v.index.min(), v.index.max(), freq))


def target_returns(prices: pd.Series, index: pd.DatetimeIndex) -> np.ndarray:
    """Period returns of the target on `index`. A missing close inside the grid is an error (no silent
    multi-period returns)."""
    p = prices.reindex(index)
    first = p.first_valid_index()
    if p.loc[first:].isna().any():
        raise ValueError(f"target price missing inside the grid: {list(p.loc[first:][p.loc[first:].isna()].index[:5])}")
    return p.pct_change().to_numpy(float)


def _extend_to(levels: pd.DataFrame, index: pd.DatetimeIndex, freq: str) -> pd.DataFrame:
    """`levels` with empty rows appended up to index[-1] on its own period grid (monthly / quarterly) or the
    index's trading days (daily). Earlier rows are untouched."""
    if not len(index) or not len(levels) or levels.index.max() >= index[-1]:
        return levels
    if freq in ("M", "Q"):
        ext = period_grid(levels.index.max(), index[-1], freq)
    else:
        ext = index[index > levels.index.max()]
    return levels.reindex(levels.index.union(ext))


def revised_inputs(spec: PairSpec, levels: pd.DataFrame, index: pd.DatetimeIndex, ret: np.ndarray,
                   name: str = "revised", harsh: bool = False) -> TrackInputs:
    """Revised (or unrevised market) values, point-in-time timing: the reading frame is built on the level
    grid and as-of shifted there with the series' availability dates, then read on the rebalance index. The level
    grid is first extended to the end of the rebalance index (empty readings): a series that ends before the last
    rebalance period (HSN1F 2026-08 vs SPY 2026-09) otherwise left that period undefined although its lagged
    reading was published long before (QA B1 nhs F1; the 1-period comparison undefined tails)."""
    levels = _extend_to(levels, index, spec.freq)
    frame = reading_frame(spec, levels)
    rel = align.release_for(spec.release_series, frame.index, harsh=harsh)
    lagged = {L: align.lag_asof(frame, L, rel, spec.position_shift).reindex(index) for L in spec.leads}
    return TrackInputs(name, index, ret, lagged, {"alignment": "pit_asof", "release_series": spec.release_series,
                                                  "harsh": harsh})


def realtime_inputs(spec: PairSpec, vint: pd.DataFrame, index: pd.DatetimeIndex, ret: np.ndarray,
                    value_map=None) -> TrackInputs:
    """Real-time values: per row, the vintage visible when the window opens (after-close aware). `value_map`
    transforms every visible vintage first (the real-time null no longer uses it: null v3 rolls the built inputs)."""
    col = spec.level_columns[0]
    ac = align.after_close_rule(spec.vintage_series)
    lagged = align.realtime_frames(vint, index, spec.leads,
                                   lambda v: reading_frame(spec, v.rename(col).to_frame()),
                                   spec.position_shift, spec.freq, ac, value_map)
    return TrackInputs("real_time", index, ret, lagged,
                       {"alignment": "realtime_vintage", "vintage_series": spec.vintage_series,
                        "after_close": ac, "first_vintage": vint.realtime_start.min().date().isoformat()})


def legacy_inputs(spec: PairSpec, panel: pd.DataFrame, ret: np.ndarray) -> TrackInputs:
    """Replay of a pre-harness pipeline: reading frame on its own panel, fixed shift(lead)."""
    frame = reading_frame(spec, panel)
    return TrackInputs("legacy", panel.index, ret, {L: align.lag_fixed(frame, L) for L in spec.leads},
                       {"alignment": "fixed_lag"})
