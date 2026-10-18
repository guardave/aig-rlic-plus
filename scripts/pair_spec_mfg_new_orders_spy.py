"""Pair spec: core capital goods orders (FRED NEWORDER) x SPY, monthly (Phase B harness).

NEWORDER = manufacturers' new orders, nondefense capital goods excluding aircraft ("core capital goods orders",
nominal $ millions, SA). It is NOT Census M3 total manufacturing new orders (AMTMNO); the `mfg_new_orders*`
column names are legacy labels kept from the published pipeline. The level trends, so every signal is a growth
transform of the level; signals are functions of the NEWORDER level only, so the same code runs on the revised
panel and inside every ALFRED vintage. Signal formulas, threshold families, the long/cash position rule and both
orientations follow the published pipeline (scripts/pair_pipeline_mfg_new_orders_spy.py at 1d06839f, run
20261016 on the strict-floor grid L3..L14).

Legacy = that 20261016 run (commit 1d06839f, the latest committed rule of this pair on the development lineage).
It selected its rule by raw IN-SAMPLE Sharpe argmax on a common IS start (latest first-valid return over the whole
grid), NaN returns dropped, IS validity = >= 60 returns, exposure in [0.05, 0.95], sd > 0; positions = fixed
shift(lead) of the revised series with NO extra position shift. LEGACY_SPEC replays exactly that (selection
"is_argmax", is_window "common", position_shift 0) on the run's own panel (pinned copy of the ignored
data/mfg_new_orders_spy_monthly_latest.parquet that run read and wrote, sha256 3ee384ff...: NEWORDER from
Data Master.xlsx, yfinance SPY). The rule shown on the main site (c1797488, 2026-08-29: yoy / T_roll_p50 /
countercyclical / L12, OOS Sharpe 1.56) was picked by the older out-of-sample method on the pre-floor grid; it is
the legacy_oos_selected row of the 20261016 record and is named on the page, not replayed.
"""
from __future__ import annotations

from dataclasses import replace

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "mfg_new_orders_spy"
SERIES = "NEWORDER"
ROLL_WINDOW = 60          # months: rolling z-score window of the YoY growth and rolling-percentile thresholds
ROLL_MIN_PERIODS = 36     # readings required before a rolling statistic is defined

SIGNALS = {
    "yoy": "mfg_new_orders_yoy",
    "mom": "mfg_new_orders_mom",
    "chg_3m": "mfg_new_orders_3m",
    "chg_6m": "mfg_new_orders_6m",
    "yoy_zscore_60m": "mfg_new_orders_yoy_zscore_60m",
    "accel": "mfg_new_orders_accel",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    x = levels["mfg_new_orders"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["mfg_new_orders"] = x
    out["mfg_new_orders_yoy"] = 100.0 * (x / x.shift(12) - 1.0)
    out["mfg_new_orders_mom"] = 100.0 * (x / x.shift(1) - 1.0)
    out["mfg_new_orders_3m"] = 100.0 * (x / x.shift(3) - 1.0)
    out["mfg_new_orders_6m"] = 100.0 * (x / x.shift(6) - 1.0)
    yoy = out["mfg_new_orders_yoy"]
    rm = yoy.rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS)
    out["mfg_new_orders_yoy_zscore_60m"] = (yoy - rm.mean()) / rm.std()
    out["mfg_new_orders_accel"] = yoy.diff()
    return out


def _roll_q(q: float, window: int = ROLL_WINDOW, min_periods: int = ROLL_MIN_PERIODS):
    return lambda s: s.rolling(window, min_periods=min_periods).quantile(q)


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order (pipeline threshold_codes_for)."""
    if signal in {"yoy", "mom", "chg_3m", "chg_6m", "accel"}:
        return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p25": Rule("raw", None, _roll_q(0.25)),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    if signal == "yoy_zscore_60m":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {f"T_roll_p{p}": Rule("raw", None, _roll_q(p / 100)) for p in (25, 50, 75)}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(3, 15)), oos_start="2017-01-31",
    min_is_n=60, position_shift=0, track_policy="compute_twice", release_series=SERIES,
    level_columns=["mfg_new_orders"], features=features, signals=SIGNALS, rules=rules, strategies=("P1",),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"), vintage_series=SERIES,
)

# Published run: same grid and rules, fixed shift(lead) with no position shift, raw IS argmax on the common IS
# start over ALL candidates, dropna IS and OOS returns, geometric annual return, first-in-order ties.
LEGACY_SPEC = replace(
    SPEC,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first",
                  ann_return="geometric", round_table=None, selection="is_argmax", is_window="common"),
)
LEGACY_TAG = "20261016"
LEGACY_REPLAY = "is_argmax"          # replayable: the published rule was IS-selected (see module docstring)

SIGNAL_DISPLAY = {
    "yoy": "Core capital goods orders, year-over-year growth",
    "mom": "Core capital goods orders, month-over-month growth",
    "chg_3m": "Core capital goods orders, 3-month growth",
    "chg_6m": "Core capital goods orders, 6-month growth",
    "yoy_zscore_60m": "Core capital goods orders YoY growth versus its 60-month history (z-score)",
    "accel": "Core capital goods orders growth acceleration (change in YoY growth)",
}


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's revised NEWORDER (latest pinned ALFRED vintage) on the full monthly grid."""
    return latest_levels(SERIES, "M").rename("mfg_new_orders").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The 20261016 run's own panel (NEWORDER from Data Master.xlsx, 1993-01..2025-08; its yfinance SPY pull)
    and its returns."""
    df = load_pinned("mfg_new_orders_spy_monthly_legacy_20261016.csv")
    return df[["mfg_new_orders"]], df["spy_ret"]
