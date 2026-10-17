"""R7.1 null tournament: break the indicator-return link by a circular shift, rerun the same selection, K draws.

The RAW indicator is shifted and the whole pipeline is rebuilt for every draw (Codex B0 fix):
  revised / market track: the raw level inputs are circularly shifted inside their data span and every
      transform, threshold and regime fit is recomputed.
  real-time track (decision 3): inside EVERY vintage, the value of reference period d is replaced by that
      vintage's value of period d - k (circular over the reference-period grid of the latest vintage). A source
      period that this vintage does not contain gives a MISSING value (never a value from another vintage:
      that would import later information); missing readings are handled like real missing data (no signal,
      position undefined, scored by the metrics' NaN rule). Each vintage keeps its own release structure
      (which periods it contains, and when it was published), and realtime_inputs, transforms and thresholds
      are rebuilt per draw. At large offsets the wrapped (missing) part can cover the whole in-sample window
      of the early vintages, so the admissible set is restricted UP FRONT to offsets that leave a usable
      training window (some candidate meets the R3.3 eligibility rule; max_usable_offset, found by binary
      search because usability is monotone in k); offsets are then drawn from that set. An offset can still
      be eligible yet have no VALID rule (exposure / turnover filters): that draw records no winner and is
      excluded; n_draws counts draws with a winner, the percentiles are computed from them, and
      n_admissible_offsets / n_draws_without_winner are reported (cc MAIN: 56 admissible, 55 with a winner).
Offsets: DISTINCT admissible values in [m, n - m], m = max(36 months in native periods, 20% of n), drawn without
replacement (seed 20261016); all of them when there are at most K. R7.1 is calibrated for the dependence between
neighbouring offsets: the SE of the mean timing Sharpe is a Bartlett (Newey-West) long-run SE over the draws
ordered by offset, with a bandwidth covering one year of shift (see summarize).
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from .engine import TrackInputs, TrackResult, any_eligible, run_tournament
from .spec import PairSpec

SEED_BASE = 20261016


def admissible(n: int, ppy: int, max_offset: int | None = None) -> np.ndarray:
    m = max(3 * ppy, int(np.ceil(0.2 * n)))
    if n - m < m:
        raise ValueError(f"span {n} too short for a circular-shift null (m={m})")
    hi = n - m if max_offset is None else min(n - m, max_offset)
    return np.arange(m, hi + 1)


def max_usable_offset(spec: PairSpec, make_inputs: Callable[[int], TrackInputs], n: int) -> int | None:
    """Real-time track: the largest admissible offset whose shifted inputs still leave a usable training window
    (some candidate meets the R3.3 eligibility rule). Without cross-vintage fill, the missing (wrapped) part of
    every vintage only grows with the offset, so usability is monotone in k and a binary search over the
    admissible range finds the cut. None when not even the smallest admissible offset is usable."""
    adm = admissible(n, spec.ppy)
    lo, hi = 0, len(adm) - 1
    if not any_eligible(spec, make_inputs(int(adm[lo]))):
        return None
    if any_eligible(spec, make_inputs(int(adm[hi]))):
        return int(adm[hi])
    while hi - lo > 1:                    # invariant: adm[lo] usable, adm[hi] not
        mid = (lo + hi) // 2
        if any_eligible(spec, make_inputs(int(adm[mid]))):
            lo = mid
        else:
            hi = mid
    return int(adm[lo])


def offsets(n: int, ppy: int, K: int, seed: int = SEED_BASE, max_offset: int | None = None) -> list[int]:
    """K distinct admissible offsets (all of them when there are at most K), drawn without replacement."""
    adm = admissible(n, ppy, max_offset)
    if len(adm) <= K:
        return [int(x) for x in adm]
    return [int(x) for x in np.random.default_rng(seed).choice(adm, size=K, replace=False)]


def shift_vintage_values(v: pd.Series, k: int, grid: pd.DatetimeIndex) -> pd.Series:
    """Real-time null transform of one vintage (see module doc): period d gets the vintage's OWN value of period
    grid[(pos(d) - k) mod N]; NaN when this vintage does not contain that period (no cross-vintage fill)."""
    pos = grid.get_indexer(v.index)
    keep = pos >= 0
    src = grid[(pos[keep] - k) % len(grid)]
    vals = v.reindex(src).to_numpy(dtype=float)
    return pd.Series(vals, index=v.index[keep]).sort_index()


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


def _timing_sharpe_all(res: TrackResult, cols: np.ndarray, ppy: int) -> np.ndarray:
    """Timing Sharpe (as _timing_sharpe) of many candidate columns at once."""
    S = np.nan_to_num(res.returns[:, cols], nan=0.0)[res.oos_mask]
    r = np.nan_to_num(res.ret, nan=0.0)[res.oos_mask]
    P = res.positions[:, cols]
    k = res.spec.position_shift
    if k:
        P = np.vstack([np.full((k, P.shape[1]), np.nan), P[:-k]])
    e = np.nanmean(np.where(np.isnan(P), 0.0, P)[res.oos_mask], axis=0)
    T = S - e[None, :] * r[:, None]
    sd = T.std(axis=0, ddof=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(sd > 0, T.mean(axis=0) / sd * np.sqrt(ppy), 0.0)


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
            "timing_sharpe_all_valid": float(np.mean(_timing_sharpe_all(res, valid.index.to_numpy(), res.spec.ppy))),
            "lead": lead, "lead_pos": leads.index(lead), "grid_edge": lead in (leads[0], leads[-1]),
            "winner_key": tab.loc[w, "key"]}


def run_null(spec: PairSpec, make_inputs: Callable[[int], TrackInputs], n_span: int, K: int = 100,
             legacy: bool = False, shuffle_returns_seed: int | None = None,
             max_offset: int | None = None) -> pd.DataFrame:
    """K draws; make_inputs(k) returns the shifted track inputs for offset k. shuffle_returns_seed (diagnostic
    only): the target returns are also randomly permuted, which removes their time path."""
    rows = []
    offs = offsets(n_span, spec.ppy, K, max_offset=max_offset)
    for d, k in enumerate(offs):
        ti = make_inputs(k)
        if shuffle_returns_seed is not None:
            r = ti.ret.copy()
            ok = ~np.isnan(r)
            r[ok] = np.random.default_rng(shuffle_returns_seed + d).permutation(r[ok])
            ti = TrackInputs(ti.name, ti.index, r, ti.lagged, ti.meta)
        res = run_tournament(spec, ti, legacy=legacy, full_table=False)
        rows.append({"draw": d, "seed": SEED_BASE, "offset": k, **draw_record(res)})
    out = pd.DataFrame(rows)
    out.attrs.update(n_admissible=int(len(admissible(n_span, spec.ppy, max_offset))), span=int(n_span),
                     max_offset=max_offset)
    return out


def dependent_se(x: np.ndarray, offs: np.ndarray, ppy: int) -> tuple[float, int]:
    """(SE of the mean, Bartlett bandwidth) for draws ordered by offset: draws whose offsets are close shift the
    same history by almost the same amount, so they are dependent. The bandwidth covers one year of shift
    (ppy / median offset gap draws, at least the Newey-West floor(4 (K/100)^(2/9)))."""
    order = np.argsort(offs)
    x = np.asarray(x, float)[order]
    K = len(x)
    gaps = np.diff(np.sort(offs))
    gap = float(np.median(gaps)) if len(gaps) else 1.0
    L = int(min(K - 1, max(np.floor(4 * (K / 100) ** (2 / 9)), np.ceil(ppy / max(gap, 1.0)))))
    e = x - x.mean()
    lrv = e @ e / K
    for j in range(1, L + 1):
        lrv += 2 * (1 - j / (L + 1)) * (e[j:] @ e[:-j]) / K
    return float(np.sqrt(max(lrv, 0.0) / K)), L


def summarize(null: pd.DataFrame, actual: dict, grid_len: int, ppy: int = 12) -> dict:
    """Percentiles of the actual winner within the null, R5.7 edge-share check and R7.1 PASS (dependence-aware:
    |mean timing Sharpe| <= max(0.10, 2 SE) with SE from dependent_se)."""
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
    ok = null["timing_sharpe"].notna()
    st = null.loc[ok, "timing_sharpe"]
    se, bw = dependent_se(st.to_numpy(), null.loc[ok, "offset"].to_numpy(), ppy) if len(st) > 2 else (np.nan, 0)
    pass_tol = max(0.10, 2 * se) if len(st) > 2 else np.nan
    sd = float(st.std(ddof=1)) if len(st) > 1 else np.nan
    hist_counts, hist_bins = np.histogram(null["selection_stat"].dropna(), bins=20) if K else ([], [])
    return {
        "n_draws": K, "n_unique_offsets": int(null["offset"].nunique()),
        "n_draws_without_winner": int(null["selection_stat"].isna().sum()),
        "n_admissible_offsets": null.attrs.get("n_admissible"), "span": null.attrs.get("span"),
        "max_usable_offset": null.attrs.get("max_offset"),
        "method": "circular shift of the raw indicator (revised/market: level series; real-time: reference-period "
        "values inside every vintage), pipeline rebuilt per draw, same selection rule; distinct offsets; R7.1",
        "seed_base": SEED_BASE,
        "is_max_percentile": p_is[0], "p_is": p_is[1],
        "selection_stat_percentile": p_j[0], "p_selection_stat": p_j[1],
        "winner_oos_percentile": p_oos[0], "p_oos": p_oos[1],
        "null_is_max_p5_p50_p95": [round(float(v), 4) for v in np.nanpercentile(null["is_max"], [5, 50, 95])] if K else None,
        "null_winner_oos_median": round(float(null["winner_oos"].median()), 4) if K else None,
        "edge_share": round(float(edge.mean()), 4) if len(edge) else None, "edge_share_uniform": round(uni, 4),
        "edge_share_bound": round(float(bound), 4), "edge_flag": bool(len(edge) and edge.mean() > bound),
        "timing_sharpe_mean": round(float(st.mean()), 4) if len(st) else None,
        "timing_sharpe_sd": round(sd, 4) if len(st) > 1 else None,
        "timing_sharpe_se_dependent": round(se, 4) if len(st) > 2 else None, "timing_sharpe_se_bandwidth": bw,
        "timing_sharpe_effective_draws": round(float(sd ** 2 / se ** 2), 1) if len(st) > 2 and se > 0 else None,
        "r71_tolerance": round(float(pass_tol), 4) if len(st) > 2 else None,
        "timing_sharpe_mean_all_valid_candidates": round(float(null["timing_sharpe_all_valid"].mean()), 4)
        if "timing_sharpe_all_valid" in null else None,
        "r71_pass": bool(len(st) > 2 and abs(st.mean()) <= pass_tol),
        "null_scores_hist": {"bins": [round(float(b), 4) for b in hist_bins], "counts": [int(c) for c in hist_counts]},
    }
