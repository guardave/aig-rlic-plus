#!/usr/bin/env python3
"""Visualize pilot260807 (unrate run-length regime) — 4-panel review figure.

Panels (each single-axis; no dual-axis):
  A  Unemployment rate with latched-regime shading (green=falling, red=rising) + recessions
  B  Verdict: best OOS Sharpe — run-length vs incumbent / Sahm / buy-and-hold
  C  run-length per-lead OOS Sharpe (both directions) vs B&H and incumbent reference lines
  D  OOS growth of $1 (2017+): run-length best vs incumbent vs buy-and-hold

Palette: Okabe-Ito (published colorblind-safe). Run:
  python3 scripts/pilots/viz_pilot260807_unrate_runlength.py
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "pilots"))
from pair_pipeline_unrate_spy import make_position, build_threshold  # noqa: E402
from run_pilot260807_unrate_runlength import runlen_regime, OOS_START, K  # noqa: E402

PILOT = ROOT / "docs" / "pilots" / "pilot260807_unrate_runlength"
PARQUET = ROOT / "data" / "unrate_spy_monthly_latest.parquet"
OUT = PILOT / "unrate_runlen3_pilot260807.png"

# Okabe-Ito
BLUE, ORANGE, GREEN, VERM, GREY = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#7f7f7f"
INK = "#222222"
RECESSIONS = [("2001-03-01", "2001-11-30"), ("2007-12-01", "2009-06-30"), ("2020-02-01", "2020-04-30")]


def shade_regime(ax, state):
    """Green where falling-unemployment regime (-1), red where rising (+1)."""
    s = state.copy()
    idx = list(s.index)
    start = 0
    for i in range(1, len(idx) + 1):
        if i == len(idx) or s.iloc[i] != s.iloc[start]:
            v = s.iloc[start]
            c = GREEN if v < 0 else (VERM if v > 0 else GREY)
            ax.axvspan(idx[start], idx[i - 1], color=c, alpha=0.13, lw=0)
            start = i


def main() -> int:
    df = pd.read_parquet(PARQUET)
    state = runlen_regime(df["unrate"], K)
    res = pd.read_csv(PILOT / f"unrate_runlen{K}_pilot260807.csv")

    # ---- equity curves (OOS, deployable cash-fill) ----
    spy_ret = df["spy_ret"]
    # run-length best: countercyclical / L0
    pos_rl = make_position(state.shift(0), 0.0, "countercyclical")
    rl_ret = (pos_rl * spy_ret).fillna(0.0)
    # incumbent chg_6m / T_roll_p75 / procyclical / L9
    raw = df["unrate_6m_chg"].astype(float)
    thr = build_threshold(raw, "T_roll_p75")
    pos_inc = make_position(raw.shift(9), thr.shift(9), "procyclical")
    inc_ret = (pos_inc * spy_ret).fillna(0.0)
    bh_ret = spy_ret.fillna(0.0)

    def eq(r):
        r = r.loc[OOS_START:]
        return (1 + r).cumprod()

    fig = plt.figure(figsize=(11, 9))
    gs = fig.add_gridspec(2, 2, hspace=0.33, wspace=0.22,
                          left=0.07, right=0.97, top=0.90, bottom=0.07)
    fig.suptitle(f"Pilot 260807 — run-length (3-up / 3-down) regime derivative on UNRATE × SPY",
                 fontsize=13.5, fontweight="bold", color="#1f4e79", x=0.07, ha="left", y=0.965)
    fig.text(0.07, 0.925, "Negative result: the latched k=3 regime is too coarse (7 switches in 33 yrs) "
             "and is dominated by the incumbent, Sahm, and even buy-and-hold.",
             fontsize=9.5, style="italic", color=INK, ha="left")

    # ---- Panel A: unemployment + regime shading ----
    axA = fig.add_subplot(gs[0, 0])
    shade_regime(axA, state)
    for s, e in RECESSIONS:
        axA.axvspan(pd.Timestamp(s), pd.Timestamp(e), color=GREY, alpha=0.28, lw=0)
    axA.plot(df.index, df["unrate"], color=INK, lw=1.6)
    # Annotate the pathological stuck-latch: rising-latched 2016-2020 while U fell to a 50yr low.
    axA.annotate("latched RISING 2016–20\nwhile U fell to 3.5%\n(flat months break the down-run)",
                 xy=(pd.Timestamp("2018-06-30"), 4.1), xytext=(pd.Timestamp("2004-06-30"), 12.6),
                 fontsize=7.2, color=VERM, ha="left", va="top",
                 arrowprops=dict(arrowstyle="->", color=VERM, lw=1.1))
    axA.set_title("A. Unemployment rate & latched regime (7 switches)", fontsize=10, color=INK)
    axA.set_ylabel("Unemployment rate (%)", fontsize=9)
    axA.legend(handles=[Patch(fc=GREEN, alpha=0.3, label="Falling-U regime"),
                        Patch(fc=VERM, alpha=0.3, label="Rising-U regime"),
                        Patch(fc=GREY, alpha=0.4, label="NBER recession")],
               fontsize=7.5, loc="upper left", framealpha=0.85)
    for sp in ("top", "right"):
        axA.spines[sp].set_visible(False)

    # ---- Panel B: verdict bars ----
    axB = fig.add_subplot(gs[0, 1])
    labels = ["Incumbent\n(chg_6m/L9)", "Sahm\nregime", "Buy &\nhold", f"Run-length{K}\n(best)"]
    vals = [1.5510, 1.2074, 0.9910, 0.8604]
    colors = [BLUE, BLUE, GREY, VERM]
    bars = axB.bar(labels, vals, color=colors, width=0.66)
    axB.axhline(0.9910, color=GREY, ls="--", lw=1, alpha=0.8)
    for b, v in zip(bars, vals):
        axB.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.2f}",
                 ha="center", fontsize=9, color=INK, fontweight="bold")
    axB.set_title("B. Best OOS Sharpe by signal — the verdict", fontsize=10, color=INK)
    axB.set_ylabel("Best valid OOS Sharpe", fontsize=9)
    axB.set_ylim(0, 1.75)
    axB.tick_params(axis="x", labelsize=8)
    for sp in ("top", "right"):
        axB.spines[sp].set_visible(False)

    # ---- Panel C: per-lead sharpe ----
    axC = fig.add_subplot(gs[1, 0])
    v = res[res.valid & (res.strategy == "P1_long_cash")]
    for dirn, col, mk in [("countercyclical", GREEN, "o"), ("procyclical", ORANGE, "s")]:
        d = v[v.direction == dirn].sort_values("lead_months")
        axC.plot(d.lead_months, d.oos_sharpe, marker=mk, color=col, lw=2, ms=7,
                 label=f"{dirn}")
    axC.axhline(0.9910, color=GREY, ls="--", lw=1.2, label="Buy & hold 0.99")
    axC.axhline(1.5510, color=BLUE, ls=":", lw=1.4, label="Incumbent 1.55")
    axC.set_title("C. Run-length OOS Sharpe by lead — every lead trails B&H", fontsize=10, color=INK)
    axC.set_xlabel("Lead (months)", fontsize=9)
    axC.set_ylabel("OOS Sharpe", fontsize=9)
    axC.set_ylim(0, 1.7)
    axC.legend(fontsize=7.5, loc="upper right", framealpha=0.85)
    for sp in ("top", "right"):
        axC.spines[sp].set_visible(False)

    # ---- Panel D: OOS equity ----
    axD = fig.add_subplot(gs[1, 1])
    axD.plot(eq(inc_ret).index, eq(inc_ret), color=BLUE, lw=2, label="Incumbent chg_6m/L9")
    axD.plot(eq(bh_ret).index, eq(bh_ret), color=GREY, lw=1.8, label="Buy & hold")
    axD.plot(eq(rl_ret).index, eq(rl_ret), color=VERM, lw=2, label=f"Run-length{K} best")
    axD.set_title("D. Growth of $1, OOS (2017+)", fontsize=10, color=INK)
    axD.set_ylabel("Growth of $1", fontsize=9)
    axD.legend(fontsize=7.5, loc="upper left", framealpha=0.85)
    for sp in ("top", "right"):
        axD.spines[sp].set_visible(False)

    fig.savefig(OUT, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
