#!/usr/bin/env python3
"""
Retro-apply VIZ-CV1 perceptual PNG mandate to all pairs.

For every .json chart file (excluding _meta.json sidecars) in
output/charts/{pair_id}/plotly/, generate a corresponding
_perceptual_check_{chart_name}.png if one does not already exist.

Render spec: plotly.io.to_image(fig, format='png', width=1200, height=600)
Kaleido >= 1.0.0 required.
"""

import os
import glob
import plotly.io as pio

PAIRS = [
    "dff_ted_spy",
    "sofr_ted_spy",
    "ted_spliced_spy",
    "indpro_spy",
    "indpro_xlp",
    "permit_spy",
    "umcsent_xlv",
    "vix_vix3m_spy",
    "hy_ig_spy",
    "hy_ig_v2_spy",
]

CHARTS_BASE = "output/charts"

total_rendered = 0
total_skipped = 0
total_failed = 0
failures = []


def is_sidecar(stem: str) -> bool:
    """Return True if this stem is a _meta sidecar or a smoke-test log placeholder."""
    return stem.endswith("_meta") or stem.startswith("_smoke_test")


for pair_id in PAIRS:
    plotly_dir = os.path.join(CHARTS_BASE, pair_id, "plotly")
    if not os.path.isdir(plotly_dir):
        print(f"[WARN] Directory not found: {plotly_dir} — skipping pair {pair_id}")
        continue

    json_files = sorted(glob.glob(os.path.join(plotly_dir, "*.json")))
    pair_rendered = 0
    pair_skipped = 0
    pair_failed = 0

    for json_path in json_files:
        stem = os.path.basename(json_path).replace(".json", "")
        if is_sidecar(stem):
            continue

        png_path = os.path.join(plotly_dir, f"_perceptual_check_{stem}.png")
        if os.path.exists(png_path):
            pair_skipped += 1
            total_skipped += 1
            continue

        try:
            fig = pio.read_json(json_path)
            img_bytes = pio.to_image(fig, format="png", width=1200, height=600)
            with open(png_path, "wb") as f:
                f.write(img_bytes)
            print(f"  RENDERED: {pair_id}/{stem}")
            pair_rendered += 1
            total_rendered += 1
        except Exception as e:
            msg = f"  FAIL: {pair_id}/{stem} — {e}"
            print(msg)
            failures.append(msg)
            pair_failed += 1
            total_failed += 1

    print(f"[{pair_id}] rendered={pair_rendered} skipped={pair_skipped} failed={pair_failed}")

print()
print("=" * 60)
print(f"TOTAL RENDERED : {total_rendered}")
print(f"TOTAL SKIPPED  : {total_skipped} (already existed)")
print(f"TOTAL FAILED   : {total_failed}")
if failures:
    print("\nFailed charts:")
    for f in failures:
        print(f)
print("=" * 60)
