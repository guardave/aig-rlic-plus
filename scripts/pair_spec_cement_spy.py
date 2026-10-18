"""Pair spec: USGS Portland cement shipments x SPY, monthly (Phase B harness, single track).

USGS cement shipments have no public archive of past values (registry value_vintage revised_no_archive), so there is
ONE track: today's values (track_policy single_revised_no_archive) with point-in-time release timing. A month's
reading is used only after its release date (release calendar series USGS_CEMENT_MIS: the USGS Mineral Industry
Surveys publication date where known, otherwise the conservative 126-day fallback). The values are the pinned
snapshot of data/Data Master.xlsx taken 2026-10-16 (data/release_calendar/snapshots/20261016T232733Z/USGS_CEMENT.csv,
identical to the published run's signals on every month). USGS revises earlier months (late survey responses and
annual revisions); what was first published cannot be reconstructed, so that revision lookahead is unquantified and
disclosed on the page.

Signals are growth transforms of the shipment level only (the nominal level trends and is never traded). Signal
formulas and threshold families follow the published pipeline (scripts/pair_pipeline_cement_spy.py at 1d06839f, the
20261016 strict-floor run on the registry grid L5..L14): 12-, 1-, 3- and 6-month growth, the 60-month z-score of
12-month growth and the change in 12-month growth; constant and rolling 60-month quantile thresholds; long/cash (P1)
only, both orientations; position_shift 0 (the lead is the whole lag between the reading month and the return
month; strict floor E5).

Legacy = that published 20261016 run. It selected its rule by raw IN-SAMPLE Sharpe argmax on a common IS start with
eligibility before alignment (a candidate is eligible when its own pre-OOS returns number >= 60; common start =
latest first-valid return among eligible candidates), NaN returns dropped (IS and OOS), IS validity = >= 60 returns,
exposure in [0.05, 0.95], sd > 0, first-in-order ties (pandas idxmax). The harness replays it on the run's own panel:
the snapshot's cement levels and the run's SPY returns (the benchmark_return column of the committed
strategy_returns_20261016.csv; the run's yfinance pull is not pinned elsewhere).

Sample end: the Data Master cement series ends 2025-06 (the snapshot's last month), although USGS has since
published later months; the rebalance grid ends at SAMPLE_END, the last month with a reading, as in the published
run. SPY months after it are not tested.
"""
from __future__ import annotations

import dataclasses

import pandas as pd

from harness.data import REPO, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "cement_spy"
SERIES = "USGS_CEMENT_MIS"
SNAPSHOT = REPO / "data" / "release_calendar" / "snapshots" / "20261016T232733Z" / "USGS_CEMENT.csv"
ROLL_WINDOW = 60          # months: rolling z-score window and rolling-quantile thresholds (legacy constant)
ROLL_MIN_PERIODS = 36     # readings required before a rolling statistic is defined (legacy constant)

SIGNALS = {
    "yoy": "cement_yoy",
    "mom": "cement_mom",
    "chg_3m": "cement_3m",
    "chg_6m": "cement_6m",
    "yoy_zscore_60m": "cement_yoy_zscore_60m",
    "accel": "cement_accel",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    lvl = levels["cement"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["cement_yoy"] = 100.0 * (lvl / lvl.shift(12) - 1.0)
    out["cement_mom"] = 100.0 * (lvl / lvl.shift(1) - 1.0)
    out["cement_3m"] = 100.0 * (lvl / lvl.shift(3) - 1.0)
    out["cement_6m"] = 100.0 * (lvl / lvl.shift(6) - 1.0)
    rm = out["cement_yoy"].rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS)
    out["cement_yoy_zscore_60m"] = (out["cement_yoy"] - rm.mean()) / rm.std()
    out["cement_accel"] = out["cement_yoy"].diff()
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS).quantile(q)


def rules(signal: str) -> dict[str, Rule]:
    """Published threshold families in the published order (pipeline threshold_codes_for)."""
    if signal == "yoy_zscore_60m":
        return {"T_z_0": Rule("raw", None, 0.0), "T_z_1.0": Rule("raw", None, 1.0),
                "T_roll_p50": Rule("raw", None, _roll_q(0.50))}
    return {"T0_zero": Rule("raw", None, 0.0), "T_roll_p25": Rule("raw", None, _roll_q(0.25)),
            "T_roll_p50": Rule("raw", None, _roll_q(0.50))}


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(5, 15)), oos_start="2017-01-31",
    min_is_n=60, position_shift=0, track_policy="single_revised_no_archive", release_series=SERIES,
    level_columns=["cement"], features=features, signals=SIGNALS, rules=rules, strategies=("P1",),
    directions=("countercyclical", "procyclical"),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"),
)
LEGACY_TAG = "20261016"
LEGACY_REPLAY = "is_argmax"          # replayable: the published rule was IS-selected (see module docstring)
LEGACY_SPEC = dataclasses.replace(
    SPEC, legacy=Legacy(eligibility="own_is_n", is_scoring="dropna", oos_scoring="dropna", tie_break="first",
                        ann_return="geometric", round_table=None, selection="is_argmax", is_window="common"))

SIGNAL_DISPLAY = {
    "yoy": "Year-over-year growth in cement shipments",
    "mom": "Month-over-month growth in cement shipments",
    "chg_3m": "3-month growth in cement shipments",
    "chg_6m": "6-month growth in cement shipments",
    "yoy_zscore_60m": "Year-over-year cement shipment growth versus its 60-month history (z-score)",
    "accel": "Change in year-over-year cement shipment growth (acceleration)",
}


def snapshot_levels() -> pd.Series:
    """The pinned Data Master snapshot (2026-10-16): shipments by month-end stamp."""
    s = pd.read_csv(SNAPSHOT, parse_dates=["ref_date"], float_precision="round_trip").set_index("ref_date")["value"]
    s.index = s.index + pd.offsets.MonthEnd(0)
    return s.astype(float).rename("cement")


SAMPLE_START = "2005-11-30"          # first month of the snapshot (= snapshot_levels().index.min(); asserted below)
SAMPLE_END = "2025-06-30"            # last month of the snapshot (= snapshot_levels().index.max(); asserted below)


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's values (the pinned snapshot) on the full monthly grid."""
    s = snapshot_levels()
    return s.reindex(period_grid(s.index.min(), s.index.max(), "M")).to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    """Month-ends from the first to the last month with a cement reading (the published run's panel)."""
    s = snapshot_levels()
    if (s.index.min(), s.index.max()) != (pd.Timestamp(SAMPLE_START), pd.Timestamp(SAMPLE_END)):
        raise ValueError(f"snapshot spans {s.index.min().date()}..{s.index.max().date()}, "
                         f"SAMPLE_START/END say {SAMPLE_START}..{SAMPLE_END}")
    return period_grid(SAMPLE_START, SAMPLE_END, "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The published 20261016 run's own panel (2005-11..2025-06): cement levels from the snapshot (= Data Master.xlsx)
    and that run's SPY returns."""
    df = load_pinned("cement_spy_monthly_legacy_20261016.csv")
    return df[["cement"]], df["spy_ret"]
