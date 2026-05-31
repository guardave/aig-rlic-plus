"""Standardise chart legends to right-side vertical placement.

Class of bug (fix260531, follow-on to the legend/caption overlap fix):
    Different chart generators placed legends inconsistently — some
    bottom-horizontal (history_zoom, rolling_*), some top-right horizontal
    (equity_curves, granger, hero). The user requested a single
    portfolio-wide convention: legend always right-side vertical.

Convention applied:
    legend.orientation = "v"
    legend.x           = 1.02   (just outside the plot frame, right side)
    legend.xanchor     = "left"
    legend.y           = 1.0    (top-aligned)
    legend.yanchor     = "top"
    margin.r           = max(160, current)   (room for legend)

For charts that had previously had the legend below the plot, the bottom
margin is also recovered:
    margin.b           = min(current, 80)
    caption-annotation y = -0.15  (close to the x-axis, no longer competing
                                   with a now-absent bottom legend)

The script only touches charts whose layout currently sets a legend. Charts
with one trace (no visible legend) are left alone.

Usage:
    python3 scripts/patch_legend_right_side.py [--dry-run] [--pair PAIR_ID]

Idempotent: re-runs on already-patched files are a no-op.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHARTS_ROOT = REPO_ROOT / "output" / "charts"

LEGEND_X = 1.08  # bumped from 1.02 so right-axis tick labels are not
                 # occluded by the legend on dual-axis charts (the right
                 # y-axis ticks render around x=1.0).
LEGEND_XANCHOR = "left"
LEGEND_Y = 1.0
LEGEND_YANCHOR = "top"
LEGEND_ORIENTATION = "v"

MIN_MARGIN_R_WITH_LEGEND = 180  # widened from 160 to absorb the new x=1.08
RECLAIMED_MARGIN_B = 80
RECLAIMED_CAPTION_Y = -0.15


def _has_visible_legend(doc: dict) -> bool:
    """Heuristic: a legend is visible if showlegend != False AND there are
    >= 2 visible traces, OR a legend block exists in layout."""
    layout = doc.get("layout") or {}
    if layout.get("showlegend") is False:
        return False
    if layout.get("legend"):
        return True
    visible_traces = [t for t in (doc.get("data") or []) if t.get("showlegend") is not False]
    return len(visible_traces) >= 2


def _patch_layout(doc: dict) -> bool:
    """Mutate layout in place. Return True iff anything changed."""
    if not _has_visible_legend(doc):
        return False
    layout = doc.setdefault("layout", {})
    legend = dict(layout.get("legend") or {})
    margin = dict(layout.get("margin") or {})
    annotations = layout.get("annotations") or []
    changed = False

    # Detect whether the previous layout had a bottom-positioned legend.
    prev_y = legend.get("y")
    try:
        prev_y_f = float(prev_y) if prev_y is not None else None
    except Exception:
        prev_y_f = None
    was_bottom_legend = prev_y_f is not None and prev_y_f < 0

    # Apply right-side vertical legend.
    new_legend = {
        "orientation": LEGEND_ORIENTATION,
        "x": LEGEND_X,
        "xanchor": LEGEND_XANCHOR,
        "y": LEGEND_Y,
        "yanchor": LEGEND_YANCHOR,
    }
    # Preserve any extra legend props (font, bgcolor, traceorder) that
    # the generator might have set.
    for k, v in legend.items():
        if k not in new_legend:
            new_legend[k] = v
    if legend != new_legend:
        layout["legend"] = new_legend
        changed = True

    # Ensure right margin is wide enough for the legend.
    cur_r = margin.get("r")
    try:
        cur_r_int = int(cur_r) if cur_r is not None else 0
    except Exception:
        cur_r_int = 0
    if cur_r_int < MIN_MARGIN_R_WITH_LEGEND:
        margin["r"] = MIN_MARGIN_R_WITH_LEGEND
        layout["margin"] = margin
        changed = True

    if was_bottom_legend:
        # Reclaim the bottom: shrink margin.b and pull the caption up.
        cur_b = margin.get("b")
        try:
            cur_b_int = int(cur_b) if cur_b is not None else 0
        except Exception:
            cur_b_int = 0
        if cur_b_int > RECLAIMED_MARGIN_B:
            margin["b"] = RECLAIMED_MARGIN_B
            layout["margin"] = margin
            changed = True
        # Pull up the caption annotation (the small grey source-note).
        for anno in annotations:
            if anno.get("yref") != "paper":
                continue
            ay = anno.get("y")
            try:
                ay_f = float(ay)
            except Exception:
                continue
            if ay_f is None or ay_f >= 0:
                continue
            text = str(anno.get("text", ""))
            font = anno.get("font") or {}
            is_caption = (
                "Source" in text
                or "Zoom:" in text
                or font.get("size") in (9, 10)
                and font.get("color") in ("#888888", "grey", "#888", "#555")
            )
            if not is_caption:
                continue
            if ay_f != RECLAIMED_CAPTION_Y:
                anno["y"] = RECLAIMED_CAPTION_Y
                changed = True

    return changed


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--pair", default=None, help="Limit to a single pair_id directory")
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
