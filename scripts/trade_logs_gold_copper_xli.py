#!/usr/bin/env python3
"""
Trade Log Generation: gold_copper_xli (APP-TL1)

Produces the two CSVs the Strategy page expects:
  results/{pair_id}/winner_trades_broker_style.csv  (user-facing)
  results/{pair_id}/winner_trade_log.csv            (researcher)

Reads the signals parquet + winner_summary.json, derives position
changes from the position column, formats each change as a broker-
style execution row and as a position-log row.
"""

import os, json, time
import numpy as np
import pandas as pd

PAIR_ID = "gold_copper_xli"
DATE_TAG = "20260526"
BASE = "/workspaces/aig-rlic-plus"
RESULTS = os.path.join(BASE, "results", PAIR_ID)
DATA = os.path.join(BASE, "data", f"{PAIR_ID}_daily_{DATE_TAG}.parquet")

SIGNALS = os.path.join(RESULTS, f"signals_{DATE_TAG}.parquet")
WINNER = os.path.join(RESULTS, "winner_summary.json")

BROKER_PATH = os.path.join(RESULTS, "winner_trades_broker_style.csv")
LOG_PATH = os.path.join(RESULTS, "winner_trade_log.csv")


def main():
    sig = pd.read_parquet(SIGNALS)
    raw = pd.read_parquet(DATA)
    with open(WINNER) as f:
        w = json.load(f)
    pos = sig["position"].fillna(0)
    raw_sig = sig["signal_raw"].fillna(method="ffill")
    price = raw["xli"].reindex(sig.index).ffill()
    threshold = float(w["threshold_value"])
    direction = w["direction"]
    strategy_code = w.get("strategy_code", "P1")
    family = w.get("strategy_family", "P1_long_cash")
    signal_disp = w.get("signal_display_name", w.get("signal_column", "signal"))
    target_symbol = w.get("target_symbol", "XLI")
    starting_capital = 10000.0
    commission_bps = 5.0

    # Identify position changes
    prev_pos = pos.shift(1).fillna(0)
    delta = pos - prev_pos
    change_idx = pos.index[delta != 0]
    print(f"position changes: {len(change_idx)}  pos value range: {pos.min()} -> {pos.max()}")

    # Broker-style rows
    broker_rows = []
    log_rows = []
    last_long_entry = None  # (date, price)
    cum_pnl_pct = 0.0
    cum_equity = starting_capital
    prev_position_value = 0.0

    for i, dt in enumerate(change_idx):
        new = float(pos.loc[dt])
        old = float(prev_pos.loc[dt])
        p = float(price.loc[dt]) if pd.notna(price.loc[dt]) else float("nan")
        s_val = float(raw_sig.loc[dt]) if pd.notna(raw_sig.loc[dt]) else float("nan")

        side = "BUY" if new > old else "SELL"
        qty_pct = abs(new - old) * 100.0  # position in % scale
        # notional in $ (treat position as fraction of starting capital for log)
        notional = qty_pct * starting_capital / 100.0
        commission_usd = notional * commission_bps / 10000.0

        # cum P&L update — track equity through strategy_return
        # We use the actual strategy_return from the signals parquet between
        # the prior change and this one to get a faithful cum_pnl.
        if i == 0:
            seg = sig["strategy_return"].loc[:dt]
        else:
            prev_dt = change_idx[i - 1]
            seg = sig["strategy_return"].loc[prev_dt:dt]
        cum_equity *= float((1 + seg.fillna(0)).prod())
        cum_pnl_pct = (cum_equity / starting_capital - 1) * 100.0

        # reason text
        reason = (
            f"{strategy_code}/{direction}: {signal_disp} = "
            f"{s_val:.3f} (threshold {threshold:.3f}) — "
            f"position {old*100:.1f}% → {new*100:.1f}%"
        )

        broker_rows.append({
            "trade_date": dt.strftime("%Y-%m-%d"),
            "side": side,
            "instrument": target_symbol,
            "quantity_pct": round(qty_pct, 4),
            "price": round(p, 4) if not np.isnan(p) else "",
            "notional_usd": round(notional, 2),
            "commission_bps": commission_bps,
            "commission_usd": round(commission_usd, 4),
            "cum_pnl_pct": round(cum_pnl_pct, 4),
            "reason": reason,
        })

        # Researcher / position-log row: one row per position-weight change
        log_rows.append({
            "change_date": dt.strftime("%Y-%m-%d"),
            "from_pct": round(old * 100.0, 4),
            "to_pct": round(new * 100.0, 4),
            "delta_pct": round((new - old) * 100.0, 4),
            "side": side,
            "price": round(p, 4) if not np.isnan(p) else "",
            "signal_value": round(s_val, 4) if not np.isnan(s_val) else "",
            "threshold": threshold,
            "cum_pnl_pct": round(cum_pnl_pct, 4),
        })

    # Write broker-style CSV with comment header
    header_comment = (
        f"# Simulated trade record based on backtest signals. No real trades executed. "
        f"Starting capital: ${starting_capital:.0f}. Commission: {commission_bps:.0f} bps. "
        f"Pair: {PAIR_ID}. Strategy: {strategy_code} ({family}, {direction}). "
        f"Signal: {signal_disp}. Threshold rule: {w.get('threshold_rule')} {threshold:.4f}."
    )
    with open(BROKER_PATH, "w") as f:
        f.write(header_comment + "\n")
        pd.DataFrame(broker_rows).to_csv(f, index=False)
    print(f"wrote {BROKER_PATH}  ({len(broker_rows)} rows)")

    pd.DataFrame(log_rows).to_csv(LOG_PATH, index=False)
    print(f"wrote {LOG_PATH}  ({len(log_rows)} rows)")


if __name__ == "__main__":
    main()
