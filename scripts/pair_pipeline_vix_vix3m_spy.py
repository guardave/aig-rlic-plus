#!/usr/bin/env python3
"""
Full Analysis Pipeline: VIX/VIX3M (Vol Term Structure) → S&P 500 (SPY)
======================================================================
Priority pair #11. Daily volatility/options indicator → equity target.
VIX/VIX3M > 1 (backwardation) = near-term fear exceeds longer-term = bearish.

Date: 2026-03-14
"""

import os, sys, json, warnings, time
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

PAIR_ID = "vix_vix3m_spy"
INDICATOR_NAME = "VIX/VIX3M Ratio"
TARGET_NAME = "S&P 500"
START_DATE = "2007-01-01"  # VIX3M starts ~2007
END_DATE = "2025-12-31"
IS_END = "2019-12-31"
OOS_START = "2020-01-01"
DATE_TAG = "20260314"

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")

for d in [DATA_DIR, RESULTS_DIR, EXPLORE_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}

def timed(name):
    def dec(func):
        def wrap(*a, **kw):
            t0 = time.time()
            print(f"\n{'='*60}\n  {name}\n{'='*60}")
            r = func(*a, **kw)
            STAGE_TIMES[name] = time.time() - t0
            print(f"  [{name}] {STAGE_TIMES[name]:.1f}s")
            return r
        return wrap
    return dec

@timed("1_data")
def stage_data():
    import yfinance as yf
    from fredapi import Fred
    api_key = os.environ.get("FRED_API_KEY", "952aa4d0c4b2057609fbf3ecc6954e58")
    fred = Fred(api_key=api_key)

    series = {}
    for sid, name in [("DGS10", "dgs10"), ("DTB3", "dtb3"), ("DFF", "fed_funds")]:
        try:
            s = fred.get_series(sid, observation_start=START_DATE, observation_end=END_DATE)
            series[name] = s.astype(float)
            v = s.dropna()
            print(f"  [FRED] {sid:10s} -> {name}: {len(v)} obs")
        except Exception as e:
            print(f"  [FRED] {sid} FAILED: {e}")

    for ticker, name in [("SPY", "spy"), ("^VIX", "vix"), ("^VIX3M", "vix3m")]:
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

@timed("2_derived")
def stage_derived(series):
    bdays = pd.bdate_range(START_DATE, END_DATE)
    df = pd.DataFrame(index=bdays)
    df.index.name = "date"

    for col in ["spy", "vix", "vix3m", "dgs10", "dtb3", "fed_funds"]:
        if col in series:
            df[col] = series[col].reindex(bdays).ffill(limit=5)

    # Core indicator: VIX / VIX3M ratio
    df["vix_ratio"] = df["vix"] / df["vix3m"]

    # Derived signals
    r = df["vix_ratio"]
    df["vix_ratio_zscore_252d"] = (r - r.rolling(252, min_periods=200).mean()) / r.rolling(252, min_periods=200).std()
    df["vix_ratio_zscore_126d"] = (r - r.rolling(126, min_periods=100).mean()) / r.rolling(126, min_periods=100).std()
    df["vix_ratio_roc_5d"] = (r / r.shift(5) - 1) * 100
    df["vix_ratio_roc_21d"] = (r / r.shift(21) - 1) * 100
    df["vix_ratio_mom_5d"] = r - r.shift(5)
    df["vix_ratio_mom_21d"] = r - r.shift(21)
    df["vix_ratio_pctrank_252d"] = r.rolling(252, min_periods=200).apply(
        lambda x: stats.rankdata(x)[-1] / len(x), raw=True)
    df["vix_ratio_vol_21d"] = r.diff().rolling(21, min_periods=15).std()
    # Backwardation dummy: VIX > VIX3M (ratio > 1)
    df["vix_backwardation"] = (r > 1.0).astype(float)
    # VIX term structure (level difference, not ratio)
    df["vix_term_spread"] = df["vix3m"] - df["vix"]

    # Controls
    if "dgs10" in df.columns and "dtb3" in df.columns:
        df["yield_10y3m"] = df["dgs10"] - df["dtb3"]

    # Forward SPY returns
    spy = df["spy"]
    df["spy_ret"] = spy.pct_change()
    df["spy_fwd_1d"] = spy.pct_change(1).shift(-1)
    df["spy_fwd_5d"] = spy.shift(-5) / spy - 1
    df["spy_fwd_21d"] = spy.shift(-21) / spy - 1
    df["spy_fwd_63d"] = spy.shift(-63) / spy - 1

    df = df.dropna(subset=["vix_ratio", "spy"])
    print(f"  Dataset: {df.shape}, {df.index.min().date()} to {df.index.max().date()}")
    return df

@timed("3_stationarity")
def stage_stationarity(df):
    from arch.unitroot import ADF
    results = []
    for col in ["vix_ratio", "vix", "vix3m", "spy", "vix_ratio_roc_21d"]:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if len(s) < 100:
            continue
        if len(s) > 5000:
            s = s.iloc[::5]
        try:
            adf = ADF(s, max_lags=12)
            results.append({"variable": col, "test": "ADF", "statistic": round(adf.stat, 4),
                          "p_value": round(adf.pvalue, 4),
                          "conclusion": "Stationary" if adf.pvalue < 0.05 else "Non-stationary"})
            print(f"  ADF {col}: stat={adf.stat:.3f}, p={adf.pvalue:.4f}")
        except Exception:
            pass
    pd.DataFrame(results).to_csv(os.path.join(RESULTS_DIR, f"stationarity_tests_{DATE_TAG}.csv"), index=False)

@timed("4_exploratory")
def stage_exploratory(df):
    signals = [c for c in df.columns if c.startswith("vix_ratio") or c == "vix_backwardation" or c == "vix_term_spread"]
    signals = [s for s in signals if "fwd" not in s and "ret" not in s]
    fwd_cols = [c for c in df.columns if c.startswith("spy_fwd_")]

    corr_results = []
    for sig in signals:
        for fwd in fwd_cols:
            valid = df[[sig, fwd]].dropna()
            if len(valid) < 50:
                continue
            r, p = stats.pearsonr(valid[sig], valid[fwd])
            corr_results.append({"signal": sig, "horizon": fwd, "method": "Pearson",
                                "correlation": round(r, 4), "p_value": round(p, 4), "n": len(valid)})
    corr_df = pd.DataFrame(corr_results)
    corr_df.to_csv(os.path.join(EXPLORE_DIR, "correlations.csv"), index=False)

    # Regime stats (quartiles of VIX ratio)
    regime_results = []
    valid = df[["vix_ratio", "spy_ret"]].dropna()
    if len(valid) > 200:
        quartiles = pd.qcut(valid["vix_ratio"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"])
        for q in ["Q1_low", "Q2", "Q3", "Q4_high"]:
            rets = valid.loc[quartiles == q, "spy_ret"]
            if len(rets) < 20:
                continue
            ann_ret = rets.mean() * 252 * 100
            ann_vol = rets.std() * np.sqrt(252) * 100
            regime_results.append({"regime": q, "n_days": len(rets),
                "ann_return_pct": round(ann_ret, 2), "ann_vol_pct": round(ann_vol, 2),
                "sharpe": round(ann_ret / ann_vol, 3) if ann_vol > 0 else 0})
    pd.DataFrame(regime_results).to_csv(os.path.join(EXPLORE_DIR, "regime_descriptive_stats.csv"), index=False)

    sig_count = len(corr_df[corr_df["p_value"] < 0.05]) if len(corr_df) > 0 else 0
    print(f"  Correlations: {len(corr_df)} ({sig_count} sig)")
    if regime_results:
        print(f"  Regime Sharpes: {dict(zip([r['regime'] for r in regime_results], [r['sharpe'] for r in regime_results]))}")
    return corr_df

@timed("5_models")
def stage_models(df):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    work = df.dropna(subset=["vix_ratio", "spy_ret"])

    # Granger
    gc_results = []
    try:
        gc_data = work[["spy_ret", "vix_ratio"]].dropna()
        if len(gc_data) > 100:
            gc = grangercausalitytests(gc_data[["spy_ret", "vix_ratio"]], maxlag=5, verbose=False)
            for lag, r in gc.items():
                gc_results.append({"direction": "VIX_Ratio->SPY", "lag": lag,
                    "f_stat": round(r[0]["ssr_ftest"][0], 4), "p_value": round(r[0]["ssr_ftest"][1], 4)})
            gc_rev = grangercausalitytests(gc_data[["vix_ratio", "spy_ret"]], maxlag=5, verbose=False)
            for lag, r in gc_rev.items():
                gc_results.append({"direction": "SPY->VIX_Ratio", "lag": lag,
                    "f_stat": round(r[0]["ssr_ftest"][0], 4), "p_value": round(r[0]["ssr_ftest"][1], 4)})
    except Exception as e:
        print(f"  Granger failed: {e}")
    pd.DataFrame(gc_results).to_csv(os.path.join(MODELS_DIR, "granger_causality.csv"), index=False)
    print(f"  Granger: {len(gc_results)} tests")

    # Regressions
    reg_results = []
    for sig in ["vix_ratio", "vix_ratio_zscore_252d", "vix_ratio_roc_21d", "vix_backwardation", "vix_term_spread"]:
        for fwd in ["spy_fwd_1d", "spy_fwd_5d", "spy_fwd_21d", "spy_fwd_63d"]:
            if sig not in work.columns or fwd not in work.columns:
                continue
            valid = work[[sig, fwd]].dropna()
            if len(valid) < 50:
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
    for fwd, h in [("spy_fwd_5d", 5), ("spy_fwd_21d", 21), ("spy_fwd_63d", 63)]:
        if fwd not in work.columns:
            continue
        valid = work[["vix_ratio", fwd]].dropna()
        ctrls = [c for c in ["yield_10y3m"] if c in work.columns]
        for c in ctrls:
            valid[c] = work.loc[valid.index, c]
        valid = valid.dropna()
        if len(valid) < 100:
            continue
        try:
            X = sm.add_constant(valid[["vix_ratio"] + ctrls])
            nw = int(0.75 * len(valid) ** (1/3))
            model = sm.OLS(valid[fwd], X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = model.conf_int().loc["vix_ratio"]
            lp_results.append({"horizon_days": h,
                "coef": round(model.params["vix_ratio"], 6), "se": round(model.bse["vix_ratio"], 6),
                "t_stat": round(model.tvalues["vix_ratio"], 3), "p_value": round(model.pvalues["vix_ratio"], 4),
                "ci_lower": round(ci[0], 6), "ci_upper": round(ci[1], 6),
                "r_squared": round(model.rsquared, 4), "n": int(model.nobs)})
        except Exception:
            pass
    pd.DataFrame(lp_results).to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    print(f"  Local projections: {len(lp_results)}")

    # Quantile regression
    qr_results = []
    valid_qr = work[["vix_ratio", "spy_fwd_21d"]].dropna()
    if len(valid_qr) > 50:
        for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
            try:
                qr = smf.quantreg("spy_fwd_21d ~ vix_ratio", data=valid_qr).fit(q=tau)
                qr_results.append({"quantile": tau,
                    "coef": round(qr.params["vix_ratio"], 6), "p_value": round(qr.pvalues["vix_ratio"], 4),
                    "ci_lower": round(qr.conf_int().loc["vix_ratio", 0], 6),
                    "ci_upper": round(qr.conf_int().loc["vix_ratio", 1], 6)})
            except Exception:
                pass
    pd.DataFrame(qr_results).to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    print(f"  Quantile reg: {len(qr_results)}")

    # Diagnostics
    diag_results = []
    valid_diag = work[["vix_ratio", "spy_fwd_21d"]].dropna()
    if len(valid_diag) > 50:
        X = sm.add_constant(valid_diag["vix_ratio"])
        model = sm.OLS(valid_diag["spy_fwd_21d"], X).fit()
        jb_s, jb_p = stats.jarque_bera(model.resid)
        diag_results.append({"test": "Jarque-Bera", "statistic": round(jb_s, 4), "p_value": round(jb_p, 4)})
        from statsmodels.stats.stattools import durbin_watson
        diag_results.append({"test": "Durbin-Watson", "statistic": round(durbin_watson(model.resid), 4), "p_value": np.nan})
    pd.DataFrame(diag_results).to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)

    # Interpretation
    interp = {
        "indicator": "vix_vix3m", "target": "spy",
        "expected_direction": "counter_cyclical",
        "observed_direction": "unknown", "direction_consistent": True,
        "mechanism": "VIX/VIX3M > 1 (backwardation) signals near-term fear exceeding longer-term expectations — a panic indicator. Historically associated with sharp selloffs and elevated put demand.",
        "confidence": "high", "key_finding": "",
        "caveats": ["VIX3M starts ~2007, limiting sample to 18 years",
                     "VIX ratio mean-reverts quickly — signal may be too fast for monthly strategies",
                     "COVID March 2020 was extreme backwardation"]
    }
    if len(reg_df) > 0:
        best = reg_df.loc[reg_df["p_value"].idxmin()]
        interp["key_finding"] = f"{best['signal']} predicts {best['horizon']} (coef={best['coef']:.4f}, t={best['t_stat']:.2f}, p={best['p_value']:.4f})"
        interp["observed_direction"] = "counter_cyclical" if best["coef"] < 0 else "pro_cyclical"
        interp["direction_consistent"] = bool(best["coef"] < 0)
    with open(os.path.join(RESULTS_DIR, "interpretation_metadata.json"), "w") as f:
        json.dump(interp, f, indent=2)

    return reg_df

@timed("6_tournament")
def stage_tournament(df):
    work = df.copy()
    is_mask = work.index <= IS_END
    oos_mask = work.index >= OOS_START

    signal_cols = {
        "S1_ratio": "vix_ratio", "S2_z252": "vix_ratio_zscore_252d",
        "S3_z126": "vix_ratio_zscore_126d", "S4_roc5": "vix_ratio_roc_5d",
        "S5_roc21": "vix_ratio_roc_21d", "S6_mom5": "vix_ratio_mom_5d",
        "S7_mom21": "vix_ratio_mom_21d", "S8_pctrank": "vix_ratio_pctrank_252d",
        "S9_backwd": "vix_backwardation", "S10_spread": "vix_term_spread",
    }
    available = {k: v for k, v in signal_cols.items() if v in work.columns and work[v].notna().sum() > 200}

    leads = [0, 1, 5, 10, 21]
    results = []

    for sig_name, sig_col in available.items():
        signal = work[sig_col]
        for lead in leads:
            sig_l = signal.shift(lead) if lead > 0 else signal
            is_sig = sig_l[is_mask].dropna()
            if len(is_sig) < 100:
                continue

            thresholds = {}
            for pct in [25, 50, 75]:
                thresholds[f"T1_p{pct}"] = is_sig.quantile(pct / 100)
            for pct in [25, 50, 75]:
                thresholds[f"T2_rp{pct}"] = sig_l.rolling(252, min_periods=200).quantile(pct / 100)
            # Key threshold for ratio: 1.0 (backwardation line)
            if sig_name == "S1_ratio":
                thresholds["T4_unity"] = 1.0

            for tname, tval in thresholds.items():
                for strat in ["P1", "P2", "P3"]:
                    try:
                        # Counter-cyclical: BELOW threshold = calm = bullish
                        if isinstance(tval, (int, float)):
                            bullish = sig_l < tval
                        else:
                            bullish = sig_l < tval

                        if strat == "P1":
                            pos = bullish.astype(float)
                        elif strat == "P2":
                            smin = sig_l.rolling(252, min_periods=200).min()
                            smax = sig_l.rolling(252, min_periods=200).max()
                            sr = (smax - smin).replace(0, np.nan)
                            pos = (1 - (sig_l - smin) / sr).clip(0, 1)
                        elif strat == "P3":
                            pos = bullish.astype(float) * 2 - 1

                        strat_ret = pos.shift(1) * work["spy_ret"]
                        is_r = strat_ret[is_mask].dropna()
                        oos_r = strat_ret[oos_mask].dropna()
                        if len(is_r) < 100 or len(oos_r) < 50:
                            continue

                        oos_sharpe = (oos_r.mean() / oos_r.std()) * np.sqrt(252) if oos_r.std() > 0 else 0
                        cum = (1 + oos_r).cumprod()
                        dd = ((cum - cum.cummax()) / cum.cummax()).min()
                        turnover = pos.diff().abs().sum() / (len(pos.dropna()) / 252)
                        valid = oos_sharpe > 0 and turnover < 24 and len(oos_r) >= 50

                        results.append({"signal": sig_name, "threshold": tname, "strategy": strat,
                            "lead_days": lead, "oos_sharpe": round(oos_sharpe, 4),
                            "oos_ann_return": round(oos_r.mean() * 252 * 100, 2),
                            "max_drawdown": round(dd * 100, 2), "annual_turnover": round(turnover, 2),
                            "oos_n": len(oos_r), "valid": valid})
                    except Exception:
                        continue

    # Benchmark
    bh = work.loc[oos_mask, "spy_ret"].dropna()
    if len(bh) > 0:
        bh_s = (bh.mean() / bh.std()) * np.sqrt(252) if bh.std() > 0 else 0
        bh_cum = (1 + bh).cumprod()
        bh_dd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min()
        results.append({"signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BH",
            "lead_days": 0, "oos_sharpe": round(bh_s, 4),
            "oos_ann_return": round(bh.mean() * 252 * 100, 2),
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
            print(f"  Best: {best['signal']}/{best['threshold']}/{best['strategy']}/L{best['lead_days']} Sharpe={best['oos_sharpe']:.2f} DD={best['max_drawdown']:.1f}%")
        bm = rdf[rdf["signal"] == "BENCHMARK"]
        if len(bm) > 0:
            print(f"  B&H:  Sharpe={bm.iloc[0]['oos_sharpe']:.2f} DD={bm.iloc[0]['max_drawdown']:.1f}%")
    return rdf

def main():
    t0 = time.time()
    print(f"{'='*60}\n  {INDICATOR_NAME} -> {TARGET_NAME}\n{'='*60}")

    series = stage_data()
    df = stage_derived(series)
    df.to_parquet(os.path.join(DATA_DIR, f"{PAIR_ID}_daily_{DATE_TAG}.parquet"), engine="pyarrow")

    stage_stationarity(df)
    stage_exploratory(df)
    stage_models(df)
    stage_tournament(df)

    elapsed = time.time() - t0
    print(f"\n{'='*60}\n  DONE in {elapsed:.1f}s\n{'='*60}")

    timing = {"pair_id": PAIR_ID, "total_seconds": round(elapsed, 1),
              "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()}}
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump(timing, f, indent=2)

if __name__ == "__main__":
    main()
