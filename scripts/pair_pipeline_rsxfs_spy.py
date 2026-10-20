#!/usr/bin/env python3
"""Pair pipeline: advance retail sales ex food services (FRED RSXFS) x SPY (Phase B harness).

RSXFS = Advance Retail Sales: Retail Trade (retail sales excluding food services; nominal $ millions, SA, U.S.
Census Bureau). The first print is the advance estimate, about two weeks after month-end; it is revised in the
next two monthly reports and in annual benchmark revisions.

The tournament runs on scripts/harness (spec: scripts/pair_spec_rsxfs_spy.py) on two tracks:
  * MAIN, "As known at the time": real-time RSXFS vintages (ALFRED); each rebalance uses the vintage visible
    when its return window opens, and growth signals and rolling thresholds are computed inside that vintage.
  * COMPARISON, "As revised today (hindsight)": today's revised values with point-in-time release timing.
Each track selects its own winner on in-sample data by the D9 lead-plateau rule over the registry grid L2..L13
(position_shift 0: the lead is the whole lag between the reading month and the return month); null tournament
K=100, paired block bootstrap vs buy-and-hold SPY, leak tests. The earlier research run 20261016 (raw IS-Sharpe
argmax on a common IS start, fixed lags, commit 1d06839f on fix261016_strict_lead_floor, never on the main site) is
replayed exactly by the harness (LEGACY_SPEC) and kept as the previous rule; the rule the main site shows (run
20260827, commit 6d6b16db, OOS-selected) is recorded for reference from that run's own files.

This file keeps the pair's evidence stages (computed on the revised panel, descriptive only), metadata and the
narrative-provenance record. Inference on overlapping h-month forward returns is HAC (Newey-West, maxlags >=
h-1) for correlations, predictive regressions and local projections, and a moving-block bootstrap for the
quantile regression; the smallest Granger p-value over the lags tried is Bonferroni-adjusted.
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import pair_spec_rsxfs_spy as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series, write_json  # noqa: E402
from harness.evidence import evidence_path, write_evidence_facts  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "rsxfs_spy"
DATE_TAG = "20261020"  # Phase B B1 post-Codex rerun: harness v2 (run_tag), data.py last-row fix, null v4
MAIN_SITE_TAG = "20260827"  # the run whose rule the main site shows (OOS-selected, legacy method; commit 6d6b16db)
TARGET_SYMBOL = "SPY"
COST_BPS = 5
K_NULL = 100                          # null-tournament draws per track
EXPECTED_DIRECTION = "procyclical"
EVIDENCE_SIGNAL = "rsxfs_yoy"         # YoY growth: the descriptive-test transform of the published run
HORIZONS = (1, 3, 6, 12)              # forward SPY return horizons (months)
GRANGER_MAXLAG = 12                   # Granger lags 1..12; the smallest p is Bonferroni-adjusted for 12 tests
ROLL_CORR_WINDOW, ROLL_CORR_MIN = 60, 36
QR_BLOCK, QR_DRAWS, QR_SEED = 6, 999, 42
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90)
SIGNIFICANCE_P = 0.05                 # significance level of the stars, bands and lines on the evidence charts

DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
NOW_ISO = datetime.now(timezone.utc).isoformat()
SIGNALS = spec_mod.SIGNALS


def hac_lags(n: int, h: int) -> int:
    """Newey-West lag length for overlapping h-period returns: max(int(0.75 n^(1/3)), h-1)."""
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


def hac_slope(x: pd.Series, y: pd.Series, h: int) -> dict:
    """OLS y ~ x with HAC errors (maxlags >= h-1)."""
    import statsmodels.api as sm
    lags = hac_lags(len(x), h)
    fit = sm.OLS(y.to_numpy(float), sm.add_constant(x.to_numpy(float))).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    lo, hi = fit.conf_int()[1]
    return {"coef": float(fit.params[1]), "se": float(fit.bse[1]), "t_stat": float(fit.tvalues[1]),
            "p_value": float(fit.pvalues[1]), "ci_lower": float(lo), "ci_upper": float(hi),
            "r_squared": float(fit.rsquared), "n": int(fit.nobs), "nw_lags": lags}


def build_panel() -> pd.DataFrame:
    """Revised RSXFS (latest pinned ALFRED vintage) and pinned SPY month-end closes on the full monthly grid."""
    idx = spec_mod.rebalance_index()
    lv = spec_mod.revised_levels()
    df = lv.reindex(idx)
    df.index.name = "date"
    full = spec_mod.features(lv)
    for col in SIGNALS.values():
        df[col] = full[col].reindex(idx)
    df["spy"] = spec_mod.target_prices().reindex(idx)
    df["spy_ret"] = df["spy"].pct_change()
    for h in HORIZONS:
        df[f"spy_fwd_{h}m"] = df["spy"].shift(-h) / df["spy"] - 1
    df.to_parquet(DATA_DIR / f"{PAIR_ID}_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_{PAIR_ID}_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_{PAIR_ID}_{DATE_TAG}.md")
    pd.DataFrame([
        {"Column Name": "rsxfs", "Display Name": "Retail sales ex food services (RSXFS)",
         "Description": "Advance Retail Sales: Retail Trade (retail sales excluding food services)",
         "Source": "FRED / ALFRED (pinned vintages; U.S. Census Bureau, Advance Monthly Retail Trade Survey)",
         "Series ID": "RSXFS", "Unit": "Millions of USD", "Transformation": "Monthly level",
         "Seasonal Adj.": "Seasonally adjusted",
         "Direction Convention": "Higher growth = stronger consumer spending",
         "Effective Start": str(df["rsxfs"].first_valid_index().date()),
         "Known Quirks": "Trending nominal level, so the signals are growth rates; the advance estimate is first "
                         "printed about two weeks after month-end and revised in the next two monthly reports and "
                         "in annual benchmark revisions; extreme 2020-21 swings",
         "Display Note": "Nominal, not inflation-adjusted. Excludes food services (restaurants and bars).",
         "Refresh Freq.": "Monthly", "Refresh Source": "data/release_calendar/vintages/RSXFS.csv.gz"},
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


def trade_reason(winner: dict) -> str:
    return f"{winner['signal_code']} {winner['direction']} rule crossed {winner['threshold_code']}"


def main_site_rule() -> dict:
    """The rule shown on the main site: winner of run 20260827 (strategy_returns_20260827_meta.json winner key),
    its row in tournament_results_20260827.csv (both restored from commit 6d6b16db, byte-identical to main). That run
    selected on test-period Sharpe (its is_sharpe column holds the OOS values), so it is reported as the main-site
    rule, not replayed as a selection rule."""
    meta = json.loads((RES / f"strategy_returns_{MAIN_SITE_TAG}_meta.json").read_text())
    sig, thr, dirn, lead = meta["winner_key"].split("|")
    t = pd.read_csv(RES / f"tournament_results_{MAIN_SITE_TAG}.csv")
    r = t[(t["signal"] == sig) & (t["threshold"] == thr) & (t["direction"] == dirn) & (t["lead_months"] == int(lead))]
    if len(r) != 1:
        raise ValueError(f"main-site rule {meta['winner_key']} not found once in tournament_results_{MAIN_SITE_TAG}")
    r = r.iloc[0]
    return {"signal": sig, "threshold": thr, "direction": dirn, "lead_value": int(lead),
            "oos_sharpe": float(r["oos_sharpe"]), "tag": MAIN_SITE_TAG,
            "source": f"tournament_results_{MAIN_SITE_TAG}.csv row {int(r.name)}, "
                      f"strategy_returns_{MAIN_SITE_TAG}_meta.json winner_key",
            "note": f"Rule shown on the main site (run {MAIN_SITE_TAG}), selected on its test-period Sharpe (legacy "
                    "method); reference only, not a selection rule."}


def run_tournament() -> tuple[pd.DataFrame, dict, dict]:
    out = run_pair(PAIR_ID, DATE_TAG, K=K_NULL, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "lookback": "LB60 where rolling thresholds apply",
        "strategy_description": "Hold SPY when the lagged retail sales growth signal is on the favorable side "
                                "of its threshold; otherwise cash (long/cash).",
        "notes": "Retail sales ex food services (RSXFS) is a nominal, trending level, so every signal is a growth "
                 "transform. Headline = as known at the time (real-time "
                 "vintages); still a search-selected rule. The main site shows the 20260827 rule (OOS-selected, "
                 "legacy method); the earlier research run 20261016 (raw in-sample Sharpe argmax, fixed lags, never "
                 "on the main site) is replayed exactly and kept as the previous rule."})
    winner = json.loads((RES / "winner_summary.json").read_text())
    # the rule the main site still shows (run 20260827, OOS-selected): recorded next to the selection as the
    # legacy_oos_selected_row, read from that run's immutable files; reference only, never a selection rule
    winner["selection"]["legacy_oos_selected_row"] = main_site_rule()
    write_json(RES / "winner_summary.json", winner, "winner_summary")
    from harness import charts as HC            # re-record the harness charts on the amended summary (provenance)
    HC.lead_plateau(PAIR_ID, DATE_TAG, spec_mod.SPEC.lead_unit)
    HC.chance_check(PAIR_ID, DATE_TAG)
    tourn = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["main"]
    ws = winner_series(res, res.selection["winner"])
    log = trade_log(ws, TARGET_SYMBOL, COST_BPS, trade_reason(winner))
    log.to_csv(RES / "winner_trade_log.csv", index=False)
    log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, winner, out


def _qr_block_bootstrap(d: pd.DataFrame) -> tuple[list[dict], dict]:
    """Quantile regression of the 3-month forward SPY return on the YoY retail sales growth at each tau, with a
    moving-block bootstrap (overlapping 3-month returns): per-tau SE, 95% percentile interval and two-sided p of
    slope = 0, and a Wald test of equal slopes across taus from the joint bootstrap covariance."""
    import statsmodels.formula.api as smf
    formula = "y ~ x"
    est = {q: float(smf.quantreg(formula, d).fit(q=q).params["x"]) for q in QUANTILES}
    iid = {q: float(smf.quantreg(formula, d).fit(q=q).pvalues["x"]) for q in QUANTILES}
    rng = np.random.default_rng(QR_SEED)
    n = len(d)
    nb = int(np.ceil(n / QR_BLOCK))
    draws = []
    for _ in range(QR_DRAWS):
        starts = rng.integers(0, n - QR_BLOCK + 1, size=nb)
        ix = np.concatenate([np.arange(s, s + QR_BLOCK) for s in starts])[:n]
        sub = d.iloc[ix]
        try:
            draws.append([float(smf.quantreg(formula, sub).fit(q=q).params["x"]) for q in QUANTILES])
        except Exception:  # noqa: BLE001 - a degenerate resample is skipped and counted
            continue
    B = np.asarray(draws)
    rows = []
    for j, q in enumerate(QUANTILES):
        b = B[:, j]
        rows.append({"quantile": q, "coef": est[q], "se": float(b.std(ddof=1)),
                     "p_value": float(min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))),
                     "ci_lower": float(np.quantile(b, 0.025)), "ci_upper": float(np.quantile(b, 0.975)),
                     "p_value_iid": iid[q], "n": n,
                     "inference": f"moving-block bootstrap, block {QR_BLOCK}, {len(B)} draws, seed {QR_SEED}"})
    ref = QUANTILES.index(0.50)
    others = [j for j in range(len(QUANTILES)) if j != ref]
    dobs = np.array([est[QUANTILES[j]] - est[0.50] for j in others])
    D = B[:, others] - B[:, [ref]]
    stat = float(dobs @ np.linalg.pinv(np.atleast_2d(np.cov(D, rowvar=False))) @ dobs)
    p = float(stats.chi2.sf(stat, len(others)))
    test = {"method": f"block-bootstrap Wald (block {QR_BLOCK}, {len(B)} draws, seed {QR_SEED})", "stat": stat,
            "df": len(others), "p_value": p, "reject_equality": bool(p < 0.05), "n": n}
    return rows, test


def write_evidence(df: pd.DataFrame, winner: dict) -> None:
    from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss
    x_col = EVIDENCE_SIGNAL

    # correlations: Pearson r of each signal with each forward return; p from HAC (overlapping returns)
    corr_rows = []
    for col in SIGNALS.values():
        for h in HORIZONS:
            fwd = f"spy_fwd_{h}m"
            sub = df[[col, fwd]].dropna()
            if len(sub) < 24 or sub[col].std() == 0:
                continue
            r, p_iid = stats.pearsonr(sub[col], sub[fwd])
            zx = (sub[col] - sub[col].mean()) / sub[col].std()
            zy = (sub[fwd] - sub[fwd].mean()) / sub[fwd].std()
            hs = hac_slope(zx, zy, h)
            corr_rows.append({"pair_name": f"{col}_to_{fwd}", "metric": "pearson", "value": float(r),
                              "p_value": hs["p_value"], "p_value_iid": float(p_iid), "hac_lags": hs["nw_lags"],
                              "n": len(sub)})
    pd.DataFrame(corr_rows).to_csv(CORE / "correlations.csv", index=False)

    # Granger: does YoY retail sales growth help forecast SPY returns (lags 1..GRANGER_MAXLAG)?
    g = df[["spy_ret", x_col]].dropna()
    tests = grangercausalitytests(g[["spy_ret", x_col]], maxlag=GRANGER_MAXLAG, verbose=False)
    granger_rows = []
    for lag, res in tests.items():
        f_stat, p_val, _, _ = res[0]["ssr_ftest"]
        granger_rows.append({"lag": lag, "f_stat": f_stat, "p_value": p_val,
                             "p_value_bonferroni": min(1.0, GRANGER_MAXLAG * p_val), "direction": "RSXFS_to_SPY"})
    gr = pd.DataFrame(granger_rows)
    gr.to_csv(CORE / "granger_causality.csv", index=False)
    gr.to_csv(RES / "granger_by_lag.csv", index=False)

    # pre-whitened CCF: first difference of YoY growth vs SPY return; positive lag = retail sales growth leads
    ccf_rows = []
    xd = df[x_col].diff()
    for lag in range(-12, 13):
        sub = pd.concat([xd.shift(lag), df["spy_ret"]], axis=1).dropna()
        c = sub.iloc[:, 0].corr(sub.iloc[:, 1]) if len(sub) > 24 else np.nan
        band = stats.norm.ppf(1 - SIGNIFICANCE_P / 2) / np.sqrt(max(len(sub), 1))
        ccf_rows.append({"lag": lag, "ccf": c, "upper_ci": band, "lower_ci": -band,
                         "significant": bool(abs(c) > band) if pd.notna(c) else False})
    pd.DataFrame(ccf_rows).to_csv(CORE / "ccf_prewhitened.csv", index=False)

    # concurrent quartiles of YoY retail sales growth
    sub = df[[x_col, "spy_ret"]].dropna()
    q = pd.qcut(sub[x_col], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q_rows = []
    for label in ["Q1", "Q2", "Q3", "Q4"]:
        rets = sub.loc[q == label, "spy_ret"]
        q_rows.append({"quartile": label, "mean_return": float(rets.mean()), "sharpe": ann_metrics(rets)["sharpe"],
                       "n": int(len(rets)), "chg_low": float(sub.loc[q == label, x_col].min()),
                       "chg_high": float(sub.loc[q == label, x_col].max())})
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)

    # rolling correlation and a z-score proxy for instability
    d2 = df[[x_col, "spy_ret"]].dropna()
    rc = d2[x_col].rolling(ROLL_CORR_WINDOW, min_periods=ROLL_CORR_MIN).corr(d2["spy_ret"]).dropna()
    rc = pd.DataFrame({"date": rc.index, "rolling_corr": rc.values})
    rc.to_csv(RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    max_abs_z = 0.0
    if not rc.empty and rc["rolling_corr"].std() > 0:
        max_abs_z = float(((rc["rolling_corr"] - rc["rolling_corr"].mean()) / rc["rolling_corr"].std()).abs().max())
    (RES / f"structural_break_{PAIR_ID}.json").write_text(json.dumps(
        {"pair_id": PAIR_ID, "method": "rolling-correlation z-score proxy (not a formal break test)",
         "window_months": ROLL_CORR_WINDOW, "max_abs_z": max_abs_z}, indent=2) + "\n")

    # local projections / predictive regressions: forward h-month return on YoY retail sales growth, HAC >= h-1
    lp_rows = []
    for h in HORIZONS:
        s = df[[x_col, f"spy_fwd_{h}m"]].dropna()
        lp_rows.append({"horizon": h, **hac_slope(s[x_col], s[f"spy_fwd_{h}m"], h),
                        "sample_start": s.index.min().date().isoformat(), "sample_end": s.index.max().date().isoformat()})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)

    qs = df[[x_col, "spy_fwd_3m"]].dropna().rename(columns={x_col: "x", "spy_fwd_3m": "y"})
    qr_rows, qr_test = _qr_block_bootstrap(qs)
    pd.DataFrame(qr_rows).to_csv(CORE / "quantile_regression.csv", index=False)
    (CORE / "quantile_equality_test.json").write_text(json.dumps(qr_test, indent=2) + "\n")

    # stress windows on the MAIN winner's deployable returns, with the sample phase of every month
    subperiods = [("Dot-Com", "2000-03-31", "2002-10-31"), ("GFC", "2007-12-31", "2009-06-30"),
                  ("COVID", "2020-02-29", "2020-06-30"), ("2022 Rate Hikes", "2022-01-31", "2022-12-31")]
    strat = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    sp_rows = []
    for name, start, end in subperiods:
        seg = strat.loc[start:end]
        cnt = seg["sample"].value_counts()
        sp_rows.append({"period": name, "start": start, "end": end, "n_obs": int(len(seg)),
                        "n_pre_is": int(cnt.get("pre_IS", 0)), "n_is": int(cnt.get("IS", 0)),
                        "n_oos": int(cnt.get("OOS", 0)),
                        "strategy_sharpe": ann_metrics(seg["strategy_return"])["sharpe"],
                        "buy_hold_sharpe": ann_metrics(seg["benchmark_return"])["sharpe"],
                        "strategy_return": float((1 + seg["strategy_return"]).prod() - 1),
                        "buy_hold_return": float((1 + seg["benchmark_return"]).prod() - 1)})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)

    station_rows = []
    for col in ["rsxfs"] + list(SIGNALS.values()) + ["spy_ret"]:
        s = df[col].dropna()
        adf = adfuller(s, autolag="AIC")
        station_rows.append({"variable": col, "test": "ADF", "statistic": round(float(adf[0]), 4),
                             "p_value": round(float(adf[1]), 4), "lags": int(adf[2]),
                             "conclusion": "stationary" if adf[1] < 0.05 else "unit_root_not_rejected"})
        kp = kpss(s, regression="c", nlags="auto")
        station_rows.append({"variable": col, "test": "KPSS", "statistic": round(float(kp[0]), 4),
                             "p_value": round(float(kp[1]), 4), "lags": int(kp[2]),
                             "conclusion": "stationary_not_rejected" if kp[1] > 0.05 else "nonstationary"})
    pd.DataFrame(station_rows).to_csv(RES / f"stationarity_tests_{DATE_TAG}.csv", index=False)

    bs = winner["selection"]["inference"]["oos_sharpe_diff_vs_bh_bootstrap"]
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "track": "as known at the time",
                   "oos_sharpe": winner["oos_sharpe"], "sharpe_diff_vs_bh": bs["observed"],
                   "ci_95_low": bs["ci_95"][0], "ci_95_high": bs["ci_95"][1], "p_diff_le_0": bs["p_diff_le_0"],
                   "method": bs["method"], "block_length": bs["block_length"], "draws": bs["draws"],
                   "seed": bs["seed"]}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "tx_cost_bps": COST_BPS,
                   "gross_sharpe": winner["oos_sharpe"],
                   "net_sharpe": (winner["tracks"]["main"]["winner"] or {}).get("oos_sharpe_net_5bp")}]
                 ).to_csv(VALID / "transaction_costs.csv", index=False)


def write_metadata(winner: dict, elapsed: float) -> None:
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "coincident", "indicator_type": "macro",
        "strategy_objective": "max_sharpe",
        "owner_writes": {
            "dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"],
        },
        "last_updated_by": "evan", "last_updated_at": NOW_ISO, "indicator": "rsxfs", "target": "spy",
        "expected_direction": EXPECTED_DIRECTION, "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == EXPECTED_DIRECTION,
        "mechanism": "Retail sales track household goods spending, the largest part of consumption. Firm sales "
                     "growth supports company revenues and earnings (risk-on); slowing sales are an early sign of "
                     "softening consumer demand.",
        "confidence": "low",
        "key_finding": f"As known at the time (real-time RSXFS vintages), the rule selected on in-sample data uses "
                       f"{winner['signal_code']} / {winner['threshold_code']} at L{winner['lead_value']} "
                       f"(IS Sharpe {winner['is_sharpe']:.2f}); held-out OOS Sharpe {winner['oos_sharpe']:.2f} "
                       f"versus buy-and-hold SPY {winner['bh_sharpe']:.2f}.",
        "caveats": [
            "The strategy is search-selected and needs a frozen-rule holdout confirmation.",
            "Retail sales are nominal and the advance estimate is revised in later reports, so the as-known-at-the-time "
            "and revised tracks differ through revisions as well as release timing.",
            "Retail sales are broadly coincident with the business cycle, so a long apparent lead needs scrutiny.",
            "The 2020-21 collapse and rebound in retail sales is an extreme outlier inside the test window.",
            "The test window was seen by the previously published runs, so it is not a frozen hold-out.",
        ],
        "narrative_summary": "Retail sales ex food services (RSXFS) growth is tested as a procyclical consumer-demand "
                             "overlay for SPY, not as a clean leading indicator.",
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "NBER recession."},
            {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30", "note": "NBER recession."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "NBER recession."},
            {"label": "2022 drawdown", "start": "2022-01-01", "end": "2022-12-31", "note": "Rate-hike bear market."},
        ],
        "data_provenance": {"source": "FRED / ALFRED (U.S. Census Bureau, Advance Monthly Retail Trade Survey)",
                            "series_id": "RSXFS", "accessed_at": NOW_ISO},
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    zooms = ["history_zoom_dotcom", "history_zoom_gfc", "history_zoom_covid", "history_zoom_inflation_2022"]
    evid = ["correlation_heatmap", "regime_stats", "granger_f_by_lag", "ccf_prewhitened", "local_projections",
            "quantile_coef", "rolling_correlation", "structural_break"]
    win_col = winner["signal_column"]

    def charts_for(col: str) -> list[str]:
        out = ["correlation_heatmap"] if col != EVIDENCE_SIGNAL else list(evid)
        if col == win_col:
            out += ["hero", "equity_curves", "drawdown"] + zooms
        return out
    defs = [("rsxfs", "Retail sales ex food services level (RSXFS; nominal $ millions, SA)",
             "FRED / ALFRED RSXFS", "raw", [])]
    formulas = {"rsxfs_yoy": ("Year-over-year growth (tournament signal yoy; descriptive-test transform)",
                                       "100*(x_t/x_{t-12}-1)"),
                "rsxfs_mom": ("Month-over-month growth (tournament signal mom)", "100*(x_t/x_{t-1}-1)"),
                "rsxfs_3m": ("3-month growth (tournament signal chg_3m)", "100*(x_t/x_{t-3}-1)"),
                "rsxfs_6m": ("6-month growth (tournament signal chg_6m)", "100*(x_t/x_{t-6}-1)"),
                "rsxfs_yoy_zscore_60m": ("YoY growth versus its 60-month history (tournament signal "
                                                  "yoy_zscore_60m)", "(yoy - mean60)/std60, min 36 readings"),
                "rsxfs_accel": ("Change in YoY growth (tournament signal accel)", "yoy_t - yoy_{t-1}")}
    defs += [(c, formulas[c][0], formulas[c][1], "derivative", charts_for(c)) for c in SIGNALS.values()]
    spy_defs = [
        ("spy", "SPY adjusted month-end close", "month-end adjusted close", "raw", ["hero"] + zooms),
        ("spy_ret", "SPY monthly return", "spy_t / spy_{t-1} - 1", "derivative",
         ["equity_curves", "drawdown", "regime_stats", "ccf_prewhitened", "granger_f_by_lag", "rolling_correlation",
          "subperiod_sharpe"]),
    ] + [(f"spy_fwd_{h}m", f"{h}-month forward SPY return", f"spy_{{t+{h}}} / spy_t - 1", "derivative",
          ["correlation_heatmap", "local_projections"] + (["quantile_coef"] if h == 3 else []))
         for h in HORIZONS]
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {"canonical_column": "rsxfs",
                           "display_name": "Retail sales ex food services (RSXFS)",
                           "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch}
                                           for c, d, f, r, ch in defs]},
        "target_axis": {"canonical_column": "spy", "display_name": "SPY adjusted close",
                        "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch}
                                        for c, d, f, r, ch in spy_defs]},
        "notes": "Six RSXFS growth transforms are the tournament signals (pair spec SIGNALS); the level trends and "
                 "is never traded. YoY growth is the transform used by the descriptive tests.",
    }
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"],
                                               "benchmark_oos_sharpe": winner["bh_sharpe"],
                                               "oos_max_drawdown": winner["oos_max_drawdown"],
                                               "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    (RES / "evidence_status.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search", "updated_at": NOW_ISO,
        "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": f"Winner selected on in-sample data by the lead-plateau rule (D9) from the {DATE_TAG} "
                          "tournament on real-time RSXFS vintages and reported on the test window (seen by earlier "
                          "runs, so not a frozen hold-out).",
        "next_step": "Freeze the selected rule and run a confirmation test on future data or a reserved holdout window.",
        "owner": "evan"}, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    (RES / "analyst_suggestions.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{
            "signal_name": "Lead robustness", "proposed_by": "evan", "source": "FRED",
            "observation": f"The rule selected on in-sample data uses a lead of {winner['lead_value']} months on the "
                           f"{winner['signal_display_name'].lower()} ({winner['direction']}, "
                           f"{winner['threshold_code']}); held-out OOS max drawdown {winner['oos_max_drawdown']:.1%} "
                           f"vs buy-and-hold {winner['bh_max_drawdown']:.1%}.",
            "rationale": "Retail sales are broadly coincident and the sample holds few consumer downturns, so "
                         "the lead needs adjacent-lead durability on new data.",
            "possible_use_case": "robustness check",
            "caveats": "Search-selected rule; not final-exam validated.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
        }],
        "notes": "Generated with the retail sales ex food services (RSXFS) x SPY pair pipeline.",
    }, indent=2) + "\n")


def revision_stats() -> dict:
    """How much the advance estimate is revised: first-print vs today's month-over-month and year-over-year growth
    for every reference month whose first print is in the pinned ALFRED file (months first seen in the archive's
    opening vintage are excluded: their first value there is not the advance estimate). Written per month to
    revision_first_vs_latest_<tag>.csv; the summary goes to evidence_facts."""
    from harness import align
    v = align.load_vintages(spec_mod.SERIES)
    first = v.groupby("date")["realtime_start"].min()
    latest = v[v["realtime_end"] == v["realtime_end"].max()].set_index("date")["value"]
    rows = []
    for m, rs in first.items():
        if rs == v["realtime_start"].min():
            continue
        fv = v[(v["realtime_start"] <= rs) & (v["realtime_end"] >= rs)].set_index("date")["value"]
        p1, p12 = m - pd.DateOffset(months=1), m - pd.DateOffset(months=12)
        rows.append({"month": m.strftime("%Y-%m"), "first_release": rs.date().isoformat(),
                     "mom_first": 100 * (fv[m] / fv[p1] - 1), "mom_latest": 100 * (latest[m] / latest[p1] - 1),
                     "yoy_first": 100 * (fv[m] / fv[p12] - 1), "yoy_latest": 100 * (latest[m] / latest[p12] - 1)})
    d = pd.DataFrame(rows)
    d.to_csv(RES / f"revision_first_vs_latest_{DATE_TAG}.csv", index=False)
    out = {"n_months": int(len(d)), "first_month": d["month"].iloc[0], "last_month": d["month"].iloc[-1]}
    for k in ("mom", "yoy"):
        e = d[f"{k}_first"] - d[f"{k}_latest"]
        out[k] = {"mean_abs_revision_pp": round(float(e.abs().mean()), 4),
                  "sign_changed_share": round(float((np.sign(d[f"{k}_first"]) != np.sign(d[f"{k}_latest"])).mean()), 4),
                  "corr_first_latest": round(float(d[f"{k}_first"].corr(d[f"{k}_latest"])), 4),
                  "sd_latest_pp": round(float(d[f"{k}_latest"].std()), 4)}
    return out


NARRATIVE_SOURCES = ["regime_quartile_returns.csv", "granger_by_lag.csv", "subperiod_sharpe.csv",
                     f"core_models_{DATE_TAG}/quantile_regression.csv",
                     f"core_models_{DATE_TAG}/quantile_equality_test.json",
                     f"core_models_{DATE_TAG}/local_projections.csv",
                     f"core_models_{DATE_TAG}/ccf_prewhitened.csv"]


def write_narrative_provenance(df: pd.DataFrame) -> None:
    """evidence_facts_<tag>.json: the evidence tables the page prose cites (scripts/gate_number_provenance.py),
    plus derived facts (trade-log counts, Granger summary)."""
    blog = pd.read_csv(RES / "winner_trades_broker_style.csv", parse_dates=["trade_date"])
    sr = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"])
    oos = sr[sr["sample"] == "OOS"]
    oos_first = oos["date"].iloc[0]
    tlo = blog[blog["trade_date"] >= oos_first]            # log rows dated in the test period
    size = tlo["trade_size_pct"].astype(float) / 100
    d = np.abs(np.diff(oos["position"].fillna(0.0).to_numpy(float)))   # harness window: changes inside OOS rows
    gr = pd.read_csv(RES / "granger_by_lag.csv")
    jmin = int(gr["p_value"].idxmin())
    ccf = pd.read_csv(CORE / "ccf_prewhitened.csv")
    write_evidence_facts(PAIR_ID, DATE_TAG, sources=NARRATIVE_SOURCES, derived={
        "trade_log_rows": int(len(blog)),
        "n_oos_trade_log_rows": int(len(tlo)),
        "oos_sum_abs_position_change": round(float(size.sum()), 4),
        "n_oos_changes_within_test": int((d > 0).sum()),
        "oos_entry_move_into_first_test_month": bool(len(tlo) and tlo["trade_date"].iloc[0] == oos_first),
        "significance_p": SIGNIFICANCE_P,
        "n_granger_lags": GRANGER_MAXLAG,
        "granger_min_p": float(gr.loc[jmin, "p_value"]),
        "granger_best": {"lag": int(gr.loc[jmin, "lag"])},
        "granger_min_p_bonferroni": float(gr.loc[jmin, "p_value_bonferroni"]),
        # CCF offsets outside the band: retail sales growth moves first (positive lags) / SPY first (|negative lags|)
        "ccf_sales_first": {"lag": [int(v) for v in ccf.loc[ccf["significant"] & (ccf["lag"] > 0), "lag"]]},
        "ccf_spy_first": {"lag": [int(-v) for v in ccf.loc[ccf["significant"] & (ccf["lag"] < 0), "lag"]]},
        "panel_first_month": df["rsxfs"].first_valid_index().strftime("%Y-%m"),
        "revision": revision_stats(),
    })


def main() -> None:
    t0 = time.time()
    for path in (RES, CORE, VALID):
        path.mkdir(parents=True, exist_ok=True)
    evidence_path(PAIR_ID, DATE_TAG).unlink(missing_ok=True)   # rebuilt from scratch (write_evidence_facts merges)
    df = build_panel()
    df[list(SIGNALS.values())].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    _tourn, winner, _ = run_tournament()
    write_evidence(df, winner)
    write_metadata(winner, time.time() - t0)
    write_narrative_provenance(df)
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
