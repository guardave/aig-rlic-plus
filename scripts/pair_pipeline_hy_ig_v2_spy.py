#!/usr/bin/env python3
"""
Full Analysis Pipeline: HY-IG Credit Spread → S&P 500 (SPY)
=============================================================
Pair #5 v2 (re-run with updated SOPs and self-contained pipeline).
HY-IG OAS spread widens when credit stress rises → bearish equities.

Date: 2026-04-10
"""

import os, sys, json, warnings, time, itertools
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

PAIR_ID = "hy_ig_v2_spy"
INDICATOR_NAME = "HY-IG Credit Spread"
TARGET_NAME = "S&P 500"
START_DATE = "2000-01-01"
END_DATE = "2025-12-31"
IS_END = "2017-12-31"
OOS_START = "2018-01-01"
DATE_TAG = "20260410"

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")

SIGNALS_DIR = RESULTS_DIR
VALIDATION_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")

for d in [DATA_DIR, RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALIDATION_DIR]:
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


# ─────────────────────────────────────────────────────────────
# STAGE 1: DATA SOURCING
# ─────────────────────────────────────────────────────────────

@timed("1_data")
def stage_data():
    """Source all 23 series from FRED (13) and Yahoo Finance (10)."""
    import yfinance as yf
    from fredapi import Fred

    api_key = os.environ.get("FRED_API_KEY") or "952aa4d0c4b2057609fbf3ecc6954e58"
    fred = Fred(api_key=api_key)

    series = {}

    # --- FRED series (13) ---
    fred_map = [
        ("BAMLH0A0HYM2", "hy_oas"),
        ("BAMLC0A0CM",    "ig_oas"),
        ("BAMLH0A1HYBB",  "bb_hy_oas"),
        ("BAMLH0A3HYC",   "ccc_hy_oas"),
        ("DGS10",         "dgs10"),
        ("DTB3",          "dtb3"),
        ("DGS2",          "dgs2"),
        ("NFCI",          "nfci"),
        ("DFF",           "fed_funds_rate"),
        ("BAMLC0A4CBBB",  "bbb_oas"),
        ("STLFSI4",       "fsi"),
        ("ICSA",          "initial_claims"),
        ("SOFR",          "sofr"),
    ]
    for sid, name in fred_map:
        for attempt in range(3):
            try:
                s = fred.get_series(sid, observation_start=START_DATE, observation_end=END_DATE)
                series[name] = s.astype(float)
                v = s.dropna()
                print(f"  [FRED] {sid:20s} -> {name:20s}: {len(v)} obs  ({v.index.min().date()} to {v.index.max().date()})")
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(1)
                else:
                    print(f"  [FRED] {sid} FAILED after 3 attempts: {e}")

    # --- Yahoo Finance tickers (10) ---
    yf_map = [
        ("SPY",       "spy"),
        ("^VIX",      "vix"),
        ("^VIX3M",    "vix3m"),
        ("KBE",       "kbe"),
        ("IWM",       "iwm"),
        ("^MOVE",     "move_index"),
        ("GC=F",      "gold"),
        ("HG=F",      "copper"),
        ("DX-Y.NYB",  "dxy"),
        ("HYG",       "hyg"),
    ]
    for ticker, name in yf_map:
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            s = df["Close"]
            s.index = s.index.tz_localize(None) if s.index.tz else s.index
            series[name] = s.astype(float)
            print(f"  [YF]   {ticker:10s} -> {name:15s}: {len(s)} obs  ({s.index.min().date()} to {s.index.max().date()})")
        except Exception as e:
            print(f"  [YF]   {ticker} FAILED: {e}")

    print(f"\n  Total series sourced: {len(series)}")
    return series


# ─────────────────────────────────────────────────────────────
# STAGE 2: DERIVED SIGNALS
# ─────────────────────────────────────────────────────────────

@timed("2_derived")
def stage_derived(series):
    """Build master DataFrame with all derived signals and forward returns."""
    bdays = pd.bdate_range(START_DATE, END_DATE)
    df = pd.DataFrame(index=bdays)
    df.index.name = "date"

    # Align all raw series to business-day calendar
    # Daily series: ffill(limit=5). Weekly series (NFCI, FSI, ICSA): ffill(limit=10)
    weekly_cols = {"nfci", "fsi", "initial_claims"}
    all_cols = [
        "hy_oas", "ig_oas", "bb_hy_oas", "ccc_hy_oas",
        "dgs10", "dtb3", "dgs2", "nfci", "fed_funds_rate",
        "bbb_oas", "fsi", "initial_claims", "sofr",
        "spy", "vix", "vix3m", "kbe", "iwm",
        "move_index", "gold", "copper", "dxy", "hyg",
    ]
    for col in all_cols:
        if col in series:
            s = series[col]
            limit = 10 if col in weekly_cols else 5
            if col in weekly_cols:
                # Weekly series may have weekend dates (e.g. ICSA on Saturdays).
                # Shift weekend dates to the preceding Friday so they align with bdays.
                new_idx = s.index.map(
                    lambda d: d - pd.tseries.offsets.BDay(0) if d.weekday() < 5
                    else d - pd.Timedelta(days=d.weekday() - 4)
                )
                s = s.copy()
                s.index = new_idx
                s = s[~s.index.duplicated(keep="last")]
            df[col] = s.reindex(bdays).ffill(limit=limit)

    # ── Core indicator: HY-IG spread (bps) ──
    df["hy_ig_spread"] = df["hy_oas"] - df["ig_oas"]

    spread = df["hy_ig_spread"]

    # ── Z-scores ──
    df["hy_ig_zscore_252d"] = (
        (spread - spread.rolling(252, min_periods=200).mean())
        / spread.rolling(252, min_periods=200).std()
    )
    df["hy_ig_zscore_504d"] = (
        (spread - spread.rolling(504, min_periods=400).mean())
        / spread.rolling(504, min_periods=400).std()
    )

    # ── Percentile ranks ──
    df["hy_ig_pctrank_504d"] = spread.rolling(504, min_periods=400).apply(
        lambda x: stats.rankdata(x)[-1] / len(x), raw=True
    )
    df["hy_ig_pctrank_1260d"] = spread.rolling(1260, min_periods=1000).apply(
        lambda x: stats.rankdata(x)[-1] / len(x), raw=True
    )

    # ── Rates of change (%) ──
    df["hy_ig_roc_21d"] = (spread / spread.shift(21) - 1) * 100
    df["hy_ig_roc_63d"] = (spread / spread.shift(63) - 1) * 100
    df["hy_ig_roc_126d"] = (spread / spread.shift(126) - 1) * 100

    # ── Momentum (absolute) ──
    df["hy_ig_mom_21d"] = spread - spread.shift(21)
    df["hy_ig_mom_63d"] = spread - spread.shift(63)
    df["hy_ig_mom_252d"] = spread - spread.shift(252)

    # ── Acceleration ──
    df["hy_ig_acceleration"] = df["hy_ig_roc_21d"] - df["hy_ig_roc_21d"].shift(21)

    # ── Quality spread: CCC - BB ──
    if "ccc_hy_oas" in df.columns and "bb_hy_oas" in df.columns:
        df["ccc_bb_spread"] = df["ccc_hy_oas"] - df["bb_hy_oas"]
    else:
        print("  SKIP ccc_bb_spread: missing inputs")

    # ── Realized volatility of spread changes ──
    df["hy_ig_realized_vol_21d"] = spread.diff().rolling(21, min_periods=15).std()

    # ── Cross-market signals (guarded for missing columns) ──
    def _safe_sub(a, b, name):
        if a in df.columns and b in df.columns:
            df[name] = df[a] - df[b]
        else:
            print(f"  SKIP {name}: missing {a if a not in df.columns else b}")

    def _safe_div(a, b, name):
        if a in df.columns and b in df.columns:
            df[name] = df[a] / df[b]
        else:
            print(f"  SKIP {name}: missing {a if a not in df.columns else b}")

    _safe_sub("vix3m", "vix", "vix_term_structure")
    _safe_sub("dgs10", "dtb3", "yield_spread_10y3m")
    _safe_sub("dgs10", "dgs2", "yield_spread_10y2y")
    _safe_div("kbe", "iwm", "bank_smallcap_ratio")
    if "nfci" in df.columns:
        df["nfci_momentum_13w"] = df["nfci"] - df["nfci"].shift(65)
    else:
        print("  SKIP nfci_momentum_13w: missing nfci")
    _safe_sub("bbb_oas", "ig_oas", "bbb_ig_spread")

    # ── Forward SPY returns (6 horizons) ──
    spy = df["spy"]
    df["spy_ret"] = spy.pct_change()
    df["spy_fwd_1d"] = spy.pct_change(1).shift(-1)
    df["spy_fwd_5d"] = spy.shift(-5) / spy - 1
    df["spy_fwd_21d"] = spy.shift(-21) / spy - 1
    df["spy_fwd_63d"] = spy.shift(-63) / spy - 1
    df["spy_fwd_126d"] = spy.shift(-126) / spy - 1
    df["spy_fwd_252d"] = spy.shift(-252) / spy - 1

    # ── Drop rows missing core variables ──
    df = df.dropna(subset=["hy_ig_spread", "spy"])

    # ── Summary ──
    n_derived = len([c for c in df.columns if c.startswith("hy_ig_") or c in [
        "ccc_bb_spread", "vix_term_structure", "yield_spread_10y3m",
        "yield_spread_10y2y", "bank_smallcap_ratio", "nfci_momentum_13w", "bbb_ig_spread"
    ]])
    n_fwd = len([c for c in df.columns if c.startswith("spy_fwd_")])
    print(f"  Dataset: {df.shape[0]} rows x {df.shape[1]} cols")
    print(f"  Date range: {df.index.min().date()} to {df.index.max().date()}")
    print(f"  Derived signals: {n_derived}, Forward returns: {n_fwd}")
    print(f"  IS period: {START_DATE} to {IS_END}")
    print(f"  OOS period: {OOS_START} to {END_DATE}")

    # Missing-value summary for key columns
    key_cols = ["hy_ig_spread", "hy_ig_zscore_252d", "hy_ig_roc_21d", "spy", "vix"]
    for c in key_cols:
        if c in df.columns:
            pct_missing = df[c].isna().mean() * 100
            print(f"  Missing: {c:30s} {pct_missing:.1f}%")

    return df


# ─────────────────────────────────────────────────────────────
# STAGE 3: STATIONARITY TESTS
# ─────────────────────────────────────────────────────────────

@timed("3_stationarity")
def stage_stationarity(df):
    """Run ADF tests on key variables."""
    from arch.unitroot import ADF

    test_vars = [
        "hy_ig_spread", "hy_ig_zscore_252d", "hy_ig_roc_21d", "hy_ig_roc_63d",
        "hy_ig_mom_21d", "hy_ig_acceleration", "ccc_bb_spread",
        "hy_ig_realized_vol_21d", "vix_term_structure",
        "yield_spread_10y3m", "yield_spread_10y2y",
        "nfci_momentum_13w", "bbb_ig_spread",
        "spy", "spy_ret",
    ]
    results = []
    for col in test_vars:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if len(s) < 100:
            continue
        # Subsample very long series for efficiency
        if len(s) > 5000:
            s = s.iloc[::5]
        try:
            adf = ADF(s, max_lags=12)
            conclusion = "Stationary" if adf.pvalue < 0.05 else "Non-stationary"
            results.append({
                "variable": col,
                "test": "ADF",
                "statistic": round(adf.stat, 4),
                "p_value": round(adf.pvalue, 4),
                "lags": adf.lags,
                "n_obs": len(s),
                "conclusion": conclusion,
            })
            print(f"  ADF {col:35s}: stat={adf.stat:8.3f}, p={adf.pvalue:.4f} -> {conclusion}")
        except Exception as e:
            print(f"  ADF {col} FAILED: {e}")

    results_df = pd.DataFrame(results)
    out_path = os.path.join(RESULTS_DIR, f"stationarity_tests_{DATE_TAG}.csv")
    results_df.to_csv(out_path, index=False)
    print(f"\n  Saved: {out_path}")
    return results_df


# ─────────────────────────────────────────────────────────────
# STAGE 4: EXPLORATORY ANALYSIS
# ─────────────────────────────────────────────────────────────

@timed("4_exploratory")
def stage_exploratory(df):
    """Correlations and regime descriptive statistics."""
    # ── Correlations: signal columns × forward horizons ──
    signal_cols = [c for c in df.columns
                   if (c.startswith("hy_ig_") or c in [
                       "ccc_bb_spread", "vix_term_structure", "yield_spread_10y3m",
                       "yield_spread_10y2y", "bank_smallcap_ratio", "nfci_momentum_13w",
                       "bbb_ig_spread", "hy_ig_realized_vol_21d"])
                   and "fwd" not in c and "ret" not in c]
    fwd_cols = [c for c in df.columns if c.startswith("spy_fwd_")]

    corr_results = []
    for sig in signal_cols:
        for fwd in fwd_cols:
            valid = df[[sig, fwd]].dropna()
            if len(valid) < 50:
                continue
            r, p = stats.pearsonr(valid[sig], valid[fwd])
            corr_results.append({
                "signal": sig, "horizon": fwd, "method": "Pearson",
                "correlation": round(r, 4), "p_value": round(p, 4), "n": len(valid)
            })
    corr_df = pd.DataFrame(corr_results)
    corr_df.to_csv(os.path.join(EXPLORE_DIR, "correlations.csv"), index=False)

    # ── Regime descriptive stats: quartiles of hy_ig_spread ──
    regime_results = []
    valid = df[["hy_ig_spread", "spy_ret"]].dropna()
    if len(valid) > 200:
        quartiles = pd.qcut(valid["hy_ig_spread"], 4,
                            labels=["Q1_low", "Q2", "Q3", "Q4_high"])
        for q in ["Q1_low", "Q2", "Q3", "Q4_high"]:
            rets = valid.loc[quartiles == q, "spy_ret"]
            if len(rets) < 20:
                continue
            ann_ret = rets.mean() * 252 * 100
            ann_vol = rets.std() * np.sqrt(252) * 100
            regime_results.append({
                "regime": q, "n_days": len(rets),
                "ann_return_pct": round(ann_ret, 2),
                "ann_vol_pct": round(ann_vol, 2),
                "sharpe": round(ann_ret / ann_vol, 3) if ann_vol > 0 else 0,
            })
    pd.DataFrame(regime_results).to_csv(
        os.path.join(EXPLORE_DIR, "regime_descriptive_stats.csv"), index=False)

    sig_count = len(corr_df[corr_df["p_value"] < 0.05]) if len(corr_df) > 0 else 0
    print(f"  Correlations: {len(corr_df)} ({sig_count} significant at 5%)")
    if regime_results:
        print(f"  Regime Sharpes: {dict(zip([r['regime'] for r in regime_results], [r['sharpe'] for r in regime_results]))}")
    return corr_df


# ─────────────────────────────────────────────────────────────
# STAGE 5: CORE MODELS
# ─────────────────────────────────────────────────────────────

@timed("5_models")
def stage_models(df):
    """Granger, predictive regressions, local projections, quantile reg,
    HMM, Markov-switching, diagnostics. Persists HMM/MS signals."""
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    work = df.dropna(subset=["hy_ig_spread", "spy_ret"]).copy()

    # ── 1. Granger Causality ──
    gc_results = []
    try:
        gc_data = work[["spy_ret", "hy_ig_spread"]].dropna()
        if len(gc_data) > 100:
            gc = grangercausalitytests(gc_data[["spy_ret", "hy_ig_spread"]], maxlag=5, verbose=False)
            for lag, r in gc.items():
                gc_results.append({
                    "direction": "HY_IG_Spread->SPY", "lag": lag,
                    "f_stat": round(r[0]["ssr_ftest"][0], 4),
                    "p_value": round(r[0]["ssr_ftest"][1], 4),
                })
            gc_rev = grangercausalitytests(gc_data[["hy_ig_spread", "spy_ret"]], maxlag=5, verbose=False)
            for lag, r in gc_rev.items():
                gc_results.append({
                    "direction": "SPY->HY_IG_Spread", "lag": lag,
                    "f_stat": round(r[0]["ssr_ftest"][0], 4),
                    "p_value": round(r[0]["ssr_ftest"][1], 4),
                })
    except Exception as e:
        print(f"  Granger failed: {e}")
    pd.DataFrame(gc_results).to_csv(os.path.join(MODELS_DIR, "granger_causality.csv"), index=False)
    print(f"  Granger: {len(gc_results)} tests")

    # ── 2. Predictive Regressions ──
    reg_results = []
    reg_signals = [
        "hy_ig_spread", "hy_ig_zscore_252d", "hy_ig_zscore_504d",
        "hy_ig_pctrank_504d", "hy_ig_pctrank_1260d",
        "hy_ig_roc_21d", "hy_ig_roc_63d", "hy_ig_roc_126d",
        "hy_ig_mom_21d", "hy_ig_mom_63d", "hy_ig_acceleration",
        "ccc_bb_spread",
    ]
    reg_horizons = ["spy_fwd_1d", "spy_fwd_5d", "spy_fwd_21d", "spy_fwd_63d", "spy_fwd_126d"]
    for sig in reg_signals:
        for fwd in reg_horizons:
            if sig not in work.columns or fwd not in work.columns:
                continue
            valid = work[[sig, fwd]].dropna()
            if len(valid) < 50:
                continue
            try:
                X = sm.add_constant(valid[sig])
                model = sm.OLS(valid[fwd], X).fit(cov_type="HC3")
                reg_results.append({
                    "signal": sig, "horizon": fwd,
                    "coef": round(model.params.iloc[1], 6),
                    "t_stat": round(model.tvalues.iloc[1], 3),
                    "p_value": round(model.pvalues.iloc[1], 4),
                    "r_squared": round(model.rsquared, 4),
                    "n": int(model.nobs),
                })
            except Exception:
                pass
    reg_df = pd.DataFrame(reg_results)
    reg_df.to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    print(f"  Regressions: {len(reg_df)}")

    # ── 3. Local Projections (Jordà) ──
    lp_results = []
    for fwd, h in [("spy_fwd_5d", 5), ("spy_fwd_21d", 21), ("spy_fwd_63d", 63)]:
        if fwd not in work.columns:
            continue
        valid = work[["hy_ig_spread", fwd]].dropna()
        ctrls = [c for c in ["vix", "yield_spread_10y3m"] if c in work.columns]
        for c in ctrls:
            valid[c] = work.loc[valid.index, c]
        valid = valid.dropna()
        if len(valid) < 100:
            continue
        try:
            X = sm.add_constant(valid[["hy_ig_spread"] + ctrls])
            nw = int(0.75 * len(valid) ** (1 / 3))
            model = sm.OLS(valid[fwd], X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = model.conf_int().loc["hy_ig_spread"]
            lp_results.append({
                "horizon_days": h,
                "coef": round(model.params["hy_ig_spread"], 6),
                "se": round(model.bse["hy_ig_spread"], 6),
                "t_stat": round(model.tvalues["hy_ig_spread"], 3),
                "p_value": round(model.pvalues["hy_ig_spread"], 4),
                "ci_lower": round(ci[0], 6), "ci_upper": round(ci[1], 6),
                "r_squared": round(model.rsquared, 4), "n": int(model.nobs),
            })
        except Exception:
            pass
    pd.DataFrame(lp_results).to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    print(f"  Local projections: {len(lp_results)} horizons")

    # ── 4. Quantile Regression ──
    qr_results = []
    valid_qr = work[["hy_ig_spread", "spy_fwd_21d"]].dropna()
    if len(valid_qr) > 50:
        for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
            try:
                qr = smf.quantreg("spy_fwd_21d ~ hy_ig_spread", data=valid_qr).fit(q=tau)
                qr_results.append({
                    "quantile": tau,
                    "coef": round(qr.params["hy_ig_spread"], 6),
                    "p_value": round(qr.pvalues["hy_ig_spread"], 4),
                    "ci_lower": round(qr.conf_int().loc["hy_ig_spread", 0], 6),
                    "ci_upper": round(qr.conf_int().loc["hy_ig_spread", 1], 6),
                })
            except Exception:
                pass
    pd.DataFrame(qr_results).to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    print(f"  Quantile reg: {len(qr_results)} quantiles")

    # ── 5. HMM Regime Detection (2-state) ──
    hmm_probs = pd.Series(np.nan, index=df.index, name="hmm_2state_prob_stress")
    try:
        from hmmlearn.hmm import GaussianHMM

        hmm_features = []
        for c in ["hy_ig_spread", "vix"]:
            if c in work.columns:
                hmm_features.append(c)
        hmm_data = work[hmm_features].dropna()
        # Compute spread_change for HMM input
        spread_change = work["hy_ig_spread"].diff()
        hmm_data = hmm_data.copy()
        hmm_data["spread_change"] = spread_change.reindex(hmm_data.index)
        hmm_data = hmm_data.dropna()

        X_hmm = hmm_data[["spread_change", "vix"]].values
        # Standardize for numerical stability
        X_mean = X_hmm.mean(axis=0)
        X_std = X_hmm.std(axis=0)
        X_std[X_std == 0] = 1
        X_hmm_scaled = (X_hmm - X_mean) / X_std

        model_hmm = GaussianHMM(n_components=2, covariance_type="full",
                                n_iter=200, random_state=42)
        model_hmm.fit(X_hmm_scaled)
        probs = model_hmm.predict_proba(X_hmm_scaled)

        # Identify stress state: higher mean spread_change = stress
        means = model_hmm.means_[:, 0]  # spread_change dimension
        stress_state = int(np.argmax(means))
        calm_state = 1 - stress_state

        hmm_stress = pd.Series(probs[:, stress_state], index=hmm_data.index,
                               name="hmm_2state_prob_stress")
        hmm_calm = pd.Series(probs[:, calm_state], index=hmm_data.index,
                             name="hmm_2state_prob_calm")

        hmm_probs = hmm_stress.reindex(df.index)

        # Save HMM states parquet (for enrichment by generate_winner_outputs)
        hmm_states_df = pd.DataFrame({
            "prob_state_0": probs[:, stress_state],
            "prob_state_1": probs[:, calm_state],
            "state": model_hmm.predict(X_hmm_scaled),
        }, index=hmm_data.index)
        hmm_states_df.to_parquet(os.path.join(MODELS_DIR, "hmm_states_2state.parquet"))

        print(f"  HMM 2-state: stress_state={stress_state}, "
              f"mean stress prob={hmm_stress.mean():.3f}")
    except Exception as e:
        print(f"  HMM FAILED: {e}")

    # ── 6. Markov-Switching Regression ──
    ms_probs = pd.Series(np.nan, index=df.index, name="ms_2state_stress_prob")
    try:
        from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

        ms_data = work[["spy_ret", "hy_ig_spread"]].dropna()
        # Subsample if too large for speed
        if len(ms_data) > 3000:
            ms_sample = ms_data.iloc[::2]
        else:
            ms_sample = ms_data

        ms_model = MarkovRegression(
            ms_sample["spy_ret"], k_regimes=2,
            exog=sm.add_constant(ms_sample["hy_ig_spread"]),
            switching_variance=True,
        )
        ms_fit = ms_model.fit(maxiter=200, disp=False)

        # Identify stress regime: higher variance = stress
        variances = [ms_fit.params[f"sigma2[{i}]"] for i in range(2)]
        stress_regime = int(np.argmax(variances))

        ms_stress = pd.Series(
            ms_fit.smoothed_marginal_probabilities[stress_regime].values,
            index=ms_sample.index, name="ms_2state_stress_prob"
        )
        ms_probs = ms_stress.reindex(df.index)

        print(f"  MS 2-state: stress_regime={stress_regime}, "
              f"stress_frac={ms_stress.mean():.3f}")
    except Exception as e:
        print(f"  Markov-Switching FAILED: {e}")

    # ── DERIVED SIGNAL PERSISTENCE: Save signals parquet ──
    signals_df = df[[]].copy()  # empty with df index
    # Core derived signals
    for col in ["hy_ig_spread", "hy_ig_zscore_252d", "hy_ig_zscore_504d",
                "hy_ig_pctrank_504d", "hy_ig_pctrank_1260d",
                "hy_ig_roc_21d", "hy_ig_roc_63d", "hy_ig_roc_126d",
                "hy_ig_mom_21d", "hy_ig_mom_63d", "hy_ig_mom_252d",
                "hy_ig_acceleration", "ccc_bb_spread"]:
        if col in df.columns:
            signals_df[col] = df[col]
    # HMM and MS probabilities
    signals_df["hmm_2state_prob_stress"] = hmm_probs
    signals_df["hmm_2state_prob_calm"] = 1.0 - hmm_probs
    signals_df["ms_2state_stress_prob"] = ms_probs
    signals_path = os.path.join(SIGNALS_DIR, f"signals_{DATE_TAG}.parquet")
    signals_df.to_parquet(signals_path)
    print(f"  Signals parquet saved: {signals_path} ({signals_df.shape})")

    # ── 7. Diagnostics ──
    diag_results = []
    valid_diag = work[["hy_ig_spread", "spy_fwd_21d"]].dropna()
    if len(valid_diag) > 50:
        X = sm.add_constant(valid_diag["hy_ig_spread"])
        model = sm.OLS(valid_diag["spy_fwd_21d"], X).fit()
        jb_s, jb_p = stats.jarque_bera(model.resid)
        diag_results.append({"test": "Jarque-Bera", "statistic": round(jb_s, 4),
                             "p_value": round(jb_p, 4)})
        from statsmodels.stats.stattools import durbin_watson
        dw = durbin_watson(model.resid)
        diag_results.append({"test": "Durbin-Watson", "statistic": round(dw, 4),
                             "p_value": np.nan})
    pd.DataFrame(diag_results).to_csv(
        os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)

    # ── Interpretation metadata ──
    interp = {
        "indicator": "hy_ig_spread",
        "target": "spy",
        "expected_direction": "counter_cyclical",
        "observed_direction": "unknown",
        "direction_consistent": True,
        "mechanism": "Wider HY-IG credit spreads signal rising default risk and tightening "
                     "financial conditions — bearish for equities. Spread compression is bullish.",
        "confidence": "high",
        "key_finding": "",
        "caveats": [
            "OAS data starts 1997; pre-2000 coverage is thin",
            "GFC 2008-2009 dominates the tails",
            "COVID March 2020 was an extreme but transient widening",
            "Regime-model signals (HMM, MS) are fitted in-sample; use persisted probabilities only",
        ],
    }
    if len(reg_df) > 0:
        best = reg_df.loc[reg_df["p_value"].idxmin()]
        interp["key_finding"] = (
            f"{best['signal']} predicts {best['horizon']} "
            f"(coef={best['coef']:.4f}, t={best['t_stat']:.2f}, p={best['p_value']:.4f})")
        interp["observed_direction"] = "counter_cyclical" if best["coef"] < 0 else "pro_cyclical"
        interp["direction_consistent"] = bool(best["coef"] < 0)
    with open(os.path.join(RESULTS_DIR, "interpretation_metadata.json"), "w") as f:
        json.dump(interp, f, indent=2)

    return reg_df, hmm_probs, ms_probs


# ─────────────────────────────────────────────────────────────
# STAGE 6: TOURNAMENT
# ─────────────────────────────────────────────────────────────

@timed("6_tournament")
def stage_tournament(df):
    """5D combinatorial backtest over signals, thresholds, strategies, leads, direction."""
    # Load persisted signals (Derived Signal Persistence Rule)
    signals_path = os.path.join(SIGNALS_DIR, f"signals_{DATE_TAG}.parquet")
    sig_df = pd.read_parquet(signals_path)
    # Merge HMM/MS columns into work frame
    work = df.copy()
    for col in ["hmm_2state_prob_stress", "ms_2state_stress_prob"]:
        if col in sig_df.columns and col not in work.columns:
            work[col] = sig_df[col].reindex(work.index)

    is_mask = work.index <= IS_END
    oos_mask = work.index >= OOS_START

    if "spy_ret" not in work.columns:
        work["spy_ret"] = work["spy"].pct_change()

    # ── Signal map (13 signals) ──
    signal_cols = {
        "S1_spread_level":     "hy_ig_spread",
        "S2a_zscore_252d":     "hy_ig_zscore_252d",
        "S2b_zscore_504d":     "hy_ig_zscore_504d",
        "S3a_pctrank_504d":    "hy_ig_pctrank_504d",
        "S3b_pctrank_1260d":   "hy_ig_pctrank_1260d",
        "S4a_roc_21d":         "hy_ig_roc_21d",
        "S4b_roc_63d":         "hy_ig_roc_63d",
        "S4c_roc_126d":        "hy_ig_roc_126d",
        "S5_ccc_bb_spread":    "ccc_bb_spread",
        "S6_hmm_stress":       "hmm_2state_prob_stress",
        "S7_ms_stress":        "ms_2state_stress_prob",
        "S10_mom_21d":         "hy_ig_mom_21d",
        "S11_mom_63d":         "hy_ig_mom_63d",
        "S12_mom_252d":        "hy_ig_mom_252d",
        "S13_acceleration":    "hy_ig_acceleration",
    }
    available = {k: v for k, v in signal_cols.items()
                 if v in work.columns and work[v].notna().sum() > 200}
    print(f"  Available signals: {len(available)} of {len(signal_cols)}")

    leads = [0, 1, 5, 10, 21, 63]
    results = []

    for sig_name, sig_col in available.items():
        signal = work[sig_col]
        for lead in leads:
            sig_l = signal.shift(lead) if lead > 0 else signal
            is_sig = sig_l[is_mask].dropna()
            if len(is_sig) < 100:
                continue

            # Build threshold dictionary based on signal type
            thresholds = {}

            if sig_name in ("S6_hmm_stress", "S7_ms_stress"):
                # Probability-based thresholds only
                for p in [0.5, 0.7]:
                    tkey = "T4" if sig_name == "S6_hmm_stress" else "T5"
                    thresholds[f"{tkey}_hmm_{p}" if "hmm" in sig_name else f"{tkey}_ms_{p}"] = p
            else:
                # T1: Fixed percentile
                for pct in [75, 85, 95]:
                    thresholds[f"T1_p{pct}"] = is_sig.quantile(pct / 100)
                # T2: Rolling 504d percentile
                for pct in [75, 85, 95]:
                    thresholds[f"T2_rp{pct}"] = sig_l.rolling(504, min_periods=400).quantile(pct / 100)
                # T3: Rolling z-score thresholds
                for z in [1.5, 2.0, 2.5]:
                    thresholds[f"T3_z{z}"] = z

            for tname, tval in thresholds.items():
                for strat in ["P1", "P2", "P3"]:
                    try:
                        # Counter-cyclical: HIGH signal = stressed = bearish → go to cash
                        # So bullish = signal BELOW threshold
                        if tname.startswith("T3_z"):
                            # Z-score comparison: need z-score of the signal
                            roll_mean = sig_l.rolling(504, min_periods=400).mean()
                            roll_std = sig_l.rolling(504, min_periods=400).std()
                            roll_std = roll_std.replace(0, np.nan)
                            z_series = (sig_l - roll_mean) / roll_std
                            bullish = z_series < tval
                        elif isinstance(tval, (int, float)):
                            bullish = sig_l < tval
                        else:
                            bullish = sig_l < tval

                        if strat == "P1":
                            pos = bullish.astype(float)
                        elif strat == "P2":
                            smin = sig_l.rolling(504, min_periods=400).min()
                            smax = sig_l.rolling(504, min_periods=400).max()
                            sr = (smax - smin).replace(0, np.nan)
                            pos = (1 - (sig_l - smin) / sr).clip(0, 1)
                        elif strat == "P3":
                            pos = bullish.astype(float) * 2 - 1

                        strat_ret = pos.shift(1) * work["spy_ret"]
                        is_r = strat_ret[is_mask].dropna()
                        oos_r = strat_ret[oos_mask].dropna()
                        if len(is_r) < 100 or len(oos_r) < 50:
                            continue

                        oos_sharpe = ((oos_r.mean() / oos_r.std()) * np.sqrt(252)
                                      if oos_r.std() > 0 else 0)
                        cum = (1 + oos_r).cumprod()
                        dd = ((cum - cum.cummax()) / cum.cummax()).min()
                        turnover = pos.diff().abs().sum() / max(len(pos.dropna()) / 252, 1)
                        n_trades_raw = pos.diff().abs().gt(0).sum()
                        valid = (oos_sharpe > 0 and turnover < 24
                                 and n_trades_raw >= 30)

                        # Win rate
                        wins = (oos_r > 0).sum()
                        win_rate = wins / len(oos_r) if len(oos_r) > 0 else 0

                        results.append({
                            "signal": sig_name,
                            "threshold": tname,
                            "strategy": strat,
                            "lead_days": lead,
                            "oos_sharpe": round(oos_sharpe, 4),
                            "oos_ann_return": round(oos_r.mean() * 252 * 100, 2),
                            "max_drawdown": round(dd * 100, 2),
                            "win_rate": round(win_rate, 4),
                            "n_trades": int(n_trades_raw),
                            "annual_turnover": round(turnover, 2),
                            "valid": valid,
                            "oos_n": len(oos_r),
                        })
                    except Exception:
                        continue

    # ── Benchmark (buy-and-hold SPY) ──
    bh = work.loc[oos_mask, "spy_ret"].dropna()
    if len(bh) > 0:
        bh_s = (bh.mean() / bh.std()) * np.sqrt(252) if bh.std() > 0 else 0
        bh_cum = (1 + bh).cumprod()
        bh_dd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min()
        results.append({
            "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BH",
            "lead_days": 0, "oos_sharpe": round(bh_s, 4),
            "oos_ann_return": round(bh.mean() * 252 * 100, 2),
            "max_drawdown": round(bh_dd * 100, 2),
            "win_rate": round((bh > 0).mean(), 4),
            "n_trades": 1, "annual_turnover": 0,
            "valid": True, "oos_n": len(bh),
        })

    rdf = pd.DataFrame(results)
    rdf.to_csv(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv"), index=False)

    valid_count = rdf["valid"].sum() if len(rdf) > 0 else 0
    print(f"  Tournament: {len(rdf)} combos, {valid_count} valid")
    if len(rdf) > 0:
        vs = rdf[rdf["valid"] & (rdf["signal"] != "BENCHMARK")]
        if len(vs) > 0:
            best = vs.loc[vs["oos_sharpe"].idxmax()]
            print(f"  Best: {best['signal']}/{best['threshold']}/{best['strategy']}"
                  f"/L{best['lead_days']} Sharpe={best['oos_sharpe']:.2f}"
                  f" DD={best['max_drawdown']:.1f}%")
        bm = rdf[rdf["signal"] == "BENCHMARK"]
        if len(bm) > 0:
            print(f"  B&H:  Sharpe={bm.iloc[0]['oos_sharpe']:.2f}"
                  f" DD={bm.iloc[0]['max_drawdown']:.1f}%")
    return rdf


# ─────────────────────────────────────────────────────────────
# STAGE 7: VALIDATION + WINNER OUTPUTS
# ─────────────────────────────────────────────────────────────

def _replay_strategy(work, sig_col, threshold_name, threshold_val, strategy,
                     lead, counter_cyclical=True):
    """Replay a single tournament combo and return (position, strategy_returns)."""
    signal = work[sig_col].shift(lead) if lead > 0 else work[sig_col]

    # Align rolling threshold to work's index if it's a Series
    if isinstance(threshold_val, pd.Series):
        threshold_val = threshold_val.reindex(work.index)

    if threshold_name.startswith("T3_z"):
        roll_mean = signal.rolling(504, min_periods=400).mean()
        roll_std = signal.rolling(504, min_periods=400).std().replace(0, np.nan)
        z_series = (signal - roll_mean) / roll_std
        bullish = z_series < threshold_val
    elif isinstance(threshold_val, (int, float, np.floating)):
        bullish = signal < threshold_val if counter_cyclical else signal > threshold_val
    else:
        bullish = signal < threshold_val if counter_cyclical else signal > threshold_val

    if strategy == "P1":
        pos = bullish.astype(float)
    elif strategy == "P2":
        smin = signal.rolling(504, min_periods=400).min()
        smax = signal.rolling(504, min_periods=400).max()
        sr = (smax - smin).replace(0, np.nan)
        pos = (1 - (signal - smin) / sr).clip(0, 1)
    elif strategy == "P3":
        pos = bullish.astype(float) * 2 - 1
    else:
        pos = bullish.astype(float)

    strat_ret = pos.shift(1) * work["spy_ret"]
    return pos, strat_ret


def _compute_threshold_val(is_signal, threshold_name, signal_series):
    """Compute threshold value from in-sample signal for a given threshold name."""
    if threshold_name.startswith("T1_p"):
        pct = int(threshold_name.split("p")[1])
        return is_signal.quantile(pct / 100)
    elif threshold_name.startswith("T2_rp"):
        pct = int(threshold_name.split("rp")[1])
        return signal_series.rolling(504, min_periods=400).quantile(pct / 100)
    elif threshold_name.startswith("T3_z"):
        return float(threshold_name.split("z")[1])
    elif threshold_name.startswith(("T4_hmm_", "T4_ms_", "T5_hmm_", "T5_ms_")):
        return float(threshold_name.rsplit("_", 1)[1])
    return None


@timed("7_validation")
def stage_validation(df, tourn_df):
    """Walk-forward, bootstrap, cost, decay, stress tests for top-5 winners.
    Then generate winner_summary.json, winner_trade_log.csv, execution_notes.md."""
    import statsmodels.api as sm

    # Load signals from persisted parquet
    signals_path = os.path.join(SIGNALS_DIR, f"signals_{DATE_TAG}.parquet")
    sig_df = pd.read_parquet(signals_path)
    work = df.copy()
    for col in ["hmm_2state_prob_stress", "ms_2state_stress_prob"]:
        if col in sig_df.columns and col not in work.columns:
            work[col] = sig_df[col].reindex(work.index)
    if "spy_ret" not in work.columns:
        work["spy_ret"] = work["spy"].pct_change()

    # ── Select top-5 valid winners ──
    valid = tourn_df[tourn_df["valid"] & (tourn_df["signal"] != "BENCHMARK")]
    if len(valid) == 0:
        print("  No valid winners to validate.")
        return
    top5 = valid.nlargest(5, "oos_sharpe")
    print(f"  Validating top {len(top5)} winners")

    # Signal name -> column mapping (same as tournament)
    signal_col_map = {
        "S1_spread_level":     "hy_ig_spread",
        "S2a_zscore_252d":     "hy_ig_zscore_252d",
        "S2b_zscore_504d":     "hy_ig_zscore_504d",
        "S3a_pctrank_504d":    "hy_ig_pctrank_504d",
        "S3b_pctrank_1260d":   "hy_ig_pctrank_1260d",
        "S4a_roc_21d":         "hy_ig_roc_21d",
        "S4b_roc_63d":         "hy_ig_roc_63d",
        "S4c_roc_126d":        "hy_ig_roc_126d",
        "S5_ccc_bb_spread":    "ccc_bb_spread",
        "S6_hmm_stress":       "hmm_2state_prob_stress",
        "S7_ms_stress":        "ms_2state_stress_prob",
        "S10_mom_21d":         "hy_ig_mom_21d",
        "S11_mom_63d":         "hy_ig_mom_63d",
        "S12_mom_252d":        "hy_ig_mom_252d",
        "S13_acceleration":    "hy_ig_acceleration",
    }

    all_wf = []
    all_bootstrap = []
    all_costs = []
    all_decay = []
    all_stress = []

    for rank, (idx, row) in enumerate(top5.iterrows(), 1):
        sig_name = row["signal"]
        sig_col = signal_col_map.get(sig_name)
        if sig_col is None or sig_col not in work.columns:
            print(f"  SKIP {sig_name}: column not found")
            continue

        tname = row["threshold"]
        strat = row["strategy"]
        lead = int(row["lead_days"])

        signal = work[sig_col]
        is_signal = signal[work.index <= IS_END].dropna()
        tval = _compute_threshold_val(is_signal, tname, signal)

        combo_tag = f"{sig_name}/{tname}/{strat}/L{lead}"
        print(f"  [{rank}] {combo_tag} (OOS Sharpe={row['oos_sharpe']:.2f})")

        # ── 1. Walk-forward (5yr train / 1yr test, rolling annually) ──
        years = sorted(work.index.year.unique())
        for test_year in range(max(years[0] + 5, 2010), max(years) + 1):
            train_start = pd.Timestamp(f"{test_year - 5}-01-01")
            train_end = pd.Timestamp(f"{test_year - 1}-12-31")
            test_start = pd.Timestamp(f"{test_year}-01-01")
            test_end = pd.Timestamp(f"{test_year}-12-31")

            train_mask = (work.index >= train_start) & (work.index <= train_end)
            test_mask = (work.index >= test_start) & (work.index <= test_end)

            train_sig = signal[train_mask].dropna()
            if len(train_sig) < 200:
                continue

            # Recompute threshold on training window
            if tname.startswith("T1_p"):
                pct = int(tname.split("p")[1])
                tv = train_sig.quantile(pct / 100)
            elif tname.startswith("T2_rp"):
                # Rolling thresholds are self-updating; use train+test slice
                # so rolling window has sufficient history
                tv = tval
            else:
                tv = tval  # z-score/probability thresholds are self-updating

            # Use train+test slice so rolling computations have enough lookback
            wf_slice_mask = (work.index >= train_start) & (work.index <= test_end)
            _, wf_ret = _replay_strategy(work[wf_slice_mask], sig_col, tname, tv, strat, lead)
            # Extract only the test period returns
            test_ret = wf_ret[(wf_ret.index >= test_start) & (wf_ret.index <= test_end)].dropna()
            if len(test_ret) < 20:
                continue
            wf_sharpe = ((test_ret.mean() / test_ret.std()) * np.sqrt(252)
                         if test_ret.std() > 0 else 0)
            all_wf.append({
                "rank": rank, "signal": sig_name, "threshold": tname,
                "strategy": strat, "lead_days": lead,
                "test_year": test_year, "oos_sharpe": round(wf_sharpe, 4),
                "n_obs": len(test_ret),
            })

        # ── 2. Bootstrap (10,000 resamples) ──
        oos_mask = work.index >= OOS_START
        _, oos_ret = _replay_strategy(work[oos_mask], sig_col, tname, tval, strat, lead)
        oos_ret = oos_ret.dropna()
        if len(oos_ret) > 50:
            rng = np.random.RandomState(42)
            boot_sharpes = []
            oos_arr = oos_ret.values
            n = len(oos_arr)
            for _ in range(10000):
                sample = rng.choice(oos_arr, size=n, replace=True)
                bs = (sample.mean() / sample.std()) * np.sqrt(252) if sample.std() > 0 else 0
                boot_sharpes.append(bs)
            boot_sharpes = np.array(boot_sharpes)
            all_bootstrap.append({
                "rank": rank, "signal": sig_name, "threshold": tname,
                "strategy": strat, "lead_days": lead,
                "mean_sharpe": round(np.mean(boot_sharpes), 4),
                "ci_2_5": round(np.percentile(boot_sharpes, 2.5), 4),
                "ci_97_5": round(np.percentile(boot_sharpes, 97.5), 4),
                "pct_positive": round((boot_sharpes > 0).mean() * 100, 1),
            })

        # ── 3. Transaction costs ──
        for bps in [0, 5, 10, 20, 50]:
            _, ret = _replay_strategy(work[oos_mask], sig_col, tname, tval, strat, lead)
            ret = ret.dropna()
            if len(ret) < 50:
                continue
            # Position changes incur cost
            pos, _ = _replay_strategy(work[oos_mask], sig_col, tname, tval, strat, lead)
            pos_changes = pos.diff().abs().fillna(0)
            cost_per_day = pos_changes * (bps / 10000)
            net_ret = ret - cost_per_day.shift(1).reindex(ret.index, fill_value=0)
            net_sharpe = ((net_ret.mean() / net_ret.std()) * np.sqrt(252)
                          if net_ret.std() > 0 else 0)
            all_costs.append({
                "rank": rank, "signal": sig_name, "threshold": tname,
                "strategy": strat, "lead_days": lead,
                "tx_cost_bps": bps,
                "net_sharpe_approx": round(net_sharpe, 4),
                "oos_sharpe": round(row["oos_sharpe"], 4),
            })

        # ── 4. Signal decay (execution delay 0-5 days) ──
        for delay in [0, 1, 2, 3, 5]:
            actual_lead = lead + delay
            _, delay_ret = _replay_strategy(
                work[oos_mask], sig_col, tname, tval, strat, actual_lead)
            delay_ret = delay_ret.dropna()
            if len(delay_ret) < 50:
                continue
            delay_sharpe = ((delay_ret.mean() / delay_ret.std()) * np.sqrt(252)
                            if delay_ret.std() > 0 else 0)
            all_decay.append({
                "rank": rank, "signal": sig_name, "threshold": tname,
                "strategy": strat, "lead_days": lead,
                "execution_delay": delay,
                "oos_sharpe": round(delay_sharpe, 4),
            })

        # ── 5. Stress tests ──
        stress_periods = [
            ("GFC_2007_2009", "2007-07-01", "2009-03-31"),
            ("COVID_2020", "2020-02-01", "2020-06-30"),
            ("Taper_Tantrum_2013", "2013-05-01", "2013-09-30"),
            ("Rate_Shock_2022", "2022-01-01", "2022-12-31"),
        ]
        for period_name, pstart, pend in stress_periods:
            pmask = (work.index >= pstart) & (work.index <= pend)
            if pmask.sum() < 20:
                continue
            _, stress_ret = _replay_strategy(work[pmask], sig_col, tname, tval, strat, lead)
            stress_ret = stress_ret.dropna()
            if len(stress_ret) < 10:
                continue
            s_sharpe = ((stress_ret.mean() / stress_ret.std()) * np.sqrt(252)
                        if stress_ret.std() > 0 else 0)
            cum = (1 + stress_ret).cumprod()
            s_dd = ((cum - cum.cummax()) / cum.cummax()).min()
            # Benchmark for same period
            bh_stress = work.loc[pmask, "spy_ret"].dropna()
            bh_sharpe = ((bh_stress.mean() / bh_stress.std()) * np.sqrt(252)
                         if bh_stress.std() > 0 else 0)
            all_stress.append({
                "rank": rank, "signal": sig_name, "threshold": tname,
                "strategy": strat, "lead_days": lead,
                "period": period_name, "start": pstart, "end": pend,
                "strategy_sharpe": round(s_sharpe, 4),
                "strategy_max_dd": round(s_dd * 100, 2),
                "benchmark_sharpe": round(bh_sharpe, 4),
                "n_obs": len(stress_ret),
            })

    # ── Save validation results ──
    pd.DataFrame(all_wf).to_csv(
        os.path.join(VALIDATION_DIR, "walk_forward.csv"), index=False)
    pd.DataFrame(all_bootstrap).to_csv(
        os.path.join(VALIDATION_DIR, "bootstrap_ci.csv"), index=False)
    pd.DataFrame(all_costs).to_csv(
        os.path.join(VALIDATION_DIR, "transaction_costs.csv"), index=False)
    pd.DataFrame(all_decay).to_csv(
        os.path.join(VALIDATION_DIR, "signal_decay.csv"), index=False)
    pd.DataFrame(all_stress).to_csv(
        os.path.join(VALIDATION_DIR, "stress_tests.csv"), index=False)
    print(f"  Walk-forward: {len(all_wf)} year-combos")
    print(f"  Bootstrap: {len(all_bootstrap)} combos")
    print(f"  Cost analysis: {len(all_costs)} rows")
    print(f"  Signal decay: {len(all_decay)} rows")
    print(f"  Stress tests: {len(all_stress)} rows")

    # ── Generate winner outputs ──
    _generate_winner_outputs(tourn_df, work)


def _generate_winner_outputs(tourn_df, work):
    """Generate winner_summary.json, winner_trade_log.csv, execution_notes.md."""
    valid = tourn_df[tourn_df["valid"] & (tourn_df["signal"] != "BENCHMARK")]
    if len(valid) == 0:
        print("  No valid winner for outputs.")
        return
    winner = valid.loc[valid["oos_sharpe"].idxmax()]

    # Load interpretation metadata
    meta_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    with open(meta_path) as f:
        metadata = json.load(f)

    signal_col_map = {
        "S1_spread_level":     "hy_ig_spread",
        "S2a_zscore_252d":     "hy_ig_zscore_252d",
        "S2b_zscore_504d":     "hy_ig_zscore_504d",
        "S3a_pctrank_504d":    "hy_ig_pctrank_504d",
        "S3b_pctrank_1260d":   "hy_ig_pctrank_1260d",
        "S4a_roc_21d":         "hy_ig_roc_21d",
        "S4b_roc_63d":         "hy_ig_roc_63d",
        "S4c_roc_126d":        "hy_ig_roc_126d",
        "S5_ccc_bb_spread":    "ccc_bb_spread",
        "S6_hmm_stress":       "hmm_2state_prob_stress",
        "S7_ms_stress":        "ms_2state_stress_prob",
        "S10_mom_21d":         "hy_ig_mom_21d",
        "S11_mom_63d":         "hy_ig_mom_63d",
        "S12_mom_252d":        "hy_ig_mom_252d",
        "S13_acceleration":    "hy_ig_acceleration",
    }

    signal_display = {
        "S1_spread_level": "HY-IG Spread Level",
        "S2a_zscore_252d": "HY-IG Z-Score (252d)",
        "S2b_zscore_504d": "HY-IG Z-Score (504d)",
        "S3a_pctrank_504d": "HY-IG Percentile Rank (504d)",
        "S3b_pctrank_1260d": "HY-IG Percentile Rank (1260d)",
        "S4a_roc_21d": "HY-IG 21-Day Rate of Change",
        "S4b_roc_63d": "HY-IG 63-Day Rate of Change",
        "S4c_roc_126d": "HY-IG 126-Day Rate of Change",
        "S5_ccc_bb_spread": "CCC-BB Quality Spread",
        "S6_hmm_stress": "HMM Stress Probability",
        "S7_ms_stress": "Markov-Switching Stress Probability",
        "S10_mom_21d": "HY-IG 21-Day Momentum",
        "S11_mom_63d": "HY-IG 63-Day Momentum",
        "S12_mom_252d": "HY-IG 252-Day Momentum",
        "S13_acceleration": "HY-IG Acceleration",
    }

    threshold_display = {
        "T1_p75": "75th percentile (fixed)",
        "T1_p85": "85th percentile (fixed)",
        "T1_p95": "95th percentile (fixed)",
        "T2_rp75": "75th percentile (rolling 504d)",
        "T2_rp85": "85th percentile (rolling 504d)",
        "T2_rp95": "95th percentile (rolling 504d)",
        "T3_z1.5": "Z-score > 1.5",
        "T3_z2.0": "Z-score > 2.0",
        "T3_z2.5": "Z-score > 2.5",
        "T4_hmm_0.5": "HMM probability > 0.5",
        "T4_hmm_0.7": "HMM probability > 0.7",
        "T5_ms_0.5": "MS probability > 0.5",
        "T5_ms_0.7": "MS probability > 0.7",
    }

    strategy_display = {"P1": "Long/Cash", "P2": "Signal Strength", "P3": "Long/Short"}
    strategy_desc = {
        "P1": "Go fully long SPY when signal is bullish; move to cash otherwise.",
        "P2": "Scale position size proportionally to signal strength (0% to 100% invested).",
        "P3": "Go long SPY when bullish, short SPY when bearish.",
    }

    sig_name = winner["signal"]
    tname = winner["threshold"]
    strat = winner["strategy"]
    lead = int(winner["lead_days"])

    # ── winner_summary.json ──
    summary = {
        "pair_id": PAIR_ID,
        "signal_code": sig_name,
        "signal_display_name": signal_display.get(sig_name, sig_name),
        "threshold_code": tname,
        "threshold_display_name": threshold_display.get(tname, tname),
        "strategy_code": strat,
        "strategy_display_name": strategy_display.get(strat, strat),
        "strategy_description": strategy_desc.get(strat, ""),
        "lead_value": lead,
        "lead_unit": "days",
        "lead_description": f"{lead} days" if lead > 0 else "No lead (same-period)",
        "direction": metadata.get("expected_direction", "counter_cyclical"),
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "oos_ann_return": round(float(winner.get("oos_ann_return", 0)), 2),
        "max_drawdown": round(float(winner["max_drawdown"]), 2),
        "annual_turnover": round(float(winner.get("annual_turnover", 0)), 2),
        "win_rate": round(float(winner.get("win_rate", 0)), 4)
            if "win_rate" in winner.index else None,
    }

    # Threshold value for fixed thresholds
    if tname.startswith("T4_") or tname.startswith("T5_"):
        summary["threshold_value"] = float(tname.rsplit("_", 1)[1])
    elif tname.startswith("T1_p"):
        pct = int(tname.split("p")[1])
        sig_col = signal_col_map.get(sig_name)
        if sig_col and sig_col in work.columns:
            is_sig = work.loc[work.index <= IS_END, sig_col].dropna()
            summary["threshold_value"] = round(float(is_sig.quantile(pct / 100)), 4)
        else:
            summary["threshold_value"] = None
    else:
        summary["threshold_value"] = None

    # Signal decay and cost info from validation
    decay_path = os.path.join(VALIDATION_DIR, "signal_decay.csv")
    if os.path.exists(decay_path):
        decay_df = pd.read_csv(decay_path)
        decay_winner = decay_df[
            (decay_df["signal"] == sig_name) & (decay_df["threshold"] == tname)
            & (decay_df["strategy"] == strat) & (decay_df["lead_days"] == lead)]
        if len(decay_winner) > 0:
            pos_rows = decay_winner[decay_winner["oos_sharpe"] > 0]
            summary["max_acceptable_delay_days"] = int(pos_rows["execution_delay"].max()) if len(pos_rows) > 0 else 0

    cost_path = os.path.join(VALIDATION_DIR, "transaction_costs.csv")
    if os.path.exists(cost_path):
        cost_df = pd.read_csv(cost_path)
        cost_winner = cost_df[
            (cost_df["signal"] == sig_name) & (cost_df["threshold"] == tname)
            & (cost_df["strategy"] == strat) & (cost_df["lead_days"] == lead)]
        if len(cost_winner) > 0:
            pos_costs = cost_winner[cost_winner["net_sharpe_approx"] > 0]
            summary["breakeven_cost_bps"] = float(pos_costs["tx_cost_bps"].max()) if len(pos_costs) > 0 else 0.0

    summary_path = os.path.join(RESULTS_DIR, "winner_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Saved: winner_summary.json (Sharpe={summary['oos_sharpe']:.2f})")

    # ── winner_trade_log.csv ──
    sig_col = signal_col_map.get(sig_name)
    if sig_col and sig_col in work.columns:
        signal = work[sig_col]
        is_signal = signal[work.index <= IS_END].dropna()
        tval = _compute_threshold_val(is_signal, tname, signal)
        pos, strat_ret = _replay_strategy(work, sig_col, tname, tval, strat, lead)
        cum_ret = (1 + strat_ret.fillna(0)).cumprod()

        pos_clean = pos.dropna()
        pos_change = pos_clean.diff().fillna(pos_clean.iloc[0] if len(pos_clean) > 0 else 0)
        trade_entries = pos_change[pos_change != 0].index

        trades = []
        for i in range(len(trade_entries)):
            entry_date = trade_entries[i]
            exit_date = trade_entries[i + 1] if i + 1 < len(trade_entries) else work.index[-1]
            entry_pos = pos.loc[entry_date]
            direction = "Long" if entry_pos > 0 else ("Short" if entry_pos < 0 else "Cash")
            holding_days = (exit_date - entry_date).days

            if entry_date in cum_ret.index and exit_date in cum_ret.index:
                entry_cum = cum_ret.loc[:entry_date].iloc[-1]
                exit_cum = cum_ret.loc[:exit_date].iloc[-1]
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

        trade_df = pd.DataFrame(trades)
        trade_df.to_csv(os.path.join(RESULTS_DIR, "winner_trade_log.csv"), index=False)
        print(f"  Saved: winner_trade_log.csv ({len(trade_df)} trades)")

    # ── execution_notes.md ──
    direction_text = ("Higher values are bearish (go long when signal falls below threshold)."
                      if metadata.get("expected_direction") == "counter_cyclical"
                      else "Higher values are bullish (go long when signal rises above threshold).")

    lines = [
        f"# Execution Notes: {PAIR_ID}",
        "",
        f"## Winner: {signal_display.get(sig_name, sig_name)} / "
        f"{threshold_display.get(tname, tname)} / {strategy_display.get(strat, strat)}",
        "",
        "## Step-by-Step Execution",
        "",
        f"1. **Monitor** the {signal_display.get(sig_name, sig_name)} indicator daily.",
        f"2. **Apply threshold**: {threshold_display.get(tname, tname)}.",
        f"3. **Direction**: {direction_text}",
        f"4. **Action**: {strategy_desc.get(strat, '')}",
        f"5. **Lead time**: {summary['lead_description']}.",
    ]
    if summary.get("max_acceptable_delay_days") is not None:
        lines.append(
            f"6. **Execution window**: Signal remains actionable up to "
            f"{summary['max_acceptable_delay_days']} day(s) after generation.")
    if summary.get("breakeven_cost_bps") is not None:
        lines.append(
            f"7. **Transaction cost budget**: Strategy Sharpe remains positive "
            f"up to {summary['breakeven_cost_bps']:.1f} bps round-trip.")
    lines.append(f"8. **Expected turnover**: ~{summary['annual_turnover']:.1f} trades per year.")

    caveats = metadata.get("caveats", [])
    if caveats:
        lines.extend(["", "## Caveats", ""])
        for c in caveats:
            lines.append(f"- {c}")

    lines.extend(["", "---", f"*Generated by Evan's pipeline for {PAIR_ID}*"])
    notes_path = os.path.join(RESULTS_DIR, "execution_notes.md")
    with open(notes_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  Saved: execution_notes.md")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print(f"{'='*60}\n  {INDICATOR_NAME} -> {TARGET_NAME}\n  Pair ID: {PAIR_ID} | Date: {DATE_TAG}\n{'='*60}")

    # Stage 1: Source data
    series = stage_data()

    # Stage 2: Derive signals and build master DataFrame
    df = stage_derived(series)

    # Save master parquet
    parquet_path = os.path.join(DATA_DIR, f"{PAIR_ID}_daily_{DATE_TAG}.parquet")
    df.to_parquet(parquet_path, engine="pyarrow")
    print(f"\n  Saved master parquet: {parquet_path}")
    print(f"  Shape: {df.shape}")

    # Stage 3: Stationarity tests
    stage_stationarity(df)

    # Stage 4: Exploratory analysis
    stage_exploratory(df)

    # Stage 5: Core models (+ persist HMM/MS signals)
    reg_df, hmm_probs, ms_probs = stage_models(df)

    # Stage 6: Tournament
    tourn_df = stage_tournament(df)

    # Stage 7: Validation + winner outputs
    stage_validation(df, tourn_df)

    elapsed = time.time() - t0
    print(f"\n{'='*60}\n  ALL 7 STAGES DONE in {elapsed:.1f}s\n{'='*60}")
    for name, secs in STAGE_TIMES.items():
        print(f"  {name:25s}: {secs:.1f}s")

    timing = {
        "pair_id": PAIR_ID,
        "total_seconds": round(elapsed, 1),
        "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
    }
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump(timing, f, indent=2)


if __name__ == "__main__":
    main()
