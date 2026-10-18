"""retail_inv_sales class (B1): MAIN (as known at the time) has no eligible candidate, so no winner is published.
Shared code must not assume a MAIN winner: run tag, consistency gate, sidebar data end, page state."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
import chart_provenance as cp  # noqa: E402
import gate_consistency as gc  # noqa: E402
from components import provenance as P  # noqa: E402
from components import sidebar, two_track  # noqa: E402

WS = {"pair_id": "toy_spy", "schema_version": "1.3.0", "main_eligible": False,
      "status": {"main_not_eligible": {"rt_start": "2013-07-31", "n_is_rows": 47, "min_required": 60}},
      "tracks": {"main": {"eligible": False, "winner": None, "n_candidates": 288},
                 "comparison": {"eligible": True, "oos_window": ["2017-06-30", "2026-09-30"]}}}


def _pair(tmp_path, ws, rows="signal,valid,is_eligible\nlevel,False,False\nBENCHMARK,True,True\n"):
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    (d / "winner_summary.json").write_text(json.dumps(ws))
    (d / "tournament_results_20261016.csv").write_text(rows)
    (d / "tournament_results_20261018.csv").write_text(rows)
    return d


def test_run_tag_without_a_main_winner(tmp_path):
    d = _pair(tmp_path, WS)
    assert cp.run_tag_of(WS, d) == "20261018"                       # latest dated tournament file
    assert cp.run_tag_of(dict(WS, run_tag="20261019"), d) == "20261019"   # harness writes it explicitly
    assert P.run_tag(WS, d) == "20261018" and P.run_tag(dict(WS, run_tag="20261019"), d) == "20261019"


def test_consistency_gate_checks_the_no_winner_claim(tmp_path, monkeypatch):
    _pair(tmp_path, WS)
    monkeypatch.setattr(gc, "REPO", tmp_path)
    hard, soft = gc.check_pair("toy_spy")
    assert hard == [] and soft[0].startswith("INFO: MAIN not eligible")
    (tmp_path / "results" / "toy_spy" / "tournament_results_20261018.csv").write_text(
        "signal,valid,is_eligible\nlevel,True,True\n")
    hard, _ = gc.check_pair("toy_spy")
    assert hard and "says MAIN has no eligible candidate" in hard[0]


def test_sidebar_data_end_and_page_state(tmp_path, monkeypatch):
    _pair(tmp_path, WS)
    monkeypatch.setattr(sidebar, "_REPO_ROOT", tmp_path)
    sidebar._oos_end.cache_clear()
    assert sidebar._oos_end("toy_spy") == "2026-09-30"             # the as-revised-today test window end
    sidebar._oos_end.cache_clear()
    assert two_track.no_main({"track_state": "rt_insufficient"})
    assert not two_track.no_main({"track_state": "both"}) and not two_track.no_main(None)
