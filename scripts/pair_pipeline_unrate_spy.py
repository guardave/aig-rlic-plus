#!/usr/bin/env python3
"""Pair pipeline: Unemployment Rate (UNRATE) x SPY (Phase B harness).

The tournament runs on scripts/harness (spec: scripts/pair_spec_unrate_spy.py) on two tracks:
  * MAIN, "As known at the time": real-time UNRATE vintages (ALFRED), each rebalance uses the vintage visible when
    its return window opens; signals and rolling thresholds are computed inside that vintage.
  * COMPARISON, "As revised today (hindsight)": today's revised values with point-in-time release timing.
Each track selects its own winner by the D9 lead-plateau rule on in-sample data; null tournament K=100,
paired block bootstrap vs buy-and-hold, leak tests. This file keeps the pair's evidence and metadata stages
(computed on the revised panel, descriptive).
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
import pair_spec_unrate_spy as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series  # noqa: E402
from harness.evidence import write_evidence_facts  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "unrate_spy"
DATE_TAG = "20261017"  # Phase B B0 pilot: harness, two tracks, D9 plateau, null K=100, bootstrap
TARGET_SYMBOL = "SPY"
COST_BPS = 5
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
    """Revised UNRATE (latest pinned ALFRED vintage) and SPY month-end closes on the full monthly grid (the
    unpublished 2025-10 UNRATE reading is a NaN row, so the 2025-11 SPY return is a one-month return)."""
    idx = spec_mod.rebalance_index()
    lv = spec_mod.revised_levels().reindex(idx)
    df = lv.copy()
    df["spy"] = spec_mod.target_prices().reindex(idx)
    df["spy_ret"] = df["spy"].pct_change()
    for horizon in (1, 3, 6, 12):
        df[f"spy_fwd_{horizon}m"] = df["spy"].pct_change(horizon).shift(-horizon)
    full = spec_mod.features(spec_mod.revised_levels())
    for col in SIGNALS.values():
        df[col] = full[col].reindex(idx)
    df["unrate_recession_flag"] = (df["unrate_sahm"] >= 0.5).astype(float).where(df["unrate_sahm"].notna())
    df.to_parquet(DATA_DIR / "unrate_spy_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_unrate_spy_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_unrate_spy_{DATE_TAG}.md")
    pd.DataFrame([
        {"Column Name": "unrate", "Display Name": "U.S. Unemployment Rate", "Description": "Civilian unemployment rate",
         "Source": "FRED / ALFRED (pinned vintages)", "Series ID": "UNRATE", "Unit": "Percent",
         "Transformation": "Monthly level", "Seasonal Adj.": "Seasonally adjusted",
         "Direction Convention": "Higher = weaker labor market / higher macro stress",
         "Effective Start": str(df["unrate"].first_valid_index().date()),
         "Known Quirks": "Lagging labor-market indicator; revised; 2025-10 never published (shutdown)",
         "Display Note": "Unemployment usually rises after the economy has already weakened.",
         "Refresh Freq.": "Monthly", "Refresh Source": "data/release_calendar/vintages/UNRATE.csv.gz"},
        {"Column Name": "spy", "Display Name": "SPY adjusted close", "Description": "SPDR S&P 500 ETF adjusted close",
         "Source": "Yahoo Finance (pinned)", "Series ID": "SPY", "Unit": "USD",
         "Transformation": "Month-end adjusted close", "Seasonal Adj.": "N/A",
         "Direction Convention": "Higher = higher equity price",
         "Effective Start": str(df["spy"].first_valid_index().date()), "Known Quirks": "ETF history begins in 1993",
         "Display Note": "Used as the equity-market target and benchmark.", "Refresh Freq.": "Daily",
         "Refresh Source": "data/phaseB_inputs/spy_month_end_20261017.csv"},
    ]).to_csv(DATA_DIR / f"data_dictionary_unrate_spy_{DATE_TAG}.csv", index=False)
    print(f"  Panel rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def run_tournament() -> tuple[pd.DataFrame, dict, dict]:
    out = run_pair(PAIR_ID, DATE_TAG, K=100, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "lookback": "LB60 where rolling thresholds apply",
        "strategy_description": "Hold SPY when the lagged unemployment signal is on the favourable side of its "
                                "threshold; otherwise hold cash.",
        "notes": "UNRATE is a lagging labor-market indicator; read the rule as defensive regime context, not a "
                 "leading forecast. Headline = as known at the time (real-time vintages); still a search-selected "
                 "rule."})
    winner = json.loads((RES / "winner_summary.json").read_text())
    tourn = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["main"]
    ws = winner_series(res, res.selection["winner"])
    log = trade_log(ws, TARGET_SYMBOL, COST_BPS, f"{winner['signal_code']} {winner['direction']} rule crossed "
                                                  f"{winner['threshold_code']}")
    log.to_csv(RES / "winner_trade_log.csv", index=False)
    log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, winner, out


def write_evidence(df: pd.DataFrame, tourn: pd.DataFrame, winner: dict) -> None:
    target_cols = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m", "spy_fwd_12m"]
    corr_rows = []
    for sig_code, col in SIGNALS.items():
        for fwd in target_cols:
            sub = df[[col, fwd]].dropna()
            if len(sub) < 20:
                continue
            r, p = stats.pearsonr(sub[col], sub[fwd])
            corr_rows.append({"pair_name": f"{col}_to_{fwd}", "metric": "pearson", "value": r, "p_value": p})
    pd.DataFrame(corr_rows).to_csv(CORE / "correlations.csv", index=False)

    granger_rows = []
    gdata = df[["spy_ret", "unrate_3m_chg"]].dropna()
    if len(gdata) > 80:
        tests = grangercausalitytests(gdata[["spy_ret", "unrate_3m_chg"]], maxlag=12, verbose=False)
        for lag, res in tests.items():
            f_stat, p_val, _, _ = res[0]["ssr_ftest"]
            granger_rows.append({"lag": lag, "f_stat": f_stat, "p_value": p_val, "direction": "UNRATE_to_SPY"})
    pd.DataFrame(granger_rows).to_csv(CORE / "granger_causality.csv", index=False)
    pd.DataFrame(granger_rows).to_csv(RES / "granger_by_lag.csv", index=False)

    ccf_rows = []
    x = df["unrate_3m_chg"]
    y = df["spy_ret"]
    for lag in range(-12, 13):
        sub = pd.concat([x.shift(lag), y], axis=1).dropna()
        corr = sub.iloc[:, 0].corr(sub.iloc[:, 1]) if len(sub) > 20 else np.nan
        ccf_rows.append({"lag": lag, "ccf": corr, "upper_ci": 1.96 / np.sqrt(max(len(sub), 1)), "lower_ci": -1.96 / np.sqrt(max(len(sub), 1)), "significant": abs(corr) > 1.96 / np.sqrt(max(len(sub), 1)) if pd.notna(corr) else False})
    pd.DataFrame(ccf_rows).to_csv(CORE / "ccf_prewhitened.csv", index=False)

    q = pd.qcut(df["unrate"].dropna(), 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q_rows = []
    for label in ["Q1", "Q2", "Q3", "Q4"]:
        idx = q[q == label].index
        rets = df.loc[idx, "spy_ret"].dropna()
        m = ann_metrics(rets)
        q_rows.append({"quartile": label, "mean_return": rets.mean(), "sharpe": m["oos_sharpe"], "n": len(rets)})
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)

    roll = df[["unrate_3m_chg", "spy_ret"]].rolling(60).corr().dropna()
    rcorr = []
    for dt in df.index:
        window = df.loc[:dt, ["unrate_3m_chg", "spy_ret"]].tail(60).dropna()
        if len(window) >= 36:
            rcorr.append({"date": dt, "rolling_corr": window["unrate_3m_chg"].corr(window["spy_ret"])})
    pd.DataFrame(rcorr).to_csv(RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)

    rc = pd.DataFrame(rcorr)
    max_abs_z = 0.0
    if not rc.empty and rc["rolling_corr"].std() > 0:
        max_abs_z = float(((rc["rolling_corr"] - rc["rolling_corr"].mean()) / rc["rolling_corr"].std()).abs().max())
    (RES / f"structural_break_{PAIR_ID}.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "method": "rolling-correlation z-score proxy", "max_abs_z": max_abs_z}, indent=2) + "\n"
    )

    lp_rows = []
    for h in [1, 3, 6, 12]:
        sub = df[["unrate_3m_chg", f"spy_fwd_{h}m"]].dropna()
        if len(sub) > 20:
            slope, intercept, r, p, se = stats.linregress(sub["unrate_3m_chg"], sub[f"spy_fwd_{h}m"])
            lp_rows.append({"horizon": h, "coef": slope, "p_value": p, "r_squared": r * r})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)

    # #243 fix: REAL quantile regression. The previous loop ran OLS
    # (stats.linregress) and never used `qtile`, so every quantile row
    # carried the identical slope — the chart always looked "flat across
    # quantiles" and narratives claimed "no tail asymmetry" from an analysis
    # that was never run. The shared helper fits statsmodels QuantReg per tau
    # and adds a bootstrap cross-quantile equality Wald test.
    import sys as _sys
    _qr_sp = str(REPO / "scripts")
    if _qr_sp not in _sys.path:
        _sys.path.insert(0, _qr_sp)
    from _quantile_regression import fit_quantile_regression, DEFAULT_QUANTILES
    _qr_sub = df[["unrate_3m_chg", "spy_fwd_3m"]].dropna()
    _qr_rows, _qr_test = fit_quantile_regression(
        _qr_sub["unrate_3m_chg"], _qr_sub["spy_fwd_3m"], DEFAULT_QUANTILES
    )
    pd.DataFrame(_qr_rows).to_csv(CORE / "quantile_regression.csv", index=False)
    (CORE / "quantile_equality_test.json").write_text(
        json.dumps(_qr_test, indent=2) + "\n"
    )

    subperiods = [
        ("Dot_Com", "2000-03-31", "2002-10-31"),
        ("GFC", "2007-12-31", "2009-06-30"),
        ("COVID", "2020-02-29", "2020-04-30"),
        ("Rate_Hike_2022", "2022-01-31", "2022-12-31"),
    ]
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    sp_rows = []
    for name, start, end in subperiods:
        sret = strat.loc[start:end, "strategy_return"]
        bret = strat.loc[start:end, "benchmark_return"]
        sp_rows.append({"period": name, "strategy_sharpe": ann_metrics(sret)["oos_sharpe"], "buy_hold_sharpe": ann_metrics(bret)["oos_sharpe"], "strategy_return": (1 + sret).prod() - 1, "buy_hold_return": (1 + bret).prod() - 1})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)

    station_rows = []
    for col in ["unrate", "unrate_3m_chg", "unrate_sahm", "spy_ret"]:
        s = df[col].dropna()
        try:
            adf = adfuller(s, autolag="AIC")
            station_rows.append({"variable": col, "test": "ADF", "statistic": adf[0], "p_value": adf[1], "lags": adf[2], "conclusion": "stationary" if adf[1] < 0.05 else "unit_root_not_rejected"})
        except Exception:
            pass
        try:
            kp = kpss(s, regression="c", nlags="auto")
            station_rows.append({"variable": col, "test": "KPSS", "statistic": kp[0], "p_value": kp[1], "lags": kp[2], "conclusion": "stationary_not_rejected" if kp[1] > 0.05 else "nonstationary"})
        except Exception:
            pass
    pd.DataFrame(station_rows).to_csv(RES / f"stationarity_tests_{DATE_TAG}.csv", index=False)

    # R6.8 honest names: the share of valid combos with OOS >= the winner is a percentile in the grid, not a
    # p-value; the inference is the paired block bootstrap of the Sharpe gap vs buy-and-hold (winner_summary).
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    pct_in_grid = float((valid["oos_sharpe"] >= winner["oos_sharpe"]).mean())
    bs = winner["selection"]["inference"]["oos_sharpe_diff_vs_bh_bootstrap"]
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"], "strategy": winner["strategy_family"],
                   "track": "as known at the time", "oos_sharpe": winner["oos_sharpe"],
                   "oos_percentile_in_grid": pct_in_grid, "sharpe_diff_vs_bh": bs["observed"],
                   "ci_95_low": bs["ci_95"][0], "ci_95_high": bs["ci_95"][1], "p_diff_le_0": bs["p_diff_le_0"],
                   "method": bs["method"], "block_length": bs["block_length"], "draws": bs["draws"],
                   "seed": bs["seed"]}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"], "strategy": winner["strategy_family"], "tx_cost_bps": COST_BPS, "gross_sharpe": winner["oos_sharpe"]}]).to_csv(VALID / "transaction_costs.csv", index=False)


def write_metadata(df: pd.DataFrame, winner: dict, elapsed: float) -> None:
    interp = {
        "pair_id": PAIR_ID,
        "schema_version": "1.1.0",
        "indicator_nature": "lagging",
        "indicator_type": "macro",
        "strategy_objective": "countercyclical_protection",
        "owner_writes": {
            "dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"],
        },
        "last_updated_by": "ray",
        "last_updated_at": NOW_ISO,
        "indicator": "unrate",
        "target": "spy",
        "expected_direction": "countercyclical",
        "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "countercyclical",
        "mechanism": "A rising unemployment rate usually reflects a weakening labor market and recession risk; equity exposure should be reduced when labor stress is elevated.",
        "confidence": "low",
        "key_finding": f"As known at the time (real-time UNRATE vintages), the rule selected on in-sample data uses {winner['signal_code']} at L{winner['lead_value']} (IS Sharpe {winner['is_sharpe']:.2f}) with held-out OOS Sharpe {winner['oos_sharpe']:.2f} versus buy-and-hold {winner['bh_sharpe']:.2f}.",
        "caveats": [
            "UNRATE is usually lagging, so it may confirm recessions after equities have already moved.",
            "The strategy is search-selected and needs fresh holdout validation.",
            "Monthly labor data is revised and released with a delay; the headline uses the values as published at each date (ALFRED vintages), and the as-revised-today result is shown only for comparison.",
        ],
        "narrative_summary": "UNRATE is tested as a defensive labor-market stress overlay for SPY, not as a clean leading indicator.",
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "Unemployment rose after the equity peak."},
            {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30", "note": "UNRATE and Sahm-style signals rose sharply."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "Unemployment spiked rapidly."},
        ],
        "data_provenance": {"source": "FRED", "series_id": "UNRATE", "accessed_at": NOW_ISO},
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    signal_scope = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "owner": "evan",
        "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {
            "canonical_column": "unrate",
            "display_name": "U.S. Unemployment Rate",
            "derivatives": [
                {"name": col, "definition": desc, "formula": formula, "role": role, "appears_in_charts": charts}
                for col, desc, formula, role, charts in [
                    ("unrate", "Civilian unemployment rate", "FRED UNRATE", "raw", ["hero", "regime_stats"]),
                    ("unrate_mom", "Monthly change in unemployment", "x_t - x_{t-1}", "derivative", []),
                    ("unrate_3m_chg", "Three-month change in unemployment", "x_t - x_{t-3}", "derivative", ["local_projections"]),
                    ("unrate_6m_chg", "Six-month change in unemployment", "x_t - x_{t-6}", "derivative", []),
                    ("unrate_12m_chg", "Twelve-month change in unemployment", "x_t - x_{t-12}", "derivative", []),
                    ("unrate_zscore_60m", "Unemployment versus its five-year history", "(x - mean60)/std60", "threshold_input", []),
                    ("unrate_sahm", "Sahm-style recession signal", "3m average minus trailing 12m low", "regime_state", ["hero"]),
                ]
            ],
        },
        "target_axis": {
            "canonical_column": "spy",
            "display_name": "SPY adjusted close",
            "derivatives": [
                {"name": "spy", "definition": "SPY adjusted month-end close", "formula": "month-end adjusted close", "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "SPY monthly return", "formula": "spy_t / spy_{t-1} - 1", "role": "derivative", "appears_in_charts": []},
                {"name": "spy_fwd_1m", "definition": "One-month forward SPY return", "formula": "spy_{t+1} / spy_t - 1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_3m", "definition": "Three-month forward SPY return", "formula": "spy_{t+3} / spy_t - 1", "role": "derivative", "appears_in_charts": ["local_projections", "quantile_coef"]},
                {"name": "spy_fwd_6m", "definition": "Six-month forward SPY return", "formula": "spy_{t+6} / spy_t - 1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_12m", "definition": "Twelve-month forward SPY return", "formula": "spy_{t+12} / spy_t - 1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
            ],
        },
        "notes": "Scope limited to UNRATE-derived labor-market signals and SPY returns.",
    }
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"], "benchmark_oos_sharpe": winner["bh_sharpe"], "oos_max_drawdown": winner["oos_max_drawdown"], "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    evidence_status = {
        "pair_id": PAIR_ID,
        "schema_version": "1.2.0",
        "status": "found_in_search",
        "updated_at": NOW_ISO,
        "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": f"Winner selected on in-sample data by the lead-plateau rule (D9) from the {DATE_TAG} tournament on real-time UNRATE vintages and evaluated on the held-out OOS window; UNRATE is lagging and Granger evidence is weak.",
        "next_step": "Freeze the selected rule and run a confirmation test on future data or a reserved holdout window.",
        "owner": "evan",
    }
    (RES / "evidence_status.json").write_text(json.dumps(evidence_status, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    analyst_suggestions = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "last_updated_at": NOW_ISO,
        "suggestions": [
            {
                "signal_name": "UNRATE release-lag robustness",
                "proposed_by": "evan",
                "source": "FRED",
                "observation": f"The rule selected on in-sample data uses a {winner['lead_value']}-month lead on the {winner['signal_display_name'].lower()} ({winner['direction']}, {winner['threshold_code']}); held-out OOS max drawdown {winner['oos_max_drawdown']:.1%} vs buy-and-hold {winner['bh_max_drawdown']:.1%}.",
                "rationale": "UNRATE is lagging and published after month end, so deployment should test whether release timing and revision assumptions change the result.",
                "possible_use_case": "robustness check",
                "caveats": "Search-selected rule; Granger evidence is weak and the live tradability assumptions are not final-exam validated.",
                "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
            }
        ],
        "notes": "Generated with the UNRATE x SPY pair pipeline.",
    }
    (RES / "analyst_suggestions.json").write_text(json.dumps(analyst_suggestions, indent=2) + "\n")


NARRATIVE_SOURCES = ["regime_quartile_returns.csv", "granger_by_lag.csv",
                     f"core_models_{DATE_TAG}/quantile_regression.csv",
                     f"core_models_{DATE_TAG}/quantile_equality_test.json"]


def write_narrative_provenance() -> None:
    """evidence_facts_<tag>.json: the evidence tables the page prose cites (scripts/gate_number_provenance.py)."""
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    derived = {"regime_quartile_ann_return_pct": {r.quartile: round(float(r.mean_return) * 12 * 100, 6)
                                                  for r in q.itertuples()}}   # the regime chart's return labels
    write_evidence_facts(PAIR_ID, DATE_TAG, sources=NARRATIVE_SOURCES, derived=derived)


def main() -> None:
    t0 = time.time()
    for path in (RES, CORE, VALID):
        path.mkdir(parents=True, exist_ok=True)
    df = build_panel()
    df[list(SIGNALS.values()) + ["unrate_recession_flag"]].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    tourn, winner, _ = run_tournament()
    write_evidence(df, tourn, winner)
    write_metadata(df, winner, time.time() - t0)
    write_narrative_provenance()
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
