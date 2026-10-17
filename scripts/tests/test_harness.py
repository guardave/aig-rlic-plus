"""Unit tests for the Phase B harness (scripts/harness/)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _pit_align as pa  # noqa: E402
from harness import align, inference, leak, null, selection  # noqa: E402
from harness.candidates import P2_THRESHOLD, distinct_series, manifest, reading_frame  # noqa: E402
from harness.data import legacy_inputs, realtime_inputs, revised_inputs  # noqa: E402
from harness.engine import TrackInputs, run_tournament  # noqa: E402
from harness.spec import ISQuantile, Legacy, PairSpec, Rule  # noqa: E402

ME = pd.date_range("1990-01-31", periods=240, freq="ME")


def _feats(lv):
    x = lv["x"]
    return pd.DataFrame({"lvl": x, "chg": x.diff(3), "flag": (x > x.rolling(12, min_periods=6).mean()).astype(float)
                         .where(x.rolling(12, min_periods=6).mean().notna())}, index=lv.index)


def _rules(s):
    if s == "flag":
        return {"T_half": Rule("raw", None, 0.5)}
    return {"T0": Rule("raw", None, 0.0), "T_roll": Rule("raw", None, lambda v: v.rolling(24, min_periods=12).median()),
            "T_isq": Rule("raw", None, ISQuantile(0.6))}


def make_spec(**kw):
    base = dict(pair_id="toy", freq="M", lead_unit="months", leads=[1, 2, 3, 4, 5], oos_start="2008-01-31",
                min_is_n=36, position_shift=0, track_policy="compute_twice", release_series=None,
                level_columns=["x"], features=_feats, signals={"lvl": "lvl", "chg": "chg", "flag": "flag"},
                rules=_rules, strategies=("P1", "P2", "P3"), p2_window=(24, 12), binary_signals=frozenset({"flag"}))
    base.update(kw)
    return PairSpec(**base)


def toy_data(seed=0, n=240):
    rng = np.random.default_rng(seed)
    x = pd.Series(np.cumsum(rng.normal(size=n)), index=ME[:n], name="x")
    ret = rng.normal(0.006, 0.04, n)
    ret[0] = np.nan
    return x.to_frame(), ret


def mid_month_release(index, day=15):
    return pd.Series([(t + pd.offsets.MonthBegin(1)).replace(day=day) for t in index], index=index)


# ------------------------------------------------------------------------------------------- manifest / positions
def test_manifest_excludes_p2_p3_on_binary_and_dedupes_p2():
    spec = make_spec()
    cands = manifest(spec)
    assert not [c for c in cands if c.signal == "flag" and c.strategy != "P1"]
    p2 = [c for c in cands if c.strategy == "P2"]
    assert {c.threshold for c in p2} == {P2_THRESHOLD}
    assert len(p2) == 2 * len(spec.directions) * len(spec.leads)          # one per signal/direction/lead
    legacy = manifest(make_spec(legacy=Legacy(p2_per_threshold=True)), legacy=True)
    assert len([c for c in legacy if c.strategy == "P2"]) == 3 * len(p2)   # repeated per threshold


def test_distinct_series_collapses_identical_positions():
    P = np.array([[1, 1, 0, np.nan], [0, 0, 1, np.nan], [np.nan, np.nan, 1, 1.0]])   # rows x 4 candidates
    n, collapse = distinct_series(P, np.array([True, True, True, False]))
    assert n == 2 and collapse == {0: [1]}


def test_undefined_positions_are_nan_and_deployable_scoring_holds_cash():
    spec = make_spec()
    lv, ret = toy_data()
    ti = legacy_inputs(spec, lv, ret)
    res = run_tournament(spec, ti)
    assert np.isnan(res.positions[0]).all()                # lead >= 1: the first row has no reading
    j = 0
    dep = res.deployable_returns(j)
    assert np.all(dep[np.isnan(res.returns[:, j])] == 0)


# ------------------------------------------------------------------------------------------- alignment
def test_lag_asof_equals_pit_shift_and_realtime_matches_realtime_apply():
    spec = make_spec(leads=[1, 2, 3], release_series=None)
    lv, ret = toy_data()
    frame = reading_frame(spec, lv)
    rel = mid_month_release(lv.index)
    for L in (1, 2, 3):
        pd.testing.assert_frame_equal(align.lag_asof(frame, L, rel, 0), pa.pit_shift(frame, L, rel, 0))
    # vintages: each month's value released mid next month, revised once three months later (+0.5)
    rows = []
    for i, t in enumerate(lv.index):
        r0 = rel.iloc[i]
        r1 = r0 + pd.DateOffset(months=3)
        rows.append({"date": t.replace(day=1), "realtime_start": r0, "realtime_end": r1 - pd.Timedelta(days=1),
                     "value": float(lv.x.iloc[i])})
        rows.append({"date": t.replace(day=1), "realtime_start": r1, "realtime_end": pd.Timestamp("2262-01-01"),
                     "value": float(lv.x.iloc[i]) + 0.5})
    vint = pd.DataFrame(rows)
    idx = lv.index[100:160]
    frames = align.realtime_frames(vint, idx, [2], lambda v: reading_frame(spec, v.rename("x").to_frame()), 0, "M")
    ref = pa.realtime_apply(vint, idx, 2, lambda v: reading_frame(spec, v.rename("x").to_frame()), 0, "M")
    got = frames[2].iloc[2:]
    pd.testing.assert_frame_equal(got, ref.iloc[2:].astype(float)[got.columns], check_names=False)
    assert frames[2].iloc[:2].notna().any(axis=None)        # rows u < lead read pre-index vintage periods


def test_realtime_never_uses_a_vintage_published_after_the_window_opens():
    spec = make_spec(leads=[1])
    lv, _ = toy_data()
    rel = mid_month_release(lv.index)
    vint = pd.DataFrame({"date": [t.replace(day=1) for t in lv.index], "realtime_start": rel.values,
                         "realtime_end": pd.Timestamp("2262-01-01"), "value": lv.x.values})
    idx = lv.index[60:120]
    base = align.realtime_frames(vint, idx, [1], lambda v: reading_frame(spec, v.rename("x").to_frame()))[1]
    cut = idx[30]
    pert = vint.copy()
    pert.loc[pert.realtime_start > cut, "value"] += 100
    new = align.realtime_frames(pert, idx, [1], lambda v: reading_frame(spec, v.rename("x").to_frame()))[1]
    a, b = base.loc[:cut], new.loc[:cut]
    assert ((a - b).abs().fillna(0) < 1e-12).all(axis=None)


# ------------------------------------------------------------------------------------------- selection (D9)
def _table(curves: dict, valid=None):
    rows = []
    for fam, sh in curves.items():
        for i, s in enumerate(sh):
            rows.append({"signal": fam, "threshold": "T", "strategy": "P1", "direction": "countercyclical",
                         "lead": [1, 5, 21, 63, 126, 252][i] if len(sh) == 6 else i + 1, "is_sharpe": s,
                         "valid": True if valid is None else valid.get((fam, i), True), "is_eligible": True,
                         "is_ann_return": 0.0, "is_max_drawdown": 0.0, "is_n_trades": 10})
    return pd.DataFrame(rows)


def test_windows_clamped_no_wrap():
    assert selection.windows(6) == [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
    assert selection.windows(2) == [(0, 1)] and selection.windows(1) == [(0,)]
    assert selection.own_window(0, 6) == (0, 1, 2) and selection.own_window(5, 6) == (3, 4, 5)


def test_plateau_beats_isolated_peak_and_winner_is_raw_max_inside():
    # hy_ig-like: isolated top-edge peak 0.96 vs a plateau 0.80/0.85/0.82
    t = _table({"spike": [0.61, 0.57, 0.79, 0.52, 0.43, 0.96], "flat": [0.30, 0.80, 0.85, 0.82, 0.20, 0.10]})
    sel = selection.plateau_select(t)
    assert sel["family"]["signal"] == "flat" and sel["window_leads"] == [5, 21, 63]
    assert t.loc[sel["winner"], "lead"] == 21 and abs(sel["score"] - 0.80) < 1e-12
    raw = selection.raw_argmax(t, "cascade")
    assert t.loc[raw, "signal"] == "spike" and t.loc[raw, "lead"] == 252
    assert t.loc[t["signal"] == "spike"].query("lead == 252")["plateau_j"].iloc[0] == pytest.approx(0.43)


def test_window_ties_go_to_higher_raw_is_and_invalid_neighbours_count():
    t = _table({"a": [0.5, 0.5, 0.9, 0.1], "b": [0.5, 0.7, 0.5, 0.1]})
    sel = selection.plateau_select(t)
    assert sel["family"]["signal"] == "a" and t.loc[sel["winner"], "lead"] == 3
    # an invalid neighbour still enters the minimum; the invalid lead cannot win
    t2 = _table({"a": [0.9, 0.1, 0.9], "b": [0.5, 0.5, 0.5]}, valid={("a", 1): False})
    sel2 = selection.plateau_select(t2)
    assert sel2["family"]["signal"] == "b"          # a's window minimum is 0.1 (invalid neighbour counted)
    t3 = _table({"a": [0.9, 0.95, 0.2]}, valid={("a", 1): False})
    sel3 = selection.plateau_select(t3)
    assert t3.loc[sel3["winner"], "lead"] == 1


def test_common_is_start_eligibility_before_alignment():
    first = np.array([10, 12, 200])
    own = np.array([90, 88, 5])
    row, elig = selection.common_is_start(first, own, 60, "own_is_n")
    assert row == 12 and list(elig) == [True, True, False]
    row2, _ = selection.common_is_start(first, own, 60, "none")
    assert row2 == 200


def test_selection_never_consults_oos_returns():
    spec = make_spec()
    lv, ret = toy_data(3)
    ti = legacy_inputs(spec, lv, ret)
    a = run_tournament(spec, ti)
    r2 = ret.copy()
    oos = ti.index >= pd.Timestamp(spec.oos_start)
    r2[oos] = np.random.default_rng(9).permutation(r2[oos])
    b = run_tournament(spec, TrackInputs("legacy", ti.index, r2, ti.lagged))
    r3 = ret.copy()
    r3[oos] = 0.0
    c = run_tournament(spec, TrackInputs("legacy", ti.index, r3, ti.lagged))
    ka = a.table.loc[a.selection["winner"], "key"]
    assert ka == b.table.loc[b.selection["winner"], "key"] == c.table.loc[c.selection["winner"], "key"]


# ------------------------------------------------------------------------------------------- null / inference
def test_null_offsets_reproducible_and_bounded():
    o1 = null.offsets(400, 12, 50)
    assert o1 == null.offsets(400, 12, 50)
    m = max(36, 80)
    assert min(o1) >= m and max(o1) <= 400 - m
    with pytest.raises(ValueError):
        null.offsets(60, 12, 5)


def test_roll_span_only_moves_the_span():
    s = pd.Series(np.arange(10.0))
    r = null.roll_span(s, 2, 3, 8)
    assert list(r) == [0, 1, 2, 6, 7, 3, 4, 5, 8, 9]


def test_run_null_reproducible():
    spec = make_spec(leads=[1, 2, 3])
    lv, ret = toy_data(5)
    s, e = null.data_span(lv)
    make = lambda k: legacy_inputs(spec, null.roll_span(lv, k, s, e), ret)  # noqa: E731
    a = null.run_null(spec, make, e - s, K=4)
    b = null.run_null(spec, make, e - s, K=4)
    pd.testing.assert_frame_equal(a, b)
    summ = null.summarize(a, {"is_max": 0.5, "selection_stat": 0.4, "winner_oos": 0.3}, 3)
    assert summ["n_draws"] == 4 and 0 <= summ["edge_share_bound"] <= 1.5


def test_bootstrap_deterministic_shape_and_nw_lag():
    rng = np.random.default_rng(1)
    s, b = rng.normal(0.01, 0.04, 120), rng.normal(0.008, 0.045, 120)
    r1 = inference.paired_block_bootstrap_sharpe_diff(s, b, 6, 12, draws=500)
    r2 = inference.paired_block_bootstrap_sharpe_diff(s, b, 6, 12, draws=500)
    assert r1 == r2 and r1["ci_95"][0] <= r1["mean"] <= r1["ci_95"][1] and r1["draws"] == 500
    assert inference.nw_lag(100) == 4 and inference.nw_lag(1000) == int(np.floor(4 * 10 ** (2 / 9)))


# ------------------------------------------------------------------------------------------- leak tests
def test_leak_tests_pass_on_causal_features_and_fail_on_future_reading():
    spec = make_spec(leads=[1, 2], release_series="rule:same_close")
    lv, ret = toy_data(2)
    full = revised_inputs(spec, lv, lv.index, ret)
    res = run_tournament(spec, full)
    cand = res.cands[int(res.selection["winner"])]

    def trunc(c):
        idx = lv.index[lv.index <= c]
        return revised_inputs(spec, lv.loc[:c], idx, ret[: len(idx)])

    def pert(c):
        return revised_inputs(spec, leak.perturb_levels(lv, c), lv.index, ret)
    rep = leak.run_leak_tests(spec, cand, full, trunc, pert)
    assert rep["pass"], rep

    def bad_feats(v):
        f = _feats(v)
        f["lvl"] = v["x"].shift(-3)                     # reads three periods ahead: a lookahead
        return f
    bad = make_spec(leads=[1, 2], release_series="rule:same_close", features=bad_feats)
    bfull = revised_inputs(bad, lv, lv.index, ret)
    from harness.candidates import Candidate
    c = Candidate("lvl", "T0", "P1", "countercyclical", 1)
    rep2 = leak.run_leak_tests(bad, c, bfull,
                               lambda k: revised_inputs(bad, lv.loc[:k], lv.index[lv.index <= k], ret[: int((lv.index <= k).sum())]),
                               lambda k: revised_inputs(bad, leak.perturb_levels(lv, k), lv.index, ret))
    assert not rep2["pass"]


def test_realtime_inputs_ineligible_when_history_short():
    spec = make_spec(leads=[1, 2], min_is_n=60, vintage_series="TOY")
    lv, ret = toy_data(4)
    rel = mid_month_release(lv.index)
    late = rel >= pd.Timestamp("2005-01-01")          # archive starts 2005: < 60 IS months before 2008
    vint = pd.DataFrame({"date": [t.replace(day=1) for t in lv.index[late]], "realtime_start": rel[late].values,
                         "realtime_end": pd.Timestamp("2262-01-01"), "value": lv.x[late].values})
    from unittest import mock
    with mock.patch.object(align, "after_close_rule", return_value=False):
        ti = realtime_inputs(spec, vint, lv.index, ret)
    res = run_tournament(spec, ti)
    assert res.selection is None and not res.table["is_eligible"].any()


# ------------------------------------------------------------------------------------------- published replays
@pytest.mark.parametrize("pair", ["unrate_spy", "cc_delinquency_spy", "hy_ig_spy"])
def test_published_rule_replays_to_1e6(pair):
    from harness.run import load_pair, replay_legacy
    rep = replay_legacy(load_pair(pair))
    assert rep["pass"], rep
    assert rep["strategy_return"]["max_abs_diff"] <= 1e-6
