"""Tests for scripts/_regime_causal.py (causal HMM / Markov-switching regime probabilities).

Properties checked on synthetic two-regime data:
  * forward filter == brute-force normalised forward recursion; last filtered row == last
    smoothed row (the smoother at T has no future to use) — the filter is a filter;
  * filtered != smoothed away from the end (the old predict_proba path is not reproduced);
  * no future dependence: truncating the data at t leaves p_0..p_t unchanged;
  * IS-only fit: changing OOS data leaves params and IS-period probabilities unchanged;
  * deterministic state labelling (the reported state has the larger label-feature mean);
  * the MS fit refuses a target-return dependent variable for trading signals.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _regime_causal as rc  # noqa: E402

OOS = "2014-01-01"


def _two_regime(n=1500, seed=0):
    rng = np.random.RandomState(seed)
    idx = pd.bdate_range("2010-01-01", periods=n)
    s = np.zeros(n, dtype=int)
    for t in range(1, n):
        stay = 0.98 if s[t - 1] == 0 else 0.95
        s[t] = s[t - 1] if rng.rand() < stay else 1 - s[t - 1]
    a = np.where(s == 1, 1.5, 0.0) + rng.randn(n) * np.where(s == 1, 1.5, 0.6)
    b = np.where(s == 1, 30.0, 15.0) + rng.randn(n) * 3.0
    return pd.DataFrame({"spread_change": a, "vix": b}, index=idx), pd.Series(s, index=idx)


@pytest.fixture(scope="module")
def data():
    return _two_regime()


@pytest.fixture(scope="module")
def hmm_full(data):
    X, _ = data
    return rc.fit_hmm_causal(X, OOS, label_feature="spread_change", seeds=(42, 1))


def test_forward_filter_matches_bruteforce():
    rng = np.random.RandomState(3)
    T, K = 40, 3
    ll = rng.randn(T, K)
    A = rng.rand(K, K); A /= A.sum(1, keepdims=True)
    pi = rng.rand(K); pi /= pi.sum()
    alpha = pi * np.exp(ll[0]); alpha /= alpha.sum()
    out = [alpha]
    for t in range(1, T):
        alpha = (alpha @ A) * np.exp(ll[t]); alpha /= alpha.sum()
        out.append(alpha)
    np.testing.assert_allclose(rc.forward_filter(ll, pi, A), np.array(out), atol=1e-12)


def test_filter_last_row_equals_smoothed_last_row(data, hmm_full):
    X, _ = data
    mu = np.array(hmm_full.params["standardize_mean_is"]); sd = np.array(hmm_full.params["standardize_std_is"])
    sm = hmm_full.model.predict_proba((X.values - mu) / sd)
    j = int(np.argmax(hmm_full.model.means_[:, 0]))
    assert abs(sm[-1, j] - hmm_full.prob.iloc[-1]) < 1e-8


def test_filtered_differs_from_smoothed(data, hmm_full):
    X, _ = data
    mu = np.array(hmm_full.params["standardize_mean_is"]); sd = np.array(hmm_full.params["standardize_std_is"])
    sm = hmm_full.model.predict_proba((X.values - mu) / sd)
    j = int(np.argmax(hmm_full.model.means_[:, 0]))
    diff = np.abs(sm[:-1, j] - hmm_full.prob.values[:-1])
    assert diff.max() > 0.05, "filtered probabilities must not equal forward-backward smoothed ones"


def test_hmm_no_future_dependence(data, hmm_full):
    X, _ = data
    n_is = int((X.index < OOS).sum())
    for cut in (n_is + 5, 1200, len(X) - 2):
        part = rc.fit_hmm_causal(X.iloc[: cut + 1], OOS, label_feature="spread_change", seeds=(42, 1))
        np.testing.assert_allclose(part.prob.values, hmm_full.prob.values[: cut + 1], atol=1e-10)


def test_hmm_is_only_fit(data, hmm_full):
    X, _ = data
    X2 = X.copy()
    oos = X2.index >= OOS
    X2.loc[oos] = X2.loc[oos].values[::-1] * 3.0 + 7.0  # wreck the OOS data
    alt = rc.fit_hmm_causal(X2, OOS, label_feature="spread_change", seeds=(42, 1))
    for k in ("standardize_mean_is", "standardize_std_is", "means", "transmat", "startprob"):
        np.testing.assert_allclose(np.array(alt.params[k]), np.array(hmm_full.params[k]), atol=1e-12)
    is_rows = X.index < OOS
    np.testing.assert_allclose(alt.prob.values[is_rows], hmm_full.prob.values[is_rows], atol=1e-12)
    assert alt.fit_end < pd.Timestamp(OOS) and alt.n_fit == int(is_rows.sum())


def test_hmm_label_is_deterministic(data, hmm_full):
    X, truth = data
    means = np.array(hmm_full.params["means"])
    assert means[-1, 0] > means[0, 0]  # reported (last) state has the higher spread_change mean
    # the labelled state tracks the true high-mean regime
    assert np.corrcoef(hmm_full.prob.values, truth.values)[0, 1] > 0.6
    a = rc.fit_hmm_causal(X, OOS, label_feature="spread_change", seeds=(7,))
    b = rc.fit_hmm_causal(X, OOS, label_feature="spread_change", seeds=(7,))
    np.testing.assert_array_equal(a.prob.values, b.prob.values)


def test_hmm_nan_rows_are_nan(data):
    X, _ = data
    Xn = X.copy(); Xn.iloc[5, 0] = np.nan
    r = rc.fit_hmm_causal(Xn, OOS, label_feature="spread_change", seeds=(42,))
    assert np.isnan(r.prob.iloc[5]) and r.prob.notna().sum() == len(X) - 1


# ─── Markov-switching ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ms_full(data):
    X, _ = data
    return rc.fit_ms_causal(X["spread_change"], OOS)


def test_ms_filtered_differs_from_smoothed(data, ms_full):
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
    X, _ = data
    mod = MarkovRegression(X["spread_change"].values, k_regimes=2, switching_variance=True)
    sm = np.asarray(mod.smooth(ms_full.model.params).smoothed_marginal_probabilities)
    sm = sm if sm.shape[0] == len(X) else sm.T
    j = int(np.argmax([ms_full.model.params[ms_full.model.model.param_names.index(f"sigma2[{i}]")] for i in range(2)]))
    assert abs(sm[-1, j] - ms_full.prob.iloc[-1]) < 1e-8
    assert np.abs(sm[:-1, j] - ms_full.prob.values[:-1]).max() > 0.05


def test_ms_no_future_dependence(data, ms_full):
    X, _ = data
    cut = 1300
    part = rc.fit_ms_causal(X["spread_change"].iloc[: cut + 1], OOS)
    np.testing.assert_allclose(part.prob.values, ms_full.prob.values[: cut + 1], atol=1e-9)


def test_ms_is_only_fit(data, ms_full):
    X, _ = data
    y2 = X["spread_change"].copy()
    oos = y2.index >= OOS
    y2[oos] = y2[oos].values * 4.0 - 2.0
    alt = rc.fit_ms_causal(y2, OOS)
    np.testing.assert_allclose(alt.params["params_is"], ms_full.params["params_is"], atol=1e-12)
    is_rows = X.index < OOS
    np.testing.assert_allclose(alt.prob.values[is_rows], ms_full.prob.values[is_rows], atol=1e-10)
    sig = np.array(ms_full.params["label_key_sorted"])
    assert sig[-1] > sig[0]  # reported regime is the high-variance one


def test_ms_refuses_target_return(data):
    X, _ = data
    with pytest.raises(ValueError):
        rc.fit_ms_causal(X["spread_change"].rename("spy_ret"), OOS)
    with pytest.raises(ValueError):
        rc.fit_hmm_causal(X.rename(columns={"vix": "spy_ret"}), OOS)


def test_min_is_rows_guard_and_override(data):
    X, _ = data
    short = X.iloc[:120]                                    # 80 IS rows before 2010-05-01 (< 50*2)
    with pytest.raises(ValueError, match="too few in-sample rows"):
        rc.fit_hmm_causal(short, "2010-05-01", label_feature="spread_change")
    r = rc.fit_hmm_causal(short, "2010-05-01", label_feature="spread_change", min_is_rows=40)
    assert r.n_fit < 100 and r.prob.notna().all()
    with pytest.raises(ValueError, match="too few in-sample rows"):
        rc.fit_ms_causal(short["spread_change"], "2010-05-01")


def test_hmm_variance_labelling(data):
    X, s = data
    r = rc.fit_hmm_causal(X[["spread_change"]], OOS, label_feature="spread_change", label="max_variance")
    assert r.params["label_key_sorted"][1] > r.params["label_key_sorted"][0]
    # the high-variance state is the true regime 1 (sd 1.5 vs 0.6)
    agree = ((r.prob > 0.5).astype(int) == s)[r.prob.notna()].mean()
    assert agree > 0.8
    r_min = rc.fit_hmm_causal(X[["spread_change"]], OOS, label_feature="spread_change", label="min_variance")
    assert np.allclose((r.prob + r_min.prob).dropna(), 1.0)
