"""
Shared helper: build a broker-style discrete trade log from a pair's
existing `winner_trade_log.csv` + master parquet, for monthly-frequency
pairs whose position log is already emitted by the pipeline.

Complements `scripts/synthesize_broker_trade_log.py`, which replays the
daily HY-IG-family tournament winner from scratch. This helper takes a
simpler path: trust the pipeline's already-shipped `winner_trade_log.csv`
as source of truth for positions and derive broker-style trade events
directly. Appropriate for pairs whose position log is the canonical
backtest output (e.g. monthly macro-to-sector pairs).

Output columns (APP-TL1 schema):
    trade_date, side, instrument, quantity_pct, price,
    notional_usd, commission_bps, commission_usd, cum_pnl_pct, reason

CSV header is a single `#`-prefixed metadata row so consumers can read
with `pd.read_csv(path, comment="#")`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RESULTS_ROOT = REPO_ROOT / "results"


def _find_monthly_parquet(pair_id: str) -> Path:
    cands = sorted(DATA_DIR.glob(f"{pair_id}_monthly_*.parquet"))
    if not cands:
        raise FileNotFoundError(f"No monthly parquet for pair_id='{pair_id}' in {DATA_DIR}")
    return cands[-1]


def _reason_string(
    signal_display: str,
    signal_value: float,
    new_pos: float,
    old_pos: float,
    strategy_code: str,
    direction: str,
) -> str:
    sv = f"{signal_value:.3f}" if (signal_value is not None and not pd.isna(signal_value)) else "n/a"
    if old_pos == 0 and new_pos > 0:
        action = f"initial entry to {new_pos*100:.0f}% long"
    elif old_pos > 0 and new_pos == 0:
        action = "exit to cash"
    elif old_pos >= 0 and new_pos < 0:
        action = f"flip to {new_pos*100:.0f}% short"
    elif old_pos < 0 and new_pos > 0:
        action = f"flip to {new_pos*100:.0f}% long"
    elif old_pos < 0 and new_pos == 0:
        action = "cover short to cash"
    elif new_pos > old_pos:
        action = f"scale up {old_pos*100:.0f}% → {new_pos*100:.0f}%"
    else:
        action = f"scale down {old_pos*100:.0f}% → {new_pos*100:.0f}%"
    return f"{strategy_code}/{direction}: {signal_display} = {sv} — {action}"


def synthesize_from_position_log(
    pair_id: str,
    position_col: str,
    strat_ret_col: str,
    *,
    price_col: str,
    signal_col: Optional[str] = None,
    signal_display: Optional[str] = None,
    commission_bps: int = 5,
    starting_capital: float = 10_000.0,
    epsilon: float = 1e-9,
    out_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Emit a broker-style CSV for a pair whose `winner_trade_log.csv` is
    already the authoritative position log.

    Parameters
    ----------
    pair_id : str
        Directory tag under results/ and data/.
    position_col : str
        Column in `winner_trade_log.csv` holding the position weight.
    strat_ret_col : str
        Column holding the per-period strategy return (used for cum P&L).
    price_col : str
        Column in the master monthly parquet holding the traded instrument
        close price (e.g. "xlp", "xlv"). Used to populate the broker-style
        `price` column.
    signal_col : str, optional
        Column in the master parquet holding the signal value for reason
        annotation. Omit to leave `signal_value` = NaN.
    signal_display : str, optional
        Short label for the signal in the reason string (defaults to signal_col).
    commission_bps, starting_capital, epsilon
        See header docstring.
    out_path : Path, optional
        Defaults to results/<pair_id>/winner_trades_broker_style.csv.

    Returns
    -------
    pd.DataFrame
        The broker-style dataframe (also written to disk).
    """
    pair_dir = RESULTS_ROOT / pair_id
    summary = json.loads((pair_dir / "winner_summary.json").read_text())
    strategy = summary.get("strategy_family", summary.get("strategy_code", "P?"))
    direction = summary.get("direction", "unknown")
    instrument = summary.get("target_symbol") or pair_id.split("_")[-1].upper()
    signal_display = signal_display or signal_col or summary.get("signal_code", "signal")

    # ── Load position log ────────────────────────────────────────────────
    log_path = pair_dir / "winner_trade_log.csv"
    pos_df = pd.read_csv(log_path, parse_dates=["date"]).set_index("date").sort_index()
    if position_col not in pos_df.columns:
        raise KeyError(f"{position_col!r} not in {log_path.name}. Columns: {list(pos_df.columns)}")
    if strat_ret_col not in pos_df.columns:
        raise KeyError(f"{strat_ret_col!r} not in {log_path.name}. Columns: {list(pos_df.columns)}")

    # Cumulative P&L from strategy returns
    cum_ret = (1.0 + pos_df[strat_ret_col].fillna(0)).cumprod() - 1.0

    # ── Pull prices + signal from master parquet ─────────────────────────
    master = pd.read_parquet(_find_monthly_parquet(pair_id))
    if price_col not in master.columns:
        raise KeyError(f"price_col={price_col!r} not in monthly parquet. Have: {list(master.columns)[:15]}…")
    prices = master[price_col].reindex(pos_df.index).ffill()
    sig_series = master[signal_col].reindex(pos_df.index) if signal_col else None

    # ── Emit broker events on position change ────────────────────────────
    rows = []
    last_pos = 0.0
    dates = list(pos_df.index)
    for i, date in enumerate(dates):
        new_pos = float(pos_df.loc[date, position_col])
        is_first_emit = (last_pos == 0.0 and new_pos != 0.0 and not any(r for r in rows))
        is_last = (i == len(dates) - 1)
        delta = new_pos - last_pos
        emit = is_first_emit or abs(delta) > epsilon or (is_last and new_pos != last_pos)
        if not emit:
            continue

        if new_pos > last_pos:
            side = "BUY"
        elif new_pos < last_pos:
            side = "SELL"
        else:
            side = "HOLD"

        qty_pct = new_pos * 100.0
        price = float(prices.loc[date]) if not pd.isna(prices.loc[date]) else float("nan")
        notional = abs(qty_pct) / 100.0 * starting_capital
        commission_usd = notional * commission_bps / 10_000.0
        cum_pnl_pct = float(cum_ret.loc[date]) * 100.0
        sv = float(sig_series.loc[date]) if (sig_series is not None and not pd.isna(sig_series.loc[date])) else float("nan")
        reason = _reason_string(signal_display, sv, new_pos, last_pos, strategy, direction)

        rows.append({
            "trade_date": date.strftime("%Y-%m-%d"),
            "side": side,
            "instrument": instrument,
            "quantity_pct": round(qty_pct, 4),
            "price": round(price, 4) if not pd.isna(price) else np.nan,
            "notional_usd": round(notional, 2),
            "commission_bps": int(commission_bps),
            "commission_usd": round(commission_usd, 4),
            "cum_pnl_pct": round(cum_pnl_pct, 4),
            "reason": reason,
        })
        last_pos = new_pos

    broker_df = pd.DataFrame(rows)

    # ── Write CSV with metadata comment ──────────────────────────────────
    out_path = out_path or (pair_dir / "winner_trades_broker_style.csv")
    header_comment = (
        f"# Simulated trade record based on backtest signals. No real trades executed. "
        f"Starting capital: ${starting_capital:,.0f}. Commission: {commission_bps} bps. "
        f"Pair: {pair_id}. Strategy: {strategy} ({direction}). "
        f"Signal: {signal_display}. Source: {log_path.name}.\n"
    )
    with open(out_path, "w") as f:
        f.write(header_comment)
        broker_df.to_csv(f, index=False)

    print(f"Wrote {out_path.relative_to(REPO_ROOT)}")
    print(f"  rows          : {len(broker_df)}")
    print(f"  instrument    : {instrument}")
    print(f"  strategy      : {strategy} / {direction}")
    if len(broker_df):
        print(f"  first / last  : {broker_df['trade_date'].iloc[0]} → {broker_df['trade_date'].iloc[-1]}")
        print(f"  final cum P&L : {broker_df['cum_pnl_pct'].iloc[-1]:.2f}%")
    return broker_df


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Synthesize broker-style CSV from existing position log.")
    ap.add_argument("pair_id")
    ap.add_argument("--position-col", required=True)
    ap.add_argument("--strat-ret-col", required=True)
    ap.add_argument("--price-col", required=True)
    ap.add_argument("--signal-col", default=None)
    ap.add_argument("--signal-display", default=None)
    ap.add_argument("--commission-bps", type=int, default=5)
    ap.add_argument("--starting-capital", type=float, default=10_000.0)
    args = ap.parse_args()
    synthesize_from_position_log(
        pair_id=args.pair_id,
        position_col=args.position_col,
        strat_ret_col=args.strat_ret_col,
        price_col=args.price_col,
        signal_col=args.signal_col,
        signal_display=args.signal_display,
        commission_bps=args.commission_bps,
        starting_capital=args.starting_capital,
    )
