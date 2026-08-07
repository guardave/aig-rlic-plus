#!/usr/bin/env python3
"""GATE-LEAD-AXIS — axis-matches-frequency enforcement (pure Python, no LLM).

The Lead-Grid Frequency Standard (docs/lead-grid-frequency-standard.md, Step 1)
makes the lead AXIS a HARD RULE: the axis unit equals the signal's native release
frequency. A pair may not carry lead artifacts resampled to a different frequency
than its signal — that builds a second tournament whose winner differs from the
deployed strategy. This is exactly the hy_ig bug: a MONTHLY L0-12 lead sweep bolted
onto a DAILY-traded 0-day-lead winner.

For every REGISTERED pair (docs/schemas/lead_axis_registry.json) this gate reads the
recorded signal frequency -> expected lead axis, then detects the ACTUAL axis of the
pair's lead artifacts and asserts they agree:

  1. lead_sharpe_distribution chart  — layout.xaxis.title.text unit token
  2. primary lead_tournament CSV      — lead_<unit> column name (+ lead_unit column)
  3. lead_correlation CSV             — presence check (wide L0..LN header carries no
                                        unit label; reported, not unit-asserted)

THE LOAD-BEARING CHECK: a DAILY-signal pair must NOT carry a MONTHLY-axis lead chart.

The gate checks AXIS ONLY — never selection windows, caps, or floors (those are
reference metadata in the registry, deliberately not enforced here).

Exit non-zero if any registered pair's artifacts are off its recorded axis. The 4
daily Class-A pairs are EXPECTED to FAIL until rebuilt on the daily axis (rollout
item 1); that failure documents the known debt and is why this gate is NOT yet wired
into the blocking pre-commit hook.

Usage:  python scripts/gate_lead_axis.py [pair ...]   # default: all registered pairs
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "docs" / "schemas" / "lead_axis_registry.json"

# Canonical axis units. Everything normalizes onto one of these.
UNITS = ("days", "weeks", "months", "quarters")


def normalize_unit(token: str) -> str | None:
    """Map any frequency/axis word onto a canonical unit, or None if unrecognised."""
    if not token:
        return None
    t = token.strip().lower()
    if "quarter" in t:
        return "quarters"
    if "month" in t:
        return "months"
    if "week" in t:
        return "weeks"
    if "day" in t or t in {"daily",}:  # covers "days", "trading_days", "trading days"
        return "days"
    return None


def _read_csv_header(path: Path) -> list[str]:
    with open(path) as f:
        return next(csv.reader(f), [])


def _primary_lead_tournament(rdir: Path) -> Path | None:
    """The base lead tournament (the one the chart renders from) — not the weekly/
    native/monthly_axis variants."""
    cands = [p for p in rdir.glob("lead_tournament_*.csv")
             if re.match(r"^lead_tournament_\d{8}\.csv$", p.name)]
    return sorted(cands)[-1] if cands else None


def _latest_plain(rdir: Path, stem: str) -> Path | None:
    cands = [p for p in rdir.glob(f"{stem}_*.csv")
             if re.match(rf"^{re.escape(stem)}_\d{{8}}\.csv$", p.name)]
    return sorted(cands)[-1] if cands else None


def _chart_axis_unit(pair: str) -> tuple[str | None, str]:
    """(unit, detail) from the lead_sharpe_distribution chart's x-axis title."""
    cj = REPO / "output" / "charts" / pair / "plotly" / "lead_sharpe_distribution.json"
    if not cj.exists():
        return None, "no lead_sharpe_distribution.json"
    try:
        title = json.loads(cj.read_text()).get("layout", {}).get("xaxis", {}).get("title", {})
        text = title.get("text", "") if isinstance(title, dict) else str(title)
    except Exception as e:
        return None, f"chart unreadable: {type(e).__name__}"
    # The axis unit is the token inside the FIRST parentheses, e.g.
    # "Lead (months) applied to signal" / "Lead (quarters) ... — L1q ≈ 3 months".
    m = re.search(r"\(([^)]*)\)", text)
    unit = normalize_unit(m.group(1)) if m else normalize_unit(text)
    return unit, f'xaxis="{text}"'


def _tournament_axis_unit(rdir: Path) -> tuple[str | None, str]:
    """(unit, detail) from the primary lead tournament's lead_<unit> column."""
    lt = _primary_lead_tournament(rdir)
    if lt is None:
        return None, "no primary lead_tournament_YYYYMMDD.csv"
    header = _read_csv_header(lt)
    lead_cols = [c for c in header if c.startswith("lead_")]
    # Prefer an explicit lead_<unit> column; a bare "lead_unit" column (weekly
    # variant) names the unit in its values, not its header.
    for c in lead_cols:
        u = normalize_unit(c[len("lead_"):])
        if u:
            return u, f"{lt.name}:{c}"
    return None, f"{lt.name}: no unit-bearing lead column {lead_cols}"


def check_pair(pair: str, rec: dict) -> tuple[str, list[str]]:
    """Return (status, messages). status in {PASS, FAIL, NO_ARTIFACTS}."""
    expected = normalize_unit(rec.get("lead_axis", ""))
    freq = rec.get("signal_frequency", "?")
    rdir = REPO / "results" / pair
    if expected is None:
        return "FAIL", [f"registry lead_axis '{rec.get('lead_axis')}' is not a recognised unit"]

    detections: list[tuple[str, str | None, str]] = [
        ("chart", *_chart_axis_unit(pair)),
        ("tournament", *_tournament_axis_unit(rdir)),
    ]
    lead_corr = _latest_plain(rdir, "lead_correlation")

    present = [(name, unit, detail) for (name, unit, detail) in detections if unit is not None]
    if not present:
        msgs = [f"signal={freq} -> expect {expected} axis; no unit-bearing lead artifacts found"]
        msgs += [f"{name}: {detail}" for (name, unit, detail) in detections]
        return "NO_ARTIFACTS", msgs

    mismatches = [(name, unit, detail) for (name, unit, detail) in present if unit != expected]
    ok = [(name, unit, detail) for (name, unit, detail) in present if unit == expected]

    head = (f"signal={freq} -> expect {expected} axis"
            f" | {', '.join(f'{n}={u}' for n, u, _ in present)}"
            + (f" | lead_correlation={lead_corr.name}" if lead_corr else ""))
    if mismatches:
        msgs = [head]
        for name, unit, detail in mismatches:
            msgs.append(f"AXIS MISMATCH: {name} is on the {unit} axis, expected {expected} "
                        f"({detail})")
        return "FAIL", msgs
    return "PASS", [head + f" -> all {len(ok)} artifact(s) on the {expected} axis"]


def main() -> int:
    if not REGISTRY.exists():
        print(f"FATAL: registry not found at {REGISTRY}")
        return 2
    reg = json.loads(REGISTRY.read_text())
    pairs_rec = reg.get("pairs", {})

    requested = [a for a in sys.argv[1:] if not a.startswith("-")]
    pairs = requested or sorted(pairs_rec)

    fails = passes = no_art = 0
    for p in pairs:
        rec = pairs_rec.get(p)
        if rec is None:
            print(f"[----] {p}: not in lead_axis_registry.json (unregistered — classify it first)")
            continue
        try:
            status, msgs = check_pair(p, rec)
        except Exception as e:
            status, msgs = "FAIL", [f"gate error: {type(e).__name__}: {e}"]
        mark = {"PASS": "OK  ", "FAIL": "FAIL", "NO_ARTIFACTS": "--  "}[status]
        print(f"[{mark}] {p}: {msgs[0]}")
        for extra in msgs[1:]:
            print(f"         - {extra}")
        fails += status == "FAIL"
        passes += status == "PASS"
        no_art += status == "NO_ARTIFACTS"

    print(f"\nGATE-LEAD-AXIS: {passes} PASS, {fails} FAIL, {no_art} no-artifacts "
          f"across {len(pairs)} registered pair(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
