#!/usr/bin/env python3
"""
Full Econometrics Pipeline: NAHB/Wells Fargo Housing Market Index -> SPY
=========================================================================
Pair ID: wells_fargo_housing_spy (Mode 1, MONTHLY). Branch: feat260706_wells_fargo_housing_spy

Economic hypothesis (stated up front, per SOP):
  H0: Builder sentiment (HMI) does NOT Granger-cause / predict SPY forward returns.
  H1 (procyclical + LEADING prior, Dana/Leamer-2007 "housing IS the business cycle"):
      rising builder sentiment = housing expansion = risk-on; the HMI turned down
      ~2 years before the GFC equity peak. Direction AND lead/lag status are determined
      EMPIRICALLY (Toda-Yamamoto Granger / pre-whitened CCF / local projections) — the
      prior only seeds; it does NOT decide. If leading, the lead must be durable across
      adjacent leads (ECON-LT2 standard), not a lone spike.

Bounded-diffusion-index conventions (design deviations from unbounded-quantity pairs):
  * HMI is bounded 0-100, 50 = neutral. LEVEL and level z-score are FIRST-CLASS signals
    (distance from 50 = net builder optimism; mean-reverting). Point changes (diff_3m,
    diff_12m) are the natural momentum metric.
  * %-change transforms are LEVEL-DEPENDENT for a bounded index (8 -> 16 = "+100%").
    Included for standard-family consistency but every tournament row carries a
    `bounded_pct_risk` flag; a pct-transform winner is explicitly artifact-flagged.
  * Native regime axis = above/below 50 (`nahb_hmi_above50`); the level also gets a
    native T4_gap50 threshold at 50.0.
  * Integer-granularity values -> ties common on rank/percentile thresholds; strict `>`
    comparisons are deterministic, winner ties resolved by the ECON-T3 cascade.

BINDING Phase-0 constraints (Dana handoff):
  * 490 monthly obs 1985-01..2025-10; HMI x SPY overlap 1993-01..2025-10 (394 months —
    LONG by fleet standards; a proper OOS window is finally possible).
  * SA source: no seasonal-contamination constraint (all transforms admissible; the
    lead envelope and the clean envelope COINCIDE — both GH #13 files still emitted).
  * Lead grid floors at L1 (fleet convention). NAHB publishes mid-month FOR the current
    month (~zero pub lag), so an L0 variant would be defensible — noted in the manifest,
    grid kept L1..L12.
  * Static source ends 2025-10 (~9 months stale at run date) — evidence_status caveat.
  * 2008-09 single-digit trough and 2020 whipsaw are REAL — no winsorizing.

Category (Rule C1): sentiment (+ housing/leading candidate). Battery: correlations incl.
distance, pre-whitened CCF (+/-24 months — housing classically leads by up to ~2 years),
Toda-Yamamoto Granger both directions (lags 1..12), transfer entropy (tercile, 500 perms),
local projections fwd+rev (1/3/6/12M), quantile regression, HMM 2-state, Markov-switching,
quartile returns, era sub-period battery (pre-GFC / GFC / QE-era / post-COVID),
ECON-LA1 Lead Analysis + ECON-LT1 Lead Tournament (+ GH #13 winner-curve / clean-envelope).

Author: Econ Evan (Econometrics Agent). Date: 2026-07-06.
"""

import os
import sys
import json
import time
import hashlib
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
PAIR_ID = "wells_fargo_housing_spy"
INDICATOR_NAME = "NAHB/Wells Fargo Housing Market Index"
TARGET_SYMBOL = "SPY"
DATE_TAG = "20260706"
COST_BPS = 5  # equity ETF per target-class table
ANN = np.sqrt(12)
PERIODS_PER_YEAR = 12

BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_PATH = os.path.join(BASE_DIR, "data", "wells_fargo_housing_spy_monthly_latest.parquet")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
MODELS_DIR = os.path.join(RESULTS_DIR, f"core_models_{DATE_TAG}")
VALID_DIR = os.path.join(RESULTS_DIR, f"tournament_validation_{DATE_TAG}")
SCHEMA_DIR = os.path.join(BASE_DIR, "docs", "schemas")

for d in [RESULTS_DIR, MODELS_DIR, VALID_DIR]:
    os.makedirs(d, exist_ok=True)

STAGE_TIMES = {}
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# tournament signal KEY -> parquet column
SIGNAL_COLS = {
    "level": "nahb_hmi",
    "yoy": "nahb_hmi_pct_yoy",
    "mom": "nahb_hmi_pct_mom",
    "mom3m": "nahb_hmi_3m_pct",
    "mom6m": "nahb_hmi_6m_pct",
    "diff_3m": "nahb_hmi_diff_3m",
    "diff_12m": "nahb_hmi_diff_12m",
    "dev_trend": "nahb_hmi_dev_trend_pct",
    "level_zscore_60m": "nahb_hmi_zscore_60m",
    "diff12_zscore_60m": "nahb_hmi_diff12_zscore_60m",
    "accel": "nahb_hmi_accel_pct",
    "above50": "nahb_hmi_above50",
    # derived in stage_signals:
    "hmm_stress": "hmm_2state_prob_stress",
    "markov_regime": "markov_regime_2state",
}
# registry signal_code per key (ECON-DS3)
REGISTRY_CODE = {
    "level": "wells_fargo_housing_level", "yoy": "wells_fargo_housing_yoy",
    "mom": "wells_fargo_housing_mom", "mom3m": "wells_fargo_housing_mom3m",
    "mom6m": "wells_fargo_housing_mom6m", "diff_3m": "wells_fargo_housing_diff_3m",
    "diff_12m": "wells_fargo_housing_diff_12m", "dev_trend": "wells_fargo_housing_dev_trend",
    "level_zscore_60m": "wells_fargo_housing_level_zscore_60m",
    "diff12_zscore_60m": "wells_fargo_housing_diff12_zscore_60m",
    "accel": "wells_fargo_housing_accel", "above50": "wells_fargo_housing_above50",
    "hmm_stress": "hmm_stress", "markov_regime": "markov_regime",
}
# signals where 0 is an economically meaningful threshold (sign flips informative)
ZERO_CROSS = {"yoy", "mom", "mom3m", "mom6m", "diff_3m", "diff_12m", "accel",
              "dev_trend", "level_zscore_60m", "diff12_zscore_60m"}
# bounded-index %-transform artifact risk (Dana: 8->16 = "+100%")
BOUNDED_PCT_RISK = {"yoy", "mom", "mom3m", "mom6m", "accel"}

MAIN_SIG = "nahb_hmi"          # the level IS the sentiment read (bounded, first-class)
MOM_SIG = "nahb_hmi_diff_12m"  # level-independent annual momentum (era battery companion)
FWD_COLS = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]

SIG_ELIGIBLE_MIN = 120                              # min non-NaN months
LOOKBACKS = {"LB36": 36, "LB60": 60, "LB120": 120}  # 3/5/10yr — 394-month sample affords LB120
LEADS = list(range(1, 13))                          # L1..L12 months (fleet convention)
CORR_N_FLOOR = 60                                   # months

ERAS = [("pre_gfc_1993_2006", "1993-01-01", "2006-12-31"),
        ("gfc_bust_2007_2012", "2007-01-01", "2012-12-31"),
        ("qe_era_2013_2019", "2013-01-01", "2019-12-31"),
        ("post_covid_2020_2025", "2020-01-01", "2025-10-31")]


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
    m = {"file": os.path.basename(path), "pair_id": PAIR_ID,
         "produced_by": "scripts/pair_pipeline_wells_fargo_housing_spy.py",
         "generated_at": NOW_ISO,
         "frequency": "monthly",
         "annualization": "Sharpe = mean/std * sqrt(12); ann_return = mean*12 (monthly data)",
         "columns": columns, "assertions": assertions}
    if extra:
        m.update(extra)
    with open(os.path.splitext(path)[0] + "_manifest.json", "w") as f:
        json.dump(m, f, indent=2)


def ann_metrics(rets):
    """Monthly annualized metrics. Convention: Sharpe = mean/std*sqrt(12)."""
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return dict(sharpe=0.0, ann_return=0.0, ann_vol=0.0, max_dd=0.0,
                    sortino=0.0, calmar=0.0, win_rate=0.0, n=len(rets))
    sharpe = rets.mean() / rets.std() * ANN
    ann_ret = rets.mean() * PERIODS_PER_YEAR
    ann_vol = rets.std() * ANN
    cum = (1 + rets).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    neg = rets[rets < 0]
    sortino = ann_ret / (neg.std() * ANN) if len(neg) > 1 and neg.std() > 0 else 0.0
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    return dict(sharpe=sharpe, ann_return=ann_ret, ann_vol=ann_vol, max_dd=dd,
                sortino=sortino, calmar=calmar, win_rate=(rets > 0).mean(), n=len(rets))


# ===================================================================
# STAGE 1: LOAD + VERIFY (Defense 2 consumer checks)
# ===================================================================
@log_stage("1_load_verify")
def stage_load():
    df = pd.read_parquet(DATA_PATH)
    assert df.shape == (490, 23), f"unexpected shape {df.shape}"
    hmi = df["nahb_hmi"]
    assert hmi.between(0, 100).all(), "HMI outside 0-100 bounds"
    # Known-episode checks (Dana's interpretation_metadata):
    gfc_trough = hmi.loc["2008-06-30":"2009-06-30"].min()
    assert gfc_trough <= 9, f"GFC single-digit trough missing (record low 8 Jan-2009; got {gfc_trough})"
    assert hmi.loc["2020-04-30"] <= 31, "COVID crash to 30 (Apr-2020) missing"
    assert hmi.loc["2020-09-30":"2021-01-31"].max() >= 83, "COVID V-recovery to ~90 missing"
    assert hmi.loc["2022-12-31"] <= 33, "2022 rate-shock collapse (83->31) missing"
    assert df["spy_ret"].dropna().abs().max() < 0.30, "monthly SPY return magnitude implausible"
    assert df["spy_fwd_12m"].iloc[-12:].isna().all(), "forward-return leakage at tail"
    overlap = df.dropna(subset=["spy_ret"])
    print(f"  Loaded {df.shape}, {df.index.min().date()} -> {df.index.max().date()} (MONTHLY)")
    print(f"  HMI x SPY overlap: {len(overlap)} months {overlap.index.min().date()} -> {overlap.index.max().date()}")
    print("  Defense-2 episode checks: bounds, GFC trough (8), COVID whipsaw (30->90), 2022 collapse — PASS")
    return df


# ===================================================================
# STAGE 2: DERIVED REGIME SIGNALS (HMM + Markov-switching) + persistence
# ===================================================================
@log_stage("2_signals")
def stage_signals(df):
    import statsmodels.api as sm
    from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

    level = df["nahb_hmi"].dropna()

    # --- HMM 2-state on the HMI LEVEL (bounded, persistent -> optimism/pessimism split) ---
    # For a bounded mean-reverting sentiment index the level split IS the economically
    # meaningful regime: builder-pessimism regime (housing bust) vs optimism regime.
    # "stress" = LOW-sentiment regime.
    hmm_ok = False
    try:
        from hmmlearn.hmm import GaussianHMM
        X = level.values.reshape(-1, 1)
        hmm = GaussianHMM(n_components=2, covariance_type="full", n_iter=500, random_state=42)
        hmm.fit(X)
        means = [float(hmm.means_[i].ravel()[0]) for i in range(2)]
        stress_state = int(np.argmin(means))  # LOW sentiment = stress
        probs = hmm.predict_proba(X)
        prob_stress = pd.Series(probs[:, stress_state], index=level.index, name="hmm_2state_prob_stress")
        df["hmm_2state_prob_stress"] = prob_stress
        states = pd.Series(hmm.predict(X), index=level.index)
        occ = states.value_counts(normalize=True)
        if occ.min() < 0.10:
            print(f"  HMM degenerate (min regime occupancy {occ.min():.2f}) — hmm_stress EXCLUDED")
            df.drop(columns=["hmm_2state_prob_stress"], inplace=True)
        else:
            hmm_ok = True
            hmm_states = pd.DataFrame({"hmm_state": states, "prob_stress": prob_stress,
                                       "prob_calm": 1 - prob_stress})
            hmm_states.to_parquet(os.path.join(MODELS_DIR, "hmm_states.parquet"))
            spy = df["spy_ret"]
            summ = []
            for lbl, mask in [("builder_pessimism", states == stress_state),
                              ("builder_optimism", states != stress_state)]:
                idx = hmm_states.index[mask]
                rets = spy.reindex(idx).dropna()
                summ.append({"state_label": lbl,
                             "mean_return": round(rets.mean(), 6) if len(rets) else np.nan,
                             "vol": round(rets.std(), 6) if len(rets) else np.nan,
                             "duration_days": int(mask.sum()) * 21,
                             "frequency_pct": round(mask.mean() * 100, 2),
                             "mean_hmi_level": round(level.reindex(idx).mean(), 2)})
            pd.DataFrame(summ).to_csv(os.path.join(MODELS_DIR, "hmm_summary.csv"), index=False)
            gfc_p = prob_stress.loc["2008-01-31":"2009-12-31"].mean()
            boom_p = prob_stress.loc["2004-01-31":"2005-12-31"].mean()
            write_manifest(os.path.join(MODELS_DIR, "hmm_states.parquet"),
                           {"hmm_state": "integer state; stress = LOW-MEAN sentiment regime (builder pessimism / housing bust)",
                            "prob_stress": "P(builder-pessimism regime); higher = housing-bust conditions",
                            "prob_calm": "1 - prob_stress"},
                           [{"description": "probabilities in [0,1]", "check": "prob_stress between 0 and 1"},
                            {"description": "GFC housing bust = pessimism regime", "filter": "2008-01..2009-12",
                             "column": "prob_stress", "check": f"mean = {gfc_p:.2f} (expect > 0.8)"},
                            {"description": "2004-05 housing boom = optimism regime", "filter": "2004-01..2005-12",
                             "column": "prob_stress", "check": f"mean = {boom_p:.2f} (expect < 0.2)"}],
                           extra={"note": "HMM on bounded sentiment LEVEL: splits optimism vs pessimism regimes (level split, deliberate)"})
            print(f"  HMM 2-state converged; P(stress) GFC {gfc_p:.2f}, 2004-05 boom {boom_p:.2f}")
    except Exception as e:
        print(f"  HMM failed ({e}) — hmm_stress excluded from tournament")

    # --- Markov-switching regression: spy_ret ~ HMI level, 2 regimes ---
    ms_data = pd.concat([df["spy_ret"], level], axis=1).dropna()
    try:
        ms = MarkovRegression(ms_data["spy_ret"], k_regimes=2,
                              exog=sm.add_constant(ms_data["nahb_hmi"]),
                              switching_variance=True)
        ms_fit = ms.fit(maxiter=500, disp=False)
        smp = ms_fit.smoothed_marginal_probabilities
        sig2 = [ms_fit.params[f"sigma2[{i}]"] for i in range(2)]
        ms_stress = int(np.argmax(sig2))
        df["markov_regime_2state"] = smp[ms_stress].reindex(df.index)
        pd.DataFrame({"regime_stress_prob": smp[ms_stress], "regime_calm_prob": smp[1 - ms_stress]}
                     ).to_csv(os.path.join(MODELS_DIR, "markov_regime_probs_2state.csv"))
        pd.DataFrame({"parameter": ms_fit.params.index, "value": ms_fit.params.values,
                      "se": ms_fit.bse.values}).to_csv(
            os.path.join(MODELS_DIR, "markov_switching_2state.csv"), index=False)
        print("  Markov-switching 2-state converged")
    except Exception as e:
        print(f"  Markov-switching failed: {e} — signal excluded from tournament")

    sig_cols = [c for c in SIGNAL_COLS.values() if c in df.columns]
    sig_path = os.path.join(RESULTS_DIR, f"signals_{DATE_TAG}.parquet")
    df[sig_cols].to_parquet(sig_path)
    print(f"  Signals persisted -> {sig_path} ({len(sig_cols)} columns)")
    write_manifest(sig_path,
                   {c: f"tournament-eligible signal derived solely from the NAHB HMI ({c})" for c in sig_cols},
                   [{"description": "HMI bounded", "column": "nahb_hmi", "check": "0 <= value <= 100"},
                    {"description": "GFC record low", "filter": "2008-06..2009-06",
                     "column": "nahb_hmi", "check": "min <= 9"},
                    {"description": "COVID V-recovery", "filter": "2020-09..2021-01",
                     "column": "nahb_hmi", "check": "max >= 83"}],
                   extra={"bounded_pct_note": ("%-change columns (pct_yoy/pct_mom/3m_pct/6m_pct/accel_pct) are "
                                               "LEVEL-DEPENDENT for a bounded index — artifact risk flagged per "
                                               "tournament row (bounded_pct_risk)")})
    return df, hmm_ok


# ===================================================================
# STAGE 3: CORRELATION BATTERY (Rule C1/C2)
# ===================================================================
def _distance_corr(x, y):
    x = np.asarray(x, float)[:, None]
    y = np.asarray(y, float)[:, None]
    a = np.abs(x - x.T); b = np.abs(y - y.T)
    A = a - a.mean(0) - a.mean(1)[:, None] + a.mean()
    B = b - b.mean(0) - b.mean(1)[:, None] + b.mean()
    dcov2 = (A * B).mean(); dvx = (A * A).mean(); dvy = (B * B).mean()
    if dvx <= 0 or dvy <= 0:
        return 0.0
    return float(np.sqrt(max(dcov2, 0) / np.sqrt(dvx * dvy)))


@log_stage("3_correlations")
def stage_correlations(df):
    rows = []
    horizon_map = {"spy_fwd_1m": 21, "spy_fwd_3m": 63, "spy_fwd_6m": 126, "spy_fwd_12m": 252}
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwd, hd in horizon_map.items():
            v = df[[col, fwd]].dropna()
            if len(v) < CORR_N_FLOOR:
                continue
            x, y = v[col], v[fwd]
            for metric, fn in [("pearson", stats.pearsonr), ("spearman", stats.spearmanr),
                               ("kendall", stats.kendalltau)]:
                r, p = fn(x, y)
                rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": hd,
                             "metric": metric, "value": round(r, 4),
                             "p_value": round(p, 4), "n_obs": len(v)})
            rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": hd,
                         "metric": "distance", "value": round(_distance_corr(x, y), 4),
                         "p_value": np.nan, "n_obs": len(v)})
    cdf = pd.DataFrame(rows)
    path = os.path.join(MODELS_DIR, "correlations.csv")
    cdf.to_csv(path, index=False)
    write_manifest(path,
                   {"pair_name": "signal_key__forward-return-column (monthly: 1m/3m/6m/12m fwd)",
                    "horizon_days": "forward horizon in trading days (months*21)",
                    "metric": "pearson/spearman/kendall/distance", "value": "correlation coefficient",
                    "p_value": "two-sided p (NaN for distance corr); NOTE overlapping fwd windows inflate significance at 3m+",
                    "n_obs": "months"},
                   [{"description": "values bounded", "check": "abs(value) <= 1"},
                    {"description": "monthly horizons", "check": "horizon_days in {21,63,126,252}"},
                    {"description": "n floor", "check": f"min(n_obs) >= {CORR_N_FLOOR}"}])
    sig = cdf[(cdf.metric == "pearson") & (cdf.p_value < 0.05)]
    print(f"  Correlation battery: {len(cdf)} rows; {len(sig)} significant Pearson cells")
    if len(sig):
        b = sig.loc[sig.value.abs().idxmax()]
        print(f"  Strongest sig Pearson: {b.pair_name} r={b.value} p={b.p_value} (n={b.n_obs})")
    else:
        print("  No individually-significant Pearson cells.")
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

    main_sig = MAIN_SIG

    # --- 4.1 Pre-whitened CCF (monthly lags -24..+24 — housing can lead ~2yr) ---
    # Pre-whitening ESSENTIAL: the HMI level is highly persistent (ADF p=0.16); the raw
    # CCF would be dominated by autocorrelation artifacts.
    pair = df[[main_sig, "spy_ret"]].dropna()
    x = pair[main_sig]; y = pair["spy_ret"]
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
    for lag in range(-24, 25):
        if lag >= 0:
            a, b = xw.shift(lag), yw
        else:
            a, b = xw, yw.shift(-lag)
        v = pd.concat([a, b], axis=1).dropna()
        c = v.corr().iloc[0, 1] if len(v) > 60 else np.nan
        rows.append({"lag": lag, "ccf": round(c, 4) if pd.notna(c) else np.nan,
                     "lower_ci": round(-se, 4), "upper_ci": round(se, 4),
                     "significant": bool(abs(c) > se) if pd.notna(c) else False,
                     "arima_order": f"AR({best_p})", "n_obs": len(v)})
    ccf_df = pd.DataFrame(rows)
    ccf_df.to_csv(os.path.join(MODELS_DIR, "ccf_prewhitened.csv"), index=False)
    lead_sig = ccf_df[(ccf_df.lag > 0) & ccf_df.significant]
    lag_sig = ccf_df[(ccf_df.lag < 0) & ccf_df.significant]
    print(f"  [4.1] CCF (AR({best_p}) pre-whitening, n={n}, lags in MONTHS -24..+24): "
          f"sig lead(+) lags {list(lead_sig.lag)}, sig LAG(-) lags {list(lag_sig.lag)}")

    # --- 4.2 Toda-Yamamoto Granger (both directions), lags 1..12 months ---
    ty_rows, bylag_rows = [], []
    gdata = pair.rename(columns={main_sig: "ind", "spy_ret": "tgt"})
    d_max = 1  # HMI level ADF non-stationary / KPSS fail-to-reject (borderline) -> TY augmentation 1
    try:
        p_opt = max(int(VAR(gdata).select_order(maxlags=12).aic), 1)
    except Exception:
        p_opt = 1

    def ty_wald(caused, causing, lag):
        cols = {}
        for i in range(1, lag + d_max + 1):
            cols[f"{causing}_l{i}"] = gdata[causing].shift(i)
            cols[f"{caused}_l{i}"] = gdata[caused].shift(i)
        Xd = pd.DataFrame(cols).dropna()
        yv = gdata[caused].reindex(Xd.index)
        fit = sm.OLS(yv, sm.add_constant(Xd)).fit()
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
    print(f"  [4.2] Toda-Yamamoto (d_max={d_max}, VAR p* by AIC={p_opt}, lags in MONTHS 1..12):")
    print(f"        HMI->SPY significant at lags: {list(fwd_sig.lag)}")
    print(f"        SPY->HMI significant at lags: {list(rev_sig.lag)}")

    # --- 4.3 Transfer entropy (tercile-binned, permutation p) ---
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
        v = pd.concat([src, dst], axis=1).dropna()
        null = [transfer_entropy(pd.Series(rng.permutation(v.iloc[:, 0].values), index=v.index),
                                 v.iloc[:, 1]) for _ in range(n_perm)]
        pv = float((np.array(null) >= te).mean())
        te_rows.append({"direction": direction, "te_value": round(float(te), 5),
                        "permutation_p_value": round(pv, 4), "n_permutations": n_perm,
                        "bandwidth": np.nan, "bin_method": "tercile_qcut_integer_ties_dropped"})
    pd.DataFrame(te_rows).to_csv(os.path.join(MODELS_DIR, "transfer_entropy.csv"), index=False)
    print(f"  [4.3] Transfer entropy (tercile bins; integer HMI values -> qcut tie handling): "
          f"ind->tgt TE={te_rows[0]['te_value']} (p={te_rows[0]['permutation_p_value']}), "
          f"tgt->ind TE={te_rows[1]['te_value']} (p={te_rows[1]['permutation_p_value']})")

    # --- 4.4 Local projections (forward + REVERSE), monthly horizons 1/3/6/12 ---
    lp_rows = []
    for direction in ["fwd", "rev"]:
        for h in [1, 3, 6, 12]:
            if direction == "fwd":
                ycol = f"spy_fwd_{h}m"
                v = df[[main_sig, ycol]].dropna()
                xv, yv = v[main_sig], v[ycol]
            else:
                v = pd.concat([df["spy_ret"], df[main_sig].shift(-h)], axis=1).dropna()
                v.columns = ["x", "y"]; xv, yv = v["x"], v["y"]
            if len(v) < CORR_N_FLOOR:
                continue
            X = sm.add_constant(xv.values)
            nw = int(0.75 * len(v) ** (1 / 3)) + h
            fit = sm.OLS(yv.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw})
            ci = fit.conf_int()
            lp_rows.append({"horizon": h, "coef": round(fit.params[1], 6), "se": round(fit.bse[1], 6),
                            "ci_lower": round(ci[1][0], 6), "ci_upper": round(ci[1][1], 6),
                            "p_value": round(fit.pvalues[1], 4), "direction": direction})
    lp_df = pd.DataFrame(lp_rows)
    lp_df.to_csv(os.path.join(MODELS_DIR, "local_projections.csv"), index=False)
    fwd = lp_df[lp_df.direction == "fwd"]; rev = lp_df[lp_df.direction == "rev"]
    fwd_lp_flag = bool((fwd.p_value < 0.05).any())
    rev_flag = bool((rev.p_value < 0.05).any())
    print(f"  [4.4] LP (horizons in MONTHS) fwd (HMI->SPY) sig: {list(fwd.loc[fwd.p_value<0.05,'horizon'])}; "
          f"reverse (SPY->HMI) sig: {list(rev.loc[rev.p_value<0.05,'horizon'])} -> rev flag {rev_flag}")

    # --- 4.5 Quantile regression (1m fwd) ---
    qr_rows = []
    v = df[[main_sig, "spy_fwd_1m"]].dropna().rename(columns={main_sig: "sig", "spy_fwd_1m": "fwd"})
    for tau in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]:
        try:
            qf = smf.quantreg("fwd ~ sig", v).fit(q=tau)
            ci = qf.conf_int()
            qr_rows.append({"tau": tau, "coef": round(qf.params["sig"], 6), "se": round(qf.bse["sig"], 6),
                            "p_value": round(qf.pvalues["sig"], 4),
                            "ci_lower": round(ci.loc["sig", 0], 6), "ci_upper": round(ci.loc["sig", 1], 6)})
        except Exception as e:
            print(f"    QR tau={tau} failed: {e}")
    pd.DataFrame(qr_rows).to_csv(os.path.join(MODELS_DIR, "quantile_regression.csv"), index=False)
    print(f"  [4.5] Quantile regression: {len(qr_rows)} taus (394-month sample; tails adequately populated)")

    # --- 4.6 Predictive regressions (all signals x horizons, HAC) ---
    reg_rows = []
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        for fwdc in FWD_COLS:
            v = df[[col, fwdc]].dropna()
            if len(v) < CORR_N_FLOOR:
                continue
            h = int(fwdc.split("_")[-1].rstrip("m"))
            fit = sm.OLS(v[fwdc].values, sm.add_constant(v[col].values)).fit(
                cov_type="HAC", cov_kwds={"maxlags": h + 1})
            reg_rows.append({"signal": code, "horizon": fwdc, "coef": round(fit.params[1], 6),
                             "se": round(fit.bse[1], 6), "t_stat": round(fit.tvalues[1], 3),
                             "p_value": round(fit.pvalues[1], 4), "r_squared": round(fit.rsquared, 4),
                             "n": int(fit.nobs)})
    reg_df = pd.DataFrame(reg_rows)
    reg_df.to_csv(os.path.join(MODELS_DIR, "predictive_regressions.csv"), index=False)
    print(f"  [4.6] Predictive regressions: {len(reg_df)} cells (HAC SEs; overlapping windows at 3m+)")

    # --- 4.7 Diagnostics on baseline spec ---
    diag = []
    v = df[[main_sig, "spy_fwd_1m"]].dropna()
    X = sm.add_constant(v[main_sig].values)
    base = sm.OLS(v["spy_fwd_1m"].values, X).fit()
    resid = base.resid
    jb, jbp = stats.jarque_bera(resid)
    diag.append({"test": "Jarque-Bera", "statistic": round(jb, 3), "p_value": round(jbp, 4),
                 "interpretation": "Normal residuals" if jbp > 0.05 else "Non-normal — robust/HAC inference used"})
    from statsmodels.stats.diagnostic import het_breuschpagan, acorr_breusch_godfrey, linear_reset
    bp, bpp, _, _ = het_breuschpagan(resid, X)
    diag.append({"test": "Breusch-Pagan", "statistic": round(bp, 3), "p_value": round(bpp, 4),
                 "interpretation": "Homoskedastic" if bpp > 0.05 else "Heteroskedastic — HAC SEs used"})
    bg, bgp, _, _ = acorr_breusch_godfrey(base, nlags=12)
    diag.append({"test": "Breusch-Godfrey", "statistic": round(bg, 3), "p_value": round(bgp, 4),
                 "interpretation": "No serial corr" if bgp > 0.05 else "Serial correlation — HAC SEs used"})
    try:
        rs = linear_reset(base, power=3, use_f=True)
        diag.append({"test": "RESET", "statistic": round(float(rs.fvalue), 3), "p_value": round(float(rs.pvalue), 4),
                     "interpretation": "Linear form adequate" if rs.pvalue > 0.05 else "Possible nonlinearity — see quantile regression"})
    except Exception:
        pass
    pd.DataFrame(diag).to_csv(os.path.join(MODELS_DIR, "diagnostics_summary.csv"), index=False)
    print(f"  [4.7] Diagnostics: {len(diag)} tests")

    return ccf_df, ty_df, lp_df, reg_df, rev_flag, fwd_lp_flag


# ===================================================================
# STAGE 4b: LEAD ANALYSIS (ECON-LA1)
# ===================================================================
@log_stage("4b_lead_analysis")
def stage_lead_analysis(df):
    """ECON-LA1: per-transform Pearson r vs 1-MONTH-fwd return at leads L0..L12 months.
    L0 is diagnostic-only here BY CONVENTION not necessity: NAHB releases mid-month FOR
    the current month (~zero pub lag), so L0 would be defensible — grid kept L1..L12
    per fleet convention (Dana Phase-0)."""
    fwd1 = df["spy_fwd_1m"]
    transforms = [c for k, c in SIGNAL_COLS.items() if c in df.columns and not c.startswith(("hmm", "markov"))]
    rows = []
    for col in transforms:
        row = {"transform": col}
        best_lead, best_abs, best_r = None, -1, None
        for L in range(0, 13):
            v = pd.concat([df[col].shift(L), fwd1], axis=1).dropna()
            if len(v) < 60:
                row[f"L{L}"] = ""
                continue
            r, p = stats.pearsonr(v.iloc[:, 0], v.iloc[:, 1])
            star = "**" if p < 0.01 else ("*" if p < 0.05 else "")
            row[f"L{L}"] = f"{r:+.3f}{star}"
            if abs(r) > best_abs:
                best_abs, best_lead, best_r = abs(r), L, r
        row["best_lead"] = f"L{best_lead}" if best_lead is not None else ""
        row["best_r"] = f"{best_r:+.3f}" if best_r is not None else ""
        rows.append(row)
    lc = pd.DataFrame(rows)
    lc_path = os.path.join(RESULTS_DIR, f"lead_correlation_{DATE_TAG}.csv")
    lc.to_csv(lc_path, index=False)
    print(f"  [ECON-LA1] lead_correlation -> {lc_path} (leads in MONTHS; L0 diagnostic-only by fleet convention)")
    return lc, lc_path


# ===================================================================
# STAGE 5: REGIME QUARTILE RETURNS + ERA SUB-PERIOD BATTERY
# ===================================================================
@log_stage("5_regime_quartiles")
def stage_quartiles(df):
    v = df[["nahb_hmi", "spy_ret"]].dropna()
    # Integer-granularity series: qcut with duplicates='drop' would merge bins; rank-based
    # qcut on ties is deterministic but flag it. 4 quartiles on 394 distinct months.
    q = pd.qcut(v["nahb_hmi"].rank(method="first"), 4, labels=["Q1", "Q2", "Q3", "Q4"])
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
                   {"quartile": "HMI level quartile (Q1 = deepest builder pessimism)", "n_months": "obs (months)",
                    "ann_return": "annualized SPY return in quartile (ratio; monthly mean x12)",
                    "ann_vol": "annualized vol (ratio; monthly std x sqrt(12))",
                    "sharpe": "monthly Sharpe, sqrt(12) annualization",
                    "max_drawdown": "max DD within quartile months (negative ratio)"},
                   [{"description": "4 quartiles", "check": "len == 4"},
                    {"description": "returns plausible", "check": "abs(ann_return) < 0.6"},
                    {"description": "integer ties broken by rank(method=first) — deterministic", "check": "informational"},
                    {"description": "concurrent (NOT lagged) relationship — descriptive only", "check": "informational"}])

    # --- Era sub-period battery (structural-stability evidence, task mandate) ---
    era_rows = []
    for sig_name, col in [("level", MAIN_SIG), ("diff_12m", MOM_SIG)]:
        for era, s, e in ERAS:
            v = df.loc[s:e, [col, "spy_fwd_1m"]].dropna()
            if len(v) < 24:
                continue
            r, p = stats.pearsonr(v[col], v["spy_fwd_1m"])
            era_rows.append({"signal": sig_name, "era": era, "start": s[:7], "end": e[:7],
                             "n_months": len(v), "pearson_r": round(r, 4), "p_value": round(p, 4)})
    era_df = pd.DataFrame(era_rows)
    era_path = os.path.join(MODELS_DIR, "era_correlations.csv")
    era_df.to_csv(era_path, index=False)
    write_manifest(era_path,
                   {"signal": "level (nahb_hmi) or diff_12m (nahb_hmi_diff_12m)",
                    "era": "sub-period label", "n_months": "obs",
                    "pearson_r": "Pearson r of era-window signal vs 1M-fwd SPY return",
                    "p_value": "two-sided"},
                   [{"description": "4 eras x 2 signals", "check": "len == 8 (or fewer if era n<24)"},
                    {"description": "era boundaries: pre-GFC/GFC-bust/QE-era/post-COVID", "check": "informational"}])
    print("  Era battery:")
    print(era_df.to_string(index=False))
    return qdf, era_df


# ===================================================================
# STAGE 6: TOURNAMENT ENGINE (monthly, full grid L1..L12)
# ===================================================================
def run_lead_grid(df, split, leads):
    """Tournament evaluation over given leads (MONTHS). Grid mirrors the cass/monthly
    template: T1 IS-percentiles {25,50,75}, T2 rolling percentiles {25,75}, T3 rolling
    z-scores {±1.0, ±1.5} x {LB36,LB60,LB120}, T4_zero on sign-meaningful signals,
    plus bounded-index natives: T4_gap50 (level > 50) and T4_above50 (binary flag).
    Strategies P1 long/cash, P2 signal-strength, P3 long/short, each pro/counter.
    Returns strategy rows (NO benchmark)."""
    work = df.dropna(subset=["spy_ret"]).copy()
    is_end = split["in_sample_end"]; oos_start = split["oos_start"]; oos_end = split["oos_end"]
    is_mask = work.index <= is_end
    oos_mask = (work.index >= oos_start) & (work.index <= oos_end)
    spy_ret = work["spy_ret"]
    strategies = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]
    results = []
    for code, col in SIGNAL_COLS.items():
        if col not in work.columns or work[col].notna().sum() < SIG_ELIGIBLE_MIN:
            continue
        base_sig = work[col]
        for lead in leads:
            sig = base_sig.shift(lead)
            thr_static = {}
            if code == "above50":
                # binary flag: the only sensible threshold is the regime line itself
                thr_static[("T4_above50", "LB_NA")] = 0.5
            else:
                is_sig = sig[is_mask].dropna()
                if len(is_sig) > 36:
                    for pct in [25, 50, 75]:
                        thr_static[(f"T1_fixed_p{pct}", "LB_NA")] = is_sig.quantile(pct / 100)
                if code in ZERO_CROSS:
                    thr_static[("T4_zero", "LB_NA")] = 0.0
                if code == "level":
                    thr_static[("T4_gap50", "LB_NA")] = 50.0  # native neutral line
            thr_roll = {}
            if code != "above50":
                for lb_name, lb in LOOKBACKS.items():
                    minp = max(int(lb * 0.6), 12)
                    roll = sig.rolling(lb, min_periods=minp)
                    for pct in [25, 75]:
                        thr_roll[(f"T2_roll_p{pct}", lb_name)] = roll.quantile(pct / 100)
                    rm, rs = roll.mean(), roll.std()
                    for k in [1.0, 1.5]:
                        thr_roll[(f"T3_zscore_{k}", lb_name)] = rm + k * rs
                        thr_roll[(f"T3_zscore_neg_{k}", lb_name)] = rm - k * rs
            for (thr_name, lb_name), thr in {**thr_static, **thr_roll}.items():
                above = sig < thr if "neg_" in thr_name else sig > thr
                for strat in strategies:
                    for orientation in ["pro", "counter"]:
                        pos_bool = ~above if orientation == "counter" else above
                        if strat == "P1_long_cash":
                            position = pos_bool.astype(float)
                        elif strat == "P2_signal_strength":
                            if lb_name == "LB_NA" or code == "above50":
                                continue
                            lb = LOOKBACKS[lb_name]
                            roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 12))
                            rng = (roll.max() - roll.min()).replace(0, np.nan)
                            raw = ((sig - roll.min()) / rng).clip(0, 1)
                            position = 1 - raw if orientation == "counter" else raw
                        else:
                            position = pos_bool.astype(float) * 2 - 1
                        strat_ret = position * spy_ret
                        is_r, oos_r = strat_ret[is_mask].dropna(), strat_ret[oos_mask].dropna()
                        if len(is_r) < 120 or len(oos_r) < 36:
                            continue
                        m_is, m = ann_metrics(is_r), ann_metrics(oos_r)
                        pos_oos = position[oos_mask]
                        n_trades = int((pos_oos.diff().abs() > 1e-9).sum())
                        years = len(pos_oos.dropna()) / 12
                        turnover = n_trades / years if years > 0 else 999
                        valid = bool(m["sharpe"] > 0.3 and turnover < 24 and len(oos_r) >= 36)
                        results.append({
                            "signal": code, "threshold": thr_name, "strategy": f"{strat}_{orientation}",
                            "lead_months": lead, "lookback": lb_name,
                            "is_sharpe": round(m_is["sharpe"], 4), "oos_sharpe": round(m["sharpe"], 4),
                            "oos_sortino": round(m["sortino"], 4), "oos_calmar": round(m["calmar"], 4),
                            "oos_ann_return": round(m["ann_return"], 4), "oos_ann_vol": round(m["ann_vol"], 4),
                            "max_drawdown": round(m["max_dd"], 4), "win_rate": round(m["win_rate"], 4),
                            "n_trades": n_trades, "annual_turnover": round(turnover, 2),
                            "oos_n": len(oos_r), "valid": valid,
                            "bounded_pct_risk": bool(code in BOUNDED_PCT_RISK)})
    return pd.DataFrame(results)


@log_stage("6_tournament")
def stage_tournament(df):
    work = df.dropna(subset=["spy_ret"]).copy()
    n_months = len(work)
    # ECON-OOS2 policy v1_max36_25pct_cap120
    oos_n = int(min(max(36, round(n_months * 0.25)), 120))
    oos_start = work.index[-oos_n]
    is_end = work.index[-(oos_n + 1)]
    oos_end = work.index[-1]
    print(f"  Sample (SPY-bound): {n_months} months {work.index[0].date()} -> {oos_end.date()}")
    print(f"  OOS (v1_max36_25pct_cap120): {oos_n} months ({oos_n/12:.1f}yr), "
          f"{oos_start.date()} -> {oos_end.date()} — a PROPER >5yr OOS window at last")
    split = {
        "owner": "evan", "split_policy_id": "v1_max36_25pct_cap120",
        "in_sample_end": is_end.strftime("%Y-%m-%d"), "oos_start": oos_start.strftime("%Y-%m-%d"),
        "oos_end": oos_end.strftime("%Y-%m-%d"), "sample_size_months": n_months,
        "justification": (
            f"Policy v1_max36_25pct_cap120 on the HMI x SPY overlap ({n_months} months, "
            f"1993-02..2025-10 SPY-return-bound; HMI history extends to 1985-01 but SPY inception caps the pair). "
            f"span = min(max(36, round({n_months}*0.25)), 120) = {oos_n} months (~{oos_n/12:.1f} years) — "
            f"ABOVE the 5-year reliability floor, a LONG OOS window by fleet standards. "
            f"OOS {oos_start.date()}..{oos_end.date()} spans late-cycle 2018 vol, COVID, the 2021 housing boom, "
            f"the 2022 rate shock (HMI 83->31) and the 2023-25 high-rate regime. "
            f"IS = {n_months - oos_n} months covering the 1990s expansion, dot-com bust, the classic "
            f"2005-09 housing-leads-the-cycle episode, and the QE era. No structural-break exclusion applied; "
            f"break diagnostics reported separately (structural_break json + era_correlations.csv)."),
    }
    with open(os.path.join(RESULTS_DIR, "oos_split_record.json"), "w") as f:
        json.dump(split, f, indent=2)

    tstrat = run_lead_grid(df, split, LEADS)

    # Benchmark row (ECON-T4: valid=False, signal=="BENCHMARK")
    spy_ret = work["spy_ret"]
    is_mask = work.index <= is_end
    oos_mask = (work.index >= oos_start) & (work.index <= oos_end)
    mb, mbi = ann_metrics(spy_ret[oos_mask].dropna()), ann_metrics(spy_ret[is_mask].dropna())
    bench = {"signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "P0_buy_and_hold",
             "lead_months": 0, "lookback": "LB_NA", "is_sharpe": round(mbi["sharpe"], 4),
             "oos_sharpe": round(mb["sharpe"], 4), "oos_sortino": round(mb["sortino"], 4),
             "oos_calmar": round(mb["calmar"], 4), "oos_ann_return": round(mb["ann_return"], 4),
             "oos_ann_vol": round(mb["ann_vol"], 4), "max_drawdown": round(mb["max_dd"], 4),
             "win_rate": round(mb["win_rate"], 4), "n_trades": 0, "annual_turnover": 0.0,
             "oos_n": int(oos_mask.sum()), "valid": False, "bounded_pct_risk": False}
    tdf = pd.concat([tstrat, pd.DataFrame([bench])], ignore_index=True)
    assert (tdf["signal"] == "BENCHMARK").sum() == 1, "exactly one benchmark row required (ECON-T4)"
    tpath = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _tournament_io import write_tournament
    write_tournament(tdf, tpath)

    strat_pop = tdf[tdf.signal != "BENCHMARK"]
    n_valid = int(strat_pop["valid"].sum())
    print(f"  Combos evaluated: {len(strat_pop)} strategies + 1 benchmark; valid: {n_valid}")
    print(f"  B&H OOS Sharpe {mb['sharpe']:.3f}, maxDD {mb['max_dd']:.3f}, ann ret {mb['ann_return']:.3f}")

    manifest = {
        "file": os.path.basename(tpath), "pair_id": PAIR_ID,
        "frequency": "MONTHLY",
        "annualization": "Sharpe = mean/std*sqrt(12); ann_return = mean*12; ann_vol = std*sqrt(12)",
        "grid": {"signals": [k for k, v in SIGNAL_COLS.items() if v in work.columns and work[v].notna().sum() >= SIG_ELIGIBLE_MIN],
                 "thresholds": ("T1_fixed_p{25,50,75}, T2_roll_p{25,75}, T3_zscore_{±1.0,±1.5}, "
                                "T4_zero (sign-meaningful), T4_gap50 (level native neutral line), "
                                "T4_above50 (binary regime flag, sole threshold for above50)"),
                 "strategies": ["P1_long_cash_{pro,counter}", "P2_signal_strength_{pro,counter}", "P3_long_short_{pro,counter}"],
                 "leads_months": LEADS, "lookbacks": list(LOOKBACKS.keys()) + ["LB_NA"]},
        "units": "oos_ann_return / oos_ann_vol / max_drawdown are RATIOS (decimal), not percent",
        "lead_column_note": ("lead_months per ECON-LL1. Grid floors at L1 by fleet convention; NAHB publishes "
                             "mid-month FOR the current month (~zero pub lag), so an L0 variant would be "
                             "defensible — deliberately NOT scanned (Dana Phase-0 recommendation)"),
        "total_strategy_rows": len(strat_pop), "valid_strategy_rows": n_valid,
        "sampling": "exhaustive over the full tradable lead grid L1..L12 months (no coarse subset; GH #13 native)",
        "benchmark_row": "signal==BENCHMARK, valid=False per ECON-T4",
        "execution_lag": "position_t = rule(signal_{t-lead}), lead >= 1 month",
        "bounded_index_flag": ("HMI is a bounded 0-100 diffusion index: %-change transforms "
                               "(yoy/mom/mom3m/mom6m/accel) are level-dependent (8->16 = '+100%') — "
                               "per-row bounded_pct_risk column; a pct-transform winner must be artifact-flagged"),
        "tie_note": ("integer-granularity HMI values -> ties common on percentile thresholds; strict '>' "
                     "comparisons are deterministic; winner ties resolved by ECON-T3 cascade"),
        "seasonality": "SA source (NAHB adjusts) — all transform families admissible; envelope == clean envelope",
        "cost_note": "returns are gross of costs; cost sensitivity in tournament_validation",
        "assertions": ["top strategy oos_sharpe > bottom strategy oos_sharpe", "all oos_sharpe finite",
                       "exactly one BENCHMARK row, valid=False"],
        "generated_at": NOW_ISO,
    }
    with open(os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return tdf, split, tpath


# ===================================================================
# STAGE 6b: LEAD TOURNAMENT (ECON-LT1) + GH #13 winner-curve / envelope
# ===================================================================
@log_stage("6b_lead_tournament")
def stage_lead_tournament(df, split, tdf, winner):
    rows = []
    for L in LEADS:
        cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid & (tdf.lead_months == L)]
        if len(cand) == 0:
            rows.append({"lead_months": L, "n_valid": 0, "best_oos_sharpe": np.nan,
                         "median_oos_sharpe": np.nan, "p25_oos_sharpe": np.nan, "p75_oos_sharpe": np.nan,
                         "best_signal": "", "best_threshold": "", "best_strategy": "", "best_max_dd": np.nan})
            continue
        top = cand.loc[cand.oos_sharpe.idxmax()]
        rows.append({"lead_months": L, "n_valid": int(len(cand)),
                     "best_oos_sharpe": round(float(top.oos_sharpe), 4),
                     "median_oos_sharpe": round(float(cand.oos_sharpe.median()), 4),
                     "p25_oos_sharpe": round(float(cand.oos_sharpe.quantile(0.25)), 4),
                     "p75_oos_sharpe": round(float(cand.oos_sharpe.quantile(0.75)), 4),
                     "best_signal": top.signal, "best_threshold": top.threshold,
                     "best_strategy": top.strategy, "best_max_dd": round(float(top.max_drawdown), 4)})
    lt = pd.DataFrame(rows)
    lt_path = os.path.join(RESULTS_DIR, f"lead_tournament_{DATE_TAG}.csv")
    lt.to_csv(lt_path, index=False)
    valid_leads = lt[lt.n_valid > 0]
    if len(valid_leads):
        star_row = valid_leads.loc[valid_leads.best_oos_sharpe.idxmax()]
        L_star = int(star_row.lead_months)
        best_at_grid = float(star_row.best_oos_sharpe)
    else:
        L_star, best_at_grid = -1, np.nan
    gate = "CHARTS-ONLY (full L1..L12 grid scanned natively)"
    print(f"  [ECON-LT1] lead_tournament -> {lt_path}; L*={L_star} best OOS Sharpe {best_at_grid} -> {gate}")

    # --- GH #13 artifact 1: published winner's OWN Sharpe at each lead ---
    wc_rows = []
    for L in LEADS:
        match = tdf[(tdf.signal == winner["signal"]) & (tdf.threshold == winner["threshold"]) &
                    (tdf.strategy == winner["strategy"]) & (tdf.lookback == winner["lookback"]) &
                    (tdf.lead_months == L)]
        wc_rows.append({"lead_months": L,
                        "oos_sharpe": round(float(match.iloc[0].oos_sharpe), 4) if len(match) else np.nan,
                        "is_published_winner": bool(L == int(winner["lead_months"]))})
    wc = pd.DataFrame(wc_rows)
    wc_path = os.path.join(RESULTS_DIR, f"lead_winner_curve_{DATE_TAG}.csv")
    wc.to_csv(wc_path, index=False)

    # --- GH #13 artifact 2: clean envelope. SA source -> ALL signals admissible,
    # so the envelope and the "clean" envelope COINCIDE by construction (stated). ---
    env_rows = []
    for L in LEADS:
        cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid & (tdf.lead_months == L)]
        if len(cand) == 0:
            env_rows.append({"lead_months": L, "best_oos_sharpe": np.nan, "best_signal": "",
                             "best_is_clean": True, "best_clean_oos_sharpe": np.nan, "best_clean_signal": ""})
            continue
        top = cand.loc[cand.oos_sharpe.idxmax()]
        env_rows.append({"lead_months": L, "best_oos_sharpe": round(float(top.oos_sharpe), 4),
                         "best_signal": top.signal, "best_is_clean": True,
                         "best_clean_oos_sharpe": round(float(top.oos_sharpe), 4),
                         "best_clean_signal": top.signal})
    env = pd.DataFrame(env_rows)
    env_path = os.path.join(RESULTS_DIR, f"lead_clean_envelope_{DATE_TAG}.csv")
    env.to_csv(env_path, index=False)
    print(f"  [GH #13] lead_winner_curve -> {wc_path}; lead_clean_envelope -> {env_path} "
          f"(SA source: envelope == clean envelope by construction)")
    peak_lead = int(wc.loc[wc.oos_sharpe.idxmax(), "lead_months"]) if wc.oos_sharpe.notna().any() else -1

    # ECON-LT2-style durability read on the winner's own curve (honesty evidence):
    wl = int(winner["lead_months"])
    neigh = wc[wc.lead_months.isin([wl - 1, wl + 1])]["oos_sharpe"].dropna()
    w_sharpe = float(winner["oos_sharpe"])
    durable_leads = bool(len(neigh) and (neigh > w_sharpe - 0.15).any())
    return lt, lt_path, L_star, best_at_grid, gate, wc, peak_lead, durable_leads


# ===================================================================
# STAGE 7: WINNER SELECTION (ECON-T3 cascade) + artifacts
# ===================================================================
def select_winner(tdf):
    """Winner over the valid strategy population (ECON-T4 excludes BENCHMARK).
    SA source -> no seasonal-cleanliness restriction; objective = plain max_oos_sharpe."""
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid].copy()
    if len(cand) == 0:
        return None, None, None, cand
    cascade = [("oos_sharpe", False), ("oos_ann_return", False),
               ("abs_dd", True), ("n_trades", False), ("signal", True)]
    cand["abs_dd"] = cand["max_drawdown"].abs()
    pool = cand; resolved_at = 1; tie_pool_step1 = None
    for i, (colname, ascending) in enumerate(cascade, start=1):
        best_val = pool[colname].min() if ascending else pool[colname].max()
        nxt = pool[pool[colname] == best_val]
        if i == 1:
            tie_pool_step1 = nxt.copy()
        if len(nxt) == 1:
            resolved_at = i; pool = nxt; break
        pool = nxt; resolved_at = i
    return pool.iloc[0], resolved_at, tie_pool_step1, cand


def derive_winner_series(df, winner, split):
    work = df.dropna(subset=["spy_ret"]).copy()
    is_mask = work.index <= split["in_sample_end"]
    sig = work[SIGNAL_COLS[winner["signal"]]].shift(int(winner["lead_months"]))
    thr_name, lb_name = winner["threshold"], winner["lookback"]
    if thr_name.startswith("T1_fixed_p"):
        thr = sig[is_mask].dropna().quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name == "T4_zero":
        thr = 0.0
    elif thr_name == "T4_gap50":
        thr = 50.0
    elif thr_name == "T4_above50":
        thr = 0.5
    elif thr_name.startswith("T2_roll_p"):
        lb = LOOKBACKS[lb_name]
        thr = sig.rolling(lb, min_periods=max(int(lb * 0.6), 12)).quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name.startswith("T3_zscore"):
        lb = LOOKBACKS[lb_name]; roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 12))
        k = float(thr_name.split("_")[-1])
        thr = roll.mean() - k * roll.std() if "neg_" in thr_name else roll.mean() + k * roll.std()
    else:
        raise ValueError(thr_name)
    above = sig < thr if "neg_" in thr_name else sig > thr
    strat, orientation = winner["strategy"].rsplit("_", 1)
    if strat == "P2_signal_strength":
        lb = LOOKBACKS[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 12))
        rng = (roll.max() - roll.min()).replace(0, np.nan)
        raw = ((sig - roll.min()) / rng).clip(0, 1)
        position = 1 - raw if orientation == "counter" else raw
    else:
        pos_bool = ~above if orientation == "counter" else above
        if strat == "P1_long_cash":
            position = pos_bool.astype(float)
        else:
            position = pos_bool.astype(float) * 2 - 1
    return position, work["spy_ret"], sig, thr


@log_stage("7_winner_artifacts")
def stage_winner(df, tdf, split, tpath):
    winner, resolved_at, tie_pool, cand = select_winner(tdf)
    if winner is None:
        raise RuntimeError("no valid strategies — null result; escalate to Lead")
    n_valid = len(cand)
    median_sharpe = float(cand["oos_sharpe"].median())
    n_tied = int((cand["oos_sharpe"] == winner["oos_sharpe"]).sum())
    print(f"  Valid strategies: {n_valid}; winner: {winner['signal']}/{winner['threshold']}/"
          f"{winner['strategy']}/L{winner['lead_months']}/{winner['lookback']}")
    print(f"  OOS Sharpe {winner['oos_sharpe']} | ties at step1: {n_tied} | resolved at step {resolved_at} "
          f"| bounded_pct_risk={winner['bounded_pct_risk']}")

    if resolved_at > 1:
        lines = [f"# Tournament Tie Note — {PAIR_ID} ({DATE_TAG})", "",
                 f"Winner resolved at cascade step {resolved_at} (ECON-T3).", "",
                 "Context: the HMI is an integer-granularity bounded index — identical-Sharpe ties on ",
                 "percentile/rank thresholds are expected and the deterministic cascade is the designed resolver.", "",
                 "## Candidates tied at step 1 (oos_sharpe)", "",
                 tie_pool[["signal", "threshold", "strategy", "lead_months", "lookback",
                           "oos_sharpe", "oos_ann_return", "max_drawdown", "n_trades"]].to_markdown(index=False),
                 "", "Interpretation: candidates near-equivalent on the primary objective; the selected "
                 "winner is preferred on the documented tie-break dimension."]
        with open(os.path.join(RESULTS_DIR, "tournament_tie_note.md"), "w") as f:
            f.write("\n".join(lines))
        print("  Tie note written (cascade fired beyond step 1)")

    position, spy_ret, sig_lagged, thr = derive_winner_series(df, winner, split)
    oos_mask = (spy_ret.index >= split["oos_start"]) & (spy_ret.index <= split["oos_end"])
    strat_ret = position * spy_ret
    m = ann_metrics(strat_ret[oos_mask])
    rec = {}
    for key, computed, reported, tol in [
            ("oos_sharpe", m["sharpe"], float(winner["oos_sharpe"]), 0.01),
            ("oos_max_drawdown", m["max_dd"], float(winner["max_drawdown"]), 0.005),
            ("oos_ann_return", m["ann_return"], float(winner["oos_ann_return"]), 0.005)]:
        diff = computed - reported
        rec[key] = {"computed": round(float(computed), 6), "reported_tournament": reported,
                    "diff": round(float(diff), 6), "tolerance": tol,
                    "verdict": "PASS" if abs(diff) <= tol else "FAIL"}
    assert all(v["verdict"] == "PASS" for v in rec.values()), f"ECON-SR1 reconciliation FAILED: {rec}"
    print("  ECON-SR1 reconciliation: PASS on all three headline metrics")

    sr = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"),
                       "position": position.reindex(spy_ret.index).fillna(0.0).values,
                       "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0.0).values,
                       "bh_return": spy_ret.values})
    sr_path = os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv")
    sr.to_csv(sr_path, index=False)
    with open(os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}_meta.json"), "w") as f:
        json.dump({"pair_id": PAIR_ID, "artifact": os.path.basename(sr_path),
                   "produced_by": "scripts/pair_pipeline_wells_fargo_housing_spy.py", "rule": "ECON-SR1",
                   "source": "pipeline_native_derivation (same code path as tournament evaluation)",
                   "returns_file": DATA_PATH, "coverage_start": str(spy_ret.index[0].date()),
                   "coverage_end": str(spy_ret.index[-1].date()), "frequency": "monthly",
                   "annualization": "Sharpe sqrt(12); ann_return mean*12",
                   "oos_start": split["oos_start"], "oos_end": split["oos_end"],
                   "position_semantics": (f"position on row t = return-accrual weight for month t; signal lagged "
                                          f"{int(winner['lead_months'])} month(s); strategy_return = position * bh_return"),
                   "reconciliation": {k: {"computed": v["computed"], "reported_winner_summary": v["reported_tournament"],
                                          "diff": v["diff"], "tolerance": v["tolerance"], "verdict": v["verdict"]}
                                      for k, v in rec.items()},
                   "generated_at": NOW_ISO, "generated_by": "Econ Evan (feat260706_wells_fargo_housing_spy)"}, f, indent=2)

    # winner_trade_log.csv
    log = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"),
                        "signal_value": sig_lagged.reindex(spy_ret.index).round(4),
                        "threshold": (thr.reindex(spy_ret.index).round(4) if isinstance(thr, pd.Series) else np.round(thr, 4)),
                        "position": position.reindex(spy_ret.index).fillna(0.0),
                        "spy_return": spy_ret.round(6),
                        "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0.0).round(6)})
    log["cumulative_return"] = ((1 + log["strategy_return"]).cumprod() - 1).round(6)
    log.to_csv(os.path.join(RESULTS_DIR, "winner_trade_log.csv"), index=False)

    # broker-style trade log (Rule C4)
    spy_px = df["spy"].reindex(spy_ret.index)
    broker_rows = []
    cum = (1 + strat_ret.reindex(spy_ret.index).fillna(0.0)).cumprod()
    prev = 0.0; capital = 10000.0
    sig_disp = f"{winner['signal']} ({SIGNAL_COLS[winner['signal']]})"
    posf = position.reindex(spy_ret.index).fillna(0.0)
    for dt in spy_ret.index:
        p = float(posf.loc[dt])
        if abs(p - prev) > 1e-9:
            side = "BUY" if p > prev else "SELL"
            notional = abs(p - prev) * capital
            sv = sig_lagged.loc[dt]; th = thr.loc[dt] if isinstance(thr, pd.Series) else thr
            broker_rows.append({"trade_date": dt.strftime("%Y-%m-%d"), "side": side, "instrument": TARGET_SYMBOL,
                                "quantity_pct": round(abs(p) * 100, 1),
                                "price": round(float(spy_px.loc[dt]), 4) if pd.notna(spy_px.loc[dt]) else np.nan,
                                "notional_usd": round(notional, 2), "commission_bps": COST_BPS,
                                "commission_usd": round(notional * COST_BPS / 10000, 2),
                                "cum_pnl_pct": round((cum.loc[dt] - 1) * 100, 4),
                                "reason": (f"{winner['strategy']}: {sig_disp} = {sv:.3f} vs threshold "
                                           f"{th:.3f} — position {prev*100:.0f}% -> {p*100:.0f}%"
                                           if pd.notna(sv) and pd.notna(th) else "position change")})
            prev = p
    broker_path = os.path.join(RESULTS_DIR, "winner_trades_broker_style.csv")
    with open(broker_path, "w") as f:
        f.write(f"# Simulated trade record based on backtest signals. No real trades were executed. "
                f"Starting capital: $10000. Commission: {COST_BPS} bps. Pair: {PAIR_ID} (MONTHLY rebalance). "
                f"Strategy: {winner['strategy']} on {sig_disp}, threshold {winner['threshold']}, "
                f"lead L{winner['lead_months']} months, {winner['lookback']}.\n")
        pd.DataFrame(broker_rows).to_csv(f, index=False)
    print(f"  Trade logs written ({len(log)} rows, {len(broker_rows)} broker events)")

    return (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
            position, strat_ret, sig_lagged, thr, cand)


# ===================================================================
# STAGE 8: CROSS-PERIOD ANALYSES (ECON-CP1)
# ===================================================================
@log_stage("8_cross_period")
def stage_cross_period(df, winner, split, position, strat_ret, sig_lagged):
    import statsmodels.api as sm
    with open(os.path.join(SCHEMA_DIR, "episode_registry.json")) as f:
        reg = json.load(f)
    block = reg.get("production", reg["_fallback"])
    episodes = block["episodes"] if isinstance(block, dict) else block
    oos = strat_ret[(strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])]
    rows = []; pos_eps = 0; eval_eps = 0
    for ep in episodes:
        sub = oos[(oos.index >= ep["start"]) & (oos.index <= ep["end"])].dropna()
        if len(sub) < 6:
            rows.append({"episode": ep["slug"], "start_date": ep["start"], "end_date": ep["end"],
                         "n_trading_days": len(sub) * 21, "ann_sharpe": np.nan, "win_rate": np.nan,
                         "max_drawdown": np.nan, "data_status": "insufficient_data", "durability_verdict": ""})
            continue
        m = ann_metrics(sub); eval_eps += 1; pos_eps += int(m["sharpe"] > 0)
        rows.append({"episode": ep["slug"], "start_date": str(sub.index[0].date()), "end_date": str(sub.index[-1].date()),
                     "n_trading_days": len(sub) * 21, "ann_sharpe": round(m["sharpe"], 4),
                     "win_rate": round(m["win_rate"], 4), "max_drawdown": round(m["max_dd"], 4),
                     "data_status": "validated", "durability_verdict": ""})
    if eval_eps >= 3:
        verdict = "durable" if pos_eps >= 3 else ("conditionally_durable" if pos_eps == 2 else "episode_concentrated")
    else:
        verdict = ("conditionally_durable" if pos_eps == eval_eps and eval_eps > 0 else "episode_concentrated") if eval_eps else "insufficient_data"
    if rows:
        rows[-1]["durability_verdict"] = verdict
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS_DIR, "subperiod_sharpe.csv"), index=False)
    print(f"  CP1-A: {eval_eps} episodes evaluable within OOS, {pos_eps} positive -> {verdict}")

    v = pd.concat([sig_lagged.rename("sig"), df["spy_fwd_1m"]], axis=1).dropna()
    full_r = v["sig"].corr(v["spy_fwd_1m"])
    roll = v["sig"].rolling(60).corr(v["spy_fwd_1m"])   # 60 months = 5yr window
    out = pd.DataFrame({"date": v.index.strftime("%Y-%m-%d"), "rolling_corr": roll.round(4).values, "n_obs": 60,
                        "window_start": v.index.to_series().shift(59).dt.strftime("%Y-%m-%d").values}).dropna(subset=["rolling_corr"])
    out.to_csv(os.path.join(RESULTS_DIR, f"rolling_correlation_{PAIR_ID}.csv"), index=False)
    same_sign = float((np.sign(roll.dropna()) == np.sign(full_r)).mean()) if roll.dropna().size else np.nan
    stab = ("sign_stable" if same_sign >= 0.7 else "moderately_stable" if same_sign >= 0.5 else "sign_unstable")
    print(f"  CP1-B: full-sample r={full_r:.3f}, sign stability {same_sign:.2f} (60M window) -> {stab}")

    reg_v = pd.concat([sig_lagged.rename("sig"), df["spy_ret"]], axis=1).dropna()
    yv = reg_v["spy_ret"].values; Xv = sm.add_constant(reg_v["sig"].values)
    n = len(yv); lo, hi = int(n * 0.15), int(n * 0.85)
    full = sm.OLS(yv, Xv).fit(); k = Xv.shape[1]

    def sup_f(y, X):
        best, bidx = -np.inf, lo
        for b in range(lo, hi):
            s1 = sm.OLS(y[:b], X[:b]).fit().ssr; s2 = sm.OLS(y[b:], X[b:]).fit().ssr
            fval = ((sm.OLS(y, X).fit().ssr - s1 - s2) / k) / ((s1 + s2) / (len(y) - 2 * k))
            if fval > best:
                best, bidx = fval, b
        return best, bidx

    f_obs, b_idx = sup_f(yv, Xv)
    rng = np.random.default_rng(42); null = []
    resid = full.resid; fitted = full.fittedvalues
    for _ in range(300):
        y_b = fitted + rng.choice(resid, size=n, replace=True)
        null.append(sup_f(y_b, Xv)[0])
    p_break = float((np.array(null) >= f_obs).mean())
    break_date = str(reg_v.index[b_idx].date()); flagged = p_break < 0.10
    sb = {"pair_id": PAIR_ID, "test": "Quandt-Andrews unknown breakpoint (sup-F, residual-bootstrap p, 300 reps; monthly)",
          "sample_start": str(reg_v.index[0].date()), "sample_end": str(reg_v.index[-1].date()), "n_obs": n,
          "trimming_pct": 0.15, "break_date": break_date, "f_stat": round(float(f_obs), 4),
          "p_value": round(p_break, 4), "flagged": flagged,
          "flag_message": ("Structural break detected — interpret cross-period results with caution; "
                           "see era_correlations.csv for the era-by-era relationship." if flagged else None),
          "rolling_corr_sign_stability": round(same_sign, 4) if pd.notna(same_sign) else None,
          "rolling_corr_stability_verdict": stab, "cp2_note": "CP2 skipped — regime_story not set in signal_scope.json"}
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
    top5 = cand.nlargest(min(5, len(cand)), "oos_sharpe")
    rng = np.random.default_rng(42); boot = np.zeros(5000)
    for b in range(5000):
        s = rng.choice(spy_oos.values, size=len(spy_oos), replace=True)
        boot[b] = (s.mean() / s.std()) * ANN if s.std() > 0 else 0
    rows = [{"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
             "lead_months": r.lead_months, "lookback": r.lookback, "oos_sharpe": r.oos_sharpe,
             "bootstrap_p_value": round(float((boot >= r.oos_sharpe).mean()), 4),
             "significant_at_5pct": bool((boot >= r.oos_sharpe).mean() < 0.05)} for r in top5.itertuples()]
    pd.DataFrame(rows).to_csv(os.path.join(VALID_DIR, "bootstrap.csv"), index=False)

    stress = {"GFC_Housing_Bust": ("2007-01-01", "2009-06-30"), "COVID": ("2020-01-01", "2020-12-31"),
              "Rate_Shock_2022": ("2022-01-01", "2023-06-30")}
    srows = []
    for nm, (s, e) in stress.items():
        sub_bh = df["spy_ret"][(df.index >= s) & (df.index <= e)].dropna()
        sub_st = strat_ret[(strat_ret.index >= s) & (strat_ret.index <= e)].dropna()
        if len(sub_bh) > 5:
            srows.append({"period": nm, "start": s, "end": e, "n_months": len(sub_bh),
                          "buy_hold_sharpe": round(ann_metrics(sub_bh)["sharpe"], 4),
                          "buy_hold_return_pct": round(sub_bh.sum() * 100, 2),
                          "winner_sharpe": round(ann_metrics(sub_st)["sharpe"], 4) if len(sub_st) > 5 else np.nan,
                          "winner_return_pct": round(sub_st.sum() * 100, 2) if len(sub_st) > 5 else np.nan})
    pd.DataFrame(srows).to_csv(os.path.join(VALID_DIR, "stress_tests.csv"), index=False)

    tx = []
    for r in top5.itertuples():
        for bps in [0, 5, 10, 25, 50]:
            ann_cost = r.annual_turnover * bps / 10000
            net = r.oos_sharpe - ann_cost / r.oos_ann_vol if r.oos_ann_vol > 0 else r.oos_sharpe
            tx.append({"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy,
                       "tx_cost_bps": bps, "gross_sharpe": r.oos_sharpe, "net_sharpe_approx": round(net, 4)})
    pd.DataFrame(tx).to_csv(os.path.join(VALID_DIR, "transaction_costs.csv"), index=False)
    print(f"  bootstrap (top{len(top5)}), stress ({len(srows)} periods), tx-cost grid saved")
    return rows


# ===================================================================
# MAIN
# ===================================================================
def main():
    t0 = time.time()
    df = stage_load()
    df, hmm_ok = stage_signals(df)
    corr_df = stage_correlations(df)
    ccf_df, ty_df, lp_df, reg_df, rev_flag, fwd_lp_flag = stage_core_models(df)
    lc, lc_path = stage_lead_analysis(df)
    qdf, era_df = stage_quartiles(df)
    tdf, split, tpath = stage_tournament(df)
    (winner, rec, n_valid, median_sharpe, n_tied, resolved_at,
     position, strat_ret, sig_lagged, thr, cand) = stage_winner(df, tdf, split, tpath)
    (lt, lt_path, L_star, best_at_grid, gate, wc, peak_lead,
     durable_leads) = stage_lead_tournament(df, split, tdf, winner)
    verdict, stab, sb, full_r = stage_cross_period(df, winner, split, position, strat_ret, sig_lagged)
    boot_rows = stage_validation(df, tdf, split, strat_ret)
    winner_boot_p = boot_rows[0]["bootstrap_p_value"] if boot_rows else np.nan

    bh = tdf[tdf.signal == "BENCHMARK"].iloc[0]

    # --- direction of winner ---
    orientation = winner["strategy"].rsplit("_", 1)[1]
    neg_thr = "neg_" in winner["threshold"]
    long_when_high = (orientation == "pro") != neg_thr
    direction = "procyclical" if long_when_high else "countercyclical"
    thr_value = float(thr.dropna().iloc[-1]) if isinstance(thr, pd.Series) else float(thr)
    thr_rule = "lt" if neg_thr else "gt"
    strat_family = winner["strategy"].rsplit("_", 1)[0]

    # --- lead-lag verdict (empirical) ---
    fwd_sig_lags = list(ty_df[(ty_df.direction == "indicator_to_target") & ty_df.significant].lag)
    rev_sig_lags = list(ty_df[(ty_df.direction == "target_to_indicator") & ty_df.significant].lag)
    ccf_lead = list(ccf_df[(ccf_df.lag > 0) & ccf_df.significant].lag)
    ccf_lag = list(ccf_df[(ccf_df.lag < 0) & ccf_df.significant].lag)
    if fwd_sig_lags and not rev_sig_lags:
        leadlag = "leading"
    elif rev_sig_lags and not fwd_sig_lags:
        leadlag = "lagging"
    elif fwd_sig_lags and rev_sig_lags:
        leadlag = "bidirectional"
    else:
        leadlag = "coincident_or_none"

    # ================= ECON-T5 selection provenance =================
    tdf_read = tdf.reset_index(drop=True)
    def _row_id(w):
        mask = ((tdf_read.signal == w["signal"]) & (tdf_read.threshold == w["threshold"]) &
                (tdf_read.strategy == w["strategy"]) & (tdf_read.lead_months == w["lead_months"]) &
                (tdf_read.lookback == w["lookback"]))
        idxs = list(tdf_read.index[mask])
        return idxs[0] if idxs else -1
    all_valid = tdf_read[(tdf_read.signal != "BENCHMARK") & tdf_read.valid].copy()
    pop_max = float(all_valid["oos_sharpe"].max())
    ru = all_valid.sort_values("oos_sharpe", ascending=False)
    runner = ru.iloc[1] if len(ru) > 1 else None
    winner_row_idx = _row_id(winner)
    strat_pop = tdf_read[tdf_read.signal != "BENCHMARK"]
    selection = {
        "objective": "max_oos_sharpe",
        "objective_formula": ("oos_ret.mean()/oos_ret.std()*sqrt(12) — MONTHLY annualization — maximised over the "
                              "full valid strategy population (SA source: no seasonal-cleanliness restriction; "
                              "ECON-T4 benchmark excluded); ties resolved by the ECON-T3 cascade"),
        "grid_scanned": {"leads": LEADS, "n_signals": int(strat_pop["signal"].nunique()),
                         "n_thresholds": int(strat_pop["threshold"].nunique()),
                         "n_strategies": int(strat_pop["strategy"].nunique()),
                         "n_valid_combos": int(len(all_valid)),
                         "median_valid_objective": round(float(all_valid["oos_sharpe"].median()), 4)},
        "tie_break_step": int(resolved_at) - 1,
        "raw_winner_row": {"signal": winner["signal"], "threshold": winner["threshold"],
                           "strategy": winner["strategy"], "lead_column": "lead_months",
                           "lead_value": int(winner["lead_months"]),
                           "source_tournament_file": os.path.basename(tpath),
                           "source_row_index": int(winner_row_idx),
                           "display_alias": (f"signal_code={REGISTRY_CODE[winner['signal']]} (raw signal={winner['signal']}); "
                                             f"strategy_family={strat_family} (raw strategy={winner['strategy']})")},
        "runner_up": (None if runner is None else
                      {"signal": runner["signal"], "threshold": runner["threshold"], "strategy": runner["strategy"],
                       "lead_value": int(runner["lead_months"]), "objective_value": round(float(runner["oos_sharpe"]), 4)}),
        "rationale": (f"Maximiser of OOS Sharpe over the full tradable MONTHLY lead grid L1..L12 "
                      f"({len(all_valid)} valid combos; median valid OOS Sharpe "
                      f"{round(float(all_valid['oos_sharpe'].median()),4)}). 394-month HMI x SPY overlap gives a "
                      f"{int(winner['oos_n'])}-month (~{int(winner['oos_n'])/12:.1f}yr) OOS window — ABOVE the 5-year "
                      f"reliability floor (a LONG sample by fleet standards), so the found-in-search caveat is "
                      f"materially weaker than short-history pairs, though the winner is still selected from "
                      f"{len(strat_pop)} scanned combos. ECON-LT1 gate: full grid scanned natively -> no staleness "
                      f"possible. Bounded-index guard: winner bounded_pct_risk={bool(winner['bounded_pct_risk'])}."),
        "objective_runner_up_divergence": None,
    }
    # ECON-T5 validations
    assert winner_row_idx >= 0, "raw winner row must resolve to exactly one tournament row"
    assert abs(float(winner["oos_sharpe"]) - pop_max) <= 1e-6, \
        "divergence is null -> winner must equal the population max (ECON-T5 §5c)"
    if runner is not None:
        assert float(runner["oos_sharpe"]) <= float(winner["oos_sharpe"]) + 1e-9, "runner-up must be 2nd best"

    pct_risk_note = ""
    if bool(winner["bounded_pct_risk"]):
        pct_risk_note = (" ARTIFACT-RISK FLAG: the winner uses a %-change transform of a bounded 0-100 index — "
                         "%-changes are level-dependent (8->16 = '+100%'); prefer the point-diff analogue when "
                         "interpreting; see design_note bounded-index section.")

    winner_summary = {
        "pair_id": PAIR_ID, "generated_at": NOW_ISO,
        "signal_column": SIGNAL_COLS[winner["signal"]],
        "signal_code": REGISTRY_CODE[winner["signal"]],
        "signal_display_name": f"NAHB HMI {winner['signal']}",
        "target_symbol": TARGET_SYMBOL, "threshold_code": winner["threshold"],
        "threshold_value": round(thr_value, 4), "threshold_rule": thr_rule,
        "threshold_note": ("threshold is rolling (window per lookback, in MONTHS); threshold_value is the latest rolling value — "
                           "see winner_trade_log.csv for the full path" if isinstance(thr, pd.Series) else "static threshold (IS-calibrated or native)"),
        "strategy_family": strat_family, "strategy_code": strat_family.split("_")[0],
        "strategy_display_name": {"P1_long_cash": "Long/Cash", "P2_signal_strength": "Signal-Strength Sizing",
                                  "P3_long_short": "Long/Short"}[strat_family],
        "strategy_description": "",
        "lead_value": int(winner["lead_months"]), "lead_unit": "months",
        "lead_description": (f"Signal lead = {int(winner['lead_months'])} month(s); grid floors at L1 by fleet "
                             f"convention although NAHB's mid-month release FOR the current month makes even L0 "
                             f"lookahead-free"),
        "lookback": winner["lookback"], "direction": direction,
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4), "oos_sortino": round(float(winner["oos_sortino"]), 4),
        "oos_calmar": round(float(winner["oos_calmar"]), 4), "oos_ann_return": round(float(winner["oos_ann_return"]), 4),
        "oos_ann_vol": round(float(winner["oos_ann_vol"]), 4), "oos_max_drawdown": round(float(winner["max_drawdown"]), 4),
        "oos_win_rate": round(float(winner["win_rate"]), 4), "oos_n_trades": int(winner["n_trades"]),
        "annual_turnover": round(float(winner["annual_turnover"]), 2), "oos_n": int(winner["oos_n"]),
        "oos_period_start": split["oos_start"], "oos_period_end": split["oos_end"],
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4), "bh_ann_return": round(float(bh["oos_ann_return"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4), "cost_assumption_bps": COST_BPS,
        "total_combos": int(len(tdf) - 1), "valid_combos": n_valid, "schema_version": "1.1.0",
        "selection": selection,
        "notes": (f"Mode 1, feat260706_wells_fargo_housing_spy — MONTHLY bounded-diffusion-index pair. "
                  f"Tournament: {len(tdf)-1} strategy combos (+1 benchmark, valid=False per ECON-T4), "
                  f"{n_valid} valid, exhaustive over the full tradable lead grid L1..L12 (GH #13 native). "
                  f"Winner by ECON-T3 cascade (resolved at step {resolved_at}; {n_tied} tied at step 1 — integer-"
                  f"granularity index, ties expected). OOS = {int(winner['oos_n'])} months "
                  f"(~{int(winner['oos_n'])/12:.1f}yr, ABOVE the 5yr floor — long by fleet standards)."
                  f"{pct_risk_note} "
                  f"Lead-lag verdict (empirical): HMI->SPY TY-Granger sig lags(m) {fwd_sig_lags or 'NONE'}, "
                  f"SPY->HMI sig lags(m) {rev_sig_lags or 'NONE'}; pre-whitened CCF sig lead(+) lags {ccf_lead or 'NONE'}, "
                  f"lag(-) lags {ccf_lag or 'NONE'} -> classified '{leadlag}'. "
                  f"Winner's own lead-curve peaks at L{peak_lead} (published L{int(winner['lead_months'])}); "
                  f"adjacent-lead durability: {durable_leads}. "
                  f"Robustness: winner bootstrap p={winner_boot_p} (vs resampled B&H); IS Sharpe {float(winner['is_sharpe']):.2f} "
                  f"vs OOS {float(winner['oos_sharpe']):.2f}; CP1 durability '{verdict}'; corr sign-stability '{stab}'; "
                  f"structural break flagged: {sb['flagged']} ({sb['break_date']}). "
                  f"Static source ends 2025-10 (~9 months stale at run date). "
                  f"Gross of costs; sensitivity in tournament_validation_{DATE_TAG}/."),
    }
    sd = ("Long SPY when the lagged NAHB HMI signal is {} its threshold; otherwise {}."
          .format("below" if thr_rule == "lt" else "above",
                  "cash" if strat_family == "P1_long_cash" else
                  ("short SPY" if strat_family == "P3_long_short" else "scaled by signal strength")))
    if strat_family == "P2_signal_strength":
        sd = ("SPY position sized continuously by where the lagged NAHB HMI signal sits in its rolling range "
              "(0% at the range bottom, 100% at the top" + (", inverted" if orientation == "counter" else "") + ").")
    if not long_when_high:
        sd += " (Countercyclical orientation: weak/deteriorating builder sentiment = risk-on.)"
    else:
        sd += " (Procyclical orientation: strong/improving builder sentiment = risk-on.)"
    sd += " Rebalanced MONTHLY."
    winner_summary["strategy_description"] = sd

    wpath = os.path.join(RESULTS_DIR, "winner_summary.json")
    with open(wpath, "w") as f:
        json.dump(winner_summary, f, indent=2)
    print(f"\n  winner_summary -> {wpath}")

    import subprocess
    rc = subprocess.run(["python3", os.path.join(BASE_DIR, "scripts", "validate_schema.py"),
                         "--schema", os.path.join(SCHEMA_DIR, "winner_summary.schema.json"),
                         "--instance", wpath]).returncode
    if rc != 0:
        raise SystemExit("winner_summary.json failed schema validation — fix the producer (ECON-H5)")
    print("  winner_summary schema validation: PASS")

    with open(os.path.join(SCHEMA_DIR, "signal_code_registry.json")) as f:
        registry_codes = {e["signal_code"] for e in json.load(f)["signals"]}
    assert winner_summary["signal_code"] in registry_codes, (
        f"signal_code '{winner_summary['signal_code']}' not in signal_code_registry.json (ECON-DS3)")
    print("  signal_code registry assertion: PASS")

    # interpretation_metadata: update EVAN-OWNED fields (+ indicator_nature if the
    # empirical verdict contradicts Dana's provisional 'leading' prior)
    interp_path = os.path.join(RESULTS_DIR, "interpretation_metadata.json")
    with open(interp_path) as f:
        interp = json.load(f)
    # Schema enum is ['leading','coincident','lagging'] (no 'mixed'/'bidirectional').
    # A reverse-dominant bidirectional verdict maps to the closest HONEST enum value,
    # 'lagging' (same asymmetry class as eci_total_comp_spy); the bidirectional nuance
    # lives in indicator_nature_note / key_finding, not in the enum field (META-NMF fix,
    # gate T1.1 2026-07-06 — do not regress to 'mixed' on re-run).
    nature_map = {"leading": "leading", "lagging": "lagging",
                  "bidirectional": "lagging", "coincident_or_none": "coincident"}
    empirical_nature = nature_map[leadlag]
    prior_nature = interp.get("indicator_nature")
    if empirical_nature != prior_nature:
        interp["indicator_nature"] = empirical_nature
        interp["indicator_nature_note"] = (
            f"Set by Evan from empirical evidence (was Dana provisional '{prior_nature}'): Granger/CCF "
            f"verdict '{leadlag}' — reverse-dominant bidirectional; a weak lag-5 forward blip exists but "
            f"the dominant causal direction is market->sentiment (SPY->HMI significant at all 12 lags, "
            f"transfer entropy reverse-only), so the closest schema-valid class is '{empirical_nature}'.")
    interp["observed_direction"] = direction
    interp["direction_consistent"] = interp.get("expected_direction") in ("mixed", direction)
    interp["key_finding"] = (
        f"Lead-lag verdict (empirical, MONTHLY): NAHB HMI is '{leadlag}' vs SPY. Toda-Yamamoto "
        f"Granger HMI->SPY significant lags(m) {fwd_sig_lags or 'NONE'}; SPY->HMI significant lags(m) "
        f"{rev_sig_lags or 'NONE'}; pre-whitened CCF significant lead(+) lags {ccf_lead or 'NONE'}, lag(-) "
        f"{ccf_lag or 'NONE'}. Tournament winner ({winner['signal']}/{winner['threshold']}/{strat_family} "
        f"{orientation}/L{winner['lead_months']}/{winner['lookback']}) is {direction}: OOS Sharpe "
        f"{winner_summary['oos_sharpe']:.2f} vs B&H {winner_summary['bh_sharpe']:.2f} over a "
        f"{int(winner['oos_n'])}-month OOS window (above the 5yr floor). "
        f"Winner's own lead-curve peaks at L{peak_lead} (published L{int(winner['lead_months'])}); "
        f"bootstrap p={winner_boot_p}, durability '{verdict}', break flagged: {sb['flagged']}."
        + (" Bounded-index %-transform artifact-risk flag applies to the winner." if bool(winner["bounded_pct_risk"]) else ""))
    interp["confidence"] = ("medium" if (fwd_sig_lags and winner_boot_p < 0.10) else "low")
    interp["last_updated_by"] = "evan"; interp["last_updated_at"] = NOW_ISO
    with open(interp_path, "w") as f:
        json.dump(interp, f, indent=2)
    assert interp["observed_direction"] in {"procyclical", "countercyclical", "mixed"}
    assert interp["observed_direction"] == winner_summary["direction"], "ECON-DIR1 consistency check failed"
    print(f"  interpretation_metadata evan-fields updated (indicator_nature: {interp['indicator_nature']}); ECON-DIR1: PASS")

    # tournament_winner.json (META-TWJ)
    tw = {"pair_id": PAIR_ID,
          "winner_label": f"{winner['signal']} / {winner['threshold']} / {strat_family} ({orientation}) / L{winner['lead_months']} / {winner['lookback']}",
          "winner_oos_sharpe": round(float(winner["oos_sharpe"]), 4), "winner_max_drawdown": round(float(winner["max_drawdown"]), 4),
          "winner_oos_ann_return": round(float(winner["oos_ann_return"]), 4), "bh_oos_sharpe": round(float(bh["oos_sharpe"]), 4),
          "bh_max_drawdown": round(float(bh["max_drawdown"]), 4), "bh_oos_ann_return": round(float(bh["oos_ann_return"]), 4),
          "delta_sharpe": round(float(winner["oos_sharpe"] - bh["oos_sharpe"]), 4),
          "delta_max_drawdown": round(float(winner["max_drawdown"] - bh["max_drawdown"]), 4),
          "delta_ann_return": round(float(winner["oos_ann_return"] - bh["oos_ann_return"]), 4),
          "beats_benchmark": bool(winner["oos_sharpe"] > bh["oos_sharpe"]), "suggested_strategy_objective": None,
          "generated_at": NOW_ISO}
    rel_sharpe = tw["delta_sharpe"] / max(abs(tw["bh_oos_sharpe"]), 0.1)
    rel_dd = tw["delta_max_drawdown"] / max(abs(tw["bh_max_drawdown"]), 0.01)
    tw["suggested_strategy_objective"] = "min_mdd" if rel_dd > rel_sharpe else "max_sharpe"
    with open(os.path.join(RESULTS_DIR, "tournament_winner.json"), "w") as f:
        json.dump(tw, f, indent=2)

    # signal_scope.json (ECON-UD)
    ind_der = [{"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []} for c, d, s, r in [
        ("nahb_hmi", "NAHB/Wells Fargo Housing Market Index level — bounded 0-100 builder-sentiment diffusion index, 50 = neutral; SA by NAHB", "Data Master.xlsx sheet WFHMI", "raw"),
        ("nahb_hmi_pct_yoy", "12-month % change (bounded-index caveat: %-changes are level-dependent)", "100*(L_t/L_{t-12}-1)", "derivative"),
        ("nahb_hmi_pct_mom", "1-month % change (bounded-index caveat)", "100*(L_t/L_{t-1}-1)", "derivative"),
        ("nahb_hmi_3m_pct", "3-month % change (bounded-index caveat)", "100*(L_t/L_{t-3}-1)", "derivative"),
        ("nahb_hmi_6m_pct", "6-month % change (bounded-index caveat)", "100*(L_t/L_{t-6}-1)", "derivative"),
        ("nahb_hmi_diff_3m", "3-month POINT change (index points; natural bounded-index momentum)", "L_t - L_{t-3}", "derivative"),
        ("nahb_hmi_diff_12m", "12-month POINT change (index points; level-independent annual momentum)", "L_t - L_{t-12}", "derivative"),
        ("nahb_hmi_ma12_idx", "12-month moving average of the level (trend input)", "rolling mean(12)", "derivative"),
        ("nahb_hmi_dev_trend_pct", "% deviation of the level from its 12M MA", "100*(L_t/MA12-1)", "derivative"),
        ("nahb_hmi_zscore_60m", "rolling 60-month z-score of the LEVEL (first-class: mean-reverting bounded index)", "(L_t-mean60m)/sd60m", "derivative"),
        ("nahb_hmi_diff12_zscore_60m", "rolling 60-month z-score of the 12M point change", "(diff12_t-mean60m)/sd60m", "derivative"),
        ("nahb_hmi_accel_pct", "MoM acceleration (change of MoM % change)", "mom_t - mom_{t-1}", "derivative"),
        ("nahb_hmi_above50", "binary regime flag: HMI > 50 = net builder optimism (native diffusion-index line)", "1{L_t > 50}", "regime_state"),
        ("hmm_2state_prob_stress", "P(builder-pessimism regime) from 2-state HMM on the level (level-regime split, deliberate)", "GaussianHMM(level)", "regime_state"),
        ("markov_regime_2state", "P(high-variance regime) from Markov-switching regression spy_ret~level", "MarkovRegression", "regime_state")]]
    if not hmm_ok:
        ind_der = [d for d in ind_der if d["name"] != "hmm_2state_prob_stress"]
    tgt_der = [{"name": c, "definition": d, "formula": s, "role": r, "appears_in_charts": []} for c, d, s, r in [
        ("spy", "SPY adjusted month-end close", "Yahoo Finance", "raw"),
        ("spy_ret", "SPY monthly return (decimal)", "P_t/P_{t-1}-1", "derivative"),
        ("spy_fwd_1m", "1-month forward SPY return", "P_{t+1}/P_t-1", "derivative"),
        ("spy_fwd_3m", "3-month forward SPY return", "P_{t+3}/P_t-1", "derivative"),
        ("spy_fwd_6m", "6-month forward SPY return", "P_{t+6}/P_t-1", "derivative"),
        ("spy_fwd_12m", "12-month forward SPY return", "P_{t+12}/P_t-1", "derivative")]]
    scope = {"pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
             "last_updated_at": NOW_ISO,
             "indicator_axis": {"canonical_column": "nahb_hmi", "display_name": "NAHB/Wells Fargo Housing Market Index", "derivatives": ind_der},
             "target_axis": {"canonical_column": "spy", "display_name": "SPY (S&P 500 ETF)", "derivatives": tgt_der},
             "notes": ("ECON-SD: only NAHB HMI derivatives and SPY derivatives are in scope. Controls in the parquet "
                       "(unrate, dgs10, fed_funds, vix) are context columns, NOT signals. Bounded 0-100 diffusion "
                       "index: level/point-diff/z-score first-class; %-transforms carry the bounded_pct_risk flag. "
                       "SA source — no seasonal-contamination constraint. regime_story: false (CP2 skipped).")}
    with open(os.path.join(RESULTS_DIR, "signal_scope.json"), "w") as f:
        json.dump(scope, f, indent=2)

    # kpis.json
    kpis = [
        {"metric": "OOS Sharpe (winner)", "value": f"{winner_summary['oos_sharpe']:.2f}", "unit": "ratio", "delta": f"{tw['delta_sharpe']:+.2f} vs B&H"},
        {"metric": "OOS Sharpe (buy & hold)", "value": f"{winner_summary['bh_sharpe']:.2f}", "unit": "ratio", "delta": None},
        {"metric": "OOS Annual Return (winner)", "value": f"{winner_summary['oos_ann_return']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_ann_return']*100:+.1f}pp vs B&H"},
        {"metric": "OOS Max Drawdown (winner)", "value": f"{winner_summary['oos_max_drawdown']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_max_drawdown']*100:+.1f}pp vs B&H"},
        {"metric": "Valid strategy combos", "value": f"{n_valid}", "unit": "count", "delta": None},
        {"metric": "OOS window", "value": f"{split['oos_start']} → {split['oos_end']} ({int(winner['oos_n'])} months, ~{int(winner['oos_n'])/12:.0f} years)", "unit": "dates", "delta": None},
    ]
    with open(os.path.join(RESULTS_DIR, "kpis.json"), "w") as f:
        json.dump(kpis, f, indent=2)

    # lead_sweep_manifest (ECON-LT1 record)
    with open(DATA_PATH, "rb") as f:
        input_sha = "sha256:" + hashlib.sha256(f.read()).hexdigest()[:16]
    lead_manifest = {
        "pair": PAIR_ID, "run_date": DATE_TAG, "frozen": False,
        "granularity": "MONTHS L1..12 tradable (L0 diagnostic-only in lead_correlation; ECON-LL1)",
        "freq_native": "M",
        "design_note": ("Lead L = month shift on month-end signals. Grid floors at L1 by FLEET CONVENTION, not "
                        "necessity: NAHB publishes mid-month FOR the current month (~zero publication lag), so an "
                        "L0 variant would be lookahead-free and defensible — deliberately not scanned (Dana Phase-0). "
                        "Grid ceiling L12 per ECON-LL1."),
        "oos_start": split["oos_start"], "is_end": split["in_sample_end"], "input_file": DATA_PATH,
        "input_sha256": input_sha, "lead_correlation_file": f"{PAIR_ID}/lead_correlation_{DATE_TAG}.csv",
        "lead_tournament_file": f"{PAIR_ID}/lead_tournament_{DATE_TAG}.csv",
        "lead_winner_curve_file": f"{PAIR_ID}/lead_winner_curve_{DATE_TAG}.csv",
        "lead_clean_envelope_file": f"{PAIR_ID}/lead_clean_envelope_{DATE_TAG}.csv",
        "clean_envelope_note": "SA source: all signals admissible -> envelope and clean envelope COINCIDE by construction",
        "published_winner": {"signal": SIGNAL_COLS[winner["signal"]], "lead": int(winner["lead_months"]),
                             "lead_unit": "months", "oos_sharpe": round(float(winner["oos_sharpe"]), 4)},
        "winner_curve_peak_lead": peak_lead,
        "winner_adjacent_lead_durability": bool(durable_leads),
        "L_star": L_star, "best_oos_sharpe_at_grid": round(float(best_at_grid), 4) if pd.notna(best_at_grid) else None,
        "gate_decision": gate,
        "assertions": ["tradable lead grid is L1..12 MONTHS (L0 excluded by fleet convention despite ~zero pub lag)",
                       "main tournament scans the full L1..12 grid -> published winner is the global lead max",
                       f"ECON-LT1 gate: L*={L_star} -> {gate}"]}
    with open(os.path.join(RESULTS_DIR, f"lead_sweep_manifest_{DATE_TAG}.json"), "w") as f:
        json.dump(lead_manifest, f, indent=2)

    # design_note.md — APPEND Phase-1 sections to Dana's Phase-0 note (preserve her content)
    with open(os.path.join(RESULTS_DIR, "design_note.md")) as f:
        dana_note = f.read().rstrip()
    era_md = era_df.to_markdown(index=False)
    phase1 = f"""

---

# Phase 1 addendum — Econometrics & Tournament (Evan, {DATE_TAG})

## Bounded-diffusion-index conventions (design deviations, per Dana's Phase-0)
- LEVEL and level z-score are FIRST-CLASS signals (bounded 0-100, 50 = neutral, mean-reverting).
- Point changes (diff_3m/diff_12m) are the natural momentum metric; %-change transforms are
  level-dependent (8 -> 16 = "+100%") — included for family consistency, flagged per-row
  (`bounded_pct_risk` column); a pct-transform winner is artifact-flagged in winner_summary.notes.
- Native thresholds added: T4_gap50 (level > 50) and T4_above50 (the binary regime flag's only threshold).
- Integer-granularity values: percentile/rank ties are expected; strict `>` comparisons are
  deterministic and quartile bucketing uses rank(method='first'); winner ties resolve via ECON-T3.

## Method coverage (Rule C1, sentiment + leading-candidate battery)
- Correlations incl. distance (n-floor {CORR_N_FLOOR} months), horizons 1/3/6/12M fwd.
- Pre-whitened CCF at monthly lags -24..+24 (housing classically leads up to ~2yr; AR order by AIC, max 12).
- Toda-Yamamoto Granger both directions, lags 1..12 months, d_max=1 (level ADF non-stat/KPSS borderline).
- Local projections fwd+rev at 1/3/6/12M horizons, HAC SEs. Transfer entropy tercile-binned, 500 perms.
- Quantile regression on 1m-fwd. HMM 2-state on the LEVEL (optimism/pessimism split — deliberate for a
  bounded sentiment index; stress = LOW-sentiment regime). Markov-switching spy_ret ~ level.
- Era sub-period battery (era_correlations.csv): pre-GFC 1993-2006 / GFC-bust 2007-2012 /
  QE-era 2013-2019 / post-COVID 2020-2025, level + diff_12m vs 1M-fwd SPY:

{era_md}

- Stationarity: Dana's tests (stationarity_tests_{DATE_TAG}.csv) reviewed and CONFIRMED, not re-run.
  Level ADF p=0.16 / KPSS fail-to-reject (bounded — cannot be a true random walk); all change/z-score
  transforms and spy_ret stationary.

## Tournament grid (monthly template, 394-month sample affords the full battery)
- Signals: 12 native + hmm_stress + markov_regime. Thresholds: T1 IS-percentiles {{25,50,75}},
  T2 rolling percentiles {{25,75}}, T3 rolling z ±1.0/±1.5 x {{LB36,LB60,LB120}}, T4_zero
  (sign-meaningful), T4_gap50, T4_above50. Strategies: P1 long/cash, P2 signal-strength, P3 long/short,
  each pro/counter. Leads L1..L12 exhaustive (GH #13 artifacts native).
- Eligibility: signal >= {SIG_ELIGIBLE_MIN} non-NaN months; IS >= 120 months; OOS >= 36 months;
  validity = OOS Sharpe > 0.3 (equity threshold) and turnover < 24 position-changes/yr.

## OOS split (ECON-OOS2)
Policy v1_max36_25pct_cap120: span = min(max(36, round({split['sample_size_months']} x 0.25)), 120) =
{int(min(max(36, round(split['sample_size_months']*0.25)), 120))} months -> OOS {split['oos_start']}..{split['oos_end']}
(~{int(min(max(36, round(split['sample_size_months']*0.25)), 120))/12:.1f} years — ABOVE the 5yr reliability floor; the first
pair in a while where a proper OOS verdict is possible). IS covers the 1990s expansion, dot-com, the
classic 2005-09 housing-leads-the-cycle episode and the QE era; OOS spans 2018 vol, COVID, the 2021
housing boom, the 2022 rate shock (HMI 83->31) and the 2023-25 high-rate regime.

## Lead-lag verdict (empirical — determined by Granger/CCF/LP, NOT the prior)
- HMI->SPY TY-Granger significant lags (months): {fwd_sig_lags or 'NONE'}
- SPY->HMI TY-Granger significant lags (months): {rev_sig_lags or 'NONE'}
- Pre-whitened CCF significant lead(+) lags: {ccf_lead or 'NONE'}; lag(-) lags: {ccf_lag or 'NONE'}
- LP forward significant: {fwd_lp_flag}; reverse-causality flag: {rev_flag}
- **Classification: {leadlag}.** Winner direction (empirical): {direction}.
- Dana's provisional prior was 'leading' (Leamer 2007); interpretation_metadata carries the EMPIRICAL verdict.
- Winner's own lead-curve peaks at L{peak_lead} (published L{int(winner['lead_months'])}); adjacent-lead
  durability (ECON-LT2 spirit): {durable_leads}.

## Sub-period stability & structural breaks
- Quandt-Andrews sup-F on spy_ret ~ winner-signal: break at {sb['break_date']}, bootstrap p={sb['p_value']},
  flagged={sb['flagged']}. Rolling 60M correlation sign-stability: {stab}. CP1 episode durability: {verdict}.
- See era_correlations.csv above for the era-by-era relationship (the 1990s/2000s housing-equity link vs
  post-GFC vs post-COVID).

## Tournament conventions
- Units in tournament_results CSV are RATIOS (decimal). Lead column `lead_months`. Both orientations tested.
- GH #13 artifacts emitted natively: lead_winner_curve_{DATE_TAG}.csv and lead_clean_envelope_{DATE_TAG}.csv
  (SA source -> envelope == clean envelope by construction).
- Static source ends 2025-10 (~9 months stale at run date) — flagged in evidence_status.json.
- CP2 skipped (regime_story: false). Returns gross of costs; cost grid in tournament_validation_{DATE_TAG}/.

## New pair — no prior version; Rule C3 regression diff N/A.
"""
    with open(os.path.join(RESULTS_DIR, "design_note.md"), "w") as f:
        f.write(dana_note + phase1)

    # analyst_suggestions.json
    sugg = {"schema_version": "1.0.0", "pair_id": PAIR_ID, "rule": "ECON-AS",
            "suggestions": [
                {"signal_name": "NAHB HMI components (present sales / 6M expectations / buyer traffic)", "proposed_by": "evan",
                 "source": "NAHB (component series exist alongside the composite)",
                 "observation": "The composite blends three sub-questions; the 6-month-expectations component is the purest forward-looking sentiment read.",
                 "rationale": "If the composite leads, the expectations component may lead by more with less noise.",
                 "possible_use_case": "variant family", "caveats": "Component history availability in the Master unknown.",
                 "date_filed": "2026-07-06"},
                {"signal_name": "HMI minus mortgage-rate composite (sentiment net of rates)", "proposed_by": "evan",
                 "source": "Data Master + FRED (MORTGAGE30US)",
                 "observation": "Post-2020 the HMI is largely a mortgage-rate mirror; a rate-orthogonalized HMI isolates the non-rate sentiment signal.",
                 "rationale": "Separates the Fed channel from the housing-specific channel.",
                 "possible_use_case": "companion signal", "caveats": "Two-series composite — out of single-indicator scope.",
                 "date_filed": "2026-07-06"},
                {"signal_name": "HMI -> XHB/ITB (homebuilder ETFs)", "proposed_by": "evan", "source": "Yahoo",
                 "observation": "Builder sentiment should transmit to builder equities more directly than to the broad index.",
                 "rationale": "Sharper identification of the sentiment->equity channel; SPY dilutes it.",
                 "possible_use_case": "new pair", "caveats": "XHB/ITB inception 2006 — shorter overlap.", "date_filed": "2026-07-06"}],
            "last_updated_by": "evan", "last_updated_at": NOW_ISO}
    with open(os.path.join(RESULTS_DIR, "analyst_suggestions.json"), "w") as f:
        json.dump(sugg, f, indent=2)

    # evidence_status.json
    ev = {"pair_id": PAIR_ID, "generated_at": NOW_ISO, "generated_by": "evan",
          "blocks": {
              "correlations": "ready", "lead_correlation": "ready", "lead_tournament": "ready",
              "lead_winner_curve": "ready", "lead_clean_envelope": "ready",
              "ccf_prewhitened": "ready", "granger_causality": "ready", "transfer_entropy": "ready",
              "local_projections": "ready", "quantile_regression": "ready", "regime_quartile_returns": "ready",
              "era_correlations": "ready",
              "hmm_states": "ready" if hmm_ok else "skipped_degenerate",
              "subperiod_sharpe": "ready", "structural_break": "ready", "rolling_correlation": "ready",
              "tournament": "ready", "winner_summary": "ready"},
          "caveats": [f"OOS = {int(winner['oos_n'])} months (~{int(winner['oos_n'])/12:.1f}yr) — ABOVE the 5yr floor; found-in-search caveat applies but is weaker than short-history pairs",
                      "STATIC SOURCE: Data Master ends 2025-10 (~9 months stale at run date); refresh requires a Master update",
                      "bounded 0-100 index: %-change transforms are level-dependent (bounded_pct_risk flag per tournament row)",
                      "integer-granularity values: ties on rank/percentile thresholds handled deterministically",
                      "L0 would be lookahead-free (NAHB mid-month release for current month) but grid floors at L1 by fleet convention",
                      f"empirical lead-lag class: {leadlag}"]}
    with open(os.path.join(RESULTS_DIR, "evidence_status.json"), "w") as f:
        json.dump(ev, f, indent=2)

    # timing
    with open(os.path.join(RESULTS_DIR, f"pipeline_timing_{DATE_TAG}.json"), "w") as f:
        json.dump({"pair_id": PAIR_ID, "date": DATE_TAG, "pipeline_seconds": round(time.time() - t0, 1),
                   "stage_times": {k: round(v, 1) for k, v in STAGE_TIMES.items()},
                   "tournament_strategy_rows": int(len(tdf) - 1), "valid_strategies": n_valid,
                   "oos_n_months": int(winner["oos_n"]), "oos_start": split["oos_start"], "oos_end": split["oos_end"]}, f, indent=2)

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE — HANDOFF NUMBERS (DPS-SCD1)")
    print("=" * 70)
    print(f"  Strategy combos: {len(tdf)-1} | valid: {n_valid} | median OOS Sharpe (valid): {median_sharpe:.3f}")
    print(f"  Winner: {tw['winner_label']} | bounded_pct_risk={bool(winner['bounded_pct_risk'])}")
    print(f"  OOS Sharpe {winner_summary['oos_sharpe']} vs B&H {winner_summary['bh_sharpe']} | "
          f"DD {winner_summary['oos_max_drawdown']} vs {winner_summary['bh_max_drawdown']} | "
          f"ret {winner_summary['oos_ann_return']} vs {winner_summary['bh_ann_return']}")
    print(f"  Ties at step 1: {n_tied} (cascade resolved at step {resolved_at})")
    print(f"  Durability: {verdict} | corr sign-stability: {stab} | break flagged: {sb['flagged']} ({sb['break_date']})")
    print(f"  Direction (winner): {direction} | lead-lag class: {leadlag} | ECON-LT1: L*={L_star} ({gate})")
    print(f"  Winner lead-curve peak: L{peak_lead} (published L{int(winner['lead_months'])}); adjacent-lead durable: {durable_leads}")
    print(f"  Granger fwd-sig lags(m): {fwd_sig_lags or 'NONE'} | rev-sig lags(m): {rev_sig_lags or 'NONE'} | "
          f"CCF lead lags: {ccf_lead or 'NONE'}")
    print(f"  Winner bootstrap p={winner_boot_p} | OOS {int(winner['oos_n'])} months (~{int(winner['oos_n'])/12:.1f}yr)")
    return winner_summary, tw


if __name__ == "__main__":
    main()
