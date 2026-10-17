"""Pair spec: HY-IG credit spread x SPY, daily market data (single track, Phase B harness).

ICE BofA OAS is not revised, so there is one track ("market"); FRED posts the value dated t on the next
business day, so readings are available from the next trading day (registry: lead_floor 1, position_shift 1).
Regime signals are IS-frozen causal fits (HMM on [spread change, VIX]; Markov-switching on spread change),
re-estimated inside every null draw. Legacy = the published 20261016 pipeline (dropna IS scoring, deployable OOS,
P2 repeated per threshold, table rounded to 6 dp before the ECON-T3 cascade).
"""
from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
from scipy import stats

from harness.data import REPO
from harness.regime import hmm_stress, ms_stress
from harness.spec import ISQuantile, Legacy, PairSpec, Rule

PAIR_ID = "hy_ig_spy"
OOS_START = "2019-10-01"
INPUT_PARQUET = REPO / "data" / "hy_ig_spy_daily_20000101_20260422.parquet"
HMM_SEEDS = (42, 0, 1, 2, 3)

SIGNALS = {
    "S1_spread_level": "hy_ig_spread_pct",
    "S2a_zscore_252d": "hy_ig_zscore_252d",
    "S2b_zscore_504d": "hy_ig_zscore_504d",
    "S3a_pctrank_504d": "hy_ig_pctrank_504d",
    "S3b_pctrank_1260d": "hy_ig_pctrank_1260d",
    "S4a_roc_21d": "hy_ig_roc_21d",
    "S4b_roc_63d": "hy_ig_roc_63d",
    "S4c_roc_126d": "hy_ig_roc_126d",
    "S5_ccc_bb_spread": "ccc_bb_spread_pct",
    "S6_hmm_stress": "hmm_2state_prob_stress",
    "S7_ms_stress": "ms_2state_stress_prob",
    "S10_mom_21d": "hy_ig_mom_21d",
    "S11_mom_63d": "hy_ig_mom_63d",
    "S12_mom_252d": "hy_ig_mom_252d",
    "S13_acceleration": "hy_ig_acceleration",
}
LEVEL_COLUMNS = ["hy_oas", "ig_oas", "ccc_hy_oas", "bb_hy_oas", "vix"]
REGIME_COLUMNS = ("hmm_2state_prob_stress", "ms_2state_stress_prob")


def _pctrank(s: pd.Series, window: int, minp: int) -> pd.Series:
    return s.rolling(window, min_periods=minp).apply(lambda x: stats.rankdata(x)[-1] / len(x), raw=True)


def base_features(levels: pd.DataFrame) -> pd.DataFrame:
    sp = levels["hy_oas"] - levels["ig_oas"]
    out = pd.DataFrame(index=levels.index)
    out["hy_ig_spread_pct"] = sp
    out["hy_ig_zscore_252d"] = (sp - sp.rolling(252, min_periods=200).mean()) / sp.rolling(252, min_periods=200).std()
    out["hy_ig_zscore_504d"] = (sp - sp.rolling(504, min_periods=400).mean()) / sp.rolling(504, min_periods=400).std()
    out["hy_ig_pctrank_504d"] = _pctrank(sp, 504, 400)
    out["hy_ig_pctrank_1260d"] = _pctrank(sp, 1260, 1000)
    for h in (21, 63, 126):
        out[f"hy_ig_roc_{h}d"] = (sp / sp.shift(h) - 1) * 100
    for h in (21, 63, 252):
        out[f"hy_ig_mom_{h}d"] = sp - sp.shift(h)
    out["hy_ig_acceleration"] = out["hy_ig_roc_21d"] - out["hy_ig_roc_21d"].shift(21)
    out["ccc_bb_spread_pct"] = levels["ccc_hy_oas"] - levels["bb_hy_oas"]
    return out


def features(levels: pd.DataFrame) -> pd.DataFrame:
    """All signal columns, regime probabilities fitted on rows before the OOS start and filtered forward."""
    out = base_features(levels)
    chg = out["hy_ig_spread_pct"].diff()
    out["hmm_2state_prob_stress"] = hmm_stress(pd.DataFrame({"spread_change": chg, "vix": levels["vix"]}),
                                               OOS_START, "spread_change", seeds=HMM_SEEDS)
    out["ms_2state_stress_prob"] = ms_stress(chg.rename("spread_change"), OOS_START)
    return out


def _roll_q(q: float):
    return lambda s: s.rolling(504, min_periods=400).quantile(q)


def _z504(s: pd.Series) -> pd.Series:
    return (s - s.rolling(504, min_periods=400).mean()) / s.rolling(504, min_periods=400).std().replace(0, np.nan)


def rules(signal: str) -> dict[str, Rule]:
    if signal == "S6_hmm_stress":
        return {f"T4_hmm_{t}": Rule("raw", None, t) for t in (0.5, 0.7)}
    if signal == "S7_ms_stress":
        return {f"T5_ms_{t}": Rule("raw", None, t) for t in (0.5, 0.7)}
    # T1: in-sample percentile, expanding over the IS readings before each row (warm-up 400 = the min_periods
    # of the pair's 504-day rolling families), frozen at the IS end out of sample (spec.ISQuantile).
    out = {f"T1_p{p}": Rule("raw", None, ISQuantile(p / 100, min_periods=400)) for p in (75, 85, 95)}
    out.update({f"T2_rp{p}": Rule("raw", None, _roll_q(p / 100)) for p in (75, 85, 95)})
    out.update({f"T3_z{z}": Rule("z504", _z504, z) for z in (1.5, 2.0, 2.5)})
    return out


SPEC = PairSpec(
    pair_id=PAIR_ID, freq="D", lead_unit="days", leads=[1, 5, 21, 63, 126, 252], oos_start=OOS_START,
    min_is_n=1260, position_shift=1, track_policy="single_market", release_series="rule:next_business_day",
    level_columns=LEVEL_COLUMNS, features=features, signals=SIGNALS, rules=rules,
    strategies=("P1", "P2", "P3"), directions=("countercyclical",), strict_counter=True, p2_window=(504, 400),
    max_is_turnover=24, min_is_trades=10, trade_count="gt_0.05",
    loop_order=("signal", "lead", "threshold", "strategy", "direction"), regime_columns=REGIME_COLUMNS,
    legacy=Legacy(eligibility="own_is_n", is_scoring="dropna", oos_scoring="deployable", tie_break="cascade",
                  p2_per_threshold=True, ann_return="arithmetic", round_table=6),
)

SIGNAL_DISPLAY = {
    "S1_spread_level": "HY-IG Spread Level", "S2a_zscore_252d": "Z-Score (252d)", "S2b_zscore_504d": "Z-Score (504d)",
    "S3a_pctrank_504d": "Percentile Rank (504d)", "S3b_pctrank_1260d": "Percentile Rank (1260d)",
    "S4a_roc_21d": "Rate of Change (21d)", "S4b_roc_63d": "Rate of Change (63d)", "S4c_roc_126d": "Rate of Change (126d)",
    "S5_ccc_bb_spread": "CCC-BB Quality Spread", "S6_hmm_stress": "HMM Stress Probability (causal)",
    "S7_ms_stress": "Markov-Switching Stress Probability (causal)", "S10_mom_21d": "Momentum (21d)",
    "S11_mom_63d": "Momentum (63d)", "S12_mom_252d": "Momentum (252d)", "S13_acceleration": "Spread Acceleration",
}


def _panel() -> pd.DataFrame:
    df = pd.read_parquet(INPUT_PARQUET)
    return df.dropna(subset=["spy_ret"])


def target_prices() -> pd.Series:
    return pd.read_parquet(INPUT_PARQUET)["spy"]


def revised_levels() -> pd.DataFrame:
    """Market data (not revised): the pinned daily panel's raw OAS and VIX columns, every row (rolling windows warm
    up from the first observation, as in the published pipeline)."""
    return pd.read_parquet(INPUT_PARQUET)[LEVEL_COLUMNS]


def rebalance_index() -> pd.DatetimeIndex:
    return _panel().index


def target_return(index: pd.DatetimeIndex):
    """The panel's SPY daily return (its first row is a return from the prior close, kept as published)."""
    return _panel()["spy_ret"].reindex(index).to_numpy(float)


def legacy_panel() -> tuple[pd.DataFrame, pd.Series]:
    """Published inputs: the parquet's signal columns plus the committed causal regime probabilities."""
    df = _panel()
    sig = pd.read_parquet(REPO / "results" / PAIR_ID / f"signals_{LEGACY_TAG}.parquet")
    for c in REGIME_COLUMNS:
        df[c] = sig[c].reindex(df.index)
    return df, df["spy_ret"]


LEGACY_TAG = "20261016"
LEGACY_SPEC = dataclasses.replace(SPEC, features=lambda lv: lv[list(SIGNALS.values())])
