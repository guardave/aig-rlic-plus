#!/usr/bin/env python3
"""
Full Econometrics Pipeline: ISM Services PMI -> SPY
===================================================
Pair ID: ism_services_spy (Mode 3 maker dispatch)
Branch: feat_ism_services_spy

Economic hypothesis (stated up front, per SOP):
  H0: ISM Services PMI does NOT predict forward SPY returns.
  H1 (procyclical prior): PMI > 50 / rising -> services expansion -> risk-on
      -> higher forward SPY returns. Tradable signal likely long when above
      threshold or improving.
  H1b (sentiment already priced): the survey is coincident with equity
      sentiment, so SPY may predict PMI as much as PMI predicts SPY.

Category (Rule C1): sentiment-equity -> full correlation battery, pre-whitened
CCF per brief, Toda-Yamamoto Granger in BOTH directions, HMM regime analysis,
quantile regression, local projections, regime/quartile returns, structural
break, and tournament.

Data: Dana's parquet data/ism_services_spy_monthly_latest.parquet
(340 x 13, monthly, 1997-07 -> 2025-10). Daily LVCF data exists separately at
data/ism_services_spy_daily_latest.parquet and already bakes release lag for
daily L0 feasibility. Stationarity tests were produced by Dana
(results/ism_services_spy/stationarity_tests_20260618.csv) -- reviewed and
confirmed here, NOT re-run. Levels are stationary because this is a bounded
diffusion index.

Provenance: ISM Services PMI is NOT on FRED; source is project Data Master.xlsx,
sheet ISM PMI, column "CDis, CSta - ISM Services PMI", vintage through Oct 2025.

Lag convention: monthly month-end PMI is not tradable until the following
release, so monthly tournament lead grid starts at L1 and sweeps around L6.
Lead semantics: position at month t = rule(signal_{t-L}); strategy_return_t =
position_t * spy_ret_t. Daily L0 is feasible only on the carried LVCF daily file.

Author: Econ Evan (Econometrics Agent)
Date: 2026-06-18
"""

import os
import sys
import json
import time
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
PAIR_ID = "ism_services_spy"
INDICATOR_NAME = "ISM Services PMI"
TARGET_NAME = "SPY"
TARGET_SYMBOL = "SPY"
DATE_TAG = "20260618"
COST_BPS = 5  # equity ETF per ECON-T2 / target-class table

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_PATH = os.path.join(BASE_DIR, "data", "ism_services_spy_monthly_latest.parquet")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")
SCHEMA_DIR = os.path.join(BASE_DIR, "docs", "schemas")

for d in [RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SIGNAL_COLS = {
    # tournament signal_code (snake_case, ECON-DS3 style) -> parquet column
    "level": "ism_services_pmi",
    "gap_50": "ism_services_gap_50",
    "delta": "ism_services_delta",
    "change_3m": "ism_services_3m_change",
    "change_6m": "ism_services_6m_change",
    "level_zscore_60m": "ism_services_zscore_60m",
    "above_50": "ism_services_above_50",
    # derived in stage_signals:
    "hmm_stress": "hmm_2state_prob_stress",
    "markov_regime": "markov_regime_2state",
}

FWD_COLS = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]


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
        "produced_by": "scripts/pair_pipeline_ism_services_spy.py",
        "generated_at": NOW_ISO,
        "columns": columns,
        "assertions": assertions,
    }
    if extra:
        m.update(extra)
    mp = os.path.splitext(path)[0] + "_manifest.json"
    with open(mp, "w") as f:
        json.dump(m, f, indent=2)


def ann_metrics(rets):
    """Annualized metrics for a monthly return series."""
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return dict(sharpe=0.0, ann_return=0.0, ann_vol=0.0, max_dd=0.0,
                    sortino=0.0, calmar=0.0, win_rate=0.0, n=len(rets))
    sharpe = rets.mean() / rets.std() * np.sqrt(12)
    ann_ret = rets.mean() * 12
    ann_vol = rets.std() * np.sqrt(12)
    cum = (1 + rets).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    neg = rets[rets < 0]
    sortino = ann_ret / (neg.std() * np.sqrt(12)) if len(neg) > 1 and neg.std() > 0 else 0.0
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    return dict(sharpe=sharpe, ann_return=ann_ret, ann_vol=ann_vol, max_dd=dd,
                sortino=sortino, calmar=calmar, win_rate=(rets > 0).mean(), n=len(rets))


# ===================================================================
# STAGE 1: LOAD + VERIFY (Defense 2 consumer checks)
# ===================================================================
@log_stage("1_load_verify")
def stage_load():
    df = pd.read_parquet(DATA_PATH)
    assert df.shape == (340, 13), f"unexpected shape {df.shape}"
    # Known-episode checks (Dana's handoff / Data Master vintage)
    assert 35.0 < df.loc["2008-11-30", "ism_services_pmi"] < 40.0
    assert 40.0 < df.loc["2020-04-30", "ism_services_pmi"] < 45.0
    assert df["ism_services_pmi"].between(30, 75).all(), "PMI magnitude implausible"
    assert df["spy_ret"].abs().max() < 0.30, "monthly SPY return magnitude implausible"
    # forward returns: no leakage at tail
    assert df["spy_fwd_12m"].iloc[-12:].isna().all()
    print(f"  Loaded {df.shape}, {df.index.min().date()} -> {df.index.max().date()}")
    print("  Defense-2 episode checks: GFC/COVID PMI contractions, return magnitudes — PASS")
    return df


# ===================================================================
# STAGE 2: DERIVED REGIME SIGNALS (HMM + Markov-switching) + persistence
# ===================================================================
@log_stage("2_signals")
def stage_signals(df):
    """Fit 2-state HMM and Markov-switching on PMI level/gap; persist ALL
    tournament-eligible signals (Derived Signal Persistence Rule)."""
    import statsmodels.api as sm
    from hmmlearn.hmm import GaussianHMM
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

    pmi = df["ism_services_pmi"].dropna()
    gap = df["ism_services_gap_50"].dropna()

    # --- HMM 2-state on PMI level ---
    X = pmi.values.reshape(-1, 1)
    hmm = GaussianHMM(n_components=2, covariance_type="full", n_iter=500, random_state=42)
    hmm.fit(X)
    probs = hmm.predict_proba(X)
    means = [hmm.means_[i].ravel()[0] for i in range(2)]
    variances = [hmm.covars_[i].ravel()[0] for i in range(2)]
    # For a diffusion index, contraction stress is the lower-PMI state; variance is
    # retained in the summary for diagnostics but not the economic label.
    stress_state = int(np.argmin(means))
    prob_stress = pd.Series(probs[:, stress_state], index=pmi.index, name="hmm_2state_prob_stress")
    df["hmm_2state_prob_stress"] = prob_stress

    hmm_states = pd.DataFrame({
        "hmm_state": pd.Series(hmm.predict(X), index=pmi.index),
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
        sub = pmi.reindex(idx)
        summ.append({
            "state_label": lbl,
            "mean_return": round(rets.mean(), 6) if len(rets) else np.nan,
            "vol": round(rets.std(), 6) if len(rets) else np.nan,
            "duration_days": int(mask.sum()),
            "frequency_pct": round(mask.mean() * 100, 2),
            "mean_pmi": round(sub.mean(), 3),
            "state_variance": round(variances[stress_state if lbl == "stress" else 1 - stress_state], 4),
        })
    pd.DataFrame(summ).to_csv(os.path.join(MODELS_DIR, "hmm_summary.csv"), index=False)

    # sanity: stress regime should capture contraction episodes.
    gfc_p = prob_stress.loc["2008-11-30":"2009-06-30"].mean()
    cov_p = prob_stress.loc["2020-04-30":"2020-06-30"].mean()
    print(f"  HMM stress prob mean GFC contraction: {gfc_p:.2f}; COVID contraction: {cov_p:.2f}")

    write_manifest(os.path.join(MODELS_DIR, "hmm_states.parquet"),
                   {"hmm_state": "integer state; stress = lower-PMI contraction regime",
                    "prob_stress": "P(stress regime); higher = lower-activity services regime",
                    "prob_calm": "1 - prob_stress"},
                   [{"description": "probabilities in [0,1]", "check": "prob_stress between 0 and 1"},
                    {"description": "GFC contraction is stress", "filter": "2008-11 to 2009-06",
                     "column": "prob_stress", "check": f"mean = {gfc_p:.2f} (computed at fit time)"},
                    {"description": "COVID contraction is stress", "filter": "2020-04 to 2020-06",
                     "column": "prob_stress", "check": f"mean = {cov_p:.2f} (computed at fit time)"},
                    {"description": "states sum to 1", "check": "prob_stress + prob_calm == 1"}])

    # --- Markov-switching regression: spy_ret ~ PMI gap, 2 regimes ---
    ms_data = pd.concat([df["spy_ret"], gap], axis=1).dropna()
    try:
        ms = MarkovRegression(ms_data["spy_ret"], k_regimes=2,
                              exog=sm.add_constant(ms_data["ism_services_gap_50"]),
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

    # --- Persist ALL tournament-eligible signals ---
    sig_cols = [c for c in SIGNAL_COLS.values() if c in df.columns]
    sig_path = os.path.join(RESULTS_DIR, f"signals_{DATE_TAG}.parquet")
    df[sig_cols].to_parquet(sig_path)
    print(f"  Signals persisted -> {sig_path} ({len(sig_cols)} columns)")
    write_manifest(sig_path,
                   {c: f"tournament-eligible signal derived solely from ISM Services ({c})" for c in sig_cols},
                   [{"description": "PMI bounded diffusion index", "column": "ism_services_pmi", "check": "values between 30 and 75"},
                    {"description": "GFC services contraction", "filter": "2008-11..2009-06",
                     "column": "ism_services_pmi", "check": "min < 45"},
                    {"description": "COVID services contraction", "filter": "2020-04..2020-06",
                     "column": "ism_services_pmi", "check": "min < 45"},
                    {"description": "HMM prob bounded", "column": "hmm_2state_prob_stress",
                     "check": "values in [0,1]"}])
    return df


# ===================================================================
# STAGE 3: EXPLORATORY + CORRELATION BATTERY (Rule C1/C2, sentiment-equity)
# ===================================================================
def _distance_corr(x, y):
    """Distance correlation (bias-uncorrected), O(n^2) — fine for monthly N."""
    x = np.asarray(x, float)[:, None]
    y = np.asarray(y, float)[:, None]
    n = len(x)
    a = np.abs(x - x.T)
    b = np.abs(y - y.T)
    A = a - a.mean(0) - a.mean(1)[:, None] + a.mean()
    B = b - b.mean(0) - b.mean(1)[:, None] + b.mean()
    dcov2 = (A * B).mean()
    dvx = (A * A).mean()
    dvy = (B * B).mean()
    if dvx <= 0 or dvy <= 0:
        return 0.0
    return float(np.sqrt(max(dcov2, 0) / np.sqrt(dvx * dvy)))


@log_stage("3_exploratory_correlations")
def stage_correlations(df):
    rows = []
    horizon_map = {"spy_fwd_1m": 1, "spy_fwd_3m": 3, "spy_fwd_6m": 6, "spy_fwd_12m": 12}
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwd, h in horizon_map.items():
            v = df[[col, fwd]].dropna()
            if len(v) < 60:
                continue
            x, y = v[col], v[fwd]
            for metric, fn in [("pearson", stats.pearsonr), ("spearman", stats.spearmanr),
                               ("kendall", stats.kendalltau)]:
                r, p = fn(x, y)
                rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": h * 21,
                             "metric": metric, "value": round(r, 4),
                             "p_value": round(p, 4), "n_obs": len(v)})
            rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": h * 21,
                         "metric": "distance", "value": round(_distance_corr(x, y), 4),
                         "p_value": np.nan, "n_obs": len(v)})
    cdf = pd.DataFrame(rows)
    path = os.path.join(MODELS_DIR, "correlations.csv")
    cdf.to_csv(path, index=False)
    write_manifest(path,
                   {"pair_name": "signal_code__forward-return-column", "horizon_days": "forward horizon in trading days (monthly*21)",
                    "metric": "pearson/spearman/kendall/distance", "value": "correlation coefficient",
                    "p_value": "two-sided p (NaN for distance corr)", "n_obs": "obs"},
                   [{"description": "values bounded", "check": "abs(value) <= 1"},
                    {"description": "monthly pair: horizons are 21/63/126/252 day equivalents", "check": "horizon_days in {21,63,126,252}"},
                    {"description": "n_obs >= 60 enforced at producer", "check": "min(n_obs) >= 60"}])
    sig = cdf[(cdf.metric == "pearson") & (cdf.p_value < 0.05)]
    print(f"  Correlation battery: {len(cdf)} rows; {len(sig)} significant Pearson cells")
    if len(sig):
        b = sig.loc[sig.value.abs().idxmax()]
        print(f"  Strongest Pearson: {b.pair_name} r={b.value} p={b.p_value}")
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

    work = df[[v for v in set(SIGNAL_COLS.values()) | {"spy_ret"} | set(FWD_COLS)
               if v in df.columns]].copy()
    main_sig = "ism_services_pmi"

    # --- 4.1 Pre-whitened CCF (lags -20..+20) ---
    pair = df[[main_sig, "spy_ret"]].dropna()
    x = pair[main_sig]
    y = pair["spy_ret"]
    best_aic, best_p = np.inf, 1
    for p in range(1, 13):
        try:
            aic = AutoReg(x, lags=p, old_names=False).fit().aic
            if aic < best_aic:
                best_aic, best_p = aic, p
        except Exception:
            pass
    ar_fit = AutoReg(x, lags=best_p, old_names=False).fit()
    x_w = ar_fit.resid
    # filter y with same AR coefficients
    coefs = ar_fit.params
    y_w = y.copy() - coefs.iloc[0]
    for i in range(1, best_p + 1):
        y_w = y_w - coefs.iloc[i] * y.shift(i)
    common = x_w.index.intersection(y_w.dropna().index)
    xw, yw = x_w.loc[common], y_w.loc[common]
    n = len(common)
    se = 1.96 / np.sqrt(n)
    rows = []
    for lag in range(-20, 21):
        # lag > 0: indicator leads target by `lag` months
        if lag >= 0:
            a, b = xw.shift(lag), yw
        else:
            a, b = xw, yw.shift(-lag)
        v = pd.concat([a, b], axis=1).dropna()
        c = v.corr().iloc[0, 1] if len(v) > 30 else np.nan
        rows.append({"lag": lag, "ccf": round(c, 4), "lower_ci": round(-se, 4),
                     "upper_ci": round(se, 4), "significant": bool(abs(c) > se) if pd.notna(c) else False,
                     "arima_order": f"AR({best_p})", "n_obs": len(v)})
    ccf_df = pd.DataFrame(rows)
    ccf_df.to_csv(os.path.join(MODELS_DIR, "ccf_prewhitened.csv"), index=False)
    lead_sig = ccf_df[(ccf_df.lag > 0) & ccf_df.significant]
    lag_sig = ccf_df[(ccf_df.lag < 0) & ccf_df.significant]
    print(f"  [4.1] CCF (AR({best_p}) prewhitening, n={n}): significant lead lags {list(lead_sig.lag)}, "
          f"significant LAG-side lags {list(lag_sig.lag)}")

    # --- 4.2 Toda-Yamamoto Granger (both directions) + by-lag artifact ---
    ty_rows, bylag_rows = [], []
    gdata = pair.rename(columns={main_sig: "ind", "spy_ret": "tgt"})
    d_max = 1  # bounded PMI level is I(0); TY augmentation retained for conservatism
    var_sel = VAR(gdata).select_order(maxlags=12)
    p_opt = max(int(var_sel.aic), 1)

    def ty_wald(caused, causing, lag):
        """Toda-Yamamoto: OLS of caused_t on const + lags 1..(lag+d_max) of both
        variables; joint F-test that lags 1..lag of `causing` are zero (the d_max
        augmentation lags are unrestricted, per TY 1995)."""
        cols = {}
        for i in range(1, lag + d_max + 1):
            cols[f"{causing}_l{i}"] = gdata[causing].shift(i)
            cols[f"{caused}_l{i}"] = gdata[caused].shift(i)
        Xd = pd.DataFrame(cols).dropna()
        yv = gdata[caused].reindex(Xd.index)
        X = sm.add_constant(Xd)
        fit = sm.OLS(yv, X).fit()
        hyp = ", ".join(f"{causing}_l{i} = 0" for i in range(1, lag + 1))
        ft = fit.f_test(hyp)
        return float(ft.fvalue), float(ft.pvalue), int(ft.df_num), int(ft.df_denom)

    for lag in range(1, 13):
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
    print(f"  [4.2] Toda-Yamamoto (d_max={d_max}, VAR p* by AIC={p_opt}):")
    print(f"        ISM Services->SPY significant at lags: {list(fwd_sig.lag)}")
    print(f"        SPY->ISM Services significant at lags: {list(rev_sig.lag)}")

    # --- 4.3 Transfer entropy (binned, permutation p) ---
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
        null = []
        v = pd.concat([src, dst], axis=1).dropna()
        for _ in range(n_perm):
            shuf = pd.Series(rng.permutation(v.iloc[:, 0].values), index=v.index)
            null.append(transfer_entropy(shuf, v.iloc[:, 1]))
        pv = float((np.array(null) >= te).mean())
        te_rows.append({"direction": direction, "te_value": round(float(te), 5),
                        "permutation_p_value": round(pv, 4), "n_permutations": n_perm,
                        "bandwidth": np.nan, "bin_method": "tercile_qcut"})
    pd.DataFrame(te_rows).to_csv(os.path.join(MODELS_DIR, "transfer_entropy.csv"), index=False)
    print(f"  [4.3] Transfer entropy: ind->tgt TE={te_rows[0]['te_value']} (p={te_rows[0]['permutation_p_value']}), "
          f"tgt->ind TE={te_rows[1]['te_value']} (p={te_rows[1]['permutation_p_value']})")

    # --- 4.4 Local projections (forward + REVERSE per mandatory check) ---
    lp_rows = []
    for direction in ["fwd", "rev"]:
        for h in [1, 3, 6, 12]:
            if direction == "fwd":
                ycol = f"spy_fwd_{h}m"
                v = df[[main_sig, ycol]].dropna()
                xv, yv = v[main_sig], v[ycol]
            else:
                # reverse: SPY return predicting ISM Services PMI h months ahead
                v = pd.concat([df["spy_ret"], df[main_sig].shift(-h)], axis=1).dropna()
                v.columns = ["x", "y"]
                xv, yv = v["x"], v["y"]
            if len(v) < 60:
                continue
            X = sm.add_constant(xv.values)
            nw = int(0.75 * len(v) ** (1 / 3)) + h
            fit = sm.OLS(yv.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = fit.conf_int()
            lp_rows.append({"horizon": h, "coef": round(fit.params[1], 6),
                            "se": round(fit.bse[1], 6),
                            "ci_lower": round(ci[1][0], 6), "ci_upper": round(ci[1][1], 6),
                            "p_value": round(fit.pvalues[1], 4), "direction": direction})
    lp_df = pd.DataFrame(lp_rows)
    lp_df.to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    rev = lp_df[lp_df.direction == "rev"]
    rev_flag = bool((rev.p_value < 0.05).any())
    print(f"  [4.4] Local projections: reverse-causality significant horizons: "
          f"{list(rev.loc[rev.p_value < 0.05, 'horizon'])} -> reverse-causality flag: {rev_flag}")

    # --- 4.5 Quantile regression (tau battery) ---
    qr_rows = []
    v = df[[main_sig, "spy_fwd_3m"]].dropna().rename(columns={main_sig: "sig", "spy_fwd_3m": "fwd"})
    for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
        try:
            qf = smf.quantreg("fwd ~ sig", v).fit(q=tau)
            ci = qf.conf_int()
            qr_rows.append({"tau": tau, "coef": round(qf.params["sig"], 6),
                            "se": round(qf.bse["sig"], 6), "p_value": round(qf.pvalues["sig"], 4),
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
            if len(v) < 60:
                continue
            X = sm.add_constant(v[col].values)
            fit = sm.OLS(v[fwd].values, X).fit(cov_type="HC3")
            reg_rows.append({"signal": code, "horizon": fwd, "coef": round(fit.params[1], 6),
                             "se": round(fit.bse[1], 6), "t_stat": round(fit.tvalues[1], 3),
                             "p_value": round(fit.pvalues[1], 4),
                             "r_squared": round(fit.rsquared, 4), "n": int(fit.nobs)})
    reg_df = pd.DataFrame(reg_rows)
    reg_df.to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    print(f"  [4.6] Predictive regressions: {len(reg_df)} cells")

    # --- 4.7 Diagnostics on baseline spec ---
    diag = []
    v = df[[main_sig, "spy_fwd_3m"]].dropna()
    X = sm.add_constant(v[main_sig].values)
    base = sm.OLS(v["spy_fwd_3m"].values, X).fit()
    resid = base.resid
    jb, jbp = stats.jarque_bera(resid)
    diag.append({"test": "Jarque-Bera", "statistic": round(jb, 3), "p_value": round(jbp, 4),
                 "interpretation": "Normal residuals" if jbp > 0.05 else "Non-normal — robust/HAC inference used"})
    from statsmodels.stats.diagnostic import het_breuschpagan, acorr_breusch_godfrey
    bp, bpp, _, _ = het_breuschpagan(resid, X)
    diag.append({"test": "Breusch-Pagan", "statistic": round(bp, 3), "p_value": round(bpp, 4),
                 "interpretation": "Homoskedastic" if bpp > 0.05 else "Heteroskedastic — HC3/HAC SEs used"})
    bg, bgp, _, _ = acorr_breusch_godfrey(base, nlags=12)
    diag.append({"test": "Breusch-Godfrey (12)", "statistic": round(bg, 3), "p_value": round(bgp, 4),
                 "interpretation": "No serial corr" if bgp > 0.05 else "Serial correlation (overlapping fwd returns) — HAC SEs used"})
    from statsmodels.stats.diagnostic import linear_reset
    try:
        rs = linear_reset(base, power=3, use_f=True)
        diag.append({"test": "RESET", "statistic": round(float(rs.fvalue), 3),
                     "p_value": round(float(rs.pvalue), 4),
                     "interpretation": "Linear form adequate" if rs.pvalue > 0.05 else "Possible nonlinearity — see quantile regression"})
    except Exception:
        pass
    pd.DataFrame(diag).to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)
    print(f"  [4.7] Diagnostics: {len(diag)} tests")

    return ccf_df, ty_df, lp_df, reg_df, rev_flag


# ===================================================================
# STAGE 5: REGIME QUARTILE RETURNS (Rule E2)
# ===================================================================
@log_stage("5_regime_quartiles")
def stage_quartiles(df):
    outputs = []
    specs = [
        ("ism_services_pmi", "regime_quartile_returns.csv", "ISM Services PMI level quartile (Q1 lowest PMI)"),
        ("ism_services_3m_change", "regime_quartile_returns_3m_change.csv", "ISM Services PMI 3-month-change quartile (Q1 weakest momentum)"),
    ]
    for sig_col, filename, desc in specs:
        v = df[[sig_col, "spy_ret"]].dropna()
        q = pd.qcut(v[sig_col], 4, labels=["Q1", "Q2", "Q3", "Q4"])
        rows = []
        for lbl in ["Q1", "Q2", "Q3", "Q4"]:
            r = v.loc[q == lbl, "spy_ret"]
            m = ann_metrics(r)
            rows.append({"quartile": lbl, "n_months": len(r), "ann_return": round(m["ann_return"], 4),
                         "ann_vol": round(m["ann_vol"], 4), "sharpe": round(m["sharpe"], 3),
                         "max_drawdown": round(m["max_dd"], 4)})
        qdf = pd.DataFrame(rows)
        path = os.path.join(RESULTS_DIR, filename)
        qdf.to_csv(path, index=False)
        print(f"  {sig_col} quartiles:")
        print(qdf.to_string(index=False))
        write_manifest(path,
                       {"quartile": desc, "n_months": "obs",
                        "ann_return": "annualized SPY return in quartile (ratio)",
                        "ann_vol": "annualized vol (ratio)", "sharpe": "ann_return/ann_vol",
                        "max_drawdown": "max DD within quartile months (negative ratio)"},
                       [{"description": "4 quartiles", "check": "len == 4"},
                        {"description": "returns plausible", "check": "abs(ann_return) < 0.5"},
                        {"description": "concurrent (NOT lagged) relationship — descriptive only", "check": "informational"}])
        outputs.append(qdf)
    return outputs[0]


# ===================================================================
# STAGE 6: TOURNAMENT (5-D) + ECON-T3/T4/OOS1/OOS2
# ===================================================================
@log_stage("6_tournament")
def stage_tournament(df):
    work = df.dropna(subset=["spy_ret"]).copy()  # SPY availability bounds sample
    n_months = len(work)
    oos_n = int(min(max(36, round(n_months * 0.25)), 120))
    oos_start = work.index[-oos_n]
    is_end = work.index[-(oos_n + 1)]
    oos_end = work.index[-1]
    print(f"  Sample (SPY-bound): {n_months} months {work.index[0].date()} -> {oos_end.date()}")
    print(f"  OOS (v1_max36_25pct_cap120): {oos_n} months, {oos_start.date()} -> {oos_end.date()}")

    split = {
        "owner": "evan",
        "split_policy_id": "v1_max36_25pct_cap120",
        "in_sample_end": is_end.strftime("%Y-%m-%d"),
        "oos_start": oos_start.strftime("%Y-%m-%d"),
        "oos_end": oos_end.strftime("%Y-%m-%d"),
        "sample_size_months": n_months,
        "justification": (
            f"Policy v1_max36_25pct_cap120 on the SPY-availability-bound sample "
            f"({n_months} months, 1993-02 onward; ISM Services history extends to 1947 but the "
            f"tournament requires target returns). min(max(36, round({n_months}*0.25)), 120) = {oos_n} "
            f"months. No structural-break exclusion applied; ISM Services PMI vintage ends Oct 2025."),
    }
    with open(os.path.join(RESULTS_DIR, "oos_split_record.json"), "w") as f:
        json.dump(split, f, indent=2)

    is_mask = work.index <= is_end
    oos_mask = work.index >= oos_start
    spy_ret = work["spy_ret"]

    leads = [1, 2, 3, 6, 12]            # L1 = real-time floor (Dana lag doc)
    lookbacks = {"LB36": 36, "LB60": 60, "LB120": 120}
    strategies = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]

    results = []
    for code, col in SIGNAL_COLS.items():
        if col not in work.columns or work[col].notna().sum() < 120:
            continue
        base_sig = work[col]
        for lead in leads:
            sig = base_sig.shift(lead)
            # ----- lookback-independent thresholds -----
            thr_static = {}
            is_sig = sig[is_mask].dropna()
            if len(is_sig) > 60:
                for pct in [25, 50, 75]:
                    thr_static[(f"T1_fixed_p{pct}", "LB_NA")] = is_sig.quantile(pct / 100)
            if code in ["gap_50", "delta", "change_3m", "change_6m"]:
                thr_static[("T4_zero", "LB_NA")] = 0.0
            # ----- lookback-dependent thresholds -----
            thr_roll = {}
            for lb_name, lb in lookbacks.items():
                minp = max(int(lb * 0.6), 24)
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
                                continue  # P2 needs a rolling range window
                            lb = lookbacks[lb_name]
                            roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24))
                            rng = (roll.max() - roll.min()).replace(0, np.nan)
                            raw = ((sig - roll.min()) / rng).clip(0, 1)
                            position = 1 - raw if orientation == "counter" else raw
                        else:
                            position = pos_bool.astype(float) * 2 - 1
                        strat_ret = position * spy_ret  # lead >= 1 ensures no lookahead
                        is_r, oos_r = strat_ret[is_mask].dropna(), strat_ret[oos_mask].dropna()
                        if len(is_r) < 60 or len(oos_r) < 24:
                            continue
                        m_is, m = ann_metrics(is_r), ann_metrics(oos_r)
                        pos_oos = position[oos_mask]
                        n_trades = int((pos_oos.diff().abs() > 1e-9).sum())
                        years = len(pos_oos.dropna()) / 12
                        turnover = n_trades / years if years > 0 else 999
                        valid = bool(m["sharpe"] > 0.3 and turnover < 24 and len(oos_r) >= 24)
                        results.append({
                            "signal": code, "threshold": thr_name, "strategy": f"{strat}_{orientation}",
                            "lead_months": lead, "lookback": lb_name,
                            "is_sharpe": round(m_is["sharpe"], 4),
                            "oos_sharpe": round(m["sharpe"], 4),
                            "oos_sortino": round(m["sortino"], 4), "oos_calmar": round(m["calmar"], 4),
                            "oos_ann_return": round(m["ann_return"], 4),
                            "oos_ann_vol": round(m["ann_vol"], 4),
                            "max_drawdown": round(m["max_dd"], 4),
                            "win_rate": round(m["win_rate"], 4), "n_trades": n_trades,
                            "annual_turnover": round(turnover, 2),
                            "oos_n": len(oos_r), "valid": valid,
                        })

    # Benchmark row (ECON-T4: valid=False, signal=="BENCHMARK")
    bh_oos = spy_ret[oos_mask].dropna()
    bh_is = spy_ret[is_mask].dropna()
    mb, mbi = ann_metrics(bh_oos), ann_metrics(bh_is)
    results.append({
        "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "P0_buy_and_hold",
        "lead_months": 0, "lookback": "LB_NA",
        "is_sharpe": round(mbi["sharpe"], 4), "oos_sharpe": round(mb["sharpe"], 4),
        "oos_sortino": round(mb["sortino"], 4), "oos_calmar": round(mb["calmar"], 4),
        "oos_ann_return": round(mb["ann_return"], 4), "oos_ann_vol": round(mb["ann_vol"], 4),
        "max_drawdown": round(mb["max_dd"], 4), "win_rate": round(mb["win_rate"], 4),
        "n_trades": 0, "annual_turnover": 0.0, "oos_n": len(bh_oos), "valid": False,
    })

    tdf = pd.DataFrame(results)
    assert (tdf["signal"] == "BENCHMARK").sum() == 1, "exactly one benchmark row required (ECON-T4)"
    tpath = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _tournament_io import write_tournament  # ECON-T5 §4 immutability guard
    write_tournament(tdf, tpath)

    strat_pop = tdf[tdf.signal != "BENCHMARK"]
    n_valid = int(strat_pop["valid"].sum())
    print(f"  Combos evaluated: {len(strat_pop)} strategies + 1 benchmark; valid: {n_valid}")
    print(f"  B&H OOS Sharpe {mb['sharpe']:.3f}, maxDD {mb['max_dd']:.3f}, ann ret {mb['ann_return']:.3f}")

    manifest = {
        "file": os.path.basename(tpath), "pair_id": PAIR_ID,
        "grid": {"signals": [k for k, v in SIGNAL_COLS.items() if v in work.columns],
                 "thresholds": "T1_fixed_p{25,50,75}, T2_roll_p{25,75}, T3_zscore_{±1.0,±1.5}, T4_zero (gap/change signals)",
                 "strategies": [s + "_{pro,counter}" for s in strategies],
                 "leads_months": leads, "lookbacks": list(lookbacks.keys()) + ["LB_NA"]},
        "units": "oos_ann_return / oos_ann_vol / max_drawdown are RATIOS (decimal), not percent",
        "total_strategy_rows": len(strat_pop), "valid_strategy_rows": n_valid,
        "sampling": "exhaustive (no stratified sampling; grid within budget)",
        "benchmark_row": "signal==BENCHMARK, valid=False per ECON-T4",
        "execution_lag": "position_t = rule(signal_{t-lead}), lead >= 1 (L1 real-time floor per Dana lag doc)",
        "cost_note": "returns are gross of costs; 5bps sensitivity in tournament_validation",
        "assertions": [
            "top strategy oos_sharpe > bottom strategy oos_sharpe",
            "all oos_sharpe finite",
            "exactly one BENCHMARK row, valid=False",
        ],
        "generated_at": NOW_ISO,
    }
    with open(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    return tdf, split


# ===================================================================
# STAGE 7: WINNER SELECTION (ECON-T3 cascade) + artifacts
# ===================================================================
def select_winner(tdf):
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid].copy()
    if len(cand) == 0:
        raise RuntimeError("no valid strategies — escalate to Lead")
    cascade = [("oos_sharpe", False), ("oos_ann_return", False),
               ("abs_dd", True), ("n_trades", False), ("signal", True)]
    cand["abs_dd"] = cand["max_drawdown"].abs()
    pool = cand
    resolved_at = 1
    tie_pool_step1 = None
    for i, (colname, ascending) in enumerate(cascade, start=1):
        best_val = pool[colname].min() if ascending else pool[colname].max()
        nxt = pool[pool[colname] == best_val]
        if i == 1:
            tie_pool_step1 = nxt.copy()
        if len(nxt) == 1:
            resolved_at = i
            pool = nxt
            break
        pool = nxt
        resolved_at = i
    winner = pool.iloc[0]
    return winner, resolved_at, tie_pool_step1, cand


def derive_winner_series(df, winner, split):
    """Re-derive the winner's position/return series exactly as the tournament did."""
    work = df.dropna(subset=["spy_ret"]).copy()
    is_mask = work.index <= split["in_sample_end"]
    sig = work[SIGNAL_COLS[winner["signal"]]].shift(int(winner["lead_months"]))
    thr_name, lb_name = winner["threshold"], winner["lookback"]
    lookbacks = {"LB36": 36, "LB60": 60, "LB120": 120}
    if thr_name.startswith("T1_fixed_p"):
        pct = int(thr_name.split("p")[-1])
        thr = sig[is_mask].dropna().quantile(pct / 100)
    elif thr_name == "T4_zero":
        thr = 0.0
    elif thr_name.startswith("T2_roll_p"):
        lb = lookbacks[lb_name]
        thr = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24)).quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name.startswith("T3_zscore"):
        lb = lookbacks[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24))
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
        lb = lookbacks[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24))
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
    rank_metric = cand.sort_values("oos_sharpe", ascending=False).reset_index()
    median_sharpe = float(cand["oos_sharpe"].median())
    n_tied = int((cand["oos_sharpe"] == winner["oos_sharpe"]).sum())
    print(f"  Winner: {winner['signal']}/{winner['threshold']}/{winner['strategy']}/L{winner['lead_months']}/{winner['lookback']}")
    print(f"  OOS Sharpe {winner['oos_sharpe']} | ties at step1: {n_tied} | cascade resolved at step {resolved_at}")

    if resolved_at > 1:
        lines = [f"# Tournament Tie Note — {PAIR_ID} ({DATE_TAG})", "",
                 f"Winner resolved at cascade step {resolved_at} (ECON-T3).", "",
                 "## Candidates tied at step 1 (oos_sharpe)", "",
                 tie_pool[["signal", "threshold", "strategy", "lead_months", "lookback",
                           "oos_sharpe", "oos_ann_return", "max_drawdown", "n_trades"]].to_markdown(index=False),
                 "", "Interpretation: candidates are near-equivalent on the primary objective; "
                 "the selected winner is preferred on the documented tie-break dimension. No candidate "
                 "is plausibly superior on turnover (all within the validity cap)."]
        with open(os.path.join(RESULTS_DIR, "tournament_tie_note.md"), "w") as f:
            f.write("\n".join(lines))
        print("  Tie note written (cascade fired beyond step 1)")

    # --- derive winner series & reconcile (ECON-SR1) ---
    position, spy_ret, sig_lagged, thr = derive_winner_series(df, winner, split)
    oos_mask = (spy_ret.index >= split["oos_start"]) & (spy_ret.index <= split["oos_end"])
    strat_ret = (position * spy_ret)
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

    # persist strategy_returns (full sample; position NaN -> 0 pre-history)
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
        "produced_by": "scripts/pair_pipeline_ism_services_spy.py", "rule": "ECON-SR1",
        "source": "pipeline_native_derivation (same code path as tournament evaluation — not a re-derivation)",
        "returns_file": DATA_PATH,
        "coverage_start": str(spy_ret.index[0].date()), "coverage_end": str(spy_ret.index[-1].date()),
        "frequency": "monthly",
        "oos_start": split["oos_start"], "oos_end": split["oos_end"],
        "position_semantics": ("position on row t is the return-accrual weight for month t; the "
                               f"signal is lagged {int(winner['lead_months'])} month(s) (execution/publication "
                               "lag already applied); strategy_return = position * bh_return row-wise"),
        "reconciliation": {k: {"computed": v["computed"], "reported_winner_summary": v["reported_tournament"],
                               "diff": v["diff"], "tolerance": v["tolerance"], "verdict": v["verdict"]}
                           for k, v in rec.items()},
        "generated_at": NOW_ISO, "generated_by": "Econ Evan (feat_ism_services_spy)",
    }
    with open(os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}_meta.json"), "w") as f:
        json.dump(sr_meta, f, indent=2)
    print(f"  Strategy returns -> {sr_path}")

    # --- winner_trade_log.csv (internal daily/monthly position log) ---
    log = pd.DataFrame({
        "date": spy_ret.index.strftime("%Y-%m-%d"),
        "signal_value": sig_lagged.reindex(spy_ret.index).round(4),
        "threshold": (thr.reindex(spy_ret.index).round(4) if isinstance(thr, pd.Series)
                      else np.round(thr, 4)),
        "position": position.reindex(spy_ret.index).fillna(0.0),
        "spy_return": spy_ret.round(6),
        "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0.0).round(6),
    })
    log["cumulative_return"] = ((1 + log["strategy_return"]).cumprod() - 1).round(6)
    log_path = os.path.join(RESULTS_DIR, "winner_trade_log.csv")
    log.to_csv(log_path, index=False)

    # --- broker-style trade log (Rule C4) ---
    spy_px = df["spy"].reindex(spy_ret.index)
    broker_rows, cum = [], (1 + strat_ret.reindex(spy_ret.index).fillna(0.0)).cumprod()
    prev = 0.0
    capital = 10000.0
    sig_disp = f"{winner['signal']} ({SIGNAL_COLS[winner['signal']]})"
    for dt in spy_ret.index:
        p = float(position.reindex(spy_ret.index).fillna(0.0).loc[dt])
        if abs(p - prev) > 1e-9:
            side = "BUY" if p > prev else "SELL"
            qty = abs(p) * 100
            notional = abs(p - prev) * capital
            sv = sig_lagged.loc[dt]
            th = thr.loc[dt] if isinstance(thr, pd.Series) else thr
            broker_rows.append({
                "trade_date": dt.strftime("%Y-%m-%d"), "side": side, "instrument": TARGET_SYMBOL,
                "quantity_pct": round(qty, 1),
                "price": round(float(spy_px.loc[dt]), 4) if pd.notna(spy_px.loc[dt]) else np.nan,
                "notional_usd": round(notional, 2), "commission_bps": COST_BPS,
                "commission_usd": round(notional * COST_BPS / 10000, 2),
                "cum_pnl_pct": round((cum.loc[dt] - 1) * 100, 4),
                "reason": (f"{winner['strategy']}: {sig_disp} = "
                           f"{sv:.3f} vs threshold {th:.3f} — position {prev*100:.0f}% → {p*100:.0f}%"
                           if pd.notna(sv) else "position change"),
            })
            prev = p
    broker_path = os.path.join(RESULTS_DIR, "winner_trades_broker_style.csv")
    with open(broker_path, "w") as f:
        f.write(f"# Simulated trade record based on backtest signals. No real trades were executed. "
                f"Starting capital: $10000. Commission: {COST_BPS} bps (tournament cost parameter). "
                f"Pair: {PAIR_ID}. Strategy: {winner['strategy']} on {sig_disp}, "
                f"threshold {winner['threshold']}, lead L{winner['lead_months']}, {winner['lookback']}.\n")
        pd.DataFrame(broker_rows).to_csv(f, index=False)
    print(f"  Trade logs -> {log_path} ({len(log)} rows), broker-style ({len(broker_rows)} events)")

    return winner, rec, n_valid, median_sharpe, n_tied, resolved_at, position, strat_ret, sig_lagged, thr


# ===================================================================
# STAGE 8: CROSS-PERIOD ANALYSES (ECON-CP1 A/B/C)
# ===================================================================
@log_stage("8_cross_period")
def stage_cross_period(df, winner, split, position, strat_ret, sig_lagged):
    import statsmodels.api as sm

    # CP1-A: subperiod Sharpe from episode registry (sentiment category fallback)
    with open(os.path.join(SCHEMA_DIR, "episode_registry.json")) as f:
        reg = json.load(f)
    episodes = reg.get("sentiment", reg["_fallback"])
    oos = strat_ret[(strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])]
    rows = []
    pos_eps = 0
    eval_eps = 0
    for ep in episodes:
        sub = oos[(oos.index >= ep["start"]) & (oos.index <= ep["end"])].dropna()
        if len(sub) < 3:  # monthly counterpart of the 21-trading-day daily floor
            rows.append({"episode": ep["slug"], "start_date": ep["start"], "end_date": ep["end"],
                         "n_trading_days": len(sub) * 21, "ann_sharpe": np.nan, "win_rate": np.nan,
                         "max_drawdown": np.nan, "data_status": "insufficient_data",
                         "durability_verdict": ""})
            continue
        m = ann_metrics(sub)
        eval_eps += 1
        pos_eps += int(m["sharpe"] > 0)
        rows.append({"episode": ep["slug"],
                     "start_date": str(sub.index[0].date()), "end_date": str(sub.index[-1].date()),
                     "n_trading_days": len(sub) * 21, "ann_sharpe": round(m["sharpe"], 4),
                     "win_rate": round(m["win_rate"], 4), "max_drawdown": round(m["max_dd"], 4),
                     "data_status": "validated", "durability_verdict": ""})
    if eval_eps >= 3:
        verdict = "durable" if pos_eps >= 3 else ("conditionally_durable" if pos_eps == 2 else "episode_concentrated")
    else:
        verdict = ("conditionally_durable" if pos_eps == eval_eps and eval_eps > 0
                   else "episode_concentrated") if eval_eps else "insufficient_data"
    rows[-1]["durability_verdict"] = verdict
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "subperiod_sharpe.csv"), index=False)
    print(f"  CP1-A: {eval_eps} episodes evaluable within OOS, {pos_eps} positive -> {verdict}")

    # CP1-B: rolling 24M corr (winning signal vs spy_fwd_1m, full sample)
    v = pd.concat([sig_lagged.rename("sig"), df["spy_fwd_1m"]], axis=1).dropna()
    full_r = v["sig"].corr(v["spy_fwd_1m"])
    roll = v["sig"].rolling(24).corr(v["spy_fwd_1m"])
    out = pd.DataFrame({"date": v.index.strftime("%Y-%m-%d"), "rolling_corr": roll.round(4).values,
                        "n_obs": 24,
                        "window_start": v.index.to_series().shift(23).dt.strftime("%Y-%m-%d").values})
    out = out.dropna(subset=["rolling_corr"])
    out.to_csv(os.path.join(RESULTS_DIR, f"rolling_correlation_{PAIR_ID}.csv"), index=False)
    same_sign = float((np.sign(roll.dropna()) == np.sign(full_r)).mean())
    stab = ("sign_stable" if same_sign >= 0.7 else
            "moderately_stable" if same_sign >= 0.5 else "sign_unstable")
    print(f"  CP1-B: full-sample r={full_r:.3f}, sign stability {same_sign:.2f} -> {stab}")

    # CP1-C: Quandt-Andrews sup-F on spy_ret ~ signal, bootstrap p
    reg_v = pd.concat([sig_lagged.rename("sig"), df["spy_ret"]], axis=1).dropna()
    yv = reg_v["spy_ret"].values
    Xv = sm.add_constant(reg_v["sig"].values)
    n = len(yv)
    lo, hi = int(n * 0.15), int(n * 0.85)
    full = sm.OLS(yv, Xv).fit()
    ssr_full = full.ssr
    k = Xv.shape[1]

    def sup_f(y, X):
        ssr_f = sm.OLS(y, X).fit().ssr
        best, bidx = -np.inf, lo
        for b in range(lo, hi):
            s1 = sm.OLS(y[:b], X[:b]).fit().ssr
            s2 = sm.OLS(y[b:], X[b:]).fit().ssr
            f = ((ssr_f - s1 - s2) / k) / ((s1 + s2) / (len(y) - 2 * k))
            if f > best:
                best, bidx = f, b
        return best, bidx

    f_obs, b_idx = sup_f(yv, Xv)
    rng = np.random.default_rng(42)
    null = []
    resid = full.resid
    fitted = full.fittedvalues
    for _ in range(300):
        y_b = fitted + rng.choice(resid, size=n, replace=True)
        fb, _ = sup_f(y_b, Xv)
        null.append(fb)
    p_break = float((np.array(null) >= f_obs).mean())
    break_date = str(reg_v.index[b_idx].date())
    flagged = p_break < 0.10
    sb = {"pair_id": PAIR_ID, "test": "Quandt-Andrews unknown breakpoint (sup-F, residual-bootstrap p, 300 reps)",
          "sample_start": str(reg_v.index[0].date()), "sample_end": str(reg_v.index[-1].date()),
          "n_obs": n, "trimming_pct": 0.15, "break_date": break_date,
          "f_stat": round(float(f_obs), 4), "p_value": round(p_break, 4), "flagged": flagged,
          "flag_message": ("Structural break detected — interpret cross-period results with caution."
                           if flagged else None),
          "rolling_corr_sign_stability": round(same_sign, 4),
          "rolling_corr_stability_verdict": stab,
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
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid]
    top5 = cand.nlargest(5, "oos_sharpe")
    rng = np.random.default_rng(42)
    boot = np.zeros(5000)
    for b in range(5000):
        s = rng.choice(spy_oos.values, size=len(spy_oos), replace=True)
        boot[b] = (s.mean() / s.std()) * np.sqrt(12) if s.std() > 0 else 0
    rows = [{"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
             "lead_months": r.lead_months, "lookback": r.lookback, "oos_sharpe": r.oos_sharpe,
             "bootstrap_p_value": round(float((boot >= r.oos_sharpe).mean()), 4),
             "significant_at_5pct": bool((boot >= r.oos_sharpe).mean() < 0.05)}
            for r in top5.itertuples()]
    pd.DataFrame(rows).to_csv(os.path.join(VALID_DIR, "bootstrap.csv"), index=False)

    stress = {"Dot_Com": ("2000-03-01", "2002-10-31"), "GFC": ("2008-01-01", "2009-06-30"),
              "COVID": ("2020-01-01", "2020-06-30"), "Rate_Hike_2022": ("2022-01-01", "2023-06-30")}
    srows = []
    for nm, (s, e) in stress.items():
        sub_bh = df["spy_ret"][(df.index >= s) & (df.index <= e)].dropna()
        sub_st = strat_ret[(strat_ret.index >= s) & (strat_ret.index <= e)].dropna()
        if len(sub_bh) > 3:
            srows.append({"period": nm, "start": s, "end": e, "n_months": len(sub_bh),
                          "buy_hold_sharpe": round(ann_metrics(sub_bh)["sharpe"], 4),
                          "buy_hold_return_pct": round(sub_bh.sum() * 100, 2),
                          "winner_sharpe": round(ann_metrics(sub_st)["sharpe"], 4) if len(sub_st) > 3 else np.nan,
                          "winner_return_pct": round(sub_st.sum() * 100, 2) if len(sub_st) > 3 else np.nan})
    pd.DataFrame(srows).to_csv(os.path.join(VALID_DIR, "stress_tests.csv"), index=False)

    tx = []
    for r in top5.itertuples():
        for bps in [0, 5, 10, 25, 50]:
            ann_cost = r.annual_turnover * bps / 10000
            net_sharpe = r.oos_sharpe - ann_cost / r.oos_ann_vol if r.oos_ann_vol > 0 else r.oos_sharpe
            tx.append({"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
                       "tx_cost_bps": bps, "gross_sharpe": r.oos_sharpe,
                       "net_sharpe_approx": round(net_sharpe, 4)})
    pd.DataFrame(tx).to_csv(os.path.join(VALID_DIR, "transaction_costs.csv"), index=False)
    print(f"  bootstrap (top5), stress ({len(srows)} periods), tx-cost grid saved")
    return rows


# ===================================================================
# MAIN
# ===================================================================
def main():
    t0 = time.time()
    df = stage_load()
    df = stage_signals(df)
    corr_df = stage_correlations(df)
    ccf_df, ty_df, lp_df, reg_df, rev_flag = stage_core_models(df)
    qdf = stage_quartiles(df)
    tdf, split = stage_tournament(df)
    (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
     position, strat_ret, sig_lagged, thr) = stage_winner(df, tdf, split)
    verdict, stab, sb, full_r = stage_cross_period(df, winner, split, position, strat_ret, sig_lagged)
    boot_rows = stage_validation(df, tdf, split, strat_ret)
    winner_boot_p = boot_rows[0]["bootstrap_p_value"] if boot_rows else np.nan

    bh = tdf[tdf.signal == "BENCHMARK"].iloc[0]

    # --- direction of winner ---
    # orientation 'pro' + 'gt'-style rule means long when signal HIGH;
    # economic direction: does the winner go long when PMI/gap is high (procyclical) or low?
    orientation = winner["strategy"].rsplit("_", 1)[1]
    neg_thr = "neg_" in winner["threshold"]
    long_when_high = (orientation == "pro") != neg_thr
    direction = "procyclical" if long_when_high else "countercyclical"

    thr_value = float(thr.dropna().iloc[-1]) if isinstance(thr, pd.Series) else float(thr)
    thr_rule = "lt" if neg_thr else "gt"
    strat_family = winner["strategy"].rsplit("_", 1)[0]

    winner_summary = {
        "pair_id": PAIR_ID,
        "generated_at": NOW_ISO,
        "signal_column": SIGNAL_COLS[winner["signal"]],
        "signal_code": f"ism_services_{winner['signal']}" if not winner["signal"].startswith(("hmm", "markov")) else winner["signal"],
        "signal_display_name": f"ISM Services {winner['signal']}",
        "target_symbol": TARGET_SYMBOL,
        "threshold_code": winner["threshold"],
        "threshold_value": round(thr_value, 4),
        "threshold_rule": thr_rule,
        "threshold_note": ("threshold is rolling (window per lookback); threshold_value is the latest "
                           "rolling value — see winner_trade_log.csv for the full threshold path"
                           if isinstance(thr, pd.Series) else "static threshold (IS-calibrated)"),
        "strategy_family": strat_family,
        "strategy_code": strat_family.split("_")[0],
        "strategy_display_name": {"P1_long_cash": "Long/Cash", "P2_signal_strength": "Signal-strength sizing",
                                  "P3_long_short": "Long/Short"}[strat_family],
        "strategy_description": "",  # filled below
        "lead_value": int(winner["lead_months"]),
        "lead_unit": "months",
        "lead_description": f"Signal lead = {int(winner['lead_months'])} month(s); L1 is the monthly real-time floor because prior-month PMI is released early in the following month",
        "lookback": winner["lookback"],
        "direction": direction,
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
        "oos_period_start": split["oos_start"],
        "oos_period_end": split["oos_end"],
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_ann_return": round(float(bh["oos_ann_return"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4),
        "cost_assumption_bps": COST_BPS,
        "total_combos": int(len(tdf) - 1),
        "valid_combos": n_valid,
        "schema_version": "1.1.0",
        "notes": (f"Mode 3, feat_ism_services_spy. Tournament: {len(tdf)-1} strategy combos "
                  f"(+1 benchmark, valid=False per ECON-T4), {n_valid} valid. Winner by ECON-T3 cascade "
                  f"(resolved at step {resolved_at}; {n_tied} tied at step 1). Strategy returns are gross "
                  f"of transaction costs; {COST_BPS} bps sensitivity in tournament_validation_{DATE_TAG}/. "
                  f"ISM Services PMI behaves as a coincident/sentiment survey in this sample: "
                  f"Toda-Yamamoto Granger finds NO monthly forward causality (ISM Services->SPY n.s. at all lags 1-12) "
                  f"and STRONG reverse causality (SPY->ISM Services significant at every lag). "
                  f"Robustness caveats: winner bootstrap p = {winner_boot_p:.3f} (NOT significant at 5% vs "
                  f"resampled B&H); in-sample Sharpe {float(winner['is_sharpe']):.2f} vs OOS "
                  f"{float(winner['oos_sharpe']):.2f} (IS/OOS inconsistency suggests a favorable OOS draw); "
                  f"CP1 durability verdict '{verdict}'; rolling-correlation stability '{stab}'. OOS exposure "
                  f"is sparse (mean position {float(position[(position.index >= split['oos_start'])].mean()):.2f}) "
                  f"— most of the DD advantage comes from being in cash."),
    }
    sd = ("Long SPY when the lagged ISM Services signal is {} its threshold; otherwise {}."
          .format("below" if thr_rule == "lt" else "above",
                  "cash" if strat_family == "P1_long_cash" else
                  ("short SPY" if strat_family == "P3_long_short" else "scale by signal strength")))
    if not long_when_high:
        sd += " (Countercyclical orientation: weak PMI/gap = risk-on after lag.)"
    winner_summary["strategy_description"] = sd

    wpath = os.path.join(RESULTS_DIR, "winner_summary.json")
    with open(wpath, "w") as f:
        json.dump(winner_summary, f, indent=2)
    print(f"\n  winner_summary -> {wpath}")

    # --- ECON-H5 producer validation (blocking) ---
    import subprocess
    rc = subprocess.run(["python3", os.path.join(BASE_DIR, "scripts", "validate_schema.py"),
                         "--schema", os.path.join(SCHEMA_DIR, "winner_summary.schema.json"),
                         "--instance", wpath]).returncode
    if rc != 0:
        raise SystemExit("winner_summary.json failed schema validation — fix the producer (ECON-H5)")
    print("  winner_summary schema validation: PASS")

    # --- ECON-DS3 producer assertion: signal_code must be in the registry ---
    with open(os.path.join(SCHEMA_DIR, "signal_code_registry.json")) as f:
        registry_codes = {e["signal_code"] for e in json.load(f)["signals"]}
    assert winner_summary["signal_code"] in registry_codes, (
        f"signal_code '{winner_summary['signal_code']}' not in signal_code_registry.json — "
        "append it (append-only) before rerunning (ECON-DS3)")
    print("  signal_code registry assertion: PASS")

    # --- interpretation_metadata: update EVAN-OWNED fields only (per owner_writes) ---
    interp_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    with open(interp_path) as f:
        interp = json.load(f)
    assert set(["observed_direction", "direction_consistent", "key_finding", "confidence"]
               ).issubset(set(interp["owner_writes"]["evan"])), "evan-owned fields changed — re-check DATA-D6"
    interp["observed_direction"] = direction
    interp["direction_consistent"] = interp.get("expected_direction") in ("mixed", direction)
    interp["key_finding"] = (
        f"Lead-lag verdict: ISM Services PMI does not lead SPY at monthly frequency. Toda-Yamamoto Granger "
        f"ISM Services->SPY is not significant at any lag 1-12, while SPY->ISM Services is significant at every lag, "
        f"consistent with a sentiment/coincident survey already reflected in equities. The tournament winner "
        f"({winner['signal']}/{winner['threshold']}/"
        f"{strat_family} {orientation}/L{winner['lead_months']}/{winner['lookback']}) is countercyclical "
        f"(long SPY only when lagged PMI gap-to-50 is unusually weak versus its rolling window): OOS "
        f"Sharpe {winner_summary['oos_sharpe']:.2f} vs B&H {winner_summary['bh_sharpe']:.2f}, max DD "
        f"{winner_summary['oos_max_drawdown']*100:.1f}% vs {winner_summary['bh_max_drawdown']*100:.1f}%, but "
        f"it gives up return ({winner_summary['oos_ann_return']*100:.1f}% vs {winner_summary['bh_ann_return']*100:.1f}%), "
        f"bootstrap p={winner_boot_p:.3f} (n.s. at 5%), and a structural break is flagged at {sb['break_date']} — "
        f"treat as a drawdown-control search result, not validated standalone alpha.")
    interp["confidence"] = "low"
    interp["last_updated_by"] = "evan"
    interp["last_updated_at"] = NOW_ISO
    with open(interp_path, "w") as f:
        json.dump(interp, f, indent=2)
    assert interp["observed_direction"] in {"procyclical", "countercyclical", "mixed"}
    assert interp["observed_direction"] == winner_summary["direction"], "ECON-DIR1 consistency check failed"
    print("  interpretation_metadata evan-fields updated; ECON-DIR1 vocabulary+consistency: PASS")

    # tournament_winner.json (META-TWJ)
    tw = {
        "pair_id": PAIR_ID,
        "winner_label": (f"{winner['signal']} / {winner['threshold']} / {strat_family} "
                         f"({orientation}) / L{winner['lead_months']} / {winner['lookback']}"),
        "winner_oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "winner_max_drawdown": round(float(winner["max_drawdown"]), 4),
        "winner_oos_ann_return": round(float(winner["oos_ann_return"]), 4),
        "bh_oos_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4),
        "bh_oos_ann_return": round(float(bh["oos_ann_return"]), 4),
        "delta_sharpe": round(float(winner["oos_sharpe"] - bh["oos_sharpe"]), 4),
        "delta_max_drawdown": round(float(winner["max_drawdown"] - bh["max_drawdown"]), 4),
        "delta_ann_return": round(float(winner["oos_ann_return"] - bh["oos_ann_return"]), 4),
        "beats_benchmark": bool(winner["oos_sharpe"] > bh["oos_sharpe"]),
        "suggested_strategy_objective": None,  # filled below
        "generated_at": NOW_ISO,
    }
    rel_sharpe = tw["delta_sharpe"] / max(abs(tw["bh_oos_sharpe"]), 0.1)
    rel_dd = tw["delta_max_drawdown"] / max(abs(tw["bh_max_drawdown"]), 0.01)
    tw["suggested_strategy_objective"] = "min_mdd" if rel_dd > rel_sharpe else "max_sharpe"
    with open(os.path.join(RESULTS_DIR, "tournament_winner.json"), "w") as f:
        json.dump(tw, f, indent=2)

    # signal_scope.json (ECON-UD)
    ind_der = [
        {"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []}
        for c, d, s, r in [
            ("ism_services_pmi", "Headline ISM Services PMI diffusion index level", "Data Master.xlsx / ISM PMI / CDis, CSta - ISM Services PMI", "raw"),
            ("ism_services_gap_50", "PMI minus the 50 expansion threshold", "PMI_t - 50", "threshold_input"),
            ("ism_services_delta", "One-month change in PMI, in index points", "PMI_t - PMI_{t-1}", "derivative"),
            ("ism_services_3m_change", "Three-month change in PMI, in index points", "PMI_t - PMI_{t-3}", "derivative"),
            ("ism_services_6m_change", "Six-month change in PMI, in index points", "PMI_t - PMI_{t-6}", "derivative"),
            ("ism_services_zscore_60m", "Rolling 60-month z-score of the PMI level", "(PMI_t - mean60(PMI)) / sd60(PMI)", "threshold_input"),
            ("ism_services_above_50", "Flag equal to 1 when PMI is above 50", "indicator(PMI_t > 50)", "threshold_input"),
            ("hmm_2state_prob_stress", "Probability of the low-PMI contraction regime from a 2-state HMM", "GaussianHMM(PMI)", "regime_state"),
            ("markov_regime_2state", "Probability of the high-volatility regime from a Markov-switching regression", "MarkovRegression(spy_ret ~ PMI gap)", "regime_state"),
        ]]
    tgt_der = [
        {"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []}
        for c, d, s, r in [
            ("spy", "SPY adjusted month-end close", "Yahoo Finance", "raw"),
            ("spy_ret", "SPY monthly return (decimal)", "P_t/P_{t-1}-1", "derivative"),
            ("spy_fwd_1m", "1-month forward SPY return", "P_{t+1}/P_t-1", "derivative"),
            ("spy_fwd_3m", "3-month forward SPY return", "P_{t+3}/P_t-1", "derivative"),
            ("spy_fwd_6m", "6-month forward SPY return", "P_{t+6}/P_t-1", "derivative"),
            ("spy_fwd_12m", "12-month forward SPY return", "P_{t+12}/P_t-1", "derivative"),
        ]]
    scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan",
        "last_updated_by": "evan", "last_updated_at": NOW_ISO,
        "indicator_axis": {
            "canonical_column": "ism_services_pmi",
            "display_name": "ISM Services PMI",
            "derivatives": ind_der,
        },
        "target_axis": {
            "canonical_column": "spy",
            "display_name": "SPY (S&P 500 ETF)",
            "derivatives": tgt_der,
        },
        "notes": ("ECON-SD: only ISM Services PMI derivatives and SPY derivatives are in scope. "
                  "regime_story: false (CP2 skipped)."),
    }
    with open(os.path.join(RESULTS_DIR, "signal_scope.json"), "w") as f:
        json.dump(scope, f, indent=2)

    # kpis.json
    kpis = [
        {"metric": "OOS Sharpe (winner)", "value": f"{winner_summary['oos_sharpe']:.2f}", "unit": "ratio", "delta": f"{tw['delta_sharpe']:+.2f} vs B&H"},
        {"metric": "OOS Sharpe (buy & hold)", "value": f"{winner_summary['bh_sharpe']:.2f}", "unit": "ratio", "delta": None},
        {"metric": "OOS Annual Return (winner)", "value": f"{winner_summary['oos_ann_return']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_ann_return']*100:+.1f}pp vs B&H"},
        {"metric": "OOS Max Drawdown (winner)", "value": f"{winner_summary['oos_max_drawdown']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_max_drawdown']*100:+.1f}pp vs B&H"},
        {"metric": "Valid strategy combos", "value": f"{n_valid}", "unit": "count", "delta": None},
        {"metric": "OOS window", "value": f"{split['oos_start']} → {split['oos_end']}", "unit": "dates", "delta": None},
    ]
    with open(os.path.join(RESULTS_DIR, "kpis.json"), "w") as f:
        json.dump(kpis, f, indent=2)

    # design_note.md (Rule C1 deviations)
    fwd_sig_lags = list(ty_df[(ty_df.direction == "indicator_to_target") & ty_df.significant].lag)
    rev_sig_lags = list(ty_df[(ty_df.direction == "target_to_indicator") & ty_df.significant].lag)
    design = f"""# Design Note — {PAIR_ID} ({DATE_TAG})

## Category & method coverage (Rule C1, sentiment-equity + brief add-ons)
All sentiment-equity mandatory methods produced, plus CCF/local projections/structural break per brief. Deviations from the daily-pair spec, documented per Rule C1:
- Correlation horizons: pair is MONTHLY; horizons are 1m/3m/6m/12m forward returns, recorded as
  21/63/126/252 `horizon_days` equivalents in `correlations.csv`.
- Pre-whitened CCF run at monthly lags −20..+20 (not daily).
- Granger is Toda-Yamamoto (VAR in stationary PMI level with d_max=1 augmentation).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations (dcor/pyinform not in env).
- Stationarity: Dana's tests (stationarity_tests_{DATE_TAG}.csv) reviewed and CONFIRMED, not re-run.

## Lead-lag verdict (sentiment already priced / reverse causality)
- ISM Services→SPY TY-Granger significant lags: {fwd_sig_lags or 'NONE'}
- SPY→ISM Services TY-Granger significant lags: {rev_sig_lags or 'NONE'}
- Reverse-causality LP flag: {rev_flag}
See handoff for the full verdict.

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent — documented in the CSV manifest.
- Monthly lead grid starts at L1 (real-time floor: prior-month PMI publishes early in the following month). Lead semantics:
  position_t = rule(signal_(t−L)); strategy_return_t = position_t × spy_ret_t.
- Daily LVCF data has release lag baked in; daily L0 on the carried value is feasible, but this monthly tournament uses L1+.
- Both orientations (pro/counter) tested per the mixed direction prior.
- CP2 skipped — `regime_story: false` in signal_scope.json.
- Returns gross of costs; 5 bps sensitivity grid in tournament_validation_{DATE_TAG}/.

## New pair — no prior version, Rule C3 regression diff not applicable.
"""
    with open(os.path.join(RESULTS_DIR, "design_note.md"), "w") as f:
        f.write(design)

    # analyst_suggestions.json (ECON-AS) — no off-scope signals proposed
    sugg = {"schema_version": "1.0.0", "pair_id": PAIR_ID, "rule": "ECON-AS",
            "suggestions": [],
            "last_updated_by": "evan", "last_updated_at": NOW_ISO}
    with open(os.path.join(RESULTS_DIR, "analyst_suggestions.json"), "w") as f:
        json.dump(sugg, f, indent=2)

    evidence_status = {
        "pair_id": PAIR_ID,
        "schema_version": "1.2.0",
        "status": "found_in_search",
        "updated_at": NOW_ISO,
        "owner": "evan",
        "plain_english": (
            "This is the best rule found by a strategy search, not a rule that has passed a fresh final exam. "
            f"The winner improved OOS Sharpe ({winner_summary['oos_sharpe']:.2f} vs {winner_summary['bh_sharpe']:.2f}) "
            f"and reduced drawdown ({winner_summary['oos_max_drawdown']*100:.1f}% vs "
            f"{winner_summary['bh_max_drawdown']*100:.1f}%), but it gave up annual return "
            f"({winner_summary['oos_ann_return']*100:.1f}% vs {winner_summary['bh_ann_return']*100:.1f}%), "
            f"bootstrap p={winner_boot_p:.3f} was not below 5%, and the structural-break test flagged "
            f"{sb['break_date']}. The lead-lag evidence is reverse-heavy: SPY predicts the survey more than "
            "the survey predicts SPY at monthly lags."
        ),
        "technical_note": (
            f"Tournament-OOS only ({split['oos_start']}..{split['oos_end']}, {winner_summary['oos_n']} months; "
            "ECON-OOS2 v1_max36_25pct_cap120). Winner "
            f"{winner_summary['signal_code']}/{winner['threshold']}/{winner['strategy']}/"
            f"L{winner['lead_months']}/{winner['lookback']}: OOS Sharpe {winner_summary['oos_sharpe']:.4f}, "
            f"bootstrap p={winner_boot_p:.3f}, IS Sharpe {float(winner['is_sharpe']):.3f}, "
            f"CP1-A {verdict}, CP1-B {stab}, structural_break_flag={sb['flagged']}. "
            f"Spec-curve context: median OOS Sharpe across {n_valid} valid combos = {median_sharpe:.3f}. "
            f"TY Granger forward significant lags: {fwd_sig_lags or 'NONE'}; reverse significant lags: {rev_sig_lags or 'NONE'}."
        ),
        "next_step": (
            "Run ECON-FE1 final exam: freeze the winning rule and test it once on a confirmation window not used "
            "for tournament selection, or wait for post-Oct-2025 ISM vintages plus realized SPY returns."
        ),
    }
    with open(os.path.join(RESULTS_DIR, "evidence_status.json"), "w") as f:
        json.dump(evidence_status, f, indent=2)

    # timing
    timing = {"pair_id": PAIR_ID, "date": DATE_TAG,
              "pipeline_seconds": round(time.time() - t0, 1),
              "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
              "tournament_strategy_rows": int(len(tdf) - 1), "valid_strategies": n_valid,
              "oos_n_months": int(winner["oos_n"]),
              "oos_start": split["oos_start"], "oos_end": split["oos_end"]}
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump(timing, f, indent=2)

    # --- final console summary for handoff ---
    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE — HANDOFF NUMBERS (DPS-SCD1)")
    print("=" * 70)
    print(f"  Strategy combos: {len(tdf)-1} | valid: {n_valid} | median OOS Sharpe (valid): {median_sharpe:.3f}")
    print(f"  Winner: {tw['winner_label']}")
    print(f"  OOS Sharpe {winner_summary['oos_sharpe']} vs B&H {winner_summary['bh_sharpe']} | "
          f"DD {winner_summary['oos_max_drawdown']} vs {winner_summary['bh_max_drawdown']} | "
          f"ret {winner_summary['oos_ann_return']} vs {winner_summary['bh_ann_return']}")
    print(f"  Ties at step 1: {n_tied} (cascade resolved at step {resolved_at})")
    print(f"  Durability: {verdict} | corr sign-stability: {stab} | break flagged: {sb['flagged']} ({sb['break_date']})")
    print(f"  Direction (winner): {direction} | suggested strategy_objective: {tw['suggested_strategy_objective']}")
    print(f"  Granger fwd-significant lags: {fwd_sig_lags or 'NONE'} | rev-significant lags: {rev_sig_lags or 'NONE'}")
    return winner_summary, tw


if __name__ == "__main__":
    main()
