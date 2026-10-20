#!/usr/bin/env python3
"""Pair pipeline: University of Michigan Expected Business Conditions x SPY (Phase B harness, single track).

The series is the Michigan survey's EXPECTED BUSINESS CONDITIONS question from Data Master.xlsx (sheet
UoM_ExptdChgBinesCyle, column 1: the SHARE of respondents expecting better business conditions, in percent; not the
balance / relative score and not a diffusion index), not the headline Consumer Sentiment index (FRED UMCSENT). It has no public archive of past
values (registry value_vintage revised_no_archive), so the tournament runs on scripts/harness (spec:
scripts/pair_spec_umcsent_spy.py) on ONE track, "As revised today": today's values (pinned Data Master snapshot
2026-10-16), aligned point-in-time with the Michigan survey release calendar (FRED UMCSENT release dates are used
ONLY as the timing source; the component is published in the same survey release). The winner is selected on
in-sample data by the D9 lead-plateau rule over the registry grid L1..L13 (position_shift 0: the lead is the whole
lag between the reading month and the return month); null tournament K=100, paired block bootstrap vs buy-and-hold
SPY, leak tests. The rule published on the main site (20260912, commit d1b68ecd: chg_12m / T_roll_p50 /
procyclical / L9, selected on OUT-OF-SAMPLE Sharpe) is replayed exactly by the harness and kept as the previous rule.

This file keeps the pair's evidence stages (computed on the same panel, descriptive only), metadata and the
narrative-provenance record. Overlapping-horizon inference uses HAC errors with at least h-1 lags; the Granger
summary reports the best lag with a Holm adjustment over the lags tested.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import pair_spec_umcsent_spy as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series  # noqa: E402
from harness.evidence import write_evidence_facts  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "umcsent_spy"
DATE_TAG = "20261020"  # Phase B B1s: harness, single track (revised, no archive), D9 plateau, grid L1..L13, null K=100, bootstrap
TARGET_SYMBOL = "SPY"
COST_BPS = 5
EVIDENCE_SIGNAL = "umcsent_level"   # the survey level: bounded and stationary, used as is by the descriptive tests
DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
NOW_ISO = datetime.now(timezone.utc).isoformat()
SIGNALS = spec_mod.SIGNALS
HORIZONS = (1, 3, 6, 12)              # forward SPY return horizons (months) of the descriptive tests
GRANGER_MAX_LAG = 12                  # Granger lags 1..12; the best lag's p-value is Holm-adjusted over the 12
QR_HORIZON = 3                        # quantile regression on 3-month forward SPY returns
QR_BLOCK, QR_DRAWS, QR_SEED = 6, 499, 42   # moving-block bootstrap of the QR slopes (block > QR_HORIZON - 1)
POSITION_CHANGE_THRESHOLD_PP = 5      # a test-period month counts as a position change above this size
ROLL_CORR_WINDOW, ROLL_CORR_MIN = 60, 36
STRESS_PERIODS = [
    ("Dot-Com Crash", "2000-03-31", "2002-10-31"),
    ("GFC", "2007-12-31", "2009-06-30"),
    ("COVID", "2020-02-29", "2020-04-30"),
    ("2022 Rates Shock", "2022-01-31", "2022-12-31"),
]


def hac_lags(n: int, h: int) -> int:
    """Newey-West lag length for an h-period overlapping regression: max(int(0.75 n^(1/3)), h - 1)."""
    return max(int(0.75 * n ** (1 / 3)), h - 1)


def ann_metrics(rets: pd.Series) -> dict[str, float]:
    """Monthly performance block used by the evidence tables (sub-period, quartile)."""
    rets = rets.dropna()
    if len(rets) < 2 or rets.std() == 0:
        return {"sharpe": 0.0, "ann_return": 0.0, "max_drawdown": 0.0, "n": int(len(rets))}
    equity = (1 + rets).cumprod()
    return {"sharpe": float(rets.mean() / rets.std() * np.sqrt(12)),
            "ann_return": float((1 + rets).prod() ** (12 / len(rets)) - 1),
            "max_drawdown": float((equity / equity.cummax() - 1).min()), "n": int(len(rets))}


def build_panel() -> pd.DataFrame:
    """Today's Michigan Expected Business Conditions (pinned Data Master snapshot) and SPY month-end closes on the
    rebalance grid."""
    idx = spec_mod.rebalance_index()
    lv = spec_mod.revised_levels()
    df = lv.reindex(idx)
    df.index.name = "date"
    df["spy"] = spec_mod.target_prices().reindex(idx)
    df["spy_ret"] = df["spy"].pct_change()
    for h in HORIZONS:
        df[f"spy_fwd_{h}m"] = df["spy"].shift(-h) / df["spy"] - 1
    full = spec_mod.features(lv)
    for col in SIGNALS.values():
        df[col] = full[col].reindex(idx)
    df.to_parquet(DATA_DIR / f"{PAIR_ID}_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_{PAIR_ID}_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_{PAIR_ID}_{DATE_TAG}.md")
    pd.DataFrame([
        {"Column Name": "umcsent", "Display Name": "U. Michigan Expected Business Conditions (% expecting better)",
         "Description": "University of Michigan Surveys of Consumers, expected change in business conditions a year "
                        "ahead: share of respondents expecting better conditions (Data Master column 1; not the "
                        "balance/relative score, not a diffusion index, not the headline Consumer Sentiment index)",
         "Source": "Data Master.xlsx (sheet UoM_ExptdChgBinesCyle), pinned snapshot 2026-10-16",
         "Series ID": "UMICH_EXP_BUS_COND (Data Master; not on FRED/ALFRED). Release timing: FRED UMCSENT "
                      "release dates (same survey release)",
         "Unit": "% of respondents expecting better business conditions", "Transformation": "Monthly level (bounded, stationary)",
         "Seasonal Adj.": "Not seasonally adjusted",
         "Direction Convention": "Higher = more respondents expect better business conditions",
         "Effective Start": str(lv["umcsent"].first_valid_index().date()),
         "Known Quirks": "No public archive of past values: only today's values exist, so earlier months may "
                         "differ from first publication (unquantified). Published in the Michigan survey release "
                         "(preliminary mid-month, final at or before the end of the survey month). Data Master "
                         "series ends 2025-09",
         "Display Note": "Rising expected business conditions are read as a sign of stronger spending ahead.",
         "Refresh Freq.": "Monthly",
         "Refresh Source": "data/release_calendar/snapshots/20261016T232733Z/UMICH_EXP_BUS_COND.csv"},
        {"Column Name": "spy", "Display Name": "SPY adjusted close", "Description": "SPDR S&P 500 ETF adjusted close",
         "Source": "Yahoo Finance (pinned)", "Series ID": "SPY", "Unit": "USD",
         "Transformation": "Month-end adjusted close", "Seasonal Adj.": "N/A",
         "Direction Convention": "Higher = higher equity price",
         "Effective Start": str(df["spy"].first_valid_index().date()), "Known Quirks": "ETF history begins in 1993",
         "Display Note": "Used as the equity-market target and benchmark.", "Refresh Freq.": "Daily",
         "Refresh Source": "data/phaseB_inputs/spy_month_end_20261017.csv"},
    ]).to_csv(DATA_DIR / f"data_dictionary_{PAIR_ID}_{DATE_TAG}.csv", index=False)
    print(f"  Panel rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def run_tournament(K: int = 100) -> tuple[pd.DataFrame, dict, dict]:
    out = run_pair(PAIR_ID, DATE_TAG, K=K, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "lookback": "LB60 where rolling thresholds apply",
        "strategy_description": "Hold SPY when the lagged Michigan Expected Business Conditions signal is on the "
                                "favourable side "
                                "of its threshold; otherwise hold cash (P1 long/cash).",
        "notes": "The University of Michigan Expected Business Conditions series (Data Master; not the headline "
                 "Consumer Sentiment index) is the share of respondents expecting better business conditions, a "
                 "bounded percentage. One track: no public archive of past values "
                 "exists, so the results use today's values (revisions may add hindsight) with release-calendar "
                 "timing (UMCSENT release dates); still a search-selected rule. The rule published on the main site "
                 "(20260912, commit d1b68ecd, selected on out-of-sample Sharpe) is replayed exactly and kept as the "
                 "previous rule."})
    winner = json.loads((RES / "winner_summary.json").read_text())
    tourn = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["main"]
    ws = winner_series(res, res.selection["winner"])
    reason = f"{winner['signal_code']} {winner['direction']} rule crossed {winner['threshold_code']}"
    log = trade_log(ws, TARGET_SYMBOL, COST_BPS, reason)
    log.to_csv(RES / "winner_trade_log.csv", index=False)
    log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, winner, out


def hac_corr_p(x: pd.Series, y: pd.Series, h: int) -> float:
    """p-value of a correlation robust to overlapping h-month returns: slope of standardized y on standardized x
    with HAC (Newey-West) errors, maxlags = hac_lags(n, h)."""
    zx, zy = (x - x.mean()) / x.std(), (y - y.mean()) / y.std()
    fit = sm.OLS(zy.to_numpy(), sm.add_constant(zx.to_numpy())).fit(
        cov_type="HAC", cov_kwds={"maxlags": hac_lags(len(x), h)})
    return float(fit.pvalues[1])


def quantile_regression_block(x: pd.Series, y: pd.Series, taus=(0.10, 0.25, 0.50, 0.75, 0.90)):
    """Quantile regression of y on x per tau with moving-block bootstrap inference (overlapping forward returns):
    per-tau standard error, two-sided p-value of slope = 0, and a Wald test of equal slopes across taus built
    from the bootstrap covariance of the slope differences from the median tau."""
    d = pd.DataFrame({"x": x.to_numpy(float), "y": y.to_numpy(float)}).dropna().reset_index(drop=True)
    n = len(d)
    taus = list(taus)
    beta = {t: float(smf.quantreg("y ~ x", d).fit(q=t).params["x"]) for t in taus}
    rng = np.random.default_rng(QR_SEED)
    nb = int(np.ceil(n / QR_BLOCK))
    boot = []
    for _ in range(QR_DRAWS):
        starts = rng.integers(0, n - QR_BLOCK + 1, size=nb)
        idx = np.concatenate([np.arange(s0, s0 + QR_BLOCK) for s0 in starts])[:n]
        m = smf.quantreg("y ~ x", d.iloc[idx])
        try:
            boot.append([float(m.fit(q=t).params["x"]) for t in taus])
        except Exception:  # noqa: BLE001 - a degenerate resample is skipped and counted
            continue
    b = np.asarray(boot)
    rows = []
    for j, t in enumerate(taus):
        col = b[:, j]
        p = min(1.0, 2 * min((col <= 0).mean(), (col >= 0).mean()))
        rows.append({"quantile": t, "coef": beta[t], "se": float(col.std(ddof=1)), "p_value": float(p),
                     "ci_low": float(np.quantile(col, 0.025)), "ci_high": float(np.quantile(col, 0.975)), "n": n,
                     "boot_draws": int(len(col))})
    ref = taus.index(0.50)
    others = [j for j in range(len(taus)) if j != ref]
    d_obs = np.array([beta[taus[j]] - beta[taus[ref]] for j in others])
    diffs = b[:, others] - b[:, [ref]]
    stat = float(d_obs @ np.linalg.pinv(np.atleast_2d(np.cov(diffs, rowvar=False))) @ d_obs)
    p = float(stats.chi2.sf(stat, len(others)))
    test = {"method": f"moving-block bootstrap Wald (block {QR_BLOCK}, {len(b)} draws)", "stat": stat,
            "df": len(others), "p_value": p, "reject_equality": bool(p < 0.05), "n": n}
    return rows, test


def write_evidence(df: pd.DataFrame, tourn: pd.DataFrame, winner: dict) -> None:
    x_col = EVIDENCE_SIGNAL
    corr_rows = []
    for col in SIGNALS.values():
        for h in HORIZONS:
            fwd = f"spy_fwd_{h}m"
            sub = df[[col, fwd]].dropna()
            if len(sub) < 20 or sub[col].std() == 0:
                continue
            r, p_iid = stats.pearsonr(sub[col], sub[fwd])
            corr_rows.append({"pair_name": f"{col}_to_{fwd}", "metric": "pearson", "value": r,
                              "p_value": hac_corr_p(sub[col], sub[fwd], h), "p_value_iid": p_iid,
                              "hac_lags": hac_lags(len(sub), h), "n": len(sub)})
    pd.DataFrame(corr_rows).to_csv(CORE / "correlations.csv", index=False)

    gdata = df[["spy_ret", x_col]].dropna()
    tests = grangercausalitytests(gdata[["spy_ret", x_col]], maxlag=GRANGER_MAX_LAG, verbose=False)
    gr = pd.DataFrame([{"lag": lag, "f_stat": res[0]["ssr_ftest"][0], "p_value": res[0]["ssr_ftest"][1],
                        "direction": "UMICH_EBC_to_SPY", "n": len(gdata)} for lag, res in tests.items()])
    gr["p_value_holm"] = multipletests(gr["p_value"], method="holm")[1]
    gr.to_csv(CORE / "granger_causality.csv", index=False)
    gr.to_csv(RES / "granger_by_lag.csv", index=False)

    ccf_rows = []
    x = df[x_col].diff()      # pre-whitening by first differences (the survey level is persistent month to month)
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
        q_rows.append({"quartile": label, "mean_return": rets.mean(), "sharpe": ann_metrics(rets)["sharpe"],
                       "n": len(rets), "signal_low": float(sub.loc[q == label, x_col].min()),
                       "signal_high": float(sub.loc[q == label, x_col].max())})
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)

    rcorr = []
    for dt in df.index:
        window = df.loc[:dt, [x_col, "spy_ret"]].tail(ROLL_CORR_WINDOW).dropna()
        if len(window) >= ROLL_CORR_MIN:
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
    for h in HORIZONS:
        s = df[[x_col, f"spy_fwd_{h}m"]].dropna()
        lags = hac_lags(len(s), h)
        fit = sm.OLS(s[f"spy_fwd_{h}m"].to_numpy(), sm.add_constant(s[x_col].to_numpy())).fit(
            cov_type="HAC", cov_kwds={"maxlags": lags})
        lp_rows.append({"horizon": h, "coef": float(fit.params[1]), "se": float(fit.bse[1]),
                        "p_value": float(fit.pvalues[1]), "r_squared": float(fit.rsquared), "n": len(s),
                        "hac_lags": lags})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)

    qs = df[[x_col, f"spy_fwd_{QR_HORIZON}m"]].dropna()
    qr_rows, qr_test = quantile_regression_block(qs[x_col], qs[f"spy_fwd_{QR_HORIZON}m"])
    pd.DataFrame(qr_rows).to_csv(CORE / "quantile_regression.csv", index=False)
    (CORE / "quantile_equality_test.json").write_text(json.dumps(qr_test, indent=2) + "\n")

    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    sp_rows = []
    for name, start, end in STRESS_PERIODS:
        seg = strat.loc[start:end]
        cnt = seg["sample"].value_counts()
        n_pre, n_is, n_oos = int(cnt.get("pre_IS", 0)), int(cnt.get("IS", 0)), int(cnt.get("OOS", 0))
        phase = ("test" if n_oos == len(seg) else "training" if n_is == len(seg) else
                 "before training" if n_pre == len(seg) else
                 "mostly before training" if n_pre > max(n_is, n_oos) else "mixed")
        sret, bret = seg["strategy_return"], seg["benchmark_return"]
        sp_rows.append({"period": name, "start_date": start, "end_date": end, "phase": phase,
                        "n_pre_is": n_pre, "n_is": n_is, "n_oos": n_oos, "n_obs": int(len(seg)),
                        "strategy_sharpe": ann_metrics(sret)["sharpe"], "buy_hold_sharpe": ann_metrics(bret)["sharpe"],
                        "strategy_return": float((1 + sret).prod() - 1), "buy_hold_return": float((1 + bret).prod() - 1)})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)

    station_rows = []
    for col in ["umcsent_level", "umcsent_diff_1m", "umcsent_chg_12m", "umcsent_zscore_60m", "spy_ret"]:
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
                   "strategy": winner["strategy_family"], "track": "as revised today (single track)",
                   "oos_sharpe": winner["oos_sharpe"], "oos_percentile_in_grid": pct_in_grid,
                   "sharpe_diff_vs_bh": bs["observed"], "ci_95_low": bs["ci_95"][0], "ci_95_high": bs["ci_95"][1],
                   "p_diff_le_0": bs["p_diff_le_0"], "method": bs["method"], "block_length": bs["block_length"],
                   "draws": bs["draws"], "seed": bs["seed"]}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "tx_cost_bps": COST_BPS,
                   "gross_sharpe": winner["oos_sharpe"]}]).to_csv(VALID / "transaction_costs.csv", index=False)


def write_metadata(df: pd.DataFrame, winner: dict, elapsed: float) -> None:
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "leading", "indicator_type": "sentiment",
        "strategy_objective": "procyclical_capture",
        "owner_writes": {
            "dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"],
        },
        "last_updated_by": "ray", "last_updated_at": NOW_ISO, "indicator": "umcsent", "target": "spy",
        "expected_direction": "procyclical", "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "procyclical",
        "mechanism": "The University of Michigan Surveys of Consumers ask households whether they expect business "
                     "conditions to improve or worsen. Rising expectations are read as a sign of stronger spending "
                     "and risk-on equity conditions; falling expectations as the opposite. The procyclical prior "
                     "holds SPY when expectations are high or rising.",
        "confidence": "low",
        "key_finding": f"On today's Michigan Expected Business Conditions values (no archive of past values exists), the rule selected on in-sample "
                       f"data uses {winner['signal_code']} at L{winner['lead_value']} (IS Sharpe "
                       f"{winner['is_sharpe']:.2f}) with test-period Sharpe {winner['oos_sharpe']:.2f} versus "
                       f"buy-and-hold {winner['bh_sharpe']:.2f}.",
        "caveats": [
            "No public archive of past values of this series exists, so the backtest uses today's values; any "
            "revision would add hindsight that cannot be measured.",
            "The strategy is search-selected and needs fresh holdout validation.",
            "The Data Master series ends 2025-09, so the test period ends there.",
            "The rule published on the main site (20260912) was the highest out-of-sample Sharpe with fixed "
            "lags (the test period was used to choose it); it is replaced here.",
        ],
        "narrative_summary": "The share of University of Michigan respondents expecting better business conditions is "
                             "tested as a "
                             "procyclical sentiment overlay for SPY: hold equity when expectations are favourable.",
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "NBER recession."},
            {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30", "note": "NBER recession."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "NBER recession."},
            {"label": "2022 drawdown", "start": "2022-01-01", "end": "2022-12-31", "note": "Rate-hike bear market."},
        ],
        "data_provenance": {"source": "Data Master.xlsx (sheet UoM_ExptdChgBinesCyle), pinned snapshot "
                                      "20261016T232733Z; release timing from FRED UMCSENT release dates",
                            "series_id": "UMICH_EXP_BUS_COND", "accessed_at": NOW_ISO},
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    defs = [
        ("umcsent", "Michigan Expected Business Conditions: % of respondents expecting better business conditions",
         "Data Master (UoM_ExptdChgBinesCyle, column 1)", "raw", ["hero"]),
        ("umcsent_level", "Level of the share expecting better conditions (bounded percentage, used as is)", "identity", "threshold_input",
         ["hero", "regime_stats", "local_projections", "quantile_coef", "rolling_correlation", "granger_f_by_lag",
          "ccf_prewhitened"]),
        ("umcsent_diff_1m", "Month-on-month change", "x_t - x_{t-1}", "derivative", []),
        ("umcsent_chg_12m", "12-month change", "x_t - x_{t-12}", "derivative", []),
        ("umcsent_zscore_60m", "Level versus its five-year history", "(x - mean60)/std60", "derivative", []),
    ]
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {"canonical_column": "umcsent", "display_name": "U. Michigan Expected Business Conditions",
                           "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch}
                                           for c, d, f, r, ch in defs]},
        "target_axis": {
            "canonical_column": "spy", "display_name": "SPY adjusted close",
            "derivatives": [
                {"name": "spy", "definition": "SPY adjusted month-end close", "formula": "month-end adjusted close",
                 "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "SPY monthly return", "formula": "spy_t / spy_{t-1} - 1",
                 "role": "derivative", "appears_in_charts": ["regime_stats", "ccf_prewhitened"]},
                {"name": "spy_fwd_1m", "definition": "One-month forward SPY return", "formula": "spy_{t+1} / spy_t - 1",
                 "role": "derivative", "appears_in_charts": ["correlation_heatmap", "local_projections"]},
                {"name": "spy_fwd_3m", "definition": "Three-month forward SPY return",
                 "formula": "spy_{t+3} / spy_t - 1", "role": "derivative",
                 "appears_in_charts": ["correlation_heatmap", "local_projections", "quantile_coef"]},
                {"name": "spy_fwd_6m", "definition": "Six-month forward SPY return", "formula": "spy_{t+6} / spy_t - 1",
                 "role": "derivative", "appears_in_charts": ["correlation_heatmap", "local_projections"]},
                {"name": "spy_fwd_12m", "definition": "Twelve-month forward SPY return",
                 "formula": "spy_{t+12} / spy_t - 1", "role": "derivative",
                 "appears_in_charts": ["correlation_heatmap", "local_projections"]},
            ],
        },
        "notes": "Scope limited to Michigan Expected Business Conditions signals and SPY returns.",
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
                          "tournament on today's values of this series (no archive of past values exists); its test-period "
                          "window has been seen by earlier tournaments of this pair, so it is not a frozen-rule "
                          "hold-out result.",
        "next_step": "Freeze the selected rule and run a confirmation test on future data or a reserved holdout window.",
        "owner": "evan",
    }
    (RES / "evidence_status.json").write_text(json.dumps(evidence_status, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    analyst_suggestions = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{
            "signal_name": "Start a vintage record of this series", "proposed_by": "evan", "source": "Data Master",
            "observation": f"The rule selected on in-sample data uses a {winner['lead_value']}-month lead on the "
                           f"{winner['signal_display_name']} ({winner['direction']}, {winner['threshold_code']}); "
                           f"test-period max drawdown {winner['oos_max_drawdown']:.1%} vs buy-and-hold "
                           f"{winner['bh_max_drawdown']:.1%}.",
            "rationale": "Only today's values exist; the monthly Data Master snapshots started 2026-10-16 build "
                         "a record of values as published, which a later rerun can use for a forward test.",
            "possible_use_case": "robustness check",
            "caveats": "Search-selected rule; the live tradability assumptions are not final-exam validated.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
        }],
        "notes": "Generated with the Michigan Expected Business Conditions x SPY pair pipeline.",
    }
    (RES / "analyst_suggestions.json").write_text(json.dumps(analyst_suggestions, indent=2) + "\n")


NARRATIVE_SOURCES = ["regime_quartile_returns.csv", "granger_by_lag.csv", "subperiod_sharpe.csv",
                     f"core_models_{DATE_TAG}/quantile_regression.csv",
                     f"core_models_{DATE_TAG}/quantile_equality_test.json",
                     f"core_models_{DATE_TAG}/local_projections.csv"]


def write_narrative_provenance() -> None:
    """evidence_facts_<tag>.json: the evidence tables the page prose cites (scripts/gate_number_provenance.py)."""
    n_rows = len(pd.read_csv(RES / "winner_trades_broker_style.csv"))
    sr = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv")
    oos = sr.loc[sr["sample"] == "OOS", "position"].to_numpy(float)
    d = np.abs(np.diff(oos[~np.isnan(oos)]))
    gr = pd.read_csv(RES / "granger_by_lag.csv")
    best = gr.loc[gr["p_value"].idxmin()]
    write_evidence_facts(PAIR_ID, DATE_TAG, sources=NARRATIVE_SOURCES, derived={
        "n_trade_log_rows": n_rows,
        "position_change_threshold_pp": POSITION_CHANGE_THRESHOLD_PP,
        "oos_months_position_change_gt_5pct": int((d > POSITION_CHANGE_THRESHOLD_PP / 100).sum()),
        "oos_sum_abs_position_change": round(float(d.sum()), 4),
        "n_granger_lags": GRANGER_MAX_LAG,
        "granger_best": {"lag": int(best["lag"])},
        "granger_min_p_single": round(float(best["p_value"]), 4),
        "granger_min_p_holm": round(float(best["p_value_holm"]), 4),
        "n_months_qr_horizon": QR_HORIZON, "n_months_qr_block": QR_BLOCK,
        "n_months_roll_corr_window": ROLL_CORR_WINDOW})


def main(K: int = 100) -> None:
    t0 = time.time()
    for path in (RES, CORE, VALID):
        path.mkdir(parents=True, exist_ok=True)
    df = build_panel()
    df[list(SIGNALS.values())].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    tourn, winner, _ = run_tournament(K)
    write_evidence(df, tourn, winner)
    write_metadata(df, winner, time.time() - t0)
    write_narrative_provenance()
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
