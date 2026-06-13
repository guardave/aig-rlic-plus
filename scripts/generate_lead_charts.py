#!/usr/bin/env python3
"""Generate VIZ-LEAD1 lead-analysis chart pair for non-frozen pairs.

Two charts per pair, numbers re-read from Evan's CSVs at generation time:
  1. correlations_lead_view   <- lead_correlation_{date}.csv
  2. lead_sharpe_distribution <- lead_tournament_{date}.csv

Matches permit_spy reference shape (vichua). Adds _meta.json sidecars + perceptual PNGs.
Rule: VIZ-LEAD1, VIZ-IC1, VIZ-TX1. Palette: okabe_ito_2026.

NEVER touches the frozen Sample hy_ig_v2_spy.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[1]
DATE = "20260613"
CREATED = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Okabe-Ito palette (canonical, from color_palette_registry.json okabe_ito_2026)
PAL = json.loads((ROOT / "docs/schemas/color_palette_registry.json").read_text())["palettes"]["okabe_ito_2026"]
BENCH = PAL["benchmark_trace"]      # #6C7A89
BAR = PAL["primary_data_trace"]      # #D55E00
DOT = "#999999"

# Pair -> (indicator display, target display, sample range note, B&H OOS Sharpe).
# B&H values resolved from each pair's winner_summary.json at canonical OOS window;
# SPY pairs lacking an explicit B&H key use the canonical SPY OOS B&H (0.8935,
# from busloans_spy winner_summary.json bh_sharpe; corroborated by permit chart 0.8939).
SPY_BH = 0.8935
PAIRS = {
    "indpro_spy":      ("Industrial Production", "SPY", SPY_BH),
    "permit_spy":      ("Building Permits", "SPY", 0.8939),  # keep vichua's embedded value
    "vix_vix3m_spy":   ("VIX/VIX3M Term Structure", "SPY", SPY_BH),
    "indpro_xlp":      ("Industrial Production", "XLP", 0.7437),
    "hy_ig_spy":       ("HY-IG Credit Spread", "SPY", 0.8129),
    "umcsent_xlv":     ("UMich Consumer Sentiment", "XLV", 0.7164),
    "gold_copper_xli": ("Gold/Copper Ratio", "XLI", 0.6558),
    "busloans_spy":    ("C&I Loans", "SPY", 0.8935),
}
# Pairs Evan flagged RE-RUN where the L7-12 peak must be visible.
RERUN_FLAG = {"indpro_spy", "indpro_xlp", "umcsent_xlv", "gold_copper_xli"}

LEADS = [f"L{i}" for i in range(13)]


def parse_cell(s):
    """'+0.141**' -> (0.141, '**'). Returns (float, stars_str)."""
    s = s.strip()
    m = re.match(r"^([+-]?\d*\.?\d+)(\**)$", s)
    if not m:
        return float("nan"), ""
    return float(m.group(1)), m.group(2)


def read_corr(pair):
    import csv
    rows = []
    with open(ROOT / f"results/{pair}/lead_correlation_{DATE}.csv") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def read_tourn(pair):
    import csv
    rows = []
    with open(ROOT / f"results/{pair}/lead_tournament_{DATE}.csv") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def build_corr_chart(pair, ind, tgt):
    rows = read_corr(pair)
    transforms = [r["transform"] for r in rows]
    z, text = [], []
    for r in rows:
        zr, tr = [], []
        for L in LEADS:
            val, stars = parse_cell(r[L])
            zr.append(val)
            tr.append(f"{val:+.3f}{stars}")
        z.append(zr)
        text.append(tr)
    # best lead per the data (max |best_r| across transforms)
    best = max(rows, key=lambda r: abs(float(r["best_r"])))
    best_caption = (f"Strongest lead: {best['transform']} at {best['best_lead']} "
                    f"(r={float(best['best_r']):+.3f}).")

    fig = go.Figure(go.Heatmap(
        z=z, x=LEADS, y=transforms, text=text, texttemplate="%{text}",
        textfont={"size": 9},
        colorscale="RdBu_r", zmid=0, zmin=-max(0.2, max(abs(v) for row in z for v in row)),
        zmax=max(0.2, max(abs(v) for row in z for v in row)),
        colorbar={"title": "Pearson r"},
        hovertemplate="signal=%{y}<br>lead=%{x}<br>r=%{text}<extra></extra>",
    ))
    title = (f"Lead-Lag Predictability: {ind} Signal (lagged L months) vs "
             f"{tgt} 1-Month Forward Return"
             f"<br><sub>Pearson correlations across lead horizons L0..L12. "
             f"* p<0.05, ** p<0.01. {best_caption}</sub>")
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={"title": {"text": "Lead (months) applied to signal"}, "side": "bottom"},
        yaxis={"title": {"text": "Signal transform"}, "autorange": "reversed"},
        template="plotly_white",
        margin={"l": 140, "r": 80, "t": 90, "b": 60},
        annotations=[{
            "text": "Source: FRED / market data via Evan ECON-LA1. " + best_caption,
            "showarrow": False, "xref": "paper", "yref": "paper",
            "x": 0, "y": -0.13, "font": {"size": 10, "color": "#666"}, "align": "left",
        }],
    )
    return fig, best_caption


def build_sharpe_chart(pair, ind, tgt, bh):
    rows = read_tourn(pair)
    leads = [int(r["lead_months"]) for r in rows]
    best = [float(r["best_oos_sharpe"]) for r in rows]
    p25 = [float(r["p25_oos_sharpe"]) for r in rows]
    med = [float(r["median_oos_sharpe"]) for r in rows]
    p75 = [float(r["p75_oos_sharpe"]) for r in rows]
    n_valid = [int(r["n_valid"]) for r in rows]
    xlab = [f"L{l}" for l in leads]

    # locate the max
    imax = max(range(len(best)), key=lambda i: best[i])
    max_lead, max_val = leads[imax], best[imax]
    win = rows[imax]
    # spike vs ridge: how many leads within 0.05 of the max
    near = sum(1 for v in best if abs(v - max_val) <= 0.05)
    shape = "a single spike" if near <= 2 else f"a broad ridge ({near} leads within 0.05)"
    cap = (f"Best OOS Sharpe {max_val:.2f} at L{max_lead} "
           f"({win['best_signal']} x {win['best_strategy']}); {shape}. "
           f"Buy-and-hold {tgt} OOS Sharpe = {bh:.2f}.")

    fig = go.Figure()
    # p25-p75 cloud strip (band)
    fig.add_trace(go.Scatter(
        x=xlab + xlab[::-1], y=p75 + p25[::-1], fill="toself",
        fillcolor="rgba(153,153,153,0.18)", line={"width": 0},
        name="p25-p75 of valid combos", hoverinfo="skip",
    ))
    # median strip
    fig.add_trace(go.Scatter(
        x=xlab, y=med, mode="lines+markers", name="Median valid combo",
        line={"color": DOT, "width": 1.5, "dash": "dot"},
        marker={"size": 5, "color": DOT},
        hovertemplate="%{x}<br>median Sharpe=%{y:.3f}<extra></extra>",
    ))
    # best-per-lead bars
    fig.add_trace(go.Bar(
        x=xlab, y=best, name="Best Sharpe per lead",
        marker={"color": BAR},
        text=[f"{v:.2f}" for v in best], textposition="outside", textfont={"size": 9},
        customdata=n_valid,
        hovertemplate="%{x}<br>best Sharpe=%{y:.3f}<br>valid combos=%{customdata}<extra></extra>",
    ))
    # B&H reference line
    fig.add_trace(go.Scatter(
        x=xlab, y=[bh] * len(xlab), mode="lines",
        name=f"Buy & Hold {tgt} ({bh:.2f})",
        line={"color": BENCH, "dash": "dash", "width": 2}, hoverinfo="skip",
    ))
    fig.add_annotation(x=xlab[imax], y=max_val, text=f"<b>max L{max_lead}</b><br>{max_val:.2f}",
                       showarrow=True, arrowhead=2, ax=0, ay=-30, font={"size": 10})

    rr = " (gating-sweep view; L7-12 peak re-run in Track B)" if pair in RERUN_FLAG else ""
    title = (f"Lead vs OOS Sharpe: {ind} -> {tgt} (L = 0..12){rr}"
             f"<br><sub>Bars: best OOS Sharpe at each lead. Grey band/dots: "
             f"p25-p75 & median of valid combos. Dashed: {tgt} buy-and-hold. {cap}</sub>")
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={"title": {"text": "Lead (months) applied to signal"}},
        yaxis={"title": {"text": "OOS Sharpe ratio"}, "zeroline": True},
        template="plotly_white", barmode="overlay",
        legend={"orientation": "h", "y": -0.18},
        margin={"l": 70, "r": 40, "t": 95, "b": 90},
        annotations=[a for a in []],
    )
    fig.add_annotation(text="Source: Evan ECON-LT1 fine-grid lead tournament.",
                       showarrow=False, xref="paper", yref="paper",
                       x=0, y=-0.30, font={"size": 10, "color": "#666"}, align="left")
    return fig, cap


def write_meta(pair, chart_name, method_name, expected, caption, rules):
    meta = {
        "chart_name": chart_name,
        "pair_id": pair,
        "palette_id": "okabe_ito_2026",
        "rules_applied": rules,
        "narrative_alignment_note": caption,
        "caption": caption,
        "created_at": CREATED,
        "method_name": method_name,
        "expected_chart_type": expected,
        "disposition": "consumed",
    }
    out = ROOT / f"output/charts/{pair}/plotly/{chart_name}_meta.json"
    out.write_text(json.dumps(meta, indent=2) + "\n")


def main():
    for pair, (ind, tgt, bh) in PAIRS.items():
        d = ROOT / f"output/charts/{pair}/plotly"
        d.mkdir(parents=True, exist_ok=True)

        f1, c1 = build_corr_chart(pair, ind, tgt)
        (d / "correlations_lead_view.json").write_text(pio.to_json(f1))
        write_meta(pair, "correlations_lead_view", "Lead Analysis", "heatmap", c1,
                   ["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"])
        f1.write_image(str(d / "_perceptual_check_correlations_lead_view.png"),
                       width=1100, height=600, scale=2)

        f2, c2 = build_sharpe_chart(pair, ind, tgt, bh)
        (d / "lead_sharpe_distribution.json").write_text(pio.to_json(f2))
        write_meta(pair, "lead_sharpe_distribution", "Lead Tournament", "bar", c2,
                   ["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"])
        f2.write_image(str(d / "_perceptual_check_lead_sharpe_distribution.png"),
                       width=1100, height=600, scale=2)

        print(f"[{pair}] OK")
        print(f"    corr:   {c1}")
        print(f"    sharpe: {c2}")


if __name__ == "__main__":
    main()
