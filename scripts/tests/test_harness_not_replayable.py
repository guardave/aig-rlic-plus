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
