#!/usr/bin/env python3
"""GH#13 native-derive of the coherent lead artifacts for indpro_spy.

The generic `refresh_lead_coherence_artifacts.py` engine cannot handle this pair:
its signals parquet never persisted S1_level / S4_dev_trend, and the tournament
has NO lookback column (T2/T3 thresholds use a FIXED 60-month rolling window), so
the generic engine KeyErrors on LB_NA. This pair-specific derive sidesteps both.

Crucially, this is a DERIVE-ONLY case (winner already selected on the full L0-12
native grid; unchanged): tournament_results_20260620.csv already scores every combo
at every lead L0-12. And on the ECON-T4 deployable basis it needs NO re-scoring:
EVERY valid combo has oos_n == the full OOS window (96) — INDPRO's contraction flag
never collapses over a 60m window in 2018-2025 (COVID is in-window), so no P2/P3-on-
regime-flag degeneracy arises. Deployable Sharpe == the tournament's Sharpe for the
whole valid population, so the coherent artifacts are a faithful reshape of the
immutable published tournament CSV — read-only, nothing re-derived.

Emits (matching the refresh_lead_coherence_artifacts schema so generate_lead_charts
+ gate_viz_lead consume them unchanged):
  lead_tournament_native_{date}.csv, lead_winner_curve_{date}.csv,
  lead_clean_envelope_{date}.csv, and patches lead_sweep_manifest_{date}.json.
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
PAIR = "indpro_spy"
RESULTS = REPO / "results" / PAIR
RECONCILE_TOL = 0.03

# S-code -> parquet column (from pair_pipeline_indpro_spy.py signal_cols)
SIGNAL_COL = {
    "S1_level": "indpro", "S2_yoy": "indpro_yoy", "S3_mom": "indpro_mom",
    "S4_dev_trend": "indpro_dev_trend", "S5_zscore": "indpro_zscore_60m",
    "S6_mom3m": "indpro_mom_3m", "S7_mom6m": "indpro_mom_6m",
    "S8_accel": "indpro_accel", "S9_contraction": "indpro_contraction",
}


def main() -> int:
    ws = json.loads((RESULTS / "winner_summary.json").read_text())
    win_lead = int(ws["lead_value"])
    win_sharpe = float(ws["oos_sharpe"])
    w_sig = ws["selection"]["raw_winner_row"]["signal"]
    w_thr = ws["selection"]["raw_winner_row"]["threshold"]
    w_strat = ws["selection"]["raw_winner_row"]["strategy"]

    tr_path = sorted(glob.glob(str(RESULTS / "tournament_results_*.csv")))[-1]
    tr = pd.read_csv(tr_path)  # read-only; published tournament is immutable (ECON-T5 §4)
    strat = tr[tr.signal != "BENCHMARK"].copy()
    leads = sorted(int(x) for x in strat.lead_months.unique())

    # ── gate A: full L0-12 grid already scored (derive-only, not a re-run) ──
    if leads != list(range(0, 13)):
        print(f"[{PAIR}] BLOCKED — tournament grid {leads} is not full L0-12; "
              f"this is a re-run case, not derive-only.", file=sys.stderr)
        return 2

    # ── gate B: deployable == dropna for the whole VALID population ──
    valid = strat[strat.valid].copy()
    if valid.oos_n.nunique() != 1:
        print(f"[{PAIR}] BLOCKED — valid combos span multiple oos_n "
              f"{sorted(valid.oos_n.unique())}: a partial-window (degenerate) combo "
              f"exists, so deployable != dropna and this needs true re-scoring, not a "
              f"reshape.", file=sys.stderr)
        return 2

    # ── gate C: reconcile the winner at its own lead ──
    wrow = strat[(strat.signal == w_sig) & (strat.threshold == w_thr) &
                 (strat.strategy == w_strat) & (strat.lead_months == win_lead)]
    if wrow.empty or abs(float(wrow.oos_sharpe.iloc[0]) - win_sharpe) > RECONCILE_TOL:
        got = float(wrow.oos_sharpe.iloc[0]) if len(wrow) else float("nan")
        print(f"[{PAIR}] BLOCKED — winner reconcile {got} vs winner_summary "
              f"{win_sharpe}", file=sys.stderr)
        return 2

    # ── gate D: governance — winner IS the global max valid combo ──
    gmax = float(valid.oos_sharpe.max())
    if gmax > win_sharpe + RECONCILE_TOL:
        print(f"[{PAIR}] BLOCKED — a valid combo beats the winner ({gmax} > "
              f"{win_sharpe}); pending re-selection, not a derive.", file=sys.stderr)
        return 3

    man_path = sorted(f for f in glob.glob(str(RESULTS / "lead_sweep_manifest_*.json"))
                      if "weekly" not in f)[-1]
    date_tag = re.search(r"(\d{8})", Path(man_path).name).group(1)

    # ── SINGLE SOURCE: lead_tournament_native (all leads pipeline-scored) ──
    native = strat[["signal", "threshold", "strategy", "lead_months", "oos_sharpe", "valid"]].copy()
    native["lookback"] = "LB_NA"
    native["signal_column"] = native.signal.map(SIGNAL_COL).fillna(native.signal)
    native["lead_source"] = "pipeline"
    native = native[["signal", "threshold", "strategy", "lookback", "signal_column",
                     "lead_months", "oos_sharpe", "valid", "lead_source"]]
    native_path = RESULTS / f"lead_tournament_native_{date_tag}.csv"
    native.to_csv(native_path, index=False)

    # ── view 1: winner's own curve (winner combo across all leads, valid or not) ──
    wc = strat[(strat.signal == w_sig) & (strat.threshold == w_thr) &
               (strat.strategy == w_strat)].set_index("lead_months")["oos_sharpe"]
    wc_rows = [{"lead_months": L,
                "oos_sharpe": round(float(wc[L]), 4) if L in wc.index and pd.notna(wc[L]) else float("nan"),
                "is_published_winner": bool(L == win_lead), "lead_source": "pipeline"}
               for L in range(0, 13)]
    wc_df = pd.DataFrame(wc_rows)
    wc_path = RESULTS / f"lead_winner_curve_{date_tag}.csv"
    wc_df.to_csv(wc_path, index=False)
    peak_lead = int(wc_df.loc[wc_df.oos_sharpe.idxmax(), "lead_months"])

    # ── view 2: clean envelope (best VALID combo per lead) ──
    env_rows = []
    for L in range(0, 13):
        g = valid[valid.lead_months == L]
        if len(g):
            top = g.loc[g.oos_sharpe.idxmax()]
            s, sig = round(float(top.oos_sharpe), 4), SIGNAL_COL.get(top.signal, top.signal)
        else:
            s, sig = float("nan"), ""
        env_rows.append({"lead_months": L, "best_oos_sharpe": s, "best_signal": sig,
                         "best_is_clean": True, "best_clean_oos_sharpe": s,
                         "best_clean_signal": sig, "lead_source": "pipeline"})
    env = pd.DataFrame(env_rows)
    env_path = RESULTS / f"lead_clean_envelope_{date_tag}.csv"
    env.to_csv(env_path, index=False)

    # ── coherence invariant: envelope >= winner curve at every lead ──
    m = wc_df.merge(env[["lead_months", "best_oos_sharpe"]], on="lead_months")
    bad = m[m.oos_sharpe > m.best_oos_sharpe + 1e-6]
    if len(bad):
        for p in (native_path, wc_path, env_path):
            p.unlink(missing_ok=True)
        print(f"[{PAIR}] BLOCKED — winner curve exceeds envelope at leads "
              f"{bad.lead_months.tolist()}", file=sys.stderr)
        return 2

    L_star = int(env.loc[env.best_oos_sharpe.idxmax(), "lead_months"])
    top2 = env.best_oos_sharpe.dropna().sort_values(ascending=False).head(2).tolist()
    margin = round(top2[0] - top2[1], 4) if len(top2) == 2 else None
    env_flat = bool(margin is not None and margin < 0.10)

    man = json.loads(Path(man_path).read_text())
    man.update({
        "lead_tournament_native_file": f"{PAIR}/{native_path.name}",
        "lead_winner_curve_file": f"{PAIR}/{wc_path.name}",
        "lead_clean_envelope_file": f"{PAIR}/{env_path.name}",
        "clean_envelope_note": (
            "Native-derived (scripts/refresh_indpro_spy_lead_artifacts.py) because the "
            "generic engine can't reproduce this pair (signals parquet lacks S1_level/"
            "S4_dev_trend; no lookback column, fixed-60m thresholds). Winner already "
            "selected on the full L0-12 native grid; DERIVE-ONLY. On the ECON-T4 "
            "deployable basis no re-scoring is needed: every valid combo has oos_n==full "
            "window (96), so deployable Sharpe == the published tournament Sharpe."),
        "winner_curve_peak_lead": peak_lead,
        "coherent_envelope_L_star": L_star,
        "coherent_envelope_peak_margin": margin,
        "coherent_envelope_is_flat": env_flat,
        "pipeline_scored_leads": leads,
        "engine_patched_leads": [],
        "winner_governance": (f"winner holds — global max across all leads {gmax:.4f} "
                              f"does not exceed the frozen winner {win_sharpe:.4f} (ECON-T5 clear)"),
        "best_clean_oos_sharpe_at_grid": round(float(env.best_oos_sharpe.max()), 4),
        "best_clean_oos_sharpe_at_grid_signal": env.loc[env.best_oos_sharpe.idxmax(), "best_signal"],
    })
    note = (f"[GH#13] published winner ({w_sig}/{w_thr}/{w_strat}/L{win_lead}, OOS "
            f"{win_sharpe:.4f}) on the single native source: own curve peaks at L{peak_lead}, "
            f"cross-signal envelope peaks at L{L_star} (top-two margin {margin}, flat={env_flat}); "
            f"all leads {leads} pipeline-scored, deployable basis (all valid oos_n==96); "
            f"winner governance clear (no lead beats it).")
    asserts = man.get("assertions", [])
    if note not in asserts:
        asserts.append(note)
    man["assertions"] = asserts
    Path(man_path).write_text(json.dumps(man, indent=2))

    print(f"[{PAIR}] reconcile OK @ L{win_lead}: {float(wrow.oos_sharpe.iloc[0]):.4f} vs {win_sharpe:.4f}")
    print(f"[{PAIR}] source {native_path.name} ({len(native)} rows); winner curve peak L{peak_lead}, "
          f"envelope L*={L_star} (margin {margin}, flat={env_flat}); all leads pipeline-scored; "
          f"governance clear.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
