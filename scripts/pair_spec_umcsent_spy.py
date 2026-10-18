"""Pair spec: University of Michigan Expected Business Conditions x SPY, monthly (Phase B harness, single track).

The series is the University of Michigan survey's EXPECTED BUSINESS CONDITIONS index (Data Master.xlsx
sheet "UoM_ExptdChgBinesCyle"; release-calendar source id UMICH_EXP_BUS_COND). It is NOT the headline Consumer
Sentiment index (FRED/ALFRED UMCSENT, used by umcsent_xlv and consumer_sentiment_spy). It has no public archive of
past values (registry value_vintage revised_no_archive), so there is ONE track: today's values (track_policy
single_revised_no_archive) with point-in-time release timing. UMCSENT is used ONLY as the release-calendar timing
source: the expected-business-conditions component is published in the same Michigan survey release (preliminary
mid-month, final at or before the end of the survey month). The values are the pinned snapshot of Data Master
taken 2026-10-16 (data/release_calendar/snapshots/20261016T232733Z/UMICH_EXP_BUS_COND.csv), identical to the
published run's levels on every common month. Michigan survey values are rarely revised, but no record of the
values as first published exists, so any revision lookahead is unquantified and disclosed.

Signals are functions of the level only. Signal formulas and threshold families follow the published pipeline
(scripts/pair_pipeline_umcsent_spy.py at d1b68ecd on main, DATE_TAG 20260912): the bounded survey level, its 1-
and 12-month changes and its 60-month z-score; rolling 60-month quantile thresholds (and 0 / 1 for changes and the
z-score); long/cash (P1) only, both orientations, countercyclical bullish when x <= threshold; position_shift 0
(the lead is the whole lag between the reading month and the return month). Registry grid L1..L13 (strict floor 1).

Legacy = the rule published on the main site: the 20260912 run (commit d1b68ecd), chg_12m / T_roll_p50 /
procyclical / L9, test-period Sharpe 1.427. It was selected on OUT-OF-SAMPLE Sharpe: the highest OOS Sharpe among
rows with >= 20 OOS returns, OOS exposure in [0.05, 0.95] and sd > 0, on the lead grid {0,1,2,3,6,9,12}, fixed
shift(lead), NaN returns dropped. There was no in-sample window: the published table's "is_sharpe" column is a copy
of the OOS Sharpe (the legacy code wrote m["oos_sharpe"] into it). The harness replays it on the max_oos_valid path
(same 168 rows in order, OOS columns, the published row and its returns; LEGACY_SPEC below).

Legacy panel: the published run's parquet was overwritten by a later development run, so the panel is rebuilt
from the two records that run left: levels = the Data Master snapshot (the workbook is unchanged since 2026-05-31;
equal to the run's committed signals_20260912.parquet level column on all 393 months, max |diff| 0) and SPY returns
= the benchmark_return column of the run's committed strategy_returns_20260912.csv (= its spy_ret, first month NaN).

A later development run (20261015, branch spike261015_is_oos_floor, commit a5787124, never on the main site) picked
chg_12m / T_roll_p50 / countercyclical / L4 by raw IS argmax on a common IS start; the page names it as an earlier
research run.

Sample end: the Data Master series ends 2025-09 (the snapshot's last month), so the rebalance grid ends at
SAMPLE_END, the last month with a reading, as in the published run. SPY months after it are not tested.
"""
from __future__ import annotations

from dataclasses import replace

import pandas as pd

from harness.data import REPO, load_pinned, period_grid, target_returns
from harness.spec import Legacy, PairSpec, Rule

PAIR_ID = "umcsent_spy"
SERIES = "UMCSENT"                   # release-calendar TIMING source only (same Michigan survey release)
SOURCE_ID = "UMICH_EXP_BUS_COND"     # the value source: Data Master snapshot id
SNAPSHOT = REPO / "data" / "release_calendar" / "snapshots" / "20261016T232733Z" / f"{SOURCE_ID}.csv"
ROLL_WINDOW = 60          # months: rolling z-score window and rolling-quantile thresholds (legacy constant)
ROLL_MIN_PERIODS = 24     # readings required before a rolling statistic is defined (legacy constant)

SIGNALS = {
    "level": "umcsent_level",
    "diff_1m": "umcsent_diff_1m",
    "chg_12m": "umcsent_chg_12m",
    "zscore_60m": "umcsent_zscore_60m",
}


def features(levels: pd.DataFrame) -> pd.DataFrame:
    lvl = levels["umcsent"].astype(float)
    out = pd.DataFrame(index=levels.index)
    out["umcsent_level"] = lvl
    out["umcsent_diff_1m"] = lvl.diff(1)
    out["umcsent_chg_12m"] = lvl.diff(12)
    rm = lvl.rolling(ROLL_WINDOW, min_periods=ROLL_MIN_PERIODS)
    out["umcsent_zscore_60m"] = (lvl - rm.mean()) / rm.std()
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
    pair_id=PAIR_ID, freq="M", lead_unit="months", leads=list(range(1, 14)), oos_start="2017-08-31",
    min_is_n=60, position_shift=0, track_policy="single_revised_no_archive", release_series=SERIES,
    level_columns=["umcsent"], features=features, signals=SIGNALS, rules=rules, strategies=("P1",),
    directions=("countercyclical", "procyclical"),
    loop_order=("signal", "threshold", "strategy", "direction", "lead"),
)

# The published 20260912 pipeline: lead grid {0,1,2,3,6,9,12}, dropna OOS scoring, OOS-selected (max_oos_valid);
# its validity flag was OOS-based (>= 20 OOS returns, OOS exposure in [0.05, 0.95], sd > 0)
LEGACY_LEADS = [0, 1, 2, 3, 6, 9, 12]
LEGACY_SPEC = replace(
    SPEC, leads=LEGACY_LEADS,
    legacy=Legacy(eligibility="none", is_scoring="dropna", oos_scoring="dropna", tie_break="first",
                  ann_return="geometric", round_table=None, selection="max_oos_valid", is_window="own_dropna"),
)
LEGACY_TAG = "20260912"
LEGACY_REPLAY = "max_oos_valid"      # replayable: the published rule was OOS-selected (see module docstring)

SIGNAL_DISPLAY = {
    "level": "Michigan Expected Business Conditions index (level)",
    "diff_1m": "Month-on-month change in the Michigan Expected Business Conditions index",
    "chg_12m": "12-month change in the Michigan Expected Business Conditions index",
    "zscore_60m": "Michigan Expected Business Conditions index versus its 60-month history (z-score)",
}


def snapshot_levels() -> pd.Series:
    """The pinned Data Master snapshot (2026-10-16): the index by month-end stamp."""
    s = pd.read_csv(SNAPSHOT, parse_dates=["ref_date"], float_precision="round_trip").set_index("ref_date")["value"]
    s.index = s.index + pd.offsets.MonthEnd(0)
    return s.astype(float).rename("umcsent")


SAMPLE_END = "2025-09-30"            # last month of the snapshot (= snapshot_levels().index.max(); asserted below)


def target_prices() -> pd.Series:
    return load_pinned("spy_month_end_20261017.csv")["spy_close"]


def revised_levels() -> pd.DataFrame:
    """Today's values (the pinned snapshot) on the full monthly grid."""
    s = snapshot_levels()
    return s.reindex(period_grid(s.index.min(), s.index.max(), "M")).to_frame()


def rebalance_index() -> pd.DatetimeIndex:
    """SPY month-ends from the first SPY month to SAMPLE_END, the last month with a reading."""
    end = snapshot_levels().index.max()
    if end != pd.Timestamp(SAMPLE_END):
        raise ValueError(f"snapshot ends {end.date()}, SAMPLE_END says {SAMPLE_END}")
    p = target_prices()
    return period_grid(p.index.min(), end, "M")


def target_return(index: pd.DatetimeIndex):
    return target_returns(target_prices(), index)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """The published 20260912 run's panel (1993-01..2025-09; levels from the Data Master snapshot, SPY returns from
    that run's committed strategy_returns_20260912.csv; see the module docstring) and its returns."""
    df = load_pinned("umcsent_spy_monthly_legacy_20260912.csv")
    return df[["umcsent"]], df["spy_ret"]
