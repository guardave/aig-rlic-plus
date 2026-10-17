"""Scoring: windowed returns (dropna or deployable), Sharpe and the performance block, exposure, trades."""
from __future__ import annotations

import numpy as np


def window(R: np.ndarray, mask: np.ndarray, scoring: str) -> np.ndarray:
    """Rows of R inside `mask`. deployable: an undefined position earns cash (0) (R5.1, ECON-T4);
    dropna: undefined rows are left NaN and ignored by the statistics (legacy replay only)."""
    X = R[mask]
    if scoring == "deployable":
        return np.nan_to_num(X, nan=0.0)
    if scoring != "dropna":
        raise ValueError(scoring)
    return X


def col_sharpe(X: np.ndarray, ppy: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(n, sd, sharpe) per column, NaN-aware, sd with ddof=1. Sharpe := 0 when n < 2 or sd == 0 (all cash)."""
    X = np.atleast_2d(X.T).T if X.ndim == 1 else X
    n = np.sum(~np.isnan(X), axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        mu = np.where(n > 0, np.nansum(X, axis=0) / np.maximum(n, 1), np.nan)
        dev = np.where(np.isnan(X), 0.0, X - mu)
        sd = np.sqrt(np.sum(dev ** 2, axis=0) / np.maximum(n - 1, 1))
        sd = np.where(n > 1, sd, np.nan)
        sh = np.where((n > 1) & (sd > 0), mu / sd * np.sqrt(ppy), 0.0)
    return n, sd, sh


def perf(r: np.ndarray, ppy: int, ann_return: str = "geometric") -> dict:
    """Performance block of one return series (NaN rows dropped). ann_return: geometric (CAGR) or arithmetic."""
    r = np.asarray(r, float)
    r = r[~np.isnan(r)]
    n = len(r)
    if n < 2 or r.std(ddof=1) == 0:
        return {"sharpe": 0.0, "sortino": 0.0, "calmar": 0.0, "ann_return": 0.0, "ann_vol": 0.0,
                "max_drawdown": 0.0, "win_rate": float((r > 0).mean()) if n else 0.0, "n": n}
    mu, sd = r.mean(), r.std(ddof=1)
    ar = float(np.prod(1 + r) ** (ppy / n) - 1) if ann_return == "geometric" else float(mu * ppy)
    eq = np.cumprod(1 + r)
    mdd = float(np.min(eq / np.maximum.accumulate(eq) - 1))
    neg = r[r < 0]
    if ann_return == "geometric":
        sortino = ar / (neg.std(ddof=1) * np.sqrt(ppy)) if len(neg) > 1 and neg.std(ddof=1) > 0 else 0.0
    else:
        sortino = mu / neg.std(ddof=1) * np.sqrt(ppy) if len(neg) > 1 and neg.std(ddof=1) > 0 else 0.0
    return {"sharpe": float(mu / sd * np.sqrt(ppy)), "sortino": float(sortino),
            "calmar": float(ar / abs(mdd)) if mdd < 0 else 0.0, "ann_return": ar,
            "ann_vol": float(sd * np.sqrt(ppy)), "max_drawdown": mdd, "win_rate": float((r > 0).mean()), "n": n}


def exposure(pos: np.ndarray, mask: np.ndarray, strategy: str) -> float:
    """Mean position over the defined rows in the window (P3: share of rows long)."""
    p = pos[mask]
    p = p[~np.isnan(p)]
    if not len(p):
        return float("nan")
    return float((p > 0).mean()) if strategy == "P3" else float(p.mean())


def trades(pos: np.ndarray, mask: np.ndarray, mode: str, ppy: int) -> tuple[int, float]:
    """(n_trades, annual_turnover) over the defined rows of the window. abs_sum: n = sum |dpos|;
    gt_0.05: n = number of changes larger than 0.05. Turnover = sum |dpos| / max(years, 1)."""
    p = pos[mask]
    p = p[~np.isnan(p)]
    if len(p) < 2:
        return 0, 0.0
    d = np.abs(np.diff(p))
    n = int((d > 0.05).sum()) if mode == "gt_0.05" else int(d.sum())
    return n, float(d.sum() / max(len(p) / ppy, 1))


def first_valid(R: np.ndarray) -> np.ndarray:
    """Row number of each column's first non-NaN return (len(R) when none)."""
    ok = ~np.isnan(R)
    return np.where(ok.any(axis=0), ok.argmax(axis=0), len(R))
