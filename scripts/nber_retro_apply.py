"""
Wave 10J.4 — NBER recession shading retro-apply
Adds NBER recession shapes to existing Plotly JSON chart files in-place.
Author: Vera <viz-vera@idficient.com>
"""

import json
from pathlib import Path
from datetime import datetime

# ── Canonical NBER parameters (VIZ-V2) ────────────────────────────────────────
RECESSIONS = [
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]
NBER_SHADING = "rgba(150,120,120,0.22)"

# ── Charts to patch ────────────────────────────────────────────────────────────
ROOT = Path("/workspaces/aig-rlic-plus/output/charts")
TARGETS = [
    ROOT / "dff_ted_spy/plotly/dff_ted_spy_hero.json",
    ROOT / "permit_spy/plotly/permit_spy_hero.json",
    ROOT / "sofr_ted_spy/plotly/sofr_ted_spy_hero.json",
    ROOT / "ted_spliced_spy/plotly/ted_spliced_spy_hero.json",
    ROOT / "vix_vix3m_spy/plotly/vix_vix3m_spy_hero.json",
    ROOT / "hy_ig_spy/plotly/drawdown.json",
    ROOT / "hy_ig_spy/plotly/walk_forward.json",
    ROOT / "hy_ig_v2_spy/plotly/equity_curves.json",
    ROOT / "hy_ig_v2_spy/plotly/drawdown.json",
    ROOT / "hy_ig_v2_spy/plotly/walk_forward.json",
    ROOT / "indpro_spy/plotly/indpro_spy_equity_curves.json",
    ROOT / "indpro_xlp/plotly/equity_curves.json",
    ROOT / "indpro_xlp/plotly/drawdown.json",
    ROOT / "indpro_xlp/plotly/walk_forward.json",
    ROOT / "indpro_xlp/plotly/rolling_sharpe.json",
    ROOT / "umcsent_xlv/plotly/equity_curves.json",
    ROOT / "umcsent_xlv/plotly/drawdown.json",
    ROOT / "umcsent_xlv/plotly/rolling_sharpe.json",
]


def parse_date(s: str) -> datetime:
    """Parse ISO date string (with or without time component)."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19], fmt[:len(s[:19])])
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")


def get_chart_date_range(fig: dict) -> tuple[datetime | None, datetime | None]:
    """Scan all traces for min/max x values."""
    min_x = max_x = None
    for trace in fig.get("data", []):
        xs = trace.get("x", [])
        if not xs:
            continue
        for val in xs:
            if val is None:
                continue
            try:
                dt = parse_date(str(val))
            except ValueError:
                continue
            if min_x is None or dt < min_x:
                min_x = dt
            if max_x is None or dt > max_x:
                max_x = dt
    return min_x, max_x


def is_nber_shape(shape: dict) -> bool:
    """True if this shape looks like an NBER recession rect."""
    return (
        shape.get("type") == "rect"
        and shape.get("fillcolor") == NBER_SHADING
        and shape.get("yref") == "paper"
    )


def existing_nber_keys(shapes: list) -> set:
    """Return set of (x0, x1, xref) for existing NBER shapes."""
    return {
        (s.get("x0", ""), s.get("x1", ""), s.get("xref", ""))
        for s in shapes
        if is_nber_shape(s)
    }


def make_shape(x0: str, x1: str, xref: str) -> dict:
    return {
        "fillcolor": NBER_SHADING,
        "layer": "below",
        "line": {"width": 0},
        "type": "rect",
        "x0": f"{x0}T00:00:00",
        "x1": f"{x1}T00:00:00",
        "xref": xref,
        "y0": 0,
        "y1": 1,
        "yref": "paper",
    }


def detect_xrefs(layout: dict) -> list[str]:
    """Return list of xref strings for all x-axes in the layout."""
    xrefs = []
    if "xaxis" in layout:
        xrefs.append("x")
    if "xaxis2" in layout:
        xrefs.append("x2")
    if "xaxis3" in layout:
        xrefs.append("x3")
    # Fallback: if no xaxis key at all, assume single panel
    if not xrefs:
        xrefs = ["x"]
    return xrefs


def patch_file(path: Path) -> dict:
    """Patch a single JSON file. Returns a result dict."""
    result = {"file": str(path.relative_to(ROOT)), "status": None, "added": 0, "skipped": 0}

    if not path.exists():
        result["status"] = "MISSING"
        return result

    with open(path) as f:
        fig = json.load(f)

    layout = fig.setdefault("layout", {})
    shapes = layout.setdefault("shapes", [])

    min_x, max_x = get_chart_date_range(fig)
    if min_x is None or max_x is None:
        result["status"] = "NO_DATE_RANGE"
        return result

    xrefs = detect_xrefs(layout)
    existing = existing_nber_keys(shapes)

    added = 0
    for rec_start, rec_end in RECESSIONS:
        rec_s = datetime.strptime(rec_start, "%Y-%m-%d")
        rec_e = datetime.strptime(rec_end, "%Y-%m-%d")
        # Skip if recession doesn't overlap chart range
        if rec_e < min_x or rec_s > max_x:
            result["skipped"] += 1
            continue
        for xref in xrefs:
            key = (f"{rec_start}T00:00:00", f"{rec_end}T00:00:00", xref)
            if key in existing:
                continue
            shapes.append(make_shape(rec_start, rec_end, xref))
            existing.add(key)
            added += 1

    layout["shapes"] = shapes
    result["added"] = added

    if added > 0:
        with open(path, "w") as f:
            json.dump(fig, f, separators=(",", ":"))
        result["status"] = "PATCHED"
    else:
        result["status"] = "ALREADY_COMPLIANT"

    return result


def main():
    print("Wave 10J.4 — NBER Shading Retro-Apply")
    print("=" * 60)

    results = [patch_file(p) for p in TARGETS]

    total_added = sum(r["added"] for r in results)
    patched = [r for r in results if r["status"] == "PATCHED"]
    compliant = [r for r in results if r["status"] == "ALREADY_COMPLIANT"]
    missing = [r for r in results if r["status"] == "MISSING"]
    no_range = [r for r in results if r["status"] == "NO_DATE_RANGE"]

    for r in results:
        icon = {"PATCHED": "✓", "ALREADY_COMPLIANT": "–", "MISSING": "✗", "NO_DATE_RANGE": "?"}.get(r["status"], "?")
        print(f"  {icon} {r['file']}  (+{r['added']} shapes, {r['skipped']} recessions out-of-range)")

    print()
    print(f"Summary: {len(patched)} patched, {len(compliant)} already compliant, "
          f"{len(missing)} missing, {len(no_range)} no date range")
    print(f"Total shapes added: {total_added}")


if __name__ == "__main__":
    main()
