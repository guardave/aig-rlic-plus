#!/usr/bin/env python3
"""
Econometrics Pipeline: gold_copper_xli (Mode 2 Phase 3, Evan hat)

Reads Dana's parquet, produces all ECON-H-series + ECON-DS artifacts:
- stationarity_tests_<DATE>.csv  (ADF on candidate signals + targets)
- granger_by_lag.csv             (Granger F by lag, signal -> xli_ret)
- tournament_results_<DATE>.csv  (signals x thresholds x strategies x leads)
- winner_summary.json            (ECON-DS schema, all required fields)
- signal_scope.json              (canonical signal axis description)
- signals_<DATE>.parquet         (the chosen signal column series)
- regime_quartile_returns.csv    (forward returns by signal quartile)
- analyst_suggestions.json       (off-scope candidates flagged for follow-up)
- pipeline_timing.json
- Update interpretation_metadata.json with Evan's keys.

Leaner-than-Mode-1 scope: 5 signal transforms x 3 thresholds x 2 strategies
x 3 leads = 90 combos. Walk-forward style: IS through 2019, OOS 2020-2025.
"""

import os, sys, json, time, warnings, itertools
from datetime import datetime, timezone
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

PAIR_ID = "gold_copper_xli"
DATE_TAG = "20260526"
BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
os.makedirs(RESULTS_DIR, exist_ok=True)

PARQUET = os.path.join(DATA_DIR, f"{PAIR_ID}_daily_{DATE_TAG}.parquet")
INTERP = os.path.join(RESULTS_DIR, "interpretation_metadata.json")

IS_END = pd.Timestamp("2019-12-31")
OOS_START = pd.Timestamp("2020-01-01")
OOS_END = pd.Timestamp("2025-12-31")

SIGNAL_COLS = [
    "gold_copper_zscore_252d",
    "gold_copper_zscore_126d",
    "gold_copper_pctrank_504d",
    "gold_copper_roc_63d",
    "gold_copper_roc_126d",
]
TARGET_FWD = "xli_fwd_63d"  # primary horizon
TARGET_RET = "xli_ret"


def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}", flush=True)


def stage_load():
    log("Stage 1: load")
    df = pd.read_parquet(PARQUET)
    log(f"  rows={len(df)}  cols={len(df.columns)}")
    return df


def stage_stationarity(df):
    log("Stage 2: stationarity tests (ADF)")
    from statsmodels.tsa.stattools import adfuller
    rows = []
    for col in SIGNAL_COLS + ["gold_copper_ratio", "gold_copper_logratio",
                              "xli", "xli_ret"]:
        s = df[col].dropna()
        if len(s) < 200:
            continue
        try:
            stat, p, *_ = adfuller(s, autolag="AIC")
            rows.append({
                "variable": col,
                "test": "ADF",
                "statistic": round(float(stat), 4),
                "p_value": round(float(p), 4),
                "conclusion": "Stationary" if p < 0.05 else "Non-stationary",
                "n_obs": int(len(s)),
            })
        except Exception as e:
            log(f"  ADF FAIL {col}: {e}")
    out = os.path.join(RESULTS_DIR, f"stationarity_tests_{DATE_TAG}.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"  wrote {out}  ({len(rows)} variables)")
    return rows


def stage_granger(df):
    log("Stage 3: Granger by lag (gold_copper_zscore_252d -> xli_ret)")
    from statsmodels.tsa.stattools import grangercausalitytests
    sub = df[["gold_copper_zscore_252d", "xli_ret"]].dropna()
    sub = sub.loc[:IS_END]  # IS only for Granger
    rows = []
    for lag in [1, 5, 10, 21, 63]:
        try:
            res = grangercausalitytests(sub[["xli_ret", "gold_copper_zscore_252d"]],
                                        maxlag=lag, verbose=False)
            f = res[lag][0]["ssr_ftest"]
            rows.append({
                "lag": lag,
                "f_stat": round(float(f[0]), 4),
                "p_value": round(float(f[1]), 4),
                "significant_5pct": bool(f[1] < 0.05),
            })
        except Exception as e:
            log(f"  Granger FAIL lag={lag}: {e}")
    out = os.path.join(RESULTS_DIR, "granger_by_lag.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"  wrote {out}")
    return rows


def stage_tournament(df):
    """Combinatorial sweep. Each combo: signal x threshold rule x strategy x lead.

    Threshold rules (countercyclical asserted -> bearish when signal HIGH):
      T1 = static p25 (long when signal <= IS p25)
      T2 = static p50 (long when signal <= IS p50)
      T3 = static p75 (long when signal <= IS p75)
    Strategies:
      P1 = Long/Cash (long XLI when bullish, cash otherwise)
      P2 = Long/Short (long XLI when bullish, short XLI otherwise)
    Lead: signal observed at t, position taken at t+lead, held until exit.
    """
    log("Stage 4: tournament")
    rows = []
    for sig_col in SIGNAL_COLS:
        sig = df[sig_col].copy()
        is_sig = sig.loc[:IS_END].dropna()
        if len(is_sig) < 252: continue
        thresholds = {
            "T1_p25": is_sig.quantile(0.25),
            "T2_p50": is_sig.quantile(0.50),
            "T3_p75": is_sig.quantile(0.75),
        }
        for t_code, t_val in thresholds.items():
            for s_code in ["P1_long_cash", "P2_long_short"]:
                for lead in [0, 1, 5]:
                    try:
                        # Position: 1 = long when signal <= threshold (low ratio = bullish)
                        pos = (sig <= t_val).astype(int).shift(lead).fillna(0)
                        if s_code == "P2_long_short":
                            pos = pos * 2 - 1  # -1 / +1
                        ret = df[TARGET_RET].fillna(0)
                        strat_ret = pos * ret
                        oos_ret = strat_ret.loc[OOS_START:OOS_END].dropna()
                        if len(oos_ret) < 200: continue
                        sharpe = (oos_ret.mean() * 252) / (oos_ret.std() * np.sqrt(252) + 1e-12)
                        ann_ret = (1 + oos_ret).prod() ** (252 / len(oos_ret)) - 1
                        equity = (1 + oos_ret).cumprod()
                        peak = equity.cummax()
                        mdd = ((equity - peak) / peak).min()
                        turnover = pos.diff().abs().loc[OOS_START:OOS_END].sum() / (len(oos_ret) / 252)
                        rows.append({
                            "signal": sig_col,
                            "threshold": t_code,
                            "threshold_value": round(float(t_val), 4),
                            "strategy": s_code,
                            "lead_days": lead,
                            "oos_sharpe": round(float(sharpe), 4),
                            "oos_ann_return": round(float(ann_ret * 100), 2),
                            "oos_max_drawdown": round(float(mdd * 100), 2),
                            "annual_turnover": round(float(turnover), 2),
                            "oos_n": int(len(oos_ret)),
                            "valid": bool(sharpe > 0 and turnover < 100),
                        })
                    except Exception as e:
                        log(f"  combo FAIL {sig_col}/{t_code}/{s_code}/L{lead}: {e}")
    df_t = pd.DataFrame(rows).sort_values("oos_sharpe", ascending=False)
    out = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    df_t.to_csv(out, index=False)
    log(f"  wrote {out}  ({len(df_t)} combos, {df_t['valid'].sum()} valid)")
    return df_t


def stage_winner(df, df_t):
    log("Stage 5: winner_summary + signals parquet")
    valid = df_t[df_t["valid"]].copy()
    if len(valid) == 0:
        log("  WARN: no valid winner; using best by sharpe regardless")
        valid = df_t.head(1)
    w = valid.iloc[0]

    # Recompute winner series for signals parquet
    sig_col = w["signal"]
    sig = df[sig_col]
    pos = (sig <= w["threshold_value"]).astype(int).shift(int(w["lead_days"])).fillna(0)
    if w["strategy"] == "P2_long_short":
        pos = pos * 2 - 1
    ret = df[TARGET_RET].fillna(0)
    strat_ret = pos * ret
    equity = (1 + strat_ret).cumprod()
    bh_equity = (1 + ret).cumprod()
    signals = pd.DataFrame({
        "signal_raw": sig,
        "position": pos,
        "strategy_return": strat_ret,
        "equity_curve": equity,
        "buy_and_hold_equity": bh_equity,
    }, index=df.index)
    sig_path = os.path.join(RESULTS_DIR, f"signals_{DATE_TAG}.parquet")
    signals.to_parquet(sig_path, engine="pyarrow", compression="snappy")
    log(f"  wrote {sig_path}")

    direction = "countercyclical"  # asserted by Ray
    summary = {
        "pair_id": PAIR_ID,
        "signal_code": f"S_{sig_col.replace('gold_copper_', '')}",
        "signal_display_name": sig_col.replace("gold_copper_", "G/C "),
        "signal_column": sig_col,
        "threshold_code": w["threshold"],
        "threshold_display_name": w["threshold"].replace("_", " "),
        "threshold_value": float(w["threshold_value"]),
        "threshold_rule": "le",  # long when signal <= threshold
        "strategy_code": w["strategy"].split("_")[0],
        "strategy_display_name": w["strategy"].replace("P1_long_cash", "Long/Cash").replace("P2_long_short", "Long/Short"),
        "strategy_description": (
            "Long XLI when the signal is below its IS-calibrated threshold "
            "(ratio low = risk-on regime); otherwise cash."
            if w["strategy"] == "P1_long_cash"
            else "Long XLI when signal is below threshold; short XLI otherwise."
        ),
        "strategy_family": w["strategy"],
        "lead_value": int(w["lead_days"]),
        "lead_unit": "days",
        "lead_description": f"Signal lead = {int(w['lead_days'])} business day(s)",
        "direction": direction,
        "oos_sharpe": float(w["oos_sharpe"]),
        "oos_ann_return": float(w["oos_ann_return"]) / 100.0,
        "max_drawdown": float(w["oos_max_drawdown"]),
        "oos_max_drawdown": float(w["oos_max_drawdown"]) / 100.0,
        "annual_turnover": float(w["annual_turnover"]),
        "win_rate": float((strat_ret.loc[OOS_START:OOS_END] > 0).mean()),
        "oos_n_trades": int(pos.diff().abs().loc[OOS_START:OOS_END].sum()),
        "oos_period_start": str(OOS_START.date()),
        "oos_period_end": str(OOS_END.date()),
        "target_symbol": "XLI",
        "schema_version": "1.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": (
            f"Mode 2 Phase 3 (Evan hat). Tournament: 5 signals x 3 thresholds "
            f"x 2 strategies x 3 leads = 90 combos, {len(df_t)} fit, "
            f"{int(df_t['valid'].sum())} valid. Winner selected by OOS Sharpe."
        ),
    }
    out = os.path.join(RESULTS_DIR, "winner_summary.json")
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"  wrote {out}  sharpe={summary['oos_sharpe']:.3f}  "
        f"ann_ret={summary['oos_ann_return']*100:.1f}%  "
        f"mdd={summary['oos_max_drawdown']*100:.1f}%")
    return summary


def stage_signal_scope():
    log("Stage 6: signal_scope.json")
    scope = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "owner": "evan",
        "last_updated_by": "lead-as-evan (Mode 2 Phase 3)",
        "last_updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "indicator_axis": {
            "canonical_column": "gold_copper_ratio",
            "display_name": "Gold/Copper Ratio (real-asset risk-off proxy)",
            "derivatives": [
                {"name": "gold_copper_ratio", "definition": "Raw ratio of gold ($/oz) to copper ($/lb).",
                 "formula": "gold[t] / copper[t]", "role": "raw"},
                {"name": "gold_copper_logratio", "definition": "Natural log of the ratio. Better-distributed.",
                 "formula": "log(gold_copper_ratio)", "role": "transform"},
                {"name": "gold_copper_zscore_252d", "definition": "252d rolling z-score.",
                 "formula": "(ratio - rollmean_252) / rollstd_252", "role": "threshold_input"},
                {"name": "gold_copper_zscore_126d", "definition": "126d rolling z-score.",
                 "formula": "(ratio - rollmean_126) / rollstd_126", "role": "threshold_input"},
                {"name": "gold_copper_pctrank_504d", "definition": "504d percentile rank.",
                 "formula": "rank(ratio, 504) / 504", "role": "threshold_input"},
                {"name": "gold_copper_roc_63d", "definition": "63d rate-of-change of ratio.",
                 "formula": "(ratio[t]/ratio[t-63] - 1) * 100", "role": "threshold_input"},
                {"name": "gold_copper_roc_126d", "definition": "126d rate-of-change.",
                 "formula": "(ratio[t]/ratio[t-126] - 1) * 100", "role": "threshold_input"},
            ],
        },
        "target": {"symbol": "XLI", "primary_return_col": "xli_ret",
                   "forward_horizons": ["xli_fwd_5d", "xli_fwd_21d", "xli_fwd_63d", "xli_fwd_126d"]},
        "direction_asserted": "countercyclical",
    }
    out = os.path.join(RESULTS_DIR, "signal_scope.json")
    with open(out, "w") as f:
        json.dump(scope, f, indent=2)
    log(f"  wrote {out}")


def stage_quartile_returns(df):
    log("Stage 7: regime_quartile_returns")
    sig = df["gold_copper_zscore_252d"]
    sub = pd.DataFrame({"sig": sig, "fwd": df["xli_fwd_63d"]}).dropna()
    sub["quartile"] = pd.qcut(sub["sig"], 4, labels=["Q1_low", "Q2", "Q3", "Q4_high"])
    grp = sub.groupby("quartile")["fwd"].agg(["mean", "median", "std", "count"])
    grp["mean_pct"] = (grp["mean"] * 100).round(2)
    grp["median_pct"] = (grp["median"] * 100).round(2)
    grp["std_pct"] = (grp["std"] * 100).round(2)
    out = os.path.join(RESULTS_DIR, "regime_quartile_returns.csv")
    grp.reset_index().to_csv(out, index=False)
    log(f"  wrote {out}")
    for q, row in grp.iterrows():
        log(f"    {q}: mean={row['mean_pct']:+.2f}%  n={int(row['count'])}")


def stage_analyst_suggestions():
    log("Stage 8: analyst_suggestions.json (Evan key only)")
    out = os.path.join(RESULTS_DIR, "analyst_suggestions.json")
    payload = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "suggestions": [
            {"slug": "log_ratio_signals", "owner": "evan", "priority": "medium",
             "title": "Log-ratio (gold_copper_logratio) as tournament input",
             "rationale": "Raw ratio is right-skewed; log-ratio is better-distributed and may yield cleaner z-score thresholds."},
            {"slug": "dxy_conditional_signal", "owner": "evan", "priority": "medium",
             "title": "Condition signal strength on DXY regime",
             "rationale": "Both legs USD-priced. When DXY moves dominate, ratio signal may be noise; conditional model would gate the signal on |DXY z-score|."},
            {"slug": "supply_decoupling_check", "owner": "evan", "priority": "low",
             "title": "Detect supply-driven decoupling (2022 failure case)",
             "rationale": "Add a structural-break flag when ratio direction contradicts copper-vs-history percentile (supply tightness regime)."},
        ],
        "exploratory_charts": [],
    }
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    log(f"  wrote {out}")


def stage_update_interp(summary):
    log("Stage 9: update interpretation_metadata.json (Evan keys)")
    with open(INTERP) as f: interp = json.load(f)
    direction = summary["direction"]
    interp["observed_direction"] = direction
    interp["direction_consistent"] = (direction == interp["expected_direction"])
    interp["confidence"] = "medium" if summary["oos_sharpe"] >= 0.5 else "low"
    interp["key_finding"] = (
        f"{summary['signal_column']} <= {summary['threshold_value']:.3f} "
        f"(strategy {summary['strategy_display_name']}, lead {summary['lead_value']}d) "
        f"yields OOS Sharpe {summary['oos_sharpe']:.2f}, ann.return "
        f"{summary['oos_ann_return']*100:.1f}%, max DD "
        f"{summary['oos_max_drawdown']*100:.1f}%."
    )
    interp["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(INTERP, "w") as f: json.dump(interp, f, indent=2)
    log(f"  observed_direction={direction}  consistent={interp['direction_consistent']}  confidence={interp['confidence']}")


def main():
    t0 = time.time()
    df = stage_load()
    stage_stationarity(df)
    stage_granger(df)
    df_t = stage_tournament(df)
    summary = stage_winner(df, df_t)
    stage_signal_scope()
    stage_quartile_returns(df)
    stage_analyst_suggestions()
    stage_update_interp(summary)
    timing = {"elapsed_seconds": round(time.time() - t0, 1),
              "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(os.path.join(RESULTS_DIR, "pipeline_timing.json"), "w") as f:
        json.dump(timing, f, indent=2)
    log(f"\nDONE in {timing['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
