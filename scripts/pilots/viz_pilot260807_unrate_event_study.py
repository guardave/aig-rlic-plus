#!/usr/bin/env python3
"""Visualize the unrate run-length EVENT STUDY — abnormal CAR vs horizon, by direction.

Two panels (3-up / 3-down). Primary = cum0.2 (rounding-aware, more events) with a
bootstrap 90% CI band; strict-monotonic overlaid as a faded line for shape-robustness.
Okabe-Ito palette. Run:
  python3 scripts/pilots/viz_pilot260807_unrate_event_study.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "docs" / "pilots" / "pilot260807_unrate_runlength"
CSV = PILOT / "unrate_event_study_pilot260807.csv"
OUT = PILOT / "unrate_event_study_pilot260807.png"

BLUE, GREEN, VERM, GREY, INK = "#0072B2", "#009E73", "#D55E00", "#7f7f7f", "#222222"


def panel(ax, df, direction, primary_color, title):
    cum = df[(df.event_def == "cum0.2") & (df.direction == direction)].sort_values("horizon_months")
    strict = df[(df.event_def == "strict") & (df.direction == direction)].sort_values("horizon_months")
    h = cum.horizon_months
    ax.axhline(0, color=INK, lw=1)
    ax.fill_between(h, cum.ci_lo * 100, cum.ci_hi * 100, color=primary_color, alpha=0.15,
                    label="cum0.2 90% CI")
    ax.plot(h, cum.abnormal * 100, color=primary_color, lw=2.2,
            label=f"cum0.2 (N={int(cum.n_events.iloc[0])})")
    ax.plot(strict.horizon_months, strict.abnormal * 100, color=GREY, lw=1.4, ls="--",
            label=f"strict (N={int(strict.n_events.iloc[0])})")
    # mark any horizon whose CI excludes zero
    hit = cum[cum.ci_excludes_zero]
    if len(hit):
        ax.scatter(hit.horizon_months, hit.abnormal * 100, color=primary_color, s=55,
                   zorder=5, edgecolor="white", lw=1)
        for _, r in hit.iterrows():
            ax.annotate(f"h{int(r.horizon_months)}: {r.abnormal*100:+.1f}%\n(lone hit, 1 of ~96 tests)",
                        xy=(r.horizon_months, r.abnormal * 100),
                        xytext=(r.horizon_months + 1.5, r.abnormal * 100 + 3.5),
                        fontsize=7.2, color=primary_color,
                        arrowprops=dict(arrowstyle="->", color=primary_color, lw=1))
    ax.set_title(title, fontsize=10.5, color=INK)
    ax.set_xlabel("Horizon h (months after event, entry at event + 1m pub-lag)", fontsize=8.5)
    ax.set_ylabel("Abnormal SPY CAR (conditional − unconditional), %", fontsize=8.5)
    ax.legend(fontsize=7.5, loc="best", framealpha=0.85)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def main() -> int:
    df = pd.read_csv(CSV)
    fig, (axU, axD) = plt.subplots(1, 2, figsize=(12.5, 5.4))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.83, bottom=0.13, wspace=0.22)
    fig.suptitle("Pilot 260807 (event study) — SPY abnormal return after 3-consecutive-move "
                 "unemployment events", fontsize=13, fontweight="bold", color="#1f4e79",
                 x=0.07, ha="left", y=0.96)
    fig.text(0.07, 0.885, "Negative: signs are economically sensible (U-up → SPY underperforms, "
             "U-down → outperforms) but NO horizon's 90% CI clears zero once the risk premium is "
             "removed. The lone h=8 down-hit is a multiple-testing artifact.",
             fontsize=9, style="italic", color=INK, ha="left")
    panel(axU, df, "up", VERM, "A. 3-UP events (unemployment rising = recession warning)")
    panel(axD, df, "down", GREEN, "B. 3-DOWN events (unemployment falling = expansion)")
    fig.savefig(OUT, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
