"""Mechanism-agnostic leak tests (R7.3 truncation, perturbation of the future) on a selected candidate.

Truncation: rebuild the track from data available up to a cut c (revised: rows <= c; real-time: the vintage
panel as published by c) and require the candidate's position on every row <= c to equal the full run.
Perturbation: replace every reading after c (and every vintage published after c) by noise and require the
same. Cuts before the OOS start may differ only for IS-frozen objects (regime fits, IS-quantile thresholds);
those candidates are reported as exempt at IS cuts.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from .candidates import Candidate
from .engine import TrackInputs
from .positions import position_matrix
from .spec import ISQuantile, PairSpec


def candidate_positions(spec: PairSpec, ti: TrackInputs, cand: Candidate) -> pd.Series:
    pre = np.asarray(ti.index < pd.Timestamp(spec.oos_start))
    return pd.Series(position_matrix(spec, ti.lagged[cand.lead], [cand], pre)[:, 0], index=ti.index)


def is_frozen(spec: PairSpec, cand: Candidate) -> bool:
    """True when the rule uses an object fitted on the IS window (regime fit or IS-quantile threshold)."""
    if spec.signals[cand.signal] in spec.regime_columns:
        return True
    if cand.strategy != "P2":
        return isinstance(spec.rules(cand.signal)[cand.threshold].thr, ISQuantile)
    return False


def cuts(index: pd.DatetimeIndex, oos_start: str, ppy: int) -> dict[str, pd.Timestamp]:
    o = pd.Timestamp(oos_start)
    oos = index[index >= o]
    pre = index[index < o]
    out = {"oos_start": oos[0], "oos_50pct": oos[len(oos) // 2], "end_minus_1y": index[-1 - ppy]}
    if len(pre) > 10:
        out["is_33pct"] = pre[len(pre) // 3]
        out["is_66pct"] = pre[2 * len(pre) // 3]
    return out


def compare(full: pd.Series, part: pd.Series, cut: pd.Timestamp, tol: float = 1e-9) -> dict:
    a = full.loc[:cut]
    b = part.reindex(a.index)
    same = ((a - b).abs() <= tol) | (a.isna() & b.isna())
    bad = a.index[~same.to_numpy()]
    return {"rows_checked": int(len(a)), "rows_differing": int(len(bad)),
            "first_difference": None if not len(bad) else bad[0].date().isoformat()}


def run_leak_tests(spec: PairSpec, cand: Candidate, full: TrackInputs,
                   truncated: Callable[[pd.Timestamp], TrackInputs],
                   perturbed: Callable[[pd.Timestamp], TrackInputs]) -> dict:
    """truncated(c) / perturbed(c) rebuild the track's inputs from data cut / scrambled after c."""
    base = candidate_positions(spec, full, cand)
    frozen = is_frozen(spec, cand)
    out = {"candidate": cand.key, "is_frozen_object": frozen, "cuts": {}}
    ok = True
    for name, c in cuts(full.index, spec.oos_start, spec.ppy).items():
        exempt = frozen and c < pd.Timestamp(spec.oos_start)
        rec = {"cut": c.date().isoformat(), "exempt_is_frozen": exempt}
        rec["truncation"] = compare(base, candidate_positions(spec, truncated(c), cand), c)
        rec["perturbation"] = compare(base, candidate_positions(spec, perturbed(c), cand), c)
        rec["pass"] = exempt or (rec["truncation"]["rows_differing"] == 0 and rec["perturbation"]["rows_differing"] == 0)
        ok &= rec["pass"]
        out["cuts"][name] = rec
    out["pass"] = bool(ok)
    return out


def truncate_vintages(vint: pd.DataFrame, cut: pd.Timestamp) -> pd.DataFrame:
    """The vintage panel as it stood at the close of `cut`: rows published by then, still open at that date."""
    v = vint[vint.realtime_start <= cut].copy()
    v.loc[v.realtime_end > cut, "realtime_end"] = pd.Timestamp("2262-01-01")
    return v


def perturb_vintages(vint: pd.DataFrame, cut: pd.Timestamp, seed: int = 7) -> pd.DataFrame:
    """Scramble every value first published after `cut` (later vintages and revisions)."""
    v = vint.copy()
    m = v.realtime_start > cut
    v.loc[m, "value"] = v.loc[m, "value"] + np.random.default_rng(seed).normal(0, 5, int(m.sum()))
    return v


def perturb_levels(levels: pd.DataFrame, cut: pd.Timestamp, seed: int = 7) -> pd.DataFrame:
    """Scramble every reading stamped after `cut`."""
    lv = levels.copy()
    m = lv.index > cut
    rng = np.random.default_rng(seed)
    for c in lv.columns:
        sd = float(lv[c].std()) or 1.0
        lv.loc[m, c] = lv.loc[m, c] + rng.normal(0, 3 * sd, int(m.sum()))
    return lv
