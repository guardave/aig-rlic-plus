#!/usr/bin/env python3
"""permit_spy — Option-B trade-log regenerator.

Why this script exists
======================
The committed `winner_trade_log.csv` for `permit_spy` carries 13 phantom
zero-return trades from 1990-01 to 1992-10. Cause: the canonical
generator (`scripts/generate_winner_outputs.py`) does
`cum_ret = (1 + strat_ret.fillna(0)).cumprod()` on a strategy-return
series whose SPY input is NaN before SPY ETF inception (1993-01-29).
NaN coerced to 0 → 0% returns emitted as real trades.

Rather than modify the shared generator (which would change behaviour
for every pair), this permit-specific helper:

  - Reads the SIGNAL column (`permit_mom1m`) from the existing
    `signals_20260423.parquet` — the April-2026 vintage that the
    committed tournament was scored against. This keeps the trade log
    consistent with the leaderboard, OOS Sharpe, MaxDD, etc.
  - Reads the SPY price column from the freshly rebuilt master parquet
    (`data/permit_spy_monthly_20260605.parquet`). SPY adjusted closes
    are point-in-time immutable, so vendor swap is clean.
  - Gates trade emission on `spy.first_valid_index()` so no row is
    written for months where SPY had no price.
  - Emits the diagnostic columns the requestor (土撥鼠 #94) asked for:
    `signal_value`, `threshold_value`, `threshold_comparison`,
    `regime_tag`.
  - Also emits `winner_trades_broker_style.csv` in the schema used by
    other monthly P3 pairs (e.g. indpro_xlp), to suppress the missing-
    broker-log warning on the Strategy page.

The vintage seam between signal and price is documented in
`docs/data_vintage_note_permit_spy.md`.

Usage
-----
    python3 scripts/regen_permit_trade_log.py

Prerequisite
------------
The master parquet `data/permit_spy_monthly_*.parquet` must exist on
disk. It is gitignored, so a fresh clone of this repo will not have it.
Restore it via the data-refresh helper documented in
`docs/data_vintage_note_permit_spy.md` (FRED for indicators, mqr_datalayer
for SPY). Without it this script raises FileNotFoundError immediately.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
PAIR_ID = "permit_spy"
PAIR_DIR = REPO_ROOT / "results" / PAIR_ID
DATA_DIR = REPO_ROOT / "data"

STARTING_CAPITAL = 10000.0
COMMISSION_BPS = 5
INSTRUMENT = "SPY"


def load_winner_summary() -> dict:
    with open(PAIR_DIR / "winner_summary.json") as fh:
        return json.load(fh)


def load_signal_series(signal_column: str) -> pd.Series:
    """Vintage-pinned signal: read from the April-2026 signals parquet."""
    parquet = sorted(PAIR_DIR.glob("signals_*.parquet"))[-1]
    df = pd.read_parquet(parquet)
    if signal_column not in df.columns:
        raise KeyError(
            f"signal column {signal_column!r} not in {parquet.name}; "
            f"available: {list(df.columns)}"
        )
    s = df[signal_column].copy()
    s.index = pd.DatetimeIndex(s.index)
    return s


def load_spy_series() -> pd.Series:
    """Current-vintage SPY adjusted close from the rebuilt master parquet."""
    candidates = sorted(DATA_DIR.glob(f"{PAIR_ID}_monthly_*.parquet"))
    if not candidates:
        raise FileNotFoundError(
            f"No master parquet found at {DATA_DIR}/{PAIR_ID}_monthly_*.parquet. "
            "Rebuild via /tmp/refresh_permit_master.py (see "
            "docs/data_vintage_note_permit_spy.md)."
        )
    master = candidates[-1]
    df = pd.read_parquet(master)
    if "spy" not in df.columns:
        raise KeyError(f"'spy' column missing from {master.name}")
    s = df["spy"].copy()
    s.index = pd.DatetimeIndex(s.index)
    return s


def in_sample_threshold(signal: pd.Series, oos_start: pd.Timestamp,
                        percentile: int) -> float:
    """T1_pXX: fixed in-sample percentile threshold."""
    is_window = signal.loc[:oos_start - pd.offsets.Day(1)].dropna()
    return float(is_window.quantile(percentile / 100))


def regime_tag_from_signal(value: float, threshold: float) -> str:
    """Classify a single-month signal value relative to threshold."""
    if pd.isna(value):
        return "no-signal"
    diff = value - threshold
    if diff >= 1.5:
        return "strong-bullish"
    if diff >= 0:
        return "bullish"
    if diff >= -1.5:
        return "bearish"
    return "strong-bearish"


def build_trade_log(winner: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (winner_trade_log_df, broker_style_df)."""
    signal_col = winner["signal_column"]              # permit_mom1m
    threshold_code = winner["threshold_code"]         # T1_p25
    direction = winner["direction"]                   # procyclical
    strategy_family = winner["strategy_family"]       # P3_long_short
    lead_months = int(winner["lead_value"])           # 6
    oos_start = pd.Timestamp(winner["oos_period_start"])  # 2018-01-01

    signal = load_signal_series(signal_col)
    spy = load_spy_series()

    # Align both series on the union of month-end dates (signals parquet
    # is monthly; master is monthly).
    idx = signal.index.union(spy.index).sort_values()
    signal = signal.reindex(idx)
    spy = spy.reindex(idx)
    spy_ret = spy.pct_change()

    # ------ Threshold ------
    if not threshold_code.startswith("T1_p"):
        raise NotImplementedError(
            f"Threshold {threshold_code!r} not implemented in this helper "
            "(only T1_pXX). Extend if a different threshold ever wins."
        )
    pct = int(threshold_code.split("p")[1])
    threshold_val = in_sample_threshold(signal, oos_start, pct)
    print(f"  T1_p{pct} fixed threshold (1990-01..2017-12): {threshold_val:+.4f}")

    # ------ Apply lead ------
    # Position at month t uses signal value from month t - lead_months.
    leaded_signal = signal.shift(lead_months)

    # ------ Bullish condition ------
    counter = direction.startswith("counter")
    if counter:
        bullish = leaded_signal < threshold_val
    else:
        bullish = leaded_signal > threshold_val

    # ------ Position ------
    if strategy_family.startswith("P1"):
        position = bullish.astype(float)               # 0 or 1
    elif strategy_family.startswith("P3"):
        position = bullish.astype(float) * 2 - 1       # -1 or +1
    elif strategy_family.startswith("P2"):
        # Not used by permit_spy winner; kept for completeness.
        smin = leaded_signal.rolling(60, min_periods=48).min()
        smax = leaded_signal.rolling(60, min_periods=48).max()
        scale = (leaded_signal - smin) / (smax - smin).replace(0, np.nan)
        position = (1 - scale).clip(0, 1) if counter else scale.clip(0, 1)
    else:
        raise NotImplementedError(f"strategy_family={strategy_family!r}")

    # ------ THE FIX (item 96): gate strategy returns on SPY availability ------
    spy_first_valid = spy.first_valid_index()
    spy_avail = spy.notna()                            # True iff SPY had a price
    strat_ret = (position.shift(1) * spy_ret).where(spy_avail)
    # Compound only from the first month that has both a price AND a position.
    cum_start = strat_ret.first_valid_index()
    if cum_start is None:
        raise RuntimeError("No valid strategy-return observations.")
    print(f"  SPY first valid: {spy_first_valid.date()} | "
          f"strategy-return first valid: {cum_start.date()}")

    cum_ret = (1 + strat_ret.loc[cum_start:].fillna(0)).cumprod()

    # ------ Identify discrete trades (position changes) ------
    pos_clean = position.dropna()
    # Skip any pre-cum-start position values.
    pos_clean = pos_clean.loc[cum_start:]
    pos_change = pos_clean.diff().fillna(pos_clean.iloc[0] if len(pos_clean) else 0)
    trade_entries = pos_change[pos_change != 0].index

    if len(trade_entries) < 2:
        raise RuntimeError("Fewer than 2 position transitions found.")

    rows: list[dict] = []
    for i, entry_date in enumerate(trade_entries):
        exit_date = (trade_entries[i + 1]
                     if i + 1 < len(trade_entries)
                     else cum_ret.index[-1])

        entry_pos = position.loc[entry_date]
        if entry_pos > 0:
            direction_label = "Long"
        elif entry_pos < 0:
            direction_label = "Short"
        else:
            direction_label = "Cash"

        holding_days = (exit_date - entry_date).days

        entry_cum = cum_ret.loc[:entry_date].iloc[-1]
        exit_cum = cum_ret.loc[:exit_date].iloc[-1]
        trade_ret = (exit_cum / entry_cum - 1) if entry_cum != 0 else 0.0

        sig_val = leaded_signal.loc[entry_date]
        regime = regime_tag_from_signal(sig_val, threshold_val)
        cmp_str = f"{sig_val:+.4f} > {threshold_val:+.4f}" if not pd.isna(sig_val) and sig_val > threshold_val \
            else f"{sig_val:+.4f} <= {threshold_val:+.4f}"

        rows.append({
            "entry_date": entry_date.strftime("%Y-%m-%d"),
            "exit_date": exit_date.strftime("%Y-%m-%d"),
            "direction": direction_label,
            "holding_days": holding_days,
            "trade_return_pct": round(trade_ret * 100, 2),
            "signal_value": round(float(sig_val), 4) if not pd.isna(sig_val) else None,
            "threshold_value": round(threshold_val, 4),
            "threshold_comparison": cmp_str,
            "regime_tag": regime,
        })

    log_df = pd.DataFrame(rows)

    # ------ Broker-style CSV (mirror schema of indpro_xlp) ------
    broker_rows: list[dict] = []
    cum_pnl_pct = 0.0
    for i, r in enumerate(rows):
        entry_dt = pd.Timestamp(r["entry_date"])
        # Always emit a BUY row at the start of a position.
        if r["direction"] in ("Long", "Short"):
            qty = 100.0
            side = "BUY" if r["direction"] == "Long" else "SELL"
            price = float(spy.loc[entry_dt]) if entry_dt in spy.index and not pd.isna(spy.loc[entry_dt]) else None
            notional = STARTING_CAPITAL
            commission_usd = round(notional * COMMISSION_BPS / 10000.0, 4)
            cum_pnl_pct = round(((cum_ret.loc[entry_dt] - 1) * 100), 4) if entry_dt in cum_ret.index else 0.0
            broker_rows.append({
                "trade_date": r["entry_date"],
                "side": side,
                "instrument": INSTRUMENT,
                "quantity_pct": qty,
                "price": price,
                "notional_usd": notional,
                "commission_bps": COMMISSION_BPS,
                "commission_usd": commission_usd,
                "cum_pnl_pct": cum_pnl_pct,
                "reason": (
                    f"P3_long_short/procyclical: 1-Month Momentum (lead 6m) = "
                    f"{r['signal_value']} (threshold {r['threshold_value']}) — "
                    f"{'enter long' if r['direction']=='Long' else 'enter short'} {INSTRUMENT}"
                ),
            })
    broker_df = pd.DataFrame(broker_rows)

    return log_df, broker_df


def main() -> None:
    print(f"=== Regenerating {PAIR_ID} trade log (Option B) ===\n")
    winner = load_winner_summary()
    log_df, broker_df = build_trade_log(winner)

    log_path = PAIR_DIR / "winner_trade_log.csv"
    log_df.to_csv(log_path, index=False)
    print(f"\n  WROTE -> {log_path} ({len(log_df)} rows)")
    if len(log_df):
        print(f"  first trade entry: {log_df['entry_date'].iloc[0]}")
        print(f"  last trade exit  : {log_df['exit_date'].iloc[-1]}")
        zero_count = (log_df["trade_return_pct"] == 0.0).sum()
        print(f"  zero-return rows : {zero_count} (target: 0)")

    broker_path = PAIR_DIR / "winner_trades_broker_style.csv"
    header_comment = (
        f"# Simulated trade record based on backtest signals. No real trades "
        f"executed. Starting capital: ${STARTING_CAPITAL:,.0f}. Commission: "
        f"{COMMISSION_BPS} bps. Pair: {PAIR_ID}. Strategy: "
        f"{winner['strategy_family']} ({winner['direction']}). Signal: "
        f"{winner['signal_display_name']} (lead {winner['lead_description']}). "
        f"Source: winner_trade_log.csv. See "
        f"docs/data_vintage_note_permit_spy.md.\n"
    )
    with open(broker_path, "w") as fh:
        fh.write(header_comment)
        broker_df.to_csv(fh, index=False)
    print(f"  WROTE -> {broker_path} ({len(broker_df)} rows)")


if __name__ == "__main__":
    main()
