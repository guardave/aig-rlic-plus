#!/usr/bin/env python3
"""Shared writer for ``results/<pair>/evidence_status.json`` (schema 1.2.0).

Four pipelines (t10y3m_spy, cass_freight_spy, eci_total_comp_spy, wells_fargo_housing_spy) emitted an
older, schema-INVALID shape - a ``blocks``/``caveats``/``generated_by`` manifest, or a 1.0.0 file
carrying ``confidence``/``generated_at``/``notes`` - which ``docs/schemas/evidence_status.schema.json``
forbids (additionalProperties:false; ``schema_version``/``status``/``updated_at`` required). The app's
consumer-side ``validate_or_die`` therefore fell back to a yellow "Evidence status ... could not be
validated" banner on those four pairs while every pre-commit gate stayed green.

``to_v12`` converts a legacy dict WITHOUT inventing anything: the disposition stays
``found_in_search`` (what the old files said and what the app already defaulted to), and every
legacy fact (caveats, notes, pipeline-block names and statuses verbatim, confidence label,
generated_at when it differs from updated_at) is preserved in ``technical_note``. No sentence is
added that is not in the source. ``plain_english`` is left unset so the app uses its canonical copy for the status.

CLI (artifact-level regeneration without re-running any pipeline):
    python3 scripts/evidence_status_util.py results/<pair>/evidence_status.json [...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.2.0"


def to_v12(ev: dict[str, Any], owner: str = "evan") -> dict[str, Any]:
    """Schema-1.2.0 evidence status from a legacy-shape dict (idempotent on a valid 1.2.0 dict)."""
    if ev.get("schema_version") == SCHEMA_VERSION and "blocks" not in ev:
        return ev
    parts: list[str] = []
    blocks = ev.get("blocks")
    if isinstance(blocks, dict) and blocks:
        # Block names and their statuses are kept verbatim (no collapsing into counts).
        parts.append("Pipeline blocks: " + "; ".join(f"{k}={v}" for k, v in blocks.items()) + ".")
    caveats = ev.get("caveats")
    if caveats:
        parts.append("Caveats: " + "; ".join(str(c) for c in caveats) + ".")
    if ev.get("notes"):
        parts.append(str(ev["notes"]).strip())
    if ev.get("confidence"):
        parts.append(f"Producer confidence label: {ev['confidence']}.")
    if ev.get("generated_at") and ev.get("generated_at") != ev.get("updated_at"):
        parts.append(f"Generated at: {ev['generated_at']}.")
    out: dict[str, Any] = {
        "pair_id": ev["pair_id"],
        "schema_version": SCHEMA_VERSION,
        "status": ev.get("status") if ev.get("status") in (
            "found_in_search", "needs_final_exam", "passed_final_exam", "failed_final_exam") else "found_in_search",
        "updated_at": ev.get("updated_at") or ev.get("generated_at"),
        "owner": ev.get("owner") or ev.get("generated_by") or owner,
        "technical_note": " ".join(parts),
    }
    return out


def write_evidence_status(path: Path | str, ev: dict[str, Any], owner: str = "evan") -> None:
    Path(path).write_text(json.dumps(to_v12(ev, owner), indent=2) + "\n")


def main(argv: list[str]) -> int:
    for a in argv:
        p = Path(a)
        write_evidence_status(p, json.loads(p.read_text()))
        print(f"rewrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
