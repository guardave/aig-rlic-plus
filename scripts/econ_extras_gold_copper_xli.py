#!/usr/bin/env python3
"""
Econometrics Extensions: gold_copper_xli (Mode 2 Phase 3.5, Evan hat ext)

Adds the 4 econometric methods that Phase 3 deferred:
  - HMM 2-state regime probabilities (statsmodels MarkovRegression)
  - Local projections (Jordà-style impulse responses, HAC SE)
  - Quantile regression at multiple quantiles (0.05..0.95)
  - Transfer entropy (binned, non-linear lead-lag) — pure-numpy fallback

Outputs (all under results/gold_copper_xli/):
  hmm_regime_probs.csv      (date, p_state0, p_state1, viterbi_state)
  hmm_summary.json          (state means, transition matrix, log-likelihood)
  local_projections.csv     (horizon, beta, se_hac, t_stat, ci_low, ci_high)
  quantile_regression.csv   (quantile, beta, se, t_stat, p_value)
  transfer_entropy.json     (TE values + bootstrap CI)
"""

import os, json, time, warnings
from datetime import datetime, timezone
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

PAIR_ID = "gold_copper_xli"
DATE_TAG = "20260526"
BASE = "/workspaces/aig-rlic-plus"
PARQUET = os.path.join(BASE, "data", f"{PAIR_ID}_daily_{DATE_TAG}.parquet")
RESULTS = os.path.join(BASE, "results", PAIR_ID)

IS_END = pd.Timestamp("2019-12-31")

SIGNAL_COL = "gold_copper_zscore_252d"  # use 252d for the analytic methods
RETURN_COL = "xli_ret"
FWD_COL = "xli_fwd_63d"


def log(m): print(f"[econ_ext] {m}", flush=True)


# ------------------------------------------------------------------
# HMM 2-state on signal series
# ------------------------------------------------------------------
def run_hmm(df):
    log("HMM: 2-state Markov regression on gold_copper_zscore_252d")
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
    sig = df[SIGNAL_COL].dropna()
    mod = MarkovRegression(sig.values, k_regimes=2, switching_variance=True)
    res = mod.fit(disp=False, maxiter=500)
    smoothed = np.asarray(res.smoothed_marginal_probabilities)
    probs = pd.DataFrame({
        "date": sig.index,
        "p_state0": smoothed[:, 0],
        "p_state1": smoothed[:, 1],
    }).set_index("date")
    probs["viterbi_state"] = (probs["p_state1"] > 0.5).astype(int)

    # Identify which state is "stress" — the higher-VARIANCE state.
    # With switching_variance=True the regimes are discriminated primarily
    # by variance, not mean. Stress regimes carry the wider distribution.
    state_means = [
        sig[probs["viterbi_state"].values == s].mean() for s in (0, 1)
    ]
    state_vars = [
        sig[probs["viterbi_state"].values == s].var() for s in (0, 1)
    ]
    stress_state = int(np.argmax(state_vars))
    log(f"  state means: s0={state_means[0]:.3f}, s1={state_means[1]:.3f}")
    log(f"  state vars : s0={state_vars[0]:.3f}, s1={state_vars[1]:.3f}")
    log(f"  stress = state {stress_state} (higher variance)")
    probs["p_stress"] = probs[f"p_state{stress_state}"]

    out_csv = os.path.join(RESULTS, "hmm_regime_probs.csv")
    probs.to_csv(out_csv)
    log(f"  wrote {out_csv}  ({len(probs)} obs)")

    # Transition matrix
    trans = np.array(res.regime_transition).reshape(2, 2).tolist()
    summary = {
        "method": "MarkovRegression (statsmodels)",
        "signal_series": SIGNAL_COL,
        "k_regimes": 2,
        "switching_variance": True,
        "log_likelihood": float(res.llf),
        "state_means": {f"state{i}": float(state_means[i]) for i in (0, 1)},
        "state_variances": {f"state{i}": float(state_vars[i]) for i in (0, 1)},
        "stress_state": stress_state,
        "stress_state_identification": "higher_variance",
        "transition_matrix_2x2": trans,
        "n_obs": int(len(sig)),
        "is_end": str(IS_END.date()),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    out_json = os.path.join(RESULTS, "hmm_summary.json")
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"  wrote {out_json}")
    return probs


# ------------------------------------------------------------------
# Local Projections (Jordà)
# ------------------------------------------------------------------
def run_local_projections(df):
    log("Local Projections: cumulative XLI return at horizons 1..126 days")
    import statsmodels.api as sm
    sub = df[[SIGNAL_COL, "xli_ret"]].dropna()
    sub = sub.loc[:IS_END]  # IS estimation per scope discipline
    horizons = [1, 5, 10, 21, 42, 63, 84, 105, 126]
    rows = []
    sig = sub[SIGNAL_COL]
    ret = sub["xli_ret"]
    for h in horizons:
        # Cumulative return over next h days
        cum = ret.shift(-h+1).rolling(h).sum()
        y = cum.dropna()
        x = sig.reindex(y.index)
        X = sm.add_constant(x.values)
        try:
            model = sm.OLS(y.values * 100.0, X).fit(
                cov_type="HAC", cov_kwds={"maxlags": h}
            )
            beta = float(model.params[1])
            se = float(model.bse[1])
            t = float(model.tvalues[1])
            rows.append({
                "horizon_days": h,
                "beta_pct": round(beta, 4),
                "se_hac": round(se, 4),
                "t_stat": round(t, 3),
                "ci_low_pct": round(beta - 1.96 * se, 4),
                "ci_high_pct": round(beta + 1.96 * se, 4),
                "n_obs": int(len(y)),
            })
        except Exception as e:
            log(f"  LP fail h={h}: {e}")
    out = os.path.join(RESULTS, "local_projections.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"  wrote {out}  ({len(rows)} horizons)")
    return rows


# ------------------------------------------------------------------
# Quantile Regression
# ------------------------------------------------------------------
def run_quantile_regression(df):
    log("Quantile Regression: signal -> 63d fwd return at quantiles")
    from statsmodels.regression.quantile_regression import QuantReg
    import statsmodels.api as sm
    sub = df[[SIGNAL_COL, FWD_COL]].dropna()
    sub = sub.loc[:IS_END]
    quantiles = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
    rows = []
    X = sm.add_constant(sub[SIGNAL_COL].values)
    y = sub[FWD_COL].values * 100.0
    for q in quantiles:
        try:
            res = QuantReg(y, X).fit(q=q, max_iter=2000)
            beta = float(res.params[1])
            se = float(res.bse[1])
            t = float(res.tvalues[1])
            p = float(res.pvalues[1])
            rows.append({
                "quantile": q,
                "beta_pct": round(beta, 4),
                "se": round(se, 4),
                "t_stat": round(t, 3),
                "p_value": round(p, 4),
            })
        except Exception as e:
            log(f"  QR fail q={q}: {e}")
    out = os.path.join(RESULTS, "quantile_regression.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"  wrote {out}  ({len(rows)} quantiles)")
    return rows


# ------------------------------------------------------------------
# Transfer Entropy (binned, non-parametric)
# ------------------------------------------------------------------
def run_transfer_entropy(df):
    """Binned TE from signal to xli_ret, lag 1. Pure numpy.

    TE(X -> Y) = H(Y_t+1 | Y_t) - H(Y_t+1 | Y_t, X_t)
    Estimate with discretization into N bins.
    """
    log("Transfer Entropy: signal -> xli_ret (binned, N=4)")
    sub = df[[SIGNAL_COL, RETURN_COL]].dropna()
    sub = sub.loc[:IS_END]
    nbins = 4

    def discretize(s, n):
        edges = np.quantile(s, np.linspace(0, 1, n + 1))
        edges[0] -= 1e-9
        edges[-1] += 1e-9
        return np.digitize(s, edges) - 1

    def te_xy(x, y, lag=1):
        # y_t, y_{t+lag}, x_t
        yt = y[:-lag]
        yt1 = y[lag:]
        xt = x[:-lag]
        # joint counts
        # H(Y_{t+1} | Y_t) = H(Y_t, Y_{t+1}) - H(Y_t)
        def H(arr):
            # entropy of a sequence treating each row as a discrete symbol
            unique, counts = np.unique(arr, return_counts=True, axis=0)
            p = counts / counts.sum()
            return -np.sum(p * np.log2(p + 1e-12))
        H_y = H(yt)
        H_yy1 = H(np.column_stack([yt, yt1]))
        H_yx = H(np.column_stack([yt, xt]))
        H_yxy1 = H(np.column_stack([yt, xt, yt1]))
        te = (H_yy1 - H_y) - (H_yxy1 - H_yx)
        return float(te)

    x = discretize(sub[SIGNAL_COL].values, nbins)
    y = discretize(sub[RETURN_COL].values, nbins)

    te_observed = te_xy(x, y)
    te_reverse = te_xy(y, x)

    # Bootstrap CI under null (shuffle x)
    rng = np.random.default_rng(42)
    boots = []
    for _ in range(200):
        x_shuf = rng.permutation(x)
        boots.append(te_xy(x_shuf, y))
    null_ci = (float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975)))
    p_emp = float(np.mean(np.array(boots) >= te_observed))

    summary = {
        "method": "binned transfer entropy (numpy, N_bins=4, lag=1)",
        "signal": SIGNAL_COL,
        "target": RETURN_COL,
        "te_signal_to_return": round(te_observed, 5),
        "te_return_to_signal": round(te_reverse, 5),
        "null_ci_95_via_shuffle": [round(c, 5) for c in null_ci],
        "p_value_empirical": round(p_emp, 4),
        "n_obs": int(len(x)),
        "n_bootstrap": 200,
        "is_end": str(IS_END.date()),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    out = os.path.join(RESULTS, "transfer_entropy.json")
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"  TE(signal->return) = {te_observed:.5f}  "
        f"null 95% CI = {null_ci}  p_emp = {p_emp:.3f}")
    log(f"  wrote {out}")
    return summary


def main():
    t0 = time.time()
    df = pd.read_parquet(PARQUET)
    log(f"loaded {PARQUET}  rows={len(df)}")
    run_hmm(df)
    run_local_projections(df)
    run_quantile_regression(df)
    run_transfer_entropy(df)
    log(f"DONE in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
