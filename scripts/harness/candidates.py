"""Reading frame (all rule inputs on the indicator's own stamps) and the pre-declared candidate manifest (R4.1)."""
from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .spec import ISQuantile, PairSpec

P2_THRESHOLD = "-"   # P2 sizes on the trailing range and ignores the threshold: one candidate per signal/direction/lead


@dataclass(frozen=True)
class Candidate:
    signal: str
    threshold: str
    strategy: str
    direction: str
    lead: int

    @property
    def key(self) -> str:
        return f"{self.signal}|{self.threshold}|{self.strategy}|{self.direction}|{self.lead}"

    @property
    def family(self) -> tuple:
        """The lead-less tuple of R5.7 (signal, threshold, direction, position rule)."""
        return (self.signal, self.threshold, self.strategy, self.direction)


def x_col(signal: str, x_name: str) -> str:
    return f"x|{signal}|{x_name}"


def thr_col(signal: str, tcode: str) -> str:
    return f"t|{signal}|{tcode}"


def p2_col(signal: str) -> str:
    return f"p2|{signal}"


def reading_frame(spec: PairSpec, levels: pd.DataFrame) -> pd.DataFrame:
    """Every rule input computed from the level frame on its own stamps (before any lag). Run on the revised
    panel or inside one vintage. Constant and IS-quantile thresholds are not columns (see positions)."""
    feats = spec.features(levels)
    cols: dict[str, pd.Series] = {}
    for s, fcol in spec.signals.items():
        sig = feats[fcol].astype(float)
        for tcode, rule in spec.rules(s).items():
            xc = x_col(s, rule.x_name)
            if xc not in cols:
                cols[xc] = (rule.x_fn(sig) if rule.x_fn else sig).astype(float)
            if callable(rule.thr):
                cols[thr_col(s, tcode)] = pd.Series(rule.thr(sig), index=sig.index).astype(float)
        if "P2" in spec.strategies and s not in spec.binary_signals:
            w, mp = spec.p2_window
            lo, hi = sig.rolling(w, min_periods=mp).min(), sig.rolling(w, min_periods=mp).max()
            cols[p2_col(s)] = (sig - lo) / (hi - lo).replace(0, np.nan)
    return pd.DataFrame(cols, index=levels.index)


def manifest(spec: PairSpec, legacy: bool = False) -> list[Candidate]:
    """Pre-declared candidate list in the pair's loop order. P2/P3 are not declared on binary flags (R4.2);
    P2 is declared once per signal/direction/lead (threshold '-') unless replaying a legacy manifest."""
    out: list[Candidate] = []
    seen = set()
    for s in spec.signals:
        tcodes = list(spec.rules(s))
        axes = {"signal": [s], "threshold": tcodes, "strategy": list(spec.strategies),
                "direction": list(spec.directions), "lead": list(spec.leads)}
        for combo in itertools.product(*(axes[a] for a in spec.loop_order)):
            d = dict(zip(spec.loop_order, combo))
            if d["strategy"] in ("P2", "P3") and s in spec.binary_signals:
                continue
            if d["strategy"] == "P2" and not (legacy and spec.legacy.p2_per_threshold):
                d["threshold"] = P2_THRESHOLD
            c = Candidate(d["signal"], d["threshold"], d["strategy"], d["direction"], int(d["lead"]))
            if c.key in seen:
                continue
            seen.add(c.key)
            out.append(c)
    return out


def manifest_record(spec: PairSpec, cands: list[Candidate]) -> dict:
    """candidates_manifest JSON body (R4.1): the declared grid and constants, plus a hash of the candidate list."""
    keys = [c.key for c in cands]
    rules = {}
    for s in spec.signals:
        rules[s] = {t: {"variable": r.x_name,
                        "threshold": (f"is_quantile({r.thr.q})" if isinstance(r.thr, ISQuantile)
                                      else ("rolling/function of signal" if callable(r.thr) else float(r.thr)))}
                    for t, r in spec.rules(s).items()}
    return {
        "pair_id": spec.pair_id, "signals": spec.signals, "rules": rules, "strategies": list(spec.strategies),
        "directions": list(spec.directions), "leads": list(spec.leads), "lead_unit": spec.lead_unit,
        "binary_signals": sorted(spec.binary_signals), "min_is_n": spec.min_is_n, "ppy": spec.ppy,
        "oos_start": spec.oos_start, "exposure_bounds": list(spec.exposure_bounds),
        "max_is_turnover": spec.max_is_turnover, "min_is_trades": spec.min_is_trades,
        "position_shift": spec.position_shift, "n_candidates": len(keys),
        "candidates_sha256": hashlib.sha256(json.dumps(keys).encode()).hexdigest(),
    }


def distinct_series(positions: np.ndarray, valid: np.ndarray) -> tuple[int, dict[int, list[int]]]:
    """R4.2: number of distinct position series (exact equality over the full history, NaN = NaN) among the
    valid columns, and the collapse map {representative column: [collapsed columns]}."""
    groups: dict[bytes, list[int]] = {}
    for j in np.flatnonzero(valid):
        col = positions[:, j]
        h = hashlib.sha1(np.where(np.isnan(col), -9.0e300, col).tobytes()).digest()
        groups.setdefault(h, []).append(int(j))
    collapse = {g[0]: g[1:] for g in groups.values() if len(g) > 1}
    return len(groups), collapse
