"""Reconstruct and export trading history for tournament winners."""

import os
import numpy as np
import pandas as pd


BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")


def reconstruct_winner_history(pair_id: str, date_tag: str = "20260314") -> pd.DataFrame | None:
    """Reconstruct daily trading history for the tournament winner.

    Returns DataFrame with columns: date, signal_value, threshold_value,
    position, spy_return, strategy_return, cumulative_return, drawdown.
    Returns None if data is unavailable.
    """
    # Load tournament results to find the winner
    tourn_path = os.path.join(BASE, "results", pair_id, f"tournament_results_{date_tag}.csv")
    if not os.path.exists(tourn_path):
        return None

    tdf = pd.read_csv(tourn_path)
    valid = tdf[tdf["valid"] & (tdf["signal"] != "BENCHMARK")]
    if len(valid) == 0:
        return None

    winner = valid.loc[valid["oos_sharpe"].idxmax()]

    # Load dataset
    data_files = [f for f in os.listdir(os.path.join(BASE, "data"))
                  if f.startswith(pair_id) and f.endswith(".parquet")]
    if not data_files:
        return None

    df = pd.read_parquet(os.path.join(BASE, "data", data_files[0]))

    # Determine OOS period from the dataset
    # Heuristic: find IS/OOS split from the winner's oos_n
    oos_n = int(winner["oos_n"])

    # Determine signal column
    sig_name = winner["signal"]
    # Map signal name to column
    signal_map = {}
    for col in df.columns:
        # Build reverse mapping from tournament signal names to columns
        short = col.replace("indpro_", "").replace("permit_", "").replace("vix_ratio_", "VR_").replace("spread_", "")
        signal_map[col] = col

    # Try to find the signal column
    sig_col = None
    # Common patterns from our pipelines
    sig_mappings = {
        "S1_level": lambda: next((c for c in df.columns if c in ["indpro", "permit", "spread", "vix_ratio"]), None),
        "S2_yoy": lambda: next((c for c in df.columns if "yoy" in c and "fwd" not in c), None),
        "S3_mom": lambda: next((c for c in df.columns if c.endswith("_mom") and "fwd" not in c), None),
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
        sig_col = sig_mappings[sig_name]()
    if sig_col is None:
        # Direct column name match
        for col in df.columns:
            if sig_name.lower().replace("s", "").replace("_", "") in col.lower().replace("_", ""):
                sig_col = col
                break
    if sig_col is None:
        return None

    # Get SPY return column
    ret_col = "spy_ret"
    if ret_col not in df.columns:
        if "spy" in df.columns:
            df["spy_ret"] = df["spy"].pct_change()
            ret_col = "spy_ret"
        else:
            return None

    # Apply lead
    lead_col = "lead_months" if "lead_months" in winner.index else "lead_days"
    lead = int(winner[lead_col])
    signal = df[sig_col].shift(lead) if lead > 0 else df[sig_col]

    # Apply threshold
    thresh_name = winner["threshold"]
    thresh_val = None

    # Determine IS period (everything before OOS)
    n_total = len(df)
    oos_start_idx = n_total - oos_n
    is_data = df.iloc[:oos_start_idx]

    if thresh_name.startswith("T1_p"):
        pct = int(thresh_name.split("p")[1])
        is_signal = signal.iloc[:oos_start_idx].dropna()
        thresh_val = is_signal.quantile(pct / 100)
    elif thresh_name.startswith("T2_rp"):
        pct = int(thresh_name.split("p")[1])
        window = 252 if "daily" in data_files[0] or "vix" in pair_id or "ted" in pair_id else 60
        thresh_val = signal.rolling(window, min_periods=int(window * 0.8)).quantile(pct / 100)
    elif thresh_name == "T4_zero":
        thresh_val = 0
    elif thresh_name == "T4_unity":
        thresh_val = 1.0
    else:
        return None

    # Determine direction (counter-cyclical: below = bullish; pro-cyclical: above = bullish)
    interp_path = os.path.join(BASE, "results", pair_id, "interpretation_metadata.json")
    counter_cyclical = False
    if os.path.exists(interp_path):
        import json
        with open(interp_path) as f:
            interp = json.load(f)
            counter_cyclical = interp.get("expected_direction") == "counter_cyclical"

    if isinstance(thresh_val, (int, float)):
        if counter_cyclical:
            bullish = signal < thresh_val
        else:
            bullish = signal > thresh_val
    else:
        if counter_cyclical:
            bullish = signal < thresh_val
        else:
            bullish = signal > thresh_val

    # Apply strategy
    strat = winner["strategy"]
    if strat in ["P1", "P1_long_cash"]:
        position = bullish.astype(float)
    elif strat in ["P2", "P2_signal_strength"]:
        window = 252 if "daily" in data_files[0] or "vix" in pair_id or "ted" in pair_id else 60
        smin = signal.rolling(window, min_periods=int(window * 0.8)).min()
        smax = signal.rolling(window, min_periods=int(window * 0.8)).max()
        sr = (smax - smin).replace(0, np.nan)
        if counter_cyclical:
            position = (1 - (signal - smin) / sr).clip(0, 1)
        else:
            position = ((signal - smin) / sr).clip(0, 1)
    elif strat in ["P3", "P3_long_short"]:
        position = bullish.astype(float) * 2 - 1
    else:
        position = bullish.astype(float)

    # Calculate returns
    strat_ret = position.shift(1) * df[ret_col]
    cum_ret = (1 + strat_ret.fillna(0)).cumprod()
    rolling_max = cum_ret.cummax()
    drawdown = (cum_ret - rolling_max) / rolling_max

    # Build output
    history = pd.DataFrame({
        "date": df.index,
        "signal_value": signal.values,
        "position": position.values,
        "spy_daily_return": df[ret_col].values,
        "strategy_daily_return": strat_ret.values,
        "cumulative_return": cum_ret.values,
        "drawdown": drawdown.values,
    })
    history = history.dropna(subset=["strategy_daily_return"])

    # Add metadata as attributes (for display)
    history.attrs["winner_signal"] = sig_name
    history.attrs["winner_threshold"] = thresh_name
    history.attrs["winner_strategy"] = strat
    history.attrs["winner_lead"] = lead
    history.attrs["pair_id"] = pair_id

    return history
