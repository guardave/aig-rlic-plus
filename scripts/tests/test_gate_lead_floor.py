"""Synthetic-fixture tests for scripts/gate_lead_floor.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gate_lead_floor as g  # noqa: E402


def make_repo(tmp, pair, pipeline_src, registry_pairs, winner_lead=1, extra=None):
    (tmp / "app" / "pages").mkdir(parents=True)
    (tmp / "app" / "pages" / f"1_{pair}_story.py").write_text("")
    (tmp / "scripts").mkdir()
    (tmp / "scripts" / f"pair_pipeline_{pair}.py").write_text(pipeline_src)
    for name, src in (extra or {}).items():
        (tmp / "scripts" / name).write_text(src)
    (tmp / "docs" / "schemas").mkdir(parents=True)
    (tmp / "docs" / "schemas" / "lead_axis_registry.json").write_text(json.dumps({"pairs": registry_pairs}))
    (tmp / "results" / pair).mkdir(parents=True)
    (tmp / "results" / pair / "winner_summary.json").write_text(json.dumps({"lead_value": winner_lead}))
    return tmp


REC = {"lead_floor": 1, "lead_grid": list(range(1, 14))}


def status(tmp, pair="x_spy"):
    return g.run(tmp, [pair], mode="floor")[0]["status"]


def test_l0_below_floor_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = [0, 1, 2, 3]\n", {"x_spy": REC})
    assert status(r) == "FAIL"


def test_inconsistent_duplicate_grids_fail(tmp_path):
    src = "lead_times = list(range(1, 14))\nmeta = {'leads': list(range(0, 13))}\n"
    r = make_repo(tmp_path, "x_spy", src, {"x_spy": {"lead_floor": 0}})
    res = g.run(r, ["x_spy"], mode="floor")[0]
    assert res["status"] == "FAIL" and "inconsistent" in " ".join(res["reasons"])


def test_floored_grid_passes(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(1, 14))\nd = {'leads': leads}\nret = pos * r\n", {"x_spy": REC})
    assert status(r) == "PASS"


def test_unregistered_live_pair_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(1, 14))\n", {})
    assert status(r) == "FAIL"


def test_winner_below_floor_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(1, 14))\n", {"x_spy": REC}, winner_lead=0)
    assert status(r) == "FAIL"


OK = "leads = list(range(1, 14))\nret = pos * r\n"


def reasons(tmp, pair="x_spy"):
    r = g.run(tmp, [pair], mode="floor")[0]
    return r["status"], " ".join(r["reasons"])


def test_econ_pipeline_file_scanned(tmp_path):
    r = make_repo(tmp_path, "x_spy", OK, {"x_spy": REC}, extra={"econ_pipeline_x_spy.py": "leads = [0, 1, 2]\n"})
    st, why = reasons(r)
    assert st == "FAIL" and "econ_pipeline_x_spy.py" in why


def test_refresh_daily_leads_scanned(tmp_path):
    r = make_repo(tmp_path, "x_spy", OK, {"x_spy": REC},
                  extra={"refresh_x_spy_lead_artifacts.py": "DAILY_LEADS = [0, 1, 5]\n"})
    st, why = reasons(r)
    assert st == "FAIL" and "refresh_x_spy_lead_artifacts.py" in why


def test_for_lead_loop_with_shift_scanned(tmp_path):
    src = "for lead in [0, 1, 5]:\n    pos = s.shift(lead)\n"
    r = make_repo(tmp_path, "x_spy", OK, {"x_spy": REC}, extra={"econ_pipeline_x_spy.py": src})
    assert status(r) == "FAIL"


def test_diagnostic_loop_ignored(tmp_path):
    src = "for L in range(0, 13):\n    c = s.shift(L).corr(r)\n"
    r = make_repo(tmp_path, "x_spy", OK, {"x_spy": REC}, extra={"econ_pipeline_x_spy.py": src})
    assert status(r) == "PASS"


def test_no_grid_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "x = 1\n", {"x_spy": REC})
    st, why = reasons(r)
    assert st == "FAIL" and "no lead-grid" in why


def test_unparseable_grid_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = make_grid(cfg)\n", {"x_spy": REC})
    st, why = reasons(r)
    assert st == "FAIL" and "unparseable" in why


def test_position_shift_mismatch_fails(tmp_path):
    src = "leads = list(range(1, 14))\nret = pos.shift(1) * spy_ret\n"
    r = make_repo(tmp_path, "x_spy", src, {"x_spy": REC})  # registry shift defaults 0
    st, why = reasons(r)
    assert st == "FAIL" and "alignment mismatch" in why


def test_position_shift_declared_passes(tmp_path):
    src = "leads = list(range(1, 14))\nret = pos.shift(1) * spy_ret\n"
    r = make_repo(tmp_path, "x_spy", src, {"x_spy": dict(REC, position_shift=1)})
    assert status(r) == "PASS"


def test_l0_with_shift_and_floor_effective_passes(tmp_path):
    src = "leads = [0, 1, 5]\nret = pos.shift(1) * spy_ret\n"
    rec = {"lead_floor": 0, "lead_floor_effective": 1, "lead_grid": [0, 1, 5], "position_shift": 1}
    r = make_repo(tmp_path, "x_spy", src, {"x_spy": rec}, winner_lead=0)
    assert status(r) == "PASS"


def test_l0_without_shift_fails_even_if_floor_zero(tmp_path):
    src = "leads = [0, 1, 5]\nret = pos * spy_ret\n"
    r = make_repo(tmp_path, "x_spy", src, {"x_spy": {"lead_floor": 0, "lead_grid": [0, 1, 5]}}, winner_lead=0)
    st, why = reasons(r)
    assert st == "FAIL" and "contemporaneous" in why


def test_double_shift_effective_lag(tmp_path):
    src = "leads = [1, 2]\nsig = raw.shift(lead)\nret = pos.shift(1) * r\n"
    rec = {"lead_floor": 1, "lead_floor_effective": 2, "lead_grid": [1, 2], "position_shift": 1}
    r = make_repo(tmp_path, "x_spy", src, {"x_spy": rec})
    assert status(r) == "PASS"


def test_registry_shift_cannot_launder_unshifted_l0(tmp_path):
    src = "leads = [0, 1, 5]\nstrat = w * z\n"  # no detectable shift
    rec = {"lead_floor": 0, "lead_grid": [0, 1, 5], "position_shift": 1}
    r = make_repo(tmp_path, "x_spy", src, {"x_spy": rec}, winner_lead=1)
    st, why = reasons(r)
    assert st == "FAIL" and "not confirmed" in why


def test_shift_periods_keyword_detected(tmp_path):
    src = "leads = list(range(1, 14))\nret = pos.shift(periods=1) * spy_ret\n"
    assert status(make_repo(tmp_path, "x_spy", src, {"x_spy": dict(REC, position_shift=1)})) == "PASS"
    assert g.detect_position_shift("r = w.shift(1, fill_value=0) * spy_ret\n")[0] == 1


def test_reversed_order_other_names(tmp_path):
    assert g.detect_position_shift("out = spy_ret * weights.shift(1)\n")[0] == 1
    assert g.detect_position_shift("sig = base.shift(lead)\nout = sig * spy_ret\n")[0] == 0
    src = "leads = [0, 1]\nout = spy_ret * weights.shift(1)\n"
    rec = {"lead_floor": 0, "lead_grid": [0, 1], "position_shift": 1}
    assert status(make_repo(tmp_path, "x_spy", src, {"x_spy": rec}, winner_lead=0)) == "PASS"


def test_strict_turns_warn_into_nonzero(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(1, 14))\nx = 1\n", {"x_spy": REC})  # no pos*ret => WARN
    assert status(r) == "WARN"
    assert g.main(["--repo", str(r), "--mode", "floor", "x_spy"]) == 0
    assert g.main(["--repo", str(r), "--mode", "floor", "--strict", "x_spy"]) == 1


def test_lags_name_fails_safe(tmp_path):
    r = make_repo(tmp_path, "x_spy", "LAGS = [0, 1, 2]\nret = pos * r\n", {"x_spy": REC})
    assert status(r) == "FAIL"


def test_helper_module_grid_fails_safe(tmp_path):
    assert status(make_repo(tmp_path, "x_spy", "from helpers import LEADS\nret = pos * r\n", {"x_spy": REC})) == "FAIL"
    assert status(make_repo(tmp_path / "b", "x_spy", "import helpers\nleads = helpers.LEADS\n", {"x_spy": REC})) == "FAIL"


def test_chained_calls_after_shift_detected():
    assert g.detect_position_shift("o = pos.shift(1).fillna(0) * ret\n")[0] == 1
    assert g.detect_position_shift("o = ret * w.shift(1).fillna(0).astype(float)\n")[0] == 1
    assert g.detect_position_shift("p = x.shift(1).reindex(i).clip(0, 1)\nq = p * spy_ret\no = a.shift(1).dropna() * spy_ret\n")[0] == 1
    assert g.detect_position_shift("return pos, pos.shift(1).fillna(0) * ret\n")[0] == 1
    assert g.detect_position_shift("sig = b.shift(lead)\no = sig.fillna(0) * ret\n")[0] == 0


def test_scaling_pos_by_constant_is_not_a_return_use():
    assert g.detect_position_shift("pos = pos * 2 - 1\no = pos.shift(1).fillna(0) * ret\n")[0] == 1


# --- strict floor on the effective lag (standard Step 2, amended 2026-10-16) -----------------------

# Mid-month release (e.g. retail sales ~16 d after month-end): the reading for M is public in M+1, so the
# first return window it may drive opens at end(M+1): strict floor E2.
MID_MONTH = {"lead_floor": 2, "position_shift": 0, "lead_floor_effective": 2, "lead_grid": list(range(2, 14))}


def test_mid_month_release_l1_grid_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(1, 14))\nret = pos * spy_ret\n", {"x_spy": MID_MONTH}, winner_lead=3)
    st, why = reasons(r)
    assert st == "FAIL" and "sub-floor leads [1]" in why and "E2" in why


def test_mid_month_release_truncated_grid_passes(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(2, 14))\nret = pos * spy_ret\n", {"x_spy": MID_MONTH}, winner_lead=3)
    assert status(r) == "PASS"


def test_mid_month_release_winner_at_l1_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(2, 14))\nret = pos * spy_ret\n", {"x_spy": MID_MONTH}, winner_lead=1)
    st, why = reasons(r)
    assert st == "FAIL" and "effective lag 1 < strict floor E2" in why


def test_mid_month_release_met_by_position_shift(tmp_path):
    # L1 + pos.shift(1) = effective lag 2: the same strict floor is met through the shift.
    rec = {"lead_floor": 1, "position_shift": 1, "lead_floor_effective": 2, "lead_grid": list(range(1, 14))}
    src = "leads = list(range(1, 14))\nret = pos.shift(1) * spy_ret\n"
    assert status(make_repo(tmp_path, "x_spy", src, {"x_spy": rec}, winner_lead=1)) == "PASS"


# Quarterly series released ~7 weeks after quarter-end (credit-card delinquency, ~51 d): the window that
# opens at the quarter-end of Q is ~51 d before publication, so the strict floor is E2 (quarters).
QUARTERLY_7WK = {"lead_floor": 2, "position_shift": 0, "lead_floor_effective": 2, "lead_grid": [2, 3, 4, 5]}


def test_quarterly_seven_week_lag_l1_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(1, 6))\nret = pos * spy_ret\n", {"x_spy": QUARTERLY_7WK}, winner_lead=2)
    st, why = reasons(r)
    assert st == "FAIL" and "sub-floor leads [1]" in why


def test_quarterly_seven_week_lag_floored_passes(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = list(range(2, 6))\nret = pos * spy_ret\n", {"x_spy": QUARTERLY_7WK}, winner_lead=2)
    assert status(r) == "PASS"


def test_every_grid_lead_checked_not_only_declared_min(tmp_path):
    # a grid that lists a sub-floor lead out of order is still caught
    r = make_repo(tmp_path, "x_spy", "leads = [3, 2, 1]\nret = pos * spy_ret\n",
                  {"x_spy": dict(MID_MONTH, lead_grid=[3, 2, 1])}, winner_lead=3)
    st, why = reasons(r)
    assert st == "FAIL" and "sub-floor leads [1]" in why


def test_registry_inconsistent_floor_fields_fail(tmp_path):
    rec = {"lead_floor": 1, "position_shift": 0, "lead_floor_effective": 2, "lead_grid": list(range(2, 14))}
    r = make_repo(tmp_path, "x_spy", "leads = list(range(2, 14))\nret = pos * spy_ret\n", {"x_spy": rec}, winner_lead=3)
    st, why = reasons(r)
    assert st == "FAIL" and "registry inconsistent" in why


def test_registry_grid_below_floor_fails(tmp_path):
    rec = {"lead_floor": 2, "position_shift": 0, "lead_floor_effective": 2, "lead_grid": list(range(1, 14))}
    r = make_repo(tmp_path, "x_spy", "leads = list(range(1, 14))\nret = pos * spy_ret\n", {"x_spy": rec}, winner_lead=3)
    st, why = reasons(r)
    assert st == "FAIL" and "registry lead_grid has sub-floor leads [1]" in why


def test_effective_floor_defaults_to_floor_plus_shift(tmp_path):
    rec = {"lead_floor": 1, "position_shift": 1, "lead_grid": list(range(1, 14))}  # => E2
    src = "leads = list(range(1, 14))\nret = pos.shift(1) * spy_ret\n"
    res = g.run(make_repo(tmp_path, "x_spy", src, {"x_spy": rec}, winner_lead=1), ["x_spy"], mode="floor")[0]
    assert res["status"] == "PASS" and res["floor_effective"] == 2


# ---- --mode per-period (pkg12 point-in-time rule) ----
import pandas as pd  # noqa: E402


def pp_repo(tmp, src, rec, winner_lead=2, delayed=None, sample=("2018-01-31", "2020-12-31"), returns=True,
            freq="ME"):
    """Synthetic repo with a release calendar for series XS: reading M released on the 15th of M+1; `delayed`
    maps a reference month 'YYYY-MM' to a later release date (shutdown backlog)."""
    rec = {"lead_axis": "months", "release_calendar_series": "XS", "alignment": "fixed_lag", **rec}
    r = make_repo(tmp, "x_spy", src, {"x_spy": rec}, winner_lead=winner_lead)
    months = pd.date_range("2015-01-01", "2021-06-01", freq="MS")
    rows = []
    for m in months:
        rel = (m + pd.offsets.MonthBegin(1)).replace(day=15)
        if delayed and m.strftime("%Y-%m") in delayed:
            rel = pd.Timestamp(delayed[m.strftime("%Y-%m")])
        rows.append(("XS", m.date(), (m + pd.offsets.MonthEnd(0)).date(), rel.date(), 0, "alfred_first_vintage"))
    (r / "data" / "release_calendar").mkdir(parents=True)
    pd.DataFrame(rows, columns=["series_id", "ref_date", "period_end", "first_release", "lag_days", "basis"]).to_csv(
        r / "data" / "release_calendar" / "release_calendar.csv", index=False)
    if returns:
        idx = pd.date_range(*sample, freq=freq)
        pd.DataFrame({"date": idx, "position": 1.0}).to_csv(r / "results" / "x_spy" / "strategy_returns_20261016.csv",
                                                            index=False)
    return r


PP_OK = "leads = list(range(2, 14))\nret = pos * r\n"
PP_REC = {"lead_floor": 2, "lead_floor_effective": 2, "lead_grid": list(range(2, 14))}


def pp(r, mode="per-period"):
    res = g.run(r, ["x_spy"], mode=mode)[0]
    return res["status"], " ".join(res["reasons"]), res


def test_per_period_passes_when_every_reading_released(tmp_path):
    st, why, res = pp(pp_repo(tmp_path, PP_OK, PP_REC))
    assert st == "PASS" and "0 breaching periods" in why
    assert res["per_period"]["by_lead"][2]["n"] == 0


def test_per_period_fails_on_shutdown_backlog_that_p90_floor_passes(tmp_path):
    # 2019-09 reading released 2020-01-09: L2, L3 and L4 use it in the windows opening 2019-10-31, 2019-11-29 and
    # 2019-12-31, before release; L5 (window opens 2020-01-31) is clean. The fixed E2 floor (p90 rule) still PASSes
    r = pp_repo(tmp_path, PP_OK, PP_REC, delayed={"2019-09": "2020-01-09"})
    st, why, res = pp(r)
    assert st == "FAIL" and "L2 + shift 0" in why and "2019-11-30" in why
    assert res["per_period"]["by_lead"][3]["return_rows"] == ["2019-12-31"]
    assert res["per_period"]["by_lead"][4]["return_rows"] == ["2020-01-31"]
    assert res["per_period"]["by_lead"][5]["n"] == 0
    assert pp(r, mode="floor")[0] == "PASS"


def test_per_period_winner_breach_is_labelled(tmp_path):
    r = pp_repo(tmp_path, PP_OK, PP_REC, winner_lead=2, delayed={"2019-09": "2020-01-09"})
    assert "winner L2" in pp(r)[1]


def test_per_period_counts_only_backtest_sample(tmp_path):
    r = pp_repo(tmp_path, PP_OK, PP_REC, delayed={"2016-03": "2016-08-01"})  # before the sample starts
    assert pp(r)[0] == "PASS"


def test_per_period_uses_position_shift(tmp_path):
    src = "leads = list(range(1, 14))\nret = pos.shift(1) * r\n"
    rec = {"lead_floor": 1, "position_shift": 1, "lead_floor_effective": 2, "lead_grid": list(range(1, 14))}
    assert pp(pp_repo(tmp_path, src, rec))[0] == "PASS"  # L1 + shift 1 = E2, mid-month release


def test_per_period_never_released_reading_fails(tmp_path):
    r = pp_repo(tmp_path, PP_OK, PP_REC)
    p = r / "data" / "release_calendar" / "release_calendar.csv"
    cal = pd.read_csv(p)
    cal.loc[cal.ref_date == "2019-10-01", "first_release"] = None
    cal.to_csv(p, index=False)
    st, why, _ = pp(r)
    assert st == "FAIL" and "never released" in why


def test_per_period_pit_asof_alignment_passes_only_with_helper_call(tmp_path):
    rec = {**PP_REC, "alignment": "pit_asof"}
    src = PP_OK + "sig = pit_shift(df[['s', 't']], lead, rel)\n"
    r = pp_repo(tmp_path / "a", src, rec, delayed={"2019-09": "2020-01-09"})
    st, why, _ = pp(r)
    assert st == "PASS" and "as-of aligned" in why
    r2 = pp_repo(tmp_path / "b", PP_OK, rec, delayed={"2019-09": "2020-01-09"})
    st, why, _ = pp(r2)
    assert st == "FAIL" and "no pit_shift( call" in why


def test_per_period_missing_calendar_series_fails(tmp_path):
    r = pp_repo(tmp_path, PP_OK, {**PP_REC, "release_calendar_series": None})
    st, why, _ = pp(r)
    assert st == "FAIL" and "release_calendar_series" in why
    r2 = pp_repo(tmp_path / "u", PP_OK, {**PP_REC, "release_calendar_series": "NOPE"})
    assert "release calendar unavailable" in pp(r2)[1]


def test_per_period_unknown_sample_warns(tmp_path):
    st, why, _ = pp(pp_repo(tmp_path, PP_OK, PP_REC, returns=False))
    assert st == "WARN" and "sample unknown" in why


def test_per_period_daily_rules(tmp_path):
    day = {"lead_axis": "trading_days", "lead_floor": 1, "position_shift": 1, "lead_floor_effective": 2,
           "lead_grid": [1, 5, 21], "release_calendar_series": "rule:next_business_day"}
    src = "leads = [1, 5, 21]\nret = pos.shift(1) * r\n"
    r = pp_repo(tmp_path / "a", src, day, winner_lead=1, freq="B")
    assert pp(r)[0] == "PASS"
    src0 = "leads = [0, 5, 21]\nret = pos.shift(1) * r\n"
    r0 = pp_repo(tmp_path / "b", src0, {**day, "lead_floor": 0, "lead_floor_effective": 1, "lead_grid": [0, 5, 21]},
                 winner_lead=5, freq="B")
    st, why, _ = pp(r0)
    assert st == "FAIL" and "L0 + shift 1" in why  # next-day posting: E1 is a one-day lookahead
    mc = pp_repo(tmp_path / "c", src0, {**day, "lead_floor": 0, "lead_floor_effective": 1, "lead_grid": [0, 5, 21],
                                        "release_calendar_series": "rule:market_close"}, winner_lead=5, freq="B")
    assert pp(mc)[0] == "PASS"


def test_cli_mode_flag(tmp_path):
    r = pp_repo(tmp_path, PP_OK, PP_REC, delayed={"2019-09": "2020-01-09"})
    assert g.main(["--repo", str(r), "x_spy"]) == 1
    assert g.main(["--repo", str(r), "--mode", "floor", "x_spy"]) == 0
