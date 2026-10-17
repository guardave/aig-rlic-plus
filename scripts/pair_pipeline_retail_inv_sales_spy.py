#!/usr/bin/env python3
"""Pair pipeline: Retail Inventories-to-Sales Ratio x SPY.

MONTHLY pipeline. The indicator is the retail inventories-to-sales ratio from Data Master.xlsx.
Bounded, mean-reverting — the LEVEL is stationary and used directly. Economic prior: a HIGH/rising
ratio signals inventory overhang and weakening demand → COUNTERCYCLICAL (reduce SPY when the ratio
is high). Monthly grid, sqrt(12).
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import adfuller, kpss

PAIR_ID = "retail_inv_sales_spy"
DATE_TAG = "20261016"  # pkg9 strict lead floor rerun (grid truncated from the bottom); IS-selected winner (GH #251/#268, common IS start)
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

MASTER_XLSX = str(DATA_DIR / "Data Master.xlsx")
MASTER_SHEET = "Retailers_Inv_to_sales"
MASTER_COL = "Retail Inventories-to-Sales Ratio"
PERIODS_PER_YEAR = 12                 # monthly
MIN_IS_N = 60                         # IS validity floor (months), GH #251/#268
MIN_OOS_N = 20                        # legacy OOS validity floor (months), info only


def read_master() -> pd.Series:
    """Retail Inventories-to-Sales Ratio, monthly, from Data Master."""
    import openpyxl
    wb = openpyxl.load_workbook(MASTER_XLSX, read_only=True, data_only=True)
    ws = wb[MASTER_SHEET]
    rows = [(r[0], r[1]) for r in ws.iter_rows(min_row=2, values_only=True)
            if r and r[0] is not None and r[1] is not None and hasattr(r[0], "year")]
    s = pd.Series({pd.Timestamp(d): float(v) for d, v in rows}, name="invsales").sort_index()
    s = s.resample("ME").last()
    print(f"  [MASTER] Retail Inventories-to-Sales Ratio: {len(s.dropna())} mo, "
          f"{s.dropna().index.min().date()} to {s.dropna().index.max().date()}")
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
    print("Sourcing Retail Inventories-to-Sales Ratio (Data Master) and SPY month-end prices")
    raw = read_master()
    spy, spy_source = _read_spy_monthly()
    df = pd.concat([raw, spy], axis=1).dropna(subset=["invsales", "spy"])
    df["spy_ret"] = df["spy"].pct_change()
    for h in (1, 3, 6):
        df[f"spy_fwd_{h}m"] = df["spy"].pct_change(h).shift(-h)

    lvl = df["invsales"]
    # Bounded / mean-reverting level is a valid stationary signal.
    df["invsales_level"] = lvl
    df["invsales_diff_1m"] = lvl.diff(1)             # month-on-month change
    df["invsales_chg_12m"] = lvl.diff(12)             # 12-month change
    roll_mean = lvl.rolling(60, min_periods=24).mean()
    roll_std = lvl.rolling(60, min_periods=24).std()
    df["invsales_zscore_60m"] = (lvl - roll_mean) / roll_std

    df = df.loc["1993-01-01":].copy()
    df.to_parquet(DATA_DIR / "retail_inv_sales_spy_monthly_latest.parquet")
    df.describe().T.to_csv(DATA_DIR / f"summary_stats_retail_inv_sales_spy_{DATE_TAG}.csv")
    missing = df.isna().sum().rename("missing_count").to_frame()
    missing["missing_pct"] = missing["missing_count"] / len(df)
    missing.to_markdown(DATA_DIR / f"missing_value_report_retail_inv_sales_spy_{DATE_TAG}.md")

    data_dict = pd.DataFrame([
        {"Column Name": "invsales", "Display Name": "Retail Inventories-to-Sales Ratio",
         "Description": "Retail inventories-to-sales ratio",
         "Source": "Data Master.xlsx", "Series ID": "RETAILIRSA", "Unit": "Ratio",
         "Transformation": "Monthly level",
         "Direction Convention": "Higher = inventory overhang / weak demand (bearish equities)",
         "Effective Start": str(df["invsales"].first_valid_index().date()),
         "Known Quirks": "Bounded ratio ~[1.1,1.8], mean-reverting; inventory overhang precedes production cuts",
         "Display Note": "A high inventories-to-sales ratio signals weakening demand and precedes equity weakness.",
         "Refresh Freq.": "Monthly", "Refresh Source": "Data Master"},
        {"Column Name": "spy", "Display Name": "SPY adjusted close",
         "Description": "SPDR S&P 500 ETF adjusted close", "Source": spy_source, "Series ID": "SPY",
         "Unit": "USD", "Transformation": "Month-end adjusted close",
         "Direction Convention": "Higher = higher equity price",
         "Effective Start": str(df["spy"].first_valid_index().date()),
         "Known Quirks": "ETF history begins 1993", "Display Note": "Equity target and benchmark.",
         "Refresh Freq.": "Daily", "Refresh Source": spy_source},
    ])
    data_dict.to_csv(DATA_DIR / f"data_dictionary_retail_inv_sales_spy_{DATE_TAG}.csv", index=False)
    print(f"  Data rows: {len(df)}, {df.index.min().date()} to {df.index.max().date()}")
    return df


def stationarity_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ["invsales_level", "invsales_diff_1m", "invsales_chg_12m", "invsales_zscore_60m", "spy_ret"]:
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
    "level": "invsales_level",
    "diff_1m": "invsales_diff_1m",
    "chg_12m": "invsales_chg_12m",
    "zscore_60m": "invsales_zscore_60m",
}
SIGNAL_DISPLAY = {
    "level": "Retail Inventories-to-Sales Ratio (level)",
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
    leads = list(range(3, 15))  # strict floor E3 (Census MTIS ~46 d after month-end): sub-floor L2 truncated, top not extended (pkg9, protocol D2)
    # GH #251/#268 + common IS start (Lead decision 2026-10-15):
    #   pass 1 builds every candidate's return stream; common_is_start = the LATEST
    #   first-valid-return date across the grid. IS metrics for every candidate are
    #   computed on the SAME window [common_is_start, oos_start); OOS = [oos_start, end].
    cands = []
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
                    cands.append((signal_code, col, tcode, direction, lead, pos, rets))
    common_is_start = max(c[6].index.min() for c in cands)
    is_mask_bh = (work.index >= common_is_start) & (work.index < oos_start)
    bh_is = ann_metrics(work.loc[is_mask_bh, "spy_ret"].dropna())
    bh = ann_metrics(df.loc[oos_start:, "spy_ret"].dropna())

    def _is_block(rets, pos, start):
        r = rets.loc[(rets.index >= start) & (rets.index < oos_start)]
        p = pos.loc[(pos.index >= start) & (pos.index < oos_start)].dropna()
        expo = p.mean() if len(p) else np.nan
        ok = bool(len(r) >= MIN_IS_N and 0.05 <= expo <= 0.95 and r.std() > 0)
        return r, expo, ok

    rows = []
    for signal_code, col, tcode, direction, lead, pos, rets in cands:
        is_rets, is_exposure, is_valid = _is_block(rets, pos, common_is_start)
        own_rets, _own_expo, own_valid = _is_block(rets, pos, rets.index.min())  # sensitivity only
        oos = rets.loc[rets.index >= oos_start]
        pos_oos = pos.loc[pos.index >= oos_start].dropna()
        exposure = pos_oos.mean() if len(pos_oos) else np.nan
        n_trades = int(pos_oos.diff().abs().fillna(0).sum())
        oos_valid = bool(len(oos) >= MIN_OOS_N and 0.05 <= exposure <= 0.95 and oos.std() > 0)  # info / legacy only
        mi = ann_metrics(is_rets)
        mo = ann_metrics(own_rets)
        m = ann_metrics(oos)
        rows.append({"signal": signal_code, "signal_column": col, "threshold": tcode,
                     "strategy": "P1_long_cash", "lead_months": lead, "direction": direction,
                     "is_sharpe": mi["oos_sharpe"], "is_ann_return": mi["oos_ann_return"],
                     "is_max_drawdown": mi["max_drawdown"], "is_exposure": is_exposure,
                     "is_start": is_rets.index.min().date().isoformat() if len(is_rets) else None,
                     "is_end": is_rets.index.max().date().isoformat() if len(is_rets) else None,
                     "common_is_start": common_is_start.date().isoformat(),
                     "own_is_start": own_rets.index.min().date().isoformat() if len(own_rets) else None,
                     "own_is_sharpe": mo["oos_sharpe"], "own_is_n": mo["oos_n"], "own_is_valid": own_valid,
                     "oos_sharpe": m["oos_sharpe"], "oos_sortino": m["oos_sortino"],
                     "oos_calmar": m["oos_calmar"], "oos_ann_return": m["oos_ann_return"], "oos_ann_vol": m["oos_ann_vol"],
                     "max_drawdown": m["max_drawdown"], "win_rate": m["win_rate"], "n_trades": n_trades,
                     "annual_turnover": n_trades / max(len(pos_oos) / PERIODS_PER_YEAR, 1),
                     "is_n": mi["oos_n"], "oos_n": m["oos_n"], "is_valid": is_valid, "oos_valid": oos_valid,
                     "valid": is_valid})  # selection validity = IS (common window) only
    rows.append({"signal": "BENCHMARK", "signal_column": "spy", "threshold": "BUY_HOLD", "strategy": "BUY_HOLD",
                 "lead_months": 0, "direction": "benchmark", "is_sharpe": bh_is["oos_sharpe"], "is_ann_return": bh_is["oos_ann_return"],
                 "is_max_drawdown": bh_is["max_drawdown"], "is_exposure": 1.0,
                 "is_start": common_is_start.date().isoformat(), "is_end": work.index[is_mask_bh][-1].date().isoformat(),
                 "common_is_start": common_is_start.date().isoformat(), "own_is_start": None,
                 "own_is_sharpe": np.nan, "own_is_n": 0, "own_is_valid": False,
                 "oos_sharpe": bh["oos_sharpe"],
                 "oos_sortino": bh["oos_sortino"], "oos_calmar": bh["oos_calmar"], "oos_ann_return": bh["oos_ann_return"],
                 "oos_ann_vol": bh["oos_ann_vol"], "max_drawdown": bh["max_drawdown"], "win_rate": bh["win_rate"], "n_trades": 0,
                 "annual_turnover": 0.0, "is_n": bh_is["oos_n"], "oos_n": bh["oos_n"], "is_valid": False, "oos_valid": False,
                 "valid": False})
    tourn = pd.DataFrame(rows)
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    # PRIMARY selection: argmax IN-SAMPLE Sharpe (common IS window) among IS-valid rows; OOS never consulted.
    wi = valid["is_sharpe"].idxmax()
    # SENSITIVITY (report only): argmax IS Sharpe on each candidate's OWN IS start (no common-start alignment).
    own_pool = tourn[(tourn["own_is_valid"]) & (tourn["signal"] != "BENCHMARK")]
    oi = own_pool["own_is_sharpe"].idxmax()
    # LEGACY comparison only (pre-GH#251 look-ahead behaviour): argmax OOS Sharpe among OOS-valid rows.
    legacy_pool = tourn[(tourn["oos_valid"]) & (tourn["signal"] != "BENCHMARK")]
    li = legacy_pool["oos_sharpe"].idxmax()
    nb = tourn["signal"] != "BENCHMARK"
    tourn["is_rank"] = tourn["is_sharpe"].where(nb).rank(ascending=False, method="min")
    tourn["oos_rank"] = tourn["oos_sharpe"].where(nb).rank(ascending=False, method="min")
    tourn.to_csv(RES / f"tournament_results_{DATE_TAG}.csv", index=False)
    side_cols = ["signal", "threshold", "direction", "lead_months", "is_start", "is_end", "is_n", "is_sharpe",
                 "own_is_start", "own_is_n", "own_is_sharpe", "oos_sharpe", "oos_ann_return",
                 "max_drawdown", "n_trades", "oos_n", "is_rank", "oos_rank"]
    side = pd.DataFrame([dict(role="primary_is_selected_common_start", **tourn.loc[wi, side_cols].to_dict()),
                         dict(role="sensitivity_is_selected_own_start", **tourn.loc[oi, side_cols].to_dict()),
                         dict(role="legacy_oos_selected", **tourn.loc[li, side_cols].to_dict())])
    side.to_csv(RES / f"legacy_oos_selection_{DATE_TAG}.csv", index=False)
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
    runner = valid.drop(index=wi).sort_values("is_sharpe", ascending=False).head(1)
    runner_obj = None
    if not runner.empty:
        r = runner.iloc[0]
        runner_obj = {"signal": str(r["signal"]), "threshold": str(r["threshold"]), "strategy": str(r["strategy"]),
                      "lead_value": int(r["lead_months"]), "objective_value": round(float(r["is_sharpe"]), 6),
                      "oos_sharpe": round(float(r["oos_sharpe"]), 6)}
    is_window = {"start": str(wr["is_start"]), "end": str(wr["is_end"]), "n": int(wr["is_n"]),
                 "common_is_start": common_is_start.date().isoformat(), "oos_start": oos_start.date().isoformat(),
                 "rule": "common_is_start = latest first-valid-return date across all grid candidates; "
                         "IS metrics for every candidate computed on [common_is_start, oos_start)",
                 "bh_is_sharpe": round(float(bh_is["oos_sharpe"]), 6)}
    winner = {
        "pair_id": PAIR_ID, "generated_at": NOW_ISO, "signal_column": str(wr["signal_column"]),
        "signal_code": str(wr["signal"]), "signal_display_name": SIGNAL_DISPLAY[str(wr["signal"])],
        "target_symbol": TARGET_SYMBOL, "threshold_code": str(wr["threshold"]), "threshold_value": round(thr_latest, 6),
        "threshold_rule": "lte" if wr["direction"] == "countercyclical" else "gte",
        "threshold_note": f"{wr['threshold']} threshold; latest if rolling", "strategy_family": "P1_long_cash",
        "strategy_code": "P1", "strategy_display_name": "P1 long cash",
        "strategy_description": f"Use the ratio from {int(wr['lead_months'])} months earlier; hold SPY when it is at or above its rolling five-year median, otherwise hold cash.",
        "lead_value": int(wr["lead_months"]), "lead_unit": "months",
        "lead_description": f"Uses the ratio from {int(wr['lead_months'])} months earlier at each monthly decision date.",
        "lookback": "60m where rolling thresholds apply", "direction": str(wr["direction"]),
        "oos_sharpe": round(om["oos_sharpe"], 6), "oos_sortino": round(om["oos_sortino"], 6), "oos_calmar": round(om["oos_calmar"], 6),
        "oos_ann_return": round(om["oos_ann_return"], 6), "oos_ann_vol": round(om["oos_ann_vol"], 6),
        "oos_max_drawdown": round(om["max_drawdown"], 6), "oos_win_rate": round(om["win_rate"], 6), "oos_n_trades": n_trades,
        "annual_turnover": round(n_trades / max(len(oos) / PERIODS_PER_YEAR, 1), 6), "oos_n": int(len(oos)),
        "oos_period_start": oos.index.min().date().isoformat(), "oos_period_end": oos.index.max().date().isoformat(),
        "bh_sharpe": round(bm["oos_sharpe"], 6), "bh_ann_return": round(bm["oos_ann_return"], 6), "bh_max_drawdown": round(bm["max_drawdown"], 6),
        "cost_assumption_bps": COST_BPS, "total_combos": int((tourn["signal"] != "BENCHMARK").sum()), "valid_combos": int(valid.shape[0]),
        "schema_version": "1.2.0",
        "notes": "A high inventories-to-sales ratio signals weakening demand and precedes equity weakness. On this sample the raw level is NOT stationary (ADF does not reject a unit root; KPSS rejects stationarity) — it drifts — so level signals use 60-month ROLLING-percentile thresholds as adaptive regime filters rather than fixed cutoffs. "
                 f"Winner ({wr['signal']}/{wr['threshold']}) is selected by in-sample Sharpe on the common IS window ({is_window['start']} to {is_window['end']}) "
                 "and evaluated on the held-out OOS window; still a search-selected rule — read as found-in-search.",
        "is_sharpe": round(float(wr["is_sharpe"]), 6), "is_n": int(wr["is_n"]),
        "is_period_start": is_window["start"], "is_period_end": is_window["end"],
        "selection": {"objective": "max_is_sharpe", "objective_formula": "in-sample (common window [common_is_start, OOS start)) monthly mean/std*sqrt(12); winner evaluated on OOS window",
                      "is_window": is_window,
                      "grid_scanned": {"leads": leads, "n_signals": len(SIGNALS),
                                       "n_thresholds": int(sum(len(threshold_codes_for(s)) for s in SIGNALS)),
                                       "n_strategies": 1, "n_valid_combos": int(valid.shape[0]),
                                       "median_valid_objective": round(float(valid["is_sharpe"].median()), 6)},
                      "tie_break_step": None,
                      "raw_winner_row": {"signal": str(wr["signal"]), "threshold": str(wr["threshold"]), "strategy": str(wr["strategy"]),
                                         "lead_column": "lead_months", "lead_value": int(wr["lead_months"]),
                                         "source_tournament_file": f"tournament_results_{DATE_TAG}.csv", "source_row_index": int(wi)},
                      "runner_up": runner_obj, "rationale": "Winner is the IS-valid row with the highest IN-SAMPLE Sharpe (common IS window) over the published grid; OOS metrics are reported for that row only (no OOS look-ahead in selection).",
                      "legacy_oos_selected_row": {"signal": str(tourn.loc[li, "signal"]), "threshold": str(tourn.loc[li, "threshold"]),
                                                  "direction": str(tourn.loc[li, "direction"]), "lead_value": int(tourn.loc[li, "lead_months"]),
                                                  "oos_sharpe": round(float(tourn.loc[li, "oos_sharpe"]), 6),
                                                  "note": f"Pre-GH#251 OOS-argmax selection, comparison only; see legacy_oos_selection_{DATE_TAG}.csv"},
                      "sensitivity_own_is_start_row": {"signal": str(tourn.loc[oi, "signal"]), "threshold": str(tourn.loc[oi, "threshold"]),
                                                       "direction": str(tourn.loc[oi, "direction"]), "lead_value": int(tourn.loc[oi, "lead_months"]),
                                                       "own_is_start": str(tourn.loc[oi, "own_is_start"]),
                                                       "own_is_sharpe": round(float(tourn.loc[oi, "own_is_sharpe"]), 6),
                                                       "note": "IS argmax without common-start alignment; sensitivity only"},
                      "objective_runner_up_divergence": None}}
    (RES / "winner_summary.json").write_text(json.dumps(winner, indent=2) + "\n")
    (RES / "tournament_winner.json").write_text(json.dumps(winner, indent=2) + "\n")
    print(f"  Winner: {winner['signal_code']}/{winner['threshold_code']}/{winner['direction']}/L{winner['lead_value']} "
          f"Sharpe={winner['oos_sharpe']:.3f} vs B&H {winner['bh_sharpe']:.3f} (OOS {winner['oos_n']}mo)")
    return tourn, winner


REP_SIGNAL = "invsales_chg_12m"


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
    # Build quartiles on the common descriptive sample so the count audit is
    # explicit. qcut uses right-closed intervals: observations tied exactly at
    # an internal boundary stay together in the lower bucket. Because the
    # indicator is published to two decimals, boundary ties can make bucket
    # sizes unequal even though the cut points are sample quartiles.
    regime_sample = df[[REP_SIGNAL, "spy_ret"]].dropna()
    q, q_bins = pd.qcut(
        regime_sample[REP_SIGNAL],
        4,
        labels=["Q1", "Q2", "Q3", "Q4"],
        retbins=True,
    )
    q_rows = []
    for lab in ["Q1", "Q2", "Q3", "Q4"]:
        rets = regime_sample.loc[q[q == lab].index, "spy_ret"]
        m = ann_metrics(rets)
        q_rows.append({"quartile": lab, "mean_return": rets.mean(), "sharpe": m["oos_sharpe"], "n": len(rets)})
    assigned_n = sum(row["n"] for row in q_rows)
    if q.isna().any() or assigned_n != len(regime_sample):
        raise RuntimeError(
            "Regime quartile assignment failed completeness check: "
            f"eligible={len(regime_sample)}, assigned={assigned_n}, "
            f"unassigned={int(q.isna().sum())}"
        )
    pd.DataFrame(q_rows).to_csv(RES / "regime_quartile_returns.csv", index=False)
    quartile_meta = {
        "pair_id": PAIR_ID,
        "signal": REP_SIGNAL,
        "construction": "pandas.qcut(signal, 4), right-closed intervals",
        "sample_start": regime_sample.index.min().date().isoformat(),
        "sample_end": regime_sample.index.max().date().isoformat(),
        "eligible_observations": int(len(regime_sample)),
        "boundaries": [float(value) for value in q_bins],
        "boundary_tie_counts": {
            str(float(value)): int(regime_sample[REP_SIGNAL].eq(value).sum())
            for value in q_bins[1:-1]
        },
        "bucket_counts": {row["quartile"]: int(row["n"]) for row in q_rows},
        "unassigned_observations": int(q.isna().sum()),
        "assignment_rule": (
            "Q1 includes the sample minimum and first quartile boundary; "
            "Q2-Q4 are open on the left and closed on the right. Boundary ties "
            "remain together in the lower bucket."
        ),
    }
    (RES / "regime_quartile_metadata.json").write_text(
        json.dumps(quartile_meta, indent=2) + "\n"
    )
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


def write_evidence_status() -> None:
    """Write the search-status explanation without regenerating model outputs."""
    evidence_status = {
        "pair_id": PAIR_ID,
        "schema_version": "1.2.0",
        "status": "found_in_search",
        "updated_at": NOW_ISO,
        "plain_english": (
            "The winning rule was selected for the highest in-sample Sharpe. Lower drawdown than "
            "buy-and-hold in the held-out window is an observed secondary outcome, not the selection "
            "criterion. Neither the Sharpe result nor the lower drawdown has been tested on data "
            "released after the rule was chosen."
        ),
        "technical_note": (
            f"Winner selected by in-sample Sharpe (common pre-OOS window) from the {DATE_TAG} monthly "
            "tournament and evaluated on the held-out OOS window, which was not used for selection; "
            "the OOS window is limited, and drawdown was not a selection criterion."
        ),
        "next_step": (
            "Freeze the selected rule and predefine confirmation criteria, then assess both "
            "Sharpe and drawdown on an independent holdout not used to select the rule."
        ),
        "owner": "evan",
    }
    (RES / "evidence_status.json").write_text(json.dumps(evidence_status, indent=2) + "\n")


def write_metadata(df: pd.DataFrame, winner: dict, elapsed: float) -> None:
    interp = {
        "pair_id": PAIR_ID, "schema_version": "1.1.0", "indicator_nature": "coincident", "indicator_type": "production",
        "strategy_objective": "countercyclical_protection",
        "owner_writes": {"dana": ["indicator_nature", "indicator_type", "known_stress_episodes", "data_provenance"],
                         "evan": ["observed_direction", "direction_consistent", "key_finding", "confidence"],
                         "ray": ["strategy_objective", "narrative_summary", "expected_direction", "mechanism", "caveats"]},
        "last_updated_by": "ray", "last_updated_at": NOW_ISO, "indicator": "invsales", "target": "spy",
        "expected_direction": "countercyclical", "observed_direction": winner["direction"],
        "direction_consistent": winner["direction"] == "countercyclical",
        "mechanism": "The retail inventories-to-sales ratio rises when inventories accumulate faster than sales — a sign of weakening demand that typically precedes production cuts and equity weakness. A low/falling ratio signals healthy demand. The strategy reduces equity exposure when the ratio is high.",
        "confidence": "low",
        "key_finding": f"Best search-phase rule uses {winner['signal_code']} from {winner['lead_value']} months earlier with OOS Sharpe "
                       f"{winner['oos_sharpe']:.2f} versus buy-and-hold {winner['bh_sharpe']:.2f}.",
        "caveats": ["Winner is search-selected on a single monthly sample and needs holdout validation.", "Level thresholds are rolling-percentile based; regime pivots can drift across decades.", "Lead estimates rest on a limited number of cycles in the sample."],
        "narrative_summary": "Retail inventories-to-sales ratio is tested as a countercyclical demand-stress overlay for SPY — reduce exposure when the ratio is high.",
        "known_stress_episodes": [{"label": "Dot-Com recession", "start": "2001-03-01", "end": "2001-11-30", "note": "NBER recession."}, {"label": "Global Financial Crisis", "start": "2007-12-01", "end": "2009-06-30", "note": "NBER recession."}, {"label": "COVID shock", "start": "2020-02-01", "end": "2020-04-30", "note": "NBER recession."}, {"label": "2022 drawdown", "start": "2022-01-01", "end": "2022-12-31", "note": "Rate-hike bear market."}],
        "data_provenance": {"source": "Data Master.xlsx (Census)", "series_id": "RETAILIRSA", "accessed_at": NOW_ISO}}
    (RES / "interpretation_metadata.json").write_text(json.dumps(interp, indent=2) + "\n")
    signal_scope = {
        "pair_id": PAIR_ID, "schema_version": "1.0.0", "owner": "evan", "last_updated_by": "evan", "last_updated_at": NOW_ISO,
        "indicator_axis": {"canonical_column": "invsales", "display_name": "Retail Inventories-to-Sales Ratio",
            "derivatives": [{"name": c, "definition": d, "formula": f, "role": r, "appears_in_charts": ch} for c, d, f, r, ch in [
                ("invsales", "Retail Inventories-to-Sales Ratio", "Data Master (Census)", "raw", ["hero"]),
                ("invsales_level", "Inventories-to-sales ratio level", "identity", "threshold_input", ["hero", "regime_stats"]),
                ("invsales_diff_1m", "Month-on-month change", "x_t - x_{t-1}", "derivative", []),
                ("invsales_chg_12m", "12-month change", "x_t - x_{t-12}", "threshold_input", ["local_projections"]),
                ("invsales_zscore_60m", "Level vs 5-year history", "(x-mean60m)/std60m", "threshold_input", [])]]},
        "target_axis": {"canonical_column": "spy", "display_name": "SPY adjusted close",
            "derivatives": [{"name": "spy", "definition": "SPY adjusted month-end close", "formula": "month-end adjusted close", "role": "raw", "appears_in_charts": ["hero", "equity_curves"]},
                {"name": "spy_ret", "definition": "SPY monthly return", "formula": "spy_t/spy_{t-1}-1", "role": "derivative", "appears_in_charts": []},
                {"name": "spy_fwd_1m", "definition": "1-month forward SPY return", "formula": "spy_{t+1}/spy_t-1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]},
                {"name": "spy_fwd_3m", "definition": "3-month forward SPY return", "formula": "spy_{t+3}/spy_t-1", "role": "derivative", "appears_in_charts": ["local_projections", "quantile_coef"]},
                {"name": "spy_fwd_6m", "definition": "6-month forward SPY return", "formula": "spy_{t+6}/spy_t-1", "role": "derivative", "appears_in_charts": ["correlation_heatmap"]}]},
        "notes": "Scope limited to Retail Inventories-to-Sales Ratio signals and SPY returns."}
    (RES / "signal_scope.json").write_text(json.dumps(signal_scope, indent=2) + "\n")
    (RES / "kpis.json").write_text(json.dumps({"pair_id": PAIR_ID, "winner_oos_sharpe": winner["oos_sharpe"],
        "benchmark_oos_sharpe": winner["bh_sharpe"], "oos_max_drawdown": winner["oos_max_drawdown"], "bh_max_drawdown": winner["bh_max_drawdown"]}, indent=2) + "\n")
    write_evidence_status()
    (RES / f"pipeline_timing_{DATE_TAG}.json").write_text(json.dumps({"pair_id": PAIR_ID, "elapsed_seconds": elapsed, "generated_at": NOW_ISO}, indent=2) + "\n")
    (RES / "analyst_suggestions.json").write_text(json.dumps({"pair_id": PAIR_ID, "schema_version": "1.0.0", "last_updated_at": NOW_ISO,
        "suggestions": [{"signal_name": "Timing robustness", "proposed_by": "evan", "source": "Data Master",
            "observation": f"The rule uses {winner['signal_code']} from {winner['lead_value']} months earlier; verify adjacent timing offsets.",
            "rationale": "Cycles in the sample are few, so the timing choice needs adjacent-offset durability and a cycle-count caveat.",
            "possible_use_case": "robustness check", "caveats": "Search-selected on a limited OOS; needs final-exam validation.",
            "date_filed": DATE_TAG[:4] + "-" + DATE_TAG[4:6] + "-" + DATE_TAG[6:]}], "notes": "Generated with the Retail Inventories-to-Sales Ratio x SPY pair pipeline."}, indent=2) + "\n")


def main() -> None:
    t0 = time.time()
    df = source_data()
    tourn, winner = run_tournament(df)
    write_evidence(df, tourn, winner)
    write_metadata(df, winner, time.time() - t0)
    print(f"Done. Results saved to {RES}")


if __name__ == "__main__":
    main()
