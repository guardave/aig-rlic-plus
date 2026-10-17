"""Pair spec: Credit Card Delinquency Rate (DRCCLACBN, not seasonally adjusted) x SPY, quarterly (Phase B).

Legacy = the published pkg9 pipeline (20261016) on the Data Master panel (1993Q1-2025Q2, identical to the latest
ALFRED vintage on every common quarter). The OOS start 2017-09-30 is kept from the published run; it was set by
the old `work.index[-oos_n]` rule on that panel and is now fixed so a longer panel does not move it.
"""
from __future__ import annotations

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "cc_delinquency_spy"
SERIES = "DRCCLACBN"

SIGNALS = {
    "level": "ccdelinq_level",
    "diff_1q": "ccdelinq_diff_1q",
    "chg_4q": "ccdelinq_chg_4q",
    "zscore_20q": "ccdelinq_zscore_20q",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    lvl = levels["ccdelinq"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["ccdelinq_level"] = lvl
    out["ccdelinq_diff_1q"] = lvl.diff(1)
    out["ccdelinq_chg_4q"] = lvl.diff(4)
    out["ccdelinq_zscore_20q"] = (lvl - lvl.rolling(20, min_periods=12).mean()) / lvl.rolling(20, min_periods=12).std()
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(20, min_periods=12).quantile(q)


def rules(signal: str) -> dict[str, Rule]:
    if signal == "zscore_20q":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p50": Rule("raw", None, _roll_q(0.50)),
            "T_roll_p75": Rule("raw", None, _roll_q(0.75))}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="Q", lead_unit="quarters", leads=[2, 3, 4, 5], oos_start="2017-09-30",
    min_is_n=20, position_shift=0, track_policy="compute_twice", release_series=SERIES,
    level_columns=["ccdelinq"], features=features, signals=SIGNALS, rules=rules,
    loop_order=("signal", "threshold", "direction", "lead", "strategy"), vintage_series=SERIES,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first"),
)

SIGNAL_DISPLAY = {
    "level": "Credit-card delinquency rate (level)",
    "diff_1q": "Quarter-on-quarter change",
    "chg_4q": "4-quarter change",
    "zscore_20q": "Level vs 5-year history (z-score)",
}


def target_prices() -> pd.Series:
    """SPY quarter-end closes = the month-end close of each quarter's last month (pinned monthly series)."""
    m = load_pinned("spy_month_end_20261017.csv")["spy_close"]
    return m[m.index.month % 3 == 0]


def revised_levels() -> pd.DataFrame:
    return latest_levels(SERIES, "Q").rename("ccdelinq").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "Q")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    df = load_pinned("cc_delinquency_spy_quarterly_legacy_20261016.csv")
    return df[["ccdelinq"]], df["spy_ret"]


LEGACY_TAG = "20261016"
