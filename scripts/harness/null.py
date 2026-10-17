"""R7.1 null tournament: break the indicator-return link by a circular shift, rerun the same selection, K draws.

  revised / market track: the RAW level inputs are circularly shifted inside their data span and every
      transform, threshold and regime fit is recomputed (R7.1 'run the full pipeline').
  real-time track (decision 3): the vintage panel is shifted as a block. Row u receives the whole real-time
      information set of row u - k (the vintage visible at that row's window open and the readings it implies),
      so the revision structure moves together.
Offsets: uniform on [m, n - m], m = max(36 months in native periods, 20% of n); draw k uses seed 20261016 + k.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from .engine import TrackInputs, TrackResult, run_tournament
from .spec import PairSpec

SEED_BASE = 20261016


def offsets(n: int, ppy: int, K: int, seed_base: int = SEED_BASE) -> list[int]:
    m = max(3 * ppy, int(np.ceil(0.2 * n)))
    if n - m < m:
        raise ValueError(f"span {n} too short for a circular-shift null (m={m})")
    return [int(np.random.default_rng(seed_base + k).integers(m, n - m + 1)) for k in range(K)]


def roll_span(obj, k: int, start: int = 0, stop: int | None = None):
    """Circularly shift rows [start, stop) of a Series / DataFrame / array by k (row u gets row u - k)."""
    stop = len(obj) if stop is None else stop
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        vals = obj.to_numpy().copy()
        vals[start:stop] = np.roll(vals[start:stop], k, axis=0)
        return (pd.Series(vals, index=obj.index, name=obj.name) if isinstance(obj, pd.Series)
                else pd.DataFrame(vals, index=obj.index, columns=obj.columns))
    out = np.array(obj, copy=True)
    out[start:stop] = np.roll(out[start:stop], k, axis=0)
    return out


def data_span(levels: pd.DataFrame) -> tuple[int, int]:
    """[first, last + 1) rows where any level column is observed."""
    ok = levels.notna().any(axis=1).to_numpy()
    rows = np.flatnonzero(ok)
    return int(rows[0]), int(rows[-1]) + 1


def realtime_block_shift(ti: TrackInputs, k: int) -> TrackInputs:
    """Shift every lead's real-time frame by k rows inside the span where real-time data exist."""
    any_rows = np.zeros(len(ti.index), bool)
    for f in ti.lagged.values():
        any_rows |= f.notna().any(axis=1).to_numpy()
    rows = np.flatnonzero(any_rows)
    s, e = int(rows[0]), int(rows[-1]) + 1
    return TrackInputs(ti.name, ti.index, ti.ret, {L: roll_span(f, k, s, e) for L, f in ti.lagged.items()},
                       dict(ti.meta, null_shift=k))


def _timing_sharpe(res: TrackResult, j: int, ppy: int) -> float:
    """OOS Sharpe of the exposure-matched timing return s_t - mean(exposure) * r_t (zero mean without skill)."""
    s = np.nan_to_num(res.returns[:, j], nan=0.0)[res.oos_mask]
    r = np.nan_to_num(res.ret, nan=0.0)[res.oos_mask]
    pos = res.positions[:, j]
    if res.spec.position_shift:
        pos = np.concatenate([[np.nan] * res.spec.position_shift, pos[:-res.spec.position_shift]])
    e = np.nanmean(np.where(np.isnan(pos), 0.0, pos)[res.oos_mask])
    t = s - e * r
    return float(t.mean() / t.std(ddof=1) * np.sqrt(ppy)) if t.std(ddof=1) > 0 else 0.0


def draw_record(res: TrackResult) -> dict:
    """Statistics recorded per draw (R7.1) for the selection actually used."""
    tab = res.table
    valid = tab[tab["valid"]]
    if res.selection is None or valid.empty:
        return {"is_max": np.nan, "selection_stat": np.nan, "winner_oos": np.nan, "timing_sharpe": np.nan,
                "lead": np.nan, "lead_pos": np.nan, "grid_edge": np.nan, "winner_key": None}
    w = res.selection["winner"]
    leads = list(res.spec.leads)
    lead = int(tab.loc[w, "lead"])
    return {"is_max": float(valid["is_sharpe"].max()), "selection_stat": float(res.selection.get("score",
            tab.loc[w, "is_sharpe"])), "winner_is": float(tab.loc[w, "is_sharpe"]),
            "winner_oos": float(tab.loc[w, "oos_sharpe"]), "timing_sharpe": _timing_sharpe(res, int(w), res.spec.ppy),
            "lead": lead, "lead_pos": leads.index(lead), "grid_edge": lead in (leads[0], leads[-1]),
            "winner_key": tab.loc[w, "key"]}


def run_null(spec: PairSpec, make_inputs: Callable[[int], TrackInputs], n_span: int, K: int = 100,
             legacy: bool = False) -> pd.DataFrame:
    """K draws; make_inputs(k) returns the shifted track inputs for offset k."""
    rows = []
    for d, k in enumerate(offsets(n_span, spec.ppy, K)):
        res = run_tournament(spec, make_inputs(k), legacy=legacy, full_table=False)
        rows.append({"draw": d, "seed": SEED_BASE + d, "offset": k, **draw_record(res)})
    return pd.DataFrame(rows)


def summarize(null: pd.DataFrame, actual: dict, grid_len: int) -> dict:
    """Percentiles of the actual winner within the null, R5.7 edge-share check and R7.1 PASS."""
    K = int(null["is_max"].notna().sum())

    def pct(col, val):
        x = null[col].dropna().to_numpy()
        if not len(x) or val is None or np.isnan(val):
            return None, None
        return round(float((x < val).mean()), 4), round(float((x >= val).mean()), 4)

    p_is = pct("is_max", actual.get("is_max"))
    p_j = pct("selection_stat", actual.get("selection_stat"))
    p_oos = pct("winner_oos", actual.get("winner_oos"))
    edge = null["grid_edge"].dropna().astype(bool)
    uni = min(2 / grid_len, 1.0) if grid_len else np.nan
    bound = uni + 3 * np.sqrt(uni * (1 - uni) / max(K, 1))
    st = null["timing_sharpe"].dropna()
    pass_tol = max(0.10, 2 * st.std(ddof=1) / np.sqrt(max(len(st), 1))) if len(st) > 1 else np.nan
    hist_counts, hist_bins = np.histogram(null["selection_stat"].dropna(), bins=20) if K else ([], [])
    return {
        "n_draws": K, "method": "circular shift of the raw input (revised/market) or vintage block (real-time); "
        "same selection rule; R7.1", "seed_base": SEED_BASE,
        "is_max_percentile": p_is[0], "p_is": p_is[1],
        "selection_stat_percentile": p_j[0], "p_selection_stat": p_j[1],
        "winner_oos_percentile": p_oos[0], "p_oos": p_oos[1],
        "null_is_max_p5_p50_p95": [round(float(v), 4) for v in np.nanpercentile(null["is_max"], [5, 50, 95])] if K else None,
        "null_winner_oos_median": round(float(null["winner_oos"].median()), 4) if K else None,
        "edge_share": round(float(edge.mean()), 4) if len(edge) else None, "edge_share_uniform": round(uni, 4),
        "edge_share_bound": round(float(bound), 4), "edge_flag": bool(len(edge) and edge.mean() > bound),
        "timing_sharpe_mean": round(float(st.mean()), 4) if len(st) else None,
        "timing_sharpe_sd": round(float(st.std(ddof=1)), 4) if len(st) > 1 else None,
        "r71_pass": bool(len(st) > 1 and abs(st.mean()) <= pass_tol),
        "null_scores_hist": {"bins": [round(float(b), 4) for b in hist_bins], "counts": [int(c) for c in hist_counts]},
    }
