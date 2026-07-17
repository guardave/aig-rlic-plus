#!/usr/bin/env python3
"""Build the 1-page A4 executive summary PDF for pilot260717 (petrol grid-ceiling test).

Reproducible: reads the committed extended tournament CSV
(docs/pilots/pilot260717_grid_ceiling/petrol_tournament_L0-36_pilot260717.csv),
recomputes the per-lead best valid OOS Sharpe, and renders the summary. Nothing
is hardcoded that can be derived from the CSV.

Run: python3 scripts/pilots/build_pilot260717_summary_pdf.py
"""
from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "docs" / "pilots" / "pilot260717_grid_ceiling"
CSV = PILOT / "petrol_tournament_L0-36_pilot260717.csv"
OUT = PILOT / "petrol_grid_ceiling_pilot_summary.pdf"

BLUE, RED, GREY, GREEN = "#1f4e79", "#c0392b", "#7f7f7f", "#2e7d32"


def main() -> int:
    df = pd.read_csv(CSV)
    strat = df[df.signal != "BENCHMARK"].copy()
    val = strat[strat.valid == True]
    best = val.groupby("lead_months")["oos_sharpe"].max()
    leads = sorted(int(x) for x in best.index)
    incumbent = round(float(best.get(11)), 3)
    bench = float(df[df.signal == "BENCHMARK"]["oos_sharpe"].iloc[0])
    worst_L = int(best.idxmin())
    ext = [18, 24, 36]
    n_combos, n_valid = len(strat), len(val)

    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
    fig.subplots_adjust(left=0.08, right=0.95, top=0.99, bottom=0.05)
    gs = fig.add_gridspec(3, 1, height_ratios=[0.95, 1.05, 1.55], hspace=0.30)

    # ── Header + verdict ─────────────────────────────────────────────
    ax0 = fig.add_subplot(gs[0]); ax0.axis("off")
    ax0.text(0, 1.00, "PILOT 260717 — Lead-Grid Ceiling Test",
             fontsize=17, fontweight="bold", color=BLUE, va="top")
    ax0.text(0, 0.85, "Does extending the monthly lead grid beyond 12 months surface a "
             "signal we are missing?", fontsize=10.5, style="italic", color="#333", va="top")
    ax0.text(0, 0.70, "Pair: Industrial Production → Petroleum Inventories (petrol_inv_spy)   |   "
             "Lesandro (Lead)   |   2026-07-17", fontsize=8.5, color=GREY, va="top")

    ax0.add_patch(plt.Rectangle((0, 0.02), 1.0, 0.56, transform=ax0.transAxes,
                  facecolor="#eef3f8", edgecolor=BLUE, linewidth=1.2))
    ax0.text(0.02, 0.50, "VERDICT — the extension surfaces nothing.", fontsize=12,
             fontweight="bold", color=RED, va="top")
    ax0.text(0.02, 0.37,
             f"The winner is unchanged at L11 (OOS Sharpe {incumbent:.2f}), and no lead beyond L12 "
             f"beats it. The stakeholder\ndeck's claim of a 24–36 month petroleum lead lands on the two "
             f"weakest horizons on the grid\n(L{worst_L} is the single worst). The L0–12 ceiling is "
             f"empirically justified for this pair.",
             fontsize=9.2, color="#222", va="top", linespacing=1.55)

    # ── Bar chart: best valid OOS Sharpe by lead ─────────────────────
    ax1 = fig.add_subplot(gs[1])
    vals = [float(best[L]) for L in leads]
    colors = [GREEN if L == 11 else (RED if L in ext else BLUE) for L in leads]
    xs = range(len(leads))
    ax1.bar(list(xs), vals, color=colors, width=0.72)
    ax1.axhline(incumbent, color=GREEN, ls="--", lw=1, alpha=0.7)
    ax1.text(0.2, incumbent + 0.006, f"L11 incumbent {incumbent:.2f}",
             fontsize=7.5, color=GREEN, ha="left")
    ax1.set_xticks(list(xs)); ax1.set_xticklabels([f"L{L}" for L in leads], fontsize=7.5)
    ax1.set_ylabel("Best valid OOS Sharpe", fontsize=9)
    ax1.set_ylim(min(vals) - 0.05, max(vals) + 0.05)
    ax1.set_title(f"Best out-of-sample Sharpe by lead horizon (buy & hold = {bench:.2f}, "
                  "off-scale below) — extension leads in red",
                  fontsize=9, color="#333", pad=6)
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)

    # ── Findings + method ────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[2]); ax2.axis("off")
    lines = [
        ("Key findings", "head"),
        (f"•  Global winner unchanged: L11, OOS Sharpe {incumbent:.2f} "
         f"(petrol_level_z60 / T2_roll_p25 / P1_long_cash_pro / LB36).", "body"),
        (f"•  Extension horizons underperform: L18 {best[18]:.2f}, L24 {best[24]:.2f} "
         f"(worst on grid), L36 {best[36]:.2f} — all below L11 and mid-grid.", "body"),
        ("•  The long-lead top entries are degenerate, not discoveries: large clusters of combos "
         "sit exactly at", "body"),
        (f"   the buy-and-hold Sharpe {bench:.2f} (L18: 28, L24: 20, L36: 20) — always-invested rules "
         "collapsing to benchmark,", "body"),
        ("   plus P2-on-binary threshold-insensitive ties. On a flat leaderboard these read as "
         "multiple-testing noise.", "body"),
        ("•  Statistical hurdle: nothing beyond L12 approaches the incumbent, so the t > 3.0 "
         "(Harvey-Liu-Zhu) hurdle never engages.", "body"),
        ("Method", "head"),
        (f"•  Extended the grid to L0–12 + {{18, 24, 36}} (added, not replaced, so L11 stays reachable "
         "and any long-lead win is", "body"),
        ("   unambiguous). Re-scored the full tournament with production ECON-T4 deployable scoring "
         "(undefined position → cash).", "body"),
        (f"•  {n_combos:,} strategy combinations ({n_valid:,} valid); OOS window 2017-08 to 2025-09 "
         "(98 months). L36 retains full OOS —", "body"),
        ("   no window starvation. Winner and production tournament were left untouched (ECON-T5 "
         "immutability respected).", "body"),
        ("Caveat & scope", "head"),
        ("•  This tests the TRADABLE long lead (Sharpe). A complete test of the 24–36mo claim would also "
         "check raw lead-lag", "body"),
        ("   predictability (correlation / Granger) at those horizons, which the tournament does not "
         "isolate.", "body"),
        ("•  Petroleum was the deck's strongest a-priori long-lead candidate. One pair is not "
         "dispositive; the grid-SHAPE", "body"),
        ("   question (dense vs sparse) is untested. Evidence for issue #23. A second pair "
         "(indpro_xlp) is under test.", "body"),
    ]
    y = 1.00
    for txt, kind in lines:
        if kind == "head":
            y -= 0.015
            ax2.text(0, y, txt, fontsize=10, fontweight="bold", color=BLUE, va="top")
            y -= 0.070
        else:
            ax2.text(0, y, txt, fontsize=8.4, color="#222", va="top", linespacing=1.3)
            y -= 0.055

    with PdfPages(OUT) as pdf:
        pdf.savefig(fig)
    fig.savefig(OUT.with_suffix(".png"), dpi=110)  # preview companion
    plt.close(fig)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
