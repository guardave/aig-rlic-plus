"""MAIN (as known at the time) has no eligible candidate (retail_inv_sales class), and current-run files only
(QA nomain b686ff42 F1-F6): no silent fallback to another run, gate checks against the run's files, page text."""
import json
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))
import chart_provenance as cp  # noqa: E402
import gate_consistency as gc  # noqa: E402
import gate_number_provenance as g  # noqa: E402
from components import provenance as P  # noqa: E402
from components import sidebar, two_track  # noqa: E402

TAG = "20261018"
WS = {"pair_id": "toy_spy", "schema_version": "1.3.0", "run_tag": TAG, "main_eligible": False,
      "status": {"main_not_eligible": {"rt_start": "2013-07-31", "n_is_rows": 47, "min_required": 60}},
      "tracks": {"main": {"eligible": False, "winner": None, "n_candidates": 2,
                          "sample": {"first_vintage": "2013-06-13"}},
                 "comparison": {"eligible": True, "oos_window": ["2017-06-30", "2026-09-30"],
                                "winner": {"key": "a|T|P1|procyclical|6", "is_sharpe": 0.855, "oos_sharpe": 0.818},
                                "bh_oos": {"sharpe": 0.964}}}}
MAIN = ("signal,key,valid,is_eligible,own_is_n,own_is_start\n"
        "a,a|T|P1|procyclical|6,False,False,47,2013-07-31\nb,b|T|P1|procyclical|6,False,False,40,2014-02-28\n"
        "BENCHMARK,BH,True,True,,\n")
HIND = ("signal,key,is_sharpe,oos_sharpe\na,a|T|P1|procyclical|6,0.855,0.818\nb,b|T|P1|procyclical|6,0.5,0.4\n"
        "BENCHMARK,BH,0.7,0.964\n")


def _pair(tmp_path, ws=WS, main=MAIN, hind=HIND):
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True, exist_ok=True)
    (d / "winner_summary.json").write_text(json.dumps(ws))
    (d / f"tournament_results_{TAG}.csv").write_text(main)
    (d / f"hindsight_tournament_results_{TAG}.csv").write_text(hind)
    (d / "tournament_results_20261016.csv").write_text(main.replace("False,False,47", "True,True,99"))  # superseded
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "pair_spec_toy_spy.py").write_text("class _S:\n    min_is_n = 60\nSPEC = _S()\n")
    return d


def test_run_tag_never_guesses_from_the_latest_file(tmp_path):
    d = _pair(tmp_path)
    assert cp.run_tag_of(WS, d) == TAG and P.run_tag(WS, d) == TAG
    bare = {k: v for k, v in WS.items() if k != "run_tag"}
    assert cp.run_tag_of(bare, d) is None and P.run_tag(bare, d) is None   # no latest-dated-file guess (F2)


def test_phase_b_current_file_fails_loudly_and_never_serves_another_run(tmp_path, monkeypatch):
    d = _pair(tmp_path)
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")
    assert P.current_file("toy_spy", "tournament_results") == d / f"tournament_results_{TAG}.csv"
    (d / f"tournament_results_{TAG}.csv").unlink()                 # the 20261016 file is still there
    with pytest.raises(P.CurrentRunFileError, match="is missing"):
        P.current_file("toy_spy", "tournament_results")
    (d / "winner_summary.json").write_text(json.dumps({k: v for k, v in WS.items() if k != "run_tag"}))
    with pytest.raises(P.CurrentRunFileError, match="no run tag"):
        P.current_file("toy_spy", "tournament_results")


def test_consistency_gate_checks_every_no_winner_claim_against_the_run_files(tmp_path, monkeypatch):
    monkeypatch.setattr(gc, "REPO", tmp_path)
    _pair(tmp_path)
    hard, soft = gc.check_pair("toy_spy")
    assert hard == [] and soft[0].startswith("INFO: MAIN not eligible")
    mutations = {
        "a valid MAIN row": dict(main=MAIN.replace("a,a|T|P1|procyclical|6,False,False", "a,a|T|P1|procyclical|6,True,True")),
        "candidate count": dict(ws=json.loads(json.dumps(WS).replace('"n_candidates": 2', '"n_candidates": 3'))),
        "first training month": dict(ws=json.loads(json.dumps(WS).replace('"rt_start": "2013-07-31"', '"rt_start": "2012-01-31"'))),
        "training rows": dict(ws=json.loads(json.dumps(WS).replace('"n_is_rows": 47', '"n_is_rows": 59'))),
        "rows required": dict(ws=json.loads(json.dumps(WS).replace('"min_required": 60', '"min_required": 36'))),
        "hindsight winner Sharpe": dict(hind=HIND.replace("0.855,0.818", "0.855,0.95")),
        "hindsight winner row": dict(hind=HIND.replace("a,a|T|P1|procyclical|6", "a,zz")),
        "hindsight buy-and-hold": dict(hind=HIND.replace("BENCHMARK,BH,0.7,0.964", "BENCHMARK,BH,0.7,0.91")),
        "missing column": dict(main=MAIN.replace("own_is_n", "x_is_n")),
    }
    for name, kw in mutations.items():
        import shutil
        shutil.rmtree(tmp_path / "results")
        _pair(tmp_path, **kw)
        hard, _ = gc.check_pair("toy_spy")
        assert hard, name
    shutil.rmtree(tmp_path / "results")
    _pair(tmp_path, ws={k: v for k, v in WS.items() if k != "run_tag"})
    assert gc.check_pair("toy_spy")[0]                               # no run tag: hard


def test_sidebar_data_end_and_state(tmp_path, monkeypatch):
    _pair(tmp_path)
    monkeypatch.setattr(sidebar, "_REPO_ROOT", tmp_path)
    sidebar._oos_end.cache_clear()
    assert sidebar._oos_end("toy_spy") == "2026-09-30"
    sidebar._oos_end.cache_clear()
    assert two_track.no_main({"track_state": "rt_insufficient"}) and not two_track.no_main({"track_state": "both"})


NO_MAIN_PAIRS = sorted(p.parent.name for p in (ROOT / "results").glob("*/winner_summary.json")
                       if json.loads(p.read_text()).get("main_eligible") is False
                       and "tracks" in json.loads(p.read_text()))


def _page_text(pair, sections=("story", "evidence", "strategy", "methodology")):
    pages = g.render_pages(pair, sections=sections, tagged=False)
    return {s: "\n".join(t for _k, t in blocks) for s, blocks in pages.items()}


@pytest.mark.parametrize("pair", NO_MAIN_PAIRS or [pytest.param(None, marks=pytest.mark.skip(
    reason="no MAIN-ineligible Phase B pair on this branch (retail_inv_sales_spy lands with its merge)"))])
def test_no_main_pair_pages_state_the_reason_and_label_the_hindsight(pair):
    txt = _page_text(pair)
    allt = "\n".join(txt.values())
    assert "not yet run" not in allt                                  # F1
    assert "Real-time track: not eligible" in txt["story"] and "Real-time track: not eligible" in txt["strategy"]
    assert "Hindsight test-period Sharpe (revised data)" in txt["strategy"]
    assert "Training Sharpe 0.00" not in allt and "\n0.00 (did not meet" not in allt   # F5
    assert "Status: No status" not in allt


@pytest.mark.parametrize("pair", ["unrate_spy"] + NO_MAIN_PAIRS)
def test_a_missing_current_run_file_fails_visibly(pair):
    ws = json.loads((ROOT / "results" / pair / "winner_summary.json").read_text())
    f = ROOT / "results" / pair / f"tournament_results_{P.run_tag(ws)}.csv"
    hidden = f.with_suffix(".csv.hidden")
    os.rename(f, hidden)
    try:
        txt = _page_text(pair, sections=("strategy",))["strategy"]
    finally:
        os.rename(hidden, f)
    assert "Current-run file missing" in txt and f.name in txt


def test_structured_prose_knows_the_previous_rule_without_a_selection_block():
    # retail helper item 11: previous Sharpes / lead were read from selection.previously_published only
    import gate_structured_prose as gsp
    ws = dict(WS, winner_fields={"previous_oos_sharpe": {"value": 0.7312, "text": "0.73"},
                                 "previous_is_sharpe": {"value": 0.8905, "text": "0.89"},
                                 "previous_lead": {"value": 6, "text": "6"}})
    f = gsp.fields_from_summary(ws)
    assert 0.7312 in f["_legacy_oos_sharpe"] and 0.8905 in f["_legacy_oos_sharpe"] and 6 in f["_legacy_lead"]


SINGLE_NO_ARCHIVE = sorted(p.parent.name for p in (ROOT / "results").glob("*/winner_summary.json")
                           if json.loads(p.read_text()).get("track_policy") == "single_revised_no_archive")


@pytest.mark.parametrize("pair", SINGLE_NO_ARCHIVE or [pytest.param(None, marks=pytest.mark.skip(
    reason="no single_revised_no_archive pair on this branch (ism_mfg / umcsent_spy / cement land with their merges)"))])
def test_single_track_no_archive_pages_never_claim_as_known_at(pair):
    # umcsent_spy QA HIGH: shared text said "as known at each date / at the time" on revised-only pairs
    import re
    txt = "\n".join(_page_text(pair).values())
    assert not re.search(r"\bas[- ]known[- ]at", txt, re.I), re.search(r".{80}\bas[- ]known[- ]at.{80}", txt,
                                                                       re.I | re.S)


def _cal_pair(tmp_path, null_text="draw,offset\n0,5\n", rec_sha=None, tag=TAG, track="main", extra=None):
    import hashlib
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True, exist_ok=True)
    (d / "winner_summary.json").write_text(json.dumps({"run_tag": TAG, "tracks": {"main": {}}}))
    (d / f"null_tournament_{TAG}.csv").write_text(null_text)
    sha = rec_sha or hashlib.sha256(null_text.encode()).hexdigest()
    (d / f"r71_calibration_{tag}.json").write_text(json.dumps({"tracks": {track: {
        "null_file": f"null_tournament_{TAG}.csv", "null_sha256": sha, "method": "stationary bootstrap",
        "B": 199, "T": -0.196, "centre": -0.01, "critical_value": 0.17, "pass": False, "p_value": 0.03,
        "L": 3, "L_floor": 3, "L_cap": 9, "p_resolution": 0.005, "tail_paths": 10,
        "sensitivity": {"B": 99, "block": 6, "centre": 0.0, "critical_value": 0.16, "pass": False, "p_value": 0.02},
        "screening_threshold": 0.1, "screening_flag": True, "harness_commit": "f" * 40, **(extra or {})}}}))
    return d


def test_r71_calibration_artifact_status(tmp_path):
    # Lead decoupling: the calibrated reference is a separate artifact hash-bound to the null file
    d = _cal_pair(tmp_path)
    assert P.r71_calibration("toy_spy", "main", d)[0] == "ok"
    assert P.r71_calibration("toy_spy", "comparison", d)[0] == "pending"           # no record for the track
    (d / f"null_tournament_{TAG}.csv").write_text("draw,offset\n0,6\n")            # null changed since
    assert P.r71_calibration("toy_spy", "main", d)[0] == "stale"
    d2 = _cal_pair(tmp_path / "b", tag="20261001")                                 # artifact of another run
    assert P.r71_calibration("toy_spy", "main", d2)[0] == "stale"
    (d2 / "r71_calibration_20261001.json").unlink()
    assert P.r71_calibration("toy_spy", "main", d2)[0] == "pending"


def test_r71_note_pending_text_on_the_pilots():
    note = two_track.r71_note("unrate_spy")
    assert "understates the spread of the null mean" in note and "calibrated reference is pending" in note
    assert "\n\n" + two_track.R71_SCREEN_LABEL + ": " in note          # option C: the screen is stated while pending


def _cal_note(tmp_path, monkeypatch, **kw):
    d = _cal_pair(tmp_path, **kw)
    ws = {"run_tag": TAG, "lead_unit": "quarters", "tracks": {"main": {"null_tournament": {
        "timing_sharpe_mean": -0.196, "timing_sharpe_se_dependent": 0.058, "r71_tolerance": 0.117, "r71_pass": False}}}}
    (d / "winner_summary.json").write_text(json.dumps(ws))
    monkeypatch.setattr(two_track, "__file__", str(tmp_path / "app" / "components" / "two_track.py"))
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")
    return d, ws


def test_r71_note_renders_block_rule_p_value_resolution_and_a_separate_screening_line(tmp_path, monkeypatch):
    # Codex option-C C5: L, block rule, p-value, B and the resolution limit in words; the 0.10 screen on its own
    # line, never merged into the pass / fail
    _cal_note(tmp_path, monkeypatch)
    note = two_track.r71_note("toy_spy")
    body, _sep, flag = note.partition("\n\n")
    for frag in ("199 simulated return paths", "stationary bootstrap", "blocks averaging 3 quarters",
                 "Politis-White rule on squared returns, at least 3 and at most 9 quarters", "p-value 0.030",
                 "the check does not pass", "fixed blocks of 6 quarters (99 paths)", "p-value 0.020",
                 "steps of 0.005", "the 10 paths beyond it", "coarse estimate"):
        assert frag in body, frag
    assert "Screening flag" not in body and "construction review" not in body
    assert flag.strip() == (two_track.R71_SCREEN_LABEL + ": raised; construction review required.")
    monkeypatch.setenv("AIG_PROVENANCE_GATE", "1")
    clean, _k, _p, _sents, _d = g.parse_markers(two_track.r71_note("toy_spy"))
    assert "Screening flag" in clean


def test_r71_screening_flag_is_independent_of_the_outcome(tmp_path, monkeypatch):
    # a calibrated PASS with |T| > 0.10 still raises the screen; a completed review is named
    _cal_note(tmp_path, monkeypatch, extra={"T": 0.15, "centre": 0.1, "critical_value": 0.17, "pass": True,
                                             "construction_review": {"status": "completed", "ref": "ledger R71-CR1"}})
    note = two_track.r71_note("toy_spy")
    assert "the check passes" in note
    assert note.rstrip().endswith("raised; construction review completed (see ledger R71-CR1).")
    _cal_note(tmp_path / "b", monkeypatch, extra={"T": 0.05, "centre": 0.0, "pass": True, "screening_flag": False})
    assert note != two_track.r71_note("toy_spy") and two_track.r71_note("toy_spy").rstrip().endswith(": not raised.")


def test_gate_flags_a_calibrated_record_that_contradicts_itself(tmp_path, monkeypatch):
    for extra, frag in (({"pass": True}, "contradicts |T - centre|"),
                        ({"screening_flag": False}, "screening_flag=False contradicts"),
                        ({"harness_commit": ""}, "harness_commit is empty")):
        d = _cal_pair(tmp_path / frag[:6].strip(), extra=extra)
        ws = {"run_tag": TAG, "tracks": {"main": {"null_tournament": {"timing_sharpe_mean": -0.196}}}}
        (d / "winner_summary.json").write_text(json.dumps(ws))
        monkeypatch.setattr(gc, "REPO", tmp_path)
        hard, _soft = gc._r71_calibration("toy_spy", d, ws)
        assert any(frag in h for h in hard), (frag, hard)


def test_r71_note_uses_the_calibrated_reference_and_gate_flags_stale(tmp_path, monkeypatch):
    d = _cal_pair(tmp_path)
    ws = {"run_tag": TAG, "tracks": {"main": {"null_tournament": {
        "timing_sharpe_mean": -0.196, "timing_sharpe_se_dependent": 0.058, "r71_tolerance": 0.117, "r71_pass": False}}}}
    (d / "winner_summary.json").write_text(json.dumps(ws))
    monkeypatch.setattr(two_track, "__file__", str(tmp_path / "app" / "components" / "two_track.py"))
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")
    note = two_track.r71_note("toy_spy")
    assert "calibrated reference: 199 simulated return paths" in note and "does not pass" in note
    assert "pending" not in note
    monkeypatch.setattr(gc, "REPO", tmp_path)
    hard, _soft = gc._r71_calibration("toy_spy", d, ws)
    assert hard == []
    (d / f"null_tournament_{TAG}.csv").write_text("draw,offset\n0,7\n")
    hard, _soft = gc._r71_calibration("toy_spy", d, ws)
    assert hard and "STALE" in hard[0]
    assert "calibrated reference is pending" in two_track.r71_note("toy_spy")
