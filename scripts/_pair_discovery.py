"""Shared registered-pair discovery for META-CMP gate scripts (GH #7).

Single source of truth: `app/components/pair_registry.load_pair_registry()` —
the exact discovery the portal uses. Gate scripts MUST NOT glob `results/`
directly: the registry already excludes archived dirs (`*_v1`, `*_archived`)
and dirs without `interpretation_metadata.json` (e.g. `results/crude_oil_xle/`
raw-data stubs), so registry-scoping keeps known-legacy artifacts out of gate
scope by construction.

Usage (from any script in scripts/):
    from _pair_discovery import registered_pair_ids
"""
from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def registered_pair_ids() -> list[str]:
    """Return sorted pair_ids of all pairs registered on the portal."""
    app_dir = os.path.join(_REPO_ROOT, "app")
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    from components.pair_registry import load_pair_registry

    return sorted(p["pair_id"] for p in load_pair_registry())
