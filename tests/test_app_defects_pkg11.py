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


# ---- follow-up (QA_VERIFY issues 3-5) ----
def _monthly_panel(values_fn):
    idx = pd.date_range("2000-01-31", "2024-12-31", freq="ME")
    return pd.DataFrame({"hmm_2state_prob_stress": [values_fn(d) for d in idx]}, index=idx)


def test_validate_signal_rejects_constant_all_one_flag():
    idx = pd.date_range("2000-01-31", "2024-12-31", freq="ME")
    flag = pd.DataFrame({"hst_yoy_contraction_flag": 1.0}, index=idx)
    ok, why = pe._validate_signal(flag, "hst_yoy_contraction_flag", {"threshold_value": 0.0}, {})
    assert not ok and "constant" in why


def test_validate_signal_rejects_constant_high_probability_threshold_ge_1():
    prob = _monthly_panel(lambda d: 0.6)
    ok, why = pe._validate_signal(prob, "hmm_2state_prob_stress", {"threshold_value": 1.0}, {})
    assert not ok and "constant" in why


def test_validate_signal_rejects_saturated_nonconstant_probability_threshold_ge_1():
    prob = _monthly_panel(lambda d: 0.9 if d.month % 2 else 1.0)  # never leaves the high regime
    ok, _ = pe._validate_signal(prob, "hmm_2state_prob_stress", {"threshold_value": 1.0}, {})
    assert not ok


def test_validate_signal_still_accepts_real_panels():
    for pair, col in (("eci_total_comp_spy", None), ("housing_starts_rebuilt_spy", None)):
        d = REPO / "results" / pair
        f = sorted(d.glob("signals_*.parquet"))[-1]
        df = pd.read_parquet(f)
        ws = _w(pair)
        col = ws.get("signal_column") or ws.get("signal_col")
        if col is None or col not in df.columns:
            import glob  # fall back to the app's own column resolution
            col = next(c for c in df.columns if "hmm" in c or "flag" in c)
        ok, why = pe._validate_signal(df, col, ws, {})
        assert ok, (pair, col, why)


def test_evidence_status_no_invented_text_and_block_names_kept():
    sys.path.insert(0, str(REPO / "scripts"))
    import evidence_status_util as esu
    legacy = {"pair_id": "x_spy", "generated_at": "2026-10-08T00:00:00Z", "generated_by": "evan",
              "blocks": {"correlations": "ready", "era_correlations": "ready", "winner_summary": "ready"},
              "caveats": ["OOS short"]}
    note = esu.to_v12(legacy)["technical_note"]
    assert "holdout" not in note and "final exam" not in note
    assert "correlations=ready" in note and "era_correlations=ready" in note and "winner_summary=ready" in note
    assert "3/3" not in note and "OOS short" in note


def test_complete_months_last_calendar_day_partial_month_dropped():
    sys.path.insert(0, str(REPO / "scripts"))
    from month_completeness import complete_months
    days = pd.bdate_range("2026-08-01", "2026-10-30")      # data stops Fri 2026-10-30
    s = pd.Series(1.0, index=days).resample("ME").last()
    # 2026-10-31 is a Saturday: last business day = Fri 10-30 -> Oct is complete
    assert list(complete_months(s, days.max()).index.month) == [8, 9, 10]
    # run on the last calendar day of a month with data only to the prior business day: partial
    days2 = pd.bdate_range("2026-08-01", "2026-09-29")
    s2 = pd.Series(1.0, index=days2).resample("ME").last()
    assert list(complete_months(s2, days2.max()).index.month) == [8]
    # data ending mid-month
    days3 = pd.bdate_range("2026-08-01", "2026-10-09")
    s3 = pd.Series(1.0, index=days3).resample("ME").last()
    assert list(complete_months(s3, days3.max()).index.month) == [8, 9]


def test_complete_months_holiday_month_end():
    sys.path.insert(0, str(REPO / "scripts"))
    from month_completeness import last_business_day
    assert last_business_day(pd.Timestamp("2027-05-31")) == pd.Timestamp("2027-05-28")  # Memorial Day
    assert last_business_day(pd.Timestamp("2018-03-31")) == pd.Timestamp("2018-03-29")  # Good Friday 3/30
