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
