#!/usr/bin/env python3
"""Pilot 260807 (event-study variant) — 3-up / 3-down unemployment RUNS as discrete events.

Reframes the run-length idea (Q1 / methodology memo Challenge 3): instead of a latched
persistent state, treat the COMPLETION of a 3-consecutive-rise (or 3-consecutive-fall)
in the unemployment level as a dated EVENT, then ask: h months after the event, what is
SPY's forward performance — and does it beat the unconditional baseline?

Conventions (documented, no look-ahead):
  - Monthly month-end data. UNRATE for reference month t is released ~early t+1, so the
    event is only actionable from t+1. We apply PUB_LAG = 1 month: entry at end of month
    (t + PUB_LAG); CAR(h) compounds spy_ret over the h months AFTER entry.
  - Events are episode ONSETS: the first month a 3-run completes after a non-run month,
    so overlapping consecutive completions are not double-counted.
  - Abnormal(h) = conditional mean CAR(h) over events  -  unconditional mean CAR(h) over
    ALL eligible months. This strips out the equity risk premium — the event only has
    content if abnormal != 0.
  - 3-up and 3-down analysed SEPARATELY (the deck's state-dependent-lead thesis).

Statistics: event-resample bootstrap 90% CI (events are the unit); a naive t is printed
with an explicit overlapping-window caveat (treat the bootstrap CI as primary).

Evidence only — writes under docs/pilots/, never results/. Run:
  python3 scripts/pilots/run_pilot260807_unrate_event_study.py
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data" / "unrate_spy_monthly_latest.parquet"
OUT = ROOT / "docs" / "pilots" / "pilot260807_unrate_runlength"

K = 3
H_MAX = 24
PUB_LAG = 1
N_BOOT = 4000
SEED = 260807  # fixed for reproducibility (no Math.random equivalent needed)


def _onsets_from_completes(completes: np.ndarray) -> np.ndarray:
    """onset = a completion whose previous month was NOT already a completion."""
    onsets = completes & ~np.r_[False, completes[:-1]]
    return np.flatnonzero(onsets)


def run_onsets(level: pd.Series, k: int, direction: str) -> np.ndarray:
    """STRICT: k consecutive strictly-monotonic months (flat breaks the run)."""
    d = level.diff().to_numpy()
    cond = d > 0 if direction == "up" else d < 0
    run = 0
    completes = np.zeros(len(d), dtype=bool)
    for i in range(len(d)):
        if np.isnan(d[i]):
            run = 0
            continue
        run = run + 1 if cond[i] else 0
        if run >= k:
            completes[i] = True
    return _onsets_from_completes(completes)


def cum_onsets(level: pd.Series, k: int, direction: str, eps: float = 0.2) -> np.ndarray:
    """ROUNDING-AWARE: the k-month change is 'meaningfully' up/down (|Δ_k| >= eps),
    so flat 0.1%-rounding months no longer break an economically real move."""
    chg = (level - level.shift(k)).to_numpy()
    completes = (chg >= eps) if direction == "up" else (chg <= -eps)
    completes = completes & ~np.isnan(chg)
    return _onsets_from_completes(completes)


def cum_forward(spy_ret: np.ndarray, entry_pos: int, h: int) -> float:
    """Compounded SPY return over the h months following an end-of-`entry_pos` entry."""
    a, b = entry_pos + 1, entry_pos + 1 + h
    if b > len(spy_ret):
        return np.nan
    seg = spy_ret[a:b]
    if np.any(np.isnan(seg)):
        return np.nan
    return float(np.prod(1.0 + seg) - 1.0)


def car_matrix(spy_ret: np.ndarray, event_pos: np.ndarray) -> np.ndarray:
    """(n_events x H_MAX) matrix of CAR(h); entry = event_pos + PUB_LAG."""
    M = np.full((len(event_pos), H_MAX), np.nan)
    for r, ep in enumerate(event_pos):
        entry = ep + PUB_LAG
        for h in range(1, H_MAX + 1):
            M[r, h - 1] = cum_forward(spy_ret, entry, h)
    return M


def unconditional_car(spy_ret: np.ndarray, eligible: np.ndarray) -> np.ndarray:
    """Mean CAR(h) over ALL eligible entry positions (the baseline)."""
    out = np.full(H_MAX, np.nan)
    for h in range(1, H_MAX + 1):
        vals = [cum_forward(spy_ret, ep + PUB_LAG, h) for ep in eligible]
        vals = [v for v in vals if not np.isnan(v)]
        out[h - 1] = np.mean(vals) if vals else np.nan
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PARQUET)
    level = df["unrate"].astype(float)
    spy_ret = df["spy_ret"].astype(float).to_numpy()
    n = len(df)
    eligible = np.arange(n)  # every month is a candidate entry for the baseline
    rng = np.random.default_rng(SEED)
    print(f"data: {n} months {df.index.min().date()}..{df.index.max().date()}")

    uncond = unconditional_car(spy_ret, eligible)

    defs = {"strict": lambda d: run_onsets(level, K, d),
            "cum0.2": lambda d: cum_onsets(level, K, d, 0.2)}
    rows = []
    for defname, detect in defs.items():
      for direction in ("up", "down"):
        ev = detect(direction)
        M = car_matrix(spy_ret, ev)
        cond = np.nanmean(M, axis=0)
        abn = cond - uncond
        n_ev = len(ev)

        # event-resample bootstrap 90% CI on the abnormal curve
        boot = np.empty((N_BOOT, H_MAX))
        for b in range(N_BOOT):
            idx = rng.integers(0, n_ev, n_ev)
            boot[b] = np.nanmean(M[idx], axis=0) - uncond
        lo, hi = np.nanpercentile(boot, 5, axis=0), np.nanpercentile(boot, 95, axis=0)

        # naive t (overlapping-window caveat)
        sd = np.nanstd(M - uncond, axis=0, ddof=1)
        tnaive = abn / (sd / np.sqrt(n_ev))

        for h in range(1, H_MAX + 1):
            rows.append(dict(event_def=defname, direction=direction, n_events=n_ev,
                             horizon_months=h,
                             conditional_car=cond[h - 1], unconditional_car=uncond[h - 1],
                             abnormal=abn[h - 1], ci_lo=lo[h - 1], ci_hi=hi[h - 1],
                             t_naive=tnaive[h - 1],
                             ci_excludes_zero=bool(lo[h - 1] > 0 or hi[h - 1] < 0)))

        # console summary
        print(f"\n=== [{defname}] 3-{direction} onsets: N = {n_ev} events ===")
        sig = [(h + 1, abn[h], lo[h], hi[h], tnaive[h]) for h in range(H_MAX)
               if lo[h] > 0 or hi[h] < 0]
        hmax = int(np.nanargmax(np.abs(abn))) + 1
        print(f"  largest |abnormal| at h={hmax}: {abn[hmax-1]:+.3%} "
              f"(90% CI {lo[hmax-1]:+.2%}..{hi[hmax-1]:+.2%}, naive t={tnaive[hmax-1]:+.2f})")
        if sig:
            print(f"  horizons where 90% CI excludes 0: " +
                  ", ".join(f"h{h}({a:+.1%})" for h, a, _, _, _ in sig))
        else:
            print("  NO horizon has a 90% CI excluding zero — no reliable abnormal return.")

    res = pd.DataFrame(rows)
    res.to_csv(OUT / f"unrate_event_study_pilot260807.csv", index=False)
    print(f"\nwrote {OUT / 'unrate_event_study_pilot260807.csv'}")
    print("NOTE: full-sample descriptive event study; naive t ignores overlapping windows "
          "(bootstrap CI is primary). Harvey-Liu-Zhu t>3 + order-statistic bias apply to any "
          "argmax-h picked from this curve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
