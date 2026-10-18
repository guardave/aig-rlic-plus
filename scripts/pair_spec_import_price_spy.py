"""Pair spec: BLS Import Price Index, all commodities (IR) x SPY, monthly (Phase B harness).

Signals are functions of the IR level only, so the same code runs on the revised panel and inside every ALFRED
vintage. Signal formulas and threshold families follow the published pipeline (scripts/pair_pipeline_import_price_spy.py
at 1d06839f, the 20261016 strict-floor run on the registry grid L2..L13): six growth transforms of the index
(the level itself is a trending price index and is never traded), constant and rolling 60-month quantile thresholds,
long/cash (P1) only, both orientations, fixed shift(lead) with no extra position shift (position_shift 0).

Legacy = that published 20261016 run. It selected its rule by raw IN-SAMPLE Sharpe argmax on a common IS start
(latest first-valid return over the whole grid), NaN returns dropped, IS validity = >= 60 returns, exposure in
[0.05, 0.95], sd > 0, first-in-order ties (pandas idxmax). The harness replays it on the run's own panel: a pinned
copy of the ignored data/import_price_spy_monthly_latest.parquet that run read (IR level from the tracked
data/Data Master.xlsx sheet "Import Price Index", SPY from yfinance; parquet sha256 2b79a09e...).

Real-time track: ALFRED holds IR vintages from 2010-03-16 only (data/release_calendar/alfred_first_vintage_dates.csv),
so the real-time readings start in 2010 and the real-time training window is short (2010 to the 2016 end of the
training window, less the lead).
"""
from __future__ import annotations

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "import_price_spy"
SERIES = "IR"
ROLL_WINDOW = 60          # months: rolling z-score window and rolling-quantile thresholds (legacy constant)
ROLL_MIN_PERIODS = 36     # readings required before a rolling statistic is defined (legacy constant)

SIGNALS = {
    "yoy": "import_price_yoy",
    "mom": "import_price_mom",
    "chg_3m": "import_price_3m",
    "chg_6m": "import_price_6m",
    "yoy_zscore_60m": "import_price_yoy_zscore_60m",
    "accel": "import_price_accel",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    lvl = levels["import_price"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["import_price"] = lvl
    out["import_price_yoy"] = 100.0 * (lvl / lvl.shift(12) - 1.0)
    out["import_price_mom"] = 100.0 * (lvl / lvl.shift(1) - 1.0)
    out["import_price_3m"] = 100.0 * (lvl / lvl.shift(3) - 1.0)
    out["import_price_6m"] = 100.0 * (lvl / lvl.shift(6) - 1.0)
    rm = out["import_price_yoy"].rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS)
    out["import_price_yoy_zscore_60m"] = (out["import_price_yoy"] - rm.mean()) / rm.std()
    out["import_price_accel"] = out["import_price_yoy"].diff()
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(60, min_periods=36).quantile(q)       # = ROLL_WINDOW, ROLL_MIN_PERIODS


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order (pipeline threshold_codes_for)."""
    if signal == "yoy_zscore_60m":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p25": Rule("raw", None, _roll_q(0.25)),
            "T_roll_p50": Rule("raw", None, _roll_q(0.50))}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(2, 14)), oos_start="2017-01-31",
    min_is_n=60, position_shift=0, track_policy="compute_twice", release_series=SERIES,
    level_columns=["import_price"], features=features, signals=SIGNALS, rules=rules, strategies=("P1",),
    directions=("countercyclical", "procyclical"),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"), vintage_series=SERIES,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first",
                  ann_return="geometric", round_table=None, selection="is_argmax", is_window="common"),
)
LEGACY_TAG = "20261016"
LEGACY_REPLAY = "is_argmax"          # replayable: the published rule was IS-selected (see module docstring)

SIGNAL_DISPLAY = {
    "yoy": "Year-over-year growth in import prices",
    "mom": "Month-over-month growth in import prices",
    "chg_3m": "3-month growth in import prices",
    "chg_6m": "6-month growth in import prices",
    "yoy_zscore_60m": "Year-over-year import-price growth versus its 60-month history (z-score)",
    "accel": "Change in year-over-year import-price growth (acceleration)",
}


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's revised IR (latest pinned ALFRED vintage) on the full monthly grid."""
    return latest_levels(SERIES, "M").rename("import_price").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The published 20261016 run's own panel (1993-01..2025-08: IR from Data Master.xlsx, its yfinance SPY pull)
    and its returns."""
    df = load_pinned("import_price_spy_monthly_legacy_20261016.csv")
    return df[["import_price"]], df["spy_ret"]
