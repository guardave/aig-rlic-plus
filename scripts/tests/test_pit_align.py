"""Tests for scripts/_pit_align.py (point-in-time as-of alignment)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _pit_align as pa  # noqa: E402

ME = pd.date_range("2020-01-31", periods=24, freq="ME")


def mid_month_release(index, day=15):
    """Reading for month M released on `day` of M+1 (a mid-M+1 FRED-style source)."""
    return pd.Series([(t + pd.offsets.MonthBegin(1)).replace(day=day) for t in index], index=index)


def test_regular_release_matches_fixed_shift_at_floor():
    rel = mid_month_release(ME)
    sig = pd.Series(np.arange(len(ME), dtype=float), index=ME)
    # E2: reading M drives the window opening at ME(M+1), released mid M+1 -> always available
    out = pa.pit_shift(sig, 2, rel)
    pd.testing.assert_series_equal(out, sig.shift(2), check_names=False)
    assert pa.breaches(ME, 2, rel).empty


def test_below_floor_falls_back_to_previous_release():
    rel = mid_month_release(ME)
    sig = pd.Series(np.arange(len(ME), dtype=float), index=ME)
    lags = pa.asof_lags(ME, 1, rel)
    assert (lags.iloc[2:] == 2).all()  # L1 never available (released mid M+1 > ME(M)) -> as-of uses M-1
    assert pa.pit_shift(sig, 1, rel).iloc[5] == sig.iloc[3]
    assert len(pa.breaches(ME, 1, rel)) == len(ME) - 1


def test_no_lookahead_property_random_perturbation():
    """Changing a reading can only change rows whose return window opens on/after its release date."""
    rng = np.random.default_rng(12345)
    for _ in range(200):
        lag_days = rng.integers(-10, 120, size=len(ME))
        rel = pd.Series(ME + pd.to_timedelta(lag_days, unit="D"), index=ME)
        rel[rng.random(len(ME)) < 0.05] = pd.NaT  # some readings never published
        lead, shift = int(rng.integers(0, 4)), int(rng.integers(0, 2))
        sig = pd.Series(rng.normal(size=len(ME)), index=ME)
        base = pa.pit_shift(sig, lead, rel, shift)
        j = int(rng.integers(0, len(ME)))
        pert = sig.copy()
        pert.iloc[j] += 100.0
        new = pa.pit_shift(pert, lead, rel, shift)
        changed = ~((base == new) | (base.isna() & new.isna()))
        opn = pa.window_open(ME, shift)
        for u in np.flatnonzero(changed.to_numpy()):
            # the changed row used reading j: it must be public by the window open, and never newer than nominal
            assert pd.notna(rel.iloc[j]) and rel.iloc[j] <= opn.iloc[u]
            assert j <= u - lead
        # a perturbation of any FUTURE reading (j > u - lead) never changes row u
        assert not changed.iloc[: j + lead].any()


def test_shutdown_backlog_holds_last_released_reading():
    """Sep and Oct readings both published in mid-January (backlog); Nov released late too."""
    idx = pd.date_range("2025-06-30", "2026-04-30", freq="ME")
    rel = mid_month_release(idx)
    rel[pd.Timestamp("2025-09-30")] = pd.Timestamp("2026-01-09")
    rel[pd.Timestamp("2025-10-31")] = pd.Timestamp("2026-01-09")
    rel[pd.Timestamp("2025-11-30")] = pd.Timestamp("2026-02-18")
    sig = pd.Series(np.arange(len(idx), dtype=float), index=idx)  # value = row number
    out = pa.pit_shift(sig, 2, rel)
    used = dict(zip(idx.strftime("%Y-%m"), out))
    # window opening 2025-10-31 wants Sep (not yet out) -> Aug (row 2)
    assert used["2025-11"] == 2
    # window opening 2025-11-28 wants Oct (not out) -> Sep (not out) -> Aug
    assert used["2025-12"] == 2
    # window opening 2025-12-31 wants Nov (out Feb) -> Oct, Sep (out Jan 9) -> Aug
    assert used["2026-01"] == 2
    # window opening 2026-01-30: Dec released mid-Jan -> nominal Dec (row 6)
    assert used["2026-02"] == 6
    b = pa.breaches(idx, 2, rel)
    assert list(b.return_row.dt.strftime("%Y-%m")) == ["2025-11", "2025-12", "2026-01"]
    assert (b.days_early > 0).all() and list(b.asof_lag) == [3, 4, 5]


def test_release_on_window_open_date_counts_as_available():
    # reading M released exactly on the E2 window-open date: the last trading day of M+1
    rel = pd.Series(pa.last_trading_day(ME), index=ME).shift(-1)
    lags = pa.asof_lags(ME, 2, rel)
    assert (lags.iloc[2:-1] == 2).all()
    rel2 = rel + pd.Timedelta(days=1)  # one day later: falls back one period
    assert (pa.asof_lags(ME, 2, rel2).iloc[3:] == 3).all()


def test_window_open_rolls_back_to_last_trading_day():
    # 2025-08-31 is a Sunday: the window opens at Friday 2025-08-29's close; a reading dated Saturday is not usable
    idx = pd.DatetimeIndex(["2025-07-31", "2025-08-31", "2025-09-30"])
    rel = pd.Series([pd.NaT, pd.Timestamp("2025-08-30"), pd.NaT], index=idx)
    assert pa.window_open(idx).iloc[2] == pd.Timestamp("2025-08-29")
    assert pd.isna(pa.asof_lags(idx, 1, rel).iloc[2])
    rel.iloc[1] = pd.Timestamp("2025-08-29")
    assert pa.asof_lags(idx, 1, rel).iloc[2] == 1


def test_grid_edge_first_rows_and_max_extra():
    rel = mid_month_release(ME)
    lags = pa.asof_lags(ME, 13, rel)
    assert lags.iloc[:13].isna().all() and (lags.iloc[13:] == 13).all()  # top grid lead: no reading before row 13
    # nothing available within max_extra -> NaN, never a newer reading
    late = pd.Series(ME + pd.Timedelta(days=400), index=ME)
    assert pa.asof_lags(ME, 2, late, max_extra=3).isna().all()
    assert pa.pit_shift(pd.Series(1.0, index=ME), 2, late, max_extra=3).isna().all()


def test_position_shift_one_uses_next_window():
    rel = mid_month_release(ME)
    # L1 + pos.shift(1): position at row u trades the window opening at ME(u) -> reading u-1 released mid month u
    assert (pa.asof_lags(ME, 1, rel, position_shift=1).iloc[1:] == 1).all()
    assert pa.breaches(ME, 1, rel, position_shift=1).empty


def test_dataframe_inputs_share_one_reading():
    rel = mid_month_release(ME)
    rel.iloc[10] = rel.iloc[10] + pd.Timedelta(days=60)
    df = pd.DataFrame({"sig": np.arange(24.0), "thr": np.arange(24.0) * 10}, index=ME)
    out = pa.pit_shift(df, 2, rel)
    assert (out.thr.dropna() == out.sig.dropna() * 10).all()


def test_daily_rule_release_next_business_day():
    idx = pd.bdate_range("2024-01-02", periods=30, freq=pa.TRADING_DAY)
    rel = pa.rule_release(idx, 1)
    assert (pa.asof_lags(idx, 1, rel, position_shift=1).iloc[1:] == 1).all()  # E2 is enough
    assert len(pa.breaches(idx, 0, rel, position_shift=1)) == len(idx) - 1  # E1 is a 1-day lookahead
    assert pa.breaches(idx, 1, pa.rule_release(idx, 0)).empty  # market close data: E1 fine


def test_load_release_from_committed_calendar():
    idx = pd.DatetimeIndex(["2018-11-30", "2025-09-30", "2025-10-31", "2026-03-31"])
    rel = pa.load_release("UNRATE", idx)
    assert rel.iloc[0] == pd.Timestamp("2018-12-07")
    assert rel.iloc[1] == pd.Timestamp("2025-11-20") and pd.isna(rel.iloc[2])  # Oct-2025 never released
    q = pa.load_release("DRCCLACBS", pd.DatetimeIndex(["2026-06-30"]))
    assert q.iloc[0] == pd.Timestamp("2026-08-25")
    # readings stamped before the series exists are not breaches (the pipeline has no signal there)
    eci = pd.date_range("2000-03-31", "2002-12-31", freq="QE")
    assert pa.breaches(eci, 2, pa.load_release("ECIALLCIV", eci)).empty
    with pytest.raises(KeyError):
        pa.load_release("NOPE", idx)
