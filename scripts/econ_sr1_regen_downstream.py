#!/usr/bin/env python3
"""ECON-SR1 round 2: regenerate the defective downstream NON-CHART artifacts
for vix_vix3m_spy / indpro_spy / indpro_xlp from the reconciled canonical
strategy series (results/{pair}/strategy_returns_20260611.csv).

Per ECON-SR1 §3 ("one series, many consumers") this script ONLY consumes the
canonical CSV — it never re-derives positions from signal/threshold logic.

Regenerates:
  1. results/{pair}/subperiod_sharpe.csv
       - episode rows: same period_name/start_date/end_date structure as the
         previous file (episode set unchanged); metrics recomputed.
       - Full OOS row: window taken from the (corrected) winner_summary
         oos_period_start/oos_period_end; Full-OOS sharpe + max_drawdown are
         verified against winner_summary headline (±0.01 / ±0.5pp).
       - ann_return per row is GEOMETRIC (legacy producer convention,
         unchanged); winner_summary oos_ann_return is ARITHMETIC mean×ann —
         both are printed in the verification block.
  2. results/{pair}/winner_trades_broker_style.csv
       - APP-TL1 schema via the established _trade_log_broker conventions
         (BUY/SELL on position change, quantity_pct = target weight,
         cum_pnl_pct from the canonical strategy_return).
  3. results/indpro_xlp/winner_trade_log.csv
       - the on-disk log was NOT the tournament winner (long/cash series,
         OOS Sharpe 0.6352 vs winner 1.1147 — ECON-SR1 round-1 finding).
         Regenerated in the standard span shape (entry_date, exit_date,
         direction, holding_days, trade_return_pct) from the canonical
         series; the wrong-combo log is preserved as
         winner_trade_log_superseded_20260611.csv.

Position semantics reminder: in strategy_returns_{date}.csv, `position` on
row t is the return-accrual weight for period t (execution lag already
applied). Broker/trade events are therefore stamped on the first period
whose return accrues at the new weight — the same convention as the
existing monthly broker logs built by _trade_log_broker.py.

Author: Evan (Econometrics Agent) — fix260611_meta_cmp round 2
"""
from __future__ import annotations

import glob
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _trade_log_broker import _reason_string  # noqa: E402  (established APP-TL1 helper)

REPO = Path("/workspaces/aig-rlic-plus")
DATE_TAG = "20260611"

PAIRS = {
    "vix_vix3m_spy": {"master": "data/vix_vix3m_spy_daily_20260314.parquet",
                       "price_col": "spy", "ann": 252},
    "indpro_spy": {"master": "data/indpro_spy_monthly_19900101_20251231.parquet",
                    "price_col": "spy", "ann": 12},
    "indpro_xlp": {"master": "data/indpro_xlp_monthly_19980101_20251231.parquet",
                    "price_col": "xlp", "ann": 12},
}


def load_canonical(pair: str) -> pd.DataFrame:
    p = REPO / "results" / pair / f"strategy_returns_{DATE_TAG}.csv"
    df = pd.read_csv(p, parse_dates=["date"]).set_index("date").sort_index()
    # Integrity gate: canonical invariant
    resid = (df["strategy_return"] - df["position"] * df["bh_return"]).abs().max()
    assert resid < 1e-9, f"{pair}: canonical series violates position*bh_return invariant"
    return df


def load_winner(pair: str) -> dict:
    return json.loads((REPO / "results" / pair / "winner_summary.json").read_text())


def seg_metrics(seg: pd.Series, ann: int) -> dict:
    if len(seg) < 3:
        return {"ann_return": np.nan, "ann_vol": np.nan, "sharpe": np.nan,
                "n_obs": len(seg), "max_drawdown": np.nan}
    ann_ret = (1 + seg).prod() ** (ann / max(len(seg), 1)) - 1
    ann_vol = seg.std() * np.sqrt(ann)
    sharpe = (seg.mean() * ann) / (seg.std() * np.sqrt(ann) + 1e-12)
    eq = (1 + seg).cumprod()
    mdd = ((eq / eq.cummax()) - 1).min()
    return {"ann_return": round(float(ann_ret), 4), "ann_vol": round(float(ann_vol), 4),
            "sharpe": round(float(sharpe), 4), "n_obs": int(len(seg)),
            "max_drawdown": round(float(mdd), 4)}


# ── 1. subperiod_sharpe.csv ─────────────────────────────────────────────────

def regen_subperiod(pair: str, df: pd.DataFrame, w: dict, ann: int) -> None:
    csv_path = REPO / "results" / pair / "subperiod_sharpe.csv"
    old = pd.read_csv(csv_path)
    episodes = old[old["period_name"] != "Full OOS"][
        ["period_name", "start_date", "end_date"]].to_dict("records")

    oos_start = pd.Timestamp(w["oos_period_start"])
    oos_end = pd.Timestamp(w["oos_period_end"])
    ret = df["strategy_return"]

    rows = []
    for ep in episodes:
        s, e = pd.Timestamp(ep["start_date"]), pd.Timestamp(ep["end_date"])
        m = seg_metrics(ret.loc[s:e], ann)
        rows.append({"period_name": ep["period_name"], "start_date": ep["start_date"],
                      "end_date": ep["end_date"], "is_oos": bool(s >= oos_start), **m})
    seg_oos = ret.loc[oos_start:oos_end]
    m = seg_metrics(seg_oos, ann)
    rows.append({"period_name": "Full OOS", "start_date": str(oos_start.date()),
                  "end_date": str(oos_end.date()), "is_oos": True, **m})
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"  wrote {csv_path.relative_to(REPO)}  ({len(rows)} rows)")

    # Verification: Full-OOS row vs winner_summary headline
    sharpe_diff = m["sharpe"] - float(w["oos_sharpe"])
    mdd_diff = m["max_drawdown"] - float(w["oos_max_drawdown"])
    arith_ann = float(seg_oos.mean() * ann)
    print(f"  CHECK Full-OOS sharpe {m['sharpe']:.4f} vs winner_summary "
          f"{w['oos_sharpe']:.4f} (diff {sharpe_diff:+.4f}, tol 0.01) -> "
          f"{'PASS' if abs(sharpe_diff) <= 0.01 else 'FAIL'}")
    print(f"  CHECK Full-OOS max_drawdown {m['max_drawdown']:.4f} vs "
          f"{w['oos_max_drawdown']:.4f} (diff {mdd_diff:+.4f}, tol 0.005) -> "
          f"{'PASS' if abs(mdd_diff) <= 0.005 else 'FAIL'}")
    print(f"  NOTE ann_return row={m['ann_return']:.4f} is geometric (legacy row "
          f"convention); arithmetic mean×{ann} = {arith_ann:.4f} vs winner_summary "
          f"{w['oos_ann_return']:.4f} (diff {arith_ann - float(w['oos_ann_return']):+.4f})")
    if abs(sharpe_diff) > 0.01 or abs(mdd_diff) > 0.005:
        raise SystemExit(f"ECON-SR1 verification FAILED for {pair} subperiod Full-OOS row")


# ── 2. winner_trades_broker_style.csv ───────────────────────────────────────

def _signal_series(pair: str, w: dict, index: pd.DatetimeIndex):
    """Best-effort signal values for reason annotation (NaN if unresolvable).

    ECON-T5 §4 (read-only): this helper opens only signals_*.parquet and the
    master parquet, strictly READ-ONLY (pd.read_parquet), and NEVER writes or
    appends to any tournament_results_*.csv. It does not touch the publish-time
    tournament grid. Confirmed non-mutating by the 2026-06-20 provenance audit.
    """
    sig_col = w.get("signal_column")
    if not sig_col:
        return None
    for cand in sorted(glob.glob(str(REPO / "results" / pair / "signals_*.parquet"))) \
                + [str(REPO / PAIRS[pair]["master"])]:
        try:
            sdf = pd.read_parquet(cand)
            if sig_col in sdf.columns:
                return sdf[sig_col].reindex(index, method="ffill")
        except Exception:
            continue
    return None


def regen_broker(pair: str, df: pd.DataFrame, w: dict,
                  commission_bps: int = 5, starting_capital: float = 10_000.0,
                  epsilon: float = 1e-9) -> None:
    """APP-TL1 broker-style CSV from the canonical series. Mirrors the
    emission loop of _trade_log_broker.synthesize_from_position_log, with the
    canonical strategy_returns CSV as the position log."""
    cfg = PAIRS[pair]
    instrument = w.get("target_symbol") or cfg["price_col"].upper()
    strategy = w.get("strategy_family", w.get("strategy_code", "P?"))
    direction = w.get("direction", "unknown")
    signal_display = w.get("signal_display_name") or w.get("signal_code", "signal")

    prices = pd.read_parquet(REPO / cfg["master"])[cfg["price_col"]] \
        .reindex(df.index).ffill()
    sig_series = _signal_series(pair, w, df.index)
    cum_ret = (1.0 + df["strategy_return"].fillna(0)).cumprod() - 1.0

    rows = []
    last_pos = 0.0
    dates = list(df.index)
    for i, date in enumerate(dates):
        new_pos = float(df.loc[date, "position"])
        is_first_emit = (last_pos == 0.0 and new_pos != 0.0 and not rows)
        is_last = (i == len(dates) - 1)
        delta = new_pos - last_pos
        emit = is_first_emit or abs(delta) > epsilon or (is_last and new_pos != last_pos)
        if not emit:
            continue
        side = "BUY" if new_pos > last_pos else ("SELL" if new_pos < last_pos else "HOLD")
        qty_pct = new_pos * 100.0
        price = float(prices.loc[date]) if not pd.isna(prices.loc[date]) else float("nan")
        notional = abs(qty_pct) / 100.0 * starting_capital
        commission_usd = notional * commission_bps / 10_000.0
        sv = (float(sig_series.loc[date])
              if sig_series is not None and not pd.isna(sig_series.loc[date])
              else float("nan"))
        rows.append({
            "trade_date": date.strftime("%Y-%m-%d"),
            "side": side,
            "instrument": instrument,
            "quantity_pct": round(qty_pct, 4),
            "price": round(price, 4) if not pd.isna(price) else np.nan,
            "notional_usd": round(notional, 2),
            "commission_bps": int(commission_bps),
            "commission_usd": round(commission_usd, 4),
            "cum_pnl_pct": round(float(cum_ret.loc[date]) * 100.0, 4),
            "reason": _reason_string(signal_display, sv, new_pos, last_pos,
                                      strategy, direction),
        })
        last_pos = new_pos

    out_path = REPO / "results" / pair / "winner_trades_broker_style.csv"
    header = (f"# Simulated trade record based on backtest signals. No real trades "
              f"executed. Starting capital: ${starting_capital:,.0f}. Commission: "
              f"{commission_bps} bps. Pair: {pair}. Strategy: {strategy} ({direction}). "
              f"Signal: {signal_display}. Source: strategy_returns_{DATE_TAG}.csv "
              f"(ECON-SR1 reconciled canonical series).\n")
    with open(out_path, "w") as f:
        f.write(header)
        pd.DataFrame(rows).to_csv(f, index=False)
    print(f"  wrote {out_path.relative_to(REPO)}  ({len(rows)} rows, "
          f"final cum P&L {rows[-1]['cum_pnl_pct']:.2f}%)")


# ── 3. indpro_xlp winner_trade_log.csv (span shape) ─────────────────────────

def regen_xlp_trade_log(df: pd.DataFrame) -> None:
    pair_dir = REPO / "results" / "indpro_xlp"
    src = pair_dir / "winner_trade_log.csv"
    superseded = pair_dir / f"winner_trade_log_superseded_{DATE_TAG}.csv"
    if not superseded.exists():
        shutil.copy2(src, superseded)
        print(f"  preserved wrong-combo log -> {superseded.relative_to(REPO)}")

    # Decision-time positions: accrual weight at t was decided at t-1.
    decision = df["position"].shift(-1)
    decision.iloc[-1] = df["position"].iloc[-1]  # carry last weight
    change = decision.ne(decision.shift(1))
    change.iloc[0] = True
    span_starts = list(decision.index[change])

    cum = (1.0 + df["strategy_return"].fillna(0)).cumprod()
    trades = []
    for i, entry in enumerate(span_starts):
        exit_ = span_starts[i + 1] if i + 1 < len(span_starts) else df.index[-1]
        pos = float(decision.loc[entry])
        if not trades and pos == 0.0:
            continue  # skip leading flat warm-up before the first real position
        direction = "Long" if pos > 0 else ("Short" if pos < 0 else "Cash")
        # Returns accrue on (entry, exit] under the decision/accrual convention
        trade_ret = float(cum.loc[exit_] / cum.loc[entry] - 1.0)
        trades.append({
            "entry_date": entry.strftime("%Y-%m-%d"),
            "exit_date": exit_.strftime("%Y-%m-%d"),
            "direction": direction,
            "holding_days": (exit_ - entry).days,
            "trade_return_pct": round(trade_ret * 100, 2),
        })
    pd.DataFrame(trades).to_csv(src, index=False)
    print(f"  wrote {src.relative_to(REPO)}  ({len(trades)} trades, span shape)")

    # Verification: compounded trade returns must reproduce the series total
    total_from_trades = np.prod([1 + t["trade_return_pct"] / 100 for t in trades]) - 1
    first_entry = pd.Timestamp(trades[0]["entry_date"])
    total_from_series = float(cum.iloc[-1] / cum.loc[first_entry] - 1.0)
    print(f"  CHECK compounded trade returns {total_from_trades:+.4f} vs series "
          f"total {total_from_series:+.4f} (rounding-level diff "
          f"{total_from_trades - total_from_series:+.4f})")


if __name__ == "__main__":
    for pair, cfg in PAIRS.items():
        print(f"\n=== {pair} ===")
        df = load_canonical(pair)
        w = load_winner(pair)
        regen_subperiod(pair, df, w, cfg["ann"])
        regen_broker(pair, df, w)
        if pair == "indpro_xlp":
            regen_xlp_trade_log(df)
    print("\nDone.")
