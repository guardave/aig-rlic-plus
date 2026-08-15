#!/usr/bin/env python3
"""Pilot 260807 — run-length regime derivative on unrate_spy (Q1 / methodology memo Challenge 3).

Question: does a "N consecutive rises / N consecutive falls -> latched regime switch"
derivative — a rule *shape* the current grid does not span — add anything over the
incumbent (chg_6m, OOS Sharpe 1.5510) or the existing Sahm regime signal (1.2074)?

Design (fixed by the stakeholder this session):
  - Latched SIGNED regime state with hysteresis:
      k consecutive monthly RISES in the raw unemployment level -> latch state = +1
        ("rising-unemployment regime"), held until ...
      k consecutive FALLS -> latch state = -1 ("falling-unemployment regime").
    A flat month (diff == 0) breaks the current run but does not flip the latch.
    State is 0 only before the first trigger (well before the 2017 OOS window).
  - k FIXED at 3 (no sweep, per instruction).

Scoring is PRODUCTION-IDENTICAL: it reuses the pipeline's own pure helpers
(ann_metrics / make_position / build_threshold) and re-implements run_tournament's
loop verbatim (oos_start 2017-01-31, leads [0,1,2,3,6,9,12], valid = oos>=60 &
0.05<=exposure<=0.95 & std>0). It NEVER calls run_tournament (that writes to the
frozen production paths) and writes nothing under results/ — evidence only.

Run: python3 scripts/pilots/run_pilot260807_unrate_runlength.py
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

# Pure helpers only — no writes happen at import (main() is __main__-guarded).
from pair_pipeline_unrate_spy import (  # noqa: E402
    ann_metrics,
    make_position,
    build_threshold,
    SIGNALS,
    threshold_codes_for,
)

PARQUET = ROOT / "data" / "unrate_spy_monthly_latest.parquet"
OUT = ROOT / "docs" / "pilots" / "pilot260807_unrate_runlength"
OOS_START = pd.Timestamp("2017-01-31")
LEADS = [0, 1, 2, 3, 6, 9, 12]
K = 3


def score_combo(sig: pd.Series, thresh, direction: str, spy_ret: pd.Series) -> dict:
    """Verbatim replica of run_tournament's per-combo scoring (no writes)."""
    pos = make_position(sig, thresh, direction)
    rets = (pos * spy_ret).dropna()
    oos = rets.loc[OOS_START:]
    exposure = pos.loc[OOS_START:].dropna().mean()
    valid = len(oos) >= 60 and 0.05 <= exposure <= 0.95 and oos.std() > 0
    m = ann_metrics(oos)
    m["valid"] = bool(valid)
    m["exposure"] = float(exposure) if pd.notna(exposure) else float("nan")
    return m


def reproduce_incumbent(df: pd.DataFrame) -> pd.DataFrame:
    """Re-run the full production grid in-memory; must reproduce chg_6m/L9/1.5510."""
    rows = []
    for signal_code, col in SIGNALS.items():
        raw = df[col].astype(float)
        for tcode in threshold_codes_for(signal_code):
            threshold = build_threshold(raw, tcode)
            for direction in ["countercyclical", "procyclical"]:
                for lead in LEADS:
                    sig = raw.shift(lead)
                    thr = threshold.shift(lead) if isinstance(threshold, pd.Series) else threshold
                    m = score_combo(sig, thr, direction, df["spy_ret"])
                    rows.append(dict(signal=signal_code, threshold=tcode, direction=direction,
                                     lead_months=lead, oos_sharpe=m["oos_sharpe"], valid=m["valid"]))
    return pd.DataFrame(rows)


def runlen_regime(level: pd.Series, k: int = K) -> pd.Series:
    """Latched signed regime: +1 after k consecutive rises, -1 after k consecutive falls."""
    d = level.diff()
    state = pd.Series(0.0, index=level.index)
    cur = 0.0
    up = dn = 0
    for t in level.index:
        di = d.loc[t]
        if pd.isna(di):
            state.loc[t] = cur
            continue
        if di > 0:
            up += 1; dn = 0
        elif di < 0:
            dn += 1; up = 0
        else:  # flat breaks the run, does not flip the latch
            up = dn = 0
        if up >= k:
            cur = 1.0
        elif dn >= k:
            cur = -1.0
        state.loc[t] = cur
    return state


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PARQUET)
    print(f"data: {df.shape[0]} rows {df.index.min().date()}..{df.index.max().date()}")

    # ---- GATE: reproduce the live winner ---------------------------------
    grid = reproduce_incumbent(df)
    v = grid[grid.valid]
    w = v.loc[v.oos_sharpe.idxmax()]
    print("\n[reproduction gate]")
    print(f"  regenerated winner: {w.signal}/{w.threshold}/{w.direction}/L{int(w.lead_months)} "
          f"= {w.oos_sharpe:.4f}")
    ok = (w.signal == "chg_6m" and int(w.lead_months) == 9 and abs(w.oos_sharpe - 1.550998) < 1e-4)
    print(f"  matches live chg_6m/L9/1.5510: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  !! reproduction failed — aborting (do not pilot on a non-reproducible pair)")
        return 1

    # ---- Build the run-length regime derivative --------------------------
    state = runlen_regime(df["unrate"], K)
    n_switch = int((state.diff().fillna(0) != 0).sum())
    print(f"\n[derivative] unrate_runlen{K} latched signed regime — {n_switch} switches "
          f"over {len(state)} months; state distn {dict(state.value_counts())}")

    # ---- Score it, production-identical (T0_zero, both directions, P1) ---
    # State is +/-1 over the whole OOS window, so T0_zero cleanly separates:
    #   countercyclical (state<=0 -> long) = long only in falling-unemployment regime (sensible)
    #   procyclical     (state>=0 -> long) = long in rising-unemployment regime (perverse control)
    rows = []
    for direction in ["countercyclical", "procyclical"]:
        for lead in LEADS:
            sig = state.shift(lead)
            m = score_combo(sig, 0.0, direction, df["spy_ret"])
            rows.append(dict(signal=f"runlen{K}", threshold="T0_zero", direction=direction,
                             strategy="P1_long_cash", lead_months=lead, **m))
    # Supplementary: long-short (P3) — the natural home for a signed state.
    for lead in LEADS:
        sig = state.shift(lead)
        pos = sig.reindex(df.index)  # -1/+1 directly as position
        rets = (pos * df["spy_ret"]).dropna()
        oos = rets.loc[OOS_START:]
        m = ann_metrics(oos)
        valid = len(oos) >= 60 and oos.std() > 0
        rows.append(dict(signal=f"runlen{K}", threshold="none", direction="signed_ls",
                         strategy="P3_long_short", lead_months=lead, valid=bool(valid), **{k: v for k, v in m.items()}))

    res = pd.DataFrame(rows)
    res.to_csv(OUT / f"unrate_runlen{K}_pilot260807.csv", index=False)

    valid = res[res.valid]
    print("\n[results] valid run-length combos, best first:")
    show = ["direction", "strategy", "lead_months", "oos_sharpe", "max_drawdown", "oos_n"]
    print(valid.sort_values("oos_sharpe", ascending=False)[show].head(10).to_string(index=False))

    best = valid.loc[valid.oos_sharpe.idxmax()] if len(valid) else None
    print("\n[verdict vs baselines]")
    print(f"  incumbent chg_6m/L9           : 1.5510")
    print(f"  Sahm regime (best)            : 1.2074")
    if best is not None:
        print(f"  run-length{K} (best valid)     : {best.oos_sharpe:.4f}  "
              f"({best.direction}/{best.strategy}/L{int(best.lead_months)})")
        print(f"  -> beats incumbent? {'YES' if best.oos_sharpe > 1.5510 else 'no'}"
              f" | beats Sahm? {'YES' if best.oos_sharpe > 1.2074 else 'no'}")
    else:
        print(f"  run-length{K}: NO valid combo")
    print(f"\nwrote {OUT / f'unrate_runlen{K}_pilot260807.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
