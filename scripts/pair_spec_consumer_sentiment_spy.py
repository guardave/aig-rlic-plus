"""Pair spec: U. Michigan headline Consumer Sentiment (UMCSENT) x SPY, monthly (Phase B harness).

Signals are functions of the UMCSENT level only, so the same code runs on the revised panel and inside every
ALFRED vintage. Signal formulas, threshold families, the long/cash position rule and both orientations follow the
published pipeline (scripts/pair_pipeline_consumer_sentiment_spy.py at 3433194c, run 20261015).

Legacy = that published 20261015 run. It selected its rule by raw IN-SAMPLE Sharpe argmax on a common IS start
(latest first-valid return over the whole grid), NaN returns dropped, IS validity = >= 60 returns, exposure in
[0.05, 0.95], sd > 0; positions = fixed shift(lead) of the revised series with NO extra position shift (the
position of row t earns the return of row t). LEGACY_SPEC replays exactly that (Legacy.selection "is_argmax",
is_window "common", position_shift 0) on the run's own panel (pinned copy of the ignored
data/consumer_sentiment_spy_monthly_latest.parquet written by that run, sha256 0b7e78fc...).
"""
from __future__ import annotations

from dataclasses import replace

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "consumer_sentiment_spy"
SERIES = "UMCSENT"
ROLL_WINDOW = 60          # months: rolling z-score window and rolling-percentile thresholds
ROLL_MIN_PERIODS = 24     # readings required before a rolling statistic is defined

SIGNALS = {
    "level": "umcsent_level",
    "diff_1m": "umcsent_diff_1m",
    "chg_12m": "umcsent_chg_12m",
    "zscore_60m": "umcsent_zscore_60m",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    u = levels["umcsent"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["umcsent_level"] = u
    out["umcsent_diff_1m"] = u.diff(1)
    out["umcsent_chg_12m"] = u.diff(12)
    rm = u.rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS)
    out["umcsent_zscore_60m"] = (u - rm.mean()) / rm.std()
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS).quantile(q)


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order (pipeline threshold_codes_for)."""
    if signal in ("diff_1m", "chg_12m"):
        return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p50": Rule("raw", None, _roll_q(0.50)),
                "T_roll_p75": Rule("raw", None, _roll_q(0.75))}
    if signal == "zscore_60m":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {f"T_roll_p{p}": Rule("raw", None, _roll_q(p / 100)) for p in (25, 50, 75)}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(1, 14)), oos_start="2018-04-30",
    min_is_n=60, position_shift=1, track_policy="compute_twice", release_series=SERIES,
    level_columns=["umcsent"], features=features, signals=SIGNALS, rules=rules, strategies=("P1",),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"), vintage_series=SERIES,
)

# Published run: same grid and rules, fixed shift(lead) with no position shift, raw IS argmax on the common IS
# start over ALL candidates, dropna IS and OOS returns, geometric annual return, first-in-order ties.
LEGACY_SPEC = replace(
    SPEC, position_shift=0,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first",
                  ann_return="geometric", round_table=None, selection="is_argmax", is_window="common"),
)
LEGACY_TAG = "20261015"
LEGACY_REPLAY = "is_argmax"          # replayable: the published rule was IS-selected (see module docstring)

SIGNAL_DISPLAY = {
    "level": "Consumer sentiment level",
    "diff_1m": "Month-on-month change in consumer sentiment",
    "chg_12m": "12-month change in consumer sentiment",
    "zscore_60m": "Consumer sentiment versus its 60-month history (z-score)",
}


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's revised UMCSENT (latest pinned ALFRED vintage) on the full monthly grid."""
    return latest_levels(SERIES, "M").rename("umcsent").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The published 20261015 run's own panel (UMCSENT as downloaded on 2026-10-15, its SPY pull) and returns."""
    df = load_pinned("consumer_sentiment_spy_monthly_legacy_20261015.csv")
    return df[["umcsent"]], df["spy_ret"]
