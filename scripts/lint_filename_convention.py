#!/usr/bin/env python3
"""META-CMP T1.3 — Chart filename convention lint (VIZ-NM1, GH #7).

For every REGISTERED pair (discovered via app/components/pair_registry.py),
assert that no chart JSON under output/charts/<pair_id>/plotly/ starts with
the legacy '<pair_id>_' prefix. Bare names are canonical (team-standards
§2.1): the pair_id lives in the directory path, NEVER in the filename.

Catches: the silent shadow-file class from fix260526 W1 — a pre-fix
`indpro_xlp_drawdown.json` co-existing with the cloud-served `drawdown.json`.

Scope notes:
    - Only *.json files are checked. `_perceptual_check_*.png` renders are
      exempt by construction (not JSON).
    - `*_meta.json` sidecars of bare names (e.g. `hero_meta.json`) are fine —
      they carry no pair prefix. A pair-prefixed sidecar
      (`<pair_id>_hero_meta.json`) IS a violation like any other.
    - Archived / non-registered chart dirs (e.g. output/charts/dff_ted_spy/)
      are OUT of scope — they hold known legacy prefixes and are no longer
      referenced by the portal.

Usage:
    python3 scripts/lint_filename_convention.py

Exit codes:
    0 - clean
    1 - one or more violations
    2 - infrastructure error (registry unavailable)

A violation means fix the PRODUCER (chart generator emitting the prefix),
never just rename the artifact (META-NMF).
"""
from __future__ import annotations

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from _pair_discovery import registered_pair_ids  # noqa: E402

_CHARTS_DIR = os.path.join(_REPO_ROOT, "output", "charts")


def main() -> int:
    try:
        pair_ids = registered_pair_ids()
    except Exception as exc:
        print(f"ERROR: pair registry discovery failed: {exc!r}", file=sys.stderr)
        return 2
    if not pair_ids:
        print("ERROR: pair registry returned no registered pairs.", file=sys.stderr)
        return 2

    n_checked = 0
    violations: list[str] = []

    for pair_id in pair_ids:
        plotly_dir = os.path.join(_CHARTS_DIR, pair_id, "plotly")
        if not os.path.isdir(plotly_dir):
            print(f"SKIP  output/charts/{pair_id}/plotly/ — directory absent "
                  f"(chart presence is GATE-DPS1 / T2's job)")
            continue
        prefix = f"{pair_id}_"
        for fname in sorted(os.listdir(plotly_dir)):
            if not fname.endswith(".json"):
                continue
            n_checked += 1
            if fname.startswith(prefix):
                violations.append(
                    f"FAIL  pair={pair_id}  file=output/charts/{pair_id}/plotly/{fname}  "
                    f"legacy pair-prefixed filename — canonical is bare-name "
                    f"'{fname[len(prefix):]}' (VIZ-NM1 / team-standards §2.1)"
                )

    for v in violations:
        print(v)

    print(f"\n# T1.3 lint_filename_convention  pairs={len(pair_ids)}  "
          f"json_files_checked={n_checked}  violations={len(violations)}")
    if violations:
        print("# FAIL — fix the chart generator, never just rename the file (META-NMF).",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
