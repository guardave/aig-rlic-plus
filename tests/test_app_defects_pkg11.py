"""Regression tests for pkg11 app defects (rolling-threshold wording, vix None, validity caption,
leaderboard lookback column, plausibility check on binary flags / saturated probabilities)."""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "app"))

from components.rolling_threshold import resolve_threshold, rolling_quantile_spec  # noqa: E402
from components import page_templates as pt  # noqa: E402
from components import probability_engine_panel as pe  # noqa: E402


def _w(pair):
    return json.loads((REPO / "results" / pair / "winner_summary.json").read_text())


@pytest.mark.parametrize("pair,label", [
    ("busloans_spy", "rolling 36-month 25th percentile"),    # LB36, p25 (was "60-month median")
    ("petrol_inv_spy", "rolling 36-month 25th percentile"),
    ("phlxsox_spy", "rolling 63-day 75th percentile"),       # daily LB63
    ("cass_freight_spy", "rolling 60-month 75th percentile"),
    ("sloos_ci_small_spy", "rolling 20-quarter 75th percentile"),
    ("retail_inv_sales_spy", "rolling 60-month median"),
    ("indpro_spy", "rolling 60-month 75th percentile"),      # window only in display name
])
def test_rolling_label_from_artifacts(pair, label):
    assert rolling_quantile_spec(_w(pair))["label"] == label


def test_unknown_window_is_neutral():
    spec = rolling_quantile_spec({"threshold_code": "T2_roll_p25"})
    assert spec["window"] is None and "not recorded" in spec["label"] and "60" not in spec["label"]
    assert rolling_quantile_spec({"threshold_code": "T1_fixed_p50"}) is None


def test_vix_threshold_derived_not_none():
    t = resolve_threshold("vix_vix3m_spy", _w("vix_vix3m_spy"))
    assert t["source"] == "derived" and t["label"] == "trailing 252-day 75th percentile"
    assert abs(t["value"] - 0.4736593) < 1e-5


def test_indpro_threshold_derived_from_pipeline_definition():
    # pipeline: signal.shift(4).rolling(60, min_periods=36).quantile(0.75); reproduces winner_trade_log positions
    t = resolve_threshold("indpro_spy", _w("indpro_spy"))
    assert t["source"] == "derived" and abs(t["value"] - 0.513031) < 1e-5


def test_recorded_value_is_kept_verbatim():
    t = resolve_threshold("busloans_spy", _w("busloans_spy"))
    assert t["source"] == "recorded" and t["raw"] == -0.197


def test_validity_caption_does_not_claim_oos_sharpe_gt_0():
    assert "OOS Sharpe > 0" not in pt._VALID_RULE_TXT


def test_plausibility_accepts_binary_flag_and_saturated_probability():
    idx = pd.date_range("2005-01-31", "2010-12-31", freq="ME")
    flag = pd.DataFrame({"hst_yoy_contraction_flag": (idx.year < 2010).astype(float)}, index=idx)
    ok, why = pe._validate_signal(flag, "hst_yoy_contraction_flag", {"threshold_value": 0.0}, {})
    assert ok, why
    prob = pd.DataFrame({"hmm_2state_prob_stress": [0.0] * (len(idx) - 12) + [1.0] * 12}, index=idx)
    ok, why = pe._validate_signal(prob, "hmm_2state_prob_stress", {"threshold_value": 1.0},
                                  {"known_stress_episodes": [("2005-01-01", "2010-12-31")]})
    assert ok, why


def test_plausibility_still_rejects_flat_probability():
    idx = pd.date_range("2005-01-31", "2010-12-31", freq="ME")
    prob = pd.DataFrame({"hmm_2state_prob_stress": [0.01] * len(idx)}, index=idx)
    ok, _ = pe._validate_signal(prob, "hmm_2state_prob_stress", {"threshold_value": 1.0}, {})
    assert not ok
