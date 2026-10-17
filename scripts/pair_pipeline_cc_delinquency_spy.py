#!/usr/bin/env python3
"""Pair pipeline: Credit Card Delinquency Rate x SPY (Phase B harness).

QUARTERLY. The indicator is the delinquency rate on credit-card loans (percent of balances 30+ days past due;
FRED DRCCLACBN, NOT seasonally adjusted). Economic prior: high / rising delinquency signals household credit
stress -> COUNTERCYCLICAL. Delinquency is a lagging credit indicator.

The tournament runs on scripts/harness (spec: scripts/pair_spec_cc_delinquency_spy.py) on two tracks:
  * MAIN, "As known at the time": real-time DRCCLACBN vintages (ALFRED archive from 2011-05), signals and rolling
    thresholds computed inside the vintage visible when each quarter's return window opens.
  * COMPARISON, "As revised today (hindsight)": today's revised values with point-in-time release timing.
Evidence and metadata stages below are computed on the revised panel (descriptive).
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import pair_spec_cc_delinquency_spy as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "cc_delinquency_spy"
DATE_TAG = "20261017"  # Phase B B0 pilot: harness, two tracks, D9 plateau, null K=100, bootstrap
TARGET_SYMBOL = "SPY"
COST_BPS = 5
DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
NOW_ISO = datetime.now(timezone.utc).isoformat()
PERIODS_PER_YEAR = 4
SIGNALS = spec_mod.SIGNALS
SIGNAL_DISPLAY = spec_mod.SIGNAL_DISPLAY


def build_panel() -> pd.DataFrame:
    """Revised DRCCLACBN (latest pinned ALFRED vintage) and SPY quarter-end closes on the full quarterly grid."""
    idx = spec_mod.rebalance_index()
    df = spec_mod.revised_levels().reindex(idx)
    df["spy"] = spec_mod.target_prices().reindex(idx)
    df["spy_ret"] = df["spy"].pct_change()
    for h in (1, 2, 4):
        df[f"spy_fwd_{h}q"] = df["spy"].pct_change(h).shift(-h)
    full = spec_mod.features(spec_mod.revised_levels())
    for col in SIGNALS.values():
        df[col] = full[col].reindex(idx)
    df.to_parquet(DATA_DIR / "cc_delinquency_spy_quarterly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_cc_delinquency_spy_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_cc_delinquency_spy_{DATE_TAG}.md")
    pd.DataFrame([
        {"Column Name": "ccdelinq", "Display Name": "Credit Card Delinquency Rate",
         "Description": "Delinquency rate on credit-card loans (% of balances 30+ days past due), not seasonally adjusted",
         "Source": "FRB via ALFRED (pinned vintages)", "Series ID": "DRCCLACBN", "Unit": "Percent",
         "Transformation": "Quarterly level (NSA)",
         "Direction Convention": "Higher = more household credit stress (bearish equities)",
         "Effective Start": str(df["ccdelinq"].first_valid_index().date()),
         "Known Quirks": "Bounded rate, mean-reverting; lagging-to-coincident credit measure; NOT seasonally adjusted (DRCCLACBN); real-time vintages exist from 2011-05",
         "Display Note": "Rising credit-card delinquency accompanies household stress and equity weakness.",
         "Refresh Freq.": "Quarterly", "Refresh Source": "data/release_calendar/vintages/DRCCLACBN.csv.gz"},
        {"Column Name": "spy", "Display Name": "SPY adjusted close", "Description": "SPDR S&P 500 ETF adjusted close",
         "Source": "Yahoo Finance (pinned)", "Series ID": "SPY", "Unit": "USD", "Transformation": "Quarter-end adjusted close",
         "Direction Convention": "Higher = higher equity price", "Effective Start": str(df["spy"].first_valid_index().date()),
         "Known Quirks": "ETF history begins 1993", "Display Note": "Equity target and benchmark.",
         "Refresh Freq.": "Daily", "Refresh Source": "data/phaseB_inputs/spy_month_end_20261017.csv"},
    ]).to_csv(DATA_DIR / f"data_dictionary_cc_delinquency_spy_{DATE_TAG}.csv", index=False)
    print(f"  Panel rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def run_tournament() -> tuple[pd.DataFrame, dict, dict]:
    out = run_pair(PAIR_ID, DATE_TAG, K=100, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "strategy_description": "Hold SPY when the lagged delinquency signal is on the favourable side of its "
                                "threshold; otherwise hold cash.",
        "notes": "Credit-card delinquency is a quarterly, lagging credit-stress measure. Headline = as known at the "
                 "time (real-time vintages from 2011), so the training period is short; still a search-selected rule."})
    winner = json.loads((RES / "winner_summary.json").read_text())
    tourn = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["main"]
    if res.selection is not None:
        ws = winner_series(res, res.selection["winner"])
        log = trade_log(ws, TARGET_SYMBOL, COST_BPS, f"{winner['signal_code']} {winner['direction']} rule crossed "
                                                      f"{winner['threshold_code']}")
        log.to_csv(RES / "winner_trade_log.csv", index=False)
        log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, winner, out


def stationarity_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ["ccdelinq_level", "ccdelinq_diff_1q", "ccdelinq_chg_4q", "ccdelinq_zscore_20q", "spy_ret"]:
        s = df[col].dropna()
        if len(s) < 20:
            continue
        try:
            adf = adfuller(s, autolag="AIC")
            rows.append({"variable": col, "test": "ADF", "statistic": adf[0], "p_value": adf[1],
                         "lags": adf[2], "conclusion": "stationary" if adf[1] < 0.05 else "unit_root_not_rejected"})
        except Exception as exc:
            rows.append({"variable": col, "test": "ADF", "statistic": np.nan, "p_value": np.nan, "lags": np.nan, "conclusion": f"err:{exc}"})
        try:
            kp = kpss(s, regression="c", nlags="auto")
            rows.append({"variable": col, "test": "KPSS", "statistic": kp[0], "p_value": kp[1],
                         "lags": kp[2], "conclusion": "stationary_not_rejected" if kp[1] > 0.05 else "nonstationary"})
        except Exception as exc:
            rows.append({"variable": col, "test": "KPSS", "statistic": np.nan, "p_value": np.nan, "lags": np.nan, "conclusion": f"err:{exc}"})
    out = pd.DataFrame(rows)
    out.to_csv(RES / f"stationarity_tests_{DATE_TAG}.csv", index=False)
    return out




def ann_metrics(rets: pd.Series) -> dict[str, float]:
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return {"oos_sharpe": 0.0, "oos_sortino": 0.0, "oos_calmar": 0.0, "oos_ann_return": 0.0,
                "oos_ann_vol": 0.0, "max_drawdown": 0.0, "win_rate": 0.0, "oos_n": int(len(rets))}
    ppy = PERIODS_PER_YEAR
    ann_return = (1 + rets).prod() ** (ppy / len(rets)) - 1
    ann_vol = rets.std() * np.sqrt(ppy)
    sharpe = rets.mean() / rets.std() * np.sqrt(ppy)
    neg = rets[rets < 0]
    sortino = ann_return / (neg.std() * np.sqrt(ppy)) if len(neg) > 1 and neg.std() > 0 else 0.0
    equity = (1 + rets).cumprod()
    max_dd = (equity / equity.cummax() - 1).min()
    calmar = ann_return / abs(max_dd) if max_dd < 0 else 0.0
    return {"oos_sharpe": float(sharpe), "oos_sortino": float(sortino), "oos_calmar": float(calmar),
            "oos_ann_return": float(ann_return), "oos_ann_vol": float(ann_vol),
            "max_drawdown": float(max_dd), "win_rate": float((rets > 0).mean()), "oos_n": int(len(rets))}




REP_SIGNAL = "ccdelinq_chg_4q"


def write_evidence(df: pd.DataFrame, tourn: pd.DataFrame, winner: dict) -> None:
    from scipy import stats
    from statsmodels.tsa.stattools import grangercausalitytests
    tcols = ["spy_fwd_1q", "spy_fwd_2q", "spy_fwd_4q"]
    corr_rows = []
    for sc, col in SIGNALS.items():
        for fwd in tcols:
            sub = df[[col, fwd]].dropna()
            if len(sub) < 16:
                continue
            r, p = stats.pearsonr(sub[col], sub[fwd])
            corr_rows.append({"pair_name": f"{col}_to_{fwd}", "metric": "pearson", "value": r, "p_value": p})
    pd.DataFrame(corr_rows).to_csv(CORE / "correlations.csv", index=False)
    granger_rows = []
    g = df[["spy_ret", REP_SIGNAL]].dropna()
    if len(g) > 40:
        tests = grangercausalitytests(g[["spy_ret", REP_SIGNAL]], maxlag=4, verbose=False)
        for lag, res in tests.items():
            f, p, _, _ = res[0]["ssr_ftest"]
            granger_rows.append({"lag": lag, "f_stat": f, "p_value": p, "direction": "signal_to_SPY"})
    pd.DataFrame(granger_rows).to_csv(CORE / "granger_causality.csv", index=False)
    pd.DataFrame(granger_rows).to_csv(RES / "granger_by_lag.csv", index=False)
    ccf_rows = []
    x, y = df[REP_SIGNAL], df["spy_ret"]
    for lag in range(-4, 5):
        sub = pd.concat([x.shift(lag), y], axis=1).dropna()
        c = sub.iloc[:, 0].corr(sub.iloc[:, 1]) if len(sub) > 16 else np.nan
        ci = 1.96 / np.sqrt(max(len(sub), 1))
        ccf_rows.append({"lag": lag, "ccf": c, "upper_ci": ci, "lower_ci": -ci, "significant": abs(c) > ci if pd.notna(c) else False})
    pd.DataFrame(ccf_rows).to_csv(CORE / "ccf_prewhitened.csv", index=False)
    q = pd.qcut(df[REP_SIGNAL].dropna(), 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q_rows = []
    for lab in ["Q1", "Q2", "Q3", "Q4"]:
        rets = df.loc[q[q == lab].index, "spy_ret"].dropna()
        m = ann_metrics(rets)
        q_rows.append({"quartile": lab, "mean_return": rets.mean(), "sharpe": m["oos_sharpe"], "n": len(rets)})
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)
    rcorr = []
    for dt in df.index:
        w = df.loc[:dt, [REP_SIGNAL, "spy_ret"]].tail(20).dropna()
        if len(w) >= 12:
            rcorr.append({"date": dt, "rolling_corr": w[REP_SIGNAL].corr(w["spy_ret"])})
    pd.DataFrame(rcorr).to_csv(RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    rc = pd.DataFrame(rcorr)
    maz = float(((rc["rolling_corr"] - rc["rolling_corr"].mean()) / rc["rolling_corr"].std()).abs().max()) if not rc.empty and rc["rolling_corr"].std() > 0 else 0.0
    (RES / f"structural_break_{PAIR_ID}.json").write_text(json.dumps({"pair_id": PAIR_ID, "method": "rolling-correlation z-score proxy", "max_abs_z": maz}, indent=2) + "\n")
    lp_rows = []
    for h in [1, 2, 4]:
        sub = df[[REP_SIGNAL, f"spy_fwd_{h}q"]].dropna()
        if len(sub) > 16:
            sl, ic, r, p, se = stats.linregress(sub[REP_SIGNAL], sub[f"spy_fwd_{h}q"])
            lp_rows.append({"horizon": h, "coef": sl, "p_value": p, "r_squared": r * r})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)
    # #243 fix (found in the Phase B port): the previous loop ran OLS three times and ignored the quantile, so
    # every row carried the same slope. Real QuantReg per tau plus the cross-quantile equality Wald test.
    from _quantile_regression import DEFAULT_QUANTILES, fit_quantile_regression
    sub = df[[REP_SIGNAL, "spy_fwd_2q"]].dropna()
    qr_rows, qr_test = fit_quantile_regression(sub[REP_SIGNAL], sub["spy_fwd_2q"], DEFAULT_QUANTILES)
    pd.DataFrame(qr_rows).to_csv(CORE / "quantile_regression.csv", index=False)
    (CORE / "quantile_equality_test.json").write_text(json.dumps(qr_test, indent=2) + "\n")
    subs = [("Dot_Com", "2000-03-31", "2002-10-31"), ("GFC", "2007-12-31", "2009-06-30"),
            ("COVID", "2020-02-29", "2020-06-30"), ("Rate_Hike_2022", "2022-01-31", "2022-12-31")]
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    sp_rows = []
    for name, s, e in subs:
        sr = strat.loc[s:e, "strategy_return"]; br = strat.loc[s:e, "benchmark_return"]
        sp_rows.append({"period": name, "strategy_sharpe": ann_metrics(sr)["oos_sharpe"], "buy_hold_sharpe": ann_metrics(br)["oos_sharpe"],
                        "strategy_return": (1 + sr).prod() - 1, "buy_hold_return": (1 + br).prod() - 1})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)
    stationarity_report(df)
    # R6.8 honest names: share of valid combos with OOS >= winner = percentile in the grid, not a p-value.
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    pct_in_grid = float((valid["oos_sharpe"] >= winner["oos_sharpe"]).mean())
    bs = winner["selection"]["inference"]["oos_sharpe_diff_vs_bh_bootstrap"]
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"], "strategy": winner["strategy_family"],
                   "track": "as known at the time", "oos_sharpe": winner["oos_sharpe"],
                   "oos_percentile_in_grid": pct_in_grid, "sharpe_diff_vs_bh": bs["observed"],
                   "ci_95_low": bs["ci_95"][0], "ci_95_high": bs["ci_95"][1], "p_diff_le_0": bs["p_diff_le_0"],
                   "method": bs["method"], "block_length": bs["block_length"], "draws": bs["draws"],
                   "seed": bs["seed"]}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"], "strategy": winner["strategy_family"],
                   "tx_cost_bps": COST_BPS, "gross_sharpe": winner["oos_sharpe"]}]).to_csv(VALID / "transaction_costs.csv", index=False)


def write_metadata(df: pd.DataFrame, winner: dict, elapsed: float) -> None:
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "lagging", "indicator_type": "credit",
        "strategy_objective": "countercyclical_protection",
        "owner_writes": {"dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
                         "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
                         "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"]},
        "last_updated_by": "ray", "last_updated_at": NOW_ISO, "indicator": "ccdelinq", "target": "spy",
        "expected_direction": "countercyclical", "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "countercyclical",
        "mechanism": "Rising credit-card delinquency reflects deteriorating household balance sheets and precedes/accompanies consumption slowdowns and recessions; equity exposure should be reduced when delinquency is high or rising. Delinquency is a lagging-to-coincident credit-stress measure.",
        "confidence": "low",
        "key_finding": f"As known at the time (real-time DRCCLACBN vintages from {winner['tracks']['main']['sample']['first_vintage']}), "
                       f"the rule selected on in-sample data uses {winner['signal_code']} at L{winner['lead_value']}q with OOS Sharpe "
                       f"{winner['oos_sharpe']:.2f} versus buy-and-hold {winner['bh_sharpe']:.2f}.",
        "caveats": ["Quarterly survey with a small OOS window — winner is search-selected, needs holdout validation.", "Delinquency is lagging; leads should be read with care.", "Few distinct stress cycles in the sample; the real-time (as known at the time) archive starts in 2011, so the training period is short.", "Series is DRCCLACBN, NOT seasonally adjusted: its quarterly seasonal swings of up to ~0.15 pp vs the seasonally adjusted series can affect level-vs-rolling-percentile signals."],
        "narrative_summary": "Credit-card delinquency is tested as a countercyclical household-credit-stress overlay for SPY — reduce exposure when delinquency is high.",
        "known_stress_episodes": [{"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "NBER recession."}, {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30", "note": "Delinquencies spiked."}, {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "NBER recession."}, {"label": "2022 drawdown", "start": "2022-01-01", "end": "2022-12-31", "note": "Rate-hike bear market."}],
        "data_provenance": {"source": "FRB via ALFRED (pinned vintages data/release_calendar/vintages/DRCCLACBN.csv.gz)", "series_id": "DRCCLACBN", "accessed_at": NOW_ISO}}
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan", "last_updated_at": NOW_ISO,
        "indicator_axis": {"canonical_column": "ccdelinq", "display_name": "Credit Card Delinquency Rate",
            "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch} for c, d, f, r, ch in [
                ("ccdelinq", "Credit-card delinquency rate (%)", "Data Master (FRB)", "raw", ["hero"]),
                ("ccdelinq_level", "Delinquency level (%)", "identity", "threshold_input", ["hero", "regime_stats"]),
                ("ccdelinq_diff_1q", "Quarter-on-quarter change", "x_t - x_{t-1}", "derivative", []),
                ("ccdelinq_chg_4q", "4-quarter change", "x_t - x_{t-4}", "threshold_input", ["local_projections"]),
                ("ccdelinq_zscore_20q", "Level vs 5-year history", "(x-mean20q)/std20q", "threshold_input", [])]]},
        "target_axis": {"canonical_column": "spy", "display_name": "SPY adjusted close",
            "derivatives": [{"name": "spy", "definition": "SPY adjusted quarter-end close", "formula": "quarter-end adjusted close", "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "SPY quarterly return", "formula": "spy_t/spy_{t-1}-1", "role": "derivative", "appears_in_charts": []},
                {"name": "spy_fwd_1q", "definition": "1-quarter forward SPY return", "formula": "spy_{t+1}/spy_t-1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_2q", "definition": "2-quarter forward SPY return", "formula": "spy_{t+2}/spy_t-1", "role": "derivative", "appears_in_charts": ["local_projections", "quantile_coef"]},
                {"name": "spy_fwd_4q", "definition": "4-quarter forward SPY return", "formula": "spy_{t+4}/spy_t-1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]}]},
        "notes": "Scope limited to Credit Card Delinquency Rate signals and SPY returns."}
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"],
        "benchmark_oos_sharpe": winner["bh_sharpe"], "oos_max_drawdown": winner["oos_max_drawdown"], "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    (RES / "evidence_status.json").write_text(json.dumps({"pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search",
        "updated_at": NOW_ISO, "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": f"Winner selected on in-sample data by the lead-plateau rule (D9) from the {DATE_TAG} quarterly tournament on real-time DRCCLACBN vintages and evaluated on the held-out OOS window; the training and OOS windows are small.",
        "next_step": "Freeze the selected rule and run a confirmation test on future data.", "owner": "evan"}, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    (RES / "analyst_suggestions.json").write_text(json.dumps({"pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{"signal_name": "Lead robustness", "proposed_by": "evan", "source": "ALFRED / FRB",
            "observation": f"The rule uses an L{winner['lead_value']}q lead on {winner['signal_code']}; verify adjacent-lead durability.",
            "rationale": "Cycles in the sample are few, so the lead needs adjacent-lead durability and a cycle-count caveat.",
            "possible_use_case": "robustness check", "caveats": "Search-selected on a small quarterly OOS; needs final-exam validation.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:]}], "notes": "Generated with the Credit Card Delinquency Rate x SPY pair pipeline."}, indent=2) + "\n")


def main() -> None:
    t0 = time.time()
    for path in (RES, CORE, VALID):
        path.mkdir(parents=True, exist_ok=True)
    df = build_panel()
    df[list(SIGNALS.values())].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    tourn, winner, _ = run_tournament()
    write_evidence(df, tourn, winner)
    write_metadata(df, winner, time.time() - t0)
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
