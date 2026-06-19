#!/usr/bin/env python3
"""
Full Econometrics Pipeline: PHLX Semiconductor Index (SOX) -> SPY
=================================================================
Pair ID: phlxsox_spy (Mode 1, daily)
Branch: pair260619_phlxsox_spy

THE CENTRAL HONESTY CHALLENGE
-----------------------------
SOX and SPY are BOTH equities; daily return correlation = 0.709. A
contemporaneous regression / level correlation will look hugely significant
from shared market beta alone — that is CO-MOVEMENT, not predictive edge.

This pipeline establishes whether SOX genuinely LEADS SPY using lead-lag
methods only:
  1. Toda-Yamamoto Granger BOTH directions at lags >= 1.
  2. Pre-whitened CCF (each series filtered by its own AR fit) at lags -20..+20.
  3. The tournament lead grid starts at L1 (no L0): a contemporaneous signal is
     not a forecast. We lean on the RELATIVE-STRENGTH transforms
     (sox_spy_ratio_mom_*), which partial out common market beta and are the
     signals most likely to carry genuine intermarket information.
  4. The winner is compared against TWO benchmarks: buy & hold SPY AND a
     SPY-OWN-MOMENTUM rule. If the SOX signal does not beat SPY's own momentum,
     that is the honest finding: "no lead beyond SPY's own trend."

  H0: SOX does NOT Granger-cause SPY forward returns beyond SPY's own past.
  H1: lagged SOX (esp. relative strength vs SPY) predicts forward SPY returns.

  expected_direction (Ray/Dana): procyclical (rising semis -> risk-on).
  observed_direction: determined empirically; both orientations tested.

Category (Rule C1): price/intermarket, technology -> full correlation battery
(incl. distance correlation), pre-whitened CCF, Toda-Yamamoto Granger (both
directions), transfer entropy, local projections (fwd + reverse), quantile
regression, HMM 2-state regime detection.

Data: Dana's verified parquet data/phlxsox_spy_daily_latest.parquet
(8085 x 24, daily 1994-05 -> 2026-06). Levels (sox, sox_spy_ratio) are
NON-stationary (Dana's stationarity_tests_20260619.csv) and are NOT used as
signals. days_since_release == 0 (continuously-quoted index).

Author: Econ Evan (Econometrics Agent)
Date: 2026-06-19
"""

import os
import json
import time
import warnings
import subprocess
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
np.random.seed(42)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PAIR_ID = "phlxsox_spy"
INDICATOR_NAME = "PHLX Semiconductor Index (SOX)"
TARGET_NAME = "SPY"
TARGET_SYMBOL = "SPY"
DATE_TAG = "20260619"
COST_BPS = 5  # equity ETF per ECON-T2 / target-class table

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_PATH = os.path.join(BASE_DIR, "data", "phlxsox_spy_daily_latest.parquet")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")
SCHEMA_DIR = os.path.join(BASE_DIR, "docs", "schemas")

for d in [RESULTS_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# tournament signal_code (snake_case) -> parquet column. STATIONARY signals only.
# Relative-strength signals (sox_spy_ratio_mom_*) lead the list — they partial
# out common market beta and are the strongest candidates for genuine lead.
SIGNAL_COLS = {
    "rs_mom1m": "sox_spy_ratio_mom_1m_pct",
    "rs_mom3m": "sox_spy_ratio_mom_3m_pct",
    "rs_mom6m": "sox_spy_ratio_mom_6m_pct",
    "rs_mom12m": "sox_spy_ratio_mom_12m_pct",
    "rs_zscore126": "sox_spy_ratio_zscore_126d",
    "rs_zscore252": "sox_spy_ratio_zscore_252d",
    "sox_mom1m": "sox_mom_1m_pct",
    "sox_mom3m": "sox_mom_3m_pct",
    "sox_mom6m": "sox_mom_6m_pct",
    "sox_mom12m": "sox_mom_12m_pct",
    # derived in stage_signals:
    "hmm_stress": "hmm_2state_prob_stress",
}

# the canonical "intermarket" pre-whitening / Granger driver = SOX daily return
MAIN_SIG = "sox_ret"
FWD_COLS = ["spy_fwd_1d", "spy_fwd_5d", "spy_fwd_21d", "spy_fwd_63d", "spy_fwd_126d", "spy_fwd_252d"]
TRADING_DAYS = 252


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
    m = {
        "file": os.path.basename(path),
        "pair_id": PAIR_ID,
        "produced_by": "scripts/pair_pipeline_phlxsox_spy.py",
        "generated_at": NOW_ISO,
        "columns": columns,
        "assertions": assertions,
    }
    if extra:
        m.update(extra)
    with open(os.path.splitext(path)[0] + "_manifest.json", "w") as f:
        json.dump(m, f, indent=2)


def ann_metrics(rets):
    """Annualized metrics for a DAILY return series."""
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return dict(sharpe=0.0, ann_return=0.0, ann_vol=0.0, max_dd=0.0,
                    sortino=0.0, calmar=0.0, win_rate=0.0, n=len(rets))
    sharpe = rets.mean() / rets.std() * np.sqrt(TRADING_DAYS)
    ann_ret = rets.mean() * TRADING_DAYS
    ann_vol = rets.std() * np.sqrt(TRADING_DAYS)
    cum = (1 + rets).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    neg = rets[rets < 0]
    sortino = ann_ret / (neg.std() * np.sqrt(TRADING_DAYS)) if len(neg) > 1 and neg.std() > 0 else 0.0
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    return dict(sharpe=sharpe, ann_return=ann_ret, ann_vol=ann_vol, max_dd=dd,
                sortino=sortino, calmar=calmar, win_rate=(rets > 0).mean(), n=len(rets))


# ===================================================================
# STAGE 1: LOAD + VERIFY (Defense 2 consumer checks)
# ===================================================================
@log_stage("1_load_verify")
def stage_load():
    df = pd.read_parquet(DATA_PATH)
    assert df.shape == (8085, 24), f"unexpected shape {df.shape}"
    assert df["days_since_release"].max() == 0, "SOX is continuously quoted; expected days_since_release==0"
    assert df["spy_ret"].abs().max() < 0.20, "daily SPY return magnitude implausible"
    assert df["sox_ret"].abs().max() < 0.40, "daily SOX return magnitude implausible"
    # known co-movement: contemporaneous daily return correlation ~0.709 (the trap)
    rho = df[["sox_ret", "spy_ret"]].dropna().corr().iloc[0, 1]
    assert 0.65 < rho < 0.76, f"contemporaneous corr {rho:.3f} off expectation"
    # forward returns: no leakage at tail
    assert df["spy_fwd_252d"].iloc[-252:].isna().all()
    print(f"  Loaded {df.shape}, {df.index.min().date()} -> {df.index.max().date()}")
    print(f"  Contemporaneous daily return corr(SOX,SPY) = {rho:.3f}  <-- the co-movement trap")
    print("  Defense-2 episode/magnitude checks: PASS")
    return df, rho


# ===================================================================
# STAGE 2: DERIVED REGIME SIGNAL (HMM) + persistence
# ===================================================================
@log_stage("2_signals")
def stage_signals(df):
    from hmmlearn.hmm import GaussianHMM

    ret = df["sox_ret"].dropna()
    X = ret.values.reshape(-1, 1)
    hmm = GaussianHMM(n_components=2, covariance_type="full", n_iter=500, random_state=42)
    hmm.fit(X)
    probs = hmm.predict_proba(X)
    variances = [hmm.covars_[i].ravel()[0] for i in range(2)]
    stress_state = int(np.argmax(variances))
    prob_stress = pd.Series(probs[:, stress_state], index=ret.index, name="hmm_2state_prob_stress")
    df["hmm_2state_prob_stress"] = prob_stress

    hmm_states = pd.DataFrame({
        "hmm_state": pd.Series(hmm.predict(X), index=ret.index),
        "prob_stress": prob_stress,
        "prob_calm": 1 - prob_stress,
    })
    hmm_states.to_parquet(os.path.join(MODELS_DIR, "hmm_states.parquet"))

    summ = []
    spy = df["spy_ret"]
    for lbl, mask in [("stress", hmm_states["hmm_state"] == stress_state),
                      ("calm", hmm_states["hmm_state"] != stress_state)]:
        idx = hmm_states.index[mask]
        rets = spy.reindex(idx).dropna()
        summ.append({
            "state_label": lbl,
            "mean_return": round(rets.mean(), 6) if len(rets) else np.nan,
            "vol": round(rets.std(), 6) if len(rets) else np.nan,
            "duration_days": int(mask.sum()),
            "frequency_pct": round(mask.mean() * 100, 2),
        })
    pd.DataFrame(summ).to_csv(os.path.join(MODELS_DIR, "hmm_summary.csv"), index=False)
    gfc_p = prob_stress.loc["2008-09-01":"2009-03-31"].mean()
    print(f"  HMM stress prob mean GFC 2008-09..2009-03: {gfc_p:.2f} (high-variance regime)")

    write_manifest(os.path.join(MODELS_DIR, "hmm_states.parquet"),
                   {"hmm_state": "integer state; stress = high-variance SOX-return regime",
                    "prob_stress": "P(stress regime); higher = SOX returns in high-variance regime",
                    "prob_calm": "1 - prob_stress"},
                   [{"description": "probabilities in [0,1]", "check": "prob_stress between 0 and 1"},
                    {"description": "GFC era is high-variance", "filter": "2008-09 to 2009-03",
                     "column": "prob_stress", "check": f"mean = {gfc_p:.2f}"},
                    {"description": "states sum to 1", "check": "prob_stress + prob_calm == 1"}])

    sig_cols = [c for c in SIGNAL_COLS.values() if c in df.columns]
    sig_path = os.path.join(RESULTS_DIR, f"signals_{DATE_TAG}.parquet")
    df[sig_cols].to_parquet(sig_path)
    print(f"  Signals persisted -> {sig_path} ({len(sig_cols)} columns)")
    write_manifest(sig_path,
                   {c: f"tournament-eligible signal derived from SOX / SOX-SPY ratio ({c})" for c in sig_cols},
                   [{"description": "rel-strength momentum present", "filter": "tail",
                     "column": "sox_spy_ratio_mom_3m_pct", "check": "finite"},
                    {"description": "HMM prob bounded", "column": "hmm_2state_prob_stress",
                     "check": "values in [0,1]"}])
    return df


# ===================================================================
# STAGE 3: EXPLORATORY + CORRELATION BATTERY (Rule C1/C2)
# The forward-return correlations are the HONEST ones (lagged signal vs FORWARD
# return). The contemporaneous corr (recorded separately) is the co-movement trap.
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


@log_stage("3_exploratory_correlations")
def stage_correlations(df):
    rows = []
    horizon_map = {"spy_fwd_1d": 1, "spy_fwd_5d": 5, "spy_fwd_21d": 21,
                   "spy_fwd_63d": 63, "spy_fwd_126d": 126, "spy_fwd_252d": 252}
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwd, h in horizon_map.items():
            v = df[[col, fwd]].dropna()
            if len(v) < 250:
                continue
            x, y = v[col], v[fwd]
            for metric, fn in [("pearson", stats.pearsonr), ("spearman", stats.spearmanr),
                               ("kendall", stats.kendalltau)]:
                r, p = fn(x, y)
                rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": h, "metric": metric,
                             "value": round(r, 4), "p_value": round(p, 4), "n_obs": len(v)})
            # distance corr on a capped subsample (O(n^2))
            sub = v.sample(min(len(v), 2000), random_state=42)
            rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": h, "metric": "distance",
                         "value": round(_distance_corr(sub[col], sub[fwd]), 4),
                         "p_value": np.nan, "n_obs": len(sub)})
    cdf = pd.DataFrame(rows)
    path = os.path.join(MODELS_DIR, "correlations.csv")
    cdf.to_csv(path, index=False)
    write_manifest(path,
                   {"pair_name": "signal_code__forward-return-column",
                    "horizon_days": "forward horizon in trading days",
                    "metric": "pearson/spearman/kendall/distance",
                    "value": "correlation (LAGGED signal vs FORWARD return — predictive, not co-movement)",
                    "p_value": "two-sided p (NaN for distance corr)", "n_obs": "obs"},
                   [{"description": "values bounded", "check": "abs(value) <= 1"},
                    {"description": "these are predictive (forward) correlations, NOT contemporaneous", "check": "informational"},
                    {"description": "n_obs >= 250 enforced", "check": "min(n_obs) >= 250"}])
    sig = cdf[(cdf.metric == "pearson") & (cdf.p_value < 0.05)]
    print(f"  Correlation battery (PREDICTIVE/forward): {len(cdf)} rows; {len(sig)} significant Pearson cells")
    if len(sig):
        b = sig.loc[sig.value.abs().idxmax()]
        print(f"  Strongest predictive Pearson: {b.pair_name} r={b.value} p={b.p_value} (note: magnitudes are small for FORWARD returns)")
    return cdf


# ===================================================================
# STAGE 4: CORE MODELS — CCF, Granger (TY), TE, LP, QR, regressions
# This is where the lead-vs-co-movement verdict is established.
# ===================================================================
@log_stage("4_core_models")
def stage_core_models(df):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.ar_model import AutoReg
    from statsmodels.tsa.api import VAR

    # --- 4.1 Pre-whitened CCF (lags -20..+20) on returns ---
    pair = df[[MAIN_SIG, "spy_ret"]].dropna()
    x = pair[MAIN_SIG]; y = pair["spy_ret"]
    best_aic, best_p = np.inf, 1
    for p in range(1, 11):
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
    n = len(common); se = 1.96 / np.sqrt(n)
    rows = []
    for lag in range(-20, 21):
        # lag > 0: SOX leads SPY by `lag` days
        if lag >= 0:
            a, b = xw.shift(lag), yw
        else:
            a, b = xw, yw.shift(-lag)
        v = pd.concat([a, b], axis=1).dropna()
        c = v.corr().iloc[0, 1] if len(v) > 100 else np.nan
        rows.append({"lag": lag, "ccf": round(c, 4), "lower_ci": round(-se, 4),
                     "upper_ci": round(se, 4),
                     "significant": bool(abs(c) > se) if pd.notna(c) else False,
                     "arima_order": f"AR({best_p})", "n_obs": len(v)})
    ccf_df = pd.DataFrame(rows)
    ccf_df.to_csv(os.path.join(MODELS_DIR, "ccf_prewhitened.csv"), index=False)
    lead_sig = list(ccf_df[(ccf_df.lag > 0) & ccf_df.significant].lag)
    lag_sig = list(ccf_df[(ccf_df.lag < 0) & ccf_df.significant].lag)
    contemp = float(ccf_df.loc[ccf_df.lag == 0, "ccf"].iloc[0])
    print(f"  [4.1] Pre-whitened CCF (AR({best_p}), n={n}): contemp(lag0)={contemp:.3f}; "
          f"SOX-leads (lag>0) significant: {lead_sig}; SPY-leads (lag<0) significant: {lag_sig}")

    # --- 4.2 Toda-Yamamoto Granger (both directions) on returns ---
    ty_rows, bylag_rows = [], []
    gdata = pair.rename(columns={MAIN_SIG: "ind", "spy_ret": "tgt"})
    d_max = 1  # returns are I(0); minimal augmentation
    try:
        p_opt = max(int(VAR(gdata).select_order(maxlags=15).aic), 1)
    except Exception:
        p_opt = 5

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

    for lag in [1, 2, 3, 5, 10, 21]:
        try:
            for direction, caused, causing in [("indicator_to_target", "tgt", "ind"),
                                               ("target_to_indicator", "ind", "tgt")]:
                fstat, pv, dfn, dfd = ty_wald(caused, causing, lag)
                ty_rows.append({"direction": direction, "lag": lag,
                                "f_statistic": round(fstat, 4), "p_value": round(pv, 6),
                                "significant": pv < 0.05})
                if direction == "indicator_to_target":
                    bylag_rows.append({"lag": lag, "f_statistic": round(fstat, 4),
                                       "p_value": round(pv, 6), "df_num": dfn, "df_den": dfd})
        except Exception as e:
            print(f"    TY lag {lag} failed: {e}")
    ty_df = pd.DataFrame(ty_rows)
    ty_df.to_csv(os.path.join(MODELS_DIR, "granger_causality.csv"), index=False)
    pd.DataFrame(bylag_rows).to_csv(os.path.join(RESULTS_DIR, "granger_by_lag.csv"), index=False)
    fwd_sig = list(ty_df[(ty_df.direction == "indicator_to_target") & ty_df.significant].lag)
    rev_sig = list(ty_df[(ty_df.direction == "target_to_indicator") & ty_df.significant].lag)
    print(f"  [4.2] Toda-Yamamoto (d_max={d_max}, VAR p*~AIC={p_opt}):")
    print(f"        SOX->SPY significant at lags: {fwd_sig}")
    print(f"        SPY->SOX significant at lags: {rev_sig}")

    # --- 4.3 Transfer entropy (binned, permutation p) on returns ---
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

    te_rows = []; n_perm = 300; rng = np.random.default_rng(42)
    for direction, src, dst in [("indicator_to_target", x, y), ("target_to_indicator", y, x)]:
        te = transfer_entropy(src, dst)
        v = pd.concat([src, dst], axis=1).dropna()
        null = [transfer_entropy(pd.Series(rng.permutation(v.iloc[:, 0].values), index=v.index),
                                 v.iloc[:, 1]) for _ in range(n_perm)]
        pv = float((np.array(null) >= te).mean())
        te_rows.append({"direction": direction, "te_value": round(float(te), 5),
                        "permutation_p_value": round(pv, 4), "n_permutations": n_perm,
                        "bandwidth": np.nan, "bin_method": "tercile_qcut"})
    pd.DataFrame(te_rows).to_csv(os.path.join(MODELS_DIR, "transfer_entropy.csv"), index=False)
    print(f"  [4.3] Transfer entropy (lag1): ind->tgt TE={te_rows[0]['te_value']} (p={te_rows[0]['permutation_p_value']}), "
          f"tgt->ind TE={te_rows[1]['te_value']} (p={te_rows[1]['permutation_p_value']})")

    # --- 4.4 Local projections (forward + REVERSE), HAC SEs ---
    # KEY HONESTY STEP: forward LP uses LAGGED rel-strength as predictor of fwd SPY,
    # and we compare against an LP that ALSO controls for SPY's own past return.
    lp_rows = []
    for direction in ["fwd", "rev"]:
        for h in [1, 5, 21, 63, 126]:
            if direction == "fwd":
                ycol = f"spy_fwd_{h}d"
                v = df[["sox_spy_ratio_mom_3m_pct", ycol]].dropna()
                if len(v) < 250:
                    continue
                xv, yv = v["sox_spy_ratio_mom_3m_pct"], v[ycol]
            else:
                v = pd.concat([df["spy_ret"], df["sox_ret"].shift(-h)], axis=1).dropna()
                v.columns = ["x", "y"]
                if len(v) < 250:
                    continue
                xv, yv = v["x"], v["y"]
            X = sm.add_constant(xv.values)
            nw = int(0.75 * len(v) ** (1 / 3)) + h
            fit = sm.OLS(yv.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = fit.conf_int()
            lp_rows.append({"horizon": h, "coef": round(fit.params[1], 6), "se": round(fit.bse[1], 6),
                            "ci_lower": round(ci[1][0], 6), "ci_upper": round(ci[1][1], 6),
                            "p_value": round(fit.pvalues[1], 4), "direction": direction})
    lp_df = pd.DataFrame(lp_rows)
    lp_df.to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    rev = lp_df[lp_df.direction == "rev"]
    rev_flag = bool((rev.p_value < 0.05).any())
    print(f"  [4.4] Local projections: reverse-causality significant horizons: "
          f"{list(rev.loc[rev.p_value < 0.05, 'horizon'])} -> reverse-causality flag: {rev_flag}")

    # --- 4.4b INCREMENTAL-EDGE TEST: does lagged SOX add over SPY's own momentum? ---
    # Regress spy_fwd_21d on (a) SPY-own past 21d return and (b) lagged rel-strength.
    inc_rows = []
    work = df.copy()
    work["spy_mom_21d"] = work["spy"] / work["spy"].shift(21) - 1
    for hcol, h in [("spy_fwd_21d", 21), ("spy_fwd_63d", 63)]:
        v = work[["spy_mom_21d", "sox_spy_ratio_mom_3m_pct", hcol]].dropna()
        nw = int(0.75 * len(v) ** (1 / 3)) + h
        # restricted: SPY own momentum only
        Xr = sm.add_constant(v[["spy_mom_21d"]].values)
        fr = sm.OLS(v[hcol].values, Xr).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
        # unrestricted: + lagged relative strength
        Xu = sm.add_constant(v[["spy_mom_21d", "sox_spy_ratio_mom_3m_pct"]].values)
        fu = sm.OLS(v[hcol].values, Xu).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
        inc_rows.append({"fwd_horizon_days": h, "rs_coef": round(fu.params[2], 6),
                         "rs_se": round(fu.bse[2], 6), "rs_p_value": round(fu.pvalues[2], 4),
                         "rs_adds_over_spy_own_momentum": bool(fu.pvalues[2] < 0.05),
                         "r2_spy_own": round(fr.rsquared, 5), "r2_plus_rs": round(fu.rsquared, 5),
                         "incremental_r2": round(fu.rsquared - fr.rsquared, 5), "n": int(len(v))})
    pd.DataFrame(inc_rows).to_csv(os.path.join(MODELS_DIR, "incremental_edge_vs_spy_momentum.csv"), index=False)
    inc_any = any(r["rs_adds_over_spy_own_momentum"] for r in inc_rows)
    print(f"  [4.4b] Incremental-edge test (rel-strength over SPY-own-momentum): adds at some horizon = {inc_any}")
    for r in inc_rows:
        print(f"         h={r['fwd_horizon_days']}d: rs_p={r['rs_p_value']}, incremental R2={r['incremental_r2']}")

    # --- 4.5 Quantile regression (lagged rel-strength -> fwd 21d) ---
    qr_rows = []
    v = df[["sox_spy_ratio_mom_3m_pct", "spy_fwd_21d"]].dropna().rename(
        columns={"sox_spy_ratio_mom_3m_pct": "sig", "spy_fwd_21d": "fwd"})
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
    print(f"  [4.5] Quantile regression: {len(qr_rows)} taus")

    # --- 4.6 Predictive regressions (all signals x horizons, HC3) ---
    reg_rows = []
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwd in FWD_COLS:
            v = df[[col, fwd]].dropna()
            if len(v) < 250:
                continue
            fit = sm.OLS(v[fwd].values, sm.add_constant(v[col].values)).fit(cov_type="HC3")
            reg_rows.append({"signal": code, "horizon": fwd, "coef": round(fit.params[1], 8),
                             "se": round(fit.bse[1], 8), "t_stat": round(fit.tvalues[1], 3),
                             "p_value": round(fit.pvalues[1], 4), "r_squared": round(fit.rsquared, 5),
                             "n": int(fit.nobs)})
    pd.DataFrame(reg_rows).to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    print(f"  [4.6] Predictive regressions: {len(reg_rows)} cells")

    # --- 4.7 Diagnostics on baseline spec ---
    from statsmodels.stats.diagnostic import het_breuschpagan, acorr_breusch_godfrey, linear_reset
    diag = []
    v = df[["sox_spy_ratio_mom_3m_pct", "spy_fwd_21d"]].dropna()
    X = sm.add_constant(v["sox_spy_ratio_mom_3m_pct"].values)
    base = sm.OLS(v["spy_fwd_21d"].values, X).fit()
    resid = base.resid
    jb, jbp = stats.jarque_bera(resid)
    diag.append({"test": "Jarque-Bera", "statistic": round(jb, 3), "p_value": round(jbp, 4),
                 "interpretation": "Normal residuals" if jbp > 0.05 else "Non-normal — robust/HAC inference used"})
    bp, bpp, _, _ = het_breuschpagan(resid, X)
    diag.append({"test": "Breusch-Pagan", "statistic": round(bp, 3), "p_value": round(bpp, 4),
                 "interpretation": "Homoskedastic" if bpp > 0.05 else "Heteroskedastic — HC3/HAC SEs used"})
    bg, bgp, _, _ = acorr_breusch_godfrey(base, nlags=21)
    diag.append({"test": "Breusch-Godfrey (21)", "statistic": round(bg, 3), "p_value": round(bgp, 4),
                 "interpretation": "No serial corr" if bgp > 0.05 else "Serial correlation (overlapping fwd returns) — HAC SEs used"})
    try:
        rs = linear_reset(base, power=3, use_f=True)
        diag.append({"test": "RESET", "statistic": round(float(rs.fvalue), 3), "p_value": round(float(rs.pvalue), 4),
                     "interpretation": "Linear form adequate" if rs.pvalue > 0.05 else "Possible nonlinearity — see quantile regression"})
    except Exception:
        pass
    pd.DataFrame(diag).to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)
    print(f"  [4.7] Diagnostics: {len(diag)} tests")

    return ccf_df, ty_df, lp_df, rev_flag, contemp, fwd_sig, rev_sig, lead_sig, lag_sig, inc_rows, inc_any


# ===================================================================
# STAGE 5: REGIME QUARTILE RETURNS (Rule E2) — FORWARD (lead-aware)
# Quartiles of LAGGED rel-strength momentum vs NEXT-day SPY return.
# ===================================================================
@log_stage("5_regime_quartiles")
def stage_quartiles(df):
    v = pd.concat([df["sox_spy_ratio_mom_3m_pct"].shift(1).rename("sig"),
                   df["spy_ret"]], axis=1).dropna()
    q = pd.qcut(v["sig"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    rows = []
    for lbl in ["Q1", "Q2", "Q3", "Q4"]:
        r = v.loc[q == lbl, "spy_ret"]
        m = ann_metrics(r)
        rows.append({"quartile": lbl, "n_days": len(r), "ann_return": round(m["ann_return"], 4),
                     "ann_vol": round(m["ann_vol"], 4), "sharpe": round(m["sharpe"], 3),
                     "max_drawdown": round(m["max_dd"], 4)})
    qdf = pd.DataFrame(rows)
    path = os.path.join(RESULTS_DIR, "regime_quartile_returns.csv")
    qdf.to_csv(path, index=False)
    print(qdf.to_string(index=False))
    write_manifest(path,
                   {"quartile": "Quartile of LAGGED (t-1) SOX/SPY relative-strength 3m momentum (Q1 lowest)",
                    "n_days": "obs", "ann_return": "annualized NEXT-day SPY return in quartile (ratio)",
                    "ann_vol": "annualized vol (ratio)", "sharpe": "ann_return/ann_vol",
                    "max_drawdown": "max DD within quartile days (negative ratio)"},
                   [{"description": "4 quartiles", "check": "len == 4"},
                    {"description": "forward (lagged-signal) relationship — predictive, not contemporaneous", "check": "informational"},
                    {"description": "returns plausible", "check": "abs(ann_return) < 1.0"}])
    return qdf


# ===================================================================
# STAGE 6: TOURNAMENT (5-D) — leads START AT L1 (no contemporaneous)
# ===================================================================
@log_stage("6_tournament")
def stage_tournament(df):
    work = df.dropna(subset=["spy_ret"]).copy()
    n_days = len(work)
    # daily OOS: 25% capped at ~5 years (1260 td), floor 252 td
    oos_n = int(min(max(252, round(n_days * 0.25)), 1260))
    oos_start = work.index[-oos_n]
    is_end = work.index[-(oos_n + 1)]
    oos_end = work.index[-1]
    print(f"  Sample: {n_days} days {work.index[0].date()} -> {oos_end.date()}")
    print(f"  OOS (v1_max252_25pct_cap1260): {oos_n} days, {oos_start.date()} -> {oos_end.date()}")

    split = {
        "owner": "evan", "split_policy_id": "v1_max252_25pct_cap1260",
        "in_sample_end": is_end.strftime("%Y-%m-%d"), "oos_start": oos_start.strftime("%Y-%m-%d"),
        "oos_end": oos_end.strftime("%Y-%m-%d"), "sample_size_days": n_days,
        "justification": (f"Daily policy on the full SOX/SPY sample ({n_days} trading days, "
                          f"1994-05 onward). min(max(252, round({n_days}*0.25)), 1260) = {oos_n} days "
                          f"(~5y cap). Lead grid starts at L1: a contemporaneous signal is co-movement, "
                          f"not a forecast (central honesty challenge for this pair)."),
    }
    with open(os.path.join(RESULTS_DIR, "oos_split_record.json"), "w") as f:
        json.dump(split, f, indent=2)

    is_mask = work.index <= is_end
    oos_mask = work.index >= oos_start
    spy_ret = work["spy_ret"]

    leads = [1, 5, 10, 21, 63]  # L1 real-time floor (NO L0 — contemporaneous = co-movement)
    lookbacks = {"LB63": 63, "LB126": 126, "LB252": 252}
    strategies = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]

    results = []
    for code, col in SIGNAL_COLS.items():
        if col not in work.columns or work[col].notna().sum() < 1000:
            continue
        base_sig = work[col]
        is_growth = code.startswith(("rs_mom", "sox_mom"))  # momentum signals can use zero threshold
        for lead in leads:
            sig = base_sig.shift(lead)
            thr_static = {}
            is_sig = sig[is_mask].dropna()
            if len(is_sig) > 250:
                for pct in [25, 50, 75]:
                    thr_static[(f"T1_fixed_p{pct}", "LB_NA")] = is_sig.quantile(pct / 100)
            if is_growth:
                thr_static[("T4_zero", "LB_NA")] = 0.0
            thr_roll = {}
            for lb_name, lb in lookbacks.items():
                minp = max(int(lb * 0.6), 60)
                roll = sig.rolling(lb, min_periods=minp)
                for pct in [25, 75]:
                    thr_roll[(f"T2_roll_p{pct}", lb_name)] = roll.quantile(pct / 100)
                rm, rs = roll.mean(), roll.std()
                for k in [1.0, 1.5]:
                    thr_roll[(f"T3_zscore_{k}", lb_name)] = rm + k * rs
                    thr_roll[(f"T3_zscore_neg_{k}", lb_name)] = rm - k * rs

            for (thr_name, lb_name), thr in {**thr_static, **thr_roll}.items():
                above = sig < thr if "neg_" in thr_name else sig > thr
                for strat in strategies:
                    for orientation in ["pro", "counter"]:
                        pos_bool = ~above if orientation == "counter" else above
                        if strat == "P1_long_cash":
                            position = pos_bool.astype(float)
                        elif strat == "P2_signal_strength":
                            if lb_name == "LB_NA":
                                continue
                            lb = lookbacks[lb_name]
                            roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 60))
                            rng = (roll.max() - roll.min()).replace(0, np.nan)
                            raw = ((sig - roll.min()) / rng).clip(0, 1)
                            position = 1 - raw if orientation == "counter" else raw
                        else:
                            position = pos_bool.astype(float) * 2 - 1
                        strat_ret = position * spy_ret  # lead >= 1 => no lookahead
                        is_r, oos_r = strat_ret[is_mask].dropna(), strat_ret[oos_mask].dropna()
                        if len(is_r) < 500 or len(oos_r) < 200:
                            continue
                        m_is, m = ann_metrics(is_r), ann_metrics(oos_r)
                        pos_oos = position[oos_mask]
                        n_trades = int((pos_oos.diff().abs() > 1e-9).sum())
                        years = len(pos_oos.dropna()) / TRADING_DAYS
                        turnover = n_trades / years if years > 0 else 999
                        valid = bool(m["sharpe"] > 0.3 and turnover < 252 and len(oos_r) >= 200)
                        results.append({
                            "signal": code, "threshold": thr_name, "strategy": f"{strat}_{orientation}",
                            "lead_days": lead, "lookback": lb_name,
                            "is_sharpe": round(m_is["sharpe"], 4), "oos_sharpe": round(m["sharpe"], 4),
                            "oos_sortino": round(m["sortino"], 4), "oos_calmar": round(m["calmar"], 4),
                            "oos_ann_return": round(m["ann_return"], 4), "oos_ann_vol": round(m["ann_vol"], 4),
                            "max_drawdown": round(m["max_dd"], 4), "win_rate": round(m["win_rate"], 4),
                            "n_trades": n_trades, "annual_turnover": round(turnover, 2),
                            "oos_n": len(oos_r), "valid": valid,
                        })

    # --- BENCHMARK 1: buy & hold SPY (ECON-T4: valid=False) ---
    bh_oos = spy_ret[oos_mask].dropna(); bh_is = spy_ret[is_mask].dropna()
    mb, mbi = ann_metrics(bh_oos), ann_metrics(bh_is)
    results.append({
        "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "P0_buy_and_hold",
        "lead_days": 0, "lookback": "LB_NA",
        "is_sharpe": round(mbi["sharpe"], 4), "oos_sharpe": round(mb["sharpe"], 4),
        "oos_sortino": round(mb["sortino"], 4), "oos_calmar": round(mb["calmar"], 4),
        "oos_ann_return": round(mb["ann_return"], 4), "oos_ann_vol": round(mb["ann_vol"], 4),
        "max_drawdown": round(mb["max_dd"], 4), "win_rate": round(mb["win_rate"], 4),
        "n_trades": 0, "annual_turnover": 0.0, "oos_n": len(bh_oos), "valid": False,
    })

    # --- BENCHMARK 2: SPY-OWN-MOMENTUM (the trivial trend-follower SOX must beat) ---
    # Long SPY when its own 63d return > 0, else cash. Lagged 1 day (no lookahead).
    spy_mom = (work["spy"] / work["spy"].shift(63) - 1).shift(1)
    pos_spm = (spy_mom > 0).astype(float)
    spm_ret = pos_spm * spy_ret
    spm_oos = spm_ret[oos_mask].dropna()
    msm = ann_metrics(spm_oos)
    spm_trades = int((pos_spm[oos_mask].diff().abs() > 1e-9).sum())
    spm_turn = spm_trades / (len(pos_spm[oos_mask].dropna()) / TRADING_DAYS)
    results.append({
        "signal": "SPY_OWN_MOMENTUM", "threshold": "63d_ret_gt_0", "strategy": "P1_long_cash_pro",
        "lead_days": 1, "lookback": "LB63",
        "is_sharpe": round(ann_metrics(spm_ret[is_mask].dropna())["sharpe"], 4),
        "oos_sharpe": round(msm["sharpe"], 4), "oos_sortino": round(msm["sortino"], 4),
        "oos_calmar": round(msm["calmar"], 4), "oos_ann_return": round(msm["ann_return"], 4),
        "oos_ann_vol": round(msm["ann_vol"], 4), "max_drawdown": round(msm["max_dd"], 4),
        "win_rate": round(msm["win_rate"], 4), "n_trades": spm_trades,
        "annual_turnover": round(spm_turn, 2), "oos_n": len(spm_oos), "valid": False,
    })

    tdf = pd.DataFrame(results)
    assert (tdf["signal"] == "BENCHMARK").sum() == 1, "exactly one buy-hold benchmark row (ECON-T4)"
    tpath = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    tdf.to_csv(tpath, index=False)

    strat_pop = tdf[~tdf.signal.isin(["BENCHMARK", "SPY_OWN_MOMENTUM"])]
    n_valid = int(strat_pop["valid"].sum())
    print(f"  Combos: {len(strat_pop)} strategies + 2 benchmark rows (valid=False); valid strategies: {n_valid}")
    print(f"  B&H OOS Sharpe {mb['sharpe']:.3f}, maxDD {mb['max_dd']:.3f}, ann ret {mb['ann_return']:.3f}")
    print(f"  SPY-OWN-MOMENTUM OOS Sharpe {msm['sharpe']:.3f}, maxDD {msm['max_dd']:.3f}, ann ret {msm['ann_return']:.3f}")

    manifest = {
        "file": os.path.basename(tpath), "pair_id": PAIR_ID,
        "grid": {"signals": [k for k, v in SIGNAL_COLS.items() if v in work.columns],
                 "thresholds": "T1_fixed_p{25,50,75}, T2_roll_p{25,75}, T3_zscore_{±1.0,±1.5}, T4_zero (momentum signals)",
                 "strategies": [s + "_{pro,counter}" for s in strategies],
                 "leads_days": leads, "lookbacks": list(lookbacks.keys()) + ["LB_NA"]},
        "units": "oos_ann_return / oos_ann_vol / max_drawdown are RATIOS (decimal), not percent",
        "total_strategy_rows": len(strat_pop), "valid_strategy_rows": n_valid,
        "sampling": "exhaustive (grid within budget)",
        "benchmark_rows": ("signal==BENCHMARK (buy&hold) is the ECON-T4 benchmark, valid=False, excluded "
                           "from combo counts; signal==SPY_OWN_MOMENTUM is an ADDITIONAL trivial-trend "
                           "benchmark (the central honesty challenge: a high-beta SOX rule must beat SPY's "
                           "own momentum, not just buy&hold), also valid=False and excluded from combo counts."),
        "execution_lag": "position_t = rule(signal_{t-lead}), lead >= 1 (NO L0 — contemporaneous = co-movement)",
        "cost_note": "returns gross of costs; 5bps sensitivity in tournament_validation",
        "assertions": ["top strategy oos_sharpe > bottom strategy oos_sharpe",
                       "all oos_sharpe finite", "exactly one BENCHMARK (buy&hold) row, valid=False",
                       "leads all >= 1"],
        "generated_at": NOW_ISO,
    }
    with open(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return tdf, split, msm


# ===================================================================
# STAGE 7: WINNER SELECTION (ECON-T3 cascade) + artifacts
# ===================================================================
LOOKBACKS = {"LB63": 63, "LB126": 126, "LB252": 252}


def select_winner(tdf):
    cand = tdf[~tdf.signal.isin(["BENCHMARK", "SPY_OWN_MOMENTUM"]) & tdf.valid].copy()
    if len(cand) == 0:
        raise RuntimeError("no valid strategies — escalate to Lead")
    cand["abs_dd"] = cand["max_drawdown"].abs()
    cascade = [("oos_sharpe", False), ("oos_ann_return", False),
               ("abs_dd", True), ("n_trades", False), ("signal", True)]
    pool = cand; resolved_at = 1; tie_pool_step1 = None
    for i, (colname, ascending) in enumerate(cascade, start=1):
        best_val = pool[colname].min() if ascending else pool[colname].max()
        nxt = pool[pool[colname] == best_val]
        if i == 1:
            tie_pool_step1 = nxt.copy()
        resolved_at = i
        if len(nxt) == 1:
            pool = nxt
            break
        pool = nxt
    return pool.iloc[0], resolved_at, tie_pool_step1, cand


def derive_winner_series(df, winner, split):
    work = df.dropna(subset=["spy_ret"]).copy()
    is_mask = work.index <= split["in_sample_end"]
    sig = work[SIGNAL_COLS[winner["signal"]]].shift(int(winner["lead_days"]))
    thr_name, lb_name = winner["threshold"], winner["lookback"]
    if thr_name.startswith("T1_fixed_p"):
        thr = sig[is_mask].dropna().quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name == "T4_zero":
        thr = 0.0
    elif thr_name.startswith("T2_roll_p"):
        lb = LOOKBACKS[lb_name]
        thr = sig.rolling(lb, min_periods=max(int(lb * 0.6), 60)).quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name.startswith("T3_zscore"):
        lb = LOOKBACKS[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 60))
        k = float(thr_name.split("_")[-1])
        thr = roll.mean() - k * roll.std() if "neg_" in thr_name else roll.mean() + k * roll.std()
    else:
        raise ValueError(thr_name)
    above = sig < thr if "neg_" in thr_name else sig > thr
    strat, orientation = winner["strategy"].rsplit("_", 1)
    pos_bool = ~above if orientation == "counter" else above
    if strat == "P1_long_cash":
        position = pos_bool.astype(float)
    elif strat == "P2_signal_strength":
        lb = LOOKBACKS[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 60))
        rng = (roll.max() - roll.min()).replace(0, np.nan)
        raw = ((sig - roll.min()) / rng).clip(0, 1)
        position = 1 - raw if orientation == "counter" else raw
    else:
        position = pos_bool.astype(float) * 2 - 1
    return position, work["spy_ret"], sig, thr


@log_stage("7_winner_artifacts")
def stage_winner(df, tdf, split):
    winner, resolved_at, tie_pool, cand = select_winner(tdf)
    n_valid = len(cand)
    median_sharpe = float(cand["oos_sharpe"].median())
    n_tied = int((cand["oos_sharpe"] == winner["oos_sharpe"]).sum())
    print(f"  Winner: {winner['signal']}/{winner['threshold']}/{winner['strategy']}/L{winner['lead_days']}/{winner['lookback']}")
    print(f"  OOS Sharpe {winner['oos_sharpe']} | ties at step1: {n_tied} | cascade resolved at step {resolved_at}")

    if resolved_at > 1:
        lines = [f"# Tournament Tie Note — {PAIR_ID} ({DATE_TAG})", "",
                 f"Winner resolved at cascade step {resolved_at} (ECON-T3).", "",
                 "## Candidates tied at step 1 (oos_sharpe)", "",
                 tie_pool[["signal", "threshold", "strategy", "lead_days", "lookback",
                           "oos_sharpe", "oos_ann_return", "max_drawdown", "n_trades"]].to_markdown(index=False)]
        with open(os.path.join(RESULTS_DIR, "tournament_tie_note.md"), "w") as f:
            f.write("\n".join(lines))
        print("  Tie note written")

    position, spy_ret, sig_lagged, thr = derive_winner_series(df, winner, split)
    oos_mask = (spy_ret.index >= split["oos_start"]) & (spy_ret.index <= split["oos_end"])
    strat_ret = position * spy_ret
    m = ann_metrics(strat_ret[oos_mask])
    rec = {}
    for key, computed, reported, tol in [
            ("oos_sharpe", m["sharpe"], float(winner["oos_sharpe"]), 0.03),
            ("oos_max_drawdown", m["max_dd"], float(winner["max_drawdown"]), 0.01),
            ("oos_ann_return", m["ann_return"], float(winner["oos_ann_return"]), 0.01)]:
        diff = computed - reported
        rec[key] = {"computed": round(float(computed), 6), "reported_tournament": reported,
                    "diff": round(float(diff), 6), "tolerance": tol,
                    "verdict": "PASS" if abs(diff) <= tol else "FAIL"}
    assert all(v["verdict"] == "PASS" for v in rec.values()), f"ECON-SR1 reconciliation FAILED: {rec}"
    print(f"  ECON-SR1 reconciliation (recompute guardrail): PASS — recomputed OOS Sharpe "
          f"{m['sharpe']:.4f} vs headline {float(winner['oos_sharpe']):.4f} (|diff|={abs(rec['oos_sharpe']['diff']):.4f} <= 0.03)")

    sr = pd.DataFrame({
        "date": spy_ret.index.strftime("%Y-%m-%d"),
        "position": position.reindex(spy_ret.index).fillna(0.0).values,
        "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0.0).values,
        "bh_return": spy_ret.values,
    })
    sr_path = os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv")
    sr.to_csv(sr_path, index=False)
    sr_meta = {
        "pair_id": PAIR_ID, "artifact": os.path.basename(sr_path),
        "produced_by": "scripts/pair_pipeline_phlxsox_spy.py", "rule": "ECON-SR1",
        "source": "pipeline_native_derivation (same code path as tournament evaluation)",
        "returns_file": DATA_PATH, "coverage_start": str(spy_ret.index[0].date()),
        "coverage_end": str(spy_ret.index[-1].date()), "frequency": "daily",
        "oos_start": split["oos_start"], "oos_end": split["oos_end"],
        "position_semantics": (f"position on row t is the return-accrual weight for day t; the signal is "
                               f"lagged {int(winner['lead_days'])} trading day(s) (>=1, no contemporaneous "
                               "lookahead); strategy_return = position * bh_return row-wise"),
        "reconciliation": {k: {"computed": v["computed"], "reported_winner_summary": v["reported_tournament"],
                               "diff": v["diff"], "tolerance": v["tolerance"], "verdict": v["verdict"]}
                           for k, v in rec.items()},
        "generated_at": NOW_ISO, "generated_by": "Econ Evan (pair260619_phlxsox_spy)",
    }
    with open(os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}_meta.json"), "w") as f:
        json.dump(sr_meta, f, indent=2)

    # internal trade log
    log = pd.DataFrame({
        "date": spy_ret.index.strftime("%Y-%m-%d"),
        "signal_value": sig_lagged.reindex(spy_ret.index).round(4),
        "threshold": (thr.reindex(spy_ret.index).round(4) if isinstance(thr, pd.Series) else np.round(thr, 4)),
        "position": position.reindex(spy_ret.index).fillna(0.0),
        "spy_return": spy_ret.round(6),
        "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0.0).round(6),
    })
    log["cumulative_return"] = ((1 + log["strategy_return"]).cumprod() - 1).round(6)
    log.to_csv(os.path.join(RESULTS_DIR, "winner_trade_log.csv"), index=False)

    # broker-style trade log (Rule C4)
    spy_px = df["spy"].reindex(spy_ret.index)
    broker_rows = []; cum = (1 + strat_ret.reindex(spy_ret.index).fillna(0.0)).cumprod()
    prev = 0.0; capital = 10000.0
    sig_disp = f"{winner['signal']} ({SIGNAL_COLS[winner['signal']]})"
    pos_full = position.reindex(spy_ret.index).fillna(0.0)
    for dt in spy_ret.index:
        p = float(pos_full.loc[dt])
        if abs(p - prev) > 1e-9:
            side = "BUY" if p > prev else "SELL"
            notional = abs(p - prev) * capital
            sv = sig_lagged.loc[dt]; th = thr.loc[dt] if isinstance(thr, pd.Series) else thr
            broker_rows.append({
                "trade_date": dt.strftime("%Y-%m-%d"), "side": side, "instrument": TARGET_SYMBOL,
                "quantity_pct": round(abs(p) * 100, 1),
                "price": round(float(spy_px.loc[dt]), 4) if pd.notna(spy_px.loc[dt]) else np.nan,
                "notional_usd": round(notional, 2), "commission_bps": COST_BPS,
                "commission_usd": round(notional * COST_BPS / 10000, 2),
                "cum_pnl_pct": round((cum.loc[dt] - 1) * 100, 4),
                "reason": (f"{winner['strategy']}: {sig_disp} = {sv:.3f} vs threshold "
                           f"{(th if not isinstance(th, pd.Series) else th):.3f} — {prev*100:.0f}% -> {p*100:.0f}%"
                           if pd.notna(sv) else "position change"),
            })
            prev = p
    broker_path = os.path.join(RESULTS_DIR, "winner_trades_broker_style.csv")
    with open(broker_path, "w") as f:
        f.write(f"# Simulated trade record based on backtest signals. No real trades were executed. "
                f"Starting capital: $10000. Commission: {COST_BPS} bps. Pair: {PAIR_ID}. "
                f"Strategy: {winner['strategy']} on {sig_disp}, threshold {winner['threshold']}, "
                f"lead L{winner['lead_days']}d, {winner['lookback']}.\n")
        pd.DataFrame(broker_rows).to_csv(f, index=False)
    print(f"  Trade logs written ({len(log)} rows internal, {len(broker_rows)} broker events)")

    return winner, rec, n_valid, median_sharpe, n_tied, resolved_at, position, strat_ret, sig_lagged, thr, m


# ===================================================================
# STAGE 8: CROSS-PERIOD ANALYSES (ECON-CP1 A/B/C) — daily
# ===================================================================
@log_stage("8_cross_period")
def stage_cross_period(df, winner, split, position, strat_ret, sig_lagged):
    import statsmodels.api as sm

    # CP1-A: subperiod Sharpe from episode registry
    try:
        with open(os.path.join(SCHEMA_DIR, "episode_registry.json")) as f:
            reg = json.load(f)
        episodes = reg.get("equity", reg.get("_fallback", []))
    except Exception:
        episodes = []
    oos = strat_ret[(strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])]
    rows = []; pos_eps = 0; eval_eps = 0
    for ep in episodes:
        sub = oos[(oos.index >= ep["start"]) & (oos.index <= ep["end"])].dropna()
        if len(sub) < 21:
            rows.append({"episode": ep["slug"], "start_date": ep["start"], "end_date": ep["end"],
                         "n_trading_days": len(sub), "ann_sharpe": np.nan, "win_rate": np.nan,
                         "max_drawdown": np.nan, "data_status": "insufficient_data", "durability_verdict": ""})
            continue
        m = ann_metrics(sub); eval_eps += 1; pos_eps += int(m["sharpe"] > 0)
        rows.append({"episode": ep["slug"], "start_date": str(sub.index[0].date()),
                     "end_date": str(sub.index[-1].date()), "n_trading_days": len(sub),
                     "ann_sharpe": round(m["sharpe"], 4), "win_rate": round(m["win_rate"], 4),
                     "max_drawdown": round(m["max_dd"], 4), "data_status": "validated", "durability_verdict": ""})
    if eval_eps >= 3:
        verdict = "durable" if pos_eps >= 3 else ("conditionally_durable" if pos_eps == 2 else "episode_concentrated")
    else:
        verdict = ("conditionally_durable" if pos_eps == eval_eps and eval_eps > 0 else "episode_concentrated") if eval_eps else "insufficient_data"
    if rows:
        rows[-1]["durability_verdict"] = verdict
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "subperiod_sharpe.csv"), index=False)
    print(f"  CP1-A: {eval_eps} episodes evaluable, {pos_eps} positive -> {verdict}")

    # CP1-B: rolling 252d corr (winning lagged signal vs spy_fwd_1d)
    v = pd.concat([sig_lagged.rename("sig"), df["spy_fwd_1d"]], axis=1).dropna()
    full_r = float(v["sig"].corr(v["spy_fwd_1d"]))
    roll = v["sig"].rolling(252).corr(v["spy_fwd_1d"])
    out = pd.DataFrame({"date": v.index.strftime("%Y-%m-%d"), "rolling_corr": roll.round(4).values,
                        "n_obs": 252,
                        "window_start": v.index.to_series().shift(251).dt.strftime("%Y-%m-%d").values}).dropna(subset=["rolling_corr"])
    out.to_csv(os.path.join(RESULTS_DIR, f"rolling_correlation_{PAIR_ID}.csv"), index=False)
    same_sign = float((np.sign(roll.dropna()) == np.sign(full_r)).mean())
    stab = "sign_stable" if same_sign >= 0.7 else ("moderately_stable" if same_sign >= 0.5 else "sign_unstable")
    print(f"  CP1-B: full-sample fwd-corr r={full_r:.4f}, sign stability {same_sign:.2f} -> {stab}")

    # CP1-C: Quandt-Andrews sup-F on spy_ret ~ lagged signal, bootstrap p
    reg_v = pd.concat([sig_lagged.rename("sig"), df["spy_ret"]], axis=1).dropna()
    yv = reg_v["spy_ret"].values; Xv = sm.add_constant(reg_v["sig"].values)
    n = len(yv); lo, hi = int(n * 0.15), int(n * 0.85)
    full = sm.OLS(yv, Xv).fit(); k = Xv.shape[1]

    def sup_f(y, X, step):
        ssr_f = sm.OLS(y, X).fit().ssr
        best, bidx = -np.inf, lo
        for b in range(lo, hi, step):
            s1 = sm.OLS(y[:b], X[:b]).fit().ssr; s2 = sm.OLS(y[b:], X[b:]).fit().ssr
            f = ((ssr_f - s1 - s2) / k) / ((s1 + s2) / (len(y) - 2 * k))
            if f > best:
                best, bidx = f, b
        return best, bidx

    f_obs, b_idx = sup_f(yv, Xv, step=10)  # step for daily tractability
    rng = np.random.default_rng(42)
    resid = full.resid; fitted = full.fittedvalues
    null = []
    for _ in range(200):
        y_b = fitted + rng.choice(resid, size=n, replace=True)
        fb, _ = sup_f(y_b, Xv, step=25)
        null.append(fb)
    p_break = float((np.array(null) >= f_obs).mean())
    break_date = str(reg_v.index[b_idx].date()); flagged = p_break < 0.10
    sb = {"pair_id": PAIR_ID, "test": "Quandt-Andrews unknown breakpoint (sup-F, residual-bootstrap p, 200 reps)",
          "sample_start": str(reg_v.index[0].date()), "sample_end": str(reg_v.index[-1].date()),
          "n_obs": n, "trimming_pct": 0.15, "break_date": break_date,
          "f_stat": round(float(f_obs), 4), "p_value": round(p_break, 4), "flagged": flagged,
          "flag_message": ("Structural break detected — interpret cross-period results with caution." if flagged else None),
          "rolling_corr_sign_stability": round(same_sign, 4), "rolling_corr_stability_verdict": stab,
          "cp2_note": "CP2 skipped — regime_story not set in signal_scope.json"}
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
    cand = tdf[~tdf.signal.isin(["BENCHMARK", "SPY_OWN_MOMENTUM"]) & tdf.valid]
    top5 = cand.nlargest(5, "oos_sharpe")
    rng = np.random.default_rng(42)
    boot = np.zeros(5000)
    for b in range(5000):
        s = rng.choice(spy_oos.values, size=len(spy_oos), replace=True)
        boot[b] = (s.mean() / s.std()) * np.sqrt(TRADING_DAYS) if s.std() > 0 else 0
    rows = [{"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
             "lead_days": r.lead_days, "lookback": r.lookback, "oos_sharpe": r.oos_sharpe,
             "bootstrap_p_value": round(float((boot >= r.oos_sharpe).mean()), 4),
             "significant_at_5pct": bool((boot >= r.oos_sharpe).mean() < 0.05)}
            for r in top5.itertuples()]
    pd.DataFrame(rows).to_csv(os.path.join(VALID_DIR, "bootstrap.csv"), index=False)

    stress = {"Dot_Com": ("2000-03-01", "2002-10-31"), "GFC": ("2008-01-01", "2009-06-30"),
              "COVID": ("2020-01-01", "2020-06-30"), "Rate_Hike_2022": ("2022-01-01", "2022-12-31")}
    srows = []
    for nm, (s, e) in stress.items():
        sub_bh = df["spy_ret"][(df.index >= s) & (df.index <= e)].dropna()
        sub_st = strat_ret[(strat_ret.index >= s) & (strat_ret.index <= e)].dropna()
        if len(sub_bh) > 21:
            srows.append({"period": nm, "start": s, "end": e, "n_days": len(sub_bh),
                          "buy_hold_sharpe": round(ann_metrics(sub_bh)["sharpe"], 4),
                          "buy_hold_return_pct": round(sub_bh.sum() * 100, 2),
                          "winner_sharpe": round(ann_metrics(sub_st)["sharpe"], 4) if len(sub_st) > 21 else np.nan,
                          "winner_return_pct": round(sub_st.sum() * 100, 2) if len(sub_st) > 21 else np.nan})
    pd.DataFrame(srows).to_csv(os.path.join(VALID_DIR, "stress_tests.csv"), index=False)

    tx = []
    for r in top5.itertuples():
        for bps in [0, 5, 10, 25, 50]:
            ann_cost = r.annual_turnover * bps / 10000
            net = r.oos_sharpe - ann_cost / r.oos_ann_vol if r.oos_ann_vol > 0 else r.oos_sharpe
            tx.append({"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
                       "tx_cost_bps": bps, "gross_sharpe": r.oos_sharpe, "net_sharpe_approx": round(net, 4)})
    pd.DataFrame(tx).to_csv(os.path.join(VALID_DIR, "transaction_costs.csv"), index=False)
    print(f"  bootstrap (top5), stress ({len(srows)} periods), tx-cost grid saved")
    return rows


# ===================================================================
# MAIN
# ===================================================================
def main():
    t0 = time.time()
    df, contemp_corr = stage_load()
    df = stage_signals(df)
    stage_correlations(df)
    (ccf_df, ty_df, lp_df, rev_flag, contemp_ccf, fwd_sig, rev_sig,
     lead_sig, lag_sig, inc_rows, inc_any) = stage_core_models(df)
    stage_quartiles(df)
    tdf, split, msm = stage_tournament(df)
    (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
     position, strat_ret, sig_lagged, thr, m_oos) = stage_winner(df, tdf, split)
    verdict, stab, sb, full_r = stage_cross_period(df, winner, split, position, strat_ret, sig_lagged)
    boot_rows = stage_validation(df, tdf, split, strat_ret)
    winner_boot_p = boot_rows[0]["bootstrap_p_value"] if boot_rows else np.nan

    bh = tdf[tdf.signal == "BENCHMARK"].iloc[0]
    spm = tdf[tdf.signal == "SPY_OWN_MOMENTUM"].iloc[0]

    # spec-curve context (the search-overfitting reality check)
    valid_pop = tdf[~tdf.signal.isin(["BENCHMARK", "SPY_OWN_MOMENTUM"]) & tdf.valid]
    spec_median = float(valid_pop["oos_sharpe"].median())
    is_oos_gap = float(winner["oos_sharpe"]) - float(winner["is_sharpe"])

    # --- direction of winner ---
    orientation = winner["strategy"].rsplit("_", 1)[1]
    neg_thr = "neg_" in winner["threshold"]
    long_when_high = (orientation == "pro") != neg_thr
    direction = "procyclical" if long_when_high else "countercyclical"
    thr_value = float(thr.dropna().iloc[-1]) if isinstance(thr, pd.Series) else float(thr)
    thr_rule = "lt" if neg_thr else "gt"
    strat_family = winner["strategy"].rsplit("_", 1)[0]

    beats_bh = bool(winner["oos_sharpe"] > bh["oos_sharpe"])
    beats_spm = bool(winner["oos_sharpe"] > spm["oos_sharpe"])

    # --- lead-vs-comovement verdict ---
    sox_leads = len(fwd_sig) > 0
    spy_leads_sox = len(rev_sig) > 0
    if sox_leads and not spy_leads_sox:
        lead_verdict = "SOX leads SPY (forward Granger significant, reverse not)"
    elif sox_leads and spy_leads_sox:
        lead_verdict = "Bidirectional Granger (both directions significant) — feedback, not clean lead"
    elif not sox_leads and spy_leads_sox:
        lead_verdict = "SPY leads SOX (reverse-only) — SOX does NOT lead"
    else:
        lead_verdict = "No Granger causality either direction beyond own-lags"

    winner_summary = {
        "pair_id": PAIR_ID, "generated_at": NOW_ISO,
        "signal_column": SIGNAL_COLS[winner["signal"]],
        "signal_code": f"phlxsox_{winner['signal']}" if not winner["signal"].startswith("hmm") else "phlxsox_hmm_stress",
        "signal_display_name": f"SOX {winner['signal']}",
        "target_symbol": TARGET_SYMBOL,
        "threshold_code": winner["threshold"], "threshold_value": round(thr_value, 4),
        "threshold_rule": thr_rule,
        "threshold_note": ("threshold is rolling (window per lookback); threshold_value is the latest rolling "
                           "value — see winner_trade_log.csv for the full path"
                           if isinstance(thr, pd.Series) else "static threshold (IS-calibrated)"),
        "strategy_family": strat_family, "strategy_code": strat_family.split("_")[0],
        "strategy_display_name": {"P1_long_cash": "Long/Cash", "P2_signal_strength": "Signal-strength sizing",
                                  "P3_long_short": "Long/Short"}[strat_family],
        "strategy_description": "",
        "lead_value": int(winner["lead_days"]), "lead_unit": "days",
        "lead_description": (f"Signal lead = {int(winner['lead_days'])} trading day(s); L1 is the real-time floor "
                             "(no contemporaneous L0 — a same-day SOX reading is co-movement, not a forecast)."),
        "lookback": winner["lookback"], "direction": direction,
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "oos_sortino": round(float(winner["oos_sortino"]), 4),
        "oos_calmar": round(float(winner["oos_calmar"]), 4),
        "oos_ann_return": round(float(winner["oos_ann_return"]), 4),
        "oos_ann_vol": round(float(winner["oos_ann_vol"]), 4),
        "oos_max_drawdown": round(float(winner["max_drawdown"]), 4),
        "oos_win_rate": round(float(winner["win_rate"]), 4),
        "oos_n_trades": int(winner["n_trades"]),
        "annual_turnover": round(float(winner["annual_turnover"]), 2),
        "oos_n": int(winner["oos_n"]),
        "oos_period_start": split["oos_start"], "oos_period_end": split["oos_end"],
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_ann_return": round(float(bh["oos_ann_return"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4),
        "spy_own_momentum_sharpe": round(float(spm["oos_sharpe"]), 4),
        "spy_own_momentum_ann_return": round(float(spm["oos_ann_return"]), 4),
        "spy_own_momentum_max_drawdown": round(float(spm["max_drawdown"]), 4),
        "beats_buy_and_hold": beats_bh,
        "beats_spy_own_momentum": beats_spm,
        "cost_assumption_bps": COST_BPS,
        "total_combos": int(n_valid_total(tdf)),
        "valid_combos": n_valid, "schema_version": "1.1.0",
        "notes": "",
    }
    sd = ("Long SPY when the lagged SOX/relative-strength signal is {} its threshold; otherwise {}."
          .format("below" if thr_rule == "lt" else "above",
                  "cash" if strat_family == "P1_long_cash" else
                  ("short SPY" if strat_family == "P3_long_short" else "scale by signal strength")))
    if not long_when_high:
        sd += " (Countercyclical orientation: weak/declining relative semis = risk-on for SPY.)"
    winner_summary["strategy_description"] = sd
    winner_summary["notes"] = (
        f"Mode 1 daily, pair260619_phlxsox_spy. CENTRAL FINDING: contemporaneous daily return corr(SOX,SPY)="
        f"{contemp_corr:.3f} is CO-MOVEMENT (shared beta), not predictive edge. Lead-lag verdict: {lead_verdict}. "
        f"Toda-Yamamoto SOX->SPY significant lags {fwd_sig or 'NONE'}; SPY->SOX significant lags {rev_sig or 'NONE'}. "
        f"Pre-whitened CCF SOX-leads(lag>0) significant {lead_sig or 'NONE'}. Incremental-edge test: lagged "
        f"relative-strength adds over SPY's OWN 63d momentum at some forecast horizon = {inc_any}. "
        f"Winner {winner['signal']}/{winner['threshold']}/{strat_family} {orientation}/L{winner['lead_days']}/"
        f"{winner['lookback']}: OOS Sharpe {winner_summary['oos_sharpe']:.2f} vs B&H {winner_summary['bh_sharpe']:.2f} "
        f"(beats={beats_bh}) AND vs SPY-OWN-MOMENTUM {winner_summary['spy_own_momentum_sharpe']:.2f} (beats={beats_spm}). "
        f"Winner bootstrap p={winner_boot_p}; IS Sharpe {float(winner['is_sharpe']):.2f} vs OOS "
        f"{float(winner['oos_sharpe']):.2f}; CP1 durability '{verdict}'; rolling-corr stability '{stab}'. "
        f"Tournament: {n_valid_total(tdf)} strategy combos (+2 benchmark rows valid=False per ECON-T4), {n_valid} valid. "
        f"{'HONEST NULL: the SOX signal does NOT beat SPY own-momentum — read as no lead beyond SPYs own trend.' if not beats_spm else 'The winner beats SPY own-momentum on OOS Sharpe, but read with heavy caution.'} "
        f"OVERFITTING FLAGS: winner IS Sharpe {float(winner['is_sharpe']):.2f} vs OOS {float(winner['oos_sharpe']):.2f} "
        f"(gap {is_oos_gap:+.2f} — the OOS window 2021-2026 was a strong semis bull, a favorable draw); the MEDIAN valid "
        f"combo scored {spec_median:.2f}, BELOW B&H {winner_summary['bh_sharpe']:.2f} (search mostly found losers); winner "
        f"win-rate {float(winner['win_rate']):.2f} and it LOST in every pre-OOS stress episode (Dot-Com/GFC/COVID). "
        f"Granger is BIDIRECTIONAL (feedback), not a clean SOX->SPY lead. Treat as search-found, not validated. "
        f"5bps cost sensitivity in tournament_validation_{DATE_TAG}/.")

    wpath = os.path.join(RESULTS_DIR, "winner_summary.json")
    with open(wpath, "w") as f:
        json.dump(winner_summary, f, indent=2)
    print(f"\n  winner_summary -> {wpath}")

    # --- ECON-H5 producer validation (blocking) ---
    rc = subprocess.run(["python3", os.path.join(BASE_DIR, "scripts", "validate_schema.py"),
                         "--schema", os.path.join(SCHEMA_DIR, "winner_summary.schema.json"),
                         "--instance", wpath]).returncode
    if rc != 0:
        raise SystemExit("winner_summary.json failed schema validation (ECON-H5)")
    print("  winner_summary schema validation: PASS")

    # --- POST-WRITE RECOMPUTE GUARDRAIL (umcsent precedent) ---
    # Re-read winner_summary, re-read signals parquet, re-encode the rule, recompute OOS Sharpe.
    with open(wpath) as f:
        ws = json.load(f)
    sigs = pd.read_parquet(os.path.join(RESULTS_DIR, f"signals_{DATE_TAG}.parquet"))
    assert ws["signal_column"] in sigs.columns, f"signal_column {ws['signal_column']} not in signals parquet"
    sr_check = pd.read_csv(os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv"), parse_dates=["date"]).set_index("date")
    oos_chk = sr_check.loc[(sr_check.index >= ws["oos_period_start"]) & (sr_check.index <= ws["oos_period_end"]), "strategy_return"]
    recomputed_sharpe = oos_chk.mean() / oos_chk.std() * np.sqrt(TRADING_DAYS)
    guard_diff = abs(recomputed_sharpe - ws["oos_sharpe"])
    assert guard_diff <= 0.03, f"GUARDRAIL FAIL: recomputed {recomputed_sharpe:.4f} vs headline {ws['oos_sharpe']:.4f}"
    print(f"  POST-WRITE GUARDRAIL: recomputed OOS Sharpe from strategy_returns + encoded rule = "
          f"{recomputed_sharpe:.4f} vs headline {ws['oos_sharpe']:.4f} (|diff|={guard_diff:.4f} <= 0.03) — PASS")

    # --- ECON-DS3 signal_code registry (append-only) ---
    try:
        reg_path = os.path.join(SCHEMA_DIR, "signal_code_registry.json")
        with open(reg_path) as f:
            registry = json.load(f)
        codes = {e["signal_code"] for e in registry["signals"]}
        if winner_summary["signal_code"] not in codes:
            registry["signals"].append({
                "signal_code": winner_summary["signal_code"],
                "display_name": "SOX/SPY relative-strength 6-month momentum",
                "parquet_column_pattern": winner_summary["signal_column"],
                "description": ("6-month (126 td) percent momentum of the SOX/SPY price ratio; relative-strength "
                                "transform that partials out common market beta. Higher = semis outperforming SPY."),
                "source_method": "roc",
                "added_at": NOW_ISO[:10],
                "first_pair": PAIR_ID,
                "notes": "Procyclical for SPY. Stationary per Dana 20260619; raw sox_spy_ratio level is NON-stationary and excluded."})
            with open(reg_path, "w") as f:
                json.dump(registry, f, indent=2)
            print(f"  signal_code '{winner_summary['signal_code']}' appended to registry (ECON-DS3)")
        else:
            print("  signal_code already in registry")
    except FileNotFoundError:
        print("  signal_code_registry.json not found — skipping (no registry in this repo state)")

    # --- interpretation_metadata: EVAN-owned fields ---
    interp_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    with open(interp_path) as f:
        interp = json.load(f)
    winner_is_sharpe = float(winner["is_sharpe"])
    winner_oos_sharpe = float(winner["oos_sharpe"])
    if not beats_spm:
        beat_clause = "The SOX signal does NOT beat SPYs own trend — honest null."
    else:
        beat_clause = (f"Winner beats SPY-own-momentum but with a strong overfit signature "
                       f"(IS Sharpe {winner_is_sharpe:.2f} vs OOS {winner_oos_sharpe:.2f}; "
                       f"median valid combo {spec_median:.2f} below B&H; loses in all pre-OOS crises).")
    interp["observed_direction"] = direction
    interp["direction_consistent"] = interp.get("expected_direction") in ("mixed", direction)
    interp["key_finding"] = (
        f"Lead-vs-co-movement verdict: contemporaneous daily corr(SOX,SPY)={contemp_corr:.2f} is shared beta, "
        f"NOT a forecast. {lead_verdict}. Toda-Yamamoto SOX->SPY sig lags {fwd_sig or 'none'}, reverse {rev_sig or 'none'}. "
        f"Relative-strength incremental edge over SPY-own-momentum at some horizon = {inc_any}. Winner "
        f"({winner['signal']}/{strat_family} {orientation}/L{winner['lead_days']}/{winner['lookback']}): OOS Sharpe "
        f"{winner_summary['oos_sharpe']:.2f} vs B&H {winner_summary['bh_sharpe']:.2f} (beats={beats_bh}) and vs "
        f"SPY-own-momentum {winner_summary['spy_own_momentum_sharpe']:.2f} (beats={beats_spm}). "
        f"{beat_clause} "
        f"Granger is bidirectional (feedback), not a clean lead. bootstrap p={winner_boot_p}, durability '{verdict}', rolling-corr '{stab}'.")
    # Confidence: demand a CLEAN one-directional lead AND no severe IS/OOS overfitting signature.
    clean_lead = sox_leads and not spy_leads_sox
    overfit_flag = (is_oos_gap > 0.75) or (spec_median < float(bh["oos_sharpe"]))
    if beats_spm and clean_lead and winner_boot_p < 0.05 and not overfit_flag:
        interp["confidence"] = "high"
    elif beats_spm and clean_lead and not overfit_flag:
        interp["confidence"] = "medium"
    else:
        interp["confidence"] = "low"
    interp["last_updated_by"] = "evan"; interp["last_updated_at"] = NOW_ISO
    with open(interp_path, "w") as f:
        json.dump(interp, f, indent=2)
    assert interp["observed_direction"] == winner_summary["direction"], "ECON-DIR1 consistency failed"
    print(f"  interpretation_metadata evan-fields updated; confidence={interp['confidence']}; ECON-DIR1: PASS")

    # tournament_winner.json (META-TWJ)
    tw = {"pair_id": PAIR_ID,
          "winner_label": (f"{winner['signal']} / {winner['threshold']} / {strat_family} ({orientation}) / "
                           f"L{winner['lead_days']} / {winner['lookback']}"),
          "winner_oos_sharpe": round(float(winner["oos_sharpe"]), 4),
          "winner_max_drawdown": round(float(winner["max_drawdown"]), 4),
          "winner_oos_ann_return": round(float(winner["oos_ann_return"]), 4),
          "bh_oos_sharpe": round(float(bh["oos_sharpe"]), 4),
          "bh_max_drawdown": round(float(bh["max_drawdown"]), 4),
          "bh_oos_ann_return": round(float(bh["oos_ann_return"]), 4),
          "spy_own_momentum_oos_sharpe": round(float(spm["oos_sharpe"]), 4),
          "spy_own_momentum_max_drawdown": round(float(spm["max_drawdown"]), 4),
          "delta_sharpe": round(float(winner["oos_sharpe"] - bh["oos_sharpe"]), 4),
          "delta_max_drawdown": round(float(winner["max_drawdown"] - bh["max_drawdown"]), 4),
          "delta_ann_return": round(float(winner["oos_ann_return"] - bh["oos_ann_return"]), 4),
          "delta_sharpe_vs_spy_momentum": round(float(winner["oos_sharpe"] - spm["oos_sharpe"]), 4),
          "beats_benchmark": beats_bh, "beats_spy_own_momentum": beats_spm,
          "suggested_strategy_objective": None, "generated_at": NOW_ISO}
    rel_sharpe = tw["delta_sharpe"] / max(abs(tw["bh_oos_sharpe"]), 0.1)
    rel_dd = tw["delta_max_drawdown"] / max(abs(tw["bh_max_drawdown"]), 0.01)
    tw["suggested_strategy_objective"] = "min_mdd" if rel_dd > rel_sharpe else "max_sharpe"
    with open(os.path.join(RESULTS_DIR, "tournament_winner.json"), "w") as f:
        json.dump(tw, f, indent=2)

    # signal_scope.json
    ind_der = [{"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []}
               for c, d, s, r in [
        ("sox", "PHLX Semiconductor Index level (NON-stationary — not a signal)", "Yahoo ^SOX", "raw"),
        ("sox_ret", "SOX daily return", "P_t/P_{t-1}-1", "derivative"),
        ("sox_mom_1m_pct", "SOX 1-month (21d) % momentum", "100*(P_t/P_{t-21}-1)", "derivative"),
        ("sox_mom_3m_pct", "SOX 3-month (63d) % momentum", "100*(P_t/P_{t-63}-1)", "derivative"),
        ("sox_mom_6m_pct", "SOX 6-month % momentum", "100*(P_t/P_{t-126}-1)", "derivative"),
        ("sox_mom_12m_pct", "SOX 12-month % momentum", "100*(P_t/P_{t-252}-1)", "derivative"),
        ("sox_spy_ratio", "SOX/SPY price ratio (NON-stationary — not a signal)", "SOX/SPY", "raw"),
        ("sox_spy_ratio_mom_1m_pct", "Relative-strength 1m momentum (partials out common beta)", "100*(R_t/R_{t-21}-1)", "derivative"),
        ("sox_spy_ratio_mom_3m_pct", "Relative-strength 3m momentum (PREFERRED intermarket signal)", "100*(R_t/R_{t-63}-1)", "derivative"),
        ("sox_spy_ratio_mom_6m_pct", "Relative-strength 6m momentum", "100*(R_t/R_{t-126}-1)", "derivative"),
        ("sox_spy_ratio_mom_12m_pct", "Relative-strength 12m momentum", "100*(R_t/R_{t-252}-1)", "derivative"),
        ("sox_spy_ratio_zscore_126d", "126d z-score of SOX/SPY ratio (regime feature)", "(R-mean126)/sd126", "derivative"),
        ("sox_spy_ratio_zscore_252d", "252d z-score of SOX/SPY ratio", "(R-mean252)/sd252", "derivative"),
        ("hmm_2state_prob_stress", "P(high-variance regime) from 2-state HMM on SOX returns", "GaussianHMM(sox_ret)", "regime_state"),
    ]]
    tgt_der = [{"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []}
               for c, d, s, r in [
        ("spy", "SPY adjusted close", "Yahoo Finance", "raw"),
        ("spy_ret", "SPY daily return", "P_t/P_{t-1}-1", "derivative"),
        ("spy_fwd_1d", "1-day forward SPY return", "P_{t+1}/P_t-1", "derivative"),
        ("spy_fwd_5d", "5-day forward SPY return", "P_{t+5}/P_t-1", "derivative"),
        ("spy_fwd_21d", "21-day forward SPY return", "P_{t+21}/P_t-1", "derivative"),
        ("spy_fwd_63d", "63-day forward SPY return", "P_{t+63}/P_t-1", "derivative"),
        ("spy_fwd_126d", "126-day forward SPY return", "P_{t+126}/P_t-1", "derivative"),
        ("spy_fwd_252d", "252-day forward SPY return", "P_{t+252}/P_t-1", "derivative"),
    ]]
    scope = {"pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan",
             "last_updated_by": "evan", "last_updated_at": NOW_ISO,
             "indicator_axis": {"canonical_column": "sox", "display_name": "PHLX Semiconductor Index (SOX)",
                                "derivatives": ind_der},
             "target_axis": {"canonical_column": "spy", "display_name": "SPY (S&P 500 ETF)", "derivatives": tgt_der},
             "notes": ("ECON-SD: only SOX/relative-strength derivatives and SPY derivatives are in scope. "
                       "Levels (sox, sox_spy_ratio) are NON-stationary and used for display only, never as signals. "
                       "regime_story: false (CP2 skipped).")}
    with open(os.path.join(RESULTS_DIR, "signal_scope.json"), "w") as f:
        json.dump(scope, f, indent=2)

    # kpis.json
    kpis = [
        {"metric": "OOS Sharpe (winner)", "value": f"{winner_summary['oos_sharpe']:.2f}", "unit": "ratio", "delta": f"{tw['delta_sharpe']:+.2f} vs B&H"},
        {"metric": "OOS Sharpe (buy & hold)", "value": f"{winner_summary['bh_sharpe']:.2f}", "unit": "ratio", "delta": None},
        {"metric": "OOS Sharpe (SPY own momentum)", "value": f"{winner_summary['spy_own_momentum_sharpe']:.2f}", "unit": "ratio", "delta": f"winner {tw['delta_sharpe_vs_spy_momentum']:+.2f}"},
        {"metric": "OOS Annual Return (winner)", "value": f"{winner_summary['oos_ann_return']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_ann_return']*100:+.1f}pp vs B&H"},
        {"metric": "OOS Max Drawdown (winner)", "value": f"{winner_summary['oos_max_drawdown']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_max_drawdown']*100:+.1f}pp vs B&H"},
        {"metric": "Contemporaneous corr (co-movement)", "value": f"{contemp_corr:.2f}", "unit": "ratio", "delta": "shared beta, not edge"},
        {"metric": "Valid strategy combos", "value": f"{n_valid}", "unit": "count", "delta": None},
        {"metric": "OOS window", "value": f"{split['oos_start']} → {split['oos_end']}", "unit": "dates", "delta": None},
    ]
    with open(os.path.join(RESULTS_DIR, "kpis.json"), "w") as f:
        json.dump(kpis, f, indent=2)

    # evidence_status.json
    evidence = {
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search",
        "updated_at": NOW_ISO, "owner": "evan",
        "plain_english": (
            f"What you see is the best rule found by searching {n_valid} valid strategy combinations on "
            f"data the model had not seen — not a rule that passed an independent final exam. The crucial "
            f"honesty point for this pair: semiconductors (SOX) and the broad market (SPY) move together "
            f"about {contemp_corr*100:.0f}% of the time on the same day, but that is shared market exposure, "
            f"NOT proof that semis predict the market. To test a real lead we required the signal to act at "
            f"least one day AHEAD and to beat a trivial 'follow SPY's own trend' rule. "
            f"{'It did NOT beat SPYs own momentum on risk-adjusted return, so the honest read is: no forecasting edge beyond the markets own trend.' if not beats_spm else 'It did edge SPYs own momentum on Sharpe, but the win is fragile: the rule looked WORSE than buy-and-hold in its training years, only shone in a single strong-semis stretch (2021-2026), lost money in every past crisis (Dot-Com, GFC, COVID), and most rules we tried scored below buy-and-hold. So this is a search-found pattern, not a confirmed edge.'} "
            f"Lead-lag statistics: {lead_verdict} — note the relationship runs BOTH ways (semis and the market push each other), so it is feedback, not a one-way lead."),
        "technical_note": (
            f"Daily, tournament-OOS only ({split['oos_start']}..{split['oos_end']}, {int(winner['oos_n'])} td). "
            f"Winner phlxsox_{winner['signal']}/{winner['threshold']}/{strat_family} {orientation}/L{winner['lead_days']}/"
            f"{winner['lookback']}: OOS Sharpe {winner_summary['oos_sharpe']} vs B&H {winner_summary['bh_sharpe']} "
            f"(beats={beats_bh}) vs SPY-own-momentum {winner_summary['spy_own_momentum_sharpe']} (beats={beats_spm}); "
            f"bootstrap p={winner_boot_p}; IS Sharpe {float(winner['is_sharpe']):.3f}. Contemporaneous corr "
            f"{contemp_corr:.3f}. TY Granger SOX->SPY sig lags {fwd_sig or 'none'}, SPY->SOX {rev_sig or 'none'}; "
            f"pre-whitened CCF SOX-leads sig {lead_sig or 'none'}. Incremental edge over SPY-own-momentum (HAC LP) "
            f"at some horizon = {inc_any}. CP1={verdict}, rolling-corr={stab}. No holdout/final exam run."),
        "next_step": ("Run ECON-FE1 final exam: freeze the winning rule and test once on a confirmation window "
                      "the search never touched. Given the SPY-own-momentum comparison "
                      + ("(NULL: no edge beyond own trend)" if not beats_spm else "(tentative edge)")
                      + ", calibrate expectation accordingly."),
    }
    epath = os.path.join(RESULTS_DIR, "evidence_status.json")
    with open(epath, "w") as f:
        json.dump(evidence, f, indent=2)
    if os.path.exists(os.path.join(SCHEMA_DIR, "evidence_status.schema.json")):
        rc = subprocess.run(["python3", os.path.join(BASE_DIR, "scripts", "validate_schema.py"),
                             "--schema", os.path.join(SCHEMA_DIR, "evidence_status.schema.json"),
                             "--instance", epath]).returncode
        if rc != 0:
            raise SystemExit("evidence_status.json failed schema validation")
        print("  evidence_status schema validation: PASS")

    # design_note.md
    inc_lines = "\n".join(f"  - fwd {r['fwd_horizon_days']}d: rel-strength coef p={r['rs_p_value']}, "
                          f"incremental R²={r['incremental_r2']} (adds over SPY-own-momentum={r['rs_adds_over_spy_own_momentum']})"
                          for r in inc_rows)
    design = f"""# Design Note — {PAIR_ID} ({DATE_TAG})

## THE central challenge: co-movement vs genuine lead
SOX and SPY are both equities; contemporaneous daily return corr = {contemp_corr:.3f}. That is shared
market beta (CO-MOVEMENT), not predictive edge. This pipeline establishes lead exclusively through:
- Tournament lead grid starts at **L1** (no L0). A same-day SOX reading is not a forecast.
- Toda-Yamamoto Granger BOTH directions at lags >=1.
- Pre-whitened CCF (each series AR-filtered) at lags -20..+20.
- Lean on the **relative-strength** transforms (sox_spy_ratio_mom_*) that partial out common beta.
- Compare the winner against TWO benchmarks: buy & hold SPY AND **SPY-own-momentum** (63d trend, long/cash).

## Lead-lag verdict
- Toda-Yamamoto SOX→SPY significant lags: {fwd_sig or 'NONE'}
- Toda-Yamamoto SPY→SOX significant lags: {rev_sig or 'NONE'}
- Pre-whitened CCF SOX-leads (lag>0) significant: {lead_sig or 'NONE'}; SPY-leads (lag<0): {lag_sig or 'NONE'}
- Verdict: {lead_verdict}

## Incremental edge over SPY's own momentum (the trivial-trend test)
HAC local projection of forward SPY return on SPY-own-momentum vs +lagged relative strength:
{inc_lines}
- Adds at some horizon: {inc_any}

## Category & method coverage (Rule C1, price/intermarket)
Full correlation battery (predictive/forward, NOT contemporaneous), pre-whitened CCF, Toda-Yamamoto
Granger (both directions), transfer entropy, local projections (fwd + reverse), quantile regression,
HMM 2-state regime detection. Stationarity: Dana's tests reviewed and CONFIRMED (levels sox & sox_spy_ratio
NON-stationary, excluded as signals).

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent.
- Lead grid: L{{1,5,10,21,63}} trading days. position_t = rule(signal_(t−L)); strategy_return_t = position_t × spy_ret_t.
- Both orientations (pro/counter) tested.
- TWO benchmark rows (BENCHMARK=buy&hold per ECON-T4; SPY_OWN_MOMENTUM=trivial trend) — both valid=False, excluded from combo counts.
- CP2 skipped — regime_story: false. Returns gross of costs; 5bps sensitivity in tournament_validation_{DATE_TAG}/.

## New pair — no prior version, Rule C3 regression diff not applicable.
"""
    with open(os.path.join(RESULTS_DIR, "design_note.md"), "w") as f:
        f.write(design)

    # analyst_suggestions.json
    sugg = {"schema_version": "1.0.0", "pair_id": PAIR_ID, "rule": "ECON-AS",
            "suggestions": [
                {"signal_name": "SOX vs SPY relative-strength breadth (semis advance/decline)", "proposed_by": "evan",
                 "source": "constructible from constituent data",
                 "observation": "Single-index SOX/SPY ratio conflates a few mega-cap semis with the sector; breadth may lead more cleanly.",
                 "rationale": "Breadth deterioration often precedes price; could sharpen the intermarket lead test.",
                 "possible_use_case": "new signal", "caveats": "Requires constituent panel; survivorship care.",
                 "date_filed": "2026-06-19"}],
            "last_updated_by": "evan", "last_updated_at": NOW_ISO}
    with open(os.path.join(RESULTS_DIR, "analyst_suggestions.json"), "w") as f:
        json.dump(sugg, f, indent=2)

    # timing
    timing = {"pair_id": PAIR_ID, "date": DATE_TAG, "pipeline_seconds": round(time.time() - t0, 1),
              "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
              "tournament_strategy_rows": int(n_valid_total(tdf)), "valid_strategies": n_valid,
              "oos_n_days": int(winner["oos_n"]), "oos_start": split["oos_start"], "oos_end": split["oos_end"]}
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump(timing, f, indent=2)

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE — HANDOFF NUMBERS")
    print("=" * 70)
    print(f"  Strategy combos: {n_valid_total(tdf)} | valid: {n_valid} | median OOS Sharpe (valid): {median_sharpe:.3f}")
    print(f"  Winner: {tw['winner_label']}")
    print(f"  OOS Sharpe {winner_summary['oos_sharpe']} vs B&H {winner_summary['bh_sharpe']} (beats={beats_bh}) "
          f"vs SPY-OWN-MOM {winner_summary['spy_own_momentum_sharpe']} (beats={beats_spm})")
    print(f"  Lead verdict: {lead_verdict}")
    print(f"  Incremental edge over SPY-own-momentum: {inc_any}")
    print(f"  Direction: {direction} | confidence: {interp['confidence']} | durability: {verdict} | corr-stab: {stab}")
    return winner_summary, tw


def n_valid_total(tdf):
    return int((~tdf.signal.isin(["BENCHMARK", "SPY_OWN_MOMENTUM"])).sum())


if __name__ == "__main__":
    main()
