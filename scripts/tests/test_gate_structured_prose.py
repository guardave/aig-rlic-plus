"""Tests for scripts/gate_structured_prose.py (Phase B structured-prose hard gate, plan section 4 item 7)."""
import shutil
import sys

import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gate_structured_prose as g  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "structured_prose"
RETAIL = FIX / "retail_inv_sales_spy_8198187b"        # config + winner_summary at int @8198187b (QA_VERIFY_int)
REWRITTEN = FIX / "retail_inv_sales_spy_rewritten"


@pytest.fixture(autouse=True)
def _fixture_results(tmp_path, monkeypatch):
    """A config reads its fields with components.winner_fields.load(pair) (PROVENANCE-API v5 allows nothing else):
    point load() at the fixture's own winner_summary.json."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
    from components import winner_fields
    (tmp_path / "retail_inv_sales_spy").mkdir()
    shutil.copy(REWRITTEN / "winner_summary.json", tmp_path / "retail_inv_sales_spy" / "winner_summary.json")
    monkeypatch.setattr(winner_fields, "_RESULTS", tmp_path)


def findings(d, hard=False):
    cfg = next(iter(sorted(d.glob("*_config.py*"))))
    return g.check_pair_files(cfg, d / "winner_summary.json", hard)


def test_retail_fixture_fails_on_all_four_stale_facts():
    res = findings(RETAIL)
    assert any(r.startswith("LEAD") and "three months earlier" in r for r in res)           # L3 prose, winner L6
    assert any(r.startswith("SHARPE") and "1.23" in r for r in res)                          # OOS 1.23, winner 0.73
    assert any(r.startswith("OBJECTIVE") for r in res)                                       # "selected for max OOS"
    assert any(r.startswith("COUNT") and "168" in r for r in res)                            # 168 vs 288
    assert not any(r.startswith("SHARPE") and ": 0.73 is not" in r for r in res)            # the true value passes


def test_rewritten_fixture_passes_hard_mode():
    assert findings(REWRITTEN, hard=True) == []


def test_hand_typed_number_fails_hard_mode(tmp_path):
    d = tmp_path / "typed"
    shutil.copytree(REWRITTEN, d)
    cfg = d / "retail_inv_sales_spy_config.py.txt"
    cfg.write_text(cfg.read_text().replace('out-of-sample Sharpe {W.oos_sharpe} versus "', 'out-of-sample Sharpe 0.73 versus "'))
    res = findings(d, hard=True)
    assert res and all(r.startswith(("HANDTYPED", "STRUCTURAL")) for r in res)
    assert any(r.startswith("STRUCTURAL") and '"0.73"' in r for r in res)


# QA_VERIFY_B0 M3: realistic stale prose the regex-only gate missed. Each is edited into the rewritten (passing)
# fixture; every one must FAIL in hard mode (old -> new replacement in the config text).
_PE = '"The rule holds SPY when the inventories-to-sales ratio from {W.lead_word} months earlier was at or above "'
EVASIONS = {
    "sharpe_one_decimal": ('out-of-sample Sharpe {W.oos_sharpe} versus "', 'out-of-sample Sharpe 0.7 versus "'),
    "number_words": (_PE, _PE.replace("{W.lead_word}", "six")),
    "no_sharpe_word": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                       'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. It returned 0.73 against 0.92 for SPY."'),
    "swapped_strategy_bh": ('f"scores an in-sample Sharpe of {W.median_valid_is_sharpe}. Out of sample it records Sharpe '
                            '{W.oos_sharpe} "\n        f"versus {W.bh_oos_sharpe},',
                            'f"scores an in-sample Sharpe of {W.median_valid_is_sharpe}. Out of sample it records Sharpe '
                            '{W.bh_oos_sharpe} "\n        f"versus {W.oos_sharpe},'),
    "prior_months_reading": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                             'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. It acts on the prior month\'s reading."'),
    "delayed_one_calendar_quarter": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                                     'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. The signal is delayed by one '
                                     'calendar quarter."'),
    "chosen_for_oos_performance": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                                   'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. It was chosen for out-of-sample '
                                   'performance."'),
    "count_168_rules": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                        'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. It is the best of 168 rules."'),
    "stale_drawdown": ('maximum drawdown {W.oos_max_drawdown} versus', 'maximum drawdown -12.0% versus'),
    "stale_return": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                     'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. Its annual return was 9.4%."'),
    # QA_VERIFY_B0r allowlist loopholes: a percentile result outside threshold definitions, a bare 0% / 100%
    "ordinal_percentile_result": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                                  'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. Its score ranks at the 97th '
                                  'percentile of the scrambled contests."'),
    "bare_full_percent": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                          'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. It was right 100% of the time."'),
    "bare_zero_percent": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                          'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. Drawdown was 0% in the test period."'),
    "verdict_word": ('f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise."',
                     'f"{THRESHOLD_TEXT[\'T_roll_median\']}, and holds cash otherwise. This is not a validated edge."'),
}


@pytest.mark.parametrize("name", sorted(EVASIONS))
def test_qa_evasion_fixture_fails_hard_mode(tmp_path, name):
    old, new = EVASIONS[name]
    d = tmp_path / name
    shutil.copytree(REWRITTEN, d)
    cfg = d / "retail_inv_sales_spy_config.py.txt"
    text = cfg.read_text()
    assert text.count(old) == 1, name
    cfg.write_text(text.replace(old, new))
    assert findings(d, hard=True), name


def test_missing_field_placeholder_fails(tmp_path):
    d = tmp_path / "missing"
    shutil.copytree(REWRITTEN, d)
    cfg = d / "retail_inv_sales_spy_config.py.txt"
    cfg.write_text(cfg.read_text().replace("{W.n_valid}", "{W.n_valid_typo}"))
    assert any(r.startswith("MISSING") for r in findings(d, hard=True))


def test_sentence_rules():
    f = {"oos_sharpe": 0.81, "bh_oos_sharpe": 1.0, "is_sharpe": 0.93, "lead": 6, "_lead_unit": "months",
         "n_valid": 504, "n_candidates": 504, "_objective": "max_is_sharpe_lead_plateau_w3", "_legacy_oos_sharpe": [1.55],
         "_legacy_lead": [9], "plateau_leads": [5, 6, 7]}
    ok = ("The rule earns an OOS Sharpe of 0.81 versus 1.00 for buy-and-hold. "
          "It uses the reading from six months earlier. The plateau spans leads 5 to 7 (a 5-month lag also scores well). "
          "Concurrent quartile Sharpe 0.49 is descriptive. The previously published rule (OOS 1.55, 9-month lag) is superseded. "
          "It uses the lagged 3-month change. It is the best of 504 valid combinations. "
          "The signal from two quarters earlier drives it.")
    assert g.check_text(ok, f, "t") == []
    bad = g.check_text("Selection maximized OOS Sharpe (1.55). It waits 9 months. Best of 168 combinations.", f, "t")
    assert {r.split()[0] for r in bad} == {"OBJECTIVE", "SHARPE", "LEAD", "COUNT"}


def test_component_rule_flags_new_pair_branch(tmp_path, monkeypatch):
    app = tmp_path / "app"
    (app / "components").mkdir(parents=True)
    (app / "pair_configs").mkdir()
    (app / "pair_configs_archive").mkdir()
    (app / "pair_configs" / "unrate_spy_config.py").write_text("")
    (tmp_path / "results").mkdir()
    (app / "components" / "panel.py").write_text(
        "NAMES = {'unrate_spy': 'Unemployment'}\n"            # id -> display map: allowed
        "def f(pair_id):\n    if pair_id == 'unrate_spy':\n        return 1\n    return 'unrate' in pair_id\n")
    monkeypatch.setattr(g, "APP", app)
    monkeypatch.setattr(g, "REPO", tmp_path)
    v = g.component_violations()
    snippets = sorted(x["snippet"] for x in v)
    assert "pair_id == 'unrate_spy'" in snippets and "'unrate' in pair_id" in snippets
    assert all(x["line"] != 1 for x in v)


# Codex B0r: numeric literals inside Python expressions reach prose without appearing in authored text.
CODE_EVASIONS = {
    "str_call": 'QA_STALE_PROSE = "The model\'s test score was " + str(0.73) + "."',
    "fstring_format_spec": 'QA_STALE_PROSE = f"Its annual return was {0.094:.1%}."',
    "fstring_int": 'QA_STALE_PROSE = f"The rule consults the observation from {3} calendar months back."',
    "repr_call": 'QA_STALE_PROSE = "Sharpe " + repr(0.73)',
    "percent_format": 'QA_STALE_PROSE = "Out-of-sample Sharpe %.2f" % 0.73',
    "dot_format": 'QA_STALE_PROSE = "Out-of-sample Sharpe {:.2f}".format(0.73)',
    "concatenation_of_constants": 'QA_STALE_PROSE = "Lead L" + str(1 + 2)',
    "named_constant": '_OLD = 0.73\nQA_STALE_PROSE = f"Out-of-sample Sharpe {_OLD}"',
    "unit_constant_only": 'QA_STALE_PROSE = f"It waits {1 * 12} months."',
    "list_index_smuggle": 'QA_STALE_PROSE = f"Sharpe {[0.73][0]}"',
    "format_builtin": 'QA_STALE_PROSE = "Sharpe " + format(0.73, ".2f")',
}


@pytest.mark.parametrize("name", sorted(CODE_EVASIONS))
def test_codex_numeric_literal_evasion_fails_hard_mode(tmp_path, name):
    d = tmp_path / name
    shutil.copytree(REWRITTEN, d)
    cfg = d / "retail_inv_sales_spy_config.py.txt"
    cfg.write_text(cfg.read_text() + "\n" + CODE_EVASIONS[name] + "\n")
    assert any(r.startswith("NUMLIT") for r in findings(d, hard=True)), name


def test_numeric_literal_allowed_contexts(tmp_path):
    d = tmp_path / "allowed"
    shutil.copytree(REWRITTEN, d)
    cfg = d / "retail_inv_sales_spy_config.py.txt"
    cfg.write_text(cfg.read_text() + '''
_ROOT = Path(__file__).resolve().parents[2]
_LAST = sorted([W.value("lead")])[-1]


def _pct(v, nd=1):
    return f"{abs(v) * 100:.{nd}f}%"


_SHARE = _pct(W.value("oos_sharpe"), 0)
THRESHOLD_TEXT = {"T_roll_p75": "its rolling 60-month 75th percentile"}
RULE_ACTION_TEXT = {"P1": "hold 100% SPY when the reading is below the threshold; otherwise exposure from 100% to 0%."}
_POS = W.value("oos_sharpe") > 0
''')
    assert findings(d, hard=True) == []


def test_swapped_compares_buy_and_hold_on_the_same_track_period_and_kind():
    # QA B1 consumer_sentiment: comparison_bh_is_sharpe 0.7092 rounded to the winner's OOS 0.71, so a correct
    # 'X versus Y for buy-and-hold' was flagged; and a value from another track used to count as buy-and-hold
    f = {"oos_sharpe": 0.711528, "bh_oos_sharpe": 0.946184, "is_sharpe": 0.759517, "bh_is_sharpe": 0.62,
         "comparison_oos_sharpe": 0.711528, "comparison_bh_oos_sharpe": 0.95, "comparison_bh_is_sharpe": 0.7092}
    assert g.swapped("Test-period Sharpe 0.71 versus 0.95 for buy-and-hold.", f, "x") == []
    assert g.swapped("Test-period Sharpe 0.95 versus 0.71 for buy-and-hold.", f, "x")          # swapped
    assert g.swapped("Training Sharpe 0.76 versus 0.95 for buy-and-hold.", f, "x")            # IS vs OOS B&H
    assert g.swapped("Training Sharpe 0.76 versus 0.62 for buy-and-hold.", f, "x") == []
    # the reworded form is checked too (QA cs F3), with a deliberately swapped value caught
    assert g.swapped("Test-period Sharpe 0.71 (buy-and-hold SPY: 0.95).", f, "x") == []
    assert g.swapped("Test-period Sharpe 0.95 (buy-and-hold SPY: 0.71).", f, "x")


def test_a_legacy_label_covers_only_its_own_clause():
    # QA EF E1: a sentence-wide legacy scope exempted a later clause claiming a stale published value as current
    f = {"oos_sharpe": 0.385, "lead": 4, "_lead_unit": "months", "_objective": "max_is_sharpe_lead_plateau_w3",
         "_legacy_oos_sharpe": [1.43], "_legacy_lead": []}
    bad = g.check_text("The earlier rule was published at Sharpe 1.43; the current winner earns Sharpe 1.43.", f, "x")
    assert any(b.startswith("SHARPE") for b in bad)
    bad = g.check_text("Previously the winner was selected on out-of-sample Sharpe; the winner is selected on "
                       "out-of-sample Sharpe.", f, "x")
    assert any(b.startswith("OBJECTIVE") for b in bad)
    assert [lg for _c, lg in g._units("The previous rule (published earlier) used lead 1; it scored 0.18.")] == \
        [True, False]


def test_swapped_is_field_bound_when_values_coincide():
    # QA EF E2: X equals a buy-and-hold field AND another strategy field; Y equals that buy-and-hold field's own
    # strategy value -> the swap is still reported
    f = {"oos_sharpe": 0.71, "bh_oos_sharpe": 0.95, "comparison_oos_sharpe": 0.95, "comparison_bh_oos_sharpe": 0.71}
    assert g.swapped("Sharpe 0.95 versus 0.71 for buy-and-hold.", f, "x")
