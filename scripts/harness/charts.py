"""Shared two-track charts (app design sections 6, 8): lead plateau chart and chance-check histogram.

Written to output/charts/<pair>/plotly/{lead_plateau,chance_check}.json with the usual _meta.json sidecar.
Okabe-Ito palette: as known at the time #0072B2 (solid, circles), as revised today #D55E00 (dashed, squares,
hidden by default), stable lead range band #56B4E9 alpha 0.25, null histogram #999999.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

REPO = Path(__file__).resolve().parents[2]
C_MAIN, C_REV, C_BAND, C_NULL, C_TEXT = "#0072B2", "#D55E00", "#56B4E9", "#999999", "#222222"
LABEL = {"real_time": "As known at the time", "revised": "As revised today (hindsight)", "market": "Market data"}
UNIT_WORD = {"months": "months", "quarters": "quarters", "days": "trading days"}


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _save(pair: str, name: str, fig: go.Figure, caption: str, sources: list[str]) -> Path:
    out = REPO / "output" / "charts" / pair / "plotly"
    out.mkdir(parents=True, exist_ok=True)
    fig.write_json(out / f"{name}.json")
    meta = {"chart_name": name, "pair_id": pair, "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "scripts/harness/charts.py", "caption": caption, "narrative_alignment_note": caption,
            "disposition": "consumed", "source_artifacts": sources}
    (out / f"{name}_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    try:                                    # perceptual-check PNG (GATE-27); kaleido needs a Chromium (BROWSER_PATH)
        fig.write_image(out / f"_perceptual_check_{name}.png", width=1200, height=600)
    except Exception as e:                  # noqa: BLE001 - no renderer: say so, never write an empty file
        print(f"  (perceptual PNG skipped for {name}: {type(e).__name__})")
    return out / f"{name}.json"


def lead_plateau(pair: str, tag: str, lead_unit: str) -> str | None:
    """Score (training-period Sharpe) vs lead for the MAIN winner's rule, plateau band, winner diamond, open
    triangle for an off-plateau maximum; the hindsight curve is a legend-toggle trace. Returns the caption."""
    rdir = REPO / "results" / pair
    main = pd.read_csv(rdir / f"lead_curve_{tag}.csv")
    if main.empty:
        return None
    lc = [c for c in main.columns if c.startswith("lead_")][0]
    hind_p = rdir / f"hindsight_lead_curve_{tag}.csv"
    hind = pd.read_csv(hind_p) if hind_p.exists() else None
    track = main["track"].iloc[0]
    leads = main[lc].astype(int).tolist()
    band = main.loc[main["in_plateau"], lc].astype(int).tolist()
    w = main.loc[main["winner"]].iloc[0]
    wl = int(w[lc])
    fig = go.Figure()
    pos = {L: i for i, L in enumerate(leads)}
    if band:
        fig.add_vrect(x0=pos[min(band)] - 0.4, x1=pos[max(band)] + 0.4, fillcolor=C_BAND, opacity=0.25, line_width=0,
                      layer="below")
        fig.add_annotation(x=(pos[min(band)] + pos[max(band)]) / 2, y=1.0, yref="paper", yanchor="bottom",
                           text=f"Stable lead range ({len(band)} leads)", showarrow=False, font=dict(color=C_TEXT))
    x = [pos[L] for L in leads]
    hover = [f"Lead {L}<br>Score {s:.2f}<br>Inside stable lead range: {'yes' if p else 'no'}"
             for L, s, p in zip(leads, main["is_sharpe"], main["in_plateau"])]
    fig.add_trace(go.Scatter(x=x, y=main["is_sharpe"], mode="lines+markers", name=LABEL.get(track, track),
                             line=dict(color=C_MAIN, width=2), marker=dict(symbol="circle", size=8),
                             hovertext=hover, hoverinfo="text"))
    if hind is not None and not hind.empty:
        hl = hind[[c for c in hind.columns if c.startswith("lead_")][0]].astype(int)
        fig.add_trace(go.Scatter(x=[pos.get(L, np.nan) for L in hl], y=hind["is_sharpe"], mode="lines+markers",
                                 name=LABEL["revised"], line=dict(color=C_REV, width=2, dash="dash"),
                                 marker=dict(symbol="square", size=7), visible="legendonly",
                                 hovertext=[f"Lead {L}<br>Score {s:.2f} (hindsight)" for L, s in zip(hl, hind["is_sharpe"])],
                                 hoverinfo="text"))
    fig.add_trace(go.Scatter(x=[pos[wl]], y=[w["is_sharpe"]], mode="markers", name=f"Winner L{wl}",
                             marker=dict(symbol="diamond-dot", size=16, color="white", line=dict(color=C_TEXT, width=2)),
                             hoverinfo="skip"))
    fig.add_annotation(x=pos[wl], y=w["is_sharpe"], text=f"Winner L{wl}", showarrow=True, arrowcolor=C_TEXT,
                       ax=0, ay=42, font=dict(color=C_TEXT), bgcolor="white")
    gmax = main.loc[main["is_sharpe"].idxmax()]
    gl = int(gmax[lc])
    off = gl not in band
    if off:
        fig.add_trace(go.Scatter(x=[pos[gl]], y=[gmax["is_sharpe"]], mode="markers",
                                 name="Highest single lead (not chosen)",
                                 marker=dict(symbol="triangle-up-open", size=14, color=C_TEXT), hoverinfo="skip"))
        fig.add_annotation(x=pos[gl], y=gmax["is_sharpe"], text="Highest single lead (not chosen)", showarrow=True,
                           arrowcolor=C_TEXT, ax=0, ay=-34, font=dict(color=C_TEXT), bgcolor="white")
    unit = UNIT_WORD.get(lead_unit, lead_unit)
    ys = pd.concat([main["is_sharpe"]] + ([hind["is_sharpe"]] if hind is not None and not hind.empty else [])).dropna()
    span = float(ys.max() - ys.min()) or 0.1
    fig.update_yaxes(range=[float(ys.min()) - 0.35 * span, float(ys.max()) + 0.3 * span])
    fig.update_layout(template="plotly_white", height=430, title="Lead robustness: training-period Sharpe by lead",
                      xaxis=dict(title=f"Lead ({unit})", tickmode="array", tickvals=x, ticktext=[f"L{L}" for L in leads]),
                      yaxis=dict(title="Score (training-period Sharpe)"), legend=dict(orientation="h", y=-0.2))
    rng = f"L{min(band)}-L{max(band)}" if band else f"L{wl}"
    if band and band != list(range(min(band), max(band) + 1)):
        rng += f" (adjacent grid points {', '.join(str(x) for x in band)} {unit})"
    cap = f"The winner L{wl} sits in a stable range {rng}."
    if off:
        cap += f" The highest single point, L{gl}, was not chosen because its neighbours score lower."
    _save(pair, "lead_plateau", fig, cap, [f"results/{pair}/lead_curve_{tag}.csv"]
          + ([f"results/{pair}/hindsight_lead_curve_{tag}.csv"] if hind is not None else []))
    return cap


def chance_check(pair: str, tag: str) -> str | None:
    """Histogram of null plateau scores with the real winner's score (design section 8)."""
    rdir = REPO / "results" / pair
    p = rdir / f"null_tournament_{tag}.csv"
    ts = json.loads((rdir / "track_summary.json").read_text())
    if not p.exists() or not ts.get("null_tournament") or not ts.get("plateau"):
        return None
    nd = pd.read_csv(p)
    real = ts["plateau"]["score"]
    pct = ts["null_tournament"]["winner_percentile"]
    fig = go.Figure(go.Histogram(x=nd["selection_stat"].dropna(), marker_color=C_NULL, nbinsx=20,
                                 name="Scrambled-signal contests"))
    fig.add_vline(x=real, line_color=C_REV, line_width=3,
                  annotation_text="Real winner's plateau score (the statistic the null compares)",
                  annotation_position="top")
    q95 = float(np.nanpercentile(nd["selection_stat"], 95))
    fig.add_vline(x=q95, line_color=C_TEXT, line_width=1, line_dash="dot", annotation_text="95th",
                  annotation_position="top right")
    k = int(nd["selection_stat"].notna().sum())
    if pct is None:
        cap = "Chance check not yet run for this pair."
    elif pct >= 1:
        cap = f"The real winner's plateau score is above all {k:,} scrambled-signal contests."
    else:
        cap = (f"The real winner's plateau score ranks at the {ordinal(round(pct * 100))} percentile of {k:,} "
               "scrambled-signal contests.")
    fig.update_layout(template="plotly_white", height=380, title="Chance check: real winner vs scrambled signals",
                      xaxis_title="Best score in a contest (training-period Sharpe, stable lead range)",
                      yaxis_title="Number of contests", showlegend=False)
    _save(pair, "chance_check", fig, cap, [f"results/{pair}/null_tournament_{tag}.csv", f"results/{pair}/track_summary.json"])
    return cap
