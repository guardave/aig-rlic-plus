"""Wave 3 of fix260601_chart_hygiene — BL-VIZ-O1-LEGACY sidecar backfill.

For each chart JSON in `output/charts/<pair>/plotly/` that lacks a matching
`_meta.json` sidecar, emit the canonical VIZ-O1 `consumed` disposition
sidecar. Idempotent — re-running is a no-op on charts that already have
sidecars.

Scope after fix260601_chart_hygiene Wave 2 (TED archive):
    indpro_spy  — 10 missing sidecars
    permit_spy  — 5 missing sidecars
    vix_vix3m_spy — 5 missing sidecars
    20 total.

The 3 archived TED pairs are excluded — their charts under
`output/charts/<pair>/plotly/` are no longer referenced (their pages and
configs were moved to `_archive` locations), so they don't need VIZ-O1
compliance.

Usage:
    python3 scripts/backfill_chart_sidecars.py [--pair PAIR_ID] [--dry-run]

Sidecar schema (per VIZ-O1, mirrors the canonical templates already in
tree for `hy_ig_spy/hero_meta.json` etc.):

    {
      "chart_name": "<bare name>",
      "pair_id": "<pair>",
      "palette_id": "okabe_ito_2026",
      "rules_applied": ["VIZ-O1", "VIZ-BF1"],
      "narrative_alignment_note": "<from chart title>",
      "created_at": "<iso utc>",
      "method_name": "<bare name>",
      "expected_chart_type": "<inferred>",
      "disposition": "consumed",
      "backfilled_by": "fix260601_chart_hygiene Wave 3 (2026-06-02)"
    }
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
from _stamp import iso_utc_now  # noqa: E402

# Two scopes:
#   EMIT_TARGETS — pairs missing sidecars entirely. Original BL-VIZ-O1-LEGACY
#     scope (the 3 active legacy pairs after Wave 2 archived the TED variants).
#   PATCH_TARGETS — all active pairs. Existing sidecars on the modern pairs
#     (gold_copper_xli, hy_ig_*, etc.) often lack the VIZ-O1 disposition field;
#     patching them in completes the Disposition Mandate uniformly.
EMIT_TARGETS = ("indpro_spy", "permit_spy", "vix_vix3m_spy")
PATCH_TARGETS = (
    "indpro_spy", "indpro_xlp", "umcsent_xlv",
    "hy_ig_v2_spy", "hy_ig_spy",
    "permit_spy", "vix_vix3m_spy",
    "gold_copper_xli",
)


# Chart-type inference. Maps known bare chart names to the expected
# Plotly chart type that VIZ-O1 sidecars record. The values match those
# already present in canonical sidecars elsewhere in tree (hy_ig_spy,
# hy_ig_v2_spy, etc.).
_CHART_TYPE_HINTS = {
    "hero": "dual_axis_line",
    "regime_stats": "bar",
    "correlations": "heatmap",
    "ccf": "bar",
    "granger": "scatter",
    "rolling_granger": "scatter",
    "local_projections": "scatter",
    "quantile_regression": "scatter",
    "rf_importance": "bar",
    "tournament_scatter": "scatter",
    "equity_curves": "line",
    "drawdown": "area",
    "drawdown_comparison": "area",
    "walk_forward": "bar",
    "rolling_correlation": "line",
    "rolling_sharpe_cp": "line",
    "structural_break": "scatter",
    "subperiod_sharpe": "bar",
}


def _expected_chart_type(chart_name: str) -> str:
    """Best-effort chart-type label."""
    if chart_name in _CHART_TYPE_HINTS:
        return _CHART_TYPE_HINTS[chart_name]
    if chart_name.startswith("history_zoom_"):
        return "dual_panel_line"
    return "line"


def _title_text(chart_json: dict) -> str:
    """Extract title text from chart JSON, robust to missing fields."""
    title = chart_json.get("layout", {}).get("title")
    if isinstance(title, dict):
        return title.get("text", "") or ""
    if isinstance(title, str):
        return title
    return ""


def _plotted_window(chart_json: dict) -> str:
    """Actual date span of the plotted traces, as 'YYYY-MM-DD to YYYY-MM-DD'.

    Returns "" when x data is absent or not date-like. Drawdown-family charts
    differ per pair in whether they plot the full sample or only the OOS window,
    so a note must read the span off the data rather than assume one.
    """
    stamps = []
    for trace in chart_json.get("data", []):
        for x in (trace.get("x") or []):
            if isinstance(x, str) and len(x) >= 10 and x[4] == "-" and x[7] == "-":
                stamps.append(x[:10])
    if not stamps:
        return ""
    return f"{min(stamps)} to {max(stamps)}"


def _alignment_note(chart_name: str, title: str, chart_json: dict | None = None) -> str:
    """Compose a one-line narrative alignment note.

    For canonical chart types we know the analytical purpose; otherwise
    fall back to a literal title-based description.
    """
    base = title or chart_name.replace("_", " ")
    intent = {
        "hero": "Full-sample context view establishing the indicator-target relationship.",
        "regime_stats": "Stats across regime quartiles supporting the regime-conditional thesis.",
        "correlations": "Pearson correlations across signal variants × forward target horizons.",
        "ccf": "Cross-correlation at lags ±N showing lead/lag structure between indicator and target.",
        "granger": "Granger causality p-values by lag, both directions.",
        "rolling_granger": "Rolling-window Granger F-statistic; flags when causation strengthens or weakens.",
        "local_projections": "Local projection coefficients by forecast horizon with HAC-robust CIs.",
        "quantile_regression": "Quantile regression coefficients across the conditional target distribution.",
        "rf_importance": "Random Forest feature importance ranking the indicator's contribution vs controls.",
        "tournament_scatter": "Tournament combos scattered by OOS Sharpe vs annual return; winner highlighted.",
        "equity_curves": "Cumulative $1 invested in strategy vs buy-and-hold target over OOS window.",
        "drawdown": "Strategy drawdown timeline (peak-to-trough) over OOS window.",
        "drawdown_comparison": (
            "Strategy vs target buy-and-hold drawdown overlay. The plotted window "
            "varies by pair — some plot the full sample, some OOS only — so where "
            "this chart's trough is deeper than the OOS max drawdown quoted in the "
            "Strategy headline, read the window stated below before treating the "
            "two figures as inconsistent."
        ),
        "walk_forward": "Rolling per-year OOS Sharpe — walk-forward robustness.",
        "rolling_correlation": "24-month rolling correlation between signal and target forward returns.",
        "rolling_sharpe_cp": "24-month rolling strategy Sharpe over OOS window.",
        "structural_break": "Quandt-Andrews structural break test on the rolling signal-target correlation.",
        "subperiod_sharpe": "Strategy Sharpe across canonical market episodes (DPS-EP1 set).",
    }.get(chart_name, f"Backfill: {base}")
    if chart_name in ("drawdown", "drawdown_comparison") and chart_json is not None:
        window = _plotted_window(chart_json)
        if window:
            intent += f" Plotted window, read from the chart data: {window}."
    return intent


def _enumerate_missing(pair_id: str) -> list[Path]:
    """Charts whose sidecar is entirely absent."""
    plotly_dir = CHARTS_ROOT / pair_id / "plotly"
    if not plotly_dir.is_dir():
        return []
    missing = []
    for json_path in sorted(plotly_dir.glob("*.json")):
        if json_path.name.endswith("_meta.json"):
            continue
        sidecar = json_path.with_name(json_path.stem + "_meta.json")
        if sidecar.exists():
            continue
        missing.append(json_path)
    return missing


def _enumerate_no_disposition(pair_id: str) -> list[Path]:
    """Sidecars that exist but lack the VIZ-O1 disposition field."""
    plotly_dir = CHARTS_ROOT / pair_id / "plotly"
    if not plotly_dir.is_dir():
        return []
    needs_patch = []
    for sidecar in sorted(plotly_dir.glob("*_meta.json")):
        try:
            with open(sidecar) as fh:
                meta = json.load(fh)
        except Exception:
            continue
        if not meta.get("disposition"):
            needs_patch.append(sidecar)
    return needs_patch


def _patch_disposition(sidecar_path: Path, dry_run: bool) -> bool:
    """Add `disposition: consumed` to a sidecar that lacks it. Preserves
    all other fields. Returns True iff a file was written."""
    try:
        with open(sidecar_path) as fh:
            meta = json.load(fh)
    except Exception as e:
        print(f"  ERR  could not read {sidecar_path}: {e}", file=sys.stderr)
        return False
    if meta.get("disposition"):
        return False
    meta["disposition"] = "consumed"
    # Annotate the patch so future audits know it was a Wave 3 backfill.
    rules = meta.get("rules_applied") or []
    if "VIZ-BF1" not in rules:
        rules = list(rules) + ["VIZ-BF1"]
    meta["rules_applied"] = rules
    meta["backfilled_disposition_by"] = "fix260601_chart_hygiene Wave 3 (2026-06-02)"
    rel = sidecar_path.relative_to(REPO_ROOT)
    if dry_run:
        print(f"  DRY  patch {rel}")
        return False
    with open(sidecar_path, "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"  OK   patch {rel}")
    return True


def _emit_sidecar(chart_json_path: Path, pair_id: str, dry_run: bool) -> bool:
    """Emit a sidecar next to the chart JSON. Return True iff a file was
    written."""
    try:
        with open(chart_json_path) as fh:
            chart_doc = json.load(fh)
    except Exception as e:
        print(f"  ERR  could not read {chart_json_path}: {e}", file=sys.stderr)
        return False

    chart_name = chart_json_path.stem
    title = _title_text(chart_doc)
    sidecar_doc = {
        "chart_name": chart_name,
        "pair_id": pair_id,
        "palette_id": "okabe_ito_2026",
        "rules_applied": ["VIZ-O1", "VIZ-BF1"],
        "narrative_alignment_note": _alignment_note(chart_name, title, chart_doc),
        "created_at": iso_utc_now(),
        "method_name": chart_name,
        "expected_chart_type": _expected_chart_type(chart_name),
        "disposition": "consumed",
        "backfilled_by": "fix260601_chart_hygiene Wave 3 (2026-06-02)",
    }

    sidecar_path = chart_json_path.with_name(chart_name + "_meta.json")
    rel = sidecar_path.relative_to(REPO_ROOT)
    if dry_run:
        print(f"  DRY  {rel}")
        return False
    with open(sidecar_path, "w") as fh:
        json.dump(sidecar_doc, fh, indent=2)
    print(f"  OK   {rel}")
    return True


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pair", default=None,
                   help="Limit to a single pair_id")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    emit_pairs = (args.pair,) if args.pair else EMIT_TARGETS
    patch_pairs = (args.pair,) if args.pair else PATCH_TARGETS

    # Phase 1: emit missing sidecars on the 3 active legacy pairs.
    print("=" * 64)
    print("Phase 1: emit missing sidecars (BL-VIZ-O1-LEGACY core)")
    print("=" * 64)
    n_emitted = 0
    for pair in emit_pairs:
        missing = _enumerate_missing(pair)
        if not missing:
            print(f"({pair}: 0 missing — already canonical)")
            continue
        print(f"\n{pair} — {len(missing)} missing sidecars:")
        for chart in missing:
            if _emit_sidecar(chart, pair, args.dry_run):
                n_emitted += 1

    # Phase 2: patch the disposition field on existing-but-incomplete
    # sidecars across all active pairs.
    print()
    print("=" * 64)
    print("Phase 2: patch disposition field on existing sidecars")
    print("=" * 64)
    n_patched = 0
    for pair in patch_pairs:
        needs_patch = _enumerate_no_disposition(pair)
        if not needs_patch:
            print(f"({pair}: 0 sidecars need patching — already canonical)")
            continue
        print(f"\n{pair} — {len(needs_patch)} sidecars need disposition:")
        for sidecar in needs_patch:
            if _patch_disposition(sidecar, args.dry_run):
                n_patched += 1

    verb = "Would" if args.dry_run else "Did"
    print(f"\n{verb}: emit {n_emitted} new sidecars + patch {n_patched} existing sidecars = "
          f"{n_emitted + n_patched} VIZ-O1 actions total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
