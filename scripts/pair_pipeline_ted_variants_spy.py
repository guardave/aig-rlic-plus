#!/usr/bin/env python3
"""
Full Analysis Pipeline: TED Spread Variants → S&P 500 (SPY)
============================================================
Runs 3 variants of the funding-stress indicator:
  A) SOFR - DTB3  (pure SOFR-based, 2018-2025)
  B) DFF - DTB3   (Fed Funds TED, 1993-2025)
  C) TEDRATE + adjusted DFF-TED splice (1993-2025)

Shared data sourcing, separate analysis per variant.

Date: 2026-03-14
Analysis Brief: docs/analysis_brief_sofr_us3m_spy_20260314.md
"""

import os, sys, json, warnings, time
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
DATE_TAG = "20260314"
os.makedirs(DATA_DIR, exist_ok=True)

STAGE_TIMES = {}

def timed(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            t0 = time.time()
            print(f"\n{'='*60}\n  {name}\n{'='*60}")
            result = func(*args, **kwargs)
            elapsed = time.time() - t0
            STAGE_TIMES[name] = elapsed
            print(f"  [{name}] {elapsed:.1f}s")
            return result
        return wrapper
    return decorator


# =====================================================================
# SHARED DATA SOURCING
# =====================================================================

@timed("data_sourcing")
def source_all():
    from fredapi import Fred
    import yfinance as yf

    api_key = os.environ.get("FRED_API_KEY", "952aa4d0c4b2057609fbf3ecc6954e58")
    fred = Fred(api_key=api_key)

    series = {}
    for sid, name in [("TEDRATE", "tedrate"), ("SOFR", "sofr"), ("DTB3", "dtb3"),
                      ("DFF", "dff"), ("DGS10", "dgs10")]:
        try:
            s = fred.get_series(sid, observation_start="1986-01-01", observation_end="2025-12-31")
            series[name] = s.astype(float)
            valid = s.dropna()
            print(f"  [FRED] {sid:10s} -> {name}: {len(valid)} obs, {valid.index.min().date()} to {valid.index.max().date()}")
        except Exception as e:
            print(f"  [FRED] {sid} FAILED: {e}")

    for ticker, name in [("SPY", "spy"), ("^VIX", "vix")]:
        try:
            df = yf.download(ticker, start="1993-01-01", end="2025-12-31", progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            s = df["Close"]
            s.index = s.index.tz_localize(None) if s.index.tz else s.index
            series[name] = s.astype(float)
            print(f"  [YF]   {ticker:10s} -> {name}: {len(s)} obs")
        except Exception as e:
            print(f"  [YF]   {ticker} FAILED: {e}")

    return series


# =====================================================================
# BUILD 3 VARIANT DATASETS
# =====================================================================

@timed("build_variants")
def build_variants(series):
    bdays = pd.bdate_range("1993-01-01", "2025-12-31")
    base = pd.DataFrame(index=bdays)
    base.index.name = "date"

    for col in ["tedrate", "sofr", "dtb3", "dff", "dgs10", "spy", "vix"]:
        if col in series:
            base[col] = series[col].reindex(bdays).ffill(limit=5)

    # Forward SPY returns
    spy = base["spy"]
    base["spy_fwd_1d"] = spy.pct_change(1).shift(-1)
    base["spy_fwd_5d"] = spy.shift(-5) / spy - 1
    base["spy_fwd_21d"] = spy.shift(-21) / spy - 1
    base["spy_fwd_63d"] = spy.shift(-63) / spy - 1
    base["spy_ret"] = spy.pct_change()

    # Yield spread control
    if "dgs10" in base.columns and "dtb3" in base.columns:
        base["yield_10y3m"] = base["dgs10"] - base["dtb3"]

    variants = {}

    # --- Variant A: SOFR - DTB3 ---
    a = base.copy()
    a["spread"] = a["sofr"] - a["dtb3"]
    a = a.dropna(subset=["spread", "spy"]).loc["2018-04-01":]
    variants["sofr_ted_spy"] = {
        "df": a, "label": "SOFR - DTB3",
        "start": "2018-04-01", "is_end": "2022-12-31", "oos_start": "2023-01-01",
    }
    print(f"  Variant A (SOFR-DTB3): {len(a)} obs, {a.index.min().date()} to {a.index.max().date()}")

    # --- Variant B: DFF - DTB3 ---
    b = base.copy()
    b["spread"] = b["dff"] - b["dtb3"]
    b = b.dropna(subset=["spread", "spy"])
    variants["dff_ted_spy"] = {
        "df": b, "label": "DFF - DTB3 (Fed Funds TED)",
        "start": "1993-01-01", "is_end": "2017-12-31", "oos_start": "2018-01-01",
    }
    print(f"  Variant B (DFF-DTB3):  {len(b)} obs, {b.index.min().date()} to {b.index.max().date()}")

    # --- Variant C: TEDRATE + adjusted DFF-TED splice ---
    c = base.copy()
    # Compute adjustment from overlap period
    overlap_mask = c["tedrate"].notna() & c["dff"].notna() & c["dtb3"].notna()
    c["dff_ted_raw"] = c["dff"] - c["dtb3"]
    overlap = c[overlap_mask]
    ted_mean = overlap["tedrate"].mean()
    ted_std = overlap["tedrate"].std()
    dff_mean = overlap["dff_ted_raw"].mean()
    dff_std = overlap["dff_ted_raw"].std()
    scale = ted_std / dff_std if dff_std > 0 else 1
    shift = ted_mean - dff_mean * scale
    c["dff_ted_adj"] = c["dff_ted_raw"] * scale + shift

    # Splice: TEDRATE where available, then adjusted DFF-TED
    cutover = "2022-01-21"
    c["spread"] = c["tedrate"].copy()
    c.loc[c.index > cutover, "spread"] = c.loc[c.index > cutover, "dff_ted_adj"]
    c = c.dropna(subset=["spread", "spy"])
    variants["ted_spliced_spy"] = {
        "df": c, "label": f"TEDRATE + adj DFF-TED (scale={scale:.3f}, shift={shift:.3f})",
        "start": "1993-01-01", "is_end": "2017-12-31", "oos_start": "2018-01-01",
    }
    print(f"  Variant C (Spliced):   {len(c)} obs, {c.index.min().date()} to {c.index.max().date()}")

    return variants


# =====================================================================
# GENERIC ANALYSIS FUNCTIONS
# =====================================================================

def compute_derived(df):
    """Add derived signals from the 'spread' column."""
    s = df["spread"]
    # Z-scores
    rm252 = s.rolling(252, min_periods=200)
    df["spread_zscore_252d"] = (s - rm252.mean()) / rm252.std()
    rm126 = s.rolling(126, min_periods=100)
    df["spread_zscore_126d"] = (s - rm126.mean()) / rm126.std()
    # Rate of change
    df["spread_roc_21d"] = (s / s.shift(21).replace(0, np.nan) - 1) * 100
    df["spread_roc_63d"] = (s / s.shift(63).replace(0, np.nan) - 1) * 100
    # Momentum
    df["spread_mom_21d"] = s - s.shift(21)
    df["spread_mom_63d"] = s - s.shift(63)
    # Percentile rank
    df["spread_pctrank_252d"] = s.rolling(252, min_periods=200).apply(
        lambda x: stats.rankdata(x)[-1] / len(x), raw=True)
    # Realized vol
    df["spread_vol_21d"] = s.diff().rolling(21, min_periods=15).std()
    # Stress dummy (top quartile)
    df["spread_stress"] = (df["spread_pctrank_252d"] > 0.75).astype(float)
    return df


def run_exploratory(df, explore_dir):
    """Correlations, CCF, regime stats."""
    signals = [c for c in df.columns if c.startswith("spread_") and "fwd" not in c]
    fwd_cols = [c for c in df.columns if c.startswith("spy_fwd_")]

    # Correlations
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
    corr_df.to_csv(os.path.join(explore_dir, "correlations.csv"), index=False)

    # Regime stats (quartiles of spread)
    regime_results = []
    if "spy_ret" in df.columns:
        valid = df[["spread", "spy_ret"]].dropna()
        if len(valid) > 100:
            quartiles = pd.qcut(valid["spread"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"])
            for q in ["Q1_low", "Q2", "Q3", "Q4_high"]:
                rets = valid.loc[quartiles == q, "spy_ret"]
                if len(rets) < 10:
                    continue
                ann_ret = rets.mean() * 252 * 100
                ann_vol = rets.std() * np.sqrt(252) * 100
                regime_results.append({
                    "regime": q, "n_days": len(rets),
                    "ann_return_pct": round(ann_ret, 2),
                    "ann_vol_pct": round(ann_vol, 2),
                    "sharpe": round(ann_ret / ann_vol, 3) if ann_vol > 0 else 0,
                })
    regime_df = pd.DataFrame(regime_results)
    regime_df.to_csv(os.path.join(explore_dir, "regime_descriptive_stats.csv"), index=False)

    sig_count = len(corr_df[corr_df["p_value"] < 0.05]) if len(corr_df) > 0 else 0
    print(f"    Correlations: {len(corr_df)} pairs ({sig_count} significant)")
    if len(regime_df) > 0:
        print(f"    Regime Sharpes: {dict(zip(regime_df['regime'], regime_df['sharpe']))}")
    return corr_df, regime_df


def run_core_models(df, models_dir):
    """Granger, OLS, local projections, quantile regression, change-points, RF."""
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    results = {}
    work = df.dropna(subset=["spread", "spy_ret"])

    # Granger causality
    gc_results = []
    try:
        gc_data = work[["spy_ret", "spread"]].dropna()
        if len(gc_data) > 50:
            gc = grangercausalitytests(gc_data[["spy_ret", "spread"]], maxlag=5, verbose=False)
            for lag, r in gc.items():
                gc_results.append({"direction": "Spread->SPY", "lag": lag,
                    "f_stat": round(r[0]["ssr_ftest"][0], 4), "p_value": round(r[0]["ssr_ftest"][1], 4)})
            gc_rev = grangercausalitytests(gc_data[["spread", "spy_ret"]], maxlag=5, verbose=False)
            for lag, r in gc_rev.items():
                gc_results.append({"direction": "SPY->Spread", "lag": lag,
                    "f_stat": round(r[0]["ssr_ftest"][0], 4), "p_value": round(r[0]["ssr_ftest"][1], 4)})
    except Exception as e:
        print(f"    Granger failed: {e}")
    pd.DataFrame(gc_results).to_csv(os.path.join(models_dir, "granger_causality.csv"), index=False)
    print(f"    Granger: {len(gc_results)} tests")

    # Predictive regressions
    reg_results = []
    for sig in ["spread", "spread_zscore_252d", "spread_mom_21d"]:
        for fwd in ["spy_fwd_5d", "spy_fwd_21d", "spy_fwd_63d"]:
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
    reg_df.to_csv(os.path.join(models_dir, "predictive_regressions.csv"), index=False)
    results["regressions"] = reg_df
    print(f"    Regressions: {len(reg_df)}")

    # Local projections
    lp_results = []
    for fwd, h in [("spy_fwd_5d", 5), ("spy_fwd_21d", 21), ("spy_fwd_63d", 63)]:
        if fwd not in work.columns:
            continue
        valid = work[["spread", fwd]].dropna()
        ctrls = [c for c in ["vix", "yield_10y3m"] if c in work.columns]
        for c in ctrls:
            valid[c] = work.loc[valid.index, c]
        valid = valid.dropna()
        if len(valid) < 50:
            continue
        try:
            X = sm.add_constant(valid[["spread"] + ctrls])
            nw = int(0.75 * len(valid) ** (1/3))
            model = sm.OLS(valid[fwd], X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = model.conf_int().loc["spread"]
            lp_results.append({"horizon_days": h,
                "coef": round(model.params["spread"], 6), "se": round(model.bse["spread"], 6),
                "t_stat": round(model.tvalues["spread"], 3), "p_value": round(model.pvalues["spread"], 4),
                "ci_lower": round(ci[0], 6), "ci_upper": round(ci[1], 6),
                "r_squared": round(model.rsquared, 4), "n": int(model.nobs)})
        except Exception:
            pass
    pd.DataFrame(lp_results).to_csv(os.path.join(models_dir, "local_projections.csv"), index=False)
    print(f"    Local projections: {len(lp_results)} horizons")

    # Quantile regression
    qr_results = []
    valid_qr = work[["spread", "spy_fwd_21d"]].dropna()
    if len(valid_qr) > 50:
        for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
            try:
                qr = smf.quantreg("spy_fwd_21d ~ spread", data=valid_qr).fit(q=tau)
                qr_results.append({"quantile": tau,
                    "coef": round(qr.params["spread"], 6), "p_value": round(qr.pvalues["spread"], 4),
                    "ci_lower": round(qr.conf_int().loc["spread", 0], 6),
                    "ci_upper": round(qr.conf_int().loc["spread", 1], 6)})
            except Exception:
                pass
    pd.DataFrame(qr_results).to_csv(os.path.join(models_dir, "quantile_regression.csv"), index=False)
    print(f"    Quantile regression: {len(qr_results)} quantiles")

    # Diagnostics on baseline
    diag_results = []
    valid_diag = work[["spread", "spy_fwd_21d"]].dropna()
    if len(valid_diag) > 50:
        X = sm.add_constant(valid_diag["spread"])
        model = sm.OLS(valid_diag["spy_fwd_21d"], X).fit()
        resid = model.resid
        jb_s, jb_p = stats.jarque_bera(resid)
        diag_results.append({"test": "Jarque-Bera", "statistic": round(jb_s, 4), "p_value": round(jb_p, 4)})
        from statsmodels.stats.stattools import durbin_watson
        dw = durbin_watson(resid)
        diag_results.append({"test": "Durbin-Watson", "statistic": round(dw, 4), "p_value": np.nan})
    pd.DataFrame(diag_results).to_csv(os.path.join(models_dir, "diagnostics_summary.csv"), index=False)

    return results


def run_tournament(df, is_end, oos_start, results_dir):
    """Combinatorial tournament backtest."""
    work = df.copy()
    is_mask = work.index <= is_end
    oos_mask = work.index >= oos_start

    if "spy_ret" not in work.columns:
        work["spy_ret"] = work["spy"].pct_change()

    signal_cols = {k: k for k in work.columns
                   if k.startswith("spread") and "fwd" not in k and "ret" not in k}
    signal_cols["spread_level"] = "spread"

    leads = [0, 1, 5, 10, 21]
    strategies = ["P1", "P2", "P3"]
    results = []

    for sig_name, sig_col in signal_cols.items():
        if sig_col not in work.columns:
            continue
        signal = work[sig_col]
        if signal.dropna().shape[0] < 100:
            continue

        for lead in leads:
            sig_l = signal.shift(lead) if lead > 0 else signal
            is_sig = sig_l[is_mask].dropna()
            if len(is_sig) < 50:
                continue

            thresholds = {}
            for pct in [25, 50, 75]:
                thresholds[f"T1_p{pct}"] = is_sig.quantile(pct / 100)
            for pct in [25, 50, 75]:
                thresholds[f"T2_rp{pct}"] = sig_l.rolling(252, min_periods=200).quantile(pct / 100)

            for tname, tval in thresholds.items():
                for strat in strategies:
                    try:
                        if isinstance(tval, (int, float)):
                            # Counter-cyclical: ABOVE threshold = stress = go to cash
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
                        else:
                            continue

                        strat_ret = pos.shift(1) * work["spy_ret"]
                        is_r = strat_ret[is_mask].dropna()
                        oos_r = strat_ret[oos_mask].dropna()

                        if len(is_r) < 50 or len(oos_r) < 30:
                            continue

                        oos_sharpe = (oos_r.mean() / oos_r.std()) * np.sqrt(252) if oos_r.std() > 0 else 0
                        cum = (1 + oos_r).cumprod()
                        dd = ((cum - cum.cummax()) / cum.cummax()).min()
                        turnover = pos.diff().abs().sum() / (len(pos.dropna()) / 252)
                        valid = oos_sharpe > 0 and turnover < 24 and len(oos_r) >= 30

                        results.append({
                            "signal": sig_name, "threshold": tname, "strategy": strat,
                            "lead_days": lead,
                            "oos_sharpe": round(oos_sharpe, 4),
                            "oos_ann_return": round(oos_r.mean() * 252 * 100, 2),
                            "max_drawdown": round(dd * 100, 2),
                            "annual_turnover": round(turnover, 2),
                            "oos_n": len(oos_r), "valid": valid,
                        })
                    except Exception:
                        continue

    # Benchmark
    bh = work.loc[oos_mask, "spy_ret"].dropna()
    if len(bh) > 0:
        bh_sharpe = (bh.mean() / bh.std()) * np.sqrt(252) if bh.std() > 0 else 0
        bh_cum = (1 + bh).cumprod()
        bh_dd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min()
        results.append({"signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BH",
            "lead_days": 0, "oos_sharpe": round(bh_sharpe, 4),
            "oos_ann_return": round(bh.mean() * 252 * 100, 2),
            "max_drawdown": round(bh_dd * 100, 2), "annual_turnover": 0,
            "oos_n": len(bh), "valid": True})

    rdf = pd.DataFrame(results)
    rdf.to_csv(os.path.join(results_dir, f"tournament_results_{DATE_TAG}.csv"), index=False)

    valid_count = rdf["valid"].sum() if len(rdf) > 0 else 0
    print(f"    Tournament: {len(rdf)} combos, {valid_count} valid")

    if len(rdf) > 0:
        vs = rdf[rdf["valid"] & (rdf["signal"] != "BENCHMARK")]
        if len(vs) > 0:
            best = vs.loc[vs["oos_sharpe"].idxmax()]
            print(f"    Best: {best['signal']}/{best['threshold']}/{best['strategy']}/L{best['lead_days']} "
                  f"Sharpe={best['oos_sharpe']:.2f} DD={best['max_drawdown']:.1f}%")
        bh_row = rdf[rdf["signal"] == "BENCHMARK"]
        if len(bh_row) > 0:
            print(f"    B&H:  Sharpe={bh_row.iloc[0]['oos_sharpe']:.2f} DD={bh_row.iloc[0]['max_drawdown']:.1f}%")

    return rdf


def save_interpretation(results_dir, variant_label, reg_df, direction_expected="counter_cyclical"):
    """Save interpretation metadata JSON."""
    interp = {
        "indicator": variant_label,
        "target": "spy",
        "expected_direction": direction_expected,
        "observed_direction": "unknown",
        "direction_consistent": True,
        "mechanism": "Wider funding spread indicates stress in interbank/repo markets, tightening financial conditions, reduced liquidity — bearish for equities.",
        "confidence": "medium",
        "key_finding": "",
        "caveats": []
    }

    if len(reg_df) > 0:
        best = reg_df.loc[reg_df["p_value"].idxmin()]
        interp["key_finding"] = (
            f"{best['signal']} predicts {best['horizon']} "
            f"(coef={best['coef']:.4f}, t={best['t_stat']:.2f}, p={best['p_value']:.4f})")
        if best["coef"] > 0:
            interp["observed_direction"] = "pro_cyclical"
            interp["direction_consistent"] = False
        else:
            interp["observed_direction"] = "counter_cyclical"

    with open(os.path.join(results_dir, "interpretation_metadata.json"), "w") as f:
        json.dump(interp, f, indent=2)


# =====================================================================
# MAIN
# =====================================================================

def main():
    t0 = time.time()
    print("="*60)
    print("  TED VARIANTS → SPY: 3-way comparison")
    print("="*60)

    series = source_all()
    variants = build_variants(series)

    all_results = {}

    for pair_id, vinfo in variants.items():
        df = vinfo["df"]
        label = vinfo["label"]
        is_end = vinfo["is_end"]
        oos_start = vinfo["oos_start"]

        results_dir = os.path.join(BASE_DIR, "results", pair_id)
        explore_dir = os.path.join(results_dir, f"exploratory_{DATE_TAG}")
        models_dir = os.path.join(results_dir, f"core_models_{DATE_TAG}")

        print(f"\n{'#'*60}")
        print(f"  VARIANT: {label}")
        print(f"  Pair ID: {pair_id}")
        print(f"  Obs: {len(df)}, IS: {vinfo['start']}–{is_end}, OOS: {oos_start}–")
        print(f"{'#'*60}")

        # Derived signals
        df = compute_derived(df)

        # Stationarity (quick)
        from arch.unitroot import ADF
        for col in ["spread", "spy"]:
            if col in df.columns:
                s = df[col].dropna()
                if len(s) > 100:
                    if len(s) > 5000:
                        s = s.iloc[::5]
                    try:
                        adf = ADF(s, max_lags=12)
                        print(f"  ADF {col}: stat={adf.stat:.3f}, p={adf.pvalue:.4f} "
                              f"({'Stationary' if adf.pvalue < 0.05 else 'Non-stationary'})")
                    except Exception:
                        pass

        # Exploratory
        corr_df, regime_df = run_exploratory(df, explore_dir)

        # Core models
        model_results = run_core_models(df, models_dir)

        # Interpretation metadata
        reg_df = model_results.get("regressions", pd.DataFrame())
        save_interpretation(results_dir, pair_id, reg_df)

        # Tournament
        tourn_df = run_tournament(df, is_end, oos_start, results_dir)

        # Save dataset
        ds_path = os.path.join(DATA_DIR, f"{pair_id}_daily_{DATE_TAG}.parquet")
        df.to_parquet(ds_path, engine="pyarrow")

        all_results[pair_id] = {
            "label": label, "obs": len(df),
            "tournament_combos": len(tourn_df),
            "valid": int(tourn_df["valid"].sum()) if len(tourn_df) > 0 else 0,
        }

    # Summary
    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  ALL 3 VARIANTS COMPLETE — {elapsed:.1f}s total")
    print(f"{'='*60}")

    for pid, info in all_results.items():
        print(f"  {pid:20s}: {info['obs']:,} obs, {info['valid']}/{info['tournament_combos']} valid")

    # Save timing
    timing = {
        "date": DATE_TAG, "total_seconds": round(elapsed, 1),
        "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
        "variants": all_results,
    }
    with open(os.path.join(BASE_DIR, "results", f"ted_variants_timing_{DATE_TAG}.json"), "w") as f:
        json.dump(timing, f, indent=2)

    return all_results


if __name__ == "__main__":
    main()
