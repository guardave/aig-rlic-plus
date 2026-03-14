#!/usr/bin/env python3
"""
Full Analysis Pipeline: Building Permits (PERMIT) → S&P 500 (SPY)
=================================================================
Priority pair #3. Monthly housing indicator → equity target.
Adapted from INDPRO template.

Date: 2026-03-14
"""

import os, sys, json, warnings, time
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

PAIR_ID = "permit_spy"
INDICATOR_NAME = "Building Permits"
TARGET_NAME = "S&P 500"
START_DATE = "1990-01-01"
END_DATE = "2025-12-31"
IS_END = "2017-12-31"
OOS_START = "2018-01-01"
DATE_TAG = "20260314"

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")

for d in [DATA_DIR, RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}

def timed(name):
    def dec(func):
        def wrap(*a, **kw):
            t0 = time.time()
            print(f"\n{'='*60}\n  {name}\n{'='*60}")
            r = func(*a, **kw)
            el = time.time() - t0
            STAGE_TIMES[name] = el
            print(f"  [{name}] {el:.1f}s")
            return r
        return wrap
    return dec

# ===== STAGE 1: DATA =====
@timed("1_data")
def stage_data():
    from fredapi import Fred
    import yfinance as yf

    api_key = os.environ.get("FRED_API_KEY", "952aa4d0c4b2057609fbf3ecc6954e58")
    fred = Fred(api_key=api_key)

    series = {}
    for sid, name in [("PERMIT", "permit"), ("UNRATE", "unrate"), ("HOUST", "houst"),
                      ("DGS10", "dgs10"), ("DTB3", "dtb3"), ("DFF", "fed_funds")]:
        try:
            s = fred.get_series(sid, observation_start=START_DATE, observation_end=END_DATE)
            series[name] = s.astype(float)
            v = s.dropna()
            print(f"  [FRED] {sid:10s} -> {name}: {len(v)} obs, {v.index.min().date()} to {v.index.max().date()}")
        except Exception as e:
            print(f"  [FRED] {sid} FAILED: {e}")

    for ticker, name in [("SPY", "spy"), ("^VIX", "vix")]:
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            s = df["Close"]
            s.index = s.index.tz_localize(None) if s.index.tz else s.index
            series[name] = s.astype(float)
            print(f"  [YF]   {ticker:10s} -> {name}: {len(s)} obs")
        except Exception as e:
            print(f"  [YF]   {ticker} FAILED: {e}")

    return series

# ===== STAGE 2: ALIGNMENT + DERIVED =====
@timed("2_derived")
def stage_derived(series):
    monthly_idx = pd.date_range(START_DATE, END_DATE, freq="ME")
    df = pd.DataFrame(index=monthly_idx)
    df.index.name = "date"

    monthly_cols = {"permit", "unrate", "houst"}
    daily_cols = {"spy", "vix", "dgs10", "dtb3", "fed_funds"}

    for col in monthly_cols:
        if col in series:
            df[col] = series[col].resample("ME").last().reindex(monthly_idx)
    for col in daily_cols:
        if col in series:
            df[col] = series[col].resample("ME").last().reindex(monthly_idx)
    df = df.ffill(limit=2)

    # Derived
    p = df["permit"]
    df["permit_yoy"] = (p / p.shift(12) - 1) * 100
    df["permit_mom"] = (p / p.shift(1) - 1) * 100
    df["permit_ma12"] = p.rolling(12, min_periods=10).mean()
    df["permit_dev_trend"] = p - df["permit_ma12"]
    rm60 = p.rolling(60, min_periods=48)
    df["permit_zscore_60m"] = (p - rm60.mean()) / rm60.std()
    df["permit_mom_3m"] = p - p.shift(3)
    df["permit_mom_6m"] = p - p.shift(6)
    df["permit_accel"] = df["permit_mom"] - df["permit_mom"].shift(1)
    df["permit_contraction"] = (df["permit_yoy"] < 0).astype(int)

    if "dgs10" in df.columns and "dtb3" in df.columns:
        df["yield_spread_10y3m"] = df["dgs10"] - df["dtb3"]

    if "spy" in df.columns:
        df["spy_ret"] = df["spy"].pct_change()
        spy = df["spy"]
        df["spy_fwd_1m"] = spy.shift(-1) / spy - 1
        df["spy_fwd_3m"] = spy.shift(-3) / spy - 1
        df["spy_fwd_6m"] = spy.shift(-6) / spy - 1
        df["spy_fwd_12m"] = spy.shift(-12) / spy - 1

    df = df.dropna(subset=["permit"])
    print(f"  Monthly: {df.shape}, {df.index.min().date()} to {df.index.max().date()}")
    return df

# ===== STAGE 3: STATIONARITY =====
@timed("3_stationarity")
def stage_stationarity(df):
    from arch.unitroot import ADF, KPSS
    results = []
    for col in ["permit", "spy", "permit_yoy", "permit_mom", "unrate"]:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if len(s) < 50:
            continue
        try:
            adf = ADF(s, max_lags=12)
            results.append({"variable": col, "test": "ADF", "statistic": round(adf.stat, 4),
                          "p_value": round(adf.pvalue, 4),
                          "conclusion": "Stationary" if adf.pvalue < 0.05 else "Non-stationary"})
        except Exception:
            pass
        try:
            kpss = KPSS(s)
            results.append({"variable": col, "test": "KPSS", "statistic": round(kpss.stat, 4),
                          "p_value": round(kpss.pvalue, 4),
                          "conclusion": "Stationary" if kpss.pvalue > 0.05 else "Non-stationary"})
        except Exception:
            pass
    stat_df = pd.DataFrame(results)
    stat_df.to_csv(os.path.join(RESULTS_DIR, f"stationarity_tests_{DATE_TAG}.csv"), index=False)
    print(f"  {len(stat_df)} tests saved")
    return stat_df

# ===== STAGE 4: EXPLORATORY =====
@timed("4_exploratory")
def stage_exploratory(df):
    signals = [c for c in df.columns if c.startswith("permit_") and "fwd" not in c and "ma12" not in c]
    fwd_cols = [c for c in df.columns if c.startswith("spy_fwd_")]

    corr_results = []
    for sig in signals:
        for fwd in fwd_cols:
            valid = df[[sig, fwd]].dropna()
            if len(valid) < 30:
                continue
            r, p = stats.pearsonr(valid[sig], valid[fwd])
            corr_results.append({"signal": sig, "horizon": fwd, "method": "Pearson",
                                "correlation": round(r, 4), "p_value": round(p, 4), "n": len(valid)})
    corr_df = pd.DataFrame(corr_results)
    corr_df.to_csv(os.path.join(EXPLORE_DIR, "correlations.csv"), index=False)

    # Regime stats
    regime_results = []
    if "permit_yoy" in df.columns and "spy_ret" in df.columns:
        valid = df[["permit_yoy", "spy_ret"]].dropna()
        if len(valid) > 100:
            quartiles = pd.qcut(valid["permit_yoy"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"])
            for q in ["Q1_low", "Q2", "Q3", "Q4_high"]:
                rets = valid.loc[quartiles == q, "spy_ret"]
                if len(rets) < 5:
                    continue
                ann_ret = rets.mean() * 12 * 100
                ann_vol = rets.std() * np.sqrt(12) * 100
                regime_results.append({"regime": q, "n_months": len(rets),
                    "ann_return_pct": round(ann_ret, 2), "ann_vol_pct": round(ann_vol, 2),
                    "sharpe": round(ann_ret / ann_vol, 3) if ann_vol > 0 else 0})
    pd.DataFrame(regime_results).to_csv(os.path.join(EXPLORE_DIR, "regime_descriptive_stats.csv"), index=False)

    sig_count = len(corr_df[corr_df["p_value"] < 0.05]) if len(corr_df) > 0 else 0
    print(f"  Correlations: {len(corr_df)} ({sig_count} sig)")
    if regime_results:
        print(f"  Regime Sharpes: {dict(zip([r['regime'] for r in regime_results], [r['sharpe'] for r in regime_results]))}")
    return corr_df

# ===== STAGE 5: CORE MODELS =====
@timed("5_models")
def stage_models(df):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    base_cols = ["permit_yoy", "permit_mom", "permit_zscore_60m", "permit_contraction",
                 "permit_mom_3m", "permit_mom_6m", "permit_accel",
                 "spy_ret", "spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]
    ctrl_cols = ["vix", "yield_spread_10y3m", "unrate"]
    work_cols = [c for c in base_cols + ctrl_cols if c in df.columns]
    work = df[work_cols].dropna(subset=["permit_yoy", "spy_ret"])
    print(f"  Working: {work.shape}")

    # Granger
    gc_results = []
    try:
        gc_data = work[["spy_ret", "permit_yoy"]].dropna()
        if len(gc_data) > 50:
            gc = grangercausalitytests(gc_data[["spy_ret", "permit_yoy"]], maxlag=6, verbose=False)
            for lag, r in gc.items():
                gc_results.append({"direction": "Permit->SPY", "lag": lag,
                    "f_stat": round(r[0]["ssr_ftest"][0], 4), "p_value": round(r[0]["ssr_ftest"][1], 4)})
            gc_rev = grangercausalitytests(gc_data[["permit_yoy", "spy_ret"]], maxlag=6, verbose=False)
            for lag, r in gc_rev.items():
                gc_results.append({"direction": "SPY->Permit", "lag": lag,
                    "f_stat": round(r[0]["ssr_ftest"][0], 4), "p_value": round(r[0]["ssr_ftest"][1], 4)})
    except Exception as e:
        print(f"  Granger failed: {e}")
    pd.DataFrame(gc_results).to_csv(os.path.join(MODELS_DIR, "granger_causality.csv"), index=False)
    print(f"  Granger: {len(gc_results)} tests")

    # Regressions
    reg_results = []
    for sig in ["permit_yoy", "permit_mom", "permit_zscore_60m"]:
        for fwd in ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]:
            if sig not in work.columns or fwd not in work.columns:
                continue
            valid = work[[sig, fwd]].dropna()
            if len(valid) < 30:
                continue
            try:
                X = sm.add_constant(valid[sig])
                model = sm.OLS(valid[fwd], X).fit(cov_type="HC3")
                reg_results.append({"signal": sig, "horizon": fwd,
                    "coef": round(model.params.iloc[1], 6), "t_stat": round(model.tvalues.iloc[1], 3),
                    "p_value": round(model.pvalues.iloc[1], 4), "r_squared": round(model.rsquared, 4),
                    "n": int(model.nobs)})
            except Exception:
                pass
    reg_df = pd.DataFrame(reg_results)
    reg_df.to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    print(f"  Regressions: {len(reg_df)}")

    # Local projections
    lp_results = []
    for fwd, h in [("spy_fwd_1m", 1), ("spy_fwd_3m", 3), ("spy_fwd_6m", 6), ("spy_fwd_12m", 12)]:
        if fwd not in work.columns:
            continue
        valid = work[["permit_yoy", fwd]].dropna()
        ctrls = [c for c in ["vix", "yield_spread_10y3m"] if c in work.columns]
        for c in ctrls:
            valid[c] = work.loc[valid.index, c]
        valid = valid.dropna()
        if len(valid) < 30:
            continue
        try:
            X = sm.add_constant(valid[["permit_yoy"] + ctrls])
            nw = int(0.75 * len(valid) ** (1/3))
            model = sm.OLS(valid[fwd], X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = model.conf_int().loc["permit_yoy"]
            lp_results.append({"horizon_months": h,
                "coef": round(model.params["permit_yoy"], 6), "se": round(model.bse["permit_yoy"], 6),
                "t_stat": round(model.tvalues["permit_yoy"], 3), "p_value": round(model.pvalues["permit_yoy"], 4),
                "ci_lower": round(ci[0], 6), "ci_upper": round(ci[1], 6),
                "r_squared": round(model.rsquared, 4), "n": int(model.nobs)})
        except Exception:
            pass
    pd.DataFrame(lp_results).to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    print(f"  Local projections: {len(lp_results)} horizons")

    # Quantile regression
    qr_results = []
    valid_qr = work[["permit_yoy", "spy_fwd_3m"]].dropna()
    if len(valid_qr) > 30:
        for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
            try:
                qr = smf.quantreg("spy_fwd_3m ~ permit_yoy", data=valid_qr).fit(q=tau)
                qr_results.append({"quantile": tau,
                    "coef": round(qr.params["permit_yoy"], 6), "p_value": round(qr.pvalues["permit_yoy"], 4),
                    "ci_lower": round(qr.conf_int().loc["permit_yoy", 0], 6),
                    "ci_upper": round(qr.conf_int().loc["permit_yoy", 1], 6)})
            except Exception:
                pass
    pd.DataFrame(qr_results).to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    print(f"  Quantile reg: {len(qr_results)} quantiles")

    # Diagnostics
    diag_results = []
    valid_diag = work[["permit_yoy", "spy_fwd_3m"]].dropna()
    if len(valid_diag) > 30:
        X = sm.add_constant(valid_diag["permit_yoy"])
        model = sm.OLS(valid_diag["spy_fwd_3m"], X).fit()
        resid = model.resid
        jb_s, jb_p = stats.jarque_bera(resid)
        diag_results.append({"test": "Jarque-Bera", "statistic": round(jb_s, 4), "p_value": round(jb_p, 4)})
        from statsmodels.stats.stattools import durbin_watson
        dw = durbin_watson(resid)
        diag_results.append({"test": "Durbin-Watson", "statistic": round(dw, 4), "p_value": np.nan})
    pd.DataFrame(diag_results).to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)

    # Interpretation metadata
    interp = {
        "indicator": "permit", "target": "spy",
        "expected_direction": "pro_cyclical", "observed_direction": "unknown",
        "direction_consistent": True,
        "mechanism": "Rising building permits signal housing expansion, driving employment, consumer wealth, and material demand — bullish for equities.",
        "confidence": "high", "key_finding": "", "caveats": [
            "Monthly frequency with ~3-week publication lag",
            "Housing bubble (2003-2007) may dominate regime models",
            "COVID April 2020 collapse is an outlier"
        ]
    }
    if len(reg_df) > 0:
        best = reg_df.loc[reg_df["p_value"].idxmin()]
        interp["key_finding"] = f"{best['signal']} predicts {best['horizon']} (coef={best['coef']:.4f}, t={best['t_stat']:.2f}, p={best['p_value']:.4f})"
        interp["observed_direction"] = "pro_cyclical" if best["coef"] > 0 else "counter_cyclical"
        interp["direction_consistent"] = bool(best["coef"] > 0)

    with open(os.path.join(RESULTS_DIR, "interpretation_metadata.json"), "w") as f:
        json.dump(interp, f, indent=2)

    return reg_df

# ===== STAGE 6: TOURNAMENT =====
@timed("6_tournament")
def stage_tournament(df):
    work = df.copy().dropna(subset=["permit"])
    is_mask = work.index <= IS_END
    oos_mask = work.index >= OOS_START

    if "spy_ret" not in work.columns:
        work["spy_ret"] = work["spy"].pct_change()

    signal_cols = {"S1_level": "permit", "S2_yoy": "permit_yoy", "S3_mom": "permit_mom",
                   "S4_dev": "permit_dev_trend", "S5_z": "permit_zscore_60m",
                   "S6_mom3m": "permit_mom_3m", "S7_mom6m": "permit_mom_6m",
                   "S8_accel": "permit_accel", "S9_contr": "permit_contraction"}
    available = {k: v for k, v in signal_cols.items() if v in work.columns and work[v].notna().sum() > 50}

    leads = [0, 1, 2, 3, 6]
    results = []

    for sig_name, sig_col in available.items():
        signal = work[sig_col]
        for lead in leads:
            sig_l = signal.shift(lead) if lead > 0 else signal
            is_sig = sig_l[is_mask].dropna()
            if len(is_sig) < 20:
                continue

            thresholds = {}
            for pct in [25, 50, 75]:
                thresholds[f"T1_p{pct}"] = is_sig.quantile(pct / 100)
            for pct in [25, 50, 75]:
                thresholds[f"T2_rp{pct}"] = sig_l.rolling(60, min_periods=36).quantile(pct / 100)
            if sig_name in ["S2_yoy", "S3_mom", "S8_accel"]:
                thresholds["T4_zero"] = 0

            for tname, tval in thresholds.items():
                for strat in ["P1", "P2", "P3"]:
                    try:
                        if isinstance(tval, (int, float)):
                            bullish = sig_l > tval
                        else:
                            bullish = sig_l > tval

                        if strat == "P1":
                            pos = bullish.astype(float)
                        elif strat == "P2":
                            smin = sig_l.rolling(60, min_periods=36).min()
                            smax = sig_l.rolling(60, min_periods=36).max()
                            sr = (smax - smin).replace(0, np.nan)
                            pos = ((sig_l - smin) / sr).clip(0, 1)
                        elif strat == "P3":
                            pos = bullish.astype(float) * 2 - 1

                        strat_ret = pos.shift(1) * work["spy_ret"]
                        is_r = strat_ret[is_mask].dropna()
                        oos_r = strat_ret[oos_mask].dropna()
                        if len(is_r) < 24 or len(oos_r) < 12:
                            continue

                        oos_sharpe = (oos_r.mean() / oos_r.std()) * np.sqrt(12) if oos_r.std() > 0 else 0
                        cum = (1 + oos_r).cumprod()
                        dd = ((cum - cum.cummax()) / cum.cummax()).min()
                        turnover = pos.diff().abs().sum() / (len(pos.dropna()) / 12)
                        valid = oos_sharpe > 0 and turnover < 24 and len(oos_r) >= 12

                        results.append({"signal": sig_name, "threshold": tname, "strategy": strat,
                            "lead_months": lead, "oos_sharpe": round(oos_sharpe, 4),
                            "oos_ann_return": round(oos_r.mean() * 12 * 100, 2),
                            "max_drawdown": round(dd * 100, 2), "annual_turnover": round(turnover, 2),
                            "oos_n": len(oos_r), "valid": valid})
                    except Exception:
                        continue

    # Benchmark
    bh = work.loc[oos_mask, "spy_ret"].dropna()
    if len(bh) > 0:
        bh_s = (bh.mean() / bh.std()) * np.sqrt(12) if bh.std() > 0 else 0
        bh_cum = (1 + bh).cumprod()
        bh_dd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min()
        results.append({"signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BH",
            "lead_months": 0, "oos_sharpe": round(bh_s, 4),
            "oos_ann_return": round(bh.mean() * 12 * 100, 2),
            "max_drawdown": round(bh_dd * 100, 2), "annual_turnover": 0,
            "oos_n": len(bh), "valid": True})

    rdf = pd.DataFrame(results)
    rdf.to_csv(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv"), index=False)

    valid_count = rdf["valid"].sum() if len(rdf) > 0 else 0
    print(f"  Tournament: {len(rdf)} combos, {valid_count} valid")
    if len(rdf) > 0:
        vs = rdf[rdf["valid"] & (rdf["signal"] != "BENCHMARK")]
        if len(vs) > 0:
            best = vs.loc[vs["oos_sharpe"].idxmax()]
            print(f"  Best: {best['signal']}/{best['threshold']}/{best['strategy']}/L{best['lead_months']} Sharpe={best['oos_sharpe']:.2f} DD={best['max_drawdown']:.1f}%")
        bm = rdf[rdf["signal"] == "BENCHMARK"]
        if len(bm) > 0:
            print(f"  B&H:  Sharpe={bm.iloc[0]['oos_sharpe']:.2f} DD={bm.iloc[0]['max_drawdown']:.1f}%")
    return rdf

# ===== MAIN =====
def main():
    t0 = time.time()
    print(f"{'='*60}\n  {INDICATOR_NAME} -> {TARGET_NAME}\n{'='*60}")

    series = stage_data()
    df = stage_derived(series)
    df.to_parquet(os.path.join(DATA_DIR, f"{PAIR_ID}_monthly_{DATE_TAG}.parquet"), engine="pyarrow")

    stage_stationarity(df)
    stage_exploratory(df)
    reg_df = stage_models(df)
    tourn_df = stage_tournament(df)

    elapsed = time.time() - t0
    print(f"\n{'='*60}\n  DONE in {elapsed:.1f}s\n{'='*60}")

    timing = {"pair_id": PAIR_ID, "total_seconds": round(elapsed, 1),
              "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()}}
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump(timing, f, indent=2)

if __name__ == "__main__":
    main()
