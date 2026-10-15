"""Check E of scripts/gate_consistency.py: prose must state the CURRENT winner.

Run:  python -m pytest tests/test_gate_consistency_e.py
Fixtures are built in tmp_path and gate_consistency.REPO is monkeypatched, so no repo data is read.
"""
import importlib.util
import json
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "gate_consistency", Path(__file__).resolve().parents[1] / "scripts" / "gate_consistency.py")
gc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gc)

# cc_delinquency_spy after the IS/OOS rework (spike261015_is_oos_floor, 7d7cee1f)
NEW_WINNER = {
    "pair_id": "fx_spy", "signal_code": "level", "threshold_code": "T_roll_p75",
    "direction": "countercyclical", "lead_value": 2, "lead_unit": "quarters",
    "oos_sharpe": 0.504477,
}
# Prose as it stood before the rework: old winner diff_1q / T0_zero / procyclical / L4 QUARTERS.
# NB the string "0.50" appears legitimately (a concurrent-quartile Sharpe), which is what
# let the old Sharpe-only check pass.
STALE_PROSE = '''
"""
  - The winner (`diff_1q / T0_zero / procyclical / L4 QUARTERS`; OOS Sharpe 1.37 vs 0.87)
    quartiles (Q4, worst SPY Sharpe 0.50 vs 1.23 in Q1) support the countercyclical reading.
QUARTERLY conventions: leads in QUARTERS (winner L4q ~ 12 months)
"""
'''
CURRENT_PROSE = '''
"""
  - The winner (`level / T_roll_p75 / countercyclical / L2 QUARTERS`; OOS Sharpe 0.50 vs 0.87)
    Runner-up (`zscore_20q / T_z_0 / procyclical / L2`, 0.35) is a different signal.
"""
'''


def _run(tmp_path, monkeypatch, prose, ws=NEW_WINNER):
    pair = ws["pair_id"]
    (tmp_path / "results" / pair).mkdir(parents=True)
    (tmp_path / "results" / pair / "winner_summary.json").write_text(json.dumps(ws))
    (tmp_path / "app" / "pair_configs").mkdir(parents=True)
    (tmp_path / "app" / "pair_configs" / f"{pair}_config.py").write_text(prose)
    monkeypatch.setattr(gc, "REPO", tmp_path)
    return gc.check_pair(pair)


def test_cc_delinquency_stale_prose_fires(tmp_path, monkeypatch):
    hard, soft = _run(tmp_path, monkeypatch, STALE_PROSE)
    e = [m for m in soft if m.startswith("E:")]
    assert not hard
    # Sharpe "0.50" coincidentally present -> must NOT be the only line of defence
    assert any("lead L2" in m for m in e)
    assert any("T_roll_p75" in m for m in e)
    assert any("none equals the winner" in m for m in e)


def test_consistent_pair_passes(tmp_path, monkeypatch):
    hard, soft = _run(tmp_path, monkeypatch, CURRENT_PROSE)
    assert not hard
    assert [m for m in soft if m.startswith("E:")] == []


def test_runner_up_with_different_combo_is_not_flagged():
    prose = ("winner `level / T_roll_p75 / countercyclical / L2` 0.5045; "
             "runner-up `chg_12m / T0_zero / procyclical / L9`")
    assert gc.check_prose(prose, NEW_WINNER) == []


def test_pair_prefixed_signal_name_tolerated():
    prose = "winner `fx_level / T_roll_p75 / countercyclical / L2` 0.5045"
    assert gc.check_prose(prose, NEW_WINNER) == []


@pytest.mark.parametrize("prose", [
    "winner `level / T_roll_p75 / procyclical / L2` 0.5045",      # wrong direction
    "winner `level / T_roll_p75 / countercyclical / L4` 0.5045",  # wrong lead (L2 absent too)
    "winner `level / T0_zero / countercyclical / L2` 0.5045",     # wrong threshold
])
def test_single_field_drift_fires(prose):
    assert any(m.startswith("E:") for m in gc.check_prose(prose, NEW_WINNER))


def test_lead_l1_does_not_match_l12():
    ws = dict(NEW_WINNER, lead_value=1, lead_unit="months")
    out = gc.check_prose("T_roll_p75 0.5045 lead L12", ws)
    assert any("lead L1 " in m for m in out)


# ---------------------------------------------------------------------------------------------
# v2: standalone direction / lead binding / signal identity / daily phrasings / spellings
# ---------------------------------------------------------------------------------------------
def _E(out):
    return [m for m in out if m.startswith("E:")]


def _INFO(out):
    return [m for m in out if m.startswith("INFO:")]


DAILY = {"pair_id": "d_spy", "signal_code": "S_zscore_126d", "signal_column": "gold_copper_zscore_126d",
         "signal_display_name": "G/C zscore_126d", "threshold_code": "T2_p50", "direction": "countercyclical",
         "lead_value": 21, "lead_unit": "days", "oos_sharpe": 1.2734}
OTHERS = {"gold_copper_roc_63d": "gold_copper_roc_63d", "gold_copper_pctrank_504d": "gold_copper_pctrank_504d",
          "S_zscore_126d": "gold_copper_zscore_126d"}
# no triple notation anywhere: the shape most real pairs have
FREE = ("The tournament winner uses the 126-day z-score of the gold/copper ratio at a 21-day lead "
        "(threshold T2_p50). The countercyclical orientation means we go to cash when the ratio rises. "
        "OOS Sharpe 1.27 versus 0.66 for buy-and-hold.")


def test_free_prose_consistent_passes():
    out = gc.check_prose(FREE, DAILY, OTHERS)
    assert _E(out) == [] and _INFO(out) == []


def test_gap1_standalone_direction_flip_fires():
    out = gc.check_prose(FREE.replace("countercyclical", "procyclical"), DAILY, OTHERS)
    assert any("direction" in m for m in _E(out))


def test_gap1_direction_in_non_winner_sentence_or_contrast_is_ignored():
    prose = FREE + " The economic prior is procyclical. Correlation confirms the procyclical hypothesis."
    assert _E(gc.check_prose(prose, DAILY, OTHERS)) == []


def test_gap1_direction_unstated_is_info_not_silence():
    prose = FREE.replace("The countercyclical orientation means we go to cash when the ratio rises. ", "")
    out = gc.check_prose(prose, DAILY, OTHERS)
    assert _E(out) == [] and any("direction" in m and "NOT verified" in m for m in _INFO(out))


def test_gap2_signal_swap_fires_and_alias_forms_verify():
    swapped = FREE.replace("126-day z-score", "gold_copper_roc_63d")
    assert any("signal" in m for m in _E(gc.check_prose(swapped, DAILY, OTHERS)))
    # winner named by data column / display label / human form all verify
    for form in ("gold_copper_zscore_126d", "G/C zscore_126d", "126-day z-score"):
        prose = FREE.replace("126-day z-score", form)
        assert _INFO(gc.check_prose(prose, DAILY, OTHERS)) == [], form


def test_gap2_unverifiable_signal_emits_info():
    prose = FREE.replace("the 126-day z-score of the gold/copper ratio", "a ratio rule")
    out = gc.check_prose(prose, DAILY, OTHERS)
    assert _E(out) == [] and any("signal" in m and "NOT verified" in m for m in _INFO(out))


def test_gap3_lead_masking_bound_to_winner_context():
    ws = dict(NEW_WINNER, lead_value=12, lead_unit="months")
    stale = "T_roll_p75 0.5045 level countercyclical. The winner is L9; the L12 curve peaks elsewhere."
    assert any("winner-describing prose states lead" in m for m in _E(gc.check_prose(stale, ws)))
    stale2 = "T_roll_p75 0.5045 level countercyclical. L9 winner; L12 curve peak"
    assert any("winner-describing prose states lead" in m for m in _E(gc.check_prose(stale2, ws)))
    ok = "T_roll_p75 0.5045 level countercyclical. The winner is L12; the L9 runner-up is weaker."
    assert _E(gc.check_prose(ok, ws)) == []
    ws9 = dict(ws, lead_value=9)
    assert _E(gc.check_prose("T_roll_p75 0.5045 level countercyclical. L9 winner; L12 curve peak", ws9)) == []


@pytest.mark.parametrize("phr", ["21 trading days", "21d", "21-day", "21 days", "L21"])
def test_gap4_daily_phrasings_recognised(phr):
    assert gc._lead_mentioned(f"the lead is {phr} here", 21, "days")
    out = gc.check_prose(FREE.replace("21-day lead", f"{phr} lead"), DAILY, OTHERS)
    assert not any("lead L21" in m for m in _E(out))


def test_gap4_daily_wrong_lead_fires():
    out = gc.check_prose(FREE.replace("21-day", "5-day"), DAILY, OTHERS)
    assert _E(out)


@pytest.mark.parametrize("spelling,norm", [
    ("pro", "procyclical"), ("procyclical", "procyclical"), ("pro_cyclical", "procyclical"),
    ("pro-cyclical", "procyclical"), ("cc", "countercyclical"), ("countercyclical", "countercyclical"),
    ("counter_cyclical", "countercyclical"), ("counter-cyclical", "countercyclical"),
    ("Counter Cyclical", "countercyclical")])
def test_gap5_direction_spellings_normalised(spelling, norm):
    assert gc._norm_dir(spelling) == norm


def test_gap5_counter_cyclical_in_triple_matches_winner():
    ws = dict(NEW_WINNER, direction="counter_cyclical")
    prose = "winner `level / T_roll_p75 / counter_cyclical / L2` 0.5045"
    assert _E(gc.check_prose(prose, ws)) == []
    prose_bad = "winner `level / T_roll_p75 / procyclical / L2` 0.5045"
    assert _E(gc.check_prose(prose_bad, ws))
