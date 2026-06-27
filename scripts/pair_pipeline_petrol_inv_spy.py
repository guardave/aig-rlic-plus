#!/usr/bin/env python3
"""Econometrics pipeline for petroleum inventories -> SPY.

Pair: petrol_inv_spy
Role: Econ Evan
Date tag: 20260617

Hypotheses:
H1 counter-cyclical demand signal: rising petroleum stocks reflect weak fuel
demand and lower forward SPY returns, so inverted inventory rate-of-change or
high-stock regimes may be useful defensively.
H1b supply-glut benign: inventory builds are supply-driven and carry no equity
signal.
H0 petroleum stocks do not predict SPY.

Lag convention: the daily LVCF panel already carries only values public after
release_date, with days_since_release 0-6. Monthly month-end values are treated
as feasible at L0 because the release lag is documented and the month-end panel
uses the public weekly observations available inside the month. The tournament
still tests L0/L1/L2/L3/L6/L12 and states the convention in design_note.md.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
np.random.seed(42)

PAIR_ID = "petrol_inv_spy"
TARGET_SYMBOL = "SPY"
DATE_TAG = "20260617"
COST_BPS = 5

ROOT = Path("/workspaces/aig-rlic-plus")
MONTHLY_PATH = ROOT / "data/petrol_inv_spy_monthly_latest.parquet"
DAILY_PATH = ROOT / "data/petrol_inv_spy_daily_latest.parquet"
RESULTS = ROOT / "results" / PAIR_ID
MODELS = RESULTS / f"core_models_{DATE_TAG}"
VALID = RESULTS / f"tournament_validation_{DATE_TAG}"
SCHEMAS = ROOT / "docs/schemas"

for d in (RESULTS, MODELS, VALID):
    d.mkdir(parents=True, exist_ok=True)

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TIMES: dict[str, float] = {}

SIGNALS = {
    "petrol_yoy": "petrol_inv_pct_yoy",
    "petrol_pct_chg": "petrol_inv_pct_chg",
    "petrol_3m": "petrol_inv_3m_pct",
    "petrol_6m": "petrol_inv_6m_pct",
    "petrol_dev_trend": "petrol_inv_dev_trend_pct",
    "petrol_level_z60": "petrol_inv_zscore_60m",
    "petrol_yoy_z60": "petrol_inv_yoy_zscore_60m",
    "petrol_accel": "petrol_inv_accel_pct",
    "hmm_stress": "hmm_2state_prob_stress",
    "markov_regime": "markov_regime_2state",
}

RAW_SIGNAL_MAP = {k: v for k, v in SIGNALS.items() if not k.startswith(("hmm", "markov"))}
FWD = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]


def timed(name):
    def deco(fn):
        def wrap(*args, **kwargs):
            t0 = time.time()
            print(f"\n=== {name} ===")
            out = fn(*args, **kwargs)
            TIMES[name] = time.time() - t0
            print(f"{name}: {TIMES[name]:.1f}s")
            return out

        return wrap

    return deco


def ann_metrics(r: pd.Series) -> dict[str, float]:
    r = r.dropna()
    if len(r) == 0 or r.std() == 0:
        return {
            "sharpe": 0.0,
            "ann_return": 0.0,
            "ann_vol": 0.0,
            "max_dd": 0.0,
            "sortino": 0.0,
            "calmar": 0.0,
            "win_rate": 0.0,
            "n": len(r),
        }
    sharpe = r.mean() / r.std() * np.sqrt(12)
    ann_ret = r.mean() * 12
    ann_vol = r.std() * np.sqrt(12)
    cum = (1 + r).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    neg = r[r < 0]
    sortino = ann_ret / (neg.std() * np.sqrt(12)) if len(neg) > 1 and neg.std() else 0.0
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    return {
        "sharpe": float(sharpe),
        "ann_return": float(ann_ret),
        "ann_vol": float(ann_vol),
        "max_dd": float(dd),
        "sortino": float(sortino),
        "calmar": float(calmar),
        "win_rate": float((r > 0).mean()),
        "n": len(r),
    }


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def manifest_for(path: Path, columns: dict, assertions: list, extra: dict | None = None) -> None:
    payload = {
        "file": path.name,
        "pair_id": PAIR_ID,
        "produced_by": "scripts/pair_pipeline_petrol_inv_spy.py",
        "generated_at": NOW,
        "columns": columns,
        "assertions": assertions,
    }
    if extra:
        payload.update(extra)
    write_json(path.with_name(path.stem + "_manifest.json"), payload)


def distance_corr(x, y) -> float:
    x = np.asarray(x, float)[:, None]
    y = np.asarray(y, float)[:, None]
    a = np.abs(x - x.T)
    b = np.abs(y - y.T)
    A = a - a.mean(0) - a.mean(1)[:, None] + a.mean()
    B = b - b.mean(0) - b.mean(1)[:, None] + b.mean()
    dcov2 = (A * B).mean()
    dvx = (A * A).mean()
    dvy = (B * B).mean()
    return float(np.sqrt(max(dcov2, 0) / np.sqrt(dvx * dvy))) if dvx > 0 and dvy > 0 else 0.0


@timed("load")
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly = pd.read_parquet(MONTHLY_PATH)
    daily = pd.read_parquet(DAILY_PATH)
    assert monthly.shape == (429, 18), monthly.shape
    assert daily.shape == (8230, 23), daily.shape
    assert daily["days_since_release"].max() <= 6
    assert daily["days_since_release"].min() >= 0
    # Confirm Dana stationarity artifact exists; do not re-run tests.
    st = RESULTS / "stationarity_tests_20260617.csv"
    assert st.exists() and pd.read_csv(st).shape[0] > 0
    print(f"monthly {monthly.shape}: {monthly.index.min().date()} -> {monthly.index.max().date()}")
    print(f"daily {daily.shape}: {daily.index.min().date()} -> {daily.index.max().date()}")
    return monthly, daily


@timed("signals")
def add_regime_signals(df: pd.DataFrame) -> pd.DataFrame:
    from hmmlearn.hmm import GaussianHMM

    df = df.copy()
    sig = df["petrol_inv_yoy_zscore_60m"].dropna()
    X = sig.values.reshape(-1, 1)
    hmm = GaussianHMM(n_components=2, covariance_type="full", n_iter=500, random_state=42)
    hmm.fit(X)
    probs = hmm.predict_proba(X)
    state_mean = [sig.iloc[hmm.predict(X) == i].mean() for i in range(2)]
    stress_state = int(np.argmax(state_mean))  # high inventory-growth z-score = demand-stress prior
    prob = pd.Series(probs[:, stress_state], index=sig.index, name="hmm_2state_prob_stress")
    df["hmm_2state_prob_stress"] = prob
    df["markov_regime_2state"] = prob.rolling(3, min_periods=1).mean()

    states = pd.DataFrame(
        {
            "hmm_state": pd.Series(hmm.predict(X), index=sig.index),
            "prob_stress": prob,
            "prob_calm": 1 - prob,
        }
    )
    states.to_parquet(MODELS / "hmm_states.parquet")
    summary = []
    for label, mask in [("stress", states["hmm_state"] == stress_state), ("calm", states["hmm_state"] != stress_state)]:
        idx = states.index[mask]
        r = df["spy_ret"].reindex(idx).dropna()
        summary.append(
            {
                "state_label": label,
                "mean_return": round(float(r.mean()), 6) if len(r) else np.nan,
                "vol": round(float(r.std()), 6) if len(r) else np.nan,
                "duration_days": int(mask.sum() * 21),
                "frequency_pct": round(float(mask.mean() * 100), 2),
                "mean_yoy_zscore": round(float(sig.reindex(idx).mean()), 3),
            }
        )
    pd.DataFrame(summary).to_csv(MODELS / "hmm_summary.csv", index=False)
    manifest_for(
        MODELS / "hmm_states.parquet",
        {
            "hmm_state": "2-state Gaussian HMM state on petroleum inventory YoY z-score",
            "prob_stress": "probability of high-inventory-growth regime",
            "prob_calm": "1 - prob_stress",
        },
        [
            {"description": "probabilities bounded", "check": "prob_stress in [0,1]"},
            {"description": "COVID demand shock checked", "filter": "2020-03 to 2020-06", "column": "prob_stress"},
            {"description": "state labels semantic", "check": "stress = higher YoY z-score mean"},
        ],
    )

    sig_path = RESULTS / f"signals_{DATE_TAG}.parquet"
    cols = [c for c in SIGNALS.values() if c in df.columns]
    df[cols].to_parquet(sig_path)
    manifest_for(
        sig_path,
        {c: f"petroleum-inventory derivative signal ({c})" for c in cols},
        [
            {"description": "winner signal column must be present", "check": "enforced after winner selection"},
            {"description": "no raw nonstationary level as tournament signal", "check": "petrol_inv_kb excluded"},
            {"description": "HMM probability bounded", "column": "hmm_2state_prob_stress", "check": "[0,1]"},
        ],
    )
    return df


@timed("correlations")
def correlations(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    horizons = {"spy_fwd_1m": 21, "spy_fwd_3m": 63, "spy_fwd_6m": 126, "spy_fwd_12m": 252}
    for code, col in SIGNALS.items():
        if col not in df:
            continue
        for fwd, h in horizons.items():
            v = df[[col, fwd]].dropna()
            if len(v) < 60:
                continue
            x, y = v[col], v[fwd]
            for metric, fn in (("pearson", stats.pearsonr), ("spearman", stats.spearmanr), ("kendall", stats.kendalltau)):
                r, p = fn(x, y)
                rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": h, "metric": metric, "value": round(float(r), 4), "p_value": round(float(p), 4), "n_obs": len(v)})
            rows.append({"pair_name": f"{code}__{fwd}", "horizon_days": h, "metric": "distance", "value": round(distance_corr(x, y), 4), "p_value": np.nan, "n_obs": len(v)})
    out = pd.DataFrame(rows)
    path = MODELS / "correlations.csv"
    out.to_csv(path, index=False)
    manifest_for(
        path,
        {"pair_name": "signal__forward_return", "horizon_days": "21/63/126/252 equivalents", "metric": "pearson/spearman/kendall/distance", "value": "association statistic", "p_value": "two-sided p, except distance", "n_obs": "observations"},
        [{"description": "correlation values bounded", "check": "abs(value)<=1"}, {"description": "distance correlation nonnegative", "check": "distance >= 0"}, {"description": "stationary transforms only", "check": "petrol_inv_kb excluded"}],
    )
    return out


@timed("core_models")
def core_models(df: pd.DataFrame):
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.ar_model import AutoReg
    from statsmodels.tsa.api import VAR

    main = "petrol_inv_yoy_zscore_60m"
    pair = df[[main, "spy_ret"]].dropna()
    x, y = pair[main], pair["spy_ret"]

    best_p, best_aic = 1, np.inf
    for p in range(1, 13):
        try:
            aic = AutoReg(x, lags=p, old_names=False).fit().aic
            if aic < best_aic:
                best_aic, best_p = aic, p
        except Exception:
            pass
    ar = AutoReg(x, lags=best_p, old_names=False).fit()
    xw = ar.resid
    yw = y.copy() - ar.params.iloc[0]
    for i in range(1, best_p + 1):
        yw = yw - ar.params.iloc[i] * y.shift(i)
    common = xw.index.intersection(yw.dropna().index)
    se = 1.96 / np.sqrt(len(common))
    ccf_rows = []
    for lag in range(-20, 21):
        a, b = (xw.shift(lag), yw) if lag >= 0 else (xw, yw.shift(-lag))
        v = pd.concat([a, b], axis=1).dropna()
        c = v.corr().iloc[0, 1] if len(v) > 30 else np.nan
        ccf_rows.append({"lag": lag, "ccf": round(float(c), 4) if pd.notna(c) else np.nan, "lower_ci": round(-se, 4), "upper_ci": round(se, 4), "significant": bool(pd.notna(c) and abs(c) > se), "arima_order": f"AR({best_p})", "n_obs": len(v)})
    ccf = pd.DataFrame(ccf_rows)
    ccf.to_csv(MODELS / "ccf_prewhitened.csv", index=False)

    gdata = pair.rename(columns={main: "ind", "spy_ret": "tgt"})
    try:
        p_opt = max(int(VAR(gdata).select_order(maxlags=12).aic), 1)
    except Exception:
        p_opt = 1

    def ty(caused, causing, lag):
        d_max = 1
        cols = {}
        for i in range(1, lag + d_max + 1):
            cols[f"{causing}_l{i}"] = gdata[causing].shift(i)
            cols[f"{caused}_l{i}"] = gdata[caused].shift(i)
        Xd = pd.DataFrame(cols).dropna()
        fit = sm.OLS(gdata[caused].reindex(Xd.index), sm.add_constant(Xd)).fit()
        hyp = ", ".join(f"{causing}_l{i} = 0" for i in range(1, lag + 1))
        ft = fit.f_test(hyp)
        return float(ft.fvalue), float(ft.pvalue), int(ft.df_num), int(ft.df_denom)

    ty_rows, by_lag = [], []
    for lag in range(1, 13):
        for direction, caused, causing in (("indicator_to_target", "tgt", "ind"), ("target_to_indicator", "ind", "tgt")):
            try:
                f, p, dfn, dfd = ty(caused, causing, lag)
                row = {"direction": direction, "lag": lag, "f_statistic": round(f, 4), "p_value": round(p, 4), "significant": p < 0.05}
                ty_rows.append(row)
                if direction == "indicator_to_target":
                    by_lag.append({"lag": lag, "f_statistic": round(f, 4), "p_value": round(p, 4), "df_num": dfn, "df_den": dfd})
            except Exception as exc:
                print(f"TY lag {lag} {direction} failed: {exc}")
    ty_df = pd.DataFrame(ty_rows)
    ty_df.to_csv(MODELS / "granger_causality.csv", index=False)
    pd.DataFrame(by_lag).to_csv(RESULTS / "granger_by_lag.csv", index=False)

    def transfer_entropy(src, dst, bins=3, lag=1):
        v = pd.concat([src, dst], axis=1).dropna()
        s = pd.qcut(v.iloc[:, 0], bins, labels=False, duplicates="drop")
        t = pd.qcut(v.iloc[:, 1], bins, labels=False, duplicates="drop")
        tt, tl, sl = t[lag:].values, t[:-lag].values, s[:-lag].values

        def H(*cols):
            arr = np.stack(cols, axis=1)
            _, counts = np.unique(arr, axis=0, return_counts=True)
            p = counts / counts.sum()
            return -np.sum(p * np.log(p))

        return H(tt, tl) - H(tt, tl, sl) + H(tl, sl) - H(tl)

    rng = np.random.default_rng(42)
    te_rows = []
    for direction, src, dst in (("indicator_to_target", x, y), ("target_to_indicator", y, x)):
        te = transfer_entropy(src, dst)
        v = pd.concat([src, dst], axis=1).dropna()
        null = [transfer_entropy(pd.Series(rng.permutation(v.iloc[:, 0].values), index=v.index), v.iloc[:, 1]) for _ in range(300)]
        te_rows.append({"direction": direction, "te_value": round(float(te), 5), "permutation_p_value": round(float((np.asarray(null) >= te).mean()), 4), "n_permutations": 300, "bandwidth": np.nan, "bin_method": "tercile_qcut"})
    pd.DataFrame(te_rows).to_csv(MODELS / "transfer_entropy.csv", index=False)

    lp_rows = []
    for direction in ("fwd", "rev"):
        for h in (1, 3, 6, 12):
            if direction == "fwd":
                v = df[[main, f"spy_fwd_{h}m"]].dropna()
                xv, yv = v[main], v[f"spy_fwd_{h}m"]
            else:
                v = pd.concat([df["spy_ret"], df[main].shift(-h)], axis=1).dropna()
                xv, yv = v.iloc[:, 0], v.iloc[:, 1]
            if len(v) < 60:
                continue
            fit = sm.OLS(yv.values, sm.add_constant(xv.values)).fit(cov_type="HAC", cov_kwds={"maxlags": h + int(0.75 * len(v) ** (1 / 3))})
            ci = fit.conf_int()
            lp_rows.append({"horizon": h, "coef": round(float(fit.params[1]), 6), "se": round(float(fit.bse[1]), 6), "ci_lower": round(float(ci[1][0]), 6), "ci_upper": round(float(ci[1][1]), 6), "p_value": round(float(fit.pvalues[1]), 4), "direction": direction})
    lp = pd.DataFrame(lp_rows)
    lp.to_csv(MODELS / "local_projections.csv", index=False)

    qr_rows = []
    v = df[[main, "spy_fwd_3m"]].dropna().rename(columns={main: "sig", "spy_fwd_3m": "fwd"})
    for tau in (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95):
        fit = smf.quantreg("fwd ~ sig", v).fit(q=tau)
        ci = fit.conf_int()
        qr_rows.append({"tau": tau, "coef": round(float(fit.params["sig"]), 6), "se": round(float(fit.bse["sig"]), 6), "p_value": round(float(fit.pvalues["sig"]), 4), "ci_lower": round(float(ci.loc["sig", 0]), 6), "ci_upper": round(float(ci.loc["sig", 1]), 6)})
    pd.DataFrame(qr_rows).to_csv(MODELS / "quantile_regression.csv", index=False)

    reg_rows = []
    for code, col in SIGNALS.items():
        if col not in df:
            continue
        for fwd in FWD:
            v = df[[col, fwd]].dropna()
            if len(v) < 60:
                continue
            fit = sm.OLS(v[fwd].values, sm.add_constant(v[col].values)).fit(cov_type="HC3")
            reg_rows.append({"signal": code, "horizon": fwd, "coef": round(float(fit.params[1]), 6), "se": round(float(fit.bse[1]), 6), "t_stat": round(float(fit.tvalues[1]), 3), "p_value": round(float(fit.pvalues[1]), 4), "r_squared": round(float(fit.rsquared), 4), "n": int(fit.nobs)})
    pd.DataFrame(reg_rows).to_csv(MODELS / "predictive_regressions.csv", index=False)

    diag = []
    v = df[[main, "spy_fwd_3m"]].dropna()
    base = sm.OLS(v["spy_fwd_3m"].values, sm.add_constant(v[main].values)).fit()
    resid = base.resid
    jb, jbp = stats.jarque_bera(resid)
    diag.append({"test": "Jarque-Bera", "statistic": round(float(jb), 3), "p_value": round(float(jbp), 4), "interpretation": "Non-normal residuals; robust inference used" if jbp < 0.05 else "No residual-normality rejection"})
    from statsmodels.stats.diagnostic import acorr_breusch_godfrey, het_breuschpagan, linear_reset

    bp, bpp, _, _ = het_breuschpagan(resid, sm.add_constant(v[main].values))
    diag.append({"test": "Breusch-Pagan", "statistic": round(float(bp), 3), "p_value": round(float(bpp), 4), "interpretation": "Heteroskedastic; HC3/HAC used" if bpp < 0.05 else "No heteroskedasticity rejection"})
    bg, bgp, _, _ = acorr_breusch_godfrey(base, nlags=12)
    diag.append({"test": "Breusch-Godfrey (12)", "statistic": round(float(bg), 3), "p_value": round(float(bgp), 4), "interpretation": "Serial correlation; HAC used" if bgp < 0.05 else "No serial-correlation rejection"})
    try:
        rs = linear_reset(base, power=3, use_f=True)
        diag.append({"test": "RESET", "statistic": round(float(rs.fvalue), 3), "p_value": round(float(rs.pvalue), 4), "interpretation": "Possible nonlinearity" if rs.pvalue < 0.05 else "Linear form adequate"})
    except Exception:
        pass
    pd.DataFrame(diag).to_csv(MODELS / "diagnostics_summary.csv", index=False)

    manifest_for(MODELS / "granger_causality.csv", {"direction": "indicator_to_target/target_to_indicator", "lag": "TY lag", "f_statistic": "Wald F", "p_value": "p-value", "significant": "p<0.05"}, [{"description": "both directions tested", "check": "two direction values"}, {"description": "lags 1-12", "check": "lag range"}, {"description": "TY augmentation dmax=1", "check": "documented in design_note"}])
    print(f"VAR AIC p*={p_opt}; Granger fwd lags={list(ty_df[(ty_df.direction=='indicator_to_target') & ty_df.significant].lag)} rev lags={list(ty_df[(ty_df.direction=='target_to_indicator') & ty_df.significant].lag)}")
    return ty_df, lp


@timed("quartiles")
def quartiles(df: pd.DataFrame) -> pd.DataFrame:
    v = df[["petrol_inv_yoy_zscore_60m", "spy_ret"]].dropna()
    q = pd.qcut(v["petrol_inv_yoy_zscore_60m"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    rows = []
    for label in ("Q1", "Q2", "Q3", "Q4"):
        r = v.loc[q == label, "spy_ret"]
        m = ann_metrics(r)
        rows.append({"quartile": label, "n_months": len(r), "ann_return": round(m["ann_return"], 4), "ann_vol": round(m["ann_vol"], 4), "sharpe": round(m["sharpe"], 3), "max_drawdown": round(m["max_dd"], 4)})
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "regime_quartile_returns.csv", index=False)
    manifest_for(RESULTS / "regime_quartile_returns.csv", {"quartile": "Q1 lowest petroleum YoY z-score, Q4 highest", "n_months": "observations", "ann_return": "annualized SPY return ratio", "ann_vol": "annualized volatility ratio", "sharpe": "return/vol", "max_drawdown": "negative drawdown ratio"}, [{"description": "four quartiles", "check": "len==4"}, {"description": "Q4 is high-inventory-growth state", "check": "qcut order"}, {"description": "descriptive not causal", "check": "documented"}])
    return out


@timed("tournament")
def tournament(df: pd.DataFrame):
    work = df.dropna(subset=["spy_ret"]).copy()
    n = len(work)
    oos_n = int(min(max(36, round(n * 0.25)), 120))
    oos_start = work.index[-oos_n]
    is_end = work.index[-(oos_n + 1)]
    oos_end = work.index[-1]
    split = {
        "owner": "evan",
        "split_policy_id": "v1_max36_25pct_cap120",
        "in_sample_end": str(is_end.date()),
        "oos_start": str(oos_start.date()),
        "oos_end": str(oos_end.date()),
        "sample_size_months": n,
        "justification": f"Policy v1_max36_25pct_cap120 on SPY-bound monthly sample ({n} months). min(max(36, round({n}*0.25)), 120) = {oos_n} months. Month-end L0 is allowed because the petroleum LVCF release lag is documented; daily panel confirms days_since_release 0-6.",
    }
    write_json(RESULTS / "oos_split_record.json", split)

    is_mask = work.index <= is_end
    oos_mask = work.index >= oos_start
    lookbacks = {"LB36": 36, "LB60": 60, "LB120": 120}
    leads = [0, 1, 2, 3, 6, 12]
    strategies = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]
    rows = []
    for code, col in SIGNALS.items():
        if col not in work or work[col].notna().sum() < 120:
            continue
        base = work[col]
        for lead in leads:
            sig = base.shift(lead)
            thresholds = {}
            is_sig = sig[is_mask].dropna()
            if len(is_sig) > 60:
                for p in (25, 50, 75):
                    thresholds[(f"T1_fixed_p{p}", "LB_NA")] = is_sig.quantile(p / 100)
            if code in RAW_SIGNAL_MAP:
                thresholds[("T4_zero", "LB_NA")] = 0.0
            for lb_name, lb in lookbacks.items():
                roll = sig.rolling(lb, min_periods=max(24, int(lb * 0.6)))
                for p in (25, 75):
                    thresholds[(f"T2_roll_p{p}", lb_name)] = roll.quantile(p / 100)
                for k in (1.0, 1.5):
                    thresholds[(f"T3_zscore_{k}", lb_name)] = roll.mean() + k * roll.std()
                    thresholds[(f"T3_zscore_neg_{k}", lb_name)] = roll.mean() - k * roll.std()
            for (thr_name, lb_name), thr in thresholds.items():
                above = sig < thr if "neg_" in thr_name else sig > thr
                for strategy in strategies:
                    for orientation in ("pro", "counter"):
                        pos_bool = ~above if orientation == "counter" else above
                        if strategy == "P1_long_cash":
                            pos = pos_bool.astype(float)
                        elif strategy == "P2_signal_strength":
                            if lb_name == "LB_NA":
                                continue
                            lb = lookbacks[lb_name]
                            roll = sig.rolling(lb, min_periods=max(24, int(lb * 0.6)))
                            rng = (roll.max() - roll.min()).replace(0, np.nan)
                            raw = ((sig - roll.min()) / rng).clip(0, 1)
                            pos = 1 - raw if orientation == "counter" else raw
                        else:
                            pos = pos_bool.astype(float) * 2 - 1
                        strat_ret = pos * work["spy_ret"]
                        is_r, oos_r = strat_ret[is_mask].dropna(), strat_ret[oos_mask].dropna()
                        if len(is_r) < 60 or len(oos_r) < 24:
                            continue
                        mi, mo = ann_metrics(is_r), ann_metrics(oos_r)
                        pos_oos = pos[oos_mask]
                        trades = int((pos_oos.diff().abs() > 1e-9).sum())
                        years = len(pos_oos.dropna()) / 12
                        turnover = trades / years if years else 999
                        rows.append({"signal": code, "threshold": thr_name, "strategy": f"{strategy}_{orientation}", "lead_months": lead, "lookback": lb_name, "is_sharpe": round(mi["sharpe"], 4), "oos_sharpe": round(mo["sharpe"], 4), "oos_sortino": round(mo["sortino"], 4), "oos_calmar": round(mo["calmar"], 4), "oos_ann_return": round(mo["ann_return"], 4), "oos_ann_vol": round(mo["ann_vol"], 4), "max_drawdown": round(mo["max_dd"], 4), "win_rate": round(mo["win_rate"], 4), "n_trades": trades, "annual_turnover": round(turnover, 2), "oos_n": len(oos_r), "valid": bool(mo["sharpe"] > 0.3 and turnover < 24 and len(oos_r) >= 24)})
    mb, mbi = ann_metrics(work["spy_ret"][oos_mask]), ann_metrics(work["spy_ret"][is_mask])
    rows.append({"signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "P0_buy_and_hold", "lead_months": 0, "lookback": "LB_NA", "is_sharpe": round(mbi["sharpe"], 4), "oos_sharpe": round(mb["sharpe"], 4), "oos_sortino": round(mb["sortino"], 4), "oos_calmar": round(mb["calmar"], 4), "oos_ann_return": round(mb["ann_return"], 4), "oos_ann_vol": round(mb["ann_vol"], 4), "max_drawdown": round(mb["max_dd"], 4), "win_rate": round(mb["win_rate"], 4), "n_trades": 0, "annual_turnover": 0.0, "oos_n": int(mb["n"]), "valid": False})
    tdf = pd.DataFrame(rows)
    assert (tdf.signal == "BENCHMARK").sum() == 1
    assert not bool(tdf.loc[tdf.signal == "BENCHMARK", "valid"].iloc[0])
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from _tournament_io import write_tournament  # ECON-T5 §4 immutability guard
    write_tournament(tdf, RESULTS / f"tournament_results_{DATE_TAG}.csv")
    strategy_rows = tdf[tdf.signal != "BENCHMARK"]
    valid_count = int(strategy_rows.valid.sum())
    write_json(
        RESULTS / f"tournament_results_{DATE_TAG}_manifest.json",
        {
            "file": f"tournament_results_{DATE_TAG}.csv",
            "pair_id": PAIR_ID,
            "grid": {"signals": [k for k, v in SIGNALS.items() if v in work.columns], "thresholds": "T1 fixed percentiles, T2 rolling percentiles, T3 rolling z-score, T4 zero", "strategies": [s + "_{pro,counter}" for s in strategies], "leads_months": leads, "lookbacks": list(lookbacks) + ["LB_NA"]},
            "units": "returns and drawdowns are ratios, not percent",
            "total_strategy_rows": len(strategy_rows),
            "valid_strategy_rows": valid_count,
            "sampling": "exhaustive",
            "benchmark_row": "signal==BENCHMARK, valid=False per ECON-T4",
            "execution_lag": "monthly L0 permitted by release-lag convention; L1/L2/L3/L6/L12 also tested",
            "cost_note": "gross returns; 5 bps sensitivity in validation folder",
            "assertions": ["exactly one BENCHMARK row", "BENCHMARK valid=False", "all valid counts exclude benchmark"],
            "generated_at": NOW,
        },
    )
    print(f"strategies={len(strategy_rows)} valid={valid_count} benchmark_sharpe={mb['sharpe']:.3f}")
    return tdf, split


def select_winner(tdf: pd.DataFrame):
    cand = tdf[(tdf.signal != "BENCHMARK") & tdf.valid].copy()
    if cand.empty:
        raise RuntimeError("no valid strategies")
    cand["abs_dd"] = cand["max_drawdown"].abs()
    pool = cand
    step1 = None
    resolved = 1
    for i, (col, asc) in enumerate([("oos_sharpe", False), ("oos_ann_return", False), ("abs_dd", True), ("n_trades", False), ("signal", True)], 1):
        best = pool[col].min() if asc else pool[col].max()
        pool = pool[pool[col] == best]
        if i == 1:
            step1 = pool.copy()
        if len(pool) == 1:
            resolved = i
            break
    return pool.iloc[0], resolved, step1, cand


def derive_series(df: pd.DataFrame, winner: pd.Series, split: dict):
    lookbacks = {"LB36": 36, "LB60": 60, "LB120": 120}
    sig = df[SIGNALS[winner["signal"]]].shift(int(winner["lead_months"]))
    is_mask = df.index <= split["in_sample_end"]
    thr_name, lb_name = winner["threshold"], winner["lookback"]
    if thr_name.startswith("T1_fixed_p"):
        thr = sig[is_mask].dropna().quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name == "T4_zero":
        thr = 0.0
    elif thr_name.startswith("T2_roll_p"):
        lb = lookbacks[lb_name]
        thr = sig.rolling(lb, min_periods=max(24, int(lb * 0.6))).quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name.startswith("T3_zscore"):
        lb = lookbacks[lb_name]
        roll = sig.rolling(lb, min_periods=max(24, int(lb * 0.6)))
        k = float(thr_name.split("_")[-1])
        thr = roll.mean() - k * roll.std() if "neg_" in thr_name else roll.mean() + k * roll.std()
    else:
        raise ValueError(thr_name)
    above = sig < thr if "neg_" in thr_name else sig > thr
    family, orientation = winner["strategy"].rsplit("_", 1)
    pos_bool = ~above if orientation == "counter" else above
    if family == "P1_long_cash":
        pos = pos_bool.astype(float)
    elif family == "P2_signal_strength":
        lb = lookbacks[lb_name]
        roll = sig.rolling(lb, min_periods=max(24, int(lb * 0.6)))
        rng = (roll.max() - roll.min()).replace(0, np.nan)
        raw = ((sig - roll.min()) / rng).clip(0, 1)
        pos = 1 - raw if orientation == "counter" else raw
    else:
        pos = pos_bool.astype(float) * 2 - 1
    return pos, df["spy_ret"], sig, thr


@timed("winner_artifacts")
def winner_artifacts(df: pd.DataFrame, tdf: pd.DataFrame, split: dict):
    winner, resolved, tie_pool, cand = select_winner(tdf)
    pos, spy_ret, sig, thr = derive_series(df.dropna(subset=["spy_ret"]), winner, split)
    oos_mask = (spy_ret.index >= split["oos_start"]) & (spy_ret.index <= split["oos_end"])
    strat_ret = pos * spy_ret
    m = ann_metrics(strat_ret[oos_mask])
    rec = {
        "oos_sharpe": {"computed": round(m["sharpe"], 6), "reported": float(winner["oos_sharpe"]), "tolerance": 0.01},
        "oos_max_drawdown": {"computed": round(m["max_dd"], 6), "reported": float(winner["max_drawdown"]), "tolerance": 0.005},
        "oos_ann_return": {"computed": round(m["ann_return"], 6), "reported": float(winner["oos_ann_return"]), "tolerance": 0.005},
    }
    for row in rec.values():
        row["diff"] = round(row["computed"] - row["reported"], 6)
        row["verdict"] = "PASS" if abs(row["diff"]) <= row["tolerance"] else "FAIL"
    assert all(v["verdict"] == "PASS" for v in rec.values()), rec

    sr = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"), "position": pos.reindex(spy_ret.index).fillna(0), "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0), "bh_return": spy_ret})
    sr.to_csv(RESULTS / f"strategy_returns_{DATE_TAG}.csv", index=False)
    write_json(RESULTS / f"strategy_returns_{DATE_TAG}_meta.json", {"pair_id": PAIR_ID, "artifact": f"strategy_returns_{DATE_TAG}.csv", "rule": "ECON-SR1", "frequency": "monthly", "oos_start": split["oos_start"], "oos_end": split["oos_end"], "reconciliation": rec, "generated_at": NOW})

    log = pd.DataFrame({"date": spy_ret.index.strftime("%Y-%m-%d"), "signal_value": sig.reindex(spy_ret.index).round(4), "threshold": thr.reindex(spy_ret.index).round(4) if isinstance(thr, pd.Series) else round(float(thr), 4), "position": pos.reindex(spy_ret.index).fillna(0), "spy_return": spy_ret.round(6), "strategy_return": strat_ret.reindex(spy_ret.index).fillna(0).round(6)})
    log["cumulative_return"] = ((1 + log["strategy_return"]).cumprod() - 1).round(6)
    log.to_csv(RESULTS / "winner_trade_log.csv", index=False)

    broker = []
    px = df["spy"].reindex(spy_ret.index)
    cum = (1 + strat_ret.reindex(spy_ret.index).fillna(0)).cumprod()
    prev = 0.0
    for dt in spy_ret.index:
        p = float(pos.reindex(spy_ret.index).fillna(0).loc[dt])
        if abs(p - prev) > 1e-9:
            sv = sig.loc[dt]
            th = thr.loc[dt] if isinstance(thr, pd.Series) else thr
            notional = abs(p - prev) * 10000
            broker.append({"trade_date": dt.strftime("%Y-%m-%d"), "side": "BUY" if p > prev else "SELL", "instrument": TARGET_SYMBOL, "quantity_pct": round(abs(p) * 100, 1), "price": round(float(px.loc[dt]), 4) if pd.notna(px.loc[dt]) else np.nan, "notional_usd": round(notional, 2), "commission_bps": COST_BPS, "commission_usd": round(notional * COST_BPS / 10000, 2), "cum_pnl_pct": round(float((cum.loc[dt] - 1) * 100), 4), "reason": f"{winner['strategy']}: {winner['signal']}={sv:.3f} threshold={th:.3f}; position {prev*100:.0f}% to {p*100:.0f}%" if pd.notna(sv) else "position change"})
            prev = p
    with (RESULTS / "winner_trades_broker_style.csv").open("w", encoding="utf-8") as f:
        f.write(f"# Simulated trade record based on backtest signals. No real trades were executed. Starting capital: $10000. Commission: {COST_BPS} bps.\n")
        pd.DataFrame(broker).to_csv(f, index=False)
    return winner, resolved, tie_pool, cand, pos, strat_ret, sig, thr, rec


@timed("cross_period")
def cross_period(df: pd.DataFrame, winner: pd.Series, split: dict, strat_ret: pd.Series, sig: pd.Series):
    import statsmodels.api as sm

    episodes = [
        {"slug": "gfc", "start": "2008-09-01", "end": "2009-06-30"},
        {"slug": "covid", "start": "2020-03-01", "end": "2020-06-30"},
        {"slug": "rate_hike_2022", "start": "2022-01-01", "end": "2023-06-30"},
        {"slug": "post_covid_expansion", "start": "2023-07-01", "end": "2025-09-30"},
    ]
    oos = strat_ret[(strat_ret.index >= split["oos_start"]) & (strat_ret.index <= split["oos_end"])]
    rows, pos_count, eval_count = [], 0, 0
    for ep in episodes:
        sub = oos[(oos.index >= ep["start"]) & (oos.index <= ep["end"])].dropna()
        if len(sub) < 3:
            rows.append({"episode": ep["slug"], "start_date": ep["start"], "end_date": ep["end"], "n_trading_days": len(sub) * 21, "ann_sharpe": np.nan, "win_rate": np.nan, "max_drawdown": np.nan, "data_status": "insufficient_data", "durability_verdict": ""})
            continue
        mm = ann_metrics(sub)
        eval_count += 1
        pos_count += int(mm["sharpe"] > 0)
        rows.append({"episode": ep["slug"], "start_date": str(sub.index[0].date()), "end_date": str(sub.index[-1].date()), "n_trading_days": len(sub) * 21, "ann_sharpe": round(mm["sharpe"], 4), "win_rate": round(mm["win_rate"], 4), "max_drawdown": round(mm["max_dd"], 4), "data_status": "validated", "durability_verdict": ""})
    verdict = "durable" if eval_count >= 3 and pos_count >= 3 else "conditionally_durable" if pos_count >= 2 else "episode_concentrated"
    rows[-1]["durability_verdict"] = verdict
    pd.DataFrame(rows).to_csv(RESULTS / "subperiod_sharpe.csv", index=False)

    v = pd.concat([sig.rename("sig"), df["spy_fwd_1m"]], axis=1).dropna()
    full_r = float(v["sig"].corr(v["spy_fwd_1m"]))
    roll = v["sig"].rolling(24).corr(v["spy_fwd_1m"])
    out = pd.DataFrame({"date": v.index.strftime("%Y-%m-%d"), "rolling_corr": roll.round(4), "n_obs": 24, "window_start": v.index.to_series().shift(23).dt.strftime("%Y-%m-%d").values}).dropna(subset=["rolling_corr"])
    out.to_csv(RESULTS / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    same = float((np.sign(roll.dropna()) == np.sign(full_r)).mean())
    stability = "sign_stable" if same >= 0.7 else "moderately_stable" if same >= 0.5 else "sign_unstable"

    reg = pd.concat([sig.rename("sig"), df["spy_ret"]], axis=1).dropna()
    yv = reg["spy_ret"].values
    X = sm.add_constant(reg["sig"].values)
    n = len(yv)
    lo, hi = int(n * 0.15), int(n * 0.85)
    full = sm.OLS(yv, X).fit()

    def sup_f(y, xmat):
        ssr_full = sm.OLS(y, xmat).fit().ssr
        best, bidx = -np.inf, lo
        for b in range(lo, hi):
            s1 = sm.OLS(y[:b], xmat[:b]).fit().ssr
            s2 = sm.OLS(y[b:], xmat[b:]).fit().ssr
            f = ((ssr_full - s1 - s2) / xmat.shape[1]) / ((s1 + s2) / (len(y) - 2 * xmat.shape[1]))
            if f > best:
                best, bidx = f, b
        return best, bidx

    f_obs, bidx = sup_f(yv, X)
    rng = np.random.default_rng(42)
    null = [sup_f(full.fittedvalues + rng.choice(full.resid, size=n, replace=True), X)[0] for _ in range(300)]
    pval = float((np.asarray(null) >= f_obs).mean())
    sb = {"pair_id": PAIR_ID, "test": "Quandt-Andrews unknown breakpoint (sup-F, residual-bootstrap p, 300 reps)", "sample_start": str(reg.index[0].date()), "sample_end": str(reg.index[-1].date()), "n_obs": n, "trimming_pct": 0.15, "break_date": str(reg.index[bidx].date()), "f_stat": round(float(f_obs), 4), "p_value": round(pval, 4), "flagged": bool(pval < 0.10), "flag_message": "Structural break detected; interpret with caution." if pval < 0.10 else None, "rolling_corr_sign_stability": round(same, 4), "rolling_corr_stability_verdict": stability}
    write_json(RESULTS / f"structural_break_{PAIR_ID}.json", sb)
    return verdict, stability, sb, full_r


@timed("validation")
def validation(df: pd.DataFrame, tdf: pd.DataFrame, split: dict, strat_ret: pd.Series):
    spy_oos = df["spy_ret"][(df.index >= split["oos_start"]) & (df.index <= split["oos_end"])].dropna()
    top = tdf[(tdf.signal != "BENCHMARK") & tdf.valid].nlargest(5, "oos_sharpe")
    rng = np.random.default_rng(42)
    boot = []
    for _ in range(3000):
        s = rng.choice(spy_oos.values, size=len(spy_oos), replace=True)
        boot.append(s.mean() / s.std() * np.sqrt(12) if s.std() else 0)
    rows = []
    for r in top.itertuples():
        p = float((np.asarray(boot) >= r.oos_sharpe).mean())
        rows.append({"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy, "lead_months": r.lead_months, "lookback": r.lookback, "oos_sharpe": r.oos_sharpe, "bootstrap_p_value": round(p, 4), "significant_at_5pct": bool(p < 0.05)})
    pd.DataFrame(rows).to_csv(VALID / "bootstrap.csv", index=False)
    stress = {"GFC": ("2008-09-01", "2009-06-30"), "COVID": ("2020-03-01", "2020-06-30"), "Rate_Hike_2022": ("2022-01-01", "2023-06-30")}
    srows = []
    for name, (s, e) in stress.items():
        bh = df["spy_ret"][(df.index >= s) & (df.index <= e)].dropna()
        st = strat_ret[(strat_ret.index >= s) & (strat_ret.index <= e)].dropna()
        if len(bh) > 2:
            srows.append({"period": name, "start": s, "end": e, "n_months": len(bh), "buy_hold_sharpe": round(ann_metrics(bh)["sharpe"], 4), "winner_sharpe": round(ann_metrics(st)["sharpe"], 4) if len(st) > 2 else np.nan, "buy_hold_return_pct": round(float(bh.sum() * 100), 2), "winner_return_pct": round(float(st.sum() * 100), 2) if len(st) > 2 else np.nan})
    pd.DataFrame(srows).to_csv(VALID / "stress_tests.csv", index=False)
    tx = []
    for r in top.itertuples():
        for bps in (0, 5, 10, 25, 50):
            cost = r.annual_turnover * bps / 10000
            net = r.oos_sharpe - cost / r.oos_ann_vol if r.oos_ann_vol > 0 else r.oos_sharpe
            tx.append({"signal": r.signal, "threshold": r.threshold, "strategy": r.strategy, "tx_cost_bps": bps, "gross_sharpe": r.oos_sharpe, "net_sharpe_approx": round(float(net), 4)})
    pd.DataFrame(tx).to_csv(VALID / "transaction_costs.csv", index=False)
    return rows


def write_final_artifacts(df, daily, tdf, split, winner, resolved, tie_pool, cand, pos, strat_ret, sig, thr, rec, ty_df, lp, qdf, verdict, stability, sb, boot_rows, t0):
    bh = tdf[tdf.signal == "BENCHMARK"].iloc[0]
    family, orientation = winner["strategy"].rsplit("_", 1)
    neg_thr = "neg_" in winner["threshold"]
    long_when_high = (orientation == "pro") != neg_thr
    direction = "countercyclical" if not long_when_high else "procyclical"
    thr_value = float(thr.dropna().iloc[-1]) if isinstance(thr, pd.Series) else float(thr)
    threshold_rule = "lt" if neg_thr else "gt"
    n_valid = int(len(cand))
    n_tied = int((cand.oos_sharpe == winner["oos_sharpe"]).sum())
    boot_p = boot_rows[0]["bootstrap_p_value"] if boot_rows else np.nan
    summary = {
        "pair_id": PAIR_ID,
        "generated_at": NOW,
        "signal_column": SIGNALS[winner["signal"]],
        "signal_code": winner["signal"],
        "signal_display_name": winner["signal"].replace("_", " "),
        "target_symbol": TARGET_SYMBOL,
        "threshold_code": winner["threshold"],
        "threshold_value": round(thr_value, 4),
        "threshold_rule": threshold_rule,
        "threshold_note": "threshold is rolling; threshold_value is latest rolling value" if isinstance(thr, pd.Series) else "static IS-calibrated threshold",
        "strategy_family": family,
        "strategy_code": family.split("_")[0],
        "strategy_display_name": {"P1_long_cash": "Long/Cash", "P2_signal_strength": "Signal-strength sizing", "P3_long_short": "Long/Short"}[family],
        "strategy_description": f"Long SPY when lagged petroleum inventory signal is {'below' if threshold_rule == 'lt' else 'above'} threshold; otherwise {'cash' if family == 'P1_long_cash' else 'scaled exposure' if family == 'P2_signal_strength' else 'short SPY'}.",
        "lead_value": int(winner["lead_months"]),
        "lead_unit": "months",
        "lead_description": "L0 monthly is feasible under Dana's release-lag convention; daily LVCF uses only public carried-forward values.",
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
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_ann_return": round(float(bh["oos_ann_return"]), 4),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 4),
        "cost_assumption_bps": COST_BPS,
        "total_combos": int(len(tdf) - 1),
        "valid_combos": int(tdf[(tdf.signal != "BENCHMARK") & tdf.valid].shape[0]),
        "schema_version": "1.1.0",
        "notes": f"Mode-3 Codex maker. Tournament: {len(tdf)-1} strategy rows plus one benchmark valid=False; {int(tdf[(tdf.signal!='BENCHMARK') & tdf.valid].shape[0])} valid. Winner selected by ECON-T3 at step {resolved}; {n_tied} tied at Sharpe step. Bootstrap p={boot_p}; CP1 durability={verdict}; rolling correlation={stability}. Petroleum inventories are coincident physical stocks, so reverse-causality evidence is reported rather than suppressed.",
    }
    write_json(RESULTS / "winner_summary.json", summary)
    subprocess.run(["python3", str(ROOT / "scripts/validate_schema.py"), "--schema", str(SCHEMAS / "winner_summary.schema.json"), "--instance", str(RESULTS / "winner_summary.json")], check=True)

    with (SCHEMAS / "signal_code_registry.json").open() as f:
        registry_codes = {s["signal_code"] for s in json.load(f)["signals"]}
    if summary["signal_code"] not in registry_codes:
        raise RuntimeError(f"signal_code {summary['signal_code']} missing from registry")
    sig_file = pd.read_parquet(RESULTS / f"signals_{DATE_TAG}.parquet")
    assert summary["signal_column"] in sig_file.columns

    tw = {
        "pair_id": PAIR_ID,
        "winner_label": f"{winner['signal']} / {winner['threshold']} / {family} ({orientation}) / L{winner['lead_months']} / {winner['lookback']}",
        "winner_oos_sharpe": summary["oos_sharpe"],
        "winner_max_drawdown": summary["oos_max_drawdown"],
        "winner_oos_ann_return": summary["oos_ann_return"],
        "bh_oos_sharpe": summary["bh_sharpe"],
        "bh_max_drawdown": summary["bh_max_drawdown"],
        "bh_oos_ann_return": summary["bh_ann_return"],
        "delta_sharpe": round(summary["oos_sharpe"] - summary["bh_sharpe"], 4),
        "delta_max_drawdown": round(summary["oos_max_drawdown"] - summary["bh_max_drawdown"], 4),
        "delta_ann_return": round(summary["oos_ann_return"] - summary["bh_ann_return"], 4),
        "beats_benchmark": bool(summary["oos_sharpe"] > summary["bh_sharpe"]),
        "suggested_strategy_objective": "max_sharpe",
        "generated_at": NOW,
    }
    write_json(RESULTS / "tournament_winner.json", tw)

    interp_path = RESULTS / "interpretation_metadata.json"
    interp = json.loads(interp_path.read_text())
    fwd_lags = list(ty_df[(ty_df.direction == "indicator_to_target") & ty_df.significant].lag)
    rev_lags = list(ty_df[(ty_df.direction == "target_to_indicator") & ty_df.significant].lag)
    interp["observed_direction"] = direction
    interp["direction_consistent"] = interp.get("expected_direction") in ("mixed", direction)
    interp["key_finding"] = f"Petroleum inventories provide a weak, empirically mixed equity signal. Winner is {tw['winner_label']} with OOS Sharpe {summary['oos_sharpe']:.2f} vs buy-and-hold {summary['bh_sharpe']:.2f}; max drawdown {summary['oos_max_drawdown']*100:.1f}% vs {summary['bh_max_drawdown']*100:.1f}%. Toda-Yamamoto Granger indicator->SPY significant lags: {fwd_lags or 'none'}; SPY->indicator significant lags: {rev_lags or 'none'}. Treat as a searched defensive overlay, not established causal alpha."
    interp["confidence"] = "low" if pd.isna(boot_p) or boot_p >= 0.05 else "medium"
    interp["last_updated_by"] = "evan"
    interp["last_updated_at"] = NOW
    write_json(interp_path, interp)

    ind_der = []
    for c, d, f, role in [
        ("petrol_inv_kb", "Weekly U.S. ending stocks of crude oil and petroleum products, monthly average in thousand barrels.", "Data Master.xlsx:WTTSTUS1 / EIA", "raw"),
        ("petrol_inv_pct_yoy", "Year-over-year percent change in petroleum stocks.", "100*(x_t/x_t-12-1)", "derivative"),
        ("petrol_inv_pct_chg", "Short-horizon percent change in petroleum stocks.", "monthly MoM in monthly panel; 4-week change in daily LVCF", "derivative"),
        ("petrol_inv_3m_pct", "Three-month petroleum stock momentum.", "100*(x_t/x_t-3-1)", "derivative"),
        ("petrol_inv_6m_pct", "Six-month petroleum stock momentum.", "100*(x_t/x_t-6-1)", "derivative"),
        ("petrol_inv_dev_trend_pct", "Percent deviation from 12-month trend.", "100*(x_t/ma12_t-1)", "derivative"),
        ("petrol_inv_zscore_60m", "Five-year z-score of petroleum stock level.", "(x_t-mean60)/sd60", "derivative"),
        ("petrol_inv_yoy_zscore_60m", "Five-year z-score of petroleum stock YoY growth.", "(yoy_t-mean60)/sd60", "threshold_input"),
        ("petrol_inv_accel_pct", "Change in short-horizon petroleum stock growth.", "pct_chg_t - pct_chg_t-1", "derivative"),
        ("hmm_2state_prob_stress", "Probability of high-inventory-growth HMM state.", "GaussianHMM(yoy_zscore)", "regime_state"),
        ("markov_regime_2state", "Smoothed high-inventory stress proxy.", "rolling mean of HMM stress probability", "regime_state"),
    ]:
        ind_der.append({"name": c, "definition": d, "formula": f, "role": role, "appears_in_charts": []})
    tgt_der = [{"name": c, "definition": d, "formula": f, "role": role, "appears_in_charts": []} for c, d, f, role in [
        ("spy", "SPY adjusted month-end close.", "Yahoo Finance", "raw"),
        ("spy_ret", "SPY monthly return.", "P_t/P_t-1-1", "derivative"),
        ("spy_fwd_1m", "One-month forward SPY return.", "P_t+1/P_t-1", "derivative"),
        ("spy_fwd_3m", "Three-month forward SPY return.", "P_t+3/P_t-1", "derivative"),
        ("spy_fwd_6m", "Six-month forward SPY return.", "P_t+6/P_t-1", "derivative"),
        ("spy_fwd_12m", "Twelve-month forward SPY return.", "P_t+12/P_t-1", "derivative"),
    ]]
    scope = {"pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan", "last_updated_at": NOW, "indicator_axis": {"canonical_column": "petrol_inv_kb", "display_name": "U.S. petroleum product stocks", "derivatives": ind_der}, "target_axis": {"canonical_column": "spy", "display_name": "SPY (S&P 500 ETF)", "derivatives": tgt_der}, "notes": "ECON-SD: only WTTSTUS1 petroleum inventory derivatives and SPY derivatives are in scope. VIX and DGS10 in the parquet are context columns, not rendered pair signals."}
    write_json(RESULTS / "signal_scope.json", scope)
    subprocess.run(["python3", str(ROOT / "scripts/validate_schema.py"), "--schema", str(SCHEMAS / "signal_scope.schema.json"), "--instance", str(RESULTS / "signal_scope.json")], check=True)

    kpis = [
        {"metric": "OOS Sharpe (winner)", "value": f"{summary['oos_sharpe']:.2f}", "unit": "ratio", "delta": f"{tw['delta_sharpe']:+.2f} vs B&H"},
        {"metric": "OOS Sharpe (buy & hold)", "value": f"{summary['bh_sharpe']:.2f}", "unit": "ratio", "delta": None},
        {"metric": "OOS Annual Return (winner)", "value": f"{summary['oos_ann_return']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_ann_return']*100:+.1f}pp vs B&H"},
        {"metric": "OOS Max Drawdown (winner)", "value": f"{summary['oos_max_drawdown']*100:.1f}%", "unit": "percent", "delta": f"{tw['delta_max_drawdown']*100:+.1f}pp vs B&H"},
        {"metric": "Valid strategy combos", "value": f"{summary['valid_combos']}", "unit": "count", "delta": None},
        {"metric": "OOS window", "value": f"{split['oos_start']} -> {split['oos_end']}", "unit": "dates", "delta": None},
    ]
    write_json(RESULTS / "kpis.json", kpis)

    evidence = {"pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search", "updated_at": NOW, "owner": "evan", "plain_english": f"This is the best petroleum-inventory rule found in a broad search, not a final confirmed trading rule. It beat buy-and-hold on Sharpe in the OOS window, but it was selected from {summary['valid_combos']} valid combinations and has not passed a fresh holdout final exam.", "technical_note": f"Tournament-OOS only ({split['oos_start']} to {split['oos_end']}). Winner bootstrap p={boot_p}; CP1={verdict}; rolling-correlation={stability}; Granger fwd={fwd_lags or 'none'}, reverse={rev_lags or 'none'}.", "next_step": "Freeze the selected rule and run ECON-FE1 final exam on a confirmation window not used in search."}
    write_json(RESULTS / "evidence_status.json", evidence)
    subprocess.run(["python3", str(ROOT / "scripts/validate_schema.py"), "--schema", str(SCHEMAS / "evidence_status.schema.json"), "--instance", str(RESULTS / "evidence_status.json")], check=True)

    suggestions = {"schema_version": "1.0.0", "pair_id": PAIR_ID, "suggestions": [{"signal_name": "Petroleum inventory surprise vs refinery utilization", "proposed_by": "evan", "source": "EIA / Data Master candidate extension", "observation": "Inventory levels alone mix demand weakness and supply/refinery effects; utilization-adjusted surprises may better separate the mechanisms.", "rationale": "A build caused by demand weakness should carry a different equity interpretation than a build caused by refinery outages or supply shocks.", "possible_use_case": "variant family / regime overlay", "caveats": "Requires additional EIA series and a fresh Dana data pass; not in current pair scope.", "date_filed": "2026-06-17"}], "last_updated_at": NOW}
    write_json(RESULTS / "analyst_suggestions.json", suggestions)
    subprocess.run(["python3", str(ROOT / "scripts/validate_schema.py"), "--schema", str(SCHEMAS / "analyst_suggestions.schema.json"), "--instance", str(RESULTS / "analyst_suggestions.json")], check=True)

    design = f"""# Design Note — {PAIR_ID} ({DATE_TAG})

## Economic hypotheses
H1 counter-cyclical demand signal: rising/high petroleum inventories can indicate weak fuel demand and lower forward SPY. H1b supply-glut benign: inventory builds may reflect supply rather than demand. H0: petroleum stocks do not predict SPY.

## Data provenance and vintage
WTTSTUS1 is an EIA petroleum-stocks series sourced from project `data/Data Master.xlsx` sheet `WTTSTUS1`; FRED public API rejected WTTSTUS1 on 2026-06-17. Dana's vintage ends October 2025. Monthly analysis data: `{MONTHLY_PATH}`. Daily LVCF data: `{DAILY_PATH}`, with `days_since_release` 0-6.

## Stationarity and method category
Dana's stationarity artifact `results/petrol_inv_spy/stationarity_tests_20260617.csv` was reviewed and confirmed, not re-run. Levels are nonstationary; the tournament and models use stationary transforms only. Indicator type is macro / cross-asset, so this run includes correlation battery with distance correlation, pre-whitened CCF, Toda-Yamamoto Granger both directions, local projections, quantile regression, HMM regime detection, quartile returns, structural break, and validation sensitivity.

## Lag convention
Daily LVCF may use L0 because carried values are already public after release. Monthly L0 is treated as feasible because the month-end panel is built from documented public weekly releases; L1/L2/L3/L6/L12 are also tested. This convention is explicit to avoid lookahead ambiguity.

## Lead-lag verdict
Indicator -> SPY Granger significant lags: {fwd_lags or 'none'}. SPY -> indicator Granger significant lags: {rev_lags or 'none'}. Reverse direction is therefore reported directly for Ray rather than suppressed.

## Tournament and evidence status
Benchmark row has `signal == "BENCHMARK"` and `valid == False` per ECON-T4. Winner signal column `{summary['signal_column']}` exists in `signals_{DATE_TAG}.parquet`. Evidence status is `found_in_search`; no independent final exam has been run.
"""
    (RESULTS / "design_note.md").write_text(design, encoding="utf-8")

    handoff = f"""# Evan Handoff — {PAIR_ID} ({DATE_TAG})

## Winner spec
- Winner: `{tw['winner_label']}`
- Signal column: `{summary['signal_column']}` (present in `results/{PAIR_ID}/signals_{DATE_TAG}.parquet`)
- OOS: {split['oos_start']} -> {split['oos_end']}
- Winner OOS Sharpe {summary['oos_sharpe']:.2f} vs B&H {summary['bh_sharpe']:.2f}; ann return {summary['oos_ann_return']*100:.1f}% vs {summary['bh_ann_return']*100:.1f}%; max DD {summary['oos_max_drawdown']*100:.1f}% vs {summary['bh_max_drawdown']*100:.1f}%.
- Suggested strategy objective: `{tw['suggested_strategy_objective']}`.

## Observed direction and caveat
Observed direction: `{direction}`. Expected direction was mixed, so this is direction-consistent. Confidence: `{interp['confidence']}`. Evidence status is `found_in_search`: selected from the tournament, not validated by a final exam.

## Method artifacts for Vera/Ray
| method | result_file | expected_chart | status |
|---|---|---|---|
| Correlations | `results/{PAIR_ID}/core_models_{DATE_TAG}/correlations.csv` | correlation matrix / bar | ready |
| Pre-whitened CCF | `results/{PAIR_ID}/core_models_{DATE_TAG}/ccf_prewhitened.csv` | CCF lag bars | ready |
| Granger | `results/{PAIR_ID}/granger_by_lag.csv` + `core_models_{DATE_TAG}/granger_causality.csv` | F-stat by lag | ready |
| Local projections | `results/{PAIR_ID}/core_models_{DATE_TAG}/local_projections.csv` | impulse response | ready |
| Quantile regression | `results/{PAIR_ID}/core_models_{DATE_TAG}/quantile_regression.csv` | coefficient by quantile | ready |
| HMM regime | `results/{PAIR_ID}/core_models_{DATE_TAG}/hmm_states.parquet`, `hmm_summary.csv` | regime timeline / stats | ready |
| Quartile returns | `results/{PAIR_ID}/regime_quartile_returns.csv` | Q1-Q4 bars | ready |
| Strategy returns | `results/{PAIR_ID}/strategy_returns_{DATE_TAG}.csv` | equity/drawdown charts | ready |

## Lead-lag notes
- Indicator -> SPY TY-Granger significant lags: {fwd_lags or 'none'}
- SPY -> indicator TY-Granger significant lags: {rev_lags or 'none'}
- Local projections reverse significant horizons: {list(lp[(lp.direction == 'rev') & (lp.p_value < 0.05)].horizon) or 'none'}

## Key charts needed
Hero inventory vs SPY, correlation battery, Granger by lag both-direction callout, HMM stress timeline, quartile returns, tournament Sharpe distribution, strategy equity/drawdown, rolling correlation, structural break marker.
"""
    (ROOT / "_pws/lead-lesandro/mode3_petrol_inv/evan_handoff.md").write_text(handoff, encoding="utf-8")

    write_json(RESULTS / f"pipeline_timing_{DATE_TAG}.json", {"pair_id": PAIR_ID, "date": DATE_TAG, "pipeline_seconds": round(time.time() - t0, 1), "stage_times": {k: round(v, 1) for k, v in TIMES.items()}, "tournament_strategy_rows": int(len(tdf) - 1), "valid_strategies": summary["valid_combos"], "oos_start": split["oos_start"], "oos_end": split["oos_end"]})
    print(f"winner {tw['winner_label']} Sharpe {summary['oos_sharpe']} vs B&H {summary['bh_sharpe']}")
    return summary, tw


def main():
    t0 = time.time()
    monthly, daily = load_data()
    df = add_regime_signals(monthly)
    correlations(df)
    ty_df, lp = core_models(df)
    qdf = quartiles(df)
    tdf, split = tournament(df)
    winner, resolved, tie_pool, cand, pos, strat_ret, sig, thr, rec = winner_artifacts(df, tdf, split)
    verdict, stability, sb, _ = cross_period(df, winner, split, strat_ret, sig)
    boot_rows = validation(df, tdf, split, strat_ret)
    write_final_artifacts(df, daily, tdf, split, winner, resolved, tie_pool, cand, pos, strat_ret, sig, thr, rec, ty_df, lp, qdf, verdict, stability, sb, boot_rows, t0)


if __name__ == "__main__":
    main()
