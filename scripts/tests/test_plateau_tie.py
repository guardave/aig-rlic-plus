"""An exact tie on the stable-range score J is broken deterministically, recorded, and stated (QA rsxfs F3)."""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))
import gate_structured_prose as g  # noqa: E402
from components import provenance as P  # noqa: E402
from components import two_track  # noqa: E402
from harness.selection import plateau_select  # noqa: E402


def _table(sharpes):
    return pd.DataFrame({"signal": "s", "threshold": "t", "strategy": "P1", "direction": "pro",
                         "lead": list(range(2, 2 + len(sharpes))), "is_sharpe": sharpes, "valid": True,
                         "is_eligible": True, "is_ann_return": 0.1, "is_max_drawdown": -0.1, "is_n_trades": 5})


def test_tie_broken_by_the_best_sharpe_inside_the_range():
    # rsxfs: L2-L4 and L3-L5 both limited by L4 (J 0.68165); L3-L5 holds the higher best Sharpe
    sel = plateau_select(_table([0.70, 0.75, 0.68165, 0.90, 0.10]))
    assert sel["window_leads"] == [3, 4, 5] and sel["score"] == 0.68165
    assert sel["tie"] == {"n_windows": 2, "alternatives": [[2, 3, 4]], "broken_by": "best_is_sharpe_in_window"}
    assert plateau_select(_table([0.70, 0.75, 0.68165, 0.90, 0.10]))["tie"] == sel["tie"]     # deterministic


def test_tie_broken_by_search_order_and_no_tie_recorded_otherwise():
    sel = plateau_select(_table([0.9, 0.5, 0.5, 0.9]))          # L2-L4 and L3-L5: J 0.5, best 0.9 in both
    assert sel["window_leads"] == [2, 3, 4] and sel["tie"]["broken_by"] == "search_order"
    assert plateau_select(_table([0.3, 0.8, 0.9, 0.85, 0.2]))["tie"] is None


def test_page_states_the_tie_and_the_gate_accepts_the_named_leads(tmp_path, monkeypatch):
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    ws = {"lead_unit": "months", "tracks": {"main": {"eligible": True, "plateau": {
        "leads": [3, 4, 5], "score": 0.6817, "winner_lead": 5, "grid_edge": False,
        "tie": {"n_windows": 2, "alternatives": [[2, 3, 4]], "broken_by": "best_is_sharpe_in_window"}}}}}
    (d / "winner_summary.json").write_text(json.dumps(ws))
    monkeypatch.setattr(two_track, "__file__", str(tmp_path / "app" / "components" / "two_track.py"))
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(P, "lead_grid", lambda pair: [2, 3, 4, 5, 6])
    notes = two_track.grid_edge_notes("toy_spy")
    tie = [n for n in notes if "tied exactly" in n]
    assert tie == ["As known at the time: the stable range L3-L5 tied exactly on its score with L2-L4; the tie went "
                   "to L3-L5 because it has the higher best training Sharpe inside the range."]
    f = {"lead": 5, "plateau_leads": [3, 4, 5], "_lead_unit": "months", **{"_tie_leads": [2, 3, 4]}}
    assert not [b for b in g.check_text(tie[0], f, "x") if b.startswith("LEAD")]
    assert g.fields_from_summary(ws)["_tie_leads"] == [2, 3, 4]
    bad = g.check_text("The winning rule uses lead L2.", dict(f), "x")        # L2 outside a tie sentence: caught
    assert any(b.startswith("LEAD") for b in bad)


def test_single_track_notes_never_say_as_known_at(tmp_path, monkeypatch):
    # ism_mfg rebase: the raw-argmax grid-end line used the MAIN label on a no-archive pair
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    ws = {"lead_unit": "months", "track_policy": "single_revised_no_archive", "tracks": {"main": {
        "eligible": True, "plateau": {"leads": [9, 10, 11], "score": 0.5, "winner_lead": 10, "grid_edge": False},
        "raw_argmax": {"lead": 2}}}}
    (d / "winner_summary.json").write_text(json.dumps(ws))
    monkeypatch.setattr(two_track, "__file__", str(tmp_path / "app" / "components" / "two_track.py"))
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(P, "lead_grid", lambda pair: list(range(2, 14)))
    notes = two_track.grid_edge_notes("toy_spy")
    assert notes and notes[0].startswith("As revised today (no archive): the highest single training score")
    assert not any("as known at" in n.lower() for n in notes)
