#!/usr/bin/env python3
"""Retro-apply VIZ-QR1 dual-panel quartile charts across active pairs.

Rule VIZ-QR1 (2026-06-10, fix260610_xpair_general): every pair's quartile
regime chart shows Annualized Sharpe (left) + Annualized Return % (right)
side-by-side. Reference look: umcsent_xlv (already conformant — skipped).
Sample hy_ig_v2_spy is FROZEN per standing user direction — skipped.

Per-pair data adapters normalise each pair's regime CSV into
(quartile_labels, sharpe, ann_return_pct), then the shared
`scripts/_quartile_chart.py` helper builds the figure. Output overwrites the
pair's existing regime chart JSON (file name preserved so pair_configs need
no changes), regenerates the `_meta.json` sidecar and the perceptual PNG.

Pairs covered:
  indpro_spy      regime_stats.json   <- exploratory_20260314/regime_descriptive_stats.csv
  permit_spy      regime_stats.json   <- exploratory_20260314/regime_descriptive_stats.csv
  vix_vix3m_spy   regime_stats.json   <- exploratory_20260314/regime_descriptive_stats.csv
  indpro_xlp      regime_stats.json   <- exploratory_20260420/regime_descriptive_stats.csv
  hy_ig_spy       regime_stats.json   <- exploratory_20260422/regime_descriptive_stats.csv
  gold_copper_xli quartile_returns.json <- regime_quartile_returns.csv (derived:
                  sharpe = mean/std * sqrt(252/63); ann_return_pct = mean * 4 * 100)
"""

from __future__ import annotations

import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts._quartile_chart import make_dual_panel_regime_chart  # noqa: E402


def _latest(pattern: str) -> Path:
    matches = sorted(glob.glob(str(ROOT / pattern)))
    if not matches:
        raise FileNotFoundError(pattern)
    return Path(matches[-1])


def _std_adapter(csv_path: Path) -> tuple[list, list, list]:
    """Pairs whose CSV already has regime / sharpe / ann_return_pct columns."""
    df = pd.read_csv(csv_path)
    return (
        df["regime"].tolist(),
        df["sharpe"].round(2).tolist(),
        df["ann_return_pct"].round(1).tolist(),
    )


def _gold_copper_adapter(csv_path: Path) -> tuple[list, list, list]:
    """gold_copper_xli: derive from 63d-forward-return quartile stats.

    sharpe = (mean / std) * sqrt(252/63)  [= *2, annualization of 63d stats]
    ann_return_pct = mean * (252/63) * 100  [arithmetic annualization]
    Matches the KS-108 fix convention (commit 078ce14).
    """
    df = pd.read_csv(csv_path)
    ann_factor = 252.0 / 63.0  # = 4
    sharpe = ((df["mean"] / df["std"]) * np.sqrt(ann_factor)).round(2).tolist()
    ann_return_pct = (df["mean"] * ann_factor * 100).round(1).tolist()
    return df["quartile"].tolist(), sharpe, ann_return_pct


# Intuitive quartile labels per fix260526 #27 + VIZ-NS1: raw machine codes
# ("Q1_low") never appear on a user surface. Keys are the CSV regime codes.
_GROWTH_LABELS = {
    "Q1_low": "Q1<br>(Weakest growth)",
    "Q2": "Q2<br>(Below-median growth)",
    "Q3": "Q3<br>(Above-median growth)",
    "Q4_high": "Q4<br>(Strongest growth)",
}

PAIRS = {
    "indpro_spy": dict(
        csv="results/indpro_spy/exploratory_*/regime_descriptive_stats.csv",
        adapter=_std_adapter,
        chart_name="regime_stats",
        signal_label="INDPRO YoY",
        x_axis_title="IP YoY Growth Quartile",
        label_map=_GROWTH_LABELS,
    ),
    "permit_spy": dict(
        csv="results/permit_spy/exploratory_*/regime_descriptive_stats.csv",
        adapter=_std_adapter,
        chart_name="regime_stats",
        signal_label="Building Permits YoY",
        x_axis_title="Permits YoY Growth Quartile",
        label_map=_GROWTH_LABELS,
    ),
    "vix_vix3m_spy": dict(
        csv="results/vix_vix3m_spy/exploratory_*/regime_descriptive_stats.csv",
        adapter=_std_adapter,
        chart_name="regime_stats",
        signal_label="VIX/VIX3M Ratio",
        x_axis_title="VIX/VIX3M Ratio Quartile",
        label_map={
            "Q1_low": "Q1<br>(Lowest ratio — calm)",
            "Q2": "Q2",
            "Q3": "Q3",
            "Q4_high": "Q4<br>(Highest ratio — stressed)",
        },
    ),
    "indpro_xlp": dict(
        csv="results/indpro_xlp/exploratory_*/regime_descriptive_stats.csv",
        adapter=_std_adapter,
        chart_name="regime_stats",
        signal_label="INDPRO YoY",
        x_axis_title="IP Growth Regime",
        # fix260526 #27 exact wording preserved (YYY praised these labels)
        label_map={
            "Q1_low": "Q1<br>(Weakest IP growth)",
            "Q2": "Q2<br>(Below-median growth)",
            "Q3": "Q3<br>(Above-median growth)",
            "Q4_high": "Q4<br>(Strongest IP growth)",
        },
    ),
    # NOTE: hy_ig_spy is NOT in this runner. Its Story regime chart is the
    # 2-state HMM Calm/Stress discrimination (not a quartile chart) — the
    # dual-panel treatment is applied on its native HMM axis inside
    # scripts/generate_charts_hy_ig_spy.py::chart_regime_stats, which
    # computes the regime stats from master+signals parquets at run time.
    "gold_copper_xli": dict(
        csv="results/gold_copper_xli/regime_quartile_returns.csv",
        adapter=_gold_copper_adapter,
        chart_name="quartile_returns",
        signal_label="Gold/Copper Z-Score",
        x_axis_title="Z-Score Quartile",
        label_map={
            "Q1_low": "Q1<br>(Low ratio — risk-on)",
            "Q2": "Q2",
            "Q3": "Q3",
            "Q4_high": "Q4<br>(High ratio — risk-off)",
        },
    ),
}


def main() -> int:
    iso_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for pair_id, spec in PAIRS.items():
        csv_path = _latest(spec["csv"])
        raw_labels, sharpe, ann_ret = spec["adapter"](csv_path)
        label_map = spec.get("label_map", {})
        labels = [label_map.get(l, l) for l in raw_labels]
        fig = make_dual_panel_regime_chart(
            quartile_labels=labels,
            sharpe=sharpe,
            ann_return_pct=ann_ret,
            signal_label=spec["signal_label"],
            x_axis_title=spec["x_axis_title"],
        )
        outdir = ROOT / "output" / "charts" / pair_id / "plotly"
        outdir.mkdir(parents=True, exist_ok=True)
        chart_path = outdir / f"{spec['chart_name']}.json"
        pio.write_json(fig, str(chart_path), pretty=False)

        meta = {
            "chart_name": spec["chart_name"],
            "pair_id": pair_id,
            "palette_id": "quartile_v1",
            "rules_applied": ["VIZ-QR1", "VIZ-IC1"],
            "narrative_alignment_note": (
                f"VIZ-QR1 dual-panel retro-apply ({iso_now}): Annualized Sharpe "
                f"+ Annualized Return % side-by-side per quartile, sourced from "
                f"{csv_path.relative_to(ROOT)}. Values: sharpe={sharpe}, "
                f"ann_return_pct={ann_ret}."
            ),
            "generated_at": iso_now,
            "generated_by": "Lead Lesandro (fix260610_xpair_general, VIZ-QR1 retro-apply)",
            "disposition": "consumed",
        }
        (outdir / f"{spec['chart_name']}_meta.json").write_text(json.dumps(meta, indent=2))

        try:
            fig.write_image(str(outdir / f"_perceptual_check_{spec['chart_name']}.png"),
                            width=1100, height=540, scale=1)
        except Exception as e:
            print(f"  PNG fail for {pair_id}: {e}")

        print(f"  {pair_id:18s} {spec['chart_name']:18s} sharpe={sharpe}  ann_ret_pct={ann_ret}")
    print("VIZ-QR1 retro-apply complete (umcsent_xlv already conformant; Sample frozen — both skipped).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
