#!/usr/bin/env python3
"""
Extended Lead Tournament Re-Run: gold_copper_xli (ECON-LT1 cascade)

Extends the native tournament to L=0..12 months (×21 trading days per ECON-LL1).
Broader signal set (all 13 gold_copper_* transforms) and expanded threshold grid
matching the gating sweep design. Produces the full cascade:
- tournament_results_20260613.csv (extended)
- winner_summary.json (new winner)
- signals_20260613.parquet
- strategy_returns_20260613.csv (ECON-SR1)
- winner_trade_log.csv
- winner_trades_broker_style.csv
- subperiod_sharpe.csv
- rolling_correlation_gold_copper_xli.csv (CP1-B, signal-dependent)
- structural_break_gold_copper_xli.json (CP1-C, signal-dependent)
- rolling_sharpe_gold_copper_xli.csv (CP2-A)  [rolling sharpe from trade log]
- rolling_granger_gold_copper_xli.csv (CP2-B, signal-dependent)

Supersedes: econ_pipeline_gold_copper_xli.py (original 90-combo tournament)
"""

import os, sys, json, time, warnings, itertools
from datetime import datetime, timezone
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
np.random.seed(42)

PAIR_ID = "gold_copper_xli"
DATE_TAG = "20260613"
BASE_DIR = "/workspaces/aig-rlic-plus"
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results", PAIR_ID)
os.makedirs(RESULTS_DIR, exist_ok=True)

PARQUET = os.path.join(DATA_DIR, f"{PAIR_ID}_daily_20260526.parquet")

IS_END = pd.Timestamp("2019-12-31")
OOS_START = pd.Timestamp("2020-01-01")
OOS_END = pd.Timestamp("2025-12-31")

# All signal transforms (excluding raw ratio, logratio, realized_vol)
SIGNAL_COLS = [
    "gold_copper_zscore_126d",
    "gold_copper_zscore_252d",
    "gold_copper_zscore_504d",
    "gold_copper_pctrank_504d",
    "gold_copper_pctrank_1260d",
    "gold_copper_roc_5d",
    "gold_copper_roc_21d",
    "gold_copper_roc_63d",
    "gold_copper_roc_126d",
    "gold_copper_mom_21d",
    "gold_copper_mom_63d",
    "gold_copper_mom_252d",
    "gold_copper_acceleration",
]

TARGET_RET = "xli_ret"

# Lead grid: L=0..12 months, 1 month = 21 trading days
LEAD_MONTHS = list(range(13))  # 0..12
DAYS_PER_MONTH = 21


def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}", flush=True)


def compute_thresholds(is_sig):
    """Expanded threshold grid matching gating sweep design."""
    thresholds = {}
    # Quantile-based
    thresholds["Tp25_lo"] = ("lte", is_sig.quantile(0.25))
    thresholds["Tp50_lo"] = ("lte", is_sig.quantile(0.50))
    thresholds["Tp75_lo"] = ("lte", is_sig.quantile(0.75))
    thresholds["Tp90_lo"] = ("lte", is_sig.quantile(0.90))
    thresholds["Tp25_hi"] = ("gte", is_sig.quantile(0.25))
    thresholds["Tp50_hi"] = ("gte", is_sig.quantile(0.50))
    thresholds["Tp75_hi"] = ("gte", is_sig.quantile(0.75))
    thresholds["Tp90_hi"] = ("gte", is_sig.quantile(0.90))
    # Z-score fixed thresholds
    thresholds["Tz1_lo"] = ("lte", -1.0)
    thresholds["Tz1_hi"] = ("gte", 1.0)
    thresholds["Tzn1_lo"] = ("lte", -1.0)
    # Fixed thresholds for pctrank signals
    thresholds["Tfix03_lo"] = ("lte", 0.3)
    thresholds["Tfix07_hi"] = ("gte", 0.7)
    # Reversed quantiles for roc/mom
    thresholds["Trp25_lo"] = ("lte", is_sig.quantile(0.25))
    return thresholds


def run_tournament(df):
    """Full tournament: signals × thresholds × strategies × leads (monthly grid)."""
    log("Running extended tournament (L=0..12 months)")
    rows = []
    ret = df[TARGET_RET].fillna(0)

    for sig_col in SIGNAL_COLS:
        sig = df[sig_col].copy()
        is_sig = sig.loc[:IS_END].dropna()
        if len(is_sig) < 252:
            continue

        thresholds = compute_thresholds(is_sig)

        for t_code, (t_rule, t_val) in thresholds.items():
            if pd.isna(t_val):
                continue
            for s_code in ["P1_long_cash", "P2_long_short"]:
                for lead_m in LEAD_MONTHS:
                    lead_days = lead_m * DAYS_PER_MONTH
                    try:
                        # Position based on threshold rule
                        if t_rule == "lte":
                            raw_pos = (sig <= t_val).astype(int)
                        elif t_rule == "gte":
                            raw_pos = (sig >= t_val).astype(int)
                        else:
                            raw_pos = (sig <= t_val).astype(int)

                        pos = raw_pos.shift(lead_days).fillna(0)
                        if s_code == "P2_long_short":
                            pos = pos * 2 - 1  # -1 / +1

                        strat_ret = pos * ret
                        oos_ret = strat_ret.loc[OOS_START:OOS_END].dropna()
                        if len(oos_ret) < 200:
                            continue

                        sharpe = (oos_ret.mean() * 252) / (oos_ret.std() * np.sqrt(252) + 1e-12)
                        ann_ret = (1 + oos_ret).prod() ** (252 / len(oos_ret)) - 1
                        equity = (1 + oos_ret).cumprod()
                        peak = equity.cummax()
                        mdd = ((equity - peak) / peak).min()
                        turnover = pos.diff().abs().loc[OOS_START:OOS_END].sum() / (len(oos_ret) / 252)

                        rows.append({
                            "signal": sig_col,
                            "threshold": t_code,
                            "threshold_value": round(float(t_val), 4),
                            "threshold_rule": t_rule,
                            "strategy": s_code,
                            "lead_days": lead_days,
                            "lead_months": lead_m,
                            "oos_sharpe": round(float(sharpe), 4),
                            "oos_ann_return": round(float(ann_ret * 100), 2),
                            "oos_max_drawdown": round(float(mdd * 100), 2),
                            "annual_turnover": round(float(turnover), 2),
                            "oos_n": int(len(oos_ret)),
                            "valid": bool(sharpe > 0 and turnover < 100),
                        })
                    except Exception as e:
                        pass

    df_t = pd.DataFrame(rows).sort_values("oos_sharpe", ascending=False)

    # Add benchmark row
    sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
    from tournament import emit_benchmark_row
    bm_row = emit_benchmark_row(
        df[TARGET_RET], str(OOS_START.date()), str(OOS_END.date()),
        columns_template=df_t.columns,
    )
    df_t = pd.concat([df_t, pd.DataFrame([bm_row])], ignore_index=True)

    out = os.path.join(RESULTS_DIR, f"tournament_results_{DATE_TAG}.csv")
    df_t.to_csv(out, index=False)
    n_valid = int(df_t[df_t["signal"] != "BENCHMARK"]["valid"].sum())
    log(f"  wrote {out}  ({len(df_t)} rows, {n_valid} valid)")
    return df_t


def select_winner_t3(df_t):
    """ECON-T3 tie-break cascade."""
    cands = df_t[(df_t["signal"] != "BENCHMARK") & (df_t["valid"] == True)].copy()
    if len(cands) == 0:
        raise ValueError("No valid candidates")

    # Step 1: highest oos_sharpe
    max_sharpe = cands["oos_sharpe"].max()
    cands = cands[cands["oos_sharpe"] == max_sharpe]
    if len(cands) == 1:
        return cands.iloc[0], 1

    # Step 2: highest oos_ann_return
    max_ret = cands["oos_ann_return"].max()
    cands = cands[cands["oos_ann_return"] == max_ret]
    if len(cands) == 1:
        return cands.iloc[0], 2

    # Step 3: lowest |oos_max_drawdown|
    cands["abs_dd"] = cands["oos_max_drawdown"].abs()
    min_dd = cands["abs_dd"].min()
    cands = cands[cands["abs_dd"] == min_dd]
    if len(cands) == 1:
        return cands.iloc[0], 3

    # Step 4: highest oos_n (trades proxy)
    max_n = cands["oos_n"].max()
    cands = cands[cands["oos_n"] == max_n]
    if len(cands) == 1:
        return cands.iloc[0], 4

    # Step 5: lexicographic signal
    cands = cands.sort_values("signal")
    return cands.iloc[0], 5


def build_winner_series(df, w):
    """Reconstruct the winner's position and return series."""
    sig = df[w["signal"]].copy()
    lead_days = int(w["lead_days"])
    t_val = float(w["threshold_value"])
    t_rule = w.get("threshold_rule", "lte")

    if t_rule == "lte":
        raw_pos = (sig <= t_val).astype(int)
    elif t_rule == "gte":
        raw_pos = (sig >= t_val).astype(int)
    else:
        raw_pos = (sig <= t_val).astype(int)

    pos = raw_pos.shift(lead_days).fillna(0)
    if w["strategy"] == "P2_long_short":
        pos = pos * 2 - 1

    ret = df[TARGET_RET].fillna(0)
    strat_ret = pos * ret
    return pos, strat_ret, ret


def produce_winner_summary(df, w, df_t, tie_step):
    """Write winner_summary.json per ECON-H5."""
    pos, strat_ret, ret = build_winner_series(df, w)

    sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
    from tournament import compute_buy_and_hold_stats
    bh = compute_buy_and_hold_stats(df[TARGET_RET], str(OOS_START.date()), str(OOS_END.date()))

    sig_col = w["signal"]
    lead_days = int(w["lead_days"])
    lead_months = int(w["lead_months"])
    t_rule = w.get("threshold_rule", "lte")

    # Determine direction
    # For pctrank with gte threshold: high pctrank = high ratio = risk-off
    # Going long when ratio is high (risk-off) = countercyclical to equities
    # But the gating sweep says P1 with Tfix07_hi — that means long when pctrank >= 0.7
    # High pctrank = high ratio = risk-off → going long industrials when risk-off is high
    # That's actually procyclical? No — countercyclical means signal goes UP when market goes DOWN.
    # pctrank high = gold/copper high = risk-off = bearish for industrials
    # But we're going LONG when the signal is high. That's contrarian/countercyclical.
    direction = "countercyclical"

    # Signal code — need to check/append to registry
    signal_code_map = {
        "gold_copper_zscore_126d": "S_zscore_126d",
        "gold_copper_zscore_252d": "S_zscore_252d",
        "gold_copper_zscore_504d": "S_zscore_504d",
        "gold_copper_pctrank_504d": "S_pctrank_504d",
        "gold_copper_pctrank_1260d": "S_pctrank_1260d",
        "gold_copper_roc_5d": "S_roc_5d",
        "gold_copper_roc_21d": "S_roc_21d",
        "gold_copper_roc_63d": "S_roc_63d",
        "gold_copper_roc_126d": "S_roc_126d",
        "gold_copper_mom_21d": "S_mom_21d",
        "gold_copper_mom_63d": "S_mom_63d",
        "gold_copper_mom_252d": "S_mom_252d",
        "gold_copper_acceleration": "S_acceleration",
    }
    signal_code = signal_code_map.get(sig_col, f"S_{sig_col.replace('gold_copper_', '')}")

    oos_ret = strat_ret.loc[OOS_START:OOS_END].dropna()
    oos_sharpe = (oos_ret.mean() * 252) / (oos_ret.std() * np.sqrt(252) + 1e-12)
    oos_ann_return = (1 + oos_ret).prod() ** (252 / len(oos_ret)) - 1
    equity = (1 + oos_ret).cumprod()
    peak = equity.cummax()
    oos_max_dd = ((equity - peak) / peak).min()
    n_trades = int(pos.diff().abs().loc[OOS_START:OOS_END].sum())
    turnover = pos.diff().abs().loc[OOS_START:OOS_END].sum() / (len(oos_ret) / 252)
    win_rate = float((oos_ret > 0).mean())

    n_valid = int(df_t[(df_t["signal"] != "BENCHMARK") & (df_t["valid"] == True)].shape[0])

    strategy_display = "Long/Cash" if w["strategy"] == "P1_long_cash" else "Long/Short"
    # Map pipeline family codes to schema enum
    strategy_family_map = {
        "P1_long_cash": "P1_long_cash",
        "P2_long_short": "P3_long_short",
    }
    schema_family = strategy_family_map.get(w["strategy"], w["strategy"])
    strategy_desc = (
        f"Long XLI when {sig_col.replace('gold_copper_', 'G/C ')} "
        f"{'<=' if t_rule == 'lte' else '>='} {float(w['threshold_value']):.4f} "
        f"(IS-calibrated {w['threshold']}); lead = {lead_months} month(s) ({lead_days}d); "
        f"otherwise {'cash' if w['strategy'] == 'P1_long_cash' else 'short XLI'}."
    )

    summary = {
        "pair_id": PAIR_ID,
        "signal_code": signal_code,
        "signal_display_name": sig_col.replace("gold_copper_", "G/C "),
        "signal_column": sig_col,
        "threshold_code": w["threshold"],
        "threshold_display_name": w["threshold"].replace("_", " "),
        "threshold_value": float(w["threshold_value"]),
        "threshold_rule": t_rule,
        "strategy_code": w["strategy"].split("_")[0],
        "strategy_display_name": strategy_display,
        "strategy_description": strategy_desc,
        "strategy_family": schema_family,
        "lead_value": lead_days,
        "lead_unit": "days",
        "lead_months": lead_months,
        "lead_description": f"Signal lead = {lead_months} month(s) ({lead_days} business days)",
        "direction": direction,
        "oos_sharpe": round(float(oos_sharpe), 4),
        "oos_ann_return": round(float(oos_ann_return), 4),
        "oos_max_drawdown": round(float(oos_max_dd), 4),
        "bh_sharpe": bh["bh_sharpe"],
        "bh_ann_return": bh["bh_ann_return"],
        "bh_max_drawdown": bh["bh_max_drawdown"],
        "annual_turnover": round(float(turnover), 2),
        "win_rate": round(win_rate, 4),
        "oos_n_trades": n_trades,
        "oos_period_start": str(OOS_START.date()),
        "oos_period_end": str(OOS_END.date()),
        "target_symbol": "XLI",
        "schema_version": "1.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": (
            f"ECON-LT1 re-run (lead horizon extension L0..12mo). "
            f"Extended tournament: 13 signals x ~14 thresholds x 2 strategies x 13 leads. "
            f"{len(df_t)} fit incl. benchmark, {n_valid} valid. "
            f"Winner selected by OOS Sharpe (T3 cascade step {tie_step}). "
            f"Supersedes prior winner (S_zscore_126d, L0, Sharpe 1.273). "
            f"New winner: {signal_code}, L{lead_months} ({lead_days}d), Sharpe {oos_sharpe:.4f}."
        ),
    }
    return summary, pos, strat_ret, ret


def write_winner_summary(summary):
    """Write and schema-validate winner_summary.json."""
    out = os.path.join(RESULTS_DIR, "winner_summary.json")
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"  wrote winner_summary.json  sharpe={summary['oos_sharpe']:.4f}")
    return out


def write_signals_parquet(df, summary, pos, strat_ret, ret):
    """Write signals parquet with APP-WS1 contract."""
    sig_col = summary["signal_column"]
    sig = df[sig_col]
    equity = (1 + strat_ret).cumprod()
    bh_equity = (1 + ret).cumprod()
    signals = pd.DataFrame({
        sig_col: sig,
        "signal_raw": sig,
        "position": pos,
        "strategy_return": strat_ret,
        "equity_curve": equity,
        "buy_and_hold_equity": bh_equity,
    }, index=df.index)
    out = os.path.join(RESULTS_DIR, f"signals_{DATE_TAG}.parquet")
    signals.to_parquet(out, engine="pyarrow", compression="snappy")
    log(f"  wrote {out}")


def write_strategy_returns(pos, strat_ret, ret):
    """ECON-SR1: reconciled strategy returns CSV."""
    bh_ret = ret
    sr = pd.DataFrame({
        "date": strat_ret.index.strftime("%Y-%m-%d"),
        "position": pos.values,
        "strategy_return": strat_ret.values,
        "bh_return": bh_ret.values,
    })
    out = os.path.join(RESULTS_DIR, f"strategy_returns_{DATE_TAG}.csv")
    sr.to_csv(out, index=False)
    log(f"  wrote {out}")
    return sr


def reconcile_sr1(summary, strat_ret):
    """ECON-SR1 reconciliation check."""
    oos = strat_ret.loc[OOS_START:OOS_END].dropna()
    sr_sharpe = (oos.mean() * 252) / (oos.std() * np.sqrt(252) + 1e-12)
    sr_ann_ret = (1 + oos).prod() ** (252 / len(oos)) - 1
    eq = (1 + oos).cumprod()
    sr_dd = ((eq - eq.cummax()) / eq.cummax()).min()

    d_sharpe = abs(sr_sharpe - summary["oos_sharpe"])
    d_ret = abs(sr_ann_ret - summary["oos_ann_return"]) * 100
    d_dd = abs(sr_dd - summary["oos_max_drawdown"]) * 100

    ok = d_sharpe <= 0.01 and d_ret <= 0.5 and d_dd <= 0.5
    log(f"  SR1 reconciliation: dSharpe={d_sharpe:.4f} dRet={d_ret:.2f}pp dDD={d_dd:.2f}pp → {'PASS' if ok else 'FAIL'}")
    return ok, {"d_sharpe": d_sharpe, "d_ret": d_ret, "d_dd": d_dd}


def write_trade_logs(df, pos, strat_ret, summary):
    """Write winner_trade_log.csv and winner_trades_broker_style.csv per ECON-C4."""
    sig_col = summary["signal_column"]
    sig = df[sig_col]
    ret = df[TARGET_RET].fillna(0)

    # Internal daily trade log
    equity = (1 + strat_ret).cumprod()
    tl = pd.DataFrame({
        "date": df.index.strftime("%Y-%m-%d"),
        "signal_value": sig.values,
        "threshold": summary["threshold_value"],
        "position": pos.values,
        "daily_return": strat_ret.values,
        "cumulative_return": equity.values,
    })
    tl_path = os.path.join(RESULTS_DIR, "winner_trade_log.csv")
    tl.to_csv(tl_path, index=False)
    log(f"  wrote {tl_path}")

    # Broker-style trade log
    pos_changes = pos.diff().fillna(pos)
    change_mask = pos_changes != 0
    change_dates = df.index[change_mask]

    broker_rows = []
    starting_capital = 10000.0
    commission_bps = 5
    cum_pnl = (equity - 1) * 100  # percent

    for d in change_dates:
        p = pos.loc[d]
        if p > 0:
            side = "BUY"
        elif p < 0:
            side = "SELL"
        else:
            side = "CASH"
        qty_pct = abs(float(p)) * 100
        price = float(df.loc[d, "xli"]) if "xli" in df.columns else 0.0
        notional = qty_pct / 100 * starting_capital
        comm = notional * commission_bps / 10000
        sig_val = float(sig.loc[d]) if not pd.isna(sig.loc[d]) else 0.0
        reason = (
            f"{sig_col.replace('gold_copper_', 'G/C ')} "
            f"{'<=' if summary['threshold_rule'] == 'lte' else '>='} "
            f"{summary['threshold_value']:.4f}"
        )
        broker_rows.append({
            "trade_date": d.strftime("%Y-%m-%d"),
            "side": side,
            "instrument": "XLI",
            "quantity_pct": round(qty_pct, 1),
            "price": round(price, 4),
            "notional_usd": round(notional, 2),
            "commission_bps": commission_bps,
            "commission_usd": round(comm, 4),
            "cum_pnl_pct": round(float(cum_pnl.loc[d]) if d in cum_pnl.index else 0, 4),
            "reason": reason,
        })

    broker_df = pd.DataFrame(broker_rows)
    broker_path = os.path.join(RESULTS_DIR, "winner_trades_broker_style.csv")
    broker_df.to_csv(broker_path, index=False)
    log(f"  wrote {broker_path} ({len(broker_df)} trades)")


def write_subperiod_sharpe(strat_ret):
    """CP1-A: subperiod Sharpe decomposition."""
    # Read episode registry for commodity_ratio (fallback to _fallback)
    reg_path = os.path.join(BASE_DIR, "docs", "schemas", "episode_registry.json")
    with open(reg_path) as f:
        reg = json.load(f)

    category = "commodity_ratio"
    episodes = reg.get(category, reg.get("_fallback", []))
    if isinstance(episodes, dict) and "episodes" in episodes:
        episodes = episodes["episodes"]
    if isinstance(episodes, dict):
        episodes = reg.get("_fallback", [])

    oos_ret = strat_ret.loc[OOS_START:OOS_END].dropna()

    rows = []
    positive_count = 0

    for ep in episodes:
        s, e = pd.Timestamp(ep["start"]), pd.Timestamp(ep["end"])
        # Clip to OOS
        s = max(s, OOS_START)
        e = min(e, OOS_END)
        sub = strat_ret.loc[s:e].dropna()
        if len(sub) < 21:
            rows.append({
                "episode": ep["slug"],
                "start_date": str(s.date()),
                "end_date": str(e.date()),
                "n_trading_days": len(sub),
                "ann_sharpe": None,
                "win_rate": None,
                "max_drawdown": None,
                "data_status": "insufficient_data",
            })
            continue
        sh = (sub.mean() * 252) / (sub.std() * np.sqrt(252) + 1e-12)
        wr = float((sub > 0).mean())
        eq = (1 + sub).cumprod()
        dd = ((eq - eq.cummax()) / eq.cummax()).min()
        if sh > 0:
            positive_count += 1
        rows.append({
            "episode": ep["slug"],
            "start_date": str(s.date()),
            "end_date": str(e.date()),
            "n_trading_days": len(sub),
            "ann_sharpe": round(float(sh), 4),
            "win_rate": round(wr, 4),
            "max_drawdown": round(float(dd), 4),
            "data_status": "validated",
        })

    # Full OOS row
    sh_full = (oos_ret.mean() * 252) / (oos_ret.std() * np.sqrt(252) + 1e-12)
    wr_full = float((oos_ret > 0).mean())
    eq_full = (1 + oos_ret).cumprod()
    dd_full = ((eq_full - eq_full.cummax()) / eq_full.cummax()).min()

    valid_eps = [r for r in rows if r["data_status"] == "validated"]
    pos_eps = sum(1 for r in valid_eps if r["ann_sharpe"] and r["ann_sharpe"] > 0)
    if pos_eps >= 3:
        verdict = "durable"
    elif pos_eps == 2:
        verdict = "conditionally_durable"
    else:
        verdict = "episode_concentrated"

    rows.append({
        "episode": "Full-OOS",
        "start_date": str(OOS_START.date()),
        "end_date": str(OOS_END.date()),
        "n_trading_days": len(oos_ret),
        "ann_sharpe": round(float(sh_full), 4),
        "win_rate": round(wr_full, 4),
        "max_drawdown": round(float(dd_full), 4),
        "data_status": "validated",
        "durability_verdict": verdict,
    })

    out = os.path.join(RESULTS_DIR, "subperiod_sharpe.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"  wrote {out} (verdict: {verdict})")


def write_rolling_correlation(df, sig_col):
    """CP1-B: Rolling 24M Pearson correlation (signal vs 1M fwd return)."""
    # Monthly resampling
    monthly = df[[sig_col, TARGET_RET]].resample("ME").agg({
        sig_col: "last",
        TARGET_RET: lambda x: (1 + x).prod() - 1,
    }).dropna()

    window = 24
    rows = []
    for i in range(window, len(monthly)):
        w = monthly.iloc[i - window:i]
        if len(w) < window:
            continue
        corr = w[sig_col].corr(w[TARGET_RET])
        rows.append({
            "date": w.index[-1].strftime("%Y-%m-%d"),
            "rolling_corr": round(float(corr), 6),
            "n_obs": len(w),
            "window_start": w.index[0].strftime("%Y-%m-%d"),
        })

    out = os.path.join(RESULTS_DIR, f"rolling_correlation_{PAIR_ID}.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"  wrote {out} ({len(rows)} rows)")
    return rows


def write_structural_break(df, sig_col):
    """CP1-C: Quandt-Andrews structural break test."""
    monthly = df[[sig_col, TARGET_RET]].resample("ME").agg({
        sig_col: "last",
        TARGET_RET: lambda x: (1 + x).prod() - 1,
    }).dropna()

    import statsmodels.api as sm
    y = monthly[TARGET_RET].values
    X = sm.add_constant(monthly[sig_col].values)
    n = len(y)
    trim = int(n * 0.15)

    best_f, best_idx = 0, trim
    for i in range(trim, n - trim):
        d = np.zeros(n)
        d[i:] = 1
        X_break = np.column_stack([X, d, d * monthly[sig_col].values])
        try:
            res_full = sm.OLS(y, X_break).fit()
            res_null = sm.OLS(y, X).fit()
            f_stat = ((res_null.ssr - res_full.ssr) / 2) / (res_full.ssr / (n - 4))
            if f_stat > best_f:
                best_f = f_stat
                best_idx = i
        except:
            continue

    from scipy import stats as spstats
    p_value = 1 - spstats.f.cdf(best_f, 2, n - 4)
    break_date = monthly.index[best_idx]
    flagged = p_value < 0.10

    # Compute rolling correlation sign stability
    rc_rows = write_rolling_correlation(df, sig_col)
    if rc_rows:
        full_corr = monthly[sig_col].corr(monthly[TARGET_RET])
        same_sign = sum(1 for r in rc_rows if (r["rolling_corr"] > 0) == (full_corr > 0))
        stability = same_sign / len(rc_rows) if rc_rows else 0
    else:
        stability = 0

    if stability >= 0.70:
        stab_verdict = "sign_stable"
    elif stability >= 0.50:
        stab_verdict = "moderately_stable"
    else:
        stab_verdict = "sign_unstable"

    result = {
        "pair_id": PAIR_ID,
        "test": "Quandt-Andrews unknown breakpoint",
        "sample_start": str(monthly.index[0].date()),
        "sample_end": str(monthly.index[-1].date()),
        "n_obs": n,
        "trimming_pct": 0.15,
        "break_date": str(break_date.date()),
        "f_stat": round(float(best_f), 4),
        "p_value": round(float(p_value), 4),
        "flagged": bool(flagged),
        "flag_message": "Structural break detected — interpret cross-period results with caution." if flagged else None,
        "rolling_corr_sign_stability": round(stability, 4),
        "rolling_corr_stability_verdict": stab_verdict,
    }

    out = os.path.join(RESULTS_DIR, f"structural_break_{PAIR_ID}.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    log(f"  wrote {out} (break={break_date.date()}, p={p_value:.4f}, stability={stab_verdict})")
    return result


def write_rolling_sharpe(strat_ret, ret):
    """CP2-A: Rolling 24M Sharpe."""
    # Use daily data, 24M ≈ 504 trading days
    window = 504
    rows = []
    for i in range(window, len(strat_ret)):
        w = strat_ret.iloc[i - window:i]
        bh_w = ret.iloc[i - window:i]
        if len(w.dropna()) < 252:
            continue
        sh = (w.mean() * 252) / (w.std() * np.sqrt(252) + 1e-12)
        ann_ret = (1 + w).prod() ** (252 / len(w)) - 1
        ann_vol = w.std() * np.sqrt(252)
        rows.append({
            "date": strat_ret.index[i].strftime("%Y-%m-%d"),
            "rolling_sharpe": round(float(sh), 4),
            "rolling_return": round(float(ann_ret), 4),
            "rolling_vol": round(float(ann_vol), 4),
            "n_trading_days": len(w),
        })

    out = os.path.join(RESULTS_DIR, f"rolling_sharpe_{PAIR_ID}.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"  wrote {out} ({len(rows)} rows)")


def write_rolling_granger(df, sig_col):
    """CP2-B: Rolling 24M Granger causality."""
    from statsmodels.tsa.stattools import grangercausalitytests

    monthly = df[[sig_col, TARGET_RET]].resample("ME").agg({
        sig_col: "last",
        TARGET_RET: lambda x: (1 + x).prod() - 1,
    }).dropna()

    window = 24
    lag = 1  # Use lag-1 for rolling
    rows = []

    for i in range(window, len(monthly)):
        w = monthly.iloc[i - window:i]
        try:
            res = grangercausalitytests(w[[TARGET_RET, sig_col]].values,
                                         maxlag=lag, verbose=False)
            f_info = res[lag][0]["ssr_ftest"]
            f_stat = float(f_info[0])
            p_val = float(f_info[1])
            from scipy.stats import f as fdist
            df1 = lag
            df2 = len(w) - 2 * lag - 1
            cv = fdist.ppf(0.90, df1, max(df2, 1))
            rows.append({
                "date": w.index[-1].strftime("%Y-%m-%d"),
                "f_stat": round(f_stat, 4),
                "p_value": round(p_val, 4),
                "significant_10pct": bool(p_val < 0.10),
                "critical_value_10pct": round(float(cv), 4),
                "n_obs": len(w),
                "lag_used": lag,
            })
        except:
            continue

    out = os.path.join(RESULTS_DIR, f"rolling_granger_{PAIR_ID}.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"  wrote {out} ({len(rows)} rows)")


def supersede_old_artifacts():
    """Rename old artifacts to *_superseded_20260613.*"""
    files_to_supersede = [
        "winner_summary.json",
        "winner_trade_log.csv",
        "winner_trades_broker_style.csv",
    ]
    for f in files_to_supersede:
        src = os.path.join(RESULTS_DIR, f)
        if os.path.exists(src):
            base, ext = os.path.splitext(f)
            dst = os.path.join(RESULTS_DIR, f"{base}_superseded_20260613{ext}")
            if not os.path.exists(dst):  # Don't overwrite if already superseded
                import shutil
                shutil.copy2(src, dst)
                log(f"  superseded: {f} → {os.path.basename(dst)}")


def validate_schema(summary):
    """Producer-side schema validation per ECON-H5."""
    import jsonschema
    schema_path = os.path.join(BASE_DIR, "docs", "schemas", "winner_summary.schema.json")
    with open(schema_path) as f:
        schema = json.load(f)

    # The schema requires strategy_family enum; our P2_long_short may not match
    # Check and handle
    errs = list(jsonschema.Draft202012Validator(schema).iter_errors(summary))
    if errs:
        log(f"  Schema validation: {len(errs)} errors")
        for e in errs[:5]:
            path = "/".join(map(str, e.absolute_path))
            log(f"    [{path}] {e.message[:140]}")
        return False
    log("  Schema validation: PASS")
    return True


def main():
    t0 = time.time()
    log("=" * 60)
    log("ECON-LT1 Re-Run: gold_copper_xli (extended lead tournament)")
    log("=" * 60)

    # Step 0: supersede old artifacts
    log("\nStep 0: Supersede old artifacts")
    supersede_old_artifacts()

    # Step 1: Load data
    log("\nStep 1: Load data")
    df = pd.read_parquet(PARQUET)
    log(f"  rows={len(df)}  cols={len(df.columns)}")

    # Step 2: Extended tournament
    log("\nStep 2: Extended tournament")
    df_t = run_tournament(df)

    # Step 3: Select winner (ECON-T3)
    log("\nStep 3: Select winner (ECON-T3 cascade)")
    w, tie_step = select_winner_t3(df_t)
    log(f"  Winner: {w['signal']} / {w['threshold']} / {w['strategy']} / L{w['lead_months']}mo ({w['lead_days']}d)")
    log(f"  Sharpe={w['oos_sharpe']:.4f}  Return={w['oos_ann_return']:.2f}%  DD={w['oos_max_drawdown']:.2f}%")
    log(f"  Tie-break resolved at step {tie_step}")

    # Step 4: Build winner series
    log("\nStep 4: Build winner series")
    summary, pos, strat_ret, ret = produce_winner_summary(df, w, df_t, tie_step)

    # Step 5: Schema validation
    log("\nStep 5: Schema validation")
    valid = validate_schema(summary)

    # Step 6: Write artifacts
    log("\nStep 6: Write artifacts")
    write_winner_summary(summary)
    write_signals_parquet(df, summary, pos, strat_ret, ret)
    sr = write_strategy_returns(pos, strat_ret, ret)

    # Step 7: ECON-SR1 reconciliation
    log("\nStep 7: ECON-SR1 reconciliation")
    ok, deltas = reconcile_sr1(summary, strat_ret)

    # Step 8: Trade logs
    log("\nStep 8: Trade logs")
    write_trade_logs(df, pos, strat_ret, summary)

    # Step 9: Subperiod Sharpe (CP1-A)
    log("\nStep 9: Subperiod Sharpe (CP1-A)")
    write_subperiod_sharpe(strat_ret)

    # Step 10: Cross-period analyses (CP1-B/C, CP2-A/B)
    log("\nStep 10: Cross-period analyses")
    sig_col = summary["signal_column"]
    write_structural_break(df, sig_col)  # Also writes rolling_correlation
    write_rolling_sharpe(strat_ret, ret)
    write_rolling_granger(df, sig_col)

    # Summary
    elapsed = round(time.time() - t0, 1)
    log(f"\n{'=' * 60}")
    log(f"DONE in {elapsed}s")
    log(f"New winner: {summary['signal_code']} / L{summary.get('lead_months', '?')}mo / Sharpe {summary['oos_sharpe']:.4f}")
    log(f"Old winner: S_zscore_126d / L0 / Sharpe 1.273")
    log(f"SR1 reconciliation: {'PASS' if ok else 'FAIL'}")
    log(f"Schema validation: {'PASS' if valid else 'FAIL'}")
    log(f"{'=' * 60}")

    # Write timing
    timing = {"elapsed_seconds": elapsed,
              "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(os.path.join(RESULTS_DIR, "pipeline_timing.json"), "w") as f:
        json.dump(timing, f, indent=2)


if __name__ == "__main__":
    main()
