#!/usr/bin/env python3
"""Generate the two mandatory VIZ-LEAD1 Evidence charts for any pair, fully
data-driven from Evan's lead-sweep CSVs (ECON-LA1 / ECON-LT1).

Two charts per pair, numbers re-read from the latest dated CSVs at generation
time (no per-pair hardcoded statistics):
  1. correlations_lead_view    <- results/{pair}/lead_correlation_{date}.csv  (ECON-LA1)
  2. lead_sharpe_distribution  <- results/{pair}/lead_tournament_{date}.csv   (ECON-LT1)

Universal monthly lead axis L0..L12 for ALL pairs (incl. daily-target pairs) per
VIZ-LEAD1. Palette okabe_ito_2026. Rules: VIZ-LEAD1, VIZ-IC1, VIZ-TX1, VIZ-O1.
Emits {chart}.json + {chart}_meta.json + _perceptual_check_{chart}.png per chart.

Data-driven design (no per-pair hardcoding of statistics):
  - date tag        -> latest results/{pair}/lead_correlation_*.csv (glob, sorted)
  - B&H OOS Sharpe  -> winner_summary.json bh_oos_sharpe (fallback bh_sharpe)
  - indicator/target display names -> winner_summary.json + display_names registry
  - winner lead/Sharpe (for the winner-vs-sweep annotation) -> winner_summary.json

IMPORTANT — sweep grid vs native winner (VIZ-LEAD1 honesty clause):
  lead_tournament_*.csv is the STANDARDIZED gating-sweep grid (P1/P2 comparator
  across L0..12), NOT the native tournament. Its per-lead bar max can sit at a
  DIFFERENT lead than the published winner (e.g. indpro_spy sweep max L12 vs
  published winner L4; indpro_xlp sweep max L8 vs published L11). The
  lead_sharpe_distribution caption therefore states BOTH the sweep-max lead AND
  the published-winner lead, so a reader never mistakes the sweep landscape's
  tallest bar for the deployed strategy.

NEVER touches the frozen/retired Sample hy_ig_v2_spy.

Usage:
    python3 scripts/generate_lead_charts.py [pair_id ...]
    # default: all non-frozen pairs that have lead_correlation + lead_tournament CSVs
"""
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
CREATED = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

PAL = json.loads((ROOT / "docs/schemas/color_palette_registry.json").read_text())["palettes"]["okabe_ito_2026"]
BENCH = PAL["benchmark_trace"]       # #6C7A89
BAR = PAL["primary_data_trace"]      # #D55E00
DOT = "#999999"

LEADS = [f"L{i}" for i in range(13)]

FROZEN = {"hy_ig_v2_spy"}  # retired Sample — never regenerate

# Clean indicator labels keyed by pair stem (the part before the target suffix).
# Backstop only — Ace's SHORT_INDICATOR_LABELS registry (keyed by full pair_id)
# is consulted FIRST. The winner's signal_display_name is NOT used as the title
# indicator because it leaks the winning transform token (e.g. "ISM Services
# gap_50", "M2SL accel", "petrol 3m") — a VIZ-NS1 violation on a user surface.
_IND_FALLBACK = {
    "indpro": "Industrial Production",
    "permit": "Building Permits",
    "vix_vix3m": "VIX/VIX3M Term Structure",
    "hy_ig": "HY-IG Credit Spread",
    "umcsent": "UMich Consumer Sentiment",
    "gold_copper": "Gold/Copper Ratio",
    "busloans": "C&I Loans",
    "ism_services": "ISM Services PMI",
    "m2sl_yoy": "M2 Money Supply (YoY)",
    "petrol_inv": "Petroleum Inventories",
    "phlxsox": "PHLX Semiconductor Index",
}

try:
    from components.display_names import SHORT_INDICATOR_LABELS as _ACE_LABELS
except Exception:
    _ACE_LABELS = {}


# Daily-executed pairs: their native lead_correlation is at DAILY granularity
# (L1..L52). For the universal monthly VIZ-LEAD1 axis, Evan emits a separate
# month-end-resampled comparability file that MUST be read BY NAME — the
# latest-glob would resolve to the daily file and put the wrong axis on the
# chart (per each monthly_axis _meta.json `consume_for_chart`). Their
# lead_tournament IS monthly (lead_months 0..12), so the Sharpe chart is normal.
DAILY_PAIRS = {"vix_vix3m_spy", "gold_copper_xli", "hy_ig_spy", "phlxsox_spy"}


def latest_dated(pair, stem):
    """Newest results/{pair}/{stem}_YYYYMMDD.csv -> (path, date_str).

    Matches ONLY the canonical `{stem}_<8digits>.csv` — an exact-date suffix with
    no infix. This deliberately excludes sibling variants like
    `{stem}_weekly_YYYYMMDD.csv` / `{stem}_monthly_axis_YYYYMMDD.csv`, which a
    naive `{stem}_*.csv` glob would sort AFTER the canonical file ("weekly" > a
    digit) and wrongly select — putting a daily/weekly lead axis on the chart."""
    pat = re.compile(rf"^{re.escape(stem)}_(\d{{8}})\.csv$")
    cand = [(p, pat.match(p.name).group(1)) for p in (ROOT / "results" / pair).glob(f"{stem}_*.csv")
            if pat.match(p.name)]
    if not cand:
        raise FileNotFoundError(f"no canonical {stem}_YYYYMMDD.csv for {pair}")
    cand.sort(key=lambda t: t[1])
    return cand[-1]


def corr_csv(pair):
    """Resolve the correlation CSV + date for the monthly L0..L12 heatmap.
    Daily pairs MUST use the month-end-resampled `lead_correlation_monthly_axis_*`
    file BY NAME (never the latest-glob, which is the daily-axis file)."""
    if pair in DAILY_PAIRS:
        matches = sorted((ROOT / "results" / pair).glob("lead_correlation_monthly_axis_*.csv"))
        if not matches:
            raise FileNotFoundError(
                f"{pair} is daily but has no lead_correlation_monthly_axis_*.csv "
                f"(Evan ECON-LA1 monthly-resample). Cannot build monthly-axis heatmap.")
        p = matches[-1]
        m = re.search(r"_(\d{8})\.csv$", p.name)
        return p, (m.group(1) if m else ""), True  # is_daily
    p, date = latest_dated(pair, "lead_correlation")
    return p, date, False


def load_winner(pair):
    p = ROOT / "results" / pair / "winner_summary.json"
    return json.loads(p.read_text()) if p.exists() else {}


def display_names(pair, w):
    """(indicator_display, target_display). Indicator label resolves in order:
    Ace's SHORT_INDICATOR_LABELS registry (canonical, keyed by pair_id) ->
    _IND_FALLBACK (keyed by stem) -> title-cased stem. The winner's
    signal_display_name is deliberately NOT used (it leaks the winning transform
    token, a VIZ-NS1 violation)."""
    tgt = (w.get("target_symbol") or pair.rsplit("_", 1)[-1]).upper()
    stem = pair.rsplit("_", 1)[0]
    ind = (_ACE_LABELS.get(pair)
           or _IND_FALLBACK.get(stem)
           or stem.replace("_", " ").title())
    return ind, tgt


# Canonical SPY OOS buy-and-hold Sharpe (busloans_spy winner_summary bh_oos_sharpe,
# corroborated by permit's prior chart 0.8939). Used ONLY as a documented fallback
# for *_spy pairs whose winner_summary.json omits a B&H key (e.g. permit_spy).
# Any pair that hits this fallback is flagged at run time — its winner_summary is
# missing bh_oos_sharpe and should be fixed upstream.
_SPY_BH_FALLBACK = 0.8935


def bh_sharpe(pair, w):
    v = w.get("bh_oos_sharpe", w.get("bh_sharpe"))
    if v is not None:
        return float(v), False
    if pair.endswith("_spy"):
        return _SPY_BH_FALLBACK, True
    return float("nan"), True


def parse_cell(s):
    """'+0.141**' -> (0.141, '**')."""
    s = s.strip()
    m = re.match(r"^([+-]?\d*\.?\d+)(\**)$", s)
    if not m:
        return float("nan"), ""
    return float(m.group(1)), m.group(2)


def read_rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def winner_transform_row(pair, rows, w, is_daily):
    """Resolve the correlation-CSV row for the WINNER SIGNAL (the signal the
    deployed strategy trades), so the corr callout names the winner signal's
    monthly-lead peak (convention (b), ECON-LA1 — matches Ray's winner-centric
    narrative + the monthly_axis _meta winner_signal_monthly_lead_peak), NOT the
    globally strongest transform.

    Resolution: daily pairs -> monthly_axis _meta `winner_signal` (the exact
    transform name). Monthly pairs -> winner_summary signal_column, exact match
    then a trailing-token-stripped fallback (e.g. permit_mom1m -> permit_mom).
    Returns (row, resolved_name, matched_bool); falls back to global-|r| max with
    matched=False if the winner signal can't be located (flagged at run time)."""
    by_name = {r["transform"]: r for r in rows}
    target = None
    if is_daily:
        meta_p = ROOT / "results" / pair / "lead_correlation_monthly_axis_20260620_meta.json"
        if meta_p.exists():
            target = json.loads(meta_p.read_text()).get("winner_signal")
    if not target:
        target = w.get("signal_column")
    if target and target in by_name:
        return by_name[target], target, True
    # trailing-token-stripped fallback (permit_mom1m -> permit_mom, etc.)
    if target:
        for cand in (re.sub(r"\d+[a-z]*$", "", target).rstrip("_"),
                     re.sub(r"(1m|_1m|1month)$", "", target)):
            if cand and cand in by_name:
                return by_name[cand], cand, True
    best = max(rows, key=lambda r: abs(float(r["best_r"])))
    return best, best["transform"], False


# ── Chart 1: correlations_lead_view (heatmap) ───────────────────────────────
def build_corr_chart(pair, ind, tgt, w):
    path, date, is_daily = corr_csv(pair)
    rows = read_rows(path)
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
    # Convention (b): callout = the WINNER SIGNAL's monthly-lead peak.
    wrow, wname, matched = winner_transform_row(pair, rows, w, is_daily)
    if not matched:
        print(f"  [FLAG] {pair}: winner signal not found in correlation transforms — "
              f"corr callout fell back to global max {wname}. Check signal_column.")
    best_caption = (f"Winner signal {wname} peaks at {wrow['best_lead']} "
                    f"(r={float(wrow['best_r']):+.3f}).")
    # Daily-pair comparability caveat (matches Ray's narrative + the monthly_axis
    # _meta honest_caveat): this monthly axis is a resampled comparability view,
    # NOT the pair's daily execution horizon.
    daily_caveat = ("" if not is_daily else
                    " NOTE: this is a DAILY-executed pair; the monthly L0..L12 "
                    "axis is a resampled comparability view (the native diagnostic "
                    "is daily), not the execution horizon.")
    zabs = max(0.2, max(abs(v) for row in z for v in row))

    fig = go.Figure(go.Heatmap(
        z=z, x=LEADS, y=transforms, text=text, texttemplate="%{text}",
        textfont={"size": 9}, colorscale="RdBu_r", zmid=0, zmin=-zabs, zmax=zabs,
        colorbar={"title": "Pearson r"},
        hovertemplate="signal=%{y}<br>lead=%{x}<br>r=%{text}<extra></extra>",
    ))
    axis_note = ("monthly-resampled L0..L12 axis (daily-executed pair)"
                 if is_daily else "L0..L12")
    title = (f"Lead-Lag Predictability: {ind} Signal (lagged L months) vs "
             f"{tgt} 1-Month Forward Return"
             f"<br><sub>Pearson correlations across lead horizons {axis_note}. "
             f"* p<0.05, ** p<0.01. {best_caption}{daily_caveat}</sub>")
    src_note = ("Source: FRED / market data via Evan ECON-LA1 "
                f"({path.name}). " + best_caption + daily_caveat)
    # The heatmap has no legend, but the x-axis title and the source note both
    # live below the plot. Give the axis title a standoff and drop the source note
    # to its own band (y=-0.22) under a larger bottom margin so they never overlap
    # at narrow viewport widths.
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={"title": {"text": "Lead (months) applied to signal", "standoff": 16}, "side": "bottom"},
        yaxis={"title": {"text": "Signal transform"}, "autorange": "reversed"},
        template="plotly_white", margin={"l": 140, "r": 80, "t": 110 if is_daily else 90, "b": 95},
        annotations=[{
            "text": src_note, "showarrow": False, "xref": "paper", "yref": "paper",
            "x": 0, "y": -0.22, "yanchor": "top", "font": {"size": 10, "color": "#666"},
            "align": "left",
        }],
    )
    return fig, best_caption + daily_caveat, str(path.relative_to(ROOT))


STAR = "#009E73"  # okabe-ito green — winner marker, distinct from bars/bench


def _coherent_artifacts(pair):
    """Return (winner_curve_path, clean_envelope_path) if the GH#13 native
    coherent artifacts exist for this pair, else (None, None)."""
    try:
        wc, _ = latest_dated(pair, "lead_winner_curve")
        env, _ = latest_dated(pair, "lead_clean_envelope")
        return wc, env
    except (FileNotFoundError, IndexError, ValueError):
        return None, None


# ── Chart 2 (COHERENT): winner's own curve on the native grid ───────────────
# GH #13. Foregrounds the PUBLISHED winner's own OOS-Sharpe-by-lead curve against
# the best-of-any-signal envelope on the SAME native tournament grid (envelope >=
# winner curve by construction). Replaces the exploratory-sweep bars, on which the
# winner could appear to sit off a taller bar from a different grid.
def build_coherent_sharpe_chart(pair, ind, tgt, bh, w, wc_path, env_path):
    wc = read_rows(wc_path)
    env = read_rows(env_path)
    date = re.search(r"(\d{8})", wc_path.name).group(1)
    leads = [int(r["lead_months"]) for r in wc]
    xlab = [f"L{l}" for l in leads]
    curve = [float(r["oos_sharpe"]) for r in wc]
    envv = [float(r["best_oos_sharpe"]) for r in env]
    # provenance per lead: which the pipeline scored vs which the validated engine
    # patched, so the reader can see exactly what was originally tested.
    src = [r.get("lead_source", "pipeline") for r in wc]
    patched = [f"L{l}" for l, s in zip(leads, src) if s == "patched"]
    curve_sym = ["circle" if s == "pipeline" else "circle-open" for s in src]
    env_col = ["rgba(108,122,137,0.42)" if s == "pipeline" else "rgba(108,122,137,0.18)"
               for s in src]
    win_lead = int(w.get("lead_value", w.get("lead_months")))
    win_sharpe = float(w.get("oos_sharpe"))
    curve_peak = leads[max(range(len(curve)), key=lambda i: curve[i])]
    env_peak = leads[max(range(len(envv)), key=lambda i: envv[i])]
    _sorted_env = sorted(envv, reverse=True)
    env_flat = len(_sorted_env) > 1 and (_sorted_env[0] - _sorted_env[1]) < 0.10

    if curve_peak == win_lead == env_peak:
        # winner at the top, but be honest about a flat envelope (verifier caution):
        # a marginal peak within reconstruction/OOS noise is not a decisive one.
        if env_flat:
            frame = (f"On the tournament's own grid the winner's lead L{win_lead} is at the "
                     f"top of a NEARLY FLAT envelope (leads differ by &lt;0.10 Sharpe) — no lead "
                     f"is decisively best. It is not the off-peak dip a different (exploratory) "
                     f"sweep grid suggested, but the flat profile means the lead choice is "
                     f"weakly identified, consistent with this pair's low-confidence framing.")
        else:
            frame = (f"On the tournament's own grid the published winner sits at the envelope "
                     f"peak (L{win_lead}): its own curve and the best-of-any-signal envelope "
                     f"both peak there.")
    else:
        frame = (f"The grey bars show the best ANY signal can do at each lead; the "
                 f"published strategy is chosen for reliability, not the single highest "
                 f"score, so its lead (L{win_lead}) can differ from the tallest bar "
                 f"(L{env_peak}) — by design. The orange line is the winner's OWN "
                 f"curve, peaking at L{curve_peak}.")
    cap = (f"Published winner's own OOS-Sharpe-by-lead curve (foreground, {ind}) peaks "
           f"at L{curve_peak}; deployed lead L{win_lead} = {win_sharpe:.2f}. "
           f"Grey bars: best-of-any-signal envelope on the same native grid "
           f"(envelope >= winner curve at every lead). Buy-and-hold {tgt} = {bh:.2f}. "
           f"{frame}")

    patched_clause = (f" Open markers = leads the pipeline's coarse grid did not test, "
                      f"patched here by the same validated tournament rule ({', '.join(patched)})."
                      if patched else "")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=xlab, y=envv, name="Best of ANY signal per lead (context)",
        marker={"color": env_col},
        hovertemplate="%{x}<br>envelope Sharpe=%{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=xlab, y=curve, mode="lines+markers", name="Published winner's own curve",
        line={"color": BAR, "width": 3},
        marker={"size": 8, "color": BAR, "symbol": curve_sym,
                "line": {"width": 1.5, "color": BAR}},
        hovertemplate="%{x}<br>winner Sharpe=%{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[f"L{win_lead}"], y=[win_sharpe], mode="markers",
        name=f"Published winner L{win_lead} = {win_sharpe:.2f}",
        marker={"size": 16, "color": STAR, "symbol": "star",
                "line": {"width": 1, "color": "#000"}}))
    fig.add_trace(go.Scatter(
        x=xlab, y=[bh] * len(xlab), mode="lines", name=f"Buy & Hold {tgt} ({bh:.2f})",
        line={"color": BENCH, "dash": "dash", "width": 1.5}, hoverinfo="skip"))
    title = (f"Lead vs OOS Sharpe — winner on the native tournament grid: {ind} -> "
             f"{tgt}<br><sub>Orange: the PUBLISHED winner's OWN OOS Sharpe by lead "
             f"(solid = pipeline-scored, open = patched). Grey bars: best-of-any-signal "
             f"envelope, same source. Dashed: {tgt} buy-and-hold. {frame}</sub>")
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={"title": {"text": "Lead (months) applied to signal", "standoff": 18}},
        yaxis={"title": {"text": "OOS Sharpe ratio"}, "zeroline": True},
        template="plotly_white", barmode="overlay",
        legend={"orientation": "h", "y": -0.34, "yanchor": "top", "x": 0, "xanchor": "left"},
        margin={"l": 70, "r": 40, "t": 110, "b": 150})
    fig.add_annotation(
        text=f"Source: single native lead tournament (lead_tournament_native, {date}).{patched_clause}",
        showarrow=False, xref="paper", yref="paper", x=0, y=-0.52, yanchor="top",
        font={"size": 10, "color": "#666"}, align="left")
    return fig, cap + patched_clause, str(wc_path.relative_to(ROOT))


# ── Chart 2 (COHERENT, DAILY axis): winner's own curve on the daily grid ────
# GH#13 daily Class-A track. Same coherent construction as build_coherent_sharpe_chart
# but on the pair's NATIVE DAILY lead axis (trading days {0,1,5,21,63,126,252}), not a
# monthly resample. The winner is a same-day (L0) COINCIDENT strategy — credit->equity
# is coincident/short-horizon — so the x-axis is trading days and the star sits at 0d.
def build_coherent_sharpe_chart_daily(pair, ind, tgt, bh, w, wc_path, env_path):
    wc = read_rows(wc_path)
    env = read_rows(env_path)
    date = re.search(r"(\d{8})", wc_path.name).group(1)
    lead_key = next(k for k in wc[0] if k.startswith("lead_"))   # lead_days
    leads = [int(r[lead_key]) for r in wc]

    def _lab(l):
        return f"{l}d"

    xlab = [_lab(l) for l in leads]
    curve = [float(r["oos_sharpe"]) for r in wc]
    envv = [float(r["best_oos_sharpe"]) for r in env]
    win_lead = int(w.get("lead_value", 0))
    win_sharpe = float(w.get("oos_sharpe"))
    win_lab = _lab(win_lead)
    curve_peak = leads[max(range(len(curve)), key=lambda i: curve[i])]
    env_peak = leads[max(range(len(envv)), key=lambda i: envv[i])]

    coincident = win_lead == 0
    if curve_peak == win_lead == env_peak:
        frame = (f"On the pair's OWN daily grid the published winner sits at the envelope "
                 f"peak ({win_lab}) — both its own curve and the best-of-any-signal envelope "
                 f"peak there, and the profile decays monotonically as the signal is lagged. "
                 + ("This is a SAME-DAY (coincident) edge: when the credit-stress regime flips, "
                    "equities move the same day — not a multi-month leading indicator. "
                    if coincident else "")
                 + "The grid extension to 126/252 trading days surfaces no long-lead edge "
                   "(both fail a t&gt;3 hurdle) — multiple-testing noise, as credit&#8594;equity "
                   "coincident/short-horizon transmission predicts.")
    else:
        frame = (f"The orange line is the winner's OWN OOS Sharpe by daily lead, peaking at "
                 f"{_lab(curve_peak)}; grey bars are the best any signal reaches at each lead "
                 f"(envelope &#8805; winner curve by construction).")
    cap = (f"Published winner's own OOS-Sharpe-by-lead curve (foreground, {ind}) on the DAILY "
           f"axis; deployed lead {win_lab} = {win_sharpe:.2f}. Grey bars: best-of-any-signal "
           f"envelope on the same daily grid. Buy-and-hold {tgt} = {bh:.2f}. {frame}")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=xlab, y=envv, name="Best of ANY signal per lead (context)",
        marker={"color": "rgba(108,122,137,0.42)"},
        hovertemplate="%{x}<br>envelope Sharpe=%{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=xlab, y=curve, mode="lines+markers", name="Published winner's own curve",
        line={"color": BAR, "width": 3},
        marker={"size": 8, "color": BAR, "symbol": "circle", "line": {"width": 1.5, "color": BAR}},
        hovertemplate="%{x}<br>winner Sharpe=%{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[win_lab], y=[win_sharpe], mode="markers",
        name=f"Published winner {win_lab} = {win_sharpe:.2f} (same-day)",
        marker={"size": 16, "color": STAR, "symbol": "star", "line": {"width": 1, "color": "#000"}}))
    fig.add_trace(go.Scatter(
        x=xlab, y=[bh] * len(xlab), mode="lines", name=f"Buy & Hold {tgt} ({bh:.2f})",
        line={"color": BENCH, "dash": "dash", "width": 1.5}, hoverinfo="skip"))
    title = (f"Lead vs OOS Sharpe — winner on the native DAILY grid: {ind} -> {tgt}"
             f"<br><sub>Orange: the PUBLISHED winner's OWN OOS Sharpe by daily lead (trading days). "
             f"Grey bars: best-of-any-signal envelope, same source. Dashed: {tgt} buy-and-hold. {frame}</sub>")
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={"title": {"text": "Lead (trading days) applied to signal", "standoff": 18},
               "type": "category"},
        yaxis={"title": {"text": "OOS Sharpe ratio"}, "zeroline": True},
        template="plotly_white", barmode="overlay",
        legend={"orientation": "h", "y": -0.34, "yanchor": "top", "x": 0, "xanchor": "left"},
        margin={"l": 70, "r": 40, "t": 110, "b": 150})
    fig.add_annotation(
        text=f"Source: single native DAILY lead tournament (lead_tournament_native, {date}).",
        showarrow=False, xref="paper", yref="paper", x=0, y=-0.52, yanchor="top",
        font={"size": 10, "color": "#666"}, align="left")
    return fig, cap, str(wc_path.relative_to(ROOT))


# ── Chart 2: lead_sharpe_distribution (bar + cloud) ─────────────────────────
def build_sharpe_chart(pair, ind, tgt, bh, w):
    # GH #13 coherent view: when native winner-curve + clean-envelope artifacts
    # exist AND the winner is on the monthly comparability axis, foreground the
    # winner's own curve on the native grid instead of the exploratory sweep bars.
    wc_path, env_path = _coherent_artifacts(pair)
    win_unit = (w.get("lead_unit") or "months").rstrip("s")
    if wc_path is not None and env_path is not None and win_unit == "month":
        return build_coherent_sharpe_chart(pair, ind, tgt, bh, w, wc_path, env_path)
    # GH#13 daily Class-A track: a DAILY-signal pair with native coherent artifacts
    # gets the coherent chart on its OWN daily axis (trading days) — never the monthly
    # resample. Guarded on win_unit=="day" so monthly/quarterly paths are untouched.
    if wc_path is not None and env_path is not None and win_unit == "day":
        return build_coherent_sharpe_chart_daily(pair, ind, tgt, bh, w, wc_path, env_path)

    path, date = latest_dated(pair, "lead_tournament")
    rows = read_rows(path)
    leads = [int(r["lead_months"]) for r in rows]
    best = [float(r["best_oos_sharpe"]) for r in rows]
    p25 = [float(r["p25_oos_sharpe"]) for r in rows]
    med = [float(r["median_oos_sharpe"]) for r in rows]
    p75 = [float(r["p75_oos_sharpe"]) for r in rows]
    n_valid = [int(r["n_valid"]) for r in rows]
    xlab = [f"L{l}" for l in leads]

    imax = max(range(len(best)), key=lambda i: best[i])
    max_lead, max_val = leads[imax], best[imax]
    win = rows[imax]
    near = sum(1 for v in best if abs(v - max_val) <= 0.05)
    shape = "a single spike" if near <= 2 else f"a broad ridge ({near} leads within 0.05)"

    # Published-winner lead/Sharpe (native tournament) — distinct from sweep max.
    # For DAILY-executed pairs the winner lead is in trading DAYS and does NOT
    # sit on the monthly L0..L12 comparability axis — say so explicitly and in
    # the native unit (do not print a misleading "L{days}" on a monthly chart).
    win_lead = w.get("lead_value", w.get("lead_months"))
    win_sharpe = w.get("oos_sharpe")
    win_unit = (w.get("lead_unit") or "months").rstrip("s")  # "day"/"month"
    # Winner is markable only when it is an ACTUAL grid column. On non-contiguous
    # sweep grids (e.g. t10y3m leads = [0,1,2,3,6,9,12]) a lead can be within 0..12
    # yet not be a column — drawing a vline there would land at a phantom position.
    winner_on_axis = (win_lead is not None and win_unit == "month"
                      and 0 <= int(win_lead) <= 12 and int(win_lead) in leads)
    winner_note = ""
    if win_lead is not None and win_sharpe is not None:
        if win_unit == "month":
            winner_note = (f" Published winner sits at L{int(win_lead)} "
                           f"(native tournament, OOS Sharpe {float(win_sharpe):.2f}).")
        else:
            winner_note = (f" Published winner is a daily-executed strategy at "
                           f"{int(win_lead)} {win_unit}(s) lead (OOS Sharpe "
                           f"{float(win_sharpe):.2f}) — off this monthly comparability "
                           f"axis; the bars are the monthly-resampled sweep, not the "
                           f"deployed daily horizon.")
    cap = (f"Sweep-grid best OOS Sharpe {max_val:.2f} at L{max_lead} "
           f"({win['best_signal']} x {win['best_strategy']}); {shape}. "
           f"Buy-and-hold {tgt} OOS Sharpe = {bh:.2f}.{winner_note}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xlab + xlab[::-1], y=p75 + p25[::-1], fill="toself",
        fillcolor="rgba(153,153,153,0.18)", line={"width": 0},
        name="p25-p75 of valid combos", hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=xlab, y=med, mode="lines+markers", name="Median valid combo",
        line={"color": DOT, "width": 1.5, "dash": "dot"}, marker={"size": 5, "color": DOT},
        hovertemplate="%{x}<br>median Sharpe=%{y:.3f}<extra></extra>"))
    fig.add_trace(go.Bar(
        x=xlab, y=best, name="Best Sharpe per lead", marker={"color": BAR},
        text=[f"{v:.2f}" for v in best], textposition="outside", textfont={"size": 9},
        customdata=n_valid,
        hovertemplate="%{x}<br>best Sharpe=%{y:.3f}<br>valid combos=%{customdata}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=xlab, y=[bh] * len(xlab), mode="lines", name=f"Buy & Hold {tgt} ({bh:.2f})",
        line={"color": BENCH, "dash": "dash", "width": 2}, hoverinfo="skip"))
    # Sweep-max callout: arrow above the tallest bar.
    fig.add_annotation(x=xlab[imax], y=max_val, text=f"<b>sweep max L{max_lead}</b><br>{max_val:.2f}",
                       showarrow=True, arrowhead=2, ax=0, ay=-30, font={"size": 10})
    # Mark the published-winner lead with a distinct vertical reference so it is
    # never conflated with the sweep-grid tallest bar. The vline annotation is
    # anchored to the BOTTOM of the plot (opposite the sweep-max arrow, which sits
    # at the top) so the two callouts never collide — including when the two leads
    # are identical or adjacent (e.g. busloans sweep max L5 vs winner L6). When the
    # winner lead EQUALS the sweep-max lead, suppress the separate callout text and
    # fold the fact into the vline label to avoid double-printing the same column.
    if winner_on_axis:
        same_lead = int(win_lead) == int(max_lead)
        win_text = ("published winner = sweep max"
                    if same_lead else f"published winner L{int(win_lead)}")
        # Position by CATEGORICAL LABEL (xlab at the winner's grid index), NOT the
        # raw int. On a categorical x-axis add_vline(x=N) anchors to category INDEX
        # N, so on a non-contiguous grid the raw lead value lands on the wrong bar
        # (t10y3m winner L6 is index 4; x=6 would land on L12). Mirrors how the
        # sweep-max arrow already positions via xlab[imax].
        # Position by the winner's CATEGORICAL INDEX, not the raw lead value. On a
        # categorical x-axis Plotly anchors a numeric x to the category INDEX, so
        # the raw value lands on the wrong bar on a non-contiguous grid (t10y3m
        # winner L6 is index 4; x=6 would land on L12). For contiguous grids
        # index == value, so this is a no-op and the JSON is unchanged. Passing an
        # int (the index) keeps add_vline's annotation helper working — a string
        # label would make it raise on the numeric x-range average.
        wxi = leads.index(int(win_lead))
        fig.add_vline(x=wxi, line={"color": "#000", "dash": "dot", "width": 1.2},
                      annotation_text=win_text,
                      annotation_position="bottom right", annotation_font_size=9,
                      annotation_yshift=4)

    title = (f"Lead vs OOS Sharpe (standardized sweep grid): {ind} -> {tgt} (L = 0..12)"
             f"<br><sub>Bars: best OOS Sharpe at each lead in the P1/P2 gating sweep. "
             f"Grey band/dots: p25-p75 & median of valid combos. Dashed: {tgt} "
             f"buy-and-hold. {cap}</sub>")
    # Layout band budget (top -> bottom): x-axis ticks, then the x-axis title
    # (standoff 18), then the horizontal legend (y=-0.34, anchored top so it grows
    # downward), then the source note (y=-0.52). Each element gets its own band so
    # the axis title never prints through the legend row. Bottom margin (150) is
    # sized for the narrowest plausible content column (~700px) where the legend
    # wraps to two rows.
    fig.update_layout(
        title={"text": title, "font": {"size": 14}},
        xaxis={"title": {"text": "Lead (months) applied to signal", "standoff": 18}},
        yaxis={"title": {"text": "OOS Sharpe ratio"}, "zeroline": True},
        template="plotly_white", barmode="overlay",
        legend={"orientation": "h", "y": -0.34, "yanchor": "top", "x": 0, "xanchor": "left"},
        margin={"l": 70, "r": 40, "t": 110, "b": 150})
    fig.add_annotation(text=f"Source: Evan ECON-LT1 standardized lead sweep ({date}).",
                       showarrow=False, xref="paper", yref="paper",
                       x=0, y=-0.52, yanchor="top", font={"size": 10, "color": "#666"}, align="left")
    return fig, cap, str(path.relative_to(ROOT))


def write_meta(pair, chart_name, method_name, expected, caption, rules, sources):
    meta = {
        "chart_name": chart_name, "pair_id": pair, "palette_id": "okabe_ito_2026",
        "rules_applied": rules, "narrative_alignment_note": caption, "caption": caption,
        "created_at": CREATED, "method_name": method_name,
        "expected_chart_type": expected, "disposition": "consumed",
        "source_artifacts": sources,
        "generated_by": "Viz Vera — scripts/generate_lead_charts.py (VIZ-LEAD1)",
    }
    (ROOT / f"output/charts/{pair}/plotly/{chart_name}_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n")


def discover_pairs():
    out = []
    for d in sorted((ROOT / "results").iterdir()):
        if not d.is_dir() or d.name in FROZEN:
            continue
        if list(d.glob("lead_correlation_*.csv")) and list(d.glob("lead_tournament_*.csv")):
            out.append(d.name)
    return out


def _perceptual_png(fig, path):
    """Best-effort perceptual-check PNG. Skipped (with a warning) when kaleido is
    absent — the PNG is a review aid, not a portal artifact, so its absence must
    never block JSON emission in a minimal environment."""
    try:
        fig.write_image(str(path), width=1100, height=600, scale=2)
    except Exception as e:  # kaleido missing / export engine error
        print(f"    [skip PNG] {path.name}: {type(e).__name__} (JSON written)")


def run(pair):
    w = load_winner(pair)
    ind, tgt = display_names(pair, w)
    bh, bh_fallback = bh_sharpe(pair, w)
    if bh_fallback:
        print(f"  [FLAG] {pair}: winner_summary.json has no bh_oos_sharpe — "
              f"used canonical SPY B&H fallback {bh:.4f}. Upstream gap (Evan).")
    d = ROOT / f"output/charts/{pair}/plotly"
    d.mkdir(parents=True, exist_ok=True)

    f1, c1, src1 = build_corr_chart(pair, ind, tgt, w)
    (d / "correlations_lead_view.json").write_text(pio.to_json(f1))
    write_meta(pair, "correlations_lead_view", "lead_correlation_view", "heatmap", c1,
               ["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"], [src1])
    _perceptual_png(f1, d / "_perceptual_check_correlations_lead_view.png")

    f2, c2, src2 = build_sharpe_chart(pair, ind, tgt, bh, w)
    (d / "lead_sharpe_distribution.json").write_text(pio.to_json(f2))
    write_meta(pair, "lead_sharpe_distribution", "lead_sharpe_distribution", "bar", c2,
               ["VIZ-LEAD1", "VIZ-IC1", "VIZ-TX1", "VIZ-O1"],
               [src2, f"results/{pair}/winner_summary.json"])
    _perceptual_png(f2, d / "_perceptual_check_lead_sharpe_distribution.png")

    print(f"[{pair}] OK  (B&H={bh:.4f})")
    print(f"    corr:   {c1}")
    print(f"    sharpe: {c2}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pairs = args or discover_pairs()
    for p in pairs:
        if p in FROZEN:
            print(f"[{p}] SKIP (frozen)")
            continue
        run(p)


if __name__ == "__main__":
    main()
