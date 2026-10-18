"""Pair spec: Retail Inventories-to-Sales Ratio (RETAILIRSA) x SPY, monthly (Phase B harness).

Signals are functions of the RETAILIRSA level only, so the same code runs on the revised panel and inside every
ALFRED vintage. Signal formulas and threshold families follow the legacy pipeline (git 1d06839f, the 20261016
strict-floor run on the registry grid L3..L14): the ratio level, its 1-month and 12-month changes and its 60-month
z-score; rolling 60-month quantile and constant thresholds; long/cash (P1) only, both orientations, fixed
shift(lead) with no extra position shift (position_shift 0). The ratio is seasonally adjusted, so no
deseasonalising filter is applied (no regime, HMM or smoothing fit).

Real-time track: the ALFRED archive of RETAILIRSA starts 2013-06-13, so the training window before the test period
(oos_start, the published split) holds fewer rows than min_is_n: MAIN has no eligible candidate and the pair is
shown unranked (track_state rt_insufficient); the revised track is the comparison.

Legacy = the 20261016 run (commit 1d06839f): fixed shift(lead) on month-end stamps, common IS start over all
candidates (no eligibility filter), dropna IS / OOS scoring, raw IS Sharpe argmax (pandas idxmax, manifest order),
test period from 2017-06-30. The harness replays it on the run's own panel (pinned copy of the ignored data parquet
written by that run: the ratio from Data Master.xlsx, identical to the ALFRED vintage of 2025-09-16, and yfinance SPY).
"""
from __future__ import annotations

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "retail_inv_sales_spy"
SERIES = "RETAILIRSA"
ROLL_WINDOW = 60                      # rolling z-score and rolling-quantile window, months (legacy constant)
ROLL_MIN = 24                         # minimum readings in that window (legacy constant)

SIGNALS = {
    "level": "invsales_level",
    "diff_1m": "invsales_diff_1m",
    "chg_12m": "invsales_chg_12m",
    "zscore_60m": "invsales_zscore_60m",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    x = levels["invsales"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["invsales"] = x
    out["invsales_level"] = x
    out["invsales_diff_1m"] = x.diff(1)
    out["invsales_chg_12m"] = x.diff(12)
    rm = x.rolling(ROLL_WINDOW, min_periods=ROLL_MIN)
    out["invsales_zscore_60m"] = (x - rm.mean()) / rm.std()
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(60, min_periods=24).quantile(q)       # = ROLL_WINDOW, ROLL_MIN


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order."""
    if signal in {"diff_1m", "chg_12m"}:
        return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p50": Rule("raw", None, _roll_q(0.50)),
                "T_roll_p75": Rule("raw", None, _roll_q(0.75))}
    if signal == "zscore_60m":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {f"T_roll_p{q}": Rule("raw", None, _roll_q(q / 100)) for q in (25, 50, 75)}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(3, 15)), oos_start="2017-06-30",
    min_is_n=60, position_shift=0, track_policy="compute_twice", release_series=SERIES,
    level_columns=["invsales"], features=features, signals=SIGNALS, rules=rules,
    directions=("countercyclical", "procyclical"),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"), vintage_series=SERIES,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first"),
)

SIGNAL_DISPLAY = {
    "level": "Retail inventories-to-sales ratio (level)",
    "diff_1m": "Month-on-month change in the ratio",
    "chg_12m": "12-month change in the ratio",
    "zscore_60m": "Ratio versus its five-year history (z-score)",
}


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's revised RETAILIRSA (latest pinned ALFRED vintage) on the full monthly grid."""
    return latest_levels(SERIES, "M").rename("invsales").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The 20261016 run's own panel (pinned copy of the ignored data/retail_inv_sales_spy_monthly_latest.parquet
    written by that run, 1993-01..2025-07: the ratio from Data Master.xlsx, yfinance SPY) and its returns."""
    df = load_pinned("retail_inv_sales_spy_monthly_legacy_20261016.csv")
    return df[["invsales"]], df["spy_ret"]


LEGACY_TAG = "20261016"
