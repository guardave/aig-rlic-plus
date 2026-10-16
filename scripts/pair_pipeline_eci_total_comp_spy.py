#!/usr/bin/env python3
"""
Full Econometrics Pipeline: Employment Cost Index (Total Compensation) -> SPY
==============================================================================
Pair ID: eci_total_comp_spy (Mode 1, QUARTERLY — the portal's FIRST quarterly pair).
Branch: feat260705_eci_spy

Economic hypothesis (stated up front, per SOP):
  H0: ECI total-compensation growth does NOT Granger-cause / predict SPY forward returns.
  H1 (countercyclical prior, Dana/brief): accelerating compensation growth = wage-inflation
      pressure = tighter Fed / margin compression = risk-off; decelerating ECI = disinflation
      = risk-on. ECI is a classic LAGGING indicator (labor costs turn after the cycle).
  Direction AND lead/lag status are determined EMPIRICALLY (Toda-Yamamoto Granger /
  pre-whitened CCF / local projections) — the prior only seeds; it does NOT decide.
  A LAGGING/NULL verdict is a valid, publishable outcome.

QUARTERLY conventions (first quarterly pair — deliberate template adaptations):
  * Annualization factor: sqrt(4) for Sharpe, x4 for mean return / variance-based vol
    (quarterly frequency; stated explicitly in every manifest).
  * Lead grid L in QUARTERS, floor L1 (BLS releases quarter Q ~1 month after quarter end,
    so the quarter-Q print is first tradable in Q+1). Grid L1..L8 (2 years): wage-inflation
    -> Fed-policy -> equity transmission is plausibly 1-8 quarters; deeper leads on 101 obs
    destroy effective sample (L8 already costs 8 obs) with no economic rationale.
  * Rolling windows in quarter counts: lookbacks LB12 (~3yr) / LB20 (~5yr).
  * Correlation horizons: spy_fwd_1q / 2q / 4q (recorded as 63/126/252 horizon_days).
  * Sparse grid (Dana: do NOT explode combos on 101 points): 2 strategy families
    (long/cash, long/short) x 2 orientations; thresholds = IS percentiles {25,50,75},
    zero-cross (sign-meaningful signals only), rolling z-score +/-1.0 at 2 lookbacks.

BINDING Phase-0 constraints (Dana handoff):
  * 101 quarters 2001-Q1..2026-Q1 (~25yr — good cycle coverage, FEW observations).
    OOS window has few quarters -> any winner is FOUND-IN-SEARCH; CANDIDATE, never
    a validated edge. The caveat is STRONGER than Cass (25 OOS points vs 36).
  * SA source: no seasonal-contamination constraint (all transform families admissible;
    the clean-envelope and the envelope coincide — both files still emitted per GH #13).
  * Stationarity: growth family (QoQ/2Q/YoY/dev-trend) BORDERLINE (persistent wage
    inflation; YoY near-I(1)) -> pre-whitening ESSENTIAL for CCF; Toda-Yamamoto
    (d_max=1) for Granger. Cleanly stationary: accel, yoy_accel. 20Q z-scores
    regime-contaminated (KPSS reject) — usable but flagged.
  * Nominal stickiness: the ECI level almost never declines -> level-based contraction
    flags uninformative (none included); YoY>0 always -> no zero-cross on growth levels.

Category (Rule C1): macro. Battery: correlations incl. distance, pre-whitened CCF,
Toda-Yamamoto Granger both directions (lags 1..4 — sane for 101 obs), transfer entropy
(tercile-binned, 500 perms; small-sample caveat), local projections fwd+rev (1/2/4Q),
quantile regression, HMM 2-state (attempted; flagged if degenerate), quartile returns,
ECON-LA1 Lead Analysis + ECON-LT1 Lead Tournament (+ GH #13 winner-curve / clean-envelope).

Author: Econ Evan (Econometrics Agent). Date: 2026-07-06.
"""

import os
import sys
import json
from pathlib import Path
import time
import hashlib
import warnings
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
np.random.seed(42)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PAIR_ID = "eci_total_comp_spy"
INDICATOR_NAME = "Employment Cost Index (Total Compensation)"
TARGET_SYMBOL = "SPY"
DATE_TAG = "20261016"
PREV_TAG = "20261008"   # previously published run (smoothed full-sample HMM winner); immutable
COST_BPS = 5  # equity ETF per target-class table
ANN = np.sqrt(4)   # QUARTERLY annualization factor (Sharpe); mean x4, vol x sqrt(4)
PERIODS_PER_YEAR = 4

BASE_DIR = str(Path(__file__).resolve().parents[1])
DATA_PATH = os.path.join(BASE_DIR, "data", "eci_total_comp_spy_quarterly_latest.parquet")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")
SCHEMA_DIR = os.path.join(BASE_DIR, "docs", "schemas")

for d in [RESULTS_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# tournament signal KEY -> parquet column
SIGNAL_COLS = {
    "qoq": "eci_total_comp_pct_qoq",
    "growth_2q": "eci_total_comp_pct_2q",
    "yoy": "eci_total_comp_pct_yoy",
    "dev_trend": "eci_total_comp_dev_trend_pct",
    "level_zscore_20q": "eci_total_comp_zscore_20q",
    "yoy_zscore_20q": "eci_total_comp_yoy_zscore_20q",
    "accel": "eci_total_comp_accel_pct",
    "yoy_accel": "eci_total_comp_yoy_accel_pct",
    # derived in stage_signals:
    "hmm_stress": "hmm_2state_prob_stress",
    "markov_regime": "markov_regime_2state",
}
SIGNAL_DISPLAY = {
    "qoq": "ECI quarter-on-quarter growth", "growth_2q": "ECI 2-quarter growth", "yoy": "ECI year-over-year growth",
    "dev_trend": "ECI deviation from 8-quarter trend", "level_zscore_20q": "ECI level z-score (20 quarters)",
    "yoy_zscore_20q": "ECI YoY growth z-score (20 quarters)", "accel": "ECI quarter-on-quarter acceleration",
    "yoy_accel": "ECI YoY acceleration", "hmm_stress": "HMM wage-inflation stress probability",
    "markov_regime": "Markov-switching regime probability",
}
# registry signal_code per key (ECON-DS3)
REGISTRY_CODE = {
    "qoq": "eci_total_comp_qoq", "growth_2q": "eci_total_comp_2q", "yoy": "eci_total_comp_yoy",
    "dev_trend": "eci_total_comp_dev_trend", "level_zscore_20q": "eci_total_comp_level_zscore_20q",
    "yoy_zscore_20q": "eci_total_comp_yoy_zscore_20q", "accel": "eci_total_comp_accel",
    "yoy_accel": "eci_total_comp_yoy_accel", "hmm_stress": "hmm_stress", "markov_regime": "markov_regime",
}
# signals where 0 is an economically meaningful threshold (sign flips are informative).
# NOT the growth levels (wage growth never goes negative — nominal stickiness).
ZERO_CROSS = {"accel", "yoy_accel", "dev_trend"}
# stationarity class per Dana's tests (for honesty flags in the tournament CSV)
STATIONARY_CLEAN = {"accel", "yoy_accel"}          # ADF+KPSS both clean
REGIME_CONTAMINATED = {"level_zscore_20q", "yoy_zscore_20q"}  # KPSS reject

MAIN_SIG = "eci_total_comp_pct_yoy"  # headline wage-inflation rate (pre-whitened for CCF)
FWD_COLS = ["spy_fwd_1q", "spy_fwd_2q", "spy_fwd_4q"]

SIG_ELIGIBLE_MIN = 60          # min non-NaN QUARTERS for tournament eligibility
LOOKBACKS = {"LB12": 12, "LB20": 20}   # quarters (~3yr / ~5yr)
LEADS = list(range(1, 6))  # #255 floor L1 shifted grid [1..5] (quarters)
MIN_IS_N = 20                  # quarterly IS minimum (PORT_GUIDE: 5 years)
MAX_TURNOVER = 6               # position changes per year (quarterly rebalance ceiling)
REGIME_SEEDS = (42, 0, 1, 2, 3)
CORR_N_FLOOR = 40              # quarters


def log_stage(name):
    def deco(fn):
        def wrap(*a, **k):
            t0 = time.time()
            print(f"\n{'='*70}\n  STAGE: {name}\n{'='*70}")
            out = fn(*a, **k)
            STAGE_TIMES[name] = time.time() - t0
            print(f"  [{name}] done in {STAGE_TIMES[name]:.1f}s")
            return out
        return wrap
    return deco


def write_manifest(path, columns, assertions, extra=None):
    m = {"file": os.path.basename(path), "pair_id": PAIR_ID,
         "produced_by": "scripts/pair_pipeline_eci_total_comp_spy.py",
         "generated_at": NOW_ISO,
         "frequency": "quarterly",
         "annualization": "Sharpe = mean/std * sqrt(4); ann_return = mean*4 (quarterly data)",
         "columns": columns, "assertions": assertions}
    if extra:
        m.update(extra)
    with open(os.path.splitext(path)[0] + "_manifest.json", "w") as f:
        json.dump(m, f, indent=2)


def ann_metrics(rets):
    """Quarterly annualized metrics. Convention: Sharpe = mean/std*sqrt(4)."""
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return dict(sharpe=0.0, ann_return=0.0, ann_vol=0.0, max_dd=0.0,
                    sortino=0.0, calmar=0.0, win_rate=0.0, n=len(rets))
    sharpe = rets.mean() / rets.std() * ANN
    ann_ret = rets.mean() * PERIODS_PER_YEAR
    ann_vol = rets.std() * ANN
    cum = (1 + rets).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    neg = rets[rets < 0]
    sortino = ann_ret / (neg.std() * ANN) if len(neg) > 1 and neg.std() > 0 else 0.0
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    return dict(sharpe=sharpe, ann_return=ann_ret, ann_vol=ann_vol, max_dd=dd,
                sortino=sortino, calmar=calmar, win_rate=(rets > 0).mean(), n=len(rets))


# ===================================================================
# STAGE 1: LOAD + VERIFY (Defense 2 consumer checks)
# ===================================================================
@log_stage("1_load_verify")
def stage_load():
    df = pd.read_parquet(DATA_PATH)
    assert df.shape == (101, 19), f"unexpected shape {df.shape}"
    # Known-episode checks (Dana's interpretation_metadata):
    surge = df.loc["2021-06-30":"2023-12-31", "eci_total_comp_pct_yoy"]
    assert surge.max() > 4.8, "2021-23 wage surge missing (YoY peak ~5.1%)"
    gfc = df.loc["2009-06-30":"2010-12-31", "eci_total_comp_pct_yoy"]
    assert gfc.min() < 2.0, "post-GFC wage deceleration missing"
    assert (df["eci_total_comp_idx"].diff().dropna() >= -0.2).all(), "nominal stickiness violated (level declines)"
    assert df["spy_ret"].abs().max() < 0.35, "quarterly SPY return magnitude implausible"
    assert df["spy_fwd_4q"].iloc[-4:].isna().all(), "forward-return leakage at tail"
    print(f"  Loaded {df.shape}, {df.index.min().date()} -> {df.index.max().date()} (QUARTERLY)")
    print("  Defense-2 episode checks: 2021-23 wage surge, post-GFC deceleration, nominal stickiness — PASS")
    return df


# ===================================================================
# STAGE 2: DERIVED REGIME SIGNALS (HMM + Markov-switching) + persistence
# ===================================================================
def compute_split(df):
    """ECON-OOS2 policy v1_max36_25pct_cap120 in native quarterly units (unchanged rule).
    Computed before the regime models so they can be fit on IS rows only."""
    work = df.dropna(subset=["spy_ret"])
    n_q = len(work)
    oos_n = int(min(max(12, round(n_q * 0.25)), 40))
    return {"n_q": n_q, "oos_n": oos_n, "oos_start": work.index[-oos_n],
            "is_end": work.index[-(oos_n + 1)], "oos_end": work.index[-1]}


@log_stage("2_signals")
def stage_signals(df, oos_start):
    """Regime signals, causal (scripts/_regime_causal.py): IS-only fit, IS-only standardisation,
    forward-filtered P(state_t | x_1..x_t). The target return is not in any likelihood.

    ECI has 97 YoY quarters; 72 fall before the OOS start. The helper's minimum for a traded
    fit is 100 IS rows (HMM 50 x 2 states; MS 100), so both regime signals are EXCLUDED from
    the tournament (PORT GUIDE step 5: accept the raise; report it). A 2-state HMM is still fit
    on the 72 IS quarters with an explicit override as a DIAGNOSTIC (not traded) so the Evidence
    page can show what a causal regime read looks like and the look-ahead audit can score the
    superseded rule on it."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _regime_causal import fit_hmm_causal, fit_ms_causal

    yoy = df["eci_total_comp_pct_yoy"]
    regime_log = {"oos_start": str(pd.Timestamp(oos_start).date()), "models": {}}

    # --- traded attempt: HMM 2-state on YoY wage growth ("stress" = higher-mean state) ---
    try:
        r = fit_hmm_causal(yoy.to_frame(), oos_start, n_states=2, label_feature=yoy.name,
                           label="max", seeds=REGIME_SEEDS)
        df["hmm_2state_prob_stress"] = r.prob.reindex(df.index)
        regime_log["models"]["hmm_2state_prob_stress"] = {"status": "traded", **r.summary()}
    except ValueError as e:
        regime_log["models"]["hmm_2state_prob_stress"] = {
            "status": "excluded_from_tournament", "reason": str(e),
            "rule": "helper minimum 100 IS rows for a traded 2-state HMM (50 x n_states)"}
        print(f"  HMM excluded from the tournament: {e}")

    # --- traded attempt: Markov-switching on the indicator (YoY change), never spy_ret ---
    try:
        d_yoy = yoy.diff().rename("eci_total_comp_yoy_diff")
        ms = fit_ms_causal(d_yoy, oos_start, k_regimes=2, switching_variance=True, label="max_variance")
        df["markov_regime_2state"] = ms.prob.reindex(df.index)
        regime_log["models"]["markov_regime_2state"] = {"status": "traded", **ms.summary()}
    except ValueError as e:
        regime_log["models"]["markov_regime_2state"] = {
            "status": "excluded_from_tournament", "reason": str(e),
            "rule": "helper minimum 100 IS rows for a traded Markov-switching fit"}
        print(f"  Markov-switching excluded from the tournament: {e}")

    # --- diagnostic (NOT traded): causal HMM on the 72 IS quarters, explicit override ---
    hmm_diag = None
    try:
        hmm_diag = fit_hmm_causal(yoy.to_frame(), oos_start, n_states=2, label_feature=yoy.name,
                                  label="max", seeds=REGIME_SEEDS, min_is_rows=40)
        prob = hmm_diag.prob.reindex(df.index)
        states = (prob > 0.5).astype(float).where(prob.notna())
        hmm_states = pd.DataFrame({"hmm_state": states, "prob_stress": prob, "prob_calm": 1 - prob}).dropna()
        hmm_states.to_parquet(os.path.join(MODELS_DIR, "hmm_states.parquet"))
        spy = df["spy_ret"]
        summ = []
        for lbl, mask in [("high_wage_inflation", hmm_states["hmm_state"] == 1),
                          ("low_wage_inflation", hmm_states["hmm_state"] == 0)]:
            idx = hmm_states.index[mask]
            rets = spy.reindex(idx).dropna()
            summ.append({"state_label": lbl,
                         "mean_return": round(rets.mean(), 6) if len(rets) else np.nan,
                         "vol": round(rets.std(), 6) if len(rets) else np.nan,
                         "duration_days": int(mask.sum()) * 63,  # quarters -> ~trading days
                         "frequency_pct": round(mask.mean() * 100, 2),
                         "mean_yoy_growth": round(yoy.reindex(idx).mean(), 3)})
        pd.DataFrame(summ).to_csv(os.path.join(MODELS_DIR, "hmm_summary.csv"), index=False)
        surge_p = prob.loc["2021-12-31":"2023-06-30"].mean()
        write_manifest(os.path.join(MODELS_DIR, "hmm_states.parquet"),
                       {"hmm_state": "1 if filtered prob_stress > 0.5 else 0 (stress = higher-mean wage-inflation state)",
                        "prob_stress": "forward-filtered P(high wage-inflation state | ECI YoY up to t); params fit on IS quarters only",
                        "prob_calm": "1 - prob_stress"},
                       [{"description": "probabilities in [0,1]", "check": "prob_stress between 0 and 1"},
                        {"description": "2021-23 wage surge", "filter": "2021-12..2023-06",
                         "column": "prob_stress", "check": f"mean = {surge_p:.2f}"}],
                       extra={"status": "DIAGNOSTIC ONLY - not a tournament signal",
                              "fit": hmm_diag.summary(),
                              "caveat": (f"fit on {hmm_diag.n_fit} IS quarters, below the 100-row minimum the helper "
                                         "requires for a traded signal (override min_is_rows=40); transition matrix weakly identified")})
        regime_log["models"]["hmm_diagnostic"] = {"status": "diagnostic_not_traded", **hmm_diag.summary()}
        print(f"  Diagnostic causal HMM (not traded): n_fit={hmm_diag.n_fit}; filtered stress mean 2021Q4-2023Q2 {surge_p:.2f}")
    except Exception as e:
        regime_log["models"]["hmm_diagnostic"] = {"status": "failed", "reason": repr(e)}
        print(f"  Diagnostic HMM failed: {e}")
    with open(os.path.join(MODELS_DIR, "regime_models.json"), "w") as f:
        json.dump(regime_log, f, indent=2, default=str)

    sig_cols = [c for c in SIGNAL_COLS.values() if c in df.columns]
    sig_path = os.path.join(RESULTS_DIR, f"signals_{DATE_TAG}.parquet")
    df[sig_cols].to_parquet(sig_path)
    print(f"  Signals persisted -> {sig_path} ({len(sig_cols)} columns)")
    write_manifest(sig_path,
                   {c: f"tournament-eligible signal derived solely from ECI total compensation ({c})" for c in sig_cols},
                   [{"description": "2021-23 wage surge present", "filter": "2021-06..2023-12",
                     "column": "eci_total_comp_pct_yoy", "check": "max > 4.8"},
                    {"description": "post-GFC deceleration", "filter": "2009-06..2010-12",
                     "column": "eci_total_comp_pct_yoy", "check": "min < 2.0"},
                    {"description": "wage growth never negative (nominal stickiness)",
                     "column": "eci_total_comp_pct_yoy", "check": "min > 0"}],
                   extra={"regime_signals": regime_log["models"]})
    hmm_ok = "hmm_2state_prob_stress" in df.columns
    return df, hmm_ok, hmm_diag


# ===================================================================
# STAGE 3: CORRELATION BATTERY (Rule C1/C2)
# ===================================================================
def _distance_corr(x, y):
    x = np.asarray(x, float)[:, None]
    y = np.asarray(y, float)[:, None]
    a = np.abs(x - x.T); b = np.abs(y - y.T)
    A = a - a.mean(0) - a.mean(1)[:, None] + a.mean()
    B = b - b.mean(0) - b.mean(1)[:, None] + b.mean()
    dcov2 = (A * B).mean(); dvx = (A * A).mean(); dvy = (B * B).mean()
    if dvx <= 0 or dvy <= 0:
        return 0.0
    return float(np.sqrt(max(dcov2, 0) / np.sqrt(dvx * dvy)))


@log_stage("3_correlations")
def stage_correlations(df):
    rows = []
    horizon_map = {"spy_fwd_1q": 63, "spy_fwd_2q": 126, "spy_fwd_4q": 252}
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwd, hd in horizon_map.items():
            v = df[[col, fwd]].dropna()
            if len(v) < CORR_N_FLOOR:
                continue
            x, y = v[col], v[fwd]
            for metric, fn in [("pearson", stats.pearsonr), ("spearman", stats.spearmanr),
                               ("kendall", stats.kendalltau)]:
                r, p = fn(x, y)
                rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": hd,
                             "metric": metric, "value": round(r, 4),
                             "p_value": round(p, 4), "n_obs": len(v)})
            rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": hd,
                         "metric": "distance", "value": round(_distance_corr(x, y), 4),
                         "p_value": np.nan, "n_obs": len(v)})
    cdf = pd.DataFrame(rows)
    path = os.path.join(MODELS_DIR, "correlations.csv")
    cdf.to_csv(path, index=False)
    write_manifest(path,
                   {"pair_name": "signal_key__forward-return-column (quarterly: 1q/2q/4q fwd)",
                    "horizon_days": "forward horizon in trading days (quarters*63)",
                    "metric": "pearson/spearman/kendall/distance", "value": "correlation coefficient",
                    "p_value": "two-sided p (NaN for distance corr); NOTE overlapping fwd windows inflate significance",
                    "n_obs": "quarters"},
                   [{"description": "values bounded", "check": "abs(value) <= 1"},
                    {"description": "quarterly horizons", "check": "horizon_days in {63,126,252}"},
                    {"description": "small-sample n floor", "check": f"min(n_obs) >= {CORR_N_FLOOR}"}])
    sig = cdf[(cdf.metric == "pearson") & (cdf.p_value < 0.05)]
    print(f"  Correlation battery: {len(cdf)} rows; {len(sig)} significant Pearson cells")
    if len(sig):
        b = sig.loc[sig.value.abs().idxmax()]
        print(f"  Strongest sig Pearson: {b.pair_name} r={b.value} p={b.p_value}")
    else:
        print("  No individually-significant Pearson cells.")
    return cdf


# ===================================================================
# STAGE 4: CORE MODELS — CCF, Granger (TY), TE, LP, QR, regressions
# ===================================================================
@log_stage("4_core_models")
def stage_core_models(df):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.ar_model import AutoReg
    from statsmodels.tsa.api import VAR

    main_sig = MAIN_SIG

    # --- 4.1 Pre-whitened CCF (quarterly lags -8..+8) ---
    # Pre-whitening is ESSENTIAL here (Dana): YoY wage inflation is highly persistent
    # (near-I(1)); the raw CCF would be dominated by autocorrelation artifacts.
    pair = df[[main_sig, "spy_ret"]].dropna()
    x = pair[main_sig]; y = pair["spy_ret"]
    best_aic, best_p = np.inf, 1
    for p in range(1, 5):   # AR order search capped at 4 (101 obs)
        try:
            aic = AutoReg(x, lags=p, old_names=False).fit().aic
            if aic < best_aic:
                best_aic, best_p = aic, p
        except Exception:
            pass
    ar_fit = AutoReg(x, lags=best_p, old_names=False).fit()
    x_w = ar_fit.resid
    coefs = ar_fit.params
    y_w = y.copy() - coefs.iloc[0]
    for i in range(1, best_p + 1):
        y_w = y_w - coefs.iloc[i] * y.shift(i)
    common = x_w.index.intersection(y_w.dropna().index)
    xw, yw = x_w.loc[common], y_w.loc[common]
    n = len(common)
    se = 1.96 / np.sqrt(n)
    rows = []
    for lag in range(-8, 9):
        if lag >= 0:
            a, b = xw.shift(lag), yw
        else:
            a, b = xw, yw.shift(-lag)
        v = pd.concat([a, b], axis=1).dropna()
        c = v.corr().iloc[0, 1] if len(v) > 30 else np.nan
        rows.append({"lag": lag, "ccf": round(c, 4) if pd.notna(c) else np.nan,
                     "lower_ci": round(-se, 4), "upper_ci": round(se, 4),
                     "significant": bool(abs(c) > se) if pd.notna(c) else False,
                     "arima_order": f"AR({best_p})", "n_obs": len(v)})
    ccf_df = pd.DataFrame(rows)
    ccf_df.to_csv(os.path.join(MODELS_DIR, "ccf_prewhitened.csv"), index=False)
    lead_sig = ccf_df[(ccf_df.lag > 0) & ccf_df.significant]
    lag_sig = ccf_df[(ccf_df.lag < 0) & ccf_df.significant]
    print(f"  [4.1] CCF (AR({best_p}) pre-whitening, n={n}, lags in QUARTERS): "
          f"sig lead(+) lags {list(lead_sig.lag)}, sig LAG(-) lags {list(lag_sig.lag)}")

    # --- 4.2 Toda-Yamamoto Granger (both directions), lags 1..4 quarters ---
    # Lag count capped at 4 (=1 year): 101 obs cannot support deep quarterly VARs
    # (lag 4 + d_max 1 already burns 10 regressors on ~95 usable obs).
    ty_rows, bylag_rows = [], []
    gdata = pair.rename(columns={main_sig: "ind", "spy_ret": "tgt"})
    d_max = 1  # YoY near-I(1) (ADF non-stat, KPSS borderline) -> TY augmentation lag 1
    try:
        p_opt = max(int(VAR(gdata).select_order(maxlags=4).aic), 1)
    except Exception:
        p_opt = 1

    def ty_wald(caused, causing, lag):
        cols = {}
        for i in range(1, lag + d_max + 1):
            cols[f"{causing}_l{i}"] = gdata[causing].shift(i)
            cols[f"{caused}_l{i}"] = gdata[caused].shift(i)
        Xd = pd.DataFrame(cols).dropna()
        yv = gdata[caused].reindex(Xd.index)
        fit = sm.OLS(yv, sm.add_constant(Xd)).fit()
        hyp = ", ".join(f"{causing}_l{i} = 0" for i in range(1, lag + 1))
        ft = fit.f_test(hyp)
        return float(ft.fvalue), float(ft.pvalue), int(ft.df_num), int(ft.df_denom)

    for lag in range(1, 5):
        try:
            for direction, caused, causing in [("indicator_to_target", "tgt", "ind"),
                                               ("target_to_indicator", "ind", "tgt")]:
                fstat, pv, dfn, dfd = ty_wald(caused, causing, lag)
                ty_rows.append({"direction": direction, "lag": lag,
                                "f_statistic": round(fstat, 4), "p_value": round(pv, 4),
                                "significant": pv < 0.05})
                if direction == "indicator_to_target":
                    bylag_rows.append({"lag": lag, "f_statistic": round(fstat, 4),
                                       "p_value": round(pv, 4), "df_num": dfn, "df_den": dfd})
        except Exception as e:
            print(f"    TY lag {lag} failed: {e}")
    ty_df = pd.DataFrame(ty_rows)
    ty_df.to_csv(os.path.join(MODELS_DIR, "granger_causality.csv"), index=False)
    pd.DataFrame(bylag_rows).to_csv(os.path.join(RESULTS_DIR, "granger_by_lag.csv"), index=False)
    fwd_sig = ty_df[(ty_df.direction == "indicator_to_target") & ty_df.significant]
    rev_sig = ty_df[(ty_df.direction == "target_to_indicator") & ty_df.significant]
    print(f"  [4.2] Toda-Yamamoto (d_max={d_max}, VAR p* by AIC={p_opt}, lags in QUARTERS 1..4):")
    print(f"        ECI->SPY significant at lags: {list(fwd_sig.lag)}")
    print(f"        SPY->ECI significant at lags: {list(rev_sig.lag)}")

    # --- 4.3 Transfer entropy (binned, permutation p; small-sample caveat) ---
    def transfer_entropy(src, dst, bins=3, lag=1):
        v = pd.concat([src, dst], axis=1).dropna()
        s = pd.qcut(v.iloc[:, 0], bins, labels=False, duplicates="drop")
        t = pd.qcut(v.iloc[:, 1], bins, labels=False, duplicates="drop")
        tt, tl, sl = t[lag:].values, t[:-lag].values, s[:-lag].values

        def H(*cols):
            arr = np.stack(cols, 1)
            _, counts = np.unique(arr, axis=0, return_counts=True)
            p = counts / counts.sum()
            return -np.sum(p * np.log(p))
        return H(tt, tl) - H(tt, tl, sl) + H(tl, sl) - H(tl)

    te_rows = []
    n_perm = 500
    rng = np.random.default_rng(42)
    for direction, src, dst in [("indicator_to_target", x, y), ("target_to_indicator", y, x)]:
        te = transfer_entropy(src, dst)
        v = pd.concat([src, dst], axis=1).dropna()
        null = [transfer_entropy(pd.Series(rng.permutation(v.iloc[:, 0].values), index=v.index),
                                 v.iloc[:, 1]) for _ in range(n_perm)]
        pv = float((np.array(null) >= te).mean())
        te_rows.append({"direction": direction, "te_value": round(float(te), 5),
                        "permutation_p_value": round(pv, 4), "n_permutations": n_perm,
                        "bandwidth": np.nan, "bin_method": "tercile_qcut_96obs_smallsample"})
    pd.DataFrame(te_rows).to_csv(os.path.join(MODELS_DIR, "transfer_entropy.csv"), index=False)
    print(f"  [4.3] Transfer entropy (~97 obs, tercile bins — LOW POWER, directional check only): "
          f"ind->tgt TE={te_rows[0]['te_value']} (p={te_rows[0]['permutation_p_value']}), "
          f"tgt->ind TE={te_rows[1]['te_value']} (p={te_rows[1]['permutation_p_value']})")

    # --- 4.4 Local projections (forward + REVERSE), quarterly horizons 1/2/4 ---
    lp_rows = []
    for direction in ["fwd", "rev"]:
        for h in [1, 2, 4]:
            if direction == "fwd":
                ycol = f"spy_fwd_{h}q"
                v = df[[main_sig, ycol]].dropna()
                xv, yv = v[main_sig], v[ycol]
            else:
                v = pd.concat([df["spy_ret"], df[main_sig].shift(-h)], axis=1).dropna()
                v.columns = ["x", "y"]; xv, yv = v["x"], v["y"]
            if len(v) < CORR_N_FLOOR:
                continue
            X = sm.add_constant(xv.values)
            nw = int(0.75 * len(v) ** (1 / 3)) + h
            fit = sm.OLS(yv.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = fit.conf_int()
            lp_rows.append({"horizon": h, "coef": round(fit.params[1], 6), "se": round(fit.bse[1], 6),
                            "ci_lower": round(ci[1][0], 6), "ci_upper": round(ci[1][1], 6),
                            "p_value": round(fit.pvalues[1], 4), "direction": direction})
    lp_df = pd.DataFrame(lp_rows)
    lp_df.to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    fwd = lp_df[lp_df.direction == "fwd"]; rev = lp_df[lp_df.direction == "rev"]
    fwd_lp_flag = bool((fwd.p_value < 0.05).any())
    rev_flag = bool((rev.p_value < 0.05).any())
    print(f"  [4.4] LP (horizons in QUARTERS) fwd (ECI->SPY) sig: {list(fwd.loc[fwd.p_value<0.05,'horizon'])}; "
          f"reverse (SPY->ECI) sig: {list(rev.loc[rev.p_value<0.05,'horizon'])} -> rev flag {rev_flag}")

    # --- 4.5 Quantile regression (1q fwd) ---
    qr_rows = []
    v = df[[main_sig, "spy_fwd_1q"]].dropna().rename(columns={main_sig: "sig", "spy_fwd_1q": "fwd"})
    for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
        try:
            qf = smf.quantreg("fwd ~ sig", v).fit(q=tau)
            ci = qf.conf_int()
            qr_rows.append({"tau": tau, "coef": round(qf.params["sig"], 6), "se": round(qf.bse["sig"], 6),
                            "p_value": round(qf.pvalues["sig"], 4),
                            "ci_lower": round(ci.loc["sig", 0], 6), "ci_upper": round(ci.loc["sig", 1], 6)})
        except Exception as e:
            print(f"    QR tau={tau} failed: {e}")
    pd.DataFrame(qr_rows).to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    print(f"  [4.5] Quantile regression: {len(qr_rows)} taus (NOTE: tail taus on ~97 obs = ~5 effective tail points; interpret loosely)")

    # --- 4.6 Predictive regressions (all signals x horizons, HAC) ---
    reg_rows = []
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwdc in FWD_COLS:
            v = df[[col, fwdc]].dropna()
            if len(v) < CORR_N_FLOOR:
                continue
            h = int(fwdc.split("_")[-1][0])
            fit = sm.OLS(v[fwdc].values, sm.add_constant(v[col].values)).fit(
                cov_type="HAC", cov_kwds={"maxlags": h + 1})
            reg_rows.append({"signal": code, "horizon": fwdc, "coef": round(fit.params[1], 6),
                             "se": round(fit.bse[1], 6), "t_stat": round(fit.tvalues[1], 3),
                             "p_value": round(fit.pvalues[1], 4), "r_squared": round(fit.rsquared, 4),
                             "n": int(fit.nobs)})
    reg_df = pd.DataFrame(reg_rows)
    reg_df.to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    print(f"  [4.6] Predictive regressions: {len(reg_df)} cells (HAC SEs; overlapping windows)")

    # --- 4.7 Diagnostics on baseline spec ---
    diag = []
    v = df[[main_sig, "spy_fwd_1q"]].dropna()
    X = sm.add_constant(v[main_sig].values)
    base = sm.OLS(v["spy_fwd_1q"].values, X).fit()
    resid = base.resid
    jb, jbp = stats.jarque_bera(resid)
    diag.append({"test": "Jarque-Bera", "statistic": round(jb, 3), "p_value": round(jbp, 4),
                 "interpretation": "Normal residuals" if jbp > 0.05 else "Non-normal — robust/HAC inference used"})
    from statsmodels.stats.diagnostic import het_breuschpagan, acorr_breusch_godfrey, linear_reset
    bp, bpp, _, _ = het_breuschpagan(resid, X)
    diag.append({"test": "Breusch-Pagan", "statistic": round(bp, 3), "p_value": round(bpp, 4),
                 "interpretation": "Homoskedastic" if bpp > 0.05 else "Heteroskedastic — HAC SEs used"})
    bg, bgp, _, _ = acorr_breusch_godfrey(base, nlags=4)
    diag.append({"test": "Breusch-Godfrey", "statistic": round(bg, 3), "p_value": round(bgp, 4),
                 "interpretation": "No serial corr" if bgp > 0.05 else "Serial correlation — HAC SEs used"})
    try:
        rs = linear_reset(base, power=3, use_f=True)
        diag.append({"test": "RESET", "statistic": round(float(rs.fvalue), 3), "p_value": round(float(rs.pvalue), 4),
                     "interpretation": "Linear form adequate" if rs.pvalue > 0.05 else "Possible nonlinearity — see quantile regression"})
    except Exception:
        pass
    pd.DataFrame(diag).to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)
    print(f"  [4.7] Diagnostics: {len(diag)} tests")

    return ccf_df, ty_df, lp_df, reg_df, rev_flag, fwd_lp_flag


# ===================================================================
# STAGE 4b: LEAD ANALYSIS (ECON-LA1, quarterly-adapted)
# ===================================================================
@log_stage("4b_lead_analysis")
def stage_lead_analysis(df):
    """ECON-LA1 quarterly adaptation: per-transform Pearson r vs 1-QUARTER-fwd return
    at leads L0..L8 QUARTERS. L0 is diagnostic-only (BLS ~1-month pub lag -> the
    quarter-Q print is first tradable in Q+1). Tradable grid = L1..L8."""
    fwd1 = df["spy_fwd_1q"]
    transforms = [c for k, c in SIGNAL_COLS.items() if c in df.columns and not c.startswith(("hmm", "markov"))]
    rows = []
    for col in transforms:
        row = {"transform": col}
        best_lead, best_abs, best_r = None, -1, None
        for L in range(0, 9):
            v = pd.concat([df[col].shift(L), fwd1], axis=1).dropna()
            if len(v) < 30:
                row[f"L{L}"] = ""
                continue
            r, p = stats.pearsonr(v.iloc[:, 0], v.iloc[:, 1])
            star = "**" if p < 0.01 else ("*" if p < 0.05 else "")
            row[f"L{L}"] = f"{r:+.3f}{star}"
            if abs(r) > best_abs:
                best_abs, best_lead, best_r = abs(r), L, r
        row["best_lead"] = f"L{best_lead}" if best_lead is not None else ""
        row["best_r"] = f"{best_r:+.3f}" if best_r is not None else ""
        rows.append(row)
    lc = pd.DataFrame(rows)
    lc_path = os.path.join(RESULTS_DIR, f"lead_correlation_{DATE_TAG}.csv")
    lc.to_csv(lc_path, index=False)
    print(f"  [ECON-LA1] lead_correlation -> {lc_path} (leads in QUARTERS; L0 diagnostic-only, not tradable)")
    return lc, lc_path


# ===================================================================
# STAGE 5: REGIME QUARTILE RETURNS
# ===================================================================
@log_stage("5_regime_quartiles")
def stage_quartiles(df):
    v = df[["eci_total_comp_pct_yoy", "spy_ret"]].dropna()
    q = pd.qcut(v["eci_total_comp_pct_yoy"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    rows = []
    for lbl in ["Q1", "Q2", "Q3", "Q4"]:
        r = v.loc[q == lbl, "spy_ret"]
        m = ann_metrics(r)
        rows.append({"quartile": lbl, "n_quarters": len(r), "ann_return": round(m["ann_return"], 4),
                     "ann_vol": round(m["ann_vol"], 4), "sharpe": round(m["sharpe"], 3),
                     "max_drawdown": round(m["max_dd"], 4)})
    qdf = pd.DataFrame(rows)
    path = os.path.join(RESULTS_DIR, "regime_quartile_returns.csv")
    qdf.to_csv(path, index=False)
    print(qdf.to_string(index=False))
    write_manifest(path,
                   {"quartile": "ECI YoY wage-growth quartile (Q1 lowest growth)", "n_quarters": "obs (quarters)",
                    "ann_return": "annualized SPY return in quartile (ratio; quarterly mean x4)",
                    "ann_vol": "annualized vol (ratio; quarterly std x sqrt(4))",
                    "sharpe": "quarterly Sharpe, sqrt(4) annualization", "max_drawdown": "max DD within quartile quarters (negative ratio)"},
                   [{"description": "4 quartiles", "check": "len == 4"},
                    {"description": "returns plausible", "check": "abs(ann_return) < 0.6"},
                    {"description": "concurrent (NOT lagged) relationship — descriptive only", "check": "informational"}])
    return qdf


# ===================================================================
# STAGE 6: TOURNAMENT ENGINE (sparse quarterly grid)
# ===================================================================
CTX = {}


def hac_t_mean(r, horizon=1):
    """HAC (Newey-West) t-stat of the mean; maxlags = max(floor(4*(n/100)^(2/9)), horizon-1)."""
    import statsmodels.api as sm
    y = pd.Series(r).dropna().values
    nw = max(int(np.floor(4 * (len(y) / 100) ** (2 / 9))), horizon - 1)
    m = sm.OLS(y, np.ones((len(y), 1))).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
    return float(m.tvalues[0]), float(m.pvalues[0]), nw


def thresholds_for(code, sig, is_mask):
    """Sparse quarterly threshold set for one lead-shifted signal: IS percentiles {25,50,75}
    (IS rows only), zero-cross for sign-meaningful signals, rolling z +/-1.0 at LB12/LB20."""
    out = {}
    is_sig = sig[is_mask].dropna()
    if len(is_sig) > 30:
        for pct in [25, 50, 75]:
            out[(f"T1_fixed_p{pct}", "LB_NA")] = is_sig.quantile(pct / 100)
    if code in ZERO_CROSS:
        out[("T4_zero", "LB_NA")] = 0.0
    for lb_name, lb in LOOKBACKS.items():
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 8))
        rm, rs = roll.mean(), roll.std()
        out[("T3_zscore_1.0", lb_name)] = rm + 1.0 * rs
        out[("T3_zscore_neg_1.0", lb_name)] = rm - 1.0 * rs
    return out


def build_position(sig, thr_name, thr, strategy):
    """Position on row t (accrues spy_ret of quarter t). Undefined (NaN) while the lagged
    signal or its rolling threshold is still warming up; earlier code traded those rows as
    cash/short because NaN comparisons evaluate to False."""
    strat, orientation = strategy.rsplit("_", 1)
    above = sig < thr if "neg_" in thr_name else sig > thr
    defined = sig.notna() & (thr.notna() if isinstance(thr, pd.Series) else True)
    pos_bool = ~above if orientation == "counter" else above
    pos = pos_bool.astype(float) if strat == "P1_long_cash" else pos_bool.astype(float) * 2 - 1
    return pos.where(defined)


def replay(work, code, thr_name, lb_name, strategy, lead, is_mask):
    sig = work[SIGNAL_COLS[code]].shift(lead)
    thr = thresholds_for(code, sig, is_mask)[(thr_name, lb_name)]
    pos = build_position(sig, thr_name, thr, strategy)
    return pos, pos * work["spy_ret"], sig, thr


def _trades(pos, mask):
    p = pos[mask].dropna()
    n = int((p.diff().abs() > 1e-9).sum())
    years = len(p) / PERIODS_PER_YEAR
    return n, (n / years if years > 0 else np.nan)


def _exposure(pos, strategy):
    p = pos.dropna()
    if not len(p):
        return np.nan
    return float((p > 0).mean()) if strategy.startswith("P3") else float(p.mean())


def run_grid(df, split, leads=LEADS):
    """Full sparse quarterly grid with IS selection (PORT_GUIDE blocks 1-3, eligibility before
    alignment). Pure: returns (tourn, selection-context); writes nothing."""
    work = df.dropna(subset=["spy_ret"]).copy()
    oos_start, oos_end, is_end = split["oos_start"], split["oos_end"], split["is_end"]
    is_full = work.index <= is_end
    oos_mask = (work.index >= oos_start) & (work.index <= oos_end)
    spy_ret = work["spy_ret"]
    strategies = [f"{s}_{o}" for s in ["P1_long_cash", "P3_long_short"] for o in ["pro", "counter"]]
    avail = {k: v for k, v in SIGNAL_COLS.items() if v in work.columns and work[v].notna().sum() >= SIG_ELIGIBLE_MIN}

    cands = []
    for code, col in avail.items():
        for lead in leads:
            sig = work[col].shift(lead)
            for (thr_name, lb_name), thr in thresholds_for(code, sig, is_full).items():
                for strategy in strategies:
                    pos = build_position(sig, thr_name, thr, strategy)
                    cands.append((code, thr_name, lb_name, strategy, lead, pos, pos * spy_ret))

    def _first(rets):
        r = rets.dropna()
        return r.index.min() if len(r) else pd.NaT

    def _own_is_n(rets):
        return int(((rets.index < oos_start) & rets.notna()).sum())

    eligible = [_own_is_n(c[6]) >= MIN_IS_N for c in cands]
    if not any(eligible):
        raise RuntimeError("No IS-eligible candidate")
    common_is_start = max(_first(c[6]) for c, ok in zip(cands, eligible) if ok)
    is_mask = (work.index >= common_is_start) & (work.index < oos_start)
    driver = sorted({f"{c[0]}/{c[1]}/{c[2]}/L{c[4]}" for c, ok in zip(cands, eligible)
                     if ok and _first(c[6]) == common_is_start})[:3]
    bh_is = ann_metrics(spy_ret[is_mask])
    bh = ann_metrics(spy_ret[oos_mask])

    rows = []
    for (code, thr_name, lb_name, strategy, lead, pos, rets), elig in zip(cands, eligible):
        is_r = rets[is_mask].dropna()
        own_start = _first(rets)
        own_mask = (work.index >= own_start) & (work.index < oos_start) if pd.notna(own_start) else is_mask & False
        own_r = rets[own_mask].dropna()
        oos_r = rets[oos_mask].fillna(0.0)                      # ECON-T4 deployable OOS
        mi, mo, m = ann_metrics(is_r), ann_metrics(own_r), ann_metrics(oos_r)
        is_tr, is_to = _trades(pos, is_mask)
        oos_tr, oos_to = _trades(pos, oos_mask)
        is_expo = _exposure(pos[is_mask], strategy)
        own_expo = _exposure(pos[own_mask], strategy)
        is_valid = bool(elig and len(is_r) >= MIN_IS_N and is_expo == is_expo and 0.05 <= is_expo <= 0.95
                        and is_r.std() > 0 and is_to < MAX_TURNOVER)
        own_valid = bool(len(own_r) >= MIN_IS_N and own_expo == own_expo and 0.05 <= own_expo <= 0.95
                         and own_r.std() > 0)
        # pre-#251 rule, comparison only: OOS Sharpe > 0.3, OOS turnover < 6, >= 20 OOS quarters
        legacy_valid = bool(m["sharpe"] > 0.3 and oos_to < MAX_TURNOVER and len(oos_r) >= 20)
        rows.append({
            "signal": code, "threshold": thr_name, "strategy": strategy, "lead_quarters": lead, "lookback": lb_name,
            "direction": ("procyclical" if (strategy.endswith("_pro") != ("neg_" in thr_name)) else "countercyclical"),
            "is_sharpe": round(mi["sharpe"], 6), "is_ann_return": round(mi["ann_return"], 6),
            "is_max_drawdown": round(mi["max_dd"], 6), "is_exposure": round(is_expo, 4) if is_expo == is_expo else np.nan,
            "is_n_trades": is_tr, "is_annual_turnover": round(is_to, 3) if is_to == is_to else np.nan,
            "is_start": is_r.index.min().date().isoformat() if len(is_r) else None,
            "is_end": is_r.index.max().date().isoformat() if len(is_r) else None,
            "common_is_start": common_is_start.date().isoformat(),
            "own_is_start": own_r.index.min().date().isoformat() if len(own_r) else None,
            "own_is_sharpe": round(mo["sharpe"], 6), "own_is_n": mo["n"], "own_is_valid": own_valid,
            "oos_sharpe": round(m["sharpe"], 6), "oos_sortino": round(m["sortino"], 6),
            "oos_calmar": round(m["calmar"], 6), "oos_ann_return": round(m["ann_return"], 6),
            "oos_ann_vol": round(m["ann_vol"], 6), "max_drawdown": round(m["max_dd"], 6),
            "win_rate": round(m["win_rate"], 4), "n_trades": oos_tr,
            "annual_turnover": round(oos_to, 3) if oos_to == oos_to else np.nan,
            "is_n": mi["n"], "oos_n": m["n"], "is_eligible": bool(elig),
            "is_ineligible_reason": "" if elig else f"insufficient IS history: n_own={_own_is_n(rets)} < MIN_IS_N={MIN_IS_N}",
            "is_valid": is_valid, "oos_valid": legacy_valid, "valid": is_valid,
            "stationarity_class": ("clean" if code in STATIONARY_CLEAN else
                                   "regime_contaminated" if code in REGIME_CONTAMINATED else "borderline_persistent")})
    rows.append({
        "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "P0_buy_and_hold", "lead_quarters": 0,
        "lookback": "LB_NA", "direction": "benchmark", "is_sharpe": round(bh_is["sharpe"], 6),
        "is_ann_return": round(bh_is["ann_return"], 6), "is_max_drawdown": round(bh_is["max_dd"], 6),
        "is_exposure": 1.0, "is_n_trades": 0, "is_annual_turnover": 0.0,
        "is_start": common_is_start.date().isoformat(), "is_end": work.index[is_mask][-1].date().isoformat(),
        "common_is_start": common_is_start.date().isoformat(), "own_is_start": None, "own_is_sharpe": np.nan,
        "own_is_n": 0, "own_is_valid": False, "oos_sharpe": round(bh["sharpe"], 6),
        "oos_sortino": round(bh["sortino"], 6), "oos_calmar": round(bh["calmar"], 6),
        "oos_ann_return": round(bh["ann_return"], 6), "oos_ann_vol": round(bh["ann_vol"], 6),
        "max_drawdown": round(bh["max_dd"], 6), "win_rate": round(bh["win_rate"], 4), "n_trades": 0,
        "annual_turnover": 0.0, "is_n": bh_is["n"], "oos_n": bh["n"], "is_eligible": False,
        "is_ineligible_reason": "benchmark", "is_valid": False, "oos_valid": False, "valid": False,
        "stationarity_class": "n_a"})
    tourn = pd.DataFrame(rows)
    assert (tourn["signal"] == "BENCHMARK").sum() == 1, "exactly one benchmark row required (ECON-T4)"

    nb = tourn["signal"] != "BENCHMARK"
    valid = tourn[tourn["valid"] & nb]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    # ECON-T3 cascade on the IS objective (explicit sort, not pandas-order dependent)
    keys = ["is_sharpe", "is_ann_return", "is_max_drawdown", "is_n_trades", "signal", "threshold",
            "strategy", "lookback", "lead_quarters"]
    asc = [False, False, False, True, True, True, True, True, True]
    ranked = valid.sort_values(keys, ascending=asc, kind="mergesort")
    wi = ranked.index[0]
    tied, tie_step = valid, 5
    for step, k in enumerate(["is_sharpe", "is_ann_return", "is_max_drawdown", "is_n_trades"], 1):
        tied = tied[(tied[k] - tourn.loc[wi, k]).abs() <= 1e-9]
        if len(tied) == 1:
            tie_step = step
            break
    own_pool = tourn[tourn["own_is_valid"] & nb]
    oi = own_pool.sort_values(["own_is_sharpe", "signal", "threshold"], ascending=[False, True, True],
                              kind="mergesort").index[0]
    legacy_pool = tourn[tourn["oos_valid"] & nb]
    li = (legacy_pool.sort_values(["oos_sharpe", "oos_ann_return", "signal", "threshold"],
                                  ascending=[False, False, True, True], kind="mergesort").index[0]
          if len(legacy_pool) else None)
    tourn["is_rank"] = tourn["is_sharpe"].where(nb & tourn["valid"]).rank(ascending=False, method="min")
    tourn["oos_rank"] = tourn["oos_sharpe"].where(nb & tourn["valid"]).rank(ascending=False, method="min")
    distinct = valid.drop_duplicates(["signal", "strategy", "lead_quarters", "is_sharpe", "oos_sharpe"])
    sp = stats.spearmanr(valid["is_sharpe"], valid["oos_sharpe"]).correlation
    sel = dict(wi=wi, oi=oi, li=li, tie_step=tie_step, tied=tied, common_is_start=common_is_start,
               n_cands=len(cands), n_eligible=int(sum(eligible)), n_inel=int(len(cands) - sum(eligible)),
               bh_is=bh_is, bh=bh, n_distinct=len(distinct), spearman=float(sp), driver=driver,
               ranked=ranked)
    return tourn, sel


@log_stage("6_tournament")
def stage_tournament(df, sp):
    oos_n, n_q = sp["oos_n"], sp["n_q"]
    oos_start, is_end, oos_end = sp["oos_start"], sp["is_end"], sp["oos_end"]
    n_months = n_q * 3
    print(f"  Sample: {n_q} quarters -> {oos_end.date()}; OOS {oos_n} quarters {oos_start.date()} -> {oos_end.date()}")
    split = {
        "owner": "evan", "split_policy_id": "v1_max36_25pct_cap120",
        "in_sample_end": is_end.strftime("%Y-%m-%d"), "oos_start": oos_start.strftime("%Y-%m-%d"),
        "oos_end": oos_end.strftime("%Y-%m-%d"), "sample_size_months": n_months,
        "justification": (
            f"Policy v1_max36_25pct_cap120 applied in native QUARTERLY units: total sample {n_q} quarters "
            f"({n_months} months). span = min(max(12q, round({n_q}*0.25)), 40q) = {oos_n} quarters. "
            f"OOS {oos_start.date()}..{oos_end.date()} covers COVID, the 2021-23 wage-inflation surge and the 2022 "
            f"tightening bear market. {oos_n} quarterly observations is a small OOS sample. IS = {n_q - oos_n} quarters; "
            f"the regime models (HMM, Markov-switching) may only be fit on IS rows. No structural-break exclusion applied."),
    }
    with open(os.path.join(RESULTS_DIR, "oos_split_record.json"), "w") as f:
        json.dump(split, f, indent=2)

    split_ts = {"oos_start": oos_start, "oos_end": oos_end, "is_end": is_end}
    tdf, sel = run_grid(df, split_ts)
    CTX["selection"] = sel
    tpath = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _tournament_io import write_tournament
    write_tournament(tdf, tpath)
    side_cols = ["signal", "threshold", "strategy", "lookback", "direction", "lead_quarters", "is_start", "is_end",
                 "is_n", "is_sharpe", "own_is_start", "own_is_n", "own_is_sharpe", "oos_sharpe", "oos_ann_return",
                 "max_drawdown", "n_trades", "oos_n", "is_rank", "oos_rank"]
    side = [dict(role="primary_is_selected_common_start", **tdf.loc[sel["wi"], side_cols].to_dict()),
            dict(role="sensitivity_is_selected_own_start", **tdf.loc[sel["oi"], side_cols].to_dict())]
    if sel["li"] is not None:
        side.append(dict(role="legacy_oos_selected", **tdf.loc[sel["li"], side_cols].to_dict()))
    pd.DataFrame(side).to_csv(os.path.join(RESULTS_DIR, f"legacy_oos_selection_{DATE_TAG}.csv"), index=False)

    strat_pop = tdf[tdf.signal != "BENCHMARK"]
    n_valid = int(strat_pop["valid"].sum())
    w = tdf.loc[sel["wi"]]
    print(f"  common IS start {sel['common_is_start'].date()} (set by {sel['driver']}); {sel['n_inel']} ineligible")
    print(f"  Combos: {len(strat_pop)} + 1 benchmark; IS-valid {n_valid} ({sel['n_distinct']} distinct series)")
    print(f"  WINNER (IS argmax): {w.signal}/{w.threshold}/{w.strategy}/L{w.lead_quarters}q/{w.lookback} "
          f"IS {w.is_sharpe:.4f} OOS {w.oos_sharpe:.4f} (B&H IS {sel['bh_is']['sharpe']:.4f} OOS {sel['bh']['sharpe']:.4f}); "
          f"tie step {sel['tie_step']}")
    if sel["li"] is not None:
        lw = tdf.loc[sel["li"]]
        print(f"  legacy OOS-argmax on this grid: {lw.signal}/{lw.threshold}/{lw.strategy}/L{lw.lead_quarters}q/"
              f"{lw.lookback} OOS {lw.oos_sharpe:.4f}")
    print(f"  Spearman(IS, OOS) over IS-valid = {sel['spearman']:.3f}")

    manifest = {
        "file": os.path.basename(tpath), "pair_id": PAIR_ID,
        "frequency": "QUARTERLY",
        "annualization": "Sharpe = mean/std*sqrt(4); ann_return = mean*4; ann_vol = std*sqrt(4)",
        "grid": {"signals": sorted(strat_pop["signal"].unique().tolist()),
                 "thresholds": "T1_fixed_p{25,50,75} (IS percentiles), T4_zero (accel/yoy_accel/dev_trend), T3_zscore_{+1.0,-1.0} x {LB12,LB20}",
                 "strategies": ["P1_long_cash_{pro,counter}", "P3_long_short_{pro,counter}"],
                 "leads_quarters": LEADS, "lookbacks": list(LOOKBACKS.keys()) + ["LB_NA"],
                 "regime_signals": "hmm_stress and markov_regime EXCLUDED: a causal (IS-only) fit needs >= 100 IS rows; ECI has 72 IS quarters (core_models/regime_models.json)"},
        "selection": "argmax IS Sharpe on the common IS window [common_is_start, oos_start); OOS never consulted (is_valid/valid). oos_valid = pre-#251 OOS rule, comparison only",
        "validity": f"IS window only: eligible (own IS n >= {MIN_IS_N}), is_n >= {MIN_IS_N}, IS exposure in [0.05, 0.95] (P3: share of quarters long), IS std > 0, IS turnover < {MAX_TURNOVER}/yr",
        "warmup": "positions are NaN (not traded, excluded from IS metrics) until the lagged signal and its rolling threshold are defined; OOS scored deployable (fillna 0)",
        "units": "oos_ann_return / oos_ann_vol / max_drawdown are RATIOS (decimal), not percent",
        "lead_column_note": "lead_quarters (QUARTERS)",
        "total_strategy_rows": len(strat_pop), "valid_strategy_rows": n_valid,
        "common_is_start": sel["common_is_start"].date().isoformat(), "common_is_start_set_by": sel["driver"],
        "spearman_is_vs_oos": round(sel["spearman"], 4),
        "benchmark_row": "signal==BENCHMARK, valid=False per ECON-T4",
        "execution_lag": "position_t = rule(signal_{t-lead}), lead >= 1 quarter",
        "small_sample_flag": f"OOS window {oos_n} QUARTERS",
        "cost_note": "returns are gross of costs; cost sensitivity in tournament_validation",
        "generated_at": NOW_ISO,
    }
    with open(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return tdf, split, tpath


# ===================================================================
# STAGE 6b: LEAD TOURNAMENT (ECON-LT1) + GH #13 winner-curve / envelope
# ===================================================================
@log_stage("6b_lead_tournament")
def stage_lead_tournament(df, split, tdf, winner):
    """Per-lead summaries. best_oos_sharpe is an OOS-argmax (selection-biased context); the
    is_best_* columns are the IS-selected row at each lead."""
    valid = tdf[(tdf.signal != "BENCHMARK") & tdf.valid]
    same = tdf[(tdf.signal == winner["signal"]) & (tdf.threshold == winner["threshold"]) &
               (tdf.strategy == winner["strategy"]) & (tdf.lookback == winner["lookback"])]
    rows, env_rows, wc_rows = [], [], []
    for L in LEADS:
        g = valid[valid.lead_quarters == L]
        wrow = same[same.lead_quarters == L]
        wc_rows.append({"lead_quarters": L,
                        "is_sharpe": round(float(wrow.iloc[0].is_sharpe), 4) if len(wrow) else np.nan,
                        "oos_sharpe": round(float(wrow.iloc[0].oos_sharpe), 4) if len(wrow) else np.nan,
                        "is_valid": bool(wrow.iloc[0].valid) if len(wrow) else False,
                        "is_published_winner": bool(L == int(winner["lead_quarters"]))})
        pool = pd.concat([g, wrow])
        if len(g) == 0:
            rows.append({"lead_quarters": L, "n_valid": 0})
        else:
            top, bi = g.loc[g.oos_sharpe.idxmax()], g.loc[g.is_sharpe.idxmax()]
            rows.append({"lead_quarters": L, "n_valid": int(len(g)),
                         "best_oos_sharpe": round(float(top.oos_sharpe), 4),
                         "median_oos_sharpe": round(float(g.oos_sharpe.median()), 4),
                         "p25_oos_sharpe": round(float(g.oos_sharpe.quantile(0.25)), 4),
                         "p75_oos_sharpe": round(float(g.oos_sharpe.quantile(0.75)), 4),
                         "best_signal": top.signal, "best_threshold": top.threshold,
                         "best_strategy": top.strategy, "best_max_dd": round(float(top.max_drawdown), 4),
                         "best_is_sharpe": round(float(bi.is_sharpe), 4),
                         "median_is_sharpe": round(float(g.is_sharpe.median()), 4),
                         "is_best_signal": bi.signal, "is_best_threshold": bi.threshold,
                         "is_best_strategy": bi.strategy, "is_best_oos_sharpe": round(float(bi.oos_sharpe), 4)})
        if len(pool):
            b = pool.loc[pool.oos_sharpe.idxmax()]
            env_rows.append({"lead_quarters": L, "best_oos_sharpe": round(float(b.oos_sharpe), 4),
                             "best_signal": b.signal, "best_is_clean": True,
                             "best_clean_oos_sharpe": round(float(b.oos_sharpe), 4), "best_clean_signal": b.signal,
                             "note": "OOS-argmax over IS-valid rows plus the winner rule (context, selection-biased)"})
    lt = pd.DataFrame(rows)
    lt_path = os.path.join(RESULTS_DIR, f"lead_tournament_{DATE_TAG}.csv")
    lt.to_csv(lt_path, index=False)
    wc = pd.DataFrame(wc_rows)
    wc_path = os.path.join(RESULTS_DIR, f"lead_winner_curve_{DATE_TAG}.csv")
    wc.to_csv(wc_path, index=False)
    env = pd.DataFrame(env_rows)
    env_path = os.path.join(RESULTS_DIR, f"lead_clean_envelope_{DATE_TAG}.csv")
    env.to_csv(env_path, index=False)
    for L in LEADS:
        a = wc.loc[wc.lead_quarters == L, "oos_sharpe"].iloc[0]
        e = env.loc[env.lead_quarters == L, "best_oos_sharpe"]
        if pd.notna(a) and len(e) and a > float(e.iloc[0]) + 1e-9:
            raise SystemExit(f"COHERENCE VIOLATION at L{L}")
    vl = lt[lt.n_valid > 0]
    L_star = int(vl.loc[vl.best_oos_sharpe.idxmax(), "lead_quarters"]) if len(vl) else -1
    best_at_grid = float(vl.best_oos_sharpe.max()) if len(vl) else np.nan
    gate = "CHARTS-ONLY (full grid scanned natively; winner selected by IS Sharpe)"
    peak_lead = int(wc.loc[wc.oos_sharpe.idxmax(), "lead_quarters"]) if wc.oos_sharpe.notna().any() else -1
    print(f"  [ECON-LT1] {lt_path}; winner curve OOS {dict(zip(wc.lead_quarters, wc.oos_sharpe))}")
    return lt, lt_path, L_star, best_at_grid, gate, wc, peak_lead


# ===================================================================
# STAGE 7: WINNER (IS-selected) + artifacts
# ===================================================================
@log_stage("7_winner_artifacts")
def stage_winner(df, tdf, split, tpath):
    sel = CTX["selection"]
    winner = tdf.loc[sel["wi"]]
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid]
    n_valid = len(cand)
    median_sharpe = float(cand["is_sharpe"].median())
    resolved_at = sel["tie_step"]
    n_tied = int((cand["is_sharpe"] - winner["is_sharpe"]).abs().le(1e-9).sum())
    print(f"  IS-valid strategies: {n_valid}; winner: {winner['signal']}/{winner['threshold']}/"
          f"{winner['strategy']}/L{winner['lead_quarters']}q/{winner['lookback']} (tie step {resolved_at})")

    if resolved_at > 1:
        tie_pool = sel["tied"] if resolved_at < 5 else cand[(cand["is_sharpe"] - winner["is_sharpe"]).abs() <= 1e-9]
        lines = [f"# Tournament Tie Note - {PAIR_ID} ({DATE_TAG})", "",
                 f"Winner resolved at IS cascade step {resolved_at} (is_sharpe, is_ann_return, is_max_drawdown, "
                 "is_n_trades, then names).", "",
                 cand[(cand["is_sharpe"] - winner["is_sharpe"]).abs() <= 1e-9][
                     ["signal", "threshold", "strategy", "lead_quarters", "lookback", "is_sharpe",
                      "is_ann_return", "is_max_drawdown", "is_n_trades", "oos_sharpe"]].to_markdown(index=False)]
        with open(os.path.join(RESULTS_DIR, "tournament_tie_note.md"), "w") as f:
            f.write("\n".join(lines))

    work = df.dropna(subset=["spy_ret"])
    is_full = work.index <= split["in_sample_end"]
    position, strat_ret, sig_lagged, thr = replay(work, winner["signal"], winner["threshold"], winner["lookback"],
                                                 winner["strategy"], int(winner["lead_quarters"]), is_full)
    spy_ret = work["spy_ret"]
    oos_mask = (spy_ret.index >= split["oos_start"]) & (spy_ret.index <= split["oos_end"])
    m = ann_metrics(strat_ret[oos_mask].fillna(0.0))
    rec = {}
    for key, computed, reported, tol in [
            ("oos_sharpe", m["sharpe"], float(winner["oos_sharpe"]), 1e-5),
            ("oos_max_drawdown", m["max_dd"], float(winner["max_drawdown"]), 1e-5),
            ("oos_ann_return", m["ann_return"], float(winner["oos_ann_return"]), 1e-5)]:
        diff = computed - reported
        rec[key] = {"computed": round(float(computed), 6), "reported_tournament": reported,
                    "diff": round(float(diff), 6), "tolerance": tol,
                    "verdict": "PASS" if abs(diff) <= tol else "FAIL"}
    assert all(v["verdict"] == "PASS" for v in rec.values()), f"ECON-SR1 reconciliation FAILED: {rec}"
    print("  ECON-SR1 reconciliation: PASS on all three headline metrics")

    pos_f = position.reindex(spy_ret.index).fillna(0.0)
    sr_f = strat_ret.reindex(spy_ret.index).fillna(0.0)
    sr = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"), "position": pos_f.values,
                       "strategy_return": sr_f.values, "bh_return": spy_ret.values})
    sr_path = os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv")
    sr.to_csv(sr_path, index=False)
    with open(os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}_meta.json"), "w") as f:
        json.dump({"pair_id": PAIR_ID, "artifact": os.path.basename(sr_path),
                   "produced_by": "scripts/pair_pipeline_eci_total_comp_spy.py", "rule": "ECON-SR1",
                   "source": "pipeline_native_derivation (same replay() as the tournament)",
                   "returns_file": os.path.relpath(DATA_PATH, BASE_DIR), "coverage_start": str(spy_ret.index[0].date()),
                   "coverage_end": str(spy_ret.index[-1].date()), "frequency": "quarterly",
                   "annualization": "Sharpe sqrt(4); ann_return mean*4",
                   "oos_start": split["oos_start"], "oos_end": split["oos_end"],
                   "position_semantics": (f"position on row t = return-accrual weight for quarter t; signal lagged "
                                          f"{int(winner['lead_quarters'])} quarter(s); strategy_return = position * bh_return; "
                                          "warm-up rows (signal or threshold undefined) written as 0"),
                   "reconciliation": {k: {"computed": v["computed"], "reported_winner_summary": v["reported_tournament"],
                                          "diff": v["diff"], "tolerance": v["tolerance"], "verdict": v["verdict"]}
                                      for k, v in rec.items()},
                   "generated_at": NOW_ISO, "generated_by": "Econ Evan (fix261016_hmm_port_eci_nhs)"}, f, indent=2)

    log = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"),
                        "signal_value": sig_lagged.reindex(spy_ret.index).round(4),
                        "threshold": (thr.reindex(spy_ret.index).round(4) if isinstance(thr, pd.Series) else np.round(thr, 4)),
                        "position": pos_f, "spy_return": spy_ret.round(6), "strategy_return": sr_f.round(6)})
    log["cumulative_return"] = ((1 + log["strategy_return"]).cumprod() - 1).round(6)
    log.to_csv(os.path.join(RESULTS_DIR, "winner_trade_log.csv"), index=False)

    spy_px = df["spy"].reindex(spy_ret.index)
    broker_rows = []
    cum = (1 + sr_f).cumprod()
    prev = 0.0; capital = 10000.0
    sig_disp = f"{winner['signal']} ({SIGNAL_COLS[winner['signal']]})"
    for dt in spy_ret.index:
        p = float(pos_f.loc[dt])
        if abs(p - prev) > 1e-9:
            side = "BUY" if p > prev else "SELL"
            notional = abs(p - prev) * capital
            sv = sig_lagged.loc[dt]; th = thr.loc[dt] if isinstance(thr, pd.Series) else thr
            broker_rows.append({"trade_date": dt.strftime("%Y-%m-%d"), "side": side, "instrument": TARGET_SYMBOL,
                                "quantity_pct": round(abs(p) * 100, 1),
                                "price": round(float(spy_px.loc[dt]), 4) if pd.notna(spy_px.loc[dt]) else np.nan,
                                "notional_usd": round(notional, 2), "commission_bps": COST_BPS,
                                "commission_usd": round(notional * COST_BPS / 10000, 2),
                                "cum_pnl_pct": round((cum.loc[dt] - 1) * 100, 4),
                                "reason": (f"{winner['strategy']}: {sig_disp} = {sv:.3f} vs threshold "
                                           f"{th:.3f} - position {prev*100:.0f}% -> {p*100:.0f}%"
                                           if pd.notna(sv) and pd.notna(th) else "position change")})
            prev = p
    broker_path = os.path.join(RESULTS_DIR, "winner_trades_broker_style.csv")
    with open(broker_path, "w") as f:
        f.write(f"# Simulated trade record based on backtest signals. No real trades were executed. "
                f"Starting capital: $10000. Commission: {COST_BPS} bps. Pair: {PAIR_ID} (QUARTERLY rebalance). "
                f"Strategy: {winner['strategy']} on {sig_disp}, threshold {winner['threshold']}, "
                f"lead L{winner['lead_quarters']} quarters, {winner['lookback']}.\n")
        pd.DataFrame(broker_rows).to_csv(f, index=False)
    print(f"  Trade logs written ({len(log)} rows, {len(broker_rows)} broker events)")
    CTX["winner_series"] = dict(position=position, strat_ret=strat_ret, work=work, is_full=is_full)
    return (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
            pos_f, sr_f, sig_lagged, thr, cand)


# ===================================================================
# STAGE 7b: LOOK-AHEAD AUDIT (superseded smoothed-HMM rule vs causal)
# ===================================================================
@log_stage("7b_lookahead_audit")
def stage_lookahead_audit(df, split, hmm_diag):
    """Score the PREVIOUSLY PUBLISHED rule (hmm_stress / T3_zscore_1.0 / LB12 / P1_long_cash_counter /
    L4q) on (a) the committed smoothed full-sample HMM column (signals_{PREV_TAG}.parquet, immutable,
    not re-fitted) with the old warm-up semantics, which must reproduce the published OOS Sharpe,
    and (b) the diagnostic causal HMM (IS-only fit on 72 quarters, forward-filtered; not traded)."""
    prev_ws = json.load(open(os.path.join(RESULTS_DIR, "winner_summary.json")))
    prev_sel = prev_ws.get("selection", {})
    if prev_sel.get("objective") == "max_is_sharpe":           # rerun on an already-ported tree
        prev = prev_sel["previously_published"]
    else:
        rw = prev_sel["raw_winner_row"]
        prev = {"signal": rw["signal"], "threshold": rw["threshold"], "strategy": rw["strategy"],
                "lead_quarters": int(rw["lead_value"]), "lookback": prev_ws["lookback"],
                "oos_sharpe": float(prev_ws["oos_sharpe"]), "source": f"winner_summary.json ({PREV_TAG})"}
    work = df.dropna(subset=["spy_ret"]).copy()
    old = pd.read_parquet(os.path.join(RESULTS_DIR, f"signals_{PREV_TAG}.parquet"))["hmm_2state_prob_stress"]
    work["smoothed_fullsample"] = old.reindex(work.index)
    work["causal_filtered_diag"] = hmm_diag.prob.reindex(work.index) if hmm_diag is not None else np.nan
    is_full = work.index <= split["in_sample_end"]
    oos = (work.index >= split["oos_start"]) & (work.index <= split["oos_end"])

    def score(col, lead, legacy_warmup):
        sig = work[col].shift(lead)
        thr = thresholds_for("hmm_stress", sig, is_full)[(prev["threshold"], prev["lookback"])]
        pos = build_position(sig, prev["threshold"], thr, prev["strategy"])
        if legacy_warmup:   # pre-port semantics: undefined comparisons -> False -> counter = long
            above = sig > thr
            pos = (~above).astype(float) if prev["strategy"].endswith("counter") else above.astype(float)
        r = (pos * work["spy_ret"])[oos].fillna(0.0)
        a = ann_metrics(r)
        t, p, nw = hac_t_mean(r)
        return {"oos_sharpe": round(a["sharpe"], 6), "oos_ann_return": round(a["ann_return"], 6),
                "oos_max_drawdown": round(a["max_dd"], 6), "hac_t": round(t, 3), "hac_p": round(p, 4),
                "hac_maxlags": nw, "oos_exposure": round(float(pos[oos].mean()), 4)}

    rows = []
    for col in ["smoothed_fullsample", "causal_filtered_diag"]:
        for lead in sorted({int(prev["lead_quarters"])} | {1}):
            rows.append({"probabilities": col, "lead_quarters": lead, **score(col, lead, legacy_warmup=True)})
    rep = next(r for r in rows if r["probabilities"] == "smoothed_fullsample" and r["lead_quarters"] == int(prev["lead_quarters"]))
    reproduced = abs(rep["oos_sharpe"] - float(prev["oos_sharpe"])) < 1e-4
    assert reproduced, f"old smoothed replay {rep['oos_sharpe']} != published {prev['oos_sharpe']} (data drift)"
    bh = ann_metrics(work["spy_ret"][oos])
    out = {"rule": (f"{prev['signal']} / {prev['threshold']} / {prev['lookback']} / {prev['strategy']} / "
                    f"L{prev['lead_quarters']}q; strat_ret = position_t * spy_ret_t"),
           "previously_published": prev, "oos_window": [split["oos_start"], split["oos_end"]],
           "published_reproduced_from_committed_smoothed_column": bool(reproduced),
           "reproduction_note": "published value is rounded to 4 d.p.; replay matches to < 1e-4",
           "causal_fit": hmm_diag.summary() if hmm_diag is not None else None,
           "causal_status": ("DIAGNOSTIC ONLY: the causal HMM is fit on the 72 IS quarters with an explicit override "
                             "(min_is_rows=40); the helper requires 100 IS rows for a traded signal, so hmm_stress is "
                             "not in the 20261016 tournament"),
           "rows": rows, "bh_oos_sharpe": round(bh["sharpe"], 6)}
    d = (work["smoothed_fullsample"] - work["causal_filtered_diag"])[oos]
    out["corr_smoothed_minus_filtered_vs_same_quarter_spy_ret_oos"] = round(float(d.corr(work["spy_ret"][oos])), 4)
    with open(os.path.join(RESULTS_DIR, f"hmm_lookahead_audit_{DATE_TAG}.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    for r in rows:
        print(f"  {r['probabilities']:22s} L{r['lead_quarters']}: OOS Sharpe {r['oos_sharpe']:.4f}  HAC t {r['hac_t']:.2f}")
    CTX["audit"] = out
    return out


# ===================================================================
# STAGE 8: CROSS-PERIOD ANALYSES (ECON-CP1)
# ===================================================================
@log_stage("8_cross_period")
def stage_cross_period(df, winner, split, position, strat_ret, sig_lagged):
    import statsmodels.api as sm
    with open(os.path.join(SCHEMA_DIR, "episode_registry.json")) as f:
        reg = json.load(f)
    block = reg.get("production", reg["_fallback"])
    episodes = block["episodes"] if isinstance(block, dict) else block
    oos = strat_ret[(strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])]
    rows = []; pos_eps = 0; eval_eps = 0
    for ep in episodes:
        sub = oos[(oos.index >= ep["start"]) & (oos.index <= ep["end"])].dropna()
        if len(sub) < 3:
            rows.append({"episode": ep["slug"], "start_date": ep["start"], "end_date": ep["end"],
                         "n_trading_days": len(sub) * 63, "ann_sharpe": np.nan, "win_rate": np.nan,
                         "max_drawdown": np.nan, "data_status": "insufficient_data", "durability_verdict": ""})
            continue
        m = ann_metrics(sub); eval_eps += 1; pos_eps += int(m["sharpe"] > 0)
        rows.append({"episode": ep["slug"], "start_date": str(sub.index[0].date()), "end_date": str(sub.index[-1].date()),
                     "n_trading_days": len(sub) * 63, "ann_sharpe": round(m["sharpe"], 4),
                     "win_rate": round(m["win_rate"], 4), "max_drawdown": round(m["max_dd"], 4),
                     "data_status": "validated", "durability_verdict": ""})
    if eval_eps >= 3:
        verdict = "durable" if pos_eps >= 3 else ("conditionally_durable" if pos_eps == 2 else "episode_concentrated")
    else:
        verdict = ("conditionally_durable" if pos_eps == eval_eps and eval_eps > 0 else "episode_concentrated") if eval_eps else "insufficient_data"
    if rows:
        rows[-1]["durability_verdict"] = verdict
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "subperiod_sharpe.csv"), index=False)
    print(f"  CP1-A: {eval_eps} episodes evaluable within OOS (quarterly data — most registry episodes "
          f"are pre-OOS or too short in quarters), {pos_eps} positive -> {verdict}")

    v = pd.concat([sig_lagged.rename("sig"), df["spy_fwd_1q"]], axis=1).dropna()
    full_r = v["sig"].corr(v["spy_fwd_1q"])
    roll = v["sig"].rolling(16).corr(v["spy_fwd_1q"])   # 16 quarters = 4yr window
    out = pd.DataFrame({"date": v.index.strftime("%Y-%m-%d"), "rolling_corr": roll.round(4).values, "n_obs": 16,
                        "window_start": v.index.to_series().shift(15).dt.strftime("%Y-%m-%d").values}).dropna(subset=["rolling_corr"])
    out.to_csv(os.path.join(RESULTS_DIR, f"rolling_correlation_{PAIR_ID}.csv"), index=False)
    same_sign = float((np.sign(roll.dropna()) == np.sign(full_r)).mean()) if roll.dropna().size else np.nan
    stab = ("sign_stable" if same_sign >= 0.7 else "moderately_stable" if same_sign >= 0.5 else "sign_unstable")
    print(f"  CP1-B: full-sample r={full_r:.3f}, sign stability {same_sign:.2f} (16Q window) -> {stab}")

    reg_v = pd.concat([sig_lagged.rename("sig"), df["spy_ret"]], axis=1).dropna()
    yv = reg_v["spy_ret"].values; Xv = sm.add_constant(reg_v["sig"].values)
    n = len(yv); lo, hi = int(n * 0.15), int(n * 0.85)
    full = sm.OLS(yv, Xv).fit(); k = Xv.shape[1]

    def sup_f(y, X):
        best, bidx = -np.inf, lo
        for b in range(lo, hi):
            s1 = sm.OLS(y[:b], X[:b]).fit().ssr; s2 = sm.OLS(y[b:], X[b:]).fit().ssr
            fval = ((sm.OLS(y, X).fit().ssr - s1 - s2) / k) / ((s1 + s2) / (len(y) - 2 * k))
            if fval > best:
                best, bidx = fval, b
        return best, bidx

    f_obs, b_idx = sup_f(yv, Xv)
    rng = np.random.default_rng(42); null = []
    resid = full.resid; fitted = full.fittedvalues
    for _ in range(300):
        y_b = fitted + rng.choice(resid, size=n, replace=True)
        null.append(sup_f(y_b, Xv)[0])
    p_break = float((np.array(null) >= f_obs).mean())
    break_date = str(reg_v.index[b_idx].date()); flagged = p_break < 0.10
    sb = {"pair_id": PAIR_ID, "test": "Quandt-Andrews unknown breakpoint (sup-F, residual-bootstrap p, 300 reps; quarterly)",
          "sample_start": str(reg_v.index[0].date()), "sample_end": str(reg_v.index[-1].date()), "n_obs": n,
          "trimming_pct": 0.15, "break_date": break_date, "f_stat": round(float(f_obs), 4),
          "p_value": round(p_break, 4), "flagged": flagged,
          "flag_message": ("Structural break detected — interpret cross-period results with caution." if flagged else None),
          "rolling_corr_sign_stability": round(same_sign, 4) if pd.notna(same_sign) else None,
          "rolling_corr_stability_verdict": stab, "cp2_note": "CP2 skipped — regime_story not set in signal_scope.json"}
    with open(os.path.join(RESULTS_DIR, f"structural_break_{PAIR_ID}.json"), "w") as f:
        json.dump(sb, f, indent=2)
    print(f"  CP1-C: sup-F={f_obs:.2f} at {break_date}, bootstrap p={p_break:.3f}, flagged={flagged}")
    return verdict, stab, sb, full_r


# ===================================================================
# STAGE 9: VALIDATION (bootstrap, stress, tx-costs)
# ===================================================================
@log_stage("9_validation")
def stage_validation(df, tdf, split, strat_ret):
    spy_oos = df["spy_ret"][(df.index >= split["oos_start"]) & (df.index <= split["oos_end"])].dropna()
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid]
    # winner + next four DISTINCT IS-ranked candidates (no OOS ranking)
    wi = CTX["selection"]["wi"]
    distinct = CTX["selection"]["ranked"].drop_duplicates(["signal", "strategy", "lead_quarters", "is_sharpe", "oos_sharpe"])
    top5 = pd.concat([tdf.loc[[wi]], distinct.drop(index=wi, errors="ignore").head(4)])
    rng = np.random.default_rng(42); boot = np.zeros(5000)
    for b in range(5000):
        s = rng.choice(spy_oos.values, size=len(spy_oos), replace=True)
        boot[b] = (s.mean() / s.std()) * ANN if s.std() > 0 else 0
    rows = [{"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
             "lead_quarters": r.lead_quarters, "lookback": r.lookback, "oos_sharpe": r.oos_sharpe,
             "is_sharpe": r.is_sharpe,
             "bootstrap_p_value": round(float((boot >= r.oos_sharpe).mean()), 4),
             "significant_at_5pct": bool((boot >= r.oos_sharpe).mean() < 0.05),
             "note": "share of iid-resampled B&H OOS Sharpes >= this row's OOS Sharpe; not a selection-bias test"}
            for r in top5.itertuples()]
    pd.DataFrame(rows).to_csv(os.path.join(VALID_DIR, "bootstrap.csv"), index=False)

    stress = {"COVID": ("2020-01-01", "2020-12-31"), "Rate_Hike_2022": ("2022-01-01", "2023-06-30"),
              "Wage_Surge_2021_23": ("2021-06-01", "2023-12-31")}
    srows = []
    for nm, (s, e) in stress.items():
        sub_bh = df["spy_ret"][(df.index >= s) & (df.index <= e)].dropna()
        sub_st = strat_ret[(strat_ret.index >= s) & (strat_ret.index <= e)].dropna()
        if len(sub_bh) > 2:
            srows.append({"period": nm, "start": s, "end": e, "n_quarters": len(sub_bh),
                          "buy_hold_sharpe": round(ann_metrics(sub_bh)["sharpe"], 4),
                          "buy_hold_return_pct": round(sub_bh.sum() * 100, 2),
                          "winner_sharpe": round(ann_metrics(sub_st)["sharpe"], 4) if len(sub_st) > 2 else np.nan,
                          "winner_return_pct": round(sub_st.sum() * 100, 2) if len(sub_st) > 2 else np.nan})
    pd.DataFrame(srows).to_csv(os.path.join(VALID_DIR, "stress_tests.csv"), index=False)

    tx = []
    for r in top5.itertuples():
        for bps in [0, 5, 10, 25, 50]:
            ann_cost = r.annual_turnover * bps / 10000
            net = r.oos_sharpe - ann_cost / r.oos_ann_vol if r.oos_ann_vol > 0 else r.oos_sharpe
            tx.append({"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
                       "tx_cost_bps": bps, "gross_sharpe": r.oos_sharpe, "net_sharpe_approx": round(net, 4)})
    pd.DataFrame(tx).to_csv(os.path.join(VALID_DIR, "transaction_costs.csv"), index=False)
    print(f"  bootstrap (top{len(top5)}), stress ({len(srows)} periods), tx-cost grid saved")
    return rows


# ===================================================================
# MAIN
# ===================================================================
def main():
    t0 = time.time()
    df = stage_load()
    sp = compute_split(df)
    df, hmm_ok, hmm_diag = stage_signals(df, sp["oos_start"])
    corr_df = stage_correlations(df)
    ccf_df, ty_df, lp_df, reg_df, rev_flag, fwd_lp_flag = stage_core_models(df)
    lc, lc_path = stage_lead_analysis(df)
    qdf = stage_quartiles(df)
    tdf, split, tpath = stage_tournament(df, sp)
    (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
     position, strat_ret, sig_lagged, thr, cand) = stage_winner(df, tdf, split, tpath)
    lt, lt_path, L_star, best_at_grid, gate, wc, peak_lead = stage_lead_tournament(df, split, tdf, winner)
    stage_lookahead_audit(df, split, hmm_diag)
    verdict, stab, sb, full_r = stage_cross_period(df, winner, split, position, strat_ret, sig_lagged)
    boot_rows = stage_validation(df, tdf, split, strat_ret)
    winner_boot_p = boot_rows[0]["bootstrap_p_value"] if boot_rows else np.nan

    bh = tdf[tdf.signal == "BENCHMARK"].iloc[0]

    # --- direction of winner ---
    orientation = winner["strategy"].rsplit("_", 1)[1]
    neg_thr = "neg_" in winner["threshold"]
    long_when_high = (orientation == "pro") != neg_thr
    direction = "procyclical" if long_when_high else "countercyclical"
    thr_value = float(thr.dropna().iloc[-1]) if isinstance(thr, pd.Series) else float(thr)
    # long-entry relation of the (lagged) signal to its threshold (schema: entry = signal satisfies relation)
    thr_rule = {(False, "pro"): "gt", (False, "counter"): "lte",
                (True, "pro"): "lt", (True, "counter"): "gte"}[(neg_thr, orientation)]
    strat_family = winner["strategy"].rsplit("_", 1)[0]

    # --- lead-lag verdict (empirical) ---
    fwd_sig_lags = list(ty_df[(ty_df.direction == "indicator_to_target") & ty_df.significant].lag)
    rev_sig_lags = list(ty_df[(ty_df.direction == "target_to_indicator") & ty_df.significant].lag)
    ccf_lead = list(ccf_df[(ccf_df.lag > 0) & ccf_df.significant].lag)
    ccf_lag = list(ccf_df[(ccf_df.lag < 0) & ccf_df.significant].lag)
    if fwd_sig_lags and not rev_sig_lags:
        leadlag = "leading"
    elif rev_sig_lags and not fwd_sig_lags:
        leadlag = "lagging"
    elif fwd_sig_lags and rev_sig_lags:
        leadlag = "bidirectional"
    else:
        leadlag = "coincident_or_none"

    # ================= ECON-T5 selection provenance (IS-selected) =================
    sel = CTX["selection"]
    audit = CTX["audit"]
    wi, oi, li = sel["wi"], sel["oi"], sel["li"]
    tdf_read = tdf.reset_index(drop=True)
    all_valid = tdf_read[(tdf_read.signal != "BENCHMARK") & tdf_read.valid].copy()
    winner_row_idx = int(wi)
    n_sig = int(tdf[tdf.signal != "BENCHMARK"]["signal"].nunique())
    distinct_rank = sel["ranked"].drop_duplicates(["signal", "strategy", "lead_quarters", "is_sharpe", "oos_sharpe"])
    runner = sel["ranked"].drop(index=wi).iloc[0] if len(sel["ranked"]) > 1 else None
    runner_d = distinct_rank.drop(index=wi, errors="ignore")
    runner_d = runner_d.iloc[0] if len(runner_d) else None

    def _ro(r):
        return None if r is None else {
            "signal": r["signal"], "threshold": r["threshold"], "strategy": r["strategy"],
            "lead_value": int(r["lead_quarters"]), "objective_value": round(float(r["is_sharpe"]), 6),
            "oos_sharpe": round(float(r["oos_sharpe"]), 6)}

    oos_r = strat_ret[(strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])]
    t_oos, p_oos, nw_oos = hac_t_mean(oos_r)
    ws_meta = CTX["winner_series"]
    is_r = ws_meta["strat_ret"][(ws_meta["work"].index >= sel["common_is_start"]) &
                                (ws_meta["work"].index < pd.Timestamp(split["oos_start"]))].dropna()
    t_is, p_is, nw_is = hac_t_mean(is_r)
    from scipy.stats import norm
    exp_max_z = float(norm.ppf(1 - 0.5 / max(sel["n_distinct"], 1)))
    is_window = {"start": str(winner["is_start"]), "end": str(winner["is_end"]), "n": int(winner["is_n"]),
                 "common_is_start": sel["common_is_start"].date().isoformat(), "oos_start": split["oos_start"],
                 "min_is_n": MIN_IS_N, "n_candidates": sel["n_cands"], "n_eligible": sel["n_eligible"],
                 "n_ineligible_short_history": sel["n_inel"], "common_start_set_by": sel["driver"],
                 "rule": (f"eligibility before alignment: a candidate is IS-eligible only if its own first valid return "
                          f"leaves >= {MIN_IS_N} IS quarters; common_is_start = latest first-valid-return date among "
                          "eligible candidates; IS metrics for every candidate computed on [common_is_start, oos_start)"),
                 "validity": (f"IS window only: is_n >= {MIN_IS_N}, IS exposure in [0.05, 0.95] (P3: share of quarters "
                              f"long), IS std > 0, IS turnover < {MAX_TURNOVER}/yr; OOS never consulted"),
                 "bh_is_sharpe": round(float(sel["bh_is"]["sharpe"]), 6)}
    prev = audit["previously_published"]
    rep_rows = {(r["probabilities"], r["lead_quarters"]): r for r in audit["rows"]}
    prev_l = int(prev["lead_quarters"])
    selection = {
        "objective": "max_is_sharpe",
        "objective_formula": ("in-sample (common window [common_is_start, OOS start)) quarterly mean/std*sqrt(4) of "
                              "position_t*spy_ret_t; winner evaluated on the OOS window with ECON-T4 deployable scoring (fillna 0)"),
        "is_window": is_window,
        "grid_scanned": {"leads": LEADS, "n_signals": n_sig, "n_thresholds": 8, "n_strategies": 4,
                         "n_combos": int(len(tdf) - 1), "n_valid_combos": int(len(all_valid)),
                         "n_distinct_position_series": int(sel["n_distinct"]),
                         "median_valid_objective": round(float(all_valid["is_sharpe"].median()), 6),
                         "spearman_is_vs_oos": round(sel["spearman"], 4)},
        "tie_break_step": int(resolved_at),
        "raw_winner_row": {"signal": winner["signal"], "threshold": winner["threshold"],
                           "strategy": winner["strategy"], "lead_column": "lead_quarters",
                           "lead_value": int(winner["lead_quarters"]),
                           "source_tournament_file": os.path.basename(tpath),
                           "source_row_index": winner_row_idx,
                           "display_alias": (f"signal_code={REGISTRY_CODE[winner['signal']]} (raw signal={winner['signal']}); "
                                             f"strategy_family={strat_family} (raw strategy={winner['strategy']})")},
        "runner_up": _ro(runner),
        "runner_up_distinct_series": _ro(runner_d),
        "rationale": ("Winner is the IS-valid row with the highest IN-SAMPLE Sharpe (common IS window) over the floored "
                      "quarterly grid L1..L5; OOS metrics are reported for that row only (no OOS look-ahead in selection). "
                      "Regime signals (HMM, Markov-switching) are not in the grid: a causal IS-only fit needs >= 100 IS rows "
                      "and ECI has 72 IS quarters."),
        "legacy_oos_selected_row": (None if li is None else {
            "signal": str(tdf.loc[li, "signal"]), "threshold": str(tdf.loc[li, "threshold"]),
            "strategy": str(tdf.loc[li, "strategy"]), "direction": str(tdf.loc[li, "direction"]),
            "lead_value": int(tdf.loc[li, "lead_quarters"]), "oos_sharpe": round(float(tdf.loc[li, "oos_sharpe"]), 6),
            "note": f"OOS-argmax on this grid (pre-GH#251 rule), comparison only; see legacy_oos_selection_{DATE_TAG}.csv"}),
        "sensitivity_own_is_start_row": {
            "signal": str(tdf.loc[oi, "signal"]), "threshold": str(tdf.loc[oi, "threshold"]),
            "strategy": str(tdf.loc[oi, "strategy"]), "direction": str(tdf.loc[oi, "direction"]),
            "lead_value": int(tdf.loc[oi, "lead_quarters"]), "own_is_start": str(tdf.loc[oi, "own_is_start"]),
            "own_is_sharpe": round(float(tdf.loc[oi, "own_is_sharpe"]), 6),
            "oos_sharpe": round(float(tdf.loc[oi, "oos_sharpe"]), 6),
            "note": "IS argmax without common-start alignment; sensitivity only"},
        "previously_published": {
            **{k: prev[k] for k in ("signal", "threshold", "strategy", "lead_quarters", "lookback", "oos_sharpe")},
            "combo": f"{prev['signal']}/{prev['threshold']}/{prev['lookback']}/{prev['strategy']}/L{prev_l}q",
            "hac_t": rep_rows[("smoothed_fullsample", prev_l)]["hac_t"],
            "causal_same_rule_oos_sharpe": rep_rows[("causal_filtered_diag", prev_l)]["oos_sharpe"],
            "causal_same_rule_hac_t": rep_rows[("causal_filtered_diag", prev_l)]["hac_t"],
            "source": prev.get("source", f"winner_summary.json ({PREV_TAG})"),
            "status": ("superseded: relied on full-sample, forward-backward smoothed HMM probabilities (look-ahead) and "
                       "was selected by OOS Sharpe"),
            "audit_file": f"hmm_lookahead_audit_{DATE_TAG}.json"},
        "inference": {"oos_hac_t": round(t_oos, 3), "oos_hac_p": round(p_oos, 4), "oos_hac_maxlags": nw_oos,
                      "is_hac_t": round(t_is, 3), "is_hac_maxlags": nw_is,
                      "n_distinct_candidates": int(sel["n_distinct"]),
                      "expected_max_abs_z_under_null": round(exp_max_z, 2),
                      "note": "expected max |z| = Phi^-1(1 - 0.5/N) over N distinct position series (two-sided, independence approximation)"},
        "objective_runner_up_divergence": None,
    }
    assert tdf.loc[wi, "valid"] and abs(float(winner["is_sharpe"]) - float(all_valid["is_sharpe"].max())) <= 1e-9, \
        "winner must be the IS-valid population max"

    winner_summary = {
        "pair_id": PAIR_ID, "generated_at": NOW_ISO,
        "signal_column": SIGNAL_COLS[winner["signal"]],
        "signal_code": REGISTRY_CODE[winner["signal"]],
        "signal_display_name": SIGNAL_DISPLAY[winner["signal"]],
        "target_symbol": TARGET_SYMBOL, "threshold_code": winner["threshold"],
        "threshold_value": round(thr_value, 4), "threshold_rule": thr_rule,
        "threshold_note": (f"Moving boundary: rolling {LOOKBACKS.get(winner['lookback'], '')}-quarter mean "
                           f"{'-' if neg_thr else '+'} 1.0 std of the lead-shifted signal; threshold_value is its latest value"
                           if isinstance(thr, pd.Series) else
                           "static threshold: percentile of the lead-shifted signal over the IS quarters"),
        "strategy_family": strat_family, "strategy_code": strat_family.split("_")[0],
        "strategy_display_name": {"P1_long_cash": "Long/Cash", "P3_long_short": "Long/Short"}[strat_family],
        "strategy_description": "",
        "lead_value": int(winner["lead_quarters"]), "lead_unit": "quarters",
        "lead_description": (f"Signal lead = {int(winner['lead_quarters'])} quarter(s) (~{int(winner['lead_quarters'])*3} months); "
                             f"L1 is the registry floor (BLS releases quarter Q's ECI ~1 month after quarter end)"),
        "lookback": winner["lookback"], "direction": direction,
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4), "oos_sortino": round(float(winner["oos_sortino"]), 4),
        "oos_calmar": round(float(winner["oos_calmar"]), 4), "oos_ann_return": round(float(winner["oos_ann_return"]), 4),
        "oos_ann_vol": round(float(winner["oos_ann_vol"]), 4), "oos_max_drawdown": round(float(winner["max_drawdown"]), 4),
        "oos_win_rate": round(float(winner["win_rate"]), 4), "oos_n_trades": int(winner["n_trades"]),
        "annual_turnover": round(float(winner["annual_turnover"]), 2), "oos_n": int(winner["oos_n"]),
        "oos_period_start": split["oos_start"], "oos_period_end": split["oos_end"],
        "oos_hac_t": round(t_oos, 3),
        "is_sharpe": round(float(winner["is_sharpe"]), 6), "is_n": int(winner["is_n"]),
        "is_period_start": is_window["start"], "is_period_end": is_window["end"],
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4), "bh_ann_return": round(float(bh["oos_ann_return"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4), "bh_is_sharpe": round(float(sel["bh_is"]["sharpe"]), 4),
        "cost_assumption_bps": COST_BPS,
        "total_combos": int(len(tdf) - 1), "valid_combos": n_valid, "schema_version": "1.2.0",
        "selection": selection,
        "notes": (f"Quarterly pair (annualization sqrt(4); leads/lookbacks/oos_n in quarters). {DATE_TAG} rerun: "
                  f"tournament of {len(tdf)-1} strategy combos (+1 benchmark), {n_valid} IS-valid. Winner selected by "
                  f"in-sample Sharpe on the common IS window {is_window['start']}..{is_window['end']} "
                  f"({is_window['n']} quarters) and evaluated on the held-out OOS window "
                  f"{split['oos_start']}..{split['oos_end']} ({int(winner['oos_n'])} quarters): IS Sharpe "
                  f"{float(winner['is_sharpe']):.2f} (B&H {sel['bh_is']['sharpe']:.2f}), OOS Sharpe "
                  f"{float(winner['oos_sharpe']):.2f} (B&H {float(bh['oos_sharpe']):.2f}), OOS HAC t {t_oos:.2f}. "
                  f"The HMM and Markov-switching regime signals are not in the grid: a causal (IS-only, forward-filtered) "
                  f"fit needs at least 100 IS rows and ECI has 72 IS quarters. The previously published winner "
                  f"({selection['previously_published']['combo']}, OOS Sharpe {float(prev['oos_sharpe']):.2f}) used full-sample "
                  f"smoothed HMM probabilities; the same rule on a causal diagnostic HMM scores "
                  f"{selection['previously_published']['causal_same_rule_oos_sharpe']:.2f} (hmm_lookahead_audit_{DATE_TAG}.json). "
                  f"Lead-lag (empirical): ECI->SPY TY-Granger sig lags(q) {fwd_sig_lags or 'NONE'}, SPY->ECI {rev_sig_lags or 'NONE'} "
                  f"-> '{leadlag}'. Gross of costs; sensitivity in tournament_validation_{DATE_TAG}/."),
    }
    sd = ("Long SPY when the {}-quarter-lagged {} is {} its threshold; otherwise {}."
          .format(int(winner["lead_quarters"]), SIGNAL_DISPLAY[winner["signal"]],
                  {"gt": "above", "gte": "at or above", "lt": "below", "lte": "at or below"}[thr_rule],
                  "cash" if strat_family == "P1_long_cash" else "short SPY"))
    if not long_when_high:
        sd += " (Countercyclical orientation: low/decelerating wage inflation = risk-on.)"
    else:
        sd += " (Procyclical orientation: high/accelerating wage inflation = risk-on.)"
    sd += " Rebalanced quarterly."
    winner_summary["strategy_description"] = sd

    wpath = os.path.join(RESULTS_DIR, "winner_summary.json")
    with open(wpath, "w") as f:
        json.dump(winner_summary, f, indent=2)
    print(f"\n  winner_summary -> {wpath}")

    import subprocess
    rc = subprocess.run(["python3", os.path.join(BASE_DIR, "scripts", "validate_schema.py"),
                         "--schema", os.path.join(SCHEMA_DIR, "winner_summary.schema.json"),
                         "--instance", wpath]).returncode
    if rc != 0:
        raise SystemExit("winner_summary.json failed schema validation — fix the producer (ECON-H5)")
    print("  winner_summary schema validation: PASS")

    with open(os.path.join(SCHEMA_DIR, "signal_code_registry.json")) as f:
        registry_codes = {e["signal_code"] for e in json.load(f)["signals"]}
    assert winner_summary["signal_code"] in registry_codes, (
        f"signal_code '{winner_summary['signal_code']}' not in signal_code_registry.json (ECON-DS3)")
    print("  signal_code registry assertion: PASS")

    # interpretation_metadata: update EVAN-OWNED fields (+ indicator_nature if the
    # empirical verdict contradicts Dana's provisional 'lagging' prior)
    interp_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    with open(interp_path) as f:
        interp = json.load(f)
    nature_map = {"leading": "leading", "lagging": "lagging",
                  "bidirectional": "mixed", "coincident_or_none": "coincident"}
    empirical_nature = nature_map[leadlag]
    prior_nature = interp.get("indicator_nature")
    if empirical_nature != prior_nature:
        interp["indicator_nature"] = empirical_nature
        interp["indicator_nature_note"] = (f"Set by Evan from empirical evidence (was Dana provisional "
                                           f"'{prior_nature}'): Granger/CCF verdict '{leadlag}'.")
    interp["observed_direction"] = direction
    interp["direction_consistent"] = interp.get("expected_direction") in ("mixed", direction)
    interp["key_finding"] = (
        f"Lead-lag verdict (empirical, QUARTERLY): ECI total compensation is '{leadlag}' vs SPY. Toda-Yamamoto "
        f"Granger ECI->SPY significant lags(q) {fwd_sig_lags or 'NONE'}; SPY->ECI significant lags(q) "
        f"{rev_sig_lags or 'NONE'}; pre-whitened CCF significant lead(+) lags {ccf_lead or 'NONE'}, lag(-) "
        f"{ccf_lag or 'NONE'}. Tournament winner ({winner['signal']}/{winner['threshold']}/{strat_family} "
        f"{orientation}/L{winner['lead_quarters']}q/{winner['lookback']}, selected by IS Sharpe) is {direction}: "
        f"IS Sharpe {float(winner['is_sharpe']):.2f} vs B&H {sel['bh_is']['sharpe']:.2f}; OOS Sharpe "
        f"{winner_summary['oos_sharpe']:.2f} vs B&H {winner_summary['bh_sharpe']:.2f} (sqrt(4) annualization), "
        f"OOS HAC t {t_oos:.2f} on {int(winner['oos_n'])} quarters. HMM/Markov-switching regime signals are not "
        f"traded (causal fit needs >= 100 IS rows; 72 available).")
    interp["confidence"] = "low"
    interp["last_updated_by"] = "evan"; interp["last_updated_at"] = NOW_ISO
    with open(interp_path, "w") as f:
        json.dump(interp, f, indent=2)
    assert interp["observed_direction"] in {"procyclical", "countercyclical", "mixed"}
    assert interp["observed_direction"] == winner_summary["direction"], "ECON-DIR1 consistency check failed"
    print(f"  interpretation_metadata evan-fields updated (indicator_nature: {interp['indicator_nature']}); ECON-DIR1: PASS")

    # tournament_winner.json (META-TWJ)
    tw = {"pair_id": PAIR_ID,
          "winner_label": f"{winner['signal']} / {winner['threshold']} / {strat_family} ({orientation}) / L{winner['lead_quarters']}q / {winner['lookback']}",
          "winner_oos_sharpe": round(float(winner["oos_sharpe"]), 4), "winner_max_drawdown": round(float(winner["max_drawdown"]), 4),
          "winner_oos_ann_return": round(float(winner["oos_ann_return"]), 4), "bh_oos_sharpe": round(float(bh["oos_sharpe"]), 4),
          "bh_max_drawdown": round(float(bh["max_drawdown"]), 4), "bh_oos_ann_return": round(float(bh["oos_ann_return"]), 4),
          "delta_sharpe": round(float(winner["oos_sharpe"] - bh["oos_sharpe"]), 4),
          "delta_max_drawdown": round(float(winner["max_drawdown"] - bh["max_drawdown"]), 4),
          "delta_ann_return": round(float(winner["oos_ann_return"] - bh["oos_ann_return"]), 4),
          "beats_benchmark": bool(winner["oos_sharpe"] > bh["oos_sharpe"]), "suggested_strategy_objective": None,
          "generated_at": NOW_ISO}
    rel_sharpe = tw["delta_sharpe"] / max(abs(tw["bh_oos_sharpe"]), 0.1)
    rel_dd = tw["delta_max_drawdown"] / max(abs(tw["bh_max_drawdown"]), 0.01)
    tw["suggested_strategy_objective"] = "min_mdd" if rel_dd > rel_sharpe else "max_sharpe"
    with open(os.path.join(RESULTS_DIR, "tournament_winner.json"), "w") as f:
        json.dump(tw, f, indent=2)

    # signal_scope.json (ECON-UD)
    ind_der = [{"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []} for c, d, s, r in [
        ("eci_total_comp_idx", "Employment Cost Index: Total Compensation, All Civilian, SA quarterly index (Dec 2005=100)", "FRED ECIALLCIV", "raw"),
        ("eci_total_comp_pct_qoq", "quarter-on-quarter % change (short-horizon wage momentum)", "100*(L_t/L_{t-1}-1)", "derivative"),
        ("eci_total_comp_pct_2q", "2-quarter (~6M) % change", "100*(L_t/L_{t-2}-1)", "derivative"),
        ("eci_total_comp_pct_yoy", "4-quarter % change (headline wage inflation; near-I(1) persistent)", "100*(L_t/L_{t-4}-1)", "derivative"),
        ("eci_total_comp_ma8q_idx", "8-quarter (~2yr) moving average of the level", "rolling mean(8)", "derivative"),
        ("eci_total_comp_dev_trend_pct", "% deviation of the level from its 8Q MA", "100*(L_t/MA8Q-1)", "derivative"),
        ("eci_total_comp_zscore_20q", "rolling 20Q (~5yr) z-score of the LEVEL (regime-contaminated; KPSS reject)", "(L_t-mean20q)/sd20q", "derivative"),
        ("eci_total_comp_yoy_zscore_20q", "rolling 20Q z-score of YoY growth (regime-contaminated; KPSS reject)", "(yoy_t-mean20q)/sd20q", "derivative"),
        ("eci_total_comp_accel_pct", "QoQ acceleration (pp; cleanly stationary)", "qoq_t - qoq_{t-1}", "derivative"),
        ("eci_total_comp_yoy_accel_pct", "YoY acceleration (pp; cleanly stationary)", "yoy_t - yoy_{t-1}", "derivative"),
        ("hmm_2state_prob_stress", "DIAGNOSTIC, not traded: forward-filtered P(high wage-inflation state) from a 2-state HMM on YoY growth fit on IS quarters only (72 < 100-row minimum for a traded signal)", "GaussianHMM(yoy), IS-only fit, forward filter (scripts/_regime_causal.py)", "regime_state")]]
    tgt_der = [{"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []} for c, d, s, r in [
        ("spy", "SPY adjusted quarter-end close", "Yahoo Finance", "raw"),
        ("spy_ret", "SPY quarterly return (decimal)", "P_t/P_{t-1}-1", "derivative"),
        ("spy_fwd_1q", "1-quarter forward SPY return", "P_{t+1}/P_t-1", "derivative"),
        ("spy_fwd_2q", "2-quarter forward SPY return", "P_{t+2}/P_t-1", "derivative"),
        ("spy_fwd_4q", "4-quarter forward SPY return", "P_{t+4}/P_t-1", "derivative")]]
    scope = {"pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
             "last_updated_at": NOW_ISO,
             "indicator_axis": {"canonical_column": "eci_total_comp_idx", "display_name": "Employment Cost Index (Total Compensation)", "derivatives": ind_der},
             "target_axis": {"canonical_column": "spy", "display_name": "SPY (S&P 500 ETF)", "derivatives": tgt_der},
             "notes": ("ECON-SD: only ECI derivatives and SPY derivatives are in scope. Controls in the parquet "
                       "(unrate, dgs10, fed_funds, vix) are context columns, NOT signals. FIRST QUARTERLY pair: "
                       "windows named in quarters (20Q/8Q), leads in quarters, sqrt(4) annualization. SA source — "
                       "no seasonal-contamination constraint. regime_story: false (CP2 skipped).")}
    with open(os.path.join(RESULTS_DIR, "signal_scope.json"), "w") as f:
        json.dump(scope, f, indent=2)

    # kpis.json
    kpis = [
        {"metric": "OOS Sharpe (winner)", "value": f"{winner_summary['oos_sharpe']:.2f}", "unit": "ratio", "delta": f"{tw['delta_sharpe']:+.2f} vs B&H"},
        {"metric": "IS Sharpe (winner, selection objective)", "value": f"{float(winner['is_sharpe']):.2f}", "unit": "ratio", "delta": f"{float(winner['is_sharpe']) - sel['bh_is']['sharpe']:+.2f} vs B&H"},
        {"metric": "OOS Sharpe (buy & hold)", "value": f"{winner_summary['bh_sharpe']:.2f}", "unit": "ratio", "delta": None},
        {"metric": "OOS Annual Return (winner)", "value": f"{winner_summary['oos_ann_return']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_ann_return']*100:+.1f}pp vs B&H"},
        {"metric": "OOS Max Drawdown (winner)", "value": f"{winner_summary['oos_max_drawdown']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_max_drawdown']*100:+.1f}pp vs B&H"},
        {"metric": "IS-valid strategy combos", "value": f"{n_valid}", "unit": "count", "delta": None},
        {"metric": "OOS window", "value": f"{split['oos_start']} → {split['oos_end']} ({int(winner['oos_n'])} quarters)", "unit": "dates", "delta": None},
    ]
    with open(os.path.join(RESULTS_DIR, "kpis.json"), "w") as f:
        json.dump(kpis, f, indent=2)

    # lead_sweep_manifest (ECON-LT1 record)
    with open(DATA_PATH, "rb") as f:
        input_sha = "sha256:" + hashlib.sha256(f.read()).hexdigest()[:16]
    lead_manifest = {
        "pair": PAIR_ID, "run_date": DATE_TAG, "frozen": False,
        "granularity": "QUARTERS L1..5 tradable (L0..8 diagnostic in lead_correlation; quarterly adaptation of ECON-LL1)",
        "freq_native": "Q",
        "design_note": ("Quarterly pair; lead L = quarter shift on quarter-end signals. Registry floor L1, grid "
                        "L1..L5 (#255). Winner selected by IS Sharpe; lead summaries are context."),
        "oos_start": split["oos_start"], "is_end": split["in_sample_end"], "input_file": os.path.relpath(DATA_PATH, BASE_DIR),
        "input_sha256": input_sha, "lead_correlation_file": f"{PAIR_ID}/lead_correlation_{DATE_TAG}.csv",
        "lead_tournament_file": f"{PAIR_ID}/lead_tournament_{DATE_TAG}.csv",
        "lead_winner_curve_file": f"{PAIR_ID}/lead_winner_curve_{DATE_TAG}.csv",
        "lead_clean_envelope_file": f"{PAIR_ID}/lead_clean_envelope_{DATE_TAG}.csv",
        "clean_envelope_note": "SA source: all signals admissible -> envelope and clean envelope COINCIDE by construction",
        "published_winner": {"signal": SIGNAL_COLS[winner["signal"]], "lead": int(winner["lead_quarters"]),
                             "lead_unit": "quarters", "oos_sharpe": round(float(winner["oos_sharpe"]), 4),
                             "is_sharpe": round(float(winner["is_sharpe"]), 4), "selection": "max_is_sharpe"},
        "winner_curve_peak_lead": peak_lead,
        "L_star": L_star, "best_oos_sharpe_at_grid": round(float(best_at_grid), 4) if pd.notna(best_at_grid) else None,
        "gate_decision": gate,
        "assertions": ["tradable lead grid is L1..5 QUARTERS (registry floor L1)",
                       "main tournament scans the full L1..5 grid; winner = IS-Sharpe argmax",
                       f"ECON-LT1: OOS-best lead L*={L_star} (context only) -> {gate}"],
        "small_sample_caveat": f"OOS = {int(winner['oos_n'])} quarters -> winner is found-in-search; lead-sweep peaks are high-variance."}
    with open(os.path.join(RESULTS_DIR, f"lead_sweep_manifest_{DATE_TAG}.json"), "w") as f:
        json.dump(lead_manifest, f, indent=2)

    # design_note.md — APPEND Phase-1 sections to Dana's Phase-0 note (preserve her content)
    with open(os.path.join(RESULTS_DIR, "design_note.md")) as f:
        dana_note = f.read().rstrip()
    pp = selection["previously_published"]
    phase1 = f"""

---

# Phase 1 addendum — causal regime port + IS selection (Evan, {DATE_TAG})

## What changed
- **Look-ahead removed.** The {PREV_TAG} winner ({pp['combo']}, OOS Sharpe {float(pp['oos_sharpe']):.4f}) traded a
  2-state HMM probability fit on the FULL sample and read with forward-backward SMOOTHING (`predict_proba`), so each
  quarter's value used later quarters. The Markov-switching signal also put `spy_ret` in its likelihood.
- **Causal rule (scripts/_regime_causal.py):** fit on IS rows only, IS-only standardisation, forward-filtered
  probabilities, no target return in the likelihood. A traded fit needs >= 100 IS rows; ECI has 72 IS quarters, so
  `hmm_stress` and `markov_regime` are **excluded from the tournament** (core_models_{DATE_TAG}/regime_models.json).
- A diagnostic causal HMM (IS-only, 72 quarters, override `min_is_rows=40`, NOT traded) is kept for the Evidence
  chart and the audit. The superseded rule on it scores OOS Sharpe {pp['causal_same_rule_oos_sharpe']:.4f}
  (HAC t {pp['causal_same_rule_hac_t']:.2f}) vs {float(pp['oos_sharpe']):.4f} (HAC t {pp['hac_t']:.2f}) on the smoothed column
  (hmm_lookahead_audit_{DATE_TAG}.json).
- **Selection:** argmax IS Sharpe on the common IS window {is_window['start']}..{is_window['end']} ({is_window['n']}
  quarters; start set by {', '.join(sel['driver'])}); eligibility before alignment, MIN_IS_N={MIN_IS_N}; validity uses IS
  rows only (exposure 0.05-0.95, turnover < {MAX_TURNOVER}/yr). The old validity rule (OOS Sharpe > 0.3) is kept only as
  `oos_valid` for the legacy comparison.
- Warm-up rows (lagged signal or rolling threshold undefined) are now NaN instead of cash/short.

## Result
- Winner: {winner['signal']} / {winner['threshold']} / {winner['lookback']} / {winner['strategy']} / L{int(winner['lead_quarters'])}q.
- IS Sharpe {float(winner['is_sharpe']):.4f} (B&H {sel['bh_is']['sharpe']:.4f}); OOS Sharpe {float(winner['oos_sharpe']):.4f}
  (B&H {float(bh['oos_sharpe']):.4f}), OOS HAC t {t_oos:.2f} (p {p_oos:.3f}), {int(winner['oos_n'])} OOS quarters.
- Grid {len(tdf)-1} combos, {n_valid} IS-valid, {sel['n_distinct']} distinct position series; Spearman(IS, OOS) {sel['spearman']:.3f}.
- Lead-lag (empirical): ECI->SPY TY-Granger sig lags {fwd_sig_lags or 'NONE'}; SPY->ECI {rev_sig_lags or 'NONE'} -> {leadlag}.
"""
    with open(os.path.join(RESULTS_DIR, "design_note.md"), "w") as f:
        f.write(dana_note + phase1)

    # analyst_suggestions.json
    sugg = {"schema_version": "1.0.0", "pair_id": PAIR_ID, "rule": "ECON-AS",
            "suggestions": [
                {"signal_name": "ECI Wages & Salaries vs Benefits split (ECIWAG / ECIBEN)", "proposed_by": "evan",
                 "source": "FRED", "observation": "Total compensation blends wages and benefits; the wage component is the cleaner wage-price-spiral read and the benefits component is contract-lagged.",
                 "rationale": "The wages-only series may carry the Fed-relevant signal with less smoothing.",
                 "possible_use_case": "variant family / companion signal", "caveats": "Same quarterly small-sample limits.",
                 "date_filed": "2026-07-06"},
                {"signal_name": "Atlanta Fed Wage Growth Tracker", "proposed_by": "evan", "source": "Atlanta Fed",
                 "observation": "MONTHLY wage-growth measure (median, matched-person) — 3x the observation density of ECI with a similar economic object.",
                 "rationale": "If quarterly granularity is the binding constraint here, the monthly tracker offers the same hypothesis with ~300 obs.",
                 "possible_use_case": "new pair", "caveats": "Shorter history (1997+), survey-based, noisier.", "date_filed": "2026-07-06"},
                {"signal_name": "ECI YoY minus CPI YoY (real wage growth)", "proposed_by": "evan", "source": "FRED (ECIALLCIV, CPIAUCSL)",
                 "observation": "Real (inflation-adjusted) compensation growth separates wage-price-spiral pressure from pure price inflation.",
                 "rationale": "The Fed reaction function arguably keys on real wage growth vs productivity.",
                 "possible_use_case": "companion signal", "caveats": "Two-series composite — out of current single-indicator scope.", "date_filed": "2026-07-06"}],
            "last_updated_by": "evan", "last_updated_at": NOW_ISO}
    with open(os.path.join(RESULTS_DIR, "analyst_suggestions.json"), "w") as f:
        json.dump(sugg, f, indent=2)

    # evidence_status.json (docs/schemas/evidence_status.schema.json)
    ev = {"pair_id": PAIR_ID, "schema_version": "1.0.0", "status": "found_in_search", "updated_at": NOW_ISO,
          "technical_note": (f"Winner selected by in-sample Sharpe (common pre-OOS window {is_window['start']}.."
                             f"{is_window['end']}) from the {DATE_TAG} quarterly tournament ({n_valid} IS-valid combos) and "
                             f"evaluated on the held-out OOS window {split['oos_start']}..{split['oos_end']} "
                             f"({int(winner['oos_n'])} quarters): OOS Sharpe {float(winner['oos_sharpe']):.2f} vs B&H "
                             f"{float(bh['oos_sharpe']):.2f}, HAC t {t_oos:.2f}. No frozen-rule confirmation test has been run."),
          "next_step": "Freeze the rule and evaluate it on quarters released after the freeze date.",
          "owner": "evan"}
    with open(os.path.join(RESULTS_DIR, "evidence_status.json"), "w") as f:
        json.dump(ev, f, indent=2)

    # timing
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump({"pair_id": PAIR_ID, "date": DATE_TAG, "pipeline_seconds": round(time.time() - t0, 1),
                   "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
                   "tournament_strategy_rows": int(len(tdf) - 1), "valid_strategies": n_valid,
                   "oos_n_quarters": int(winner["oos_n"]), "oos_start": split["oos_start"], "oos_end": split["oos_end"]}, f, indent=2)

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE — HANDOFF NUMBERS (DPS-SCD1)")
    print("=" * 70)
    print(f"  Strategy combos: {len(tdf)-1} | IS-valid: {n_valid} | median IS Sharpe (valid): {median_sharpe:.3f}")
    print(f"  Winner: {tw['winner_label']} | stationarity_class={winner['stationarity_class']}")
    print(f"  OOS Sharpe {winner_summary['oos_sharpe']} vs B&H {winner_summary['bh_sharpe']} | "
          f"DD {winner_summary['oos_max_drawdown']} vs {winner_summary['bh_max_drawdown']} | "
          f"ret {winner_summary['oos_ann_return']} vs {winner_summary['bh_ann_return']}")
    print(f"  Ties at step 1: {n_tied} (cascade resolved at step {resolved_at})")
    print(f"  Durability: {verdict} | corr sign-stability: {stab} | break flagged: {sb['flagged']} ({sb['break_date']})")
    print(f"  Direction (winner): {direction} | lead-lag class: {leadlag} | ECON-LT1: L*={L_star} ({gate})")
    print(f"  Winner lead-curve peak: L{peak_lead}q (published L{int(winner['lead_quarters'])}q)")
    print(f"  Granger fwd-sig lags(q): {fwd_sig_lags or 'NONE'} | rev-sig lags(q): {rev_sig_lags or 'NONE'} | "
          f"CCF lead lags: {ccf_lead or 'NONE'}")
    print(f"  Winner bootstrap p={winner_boot_p} | {int(winner['oos_n'])}-QUARTER OOS CANDIDATE (found-in-search)")
    return winner_summary, tw


if __name__ == "__main__":
    main()
