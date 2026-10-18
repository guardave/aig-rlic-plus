"""Pair spec: ISM Manufacturing PMI x SPY, monthly (Phase B harness, single track).

The ISM Manufacturing PMI has no public archive of past values (it is not on FRED/ALFRED; registry value_vintage
revised_no_archive), so there is ONE track: today's values (track_policy single_revised_no_archive) with
point-in-time release timing (ISM publishes on the first business day of the following month; release calendar
series ISM_MFG). The values are the pinned snapshot of data/Data Master.xlsx taken 2026-10-16
(data/release_calendar/snapshots/20261016T232733Z/ISM_MFG.csv, identical to the published run's panel on every
common month). The PMI is seasonally adjusted and its seasonal factors are re-estimated each year, so earlier
months may differ slightly from what was first published; that revision lookahead is unquantified and disclosed.

Signals are functions of the PMI level only. Signal formulas and threshold families follow the published pipeline
(scripts/pair_pipeline_ism_mfg_spy.py at 1d06839f, the 20261016 strict-floor run on the registry grid L2..L13):
the bounded diffusion level, its 1- and 12-month changes and its 60-month z-score; constant and rolling 60-month
quantile thresholds; long/cash (P1) only, both orientations; position_shift 0 (the lead is the whole lag between
the reading month and the return month; floor E2).

Legacy = that published 20261016 run. It selected its rule by raw IN-SAMPLE Sharpe argmax on a common IS start
(latest first-valid return over the whole grid), NaN returns dropped, IS validity = >= 60 returns, exposure in
[0.05, 0.95], sd > 0, first-in-order ties (pandas idxmax). The harness replays it on the run's own panel: a pinned
copy of the ignored data/ism_mfg_spy_monthly_latest.parquet that run wrote (ISM from Data Master.xlsx sheet
"ISM Manufacturing PMI", SPY from yfinance; parquet sha256 ce946790...).

Sample end: the Data Master ISM series ends 2025-10 (the snapshot's last month), so the rebalance grid ends at
SAMPLE_END, the last month with a PMI reading, as in the published run. SPY months after it are not tested.
"""
from __future__ import annotations

import pandas as pd

from harness.data import REPO, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "ism_mfg_spy"
SERIES = "ISM_MFG"
SNAPSHOT = REPO / "data" / "release_calendar" / "snapshots" / "20261016T232733Z" / "ISM_MFG.csv"
ROLL_WINDOW = 60          # months: rolling z-score window and rolling-quantile thresholds (legacy constant)
ROLL_MIN_PERIODS = 24     # readings required before a rolling statistic is defined (legacy constant)

SIGNALS = {
    "level": "ism_level",
    "diff_1m": "ism_diff_1m",
    "chg_12m": "ism_chg_12m",
    "zscore_60m": "ism_zscore_60m",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    lvl = levels["ism"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["ism_level"] = lvl
    out["ism_diff_1m"] = lvl.diff(1)
    out["ism_chg_12m"] = lvl.diff(12)
    rm = lvl.rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS)
    out["ism_zscore_60m"] = (lvl - rm.mean()) / rm.std()
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(60, min_periods=24).quantile(q)       # = ROLL_WINDOW, ROLL_MIN_PERIODS


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order (pipeline threshold_codes_for)."""
    if signal in ("diff_1m", "chg_12m"):
        return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p50": Rule("raw", None, _roll_q(0.50)),
                "T_roll_p75": Rule("raw", None, _roll_q(0.75))}
    if signal == "zscore_60m":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {"T_roll_p25": Rule("raw", None, _roll_q(0.25)), "T_roll_p50": Rule("raw", None, _roll_q(0.50)),
            "T_roll_p75": Rule("raw", None, _roll_q(0.75))}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(2, 14)), oos_start="2017-09-30",
    min_is_n=60, position_shift=0, track_policy="single_revised_no_archive", release_series=SERIES,
    level_columns=["ism"], features=features, signals=SIGNALS, rules=rules, strategies=("P1",),
    directions=("countercyclical", "procyclical"),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"),
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first",
                  ann_return="geometric", round_table=None, selection="is_argmax", is_window="common"),
)
LEGACY_TAG = "20261016"
LEGACY_REPLAY = "is_argmax"          # replayable: the published rule was IS-selected (see module docstring)

SIGNAL_DISPLAY = {
    "level": "ISM Manufacturing PMI (level)",
    "diff_1m": "Month-on-month change in the ISM Manufacturing PMI",
    "chg_12m": "12-month change in the ISM Manufacturing PMI",
    "zscore_60m": "ISM Manufacturing PMI versus its 60-month history (z-score)",
}


def snapshot_levels() -> pd.Series:
    """The pinned Data Master snapshot (2026-10-16): PMI by month-end stamp."""
    s = pd.read_csv(SNAPSHOT, parse_dates=["ref_date"], float_precision="round_trip").set_index("ref_date")["value"]
    s.index = s.index + pd.offsets.MonthEnd(0)
    return s.astype(float).rename("ism")


SAMPLE_END = "2025-10-31"            # last month of the snapshot (= snapshot_levels().index.max(); asserted below)


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's values (the pinned snapshot) on the full monthly grid."""
    s = snapshot_levels()
    return s.reindex(period_grid(s.index.min(), s.index.max(), "M")).to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    """SPY month-ends from the first SPY month to SAMPLE_END, the last month with a PMI reading."""
    end = snapshot_levels().index.max()
    if end != pd.Timestamp(SAMPLE_END):
        raise ValueError(f"snapshot ends {end.date()}, SAMPLE_END says {SAMPLE_END}")
    p = target_prices()
    return period_grid(p.index.min(), end, "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The published 20261016 run's own panel (1993-01..2025-10: ISM from Data Master.xlsx, its yfinance SPY pull)
    and its returns."""
    df = load_pinned("ism_mfg_spy_monthly_legacy_20261016.csv")
    return df[["ism"]], df["spy_ret"]
