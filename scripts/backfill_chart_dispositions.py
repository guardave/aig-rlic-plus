#!/usr/bin/env python3
"""
Backfill VIZ-O1 `disposition` field on existing chart _meta.json sidecars.

Wave 10H.1 — one-shot idempotent migration.

Rules applied:
  - VIZ-O1 (Chart Disposition Mandate)
  - VIZ-E1 (Exploration Zone + Sidecar Spec)

Semantics:
  - Default disposition for every existing sidecar is "consumed"
    (every shipping chart is rendered by some page today).
  - Three Sample-pair orphans are "suggested" with exploratory=true, because
    they have no current page slot and route to the Methodology-page
    Exploratory Insights section via APP-PT2.
  - Matching is by file *stem* (everything before `_meta.json`), NOT the
    `chart_name` JSON field — legacy sidecars wrote pair-id-prefixed
    chart_names (e.g. "hy_ig_v2_spy_hero_spread_vs_spy").

Idempotent: re-running produces identical file contents; only "unchanged"
grows on reruns.

Usage:
    python scripts/backfill_chart_dispositions.py
"""

from __future__ import annotations

import glob
import json
import os
import sys
from typing import Any

BASE_DIR = "/workspaces/aig-rlic-plus"
CHART_GLOB = os.path.join(BASE_DIR, "output", "charts", "*", "plotly", "*_meta.json")

# (pair_id, file_stem) → desired exploratory payload
#   Orphans in the Sample pair (hy_ig_v2_spy) that have no page slot.
EXPLORATORY_ORPHANS: dict[tuple[str, str], dict[str, Any]] = {
    ("hy_ig_v2_spy", "hero_spread_vs_spy"): {
        "disposition": "suggested",
        "exploratory": True,
    },
    ("hy_ig_v2_spy", "spread_history_annotated"): {
        "disposition": "suggested",
        "exploratory": True,
    },
    ("hy_ig_v2_spy", "tournament_sharpe_dist"): {
        "disposition": "suggested",
        "exploratory": True,
    },
}


def _stem(meta_filename: str) -> str:
    """Strip trailing `_meta.json` from a filename to get the chart stem."""
    base = os.path.basename(meta_filename)
    assert base.endswith("_meta.json"), base
    return base[: -len("_meta.json")]


def _pair_id(meta_path: str) -> str:
    # .../output/charts/<pair_id>/plotly/<stem>_meta.json
    parts = os.path.normpath(meta_path).split(os.sep)
    return parts[-3]


def _desired_fields(pair_id: str, stem: str) -> dict[str, Any]:
    key = (pair_id, stem)
    if key in EXPLORATORY_ORPHANS:
        return dict(EXPLORATORY_ORPHANS[key])
    return {"disposition": "consumed"}


def _needs_update(existing: dict[str, Any], desired: dict[str, Any]) -> bool:
    for k, v in desired.items():
        if existing.get(k) != v:
            return True
    return False


def main() -> int:
    paths = sorted(glob.glob(CHART_GLOB))
    consumed = suggested = unchanged = errors = 0

    for path in paths:
        try:
            with open(path) as f:
                meta = json.load(f)
        except Exception as exc:
            print(f"  ERROR reading {path}: {exc}", file=sys.stderr)
            errors += 1
            continue

        pair_id = _pair_id(path)
        stem = _stem(path)
        desired = _desired_fields(pair_id, stem)

        if not _needs_update(meta, desired):
            unchanged += 1
            continue

        meta.update(desired)

        try:
            with open(path, "w") as f:
                json.dump(meta, f, indent=2)
        except Exception as exc:
            print(f"  ERROR writing {path}: {exc}", file=sys.stderr)
            errors += 1
            continue

        if desired["disposition"] == "suggested":
            suggested += 1
        else:
            consumed += 1

    summary = {
        "consumed": consumed,
        "suggested": suggested,
        "unchanged": unchanged,
        "errors": errors,
    }
    print(json.dumps(summary))
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
