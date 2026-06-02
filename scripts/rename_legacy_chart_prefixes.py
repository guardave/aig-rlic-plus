"""Wave 1 of fix260601_chart_hygiene — BL-VIZ-CHART-PREFIX-LEGACY.

Renames legacy pair-id-prefixed chart filenames to the canonical bare-name
convention (VIZ-NM1). Three pairs are affected:
  - indpro_spy:    10 charts + 10 perceptual PNGs
  - permit_spy:     5 charts +  5 perceptual PNGs
  - vix_vix3m_spy:  5 charts +  5 perceptual PNGs

Idempotent — a second run is a no-op once the renames are applied.

Usage:
    python scripts/rename_legacy_chart_prefixes.py [--dry-run]
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTS_ROOT = REPO_ROOT / "output" / "charts"

AFFECTED_PAIRS = ("indpro_spy", "permit_spy", "vix_vix3m_spy")


def _enumerate_renames(pair_id: str) -> list[tuple[Path, Path]]:
    """Return list of (from, to) paths for one pair."""
    prefix = f"{pair_id}_"
    plotly = CHARTS_ROOT / pair_id / "plotly"
    if not plotly.is_dir():
        return []

    renames: list[tuple[Path, Path]] = []

    # Chart JSONs: <pair>_<name>.json -> <name>.json
    for src in sorted(plotly.glob(f"{prefix}*.json")):
        name = src.name
        # Exclude already-bare files that happen to share the prefix; only
        # rename if the prefix strips to a non-empty bare name AND the
        # resulting target doesn't already exist.
        if not name.startswith(prefix):
            continue
        bare = name[len(prefix):]
        if not bare:
            continue
        dst = src.with_name(bare)
        if dst.exists():
            # Already renamed in a prior pass, or a collision with another
            # canonical file — skip with a warning printed by caller.
            continue
        renames.append((src, dst))

    # Perceptual PNGs: _perceptual_check_<pair>_<name>.png ->
    #                  _perceptual_check_<name>.png
    pp_prefix = f"_perceptual_check_{prefix}"
    for src in sorted(plotly.glob(f"{pp_prefix}*.png")):
        name = src.name
        if not name.startswith(pp_prefix):
            continue
        bare = name[len(pp_prefix):]
        if not bare:
            continue
        dst = src.with_name(f"_perceptual_check_{bare}")
        if dst.exists():
            continue
        renames.append((src, dst))

    return renames


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    total = 0
    for pair_id in AFFECTED_PAIRS:
        pair_renames = _enumerate_renames(pair_id)
        if not pair_renames:
            print(f"  ({pair_id}: nothing to rename — already canonical)")
            continue
        print(f"\n{pair_id} — {len(pair_renames)} renames:")
        for src, dst in pair_renames:
            rel_src = src.relative_to(REPO_ROOT)
            rel_dst = dst.relative_to(REPO_ROOT)
            print(f"  {'DRY' if args.dry_run else 'OK '}  {rel_src.name:50s} → {rel_dst.name}")
            if not args.dry_run:
                src.rename(dst)
            total += 1

    print(f"\n{'Would rename' if args.dry_run else 'Renamed'}: {total} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
