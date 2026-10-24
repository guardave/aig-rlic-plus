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


def test_daily_index_is_its_own_trading_calendar():
    # a pipeline trading day that the NYSE approximation calls a holiday (e.g. a 2025 Columbus Day row is fine,
    # but rows on federal holidays / special closures must not be rolled back to an earlier close)
    idx = pd.DatetimeIndex(["2024-06-18", "2024-06-19", "2024-06-20", "2024-06-21"])  # 06-19 Juneteenth
    assert pa.window_open(idx).iloc[2] == pd.Timestamp("2024-06-19")
    assert pa.breaches(idx, 1, pa.rule_release(idx, 0)).empty
    assert pa.breaches(idx, 1, pa.rule_release(idx, 1), position_shift=1).empty


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


def vint_table(rows):
    """rows: (period_end, realtime_start, realtime_end or None, value)."""
    return pd.DataFrame({"date": [pd.Timestamp(p) - pd.offsets.MonthBegin(1) for p, *_ in rows],
                         "realtime_start": [pd.Timestamp(r) for _, r, _, _ in rows],
                         "realtime_end": [pd.Timestamp(e or "2262-01-01") for _, _, e, _ in rows],
                         "value": [float(x) for *_, x in rows]})


def test_realtime_apply_uses_the_value_known_when_the_window_opens():
    # Jan reading first printed 100 on Feb-15, revised to 130 on Mar-20
    rows = [("2020-01-31", "2020-02-15", "2020-03-19", 100), ("2020-01-31", "2020-03-20", None, 130),
            ("2020-02-29", "2020-03-16", None, 200), ("2020-03-31", "2020-04-15", None, 300),
            ("2020-04-30", "2020-05-15", None, 400)]
    v = vint_table(rows)
    idx = pd.date_range("2020-01-31", "2020-05-31", freq="ME")
    out = pa.realtime_apply(v, idx, 2, lambda s: s.rename("x"))["x"]
    # window opening 2020-02-28 (row 2020-03): Jan known as 100 (first print) -> the revised 130 is not used yet
    assert out.loc["2020-03-31"] == 100
    # window opening 2020-03-31 (row 2020-04): nominal Feb (released Mar-16) -> 200; Jan now 130 in the vintage
    assert out.loc["2020-04-30"] == 200
    assert pa.vintage_asof(v, "2020-03-31").loc["2020-01-31"] == 130
    # latest-vintage values with first-release timing would have used 130 in row 2020-03: the D8 lookahead
    latest = pa.vintage_asof(v, "2026-01-01")
    assert latest.loc["2020-01-31"] == 130


def test_realtime_apply_matches_pit_shift_without_revisions():
    rel = mid_month_release(ME)
    vals = pd.Series(np.arange(len(ME), dtype=float), index=ME)
    v = vint_table([(str(t.date()), str(rel[t].date()), None, vals[t]) for t in ME])
    out = pa.realtime_apply(v, ME, 2, lambda s: s.rename("x"))["x"]
    ref = pa.pit_shift(vals, 2, rel)
    ok = out.notna()
    assert ok.sum() > 15 and (out[ok] == ref[ok]).all()


def test_realtime_apply_rolling_inputs_come_from_one_vintage():
    rows = [(str(t.date()), str((t + pd.Timedelta(days=10)).date()), None, 1.0) for t in ME]
    v = vint_table(rows)
    # a later benchmark revision rewrites the whole history to 2.0 from 2021-06-01: earlier rows must not see it
    v.loc[:, "realtime_end"] = pd.Timestamp("2021-05-31")
    rev = vint_table([(str(t.date()), "2021-06-01", None, 2.0) for t in ME if t < pd.Timestamp("2021-05-01")])
    v = pd.concat([v, rev], ignore_index=True)
    out = pa.realtime_apply(v, ME, 1, lambda s: s.rolling(3).mean().rename("m"))["m"]
    assert (out.loc[:"2021-05-31"].dropna() == 1.0).all()
    assert (out.loc["2021-07-31":].dropna() == 2.0).all()


def test_calendar_after_close_fallback_and_verified_rows():
    cal = pd.read_csv(pa.CALENDAR)
    row = lambda s, r: cal[(cal.series_id == s) & (cal.ref_date == r)].iloc[0]  # noqa: E731
    # Q3: H.8 is released 16:15 ET (Friday) -> usable from the next trading day's close (Monday)
    b = row("BUSLOANS", "2024-01-01")
    assert b.first_release == "2024-02-09" and b.available_date == "2024-02-12"
    assert pa.load_release("BUSLOANS", pd.DatetimeIndex(["2024-01-31"])).iloc[0] == pd.Timestamp("2024-02-12")
    # MED-4: the cement 2023-11 S3 hole is a flagged fallback row, not "never released"
    c = row("USGS_CEMENT_MIS", "2023-11-01")
    assert c.basis.startswith("fallback_data_hole") and isinstance(c.first_release, str)
    # MED-5: UMich released final March 2018 on 2018-03-29 (ALFRED posted it 2018-04-27)
    u = row("UMCSENT", "2018-03-01")
    assert u.basis == "publisher_verified" and u.first_release == "2018-03-29"
    # Q1: default fallback excludes shutdown windows; the harsh column keeps the shutdown-inclusive max
    i = row("IR", "2005-01-01")
    assert i.basis.startswith("fallback_max_lag_excl_shutdown") and i.first_release < i.first_release_harsh
    assert pa.load_release("IR", pd.DatetimeIndex(["2005-01-31"]), harsh=True).iloc[0] == pd.Timestamp(
        i.available_date_harsh)
    # never-published months stay unavailable
    assert pd.isna(row("UNRATE", "2025-10-01").first_release)


def test_realtime_apply_after_close_vintage_not_visible_on_its_posting_date():
    """QA2 M-1: an H.8-style 16:15 ET posting on the window-open date is not usable at that close."""
    idx = pd.DatetimeIndex(["2024-01-31", "2024-02-29", "2024-03-29"])
    # Jan value first posted Thu 2024-02-29 (= the window-open close of row 2024-03-29) at 16:15 ET
    v = vint_table([("2023-12-31", "2024-01-12", None, 1.0), ("2024-01-31", "2024-02-29", None, 2.0)])
    same_day = pa.realtime_apply(v, idx, 1, lambda s: s.rename("x"))["x"]
    after = pa.realtime_apply(v, idx, 1, lambda s: s.rename("x"), after_close=True)["x"]
    assert same_day.loc["2024-03-29"] == 2.0 and after.loc["2024-03-29"] == 1.0
    # a dated rule switches off from its date (M2SL: before-close releases from 2021-02-23)
    assert pa.visible_on("2024-02-29", "2021-02-23") == pd.Timestamp("2024-02-29")
    assert pa.visible_on("2005-02-10", "2021-02-23") == pd.Timestamp("2005-02-09")
    assert pa.after_close_rule("BUSLOANS") is True and pa.after_close_rule("M2SL") == "2021-02-23"
    assert pa.after_close_rule("UNRATE") is False


@pytest.mark.parametrize("year_end", ["2004-12-31", "2010-12-31", "2021-12-31"])
def test_nyse_saturday_new_year_not_observed_on_friday(year_end):
    """NYSE (unlike the federal calendar) trades on Friday 31 Dec when 1 Jan falls on a Saturday."""
    d = pd.Timestamp(year_end)
    assert pa.TRADING_DAY.is_on_offset(d)
    assert pa.last_trading_day(pd.DatetimeIndex([d]))[0] == d


@pytest.mark.parametrize("closure", pa._NYSE_SPECIAL_CLOSURES)
def test_nyse_special_closures_are_non_trading_days(closure):
    assert not pa.TRADING_DAY.is_on_offset(pd.Timestamp(closure))


def test_nyse_special_closures_count():
    assert len(pa._NYSE_SPECIAL_CLOSURES) == 12


def test_nyse_calendar_closures_and_open_days():
    closed = ["2022-01-17", "2021-04-02", "2022-06-20", "2021-12-24", "2012-10-29", "2001-09-11", "2025-01-09",
              "2017-01-02"]
    opened = ["2021-06-18", "2021-10-11", "2021-11-11", "1997-01-20"]
    assert not any(pa.TRADING_DAY.is_on_offset(pd.Timestamp(x)) for x in closed)
    assert all(pa.TRADING_DAY.is_on_offset(pd.Timestamp(x)) for x in opened)
