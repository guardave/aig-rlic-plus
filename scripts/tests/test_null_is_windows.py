"""QA B1 umcsent M1: the chance check discloses the training windows of the scrambled contests vs the real winner."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
import gate_number_provenance as g  # noqa: E402
from components import provenance as P  # noqa: E402
from components import two_track  # noqa: E402


def _pair(tmp_path, monkeypatch, draws, actual):
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    (d / "winner_summary.json").write_text('{"lead_unit": "months"}')
    rows = [{"draw": -1, "offset": 0, "is_start": "1993-02-28", "is_n_draw": None, "is_n_actual": actual}]
    rows += [{"draw": i, "offset": 115 + i, "is_start": "2000-01-31", "is_n_draw": n, "is_n_actual": None}
             for i, n in enumerate(draws)]
    pd.DataFrame(rows).to_csv(d / "null_is_windows_20261017.csv", index=False)
    monkeypatch.setattr(two_track, "__file__", str(tmp_path / "app" / "components" / "two_track.py"))
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")


def test_note_states_the_draws_window_range_against_the_actual(tmp_path, monkeypatch):
    _pair(tmp_path, monkeypatch, [60, 124, 246], 287)
    note = two_track.is_window_note("toy_spy")
    assert "60 to 246 months" in note and "the real winner on 287" in note and "not like-for-like" in note


def test_note_is_tagged_in_gate_mode(tmp_path, monkeypatch):
    _pair(tmp_path, monkeypatch, [60, 124, 246], 287)
    monkeypatch.setenv("AIG_PROVENANCE_GATE", "1")
    clean, _k, _p, sents, _d = g.parse_markers(two_track.is_window_note("toy_spy"))
    assert len(sents) == 3
    for _a, _b, src, unit, shown in sents:
        assert g.verify_sentinel(src, unit, shown, {}, "toy_spy") is None, src


def test_equal_windows_say_so_and_no_file_says_nothing(tmp_path, monkeypatch):
    _pair(tmp_path, monkeypatch, [287, 287], 287)
    assert "same 287 months" in two_track.is_window_note("toy_spy")
    assert two_track.is_window_note("absent_spy") == ""


def test_draw_record_carries_the_training_window():
    import inspect
    from harness import null
    src = inspect.getsource(null.draw_record)
    assert '"is_start"' in src and '"is_n"' in src


@pytest.mark.skipif(not (Path(__file__).resolve().parents[2] / "results" / "unrate_spy").exists(),
                    reason="unrate_spy artifacts not present")
def test_real_time_draws_train_on_the_real_winners_window():
    # Lead ruling on M1: the within-vintage wrap keeps every draw's training window equal to the real winner's
    # (v1: offset 166 trained on 195 of 287 months)
    from harness import run as R
    from harness.engine import run_tournament
    mod = R.load_pair("unrate_spy")
    ti = R.build_tracks(mod)["main"]
    act = run_tournament(mod.SPEC, ti, full_table=False)
    make, _n = R.null_maker(mod, "main", ti)
    for k in (115, 381):
        r = run_tournament(mod.SPEC, make(k), full_table=False)
        assert r.common_is_start == act.common_is_start and int(r.is_mask.sum()) == int(act.is_mask.sum()), k


def test_previously_published_pilots_carry_previous_selection():
    # QA null v2 F4 (read as 'dropped'; the field was in fact ADDED when the reruns moved the pilots to the current
    # harness): a pair with a previously published rule must carry previous_selection in its winner fields
    import json
    root = Path(__file__).resolve().parents[2]
    for pair in ("unrate_spy", "cc_delinquency_spy"):
        ws = json.loads((root / "results" / pair / "winner_summary.json").read_text())
        if ws["selection"].get("previously_published"):
            f = ws["winner_fields"].get("previous_selection")
            assert f and f["text"] == ws["selection"]["previously_published"][0]["selection"], pair


def test_panel_caption_describes_a_constant_roll():
    src = Path(two_track.__file__).read_text()
    assert "fixed " in src and "wrapping around once" in src and "within each" not in src


def _coarse_pair(tmp_path, monkeypatch, eff=14.1):
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    (d / "winner_summary.json").write_text(
        '{"tracks": {"main": {"null_tournament": {"timing_sharpe_effective_draws": %s}}}}' % eff)
    monkeypatch.setattr(two_track, "__file__", str(tmp_path / "app" / "components" / "two_track.py"))
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")


def test_coarse_percentile_is_disclosed_when_the_span_caps_the_draws(tmp_path, monkeypatch):
    # Lead v3.1 item 2: cc runs every admissible shift (36), about 14 effectively independent.
    _coarse_pair(tmp_path, monkeypatch)
    nt = {"n_draws": 36, "n_admissible_offsets": 36, "n_draws_without_winner": 0}
    note = two_track.coarse_note("toy_spy", nt)
    assert "coarse" in note and "only 36 contests" in note and "about 14 of them effectively independent" in note
    assert two_track.coarse_note("toy_spy", {"n_draws": 100, "n_admissible_offsets": 243}) == ""


def test_coarse_note_is_tagged_in_gate_mode(tmp_path, monkeypatch):
    _coarse_pair(tmp_path, monkeypatch)
    monkeypatch.setenv("AIG_PROVENANCE_GATE", "1")
    nt = P.artifact({"n_draws": 36, "n_admissible_offsets": 36, "n_draws_without_winner": 0},
                    tmp_path / "results" / "toy_spy" / "track_summary.json")
    clean, _k, _p, sents, _d = g.parse_markers(two_track.coarse_note("toy_spy", nt))
    assert len(sents) == 2 and "36" in clean and "14" in clean
