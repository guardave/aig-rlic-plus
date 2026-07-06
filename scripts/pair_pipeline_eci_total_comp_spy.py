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
DATE_TAG = "20260706"
COST_BPS = 5  # equity ETF per target-class table
ANN = np.sqrt(4)   # QUARTERLY annualization factor (Sharpe); mean x4, vol x sqrt(4)
PERIODS_PER_YEAR = 4

BASE_DIR = "/workspaces/aig-rlic-plus"
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
LEADS = list(range(1, 9))      # L1..L8 QUARTERS — L1 pub-lag floor, L8 = 2yr ceiling
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
@log_stage("2_signals")
def stage_signals(df):
    import statsmodels.api as sm
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

    yoy = df["eci_total_comp_pct_yoy"].dropna()  # 97 obs

    # --- HMM 2-state on YoY wage growth (97 obs — attempted, honesty-flagged) ---
    # Caveat stated up front: with wage YoY this persistent, the HMM will likely split
    # high- vs low-wage-inflation REGIMES (level split), not volatility states. That is
    # still an economically meaningful regime signal (post-COVID surge vs pre-COVID calm),
    # but on 97 obs the transition-matrix estimate is weak — flagged in the manifest.
    hmm_ok = False
    try:
        from hmmlearn.hmm import GaussianHMM
        X = yoy.values.reshape(-1, 1)
        hmm = GaussianHMM(n_components=2, covariance_type="full", n_iter=500, random_state=42)
        hmm.fit(X)
        means = [float(hmm.means_[i].ravel()[0]) for i in range(2)]
        # "stress" = HIGH wage-inflation regime (wage-price-spiral / Fed-tightening pressure)
        stress_state = int(np.argmax(means))
        probs = hmm.predict_proba(X)
        prob_stress = pd.Series(probs[:, stress_state], index=yoy.index, name="hmm_2state_prob_stress")
        df["hmm_2state_prob_stress"] = prob_stress
        states = pd.Series(hmm.predict(X), index=yoy.index)
        # Degeneracy guard: both regimes must be occupied >= 10% of the sample
        occ = states.value_counts(normalize=True)
        if occ.min() < 0.10:
            print(f"  HMM degenerate (min regime occupancy {occ.min():.2f}) — hmm_stress EXCLUDED")
            df.drop(columns=["hmm_2state_prob_stress"], inplace=True)
        else:
            hmm_ok = True
            hmm_states = pd.DataFrame({"hmm_state": states, "prob_stress": prob_stress,
                                       "prob_calm": 1 - prob_stress})
            hmm_states.to_parquet(os.path.join(MODELS_DIR, "hmm_states.parquet"))
            spy = df["spy_ret"]
            summ = []
            for lbl, mask in [("high_wage_inflation", states == stress_state),
                              ("low_wage_inflation", states != stress_state)]:
                idx = hmm_states.index[mask]
                rets = spy.reindex(idx).dropna()
                summ.append({"state_label": lbl,
                             "mean_return": round(rets.mean(), 6) if len(rets) else np.nan,
                             "vol": round(rets.std(), 6) if len(rets) else np.nan,
                             "duration_days": int(mask.sum()) * 63,  # quarters -> ~trading days
                             "frequency_pct": round(mask.mean() * 100, 2),
                             "mean_yoy_growth": round(yoy.reindex(idx).mean(), 3)})
            pd.DataFrame(summ).to_csv(os.path.join(MODELS_DIR, "hmm_summary.csv"), index=False)
            surge_p = prob_stress.loc["2021-12-31":"2023-06-30"].mean()
            write_manifest(os.path.join(MODELS_DIR, "hmm_states.parquet"),
                           {"hmm_state": "integer state; stress = HIGH-MEAN wage-inflation regime (level split, not vol split)",
                            "prob_stress": "P(high wage-inflation regime); higher = wage-price-spiral / Fed-pressure regime",
                            "prob_calm": "1 - prob_stress"},
                           [{"description": "probabilities in [0,1]", "check": "prob_stress between 0 and 1"},
                            {"description": "2021-23 wage surge = high regime", "filter": "2021-12..2023-06",
                             "column": "prob_stress", "check": f"mean = {surge_p:.2f} (expect > 0.8)"},
                            {"description": "states sum to 1", "check": "prob_stress + prob_calm == 1"}],
                           extra={"small_sample_caveat": "97 quarterly obs; persistent series -> HMM splits wage-inflation LEVEL regimes; transition matrix weakly identified"})
            print(f"  HMM 2-state converged (level-regime split); stress prob mean 2021Q4-2023Q2: {surge_p:.2f}")
    except Exception as e:
        print(f"  HMM failed on quarterly sample ({e}) — hmm_stress excluded from tournament")

    # --- Markov-switching regression: spy_ret ~ yoy, 2 regimes ---
    ms_data = pd.concat([df["spy_ret"], yoy], axis=1).dropna()
    try:
        ms = MarkovRegression(ms_data["spy_ret"], k_regimes=2,
                              exog=sm.add_constant(ms_data["eci_total_comp_pct_yoy"]),
                              switching_variance=True)
        ms_fit = ms.fit(maxiter=500, disp=False)
        smp = ms_fit.smoothed_marginal_probabilities
        sig2 = [ms_fit.params[f"sigma2[{i}]"] for i in range(2)]
        ms_stress = int(np.argmax(sig2))
        df["markov_regime_2state"] = smp[ms_stress].reindex(df.index)
        pd.DataFrame({"regime_stress_prob": smp[ms_stress], "regime_calm_prob": smp[1 - ms_stress]}
                     ).to_csv(os.path.join(MODELS_DIR, "markov_regime_probs_2state.csv"))
        pd.DataFrame({"parameter": ms_fit.params.index, "value": ms_fit.params.values,
                      "se": ms_fit.bse.values}).to_csv(
            os.path.join(MODELS_DIR, "markov_switching_2state.csv"), index=False)
        print("  Markov-switching 2-state converged")
    except Exception as e:
        print(f"  Markov-switching failed: {e} — signal excluded from tournament")

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
                     "column": "eci_total_comp_pct_yoy", "check": "min > 0"}])
    return df, hmm_ok


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
def run_lead_grid(df, split, leads):
    """Tournament evaluation over given leads (in QUARTERS). Sparse grid per Dana's
    101-obs constraint: thresholds = IS percentiles {25,50,75} + zero-cross (sign-
    meaningful signals) + rolling z-score +/-1.0 at LB12/LB20; strategies = P1 long/cash
    and P3 long/short, each pro/counter. Returns strategy rows (NO benchmark)."""
    work = df.dropna(subset=["spy_ret"]).copy()
    is_end = split["in_sample_end"]; oos_start = split["oos_start"]; oos_end = split["oos_end"]
    is_mask = work.index <= is_end
    oos_mask = (work.index >= oos_start) & (work.index <= oos_end)
    spy_ret = work["spy_ret"]
    strategies = ["P1_long_cash", "P3_long_short"]
    results = []
    for code, col in SIGNAL_COLS.items():
        if col not in work.columns or work[col].notna().sum() < SIG_ELIGIBLE_MIN:
            continue
        base_sig = work[col]
        for lead in leads:
            sig = base_sig.shift(lead)
            thr_static = {}
            is_sig = sig[is_mask].dropna()
            if len(is_sig) > 30:
                for pct in [25, 50, 75]:
                    thr_static[(f"T1_fixed_p{pct}", "LB_NA")] = is_sig.quantile(pct / 100)
            if code in ZERO_CROSS:
                thr_static[("T4_zero", "LB_NA")] = 0.0
            thr_roll = {}
            for lb_name, lb in LOOKBACKS.items():
                minp = max(int(lb * 0.6), 8)
                roll = sig.rolling(lb, min_periods=minp)
                rm, rs = roll.mean(), roll.std()
                thr_roll[("T3_zscore_1.0", lb_name)] = rm + 1.0 * rs
                thr_roll[("T3_zscore_neg_1.0", lb_name)] = rm - 1.0 * rs
            for (thr_name, lb_name), thr in {**thr_static, **thr_roll}.items():
                above = sig < thr if "neg_" in thr_name else sig > thr
                for strat in strategies:
                    for orientation in ["pro", "counter"]:
                        pos_bool = ~above if orientation == "counter" else above
                        if strat == "P1_long_cash":
                            position = pos_bool.astype(float)
                        else:
                            position = pos_bool.astype(float) * 2 - 1
                        strat_ret = position * spy_ret
                        is_r, oos_r = strat_ret[is_mask].dropna(), strat_ret[oos_mask].dropna()
                        if len(is_r) < 40 or len(oos_r) < 20:
                            continue
                        m_is, m = ann_metrics(is_r), ann_metrics(oos_r)
                        pos_oos = position[oos_mask]
                        n_trades = int((pos_oos.diff().abs() > 1e-9).sum())
                        years = len(pos_oos.dropna()) / PERIODS_PER_YEAR
                        turnover = n_trades / years if years > 0 else 999
                        # quarterly rebalance ceiling: < 6 position changes / year
                        valid = bool(m["sharpe"] > 0.3 and turnover < 6 and len(oos_r) >= 20)
                        results.append({
                            "signal": code, "threshold": thr_name, "strategy": f"{strat}_{orientation}",
                            "lead_quarters": lead, "lookback": lb_name,
                            "is_sharpe": round(m_is["sharpe"], 4), "oos_sharpe": round(m["sharpe"], 4),
                            "oos_sortino": round(m["sortino"], 4), "oos_calmar": round(m["calmar"], 4),
                            "oos_ann_return": round(m["ann_return"], 4), "oos_ann_vol": round(m["ann_vol"], 4),
                            "max_drawdown": round(m["max_dd"], 4), "win_rate": round(m["win_rate"], 4),
                            "n_trades": n_trades, "annual_turnover": round(turnover, 2),
                            "oos_n": len(oos_r), "valid": valid,
                            "stationarity_class": ("clean" if code in STATIONARY_CLEAN else
                                                   "regime_contaminated" if code in REGIME_CONTAMINATED else
                                                   "borderline_persistent")})
    return pd.DataFrame(results)


@log_stage("6_tournament")
def stage_tournament(df):
    work = df.dropna(subset=["spy_ret"]).copy()
    n_q = len(work)
    n_months = n_q * 3
    # ECON-OOS2 policy v1_max36_25pct_cap120 translated to native quarterly units:
    # span_months = min(max(36, round(303*0.25)), 120) = 76 months -> 25 quarters (rounded).
    oos_n = int(min(max(12, round(n_q * 0.25)), 40))
    oos_start = work.index[-oos_n]
    is_end = work.index[-(oos_n + 1)]
    oos_end = work.index[-1]
    print(f"  Sample: {n_q} quarters {work.index[0].date()} -> {oos_end.date()}")
    print(f"  OOS (v1_max36_25pct_cap120, quarterly-translated): {oos_n} quarters, "
          f"{oos_start.date()} -> {oos_end.date()} — {oos_n} OOS points is FEW; "
          f"found-in-search caveat STRONGER than monthly pairs")
    split = {
        "owner": "evan", "split_policy_id": "v1_max36_25pct_cap120",
        "in_sample_end": is_end.strftime("%Y-%m-%d"), "oos_start": oos_start.strftime("%Y-%m-%d"),
        "oos_end": oos_end.strftime("%Y-%m-%d"), "sample_size_months": n_months,
        "justification": (
            f"Policy v1_max36_25pct_cap120 applied in native QUARTERLY units on the first quarterly pair: "
            f"total sample {n_q} quarters ({n_months} months, 2001-Q1..2026-Q1). "
            f"span = min(max(12q, round({n_q}*0.25)), 40q) = {oos_n} quarters (= {oos_n*3} months; the monthly "
            f"formula min(max(36, round({n_months}*0.25)), 120) = {int(min(max(36, round(n_months*0.25)), 120))} months "
            f"~= the same window). OOS {oos_start.date()}..{oos_end.date()} spans COVID, the 2021-23 wage-inflation "
            f"surge and the 2022 tightening bear — the exact episodes the countercyclical hypothesis is about. "
            f"CAVEAT: {oos_n} quarterly observations is a SMALL OOS sample; any winner is found-in-search with a "
            f"high-variance Sharpe (stronger caveat than Cass's 36 monthly OOS points). IS = {n_q - oos_n} quarters "
            f"(z-score transforms usable from 2003-Q4/2004-Q4 within IS). No structural-break exclusion applied."),
    }
    with open(os.path.join(RESULTS_DIR, "oos_split_record.json"), "w") as f:
        json.dump(split, f, indent=2)

    tstrat = run_lead_grid(df, split, LEADS)

    # Benchmark row (ECON-T4: valid=False, signal=="BENCHMARK")
    spy_ret = work["spy_ret"]
    is_mask = work.index <= is_end
    oos_mask = (work.index >= oos_start) & (work.index <= oos_end)
    mb, mbi = ann_metrics(spy_ret[oos_mask].dropna()), ann_metrics(spy_ret[is_mask].dropna())
    bench = {"signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "P0_buy_and_hold",
             "lead_quarters": 0, "lookback": "LB_NA", "is_sharpe": round(mbi["sharpe"], 4),
             "oos_sharpe": round(mb["sharpe"], 4), "oos_sortino": round(mb["sortino"], 4),
             "oos_calmar": round(mb["calmar"], 4), "oos_ann_return": round(mb["ann_return"], 4),
             "oos_ann_vol": round(mb["ann_vol"], 4), "max_drawdown": round(mb["max_dd"], 4),
             "win_rate": round(mb["win_rate"], 4), "n_trades": 0, "annual_turnover": 0.0,
             "oos_n": int(oos_mask.sum()), "valid": False, "stationarity_class": "n_a"}
    tdf = pd.concat([tstrat, pd.DataFrame([bench])], ignore_index=True)
    assert (tdf["signal"] == "BENCHMARK").sum() == 1, "exactly one benchmark row required (ECON-T4)"
    tpath = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _tournament_io import write_tournament
    write_tournament(tdf, tpath)

    strat_pop = tdf[tdf.signal != "BENCHMARK"]
    n_valid = int(strat_pop["valid"].sum())
    print(f"  Combos evaluated: {len(strat_pop)} strategies + 1 benchmark; valid: {n_valid}")
    print(f"  B&H OOS Sharpe {mb['sharpe']:.3f}, maxDD {mb['max_dd']:.3f}, ann ret {mb['ann_return']:.3f}")

    manifest = {
        "file": os.path.basename(tpath), "pair_id": PAIR_ID,
        "frequency": "QUARTERLY (first quarterly pair)",
        "annualization": "Sharpe = mean/std*sqrt(4); ann_return = mean*4; ann_vol = std*sqrt(4)",
        "grid": {"signals": [k for k, v in SIGNAL_COLS.items() if v in work.columns and work[v].notna().sum() >= SIG_ELIGIBLE_MIN],
                 "thresholds": "T1_fixed_p{25,50,75}, T4_zero (sign-meaningful: accel/yoy_accel/dev_trend), T3_zscore_{+1.0,-1.0} x {LB12,LB20}",
                 "strategies": ["P1_long_cash_{pro,counter}", "P3_long_short_{pro,counter}"],
                 "leads_quarters": LEADS, "lookbacks": list(LOOKBACKS.keys()) + ["LB_NA"],
                 "sparse_grid_rationale": "101 quarterly obs — Dana Phase-0: no dense grids; P2 signal-strength and z-score +/-1.5 variants dropped; zero-cross restricted to sign-meaningful signals (wage growth never negative)"},
        "units": "oos_ann_return / oos_ann_vol / max_drawdown are RATIOS (decimal), not percent",
        "lead_column_note": "lead_quarters (QUARTERS, not months) — quarterly adaptation of the ECON-LL1 monthly standard; L1=~3 months, L8=~24 months",
        "total_strategy_rows": len(strat_pop), "valid_strategy_rows": n_valid,
        "sampling": "exhaustive over the full tradable lead grid L1..L8 quarters (no coarse subset)",
        "benchmark_row": "signal==BENCHMARK, valid=False per ECON-T4",
        "execution_lag": "position_t = rule(signal_{t-lead}), lead >= 1 quarter (BLS releases quarter Q ~1 month after quarter end -> Q print first tradable in Q+1)",
        "small_sample_flag": f"OOS window {int(oos_mask.sum())} QUARTERS — few OOS points; winner is found-in-search / CANDIDATE, not validated (stronger caveat than monthly pairs)",
        "stationarity_flag": "growth family (qoq/2q/yoy/dev_trend) borderline-persistent; 20Q z-scores regime-contaminated (KPSS reject); accel family clean — per-row stationarity_class column",
        "cost_note": "returns are gross of costs; cost sensitivity in tournament_validation",
        "assertions": ["top strategy oos_sharpe > bottom strategy oos_sharpe", "all oos_sharpe finite",
                       "exactly one BENCHMARK row, valid=False"],
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
    rows = []
    for L in LEADS:
        cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid & (tdf.lead_quarters == L)]
        if len(cand) == 0:
            rows.append({"lead_quarters": L, "n_valid": 0, "best_oos_sharpe": np.nan,
                         "median_oos_sharpe": np.nan, "p25_oos_sharpe": np.nan, "p75_oos_sharpe": np.nan,
                         "best_signal": "", "best_threshold": "", "best_strategy": "", "best_max_dd": np.nan})
            continue
        top = cand.loc[cand.oos_sharpe.idxmax()]
        rows.append({"lead_quarters": L, "n_valid": int(len(cand)),
                     "best_oos_sharpe": round(float(top.oos_sharpe), 4),
                     "median_oos_sharpe": round(float(cand.oos_sharpe.median()), 4),
                     "p25_oos_sharpe": round(float(cand.oos_sharpe.quantile(0.25)), 4),
                     "p75_oos_sharpe": round(float(cand.oos_sharpe.quantile(0.75)), 4),
                     "best_signal": top.signal, "best_threshold": top.threshold,
                     "best_strategy": top.strategy, "best_max_dd": round(float(top.max_drawdown), 4)})
    lt = pd.DataFrame(rows)
    lt_path = os.path.join(RESULTS_DIR, f"lead_tournament_{DATE_TAG}.csv")
    lt.to_csv(lt_path, index=False)
    valid_leads = lt[lt.n_valid > 0]
    if len(valid_leads):
        star_row = valid_leads.loc[valid_leads.best_oos_sharpe.idxmax()]
        L_star = int(star_row.lead_quarters)
        best_at_grid = float(star_row.best_oos_sharpe)
    else:
        L_star, best_at_grid = -1, np.nan
    # Full L1..L8 grid is scanned by the main tournament -> published winner is already
    # the global lead max; ECON-LT1 gate informational (no staleness possible).
    gate = "CHARTS-ONLY (full grid scanned natively)"
    print(f"  [ECON-LT1] lead_tournament -> {lt_path}; L*={L_star} best OOS Sharpe {best_at_grid} -> {gate}")

    # --- GH #13 artifact 1: published winner's OWN Sharpe at each lead ---
    # Re-evaluate the winner combo (signal/threshold/strategy/lookback fixed) across leads.
    wc_rows = []
    for L in LEADS:
        match = tdf[(tdf.signal == winner["signal"]) & (tdf.threshold == winner["threshold"]) &
                    (tdf.strategy == winner["strategy"]) & (tdf.lookback == winner["lookback"]) &
                    (tdf.lead_quarters == L)]
        wc_rows.append({"lead_quarters": L,
                        "oos_sharpe": round(float(match.iloc[0].oos_sharpe), 4) if len(match) else np.nan,
                        "is_published_winner": bool(L == int(winner["lead_quarters"]))})
    wc = pd.DataFrame(wc_rows)
    wc_path = os.path.join(RESULTS_DIR, f"lead_winner_curve_{DATE_TAG}.csv")
    wc.to_csv(wc_path, index=False)

    # --- GH #13 artifact 2: clean envelope. SA source -> ALL signals admissible,
    # so the envelope and the "clean" envelope COINCIDE by construction (stated). ---
    env_rows = []
    for L in LEADS:
        cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid & (tdf.lead_quarters == L)]
        if len(cand) == 0:
            env_rows.append({"lead_quarters": L, "best_oos_sharpe": np.nan, "best_signal": "",
                             "best_is_clean": True, "best_clean_oos_sharpe": np.nan, "best_clean_signal": ""})
            continue
        top = cand.loc[cand.oos_sharpe.idxmax()]
        env_rows.append({"lead_quarters": L, "best_oos_sharpe": round(float(top.oos_sharpe), 4),
                         "best_signal": top.signal, "best_is_clean": True,
                         "best_clean_oos_sharpe": round(float(top.oos_sharpe), 4),
                         "best_clean_signal": top.signal})
    env = pd.DataFrame(env_rows)
    env_path = os.path.join(RESULTS_DIR, f"lead_clean_envelope_{DATE_TAG}.csv")
    env.to_csv(env_path, index=False)
    print(f"  [GH #13] lead_winner_curve -> {wc_path}; lead_clean_envelope -> {env_path} "
          f"(SA source: envelope == clean envelope by construction)")
    peak_lead = int(wc.loc[wc.oos_sharpe.idxmax(), "lead_quarters"]) if wc.oos_sharpe.notna().any() else -1
    return lt, lt_path, L_star, best_at_grid, gate, wc, peak_lead


# ===================================================================
# STAGE 7: WINNER SELECTION (ECON-T3 cascade) + artifacts
# ===================================================================
def select_winner(tdf):
    """Winner over the valid strategy population (ECON-T4 excludes BENCHMARK).
    SA source -> no seasonal-cleanliness restriction; objective = plain max_oos_sharpe."""
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid].copy()
    if len(cand) == 0:
        return None, None, None, cand
    cascade = [("oos_sharpe", False), ("oos_ann_return", False),
               ("abs_dd", True), ("n_trades", False), ("signal", True)]
    cand["abs_dd"] = cand["max_drawdown"].abs()
    pool = cand; resolved_at = 1; tie_pool_step1 = None
    for i, (colname, ascending) in enumerate(cascade, start=1):
        best_val = pool[colname].min() if ascending else pool[colname].max()
        nxt = pool[pool[colname] == best_val]
        if i == 1:
            tie_pool_step1 = nxt.copy()
        if len(nxt) == 1:
            resolved_at = i; pool = nxt; break
        pool = nxt; resolved_at = i
    return pool.iloc[0], resolved_at, tie_pool_step1, cand


def derive_winner_series(df, winner, split):
    work = df.dropna(subset=["spy_ret"]).copy()
    is_mask = work.index <= split["in_sample_end"]
    sig = work[SIGNAL_COLS[winner["signal"]]].shift(int(winner["lead_quarters"]))
    thr_name, lb_name = winner["threshold"], winner["lookback"]
    if thr_name.startswith("T1_fixed_p"):
        thr = sig[is_mask].dropna().quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name == "T4_zero":
        thr = 0.0
    elif thr_name.startswith("T3_zscore"):
        lb = LOOKBACKS[lb_name]; roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 8))
        thr = roll.mean() - 1.0 * roll.std() if "neg_" in thr_name else roll.mean() + 1.0 * roll.std()
    else:
        raise ValueError(thr_name)
    above = sig < thr if "neg_" in thr_name else sig > thr
    strat, orientation = winner["strategy"].rsplit("_", 1)
    pos_bool = ~above if orientation == "counter" else above
    if strat == "P1_long_cash":
        position = pos_bool.astype(float)
    else:
        position = pos_bool.astype(float) * 2 - 1
    return position, work["spy_ret"], sig, thr


@log_stage("7_winner_artifacts")
def stage_winner(df, tdf, split, tpath):
    winner, resolved_at, tie_pool, cand = select_winner(tdf)
    if winner is None:
        raise RuntimeError("no valid strategies — null result; escalate to Lead")
    n_valid = len(cand)
    median_sharpe = float(cand["oos_sharpe"].median())
    n_tied = int((cand["oos_sharpe"] == winner["oos_sharpe"]).sum())
    print(f"  Valid strategies: {n_valid}; winner: {winner['signal']}/{winner['threshold']}/"
          f"{winner['strategy']}/L{winner['lead_quarters']}q/{winner['lookback']}")
    print(f"  OOS Sharpe {winner['oos_sharpe']} | ties at step1: {n_tied} | resolved at step {resolved_at} "
          f"| stationarity_class={winner['stationarity_class']}")

    if resolved_at > 1:
        lines = [f"# Tournament Tie Note — {PAIR_ID} ({DATE_TAG})", "",
                 f"Winner resolved at cascade step {resolved_at} (ECON-T3).", "",
                 "## Candidates tied at step 1 (oos_sharpe)", "",
                 tie_pool[["signal", "threshold", "strategy", "lead_quarters", "lookback",
                           "oos_sharpe", "oos_ann_return", "max_drawdown", "n_trades"]].to_markdown(index=False),
                 "", "Interpretation: candidates near-equivalent on the primary objective; the selected "
                 "winner is preferred on the documented tie-break dimension."]
        with open(os.path.join(RESULTS_DIR, "tournament_tie_note.md"), "w") as f:
            f.write("\n".join(lines))
        print("  Tie note written (cascade fired beyond step 1)")

    position, spy_ret, sig_lagged, thr = derive_winner_series(df, winner, split)
    oos_mask = (spy_ret.index >= split["oos_start"]) & (spy_ret.index <= split["oos_end"])
    strat_ret = position * spy_ret
    m = ann_metrics(strat_ret[oos_mask])
    rec = {}
    for key, computed, reported, tol in [
            ("oos_sharpe", m["sharpe"], float(winner["oos_sharpe"]), 0.01),
            ("oos_max_drawdown", m["max_dd"], float(winner["max_drawdown"]), 0.005),
            ("oos_ann_return", m["ann_return"], float(winner["oos_ann_return"]), 0.005)]:
        diff = computed - reported
        rec[key] = {"computed": round(float(computed), 6), "reported_tournament": reported,
                    "diff": round(float(diff), 6), "tolerance": tol,
                    "verdict": "PASS" if abs(diff) <= tol else "FAIL"}
    assert all(v["verdict"] == "PASS" for v in rec.values()), f"ECON-SR1 reconciliation FAILED: {rec}"
    print("  ECON-SR1 reconciliation: PASS on all three headline metrics")

    sr = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"),
                       "position": position.reindex(spy_ret.index).fillna(0.0).values,
                       "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0.0).values,
                       "bh_return": spy_ret.values})
    sr_path = os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv")
    sr.to_csv(sr_path, index=False)
    with open(os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}_meta.json"), "w") as f:
        json.dump({"pair_id": PAIR_ID, "artifact": os.path.basename(sr_path),
                   "produced_by": "scripts/pair_pipeline_eci_total_comp_spy.py", "rule": "ECON-SR1",
                   "source": "pipeline_native_derivation (same code path as tournament evaluation)",
                   "returns_file": DATA_PATH, "coverage_start": str(spy_ret.index[0].date()),
                   "coverage_end": str(spy_ret.index[-1].date()), "frequency": "quarterly",
                   "annualization": "Sharpe sqrt(4); ann_return mean*4",
                   "oos_start": split["oos_start"], "oos_end": split["oos_end"],
                   "position_semantics": (f"position on row t = return-accrual weight for quarter t; signal lagged "
                                          f"{int(winner['lead_quarters'])} quarter(s); strategy_return = position * bh_return"),
                   "reconciliation": {k: {"computed": v["computed"], "reported_winner_summary": v["reported_tournament"],
                                          "diff": v["diff"], "tolerance": v["tolerance"], "verdict": v["verdict"]}
                                      for k, v in rec.items()},
                   "generated_at": NOW_ISO, "generated_by": "Econ Evan (feat260705_eci_spy)"}, f, indent=2)

    # winner_trade_log.csv
    log = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"),
                        "signal_value": sig_lagged.reindex(spy_ret.index).round(4),
                        "threshold": (thr.reindex(spy_ret.index).round(4) if isinstance(thr, pd.Series) else np.round(thr, 4)),
                        "position": position.reindex(spy_ret.index).fillna(0.0),
                        "spy_return": spy_ret.round(6),
                        "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0.0).round(6)})
    log["cumulative_return"] = ((1 + log["strategy_return"]).cumprod() - 1).round(6)
    log.to_csv(os.path.join(RESULTS_DIR, "winner_trade_log.csv"), index=False)

    # broker-style trade log (Rule C4)
    spy_px = df["spy"].reindex(spy_ret.index)
    broker_rows = []
    cum = (1 + strat_ret.reindex(spy_ret.index).fillna(0.0)).cumprod()
    prev = 0.0; capital = 10000.0
    sig_disp = f"{winner['signal']} ({SIGNAL_COLS[winner['signal']]})"
    posf = position.reindex(spy_ret.index).fillna(0.0)
    for dt in spy_ret.index:
        p = float(posf.loc[dt])
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
                                           f"{th:.3f} — position {prev*100:.0f}% -> {p*100:.0f}%"
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

    return (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
            position, strat_ret, sig_lagged, thr, cand)


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
    top5 = cand.nlargest(min(5, len(cand)), "oos_sharpe")
    rng = np.random.default_rng(42); boot = np.zeros(5000)
    for b in range(5000):
        s = rng.choice(spy_oos.values, size=len(spy_oos), replace=True)
        boot[b] = (s.mean() / s.std()) * ANN if s.std() > 0 else 0
    rows = [{"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
             "lead_quarters": r.lead_quarters, "lookback": r.lookback, "oos_sharpe": r.oos_sharpe,
             "bootstrap_p_value": round(float((boot >= r.oos_sharpe).mean()), 4),
             "significant_at_5pct": bool((boot >= r.oos_sharpe).mean() < 0.05)} for r in top5.itertuples()]
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
    df, hmm_ok = stage_signals(df)
    corr_df = stage_correlations(df)
    ccf_df, ty_df, lp_df, reg_df, rev_flag, fwd_lp_flag = stage_core_models(df)
    lc, lc_path = stage_lead_analysis(df)
    qdf = stage_quartiles(df)
    tdf, split, tpath = stage_tournament(df)
    (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
     position, strat_ret, sig_lagged, thr, cand) = stage_winner(df, tdf, split, tpath)
    lt, lt_path, L_star, best_at_grid, gate, wc, peak_lead = stage_lead_tournament(df, split, tdf, winner)
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
    thr_rule = "lt" if neg_thr else "gt"
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

    # ================= ECON-T5 selection provenance =================
    tdf_read = tdf.reset_index(drop=True)
    def _row_id(w):
        mask = ((tdf_read.signal == w["signal"]) & (tdf_read.threshold == w["threshold"]) &
                (tdf_read.strategy == w["strategy"]) & (tdf_read.lead_quarters == w["lead_quarters"]) &
                (tdf_read.lookback == w["lookback"]))
        idxs = list(tdf_read.index[mask])
        return idxs[0] if idxs else -1
    all_valid = tdf_read[(tdf_read.signal != "BENCHMARK") & tdf_read.valid].copy()
    pop_max = float(all_valid["oos_sharpe"].max())
    ru = all_valid.sort_values("oos_sharpe", ascending=False)
    runner = ru.iloc[1] if len(ru) > 1 else None
    winner_row_idx = _row_id(winner)
    n_sig = len([k for k, v in SIGNAL_COLS.items() if v in df.columns and df[v].notna().sum() >= SIG_ELIGIBLE_MIN])
    selection = {
        "objective": "max_oos_sharpe",
        "objective_formula": ("oos_ret.mean()/oos_ret.std()*sqrt(4) — QUARTERLY annualization — maximised over the "
                              "full valid strategy population (SA source: no seasonal-cleanliness restriction; "
                              "ECON-T4 benchmark excluded); ties resolved by the ECON-T3 cascade"),
        "grid_scanned": {"leads": LEADS, "n_signals": n_sig,
                         "n_thresholds": 8, "n_strategies": 4,
                         "n_valid_combos": int(len(all_valid)),
                         "median_valid_objective": round(float(all_valid["oos_sharpe"].median()), 4)},
        "tie_break_step": int(resolved_at) - 1,
        "raw_winner_row": {"signal": winner["signal"], "threshold": winner["threshold"],
                           "strategy": winner["strategy"], "lead_column": "lead_quarters",
                           "lead_value": int(winner["lead_quarters"]),
                           "source_tournament_file": os.path.basename(tpath),
                           "source_row_index": int(winner_row_idx),
                           "display_alias": (f"signal_code={REGISTRY_CODE[winner['signal']]} (raw signal={winner['signal']}); "
                                             f"strategy_family={strat_family} (raw strategy={winner['strategy']})")},
        "runner_up": (None if runner is None else
                      {"signal": runner["signal"], "threshold": runner["threshold"], "strategy": runner["strategy"],
                       "lead_value": int(runner["lead_quarters"]), "objective_value": round(float(runner["oos_sharpe"]), 4)}),
        "rationale": (f"Maximiser of OOS Sharpe over the full tradable QUARTERLY lead grid L1..L8 "
                      f"({len(all_valid)} valid combos; median valid OOS Sharpe "
                      f"{round(float(all_valid['oos_sharpe'].median()),4)}). FIRST QUARTERLY PAIR: leads in quarters "
                      f"(L1=~3M pub-lag floor, L8=2yr), Sharpe annualized by sqrt(4). ECON-LT1 gate: full grid scanned "
                      f"natively -> no staleness possible. SMALL-SAMPLE CAVEAT (STRONG): OOS = "
                      f"{int(winner['oos_n'])} QUARTERS only -> the winner is found-in-search / CANDIDATE, never a "
                      f"validated edge; the caveat is stronger than any monthly pair to date."),
        "objective_runner_up_divergence": None,
    }
    # ECON-T5 validations
    assert winner_row_idx >= 0, "raw winner row must resolve to exactly one tournament row"
    assert abs(float(winner["oos_sharpe"]) - pop_max) <= 1e-6, \
        "divergence is null -> winner must equal the population max (ECON-T5 §5c)"
    if runner is not None:
        assert float(runner["oos_sharpe"]) <= float(winner["oos_sharpe"]) + 1e-9, "runner-up must be 2nd best"

    winner_summary = {
        "pair_id": PAIR_ID, "generated_at": NOW_ISO,
        "signal_column": SIGNAL_COLS[winner["signal"]],
        "signal_code": REGISTRY_CODE[winner["signal"]],
        "signal_display_name": f"ECI Total Compensation {winner['signal']}",
        "target_symbol": TARGET_SYMBOL, "threshold_code": winner["threshold"],
        "threshold_value": round(thr_value, 4), "threshold_rule": thr_rule,
        "threshold_note": ("threshold is rolling (window per lookback, in QUARTERS); threshold_value is the latest rolling value — "
                           "see winner_trade_log.csv for the full path" if isinstance(thr, pd.Series) else "static threshold (IS-calibrated)"),
        "strategy_family": strat_family, "strategy_code": strat_family.split("_")[0],
        "strategy_display_name": {"P1_long_cash": "Long/Cash", "P3_long_short": "Long/Short"}[strat_family],
        "strategy_description": "",
        "lead_value": int(winner["lead_quarters"]), "lead_unit": "quarters",
        "lead_description": (f"Signal lead = {int(winner['lead_quarters'])} QUARTER(S) (~{int(winner['lead_quarters'])*3} months); "
                             f"L1 is the real-time floor (BLS releases quarter Q's ECI ~1 month after quarter end)"),
        "lookback": winner["lookback"], "direction": direction,
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4), "oos_sortino": round(float(winner["oos_sortino"]), 4),
        "oos_calmar": round(float(winner["oos_calmar"]), 4), "oos_ann_return": round(float(winner["oos_ann_return"]), 4),
        "oos_ann_vol": round(float(winner["oos_ann_vol"]), 4), "oos_max_drawdown": round(float(winner["max_drawdown"]), 4),
        "oos_win_rate": round(float(winner["win_rate"]), 4), "oos_n_trades": int(winner["n_trades"]),
        "annual_turnover": round(float(winner["annual_turnover"]), 2), "oos_n": int(winner["oos_n"]),
        "oos_period_start": split["oos_start"], "oos_period_end": split["oos_end"],
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4), "bh_ann_return": round(float(bh["oos_ann_return"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4), "cost_assumption_bps": COST_BPS,
        "total_combos": int(len(tdf) - 1), "valid_combos": n_valid, "schema_version": "1.1.0",
        "selection": selection,
        "notes": (f"Mode 1, feat260705_eci_spy — FIRST QUARTERLY PAIR (annualization sqrt(4); leads/lookbacks/oos_n in "
                  f"QUARTERS). Tournament: {len(tdf)-1} strategy combos (+1 benchmark, valid=False per ECON-T4), "
                  f"{n_valid} valid, sparse grid over full tradable lead grid L1..L8 quarters. Winner by ECON-T3 "
                  f"cascade (resolved at step {resolved_at}; {n_tied} tied at step 1). "
                  f"SMALL-SAMPLE / FOUND-IN-SEARCH (STRONG): OOS window is {int(winner['oos_n'])} QUARTERS "
                  f"-> the winner is a CANDIDATE, not a validated edge; OOS Sharpe is high-variance. "
                  f"Winner stationarity class: {winner['stationarity_class']}. "
                  f"Lead-lag verdict (empirical): ECI->SPY TY-Granger sig lags(q) {fwd_sig_lags or 'NONE'}, "
                  f"SPY->ECI sig lags(q) {rev_sig_lags or 'NONE'}; pre-whitened CCF sig lead(+) lags {ccf_lead or 'NONE'}, "
                  f"lag(-) lags {ccf_lag or 'NONE'} -> classified '{leadlag}'. "
                  f"Winner's own lead-curve peaks at L{peak_lead}q (published L{int(winner['lead_quarters'])}q). "
                  f"Robustness: winner bootstrap p={winner_boot_p} (vs resampled B&H); IS Sharpe {float(winner['is_sharpe']):.2f} "
                  f"vs OOS {float(winner['oos_sharpe']):.2f}; CP1 durability '{verdict}'; corr sign-stability '{stab}'. "
                  f"Gross of costs; sensitivity in tournament_validation_{DATE_TAG}/."),
    }
    sd = ("Long SPY when the lagged ECI wage signal is {} its threshold; otherwise {}."
          .format("below" if thr_rule == "lt" else "above",
                  "cash" if strat_family == "P1_long_cash" else "short SPY"))
    if not long_when_high:
        sd += " (Countercyclical orientation: low/decelerating wage inflation = risk-on.)"
    else:
        sd += " (Procyclical orientation: high/accelerating wage inflation = risk-on.)"
    sd += " Rebalanced QUARTERLY (first quarterly pair)."
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
        f"{orientation}/L{winner['lead_quarters']}q/{winner['lookback']}) is {direction}: OOS Sharpe "
        f"{winner_summary['oos_sharpe']:.2f} vs B&H {winner_summary['bh_sharpe']:.2f} (sqrt(4) annualization). "
        f"SMALL-SAMPLE CANDIDATE: {int(winner['oos_n'])}-QUARTER OOS -> found-in-search, not a validated edge; "
        f"bootstrap p={winner_boot_p}, durability '{verdict}'. Winner's own lead-curve peaks at L{peak_lead}q "
        f"(published L{int(winner['lead_quarters'])}q).")
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
        ("hmm_2state_prob_stress", "P(high wage-inflation regime) from 2-state HMM on YoY growth (level-regime split)", "GaussianHMM(yoy)", "regime_state"),
        ("markov_regime_2state", "P(high-variance regime) from Markov-switching regression spy_ret~yoy", "MarkovRegression", "regime_state")]]
    if not hmm_ok:
        ind_der = [d for d in ind_der if d["name"] != "hmm_2state_prob_stress"]
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
        {"metric": "OOS Sharpe (buy & hold)", "value": f"{winner_summary['bh_sharpe']:.2f}", "unit": "ratio", "delta": None},
        {"metric": "OOS Annual Return (winner)", "value": f"{winner_summary['oos_ann_return']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_ann_return']*100:+.1f}pp vs B&H"},
        {"metric": "OOS Max Drawdown (winner)", "value": f"{winner_summary['oos_max_drawdown']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_max_drawdown']*100:+.1f}pp vs B&H"},
        {"metric": "Valid strategy combos", "value": f"{n_valid}", "unit": "count", "delta": None},
        {"metric": "OOS window", "value": f"{split['oos_start']} → {split['oos_end']} ({int(winner['oos_n'])} quarters, candidate)", "unit": "dates", "delta": None},
    ]
    with open(os.path.join(RESULTS_DIR, "kpis.json"), "w") as f:
        json.dump(kpis, f, indent=2)

    # lead_sweep_manifest (ECON-LT1 record)
    with open(DATA_PATH, "rb") as f:
        input_sha = "sha256:" + hashlib.sha256(f.read()).hexdigest()[:16]
    lead_manifest = {
        "pair": PAIR_ID, "run_date": DATE_TAG, "frozen": False,
        "granularity": "QUARTERS L1..8 tradable (L0 diagnostic-only in lead_correlation; quarterly adaptation of ECON-LL1)",
        "freq_native": "Q",
        "design_note": ("FIRST QUARTERLY pair; lead L = quarter shift on quarter-end signals. L0 excluded from the "
                        "tradable grid (BLS ~1-month publication lag: quarter Q's print is first tradable in Q+1). "
                        "Grid ceiling L8 (2 years) — deeper leads on 101 obs destroy effective sample."),
        "oos_start": split["oos_start"], "is_end": split["in_sample_end"], "input_file": DATA_PATH,
        "input_sha256": input_sha, "lead_correlation_file": f"{PAIR_ID}/lead_correlation_{DATE_TAG}.csv",
        "lead_tournament_file": f"{PAIR_ID}/lead_tournament_{DATE_TAG}.csv",
        "lead_winner_curve_file": f"{PAIR_ID}/lead_winner_curve_{DATE_TAG}.csv",
        "lead_clean_envelope_file": f"{PAIR_ID}/lead_clean_envelope_{DATE_TAG}.csv",
        "clean_envelope_note": "SA source: all signals admissible -> envelope and clean envelope COINCIDE by construction",
        "published_winner": {"signal": SIGNAL_COLS[winner["signal"]], "lead": int(winner["lead_quarters"]),
                             "lead_unit": "quarters", "oos_sharpe": round(float(winner["oos_sharpe"]), 4)},
        "winner_curve_peak_lead": peak_lead,
        "L_star": L_star, "best_oos_sharpe_at_grid": round(float(best_at_grid), 4) if pd.notna(best_at_grid) else None,
        "gate_decision": gate,
        "assertions": ["tradable lead grid is L1..8 QUARTERS (L0 non-tradable, pub-lag floor)",
                       "main tournament scans the full L1..8 grid -> published winner is the global lead max",
                       f"ECON-LT1 gate: L*={L_star} -> {gate}"],
        "small_sample_caveat": f"OOS = {int(winner['oos_n'])} quarters -> winner is found-in-search; lead-sweep peaks are high-variance."}
    with open(os.path.join(RESULTS_DIR, f"lead_sweep_manifest_{DATE_TAG}.json"), "w") as f:
        json.dump(lead_manifest, f, indent=2)

    # design_note.md — APPEND Phase-1 sections to Dana's Phase-0 note (preserve her content)
    with open(os.path.join(RESULTS_DIR, "design_note.md")) as f:
        dana_note = f.read().rstrip()
    phase1 = f"""

---

# Phase 1 addendum — Econometrics & Tournament (Evan, {DATE_TAG})

## Quarterly conventions (stated explicitly — first quarterly pair)
- **Annualization: Sharpe = mean/std x sqrt(4); ann_return = mean x 4; ann_vol = std x sqrt(4).**
- Lead grid **L1..L8 in QUARTERS** (L1 = pub-lag floor, BLS releases ~1 month after quarter end;
  L8 = 2yr ceiling — wage->Fed->equity transmission has no rationale beyond ~2yr and deeper leads
  eat the 101-obs sample). Tournament CSV lead column is `lead_quarters` (NOT lead_months).
- Lookbacks LB12 (~3yr) / LB20 (~5yr) quarters. Correlation horizons spy_fwd_1q/2q/4q.

## Method coverage (Rule C1, macro) & quarterly adaptations
- Correlations incl. distance (n-floor {CORR_N_FLOOR} quarters); horizons recorded as 63/126/252 horizon_days.
- Pre-whitened CCF at quarterly lags -8..+8 (pre-whitening ESSENTIAL — YoY wage inflation near-I(1); AR order by AIC, max 4).
- Toda-Yamamoto Granger, lags 1..4 quarters ONLY (101 obs cannot support deeper quarterly VARs), d_max=1.
- Local projections fwd+rev at 1/2/4-quarter horizons, HAC SEs.
- Quantile regression on 1q-fwd (tail taus on ~97 obs = ~5 effective tail points; interpret loosely).
- Transfer entropy: tercile-binned, 500 permutations — LOW POWER at 97 obs; retained as a directional check with caveat.
- HMM 2-state on YoY: attempted with a degeneracy guard (min 10% regime occupancy). NOTE: on a series this
  persistent the HMM splits wage-inflation LEVEL regimes (high vs low), not volatility states — still
  economically meaningful (2021-23 surge vs pre-COVID calm) but transition probabilities weakly identified.
  HMM converged and retained: {hmm_ok}.
- Markov-switching regression spy_ret ~ yoy (2-state, switching variance).
- Stationarity: Dana's tests (stationarity_tests_{DATE_TAG}.csv) reviewed and CONFIRMED, not re-run.
  Growth family borderline-persistent; 20Q z-scores regime-contaminated (KPSS reject); accel family clean.
  Each tournament row carries a `stationarity_class` flag.

## Sparse grid (BINDING Dana small-sample constraint — do not explode combos on 101 points)
- Thresholds: IS percentiles {{25,50,75}}, zero-cross ONLY on sign-meaningful signals (accel/yoy_accel/dev_trend
  — wage growth itself never goes negative, nominal stickiness), rolling z-score +/-1.0 at LB12/LB20
  (the +/-1.5 variants and Jenks/GMM/CUSUM thresholds dropped).
- Strategies: P1 long/cash + P3 long/short x pro/counter (P2 signal-strength sizing dropped — a continuous
  sizing rule has too many effective d.o.f. for 25 OOS quarters).
- Eligibility: signal >= {SIG_ELIGIBLE_MIN} non-NaN quarters; IS >= 40 quarters; OOS >= 20 quarters; validity
  requires OOS Sharpe > 0.3 (equity threshold) and turnover < 6 position-changes/yr.

## OOS split (ECON-OOS2, quarterly-translated)
Policy v1_max36_25pct_cap120 in native quarterly units: span = min(max(12q, round(101 x 0.25)), 40q) =
{int(min(max(12, round(101*0.25)), 40))} quarters -> OOS {split['oos_start']}..{split['oos_end']}. OOS spans COVID +
the 2021-23 wage surge + the 2022 tightening bear — exactly the episodes the countercyclical hypothesis concerns.
**Found-in-search caveat is STRONGER than any monthly pair: only {int(winner['oos_n'])} OOS quarters.**

## Lead-lag verdict (empirical — determined by Granger/CCF/LP, NOT the prior)
- ECI->SPY TY-Granger significant lags (quarters): {fwd_sig_lags or 'NONE'}
- SPY->ECI TY-Granger significant lags (quarters): {rev_sig_lags or 'NONE'}
- Pre-whitened CCF significant lead(+) lags: {ccf_lead or 'NONE'}; lag(-) lags: {ccf_lag or 'NONE'}
- LP forward significant: {fwd_lp_flag}; reverse-causality flag: {rev_flag}
- **Classification: {leadlag}.** Winner direction (empirical): {direction}.
- indicator_nature in interpretation_metadata set to the EMPIRICAL verdict (Dana's provisional prior was 'lagging').

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal). Lead column `lead_quarters`. Both orientations tested.
- GH #13 artifacts emitted from the start: lead_winner_curve_{DATE_TAG}.csv (published winner's own Sharpe per lead;
  peak at L{peak_lead}q vs published L{int(winner['lead_quarters'])}q) and lead_clean_envelope_{DATE_TAG}.csv
  (SA source -> envelope == clean envelope by construction; stated in the file's manifest entry).
- CP2 skipped (regime_story: false). Returns gross of costs; cost grid in tournament_validation_{DATE_TAG}/.

## New pair — no prior version; Rule C3 regression diff N/A.
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

    # evidence_status.json
    ev = {"pair_id": PAIR_ID, "generated_at": NOW_ISO, "generated_by": "evan",
          "blocks": {
              "correlations": "ready", "lead_correlation": "ready", "lead_tournament": "ready",
              "lead_winner_curve": "ready", "lead_clean_envelope": "ready",
              "ccf_prewhitened": "ready", "granger_causality": "ready", "transfer_entropy": "ready",
              "local_projections": "ready", "quantile_regression": "ready", "regime_quartile_returns": "ready",
              "hmm_states": "ready" if hmm_ok else "skipped_degenerate_small_sample",
              "subperiod_sharpe": "ready", "structural_break": "ready", "rolling_correlation": "ready",
              "tournament": "ready", "winner_summary": "ready"},
          "caveats": [f"OOS = {int(winner['oos_n'])} QUARTERS -> winner is a found-in-search CANDIDATE (high-variance Sharpe; STRONGER caveat than monthly pairs)",
                      "FIRST QUARTERLY pair: sqrt(4) annualization; leads/lookbacks in quarters",
                      "growth-family signals borderline-persistent; 20Q z-scores regime-contaminated (KPSS reject)",
                      "transfer entropy low-power at ~97 obs (directional check only)",
                      f"empirical lead-lag class: {leadlag}"]}
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
    print(f"  Strategy combos: {len(tdf)-1} | valid: {n_valid} | median OOS Sharpe (valid): {median_sharpe:.3f}")
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
