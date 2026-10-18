#!/usr/bin/env python3
"""Pair pipeline: Retail Inventories-to-Sales Ratio (RETAILIRSA) x SPY (Phase B harness).

The tournament runs on scripts/harness (spec: scripts/pair_spec_retail_inv_sales_spy.py) on two tracks:
  * MAIN, "As known at the time": real-time RETAILIRSA vintages (ALFRED); each rebalance uses the vintage visible
    when its return window opens. The ALFRED archive of this series starts 2013-06-13, so the training window before
    the test period (2017-06-30) is shorter than the method's minimum: MAIN has no eligible candidate and no winner
    (track_state rt_insufficient). The page says so and is shown unranked.
  * COMPARISON, "As revised today (hindsight)": today's revised values with point-in-time release timing. It
    selects its own winner by the D9 lead-plateau rule over the registry grid L3..L14 (position_shift 0: the lead is
    the whole lag between the reading month and the return month); null tournament K=100, paired block bootstrap vs
    buy-and-hold SPY, leak tests. Shown as hindsight, never as the headline.
The 20261016 rule (raw IS argmax, commit 1d06839f) is replayed exactly by the harness and kept as the previous rule.

This file keeps the pair's evidence stages (computed on the revised panel, descriptive only), metadata and the
narrative-provenance record. The strategy-dependent evidence (stress windows, trade log) uses the hindsight rule,
since MAIN has none; files and labels say so. Overlapping-horizon inference uses HAC errors with at least h-1 lags;
the Granger summary reports the best lag with a Holm adjustment over the lags tested.
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
import pair_spec_retail_inv_sales_spy as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series  # noqa: E402
from harness.evidence import write_evidence_facts  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "retail_inv_sales_spy"
DATE_TAG = "20261018"  # Phase B B1: harness, two tracks, D9 plateau, registry grid L3..L14, null K=100, bootstrap
TARGET_SYMBOL = "SPY"
COST_BPS = 5
EVIDENCE_SIGNAL = "invsales_chg_12m"  # 12-month change: the transform the legacy evidence tests used
DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
NOW_ISO = datetime.now(timezone.utc).isoformat()
SIGNALS = spec_mod.SIGNALS
HORIZONS = (1, 3, 6, 12)              # forward SPY return horizons (months) of the descriptive tests
GRANGER_MAX_LAG = 6                   # Granger lags 1..6 (legacy); the best lag's p-value is Holm-adjusted over them
QR_HORIZON = 3                        # quantile regression on 3-month forward SPY returns
QR_BLOCK, QR_DRAWS, QR_SEED = 6, 499, 42   # moving-block bootstrap of the QR slopes (block > QR_HORIZON - 1)
POSITION_CHANGE_THRESHOLD_PP = 5      # a test-period month counts as a position change above this size
ROLL_CORR_WINDOW, ROLL_CORR_MIN = 24, 12   # rolling correlation window (legacy constants), months
STRESS_PERIODS = [
    ("Dot-Com Crash", "2000-03-31", "2002-10-31"),
    ("GFC", "2007-12-31", "2009-06-30"),
    ("COVID", "2020-02-29", "2020-06-30"),
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
    """Revised RETAILIRSA (latest pinned ALFRED vintage) and SPY month-end closes on the full monthly grid."""
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
        {"Column Name": "invsales", "Display Name": "Retail Inventories-to-Sales Ratio",
         "Description": "Retailers: inventories-to-sales ratio (Census Monthly Retail Trade / MTIS)",
         "Source": "FRED / ALFRED (pinned vintages)", "Series ID": "RETAILIRSA", "Unit": "Ratio",
         "Transformation": "Monthly level", "Seasonal Adj.": "Seasonally adjusted",
         "Direction Convention": "Higher = inventories large relative to sales (softer demand)",
         "Effective Start": str(df["invsales"].first_valid_index().date()),
         "Known Quirks": "Published about six to seven weeks after month end and revised in later releases and "
                         "annual benchmarks; the ALFRED archive of earlier vintages starts 2013-06-13",
         "Display Note": "A high ratio means stock on shelves is large relative to what is selling.",
         "Refresh Freq.": "Monthly", "Refresh Source": "data/release_calendar/vintages/RETAILIRSA.csv.gz"},
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
    """Harness run. Returns the hindsight tournament table, the hindsight track record (MAIN has no winner) and
    the run output."""
    out = run_pair(PAIR_ID, DATE_TAG, K=K, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "lookback": "LB60 where rolling thresholds apply",
        "strategy_description": "Hold SPY when the lagged inventories-to-sales signal is on the favourable side of "
                                "its threshold; otherwise hold cash (P1 long/cash).",
        "notes": "Retail inventories relative to sales, a demand-softness gauge. As known at the time (real-time "
                 "RETAILIRSA vintages) the archive is too short for the training window, so there is no headline "
                 "winner; the as-revised-today result is shown for comparison only. The 20261016 rule (raw IS "
                 "argmax) is replayed exactly and kept as the previous rule."})
    ws = json.loads((RES / "winner_summary.json").read_text())
    hind = ws["tracks"]["comparison"]
    tourn = pd.read_csv(RES / f"hindsight_tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["comparison"]
    wsr = winner_series(res, res.selection["winner"])
    w = hind["winner"]
    reason = f"{w['signal']} {w['direction']} rule crossed {w['threshold']} (as revised today, hindsight)"
    log = trade_log(wsr, TARGET_SYMBOL, COST_BPS, reason)
    log.to_csv(RES / "winner_trade_log.csv", index=False)
    log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, hind, out


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


def write_evidence(df: pd.DataFrame, tourn: pd.DataFrame, hind: dict) -> None:
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
                        "direction": "INVSALES_to_SPY", "n": len(gdata)} for lag, res in tests.items()])
    gr["p_value_holm"] = multipletests(gr["p_value"], method="holm")[1]
    gr.to_csv(CORE / "granger_causality.csv", index=False)
    gr.to_csv(RES / "granger_by_lag.csv", index=False)

    # quartiles on the common descriptive sample; qcut is right-closed, so readings tied exactly at an internal
    # boundary stay together in the lower bucket (the ratio is published to two decimals: unequal bucket sizes)
    sub = df[[x_col, "spy_ret"]].dropna()
    q, q_bins = pd.qcut(sub[x_col], 4, labels=["Q1", "Q2", "Q3", "Q4"], retbins=True)
    q_rows = []
    for label in ["Q1", "Q2", "Q3", "Q4"]:
        rets = sub.loc[q == label, "spy_ret"]
        q_rows.append({"quartile": label, "mean_return": rets.mean(), "sharpe": ann_metrics(rets)["sharpe"],
                       "n": len(rets), "signal_low": float(sub.loc[q == label, x_col].min()),
                       "signal_high": float(sub.loc[q == label, x_col].max())})
    if q.isna().any() or sum(r["n"] for r in q_rows) != len(sub):
        raise RuntimeError("regime quartile assignment incomplete")
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)
    (RES / "regime_quartile_metadata.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "signal": x_col, "construction": "pandas.qcut(signal, 4), right-closed intervals",
        "sample_start": sub.index.min().date().isoformat(), "sample_end": sub.index.max().date().isoformat(),
        "eligible_observations": int(len(sub)), "boundaries": [float(v) for v in q_bins],
        "boundary_tie_counts": {str(float(v)): int(sub[x_col].eq(v).sum()) for v in q_bins[1:-1]},
        "bucket_counts": {r["quartile"]: int(r["n"]) for r in q_rows}, "unassigned_observations": int(q.isna().sum()),
        "assignment_rule": "Q1 includes the sample minimum and first quartile boundary; Q2-Q4 are open on the left "
                           "and closed on the right. Boundary ties remain together in the lower bucket."},
        indent=2) + "\n")

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

    # stress windows of the hindsight rule (MAIN has no winner)
    strat = pd.read_csv(RES / f"hindsight_strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
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
                        "track": "as revised today (hindsight)",
                        "strategy_sharpe": ann_metrics(sret)["sharpe"], "buy_hold_sharpe": ann_metrics(bret)["sharpe"],
                        "strategy_return": float((1 + sret).prod() - 1), "buy_hold_return": float((1 + bret).prod() - 1)})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)

    station_rows = []
    for col in ["invsales", "invsales_diff_1m", "invsales_chg_12m", "invsales_zscore_60m", "spy_ret"]:
        s = df[col].dropna()
        adf = adfuller(s, autolag="AIC")
        station_rows.append({"variable": col, "test": "ADF", "statistic": adf[0], "p_value": adf[1], "lags": adf[2],
                             "conclusion": "stationary" if adf[1] < 0.05 else "unit_root_not_rejected"})
        kp = kpss(s, regression="c", nlags="auto")
        station_rows.append({"variable": col, "test": "KPSS", "statistic": kp[0], "p_value": kp[1], "lags": kp[2],
                             "conclusion": "stationary_not_rejected" if kp[1] > 0.05 else "nonstationary"})
    pd.DataFrame(station_rows).to_csv(RES / f"stationarity_tests_{DATE_TAG}.csv", index=False)

    w = hind["winner"]
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    pct_in_grid = float((valid["oos_sharpe"] >= w["oos_sharpe"]).mean())
    bs = hind["vs_buy_hold"]
    pd.DataFrame([{"signal": w["signal"], "threshold": w["threshold"], "strategy": w["strategy_family"],
                   "track": "as revised today (hindsight)", "oos_sharpe": w["oos_sharpe"],
                   "oos_percentile_in_grid": pct_in_grid, "sharpe_diff_vs_bh": bs["sharpe_diff"],
                   "ci_95_low": bs["ci_95"][0], "ci_95_high": bs["ci_95"][1], "p_diff_le_0": bs["p_diff_le_0"],
                   "method": bs.get("method"), "block_length": bs["block_length"], "draws": bs["draws"],
                   "seed": bs.get("seed")}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": w["signal"], "threshold": w["threshold"], "strategy": w["strategy_family"],
                   "track": "as revised today (hindsight)", "tx_cost_bps": COST_BPS,
                   "gross_sharpe": w["oos_sharpe"]}]).to_csv(VALID / "transaction_costs.csv", index=False)


def write_metadata(df: pd.DataFrame, ws: dict, elapsed: float) -> None:
    hind = ws["tracks"]["comparison"]
    w = hind["winner"]
    ir = ws["tracks"]["main"]["insufficient_reason"]
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "coincident", "indicator_type": "production",
        "strategy_objective": "max_sharpe",
        "owner_writes": {
            "dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"],
        },
        "last_updated_by": "ray", "last_updated_at": NOW_ISO, "indicator": "invsales", "target": "spy",
        "expected_direction": "countercyclical", "observed_direction": w["direction"],
        "direction_consistent": w["direction"] == "countercyclical",
        "mechanism": "The retail inventories-to-sales ratio rises when stock accumulates faster than sales, a sign of "
                     "softening demand that can precede order and production cuts; the prior is countercyclical "
                     "(reduce SPY when the ratio is high).",
        "confidence": "low",
        "key_finding": (f"As known at the time (real-time RETAILIRSA vintages) there is no winner: the archive starts "
                        f"{ir['rt_start']} and leaves {ir['n_is_rows']} training months, fewer than the "
                        f"{ir['min_required']} required. On today's revised data (hindsight) the rule selected on "
                        f"in-sample data uses {w['signal']} at L{w['lead']} ({w['direction']}) with test-period Sharpe "
                        f"{w['oos_sharpe']:.2f} versus buy-and-hold {hind['bh_oos']['sharpe']:.2f}."),
        "caveats": [
            "There is no result on data as known at the time: the vintage archive is too short for the training "
            "window. The as-revised-today result uses today's corrected values and is hindsight.",
            "The hindsight rule is procyclical, opposite to the countercyclical prior.",
            "The strategy is search-selected and needs fresh holdout validation.",
        ],
        "narrative_summary": "Retail inventories relative to sales are tested as a demand-softness signal for SPY "
                             "allocation; the real-time archive is too short to rank the pair.",
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "NBER recession."},
            {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30",
             "note": "Sales collapsed faster than inventories; the ratio spiked."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30",
             "note": "Ratio spiked as stores closed, then fell to record lows as sales rebounded."},
            {"label": "2022 drawdown", "start": "2022-01-01", "end": "2022-12-31", "note": "Rate-hike bear market."},
        ],
        "data_provenance": {"source": "FRED / ALFRED", "series_id": "RETAILIRSA", "accessed_at": NOW_ISO},
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    defs = [
        ("invsales", "Retail inventories-to-sales ratio", "FRED RETAILIRSA", "raw", ["hero"]),
        ("invsales_level", "Ratio level (threshold input)", "identity", "threshold_input", []),
        ("invsales_diff_1m", "Month-on-month change", "x_t - x_{t-1}", "derivative", []),
        ("invsales_chg_12m", "12-month change", "x_t - x_{t-12}", "derivative",
         ["regime_stats", "local_projections", "quantile_coef", "rolling_correlation", "granger_f_by_lag"]),
        ("invsales_zscore_60m", "Level versus its five-year history", "(x - mean60)/std60", "derivative", []),
    ]
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {"canonical_column": "invsales", "display_name": "Retail Inventories-to-Sales Ratio (RETAILIRSA)",
                           "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch}
                                           for c, d, f, r, ch in defs]},
        "target_axis": {
            "canonical_column": "spy", "display_name": "SPY adjusted close",
            "derivatives": [
                {"name": "spy", "definition": "SPY adjusted month-end close", "formula": "month-end adjusted close",
                 "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "SPY monthly return", "formula": "spy_t / spy_{t-1} - 1",
                 "role": "derivative", "appears_in_charts": ["regime_stats"]},
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
        "notes": "Scope limited to RETAILIRSA-derived signals and SPY returns.",
    }
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    # MAIN has no winner: the KPI file carries the buy-and-hold side only, never the hindsight rule as a headline
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "main_eligible": False,
                                               "winner_oos_sharpe": None,
                                               "benchmark_oos_sharpe": hind["bh_oos"]["sharpe"],
                                               "oos_max_drawdown": None,
                                               "bh_max_drawdown": hind["bh_oos"]["max_drawdown"]}, indent=2) + "\n")
    evidence_status = {
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search", "updated_at": NOW_ISO,
        "plain_english": "There is no winning rule on data as known at the time: the archive of past releases is "
                         "too short to train on. A rule found on today's revised data is shown as hindsight only.",
        "technical_note": f"Real-time RETAILIRSA vintages start {ir['rt_start']}, leaving {ir['n_is_rows']} training "
                          f"rows before the test period (minimum {ir['min_required']}); MAIN is not eligible. The "
                          f"as-revised-today winner comes from the {DATE_TAG} tournament (D9 lead plateau) and is "
                          "search-selected hindsight, not a frozen-rule hold-out result.",
        "next_step": "Re-run once enough real-time history exists, or freeze the hindsight rule and test it on data "
                     "released after this run.",
        "owner": "evan",
    }
    (RES / "evidence_status.json").write_text(json.dumps(evidence_status, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    analyst_suggestions = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{
            "signal_name": "Real-time history", "proposed_by": "evan", "source": "ALFRED",
            "observation": f"No result as known at the time: the RETAILIRSA vintage archive starts {ir['rt_start']} "
                           f"({ir['n_is_rows']} training months, {ir['min_required']} required).",
            "rationale": "Revisions to the ratio cannot be measured before the archive starts, so the hindsight rule "
                         "may rely on corrected values investors did not see.",
            "possible_use_case": "re-run when the archive is long enough, or source earlier vintages",
            "caveats": "The as-revised-today rule is hindsight and search-selected.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
        }],
        "notes": "Generated with the RETAILIRSA x SPY pair pipeline.",
    }
    (RES / "analyst_suggestions.json").write_text(json.dumps(analyst_suggestions, indent=2) + "\n")


NARRATIVE_SOURCES = ["regime_quartile_returns.csv", "granger_by_lag.csv", "subperiod_sharpe.csv",
                     f"core_models_{DATE_TAG}/quantile_regression.csv",
                     f"core_models_{DATE_TAG}/quantile_equality_test.json",
                     f"core_models_{DATE_TAG}/local_projections.csv"]


def write_narrative_provenance() -> None:
    """evidence_facts_<tag>.json: the evidence tables the page prose cites (scripts/gate_number_provenance.py)."""
    n_rows = len(pd.read_csv(RES / "winner_trades_broker_style.csv"))
    sr = pd.read_csv(RES / f"hindsight_strategy_returns_{DATE_TAG}.csv")
    oos = sr.loc[sr["sample"] == "OOS", "position"].to_numpy(float)
    d = np.abs(np.diff(oos[~np.isnan(oos)]))
    gr = pd.read_csv(RES / "granger_by_lag.csv")
    best = gr.loc[gr["p_value"].idxmin()]
    write_evidence_facts(PAIR_ID, DATE_TAG, sources=NARRATIVE_SOURCES, derived={
        "n_trade_log_rows": n_rows,
        "position_change_threshold_pp": POSITION_CHANGE_THRESHOLD_PP,
        "comparison_oos_months_position_change_gt_5pct": int((d > POSITION_CHANGE_THRESHOLD_PP / 100).sum()),
        "comparison_oos_sum_abs_position_change": round(float(d.sum()), 4),
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
    tourn, hind, _ = run_tournament(K)
    write_evidence(df, tourn, hind)
    write_metadata(df, json.loads((RES / "winner_summary.json").read_text()), time.time() - t0)
    write_narrative_provenance()
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
