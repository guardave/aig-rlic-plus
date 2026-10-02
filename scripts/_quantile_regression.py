"""Shared real quantile-regression helper (Step C #243 fix).

Replaces the fleet-wide bug where six pipelines computed their "quantile
regression" as ``scipy.stats.linregress`` (OLS) inside a ``for qtile in [...]``
loop — the ``qtile`` variable was never used, so every quantile row carried the
*identical* OLS slope. The chart therefore always looked "flat across quantiles"
and the narratives claimed "no tail asymmetry" from an analysis that was never
run (re-opened issue #243, Import Price Index x SPY).

This module provides one correct implementation used by every pipeline:

  * ``fit_quantile_regression`` — real ``statsmodels`` ``QuantReg`` estimated
    separately at each requested tau, returning coef / se / p / n per quantile.
  * a cross-quantile slope-equality **Wald test** (bootstrap covariance), so a
    narrative may only claim "uniform / no tail asymmetry" when the test does
    not reject equality. The test is reproducible (fixed seed).

Design mirrors ``scripts/_ci_band.py`` / ``scripts/_quartile_chart.py``:
single implementation, imported by the per-pair generators rather than copied.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# Canonical quantile grid: widened beyond the old [0.25, 0.5, 0.75] interquartile
# set to include the 0.10 / 0.90 tails, so a "crash tail" claim is at least
# estimated rather than asserted about untested regions (#243 re-open note).
DEFAULT_QUANTILES: tuple[float, ...] = (0.10, 0.25, 0.50, 0.75, 0.90)

# Bootstrap replications for the cross-quantile equality test. Fixed seed keeps
# the published p-value reproducible (CLAUDE.md code standard).
_N_BOOT = 500
_SEED = 42


def fit_quantile_regression(
    x: pd.Series | np.ndarray,
    y: pd.Series | np.ndarray,
    quantiles: Sequence[float] = DEFAULT_QUANTILES,
) -> tuple[list[dict], dict]:
    """Estimate ``y ~ x`` by real quantile regression at each tau.

    Parameters
    ----------
    x, y : aligned 1-D signal / forward-return samples (NaNs dropped jointly).
    quantiles : taus to estimate (SPY forward-return quantiles).

    Returns
    -------
    (rows, test)
        rows : list of {quantile, coef, se, p_value, n} — one per tau, real
            per-quantile slopes (no longer identical across tau).
        test : {method, stat, df, p_value, reject_equality, n} for the joint
            H0 that the slope is equal across all taus. ``reject_equality`` is
            True when p < 0.05 (evidence of tail asymmetry); False means the
            data are consistent with a uniform effect.
    """
    df = pd.DataFrame({"x": np.asarray(x, dtype=float), "y": np.asarray(y, dtype=float)}).dropna()
    n = len(df)
    quantiles = list(quantiles)

    rows: list[dict] = []
    if n <= 20:
        # Too few observations for stable quantile fits — surface empties rather
        # than fabricate. Callers already guard on length in the OLS path.
        for q in quantiles:
            rows.append({"quantile": q, "coef": np.nan, "se": np.nan, "p_value": np.nan, "n": n})
        return rows, {"method": "bootstrap-wald", "stat": np.nan, "df": max(0, len(quantiles) - 1),
                      "p_value": np.nan, "reject_equality": False, "n": n}

    mod = smf.quantreg("y ~ x", df)
    betas = {}
    for q in quantiles:
        res = mod.fit(q=q)
        betas[q] = float(res.params["x"])
        rows.append({
            "quantile": q,
            "coef": float(res.params["x"]),
            "se": float(res.bse["x"]),
            "p_value": float(res.pvalues["x"]),
            "n": n,
        })

    test = _equality_wald(df, quantiles, betas)
    test["n"] = n
    return rows, test


def _equality_wald(df: pd.DataFrame, quantiles: list[float], betas: dict) -> dict:
    """Bootstrap Wald test of H0: slope equal across all taus.

    statsmodels fits each tau separately and gives no joint cross-tau
    covariance, so we bootstrap it: resample rows, refit every tau, and build
    the empirical covariance of the slope *differences* from the median tau.
    Wald = d' Σ⁻¹ d ~ χ²(k-1).
    """
    k = len(quantiles)
    if k < 2:
        return {"method": "bootstrap-wald", "stat": np.nan, "df": 0,
                "p_value": np.nan, "reject_equality": False}

    ref = 0.50 if 0.50 in quantiles else quantiles[len(quantiles) // 2]
    others = [q for q in quantiles if q != ref]
    d_obs = np.array([betas[q] - betas[ref] for q in others])

    rng = np.random.default_rng(_SEED)
    idx = np.arange(len(df))
    boot = []
    for _ in range(_N_BOOT):
        sample = df.iloc[rng.choice(idx, size=len(df), replace=True)]
        try:
            m = smf.quantreg("y ~ x", sample)
            bq = {q: float(m.fit(q=q).params["x"]) for q in quantiles}
            boot.append([bq[q] - bq[ref] for q in others])
        except Exception:
            continue

    boot_arr = np.asarray(boot)
    if boot_arr.shape[0] < 30:
        return {"method": "bootstrap-wald", "stat": np.nan, "df": len(others),
                "p_value": np.nan, "reject_equality": False}

    cov = np.cov(boot_arr, rowvar=False)
    cov = np.atleast_2d(cov)
    stat = float(d_obs @ np.linalg.pinv(cov) @ d_obs)
    dof = len(others)
    from scipy import stats as _st
    p = float(_st.chi2.sf(stat, dof))
    return {
        "method": "bootstrap-wald",
        "stat": stat,
        "df": dof,
        "p_value": p,
        "reject_equality": bool(p < 0.05),
    }
