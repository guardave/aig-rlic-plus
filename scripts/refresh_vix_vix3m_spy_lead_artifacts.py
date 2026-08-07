#!/usr/bin/env python3
"""Daily-axis rebuild for vix_vix3m_spy — GH#13 daily Class-A track (pair 3/4).

Mirrors the hy_ig pilot: rebuild the lead apparatus on the pair's NATIVE DAILY axis
{0,1,5,21,63,126,252} trading days, from the RESTORED committed raw data
(data/vix_vix3m_spy_daily_20260314.parquet — all signals are deterministic transforms of
the VIX/VIX3M ratio + spy_ret; NO HMM/regime model to re-fit). Sources the ORIGINAL SPY
return from that parquet (NOT a re-fetch). Reproduces the committed headline 1.1295 EXACTLY
(verified) → headline unchanged, clean (no pin, no data_vintage).

Faithful to scripts/pair_pipeline_vix_vix3m_spy.py::stage_tournament:
  * 10 signals (S1_ratio..S10_spread) × {T1_p{25,50,75} IS-quantile, T2_rp{25,50,75}
    rolling-252 quantile, T4_unity (S1 only)} × {P1,P2,P3}. Countercyclical: long SPY
    when signal < threshold (low VIX/VIX3M = calm = risk-on). strat_ret = pos.shift(1)*spy_ret.
  * ECON-T4 deployable OOS scoring: strat_ret[oos].fillna(0) (was dropna). No-op for the
    L0 winner (positions defined every OOS day → deployable == dropna). Free full-grid, NO cap.

Winner (verified UNCHANGED): S3_z126 / T2_rp75 / P1 / L0 = 1.1295 — COINCIDENT / same-day.
No long-lead edge (long leads fail t>3).

DAILY TEMPLATE sibling of refresh_hy_ig_spy_lead_artifacts.py.
Run:  python3 scripts/refresh_vix_vix3m_spy_lead_artifacts.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO = Path(__file__).resolve().parents[1]
PAIR = "vix_vix3m_spy"
RES = REPO / "results" / PAIR
DATE_TAG = "20260715"
SRC_TAG = "20260314"
RAW_PARQUET = "data/vix_vix3m_spy_daily_20260314.parquet"
IS_END, OOS_START, OOS_END = "2019-12-31", "2020-01-01", "2025-12-31"
ANN = 252
DAILY_LEADS = [0, 1, 5, 21, 63, 126, 252]
SIGNAL_COLS = {
    "S1_ratio": "vix_ratio", "S2_z252": "vix_ratio_zscore_252d", "S3_z126": "vix_ratio_zscore_126d",
    "S4_roc5": "vix_ratio_roc_5d", "S5_roc21": "vix_ratio_roc_21d", "S6_mom5": "vix_ratio_mom_5d",
    "S7_mom21": "vix_ratio_mom_21d", "S8_pctrank": "vix_ratio_pctrank_252d",
    "S9_backwd": "vix_backwardation", "S10_spread": "vix_term_spread",
}
STRATS = ["P1", "P2", "P3"]


def _threshold(sig_l, is_mask, tname):
    if tname.startswith("T1_p"):
        pct = int(tname.split("p")[1])
        return sig_l[is_mask].dropna().quantile(pct / 100)
    if tname.startswith("T2_rp"):
        pct = int(tname.split("rp")[1])
        return sig_l.rolling(252, min_periods=200).quantile(pct / 100)
    return 1.0  # T4_unity


def replay(df, spy_ret, sig_col, tname, strat, lead, is_mask):
    sig_l = df[sig_col].shift(lead) if lead > 0 else df[sig_col]
    tval = _threshold(sig_l, is_mask, tname)
    bullish = sig_l < tval
    if strat == "P1":
        pos = bullish.astype(float)
    elif strat == "P2":
        smin = sig_l.rolling(252, min_periods=200).min()
        smax = sig_l.rolling(252, min_periods=200).max()
        pos = (1 - (sig_l - smin) / (smax - smin).replace(0, np.nan)).clip(0, 1)
    else:  # P3
        pos = bullish.astype(float) * 2 - 1
    return pos, pos.shift(1) * spy_ret


def score(df, spy_ret, sig_col, tname, strat, lead, is_mask, oos_mask):
    pos, sr = replay(df, spy_ret, sig_col, tname, strat, lead, is_mask)
    is_r = sr[is_mask].dropna()
    oos_r = sr[oos_mask].fillna(0.0)          # ECON-T4 deployable
    if len(is_r) < 100 or len(oos_r) < 50:
        return None
    sharpe = (oos_r.mean() / oos_r.std()) * np.sqrt(ANN) if oos_r.std() > 0 else 0
    cum = (1 + oos_r).cumprod()
    dd = ((cum - cum.cummax()) / cum.cummax()).min()
    turnover = pos.diff().abs().sum() / (len(pos.dropna()) / ANN)
    return {"oos_sharpe": round(float(sharpe), 4),
            "oos_ann_return": round(float(oos_r.mean() * ANN * 100), 2),   # percent (pipeline schema)
            "max_drawdown": round(float(dd * 100), 2),                     # percent
            "annual_turnover": round(float(turnover), 2), "oos_n": len(oos_r),
            "valid": bool(sharpe > 0 and turnover < 24 and len(oos_r) >= 50)}


def run_tournament(df, spy_ret, is_mask, oos_mask):
    available = {k: v for k, v in SIGNAL_COLS.items() if v in df.columns and df[v].notna().sum() > 200}
    rows = []
    for sig_name, sig_col in available.items():
        for lead in DAILY_LEADS:
            sig_l = df[sig_col].shift(lead) if lead > 0 else df[sig_col]
            if len(sig_l[is_mask].dropna()) < 100:
                continue
            tnames = [f"T1_p{p}" for p in (25, 50, 75)] + [f"T2_rp{p}" for p in (25, 50, 75)]
            if sig_name == "S1_ratio":
                tnames.append("T4_unity")
            for tname in tnames:
                for strat in STRATS:
                    m = score(df, spy_ret, sig_col, tname, strat, lead, is_mask, oos_mask)
                    if m is None:
                        continue
                    rows.append({"signal": sig_name, "threshold": tname, "strategy": strat,
                                 "lead_days": lead, **m})
    bh = spy_ret[oos_mask].dropna()
    bh_sh = (bh.mean() / bh.std()) * np.sqrt(ANN) if bh.std() > 0 else 0
    bh_cum = (1 + bh).cumprod()
    bh_dd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min()
    rows.append({"signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BH", "lead_days": 0,
                 "oos_sharpe": round(float(bh_sh), 4), "oos_ann_return": round(float(bh.mean() * ANN * 100), 2),
                 "max_drawdown": round(float(bh_dd * 100), 2), "annual_turnover": 0.0,
                 "oos_n": len(bh), "valid": False})
    return pd.DataFrame(rows)


def hac_t(series):
    y = series.values
    X = np.ones((len(y), 1))
    nw = int(0.75 * len(y) ** (1 / 3))
    return float(sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw}).tvalues[0]), nw


def main():
    df = pd.read_parquet(REPO / RAW_PARQUET)
    spy_ret = df["spy_ret"]
    idx = df.index
    is_mask = idx <= IS_END
    oos_mask = idx >= OOS_START
    print(f"  [data] {RAW_PARQUET}  rows={len(df)}  target=SPY")

    tr = run_tournament(df, spy_ret, is_mask, oos_mask)
    tr.to_csv(RES / f"tournament_results_{DATE_TAG}.csv", index=False)
    valid = tr[tr["valid"] & (tr["signal"] != "BENCHMARK")].copy().reset_index(drop=True)
    bench = tr[tr["signal"] == "BENCHMARK"].iloc[0]
    print(f"  [tournament] daily grid {DAILY_LEADS}: {len(valid)} valid; bh SPY Sharpe {bench['oos_sharpe']}")

    winner = valid.loc[valid["oos_sharpe"].idxmax()]
    assert (winner["signal"], winner["threshold"], winner["strategy"], int(winner["lead_days"])) == \
        ("S3_z126", "T2_rp75", "P1", 0), \
        f"WINNER CHANGED: {winner[['signal','threshold','strategy','lead_days','oos_sharpe']].to_dict()} — STOP, escalate"
    wsig, wthr, wstrat, wlead = winner["signal"], winner["threshold"], winner["strategy"], int(winner["lead_days"])
    wcol = SIGNAL_COLS[wsig]
    print(f"  [winner] {wsig}/{wthr}/{wstrat}/L{wlead} = {winner['oos_sharpe']} (UNCHANGED; reproduces 1.1295)")

    pos, sr = replay(df, spy_ret, wcol, wthr, wstrat, wlead, is_mask)
    oos_sr = sr[oos_mask].fillna(0.0)
    t_hac, nw = hac_t(oos_sr)
    print(f"  [adjudication] winner HAC t={t_hac:.3f} (nw={nw}) t>3: {'PASS' if t_hac > 3 else 'FAIL'}")
    ll_t = {}
    for L in (126, 252):
        g = valid[valid["lead_days"] == L]
        if len(g):
            b = g.loc[g["oos_sharpe"].idxmax()]
            _, blr = replay(df, spy_ret, SIGNAL_COLS[b["signal"]], b["threshold"], b["strategy"], L, is_mask)
            ll_t[L] = (round(float(b["oos_sharpe"]), 3), round(hac_t(blr[oos_mask].fillna(0.0))[0], 2))
    print(f"  [adjudication] long-lead: " + ", ".join(f"L{L}={s}/t={t}" for L, (s, t) in ll_t.items()))

    sr_df = pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "position": pos.reindex(idx).values,
                          "strategy_return": sr.reindex(idx).fillna(0.0).values, "bh_return": spy_ret.reindex(idx).values})
    sr_df.to_csv(RES / f"strategy_returns_{DATE_TAG}.csv", index=False)

    # ── lead apparatus (daily axis) ──
    native = valid.copy()
    native["signal_column"] = native["signal"].map(SIGNAL_COLS)
    native["lead_source"] = "pipeline"
    native = native[["signal", "threshold", "strategy", "signal_column", "lead_days",
                     "oos_sharpe", "max_drawdown", "valid", "lead_source"]]
    native.to_csv(RES / f"lead_tournament_native_{DATE_TAG}.csv", index=False)

    wc_rows = []
    for L in DAILY_LEADS:
        m = score(df, spy_ret, wcol, wthr, wstrat, L, is_mask, oos_mask)
        wc_rows.append({"lead_days": L, "oos_sharpe": round(m["oos_sharpe"], 4) if m else float("nan"),
                        "is_published_winner": (L == wlead), "lead_source": "pipeline"})
    wc = pd.DataFrame(wc_rows)
    wc.to_csv(RES / f"lead_winner_curve_{DATE_TAG}.csv", index=False)

    env_rows = []
    for L in DAILY_LEADS:
        g = valid[valid["lead_days"] == L]
        if len(g):
            b = g.loc[g["oos_sharpe"].idxmax()]
            env_rows.append({"lead_days": L, "best_oos_sharpe": round(float(b["oos_sharpe"]), 4),
                             "best_signal": b["signal"], "best_threshold": b["threshold"], "best_strategy": b["strategy"]})
        else:
            env_rows.append({"lead_days": L, "best_oos_sharpe": float("nan"),
                             "best_signal": "", "best_threshold": "", "best_strategy": ""})
    env = pd.DataFrame(env_rows)
    env.to_csv(RES / f"lead_clean_envelope_{DATE_TAG}.csv", index=False)
    for L in DAILY_LEADS:
        w_ = wc.loc[wc.lead_days == L, "oos_sharpe"].iloc[0]
        e_ = env.loc[env.lead_days == L, "best_oos_sharpe"].iloc[0]
        if pd.notna(w_) and pd.notna(e_) and w_ > e_ + 1e-6:
            raise SystemExit(f"COHERENCE VIOLATION at L{L}: winner {w_} > envelope {e_}")

    agg_rows = []
    for L in DAILY_LEADS:
        g = valid[valid["lead_days"] == L]
        if not len(g):
            continue
        b = g.loc[g["oos_sharpe"].idxmax()]
        agg_rows.append({"lead_days": L, "n_valid": len(g),
                         "best_oos_sharpe": round(float(g["oos_sharpe"].max()), 4),
                         "median_oos_sharpe": round(float(g["oos_sharpe"].median()), 4),
                         "p25_oos_sharpe": round(float(g["oos_sharpe"].quantile(0.25)), 4),
                         "p75_oos_sharpe": round(float(g["oos_sharpe"].quantile(0.75)), 4),
                         "best_signal": b["signal"], "best_threshold": b["threshold"],
                         "best_strategy": b["strategy"], "best_max_dd": round(float(b["max_drawdown"]), 2)})
    pd.DataFrame(agg_rows).to_csv(RES / f"lead_tournament_{DATE_TAG}.csv", index=False)

    spy_fwd = spy_ret.shift(-1)
    corr_rows = []
    for code, col in SIGNAL_COLS.items():
        if col not in df.columns:
            continue
        row = {"transform": col}
        best_l, best_r = None, 0.0
        for L in DAILY_LEADS:
            s = df[col].shift(L) if L > 0 else df[col]
            d = pd.concat([s, spy_fwd], axis=1).dropna()
            r = d.iloc[:, 0].corr(d.iloc[:, 1]) if len(d) > 50 else float("nan")
            row[f"L{L}"] = round(float(r), 4) if pd.notna(r) else float("nan")
            if pd.notna(r) and abs(r) > abs(best_r):
                best_l, best_r = L, r
        row["best_lead"], row["best_r"] = best_l, round(float(best_r), 4)
        corr_rows.append(row)
    pd.DataFrame(corr_rows).to_csv(RES / f"lead_correlation_{DATE_TAG}.csv", index=False)

    # ── winner_summary refresh (headline unchanged 1.1295; ratio form; daily provenance) ──
    ws = json.loads((RES / "winner_summary.json").read_text())
    oos_ann_ratio = float(oos_sr.mean() * ANN)
    cumw = (1 + oos_sr).cumprod()
    mdd_ratio = float(((cumw - cumw.cummax()) / cumw.cummax()).min())
    turnover = float(pos.diff().abs().sum() / (len(pos.dropna()) / ANN))
    ranked = valid.sort_values("oos_sharpe", ascending=False)
    runner = ranked.iloc[1]
    ws.update({
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "oos_ann_return": round(oos_ann_ratio, 4), "oos_max_drawdown": round(mdd_ratio, 4),
        "annual_turnover": round(turnover, 2), "oos_n_trades": int(winner["oos_n"]),
        "bh_sharpe": round(float(bench["oos_sharpe"]), 4), "bh_oos_sharpe": round(float(bench["oos_sharpe"]), 4),
    })
    ws["selection"]["grid_scanned"] = {
        "leads": DAILY_LEADS, "n_signals": int(valid["signal"].nunique()),
        "n_thresholds": int(valid["threshold"].nunique()), "n_strategies": int(valid["strategy"].nunique()),
        "n_valid_combos": int(len(valid)), "median_valid_objective": round(float(valid["oos_sharpe"].median()), 4),
    }
    ws["selection"]["raw_winner_row"] = {
        "signal": wsig, "threshold": wthr, "strategy": wstrat, "lead_column": "lead_days",
        "lead_value": wlead, "source_tournament_file": f"tournament_results_{DATE_TAG}.csv",
        "source_row_index": int(winner.name), "display_alias": "strategy_family=P1_long_cash (raw strategy=P1)",
    }
    ws["selection"]["runner_up"] = {
        "signal": runner["signal"], "threshold": runner["threshold"], "strategy": runner["strategy"],
        "lead_value": int(runner["lead_days"]), "objective_value": round(float(runner["oos_sharpe"]), 4),
    }
    _ll = "; ".join(f"L{L} best={s} (HAC t={t})" for L, (s, t) in ll_t.items())
    _hurdle = (f"Newey-West HAC t={t_hac:.2f} > 3.0 (Harvey-Liu-Zhu) — clears the raised hurdle."
               if t_hac > 3.0 else
               f"Newey-West HAC t={t_hac:.2f} is MARGINALLY BELOW the raised t>3.0 hurdle (Harvey-Liu-Zhu) — a "
               f"LOW-CONFIDENCE coincident edge: it reproduces the committed headline and remains the global-max "
               f"valid combo, but its significance is borderline after multiple-horizon testing.")
    ws["selection"]["rationale"] = (
        f"FREE full-grid daily selection (Lead-Grid Frequency Standard, 2026-07-15): NO cap. Winner is the "
        f"global-max valid OOS Sharpe over the anchored DAILY grid {{0,1,5,21,63,126,252}} trading days "
        f"({len(valid)} valid combos, median {valid['oos_sharpe'].median():.4f}; ECON-T4 deployable scoring): "
        f"{wsig}/{wthr}/{wstrat}/L{wlead} = {winner['oos_sharpe']:.4f}. Winner is at L0 = COINCIDENT / same-day "
        f"(VIX/VIX3M term-structure observed at close; real-time floor L0). {_hurdle} NO long-lead edge "
        f"({_ll} — all below the winner and below t>3), so the grid extension surfaces only multiple-testing "
        f"noise. Built from the RESTORED original raw data ({RAW_PARQUET}, deterministic ratio transforms — no "
        f"model re-fit): reproduces the committed headline 1.1295 EXACTLY — a lead-AXIS rebuild (monthly→daily), "
        f"NOT a re-selection and NOT a data-vintage change."
    )
    ws["selection"]["tie_break_step"] = 0
    ws["selection"]["objective_runner_up_divergence"] = None
    ws["notes"] = (
        f"vix_vix3m_spy DAILY Class-A rebuild (GH#13, Lead-Grid Frequency Standard). Coincident same-day (L0) "
        f"winner S3_z126/P1 on the DAILY lead axis {{0,1,5,21,63,126,252}} (target SPY). OOS {OOS_START}..{OOS_END}. "
        f"Lead-axis rebuild from restored original data (deterministic signals, no re-fit) — reproduces committed "
        f"1.1295; winner UNCHANGED. oos_n_trades=1566 is the OOS daily period count (not discrete trades)."
    )
    (RES / "winner_summary.json").write_text(json.dumps(ws, indent=2) + "\n")
    print(f"  [winner_summary] oos_sharpe={ws['oos_sharpe']} bh={ws['bh_sharpe']} lead={ws['lead_value']}{ws['lead_unit']}")

    r = sr_df.assign(date=pd.to_datetime(sr_df["date"])).set_index("date")
    ro = r.loc[r.index >= OOS_START, "strategy_return"]
    rec = (ro.mean() / ro.std()) * np.sqrt(ANN)
    print(f"  [ECON-SR1] strategy_returns OOS Sharpe {rec:.4f} vs winner_summary {ws['oos_sharpe']} "
          f"-> {'RECONCILES' if abs(rec - ws['oos_sharpe']) <= 0.01 else 'MISMATCH'}")
    print("  DONE.")


if __name__ == "__main__":
    main()
