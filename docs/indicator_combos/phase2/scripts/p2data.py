"""Shared point-in-time data access for Phase 2 (EXPLORATORY). Read-only use of the repository's PIT machinery.

Conventions
  * Monthly decision index: month-end stamps; a decision at month-end t is made at the close of the last trading day
    of t (scripts/_pit_align.last_trading_day) and earns / is scored against what happens after t.
  * ALFRED series: the vintage visible at that close, transform recomputed inside the vintage
    (scripts/_pit_align.realtime_apply with lead 0, position_shift 1).
  * Daily market series posted by FRED the next business day (T10Y3M, ICE BofA OAS): the value dated the previous
    trading day is used at the month-end close.
  * Asset returns: SPY dividend-adjusted month-end closes pinned by Phase B
    (feat261017_phaseB_harness:data/phaseB_inputs/spy_month_end_20261017.csv), read with `git show`, read-only.
  * NBER recessions: scripts/_nber.RECESSIONS (1990+) plus the two earlier NBER-dated recessions in the vintage era
    (1980-01..1980-07, 1981-07..1982-11).

Every git call runs with all GIT_* variables removed (lesson of 2026-10-17, KNOWN_LIMITS.md section 6).
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
from _nber import RECESSIONS  # noqa: E402
from _pit_align import TRADING_DAY, last_trading_day, load_vintages, realtime_apply  # noqa: E402

P2 = REPO / "docs" / "indicator_combos" / "phase2"
PIN = P2 / "data" / "pinned"
END = pd.Timestamp("2026-09-30")
EARLY_RECESSIONS = [("1980-01-01", "1980-07-31"), ("1981-07-01", "1982-11-30")]
HARNESS_BRANCH = "feat261017_phaseB_harness"


def clean_env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git_show(ref_path: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "show", ref_path], capture_output=True, text=True, check=True,
                          env=clean_env()).stdout


def month_index(start: str, end=END) -> pd.DatetimeIndex:
    return pd.date_range(start, end, freq="ME")


@lru_cache(maxsize=1)
def spy_monthly() -> pd.DataFrame:
    """SPY dividend-adjusted month-end close and simple monthly return (row t = return over month t)."""
    d = pd.read_csv(io.StringIO(git_show(f"{HARNESS_BRANCH}:data/phaseB_inputs/spy_month_end_20261017.csv")),
                    parse_dates=["date"]).set_index("date")
    d.index = d.index.to_period("M").to_timestamp(how="end").normalize()
    d["ret"] = d["spy_close"].pct_change()
    return d


def nber_monthly(index: pd.DatetimeIndex) -> pd.Series:
    """1 in NBER recession months (peak month excluded, trough month included, NBER convention), else 0."""
    rec = pd.Series(0, index=index, dtype=int)
    for a, b in EARLY_RECESSIONS + list(RECESSIONS):
        pk = pd.Timestamp(a).to_period("M")
        tr = pd.Timestamp(b).to_period("M")
        m = (index.to_period("M") > pk) & (index.to_period("M") <= tr)
        rec[m] = 1
    return rec


def recession_episodes() -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """(peak month-end, trough month-end) for every recession used."""
    out = []
    for a, b in EARLY_RECESSIONS + list(RECESSIONS):
        out.append((pd.Timestamp(a).to_period("M").to_timestamp(how="end").normalize(),
                    pd.Timestamp(b).to_period("M").to_timestamp(how="end").normalize()))
    return out


def _prev_bday_month_end(daily: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    """Value dated the trading day before each month-end close (next-business-day posting rule)."""
    s = daily.dropna().sort_index()
    closes = last_trading_day(index)
    asof = pd.DatetimeIndex([c - TRADING_DAY for c in closes])
    v = s.reindex(s.index.union(asof)).ffill().reindex(asof)
    out = pd.Series(v.to_numpy(), index=index)
    out[asof > s.index.max()] = np.nan
    return out


def fred_daily_pinned(series_id: str) -> pd.Series:
    """FRED daily market series, pulled once and pinned under phase2/data/pinned/ (unrevised market data).
    T10Y3M is NOT one of the do-not-acquire gaps (G5/G13/G15/G16/G17); it is gap G8 (pre-2000 market history)."""
    PIN.mkdir(parents=True, exist_ok=True)
    hits = sorted(PIN.glob(f"fred_{series_id}_*.csv"))
    if hits:
        return pd.read_csv(hits[-1], parse_dates=["date"]).set_index("date")["value"]
    from fredapi import Fred
    s = Fred(api_key=os.environ["FRED_API_KEY"]).get_series(series_id).rename("value")
    s.index.name = "date"
    s.to_frame().to_csv(PIN / f"fred_{series_id}_{pd.Timestamp.today():%Y%m%d}.csv")
    return s


def t10y3m(index: pd.DatetimeIndex) -> pd.Series:
    return _prev_bday_month_end(fred_daily_pinned("T10Y3M"), index).rename("term")


def hy_ig(index: pd.DatetimeIndex) -> pd.Series:
    hy = pd.read_parquet(REPO / "data/hy_ig_spy_daily_20000101_20260422.parquet", columns=["hy_oas", "ig_oas"])
    return _prev_bday_month_end(hy["hy_oas"] - hy["ig_oas"], index).rename("credit")


def _rt(series_id: str, index: pd.DatetimeIndex, fn) -> pd.Series:
    v = load_vintages(series_id)
    out = realtime_apply(v, index, lead=0, fn=fn, position_shift=1, freq="M")
    return out.iloc[:, 0]


def sahm_gap(index: pd.DatetimeIndex) -> pd.Series:
    """Real-time Sahm gap: 3-month average UNRATE minus the minimum of the 3-month averages of the prior 12 months
    (Sahm 2019), computed inside the UNRATE vintage visible at each month-end close."""
    def fn(s):
        ma = s.rolling(3).mean()
        return (ma - ma.shift(1).rolling(12).min()).rename("sahm")
    return _rt("UNRATE", index, fn).rename("sahm")


def permit_yoy(index: pd.DatetimeIndex) -> pd.Series:
    return _rt("PERMIT", index, lambda s: (100 * (s / s.shift(12) - 1)).rename("permit")).rename("permit")


def spy_sma_flag(index: pd.DatetimeIndex) -> pd.Series:
    """1 when the SPY month-end close is below its 10-month SMA (known at the close), NaN before SPY exists."""
    p = spy_monthly()["spy_close"]
    f = (p < p.rolling(10).mean()).astype(float)
    f[p.rolling(10).mean().isna()] = np.nan
    return f.reindex(index).rename("sma_flag")
