"""
Generate winner-level outputs for the Strategy Execution Panel.

This script produces three artifacts per pair, placed in results/{pair_id}/:
  - winner_summary.json   (structured winner metadata for display)
  - winner_trade_log.csv  (pre-computed trade log)
  - execution_notes.md    (domain-expert execution guidance)

Author: Evan (Econometrics Agent)
Domain: Strategy analysis & backtest interpretation
"""

import json
import os
import sys
import warnings
from glob import glob

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Signal & threshold display-name mappings ─────────────────────────────────
# These are domain-knowledge mappings owned by Evan, not Ace.

SIGNAL_DISPLAY_NAMES = {
    # Monthly indicators (indpro, permit)
    "S1_level": "Level",
    "S2_yoy": "Year-over-Year Change",
    "S3_mom": "1-Month Momentum",
    "S4_mom": "3-Month Momentum",  # indpro pipeline alias
    "S4_dev": "Deviation from Trend",
    "S5_z": "Z-Score (60-month)",
    "S6_mom3m": "3-Month Momentum",
    "S7_mom6m": "6-Month Momentum",
    "S8_accel": "Acceleration",
    "S9_contr": "Contraction Flag",
    # Daily indicators (vix_vix3m)
    "S1_ratio": "VIX/VIX3M Ratio",
    "S2_z252": "Z-Score (252-day)",
    "S3_z126": "Z-Score (126-day)",
    "S4_roc5": "5-Day Rate of Change",
    "S5_roc21": "21-Day Rate of Change",
    "S6_mom5": "5-Day Momentum",
    "S7_mom21": "21-Day Momentum",
    "S8_pctrank": "Percentile Rank",
    "S9_backwd": "Backwardation Flag",
    "S10_spread": "Term Spread",
    # TED variants
    "spread_level": "Spread Level",
    "spread_zscore_252d": "Spread Z-Score (252-day)",
    "spread_roc_21d": "Spread 21-Day ROC",
    "spread_roc_63d": "Spread 63-Day ROC",
    "spread_mom_21d": "Spread 21-Day Momentum",
    # Legacy HY-IG
    "HMM 2-state": "HMM 2-State Regime Probability",
    "hmm_2state_prob_stress": "HMM Stress Probability",
    "composite_zscore_vts": "Composite Z-Score + VIX Term Structure",
    "hy_ig_zscore_252d": "HY-IG Spread Z-Score (252-day)",
}

THRESHOLD_DISPLAY_NAMES = {
    "T1_fixed_p25": "25th percentile (fixed, in-sample)",
    "T1_fixed_p50": "50th percentile (fixed, in-sample)",
    "T1_fixed_p75": "75th percentile (fixed, in-sample)",
    "T1_p25": "25th percentile (fixed)",
    "T1_p50": "50th percentile (fixed)",
    "T1_p75": "75th percentile (fixed)",
    "T2_roll_p25": "25th percentile (rolling window)",
    "T2_roll_p50": "50th percentile (rolling window)",
    "T2_roll_p75": "75th percentile (rolling window)",
    "T2_rp25": "25th percentile (rolling)",
    "T2_rp50": "50th percentile (rolling)",
    "T2_rp75": "75th percentile (rolling)",
    "T3_zscore_1.0": "Z-score > 1.0",
    "T3_zscore_1.5": "Z-score > 1.5",
    "T3_zscore_2.0": "Z-score > 2.0",
    "T4_zero": "Zero crossing",
    "T4_unity": "Ratio = 1.0",
    "T4_0.5": "Threshold = 0.5",
    "T4_0.7": "Threshold = 0.7",
}

STRATEGY_DISPLAY_NAMES = {
    "P1": "Long/Cash",
    "P1_long_cash": "Long/Cash",
    "P2": "Signal Strength (Proportional)",
    "P2_signal_strength": "Signal Strength (Proportional)",
    "P3": "Long/Short",
    "P3_long_short": "Long/Short",
}

STRATEGY_DESCRIPTIONS = {
    "P1": "Go fully long SPY when signal is bullish; move to cash otherwise.",
    "P1_long_cash": "Go fully long SPY when signal is bullish; move to cash otherwise.",
    "P2": "Scale position size proportionally to signal strength (0% to 100% invested).",
    "P2_signal_strength": "Scale position size proportionally to signal strength (0% to 100% invested).",
    "P3": "Go long SPY when bullish, short SPY when bearish.",
    "P3_long_short": "Go long SPY when bullish, short SPY when bearish.",
}


def find_latest_tournament(pair_id: str) -> str | None:
    """Find the latest tournament_results CSV for a pair."""
    pair_dir = os.path.join(BASE, "results", pair_id)
    files = sorted(glob(os.path.join(pair_dir, "tournament_results_*.csv")))
    return files[-1] if files else None


def load_winner(tourn_path: str) -> pd.Series | None:
    """Load tournament CSV and return the winner row."""
    tdf = pd.read_csv(tourn_path)
    valid = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
    if len(valid) == 0:
        return None
    return valid.loc[valid["oos_sharpe"].idxmax()]


def load_metadata(pair_id: str) -> dict | None:
    """Load interpretation_metadata.json for a pair."""
    path = os.path.join(BASE, "results", pair_id, "interpretation_metadata.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def find_validation_dir(pair_id: str) -> str | None:
    """Find the validation directory (nested or legacy top-level)."""
    # Nested: results/{pair_id}/tournament_validation_*/
    pair_dir = os.path.join(BASE, "results", pair_id)
    nested = sorted(glob(os.path.join(pair_dir, "tournament_validation_*")))
    if nested:
        return nested[-1]
    # Legacy: results/tournament_validation_*/ (only for hy_ig_spy)
    if pair_id == "hy_ig_spy":
        legacy = sorted(glob(os.path.join(BASE, "results", "tournament_validation_*")))
        if legacy:
            return legacy[-1]
    return None


def determine_lead_col(winner: pd.Series) -> tuple[str, int]:
    """Return (lead_column_name, lead_value) from winner row."""
    if "lead_months" in winner.index:
        return "lead_months", int(winner["lead_months"])
    elif "lead_days" in winner.index:
        return "lead_days", int(winner["lead_days"])
    return "lead", 0


def generate_winner_summary(pair_id: str, winner: pd.Series, metadata: dict,
                            validation_dir: str | None) -> dict:
    """Produce winner_summary.json content."""
    signal_code = winner["signal"]
    threshold_code = winner["threshold"]
    strategy_code = winner["strategy"]
    lead_col, lead_val = determine_lead_col(winner)
    lead_unit = "months" if "month" in lead_col else "days"

    summary = {
        "pair_id": pair_id,
        "signal_code": signal_code,
        "signal_display_name": SIGNAL_DISPLAY_NAMES.get(signal_code, signal_code),
        "threshold_code": threshold_code,
        "threshold_display_name": THRESHOLD_DISPLAY_NAMES.get(threshold_code, threshold_code),
        "strategy_code": strategy_code,
        "strategy_display_name": STRATEGY_DISPLAY_NAMES.get(strategy_code, strategy_code),
        "strategy_description": STRATEGY_DESCRIPTIONS.get(strategy_code, ""),
        "lead_value": lead_val,
        "lead_unit": lead_unit,
        "lead_description": f"{lead_val} {lead_unit}" if lead_val > 0 else "No lead (same-period)",
        "direction": metadata.get("expected_direction", "unknown"),
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "oos_ann_return": round(float(winner.get("oos_ann_return", 0)), 2),
        "max_drawdown": round(float(winner["max_drawdown"]), 2),
        "annual_turnover": round(float(winner.get("annual_turnover", 0)), 2),
        "win_rate": round(float(winner.get("win_rate", 0)), 4)
            if "win_rate" in winner.index else None,
    }

    # Add threshold value if computable from in-sample data
    # For fixed thresholds (T1), we can compute from the tournament parameters
    # For rolling (T2) and z-score (T3), threshold varies over time — report method only
    if threshold_code.startswith("T4_"):
        parts = threshold_code.split("_", 1)
        try:
            summary["threshold_value"] = float(parts[1])
        except ValueError:
            summary["threshold_value"] = None
    else:
        summary["threshold_value"] = None  # Time-varying or requires data access

    # Signal decay and cost info from validation
    if validation_dir:
        decay_path = os.path.join(validation_dir, "signal_decay.csv")
        if os.path.exists(decay_path):
            decay_df = pd.read_csv(decay_path)
            # Find max delay where Sharpe stays positive
            positive_rows = decay_df[decay_df["oos_sharpe"] > 0]
            if len(positive_rows) > 0:
                max_delay = int(positive_rows["execution_delay"].max())
                summary["max_acceptable_delay_days"] = max_delay
            else:
                summary["max_acceptable_delay_days"] = 0

        cost_path = os.path.join(validation_dir, "transaction_costs.csv")
        if os.path.exists(cost_path):
            cost_df = pd.read_csv(cost_path)
            # Handle both schemas: nested uses net_sharpe_approx/tx_cost_bps,
            # legacy uses net_sharpe/cost_bps
            sharpe_col = ("net_sharpe_approx" if "net_sharpe_approx" in cost_df.columns
                          else "net_sharpe")
            cost_col = ("tx_cost_bps" if "tx_cost_bps" in cost_df.columns
                        else "cost_bps")
            if sharpe_col in cost_df.columns and cost_col in cost_df.columns:
                positive_costs = cost_df[cost_df[sharpe_col] > 0]
                if len(positive_costs) > 0:
                    summary["breakeven_cost_bps"] = float(
                        positive_costs[cost_col].max()
                    )
                else:
                    summary["breakeven_cost_bps"] = 0.0

    return summary


def resolve_signal_column(df: pd.DataFrame, sig_name: str, pair_id: str) -> str | None:
    """Map tournament signal name to actual DataFrame column."""
    # Same logic as trade_history.py sig_mappings — this is Evan's domain
    sig_mappings = {
        "S1_level": lambda: next((c for c in df.columns if c in [
            "indpro", "permit", "spread", "vix_ratio"]), None),
        "S2_yoy": lambda: next((c for c in df.columns if "yoy" in c and "fwd" not in c), None),
        "S3_mom": lambda: next((c for c in df.columns if c.endswith("_mom") and "fwd" not in c), None),
        "S4_mom": lambda: next((c for c in df.columns if "mom_3m" in c or c.endswith("_mom")), None),
        "S4_dev": lambda: next((c for c in df.columns if "dev_trend" in c), None),
        "S5_z": lambda: next((c for c in df.columns if "zscore_60m" in c), None),
        "S6_mom3m": lambda: next((c for c in df.columns if "mom_3m" in c), None),
        "S7_mom6m": lambda: next((c for c in df.columns if "mom_6m" in c), None),
        "S8_accel": lambda: next((c for c in df.columns if "accel" in c), None),
        "S9_contr": lambda: next((c for c in df.columns if "contraction" in c), None),
        "S1_ratio": lambda: next((c for c in df.columns if c == "vix_ratio"), None),
        "S2_z252": lambda: next((c for c in df.columns if "zscore_252d" in c), None),
        "S3_z126": lambda: next((c for c in df.columns if "zscore_126d" in c), None),
        "S4_roc5": lambda: next((c for c in df.columns if "roc_5d" in c), None),
        "S5_roc21": lambda: next((c for c in df.columns if "roc_21d" in c), None),
        "S6_mom5": lambda: next((c for c in df.columns if "mom_5d" in c), None),
        "S7_mom21": lambda: next((c for c in df.columns if "mom_21d" in c), None),
        "S8_pctrank": lambda: next((c for c in df.columns if "pctrank" in c), None),
        "S9_backwd": lambda: next((c for c in df.columns if "backwardation" in c), None),
        "S10_spread": lambda: next((c for c in df.columns if "term_spread" in c), None),
        # TED variants
        "spread_level": lambda: next((c for c in df.columns if c == "spread"), None),
        "spread_zscore_252d": lambda: next((c for c in df.columns if c == "spread_zscore_252d"), None),
        "spread_roc_21d": lambda: next((c for c in df.columns if c == "spread_roc_21d"), None),
        "spread_roc_63d": lambda: next((c for c in df.columns if c == "spread_roc_63d"), None),
        "spread_mom_21d": lambda: next((c for c in df.columns if c == "spread_mom_21d"), None),
    }

    if sig_name in sig_mappings:
        return sig_mappings[sig_name]()
    # Direct column match
    if sig_name in df.columns:
        return sig_name
    return None


def generate_trade_log(pair_id: str, winner: pd.Series, metadata: dict) -> pd.DataFrame | None:
    """Produce winner_trade_log.csv — pre-computed trade-level metrics.

    This is backtest logic belonging to Evan's domain.
    """
    # Find data file
    data_dir = os.path.join(BASE, "data")
    data_files = [f for f in os.listdir(data_dir)
                  if f.startswith(pair_id) and f.endswith(".parquet")]
    if not data_files:
        return None

    df = pd.read_parquet(os.path.join(data_dir, data_files[0]))

    # Resolve signal column
    sig_name = winner["signal"]
    sig_col = resolve_signal_column(df, sig_name, pair_id)
    if sig_col is None:
        return None

    # Get SPY return column
    if "spy_ret" in df.columns:
        ret_col = "spy_ret"
    elif "spy" in df.columns:
        df["spy_ret"] = df["spy"].pct_change()
        ret_col = "spy_ret"
    else:
        return None

    # Apply lead
    lead_col, lead_val = determine_lead_col(winner)
    signal = df[sig_col].shift(lead_val) if lead_val > 0 else df[sig_col]

    # Apply threshold
    thresh_name = winner["threshold"]
    oos_n = int(winner["oos_n"])
    n_total = len(df)
    oos_start_idx = n_total - oos_n

    counter_cyclical = metadata.get("expected_direction") == "counter_cyclical"

    if thresh_name.startswith("T1_") or thresh_name.startswith("T1_fixed_"):
        # Extract percentile
        parts = thresh_name.replace("T1_fixed_", "").replace("T1_", "")
        pct = int(parts.lstrip("p"))
        is_signal = signal.iloc[:oos_start_idx].dropna()
        thresh_val = is_signal.quantile(pct / 100)
    elif thresh_name.startswith("T2_") or thresh_name.startswith("T2_r"):
        parts = thresh_name.replace("T2_roll_", "").replace("T2_r", "")
        pct = int(parts.lstrip("p"))
        is_daily = "daily" in data_files[0] or "vix" in pair_id or "ted" in pair_id
        window = 252 if is_daily else 60
        thresh_val = signal.rolling(window, min_periods=int(window * 0.8)).quantile(pct / 100)
    elif thresh_name.startswith("T3_"):
        z_val = float(thresh_name.split("_")[1].replace("zscore_", ""))
        thresh_val = z_val  # Z-score threshold is the value itself
    elif thresh_name.startswith("T4_"):
        val_str = thresh_name.split("_", 1)[1]
        if val_str == "zero":
            thresh_val = 0
        elif val_str == "unity":
            thresh_val = 1.0
        else:
            thresh_val = float(val_str)
    else:
        return None

    # Determine bullish condition
    if isinstance(thresh_val, (int, float)):
        bullish = signal < thresh_val if counter_cyclical else signal > thresh_val
    else:
        bullish = signal < thresh_val if counter_cyclical else signal > thresh_val

    # Apply strategy
    strat = winner["strategy"]
    if strat in ("P1", "P1_long_cash"):
        position = bullish.astype(float)
    elif strat in ("P2", "P2_signal_strength"):
        is_daily = "daily" in data_files[0] or "vix" in pair_id or "ted" in pair_id
        window = 252 if is_daily else 60
        smin = signal.rolling(window, min_periods=int(window * 0.8)).min()
        smax = signal.rolling(window, min_periods=int(window * 0.8)).max()
        sr = (smax - smin).replace(0, np.nan)
        if counter_cyclical:
            position = (1 - (signal - smin) / sr).clip(0, 1)
        else:
            position = ((signal - smin) / sr).clip(0, 1)
    elif strat in ("P3", "P3_long_short"):
        position = bullish.astype(float) * 2 - 1
    else:
        position = bullish.astype(float)

    # Calculate strategy returns
    strat_ret = position.shift(1) * df[ret_col]
    cum_ret = (1 + strat_ret.fillna(0)).cumprod()

    # Identify trades: position changes
    pos_clean = position.dropna()
    pos_change = pos_clean.diff().fillna(pos_clean.iloc[0] if len(pos_clean) > 0 else 0)
    trade_entries = pos_change[pos_change != 0].index

    if len(trade_entries) < 2:
        return None

    trades = []
    for i in range(len(trade_entries)):
        entry_date = trade_entries[i]
        exit_date = trade_entries[i + 1] if i + 1 < len(trade_entries) else df.index[-1]

        entry_pos = position.loc[entry_date]
        direction = "Long" if entry_pos > 0 else ("Short" if entry_pos < 0 else "Cash")

        # Holding period
        holding_days = (exit_date - entry_date).days

        # Trade return: cumulative strategy return over the period
        if entry_date in cum_ret.index and exit_date in cum_ret.index:
            entry_cum = cum_ret.loc[:entry_date].iloc[-1] if entry_date in cum_ret.index else 1.0
            exit_cum = cum_ret.loc[:exit_date].iloc[-1] if exit_date in cum_ret.index else 1.0
            trade_ret = (exit_cum / entry_cum - 1) if entry_cum != 0 else 0.0
        else:
            trade_ret = 0.0

        trades.append({
            "entry_date": entry_date.strftime("%Y-%m-%d"),
            "exit_date": exit_date.strftime("%Y-%m-%d"),
            "direction": direction,
            "holding_days": holding_days,
            "trade_return_pct": round(trade_ret * 100, 2),
        })

    return pd.DataFrame(trades)


def generate_execution_notes(pair_id: str, winner: pd.Series,
                             metadata: dict, summary: dict) -> str:
    """Produce execution_notes.md — domain-expert guidance from Evan."""
    signal_display = summary["signal_display_name"]
    thresh_display = summary["threshold_display_name"]
    strat_display = summary["strategy_display_name"]
    lead_desc = summary["lead_description"]
    direction = metadata.get("expected_direction", "unknown")

    direction_text = {
        "pro_cyclical": "Higher values are bullish (go long when signal rises above threshold).",
        "counter_cyclical": "Higher values are bearish (go long when signal falls below threshold).",
    }.get(direction, "Direction depends on empirical regime analysis.")

    lines = [
        f"# Execution Notes: {pair_id}",
        "",
        f"## Winner: {signal_display} / {thresh_display} / {strat_display}",
        "",
        "## Step-by-Step Execution",
        "",
        f"1. **Monitor** the {signal_display} indicator at its native publication frequency.",
        f"2. **Apply threshold**: {thresh_display}.",
        f"3. **Direction**: {direction_text}",
        f"4. **Action**: {summary['strategy_description']}",
        f"5. **Lead time**: {lead_desc}.",
    ]

    if summary.get("max_acceptable_delay_days") is not None:
        lines.append(
            f"6. **Execution window**: Signal remains actionable up to "
            f"{summary['max_acceptable_delay_days']} day(s) after generation "
            f"(based on signal decay analysis)."
        )

    if summary.get("breakeven_cost_bps") is not None:
        lines.append(
            f"7. **Transaction cost budget**: Strategy Sharpe remains positive "
            f"up to {summary['breakeven_cost_bps']:.1f} bps round-trip."
        )

    lines.append(
        f"8. **Expected turnover**: ~{summary['annual_turnover']:.1f} trades per year."
    )

    # Caveats
    caveats = metadata.get("caveats", [])
    if caveats:
        lines.extend(["", "## Caveats", ""])
        for caveat in caveats:
            lines.append(f"- {caveat}")

    lines.extend(["", "---", f"*Generated by Evan's pipeline for {pair_id}*"])
    return "\n".join(lines)


def process_pair(pair_id: str) -> dict:
    """Generate all winner outputs for a single pair."""
    status = {"pair_id": pair_id, "outputs": []}

    tourn_path = find_latest_tournament(pair_id)
    if not tourn_path:
        status["error"] = "No tournament results found"
        return status

    winner = load_winner(tourn_path)
    if winner is None:
        status["error"] = "No valid winner in tournament"
        return status

    metadata = load_metadata(pair_id)
    if metadata is None:
        status["error"] = "No interpretation metadata found"
        return status

    validation_dir = find_validation_dir(pair_id)
    output_dir = os.path.join(BASE, "results", pair_id)

    # 1. winner_summary.json
    summary = generate_winner_summary(pair_id, winner, metadata, validation_dir)
    summary_path = os.path.join(output_dir, "winner_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    status["outputs"].append("winner_summary.json")
    print(f"  ✓ winner_summary.json")

    # 2. winner_trade_log.csv
    trade_log = generate_trade_log(pair_id, winner, metadata)
    if trade_log is not None:
        log_path = os.path.join(output_dir, "winner_trade_log.csv")
        trade_log.to_csv(log_path, index=False)
        status["outputs"].append(f"winner_trade_log.csv ({len(trade_log)} trades)")
        print(f"  ✓ winner_trade_log.csv ({len(trade_log)} trades)")
    else:
        status["outputs"].append("winner_trade_log.csv (SKIPPED — data unavailable)")
        print(f"  ⚠ winner_trade_log.csv skipped (data unavailable)")

    # 3. execution_notes.md
    notes = generate_execution_notes(pair_id, winner, metadata, summary)
    notes_path = os.path.join(output_dir, "execution_notes.md")
    with open(notes_path, "w") as f:
        f.write(notes)
    status["outputs"].append("execution_notes.md")
    print(f"  ✓ execution_notes.md")

    return status


def main():
    # Discover all pairs with tournament results
    results_dir = os.path.join(BASE, "results")
    pairs = []
    for name in sorted(os.listdir(results_dir)):
        pair_path = os.path.join(results_dir, name)
        if not os.path.isdir(pair_path):
            continue
        if any(f.startswith("tournament_results") for f in os.listdir(pair_path)):
            pairs.append(name)

    if not pairs:
        print("No pairs with tournament results found.")
        sys.exit(1)

    print(f"Processing {len(pairs)} pairs: {', '.join(pairs)}\n")

    results = []
    for pair_id in pairs:
        print(f"[{pair_id}]")
        result = process_pair(pair_id)
        results.append(result)
        print()

    # Summary
    print("=" * 60)
    print("Summary:")
    for r in results:
        err = r.get("error", "")
        outputs = ", ".join(r.get("outputs", []))
        if err:
            print(f"  {r['pair_id']}: ERROR — {err}")
        else:
            print(f"  {r['pair_id']}: {outputs}")


if __name__ == "__main__":
    main()
