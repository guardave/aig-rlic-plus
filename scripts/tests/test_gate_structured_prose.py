"""Tests for scripts/gate_structured_prose.py (Phase B structured-prose hard gate, plan section 4 item 7)."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gate_structured_prose as g  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "structured_prose"
RETAIL = FIX / "retail_inv_sales_spy_8198187b"        # config + winner_summary at int @8198187b (QA_VERIFY_int)
REWRITTEN = FIX / "retail_inv_sales_spy_rewritten"


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
    assert res and all(r.startswith("HANDTYPED") for r in res)


def test_missing_field_placeholder_fails(tmp_path):
    d = tmp_path / "missing"
    shutil.copytree(REWRITTEN, d)
    cfg = d / "retail_inv_sales_spy_config.py.txt"
    cfg.write_text(cfg.read_text().replace("{W.n_valid}", "{W.n_valid_typo}"))
    assert any(r.startswith("MISSING") for r in findings(d, hard=True))


def test_sentence_rules():
    f = {"oos_sharpe": 0.81, "bh_oos_sharpe": 1.0, "is_sharpe": 0.93, "lead": 6, "_lead_unit": "months",
         "n_valid": 504, "n_candidates": 504, "_objective": "max_is_sharpe_lead_plateau_w3", "_legacy_oos_sharpe": 1.55,
         "_legacy_lead": 9, "plateau_leads": [5, 6, 7]}
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
