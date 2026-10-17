"""Pair spec: Building Permits (PERMIT) x SPY, monthly (Phase B harness).

Signals are functions of the PERMIT level only, so the same code runs on the revised panel and inside every
ALFRED vintage. Signal formulas and threshold families follow the legacy pipeline (git c64a609a); the binary
contraction flag gets one flag threshold (0.5) instead of quantiles of a 0/1 series.

Legacy: NOT replayable through the harness (LEGACY_REPLAY = None). The published rule (winner_summary 1.1.0,
S3_mom / T1_p25 / P3 / L6, OOS Sharpe 1.4454) was selected by the OLD OOS method on tournament_results_20260314.csv
and no strategy_returns file was ever written. Acceptance 4.1 is met by the verbatim legacy-code reproduction
(scripts/legacy_repro/permit_spy.py -> results/permit_spy/legacy_reproduction_20260314.json).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from harness.data import latest_levels, load_pinned, period_grid, target_returns
from harness.spec import ISQuantile, PairSpec, Rule

PAIR_ID = "permit_spy"
SERIES = "PERMIT"
REPO = Path(__file__).resolve().parents[1]

SIGNALS = {
    "S1_level": "permit",
    "S2_yoy": "permit_yoy",
    "S3_mom": "permit_mom",
    "S4_dev": "permit_dev_trend",
    "S5_z": "permit_zscore_60m",
    "S6_mom3m": "permit_mom_3m",
    "S7_mom6m": "permit_mom_6m",
    "S8_accel": "permit_accel",
    "S9_contr": "permit_contraction",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    p = levels["permit"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["permit"] = p
    out["permit_yoy"] = (p / p.shift(12) - 1) * 100
    out["permit_mom"] = (p / p.shift(1) - 1) * 100
    out["permit_dev_trend"] = p - p.rolling(12, min_periods=10).mean()
    rm60 = p.rolling(60, min_periods=48)
    out["permit_zscore_60m"] = (p - rm60.mean()) / rm60.std()
    out["permit_mom_3m"] = p - p.shift(3)
    out["permit_mom_6m"] = p - p.shift(6)
    out["permit_accel"] = out["permit_mom"] - out["permit_mom"].shift(1)
    out["permit_contraction"] = (out["permit_yoy"] < 0).astype(float).where(out["permit_yoy"].notna())
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(60, min_periods=36).quantile(q)


def rules(signal: str) -> dict[str, Rule]:
    if signal == "S9_contr":
        return {"T_flag": Rule("raw", None, 0.5)}
    out = {f"T1_p{q}": Rule("raw", None, ISQuantile(q / 100, 36)) for q in (25, 50, 75)}
    out.update({f"T2_rp{q}": Rule("raw", None, _roll_q(q / 100)) for q in (25, 50, 75)})
    if signal in {"S2_yoy", "S3_mom", "S8_accel"}:
        out["T4_zero"] = Rule("raw", None, 0.0)
    return out


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(1, 14)), oos_start="2018-01-31",
    min_is_n=60, position_shift=1, track_policy="compute_twice", release_series=SERIES,
    level_columns=["permit"], features=features, signals=SIGNALS, rules=rules,
    strategies=("P1", "P2", "P3"), binary_signals=frozenset({"S9_contr"}), p2_window=(60, 36),
    loop_order=("signal", "lead", "threshold", "strategy", "direction"), vintage_series=SERIES,
)

SIGNAL_DISPLAY = {
    "S1_level": "Building permits level",
    "S2_yoy": "Year-over-year change in building permits",
    "S3_mom": "Month-over-month change in building permits",
    "S4_dev": "Building permits versus their 12-month average",
    "S5_z": "60-month building permits z-score",
    "S6_mom3m": "3-month change in building permits",
    "S7_mom6m": "6-month change in building permits",
    "S8_accel": "Acceleration of monthly building permits change",
    "S9_contr": "Building permits contraction flag (year-over-year below zero)",
}

# ---------------------------------------------------------------------------------------------------- legacy
LEGACY_TAG = "20260314"
LEGACY_REPLAY = None
LEGACY_REPLAY_REASON = (
    "The published rule was selected by the legacy OOS method (max OOS Sharpe among rows with OOS Sharpe > 0 and "
    "full-sample turnover < 24) on tournament_results_20260314.csv, which has OOS columns only (4 dp). The legacy "
    "pipeline never wrote a strategy_returns file or a legacy selection record, so there is nothing to replay "
    "against; the harness legacy mode also selects by in-sample Sharpe, not OOS.")
LEGACY_PUBLISHED = {
    "key": "S3_mom|T1_p25|P3|procyclical|6", "signal": "S3_mom", "threshold": "T1_p25", "strategy": "P3",
    "direction": "procyclical", "lead": 6, "oos_sharpe": 1.4454, "is_sharpe": None, "tag": LEGACY_TAG,
    "selection": "published (OOS-selected, legacy method)",
    "selection_method": "max OOS Sharpe over valid rows (OOS Sharpe > 0, full-sample annual turnover < 24); "
                        "lead grid {0,1,2,3,6}; fixed shift(lead) plus pos.shift(1); revised values",
    "source": "results/permit_spy/winner_summary.json 1.1.0 (tournament_results_20260314.csv row 281)",
}
LEGACY_DIFFERENCES = [
    "Selection: legacy = max OOS Sharpe (OOS consulted); harness = D9 plateau on in-sample Sharpe (OOS never consulted).",
    "Valid flag: legacy = OOS Sharpe > 0 and full-sample turnover < 24; harness = R3.3 eligibility, IS exposure "
    "within [0.05, 0.95], IS sd > 0.",
    "Undefined signal or threshold: legacy treats a NaN comparison as bearish (P1 = 0 cash, P3 = -1 short); "
    "harness leaves the position undefined (held as cash on deployable returns).",
    "IS-quantile thresholds (T1): legacy = one quantile over all IS rows applied to every row; harness = expanding "
    "quantile of earlier IS readings, frozen at the IS end.",
    "Timing: legacy = fixed shift(lead) on month-end stamps with revised values; harness = release-calendar as-of "
    "timing (revised track) or ALFRED vintages (real-time track).",
    "Grid: legacy published grid {0,1,2,3,6}, procyclical only, P2 repeated per threshold; harness = registry grid "
    "1..13, both directions, P2 once per signal/direction/lead, contraction flag with one 0.5 threshold.",
    "Scoring: legacy = dropna returns; harness = deployable returns (undefined position = cash).",
]


def legacy_reproduction() -> dict | None:
    """Acceptance 4.1 record written by scripts/legacy_repro/permit_spy.py (None until it has been run)."""
    p = REPO / "results" / PAIR_ID / f"legacy_reproduction_{LEGACY_TAG}.json"
    return json.loads(p.read_text()) if p.exists() else None


# ---------------------------------------------------------------------------------------------------- data
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
    """Pinned panel of the legacy reproduction (PERMIT vintage 2026-03-14, legacy SPY pull)."""
    df = load_pinned("permit_spy_monthly_legacy_20260314.csv")
    return df[["permit"]], df["spy"].pct_change()
