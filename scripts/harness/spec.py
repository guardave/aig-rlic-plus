"""Pair specification: everything that differs between pairs. The harness never branches on a pair id."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

TRACK_POLICIES = ("compute_twice", "single_revised_no_archive", "single_market")
STRATEGIES = ("P1", "P2", "P3")
DIRECTIONS = ("countercyclical", "procyclical")


@dataclass(frozen=True)
class ISQuantile:
    """Threshold calibrated on the in-sample rows, resolved AFTER lagging (positions.is_quantile_threshold).

    In-sample rows: EXPANDING quantile `q` of the lagged rule variable over the IS rows strictly before the row
    (each IS month uses only readings known before it), NaN until `min_periods` readings exist (the family's
    warm-up; the position is then undefined = cash). OOS rows: frozen at the quantile over all IS rows.
    Legacy replay (Legacy.is_quantile="full") reproduces the pre-Phase-B fit: one quantile over all IS rows
    applied to every row, which let early IS months use later IS readings (Codex B0 HIGH, fleet-wide item)."""
    q: float
    min_periods: int = 1


@dataclass(frozen=True)
class Rule:
    """One (signal, threshold) rule in reading time.

    x_name / x_fn   rule variable (a column computed from the signal; usually the signal itself, e.g. a rolling
                    z-score of it for z thresholds). x_fn maps the signal Series to the variable.
    thr             float, ISQuantile, or a callable signal -> Series (rolling threshold computed on the signal).
    """
    x_name: str
    x_fn: Callable[[pd.Series], pd.Series] | None
    thr: object


@dataclass(frozen=True)
class Legacy:
    """How the pre-harness pipeline scored and selected, so the harness can replay it exactly (checklist 1)."""
    eligibility: str = "none"         # none: common IS start over all candidates | own_is_n: eligibility first
    is_scoring: str = "dropna"        # dropna | deployable (NaN return = cash, 0)
    oos_scoring: str = "dropna"
    tie_break: str = "first"          # first: idxmax in manifest order | cascade: ECON-T3 keys
    p2_per_threshold: bool = False    # True: P2 rows repeated per threshold (pre-dedupe manifests)
    ann_return: str = "geometric"     # geometric (CAGR) | arithmetic (mean * ppy)
    round_table: int | None = None    # decimals the legacy table was rounded to BEFORE selection
    is_quantile: str = "full"         # how the legacy pipeline fitted ISQuantile thresholds (full | expanding)
    selection: str = "is_argmax"      # how the PUBLISHED row was picked: is_argmax (raw IS Sharpe argmax) |
    #                                   max_oos_valid (highest OOS Sharpe among the legacy-valid rows: OOS > 0 and
    #                                   full-history turnover < 24, the legacy `valid` flag; OOS-selected)
    is_window: str = "common"         # common: IS on the common IS start | own_dropna: each candidate's own
    #                                   pre-OOS rows, NaN returns dropped (legacy is_sharpe / is_n)


@dataclass
class PairSpec:
    pair_id: str
    freq: str                          # "M" | "Q" | "D" (period grid of the rebalance index)
    lead_unit: str                     # months | quarters | days (registry lead_axis wording)
    leads: list[int]
    oos_start: str
    min_is_n: int
    position_shift: int                # 0: lead includes the trading lag | 1: pos.shift(1) * return
    track_policy: str
    release_series: str | None         # release_calendar series id or "rule:next_business_day"
    level_columns: list[str]           # raw indicator columns the features are computed from
    features: Callable[[pd.DataFrame], pd.DataFrame]   # level frame -> signal columns (one per signal code)
    signals: dict[str, str]            # signal code -> feature column
    rules: Callable[[str], dict[str, Rule]]            # signal code -> {threshold code: Rule}
    strategies: tuple = ("P1",)
    directions: tuple = DIRECTIONS
    strict_counter: bool = False       # countercyclical bull: x < thr (True) or x <= thr (False)
    binary_signals: frozenset = frozenset()            # 0/1 flags: P2/P3 excluded on these (R4.2)
    p2_window: tuple[int, int] | None = None           # (window, min_periods) of the P2 trailing range
    exposure_bounds: tuple[float, float] = (0.05, 0.95)
    max_is_turnover: float | None = None
    min_is_trades: int | None = None
    trade_count: str = "abs_sum"       # abs_sum: sum |dpos| | gt_0.05: number of changes > 0.05
    loop_order: tuple = ("signal", "threshold", "strategy", "direction", "lead")
    vintage_series: str | None = None  # ALFRED vintage file id for the real-time track
    regime_columns: tuple = ()         # feature columns produced by IS-frozen regime fits (shifted as a block in nulls)
    bootstrap_block: int | None = None # periods; default 6 months / 2 quarters / 21 days
    legacy: Legacy = field(default_factory=Legacy)
    lead_col: str = ""
    ppy: int = 0

    def __post_init__(self):
        if self.track_policy not in TRACK_POLICIES:
            raise ValueError(f"track_policy {self.track_policy!r}")
        if self.freq not in ("M", "Q", "D"):
            raise ValueError(f"freq {self.freq!r}")
        if self.position_shift not in (0, 1):
            raise ValueError("position_shift must be 0 or 1")
        if sorted(self.leads) != list(self.leads) or len(set(self.leads)) != len(self.leads):
            raise ValueError("leads must be strictly increasing")
        self.ppy = self.ppy or {"M": 12, "Q": 4, "D": 252}[self.freq]
        self.lead_col = self.lead_col or {"M": "lead_months", "Q": "lead_quarters", "D": "lead_days"}[self.freq]
        if self.bootstrap_block is None:
            self.bootstrap_block = {"M": 6, "Q": 2, "D": 21}[self.freq]
        unknown = set(self.strategies) - set(STRATEGIES)
        if unknown:
            raise ValueError(f"unknown strategies {unknown}")
        if "P2" in self.strategies and self.p2_window is None:
            raise ValueError("P2 needs p2_window")
