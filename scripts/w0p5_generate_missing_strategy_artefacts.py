#!/usr/bin/env python3
"""W0.5 generator: produce missing Strategy-page artefacts for indpro_spy + vix_vix3m_spy.

For each pair, generates the 3 artefacts the Strategy template expects:
  output/charts/<pair>/plotly/drawdown.json          (Performance tab)
  output/charts/<pair>/plotly/walk_forward.json      (Confidence tab)
  results/<pair>/winner_trades_broker_style.csv      (APP-TL1 broker log)

Reads:
  results/<pair>/winner_summary.json                 (winner spec)
  results/<pair>/signals_*.parquet                   (most recent — signal series)
  results/<pair>/tournament_results_*.csv            (lookup threshold by winner code)
  data/<pair>_*.parquet                              (target price series)

The tournament_results lookup is needed because legacy pairs (incl.
indpro_spy + vix_vix3m_spy) have `threshold_value: null` in their
winner_summary — known migration debt (BL-LEGACY-WINNER-SUMMARY-SHAPE).
We pull the actual numeric threshold from the matching row in
tournament_results.csv based on signal_code + threshold_code +
strategy_code.

Following the threshold/strategy semantics already encoded by
synthesize_broker_trade_log.py and pair_pipeline_indpro_spy.py.
"""
from __future__ import annotations

import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

REPO = Path("/workspaces/aig-rlic-plus")


def latest(pattern: str) -> Path | None:
    matches = sorted(REPO.glob(pattern))
    return matches[-1] if matches else None


def load_winner_with_threshold(pair: str) -> dict:
    """Load winner_summary.json and backfill threshold_value if null
    by scanning the tournament_results.csv for the matching row."""
    ws_path = REPO / "results" / pair / "winner_summary.json"
    w = json.loads(ws_path.read_text())
    if w.get("threshold_value") is not None:
        return w
    # Backfill from tournament_results — match signal_code + threshold_code + strategy_code
    tr_path = latest(f"results/{pair}/tournament_results_*.csv")
    if tr_path is None:
        raise FileNotFoundError(f"No tournament_results CSV for {pair}")
    t = pd.read_csv(tr_path)
    # Some legacy CSVs use 'threshold' instead of 'threshold_code', etc.
    sig_code = w.get("signal_code")
    thr_code = w.get("threshold_code")
    strat_code = w.get("strategy_code") or w.get("strategy_family")
    cand = t[(t["signal"] == sig_code) & (t["threshold"] == thr_code) & (t["strategy"] == strat_code)]
    if cand.empty:
        # Fall back to best valid row by oos_sharpe
        cand = t[t.get("valid", True) == True].sort_values("oos_sharpe", ascending=False).head(1)
    if cand.empty:
        raise ValueError(f"Could not backfill threshold for {pair}: no matching tournament row")
    row = cand.iloc[0]
    # Threshold code names like T1_fixed_p25 -> need the actual numeric. The
    # tournament CSV typically doesn't store the numeric threshold (it stored
    # the code). We re-derive from the signal series + percentile semantics
    # below. Mark threshold_code so derive_position can compute it.
    w["_backfilled"] = True
    w["_tournament_row_lead_months"] = int(row.get("lead_months", row.get("lead_days", 0)) or 0)
    return w


def parse_threshold_code(code: str) -> tuple[str, float] | None:
    """Parse 'T1_fixed_p25' -> ('fixed_pct', 0.25). Returns None on unknown."""
    if not code:
        return None
    c = code.lower()
    # Strip the leading Tn_ prefix if present
    if c.startswith("t") and "_" in c:
        c = c.split("_", 1)[1]
    if "fixed_p" in c:
        try:
            pct = int(c.split("fixed_p")[-1])
            return ("fixed_pct", pct / 100.0)
        except ValueError:
            return None
    if "roll" in c and "_p" in c:
        try:
            pct = int(c.split("_p")[-1])
            return ("roll_pct", pct / 100.0)
        except ValueError:
            return None
    if "z" in c and "_" in c:
        # e.g. zscore_1_5 -> ('zscore', 1.5)
        try:
            parts = c.split("_")
            num = float(".".join(parts[-2:]).replace("z", ""))
            return ("zscore", num)
        except ValueError:
            return None
    return None


def derive_position(signal: pd.Series, threshold_code: str, threshold_rule: str,
                     direction: str, strategy_family: str,
                     is_end: pd.Timestamp) -> pd.Series:
    """Derive position series. Uses IS portion of signal to compute the
    numeric threshold via percentile, then applies the strategy rule."""
    is_sig = signal.loc[:is_end].dropna()
    if is_sig.empty:
        return pd.Series(0.0, index=signal.index)
    parsed = parse_threshold_code(threshold_code)
    if parsed is None:
        # Best-effort fallback: use IS median
        thr = float(is_sig.median())
    elif parsed[0] in {"fixed_pct"}:
        thr = float(is_sig.quantile(parsed[1]))
    elif parsed[0] == "roll_pct":
        # Use trailing 1-year rolling percentile (252 daily / 12 monthly)
        win = 252 if isinstance(signal.index, pd.DatetimeIndex) and len(signal) > 1000 else 12
        thr_series = signal.rolling(win, min_periods=max(20, win // 5)).quantile(parsed[1])
        thr = thr_series  # vector threshold
    elif parsed[0] == "zscore":
        # threshold is in z-score units; convert to signal units via IS stats
        mu, sd = float(is_sig.mean()), float(is_sig.std())
        thr = mu + parsed[1] * sd
    else:
        thr = float(is_sig.median())

    # Comparison
    if threshold_rule in {"gt", "gte"}:
        bull = signal > thr
    elif threshold_rule in {"lt", "lte"}:
        bull = signal < thr
    else:
        bull = signal > thr  # fallback

    # Direction
    if (direction or "").lower().startswith("counter"):
        bull = ~bull

    # Strategy translation
    fam = (strategy_family or "").upper()
    if "LONG_SHORT" in fam or "P3" in fam:
        pos = bull.astype(int) * 2 - 1
    elif "SIGNAL_STRENGTH" in fam or "P2" in fam:
        # Crude proxy: clip signal between IS p10 and p90, scale to [-1,+1]
        lo, hi = float(is_sig.quantile(0.10)), float(is_sig.quantile(0.90))
        normed = ((signal - lo) / (hi - lo)).clip(0, 1) * 2 - 1
        if (direction or "").lower().startswith("counter"):
            normed = -normed
        pos = normed
    else:
        pos = bull.astype(int)
    return pos.fillna(0).astype(float)


def make_strategy_returns(pair: str, w: dict) -> tuple[pd.DataFrame, dict]:
    """Returns (df with [position, strategy_ret, equity_curve, bh_equity], meta)."""
    sig_path = latest(f"results/{pair}/signals_*.parquet")
    sig_df = pd.read_parquet(sig_path)
    sig_col = w["signal_column"]
    if sig_col not in sig_df.columns:
        raise ValueError(f"{sig_col!r} not in signals parquet ({sig_path.name})")

    # Target price + return: use the master daily parquet
    data_path = latest(f"data/{pair}_*.parquet")
    if data_path is None:
        raise FileNotFoundError(f"No master parquet for {pair}")
    data_df = pd.read_parquet(data_path)
    # Identify target series. Try common names.
    target_col = None
    for cand in ["spy", "xlp", "xli", "xlv", "xlk", "xly", "xlu", "xlf", "xle"]:
        if cand in data_df.columns:
            target_col = cand
            break
    if target_col is None:
        # Use any column matching the pair_id suffix
        suffix = pair.split("_")[-1]
        if suffix in data_df.columns:
            target_col = suffix
    if target_col is None:
        raise ValueError(f"Cannot identify target price column in {data_path.name}")
    target_ret_col = f"{target_col}_ret"
    if target_ret_col not in data_df.columns:
        data_df[target_ret_col] = data_df[target_col].pct_change()

    # Align signal series to data index (monthly indpro_spy → daily target;
    # forward-fill the signal so each day inherits the most recent month-end value)
    is_end = pd.Timestamp(w.get("oos_period_start", "2019-01-01")) - pd.Timedelta(days=1)
    sig_full = sig_df[sig_col].copy()
    if not isinstance(sig_full.index, pd.DatetimeIndex):
        sig_full.index = pd.to_datetime(sig_full.index)
    sig_on_data = sig_full.reindex(data_df.index, method="ffill")

    pos = derive_position(sig_on_data, w.get("threshold_code", ""),
                           w.get("threshold_rule", "gt"),
                           w.get("direction", "procyclical"),
                           w.get("strategy_family", "P1_long_cash"),
                           is_end)
    lead = int(w.get("lead_value", 0) or 0)
    if lead:
        pos = pos.shift(lead).fillna(0)

    ret = data_df[target_ret_col].fillna(0).astype(float)
    strat_ret = pos * ret
    equity = (1 + strat_ret).cumprod()
    bh_equity = (1 + ret).cumprod()
    out = pd.DataFrame({
        sig_col: sig_on_data,
        "position": pos,
        "strategy_return": strat_ret,
        "equity_curve": equity,
        "buy_and_hold_equity": bh_equity,
    }, index=data_df.index)
    meta = {
        "target_col": target_col,
        "target_ret_col": target_ret_col,
        "is_end": str(is_end.date()),
        "data_path": str(data_path.relative_to(REPO)),
        "signals_path": str(sig_path.relative_to(REPO)),
    }
    return out, meta


# ---------------------------------------------------------------------------
# Chart producers
# ---------------------------------------------------------------------------

def save_chart(pair: str, name: str, fig: go.Figure, rules_applied: list[str],
                alignment: str):
    out_dir = REPO / "output" / "charts" / pair / "plotly"
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{name}.json"
    pio.write_json(fig, p, pretty=False)
    meta = {
        "chart_name": name,
        "pair_id": pair,
        "palette_id": "v1",
        "rules_applied": rules_applied,
        "narrative_alignment_note": alignment,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "fix260526 W0.5 (Lead-as-Vera)",
    }
    (out_dir / f"{name}_meta.json").write_text(json.dumps(meta, indent=2))
    try:
        fig.write_image(str(out_dir / f"_perceptual_check_{name}.png"),
                        width=900, height=540, scale=1)
    except Exception:
        pass
    print(f"  wrote {p.relative_to(REPO)}")


def make_drawdown(pair: str, df: pd.DataFrame, w: dict):
    eq = df["equity_curve"].dropna()
    bh = df["buy_and_hold_equity"].dropna()
    dd_s = ((eq / eq.cummax()) - 1) * 100
    dd_b = ((bh / bh.cummax()) - 1) * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd_s.index, y=dd_s, name="Strategy",
                              line=dict(color="#d62728", width=1.4),
                              fill="tozeroy", fillcolor="rgba(214,39,40,0.15)"))
    fig.add_trace(go.Scatter(x=dd_b.index, y=dd_b, name=f"Buy & Hold",
                              line=dict(color="#888", width=1.0, dash="dot")))
    target = w.get("target_symbol", "TARGET")
    fig.update_layout(
        title=f"Strategy drawdown vs buy-and-hold ({target}) — full sample",
        xaxis=dict(title="Date"), yaxis=dict(title="Drawdown (%)"),
        template="plotly_white", height=420,
        legend=dict(orientation="h", y=-0.15),
    )
    save_chart(pair, "drawdown", fig,
               rules_applied=["VIZ-IC1"],
               alignment="Strategy vs Buy-and-Hold drawdown for Strategy Performance tab.")


def make_walk_forward(pair: str, df: pd.DataFrame, w: dict):
    oos_start = pd.Timestamp(w.get("oos_period_start", "2019-01-01"))
    sub = df.loc[oos_start:]
    # Rolling Sharpe window: 1y for monthly, 252d for daily
    if len(sub) > 800:
        window = 252; ann = 252
    else:
        window = 12; ann = 12
    ret = sub["strategy_return"].fillna(0)
    roll_mean = ret.rolling(window).mean() * ann
    roll_std = ret.rolling(window).std() * np.sqrt(ann)
    roll_sharpe = roll_mean / (roll_std + 1e-12)
    reported_sharpe = float(w.get("oos_sharpe", 0))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll_sharpe.index, y=roll_sharpe,
                              name=f"Strategy {window}-period rolling Sharpe",
                              line=dict(color="#2ca02c", width=1.4)))
    fig.add_hline(y=reported_sharpe, line=dict(color="#1f77b4", dash="dash"),
                   annotation_text=f"Reported OOS Sharpe = {reported_sharpe:.2f}")
    fig.add_hline(y=0, line=dict(color="#888", width=0.6, dash="dot"))
    fig.update_layout(
        title=f"Walk-forward: rolling Sharpe (OOS {oos_start.date()} onwards)",
        xaxis=dict(title="Date"), yaxis=dict(title="Annualized Sharpe ratio"),
        template="plotly_white", height=380,
    )
    save_chart(pair, "walk_forward", fig,
               rules_applied=["VIZ-IC1"],
               alignment="Rolling Sharpe over OOS — Strategy Confidence tab.")


def make_broker_trade_log(pair: str, df: pd.DataFrame, w: dict, meta: dict):
    """Emit one row per position change, broker-style.

    Follows the APP-TL1 column set used by hy_ig_v2_spy + gold_copper_xli:
    trade_date, side, instrument, quantity_pct, price, notional_usd,
    commission_bps, commission_usd, cum_pnl_pct, reason
    """
    out_path = REPO / "results" / pair / "winner_trades_broker_style.csv"
    starting_capital = 10000.0
    commission_bps = 5.0
    target = w.get("target_symbol") or meta["target_col"].upper()
    target_price_col = meta["target_col"]
    data_df = pd.read_parquet(REPO / meta["data_path"])
    price_series = data_df[target_price_col]

    pos = df["position"].fillna(0)
    delta = pos.diff().fillna(pos)
    change_idx = pos.index[delta != 0]
    if len(change_idx) == 0:
        # No transitions — write a single row noting the static position
        change_idx = pos.index[[0]]

    sig_col = w["signal_column"]
    sig_disp = w.get("signal_display_name", sig_col)
    direction = w.get("direction", "procyclical")
    fam = w.get("strategy_family", "P1_long_cash")

    cum_equity = starting_capital
    prev_dt = None
    rows = []
    for i, dt in enumerate(change_idx):
        new = float(pos.loc[dt])
        old = float(pos.shift(1).loc[dt]) if i > 0 else 0.0
        side = "BUY" if new > old else ("SELL" if new < old else "HOLD")
        qty_pct = abs(new - old) * 100.0
        notional = qty_pct * starting_capital / 100.0
        commission_usd = notional * commission_bps / 10000.0
        # Cumulative P&L using strategy_return between prev change and now
        if prev_dt is None:
            seg = df["strategy_return"].loc[:dt]
        else:
            seg = df["strategy_return"].loc[prev_dt:dt]
        cum_equity *= float((1 + seg.fillna(0)).prod())
        cum_pnl_pct = (cum_equity / starting_capital - 1) * 100.0
        prev_dt = dt
        try:
            sig_val = float(df[sig_col].loc[dt])
        except Exception:
            sig_val = float("nan")
        try:
            p = float(price_series.reindex(df.index).ffill().loc[dt])
        except Exception:
            p = float("nan")
        reason = (
            f"{fam}/{direction}: {sig_disp} = "
            f"{sig_val:.4f} — position {old*100:.0f}% -> {new*100:.0f}%"
        )
        rows.append({
            "trade_date": dt.strftime("%Y-%m-%d"),
            "side": side,
            "instrument": target,
            "quantity_pct": round(qty_pct, 4),
            "price": round(p, 4) if not np.isnan(p) else "",
            "notional_usd": round(notional, 2),
            "commission_bps": commission_bps,
            "commission_usd": round(commission_usd, 4),
            "cum_pnl_pct": round(cum_pnl_pct, 4),
            "reason": reason,
        })

    header_comment = (
        f"# Simulated trade record based on backtest signals. No real trades executed. "
        f"Starting capital: ${starting_capital:.0f}. Commission: {commission_bps:.0f} bps. "
        f"Pair: {pair}. Strategy: {fam} ({direction}). "
        f"Signal: {sig_disp}. Threshold rule: {w.get('threshold_rule')} (code {w.get('threshold_code')})."
    )
    with open(out_path, "w") as f:
        f.write(header_comment + "\n")
        pd.DataFrame(rows).to_csv(f, index=False)
    print(f"  wrote {out_path.relative_to(REPO)}  ({len(rows)} rows)")


# ---------------------------------------------------------------------------

def make_subperiod_sharpe(pair: str, df: pd.DataFrame, w: dict):
    """Re-derive sub-period Sharpe from the current strategy_return series,
    using each pair's commodity_ratio / activity / volatility episode bucket
    from episode_registry.json. Overwrites the legacy producer's CSV +
    chart (which showed empty bars labelled "(IS)" for several windows).
    """
    # Episode windows — load registry
    reg = json.loads((REPO / "docs/schemas/episode_registry.json").read_text())
    interp = json.loads((REPO / f"results/{pair}/interpretation_metadata.json").read_text())
    cat = interp.get("indicator_category") or interp.get("indicator_type") or "_fallback"
    entries = reg.get(cat)
    # Some buckets wrap entries under "episodes"
    if isinstance(entries, dict) and "episodes" in entries:
        entries = entries["episodes"]
    if not entries:
        entries = reg["_fallback"]

    oos_start = pd.Timestamp(w.get("oos_period_start", "2019-01-01"))
    oos_end = pd.Timestamp(w.get("oos_period_end", "2025-12-31"))

    ret = df["strategy_return"].dropna()
    is_daily = isinstance(ret.index, pd.DatetimeIndex) and len(ret) > 1000
    ann = 252 if is_daily else 12

    rows = []
    for ep in entries:
        s, e = pd.Timestamp(ep["start"]), pd.Timestamp(ep["end"])
        seg = ret.loc[s:e]
        if len(seg) < 3:
            rows.append({"period_name": ep["label"], "start_date": ep["start"],
                          "end_date": ep["end"], "is_oos": s >= oos_start,
                          "ann_return": np.nan, "ann_vol": np.nan,
                          "sharpe": np.nan, "n_obs": len(seg),
                          "max_drawdown": np.nan})
            continue
        ann_ret = (1 + seg).prod() ** (ann / max(len(seg), 1)) - 1
        ann_vol = seg.std() * np.sqrt(ann)
        sharpe = (seg.mean() * ann) / (seg.std() * np.sqrt(ann) + 1e-12)
        eq = (1 + seg).cumprod()
        mdd = ((eq / eq.cummax()) - 1).min()
        rows.append({
            "period_name": ep["label"],
            "start_date": ep["start"], "end_date": ep["end"],
            "is_oos": s >= oos_start,
            "ann_return": round(float(ann_ret), 4),
            "ann_vol": round(float(ann_vol), 4),
            "sharpe": round(float(sharpe), 4),
            "n_obs": int(len(seg)),
            "max_drawdown": round(float(mdd), 4),
        })
    # Full OOS row
    seg_oos = ret.loc[oos_start:oos_end]
    if len(seg_oos) >= 3:
        ann_ret = (1 + seg_oos).prod() ** (ann / max(len(seg_oos), 1)) - 1
        ann_vol = seg_oos.std() * np.sqrt(ann)
        sharpe = (seg_oos.mean() * ann) / (seg_oos.std() * np.sqrt(ann) + 1e-12)
        eq = (1 + seg_oos).cumprod()
        mdd = ((eq / eq.cummax()) - 1).min()
        rows.append({"period_name": "Full OOS",
                      "start_date": str(oos_start.date()),
                      "end_date": str(oos_end.date()),
                      "is_oos": True,
                      "ann_return": round(float(ann_ret), 4),
                      "ann_vol": round(float(ann_vol), 4),
                      "sharpe": round(float(sharpe), 4),
                      "n_obs": int(len(seg_oos)),
                      "max_drawdown": round(float(mdd), 4)})
    out_csv = REPO / f"results/{pair}/subperiod_sharpe.csv"
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"  wrote {out_csv.relative_to(REPO)}  ({len(rows)} rows)")

    # Chart — distinguish three states:
    #   (a) NaN sharpe AND n_obs < 3       → "no data" (period outside coverage)
    #   (b) sharpe == 0 AND position never moved → "stayed in cash" (long-cash strategy)
    #   (c) real sharpe                    → coloured bar
    labels, values, colors, texts = [], [], [], []
    for r in rows:
        ep_label = r["period_name"] + (" (IS)" if not r["is_oos"] else " (OOS)")
        s, e = pd.Timestamp(r["start_date"]), pd.Timestamp(r["end_date"])
        seg_pos = df["position"].loc[s:e]
        n = r["n_obs"]
        sharpe = r["sharpe"]
        if isinstance(sharpe, float) and np.isnan(sharpe):
            # No coverage at all
            labels.append(f"{ep_label}\n(no data)")
            values.append(0)
            colors.append("#cccccc")
            texts.append("no data")
        elif n >= 3 and float(seg_pos.abs().sum()) == 0 and abs(sharpe) < 1e-9:
            labels.append(f"{ep_label}\n(in cash)")
            values.append(0)
            colors.append("#dddddd")
            texts.append("cash")
        else:
            labels.append(ep_label)
            values.append(sharpe)
            colors.append("#2ca02c" if sharpe >= 0 else "#d62728")
            texts.append(f"{sharpe:+.2f}")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values, marker_color=colors,
                          text=texts, textposition="outside"))
    fig.add_hline(y=0, line=dict(color="#888", width=0.6, dash="dot"))
    fig.update_layout(
        title=f"Sub-period Sharpe — {pair} (IS = in-sample / OOS = out-of-sample)",
        xaxis=dict(title="Historical episode"),
        yaxis=dict(title="Annualized Sharpe ratio"),
        template="plotly_white", height=420,
        margin=dict(b=120),
    )
    save_chart(pair, "subperiod_sharpe", fig,
               rules_applied=["VIZ-CP1.1", "VIZ-IC1"],
               alignment=("Sub-period Sharpe with explicit 'no data' (no coverage) "
                           "vs 'cash' (long-cash strategy was in cash through the "
                           "episode) labels — distinguishes the two zero-bar cases "
                           "the reviewer flagged as ambiguous."))


def run(pair: str):
    print(f"\n=== {pair} ===")
    w = load_winner_with_threshold(pair)
    df, meta = make_strategy_returns(pair, w)
    print(f"  signal+position derived: shape={df.shape}  position transitions={int((df['position'].diff().abs() > 0).sum())}")
    make_drawdown(pair, df, w)
    make_walk_forward(pair, df, w)
    make_broker_trade_log(pair, df, w, meta)
    make_subperiod_sharpe(pair, df, w)


if __name__ == "__main__":
    pairs = sys.argv[1:] or ["indpro_spy", "vix_vix3m_spy"]
    for p in pairs:
        run(p)
