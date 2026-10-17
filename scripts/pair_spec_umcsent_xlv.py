"""Pair spec: University of Michigan Consumer Sentiment (UMCSENT) x XLV, monthly (Phase B harness).

Signals are functions of the level series only, so the same code runs on the revised panel and inside every
ALFRED vintage. Expected direction (prior kept from the published design): procyclical only.

Legacy = the published 20261008 pipeline (#255 floored grid L1..L13, position.shift(1)). It is NOT an IS-argmax
pipeline: it picked the max OOS Sharpe among rows with OOS Sharpe > 0 and full-history turnover < 24, scored IS
per candidate on its own dropna window and held undefined P1 / P3 positions as cash / short. The harness legacy
replay (raw IS argmax on a common IS start) therefore reproduces the published OOS columns and the published
winner's returns but not its selection; see the replay note in the pipeline (acceptance 4.1).
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import ISQuantile, Legacy, PairSpec, Rule

PAIR_ID = "umcsent_xlv"
SERIES = "UMCSENT"

SIGNALS = {
    "S1_level": "umcsent",
    "S2_yoy": "umcsent_yoy",
    "S3_mom": "umcsent_mom",
    "S4_zscore": "umcsent_zscore",
    "S5_3m_ma": "umcsent_3m_ma",
    "S6_direction": "umcsent_direction",
    "S7_dev_ma": "umcsent_dev_ma",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    u = levels["umcsent"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["umcsent"] = u
    out["umcsent_yoy"] = (u / u.shift(12) - 1) * 100
    out["umcsent_mom"] = (u / u.shift(1) - 1) * 100
    rm = u.rolling(36, min_periods=24)
    out["umcsent_zscore"] = (u - rm.mean()) / rm.std()
    out["umcsent_3m_ma"] = u.rolling(3, min_periods=2).mean()
    out["umcsent_direction"] = np.sign(out["umcsent_mom"])
    out["umcsent_dev_ma"] = u - out["umcsent_3m_ma"]
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(60, min_periods=36).quantile(q)


def _roll_z(k: float):
    return lambda s: s.rolling(60, min_periods=36).mean() + k * s.rolling(60, min_periods=36).std()


def _rules(signal: str, is_quantile_min_periods: int) -> dict[str, Rule]:
    """Published threshold families in the published order: IS-fixed quantiles, rolling 60-month quantiles,
    rolling mean +/- k standard deviations, and zero for the change signals."""
    out: dict[str, Rule] = {}
    for p in (25, 50, 75):
        out[f"T1_fixed_p{p}"] = Rule("raw", None, ISQuantile(p / 100, is_quantile_min_periods))
    for p in (25, 50, 75):
        out[f"T2_roll_p{p}"] = Rule("raw", None, _roll_q(p / 100))
    for k in (1.0, 1.5, 2.0):
        out[f"T3_zscore_{k}"] = Rule("raw", None, _roll_z(k))
        out[f"T3_zscore_neg_{k}"] = Rule("raw", None, _roll_z(-k))
    if signal in ("S2_yoy", "S3_mom", "S7_dev_ma"):
        out["T4_zero"] = Rule("raw", None, 0.0)
    return out


def rules(signal: str) -> dict[str, Rule]:
    # Phase B: IS-fixed quantiles are expanding over IS readings, warm-up 36 readings (the rolling families' minimum)
    return _rules(signal, 36)


def _legacy_rules(signal: str) -> dict[str, Rule]:
    return _rules(signal, 1)


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(1, 14)), oos_start="2019-04-30",
    min_is_n=60, position_shift=1, track_policy="compute_twice", release_series=SERIES,
    level_columns=["umcsent"], features=features, signals=SIGNALS, rules=rules, strategies=("P1", "P2", "P3"),
    directions=("procyclical",), strict_counter=True, binary_signals=frozenset({"S6_direction"}), p2_window=(60, 36),
    loop_order=("signal", "lead", "threshold", "strategy", "direction"), vintage_series=SERIES,
)

# Published manifest: P2 repeated per threshold and allowed on the ternary direction flag; IS >= 24 returns;
# no exposure filter; dropna IS, cash-filled (deployable) OOS; arithmetic annual return; table rounded to 4 dp.
LEGACY_SPEC = replace(
    SPEC, min_is_n=24, rules=_legacy_rules, binary_signals=frozenset(), exposure_bounds=(-10.0, 10.0),
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="deployable", tie_break="first",
                  p2_per_threshold=True, ann_return="arithmetic", round_table=4, is_quantile="full",
                  selection="max_oos_valid", is_window="own_dropna"),
)

SIGNAL_DISPLAY = {
    "S1_level": "Consumer sentiment level",
    "S2_yoy": "Year-over-year % change in consumer sentiment",
    "S3_mom": "Month-over-month % change in consumer sentiment",
    "S4_zscore": "36-month consumer sentiment z-score",
    "S5_3m_ma": "3-month average of consumer sentiment",
    "S6_direction": "Direction of the monthly sentiment change",
    "S7_dev_ma": "Consumer sentiment minus its 3-month average",
}


def target_prices() -> pd.Series:
    return load_pinned("xlv_month_end_20261017.csv")["xlv_close"]


def revised_levels() -> pd.DataFrame:
    """Today's revised UMCSENT (latest pinned ALFRED vintage) on the full monthly grid."""
    return latest_levels(SERIES, "M").rename("umcsent").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The published 20261008 pipeline's own panel (pinned copy of the ignored
    data/umcsent_xlv_monthly_19980101_20251231.parquet written by that run) and its XLV returns."""
    df = load_pinned("umcsent_xlv_monthly_legacy_20261008.csv")
    return df[["umcsent"]], df["xlv_ret"]


LEGACY_TAG = "20261008"
