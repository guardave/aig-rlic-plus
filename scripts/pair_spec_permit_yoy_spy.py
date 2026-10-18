"""Pair spec: Building Permits year-over-year growth (PERMIT) x SPY, monthly (Phase B harness).

The indicator is the year-over-year percent change of US building permits (Census PERMIT, thousands of units,
SAAR). It is a zero-centred growth rate: > 0 means permits are above their level a year earlier. All signals are
functions of the PERMIT level only (YoY first, then transforms of the YoY series), so the same code runs on the
revised panel and inside every ALFRED vintage. Signal formulas, threshold families, the long/cash position rule
and both orientations follow the published pipeline (scripts/pair_pipeline_permit_yoy_spy.py at 1d06839f, run
20261016 on the strict-floor grid L2..L13). permit_spy (the PERMIT level pair) is a separate pair with its own page.

Legacy = that 20261016 run (commit 1d06839f, the latest committed rule of this pair on the development lineage).
It selected its rule by raw IN-SAMPLE Sharpe argmax on a common IS start (latest first-valid return over the whole
grid), NaN returns dropped, IS validity = >= 60 returns, exposure in [0.05, 0.95], sd > 0; positions = fixed
shift(lead) of the revised series with NO extra position shift. LEGACY_SPEC replays exactly that (selection
"is_argmax", is_window "common", position_shift 0) on the run's own panel (pinned copy of the ignored
data/permit_yoy_spy_monthly_latest.parquet that run read and wrote: the YoY growth of the "H Permit" level in
Data Master.xlsx and a yfinance SPY pull). That panel holds the YoY series, not the level, so the legacy reading
frame starts from the YoY column (legacy_features); every transform after the YoY step is the same code. The rule
shown on the main site (d1b68ecd, 2026-09-12: chg_12m / T_roll_p50 / procyclical / L9, OOS Sharpe 1.31) was picked
by the older out-of-sample method on the pre-floor grid; it is the legacy_oos_selected row of the 20261016 record
and is named on the page, not replayed.
"""
from __future__ import annotations

from dataclasses import replace

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "permit_yoy_spy"
SERIES = "PERMIT"
YOY_MONTHS = 12           # months: year-over-year growth window of the permit level
CHG_MONTHS = 12           # months: window of the change-in-growth signal chg_12m
ROLL_WINDOW = 60          # months: rolling z-score window and rolling-percentile thresholds
ROLL_MIN_PERIODS = 24     # readings required before a rolling statistic is defined (published pipeline)

SIGNALS = {
    "level": "permit_yoy_level",
    "diff_1m": "permit_yoy_diff_1m",
    "chg_12m": "permit_yoy_chg_12m",
    "zscore_60m": "permit_yoy_zscore_60m",
}


def _from_yoy(yoy: pd.Series) -> pd.DataFrame:
    """The four tournament signals from the YoY growth series (published formulas)."""
    out = pd.DataFrame(index=yoy.index)
    out["permit_yoy"] = yoy
    out["permit_yoy_level"] = yoy
    out["permit_yoy_diff_1m"] = yoy.diff(1)
    out["permit_yoy_chg_12m"] = yoy.diff(CHG_MONTHS)
    rm = yoy.rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS)
    out["permit_yoy_zscore_60m"] = (yoy - rm.mean()) / rm.std()
    return out


def features(levels: pd.DataFrame) -> pd.DataFrame:
    p = levels["permit"].astype(float)
    out = _from_yoy(100.0 * (p / p.shift(YOY_MONTHS) - 1.0))
    out.insert(0, "permit", p)
    return out


def legacy_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Legacy panel: the YoY growth column is the input (the published panel never stored the level)."""
    return _from_yoy(panel["permit_yoy"].astype(float))


def _roll_q(q: float, window: int = ROLL_WINDOW, min_periods: int = ROLL_MIN_PERIODS):
    return lambda s: s.rolling(window, min_periods=min_periods).quantile(q)


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order (pipeline threshold_codes_for)."""
    if signal == "zscore_60m":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p50": Rule("raw", None, _roll_q(0.50)),
            "T_roll_p75": Rule("raw", None, _roll_q(0.75))}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(2, 14)), oos_start="2017-07-31",
    min_is_n=60, position_shift=0, track_policy="compute_twice", release_series=SERIES,
    level_columns=["permit"], features=features, signals=SIGNALS, rules=rules, strategies=("P1",),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"), vintage_series=SERIES,
)

# Published run: same grid and rules, fixed shift(lead) with no position shift, raw IS argmax on the common IS
# start over ALL candidates, dropna IS and OOS returns, geometric annual return, first-in-order ties.
LEGACY_SPEC = replace(
    SPEC, level_columns=["permit_yoy"], features=legacy_features,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first",
                  ann_return="geometric", round_table=None, selection="is_argmax", is_window="common"),
)
LEGACY_TAG = "20261016"
LEGACY_REPLAY = "is_argmax"          # replayable: the published rule was IS-selected (see module docstring)

SIGNAL_DISPLAY = {
    "level": "Building permits, year-over-year growth",
    "diff_1m": "Building permits YoY growth, 1-month change",
    "chg_12m": "Building permits YoY growth, 12-month change",
    "zscore_60m": "Building permits YoY growth versus its 60-month history (z-score)",
}


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's revised PERMIT (latest pinned ALFRED vintage) on the full monthly grid."""
    return latest_levels(SERIES, "M").rename("permit").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The 20261016 run's own panel (permit YoY from Data Master.xlsx, 1993-01..2025-08; its yfinance SPY pull)
    and its returns."""
    df = load_pinned("permit_yoy_spy_monthly_legacy_20261016.csv")
    return df[["permit_yoy"]], df["spy_ret"]
