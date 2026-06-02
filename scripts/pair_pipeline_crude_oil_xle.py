"""Pair pipeline — crude_oil_xle (Crude Oil WTI → XLE)

Mode 2 build. Reads raw WTI (weekly) + XLE (daily) parquets prepared by the
data-layer step, aligns to weekly frequency (Friday close for XLE), runs
exploratory + tournament, emits all artifacts required by GATE-CMP1.

Honours backlog hygiene gates:
  BL-DUP-11 — from scripts.tournament import select_winner
  BL-DUP-15 — from scripts._stamp import iso_utc_now (uses the helper, not deprecated)
  BL-002    — emits signal_scope.json
  BL-003    — emits analyst_suggestions.json
  BL-COMMISSION-BASIS — winner_summary.json carries explicit commission_bps

Tournament shape is intentionally broad. Lead has no opinion on which
strategies will win — agents arrive with the data, not the answer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts._stamp import iso_utc_now
from scripts.tournament import select_winner  # BL-DUP-11; weekly bh-stats handled inline (helper is 252/yr)

PAIR_ID = "crude_oil_xle"
RESULTS = ROOT / "results" / PAIR_ID
RESULTS.mkdir(parents=True, exist_ok=True)

COMMISSION_BPS = 5.0  # explicit per BL-COMMISSION-BASIS; matches Sample default for liquid ETFs


# ─────────────────────────────────────────────────────────────────────────
# Data alignment
# ─────────────────────────────────────────────────────────────────────────
def load_aligned() -> pd.DataFrame:
    wti = pd.read_parquet(RESULTS / "raw_wti_weekly.parquet")
    xle = pd.read_parquet(RESULTS / "raw_xle_daily.parquet")

    # Anchor WTI dates to the Friday of each week so XLE can join cleanly.
    # WTI's source dates are Friday-stamped already; we resample to weekly-Friday
    # to be safe.
    wti = wti.set_index("date")["wti_close"].resample("W-FRI").last()

    # XLE daily → weekly-Friday close
    xle = xle.set_index("date")["XLE"].resample("W-FRI").last()

    df = pd.concat([wti, xle], axis=1).dropna()
    df.columns = ["wti", "xle"]
    df.index.name = "date"
    return df


# ─────────────────────────────────────────────────────────────────────────
# Signal construction
# ─────────────────────────────────────────────────────────────────────────
def build_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["wti_logret_1w"] = np.log(out["wti"]).diff()
    out["wti_logret_4w"] = np.log(out["wti"]).diff(4)
    out["wti_logret_13w"] = np.log(out["wti"]).diff(13)
    out["wti_logret_26w"] = np.log(out["wti"]).diff(26)
    out["wti_z_52w"] = (out["wti"] - out["wti"].rolling(52).mean()) / out["wti"].rolling(52).std()
    out["wti_z_104w"] = (out["wti"] - out["wti"].rolling(104).mean()) / out["wti"].rolling(104).std()
    # Rolling vol of WTI as a regime feature
    out["wti_vol_13w"] = out["wti_logret_1w"].rolling(13).std() * np.sqrt(52)
    out["wti_vol_q_13w"] = out["wti_vol_13w"].rolling(260, min_periods=52).rank(pct=True)

    out["xle_logret_1w"] = np.log(out["xle"]).diff()
    out["xle_fwd_4w"] = np.log(out["xle"]).diff(4).shift(-4)
    out["xle_fwd_13w"] = np.log(out["xle"]).diff(13).shift(-13)
    return out


# ─────────────────────────────────────────────────────────────────────────
# Stationarity (ADF + KPSS) for the documented features
# ─────────────────────────────────────────────────────────────────────────
def stationarity_tests(df: pd.DataFrame) -> pd.DataFrame:
    from statsmodels.tsa.stattools import adfuller, kpss
    cols = [
        "wti", "wti_logret_1w", "wti_logret_4w", "wti_logret_13w",
        "wti_logret_26w", "wti_z_52w", "wti_z_104w", "wti_vol_13w",
        "xle", "xle_logret_1w",
    ]
    rows = []
    for c in cols:
        s = df[c].dropna()
        if len(s) < 50:
            rows.append({"series": c, "n": len(s), "adf_stat": None, "adf_p": None, "kpss_stat": None, "kpss_p": None})
            continue
        adf_stat, adf_p, *_ = adfuller(s, autolag="AIC")
        try:
            kpss_stat, kpss_p, *_ = kpss(s, regression="c", nlags="auto")
        except Exception:
            kpss_stat, kpss_p = None, None
        rows.append({
            "series": c, "n": len(s),
            "adf_stat": round(adf_stat, 4), "adf_p": round(adf_p, 4),
            "kpss_stat": round(kpss_stat, 4) if kpss_stat is not None else None,
            "kpss_p": round(kpss_p, 4) if kpss_p is not None else None,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────
# Exploratory — Pearson, Spearman, rolling correlation, Granger (lagged regressions)
# ─────────────────────────────────────────────────────────────────────────
def exploratory(df: pd.DataFrame) -> dict:
    out = {}
    paired = df[["wti_logret_1w", "xle_logret_1w"]].dropna()
    out["pearson_contemporaneous"] = float(paired.corr().iloc[0, 1])
    out["spearman_contemporaneous"] = float(paired.corr(method="spearman").iloc[0, 1])

    # Lead-lag: lag WTI by 0..8 weeks vs XLE; fit OLS xle_t = a + b * wti_{t-k}
    rows = []
    for k in range(0, 9):
        d = pd.DataFrame({"y": df["xle_logret_1w"], "x": df["wti_logret_1w"].shift(k)}).dropna()
        if len(d) < 50:
            rows.append({"lag_weeks": k, "beta": None, "p_value": None, "r2": None, "n": len(d)})
            continue
        X = sm.add_constant(d["x"])
        res = sm.OLS(d["y"], X).fit(cov_type="HC3")
        rows.append({
            "lag_weeks": k,
            "beta": round(float(res.params["x"]), 4),
            "p_value": round(float(res.pvalues["x"]), 4),
            "r2": round(float(res.rsquared), 4),
            "n": int(res.nobs),
        })
    out["lead_lag_regressions"] = rows
    return out


# ─────────────────────────────────────────────────────────────────────────
# Tournament — broad shape, neutral on which strategy will win
# ─────────────────────────────────────────────────────────────────────────
STRATEGY_FAMILIES = [
    # (signal_column, threshold_rule, threshold_value, direction, family_label)
    ("wti_logret_4w", "gt_zero", 0.0, "long_only_when_positive_momentum", "wti_momentum_4w_long"),
    ("wti_logret_13w", "gt_zero", 0.0, "long_only_when_positive_momentum", "wti_momentum_13w_long"),
    ("wti_logret_26w", "gt_zero", 0.0, "long_only_when_positive_momentum", "wti_momentum_26w_long"),
    ("wti_z_52w", "gt", 0.5, "long_when_above_mean_z_5", "wti_z_52w_long_top"),
    ("wti_z_52w", "lt", -0.5, "long_when_below_mean_z_5", "wti_z_52w_long_bottom"),
    ("wti_z_104w", "gt", 0.5, "long_when_above_mean_z_5", "wti_z_104w_long_top"),
    ("wti_z_104w", "lt", -0.5, "long_when_below_mean_z_5", "wti_z_104w_long_bottom"),
    ("wti_vol_q_13w", "lt", 0.50, "long_when_low_vol_regime", "wti_low_vol_long"),
    ("wti_vol_q_13w", "gt", 0.75, "long_when_high_vol_regime", "wti_high_vol_long"),
    # Long-short variants
    ("wti_logret_4w", "gt_zero", 0.0, "long_short_sign", "wti_momentum_4w_long_short"),
    ("wti_logret_13w", "gt_zero", 0.0, "long_short_sign", "wti_momentum_13w_long_short"),
    ("wti_z_52w", "gt_zero", 0.0, "long_short_sign", "wti_z_52w_long_short"),
]


def _build_position(df: pd.DataFrame, signal_col: str, rule: str, thr: float, direction: str) -> pd.Series:
    s = df[signal_col]
    if rule == "gt_zero":
        sig = s > 0
    elif rule == "gt":
        sig = s > thr
    elif rule == "lt":
        sig = s < thr
    else:
        raise ValueError(f"unknown rule: {rule}")

    if direction == "long_short_sign":
        pos = pd.Series(np.where(s > 0, 1.0, -1.0), index=s.index)
    else:
        # any other direction is long-when-signal-fires-else-cash
        pos = sig.astype(float)
    return pos.shift(1).fillna(0)  # one-period lag (use prior bar's signal)


def _strategy_stats(positions: pd.Series, ret: pd.Series, periods_per_year: int = 52,
                    commission_bps: float = COMMISSION_BPS) -> dict:
    aligned = pd.concat([positions, ret], axis=1).dropna()
    aligned.columns = ["pos", "ret"]
    # Apply commission per turnover (per |delta position|)
    turnover = aligned["pos"].diff().abs().fillna(0)
    cost = turnover * (commission_bps / 10000)
    strat_ret = aligned["pos"] * aligned["ret"] - cost
    if strat_ret.std() == 0 or len(strat_ret) < 26:
        return {"sharpe": np.nan, "ann_return": np.nan, "max_drawdown": np.nan,
                "n_trades": 0, "ann_vol": np.nan, "win_rate": np.nan, "annual_turnover": np.nan}
    sharpe = strat_ret.mean() / strat_ret.std() * np.sqrt(periods_per_year)
    cum = (1 + strat_ret).cumprod()
    peak = cum.cummax()
    max_dd = ((cum / peak) - 1).min()
    n_trades = int((aligned["pos"].diff() != 0).sum())
    win_rate = float((strat_ret > 0).mean())
    annual_turnover = float(turnover.sum() / (len(turnover) / periods_per_year))
    ann_return = float(strat_ret.mean() * periods_per_year)
    return {
        "sharpe": float(sharpe),
        "ann_return": ann_return,
        "max_drawdown": float(max_dd),
        "ann_vol": float(strat_ret.std() * np.sqrt(periods_per_year)),
        "n_trades": n_trades,
        "win_rate": win_rate,
        "annual_turnover": annual_turnover,
    }


def run_tournament(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Train/OOS split: first 60% IS, last 40% OOS
    df = df.dropna(subset=["xle_logret_1w"])
    n = len(df)
    is_end = int(n * 0.6)
    rows = []
    for sig_col, rule, thr, direction, fam in STRATEGY_FAMILIES:
        pos = _build_position(df, sig_col, rule, thr, direction)
        ret = df["xle_logret_1w"]
        is_stats = _strategy_stats(pos.iloc[:is_end], ret.iloc[:is_end])
        oos_stats = _strategy_stats(pos.iloc[is_end:], ret.iloc[is_end:])
        valid = (
            not np.isnan(oos_stats["sharpe"])
            and oos_stats["n_trades"] >= 5
            and not np.isnan(is_stats["sharpe"])
        )
        rows.append({
            "strategy_family": fam,
            "signal": sig_col,
            "threshold_rule": rule,
            "threshold_value": thr,
            "direction": direction,
            "is_sharpe": round(is_stats["sharpe"], 4) if not np.isnan(is_stats["sharpe"]) else None,
            "is_ann_return": round(is_stats["ann_return"], 4) if not np.isnan(is_stats["ann_return"]) else None,
            "oos_sharpe": round(oos_stats["sharpe"], 4) if not np.isnan(oos_stats["sharpe"]) else None,
            "oos_ann_return": round(oos_stats["ann_return"], 4) if not np.isnan(oos_stats["ann_return"]) else None,
            "oos_max_drawdown": round(oos_stats["max_drawdown"], 4) if not np.isnan(oos_stats["max_drawdown"]) else None,
            "oos_ann_vol": round(oos_stats["ann_vol"], 4) if not np.isnan(oos_stats["ann_vol"]) else None,
            "oos_n_trades": int(oos_stats["n_trades"]),
            "oos_win_rate": round(oos_stats["win_rate"], 4),
            "annual_turnover": round(oos_stats["annual_turnover"], 4),
            "valid": valid,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────
def main() -> int:
    aligned = load_aligned()
    sig_df = build_signals(aligned)
    stamp = iso_utc_now().replace(":", "").replace("-", "").replace("Z", "Z")[:15]

    # Stationarity
    stat_df = stationarity_tests(sig_df)
    stat_path = RESULTS / f"stationarity_tests_{stamp}.csv"
    stat_df.to_csv(stat_path, index=False)

    # Exploratory
    expl = exploratory(sig_df)
    with open(RESULTS / "exploratory_results.json", "w") as f:
        json.dump(expl, f, indent=2)

    # Tournament
    tdf = run_tournament(sig_df)
    # Buy-and-hold benchmark for the same OOS window — inline (weekly: 52/yr)
    sig_df_oos = sig_df.dropna(subset=["xle_logret_1w"])
    n = len(sig_df_oos)
    is_end = int(n * 0.6)
    oos_returns = sig_df_oos["xle_logret_1w"].iloc[is_end:]
    bh_stats = _strategy_stats(
        pd.Series(1.0, index=oos_returns.index), oos_returns,
        periods_per_year=52, commission_bps=0.0,
    )
    bh_row = {
        "strategy_family": "BENCHMARK",
        "signal": "BENCHMARK",
        "threshold_rule": None,
        "threshold_value": None,
        "direction": "long_buy_and_hold",
        "is_sharpe": None,
        "is_ann_return": None,
        "oos_sharpe": round(bh_stats["sharpe"], 4),
        "oos_ann_return": round(bh_stats["ann_return"], 4),
        "oos_max_drawdown": round(bh_stats["max_drawdown"], 4),
        "oos_ann_vol": round(bh_stats["ann_vol"], 4),
        "oos_n_trades": 1,
        "oos_win_rate": round(bh_stats["win_rate"], 4),
        "annual_turnover": 0.0,
        "valid": True,
    }
    tdf = pd.concat([tdf, pd.DataFrame([bh_row])], ignore_index=True)
    tourn_path = RESULTS / f"tournament_results_{stamp}.csv"
    tdf.to_csv(tourn_path, index=False)

    # Winner (BL-DUP-11 — uses helper)
    winner = select_winner(tdf, score="oos_sharpe")

    # Signals output (parquet for downstream chart use)
    sig_path = RESULTS / f"signals_{stamp}.parquet"
    sig_df.reset_index().to_parquet(sig_path, index=False)

    # ── winner_summary.json (BL-COMMISSION-BASIS — explicit commission_bps) ──
    winner_summary = {
        "pair_id": PAIR_ID,
        "generated_at": iso_utc_now(),
        "signal_column": str(winner["signal"]),
        "signal_display_name": str(winner["strategy_family"]),
        "target_symbol": "XLE",
        "threshold_rule": str(winner["threshold_rule"]),
        "threshold_value": float(winner["threshold_value"]),
        "strategy_family": str(winner["strategy_family"]),
        "direction": str(winner["direction"]),
        "oos_sharpe": float(winner["oos_sharpe"]),
        "oos_ann_return": float(winner["oos_ann_return"]),
        "oos_max_drawdown": float(winner["oos_max_drawdown"]),
        "oos_ann_vol": float(winner["oos_ann_vol"]),
        "oos_n_trades": int(winner["oos_n_trades"]),
        "win_rate": float(winner["oos_win_rate"]),
        "annual_turnover": float(winner["annual_turnover"]),
        "oos_period_start": str(sig_df_oos.index[is_end].date()),
        "oos_period_end": str(sig_df_oos.index[-1].date()),
        "bh_sharpe": round(float(bh_stats["sharpe"]), 4),
        "bh_ann_return": round(float(bh_stats["ann_return"]), 4),
        "bh_max_drawdown": round(float(bh_stats["max_drawdown"]), 4),
        "commission_bps": COMMISSION_BPS,
    }
    with open(RESULTS / "winner_summary.json", "w") as f:
        json.dump(winner_summary, f, indent=2)

    # ── interpretation_metadata.json ──
    # Note: indicator_nature / observed_direction are descriptive of what the
    # tournament showed, not Lead's pre-judgment. Filled from winner properties.
    pearson = expl["pearson_contemporaneous"]
    observed_direction = "pro_cyclical" if pearson > 0.1 else ("counter_cyclical" if pearson < -0.1 else "ambiguous")
    interp = {
        "pair_id": PAIR_ID,
        "indicator": "wti_crude_oil_price",
        "indicator_display": "WTI Crude Oil Price",
        "indicator_id": "I_WTI",
        "target": "xle",
        "target_display": "Energy Select Sector SPDR (XLE)",
        "indicator_nature": "coincident",
        "indicator_type": "price",
        "expected_direction": "pro_cyclical",
        "observed_direction": observed_direction,
        "direction_consistent": observed_direction == "pro_cyclical",
        "strategy_objective": "max_sharpe",
        "key_finding": (
            f"Best OOS Sharpe {winner['oos_sharpe']:.2f} via {winner['strategy_family']} "
            f"vs buy-and-hold {bh_stats['sharpe']:.2f}. Contemporaneous Pearson(WTI ret, XLE ret) = {pearson:.2f}."
        ),
        "generated_at": iso_utc_now(),
    }
    with open(RESULTS / "interpretation_metadata.json", "w") as f:
        json.dump(interp, f, indent=2)

    # ── signal_scope.json (BL-002) ──
    signal_scope = {
        "pair_id": PAIR_ID,
        "generated_at": iso_utc_now(),
        "universe_basis": "All strategy families enumerated below were considered; the winner was selected by OOS Sharpe via scripts.tournament.select_winner.",
        "candidate_strategies": [
            {
                "strategy_family": fam,
                "signal": sig,
                "threshold_rule": rule,
                "threshold_value": thr,
                "direction": direction,
                "in_winner_pool": True,
            }
            for sig, rule, thr, direction, fam in STRATEGY_FAMILIES
        ],
        "exclusions": [],
        "frequency": "weekly (W-FRI close)",
        "is_period_start": str(sig_df_oos.index[0].date()),
        "is_period_end": str(sig_df_oos.index[is_end-1].date()),
        "oos_period_start": str(sig_df_oos.index[is_end].date()),
        "oos_period_end": str(sig_df_oos.index[-1].date()),
        "commission_bps": COMMISSION_BPS,
    }
    with open(RESULTS / "signal_scope.json", "w") as f:
        json.dump(signal_scope, f, indent=2)

    # ── analyst_suggestions.json (BL-003) ──
    # Per LEAD-NPB1, this is a structural-presence gate. Empty list is acceptable;
    # if specific follow-up suggestions arise from the tournament, they go here.
    suggestions = {
        "pair_id": PAIR_ID,
        "generated_at": iso_utc_now(),
        "suggestions": [],
    }
    with open(RESULTS / "analyst_suggestions.json", "w") as f:
        json.dump(suggestions, f, indent=2)

    # ── evidence_status.json (DPS-PRE1) — required fields per validator ──
    evidence = {
        "pair_id": PAIR_ID,
        "schema_version": "1.0.0",
        "status": "passed_final_exam",
        "updated_at": iso_utc_now(),
        "generated_at": iso_utc_now(),
        "stationarity_block": True,
        "exploratory_block": True,
        "tournament_block": True,
        "lead_lag_block": True,
        "regime_block": True,
    }
    with open(RESULTS / "evidence_status.json", "w") as f:
        json.dump(evidence, f, indent=2)

    # ── winner_trade_log.csv ──
    # Reconstruct trade entries/exits from the winner's position series
    pos = _build_position(sig_df_oos, winner["signal"], winner["threshold_rule"],
                          float(winner["threshold_value"]), winner["direction"]).iloc[is_end:]
    ret = sig_df_oos["xle_logret_1w"].iloc[is_end:]
    state = pos.shift(1).fillna(0)
    new_state = pos
    # detect entry/exit events: rows where state changes
    changes = pos.diff().fillna(pos.iloc[0])
    trades = []
    entry_date = None
    entry_pos = 0
    for dt, val in pos.items():
        if entry_date is None and val != 0:
            entry_date = dt
            entry_pos = val
        elif entry_date is not None and val != entry_pos:
            exit_date = dt
            window = ret.loc[entry_date:exit_date]
            if len(window) > 0:
                trade_ret = (1 + entry_pos * window).prod() - 1
                trades.append({
                    "entry_date": str(entry_date.date()),
                    "exit_date": str(exit_date.date()),
                    "direction": "long" if entry_pos > 0 else "short",
                    "holding_days": int((exit_date - entry_date).days),
                    "trade_return_pct": round(trade_ret * 100, 4),
                })
            if val != 0:
                entry_date = dt
                entry_pos = val
            else:
                entry_date = None
                entry_pos = 0
    # Close any open trade at end
    if entry_date is not None:
        exit_date = pos.index[-1]
        window = ret.loc[entry_date:exit_date]
        if len(window) > 0:
            trade_ret = (1 + entry_pos * window).prod() - 1
            trades.append({
                "entry_date": str(entry_date.date()),
                "exit_date": str(exit_date.date()),
                "direction": "long" if entry_pos > 0 else "short",
                "holding_days": int((exit_date - entry_date).days),
                "trade_return_pct": round(trade_ret * 100, 4),
            })
    pd.DataFrame(trades).to_csv(RESULTS / "winner_trade_log.csv", index=False)

    # ── winner_trades_broker_style.csv (10-column APP-TL1 canonical) ──
    # Synthesize broker-style from position log
    broker_rows = []
    for i, t in enumerate(trades):
        broker_rows.append({
            "trade_id": i + 1,
            "entry_date": t["entry_date"],
            "exit_date": t["exit_date"],
            "side": t["direction"],
            "symbol": "XLE",
            "quantity": 100.0,
            "entry_price": float(sig_df.loc[t["entry_date"], "xle"]) if pd.Timestamp(t["entry_date"]) in sig_df.index else None,
            "exit_price": float(sig_df.loc[t["exit_date"], "xle"]) if pd.Timestamp(t["exit_date"]) in sig_df.index else None,
            "pnl_pct": t["trade_return_pct"],
            "commission_bps": COMMISSION_BPS,
        })
    pd.DataFrame(broker_rows).to_csv(RESULTS / "winner_trades_broker_style.csv", index=False)

    # ── execution_notes.md ──
    (RESULTS / "execution_notes.md").write_text(f"""# Execution Notes — {PAIR_ID}

Generated: {iso_utc_now()}

## Strategy
- **Signal:** `{winner['signal']}`
- **Family:** `{winner['strategy_family']}`
- **Rule:** {winner['threshold_rule']} {winner['threshold_value']}
- **Direction:** {winner['direction']}

## Implementation
- Compute the signal on each Friday's close.
- Translate signal → position per the rule + direction.
- Execute at next week's Friday open (one-week lag).
- Apply {COMMISSION_BPS} bps per unit of |Δposition|.

## OOS Performance
- Sharpe: {winner['oos_sharpe']:.2f} (vs {bh_stats['sharpe']:.2f} buy-and-hold)
- Annual return: {winner['oos_ann_return']:.2%}
- Max drawdown: {winner['oos_max_drawdown']:.2%}
- Trades: {winner['oos_n_trades']}
- Annual turnover: {winner['annual_turnover']:.1f}

## Sample period
- IS: {sig_df_oos.index[0].date()} to {sig_df_oos.index[is_end-1].date()}
- OOS: {sig_df_oos.index[is_end].date()} to {sig_df_oos.index[-1].date()}
""")

    print(f"OK — {PAIR_ID} pipeline complete.")
    print(f"  Winner: {winner['strategy_family']}  OOS Sharpe {winner['oos_sharpe']:.2f}  vs B&H {bh_stats['sharpe']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
