#!/usr/bin/env python3
"""permit_spy — Wave-3 evidence-chart patches (items 80 + 82).

Item 80: add significance stars (* p<0.05, ** p<0.01) to the cells of
correlations.json. p-values are computed in-place from the signal x
forward-return monthly series in results/permit_spy/signals_*.parquet
(scipy.stats.pearsonr — same definition the original heatmap used).

Item 82: structural_break.json renders an orange dashed vertical line
labelled "Structural Break" at the chart's max-F-stat date even though
the underlying Quandt-Andrews test is not significant (p=0.267). Drop
that shape + annotation when p>=0.05 — leave the rolling-R² line and
recession-shading rectangles intact.

Both patches are pair-local: they read the existing JSON, mutate
specific structural fields, write back. No shared template or pipeline
edit. Idempotent.

Usage
-----
    python3 scripts/patch_permit_evidence_charts.py
"""
from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

REPO_ROOT = Path(__file__).resolve().parents[1]
PAIR_ID = "permit_spy"
CHART_DIR = REPO_ROOT / "output" / "charts" / PAIR_ID / "plotly"
RESULTS_DIR = REPO_ROOT / "results" / PAIR_ID

SIG_LEVEL_5 = 0.05
SIG_LEVEL_1 = 0.01


def _load_z(z) -> np.ndarray:
    """Decode a Plotly inline z-array (base64) or pass-through a list."""
    if isinstance(z, dict) and "bdata" in z:
        arr = np.frombuffer(base64.b64decode(z["bdata"]), dtype=z.get("dtype", "float64"))
        if "shape" in z:
            shape = tuple(int(s) for s in z["shape"].split(","))
            arr = arr.reshape(shape)
        return arr
    return np.array(z)


def patch_correlations() -> None:
    """Add significance stars to correlations heatmap cells."""
    print("\n[1/2] Patching correlations.json — significance stars (item 80)")

    chart_path = CHART_DIR / "correlations.json"
    with open(chart_path) as fh:
        d = json.load(fh)

    # Recompute p-values from the source time series.
    sig_parquet = sorted(RESULTS_DIR.glob("signals_*.parquet"))[-1]
    sig_df = pd.read_parquet(sig_parquet)
    sig_df.index = pd.DatetimeIndex(sig_df.index)

    # We need the SAME signal columns the heatmap rows refer to. The
    # heatmap rows use short keys (`accel`, `mom`, `yoy`, `zscore_60m`,
    # `mom_3m`, `mom_6m`, `contraction`, `dev_trend`). The signals
    # parquet uses prefixed names (`permit_accel`, `permit_mom1m` etc.)
    # AND `dev_trend` is missing entirely (it lives in the master
    # parquet, not the signals parquet). Reconcile from the master too.
    master_parquet = sorted((REPO_ROOT / "data").glob(f"{PAIR_ID}_monthly_*.parquet"))[-1]
    master_df = pd.read_parquet(master_parquet)
    master_df.index = pd.DatetimeIndex(master_df.index)

    # Map heatmap-row label → (df, column-name)
    row_lookup = {
        "accel":       (sig_df, "permit_accel"),
        "contraction": (sig_df, "permit_contraction"),
        "dev_trend":   (master_df, "permit_dev_trend"),
        "mom":         (sig_df, "permit_mom1m"),
        "mom_3m":      (sig_df, "permit_mom_3m"),
        "mom_6m":      (sig_df, "permit_mom_6m"),
        "yoy":         (sig_df, "permit_yoy"),
        "zscore_60m":  (sig_df, "permit_zscore_60m"),
    }
    horizon_lookup = {
        "1m":  ("spy_fwd_1m",  master_df),
        "3m":  ("spy_fwd_3m",  master_df),
        "6m":  ("spy_fwd_6m",  master_df),
        "12m": ("spy_fwd_12m", master_df),
    }

    for trace in d["data"]:
        if trace.get("type") != "heatmap":
            continue

        rows = trace["y"]
        cols = trace["x"]
        z_arr = _load_z(trace["z"])

        new_text = []
        for r_idx, row_label in enumerate(rows):
            row_text = []
            if row_label not in row_lookup:
                # Unknown row — keep original text fallback.
                for c_idx, col_label in enumerate(cols):
                    row_text.append(f"{z_arr[r_idx, c_idx]:.3f}")
                new_text.append(row_text)
                continue

            sig_src, sig_col = row_lookup[row_label]
            sig_series = sig_src[sig_col].dropna() if sig_col in sig_src.columns else None

            for c_idx, col_label in enumerate(cols):
                fwd_col, fwd_src = horizon_lookup[col_label]
                fwd_series = fwd_src[fwd_col].dropna() if fwd_col in fwd_src.columns else None

                stars = ""
                if sig_series is not None and fwd_series is not None:
                    common = sig_series.index.intersection(fwd_series.index)
                    if len(common) >= 30:
                        s = sig_series.loc[common].astype(float)
                        f = fwd_series.loc[common].astype(float)
                        # Drop any residual NaN from either side.
                        ok = (~s.isna()) & (~f.isna())
                        if ok.sum() >= 30:
                            r, p = pearsonr(s[ok], f[ok])
                            if p < SIG_LEVEL_1:
                                stars = "**"
                            elif p < SIG_LEVEL_5:
                                stars = "*"

                row_text.append(f"{z_arr[r_idx, c_idx]:.3f}{stars}")
            new_text.append(row_text)

        trace["text"] = new_text
        trace["texttemplate"] = "%{text}"

    # Update layout title to reflect the convention.
    title = d.get("layout", {}).get("title", {})
    base = title.get("text", "Correlation: Permit Signals → SPY Returns")
    if "(* p<0.05" not in base:
        title["text"] = f"{base}<br><sub>* p<0.05, ** p<0.01 (Pearson)</sub>"
        d["layout"]["title"] = title

    with open(chart_path, "w") as fh:
        json.dump(d, fh)

    # Also bump the sidecar.
    meta_path = CHART_DIR / "correlations_meta.json"
    if meta_path.exists():
        with open(meta_path) as fh:
            meta = json.load(fh)
        meta["last_patch"] = "fix260605 W3-80 significance stars"
        meta["last_patch_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(meta_path, "w") as fh:
            json.dump(meta, fh, indent=2)
    print(f"  patched -> {chart_path.relative_to(REPO_ROOT)}")


def patch_structural_break() -> None:
    """Drop the orange Structural Break flag when the test is not significant."""
    print("\n[2/2] Patching structural_break.json — false-alarm flag (item 82)")

    chart_path = CHART_DIR / "structural_break.json"
    with open(chart_path) as fh:
        d = json.load(fh)

    # Read the underlying test result.
    sb_path = RESULTS_DIR / "structural_break_permit_spy.json"
    with open(sb_path) as fh:
        sb = json.load(fh)
    p_value = float(sb["p_value"])

    layout = d.get("layout", {})

    if p_value >= SIG_LEVEL_5:
        # Drop the orange dashed flag line and its accompanying
        # "Structural Break" label. Match conservatively: orange dashed
        # lines (rgba(213,94,0...)) AND any annotation whose text
        # starts with "Structural Break".
        shapes = layout.get("shapes", [])
        new_shapes = []
        dropped_shape_count = 0
        for s in shapes:
            color = s.get("line", {}).get("color", "")
            if s.get("type") == "line" and "213,94,0" in color:
                dropped_shape_count += 1
                continue
            new_shapes.append(s)
        layout["shapes"] = new_shapes

        ann = layout.get("annotations", [])
        new_ann = []
        dropped_ann_count = 0
        for a in ann:
            text = a.get("text", "")
            if text.startswith("Structural Break") and not text.startswith("Structural Break Analysis"):
                dropped_ann_count += 1
                continue
            # Update the test summary annotation to be more honest.
            if text.startswith("Quandt-Andrews"):
                a["text"] = (
                    f"Quandt-Andrews test: F={sb['max_f_stat']:.3f}, "
                    f"p={p_value:.3f} — <b>not significant at 5%</b>; "
                    f"break-date flag suppressed."
                )
            new_ann.append(a)
        layout["annotations"] = new_ann

        print(f"  p={p_value:.3f} >= 0.05 → dropped {dropped_shape_count} shape(s), "
              f"{dropped_ann_count} annotation(s)")
    else:
        print(f"  p={p_value:.3f} < 0.05 → flag kept (significant break)")

    with open(chart_path, "w") as fh:
        json.dump(d, fh)

    meta_path = CHART_DIR / "structural_break_meta.json"
    if meta_path.exists():
        with open(meta_path) as fh:
            meta = json.load(fh)
        meta["last_patch"] = "fix260605 W3-82 suppress non-significant break flag"
        meta["last_patch_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(meta_path, "w") as fh:
            json.dump(meta, fh, indent=2)
    print(f"  patched -> {chart_path.relative_to(REPO_ROOT)}")


def main() -> None:
    print(f"=== {PAIR_ID} evidence-chart patches ===")
    patch_correlations()
    patch_structural_break()


if __name__ == "__main__":
    main()
