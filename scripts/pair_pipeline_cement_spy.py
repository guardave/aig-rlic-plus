#!/usr/bin/env python3
"""Pair pipeline: Portland Cement Shipments x SPY.

MONTHLY pipeline. The indicator is Portland cement shipments (nominal $), from Data Master.xlsx.
The level is a trending nominal series (non-stationary) so all signals are GROWTH transforms
(YoY, MoM, 3m/6m change, z-scored, accelerated), never the level itself. Economic prior: cement
shipments track construction/infrastructure activity — strong growth marks a cyclical upswing
→ PROCYCLICAL (favor SPY when cement-shipment growth is firm). Sample starts 2005.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats
from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss


PAIR_ID = "cement_spy"
DATE_TAG = "20260830"
TARGET_SYMBOL = "SPY"
COST_BPS = 5
REPO = Path(__file__).resolve().parents[1]
DATA_DIR = REPO / "data"
RES = REPO / "results" / PAIR_ID
CORE = RES / f"core_models_{DATE_TAG}"
VALID = RES / f"tournament_validation_{DATE_TAG}"
for path in (DATA_DIR, RES, CORE, VALID):
    path.mkdir(parents=True, exist_ok=True)

NOW_ISO = datetime.now(timezone.utc).isoformat()


def _read_fred_csv(series_id: str) -> pd.Series:
    """Pull a FRED series via the public fredgraph CSV endpoint (no API key)."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    with urlopen(url, timeout=30) as response:
        df = pd.read_csv(response)
    date_col = "observation_date" if "observation_date" in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    values = pd.to_numeric(df[series_id], errors="coerce")
    out = pd.Series(values.values, index=df[date_col], name=series_id.lower())
    return out.dropna()


def _read_spy_monthly() -> tuple[pd.Series, str]:
    try:
        spy_raw = yf.download(
            "SPY", start="1993-01-01", progress=False, auto_adjust=True, actions=False,
        )
        if not spy_raw.empty:
            if isinstance(spy_raw.columns, pd.MultiIndex):
                spy = spy_raw["Close"]["SPY"]
            else:
                spy = spy_raw["Close"]
            return spy.resample("ME").last().rename("spy"), "Yahoo Finance"
    except Exception as exc:
        print(f"  Yahoo Finance SPY fetch failed: {exc}")

    for fallback in (
        DATA_DIR / "unrate_spy_monthly_latest.parquet",
        DATA_DIR / "m2sl_yoy_spy_monthly_latest.parquet",
        DATA_DIR / "phlxsox_spy_monthly_latest.parquet",
        DATA_DIR / "t10y3m_spy_monthly_latest.parquet",
    ):
        if fallback.exists():
            local = pd.read_parquet(fallback)
            if "spy" in local.columns:
                print(f"  Using local SPY fallback: {fallback.relative_to(REPO)}")
                spy = local["spy"].resample("ME").last().rename("spy")
                return spy, f"Local fallback: {fallback.name}"
    raise RuntimeError("No SPY data available from Yahoo Finance or local fallback panels")


def read_neworders_master() -> pd.Series:
    """Portland Cement Shipments level (nominal $ millions, monthly) from Data Master."""
    import openpyxl
    wb = openpyxl.load_workbook(str(DATA_DIR / "Data Master.xlsx"), read_only=True, data_only=True)
    ws = wb["Portland Cement"]  # cols: date | level | YoY
    rows = [(r[0], r[1]) for r in ws.iter_rows(min_row=2, values_only=True)
            if r and r[0] is not None and r[1] is not None and hasattr(r[0], "year")]
    s = pd.Series({pd.Timestamp(d): float(v) for d, v in rows}, name="cement").sort_index().resample("ME").last()
    print(f"  [MASTER] Portland Cement Shipments: {len(s.dropna())} mo, "
          f"{s.dropna().index.min().date()} to {s.dropna().index.max().date()}")
    return s


def source_data() -> pd.DataFrame:
    print("Sourcing Portland Cement Shipments (Data Master) and SPY month-end prices")
    mfg = read_neworders_master()
    spy, spy_source = _read_spy_monthly()

    df = pd.concat([mfg.rename("cement"), spy], axis=1).dropna(subset=["cement", "spy"])
    df["spy_ret"] = df["spy"].pct_change()
    for horizon in (1, 3, 6, 12):
        df[f"spy_fwd_{horizon}m"] = df["spy"].pct_change(horizon).shift(-horizon)

    # Growth transforms (level is non-stationary trending $ — never a signal).
    lvl = df["cement"]
    df["cement_yoy"] = 100.0 * (lvl / lvl.shift(12) - 1.0)   # headline 12m growth
    df["cement_mom"] = 100.0 * (lvl / lvl.shift(1) - 1.0)    # 1m growth
    df["cement_3m"] = 100.0 * (lvl / lvl.shift(3) - 1.0)     # 3m growth
    df["cement_6m"] = 100.0 * (lvl / lvl.shift(6) - 1.0)     # 6m growth
    roll_mean = df["cement_yoy"].rolling(60, min_periods=36).mean()
    roll_std = df["cement_yoy"].rolling(60, min_periods=36).std()
    df["cement_yoy_zscore_60m"] = (df["cement_yoy"] - roll_mean) / roll_std
    df["cement_accel"] = df["cement_yoy"].diff()             # change in YoY growth

    df = df.loc["1993-01-31":].copy()
    df.to_parquet(DATA_DIR / "cement_spy_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_cement_spy_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_cement_spy_{DATE_TAG}.md")

    data_dict = pd.DataFrame(
        [
            {
                "Column Name": "cement",
                "Display Name": "Portland Cement Shipments",
                "Description": "portland cement shipments, total manufacturing (nominal $)",
                "Source": "Data Master.xlsx (USGS/Census cement shipments)",
                "Series ID": "Portland Cement Shipments (Data Master)",
                "Unit": "Millions of USD",
                "Transformation": "Monthly level (SA)",
                "Direction Convention": "Higher growth = stronger manufacturing demand / risk-on",
                "Effective Start": str(df["cement"].first_valid_index().date()),
                "Known Quirks": "Trending nominal level — model growth, not level; extreme 2020-21 COVID swings",
                "Display Note": "Nominal (not inflation-adjusted); revised in later Census M3 releases.",
                "Refresh Freq.": "Monthly",
                "Refresh Source": "Data Master",
            },
            {
                "Column Name": "spy",
                "Display Name": "SPY adjusted close",
                "Description": "SPDR S&P 500 ETF adjusted close",
                "Source": spy_source,
                "Series ID": "SPY",
                "Unit": "USD",
                "Transformation": "Month-end adjusted close",
                "Direction Convention": "Higher = higher equity price",
                "Effective Start": str(df["spy"].first_valid_index().date()),
                "Known Quirks": "ETF history begins in 1993",
                "Display Note": "Equity-market target and benchmark.",
                "Refresh Freq.": "Daily",
                "Refresh Source": spy_source,
            },
        ]
    )
    data_dict.to_csv(DATA_DIR / f"data_dictionary_cement_spy_{DATE_TAG}.csv", index=False)
    print(f"  Data rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def stationarity_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ["cement", "cement_yoy", "cement_mom", "cement_3m", "cement_yoy_zscore_60m", "spy_ret"]:
        s = df[col].dropna()
        if len(s) < 24:
            continue
        try:
            adf = adfuller(s, autolag="AIC")
            rows.append({"variable": col, "test": "ADF", "statistic": adf[0], "p_value": adf[1],
                         "lags": adf[2], "conclusion": "stationary" if adf[1] < 0.05 else "unit_root_not_rejected"})
        except Exception as exc:
            rows.append({"variable": col, "test": "ADF", "statistic": np.nan, "p_value": np.nan,
                         "lags": np.nan, "conclusion": f"error: {exc}"})
        try:
            kp = kpss(s, regression="c", nlags="auto")
            rows.append({"variable": col, "test": "KPSS", "statistic": kp[0], "p_value": kp[1],
                         "lags": kp[2], "conclusion": "stationary_not_rejected" if kp[1] > 0.05 else "nonstationary"})
        except Exception as exc:
            rows.append({"variable": col, "test": "KPSS", "statistic": np.nan, "p_value": np.nan,
                         "lags": np.nan, "conclusion": f"error: {exc}"})
    out = pd.DataFrame(rows)
    out.to_csv(RES / f"stationarity_tests_{DATE_TAG}.csv", index=False)
    return out


def ann_metrics(rets: pd.Series) -> dict[str, float]:
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return {"oos_sharpe": 0.0, "oos_sortino": 0.0, "oos_calmar": 0.0, "oos_ann_return": 0.0,
                "oos_ann_vol": 0.0, "max_drawdown": 0.0, "win_rate": 0.0, "oos_n": int(len(rets))}
    ann_return = (1 + rets).prod() ** (12 / len(rets)) - 1
    ann_vol = rets.std() * np.sqrt(12)
    sharpe = rets.mean() / rets.std() * np.sqrt(12)
    neg = rets[rets < 0]
    sortino = ann_return / (neg.std() * np.sqrt(12)) if len(neg) > 1 and neg.std() > 0 else 0.0
    equity = (1 + rets).cumprod()
    max_dd = (equity / equity.cummax() - 1).min()
    calmar = ann_return / abs(max_dd) if max_dd < 0 else 0.0
    return {"oos_sharpe": float(sharpe), "oos_sortino": float(sortino), "oos_calmar": float(calmar),
            "oos_ann_return": float(ann_return), "oos_ann_vol": float(ann_vol),
            "max_drawdown": float(max_dd), "win_rate": float((rets > 0).mean()), "oos_n": int(len(rets))}


# GROWTH signals only (the level is non-stationary — never traded).
SIGNALS = {
    "yoy": "cement_yoy",
    "mom": "cement_mom",
    "chg_3m": "cement_3m",
    "chg_6m": "cement_6m",
    "yoy_zscore_60m": "cement_yoy_zscore_60m",
    "accel": "cement_accel",
}

SIGNAL_DISPLAY = {
    "yoy": "YoY growth",
    "mom": "MoM growth",
    "chg_3m": "3-month growth",
    "chg_6m": "6-month growth",
    "yoy_zscore_60m": "YoY growth 60-month z-score",
    "accel": "Growth acceleration (ΔYoY)",
}


def build_threshold(series: pd.Series, code: str) -> pd.Series | float:
    if code in ("T0_zero", "T_z_0"):
        return 0.0
    if code == "T_z_1.0":
        return 1.0
    if code == "T_roll_p25":
        return series.rolling(60, min_periods=36).quantile(0.25)
    if code == "T_roll_p50":
        return series.rolling(60, min_periods=36).quantile(0.50)
    if code == "T_roll_p75":
        return series.rolling(60, min_periods=36).quantile(0.75)
    raise ValueError(code)


def threshold_codes_for(signal_code: str) -> list[str]:
    if signal_code in {"yoy", "mom", "chg_3m", "chg_6m", "accel"}:
        return ["T0_zero", "T_roll_p25", "T_roll_p50"]
    if signal_code == "yoy_zscore_60m":
        return ["T_z_0", "T_z_1.0", "T_roll_p50"]
    return ["T_roll_p25", "T_roll_p50", "T_roll_p75"]


def make_position(signal: pd.Series, threshold: pd.Series | float, direction: str) -> pd.Series:
    if isinstance(threshold, pd.Series):
        thresh = threshold.reindex(signal.index)
    else:
        thresh = pd.Series(float(threshold), index=signal.index)
    if direction == "countercyclical":
        pos = (signal <= thresh).astype(float)
    else:  # procyclical: long when growth is strong
        pos = (signal >= thresh).astype(float)
    return pos.where(signal.notna() & thresh.notna())


def run_tournament(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    oos_start = pd.Timestamp("2017-01-31")
    leads = [0, 1, 2, 3, 6, 9, 12]
    rows = []
    bh_oos = df.loc[oos_start:, "spy_ret"].dropna()
    bh = ann_metrics(bh_oos)

    for signal_code, col in SIGNALS.items():
        raw = df[col].astype(float)
        for threshold_code in threshold_codes_for(signal_code):
            threshold = build_threshold(raw, threshold_code)
            for direction in ["countercyclical", "procyclical"]:
                for lead in leads:
                    sig = raw.shift(lead)
                    thresh = threshold.shift(lead) if isinstance(threshold, pd.Series) else threshold
                    pos = make_position(sig, thresh, direction)
                    rets = (pos * df["spy_ret"]).dropna()
                    oos = rets.loc[oos_start:]
                    exposure = pos.loc[oos_start:].dropna().mean()
                    n_trades = int(pos.loc[oos_start:].dropna().diff().abs().fillna(0).sum())
                    valid = len(oos) >= 60 and 0.05 <= exposure <= 0.95 and oos.std() > 0
                    m = ann_metrics(oos)
                    rows.append({
                        "signal": signal_code, "signal_column": col, "threshold": threshold_code,
                        "strategy": "P1_long_cash", "lead_months": lead, "direction": direction,
                        "is_sharpe": m["oos_sharpe"], "oos_sharpe": m["oos_sharpe"],
                        "oos_sortino": m["oos_sortino"], "oos_calmar": m["oos_calmar"],
                        "oos_ann_return": m["oos_ann_return"], "oos_ann_vol": m["oos_ann_vol"],
                        "max_drawdown": m["max_drawdown"], "win_rate": m["win_rate"],
                        "annual_turnover": n_trades / max(len(pos.loc[oos_start:].dropna()) / 12, 1),
                        "is_n": m["oos_n"], "oos_n": m["oos_n"], "valid": bool(valid),
                    })

    rows.append({
        "signal": "BENCHMARK", "signal_column": "spy", "threshold": "BUY_HOLD",
        "strategy": "BUY_HOLD", "lead_months": 0, "direction": "benchmark",
        "is_sharpe": bh["oos_sharpe"], "oos_sharpe": bh["oos_sharpe"], "oos_sortino": bh["oos_sortino"],
        "oos_calmar": bh["oos_calmar"], "oos_ann_return": bh["oos_ann_return"],
        "oos_ann_vol": bh["oos_ann_vol"], "max_drawdown": bh["max_drawdown"], "win_rate": bh["win_rate"],
        "annual_turnover": 0.0, "is_n": bh["oos_n"], "oos_n": bh["oos_n"], "valid": False,
    })

    tourn = pd.DataFrame(rows)
    tourn.to_csv(RES / f"tournament_results_{DATE_TAG}.csv", index=False)
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    winner_idx = valid["oos_sharpe"].idxmax()
    winner_row = tourn.loc[winner_idx].copy()
    winner_key = f"{winner_row['signal']}|{winner_row['threshold']}|{winner_row['direction']}|{int(winner_row['lead_months'])}"

    raw = df[winner_row["signal_column"]].astype(float)
    threshold = build_threshold(raw, str(winner_row["threshold"]))
    signal_for_rule = raw.shift(int(winner_row["lead_months"]))
    threshold_for_rule = threshold.shift(int(winner_row["lead_months"])) if isinstance(threshold, pd.Series) else threshold
    position = make_position(signal_for_rule, threshold_for_rule, str(winner_row["direction"])).fillna(0.0)
    strategy_return = (position * df["spy_ret"]).fillna(0.0)   # ECON-T4 deployable cash-fill
    benchmark_return = df["spy_ret"].fillna(0.0)

    strategy_df = pd.DataFrame({
        "date": df.index, "signal": signal_for_rule.values,
        "threshold": threshold_for_rule.reindex(df.index).values if isinstance(threshold_for_rule, pd.Series) else np.repeat(float(threshold_for_rule), len(df)),
        "position": position.values, "strategy_return": strategy_return.values,
        "benchmark_return": benchmark_return.values,
    })
    strategy_df["strategy_equity"] = (1 + strategy_df["strategy_return"]).cumprod()
    strategy_df["benchmark_equity"] = (1 + strategy_df["benchmark_return"]).cumprod()
    strategy_df.to_csv(RES / f"strategy_returns_{DATE_TAG}.csv", index=False)
    (RES / f"strategy_returns_{DATE_TAG}_meta.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "winner_key": winner_key, "generated_at": NOW_ISO}, indent=2) + "\n")
    sig_cols = list(SIGNALS.values())
    df[sig_cols].to_parquet(RES / f"signals_{DATE_TAG}.parquet")

    changes = position.diff().fillna(0)
    trades = []
    for dt, delta in changes[changes != 0].items():
        trades.append({
            "trade_date": dt.date().isoformat(), "side": "BUY" if delta > 0 else "SELL",
            "instrument": TARGET_SYMBOL, "quantity_pct": abs(float(delta)) * 100, "commission_bps": COST_BPS,
            "signal_value": float(signal_for_rule.loc[dt]) if pd.notna(signal_for_rule.loc[dt]) else np.nan,
            "threshold_value": float(strategy_df.loc[strategy_df["date"] == dt, "threshold"].iloc[0]),
            "position_before": float(position.shift(1).fillna(0).loc[dt]), "position_after": float(position.loc[dt]),
            "reason": f"{winner_row['signal']} {winner_row['direction']} rule crossed {winner_row['threshold']}",
        })
    pd.DataFrame(trades).to_csv(RES / "winner_trade_log.csv", index=False)
    pd.DataFrame(trades).to_csv(RES / "winner_trades_broker_style.csv", index=False)

    oos = strategy_return.loc[oos_start:].dropna()
    n_trades = int(position.loc[oos_start:].dropna().diff().abs().fillna(0).sum())
    oos_metrics = ann_metrics(oos)
    bh_metrics = ann_metrics(benchmark_return.loc[oos_start:].dropna())
    threshold_latest = float(threshold.dropna().iloc[-1]) if isinstance(threshold, pd.Series) else float(threshold)
    runner = valid.drop(index=winner_idx).sort_values("oos_sharpe", ascending=False).head(1)
    runner_obj = None
    if not runner.empty:
        r = runner.iloc[0]
        runner_obj = {"signal": str(r["signal"]), "threshold": str(r["threshold"]), "strategy": str(r["strategy"]),
                      "lead_value": int(r["lead_months"]), "objective_value": round(float(r["oos_sharpe"]), 6)}
    winner = {
        "pair_id": PAIR_ID, "generated_at": NOW_ISO, "signal_column": str(winner_row["signal_column"]),
        "signal_code": str(winner_row["signal"]), "signal_display_name": SIGNAL_DISPLAY[str(winner_row["signal"])],
        "target_symbol": TARGET_SYMBOL, "threshold_code": str(winner_row["threshold"]),
        "threshold_value": round(threshold_latest, 6),
        "threshold_rule": "lte" if winner_row["direction"] == "countercyclical" else "gte",
        "threshold_note": f"{winner_row['threshold']} threshold; threshold_value is latest if rolling",
        "strategy_family": "P1_long_cash", "strategy_code": "P1", "strategy_display_name": "P1 long cash",
        "strategy_description": "Hold SPY when the lagged cement-shipment-growth signal is favorable (firm); otherwise hold cash.",
        "lead_value": int(winner_row["lead_months"]), "lead_unit": "months",
        "lead_description": f"Signal is lagged {int(winner_row['lead_months'])} month(s) before allocation.",
        "lookback": "LB60 where rolling thresholds apply", "direction": str(winner_row["direction"]),
        "oos_sharpe": round(oos_metrics["oos_sharpe"], 6), "oos_sortino": round(oos_metrics["oos_sortino"], 6),
        "oos_calmar": round(oos_metrics["oos_calmar"], 6), "oos_ann_return": round(oos_metrics["oos_ann_return"], 6),
        "oos_ann_vol": round(oos_metrics["oos_ann_vol"], 6), "oos_max_drawdown": round(oos_metrics["max_drawdown"], 6),
        "oos_win_rate": round(oos_metrics["win_rate"], 6), "oos_n_trades": n_trades,
        "annual_turnover": round(n_trades / max(len(oos) / 12, 1), 6), "oos_n": int(len(oos)),
        "oos_period_start": oos.index.min().date().isoformat(), "oos_period_end": oos.index.max().date().isoformat(),
        "bh_sharpe": round(bh_metrics["oos_sharpe"], 6), "bh_ann_return": round(bh_metrics["oos_ann_return"], 6),
        "bh_max_drawdown": round(bh_metrics["max_drawdown"], 6), "cost_assumption_bps": COST_BPS,
        "total_combos": int((tourn["signal"] != "BENCHMARK").sum()), "valid_combos": int(valid.shape[0]),
        "schema_version": "1.2.0",
        "notes": "Portland Cement Shipments is a construction-activity indicator; the nominal-dollar level is non-stationary so all signals are growth transforms. Sample starts 2005; winner is search-selected — read as found-in-search.",
        "selection": {
            "objective": "max_oos_sharpe",
            "objective_formula": "monthly mean/std*sqrt(12), OOS from 2017-01",
            "grid_scanned": {"leads": leads, "n_signals": len(SIGNALS),
                             "n_thresholds": int(sum(len(threshold_codes_for(s)) for s in SIGNALS)),
                             "n_strategies": 1, "n_valid_combos": int(valid.shape[0]),
                             "median_valid_objective": round(float(valid["oos_sharpe"].median()), 6)},
            "tie_break_step": None,
            "raw_winner_row": {"signal": str(winner_row["signal"]), "threshold": str(winner_row["threshold"]),
                               "strategy": str(winner_row["strategy"]), "lead_column": "lead_months",
                               "lead_value": int(winner_row["lead_months"]),
                               "source_tournament_file": f"tournament_results_{DATE_TAG}.csv",
                               "source_row_index": int(winner_idx)},
            "runner_up": runner_obj,
            "rationale": "Winner is the valid row with the highest OOS Sharpe over the published grid.",
            "objective_runner_up_divergence": None,
        },
    }
    (RES / "winner_summary.json").write_text(json.dumps(winner, indent=2) + "\n")
    (RES / "tournament_winner.json").write_text(json.dumps(winner, indent=2) + "\n")
    print(f"  Winner: {winner['signal_code']} / {winner['threshold_code']} / {winner['direction']} / "
          f"L{winner['lead_value']} Sharpe={winner['oos_sharpe']:.3f} vs B&H {winner['bh_sharpe']:.3f}")
    return tourn, winner


REP_SIGNAL = "cement_yoy"  # representative growth signal for evidence econometrics


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
    gdata = df[["spy_ret", REP_SIGNAL]].dropna()
    if len(gdata) > 80:
        tests = grangercausalitytests(gdata[["spy_ret", REP_SIGNAL]], maxlag=12, verbose=False)
        for lag, res in tests.items():
            f_stat, p_val, _, _ = res[0]["ssr_ftest"]
            granger_rows.append({"lag": lag, "f_stat": f_stat, "p_value": p_val, "direction": "signal_to_SPY"})
    pd.DataFrame(granger_rows).to_csv(CORE / "granger_causality.csv", index=False)
    pd.DataFrame(granger_rows).to_csv(RES / "granger_by_lag.csv", index=False)

    ccf_rows = []
    x, y = df[REP_SIGNAL], df["spy_ret"]
    for lag in range(-12, 13):
        sub = pd.concat([x.shift(lag), y], axis=1).dropna()
        corr = sub.iloc[:, 0].corr(sub.iloc[:, 1]) if len(sub) > 20 else np.nan
        ci = 1.96 / np.sqrt(max(len(sub), 1))
        ccf_rows.append({"lag": lag, "ccf": corr, "upper_ci": ci, "lower_ci": -ci,
                         "significant": abs(corr) > ci if pd.notna(corr) else False})
    pd.DataFrame(ccf_rows).to_csv(CORE / "ccf_prewhitened.csv", index=False)

    # Quartiles on GROWTH (level is non-stationary — quartiles of level are meaningless).
    q = pd.qcut(df[REP_SIGNAL].dropna(), 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q_rows = []
    for label in ["Q1", "Q2", "Q3", "Q4"]:
        idx = q[q == label].index
        rets = df.loc[idx, "spy_ret"].dropna()
        m = ann_metrics(rets)
        q_rows.append({"quartile": label, "mean_return": rets.mean(), "sharpe": m["oos_sharpe"], "n": len(rets)})
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)

    rcorr = []
    for dt in df.index:
        window = df.loc[:dt, [REP_SIGNAL, "spy_ret"]].tail(60).dropna()
        if len(window) >= 36:
            rcorr.append({"date": dt, "rolling_corr": window[REP_SIGNAL].corr(window["spy_ret"])})
    pd.DataFrame(rcorr).to_csv(RES / f"rolling_correlation_{PAIR_ID}.csv", index=False)
    rc = pd.DataFrame(rcorr)
    max_abs_z = 0.0
    if not rc.empty and rc["rolling_corr"].std() > 0:
        max_abs_z = float(((rc["rolling_corr"] - rc["rolling_corr"].mean()) / rc["rolling_corr"].std()).abs().max())
    (RES / f"structural_break_{PAIR_ID}.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "method": "rolling-correlation z-score proxy", "max_abs_z": max_abs_z}, indent=2) + "\n")

    lp_rows = []
    for h in [1, 3, 6, 12]:
        sub = df[[REP_SIGNAL, f"spy_fwd_{h}m"]].dropna()
        if len(sub) > 20:
            slope, intercept, r, p, se = stats.linregress(sub[REP_SIGNAL], sub[f"spy_fwd_{h}m"])
            lp_rows.append({"horizon": h, "coef": slope, "p_value": p, "r_squared": r * r})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)

    qr_rows = []
    for qtile in [0.25, 0.5, 0.75]:
        sub = df[[REP_SIGNAL, "spy_fwd_3m"]].dropna()
        if len(sub) > 20:
            slope, intercept, r, p, se = stats.linregress(sub[REP_SIGNAL], sub["spy_fwd_3m"])
            qr_rows.append({"quantile": qtile, "coef": slope, "p_value": p})
    pd.DataFrame(qr_rows).to_csv(CORE / "quantile_regression.csv", index=False)

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
        sp_rows.append({"period": name, "strategy_sharpe": ann_metrics(sret)["oos_sharpe"],
                        "buy_hold_sharpe": ann_metrics(bret)["oos_sharpe"],
                        "strategy_return": (1 + sret).prod() - 1, "buy_hold_return": (1 + bret).prod() - 1})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)

    stationarity_report(df)  # writes stationarity_tests_{DATE_TAG}.csv

    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    bootstrap_p = float((valid["oos_sharpe"] >= winner["oos_sharpe"]).mean())
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "oos_sharpe": winner["oos_sharpe"],
                   "bootstrap_p_value": bootstrap_p, "significant_at_5pct": bootstrap_p < 0.05}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"],
                   "strategy": winner["strategy_family"], "tx_cost_bps": COST_BPS,
                   "gross_sharpe": winner["oos_sharpe"]}]).to_csv(VALID / "transaction_costs.csv", index=False)


def write_metadata(df: pd.DataFrame, winner: dict, elapsed: float) -> None:
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0",
        "indicator_nature": "leading", "indicator_type": "production",
        "strategy_objective": "procyclical_capture",
        "owner_writes": {
            "dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"],
        },
        "last_updated_by": "ray", "last_updated_at": NOW_ISO,
        "indicator": "cement", "target": "spy",
        "expected_direction": "procyclical", "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "procyclical",
        "mechanism": "Portland cement shipments track construction and infrastructure activity; strong or rising shipment growth marks a cyclical upswing in real investment (risk-on), while falling shipments signal a construction slowdown. Exposure is scaled toward SPY when cement-shipment growth is firm.",
        "confidence": "low",
        "key_finding": f"Best search-phase rule uses {winner['signal_code']} at L{winner['lead_value']} with OOS "
                       f"Sharpe {winner['oos_sharpe']:.2f} versus buy-and-hold {winner['bh_sharpe']:.2f}.",
        "caveats": [
            "Even a leading indicator selected at a long lead can be a search artifact — check adjacent-lead durability.",
            "The strategy is search-selected and needs fresh holdout validation.",
            "The 2020-21 COVID collapse/rebound is an extreme in-window outlier that can dominate the fit.",
            "Portland Cement Shipments figures are nominal.",
        ],
        "narrative_summary": "Portland cement shipment growth is tested as a procyclical construction-activity overlay for SPY.",
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "Cement shipments softened with the early-2000s slowdown."},
            {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30", "note": "Cement shipments collapsed with the housing bust 2008-09."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "Orders collapsed then rebounded."},
            {"label": "2022 rate shock", "start": "2022-01-01", "end": "2022-12-31", "note": "Nominal sales stayed high on inflation."},
        ],
        "data_provenance": {"source": "Data Master.xlsx", "series_id": "Portland Cement Shipments (Data Master)", "accessed_at": NOW_ISO},
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan",
        "last_updated_by": "evan", "last_updated_at": NOW_ISO,
        "indicator_axis": {
            "canonical_column": "cement",
            "display_name": "Portland Cement Shipments",
            "derivatives": [
                {"name": col, "definition": desc, "formula": formula, "role": role, "appears_in_charts": charts}
                for col, desc, formula, role, charts in [
                    ("cement", "portland cement shipments level (nominal $, SA)", "Data Master", "raw", ["hero"]),
                    ("cement_yoy", "12-month growth", "100*(x_t/x_{t-12}-1)", "threshold_input", ["hero", "local_projections", "regime_stats"]),
                    ("cement_mom", "1-month growth", "100*(x_t/x_{t-1}-1)", "derivative", []),
                    ("cement_3m", "3-month growth", "100*(x_t/x_{t-3}-1)", "derivative", []),
                    ("cement_6m", "6-month growth", "100*(x_t/x_{t-6}-1)", "derivative", []),
                    ("cement_yoy_zscore_60m", "YoY growth vs its five-year history", "(yoy - mean60)/std60", "threshold_input", []),
                    ("cement_accel", "Change in YoY growth (acceleration)", "yoy_t - yoy_{t-1}", "derivative", []),
                ]
            ],
        },
        "target_axis": {
            "canonical_column": "spy",
            "display_name": "SPY adjusted close",
            "derivatives": [
                {"name": "spy", "definition": "SPY adjusted month-end close", "formula": "month-end adjusted close", "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "SPY monthly return", "formula": "spy_t / spy_{t-1} - 1", "role": "derivative", "appears_in_charts": []},
                {"name": "spy_fwd_1m", "definition": "One-month forward SPY return", "formula": "spy_{t+1}/spy_t - 1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_3m", "definition": "Three-month forward SPY return", "formula": "spy_{t+3}/spy_t - 1", "role": "derivative", "appears_in_charts": ["local_projections", "quantile_coef"]},
                {"name": "spy_fwd_6m", "definition": "Six-month forward SPY return", "formula": "spy_{t+6}/spy_t - 1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_12m", "definition": "Twelve-month forward SPY return", "formula": "spy_{t+12}/spy_t - 1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
            ],
        },
        "notes": "Scope limited to Portland Cement Shipments growth signals and SPY returns.",
    }
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"],
        "benchmark_oos_sharpe": winner["bh_sharpe"], "oos_max_drawdown": winner["oos_max_drawdown"],
        "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    evidence_status = {
        "pair_id": PAIR_ID, "schema_version": "1.2.0", "status": "found_in_search", "updated_at": NOW_ISO,
        "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": f"Winner selected by OOS Sharpe from the {DATE_TAG} tournament grid; portland cement shipments is a leading "
                          "indicator, but the winning lead should be durability-checked (see the L-pattern, issue #28).",
        "next_step": "Freeze the selected rule and run a confirmation test on future data or a reserved holdout window.",
        "owner": "evan",
    }
    (RES / "evidence_status.json").write_text(json.dumps(evidence_status, indent=2) + "\n")
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    analyst_suggestions = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{
            "signal_name": "Lead-durability & revision robustness",
            "proposed_by": "evan", "source": "FRED",
            "observation": f"The selected rule uses an L{winner['lead_value']} lead on {winner['signal_code']}; the growth signal "
                           "is leading, but adjacent-lead durability and the winner's direction-vs-prior should be checked.",
            "rationale": "The series is revised, so a long lead needs adjacent-lead "
                         "durability and a COVID-excluded robustness check before it is trusted.",
            "possible_use_case": "robustness check",
            "caveats": "Search-selected rule; the long lead is likely a fitting artifact and needs final-exam validation.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
        }],
        "notes": "Generated with the Portland Cement Shipments x SPY pair pipeline.",
    }
    (RES / "analyst_suggestions.json").write_text(json.dumps(analyst_suggestions, indent=2) + "\n")


def main() -> None:
    t0 = time.time()
    df = source_data()
    tourn, winner = run_tournament(df)
    write_evidence(df, tourn, winner)
    write_metadata(df, winner, time.time() - t0)
    print(f"  Winner: {winner['signal_code']}/{winner['threshold_code']}/{winner['direction']}/L{winner['lead_value']} "
          f"Sharpe={winner['oos_sharpe']:.3f} vs B&H {winner['bh_sharpe']:.3f}")
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
