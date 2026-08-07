#!/usr/bin/env python3
"""GATE-VIZ-LEAD — GH #13 lead-coherence enforcement (pure Python, no LLM).

For every pair that carries the native coherent artifacts (lead_winner_curve +
lead_clean_envelope), HARD-VALIDATE self-consistency so the coherent lead chart can
never silently regress:

  1. envelope >= winner curve at every lead (the coherence invariant);
  2. exactly one row flagged is_published_winner, at the winner's deployed lead,
     and its Sharpe reconciles to winner_summary (<= 0.03);
  3. the rendered lead_sharpe_distribution.json carries the coherent winner-curve
     trace (not the exploratory-sweep bars).

Pairs WITHOUT the artifacts are reported as "not yet covered" (informational) — a
coverage tracker for the GH #13 rollout, not a failure (their native divergence
can only be computed by the generator).

Exit non-zero if any COVERED pair fails a hard check.

Usage:  python scripts/gate_viz_lead.py [pair ...]   # default: all pairs under results/
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOL = 0.03


def _latest(pair: str, stem: str):
    pat = re.compile(rf"^{re.escape(stem)}_(\d{{8}})\.csv$")
    c = [(p, pat.match(p.name).group(1))
         for p in (REPO / "results" / pair).glob(f"{stem}_*.csv") if pat.match(p.name)]
    return sorted(c, key=lambda t: t[1])[-1][0] if c else None


def _read_csv(path: Path):
    import csv
    with open(path) as f:
        return list(csv.DictReader(f))


def check_pair(pair: str) -> tuple[str, list[str]]:
    """Return (status, messages). status in {PASS, FAIL, UNCOVERED, SKIP}."""
    rdir = REPO / "results" / pair
    ws_path = rdir / "winner_summary.json"
    if not ws_path.exists():
        return "SKIP", ["no winner_summary.json"]
    ws = json.loads(ws_path.read_text())
    unit = (ws.get("lead_unit") or "months").rstrip("s")

    wc_p = _latest(pair, "lead_winner_curve")
    env_p = _latest(pair, "lead_clean_envelope")
    if not (wc_p and env_p):
        # daily pairs are handled by the diagnostic-sweep framing, not the monthly
        # coherent overlay; only monthly pairs are "expected" to be covered here.
        return "UNCOVERED", ["no native coherent artifacts (lead_winner_curve/clean_envelope)"]

    msgs: list[str] = []
    wc_rows = _read_csv(wc_p)
    lead_key = next(k for k in wc_rows[0] if k.startswith("lead_"))  # lead_months|lead_quarters
    wc = {int(r[lead_key]): r for r in wc_rows}
    env = {int(r[lead_key]): float(r["best_oos_sharpe"]) for r in _read_csv(env_p)}

    # 1. coherence invariant
    viol = [L for L in wc if L in env and float(wc[L]["oos_sharpe"]) > env[L] + 1e-6]
    if viol:
        msgs.append(f"envelope < winner curve at leads {viol}")

    # 2. winner flag + reconciliation
    flagged = [L for L, r in wc.items() if str(r["is_published_winner"]).lower() == "true"]
    win_lead = int(ws["lead_value"])
    if flagged != [win_lead]:
        msgs.append(f"is_published_winner flags {flagged}, expected [{win_lead}]")
    elif abs(float(wc[win_lead]["oos_sharpe"]) - float(ws["oos_sharpe"])) > TOL:
        msgs.append(f"winner-lead Sharpe {wc[win_lead]['oos_sharpe']} != "
                    f"winner_summary {ws['oos_sharpe']} (tol {TOL})")

    # 3. single-source consistency: the native lead tournament's pipeline-tagged
    #    rows MUST match tournament_results (the selection source the strategy-
    #    tournament details render) — this is what keeps the two views consistent.
    src_p = _latest(pair, "lead_tournament_native")
    tr_p = sorted((REPO / "results" / pair).glob("tournament_results_*.csv"))
    if src_p and tr_p:
        src_rows = _read_csv(src_p)
        tr_rows = [r for r in _read_csv(sorted(tr_p)[-1]) if r["signal"] != "BENCHMARK"]
        src = [r for r in src_rows if r.get("lead_source") == "pipeline"]
        # axis-agnostic: the lead column is lead_months (monthly/quarterly pairs) or
        # lead_days (daily Class-A pairs) — read it generically from each file's header.
        src_lk = next((k for k in src_rows[0] if k.startswith("lead_")), "lead_months") if src_rows else "lead_months"
        tr_lk = next((k for k in tr_rows[0] if k.startswith("lead_")), "lead_months") if tr_rows else "lead_months"
        tr = {(r["signal"], r["threshold"], r["strategy"], r.get("lookback", ""),
               int(float(r[tr_lk]))): float(r["oos_sharpe"]) for r in tr_rows}
        mism = sum(1 for r in src
                   if (k := (r["signal"], r["threshold"], r["strategy"], r.get("lookback", ""),
                             int(float(r[src_lk])))) in tr
                   and abs(float(r["oos_sharpe"]) - tr[k]) > 0.02)
        if mism:
            msgs.append(f"single-source drift: {mism} pipeline rows in "
                        f"lead_tournament_native disagree with tournament_results")

    # 4. rendered chart carries the coherent trace
    cj = REPO / f"output/charts/{pair}/plotly/lead_sharpe_distribution.json"
    if not cj.exists():
        msgs.append("no rendered lead_sharpe_distribution.json")
    else:
        names = [t.get("name", "") for t in json.loads(cj.read_text())["data"]]
        if not any("winner's own curve" in n for n in names):
            msgs.append("chart lacks the coherent winner-curve trace "
                        "(still showing the exploratory sweep bars?)")

    return ("PASS", ["coherent + self-consistent"]) if not msgs else ("FAIL", msgs)


def main() -> int:
    pairs = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not pairs:
        pairs = sorted(p.name for p in (REPO / "results").iterdir()
                       if p.is_dir() and (p / "winner_summary.json").exists()
                       and not p.name.endswith("_archived"))
    fails = 0
    covered = uncovered = 0
    for p in pairs:
        try:
            status, msgs = check_pair(p)
        except Exception as e:  # a malformed artifact must fail loudly, not crash the sweep
            status, msgs = "FAIL", [f"gate error: {type(e).__name__}: {e}"]
        mark = {"PASS": "OK  ", "FAIL": "FAIL", "UNCOVERED": "--  ", "SKIP": "skip"}[status]
        print(f"[{mark}] {p}: {msgs[0]}" + (f" (+{len(msgs)-1} more)" if len(msgs) > 1 else ""))
        for extra in msgs[1:]:
            print(f"         - {extra}")
        if status == "FAIL":
            fails += 1
        elif status == "PASS":
            covered += 1
        elif status == "UNCOVERED":
            uncovered += 1
    print(f"\nGATE-VIZ-LEAD: {covered} covered/PASS, {uncovered} not-yet-covered, {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
