"""Chart generator — crude_oil_xle.

Emits the 9 mandatory chart JSONs + 4 crisis-episode zooms required by
GATE-CMP1 / DPS-EP1. Uses scripts._nber for recession shading (BL-DUP-4).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts._nber import RECESSIONS, add_nber_shading
from scripts._stamp import iso_utc_now
PAIR_ID = "crude_oil_xle"
RESULTS = ROOT / "results" / PAIR_ID
CHARTS = ROOT / "output" / "charts" / PAIR_ID / "plotly"
CHARTS.mkdir(parents=True, exist_ok=True)

# Okabe-Ito palette (SOP-declared standard per Wave 10H.1)
COL_INDICATOR = "#D55E00"   # vermillion — WTI
COL_TARGET = "#0072B2"      # blue — XLE
COL_STRATEGY = "#009E73"    # bluish-green
COL_BENCHMARK = "#999999"   # neutral grey


def _save(fig: go.Figure, name: str, *, description: str = "", page: str = "story"):
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=60, r=40, t=80, b=120),
        title_x=0.01,
        legend=dict(orientation="h", y=-0.18, x=0),
    )
    out = CHARTS / f"{name}.json"
    out.write_text(fig.to_json())
    meta = {
        "pair_id": PAIR_ID,
        "chart_name": name,
        "description": description,
        "page": page,
        "generated_at": iso_utc_now(),
        "disposition": "consumed",
        "palette_id": "okabe_ito_2026",
    }
    (CHARTS / f"{name}_meta.json").write_text(json.dumps(meta, indent=2))


def load_signals() -> pd.DataFrame:
    sig_path = sorted(RESULTS.glob("signals_*.parquet"))[-1]
    df = pd.read_parquet(sig_path)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")


def load_winner() -> dict:
    return json.loads((RESULTS / "winner_summary.json").read_text())


def load_trades() -> pd.DataFrame:
    return pd.read_csv(RESULTS / "winner_trade_log.csv")


def chart_hero(df: pd.DataFrame, winner: dict):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df.index, y=df["wti"], name="WTI Crude (USD/bbl)",
                              line=dict(color=COL_INDICATOR, width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df["xle"], name="XLE (USD)",
                              line=dict(color=COL_TARGET, width=2)), secondary_y=True)
    fig.update_yaxes(title_text="WTI (USD/barrel)", secondary_y=False)
    fig.update_yaxes(title_text="XLE (USD)", secondary_y=True)
    add_nber_shading(fig, recessions=RECESSIONS)
    fig.update_layout(
        title=f"WTI Crude vs XLE — full sample (weekly, {df.index[0].date()} to {df.index[-1].date()})",
    )
    _save(fig, "hero", description="WTI crude and XLE side by side over the full sample.", page="story")


def _equity_from_position(df: pd.DataFrame, winner: dict) -> tuple[pd.Series, pd.Series]:
    """Reconstruct strategy equity + buy-and-hold equity over OOS window."""
    sig_col = winner["signal_column"]
    rule = winner["threshold_rule"]
    thr = float(winner["threshold_value"])
    direction = winner["direction"]
    s = df[sig_col]
    if rule == "gt":
        fire = s > thr
    elif rule == "lt":
        fire = s < thr
    elif rule == "gt_zero":
        fire = s > 0
    else:
        raise ValueError(rule)
    if direction == "long_short_sign":
        pos = pd.Series(np.where(s > 0, 1.0, -1.0), index=s.index)
    else:
        pos = fire.astype(float)
    pos = pos.shift(1).fillna(0)
    ret = df["xle_logret_1w"]
    strat = (pos * ret).dropna()
    bh = ret.dropna()
    # Slice OOS
    start = winner["oos_period_start"]
    end = winner["oos_period_end"]
    strat = strat.loc[start:end]
    bh = bh.loc[start:end]
    return (1 + strat).cumprod(), (1 + bh).cumprod()


def chart_equity_curves(df: pd.DataFrame, winner: dict):
    strat_eq, bh_eq = _equity_from_position(df, winner)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strat_eq.index, y=strat_eq.values, name="Strategy",
                              line=dict(color=COL_STRATEGY, width=2)))
    fig.add_trace(go.Scatter(x=bh_eq.index, y=bh_eq.values, name="Buy & Hold (XLE)",
                              line=dict(color=COL_BENCHMARK, width=2, dash="dot")))
    fig.update_layout(
        title=f"OOS equity curves — strategy vs buy-and-hold ({winner['oos_period_start']} to {winner['oos_period_end']})",
        yaxis_title="Cumulative return (1.0 = start)",
    )
    add_nber_shading(fig, recessions=RECESSIONS)
    _save(fig, "equity_curves", description="Cumulative return of strategy vs XLE buy-and-hold over the OOS window.", page="strategy")


def chart_drawdown(df: pd.DataFrame, winner: dict):
    strat_eq, bh_eq = _equity_from_position(df, winner)
    strat_dd = strat_eq / strat_eq.cummax() - 1
    bh_dd = bh_eq / bh_eq.cummax() - 1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strat_dd.index, y=strat_dd.values * 100, name="Strategy",
                              line=dict(color=COL_STRATEGY, width=2),
                              fill="tozeroy", fillcolor="rgba(0,158,115,0.12)"))
    fig.add_trace(go.Scatter(x=bh_dd.index, y=bh_dd.values * 100, name="Buy & Hold",
                              line=dict(color=COL_BENCHMARK, width=2, dash="dot")))
    fig.update_layout(title="OOS drawdown — strategy vs buy-and-hold",
                      yaxis_title="Drawdown (%)")
    add_nber_shading(fig, recessions=RECESSIONS)
    _save(fig, "drawdown", description="Drawdown comparison over the OOS window.", page="strategy")


def chart_walk_forward(df: pd.DataFrame, winner: dict):
    """Rolling 1-year Sharpe of the strategy over OOS."""
    strat_eq, _ = _equity_from_position(df, winner)
    strat_ret = strat_eq.pct_change().dropna()
    rolling_sharpe = (strat_ret.rolling(52).mean() / strat_ret.rolling(52).std()) * np.sqrt(52)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rolling_sharpe.index, y=rolling_sharpe.values, name="Rolling 1y Sharpe",
                              line=dict(color=COL_STRATEGY, width=2)))
    fig.add_hline(y=0, line_dash="dash", line_color="#888")
    fig.update_layout(title="Walk-forward — rolling 1-year strategy Sharpe (OOS)",
                      yaxis_title="Sharpe ratio")
    add_nber_shading(fig, recessions=RECESSIONS)
    _save(fig, "walk_forward", description="Rolling one-year Sharpe of the strategy across the OOS window.", page="strategy")


def chart_tournament_scatter(winner: dict):
    tdf_path = sorted(RESULTS.glob("tournament_results_*.csv"))[-1]
    tdf = pd.read_csv(tdf_path)
    tdf = tdf[tdf["signal"] != "BENCHMARK"].dropna(subset=["is_sharpe", "oos_sharpe"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tdf["is_sharpe"], y=tdf["oos_sharpe"], mode="markers+text",
        marker=dict(size=12, color=COL_STRATEGY, line=dict(width=1, color="white")),
        text=tdf["strategy_family"], textposition="top center", textfont=dict(size=9),
        name="Strategies",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="#aaa")
    fig.add_vline(x=0, line_dash="dot", line_color="#aaa")
    fig.update_layout(
        title="Tournament scatter — IS vs OOS Sharpe",
        xaxis_title="In-sample Sharpe",
        yaxis_title="Out-of-sample Sharpe",
    )
    _save(fig, "tournament_scatter", description="IS vs OOS Sharpe scatter across all tournament strategies.", page="evidence")


def chart_subperiod_sharpe(df: pd.DataFrame, winner: dict):
    """Sharpe per calendar year over OOS."""
    strat_eq, bh_eq = _equity_from_position(df, winner)
    strat_ret = strat_eq.pct_change().dropna()
    bh_ret = bh_eq.pct_change().dropna()
    years = pd.DataFrame({"strat": strat_ret, "bh": bh_ret})
    by_year = years.groupby(years.index.year).agg(lambda s: (s.mean() / s.std() * np.sqrt(52)) if s.std() > 0 else 0)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=by_year.index, y=by_year["strat"], name="Strategy", marker_color=COL_STRATEGY))
    fig.add_trace(go.Bar(x=by_year.index, y=by_year["bh"], name="Buy & Hold", marker_color=COL_BENCHMARK))
    fig.update_layout(title="Sub-period Sharpe — calendar year (OOS)", yaxis_title="Sharpe", barmode="group")
    _save(fig, "subperiod_sharpe", description="Per-calendar-year Sharpe for the strategy vs buy-and-hold.", page="evidence")


def chart_rolling_correlation(df: pd.DataFrame):
    rho = df["wti_logret_1w"].rolling(52).corr(df["xle_logret_1w"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rho.index, y=rho.values, name="ρ(WTI ret, XLE ret), 52w rolling",
                              line=dict(color=COL_INDICATOR, width=2)))
    fig.add_hline(y=0, line_dash="dot", line_color="#888")
    fig.update_layout(title="Rolling 52-week correlation — WTI vs XLE weekly returns",
                      yaxis_title="Pearson ρ")
    add_nber_shading(fig, recessions=RECESSIONS)
    _save(fig, "rolling_correlation", description="Rolling Pearson correlation between WTI and XLE weekly returns.", page="evidence")


def chart_structural_break(df: pd.DataFrame):
    """CUSUM of recursive residuals of OLS xle_ret = a + b*wti_ret over the sample."""
    from statsmodels.stats.diagnostic import recursive_olsresiduals
    import statsmodels.api as sm
    paired = df[["wti_logret_1w", "xle_logret_1w"]].dropna()
    X = sm.add_constant(paired["wti_logret_1w"])
    res = sm.OLS(paired["xle_logret_1w"], X).fit()
    rresid, *_ = recursive_olsresiduals(res, skip=20, alpha=0.95)
    cusum = pd.Series(rresid, index=paired.index[len(paired)-len(rresid):]).cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cusum.index, y=cusum.values, name="CUSUM",
                              line=dict(color=COL_INDICATOR, width=2)))
    fig.add_hline(y=0, line_dash="dot", line_color="#888")
    fig.update_layout(title="Structural break — CUSUM of recursive residuals",
                      yaxis_title="Cumulative residual")
    add_nber_shading(fig, recessions=RECESSIONS)
    _save(fig, "structural_break", description="CUSUM of recursive residuals; departures from zero suggest regime shifts.", page="evidence")


def chart_regime_stats(df: pd.DataFrame):
    """Mean XLE forward return by WTI rolling-vol quartile."""
    q = df["wti_vol_q_13w"].dropna()
    fwd = df["xle_fwd_13w"].dropna()
    paired = pd.concat([q, fwd], axis=1).dropna()
    paired.columns = ["vol_quartile", "fwd_ret"]
    paired["bucket"] = pd.cut(paired["vol_quartile"], [0, 0.25, 0.5, 0.75, 1.0],
                              labels=["Q1 (low vol)", "Q2", "Q3", "Q4 (high vol)"])
    grouped = paired.groupby("bucket", observed=True)["fwd_ret"].agg(["mean", "std", "count"])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped.index.astype(str), y=grouped["mean"] * 100,
        error_y=dict(type="data", array=grouped["std"] * 100 / np.sqrt(grouped["count"])),
        marker_color=COL_INDICATOR, name="Mean 13w fwd XLE return",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="#888")
    fig.update_layout(title="Regime stats — 13-week forward XLE return by WTI realized-vol quartile",
                      yaxis_title="Mean forward return (%)")
    _save(fig, "regime_stats", description="Mean 13-week forward XLE return conditioned on WTI's 13-week realized-vol quartile.", page="evidence")


# ── Crisis-episode zooms ────────────────────────────────────────────────
EPISODES = {
    "dotcom": ("2000-01-01", "2002-12-31", "Dot-com bust"),
    "gfc": ("2007-06-01", "2009-12-31", "Global Financial Crisis"),
    "covid": ("2020-01-01", "2020-12-31", "COVID-19 shock"),
    "inflation_2022": ("2022-01-01", "2023-06-30", "2022 inflation / rate-shock cycle"),
}


def chart_episode_zoom(df: pd.DataFrame, slug: str, start: str, end: str, label: str):
    sub = df.loc[start:end]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=sub.index, y=sub["wti"], name="WTI",
                              line=dict(color=COL_INDICATOR, width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=sub.index, y=sub["xle"], name="XLE",
                              line=dict(color=COL_TARGET, width=2)), secondary_y=True)
    fig.update_yaxes(title_text="WTI (USD/bbl)", secondary_y=False)
    fig.update_yaxes(title_text="XLE (USD)", secondary_y=True)
    fig.update_layout(title=f"Episode zoom — {label} ({start} to {end})")
    _save(fig, f"history_zoom_{slug}",
          description=f"Side-by-side WTI and XLE during {label}.",
          page="evidence")


def main():
    df = load_signals()
    winner = load_winner()
    chart_hero(df, winner)
    chart_equity_curves(df, winner)
    chart_drawdown(df, winner)
    chart_walk_forward(df, winner)
    chart_tournament_scatter(winner)
    chart_subperiod_sharpe(df, winner)
    chart_rolling_correlation(df)
    chart_structural_break(df)
    chart_regime_stats(df)
    for slug, (start, end, label) in EPISODES.items():
        chart_episode_zoom(df, slug, start, end, label)
    print(f"OK — {len(list(CHARTS.glob('*.json'))) // 2} chart pairs (json+meta) emitted to {CHARTS}.")


if __name__ == "__main__":
    main()
