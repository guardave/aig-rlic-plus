"""Position rules (P1 long/cash, P2 signal strength, P3 long/short) on lagged rule inputs, as a matrix.

Positions are NaN wherever the rule variable or its threshold is undefined; how a NaN position is scored
(dropped or held as cash) is decided in metrics, never here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .candidates import Candidate, p2_col, thr_col, x_col
from .spec import ISQuantile, PairSpec


def _bull(x: np.ndarray, thr: np.ndarray, direction: str, strict: bool) -> np.ndarray:
    if direction == "countercyclical":
        return x < thr if strict else x <= thr
    return x > thr if strict else x >= thr


def is_quantile_threshold(x: np.ndarray, is_rows: np.ndarray, thr: ISQuantile, mode: str = "expanding") -> np.ndarray:
    """Per-row ISQuantile threshold (see spec.ISQuantile). mode "expanding": IS rows use the quantile of the IS
    readings strictly before them (min_periods warm-up), OOS rows the quantile over all IS rows; mode "full"
    (legacy replay only): the all-IS quantile on every row."""
    xi = x[is_rows]
    xi = xi[~np.isnan(xi)]
    frozen = np.quantile(xi, thr.q) if len(xi) else np.nan
    if mode == "full":
        return np.full(len(x), frozen)
    if mode != "expanding":
        raise ValueError(mode)
    s = pd.Series(np.where(is_rows, x, np.nan))
    exp = s.expanding(min_periods=thr.min_periods).quantile(thr.q).shift(1).to_numpy()
    return np.where(is_rows, exp, frozen)


def position_matrix(spec: PairSpec, lagged: pd.DataFrame, cands: list[Candidate], is_rows: np.ndarray,
                    is_quantile: str = "expanding") -> np.ndarray:
    """(rows x len(cands)) positions from one lead's lagged reading frame. `is_rows` marks the in-sample rows
    used to calibrate ISQuantile thresholds (`is_quantile`: expanding | full, see is_quantile_threshold)."""
    n = len(lagged)
    out = np.full((n, len(cands)), np.nan)
    rules = {s: spec.rules(s) for s in {c.signal for c in cands}}
    for j, c in enumerate(cands):
        if c.strategy == "P2":
            frac = lagged[p2_col(c.signal)].to_numpy(float)
            pos = (1 - frac) if c.direction == "countercyclical" else frac
            out[:, j] = np.clip(pos, 0, 1)
            continue
        rule = rules[c.signal][c.threshold]
        x = lagged[x_col(c.signal, rule.x_name)].to_numpy(float)
        if isinstance(rule.thr, ISQuantile):
            thr = is_quantile_threshold(x, is_rows, rule.thr, is_quantile)
        elif callable(rule.thr):
            thr = lagged[thr_col(c.signal, c.threshold)].to_numpy(float)
        else:
            thr = np.full(n, float(rule.thr))
        defined = ~np.isnan(x) & ~np.isnan(thr)
        bull = _bull(x, thr, c.direction, spec.strict_counter).astype(float)
        pos = bull if c.strategy == "P1" else bull * 2 - 1
        out[:, j] = np.where(defined, pos, np.nan)
    return out


def strategy_returns(pos: np.ndarray, ret: np.ndarray, position_shift: int) -> np.ndarray:
    """Return earned by each candidate: position at row u - position_shift times the return of row u."""
    if position_shift == 0:
        p = pos
    else:
        p = np.vstack([np.full((position_shift, pos.shape[1]), np.nan), pos[:-position_shift]])
    return p * ret[:, None]
