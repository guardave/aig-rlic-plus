"""Causal (look-ahead-free) regime probabilities for tournament signals.

Why this module exists
----------------------
QC (2026-10-16, hy_ig_spy) found that every HMM / Markov-switching (MS) trading signal in
the fleet was built as

    GaussianHMM(...).fit(X_full_sample); predict_proba(X_full_sample)        # HMM
    MarkovRegression(spy_ret, exog=indicator).fit(); smoothed_marginal_...   # MS

Both are look-ahead:
  * the parameters (and the standardisation mean/std) are estimated on the FULL sample,
    so OOS observations inform the "in-sample" model;
  * ``predict_proba`` / ``smoothed_marginal_probabilities`` are forward-backward SMOOTHED
    posteriors P(state_t | x_1..x_T): the value at t uses observations after t;
  * the MS variant also puts the TARGET return in the regime likelihood, so the
    "signal" is partly a function of the return it is supposed to predict.

This module is the single shared fix. A trading-signal regime probability is produced by

  1. fitting the model ONLY on in-sample rows (index < ``oos_start``);
  2. standardising with in-sample mean/std only (HMM);
  3. running a forward-only filter with the frozen in-sample parameters over the full
     sample: p_t = P(state_t | x_1..x_t). Nothing at t depends on x_{t+1..T};
  4. labelling states deterministically (by the in-sample mean of a named feature for the
     HMM; by regime variance or mean for MS), independent of EM's arbitrary state order.

The target asset return must NOT be passed into ``fit_ms_causal`` (or ``fit_hmm_causal``)
when the output is used as a trading signal; ``fit_ms_causal`` takes the indicator series
only and refuses a column/series named like a target return unless explicitly allowed.

Fleet port: see _pws/lead-lesandro/pkg8_hmm_causal/LEDGER.md ("FLEET PORT GUIDE").

Public API
----------
    forward_filter(log_lik, startprob, transmat) -> (T, K) filtered probabilities
    fit_hmm_causal(X, oos_start, ...)            -> CausalRegime
    fit_ms_causal(y, oos_start, ...)             -> CausalRegime

Both ``fit_*`` return a ``CausalRegime`` whose ``prob`` is the filtered probability of the
labelled state ("stress" by default) on the input index (NaN where the input row was NaN).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy.special import logsumexp

__all__ = ["CausalRegime", "forward_filter", "fit_hmm_causal", "fit_ms_causal"]

_TARGET_HINTS = ("spy_ret", "target_ret", "xlp_ret", "xlv_ret", "xli_ret", "fwd")


@dataclass
class CausalRegime:
    """Result of a causal regime fit.

    prob      filtered P(labelled state | data up to t), index = input index
    probs     filtered probabilities of every state, columns state_0..state_{K-1} ordered by
              the labelling key ascending (so the labelled "high" state is the last column)
    labelled_state  column name in ``probs`` that ``prob`` reports
    params    frozen in-sample parameters (plain python containers, JSON-safe)
    fit_start / fit_end / n_fit   in-sample rows actually used for estimation
    loglik_is in-sample log-likelihood of the selected fit
    model     the fitted model object (hmmlearn GaussianHMM or statsmodels results)
    """
    prob: pd.Series
    probs: pd.DataFrame
    labelled_state: str
    params: dict
    fit_start: pd.Timestamp
    fit_end: pd.Timestamp
    n_fit: int
    loglik_is: float
    kind: str
    model: object = field(repr=False, default=None)

    def summary(self) -> dict:
        return {
            "kind": self.kind,
            "fit_start": self.fit_start.date().isoformat(),
            "fit_end": self.fit_end.date().isoformat(),
            "n_fit": int(self.n_fit),
            "loglik_is": round(float(self.loglik_is), 4),
            "labelled_state": self.labelled_state,
            "probability": "forward-filtered P(state_t | x_1..x_t) with in-sample-frozen params",
            "params": self.params,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Forward filter (HMM)
# ─────────────────────────────────────────────────────────────────────────────

def forward_filter(log_lik: np.ndarray, startprob: np.ndarray, transmat: np.ndarray) -> np.ndarray:
    """Normalised forward recursion in log space.

    log_lik  (T, K) log p(x_t | state_t = k)
    startprob (K,)  initial state distribution
    transmat (K, K) A[i, j] = P(state_t = j | state_{t-1} = i)

    Returns (T, K) filtered probabilities P(state_t = k | x_1..x_t). Row t uses rows 0..t of
    ``log_lik`` only, so truncating the input at any t leaves rows 0..t unchanged.
    """
    log_lik = np.asarray(log_lik, dtype=float)
    T, K = log_lik.shape
    log_a = np.log(np.asarray(transmat, dtype=float) + 1e-300)
    la = np.empty((T, K))
    if T == 0:
        return la
    la[0] = np.log(np.asarray(startprob, dtype=float) + 1e-300) + log_lik[0]
    la[0] -= logsumexp(la[0])
    for t in range(1, T):
        la[t] = log_lik[t] + logsumexp(la[t - 1][:, None] + log_a, axis=0)
        la[t] -= logsumexp(la[t])
    return np.exp(la)


def _gaussian_loglik(Xs: np.ndarray, means: np.ndarray, covars: np.ndarray) -> np.ndarray:
    """(T, K) multivariate-normal log densities, explicit (no private hmmlearn API)."""
    T, D = Xs.shape
    K = means.shape[0]
    out = np.empty((T, K))
    for k in range(K):
        cov = np.atleast_2d(covars[k])
        L = np.linalg.cholesky(cov)
        diff = Xs - means[k]
        sol = np.linalg.solve(L, diff.T)              # (D, T)
        maha = (sol ** 2).sum(axis=0)
        logdet = 2.0 * np.log(np.diag(L)).sum()
        out[:, k] = -0.5 * (D * np.log(2 * np.pi) + logdet + maha)
    return out


def _is_mask(index: pd.Index, oos_start) -> np.ndarray:
    return np.asarray(index < pd.Timestamp(oos_start))


def _check_no_target(names: Iterable[str], allow_target: bool) -> None:
    if allow_target:
        return
    bad = [n for n in names if any(h in str(n).lower() for h in _TARGET_HINTS)]
    if bad:
        raise ValueError(
            f"regime input looks like a target return {bad}: a trading-signal regime model must not "
            "include the target asset return in its likelihood (pass allow_target=True only for a "
            "descriptive, non-traded model)")


# ─────────────────────────────────────────────────────────────────────────────
# Gaussian HMM
# ─────────────────────────────────────────────────────────────────────────────

def fit_hmm_causal(X: pd.DataFrame, oos_start, *, n_states: int = 2, label_feature: str | None = None,
                   label: str = "max", covariance_type: str = "full", n_iter: int = 200,
                   seeds: Sequence[int] = (42,), standardize: bool = True,
                   allow_target: bool = False, min_is_rows: int | None = None) -> CausalRegime:
    """Fit a GaussianHMM on in-sample rows only and return forward-filtered probabilities.

    X              DataFrame of features (DatetimeIndex). Rows with any NaN are excluded from
                   both fit and filter (their output is NaN).
    oos_start      first OOS date; rows with index < oos_start form the estimation sample.
    label_feature  feature whose in-sample state mean orders the states (default: first column).
    label          "max" -> report the state with the highest mean of label_feature; "min" -> lowest.
    seeds          EM restarts; the fit with the highest in-sample log-likelihood is kept
                   (ties -> earliest seed), so the result is deterministic.
    min_is_rows    minimum in-sample rows (default 50 * n_states). Lower it only for a
                   descriptive / diagnostic fit that is NOT traded, and say so where it is used.
    """
    from hmmlearn.hmm import GaussianHMM

    if covariance_type not in ("full", "diag", "tied"):
        raise ValueError("covariance_type must be full|diag|tied")
    _check_no_target(X.columns, allow_target)
    Xc = X.dropna()
    ism = _is_mask(Xc.index, oos_start)
    if ism.sum() < (50 * n_states if min_is_rows is None else min_is_rows):
        raise ValueError(f"too few in-sample rows to fit HMM ({ism.sum()})")
    vals = Xc.values.astype(float)
    if standardize:
        mu = vals[ism].mean(0)
        sd = vals[ism].std(0)
        sd[sd == 0] = 1.0
    else:
        mu = np.zeros(vals.shape[1])
        sd = np.ones(vals.shape[1])
    Xs = (vals - mu) / sd

    best, best_ll, best_seed = None, -np.inf, None
    for seed in seeds:
        m = GaussianHMM(n_components=n_states, covariance_type=covariance_type,
                        n_iter=n_iter, random_state=seed)
        m.fit(Xs[ism])
        ll = float(m.score(Xs[ism]))
        if ll > best_ll + 1e-9:
            best, best_ll, best_seed = m, ll, seed

    feat = label_feature if label_feature is not None else X.columns[0]
    j = list(X.columns).index(feat)
    order = np.argsort(best.means_[:, j], kind="stable")      # ascending by label feature
    covars = best.covars_                                      # full form for full/diag/tied
    log_lik = _gaussian_loglik(Xs, best.means_, covars)
    filt = forward_filter(log_lik, best.startprob_, best.transmat_)[:, order]

    cols = [f"state_{i}" for i in range(n_states)]
    probs = pd.DataFrame(filt, index=Xc.index, columns=cols).reindex(X.index)
    lab = cols[-1] if label == "max" else cols[0]
    params = {
        "seed": int(best_seed), "seeds_tried": [int(s) for s in seeds],
        "features": list(map(str, X.columns)), "label_feature": str(feat), "label": label,
        "standardize_mean_is": [float(x) for x in mu], "standardize_std_is": [float(x) for x in sd],
        "means": best.means_[order].tolist(), "startprob": best.startprob_[order].tolist(),
        "transmat": best.transmat_[np.ix_(order, order)].tolist(),
        "covariance_type": covariance_type,
    }
    is_idx = Xc.index[ism]
    return CausalRegime(prob=probs[lab].rename(None), probs=probs, labelled_state=lab, params=params,
                        fit_start=is_idx[0], fit_end=is_idx[-1], n_fit=int(ism.sum()),
                        loglik_is=best_ll, kind="GaussianHMM", model=best)


# ─────────────────────────────────────────────────────────────────────────────
# Markov-switching (Hamilton filter via statsmodels, frozen in-sample params)
# ─────────────────────────────────────────────────────────────────────────────

def fit_ms_causal(y: pd.Series, oos_start, *, k_regimes: int = 2, exog: pd.DataFrame | None = None,
                  switching_variance: bool = True, label: str = "max_variance", maxiter: int = 200,
                  allow_target: bool = False, min_is_rows: int | None = None) -> CausalRegime:
    """MarkovRegression fit on in-sample rows only; Hamilton-filtered probabilities on all rows.

    y      regime-model dependent variable (the INDICATOR, e.g. daily spread change) — never the
           target asset return for a trading signal.
    exog   optional exogenous regressors (also must not contain the target).
    label  "max_variance" (default) / "min_variance" / "max_mean" / "min_mean" picks the reported
           regime; the probs frame is ordered ascending by the same key.

    The filtered probability P(S_t | y_1..y_t) is computed by statsmodels' Hamilton filter
    (``model.filter(params)``) on the full-sample model with the parameters frozen at the
    in-sample MLE; it never runs the Kim smoother.

    min_is_rows  minimum in-sample rows (default 100); lower it only for a non-traded diagnostic.
    """
    import statsmodels.api as sm
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

    names = [y.name] + (list(exog.columns) if exog is not None else [])
    _check_no_target(names, allow_target)
    data = y.to_frame("y") if exog is None else pd.concat([y.rename("y"), exog], axis=1)
    data = data.dropna()
    ism = _is_mask(data.index, oos_start)
    if ism.sum() < (100 if min_is_rows is None else min_is_rows):
        raise ValueError(f"too few in-sample rows to fit MS ({ism.sum()})")
    ex_all = None if exog is None else sm.add_constant(data[list(exog.columns)])
    mod_is = MarkovRegression(data["y"][ism].values, k_regimes=k_regimes,
                              exog=None if ex_all is None else ex_all[ism].values,
                              switching_variance=switching_variance)
    res_is = mod_is.fit(maxiter=maxiter, disp=False)
    mod_all = MarkovRegression(data["y"].values, k_regimes=k_regimes,
                               exog=None if ex_all is None else ex_all.values,
                               switching_variance=switching_variance)
    res_all = mod_all.filter(res_is.params)
    filt = np.asarray(res_all.filtered_marginal_probabilities)
    if filt.shape[0] != len(data):
        filt = filt.T

    pnames = list(mod_is.param_names)
    p = dict(zip(pnames, np.asarray(res_is.params, dtype=float)))
    if label.endswith("variance"):
        key = np.array([p.get(f"sigma2[{i}]", p.get("sigma2", np.nan)) for i in range(k_regimes)])
    else:
        key = np.array([p.get(f"const[{i}]", np.nan) for i in range(k_regimes)])
    order = np.argsort(key, kind="stable")
    filt = filt[:, order]
    cols = [f"state_{i}" for i in range(k_regimes)]
    probs = pd.DataFrame(filt, index=data.index, columns=cols).reindex(y.index)
    lab = cols[-1] if label.startswith("max") else cols[0]
    is_idx = data.index[ism]
    params = {"param_names": pnames, "params_is": [float(v) for v in np.asarray(res_is.params)],
              "label": label, "label_key_sorted": [float(v) for v in key[order]],
              "dependent": str(y.name), "exog": [] if exog is None else list(map(str, exog.columns)),
              "switching_variance": bool(switching_variance)}
    return CausalRegime(prob=probs[lab].rename(None), probs=probs, labelled_state=lab, params=params,
                        fit_start=is_idx[0], fit_end=is_idx[-1], n_fit=int(ism.sum()),
                        loglik_is=float(res_is.llf), kind="MarkovRegression", model=res_is)
