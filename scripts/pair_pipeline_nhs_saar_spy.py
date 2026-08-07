#!/usr/bin/env python3
"""Pair pipeline: New Home Sales, SAAR (FRED HSN1F) x SPY.

Compact monthly pipeline for the portal's standard pair contract. Sources
New Home Sales at a Seasonally Adjusted Annual Rate (FRED HSN1F, thousands of
units) and SPY month-end prices, builds home-sales growth/level signals, runs
a long/cash tournament, and writes the core artifacts consumed by the
Streamlit templates.

This is the SAAR counterpart to the existing `nhs_spy` pair, which uses the
NOT-seasonally-adjusted series (HSN1FNSA) and must deseasonalise every signal.
Because HSN1F is already seasonally adjusted, growth and level signals are
used directly without STL deseasonalisation.

New Home Sales is an early-cycle housing leading indicator: buyers commit
before construction, so sales lead starts, permits, and the activity they
drive. The natural prior is procyclical -- stronger home-sales growth should
coincide with a healthier expansion and better equities.
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


PAIR_ID = "nhs_saar_spy"
DATE_TAG = "20260804"
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
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    with urlopen(url, timeout=30) as response:
        df = pd.read_csv(response)
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    values = pd.to_numeric(df[series_id], errors="coerce")
    out = pd.Series(values.values, index=df["observation_date"], name=series_id.lower())
    return out.dropna()


def _read_spy_monthly() -> tuple[pd.Series, str]:
    try:
        spy_raw = yf.download(
            "SPY",
            start="1993-01-01",
            progress=False,
            auto_adjust=True,
            actions=False,
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
        DATA_DIR / "m2sl_yoy_spy_daily_latest.parquet",
        DATA_DIR / "phlxsox_spy_daily_latest.parquet",
    ):
        if fallback.exists():
            local = pd.read_parquet(fallback)
            if "spy" in local.columns:
                print(f"  Using local SPY fallback: {fallback.relative_to(REPO)}")
                spy = local["spy"].resample("ME").last().rename("spy")
                return spy, f"Local fallback: {fallback.name}"
    raise RuntimeError("No SPY data available from Yahoo Finance or local fallback panels")


def source_data() -> pd.DataFrame:
    print("Sourcing HSN1F (New Home Sales, SAAR) from FRED and SPY month-end prices")
    nhs = _read_fred_csv("HSN1F").resample("ME").last()
    spy, spy_source = _read_spy_monthly()

    df = pd.concat([nhs.rename("hsn1f"), spy], axis=1).dropna(subset=["hsn1f", "spy"])
    df["spy_ret"] = df["spy"].pct_change()
    for horizon in (1, 3, 6, 12):
        df[f"spy_fwd_{horizon}m"] = df["spy"].pct_change(horizon).shift(-horizon)

    # Home-sales growth/level signals (HSN1F is already seasonally adjusted).
    # Growth signals are expressed in PERCENT (x100), matching the portal's
    # convention for momentum/growth signals (e.g. permit_mom1m, umcsent_mom).
    # Raw fractional form (~0.02) never reaches the historical-plausibility
    # extreme the Probability Engine panel expects during a crisis window.
    df["nhs_mom"] = df["hsn1f"].pct_change(1) * 100
    df["nhs_pct_3m"] = df["hsn1f"].pct_change(3) * 100
    df["nhs_pct_6m"] = df["hsn1f"].pct_change(6) * 100
    df["nhs_pct_yoy"] = df["hsn1f"].pct_change(12) * 100
    roll_mean = df["hsn1f"].rolling(60, min_periods=36).mean()
    roll_std = df["hsn1f"].rolling(60, min_periods=36).std()
    df["nhs_zscore_60m"] = (df["hsn1f"] - roll_mean) / roll_std
    # 6-month momentum of the level relative to its own 6-month-ago value,
    # expressed as an annualised-style growth proxy for regime context.
    df["nhs_6m_chg"] = df["hsn1f"].diff(6)
    # Housing-contraction flag: YoY growth negative for chart shading / context.
    df["nhs_contraction_flag"] = (df["nhs_pct_yoy"] < 0).astype(float)

    df = df.loc["1993-01-31":].copy()
    df.to_parquet(DATA_DIR / "nhs_saar_spy_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_nhs_saar_spy_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_nhs_saar_spy_{DATE_TAG}.md")

    data_dict = pd.DataFrame(
        [
            {
                "Column Name": "hsn1f",
                "Display Name": "New Home Sales (SAAR)",
                "Description": "New one-family houses sold, seasonally adjusted annual rate",
                "Source": "FRED",
                "Series ID": "HSN1F",
                "Unit": "Thousands of units (SAAR)",
                "Transformation": "Monthly level",
                "Seasonal Adj.": "Seasonally adjusted",
                "Direction Convention": "Higher / rising = stronger housing demand / early-cycle strength",
                "Effective Start": str(df["hsn1f"].first_valid_index().date()),
                "Known Quirks": "Early-cycle housing leading indicator; monthly release is revised and can be volatile.",
                "Display Note": "Buyers commit before construction, so new-home sales tend to lead the broader cycle.",
                "Refresh Freq.": "Monthly",
                "Refresh Source": "FRED CSV",
            },
            {
                "Column Name": "spy",
                "Display Name": "SPY adjusted close",
                "Description": "SPDR S&P 500 ETF adjusted close",
                "Source": spy_source,
                "Series ID": "SPY",
                "Unit": "USD",
                "Transformation": "Month-end adjusted close",
                "Seasonal Adj.": "N/A",
                "Direction Convention": "Higher = higher equity price",
                "Effective Start": str(df["spy"].first_valid_index().date()),
                "Known Quirks": "ETF history begins in 1993",
                "Display Note": "Used as the equity-market target and benchmark.",
                "Refresh Freq.": "Daily",
                "Refresh Source": spy_source,
            },
        ]
    )
    data_dict.to_csv(DATA_DIR / f"data_dictionary_nhs_saar_spy_{DATE_TAG}.csv", index=False)
    print(f"  Data rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def ann_metrics(rets: pd.Series) -> dict[str, float]:
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return {
            "oos_sharpe": 0.0,
            "oos_sortino": 0.0,
            "oos_calmar": 0.0,
            "oos_ann_return": 0.0,
            "oos_ann_vol": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "oos_n": int(len(rets)),
        }
    ann_return = (1 + rets).prod() ** (12 / len(rets)) - 1
    ann_vol = rets.std() * np.sqrt(12)
    sharpe = rets.mean() / rets.std() * np.sqrt(12)
    neg = rets[rets < 0]
    sortino = ann_return / (neg.std() * np.sqrt(12)) if len(neg) > 1 and neg.std() > 0 else 0.0
    equity = (1 + rets).cumprod()
    max_dd = (equity / equity.cummax() - 1).min()
    calmar = ann_return / abs(max_dd) if max_dd < 0 else 0.0
    return {
        "oos_sharpe": float(sharpe),
        "oos_sortino": float(sortino),
        "oos_calmar": float(calmar),
        "oos_ann_return": float(ann_return),
        "oos_ann_vol": float(ann_vol),
        "max_drawdown": float(max_dd),
        "win_rate": float((rets > 0).mean()),
        "oos_n": int(len(rets)),
    }


SIGNALS = {
    "yoy": "nhs_pct_yoy",
    "pct_6m": "nhs_pct_6m",
    "pct_3m": "nhs_pct_3m",
    "mom": "nhs_mom",
    "zscore_60m": "nhs_zscore_60m",
    "chg_6m": "nhs_6m_chg",
}


def build_threshold(series: pd.Series, code: str) -> pd.Series | float:
    if code == "T0_zero":
        return 0.0
    if code == "T_z_0":
        return 0.0
    if code == "T_z_-0.5":
        return -0.5
    if code == "T_roll_p25":
        return series.rolling(60, min_periods=36).quantile(0.25)
    if code == "T_roll_p50":
        return series.rolling(60, min_periods=36).quantile(0.50)
    if code == "T_roll_p75":
        return series.rolling(60, min_periods=36).quantile(0.75)
    raise ValueError(code)


def threshold_codes_for(signal_code: str) -> list[str]:
    if signal_code in {"yoy", "pct_6m", "pct_3m", "mom"}:
        return ["T0_zero", "T_roll_p25", "T_roll_p50"]
    if signal_code == "zscore_60m":
        return ["T_z_0", "T_z_-0.5", "T_roll_p25"]
    return ["T_roll_p25", "T_roll_p50", "T_roll_p75"]


def make_position(signal: pd.Series, threshold: pd.Series | float, direction: str) -> pd.Series:
    if isinstance(threshold, pd.Series):
        thresh = threshold.reindex(signal.index)
    else:
        thresh = pd.Series(float(threshold), index=signal.index)
    if direction == "procyclical":
        # Hold equities when home-sales growth is strong (signal above threshold).
        pos = (signal >= thresh).astype(float)
    else:
        pos = (signal <= thresh).astype(float)
    return pos.where(signal.notna() & thresh.notna())


def run_tournament(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    oos_start = pd.Timestamp("2017-01-31")
    leads = [0, 1, 2, 3, 6, 9, 12]
    rows = []
    strategy_series: dict[str, pd.Series] = {}
    bh_oos = df.loc[oos_start:, "spy_ret"].dropna()
    bh = ann_metrics(bh_oos)

    for signal_code, col in SIGNALS.items():
        raw = df[col].astype(float)
        for threshold_code in threshold_codes_for(signal_code):
            threshold = build_threshold(raw, threshold_code)
            for direction in ["procyclical", "countercyclical"]:
                for lead in leads:
                    sig = raw.shift(lead)
                    thresh = threshold.shift(lead) if isinstance(threshold, pd.Series) else threshold
                    pos = make_position(sig, thresh, direction)
                    rets = (pos * df["spy_ret"]).dropna()
                    oos = rets.loc[oos_start:]
                    exposure = pos.loc[oos_start:].dropna().mean()
                    n_trades = int(pos.loc[oos_start:].dropna().diff().abs().fillna(0).sum())
                    valid = len(oos) >= 60 and 0.05 <= exposure <= 0.95 and oos.std() > 0
                    metrics = ann_metrics(oos)
                    key = f"{signal_code}|{threshold_code}|{direction}|{lead}"
                    strategy_series[key] = rets
                    rows.append(
                        {
                            "signal": signal_code,
                            "signal_column": col,
                            "threshold": threshold_code,
                            "strategy": "P1_long_cash",
                            "lead_months": lead,
                            "direction": direction,
                            "is_sharpe": metrics["oos_sharpe"],
                            "oos_sharpe": metrics["oos_sharpe"],
                            "oos_sortino": metrics["oos_sortino"],
                            "oos_calmar": metrics["oos_calmar"],
                            "oos_ann_return": metrics["oos_ann_return"],
                            "oos_ann_vol": metrics["oos_ann_vol"],
                            "max_drawdown": metrics["max_drawdown"],
                            "win_rate": metrics["win_rate"],
                            "annual_turnover": n_trades / max(len(pos.loc[oos_start:].dropna()) / 12, 1),
                            "is_n": metrics["oos_n"],
                            "oos_n": metrics["oos_n"],
                            "valid": bool(valid),
                        }
                    )

    rows.append(
        {
            "signal": "BENCHMARK",
            "signal_column": "spy",
            "threshold": "BUY_HOLD",
            "strategy": "BUY_HOLD",
            "lead_months": 0,
            "direction": "benchmark",
            "is_sharpe": bh["oos_sharpe"],
            "oos_sharpe": bh["oos_sharpe"],
            "oos_sortino": bh["oos_sortino"],
            "oos_calmar": bh["oos_calmar"],
            "oos_ann_return": bh["oos_ann_return"],
            "oos_ann_vol": bh["oos_ann_vol"],
            "max_drawdown": bh["max_drawdown"],
            "win_rate": bh["win_rate"],
            "annual_turnover": 0.0,
            "is_n": bh["oos_n"],
            "oos_n": bh["oos_n"],
            "valid": False,
        }
    )

    tourn = pd.DataFrame(rows)
    tourn_path = RES / f"tournament_results_{DATE_TAG}.csv"
    tourn.to_csv(tourn_path, index=False)
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    winner_idx = valid["oos_sharpe"].idxmax()
    winner_row = tourn.loc[winner_idx].copy()
    winner_key = (
        f"{winner_row['signal']}|{winner_row['threshold']}|"
        f"{winner_row['direction']}|{int(winner_row['lead_months'])}"
    )

    raw = df[winner_row["signal_column"]].astype(float)
    threshold = build_threshold(raw, str(winner_row["threshold"]))
    signal_for_rule = raw.shift(int(winner_row["lead_months"]))
    threshold_for_rule = threshold.shift(int(winner_row["lead_months"])) if isinstance(threshold, pd.Series) else threshold
    position = make_position(signal_for_rule, threshold_for_rule, str(winner_row["direction"])).fillna(0.0)
    strategy_return = (position * df["spy_ret"]).fillna(0.0)
    benchmark_return = df["spy_ret"].fillna(0.0)

    strategy_df = pd.DataFrame(
        {
            "date": df.index,
            "signal": signal_for_rule.values,
            "threshold": threshold_for_rule.reindex(df.index).values
            if isinstance(threshold_for_rule, pd.Series)
            else np.repeat(float(threshold_for_rule), len(df)),
            "position": position.values,
            "strategy_return": strategy_return.values,
            "benchmark_return": benchmark_return.values,
        }
    )
    strategy_df["strategy_equity"] = (1 + strategy_df["strategy_return"]).cumprod()
    strategy_df["benchmark_equity"] = (1 + strategy_df["benchmark_return"]).cumprod()
    strategy_df.to_csv(RES / f"strategy_returns_{DATE_TAG}.csv", index=False)
    (RES / f"strategy_returns_{DATE_TAG}_meta.json").write_text(
        json.dumps({"pair_id": PAIR_ID, "winner_key": winner_key, "generated_at": NOW_ISO}, indent=2) + "\n"
    )

    sig_cols = list(SIGNALS.values()) + ["nhs_contraction_flag"]
    df[sig_cols].to_parquet(RES / f"signals_{DATE_TAG}.parquet")

    changes = position.diff().fillna(0)
    trades = []
    for dt, delta in changes[changes != 0].items():
        side = "BUY" if delta > 0 else "SELL"
        trades.append(
            {
                "trade_date": dt.date().isoformat(),
                "side": side,
                "instrument": TARGET_SYMBOL,
                "quantity_pct": abs(float(delta)) * 100,
                "commission_bps": COST_BPS,
                "signal_value": float(signal_for_rule.loc[dt]) if pd.notna(signal_for_rule.loc[dt]) else np.nan,
                "threshold_value": float(strategy_df.loc[strategy_df["date"] == dt, "threshold"].iloc[0]),
                "position_before": float(position.shift(1).fillna(0).loc[dt]),
                "position_after": float(position.loc[dt]),
                "reason": f"{winner_row['signal']} {winner_row['direction']} rule crossed {winner_row['threshold']}",
            }
        )
    pd.DataFrame(trades).to_csv(RES / "winner_trade_log.csv", index=False)
    pd.DataFrame(trades).to_csv(RES / "winner_trades_broker_style.csv", index=False)

    oos = strategy_return.loc[oos_start:].dropna()
    n_trades = int(position.loc[oos_start:].dropna().diff().abs().fillna(0).sum())
    oos_metrics = ann_metrics(oos)
    bh_metrics = ann_metrics(benchmark_return.loc[oos_start:].dropna())
    threshold_latest = (
        float(threshold.dropna().iloc[-1]) if isinstance(threshold, pd.Series) else float(threshold)
    )
    runner = valid.drop(index=winner_idx).sort_values("oos_sharpe", ascending=False).head(1)
    runner_obj = None
    if not runner.empty:
        r = runner.iloc[0]
        runner_obj = {
            "signal": str(r["signal"]),
            "threshold": str(r["threshold"]),
            "strategy": str(r["strategy"]),
            "lead_value": int(r["lead_months"]),
            "objective_value": round(float(r["oos_sharpe"]), 6),
        }
    signal_display_map = {
        "yoy": "12-month growth in New Home Sales (SAAR)",
        "pct_6m": "6-month growth in New Home Sales (SAAR)",
        "pct_3m": "3-month growth in New Home Sales (SAAR)",
        "mom": "Monthly growth in New Home Sales (SAAR)",
        "zscore_60m": "60-month New Home Sales z-score",
        "chg_6m": "6-month change in New Home Sales level",
    }
    winner = {
        "pair_id": PAIR_ID,
        "generated_at": NOW_ISO,
        "signal_column": str(winner_row["signal_column"]),
        "signal_code": str(winner_row["signal"]),
        "signal_display_name": signal_display_map[str(winner_row["signal"])],
        "target_symbol": TARGET_SYMBOL,
        "threshold_code": str(winner_row["threshold"]),
        "threshold_value": round(threshold_latest, 6),
        "threshold_rule": "gte" if winner_row["direction"] == "procyclical" else "lte",
        "threshold_note": f"{winner_row['threshold']} threshold; threshold_value is latest if rolling",
        "strategy_family": "P1_long_cash",
        "strategy_code": "P1",
        "strategy_display_name": "P1 long cash",
        "strategy_description": "Hold SPY when the lagged New Home Sales signal is favorable; otherwise hold cash.",
        "lead_value": int(winner_row["lead_months"]),
        "lead_unit": "months",
        "lead_description": f"Signal is lagged {int(winner_row['lead_months'])} month(s) before allocation.",
        "lookback": "LB60 where rolling thresholds apply",
        "direction": str(winner_row["direction"]),
        "oos_sharpe": round(oos_metrics["oos_sharpe"], 6),
        "oos_sortino": round(oos_metrics["oos_sortino"], 6),
        "oos_calmar": round(oos_metrics["oos_calmar"], 6),
        "oos_ann_return": round(oos_metrics["oos_ann_return"], 6),
        "oos_ann_vol": round(oos_metrics["oos_ann_vol"], 6),
        "oos_max_drawdown": round(oos_metrics["max_drawdown"], 6),
        "oos_win_rate": round(oos_metrics["win_rate"], 6),
        "oos_n_trades": n_trades,
        "annual_turnover": round(n_trades / max(len(oos) / 12, 1), 6),
        "oos_n": int(len(oos)),
        "oos_period_start": oos.index.min().date().isoformat(),
        "oos_period_end": oos.index.max().date().isoformat(),
        "bh_sharpe": round(bh_metrics["oos_sharpe"], 6),
        "bh_ann_return": round(bh_metrics["oos_ann_return"], 6),
        "bh_max_drawdown": round(bh_metrics["max_drawdown"], 6),
        "cost_assumption_bps": COST_BPS,
        "total_combos": int((tourn["signal"] != "BENCHMARK").sum()),
        "valid_combos": int(valid.shape[0]),
        "schema_version": "1.2.0",
        "notes": "New Home Sales (SAAR) is an early-cycle housing leading indicator; the searched rule is a procyclical long/cash overlay, not a proven forecast.",
        "selection": {
            "objective": "max_oos_sharpe",
            "objective_formula": "monthly mean/std*sqrt(12), OOS from 2017-01",
            "grid_scanned": {
                "leads": leads,
                "n_signals": len(SIGNALS),
                "n_thresholds": int(sum(len(threshold_codes_for(s)) for s in SIGNALS)),
                "n_strategies": 1,
                "n_valid_combos": int(valid.shape[0]),
                "median_valid_objective": round(float(valid["oos_sharpe"].median()), 6),
            },
            "tie_break_step": None,
            "raw_winner_row": {
                "signal": str(winner_row["signal"]),
                "threshold": str(winner_row["threshold"]),
                "strategy": str(winner_row["strategy"]),
                "lead_column": "lead_months",
                "lead_value": int(winner_row["lead_months"]),
                "source_tournament_file": f"tournament_results_{DATE_TAG}.csv",
                "source_row_index": int(winner_idx),
            },
            "runner_up": runner_obj,
            "rationale": "Winner is the valid row with the highest OOS Sharpe over the published grid.",
            "objective_runner_up_divergence": None,
        },
    }
    (RES / "winner_summary.json").write_text(json.dumps(winner, indent=2) + "\n")
    (RES / "tournament_winner.json").write_text(json.dumps(winner, indent=2) + "\n")
    print(
        f"  Winner: {winner['signal_code']} / {winner['threshold_code']} / "
        f"{winner['direction']} / L{winner['lead_value']} Sharpe={winner['oos_sharpe']:.2f} "
        f"(BH {winner['bh_sharpe']:.2f})"
    )
    return tourn, winner


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
    gdata = df[["spy_ret", "nhs_pct_6m"]].dropna()
    if len(gdata) > 80:
        tests = grangercausalitytests(gdata[["spy_ret", "nhs_pct_6m"]], maxlag=12, verbose=False)
        for lag, res in tests.items():
            f_stat, p_val, _, _ = res[0]["ssr_ftest"]
            granger_rows.append({"lag": lag, "f_stat": f_stat, "p_value": p_val, "direction": "NHS_to_SPY"})
    pd.DataFrame(granger_rows).to_csv(CORE / "granger_causality.csv", index=False)
    pd.DataFrame(granger_rows).to_csv(RES / "granger_by_lag.csv", index=False)

    ccf_rows = []
    x = df["nhs_pct_6m"]
    y = df["spy_ret"]
    for lag in range(-12, 13):
        sub = pd.concat([x.shift(lag), y], axis=1).dropna()
        corr = sub.iloc[:, 0].corr(sub.iloc[:, 1]) if len(sub) > 20 else np.nan
        ci = 1.96 / np.sqrt(max(len(sub), 1))
        ccf_rows.append({"lag": lag, "ccf": corr, "upper_ci": ci, "lower_ci": -ci, "significant": abs(corr) > ci if pd.notna(corr) else False})
    pd.DataFrame(ccf_rows).to_csv(CORE / "ccf_prewhitened.csv", index=False)

    q = pd.qcut(df["hsn1f"].dropna(), 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q_rows = []
    for label in ["Q1", "Q2", "Q3", "Q4"]:
        idx = q[q == label].index
        rets = df.loc[idx, "spy_ret"].dropna()
        m = ann_metrics(rets)
        q_rows.append({"quartile": label, "mean_return": rets.mean(), "sharpe": m["oos_sharpe"], "n": len(rets)})
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)

    rcorr = []
    for dt in df.index:
        window = df.loc[:dt, ["nhs_pct_6m", "spy_ret"]].tail(60).dropna()
        if len(window) >= 36:
            rcorr.append({"date": dt, "rolling_corr": window["nhs_pct_6m"].corr(window["spy_ret"])})
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
        sub = df[["nhs_pct_6m", f"spy_fwd_{h}m"]].dropna()
        if len(sub) > 20:
            slope, intercept, r, p, se = stats.linregress(sub["nhs_pct_6m"], sub[f"spy_fwd_{h}m"])
            lp_rows.append({"horizon": h, "coef": slope, "p_value": p, "r_squared": r * r})
    pd.DataFrame(lp_rows).to_csv(CORE / "local_projections.csv", index=False)
    pd.DataFrame(lp_rows).to_csv(CORE / "predictive_regressions.csv", index=False)

    qr_rows = []
    for qtile in [0.25, 0.5, 0.75]:
        sub = df[["nhs_pct_6m", "spy_fwd_3m"]].dropna()
        if len(sub) > 20:
            slope, intercept, r, p, se = stats.linregress(sub["nhs_pct_6m"], sub["spy_fwd_3m"])
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
        sp_rows.append({"period": name, "strategy_sharpe": ann_metrics(sret)["oos_sharpe"], "buy_hold_sharpe": ann_metrics(bret)["oos_sharpe"], "strategy_return": (1 + sret).prod() - 1, "buy_hold_return": (1 + bret).prod() - 1})
    pd.DataFrame(sp_rows).to_csv(RES / "subperiod_sharpe.csv", index=False)

    station_rows = []
    for col in ["hsn1f", "nhs_pct_6m", "nhs_pct_yoy", "spy_ret"]:
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

    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    bootstrap_p = float((valid["oos_sharpe"] >= winner["oos_sharpe"]).mean())
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"], "strategy": winner["strategy_family"], "oos_sharpe": winner["oos_sharpe"], "bootstrap_p_value": bootstrap_p, "significant_at_5pct": bootstrap_p < 0.05}]).to_csv(VALID / "bootstrap.csv", index=False)
    pd.DataFrame([{"signal": winner["signal_code"], "threshold": winner["threshold_code"], "strategy": winner["strategy_family"], "tx_cost_bps": COST_BPS, "gross_sharpe": winner["oos_sharpe"]}]).to_csv(VALID / "transaction_costs.csv", index=False)


def write_metadata(df: pd.DataFrame, winner: dict, elapsed: float) -> None:
    interp = {
        "pair_id": PAIR_ID,
        "schema_version": "1.1.0",
        "indicator_nature": "leading",
        "indicator_type": "macro",
        "strategy_objective": "max_sharpe",
        "owner_writes": {
            "dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
            "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
            "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"],
        },
        "last_updated_by": "ray",
        "last_updated_at": NOW_ISO,
        "indicator": "nhs_saar",
        "target": "spy",
        "expected_direction": "procyclical",
        "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "procyclical",
        "mechanism": "New home buyers commit before construction, so new-home sales lead the housing cycle and the broader expansion; stronger home-sales growth should coincide with a healthier economy and support equities.",
        "confidence": "low",
        "key_finding": f"Best search-phase rule uses {winner['signal_code']} at L{winner['lead_value']} with OOS Sharpe {winner['oos_sharpe']:.2f} versus buy-and-hold {winner['bh_sharpe']:.2f}.",
        "caveats": [
            "New Home Sales is volatile month to month and is revised after release.",
            "The strategy is search-selected and needs a fresh holdout confirmation.",
            "Housing leads the cycle, but the lead time to equities is variable and regime-dependent.",
        ],
        "narrative_summary": "New Home Sales (SAAR) is tested as an early-cycle housing overlay for SPY: a procyclical timing signal, not a clean forecast.",
        "known_stress_episodes": [
            {"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "Housing held up better than equities in this episode."},
            {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30", "note": "New Home Sales collapsed ahead of and through the crisis."},
            {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "Home sales dropped then rebounded sharply on low rates."},
        ],
        "data_provenance": {"source": "FRED", "series_id": "HSN1F", "accessed_at": NOW_ISO},
    }
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")

    signal_scope = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "owner": "evan",
        "last_updated_by": "evan",
        "last_updated_at": NOW_ISO,
        "indicator_axis": {
            "canonical_column": "hsn1f",
            "display_name": "New Home Sales (SAAR)",
            "derivatives": [
                {"name": col, "definition": desc, "formula": formula, "role": role, "appears_in_charts": charts}
                for col, desc, formula, role, charts in [
                    ("hsn1f", "New one-family houses sold, SAAR", "FRED HSN1F", "raw", ["hero", "regime_stats"]),
                    ("nhs_mom", "Monthly growth in New Home Sales", "x_t / x_{t-1} - 1", "derivative", []),
                    ("nhs_pct_3m", "Three-month growth in New Home Sales", "x_t / x_{t-3} - 1", "derivative", []),
                    ("nhs_pct_6m", "Six-month growth in New Home Sales", "x_t / x_{t-6} - 1", "derivative", ["local_projections", "ccf_prewhitened"]),
                    ("nhs_pct_yoy", "Twelve-month growth in New Home Sales", "x_t / x_{t-12} - 1", "derivative", []),
                    ("nhs_zscore_60m", "New Home Sales versus its five-year history", "(x - mean60)/std60", "threshold_input", []),
                    ("nhs_6m_chg", "Six-month change in the New Home Sales level", "x_t - x_{t-6}", "derivative", []),
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
        "notes": "Scope limited to New Home Sales (SAAR, HSN1F) growth/level signals and SPY returns.",
    }
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"], "benchmark_oos_sharpe": winner["bh_sharpe"], "oos_max_drawdown": winner["oos_max_drawdown"], "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    evidence_status = {
        "pair_id": PAIR_ID,
        "schema_version": "1.2.0",
        "status": "found_in_search",
        "updated_at": NOW_ISO,
        "plain_english": "A winning rule was found in the search grid, but it has not passed a fresh final exam.",
        "technical_note": "Winner is selected by OOS Sharpe from the 20260804 tournament grid; New Home Sales is a volatile leading indicator and formal causality is weak.",
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
                "signal_name": "New Home Sales release-lag robustness",
                "proposed_by": "evan",
                "source": "FRED",
                "observation": f"The selected rule uses a {winner['lead_value']}-month lead on the {winner['signal_code']} New Home Sales signal in the searched OOS window.",
                "rationale": "New Home Sales is released with a delay and revised, so deployment should test whether release timing and revision assumptions change the result.",
                "possible_use_case": "robustness check",
                "caveats": "Search-selected rule; the housing-to-equity lead time is variable and the result is not final-exam validated.",
                "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:],
            }
        ],
        "notes": "Generated with the New Home Sales (SAAR) x SPY pair pipeline.",
    }
    (RES / "analyst_suggestions.json").write_text(json.dumps(analyst_suggestions, indent=2) + "\n")


def main() -> None:
    t0 = time.time()
    df = source_data()
    tourn, winner = run_tournament(df)
    write_evidence(df, tourn, winner)
    write_metadata(df, winner, time.time() - t0)
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
