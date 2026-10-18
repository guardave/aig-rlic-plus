#!/usr/bin/env python3
"""Pair pipeline: University of Michigan Consumer Sentiment (UMCSENT) x XLV (Phase B harness).

The tournament runs on scripts/harness (spec: scripts/pair_spec_umcsent_xlv.py) on two tracks:
  * MAIN, "As known at the time": real-time UMCSENT vintages (ALFRED); each rebalance uses the vintage visible
    when its return window opens, and signals and rolling thresholds are computed inside that vintage.
  * COMPARISON, "As revised today (hindsight)": today's revised values with point-in-time release timing.
Each track selects its own winner on in-sample data by the D9 lead-plateau rule over the registry grid L1..L13
(position.shift(1): effective lag >= 2 months); null tournament K=100, paired block bootstrap vs buy-and-hold XLV,
leak tests. The published 20261008 pipeline (max OOS Sharpe selection) is replayed by the harness (LEGACY_SPEC).

This file keeps the pair's evidence stages (stationarity, exploratory, core models, stress tests), computed on the
revised panel and descriptive only, plus metadata and the narrative-provenance record.
"""

from __future__ import annotations

import json
import os
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import pair_spec_umcsent_xlv as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series  # noqa: E402
from harness.data import load_pinned  # noqa: E402
from harness.evidence import write_evidence_facts  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "umcsent_xlv"
INDICATOR_NAME = "University of Michigan Consumer Sentiment"
TARGET_NAME = "Health Care Select Sector (XLV)"
DATE_TAG = "20261017"  # Phase B B1: harness, two tracks, D9 plateau, registry grid L1..L13, null K=100, bootstrap
TARGET_SYMBOL = "XLV"
COST_BPS = 5
EXPECTED_DIRECTION = "procyclical"

DATA_DIR = str(REPO / "data")
RES = REPO / "results" / PAIR_ID
RESULTS_DIR = str(RES)
EXPLORE_DIR = str(RES / f"exploratory_{DATE_TAG}")
MODELS_DIR = str(RES / f"core_models_{DATE_TAG}")
VALID_DIR = str(RES / f"tournament_validation_{DATE_TAG}")
NOW_ISO = datetime.now(timezone.utc).isoformat()
SIGNALS = spec_mod.SIGNALS
OOS_START = pd.Timestamp(spec_mod.SPEC.oos_start)

STAGE_TIMES: dict[str, float] = {}


def log_stage(name):
    """Decorator to time stages."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            t0 = time.time()
            print(f"\n{'=' * 70}\n  STAGE: {name}\n{'=' * 70}")
            result = func(*args, **kwargs)
            STAGE_TIMES[name] = time.time() - t0
            print(f"\n  [{name}] completed in {STAGE_TIMES[name]:.1f}s")
            return result
        return wrapper
    return decorator


def sharpe(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.mean() / r.std() * np.sqrt(12)) if len(r) > 1 and r.std() > 0 else 0.0



def _hac_corr_p(x: pd.Series, y: pd.Series, h: int) -> float:
    """p-value of a correlation robust to overlapping h-month returns: slope of standardized y on standardized x
    with HAC (Newey-West) errors, maxlags >= h-1."""
    import statsmodels.api as sm
    zx, zy = (x - x.mean()) / x.std(), (y - y.mean()) / y.std()
    lags = max(int(0.75 * len(x) ** (1 / 3)), h - 1)
    fit = sm.OLS(zy.to_numpy(), sm.add_constant(zx.to_numpy())).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return float(fit.pvalues[1])


def _qr_block_bootstrap(data: pd.DataFrame, tau: float, block: int = 6, draws: int = 999, seed: int = 42):
    """Moving-block bootstrap of the quantile-regression slope (overlapping forward returns): standard error,
    95% percentile interval and a two-sided p-value of slope = 0."""
    import statsmodels.formula.api as smf
    rng = np.random.default_rng(seed)
    n = len(data)
    nb = int(np.ceil(n / block))
    out = []
    for _ in range(draws):
        starts = rng.integers(0, n - block + 1, size=nb)
        idx = np.concatenate([np.arange(s0, s0 + block) for s0 in starts])[:n]
        try:
            out.append(float(smf.quantreg("xlv_fwd_3m ~ umcsent_yoy", data=data.iloc[idx]).fit(q=tau)
                             .params["umcsent_yoy"]))
        except Exception:
            continue
    b = np.array(out)
    p = min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
    return float(b.std(ddof=1)), float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975)), float(p), len(b)


@log_stage("1_2_panel")
def build_panel() -> pd.DataFrame:
    """Revised UMCSENT (latest pinned ALFRED vintage) and pinned XLV month-end closes on the full monthly grid,
    plus the published run's regression controls (VIX, DGS10, UNRATE month-end values through 2025-12, pinned
    in the legacy panel) and SPY for reference."""
    idx = spec_mod.rebalance_index()
    df = spec_mod.revised_levels().reindex(idx)
    df.index.name = "date"
    feats = spec_mod.features(spec_mod.revised_levels())
    for col in SIGNALS.values():
        if col != "umcsent":
            df[col] = feats[col].reindex(idx)
    df["xlv"] = spec_mod.target_prices().reindex(idx)
    df["xlv_ret"] = df["xlv"].pct_change()
    x = df["xlv"]
    for h in (1, 3, 6, 12):
        df[f"xlv_fwd_{h}m"] = x.shift(-h) / x - 1
    df["xlv_vol_12m"] = df["xlv_ret"].rolling(12, min_periods=10).std() * np.sqrt(12)
    ctrl = load_pinned("umcsent_xlv_monthly_legacy_20261008.csv")[["spy", "vix", "dgs10", "unrate"]]
    for c in ctrl.columns:
        df[c] = ctrl[c].reindex(idx)
    df["spy_ret"] = df["spy"].pct_change()
    df.to_parquet(Path(DATA_DIR) / "umcsent_xlv_monthly_latest.parquet")
    pd.DataFrame([
        {"Column Name": "umcsent", "Display Name": "University of Michigan Consumer Sentiment",
         "Description": "Index of consumer sentiment (1966:Q1 = 100)", "Source": "FRED / ALFRED (pinned vintages)",
         "Series ID": "UMCSENT", "Unit": "Index", "Transformation": "Monthly level", "Seasonal Adj.": "Not seasonally adjusted",
         "Direction Convention": "Higher = more optimistic households",
         "Effective Start": str(df["umcsent"].first_valid_index().date()),
         "Known Quirks": "Preliminary mid-month and final reading at month end; the final reading revises the preliminary one",
         "Display Note": "A survey of household confidence, published within the survey month.",
         "Refresh Freq.": "Monthly", "Refresh Source": "data/release_calendar/vintages/UMCSENT.csv.gz"},
        {"Column Name": "xlv", "Display Name": "XLV adjusted close", "Description": "Health Care Select Sector SPDR Fund adjusted close",
         "Source": "Yahoo Finance (pinned)", "Series ID": "XLV", "Unit": "USD", "Transformation": "Month-end adjusted close",
         "Seasonal Adj.": "N/A", "Direction Convention": "Higher = higher health-care equity price",
         "Effective Start": str(df["xlv"].first_valid_index().date()), "Known Quirks": "ETF history begins in December 1998",
         "Display Note": "Used as the target and the buy-and-hold benchmark.", "Refresh Freq.": "Daily",
         "Refresh Source": "data/phaseB_inputs/xlv_month_end_20261017.csv"},
    ]).to_csv(Path(DATA_DIR) / f"data_dictionary_{PAIR_ID}_{DATE_TAG}.csv", index=False)
    print(f"  Panel rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


@log_stage("3_stationarity_and_quality")
def stage_stationarity_and_quality(df_monthly):
    """Run ADF/KPSS tests and generate quality reports."""
    from arch.unitroot import ADF, KPSS

    test_cols = ["umcsent", "xlv", "spy", "vix", "dgs10",
                 "unrate", "umcsent_yoy", "umcsent_mom", "umcsent_zscore"]

    results = []
    for col in test_cols:
        s = df_monthly[col].dropna() if col in df_monthly.columns else pd.Series(dtype=float)
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

            h = int(fwd.split("_")[-1].rstrip("m"))       # overlapping h-month forward returns
            r_p, p_p = stats.pearsonr(x, y)
            corr_results.append({"signal": sig, "horizon": fwd, "method": "Pearson",
                                 "correlation": round(r_p, 4), "p_value_iid": round(p_p, 4),
                                 "p_value": round(_hac_corr_p(x, y, h), 4), "n": len(valid)})

            r_s, p_s = stats.spearmanr(x, y)
            corr_results.append({"signal": sig, "horizon": fwd, "method": "Spearman",
                                 "correlation": round(r_s, 4), "p_value_iid": round(p_s, 4),
                                 "p_value": round(_hac_corr_p(x.rank(), y.rank(), h), 4), "n": len(valid)})

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
                h = int(horizon.split("_")[-1].rstrip("m"))     # overlapping h-month returns: HAC, maxlags >= h-1
                lags = max(int(0.75 * len(valid) ** (1 / 3)), h - 1)
                model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
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

            nw_lags = max(int(0.75 * len(valid) ** (1 / 3)), h - 1)  # overlapping h-month returns
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

                nw_lags = max(int(0.75 * len(valid) ** (1 / 3)), h - 1)  # overlapping h-month returns
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
                # overlapping 3-month returns: inference from a moving-block bootstrap (block 6, 999 draws);
                # the default (iid) QuantReg p-value is kept as p_value_iid for reference
                se_b, lo_b, hi_b, p_b, nb = _qr_block_bootstrap(valid_qr, tau)
                qr_results.append({
                    "quantile": tau,
                    "intercept": round(qr_fit.params["Intercept"], 6),
                    "coef_umcsent_yoy": round(qr_fit.params["umcsent_yoy"], 6),
                    "se": round(se_b, 6),
                    "p_value": round(p_b, 4),
                    "ci_lower": round(lo_b, 6),
                    "ci_upper": round(hi_b, 6),
                    "p_value_iid": round(qr_fit.pvalues["umcsent_yoy"], 4),
                    "inference": f"moving-block bootstrap, block 6, {nb} draws, seed 42",
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

    return model_results



# ===================================================================
# ROLLING STABILITY (descriptive, revised panel)
# ===================================================================

@log_stage("5b_rolling_stability")
def stage_rolling_stability(df: pd.DataFrame) -> None:
    """24-month rolling correlation and rolling Granger F of the year-over-year change in UMCSENT and the XLV
    monthly return, and a Quandt-Andrews sup-F test (15% trimming) for a break in xlv_ret_t = a + b *
    umcsent_yoy_{t-1}, with a residual-bootstrap p-value under the no-break null (499 draws, seed 42).
    Replaces the fleet retro-apply files of the published run (legacy panel, old winner's lead)."""
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import grangercausalitytests
    d = df[["umcsent_yoy", "xlv_ret"]].dropna()
    rc = d["umcsent_yoy"].rolling(24, min_periods=12).corr(d["xlv_ret"]).dropna()
    pd.DataFrame({"date": rc.index.strftime("%Y-%m-%d"), "rolling_corr_24m": rc.values}).to_csv(
        RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    rows = []
    for i in range(24, len(d) + 1):
        sub = d.iloc[i - 24:i]
        try:
            g = grangercausalitytests(sub[["xlv_ret", "umcsent_yoy"]], maxlag=3, verbose=False)
            f = [g[k][0]["ssr_ftest"][0] for k in (1, 2, 3)]
            j = int(np.argmax(f))
            rows.append({"date": sub.index[-1].strftime("%Y-%m-%d"), "granger_f_24m": f[j],
                         "p_value_24m": g[j + 1][0]["ssr_ftest"][1], "best_lag": j + 1})
        except Exception:
            continue
    pd.DataFrame(rows).to_csv(RES / f"rolling_granger_{PAIR_ID}.csv", index=False)

    z = pd.concat([d["xlv_ret"].rename("y"), d["umcsent_yoy"].shift(1).rename("x")], axis=1).dropna()
    y, X = z["y"].to_numpy(), sm.add_constant(z["x"].to_numpy())
    n, k = len(y), X.shape[1]
    lo, hi = int(0.15 * n), int(0.85 * n)

    def sup_f(yv):
        ssr0 = float(((yv - X @ np.linalg.lstsq(X, yv, rcond=None)[0]) ** 2).sum())
        best, at = -np.inf, lo
        for t in range(lo, hi):
            s = 0.0
            for a, b in ((0, t), (t, n)):
                beta = np.linalg.lstsq(X[a:b], yv[a:b], rcond=None)[0]
                s += float(((yv[a:b] - X[a:b] @ beta) ** 2).sum())
            fs = ((ssr0 - s) / k) / (s / (n - 2 * k))
            if fs > best:
                best, at = fs, t
        return best, at

    f_obs, t_obs = sup_f(y)
    beta0 = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta0
    rng = np.random.default_rng(42)
    draws = [sup_f(X @ beta0 + rng.choice(resid, size=n, replace=True))[0] for _ in range(499)]
    p = float((1 + sum(f >= f_obs for f in draws)) / (1 + len(draws)))
    out = {"pair_id": PAIR_ID, "test": "quandt_andrews_sup_f", "model": "xlv_ret_t ~ umcsent_yoy_{t-1}",
           "trim_pct": 0.15, "n_obs": int(n), "sup_f": round(float(f_obs), 4),
           "breakpoint_date": z.index[t_obs].strftime("%Y-%m-%d"), "p_value": round(p, 4),
           "p_value_method": "residual bootstrap under the no-break null, 499 draws, seed 42",
           "sample": [z.index[0].strftime("%Y-%m-%d"), z.index[-1].strftime("%Y-%m-%d")]}
    (RES / f"structural_break_{PAIR_ID}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"  sup-F {f_obs:.2f} at {out['breakpoint_date']}, bootstrap p {p:.3f}")


# ===================================================================
# TOURNAMENT (harness)
# ===================================================================

@log_stage("6_tournament_harness")
def run_tournament() -> tuple[pd.DataFrame, dict, dict]:
    out = run_pair(PAIR_ID, DATE_TAG, K=100, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "lookback": "LB60 where rolling thresholds apply",
        "strategy_description": "Position in XLV set by the lagged consumer-sentiment signal relative to its "
                                "threshold (long/cash, signal-strength sizing or long/short, per the rule).",
        "notes": "UMCSENT is a monthly household survey; read the rule as sentiment-regime context for a defensive "
                 "sector, not a forecast. Headline = as known at the time (real-time vintages); still a "
                 "search-selected rule."})
    winner = json.loads((RES / "winner_summary.json").read_text())
    tourn = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["main"]
    if res.selection is not None:
        ws = winner_series(res, res.selection["winner"])
        reason = (f"{winner['signal_code']} signal-strength resize (position in its trailing 60-month range)"
                  if str(winner["strategy_family"]).startswith("P2") else
                  f"{winner['signal_code']} {winner['direction']} rule crossed {winner['threshold_code']}")
        log = trade_log(ws, TARGET_SYMBOL, COST_BPS, reason)
        log.to_csv(RES / "winner_trade_log.csv", index=False)
        log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, winner, out


# ===================================================================
# VALIDATION (winner-specific, from the harness strategy returns)
# ===================================================================

STRESS_PERIODS = [
    ("Dot-Com Crash", "2000-03-01", "2002-10-31"),
    ("GFC", "2007-12-01", "2009-06-30"),
    ("COVID", "2020-02-01", "2020-12-31"),
    ("2022 Rates Shock", "2022-01-01", "2022-12-31"),
]


@log_stage("7_validation")
def stage_validation(winner: dict) -> None:
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    rows = []
    for name, start, end in STRESS_PERIODS + [("Full OOS", winner["oos_period_start"], winner["oos_period_end"])]:
        seg = strat.loc[start:end]
        r, b = seg["strategy_return"], seg["benchmark_return"]
        eq = (1 + r).cumprod()
        cnt = seg["sample"].value_counts()
        n_pre, n_is, n_oos = int(cnt.get("pre_IS", 0)), int(cnt.get("IS", 0)), int(cnt.get("OOS", 0))
        phase = ("test" if n_oos == len(seg) else "training" if n_is == len(seg) else
                 "before training" if n_pre == len(seg) else
                 "mostly before training" if n_pre > max(n_is, n_oos) else "mixed")
        rows.append({"period_name": name, "start_date": start, "end_date": end,
                     "is_oos": bool(n_oos == len(seg)), "phase": phase,
                     "n_pre_is": n_pre, "n_is": n_is, "n_oos": n_oos,
                     "ann_return": float(r.mean() * 12), "ann_vol": float(r.std() * np.sqrt(12)),
                     "sharpe": sharpe(r), "buy_hold_sharpe": sharpe(b), "n_obs": int(len(r)),
                     "max_drawdown": float((eq / eq.cummax() - 1).min()),
                     "strategy_return": float((1 + r).prod() - 1), "buy_hold_return": float((1 + b).prod() - 1)})
    pd.DataFrame(rows).to_csv(RES / "subperiod_sharpe.csv", index=False)
    pd.DataFrame([{k: r[k] for k in ("period_name", "start_date", "end_date", "n_obs", "buy_hold_sharpe",
                                     "buy_hold_return", "sharpe", "strategy_return")} for r in rows[:-1]]
                 ).to_csv(Path(VALID_DIR) / "stress_tests.csv", index=False)
    roll = strat["strategy_return"].where(strat["sample"] != "pre_IS").rolling(24, min_periods=16)
    pd.DataFrame({"date": strat.index, "rolling_sharpe_24m": roll.mean() / roll.std() * np.sqrt(12)}
                 ).dropna().to_csv(RES / f"rolling_sharpe_{PAIR_ID}.csv", index=False)
    bs = winner["selection"]["inference"]["oos_sharpe_diff_vs_bh_bootstrap"]
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "track": "as known at the time",
                   "oos_sharpe": winner["oos_sharpe"], "sharpe_diff_vs_bh": bs["observed"],
                   "ci_95_low": bs["ci_95"][0], "ci_95_high": bs["ci_95"][1], "p_diff_le_0": bs["p_diff_le_0"],
                   "method": bs["method"], "block_length": bs["block_length"], "draws": bs["draws"],
                   "seed": bs["seed"]}]).to_csv(Path(VALID_DIR) / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "tx_cost_bps": COST_BPS,
                   "gross_sharpe": winner["oos_sharpe"],
                   "net_sharpe": (winner["tracks"]["main"]["winner"] or {}).get("oos_sharpe_net_5bp")}]
                 ).to_csv(Path(VALID_DIR) / "transaction_costs.csv", index=False)


# ===================================================================
# METADATA
# ===================================================================

def write_metadata(model_results: dict, winner: dict, elapsed: float) -> None:
    reg_df = model_results.get("regressions", pd.DataFrame())
    observed = winner["direction"]
    key_finding = (f"As known at the time (real-time UMCSENT vintages), the rule selected on in-sample data uses "
                   f"{winner['signal_code']} / {winner['threshold_code']} / {winner['strategy_code']} at "
                   f"L{winner['lead_value']} (IS Sharpe {winner['is_sharpe']:.2f}); held-out OOS Sharpe "
                   f"{winner['oos_sharpe']:.2f} versus buy-and-hold XLV {winner['bh_sharpe']:.2f}.")
    if len(reg_df):
        best = reg_df.loc[reg_df["p_value"].idxmin()]
        key_finding += (f" Strongest predictive regression: {best['signal']} -> {best['horizon']} "
                        f"(t={best['t_stat']:.2f}, p={best['p_value']:.3f}).")
    interp = {
        "schema_version": "1.0.0", "pair_id": PAIR_ID, "indicator": "umcsent", "target": "xlv",
        "indicator_nature": "leading", "indicator_type": "sentiment", "strategy_objective": "min_mdd",
        "expected_direction": EXPECTED_DIRECTION, "observed_direction": observed,
        "direction_consistent": observed == EXPECTED_DIRECTION, "key_finding": key_finding,
        "owner_writes": {"dana": ["indicator", "target"],
                         "evan": ["indicator_nature", "indicator_type", "strategy_objective"],
                         "ray": ["key_finding"]},
        "last_updated_by": "evan", "last_updated_at": NOW_ISO,
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    def der(name, definition, formula, role, charts, notes=""):
        return {"name": name, "definition": definition, "formula": formula, "role": role,
                "appears_in_charts": charts, "notes": notes}
    code = {v: k for k, v in SIGNALS.items()}
    sig_note = lambda col: f"Tournament signal {code[col]}."  # noqa: E731
    scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {
            "canonical_column": "umcsent", "display_name": "University of Michigan Consumer Sentiment",
            "derivatives": [
                der("umcsent", "The University of Michigan index of consumer sentiment (monthly survey).",
                    "raw column (ALFRED/FRED UMCSENT; real-time vintages on the headline track)", "raw",
                    ["hero", "history_zoom_dotcom", "history_zoom_gfc", "history_zoom_covid",
                     "history_zoom_inflation_2022"], sig_note("umcsent")),
                der("umcsent_yoy", "Year-over-year percent change in consumer sentiment.",
                    "(umcsent / umcsent.shift(12) - 1) * 100", "derivative",
                    ["hero", "correlation_scatter", "correlations", "regime_stats", "ccf", "signal_dist",
                     "local_projections", "quantile_coef", "rolling_correlation", "rolling_granger",
                     "structural_break"], sig_note("umcsent_yoy")),
                der("umcsent_mom", "Month-over-month percent change in consumer sentiment.",
                    "(umcsent / umcsent.shift(1) - 1) * 100", "derivative", ["correlations"],
                    sig_note("umcsent_mom")),
                der("umcsent_zscore", "Consumer sentiment relative to its trailing 36-month mean, in standard deviations.",
                    "(umcsent - rolling_mean_36(umcsent)) / rolling_std_36(umcsent), min 24 readings", "derivative",
                    ["correlations", "equity_curves", "drawdown", "lead_plateau"], sig_note("umcsent_zscore")),
                der("umcsent_3m_ma", "Three-month moving average of consumer sentiment.",
                    "umcsent.rolling(3, min_periods=2).mean()", "derivative", ["correlations"],
                    sig_note("umcsent_3m_ma")),
                der("umcsent_direction", "Direction of the monthly change: +1 rising, -1 falling, 0 unchanged.",
                    "sign(umcsent_mom)", "derivative", ["correlations", "signal_dist"],
                    sig_note("umcsent_direction") + " Long/cash only (P2/P3 excluded on this flag)."),
                der("umcsent_dev_ma", "Consumer sentiment minus its three-month moving average.",
                    "umcsent - umcsent_3m_ma", "derivative", ["correlations"], sig_note("umcsent_dev_ma")),
            ],
        },
        "target_axis": {
            "canonical_column": "xlv", "display_name": "Health Care Select Sector (XLV)",
            "derivatives": [
                der("xlv", "XLV adjusted month-end close (dividends and splits).",
                    "pinned: data/phaseB_inputs/xlv_month_end_20261017.csv", "raw",
                    ["hero", "history_zoom_dotcom", "history_zoom_gfc", "history_zoom_covid",
                     "history_zoom_inflation_2022"]),
                der("xlv_ret", "XLV monthly return.", "xlv.pct_change()", "derivative",
                    ["equity_curves", "drawdown", "rolling_sharpe", "walk_forward", "subperiod_sharpe", "ccf",
                     "regime_stats", "rolling_correlation", "rolling_granger", "structural_break"]),
                der("xlv_fwd_1m", "XLV return over the next month.", "xlv.shift(-1) / xlv - 1", "derivative",
                    ["correlations"]),
                der("xlv_fwd_3m", "XLV return over the next three months.", "xlv.shift(-3) / xlv - 1", "derivative",
                    ["correlations", "signal_dist", "quantile_coef", "local_projections"]),
                der("xlv_fwd_6m", "XLV return over the next six months.", "xlv.shift(-6) / xlv - 1", "derivative",
                    ["correlations", "correlation_scatter", "local_projections"]),
                der("xlv_fwd_12m", "XLV return over the next twelve months.", "xlv.shift(-12) / xlv - 1",
                    "derivative", ["correlations", "local_projections"]),
            ],
        },
        "notes": ("Seven UMCSENT transforms are the tournament signals (pair spec SIGNALS). VIX, DGS10 and UNRATE "
                  "are regression controls only (local projections, random forest), not signals."),
    }
    (RES / "signal_scope.json").write_text(json.dumps(scope, indent=2) + "\n")

    (RES / "kpis.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"], "benchmark_oos_sharpe": winner["bh_sharpe"],
        "oos_max_drawdown": winner["oos_max_drawdown"], "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    (RES / "evidence_status.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search", "updated_at": NOW_ISO,
        "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": (f"Winner selected on in-sample data by the lead-plateau rule (D9) from the {DATE_TAG} "
                           "tournament on real-time UMCSENT vintages and reported on the test window (seen by earlier runs, so "
                           "not a frozen hold-out); "
                           "formal lead-lag (Granger) evidence is weak."),
        "next_step": "Freeze the selected rule and run a confirmation test on future data or a reserved holdout window.",
        "owner": "evan"}, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "elapsed_seconds": elapsed, "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
        "generated_at": NOW_ISO}, indent=2) + "\n")


NARRATIVE_SOURCES = [
    f"exploratory_{DATE_TAG}/regime_descriptive_stats.csv",
    f"exploratory_{DATE_TAG}/ccf.csv",
    f"exploratory_{DATE_TAG}/correlations.csv",
    f"core_models_{DATE_TAG}/granger_causality.csv",
    f"core_models_{DATE_TAG}/predictive_regressions.csv",
    f"core_models_{DATE_TAG}/quantile_regression.csv",
    f"core_models_{DATE_TAG}/local_projections.csv",
    "subperiod_sharpe.csv",
]


def write_narrative_provenance(df: pd.DataFrame) -> None:
    """evidence_facts_<tag>.json: the evidence tables the page prose cites (scripts/gate_number_provenance.py),
    plus facts computed here from the panel (sample sizes the prose states)."""
    xlv_first = df["xlv"].first_valid_index()
    derived = {
        "xlv_first_month": xlv_first.strftime("%Y-%m"),
        "panel_months": int(df["xlv_ret"].notna().sum()),
        "granger_min_p_umcsent_to_xlv": None,
        "granger_min_p_xlv_to_umcsent": None,
    }
    # numbers the page templates print from result files: trade-log row counts and the winner's rank by
    # training Sharpe among the valid combinations (the tournament table caption)
    derived["trade_log_rows"] = int(len(pd.read_csv(RES / "winner_trades_broker_style.csv")))
    derived["position_log_rows"] = int(len(pd.read_csv(RES / "winner_trade_log.csv")))
    t = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    v = t[t["valid"].astype(bool)].dropna(subset=["is_sharpe"])
    rk = v["is_sharpe"].rank(ascending=False, method="min")
    sel = v.index[v["selected"].astype(bool)]
    derived["winner_is_rank_among_valid"] = int(rk.loc[sel[0]]) if len(sel) else None
    # test-period position changes of the MAIN winner (winner_summary oos_n_trades is the harness abs_sum count:
    # int(sum |position change|), i.e. full XLV units traded); the P2 rule resizes most months
    sr = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv")
    dpos = np.abs(np.diff(sr.loc[sr["sample"] == "OOS", "position"].dropna().to_numpy(float)))
    derived["position_change_threshold_pp"] = 5
    derived["oos_months_position_change_gt_5pct"] = int((dpos > 0.05).sum())
    derived["oos_sum_abs_position_change"] = round(float(dpos.sum()), 4)
    # XLV pin splice (legacy closes through 2025-11, Yahoo from 2025-12): adjusted-close basis check
    sc = json.loads((Path(DATA_DIR) / "phaseB_inputs" / "xlv_splice_check_20261017.json").read_text())
    derived["xlv_splice_close_ratio_max_abs_dev"] = max(abs(sc["close_ratio_yahoo_over_legacy_min"] - 1),
                                                         abs(sc["close_ratio_max"] - 1))
    derived["xlv_splice_overlap_return_max_abs_diff"] = sc["monthly_return_max_abs_diff_overlap"]
    derived["xlv_splice_join_month_return_abs_diff"] = sc["join_month_abs_diff"]
    gc = pd.read_csv(Path(MODELS_DIR) / "granger_causality.csv")
    if len(gc):
        for d, k in (("UMCSENT->XLV", "granger_min_p_umcsent_to_xlv"), ("XLV->UMCSENT", "granger_min_p_xlv_to_umcsent")):
            sub = gc[gc["direction"] == d]
            derived[k] = float(sub["p_value"].min()) if len(sub) else None
    write_evidence_facts(PAIR_ID, DATE_TAG, sources=NARRATIVE_SOURCES, derived=derived)


def main() -> None:
    t0 = time.time()
    for d in (RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALID_DIR):
        os.makedirs(d, exist_ok=True)
    df = build_panel()
    df[[c for c in SIGNALS.values()]].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    stage_stationarity_and_quality(df)
    stage_exploratory(df)
    model_results = stage_core_models(df)
    stage_rolling_stability(df)
    _tourn, winner, _out = run_tournament()
    stage_validation(winner)
    write_metadata(model_results, winner, time.time() - t0)
    write_narrative_provenance(df)
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
