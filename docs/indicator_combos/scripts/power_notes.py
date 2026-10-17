"""Power / minimum-detectable-effect notes for the registered endpoints (COMBINATORICS.md section 4).

SYNTHETIC ONLY: no project data and no asset returns are read. Every random draw is seeded.

1. Sharpe-ratio gap (Jobson-Korkie with Memmel's 2003 correction), monthly data, annualised Sharpe SR_a, T years:
     Var(SR_a1 - SR_a2) = (1/T) * [ 2(1 - rho) + (1/2)(SR_a1^2 + SR_a2^2 - 2 SR_a1 SR_a2 rho^2) / 12 ]
   (Memmel's formula holds per observation; with n = 12T monthly observations and SR_a = sqrt(12) SR_m the quadratic
   term is divided by 12.) MDE = (z_{1-alpha/(2m)} + z_{0.8}) * sqrt(VIF * Var).
2. Relative CVaR(5%) reduction: Monte Carlo with bivariate Student-t (df 5) monthly returns, 15% annual volatility,
   0.6% monthly mean, correlation rho; the overlay is (1 - delta) times a correlated copy of the benchmark, so its
   true CVaR is lower by the fraction delta. One-sided 5% test on the empirical relative reduction; MDE = smallest
   delta with power >= 0.8.
3. Interaction coefficient d (s = +/-1 balanced, regime share p, monthly excess-return s.d. sigma):
     Var(d) ~= sigma^2 / (n p) + sigma^2 / (n (1 - p)),  MDE = 2.8 * sqrt(VIF * Var(d)).
4. Episode-level exact tests: smallest number of episodes for which an all-favourable outcome reaches one-sided
   p <= alpha (sign / exact McNemar on discordant episodes, binomial 1/2).

Run:  python docs/indicator_combos/scripts/power_notes.py   ->  docs/indicator_combos/data/power_notes.json
"""
from __future__ import annotations

import json
from math import ceil, log, sqrt
from pathlib import Path

import numpy as np
from scipy.stats import norm

OUT = Path(__file__).resolve().parents[1] / "data" / "power_notes.json"
SEED = 20261017


def sharpe_mde(T, rho, sr, vif=1.0, m=1, power=0.8, alpha=0.05):
    z = norm.ppf(1 - alpha / (2 * m)) + norm.ppf(power)
    v = (2 * (1 - rho) + 0.5 * (2 * sr ** 2 - 2 * sr * sr * rho ** 2) / 12) / T
    return round(float(z * sqrt(vif * v)), 2)


def cvar(x: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Empirical CVaR (positive loss) per row: mean of the worst ceil(q n) returns."""
    k = max(1, int(ceil(q * x.shape[1])))
    return -np.sort(x, axis=1)[:, :k].mean(axis=1)


def cvar_mde(T: int, rho: float, sims: int = 4000, rng=None) -> dict:
    n = 12 * T
    df, mu, sd = 5, 0.006, 0.15 / sqrt(12)
    L = np.linalg.cholesky(np.array([[1, rho], [rho, 1]]))

    def draw():
        z = rng.standard_normal((sims, n, 2)) @ L.T
        w = np.sqrt(df / rng.chisquare(df, (sims, n, 1)))
        e = z * w * sqrt((df - 2) / df)
        return mu + sd * e[..., 0], mu + sd * e[..., 1]

    b, a = draw()
    null = 1 - cvar(a) / cvar(b)
    thr = float(np.percentile(null, 95))
    out = {"n_months": n, "tail_obs": int(ceil(0.05 * n)), "null_95pct_rel_reduction": round(thr, 3)}
    b, a = draw()
    for delta in np.arange(0.0, 0.95, 0.025):
        r = 1 - cvar((1 - delta) * a) / cvar(b)
        if np.mean(r > thr) >= 0.8:
            out["mde_rel_reduction_80pct_power"] = round(float(delta), 3)
            break
    else:
        out["mde_rel_reduction_80pct_power"] = ">0.9"
    return out


def interaction_mde(T: int, p: float, sigma: float = 4.5, vif: float = 1.0) -> float:
    n = 12 * T
    return round(2.8 * sqrt(vif * (sigma ** 2 / (n * p) + sigma ** 2 / (n * (1 - p)))), 2)


def main():
    rng = np.random.default_rng(SEED)
    res = {"seed": SEED, "synthetic_only": True}
    res["sharpe_mde_monthly_memmel"] = {
        f"T{T}": {f"rho{r}": [sharpe_mde(T, r, 0.5), sharpe_mde(T, r, 1.0)] for r in (0.5, 0.7, 0.8, 0.9)}
        for T in (3, 8, 16, 25)}
    res["sharpe_mde_rho0.8_sr0.5_vif1.5"] = {f"m{m}": [sharpe_mde(T, 0.8, 0.5, 1.5, m) for T in (3, 8, 16, 25)]
                                            for m in (1, 4, 10, 50)}
    res["cvar5_rel_reduction"] = {f"T{T}_rho{r}": cvar_mde(T, r, rng=rng) for T in (3, 8, 16, 25) for r in (0.8, 0.9)}
    res["interaction_mde_pp_per_month_sigma4.5"] = {
        f"T{T}": {f"p{p}": interaction_mde(T, p) for p in (0.1, 0.2, 0.3)} for T in (3, 8, 16, 25)}
    res["episodes_needed_all_favourable"] = {f"alpha{a}": int(ceil(log(a) / log(0.5))) for a in (0.05, 0.025, 0.0125)}
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
