"""Pair spec: Unemployment Rate (UNRATE) x SPY, monthly (Phase B harness).

Signals are functions of the level series only, so the same code runs on the revised panel and inside every
ALFRED vintage. Legacy = the published pkg9 pipeline (20261016): fixed shift(lead), common IS start over all
candidates, dropna scoring, raw IS argmax (pandas idxmax, manifest order).
"""
from __future__ import annotations

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "unrate_spy"
SERIES = "UNRATE"

SIGNALS = {
    "level": "unrate",
    "mom": "unrate_mom",
    "chg_3m": "unrate_3m_chg",
    "chg_6m": "unrate_6m_chg",
    "chg_12m": "unrate_12m_chg",
    "zscore_60m": "unrate_zscore_60m",
    "sahm": "unrate_sahm",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    u = levels["unrate"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["unrate"] = u
    out["unrate_mom"] = u.diff(1)
    out["unrate_3m_chg"] = u.diff(3)
    out["unrate_6m_chg"] = u.diff(6)
    out["unrate_12m_chg"] = u.diff(12)
    roll_mean = u.rolling(60, min_periods=36).mean()
    roll_std = u.rolling(60, min_periods=36).std()
    out["unrate_zscore_60m"] = (u - roll_mean) / roll_std
    avg3 = u.rolling(3, min_periods=3).mean()
    out["unrate_sahm"] = avg3 - avg3.rolling(12, min_periods=12).min()
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(60, min_periods=36).quantile(q)


def rules(signal: str) -> dict[str, Rule]:
    roll = {"T_roll_p75": Rule("raw", None, _roll_q(0.75)), "T_roll_p90": Rule("raw", None, _roll_q(0.90))}
    if signal in {"mom", "chg_3m", "chg_6m", "chg_12m"}:
        return {"T0_zero": Rule("raw", None, 0.0), **roll}
    if signal == "zscore_60m":
        return {"T_z_1.0": Rule("raw", None, 1.0), **roll}
    if signal == "sahm":
        return {"T_sahm_0.5": Rule("raw", None, 0.5), **roll}
    return {**roll, "T_roll_p25": Rule("raw", None, _roll_q(0.25))}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(2, 14)), oos_start="2017-01-31",
    min_is_n=60, position_shift=0, track_policy="compute_twice", release_series=SERIES,
    level_columns=["unrate"], features=features, signals=SIGNALS, rules=rules,
    loop_order=("signal", "threshold", "direction", "lead", "strategy"), vintage_series=SERIES,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first"),
)

SIGNAL_DISPLAY = {
    "level": "Unemployment rate level",
    "mom": "Monthly change in unemployment rate",
    "chg_3m": "3-month change in unemployment rate",
    "chg_6m": "6-month change in unemployment rate",
    "chg_12m": "12-month change in unemployment rate",
    "zscore_60m": "60-month unemployment z-score",
    "sahm": "Sahm-style unemployment recession signal",
}


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's revised UNRATE (latest pinned ALFRED vintage) on the full monthly grid."""
    return latest_levels(SERIES, "M").rename("unrate").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The published pipeline's own panel (data/unrate_spy_monthly_latest.parquet, tracked) and its returns."""
    from harness.data import REPO
    df = pd.read_parquet(REPO / "data" / "unrate_spy_monthly_latest.parquet")
    return df[["unrate"]], df["spy_ret"]


LEGACY_TAG = "20261016"
