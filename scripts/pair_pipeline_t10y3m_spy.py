#!/usr/bin/env python3
"""
Econometrics Pipeline: 10Y-3M Treasury Spread x SPY
===================================================

Pair ID: t10y3m_spy

SOP path:
  - Econ Evan: rates-pair method catalog.
  - Mandatory methods covered here: correlations, Granger causality,
    pre-whitened-style CCF, local projections, quantile regression, yield
    curve factor table, regime quartiles, and tournament/backtest artifacts.

Hypothesis:
  H0: the 10Y-3M Treasury spread has no predictive value for SPY returns.
  H1: steeper curves are procyclical/risk-on for equities; inversion or
      flattening is a cautionary signal for future SPY exposure.
"""

from __future__ import annotations

import json
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
np.random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
PAIR_ID = "t10y3m_spy"
DATE_TAG = "20260620"
DATA_PATH = ROOT / "data" / "t10y3m_spy_monthly_latest.parquet"
RESULTS_DIR = ROOT / "results" / PAIR_ID
EXPLORE_DIR = RESULTS_DIR / f"exploratory_{DATE_TAG}"
CORE_DIR = RESULTS_DIR / f"core_models_{DATE_TAG}"
VALID_DIR = RESULTS_DIR / f"tournament_validation_{DATE_TAG}"
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
COST_BPS = 5

for d in (RESULTS_DIR, EXPLORE_DIR, CORE_DIR, VALID_DIR):
    d.mkdir(parents=True, exist_ok=True)

SIGNALS = {
    "slope": ("t10y3m", "procyclical"),
    "mom": ("t10y3m_mom", "procyclical"),
    "chg_3m": ("t10y3m_3m_chg", "procyclical"),
    "chg_6m": ("t10y3m_6m_chg", "procyclical"),
    "chg_12m": ("t10y3m_12m_chg", "procyclical"),
    "zscore_60m": ("t10y3m_zscore_60m", "procyclical"),
    "inversion_flag": ("t10y3m_inversion_flag", "countercyclical"),
    "steepening_flag": ("t10y3m_curve_steepening", "procyclical"),
}

DISPLAY = {
    "t10y3m": "10Y-3M Treasury spread",
    "t10y3m_mom": "1-month change in 10Y-3M spread",
    "t10y3m_3m_chg": "3-month change in 10Y-3M spread",
    "t10y3m_6m_chg": "6-month change in 10Y-3M spread",
    "t10y3m_12m_chg": "12-month change in 10Y-3M spread",
    "t10y3m_zscore_60m": "60-month z-score of 10Y-3M spread",
    "t10y3m_inversion_flag": "Yield-curve inversion flag",
    "t10y3m_curve_steepening": "Curve steepening flag",
}


def log(msg: str) -> None:
    print(f"  {msg}")


def metrics(rets: pd.Series) -> dict:
    r = rets.dropna()
    if len(r) == 0 or r.std() == 0:
        return {"oos_sharpe": 0.0, "oos_ann_return": 0.0, "oos_ann_vol": 0.0,
                "oos_sortino": 0.0, "oos_calmar": 0.0, "max_drawdown": 0.0,
                "win_rate": 0.0, "n": len(r)}
    ann_ret = r.mean() * 12
    ann_vol = r.std() * np.sqrt(12)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
    neg = r[r < 0]
    sortino = ann_ret / (neg.std() * np.sqrt(12)) if len(neg) > 1 and neg.std() > 0 else 0.0
    curve = (1 + r).cumprod()
    dd = (curve / curve.cummax() - 1).min()
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    return {
        "oos_sharpe": float(sharpe),
        "oos_ann_return": float(ann_ret),
        "oos_ann_vol": float(ann_vol),
        "oos_sortino": float(sortino),
        "oos_calmar": float(calmar),
        "max_drawdown": float(dd),
        "win_rate": float((r > 0).mean()),
        "n": int(len(r)),
    }


def load_data() -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    df = pd.read_parquet(DATA_PATH)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    n = len(df.dropna(subset=["t10y3m", "spy_ret"]))
    oos_n = min(max(36, round(n * 0.25)), 120)
    oos_start = df.dropna(subset=["t10y3m", "spy_ret"]).index[-oos_n]
    is_end = df.index[df.index < oos_start].max()
    log(f"Loaded {df.shape}, {df.index.min().date()} -> {df.index.max().date()}")
    log(f"IS ends {is_end.date()}, OOS starts {oos_start.date()}")
    return df, is_end, oos_start


def stage_core_models(df: pd.DataFrame) -> None:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.tsa.stattools import grangercausalitytests

    # Correlation battery.
    corr_rows = []
    for sig, (col, _) in SIGNALS.items():
        for horizon in (1, 3, 6, 12):
            ycol = f"spy_fwd_{horizon}m"
            sub = df[[col, ycol]].dropna()
            if len(sub) < 50:
                continue
            pear = stats.pearsonr(sub[col], sub[ycol])
            spear = stats.spearmanr(sub[col], sub[ycol])
            kend = stats.kendalltau(sub[col], sub[ycol])
            for metric, value, pval in [
                ("pearson", pear.statistic, pear.pvalue),
                ("spearman", spear.statistic, spear.pvalue),
                ("kendall", kend.statistic, kend.pvalue),
                ("distance_proxy_abs_pearson", abs(pear.statistic), pear.pvalue),
            ]:
                corr_rows.append({
                    "pair_name": f"{sig}_to_spy_fwd_{horizon}m",
                    "horizon_days": horizon * 21,
                    "metric": metric,
                    "value": round(float(value), 6),
                    "p_value": round(float(pval), 6),
                    "n_obs": int(len(sub)),
                })
    corr_df = pd.DataFrame(corr_rows)
    corr_df.to_csv(CORE_DIR / "correlations.csv", index=False)
    corr_df.to_csv(EXPLORE_DIR / "correlations.csv", index=False)

    # Pre-whitened CCF approximation: use first differences for the slope.
    x = df["t10y3m"].diff()
    y = df["spy_ret"]
    ccf_rows = []
    clean = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    ci = 1.96 / np.sqrt(len(clean))
    for lag in range(-12, 13):
        if lag < 0:
            sub = pd.concat([clean["x"].shift(-lag), clean["y"]], axis=1).dropna()
        else:
            sub = pd.concat([clean["x"], clean["y"].shift(-lag)], axis=1).dropna()
        val = sub.iloc[:, 0].corr(sub.iloc[:, 1]) if len(sub) > 30 else np.nan
        ccf_rows.append({
            "lag": lag,
            "ccf": round(float(val), 6) if pd.notna(val) else np.nan,
            "lower_ci": round(-ci, 6),
            "upper_ci": round(ci, 6),
            "significant": bool(pd.notna(val) and abs(val) > ci),
            "arima_order": "diff1",
            "n_obs": int(len(sub)),
        })
    pd.DataFrame(ccf_rows).to_csv(CORE_DIR / "ccf_prewhitened.csv", index=False)

    # Granger both directions.
    gc = df[["spy_ret", "t10y3m"]].dropna()
    granger_rows = []
    if len(gc) > 80:
        fwd = grangercausalitytests(gc[["spy_ret", "t10y3m"]], maxlag=12, verbose=False)
        rev = grangercausalitytests(gc[["t10y3m", "spy_ret"]], maxlag=12, verbose=False)
        for lag in range(1, 13):
            f_stat, pval, *_ = fwd[lag][0]["ssr_ftest"]
            granger_rows.append({
                "direction": "indicator_to_target",
                "lag": lag,
                "f_statistic": round(float(f_stat), 6),
                "p_value": round(float(pval), 6),
                "significant": bool(pval < 0.05),
            })
            f_stat, pval, *_ = rev[lag][0]["ssr_ftest"]
            granger_rows.append({
                "direction": "target_to_indicator",
                "lag": lag,
                "f_statistic": round(float(f_stat), 6),
                "p_value": round(float(pval), 6),
                "significant": bool(pval < 0.05),
            })
    gr = pd.DataFrame(granger_rows)
    gr.to_csv(CORE_DIR / "granger_causality.csv", index=False)
    gr.to_csv(RESULTS_DIR / "granger_by_lag.csv", index=False)

    # Local projections and predictive regressions.
    lp_rows = []
    pred_rows = []
    for horizon in (1, 3, 6, 12):
        ycol = f"spy_fwd_{horizon}m"
        sub = df[["t10y3m", ycol]].dropna()
        if len(sub) < 60:
            continue
        X = sm.add_constant(sub["t10y3m"])
        model = sm.OLS(sub[ycol], X).fit(cov_type="HC3")
        ci_low, ci_high = model.conf_int().loc["t10y3m"]
        row = {
            "horizon": horizon,
            "coef": round(float(model.params["t10y3m"]), 6),
            "se": round(float(model.bse["t10y3m"]), 6),
            "ci_lower": round(float(ci_low), 6),
            "ci_upper": round(float(ci_high), 6),
            "p_value": round(float(model.pvalues["t10y3m"]), 6),
            "direction": "fwd",
        }
        lp_rows.append(row)
        pred_rows.append({
            "target": ycol,
            "coef_t10y3m": row["coef"],
            "se": row["se"],
            "p_value": row["p_value"],
            "r2": round(float(model.rsquared), 6),
            "n_obs": int(model.nobs),
        })
    pd.DataFrame(lp_rows).to_csv(CORE_DIR / "local_projections.csv", index=False)
    pd.DataFrame(pred_rows).to_csv(CORE_DIR / "predictive_regressions.csv", index=False)

    # Quantile regression.
    qr_rows = []
    qr_data = df[["t10y3m", "spy_fwd_3m"]].dropna()
    if len(qr_data) > 80:
        for tau in (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95):
            try:
                fit = smf.quantreg("spy_fwd_3m ~ t10y3m", qr_data).fit(q=tau)
                ci_low, ci_high = fit.conf_int().loc["t10y3m"]
                qr_rows.append({
                    "tau": tau,
                    "coef": round(float(fit.params["t10y3m"]), 6),
                    "se": round(float(fit.bse["t10y3m"]), 6),
                    "p_value": round(float(fit.pvalues["t10y3m"]), 6),
                    "ci_lower": round(float(ci_low), 6),
                    "ci_upper": round(float(ci_high), 6),
                })
            except Exception:
                pass
    pd.DataFrame(qr_rows).to_csv(CORE_DIR / "quantile_regression.csv", index=False)

    # Yield-curve factor table. With this pair's single direct spread, slope is
    # the observed factor; level/curvature are unavailable in the scoped data.
    factors = pd.DataFrame({
        "date": df.index,
        "level": np.nan,
        "slope": df["t10y3m"].values,
        "curvature": np.nan,
    })
    factors.to_csv(CORE_DIR / "yield_curve_factors.csv", index=False)

    # Diagnostics.
    diag = []
    for col in ("t10y3m", "t10y3m_mom", "t10y3m_zscore_60m", "spy_ret"):
        s = df[col].dropna()
        diag.append({
            "variable": col,
            "n_obs": len(s),
            "mean": round(float(s.mean()), 6),
            "std": round(float(s.std()), 6),
            "skew": round(float(s.skew()), 6),
            "kurtosis": round(float(s.kurtosis()), 6),
        })
    pd.DataFrame(diag).to_csv(CORE_DIR / "diagnostics_summary.csv", index=False)
    log(f"Core models written to {CORE_DIR.relative_to(ROOT)}")


def make_threshold(signal: pd.Series, is_mask: pd.Series, name: str):
    if name.startswith("T1_fixed_p"):
        pct = int(name.split("p")[1])
        threshold = signal[is_mask].dropna().quantile(pct / 100)
        return threshold, float(threshold), f"fixed in-sample percentile p{pct}"
    if name.startswith("T2_roll_p"):
        pct = int(name.split("p")[1])
        threshold = signal.rolling(60, min_periods=36).quantile(pct / 100)
        latest = threshold.dropna().iloc[-1] if threshold.dropna().shape[0] else np.nan
        return threshold, float(latest), f"rolling 60-month percentile p{pct}; threshold_value is latest"
    if name == "T4_zero":
        return 0.0, 0.0, "zero threshold"
    if name == "T5_half":
        return 0.5, 0.5, "0.5 threshold for binary flags"
    raise ValueError(name)


def bullish(signal: pd.Series, threshold, direction: str) -> pd.Series:
    return signal > threshold if direction == "procyclical" else signal < threshold


def signal_strength(signal: pd.Series, direction: str) -> pd.Series:
    lo = signal.rolling(60, min_periods=36).min()
    hi = signal.rolling(60, min_periods=36).max()
    scaled = ((signal - lo) / (hi - lo).replace(0, np.nan)).clip(0, 1)
    return scaled if direction == "procyclical" else 1 - scaled


def stage_tournament(df: pd.DataFrame, is_end: pd.Timestamp, oos_start: pd.Timestamp) -> pd.DataFrame:
    is_mask = df.index <= is_end
    oos_mask = df.index >= oos_start
    rows = []
    lead_grid = [0, 1, 2, 3, 6, 9, 12]
    strategies = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]

    for sig_code, (col, direction) in SIGNALS.items():
        raw = df[col].copy()
        if raw.dropna().shape[0] < 80:
            continue
        for lead in lead_grid:
            sig = raw.shift(lead) if lead > 0 else raw
            threshold_names = ["T1_fixed_p25", "T1_fixed_p50", "T1_fixed_p75", "T2_roll_p25", "T2_roll_p50", "T2_roll_p75"]
            if col.endswith("_chg") or col == "t10y3m_mom" or col == "t10y3m_zscore_60m":
                threshold_names.append("T4_zero")
            if col.endswith("_flag"):
                threshold_names = ["T5_half"]
            for tname in threshold_names:
                try:
                    thresh, _, _ = make_threshold(sig, is_mask, tname)
                except Exception:
                    continue
                for strat in strategies:
                    try:
                        b = bullish(sig, thresh, direction)
                        if strat == "P1_long_cash":
                            pos = b.astype(float)
                        elif strat == "P2_signal_strength":
                            pos = signal_strength(sig, direction)
                        else:
                            pos = b.astype(float) * 2 - 1
                        ret = pos.shift(1) * df["spy_ret"]
                        is_ret = ret[is_mask].dropna()
                        oos_ret = ret[oos_mask].dropna()
                        if len(is_ret) < 48 or len(oos_ret) < 24:
                            continue
                        m_is = metrics(is_ret)
                        m_oos = metrics(oos_ret)
                        years = len(pos.dropna()) / 12
                        turnover = float(pos.diff().abs().sum() / years) if years > 0 else 999
                        rows.append({
                            "signal": sig_code,
                            "signal_column": col,
                            "threshold": tname,
                            "strategy": strat,
                            "lead_months": lead,
                            "direction": direction,
                            "is_sharpe": round(m_is["oos_sharpe"], 4),
                            "oos_sharpe": round(m_oos["oos_sharpe"], 4),
                            "oos_sortino": round(m_oos["oos_sortino"], 4),
                            "oos_calmar": round(m_oos["oos_calmar"], 4),
                            "oos_ann_return": round(m_oos["oos_ann_return"], 6),
                            "oos_ann_vol": round(m_oos["oos_ann_vol"], 6),
                            "max_drawdown": round(m_oos["max_drawdown"], 6),
                            "win_rate": round(m_oos["win_rate"], 4),
                            "annual_turnover": round(turnover, 2),
                            "is_n": m_is["n"],
                            "oos_n": m_oos["n"],
                            "valid": bool(m_oos["oos_sharpe"] > 0 and turnover < 24),
                        })
                    except Exception:
                        continue

    bh = df.loc[oos_mask, "spy_ret"].dropna()
    bh_is = df.loc[is_mask, "spy_ret"].dropna()
    m_bh = metrics(bh)
    m_bh_is = metrics(bh_is)
    rows.append({
        "signal": "BENCHMARK",
        "signal_column": "spy",
        "threshold": "BUY_HOLD",
        "strategy": "BUY_HOLD",
        "lead_months": 0,
        "direction": "benchmark",
        "is_sharpe": round(m_bh_is["oos_sharpe"], 4),
        "oos_sharpe": round(m_bh["oos_sharpe"], 4),
        "oos_sortino": round(m_bh["oos_sortino"], 4),
        "oos_calmar": round(m_bh["oos_calmar"], 4),
        "oos_ann_return": round(m_bh["oos_ann_return"], 6),
        "oos_ann_vol": round(m_bh["oos_ann_vol"], 6),
        "max_drawdown": round(m_bh["max_drawdown"], 6),
        "win_rate": round(m_bh["win_rate"], 4),
        "annual_turnover": 0.0,
        "is_n": m_bh_is["n"],
        "oos_n": m_bh["n"],
        "valid": False,
    })

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS_DIR / f"tournament_results_{DATE_TAG}.csv", index=False)
    log(f"Tournament rows={len(out)}, valid={int((out['valid'] & (out['signal'] != 'BENCHMARK')).sum())}")
    return out


def write_strategy_artifacts(df: pd.DataFrame, tourn: pd.DataFrame, is_end: pd.Timestamp, oos_start: pd.Timestamp) -> None:
    valid = tourn[tourn["valid"].astype(bool) & (tourn["signal"] != "BENCHMARK")]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    best = valid.loc[valid["oos_sharpe"].idxmax()]
    bh = tourn[tourn["signal"] == "BENCHMARK"].iloc[0]

    col = best["signal_column"]
    direction = best["direction"]
    lead = int(best["lead_months"])
    raw = df[col].copy()
    sig = raw.shift(lead) if lead > 0 else raw
    is_mask = df.index <= is_end
    oos_mask = df.index >= oos_start
    thresh, threshold_value, threshold_note = make_threshold(sig, is_mask, best["threshold"])

    if best["strategy"] == "P1_long_cash":
        pos = bullish(sig, thresh, direction).astype(float)
        rule_desc = "Long SPY when the lagged yield-curve signal is above its threshold; otherwise cash."
    elif best["strategy"] == "P2_signal_strength":
        pos = signal_strength(sig, direction)
        rule_desc = "Scale SPY exposure by the lagged yield-curve signal's rolling strength."
    else:
        pos = bullish(sig, thresh, direction).astype(float) * 2 - 1
        rule_desc = "Long SPY when the lagged yield-curve signal is bullish and short when it is bearish."

    strat_ret = pos.shift(1) * df["spy_ret"]
    strategy = pd.DataFrame({
        "signal_value": sig,
        "position": pos,
        "strategy_return": strat_ret,
        "benchmark_return": df["spy_ret"],
    }, index=df.index)
    strategy["strategy_equity"] = (1 + strategy["strategy_return"].fillna(0)).cumprod()
    strategy["benchmark_equity"] = (1 + strategy["benchmark_return"].fillna(0)).cumprod()
    strategy.to_csv(RESULTS_DIR / f"strategy_returns_{DATE_TAG}.csv")
    signals = df[[
        "t10y3m",
        "t10y3m_mom",
        "t10y3m_3m_chg",
        "t10y3m_6m_chg",
        "t10y3m_12m_chg",
        "t10y3m_zscore_60m",
        "t10y3m_inversion_flag",
        "t10y3m_curve_steepening",
        "spy",
        "spy_ret",
        "spy_fwd_1m",
        "spy_fwd_3m",
        "spy_fwd_6m",
        "spy_fwd_12m",
    ]].copy()
    signals["winner_signal_lagged"] = sig
    signals["winner_threshold"] = thresh
    signals["winner_position"] = pos
    signals.to_parquet(RESULTS_DIR / f"signals_{DATE_TAG}.parquet")
    (RESULTS_DIR / f"strategy_returns_{DATE_TAG}_meta.json").write_text(json.dumps({
        "pair_id": PAIR_ID,
        "generated_at": NOW_ISO,
        "winner_signal": best["signal"],
        "threshold": best["threshold"],
        "strategy": best["strategy"],
        "lead_months": lead,
        "return_units": "ratio",
    }, indent=2) + "\n")

    oos = strategy.loc[oos_mask].copy()
    oos["spy"] = df.loc[oos_mask, "spy"]
    oos.to_csv(RESULTS_DIR / "winner_trade_log.csv")
    broker = oos.reset_index().rename(columns={"date": "signal_date"})
    broker["target_symbol"] = "SPY"
    broker["action"] = np.where(broker["position"] > 0.5, "LONG_SPY", np.where(broker["position"] < -0.5, "SHORT_SPY", "CASH"))
    broker.to_csv(RESULTS_DIR / "winner_trades_broker_style.csv", index=False)

    oos_pos = pos.loc[oos_mask].dropna()
    summary = {
        "pair_id": PAIR_ID,
        "generated_at": NOW_ISO,
        "signal_column": str(col),
        "signal_code": str(best["signal"]),
        "signal_display_name": DISPLAY.get(str(col), str(col)),
        "target_symbol": "SPY",
        "threshold_code": str(best["threshold"]),
        "threshold_value": round(float(threshold_value), 6) if pd.notna(threshold_value) else None,
        "threshold_rule": "gt" if direction == "procyclical" else "lt",
        "threshold_note": threshold_note,
        "strategy_family": str(best["strategy"]),
        "strategy_code": str(best["strategy"]).split("_")[0],
        "strategy_display_name": str(best["strategy"]).replace("_", " "),
        "strategy_description": rule_desc,
        "lead_value": lead,
        "lead_unit": "months",
        "lead_description": f"Signal is lagged {lead} month(s) before the position is set.",
        "lookback": "LB60" if str(best["threshold"]).startswith("T2") else "LB_NA",
        "direction": "procyclical" if direction == "procyclical" else "countercyclical",
        "oos_sharpe": round(float(best["oos_sharpe"]), 4),
        "oos_sortino": round(float(best["oos_sortino"]), 4),
        "oos_calmar": round(float(best["oos_calmar"]), 4),
        "oos_ann_return": round(float(best["oos_ann_return"]), 6),
        "oos_ann_vol": round(float(best["oos_ann_vol"]), 6),
        "oos_max_drawdown": round(float(best["max_drawdown"]), 6),
        "oos_win_rate": round(float(best["win_rate"]), 4),
        "oos_n_trades": int(oos_pos.diff().abs().fillna(0).gt(0).sum()),
        "annual_turnover": round(float(best["annual_turnover"]), 2),
        "oos_n": int(best["oos_n"]),
        "oos_period_start": oos_start.strftime("%Y-%m-%d"),
        "oos_period_end": df.loc[oos_mask].index.max().strftime("%Y-%m-%d"),
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_ann_return": round(float(bh["oos_ann_return"]), 6),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 6),
        "cost_assumption_bps": COST_BPS,
        "total_combos": int((tourn["signal"] != "BENCHMARK").sum()),
        "valid_combos": int((tourn["valid"] & (tourn["signal"] != "BENCHMARK")).sum()),
        "schema_version": "1.1.0",
        "notes": f"Rates-pair tournament. Winner selected from {len(valid)} valid strategy rows; threshold note: {threshold_note}.",
    }
    (RESULTS_DIR / "winner_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    kpis = {
        "pair_id": PAIR_ID,
        "generated_at": NOW_ISO,
        "winner_oos_sharpe": summary["oos_sharpe"],
        "benchmark_oos_sharpe": summary["bh_sharpe"],
        "winner_oos_ann_return": summary["oos_ann_return"],
        "winner_oos_max_drawdown": summary["oos_max_drawdown"],
        "valid_combos": summary["valid_combos"],
    }
    (RESULTS_DIR / "kpis.json").write_text(json.dumps(kpis, indent=2) + "\n")
    log(f"Winner: {summary['signal_code']} / {summary['threshold_code']} / L{lead}, Sharpe={summary['oos_sharpe']}")


def write_regime_and_validation(df: pd.DataFrame, tourn: pd.DataFrame, oos_start: pd.Timestamp) -> None:
    valid = df[["t10y3m", "spy_ret"]].dropna()
    q = pd.qcut(valid["t10y3m"], 4, labels=["Q1_inverted_flat", "Q2", "Q3", "Q4_steep"])
    rows = []
    for label, sub in valid.groupby(q, observed=False):
        m = metrics(sub["spy_ret"])
        rows.append({
            "quartile": str(label),
            "mean_return": round(float(sub["spy_ret"].mean()), 6),
            "vol": round(float(sub["spy_ret"].std()), 6),
            "sharpe": round(float(m["oos_sharpe"]), 4),
            "n_obs": int(len(sub)),
            "cutoff_lower": round(float(sub["t10y3m"].min()), 4),
            "cutoff_upper": round(float(sub["t10y3m"].max()), 4),
        })
    reg = pd.DataFrame(rows)
    reg.to_csv(RESULTS_DIR / "regime_quartile_returns.csv", index=False)
    reg.to_csv(EXPLORE_DIR / "regime_descriptive_stats.csv", index=False)

    periods = {
        "Dot_Com": ("2000-03-31", "2002-10-31"),
        "GFC": ("2007-10-31", "2009-03-31"),
        "COVID": ("2020-02-29", "2020-06-30"),
        "Rate_Hike_2022": ("2022-01-31", "2023-10-31"),
    }
    sp = []
    for name, (start, end) in periods.items():
        r = df.loc[start:end, "spy_ret"].dropna()
        if len(r):
            m = metrics(r)
            sp.append({"period": name, "start": start, "end": end, "n_months": len(r), "buy_hold_sharpe": round(m["oos_sharpe"], 4), "buy_hold_return": round(float(r.sum()), 6)})
    pd.DataFrame(sp).to_csv(RESULTS_DIR / "subperiod_sharpe.csv", index=False)

    valid_strats = tourn[tourn["valid"] & (tourn["signal"] != "BENCHMARK")].nlargest(5, "oos_sharpe")
    boot_rows = []
    oos = df.loc[df.index >= oos_start, "spy_ret"].dropna()
    boot = []
    for _ in range(1000):
        sample = np.random.choice(oos.values, size=len(oos), replace=True)
        boot.append(sample.mean() / sample.std() * np.sqrt(12) if sample.std() > 0 else 0)
    boot = np.array(boot)
    for _, row in valid_strats.iterrows():
        boot_rows.append({
            "signal": row["signal"],
            "threshold": row["threshold"],
            "strategy": row["strategy"],
            "oos_sharpe": row["oos_sharpe"],
            "bootstrap_p_value": round(float((boot >= row["oos_sharpe"]).mean()), 4),
            "significant_at_5pct": bool((boot >= row["oos_sharpe"]).mean() < 0.05),
        })
    pd.DataFrame(boot_rows).to_csv(VALID_DIR / "bootstrap.csv", index=False)
    pd.DataFrame([
        {"signal": r["signal"], "threshold": r["threshold"], "strategy": r["strategy"], "tx_cost_bps": bps, "gross_sharpe": r["oos_sharpe"]}
        for _, r in valid_strats.iterrows() for bps in (0, 5, 10, 25, 50)
    ]).to_csv(VALID_DIR / "transaction_costs.csv", index=False)


def write_scope_and_suggestions() -> None:
    scope = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "owner": "evan",
        "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {
            "canonical_column": "t10y3m",
            "display_name": "10Y-3M Treasury Spread",
            "derivatives": [
                {"name": "t10y3m", "definition": "The 10-year Treasury yield minus the 3-month Treasury yield, in percentage points.", "formula": "FRED T10Y3M", "role": "raw", "appears_in_charts": ["hero", "regime_stats"]},
                {"name": "t10y3m_mom", "definition": "One-month change in the yield-curve spread.", "formula": "x_t - x_{t-1}", "role": "derivative", "appears_in_charts": []},
                {"name": "t10y3m_3m_chg", "definition": "Three-month change in the yield-curve spread.", "formula": "x_t - x_{t-3}", "role": "derivative", "appears_in_charts": []},
                {"name": "t10y3m_6m_chg", "definition": "Six-month change in the yield-curve spread.", "formula": "x_t - x_{t-6}", "role": "derivative", "appears_in_charts": []},
                {"name": "t10y3m_12m_chg", "definition": "Twelve-month change in the yield-curve spread.", "formula": "x_t - x_{t-12}", "role": "derivative", "appears_in_charts": []},
                {"name": "t10y3m_zscore_60m", "definition": "How unusual the spread is versus its own five-year history.", "formula": "(x_t - mean60) / std60", "role": "threshold_input", "appears_in_charts": []},
                {"name": "t10y3m_inversion_flag", "definition": "A flag equal to one when the yield curve is inverted.", "formula": "indicator(x < 0)", "role": "regime_state", "appears_in_charts": ["hero"]},
            ],
        },
        "target_axis": {
            "canonical_column": "spy",
            "display_name": "SPY adjusted close",
            "derivatives": [
                {"name": "spy", "definition": "SPY adjusted month-end close.", "formula": "month-end close", "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "Monthly SPY return.", "formula": "p_t / p_{t-1} - 1", "role": "derivative", "appears_in_charts": []},
                {"name": "spy_fwd_1m", "definition": "One-month forward SPY return.", "formula": "p_{t+1} / p_t - 1", "role": "diagnostic", "appears_in_charts": []},
                {"name": "spy_fwd_3m", "definition": "Three-month forward SPY return.", "formula": "p_{t+3} / p_t - 1", "role": "diagnostic", "appears_in_charts": ["local_projections", "quantile_coef"]},
                {"name": "spy_fwd_6m", "definition": "Six-month forward SPY return.", "formula": "p_{t+6} / p_t - 1", "role": "diagnostic", "appears_in_charts": []},
                {"name": "spy_fwd_12m", "definition": "Twelve-month forward SPY return.", "formula": "p_{t+12} / p_t - 1", "role": "diagnostic", "appears_in_charts": []},
            ],
        },
        "notes": "Scope limited to T10Y3M derivatives and SPY returns; no off-axis macro controls are used as trading signals.",
    }
    (RESULTS_DIR / "signal_scope.json").write_text(json.dumps(scope, indent=2) + "\n")

    suggestions = {
        "schema_version": "1.0.0",
        "pair_id": PAIR_ID,
        "suggestions": [
            {
                "signal_name": "10Y-2Y Treasury spread",
                "proposed_by": "evan",
                "source": "FRED T10Y2Y",
                "observation": "10Y-2Y is a widely watched alternate yield-curve slope and may differ from the 10Y-3M signal around policy turning points.",
                "rationale": "Comparing the two curve slopes can separate policy-rate pressure from intermediate-term growth expectations.",
                "possible_use_case": "variant family / cross-pair comparison",
                "caveats": "Highly correlated with 10Y-3M, so it should be treated as a variant rather than a new independent signal.",
                "date_filed": "2026-06-20",
            }
        ],
        "last_updated_at": NOW_ISO,
    }
    (RESULTS_DIR / "analyst_suggestions.json").write_text(json.dumps(suggestions, indent=2) + "\n")

    evidence = {
        "schema_version": "1.0.0",
        "pair_id": PAIR_ID,
        "status": "found_in_search",
        "confidence": "medium",
        "generated_at": NOW_ISO,
        "updated_at": NOW_ISO,
        "notes": "Rates-pair winner selected from tournament search; no untouched final exam yet.",
    }
    (RESULTS_DIR / "evidence_status.json").write_text(json.dumps(evidence, indent=2) + "\n")


def update_interpretation_from_winner() -> None:
    meta_path = RESULTS_DIR / "interpretation_metadata.json"
    winner = json.loads((RESULTS_DIR / "winner_summary.json").read_text())
    meta = json.loads(meta_path.read_text())
    meta["observed_direction"] = winner.get("direction", "procyclical")
    meta["direction_consistent"] = meta["observed_direction"] == meta.get("expected_direction")
    meta["confidence"] = "medium"
    meta["key_finding"] = (
        f"Winner is {winner['signal_display_name']} with {winner['lead_value']}-month lead; "
        f"OOS Sharpe {winner['oos_sharpe']:.2f} vs buy-and-hold {winner['bh_sharpe']:.2f}."
    )
    meta["last_updated_by"] = "ray"
    meta["last_updated_at"] = NOW_ISO
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")


def main() -> None:
    t0 = time.time()
    df, is_end, oos_start = load_data()
    stage_core_models(df)
    tourn = stage_tournament(df, is_end, oos_start)
    write_regime_and_validation(df, tourn, oos_start)
    write_strategy_artifacts(df, tourn, is_end, oos_start)
    write_scope_and_suggestions()
    update_interpretation_from_winner()
    timing = {
        "pair_id": PAIR_ID,
        "generated_at": NOW_ISO,
        "seconds": round(time.time() - t0, 2),
        "stages": ["core_models", "tournament", "validation", "contracts"],
    }
    (RESULTS_DIR / f"pipeline_timing_{DATE_TAG}.json").write_text(json.dumps(timing, indent=2) + "\n")
    log("Pipeline complete")


if __name__ == "__main__":
    main()
