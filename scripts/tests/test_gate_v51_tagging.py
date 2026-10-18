"""Gate v5.1: result-type numbers in shared templates are tagged (Lead ruling on the v5 residual)."""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
import gate_number_provenance as g  # noqa: E402
from components import provenance as P  # noqa: E402


@pytest.fixture
def gate(monkeypatch):
    monkeypatch.setenv("AIG_PROVENANCE_GATE", "1")


def test_cross_eval_drawdown_is_tagged_for_a_p2_key(tmp_path, monkeypatch, gate):
    # permit_spy v5: '-18.7%' / '-17.2%' were UNRESOLVED; the cell came from an untagged pd.read_csv (key S5_z|-|P2|..)
    from components import two_track
    (tmp_path / "results" / "toy_spy").mkdir(parents=True)
    pd.DataFrame({"key": ["S5_z|-|P2|procyclical|13", "x|y|P1|procyclical|1"], "max_drawdown": [-0.18689, -0.3]}) \
        .to_csv(tmp_path / "results" / "toy_spy" / "hindsight_tournament_results_20261017.csv", index=False)
    monkeypatch.setattr(two_track, "_REPO", tmp_path)
    monkeypatch.setattr(P, "RESULTS", tmp_path / "results")
    row = two_track._tourn_row("toy_spy", "hindsight_", "20261017", "S5_z|-|P2|procyclical|13")
    cell = two_track._pct(row["max_drawdown"])
    clean, _k, _p, sents, _d = g.parse_markers(cell)
    assert clean == "-18.7%" and len(sents) == 1
    assert g.verify_sentinel(sents[0][2], sents[0][3], sents[0][4], {}, "toy_spy") is None


def test_window_years_and_length_are_tagged(gate):
    w = P.artifact({"window": ["1993-02-28", "2026-09-30"]}, P.RESULTS / "unrate_spy" / "winner_summary.json")
    a, b = P.field_text(w["window"], 0), P.field_text(w["window"], 1)
    text = f"{P.year(a)}-{P.year(b)} ({P.span_years(a, b):.0f} years)"
    clean, _k, _p, sents, _d = g.parse_markers(text)
    assert clean == "1993-2026 (34 years)" and len(sents) == 3
    assert P.kind_of(sents[2][2], "unrate_spy") == "duration"


def test_sidebar_cache_stays_plain_after_a_gate_render(gate):
    from components import sidebar
    t = sidebar._data_through("unrate_spy")
    assert P.S0 in t                                      # tagged on the page
    assert P.S0 not in sidebar._oos_end("unrate_spy")     # the lru_cached value never carries markers


def test_integrity_check_rejects_a_constant_series_and_claims_nothing_about_crises():
    from components import probability_engine_panel as pe
    df = pd.DataFrame({"x": [0.3] * 200}, index=pd.date_range("2005-01-31", periods=200, freq="ME"))
    ok, diag = pe._validate_signal(df, "x", {"threshold_value": 0.5}, {})
    assert not ok and "constant" in diag
    src = Path(pe.__file__).read_text()
    assert "quiet in those crises" not in src and "signal behaved in crises" in src


def test_no_result_number_is_value_matched_on_the_unrate_pilot():
    findings, stats = g.check_pair("unrate_spy")
    assert findings == [] and stats["template_list"] == [], stats["template_list"][:5]


def test_integrity_accepts_a_valid_signal_with_no_stress_extreme_and_names_real_defects():
    # QA pilot-visual M2: a full-history, varying, monotone series was rejected as "constant, truncated or mostly
    # missing"; the check is now a genuine degeneracy test and its message says what failed
    from components import probability_engine_panel as pe
    import numpy as np
    idx = pd.date_range("2000-01-31", periods=300, freq="ME")
    ok, why = pe._validate_signal(pd.DataFrame({"x": np.arange(300.0)}, index=idx), "x", {"threshold_value": 0.5}, {})
    assert ok, why
    gappy = pd.DataFrame({"x": [v if i % 3 == 0 else np.nan for i, v in enumerate(np.arange(300.0))]}, index=idx)
    ok, why = pe._validate_signal(gappy, "x", {"threshold_value": 0.5}, {})
    assert not ok and "mostly missing" in why
    cut = pd.DataFrame({"x": list(np.arange(200.0)) + [np.nan] * 100}, index=idx)
    ok, why = pe._validate_signal(cut, "x", {"threshold_value": 0.5}, {})
    assert not ok and "truncated" in why
