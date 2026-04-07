"""
Generate drawdown comparison charts for the Strategy Execution Panel.

Produces {pair_id}_drawdown.json in output/charts/{pair_id}/plotly/ for each pair
that has a winner_trade_log.csv and corresponding data.

Author: Vera (Visualization Agent)
Domain: Chart production — Plotly JSON serialization
"""

import json
import os
import sys
import warnings
from glob import glob

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Vera's SOP color palette (colorblind-safe)
STRATEGY_COLOR = "#0072B2"  # Blue
BENCHMARK_COLOR = "#999999"  # Gray
ZERO_LINE_COLOR = "#D55E00"  # Orange-red


def load_pair_data(pair_id: str) -> pd.DataFrame | None:
    """Load the analysis-ready parquet for a pair."""
    data_dir = os.path.join(BASE, "data")
    data_files = [f for f in os.listdir(data_dir)
                  if f.startswith(pair_id) and f.endswith(".parquet")]
    if not data_files:
        return None
    return pd.read_parquet(os.path.join(data_dir, data_files[0]))


def load_winner_summary(pair_id: str) -> dict | None:
    """Load the structured winner summary produced by Evan."""
    path = os.path.join(BASE, "results", pair_id, "winner_summary.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def resolve_signal_column(df: pd.DataFrame, sig_code: str) -> str | None:
    """Map signal code to DataFrame column — same logic as generate_winner_outputs.py."""
    # Import the mapping from Evan's script to stay DRY
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
        "spread_level": lambda: next((c for c in df.columns if c == "spread"), None),
        "spread_zscore_252d": lambda: next((c for c in df.columns if c == "spread_zscore_252d"), None),
        "spread_roc_21d": lambda: next((c for c in df.columns if c == "spread_roc_21d"), None),
        "spread_roc_63d": lambda: next((c for c in df.columns if c == "spread_roc_63d"), None),
        "spread_mom_21d": lambda: next((c for c in df.columns if c == "spread_mom_21d"), None),
    }
    if sig_code in sig_mappings:
        return sig_mappings[sig_code]()
    if sig_code in df.columns:
        return sig_code
    return None


def reconstruct_drawdowns(pair_id: str, summary: dict, df: pd.DataFrame) -> tuple | None:
    """Reconstruct strategy and buy-and-hold drawdown series.

    Returns (dates, strategy_drawdown, bh_drawdown) or None.
    """
    sig_col = resolve_signal_column(df, summary["signal_code"])
    if sig_col is None:
        return None

    # SPY returns
    if "spy_ret" in df.columns:
        ret_col = "spy_ret"
    elif "spy" in df.columns:
        df["spy_ret"] = df["spy"].pct_change()
        ret_col = "spy_ret"
    else:
        return None

    # Apply lead
    lead_val = summary["lead_value"]
    signal = df[sig_col].shift(lead_val) if lead_val > 0 else df[sig_col]

    # OOS period
    oos_n = None
    tourn_files = sorted(glob(os.path.join(BASE, "results", pair_id, "tournament_results_*.csv")))
    if tourn_files:
        tdf = pd.read_csv(tourn_files[-1])
        valid = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
        if len(valid) > 0:
            winner = valid.loc[valid["oos_sharpe"].idxmax()]
            oos_n = int(winner["oos_n"])

    if oos_n is None:
        return None

    n_total = len(df)
    oos_start_idx = n_total - oos_n

    # Threshold
    thresh_code = summary["threshold_code"]
    metadata_path = os.path.join(BASE, "results", pair_id, "interpretation_metadata.json")
    counter_cyclical = False
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            meta = json.load(f)
            counter_cyclical = meta.get("expected_direction") == "counter_cyclical"

    if thresh_code.startswith("T1_") or thresh_code.startswith("T1_fixed_"):
        parts = thresh_code.replace("T1_fixed_", "").replace("T1_", "")
        pct = int(parts.lstrip("p"))
        is_signal = signal.iloc[:oos_start_idx].dropna()
        thresh_val = is_signal.quantile(pct / 100)
    elif thresh_code.startswith("T2_") or thresh_code.startswith("T2_r"):
        parts = thresh_code.replace("T2_roll_", "").replace("T2_r", "")
        pct = int(parts.lstrip("p"))
        is_daily = "daily" in str(df.index.freq) or "vix" in pair_id or "ted" in pair_id
        window = 252 if is_daily else 60
        thresh_val = signal.rolling(window, min_periods=int(window * 0.8)).quantile(pct / 100)
    elif thresh_code.startswith("T4_"):
        val_str = thresh_code.split("_", 1)[1]
        if val_str == "zero":
            thresh_val = 0
        elif val_str == "unity":
            thresh_val = 1.0
        else:
            thresh_val = float(val_str)
    else:
        return None

    # Position
    if isinstance(thresh_val, (int, float)):
        bullish = signal < thresh_val if counter_cyclical else signal > thresh_val
    else:
        bullish = signal < thresh_val if counter_cyclical else signal > thresh_val

    strat_code = summary["strategy_code"]
    if strat_code in ("P1", "P1_long_cash"):
        position = bullish.astype(float)
    elif strat_code in ("P2", "P2_signal_strength"):
        is_daily = "vix" in pair_id or "ted" in pair_id
        window = 252 if is_daily else 60
        smin = signal.rolling(window, min_periods=int(window * 0.8)).min()
        smax = signal.rolling(window, min_periods=int(window * 0.8)).max()
        sr = (smax - smin).replace(0, np.nan)
        if counter_cyclical:
            position = (1 - (signal - smin) / sr).clip(0, 1)
        else:
            position = ((signal - smin) / sr).clip(0, 1)
    elif strat_code in ("P3", "P3_long_short"):
        position = bullish.astype(float) * 2 - 1
    else:
        position = bullish.astype(float)

    # Strategy drawdown
    strat_ret = position.shift(1) * df[ret_col]
    strat_cum = (1 + strat_ret.fillna(0)).cumprod()
    strat_peak = strat_cum.cummax()
    strat_dd = ((strat_cum - strat_peak) / strat_peak) * 100  # percentage

    # Buy-and-hold drawdown
    bh_cum = (1 + df[ret_col].fillna(0)).cumprod()
    bh_peak = bh_cum.cummax()
    bh_dd = ((bh_cum - bh_peak) / bh_peak) * 100

    return df.index, strat_dd, bh_dd


def create_drawdown_chart(pair_id: str, dates, strat_dd, bh_dd,
                          summary: dict) -> go.Figure:
    """Create a Plotly drawdown comparison chart following Vera's SOP standards."""
    sig_display = summary["signal_display_name"]
    strat_display = summary["strategy_display_name"]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=bh_dd,
        name="Buy-and-Hold SPY",
        line=dict(color=BENCHMARK_COLOR, width=1),
        fill="tozeroy",
        fillcolor="rgba(153,153,153,0.15)",
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=strat_dd,
        name=f"Strategy ({sig_display} / {strat_display})",
        line=dict(color=STRATEGY_COLOR, width=1.5),
        fill="tozeroy",
        fillcolor="rgba(0,114,178,0.15)",
    ))

    fig.add_hline(y=0, line_dash="dot", line_color=ZERO_LINE_COLOR, line_width=0.5)

    fig.update_layout(
        title=dict(
            text=f"Drawdown Comparison: {pair_id.upper().replace('_', ' ')}",
            font=dict(size=14),
        ),
        yaxis=dict(
            title="Drawdown (%)",
            ticksuffix="%",
            range=[min(bh_dd.min(), strat_dd.min()) * 1.1, 5],
        ),
        xaxis=dict(title=""),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        template="plotly_white",
        height=350,
        margin=dict(l=60, r=20, t=60, b=40),
    )

    return fig


def process_pair(pair_id: str) -> bool:
    """Generate drawdown chart for a single pair. Returns True on success."""
    summary = load_winner_summary(pair_id)
    if summary is None:
        print(f"  ⚠ No winner_summary.json — run generate_winner_outputs.py first")
        return False

    df = load_pair_data(pair_id)
    if df is None:
        print(f"  ⚠ No data parquet found")
        return False

    result = reconstruct_drawdowns(pair_id, summary, df)
    if result is None:
        print(f"  ⚠ Could not reconstruct drawdowns")
        return False

    dates, strat_dd, bh_dd = result
    fig = create_drawdown_chart(pair_id, dates, strat_dd, bh_dd, summary)

    # Save to correct chart directory
    chart_dir = os.path.join(BASE, "output", "charts", pair_id, "plotly")
    os.makedirs(chart_dir, exist_ok=True)
    chart_path = os.path.join(chart_dir, f"{pair_id}_drawdown.json")
    with open(chart_path, "w") as f:
        f.write(pio.to_json(fig))

    print(f"  ✓ {pair_id}_drawdown.json")
    return True


def main():
    results_dir = os.path.join(BASE, "results")
    pairs = []
    for name in sorted(os.listdir(results_dir)):
        pair_path = os.path.join(results_dir, name)
        if not os.path.isdir(pair_path):
            continue
        if os.path.exists(os.path.join(pair_path, "winner_summary.json")):
            pairs.append(name)

    if not pairs:
        print("No pairs with winner_summary.json found.")
        print("Run scripts/generate_winner_outputs.py first.")
        sys.exit(1)

    print(f"Processing {len(pairs)} pairs: {', '.join(pairs)}\n")

    success = 0
    for pair_id in pairs:
        print(f"[{pair_id}]")
        if process_pair(pair_id):
            success += 1
        print()

    print(f"Generated {success}/{len(pairs)} drawdown charts.")


if __name__ == "__main__":
    main()
