#!/usr/bin/env python3
"""Pair pipeline: Building Permits (PERMIT) x SPY (Phase B harness).

The tournament runs on scripts/harness (spec: scripts/pair_spec_permit_spy.py) on two tracks:
  * MAIN, "As known at the time": real-time PERMIT vintages (ALFRED), each rebalance uses the vintage visible when
    its return window opens; signals and rolling thresholds are computed inside that vintage.
  * COMPARISON, "As revised today (hindsight)": today's revised values with point-in-time release timing.
Each track selects its own winner by the D9 lead-plateau rule on in-sample data; null tournament K=100,
paired block bootstrap vs buy-and-hold, leak tests. This file keeps the pair's evidence and metadata stages
(computed on the revised panel, descriptive).

The published pre-harness rule (S3_mom / T1_p25 / P3 / L6, OOS-selected, 20260314) is not replayable through the
harness; its legacy-code reproduction is scripts/legacy_repro/permit_spy.py (run first by main()).
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from legacy_repro import permit_spy as legacy_repro_permit_spy  # noqa: E402
import pair_spec_permit_spy as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series  # noqa: E402
from harness.evidence import write_evidence_facts  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "permit_spy"
DATE_TAG = "20261017"  # Phase B B1: harness, two tracks, D9 plateau, null K=100, bootstrap
TARGET_SYMBOL = "SPY"
COST_BPS = 5
EVIDENCE_SIGNAL = "permit_yoy"   # year-over-year change: the smooth transform used by the descriptive tests
DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
NOW_ISO = datetime.now(timezone.utc).isoformat()
SIGNALS = spec_mod.SIGNALS


def ann_metrics(rets: pd.Series) -> dict[str, float]:
    """Monthly performance block used by the evidence tables (sub-period, quartile)."""
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return {"oos_sharpe": 0.0, "oos_ann_return": 0.0, "max_drawdown": 0.0, "oos_n": int(len(rets))}
    equity = (1 + rets).cumprod()
    return {"oos_sharpe": float(rets.mean() / rets.std() * np.sqrt(12)),
            "oos_ann_return": float((1 + rets).prod() ** (12 / len(rets)) - 1),
            "max_drawdown": float((equity / equity.cummax() - 1).min()), "oos_n": int(len(rets))}


def build_panel() -> pd.DataFrame:
    """Revised PERMIT (latest pinned ALFRED vintage) and SPY month-end closes on the full monthly grid."""
    idx = spec_mod.rebalance_index()
    lv = spec_mod.revised_levels()
    df = lv.reindex(idx)
    df["spy"] = spec_mod.target_prices().reindex(idx)
    df["spy_ret"] = df["spy"].pct_change()
    for horizon in (1, 3, 6, 12):
        df[f"spy_fwd_{horizon}m"] = df["spy"].pct_change(horizon).shift(-horizon)
    full = spec_mod.features(lv)
    for col in SIGNALS.values():
        if col != "permit":
            df[col] = full[col].reindex(idx)
    df.to_parquet(DATA_DIR / "permit_spy_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_permit_spy_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_permit_spy_{DATE_TAG}.md")
    pd.DataFrame([
        {"Column Name": "permit", "Display Name": "Building permits", "Description": "New private housing units "
         "authorized by building permits", "Source": "FRED / ALFRED (pinned vintages)", "Series ID": "PERMIT",
         "Unit": "Thousands of units, SAAR", "Transformation": "Monthly level", "Seasonal Adj.": "Seasonally adjusted",
         "Direction Convention": "Higher = more planned residential construction",
         "Effective Start": str(df["permit"].first_valid_index().date()),
         "Known Quirks": "Revised (monthly and annual seasonal-factor revisions); published about three weeks after month end",
         "Display Note": "Builders apply for permits before they start construction.",
         "Refresh Freq.": "Monthly", "Refresh Source": "data/release_calendar/vintages/PERMIT.csv.gz"},
        {"Column Name": "spy", "Display Name": "SPY adjusted close", "Description": "SPDR S&P 500 ETF adjusted close",
         "Source": "Yahoo Finance (pinned)", "Series ID": "SPY", "Unit": "USD",
         "Transformation": "Month-end adjusted close", "Seasonal Adj.": "N/A",
         "Direction Convention": "Higher = higher equity price",
         "Effective Start": str(df["spy"].first_valid_index().date()), "Known Quirks": "ETF history begins in 1993",
         "Display Note": "Used as the equity-market target and benchmark.", "Refresh Freq.": "Daily",
         "Refresh Source": "data/phaseB_inputs/spy_month_end_20261017.csv"},
    ]).to_csv(DATA_DIR / f"data_dictionary_permit_spy_{DATE_TAG}.csv", index=False)
    print(f"  Panel rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def trade_reason(winner: dict) -> str:
    if winner["threshold_code"] == "-":      # P2 sizes on the trailing 60-month range: no threshold crossing
        return f"{winner['signal_code']} {winner['direction']} position resized to the trailing-range reading"
    return f"{winner['signal_code']} {winner['direction']} rule crossed {winner['threshold_code']}"


def run_tournament() -> tuple[pd.DataFrame, dict, dict]:
    out = run_pair(PAIR_ID, DATE_TAG, K=100, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "lookback": "LB60 where rolling thresholds apply",
        "strategy_description": "Position in SPY set by the lagged building-permits signal relative to its "
                                "threshold (P1 long/cash, P2 sized by the trailing range, P3 long/short).",
        "notes": "Building permits are a leading housing indicator. Headline = as known at the time (real-time "
                 "vintages); still a search-selected rule. The published 20260314 rule was OOS-selected and is "
                 "not replayable through the harness (see legacy_reproduction_20260314.json)."})
    winner = json.loads((RES / "winner_summary.json").read_text())
    tourn = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["main"]
    ws = winner_series(res, res.selection["winner"])
    log = trade_log(ws, TARGET_SYMBOL, COST_BPS, trade_reason(winner))
    log.to_csv(RES / "winner_trade_log.csv", index=False)
    log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, winner, out


def write_evidence(df: pd.DataFrame, tourn: pd.DataFrame, winner: dict) -> None:
    x_col = EVIDENCE_SIGNAL
    target_cols = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]
    corr_rows = []
    for col in SIGNALS.values():
        for fwd in target_cols:
            sub = df[[col, fwd]].dropna()
            if len(sub) < 20 or sub[col].std() == 0:
                continue
            r, p = stats.pearsonr(sub[col], sub[fwd])
            corr_rows.append({"pair_name": f"{col}_to_{fwd}", "metric": "pearson", "value": r, "p_value": p})
    pd.DataFrame(corr_rows).to_csv(CORE / "correlations.csv", index=False)

    granger_rows = []
    gdata = df[["spy_ret", x_col]].dropna()
    tests = grangercausalitytests(gdata[["spy_ret", x_col]], maxlag=12, verbose=False)
    for lag, res in tests.items():
        f_stat, p_val, _, _ = res[0]["ssr_ftest"]
        granger_rows.append({"lag": lag, "f_stat": f_stat, "p_value": p_val, "direction": "PERMIT_to_SPY"})
    pd.DataFrame(granger_rows).to_csv(CORE / "granger_causality.csv", index=False)
    pd.DataFrame(granger_rows).to_csv(RES / "granger_by_lag.csv", index=False)

    ccf_rows = []
    x = df[x_col].diff()      # pre-whitening by first differences (the YoY change is persistent)
    y = df["spy_ret"]
    for lag in range(-12, 13):
        sub = pd.concat([x.shift(lag), y], axis=1).dropna()
        corr = sub.iloc[:, 0].corr(sub.iloc[:, 1]) if len(sub) > 20 else np.nan
        band = 1.96 / np.sqrt(max(len(sub), 1))
        ccf_rows.append({"lag": lag, "ccf": corr, "upper_ci": band, "lower_ci": -band,
                         "significant": bool(abs(corr) > band) if pd.notna(corr) else False})
    pd.DataFrame(ccf_rows).to_csv(CORE / "ccf_prewhitened.csv", index=False)

    sub = df[[x_col, "spy_ret"]].dropna()
    q = pd.qcut(sub[x_col], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q_rows = []
    for label in ["Q1", "Q2", "Q3", "Q4"]:
        rets = sub.loc[q == label, "spy_ret"]
        q_rows.append({"quartile": label, "mean_return": rets.mean(), "sharpe": ann_metrics(rets)["oos_sharpe"],
                       "n": len(rets), "yoy_low": float(sub.loc[q == label, x_col].min()),
                       "yoy_high": float(sub.loc[q == label, x_col].max())})
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)

    rcorr = []
    for dt in df.index:
        window = df.loc[:dt, [x_col, "spy_ret"]].tail(60).dropna()
        if len(window) >= 36:
            rcorr.append({"date": dt, "rolling_corr": window[x_col].corr(window["spy_ret"])})
    rc = pd.DataFrame(rcorr)
    rc.to_csv(RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    max_abs_z = 0.0
    if not rc.empty and rc["rolling_corr"].std() > 0:
        max_abs_z = float(((rc["rolling_corr"] - rc["rolling_corr"].mean()) / rc["rolling_corr"].std()).abs().max())
    (RES / f"structural_break_{PAIR_ID}.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "method": "rolling-correlation z-score proxy", "max_abs_z": max_abs_z},
                   indent=2) + "\n")

    lp_rows = []
    for h in [1, 3, 6, 12]:
        s = df[[x_col, f"spy_fwd_{h}m"]].dropna()
        slope, intercept, r, p, se = stats.linregress(s[x_col], s[f"spy_fwd_{h}m"])
        lp_rows.append({"horizon": h, "coef": slope, "p_value": p, "r_squared": r * r})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)

    from _quantile_regression import DEFAULT_QUANTILES, fit_quantile_regression
    qs = df[[x_col, "spy_fwd_3m"]].dropna()
    qr_rows, qr_test = fit_quantile_regression(qs[x_col], qs["spy_fwd_3m"], DEFAULT_QUANTILES)
    pd.DataFrame(qr_rows).to_csv(CORE / "quantile_regression.csv", index=False)
    (CORE / "quantile_equality_test.json").write_text(json.dumps(qr_test, indent=2) + "\n")

    subperiods = [("Dot_Com", "2000-03-31", "2002-10-31"), ("GFC", "2007-12-31", "2009-06-30"),
                  ("COVID", "2020-02-29", "2020-04-30"), ("Rate_Hike_2022", "2022-01-31", "2022-12-31")]
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    sp_rows = []
    for name, start, end in subperiods:
        sret = strat.loc[start:end, "strategy_return"]
        bret = strat.loc[start:end, "benchmark_return"]
        sp_rows.append({"period": name, "strategy_sharpe": ann_metrics(sret)["oos_sharpe"],
                        "buy_hold_sharpe": ann_metrics(bret)["oos_sharpe"], "strategy_return": (1 + sret).prod() - 1,
                        "buy_hold_return": (1 + bret).prod() - 1})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)

    station_rows = []
    for col in ["permit", "permit_yoy", "permit_mom", "spy_ret"]:
        s = df[col].dropna()
        adf = adfuller(s, autolag="AIC")
        station_rows.append({"variable": col, "test": "ADF", "statistic": adf[0], "p_value": adf[1], "lags": adf[2],
                             "conclusion": "stationary" if adf[1] < 0.05 else "unit_root_not_rejected"})
        kp = kpss(s, regression="c", nlags="auto")
        station_rows.append({"variable": col, "test": "KPSS", "statistic": kp[0], "p_value": kp[1], "lags": kp[2],
                             "conclusion": "stationary_not_rejected" if kp[1] > 0.05 else "nonstationary"})
    pd.DataFrame(station_rows).to_csv(RES / f"stationarity_tests_{DATE_TAG}.csv", index=False)

    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    pct_in_grid = float((valid["oos_sharpe"] >= winner["oos_sharpe"]).mean())
    bs = winner["selection"]["inference"]["oos_sharpe_diff_vs_bh_bootstrap"]
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "track": "as known at the time",
                   "oos_sharpe": winner["oos_sharpe"], "oos_percentile_in_grid": pct_in_grid,
                   "sharpe_diff_vs_bh": bs["observed"], "ci_95_low": bs["ci_95"][0], "ci_95_high": bs["ci_95"][1],
                   "p_diff_le_0": bs["p_diff_le_0"], "method": bs["method"], "block_length": bs["block_length"],
                   "draws": bs["draws"], "seed": bs["seed"]}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "tx_cost_bps": COST_BPS,
                   "gross_sharpe": winner["oos_sharpe"]}]).to_csv(VALID / "transaction_costs.csv", index=False)


def write_metadata(df: pd.DataFrame, winner: dict, elapsed: float) -> None:
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "leading", "indicator_type": "production",
        "strategy_objective": "max_sharpe",
        "owner_writes": {
            "dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"],
        },
        "last_updated_by": "ray", "last_updated_at": NOW_ISO, "indicator": "permit", "target": "spy",
        "expected_direction": "procyclical", "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "procyclical",
        "mechanism": "Rising building permits signal planned residential construction, which feeds employment, "
                     "materials demand and household wealth; a pro-cyclical reading is bullish for equities.",
        "confidence": "low",
        "key_finding": f"As known at the time (real-time PERMIT vintages), the rule selected on in-sample data uses "
                       f"{winner['signal_code']} at L{winner['lead_value']} (IS Sharpe {winner['is_sharpe']:.2f}) "
                       f"with held-out OOS Sharpe {winner['oos_sharpe']:.2f} versus buy-and-hold "
                       f"{winner['bh_sharpe']:.2f}.",
        "caveats": [
            "Building permits are revised, including annual seasonal-factor revisions; the headline uses the values "
            "as published at each date (ALFRED vintages) and the as-revised-today result is shown for comparison only.",
            "The strategy is search-selected and needs fresh holdout validation.",
            "The previously published rule was selected on its test-period score and is replaced here.",
        ],
        "narrative_summary": "Building permits are tested as a leading housing-cycle signal for SPY allocation.",
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30",
             "note": "Housing held up while equities fell."},
            {"label": "Housing bust and Global Financial Crisis", "start": "2006-01-01", "end": "2009-06-30",
             "note": "Permits fell for several years before and during the recession."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-06-30",
             "note": "Brief collapse, then a fast rebound."},
        ],
        "data_provenance": {"source": "FRED", "series_id": "PERMIT", "accessed_at": NOW_ISO},
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    defs = [
        ("permit", "Building permits level (thousands of units, SAAR)", "FRED PERMIT", "raw", ["hero"]),
        ("permit_yoy", "Year-over-year percent change", "(x_t / x_{t-12} - 1) * 100", "derivative",
         ["regime_stats", "local_projections", "quantile_coef"]),
        ("permit_mom", "Month-over-month percent change", "(x_t / x_{t-1} - 1) * 100", "derivative", []),
        ("permit_dev_trend", "Level minus its 12-month average", "x_t - mean12", "derivative", []),
        ("permit_zscore_60m", "Level versus its five-year history", "(x - mean60)/std60", "derivative", []),
        ("permit_mom_3m", "Three-month change in level", "x_t - x_{t-3}", "derivative", []),
        ("permit_mom_6m", "Six-month change in level", "x_t - x_{t-6}", "derivative", []),
        ("permit_accel", "Change in the monthly percent change", "mom_t - mom_{t-1}", "derivative", []),
        ("permit_contraction", "Year-over-year change below zero", "1[yoy < 0]", "regime_state", []),
    ]
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {"canonical_column": "permit", "display_name": "Building Permits (PERMIT)",
                           "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch}
                                           for c, d, f, r, ch in defs]},
        "target_axis": {
            "canonical_column": "spy", "display_name": "SPY adjusted close",
            "derivatives": [
                {"name": "spy", "definition": "SPY adjusted month-end close", "formula": "month-end adjusted close",
                 "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "SPY monthly return", "formula": "spy_t / spy_{t-1} - 1",
                 "role": "derivative", "appears_in_charts": []},
                {"name": "spy_fwd_1m", "definition": "One-month forward SPY return", "formula": "spy_{t+1} / spy_t - 1",
                 "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_3m", "definition": "Three-month forward SPY return",
                 "formula": "spy_{t+3} / spy_t - 1", "role": "derivative",
                 "appears_in_charts": ["local_projections", "quantile_coef"]},
                {"name": "spy_fwd_6m", "definition": "Six-month forward SPY return", "formula": "spy_{t+6} / spy_t - 1",
                 "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_12m", "definition": "Twelve-month forward SPY return",
                 "formula": "spy_{t+12} / spy_t - 1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
            ],
        },
        "notes": "Scope limited to PERMIT-derived housing signals and SPY returns.",
    }
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"],
                                               "benchmark_oos_sharpe": winner["bh_sharpe"],
                                               "oos_max_drawdown": winner["oos_max_drawdown"],
                                               "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    evidence_status = {
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search", "updated_at": NOW_ISO,
        "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": f"Winner selected on in-sample data by the lead-plateau rule (D9) from the {DATE_TAG} "
                          "tournament on real-time PERMIT vintages and evaluated on the held-out OOS window.",
        "next_step": "Freeze the selected rule and run a confirmation test on future data or a reserved holdout window.",
        "owner": "evan",
    }
    (RES / "evidence_status.json").write_text(json.dumps(evidence_status, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    analyst_suggestions = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{
            "signal_name": "PERMIT revision robustness", "proposed_by": "evan", "source": "FRED",
            "observation": f"The rule selected on in-sample data uses a {winner['lead_value']}-month lead on the "
                           f"{winner['signal_display_name'].lower()} ({winner['direction']}, {winner['threshold_code']}); "
                           f"held-out OOS max drawdown {winner['oos_max_drawdown']:.1%} vs buy-and-hold "
                           f"{winner['bh_max_drawdown']:.1%}.",
            "rationale": "Permits are revised every year (seasonal factors), so deployment should track whether "
                         "real-time and revised readings keep giving the same signal.",
            "possible_use_case": "robustness check",
            "caveats": "Search-selected rule; the live tradability assumptions are not final-exam validated.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
        }],
        "notes": "Generated with the PERMIT x SPY pair pipeline.",
    }
    (RES / "analyst_suggestions.json").write_text(json.dumps(analyst_suggestions, indent=2) + "\n")


NARRATIVE_SOURCES = ["regime_quartile_returns.csv", "granger_by_lag.csv",
                     f"core_models_{DATE_TAG}/quantile_regression.csv",
                     f"core_models_{DATE_TAG}/quantile_equality_test.json",
                     f"core_models_{DATE_TAG}/local_projections.csv"]


def write_narrative_provenance() -> None:
    """evidence_facts_<tag>.json: the evidence tables the page prose cites (scripts/gate_number_provenance.py)."""
    # the Strategy page's trade-log caption counts the broker-style log rows (full reconstructed history)
    n_rows = len(pd.read_csv(RES / "winner_trades_broker_style.csv"))
    # test-period position changes of the MAIN winner, two counts (winner_summary oos_n_trades is the harness
    # abs_sum count: int(sum |position change|), i.e. full SPY units traded)
    sr = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv")
    d = np.abs(np.diff(sr.loc[sr["sample"] == "OOS", "position"].dropna().to_numpy(float)))
    write_evidence_facts(PAIR_ID, DATE_TAG, sources=NARRATIVE_SOURCES, derived={
        "trade_log_rows": n_rows,
        "position_change_threshold_pp": 5,
        "oos_months_position_change_gt_5pct": int((d > 0.05).sum()),
        "oos_sum_abs_position_change": round(float(d.sum()), 4)})


def main() -> None:
    t0 = time.time()
    for path in (RES, CORE, VALID):
        path.mkdir(parents=True, exist_ok=True)
    legacy_repro_permit_spy.main()
    df = build_panel()
    df[[c for c in SIGNALS.values() if c != "permit"]].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    tourn, winner, _ = run_tournament()
    write_evidence(df, tourn, winner)
    write_metadata(df, winner, time.time() - t0)
    write_narrative_provenance()
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
