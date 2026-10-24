"""Point-in-time (as-of) alignment of a lagged signal to its actual release dates.

Shared helper for the pair pipelines (design: _pws/lead-lesandro/pkg12_pit_release/DESIGN.md). It replaces the
fixed-lag `signal.shift(lead)` with an as-of shift that never lets a reading drive a return window opening before
the reading was public.

Conventions (identical to the pipelines):
  * `index` is the pipeline's rebalance index (month-end / quarter-end / trading-day stamps, ascending). Row u holds
    the reading for the reference period stamped index[u] and, for return rows, the return index[u-1] -> index[u].
  * A position computed at row u is applied to return row u + position_shift, whose window opens at the close of
    index[u + position_shift - 1] (rolled back to the last trading day).
  * A reading is AVAILABLE for that window iff first_release <= window-open date (a release on the open date counts,
    standard Step 2).

as-of rule: row u uses the reading stamped index[u - k_u], where k_u is the smallest k >= lead whose reading is
available for the row's window, i.e. the latest released reading at or before the nominal one (index[u - lead]).
It never uses a reading newer than the nominal one. When nothing within `max_extra` extra periods is available,
the row is NaN (no position).

    from _pit_align import load_release, pit_shift
    rel = load_release("INDPRO", df.index)                  # first-release date per row stamp
    sig_L = pit_shift(df[["sig", "thr"]], lead, rel)          # instead of df[["sig", "thr"]].shift(lead)
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.tseries.holiday import (AbstractHolidayCalendar, GoodFriday, Holiday, USLaborDay, USMartinLutherKingJr,
                                    USMemorialDay, USPresidentsDay, USThanksgivingDay, nearest_workday,
                                    sunday_to_monday)
from pandas.tseries.offsets import CustomBusinessDay

REPO = Path(__file__).resolve().parents[1]
CALENDAR = REPO / "data" / "release_calendar" / "release_calendar.csv"
MAX_EXTRA = 24  # periods searched beyond the nominal lead before giving up (NaN)


# Unscheduled full-day NYSE closures since 1980 (weather, national mourning, 9/11).
_NYSE_SPECIAL_CLOSURES = ["1985-09-27", "1994-04-27", "2001-09-11", "2001-09-12", "2001-09-13", "2001-09-14",
                          "2004-06-11", "2007-01-02", "2012-10-29", "2012-10-30", "2018-12-05", "2025-01-09"]


class _TradingHolidays(AbstractHolidayCalendar):
    """NYSE full-day closures. Differs from the federal calendar: New Year's Day on a Saturday is NOT observed on the
    prior Friday (NYSE Rule 7.2; e.g. 2004-12-31, 2010-12-31 and 2021-12-31 were trading days); MLK Day from 1998;
    Juneteenth from 2022; Good Friday; no Columbus / Veterans Day; plus the unscheduled closures above."""
    rules = [Holiday("New Year's Day", month=1, day=1, observance=sunday_to_monday),
             Holiday("Martin Luther King Jr. Day", month=1, day=1, offset=USMartinLutherKingJr.offset,
                     start_date="1998-01-01"),
             USPresidentsDay, GoodFriday, USMemorialDay,
             Holiday("Juneteenth", month=6, day=19, observance=nearest_workday, start_date="2022-01-01"),
             Holiday("Independence Day", month=7, day=4, observance=nearest_workday),
             USLaborDay, USThanksgivingDay,
             Holiday("Christmas Day", month=12, day=25, observance=nearest_workday)] + [
        Holiday(f"NYSE closure {d}", year=int(d[:4]), month=int(d[5:7]), day=int(d[8:])) for d in _NYSE_SPECIAL_CLOSURES]


TRADING_DAY = CustomBusinessDay(calendar=_TradingHolidays())


def last_trading_day(ts: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Roll each stamp back to the last trading day on or before it (the close that opens the return window)."""
    ts = pd.DatetimeIndex(ts).normalize()
    return pd.DatetimeIndex([t if TRADING_DAY.is_on_offset(t) else TRADING_DAY.rollback(t) for t in ts])


@lru_cache(maxsize=4)
def _calendar(path: str) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["ref_date", "period_end", "first_release"])


def load_release(series_id: str, index: pd.DatetimeIndex, path: Path | str = CALENDAR, harsh: bool = False) -> pd.Series:
    """Availability date for each stamp of `index`, matched on the reference period that contains the stamp
    (monthly or quarterly per the calendar): the calendar's available_date (first release, moved to the next trading
    day for after-close releases); harsh=True uses the shutdown-inclusive fallback variant (sensitivity). NaT where
    the calendar has no date (never published, before the calendar starts or after its last period): such readings
    are treated as never available."""
    cal = _calendar(str(path))
    c = cal[cal.series_id == series_id]
    if c.empty:
        raise KeyError(f"series {series_id!r} not in {path}")
    col = ("available_date_harsh" if harsh else "available_date") if "available_date" in c else "first_release"
    freq = "Q" if (c.ref_date.diff().dropna().dt.days > 80).all() else "M"
    by_period = pd.Series(pd.to_datetime(c[col]).values, index=c.period_end.dt.to_period(freq))
    idx = pd.DatetimeIndex(index)
    out = pd.Series(by_period.reindex(idx.to_period(freq)).values, index=idx, name=f"release_{series_id}")
    out.attrs["first_period_end"] = c.period_end.min()  # readings stamped before this do not exist in the series
    return out


def is_daily(index: pd.DatetimeIndex) -> bool:
    """A trading-day index (median spacing <= 4 days): its stamps ARE the closes, no calendar roll-back."""
    idx = pd.DatetimeIndex(index)
    return len(idx) > 2 and pd.Series(idx).diff().dt.days.median() <= 4


def rule_release(index: pd.DatetimeIndex, business_days: int = 1) -> pd.Series:
    """Release dates for a series posted `business_days` trading days after the stamp (0 = observed at the close).
    On a trading-day index the next trading day is the next row of the index (the pipeline's own calendar)."""
    idx = pd.DatetimeIndex(index)
    if business_days == 0:
        rel = idx
    elif is_daily(idx):
        n = business_days
        tail = [idx[-1] + (k + 1) * TRADING_DAY for k in range(n)]
        rel = idx[n:].append(pd.DatetimeIndex(tail))
    else:
        rel = pd.DatetimeIndex([t + business_days * TRADING_DAY for t in idx])
    return pd.Series(rel, index=idx, name="release_rule")


def window_open(index: pd.DatetimeIndex, position_shift: int = 0) -> pd.Series:
    """Window-open date of the return earned by a position computed at row u: close of index[u + shift - 1]
    (period-end stamps rolled back to the last trading day; a trading-day index is used as is)."""
    idx = pd.DatetimeIndex(index)
    closes = pd.Series(idx if is_daily(idx) else last_trading_day(idx), index=idx)
    return closes.shift(1 - position_shift)


def asof_lags(index: pd.DatetimeIndex, lead: int, release: pd.Series, position_shift: int = 0,
              max_extra: int = MAX_EXTRA) -> pd.Series:
    """Per-row as-of lag k_u >= lead (rows), or <NA> when no available reading within lead + max_extra."""
    if lead < 0 or position_shift not in (0, 1):
        raise ValueError("lead must be >= 0 and position_shift 0|1")
    idx = pd.DatetimeIndex(index)
    if not idx.is_monotonic_increasing or idx.has_duplicates:
        raise ValueError("index must be strictly increasing")
    rel = pd.Series(release).reindex(idx).to_numpy(dtype="datetime64[ns]")
    opn = window_open(idx, position_shift).to_numpy(dtype="datetime64[ns]")
    n, out = len(idx), np.full(len(idx), -1, dtype=np.int64)
    for u in range(n):
        if np.isnat(opn[u]):
            continue
        for k in range(lead, lead + max_extra + 1):
            j = u - k
            if j < 0:
                break
            if not np.isnat(rel[j]) and rel[j] <= opn[u]:
                out[u] = k
                break
    return pd.Series(pd.array(np.where(out >= 0, out, None), dtype="Int64"), index=idx, name="asof_lag")


def take_lagged(obj, lags: pd.Series):
    """Row u of the result is obj row u - lags[u] (NaN where lags is NA). Works on Series and DataFrames."""
    lags = pd.Series(lags).reindex(obj.index)
    src = np.arange(len(obj)) - lags.fillna(-10**9).to_numpy(dtype=np.int64)
    ok = lags.notna().to_numpy() & (src >= 0)
    vals = obj.to_numpy(dtype=float) if isinstance(obj, pd.Series) else obj.to_numpy(dtype=float)
    res = np.full(vals.shape, np.nan)
    res[ok] = vals[src[ok]]
    if isinstance(obj, pd.Series):
        return pd.Series(res, index=obj.index, name=obj.name)
    return pd.DataFrame(res, index=obj.index, columns=obj.columns)


def pit_shift(obj, lead: int, release: pd.Series, position_shift: int = 0, max_extra: int = MAX_EXTRA):
    """As-of replacement for `obj.shift(lead)`: row u gets the latest reading at or before index[u - lead] that was
    public when the row's return window opens (see module doc). Shift every input of the trading rule (signal AND
    rolling threshold) through the same call so they refer to the same reading."""
    return take_lagged(obj, asof_lags(obj.index, lead, release, position_shift, max_extra))


def breaches(index: pd.DatetimeIndex, lead: int, release: pd.Series, position_shift: int = 0,
             start=None, end=None, data_start=None) -> pd.DataFrame:
    """Rows where the FIXED-lag rule (reading index[u - lead]) uses a reading not public when the window opens,
    restricted to rows u whose return row (u + position_shift) lies in [start, end]. Rows whose nominal reading is
    stamped before `data_start` (default release.attrs["first_period_end"]: the series does not exist yet, so the
    pipeline has no signal and no position) are not breaches. Columns: return row, nominal reading stamp, its
    release (NaT = never released), window open, days_early (release - open, > 0), as-of lag."""
    if data_start is None:
        data_start = getattr(release, "attrs", {}).get("first_period_end")
    idx = pd.DatetimeIndex(index)
    rel = pd.Series(release).reindex(idx)
    opn = window_open(idx, position_shift)
    nominal = pd.Series(idx, index=idx).shift(lead)
    nom_rel = rel.shift(lead)
    ret_row = pd.Series(idx, index=idx).shift(-position_shift)
    m = nominal.notna() & opn.notna() & ret_row.notna()
    if start is not None:
        m &= ret_row >= pd.Timestamp(start)
    if end is not None:
        m &= ret_row <= pd.Timestamp(end)
    if data_start is not None:
        m &= nominal >= pd.Timestamp(data_start)
    bad = m & (nom_rel.isna() | (nom_rel > opn))
    lags = asof_lags(idx, lead, release, position_shift)
    out = pd.DataFrame({"return_row": ret_row[bad], "reading": nominal[bad], "release": nom_rel[bad],
                        "window_open": opn[bad]})
    out["days_early"] = (out.release - out.window_open).dt.days
    out["asof_lag"] = lags[bad]
    return out


# ---------------------------------------------------------------------------------------------------------------
# Track (b): real-time vintages. A REVISED value of period M is only known from the date of that revision, so
# latest-vintage values with first-release timing are themselves a lookahead (pkg12 D8). These helpers give the
# value "as known at date t" from ALFRED vintage histories (data/release_calendar/vintages/<SID>.csv.gz).
VINTAGES = REPO / "data" / "release_calendar" / "vintages"


def load_vintages(series_id: str, path: Path | str | None = None) -> pd.DataFrame:
    """ALFRED rows (date, realtime_start, realtime_end, value); realtime_end 9999-12-31 -> 2262-01-01."""
    v = pd.read_csv(Path(path) if path else VINTAGES / f"{series_id}.csv.gz", parse_dates=["date", "realtime_start"])
    v["realtime_end"] = pd.to_datetime(v["realtime_end"].astype(str).replace("9999-12-31", "2262-01-01"))
    v["value"] = v["value"].astype(float)
    return v


def vintage_asof(vint: pd.DataFrame, date, freq: str = "M") -> pd.Series:
    """The series as published on `date`: rows with realtime_start <= date <= realtime_end, stamped at period end.
    A period absent from it was not yet released on that date."""
    d = pd.Timestamp(date)
    x = vint[(vint.realtime_start <= d) & (vint.realtime_end >= d)]
    idx = x["date"].dt.to_period(freq).dt.to_timestamp(how="end").dt.normalize()
    s = pd.Series(x["value"].to_numpy(), index=pd.DatetimeIndex(idx)).sort_index()
    return s[~s.index.duplicated(keep="last")]


def after_close_rule(series_id: str, meta: Path | str = CALENDAR.with_name("release_calendar_meta.json")):
    """The calendar's after-close rule for a series: False, True (always after the 16:00 ET close) or a date
    string = after the close for releases before that date (e.g. M2SL until 2021-02-23)."""
    import json
    rule = json.loads(Path(meta).read_text()).get("after_close", {}).get(series_id)
    if not rule:
        return False
    return rule.get("before_close_from") or True


def visible_on(date, after_close=False) -> pd.Timestamp:
    """Vintage date whose contents are visible at the close of `date`: `date` itself, or the previous trading day
    when the series is published after the 16:00 ET close (Lead decision Q3)."""
    d = pd.Timestamp(date)
    if after_close is True or (isinstance(after_close, str) and d < pd.Timestamp(after_close)):
        return TRADING_DAY.rollback(d - pd.Timedelta(days=1))
    return d


def realtime_apply(vint: pd.DataFrame, index: pd.DatetimeIndex, lead: int, fn, position_shift: int = 0,
                   freq: str = "M", after_close=False) -> pd.DataFrame:
    """Track (b) as-of alignment. For each row u: take the vintage published at the row's window open, compute
    fn(vintage) (a Series/DataFrame on the vintage's period-end stamps, e.g. signal and rolling threshold), and
    return its row for the latest period present in that vintage at or before the nominal reading index[u - lead].
    Rows whose window opens before the first vintage, or with no reading, are NaN. Never uses a value published
    after the window opens. after_close (False | True | 'YYYY-MM-DD', see after_close_rule): a vintage posted
    after the 16:00 ET close on the window-open date is not used (QA2 M-1)."""
    idx = pd.DatetimeIndex(index)
    opn = window_open(idx, position_shift)
    first = vint.realtime_start.min()
    rows = {}
    for u, t in enumerate(idx):
        o = opn.iloc[u]
        if pd.isna(o) or o < first or u - lead < 0:
            continue
        v = vintage_asof(vint, visible_on(o, after_close), freq)
        full = pd.date_range(v.index.min(), v.index.max(), freq="QE" if freq == "Q" else "ME")
        out = fn(v.reindex(full))
        out = out.to_frame() if isinstance(out, pd.Series) else out
        ok = out.index[(out.index <= idx[u - lead]) & out.index.isin(v.index)]
        if len(ok):
            rows[t] = out.loc[ok.max()]
    return pd.DataFrame(rows).T.reindex(idx)
