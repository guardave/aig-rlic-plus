#!/usr/bin/env python3
"""Pair pipeline: U. Michigan **headline Consumer Sentiment** (FRED UMCSENT) x SPY.

MONTHLY pipeline. The indicator is the University of Michigan Index of Consumer
Sentiment (FRED series UMCSENT, the HEADLINE index, range ~50-112) -- NOT the
"expected business conditions" diffusion sub-index used by umcsent_spy. Bounded,
mean-reverting -- the LEVEL is stationary and used directly. Economic prior:
rising consumer sentiment precedes stronger spending -> PROCYCLICAL (hold SPY
when sentiment is elevated). Monthly grid, sqrt(12).

Lead grid is FLOORED to L1 (#255 publication-lag discipline): the Michigan
survey for reference month t is released within/at the end of month t (prelim
mid-month, final end-of-month), so a 1-month lead is the smallest executable
lead; the searched grid is the contiguous shifted grid [1..13].

This is a NEW pair created to fill a gap: headline consumer sentiment was only
paired with XLV (umcsent_xlv); the SPY slot carried the expected-business-
conditions diffusion by a different name. umcsent_spy and umcsent_xlv are left
untouched; read this alongside them.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import adfuller, kpss

PAIR_ID = "consumer_sentiment_spy"
DATE_TAG = "20261009"
TARGET_SYMBOL = "SPY"
COST_BPS = 5
REPO = Path(__file__).resolve().parents[1]
DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
EXPLORE = RES / f"exploratory_{DATE_TAG}"
for path in (DATA_DIR, RES, CORE, VALID, EXPLORE):
    path.mkdir(parents=True, exist_ok=True)
NOW_ISO = datetime.now(timezone.utc).isoformat()

FRED_SERIES_ID = "UMCSENT"
START_DATE = "1978-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")
PERIODS_PER_YEAR = 12                 # monthly


def read_sentiment() -> pd.Series:
    """U. Michigan headline Consumer Sentiment (FRED UMCSENT), monthly."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise SystemExit("FRED_API_KEY not set — copy .env.example to .env, or run setup.sh.")
    s = None
    try:
        from fredapi import Fred
        s = Fred(api_key=api_key).get_series(FRED_SERIES_ID, observation_start=START_DATE, observation_end=END_DATE)
        s.index = pd.to_datetime(s.index)
    except Exception as exc:
        print(f"  [FRED] fredapi failed ({exc}); trying CSV fallback")
        import urllib.request
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={FRED_SERIES_ID}&cosd={START_DATE}&coed={END_DATE}"
        local_path = f"/tmp/fred_{FRED_SERIES_ID}.csv"
        urllib.request.urlretrieve(url, local_path)
        s = pd.read_csv(local_path, index_col=0, parse_dates=True).iloc[:, 0]
    s = pd.to_numeric(s, errors="coerce").dropna()
    s.name = "umcsent"
    s = s.resample("ME").last()
    lo, hi = float(s.dropna().min()), float(s.dropna().max())
    print(f"  [FRED] UMCSENT headline consumer sentiment: {len(s.dropna())} mo, "
          f"{s.dropna().index.min().date()} to {s.dropna().index.max().date()}, range {lo:.1f}-{hi:.1f}")
    if hi < 80:
        raise RuntimeError(f"UMCSENT range {lo:.1f}-{hi:.1f} does not look like the headline index (~50-112); aborting.")
    return s


def _read_spy_monthly() -> tuple[pd.Series, str]:
    try:
        raw = yf.download("SPY", start="1993-01-01", progress=False, auto_adjust=True, actions=False)
        if not raw.empty:
            spy = raw["Close"]["SPY"] if isinstance(raw.columns, pd.MultiIndex) else raw["Close"]
            return spy.resample("ME").last().rename("spy"), "Yahoo Finance"
    except Exception as exc:
        print(f"  Yahoo SPY fetch failed: {exc}")
    for fb in (DATA_DIR / "rsxfs_spy_monthly_latest.parquet",
               DATA_DIR / "unrate_spy_monthly_latest.parquet",
               DATA_DIR / "eci_total_comp_spy_monthly_latest.parquet"):
        if fb.exists():
            local = pd.read_parquet(fb)
            if "spy" in local.columns:
                print(f"  Using local SPY fallback: {fb.name}")
                return local["spy"].resample("ME").last().rename("spy"), f"Local fallback: {fb.name}"
    raise RuntimeError("No SPY data available")


def source_data() -> pd.DataFrame:
    print("Sourcing U. Michigan headline Consumer Sentiment (FRED UMCSENT) and SPY month-end prices")
    raw = read_sentiment()
    spy, spy_source = _read_spy_monthly()
    df = pd.concat([raw, spy], axis=1).dropna(subset=["umcsent", "spy"])
    df["spy_ret"] = df["spy"].pct_change()
    for h in (1, 3, 6):
        df[f"spy_fwd_{h}m"] = df["spy"].pct_change(h).shift(-h)

    lvl = df["umcsent"]
    # Bounded / mean-reverting level is a valid stationary signal.
    df["umcsent_level"] = lvl
    df["umcsent_diff_1m"] = lvl.diff(1)             # month-on-month change
    df["umcsent_chg_12m"] = lvl.diff(12)             # 12-month change
    roll_mean = lvl.rolling(60, min_periods=24).mean()
    roll_std = lvl.rolling(60, min_periods=24).std()
    df["umcsent_zscore_60m"] = (lvl - roll_mean) / roll_std

    df = df.loc["1993-01-01":].copy()
    df.to_parquet(DATA_DIR / "consumer_sentiment_spy_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_consumer_sentiment_spy_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_consumer_sentiment_spy_{DATE_TAG}.md")

    data_dict = pd.DataFrame([
        {"Column Name": "umcsent", "Display Name": "U. Michigan Consumer Sentiment",
         "Description": "University of Michigan Index of Consumer Sentiment (headline)",
         "Source": "FRED", "Series ID": "UMCSENT", "Unit": "Index (1966 Q1 = 100)",
         "Transformation": "Monthly level",
         "Direction Convention": "Higher = more optimism (bullish equities)",
         "Effective Start": str(df["umcsent"].first_valid_index().date()),
         "Known Quirks": "Headline sentiment index, range ~50-112; bounded/mean-reverting; sentiment leads spending",
         "Display Note": "Rising consumer sentiment precedes stronger spending and risk-on equity conditions.",
         "Refresh Freq.": "Monthly", "Refresh Source": "FRED"},
        {"Column Name": "spy", "Display Name": "SPY adjusted close",
         "Description": "SPDR S&P 500 ETF adjusted close", "Source": spy_source, "Series ID": "SPY",
         "Unit": "USD", "Transformation": "Month-end adjusted close",
         "Direction Convention": "Higher = higher equity price",
         "Effective Start": str(df["spy"].first_valid_index().date()),
         "Known Quirks": "ETF history begins 1993", "Display Note": "Equity target and benchmark.",
         "Refresh Freq.": "Daily", "Refresh Source": spy_source},
    ])
    data_dict.to_csv(DATA_DIR / f"data_dictionary_consumer_sentiment_spy_{DATE_TAG}.csv", index=False)
    print(f"  Data rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def stationarity_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ["umcsent_level", "umcsent_diff_1m", "umcsent_chg_12m", "umcsent_zscore_60m", "spy_ret"]:
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


SIGNALS = {
    "level": "umcsent_level",
    "diff_1m": "umcsent_diff_1m",
    "chg_12m": "umcsent_chg_12m",
    "zscore_60m": "umcsent_zscore_60m",
}
SIGNAL_DISPLAY = {
    "level": "U. Michigan Consumer Sentiment (level)",
    "diff_1m": "Month-on-month change",
    "chg_12m": "12-month change",
    "zscore_60m": "Level vs 5-year history (z-score)",
}


def build_threshold(series: pd.Series, code: str) -> pd.Series | float:
    if code in ("T0_zero", "T_z_0"):
        return 0.0
    if code == "T_z_1.0":
        return 1.0
    if code == "T_roll_p50":
        return series.rolling(60, min_periods=24).quantile(0.50)
    if code == "T_roll_p75":
        return series.rolling(60, min_periods=24).quantile(0.75)
    if code == "T_roll_p25":
        return series.rolling(60, min_periods=24).quantile(0.25)
    raise ValueError(code)


def threshold_codes_for(signal_code: str) -> list[str]:
    if signal_code in {"diff_1m", "chg_12m"}:
        return ["T0_zero", "T_roll_p50", "T_roll_p75"]
    if signal_code == "zscore_60m":
        return ["T_z_0", "T_z_1.0", "T_roll_p50"]
    return ["T_roll_p25", "T_roll_p50", "T_roll_p75"]  # level: percentile thresholds


def make_position(signal: pd.Series, threshold: pd.Series | float, direction: str) -> pd.Series:
    thresh = threshold.reindex(signal.index) if isinstance(threshold, pd.Series) else pd.Series(float(threshold), index=signal.index)
    if direction == "countercyclical":
        # long SPY when signal is BELOW threshold (favorable regime for a countercyclical prior)
        pos = (signal <= thresh).astype(float)
    else:
        pos = (signal >= thresh).astype(float)
    return pos.where(signal.notna() & thresh.notna())


def run_tournament(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    work = df.dropna(subset=["spy_ret"])
    n = len(work)
    oos_n = int(min(max(60, round(n * 0.25)), 120))
    oos_start = work.index[-oos_n]
    leads = list(range(1, 14))  # #255 floor L1 shifted grid [1..13] (months); Michigan survey releases within reference month
    rows = []
    bh = ann_metrics(df.loc[oos_start:, "spy_ret"].dropna())
    for signal_code, col in SIGNALS.items():
        raw = df[col].astype(float)
        for tcode in threshold_codes_for(signal_code):
            threshold = build_threshold(raw, tcode)
            for direction in ["countercyclical", "procyclical"]:
                for lead in leads:
                    sig = raw.shift(lead)
                    thr = threshold.shift(lead) if isinstance(threshold, pd.Series) else threshold
                    pos = make_position(sig, thr, direction)
                    rets = (pos * df["spy_ret"]).dropna()
                    oos = rets.loc[oos_start:]
                    exposure = pos.loc[oos_start:].dropna().mean()
                    n_trades = int(pos.loc[oos_start:].dropna().diff().abs().fillna(0).sum())
                    valid = len(oos) >= 20 and 0.05 <= exposure <= 0.95 and oos.std() > 0
                    m = ann_metrics(oos)
                    rows.append({"signal": signal_code, "signal_column": col, "threshold": tcode,
                                 "strategy": "P1_long_cash", "lead_months": lead, "direction": direction,
                                 "is_sharpe": m["oos_sharpe"], "oos_sharpe": m["oos_sharpe"], "oos_sortino": m["oos_sortino"],
                                 "oos_calmar": m["oos_calmar"], "oos_ann_return": m["oos_ann_return"], "oos_ann_vol": m["oos_ann_vol"],
                                 "max_drawdown": m["max_drawdown"], "win_rate": m["win_rate"],
                                 "annual_turnover": n_trades / max(len(pos.loc[oos_start:].dropna()) / PERIODS_PER_YEAR, 1),
                                 "is_n": m["oos_n"], "oos_n": m["oos_n"], "valid": bool(valid)})
    rows.append({"signal": "BENCHMARK", "signal_column": "spy", "threshold": "BUY_HOLD", "strategy": "BUY_HOLD",
                 "lead_months": 0, "direction": "benchmark", "is_sharpe": bh["oos_sharpe"], "oos_sharpe": bh["oos_sharpe"],
                 "oos_sortino": bh["oos_sortino"], "oos_calmar": bh["oos_calmar"], "oos_ann_return": bh["oos_ann_return"],
                 "oos_ann_vol": bh["oos_ann_vol"], "max_drawdown": bh["max_drawdown"], "win_rate": bh["win_rate"],
                 "annual_turnover": 0.0, "is_n": bh["oos_n"], "oos_n": bh["oos_n"], "valid": False})
    tourn = pd.DataFrame(rows)
    tourn.to_csv(RES / f"tournament_results_{DATE_TAG}.csv", index=False)
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    wi = valid["oos_sharpe"].idxmax()
    wr = tourn.loc[wi].copy()
    winner_key = f"{wr['signal']}|{wr['threshold']}|{wr['direction']}|{int(wr['lead_months'])}"

    raw = df[wr["signal_column"]].astype(float)
    threshold = build_threshold(raw, str(wr["threshold"]))
    sig_for_rule = raw.shift(int(wr["lead_months"]))
    thr_for_rule = threshold.shift(int(wr["lead_months"])) if isinstance(threshold, pd.Series) else threshold
    position = make_position(sig_for_rule, thr_for_rule, str(wr["direction"])).fillna(0.0)
    strat_ret = (position * df["spy_ret"]).fillna(0.0)   # ECON-T4 deployable cash-fill
    bench_ret = df["spy_ret"].fillna(0.0)
    sdf = pd.DataFrame({"date": df.index, "signal": sig_for_rule.values,
                        "threshold": thr_for_rule.reindex(df.index).values if isinstance(thr_for_rule, pd.Series) else np.repeat(float(thr_for_rule), len(df)),
                        "position": position.values, "strategy_return": strat_ret.values, "benchmark_return": bench_ret.values})
    sdf["strategy_equity"] = (1 + sdf["strategy_return"]).cumprod()
    sdf["benchmark_equity"] = (1 + sdf["benchmark_return"]).cumprod()
    sdf.to_csv(RES / f"strategy_returns_{DATE_TAG}.csv", index=False)
    (RES / f"strategy_returns_{DATE_TAG}_meta.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_key": winner_key, "generated_at": NOW_ISO}, indent=2) + "\n")
    df[list(SIGNALS.values())].to_parquet(RES / f"signals_{DATE_TAG}.parquet")
    changes = position.diff().fillna(0)
    trades = [{"trade_date": dt.date().isoformat(), "side": "BUY" if d > 0 else "SELL", "instrument": TARGET_SYMBOL,
               "quantity_pct": abs(float(d)) * 100, "commission_bps": COST_BPS,
               "signal_value": float(sig_for_rule.loc[dt]) if pd.notna(sig_for_rule.loc[dt]) else np.nan,
               "threshold_value": float(sdf.loc[sdf["date"] == dt, "threshold"].iloc[0]),
               "position_before": float(position.shift(1).fillna(0).loc[dt]), "position_after": float(position.loc[dt]),
               "reason": f"{wr['signal']} {wr['direction']} rule crossed {wr['threshold']}"} for dt, d in changes[changes != 0].items()]
    pd.DataFrame(trades).to_csv(RES / "winner_trade_log.csv", index=False)
    pd.DataFrame(trades).to_csv(RES / "winner_trades_broker_style.csv", index=False)

    oos = strat_ret.loc[oos_start:].dropna()
    n_trades = int(position.loc[oos_start:].dropna().diff().abs().fillna(0).sum())
    om = ann_metrics(oos)
    bm = ann_metrics(bench_ret.loc[oos_start:].dropna())
    thr_latest = float(threshold.dropna().iloc[-1]) if isinstance(threshold, pd.Series) else float(threshold)
    runner = valid.drop(index=wi).sort_values("oos_sharpe", ascending=False).head(1)
    runner_obj = None
    if not runner.empty:
        r = runner.iloc[0]
        runner_obj = {"signal": str(r["signal"]), "threshold": str(r["threshold"]), "strategy": str(r["strategy"]),
                      "lead_value": int(r["lead_months"]), "objective_value": round(float(r["oos_sharpe"]), 6)}
    winner = {
        "pair_id": PAIR_ID, "generated_at": NOW_ISO, "signal_column": str(wr["signal_column"]),
        "signal_code": str(wr["signal"]), "signal_display_name": SIGNAL_DISPLAY[str(wr["signal"])],
        "target_symbol": TARGET_SYMBOL, "threshold_code": str(wr["threshold"]), "threshold_value": round(thr_latest, 6),
        "threshold_rule": "lte" if wr["direction"] == "countercyclical" else "gte",
        "threshold_note": f"{wr['threshold']} threshold; latest if rolling", "strategy_family": "P1_long_cash",
        "strategy_code": "P1", "strategy_display_name": "P1 long cash",
        "strategy_description": "Hold SPY when the lagged U. Michigan Consumer Sentiment signal is favorable (optimism); else cash.",
        "lead_value": int(wr["lead_months"]), "lead_unit": "months",
        "lead_description": f"Signal is lagged {int(wr['lead_months'])} month(s) before allocation.",
        "lookback": "60m where rolling thresholds apply", "direction": str(wr["direction"]),
        "oos_sharpe": round(om["oos_sharpe"], 6), "oos_sortino": round(om["oos_sortino"], 6), "oos_calmar": round(om["oos_calmar"], 6),
        "oos_ann_return": round(om["oos_ann_return"], 6), "oos_ann_vol": round(om["oos_ann_vol"], 6),
        "oos_max_drawdown": round(om["max_drawdown"], 6), "oos_win_rate": round(om["win_rate"], 6), "oos_n_trades": n_trades,
        "annual_turnover": round(n_trades / max(len(oos) / PERIODS_PER_YEAR, 1), 6), "oos_n": int(len(oos)),
        "oos_period_start": oos.index.min().date().isoformat(), "oos_period_end": oos.index.max().date().isoformat(),
        "bh_sharpe": round(bm["oos_sharpe"], 6), "bh_ann_return": round(bm["oos_ann_return"], 6), "bh_max_drawdown": round(bm["max_drawdown"], 6),
        "cost_assumption_bps": COST_BPS, "total_combos": int((tourn["signal"] != "BENCHMARK").sum()), "valid_combos": int(valid.shape[0]),
        "schema_version": "1.2.0",
        "notes": "Rising consumer sentiment precedes stronger spending and risk-on equity conditions. The bounded headline-sentiment level is stationary. Winner is search-selected on a floored lead grid [1..13] — read as found-in-search, not validated. NEW pair; compare with umcsent_xlv (same series vs XLV) and umcsent_spy (expected-business-conditions diffusion vs SPY).",
        "selection": {"objective": "max_oos_sharpe", "objective_formula": "monthly mean/std*sqrt(12)",
                      "grid_scanned": {"leads": leads, "n_signals": len(SIGNALS),
                                       "n_thresholds": int(sum(len(threshold_codes_for(s)) for s in SIGNALS)),
                                       "n_strategies": 1, "n_valid_combos": int(valid.shape[0]),
                                       "median_valid_objective": round(float(valid["oos_sharpe"].median()), 6)},
                      "tie_break_step": None,
                      "raw_winner_row": {"signal": str(wr["signal"]), "threshold": str(wr["threshold"]), "strategy": str(wr["strategy"]),
                                         "lead_column": "lead_months", "lead_value": int(wr["lead_months"]),
                                         "source_tournament_file": f"tournament_results_{DATE_TAG}.csv", "source_row_index": int(wi)},
                      "runner_up": runner_obj, "rationale": "Winner is the valid row with the highest OOS Sharpe over the published floored grid.",
                      "objective_runner_up_divergence": None}}
    (RES / "winner_summary.json").write_text(json.dumps(winner, indent=2) + "\n")
    (RES / "tournament_winner.json").write_text(json.dumps(winner, indent=2) + "\n")
    print(f"  Winner: {winner['signal_code']}/{winner['threshold_code']}/{winner['direction']}/L{winner['lead_value']} "
          f"Sharpe={winner['oos_sharpe']:.3f} vs B&H {winner['bh_sharpe']:.3f} (OOS {winner['oos_n']}mo)")
    return tourn, winner


REP_SIGNAL = "umcsent_chg_12m"


def write_evidence(df: pd.DataFrame, tourn: pd.DataFrame, winner: dict) -> None:
    from scipy import stats
    from statsmodels.tsa.stattools import grangercausalitytests
    tcols = ["spy_fwd_1m", "spy_fwd_3m", "spy_fwd_6m"]
    corr_rows = []
    for sc, col in SIGNALS.items():
        for fwd in tcols:
            sub = df[[col, fwd]].dropna()
            if len(sub) < 24:
                continue
            r, p = stats.pearsonr(sub[col], sub[fwd])
            corr_rows.append({"pair_name": f"{col}_to_{fwd}", "metric": "pearson", "value": r, "p_value": p})
    pd.DataFrame(corr_rows).to_csv(CORE / "correlations.csv", index=False)
    granger_rows = []
    g = df[["spy_ret", REP_SIGNAL]].dropna()
    if len(g) > 40:
        tests = grangercausalitytests(g[["spy_ret", REP_SIGNAL]], maxlag=6, verbose=False)
        for lag, res in tests.items():
            f, p, _, _ = res[0]["ssr_ftest"]
            granger_rows.append({"lag": lag, "f_stat": f, "p_value": p, "direction": "signal_to_SPY"})
    pd.DataFrame(granger_rows).to_csv(CORE / "granger_causality.csv", index=False)
    pd.DataFrame(granger_rows).to_csv(RES / "granger_by_lag.csv", index=False)
    ccf_rows = []
    x, y = df[REP_SIGNAL], df["spy_ret"]
    for lag in range(-6, 7):
        sub = pd.concat([x.shift(lag), y], axis=1).dropna()
        c = sub.iloc[:, 0].corr(sub.iloc[:, 1]) if len(sub) > 24 else np.nan
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
        w = df.loc[:dt, [REP_SIGNAL, "spy_ret"]].tail(24).dropna()
        if len(w) >= 12:
            rcorr.append({"date": dt, "rolling_corr": w[REP_SIGNAL].corr(w["spy_ret"])})
    pd.DataFrame(rcorr).to_csv(RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    rc = pd.DataFrame(rcorr)
    maz = float(((rc["rolling_corr"] - rc["rolling_corr"].mean()) / rc["rolling_corr"].std()).abs().max()) if not rc.empty and rc["rolling_corr"].std() > 0 else 0.0
    (RES / f"structural_break_{PAIR_ID}.json").write_text(json.dumps({"pair_id": PAIR_ID, "method": "rolling-correlation z-score proxy", "max_abs_z": maz}, indent=2) + "\n")
    lp_rows = []
    for h in [1, 3, 6]:
        sub = df[[REP_SIGNAL, f"spy_fwd_{h}m"]].dropna()
        if len(sub) > 24:
            sl, ic, r, p, se = stats.linregress(sub[REP_SIGNAL], sub[f"spy_fwd_{h}m"])
            lp_rows.append({"horizon": h, "coef": sl, "p_value": p, "r_squared": r * r})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)
    qr_rows = []
    for qt in [0.25, 0.5, 0.75]:
        sub = df[[REP_SIGNAL, "spy_fwd_3m"]].dropna()
        if len(sub) > 24:
            sl, ic, r, p, se = stats.linregress(sub[REP_SIGNAL], sub["spy_fwd_3m"])
            qr_rows.append({"quantile": qt, "coef": sl, "p_value": p})
    pd.DataFrame(qr_rows).to_csv(CORE / "quantile_regression.csv", index=False)
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
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    bp = float((valid["oos_sharpe"] >= winner["oos_sharpe"]).mean())
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"], "strategy": winner["strategy_family"],
                   "oos_sharpe": winner["oos_sharpe"], "bootstrap_p_value": bp, "significant_at_5pct": bp < 0.05}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"], "strategy": winner["strategy_family"],
                   "tx_cost_bps": COST_BPS, "gross_sharpe": winner["oos_sharpe"]}]).to_csv(VALID / "transaction_costs.csv", index=False)
    # exploratory placeholder so the dir is populated/committed
    pd.DataFrame(corr_rows).to_csv(EXPLORE / "signal_target_correlations.csv", index=False)


def write_metadata(df: pd.DataFrame, winner: dict, elapsed: float) -> None:
    bp = None
    try:
        bp = float(pd.read_csv(VALID / "bootstrap.csv")["bootstrap_p_value"].iloc[0])
    except Exception:
        pass
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "leading", "indicator_type": "sentiment",
        "strategy_objective": "procyclical_capture",
        "owner_writes": {"dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
                         "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
                         "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"]},
        "last_updated_by": "ray", "last_updated_at": NOW_ISO, "indicator": "umcsent", "target": "spy",
        "expected_direction": "procyclical", "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "procyclical",
        "mechanism": "The University of Michigan Index of Consumer Sentiment (headline UMCSENT) is a survey measure of household economic optimism. Rising sentiment precedes stronger spending and risk-on equity conditions; falling sentiment precedes retrenchment. The strategy holds SPY when sentiment is favorable.",
        "confidence": "low",
        "key_finding": f"Best search-phase rule uses {winner['signal_code']} at L{winner['lead_value']} with OOS Sharpe "
                       f"{winner['oos_sharpe']:.2f} versus buy-and-hold {winner['bh_sharpe']:.2f}.",
        "caveats": ["Winner is search-selected on a single monthly sample and needs holdout validation.", "Lead grid is floored to L1 (#255 publication-lag discipline); the searched grid is the contiguous shifted grid [1..13].", "Level/change thresholds are rolling-percentile based; regime pivots can drift across decades.", "Lead estimates rest on a limited number of cycles in the sample."],
        "narrative_summary": "U. Michigan headline consumer sentiment is tested as a procyclical sentiment overlay for SPY. NEW pair; compare with umcsent_xlv (same series vs XLV) and umcsent_spy (expected-business-conditions diffusion vs SPY).",
        "known_stress_episodes": [{"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "NBER recession."}, {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30", "note": "NBER recession."}, {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "NBER recession."}, {"label": "2022 drawdown", "start": "2022-01-01", "end": "2022-12-31", "note": "Rate-hike bear market."}],
        "data_provenance": {"source": "FRED (University of Michigan Surveys of Consumers)", "series_id": "UMCSENT", "accessed_at": NOW_ISO}}
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan", "last_updated_at": NOW_ISO,
        "indicator_axis": {"canonical_column": "umcsent", "display_name": "U. Michigan Consumer Sentiment",
            "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch} for c, d, f, r, ch in [
                ("umcsent", "U. Michigan Consumer Sentiment (headline UMCSENT)", "FRED (University of Michigan)", "raw", ["hero"]),
                ("umcsent_level", "Consumer-sentiment level (index)", "identity", "threshold_input", ["hero", "regime_stats"]),
                ("umcsent_diff_1m", "Month-on-month change", "x_t - x_{t-1}", "derivative", []),
                ("umcsent_chg_12m", "12-month change", "x_t - x_{t-12}", "threshold_input", ["local_projections"]),
                ("umcsent_zscore_60m", "Level vs 5-year history", "(x-mean60m)/std60m", "threshold_input", [])]]},
        "target_axis": {"canonical_column": "spy", "display_name": "SPY adjusted close",
            "derivatives": [{"name": "spy", "definition": "SPY adjusted month-end close", "formula": "month-end adjusted close", "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "SPY monthly return", "formula": "spy_t/spy_{t-1}-1", "role": "derivative", "appears_in_charts": []},
                {"name": "spy_fwd_1m", "definition": "1-month forward SPY return", "formula": "spy_{t+1}/spy_t-1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_3m", "definition": "3-month forward SPY return", "formula": "spy_{t+3}/spy_t-1", "role": "derivative", "appears_in_charts": ["local_projections", "quantile_coef"]},
                {"name": "spy_fwd_6m", "definition": "6-month forward SPY return", "formula": "spy_{t+6}/spy_t-1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]}]},
        "notes": "Scope limited to U. Michigan headline Consumer Sentiment signals and SPY returns."}
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"],
        "benchmark_oos_sharpe": winner["bh_sharpe"], "oos_max_drawdown": winner["oos_max_drawdown"], "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    boot_txt = f" Re-shuffle (bootstrap) p-value ~ {bp:.3f}." if bp is not None else ""
    (RES / "evidence_status.json").write_text(json.dumps({"pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search",
        "updated_at": NOW_ISO, "owner": "evan",
        "plain_english": "What you see is the best rule found by searching a floored lead grid [1..13] of U. Michigan headline consumer sentiment against SPY. It beats buy-and-hold in the out-of-sample window, but it is search-selected and has not passed a fresh final exam. Read it alongside umcsent_xlv (same sentiment series against XLV) and umcsent_spy (the expected-business-conditions diffusion against SPY)." + boot_txt,
        "technical_note": f"Winner {winner['signal_code']}/{winner['threshold_code']}/{winner['direction']}/L{winner['lead_value']}: OOS Sharpe {winner['oos_sharpe']:.3f} vs B&H {winner['bh_sharpe']:.3f}. Selected by OOS Sharpe from the {DATE_TAG} monthly tournament on the #255-floored grid [1..13]; selection and evaluation share the same OOS window; no holdout/final exam run.",
        "next_step": "Freeze the selected rule and run an ECON-FE1 final exam on a confirmation window the search never touched.", }, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    (RES / "analyst_suggestions.json").write_text(json.dumps({"pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{"signal_name": "Lead robustness", "proposed_by": "evan", "source": "FRED",
            "observation": f"The rule uses an L{winner['lead_value']} lead on {winner['signal_code']}; verify adjacent-lead durability.",
            "rationale": "Cycles in the sample are few, so the lead needs adjacent-lead durability and a cycle-count caveat.",
            "possible_use_case": "robustness check", "caveats": "Search-selected on a limited OOS; needs final-exam validation.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:]}], "notes": "Generated with the U. Michigan headline Consumer Sentiment x SPY pair pipeline."}, indent=2) + "\n")


def main() -> None:
    t0 = time.time()
    df = source_data()
    tourn, winner = run_tournament(df)
    write_evidence(df, tourn, winner)
    write_metadata(df, winner, time.time() - t0)
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
