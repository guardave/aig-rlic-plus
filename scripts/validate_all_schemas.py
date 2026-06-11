#!/usr/bin/env python3
"""META-CMP T1.1 — Schema gate across all registered pairs (GH #7).

For every REGISTERED pair (discovered via app/components/pair_registry.py —
the same discovery the portal uses), validate the four canonical results
JSONs against their sibling schemas in docs/schemas/:

    winner_summary.json          ← winner_summary.schema.json
    signal_scope.json            ← signal_scope.schema.json
    analyst_suggestions.json     ← analyst_suggestions.schema.json
    interpretation_metadata.json ← interpretation_metadata.schema.json

Semantics (per team-coordination.md §META-CMP):
    - File present but non-conformant  → FAIL (this gate's job)
    - File absent                      → SKIP with a note (presence is
      GATE-DPS1's job — scripts/validate_pair_completeness.py — do not
      double-report)
    - Invalid JSON in a present file   → FAIL (a present-but-unparseable
      artifact is non-conformant by definition)

Catches: producer-vs-schema drift (e.g. winner_summary missing
signal_column → APP-SEV1 L1 render block on the cloud Strategy page).

Usage:
    python3 scripts/validate_all_schemas.py

Exit codes:
    0 - all present canonical JSONs conform
    1 - one or more FAILs
    2 - infrastructure error (schema file itself missing/malformed,
        registry unavailable)

A gate FAIL means fix the PRODUCER, never hand-edit the artifact (META-NMF).
"""
from __future__ import annotations

import json
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from _pair_discovery import registered_pair_ids  # noqa: E402
from validate_schema import validate_json  # noqa: E402  (META-CF validator internals)

# Canonical results artifacts — schema basename == instance basename.
CANONICAL_ARTIFACTS = [
    "winner_summary",
    "signal_scope",
    "analyst_suggestions",
    "interpretation_metadata",
]

_SCHEMAS_DIR = os.path.join(_REPO_ROOT, "docs", "schemas")
_RESULTS_DIR = os.path.join(_REPO_ROOT, "results")


def _load_schema(name: str) -> dict:
    path = os.path.join(_SCHEMAS_DIR, f"{name}.schema.json")
    if not os.path.exists(path):
        print(f"ERROR: schema not found: docs/schemas/{name}.schema.json", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: schema is not valid JSON: docs/schemas/{name}.schema.json: {exc}",
              file=sys.stderr)
        sys.exit(2)


def main() -> int:
    try:
        pair_ids = registered_pair_ids()
    except Exception as exc:
        print(f"ERROR: pair registry discovery failed: {exc!r}", file=sys.stderr)
        return 2
    if not pair_ids:
        print("ERROR: pair registry returned no registered pairs.", file=sys.stderr)
        return 2

    schemas = {name: _load_schema(name) for name in CANONICAL_ARTIFACTS}

    n_pass = n_fail = n_skip = 0
    fail_lines: list[str] = []

    for pair_id in pair_ids:
        for name in CANONICAL_ARTIFACTS:
            rel = f"results/{pair_id}/{name}.json"
            path = os.path.join(_RESULTS_DIR, pair_id, f"{name}.json")
            if not os.path.exists(path):
                n_skip += 1
                print(f"SKIP  {rel} — absent (presence is GATE-DPS1's job, not this gate's)")
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    instance = json.load(f)
            except json.JSONDecodeError as exc:
                n_fail += 1
                msg = f"FAIL  pair={pair_id}  file={rel}  [<root>] not valid JSON: {exc}"
                fail_lines.append(msg)
                print(msg)
                continue
            errors = validate_json(instance, schemas[name])
            if errors:
                n_fail += 1
                print(f"FAIL  pair={pair_id}  file={rel}  ({len(errors)} error(s))")
                for err in errors:
                    line = f"      pair={pair_id}  file={rel}  {err}"
                    fail_lines.append(line)
                    print(line)
            else:
                n_pass += 1
                print(f"PASS  {rel}")

    print(f"\n# T1.1 validate_all_schemas  pairs={len(pair_ids)}  "
          f"pass={n_pass}  fail={n_fail}  skip={n_skip}")
    if n_fail:
        print("# FAIL — fix the producer pipeline, never the artifact (META-NMF).",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
