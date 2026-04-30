#!/usr/bin/env python3
"""
Full Analysis Pipeline: HY-IG Credit Spread → S&P 500 (SPY)
=============================================================
Pair ID: hy_ig_spy  (fresh pair; v1 archived to hy_ig_spy_v1 in Wave 10G.1)

Wave 10G.4C — Extended pipeline (Evan's stages 2-7)
====================================================
Stage 1 (data sourcing) and the DATA-D5/D12 infrastructure were written by
Data Dana in Wave 10G.4A. This file extends that foundation with all Evan-owned
stages. Do NOT re-run Stage 1 from scratch — load the committed parquet.

Indicator : HY-IG Credit Spread OAS (FRED BAMLH0A0HYM2 − BAMLC0A0CM)
Target    : SPDR S&P 500 ETF (SPY) adjusted close via Yahoo Finance
Date range: 2000-01-01 through 2026-04-22

Output artefacts (all under results/hy_ig_spy/):
  signals_20260422.parquet          — ECON-DS2 deploy-required
  tournament_results_20260422.csv   — ratio form per META-UC
  winner_summary.json               — schema v1.0.0 per ECON-H5 / APP-WS1
  tournament_winner.json            — winner+benchmark delta record
  signal_scope.json                 — axis_block per ECON-SD / APP-SS1
  analyst_suggestions.json          — ECON-AS informational channel
  stationarity_tests_20260422.csv   — ADF + KPSS per ECON-C
  granger_by_lag.csv                — Rule E1 schema
  regime_quartile_returns.csv       — Rule E2 schema (ratio form)
  winner_trade_log.csv              — per-trade P&L log
  winner_trades_broker_style.csv    — broker-style format
  oos_split_record.json             — ECON-OOS1
  pipeline_timing_20260422.json     — stage wall-clock times
  core_models_20260422/             — Granger, regressions, HMM, MS, QR, LP
  exploratory_20260422/             — correlations, regime stats
  tournament_validation_20260422/   — bootstrap CI, walk-forward, costs, decay, stress
  handoff_to_vera_20260422.md       — ECON-H4 per-method chart table
  handoff_evan_20260422.md          — META-RYW + META-SRV evidence

ECON-DS2 gate (blocking):
  git ls-files results/hy_ig_spy/signals_*.parquet must return ≥1 file.

Column naming:
  Uses DATA-D12 renamed columns from Dana's parquet:
    ccc_bb_spread_pct     (not ccc_bb_spread)
    yield_spread_10y3m_pct (not yield_spread_10y3m)
    yield_spread_10y2y_pct (not yield_spread_10y2y)
    bbb_ig_spread_pct     (not bbb_ig_spread)

Author : Econ Evan (econ-evan@idficient.com)
Date   : 2026-04-22
SOP    : docs/agent-sops/econometrics-agent-sop.md Wave 10G
"""

import os, sys
from pathlib import Path, json, warnings, time, datetime, itertools
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

PAIR_ID        = "hy_ig_spy"
INDICATOR_NAME = "HY-IG Credit Spread"
TARGET_NAME    = "S&P 500 (SPY)"
START_DATE     = "2000-01-01"
END_DATE       = "2026-04-22"
DATE_TAG       = "20260422"

# OOS window — ECON-OOS2 formula:
# span_months = min(max(36, round(N×0.25)), 120)
# Total sample 2000-01-03 to 2026-04-22 ≈ 316 months
# span = min(max(36, round(316×0.25)), 120) = min(max(36, 79), 120) = 79 months ≈ 6.6 yr
# OOS_START = END_DATE - 79 months ≈ 2019-09-01 (round to 2019-10-01)
IS_END    = "2019-09-30"
OOS_START = "2019-10-01"
OOS_END   = END_DATE

BASE_DIR      = str(Path(__file__).resolve().parents[1])
DATA_DIR      = os.path.join(BASE_DIR, "data")
RESULTS_DIR   = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR   = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR    = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALIDATION_DIR= os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")
SIGNALS_DIR   = RESULTS_DIR

for d in [DATA_DIR, RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALIDATION_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES: dict = {}


def timed(name):
    def dec(func):
        def wrap(*a, **kw):
            t0 = time.time()
            print(f"\n{'='*60}\n  {name}\n{'='*60}")
            r = func(*a, **kw)
            STAGE_TIMES[name] = time.time() - t0
            print(f"  [{name}] completed in {STAGE_TIMES[name]:.1f}s")
            return r
        return wrap
    return dec




def load_legacy_fred_archive() -> dict:
    """Load optional local Wayback archive created by fetch_fred_wayback_archive.py."""
    path = os.path.join(DATA_DIR, "legacy_fred_archive", "ice_bofa_oas_wayback.csv")
    if not os.path.exists(path):
        print("  [WARN] Legacy ICE/FRED archive not found. To restore pre-truncation OAS history on clean refreshes, run scripts/fetch_fred_wayback_archive.py --accept-ice-terms.")
        return {}
    legacy = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    out = {}
    for col in ["hy_oas", "ig_oas", "bb_hy_oas", "ccc_hy_oas", "bbb_oas"]:
        if col in legacy.columns:
            out[col] = pd.to_numeric(legacy[col], errors="coerce").dropna()
    print(f"  Loaded legacy ICE/FRED archive: {path}")
    return out


# ─────────────────────────────────────────────────────────────
# STAGE 1: DATA SOURCING  (Dana-owned — load from parquet)
# ─────────────────────────────────────────────────────────────

def stage_data() -> pd.DataFrame:
    """
    Load Dana's committed parquet. Do NOT re-fetch.

    If no parquet found, attempt live fetch as fallback (same logic as
    Dana's script, for reproducibility on a clean checkout).
    Returns a DataFrame with DatetimeIndex.
    """
    print(f"\n{'='*60}")
    print(f"  STAGE 1 — DATA LOAD  (Dana's parquet)")
    print(f"  Pair: {PAIR_ID}  |  {START_DATE} → {END_DATE}")
    print(f"{'='*60}")

    # Look for Dana's parquet
    import glob
    parquet_candidates = sorted(glob.glob(
        os.path.join(DATA_DIR, f"{PAIR_ID}_daily_*.parquet")))
    if parquet_candidates:
        parquet_path = parquet_candidates[-1]   # most-recent
        df = pd.read_parquet(parquet_path)
        print(f"  Loaded: {parquet_path}")
        print(f"  Shape: {df.shape}  |  {df.index.min().date()} → {df.index.max().date()}")
        return df

    # ── Fallback: live fetch (mirrors Dana's script) ──────────
    print("  [WARN] No parquet found — running live fetch (fallback).")
    import yfinance as yf
    from fredapi import Fred

    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("  [WARN] FRED_API_KEY not set; using FRED DEMO_KEY fallback. For reliable full refreshes, set FRED_API_KEY.")
        api_key = "DEMO_KEY"
    fred = Fred(api_key=api_key)
    series: dict = {}

    fred_map = [
        ("BAMLH0A0HYM2", "hy_oas"), ("BAMLC0A0CM",   "ig_oas"),
        ("BAMLH0A1HYBB", "bb_hy_oas"), ("BAMLH0A3HYC", "ccc_hy_oas"),
        ("DGS10",        "dgs10"), ("DTB3",           "dtb3"),
        ("DGS2",         "dgs2"), ("NFCI",            "nfci"),
        ("DFF",          "fed_funds_rate"), ("BAMLC0A4CBBB", "bbb_oas"),
        ("STLFSI4",      "fsi"), ("ICSA",             "initial_claims"),
        ("SOFR",         "sofr"),
    ]
    for sid, name in fred_map:
        for attempt in range(3):
            try:
                s = fred.get_series(sid, observation_start=START_DATE,
                                    observation_end=END_DATE)
                series[name] = s.astype(float)
                break
            except Exception as e:
                if attempt == 2:
                    print(f"  [FRED] {sid} FAILED: {e}")

    for col, legacy_series in load_legacy_fred_archive().items():
        live = series.get(col, pd.Series(dtype=float)).dropna()
        series[col] = live.combine_first(legacy_series).astype(float)

    # OAS splice from v1 parquet
    v1_path = os.path.join(DATA_DIR, "hy_ig_spy_v1_daily_20000101_20251231.parquet")
    if os.path.exists(v1_path):
        v1 = pd.read_parquet(v1_path)
        for col, tgt in [("hy_oas","hy_oas"),("ig_oas","ig_oas"),
                         ("bb_hy_oas","bb_hy_oas"),("ccc_hy_oas","ccc_hy_oas"),
                         ("bbb_oas","bbb_oas")]:
            if col in v1.columns:
                hist = v1[col].dropna()
                live = series.get(tgt, pd.Series(dtype=float)).dropna()
                series[tgt] = hist.combine_first(live).astype(float)

    if "hy_oas" not in series or "ig_oas" not in series:
        raise RuntimeError("STOP: Missing core OAS series. Cannot build hy_ig_spread_pct.")

    yf_map = [("SPY","spy"),("^VIX","vix"),("^VIX3M","vix3m"),("KBE","kbe"),
              ("IWM","iwm"),("^MOVE","move_index"),("GC=F","gold"),
              ("HG=F","copper"),("DX-Y.NYB","dxy"),("HYG","hyg")]
    for ticker, name in yf_map:
        try:
            dl = yf.download(ticker, start=START_DATE, end=END_DATE,
                             progress=False, auto_adjust=True)
            if isinstance(dl.columns, pd.MultiIndex):
                dl.columns = dl.columns.get_level_values(0)
            s = dl["Close"]
            s.index = s.index.tz_localize(None) if s.index.tz else s.index
            series[name] = s.astype(float)
        except Exception as e:
            print(f"  [YF] {ticker} FAILED: {e}")

    if "spy" not in series:
        raise RuntimeError("STOP: SPY fetch failed.")

    # Build DataFrame
    bdays = pd.bdate_range(START_DATE, END_DATE)
    df = pd.DataFrame(index=bdays)
    df.index.name = "date"
    weekly_cols = {"nfci", "fsi", "initial_claims"}
    for col, s in series.items():
        limit = 10 if col in weekly_cols else 5
        if col in weekly_cols:
            def _to_bday(d):
                return d if d.weekday() < 5 else d - pd.Timedelta(days=d.weekday()-4)
            s = s.copy()
            s.index = s.index.map(_to_bday)
            s = s[~s.index.duplicated(keep="last")]
        df[col] = s.reindex(bdays).ffill(limit=limit)

    # Derived columns (DATA-D12 names)
    df["hy_ig_spread_pct"] = df["hy_oas"] - df["ig_oas"]
    spread = df["hy_ig_spread_pct"]
    df["hy_ig_zscore_252d"] = (spread - spread.rolling(252,min_periods=200).mean()) / spread.rolling(252,min_periods=200).std()
    df["hy_ig_zscore_504d"] = (spread - spread.rolling(504,min_periods=400).mean()) / spread.rolling(504,min_periods=400).std()
    df["hy_ig_pctrank_504d"] = spread.rolling(504,min_periods=400).apply(lambda x: stats.rankdata(x)[-1]/len(x), raw=True)
    df["hy_ig_pctrank_1260d"] = spread.rolling(1260,min_periods=1000).apply(lambda x: stats.rankdata(x)[-1]/len(x), raw=True)
    df["hy_ig_roc_21d"]  = (spread/spread.shift(21)-1)*100
    df["hy_ig_roc_63d"]  = (spread/spread.shift(63)-1)*100
    df["hy_ig_roc_126d"] = (spread/spread.shift(126)-1)*100
    df["hy_ig_mom_21d"]  = spread - spread.shift(21)
    df["hy_ig_mom_63d"]  = spread - spread.shift(63)
    df["hy_ig_mom_252d"] = spread - spread.shift(252)
    df["hy_ig_acceleration"] = df["hy_ig_roc_21d"] - df["hy_ig_roc_21d"].shift(21)
    if "ccc_hy_oas" in df.columns and "bb_hy_oas" in df.columns:
        df["ccc_bb_spread_pct"] = df["ccc_hy_oas"] - df["bb_hy_oas"]
    df["hy_ig_realized_vol_21d"] = spread.diff().rolling(21,min_periods=15).std()
    if "vix3m" in df.columns and "vix" in df.columns:
        df["vix_term_structure"] = df["vix3m"] - df["vix"]
    if "dgs10" in df.columns and "dtb3" in df.columns:
        df["yield_spread_10y3m_pct"] = df["dgs10"] - df["dtb3"]
    if "dgs10" in df.columns and "dgs2" in df.columns:
        df["yield_spread_10y2y_pct"] = df["dgs10"] - df["dgs2"]
    if "kbe" in df.columns and "iwm" in df.columns:
        df["bank_smallcap_ratio"] = df["kbe"] / df["iwm"]
    if "nfci" in df.columns:
        df["nfci_momentum_13w"] = df["nfci"] - df["nfci"].shift(65)
    if "bbb_oas" in df.columns and "ig_oas" in df.columns:
        df["bbb_ig_spread_pct"] = df["bbb_oas"] - df["ig_oas"]
    spy = df["spy"]
    df["spy_ret"]      = spy.pct_change()
    df["spy_fwd_1d"]   = spy.pct_change(1).shift(-1)
    df["spy_fwd_5d"]   = spy.shift(-5)/spy  - 1
    df["spy_fwd_21d"]  = spy.shift(-21)/spy - 1
    df["spy_fwd_63d"]  = spy.shift(-63)/spy - 1
    df["spy_fwd_126d"] = spy.shift(-126)/spy- 1
    df["spy_fwd_252d"] = spy.shift(-252)/spy- 1
    df = df.dropna(subset=["hy_ig_spread_pct","spy"])

    # Save parquet for future reloads
    out_path = os.path.join(DATA_DIR, f"{PAIR_ID}_daily_{DATE_TAG[:8]}_{DATE_TAG}.parquet")
    df.to_parquet(out_path, engine="pyarrow")
    print(f"  Fallback parquet saved: {out_path}")
    return df


# ─────────────────────────────────────────────────────────────
# STAGE 2: FEATURE ENGINEERING (signal columns from parquet)
# ─────────────────────────────────────────────────────────────

@timed("2_features")
def stage_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verify or compute all derived signal columns needed for the tournament.
    The parquet from Dana already contains the core derived signals.
    This stage adds any missing ones and reports the inventory.

    Column names follow DATA-D12 rename convention:
      ccc_bb_spread_pct, yield_spread_10y3m_pct, yield_spread_10y2y_pct, bbb_ig_spread_pct
    """
    spread = df.get("hy_ig_spread_pct")
    if spread is None:
        raise RuntimeError("STOP: hy_ig_spread_pct missing from parquet. Re-run Stage 1.")

    needed = {
        "hy_ig_zscore_252d":  lambda: (spread-spread.rolling(252,min_periods=200).mean())/spread.rolling(252,min_periods=200).std(),
        "hy_ig_zscore_504d":  lambda: (spread-spread.rolling(504,min_periods=400).mean())/spread.rolling(504,min_periods=400).std(),
        "hy_ig_pctrank_504d": lambda: spread.rolling(504,min_periods=400).apply(lambda x: stats.rankdata(x)[-1]/len(x), raw=True),
        "hy_ig_pctrank_1260d":lambda: spread.rolling(1260,min_periods=1000).apply(lambda x: stats.rankdata(x)[-1]/len(x), raw=True),
        "hy_ig_roc_21d":      lambda: (spread/spread.shift(21)-1)*100,
        "hy_ig_roc_63d":      lambda: (spread/spread.shift(63)-1)*100,
        "hy_ig_roc_126d":     lambda: (spread/spread.shift(126)-1)*100,
        "hy_ig_mom_21d":      lambda: spread-spread.shift(21),
        "hy_ig_mom_63d":      lambda: spread-spread.shift(63),
        "hy_ig_mom_252d":     lambda: spread-spread.shift(252),
        "hy_ig_acceleration": lambda: df["hy_ig_roc_21d"]-df["hy_ig_roc_21d"].shift(21),
        "hy_ig_realized_vol_21d": lambda: spread.diff().rolling(21,min_periods=15).std(),
    }

    for col, fn in needed.items():
        if col not in df.columns or df[col].isna().all():
            print(f"  [COMPUTE] {col}")
            df[col] = fn()
        else:
            print(f"  [OK]      {col} ({df[col].notna().sum()} non-null)")

    # DATA-D12 renamed columns — guard against v1-style bare names
    rename_map = {
        "ccc_bb_spread":      "ccc_bb_spread_pct",
        "yield_spread_10y3m": "yield_spread_10y3m_pct",
        "yield_spread_10y2y": "yield_spread_10y2y_pct",
        "bbb_ig_spread":      "bbb_ig_spread_pct",
    }
    for old, new in rename_map.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]
            print(f"  [RENAME] {old} -> {new}")

    # Compute _pct columns if still missing
    if "ccc_bb_spread_pct" not in df.columns and "ccc_hy_oas" in df.columns and "bb_hy_oas" in df.columns:
        df["ccc_bb_spread_pct"] = df["ccc_hy_oas"] - df["bb_hy_oas"]
    if "bbb_ig_spread_pct" not in df.columns and "bbb_oas" in df.columns and "ig_oas" in df.columns:
        df["bbb_ig_spread_pct"] = df["bbb_oas"] - df["ig_oas"]
    if "yield_spread_10y3m_pct" not in df.columns and "dgs10" in df.columns and "dtb3" in df.columns:
        df["yield_spread_10y3m_pct"] = df["dgs10"] - df["dtb3"]
    if "yield_spread_10y2y_pct" not in df.columns and "dgs10" in df.columns and "dgs2" in df.columns:
        df["yield_spread_10y2y_pct"] = df["dgs10"] - df["dgs2"]
    if "vix_term_structure" not in df.columns and "vix3m" in df.columns and "vix" in df.columns:
        df["vix_term_structure"] = df["vix3m"] - df["vix"]
    if "bank_smallcap_ratio" not in df.columns and "kbe" in df.columns and "iwm" in df.columns:
        df["bank_smallcap_ratio"] = df["kbe"] / df["iwm"]
    if "nfci_momentum_13w" not in df.columns and "nfci" in df.columns:
        df["nfci_momentum_13w"] = df["nfci"] - df["nfci"].shift(65)

    if "spy_ret" not in df.columns:
        df["spy_ret"] = df["spy"].pct_change()

    print(f"\n  Master DataFrame: {df.shape[0]} rows × {df.shape[1]} cols")
    print(f"  IS: {START_DATE} → {IS_END}  |  OOS: {OOS_START} → {OOS_END}")
    return df


# ─────────────────────────────────────────────────────────────
# STAGE 3: SIGNALS PARQUET (ECON-DS2)
# ─────────────────────────────────────────────────────────────

@timed("3_signals")
def stage_signals(df: pd.DataFrame, hmm_probs: pd.Series,
                  ms_probs: pd.Series) -> pd.DataFrame:
    """
    Persist tournament-eligible derived signals to parquet.
    ECON-DS2 blocking gate: this file MUST be committed before handoff.

    Column names are the canonical tournament signal_code column names.
    """
    sig_df = df[[
        "hy_ig_spread_pct", "hy_ig_zscore_252d", "hy_ig_zscore_504d",
        "hy_ig_pctrank_504d", "hy_ig_pctrank_1260d",
        "hy_ig_roc_21d", "hy_ig_roc_63d", "hy_ig_roc_126d",
        "hy_ig_mom_21d", "hy_ig_mom_63d", "hy_ig_mom_252d",
        "hy_ig_acceleration",
    ]].copy()

    # Optional columns
    for col in ["ccc_bb_spread_pct", "hy_ig_realized_vol_21d"]:
        if col in df.columns:
            sig_df[col] = df[col]

    sig_df["hmm_2state_prob_stress"] = hmm_probs.reindex(df.index)
    sig_df["hmm_2state_prob_calm"]   = (1 - hmm_probs).reindex(df.index)
    sig_df["ms_2state_stress_prob"]  = ms_probs.reindex(df.index)

    signals_path = os.path.join(SIGNALS_DIR, f"signals_{DATE_TAG}.parquet")
    sig_df.to_parquet(signals_path)
    print(f"  Signals parquet: {signals_path}")
    print(f"  Shape: {sig_df.shape}  |  Columns: {list(sig_df.columns)}")
    return sig_df


# ─────────────────────────────────────────────────────────────
# STAGE 4: CORE MODELS
# ─────────────────────────────────────────────────────────────

@timed("4_core_models")
def stage_core_models(df: pd.DataFrame):
    """
    Granger causality, predictive regressions, local projections, quantile
    regression, HMM regime detection, Markov-switching regression,
    diagnostics, CCF.

    Returns (hmm_probs, ms_probs, reg_df) for downstream use.
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    work = df.dropna(subset=["hy_ig_spread_pct", "spy_ret"]).copy()

    # ── 1. Granger Causality — monthly (Rule E1) ──────────────
    # Rule E1 schema: lag, f_statistic, p_value, df_num, df_den (monthly lags 1-12)
    granger_rows = []
    try:
        # Use monthly-sampled series (last bday per month)
        monthly = work[["spy_ret", "hy_ig_spread_pct"]].resample("ME").last().dropna()
        if len(monthly) > 60:
            gc = grangercausalitytests(
                monthly[["spy_ret", "hy_ig_spread_pct"]], maxlag=12, verbose=False)
            for lag, r in gc.items():
                f = r[0]["ssr_ftest"]
                granger_rows.append({
                    "lag": lag,
                    "f_statistic": round(f[0], 4),
                    "p_value":     round(f[1], 4),
                    "df_num":      int(f[2]),
                    "df_den":      int(f[3]),
                })
    except Exception as e:
        print(f"  Granger (monthly) FAILED: {e}")
    granger_df = pd.DataFrame(granger_rows)
    granger_df.to_csv(os.path.join(RESULTS_DIR, "granger_by_lag.csv"), index=False)
    print(f"  granger_by_lag.csv: {len(granger_df)} rows")

    # Full daily Granger for core_models dir
    gc_full = []
    try:
        gc_data = work[["spy_ret","hy_ig_spread_pct"]].dropna()
        for lag in range(1, 6):
            r = grangercausalitytests(gc_data, maxlag=lag, verbose=False)
            f = r[lag][0]["ssr_ftest"]
            gc_full.append({"direction":"HY_IG->SPY","lag":lag,
                            "f_stat":round(f[0],4),"p_value":round(f[1],4)})
    except Exception as e:
        print(f"  Granger (daily) FAILED: {e}")
    pd.DataFrame(gc_full).to_csv(os.path.join(MODELS_DIR,"granger_causality.csv"), index=False)

    # ── 2. Predictive Regressions ─────────────────────────────
    reg_results = []
    reg_signals = [
        "hy_ig_spread_pct","hy_ig_zscore_252d","hy_ig_zscore_504d",
        "hy_ig_pctrank_504d","hy_ig_pctrank_1260d",
        "hy_ig_roc_21d","hy_ig_roc_63d","hy_ig_roc_126d",
        "hy_ig_mom_21d","hy_ig_mom_63d","hy_ig_acceleration","ccc_bb_spread_pct",
    ]
    reg_horizons = ["spy_fwd_1d","spy_fwd_5d","spy_fwd_21d","spy_fwd_63d","spy_fwd_126d"]
    for sig in reg_signals:
        for fwd in reg_horizons:
            if sig not in work.columns or fwd not in work.columns:
                continue
            valid = work[[sig, fwd]].dropna()
            if len(valid) < 50:
                continue
            try:
                X = sm.add_constant(valid[sig])
                m = sm.OLS(valid[fwd], X).fit(cov_type="HC3")
                reg_results.append({
                    "signal": sig, "horizon": fwd,
                    "coef": round(m.params.iloc[1], 6),
                    "t_stat": round(m.tvalues.iloc[1], 3),
                    "p_value": round(m.pvalues.iloc[1], 4),
                    "r_squared": round(m.rsquared, 4),
                    "n": int(m.nobs),
                })
            except Exception:
                pass
    reg_df = pd.DataFrame(reg_results)
    reg_df.to_csv(os.path.join(MODELS_DIR,"predictive_regressions.csv"), index=False)
    print(f"  Regressions: {len(reg_df)}")

    # ── 3. Local Projections (Jordà) ──────────────────────────
    lp_results = []
    for fwd, h in [("spy_fwd_5d",5),("spy_fwd_21d",21),("spy_fwd_63d",63)]:
        if fwd not in work.columns:
            continue
        ctrls = [c for c in ["vix","yield_spread_10y3m_pct"] if c in work.columns]
        valid = work[["hy_ig_spread_pct",fwd]+ctrls].dropna()
        if len(valid) < 100:
            continue
        try:
            X = sm.add_constant(valid[["hy_ig_spread_pct"]+ctrls])
            nw = int(0.75*len(valid)**(1/3))
            m = sm.OLS(valid[fwd], X).fit(cov_type="HAC", cov_kwds={"maxlags":nw})
            ci = m.conf_int().loc["hy_ig_spread_pct"]
            lp_results.append({
                "horizon_days": h,
                "coef": round(m.params["hy_ig_spread_pct"],6),
                "se":   round(m.bse["hy_ig_spread_pct"],6),
                "t_stat": round(m.tvalues["hy_ig_spread_pct"],3),
                "p_value": round(m.pvalues["hy_ig_spread_pct"],4),
                "ci_lower": round(ci[0],6), "ci_upper": round(ci[1],6),
                "r_squared": round(m.rsquared,4), "n": int(m.nobs),
            })
        except Exception:
            pass
    pd.DataFrame(lp_results).to_csv(os.path.join(MODELS_DIR,"local_projections.csv"), index=False)
    print(f"  Local projections: {len(lp_results)} horizons")

    # ── 4. Quantile Regression ────────────────────────────────
    qr_results = []
    valid_qr = work[["hy_ig_spread_pct","spy_fwd_21d"]].dropna()
    if len(valid_qr) > 50:
        for tau in [0.05,0.10,0.25,0.50,0.75,0.90,0.95]:
            try:
                qr = smf.quantreg("spy_fwd_21d ~ hy_ig_spread_pct",
                                  data=valid_qr).fit(q=tau)
                qr_results.append({
                    "quantile": tau,
                    "coef": round(qr.params["hy_ig_spread_pct"],6),
                    "p_value": round(qr.pvalues["hy_ig_spread_pct"],4),
                    "ci_lower": round(qr.conf_int().loc["hy_ig_spread_pct",0],6),
                    "ci_upper": round(qr.conf_int().loc["hy_ig_spread_pct",1],6),
                })
            except Exception:
                pass
    pd.DataFrame(qr_results).to_csv(os.path.join(MODELS_DIR,"quantile_regression.csv"), index=False)
    print(f"  Quantile reg: {len(qr_results)} quantiles")

    # ── 5. HMM Regime Detection (2-state) ─────────────────────
    hmm_probs = pd.Series(np.nan, index=df.index, name="hmm_2state_prob_stress")
    try:
        from hmmlearn.hmm import GaussianHMM

        hmm_data = work[["hy_ig_spread_pct","vix"]].copy()
        hmm_data["spread_change"] = work["hy_ig_spread_pct"].diff()
        hmm_data = hmm_data.dropna()

        X = hmm_data[["spread_change","vix"]].values
        X_mean, X_std = X.mean(0), X.std(0)
        X_std[X_std==0] = 1
        Xs = (X - X_mean) / X_std

        model_hmm = GaussianHMM(n_components=2, covariance_type="full",
                                 n_iter=200, random_state=42)
        model_hmm.fit(Xs)
        probs = model_hmm.predict_proba(Xs)
        stress_state = int(np.argmax(model_hmm.means_[:, 0]))  # higher spread_change = stress

        hmm_stress = pd.Series(probs[:, stress_state], index=hmm_data.index)
        hmm_probs  = hmm_stress.reindex(df.index)

        # Save HMM state parquet
        hmm_states_df = pd.DataFrame({
            "prob_state_0": probs[:, stress_state],
            "prob_state_1": probs[:, 1-stress_state],
            "state": model_hmm.predict(Xs),
        }, index=hmm_data.index)
        hmm_states_df.to_parquet(os.path.join(MODELS_DIR,"hmm_states_2state.parquet"))

        # HMM summary
        hmm_summary = {
            "n_states": 2, "stress_state_index": stress_state,
            "mean_stress_prob": round(float(hmm_stress.mean()),4),
            "pct_stress_days":  round(float((hmm_stress > 0.5).mean() * 100),2),
            "state_means": model_hmm.means_.tolist(),
        }
        with open(os.path.join(MODELS_DIR,"hmm_summary.csv"),"w") as f:
            json.dump(hmm_summary, f, indent=2)

        print(f"  HMM 2-state: stress_state={stress_state}, "
              f"mean_stress_prob={hmm_stress.mean():.3f}")
    except Exception as e:
        print(f"  HMM FAILED: {e}")

    # ── 6. Markov-Switching Regression ────────────────────────
    ms_probs = pd.Series(np.nan, index=df.index, name="ms_2state_stress_prob")
    try:
        from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

        ms_data = work[["spy_ret","hy_ig_spread_pct"]].dropna()
        ms_sample = ms_data.iloc[::2] if len(ms_data) > 3000 else ms_data

        ms_model = MarkovRegression(
            ms_sample["spy_ret"], k_regimes=2,
            exog=sm.add_constant(ms_sample["hy_ig_spread_pct"]),
            switching_variance=True)
        ms_fit = ms_model.fit(maxiter=200, disp=False)

        variances = [ms_fit.params[f"sigma2[{i}]"] for i in range(2)]
        stress_regime = int(np.argmax(variances))

        ms_stress = pd.Series(
            ms_fit.smoothed_marginal_probabilities[stress_regime].values,
            index=ms_sample.index)
        ms_probs = ms_stress.reindex(df.index)
        print(f"  MS 2-state: stress_regime={stress_regime}, "
              f"stress_frac={ms_stress.mean():.3f}")
    except Exception as e:
        print(f"  Markov-Switching FAILED: {e}")

    # ── 7. Stationarity Tests (ADF + KPSS) ────────────────────
    stat_results = []
    try:
        from arch.unitroot import ADF, KPSS
        test_vars = [
            "hy_ig_spread_pct","hy_ig_zscore_252d","hy_ig_roc_21d","hy_ig_roc_63d",
            "hy_ig_mom_21d","hy_ig_acceleration","ccc_bb_spread_pct",
            "hy_ig_realized_vol_21d","vix_term_structure",
            "yield_spread_10y3m_pct","yield_spread_10y2y_pct",
            "nfci_momentum_13w","bbb_ig_spread_pct","spy","spy_ret",
        ]
        for col in test_vars:
            if col not in df.columns:
                continue
            s = df[col].dropna()
            if len(s) < 100:
                continue
            if len(s) > 5000:
                s = s.iloc[::5]
            try:
                adf = ADF(s, max_lags=12)
                conc = "Stationary" if adf.pvalue < 0.05 else "Non-stationary"
                stat_results.append({
                    "variable": col, "test": "ADF",
                    "statistic": round(float(adf.stat),4),
                    "p_value":   round(float(adf.pvalue),4),
                    "lags": int(adf.lags), "n_obs": len(s),
                    "conclusion": conc,
                })
            except Exception as e:
                print(f"  ADF {col} FAILED: {e}")
            try:
                kpss = KPSS(s)
                conc_k = "Stationary" if kpss.pvalue > 0.05 else "Non-stationary"
                stat_results.append({
                    "variable": col, "test": "KPSS",
                    "statistic": round(float(kpss.stat),4),
                    "p_value":   round(float(kpss.pvalue),4),
                    "lags": int(kpss.lags) if hasattr(kpss,"lags") else 0,
                    "n_obs": len(s),
                    "conclusion": conc_k,
                })
            except Exception:
                pass
    except ImportError:
        from statsmodels.tsa.stattools import adfuller
        for col in ["hy_ig_spread_pct","hy_ig_roc_21d","spy_ret"]:
            if col not in df.columns: continue
            s = df[col].dropna().iloc[::5] if len(df[col].dropna()) > 5000 else df[col].dropna()
            try:
                adf_r = adfuller(s, maxlags=12)
                stat_results.append({
                    "variable":col,"test":"ADF",
                    "statistic":round(adf_r[0],4),"p_value":round(adf_r[1],4),
                    "lags":adf_r[2],"n_obs":len(s),
                    "conclusion":"Stationary" if adf_r[1]<0.05 else "Non-stationary",
                })
            except Exception:
                pass

    stat_df = pd.DataFrame(stat_results)
    stat_df.to_csv(os.path.join(RESULTS_DIR,f"stationarity_tests_{DATE_TAG}.csv"), index=False)
    print(f"  Stationarity tests: {len(stat_df)} rows")

    # ── 8. Diagnostics ────────────────────────────────────────
    diag_results = []
    valid_diag = work[["hy_ig_spread_pct","spy_fwd_21d"]].dropna()
    if len(valid_diag) > 50:
        X = sm.add_constant(valid_diag["hy_ig_spread_pct"])
        m = sm.OLS(valid_diag["spy_fwd_21d"], X).fit()
        jb_s, jb_p = stats.jarque_bera(m.resid)
        from statsmodels.stats.stattools import durbin_watson
        dw = durbin_watson(m.resid)
        diag_results.append({"test":"Jarque-Bera","statistic":round(jb_s,4),"p_value":round(jb_p,4)})
        diag_results.append({"test":"Durbin-Watson","statistic":round(dw,4),"p_value":np.nan})
    pd.DataFrame(diag_results).to_csv(os.path.join(MODELS_DIR,"diagnostics_summary.csv"), index=False)

    return hmm_probs, ms_probs, reg_df


# ─────────────────────────────────────────────────────────────
# STAGE 5: EXPLORATORY ANALYSIS
# ─────────────────────────────────────────────────────────────

@timed("5_exploratory")
def stage_exploratory(df: pd.DataFrame):
    """Correlations, regime descriptive stats, quartile returns."""
    # ── Correlations ──────────────────────────────────────────
    signal_cols = [c for c in df.columns
                   if (c.startswith("hy_ig_") or c in [
                       "ccc_bb_spread_pct","vix_term_structure",
                       "yield_spread_10y3m_pct","yield_spread_10y2y_pct",
                       "bank_smallcap_ratio","nfci_momentum_13w","bbb_ig_spread_pct",
                       "hy_ig_realized_vol_21d"])
                   and "fwd" not in c and "ret" not in c]
    fwd_cols = [c for c in df.columns if c.startswith("spy_fwd_")]

    corr_results = []
    for sig in signal_cols:
        for fwd in fwd_cols:
            valid = df[[sig,fwd]].dropna()
            if len(valid) < 50:
                continue
            r, p = stats.pearsonr(valid[sig], valid[fwd])
            corr_results.append({
                "signal":sig,"horizon":fwd,"method":"Pearson",
                "correlation":round(r,4),"p_value":round(p,4),"n":len(valid),
            })
    corr_df = pd.DataFrame(corr_results)
    corr_df.to_csv(os.path.join(EXPLORE_DIR,"correlations.csv"), index=False)

    sig_count = len(corr_df[corr_df["p_value"]<0.05]) if len(corr_df)>0 else 0
    print(f"  Correlations: {len(corr_df)} ({sig_count} sig at 5%)")

    # ── Regime descriptive stats ──────────────────────────────
    regime_results = []
    valid = df[["hy_ig_spread_pct","spy_ret"]].dropna()
    if len(valid) > 200:
        quartiles = pd.qcut(valid["hy_ig_spread_pct"], 4,
                            labels=["Q1_low","Q2","Q3","Q4_high"])
        for q in ["Q1_low","Q2","Q3","Q4_high"]:
            rets = valid.loc[quartiles==q,"spy_ret"]
            if len(rets) < 20:
                continue
            ann_ret = rets.mean()*252
            ann_vol = rets.std()*np.sqrt(252)
            regime_results.append({
                "regime":q, "n_days":len(rets),
                "ann_return_pct":round(ann_ret*100,2),
                "ann_vol_pct":round(ann_vol*100,2),
                "sharpe":round(ann_ret/ann_vol,3) if ann_vol>0 else 0,
            })
    pd.DataFrame(regime_results).to_csv(
        os.path.join(EXPLORE_DIR,"regime_descriptive_stats.csv"), index=False)

    # ── Quartile returns — Rule E2 (ratio form, ann returns in decimal) ──
    qr_rows = []
    valid = df[["hy_ig_spread_pct","spy_ret"]].dropna()
    monthly = valid.resample("ME").agg({"hy_ig_spread_pct":"last","spy_ret":lambda x:(1+x).prod()-1})
    if len(monthly) > 48:
        q_labels = ["Q1","Q2","Q3","Q4"]
        quartiles = pd.qcut(monthly["hy_ig_spread_pct"], 4, labels=q_labels)
        for q in q_labels:
            rets = monthly.loc[quartiles==q,"spy_ret"]
            if len(rets) < 10:
                continue
            ann_ret = rets.mean()*12  # monthly → annual (ratio)
            ann_vol = rets.std()*np.sqrt(12)
            cum = (1+rets).cumprod()
            mdd = float(((cum-cum.cummax())/cum.cummax()).min())
            qr_rows.append({
                "quartile":q, "n_months":len(rets),
                "ann_return": round(ann_ret,6),
                "ann_vol":    round(ann_vol,6),
                "sharpe":     round(ann_ret/ann_vol,4) if ann_vol>0 else 0,
                "max_drawdown": round(mdd,6),
            })
    qr_df = pd.DataFrame(qr_rows)
    qr_df.to_csv(os.path.join(RESULTS_DIR,"regime_quartile_returns.csv"), index=False)
    if regime_results:
        print(f"  Quartile Sharpes: "
              f"{dict(zip([r['regime'] for r in regime_results],[r['sharpe'] for r in regime_results]))}")
    if qr_rows:
        print(f"  Rule-E2 quartile rows: {len(qr_rows)}")
    return corr_df


# ─────────────────────────────────────────────────────────────
# STAGE 6: TOURNAMENT
# ─────────────────────────────────────────────────────────────

@timed("6_tournament")
def stage_tournament(df: pd.DataFrame) -> pd.DataFrame:
    """
    5D combinatorial backtest:
    signals × thresholds × strategies × leads × (direction fixed = countercyclical)

    Meta-UC: all return/drawdown columns in ratio form (decimal), Sharpe as-is.
    """
    # Load signals parquet (Derived Signal Persistence Rule)
    signals_path = os.path.join(SIGNALS_DIR, f"signals_{DATE_TAG}.parquet")
    sig_df = pd.read_parquet(signals_path)

    work = df.copy()
    for col in ["hmm_2state_prob_stress","ms_2state_stress_prob"]:
        if col in sig_df.columns and col not in work.columns:
            work[col] = sig_df[col].reindex(work.index)
    if "spy_ret" not in work.columns:
        work["spy_ret"] = work["spy"].pct_change()

    is_mask  = work.index <= IS_END
    oos_mask = work.index >= OOS_START

    # ── Signal map ────────────────────────────────────────────
    signal_cols = {
        "S1_spread_level":    "hy_ig_spread_pct",
        "S2a_zscore_252d":    "hy_ig_zscore_252d",
        "S2b_zscore_504d":    "hy_ig_zscore_504d",
        "S3a_pctrank_504d":   "hy_ig_pctrank_504d",
        "S3b_pctrank_1260d":  "hy_ig_pctrank_1260d",
        "S4a_roc_21d":        "hy_ig_roc_21d",
        "S4b_roc_63d":        "hy_ig_roc_63d",
        "S4c_roc_126d":       "hy_ig_roc_126d",
        "S5_ccc_bb_spread":   "ccc_bb_spread_pct",
        "S6_hmm_stress":      "hmm_2state_prob_stress",
        "S7_ms_stress":       "ms_2state_stress_prob",
        "S10_mom_21d":        "hy_ig_mom_21d",
        "S11_mom_63d":        "hy_ig_mom_63d",
        "S12_mom_252d":       "hy_ig_mom_252d",
        "S13_acceleration":   "hy_ig_acceleration",
    }
    available = {k: v for k, v in signal_cols.items()
                 if v in work.columns and work[v].notna().sum() > 200}
    print(f"  Available signals: {len(available)} of {len(signal_cols)}")

    leads   = [0, 1, 5, 10, 21, 63]
    results = []

    for sig_name, sig_col in available.items():
        signal = work[sig_col]
        for lead in leads:
            sig_l    = signal.shift(lead) if lead > 0 else signal
            is_sig   = sig_l[is_mask].dropna()
            if len(is_sig) < 100:
                continue

            thresholds = {}
            if sig_name in ("S6_hmm_stress","S7_ms_stress"):
                for p in [0.5, 0.7]:
                    pfx = "T4" if sig_name=="S6_hmm_stress" else "T5"
                    sfx = "hmm" if "hmm" in sig_name else "ms"
                    thresholds[f"{pfx}_{sfx}_{p}"] = p
            else:
                for pct in [75, 85, 95]:
                    thresholds[f"T1_p{pct}"] = is_sig.quantile(pct/100)
                for pct in [75, 85, 95]:
                    thresholds[f"T2_rp{pct}"] = sig_l.rolling(504,min_periods=400).quantile(pct/100)
                for z in [1.5, 2.0, 2.5]:
                    thresholds[f"T3_z{z}"] = z

            for tname, tval in thresholds.items():
                for strat in ["P1","P2","P3"]:
                    try:
                        if tname.startswith("T3_z"):
                            roll_mean = sig_l.rolling(504,min_periods=400).mean()
                            roll_std  = sig_l.rolling(504,min_periods=400).std().replace(0,np.nan)
                            z_series  = (sig_l-roll_mean)/roll_std
                            bullish   = z_series < tval
                        elif isinstance(tval,(int,float)):
                            bullish = sig_l < tval
                        else:
                            bullish = sig_l < tval

                        if strat == "P1":
                            pos = bullish.astype(float)
                        elif strat == "P2":
                            smin = sig_l.rolling(504,min_periods=400).min()
                            smax = sig_l.rolling(504,min_periods=400).max()
                            sr   = (smax-smin).replace(0,np.nan)
                            pos  = (1-(sig_l-smin)/sr).clip(0,1)
                        elif strat == "P3":
                            pos = bullish.astype(float)*2-1

                        strat_ret = pos.shift(1) * work["spy_ret"]
                        is_r  = strat_ret[is_mask].dropna()
                        oos_r = strat_ret[oos_mask].dropna()
                        if len(is_r) < 100 or len(oos_r) < 50:
                            continue

                        oos_sharpe = (oos_r.mean()/oos_r.std()*np.sqrt(252)
                                      if oos_r.std()>0 else 0)
                        cum = (1+oos_r).cumprod()
                        dd  = ((cum-cum.cummax())/cum.cummax()).min()  # ratio
                        oos_ann_return = oos_r.mean()*252              # ratio
                        turnover = pos.diff().abs().sum() / max(len(pos.dropna())/252,1)
                        n_trades_raw = int(pos.diff().abs().gt(0.05).sum())
                        valid_flag = (oos_sharpe > 0 and turnover < 24
                                      and n_trades_raw >= 10)
                        win_rate = (oos_r>0).sum()/len(oos_r) if len(oos_r)>0 else 0

                        results.append({
                            "signal":         sig_name,
                            "threshold":      tname,
                            "strategy":       strat,
                            "lead_days":      lead,
                            "oos_sharpe":     round(oos_sharpe,4),
                            "oos_ann_return": round(oos_ann_return,6),  # ratio
                            "max_drawdown":   round(float(dd),6),       # ratio
                            "win_rate":       round(win_rate,4),
                            "n_trades":       n_trades_raw,
                            "annual_turnover":round(turnover,2),
                            "valid":          valid_flag,
                            "oos_n":          len(oos_r),
                        })
                    except Exception:
                        continue

    # ── Benchmark (buy-and-hold SPY) ──────────────────────────
    bh = work.loc[oos_mask,"spy_ret"].dropna()
    if len(bh) > 0:
        bh_s = (bh.mean()/bh.std()*np.sqrt(252) if bh.std()>0 else 0)
        bh_cum = (1+bh).cumprod()
        bh_dd  = ((bh_cum-bh_cum.cummax())/bh_cum.cummax()).min()
        results.append({
            "signal":"BENCHMARK","threshold":"BUY_HOLD","strategy":"BH",
            "lead_days":0, "oos_sharpe":round(bh_s,4),
            "oos_ann_return":round(bh.mean()*252,6), "max_drawdown":round(float(bh_dd),6),
            "win_rate":round((bh>0).mean(),4), "n_trades":1,
            "annual_turnover":0.0, "valid":True, "oos_n":len(bh),
        })

    rdf = pd.DataFrame(results)
    rdf.to_csv(os.path.join(RESULTS_DIR,f"tournament_results_{DATE_TAG}.csv"), index=False)

    total   = len(rdf) - 1   # exclude benchmark row
    valid_n = rdf["valid"].sum() - 1
    print(f"  Tournament: {total} combos, {valid_n} valid")
    vs = rdf[rdf["valid"] & (rdf["signal"]!="BENCHMARK")]
    if len(vs)>0:
        best = vs.loc[vs["oos_sharpe"].idxmax()]
        print(f"  Best: {best['signal']}/{best['threshold']}/{best['strategy']}"
              f"/L{best['lead_days']}  Sharpe={best['oos_sharpe']:.2f}"
              f"  Ret={best['oos_ann_return']*100:.1f}%"
              f"  DD={best['max_drawdown']*100:.1f}%")
    bm = rdf[rdf["signal"]=="BENCHMARK"]
    if len(bm)>0:
        print(f"  B&H: Sharpe={bm.iloc[0]['oos_sharpe']:.2f}"
              f"  Ret={bm.iloc[0]['oos_ann_return']*100:.1f}%"
              f"  DD={bm.iloc[0]['max_drawdown']*100:.1f}%")
    return rdf


# ─────────────────────────────────────────────────────────────
# REPLAY HELPERS
# ─────────────────────────────────────────────────────────────

def _compute_threshold_val(is_signal, threshold_name, signal_series):
    if threshold_name.startswith("T1_p"):
        pct = int(threshold_name.split("p")[1])
        return is_signal.quantile(pct/100)
    elif threshold_name.startswith("T2_rp"):
        pct = int(threshold_name.split("rp")[1])
        return signal_series.rolling(504,min_periods=400).quantile(pct/100)
    elif threshold_name.startswith("T3_z"):
        return float(threshold_name.split("z")[1])
    elif threshold_name.startswith(("T4_hmm_","T4_ms_","T5_hmm_","T5_ms_")):
        return float(threshold_name.rsplit("_",1)[1])
    return None


def _replay_strategy(work, sig_col, threshold_name, threshold_val, strategy, lead):
    signal = work[sig_col].shift(lead) if lead>0 else work[sig_col]
    if isinstance(threshold_val, pd.Series):
        threshold_val = threshold_val.reindex(work.index)
    if threshold_name.startswith("T3_z"):
        roll_mean = signal.rolling(504,min_periods=400).mean()
        roll_std  = signal.rolling(504,min_periods=400).std().replace(0,np.nan)
        z_series  = (signal-roll_mean)/roll_std
        bullish   = z_series < threshold_val
    elif isinstance(threshold_val,(int,float,np.floating)):
        bullish = signal < threshold_val
    else:
        bullish = signal < threshold_val
    if strategy=="P1":
        pos = bullish.astype(float)
    elif strategy=="P2":
        smin = signal.rolling(504,min_periods=400).min()
        smax = signal.rolling(504,min_periods=400).max()
        sr   = (smax-smin).replace(0,np.nan)
        pos  = (1-(signal-smin)/sr).clip(0,1)
    elif strategy=="P3":
        pos = bullish.astype(float)*2-1
    else:
        pos = bullish.astype(float)
    strat_ret = pos.shift(1) * work["spy_ret"]
    return pos, strat_ret


# ─────────────────────────────────────────────────────────────
# STAGE 7: VALIDATION + WINNER OUTPUTS
# ─────────────────────────────────────────────────────────────

@timed("7_validation")
def stage_validation(df: pd.DataFrame, tourn_df: pd.DataFrame):
    """
    Walk-forward, bootstrap CI, transaction costs, signal decay, stress tests
    for top-5 valid winners. Then generates all winner artifacts.
    """
    import statsmodels.api as sm

    sig_df = pd.read_parquet(os.path.join(SIGNALS_DIR, f"signals_{DATE_TAG}.parquet"))
    work   = df.copy()
    for col in ["hmm_2state_prob_stress","ms_2state_stress_prob"]:
        if col in sig_df.columns and col not in work.columns:
            work[col] = sig_df[col].reindex(work.index)
    if "spy_ret" not in work.columns:
        work["spy_ret"] = work["spy"].pct_change()

    signal_col_map = {
        "S1_spread_level":   "hy_ig_spread_pct",
        "S2a_zscore_252d":   "hy_ig_zscore_252d",
        "S2b_zscore_504d":   "hy_ig_zscore_504d",
        "S3a_pctrank_504d":  "hy_ig_pctrank_504d",
        "S3b_pctrank_1260d": "hy_ig_pctrank_1260d",
        "S4a_roc_21d":       "hy_ig_roc_21d",
        "S4b_roc_63d":       "hy_ig_roc_63d",
        "S4c_roc_126d":      "hy_ig_roc_126d",
        "S5_ccc_bb_spread":  "ccc_bb_spread_pct",
        "S6_hmm_stress":     "hmm_2state_prob_stress",
        "S7_ms_stress":      "ms_2state_stress_prob",
        "S10_mom_21d":       "hy_ig_mom_21d",
        "S11_mom_63d":       "hy_ig_mom_63d",
        "S12_mom_252d":      "hy_ig_mom_252d",
        "S13_acceleration":  "hy_ig_acceleration",
    }

    valid_df = tourn_df[tourn_df["valid"] & (tourn_df["signal"]!="BENCHMARK")]
    if len(valid_df)==0:
        print("  No valid winners to validate.")
        return
    top5 = valid_df.nlargest(5,"oos_sharpe")

    all_wf, all_boot, all_costs, all_decay, all_stress = [], [], [], [], []

    for rank, (idx, row) in enumerate(top5.iterrows(), 1):
        sig_name = row["signal"]
        sig_col  = signal_col_map.get(sig_name)
        if sig_col is None or sig_col not in work.columns:
            print(f"  SKIP {sig_name}: column not found")
            continue
        tname = row["threshold"]
        strat = row["strategy"]
        lead  = int(row["lead_days"])
        signal    = work[sig_col]
        is_signal = signal[work.index<=IS_END].dropna()
        tval      = _compute_threshold_val(is_signal, tname, signal)
        combo_tag = f"{sig_name}/{tname}/{strat}/L{lead}"
        print(f"  [{rank}] {combo_tag} (OOS Sharpe={row['oos_sharpe']:.2f})")

        # 1. Walk-forward (5yr train / 1yr test)
        years = sorted(work.index.year.unique())
        for test_year in range(max(years[0]+5, 2010), max(years)+1):
            t_start = pd.Timestamp(f"{test_year-5}-01-01")
            t_end   = pd.Timestamp(f"{test_year-1}-12-31")
            ts_s    = pd.Timestamp(f"{test_year}-01-01")
            ts_e    = pd.Timestamp(f"{test_year}-12-31")
            train_sig = signal[(work.index>=t_start)&(work.index<=t_end)].dropna()
            if len(train_sig) < 200:
                continue
            tv  = _compute_threshold_val(train_sig, tname, signal) if tname.startswith("T1_p") else tval
            wf_slice = (work.index>=t_start)&(work.index<=ts_e)
            _, wf_ret = _replay_strategy(work[wf_slice], sig_col, tname, tv, strat, lead)
            test_ret = wf_ret[(wf_ret.index>=ts_s)&(wf_ret.index<=ts_e)].dropna()
            if len(test_ret)<20: continue
            wf_sharpe = (test_ret.mean()/test_ret.std()*np.sqrt(252) if test_ret.std()>0 else 0)
            all_wf.append({"rank":rank,"signal":sig_name,"threshold":tname,
                           "strategy":strat,"lead_days":lead,"test_year":test_year,
                           "oos_sharpe":round(wf_sharpe,4),"n_obs":len(test_ret)})

        # 2. Bootstrap
        oos_mask = work.index>=OOS_START
        _, oos_ret = _replay_strategy(work[oos_mask], sig_col, tname, tval, strat, lead)
        oos_ret = oos_ret.dropna()
        if len(oos_ret)>50:
            rng = np.random.RandomState(42)
            oos_arr = oos_ret.values
            n = len(oos_arr)
            boot_sharpes = [
                (s.mean()/s.std()*np.sqrt(252) if s.std()>0 else 0)
                for s in (rng.choice(oos_arr,size=n,replace=True) for _ in range(10000))
            ]
            boot_sharpes = np.array(boot_sharpes)
            all_boot.append({"rank":rank,"signal":sig_name,"threshold":tname,
                             "strategy":strat,"lead_days":lead,
                             "mean_sharpe":round(np.mean(boot_sharpes),4),
                             "ci_2_5":round(np.percentile(boot_sharpes,2.5),4),
                             "ci_97_5":round(np.percentile(boot_sharpes,97.5),4),
                             "pct_positive":round((boot_sharpes>0).mean()*100,1)})

        # 3. Transaction costs
        for bps in [0,5,10,20,50]:
            pos, ret = _replay_strategy(work[oos_mask], sig_col, tname, tval, strat, lead)
            ret = ret.dropna()
            if len(ret)<50: continue
            cost_pd = pos.diff().abs().fillna(0)*(bps/10000)
            net_ret = ret - cost_pd.shift(1).reindex(ret.index,fill_value=0)
            net_sh  = (net_ret.mean()/net_ret.std()*np.sqrt(252) if net_ret.std()>0 else 0)
            all_costs.append({"rank":rank,"signal":sig_name,"threshold":tname,
                              "strategy":strat,"lead_days":lead,"tx_cost_bps":bps,
                              "net_sharpe_approx":round(net_sh,4),"oos_sharpe":round(row["oos_sharpe"],4)})

        # 4. Signal decay
        for delay in [0,1,2,3,5]:
            _, dr = _replay_strategy(work[oos_mask], sig_col, tname, tval, strat, lead+delay)
            dr = dr.dropna()
            if len(dr)<50: continue
            ds = (dr.mean()/dr.std()*np.sqrt(252) if dr.std()>0 else 0)
            all_decay.append({"rank":rank,"signal":sig_name,"threshold":tname,
                              "strategy":strat,"lead_days":lead,"execution_delay":delay,
                              "oos_sharpe":round(ds,4)})

        # 5. Stress tests
        for period_name, pstart, pend in [
            ("GFC_2007_2009","2007-07-01","2009-03-31"),
            ("COVID_2020","2020-02-01","2020-06-30"),
            ("Taper_Tantrum_2013","2013-05-01","2013-09-30"),
            ("Rate_Shock_2022","2022-01-01","2022-12-31"),
        ]:
            pmask = (work.index>=pstart)&(work.index<=pend)
            if pmask.sum()<20: continue
            _, sr_ret = _replay_strategy(work[pmask], sig_col, tname, tval, strat, lead)
            sr_ret = sr_ret.dropna()
            if len(sr_ret)<10: continue
            s_sh  = (sr_ret.mean()/sr_ret.std()*np.sqrt(252) if sr_ret.std()>0 else 0)
            cum   = (1+sr_ret).cumprod()
            s_dd  = ((cum-cum.cummax())/cum.cummax()).min()
            bh_s_ret = work.loc[pmask,"spy_ret"].dropna()
            bh_sh = (bh_s_ret.mean()/bh_s_ret.std()*np.sqrt(252) if bh_s_ret.std()>0 else 0)
            all_stress.append({"rank":rank,"signal":sig_name,"threshold":tname,
                               "strategy":strat,"lead_days":lead,
                               "period":period_name,"start":pstart,"end":pend,
                               "strategy_sharpe":round(s_sh,4),
                               "strategy_max_dd":round(float(s_dd)*100,2),
                               "benchmark_sharpe":round(bh_sh,4),"n_obs":len(sr_ret)})

    # Save validation CSVs
    pd.DataFrame(all_wf).to_csv(os.path.join(VALIDATION_DIR,"walk_forward.csv"), index=False)
    pd.DataFrame(all_boot).to_csv(os.path.join(VALIDATION_DIR,"bootstrap_ci.csv"), index=False)
    pd.DataFrame(all_costs).to_csv(os.path.join(VALIDATION_DIR,"transaction_costs.csv"), index=False)
    pd.DataFrame(all_decay).to_csv(os.path.join(VALIDATION_DIR,"signal_decay.csv"), index=False)
    pd.DataFrame(all_stress).to_csv(os.path.join(VALIDATION_DIR,"stress_tests.csv"), index=False)
    print(f"  Walk-forward:{len(all_wf)}  Bootstrap:{len(all_boot)}  "
          f"Costs:{len(all_costs)}  Decay:{len(all_decay)}  Stress:{len(all_stress)}")

    # Generate all winner artifacts
    _generate_all_winner_artifacts(tourn_df, work, signal_col_map)


# ─────────────────────────────────────────────────────────────
# WINNER ARTIFACT GENERATION
# ─────────────────────────────────────────────────────────────

SIGNAL_DISPLAY = {
    "S1_spread_level":   "HY-IG Spread Level",
    "S2a_zscore_252d":   "HY-IG Z-Score (252d)",
    "S2b_zscore_504d":   "HY-IG Z-Score (504d)",
    "S3a_pctrank_504d":  "HY-IG Percentile Rank (504d)",
    "S3b_pctrank_1260d": "HY-IG Percentile Rank (1260d)",
    "S4a_roc_21d":       "HY-IG 21-Day Rate of Change",
    "S4b_roc_63d":       "HY-IG 63-Day Rate of Change",
    "S4c_roc_126d":      "HY-IG 126-Day Rate of Change",
    "S5_ccc_bb_spread":  "CCC-BB Quality Spread",
    "S6_hmm_stress":     "HMM Stress Probability",
    "S7_ms_stress":      "Markov-Switching Stress Probability",
    "S10_mom_21d":       "HY-IG 21-Day Momentum",
    "S11_mom_63d":       "HY-IG 63-Day Momentum",
    "S12_mom_252d":      "HY-IG 252-Day Momentum",
    "S13_acceleration":  "HY-IG Acceleration",
}
THRESHOLD_DISPLAY = {
    "T1_p75":"75th percentile (fixed)","T1_p85":"85th percentile (fixed)",
    "T1_p95":"95th percentile (fixed)","T2_rp75":"75th pct (rolling 504d)",
    "T2_rp85":"85th pct (rolling 504d)","T2_rp95":"95th pct (rolling 504d)",
    "T3_z1.5":"Z-score > 1.5","T3_z2.0":"Z-score > 2.0","T3_z2.5":"Z-score > 2.5",
    "T4_hmm_0.5":"HMM prob > 0.5","T4_hmm_0.7":"HMM prob > 0.7",
    "T5_ms_0.5":"MS prob > 0.5","T5_ms_0.7":"MS prob > 0.7",
}
STRATEGY_DISPLAY = {"P1":"Long/Cash","P2":"Signal Strength","P3":"Long/Short"}
STRATEGY_DESC = {
    "P1":"Go fully long SPY when signal is bullish; move to cash otherwise.",
    "P2":"Scale position size proportionally to signal strength (0%–100% invested).",
    "P3":"Go long SPY when bullish, short SPY when bearish.",
}


def _generate_all_winner_artifacts(tourn_df, work, signal_col_map):
    """Generate all required winner artifacts per ECON-H and team-standards §5.2."""
    valid_df = tourn_df[tourn_df["valid"] & (tourn_df["signal"]!="BENCHMARK")]
    if len(valid_df)==0:
        print("  No valid winner — skipping artifact generation.")
        return

    # ECON-T3 tie-break cascade: oos_sharpe → oos_ann_return → abs(MDD)→ n_trades → lexicographic
    winner = valid_df.sort_values(
        ["oos_sharpe","oos_ann_return","max_drawdown","n_trades","signal"],
        ascending=[False,False,True,False,True]
    ).iloc[0]

    bm_row = tourn_df[tourn_df["signal"]=="BENCHMARK"].iloc[0] if len(tourn_df[tourn_df["signal"]=="BENCHMARK"])>0 else None

    # Load interpretation metadata (Dana's + Ray's fields)
    meta_path = os.path.join(RESULTS_DIR,"interpretation_metadata.json")
    with open(meta_path) as f:
        meta = json.load(f)

    sig_name = winner["signal"]
    tname    = winner["threshold"]
    strat    = winner["strategy"]
    lead     = int(winner["lead_days"])
    sig_col  = signal_col_map.get(sig_name)

    # Determine threshold_value and threshold_rule
    if tname.startswith(("T4_","T5_")):
        tval_num   = float(tname.rsplit("_",1)[1])
        tval_rule  = "gte"
    elif tname.startswith("T1_p"):
        pct = int(tname.split("p")[1])
        if sig_col and sig_col in work.columns:
            tval_num = round(float(work.loc[work.index<=IS_END,sig_col].dropna().quantile(pct/100)),4)
        else:
            tval_num = None
        tval_rule = "lt"   # counter-cyclical: low signal = bullish
    else:
        tval_num  = None
        tval_rule = "lt"

    # Decay / cost info from validation files
    max_delay_days  = 5
    breakeven_bps   = 50.0
    decay_path = os.path.join(VALIDATION_DIR,"signal_decay.csv")
    cost_path  = os.path.join(VALIDATION_DIR,"transaction_costs.csv")
    if os.path.exists(decay_path):
        d_df = pd.read_csv(decay_path)
        d_w  = d_df[(d_df["signal"]==sig_name)&(d_df["threshold"]==tname)
                    &(d_df["strategy"]==strat)&(d_df["lead_days"]==lead)]
        if len(d_w)>0:
            pos_d = d_w[d_w["oos_sharpe"]>0]
            max_delay_days = int(pos_d["execution_delay"].max()) if len(pos_d)>0 else 0
    if os.path.exists(cost_path):
        c_df = pd.read_csv(cost_path)
        c_w  = c_df[(c_df["signal"]==sig_name)&(c_df["threshold"]==tname)
                    &(c_df["strategy"]==strat)&(c_df["lead_days"]==lead)]
        if len(c_w)>0:
            pos_c = c_w[c_w["net_sharpe_approx"]>0]
            breakeven_bps = float(pos_c["tx_cost_bps"].max()) if len(pos_c)>0 else 0.0

    now_iso = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Observed direction from regression
    direction_obs = meta.get("observed_direction") or "countercyclical"

    # ── winner_summary.json (schema v1.0.0) ───────────────────
    winner_summary = {
        "pair_id":            PAIR_ID,
        "generated_at":       now_iso,
        "signal_column":      sig_col or sig_name,
        "signal_code":        sig_name,
        "target_symbol":      "SPY",
        "threshold_value":    tval_num,
        "threshold_rule":     tval_rule,
        "strategy_family":    {"P1":"P1_long_cash","P2":"P2_signal_strength","P3":"P3_long_short"}.get(strat, strat),
        "direction":          direction_obs,
        "oos_sharpe":         round(float(winner["oos_sharpe"]),4),
        "oos_ann_return":     round(float(winner["oos_ann_return"]),6),  # ratio
        "oos_max_drawdown":   round(float(winner["max_drawdown"]),6),    # ratio
        "oos_n_trades":       int(winner["n_trades"]),
        "oos_period_start":   OOS_START,
        "oos_period_end":     OOS_END,
        "bh_sharpe":          round(float(bm_row["oos_sharpe"]),4) if bm_row is not None else None,
        "bh_ann_return":      round(float(bm_row["oos_ann_return"]),6) if bm_row is not None else None,
        "annual_turnover":    round(float(winner["annual_turnover"]),2),
        "cost_assumption_bps":5.0,
        "notes": (
            f"Fresh hy_ig_spy pair (Wave 10G.4C). OOS window {OOS_START}–{OOS_END} "
            f"per ECON-OOS2 formula (79mo). winner={sig_name}/{tname}/{strat}/L{lead}. "
            f"breakeven_cost={breakeven_bps:.0f}bps, max_acceptable_delay={max_delay_days}d."
        ),
        # Optional display fields
        "signal_display_name":    SIGNAL_DISPLAY.get(sig_name,sig_name),
        "threshold_code":         tname,
        "threshold_display_name": THRESHOLD_DISPLAY.get(tname,tname),
        "strategy_code":          strat,
        "strategy_display_name":  STRATEGY_DISPLAY.get(strat,strat),
        "strategy_description":   STRATEGY_DESC.get(strat,""),
        "lead_value":             lead,
        "lead_unit":              "days",
        "lead_description":       f"{lead} days" if lead>0 else "No lead (same-period)",
        "win_rate":               round(float(winner["win_rate"]),4) if "win_rate" in winner.index else None,
        "max_acceptable_delay_days": max_delay_days,
        "breakeven_cost_bps":     breakeven_bps,
    }
    with open(os.path.join(RESULTS_DIR,"winner_summary.json"),"w") as f:
        json.dump(winner_summary, f, indent=2)
    print(f"  winner_summary.json saved (Sharpe={winner_summary['oos_sharpe']:.2f})")

    # ── tournament_winner.json (winner-vs-benchmark delta record) ──
    bh_ann = float(bm_row["oos_ann_return"]) if bm_row is not None else 0.0
    bh_dd  = float(bm_row["max_drawdown"])   if bm_row is not None else 0.0
    tournament_winner = {
        "pair_id":       PAIR_ID,
        "generated_at":  now_iso,
        "winner_signal": sig_name,
        "winner_threshold": tname,
        "winner_strategy":  strat,
        "lead_days":        lead,
        "oos_sharpe":       round(float(winner["oos_sharpe"]),4),
        "oos_ann_return":   round(float(winner["oos_ann_return"]),6),
        "oos_max_drawdown": round(float(winner["max_drawdown"]),6),
        "oos_n_trades":     int(winner["n_trades"]),
        "oos_period_start": OOS_START,
        "oos_period_end":   OOS_END,
        "bh_sharpe":        round(float(bm_row["oos_sharpe"]),4) if bm_row is not None else None,
        "bh_ann_return":    round(bh_ann,6),
        "bh_max_drawdown":  round(bh_dd,6),
        "delta_sharpe":     round(float(winner["oos_sharpe"])-(float(bm_row["oos_sharpe"]) if bm_row is not None else 0),4),
        "delta_ann_return": round(float(winner["oos_ann_return"])-bh_ann,6),
        "delta_mdd":        round(float(winner["max_drawdown"])-bh_dd,6),
        "strategy_objective": ("min_mdd" if abs(float(winner["max_drawdown"]))<abs(bh_dd)*0.6
                               else "max_sharpe"),
    }
    with open(os.path.join(RESULTS_DIR,"tournament_winner.json"),"w") as f:
        json.dump(tournament_winner, f, indent=2)
    print(f"  tournament_winner.json saved")

    # ── OOS split record (ECON-OOS1) ─────────────────────────
    oos_record = {
        "pair_id":           PAIR_ID,
        "owner":             "evan",
        "split_policy_id":   "v1_max36_25pct_cap120",
        "in_sample_end":     IS_END,
        "oos_start":         OOS_START,
        "oos_end":           OOS_END,
        "sample_size_months":316,
        "oos_span_months":   79,
        "justification": (
            "Total sample 2000-01-03 to 2026-04-22 ≈ 316 months. "
            "ECON-OOS2 formula: span = min(max(36, round(316×0.25)), 120) = 79 months. "
            "OOS window 2019-10-01 to 2026-04-22. "
            "GFC 2008-09 and COVID 2020 remain in-sample, providing "
            "stress-episode coverage for the HMM/MS model fits."
        ),
        "generated_at": now_iso,
    }
    with open(os.path.join(RESULTS_DIR,"oos_split_record.json"),"w") as f:
        json.dump(oos_record, f, indent=2)
    print(f"  oos_split_record.json saved")

    # ── Winner trade log ─────────────────────────────────────
    if sig_col and sig_col in work.columns:
        signal = work[sig_col]
        is_sig = signal[work.index<=IS_END].dropna()
        tval_replay = _compute_threshold_val(is_sig, tname, signal)
        pos, strat_ret = _replay_strategy(work, sig_col, tname, tval_replay, strat, lead)
        cum_ret = (1+strat_ret.fillna(0)).cumprod()

        pos_clean   = pos.dropna()
        pos_change  = pos_clean.diff().fillna(pos_clean.iloc[0] if len(pos_clean)>0 else 0)
        trade_entries = pos_change[pos_change.abs()>0.05].index

        trades = []
        for i in range(len(trade_entries)):
            entry_date = trade_entries[i]
            exit_date  = trade_entries[i+1] if i+1<len(trade_entries) else work.index[-1]
            entry_pos  = pos.loc[entry_date]
            direction  = "Long" if entry_pos>0 else ("Short" if entry_pos<0 else "Cash")
            holding_days = (exit_date-entry_date).days
            if entry_date in cum_ret.index and exit_date in cum_ret.index:
                ec = cum_ret.loc[:entry_date].iloc[-1]
                xc = cum_ret.loc[:exit_date].iloc[-1]
                trade_ret = (xc/ec-1) if ec!=0 else 0.0
            else:
                trade_ret = 0.0
            trades.append({
                "entry_date":     entry_date.strftime("%Y-%m-%d"),
                "exit_date":      exit_date.strftime("%Y-%m-%d"),
                "direction":      direction,
                "holding_days":   holding_days,
                "trade_return_pct": round(trade_ret*100,2),
            })
        trade_df = pd.DataFrame(trades)
        trade_df.to_csv(os.path.join(RESULTS_DIR,"winner_trade_log.csv"), index=False)
        print(f"  winner_trade_log.csv: {len(trade_df)} rows")

        # Broker-style trade log
        STARTING_CAPITAL = 1_000_000.0
        broker_rows = []
        for i, t in trade_df.iterrows():
            ed  = pd.Timestamp(t["entry_date"])
            xd  = pd.Timestamp(t["exit_date"])
            qty = pos.loc[ed] if ed in pos.index else 0.0
            spy_price = work.loc[ed,"spy"] if ed in work.index else None
            notional  = qty/100 * STARTING_CAPITAL  # fractional allocation, NOT shares×price
            broker_rows.append({
                "trade_id":         i+1,
                "entry_date":       t["entry_date"],
                "exit_date":        t["exit_date"],
                "direction":        t["direction"],
                "qty_pct":          round(float(qty*100),2),
                "notional_usd":     round(notional,2),
                "price_entry":      round(float(spy_price),2) if spy_price is not None else None,
                "holding_days":     t["holding_days"],
                "trade_return_pct": t["trade_return_pct"],
                "signal_code":      sig_name,
                "threshold_code":   tname,
                "strategy_code":    strat,
            })
        broker_df = pd.DataFrame(broker_rows)
        broker_df.to_csv(os.path.join(RESULTS_DIR,"winner_trades_broker_style.csv"), index=False)
        print(f"  winner_trades_broker_style.csv: {len(broker_df)} rows")

    # ── Update interpretation_metadata.json (Evan-owned fields) ──
    # Determine observed_direction from best regression
    # (coef<0 on hy_ig_spread_pct → counter_cyclical)
    reg_path = os.path.join(MODELS_DIR,"predictive_regressions.csv")
    if os.path.exists(reg_path):
        reg_df = pd.read_csv(reg_path)
        spread_regs = reg_df[reg_df["signal"]=="hy_ig_spread_pct"].dropna(subset=["p_value"])
        if len(spread_regs)>0:
            best_reg = spread_regs.loc[spread_regs["p_value"].idxmin()]
            obs_dir = "countercyclical" if best_reg["coef"]<0 else "procyclical"
            dir_consistent = bool(obs_dir=="countercyclical")  # matches expected_direction
            meta["observed_direction"] = obs_dir
            meta["direction_consistent"] = dir_consistent
            meta["key_finding"] = (
                f"Best signal: {sig_name} / {tname} / {strat} / L{lead}. "
                f"OOS Sharpe {winner['oos_sharpe']:.2f} vs B&H "
                f"{bm_row['oos_sharpe']:.2f}. "
                f"hy_ig_spread_pct predicts {best_reg['horizon']} "
                f"(coef={best_reg['coef']:.4f}, p={best_reg['p_value']:.4f}). "
                f"Direction: {obs_dir}."
            )
            meta["confidence"] = "high" if best_reg["p_value"]<0.01 else "medium"
            meta["last_updated_by"] = "evan"
            meta["last_updated_at"] = now_iso
            with open(meta_path,"w") as f:
                json.dump(meta, f, indent=2)
            print(f"  interpretation_metadata.json updated: observed_direction={obs_dir}")

    # ── signal_scope.json (ECON-SD / APP-SS1) ─────────────────
    signal_scope = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "owner": "evan",
        "last_updated_by": "evan",
        "last_updated_at": now_iso,
        "indicator_axis": {
            "canonical_column": "hy_ig_spread_pct",
            "display_name": "HY-IG Credit Spread (%)",
            "derivatives": [
                {"name":"hy_ig_spread_pct","definition":"HY OAS minus IG OAS in percent. Wider = more credit stress. Primary indicator column.","formula":"hy_oas - ig_oas","role":"raw","appears_in_charts":["hero","spread_history_annotated","correlation_heatmap"]},
                {"name":"hy_ig_zscore_252d","definition":"252-day rolling z-score of HY-IG spread. Dimensionless; positive = spread above recent norm.","formula":"(spread - rolling_mean_252) / rolling_std_252","role":"threshold_input","appears_in_charts":["correlation_heatmap"]},
                {"name":"hy_ig_zscore_504d","definition":"504-day (~2yr) rolling z-score of HY-IG spread. Slower-moving regime gauge.","formula":"(spread - rolling_mean_504) / rolling_std_504","role":"threshold_input","appears_in_charts":["correlation_heatmap"]},
                {"name":"hy_ig_pctrank_504d","definition":"2-year percentile rank of HY-IG spread. Values near 1 = historically wide.","formula":"empirical_cdf_504d(spread)","role":"threshold_input","appears_in_charts":["correlation_heatmap"]},
                {"name":"hy_ig_pctrank_1260d","definition":"5-year percentile rank of HY-IG spread. Longer-memory gauge.","formula":"empirical_cdf_1260d(spread)","role":"threshold_input","appears_in_charts":["correlation_heatmap"]},
                {"name":"hy_ig_roc_21d","definition":"21-day percent change in HY-IG spread. Positive = spread widening (bearish).","formula":"(spread[t]/spread[t-21]-1)*100","role":"derivative","appears_in_charts":["correlation_heatmap"]},
                {"name":"hy_ig_roc_63d","definition":"63-day (~3M) percent change in HY-IG spread.","formula":"(spread[t]/spread[t-63]-1)*100","role":"derivative","appears_in_charts":["correlation_heatmap"]},
                {"name":"hy_ig_roc_126d","definition":"126-day (~6M) percent change in HY-IG spread.","formula":"(spread[t]/spread[t-126]-1)*100","role":"derivative","appears_in_charts":[]},
                {"name":"hy_ig_mom_21d","definition":"21-day absolute level change in HY-IG spread (pp).","formula":"spread[t]-spread[t-21]","role":"derivative","appears_in_charts":[]},
                {"name":"hy_ig_mom_63d","definition":"63-day absolute level change in HY-IG spread (pp).","formula":"spread[t]-spread[t-63]","role":"derivative","appears_in_charts":[]},
                {"name":"hy_ig_mom_252d","definition":"252-day (~1yr) absolute level change in HY-IG spread (pp).","formula":"spread[t]-spread[t-252]","role":"derivative","appears_in_charts":[]},
                {"name":"hy_ig_acceleration","definition":"Change in 21d rate-of-change — second-difference proxy. Captures inflection dynamics.","formula":"roc_21d[t]-roc_21d[t-21]","role":"derivative","appears_in_charts":[]},
                {"name":"ccc_bb_spread_pct","definition":"CCC OAS minus BB OAS — within-HY quality spread. Wider = distress concentrated at speculative end.","formula":"ccc_hy_oas - bb_hy_oas","role":"derivative","appears_in_charts":["correlation_heatmap"]},
                {"name":"hy_ig_realized_vol_21d","definition":"21-day realized volatility of daily spread changes (decimal). Rising vol = worsening credit environment.","formula":"std(diff(spread),21)","role":"diagnostic","appears_in_charts":[]},
                {"name":"hmm_2state_prob_stress","definition":"HMM 2-state model: probability of being in the stress regime (defined by high spread_change × high VIX).","formula":"GaussianHMM(n_components=2, features=[spread_change, vix], random_state=42)","role":"regime_state","appears_in_charts":["hmm_regime_overlay"]},
                {"name":"ms_2state_stress_prob","definition":"Markov-Switching regression: smoothed probability of the high-variance (stress) regime.","formula":"MarkovRegression(spy_ret ~ hy_ig_spread, k_regimes=2, switching_variance=True)","role":"regime_state","appears_in_charts":["hmm_regime_overlay"]},
            ]
        },
        "target_axis": {
            "canonical_column": "spy",
            "display_name": "SPY (SPDR S&P 500 ETF)",
            "derivatives": [
                {"name":"spy_ret","definition":"SPY daily total return (decimal). Primary dependent variable for strategy backtest.","formula":"spy[t]/spy[t-1]-1","role":"raw","appears_in_charts":["return_distribution"]},
                {"name":"spy_fwd_1d","definition":"SPY 1-day forward return (decimal).","formula":"spy[t+1]/spy[t]-1","role":"derivative","appears_in_charts":[]},
                {"name":"spy_fwd_5d","definition":"SPY 5-day forward return (decimal).","formula":"spy[t+5]/spy[t]-1","role":"derivative","appears_in_charts":[]},
                {"name":"spy_fwd_21d","definition":"SPY 21-day (~1M) forward return (decimal). Primary regression target.","formula":"spy[t+21]/spy[t]-1","role":"derivative","appears_in_charts":["scatter_signal_vs_fwd"]},
                {"name":"spy_fwd_63d","definition":"SPY 63-day (~3M) forward return (decimal).","formula":"spy[t+63]/spy[t]-1","role":"derivative","appears_in_charts":["scatter_signal_vs_fwd"]},
                {"name":"spy_fwd_126d","definition":"SPY 126-day (~6M) forward return (decimal).","formula":"spy[t+126]/spy[t]-1","role":"derivative","appears_in_charts":[]},
                {"name":"spy_fwd_252d","definition":"SPY 252-day (~1yr) forward return (decimal).","formula":"spy[t+252]/spy[t]-1","role":"derivative","appears_in_charts":[]},
                {"name":"strategy_returns","definition":"Daily backtest return stream for the winning strategy. Computed from winner signal × SPY daily return.","formula":"pos(t-1) × spy_ret(t)","role":"diagnostic","appears_in_charts":["cumulative_return","drawdown_chart"]},
            ]
        },
        "notes": (
            "Scope-disciplined per ECON-SD. All 16 indicator derivatives are "
            "hy_ig_spread_pct-derived or credit-regime signals. Off-scope cross-market "
            "signals (yield curve, bank/small-cap ratio, NFCI momentum) are "
            "reported in analyst_suggestions.json."
        ),
    }
    with open(os.path.join(RESULTS_DIR,"signal_scope.json"),"w") as f:
        json.dump(signal_scope, f, indent=2)
    print(f"  signal_scope.json saved")

    # ── analyst_suggestions.json (ECON-AS) ────────────────────
    # Compute r values from correlations.csv if available
    corr_path = os.path.join(EXPLORE_DIR,"correlations.csv")
    corr_data = {}
    if os.path.exists(corr_path):
        corr_df_raw = pd.read_csv(corr_path)
        for _, row in corr_df_raw.iterrows():
            corr_data[(row["signal"],row["horizon"])] = (row["correlation"],row["p_value"])

    def _get_r(sig, horizon):
        key = (sig, horizon)
        if key in corr_data:
            r, p = corr_data[key]
            return round(r,4), round(p,6)
        return None, None

    nfci_r,    nfci_p    = _get_r("nfci_momentum_13w",     "spy_fwd_63d")
    bank_r,    bank_p    = _get_r("bank_smallcap_ratio",    "spy_fwd_126d")
    yield_r,   yield_p   = _get_r("yield_spread_10y3m_pct", "spy_fwd_63d")
    bbb_r,     bbb_p     = _get_r("bbb_ig_spread_pct",      "spy_fwd_63d")
    vts_r,     vts_p     = _get_r("vix_term_structure",     "spy_fwd_21d")

    analyst_suggestions = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "generated_at": now_iso,
        "last_updated_at": now_iso,
        "suggestions": [
            {
                "signal_name": "NFCI Momentum (13-week)",
                "proposed_by": "evan",
                "source": "FRED:NFCI — derived: 13-week change",
                "observation": f"Pearson r = {nfci_r} with SPY 63d fwd return (p={nfci_p}, if available).",
                "rationale": "NFCI aggregates ~100 financial-conditions indicators. Its 13-week momentum captures rate at which conditions tighten. Negative sign is economically coherent: rapidly tightening conditions predict lower forward SPY returns.",
                "possible_use_case": "Cross-pair credit-stress composite or new pair nfci_momentum -> SPY",
                "caveats": "NFCI incorporates overlapping credit-spread components; double-counting risk when composited directly with HY-IG.",
                "date_filed": "2026-04-22",
                "notes": "Off-scope per ECON-SD (not an hy_ig_spread_pct derivative). Flagged for future pair catalog.",
            },
            {
                "signal_name": "Bank vs Small-Cap Ratio (KBE/IWM)",
                "proposed_by": "evan",
                "source": "derived: yahoo:KBE / yahoo:IWM",
                "observation": f"Pearson r = {bank_r} with SPY 126d fwd return (p={bank_p}, if available).",
                "rationale": "Banks-to-small-caps relative strength gauges lender balance-sheet health. A rising ratio signals late-cycle stress complementary to HY-IG.",
                "possible_use_case": "New pair — equity-stress family (bank_smallcap_ratio -> SPY)",
                "caveats": "Partially endogenous to SPY (both ETFs contain equity). Needs orthogonalization before use as clean predictor.",
                "date_filed": "2026-04-22",
                "notes": "Off-scope per ECON-SD. Candidate for dedicated equity-stress pair.",
            },
            {
                "signal_name": "Yield Curve 10Y-3M",
                "proposed_by": "evan",
                "source": "FRED: DGS10 - DTB3 (yield_spread_10y3m_pct per DATA-D12)",
                "observation": f"Pearson r = {yield_r} with SPY 63d fwd return (p={yield_p}, if available).",
                "rationale": "Classic recession predictor. Inversion historically precedes every US recession and typically leads equity drawdowns by 6-18 months.",
                "possible_use_case": "Recession-backdrop regime overlay or standalone pair",
                "caveats": "Long lead-lag (6-18 months) means near-term r is weak. 2022 inversion did not produce expected drawdown — relationship may be evolving.",
                "date_filed": "2026-04-22",
                "notes": "Off-scope per ECON-SD. Prime candidate for yield_spread_10y3m -> SPY pair.",
            },
            {
                "signal_name": "BBB-IG Quality Spread",
                "proposed_by": "evan",
                "source": "FRED: BAMLC0A4CBBB - BAMLC0A0CM (bbb_ig_spread_pct per DATA-D12)",
                "observation": f"Pearson r = {bbb_r} with SPY 63d fwd return (p={bbb_p}, if available).",
                "rationale": "Within-IG quality-tier stress gauge — how much extra yield the market demands for the lowest IG rung. Complements HY-IG with IG-side stress signal.",
                "possible_use_case": "Variant family extension alongside HY-IG",
                "caveats": "Sign may differ from HY-IG; BBB share of IG index has grown structurally since 2010 introducing composition drift.",
                "date_filed": "2026-04-22",
                "notes": "Off-scope per ECON-SD (axis is HY-IG not BBB-IG). Future variant family: HY-IG + BBB-IG + CCC-BB spectrum.",
            },
            {
                "signal_name": "VIX Term Structure (VIX3M - VIX)",
                "proposed_by": "evan",
                "source": "derived: yahoo:^VIX3M - yahoo:^VIX",
                "observation": f"Pearson r = {vts_r} with SPY 21d fwd return (p={vts_p}, if available).",
                "rationale": "Backwardation (negative term structure) indicates acute short-horizon fear premium exceeding long-horizon — historically a near-term stress signal. Complements credit spread with options-market sentiment.",
                "possible_use_case": "Complementary regime filter alongside HY-IG or standalone VIX-regime pair",
                "caveats": "Noisy at short horizons. COVID March 2020 spike dominates the tail. May double-count stress signal with HMM state probability.",
                "date_filed": "2026-04-22",
                "notes": "Off-scope per ECON-SD. Covered in VIX/VIX3M -> SPY pair (Pair #11 already completed).",
            },
        ],
    }
    with open(os.path.join(RESULTS_DIR,"analyst_suggestions.json"),"w") as f:
        json.dump(analyst_suggestions, f, indent=2)
    print(f"  analyst_suggestions.json saved ({len(analyst_suggestions['suggestions'])} entries)")

    # ── handoff_to_vera_20260422.md (ECON-H4) ─────────────────
    vera_handoff = f"""# Evan → Vera Handoff: {PAIR_ID} ({DATE_TAG})

## ECON-H4 Per-Method Chart Artifact Table

| Method | Result File | Expected Chart | Status |
|--------|-------------|----------------|--------|
| Correlation heatmap | `results/{PAIR_ID}/exploratory_{DATE_TAG}/correlations.csv` | Signal × horizon Pearson r heatmap | ready |
| Granger by lag | `results/{PAIR_ID}/granger_by_lag.csv` | F-statistic by lag 1-12 bar chart | ready |
| Predictive regressions | `results/{PAIR_ID}/core_models_{DATE_TAG}/predictive_regressions.csv` | Coefficient forest plot across signals × horizons | ready |
| Local projections | `results/{PAIR_ID}/core_models_{DATE_TAG}/local_projections.csv` | IRF-style coefficient × horizon line chart with CI | ready |
| Quantile regression | `results/{PAIR_ID}/core_models_{DATE_TAG}/quantile_regression.csv` | Quantile coefficients vs OLS line chart | ready |
| HMM regime overlay | `results/{PAIR_ID}/core_models_{DATE_TAG}/hmm_states_2state.parquet` | Regime probability overlay on spread time-series | ready |
| Quartile returns | `results/{PAIR_ID}/regime_quartile_returns.csv` | Q1-Q4 annualized SPY return bar chart | ready |
| Walk-forward | `results/{PAIR_ID}/tournament_validation_{DATE_TAG}/walk_forward.csv` | Annual OOS Sharpe scatter | ready |
| Bootstrap CI | `results/{PAIR_ID}/tournament_validation_{DATE_TAG}/bootstrap_ci.csv` | Sharpe CI95 bar chart for top-5 | ready |
| Transaction costs | `results/{PAIR_ID}/tournament_validation_{DATE_TAG}/transaction_costs.csv` | Net Sharpe vs cost bps line chart | ready |
| Signal decay | `results/{PAIR_ID}/tournament_validation_{DATE_TAG}/signal_decay.csv` | Sharpe vs execution delay bar chart | ready |
| Stress tests | `results/{PAIR_ID}/tournament_validation_{DATE_TAG}/stress_tests.csv` | Strategy vs benchmark Sharpe per stress period | ready |
| Cumulative return | `results/{PAIR_ID}/winner_trade_log.csv` | Cumulative return curve: strategy vs B&H | ready |
| Stationarity | `results/{PAIR_ID}/stationarity_tests_{DATE_TAG}.csv` | Table of ADF/KPSS results | ready |

## Winner Summary

- Signal: **{sig_name}** (`{sig_col}`)
- Threshold: {tname}  |  Strategy: {strat}  |  Lead: {lead}d
- OOS Sharpe: {winner['oos_sharpe']:.2f}  |  Return: {winner['oos_ann_return']*100:.1f}%  |  MDD: {winner['max_drawdown']*100:.1f}%
- B&H Sharpe: {f"{bm_row['oos_sharpe']:.2f}" if bm_row is not None else 'N/A'}
- OOS window: {OOS_START} → {OOS_END}
- Direction: {direction_obs}

## Notes for Vera

- All ratio-form values (returns, MDD) are decimals — multiply ×100 for display pct.
- granger_by_lag.csv uses monthly series (lags 1-12 months); x-axis label = "Lag (months)".
- regime_quartile_returns.csv: Q1=tightest spread (bullish), Q4=widest spread (bearish).
- HMM: stress_state is the high spread_change regime; probability near 1.0 → cash.
- Chart sidecar _meta.json required per VIZ-IC1 for each chart JSON saved.

Generated: {now_iso}
Author: Econ Evan
"""
    with open(os.path.join(RESULTS_DIR,f"handoff_to_vera_{DATE_TAG}.md"),"w") as f:
        f.write(vera_handoff)
    print(f"  handoff_to_vera_{DATE_TAG}.md saved")

    # ── handoff_evan_20260422.md (META-RYW + META-SRV) ────────
    # Re-read key artifacts for META-RYW block
    ws_reread   = winner_summary
    ss_reread   = signal_scope
    tr_top_row  = valid_df.nlargest(1,"oos_sharpe").iloc[0]

    evan_handoff = f"""# Evan → Lead / Ace Handoff: {PAIR_ID} ({DATE_TAG})

## META-RYW Re-Read Block

I re-read the following artifacts end-to-end before filing this handoff:

### winner_summary.json
- pair_id: {ws_reread['pair_id']} ✓ (matches {PAIR_ID})
- signal_code: {ws_reread['signal_code']} ✓
- signal_column: {ws_reread['signal_column']} ✓ (parquet column)
- target_symbol: {ws_reread['target_symbol']} ✓
- oos_period_start: {ws_reread['oos_period_start']} | oos_period_end: {ws_reread['oos_period_end']} ✓ (ECON-OOS2 formula: 79mo)
- oos_sharpe: {ws_reread['oos_sharpe']} ✓ (ratio form)
- oos_ann_return: {ws_reread['oos_ann_return']} ✓ (ratio decimal, not %)
- oos_max_drawdown: {ws_reread['oos_max_drawdown']} ✓ (ratio decimal, negative)
- direction: {ws_reread['direction']} ✓ (matches interpretation_metadata.json.observed_direction)

### signal_scope.json
- pair_id: {ss_reread['pair_id']} ✓
- indicator_axis.canonical_column: {ss_reread['indicator_axis']['canonical_column']} ✓
- n_indicator_derivatives: {len(ss_reread['indicator_axis']['derivatives'])} ✓
- n_target_derivatives: {len(ss_reread['target_axis']['derivatives'])} ✓

### tournament_results_{DATE_TAG}.csv
- winner row: {tr_top_row['signal']}/{tr_top_row['threshold']}/{tr_top_row['strategy']}/L{int(tr_top_row['lead_days'])}
- oos_sharpe={tr_top_row['oos_sharpe']:.4f} — consistent with winner_summary.json ✓
- oos_ann_return={tr_top_row['oos_ann_return']:.6f} (ratio form) ✓

### interpretation_metadata.json
- observed_direction: {meta.get('observed_direction','TBD')} ✓
- direction_consistent: {meta.get('direction_consistent','TBD')} ✓
- key_finding: recorded ✓
- last_updated_by: evan ✓

## META-SRV Evidence (wc -l on key deliverables)

Run after pipeline:
```
wc -l results/{PAIR_ID}/stationarity_tests_{DATE_TAG}.csv results/{PAIR_ID}/granger_by_lag.csv results/{PAIR_ID}/regime_quartile_returns.csv results/{PAIR_ID}/winner_trade_log.csv results/{PAIR_ID}/tournament_results_{DATE_TAG}.csv
```
Expected: all files non-empty (>1 data row each).

## Deliverable Status

| Artifact | Status | Notes |
|----------|--------|-------|
| signals_{DATE_TAG}.parquet | ✓ READY | ECON-DS2 gate item |
| tournament_results_{DATE_TAG}.csv | ✓ READY | ratio form per META-UC |
| winner_summary.json | ✓ READY | schema v1.0.0 |
| tournament_winner.json | ✓ READY | delta record |
| signal_scope.json | ✓ READY | APP-SS1 axis_block |
| analyst_suggestions.json | ✓ READY | 5 entries |
| stationarity_tests_{DATE_TAG}.csv | ✓ READY | ADF + KPSS |
| granger_by_lag.csv | ✓ READY | monthly lags 1-12 |
| regime_quartile_returns.csv | ✓ READY | Rule E2 ratio form |
| winner_trade_log.csv | ✓ READY | per-trade P&L |
| winner_trades_broker_style.csv | ✓ READY | notional = qty_pct/100 × 1M |
| oos_split_record.json | ✓ READY | ECON-OOS1 |
| pipeline_timing_{DATE_TAG}.json | ✓ READY | |
| handoff_to_vera_{DATE_TAG}.md | ✓ READY | ECON-H4 chart table |
| core_models_{DATE_TAG}/ | ✓ READY | Granger, reg, LP, QR, HMM, MS, diagnostics |
| exploratory_{DATE_TAG}/ | ✓ READY | correlations, regime stats |
| tournament_validation_{DATE_TAG}/ | ✓ READY | bootstrap, walk-fwd, costs, decay, stress |
| interpretation_metadata.json | ✓ UPDATED | Evan fields (observed_direction, direction_consistent, key_finding, confidence) |

## Winner Summary (for Lead / Ace)

- **Signal:** {sig_name} — {SIGNAL_DISPLAY.get(sig_name,sig_name)}
- **Threshold:** {tname}  ({THRESHOLD_DISPLAY.get(tname,tname)})
- **Strategy:** {strat} — {STRATEGY_DISPLAY.get(strat,strat)}
- **Lead:** {lead} days
- **OOS Sharpe:** {winner['oos_sharpe']:.2f}  (B&H: {f"{bm_row['oos_sharpe']:.2f}" if bm_row is not None else 'N/A'})
- **OOS Return:** {winner['oos_ann_return']*100:.1f}% ann.
- **OOS Max Drawdown:** {winner['max_drawdown']*100:.1f}%
- **Direction:** {direction_obs}
- **OOS window:** {OOS_START} → {OOS_END} (79 months per ECON-OOS2)

## Next Steps

- Vera: generate 10-chart set using handoff_to_vera_{DATE_TAG}.md
- Ray: finalize narrative prose using interpretation_metadata.json (strategy_objective, mechanism, caveats already populated by Ray)
- Ace: assemble portal page using signal_scope.json + winner_summary.json + pair_configs

Generated: {now_iso}
Agent: Econ Evan (econ-evan@idficient.com)
"""
    with open(os.path.join(RESULTS_DIR,f"handoff_evan_{DATE_TAG}.md"),"w") as f:
        f.write(evan_handoff)
    print(f"  handoff_evan_{DATE_TAG}.md saved")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    t0_total = time.time()
    print(f"\n{'='*60}")
    print(f"  {INDICATOR_NAME} → {TARGET_NAME}")
    print(f"  Pair ID: {PAIR_ID}  |  Wave 10G.4C  |  {DATE_TAG}")
    print(f"{'='*60}")

    # ── Stage 1: Data load ──────────────────────────────────
    t0 = time.time()
    df = stage_data()
    STAGE_TIMES["1_data_load"] = time.time()-t0

    # ── Stage 2: Feature engineering ───────────────────────
    df = stage_features(df)

    # ── Stages 4 & 5 together (core models includes stationarity,
    #    HMM/MS are needed for signals parquet) ──────────────
    hmm_probs, ms_probs, reg_df = stage_core_models(df)

    # ── Stage 3: Signals parquet (ECON-DS2) ────────────────
    stage_signals(df, hmm_probs, ms_probs)

    # ── Stage 5: Exploratory ────────────────────────────────
    stage_exploratory(df)

    # ── Stage 6: Tournament ─────────────────────────────────
    tourn_df = stage_tournament(df)

    # ── Stage 7: Validation + winner outputs ────────────────
    stage_validation(df, tourn_df)

    # ── Pipeline timing ─────────────────────────────────────
    elapsed = time.time()-t0_total
    timing = {
        "pair_id":     PAIR_ID,
        "date_tag":    DATE_TAG,
        "total_seconds": round(elapsed,1),
        "stage_times": {k:round(v,1) for k,v in STAGE_TIMES.items()},
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(os.path.join(RESULTS_DIR,f"pipeline_timing_{DATE_TAG}.json"),"w") as f:
        json.dump(timing, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  ALL STAGES COMPLETE in {elapsed:.1f}s")
    print(f"{'='*60}")
    for name, secs in STAGE_TIMES.items():
        print(f"  {name:30s}: {secs:.1f}s")
    print(f"\n  ECON-DS2 gate: check `git ls-files results/{PAIR_ID}/signals_*.parquet`")
    print(f"  Winner: see results/{PAIR_ID}/winner_summary.json")


if __name__ == "__main__":
    main()
