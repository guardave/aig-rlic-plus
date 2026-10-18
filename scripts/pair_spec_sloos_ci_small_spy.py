"""Pair spec: SLOOS C&I lending standards, net % of banks tightening to large and middle-market firms (DRTSCILM)
x SPY, quarterly (Phase B harness).

The data is DRTSCILM (large and middle-market firms), not the small-firm series DRTSCIS that the pair id names
(registry note pkg12 Q8; the id is kept for stability). Signals are functions of the level only, so the same code
runs on the revised panel and inside every ALFRED vintage (archive from 2010-04). The survey is published inside
the quarter it is stamped to (early Feb / May / Aug / Nov), so L1 with position_shift 0 respects the strict floor.

Legacy = the published 20261015 pipeline (GH #251/#268: raw in-sample Sharpe argmax on a common IS start, #255
floored grid L1..L5, fixed shift(lead), dropna scoring, deployable strategy_returns) on the Data Master panel
(identical to the latest ALFRED vintage on every common quarter). It is an IS-argmax pipeline, so the harness
legacy replay applies (selection="is_argmax"). The OOS start 2017-12-31 is kept from the published run; it was set
by the old `work.index[-oos_n]` rule on that panel and is now fixed so a longer panel does not move it.
"""
from __future__ import annotations

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "sloos_ci_small_spy"
SERIES = "DRTSCILM"

SIGNALS = {
    "level": "sloos_level",
    "diff_1q": "sloos_diff_1q",
    "chg_4q": "sloos_chg_4q",
    "zscore_20q": "sloos_zscore_20q",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    lvl = levels["sloos"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["sloos_level"] = lvl
    out["sloos_diff_1q"] = lvl.diff(1)
    out["sloos_chg_4q"] = lvl.diff(4)
    roll = lvl.rolling(20, min_periods=12)                 # 20 quarters (5 years), at least 12 readings
    out["sloos_zscore_20q"] = (lvl - roll.mean()) / roll.std()
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(20, min_periods=12).quantile(q)    # rolling 20-quarter quantile, >= 12 readings


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order (legacy threshold_codes_for)."""
    if signal == "zscore_20q":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p50": Rule("raw", None, _roll_q(0.50)),
            "T_roll_p75": Rule("raw", None, _roll_q(0.75))}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="Q", lead_unit="quarters", leads=[1, 2, 3, 4, 5], oos_start="2017-12-31",
    min_is_n=20, position_shift=0, track_policy="compute_twice", release_series=SERIES,
    level_columns=["sloos"], features=features, signals=SIGNALS, rules=rules,
    loop_order=("signal", "threshold", "direction", "lead", "strategy"), vintage_series=SERIES,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first",
                  selection="is_argmax", is_window="common"),
)

SIGNAL_DISPLAY = {
    "level": "SLOOS net % tightening (level)",
    "diff_1q": "Quarterly change in net tightening",
    "chg_4q": "4-quarter change in net tightening",
    "zscore_20q": "Net tightening vs its 5-year history (z-score)",
}


def target_prices() -> pd.Series:
    """SPY quarter-end closes = the month-end close of each quarter's last month (pinned monthly series)."""
    m = load_pinned("spy_month_end_20261017.csv")["spy_close"]
    return m[m.index.month % 3 == 0]


def revised_levels() -> pd.DataFrame:
    """Today's revised DRTSCILM (latest pinned ALFRED vintage) on the full quarterly grid."""
    return latest_levels(SERIES, "Q").rename("sloos").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "Q")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The published 20261015 pipeline's own panel (pinned copy of the ignored
    data/sloos_ci_small_spy_quarterly_latest.parquet written by that run) and its SPY returns."""
    df = load_pinned("sloos_ci_small_spy_quarterly_legacy_20261015.csv")
    return df[["sloos"]], df["spy_ret"]


LEGACY_TAG = "20261015"
