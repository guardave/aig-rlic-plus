"""Harness replay: the explicit not_replayable path (pairs declaring LEGACY_REPLAY = None)."""
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import prose  # noqa: E402
from harness import run as R  # noqa: E402
from harness.spec import PairSpec, Rule  # noqa: E402


def _mod(repro=None, published=True, **extra):
    spec = PairSpec(pair_id="toy_not_replayable_pair", freq="M", lead_unit="months", leads=[1, 2, 3],
                    oos_start="2018-01-31", min_is_n=60, position_shift=1, track_policy="compute_twice",
                    release_series=None, level_columns=["x"], features=lambda lv: lv,
                    signals={"lvl": "x"}, rules=lambda s: {"T0": Rule("raw", None, 0.0)})
    m = types.SimpleNamespace(SPEC=spec, LEGACY_TAG="20260314", LEGACY_REPLAY=None,
                              LEGACY_REPLAY_REASON="OOS-selected, no strategy returns",
                              LEGACY_DIFFERENCES=["valid flag differs", "NaN bearish vs undefined"],
                              legacy_reproduction=lambda: repro, **extra)
    if published:
        m.LEGACY_PUBLISHED = {"key": "lvl|T0|P3|procyclical|6", "signal": "lvl", "threshold": "T0", "strategy": "P3",
                              "direction": "procyclical", "lead": 6, "oos_sharpe": 1.4454}
    return m


def test_not_replayable_report_fields_and_acceptance():
    rep = R.replay_legacy(_mod(repro={"gaps": "two rounding ties at 4 dp", "published_rule_reproduces": True}))
    assert rep["status"] == "not_replayable" and rep["pass"] is None
    assert set(rep["missing_files"]) == {f.format(tag="20260314") for f in R.LEGACY_FILES}
    assert rep["published"]["selection"] == "published (OOS-selected, legacy method)"
    assert rep["published"]["is_sharpe"] is None and rep["published"]["tag"] == "20260314"
    assert rep["definitional_differences"] and rep["reason"]
    assert rep["acceptance_4_1"]["pass"] is True


def test_not_replayable_fails_acceptance_without_documented_reproduction():
    assert R.replay_legacy(_mod(repro=None))["acceptance_4_1"]["pass"] is False
    assert R.replay_legacy(_mod(repro={"gaps": "  "}))["acceptance_4_1"]["pass"] is False
    assert R.replay_legacy(_mod(repro={"gaps": "x"}, published=False))["acceptance_4_1"]["pass"] is False


def test_previous_fields_carry_the_published_label_not_a_harness_row():
    rep = R.replay_legacy(_mod(repro={"gaps": "none beyond rounding"}))
    f = prose.previous_fields(rep["published"], "months")
    assert f["previous_selection"]["text"] == "published (OOS-selected, legacy method)"
    assert f["previous_rule"]["value"] == "lvl|T0|P3|procyclical|6"
    assert f["previous_is_sharpe"]["text"] == "n/a" and f["previous_oos_sharpe"]["text"] == "1.45"


def test_pairs_without_the_declaration_keep_the_harness_replay(monkeypatch):
    called = []
    m = _mod()
    del m.LEGACY_REPLAY
    monkeypatch.setattr(R, "run_tournament", lambda *a, **k: called.append(1) or (_ for _ in ()).throw(RuntimeError("replay")))
    monkeypatch.setattr(m, "legacy_panel", lambda: (None, types.SimpleNamespace(to_numpy=lambda *_: None)), raising=False)
    monkeypatch.setattr(R, "legacy_inputs", lambda *a, **k: None)
    try:
        R.replay_legacy(m)
    except RuntimeError:
        pass
    assert called == [1]


# ------------------------------------------------------------------ Legacy.selection / Legacy.is_window
def _legacy_mod(tmp_path, monkeypatch, selection):
    import dataclasses

    import numpy as np
    import pandas as pd
    from harness.data import legacy_inputs
    from harness.engine import run_tournament
    from harness.spec import Legacy
    idx = pd.date_range("1995-01-31", periods=300, freq="ME")
    rng = np.random.default_rng(3)
    lv = pd.DataFrame({"x": np.cumsum(rng.normal(size=300))}, index=idx)
    ret = pd.Series(rng.normal(0.006, 0.04, 300), index=idx)
    ret.iloc[0] = np.nan
    spec = PairSpec(pair_id="toy_legacy_sel", freq="M", lead_unit="months", leads=[1, 2, 3], oos_start="2015-01-31",
                    min_is_n=36, position_shift=0, track_policy="compute_twice", release_series=None,
                    level_columns=["x"], features=lambda d: d.assign(chg=d["x"].diff(3)),
                    signals={"lvl": "x", "chg": "chg"}, rules=lambda s: {"T0": Rule("raw", None, 0.0)},
                    legacy=Legacy(selection=selection, is_window="own_dropna"))
    res = run_tournament(spec, legacy_inputs(spec, lv, ret.to_numpy(float)), legacy=True)
    tab = res.table
    pub = tab[["signal", "threshold", "strategy", "is_sharpe", "oos_sharpe", "is_n", "oos_n", "valid"]].copy()
    pub["lead_months"] = tab["lead"].to_numpy()
    pub["annual_turnover"] = 1.0
    ok = pub[pub["valid"] & (pub["oos_sharpe"] > 0)]
    w_oos = int(ok["oos_sharpe"].idxmax())
    rdir = tmp_path / "results" / "toy_legacy_sel"
    rdir.mkdir(parents=True)
    pub.to_csv(rdir / "tournament_results_20260101.csv", index=False)
    w = w_oos if selection == "max_oos_valid" else res.selection["winner"]
    pd.DataFrame({"strategy_return": res.deployable_returns(w)}).to_csv(rdir / "strategy_returns_20260101.csv",
                                                                       index=False)
    monkeypatch.setattr(R, "REPO", tmp_path)
    m = types.SimpleNamespace(SPEC=dataclasses.replace(spec), LEGACY_TAG="20260101",
                              legacy_panel=lambda: (lv, ret))
    return m, tab, w_oos, res


def test_max_oos_valid_replays_the_oos_selected_published_row(tmp_path, monkeypatch):
    m, tab, w_oos, res = _legacy_mod(tmp_path, monkeypatch, "max_oos_valid")
    rep = R.replay_legacy(m)
    assert rep["selection_method"] == "max_oos_valid" and rep["pass"]
    assert rep["published"]["key"] == tab.loc[w_oos, "key"]
    assert rep["published"]["selection"].startswith("published (OOS-selected")
    if res.selection and res.selection["winner"] != w_oos:      # the IS argmax would have named another row
        assert rep["published"]["key"] != tab.loc[res.selection["winner"], "key"]
    f = prose.previous_fields(rep["published"], "months")
    assert f["previous_rule"]["value"] == tab.loc[w_oos, "key"]
    assert f["previous_selection"]["text"].startswith("published (OOS-selected")


def test_is_argmax_default_and_own_dropna_window(tmp_path, monkeypatch):
    m, tab, w_oos, res = _legacy_mod(tmp_path, monkeypatch, "is_argmax")
    rep = R.replay_legacy(m)
    assert rep["selection_method"] == "is_argmax" and rep["pass"]
    assert rep["published"]["key"] == tab.loc[res.selection["winner"], "key"]
    # own_dropna: every candidate is scored on all of its own pre-OOS rows, so is_n differs across signals
    assert tab.groupby("signal")["is_n"].max().nunique() > 1
