#!/usr/bin/env python3
"""
Full Analysis Pipeline: HY-IG Credit Spread -> S&P 500 (SPY)
=============================================================
Pair ID: hy_ig_spy

Indicator : HY-IG credit spread = ICE BofA US High Yield OAS minus ICE BofA US Corporate
            (investment grade) OAS, FRED BAMLH0A0HYM2 - BAMLC0A0CM, percentage points
Target    : SPY daily returns (Yahoo Finance adjusted close)
Data      : committed parquet data/hy_ig_spy_daily_20000101_20260422.parquet
            (2000-01-03 .. 2026-04-22; input vintage 20260422, no live re-fetch)

fix261016_hmm_causal rebuild (DATE_TAG 20261016) — what changed and why
-----------------------------------------------------------------------
QC (2026-10-16) found the published winner S6_hmm_stress/T4_hmm_0.5/P2/L0 (OOS Sharpe
1.4083, HAC t 3.80) used a GaussianHMM fit on the FULL sample with forward-backward
SMOOTHED probabilities (predict_proba): look-ahead. This version:
  * HMM and Markov-switching regime signals come from scripts/_regime_causal.py: fit on
    in-sample rows only (< OOS_START), IS-only standardisation, forward-filtered
    probabilities P(state_t | x_1..t). The MS model no longer contains SPY returns in its
    likelihood (dependent variable = daily HY-IG spread change).
  * Lead floor: ICE BofA OAS post on FRED ~1 business day late. Traded grid is the
    standard daily set floored at L1 -> {1,5,21,63,126,252}; with the pos.shift(1)
    execution lag the effective lag is >= 2 trading days (registry lead_floor_effective 2).
  * Selection (#251/#268, PORT_GUIDE): winner = argmax IN-SAMPLE Sharpe on the common IS
    window [common_is_start, OOS_START); eligibility before alignment; OOS is evaluation
    only. Legacy OOS-argmax and own-start sensitivity are written to a side CSV.
  * Inference fixes: predictive regressions and local projections use HAC with
    maxlags >= horizon-1; regime quartiles are a FORWARD-return test; validation replays
    run on the full series and are sliced afterwards (no warm-up truncation); OOS and
    full-sample trade counts / turnover are reported separately.
  * Lead-axis artifacts (previously scripts/refresh_hy_ig_spy_lead_artifacts.py, retired)
    and the ECON-SR1 / SR3 / CP1 sidecars are produced here from the canonical series.

Run:  python3 scripts/pair_pipeline_hy_ig_spy.py      (~1-2 min; deterministic)
Author: Econ Evan. SOP: docs/agent-sops/econometrics-agent-sop.md
"""

import os, sys, json, warnings, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _stamp import iso_utc_now  # noqa: E402
from _regime_causal import fit_hmm_causal, fit_ms_causal  # noqa: E402

import numpy as np
import pandas as pd
from scipy import stats
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
PAIR_ID        = "hy_ig_spy"
INDICATOR_NAME = "HY-IG Credit Spread"
TARGET_NAME    = "S&P 500 (SPY)"
START_DATE     = "2000-01-01"
END_DATE       = "2026-04-22"
DATE_TAG       = "20261016"   # output vintage (this rebuild)
DATA_TAG       = "20260422"   # input data vintage (committed parquet)

# OOS window — ECON-OOS2: span = min(max(36, round(316*0.25)), 120) = 79 months.
IS_END    = "2019-09-30"
OOS_START = "2019-10-01"
OOS_END   = END_DATE

# Traded lead grid (trading days): standard daily points {0,1,5,21,63,126,252} that are
# >= the L1 floor (OAS ~1-day publication lag). Registry: lead_floor 1, position_shift 1,
# lead_floor_effective 2 (docs/schemas/lead_axis_registry.json).
LEADS = [1, 5, 21, 63, 126, 252]
ANN = 252
MIN_IS_N = 1260     # 5 years of daily IS returns (daily analogue of the monthly MIN_IS_N=60)
MIN_OOS_N = 252     # legacy / information only
HMM_SEEDS = (42, 0, 1, 2, 3)   # EM restarts; max IS log-likelihood kept (deterministic)

REPO          = Path(__file__).resolve().parents[1]
BASE_DIR      = str(REPO)
DATA_DIR      = os.path.join(BASE_DIR, "data")
RESULTS_DIR   = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR   = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR    = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALIDATION_DIR= os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")
SIGNALS_DIR   = RESULTS_DIR

for d in [DATA_DIR, RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALIDATION_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES: dict = {}
CTX: dict = {}   # run context shared between stages (regime fits, selection record)


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


def hac_maxlags(n: int, horizon: int = 1) -> int:
    """Newey-West lag: the larger of the Andrews/NW rule int(0.75 n^(1/3)) and horizon-1
    (overlapping h-period returns are MA(h-1) under the null)."""
    return int(max(int(0.75 * n ** (1 / 3)), horizon - 1))


def hac_t_mean(r: pd.Series, horizon: int = 1):
    import statsmodels.api as sm
    y = pd.Series(r).dropna().values
    nw = hac_maxlags(len(y), horizon)
    m = sm.OLS(y, np.ones((len(y), 1))).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
    return float(m.tvalues[0]), float(m.pvalues[0]), nw


def ann_metrics(r: pd.Series) -> dict:
    r = pd.Series(r).dropna()
    n = len(r)
    if n < 2 or r.std() == 0:
        return {"sharpe": np.nan, "ann_return": np.nan, "ann_vol": np.nan, "max_drawdown": np.nan,
                "sortino": np.nan, "calmar": np.nan, "win_rate": np.nan, "n": n}
    mu, sd = r.mean(), r.std()
    cum = (1 + r).cumprod()
    mdd = float(((cum - cum.cummax()) / cum.cummax()).min())
    dn = r[r < 0].std()
    return {"sharpe": float(mu / sd * np.sqrt(ANN)), "ann_return": float(mu * ANN),
            "ann_vol": float(sd * np.sqrt(ANN)), "max_drawdown": mdd,
            "sortino": float(mu / dn * np.sqrt(ANN)) if dn and dn > 0 else np.nan,
            "calmar": float(mu * ANN / abs(mdd)) if mdd < 0 else np.nan,
            "win_rate": float((r > 0).mean()), "n": n}


def trade_stats(pos: pd.Series, mask) -> tuple[int, float]:
    """(n_trades, annual_turnover) of a position series inside a boolean mask.
    n_trades counts position changes larger than 0.05 (as before); turnover = sum|dpos| / years."""
    p = pos[mask].dropna()
    if len(p) < 2:
        return 0, 0.0
    d = p.diff().abs().fillna(0)
    return int(d.gt(0.05).sum()), float(d.sum() / max(len(p) / ANN, 1))


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
        os.path.join(DATA_DIR, f"{PAIR_ID}_daily_20000101_{DATA_TAG}.parquet")))
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

    load_dotenv()  # repo-root .env; hardcoded fallback removed (key rotated after leak)
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise SystemExit("FRED_API_KEY not set — copy .env.example to .env, or run setup.sh.")
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
    out_path = os.path.join(DATA_DIR, f"{PAIR_ID}_daily_20000101_{DATA_TAG}.parquet")
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
    """Persist tournament-eligible derived signals (ECON-DS2, committed).
    hmm_2state_prob_stress / ms_2state_stress_prob are CAUSAL (IS-fit, forward-filtered)."""
    sig_df = df[[
        "hy_ig_spread_pct", "hy_ig_zscore_252d", "hy_ig_zscore_504d",
        "hy_ig_pctrank_504d", "hy_ig_pctrank_1260d",
        "hy_ig_roc_21d", "hy_ig_roc_63d", "hy_ig_roc_126d",
        "hy_ig_mom_21d", "hy_ig_mom_63d", "hy_ig_mom_252d",
        "hy_ig_acceleration",
    ]].copy()
    for col in ["ccc_bb_spread_pct", "hy_ig_realized_vol_21d"]:
        if col in df.columns:
            sig_df[col] = df[col]
    sig_df["hmm_2state_prob_stress"] = hmm_probs.reindex(df.index)
    sig_df["hmm_2state_prob_calm"]   = (1 - hmm_probs).reindex(df.index)
    sig_df["ms_2state_stress_prob"]  = ms_probs.reindex(df.index)

    signals_path = os.path.join(SIGNALS_DIR, f"signals_{DATE_TAG}.parquet")
    sig_df.to_parquet(signals_path)
    print(f"  Signals parquet: {signals_path}  shape={sig_df.shape}")
    return sig_df


# ─────────────────────────────────────────────────────────────
# STAGE 4: CORE MODELS
# ─────────────────────────────────────────────────────────────

@timed("4_core_models")
def stage_core_models(df: pd.DataFrame):
    """Granger, predictive regressions (HAC), local projections (HAC, maxlags>=h-1),
    quantile regression, CAUSAL HMM + Markov-switching regimes, stationarity, diagnostics."""
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    work = df.dropna(subset=["hy_ig_spread_pct", "spy_ret"]).copy()

    # ── 1. Granger causality — monthly (Rule E1) ──────────────
    # Monthly SPY return = COMPOUNDED daily returns within the month (the earlier version took
    # the last day's return). The spread enters as its month-end CHANGE (the level is highly
    # persistent; see stationarity_tests). Direction: d(spread) -> SPY monthly return.
    granger_rows = []
    m_ret = (1 + work["spy_ret"]).resample("ME").prod() - 1
    m_spr = work["hy_ig_spread_pct"].resample("ME").last()
    monthly = pd.DataFrame({"spy_ret_m": m_ret, "d_spread_m": m_spr.diff()}).dropna()
    try:
        gc = grangercausalitytests(monthly[["spy_ret_m", "d_spread_m"]], maxlag=12, verbose=False)
        for lag, r in gc.items():
            f = r[0]["ssr_ftest"]
            granger_rows.append({"lag": lag, "f_statistic": round(f[0], 4), "p_value": round(f[1], 4),
                                 "df_num": int(f[3]), "df_den": int(f[2])})
    except Exception as e:
        print(f"  Granger (monthly) FAILED: {e}")
    granger_df = pd.DataFrame(granger_rows)
    granger_df.to_csv(os.path.join(RESULTS_DIR, "granger_by_lag.csv"), index=False)
    print(f"  granger_by_lag.csv: {len(granger_df)} rows (n_months={len(monthly)}); "
          f"min p={granger_df['p_value'].min() if len(granger_df) else float('nan')}")

    # Daily Granger, both directions, on stationary daily spread change
    gc_full = []
    d = pd.DataFrame({"spy_ret": work["spy_ret"], "d_spread": work["hy_ig_spread_pct"].diff()}).dropna()
    for direction, cols in [("HY_IG->SPY", ["spy_ret", "d_spread"]), ("SPY->HY_IG", ["d_spread", "spy_ret"])]:
        try:
            r = grangercausalitytests(d[cols], maxlag=5, verbose=False)
            for lag in range(1, 6):
                f = r[lag][0]["ssr_ftest"]
                gc_full.append({"direction": direction, "lag": lag, "f_stat": round(f[0], 4),
                                "p_value": round(f[1], 4), "spread_transform": "daily change"})
        except Exception as e:
            print(f"  Granger (daily {direction}) FAILED: {e}")
    pd.DataFrame(gc_full).to_csv(os.path.join(MODELS_DIR, "granger_causality.csv"), index=False)

    # ── 2. Predictive regressions — HAC(max(NW, h-1)) on overlapping returns ──
    reg_results = []
    reg_signals = [
        "hy_ig_spread_pct", "hy_ig_zscore_252d", "hy_ig_zscore_504d",
        "hy_ig_pctrank_504d", "hy_ig_pctrank_1260d",
        "hy_ig_roc_21d", "hy_ig_roc_63d", "hy_ig_roc_126d",
        "hy_ig_mom_21d", "hy_ig_mom_63d", "hy_ig_acceleration", "ccc_bb_spread_pct",
    ]
    horizons = {"spy_fwd_1d": 1, "spy_fwd_5d": 5, "spy_fwd_21d": 21, "spy_fwd_63d": 63, "spy_fwd_126d": 126}
    for sig in reg_signals:
        for fwd, h in horizons.items():
            if sig not in work.columns or fwd not in work.columns:
                continue
            valid = work[[sig, fwd]].dropna()
            if len(valid) < 50:
                continue
            nw = hac_maxlags(len(valid), h)
            m = sm.OLS(valid[fwd], sm.add_constant(valid[sig])).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            reg_results.append({"signal": sig, "horizon": fwd, "horizon_days": h,
                                "coef": round(m.params.iloc[1], 6), "t_stat": round(m.tvalues.iloc[1], 3),
                                "p_value": round(m.pvalues.iloc[1], 4), "r_squared": round(m.rsquared, 4),
                                "n": int(m.nobs), "cov_type": "HAC", "hac_maxlags": nw})
    reg_df = pd.DataFrame(reg_results)
    reg_df.to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    print(f"  Regressions: {len(reg_df)} (HAC; {int((reg_df['p_value'] < 0.05).sum())} with p<0.05)")

    # ── 3. Local projections (Jordà) — HAC maxlags >= h-1 ─────
    lp_results = []
    for fwd, h in [("spy_fwd_5d", 5), ("spy_fwd_21d", 21), ("spy_fwd_63d", 63)]:
        ctrls = [c for c in ["vix", "yield_spread_10y3m_pct"] if c in work.columns]
        valid = work[["hy_ig_spread_pct", fwd] + ctrls].dropna()
        nw = hac_maxlags(len(valid), h)
        m = sm.OLS(valid[fwd], sm.add_constant(valid[["hy_ig_spread_pct"] + ctrls])).fit(
            cov_type="HAC", cov_kwds={"maxlags": nw})
        ci = m.conf_int().loc["hy_ig_spread_pct"]
        lp_results.append({"horizon_days": h, "coef": round(m.params["hy_ig_spread_pct"], 6),
                           "se": round(m.bse["hy_ig_spread_pct"], 6),
                           "t_stat": round(m.tvalues["hy_ig_spread_pct"], 3),
                           "p_value": round(m.pvalues["hy_ig_spread_pct"], 4),
                           "ci_lower": round(ci[0], 6), "ci_upper": round(ci[1], 6),
                           "r_squared": round(m.rsquared, 4), "n": int(m.nobs), "hac_maxlags": nw,
                           "controls": "+".join(ctrls)})
    pd.DataFrame(lp_results).to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    print("  Local projections: " + ", ".join(f"h={r['horizon_days']}d t={r['t_stat']} p={r['p_value']}"
                                             for r in lp_results))

    # ── 4. Quantile regression (21-day forward SPY return) ────
    qr_results = []
    valid_qr = work[["hy_ig_spread_pct", "spy_fwd_21d"]].dropna()
    for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
        qr = smf.quantreg("spy_fwd_21d ~ hy_ig_spread_pct", data=valid_qr).fit(q=tau)
        qr_results.append({"quantile": tau, "coef": round(qr.params["hy_ig_spread_pct"], 6),
                           "p_value": round(qr.pvalues["hy_ig_spread_pct"], 4),
                           "ci_lower": round(qr.conf_int().loc["hy_ig_spread_pct", 0], 6),
                           "ci_upper": round(qr.conf_int().loc["hy_ig_spread_pct", 1], 6)})
    pd.DataFrame(qr_results).to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    print(f"  Quantile reg: {len(qr_results)} quantiles")

    # ── 5. HMM regime (2-state) — CAUSAL ──────────────────────
    hmm_data = pd.DataFrame({"spread_change": work["hy_ig_spread_pct"].diff(), "vix": work["vix"]},
                            index=work.index)
    hmm = fit_hmm_causal(hmm_data, OOS_START, n_states=2, label_feature="spread_change",
                         label="max", covariance_type="full", n_iter=200, seeds=HMM_SEEDS)
    hmm_probs = hmm.prob.reindex(df.index).rename("hmm_2state_prob_stress")
    hp = hmm.prob.dropna()
    oos = hp.index >= OOS_START
    pd.DataFrame({"prob_state_0": hmm.probs["state_1"], "prob_state_1": hmm.probs["state_0"],
                  "state": (hmm.probs["state_1"] > 0.5).astype("Int64").where(hmm.probs["state_1"].notna())},
                 index=hmm_data.index).dropna(subset=["prob_state_0"]).to_parquet(
        os.path.join(MODELS_DIR, "hmm_states_2state.parquet"))
    hmm_summary = {
        "n_states": 2, "model": "GaussianHMM(full cov) on [daily spread change, VIX], IS-standardised",
        "probability": "forward-filtered P(stress_t | data up to t); NOT forward-backward smoothed",
        "fit_window": [hmm.fit_start.date().isoformat(), hmm.fit_end.date().isoformat()], "n_fit": hmm.n_fit,
        "stress_state": "state with the higher in-sample mean daily spread change",
        "mean_stress_prob": round(float(hp.mean()), 4),
        "pct_stress_days": round(float((hp > 0.5).mean() * 100), 2),
        "pct_stress_days_is": round(float((hp[~oos] > 0.5).mean() * 100), 2),
        "pct_stress_days_oos": round(float((hp[oos] > 0.5).mean() * 100), 2),
        "state_means_standardised": hmm.params["means"], "transmat": hmm.params["transmat"],
        "seed_selected": hmm.params["seed"], "seeds_tried": hmm.params["seeds_tried"],
        "loglik_is": round(hmm.loglik_is, 2),
    }
    with open(os.path.join(MODELS_DIR, "hmm_summary.csv"), "w") as f:   # JSON body (legacy name kept)
        json.dump(hmm_summary, f, indent=2)
    print(f"  HMM (causal): fit {hmm_summary['fit_window']} n={hmm.n_fit}; stress days "
          f"{hmm_summary['pct_stress_days']}% (IS {hmm_summary['pct_stress_days_is']}%, "
          f"OOS {hmm_summary['pct_stress_days_oos']}%)")

    # ── 6. Markov-switching — CAUSAL, no SPY return in the likelihood ──
    ms = fit_ms_causal(work["hy_ig_spread_pct"].diff().rename("spread_change"), OOS_START,
                       k_regimes=2, switching_variance=True, label="max_variance")
    ms_probs = ms.prob.reindex(df.index).rename("ms_2state_stress_prob")
    msp = ms.prob.dropna()
    ms_summary = {
        "model": "MarkovRegression(daily HY-IG spread change ~ switching const, switching variance), k=2",
        "probability": "Hamilton-filtered P(high-variance regime_t | data up to t) with IS-frozen params",
        "dependent": "spread_change (SPY returns are NOT in the likelihood)",
        "fit_window": [ms.fit_start.date().isoformat(), ms.fit_end.date().isoformat()], "n_fit": ms.n_fit,
        "params_is": dict(zip(ms.params["param_names"], [round(v, 6) for v in ms.params["params_is"]])),
        "pct_high_var_days": round(float((msp > 0.5).mean() * 100), 2),
        "pct_high_var_days_oos": round(float((msp[msp.index >= OOS_START] > 0.5).mean() * 100), 2),
        "loglik_is": round(ms.loglik_is, 2),
    }
    with open(os.path.join(MODELS_DIR, "ms_summary.json"), "w") as f:
        json.dump(ms_summary, f, indent=2)
    print(f"  MS (causal): high-variance days {ms_summary['pct_high_var_days']}% "
          f"(OOS {ms_summary['pct_high_var_days_oos']}%), obs={msp.notna().sum()}")
    CTX["hmm"], CTX["ms"] = hmm, ms

    # ── 7. Stationarity (ADF + KPSS) ──────────────────────────
    stat_results = []
    from arch.unitroot import ADF, KPSS
    test_vars = ["hy_ig_spread_pct", "hy_ig_zscore_252d", "hy_ig_roc_21d", "hy_ig_roc_63d",
                 "hy_ig_mom_21d", "hy_ig_acceleration", "ccc_bb_spread_pct", "hy_ig_realized_vol_21d",
                 "vix_term_structure", "yield_spread_10y3m_pct", "yield_spread_10y2y_pct",
                 "nfci_momentum_13w", "bbb_ig_spread_pct", "spy", "spy_ret"]
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
            stat_results.append({"variable": col, "test": "ADF", "statistic": round(float(adf.stat), 4),
                                 "p_value": round(float(adf.pvalue), 4), "lags": int(adf.lags), "n_obs": len(s),
                                 "conclusion": "Stationary" if adf.pvalue < 0.05 else "Non-stationary"})
            kp = KPSS(s)
            stat_results.append({"variable": col, "test": "KPSS", "statistic": round(float(kp.stat), 4),
                                 "p_value": round(float(kp.pvalue), 4), "lags": int(kp.lags), "n_obs": len(s),
                                 "conclusion": "Stationary" if kp.pvalue > 0.05 else "Non-stationary"})
        except Exception as e:
            print(f"  stationarity {col} FAILED: {e}")
    pd.DataFrame(stat_results).to_csv(os.path.join(RESULTS_DIR, f"stationarity_tests_{DATE_TAG}.csv"), index=False)

    # ── 8. Diagnostics (21d predictive regression residuals) ──
    from statsmodels.stats.stattools import durbin_watson
    vd = work[["hy_ig_spread_pct", "spy_fwd_21d"]].dropna()
    m = sm.OLS(vd["spy_fwd_21d"], sm.add_constant(vd["hy_ig_spread_pct"])).fit()
    jb_s, jb_p = stats.jarque_bera(m.resid)
    pd.DataFrame([{"test": "Jarque-Bera", "statistic": round(jb_s, 4), "p_value": round(jb_p, 4)},
                  {"test": "Durbin-Watson", "statistic": round(durbin_watson(m.resid), 4), "p_value": np.nan}]
                 ).to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)

    return hmm_probs, ms_probs, reg_df


# ─────────────────────────────────────────────────────────────
# STAGE 5: EXPLORATORY ANALYSIS
# ─────────────────────────────────────────────────────────────

@timed("5_exploratory")
def stage_exploratory(df: pd.DataFrame):
    """Correlations; regime quartiles as a FORWARD-return test (Rule E2)."""
    import statsmodels.api as sm

    signal_cols = [c for c in df.columns
                   if (c.startswith("hy_ig_") or c in [
                       "ccc_bb_spread_pct", "vix_term_structure", "yield_spread_10y3m_pct",
                       "yield_spread_10y2y_pct", "bank_smallcap_ratio", "nfci_momentum_13w",
                       "bbb_ig_spread_pct", "hy_ig_realized_vol_21d"])
                   and "fwd" not in c and "ret" not in c]
    fwd_cols = [c for c in df.columns if c.startswith("spy_fwd_")]
    corr_results = []
    for sig in signal_cols:
        for fwd in fwd_cols:
            valid = df[[sig, fwd]].dropna()
            if len(valid) < 50:
                continue
            r, p = stats.pearsonr(valid[sig], valid[fwd])
            corr_results.append({"signal": sig, "horizon": fwd, "method": "Pearson",
                                 "correlation": round(r, 4), "p_value": round(p, 4), "n": len(valid),
                                 "p_value_note": "iid p-value; overlapping forward windows overstate significance"})
    corr_df = pd.DataFrame(corr_results)
    corr_df.to_csv(os.path.join(EXPLORE_DIR, "correlations.csv"), index=False)

    # Descriptive (CONCURRENT) daily SPY stats by spread quartile — labelled as such
    regime_results = []
    valid = df[["hy_ig_spread_pct", "spy_ret"]].dropna()
    qd = pd.qcut(valid["hy_ig_spread_pct"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"])
    for q in ["Q1_low", "Q2", "Q3", "Q4_high"]:
        rets = valid.loc[qd == q, "spy_ret"]
        a = ann_metrics(rets)
        regime_results.append({"regime": q, "n_days": len(rets), "ann_return_pct": round(a["ann_return"] * 100, 2),
                               "ann_vol_pct": round(a["ann_vol"] * 100, 2), "sharpe": round(a["sharpe"], 3),
                               "timing": "concurrent (same-day), descriptive"})
    pd.DataFrame(regime_results).to_csv(os.path.join(EXPLORE_DIR, "regime_descriptive_stats.csv"), index=False)

    # Rule E2 — FORWARD test: month-end spread quartile vs SPY return over the NEXT 1/3/6 months
    m_ret = (1 + valid["spy_ret"]).resample("ME").prod() - 1
    m_spr = valid["hy_ig_spread_pct"].resample("ME").last()
    mdf = pd.DataFrame({"spread": m_spr, "ret": m_ret}).dropna()
    for h in (1, 3, 6):
        mdf[f"fwd_{h}m"] = (1 + mdf["ret"]).rolling(h).apply(np.prod, raw=True).shift(-h) - 1
    q_labels = ["Q1", "Q2", "Q3", "Q4"]
    mdf["q"] = pd.qcut(mdf["spread"], 4, labels=q_labels)
    qr_rows = []
    for q in q_labels:
        sub = mdf[mdf["q"] == q]
        r1 = sub["fwd_1m"].dropna()          # non-overlapping monthly returns -> clean annualisation
        cum = (1 + r1).cumprod()
        qr_rows.append({
            "quartile": q, "n_months": int(len(r1)),
            "ann_return": round(r1.mean() * 12, 6), "ann_vol": round(r1.std() * np.sqrt(12), 6),
            "sharpe": round(r1.mean() / r1.std() * np.sqrt(12), 4) if r1.std() > 0 else 0,
            "max_drawdown": round(float(((cum - cum.cummax()) / cum.cummax()).min()), 6),
            "return_window": "next_month",
            "spread_low": round(float(sub["spread"].min()), 4), "spread_high": round(float(sub["spread"].max()), 4),
            "mean_fwd_3m": round(float(sub["fwd_3m"].mean()), 6), "mean_fwd_6m": round(float(sub["fwd_6m"].mean()), 6),
        })
    pd.DataFrame(qr_rows).to_csv(os.path.join(RESULTS_DIR, "regime_quartile_returns.csv"), index=False)

    ft_rows = []
    for h in (1, 3, 6):
        sub = mdf[["q", f"fwd_{h}m"]].dropna()
        X = pd.get_dummies(sub["q"], drop_first=True).astype(float)   # Q2..Q4 vs Q1
        X = sm.add_constant(X)
        nw = max(h - 1, 1)
        m = sm.OLS(sub[f"fwd_{h}m"], X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
        means = sub.groupby("q", observed=True)[f"fwd_{h}m"].mean()
        joint = m.wald_test("Q2 = 0, Q3 = 0, Q4 = 0", scalar=True)
        mono = bool(all(means.iloc[i] >= means.iloc[i + 1] for i in range(3)))
        ft_rows.append({"horizon_months": h, "n_months": int(len(sub)),
                        "mean_Q1": round(means["Q1"], 6), "mean_Q2": round(means["Q2"], 6),
                        "mean_Q3": round(means["Q3"], 6), "mean_Q4": round(means["Q4"], 6),
                        "q4_minus_q1": round(float(m.params["Q4"]), 6), "q4_minus_q1_hac_t": round(float(m.tvalues["Q4"]), 3),
                        "q4_minus_q1_p": round(float(m.pvalues["Q4"]), 4), "joint_wald_p": round(float(joint.pvalue), 4),
                        "monotonic_decreasing": mono, "hac_maxlags": nw,
                        "note": "quartile breakpoints from the full-sample distribution of month-end spreads (descriptive bins)"})
    ft = pd.DataFrame(ft_rows)
    ft.to_csv(os.path.join(RESULTS_DIR, f"regime_quartile_forward_tests_{DATE_TAG}.csv"), index=False)
    print("  Quartile FORWARD test: " + "; ".join(
        f"{r.horizon_months}m Q4-Q1={r.q4_minus_q1:+.4f} t={r.q4_minus_q1_hac_t} mono={r.monotonic_decreasing}"
        for r in ft.itertuples()))
    return corr_df


# ─────────────────────────────────────────────────────────────
# STAGE 6: TOURNAMENT  (IS-selected winner, #251/#268)
# ─────────────────────────────────────────────────────────────

SIGNAL_COLS = {
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


def threshold_codes_for(sig_name):
    if sig_name == "S6_hmm_stress":
        return ["T4_hmm_0.5", "T4_hmm_0.7"]
    if sig_name == "S7_ms_stress":
        return ["T5_ms_0.5", "T5_ms_0.7"]
    return ([f"T1_p{p}" for p in (75, 85, 95)] + [f"T2_rp{p}" for p in (75, 85, 95)]
            + [f"T3_z{z}" for z in (1.5, 2.0, 2.5)])


def build_position(sig_l: pd.Series, tname: str, strat: str, is_index_mask) -> pd.Series:
    """Countercyclical position from the lead-shifted signal (low signal = bullish).
    Position is NaN wherever the signal or its threshold is undefined (warm-up), so warm-up
    days are NOT silently traded as cash/short (fix: earlier versions cast NaN comparisons
    to False). T1 quantiles use IS observations only; T2/T3/P2 windows are trailing."""
    if strat == "P2":   # threshold-invariant: size on the trailing-504d range of the signal
        smin = sig_l.rolling(504, min_periods=400).min()
        smax = sig_l.rolling(504, min_periods=400).max()
        return (1 - (sig_l - smin) / (smax - smin).replace(0, np.nan)).clip(0, 1)
    if tname.startswith("T3_z"):
        z = float(tname.split("z")[1])
        rm = sig_l.rolling(504, min_periods=400).mean()
        rs = sig_l.rolling(504, min_periods=400).std().replace(0, np.nan)
        zz = (sig_l - rm) / rs
        bull, defined = zz < z, zz.notna()
    elif tname.startswith(("T4_", "T5_")):
        thr = float(tname.rsplit("_", 1)[1])
        bull, defined = sig_l < thr, sig_l.notna()
    elif tname.startswith("T1_p"):
        thr = sig_l[is_index_mask].dropna().quantile(int(tname.split("p")[1]) / 100)
        bull, defined = sig_l < thr, sig_l.notna()
    else:  # T2_rp
        thr = sig_l.rolling(504, min_periods=400).quantile(int(tname.split("rp")[1]) / 100)
        bull, defined = sig_l < thr, sig_l.notna() & thr.notna()
    pos = bull.astype(float) if strat == "P1" else bull.astype(float) * 2 - 1
    return pos.where(defined)


def replay(work: pd.DataFrame, sig_col: str, tname: str, strat: str, lead: int):
    """(pos, strat_ret) on the FULL series; callers slice afterwards (no warm-up truncation)."""
    sig_l = work[sig_col].shift(lead) if lead > 0 else work[sig_col]
    pos = build_position(sig_l, tname, strat, work.index <= IS_END)
    return pos, pos.shift(1) * work["spy_ret"]


def _exposure(pos: pd.Series, strat: str) -> float:
    p = pos.dropna()
    if not len(p):
        return np.nan
    return float((p > 0).mean()) if strat == "P3" else float(p.mean())


@timed("6_tournament")
def stage_tournament(df: pd.DataFrame) -> pd.DataFrame:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _tournament_io import write_tournament  # ECON-T5 §4 immutability guard

    sig_df = pd.read_parquet(os.path.join(SIGNALS_DIR, f"signals_{DATE_TAG}.parquet"))
    work = df.copy()
    for col in ["hmm_2state_prob_stress", "ms_2state_stress_prob"]:
        work[col] = sig_df[col].reindex(work.index)
    work = work.dropna(subset=["spy_ret"])
    oos_start = pd.Timestamp(OOS_START)
    oos_mask = work.index >= oos_start
    available = {k: v for k, v in SIGNAL_COLS.items() if v in work.columns and work[v].notna().sum() > 200}
    print(f"  Available signals: {len(available)} of {len(SIGNAL_COLS)}; leads {LEADS}")

    # pass 1: candidates (positions on the full series)
    cands = []
    for sig_name, sig_col in available.items():
        for lead in LEADS:
            p2_cache = None
            for tname in threshold_codes_for(sig_name):
                for strat in ["P1", "P2", "P3"]:
                    if strat == "P2" and p2_cache is not None:
                        pos, rets = p2_cache
                    else:
                        pos, rets = replay(work, sig_col, tname, strat, lead)
                        if strat == "P2":
                            p2_cache = (pos, rets)
                    cands.append((sig_name, sig_col, tname, strat, lead, pos, rets))

    def _first(rets):
        r = rets.dropna()
        return r.index.min() if len(r) else pd.NaT

    def _own_is_n(rets):
        return int(((rets.index < oos_start) & rets.notna()).sum())

    eligible = [_own_is_n(c[6]) >= MIN_IS_N for c in cands]
    n_inel = int(len(cands) - sum(eligible))
    if not any(eligible):
        raise RuntimeError("No IS-eligible candidate")
    common_is_start = max(_first(c[6]) for c, ok in zip(cands, eligible) if ok)
    is_mask_c = (work.index >= common_is_start) & (work.index < oos_start)
    driver = [f"{c[0]}/{c[2]}/{c[3]}/L{c[4]}" for c, ok in zip(cands, eligible)
              if ok and _first(c[6]) == common_is_start][:3]
    print(f"  common IS start {common_is_start.date()} (set by e.g. {driver}); "
          f"{n_inel} ineligible (own IS n < {MIN_IS_N})")

    bh_is = ann_metrics(work.loc[is_mask_c, "spy_ret"])
    bh = ann_metrics(work.loc[oos_mask, "spy_ret"])

    rows = []
    for (sig_name, sig_col, tname, strat, lead, pos, rets), elig in zip(cands, eligible):
        is_r = rets[is_mask_c].dropna()
        own_start = _first(rets)
        own_mask = (work.index >= own_start) & (work.index < oos_start) if pd.notna(own_start) else is_mask_c & False
        own_r = rets[own_mask].dropna()
        oos_r = rets[oos_mask].fillna(0.0)                       # ECON-T4 deployable OOS
        mi, mo, m = ann_metrics(is_r), ann_metrics(own_r), ann_metrics(oos_r)
        is_tr, is_to = trade_stats(pos, is_mask_c)
        oos_tr, oos_to = trade_stats(pos, oos_mask)
        full_tr, full_to = trade_stats(pos, np.ones(len(pos), dtype=bool))
        is_expo = _exposure(pos[is_mask_c], strat)
        own_expo = _exposure(pos[own_mask], strat)
        oos_expo = _exposure(pos[oos_mask], strat)
        is_valid = bool(elig and len(is_r) >= MIN_IS_N and 0.05 <= is_expo <= 0.95
                        and is_r.std() > 0 and is_to < 24 and is_tr >= 10)
        own_valid = bool(len(own_r) >= MIN_IS_N and own_expo == own_expo and 0.05 <= own_expo <= 0.95
                         and own_r.std() > 0)
        legacy_valid = bool(m["sharpe"] == m["sharpe"] and m["sharpe"] > 0 and full_to < 24 and full_tr >= 10)
        rows.append({
            "signal": sig_name, "signal_column": sig_col, "threshold": tname, "strategy": strat,
            "lead_days": lead, "direction": "countercyclical",
            "is_sharpe": round(mi["sharpe"], 6), "is_ann_return": round(mi["ann_return"], 6),
            "is_max_drawdown": round(mi["max_drawdown"], 6), "is_exposure": round(is_expo, 4),
            "is_n_trades": is_tr, "is_annual_turnover": round(is_to, 3),
            "is_start": is_r.index.min().date().isoformat() if len(is_r) else None,
            "is_end": is_r.index.max().date().isoformat() if len(is_r) else None,
            "common_is_start": common_is_start.date().isoformat(),
            "own_is_start": own_r.index.min().date().isoformat() if len(own_r) else None,
            "own_is_sharpe": round(mo["sharpe"], 6), "own_is_n": mo["n"], "own_is_valid": own_valid,
            "oos_sharpe": round(m["sharpe"], 6), "oos_sortino": round(m["sortino"], 6),
            "oos_calmar": round(m["calmar"], 6), "oos_ann_return": round(m["ann_return"], 6),
            "oos_ann_vol": round(m["ann_vol"], 6), "max_drawdown": round(m["max_drawdown"], 6),
            "win_rate": round(m["win_rate"], 4), "oos_exposure": round(oos_expo, 4),
            "n_trades": oos_tr, "annual_turnover": round(oos_to, 3),
            "n_trades_full": full_tr, "annual_turnover_full": round(full_to, 3),
            "is_n": mi["n"], "oos_n": m["n"], "is_eligible": bool(elig),
            "is_ineligible_reason": "" if elig else f"insufficient IS history: n_own={_own_is_n(rets)} < MIN_IS_N={MIN_IS_N}",
            "is_valid": is_valid, "oos_valid": legacy_valid, "valid": is_valid,
        })
    rows.append({
        "signal": "BENCHMARK", "signal_column": "spy", "threshold": "BUY_HOLD", "strategy": "BH", "lead_days": 0,
        "direction": "benchmark", "is_sharpe": round(bh_is["sharpe"], 6), "is_ann_return": round(bh_is["ann_return"], 6),
        "is_max_drawdown": round(bh_is["max_drawdown"], 6), "is_exposure": 1.0, "is_n_trades": 0,
        "is_annual_turnover": 0.0, "is_start": common_is_start.date().isoformat(),
        "is_end": work.index[is_mask_c][-1].date().isoformat(), "common_is_start": common_is_start.date().isoformat(),
        "own_is_start": None, "own_is_sharpe": np.nan, "own_is_n": 0, "own_is_valid": False,
        "oos_sharpe": round(bh["sharpe"], 6), "oos_sortino": round(bh["sortino"], 6), "oos_calmar": round(bh["calmar"], 6),
        "oos_ann_return": round(bh["ann_return"], 6), "oos_ann_vol": round(bh["ann_vol"], 6),
        "max_drawdown": round(bh["max_drawdown"], 6), "win_rate": round(bh["win_rate"], 4), "oos_exposure": 1.0,
        "n_trades": 0, "annual_turnover": 0.0, "n_trades_full": 0, "annual_turnover_full": 0.0,
        "is_n": bh_is["n"], "oos_n": bh["n"], "is_eligible": False, "is_ineligible_reason": "benchmark",
        "is_valid": False, "oos_valid": False, "valid": False})
    tourn = pd.DataFrame(rows)
    assert (tourn["signal"] == "BENCHMARK").sum() == 1   # ECON-T4

    valid = tourn[tourn["valid"] & (tourn["signal"] != "BENCHMARK")]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    # ECON-T3 cascade on the IS objective (explicit, not pandas-order dependent)
    keys = ["is_sharpe", "is_ann_return", "is_max_drawdown", "is_n_trades", "signal", "threshold", "strategy", "lead_days"]
    asc = [False, False, False, False, True, True, True, True]
    ranked = valid.sort_values(keys, ascending=asc, kind="mergesort")
    wi = ranked.index[0]
    tied = valid
    tie_step = None
    for step, k in enumerate(["is_sharpe", "is_ann_return", "is_max_drawdown", "is_n_trades"], 1):
        tied = tied[(tied[k] - tourn.loc[wi, k]).abs() <= 1e-9]
        if len(tied) == 1:
            tie_step = step
            break
    if tie_step is None:
        tie_step = 5
    own_pool = tourn[(tourn["own_is_valid"]) & (tourn["signal"] != "BENCHMARK")]
    oi = own_pool["own_is_sharpe"].idxmax()
    legacy_pool = tourn[(tourn["oos_valid"]) & (tourn["signal"] != "BENCHMARK")]
    li = legacy_pool.sort_values(["oos_sharpe", "oos_ann_return", "signal", "threshold"],
                                 ascending=[False, False, True, True], kind="mergesort").index[0]
    nb = tourn["signal"] != "BENCHMARK"
    tourn["is_rank"] = tourn["is_sharpe"].where(nb & tourn["valid"]).rank(ascending=False, method="min")
    tourn["oos_rank"] = tourn["oos_sharpe"].where(nb & tourn["valid"]).rank(ascending=False, method="min")
    write_tournament(tourn, os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv"))
    side_cols = ["signal", "threshold", "strategy", "direction", "lead_days", "is_start", "is_end", "is_n", "is_sharpe",
                 "own_is_start", "own_is_n", "own_is_sharpe", "oos_sharpe", "oos_ann_return", "max_drawdown",
                 "n_trades", "oos_n", "is_rank", "oos_rank"]
    pd.DataFrame([dict(role="primary_is_selected_common_start", **tourn.loc[wi, side_cols].to_dict()),
                  dict(role="sensitivity_is_selected_own_start", **tourn.loc[oi, side_cols].to_dict()),
                  dict(role="legacy_oos_selected", **tourn.loc[li, side_cols].to_dict())]
                 ).to_csv(os.path.join(RESULTS_DIR, f"legacy_oos_selection_{DATE_TAG}.csv"), index=False)

    # distinct position series (P2 ignores the threshold -> identical rows across thresholds)
    distinct = valid.drop_duplicates(["signal", "strategy", "lead_days", "is_sharpe", "oos_sharpe"])
    sp = stats.spearmanr(valid["is_sharpe"], valid["oos_sharpe"]).correlation
    CTX["selection"] = dict(wi=wi, oi=oi, li=li, tie_step=tie_step, tied_rows=list(tied.index) if tie_step == 5 else [],
                            common_is_start=common_is_start, n_cands=len(cands), n_eligible=int(sum(eligible)),
                            n_inel=n_inel, bh_is=bh_is, bh=bh, n_distinct=len(distinct),
                            spearman=float(sp), driver=driver)
    w = tourn.loc[wi]
    print(f"  Tournament: {len(cands)} combos, {len(valid)} IS-valid ({len(distinct)} distinct position series)")
    print(f"  WINNER (IS argmax): {w.signal}/{w.threshold}/{w.strategy}/L{w.lead_days}  IS {w.is_sharpe:.4f}  "
          f"OOS {w.oos_sharpe:.4f}  (B&H IS {bh_is['sharpe']:.4f} OOS {bh['sharpe']:.4f}); tie step {tie_step}")
    lw = tourn.loc[li]
    print(f"  legacy OOS-argmax: {lw.signal}/{lw.threshold}/{lw.strategy}/L{lw.lead_days} OOS {lw.oos_sharpe:.4f}")
    print(f"  Spearman(IS, OOS) over IS-valid = {sp:.3f}")
    CTX["work"] = work
    return tourn


# ─────────────────────────────────────────────────────────────
# STAGE 7: VALIDATION (replays on the FULL series, sliced afterwards)
# ─────────────────────────────────────────────────────────────

@timed("7_validation")
def stage_validation(tourn: pd.DataFrame) -> dict:
    """Walk-forward, bootstrap, costs, decay, stress for the winner and the next IS-ranked
    DISTINCT candidates (top 5 by IS Sharpe). Every replay runs on the full series and is
    sliced afterwards, so rolling windows are warmed up (fix: earlier slices restarted
    504-day windows and dropped ~400 rows)."""
    work = CTX["work"]
    valid = tourn[tourn["valid"] & (tourn["signal"] != "BENCHMARK")]
    distinct = valid.sort_values(["is_sharpe", "signal", "threshold"], ascending=[False, True, True]) \
                    .drop_duplicates(["signal", "strategy", "lead_days", "is_sharpe", "oos_sharpe"])
    wi = CTX["selection"]["wi"]
    top = pd.concat([tourn.loc[[wi]], distinct.drop(index=wi, errors="ignore").head(4)])
    oos_mask = work.index >= OOS_START
    all_wf, all_boot, all_costs, all_decay, all_stress = [], [], [], [], []

    for rank, (idx, row) in enumerate(top.iterrows(), 1):
        sig_name, tname, strat, lead = row["signal"], row["threshold"], row["strategy"], int(row["lead_days"])
        sig_col = SIGNAL_COLS[sig_name]
        tag = dict(rank=rank, signal=sig_name, threshold=tname, strategy=strat, lead_days=lead)
        pos, sr = replay(work, sig_col, tname, strat, lead)

        # 1. Walk-forward (5y train / 1y test). T1 thresholds re-estimated on each train window;
        #    other rules have no fitted parameter. NOTE: regime signals (S6/S7) use IS-fitted
        #    model params (fit through 2019-09), so WF years before 2019-10 are not true
        #    out-of-sample for those signals; years from 2020 are.
        years = sorted(work.index.year.unique())
        for ty in range(max(years[0] + 5, 2005), max(years) + 1):
            ts_s, ts_e = pd.Timestamp(f"{ty}-01-01"), pd.Timestamp(f"{ty}-12-31")
            if tname.startswith("T1_p"):
                train = (work.index >= pd.Timestamp(f"{ty-5}-01-01")) & (work.index < ts_s)
                sig_l = work[sig_col].shift(lead) if lead > 0 else work[sig_col]
                thr = sig_l[train].dropna().quantile(int(tname.split("p")[1]) / 100)
                pw = (sig_l < thr).astype(float).where(sig_l.notna())
                pw = pw if strat == "P1" else pw * 2 - 1
                r = (pw.shift(1) * work["spy_ret"])
            else:
                r = sr
            tr = r[(r.index >= ts_s) & (r.index <= ts_e)].dropna()
            if len(tr) < 20:
                continue
            bh_y = work.loc[(work.index >= ts_s) & (work.index <= ts_e), "spy_ret"].dropna()
            all_wf.append({**tag, "test_year": ty, "oos_sharpe": round(ann_metrics(tr)["sharpe"], 4),
                           "bh_sharpe": round(ann_metrics(bh_y)["sharpe"], 4), "n_obs": len(tr),
                           "is_oos_year": bool(ts_s >= pd.Timestamp(OOS_START) or ty >= 2020)})

        # 2. Bootstrap (iid resample of the deployable OOS series; NOT a selection-bias test)
        oos_r = sr[oos_mask].fillna(0.0)
        rng = np.random.RandomState(42)
        arr = oos_r.values
        bs = np.array([(s.mean() / s.std() * np.sqrt(ANN) if s.std() > 0 else 0)
                       for s in (rng.choice(arr, size=len(arr), replace=True) for _ in range(5000))])
        all_boot.append({**tag, "point_sharpe": round(ann_metrics(oos_r)["sharpe"], 4),
                         "mean_sharpe": round(bs.mean(), 4), "ci_2_5": round(np.percentile(bs, 2.5), 4),
                         "ci_97_5": round(np.percentile(bs, 97.5), 4), "pct_positive": round((bs > 0).mean() * 100, 1),
                         "method": "iid daily resample, 5000 draws, seed 42; ignores autocorrelation and selection"})

        # 3. Transaction costs (cost = |dpos| * bps, charged on the day the position changes)
        for bps in [0, 5, 10, 20, 50]:
            cost = pos.diff().abs().fillna(0) * (bps / 10000)
            net = (sr - cost.shift(1).fillna(0))[oos_mask].fillna(0.0)
            all_costs.append({**tag, "tx_cost_bps": bps, "net_sharpe_approx": round(ann_metrics(net)["sharpe"], 4),
                              "oos_sharpe": round(float(row["oos_sharpe"]), 4)})

        # 4. Signal decay: extra execution delay on top of the traded lead
        for delay in [0, 1, 2, 3, 5]:
            _, dr = replay(work, sig_col, tname, strat, lead + delay)
            all_decay.append({**tag, "execution_delay": delay,
                              "oos_sharpe": round(ann_metrics(dr[oos_mask].fillna(0.0))["sharpe"], 4)})

        # 5. Stress periods (replay on full series, slice to period)
        for pname, ps, pe in [("GFC_2007_2009", "2007-07-01", "2009-03-31"), ("Taper_Tantrum_2013", "2013-05-01", "2013-09-30"),
                              ("COVID_2020", "2020-02-01", "2020-06-30"), ("Rate_Shock_2022", "2022-01-01", "2022-12-31")]:
            pm = (work.index >= ps) & (work.index <= pe)
            s_r = sr[pm].fillna(0.0)
            a, b = ann_metrics(s_r), ann_metrics(work.loc[pm, "spy_ret"])
            all_stress.append({**tag, "period": pname, "start": ps, "end": pe, "sample": "OOS" if ps >= OOS_START else "IS",
                               "strategy_sharpe": round(a["sharpe"], 4), "strategy_max_dd": round(a["max_drawdown"] * 100, 2),
                               "strategy_return": round(float((1 + s_r).prod() - 1), 4),
                               "benchmark_sharpe": round(b["sharpe"], 4), "benchmark_max_dd": round(b["max_drawdown"] * 100, 2),
                               "benchmark_return": round(float((1 + work.loc[pm, 'spy_ret'].fillna(0)).prod() - 1), 4),
                               "n_obs": int(pm.sum())})

    for name, rows in [("walk_forward", all_wf), ("bootstrap_ci", all_boot), ("transaction_costs", all_costs),
                       ("signal_decay", all_decay), ("stress_tests", all_stress)]:
        pd.DataFrame(rows).to_csv(os.path.join(VALIDATION_DIR, f"{name}.csv"), index=False)
    print(f"  Validation rows: wf {len(all_wf)} boot {len(all_boot)} cost {len(all_costs)} "
          f"decay {len(all_decay)} stress {len(all_stress)}")
    w_decay = [r for r in all_decay if r["rank"] == 1]
    w_cost = [r for r in all_costs if r["rank"] == 1]
    bh_oos = CTX["selection"]["bh"]["sharpe"]
    return {
        "max_delay_beating_bh": max([r["execution_delay"] for r in w_decay if r["oos_sharpe"] > bh_oos], default=None),
        "max_delay_positive": max([r["execution_delay"] for r in w_decay if r["oos_sharpe"] > 0], default=0),
        "breakeven_bps": max([r["tx_cost_bps"] for r in w_cost if r["net_sharpe_approx"] > 0], default=0),
    }


# ─────────────────────────────────────────────────────────────
# LOOK-AHEAD AUDIT: published smoothed HMM vs causal HMM, same rule
# ─────────────────────────────────────────────────────────────

@timed("8_lookahead_audit")
def stage_lookahead_audit() -> dict:
    """Score the PREVIOUSLY PUBLISHED rule (S6_hmm_stress / P2, pos.shift(1)) with
    (a) the committed smoothed full-sample HMM probabilities (results/hy_ig_spy/_superseded/signals_20260422.parquet,
        immutable; NOT re-fitted here) and (b) the causal probabilities of this run, at L0 (as
    published) and at the floored L1. Provenance for the narrative's old-vs-new statement."""
    work = CTX["work"]
    old = pd.read_parquet(os.path.join(RESULTS_DIR, "_superseded", f"signals_{DATA_TAG}.parquet"))["hmm_2state_prob_stress"]
    tmp = work[["spy_ret"]].copy()
    tmp["smoothed_fullsample"] = old.reindex(work.index)
    tmp["causal_filtered"] = work["hmm_2state_prob_stress"]
    oos = work.index >= OOS_START
    out = {"rule": "S6_hmm_stress / P2 (trailing-504d min-max sizing) / countercyclical, strat_ret = pos.shift(1) * spy_ret",
           "oos_window": [OOS_START, OOS_END], "rows": []}
    for variant in ["smoothed_fullsample", "causal_filtered"]:
        for lead in (0, 1):
            pos, sr = replay(tmp, variant, "T4_hmm_0.5", "P2", lead)
            r = sr[oos].fillna(0.0)
            a = ann_metrics(r)
            t, p, nw = hac_t_mean(r)
            out["rows"].append({"probabilities": variant, "lead_days": lead, "effective_lag_days": lead + 1,
                                "oos_sharpe": round(a["sharpe"], 4), "oos_ann_return": round(a["ann_return"], 6),
                                "oos_max_drawdown": round(a["max_drawdown"], 6), "hac_t": round(t, 3), "hac_maxlags": nw})
    d = (tmp["smoothed_fullsample"] - tmp["causal_filtered"])[oos]
    out["corr_smoothed_minus_filtered_vs_next_day_spy_ret_oos"] = round(
        float(d.corr(work["spy_ret"].shift(-1)[oos])), 4)
    out["bh_oos_sharpe"] = round(CTX["selection"]["bh"]["sharpe"], 4)
    with open(os.path.join(RESULTS_DIR, f"hmm_lookahead_audit_{DATE_TAG}.json"), "w") as f:
        json.dump(out, f, indent=2)
    for r in out["rows"]:
        print(f"  {r['probabilities']:20s} L{r['lead_days']}: OOS Sharpe {r['oos_sharpe']:.4f}  HAC t {r['hac_t']:.2f}")
    CTX["audit"] = out
    return out


# ─────────────────────────────────────────────────────────────
# WINNER ARTIFACTS
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
    "S6_hmm_stress":     "HMM Stress Probability (causal)",
    "S7_ms_stress":      "Markov-Switching Stress Probability (causal)",
    "S10_mom_21d":       "HY-IG 21-Day Momentum",
    "S11_mom_63d":       "HY-IG 63-Day Momentum",
    "S12_mom_252d":      "HY-IG 252-Day Momentum",
    "S13_acceleration":  "HY-IG Acceleration",
}
THRESHOLD_DISPLAY = {
    "T1_p75": "75th percentile (IS, fixed)", "T1_p85": "85th percentile (IS, fixed)",
    "T1_p95": "95th percentile (IS, fixed)", "T2_rp75": "75th pct (rolling 504d)",
    "T2_rp85": "85th pct (rolling 504d)", "T2_rp95": "95th pct (rolling 504d)",
    "T3_z1.5": "Rolling 504d z-score > 1.5", "T3_z2.0": "Rolling 504d z-score > 2.0",
    "T3_z2.5": "Rolling 504d z-score > 2.5",
    "T4_hmm_0.5": "HMM prob >= 0.5", "T4_hmm_0.7": "HMM prob >= 0.7",
    "T5_ms_0.5": "MS prob >= 0.5", "T5_ms_0.7": "MS prob >= 0.7",
}
STRATEGY_DISPLAY = {"P1": "Long/Cash", "P2": "Signal Strength", "P3": "Long/Short"}
STRATEGY_FAMILY = {"P1": "P1_long_cash", "P2": "P2_signal_strength", "P3": "P3_long_short"}
STRATEGY_DESC = {
    "P1": "Hold SPY when the signal is below its threshold; hold cash otherwise.",
    "P2": "Size SPY exposure (0%-100%) as 1 minus the signal's position inside its trailing 504-day min-max range; the threshold label is not used.",
    "P3": "Long SPY when the signal is below its threshold; short SPY otherwise.",
}


def _threshold_value(tname, sig_col, work, lead):
    if tname.startswith(("T4_", "T5_")):
        return float(tname.rsplit("_", 1)[1]), "lt"
    if tname.startswith("T1_p"):
        sig_l = work[sig_col].shift(lead)
        return round(float(sig_l[work.index <= IS_END].dropna().quantile(int(tname.split("p")[1]) / 100)), 4), "lt"
    if tname.startswith("T3_z"):
        return float(tname.split("z")[1]), "lt"
    if tname.startswith("T2_rp"):   # moving boundary: report its LATEST value (threshold_note says so)
        sig_l = work[sig_col].shift(lead)
        q = sig_l.rolling(504, min_periods=400).quantile(int(tname.split("rp")[1]) / 100).dropna()
        return (round(float(q.iloc[-1]), 4) if len(q) else None), "lt"
    return None, "lt"


def _episodes():
    reg = json.loads((REPO / "docs/schemas/episode_registry.json").read_text())
    meta = json.loads(Path(RESULTS_DIR, "interpretation_metadata.json").read_text())
    return reg.get(meta.get("indicator_category", meta.get("indicator_type", "")), reg["_fallback"])


@timed("9_winner_artifacts")
def stage_winner_artifacts(tourn: pd.DataFrame, vinfo: dict):
    work = CTX["work"]
    S = CTX["selection"]
    wi, oi, li = S["wi"], S["oi"], S["li"]
    w = tourn.loc[wi]
    bm = tourn[tourn["signal"] == "BENCHMARK"].iloc[0]
    sig_name, tname, strat, lead = w["signal"], w["threshold"], w["strategy"], int(w["lead_days"])
    sig_col = SIGNAL_COLS[sig_name]
    oos_mask = work.index >= OOS_START
    now_iso = iso_utc_now()

    pos, sr = replay(work, sig_col, tname, strat, lead)
    oos_r = sr[oos_mask].fillna(0.0)
    m = ann_metrics(oos_r)
    assert abs(m["sharpe"] - float(w["oos_sharpe"])) < 1e-6, "winner replay != tournament row"
    t_oos, p_oos, nw_oos = hac_t_mean(oos_r)
    is_r = sr[(work.index >= S["common_is_start"]) & (work.index < OOS_START)].dropna()
    t_is, p_is, nw_is = hac_t_mean(is_r)
    n_distinct = S["n_distinct"]
    exp_max_z = float(stats.norm.ppf(1 - 0.5 / max(n_distinct, 1)))
    tval, trule = _threshold_value(tname, sig_col, work, lead)
    valid = tourn[tourn["valid"] & (tourn["signal"] != "BENCHMARK")]
    runner = valid.drop(index=wi).sort_values(["is_sharpe", "signal", "threshold"], ascending=[False, True, True]).head(1)
    runner_d = valid.drop(index=wi)
    runner_d = runner_d[~((runner_d["signal"] == sig_name) & (runner_d["strategy"] == strat)
                          & (runner_d["lead_days"] == lead) & ((runner_d["is_sharpe"] - w["is_sharpe"]).abs() < 1e-12))]
    runner_d = runner_d.sort_values(["is_sharpe", "signal", "threshold"], ascending=[False, True, True]).head(1)

    def _row(r):
        return {"signal": str(r["signal"]), "threshold": str(r["threshold"]), "strategy": str(r["strategy"]),
                "lead_value": int(r["lead_days"]), "objective_value": round(float(r["is_sharpe"]), 6),
                "oos_sharpe": round(float(r["oos_sharpe"]), 6)}

    is_window = {"start": str(w["is_start"]), "end": str(w["is_end"]), "n": int(w["is_n"]),
                 "common_is_start": S["common_is_start"].date().isoformat(), "oos_start": OOS_START,
                 "min_is_n": MIN_IS_N, "n_candidates": S["n_cands"], "n_eligible": S["n_eligible"],
                 "n_ineligible_short_history": S["n_inel"],
                 "common_start_set_by": S["driver"],
                 "rule": ("eligibility before alignment: a candidate is IS-eligible only if its own first valid return "
                          f"leaves >= {MIN_IS_N} IS observations; common_is_start = latest first-valid-return date among "
                          "eligible candidates; IS metrics for every candidate computed on [common_is_start, oos_start)"),
                 "validity": ("IS window only: is_n >= MIN_IS_N, IS exposure in [0.05, 0.95] (P3: share of days long), "
                              "IS std > 0, IS annual turnover < 24, IS trades >= 10; OOS never consulted"),
                 "bh_is_sharpe": round(float(S["bh_is"]["sharpe"]), 6)}
    selection = {
        "objective": "max_is_sharpe",
        "objective_formula": ("in-sample (common window [common_is_start, OOS start)) daily mean/std*sqrt(252) of "
                              "pos.shift(1)*spy_ret; winner evaluated on the OOS window with ECON-T4 deployable scoring (fillna 0)"),
        "is_window": is_window,
        "grid_scanned": {"leads": LEADS, "n_signals": int(valid["signal"].nunique()),
                         "n_thresholds": int(valid["threshold"].nunique()), "n_strategies": int(valid["strategy"].nunique()),
                         "n_combos": int(S["n_cands"]), "n_valid_combos": int(len(valid)),
                         "n_distinct_position_series": int(n_distinct),
                         "median_valid_objective": round(float(valid["is_sharpe"].median()), 6),
                         "spearman_is_vs_oos": round(S["spearman"], 4)},
        "tie_break_step": S["tie_step"],
        "raw_winner_row": {"signal": sig_name, "threshold": tname, "strategy": strat, "lead_column": "lead_days",
                           "lead_value": lead, "source_tournament_file": f"tournament_results_{DATE_TAG}.csv",
                           "source_row_index": int(wi),
                           "display_alias": f"strategy_family={STRATEGY_FAMILY[strat]} (raw strategy={strat})"},
        "runner_up": _row(runner.iloc[0]) if len(runner) else None,
        "runner_up_distinct_series": _row(runner_d.iloc[0]) if len(runner_d) else None,
        "rationale": ("Winner is the IS-valid row with the highest IN-SAMPLE Sharpe (common IS window) over the published "
                      "floored daily grid; OOS metrics are reported for that row only (no OOS look-ahead in selection). "
                      "Regime signals (S6 HMM, S7 Markov-switching) are IS-fit and forward-filtered (scripts/_regime_causal.py)."),
        "legacy_oos_selected_row": {"signal": str(tourn.loc[li, "signal"]), "threshold": str(tourn.loc[li, "threshold"]),
                                    "strategy": str(tourn.loc[li, "strategy"]), "direction": "countercyclical",
                                    "lead_value": int(tourn.loc[li, "lead_days"]),
                                    "oos_sharpe": round(float(tourn.loc[li, "oos_sharpe"]), 6),
                                    "note": f"OOS-argmax on this grid (pre-GH#251 rule), comparison only; see legacy_oos_selection_{DATE_TAG}.csv"},
        "sensitivity_own_is_start_row": {"signal": str(tourn.loc[oi, "signal"]), "threshold": str(tourn.loc[oi, "threshold"]),
                                         "strategy": str(tourn.loc[oi, "strategy"]), "direction": "countercyclical",
                                         "lead_value": int(tourn.loc[oi, "lead_days"]),
                                         "own_is_start": str(tourn.loc[oi, "own_is_start"]),
                                         "own_is_sharpe": round(float(tourn.loc[oi, "own_is_sharpe"]), 6),
                                         "oos_sharpe": round(float(tourn.loc[oi, "oos_sharpe"]), 6),
                                         "note": "IS argmax without common-start alignment; sensitivity only"},
        "previously_published": {"combo": "S6_hmm_stress/T4_hmm_0.5/P2/L0", "oos_sharpe": 1.4083, "hac_t": 3.80,
                                 "source": "winner_summary.json 2026-07-15 (tournament_results_20260715.csv)",
                                 "status": "superseded: relied on full-sample, forward-backward smoothed HMM probabilities (look-ahead) and an L0 grid below the OAS publication lag",
                                 "audit_file": f"hmm_lookahead_audit_{DATE_TAG}.json"},
        "inference": {"oos_hac_t": round(t_oos, 3), "oos_hac_p": round(p_oos, 4), "oos_hac_maxlags": nw_oos,
                      "is_hac_t": round(t_is, 3), "is_hac_maxlags": nw_is,
                      "n_distinct_candidates": int(n_distinct),
                      "expected_max_abs_z_under_null": round(exp_max_z, 2),
                      "note": "expected max |z| = Phi^-1(1 - 0.5/N) over N distinct position series (two-sided, independence approximation)"},
        "objective_runner_up_divergence": None,
    }
    if S["tie_step"] and S["tie_step"] > 1:
        tied = tourn.loc[S["tied_rows"]] if S["tied_rows"] else tourn.loc[[wi]]
        note = [f"# Tournament tie note — {PAIR_ID} ({DATE_TAG})", "",
                f"Resolved at ECON-T3 step {S['tie_step']} (IS objective cascade: is_sharpe, is_ann_return, "
                "is_max_drawdown, is_n_trades, then lexicographic signal/threshold/strategy/lead).", "",
                "| signal | threshold | strategy | lead_days | is_sharpe | oos_sharpe |", "|---|---|---|---|---|---|"]
        for _, r in tied.iterrows():
            note.append(f"| {r.signal} | {r.threshold} | {r.strategy} | {r.lead_days} | {r.is_sharpe:.6f} | {r.oos_sharpe:.6f} |")
        note += ["", ("The tied rows are the same position series: strategy P2 sizes on the signal's trailing 504-day "
                      "min-max range and does not use the threshold, so every threshold label produces identical "
                      "positions. The lexicographic step picks a label; the traded rule is the same.")]
        Path(RESULTS_DIR, "tournament_tie_note.md").write_text("\n".join(note) + "\n")

    n_tr_oos, to_oos = trade_stats(pos, oos_mask)
    n_tr_full, to_full = trade_stats(pos, np.ones(len(pos), dtype=bool))
    beats = "above" if m["sharpe"] > float(bm["oos_sharpe"]) else "below"
    winner_summary = {
        "pair_id": PAIR_ID, "generated_at": now_iso, "schema_version": "1.2.0",
        "signal_column": sig_col, "signal_code": sig_name, "signal_display_name": SIGNAL_DISPLAY[sig_name],
        "target_symbol": "SPY",
        "threshold_value": tval, "threshold_rule": trule, "threshold_code": tname,
        **({"threshold_window_days": 504, "threshold_min_periods": 400} if tname.startswith("T2_rp") else {}),
        "threshold_display_name": THRESHOLD_DISPLAY.get(tname, tname),
        "threshold_note": ("P2 does not use the threshold: position = 1 - (signal - min504)/(max504 - min504); "
                           "the label is the tie-break pick among identical P2 rows" if strat == "P2" else
                           (f"Moving boundary: trailing-504-day {tname.split('rp')[1]}th percentile of the lead-shifted "
                            f"signal; threshold_value is its latest value ({OOS_END})" if tname.startswith("T2_rp") else None)),
        "strategy_family": STRATEGY_FAMILY[strat], "strategy_code": strat,
        "strategy_display_name": STRATEGY_DISPLAY[strat], "strategy_description": STRATEGY_DESC[strat],
        "direction": "countercyclical",
        "lead_value": lead, "lead_unit": "days",
        "lead_description": f"{lead} trading day(s) signal lead + 1-day execution lag = {lead + 1} trading days effective",
        "oos_sharpe": round(m["sharpe"], 4), "oos_sortino": round(m["sortino"], 4), "oos_calmar": round(m["calmar"], 4),
        "oos_ann_return": round(m["ann_return"], 6), "oos_ann_vol": round(m["ann_vol"], 6),
        "oos_max_drawdown": round(m["max_drawdown"], 6), "oos_win_rate": round(m["win_rate"], 4),
        "win_rate": round(float((oos_r[oos_r != 0] > 0).mean()), 4),
        "oos_n_trades": n_tr_oos, "oos_annual_turnover": round(to_oos, 2),
        "annual_turnover": round(to_oos, 2),
        "full_sample_n_trades": n_tr_full, "full_sample_annual_turnover": round(to_full, 2),
        "oos_n": int(m["n"]), "oos_period_start": OOS_START, "oos_period_end": OOS_END,
        "oos_hac_t": round(t_oos, 3),
        "is_sharpe": round(float(w["is_sharpe"]), 6), "is_n": int(w["is_n"]),
        "is_period_start": is_window["start"], "is_period_end": is_window["end"],
        "bh_sharpe": round(float(bm["oos_sharpe"]), 4), "bh_ann_return": round(float(bm["oos_ann_return"]), 6),
        "bh_max_drawdown": round(float(bm["max_drawdown"]), 6), "bh_is_sharpe": round(float(bm["is_sharpe"]), 4),
        "cost_assumption_bps": 5.0,
        "total_combos": int(S["n_cands"]), "valid_combos": int(len(valid)),
        "max_acceptable_delay_days": vinfo["max_delay_positive"],
        "max_delay_beating_bh_days": vinfo["max_delay_beating_bh"],
        "breakeven_cost_bps": float(vinfo["breakeven_bps"]),
        "risk_category": "credit_spread",
        "notes": (f"Winner {sig_name}/{tname}/{strat}/L{lead} selected by in-sample Sharpe on the common IS window "
                  f"{is_window['start']}..{is_window['end']} (IS Sharpe {float(w['is_sharpe']):.4f}; SPY {float(bm['is_sharpe']):.4f}) "
                  f"and evaluated on the held-out OOS window {OOS_START}..{OOS_END}: OOS Sharpe {m['sharpe']:.4f} "
                  f"vs SPY buy-and-hold {float(bm['oos_sharpe']):.4f} ({beats}). Grid floored at L1 (OAS publication lag). "
                  f"Supersedes S6_hmm_stress/T4_hmm_0.5/P2/L0 (1.4083), which used smoothed full-sample HMM probabilities."),
        "selection": selection,
    }
    with open(os.path.join(RESULTS_DIR, "winner_summary.json"), "w") as f:
        json.dump(winner_summary, f, indent=2)
        f.write("\n")
    print(f"  winner_summary.json: {sig_name}/{tname}/{strat}/L{lead} IS {w['is_sharpe']:.4f} OOS {m['sharpe']:.4f} "
          f"HAC t {t_oos:.2f}; B&H {bm['oos_sharpe']:.4f}")

    tournament_winner = {
        "pair_id": PAIR_ID, "generated_at": now_iso, "winner_signal": sig_name, "winner_threshold": tname,
        "winner_strategy": strat, "lead_days": lead, "selection_objective": "max_is_sharpe",
        "is_sharpe": round(float(w["is_sharpe"]), 4), "oos_sharpe": round(m["sharpe"], 4),
        "oos_ann_return": round(m["ann_return"], 6), "oos_max_drawdown": round(m["max_drawdown"], 6),
        "oos_n_trades": n_tr_oos, "oos_period_start": OOS_START, "oos_period_end": OOS_END,
        "bh_sharpe": round(float(bm["oos_sharpe"]), 4), "bh_ann_return": round(float(bm["oos_ann_return"]), 6),
        "bh_max_drawdown": round(float(bm["max_drawdown"]), 6),
        "delta_sharpe": round(m["sharpe"] - float(bm["oos_sharpe"]), 4),
        "delta_ann_return": round(m["ann_return"] - float(bm["oos_ann_return"]), 6),
        "delta_mdd": round(m["max_drawdown"] - float(bm["max_drawdown"]), 6),
        "source_tournament_file": f"tournament_results_{DATE_TAG}.csv",
    }
    with open(os.path.join(RESULTS_DIR, "tournament_winner.json"), "w") as f:
        json.dump(tournament_winner, f, indent=2)

    oos_record = {
        "pair_id": PAIR_ID, "owner": "evan", "split_policy_id": "v1_max36_25pct_cap120",
        "in_sample_end": IS_END, "oos_start": OOS_START, "oos_end": OOS_END,
        "sample_size_months": 316, "oos_span_months": 79,
        "justification": ("Total sample 2000-01-03 to 2026-04-22 ~ 316 months. ECON-OOS2 formula: span = "
                          "min(max(36, round(316x0.25)), 120) = 79 months. OOS window 2019-10-01 to 2026-04-22. "
                          "The dot-com bust (2000-02) and the GFC (2007-09) are in-sample; the COVID shock (2020) and "
                          "the 2022 rate shock are out-of-sample. Regime models (HMM, Markov-switching) and fixed "
                          "thresholds are estimated on in-sample data only; the tournament winner is selected on "
                          f"in-sample Sharpe over the common IS window starting {is_window['common_is_start']}."),
        "generated_at": now_iso,
    }
    with open(os.path.join(RESULTS_DIR, "oos_split_record.json"), "w") as f:
        json.dump(oos_record, f, indent=2)

    # ── canonical daily series (ECON-SR1) ──
    sr_df = pd.DataFrame({"date": work.index.strftime("%Y-%m-%d"), "position": pos.values,
                          "strategy_return": sr.fillna(0.0).values, "bh_return": work["spy_ret"].values,
                          "sample": np.where(oos_mask, "OOS", "IS")})
    sr_df.to_csv(os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv"), index=False)
    chk = ann_metrics(sr_df.loc[oos_mask, "strategy_return"])["sharpe"]
    print(f"  [ECON-SR1] strategy_returns OOS Sharpe {chk:.4f} vs winner {m['sharpe']:.4f} -> "
          f"{'RECONCILES' if abs(chk - m['sharpe']) <= 0.01 else 'MISMATCH'}")

    # ── trade logs (full sample, each trade tagged IS/OOS) ──
    pc = pos.dropna()
    chg = pc.diff().fillna(pc.iloc[0])
    entries = chg[chg.abs() > 0.05].index
    cum = (1 + sr.fillna(0)).cumprod()
    trades, broker = [], []
    for i, ed in enumerate(entries):
        xd = entries[i + 1] if i + 1 < len(entries) else work.index[-1]
        ep = float(pos.loc[ed])
        tr = float(cum.loc[xd] / cum.loc[ed] - 1) if cum.loc[ed] != 0 else 0.0
        side = "Long" if ep > 0 else ("Short" if ep < 0 else "Cash")
        smp = "OOS" if ed >= pd.Timestamp(OOS_START) else "IS"
        trades.append({"entry_date": ed.strftime("%Y-%m-%d"), "exit_date": xd.strftime("%Y-%m-%d"), "direction": side,
                       "position": round(ep, 4), "holding_days": (xd - ed).days,
                       "trade_return_pct": round(tr * 100, 2), "sample": smp})
        broker.append({"trade_id": i + 1, "entry_date": ed.strftime("%Y-%m-%d"), "exit_date": xd.strftime("%Y-%m-%d"),
                       "direction": side, "qty_pct": round(ep * 100, 2), "notional_usd": round(ep * 10_000.0, 2),  # $10,000 stake (Strategy page text)
                       "price_entry": round(float(work.loc[ed, "spy"]), 2), "holding_days": (xd - ed).days,
                       "trade_return_pct": round(tr * 100, 2), "signal_code": sig_name, "threshold_code": tname,
                       "strategy_code": strat, "signal_value": round(float(work.loc[ed, sig_col]) if lead == 0 else
                                                                      float(work[sig_col].shift(lead).loc[ed]), 6),
                       "sample": smp})
    pd.DataFrame(trades).to_csv(os.path.join(RESULTS_DIR, "winner_trade_log.csv"), index=False)
    pd.DataFrame(broker).to_csv(os.path.join(RESULTS_DIR, "winner_trades_broker_style.csv"), index=False)
    print(f"  trade logs: {len(trades)} position changes (OOS {sum(t['sample']=='OOS' for t in trades)})")

    # ── ECON-SR3 / CP1 sidecars from the canonical series ──
    strat_ret = pd.Series(sr_df["strategy_return"].values, index=work.index)
    rs = (strat_ret.rolling(504, min_periods=252).mean() / strat_ret.rolling(504, min_periods=252).std()) * np.sqrt(ANN)
    rs = rs[pos.notna().cumsum() > 252].dropna()
    pd.DataFrame({"date": rs.index.strftime("%Y-%m-%d"), "rolling_sharpe_24m": rs.values}).to_csv(
        os.path.join(RESULTS_DIR, f"rolling_sharpe_{PAIR_ID}.csv"), index=False)
    sub_rows = []
    for ep in _episodes() + [{"label": "Full IS (common window)", "start": is_window["common_is_start"], "end": IS_END},
                             {"label": "Full OOS", "start": OOS_START, "end": OOS_END}]:
        pm = (work.index >= ep["start"]) & (work.index <= ep["end"]) & pos.shift(1).notna().values
        a = ann_metrics(strat_ret[pm])
        if a["n"] < 126:   # < ~6 months of traded days: not reported (position undefined / warm-up)
            a = {k: (np.nan if k != "n" else a["n"]) for k in a}
        sub_rows.append({"period_name": ep["label"], "start_date": ep["start"], "end_date": ep["end"],
                         "is_oos": bool(pd.Timestamp(ep["start"]) >= pd.Timestamp(OOS_START)),
                         "ann_return": round(a["ann_return"], 4), "ann_vol": round(a["ann_vol"], 4),
                         "sharpe": round(a["sharpe"], 4), "n_obs": int(a["n"]), "max_drawdown": round(a["max_drawdown"], 4),
                         "bh_sharpe": (round(ann_metrics(work.loc[pm, "spy_ret"])["sharpe"], 4)
                                       if a["n"] >= 126 else np.nan)})
    pd.DataFrame(sub_rows).to_csv(os.path.join(RESULTS_DIR, "subperiod_sharpe.csv"), index=False)
    sig_lag = (work[sig_col].shift(lead + 1)).rename("sig")
    rc = sig_lag.rolling(504, min_periods=252).corr(work["spy_ret"]).dropna()
    pd.DataFrame({"date": rc.index.strftime("%Y-%m-%d"), "rolling_corr_24m": rc.values}).to_csv(
        os.path.join(RESULTS_DIR, f"rolling_correlation_{PAIR_ID}.csv"), index=False)
    _structural_break(work, sig_lag)
    _rolling_granger(work, sig_col)
    sd = pd.DataFrame({"date": work.index.strftime("%Y-%m-%d"), "signal_value": work[sig_col].values,
                       "signal_value_lagged": work[sig_col].shift(lead).values,
                       "sample": np.where(oos_mask, "OOS", "IS"), "threshold": tval, "position": pos.values})
    sd.to_csv(os.path.join(RESULTS_DIR, f"signal_dist_{PAIR_ID}.csv"), index=False)
    CTX["winner"] = dict(row=w, pos=pos, sr=sr, m=m, t_oos=t_oos, t_is=t_is, ws=winner_summary)
    return winner_summary


def _structural_break(work, sig_lag):
    """Quandt likelihood-ratio (sup-Wald) test for a break in spy_ret_t = a + b*signal_{t-L-1}:
    HAC-robust Wald (q=2: intercept and slope shift) at monthly candidate dates, 15% trimming.
    Critical values: Andrews (1993) / Stock-Watson Table 14.5 (F-form, q=2): 10% 5.00, 5% 5.86, 1% 7.78.
    No p-value is reported (the asymptotic sup-F distribution is non-standard)."""
    import statsmodels.api as sm
    d = pd.concat([work["spy_ret"].rename("y"), sig_lag], axis=1).dropna()
    n = len(d)
    lo, hi = int(0.15 * n), int(0.85 * n)
    cands = d.index[lo:hi]
    cands = cands[~cands.to_period("M").duplicated()]
    best = (None, -np.inf)
    for bd in cands:
        D = (d.index >= bd).astype(float)
        X = pd.DataFrame({"c": 1.0, "s": d["sig"], "Dc": D, "Ds": D * d["sig"]}, index=d.index)
        r = sm.OLS(d["y"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
        F = float(r.wald_test("Dc = 0, Ds = 0", scalar=True).statistic) / 2.0
        if F > best[1]:
            best = (bd, F)
    out = {"test": "QLR sup-Wald (HAC, q=2, 15% trim, monthly candidates)", "breakpoint_date": best[0].date().isoformat(),
           "max_f_stat": round(best[1], 4), "p_value": None,
           "critical_values_f_form": {"10%": 5.00, "5%": 5.86, "1%": 7.78},
           "conclusion": (f"sup-F {best[1]:.2f} at {best[0].date()} "
                          f"{'exceeds' if best[1] > 5.86 else 'does not exceed'} the 5% critical value 5.86"),
           "regression": "spy_ret_t on winner signal lagged lead+1 days", "trim_pct": 0.15, "n_obs": n}
    with open(os.path.join(RESULTS_DIR, f"structural_break_{PAIR_ID}.json"), "w") as f:
        json.dump(out, f, indent=2)


def _rolling_granger(work, sig_col):
    """Rolling 504-day Granger test (does the winner signal help predict SPY daily returns, lags 1-3),
    evaluated every 5 trading days to bound run time. Reported: max F over lags and its p-value."""
    from statsmodels.tsa.stattools import grangercausalitytests
    d = pd.concat([work["spy_ret"].rename("tgt"), work[sig_col].rename("sig")], axis=1).dropna()
    rows = []
    for i in range(504, len(d), 5):
        sub = d.iloc[i - 504:i]
        try:
            g = grangercausalitytests(sub[["tgt", "sig"]], maxlag=3, verbose=False)
            fs = [g[k][0]["ssr_ftest"][0] for k in (1, 2, 3)]
            ps = [g[k][0]["ssr_ftest"][1] for k in (1, 2, 3)]
            j = int(np.argmax(fs))
            rows.append({"date": d.index[i - 1].strftime("%Y-%m-%d"), "granger_f_24m": round(fs[j], 6),
                         "p_value_24m": round(ps[j], 6)})
        except Exception:
            continue
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, f"rolling_granger_{PAIR_ID}.csv"), index=False)


# ─────────────────────────────────────────────────────────────
# LEAD-AXIS ARTIFACTS (daily axis; replaces refresh_hy_ig_spy_lead_artifacts.py)
# ─────────────────────────────────────────────────────────────

@timed("10_lead_artifacts")
def stage_lead_artifacts(tourn: pd.DataFrame):
    work = CTX["work"]
    w = CTX["winner"]["row"]
    valid = tourn[tourn["valid"] & (tourn["signal"] != "BENCHMARK")].copy()
    native = valid.copy()
    native["lead_source"] = "pipeline"
    native[["signal", "threshold", "strategy", "signal_column", "lead_days", "is_sharpe", "oos_sharpe",
            "max_drawdown", "n_trades", "valid", "lead_source"]].to_csv(
        os.path.join(RESULTS_DIR, f"lead_tournament_native_{DATE_TAG}.csv"), index=False)

    same = tourn[(tourn["signal"] == w["signal"]) & (tourn["threshold"] == w["threshold"])
                 & (tourn["strategy"] == w["strategy"])].set_index("lead_days")
    wc = pd.DataFrame([{"lead_days": L, "is_sharpe": round(float(same.loc[L, "is_sharpe"]), 4),
                        "oos_sharpe": round(float(same.loc[L, "oos_sharpe"]), 4),
                        "is_valid": bool(same.loc[L, "valid"]),
                        "is_published_winner": L == int(w["lead_days"]), "lead_source": "pipeline"} for L in LEADS])
    wc.to_csv(os.path.join(RESULTS_DIR, f"lead_winner_curve_{DATE_TAG}.csv"), index=False)

    env_rows, agg_rows = [], []
    for L in LEADS:
        g = valid[valid["lead_days"] == L]
        pool = pd.concat([g, tourn[(tourn["signal"] == w["signal"]) & (tourn["threshold"] == w["threshold"])
                                   & (tourn["strategy"] == w["strategy"]) & (tourn["lead_days"] == L)]])
        b = pool.loc[pool["oos_sharpe"].idxmax()]
        bi = g.loc[g["is_sharpe"].idxmax()] if len(g) else b
        env_rows.append({"lead_days": L, "best_oos_sharpe": round(float(b["oos_sharpe"]), 4),
                         "best_signal": b["signal"], "best_threshold": b["threshold"], "best_strategy": b["strategy"],
                         "is_best_signal": bi["signal"], "is_best_strategy": bi["strategy"],
                         "is_best_is_sharpe": round(float(bi["is_sharpe"]), 4),
                         "is_best_oos_sharpe": round(float(bi["oos_sharpe"]), 4),
                         "note": "best_oos_sharpe is an OOS-argmax (selection-biased context); is_best_* is the IS-selected row"})
        if len(g):
            agg_rows.append({"lead_days": L, "n_valid": len(g), "best_oos_sharpe": round(float(g["oos_sharpe"].max()), 4),
                             "median_oos_sharpe": round(float(g["oos_sharpe"].median()), 4),
                             "p25_oos_sharpe": round(float(g["oos_sharpe"].quantile(.25)), 4),
                             "p75_oos_sharpe": round(float(g["oos_sharpe"].quantile(.75)), 4),
                             "best_is_sharpe": round(float(g["is_sharpe"].max()), 4),
                             "median_is_sharpe": round(float(g["is_sharpe"].median()), 4),
                             "is_best_signal": bi["signal"], "is_best_threshold": bi["threshold"],
                             "is_best_strategy": bi["strategy"], "is_best_oos_sharpe": round(float(bi["oos_sharpe"]), 4),
                             "best_signal": g.loc[g["oos_sharpe"].idxmax(), "signal"],
                             "best_threshold": g.loc[g["oos_sharpe"].idxmax(), "threshold"],
                             "best_strategy": g.loc[g["oos_sharpe"].idxmax(), "strategy"],
                             "best_max_dd": round(float(g.loc[g["oos_sharpe"].idxmax(), "max_drawdown"]), 6)})
    env = pd.DataFrame(env_rows)
    env.to_csv(os.path.join(RESULTS_DIR, f"lead_clean_envelope_{DATE_TAG}.csv"), index=False)
    pd.DataFrame(agg_rows).to_csv(os.path.join(RESULTS_DIR, f"lead_tournament_{DATE_TAG}.csv"), index=False)
    for L in LEADS:
        if float(wc.loc[wc.lead_days == L, "oos_sharpe"].iloc[0]) > float(env.loc[env.lead_days == L, "best_oos_sharpe"].iloc[0]) + 1e-9:
            raise SystemExit(f"COHERENCE VIOLATION at L{L}")

    # daily lead-lag Pearson r: signal lagged L (+1 execution day) vs SPY next-day return
    spy_next = work["spy_ret"].shift(-1)
    corr_rows = []
    for sig_name, col in SIGNAL_COLS.items():
        if col not in work.columns:
            continue
        row, best = {"transform": col}, (None, 0.0)
        for L in LEADS:
            dd = pd.concat([work[col].shift(L), spy_next], axis=1).dropna()
            r, p = stats.pearsonr(dd.iloc[:, 0], dd.iloc[:, 1])
            row[f"L{L}"] = f"{r:+.4f}" + ("**" if p < 0.01 else "*" if p < 0.05 else "")
            if abs(r) > abs(best[1]):
                best = (L, r)
        row["best_lead"], row["best_r"] = best[0], round(float(best[1]), 4)
        corr_rows.append(row)
    pd.DataFrame(corr_rows).to_csv(os.path.join(RESULTS_DIR, f"lead_correlation_{DATE_TAG}.csv"), index=False)
    print(f"  lead artifacts written (winner curve OOS: {dict(zip(wc.lead_days, wc.oos_sharpe))})")


# ─────────────────────────────────────────────────────────────
# METADATA, SCOPE, SUGGESTIONS, HANDOFFS
# ─────────────────────────────────────────────────────────────

@timed("11_metadata")
def stage_metadata():
    now_iso = iso_utc_now()
    ws = CTX["winner"]["ws"]
    # interpretation_metadata.json — Evan-owned fields only (observed_direction, direction_consistent,
    # key_finding, confidence). Direction = the traded rule's orientation (all candidates countercyclical).
    meta_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    meta = json.loads(Path(meta_path).read_text())
    reg = pd.read_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"))
    lvl = reg[reg["signal"] == "hy_ig_spread_pct"].set_index("horizon")
    meta["observed_direction"] = ws["direction"]
    meta["direction_consistent"] = ws["direction"] == meta.get("expected_direction", "countercyclical")
    meta["key_finding"] = (
        f"In-sample-selected winner {ws['signal_code']}/{ws['threshold_code']}/{ws['strategy_code']}/L{ws['lead_value']} "
        f"(lead {ws['lead_value']} trading day(s) + 1-day execution lag): IS Sharpe {ws['is_sharpe']:.2f} "
        f"(SPY {ws['bh_is_sharpe']:.2f}), OOS Sharpe {ws['oos_sharpe']:.2f} vs SPY buy-and-hold {ws['bh_sharpe']:.2f}. "
        f"Spread level vs 63-day forward SPY return: coef {lvl.loc['spy_fwd_63d','coef']:.4f}, "
        f"HAC t {lvl.loc['spy_fwd_63d','t_stat']:.2f} (p={lvl.loc['spy_fwd_63d','p_value']:.3f}). "
        f"The previously published 1.41 (S6_hmm_stress/P2/L0) used smoothed full-sample HMM probabilities (look-ahead).")
    meta["confidence"] = "low" if ws["oos_sharpe"] <= ws["bh_sharpe"] else "medium"
    meta["last_updated_by"] = "evan"
    meta["last_updated_at"] = now_iso
    Path(meta_path).write_text(json.dumps(meta, indent=2) + "\n")

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
                {"name":"hmm_2state_prob_stress","definition":"Causal 2-state HMM stress probability: GaussianHMM on [daily HY-IG spread change, VIX], fit on in-sample data only (to 2019-09-30) with in-sample standardisation; forward-filtered P(stress_t | data up to t). Stress = state with the higher in-sample mean spread change.","formula":"scripts/_regime_causal.fit_hmm_causal(features=[spread_change, vix], oos_start=2019-10-01, seeds=(42,0,1,2,3))","role":"regime_state","appears_in_charts":["hmm_regime_overlay"]},
                {"name":"ms_2state_stress_prob","definition":"Causal Markov-switching probability of the high-variance regime of daily HY-IG spread changes (SPY returns not in the likelihood); in-sample fit, Hamilton-filtered.","formula":"scripts/_regime_causal.fit_ms_causal(spread_change, oos_start=2019-10-01, k_regimes=2, switching_variance=True)","role":"regime_state","appears_in_charts":["hmm_regime_overlay"]},
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
            "Scope-disciplined per ECON-SD. All 16 indicator derivatives (incl. hmm_2state_prob_calm in the signals parquet) are "
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

    w = CTX["winner"]
    handoff = f"""# Evan handoff: {PAIR_ID} ({DATE_TAG}) — causal regime rebuild

- Winner (IS argmax, common IS window {ws['is_period_start']}..{ws['is_period_end']}): **{ws['signal_code']} / {ws['threshold_code']} / {ws['strategy_code']} / L{ws['lead_value']}** (trading days; +1 execution day)
- IS Sharpe {ws['is_sharpe']:.4f} (SPY IS {ws['bh_is_sharpe']:.4f}); OOS Sharpe {ws['oos_sharpe']:.4f} (HAC t {ws['oos_hac_t']:.2f}) vs SPY B&H {ws['bh_sharpe']:.4f}
- OOS ann. return {ws['oos_ann_return']*100:.1f}%, max DD {ws['oos_max_drawdown']*100:.1f}%; OOS trades {ws['oos_n_trades']} ({ws['oos_annual_turnover']}/yr); full-sample trades {ws['full_sample_n_trades']} ({ws['full_sample_annual_turnover']}/yr)
- Grid: leads {LEADS}; {ws['total_combos']} combos, {ws['valid_combos']} IS-valid ({ws['selection']['grid_scanned']['n_distinct_position_series']} distinct position series)
- Legacy OOS-argmax (comparison only): {ws['selection']['legacy_oos_selected_row']}
- Previously published S6_hmm_stress/T4_hmm_0.5/P2/L0 1.4083 (HAC t 3.80) relied on smoothed full-sample HMM probabilities: see hmm_lookahead_audit_{DATE_TAG}.json

Files: tournament_results_{DATE_TAG}.csv, legacy_oos_selection_{DATE_TAG}.csv, signals_{DATE_TAG}.parquet,
strategy_returns_{DATE_TAG}.csv, lead_*_{DATE_TAG}.csv, core_models_{DATE_TAG}/, exploratory_{DATE_TAG}/,
tournament_validation_{DATE_TAG}/, regime_quartile_forward_tests_{DATE_TAG}.csv, hmm_lookahead_audit_{DATE_TAG}.json.
Generated: {now_iso}
"""
    Path(RESULTS_DIR, f"handoff_evan_{DATE_TAG}.md").write_text(handoff)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    t0_total = time.time()
    print(f"\n{'='*60}\n  {INDICATOR_NAME} -> {TARGET_NAME}  |  {PAIR_ID}  |  {DATE_TAG}\n{'='*60}")
    t0 = time.time()
    df = stage_data()
    STAGE_TIMES["1_data_load"] = time.time() - t0
    df = stage_features(df)
    hmm_probs, ms_probs, _ = stage_core_models(df)
    stage_signals(df, hmm_probs, ms_probs)
    stage_exploratory(df)
    tourn = stage_tournament(df)
    stage_lookahead_audit()
    vinfo = stage_validation(tourn)
    stage_winner_artifacts(tourn, vinfo)
    stage_lead_artifacts(tourn)
    stage_metadata()
    elapsed = time.time() - t0_total
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump({"pair_id": PAIR_ID, "date_tag": DATE_TAG, "total_seconds": round(elapsed, 1),
                   "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
                   "generated_at": iso_utc_now()}, f, indent=2)
    print(f"\n  ALL STAGES COMPLETE in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
