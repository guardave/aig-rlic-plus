"""Regression tests for shared app components (pkg8 QA findings H1/M1/L1)."""
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "app"))

from components.rolling_threshold import latest_rolling_value, rolling_pct_spec  # noqa: E402
from components import page_templates as pt  # noqa: E402


def _w(pair):
    return json.loads((REPO / "results" / pair / "winner_summary.json").read_text())


def test_rolling_window_comes_from_artifacts():
    # hy_ig_spy's Phase B winner is a T1 rule; the recorded-window path is checked on a T2 record of its shape
    assert rolling_pct_spec({"threshold_code": "T2_rp75", "threshold_window_days": 504})["window"] == 504
    assert rolling_pct_spec(_w("vix_vix3m_spy"))["window"] == 252


def test_rolling_window_unknown_is_neutral_not_guessed():
    w = {"threshold_code": "T2_rp75", "threshold_display_name": "75th percentile (rolling)"}
    spec = rolling_pct_spec(w)
    assert spec["window"] is None and "504" not in spec["label"] and "252" not in spec["label"]
    assert latest_rolling_value(pd.Series(range(1000), dtype=float), spec, 0) is None


def test_window_parsed_from_note_when_field_absent():
    w = {"threshold_code": "T2_rp75", "threshold_note": "Moving boundary: trailing-504-day 75th percentile"}
    assert rolling_pct_spec(w)["window"] == 504
    assert rolling_pct_spec({"threshold_code": "T1_p75"}) is None


def test_published_winner_located_in_every_pair():
    for f in sorted((REPO / "results").glob("*/winner_summary.json")):
        w = json.loads(f.read_text())
        if not (w.get("selection") or {}).get("raw_winner_row"):
            continue
        t = pt._latest_dated_file(f.parent.name, "tournament_results")
        if t is None:
            continue
        tdf = pd.read_csv(t)
        idx = pt._locate_winner_row(tdf, w)
        assert idx is not None, f.parent.name
        assert abs(float(tdf.loc[idx, "oos_sharpe"]) - float(w["oos_sharpe"])) <= 0.01


def test_benchmark_metric_falls_back_to_tournament_benchmark_row():
    for pair, expect in (("indpro_spy", 0.148), ("vix_vix3m_spy", 0.1569)):
        v = pt._benchmark_metric(pair, _w(pair), "bh_ann_return", "oos_ann_return")
        assert abs(v - expect) < 1e-6
    assert pt._vs_bh_clause("N/A", "SPY") == ""
