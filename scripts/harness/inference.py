"""Inference on the winner: paired block bootstrap of the OOS Sharpe gap vs B&H, Newey-West HAC t."""
from __future__ import annotations

import numpy as np


def paired_block_bootstrap_sharpe_diff(strat, bh, block, ppy, draws=5000, seed=42):
    """Paired circular block bootstrap of OOS Sharpe(strategy) - Sharpe(B&H): the same resampled blocks are
    applied to both series, so their dependence is kept. Returns observed, mean, 95% CI and P(diff <= 0).
    Adapted from pair_pipeline_nhs_spy.py (pkg13); the Sharpe uses the sample SD (ddof=1), the same estimator
    as every reported Sharpe (Codex B0: the pkg13 version used ddof=0)."""
    s, b = np.asarray(strat, float), np.asarray(bh, float)
    n = len(s)
    rng = np.random.default_rng(seed)

    def _sh(x):
        sd = x.std(ddof=1)
        return x.mean() / sd * np.sqrt(ppy) if sd > 0 else np.nan

    d = []
    for _ in range(draws):
        starts = rng.integers(0, n, size=int(np.ceil(n / block)))
        idx = np.concatenate([np.arange(k, k + block) % n for k in starts])[:n]
        d.append(_sh(s[idx]) - _sh(b[idx]))
    d = np.array(d)
    d = d[~np.isnan(d)]
    return {"observed": round(float(_sh(s) - _sh(b)), 4), "mean": round(float(d.mean()), 4),
            "ci_95": [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)],
            "p_diff_le_0": round(float((d <= 0).mean()), 4), "block_length": block, "draws": int(len(d)),
            "seed": seed, "method": "paired circular block bootstrap of OOS Sharpe(strategy) - Sharpe(B&H)"}


def nw_lag(n: int) -> int:
    """R6.2(a) Newey-West lag floor(4 (T/100)^(2/9))."""
    return int(np.floor(4 * (n / 100) ** (2 / 9)))


def hac_t_mean(r) -> dict:
    """Newey-West HAC t of the mean of a single-period return series, with the lag stored next to it."""
    import statsmodels.api as sm
    y = np.asarray(r, float)
    y = y[~np.isnan(y)]
    lag = nw_lag(len(y))
    m = sm.OLS(y, np.ones((len(y), 1))).fit(cov_type="HAC", cov_kwds={"maxlags": lag})
    return {"t": round(float(m.tvalues[0]), 4), "p_value": round(float(m.pvalues[0]), 4), "nw_lag": lag,
            "n": int(len(y))}
