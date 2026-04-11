"""
Retroactive HY-IG v2 Method Coverage Fix — Econometrics Evan — 2026-04-11

Purpose
-------
Apply Econometrics SOP Rule C1 (credit-equity mandatory method catalog) retroactively
to HY-IG v2. The prior v2 rerun (core_models_20260410/) silently dropped:

  1. Pre-whitened CCF (lags -20 .. +20)
  2. Transfer entropy (nonlinear information flow)
  3. Quartile-returns analysis (SPY returns conditional on HY-IG spread quartile)

Also produces the canonical tournament_winner.json per the
team-coordination.md schema.

Inputs (read-only)
------------------
  - data/hy_ig_v2_spy_daily_20260410.parquet          (master dataset)
  - results/hy_ig_v2_spy/winner_summary.json          (winner metrics)
  - results/hy_ig_v2_spy/tournament_results_20260410.csv  (benchmark row)

Outputs
-------
  - results/hy_ig_v2_spy/core_models_20260410/ccf_prewhitened.csv
  - results/hy_ig_v2_spy/core_models_20260410/transfer_entropy.csv
  - results/hy_ig_v2_spy/core_models_20260410/quartile_returns.csv
  - results/hy_ig_v2_spy/tournament_winner.json

Columns
-------
  ccf_prewhitened.csv     : lag, ccf, lower_ci, upper_ci, significant, arima_order, n_obs
  transfer_entropy.csv    : direction, te_value, permutation_p_value,
                            n_permutations, bandwidth, bin_method
  quartile_returns.csv    : quartile, mean_return, vol, sharpe, n_obs,
                            cutoff_lower, cutoff_upper
                            (plus: ann_return, max_drawdown for stakeholder display)

Non-destructive: this script does NOT touch any file that existed before 2026-04-11.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

ROOT = Path("/workspaces/aig-rlic-plus")
DATA_PATH = ROOT / "data" / "hy_ig_v2_spy_daily_20260410.parquet"
RESULTS_DIR = ROOT / "results" / "hy_ig_v2_spy"
CORE_DIR = RESULTS_DIR / "core_models_20260410"
WINNER_SUMMARY_PATH = RESULTS_DIR / "winner_summary.json"
TOURNAMENT_CSV_PATH = RESULTS_DIR / "tournament_results_20260410.csv"

OUT_CCF = CORE_DIR / "ccf_prewhitened.csv"
OUT_TE = CORE_DIR / "transfer_entropy.csv"
OUT_QR = CORE_DIR / "quartile_returns.csv"
OUT_WINNER_JSON = RESULTS_DIR / "tournament_winner.json"

RNG = np.random.default_rng(20260411)


def log(msg: str) -> None:
    print(f"[retro_fix] {msg}", flush=True)


# --------------------------------------------------------------------------- #
# Load master dataset
# --------------------------------------------------------------------------- #


def load_dataset() -> pd.DataFrame:
    log(f"Loading master dataset: {DATA_PATH}")
    df = pd.read_parquet(DATA_PATH)
    # We need the HY-IG spread and SPY daily log return
    needed = ["hy_ig_spread", "spy_ret", "hy_ig_zscore_252d"]
    for col in needed:
        if col not in df.columns:
            raise RuntimeError(f"Missing required column in master parquet: {col}")
    # Convert simple returns to log returns for stationarity
    df = df.copy()
    df["spy_log_ret"] = np.log1p(df["spy_ret"])
    log(
        f"Dataset loaded: {df.shape[0]:,} rows x {df.shape[1]} cols, "
        f"{df.index.min().date()} -> {df.index.max().date()}"
    )
    log(
        f"hy_ig_spread (percentage points): "
        f"min={df['hy_ig_spread'].min():.2f} max={df['hy_ig_spread'].max():.2f}"
    )
    return df


# --------------------------------------------------------------------------- #
# Pre-whitened CCF
# --------------------------------------------------------------------------- #


def fit_arima_bic(series: pd.Series, max_p: int = 5, max_q: int = 2) -> tuple:
    """Grid search over ARIMA(p,0,q) by BIC. Return (best_order, residuals)."""
    best_bic = np.inf
    best_order = None
    best_resid = None
    for p in range(0, max_p + 1):
        for q in range(0, max_q + 1):
            if p == 0 and q == 0:
                continue
            try:
                model = ARIMA(
                    series,
                    order=(p, 0, q),
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                res = model.fit(method_kwargs={"warn_convergence": False})
                if res.bic < best_bic:
                    best_bic = res.bic
                    best_order = (p, 0, q)
                    best_resid = res.resid
            except Exception:
                continue
    if best_order is None:
        raise RuntimeError("ARIMA BIC grid search failed for pre-whitening")
    return best_order, best_resid


def compute_prewhitened_ccf(df: pd.DataFrame, max_lag: int = 20) -> pd.DataFrame:
    log("Computing pre-whitened CCF (HY-IG spread -> SPY log return, lags -20..+20)")
    # Use spread in percent points (stationary via ARMA residuals). Drop NaN.
    joined = pd.concat(
        [df["hy_ig_spread"].rename("x"), df["spy_log_ret"].rename("y")], axis=1
    ).dropna()
    log(f"  Joined sample: {len(joined):,} rows")

    # Fit ARIMA to the indicator (spread). Pre-whiten both series by that filter.
    log("  Fitting ARIMA(p,0,q) to hy_ig_spread by BIC (max p=5, q=2)")
    order_x, resid_x = fit_arima_bic(joined["x"], max_p=5, max_q=2)
    log(f"  Best ARIMA for spread: {order_x}")

    # Apply the same filter (as residualization) to y: fit same order to y
    try:
        res_y_model = ARIMA(
            joined["y"],
            order=order_x,
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(method_kwargs={"warn_convergence": False})
        resid_y = res_y_model.resid
    except Exception as exc:
        log(f"  Warning: ARIMA{order_x} on SPY returns failed ({exc}); using ARIMA(1,0,0)")
        res_y_model = ARIMA(joined["y"], order=(1, 0, 0)).fit(
            method_kwargs={"warn_convergence": False}
        )
        resid_y = res_y_model.resid

    rx = pd.Series(resid_x, index=joined.index).dropna()
    ry = pd.Series(resid_y, index=joined.index).dropna()
    common = rx.index.intersection(ry.index)
    rx = rx.loc[common].values
    ry = ry.loc[common].values

    # Standardize residuals
    rx = (rx - rx.mean()) / rx.std(ddof=1)
    ry = (ry - ry.mean()) / ry.std(ddof=1)
    n = len(rx)
    ci_halfwidth = 1.96 / np.sqrt(n)
    log(f"  Residual series length: {n}, 95% CI half-width: +/-{ci_halfwidth:.4f}")

    # Lag convention: lag k means correlation of x(t) with y(t+k).
    #   k > 0  : x leads y (spread leads SPY return)
    #   k < 0  : y leads x (SPY leads spread)
    rows = []
    for k in range(-max_lag, max_lag + 1):
        if k >= 0:
            xa = rx[: n - k]
            ya = ry[k:]
        else:
            xa = rx[-k:]
            ya = ry[: n + k]
        corr = float(np.corrcoef(xa, ya)[0, 1])
        significant = bool(abs(corr) > ci_halfwidth)
        rows.append(
            {
                "lag": k,
                "ccf": round(corr, 6),
                "lower_ci": round(-ci_halfwidth, 6),
                "upper_ci": round(ci_halfwidth, 6),
                "significant": significant,
                "arima_order": f"({order_x[0]},{order_x[1]},{order_x[2]})",
                "n_obs": n,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT_CCF, index=False)
    log(f"  Wrote {OUT_CCF.relative_to(ROOT)} ({len(out)} rows)")
    sig_lags = out.loc[out["significant"], "lag"].tolist()
    log(f"  Significant lags (|ccf|>CI): {sig_lags[:15]}{'...' if len(sig_lags) > 15 else ''}")
    return out


# --------------------------------------------------------------------------- #
# Transfer entropy (Shannon, histogram-binned)
# --------------------------------------------------------------------------- #


def _shannon_entropy(counts: np.ndarray) -> float:
    """Shannon entropy (in nats) of a histogram, ignoring zero bins."""
    total = counts.sum()
    if total == 0:
        return 0.0
    p = counts.astype(float) / total
    nz = p[p > 0]
    return float(-(nz * np.log(nz)).sum())


def transfer_entropy_hist(
    source: np.ndarray, target: np.ndarray, n_bins: int = 6, lag: int = 1
) -> float:
    """
    TE(source -> target) = H(Y_t+1 | Y_t) - H(Y_t+1 | Y_t, X_t)
    Estimated via histogram binning on pre-discretized data.

    Returns the TE estimate in nats.
    """
    if len(source) != len(target):
        raise ValueError("source and target must have same length")
    # Lagged series
    y_future = target[lag:]
    y_past = target[:-lag]
    x_past = source[:-lag]
    # Discretize each variable using quantile bins (equal-frequency)
    def qbins(arr: np.ndarray) -> np.ndarray:
        edges = np.quantile(arr, np.linspace(0, 1, n_bins + 1))
        edges[0] -= 1e-9
        edges[-1] += 1e-9
        return np.clip(np.digitize(arr, edges[1:-1]), 0, n_bins - 1)

    yf = qbins(y_future)
    yp = qbins(y_past)
    xp = qbins(x_past)

    # 3D joint histogram of (yf, yp, xp)
    joint3 = np.zeros((n_bins, n_bins, n_bins), dtype=np.int64)
    for a, b, c in zip(yf, yp, xp):
        joint3[a, b, c] += 1
    # Marginal counts
    joint_yf_yp = joint3.sum(axis=2)          # (yf, yp)
    joint_yp_xp = joint3.sum(axis=0)          # (yp, xp)
    marg_yp = joint_yf_yp.sum(axis=0)         # (yp,)

    n = len(yf)
    # H(yf, yp, xp)
    h_yf_yp_xp = _shannon_entropy(joint3.flatten())
    # H(yp, xp)
    h_yp_xp = _shannon_entropy(joint_yp_xp.flatten())
    # H(yf, yp)
    h_yf_yp = _shannon_entropy(joint_yf_yp.flatten())
    # H(yp)
    h_yp = _shannon_entropy(marg_yp)

    # TE = H(yf|yp) - H(yf|yp,xp)
    #    = [H(yf,yp) - H(yp)] - [H(yf,yp,xp) - H(yp,xp)]
    te = (h_yf_yp - h_yp) - (h_yf_yp_xp - h_yp_xp)
    return float(te)


def transfer_entropy_with_pvalue(
    source: np.ndarray,
    target: np.ndarray,
    n_bins: int = 6,
    lag: int = 1,
    n_perm: int = 500,
) -> tuple[float, float]:
    te_obs = transfer_entropy_hist(source, target, n_bins=n_bins, lag=lag)
    perm_tes = np.empty(n_perm)
    # Block shuffle to partially preserve autocorrelation (simple circular shift).
    n = len(source)
    for i in range(n_perm):
        shift = int(RNG.integers(1, n - 1))
        shuffled = np.concatenate([source[shift:], source[:shift]])
        perm_tes[i] = transfer_entropy_hist(shuffled, target, n_bins=n_bins, lag=lag)
    p_value = float((np.sum(perm_tes >= te_obs) + 1) / (n_perm + 1))
    return te_obs, p_value


def compute_transfer_entropy(df: pd.DataFrame) -> pd.DataFrame:
    log("Computing transfer entropy (histogram estimator, 6 bins, lag=1, 500 perms)")
    joined = pd.concat(
        [df["hy_ig_spread"].rename("credit"), df["spy_log_ret"].rename("equity")],
        axis=1,
    ).dropna()
    log(f"  Joined sample: {len(joined):,} rows")

    credit = joined["credit"].values
    equity = joined["equity"].values

    rows = []
    for direction, src, tgt in [
        ("credit_to_equity", credit, equity),
        ("equity_to_credit", equity, credit),
    ]:
        log(f"  Estimating TE: {direction}")
        te, pval = transfer_entropy_with_pvalue(
            src, tgt, n_bins=6, lag=1, n_perm=500
        )
        log(f"    TE={te:.6f} nats, perm p-value={pval:.4f}")
        rows.append(
            {
                "direction": direction,
                "te_value": round(te, 6),
                "permutation_p_value": round(pval, 4),
                "n_permutations": 500,
                "bandwidth": 6,            # number of equal-frequency bins
                "bin_method": "quantile_6bins_lag1",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT_TE, index=False)
    log(f"  Wrote {OUT_TE.relative_to(ROOT)} ({len(out)} rows)")
    return out


# --------------------------------------------------------------------------- #
# Quartile-returns analysis
# --------------------------------------------------------------------------- #


def max_drawdown(returns: pd.Series) -> float:
    eq = (1.0 + returns.fillna(0.0)).cumprod()
    peak = eq.cummax()
    dd = (eq / peak) - 1.0
    return float(dd.min())


def compute_quartile_returns(df: pd.DataFrame) -> pd.DataFrame:
    log("Computing quartile-returns analysis (SPY returns conditional on HY-IG spread quartile)")
    panel = pd.concat(
        [df["hy_ig_spread"].rename("spread"), df["spy_ret"].rename("ret")], axis=1
    ).dropna()
    log(f"  Joined sample: {len(panel):,} rows")

    quantiles = panel["spread"].quantile([0.25, 0.5, 0.75]).values
    q_edges = [-np.inf, quantiles[0], quantiles[1], quantiles[2], np.inf]
    labels = ["Q1", "Q2", "Q3", "Q4"]
    panel["quartile"] = pd.cut(panel["spread"], bins=q_edges, labels=labels)

    rows = []
    for i, lab in enumerate(labels):
        mask = panel["quartile"] == lab
        rets = panel.loc[mask, "ret"]
        lower = float(q_edges[i]) if np.isfinite(q_edges[i]) else float(panel["spread"].min())
        upper = (
            float(q_edges[i + 1])
            if np.isfinite(q_edges[i + 1])
            else float(panel["spread"].max())
        )
        mean_daily = float(rets.mean())
        vol_daily = float(rets.std(ddof=1))
        ann_ret = (1.0 + mean_daily) ** 252 - 1.0
        ann_vol = vol_daily * np.sqrt(252)
        sharpe = (mean_daily / vol_daily) * np.sqrt(252) if vol_daily > 0 else np.nan
        mdd = max_drawdown(rets)
        rows.append(
            {
                "quartile": lab,
                "mean_return": round(mean_daily, 8),
                "vol": round(vol_daily, 8),
                "sharpe": round(sharpe, 4),
                "n_obs": int(mask.sum()),
                "cutoff_lower": round(lower, 4),
                "cutoff_upper": round(upper, 4),
                "ann_return": round(ann_ret, 6),
                "ann_vol": round(ann_vol, 6),
                "max_drawdown": round(mdd, 6),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT_QR, index=False)
    log(f"  Wrote {OUT_QR.relative_to(ROOT)} ({len(out)} rows)")

    # Q1 vs Q4 t-test
    q1 = panel.loc[panel["quartile"] == "Q1", "ret"].values
    q4 = panel.loc[panel["quartile"] == "Q4", "ret"].values
    t_stat, p_val = stats.ttest_ind(q1, q4, equal_var=False)
    log(f"  Q1 vs Q4 Welch t-test: t={t_stat:.3f}, p={p_val:.4f}")
    log(
        f"  Sharpe spread Q1->Q4: "
        f"{out.iloc[0]['sharpe']:.2f}  {out.iloc[1]['sharpe']:.2f}  "
        f"{out.iloc[2]['sharpe']:.2f}  {out.iloc[3]['sharpe']:.2f}"
    )
    return out


# --------------------------------------------------------------------------- #
# Tournament winner JSON
# --------------------------------------------------------------------------- #


def build_tournament_winner_json() -> dict:
    log("Building tournament_winner.json from winner_summary + tournament_results")
    with WINNER_SUMMARY_PATH.open() as f:
        winner = json.load(f)

    tourney = pd.read_csv(TOURNAMENT_CSV_PATH)
    bh_rows = tourney[tourney["signal"] == "BENCHMARK"]
    if bh_rows.empty:
        raise RuntimeError("No BENCHMARK row in tournament_results CSV")
    bh = bh_rows.iloc[0]

    winner_sharpe = float(winner["oos_sharpe"])
    winner_return = float(winner["oos_ann_return"])
    winner_mdd = float(winner["max_drawdown"])

    bh_sharpe = float(bh["oos_sharpe"])
    bh_return = float(bh["oos_ann_return"])
    bh_mdd = float(bh["max_drawdown"])

    delta_sharpe = round(winner_sharpe - bh_sharpe, 4)
    delta_return = round(winner_return - bh_return, 4)
    delta_mdd = round(winner_mdd - bh_mdd, 4)  # positive = improvement (less negative)

    # Strategy-objective classification per SOP Rule C1 handoff rule:
    #   min_mdd  if DD improvement dominates
    #   max_sharpe if Sharpe gain dominates
    #   max_return if return gain dominates
    # Normalize by the class range to compare apples to apples.
    sharpe_range = abs(bh_sharpe) if bh_sharpe != 0 else 1.0
    return_range = abs(bh_return) if bh_return != 0 else 1.0
    mdd_range = abs(bh_mdd) if bh_mdd != 0 else 1.0
    norm_sharpe = delta_sharpe / sharpe_range
    norm_return = delta_return / return_range
    norm_mdd = delta_mdd / mdd_range

    log(f"  Delta Sharpe: {delta_sharpe:+.3f} (normalized {norm_sharpe:+.3f})")
    log(f"  Delta Return: {delta_return:+.3f} (normalized {norm_return:+.3f})")
    log(f"  Delta MDD   : {delta_mdd:+.3f} (normalized {norm_mdd:+.3f})")

    dominants = {"min_mdd": norm_mdd, "max_sharpe": norm_sharpe, "max_return": norm_return}
    suggested = max(dominants, key=dominants.get)
    log(f"  Suggested strategy_objective: {suggested}")

    out = {
        "pair_id": "hy_ig_v2_spy",
        "winner": {
            "signal": winner.get("signal_display_name", winner.get("signal_code", "unknown")),
            "threshold": winner.get(
                "threshold_display_name", winner.get("threshold_code", "unknown")
            ),
            "strategy": winner.get(
                "strategy_display_name", winner.get("strategy_code", "unknown")
            ),
            "oos_sharpe": round(winner_sharpe, 4),
            "oos_ann_return": round(winner_return, 4),
            "max_drawdown": round(winner_mdd, 4),
            "annual_turnover": round(float(winner.get("annual_turnover", 0.0)), 4),
        },
        "benchmark": {
            "name": "Buy & Hold",
            "oos_sharpe": round(bh_sharpe, 4),
            "oos_ann_return": round(bh_return, 4),
            "max_drawdown": round(bh_mdd, 4),
        },
        "deltas": {
            "delta_sharpe": delta_sharpe,
            "delta_return": delta_return,
            "delta_max_drawdown": delta_mdd,
        },
        "suggested_strategy_objective": suggested,
    }

    with OUT_WINNER_JSON.open("w") as f:
        json.dump(out, f, indent=2)
    log(f"  Wrote {OUT_WINNER_JSON.relative_to(ROOT)}")
    return out


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> int:
    log("=== Retroactive HY-IG v2 Method Coverage Fix ===")
    log(f"Working dir: {ROOT}")
    # Pre-flight
    if not CORE_DIR.exists():
        raise RuntimeError(f"core_models dir missing: {CORE_DIR}")

    df = load_dataset()

    log("\n--- [1/4] Pre-whitened CCF ---")
    compute_prewhitened_ccf(df, max_lag=20)

    log("\n--- [2/4] Transfer Entropy ---")
    compute_transfer_entropy(df)

    log("\n--- [3/4] Quartile Returns ---")
    compute_quartile_returns(df)

    log("\n--- [4/4] Tournament Winner JSON ---")
    build_tournament_winner_json()

    log("\n=== All outputs produced successfully ===")
    for p in [OUT_CCF, OUT_TE, OUT_QR, OUT_WINNER_JSON]:
        log(f"  {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
