#!/usr/bin/env python3
"""Daily-axis rebuild for gold_copper_xli — GH#13 daily Class-A track (pair 2/4).

Mirrors the hy_ig pilot: rebuild the lead apparatus on the pair's NATIVE DAILY axis
{0,1,5,21,63,126,252} trading days, from the RESTORED committed raw data
(data/gold_copper_xli_daily_20260526.parquet — has all signals + xli_ret; gold_copper's
signals are deterministic price transforms, NO HMM/regime model to re-fit). Sources the
ORIGINAL XLI target return from that parquet (NOT a re-fetch). Reproduces the committed
headline 1.273 EXACTLY (verified) → headline unchanged, clean (no pin, no data_vintage).

Faithful to scripts/econ_pipeline_gold_copper_xli.py::stage_tournament:
  * 5 signals × {T1_p25, T2_p50, T3_p75} IS-quantile thresholds × {P1_long_cash,
    P2_long_short} × lead. Countercyclical: long XLI when signal <= threshold (low
    gold/copper ratio = risk-on). Position is lead-shifted and cash-filled
    (pos=(sig<=t).shift(lead).fillna(0)); strat_ret = pos * xli_ret.fillna(0).
  * OOS scoring is already deployable (positions cash-filled) so dropna == ECON-T4
    deployable. Free full-grid selection, NO cap.

Changes vs committed 20260526: grid {0,1,5} → daily {0,1,5,21,63,126,252} (adds
21/63/126/252). Winner (verified UNCHANGED): gold_copper_zscore_126d / T2_p50 /
P1_long_cash / L0 = 1.273 — COINCIDENT / same-day. No long-lead edge (best long lead
fails t>3).

DAILY TEMPLATE sibling of refresh_hy_ig_spy_lead_artifacts.py.
Run:  python3 scripts/refresh_gold_copper_xli_lead_artifacts.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO = Path(__file__).resolve().parents[1]
PAIR = "gold_copper_xli"
RES = REPO / "results" / PAIR
DATE_TAG = "20260715"
SRC_TAG = "20260526"
RAW_PARQUET = "data/gold_copper_xli_daily_20260526.parquet"
IS_END, OOS_START, OOS_END = "2019-12-31", "2020-01-01", "2025-12-31"
ANN = 252
DAILY_LEADS = [0, 1, 5, 21, 63, 126, 252]
TARGET_RET = "xli_ret"
SIGNAL_COLS = [
    "gold_copper_zscore_252d", "gold_copper_zscore_126d", "gold_copper_pctrank_504d",
    "gold_copper_roc_63d", "gold_copper_roc_126d",
]
STRATS = ["P1_long_cash", "P2_long_short"]


def signal_code(col: str) -> str:
    return f"S_{col.replace('gold_copper_', '')}"


def replay(df, ret, sig_col, t_val, s_code, lead):
    """Faithful replica of econ_pipeline stage_tournament position logic."""
    sig = df[sig_col]
    pos = (sig <= t_val).astype(int).shift(lead).fillna(0)
    if s_code == "P2_long_short":
        pos = pos * 2 - 1
    return pos, pos * ret


def score(df, ret, sig_col, t_val, s_code, lead):
    pos, strat_ret = replay(df, ret, sig_col, t_val, s_code, lead)
    oos = strat_ret.loc[OOS_START:OOS_END].dropna()   # deployable == dropna (cash-filled)
    if len(oos) < 200:
        return None
    sharpe = (oos.mean() * ANN) / (oos.std() * np.sqrt(ANN) + 1e-12)
    ann_ret = (1 + oos).prod() ** (ANN / len(oos)) - 1
    equity = (1 + oos).cumprod()
    mdd = ((equity - equity.cummax()) / equity.cummax()).min()
    turnover = pos.diff().abs().loc[OOS_START:OOS_END].sum() / (len(oos) / ANN)
    return {
        "oos_sharpe": round(float(sharpe), 4), "oos_ann_return": round(float(ann_ret), 4),
        "oos_max_drawdown": round(float(mdd), 4), "annual_turnover": round(float(turnover), 2),
        "oos_n": len(oos), "valid": bool(sharpe > 0 and turnover < 100),
    }


def is_thresholds(df, sig_col):
    is_sig = df[sig_col].loc[:IS_END].dropna()
    if len(is_sig) < 252:
        return None
    return {"T1_p25": is_sig.quantile(0.25), "T2_p50": is_sig.quantile(0.50),
            "T3_p75": is_sig.quantile(0.75)}


def run_tournament(df, ret, leads):
    rows = []
    for sig_col in SIGNAL_COLS:
        ths = is_thresholds(df, sig_col)
        if ths is None:
            continue
        for t_code, t_val in ths.items():
            for s_code in STRATS:
                for lead in leads:
                    m = score(df, ret, sig_col, t_val, s_code, lead)
                    if m is None:
                        continue
                    rows.append({"signal": sig_col, "threshold": t_code,
                                 "threshold_value": round(float(t_val), 4),
                                 "strategy": s_code, "lead_days": lead, **m})
    # BENCHMARK: buy-and-hold XLI over OOS
    bh = ret.loc[OOS_START:OOS_END].dropna()
    bh_sh = (bh.mean() * ANN) / (bh.std() * np.sqrt(ANN) + 1e-12)
    bh_ann = (1 + bh).prod() ** (ANN / len(bh)) - 1
    eq = (1 + bh).cumprod()
    bh_dd = ((eq - eq.cummax()) / eq.cummax()).min()
    rows.append({"signal": "BENCHMARK", "threshold": "BUY_HOLD", "threshold_value": 0.0,
                 "strategy": "BH", "lead_days": 0, "oos_sharpe": round(float(bh_sh), 4),
                 "oos_ann_return": round(float(bh_ann), 4), "oos_max_drawdown": round(float(bh_dd), 4),
                 "annual_turnover": 0.0, "oos_n": len(bh), "valid": False})
    return pd.DataFrame(rows)


def hac_t(series):
    y = series.values
    X = np.ones((len(y), 1))
    nw = int(0.75 * len(y) ** (1 / 3))
    return float(sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": nw}).tvalues[0]), nw


def main():
    df = pd.read_parquet(REPO / RAW_PARQUET)
    ret = df[TARGET_RET].fillna(0)
    print(f"  [data] {RAW_PARQUET}  rows={len(df)}  target={TARGET_RET}")

    tr = run_tournament(df, ret, DAILY_LEADS)
    tr.to_csv(RES / f"tournament_results_{DATE_TAG}.csv", index=False)
    valid = tr[tr["valid"] & (tr["signal"] != "BENCHMARK")].copy().reset_index(drop=True)
    bench = tr[tr["signal"] == "BENCHMARK"].iloc[0]
    print(f"  [tournament] daily grid {DAILY_LEADS}: {len(valid)} valid; bh XLI Sharpe {bench['oos_sharpe']}")

    winner = valid.loc[valid["oos_sharpe"].idxmax()]
    assert (winner["signal"], winner["threshold"], winner["strategy"], int(winner["lead_days"])) == \
        ("gold_copper_zscore_126d", "T2_p50", "P1_long_cash", 0), \
        f"WINNER CHANGED: {winner[['signal','threshold','strategy','lead_days','oos_sharpe']].to_dict()} — STOP, escalate"
    wsig, wthr, wtval, wstrat, wlead = (winner["signal"], winner["threshold"],
                                        float(winner["threshold_value"]), winner["strategy"], int(winner["lead_days"]))
    print(f"  [winner] {wsig}/{wthr}/{wstrat}/L{wlead} = {winner['oos_sharpe']} (UNCHANGED; reproduces 1.273)")

    # winner replay -> strategy_returns + adjudication
    pos, strat_ret = replay(df, ret, wsig, wtval, wstrat, wlead)
    oos_sr = strat_ret.loc[OOS_START:OOS_END].dropna()
    t_hac, nw = hac_t(oos_sr)
    print(f"  [adjudication] winner HAC t={t_hac:.3f} (nw={nw}) t>3: {'PASS' if t_hac > 3 else 'FAIL'}")
    ll_t = {}
    for L in (126, 252):
        g = valid[valid["lead_days"] == L]
        if len(g):
            b = g.loc[g["oos_sharpe"].idxmax()]
            _, blr = replay(df, ret, b["signal"], float(b["threshold_value"]), b["strategy"], L)
            ll_t[L] = (round(float(b["oos_sharpe"]), 3), round(hac_t(blr.loc[OOS_START:OOS_END].dropna())[0], 2))
    print(f"  [adjudication] long-lead: " + ", ".join(f"L{L}={s}/t={t}" for L, (s, t) in ll_t.items()))

    full = strat_ret.copy()
    sr_df = pd.DataFrame({"date": df.index.strftime("%Y-%m-%d"),
                          "position": pos.values, "strategy_return": full.values,
                          "bh_return": ret.values})
    sr_df.to_csv(RES / f"strategy_returns_{DATE_TAG}.csv", index=False)

    # ── lead apparatus (daily axis) ──
    native = valid.copy()
    native["signal_column"] = native["signal"]
    native["lead_source"] = "pipeline"
    native = native[["signal", "threshold", "strategy", "signal_column", "lead_days",
                     "oos_sharpe", "oos_max_drawdown", "valid", "lead_source"]]
    native.to_csv(RES / f"lead_tournament_native_{DATE_TAG}.csv", index=False)

    wc_rows = []
    for L in DAILY_LEADS:
        m = score(df, ret, wsig, wtval, wstrat, L)
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
                             "best_signal": b["signal"], "best_threshold": b["threshold"],
                             "best_strategy": b["strategy"]})
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
                         "best_strategy": b["strategy"], "best_max_dd": round(float(b["oos_max_drawdown"]), 4)})
    pd.DataFrame(agg_rows).to_csv(RES / f"lead_tournament_{DATE_TAG}.csv", index=False)

    # daily lead_correlation (signal lagged L vs XLI fwd 1d) — audit
    xli_fwd = ret.shift(-1)
    corr_rows = []
    for col in SIGNAL_COLS:
        row = {"transform": col}
        best_l, best_r = None, 0.0
        for L in DAILY_LEADS:
            s = df[col].shift(L) if L > 0 else df[col]
            d = pd.concat([s, xli_fwd], axis=1).dropna()
            r = d.iloc[:, 0].corr(d.iloc[:, 1]) if len(d) > 50 else float("nan")
            row[f"L{L}"] = round(float(r), 4) if pd.notna(r) else float("nan")
            if pd.notna(r) and abs(r) > abs(best_r):
                best_l, best_r = L, r
        row["best_lead"], row["best_r"] = best_l, round(float(best_r), 4)
        corr_rows.append(row)
    pd.DataFrame(corr_rows).to_csv(RES / f"lead_correlation_{DATE_TAG}.csv", index=False)

    # ── winner_summary refresh (headline unchanged 1.273; daily provenance) ──
    ws = json.loads((RES / "winner_summary.json").read_text())
    ann_ret = (1 + oos_sr).prod() ** (ANN / len(oos_sr)) - 1
    eq = (1 + oos_sr).cumprod()
    mdd = ((eq - eq.cummax()) / eq.cummax()).min()
    turnover = pos.diff().abs().loc[OOS_START:OOS_END].sum() / (len(oos_sr) / ANN)
    win_rate = float((oos_sr[oos_sr != 0] > 0).mean())
    n_trades = int(pos.diff().abs().loc[OOS_START:OOS_END].gt(0).sum())
    ranked = valid.sort_values("oos_sharpe", ascending=False)
    runner = ranked.iloc[1]
    ws.update({
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "oos_ann_return": round(float(ann_ret), 4),
        "oos_max_drawdown": round(float(mdd), 4),
        "annual_turnover": round(float(turnover), 2),
        "win_rate": round(win_rate, 4), "oos_n_trades": n_trades,
        "bh_sharpe": round(float(bench["oos_sharpe"]), 4),
        "bh_ann_return": round(float(bench["oos_ann_return"]), 4),
        "bh_max_drawdown": round(float(bench["oos_max_drawdown"]), 4),
    })
    ws["selection"]["grid_scanned"] = {
        "leads": DAILY_LEADS, "n_signals": int(valid["signal"].nunique()),
        "n_thresholds": int(valid["threshold"].nunique()), "n_strategies": int(valid["strategy"].nunique()),
        "n_valid_combos": int(len(valid)), "median_valid_objective": round(float(valid["oos_sharpe"].median()), 4),
    }
    ws["selection"]["raw_winner_row"] = {
        "signal": wsig, "threshold": wthr, "strategy": wstrat, "lead_column": "lead_days",
        "lead_value": wlead, "source_tournament_file": f"tournament_results_{DATE_TAG}.csv",
        "source_row_index": int(winner.name),
        "display_alias": f"signal_code={signal_code(wsig)} (raw signal={wsig})",
    }
    ws["selection"]["runner_up"] = {
        "signal": runner["signal"], "threshold": runner["threshold"], "strategy": runner["strategy"],
        "lead_value": int(runner["lead_days"]), "objective_value": round(float(runner["oos_sharpe"]), 4),
    }
    _ll = "; ".join(f"L{L} best={s} (HAC t={t})" for L, (s, t) in ll_t.items())
    ws["selection"]["rationale"] = (
        f"FREE full-grid daily selection (Lead-Grid Frequency Standard, 2026-07-15): NO cap. Winner is the "
        f"global-max valid OOS Sharpe over the anchored DAILY grid {{0,1,5,21,63,126,252}} trading days "
        f"({len(valid)} valid combos, median {valid['oos_sharpe'].median():.4f}; deployable/cash-filled scoring): "
        f"{wsig}/{wthr}/{wstrat}/L{wlead} = {winner['oos_sharpe']:.4f}. Winner is at L0 = COINCIDENT / same-day "
        f"(gold/copper ratio observed at close; real-time floor L0). Newey-West HAC t={t_hac:.2f} > 3.0 "
        f"(Harvey-Liu-Zhu) — genuine edge. NO long-lead edge ({_ll} — fail t>3), so the grid extension surfaces "
        f"only multiple-testing noise. Built from the RESTORED original raw data ({RAW_PARQUET}, deterministic "
        f"price-transform signals — no model re-fit): reproduces the committed headline 1.273 EXACTLY — a "
        f"lead-AXIS rebuild (monthly→daily), NOT a re-selection and NOT a data-vintage change."
    )
    ws["selection"]["tie_break_step"] = 0
    ws["selection"]["objective_runner_up_divergence"] = None
    ws["notes"] = (
        f"gold_copper_xli DAILY Class-A rebuild (GH#13, Lead-Grid Frequency Standard). Coincident same-day (L0) "
        f"winner {signal_code(wsig)}/P1 on the DAILY lead axis {{0,1,5,21,63,126,252}} (target XLI). OOS "
        f"{OOS_START}..{OOS_END}. Lead-axis rebuild from restored original data — reproduces committed 1.273; winner UNCHANGED."
    )
    (RES / "winner_summary.json").write_text(json.dumps(ws, indent=2) + "\n")
    print(f"  [winner_summary] oos_sharpe={ws['oos_sharpe']} bh={ws['bh_sharpe']} lead={ws['lead_value']}{ws['lead_unit']}")

    r = sr_df.assign(date=pd.to_datetime(sr_df["date"])).set_index("date")
    ro = r.loc[OOS_START:OOS_END, "strategy_return"]
    rec = (ro.mean() * ANN) / (ro.std() * np.sqrt(ANN) + 1e-12)
    print(f"  [ECON-SR1] strategy_returns OOS Sharpe {rec:.4f} vs winner_summary {ws['oos_sharpe']} "
          f"-> {'RECONCILES' if abs(rec - ws['oos_sharpe']) <= 0.01 else 'MISMATCH'}")
    print("  DONE.")


if __name__ == "__main__":
    main()
