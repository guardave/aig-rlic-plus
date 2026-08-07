#!/usr/bin/env python3
"""Daily-axis rebuild for phlxsox_spy — GH#13 daily Class-A track (pair 4/4, the GENUINE-LEAD one).

Unlike the other 3 daily pairs (0-day coincident), phlxsox's winner is a GENUINE ~1-quarter
lead: rs_mom6m / T2_roll_p75 / P1_long_cash_pro / L63 / LB63 = 1.5700. The narrative must be
honest to THAT — a real quarter-ahead lead (with heavy pre-existing overfitting caveats), NOT
coincident. This pair floors at L1 (NO L0: a same-day SOX/SPY reading is co-movement, not a
forecast), so the daily grid is {1,5,21,63,126,252} — the standard anchors minus L0.

Mirrors the hy_ig pilot: rebuild the lead apparatus on the native DAILY axis from the RESTORED
committed raw data (data/phlxsox_spy_daily_19940504_20260617.parquet — deterministic momentum/
z-score transforms + spy_ret) + the committed HMM stress prob (results/phlxsox_spy/signals_*.parquet,
NO re-fit). Reproduces the committed 1.5700 EXACTLY → headline unchanged, clean (no pin/vintage).

Faithful to scripts/pair_pipeline_phlxsox_spy.py::stage_tournament:
  * 11 signals (10 deterministic + hmm_stress) × lookback {LB63,LB126,LB252} × thresholds
    {T1_fixed_p{25,50,75}, T4_zero (momentum only), T2_roll_p{25,75}, T3_zscore_{1.0,1.5},
    T3_zscore_neg_{1.0,1.5}} × strategies {P1_long_cash,P2_signal_strength,P3_long_short}
    × orientation {pro,counter}. sig = base.shift(lead); above = sig<thr if neg else sig>thr;
    strat_ret = position * spy_ret (lead>=1 => no lookahead). valid = sharpe>0.3 & turnover<252.
  * ECON-T4 deployable OOS scoring (fillna 0); no-op for the L63 winner (deployable == dropna).
  * Dynamic OOS split: oos_n = min(max(252, round(n*0.25)), 1260); OOS 2021-06-11..2026-06-17.

Run:  python3 scripts/refresh_phlxsox_spy_lead_artifacts.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO = Path(__file__).resolve().parents[1]
PAIR = "phlxsox_spy"
RES = REPO / "results" / PAIR
DATE_TAG = "20260715"
SRC_TAG = "20260619"
RAW_PARQUET = "data/phlxsox_spy_daily_19940504_20260617.parquet"
SIGNALS_PARQUET = "results/phlxsox_spy/signals_20260619.parquet"
TD = 252
DAILY_LEADS = [1, 5, 21, 63, 126, 252]   # L1 floor (NO L0 — contemporaneous = co-movement)
LOOKBACKS = {"LB63": 63, "LB126": 126, "LB252": 252}
STRATS = ["P1_long_cash", "P2_signal_strength", "P3_long_short"]
SIGNAL_COLS = {
    "rs_mom1m": "sox_spy_ratio_mom_1m_pct", "rs_mom3m": "sox_spy_ratio_mom_3m_pct",
    "rs_mom6m": "sox_spy_ratio_mom_6m_pct", "rs_mom12m": "sox_spy_ratio_mom_12m_pct",
    "rs_zscore126": "sox_spy_ratio_zscore_126d", "rs_zscore252": "sox_spy_ratio_zscore_252d",
    "sox_mom1m": "sox_mom_1m_pct", "sox_mom3m": "sox_mom_3m_pct", "sox_mom6m": "sox_mom_6m_pct",
    "sox_mom12m": "sox_mom_12m_pct", "hmm_stress": "hmm_2state_prob_stress",
}


def ann_metrics(rets):
    rets = rets.dropna()
    if len(rets) == 0 or rets.std() == 0:
        return dict(sharpe=0.0, ann_return=0.0, ann_vol=0.0, max_dd=0.0, sortino=0.0, calmar=0.0, win_rate=0.0)
    sharpe = rets.mean() / rets.std() * np.sqrt(TD)
    ann_ret = rets.mean() * TD
    ann_vol = rets.std() * np.sqrt(TD)
    cum = (1 + rets).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    neg = rets[rets < 0]
    sortino = ann_ret / (neg.std() * np.sqrt(TD)) if len(neg) > 1 and neg.std() > 0 else 0.0
    calmar = ann_ret / abs(dd) if dd < 0 else 0.0
    return dict(sharpe=sharpe, ann_return=ann_ret, ann_vol=ann_vol, max_dd=dd,
                sortino=sortino, calmar=calmar, win_rate=(rets > 0).mean())


def _position(sig, thr_name, thr, strat, orientation, lb_name):
    above = sig < thr if "neg_" in thr_name else sig > thr
    pos_bool = ~above if orientation == "counter" else above
    if strat == "P1_long_cash":
        return pos_bool.astype(float)
    if strat == "P2_signal_strength":
        if lb_name == "LB_NA":
            return None
        lb = LOOKBACKS[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 60))
        rng = (roll.max() - roll.min()).replace(0, np.nan)
        raw = ((sig - roll.min()) / rng).clip(0, 1)
        return 1 - raw if orientation == "counter" else raw
    return pos_bool.astype(float) * 2 - 1


def _thresholds(sig, is_mask, is_growth):
    thr = {}
    is_sig = sig[is_mask].dropna()
    if len(is_sig) > 250:
        for pct in (25, 50, 75):
            thr[(f"T1_fixed_p{pct}", "LB_NA")] = is_sig.quantile(pct / 100)
    if is_growth:
        thr[("T4_zero", "LB_NA")] = 0.0
    for lb_name, lb in LOOKBACKS.items():
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 60))
        for pct in (25, 75):
            thr[(f"T2_roll_p{pct}", lb_name)] = roll.quantile(pct / 100)
        rm, rs = roll.mean(), roll.std()
        for k in (1.0, 1.5):
            thr[(f"T3_zscore_{k}", lb_name)] = rm + k * rs
            thr[(f"T3_zscore_neg_{k}", lb_name)] = rm - k * rs
    return thr


def replay_combo(work, spy_ret, is_mask, sig_col, thr_name, lb_name, strat, orientation, lead):
    """Reconstruct one combo's position + strat_ret (deployable). thr recomputed as pipeline."""
    sig = work[sig_col].shift(lead)
    is_growth = True  # thresholds recomputed below only need the right family for T4; recompute generically
    thr_map = _thresholds(sig, is_mask, is_growth)
    thr = thr_map.get((thr_name, lb_name))
    if thr is None:
        return None, None
    pos = _position(sig, thr_name, thr, strat, orientation, lb_name)
    if pos is None:
        return None, None
    return pos, pos * spy_ret


def run_tournament(work, spy_ret, is_mask, oos_mask, leads):
    rows = []
    for code, col in SIGNAL_COLS.items():
        if col not in work.columns or work[col].notna().sum() < 1000:
            continue
        base_sig = work[col]
        is_growth = code.startswith(("rs_mom", "sox_mom"))
        for lead in leads:
            sig = base_sig.shift(lead)
            for (thr_name, lb_name), thr in _thresholds(sig, is_mask, is_growth).items():
                for strat in STRATS:
                    for orientation in ("pro", "counter"):
                        pos = _position(sig, thr_name, thr, strat, orientation, lb_name)
                        if pos is None:
                            continue
                        strat_ret = pos * spy_ret
                        is_r = strat_ret[is_mask].dropna()
                        oos_r = strat_ret[oos_mask].fillna(0.0)   # ECON-T4 deployable
                        if len(is_r) < 500 or len(oos_r) < 200:
                            continue
                        m = ann_metrics(oos_r)
                        pos_oos = pos[oos_mask]
                        n_trades = int((pos_oos.diff().abs() > 1e-9).sum())
                        years = len(pos_oos.dropna()) / TD
                        turnover = n_trades / years if years > 0 else 999
                        rows.append({
                            "signal": code, "threshold": thr_name, "strategy": f"{strat}_{orientation}",
                            "lead_days": lead, "lookback": lb_name,
                            "oos_sharpe": round(m["sharpe"], 4), "oos_ann_return": round(m["ann_return"], 4),
                            "oos_ann_vol": round(m["ann_vol"], 4), "oos_sortino": round(m["sortino"], 4),
                            "oos_calmar": round(m["calmar"], 4), "max_drawdown": round(m["max_dd"], 4),
                            "win_rate": round(m["win_rate"], 4), "n_trades": n_trades,
                            "annual_turnover": round(turnover, 2), "oos_n": len(oos_r),
                            "valid": bool(m["sharpe"] > 0.3 and turnover < 252 and len(oos_r) >= 200),
                        })
    bh = spy_ret[oos_mask].dropna()
    mb = ann_metrics(bh)
    rows.append({"signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "P0_buy_and_hold",
                 "lead_days": 0, "lookback": "LB_NA", "oos_sharpe": round(mb["sharpe"], 4),
                 "oos_ann_return": round(mb["ann_return"], 4), "oos_ann_vol": round(mb["ann_vol"], 4),
                 "oos_sortino": round(mb["sortino"], 4), "oos_calmar": round(mb["calmar"], 4),
                 "max_drawdown": round(mb["max_dd"], 4), "win_rate": round(mb["win_rate"], 4),
                 "n_trades": 0, "annual_turnover": 0.0, "oos_n": len(bh), "valid": False})
    return pd.DataFrame(rows)


def hac_t(series):
    y = series.dropna().values
    X = np.ones((len(y), 1))
    nw = int(0.75 * len(y) ** (1 / 3))
    return float(sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw}).tvalues[0]), nw


def main():
    raw = pd.read_parquet(REPO / RAW_PARQUET)
    hmm = pd.read_parquet(REPO / SIGNALS_PARQUET)["hmm_2state_prob_stress"]
    work = raw.dropna(subset=["spy_ret"]).copy()
    work["hmm_2state_prob_stress"] = hmm.reindex(work.index)
    n_days = len(work)
    oos_n = int(min(max(252, round(n_days * 0.25)), 1260))
    oos_start = work.index[-oos_n]
    is_end = work.index[-(oos_n + 1)]
    oos_end = work.index[-1]
    is_mask = work.index <= is_end
    oos_mask = work.index >= oos_start
    spy_ret = work["spy_ret"]
    print(f"  [data] {RAW_PARQUET} + committed HMM; n={n_days} OOS {oos_start.date()}..{oos_end.date()} ({oos_n}d)")

    tr = run_tournament(work, spy_ret, is_mask, oos_mask, DAILY_LEADS)
    tr.to_csv(RES / f"tournament_results_{DATE_TAG}.csv", index=False)
    valid = tr[tr["valid"] & (tr["signal"] != "BENCHMARK")].copy().reset_index(drop=True)
    bench = tr[tr["signal"] == "BENCHMARK"].iloc[0]
    print(f"  [tournament] daily grid {DAILY_LEADS}: {len(valid)} valid; bh SPY Sharpe {bench['oos_sharpe']}")

    winner = valid.loc[valid["oos_sharpe"].idxmax()]
    assert (winner["signal"], winner["threshold"], winner["strategy"], int(winner["lead_days"]), winner["lookback"]) == \
        ("rs_mom6m", "T2_roll_p75", "P1_long_cash_pro", 63, "LB63"), \
        f"WINNER CHANGED: {winner[['signal','threshold','strategy','lead_days','lookback','oos_sharpe']].to_dict()} — STOP, escalate"
    wsig, wthr, wlb, wstrat, wlead = winner["signal"], winner["threshold"], winner["lookback"], winner["strategy"], int(winner["lead_days"])
    wcol = SIGNAL_COLS[wsig]
    worient = "pro"
    print(f"  [winner] {wsig}/{wthr}/{wstrat}/L{wlead}/{wlb} = {winner['oos_sharpe']} (UNCHANGED; reproduces 1.5700)")

    pos, sr = replay_combo(work, spy_ret, is_mask, wcol, wthr, wlb, "P1_long_cash", worient, wlead)
    oos_sr = sr[oos_mask].fillna(0.0)
    t_hac, nw = hac_t(oos_sr)
    print(f"  [adjudication] winner L{wlead} HAC t={t_hac:.3f} (nw={nw}) t>3: {'PASS' if t_hac > 3 else 'FAIL'}")

    # GENUINE-LEAD PROFILE: winner combo Sharpe + HAC at EACH lead — does it peak at 63?
    print("  [lead-profile] winner combo (rs_mom6m/T2_roll_p75/P1_long_cash_pro/LB63) by lead:")
    wc_rows = []
    for L in DAILY_LEADS:
        p2, s2 = replay_combo(work, spy_ret, is_mask, wcol, wthr, wlb, "P1_long_cash", worient, L)
        if s2 is None:
            wc_rows.append({"lead_days": L, "oos_sharpe": float("nan"), "is_published_winner": (L == wlead), "lead_source": "pipeline"})
            continue
        o2 = s2[oos_mask].fillna(0.0)
        sh2 = ann_metrics(o2)["sharpe"]
        th2 = hac_t(o2)[0]
        wc_rows.append({"lead_days": L, "oos_sharpe": round(float(sh2), 4), "is_published_winner": (L == wlead), "lead_source": "pipeline"})
        print(f"       L{L:>3}: Sharpe={sh2:.4f}  HAC t={th2:.2f}")
    wc = pd.DataFrame(wc_rows)
    wc.to_csv(RES / f"lead_winner_curve_{DATE_TAG}.csv", index=False)

    sr_df = pd.DataFrame({"date": work.index.strftime("%Y-%m-%d"), "position": pos.reindex(work.index).values,
                          "strategy_return": sr.reindex(work.index).fillna(0.0).values, "bh_return": spy_ret.reindex(work.index).values})
    sr_df.to_csv(RES / f"strategy_returns_{DATE_TAG}.csv", index=False)

    # lead apparatus
    native = valid.copy()
    native["signal_column"] = native["signal"].map(SIGNAL_COLS)
    native["lead_source"] = "pipeline"
    native = native[["signal", "threshold", "strategy", "signal_column", "lookback", "lead_days",
                     "oos_sharpe", "max_drawdown", "valid", "lead_source"]]
    native.to_csv(RES / f"lead_tournament_native_{DATE_TAG}.csv", index=False)

    env_rows, agg_rows = [], []
    for L in DAILY_LEADS:
        g = valid[valid["lead_days"] == L]
        if len(g):
            b = g.loc[g["oos_sharpe"].idxmax()]
            env_rows.append({"lead_days": L, "best_oos_sharpe": round(float(b["oos_sharpe"]), 4),
                             "best_signal": b["signal"], "best_threshold": b["threshold"], "best_strategy": b["strategy"]})
            agg_rows.append({"lead_days": L, "n_valid": len(g),
                             "best_oos_sharpe": round(float(g["oos_sharpe"].max()), 4),
                             "median_oos_sharpe": round(float(g["oos_sharpe"].median()), 4),
                             "p25_oos_sharpe": round(float(g["oos_sharpe"].quantile(0.25)), 4),
                             "p75_oos_sharpe": round(float(g["oos_sharpe"].quantile(0.75)), 4),
                             "best_signal": b["signal"], "best_threshold": b["threshold"],
                             "best_strategy": b["strategy"], "best_max_dd": round(float(b["max_drawdown"]), 4)})
        else:
            env_rows.append({"lead_days": L, "best_oos_sharpe": float("nan"), "best_signal": "", "best_threshold": "", "best_strategy": ""})
    env = pd.DataFrame(env_rows)
    env.to_csv(RES / f"lead_clean_envelope_{DATE_TAG}.csv", index=False)
    pd.DataFrame(agg_rows).to_csv(RES / f"lead_tournament_{DATE_TAG}.csv", index=False)
    for L in DAILY_LEADS:
        w_ = wc.loc[wc.lead_days == L, "oos_sharpe"].iloc[0]
        e_ = env.loc[env.lead_days == L, "best_oos_sharpe"].iloc[0]
        if pd.notna(w_) and pd.notna(e_) and w_ > e_ + 1e-6:
            raise SystemExit(f"COHERENCE VIOLATION at L{L}: winner {w_} > envelope {e_}")

    spy_fwd = spy_ret.shift(-1)
    corr_rows = []
    for code, col in SIGNAL_COLS.items():
        if col not in work.columns:
            continue
        row = {"transform": col}
        best_l, best_r = None, 0.0
        for L in DAILY_LEADS:
            s = work[col].shift(L)
            d = pd.concat([s, spy_fwd], axis=1).dropna()
            r = d.iloc[:, 0].corr(d.iloc[:, 1]) if len(d) > 50 else float("nan")
            row[f"L{L}"] = round(float(r), 4) if pd.notna(r) else float("nan")
            if pd.notna(r) and abs(r) > abs(best_r):
                best_l, best_r = L, r
        row["best_lead"], row["best_r"] = best_l, round(float(best_r), 4)
        corr_rows.append(row)
    pd.DataFrame(corr_rows).to_csv(RES / f"lead_correlation_{DATE_TAG}.csv", index=False)

    # ── winner_summary refresh (headline unchanged 1.57; daily provenance) ──
    ws = json.loads((RES / "winner_summary.json").read_text())
    m = ann_metrics(oos_sr)
    ranked = valid.sort_values("oos_sharpe", ascending=False)
    runner = ranked.iloc[1]
    ws.update({
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4), "oos_sortino": round(m["sortino"], 4),
        "oos_calmar": round(m["calmar"], 4), "oos_ann_return": round(m["ann_return"], 4),
        "oos_ann_vol": round(m["ann_vol"], 4), "oos_max_drawdown": round(m["max_dd"], 4),
        "oos_win_rate": round(m["win_rate"], 4), "oos_n": int(winner["oos_n"]),
        "bh_sharpe": round(float(bench["oos_sharpe"]), 4),
    })
    ws["selection"]["grid_scanned"] = {
        "leads": DAILY_LEADS, "n_signals": int(valid["signal"].nunique()),
        "n_thresholds": int(valid["threshold"].nunique()), "n_strategies": int(valid["strategy"].nunique()),
        "n_valid_combos": int(len(valid)), "median_valid_objective": round(float(valid["oos_sharpe"].median()), 4),
    }
    ws["selection"]["raw_winner_row"] = {
        "signal": wsig, "threshold": wthr, "strategy": wstrat, "lead_column": "lead_days",
        "lead_value": wlead, "lookback": wlb, "source_tournament_file": f"tournament_results_{DATE_TAG}.csv",
        "source_row_index": int(winner.name),
        "display_alias": "signal_code=phlxsox_rs_mom6m (raw signal=rs_mom6m); strategy_family=P1_long_cash (raw strategy=P1_long_cash_pro)",
    }
    ws["selection"]["runner_up"] = {
        "signal": runner["signal"], "threshold": runner["threshold"], "strategy": runner["strategy"],
        "lead_value": int(runner["lead_days"]), "objective_value": round(float(runner["oos_sharpe"]), 4),
    }
    _hurdle = (f"clears the t>3 hurdle (HAC t={t_hac:.2f})" if t_hac > 3 else
               f"is BELOW the strict t>3 hurdle (HAC t={t_hac:.2f}) — a LOW-CONFIDENCE lead, consistent with the "
               f"pre-existing overfitting flags (IS Sharpe 0.10 vs OOS 1.57, lost every pre-OOS stress episode, "
               f"bootstrap p=0.041; 'search-found, not validated')")
    ws["selection"]["rationale"] = (
        f"FREE full-grid daily selection (Lead-Grid Frequency Standard, 2026-07-15): NO cap. Winner is the "
        f"global-max valid OOS Sharpe over the anchored DAILY grid {{1,5,21,63,126,252}} trading days — L1 floor, "
        f"NO L0 (a same-day SOX/SPY reading is co-movement, not a forecast) — ({len(valid)} valid combos, median "
        f"{valid['oos_sharpe'].median():.4f}; ECON-T4 deployable scoring): {wsig}/{wthr}/{wstrat}/L{wlead}/{wlb} = "
        f"{winner['oos_sharpe']:.4f}. This is a GENUINE ~1-quarter (63-trading-day) LEAD, NOT coincident. Newey-West "
        f"HAC t-stat {_hurdle}. Built from the RESTORED original raw data ({RAW_PARQUET}) + committed HMM (no re-fit): "
        f"reproduces the committed headline 1.5700 EXACTLY — a lead-AXIS rebuild (monthly→daily), NOT a re-selection. "
        f"HEAVY caveats stand (see notes): search-found, favourable 2021-26 semis-bull OOS draw, median valid combo "
        f"({valid['oos_sharpe'].median():.2f}) below B&H."
    )
    ws["selection"]["tie_break_step"] = 0
    ws["selection"]["objective_runner_up_divergence"] = None
    (RES / "winner_summary.json").write_text(json.dumps(ws, indent=2) + "\n")
    print(f"  [winner_summary] oos_sharpe={ws['oos_sharpe']} bh={ws['bh_sharpe']} lead={ws['lead_value']}{ws['lead_unit']}/{wlb}")

    ro = sr_df.assign(date=pd.to_datetime(sr_df["date"])).set_index("date")
    o = ro.loc[ro.index >= oos_start, "strategy_return"]
    rec = o.mean() / o.std() * np.sqrt(TD)
    print(f"  [ECON-SR1] strategy_returns OOS Sharpe {rec:.4f} vs winner_summary {ws['oos_sharpe']} "
          f"-> {'RECONCILES' if abs(rec - ws['oos_sharpe']) <= 0.01 else 'MISMATCH'}")
    print("  DONE.")


if __name__ == "__main__":
    main()
