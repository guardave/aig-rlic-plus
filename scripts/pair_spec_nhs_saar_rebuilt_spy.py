"""Pair spec: New Home Sales, SAAR (HSN1F) x SPY, monthly (Phase B harness).

Signals are functions of the HSN1F level only, so the same code runs on the revised panel and inside every ALFRED
vintage. Signal formulas and threshold families follow the legacy pipeline (git 525922aa, the 20261015 run on the
#255 floored grid L2..L14): six growth / level transforms, constant and rolling 60-month quantile thresholds,
long/cash (P1) only, both orientations, fixed shift(lead) with no extra position shift (position_shift 0).
HSN1F is seasonally adjusted, so no deseasonalising filter is applied (no regime, HMM or smoothing fit).

Legacy = the 20261015 run (commit 525922aa): fixed shift(lead) on month-end stamps, common IS start over all
candidates (no eligibility filter), dropna IS / OOS scoring, raw IS Sharpe argmax (pandas idxmax, manifest order).
The harness replays it on the run's own panel (pinned copy of the ignored data parquet written by that run).
That record was never merged to main: it is the latest committed rule of this pair on the development lineage.
"""
from __future__ import annotations

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "nhs_saar_rebuilt_spy"
SERIES = "HSN1F"
ROLL_WINDOW, ROLL_MIN = 60, 36        # rolling z-score and rolling-quantile thresholds (legacy constants)

SIGNALS = {
    "yoy": "nhs_pct_yoy",
    "pct_6m": "nhs_pct_6m",
    "pct_3m": "nhs_pct_3m",
    "mom": "nhs_mom",
    "zscore_60m": "nhs_zscore_60m",
    "chg_6m": "nhs_6m_chg",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    h = levels["hsn1f"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["hsn1f"] = h
    out["nhs_mom"] = h.pct_change(1, fill_method=None) * 100
    out["nhs_pct_3m"] = h.pct_change(3, fill_method=None) * 100
    out["nhs_pct_6m"] = h.pct_change(6, fill_method=None) * 100
    out["nhs_pct_yoy"] = h.pct_change(12, fill_method=None) * 100
    rm = h.rolling(ROLL_WINDOW, min_periods=ROLL_MIN)
    out["nhs_zscore_60m"] = (h - rm.mean()) / rm.std()
    out["nhs_6m_chg"] = h.diff(6)
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(ROLL_WINDOW, min_periods=ROLL_MIN).quantile(q)


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order."""
    if signal in {"yoy", "pct_6m", "pct_3m", "mom"}:
        return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p25": Rule("raw", None, _roll_q(0.25)),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    if signal == "zscore_60m":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_-0.5": Rule("raw", None, -0.5),
                "T_roll_p25": Rule("raw", None, _roll_q(0.25))}
    return {f"T_roll_p{q}": Rule("raw", None, _roll_q(q / 100)) for q in (25, 50, 75)}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(2, 15)), oos_start="2017-01-31",
    min_is_n=60, position_shift=0, track_policy="compute_twice", release_series=SERIES,
    level_columns=["hsn1f"], features=features, signals=SIGNALS, rules=rules,
    directions=("procyclical", "countercyclical"),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"), vintage_series=SERIES,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first"),
)

SIGNAL_DISPLAY = {
    "yoy": "Year-over-year growth in new home sales",
    "pct_6m": "6-month growth in new home sales",
    "pct_3m": "3-month growth in new home sales",
    "mom": "Month-over-month growth in new home sales",
    "zscore_60m": "60-month new home sales z-score",
    "chg_6m": "6-month change in new home sales (thousands)",
}


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's revised HSN1F (latest pinned ALFRED vintage) on the full monthly grid."""
    return latest_levels(SERIES, "M").rename("hsn1f").to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    p = target_prices()
    return period_grid(p.index.min(), p.index.max(), "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The 20261015 run's own panel (pinned copy of the ignored data/nhs_saar_rebuilt_spy_monthly_latest.parquet
    written by that run, 1993-01..2026-08: HSN1F as downloaded from FRED that day, yfinance SPY) and its returns."""
    df = load_pinned("nhs_saar_rebuilt_spy_monthly_legacy_20261015.csv")
    return df[["hsn1f"]], df["spy_ret"]


LEGACY_TAG = "20261015"
