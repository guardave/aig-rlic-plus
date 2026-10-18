#!/usr/bin/env python3
"""Pair pipeline: SLOOS C&I lending standards (net % of banks tightening, large and middle-market firms, FRED
DRTSCILM) x SPY (Phase B harness).

QUARTERLY. The indicator is the net percentage of domestic banks reporting tighter standards for C&I loans to
large and middle-market firms in the Fed's Senior Loan Officer Opinion Survey (DRTSCILM; NOT the small-firm series
DRTSCIS that the pair id names). Economic prior: rising net tightening = a credit crunch that precedes equity
weakness -> COUNTERCYCLICAL.

The tournament runs on scripts/harness (spec: scripts/pair_spec_sloos_ci_small_spy.py) on two tracks:
  * MAIN, "As known at the time": real-time DRTSCILM vintages (ALFRED archive from 2010-04), signals and rolling
    thresholds computed inside the vintage visible when each quarter's return window opens.
  * COMPARISON, "As revised today (hindsight)": today's revised values with point-in-time release timing.
Each track selects its own winner by the D9 lead-plateau rule on in-sample data; null tournament K=100, paired
block bootstrap vs buy-and-hold, leak tests. The evidence stages below are descriptive and run on the revised
panel. Overlapping-horizon inference uses HAC errors with maxlags >= h-1; a minimum over several lags is
Holm-adjusted.
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
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss

warnings.simplefilter("ignore", InterpolationWarning)   # KPSS p-values outside the table are capped at 0.1 / 0.01

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import pair_spec_sloos_ci_small_spy as spec_mod  # noqa: E402
from harness.artifacts import trade_log, winner_series  # noqa: E402
from harness.evidence import write_evidence_facts  # noqa: E402
from harness.run import run_pair  # noqa: E402

PAIR_ID = "sloos_ci_small_spy"
DATE_TAG = "20261018"  # Phase B B1: harness, two tracks, D9 plateau, null K=100, bootstrap
TARGET_SYMBOL = "SPY"
COST_BPS = 5
DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
NOW_ISO = datetime.now(timezone.utc).isoformat()
PPY = 4                                   # quarterly annualization
SIGNALS = spec_mod.SIGNALS
SIGNAL_DISPLAY = spec_mod.SIGNAL_DISPLAY
EVIDENCE_SIGNAL = "sloos_chg_4q"          # 4-quarter change in net tightening: the descriptive tests' transform
HORIZONS = (1, 2, 4)                      # forward-return horizons (quarters)
GRANGER_MAXLAG = 4                        # quarters
CCF_MAXLAG = 4                            # quarters
ROLL_CORR_WINDOW, ROLL_CORR_MIN = 20, 12  # quarters
BREAK_TRIM = 0.15                         # Quandt-Andrews trimming
BREAK_DRAWS = 499
SEED = 42
POSITION_CHANGE_PP = 5                    # a position change counted as a trade when larger than this (pp)
EPISODES = [("Dot_Com", "2000-03-31", "2002-12-31"), ("GFC", "2007-12-31", "2009-06-30"),
            ("COVID", "2020-03-31", "2020-06-30"), ("Rate_Hike_2022", "2022-03-31", "2022-12-31")]


def hac_lags(n: int, h: int) -> int:
    """Newey-West maxlags: the usual rule of thumb, at least h-1 for overlapping h-period returns."""
    return max(int(0.75 * n ** (1 / 3)), h - 1)


def ann_metrics(rets: pd.Series) -> dict[str, float]:
    rets = rets.dropna()
    if len(rets) < 2 or rets.std() == 0:
        return {"sharpe": np.nan, "ann_return": np.nan, "n": int(len(rets))}
    return {"sharpe": float(rets.mean() / rets.std() * np.sqrt(PPY)),
            "ann_return": float((1 + rets).prod() ** (PPY / len(rets)) - 1), "n": int(len(rets))}


def build_panel() -> pd.DataFrame:
    """Revised DRTSCILM (latest pinned ALFRED vintage) and SPY quarter-end closes on the full quarterly grid."""
    idx = spec_mod.rebalance_index()
    lv = spec_mod.revised_levels()
    df = lv.reindex(idx)
    df["spy"] = spec_mod.target_prices().reindex(idx)
    df["spy_ret"] = df["spy"].pct_change()
    for h in HORIZONS:
        df[f"spy_fwd_{h}q"] = df["spy"].pct_change(h).shift(-h)
    full = spec_mod.features(lv)
    for col in SIGNALS.values():
        df[col] = full[col].reindex(idx)
    df.to_parquet(DATA_DIR / f"{PAIR_ID}_quarterly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_{PAIR_ID}_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_{PAIR_ID}_{DATE_TAG}.md")
    pd.DataFrame([
        {"Column Name": "sloos", "Display Name": "SLOOS C&I net tightening, large and middle-market firms",
         "Description": "Net percentage of domestic banks tightening standards for C&I loans to large and "
                        "middle-market firms (Senior Loan Officer Opinion Survey)",
         "Source": "Federal Reserve via ALFRED (pinned vintages)", "Series ID": "DRTSCILM", "Unit": "Net percent",
         "Transformation": "Quarterly level (survey diffusion measure)",
         "Direction Convention": "Higher = more banks tightening (tighter credit, bearish for equities)",
         "Effective Start": str(df["sloos"].first_valid_index().date()),
         "Known Quirks": "Bounded, mean-reverting diffusion index; published inside the quarter it is stamped to; "
                         "a 2019-11 vintage revised the history; real-time vintages from 2010-04",
         "Display Note": "Banks tighten lending standards before and during credit crunches.",
         "Refresh Freq.": "Quarterly", "Refresh Source": f"data/release_calendar/vintages/{spec_mod.SERIES}.csv.gz"},
        {"Column Name": "spy", "Display Name": "SPY adjusted close", "Description": "SPDR S&P 500 ETF adjusted close",
         "Source": "Yahoo Finance (pinned)", "Series ID": "SPY", "Unit": "USD",
         "Transformation": "Quarter-end adjusted close", "Direction Convention": "Higher = higher equity price",
         "Effective Start": str(df["spy"].first_valid_index().date()), "Known Quirks": "ETF history begins 1993",
         "Display Note": "Equity target and benchmark.", "Refresh Freq.": "Daily",
         "Refresh Source": "data/phaseB_inputs/spy_month_end_20261017.csv"},
    ]).to_csv(DATA_DIR / f"data_dictionary_{PAIR_ID}_{DATE_TAG}.csv", index=False)
    print(f"  Panel rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def trade_reason(winner: dict) -> str:
    return f"{winner['signal_code']} {winner['direction']} rule crossed {winner['threshold_code']}"


def run_tournament() -> tuple[pd.DataFrame, dict, dict]:
    out = run_pair(PAIR_ID, DATE_TAG, K=100, extra={
        "target_symbol": TARGET_SYMBOL, "cost_bps": COST_BPS,
        "lookback": "20q where rolling thresholds apply",
        "strategy_description": "Hold SPY when the lagged SLOOS tightening signal is on the favourable side of its "
                                "threshold; otherwise hold cash.",
        "notes": "SLOOS C&I net tightening (large and middle-market firms, DRTSCILM) is a quarterly bank-credit "
                 "survey. Headline = as known at the time (real-time vintages from 2010), so the training period "
                 "is short; still a search-selected rule."})
    winner = json.loads((RES / "winner_summary.json").read_text())
    tourn = pd.read_csv(RES / f"tournament_results_{DATE_TAG}.csv")
    tourn["valid"] = tourn["valid"].astype(bool)
    res = out["results"]["main"]
    ws = winner_series(res, res.selection["winner"])
    log = trade_log(ws, TARGET_SYMBOL, COST_BPS, trade_reason(winner))
    log.to_csv(RES / "winner_trade_log.csv", index=False)
    log.to_csv(RES / "winner_trades_broker_style.csv", index=False)
    return tourn, winner, out


def hac_corr_p(x: pd.Series, y: pd.Series, h: int) -> tuple[float, int]:
    """p-value of a correlation with overlapping h-quarter returns: slope of standardized y on standardized x
    with HAC (Newey-West) errors, maxlags >= h-1."""
    zx, zy = (x - x.mean()) / x.std(), (y - y.mean()) / y.std()
    lags = hac_lags(len(x), h)
    fit = sm.OLS(zy.to_numpy(), sm.add_constant(zx.to_numpy())).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return float(fit.pvalues[1]), lags


def prewhiten(x: pd.Series, y: pd.Series) -> tuple[pd.Series, pd.Series, int]:
    """Box-Jenkins pre-whitening: AR(p) fitted to x (p by AIC, up to CCF_MAXLAG); the same filter applied to y."""
    d = pd.concat([x, y], axis=1).dropna()
    best = min(range(1, CCF_MAXLAG + 1), key=lambda p: AutoReg(d.iloc[:, 0].to_numpy(), lags=p).fit().aic)
    phi = AutoReg(d.iloc[:, 0].to_numpy(), lags=best).fit().params[1:]

    def filt(s):
        out = s.copy()
        for k, c in enumerate(phi, start=1):
            out = out - c * s.shift(k)
        return out
    return filt(d.iloc[:, 0]), filt(d.iloc[:, 1]), best


def structural_break(df: pd.DataFrame) -> dict:
    """Quandt-Andrews sup-F for a break in spy_ret_t = a + b * chg4q_{t-1} (15% trimming), residual-bootstrap
    p-value under the no-break null."""
    d = pd.concat([df["spy_ret"], df[EVIDENCE_SIGNAL].shift(1)], axis=1, keys=["y", "x"]).dropna()
    y, x = d["y"].to_numpy(), d["x"].to_numpy()
    n = len(d)
    lo, hi = int(np.floor(BREAK_TRIM * n)), int(np.ceil((1 - BREAK_TRIM) * n))
    X = np.column_stack([np.ones(n), x])

    def f_seq(yv):
        rss_r = np.sum((yv - X @ np.linalg.lstsq(X, yv, rcond=None)[0]) ** 2)
        out = []
        for k in range(lo, hi):
            D = (np.arange(n) >= k).astype(float)
            Xu = np.column_stack([X, X * D[:, None]])
            rss_u = np.sum((yv - Xu @ np.linalg.lstsq(Xu, yv, rcond=None)[0]) ** 2)
            out.append(((rss_r - rss_u) / 2) / (rss_u / (n - 4)))
        return np.array(out)
    fs = f_seq(y)
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    rng = np.random.default_rng(SEED)
    boot = np.array([f_seq(X @ beta + rng.choice(resid, size=n, replace=True)).max() for _ in range(BREAK_DRAWS)])
    k = int(np.argmax(fs))
    seq = pd.DataFrame({"date": d.index[lo:hi], "f_stat": fs})
    seq.to_csv(RES / f"structural_break_fseq_{PAIR_ID}.csv", index=False)
    return {"pair_id": PAIR_ID, "method": "Quandt-Andrews sup-F (Andrews 1993), break in intercept and slope of "
            "spy_ret_t on chg_4q_{t-1}", "trim": BREAK_TRIM, "n": n, "statistic_name": "sup-F", "statistic": float(fs[k]),
            "breakpoint_date": d.index[lo + k].date().isoformat(), "p_value": float((boot >= fs[k]).mean()),
            "p_value_method": f"residual bootstrap under the no-break null, {BREAK_DRAWS} draws, seed {SEED}"}


def write_evidence(df: pd.DataFrame, tourn: pd.DataFrame, winner: dict) -> None:
    from _quantile_regression import DEFAULT_QUANTILES, fit_quantile_regression
    x_col = EVIDENCE_SIGNAL
    # correlations: HAC p-values (overlapping h-quarter returns)
    corr_rows = []
    for col in SIGNALS.values():
        for h in HORIZONS:
            sub = df[[col, f"spy_fwd_{h}q"]].dropna()
            p, lags = hac_corr_p(sub[col], sub[f"spy_fwd_{h}q"], h)
            corr_rows.append({"pair_name": f"{col}_to_spy_fwd_{h}q", "metric": "pearson",
                              "value": float(sub[col].corr(sub[f"spy_fwd_{h}q"])), "p_value": p,
                              "hac_lags": lags, "n": len(sub)})
    pd.DataFrame(corr_rows).to_csv(CORE / "correlations.csv", index=False)

    # Granger by lag (1..4 quarters); the minimum over lags is reported Holm-adjusted
    g = df[["spy_ret", x_col]].dropna()
    tests = grangercausalitytests(g[["spy_ret", x_col]], maxlag=GRANGER_MAXLAG, verbose=False)
    gr = pd.DataFrame([{"lag": lag, "f_stat": r[0]["ssr_ftest"][0], "p_value": r[0]["ssr_ftest"][1],
                        "direction": "SLOOS_to_SPY", "n": len(g)} for lag, r in tests.items()])
    gr["p_holm"] = multipletests(gr["p_value"], method="holm")[1]
    gr.to_csv(CORE / "granger_causality.csv", index=False)
    gr.to_csv(RES / "granger_by_lag.csv", index=False)

    # pre-whitened CCF; positive lag = SLOOS change leads the SPY return
    xw, yw, ar_p = prewhiten(df[x_col], df["spy_ret"])
    ccf_rows = []
    for lag in range(-CCF_MAXLAG, CCF_MAXLAG + 1):
        sub = pd.concat([xw.shift(lag), yw], axis=1).dropna()
        c = float(sub.iloc[:, 0].corr(sub.iloc[:, 1]))
        band = 1.96 / np.sqrt(len(sub))
        ccf_rows.append({"lag": lag, "ccf": c, "upper_ci": band, "lower_ci": -band, "significant": bool(abs(c) > band),
                         "n": len(sub), "prewhiten_ar_order": ar_p})
    pd.DataFrame(ccf_rows).to_csv(CORE / "ccf_prewhitened.csv", index=False)

    # concurrent regime quartiles of the 4-quarter change
    sub = df[[x_col, "spy_ret"]].dropna()
    q = pd.qcut(sub[x_col], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q_rows = []
    for lab in ["Q1", "Q2", "Q3", "Q4"]:
        r = sub.loc[q == lab, "spy_ret"]
        q_rows.append({"quartile": lab, "mean_return": float(r.mean()), "sharpe": ann_metrics(r)["sharpe"],
                       "n": len(r), "chg_low": float(sub.loc[q == lab, x_col].min()),
                       "chg_high": float(sub.loc[q == lab, x_col].max())})
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)

    # rolling correlation and a formal break test
    rc = []
    for dt in df.index:
        w = df.loc[:dt, [x_col, "spy_ret"]].tail(ROLL_CORR_WINDOW).dropna()
        if len(w) >= ROLL_CORR_MIN:
            rc.append({"date": dt, "rolling_corr": float(w[x_col].corr(w["spy_ret"]))})
    pd.DataFrame(rc).to_csv(RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    (RES / f"structural_break_{PAIR_ID}.json").write_text(json.dumps(structural_break(df), indent=2) + "\n")

    # local projections / predictive regressions: HAC maxlags >= h-1
    lp_rows = []
    for h in HORIZONS:
        s = df[[x_col, f"spy_fwd_{h}q"]].dropna()
        lags = hac_lags(len(s), h)
        fit = sm.OLS(s[f"spy_fwd_{h}q"].to_numpy(), sm.add_constant(s[x_col].to_numpy())).fit(
            cov_type="HAC", cov_kwds={"maxlags": lags})
        lp_rows.append({"horizon": h, "coef": float(fit.params[1]), "se": float(fit.bse[1]),
                        "p_value": float(fit.pvalues[1]), "r_squared": float(fit.rsquared), "n": len(s),
                        "nw_lags": lags})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)

    # quantile regression on the NEXT quarter's return (non-overlapping, so QuantReg errors apply)
    qs = df[[x_col, "spy_fwd_1q"]].dropna()
    qr_rows, qr_test = fit_quantile_regression(qs[x_col], qs["spy_fwd_1q"], DEFAULT_QUANTILES)
    pd.DataFrame(qr_rows).to_csv(CORE / "quantile_regression.csv", index=False)
    (CORE / "quantile_equality_test.json").write_text(json.dumps(qr_test, indent=2) + "\n")

    # stress episodes: MAIN (as known at the time) and hindsight winners vs buy-and-hold, with counts
    main_sr = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    hind_sr = pd.read_csv(RES / f"hindsight_strategy_returns_{DATE_TAG}.csv", parse_dates=["date"]).set_index("date")
    sp_rows = []
    for name, s, e in EPISODES:
        m, hs = main_sr.loc[s:e], hind_sr.loc[s:e]
        m_def = m["position"].notna()
        h_def = hs["position"].notna()
        bh = ann_metrics(m["benchmark_return"])
        sp_rows.append({
            "period": name, "start": s, "end": e, "n_quarters": len(m),
            "n_main_defined": int(m_def.sum()), "n_hindsight_defined": int(h_def.sum()),
            "strategy_sharpe": ann_metrics(m.loc[m_def, "strategy_return"])["sharpe"] if m_def.sum() >= 2 else np.nan,
            "hindsight_sharpe": ann_metrics(hs.loc[h_def, "strategy_return"])["sharpe"] if h_def.sum() >= 2 else np.nan,
            "buy_hold_sharpe": bh["sharpe"],
            "strategy_return": float((1 + m.loc[m_def, "strategy_return"]).prod() - 1) if m_def.any() else np.nan,
            "hindsight_return": float((1 + hs.loc[h_def, "strategy_return"]).prod() - 1) if h_def.any() else np.nan,
            "buy_hold_return": float((1 + m["benchmark_return"]).prod() - 1),
            "samples": "/".join(sorted(set(m["sample"])))})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)

    st_rows = []
    for col in ["sloos", *SIGNALS.values(), "spy_ret"]:
        if col == "sloos":
            continue
        s = df[col].dropna()
        adf = adfuller(s, autolag="AIC")
        st_rows.append({"variable": col, "test": "ADF", "statistic": round(float(adf[0]), 4),
                        "p_value": round(float(adf[1]), 4), "lags": int(adf[2]),
                        "conclusion": "stationary" if adf[1] < 0.05 else "unit_root_not_rejected"})
        kp = kpss(s, regression="c", nlags="auto")
        st_rows.append({"variable": col, "test": "KPSS", "statistic": round(float(kp[0]), 4),
                        "p_value": round(float(kp[1]), 4), "lags": int(kp[2]),
                        "conclusion": "stationary_not_rejected" if kp[1] > 0.05 else "nonstationary"})
    pd.DataFrame(st_rows).to_csv(RES / f"stationarity_tests_{DATE_TAG}.csv", index=False)

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


def write_metadata(winner: dict, elapsed: float) -> None:
    first_vintage = winner["tracks"]["main"]["sample"]["first_vintage"]
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "leading", "indicator_type": "credit",
        "strategy_objective": "countercyclical_protection",
        "owner_writes": {"dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
                         "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
                         "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"]},
        "last_updated_by": "evan", "last_updated_at": NOW_ISO, "indicator": "sloos", "target": "spy",
        "expected_direction": "countercyclical", "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "countercyclical",
        "mechanism": "When banks tighten C&I lending standards, firms lose access to credit, investment and hiring "
                     "slow, and default risk rises; tightening historically builds before and during recessions, so "
                     "the credit-crunch prior is to reduce equity exposure when net tightening is high or rising.",
        "confidence": "low",
        "key_finding": f"As known at the time (real-time DRTSCILM vintages from {first_vintage}), the rule selected on "
                       f"in-sample data uses {winner['signal_code']} ({winner['direction']}) at L{winner['lead_value']}q "
                       f"with OOS Sharpe {winner['oos_sharpe']:.2f} versus buy-and-hold {winner['bh_sharpe']:.2f}.",
        "caveats": [
            "Quarterly survey with a small OOS window; the winner is search-selected and needs a frozen-rule holdout.",
            "The real-time (as known at the time) archive starts in 2010, so the training period is short and holds "
            "no recession.",
            "The data is DRTSCILM (large and middle-market firms), not the small-firm series DRTSCIS the pair id names.",
        ],
        "narrative_summary": "Bank C&I lending standards (SLOOS) are tested as a credit-cycle overlay for SPY.",
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "NBER recession."},
            {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30",
             "note": "Net tightening reached its survey highs."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "NBER recession."},
            {"label": "2022 drawdown", "start": "2022-01-01", "end": "2022-12-31", "note": "Rate-hike bear market."}],
        "data_provenance": {"source": "Federal Reserve SLOOS via ALFRED (pinned vintages "
                                      f"data/release_calendar/vintages/{spec_mod.SERIES}.csv.gz)",
                            "series_id": spec_mod.SERIES, "accessed_at": NOW_ISO}}
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    defs = [("sloos", "Net % of banks tightening C&I standards, large and middle-market firms", "FRED DRTSCILM",
             "raw", ["hero"]),
            ("sloos_level", "Net tightening level (net %)", "identity", "threshold_input", []),
            ("sloos_diff_1q", "Quarterly change in net tightening", "x_t - x_{t-1}", "derivative", []),
            ("sloos_chg_4q", "4-quarter change in net tightening", "x_t - x_{t-4}", "threshold_input",
             ["regime_stats", "local_projections", "quantile_coef", "ccf_prewhitened", "granger_f_by_lag"]),
            ("sloos_zscore_20q", "Net tightening versus its 5-year history", "(x - mean20q) / std20q", "derivative", [])]
    tgt = [("spy", "SPY adjusted quarter-end close", "quarter-end adjusted close", "raw", ["hero", "equity_curves"]),
           ("spy_ret", "SPY quarterly return", "spy_t / spy_{t-1} - 1", "derivative", ["regime_stats"])]
    tgt += [(f"spy_fwd_{h}q", f"{h}-quarter forward SPY return", f"spy_{{t+{h}}} / spy_t - 1", "derivative",
             ["correlation_heatmap", "local_projections"] + (["quantile_coef"] if h == 1 else []))
            for h in HORIZONS]
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {"canonical_column": "sloos", "display_name": "SLOOS C&I net tightening (DRTSCILM)",
                           "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch}
                                           for c, d, f, r, ch in defs]},
        "target_axis": {"canonical_column": "spy", "display_name": "SPY adjusted close",
                        "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch}
                                        for c, d, f, r, ch in tgt]},
        "notes": "Scope limited to DRTSCILM-derived signals and SPY returns."}
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"],
                                               "benchmark_oos_sharpe": winner["bh_sharpe"],
                                               "oos_max_drawdown": winner["oos_max_drawdown"],
                                               "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    (RES / "evidence_status.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search", "updated_at": NOW_ISO,
        "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": f"Winner selected on in-sample data by the lead-plateau rule (D9) from the {DATE_TAG} "
                          "quarterly tournament on real-time DRTSCILM vintages and scored on the test window after "
                          "selection; the test window was seen by earlier runs of this pair, and the training and "
                          "test windows are small.",
        "next_step": "Freeze the selected rule and run a confirmation test on future data.", "owner": "evan"},
        indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    (RES / "analyst_suggestions.json").write_text(json.dumps({
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{
            "signal_name": "Small-firm series (DRTSCIS)", "proposed_by": "evan", "source": "ALFRED / Federal Reserve",
            "observation": f"The rule uses an L{winner['lead_value']}q lead on {winner['signal_code']} of the large "
                           "and middle-market series; the small-firm series the pair id names has not been tested.",
            "rationale": "Small-firm credit conditions may lead differently; the survey publishes both on the same "
                         "dates, so a like-for-like test is possible.",
            "possible_use_case": "robustness check", "caveats": "Search-selected on a small quarterly OOS window.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:]}],
        "notes": "Generated with the SLOOS C&I x SPY pair pipeline."}, indent=2) + "\n")


NARRATIVE_SOURCES = ["regime_quartile_returns.csv", "granger_by_lag.csv", "subperiod_sharpe.csv",
                     f"stationarity_tests_{DATE_TAG}.csv", f"structural_break_{PAIR_ID}.json",
                     f"core_models_{DATE_TAG}/correlations.csv", f"core_models_{DATE_TAG}/ccf_prewhitened.csv",
                     f"core_models_{DATE_TAG}/local_projections.csv",
                     f"core_models_{DATE_TAG}/quantile_regression.csv",
                     f"core_models_{DATE_TAG}/quantile_equality_test.json"]


def write_narrative_provenance() -> None:
    """evidence_facts_<tag>.json: the evidence tables the page prose cites (scripts/gate_number_provenance.py)."""
    q = pd.read_csv(RES / "regime_quartile_returns.csv")
    sr = pd.read_csv(RES / f"strategy_returns_{DATE_TAG}.csv")
    oos = sr.loc[sr["sample"] == "OOS", "position"].dropna().to_numpy(float)
    d = np.abs(np.diff(oos))                                   # changes between consecutive test-period quarters
    log = pd.read_csv(RES / "winner_trades_broker_style.csv")
    oos_start = sr.loc[sr["sample"] == "OOS", "date"].iloc[0]
    write_evidence_facts(PAIR_ID, DATE_TAG, sources=NARRATIVE_SOURCES, derived={
        "regime_quartile_ann_return_pct": {r.quartile: round(float(r.mean_return) * PPY * 100, 6)
                                           for r in q.itertuples()},       # the regime chart's return labels
        "n_trade_log_rows": len(log),
        "n_trade_log_rows_test_period": int((log["trade_date"] >= oos_start).sum()),
        "position_change_threshold_pp": POSITION_CHANGE_PP,
        "n_oos_position_changes_gt_threshold": int((d > POSITION_CHANGE_PP / 100).sum()),
        "oos_sum_abs_position_change": round(float(d.sum()), 4),
        "granger_min_p_holm": round(float(pd.read_csv(RES / "granger_by_lag.csv")["p_holm"].min()), 6)})


def main() -> None:
    t0 = time.time()
    for path in (RES, CORE, VALID):
        path.mkdir(parents=True, exist_ok=True)
    df = build_panel()
    df[list(SIGNALS.values())].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    tourn, winner, _ = run_tournament()
    write_evidence(df, tourn, winner)
    write_metadata(winner, time.time() - t0)
    write_narrative_provenance()
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
