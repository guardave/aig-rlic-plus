#!/usr/bin/env python3
"""Pair Pre-Screening POC — score each pair across the 4 stakeholder dimensions
from EXISTING Data+Econ artifacts, before any dashboard build.

See docs/pair-prescreen-proposal.md. Thresholds here are ILLUSTRATIVE and
NOT calibrated — this is a feasibility/validation demo. Degrades gracefully
when fields are missing (legacy pairs: bh_sharpe null, no evidence_status).

Usage:  python scripts/pair_prescreen.py            # all pairs with winner_summary
        python scripts/pair_prescreen.py --pairs m2sl_yoy_spy,phlxsox_spy
"""
from __future__ import annotations
import argparse, glob, json, os

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")

# ── illustrative thresholds (TO BE CALIBRATED) ───────────────────────────────
OOS_SHARPE_GREEN, OOS_SHARPE_AMBER = 1.2, 0.8
UPLIFT_GREEN, UPLIFT_AMBER = 0.4, 0.2          # oos_sharpe - bh_sharpe
TRADES_MIN, TRADES_MAX = 10, 1500              # too few = fragile; too many = cost drag
BOOTSTRAP_OK = 0.10

RAG = {"G": "🟢", "A": "🟡", "R": "🔴", "?": "⚪"}


def _load(pair):
    d = {}
    p = os.path.join(RESULTS, pair)
    try:
        d["w"] = json.load(open(os.path.join(p, "winner_summary.json")))
    except Exception:
        d["w"] = {}
    try:
        d["ev"] = json.load(open(os.path.join(p, "evidence_status.json")))
    except Exception:
        d["ev"] = {}
    sub = glob.glob(os.path.join(p, "subperiod_sharpe.csv"))
    d["sub"] = sub[0] if sub else None
    tf = sorted(glob.glob(os.path.join(p, "tournament_results_*.csv")))
    d["tourn"] = tf[-1] if tf else None
    return d


def d1_performance(w):
    """Strategy Performance."""
    oos, bh = w.get("oos_sharpe"), w.get("bh_sharpe")
    dd, bhdd = w.get("oos_max_drawdown"), w.get("bh_max_drawdown")
    trades = w.get("oos_n_trades")
    notes = []
    if oos is None:
        return "?", ["no oos_sharpe"]
    # absolute sharpe
    s = "G" if oos >= OOS_SHARPE_GREEN else "A" if oos >= OOS_SHARPE_AMBER else "R"
    notes.append(f"OOS Sharpe {oos:.2f}")
    # uplift vs B&H
    if bh is not None:
        up = oos - bh
        notes.append(f"uplift +{up:.2f}")
        if up < UPLIFT_AMBER:
            s = "R"
        elif up < UPLIFT_GREEN and s == "G":
            s = "A"
    else:
        notes.append("bh_sharpe null→uplift n/a")
        if s == "G":
            s = "A"  # can't confirm uplift → cap at amber
    # drawdown improvement
    if dd is not None and bhdd is not None and bhdd != 0:
        notes.append(f"DD {dd*100:.1f}% vs B&H {bhdd*100:.1f}%")
    # trade count tradability
    if trades is not None:
        if trades < TRADES_MIN:
            notes.append(f"only {trades} trades→fragile")
            s = "R" if s != "R" else s
        elif trades > TRADES_MAX:
            notes.append(f"{trades} trades→cost drag")
    return s, notes


def d2_operational(w):
    """Operational Practicality (PARTIAL — full read needs Dana handoff: source
    freshness + release lag). Here: turnover + trade tradability proxy."""
    notes = []
    turn = w.get("annual_turnover")
    lead = w.get("lead_value")
    lu = w.get("lead_unit")
    if lead is not None:
        notes.append(f"lead {lead}{(' '+lu) if lu else ''}")
    if turn is not None:
        notes.append(f"turnover {turn:.1f}/yr")
        s = "G" if turn <= 6 else "A" if turn <= 12 else "R"
    else:
        s = "?"
    notes.append("source-freshness+release-lag: needs Dana input")
    return s, notes


def d3_crisis(subpath):
    """Crisis Validation from subperiod_sharpe.csv.

    Note: many pairs' OOS windows are recent and DON'T cover old crises
    (rows come back `insufficient_data`). Lack of testable crises is UNKNOWN
    (⚪), not a failure — only actual crisis LOSSES are Red."""
    if not subpath:
        return "?", ["no subperiod_sharpe"]
    import csv
    val_pos = val_neg = insuff = 0
    eps = []
    with open(subpath) as f:
        for row in csv.DictReader(f):
            ds = (row.get("data_status") or "").strip()
            shp = row.get("ann_sharpe")
            ep = row.get("episode")
            if ds == "validated" and shp not in (None, ""):
                v = float(shp)
                eps.append(f"{ep}:{v:.2f}")
                if v > 0:
                    val_pos += 1
                else:
                    val_neg += 1
            else:
                insuff += 1
    testable = val_pos + val_neg
    notes = [f"{val_pos}+/{val_neg}- of {testable} testable ({insuff} insuff.)"]
    if eps:
        notes.append(", ".join(eps))
    if testable == 0:
        return "?", notes + ["no testable crises in OOS window"]
    if val_neg == 0 and val_pos >= 2:
        return "G", notes
    if val_pos >= val_neg:
        return "A", notes
    return "R", notes


def d4_durability(w, ev, tournpath):
    """Durability — penalize only genuine fragility flags:
       (a) negative in-sample Sharpe with strong OOS (regime-lucky),
       (b) episode_concentrated durability verdict,
       (c) winner NOT meaningfully above the valid-combo distribution.
    found_in_search is the NORMAL pre-final-exam state → caps at Amber, not Red.
    A low median combo is EXPECTED (most random combos underperform) and is NOT
    itself a defect — what matters is the winner sitting clearly above it."""
    notes = []
    status = ev.get("status")
    if status:
        notes.append(status)
    s = "G"
    if tournpath:
        try:
            import pandas as pd
            df = pd.read_csv(tournpath)
            sc = "oos_sharpe" if "oos_sharpe" in df.columns else None
            if sc:
                valid = df[df["valid"]] if "valid" in df.columns else df
                if "signal" in df.columns:
                    valid = valid[valid["signal"] != "BENCHMARK"]
                oos_s = w.get("oos_sharpe")
                med = valid[sc].median()
                q90 = valid[sc].quantile(0.90)
                notes.append(f"winner {oos_s:.2f} vs median {med:.2f}/p90 {q90:.2f}")
                # winner barely above the pack → weak edge
                if oos_s is not None and oos_s <= q90:
                    notes.append("winner not clearly top-decile→thin edge")
                    s = "A"
                # IS vs OOS gap from winning row (regime-luck flag)
                if "is_sharpe" in df.columns:
                    isr = valid[sc].idxmax()
                    is_s = df.loc[isr, "is_sharpe"]
                    if is_s is not None and oos_s is not None:
                        notes.append(f"IS {is_s:.2f}→OOS gap {oos_s - is_s:+.2f}")
                        if is_s < 0 < oos_s:
                            notes.append("neg-IS→regime-lucky (RED FLAG)")
                            s = "R"
        except Exception:
            notes.append("(tourn parse skipped)")
    # durability verdict from subperiod (if any row carries it)
    sub = w.get("durability_verdict") or ev.get("durability_verdict")
    if status == "found_in_search" and s == "G":
        s = "A"  # not a final-exam pass → cap at Amber
    if status is None:
        notes.append("no evidence_status")
        if s == "G":
            s = "A"
    return s, notes


def verdict(scores):
    """Aggregate the four RAG scores into a screen verdict."""
    vals = [s for s in scores if s != "?"]
    if any(s == "R" for s in [scores["D1"], scores["D4"]]):     # perf or durability red = drop
        return "DEFER/DROP"
    if scores["D2"] == "R" or scores["D3"] == "R":
        return "DEFER/DROP"
    if all(s == "G" for s in vals) and "?" not in scores.values():
        return "PROCEED"
    return "CONDITIONAL"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", help="comma-separated pair_ids; default = all with winner_summary")
    args = ap.parse_args()
    if args.pairs:
        pairs = args.pairs.split(",")
    else:
        pairs = sorted(os.path.basename(os.path.dirname(p))
                       for p in glob.glob(os.path.join(RESULTS, "*/winner_summary.json")))
        pairs = [p for p in pairs if not (p.endswith("_archived") or p.endswith("_v1"))]

    print(f"\nPair Pre-Screen POC — {len(pairs)} pairs  (thresholds illustrative, NOT calibrated)\n")
    print(f"{'pair':22s} {'D1':2s} {'D2':2s} {'D3':2s} {'D4':2s}  VERDICT")
    print("-" * 60)
    detail = {}
    for p in pairs:
        d = _load(p)
        sc = {}
        sc["D1"], n1 = d1_performance(d["w"])
        sc["D2"], n2 = d2_operational(d["w"])
        sc["D3"], n3 = d3_crisis(d["sub"])
        sc["D4"], n4 = d4_durability(d["w"], d["ev"], d["tourn"])
        v = verdict(sc)
        detail[p] = (sc, {"D1": n1, "D2": n2, "D3": n3, "D4": n4}, v)
        print(f"{p:22s} {RAG[sc['D1']]} {RAG[sc['D2']]} {RAG[sc['D3']]} {RAG[sc['D4']]}  {v}")
    print("\nLegend: D1 Performance · D2 Operational · D3 Crisis · D4 Durability   "
          + " ".join(f"{k}={v}" for k, v in RAG.items()))
    print("\n--- detail ---")
    for p, (sc, nn, v) in detail.items():
        print(f"\n{p}  [{v}]")
        for dim in ("D1", "D2", "D3", "D4"):
            print(f"  {dim} {RAG[sc[dim]]}: " + "; ".join(nn[dim]))


if __name__ == "__main__":
    main()
