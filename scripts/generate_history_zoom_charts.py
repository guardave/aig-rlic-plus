"""
VIZ-HZE1 Retro-Apply: Generate history_zoom_*.json charts for 8 pairs.
Vera - Visualization Agent

History
-------
- Originally lived as a one-shot under `temp/generate_history_zoom_charts.py`
  during the Wave 10H.1 backfill. Promoted to `scripts/` on 2026-05-31 as
  part of the fix260531 cross-pair legend/caption layout fix so the
  generator's source is tracked in git.
- 2026-05-31 layout-overlap fix (fix260531): legend.y -0.05 -> -0.18,
  caption annotation y -0.12 -> -0.32, margin.b 60 -> 120. The previous
  values placed the horizontal legend and the bottom source-note
  annotation in the same ~10 px strip, causing visible overlap on
  Streamlit Cloud. See BL-VIZ-LO1 and the relnote entry for 2026-05-31.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np

# ── NBER recession periods (start, end) ──────────────────────────────────────
NBER_RECESSIONS = [
    ("1990-07-01", "1991-03-01"),
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-30"),
]

# ── Palette (Okabe-Ito 2026) ─────────────────────────────────────────────────
PALETTE = {
    "indicator": "#0072B2",   # blue
    "target":    "#D55E00",   # orange
    "recession": "rgba(150,120,120,0.22)",
}

# ── Events registry (canonical, keyed by slug) ───────────────────────────────
# Map episode_registry slugs → events_registry slugs
EVENTS_MAP = {
    "dot_com":    "dotcom",
    "gfc":        "gfc",
    "covid":      "covid",
    "taper_2013": None,          # no canonical events for this slug
    "china_2015": None,          # no canonical events
    "rates_2022": "inflation_2022",
}

# ── Pair configuration ───────────────────────────────────────────────────────
PAIR_CONFIG = {
    "dff_ted_spy": {
        "data_file": "data/dff_ted_spy_daily_20260314.parquet",
        "indicator_col": "dff",
        "indicator_label": "Fed Funds Rate (%)",
        "target_col": "spy",
        "target_label": "SPY Price ($)",
        "target_symbol": "SPY",
        "indicator_category": "rates",
        "slugs": ["dot_com", "gfc", "taper_2013", "rates_2022"],
        "episode_category": "rates",
    },
    "sofr_ted_spy": {
        "data_file": "data/sofr_ted_spy_daily_20260314.parquet",
        "indicator_col": "sofr",
        "indicator_label": "SOFR (%)",
        "target_col": "spy",
        "target_label": "SPY Price ($)",
        "target_symbol": "SPY",
        "indicator_category": "rates",
        "slugs": ["dot_com", "gfc", "taper_2013", "rates_2022"],
        "episode_category": "rates",
    },
    "ted_spliced_spy": {
        "data_file": "data/ted_spliced_spy_daily_20260314.parquet",
        "indicator_col": "tedrate",
        "indicator_label": "TED Spread (%)",
        "target_col": "spy",
        "target_label": "SPY Price ($)",
        "target_symbol": "SPY",
        "indicator_category": "credit",
        "slugs": ["dot_com", "gfc", "covid", "rates_2022"],
        "episode_category": "credit",
    },
    "indpro_spy": {
        "data_file": "data/indpro_spy_daily_19900101_20251231.parquet",
        "indicator_col": "indpro",
        "indicator_label": "INDPRO Index",
        "target_col": "spy",
        "target_label": "SPY Price ($)",
        "target_symbol": "SPY",
        "indicator_category": "production",
        "slugs": ["dot_com", "gfc", "covid", "china_2015"],
        "episode_category": "production",
    },
    "indpro_xlp": {
        "data_file": "data/indpro_xlp_daily_19980101_20251231.parquet",
        "indicator_col": "indpro",
        "indicator_label": "INDPRO Index",
        "target_col": "xlp",
        "target_label": "XLP Price ($)",
        "target_symbol": "XLP",
        "indicator_category": "production",
        "slugs": ["dot_com", "gfc", "covid", "china_2015"],
        "episode_category": "production",
    },
    "permit_spy": {
        "data_file": "data/permit_spy_monthly_20260314.parquet",
        "indicator_col": "permit",
        "indicator_label": "Building Permits (000s)",
        "target_col": "spy",
        "target_label": "SPY Price ($)",
        "target_symbol": "SPY",
        "indicator_category": "production",
        "slugs": ["dot_com", "gfc", "covid", "china_2015"],
        "episode_category": "production",
    },
    "umcsent_xlv": {
        "data_file": "data/umcsent_xlv_monthly_19980101_20251231.parquet",
        "indicator_col": "umcsent",
        "indicator_label": "UMich Consumer Sentiment",
        "target_col": "xlv",
        "target_label": "XLV Price ($)",
        "target_symbol": "XLV",
        "indicator_category": "sentiment",
        "slugs": ["dot_com", "gfc", "covid", "rates_2022"],
        "episode_category": "sentiment",
    },
    "vix_vix3m_spy": {
        "data_file": "data/vix_vix3m_spy_daily_20260314.parquet",
        "indicator_col": "vix_ratio",
        "indicator_label": "VIX/VIX3M Ratio",
        "target_col": "spy",
        "target_label": "SPY Price ($)",
        "target_symbol": "SPY",
        "indicator_category": "volatility",
        "slugs": ["dot_com", "gfc", "covid", "rates_2022"],
        "episode_category": "volatility",
    },
}

# ── Episode date ranges ───────────────────────────────────────────────────────
EPISODE_RANGES = {
    "dot_com":    ("2000-03-01", "2002-10-31"),
    "gfc":        ("2007-12-01", "2009-06-30"),
    "taper_2013": ("2013-05-01", "2013-12-31"),
    "covid":      ("2020-02-01", "2020-12-31"),
    "china_2015": ("2015-06-01", "2016-02-29"),
    "rates_2022": ("2022-01-01", "2022-12-31"),
}

EPISODE_LABELS = {
    "dot_com":    "Dot-Com Crash (2000–2002)",
    "gfc":        "Global Financial Crisis (2007–2009)",
    "taper_2013": "Taper Tantrum (2013)",
    "covid":      "COVID-19 Shock (2020)",
    "china_2015": "China/EM Shock (2015–2016)",
    "rates_2022": "2022 Rates Shock",
}

CONTEXT_MONTHS = 3   # padding on each side


def load_events_registry(base_path: str) -> dict:
    path = os.path.join(base_path, "docs/schemas/history_zoom_events_registry.json")
    with open(path) as f:
        return json.load(f)


def get_episode_events(events_registry: dict, episode_slug: str) -> list:
    """Return list of event dicts for a given episode slug."""
    mapped = EVENTS_MAP.get(episode_slug)
    if mapped is None:
        return []
    ep = events_registry.get("episodes", {}).get(mapped, {})
    return ep.get("key_events", [])


def recession_shapes_for_window(x0_str: str, x1_str: str) -> list:
    """Return NBER recession shapes that overlap the window, for both yaxis/yaxis2."""
    x0 = pd.Timestamp(x0_str)
    x1 = pd.Timestamp(x1_str)
    shapes = []
    for r0_str, r1_str in NBER_RECESSIONS:
        r0 = pd.Timestamp(r0_str)
        r1 = pd.Timestamp(r1_str)
        if r1 < x0 or r0 > x1:
            continue
        clipped_r0 = max(r0, x0)
        clipped_r1 = min(r1, x1)
        for (xref, yref) in [("x", "y domain"), ("x2", "y2 domain")]:
            shapes.append({
                "fillcolor": PALETTE["recession"],
                "layer": "below",
                "line": {"width": 0},
                "type": "rect",
                "x0": clipped_r0.strftime("%Y-%m-%dT%H:%M:%S"),
                "x1": clipped_r1.strftime("%Y-%m-%dT%H:%M:%S"),
                "xref": xref,
                "y0": 0,
                "y1": 1,
                "yref": yref,
            })
    return shapes


def build_event_annotations(events: list, df_window: pd.DataFrame,
                             indicator_col: str) -> list:
    """Build up to 5 event marker annotations on the indicator panel (yref=y)."""
    annotations = []
    for ev in events[:5]:
        ev_date = pd.Timestamp(ev["date"])
        # Find closest date in window
        if ev_date < df_window.index.min() or ev_date > df_window.index.max():
            continue
        # Find y value
        closest_idx = df_window.index.get_indexer([ev_date], method="nearest")[0]
        y_val = float(df_window[indicator_col].iloc[closest_idx])
        annotations.append({
            "x": ev_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "xref": "x",
            "y": y_val,
            "yref": "y",
            "text": ev["label"][:35],   # truncate for space
            "showarrow": True,
            "arrowhead": 2,
            "arrowsize": 0.7,
            "ax": 0,
            "ay": -35,
            "font": {"size": 8, "color": "#4D4D4D"},
            "bgcolor": "rgba(255,255,255,0.82)",
            "borderpad": 2,
        })
    return annotations


def build_chart(pair_id: str, slug: str, cfg: dict, df: pd.DataFrame,
                events_registry: dict, base_path: str):
    ep_start_str, ep_end_str = EPISODE_RANGES[slug]
    ep_start = pd.Timestamp(ep_start_str)
    ep_end = pd.Timestamp(ep_end_str)

    # Window = episode ± 3 months
    win_start = ep_start - relativedelta(months=CONTEXT_MONTHS)
    win_end = ep_end + relativedelta(months=CONTEXT_MONTHS)

    df_win = df.loc[(df.index >= win_start) & (df.index <= win_end)].copy()

    indicator_col = cfg["indicator_col"]
    target_col = cfg["target_col"]

    # Check data availability: must have >5 non-null rows in episode proper
    # (Monthly series can have as few as 9 observations in a 9-month episode)
    ep_mask = (df.index >= ep_start) & (df.index <= ep_end)
    if df.loc[ep_mask, indicator_col].dropna().shape[0] < 5:
        return None, f"Insufficient data in episode window ({df.loc[ep_mask, indicator_col].dropna().shape[0]} rows)"

    xs = [d.strftime("%Y-%m-%dT%H:%M:%S") for d in df_win.index]
    y_ind = df_win[indicator_col].tolist()
    y_tgt = df_win[target_col].tolist() if target_col in df_win.columns else []

    # Panel titles
    ind_label = cfg["indicator_label"]
    tgt_label = cfg["target_label"]
    ep_label = EPISODE_LABELS[slug]
    pair_upper = pair_id.upper().replace("_", " → ")
    chart_title = f"{ep_label}: {ind_label} vs {cfg['target_symbol']} ({ep_start.year}–{ep_end.year})"

    # Traces
    ind_trace = {
        "name": ind_label,
        "type": "scatter",
        "x": xs,
        "y": y_ind,
        "mode": "lines",
        "line": {"color": PALETTE["indicator"], "width": 1.5},
        "yaxis": "y",
        "hovertemplate": "%{x|%Y-%m-%d}<br>" + ind_label + ": %{y:.3f}<extra></extra>",
    }
    tgt_trace = {
        "name": tgt_label,
        "type": "scatter",
        "x": xs,
        "y": y_tgt,
        "mode": "lines",
        "line": {"color": PALETTE["target"], "width": 1.5},
        "yaxis": "y2",
        "hovertemplate": "%{x|%Y-%m-%d}<br>" + tgt_label + ": %{y:.2f}<extra></extra>",
    }

    # Recession shapes
    shapes = recession_shapes_for_window(
        win_start.strftime("%Y-%m-%d"), win_end.strftime("%Y-%m-%d")
    )

    # Event annotations on indicator panel
    events = get_episode_events(events_registry, slug)
    ev_annotations = build_event_annotations(events, df_win, indicator_col)

    # Fixed layout annotations (panel titles + source note)
    layout_annotations = [
        {
            "text": ind_label,
            "x": 0.5, "xref": "paper", "xanchor": "center",
            "y": 1.0, "yref": "paper", "yanchor": "bottom",
            "showarrow": False, "font": {"size": 16},
        },
        {
            "text": tgt_label,
            "x": 0.5, "xref": "paper", "xanchor": "center",
            "y": 0.38, "yref": "paper", "yanchor": "bottom",
            "showarrow": False, "font": {"size": 16},
        },
        {
            "text": f"Zoom: {ep_label}. Source: FRED / Yahoo Finance. Gray = NBER recession.",
            "x": 0, "xref": "paper", "xanchor": "left",
            "y": -0.32, "yref": "paper",
            "showarrow": False, "font": {"size": 9, "color": "#888888"},
        },
    ] + ev_annotations

    layout = {
        "title": {"text": chart_title},
        "xaxis": {
            "anchor": "y",
            "domain": [0.0, 1.0],
            "matches": "x2",
            "showticklabels": False,
        },
        "yaxis": {
            "anchor": "x",
            "domain": [0.43, 1.0],
            "title": {"text": ind_label},
        },
        "xaxis2": {
            "anchor": "y2",
            "domain": [0.0, 1.0],
        },
        "yaxis2": {
            "anchor": "x2",
            "domain": [0.0, 0.38],
            "title": {"text": tgt_label},
        },
        "shapes": shapes,
        "annotations": layout_annotations,
        "legend": {"orientation": "h", "x": 0, "y": -0.18},
        "height": 500,
        "hovermode": "x unified",
        "margin": {"l": 60, "r": 20, "t": 60, "b": 120},
    }

    return {"data": [ind_trace, tgt_trace], "layout": layout}, None


def build_meta(pair_id: str, slug: str, skipped: bool = False,
               skip_reason: str = None) -> dict:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    if skipped:
        return {
            "chart_name": f"history_zoom_{slug}",
            "pair_id": pair_id,
            "disposition": "skipped",
            "skip_reason": skip_reason,
            "viz_hze1_applied": True,
            "created_at": now,
        }
    return {
        "chart_name": f"history_zoom_{slug}",
        "pair_id": pair_id,
        "palette_id": "okabe_ito_2026",
        "rules_applied": ["VIZ-V1", "VIZ-HZE1", "VIZ-NBER1", "VIZ-V12"],
        "narrative_alignment_note": f"Episode zoom ({EPISODE_LABELS.get(slug, slug)}) shows indicator vs target relationship.",
        "created_at": now,
        "method_name": "History Zoom",
        "expected_chart_type": "dual_panel_line",
        "disposition": "consumed",
    }


def main():
    base_path = "/workspaces/aig-rlic-plus"
    events_registry = load_events_registry(base_path)

    results = {}

    for pair_id, cfg in PAIR_CONFIG.items():
        data_path = os.path.join(base_path, cfg["data_file"])
        df = pd.read_parquet(data_path)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        out_dir = os.path.join(base_path, "output/charts", pair_id, "plotly")
        os.makedirs(out_dir, exist_ok=True)

        pair_results = {"generated": [], "skipped": []}

        for slug in cfg["slugs"]:
            chart_path = os.path.join(out_dir, f"history_zoom_{slug}.json")
            meta_path = os.path.join(out_dir, f"history_zoom_{slug}_meta.json")

            chart, skip_reason = build_chart(pair_id, slug, cfg, df, events_registry, base_path)

            if chart is None:
                # Skip
                meta = build_meta(pair_id, slug, skipped=True, skip_reason=skip_reason)
                with open(meta_path, "w") as f:
                    json.dump(meta, f, indent=2)
                pair_results["skipped"].append({"slug": slug, "reason": skip_reason})
                print(f"  SKIP  {pair_id}/{slug}: {skip_reason}")
            else:
                with open(chart_path, "w") as f:
                    json.dump(chart, f, indent=2)
                meta = build_meta(pair_id, slug)
                with open(meta_path, "w") as f:
                    json.dump(meta, f, indent=2)
                pair_results["generated"].append(slug)
                print(f"  GEN   {pair_id}/{slug}: OK")

        results[pair_id] = pair_results

    print("\n=== VIZ-HZE1 Gate Check ===")
    for pair_id, pr in results.items():
        gen = pr["generated"]
        skipped = pr["skipped"]
        print(f"\n{pair_id}:")
        print(f"  Generated: {gen}")
        print(f"  Skipped:   {[(s['slug'], s['reason']) for s in skipped]}")
        # Gate: all non-skipped slugs must have chart on disk
        gate_pass = True
        for slug in gen:
            path = f"{base_path}/output/charts/{pair_id}/plotly/history_zoom_{slug}.json"
            if not os.path.exists(path):
                print(f"  GATE FAIL: {slug} not found on disk!")
                gate_pass = False
        print(f"  VIZ-HZE1 gate: {'PASS' if gate_pass else 'FAIL'}")


if __name__ == "__main__":
    main()
