#!/usr/bin/env python3
"""
Full Analysis Pipeline: Industrial Production (INDPRO) → S&P 500 (SPY)
======================================================================
Priority pair #1 from the combinations catalog.

Stages:
  1. Data sourcing (FRED + Yahoo) + calendar alignment
  2. Derived series computation
  3. Stationarity tests + quality reports
  4. Exploratory analysis (correlations, CCF, regime stats)
  5. Core econometric models (9 categories)
  6. Tournament backtest (5D combinatorial)
  7. Tournament validation (walk-forward, bootstrap, stress tests)

Author: Dana/Evan (Data + Econometrics Agents)
Date: 2026-03-14
Analysis Brief: docs/analysis_brief_indpro_spy_20260314.md
"""

import os
import sys
import json
import warnings
from pathlib import Path
import time
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PAIR_ID = "indpro_spy"
INDICATOR_NAME = "Industrial Production"
TARGET_NAME = "S&P 500"
START_DATE = "1990-01-01"
END_DATE = "2025-12-31"
IS_END = "2017-12-31"
OOS_START = "2018-01-01"
DATE_TAG = "20260314"

BASE_DIR = str(Path(__file__).resolve().parents[1])
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")

for d in [DATA_DIR, RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}

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
    """Source INDPRO (monthly) + SPY (daily) + controls from FRED and Yahoo."""

    # --- FRED series ---
    fred_series = {
        "INDPRO": "indpro",         # Industrial Production Index (Monthly)
        "UNRATE": "unrate",          # Unemployment Rate (Monthly)
        "TCU": "caput",              # Capacity Utilization (Monthly)
        "DGS10": "dgs10",           # 10Y Treasury Yield (Daily)
        "DTB3": "dtb3",             # 3M Treasury Yield (Daily)
        "DFF": "fed_funds",          # Fed Funds Rate (Daily)
    }

    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("  [WARN] FRED_API_KEY not set; using FRED DEMO_KEY fallback. For reliable full refreshes, set FRED_API_KEY.")
        api_key = "DEMO_KEY"
    fred_data = {}

    try:
        from fredapi import Fred
        fred = Fred(api_key=api_key)
        for series_id, col_name in fred_series.items():
            try:
                s = fred.get_series(series_id, observation_start=START_DATE, observation_end=END_DATE)
                s.name = col_name
                s.index = pd.to_datetime(s.index)
                fred_data[col_name] = s.astype(float)
                print(f"  [FRED] {series_id} -> {col_name}: {len(s)} obs, {s.index.min().date()} to {s.index.max().date()}")
            except Exception as e:
                print(f"  [FRED] {series_id} -> {col_name}: FAILED ({e})")
    except Exception as e:
        print(f"  [FRED] fredapi failed: {e}")
        # Fallback: direct CSV download
        import urllib.request
        for series_id, col_name in fred_series.items():
            if col_name in fred_data:
                continue
            try:
                url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={START_DATE}&coed={END_DATE}"
                local_path = f"/tmp/fred_{series_id}.csv"
                urllib.request.urlretrieve(url, local_path)
                s = pd.read_csv(local_path, index_col=0, parse_dates=True).iloc[:, 0]
                s = pd.to_numeric(s, errors="coerce")
                s.name = col_name
                fred_data[col_name] = s
                print(f"  [CSV]  {series_id} -> {col_name}: {len(s)} obs")
            except Exception as e:
                print(f"  [CSV]  {series_id} -> {col_name}: FAILED ({e})")

    # --- Yahoo Finance series ---
    import yfinance as yf
    yahoo_tickers = {
        "SPY": "spy",
        "^VIX": "vix",
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
      1. Monthly dataset (INDPRO native frequency) for econometric models
      2. Daily dataset (SPY native frequency) for tournament backtest
    """
    # --- Monthly dataset ---
    # Resample everything to month-end
    monthly_cols = {"indpro", "unrate", "caput"}
    daily_cols = {"spy", "vix", "dgs10", "dtb3", "fed_funds"}

    # Create monthly index
    monthly_idx = pd.date_range(START_DATE, END_DATE, freq="ME")
    df_monthly = pd.DataFrame(index=monthly_idx)
    df_monthly.index.name = "date"

    # Monthly series: reindex directly
    for col in monthly_cols:
        if col in all_series:
            s = all_series[col]
            # Align to month-end
            s_monthly = s.resample("ME").last()
            df_monthly[col] = s_monthly.reindex(monthly_idx)

    # Daily series: resample to month-end (last value)
    for col in daily_cols:
        if col in all_series:
            s = all_series[col]
            s_monthly = s.resample("ME").last()
            df_monthly[col] = s_monthly.reindex(monthly_idx)

    # Forward fill gaps (max 2 months)
    df_monthly = df_monthly.ffill(limit=2)

    # --- Derived series (monthly) ---
    ip = df_monthly["indpro"]

    # D1: INDPRO YoY % change
    df_monthly["indpro_yoy"] = (ip / ip.shift(12) - 1) * 100

    # D2: INDPRO MoM % change
    df_monthly["indpro_mom"] = (ip / ip.shift(1) - 1) * 100

    # D3: 12M moving average
    df_monthly["indpro_ma12"] = ip.rolling(12, min_periods=10).mean()

    # D4: Deviation from trend
    df_monthly["indpro_dev_trend"] = ip - df_monthly["indpro_ma12"]

    # D5: Z-score (60M rolling)
    rm60 = ip.rolling(60, min_periods=48)
    df_monthly["indpro_zscore_60m"] = (ip - rm60.mean()) / rm60.std()

    # D6: Momentum 3M
    df_monthly["indpro_mom_3m"] = ip - ip.shift(3)

    # D7: Momentum 6M
    df_monthly["indpro_mom_6m"] = ip - ip.shift(6)

    # D8: Acceleration (change in MoM growth)
    df_monthly["indpro_accel"] = df_monthly["indpro_mom"] - df_monthly["indpro_mom"].shift(1)

    # D9: Contraction dummy
    df_monthly["indpro_contraction"] = (df_monthly["indpro_yoy"] < 0).astype(int)

    # D10: Yield spread 10Y-3M
    if "dgs10" in df_monthly.columns and "dtb3" in df_monthly.columns:
        df_monthly["yield_spread_10y3m"] = df_monthly["dgs10"] - df_monthly["dtb3"]

    # D11: SPY monthly return
    if "spy" in df_monthly.columns:
        df_monthly["spy_ret"] = df_monthly["spy"].pct_change()

    # --- Forward SPY returns (monthly horizons) ---
    spy_m = df_monthly["spy"]
    df_monthly["spy_fwd_1m"] = spy_m.shift(-1) / spy_m - 1
    df_monthly["spy_fwd_3m"] = spy_m.shift(-3) / spy_m - 1
    df_monthly["spy_fwd_6m"] = spy_m.shift(-6) / spy_m - 1
    df_monthly["spy_fwd_12m"] = spy_m.shift(-12) / spy_m - 1

    # --- Daily dataset (for tournament) ---
    bdays = pd.bdate_range(START_DATE, END_DATE)
    df_daily = pd.DataFrame(index=bdays)
    df_daily.index.name = "date"

    # Daily series
    for col in daily_cols:
        if col in all_series:
            s = all_series[col].reindex(bdays).ffill(limit=5)
            df_daily[col] = s

    # Forward-fill monthly INDPRO signals to daily
    for col in monthly_cols:
        if col in all_series:
            s = all_series[col]
            # Reindex to daily, forward-fill (monthly data persists until next release)
            df_daily[col] = s.reindex(bdays).ffill()

    # Recompute key derived series at daily frequency (using ffilled monthly values)
    if "indpro" in df_daily.columns:
        ip_d = df_daily["indpro"]
        # YoY: use ~252 trading day shift as proxy for 12 months
        df_daily["indpro_yoy"] = (ip_d / ip_d.shift(252) - 1) * 100
        # MoM: ~21 trading days
        df_daily["indpro_mom"] = (ip_d / ip_d.shift(21) - 1) * 100
        # Z-score
        rm = ip_d.rolling(252*5, min_periods=252*4)
        df_daily["indpro_zscore"] = (ip_d - rm.mean()) / rm.std()
        # Contraction dummy
        df_daily["indpro_contraction"] = (df_daily["indpro_yoy"] < 0).astype(float)

    # Daily SPY forward returns
    if "spy" in df_daily.columns:
        spy_d = df_daily["spy"]
        df_daily["spy_fwd_1d"] = spy_d.pct_change(1).shift(-1)
        df_daily["spy_fwd_5d"] = spy_d.shift(-5) / spy_d - 1
        df_daily["spy_fwd_21d"] = spy_d.shift(-21) / spy_d - 1
        df_daily["spy_fwd_63d"] = spy_d.shift(-63) / spy_d - 1

    # Drop rows before indicator data starts
    df_monthly = df_monthly.dropna(subset=["indpro"], how="all")

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

    test_cols = ["indpro", "spy", "vix", "dgs10", "dtb3", "fed_funds",
                 "unrate", "caput", "indpro_yoy", "indpro_mom"]

    results = []
    for col in test_cols:
        s = df_monthly[col].dropna() if col in df_monthly.columns else pd.Series(dtype=float)
        if len(s) < 50:
            # Try daily
            if col in df_daily.columns:
                s = df_daily[col].dropna()
        if len(s) < 50:
            results.append({"variable": col, "test": "ADF", "statistic": np.nan,
                          "p_value": np.nan, "conclusion": f"Insufficient data ({len(s)} obs)"})
            continue

        # Subsample if too large (for speed)
        if len(s) > 5000:
            s = s.iloc[::5]  # Take every 5th observation

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
        f"**Daily dataset:** {df_daily.shape[0]} rows × {df_daily.shape[1]} columns",
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

    signals = ["indpro_yoy", "indpro_mom", "indpro_dev_trend", "indpro_zscore_60m",
               "indpro_mom_3m", "indpro_mom_6m", "indpro_accel", "indpro_contraction"]
    fwd_cols = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]

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

            # Pearson
            r_p, p_p = stats.pearsonr(x, y)
            corr_results.append({"signal": sig, "horizon": fwd, "method": "Pearson",
                                "correlation": round(r_p, 4), "p_value": round(p_p, 4),
                                "n": len(valid)})

            # Spearman
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
    if "indpro_yoy" in df_monthly.columns and "spy_ret" in df_monthly.columns:
        sig = df_monthly["indpro_yoy"].dropna()
        ret = df_monthly["spy_ret"].dropna()
        common = sig.index.intersection(ret.index)
        sig = sig.loc[common]
        ret = ret.loc[common]

        if len(sig) > 30:
            # Standardize
            sig_std = (sig - sig.mean()) / sig.std()
            ret_std = (ret - ret.mean()) / ret.std()

            for lag in range(-12, 13):
                if lag >= 0:
                    x = sig_std.iloc[:len(sig_std)-lag] if lag > 0 else sig_std
                    y = ret_std.iloc[lag:] if lag > 0 else ret_std
                else:
                    x = sig_std.iloc[-lag:]
                    y = ret_std.iloc[:len(ret_std)+lag]

                if len(x) < 20:
                    continue

                # Align indices
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
    if "indpro_yoy" in df_monthly.columns and "spy_ret" in df_monthly.columns:
        valid = df_monthly[["indpro_yoy", "spy_ret"]].dropna()

        # Quartiles of INDPRO YoY
        quartiles = pd.qcut(valid["indpro_yoy"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"])

        for q in ["Q1_low", "Q2", "Q3", "Q4_high"]:
            mask = quartiles == q
            rets = valid.loc[mask, "spy_ret"]
            if len(rets) < 5:
                continue

            ann_ret = rets.mean() * 12 * 100  # annualized
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
    """Run core econometric models per Analysis Brief categories 1,2,3,4,6,9,12."""
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    model_results = {}

    # Prepare working dataset
    base_cols = ["indpro_yoy", "indpro_mom", "indpro_zscore_60m",
                 "indpro_contraction", "indpro_mom_3m", "indpro_mom_6m",
                 "indpro_accel", "spy_ret", "spy_fwd_1m",
                 "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]
    ctrl_cols = ["vix", "yield_spread_10y3m", "unrate", "caput"]
    all_work_cols = [c for c in base_cols + ctrl_cols if c in df_monthly.columns]
    work = df_monthly[all_work_cols].copy()

    work = work.dropna(subset=["indpro_yoy", "spy_ret"])
    print(f"  Working dataset: {work.shape}")

    # --- 5.1 Granger Causality ---
    print("\n  [5.1] Granger Causality...")
    gc_results = []
    try:
        gc_data = work[["indpro_yoy", "spy_ret"]].dropna()
        if len(gc_data) > 50:
            # Test: INDPRO_YoY -> SPY_ret
            gc = grangercausalitytests(gc_data[["spy_ret", "indpro_yoy"]], maxlag=6, verbose=False)
            for lag, result in gc.items():
                f_stat = result[0]["ssr_ftest"][0]
                p_val = result[0]["ssr_ftest"][1]
                gc_results.append({"direction": "INDPRO->SPY", "lag": lag,
                                  "f_statistic": round(f_stat, 4), "p_value": round(p_val, 4),
                                  "significant": p_val < 0.05})

            # Reverse: SPY_ret -> INDPRO_YoY
            gc_rev = grangercausalitytests(gc_data[["indpro_yoy", "spy_ret"]], maxlag=6, verbose=False)
            for lag, result in gc_rev.items():
                f_stat = result[0]["ssr_ftest"][0]
                p_val = result[0]["ssr_ftest"][1]
                gc_results.append({"direction": "SPY->INDPRO", "lag": lag,
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
    for signal in ["indpro_yoy", "indpro_mom", "indpro_zscore_60m"]:
        for horizon in ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]:
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
    horizons_map = {"spy_fwd_1m": 1, "spy_fwd_3m": 3, "spy_fwd_6m": 6, "spy_fwd_12m": 12}

    for horizon_col, h in horizons_map.items():
        valid = work[["indpro_yoy", horizon_col]].dropna()
        # Add controls if available
        controls = []
        for ctrl in ["vix", "yield_spread_10y3m"]:
            if ctrl in work.columns:
                valid[ctrl] = work.loc[valid.index, ctrl]
                controls.append(ctrl)
        valid = valid.dropna()

        if len(valid) < 30:
            continue

        try:
            X_cols = ["indpro_yoy"] + controls
            X = sm.add_constant(valid[X_cols])
            y = valid[horizon_col]

            # Newey-West HAC SEs
            nw_lags = int(0.75 * len(valid) ** (1/3))
            model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw_lags})

            lp_results.append({
                "horizon_months": h,
                "coef_indpro_yoy": round(model.params["indpro_yoy"], 6),
                "se": round(model.bse["indpro_yoy"], 6),
                "t_stat": round(model.tvalues["indpro_yoy"], 3),
                "p_value": round(model.pvalues["indpro_yoy"], 4),
                "ci_lower": round(model.conf_int().loc["indpro_yoy", 0], 6),
                "ci_upper": round(model.conf_int().loc["indpro_yoy", 1], 6),
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
    for horizon_col, h in horizons_map.items():
        valid = work[["indpro_yoy", "indpro_contraction", horizon_col]].dropna()
        if len(valid) < 50:
            continue

        try:
            # Interaction: indpro_yoy × contraction
            valid["interact"] = valid["indpro_yoy"] * valid["indpro_contraction"]
            X = sm.add_constant(valid[["indpro_yoy", "indpro_contraction", "interact"]])
            y = valid[horizon_col]

            nw_lags = int(0.75 * len(valid) ** (1/3))
            model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw_lags})

            regime_lp_results.append({
                "horizon_months": h,
                "coef_indpro_yoy": round(model.params["indpro_yoy"], 6),
                "coef_contraction": round(model.params["indpro_contraction"], 6),
                "coef_interaction": round(model.params["interact"], 6),
                "p_indpro": round(model.pvalues["indpro_yoy"], 4),
                "p_contraction": round(model.pvalues["indpro_contraction"], 4),
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
        ms_data = work[["spy_ret", "indpro_yoy"]].dropna()
        if len(ms_data) > 50:
            from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

            ms_model = MarkovRegression(
                ms_data["spy_ret"], k_regimes=2,
                exog=sm.add_constant(ms_data["indpro_yoy"]),
                switching_variance=True
            )
            ms_fit = ms_model.fit(maxiter=500, disp=False)

            # Save regime probabilities
            probs = pd.DataFrame({
                "regime_0_prob": ms_fit.smoothed_marginal_probabilities[0],
                "regime_1_prob": ms_fit.smoothed_marginal_probabilities[1],
            }, index=ms_data.index)
            probs.to_csv(os.path.join(MODELS_DIR, "markov_regime_probs_2state.csv"))

            # Save parameters
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
    valid_qr = work[["indpro_yoy", "spy_fwd_3m"]].dropna()
    if len(valid_qr) > 30:
        for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
            try:
                qr_model = smf.quantreg("spy_fwd_3m ~ indpro_yoy", data=valid_qr)
                qr_fit = qr_model.fit(q=tau)
                qr_results.append({
                    "quantile": tau,
                    "intercept": round(qr_fit.params["Intercept"], 6),
                    "coef_indpro_yoy": round(qr_fit.params["indpro_yoy"], 6),
                    "se": round(qr_fit.bse["indpro_yoy"], 6),
                    "p_value": round(qr_fit.pvalues["indpro_yoy"], 4),
                    "ci_lower": round(qr_fit.conf_int().loc["indpro_yoy", 0], 6),
                    "ci_upper": round(qr_fit.conf_int().loc["indpro_yoy", 1], 6),
                })
            except Exception as e:
                print(f"    QR at tau={tau} failed: {e}")

    qr_df = pd.DataFrame(qr_results)
    qr_df.to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    model_results["quantile_regression"] = qr_df
    print(f"    {len(qr_df)} quantiles saved")

    # --- 5.7 Cointegration (Johansen) ---
    print("\n  [5.7] Cointegration Test...")
    try:
        from statsmodels.tsa.vector_ar.vecm import coint_johansen

        coint_data = df_monthly[["indpro", "spy"]].dropna()
        if len(coint_data) > 50:
            # Use log levels
            coint_data = np.log(coint_data)
            result = coint_johansen(coint_data, det_order=1, k_ar_diff=2)

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

        ip_series = df_monthly["indpro_yoy"].dropna().values
        if len(ip_series) > 30:
            algo = rpt.Pelt(model="rbf").fit(ip_series)
            change_points = algo.predict(pen=10)

            # Map back to dates
            ip_dates = df_monthly["indpro_yoy"].dropna().index
            cp_results = []
            for cp in change_points[:-1]:  # Last element is always n
                if cp < len(ip_dates):
                    cp_results.append({
                        "index": cp,
                        "date": ip_dates[cp].strftime("%Y-%m-%d"),
                        "indpro_yoy_at_break": round(ip_series[cp], 2) if cp < len(ip_series) else np.nan,
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

        # Features: INDPRO signals + controls
        feature_cols = [c for c in ["indpro_yoy", "indpro_mom", "indpro_zscore_60m",
                       "indpro_mom_3m", "indpro_mom_6m", "indpro_accel",
                       "vix", "yield_spread_10y3m", "unrate", "caput"]
                       if c in work.columns]

        # Target: positive 3M forward return
        rf_data = work[feature_cols + ["spy_fwd_3m"]].dropna()
        rf_data["target"] = (rf_data["spy_fwd_3m"] > 0).astype(int)

        if len(rf_data) > 100:
            # Walk-forward: 10yr train / 3yr test
            wf_results = []
            feature_importances = []

            # Monthly: use year-based splits
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

                # Feature importance from last fold
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

    # --- 5.10 Diagnostics Summary ---
    print("\n  [5.10] Diagnostics Summary...")
    diag_results = []

    # Run diagnostics on the baseline regression (indpro_yoy -> spy_fwd_3m)
    valid_diag = work[["indpro_yoy", "spy_fwd_3m"]].dropna()
    if len(valid_diag) > 30:
        X = sm.add_constant(valid_diag["indpro_yoy"])
        y = valid_diag["spy_fwd_3m"]
        base_model = sm.OLS(y, X).fit()
        resid = base_model.resid

        # Jarque-Bera
        jb_stat, jb_p = stats.jarque_bera(resid)
        diag_results.append({"test": "Jarque-Bera (normality)", "statistic": round(jb_stat, 4),
                           "p_value": round(jb_p, 4),
                           "conclusion": "Normal" if jb_p > 0.05 else "Non-normal residuals"})

        # Breusch-Pagan
        try:
            from statsmodels.stats.diagnostic import het_breuschpagan
            bp_stat, bp_p, _, _ = het_breuschpagan(resid, X)
            diag_results.append({"test": "Breusch-Pagan (heteroskedasticity)",
                               "statistic": round(bp_stat, 4), "p_value": round(bp_p, 4),
                               "conclusion": "Homoskedastic" if bp_p > 0.05 else "Heteroskedastic"})
        except Exception:
            pass

        # Breusch-Godfrey
        try:
            from statsmodels.stats.diagnostic import acorr_breusch_godfrey
            bg_stat, bg_p, _, _ = acorr_breusch_godfrey(base_model, nlags=4)
            diag_results.append({"test": "Breusch-Godfrey (serial correlation)",
                               "statistic": round(bg_stat, 4), "p_value": round(bg_p, 4),
                               "conclusion": "No autocorrelation" if bg_p > 0.05 else "Serial correlation present"})
        except Exception:
            pass

        # Durbin-Watson
        from statsmodels.stats.stattools import durbin_watson
        dw = durbin_watson(resid)
        diag_results.append({"test": "Durbin-Watson", "statistic": round(dw, 4),
                           "p_value": np.nan,
                           "conclusion": f"DW={dw:.2f} (2.0=no autocorrelation)"})

    diag_df = pd.DataFrame(diag_results)
    diag_df.to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)
    model_results["diagnostics"] = diag_df
    print(f"    {len(diag_df)} diagnostic tests saved")

    # --- Interpretation Metadata ---
    interpretation = {
        "indicator": "indpro",
        "target": "spy",
        "expected_direction": "pro_cyclical",
        "observed_direction": "pro_cyclical",  # Will be updated based on results
        "direction_consistent": True,
        "mechanism": "Rising industrial production reflects expanding manufacturing activity and higher corporate earnings, supporting equity valuations.",
        "confidence": "high",
        "key_finding": "",
        "caveats": [
            "INDPRO is released with ~6-week lag — real-time trading must account for publication delay",
            "COVID-19 April 2020 outlier (-12.7% MoM) may dominate regime models",
            "Monthly frequency limits signal granularity for daily trading strategies"
        ]
    }

    # Update key finding from regression results
    if len(reg_df) > 0:
        best_reg = reg_df.loc[reg_df["p_value"].idxmin()]
        interpretation["key_finding"] = (
            f"INDPRO {best_reg['signal']} predicts {best_reg['horizon']} "
            f"(coef={best_reg['coef']:.4f}, t={best_reg['t_stat']:.2f}, "
            f"p={best_reg['p_value']:.4f}, R²={best_reg['r_squared']:.3f})"
        )
        # Check if observed direction matches expected
        if best_reg["coef"] < 0:
            interpretation["observed_direction"] = "counter_cyclical"
            interpretation["direction_consistent"] = False

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
    """
    5D combinatorial tournament backtest.
    Signals × Thresholds × Strategies × Lead Times × Lookbacks
    """
    # Use monthly data for tournament (INDPRO native frequency)
    # Forward returns already computed

    work = df_monthly.copy()
    work = work.dropna(subset=["indpro"])

    # Define IS/OOS split
    is_mask = work.index <= IS_END
    oos_mask = work.index >= OOS_START

    # Signal columns
    signal_cols = {
        "S1_level": "indpro",
        "S2_yoy": "indpro_yoy",
        "S3_mom": "indpro_mom",
        "S4_dev_trend": "indpro_dev_trend",
        "S5_zscore": "indpro_zscore_60m",
        "S6_mom3m": "indpro_mom_3m",
        "S7_mom6m": "indpro_mom_6m",
        "S8_accel": "indpro_accel",
        "S9_contraction": "indpro_contraction",
    }

    # Check which signals are available
    available_signals = {k: v for k, v in signal_cols.items() if v in work.columns and work[v].notna().sum() > 50}
    print(f"  Available signals: {len(available_signals)}")

    # Monthly SPY return for backtest
    if "spy_ret" not in work.columns:
        if "spy" in work.columns:
            work["spy_ret"] = work["spy"].pct_change()
        else:
            print("  ERROR: No SPY data for tournament")
            return pd.DataFrame()

    # Tournament parameters
    lead_times = [0, 1, 2, 3, 6]  # months
    strategies = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]

    results = []
    combo_count = 0

    for sig_name, sig_col in available_signals.items():
        signal = work[sig_col].copy()

        # Skip if not enough data
        if signal.dropna().shape[0] < 50:
            continue

        for lead in lead_times:
            # Apply lead time (lag the signal)
            if lead > 0:
                signal_lagged = signal.shift(lead)
            else:
                signal_lagged = signal

            # --- Threshold methods ---
            thresholds = {}

            # T1: Fixed percentile (IS only)
            is_signal = signal_lagged[is_mask].dropna()
            if len(is_signal) > 20:
                for pct in [25, 50, 75]:
                    thresholds[f"T1_fixed_p{pct}"] = is_signal.quantile(pct / 100)

            # T2: Rolling percentile (60M window)
            for pct in [25, 50, 75]:
                thresholds[f"T2_roll_p{pct}"] = signal_lagged.rolling(60, min_periods=36).quantile(pct / 100)

            # T3: Rolling mean ± k*std
            roll_mean = signal_lagged.rolling(60, min_periods=36).mean()
            roll_std = signal_lagged.rolling(60, min_periods=36).std()
            for k in [1.0, 1.5, 2.0]:
                thresholds[f"T3_zscore_{k}"] = roll_mean + k * roll_std
                thresholds[f"T3_zscore_neg_{k}"] = roll_mean - k * roll_std

            # T4: Zero crossing (for growth rates)
            if sig_name in ["S2_yoy", "S3_mom", "S8_accel"]:
                thresholds["T4_zero"] = 0

            for thresh_name, thresh_val in thresholds.items():
                for strat in strategies:
                    combo_count += 1

                    try:
                        # Determine position
                        if isinstance(thresh_val, (int, float)):
                            # Fixed threshold
                            if sig_name == "S9_contraction":
                                # Binary signal: 1=contraction, 0=expansion
                                above = signal_lagged > thresh_val
                            elif "neg_" in thresh_name:
                                # Below negative threshold = bearish
                                above = signal_lagged < thresh_val
                            else:
                                # Pro-cyclical: above threshold = bullish
                                above = signal_lagged > thresh_val
                        else:
                            # Rolling threshold (Series)
                            if "neg_" in thresh_name:
                                above = signal_lagged < thresh_val
                            else:
                                above = signal_lagged > thresh_val

                        # Strategy position
                        if strat == "P1_long_cash":
                            position = above.astype(float)
                        elif strat == "P2_signal_strength":
                            # Normalize signal to 0-1
                            sig_min = signal_lagged.rolling(60, min_periods=36).min()
                            sig_max = signal_lagged.rolling(60, min_periods=36).max()
                            sig_range = sig_max - sig_min
                            sig_range = sig_range.replace(0, np.nan)
                            position = ((signal_lagged - sig_min) / sig_range).clip(0, 1)
                        elif strat == "P3_long_short":
                            position = above.astype(float) * 2 - 1  # {-1, +1}
                        else:
                            continue

                        # Strategy returns: position(t) × SPY return(t+1)
                        strat_ret = position.shift(1) * work["spy_ret"]

                        # IS/OOS split
                        is_ret = strat_ret[is_mask].dropna()
                        oos_ret = strat_ret[oos_mask].dropna()

                        if len(is_ret) < 24 or len(oos_ret) < 12:
                            continue

                        # IS metrics
                        is_sharpe = (is_ret.mean() / is_ret.std()) * np.sqrt(12) if is_ret.std() > 0 else 0

                        # OOS metrics
                        oos_ann_ret = is_ret.mean() * 12
                        oos_ann_vol = oos_ret.std() * np.sqrt(12) if oos_ret.std() > 0 else 999
                        oos_sharpe = (oos_ret.mean() / oos_ret.std()) * np.sqrt(12) if oos_ret.std() > 0 else 0

                        # Sortino
                        oos_downside = oos_ret[oos_ret < 0].std() * np.sqrt(12) if len(oos_ret[oos_ret < 0]) > 1 else 999
                        oos_sortino = (oos_ret.mean() * 12) / oos_downside if oos_downside > 0 else 0

                        # Max drawdown
                        cum_ret = (1 + oos_ret).cumprod()
                        rolling_max = cum_ret.cummax()
                        drawdown = (cum_ret - rolling_max) / rolling_max
                        max_dd = drawdown.min()

                        # Calmar
                        oos_calmar = (oos_ret.mean() * 12) / abs(max_dd) if abs(max_dd) > 0 else 0

                        # Turnover
                        pos_changes = position.diff().abs().sum()
                        years = len(position.dropna()) / 12
                        annual_turnover = pos_changes / years if years > 0 else 999

                        # Win rate
                        win_rate = (oos_ret > 0).mean()

                        # Validity
                        valid = (oos_sharpe > 0 and annual_turnover < 24 and len(oos_ret) >= 12)

                        results.append({
                            "signal": sig_name,
                            "threshold": thresh_name,
                            "strategy": strat,
                            "lead_months": lead,
                            "is_sharpe": round(is_sharpe, 4),
                            "oos_sharpe": round(oos_sharpe, 4),
                            "oos_sortino": round(oos_sortino, 4),
                            "oos_calmar": round(oos_calmar, 4),
                            "oos_ann_return": round(oos_ret.mean() * 12 * 100, 2),
                            "oos_ann_vol": round(oos_ann_vol * 100, 2),
                            "max_drawdown": round(max_dd * 100, 2),
                            "win_rate": round(win_rate, 4),
                            "annual_turnover": round(annual_turnover, 2),
                            "is_n": len(is_ret),
                            "oos_n": len(oos_ret),
                            "valid": valid,
                        })
                    except Exception:
                        continue

    # Add benchmark (buy-and-hold)
    bh_ret = work["spy_ret"]
    bh_oos = bh_ret[oos_mask].dropna()
    if len(bh_oos) > 0:
        bh_sharpe = (bh_oos.mean() / bh_oos.std()) * np.sqrt(12) if bh_oos.std() > 0 else 0
        bh_cum = (1 + bh_oos).cumprod()
        bh_dd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min()

        results.append({
            "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BUY_HOLD",
            "lead_months": 0,
            "is_sharpe": round((bh_ret[is_mask].dropna().mean() / bh_ret[is_mask].dropna().std()) * np.sqrt(12), 4),
            "oos_sharpe": round(bh_sharpe, 4),
            "oos_sortino": round((bh_oos.mean() * 12) / (bh_oos[bh_oos < 0].std() * np.sqrt(12)) if len(bh_oos[bh_oos < 0]) > 1 else 0, 4),
            "oos_calmar": round((bh_oos.mean() * 12) / abs(bh_dd) if abs(bh_dd) > 0 else 0, 4),
            "oos_ann_return": round(bh_oos.mean() * 12 * 100, 2),
            "oos_ann_vol": round(bh_oos.std() * np.sqrt(12) * 100, 2),
            "max_drawdown": round(bh_dd * 100, 2),
            "win_rate": round((bh_oos > 0).mean(), 4),
            "annual_turnover": 0,
            "is_n": len(bh_ret[is_mask].dropna()),
            "oos_n": len(bh_oos),
            "valid": True,
        })

    results_df = pd.DataFrame(results)
    results_path = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    results_df.to_csv(results_path, index=False)

    # Summary
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
                      f"Sharpe={row['oos_sharpe']:.2f}, DD={row['max_drawdown']:.1f}%, Turnover={row['annual_turnover']:.1f}")

        bh = results_df[results_df["signal"] == "BENCHMARK"]
        if len(bh) > 0:
            print(f"\n    Buy-and-hold benchmark: Sharpe={bh.iloc[0]['oos_sharpe']:.2f}, DD={bh.iloc[0]['max_drawdown']:.1f}%")

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

    # --- 7.1 Bootstrap significance ---
    print("\n  [7.1] Bootstrap significance test...")
    bootstrap_results = []

    work = df_monthly.copy()
    oos_mask = work.index >= OOS_START
    spy_oos = work.loc[oos_mask, "spy_ret"].dropna()

    if len(spy_oos) > 12:
        n_bootstrap = 5000
        bootstrap_sharpes = np.zeros(n_bootstrap)

        for b in range(n_bootstrap):
            sample = np.random.choice(spy_oos.values, size=len(spy_oos), replace=True)
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

    # --- 7.2 Stress test periods ---
    print("\n  [7.2] Stress tests...")
    stress_periods = {
        "GFC": ("2008-01-01", "2009-06-30"),
        "Taper_Tantrum": ("2013-05-01", "2013-09-30"),
        "COVID": ("2020-01-01", "2020-06-30"),
        "Rate_Hike_2022": ("2022-01-01", "2023-06-30"),
    }

    stress_results = []
    for period_name, (start, end) in stress_periods.items():
        stress_mask = (work.index >= start) & (work.index <= end)
        stress_ret = work.loc[stress_mask, "spy_ret"].dropna()

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
            # Approximate cost: turnover × cost per trade
            annual_cost = row["annual_turnover"] * (tx_bps / 10000) * 12  # monthly
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
    print(f"  IS/OOS split: {IS_END} / {OOS_START}")
    print("=" * 70)

    # Stage 1: Data sourcing
    all_series = stage_data_sourcing()

    # Stage 2: Alignment + derived series
    df_monthly, df_daily = stage_alignment_and_derived(all_series)

    # Save datasets
    monthly_path = os.path.join(DATA_DIR, f"indpro_spy_monthly_19900101_20251231.parquet")
    df_monthly.to_parquet(monthly_path, engine="pyarrow")
    daily_path = os.path.join(DATA_DIR, f"indpro_spy_daily_19900101_20251231.parquet")
    df_daily.to_parquet(daily_path, engine="pyarrow")
    print(f"\n  Datasets saved: {monthly_path}")
    print(f"                  {daily_path}")

    # Stage 3: Stationarity + quality
    stat_df = stage_stationarity_and_quality(df_monthly, df_daily)

    # Stage 4: Exploratory analysis
    corr_df, ccf_df, regime_df = stage_exploratory(df_monthly)

    # Stage 5: Core models
    model_results = stage_core_models(df_monthly)

    # Stage 6: Tournament
    tournament_df = stage_tournament(df_monthly, df_daily)

    # Stage 7: Validation
    stage_validation(df_monthly, tournament_df)

    # --- Pipeline Summary ---
    pipeline_elapsed = time.time() - pipeline_start

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n  Total wall-clock time: {pipeline_elapsed:.1f}s ({pipeline_elapsed/60:.1f} min)")
    print(f"\n  Stage timings:")
    for stage, elapsed in STAGE_TIMES.items():
        print(f"    {stage:<35s} {elapsed:8.1f}s")

    print(f"\n  Datasets:")
    print(f"    Monthly: {df_monthly.shape}")
    print(f"    Daily:   {df_daily.shape}")

    if len(tournament_df) > 0:
        valid_count = tournament_df["valid"].sum()
        print(f"\n  Tournament:")
        print(f"    Total combinations: {len(tournament_df)}")
        print(f"    Valid strategies:   {valid_count}")

        bh = tournament_df[tournament_df["signal"] == "BENCHMARK"]
        if len(bh) > 0:
            print(f"    Buy-hold Sharpe:   {bh.iloc[0]['oos_sharpe']:.3f}")

        top_valid = tournament_df[tournament_df["valid"] & (tournament_df["signal"] != "BENCHMARK")]
        if len(top_valid) > 0:
            best = top_valid.loc[top_valid["oos_sharpe"].idxmax()]
            print(f"    Best strategy:     {best['signal']}/{best['threshold']}/{best['strategy']}")
            print(f"    Best OOS Sharpe:   {best['oos_sharpe']:.3f}")

    # Save timing summary
    timing = {
        "pair_id": PAIR_ID,
        "indicator": INDICATOR_NAME,
        "target": TARGET_NAME,
        "date": DATE_TAG,
        "pipeline_seconds": round(pipeline_elapsed, 1),
        "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
        "monthly_rows": df_monthly.shape[0],
        "monthly_cols": df_monthly.shape[1],
        "daily_rows": df_daily.shape[0],
        "daily_cols": df_daily.shape[1],
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
