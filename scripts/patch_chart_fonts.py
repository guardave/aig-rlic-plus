"""Standardise chart font sizes (axis titles, ticks, legend, caption).

Generators set their own font sizes per-chart, producing inconsistent
visual weight across pages (story / strategy / methodology charts looked
subtly different). This patcher enforces the canonical sizes from
``_chart_layout``:

  chart title       → FONT_SIZE_TITLE        (15)
  X/Y axis title    → FONT_SIZE_AXIS_TITLE   (12)
  X/Y tick labels   → FONT_SIZE_TICK         (11)
  legend trace text → FONT_SIZE_LEGEND       (11)
  caption text      → FONT_SIZE_CAPTION      (10)

The patcher does NOT touch:
  - per-annotation fonts (event markers, structural-break labels) —
    those have their own intentional sizes
  - bar text / textfont on traces — chart-specific

Usage:
    python3 scripts/patch_chart_fonts.py [--dry-run] [--pair PAIR_ID]

Idempotent.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTS_ROOT = REPO_ROOT / "output" / "charts"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chart_layout import (  # noqa: E402
    FONT_SIZE_TITLE,
    FONT_SIZE_AXIS_TITLE,
    FONT_SIZE_TICK,
    FONT_SIZE_LEGEND,
    FONT_SIZE_CAPTION,
)


def _set_nested(d: dict, path: list[str], value) -> bool:
    """Set d[path[0]][path[1]]... = value. Return True iff a change was made."""
    node = d
    for k in path[:-1]:
        if not isinstance(node.get(k), dict):
            node[k] = {}
        node = node[k]
    last = path[-1]
    if node.get(last) == value:
        return False
    node[last] = value
    return True


def _patch_axis(layout: dict, axis_key: str) -> bool:
    """Patch x-axis or y-axis title font and tickfont."""
    if axis_key not in layout:
        return False
    ax = layout[axis_key]
    if not isinstance(ax, dict):
        return False
    changed = False
    # title font
    title = ax.get("title")
    if isinstance(title, dict):
        if _set_nested(ax, ["title", "font", "size"], FONT_SIZE_AXIS_TITLE):
            changed = True
    elif isinstance(title, str) and title:
        ax["title"] = {"text": title, "font": {"size": FONT_SIZE_AXIS_TITLE}}
        changed = True
    # tick font
    if _set_nested(ax, ["tickfont", "size"], FONT_SIZE_TICK):
        changed = True
    return changed


def _patch_layout(doc: dict) -> bool:
    layout = doc.get("layout") or {}
    if not layout:
        return False
    changed = False

    # Title font
    title = layout.get("title")
    if isinstance(title, dict) and title.get("text"):
        if _set_nested(layout, ["title", "font", "size"], FONT_SIZE_TITLE):
            changed = True
    elif isinstance(title, str) and title:
        layout["title"] = {"text": title, "font": {"size": FONT_SIZE_TITLE}}
        changed = True

    # X / Y axis (single panel)
    for axis_key in ("xaxis", "yaxis", "xaxis2", "yaxis2"):
        if _patch_axis(layout, axis_key):
            changed = True

    # Legend font
    legend = layout.get("legend")
    if isinstance(legend, dict):
        if _set_nested(layout, ["legend", "font", "size"], FONT_SIZE_LEGEND):
            changed = True

    # Caption-class annotations (small grey font)
    for anno in layout.get("annotations", []) or []:
        if anno.get("showarrow") is True:
            continue
        font = anno.get("font") or {}
        # Identify the source-note caption: grey + size in (9, 10).
        if font.get("color") in ("grey", "#888", "#888888", "#555") and font.get("size") in (8, 9, 10, 11):
            if font.get("size") != FONT_SIZE_CAPTION:
                anno.setdefault("font", {})["size"] = FONT_SIZE_CAPTION
                changed = True

    return changed


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--pair", default=None)
    args = p.parse_args()

    if args.pair:
        glob_pat = str(CHARTS_ROOT / args.pair / "plotly" / "*.json")
    else:
        glob_pat = str(CHARTS_ROOT / "*" / "plotly" / "*.json")
    paths = sorted(Path(p) for p in glob.glob(glob_pat))
    paths = [p for p in paths if not p.name.endswith("_meta.json")]

    n_patched = 0
    for path in paths:
        try:
            with open(path) as fh:
                doc = json.load(fh)
        except Exception as e:
            print(f"  ERR  {path}: {e}", file=sys.stderr)
            continue
        if not _patch_layout(doc):
            continue
        if not args.dry_run:
            with open(path, "w") as fh:
                json.dump(doc, fh, separators=(",", ":"))
        n_patched += 1
        rel = path.relative_to(REPO_ROOT)
        print(f"  {'DRY' if args.dry_run else 'OK '}  {rel}")

    print(f"\n{'Would patch' if args.dry_run else 'Patched'}: {n_patched} charts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
