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

TARGET_CAPTION_Y = -0.28
TARGET_XAXIS_STANDOFF = 12
MIN_MARGIN_B = 110

# Filename prefixes covered. Add new chart families here as needed.
TIMESERIES_PREFIXES = (
    "rolling_",
    "walk_forward",
    "drawdown",
    "equity_curves",
    "structural_break",
)


def _is_target_caption(anno: dict) -> bool:
    """Return True iff the annotation is the small grey source-note caption.

    Heuristics: paper-anchored, y < 0, and either small grey font or one of
    the known caption substrings.
    """
    if anno.get("yref") != "paper":
        return False
    try:
        ay = float(anno.get("y"))
    except Exception:
        return False
    if ay >= 0:
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

    # 3. Push caption to standard y.
    try:
        cur_caption_y = float(caption.get("y"))
    except Exception:
        cur_caption_y = None
    if cur_caption_y != TARGET_CAPTION_Y:
        caption["y"] = TARGET_CAPTION_Y
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


def _is_target_chart(path: Path) -> bool:
    name = path.name
    return any(name.startswith(p) for p in TIMESERIES_PREFIXES)


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
    paths = [p for p in paths if not p.name.endswith("_meta.json") and _is_target_chart(p)]

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
