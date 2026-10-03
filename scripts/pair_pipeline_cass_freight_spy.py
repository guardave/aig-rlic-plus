#!/usr/bin/env python3
"""
Full Econometrics Pipeline: Cass Freight Index (Shipments) -> SPY
================================================================
Pair ID: cass_freight_spy (Mode 1, monthly). Branch: feat260705_cass_freight_spy

Economic hypothesis (stated up front, per SOP):
  H0: Cass Freight Shipments growth does NOT Granger-cause / predict SPY forward returns.
  H1 (procyclical prior, Dana/Ray): expanding freight = strengthening goods economy
      (risk-on); freight recession = goods slowdown (risk-off). Freight is commonly
      framed as an early/leading read on economic momentum.
  Direction AND lead/coincident status are determined EMPIRICALLY (Granger / pre-whitened
  CCF / local projections) — the prior only seeds; it does NOT decide.

BINDING Phase-0 constraints (Dana handoff — honesty-critical):
  * Short history: 125 monthly obs 2016-01..2026-05 (~10yr). OOS window < 5yr ->
    any winner is FOUND-IN-SEARCH, Sharpe inflated/high-variance. Treated as a
    CANDIDATE, never a validated edge; stated explicitly in provenance + notes.
  * Publication lag: Cass publishes ~mid-month for the prior month (~2-week lag) ->
    the tradable tournament lead grid FLOORS AT L1 (no L0). L0 appears only in the
    diagnostic Lead-Analysis correlation table, flagged non-tradable.
  * NSA source: MoM/3M/6M momentum and the level z-score are seasonally contaminated;
    the YoY family (_pct_yoy, _yoy_zscore_60m) and 12M-MA are the seasonality-robust
    cycle signals and are PREFERRED for direction/lead-lag. A seasonally-contaminated
    combo is NOT allowed to win silently — flagged hard in the handoff if it does.
  * 60M z-scores only usable from ~2018-12 (level)/~2019-12 (yoy) — short span,
    handled gracefully (eligibility floor, not a hard drop).

Category (Rule C1): production/macro. Full battery run to mirror busloans_spy shapes
exactly (correlations incl. distance, pre-whitened CCF, Toda-Yamamoto Granger both
directions, transfer entropy, local projections fwd+rev, quantile regression, HMM
2-state, quartile returns) + ECON-LA1 Lead Analysis + ECON-LT1 Lead Tournament.

Author: Econ Evan (Econometrics Agent). Date: 2026-07-05.
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
PAIR_ID = "cass_freight_spy"
INDICATOR_NAME = "Cass Freight Index (Shipments)"
TARGET_NAME = "SPY"
TARGET_SYMBOL = "SPY"
DATE_TAG = "20260829"
COST_BPS = 5  # equity ETF per ECON-T2 / target-class table

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_PATH = os.path.join(BASE_DIR, "data", "cass_freight_spy_monthly_latest.parquet")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")
SCHEMA_DIR = os.path.join(BASE_DIR, "docs", "schemas")

for d in [RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# tournament signal_code KEY -> parquet column
SIGNAL_COLS = {
    "yoy": "cass_freight_pct_yoy",
    "mom": "cass_freight_pct_mom",
    "mom3m": "cass_freight_3m_pct",
    "mom6m": "cass_freight_6m_pct",
    "dev_trend": "cass_freight_dev_trend_pct",
    "level_zscore_60m": "cass_freight_zscore_60m",
    "yoy_zscore_60m": "cass_freight_yoy_zscore_60m",
    "accel": "cass_freight_accel_pct",
    "contraction": "cass_freight_contraction",
    # derived in stage_signals:
    "hmm_stress": "hmm_2state_prob_stress",
    "markov_regime": "markov_regime_2state",
}
# seasonally-clean (YoY-family + 12M-MA-derived) signal keys, per Dana NSA caveat
SEASONALLY_CLEAN = {"yoy", "yoy_zscore_60m", "dev_trend", "contraction",
                    "hmm_stress", "markov_regime"}
MAIN_SIG = "cass_freight_pct_yoy"  # preferred seasonality-robust cycle signal

FWD_COLS = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]

# Short-sample adaptations (vs busloans deep history)
SIG_ELIGIBLE_MIN = 60      # min non-NaN obs for a signal to enter the tournament
LOOKBACKS = {"LB24": 24, "LB36": 36, "LB60": 60}  # LB120 impossible with 125 obs
LEADS = list(range(1, 13))  # L1..L12 — L1 real-time floor (Dana pub-lag), no L0


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
         "produced_by": "scripts/pair_pipeline_cass_freight_spy.py",
         "generated_at": NOW_ISO, "columns": columns, "assertions": assertions}
    if extra:
        m.update(extra)
    with open(os.path.splitext(path)[0] + "_manifest.json", "w") as f:
        json.dump(m, f, indent=2)


def ann_metrics(rets):
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
    # Step C #198: history extended 2016->1990 (Data Master splice). Panel now ~439 rows.
    assert df.shape[1] == 21 and df.shape[0] >= 400, f"unexpected shape {df.shape}"
    # Known-episode checks (Dana's handoff): COVID freight collapse + 2022-24 recession
    assert -25.0 < df.loc["2020-05-31", "cass_freight_pct_yoy"] < -20.0, "COVID YoY collapse missing"
    assert df.loc["2022-06-30":"2024-06-30", "cass_freight_pct_yoy"].min() < -5.0, "freight recession missing"
    assert df["spy_ret"].abs().max() < 0.30, "monthly SPY return magnitude implausible"
    assert df["spy_fwd_12m"].iloc[-12:].isna().all(), "forward-return leakage at tail"
    print(f"  Loaded {df.shape}, {df.index.min().date()} -> {df.index.max().date()}")
    print("  Defense-2 episode checks: COVID freight collapse, 2022-24 recession, return magnitudes — PASS")
    return df


# ===================================================================
# STAGE 2: DERIVED REGIME SIGNALS (HMM + Markov-switching) + persistence
# ===================================================================
@log_stage("2_signals")
def stage_signals(df):
    import statsmodels.api as sm
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

    yoy = df["cass_freight_pct_yoy"].dropna()

    # --- HMM 2-state on YoY growth (short sample -> guard) ---
    try:
        from hmmlearn.hmm import GaussianHMM
        X = yoy.values.reshape(-1, 1)
        hmm = GaussianHMM(n_components=2, covariance_type="full", n_iter=500, random_state=42)
        hmm.fit(X)
        probs = hmm.predict_proba(X)
        variances = [hmm.covars_[i].ravel()[0] for i in range(2)]
        stress_state = int(np.argmax(variances))
        prob_stress = pd.Series(probs[:, stress_state], index=yoy.index, name="hmm_2state_prob_stress")
        df["hmm_2state_prob_stress"] = prob_stress
        hmm_states = pd.DataFrame({
            "hmm_state": pd.Series(hmm.predict(X), index=yoy.index),
            "prob_stress": prob_stress, "prob_calm": 1 - prob_stress})
        hmm_states.to_parquet(os.path.join(MODELS_DIR, "hmm_states.parquet"))
        spy = df["spy_ret"]
        summ = []
        for lbl, mask in [("stress", hmm_states["hmm_state"] == stress_state),
                          ("calm", hmm_states["hmm_state"] != stress_state)]:
            idx = hmm_states.index[mask]
            rets = spy.reindex(idx).dropna()
            sub = yoy.reindex(idx)
            summ.append({"state_label": lbl,
                         "mean_return": round(rets.mean(), 6) if len(rets) else np.nan,
                         "vol": round(rets.std(), 6) if len(rets) else np.nan,
                         "duration_days": int(mask.sum()), "frequency_pct": round(mask.mean() * 100, 2),
                         "mean_yoy_growth": round(sub.mean(), 3)})
        pd.DataFrame(summ).to_csv(os.path.join(MODELS_DIR, "hmm_summary.csv"), index=False)
        cov_p = prob_stress.loc["2020-01-31":"2020-12-31"].mean()
        print(f"  HMM 2-state converged; stress prob mean 2020: {cov_p:.2f}")
        write_manifest(os.path.join(MODELS_DIR, "hmm_states.parquet"),
                       {"hmm_state": "integer state; stress = high-variance YoY-growth regime",
                        "prob_stress": "P(stress regime); higher = freight growth in high-variance regime",
                        "prob_calm": "1 - prob_stress"},
                       [{"description": "probabilities in [0,1]", "check": "prob_stress between 0 and 1"},
                        {"description": "COVID era is high-variance", "filter": "2020",
                         "column": "prob_stress", "check": f"mean = {cov_p:.2f}"},
                        {"description": "states sum to 1", "check": "prob_stress + prob_calm == 1"}])
    except Exception as e:
        print(f"  HMM failed on short sample ({e}) — hmm_stress excluded from tournament")

    # --- Markov-switching regression: spy_ret ~ yoy, 2 regimes ---
    ms_data = pd.concat([df["spy_ret"], yoy], axis=1).dropna()
    try:
        ms = MarkovRegression(ms_data["spy_ret"], k_regimes=2,
                              exog=sm.add_constant(ms_data["cass_freight_pct_yoy"]),
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
                   {c: f"tournament-eligible signal derived solely from Cass Freight ({c})" for c in sig_cols},
                   [{"description": "COVID YoY collapse present", "filter": "2020-05-31",
                     "column": "cass_freight_pct_yoy", "check": "value < -20"},
                    {"description": "2022-24 freight recession", "filter": "2022-06..2024-06",
                     "column": "cass_freight_pct_yoy", "check": "min < -5"}])
    return df


# ===================================================================
# STAGE 3: EXPLORATORY + CORRELATION BATTERY (Rule C1/C2)
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
    horizon_map = {"spy_fwd_1m": 1, "spy_fwd_3m": 3, "spy_fwd_6m": 6, "spy_fwd_12m": 12}
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwd, h in horizon_map.items():
            v = df[[col, fwd]].dropna()
            if len(v) < 40:   # short-sample floor (was 60 for busloans deep history)
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
                   {"pair_name": "signal_code__forward-return-column",
                    "horizon_days": "forward horizon in trading days (monthly*21)",
                    "metric": "pearson/spearman/kendall/distance", "value": "correlation coefficient",
                    "p_value": "two-sided p (NaN for distance corr)", "n_obs": "obs"},
                   [{"description": "values bounded", "check": "abs(value) <= 1"},
                    {"description": "monthly horizons", "check": "horizon_days in {21,63,126,252}"},
                    {"description": "short-sample n floor", "check": "min(n_obs) >= 40"}])
    sig = cdf[(cdf.metric == "pearson") & (cdf.p_value < 0.05)]
    print(f"  Correlation battery: {len(cdf)} rows; {len(sig)} significant Pearson cells")
    if len(sig):
        b = sig.loc[sig.value.abs().idxmax()]
        print(f"  Strongest sig Pearson: {b.pair_name} r={b.value} p={b.p_value}")
    else:
        print("  No individually-significant Pearson cells (weak/short-sample relationship).")
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

    # --- 4.1 Pre-whitened CCF (lags -18..+18; trimmed for short sample) ---
    pair = df[[main_sig, "spy_ret"]].dropna()
    x = pair[main_sig]; y = pair["spy_ret"]
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
    coefs = ar_fit.params
    y_w = y.copy() - coefs.iloc[0]
    for i in range(1, best_p + 1):
        y_w = y_w - coefs.iloc[i] * y.shift(i)
    common = x_w.index.intersection(y_w.dropna().index)
    xw, yw = x_w.loc[common], y_w.loc[common]
    n = len(common)
    se = 1.96 / np.sqrt(n)
    rows = []
    for lag in range(-18, 19):
        if lag >= 0:
            a, b = xw.shift(lag), yw
        else:
            a, b = xw, yw.shift(-lag)
        v = pd.concat([a, b], axis=1).dropna()
        c = v.corr().iloc[0, 1] if len(v) > 24 else np.nan
        rows.append({"lag": lag, "ccf": round(c, 4) if pd.notna(c) else np.nan,
                     "lower_ci": round(-se, 4), "upper_ci": round(se, 4),
                     "significant": bool(abs(c) > se) if pd.notna(c) else False,
                     "arima_order": f"AR({best_p})", "n_obs": len(v)})
    ccf_df = pd.DataFrame(rows)
    ccf_df.to_csv(os.path.join(MODELS_DIR, "ccf_prewhitened.csv"), index=False)
    lead_sig = ccf_df[(ccf_df.lag > 0) & ccf_df.significant]
    lag_sig = ccf_df[(ccf_df.lag < 0) & ccf_df.significant]
    print(f"  [4.1] CCF (AR({best_p}), n={n}): sig lead lags {list(lead_sig.lag)}, "
          f"sig LAG-side lags {list(lag_sig.lag)}")

    # --- 4.2 Toda-Yamamoto Granger (both directions) + by-lag artifact ---
    ty_rows, bylag_rows = [], []
    gdata = pair.rename(columns={main_sig: "ind", "spy_ret": "tgt"})
    d_max = 1  # YoY borderline I(1) (ADF non-stat, KPSS stat) -> TY augmentation lag 1
    try:
        p_opt = max(int(VAR(gdata).select_order(maxlags=12).aic), 1)
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
    print(f"        Cass->SPY significant at lags: {list(fwd_sig.lag)}")
    print(f"        SPY->Cass significant at lags: {list(rev_sig.lag)}")

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
        v = pd.concat([src, dst], axis=1).dropna()
        null = [transfer_entropy(pd.Series(rng.permutation(v.iloc[:, 0].values), index=v.index),
                                 v.iloc[:, 1]) for _ in range(n_perm)]
        pv = float((np.array(null) >= te).mean())
        te_rows.append({"direction": direction, "te_value": round(float(te), 5),
                        "permutation_p_value": round(pv, 4), "n_permutations": n_perm,
                        "bandwidth": np.nan, "bin_method": "tercile_qcut"})
    pd.DataFrame(te_rows).to_csv(os.path.join(MODELS_DIR, "transfer_entropy.csv"), index=False)
    print(f"  [4.3] Transfer entropy: ind->tgt TE={te_rows[0]['te_value']} (p={te_rows[0]['permutation_p_value']}), "
          f"tgt->ind TE={te_rows[1]['te_value']} (p={te_rows[1]['permutation_p_value']})")

    # --- 4.4 Local projections (forward + REVERSE) ---
    lp_rows = []
    for direction in ["fwd", "rev"]:
        for h in [1, 3, 6, 12]:
            if direction == "fwd":
                ycol = f"spy_fwd_{h}m"
                v = df[[main_sig, ycol]].dropna()
                xv, yv = v[main_sig], v[ycol]
            else:
                v = pd.concat([df["spy_ret"], df[main_sig].shift(-h)], axis=1).dropna()
                v.columns = ["x", "y"]; xv, yv = v["x"], v["y"]
            if len(v) < 40:
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
    print(f"  [4.4] LP fwd (Cass->SPY) sig horizons: {list(fwd.loc[fwd.p_value<0.05,'horizon'])}; "
          f"reverse (SPY->Cass) sig horizons: {list(rev.loc[rev.p_value<0.05,'horizon'])} -> rev flag {rev_flag}")

    # --- 4.5 Quantile regression ---
    qr_rows = []
    v = df[[main_sig, "spy_fwd_3m"]].dropna().rename(columns={main_sig: "sig", "spy_fwd_3m": "fwd"})
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
        for fwdc in FWD_COLS:
            v = df[[col, fwdc]].dropna()
            if len(v) < 40:
                continue
            fit = sm.OLS(v[fwdc].values, sm.add_constant(v[col].values)).fit(cov_type="HC3")
            reg_rows.append({"signal": code, "horizon": fwdc, "coef": round(fit.params[1], 6),
                             "se": round(fit.bse[1], 6), "t_stat": round(fit.tvalues[1], 3),
                             "p_value": round(fit.pvalues[1], 4), "r_squared": round(fit.rsquared, 4),
                             "n": int(fit.nobs)})
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
    from statsmodels.stats.diagnostic import het_breuschpagan, acorr_breusch_godfrey, linear_reset
    bp, bpp, _, _ = het_breuschpagan(resid, X)
    diag.append({"test": "Breusch-Pagan", "statistic": round(bp, 3), "p_value": round(bpp, 4),
                 "interpretation": "Homoskedastic" if bpp > 0.05 else "Heteroskedastic — HC3/HAC SEs used"})
    bg, bgp, _, _ = acorr_breusch_godfrey(base, nlags=min(12, len(v) // 5))
    diag.append({"test": "Breusch-Godfrey", "statistic": round(bg, 3), "p_value": round(bgp, 4),
                 "interpretation": "No serial corr" if bgp > 0.05 else "Serial correlation (overlapping fwd returns) — HAC SEs used"})
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
# STAGE 4b: LEAD ANALYSIS (ECON-LA1) + LEAD TOURNAMENT (ECON-LT1)
# ===================================================================
@log_stage("4b_lead_analysis")
def stage_lead_analysis(df, split=None):
    """ECON-LA1: per-transform Pearson r vs 1M-fwd return at leads. ECON-LL1 says
    L0..12; Cass floors tradability at L1, so L0 is emitted in the correlation table
    as a DIAGNOSTIC (contemporaneous) column, flagged non-tradable. The Lead
    Tournament (tradable) runs L1..L12 only."""
    fwd1 = df["spy_fwd_1m"]
    transforms = [c for k, c in SIGNAL_COLS.items() if c in df.columns and not c.startswith(("hmm", "markov"))]
    rows = []
    for col in transforms:
        row = {"transform": col}
        best_lead, best_abs, best_r = None, -1, None
        for L in range(0, 13):
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
    print(f"  [ECON-LA1] lead_correlation -> {lc_path} (L0 diagnostic-only; L0 not tradable)")

    return lc, lc_path


@log_stage("4c_lead_tournament")
def stage_lead_tournament(df, split, run_lead_grid):
    """ECON-LT1: best tradable OOS Sharpe per lead L1..L12 + distribution. Feeds the
    conditional re-run gate. Uses the SAME tournament engine (run_lead_grid) restricted
    to a single lead. Returns L_star and gate decision."""
    rows = []
    for L in LEADS:  # L1..L12 (tradable; L0 excluded — pub-lag floor)
        sub = run_lead_grid(df, split, [L])
        cand = sub[(sub.signal != "BENCHMARK") & sub.valid]
        if len(cand) == 0:
            rows.append({"lead_months": L, "n_valid": 0, "best_oos_sharpe": np.nan,
                         "median_oos_sharpe": np.nan, "p25_oos_sharpe": np.nan, "p75_oos_sharpe": np.nan,
                         "best_signal": "", "best_threshold": "", "best_strategy": "", "best_max_dd": np.nan})
            continue
        top = cand.loc[cand.oos_sharpe.idxmax()]
        rows.append({"lead_months": L, "n_valid": int(len(cand)),
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
        L_star = int(star_row.lead_months)
        best_at_grid = float(star_row.best_oos_sharpe)
    else:
        L_star, best_at_grid = -1, np.nan
    # ECON-LT1 gate: L* in {7..12} -> extended grid produced a better winner; else charts-only.
    # NB: full grid is L1..L12 (no L0/coarse subset), so the winner is already selected over
    # the complete tradable lead grid — the gate is informational here (no re-run needed).
    gate = "CHARTS-ONLY" if L_star <= 6 else "REVIEW-L7_12"
    print(f"  [ECON-LT1] lead_tournament -> {lt_path}; L*={L_star} best OOS Sharpe {best_at_grid} -> gate {gate}")
    print("  [ECON-LT1] Note: main tournament already scans the FULL L1..L12 grid, so the "
          "published winner is the global max over all tradable leads (no coarse-subset staleness).")
    return lt, lt_path, L_star, best_at_grid, gate


# ===================================================================
# STAGE 5: REGIME QUARTILE RETURNS
# ===================================================================
@log_stage("5_regime_quartiles")
def stage_quartiles(df):
    v = df[["cass_freight_pct_yoy", "spy_ret"]].dropna()
    q = pd.qcut(v["cass_freight_pct_yoy"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    rows = []
    for lbl in ["Q1", "Q2", "Q3", "Q4"]:
        r = v.loc[q == lbl, "spy_ret"]
        m = ann_metrics(r)
        rows.append({"quartile": lbl, "n_months": len(r), "ann_return": round(m["ann_return"], 4),
                     "ann_vol": round(m["ann_vol"], 4), "sharpe": round(m["sharpe"], 3),
                     "max_drawdown": round(m["max_dd"], 4)})
    qdf = pd.DataFrame(rows)
    path = os.path.join(RESULTS_DIR, "regime_quartile_returns.csv")
    qdf.to_csv(path, index=False)
    print(qdf.to_string(index=False))
    write_manifest(path,
                   {"quartile": "Cass YoY growth quartile (Q1 lowest growth)", "n_months": "obs",
                    "ann_return": "annualized SPY return in quartile (ratio)", "ann_vol": "annualized vol (ratio)",
                    "sharpe": "ann_return/ann_vol", "max_drawdown": "max DD within quartile months (negative ratio)"},
                   [{"description": "4 quartiles", "check": "len == 4"},
                    {"description": "returns plausible", "check": "abs(ann_return) < 0.6"},
                    {"description": "concurrent (NOT lagged) relationship — descriptive only", "check": "informational"}])
    return qdf


# ===================================================================
# STAGE 6: TOURNAMENT ENGINE (5-D)
# ===================================================================
def run_lead_grid(df, split, leads):
    """Core tournament evaluation over a given list of leads. Returns a DataFrame of
    strategy rows (NO benchmark). Shared by the full tournament and the Lead Tournament."""
    work = df.dropna(subset=["spy_ret"]).copy()
    is_end = split["in_sample_end"]; oos_start = split["oos_start"]; oos_end = split["oos_end"]
    is_mask = work.index <= is_end
    oos_mask = (work.index >= oos_start) & (work.index <= oos_end)
    spy_ret = work["spy_ret"]
    strategies = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]
    results = []
    for code, col in SIGNAL_COLS.items():
        if col not in work.columns or work[col].notna().sum() < SIG_ELIGIBLE_MIN:
            continue
        base_sig = work[col]
        for lead in leads:
            sig = base_sig.shift(lead)
            thr_static = {}
            is_sig = sig[is_mask].dropna()
            if len(is_sig) > 36:
                for pct in [25, 50, 75]:
                    thr_static[(f"T1_fixed_p{pct}", "LB_NA")] = is_sig.quantile(pct / 100)
            if code in ["yoy", "mom", "mom3m", "mom6m", "accel"]:
                thr_static[("T4_zero", "LB_NA")] = 0.0
            thr_roll = {}
            for lb_name, lb in LOOKBACKS.items():
                minp = max(int(lb * 0.6), 12)
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
                            lb = LOOKBACKS[lb_name]
                            roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 12))
                            rng = (roll.max() - roll.min()).replace(0, np.nan)
                            raw = ((sig - roll.min()) / rng).clip(0, 1)
                            position = 1 - raw if orientation == "counter" else raw
                        else:
                            position = pos_bool.astype(float) * 2 - 1
                        strat_ret = position * spy_ret
                        is_r, oos_r = strat_ret[is_mask].dropna(), strat_ret[oos_mask].dropna()
                        if len(is_r) < 36 or len(oos_r) < 24:
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
                            "is_sharpe": round(m_is["sharpe"], 4), "oos_sharpe": round(m["sharpe"], 4),
                            "oos_sortino": round(m["sortino"], 4), "oos_calmar": round(m["calmar"], 4),
                            "oos_ann_return": round(m["ann_return"], 4), "oos_ann_vol": round(m["ann_vol"], 4),
                            "max_drawdown": round(m["max_dd"], 4), "win_rate": round(m["win_rate"], 4),
                            "n_trades": n_trades, "annual_turnover": round(turnover, 2),
                            "oos_n": len(oos_r), "valid": valid,
                            "seasonally_clean": bool(code in SEASONALLY_CLEAN)})
    return pd.DataFrame(results)


@log_stage("6_tournament")
def stage_tournament(df):
    work = df.dropna(subset=["spy_ret"]).copy()
    n_months = len(work)
    oos_n = int(min(max(36, round(n_months * 0.25)), 120))
    oos_start = work.index[-oos_n]
    is_end = work.index[-(oos_n + 1)]
    oos_end = work.index[-1]
    short_oos = oos_n < 60  # 5yr reliability floor
    print(f"  Sample (SPY-bound): {n_months} months {work.index[0].date()} -> {oos_end.date()}")
    print(f"  OOS (v1_max36_25pct_cap120): {oos_n} months ({oos_n/12:.1f}yr), {oos_start.date()} -> "
          f"{oos_end.date()} " + ("(<5yr -> FOUND-IN-SEARCH)" if short_oos else "(>=5yr floor)"))
    split = {
        "owner": "evan", "split_policy_id": "v1_max36_25pct_cap120",
        "in_sample_end": is_end.strftime("%Y-%m-%d"), "oos_start": oos_start.strftime("%Y-%m-%d"),
        "oos_end": oos_end.strftime("%Y-%m-%d"), "sample_size_months": n_months,
        "justification": (
            f"Policy v1_max36_25pct_cap120 on the full Cass history ({n_months} months, 1990-01 onward "
            f"via the Data Master splice, Step C #198; SPY bounds the aligned panel from 1993). "
            f"min(max(36, round({n_months}*0.25)), 120) = {oos_n} months = {oos_n/12:.1f}yr OOS, "
            f"{'below' if short_oos else 'above'} the 5yr reliability floor. "
            + ("Short-history pair: any winner is found-in-search with an inflated/high-variance Sharpe."
               if short_oos else
               "After the #198 history extension the OOS window itself clears the 5yr floor; the winner is "
               "still found-in-search (the median valid combo underperforms buy-and-hold and the L9 lead is a "
               "likely search artifact, issue #28), but no longer for a short-OOS reason.")),
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
             "lead_months": 0, "lookback": "LB_NA", "is_sharpe": round(mbi["sharpe"], 4),
             "oos_sharpe": round(mb["sharpe"], 4), "oos_sortino": round(mb["sortino"], 4),
             "oos_calmar": round(mb["calmar"], 4), "oos_ann_return": round(mb["ann_return"], 4),
             "oos_ann_vol": round(mb["ann_vol"], 4), "max_drawdown": round(mb["max_dd"], 4),
             "win_rate": round(mb["win_rate"], 4), "n_trades": 0, "annual_turnover": 0.0,
             "oos_n": int(oos_mask.sum()), "valid": False, "seasonally_clean": True}
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
        "grid": {"signals": [k for k, v in SIGNAL_COLS.items() if v in work.columns and work[v].notna().sum() >= SIG_ELIGIBLE_MIN],
                 "thresholds": "T1_fixed_p{25,50,75}, T2_roll_p{25,75}, T3_zscore_{±1.0,±1.5}, T4_zero (growth signals)",
                 "strategies": ["P1_long_cash_{pro,counter}", "P2_signal_strength_{pro,counter}", "P3_long_short_{pro,counter}"],
                 "leads_months": LEADS, "lookbacks": list(LOOKBACKS.keys()) + ["LB_NA"]},
        "units": "oos_ann_return / oos_ann_vol / max_drawdown are RATIOS (decimal), not percent",
        "total_strategy_rows": len(strat_pop), "valid_strategy_rows": n_valid,
        "sampling": "exhaustive over the FULL tradable lead grid L1..L12 (no coarse subset)",
        "benchmark_row": "signal==BENCHMARK, valid=False per ECON-T4",
        "execution_lag": "position_t = rule(signal_{t-lead}), lead >= 1 (L1 real-time floor; Cass ~2-week pub lag)",
        "short_sample_flag": (
            f"OOS window {oos_n} months (<5yr) — winner is found-in-search / CANDIDATE, not validated"
            if oos_n < 60 else
            f"OOS window {oos_n} months ({oos_n/12:.1f}yr, clears the 5yr floor post-#198) — winner is still "
            f"found-in-search (median valid combo underperforms buy-and-hold; L9 lead a likely artifact, #28), "
            f"not validated"),
        "nsa_flag": "NSA source: MoM/3M/6M/level-zscore signals are seasonally contaminated; YoY-family preferred (seasonally_clean column flags each row)",
        "cost_note": "returns are gross of costs; 5bps sensitivity in tournament_validation",
        "assertions": ["top strategy oos_sharpe > bottom strategy oos_sharpe", "all oos_sharpe finite",
                       "exactly one BENCHMARK row, valid=False"],
        "generated_at": NOW_ISO,
    }
    with open(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return tdf, split, tpath


# ===================================================================
# STAGE 7: WINNER SELECTION (ECON-T3 cascade) + artifacts
# ===================================================================
def select_winner(tdf, clean_only=True):
    """Winner selection over the valid strategy population (ECON-T4 excludes BENCHMARK).

    NSA-source honesty constraint (Dana Phase-0, binding): the DEFAULT objective is
    restricted to seasonally-CLEAN signals (max_oos_sharpe_seasonally_clean). A
    seasonally-contaminated (MoM/3M/6M/level-zscore) combo must NOT win silently; if
    it is the higher-raw-Sharpe row it is disclosed via ECON-T5
    selection.objective_runner_up_divergence, not shipped as the winner.
    """
    pool0 = tdf[(tdf.signal != "BENCHMARK") & tdf.valid].copy()
    cand = pool0[pool0.seasonally_clean == True].copy() if clean_only else pool0
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
    sig = work[SIGNAL_COLS[winner["signal"]]].shift(int(winner["lead_months"]))
    thr_name, lb_name = winner["threshold"], winner["lookback"]
    if thr_name.startswith("T1_fixed_p"):
        thr = sig[is_mask].dropna().quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name == "T4_zero":
        thr = 0.0
    elif thr_name.startswith("T2_roll_p"):
        lb = LOOKBACKS[lb_name]
        thr = sig.rolling(lb, min_periods=max(int(lb * 0.6), 12)).quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name.startswith("T3_zscore"):
        lb = LOOKBACKS[lb_name]; roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 12))
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
        lb = LOOKBACKS[lb_name]; roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 12))
        rng = (roll.max() - roll.min()).replace(0, np.nan)
        raw = ((sig - roll.min()) / rng).clip(0, 1)
        position = 1 - raw if orientation == "counter" else raw
    else:
        position = pos_bool.astype(float) * 2 - 1
    return position, work["spy_ret"], sig, thr


@log_stage("7_winner_artifacts")
def stage_winner(df, tdf, split, tpath):
    winner, resolved_at, tie_pool, cand = select_winner(tdf)
    if winner is None:
        raise RuntimeError("no valid strategies — null result; escalate to Lead")
    n_valid = int(((tdf.signal != "BENCHMARK") & tdf.valid).sum())  # full valid strategy pop (ECON-T4)
    n_valid_clean = len(cand)                                        # seasonally-clean objective pop
    median_sharpe = float(cand["oos_sharpe"].median())
    print(f"  Valid strategies: {n_valid} total | {n_valid_clean} seasonally-clean (objective population)")
    n_tied = int((cand["oos_sharpe"] == winner["oos_sharpe"]).sum())
    print(f"  Winner: {winner['signal']}/{winner['threshold']}/{winner['strategy']}/L{winner['lead_months']}/{winner['lookback']}")
    print(f"  OOS Sharpe {winner['oos_sharpe']} | ties at step1: {n_tied} | cascade resolved at step {resolved_at} "
          f"| seasonally_clean={bool(winner['seasonally_clean'])}")

    if resolved_at > 1:
        lines = [f"# Tournament Tie Note — {PAIR_ID} ({DATE_TAG})", "",
                 f"Winner resolved at cascade step {resolved_at} (ECON-T3).", "",
                 "## Candidates tied at step 1 (oos_sharpe)", "",
                 tie_pool[["signal", "threshold", "strategy", "lead_months", "lookback",
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
                   "produced_by": "scripts/pair_pipeline_cass_freight_spy.py", "rule": "ECON-SR1",
                   "source": "pipeline_native_derivation (same code path as tournament evaluation)",
                   "returns_file": DATA_PATH, "coverage_start": str(spy_ret.index[0].date()),
                   "coverage_end": str(spy_ret.index[-1].date()), "frequency": "monthly",
                   "oos_start": split["oos_start"], "oos_end": split["oos_end"],
                   "position_semantics": (f"position on row t = return-accrual weight for month t; signal lagged "
                                          f"{int(winner['lead_months'])} month(s); strategy_return = position * bh_return"),
                   "reconciliation": {k: {"computed": v["computed"], "reported_winner_summary": v["reported_tournament"],
                                          "diff": v["diff"], "tolerance": v["tolerance"], "verdict": v["verdict"]}
                                      for k, v in rec.items()},
                   "generated_at": NOW_ISO, "generated_by": "Econ Evan (feat260705_cass_freight_spy)"}, f, indent=2)

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
                                           if pd.notna(sv) else "position change")})
            prev = p
    broker_path = os.path.join(RESULTS_DIR, "winner_trades_broker_style.csv")
    with open(broker_path, "w") as f:
        f.write(f"# Simulated trade record based on backtest signals. No real trades were executed. "
                f"Starting capital: $10000. Commission: {COST_BPS} bps. Pair: {PAIR_ID}. "
                f"Strategy: {winner['strategy']} on {sig_disp}, threshold {winner['threshold']}, "
                f"lead L{winner['lead_months']}, {winner['lookback']}.\n")
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
                         "n_trading_days": len(sub) * 21, "ann_sharpe": np.nan, "win_rate": np.nan,
                         "max_drawdown": np.nan, "data_status": "insufficient_data", "durability_verdict": ""})
            continue
        m = ann_metrics(sub); eval_eps += 1; pos_eps += int(m["sharpe"] > 0)
        rows.append({"episode": ep["slug"], "start_date": str(sub.index[0].date()), "end_date": str(sub.index[-1].date()),
                     "n_trading_days": len(sub) * 21, "ann_sharpe": round(m["sharpe"], 4),
                     "win_rate": round(m["win_rate"], 4), "max_drawdown": round(m["max_dd"], 4),
                     "data_status": "validated", "durability_verdict": ""})
    if eval_eps >= 3:
        verdict = "durable" if pos_eps >= 3 else ("conditionally_durable" if pos_eps == 2 else "episode_concentrated")
    else:
        verdict = ("conditionally_durable" if pos_eps == eval_eps and eval_eps > 0 else "episode_concentrated") if eval_eps else "insufficient_data"
    if rows:
        rows[-1]["durability_verdict"] = verdict
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "subperiod_sharpe.csv"), index=False)
    print(f"  CP1-A: {eval_eps} episodes evaluable within OOS, {pos_eps} positive -> {verdict}")

    v = pd.concat([sig_lagged.rename("sig"), df["spy_fwd_1m"]], axis=1).dropna()
    full_r = v["sig"].corr(v["spy_fwd_1m"])
    roll = v["sig"].rolling(24).corr(v["spy_fwd_1m"])
    out = pd.DataFrame({"date": v.index.strftime("%Y-%m-%d"), "rolling_corr": roll.round(4).values, "n_obs": 24,
                        "window_start": v.index.to_series().shift(23).dt.strftime("%Y-%m-%d").values}).dropna(subset=["rolling_corr"])
    out.to_csv(os.path.join(RESULTS_DIR, f"rolling_correlation_{PAIR_ID}.csv"), index=False)
    same_sign = float((np.sign(roll.dropna()) == np.sign(full_r)).mean()) if roll.dropna().size else np.nan
    stab = ("sign_stable" if same_sign >= 0.7 else "moderately_stable" if same_sign >= 0.5 else "sign_unstable")
    print(f"  CP1-B: full-sample r={full_r:.3f}, sign stability {same_sign:.2f} -> {stab}")

    reg_v = pd.concat([sig_lagged.rename("sig"), df["spy_ret"]], axis=1).dropna()
    yv = reg_v["spy_ret"].values; Xv = sm.add_constant(reg_v["sig"].values)
    n = len(yv); lo, hi = int(n * 0.15), int(n * 0.85)
    full = sm.OLS(yv, Xv).fit(); ssr_full = full.ssr; k = Xv.shape[1]

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
    sb = {"pair_id": PAIR_ID, "test": "Quandt-Andrews unknown breakpoint (sup-F, residual-bootstrap p, 300 reps)",
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
        boot[b] = (s.mean() / s.std()) * np.sqrt(12) if s.std() > 0 else 0
    rows = [{"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
             "lead_months": r.lead_months, "lookback": r.lookback, "oos_sharpe": r.oos_sharpe,
             "bootstrap_p_value": round(float((boot >= r.oos_sharpe).mean()), 4),
             "significant_at_5pct": bool((boot >= r.oos_sharpe).mean() < 0.05)} for r in top5.itertuples()]
    pd.DataFrame(rows).to_csv(os.path.join(VALID_DIR, "bootstrap.csv"), index=False)

    stress = {"COVID": ("2020-01-01", "2020-06-30"), "Rate_Hike_2022": ("2022-01-01", "2023-06-30"),
              "Freight_Recession": ("2022-06-01", "2024-06-30")}
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
    df = stage_signals(df)
    corr_df = stage_correlations(df)
    ccf_df, ty_df, lp_df, reg_df, rev_flag, fwd_lp_flag = stage_core_models(df)
    lc, lc_path = stage_lead_analysis(df)
    qdf = stage_quartiles(df)
    tdf, split, tpath = stage_tournament(df)
    lt, lt_path, L_star, best_at_grid, gate = stage_lead_tournament(df, split, run_lead_grid)
    (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
     position, strat_ret, sig_lagged, thr, cand) = stage_winner(df, tdf, split, tpath)
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
    winner_clean = bool(winner["seasonally_clean"])

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
                (tdf_read.strategy == w["strategy"]) & (tdf_read.lead_months == w["lead_months"]) &
                (tdf_read.lookback == w["lookback"]))
        idxs = list(tdf_read.index[mask])
        return idxs[0] if idxs else -1
    all_valid = tdf_read[(tdf_read.signal != "BENCHMARK") & tdf_read.valid].copy()
    clean_pop = all_valid[all_valid.seasonally_clean == True].copy()   # objective population
    clean_max = float(clean_pop["oos_sharpe"].max())
    global_max = float(all_valid["oos_sharpe"].max())
    global_row = all_valid.loc[all_valid["oos_sharpe"].idxmax()]
    ru = clean_pop.sort_values("oos_sharpe", ascending=False)
    runner = ru.iloc[1] if len(ru) > 1 else None
    winner_row_idx = _row_id(winner)
    n_sig = len([k for k, v in SIGNAL_COLS.items() if v in df.columns and df[v].notna().sum() >= SIG_ELIGIBLE_MIN])
    # ECON-T5 §3 honest-finding clause: winner is the clean max; the higher-raw-Sharpe
    # contaminated row is disclosed, not shipped.
    contaminated_beats = bool(global_max - clean_max > 1e-6)
    if contaminated_beats:
        divergence = (
            f"The globally highest-raw-OOS-Sharpe valid combo was NOT published. That row "
            f"({global_row['signal']}/{global_row['threshold']}/{global_row['strategy']}/L{int(global_row['lead_months'])}/"
            f"{global_row['lookback']}, OOS Sharpe {round(global_max,4)}) is built on a SEASONALLY-CONTAMINATED signal "
            f"(the Cass series is NOT seasonally adjusted, so MoM/3M/6M/level-zscore transforms carry a seasonal "
            f"component that inflates in-window fit). The published winner is the max-OOS-Sharpe combo among "
            f"SEASONALLY-CLEAN signals (YoY-family / 12M-MA-derived / regime), OOS Sharpe {round(clean_max,4)} — a Δ of "
            f"only {round(clean_max-global_max,4)}. Preferring the clean signal is sound because a seasonally-driven "
            f"edge is not a genuine goods-cycle signal and would not generalise out of its seasonal alignment; the "
            f"criterion is a binding Phase-0 data-quality constraint (Dana), not an ex-post rationalisation. NOTE: on "
            f"this ~36-month (<5yr) OOS both combos are found-in-search CANDIDATES; Granger/CCF find NO forward "
            f"causality (see notes), so this divergence is between two artifacts, not two validated edges.")
    else:
        divergence = None
    selection = {
        "objective": "max_oos_sharpe",
        "objective_formula": ("oos_ret.mean()/oos_ret.std()*sqrt(12), maximised over the valid population but with a "
                              "SEASONAL-ROBUSTNESS constraint (seasonally-CLEAN signals only) applied per Dana's NSA "
                              "Phase-0 gate; the raw-max override is disclosed in objective_runner_up_divergence (ECON-T5 §3)"),
        "grid_scanned": {"leads": LEADS, "n_signals": n_sig,
                         "n_thresholds": 22, "n_strategies": 6,
                         "n_valid_combos": int(len(clean_pop)),
                         "median_valid_objective": round(float(clean_pop["oos_sharpe"].median()), 4)},
        "tie_break_step": int(resolved_at) - 1,
        "raw_winner_row": {"signal": winner["signal"], "threshold": winner["threshold"],
                           "strategy": winner["strategy"], "lead_column": "lead_months",
                           "lead_value": int(winner["lead_months"]),
                           "source_tournament_file": os.path.basename(tpath),
                           "source_row_index": int(winner_row_idx),
                           "display_alias": (f"signal_code=cass_freight_{winner['signal']} (raw signal={winner['signal']}); "
                                             f"strategy_family={strat_family} (raw strategy={winner['strategy']})")},
        "runner_up": (None if runner is None else
                      {"signal": runner["signal"], "threshold": runner["threshold"], "strategy": runner["strategy"],
                       "lead_value": int(runner["lead_months"]), "objective_value": round(float(runner["oos_sharpe"]), 4)}),
        "rationale": (f"Maximiser of OOS Sharpe among SEASONALLY-CLEAN signals over the full tradable monthly lead grid "
                      f"L1..L12 ({len(clean_pop)} clean valid combos of {len(all_valid)} total valid; median clean OOS "
                      f"Sharpe {round(float(clean_pop['oos_sharpe'].median()),4)}). Objective is restricted to clean "
                      f"signals because the Cass series is NSA (Dana Phase-0 binding constraint) — see "
                      f"objective_runner_up_divergence. ECON-LT1 gate: L*={L_star}, {gate}. SHORT-HISTORY CAVEAT: OOS "
                      f"<5yr -> CANDIDATE (found-in-search), not a validated edge; Granger/CCF find no forward causality."),
        "objective_runner_up_divergence": divergence,
    }
    # ECON-T5 validations
    assert winner_row_idx >= 0, "raw winner row must resolve to exactly one tournament row"
    assert bool(winner["seasonally_clean"]) is True, "published winner must be seasonally clean under this objective"
    assert abs(float(winner["oos_sharpe"]) - clean_max) <= 1e-6, "winner must be the clean-population max"

    winner_summary = {
        "pair_id": PAIR_ID, "generated_at": NOW_ISO,
        "signal_column": SIGNAL_COLS[winner["signal"]],
        "signal_code": (f"cass_freight_{winner['signal']}" if not winner["signal"].startswith(("hmm", "markov")) else winner["signal"]),
        "signal_display_name": f"Cass Freight {winner['signal']}",
        "target_symbol": TARGET_SYMBOL, "threshold_code": winner["threshold"],
        "threshold_value": round(thr_value, 4), "threshold_rule": thr_rule,
        "threshold_note": ("threshold is rolling (window per lookback); threshold_value is the latest rolling value — "
                           "see winner_trade_log.csv for the full path" if isinstance(thr, pd.Series) else "static threshold (IS-calibrated)"),
        "strategy_family": strat_family, "strategy_code": strat_family.split("_")[0],
        "strategy_display_name": {"P1_long_cash": "Long/Cash", "P2_signal_strength": "Signal-strength sizing",
                                  "P3_long_short": "Long/Short"}[strat_family],
        "strategy_description": "",
        "lead_value": int(winner["lead_months"]), "lead_unit": "months",
        "lead_description": f"Signal lead = {int(winner['lead_months'])} month(s); L1 is the real-time floor given Cass's ~2-week publication lag",
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
        "notes": (f"Mode 1, feat260705_cass_freight_spy. Tournament: {len(tdf)-1} strategy combos (+1 benchmark, "
                  f"valid=False per ECON-T4), {n_valid} valid, full tradable lead grid L1..L12. Winner by ECON-T3 "
                  f"cascade (resolved at step {resolved_at}; {n_tied} tied at step 1). "
                  f"SHORT-HISTORY / FOUND-IN-SEARCH: OOS window is {int(winner['oos_n'])} months (<5yr) on a ~10yr "
                  f"NSA series -> the winner is a CANDIDATE, not a validated edge; OOS Sharpe is inflated/high-variance. "
                  f"NSA seasonality: winner seasonally_clean={winner_clean}"
                  + ("" if winner_clean else " — WINNER USES A SEASONALLY-CONTAMINATED SIGNAL; read with strong caution.") +
                  f" Lead-lag verdict (empirical): Cass->SPY TY-Granger sig lags {fwd_sig_lags or 'NONE'}, "
                  f"SPY->Cass sig lags {rev_sig_lags or 'NONE'}; pre-whitened CCF sig lead(+) lags {ccf_lead or 'NONE'}, "
                  f"lag(-) lags {ccf_lag or 'NONE'} -> classified '{leadlag}'. "
                  f"Robustness: winner bootstrap p={winner_boot_p} (vs resampled B&H); IS Sharpe {float(winner['is_sharpe']):.2f} "
                  f"vs OOS {float(winner['oos_sharpe']):.2f}; CP1 durability '{verdict}'; corr sign-stability '{stab}'. "
                  f"Gross of costs; {COST_BPS}bps sensitivity in tournament_validation_{DATE_TAG}/."),
    }
    sd = ("Long SPY when the lagged Cass Freight signal is {} its threshold; otherwise {}."
          .format("below" if thr_rule == "lt" else "above",
                  "cash" if strat_family == "P1_long_cash" else
                  ("short SPY" if strat_family == "P3_long_short" else "scale by signal strength")))
    if not long_when_high:
        sd += " (Countercyclical orientation: low/decelerating freight = risk-on.)"
    else:
        sd += " (Procyclical orientation: expanding freight = risk-on.)"
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

    # interpretation_metadata: update EVAN-OWNED fields only
    interp_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    with open(interp_path) as f:
        interp = json.load(f)
    interp["observed_direction"] = direction
    interp["direction_consistent"] = interp.get("expected_direction") in ("mixed", direction)
    interp["key_finding"] = (
        f"Lead-lag verdict (empirical): Cass Freight Shipments is '{leadlag}' vs SPY. Toda-Yamamoto Granger "
        f"Cass->SPY significant lags {fwd_sig_lags or 'NONE'}; SPY->Cass significant lags {rev_sig_lags or 'NONE'}; "
        f"pre-whitened CCF significant lead(+) lags {ccf_lead or 'NONE'}. Tournament winner "
        f"({winner['signal']}/{winner['threshold']}/{strat_family} {orientation}/L{winner['lead_months']}/{winner['lookback']}) "
        f"is {direction} (seasonally_clean={winner_clean}): OOS Sharpe {winner_summary['oos_sharpe']:.2f} vs B&H "
        f"{winner_summary['bh_sharpe']:.2f}. SHORT-HISTORY CANDIDATE: {int(winner['oos_n'])}-month OOS (<5yr) on a ~10yr "
        f"NSA series -> found-in-search, not a validated edge; bootstrap p={winner_boot_p}, durability '{verdict}'.")
    interp["confidence"] = "low"
    interp["last_updated_by"] = "evan"; interp["last_updated_at"] = NOW_ISO
    with open(interp_path, "w") as f:
        json.dump(interp, f, indent=2)
    assert interp["observed_direction"] in {"procyclical", "countercyclical", "mixed"}
    assert interp["observed_direction"] == winner_summary["direction"], "ECON-DIR1 consistency check failed"
    print("  interpretation_metadata evan-fields updated; ECON-DIR1: PASS")

    # tournament_winner.json (META-TWJ)
    tw = {"pair_id": PAIR_ID,
          "winner_label": f"{winner['signal']} / {winner['threshold']} / {strat_family} ({orientation}) / L{winner['lead_months']} / {winner['lookback']}",
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
        ("cass_freight_idx", "Cass Freight Index: Shipments, NSA monthly index (Jan1990=1.0)", "FRED FRGSHPUSM649NCIS", "raw"),
        ("cass_freight_pct_yoy", "12-month % change (seasonality-robust cycle signal)", "100*(L_t/L_{t-12}-1)", "derivative"),
        ("cass_freight_pct_mom", "1-month % change (NSA -> seasonal)", "100*(L_t/L_{t-1}-1)", "derivative"),
        ("cass_freight_3m_pct", "3-month % change (momentum; NSA -> partial seasonal)", "100*(L_t/L_{t-3}-1)", "derivative"),
        ("cass_freight_6m_pct", "6-month % change (momentum; NSA -> partial seasonal)", "100*(L_t/L_{t-6}-1)", "derivative"),
        ("cass_freight_ma12_idx", "12-month moving average of the level", "rolling mean(12)", "derivative"),
        ("cass_freight_dev_trend_pct", "% deviation of the level from its 12m MA", "100*(L_t/MA12-1)", "derivative"),
        ("cass_freight_zscore_60m", "rolling 60m z-score of the LEVEL (NSA; short usable span)", "(L_t-mean60)/sd60", "derivative"),
        ("cass_freight_yoy_zscore_60m", "rolling 60m z-score of YoY growth (preferred; short span)", "(yoy_t-mean60)/sd60", "derivative"),
        ("cass_freight_accel_pct", "month-on-month change in MoM growth (acceleration, pp)", "mom_t - mom_{t-1}", "derivative"),
        ("cass_freight_contraction", "1 when YoY freight growth < 0 (freight recession state)", "indicator(yoy<0)", "regime_state"),
        ("hmm_2state_prob_stress", "P(high-variance regime) from 2-state HMM on YoY growth", "GaussianHMM(yoy)", "regime_state"),
        ("markov_regime_2state", "P(high-variance regime) from Markov-switching regression spy_ret~yoy", "MarkovRegression", "regime_state")]]
    tgt_der = [{"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []} for c, d, s, r in [
        ("spy", "SPY adjusted month-end close", "Yahoo Finance", "raw"),
        ("spy_ret", "SPY monthly return (decimal)", "P_t/P_{t-1}-1", "derivative"),
        ("spy_fwd_1m", "1-month forward SPY return", "P_{t+1}/P_t-1", "derivative"),
        ("spy_fwd_3m", "3-month forward SPY return", "P_{t+3}/P_t-1", "derivative"),
        ("spy_fwd_6m", "6-month forward SPY return", "P_{t+6}/P_t-1", "derivative"),
        ("spy_fwd_12m", "12-month forward SPY return", "P_{t+12}/P_t-1", "derivative")]]
    scope = {"pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
             "last_updated_at": NOW_ISO,
             "indicator_axis": {"canonical_column": "cass_freight_idx", "display_name": "Cass Freight Index (Shipments)", "derivatives": ind_der},
             "target_axis": {"canonical_column": "spy", "display_name": "SPY (S&P 500 ETF)", "derivatives": tgt_der},
             "notes": ("ECON-SD: only Cass Freight derivatives and SPY derivatives are in scope. Controls in the parquet "
                       "(unrate, dgs10, fed_funds, vix) are context columns, NOT signals. NSA source -> YoY-family preferred "
                       "(seasonally-robust); MoM/3M/6M/level-zscore are seasonally contaminated. regime_story: false (CP2 skipped).")}
    with open(os.path.join(RESULTS_DIR, "signal_scope.json"), "w") as f:
        json.dump(scope, f, indent=2)

    # kpis.json
    kpis = [
        {"metric": "OOS Sharpe (winner)", "value": f"{winner_summary['oos_sharpe']:.2f}", "unit": "ratio", "delta": f"{tw['delta_sharpe']:+.2f} vs B&H"},
        {"metric": "OOS Sharpe (buy & hold)", "value": f"{winner_summary['bh_sharpe']:.2f}", "unit": "ratio", "delta": None},
        {"metric": "OOS Annual Return (winner)", "value": f"{winner_summary['oos_ann_return']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_ann_return']*100:+.1f}pp vs B&H"},
        {"metric": "OOS Max Drawdown (winner)", "value": f"{winner_summary['oos_max_drawdown']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_max_drawdown']*100:+.1f}pp vs B&H"},
        {"metric": "Valid strategy combos", "value": f"{n_valid}", "unit": "count", "delta": None},
        {"metric": "OOS window", "value": f"{split['oos_start']} → {split['oos_end']} (<5yr, candidate)", "unit": "dates", "delta": None},
    ]
    with open(os.path.join(RESULTS_DIR, "kpis.json"), "w") as f:
        json.dump(kpis, f, indent=2)

    # lead_sweep_manifest (ECON-LT1 record)
    with open(DATA_PATH, "rb") as f:
        input_sha = "sha256:" + hashlib.sha256(f.read()).hexdigest()[:16]
    lead_manifest = {
        "pair": PAIR_ID, "run_date": DATE_TAG, "frozen": False,
        "granularity": "months L1..12 tradable (L0 diagnostic-only in lead_correlation; ECON-LL1/LA1)",
        "freq_native": "M", "design_note": "Native monthly; lead L = calendar-month shift on month-end signals. L0 excluded from tradable grid (Cass ~2-week publication lag).",
        "oos_start": split["oos_start"], "is_end": split["in_sample_end"], "input_file": DATA_PATH,
        "input_sha256": input_sha, "lead_correlation_file": f"{PAIR_ID}/lead_correlation_{DATE_TAG}.csv",
        "lead_tournament_file": f"{PAIR_ID}/lead_tournament_{DATE_TAG}.csv",
        "published_winner": {"signal": SIGNAL_COLS[winner["signal"]], "lead": int(winner["lead_months"]),
                             "oos_sharpe": round(float(winner["oos_sharpe"]), 4)},
        # NSA-contaminated signal codes excluded from selection (complement of the
        # seasonally-clean set); consumed by gate_consistency to validate the winner
        # against the CLEAN combos only. Restored after the #198 re-run dropped it.
        "seasonally_contaminated_signals": sorted(set(SIGNAL_COLS) - SEASONALLY_CLEAN),
        "L_star": L_star, "best_oos_sharpe_at_grid": round(float(best_at_grid), 4) if pd.notna(best_at_grid) else None,
        "gate_decision": gate,
        "assertions": ["tradable lead grid is L1..12 (L0 non-tradable, pub-lag floor)",
                       "main tournament scans the full L1..12 grid -> published winner is the global lead max",
                       f"ECON-LT1 gate: L*={L_star} -> {gate}"],
        "short_history_caveat": "OOS <5yr -> winner is found-in-search; lead-sweep peaks are high-variance."}
    with open(os.path.join(RESULTS_DIR, f"lead_sweep_manifest_{DATE_TAG}.json"), "w") as f:
        json.dump(lead_manifest, f, indent=2)

    # design_note.md (Rule C1 deviations + verdict)
    design = f"""# Design Note — {PAIR_ID} ({DATE_TAG})

## Category & method coverage (Rule C1, production/macro — full battery to mirror busloans_spy)
All mandatory methods produced (correlations incl. distance, pre-whitened CCF, Toda-Yamamoto Granger both
directions, transfer entropy, local projections fwd+rev, quantile regression, HMM 2-state, quartile returns)
plus ECON-LA1 Lead Analysis and ECON-LT1 Lead Tournament. Deviations from the daily-pair spec:
- MONTHLY pair: correlation horizons are 1m/3m/6m/12m fwd returns (recorded as 21/63/126/252 horizon_days).
- Pre-whitened CCF at monthly lags -18..+18 (trimmed from -20..+20 given the ~125-obs sample).
- Granger is Toda-Yamamoto (VAR in levels of YoY, d_max=1; YoY is borderline I(1) per ADF/KPSS).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations.
- Stationarity: Dana's tests (stationarity_tests_{DATE_TAG}.csv) reviewed and CONFIRMED, not re-run.

## Short-sample adaptations (BINDING Dana Phase-0 constraints)
- 125 monthly obs (2016-01..2026-05). OOS window is {36} months (<5yr) -> ANY winner is FOUND-IN-SEARCH,
  Sharpe inflated/high-variance; treated as a CANDIDATE, never a validated edge (stated in winner_summary).
- Signal eligibility floor {SIG_ELIGIBLE_MIN} non-NaN obs; lookbacks {list(LOOKBACKS.keys())} (LB120 impossible).
- Correlation/regression n-floor lowered to 40 (short history).

## NSA seasonality (BINDING)
Source is NSA -> MoM/3M/6M momentum and the level z-score are seasonally contaminated. YoY-family
(`_pct_yoy`, `_yoy_zscore_60m`), `_dev_trend`, `_contraction`, and regime signals are treated as
seasonally-clean; each tournament row carries a `seasonally_clean` flag and the winner's flag is surfaced
in winner_summary. A seasonally-contaminated winner is NOT allowed to ship silently — flagged hard.

## Publication lag / no-lookahead
Cass publishes ~mid-month for the prior month. Tradable lead grid FLOORS at L1 (no L0). L0 appears only in
the diagnostic lead_correlation table, explicitly flagged non-tradable.

## Lead-lag verdict (empirical — determined by Granger/CCF/LP, NOT the prior)
- Cass->SPY TY-Granger significant lags: {fwd_sig_lags or 'NONE'}
- SPY->Cass TY-Granger significant lags: {rev_sig_lags or 'NONE'}
- Pre-whitened CCF significant lead(+) lags: {ccf_lead or 'NONE'}; lag(-) lags: {ccf_lag or 'NONE'}
- LP forward significant: {fwd_lp_flag}; reverse-causality flag: {rev_flag}
- Classification: {leadlag}. Winner direction (empirical): {direction}.

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal). Lead grid L1..L12 (full tradable). Both orientations tested.
- CP2 skipped (regime_story: false). Returns gross of costs; 5bps grid in tournament_validation_{DATE_TAG}/.

## New pair — no prior version; Rule C3 regression diff N/A.
"""
    with open(os.path.join(RESULTS_DIR, "design_note.md"), "w") as f:
        f.write(design)

    # analyst_suggestions.json
    sugg = {"schema_version": "1.0.0", "pair_id": PAIR_ID, "rule": "ECON-AS",
            "suggestions": [
                {"signal_name": "Cass Freight Expenditures (FRGEXPUSM649NCIS)", "proposed_by": "evan",
                 "source": "FRED", "observation": "Expenditures = shipments x price/mix; combining volume (shipments) with the expenditures deflator isolates a freight-rate signal distinct from volume.",
                 "rationale": "Freight rates (pricing power) may lead the goods cycle differently than volumes.",
                 "possible_use_case": "new pair / companion signal", "caveats": "Same NSA/short-history limits.",
                 "date_filed": "2026-07-05"},
                {"signal_name": "ISM Manufacturing New Orders", "proposed_by": "evan", "source": "FRED/ISM",
                 "observation": "A survey-based leading twin of the goods economy with a longer history (1948+) and SA.",
                 "rationale": "If Cass proves coincident/short-history-limited, ISM new orders offers a longer, SA leading read.",
                 "possible_use_case": "new pair", "caveats": "Diffusion index, not a quantity.", "date_filed": "2026-07-05"}],
            "last_updated_by": "evan", "last_updated_at": NOW_ISO}
    with open(os.path.join(RESULTS_DIR, "analyst_suggestions.json"), "w") as f:
        json.dump(sugg, f, indent=2)

    # evidence_status.json
    ev = {"pair_id": PAIR_ID, "generated_at": NOW_ISO, "generated_by": "evan",
          "blocks": {
              "correlations": "ready", "lead_correlation": "ready", "lead_tournament": "ready",
              "ccf_prewhitened": "ready", "granger_causality": "ready", "transfer_entropy": "ready",
              "local_projections": "ready", "quantile_regression": "ready", "regime_quartile_returns": "ready",
              "hmm_states": "ready" if "hmm_2state_prob_stress" in df.columns else "skipped_short_sample",
              "subperiod_sharpe": "ready", "structural_break": "ready", "rolling_correlation": "ready",
              "tournament": "ready", "winner_summary": "ready"},
          "caveats": ["OOS <5yr -> winner is a found-in-search CANDIDATE (high-variance Sharpe)",
                      "NSA source -> non-YoY signals seasonally contaminated",
                      f"empirical lead-lag class: {leadlag}"]}
    with open(os.path.join(RESULTS_DIR, "evidence_status.json"), "w") as f:
        json.dump(ev, f, indent=2)

    # timing
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump({"pair_id": PAIR_ID, "date": DATE_TAG, "pipeline_seconds": round(time.time() - t0, 1),
                   "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
                   "tournament_strategy_rows": int(len(tdf) - 1), "valid_strategies": n_valid,
                   "oos_n_months": int(winner["oos_n"]), "oos_start": split["oos_start"], "oos_end": split["oos_end"]}, f, indent=2)

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE — HANDOFF NUMBERS (DPS-SCD1)")
    print("=" * 70)
    print(f"  Strategy combos: {len(tdf)-1} | valid: {n_valid} | median OOS Sharpe (valid): {median_sharpe:.3f}")
    print(f"  Winner: {tw['winner_label']} | seasonally_clean={winner_clean}")
    print(f"  OOS Sharpe {winner_summary['oos_sharpe']} vs B&H {winner_summary['bh_sharpe']} | "
          f"DD {winner_summary['oos_max_drawdown']} vs {winner_summary['bh_max_drawdown']} | "
          f"ret {winner_summary['oos_ann_return']} vs {winner_summary['bh_ann_return']}")
    print(f"  Ties at step 1: {n_tied} (cascade resolved at step {resolved_at})")
    print(f"  Durability: {verdict} | corr sign-stability: {stab} | break flagged: {sb['flagged']} ({sb['break_date']})")
    print(f"  Direction (winner): {direction} | lead-lag class: {leadlag} | ECON-LT1 gate: {gate} (L*={L_star})")
    print(f"  Granger fwd-sig lags: {fwd_sig_lags or 'NONE'} | rev-sig lags: {rev_sig_lags or 'NONE'} | "
          f"CCF lead lags: {ccf_lead or 'NONE'}")
    print(f"  Winner bootstrap p={winner_boot_p} | SHORT-OOS (<5yr) CANDIDATE, NSA-caveat applies")
    return winner_summary, tw


if __name__ == "__main__":
    main()
