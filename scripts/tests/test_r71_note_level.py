"""The R7.1 note's "95% half-width" is the calibration's quantile level, not a result: the provenance allowlist
entry r71_note_quantile_level admits it only because the phrase, the rendered note and r71_calibrate.Q_LEVEL agree.
If the method level changes, these tests fail instead of the page stating the wrong level."""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))
import gate_number_provenance as g  # noqa: E402
import r71_calibrate as C  # noqa: E402
from components import provenance as P  # noqa: E402
from components import two_track  # noqa: E402

LEVEL = round(C.Q_LEVEL * 100)
CAL = {"B": 199, "L": 12, "L_floor": 3, "L_cap": 24, "T": 0.0697, "centre": 0.0023, "critical_value": 0.1437,
       "p_value": 0.36, "pass": True, "p_resolution": 0.005, "tail_paths": 10,
       "sensitivity": {"block": 24, "B": 99, "pass": True, "p_value": 0.36}}


def _entry():
    return next(e for e in json.loads(g.ALLOWLIST.read_text())["entries"] if e["id"] == "r71_note_quantile_level")


def _note(tmp_path, monkeypatch):
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    nt = {"timing_sharpe_mean": 0.07, "timing_sharpe_se_dependent": 0.03, "r71_tolerance": 0.1, "r71_pass": True}
    (d / "winner_summary.json").write_text(json.dumps({"lead_unit": "months", "tracks": {"main": {"null_tournament": nt}}}))
    monkeypatch.setattr(two_track, "__file__", str(tmp_path / "app" / "components" / "two_track.py"))
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(P, "r71_calibration", lambda pair, track: ("ok", CAL, None))
    return two_track.r71_note("toy_spy")


def test_rendered_note_states_the_calibration_level(tmp_path, monkeypatch):
    note = _note(tmp_path, monkeypatch)
    levels = [int(x) for x in re.findall(r"(\d+)% half-width", note)]
    assert len(levels) == 2 and set(levels) == {LEVEL}


def test_allowlist_phrase_level_matches_and_covers_the_rendered_phrases(tmp_path, monkeypatch):
    e = _entry()
    assert {int(x) for x in re.findall(r"(\d+)% half-width", e["regex"])} == {LEVEL}
    note = _note(tmp_path, monkeypatch)
    spans = [m.span(1) for m in re.finditer(r"(\d+%)\s*half-width", note)]
    assert spans and all(g._allowed(s, note, [e]) for s in spans)
    assert not g._allowed((0, 3), "90% half-width of the band", [e])     # another level is not admitted


def test_decide_uses_q_level(monkeypatch):
    rng = np.random.default_rng(7)
    s, c = rng.normal(0, 0.1, 199) * 100, np.full(199, 100)
    ts = s / c
    dev = np.abs(ts - np.median(ts))
    assert C.decide(0.0, s, c)["critical_value"] == round(float(np.quantile(dev, C.Q_LEVEL)), 4)
    monkeypatch.setattr(C, "Q_LEVEL", 0.90)
    assert C.decide(0.0, s, c)["critical_value"] == round(float(np.quantile(dev, 0.90)), 4)
