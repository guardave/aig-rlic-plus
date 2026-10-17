#!/usr/bin/env python3
"""
Full Econometrics Pipeline: New Home Sales (NSA, HSN1FNSA) -> SPY
=================================================================
Pair ID: nhs_spy
Mode: 2 (single maker, multiple checkers)

Economic hypothesis (stated up front, per SOP):
  H0: NHS growth does NOT predict / Granger-cause forward SPY returns.
  H1 (procyclical / leading): rising New Home Sales -> stronger housing demand,
      an early-cycle signal that leads construction/employment/consumption ->
      higher forward SPY. Collapsing sales (2006-07) preceded the GFC bear.
  H1b (peak-cycle mean-reversion): at cycle peaks a far-above-trend reading can
      flip countercyclical (INDPRO precedent). Direction is empirical.

  expected_direction (provisional): procyclical. Both orientations tested in the
  tournament; Granger run in BOTH directions (housing and equities are jointly
  driven by rates/the cycle; reverse causality is plausible).

NSA handling (the defining feature of this pair):
  HSN1FNSA is NOT seasonally adjusted. Signals use YoY (12-month difference
  cancels the fixed seasonal) as the PRIMARY transform; STL-deseasonalised level
  MoM as an alternative; z-score on the YoY series. The raw NSA level (nhs_nsa)
  and STL level (nhs_sa) are NON-signal (provenance only).

Category (Rule C1): housing/activity -> full correlation battery (incl. distance
correlation), pre-whitened CCF, Toda-Yamamoto Granger (both directions), transfer
entropy, local projections (fwd + reverse), quantile regression, HMM 2-state
regime detection, regime quartile returns.

Data: Dana's parquet data/nhs_spy_monthly_latest.parquet (monthly; 1990-01 ->
2026-05; SPY-bound from 1993). Source = FRED HSN1FNSA live API. Stationarity
tests produced by Dana (results/nhs_spy/stationarity_tests_20260703.csv) —
reviewed and CONFIRMED here, NOT re-run. nhs_nsa and nhs_sa LEVELS are
NON-stationary and are NOT used as signals; all signals are stationary
growth/transform series.

Lag convention (binding): Census publishes month M near the end of M+1, so the month-M
value can only drive returns from M+2 on: registry floor L2 (#255 / strict floor). The
legacy grid [0,1,2,3,6,9,12] is truncated at the bottom to [2,3,6,9,12]. Lead semantics:
position at month t is a function of the signal observed at month t-L;
strategy_return_t = position_t * spy_ret_t.

2026-10-16 (fix261016_hmm_port_eci_nhs): regime signals are IS-fit and forward-filtered
(scripts/_regime_causal.py); the winner is selected by in-sample Sharpe on the common IS
window (PORT_GUIDE); the 20260703 smoothed-HMM L0 winner is replayed in
hmm_lookahead_audit_20261016.json.

Author: Econ Evan (Econometrics Agent) — Lead wearing role hat (Mode 2)
Date: 2026-07-03
"""

import os
import sys
import json
import time
import subprocess
import warnings
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

np.random.seed(42)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PAIR_ID = "nhs_spy"
INDICATOR_NAME = "New Home Sales (NSA)"
TARGET_NAME = "SPY"
TARGET_SYMBOL = "SPY"
DATE_TAG = "20261016"
PREV_TAG = "20260703"   # previously published run (smoothed full-sample HMM winner); immutable
STAT_TAG = "20260703"   # Dana's stationarity tests (data stage, not re-run)
COST_BPS = 5  # equity ETF per ECON-T2 / target-class table

BASE_DIR = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
).stdout.strip()
DATA_PATH = os.path.join(BASE_DIR, "data", "nhs_spy_monthly_latest.parquet")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
EXPLORE_DIR = os.path.join(RESULTS_DIR, f"exploratory_{DATE_TAG}")
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")
SCHEMA_DIR = os.path.join(BASE_DIR, "docs", "schemas")
# Same interpreter that is running this script, so subprocesses inherit the environment
# the caller chose. Was pinned to .venv/bin/python — that venv is no longer tracked, and it
# was never portable anyway (built for 3.12, its shebangs hardcode an absolute host path).
PYEXE = sys.executable

for d in [RESULTS_DIR, EXPLORE_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# tournament signal_code (snake_case, ECON-DS3 style) -> parquet column.
# NHS and STL LEVELS excluded (non-stationary, brief). Only stationary transforms.
SIGNAL_COLS = {
    "yoy": "nhs_pct_yoy",
    "yoy_accel": "nhs_yoy_accel_pct",
    "yoy_3m": "nhs_3m_pct_yoy",
    "sa_mom": "nhs_sa_pct_mom",
    "sa_3m": "nhs_sa_3m_pct",
    "yoy_zscore_120m": "nhs_yoy_zscore_120m",
    "contraction": "nhs_yoy_contraction_flag",
    # derived in stage_signals:
    "hmm_stress": "hmm_2state_prob_stress",
    "markov_regime": "markov_regime_2state",
}

FWD_COLS = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]
ZERO_CROSS = {"yoy", "yoy_accel", "yoy_3m", "sa_mom", "sa_3m"}
# #255 / strict-floor registry floor L2 (Census publishes month M near the end of M+1): the
# legacy grid [0,1,2,3,6,9,12] is truncated at the bottom, never extended at the top.
LEADS = [2, 3, 6, 9, 12]
LOOKBACKS = {"LB36": 36, "LB60": 60, "LB120": 120}
STRATEGIES = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]
MIN_IS_N = 60                  # monthly IS minimum (PORT_GUIDE)
MAX_TURNOVER = 24              # position changes per year
REGIME_SEEDS = (42, 0, 1, 2, 3)


def log_stage(name):
    def deco(fn):
        def wrap(*a, **k):
            t0 = time.time()
            print(f"\n{'='*70}\n  STAGE: {name}\n{'='*70}")
            out = fn(*a, **k)
            STAGE_TIMES[name] = time.time() - t0
            print(f"  [{name}] done in {STAGE_TIMES[name]:.1f}s")
            return out
        return wrap
    return deco


def write_manifest(path, columns, assertions, extra=None):
    m = {
        "file": os.path.basename(path),
        "pair_id": PAIR_ID,
        "produced_by": "scripts/pair_pipeline_nhs_spy.py",
        "generated_at": NOW_ISO,
        "columns": columns,
        "assertions": assertions,
    }
    if extra:
        m.update(extra)
    mp = os.path.splitext(path)[0] + "_manifest.json"
    with open(mp, "w") as f:
        json.dump(m, f, indent=2)


def ann_metrics(rets):
    """Annualized metrics for a monthly return series."""
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return dict(sharpe=0.0, ann_return=0.0, ann_vol=0.0, max_dd=0.0,
                    sortino=0.0, calmar=0.0, win_rate=0.0, n=len(rets))
    sharpe = rets.mean() / rets.std() * np.sqrt(12)
    ann_ret = rets.mean() * 12
    ann_vol = rets.std() * np.sqrt(12)
    cum = (1 + rets).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    neg = rets[rets < 0]
    sortino = ann_ret / (neg.std() * np.sqrt(12)) if len(neg) > 1 and neg.std() > 0 else 0.0
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    return dict(sharpe=sharpe, ann_return=ann_ret, ann_vol=ann_vol, max_dd=dd,
                sortino=sortino, calmar=calmar, win_rate=(rets > 0).mean(), n=len(rets))


# ===================================================================
# STAGE 1: LOAD + VERIFY (Defense 2 consumer checks)
# ===================================================================
@log_stage("1_load_verify")
def stage_load():
    df = pd.read_parquet(DATA_PATH)
    # Known-episode checks (Dana's handoff / interpretation_metadata)
    assert df.loc["2009", "nhs_pct_yoy"].min() < -20.0, "GFC housing collapse (<-20% YoY) expected"
    assert df.loc["2023", "nhs_pct_yoy"].min() < 0.0, "2022-23 rate-shock contraction expected"
    assert int(df["nhs_yoy_contraction_flag"].sum()) > 0, "contraction flag should fire"
    spy_ret = df["spy_ret"].dropna()
    assert spy_ret.abs().max() < 0.40, "monthly SPY return magnitude implausible"
    print(f"  Loaded {df.shape}, {df.index.min().date()} -> {df.index.max().date()}")
    print("  Defense-2 episode checks: GFC housing collapse, 2022-23 contraction, return magnitudes — PASS")
    return df


# ===================================================================
# STAGE 2: DERIVED REGIME SIGNALS (HMM + Markov-switching)
# ===================================================================
@log_stage("2_signals")
def stage_signals(df, oos_start):
    """Regime signals, causal (scripts/_regime_causal.py): IS-only fit, IS-only standardisation,
    forward-filtered P(state_t | x_1..x_t); the target return is not in any likelihood.
    HMM: 2 states on NHS YoY growth, stress = higher in-sample-variance state (the old key).
    Markov-switching: 2 regimes with switching variance on NHS YoY growth itself (the old model
    regressed spy_ret on yoy); stress = higher-variance regime."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _regime_causal import fit_hmm_causal, fit_ms_causal

    yoy = df["nhs_pct_yoy"]
    regime_log = {"oos_start": str(pd.Timestamp(oos_start).date()), "models": {}}

    r = fit_hmm_causal(yoy.to_frame(), oos_start, n_states=2, label_feature=yoy.name,
                       label="max_variance", seeds=REGIME_SEEDS)
    prob_stress = r.prob.reindex(df.index)
    df["hmm_2state_prob_stress"] = prob_stress
    regime_log["models"]["hmm_2state_prob_stress"] = {"status": "traded", **r.summary()}
    CTX["hmm_fit"] = r.summary()

    p = prob_stress.dropna()
    hmm_states = pd.DataFrame({"hmm_state": (p > 0.5).astype(int), "prob_stress": p, "prob_calm": 1 - p})
    hmm_states.to_parquet(os.path.join(MODELS_DIR, "hmm_states.parquet"))
    summ = []
    spy = df["spy_ret"]
    for lbl, mask in [("stress", hmm_states["hmm_state"] == 1), ("calm", hmm_states["hmm_state"] == 0)]:
        idx = hmm_states.index[mask]
        rets = spy.reindex(idx).dropna()
        sub = yoy.reindex(idx)
        summ.append({"state_label": lbl,
                     "mean_return": round(rets.mean(), 6) if len(rets) else np.nan,
                     "vol": round(rets.std(), 6) if len(rets) else np.nan,
                     "duration_days": int(mask.sum()),
                     "frequency_pct": round(mask.mean() * 100, 2),
                     "mean_yoy_growth": round(sub.mean(), 3)})
    pd.DataFrame(summ).to_csv(os.path.join(MODELS_DIR, "hmm_summary.csv"), index=False)
    gfc_p = prob_stress.loc["2008-01-31":"2009-06-30"].mean()
    print(f"  Causal HMM (IS n={r.n_fit}, {r.fit_start.date()}..{r.fit_end.date()}): "
          f"filtered stress prob mean 2008-01..2009-06 = {gfc_p:.2f}")
    write_manifest(os.path.join(MODELS_DIR, "hmm_states.parquet"),
                   {"hmm_state": "1 if filtered prob_stress > 0.5 else 0 (stress = higher-variance NHS-YoY state)",
                    "prob_stress": "forward-filtered P(stress | NHS YoY up to t); params fit on IS months only",
                    "prob_calm": "1 - prob_stress"},
                   [{"description": "probabilities in [0,1]", "check": "prob_stress between 0 and 1"},
                    {"description": "GFC housing collapse era", "filter": "2008-01 to 2009-06",
                     "column": "prob_stress", "check": f"mean = {gfc_p:.2f} (computed at fit time)"},
                    {"description": "states sum to 1", "check": "prob_stress + prob_calm == 1"}],
                   extra={"fit": r.summary()})

    try:
        ms = fit_ms_causal(yoy, oos_start, k_regimes=2, switching_variance=True, label="max_variance")
        df["markov_regime_2state"] = ms.prob.reindex(df.index)
        pd.DataFrame({"regime_stress_prob": ms.prob, "regime_calm_prob": 1 - ms.prob}
                     ).to_csv(os.path.join(MODELS_DIR, "markov_regime_probs_2state.csv"))
        regime_log["models"]["markov_regime_2state"] = {"status": "traded", **ms.summary()}
        print(f"  Causal Markov-switching on NHS YoY (IS n={ms.n_fit})")
    except Exception as e:
        regime_log["models"]["markov_regime_2state"] = {"status": "excluded_from_tournament", "reason": repr(e)}
        print(f"  Markov-switching failed: {e} — signal excluded from tournament")
    with open(os.path.join(MODELS_DIR, "regime_models.json"), "w") as f:
        json.dump(regime_log, f, indent=2, default=str)

    sig_cols = [c for c in SIGNAL_COLS.values() if c in df.columns]
    sig_path = os.path.join(RESULTS_DIR, f"signals_{DATE_TAG}.parquet")
    df[sig_cols].to_parquet(sig_path)
    print(f"  Signals persisted -> {sig_path} ({len(sig_cols)} columns)")
    write_manifest(sig_path,
                   {c: f"tournament-eligible signal derived solely from HSN1FNSA ({c})" for c in sig_cols},
                   [{"description": "GFC housing collapse present", "filter": "2008-01..2009-12",
                     "column": "nhs_pct_yoy", "check": "min < -20"},
                    {"description": "2022-23 rate-shock contraction", "filter": "2022-01..2023-12",
                     "column": "nhs_pct_yoy", "check": "min < 0"},
                    {"description": "HMM prob bounded", "column": "hmm_2state_prob_stress",
                     "check": "values in [0,1]"}],
                   extra={"regime_signals": regime_log["models"],
                          "input_note": ("indicator transforms equal results/nhs_spy/signals_20260703.parquet; see "
                                         "_pws/lead-lesandro/pkg13_hmm_port/nhs_frozen_input.py")})
    return df


# ===================================================================
# STAGE 3: EXPLORATORY + CORRELATION BATTERY (Rule C1/C2)
# ===================================================================
def _distance_corr(x, y):
    x = np.asarray(x, float)[:, None]
    y = np.asarray(y, float)[:, None]
    a = np.abs(x - x.T)
    b = np.abs(y - y.T)
    A = a - a.mean(0) - a.mean(1)[:, None] + a.mean()
    B = b - b.mean(0) - b.mean(1)[:, None] + b.mean()
    dcov2 = (A * B).mean()
    dvx = (A * A).mean()
    dvy = (B * B).mean()
    if dvx <= 0 or dvy <= 0:
        return 0.0
    return float(np.sqrt(max(dcov2, 0) / np.sqrt(dvx * dvy)))


@log_stage("3_exploratory_correlations")
def stage_correlations(df):
    rows = []
    horizon_map = {"spy_fwd_1m": 1, "spy_fwd_3m": 3, "spy_fwd_6m": 6, "spy_fwd_12m": 12}
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwd, h in horizon_map.items():
            v = df[[col, fwd]].dropna()
            if len(v) < 60:
                continue
            x, y = v[col], v[fwd]
            for metric, fn in [("pearson", stats.pearsonr), ("spearman", stats.spearmanr),
                               ("kendall", stats.kendalltau)]:
                r, p = fn(x, y)
                rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": h * 21,
                             "metric": metric, "value": round(r, 4),
                             "p_value": round(p, 4), "n_obs": len(v)})
            rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": h * 21,
                         "metric": "distance", "value": round(_distance_corr(x, y), 4),
                         "p_value": np.nan, "n_obs": len(v)})
    cdf = pd.DataFrame(rows)
    for outdir in (MODELS_DIR, EXPLORE_DIR):
        cdf.to_csv(os.path.join(outdir, "correlations.csv"), index=False)
    path = os.path.join(MODELS_DIR, "correlations.csv")
    write_manifest(path,
                   {"pair_name": "signal_code__forward-return-column", "horizon_days": "forward horizon in trading days (monthly*21)",
                    "metric": "pearson/spearman/kendall/distance", "value": "correlation coefficient",
                    "p_value": "two-sided p (NaN for distance corr)", "n_obs": "obs"},
                   [{"description": "values bounded", "check": "abs(value) <= 1"},
                    {"description": "monthly pair: horizons are 21/63/126/252 day equivalents", "check": "horizon_days in {21,63,126,252}"},
                    {"description": "n_obs >= 60 enforced at producer", "check": "min(n_obs) >= 60"}])
    sig = cdf[(cdf.metric == "pearson") & (cdf.p_value < 0.05)]
    print(f"  Correlation battery: {len(cdf)} rows; {len(sig)} significant Pearson cells")
    if len(sig):
        b = sig.loc[sig.value.abs().idxmax()]
        print(f"  Strongest Pearson: {b.pair_name} r={b.value} p={b.p_value}")
    return cdf


# ===================================================================
# STAGE 4: CORE MODELS — CCF, Granger (TY), TE, LP, QR, regressions
# ===================================================================
@log_stage("4_core_models")
def stage_core_models(df):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.ar_model import AutoReg
    from statsmodels.tsa.api import VAR

    main_sig = "nhs_pct_yoy"

    # --- 4.1 Pre-whitened CCF (lags -20..+20) ---
    pair = df[[main_sig, "spy_ret"]].dropna()
    x = pair[main_sig]
    y = pair["spy_ret"]
    best_aic, best_p = np.inf, 1
    for p in range(1, 13):
        try:
            aic = AutoReg(x, lags=p, old_names=False).fit().aic
            if aic < best_aic:
                best_aic, best_p = aic, p
        except Exception:
            pass
    ar_fit = AutoReg(x, lags=best_p, old_names=False).fit()
    x_w = ar_fit.resid
    coefs = ar_fit.params
    y_w = y.copy() - coefs.iloc[0]
    for i in range(1, best_p + 1):
        y_w = y_w - coefs.iloc[i] * y.shift(i)
    common = x_w.index.intersection(y_w.dropna().index)
    xw, yw = x_w.loc[common], y_w.loc[common]
    n = len(common)
    se = 1.96 / np.sqrt(n)
    rows = []
    for lag in range(-20, 21):
        if lag >= 0:
            a, b = xw.shift(lag), yw
        else:
            a, b = xw, yw.shift(-lag)
        v = pd.concat([a, b], axis=1).dropna()
        c = v.corr().iloc[0, 1] if len(v) > 30 else np.nan
        rows.append({"lag": lag, "ccf": round(c, 4), "lower_ci": round(-se, 4),
                     "upper_ci": round(se, 4), "significant": bool(abs(c) > se) if pd.notna(c) else False,
                     "arima_order": f"AR({best_p})", "n_obs": len(v)})
    ccf_df = pd.DataFrame(rows)
    ccf_df.to_csv(os.path.join(MODELS_DIR, "ccf_prewhitened.csv"), index=False)
    lead_sig = ccf_df[(ccf_df.lag > 0) & ccf_df.significant]
    lag_sig = ccf_df[(ccf_df.lag < 0) & ccf_df.significant]
    print(f"  [4.1] CCF (AR({best_p}) prewhitening, n={n}): significant lead lags {list(lead_sig.lag)}, "
          f"significant LAG-side lags {list(lag_sig.lag)}")

    # --- 4.2 Toda-Yamamoto Granger (both directions) + by-lag artifact ---
    ty_rows, bylag_rows = [], []
    gdata = pair.rename(columns={main_sig: "ind", "spy_ret": "tgt"})
    d_max = 1
    var_sel = VAR(gdata).select_order(maxlags=12)
    p_opt = max(int(var_sel.aic), 1)

    def ty_wald(caused, causing, lag):
        cols = {}
        for i in range(1, lag + d_max + 1):
            cols[f"{causing}_l{i}"] = gdata[causing].shift(i)
            cols[f"{caused}_l{i}"] = gdata[caused].shift(i)
        Xd = pd.DataFrame(cols).dropna()
        yv = gdata[caused].reindex(Xd.index)
        X = sm.add_constant(Xd)
        fit = sm.OLS(yv, X).fit()
        hyp = ", ".join(f"{causing}_l{i} = 0" for i in range(1, lag + 1))
        ft = fit.f_test(hyp)
        return float(ft.fvalue), float(ft.pvalue), int(ft.df_num), int(ft.df_denom)

    for lag in range(1, 13):
        try:
            for direction, caused, causing in [("indicator_to_target", "tgt", "ind"),
                                               ("target_to_indicator", "ind", "tgt")]:
                fstat, pv, dfn, dfd = ty_wald(caused, causing, lag)
                ty_rows.append({"direction": direction, "lag": lag,
                                "f_statistic": round(fstat, 4), "p_value": round(pv, 4),
                                "significant": pv < 0.05})
                if direction == "indicator_to_target":
                    bylag_rows.append({"lag": lag, "f_statistic": round(fstat, 4),
                                       "p_value": round(pv, 4), "df_num": dfn, "df_den": dfd})
        except Exception as e:
            print(f"    TY lag {lag} failed: {e}")
    ty_df = pd.DataFrame(ty_rows)
    ty_df.to_csv(os.path.join(MODELS_DIR, "granger_causality.csv"), index=False)
    pd.DataFrame(bylag_rows).to_csv(os.path.join(RESULTS_DIR, "granger_by_lag.csv"), index=False)
    fwd_sig = ty_df[(ty_df.direction == "indicator_to_target") & ty_df.significant]
    rev_sig = ty_df[(ty_df.direction == "target_to_indicator") & ty_df.significant]
    print(f"  [4.2] Toda-Yamamoto (d_max={d_max}, VAR p* by AIC={p_opt}):")
    print(f"        NHS->SPY significant at lags: {list(fwd_sig.lag)}")
    print(f"        SPY->NHS significant at lags: {list(rev_sig.lag)}")

    # --- 4.3 Transfer entropy (binned, permutation p) ---
    def transfer_entropy(src, dst, bins=3, lag=1):
        v = pd.concat([src, dst], axis=1).dropna()
        s = pd.qcut(v.iloc[:, 0], bins, labels=False, duplicates="drop")
        t = pd.qcut(v.iloc[:, 1], bins, labels=False, duplicates="drop")
        tt, tl, sl = t[lag:].values, t[:-lag].values, s[:-lag].values
        def H(*cols):
            arr = np.stack(cols, 1)
            _, counts = np.unique(arr, axis=0, return_counts=True)
            p = counts / counts.sum()
            return -np.sum(p * np.log(p))
        return H(tt, tl) - H(tt, tl, sl) + H(tl, sl) - H(tl)

    te_rows = []
    n_perm = 500
    rng = np.random.default_rng(42)
    for direction, src, dst in [("indicator_to_target", x, y), ("target_to_indicator", y, x)]:
        te = transfer_entropy(src, dst)
        null = []
        v = pd.concat([src, dst], axis=1).dropna()
        for _ in range(n_perm):
            shuf = pd.Series(rng.permutation(v.iloc[:, 0].values), index=v.index)
            null.append(transfer_entropy(shuf, v.iloc[:, 1]))
        pv = float((np.array(null) >= te).mean())
        te_rows.append({"direction": direction, "te_value": round(float(te), 5),
                        "permutation_p_value": round(pv, 4), "n_permutations": n_perm,
                        "bandwidth": np.nan, "bin_method": "tercile_qcut"})
    pd.DataFrame(te_rows).to_csv(os.path.join(MODELS_DIR, "transfer_entropy.csv"), index=False)
    print(f"  [4.3] Transfer entropy: ind->tgt TE={te_rows[0]['te_value']} (p={te_rows[0]['permutation_p_value']}), "
          f"tgt->ind TE={te_rows[1]['te_value']} (p={te_rows[1]['permutation_p_value']})")

    # --- 4.4 Local projections (forward + REVERSE per mandatory check) ---
    lp_rows = []
    for direction in ["fwd", "rev"]:
        for h in [1, 3, 6, 12]:
            if direction == "fwd":
                ycol = f"spy_fwd_{h}m"
                v = df[[main_sig, ycol]].dropna()
                xv, yv = v[main_sig], v[ycol]
            else:
                v = pd.concat([df["spy_ret"], df[main_sig].shift(-h)], axis=1).dropna()
                v.columns = ["x", "y"]
                xv, yv = v["x"], v["y"]
            if len(v) < 60:
                continue
            X = sm.add_constant(xv.values)
            nw = int(0.75 * len(v) ** (1 / 3)) + h
            fit = sm.OLS(yv.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = fit.conf_int()
            lp_rows.append({"horizon": h, "coef": round(fit.params[1], 6),
                            "se": round(fit.bse[1], 6),
                            "ci_lower": round(ci[1][0], 6), "ci_upper": round(ci[1][1], 6),
                            "p_value": round(fit.pvalues[1], 4), "direction": direction})
    lp_df = pd.DataFrame(lp_rows)
    lp_df.to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    rev = lp_df[lp_df.direction == "rev"]
    rev_flag = bool((rev.p_value < 0.05).any())
    print(f"  [4.4] Local projections: reverse-causality significant horizons: "
          f"{list(rev.loc[rev.p_value < 0.05, 'horizon'])} -> reverse-causality flag: {rev_flag}")

    # --- 4.5 Quantile regression (tau battery) ---
    qr_rows = []
    v = df[[main_sig, "spy_fwd_3m"]].dropna().rename(columns={main_sig: "sig", "spy_fwd_3m": "fwd"})
    for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
        try:
            qf = smf.quantreg("fwd ~ sig", v).fit(q=tau)
            ci = qf.conf_int()
            qr_rows.append({"tau": tau, "coef": round(qf.params["sig"], 6),
                            "se": round(qf.bse["sig"], 6), "p_value": round(qf.pvalues["sig"], 4),
                            "ci_lower": round(ci.loc["sig", 0], 6), "ci_upper": round(ci.loc["sig", 1], 6)})
        except Exception as e:
            print(f"    QR tau={tau} failed: {e}")
    pd.DataFrame(qr_rows).to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    print(f"  [4.5] Quantile regression: {len(qr_rows)} taus")

    # --- 4.6 Predictive regressions (all signals x horizons, HC3) ---
    reg_rows = []
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwd in FWD_COLS:
            v = df[[col, fwd]].dropna()
            if len(v) < 60:
                continue
            X = sm.add_constant(v[col].values)
            fit = sm.OLS(v[fwd].values, X).fit(cov_type="HC3")
            reg_rows.append({"signal": code, "horizon": fwd, "coef": round(fit.params[1], 6),
                             "se": round(fit.bse[1], 6), "t_stat": round(fit.tvalues[1], 3),
                             "p_value": round(fit.pvalues[1], 4),
                             "r_squared": round(fit.rsquared, 4), "n": int(fit.nobs)})
    reg_df = pd.DataFrame(reg_rows)
    reg_df.to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    print(f"  [4.6] Predictive regressions: {len(reg_df)} cells")

    # --- 4.7 Diagnostics on baseline spec ---
    diag = []
    v = df[[main_sig, "spy_fwd_3m"]].dropna()
    X = sm.add_constant(v[main_sig].values)
    base = sm.OLS(v["spy_fwd_3m"].values, X).fit()
    resid = base.resid
    jb, jbp = stats.jarque_bera(resid)
    diag.append({"test": "Jarque-Bera", "statistic": round(jb, 3), "p_value": round(jbp, 4),
                 "interpretation": "Normal residuals" if jbp > 0.05 else "Non-normal — robust/HAC inference used"})
    from statsmodels.stats.diagnostic import het_breuschpagan, acorr_breusch_godfrey
    bp, bpp, _, _ = het_breuschpagan(resid, X)
    diag.append({"test": "Breusch-Pagan", "statistic": round(bp, 3), "p_value": round(bpp, 4),
                 "interpretation": "Homoskedastic" if bpp > 0.05 else "Heteroskedastic — HC3/HAC SEs used"})
    bg, bgp, _, _ = acorr_breusch_godfrey(base, nlags=12)
    diag.append({"test": "Breusch-Godfrey (12)", "statistic": round(bg, 3), "p_value": round(bgp, 4),
                 "interpretation": "No serial corr" if bgp > 0.05 else "Serial correlation (overlapping fwd returns) — HAC SEs used"})
    from statsmodels.stats.diagnostic import linear_reset
    try:
        rs = linear_reset(base, power=3, use_f=True)
        diag.append({"test": "RESET", "statistic": round(float(rs.fvalue), 3),
                     "p_value": round(float(rs.pvalue), 4),
                     "interpretation": "Linear form adequate" if rs.pvalue > 0.05 else "Possible nonlinearity — see quantile regression"})
    except Exception:
        pass
    pd.DataFrame(diag).to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)
    print(f"  [4.7] Diagnostics: {len(diag)} tests")

    return ccf_df, ty_df, lp_df, reg_df, rev_flag


# ===================================================================
# STAGE 5: REGIME QUARTILE RETURNS (Rule E2)
# ===================================================================
@log_stage("5_regime_quartiles")
def stage_quartiles(df):
    v = df[["nhs_pct_yoy", "spy_ret"]].dropna()
    q = pd.qcut(v["nhs_pct_yoy"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    rows = []
    for lbl in ["Q1", "Q2", "Q3", "Q4"]:
        r = v.loc[q == lbl, "spy_ret"]
        m = ann_metrics(r)
        rows.append({"quartile": lbl, "n_months": len(r), "ann_return": round(m["ann_return"], 4),
                     "ann_vol": round(m["ann_vol"], 4), "sharpe": round(m["sharpe"], 3),
                     "max_drawdown": round(m["max_dd"], 4)})
    qdf = pd.DataFrame(rows)
    path = os.path.join(RESULTS_DIR, "regime_quartile_returns.csv")
    qdf.to_csv(path, index=False)
    print(qdf.to_string(index=False))
    write_manifest(path,
                   {"quartile": "NHS YoY growth quartile (Q1 lowest growth)", "n_months": "obs",
                    "ann_return": "annualized SPY return in quartile (ratio)",
                    "ann_vol": "annualized vol (ratio)", "sharpe": "ann_return/ann_vol",
                    "max_drawdown": "max DD within quartile months (negative ratio)"},
                   [{"description": "4 quartiles", "check": "len == 4"},
                    {"description": "returns plausible", "check": "abs(ann_return) < 0.5"},
                    {"description": "concurrent (NOT lagged) relationship — descriptive only", "check": "informational"}])
    return qdf


# ===================================================================
# STAGE 6: TOURNAMENT (5-D) + ECON-T3/T4/OOS1/OOS2
# ===================================================================
CTX = {}


def compute_split(df):
    """ECON-OOS2 policy v1_max36_25pct_cap120 on the SPY-bound sample (unchanged rule).
    Computed before the regime models so they can be fit on IS rows only."""
    work = df.dropna(subset=["spy_ret"])
    n = len(work)
    oos_n = int(min(max(36, round(n * 0.25)), 120))
    return {"n": n, "oos_n": oos_n, "oos_start": work.index[-oos_n],
            "is_end": work.index[-(oos_n + 1)], "oos_end": work.index[-1]}


def paired_block_bootstrap_sharpe_diff(strat, bh, block, ppy, draws=5000, seed=42):
    """Paired circular block bootstrap of OOS Sharpe(strategy) - Sharpe(B&H): the same resampled
    blocks are applied to both series, so their dependence is kept. Returns mean, 95% CI and
    P(diff <= 0)."""
    s, b = np.asarray(strat, float), np.asarray(bh, float)
    n = len(s)
    rng = np.random.default_rng(seed)

    def _sh(x):
        return x.mean() / x.std() * np.sqrt(ppy) if x.std() > 0 else np.nan

    d = []
    for _ in range(draws):
        starts = rng.integers(0, n, size=int(np.ceil(n / block)))
        idx = np.concatenate([np.arange(k, k + block) % n for k in starts])[:n]
        d.append(_sh(s[idx]) - _sh(b[idx]))
    d = np.array(d)
    d = d[~np.isnan(d)]
    return {"observed": round(float(_sh(s) - _sh(b)), 4), "mean": round(float(d.mean()), 4),
            "ci_95": [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)],
            "p_diff_le_0": round(float((d <= 0).mean()), 4), "block_length": block, "draws": int(len(d)),
            "seed": seed, "method": "paired circular block bootstrap of OOS Sharpe(strategy) - Sharpe(B&H)"}


def hac_t_mean(r, horizon=1):
    """HAC (Newey-West) t-stat of the mean; maxlags = max(floor(4*(n/100)^(2/9)), horizon-1)."""
    import statsmodels.api as sm
    y = pd.Series(r).dropna().values
    nw = max(int(np.floor(4 * (len(y) / 100) ** (2 / 9))), horizon - 1)
    m = sm.OLS(y, np.ones((len(y), 1))).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
    return float(m.tvalues[0]), float(m.pvalues[0]), nw


def thresholds_for(code, sig, is_mask):
    """Threshold set for one lead-shifted signal (unchanged grid): IS percentiles {25,50,75}
    (IS rows only), zero-line for growth signals, rolling p25/p75 and z +/-1.0/1.5 at
    LB36/LB60/LB120."""
    out = {}
    is_sig = sig[is_mask].dropna()
    if len(is_sig) > 60:
        for pct in [25, 50, 75]:
            out[(f"T1_fixed_p{pct}", "LB_NA")] = is_sig.quantile(pct / 100)
    if code in ZERO_CROSS:
        out[("T4_zero", "LB_NA")] = 0.0
    for lb_name, lb in LOOKBACKS.items():
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24))
        for pct in [25, 75]:
            out[(f"T2_roll_p{pct}", lb_name)] = roll.quantile(pct / 100)
        rm, rs = roll.mean(), roll.std()
        for k in [1.0, 1.5]:
            out[(f"T3_zscore_{k}", lb_name)] = rm + k * rs
            out[(f"T3_zscore_neg_{k}", lb_name)] = rm - k * rs
    return out


def build_position(sig, thr_name, thr, strategy, lb_name):
    """Position on row t (accrues spy_ret of month t). NaN while the lagged signal or its
    rolling threshold is undefined; earlier code traded those rows as cash/short because NaN
    comparisons evaluate to False. P2 sizes by the signal's place in its trailing min-max range
    (the threshold label is not used)."""
    strat, orientation = strategy.rsplit("_", 1)
    if strat == "P2_signal_strength":
        lb = LOOKBACKS[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24))
        rng = (roll.max() - roll.min()).replace(0, np.nan)
        raw = ((sig - roll.min()) / rng).clip(0, 1)
        return 1 - raw if orientation == "counter" else raw
    above = sig < thr if "neg_" in thr_name else sig > thr
    defined = sig.notna() & (thr.notna() if isinstance(thr, pd.Series) else True)
    pos_bool = ~above if orientation == "counter" else above
    pos = pos_bool.astype(float) if strat == "P1_long_cash" else pos_bool.astype(float) * 2 - 1
    return pos.where(defined)


def replay(work, code, thr_name, lb_name, strategy, lead, is_mask):
    sig = work[SIGNAL_COLS[code]].shift(lead)
    thr = thresholds_for(code, sig, is_mask)[(thr_name, lb_name)]
    pos = build_position(sig, thr_name, thr, strategy, lb_name)
    return pos, pos * work["spy_ret"], sig, thr


def _trades(pos, mask):
    p = pos[mask].dropna()
    n = int((p.diff().abs() > 1e-9).sum())
    years = len(p) / 12
    return n, (n / years if years > 0 else np.nan)


def _exposure(pos, strategy):
    p = pos.dropna()
    if not len(p):
        return np.nan
    return float((p > 0).mean()) if strategy.startswith("P3") else float(p.mean())


def run_grid(df, split, leads=LEADS):
    """Full grid with IS selection (PORT_GUIDE blocks 1-3, eligibility before alignment).
    Pure: returns (tourn, selection-context); writes nothing."""
    work = df.dropna(subset=["spy_ret"]).copy()
    oos_start, oos_end, is_end = split["oos_start"], split["oos_end"], split["is_end"]
    is_full = work.index <= is_end
    oos_mask = (work.index >= oos_start) & (work.index <= oos_end)
    spy_ret = work["spy_ret"]
    strategies = [f"{s}_{o}" for s in STRATEGIES for o in ["pro", "counter"]]
    avail = {k: v for k, v in SIGNAL_COLS.items() if v in work.columns and work[v].notna().sum() >= 120}

    cands = []
    for code, col in avail.items():
        for lead in leads:
            sig = work[col].shift(lead)
            p2_cache = {}
            for (thr_name, lb_name), thr in thresholds_for(code, sig, is_full).items():
                for strategy in strategies:
                    if strategy.startswith("P2"):
                        if lb_name == "LB_NA":
                            continue
                        key = (lb_name, strategy)
                        if key not in p2_cache:
                            p2_cache[key] = build_position(sig, thr_name, thr, strategy, lb_name)
                        pos = p2_cache[key]
                    else:
                        pos = build_position(sig, thr_name, thr, strategy, lb_name)
                    cands.append((code, thr_name, lb_name, strategy, lead, pos, pos * spy_ret))

    def _first(rets):
        r = rets.dropna()
        return r.index.min() if len(r) else pd.NaT

    def _own_is_n(rets):
        return int(((rets.index < oos_start) & rets.notna()).sum())

    eligible = [_own_is_n(c[6]) >= MIN_IS_N for c in cands]
    if not any(eligible):
        raise RuntimeError("No IS-eligible candidate")
    common_is_start = max(_first(c[6]) for c, ok in zip(cands, eligible) if ok)
    is_mask = (work.index >= common_is_start) & (work.index < oos_start)
    driver = sorted({f"{c[0]}/{c[1]}/{c[2]}/L{c[4]}" for c, ok in zip(cands, eligible)
                     if ok and _first(c[6]) == common_is_start})[:3]
    bh_is = ann_metrics(spy_ret[is_mask])
    bh = ann_metrics(spy_ret[oos_mask])

    rows = []
    for (code, thr_name, lb_name, strategy, lead, pos, rets), elig in zip(cands, eligible):
        is_r = rets[is_mask].dropna()
        own_start = _first(rets)
        own_mask = (work.index >= own_start) & (work.index < oos_start) if pd.notna(own_start) else is_mask & False
        own_r = rets[own_mask].dropna()
        oos_r = rets[oos_mask].fillna(0.0)                      # ECON-T4 deployable OOS
        mi, mo, m = ann_metrics(is_r), ann_metrics(own_r), ann_metrics(oos_r)
        is_tr, is_to = _trades(pos, is_mask)
        oos_tr, oos_to = _trades(pos, oos_mask)
        is_expo = _exposure(pos[is_mask], strategy)
        own_expo = _exposure(pos[own_mask], strategy)
        is_valid = bool(elig and len(is_r) >= MIN_IS_N and is_expo == is_expo and 0.05 <= is_expo <= 0.95
                        and is_r.std() > 0 and is_to < MAX_TURNOVER)
        own_valid = bool(len(own_r) >= MIN_IS_N and own_expo == own_expo and 0.05 <= own_expo <= 0.95
                         and own_r.std() > 0)
        # pre-#251 rule, comparison only: OOS Sharpe > 0.3, OOS turnover < 24, >= 24 OOS months
        legacy_valid = bool(m["sharpe"] > 0.3 and oos_to < MAX_TURNOVER and len(oos_r) >= 24)
        rows.append({
            "signal": code, "threshold": thr_name, "strategy": strategy, "lead_months": lead, "lookback": lb_name,
            "direction": ("procyclical" if (strategy.endswith("_pro") != ("neg_" in thr_name)) else "countercyclical"),
            "is_sharpe": round(mi["sharpe"], 6), "is_ann_return": round(mi["ann_return"], 6),
            "is_max_drawdown": round(mi["max_dd"], 6), "is_exposure": round(is_expo, 4) if is_expo == is_expo else np.nan,
            "is_n_trades": is_tr, "is_annual_turnover": round(is_to, 3) if is_to == is_to else np.nan,
            "is_start": is_r.index.min().date().isoformat() if len(is_r) else None,
            "is_end": is_r.index.max().date().isoformat() if len(is_r) else None,
            "common_is_start": common_is_start.date().isoformat(),
            "own_is_start": own_r.index.min().date().isoformat() if len(own_r) else None,
            "own_is_sharpe": round(mo["sharpe"], 6), "own_is_n": mo["n"], "own_is_valid": own_valid,
            "oos_sharpe": round(m["sharpe"], 6), "oos_sortino": round(m["sortino"], 6),
            "oos_calmar": round(m["calmar"], 6), "oos_ann_return": round(m["ann_return"], 6),
            "oos_ann_vol": round(m["ann_vol"], 6), "max_drawdown": round(m["max_dd"], 6),
            "win_rate": round(m["win_rate"], 4), "n_trades": oos_tr,
            "annual_turnover": round(oos_to, 3) if oos_to == oos_to else np.nan,
            "is_n": mi["n"], "oos_n": m["n"], "is_eligible": bool(elig),
            "is_ineligible_reason": "" if elig else f"insufficient IS history: n_own={_own_is_n(rets)} < MIN_IS_N={MIN_IS_N}",
            "is_valid": is_valid, "oos_valid": legacy_valid, "valid": is_valid})
    rows.append({
        "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "P0_buy_and_hold", "lead_months": 0,
        "lookback": "LB_NA", "direction": "benchmark", "is_sharpe": round(bh_is["sharpe"], 6),
        "is_ann_return": round(bh_is["ann_return"], 6), "is_max_drawdown": round(bh_is["max_dd"], 6),
        "is_exposure": 1.0, "is_n_trades": 0, "is_annual_turnover": 0.0,
        "is_start": common_is_start.date().isoformat(), "is_end": work.index[is_mask][-1].date().isoformat(),
        "common_is_start": common_is_start.date().isoformat(), "own_is_start": None, "own_is_sharpe": np.nan,
        "own_is_n": 0, "own_is_valid": False, "oos_sharpe": round(bh["sharpe"], 6),
        "oos_sortino": round(bh["sortino"], 6), "oos_calmar": round(bh["calmar"], 6),
        "oos_ann_return": round(bh["ann_return"], 6), "oos_ann_vol": round(bh["ann_vol"], 6),
        "max_drawdown": round(bh["max_dd"], 6), "win_rate": round(bh["win_rate"], 4), "n_trades": 0,
        "annual_turnover": 0.0, "is_n": bh_is["n"], "oos_n": bh["n"], "is_eligible": False,
        "is_ineligible_reason": "benchmark", "is_valid": False, "oos_valid": False, "valid": False})
    tourn = pd.DataFrame(rows)
    assert (tourn["signal"] == "BENCHMARK").sum() == 1, "exactly one benchmark row required (ECON-T4)"

    nb = tourn["signal"] != "BENCHMARK"
    valid = tourn[tourn["valid"] & nb]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    keys = ["is_sharpe", "is_ann_return", "is_max_drawdown", "is_n_trades", "signal", "threshold",
            "strategy", "lookback", "lead_months"]
    asc = [False, False, False, True, True, True, True, True, True]
    ranked = valid.sort_values(keys, ascending=asc, kind="mergesort")
    wi = ranked.index[0]
    tied, tie_step = valid, 5
    for step, k in enumerate(["is_sharpe", "is_ann_return", "is_max_drawdown", "is_n_trades"], 1):
        tied = tied[(tied[k] - tourn.loc[wi, k]).abs() <= 1e-9]
        if len(tied) == 1:
            tie_step = step
            break
    own_pool = tourn[tourn["own_is_valid"] & nb]
    oi = own_pool.sort_values(["own_is_sharpe", "signal", "threshold"], ascending=[False, True, True],
                              kind="mergesort").index[0]
    legacy_pool = tourn[tourn["oos_valid"] & nb]
    li = (legacy_pool.sort_values(["oos_sharpe", "oos_ann_return", "signal", "threshold"],
                                  ascending=[False, False, True, True], kind="mergesort").index[0]
          if len(legacy_pool) else None)
    tourn["is_rank"] = tourn["is_sharpe"].where(nb & tourn["valid"]).rank(ascending=False, method="min")
    tourn["oos_rank"] = tourn["oos_sharpe"].where(nb & tourn["valid"]).rank(ascending=False, method="min")
    distinct = valid.drop_duplicates(["signal", "strategy", "lead_months", "lookback", "is_sharpe", "oos_sharpe"])
    sp = stats.spearmanr(valid["is_sharpe"], valid["oos_sharpe"]).correlation
    sel = dict(wi=wi, oi=oi, li=li, tie_step=tie_step, tied=tied, common_is_start=common_is_start,
               n_cands=len(cands), n_eligible=int(sum(eligible)), n_inel=int(len(cands) - sum(eligible)),
               bh_is=bh_is, bh=bh, n_distinct=len(distinct), spearman=float(sp), driver=driver,
               ranked=ranked)
    return tourn, sel


@log_stage("6_tournament")
def stage_tournament(df, sp):
    oos_n, n_months = sp["oos_n"], sp["n"]
    oos_start, is_end, oos_end = sp["oos_start"], sp["is_end"], sp["oos_end"]
    work = df.dropna(subset=["spy_ret"])
    print(f"  Sample (SPY-bound): {n_months} months {work.index[0].date()} -> {oos_end.date()}")
    print(f"  OOS (v1_max36_25pct_cap120): {oos_n} months, {oos_start.date()} -> {oos_end.date()}")
    split = {
        "owner": "evan", "split_policy_id": "v1_max36_25pct_cap120",
        "in_sample_end": is_end.strftime("%Y-%m-%d"), "oos_start": oos_start.strftime("%Y-%m-%d"),
        "oos_end": oos_end.strftime("%Y-%m-%d"), "sample_size_months": n_months,
        "justification": (
            f"Policy v1_max36_25pct_cap120 on the SPY-availability-bound sample "
            f"({n_months} months, 1993 onward; HSN1FNSA history extends to 1963 but the "
            f"tournament requires target returns). min(max(36, round({n_months}*0.25)), 120) = {oos_n} "
            f"months. Regime models (HMM, Markov-switching) are fit on IS rows only. "
            f"No structural-break exclusion applied."),
    }
    with open(os.path.join(RESULTS_DIR, "oos_split_record.json"), "w") as f:
        json.dump(split, f, indent=2)

    tdf, sel = run_grid(df, {"oos_start": oos_start, "oos_end": oos_end, "is_end": is_end})
    CTX["selection"] = sel
    tpath = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _tournament_io import write_tournament  # ECON-T5 §4 immutability guard
    write_tournament(tdf, tpath)
    side_cols = ["signal", "threshold", "strategy", "lookback", "direction", "lead_months", "is_start", "is_end",
                 "is_n", "is_sharpe", "own_is_start", "own_is_n", "own_is_sharpe", "oos_sharpe", "oos_ann_return",
                 "max_drawdown", "n_trades", "oos_n", "is_rank", "oos_rank"]
    side = [dict(role="primary_is_selected_common_start", **tdf.loc[sel["wi"], side_cols].to_dict()),
            dict(role="sensitivity_is_selected_own_start", **tdf.loc[sel["oi"], side_cols].to_dict())]
    if sel["li"] is not None:
        side.append(dict(role="legacy_oos_selected", **tdf.loc[sel["li"], side_cols].to_dict()))
    pd.DataFrame(side).to_csv(os.path.join(RESULTS_DIR, f"legacy_oos_selection_{DATE_TAG}.csv"), index=False)

    strat_pop = tdf[tdf.signal != "BENCHMARK"]
    n_valid = int(strat_pop["valid"].sum())
    w = tdf.loc[sel["wi"]]
    print(f"  common IS start {sel['common_is_start'].date()} (set by {sel['driver']}); {sel['n_inel']} ineligible")
    print(f"  Combos: {len(strat_pop)} + 1 benchmark; IS-valid {n_valid} ({sel['n_distinct']} distinct series)")
    print(f"  WINNER (IS argmax): {w.signal}/{w.threshold}/{w.strategy}/L{w.lead_months}/{w.lookback} "
          f"IS {w.is_sharpe:.4f} OOS {w.oos_sharpe:.4f} (B&H IS {sel['bh_is']['sharpe']:.4f} OOS {sel['bh']['sharpe']:.4f}); "
          f"tie step {sel['tie_step']}")
    if sel["li"] is not None:
        lw = tdf.loc[sel["li"]]
        print(f"  legacy OOS-argmax on this grid: {lw.signal}/{lw.threshold}/{lw.strategy}/L{lw.lead_months}/"
              f"{lw.lookback} OOS {lw.oos_sharpe:.4f}")
    print(f"  Spearman(IS, OOS) over IS-valid = {sel['spearman']:.3f}")

    manifest = {
        "file": os.path.basename(tpath), "pair_id": PAIR_ID,
        "grid": {"signals": sorted(strat_pop["signal"].unique().tolist()),
                 "thresholds": "T1_fixed_p{25,50,75} (IS percentiles), T2_roll_p{25,75}, T3_zscore_{±1.0,±1.5}, T4_zero (growth signals)",
                 "strategies": [s + "_{pro,counter}" for s in STRATEGIES],
                 "leads_months": LEADS, "lookbacks": list(LOOKBACKS.keys()) + ["LB_NA"]},
        "selection": "argmax IS Sharpe on the common IS window [common_is_start, oos_start); OOS never consulted (is_valid/valid). oos_valid = pre-#251 OOS rule, comparison only",
        "validity": f"IS window only: eligible (own IS n >= {MIN_IS_N}), is_n >= {MIN_IS_N}, IS exposure in [0.05, 0.95] (P3: share of months long), IS std > 0, IS turnover < {MAX_TURNOVER}/yr",
        "warmup": "positions are NaN (not traded, excluded from IS metrics) until the lagged signal and its rolling threshold are defined; OOS scored deployable (fillna 0)",
        "regime_signals": "hmm_stress / markov_regime: IS-only fit, forward-filtered (scripts/_regime_causal.py); core_models/regime_models.json",
        "units": "oos_ann_return / oos_ann_vol / max_drawdown are RATIOS (decimal), not percent",
        "total_strategy_rows": len(strat_pop), "valid_strategy_rows": n_valid,
        "common_is_start": sel["common_is_start"].date().isoformat(), "common_is_start_set_by": sel["driver"],
        "spearman_is_vs_oos": round(sel["spearman"], 4),
        "benchmark_row": "signal==BENCHMARK, valid=False per ECON-T4",
        "execution_lag": "position_t = rule(signal_{t-lead}); registry lead floor L2 (Census publishes month M near the end of M+1); grid bottom truncated to the floor",
        "cost_note": "returns are gross of costs; 5bps sensitivity in tournament_validation",
        "generated_at": NOW_ISO,
    }
    with open(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return tdf, split


# ===================================================================
# STAGE 7: WINNER (IS-selected) + artifacts (trade logs, strategy returns)
# ===================================================================
@log_stage("7_winner_artifacts")
def stage_winner(df, tdf, split):
    sel = CTX["selection"]
    winner = tdf.loc[sel["wi"]]
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid]
    n_valid = len(cand)
    median_sharpe = float(cand["is_sharpe"].median())
    resolved_at = sel["tie_step"]
    n_tied = int((cand["is_sharpe"] - winner["is_sharpe"]).abs().le(1e-9).sum())
    print(f"  Winner: {winner['signal']}/{winner['threshold']}/{winner['strategy']}/L{winner['lead_months']}/{winner['lookback']}")
    print(f"  IS Sharpe {winner['is_sharpe']} | OOS Sharpe {winner['oos_sharpe']} | tie step {resolved_at}")

    if resolved_at > 1:
        lines = [f"# Tournament Tie Note - {PAIR_ID} ({DATE_TAG})", "",
                 f"Winner resolved at IS cascade step {resolved_at} (is_sharpe, is_ann_return, is_max_drawdown, "
                 "is_n_trades, then names).", "",
                 cand[(cand["is_sharpe"] - winner["is_sharpe"]).abs() <= 1e-9][
                     ["signal", "threshold", "strategy", "lead_months", "lookback", "is_sharpe",
                      "is_ann_return", "is_max_drawdown", "is_n_trades", "oos_sharpe"]].to_markdown(index=False)]
        with open(os.path.join(RESULTS_DIR, "tournament_tie_note.md"), "w") as f:
            f.write("\n".join(lines))

    work = df.dropna(subset=["spy_ret"])
    is_full = work.index <= split["in_sample_end"]
    position, strat_ret, sig_lagged, thr = replay(work, winner["signal"], winner["threshold"], winner["lookback"],
                                                 winner["strategy"], int(winner["lead_months"]), is_full)
    spy_ret = work["spy_ret"]
    oos_mask = (spy_ret.index >= split["oos_start"]) & (spy_ret.index <= split["oos_end"])
    m = ann_metrics(strat_ret[oos_mask].fillna(0.0))
    rec = {}
    for key, computed, reported, tol in [
            ("oos_sharpe", m["sharpe"], float(winner["oos_sharpe"]), 1e-5),
            ("oos_max_drawdown", m["max_dd"], float(winner["max_drawdown"]), 1e-5),
            ("oos_ann_return", m["ann_return"], float(winner["oos_ann_return"]), 1e-5)]:
        diff = computed - reported
        rec[key] = {"computed": round(float(computed), 6), "reported_tournament": reported,
                    "diff": round(float(diff), 6), "tolerance": tol,
                    "verdict": "PASS" if abs(diff) <= tol else "FAIL"}
    assert all(v["verdict"] == "PASS" for v in rec.values()), f"ECON-SR1 reconciliation FAILED: {rec}"
    print("  ECON-SR1 reconciliation: PASS on all three headline metrics")

    pos_f = position.reindex(spy_ret.index).fillna(0.0)
    sr_f = strat_ret.reindex(spy_ret.index).fillna(0.0)
    sr = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"), "position": pos_f.values,
                       "strategy_return": sr_f.values, "bh_return": spy_ret.values})
    sr_path = os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv")
    sr.to_csv(sr_path, index=False)
    sr_meta = {
        "pair_id": PAIR_ID, "artifact": os.path.basename(sr_path),
        "produced_by": "scripts/pair_pipeline_nhs_spy.py", "rule": "ECON-SR1",
        "source": "pipeline_native_derivation (same replay() as the tournament)",
        "returns_file": os.path.relpath(DATA_PATH, BASE_DIR),
        "coverage_start": str(spy_ret.index[0].date()), "coverage_end": str(spy_ret.index[-1].date()),
        "frequency": "monthly", "oos_start": split["oos_start"], "oos_end": split["oos_end"],
        "position_semantics": ("position on row t is the return-accrual weight for month t; the "
                               f"signal is lagged {int(winner['lead_months'])} month(s); strategy_return = "
                               "position * bh_return row-wise; warm-up rows (signal or threshold undefined) written as 0"),
        "reconciliation": {k: {"computed": v["computed"], "reported_winner_summary": v["reported_tournament"],
                               "diff": v["diff"], "tolerance": v["tolerance"], "verdict": v["verdict"]}
                           for k, v in rec.items()},
        "generated_at": NOW_ISO, "generated_by": "Econ Evan (fix261016_hmm_port_eci_nhs)",
    }
    with open(os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}_meta.json"), "w") as f:
        json.dump(sr_meta, f, indent=2)

    log = pd.DataFrame({
        "date": spy_ret.index.strftime("%Y-%m-%d"),
        "signal_value": sig_lagged.reindex(spy_ret.index).round(4),
        "threshold": (thr.reindex(spy_ret.index).round(4) if isinstance(thr, pd.Series) else np.round(thr, 4)),
        "position": pos_f, "spy_return": spy_ret.round(6), "strategy_return": sr_f.round(6)})
    log["cumulative_return"] = ((1 + log["strategy_return"]).cumprod() - 1).round(6)
    log_path = os.path.join(RESULTS_DIR, "winner_trade_log.csv")
    log.to_csv(log_path, index=False)

    spy_px = df["spy"].reindex(spy_ret.index)
    broker_rows, cum = [], (1 + sr_f).cumprod()
    prev = 0.0
    capital = 10000.0
    sig_disp = f"{winner['signal']} ({SIGNAL_COLS[winner['signal']]})"
    for dt in spy_ret.index:
        p = float(pos_f.loc[dt])
        if abs(p - prev) > 1e-9:
            side = "BUY" if p > prev else "SELL"
            notional = abs(p - prev) * capital
            sv = sig_lagged.loc[dt] if dt in sig_lagged.index else np.nan
            th = thr.loc[dt] if isinstance(thr, pd.Series) else thr
            broker_rows.append({
                "trade_date": dt.strftime("%Y-%m-%d"), "side": side, "instrument": TARGET_SYMBOL,
                "quantity_pct": round(abs(p) * 100, 1),
                "price": round(float(spy_px.loc[dt]), 4) if pd.notna(spy_px.loc[dt]) else np.nan,
                "notional_usd": round(notional, 2), "commission_bps": COST_BPS,
                "commission_usd": round(notional * COST_BPS / 10000, 2),
                "cum_pnl_pct": round((cum.loc[dt] - 1) * 100, 4),
                "reason": (f"{winner['strategy']}: {sig_disp} = {sv:.3f} vs threshold {th:.3f} — "
                           f"position {prev*100:.0f}% → {p*100:.0f}%"
                           if pd.notna(sv) and pd.notna(th) else "position change"),
            })
            prev = p
    broker_path = os.path.join(RESULTS_DIR, "winner_trades_broker_style.csv")
    with open(broker_path, "w") as f:
        f.write(f"# Simulated trade record based on backtest signals. No real trades were executed. "
                f"Starting capital: $10000. Commission: {COST_BPS} bps (tournament cost parameter). "
                f"Pair: {PAIR_ID}. Strategy: {winner['strategy']} on {sig_disp}, "
                f"threshold {winner['threshold']}, lead L{winner['lead_months']}, {winner['lookback']}.\n")
        pd.DataFrame(broker_rows).to_csv(f, index=False)
    print(f"  Trade logs -> {log_path} ({len(log)} rows), broker-style ({len(broker_rows)} events)")
    CTX["winner_series"] = dict(position=position, strat_ret=strat_ret, work=work)
    return winner, rec, n_valid, median_sharpe, n_tied, resolved_at, pos_f, sr_f, sig_lagged, thr


# ===================================================================
# STAGE 7b: LOOK-AHEAD AUDIT (superseded smoothed-HMM rule vs causal)
# ===================================================================
@log_stage("7b_lookahead_audit")
def stage_lookahead_audit(df, split):
    """Score the PREVIOUSLY PUBLISHED rule (hmm_stress / T2_roll_p25 / LB60 / P1_long_cash_pro / L0)
    on (a) the committed smoothed full-sample HMM column (signals_{PREV_TAG}.parquet, immutable,
    not re-fitted) with the old warm-up semantics, which must reproduce the published OOS Sharpe,
    and (b) this run's causal HMM column, at L0 (as published, below the L2 floor) and at the
    floor L2."""
    prev_ws = json.load(open(os.path.join(RESULTS_DIR, "winner_summary.json")))
    prev_sel = prev_ws.get("selection", {})
    if prev_sel.get("objective") == "max_is_sharpe":           # rerun on an already-ported tree
        prev = {k: prev_sel["previously_published"][k]
                for k in ("signal", "threshold", "strategy", "lead_months", "lookback", "oos_sharpe", "source")}
    else:
        rw = prev_sel["raw_winner_row"]
        prev = {"signal": rw["signal"], "threshold": rw["threshold"], "strategy": rw["strategy"],
                "lead_months": int(rw["lead_value"]), "lookback": prev_ws["lookback"],
                "oos_sharpe": float(prev_ws["oos_sharpe"]), "source": f"winner_summary.json ({PREV_TAG})"}
    work = df.dropna(subset=["spy_ret"]).copy()
    old = pd.read_parquet(os.path.join(RESULTS_DIR, f"signals_{PREV_TAG}.parquet"))["hmm_2state_prob_stress"]
    work["smoothed_fullsample"] = old.reindex(work.index)
    work["causal_filtered"] = work["hmm_2state_prob_stress"]
    is_full = work.index <= split["in_sample_end"]
    oos = (work.index >= split["oos_start"]) & (work.index <= split["oos_end"])

    def score(col, lead):
        sig = work[col].shift(lead)
        thr = thresholds_for("hmm_stress", sig, is_full)[(prev["threshold"], prev["lookback"])]
        above = sig < thr if "neg_" in prev["threshold"] else sig > thr   # pre-port semantics (NaN -> False)
        pos = (~above).astype(float) if prev["strategy"].endswith("counter") else above.astype(float)
        if not prev["strategy"].startswith("P1"):
            raise NotImplementedError(prev["strategy"])
        r = (pos * work["spy_ret"])[oos].fillna(0.0)
        a = ann_metrics(r)
        t, p, nw = hac_t_mean(r)
        return {"oos_sharpe": round(a["sharpe"], 6), "oos_ann_return": round(a["ann_return"], 6),
                "oos_max_drawdown": round(a["max_dd"], 6), "hac_t": round(t, 3), "hac_p": round(p, 4),
                "hac_maxlags": nw, "oos_exposure": round(float(pos[oos].mean()), 4)}

    rows = []
    for col in ["smoothed_fullsample", "causal_filtered"]:
        for lead in sorted({int(prev["lead_months"]), min(LEADS)}):
            rows.append({"probabilities": col, "lead_months": lead, **score(col, lead)})
    rep = next(r for r in rows if r["probabilities"] == "smoothed_fullsample" and r["lead_months"] == int(prev["lead_months"]))
    reproduced = abs(rep["oos_sharpe"] - float(prev["oos_sharpe"])) < 1e-4
    assert reproduced, f"old smoothed replay {rep['oos_sharpe']} != published {prev['oos_sharpe']} (data drift)"
    bh = ann_metrics(work["spy_ret"][oos])
    out = {"rule": (f"{prev['signal']} / {prev['threshold']} / {prev['lookback']} / {prev['strategy']} / "
                    f"L{prev['lead_months']}; strat_ret = position_t * spy_ret_t"),
           "previously_published": prev, "oos_window": [split["oos_start"], split["oos_end"]],
           "published_reproduced_from_committed_smoothed_column": bool(reproduced),
           "reproduction_note": ("published value is rounded to 4 d.p.; replay matches to < 1e-4 (monthly SPY returns "
                                 "re-pulled from yfinance differ from the 20260703 file by <= 1.6e-6)"),
           "causal_fit": CTX.get("hmm_fit"),
           "rows": rows, "bh_oos_sharpe": round(bh["sharpe"], 6)}
    d = (work["smoothed_fullsample"] - work["causal_filtered"])[oos]
    out["corr_smoothed_minus_filtered_vs_same_month_spy_ret_oos"] = round(float(d.corr(work["spy_ret"][oos])), 4)
    with open(os.path.join(RESULTS_DIR, f"hmm_lookahead_audit_{DATE_TAG}.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    for r in rows:
        print(f"  {r['probabilities']:20s} L{r['lead_months']}: OOS Sharpe {r['oos_sharpe']:.4f}  HAC t {r['hac_t']:.2f}")
    CTX["audit"] = out
    return out


# ===================================================================
# STAGE 8: CROSS-PERIOD ANALYSES (ECON-CP1 A/B/C)
# ===================================================================
@log_stage("8_cross_period")
def stage_cross_period(df, winner, split, position, strat_ret, sig_lagged):
    import statsmodels.api as sm

    with open(os.path.join(SCHEMA_DIR, "episode_registry.json")) as f:
        reg = json.load(f)
    episodes = reg.get("activity", reg["_fallback"])  # housing indicator -> activity episode set
    oos = strat_ret[(strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])]
    rows = []
    pos_eps = 0
    eval_eps = 0
    for ep in episodes:
        sub = oos[(oos.index >= ep["start"]) & (oos.index <= ep["end"])].dropna()
        if len(sub) < 3:
            rows.append({"episode": ep["slug"], "start_date": ep["start"], "end_date": ep["end"],
                         "n_trading_days": len(sub) * 21, "ann_sharpe": np.nan, "win_rate": np.nan,
                         "max_drawdown": np.nan, "data_status": "insufficient_data",
                         "durability_verdict": ""})
            continue
        m = ann_metrics(sub)
        eval_eps += 1
        pos_eps += int(m["sharpe"] > 0)
        rows.append({"episode": ep["slug"],
                     "start_date": str(sub.index[0].date()), "end_date": str(sub.index[-1].date()),
                     "n_trading_days": len(sub) * 21, "ann_sharpe": round(m["sharpe"], 4),
                     "win_rate": round(m["win_rate"], 4), "max_drawdown": round(m["max_dd"], 4),
                     "data_status": "validated", "durability_verdict": ""})
    if eval_eps >= 3:
        verdict = "durable" if pos_eps >= 3 else ("conditionally_durable" if pos_eps == 2 else "episode_concentrated")
    else:
        verdict = ("conditionally_durable" if pos_eps == eval_eps and eval_eps > 0
                   else "episode_concentrated") if eval_eps else "insufficient_data"
    rows[-1]["durability_verdict"] = verdict
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "subperiod_sharpe.csv"), index=False)
    print(f"  CP1-A: {eval_eps} episodes evaluable within OOS, {pos_eps} positive -> {verdict}")

    v = pd.concat([sig_lagged.rename("sig"), df["spy_fwd_1m"]], axis=1).dropna()
    full_r = v["sig"].corr(v["spy_fwd_1m"])
    roll = v["sig"].rolling(24).corr(v["spy_fwd_1m"])
    out = pd.DataFrame({"date": v.index.strftime("%Y-%m-%d"), "rolling_corr": roll.round(4).values,
                        "n_obs": 24,
                        "window_start": v.index.to_series().shift(23).dt.strftime("%Y-%m-%d").values})
    out = out.dropna(subset=["rolling_corr"])
    out.to_csv(os.path.join(RESULTS_DIR, f"rolling_correlation_{PAIR_ID}.csv"), index=False)
    same_sign = float((np.sign(roll.dropna()) == np.sign(full_r)).mean())
    stab = ("sign_stable" if same_sign >= 0.7 else
            "moderately_stable" if same_sign >= 0.5 else "sign_unstable")
    print(f"  CP1-B: full-sample r={full_r:.3f}, sign stability {same_sign:.2f} -> {stab}")

    reg_v = pd.concat([sig_lagged.rename("sig"), df["spy_ret"]], axis=1).dropna()
    yv = reg_v["spy_ret"].values
    Xv = sm.add_constant(reg_v["sig"].values)
    n = len(yv)
    lo, hi = int(n * 0.15), int(n * 0.85)
    full = sm.OLS(yv, Xv).fit()
    k = Xv.shape[1]

    def sup_f(y, X):
        ssr_f = sm.OLS(y, X).fit().ssr
        best, bidx = -np.inf, lo
        for b in range(lo, hi):
            s1 = sm.OLS(y[:b], X[:b]).fit().ssr
            s2 = sm.OLS(y[b:], X[b:]).fit().ssr
            f = ((ssr_f - s1 - s2) / k) / ((s1 + s2) / (len(y) - 2 * k))
            if f > best:
                best, bidx = f, b
        return best, bidx

    f_obs, b_idx = sup_f(yv, Xv)
    rng = np.random.default_rng(42)
    null = []
    resid = full.resid
    fitted = full.fittedvalues
    for _ in range(300):
        y_b = fitted + rng.choice(resid, size=n, replace=True)
        fb, _ = sup_f(y_b, Xv)
        null.append(fb)
    p_break = float((np.array(null) >= f_obs).mean())
    break_date = str(reg_v.index[b_idx].date())
    flagged = p_break < 0.10
    sb = {"pair_id": PAIR_ID, "test": "Quandt-Andrews unknown breakpoint (sup-F, residual-bootstrap p, 300 reps)",
          "sample_start": str(reg_v.index[0].date()), "sample_end": str(reg_v.index[-1].date()),
          "n_obs": n, "trimming_pct": 0.15, "break_date": break_date,
          "f_stat": round(float(f_obs), 4), "p_value": round(p_break, 4), "flagged": flagged,
          "flag_message": ("Structural break detected — interpret cross-period results with caution."
                           if flagged else None),
          "rolling_corr_sign_stability": round(same_sign, 4),
          "rolling_corr_stability_verdict": stab,
          "cp2_note": "CP2 skipped — regime_story not set in signal_scope.json"}
    with open(os.path.join(RESULTS_DIR, f"structural_break_{PAIR_ID}.json"), "w") as f:
        json.dump(sb, f, indent=2)
    print(f"  CP1-C: sup-F={f_obs:.2f} at {break_date}, bootstrap p={p_break:.3f}, flagged={flagged}")
    return verdict, stab, sb, full_r


# ===================================================================
# STAGE 9: VALIDATION (bootstrap, stress, tx-costs)
# ===================================================================
@log_stage("9_validation")
def stage_validation(df, tdf, split, strat_ret):
    spy_oos = df["spy_ret"][(df.index >= split["oos_start"]) & (df.index <= split["oos_end"])].dropna()
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid]
    # winner + next four DISTINCT IS-ranked candidates (no OOS ranking)
    wi = CTX["selection"]["wi"]
    distinct = CTX["selection"]["ranked"].drop_duplicates(["signal", "strategy", "lead_months", "lookback",
                                                           "is_sharpe", "oos_sharpe"])
    top5 = pd.concat([tdf.loc[[wi]], distinct.drop(index=wi, errors="ignore").head(4)])
    rng = np.random.default_rng(42)
    boot = np.zeros(5000)
    for b in range(5000):
        s = rng.choice(spy_oos.values, size=len(spy_oos), replace=True)
        boot[b] = (s.mean() / s.std()) * np.sqrt(12) if s.std() > 0 else 0
    rows = [{"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
             "lead_months": r.lead_months, "lookback": r.lookback, "oos_sharpe": r.oos_sharpe,
             "is_sharpe": r.is_sharpe,
             "bootstrap_p_value": round(float((boot >= r.oos_sharpe).mean()), 4),
             "significant_at_5pct": bool((boot >= r.oos_sharpe).mean() < 0.05),
             "note": "share of iid-resampled B&H OOS Sharpes >= this row's OOS Sharpe; not a selection-bias test"}
            for r in top5.itertuples()]
    pd.DataFrame(rows).to_csv(os.path.join(VALID_DIR, "bootstrap.csv"), index=False)

    stress = {"Dot_Com": ("2000-03-01", "2002-10-31"), "GFC": ("2008-01-01", "2009-06-30"),
              "COVID": ("2020-01-01", "2020-06-30"), "Rate_Hike_2022": ("2022-01-01", "2023-06-30")}
    srows = []
    for nm, (s, e) in stress.items():
        sub_bh = df["spy_ret"][(df.index >= s) & (df.index <= e)].dropna()
        sub_st = strat_ret[(strat_ret.index >= s) & (strat_ret.index <= e)].dropna()
        if len(sub_bh) > 3:
            srows.append({"period": nm, "start": s, "end": e, "n_months": len(sub_bh),
                          "buy_hold_sharpe": round(ann_metrics(sub_bh)["sharpe"], 4),
                          "buy_hold_return_pct": round(sub_bh.sum() * 100, 2),
                          "winner_sharpe": round(ann_metrics(sub_st)["sharpe"], 4) if len(sub_st) > 3 else np.nan,
                          "winner_return_pct": round(sub_st.sum() * 100, 2) if len(sub_st) > 3 else np.nan})
    pd.DataFrame(srows).to_csv(os.path.join(VALID_DIR, "stress_tests.csv"), index=False)

    tx = []
    for r in top5.itertuples():
        for bps in [0, 5, 10, 25, 50]:
            ann_cost = r.annual_turnover * bps / 10000
            net_sharpe = r.oos_sharpe - ann_cost / r.oos_ann_vol if r.oos_ann_vol > 0 else r.oos_sharpe
            tx.append({"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
                       "tx_cost_bps": bps, "gross_sharpe": r.oos_sharpe,
                       "net_sharpe_approx": round(net_sharpe, 4)})
    pd.DataFrame(tx).to_csv(os.path.join(VALID_DIR, "transaction_costs.csv"), index=False)
    print(f"  bootstrap (top5), stress ({len(srows)} periods), tx-cost grid saved")
    return rows


# ===================================================================
# HELPERS used by main
# ===================================================================
def _recompute_oos_from_winner_summary(df, ws, split):
    """Independently recompute OOS Sharpe FROM the winner_summary encoded rule.
    umcsent-precedent guardrail: must reproduce headline within +/-0.03."""
    work = df.dropna(subset=["spy_ret"]).copy()
    is_mask = work.index <= split["in_sample_end"]
    code = next(k for k, v in SIGNAL_COLS.items() if v == ws["signal_column"])
    strat = ws["strategy_family"]
    if strat == "P2_signal_strength":
        orientation = "pro" if ws["direction"] == "procyclical" else "counter"
    else:   # threshold_rule is the long-entry relation: gt/lt -> pro, lte/gte -> counter
        orientation = "pro" if ws["threshold_rule"] in ("gt", "lt") else "counter"
    _, strat_ret, _, _ = replay(work, code, ws["threshold_code"], ws["lookback"], f"{strat}_{orientation}",
                                int(ws["lead_value"]), is_mask)
    oos_mask = (strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])
    m = ann_metrics(strat_ret[oos_mask].fillna(0.0))
    return {"oos_sharpe": m["sharpe"], "oos_ann_return": m["ann_return"], "oos_max_drawdown": m["max_dd"]}


def _ensure_signal_code_registered(sig_code, winner, parquet_col):
    reg_path = os.path.join(SCHEMA_DIR, "signal_code_registry.json")
    with open(reg_path) as f:
        reg = json.load(f)
    existing = {e["signal_code"] for e in reg["signals"]}
    if sig_code in existing:
        print(f"  signal_code registry assertion: PASS ({sig_code} already registered)")
        return
    descr_map = {
        "yoy": "12-month percent change in New Home Sales (FRED HSN1FNSA, NSA); primary deseasonalised signal.",
        "yoy_accel": "Month-on-month change in NHS YoY growth (acceleration, pp).",
        "yoy_3m": "YoY percent change of the 3-month moving average of NHS (smooths NSA noise).",
        "sa_mom": "Month-over-month percent change of the STL seasonally-adjusted NHS level.",
        "sa_3m": "Three-month percent change of the STL seasonally-adjusted NHS level.",
        "yoy_zscore_120m": "Rolling 120-month z-score of NHS YoY growth.",
        "contraction": "Binary flag: 1 when NHS YoY growth < 0 (housing-demand contraction).",
    }
    reg["signals"].append({
        "signal_code": sig_code,
        "display_name": f"NHS {winner['signal']} ({INDICATOR_NAME})",
        "parquet_column_pattern": parquet_col,
        "description": descr_map.get(winner["signal"], f"HSN1FNSA transform {winner['signal']}."),
        "source_method": "roc" if winner["signal"] in ("yoy", "yoy_3m", "sa_mom", "sa_3m") else (
            "zscore" if "zscore" in winner["signal"] else "transform"),
        "added_at": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
        "first_pair": PAIR_ID,
        "notes": "New Home Sales (NSA) growth transform; tested both procyclical and countercyclical in the tournament.",
    })
    with open(reg_path, "w") as f:
        json.dump(reg, f, indent=2)
    print(f"  signal_code registry: APPENDED {sig_code} (ECON-DS3 append-only)")


def _write_evidence_status(ws, split, n_valid, is_window, t_oos, bh_vol):
    bs = ws["selection"]["inference"]["oos_sharpe_diff_vs_bh_bootstrap"]
    es = {
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search",
        "updated_at": NOW_ISO, "owner": "evan",
        "technical_note": (
            f"Winner selected by in-sample Sharpe (common pre-OOS window {is_window['start']}..{is_window['end']}) "
            f"from the {DATE_TAG} monthly tournament ({n_valid} IS-valid combos) and evaluated on the held-out OOS "
            f"window {split['oos_start']}..{split['oos_end']} ({ws['oos_n']} months): OOS Sharpe {ws['oos_sharpe']:.2f} "
            f"vs B&H {ws['bh_sharpe']:.2f}, HAC t {t_oos:.2f}. No frozen-rule confirmation test has been run."),
        "plain_english": (f"This is the rule with the highest in-sample Sharpe among {n_valid} valid combinations. "
                          f"On the {ws['oos_n']}-month out-of-sample window: Sharpe {ws['oos_sharpe']:.2f} versus "
                          f"{ws['bh_sharpe']:.2f} for buy-and-hold; paired block-bootstrap 95% interval of the Sharpe "
                          f"difference [{bs['ci_95'][0]:+.2f}, {bs['ci_95'][1]:+.2f}], so the two are not statistically "
                          f"distinguishable; annualized return {ws['oos_ann_return']*100:.1f}% versus "
                          f"{ws['bh_ann_return']*100:.1f}%, with lower volatility ({ws['oos_ann_vol']*100:.1f}% vs "
                          f"{bh_vol*100:.1f}%) and drawdown ({ws['oos_max_drawdown']*100:.1f}% vs "
                          f"{ws['bh_max_drawdown']*100:.1f}%). It has not been tested on data released after it was chosen."),
        "next_step": "Freeze the rule and evaluate it on months released after the freeze date.",
    }
    with open(os.path.join(RESULTS_DIR, "evidence_status.json"), "w") as f:
        json.dump(es, f, indent=2)


# ===================================================================
# MAIN
# ===================================================================
def main():
    t0 = time.time()
    df = stage_load()
    sp = compute_split(df)
    df = stage_signals(df, sp["oos_start"])
    corr_df = stage_correlations(df)
    ccf_df, ty_df, lp_df, reg_df, rev_flag = stage_core_models(df)
    qdf = stage_quartiles(df)
    tdf, split = stage_tournament(df, sp)
    (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
     position, strat_ret, sig_lagged, thr) = stage_winner(df, tdf, split)
    audit = stage_lookahead_audit(df, split)
    verdict, stab, sb, full_r = stage_cross_period(df, winner, split, position, strat_ret, sig_lagged)
    boot_rows = stage_validation(df, tdf, split, strat_ret)
    winner_boot_p = boot_rows[0]["bootstrap_p_value"] if boot_rows else np.nan

    bh = tdf[tdf.signal == "BENCHMARK"].iloc[0]
    sel = CTX["selection"]
    wi, oi, li = sel["wi"], sel["oi"], sel["li"]

    orientation = winner["strategy"].rsplit("_", 1)[1]
    neg_thr = "neg_" in winner["threshold"]
    long_when_high = (orientation == "pro") != neg_thr
    direction = "procyclical" if long_when_high else "countercyclical"
    strat_family = winner["strategy"].rsplit("_", 1)[0]

    thr_value = float(thr.dropna().iloc[-1]) if isinstance(thr, pd.Series) else float(thr)
    # long-entry relation of the (lagged) signal to its threshold (schema: entry = signal satisfies relation)
    thr_rule = {(False, "pro"): "gt", (False, "counter"): "lte",
                (True, "pro"): "lt", (True, "counter"): "gte"}[(neg_thr, orientation)]

    if winner["signal"].startswith(("hmm", "markov")):
        sig_code = {"hmm_stress": "hmm_stress", "markov_regime": "markov_regime"}[winner["signal"]]
    else:
        sig_code = f"nhs_{winner['signal']}"

    _SIGNAL_DISPLAY = {
        "yoy": "New Home Sales YoY growth",
        "yoy_accel": "New Home Sales YoY acceleration",
        "yoy_3m": "New Home Sales 3-month-average YoY growth",
        "sa_mom": "New Home Sales SA month-over-month growth",
        "sa_3m": "New Home Sales SA 3-month growth",
        "yoy_zscore_120m": "New Home Sales YoY z-score",
        "contraction": "New Home Sales YoY contraction flag",
        "hmm_stress": "New Home Sales HMM stress probability (causal)",
        "markov_regime": "New Home Sales Markov-regime probability (causal)",
    }
    signal_display_name = _SIGNAL_DISPLAY.get(winner["signal"], f"New Home Sales {winner['signal']}")

    oos_r = strat_ret[(strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])]
    t_oos, p_oos, nw_oos = hac_t_mean(oos_r)
    ws_meta = CTX["winner_series"]
    is_r = ws_meta["strat_ret"][(ws_meta["work"].index >= sel["common_is_start"]) &
                                (ws_meta["work"].index < pd.Timestamp(split["oos_start"]))].dropna()
    t_is, p_is, nw_is = hac_t_mean(is_r)
    from scipy.stats import norm
    exp_max_z = float(norm.ppf(1 - 0.5 / max(sel["n_distinct"], 1)))
    cand_all = tdf[(tdf.signal != "BENCHMARK") & tdf.valid]

    is_window = {"start": str(winner["is_start"]), "end": str(winner["is_end"]), "n": int(winner["is_n"]),
                 "common_is_start": sel["common_is_start"].date().isoformat(), "oos_start": split["oos_start"],
                 "min_is_n": MIN_IS_N, "n_candidates": sel["n_cands"], "n_eligible": sel["n_eligible"],
                 "n_ineligible_short_history": sel["n_inel"], "common_start_set_by": sel["driver"],
                 "rule": (f"eligibility before alignment: a candidate is IS-eligible only if its own first valid return "
                          f"leaves >= {MIN_IS_N} IS months; common_is_start = latest first-valid-return date among "
                          "eligible candidates; IS metrics for every candidate computed on [common_is_start, oos_start)"),
                 "validity": (f"IS window only: is_n >= {MIN_IS_N}, IS exposure in [0.05, 0.95] (P3: share of months "
                              f"long), IS std > 0, IS turnover < {MAX_TURNOVER}/yr; OOS never consulted"),
                 "bh_is_sharpe": round(float(sel["bh_is"]["sharpe"]), 6)}

    def _ro(r):
        return None if r is None else {
            "signal": str(r["signal"]), "threshold": str(r["threshold"]), "strategy": str(r["strategy"]),
            "lead_value": int(r["lead_months"]), "objective_value": round(float(r["is_sharpe"]), 6),
            "oos_sharpe": round(float(r["oos_sharpe"]), 6)}

    ranked = sel["ranked"]
    runner = ranked.drop(index=wi).iloc[0] if len(ranked) > 1 else None
    distinct_rank = ranked.drop_duplicates(["signal", "strategy", "lead_months", "lookback", "is_sharpe", "oos_sharpe"])
    runner_d = distinct_rank.drop(index=wi, errors="ignore")
    runner_d = runner_d.iloc[0] if len(runner_d) else None
    prev = audit["previously_published"]
    rep_rows = {(r["probabilities"], r["lead_months"]): r for r in audit["rows"]}
    prev_l = int(prev["lead_months"])
    floor_l = min(LEADS)
    tourn_file = f"tournament_results_{DATE_TAG}.csv"

    winner_summary = {
        "pair_id": PAIR_ID,
        "generated_at": NOW_ISO,
        "signal_column": SIGNAL_COLS[winner["signal"]],
        "signal_code": sig_code,
        "signal_display_name": signal_display_name,
        "target_symbol": TARGET_SYMBOL,
        "threshold_code": winner["threshold"],
        "threshold_value": round(thr_value, 4),
        "threshold_rule": thr_rule,
        "threshold_note": ("threshold is rolling (window per lookback, in months); threshold_value is its latest "
                           "value — see winner_trade_log.csv for the full threshold path"
                           if isinstance(thr, pd.Series) else
                           "static threshold: percentile of the lead-shifted signal over the IS months"),
        "strategy_family": strat_family,
        "strategy_code": strat_family.split("_")[0],
        "strategy_display_name": {"P1_long_cash": "Long/Cash", "P2_signal_strength": "Signal-strength sizing",
                                  "P3_long_short": "Long/Short"}[strat_family],
        "strategy_description": "",
        "lead_value": int(winner["lead_months"]),
        "lead_unit": "months",
        "lead_description": (f"Signal lead = {int(winner['lead_months'])} month(s); registry floor L{floor_l} "
                             "(Census publishes month M near the end of M+1)"),
        "lookback": winner["lookback"],
        "direction": direction,
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "oos_sortino": round(float(winner["oos_sortino"]), 4),
        "oos_calmar": round(float(winner["oos_calmar"]), 4),
        "oos_ann_return": round(float(winner["oos_ann_return"]), 4),
        "oos_ann_vol": round(float(winner["oos_ann_vol"]), 4),
        "oos_max_drawdown": round(float(winner["max_drawdown"]), 4),
        "oos_win_rate": round(float(winner["win_rate"]), 4),
        "oos_n_trades": int(winner["n_trades"]),
        "annual_turnover": round(float(winner["annual_turnover"]), 2),
        "oos_n": int(winner["oos_n"]),
        "oos_period_start": split["oos_start"],
        "oos_period_end": split["oos_end"],
        "oos_hac_t": round(t_oos, 3),
        "is_sharpe": round(float(winner["is_sharpe"]), 6), "is_n": int(winner["is_n"]),
        "is_period_start": is_window["start"], "is_period_end": is_window["end"],
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_ann_return": round(float(bh["oos_ann_return"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4),
        "bh_is_sharpe": round(float(sel["bh_is"]["sharpe"]), 4),
        "cost_assumption_bps": COST_BPS,
        "total_combos": int(len(tdf) - 1),
        "valid_combos": n_valid,
        "schema_version": "1.2.0",
        "notes": "",
        "selection": {},
    }
    sd = ("Long SPY when the {}-month-lagged {} is {} its threshold; otherwise {}."
          .format(int(winner["lead_months"]), signal_display_name,
                  {"gt": "above", "gte": "at or above", "lt": "below", "lte": "at or below"}[thr_rule],
                  "cash" if strat_family == "P1_long_cash" else "short SPY")
          if strat_family != "P2_signal_strength" else
          ("SPY exposure (0-100%) scales with the {}-month-lagged {}'s position in its trailing {} min-max range{}."
           .format(int(winner["lead_months"]), signal_display_name, winner["lookback"],
                   " (inverted)" if orientation == "counter" else "")))
    sd += (" (Countercyclical orientation: weak/decelerating home sales = risk-on.)" if not long_when_high else
           " (Procyclical orientation: strong home-sales growth = risk-on.)")
    winner_summary["strategy_description"] = sd

    winner_summary["selection"] = {
        "objective": "max_is_sharpe",
        "objective_formula": ("in-sample (common window [common_is_start, OOS start)) monthly mean/std*sqrt(12) of "
                              "position_t*spy_ret_t; winner evaluated on the OOS window with ECON-T4 deployable scoring (fillna 0)"),
        "is_window": is_window,
        "grid_scanned": {
            "leads": LEADS,
            "n_signals": int(tdf.loc[tdf.signal != "BENCHMARK", "signal"].nunique()),
            "n_thresholds": int(tdf.loc[tdf.signal != "BENCHMARK", "threshold"].nunique()),
            "n_strategies": int(tdf.loc[tdf.signal != "BENCHMARK", "strategy"].nunique()),
            "n_combos": int(len(tdf) - 1),
            "n_valid_combos": int(n_valid),
            "n_distinct_position_series": int(sel["n_distinct"]),
            "median_valid_objective": round(float(cand_all["is_sharpe"].median()), 6),
            "spearman_is_vs_oos": round(sel["spearman"], 4),
        },
        "tie_break_step": int(resolved_at),
        "raw_winner_row": {
            "signal": str(winner["signal"]), "threshold": str(winner["threshold"]),
            "strategy": str(winner["strategy"]), "lead_column": "lead_months",
            "lead_value": int(winner["lead_months"]),
            "source_tournament_file": tourn_file, "source_row_index": int(wi),
            "display_alias": (f"{winner['signal']}/{winner['threshold']}/{winner['strategy']}/"
                              f"L{int(winner['lead_months'])}/{winner['lookback']}"),
        },
        "runner_up": _ro(runner),
        "runner_up_distinct_series": _ro(runner_d),
        "rationale": (f"Winner is the IS-valid row with the highest IN-SAMPLE Sharpe (common IS window) over the "
                      f"floored monthly grid L{floor_l}..L{max(LEADS)}; OOS metrics are reported for that row only (no OOS "
                      "look-ahead in selection). Regime signals (HMM, Markov-switching) are IS-fit and "
                      "forward-filtered (scripts/_regime_causal.py)."),
        "legacy_oos_selected_row": (None if li is None else {
            "signal": str(tdf.loc[li, "signal"]), "threshold": str(tdf.loc[li, "threshold"]),
            "strategy": str(tdf.loc[li, "strategy"]), "direction": str(tdf.loc[li, "direction"]),
            "lead_value": int(tdf.loc[li, "lead_months"]), "oos_sharpe": round(float(tdf.loc[li, "oos_sharpe"]), 6),
            "note": f"OOS-argmax on this grid (pre-GH#251 rule), comparison only; see legacy_oos_selection_{DATE_TAG}.csv"}),
        "sensitivity_own_is_start_row": {
            "signal": str(tdf.loc[oi, "signal"]), "threshold": str(tdf.loc[oi, "threshold"]),
            "strategy": str(tdf.loc[oi, "strategy"]), "direction": str(tdf.loc[oi, "direction"]),
            "lead_value": int(tdf.loc[oi, "lead_months"]), "own_is_start": str(tdf.loc[oi, "own_is_start"]),
            "own_is_sharpe": round(float(tdf.loc[oi, "own_is_sharpe"]), 6),
            "oos_sharpe": round(float(tdf.loc[oi, "oos_sharpe"]), 6),
            "note": "IS argmax without common-start alignment; sensitivity only"},
        "previously_published": {
            **{k: prev[k] for k in ("signal", "threshold", "strategy", "lead_months", "lookback", "oos_sharpe")},
            "combo": f"{prev['signal']}/{prev['threshold']}/{prev['lookback']}/{prev['strategy']}/L{prev_l}",
            "hac_t": rep_rows[("smoothed_fullsample", prev_l)]["hac_t"],
            "causal_same_rule_oos_sharpe": rep_rows[("causal_filtered", prev_l)]["oos_sharpe"],
            "causal_same_rule_hac_t": rep_rows[("causal_filtered", prev_l)]["hac_t"],
            "causal_same_rule_at_floor_oos_sharpe": rep_rows[("causal_filtered", floor_l)]["oos_sharpe"],
            "floor_lead": floor_l,
            "source": prev.get("source", f"winner_summary.json ({PREV_TAG})"),
            "status": ("superseded: relied on full-sample, forward-backward smoothed HMM probabilities (look-ahead), "
                       "a lead (L0) below the publication-lag floor, and selection by OOS Sharpe"),
            "audit_file": f"hmm_lookahead_audit_{DATE_TAG}.json"},
        "inference": {"oos_sharpe_diff_vs_bh_bootstrap": dict(paired_block_bootstrap_sharpe_diff(
                          oos_r.values, ws_meta["work"]["spy_ret"].reindex(oos_r.index).values, 6, 12),
                          block_unit="months"),
                      "oos_hac_t": round(t_oos, 3), "oos_hac_p": round(p_oos, 4), "oos_hac_maxlags": nw_oos,
                      "is_hac_t": round(t_is, 3), "is_hac_maxlags": nw_is,
                      "n_distinct_candidates": int(sel["n_distinct"]),
                      "expected_max_abs_z_under_null": round(exp_max_z, 2),
                      "note": "expected max |z| = Phi^-1(1 - 0.5/N) over N distinct position series (two-sided, independence approximation)"},
        "objective_runner_up_divergence": None,
    }
    assert abs(float(winner["is_sharpe"]) - float(cand_all["is_sharpe"].max())) <= 1e-9, \
        "winner must be the IS-valid population max"

    fwd_sig_lags = list(ty_df[(ty_df.direction == "indicator_to_target") & ty_df.significant].lag)
    rev_sig_lags = list(ty_df[(ty_df.direction == "target_to_indicator") & ty_df.significant].lag)
    oos_pos_mean = float(position[(position.index >= split["oos_start"])].mean())
    granger_verdict = (
        f"Toda-Yamamoto Granger NHS->SPY significant at lags {fwd_sig_lags or 'NONE'}; "
        f"SPY->NHS significant at lags {rev_sig_lags or 'NONE'}.")
    pp = winner_summary["selection"]["previously_published"]
    winner_summary["notes"] = (
        f"{DATE_TAG} rerun: tournament of {len(tdf)-1} strategy combos (+1 benchmark), {n_valid} IS-valid, "
        f"floored lead grid {LEADS}. Winner selected by in-sample Sharpe on the common IS window "
        f"{is_window['start']}..{is_window['end']} ({is_window['n']} months) and evaluated on the held-out OOS "
        f"window {split['oos_start']}..{split['oos_end']} ({int(winner['oos_n'])} months): IS Sharpe "
        f"{float(winner['is_sharpe']):.2f} (B&H {sel['bh_is']['sharpe']:.2f}), OOS Sharpe "
        f"{float(winner['oos_sharpe']):.2f} (B&H {float(bh['oos_sharpe']):.2f}), OOS HAC t {t_oos:.2f}. "
        f"Regime signals are IS-fit and forward-filtered. The previously published winner ({pp['combo']}, OOS "
        f"Sharpe {float(prev['oos_sharpe']):.2f}) used full-sample smoothed HMM probabilities at L0; the same rule on "
        f"the causal HMM scores {pp['causal_same_rule_oos_sharpe']:.2f} at L0 and "
        f"{pp['causal_same_rule_at_floor_oos_sharpe']:.2f} at L{floor_l} (hmm_lookahead_audit_{DATE_TAG}.json). "
        f"Input: indicator transforms as published in signals_{PREV_TAG}.parquet. Gross of costs; "
        f"{COST_BPS} bps sensitivity in tournament_validation_{DATE_TAG}/. Lead-lag: {granger_verdict}")

    wpath = os.path.join(RESULTS_DIR, "winner_summary.json")
    with open(wpath, "w") as f:
        json.dump(winner_summary, f, indent=2)
    print(f"\n  winner_summary -> {wpath}")

    # --- ECON-H5 producer validation (blocking) ---
    rc = subprocess.run([PYEXE, os.path.join(BASE_DIR, "scripts", "validate_schema.py"),
                         "--schema", os.path.join(SCHEMA_DIR, "winner_summary.schema.json"),
                         "--instance", wpath]).returncode
    if rc != 0:
        raise SystemExit("winner_summary.json failed schema validation — fix the producer (ECON-H5)")
    print("  winner_summary schema validation: PASS")

    # --- ECON-SR1 winner_summary RE-RECONCILIATION (umcsent guardrail) ---
    recompute = _recompute_oos_from_winner_summary(df, winner_summary, split)
    headline = winner_summary["oos_sharpe"]
    diff = recompute["oos_sharpe"] - headline
    print(f"  ECON-SR1 winner_summary recompute: encoded-rule OOS Sharpe {recompute['oos_sharpe']:.4f} "
          f"vs headline {headline:.4f} (diff {diff:+.4f})")
    if abs(diff) > 0.03:
        raise SystemExit(
            f"winner_summary ENCODING MISMATCH: recomputed {recompute['oos_sharpe']:.4f} "
            f"!= headline {headline:.4f} (|diff|={abs(diff):.4f} > 0.03).")
    print("  winner_summary encoding faithfully reproduces headline OOS Sharpe (±0.03): PASS")

    _ensure_signal_code_registered(sig_code, winner, SIGNAL_COLS[winner["signal"]])

    # --- interpretation_metadata: update EVAN-OWNED fields only ---
    interp_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    with open(interp_path) as f:
        interp = json.load(f)
    interp["observed_direction"] = direction
    interp["direction_consistent"] = interp.get("expected_direction") in ("mixed", direction)
    fwd_found = bool(fwd_sig_lags)
    interp["key_finding"] = (
        f"Lead-lag: New Home Sales YoY {'Granger-causes SPY at lags ' + str(fwd_sig_lags) if fwd_found else 'does NOT Granger-cause SPY at any lag 1-12'}; "
        f"reverse SPY->NHS significant at lags {rev_sig_lags or 'NONE'}. "
        f"The IS-selected tournament winner (NHS {winner['signal']}, {winner['threshold']}, {strat_family} "
        f"{orientation}, lead {winner['lead_months']}m) is {direction}: IS Sharpe {float(winner['is_sharpe']):.2f} vs "
        f"buy-and-hold {sel['bh_is']['sharpe']:.2f}; OOS Sharpe {winner_summary['oos_sharpe']:.2f} vs "
        f"{winner_summary['bh_sharpe']:.2f}, OOS HAC t {t_oos:.2f}, max drawdown "
        f"{winner_summary['oos_max_drawdown']*100:.1f}% vs {winner_summary['bh_max_drawdown']*100:.1f}%.")
    if fwd_found and verdict in ("durable",) and winner_boot_p < 0.05:
        interp["confidence"] = "medium"
    else:
        interp["confidence"] = "low"
    interp["last_updated_by"] = "evan"
    interp["last_updated_at"] = NOW_ISO
    with open(interp_path, "w") as f:
        json.dump(interp, f, indent=2)
    assert interp["observed_direction"] == winner_summary["direction"], "ECON-DIR1 consistency check failed"
    print("  interpretation_metadata evan-fields updated; ECON-DIR1: PASS")

    # tournament_winner.json (META-TWJ)
    tw = {
        "pair_id": PAIR_ID,
        "winner_label": (f"{winner['signal']} / {winner['threshold']} / {strat_family} "
                         f"({orientation}) / L{winner['lead_months']} / {winner['lookback']}"),
        "winner_oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "winner_max_drawdown": round(float(winner["max_drawdown"]), 4),
        "winner_oos_ann_return": round(float(winner["oos_ann_return"]), 4),
        "bh_oos_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4),
        "bh_oos_ann_return": round(float(bh["oos_ann_return"]), 4),
        "delta_sharpe": round(float(winner["oos_sharpe"] - bh["oos_sharpe"]), 4),
        "delta_max_drawdown": round(float(winner["max_drawdown"] - bh["max_drawdown"]), 4),
        "delta_ann_return": round(float(winner["oos_ann_return"] - bh["oos_ann_return"]), 4),
        "beats_benchmark": bool(winner["oos_sharpe"] > bh["oos_sharpe"]),
        "suggested_strategy_objective": None,
        "generated_at": NOW_ISO,
    }
    rel_sharpe = tw["delta_sharpe"] / max(abs(tw["bh_oos_sharpe"]), 0.1)
    rel_dd = tw["delta_max_drawdown"] / max(abs(tw["bh_max_drawdown"]), 0.01)
    tw["suggested_strategy_objective"] = "min_mdd" if rel_dd > rel_sharpe else "max_sharpe"
    with open(os.path.join(RESULTS_DIR, "tournament_winner.json"), "w") as f:
        json.dump(tw, f, indent=2)

    # signal_scope.json (ECON-UD)
    ind_der = [
        {"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []}
        for c, d, s, r in [
            ("nhs_nsa", "New Home Sales, 000s NSA (FRED HSN1FNSA). NON-STATIONARY, seasonal — not used as a signal", "FRED HSN1FNSA", "raw"),
            ("nhs_pct_yoy", "12-month % change in NHS (headline deseasonalised signal)", "100*(N_t/N_{t-12}-1)", "derivative"),
            ("nhs_yoy_accel_pct", "month-on-month change in YoY growth (acceleration, pp)", "yoy_t - yoy_{t-1}", "derivative"),
            ("nhs_3m_pct_yoy", "YoY change of 3-month moving average", "100*(MA3_t/MA3_{t-12}-1)", "derivative"),
            ("nhs_sa", "STL seasonally-adjusted NHS level. NON-STATIONARY — not a signal", "STL(HSN1FNSA)", "raw"),
            ("nhs_sa_pct_mom", "1-month % change of STL SA level", "100*(SA_t/SA_{t-1}-1)", "derivative"),
            ("nhs_sa_3m_pct", "3-month % change of STL SA level", "100*(SA_t/SA_{t-3}-1)", "derivative"),
            ("nhs_yoy_zscore_120m", "rolling 120m z-score of YoY growth", "(yoy_t-mean120)/sd120", "derivative"),
            ("nhs_yoy_contraction_flag", "1 when NHS YoY growth < 0", "indicator(yoy<0)", "regime_state"),
            ("hmm_2state_prob_stress", "forward-filtered P(high-variance state) from a 2-state HMM on YoY growth, fit on IS months only", "GaussianHMM(yoy), IS-only fit, forward filter (scripts/_regime_causal.py)", "regime_state"),
            ("markov_regime_2state", "Hamilton-filtered P(high-variance regime) from a 2-regime switching-variance model of YoY growth, fit on IS months only", "MarkovRegression(yoy), IS-only fit, filter (scripts/_regime_causal.py)", "regime_state"),
        ]]
    tgt_der = [
        {"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []}
        for c, d, s, r in [
            ("spy", "SPY adjusted month-end close", "Yahoo Finance", "raw"),
            ("spy_ret", "SPY monthly return (decimal)", "P_t/P_{t-1}-1", "derivative"),
            ("spy_fwd_1m", "1-month forward SPY return", "P_{t+1}/P_t-1", "derivative"),
            ("spy_fwd_3m", "3-month forward SPY return", "P_{t+3}/P_t-1", "derivative"),
            ("spy_fwd_6m", "6-month forward SPY return", "P_{t+6}/P_t-1", "derivative"),
            ("spy_fwd_12m", "12-month forward SPY return", "P_{t+12}/P_t-1", "derivative"),
        ]]
    scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan",
        "last_updated_by": "evan", "last_updated_at": NOW_ISO,
        "indicator_axis": {
            "canonical_column": "nhs_nsa",
            "display_name": "New Home Sales (NSA)",
            "derivatives": ind_der,
        },
        "target_axis": {
            "canonical_column": "spy",
            "display_name": "SPY (S&P 500 ETF)",
            "derivatives": tgt_der,
        },
        "notes": ("ECON-SD: only NHS derivatives and SPY derivatives are in scope. The NHS LEVEL "
                  "(nhs_nsa) is NSA and NON-STATIONARY; the STL level (nhs_sa) is also non-stationary — "
                  "both excluded from the signal set. Only stationary YoY/STL-MoM/z-score transforms are "
                  "used. regime_story: false (CP2 skipped)."),
    }
    with open(os.path.join(RESULTS_DIR, "signal_scope.json"), "w") as f:
        json.dump(scope, f, indent=2)

    # kpis.json
    kpis = [
        {"metric": "OOS Sharpe (winner)", "value": f"{winner_summary['oos_sharpe']:.2f}", "unit": "ratio", "delta": f"{tw['delta_sharpe']:+.2f} vs B&H"},
        {"metric": "OOS Sharpe (buy & hold)", "value": f"{winner_summary['bh_sharpe']:.2f}", "unit": "ratio", "delta": None},
        {"metric": "IS Sharpe (winner, selection objective)", "value": f"{float(winner['is_sharpe']):.2f}", "unit": "ratio", "delta": f"{float(winner['is_sharpe']) - sel['bh_is']['sharpe']:+.2f} vs B&H"},
        {"metric": "OOS Annual Return (winner)", "value": f"{winner_summary['oos_ann_return']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_ann_return']*100:+.1f}pp vs B&H"},
        {"metric": "OOS Max Drawdown (winner)", "value": f"{winner_summary['oos_max_drawdown']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_max_drawdown']*100:+.1f}pp vs B&H"},
        {"metric": "IS-valid strategy combos", "value": f"{n_valid}", "unit": "count", "delta": None},
        {"metric": "OOS window", "value": f"{split['oos_start']} → {split['oos_end']}", "unit": "dates", "delta": None},
    ]
    with open(os.path.join(RESULTS_DIR, "kpis.json"), "w") as f:
        json.dump(kpis, f, indent=2)

    # evidence_status.json
    _write_evidence_status(winner_summary, split, n_valid, is_window, t_oos, float(bh["oos_ann_vol"]))

    # design_note.md
    design = f"""# Design Note — {PAIR_ID} ({DATE_TAG})

## Category & method coverage (Rule C1, housing/activity)
All macro/activity mandatory methods produced. Deviations from the daily-pair spec, per Rule C1:
- Correlation horizons: pair is MONTHLY; horizons are 1m/3m/6m/12m forward returns, recorded as
  21/63/126/252 `horizon_days` equivalents in `correlations.csv`.
- Pre-whitened CCF run at monthly lags −20..+20 (not daily).
- Granger is Toda-Yamamoto (VAR in levels of the stationary YoY transform with d_max=1 augmentation).
- Transfer entropy: tercile-binned plug-in estimator, 500 permutations.
- Stationarity: Dana's tests (stationarity_tests_{STAT_TAG}.csv) reviewed and CONFIRMED, not re-run.
  NHS LEVEL (nhs_nsa) and STL LEVEL (nhs_sa) are NON-stationary and are EXCLUDED from the signal set.

## NSA / seasonality handling (defining feature)
HSN1FNSA is NOT seasonally adjusted. All signals are deseasonalised: `nhs_pct_yoy` (primary; 12-month
difference cancels the fixed seasonal), STL-based `nhs_sa_pct_mom`/`nhs_sa_3m_pct`, and a z-score on the
YoY series. Raw level and raw MoM are intentionally excluded as seasonal-dominated.

## Lead-lag verdict
- NHS->SPY TY-Granger significant lags: {fwd_sig_lags or 'NONE'}
- SPY->NHS TY-Granger significant lags: {rev_sig_lags or 'NONE'}
- Reverse-causality LP flag: {rev_flag}

## Data provenance
Source = FRED HSN1FNSA (1963-01 -> 2026-05) via Dana's data stage. The original input parquet is
gitignored and was rebuilt for the {DATE_TAG} run with the indicator transforms exactly as published in
signals_{PREV_TAG}.parquet and SPY re-pulled from Yahoo (monthly returns within 1.6e-6 of the {PREV_TAG}
file); see _pws/lead-lesandro/pkg13_hmm_port/nhs_frozen_input.py. A fresh live pull differs: FRED
revised 2026-04/05, and the STL seasonal adjustment behind nhs_sa_* is a full-sample (two-sided)
decomposition, so its values change when months are added.

## Regime models ({DATE_TAG})
HMM (2 states, NHS YoY, stress = higher-variance state) and Markov-switching (2 regimes, switching
variance, on NHS YoY itself; the old model put spy_ret in the likelihood) are fit on IS months only and
read with a forward filter (scripts/_regime_causal.py). The {PREV_TAG} winner used full-sample
forward-backward smoothed HMM probabilities; replay and causal comparison in
hmm_lookahead_audit_{DATE_TAG}.json.

## Selection ({DATE_TAG})
argmax IS Sharpe on the common IS window {is_window['start']}..{is_window['end']} ({is_window['n']} months;
start set by {', '.join(sel['driver'])}); eligibility before alignment, MIN_IS_N={MIN_IS_N}; validity uses
IS rows only. Winner {winner['signal']}/{winner['threshold']}/{winner['lookback']}/{winner['strategy']}/L{int(winner['lead_months'])}:
IS Sharpe {float(winner['is_sharpe']):.4f} (B&H {sel['bh_is']['sharpe']:.4f}); OOS Sharpe {float(winner['oos_sharpe']):.4f}
(B&H {float(bh['oos_sharpe']):.4f}), HAC t {t_oos:.2f}. {len(tdf)-1} combos, {n_valid} IS-valid,
Spearman(IS, OOS) {sel['spearman']:.3f}.

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal), not percent.
- Lead grid {LEADS}: the legacy ECON-LL1 grid [0,1,2,3,6,9,12] truncated at the registry floor L2
  (Census publishes month M near the end of M+1). position_t = rule(signal_(t-L));
  strategy_return_t = position_t * spy_ret_t.
- Both orientations (pro/counter) tested per the empirical direction prior.
- CP2 skipped — `regime_story: false` in signal_scope.json.
- Returns gross of costs; 5 bps sensitivity grid in tournament_validation_{DATE_TAG}/.

## Previous version: {PREV_TAG} (OOS-selected, L0 smoothed-HMM winner); superseded.
"""
    with open(os.path.join(RESULTS_DIR, "design_note.md"), "w") as f:
        f.write(design)

    # analyst_suggestions.json (ECON-AS)
    sugg = {"schema_version": "1.0.0", "pair_id": PAIR_ID, "rule": "ECON-AS",
            "suggestions": [
                {"signal_name": "New Home Sales / Building Permits ratio", "proposed_by": "evan",
                 "source": "FRED HSN1FNSA / PERMIT",
                 "observation": "Sales-to-permits ratio captures absorption vs pipeline; a falling ratio "
                                "(sales lagging permits) can flag demand softening before either level turns.",
                 "rationale": "Combines two housing leading indicators; the ratio may lead SPY more cleanly "
                              "than either series alone by netting out common rate-driven trends.",
                 "possible_use_case": "new pair / variant",
                 "caveats": "Both series NSA; ratio of two seasonal series needs joint deseasonalisation.",
                 "date_filed": "2026-07-03"},
                {"signal_name": "Mortgage-rate-conditioned NHS signal", "proposed_by": "evan",
                 "source": "FRED HSN1FNSA / MORTGAGE30US",
                 "observation": "NHS response to the cycle is rate-state dependent (2022-23 shock).",
                 "rationale": "Gating the NHS signal by the mortgage-rate regime may sharpen it.",
                 "possible_use_case": "signal enhancement",
                 "caveats": "Adds a second series; risk of overfitting the small OOS window.",
                 "date_filed": "2026-07-03"}],
            "last_updated_by": "evan", "last_updated_at": NOW_ISO}
    with open(os.path.join(RESULTS_DIR, "analyst_suggestions.json"), "w") as f:
        json.dump(sugg, f, indent=2)

    # timing
    timing = {"pair_id": PAIR_ID, "date": DATE_TAG,
              "pipeline_seconds": round(time.time() - t0, 1),
              "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
              "tournament_strategy_rows": int(len(tdf) - 1), "valid_strategies": n_valid,
              "oos_n_months": int(winner["oos_n"]),
              "oos_start": split["oos_start"], "oos_end": split["oos_end"]}
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump(timing, f, indent=2)

    # Evan handoff note
    handoff = f"""Handoff: Econ Evan -> Viz Vera / Research Ray / AppDev Ace

Pair: {PAIR_ID} (New Home Sales NSA -> SPY), Mode 2.

Winner: {tw['winner_label']}
  OOS Sharpe {winner_summary['oos_sharpe']} vs B&H {winner_summary['bh_sharpe']} | DD {winner_summary['oos_max_drawdown']} vs {winner_summary['bh_max_drawdown']} | ann ret {winner_summary['oos_ann_return']} vs {winner_summary['bh_ann_return']}
  Selected by IS Sharpe {float(winner['is_sharpe']):.4f} (B&H {sel['bh_is']['sharpe']:.4f}) on {is_window['start']}..{is_window['end']}
  Direction: {direction} | IS-valid combos {n_valid}/{len(tdf)-1} | tie step {resolved_at}
  Bootstrap p={winner_boot_p:.3f} | durability '{verdict}' | rolling-corr '{stab}' | break flagged {sb['flagged']} ({sb['break_date']})
  Superseded: {pp['combo']} OOS {float(prev['oos_sharpe']):.4f} (smoothed HMM); causal same rule L0 {pp['causal_same_rule_oos_sharpe']:.4f}, L{floor_l} {pp['causal_same_rule_at_floor_oos_sharpe']:.4f}

Lead-lag: {granger_verdict} Reverse-LP flag: {rev_flag}.

NSA note for Ray/Vera: this indicator is NOT seasonally adjusted; every signal is YoY or STL-deseasonalised.
Charts/narrative must NOT plot or describe the raw NSA level as a signal. The headline signal is
'{sig_code}' ({SIGNAL_COLS[winner['signal']]}).

Key artifacts under results/{PAIR_ID}/: winner_summary.json, strategy_returns_{DATE_TAG}.csv,
winner_trade_log.csv, tournament_results_{DATE_TAG}.csv, core_models_{DATE_TAG}/, regime_quartile_returns.csv,
subperiod_sharpe.csv, rolling_correlation_{PAIR_ID}.csv, kpis.json, signal_scope.json, evidence_status.json.

evidence_status = found_in_search (no final exam yet). Ray to set strategy_objective (suggested: {tw['suggested_strategy_objective']}).
"""
    pws = os.path.join(BASE_DIR, "_pws", "lead-lesandro", "nhs_spy")
    os.makedirs(pws, exist_ok=True)
    with open(os.path.join(pws, "evan_handoff.md"), "w") as f:
        f.write(handoff)

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE — HANDOFF NUMBERS (DPS-SCD1)")
    print("=" * 70)
    print(f"  Strategy combos: {len(tdf)-1} | IS-valid: {n_valid} | median IS Sharpe (valid): {median_sharpe:.3f}")
    print(f"  Winner: {tw['winner_label']}")
    print(f"  OOS Sharpe {winner_summary['oos_sharpe']} vs B&H {winner_summary['bh_sharpe']} | "
          f"DD {winner_summary['oos_max_drawdown']} vs {winner_summary['bh_max_drawdown']} | "
          f"ret {winner_summary['oos_ann_return']} vs {winner_summary['bh_ann_return']}")
    print(f"  Direction (winner): {direction} | suggested strategy_objective: {tw['suggested_strategy_objective']}")
    print(f"  Granger fwd lags: {fwd_sig_lags or 'NONE'} | rev lags: {rev_sig_lags or 'NONE'}")
    print(f"  Winner bootstrap p={winner_boot_p:.3f} | confidence={interp['confidence']}")
    return winner_summary, tw


if __name__ == "__main__":
    main()




