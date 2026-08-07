#!/usr/bin/env python3
"""GATE-CONSISTENCY — cross-artifact winner consistency (pure Python, no LLM).

The winner is described in many places: winner_summary.json (the anchor), the
native tournament (the selection source), kpis.json, the lead-coherence artifacts,
and the pair's narrative config. A re-selection (or any edit) that fails to
propagate leaves the report internally contradictory. This scanner anchors on
winner_summary and verifies every other surface agrees.

HARD checks (fail the gate):
  A. winner_summary's combo exists in tournament_results at its lead, Sharpe within tol.
  B. winner_summary is the MAX valid OOS Sharpe on the selection grid — i.e. no valid
     combo beats it (selection is internally consistent; a beating combo means a
     pending re-selection that has not propagated).
  C. kpis.json "OOS Sharpe (winner)" == winner_summary.oos_sharpe (2dp).
  D. lead_winner_curve (if present): the is_published_winner row's lead + Sharpe
     match winner_summary.

SOFT checks (report, don't fail — prose parsing is fuzzy):
  E. the narrative config cites the winner's Sharpe (4dp or 2dp) and winner lead token;
     absence suggests the prose may reference a stale winner.

Exit non-zero if any HARD check fails for any pair.

Usage:  python scripts/gate_consistency.py [pair ...]
"""
from __future__ import annotations

import csv
import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHARPE_TOL = 0.01


def _read_csv(path: Path):
    with open(path) as f:
        return list(csv.DictReader(f))


def _latest(pair: str, stem: str):
    c = sorted((REPO / "results" / pair).glob(f"{stem}_*.csv"))
    c = [p for p in c if re.match(rf"^{re.escape(stem)}_\d{{8}}\.csv$", p.name)]
    return c[-1] if c else None


def _native_sig(pair: str, signal_code: str) -> str:
    # best-effort code->native strip; both the stem and the leading token are tried
    stem = pair.rsplit("_", 1)[0]
    for pref in (f"{stem}_", f"{stem.split('_')[0]}_"):
        if signal_code.startswith(pref):
            return signal_code[len(pref):]
    return signal_code


def _contaminated_signals(rdir: Path) -> set:
    """Seasonally-contaminated signal codes excluded from selection (from the
    lead_sweep_manifest); empty for pairs with none."""
    mans = [p for p in sorted(rdir.glob("lead_sweep_manifest_*.json")) if "weekly" not in p.name]
    if not mans:
        return set()
    try:
        return set(json.loads(mans[-1].read_text()).get("seasonally_contaminated_signals") or [])
    except Exception:
        return set()


def check_pair(pair: str) -> tuple[list[str], list[str]]:
    """(hard_failures, soft_warnings)."""
    rdir = REPO / "results" / pair
    ws_path = rdir / "winner_summary.json"
    if not ws_path.exists():
        return [], ["no winner_summary.json — skipped"]
    ws = json.loads(ws_path.read_text())
    hard: list[str] = []
    soft: list[str] = []

    win_lead = int(ws.get("lead_value", ws.get("lead_months")))
    win_sharpe = float(ws["oos_sharpe"])
    sig_code = ws.get("signal_code", "")
    contaminated = _contaminated_signals(rdir)

    # ── A + B: against the native tournament (selection source) ──
    tr_files = sorted(rdir.glob("tournament_results_*.csv"))
    if tr_files:
        rows = [r for r in _read_csv(tr_files[-1]) if r["signal"] != "BENCHMARK"]
        lk = next((k for k in rows[0] if k.startswith("lead_")), None) if rows else None

        def _f(r, k):
            try:
                return float(r[k])
            except (KeyError, ValueError):
                return float("nan")

        if lk is None:
            soft.append("tournament_results has no lead column")
        else:
            valids = [r for r in rows if str(r.get("valid", "True")).lower() == "true"]
            # A (naming-independent): the winner Sharpe must be reproduced by SOME
            # valid combo at the winner's own lead. Signal-code<->native-name maps
            # vary per pair, so anchor on (lead, Sharpe), not the combo string.
            at_lead = [r for r in valids if int(float(r[lk])) == win_lead]
            if not any(abs(_f(r, "oos_sharpe") - win_sharpe) <= SHARPE_TOL for r in at_lead):
                hard.append(f"A: winner OOS Sharpe {win_sharpe} is not reproduced by any "
                            f"valid combo at L{win_lead} in tournament_results "
                            f"(winner_summary vs selection source drift)")
            # B: winner must be the max valid CLEAN combo (excluding seasonally-
            # contaminated signals, which are validly excluded from selection).
            clean = [r for r in valids if r["signal"] not in contaminated]
            if clean:
                top = max(clean, key=lambda r: _f(r, "oos_sharpe"))
                if _f(top, "oos_sharpe") > win_sharpe + SHARPE_TOL:
                    hard.append(f"B: a valid, non-excluded combo beats the published winner "
                                f"— {top['signal']}/{top['threshold']}/{top['strategy']}/"
                                f"L{int(float(top[lk]))} = {top['oos_sharpe']} > winner "
                                f"{win_sharpe} (pending re-selection not propagated)")
            # soft: does the winner's signal code map onto a tournament signal?
            sigs = {r["signal"] for r in rows}
            if sig_code and sig_code not in sigs and _native_sig(pair, sig_code) not in sigs:
                soft.append(f"signal_code '{sig_code}' does not obviously map to a "
                            f"tournament signal {sorted(sigs)[:6]}… (naming, likely benign)")
    else:
        soft.append("no tournament_results — cannot verify selection")

    # ── C: kpis.json winner Sharpe ──
    kpi_path = rdir / "kpis.json"
    if kpi_path.exists():
        try:
            kpis = json.loads(kpi_path.read_text())
            wk = next((k for k in kpis if isinstance(k, dict)
                       and "sharpe" in str(k.get("metric", "")).lower()
                       and "winner" in str(k.get("metric", "")).lower()), None)
            if wk and abs(float(str(wk["value"])) - round(win_sharpe, 2)) > 0.011:
                hard.append(f"C: kpis.json winner Sharpe {wk['value']} != "
                            f"winner_summary {win_sharpe:.2f}")
        except Exception as e:
            soft.append(f"kpis.json unreadable: {type(e).__name__}")

    # ── D: lead_winner_curve marker ──
    wc_path = _latest(pair, "lead_winner_curve")
    if wc_path:
        wc = _read_csv(wc_path)
        lk = next(k for k in wc[0] if k.startswith("lead_"))
        flagged = [r for r in wc if str(r["is_published_winner"]).lower() == "true"]
        if len(flagged) != 1:
            hard.append(f"D: lead_winner_curve has {len(flagged)} winner flags (expected 1)")
        elif int(flagged[0][lk]) != win_lead:
            hard.append(f"D: lead_winner_curve winner flag at L{flagged[0][lk]} != "
                        f"winner_summary L{win_lead}")
        elif abs(float(flagged[0]["oos_sharpe"]) - win_sharpe) > SHARPE_TOL:
            hard.append(f"D: lead_winner_curve winner Sharpe {flagged[0]['oos_sharpe']} "
                        f"!= winner_summary {win_sharpe}")

    # ── E (soft): narrative config cites current winner numbers ──
    cfg = REPO / "app" / "pair_configs" / f"{pair}_config.py"
    if cfg.exists():
        txt = cfg.read_text()
        s4, s2 = f"{win_sharpe:.4f}", f"{win_sharpe:.2f}"
        if s4 not in txt and s2 not in txt:
            soft.append(f"E: config cites neither {s4} nor {s2} — prose may show a "
                        f"stale winner Sharpe")
        unit = (ws.get("lead_unit") or "months").rstrip("s")
        if unit == "month" and f"L{win_lead}" not in txt:
            soft.append(f"E: config does not mention winner lead L{win_lead}")

    return hard, soft


def main() -> int:
    pairs = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not pairs:
        pairs = sorted(p.name for p in (REPO / "results").iterdir()
                       if p.is_dir() and (p / "winner_summary.json").exists()
                       and not p.name.endswith("_archived"))
    total_hard = 0
    for p in pairs:
        try:
            hard, soft = check_pair(p)
        except Exception as e:
            hard, soft = [f"scan error: {type(e).__name__}: {e}"], []
        mark = "FAIL" if hard else ("warn" if soft else "OK  ")
        print(f"[{mark}] {p}")
        for h in hard:
            print(f"         ✗ {h}")
        for s in soft:
            print(f"         · {s}")
        total_hard += len(hard)
    print(f"\nGATE-CONSISTENCY: {total_hard} hard failure(s) across {len(pairs)} pairs")
    return 1 if total_hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
