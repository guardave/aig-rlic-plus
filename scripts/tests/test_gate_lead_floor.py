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
    return g.run(tmp, [pair])[0]["status"]


def test_l0_below_floor_fails(tmp_path):
    r = make_repo(tmp_path, "x_spy", "leads = [0, 1, 2, 3]\n", {"x_spy": REC})
    assert status(r) == "FAIL"


def test_inconsistent_duplicate_grids_fail(tmp_path):
    src = "lead_times = list(range(1, 14))\nmeta = {'leads': list(range(0, 13))}\n"
    r = make_repo(tmp_path, "x_spy", src, {"x_spy": {"lead_floor": 0}})
    res = g.run(r, ["x_spy"])[0]
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
    r = g.run(tmp, [pair])[0]
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
    assert g.main(["--repo", str(r), "x_spy"]) == 0
    assert g.main(["--repo", str(r), "--strict", "x_spy"]) == 1


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
    res = g.run(make_repo(tmp_path, "x_spy", src, {"x_spy": rec}, winner_lead=1), ["x_spy"])[0]
    assert res["status"] == "PASS" and res["floor_effective"] == 2
