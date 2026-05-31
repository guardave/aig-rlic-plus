"""Standardise X-axis title vs caption vertical ordering on time-series charts.

Class of bug (fix260531):
    The rolling_*, walk_forward, drawdown, equity_curves and structural_break
    charts emit the same two text elements below the plot — the X-axis title
    ("Date") and a small grey caption note describing the chart — but at
    inconsistent vertical positions. Three patterns were shipped:

      caption.y = -0.12  → caption ends up ABOVE the axis title
      caption.y = -0.15  → caption ends up SLIGHTLY above the axis title
      caption.y = -0.22  → caption ends up BELOW the axis title

    Three different orderings of the same two elements.

Standard (this script enforces):
    xaxis_title.standoff = 12   (pulls "Date" close to the tick labels)
    caption.y            = -0.28 (well below the axis title)
    margin.b             >= 110  (room for both with comfortable gap)

The patcher only touches charts that have BOTH:
    - an x-axis title set, AND
    - a paper-anchored caption annotation with y < 0
so it doesn't disturb single-element charts (no caption, or no x-axis title)
and doesn't touch annotations that are NOT the source-note caption (e.g.
event labels, axis labels rendered as paper-anchored annotations).

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

# Single source of truth shared with chart generators (scripts/_chart_layout.py).
# Generators call apply_caption_layout() at render time; this patcher enforces
# the same constants post-hoc on already-shipped JSONs.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chart_layout import (  # noqa: E402
    CAPTION_Y_SHIFT_PX as TARGET_CAPTION_Y_SHIFT_PX,
    XAXIS_STANDOFF as TARGET_XAXIS_STANDOFF,
    MARGIN_B_WITH_CAPTION as MIN_MARGIN_B,
)

# The patcher does NOT filter by filename — every chart that has both an
# x-axis title and a paper-anchored grey caption is in scope. The rule is
# about the geometric class (axis title vs caption), not about specific
# chart families. Adding a new chart type to the codebase needs nothing
# here; the patcher picks it up automatically as long as it follows the
# common (xaxis_title, paper-anchored caption) shape.


def _is_target_caption(anno: dict) -> bool:
    """Return True iff the annotation is the small grey source-note caption.

    Heuristics: paper-anchored AND (small grey font OR a known caption
    keyword in the text). Accepts both legacy paper-y captions (y<0) and
    new pixel-shifted captions (y=0 with yshift).

    Disqualifiers: y > 0 (those are titles/labels at top of plot); arrow
    annotations (event labels — they have showarrow=True or refer to data
    coordinates).
    """
    if anno.get("yref") != "paper":
        return False
    if anno.get("showarrow") is True:
        return False
    try:
        ay = float(anno.get("y"))
    except Exception:
        return False
    if ay > 0:                   # captions sit at y=0 (pixel-shifted) or y<0 (legacy)
        return False
    text = str(anno.get("text", ""))
    font = anno.get("font") or {}
    grey_font = (
        font.get("color") in ("grey", "#888", "#888888", "#555")
        or font.get("size") in (9, 10)
    )
    caption_keyword = any(
        k in text
        for k in (
            "Pearson correlation",
            "Rolling annualized Sharpe",
            "Rolling 24-month Granger",
            "Source:",
            "Sharpe ratios computed",
            "Quandt-Andrews",
            "winner strategy",
            "Cumulative",
            "Drawdown",
            "annualized return",
        )
    )
    return grey_font or caption_keyword


def _patch_layout(doc: dict) -> bool:
    layout = doc.get("layout") or {}
    xa = layout.get("xaxis") or {}
    annotations = layout.get("annotations") or []
    margin = dict(layout.get("margin") or {})

    # 1. Must have an x-axis title.
    xa_title = xa.get("title")
    if not xa_title:
        return False

    # 2. Must have a caption-class annotation.
    caption = next((a for a in annotations if _is_target_caption(a)), None)
    if caption is None:
        return False

    changed = False

    # 3. Re-anchor caption: centered across plot-area + fixed pixel
    #    yshift below plot bottom. This sidesteps the margin.l and
    #    chart-width inconsistencies that plagued left-aligned recipes.
    if (
        caption.get("x") != 0.5
        or caption.get("y") != 0
        or caption.get("xshift") != 0
        or caption.get("yshift") != TARGET_CAPTION_Y_SHIFT_PX
        or caption.get("xanchor") != "center"
        or caption.get("yanchor") != "top"
        or caption.get("align") != "center"
    ):
        caption["x"] = 0.5
        caption["y"] = 0
        caption["xshift"] = 0
        caption["yshift"] = TARGET_CAPTION_Y_SHIFT_PX
        caption["xanchor"] = "center"
        caption["yanchor"] = "top"
        caption["align"] = "center"
        changed = True

    # 4. Set xaxis_title standoff so title hugs the tick labels.
    if isinstance(xa_title, str):
        xa["title"] = {"text": xa_title, "standoff": TARGET_XAXIS_STANDOFF}
        layout["xaxis"] = xa
        changed = True
    elif isinstance(xa_title, dict):
        if xa_title.get("standoff") != TARGET_XAXIS_STANDOFF:
            xa_title["standoff"] = TARGET_XAXIS_STANDOFF
            changed = True

    # 5. Ensure bottom margin is enough.
    try:
        cur_b = int(margin.get("b") or 0)
    except Exception:
        cur_b = 0
    if cur_b < MIN_MARGIN_B:
        margin["b"] = MIN_MARGIN_B
        layout["margin"] = margin
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
