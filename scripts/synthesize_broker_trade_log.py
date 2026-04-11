"""
Synthesize a broker-style discrete trade log from a pair's internal backtest outputs.

This helper implements Rule C4 of the Econometrics SOP: in addition to the
internal daily position log (winner_trade_log.csv), every pair must ship a
broker-style CSV (winner_trades_broker_style.csv) with one row per discrete
trade event — the kind of document a human reader or a broker statement would
recognise.

Usage
-----
    python3 scripts/synthesize_broker_trade_log.py <pair_id> [--epsilon 0.01]

Arguments
---------
pair_id     Required. Directory tag under results/<pair_id>/ and data/.
--epsilon   Optional. Minimum position-weight change (absolute) to emit a
            trade row. Default 0.01 (= 1% of portfolio). Prevents the Signal
            Strength (P2) style strategies from emitting a row on every single
            daily noise-level adjustment.
--starting-capital
            Optional. USD starting capital used for notional sizing.
            Default 10000.
--commission-bps
            Optional. Override the auto-detected commission in basis points.

Design notes
------------
1. Generic across pairs: all pair-specific information is read from
   results/<pair_id>/winner_summary.json and the master data parquet in
   data/. No strategy-specific logic is hard-coded.
2. The script replays the winning strategy (P1/P2/P3) using the same math as
   the pipeline (rolling-window min/max scaling for P2, threshold gate for
   P1/P3), then emits a broker event whenever the position weight moves by
   more than `epsilon` from the last emitted row.
3. First emitted row is always the initial entry from cash (BUY). Last row is
   always the terminal position at backtest end, even if the terminal change
   is smaller than epsilon — this makes the log round-trip correctly and
   preserves the final P&L reading.
4. The CSV starts with a single `#`-prefixed metadata row so pandas can skip
   it on read with `comment="#"`.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RESULTS_ROOT = REPO_ROOT / "results"


# ─────────────────────────────────────────────────────────────────────────────
# Signal column mapping (extend here when new pairs / signals are added)
# ─────────────────────────────────────────────────────────────────────────────
SIGNAL_COL_MAP = {
    # HY-IG family
    "S1_spread_level":   "hy_ig_spread",
    "S2a_zscore_252d":   "hy_ig_zscore_252d",
    "S2b_zscore_504d":   "hy_ig_zscore_504d",
    "S3a_pctrank_504d":  "hy_ig_pctrank_504d",
    "S3b_pctrank_1260d": "hy_ig_pctrank_1260d",
    "S4a_roc_21d":       "hy_ig_roc_21d",
    "S4b_roc_63d":       "hy_ig_roc_63d",
    "S4c_roc_126d":      "hy_ig_roc_126d",
    "S5_ccc_bb_spread":  "ccc_bb_spread",
    "S6_hmm_stress":     "hmm_2state_prob_stress",
    "S7_ms_stress":      "ms_2state_stress_prob",
    "S10_mom_21d":       "hy_ig_mom_21d",
    "S11_mom_63d":       "hy_ig_mom_63d",
    "S12_mom_252d":      "hy_ig_mom_252d",
    "S13_acceleration":  "hy_ig_acceleration",
}


def _find_master_parquet(pair_id: str) -> Path:
    """Return the most recent daily master parquet for the pair."""
    candidates = sorted(
        list(DATA_DIR.glob(f"{pair_id}_daily_*.parquet"))
        + list(DATA_DIR.glob(f"{pair_id}_daily_latest.parquet"))
    )
    if not candidates:
        raise FileNotFoundError(
            f"No daily parquet found in {DATA_DIR} for pair_id='{pair_id}'."
        )
    # Prefer a dated file over 'latest' for reproducibility
    dated = [p for p in candidates if "latest" not in p.name]
    return (dated[-1] if dated else candidates[-1])


def _find_signals_parquet(pair_dir: Path) -> Path | None:
    files = sorted(pair_dir.glob("signals_*.parquet"))
    return files[-1] if files else None


def _find_tournament_csv(pair_dir: Path) -> Path | None:
    files = sorted(pair_dir.glob("tournament_results_*.csv"))
    return files[-1] if files else None


def _detect_commission_bps(pair_dir: Path, override: int | None) -> int:
    """Pick a single commission figure in bps for the broker log.

    Priority:
        1. CLI override
        2. winner_summary.json ("commission_bps" or "transaction_cost")
        3. tournament_validation_*/transaction_costs.csv (take the lowest
           non-zero cost tier that the pipeline actually used — this
           matches the 5 bps default tier).
        4. Fallback: 5 bps.
    """
    if override is not None:
        return int(override)

    summary_path = pair_dir / "winner_summary.json"
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
        for key in ("commission_bps", "transaction_cost", "tx_cost_bps"):
            if key in summary and summary[key] is not None:
                try:
                    return int(summary[key])
                except (TypeError, ValueError):
                    pass

    tv_dirs = sorted(pair_dir.glob("tournament_validation_*"))
    if tv_dirs:
        tc_path = tv_dirs[-1] / "transaction_costs.csv"
        if tc_path.exists():
            tc = pd.read_csv(tc_path)
            # Rows can include a 'breakeven' sentinel — filter it out.
            tiers = [int(x) for x in tc["tx_cost_bps"].unique()
                     if str(x).lstrip("-").isdigit() and int(x) > 0]
            if tiers:
                return int(min(tiers))

    return 5


def _compute_threshold_val(
    is_signal: pd.Series,
    threshold_name: str,
    signal_series: pd.Series,
):
    """Mirror of pipeline _compute_threshold_val. Kept local to avoid an
    import dependency on pair-specific pipeline modules."""
    if threshold_name.startswith("T1_p"):
        pct = int(threshold_name.split("p")[1])
        return float(is_signal.quantile(pct / 100))
    if threshold_name.startswith("T2_rp"):
        pct = int(threshold_name.split("rp")[1])
        return signal_series.rolling(504, min_periods=400).quantile(pct / 100)
    if threshold_name.startswith("T3_z"):
        return float(threshold_name.split("z")[1])
    if threshold_name.startswith(("T4_hmm_", "T4_ms_", "T5_hmm_", "T5_ms_")):
        return float(threshold_name.rsplit("_", 1)[1])
    return None


def _replay_positions(
    work: pd.DataFrame,
    sig_col: str,
    threshold_name: str,
    threshold_val,
    strategy: str,
    lead: int,
    counter_cyclical: bool = True,
) -> tuple[pd.Series, pd.Series]:
    """Replay the winning strategy and return (position, strategy_returns).

    Math is identical to scripts/pair_pipeline_hy_ig_v2_spy.py::_replay_strategy.
    """
    signal = work[sig_col].shift(lead) if lead > 0 else work[sig_col]

    if isinstance(threshold_val, pd.Series):
        threshold_val = threshold_val.reindex(work.index)

    if threshold_name.startswith("T3_z"):
        roll_mean = signal.rolling(504, min_periods=400).mean()
        roll_std = signal.rolling(504, min_periods=400).std().replace(0, np.nan)
        z_series = (signal - roll_mean) / roll_std
        bullish = z_series < threshold_val if counter_cyclical else z_series > threshold_val
    else:
        bullish = (signal < threshold_val) if counter_cyclical else (signal > threshold_val)

    if strategy == "P1":
        pos = bullish.astype(float)
    elif strategy == "P2":
        smin = signal.rolling(504, min_periods=400).min()
        smax = signal.rolling(504, min_periods=400).max()
        sr = (smax - smin).replace(0, np.nan)
        pos = (1 - (signal - smin) / sr).clip(0, 1)
        if not counter_cyclical:
            pos = 1 - pos
    elif strategy == "P3":
        pos = bullish.astype(float) * 2 - 1
    else:
        pos = bullish.astype(float)

    strat_ret = pos.shift(1) * work["spy_ret"]
    return pos, strat_ret


def _reason_string(
    signal_display_name: str,
    threshold_display_name: str,
    threshold_val,
    signal_value: float,
    new_pos: float,
    old_pos: float,
    strategy_code: str,
    direction: str,
) -> str:
    """Human-readable reason for the trade event."""
    sv = signal_value if (signal_value is not None and not pd.isna(signal_value)) else float("nan")
    tv_str = ""
    if isinstance(threshold_val, (int, float, np.floating)) and not pd.isna(threshold_val):
        tv_str = f"{float(threshold_val):.2f}"

    if old_pos == 0 and new_pos > 0:
        action = f"initial entry to {new_pos*100:.1f}% long"
    elif new_pos == 0 and old_pos > 0:
        action = "exit to cash"
    elif new_pos > old_pos:
        action = f"scale up {old_pos*100:.1f}% → {new_pos*100:.1f}%"
    else:
        action = f"scale down {old_pos*100:.1f}% → {new_pos*100:.1f}%"

    signal_part = (
        f"{signal_display_name} = {sv:.3f}"
        if not pd.isna(sv) else f"{signal_display_name}"
    )
    threshold_part = f" (threshold {tv_str})" if tv_str else ""
    return f"{strategy_code}/{direction}: {signal_part}{threshold_part} — {action}"


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def synthesize(
    pair_id: str,
    epsilon: float = 0.01,
    starting_capital: float = 10_000.0,
    commission_override: int | None = None,
) -> pd.DataFrame:
    pair_dir = RESULTS_ROOT / pair_id
    if not pair_dir.exists():
        raise FileNotFoundError(f"Pair results directory not found: {pair_dir}")

    summary_path = pair_dir / "winner_summary.json"
    with open(summary_path) as f:
        summary = json.load(f)

    sig_name: str = summary["signal_code"]
    tname: str = summary["threshold_code"]
    strat: str = summary["strategy_code"]
    lead: int = int(summary.get("lead_value", 0))
    direction: str = summary.get("direction", "counter_cyclical")
    counter_cyclical = direction.lower() == "counter_cyclical"

    # Instrument: the asset traded. For now every pair maps target→SPY; infer
    # from pair_id suffix for future-proofing.
    parts = pair_id.split("_")
    instrument = parts[-1].upper() if parts else "SPY"

    sig_col = SIGNAL_COL_MAP.get(sig_name)
    if sig_col is None:
        raise KeyError(
            f"Unknown signal_code '{sig_name}'. Extend SIGNAL_COL_MAP in "
            f"{Path(__file__).name}."
        )

    # ── Load price data + signal ─────────────────────────────────────────
    master_path = _find_master_parquet(pair_id)
    df = pd.read_parquet(master_path)
    if "spy_ret" not in df.columns:
        df["spy_ret"] = df["spy"].pct_change()

    work = df.copy()
    if sig_col not in work.columns:
        sigs_path = _find_signals_parquet(pair_dir)
        if sigs_path is None:
            raise FileNotFoundError(
                f"Signal column '{sig_col}' not in master parquet and no "
                f"signals_*.parquet available under {pair_dir}."
            )
        sig_df = pd.read_parquet(sigs_path)
        if sig_col not in sig_df.columns:
            raise KeyError(
                f"Signal column '{sig_col}' not found in {sigs_path.name}."
            )
        work[sig_col] = sig_df[sig_col].reindex(work.index)

    # ── Compute threshold + replay positions ─────────────────────────────
    IS_END = pd.Timestamp("2015-12-31")  # convention matches pipelines
    is_signal = work.loc[work.index <= IS_END, sig_col].dropna()
    tval = _compute_threshold_val(is_signal, tname, work[sig_col])
    pos, strat_ret = _replay_positions(
        work, sig_col, tname, tval, strat, lead, counter_cyclical
    )
    cum_ret = (1 + strat_ret.fillna(0)).cumprod()

    pos_clean = pos.dropna()
    if len(pos_clean) == 0:
        raise RuntimeError("Replayed position series is empty.")

    # ── Commission ───────────────────────────────────────────────────────
    commission_bps = _detect_commission_bps(pair_dir, commission_override)

    # ── Emit broker events ───────────────────────────────────────────────
    signal_series = work[sig_col]
    signal_display = summary.get("signal_display_name", sig_name)
    threshold_display = summary.get("threshold_display_name", tname)

    rows = []
    last_emitted = 0.0
    first_date = pos_clean.index[0]
    last_date = pos_clean.index[-1]

    for date, new_pos in pos_clean.items():
        is_first = (date == first_date)
        is_last = (date == last_date)
        delta = float(new_pos) - last_emitted
        emit = is_first or is_last or abs(delta) >= epsilon
        if not emit:
            continue

        # Side: BUY if increasing, SELL if decreasing. First entry from 0 → BUY.
        if new_pos > last_emitted:
            side = "BUY"
        elif new_pos < last_emitted:
            side = "SELL"
        else:
            # No actual change but it's the final row → synthesize a terminal
            # snapshot without labelling it BUY/SELL. Use HOLD.
            side = "HOLD"

        price = float(work.loc[date, "spy"]) if "spy" in work.columns else float("nan")
        qty_pct = float(new_pos) * 100.0
        # Notional is the dollar allocation from the portfolio — independent of price.
        # `price` is kept as a reference column (SPY close on the trade date).
        notional = (qty_pct / 100.0) * starting_capital
        commission_usd = notional * commission_bps / 10_000.0

        cum_pnl_pct = float(cum_ret.loc[date] - 1.0) * 100.0 if date in cum_ret.index else float("nan")
        sig_val = float(signal_series.loc[date]) if date in signal_series.index else float("nan")

        reason = _reason_string(
            signal_display_name=signal_display,
            threshold_display_name=threshold_display,
            threshold_val=tval if not isinstance(tval, pd.Series) else tval.get(date, np.nan),
            signal_value=sig_val,
            new_pos=float(new_pos),
            old_pos=last_emitted,
            strategy_code=strat,
            direction=direction,
        )

        rows.append({
            "trade_date": date.strftime("%Y-%m-%d"),
            "side": side,
            "instrument": instrument,
            "quantity_pct": round(qty_pct, 4),
            "price": round(price, 4),
            "notional_usd": round(notional, 2),
            "commission_bps": int(commission_bps),
            "commission_usd": round(commission_usd, 4),
            "cum_pnl_pct": round(cum_pnl_pct, 4),
            "reason": reason,
        })
        last_emitted = float(new_pos)

    broker_df = pd.DataFrame(rows)

    # ── Write CSV with metadata comment row ──────────────────────────────
    out_path = pair_dir / "winner_trades_broker_style.csv"
    header_comment = (
        f"# Simulated trade record based on backtest signals. No real trades "
        f"executed. Starting capital: ${starting_capital:,.0f}. "
        f"Commission: {commission_bps} bps. "
        f"Emission epsilon: {epsilon:.4f} (position-weight change threshold). "
        f"Pair: {pair_id}. Strategy: {strat} ({direction}). "
        f"Signal: {signal_display} / Threshold: {threshold_display}.\n"
    )
    with open(out_path, "w") as f:
        f.write(header_comment)
        broker_df.to_csv(f, index=False)

    # ── Verification summary ────────────────────────────────────────────
    print(f"Wrote {out_path.relative_to(REPO_ROOT)}")
    print(f"  rows        : {len(broker_df)}")
    print(f"  epsilon     : {epsilon}")
    print(f"  commission  : {commission_bps} bps")
    print(f"  instrument  : {instrument}")
    print(f"  strategy    : {strat} / {direction}")
    print(f"  first date  : {broker_df['trade_date'].iloc[0] if len(broker_df) else 'n/a'}")
    print(f"  last  date  : {broker_df['trade_date'].iloc[-1] if len(broker_df) else 'n/a'}")
    final_cum = float(cum_ret.iloc[-1] - 1.0) * 100.0
    years = (pos_clean.index[-1] - pos_clean.index[0]).days / 365.25
    implied_ann = (1 + final_cum / 100.0) ** (1 / years) - 1 if years > 0 else float("nan")
    print(f"  final cum P&L: {final_cum:.2f}% over {years:.2f} years "
          f"(implied CAGR {implied_ann*100:.2f}%)")

    if len(broker_df) > 1000:
        print(
            f"  WARNING: {len(broker_df)} rows exceeds the 1,000-row guardrail. "
            f"This usually means the Signal Strength (P2) strategy is "
            f"continuously adjusting the position by small amounts. Consider "
            f"raising --epsilon (currently {epsilon})."
        )

    return broker_df


def _parse_args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pair_id", help="e.g. hy_ig_v2_spy")
    ap.add_argument("--epsilon", type=float, default=0.01,
                    help="Minimum position-weight change to emit a trade row. Default 0.01 (1 pct).")
    ap.add_argument("--starting-capital", type=float, default=10_000.0,
                    help="USD starting capital. Default 10000.")
    ap.add_argument("--commission-bps", type=int, default=None,
                    help="Override commission in basis points.")
    return ap.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        synthesize(
            pair_id=args.pair_id,
            epsilon=args.epsilon,
            starting_capital=args.starting_capital,
            commission_override=args.commission_bps,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
