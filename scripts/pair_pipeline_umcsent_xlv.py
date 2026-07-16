#!/usr/bin/env python3
"""
Full Analysis Pipeline: University of Michigan Consumer Sentiment (UMCSENT) × XLV
=====================================================================
Priority pair: sentiment indicator vs defensive health care ETF.

Expected direction: procyclical — high or improving consumer sentiment should
support stronger XLV returns, while weak or falling sentiment should reduce
XLV exposure.

Stages:
  1. Data sourcing (FRED + Yahoo) + calendar alignment
  2. Derived series computation
  3. Stationarity tests + quality reports
  4. Exploratory analysis (correlations, CCF, regime stats)
  5. Core econometric models (9 categories)
  6. Tournament backtest (5D combinatorial)
  7. Tournament validation (walk-forward, bootstrap, stress tests)

Author: Econ Evan (Econometrics Agent)
Date: 2026-04-20
Pair ID: umcsent_xlv
"""

import os
import sys
import json
import warnings
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PAIR_ID = "umcsent_xlv"
INDICATOR_NAME = "University of Michigan Consumer Sentiment"
TARGET_NAME = "Health Care Select Sector (XLV)"
START_DATE = "1998-01-01"
END_DATE = "2025-12-31"
DATE_TAG = "20260711"  # GH#13 full L0-12 grid (free selection per Lead-Grid Frequency Standard 2026-07-14; retired the interim Option-C L0-6 cap). Immutable tournament re-used; winner unchanged (L6=1.1586). Prior L0-6 run: 20260420.
EXPECTED_DIRECTION = "procyclical"

BASE_DIR = str(Path(__file__).resolve().parents[1])
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")

for d in [DATA_DIR, RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

# OOS split: computed dynamically after data load (ECON-OOS2)
# OOS window = min(max(36, round(N*0.25)), 120) months from end
IS_END = None   # set in stage 2
OOS_START = None  # set in stage 2

STAGE_TIMES = {}

SIGNAL_COLUMN_MAP = {
    "S1_level": "umcsent",
    "S2_yoy": "umcsent_yoy",
    "S3_mom": "umcsent_mom",
    "S4_zscore": "umcsent_zscore",
    "S5_3m_ma": "umcsent_3m_ma",
    "S6_direction": "umcsent_direction",
    "S7_dev_ma": "umcsent_dev_ma",
}


def bullish_condition(signal, threshold):
    """Return the XLV-bullish condition implied by EXPECTED_DIRECTION."""
    if EXPECTED_DIRECTION == "procyclical":
        return signal > threshold
    if EXPECTED_DIRECTION in {"countercyclical", "counter_cyclical"}:
        return signal < threshold
    raise ValueError(f"Unsupported EXPECTED_DIRECTION: {EXPECTED_DIRECTION}")


def signal_strength_position(signal):
    """Scale signal to [0, 1] with direction-aware exposure."""
    sig_min = signal.rolling(60, min_periods=36).min()
    sig_max = signal.rolling(60, min_periods=36).max()
    sig_range = (sig_max - sig_min).replace(0, np.nan)
    scaled = ((signal - sig_min) / sig_range).clip(0, 1)
    if EXPECTED_DIRECTION == "procyclical":
        return scaled
    return 1 - scaled


def build_threshold(signal, work, sig_col, is_mask, threshold_name):
    """Return the threshold object used by the tournament winner."""
    note = threshold_name
    if "T1_fixed" in threshold_name:
        pct = int(threshold_name.split("p")[1])
        threshold = work.loc[is_mask, sig_col].quantile(pct / 100)
        value = float(threshold)
        note = f"fixed in-sample p{pct}"
    elif "T2_roll" in threshold_name:
        pct = int(threshold_name.split("p")[1])
        threshold = signal.rolling(60, min_periods=36).quantile(pct / 100)
        value = float(threshold.dropna().iloc[-1]) if threshold.dropna().shape[0] else None
        note = f"threshold is rolling (60-month p{pct}); threshold_value is the latest rolling value"
    elif "T3_zscore_neg" in threshold_name:
        k = float(threshold_name.split("_")[-1])
        threshold = signal.rolling(60, min_periods=36).mean() - k * signal.rolling(60, min_periods=36).std()
        value = float(threshold.dropna().iloc[-1]) if threshold.dropna().shape[0] else None
        note = f"threshold is rolling (60-month mean minus {k:g} standard deviation); threshold_value is the latest rolling value"
    elif "T3_zscore" in threshold_name:
        k = float(threshold_name.split("_")[-1])
        threshold = signal.rolling(60, min_periods=36).mean() + k * signal.rolling(60, min_periods=36).std()
        value = float(threshold.dropna().iloc[-1]) if threshold.dropna().shape[0] else None
        note = f"threshold is rolling (60-month mean plus {k:g} standard deviation); threshold_value is the latest rolling value"
    else:
        threshold = 0.0
        value = 0.0
        note = "zero threshold"
    return threshold, value, note


def derive_winner_series(work, winner):
    """Derive the exact position and return series used for the tournament winner."""
    signal_column = SIGNAL_COLUMN_MAP.get(winner["signal"])
    if signal_column is None or signal_column not in work.columns:
        raise KeyError(f"Unknown winner signal column for {winner['signal']}")

    lead = int(winner["lead_months"])
    raw_signal = work[signal_column].copy()
    signal_for_rule = raw_signal.shift(lead) if lead > 0 else raw_signal
    threshold, threshold_value, threshold_note = build_threshold(
        signal_for_rule,
        work,
        signal_column,
        work.index <= IS_END,
        str(winner["threshold"]),
    )

    if winner["strategy"] == "P1_long_cash":
        position = bullish_condition(signal_for_rule, threshold).astype(float)
    elif winner["strategy"] == "P2_signal_strength":
        position = signal_strength_position(signal_for_rule)
    elif winner["strategy"] == "P3_long_short":
        position = bullish_condition(signal_for_rule, threshold).astype(float) * 2 - 1
    else:
        raise ValueError(f"Unsupported strategy: {winner['strategy']}")

    strategy_return = position.shift(1) * work["xlv_ret"]
    return position, strategy_return, signal_for_rule, threshold, threshold_value, threshold_note


def log_stage(name):
    """Decorator to time stages."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            t0 = time.time()
            print(f"\n{'='*70}")
            print(f"  STAGE: {name}")
            print(f"{'='*70}")
            result = func(*args, **kwargs)
            elapsed = time.time() - t0
            STAGE_TIMES[name] = elapsed
            print(f"\n  [{name}] completed in {elapsed:.1f}s")
            return result
        return wrapper
    return decorator


# ===================================================================
# STAGE 1: DATA SOURCING
# ===================================================================

@log_stage("1_data_sourcing")
def stage_data_sourcing():
    """Source UMCSENT (monthly) + XLV (daily) + controls from FRED and Yahoo."""

    # --- FRED series ---
    fred_series = {
        "UMCSENT": "umcsent",   # Michigan Consumer Sentiment (Monthly)
        "UNRATE":  "unrate",    # Unemployment Rate (Monthly)
        "DGS10":   "dgs10",     # 10Y Treasury Yield (Daily)
    }

    load_dotenv()  # repo-root .env; hardcoded fallback removed (key rotated after leak)
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise SystemExit("FRED_API_KEY not set — copy .env.example to .env, or run setup.sh.")
    fred_data = {}

    import urllib.request

    def _fetch_fred_csv(series_id, col_name):
        """Fallback: fetch FRED series via direct CSV download."""
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={START_DATE}&coed={END_DATE}"
        local_path = f"/tmp/fred_{series_id}.csv"
        urllib.request.urlretrieve(url, local_path)
        s = pd.read_csv(local_path, index_col=0, parse_dates=True).iloc[:, 0]
        s = pd.to_numeric(s, errors="coerce")
        s.name = col_name
        return s

    for series_id, col_name in fred_series.items():
        fetched = False
        try:
            from fredapi import Fred
            fred_client = Fred(api_key=api_key)
            s = fred_client.get_series(series_id, observation_start=START_DATE, observation_end=END_DATE)
            s.name = col_name
            s.index = pd.to_datetime(s.index)
            fred_data[col_name] = s.astype(float)
            print(f"  [FRED] {series_id} -> {col_name}: {len(s)} obs, {s.index.min().date()} to {s.index.max().date()}")
            fetched = True
        except Exception as e:
            print(f"  [FRED] {series_id} -> {col_name}: fredapi failed ({e}), trying CSV...")

        if not fetched:
            try:
                s = _fetch_fred_csv(series_id, col_name)
                fred_data[col_name] = s
                print(f"  [CSV]  {series_id} -> {col_name}: {len(s)} obs")
            except Exception as e2:
                print(f"  [CSV]  {series_id} -> {col_name}: FAILED ({e2})")

    # --- Yahoo Finance series ---
    import yfinance as yf
    yahoo_tickers = {
        "XLV":   "xlv",
        "SPY":   "spy",
        "^VIX":  "vix",
    }

    yahoo_data = {}
    for ticker, col_name in yahoo_tickers.items():
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            s = df["Close"].copy()
            s.name = col_name
            s.index = pd.to_datetime(s.index)
            if s.index.tz is not None:
                s.index = s.index.tz_localize(None)
            yahoo_data[col_name] = s.astype(float)
            print(f"  [YF]   {ticker} -> {col_name}: {len(s)} obs, {s.index.min().date()} to {s.index.max().date()}")
        except Exception as e:
            print(f"  [YF]   {ticker} -> {col_name}: FAILED ({e})")

    all_series = {**fred_data, **yahoo_data}
    print(f"\n  Total series sourced: {len(all_series)}/{len(fred_series) + len(yahoo_tickers)}")
    return all_series


# ===================================================================
# STAGE 2: CALENDAR ALIGNMENT + DERIVED SERIES
# ===================================================================

@log_stage("2_alignment_and_derived")
def stage_alignment_and_derived(all_series):
    """
    Build two datasets:
      1. Monthly dataset (UMCSENT native frequency) for econometric models
      2. Daily dataset (XLV native frequency) for tournament backtest
    """
    global IS_END, OOS_START

    monthly_cols = {"umcsent", "unrate"}
    daily_cols = {"xlv", "spy", "vix", "dgs10"}

    monthly_idx = pd.date_range(START_DATE, END_DATE, freq="ME")
    df_monthly = pd.DataFrame(index=monthly_idx)
    df_monthly.index.name = "date"

    for col in monthly_cols:
        if col in all_series:
            s = all_series[col]
            s_monthly = s.resample("ME").last()
            df_monthly[col] = s_monthly.reindex(monthly_idx)

    for col in daily_cols:
        if col in all_series:
            s = all_series[col]
            s_monthly = s.resample("ME").last()
            df_monthly[col] = s_monthly.reindex(monthly_idx)

    # Forward fill gaps (max 2 months)
    df_monthly = df_monthly.ffill(limit=2)

    # Drop before XLV data starts
    df_monthly = df_monthly.dropna(subset=["xlv"], how="all")

    # --- ECON-OOS2: dynamic IS/OOS split ---
    N = len(df_monthly.dropna(subset=["umcsent"]))
    oos_months = min(max(36, round(N * 0.25)), 120)
    is_months = N - oos_months
    all_dates = df_monthly.dropna(subset=["umcsent"]).index
    IS_END = all_dates[is_months - 1]
    OOS_START = all_dates[is_months]
    print(f"  ECON-OOS2 split: N={N}, OOS={oos_months}m, IS ends {IS_END.date()}, OOS starts {OOS_START.date()}")

    # --- Derived series: UMCSENT ---
    u = df_monthly["umcsent"]

    # D1: YoY % change
    df_monthly["umcsent_yoy"] = (u / u.shift(12) - 1) * 100

    # D2: MoM % change
    df_monthly["umcsent_mom"] = (u / u.shift(1) - 1) * 100

    # D3: Rolling 36M z-score
    rm36 = u.rolling(36, min_periods=24)
    df_monthly["umcsent_zscore"] = (u - rm36.mean()) / rm36.std()

    # D4: 3-month moving average
    df_monthly["umcsent_3m_ma"] = u.rolling(3, min_periods=2).mean()

    # D5: Direction (sign of MoM)
    df_monthly["umcsent_direction"] = np.sign(df_monthly["umcsent_mom"])

    # D6: Deviation from 3M MA
    df_monthly["umcsent_dev_ma"] = u - df_monthly["umcsent_3m_ma"]

    # --- Derived series: XLV ---
    x = df_monthly["xlv"]
    df_monthly["xlv_ret"] = x.pct_change()

    # Rolling returns
    df_monthly["xlv_ret_3m"] = x.shift(-3) / x - 1  # forward 3M
    df_monthly["xlv_ret_12m"] = x.shift(-12) / x - 1  # forward 12M

    # Backward rolling vol (annualized)
    df_monthly["xlv_vol_12m"] = df_monthly["xlv_ret"].rolling(12, min_periods=10).std() * np.sqrt(12)

    # Forward XLV returns (for regression targets)
    df_monthly["xlv_fwd_1m"] = x.shift(-1) / x - 1
    df_monthly["xlv_fwd_3m"] = x.shift(-3) / x - 1
    df_monthly["xlv_fwd_6m"] = x.shift(-6) / x - 1
    df_monthly["xlv_fwd_12m"] = x.shift(-12) / x - 1

    # SPY forward returns for comparison
    if "spy" in df_monthly.columns:
        s = df_monthly["spy"]
        df_monthly["spy_ret"] = s.pct_change()
        df_monthly["spy_fwd_1m"] = s.shift(-1) / s - 1

    # --- Daily dataset (for tournament) ---
    bdays = pd.bdate_range(START_DATE, END_DATE)
    df_daily = pd.DataFrame(index=bdays)
    df_daily.index.name = "date"

    for col in daily_cols:
        if col in all_series:
            s = all_series[col].reindex(bdays).ffill(limit=5)
            df_daily[col] = s

    # Forward-fill monthly UMCSENT signals to daily
    for col in monthly_cols:
        if col in all_series:
            s = all_series[col]
            df_daily[col] = s.reindex(bdays).ffill()

    # Recompute UMCSENT derived series at daily frequency
    if "umcsent" in df_daily.columns:
        u_d = df_daily["umcsent"]
        df_daily["umcsent_yoy"] = (u_d / u_d.shift(252) - 1) * 100
        df_daily["umcsent_mom"] = (u_d / u_d.shift(21) - 1) * 100
        rm = u_d.rolling(252 * 3, min_periods=252 * 2)
        df_daily["umcsent_zscore"] = (u_d - rm.mean()) / rm.std()
        df_daily["umcsent_direction"] = np.sign(df_daily["umcsent_mom"])

    # XLV daily forward returns
    if "xlv" in df_daily.columns:
        x_d = df_daily["xlv"]
        df_daily["xlv_fwd_1d"] = x_d.pct_change(1).shift(-1)
        df_daily["xlv_fwd_5d"] = x_d.shift(-5) / x_d - 1
        df_daily["xlv_fwd_21d"] = x_d.shift(-21) / x_d - 1
        df_daily["xlv_fwd_63d"] = x_d.shift(-63) / x_d - 1

    # Drop before UMCSENT/XLV data starts
    df_monthly = df_monthly.dropna(subset=["umcsent", "xlv"], how="all")

    print(f"  Monthly dataset: {df_monthly.shape} ({df_monthly.index.min().date()} to {df_monthly.index.max().date()})")
    print(f"  Daily dataset: {df_daily.shape} ({df_daily.index.min().date()} to {df_daily.index.max().date()})")
    print(f"  Monthly columns: {list(df_monthly.columns)}")

    return df_monthly, df_daily


# ===================================================================
# STAGE 3: STATIONARITY TESTS + QUALITY REPORTS
# ===================================================================

@log_stage("3_stationarity_and_quality")
def stage_stationarity_and_quality(df_monthly, df_daily):
    """Run ADF/KPSS tests and generate quality reports."""
    from arch.unitroot import ADF, KPSS

    test_cols = ["umcsent", "xlv", "spy", "vix", "dgs10",
                 "unrate", "umcsent_yoy", "umcsent_mom", "umcsent_zscore"]

    results = []
    for col in test_cols:
        s = df_monthly[col].dropna() if col in df_monthly.columns else pd.Series(dtype=float)
        if len(s) < 50 and col in df_daily.columns:
            s = df_daily[col].dropna()
        if len(s) < 50:
            results.append({"variable": col, "test": "ADF", "statistic": np.nan,
                           "p_value": np.nan, "conclusion": f"Insufficient data ({len(s)} obs)"})
            continue

        if len(s) > 5000:
            s = s.iloc[::5]

        try:
            adf = ADF(s, max_lags=12)
            results.append({"variable": col, "test": "ADF",
                           "statistic": round(adf.stat, 4),
                           "p_value": round(adf.pvalue, 4),
                           "conclusion": "Stationary" if adf.pvalue < 0.05 else "Non-stationary"})
        except Exception as e:
            results.append({"variable": col, "test": "ADF",
                           "statistic": np.nan, "p_value": np.nan,
                           "conclusion": f"Error: {e}"})

        try:
            kpss = KPSS(s)
            results.append({"variable": col, "test": "KPSS",
                           "statistic": round(kpss.stat, 4),
                           "p_value": round(kpss.pvalue, 4),
                           "conclusion": "Stationary" if kpss.pvalue > 0.05 else "Non-stationary"})
        except Exception as e:
            results.append({"variable": col, "test": "KPSS",
                           "statistic": np.nan, "p_value": np.nan,
                           "conclusion": f"Error: {e}"})

    stat_df = pd.DataFrame(results)
    stat_path = os.path.join(RESULTS_DIR, f"stationarity_tests_{DATE_TAG}.csv")
    stat_df.to_csv(stat_path, index=False)
    print(f"  Stationarity tests: {len(stat_df)} results -> {stat_path}")

    # Summary stats
    summary = df_monthly.describe().T
    summary["skewness"] = df_monthly.skew()
    summary["kurtosis"] = df_monthly.kurtosis()
    summary_path = os.path.join(DATA_DIR, f"summary_stats_{PAIR_ID}_{DATE_TAG}.csv")
    summary.to_csv(summary_path)
    print(f"  Summary stats -> {summary_path}")

    # Missing value report
    lines = [
        f"# Missing Value Report: {INDICATOR_NAME} → {TARGET_NAME}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Monthly dataset:** {df_monthly.shape[0]} rows × {df_monthly.shape[1]} columns",
        "",
        "## Monthly Dataset",
        "",
        "| Column | Missing | Missing % | First Available | Last Available |",
        "|--------|---------|-----------|-----------------|----------------|",
    ]
    for col in sorted(df_monthly.columns):
        missing = df_monthly[col].isna().sum()
        pct = missing / len(df_monthly) * 100
        valid = df_monthly[col].dropna()
        first = valid.index.min().date() if len(valid) > 0 else "N/A"
        last = valid.index.max().date() if len(valid) > 0 else "N/A"
        lines.append(f"| {col} | {missing} | {pct:.1f}% | {first} | {last} |")

    missing_path = os.path.join(DATA_DIR, f"missing_value_report_{PAIR_ID}_{DATE_TAG}.md")
    with open(missing_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  Missing report -> {missing_path}")

    return stat_df


# ===================================================================
# STAGE 4: EXPLORATORY ANALYSIS
# ===================================================================

@log_stage("4_exploratory")
def stage_exploratory(df_monthly):
    """Correlations, CCF, regime descriptive stats."""

    signals = ["umcsent_yoy", "umcsent_mom", "umcsent_zscore",
               "umcsent_3m_ma", "umcsent_direction", "umcsent_dev_ma"]
    fwd_cols = ["xlv_fwd_1m", "xlv_fwd_3m", "xlv_fwd_6m", "xlv_fwd_12m"]

    # --- 4.1 Correlation suite ---
    corr_results = []
    for sig in signals:
        if sig not in df_monthly.columns:
            continue
        for fwd in fwd_cols:
            if fwd not in df_monthly.columns:
                continue
            valid = df_monthly[[sig, fwd]].dropna()
            if len(valid) < 30:
                continue

            x, y = valid[sig], valid[fwd]

            r_p, p_p = stats.pearsonr(x, y)
            corr_results.append({"signal": sig, "horizon": fwd, "method": "Pearson",
                                 "correlation": round(r_p, 4), "p_value": round(p_p, 4),
                                 "n": len(valid)})

            r_s, p_s = stats.spearmanr(x, y)
            corr_results.append({"signal": sig, "horizon": fwd, "method": "Spearman",
                                 "correlation": round(r_s, 4), "p_value": round(p_s, 4),
                                 "n": len(valid)})

    corr_df = pd.DataFrame(corr_results)
    corr_path = os.path.join(EXPLORE_DIR, "correlations.csv")
    corr_df.to_csv(corr_path, index=False)
    print(f"  Correlations: {len(corr_df)} pairs -> {corr_path}")

    # --- 4.2 Cross-correlation function ---
    ccf_results = []
    if "umcsent_yoy" in df_monthly.columns and "xlv_ret" in df_monthly.columns:
        sig = df_monthly["umcsent_yoy"].dropna()
        ret = df_monthly["xlv_ret"].dropna()
        common = sig.index.intersection(ret.index)
        sig = sig.loc[common]
        ret = ret.loc[common]

        if len(sig) > 30:
            sig_std = (sig - sig.mean()) / sig.std()
            ret_std = (ret - ret.mean()) / ret.std()

            for lag in range(-12, 13):
                if lag >= 0:
                    x = sig_std.iloc[:len(sig_std) - lag] if lag > 0 else sig_std
                    y = ret_std.iloc[lag:] if lag > 0 else ret_std
                else:
                    x = sig_std.iloc[-lag:]
                    y = ret_std.iloc[:len(ret_std) + lag]

                if len(x) < 20:
                    continue

                min_len = min(len(x), len(y))
                x = x.iloc[:min_len]
                y = y.iloc[:min_len]

                ccf_val = np.corrcoef(x.values, y.values)[0, 1]
                se = 1.0 / np.sqrt(len(x))
                sig_flag = abs(ccf_val) > 1.96 * se

                ccf_results.append({"lag": lag, "ccf": round(ccf_val, 4),
                                    "se": round(se, 4), "significant": sig_flag})

    ccf_df = pd.DataFrame(ccf_results)
    ccf_path = os.path.join(EXPLORE_DIR, "ccf.csv")
    ccf_df.to_csv(ccf_path, index=False)
    print(f"  CCF: {len(ccf_df)} lags -> {ccf_path}")

    # --- 4.3 Regime descriptive stats ---
    regime_results = []
    if "umcsent_yoy" in df_monthly.columns and "xlv_ret" in df_monthly.columns:
        valid = df_monthly[["umcsent_yoy", "xlv_ret"]].dropna()

        quartiles = pd.qcut(valid["umcsent_yoy"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"])

        for q in ["Q1_low", "Q2", "Q3", "Q4_high"]:
            mask = quartiles == q
            rets = valid.loc[mask, "xlv_ret"]
            if len(rets) < 5:
                continue

            ann_ret = rets.mean() * 12 * 100
            ann_vol = rets.std() * np.sqrt(12) * 100
            sharpe = ann_ret / ann_vol if ann_vol > 0 else 0

            regime_results.append({
                "regime": q,
                "n_months": len(rets),
                "mean_monthly_ret_pct": round(rets.mean() * 100, 3),
                "ann_return_pct": round(ann_ret, 2),
                "ann_vol_pct": round(ann_vol, 2),
                "sharpe": round(sharpe, 3),
                "skewness": round(rets.skew(), 3),
                "kurtosis": round(rets.kurtosis(), 3),
                "min_monthly_pct": round(rets.min() * 100, 2),
                "max_monthly_pct": round(rets.max() * 100, 2),
            })

    regime_df = pd.DataFrame(regime_results)
    regime_path = os.path.join(EXPLORE_DIR, "regime_descriptive_stats.csv")
    regime_df.to_csv(regime_path, index=False)
    print(f"  Regime stats: {len(regime_df)} regimes -> {regime_path}")

    # Print key findings
    if len(corr_df) > 0:
        sig_corrs = corr_df[corr_df["p_value"] < 0.05]
        print(f"\n  Key findings:")
        print(f"    Significant correlations (p<0.05): {len(sig_corrs)} / {len(corr_df)}")
        if len(sig_corrs) > 0:
            best = sig_corrs.loc[sig_corrs["correlation"].abs().idxmax()]
            print(f"    Strongest: {best['signal']} -> {best['horizon']}: r={best['correlation']:.3f} (p={best['p_value']:.4f})")

    if len(regime_df) > 0:
        print(f"    Regime Sharpes: {dict(zip(regime_df['regime'], regime_df['sharpe']))}")

    return corr_df, ccf_df, regime_df


# ===================================================================
# STAGE 5: CORE ECONOMETRIC MODELS
# ===================================================================

@log_stage("5_core_models")
def stage_core_models(df_monthly):
    """Run core econometric models."""
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    model_results = {}

    base_cols = ["umcsent_yoy", "umcsent_mom", "umcsent_zscore",
                 "umcsent_direction", "umcsent_dev_ma",
                 "xlv_ret", "xlv_fwd_1m", "xlv_fwd_3m", "xlv_fwd_6m", "xlv_fwd_12m"]
    ctrl_cols = ["vix", "dgs10", "unrate"]
    all_work_cols = [c for c in base_cols + ctrl_cols if c in df_monthly.columns]
    work = df_monthly[all_work_cols].copy()
    work = work.dropna(subset=["umcsent_yoy", "xlv_ret"])
    print(f"  Working dataset: {work.shape}")

    # --- 5.1 Granger Causality ---
    print("\n  [5.1] Granger Causality...")
    gc_results = []
    try:
        gc_data = work[["umcsent_yoy", "xlv_ret"]].dropna()
        if len(gc_data) > 50:
            gc = grangercausalitytests(gc_data[["xlv_ret", "umcsent_yoy"]], maxlag=6, verbose=False)
            for lag, result in gc.items():
                f_stat = result[0]["ssr_ftest"][0]
                p_val = result[0]["ssr_ftest"][1]
                gc_results.append({"direction": "UMCSENT->XLV", "lag": lag,
                                   "f_statistic": round(f_stat, 4), "p_value": round(p_val, 4),
                                   "significant": p_val < 0.05})

            gc_rev = grangercausalitytests(gc_data[["umcsent_yoy", "xlv_ret"]], maxlag=6, verbose=False)
            for lag, result in gc_rev.items():
                f_stat = result[0]["ssr_ftest"][0]
                p_val = result[0]["ssr_ftest"][1]
                gc_results.append({"direction": "XLV->UMCSENT", "lag": lag,
                                   "f_statistic": round(f_stat, 4), "p_value": round(p_val, 4),
                                   "significant": p_val < 0.05})
    except Exception as e:
        print(f"    Granger causality failed: {e}")

    gc_df = pd.DataFrame(gc_results)
    gc_df.to_csv(os.path.join(MODELS_DIR, "granger_causality.csv"), index=False)
    model_results["granger"] = gc_df
    print(f"    {len(gc_df)} test results saved")

    # --- 5.2 Predictive Regressions (OLS) ---
    print("\n  [5.2] Predictive Regressions...")
    reg_results = []
    for signal in ["umcsent_yoy", "umcsent_mom", "umcsent_zscore"]:
        for horizon in ["xlv_fwd_1m", "xlv_fwd_3m", "xlv_fwd_6m", "xlv_fwd_12m"]:
            valid = work[[signal, horizon]].dropna()
            if len(valid) < 30:
                continue

            X = sm.add_constant(valid[signal])
            y = valid[horizon]

            try:
                model = sm.OLS(y, X).fit(cov_type="HC3")
                reg_results.append({
                    "signal": signal, "horizon": horizon,
                    "coef": round(model.params.iloc[1], 6),
                    "se": round(model.bse.iloc[1], 6),
                    "t_stat": round(model.tvalues.iloc[1], 3),
                    "p_value": round(model.pvalues.iloc[1], 4),
                    "r_squared": round(model.rsquared, 4),
                    "n": model.nobs,
                })
            except Exception as e:
                print(f"    Regression {signal}->{horizon} failed: {e}")

    reg_df = pd.DataFrame(reg_results)
    reg_df.to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    model_results["regressions"] = reg_df
    print(f"    {len(reg_df)} regressions saved")

    # --- 5.3 Local Projections (Jorda) ---
    print("\n  [5.3] Local Projections...")
    lp_results = []
    horizons_map = {"xlv_fwd_1m": 1, "xlv_fwd_3m": 3, "xlv_fwd_6m": 6, "xlv_fwd_12m": 12}

    for horizon_col, h in horizons_map.items():
        valid = work[["umcsent_yoy", horizon_col]].dropna()
        controls = []
        for ctrl in ["vix", "dgs10"]:
            if ctrl in work.columns:
                valid = valid.copy()
                valid[ctrl] = work.loc[valid.index, ctrl]
                controls.append(ctrl)
        valid = valid.dropna()

        if len(valid) < 30:
            continue

        try:
            X_cols = ["umcsent_yoy"] + controls
            X = sm.add_constant(valid[X_cols])
            y = valid[horizon_col]

            nw_lags = int(0.75 * len(valid) ** (1 / 3))
            model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw_lags})

            lp_results.append({
                "horizon_months": h,
                "coef_umcsent_yoy": round(model.params["umcsent_yoy"], 6),
                "se": round(model.bse["umcsent_yoy"], 6),
                "t_stat": round(model.tvalues["umcsent_yoy"], 3),
                "p_value": round(model.pvalues["umcsent_yoy"], 4),
                "ci_lower": round(model.conf_int().loc["umcsent_yoy", 0], 6),
                "ci_upper": round(model.conf_int().loc["umcsent_yoy", 1], 6),
                "r_squared": round(model.rsquared, 4),
                "n": int(model.nobs),
                "nw_lags": nw_lags,
            })
        except Exception as e:
            print(f"    LP at h={h} failed: {e}")

    lp_df = pd.DataFrame(lp_results)
    lp_df.to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    model_results["local_projections"] = lp_df
    print(f"    {len(lp_df)} horizons saved")

    # --- 5.4 Regime-Dependent Local Projections ---
    print("\n  [5.4] Regime-Dependent LPs...")
    regime_lp_results = []
    # Contraction dummy: umcsent below historical median
    work_copy = work.copy()
    if "umcsent_yoy" in work_copy.columns:
        med = work_copy["umcsent_yoy"].median()
        work_copy["umcsent_low"] = (work_copy["umcsent_yoy"] < med).astype(int)

        for horizon_col, h in horizons_map.items():
            valid = work_copy[["umcsent_yoy", "umcsent_low", horizon_col]].dropna()
            if len(valid) < 50:
                continue

            try:
                valid["interact"] = valid["umcsent_yoy"] * valid["umcsent_low"]
                X = sm.add_constant(valid[["umcsent_yoy", "umcsent_low", "interact"]])
                y = valid[horizon_col]

                nw_lags = int(0.75 * len(valid) ** (1 / 3))
                model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw_lags})

                regime_lp_results.append({
                    "horizon_months": h,
                    "coef_umcsent_yoy": round(model.params["umcsent_yoy"], 6),
                    "coef_low_sentiment": round(model.params["umcsent_low"], 6),
                    "coef_interaction": round(model.params["interact"], 6),
                    "p_yoy": round(model.pvalues["umcsent_yoy"], 4),
                    "p_low": round(model.pvalues["umcsent_low"], 4),
                    "p_interaction": round(model.pvalues["interact"], 4),
                    "r_squared": round(model.rsquared, 4),
                    "n": int(model.nobs),
                })
            except Exception as e:
                print(f"    Regime LP at h={h} failed: {e}")

    regime_lp_df = pd.DataFrame(regime_lp_results)
    regime_lp_df.to_csv(os.path.join(MODELS_DIR, "regime_local_projections.csv"), index=False)
    model_results["regime_lp"] = regime_lp_df
    print(f"    {len(regime_lp_df)} regime LPs saved")

    # --- 5.5 Markov-Switching Regression ---
    print("\n  [5.5] Markov-Switching Regression...")
    try:
        ms_data = work[["xlv_ret", "umcsent_yoy"]].dropna()
        if len(ms_data) > 50:
            from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

            ms_model = MarkovRegression(
                ms_data["xlv_ret"], k_regimes=2,
                exog=sm.add_constant(ms_data["umcsent_yoy"]),
                switching_variance=True
            )
            ms_fit = ms_model.fit(maxiter=500, disp=False)

            probs = pd.DataFrame({
                "regime_0_prob": ms_fit.smoothed_marginal_probabilities[0],
                "regime_1_prob": ms_fit.smoothed_marginal_probabilities[1],
            }, index=ms_data.index)
            probs.to_csv(os.path.join(MODELS_DIR, "markov_regime_probs_2state.csv"))

            ms_params = pd.DataFrame({
                "parameter": ms_fit.params.index,
                "value": ms_fit.params.values,
                "se": ms_fit.bse.values if hasattr(ms_fit, "bse") else np.nan,
            })
            ms_params.to_csv(os.path.join(MODELS_DIR, "markov_switching_2state.csv"), index=False)
            model_results["markov_switching"] = ms_params
            print(f"    2-state Markov-Switching converged, {len(ms_params)} parameters")
    except Exception as e:
        print(f"    Markov-Switching failed: {e}")

    # --- 5.6 Quantile Regression ---
    print("\n  [5.6] Quantile Regression...")
    qr_results = []
    valid_qr = work[["umcsent_yoy", "xlv_fwd_3m"]].dropna()
    if len(valid_qr) > 30:
        for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
            try:
                qr_model = smf.quantreg("xlv_fwd_3m ~ umcsent_yoy", data=valid_qr)
                qr_fit = qr_model.fit(q=tau)
                qr_results.append({
                    "quantile": tau,
                    "intercept": round(qr_fit.params["Intercept"], 6),
                    "coef_umcsent_yoy": round(qr_fit.params["umcsent_yoy"], 6),
                    "se": round(qr_fit.bse["umcsent_yoy"], 6),
                    "p_value": round(qr_fit.pvalues["umcsent_yoy"], 4),
                    "ci_lower": round(qr_fit.conf_int().loc["umcsent_yoy", 0], 6),
                    "ci_upper": round(qr_fit.conf_int().loc["umcsent_yoy", 1], 6),
                })
            except Exception as e:
                print(f"    QR at tau={tau} failed: {e}")

    qr_df = pd.DataFrame(qr_results)
    qr_df.to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    model_results["quantile_regression"] = qr_df
    print(f"    {len(qr_df)} quantiles saved")

    # --- 5.7 Cointegration ---
    print("\n  [5.7] Cointegration Test...")
    try:
        from statsmodels.tsa.vector_ar.vecm import coint_johansen

        coint_data = df_monthly[["umcsent", "xlv"]].dropna()
        if len(coint_data) > 50:
            coint_log = np.log(coint_data)
            result = coint_johansen(coint_log, det_order=1, k_ar_diff=2)

            coint_results = []
            for i in range(2):
                coint_results.append({
                    "null_hypothesis": f"r <= {i}",
                    "trace_stat": round(result.lr1[i], 4),
                    "critical_90": round(result.cvt[i, 0], 4),
                    "critical_95": round(result.cvt[i, 1], 4),
                    "critical_99": round(result.cvt[i, 2], 4),
                    "reject_at_95": result.lr1[i] > result.cvt[i, 1],
                })

            coint_df = pd.DataFrame(coint_results)
            coint_df.to_csv(os.path.join(MODELS_DIR, "cointegration.csv"), index=False)
            model_results["cointegration"] = coint_df
            print(f"    Johansen test: trace stats = {[round(x, 2) for x in result.lr1]}")
    except Exception as e:
        print(f"    Cointegration test failed: {e}")

    # --- 5.8 Change-Point Detection ---
    print("\n  [5.8] Change-Point Detection...")
    try:
        import ruptures as rpt

        u_series = df_monthly["umcsent_yoy"].dropna().values
        if len(u_series) > 30:
            algo = rpt.Pelt(model="rbf").fit(u_series)
            change_points = algo.predict(pen=10)

            u_dates = df_monthly["umcsent_yoy"].dropna().index
            cp_results = []
            for cp in change_points[:-1]:
                if cp < len(u_dates):
                    cp_results.append({
                        "index": cp,
                        "date": u_dates[cp].strftime("%Y-%m-%d"),
                        "umcsent_yoy_at_break": round(u_series[cp], 2) if cp < len(u_series) else np.nan,
                    })

            cp_df = pd.DataFrame(cp_results)
            cp_df.to_csv(os.path.join(MODELS_DIR, "change_points.csv"), index=False)
            model_results["change_points"] = cp_df
            print(f"    {len(cp_df)} change points detected")
    except Exception as e:
        print(f"    Change-point detection failed: {e}")

    # --- 5.9 Random Forest (Walk-Forward) ---
    print("\n  [5.9] Random Forest Walk-Forward...")
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score

        feature_cols = [c for c in ["umcsent_yoy", "umcsent_mom", "umcsent_zscore",
                                     "umcsent_direction", "vix", "dgs10", "unrate"]
                        if c in work.columns]

        rf_data = work[feature_cols + ["xlv_fwd_3m"]].dropna()
        rf_data = rf_data.copy()
        rf_data["target"] = (rf_data["xlv_fwd_3m"] > 0).astype(int)

        if len(rf_data) > 100:
            wf_results = []
            feature_importances = []

            rf_data = rf_data.copy()
            rf_data["year"] = rf_data.index.year
            years = sorted(rf_data["year"].unique())

            for test_start_year in range(min(years) + 10, max(years) - 2):
                train_mask = rf_data["year"] < test_start_year
                test_mask = (rf_data["year"] >= test_start_year) & (rf_data["year"] < test_start_year + 3)

                X_train = rf_data.loc[train_mask, feature_cols]
                y_train = rf_data.loc[train_mask, "target"]
                X_test = rf_data.loc[test_mask, feature_cols]
                y_test = rf_data.loc[test_mask, "target"]

                if len(X_train) < 30 or len(X_test) < 10:
                    continue

                rf = RandomForestClassifier(n_estimators=200, max_depth=5,
                                            random_state=42, n_jobs=-1)
                rf.fit(X_train, y_train)
                y_pred = rf.predict(X_test)

                wf_results.append({
                    "test_start": test_start_year,
                    "test_end": test_start_year + 2,
                    "train_n": len(X_train),
                    "test_n": len(X_test),
                    "accuracy": round(accuracy_score(y_test, y_pred), 4),
                    "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
                    "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
                })

                if test_start_year == max(years) - 3:
                    for feat, imp in zip(feature_cols, rf.feature_importances_):
                        feature_importances.append({"feature": feat, "importance": round(imp, 4)})

            wf_df = pd.DataFrame(wf_results)
            wf_df.to_csv(os.path.join(MODELS_DIR, "rf_walk_forward.csv"), index=False)
            model_results["rf_walk_forward"] = wf_df
            print(f"    {len(wf_df)} walk-forward windows, avg accuracy: {wf_df['accuracy'].mean():.3f}")

            if feature_importances:
                fi_df = pd.DataFrame(feature_importances).sort_values("importance", ascending=False)
                fi_df.to_csv(os.path.join(MODELS_DIR, "rf_feature_importance.csv"), index=False)
                model_results["rf_feature_importance"] = fi_df
                print(f"    Feature importances: {dict(zip(fi_df['feature'].head(3), fi_df['importance'].head(3)))}")
    except Exception as e:
        print(f"    Random Forest failed: {e}")

    # --- 5.10 Diagnostics ---
    print("\n  [5.10] Diagnostics Summary...")
    diag_results = []

    valid_diag = work[["umcsent_yoy", "xlv_fwd_3m"]].dropna()
    if len(valid_diag) > 30:
        X = sm.add_constant(valid_diag["umcsent_yoy"])
        y = valid_diag["xlv_fwd_3m"]
        base_model = sm.OLS(y, X).fit()
        resid = base_model.resid

        jb_stat, jb_p = stats.jarque_bera(resid)
        diag_results.append({"test": "Jarque-Bera (normality)", "statistic": round(jb_stat, 4),
                              "p_value": round(jb_p, 4),
                              "conclusion": "Normal" if jb_p > 0.05 else "Non-normal residuals"})

        try:
            from statsmodels.stats.diagnostic import het_breuschpagan
            bp_stat, bp_p, _, _ = het_breuschpagan(resid, X)
            diag_results.append({"test": "Breusch-Pagan (heteroskedasticity)",
                                  "statistic": round(bp_stat, 4), "p_value": round(bp_p, 4),
                                  "conclusion": "Homoskedastic" if bp_p > 0.05 else "Heteroskedastic"})
        except Exception:
            pass

        try:
            from statsmodels.stats.diagnostic import acorr_breusch_godfrey
            bg_stat, bg_p, _, _ = acorr_breusch_godfrey(base_model, nlags=4)
            diag_results.append({"test": "Breusch-Godfrey (serial correlation)",
                                  "statistic": round(bg_stat, 4), "p_value": round(bg_p, 4),
                                  "conclusion": "No autocorrelation" if bg_p > 0.05 else "Serial correlation present"})
        except Exception:
            pass

        from statsmodels.stats.stattools import durbin_watson
        dw = durbin_watson(resid)
        diag_results.append({"test": "Durbin-Watson", "statistic": round(dw, 4),
                              "p_value": np.nan,
                              "conclusion": f"DW={dw:.2f} (2.0=no autocorrelation)"})

    diag_df = pd.DataFrame(diag_results)
    diag_df.to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)
    model_results["diagnostics"] = diag_df
    print(f"    {len(diag_df)} diagnostic tests saved")

    # --- Observed direction from regression results ---
    observed_direction = "unknown"
    direction_consistent = False
    key_finding = "UMCSENT YoY change predicts XLV forward returns"

    if len(reg_df) > 0:
        best_reg = reg_df.loc[reg_df["p_value"].idxmin()]
        key_finding = (
            f"UMCSENT {best_reg['signal']} predicts {best_reg['horizon']} "
            f"(coef={best_reg['coef']:.4f}, t={best_reg['t_stat']:.2f}, "
            f"p={best_reg['p_value']:.4f}, R²={best_reg['r_squared']:.3f})"
        )
        observed_direction = "procyclical" if best_reg["coef"] > 0 else "countercyclical"
        direction_consistent = observed_direction == EXPECTED_DIRECTION

    # Save interpretation metadata
    interpretation = {
        "schema_version": "1.0.0",
        "pair_id": PAIR_ID,
        "indicator": "umcsent",
        "target": "xlv",
        "indicator_nature": "leading",
        "indicator_type": "sentiment",
        "strategy_objective": "min_mdd",
        "expected_direction": EXPECTED_DIRECTION,
        "observed_direction": observed_direction,
        "direction_consistent": direction_consistent,
        "key_finding": key_finding,
        "owner_writes": {
            "dana": ["indicator", "target"],
            "evan": ["indicator_nature", "indicator_type", "strategy_objective"],
            "ray": ["key_finding"]
        },
        "last_updated_by": "evan",
        "last_updated_at": "2026-04-20T00:00:00Z",
    }

    interp_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    with open(interp_path, "w") as f:
        json.dump(interpretation, f, indent=2)
    print(f"\n  Interpretation metadata -> {interp_path}")

    return model_results


# ===================================================================
# STAGE 6: TOURNAMENT BACKTEST
# ===================================================================

@log_stage("6_tournament")
def stage_tournament(df_monthly, df_daily):
    """5D combinatorial tournament backtest."""

    work = df_monthly.copy()
    work = work.dropna(subset=["umcsent"])

    is_mask = work.index <= IS_END
    oos_mask = work.index >= OOS_START

    # Signal columns (UMCSENT derivatives only — ECON-SD)
    signal_cols = {
        "S1_level":      "umcsent",
        "S2_yoy":        "umcsent_yoy",
        "S3_mom":        "umcsent_mom",
        "S4_zscore":     "umcsent_zscore",
        "S5_3m_ma":      "umcsent_3m_ma",
        "S6_direction":  "umcsent_direction",
        "S7_dev_ma":     "umcsent_dev_ma",
    }

    available_signals = {k: v for k, v in signal_cols.items()
                        if v in work.columns and work[v].notna().sum() > 50}
    print(f"  Available signals: {len(available_signals)}")

    # XLV monthly return for backtest
    if "xlv_ret" not in work.columns:
        if "xlv" in work.columns:
            work["xlv_ret"] = work["xlv"].pct_change()
        else:
            print("  ERROR: No XLV data for tournament")
            return pd.DataFrame()

    # Full anchored monthly grid L0-12 per the Lead-Grid Frequency Standard
    # (docs/lead-grid-frequency-standard.md, adopted 2026-07-14). The math selects
    # the winner over the FULL grid with NO economic-window cap; the 2-5-month
    # cross-correlation window is REFERENCE context only (Step 5), never a selection
    # constraint. This retires the interim Option-C L0-6 capped-selection pattern:
    # a long-lead derivative (e.g. umcsent_direction, significant at L10 in the
    # per-transform lead-correlation table) is TESTED and, if it wins, ADJUDICATED
    # (Step 4 / ECON-T5) — not pre-excluded.
    lead_times = list(range(0, 13))
    strategies = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]

    results = []
    combo_count = 0

    for sig_name, sig_col in available_signals.items():
        signal = work[sig_col].copy()
        if signal.dropna().shape[0] < 50:
            continue

        for lead in lead_times:
            signal_lagged = signal.shift(lead) if lead > 0 else signal

            thresholds = {}

            is_signal = signal_lagged[is_mask].dropna()
            if len(is_signal) > 20:
                for pct in [25, 50, 75]:
                    thresholds[f"T1_fixed_p{pct}"] = is_signal.quantile(pct / 100)

            for pct in [25, 50, 75]:
                thresholds[f"T2_roll_p{pct}"] = signal_lagged.rolling(60, min_periods=36).quantile(pct / 100)

            roll_mean = signal_lagged.rolling(60, min_periods=36).mean()
            roll_std = signal_lagged.rolling(60, min_periods=36).std()
            for k in [1.0, 1.5, 2.0]:
                thresholds[f"T3_zscore_{k}"] = roll_mean + k * roll_std
                thresholds[f"T3_zscore_neg_{k}"] = roll_mean - k * roll_std

            if sig_name in ["S2_yoy", "S3_mom", "S7_dev_ma"]:
                thresholds["T4_zero"] = 0

            for thresh_name, thresh_val in thresholds.items():
                for strat in strategies:
                    combo_count += 1

                    try:
                        bullish = bullish_condition(signal_lagged, thresh_val)

                        if strat == "P1_long_cash":
                            position = bullish.astype(float)
                        elif strat == "P2_signal_strength":
                            position = signal_strength_position(signal_lagged)
                        elif strat == "P3_long_short":
                            position = bullish.astype(float) * 2 - 1
                        else:
                            continue

                        strat_ret = position.shift(1) * work["xlv_ret"]

                        # ECON-T4 deployable-series scoring (GH#13): score OOS on the DEPLOYABLE
                        # series — an undefined in-window position deploys as CASH (0), not dropped.
                        # OOS opens ~15yr past every combo's warmup, so any in-window NaN is a
                        # degenerate-signal month (e.g. P2 signal-strength on the ternary S6_direction
                        # flag). Cash-fill == the deployable series the winner_summary/charts use.
                        # IS stays dropna (reported only; its window spans warmup).
                        is_ret = strat_ret[is_mask].dropna()
                        oos_ret = strat_ret[oos_mask].fillna(0.0)

                        if len(is_ret) < 24 or len(oos_ret) < 12:
                            continue

                        is_sharpe = (is_ret.mean() / is_ret.std()) * np.sqrt(12) if is_ret.std() > 0 else 0

                        oos_ann_vol = oos_ret.std() * np.sqrt(12) if oos_ret.std() > 0 else 999
                        oos_sharpe = (oos_ret.mean() / oos_ret.std()) * np.sqrt(12) if oos_ret.std() > 0 else 0

                        oos_downside = oos_ret[oos_ret < 0].std() * np.sqrt(12) if len(oos_ret[oos_ret < 0]) > 1 else 999
                        oos_sortino = (oos_ret.mean() * 12) / oos_downside if oos_downside > 0 else 0

                        cum_ret = (1 + oos_ret).cumprod()
                        rolling_max = cum_ret.cummax()
                        drawdown = (cum_ret - rolling_max) / rolling_max
                        max_dd = drawdown.min()

                        oos_calmar = (oos_ret.mean() * 12) / abs(max_dd) if abs(max_dd) > 0 else 0

                        pos_changes = position.diff().abs().sum()
                        years = len(position.dropna()) / 12
                        annual_turnover = pos_changes / years if years > 0 else 999

                        win_rate = (oos_ret > 0).mean()
                        valid_flag = (oos_sharpe > 0 and annual_turnover < 24 and len(oos_ret) >= 12)

                        results.append({
                            "signal": sig_name,
                            "threshold": thresh_name,
                            "strategy": strat,
                            "lead_months": lead,
                            "is_sharpe": round(is_sharpe, 4),
                            "oos_sharpe": round(oos_sharpe, 4),
                            "oos_sortino": round(oos_sortino, 4),
                            "oos_calmar": round(oos_calmar, 4),
                            "oos_ann_return": round(oos_ret.mean() * 12, 6),  # ratio form (META-UC)
                            "oos_ann_vol": round(oos_ann_vol, 6),
                            "max_drawdown": round(max_dd, 6),  # ratio form (META-UC)
                            "win_rate": round(win_rate, 4),
                            "annual_turnover": round(annual_turnover, 2),
                            "is_n": len(is_ret),
                            "oos_n": len(oos_ret),
                            "valid": valid_flag,
                        })
                    except Exception:
                        continue

    # Add benchmark (buy-and-hold XLV)
    bh_ret = work["xlv_ret"]
    bh_oos = bh_ret[oos_mask].dropna()
    if len(bh_oos) > 0:
        bh_sharpe = (bh_oos.mean() / bh_oos.std()) * np.sqrt(12) if bh_oos.std() > 0 else 0
        bh_cum = (1 + bh_oos).cumprod()
        bh_dd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min()

        bh_is = bh_ret[is_mask].dropna()
        bh_is_sharpe = (bh_is.mean() / bh_is.std()) * np.sqrt(12) if bh_is.std() > 0 else 0

        results.append({
            "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BUY_HOLD",
            "lead_months": 0,
            "is_sharpe": round(bh_is_sharpe, 4),
            "oos_sharpe": round(bh_sharpe, 4),
            "oos_sortino": round((bh_oos.mean() * 12) / (bh_oos[bh_oos < 0].std() * np.sqrt(12)) if len(bh_oos[bh_oos < 0]) > 1 else 0, 4),
            "oos_calmar": round((bh_oos.mean() * 12) / abs(bh_dd) if abs(bh_dd) > 0 else 0, 4),
            "oos_ann_return": round(bh_oos.mean() * 12, 6),
            "oos_ann_vol": round(bh_oos.std() * np.sqrt(12), 6),
            "max_drawdown": round(bh_dd, 6),
            "win_rate": round((bh_oos > 0).mean(), 4),
            "annual_turnover": 0,
            "is_n": len(bh_is),
            "oos_n": len(bh_oos),
            "valid": False,
        })

    results_df = pd.DataFrame(results)
    results_path = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    results_df.to_csv(results_path, index=False)

    valid_count = results_df["valid"].sum() if len(results_df) > 0 else 0
    print(f"\n  Tournament Summary:")
    print(f"    Combinations tested: {combo_count}")
    print(f"    Results saved: {len(results_df)}")
    print(f"    Valid strategies: {valid_count}")

    if len(results_df) > 0:
        valid_strats = results_df[results_df["valid"] & (results_df["signal"] != "BENCHMARK")]
        if len(valid_strats) > 0:
            top5 = valid_strats.nlargest(5, "oos_sharpe")
            print(f"\n    Top 5 strategies:")
            for _, row in top5.iterrows():
                print(f"      {row['signal']} / {row['threshold']} / {row['strategy']} / L{row['lead_months']}: "
                      f"Sharpe={row['oos_sharpe']:.2f}, DD={row['max_drawdown']*100:.1f}%, Turnover={row['annual_turnover']:.1f}")

        bh = results_df[results_df["signal"] == "BENCHMARK"]
        if len(bh) > 0:
            print(f"\n    Buy-and-hold XLV benchmark: Sharpe={bh.iloc[0]['oos_sharpe']:.2f}, DD={bh.iloc[0]['max_drawdown']*100:.1f}%")

    return results_df


# ===================================================================
# STAGE 7: TOURNAMENT VALIDATION
# ===================================================================

@log_stage("7_validation")
def stage_validation(df_monthly, tournament_df):
    """Validate top 5 tournament winners."""

    if len(tournament_df) == 0:
        print("  No tournament results to validate")
        return

    valid_strats = tournament_df[tournament_df["valid"] & (tournament_df["signal"] != "BENCHMARK")]
    if len(valid_strats) == 0:
        print("  No valid strategies to validate")
        return

    top5 = valid_strats.nlargest(5, "oos_sharpe")

    # --- 7.1 Bootstrap ---
    print("\n  [7.1] Bootstrap significance test...")
    bootstrap_results = []

    work = df_monthly.copy()
    oos_mask = work.index >= OOS_START
    xlv_oos = work.loc[oos_mask, "xlv_ret"].dropna()

    if len(xlv_oos) > 12:
        n_bootstrap = 5000
        bootstrap_sharpes = np.zeros(n_bootstrap)

        for b in range(n_bootstrap):
            sample = np.random.choice(xlv_oos.values, size=len(xlv_oos), replace=True)
            if np.std(sample) > 0:
                bootstrap_sharpes[b] = (np.mean(sample) / np.std(sample)) * np.sqrt(12)

        for _, row in top5.iterrows():
            p_value = (bootstrap_sharpes >= row["oos_sharpe"]).mean()
            bootstrap_results.append({
                "signal": row["signal"],
                "threshold": row["threshold"],
                "strategy": row["strategy"],
                "oos_sharpe": row["oos_sharpe"],
                "bootstrap_p_value": round(p_value, 4),
                "significant_at_5pct": p_value < 0.05,
            })

    boot_df = pd.DataFrame(bootstrap_results)
    boot_df.to_csv(os.path.join(VALID_DIR, "bootstrap.csv"), index=False)
    print(f"    {len(boot_df)} strategies tested")

    # --- 7.2 Stress tests ---
    print("\n  [7.2] Stress tests...")
    stress_periods = {
        "Dot_Com_Bust": ("2000-03-01", "2002-09-30"),
        "GFC": ("2008-01-01", "2009-06-30"),
        "COVID": ("2020-01-01", "2020-06-30"),
        "Rate_Hike_2022": ("2022-01-01", "2023-06-30"),
    }

    stress_results = []
    for period_name, (start, end) in stress_periods.items():
        stress_mask = (work.index >= start) & (work.index <= end)
        stress_ret = work.loc[stress_mask, "xlv_ret"].dropna()

        if len(stress_ret) > 3:
            bh_sharpe = (stress_ret.mean() / stress_ret.std()) * np.sqrt(12) if stress_ret.std() > 0 else 0
            stress_results.append({
                "period": period_name,
                "start": start,
                "end": end,
                "n_months": len(stress_ret),
                "buy_hold_sharpe": round(bh_sharpe, 4),
                "buy_hold_return_pct": round(stress_ret.sum() * 100, 2),
            })

    stress_df = pd.DataFrame(stress_results)
    stress_df.to_csv(os.path.join(VALID_DIR, "stress_tests.csv"), index=False)
    print(f"    {len(stress_df)} stress periods analyzed")

    # --- 7.3 Transaction cost sensitivity ---
    print("\n  [7.3] Transaction cost sensitivity...")
    tx_results = []

    for _, row in top5.iterrows():
        for tx_bps in [0, 5, 10, 25, 50]:
            annual_cost = row["annual_turnover"] * (tx_bps / 10000) * 12
            net_sharpe = row["oos_sharpe"] - (annual_cost * np.sqrt(12) if row.get("oos_ann_vol", 0) > 0 else 0)

            tx_results.append({
                "signal": row["signal"],
                "threshold": row["threshold"],
                "strategy": row["strategy"],
                "tx_cost_bps": tx_bps,
                "gross_sharpe": row["oos_sharpe"],
                "net_sharpe_approx": round(net_sharpe, 4),
            })

    tx_df = pd.DataFrame(tx_results)
    tx_df.to_csv(os.path.join(VALID_DIR, "transaction_costs.csv"), index=False)
    print(f"    {len(tx_df)} cost scenarios tested")

    return boot_df


# ===================================================================
# MAIN PIPELINE
# ===================================================================

def main():
    pipeline_start = time.time()

    print("=" * 70)
    print(f"  PAIR PIPELINE: {INDICATOR_NAME} → {TARGET_NAME}")
    print(f"  Pair ID: {PAIR_ID}")
    print(f"  Date: {DATE_TAG}")
    print(f"  Sample: {START_DATE} to {END_DATE}")
    print("=" * 70)

    # Stage 1
    all_series = stage_data_sourcing()

    # Stage 2
    df_monthly, df_daily = stage_alignment_and_derived(all_series)

    # Save datasets
    monthly_path = os.path.join(DATA_DIR, f"umcsent_xlv_monthly_{START_DATE.replace('-','')}_{END_DATE.replace('-','')}.parquet")
    df_monthly.to_parquet(monthly_path, engine="pyarrow")
    print(f"\n  Monthly dataset saved: {monthly_path}")

    # Stage 3
    stat_df = stage_stationarity_and_quality(df_monthly, df_daily)

    # Stage 4
    corr_df, ccf_df, regime_df = stage_exploratory(df_monthly)

    # Stage 5
    model_results = stage_core_models(df_monthly)

    # Stage 6
    tournament_df = stage_tournament(df_monthly, df_daily)

    # Stage 7
    stage_validation(df_monthly, tournament_df)

    # --- Winner summary ---
    winner_summary = {}
    if len(tournament_df) > 0:
        valid_strats = tournament_df[tournament_df["valid"] & (tournament_df["signal"] != "BENCHMARK")]
        bh = tournament_df[tournament_df["signal"] == "BENCHMARK"]

        if len(valid_strats) > 0:
            # FREE full-grid selection per the Lead-Grid Frequency Standard
            # (docs/lead-grid-frequency-standard.md, 2026-07-14): NO economic-window
            # cap. The published winner is the global max valid OOS-Sharpe combo over
            # the full L0-12 grid; the 2-5-month window is REFERENCE only. (This retires
            # the interim Option-C L0-6 cap. Verified winner-unchanged: L6 is already the
            # full-grid global max at 1.1586 vs best L7-12 = 1.033.) A surprising long
            # lead, if it won, would be ADJUDICATED (Step 4 / ECON-T5), not pre-excluded.
            best = valid_strats.loc[valid_strats["oos_sharpe"].idxmax()]
            work_for_summary = df_monthly.dropna(subset=["umcsent"])
            oos_mask_summary = work_for_summary.index >= OOS_START
            signal_column = SIGNAL_COLUMN_MAP.get(best["signal"])
            oos_period_start = OOS_START.strftime("%Y-%m-%d")
            oos_period_end = work_for_summary.loc[oos_mask_summary].index.max().strftime("%Y-%m-%d")

            position, strategy_return, signal_for_rule, threshold_obj, threshold_value, threshold_note = derive_winner_series(
                work_for_summary,
                best,
            )
            oos_position = position.loc[oos_mask_summary].dropna()
            oos_n_trades = int(oos_position.diff().abs().fillna(0).gt(0).sum())
            threshold_is_rolling = isinstance(threshold_obj, pd.Series)
            threshold_note_contract = (
                f"{threshold_note} - see winner_trade_log.csv for the full threshold path"
                if threshold_is_rolling else threshold_note
            )
            threshold_rule = "gt" if EXPECTED_DIRECTION == "procyclical" else "lt"
            strategy_display = {
                "P1_long_cash": "Long/Cash",
                "P2_signal_strength": "Signal-strength sizing",
                "P3_long_short": "Long/Short",
            }.get(best["strategy"], str(best["strategy"]))

            winner_summary = {
                "pair_id": PAIR_ID,
                "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                "signal_column": signal_column,
                "signal_code": best["signal"],
                "signal_display_name": "UMCSENT 3-month momentum" if best["signal"] == "S3_mom" else best["signal"],
                "target_symbol": "XLV",
                "threshold_code": best["threshold"],
                "threshold_value": round(float(threshold_value), 6) if threshold_value is not None else None,
                "threshold_rule": threshold_rule,
                "threshold_note": threshold_note_contract,
                "strategy_family": best["strategy"],
                "strategy_code": str(best["strategy"]).split("_")[0],
                "strategy_display_name": strategy_display,
                "strategy_description": (
                    f"Long XLV when the {int(best['lead_months'])}-month-lagged UMCSENT 3-month momentum "
                    f"is {threshold_rule} its rolling threshold; otherwise cash."
                ),
                "direction": EXPECTED_DIRECTION,
                "signal": best["signal"],
                "threshold": best["threshold"],
                "strategy": best["strategy"],
                "lead_months": int(best["lead_months"]),
                "lead_value": int(best["lead_months"]),
                "lead_unit": "months",
                "lead_description": f"Signal lead = {int(best['lead_months'])} month(s) before the rule is applied",
                "oos_sharpe": round(float(best["oos_sharpe"]), 4),
                "oos_ann_return": round(float(best["oos_ann_return"]), 6),  # ratio form (META-UC)
                "oos_ann_vol": round(float(best["oos_ann_vol"]), 6),
                "oos_sortino": round(float(best["oos_sortino"]), 4),
                "oos_calmar": round(float(best["oos_calmar"]), 4),
                "oos_max_drawdown": round(float(best["max_drawdown"]), 6),  # ratio form (META-UC)
                "oos_n_trades": oos_n_trades,
                "oos_period_start": oos_period_start,
                "oos_period_end": oos_period_end,
                "max_drawdown": round(float(best["max_drawdown"]), 6),  # ratio form (META-UC)
                "win_rate": round(float(best["win_rate"]), 4),
                "annual_turnover": round(float(best["annual_turnover"]), 2),
                "cost_assumption_bps": 5,
                "is_n": int(best["is_n"]),
                "oos_n": int(best["oos_n"]),
                "bh_oos_sharpe": round(float(bh.iloc[0]["oos_sharpe"]), 4) if len(bh) > 0 else None,
                "bh_sharpe": round(float(bh.iloc[0]["oos_sharpe"]), 4) if len(bh) > 0 else None,
                "bh_ann_return": round(float(bh.iloc[0]["oos_ann_return"]), 6) if len(bh) > 0 else None,
                "bh_max_drawdown": round(float(bh.iloc[0]["max_drawdown"]), 6) if len(bh) > 0 else None,
                "oos_start": OOS_START.strftime("%Y-%m-%d"),
                "is_end": IS_END.strftime("%Y-%m-%d"),
                "schema_version": "1.1.0",
                "notes": (
                    f"Expected relationship is {EXPECTED_DIRECTION}. "
                    f"Winning threshold uses {threshold_note_contract}. "
                    f"Signal is lagged by {int(best['lead_months'])} months before the rule is applied."
                ),
            }

            # --- ECON-T5 selection provenance (FREE full-grid L0-12 selection; no cap) ---
            # Lead-Grid Frequency Standard (2026-07-14): the winner is the global max valid
            # combo over the full grid. The 2-5-month window is REFERENCE only (Step 5); the
            # full-grid math CONFIRMED it (nothing at L7-12 beats L6).
            _sel_pool = valid_strats
            _ranked = _sel_pool.sort_values("oos_sharpe", ascending=False)
            _runner = _ranked.iloc[1] if len(_ranked) > 1 else None
            _l712 = valid_strats[valid_strats["lead_months"] >= 7]
            _l712_max = round(float(_l712["oos_sharpe"].max()), 4) if len(_l712) else None
            _s6 = _l712[_l712["signal"] == "S6_direction"]
            _s6_max = round(float(_s6["oos_sharpe"].max()), 4) if len(_s6) else None
            winner_summary["schema_version"] = "1.2.0"
            winner_summary["selection"] = {
                "objective": "max_oos_sharpe",
                "objective_formula": "oos_ret.mean()/oos_ret.std()*sqrt(ann), ann=12",
                "grid_scanned": {
                    "leads": list(range(0, 13)),
                    "n_signals": int(_sel_pool["signal"].nunique()),
                    "n_thresholds": int(_sel_pool["threshold"].nunique()),
                    "n_strategies": int(_sel_pool["strategy"].nunique()),
                    "n_valid_combos": int(len(_sel_pool)),
                    "median_valid_objective": round(float(_sel_pool["oos_sharpe"].median()), 4),
                },
                "tie_break_step": 0,
                "raw_winner_row": {
                    "signal": str(best["signal"]),
                    "threshold": str(best["threshold"]),
                    "strategy": str(best["strategy"]),
                    "lead_column": "lead_months",
                    "lead_value": int(best["lead_months"]),
                    "source_tournament_file": f"tournament_results_{DATE_TAG}.csv",
                    "source_row_index": int(best.name),
                    "display_alias": f"signal_code={winner_summary['signal_code']}; strategy={best['strategy']}",
                },
                "runner_up": ({
                    "signal": str(_runner["signal"]), "threshold": str(_runner["threshold"]),
                    "strategy": str(_runner["strategy"]), "lead_value": int(_runner["lead_months"]),
                    "objective_value": round(float(_runner["oos_sharpe"]), 4),
                } if _runner is not None else None),
                "rationale": (
                    f"FREE full-grid selection (Lead-Grid Frequency Standard, 2026-07-14): no "
                    f"economic-window cap — the winner is the global max valid OOS Sharpe over the "
                    f"FULL L0-12 grid ({len(_sel_pool)} valid combos, median "
                    f"{float(_sel_pool['oos_sharpe'].median()):.4f}): {best['signal']}/{best['threshold']}/"
                    f"{best['strategy']}/L{int(best['lead_months'])} = {float(best['oos_sharpe']):.4f}. "
                    f"The economically-motivated 2-5-month cross-correlation window is REFERENCE context "
                    f"the full-grid math CONFIRMED: the best L7-12 combo scores only {_l712_max} (< winner), "
                    f"and S6_direction — the transform with a significant L10 lead-correlation (r=0.113*) — "
                    f"scores at most {_s6_max} across L7-12, so the long-lead direction signal is "
                    f"multiple-testing noise, not a tradable edge. This retires the interim Option-C L0-6 "
                    f"cap; the winner is UNCHANGED (L6 was already the full-grid global max). Low-confidence "
                    f"framing stands: isolated L6 spike on a nearly-flat envelope, backward-Granger caveat, "
                    f"L7-12 = noise. Published winner == full-grid raw max-OOS-Sharpe valid row -> divergence null."
                ),
                "objective_runner_up_divergence": None,
            }

            sr = pd.DataFrame({
                "date": work_for_summary.index.strftime("%Y-%m-%d"),
                "signal_value": signal_for_rule.reindex(work_for_summary.index).values,
                "threshold_value": (
                    threshold_obj.reindex(work_for_summary.index).values
                    if isinstance(threshold_obj, pd.Series)
                    else np.repeat(float(threshold_obj), len(work_for_summary.index))
                ),
                "position": position.reindex(work_for_summary.index).fillna(0.0).values,
                "strategy_return": strategy_return.reindex(work_for_summary.index).fillna(0.0).values,
                "bh_return": work_for_summary["xlv_ret"].values,
            })
            sr_path = os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv")
            sr.to_csv(sr_path, index=False)
            print(f"  Strategy returns -> {sr_path}")

        winner_path = os.path.join(RESULTS_DIR, "winner_summary.json")
        with open(winner_path, "w") as f:
            json.dump(winner_summary, f, indent=2)
        print(f"\n  Winner summary -> {winner_path}")

    # --- Generate winner trade log ---
    if winner_summary and "signal" in winner_summary:
        try:
            work = df_monthly.dropna(subset=["umcsent"])
            oos_mask = work.index >= OOS_START

            position, strategy_return, signal_for_rule, threshold_obj, _, _ = derive_winner_series(
                work,
                {
                    "signal": winner_summary["signal"],
                    "threshold": winner_summary["threshold"],
                    "strategy": winner_summary["strategy"],
                    "lead_months": winner_summary["lead_months"],
                },
            )
            oos_data = work[oos_mask].copy()
            oos_data["signal_value"] = signal_for_rule[oos_mask]
            oos_data["threshold"] = (
                threshold_obj[oos_mask]
                if isinstance(threshold_obj, pd.Series)
                else float(threshold_obj)
            )
            oos_data["position"] = position[oos_mask].fillna(0.0)
            oos_data["strat_ret"] = strategy_return[oos_mask].fillna(0.0)
            oos_data["strategy_return"] = oos_data["strat_ret"]
            oos_data["xlv_return"] = oos_data["xlv_ret"]
            oos_data["cum_return"] = (1 + oos_data["strat_ret"]).cumprod()
            oos_data["cumulative_return"] = oos_data["cum_return"] - 1

            trade_log = oos_data[
                [
                    "signal_value",
                    "threshold",
                    "position",
                    "xlv_return",
                    "strat_ret",
                    "strategy_return",
                    "cum_return",
                    "cumulative_return",
                    "xlv",
                ]
            ].copy()
            trade_log.index.name = "date"
            trade_log_path = os.path.join(RESULTS_DIR, "winner_trade_log.csv")
            trade_log.to_csv(trade_log_path)
            print(f"  Winner trade log -> {trade_log_path}")
        except Exception as e:
            print(f"  Trade log generation failed: {e}")

    # --- Pipeline Summary ---
    pipeline_elapsed = time.time() - pipeline_start

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n  Total wall-clock time: {pipeline_elapsed:.1f}s ({pipeline_elapsed/60:.1f} min)")
    print(f"\n  IS/OOS Split: IS ends {IS_END.date()}, OOS starts {OOS_START.date()}")
    print(f"\n  Stage timings:")
    for stage, elapsed in STAGE_TIMES.items():
        print(f"    {stage:<35s} {elapsed:8.1f}s")

    if len(tournament_df) > 0:
        valid_count = tournament_df["valid"].sum()
        print(f"\n  Tournament:")
        print(f"    Total combinations: {len(tournament_df)}")
        print(f"    Valid strategies:   {valid_count}")

        if winner_summary:
            print(f"    Best OOS Sharpe:   {winner_summary.get('oos_sharpe', 'N/A')}")
            print(f"    Best signal:       {winner_summary.get('signal', 'N/A')}/{winner_summary.get('threshold', 'N/A')}")

    # Timing
    timing = {
        "pair_id": PAIR_ID,
        "indicator": INDICATOR_NAME,
        "target": TARGET_NAME,
        "date": DATE_TAG,
        "pipeline_seconds": round(pipeline_elapsed, 1),
        "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
        "monthly_rows": df_monthly.shape[0],
        "monthly_cols": df_monthly.shape[1],
        "tournament_combos": len(tournament_df),
        "valid_strategies": int(tournament_df["valid"].sum()) if len(tournament_df) > 0 else 0,
    }

    timing_path = os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json")
    with open(timing_path, "w") as f:
        json.dump(timing, f, indent=2)
    print(f"\n  Timing saved -> {timing_path}")

    return df_monthly, df_daily, tournament_df


if __name__ == "__main__":
    main()
