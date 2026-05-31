"""Patch chart JSONs to eliminate legend / caption-annotation overlap.

Class of bug (fix260531, comment-log meta-issue):
    Several chart generators placed a horizontal legend just below the plot
    area (`legend.y in [-0.05, -0.35]`) and a small grey "source note" /
    caption annotation just below the legend (`y in [-0.12, -0.22]`). When
    the bottom margin is too small (typical: 60–80 px) the two overlap
    visually.

Two patterns were emitted in production:

    Pattern A — history-zoom dual-axis charts (`history_zoom_*.json`)
        Before:  legend.y=-0.05, caption.y=-0.12, margin.b=60
        After:   legend.y=-0.18, caption.y=-0.32, margin.b=120

    Pattern B — rolling correlation / rolling Granger 24M charts
        Before:  legend.y=-0.35, caption.y=-0.22, margin.b=80
        After:   legend.y=-0.50, caption.y=-0.22, margin.b=140

Pattern C — `indpro_xlp` history-zoom shipped with legend.y=-0.25 (different
    constant from Pattern A); apply Pattern A's `after` values to it too.

Usage:
    python3 scripts/patch_legend_caption_layout.py [--dry-run]

The script is idempotent — running it again on already-patched files is a no-op.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTS_ROOT = REPO_ROOT / "output" / "charts"

# Target post-patch values
HISTORY_ZOOM_LEGEND_Y = -0.18
HISTORY_ZOOM_CAPTION_Y = -0.32
HISTORY_ZOOM_MARGIN_B = 120

ROLLING_LEGEND_Y = -0.50
ROLLING_CAPTION_Y = -0.22  # unchanged from current
ROLLING_MARGIN_B = 140


def _patch_layout(layout: dict, file_kind: str) -> bool:
    """Mutate layout in place. Return True iff anything changed."""
    changed = False
    legend = layout.get("legend") or {}
    annotations = layout.get("annotations") or []
    margin = layout.get("margin") or {}

    if file_kind == "history_zoom":
        target_legend_y = HISTORY_ZOOM_LEGEND_Y
        target_caption_y = HISTORY_ZOOM_CAPTION_Y
        target_margin_b = HISTORY_ZOOM_MARGIN_B
        caption_text_hint = "Source:"
    elif file_kind == "rolling":
        target_legend_y = ROLLING_LEGEND_Y
        target_caption_y = ROLLING_CAPTION_Y
        target_margin_b = ROLLING_MARGIN_B
        caption_text_hint = None  # rolling caption already at -0.22, just push legend
    else:
        return False

    cur_legend_y = legend.get("y")
    if cur_legend_y is None or float(cur_legend_y) != target_legend_y:
        legend["y"] = target_legend_y
        legend.setdefault("orientation", "h")
        layout["legend"] = legend
        changed = True

    for anno in annotations:
        if anno.get("yref") != "paper":
            continue
        ay = anno.get("y")
        try:
            ay_f = float(ay)
        except Exception:
            continue
        if ay_f >= 0:
            continue
        # Identify the caption annotation (the small grey source note).
        text = str(anno.get("text", ""))
        font = anno.get("font") or {}
        is_caption = (
            (caption_text_hint and caption_text_hint in text)
            or (font.get("size") in (9, 10) and font.get("color") in ("#888888", "grey", "#888"))
        )
        if not is_caption:
            continue
        if ay_f != target_caption_y:
            anno["y"] = target_caption_y
            changed = True

    cur_margin_b = margin.get("b")
    if cur_margin_b is None or int(cur_margin_b) < target_margin_b:
        margin["b"] = target_margin_b
        layout["margin"] = margin
        changed = True

    return changed


def _classify(path: Path) -> str | None:
    name = path.name
    if name.startswith("history_zoom_"):
        return "history_zoom"
    if name in ("rolling_correlation.json", "rolling_granger.json"):
        return "rolling"
    return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    paths = sorted(Path(p) for p in glob.glob(str(CHARTS_ROOT / "*" / "plotly" / "*.json")))
    paths = [p for p in paths if not p.name.endswith("_meta.json")]

    n_patched = 0
    by_kind = {"history_zoom": 0, "rolling": 0}
    for path in paths:
        kind = _classify(path)
        if kind is None:
            continue
        try:
            with open(path) as fh:
                doc = json.load(fh)
        except Exception as e:
            print(f"  ERR  {path}: {e}", file=sys.stderr)
            continue
        layout = doc.get("layout") or {}
        if not _patch_layout(layout, kind):
            continue
        doc["layout"] = layout
        if not args.dry_run:
            with open(path, "w") as fh:
                json.dump(doc, fh, separators=(",", ":"))
        n_patched += 1
        by_kind[kind] += 1
        rel = path.relative_to(REPO_ROOT)
        print(f"  {'DRY' if args.dry_run else 'OK '}  {rel}  ({kind})")

    print(
        f"\n{'Would patch' if args.dry_run else 'Patched'}: {n_patched} charts "
        f"({by_kind['history_zoom']} history-zoom, {by_kind['rolling']} rolling)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
