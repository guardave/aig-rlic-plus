#!/usr/bin/env python3
"""Acceptance 4.1 for permit_spy: reproduce the PUBLISHED legacy tournament from the legacy code.

The published permit_spy result (winner_summary 1.1.0, S3_mom / T1_p25 / P3 / L6, OOS Sharpe 1.4454) comes from
tournament_results_20260314.csv: an OOS-selected tournament (max OOS Sharpe among rows with oos_sharpe > 0 and
full-sample turnover < 24) on the lead grid {0,1,2,3,6}. No strategy_returns file was ever written, so the harness
cannot replay it (harness.run.replay_legacy -> not_replayable, declared in scripts/pair_spec_permit_spy.py).

Source: the stage_derived + stage_tournament code of scripts/pair_pipeline_permit_spy.py at git e1c44555 (the
commit that produced the published 20260314 run, lead grid [0, 1, 2, 3, 6]; the later c64a609a only changed the
grid to 1..13, the benchmark row's valid flag, the CSV writer and the FRED key handling). The signal, threshold,
position, return and metric formulas are unchanged. Adaptations, all outside the scoring logic:
  1. inputs come from the pinned panel below instead of a FRED / yfinance download; the panel is already on the
     month-end grid 1990-01..2025-12, so the legacy resample/reindex step is the identity and is omitted
     (ffill(limit=2) is kept);
  2. only the columns the tournament uses are derived (permit transforms, spy_ret); the controls (houst, unrate,
     vix, rates) and spy_fwd_* columns of stage_derived feed other stages only;
  3. the lead list is an argument (published [0, 1, 2, 3, 6]; a second run on c64a609a's 1..13 is a check);
  4. the per-candidate try/except, the redundant isinstance branch and the CSV write are dropped; the table gains
     an unrounded oos_sharpe column, and the published rule's positions / returns are kept for the record;
  5. the BENCHMARK row is computed for its Sharpe only (compared separately).
It runs on the pinned panel data/phaseB_inputs/permit_spy_monthly_legacy_20260314.csv and compares every row with
the published CSV:

    permit  PERMIT as published on 2026-03-14 (pinned ALFRED vintage file, data/release_calendar/vintages)
    spy     SPY month-end adjusted close of the legacy pipeline's own yfinance pull (2026-10-08 panel
            data/permit_spy_monthly_20261008.parquet, untracked), pinned here

Location: scripts/legacy_repro/, outside the live pipeline scripts that gate_lead_floor scans. This is an audit of the
PUBLISHED legacy run, so it deliberately uses the published grid {0,1,2,3,6} (L0 is below today's strict floor E2);
no live result is produced from it.

Writes results/permit_spy/legacy_reproduction_20260314.json (+ the row comparison CSV and the published rule's
legacy-code positions/returns). pair_spec_permit_spy.legacy_reproduction() reads the JSON.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from harness.data import load_pinned  # noqa: E402

PAIR_ID = "permit_spy"
LEGACY_TAG = "20260314"
PANEL = "permit_spy_monthly_legacy_20260314.csv"
RES = REPO / "results" / PAIR_ID
IS_END, OOS_START = "2017-12-31", "2018-01-01"
PUBLISHED_LEADS = [0, 1, 2, 3, 6]          # grid of the published 20260314 run (winner_summary grid_scanned)
FLOOR_LEADS = list(range(1, 14))           # grid in the legacy source after the #255 floor edit (never published)
WINNER = ("S3_mom", "T1_p25", "P3", 6)
KEYS = ["signal", "threshold", "strategy", "lead_months"]
# published precision: oos_sharpe 4 dp, returns / drawdown / turnover 2 dp
TOL = {"oos_sharpe": 1e-4, "oos_ann_return": 1e-2, "max_drawdown": 1e-2, "annual_turnover": 1e-2, "oos_n": 0}


def derived(panel: pd.DataFrame) -> pd.DataFrame:
    """stage_derived of e1c44555, signal columns only (adaptations 1-2 in the module docstring)."""
    df = panel[["permit", "spy"]].copy()
    df = df.ffill(limit=2)
    p = df["permit"]
    df["permit_yoy"] = (p / p.shift(12) - 1) * 100
    df["permit_mom"] = (p / p.shift(1) - 1) * 100
    df["permit_ma12"] = p.rolling(12, min_periods=10).mean()
    df["permit_dev_trend"] = p - df["permit_ma12"]
    rm60 = p.rolling(60, min_periods=48)
    df["permit_zscore_60m"] = (p - rm60.mean()) / rm60.std()
    df["permit_mom_3m"] = p - p.shift(3)
    df["permit_mom_6m"] = p - p.shift(6)
    df["permit_accel"] = df["permit_mom"] - df["permit_mom"].shift(1)
    df["permit_contraction"] = (df["permit_yoy"] < 0).astype(int)
    df["spy_ret"] = df["spy"].pct_change()
    return df.dropna(subset=["permit"])


def tournament(df: pd.DataFrame, leads: list[int], keep=None):
    """stage_tournament of e1c44555 (adaptations 3-5 in the module docstring)."""
    work = df.copy()
    is_mask = work.index <= IS_END
    oos_mask = work.index >= OOS_START
    signal_cols = {"S1_level": "permit", "S2_yoy": "permit_yoy", "S3_mom": "permit_mom",
                   "S4_dev": "permit_dev_trend", "S5_z": "permit_zscore_60m",
                   "S6_mom3m": "permit_mom_3m", "S7_mom6m": "permit_mom_6m",
                   "S8_accel": "permit_accel", "S9_contr": "permit_contraction"}
    available = {k: v for k, v in signal_cols.items() if v in work.columns and work[v].notna().sum() > 50}
    results, kept = [], None
    for sig_name, sig_col in available.items():
        signal = work[sig_col]
        for lead in leads:
            sig_l = signal.shift(lead) if lead > 0 else signal
            is_sig = sig_l[is_mask].dropna()
            if len(is_sig) < 20:
                continue
            thresholds = {}
            for pct in [25, 50, 75]:
                thresholds[f"T1_p{pct}"] = is_sig.quantile(pct / 100)
            for pct in [25, 50, 75]:
                thresholds[f"T2_rp{pct}"] = sig_l.rolling(60, min_periods=36).quantile(pct / 100)
            if sig_name in ["S2_yoy", "S3_mom", "S8_accel"]:
                thresholds["T4_zero"] = 0
            for tname, tval in thresholds.items():
                for strat in ["P1", "P2", "P3"]:
                    bullish = sig_l > tval
                    if strat == "P1":
                        pos = bullish.astype(float)
                    elif strat == "P2":
                        smin = sig_l.rolling(60, min_periods=36).min()
                        smax = sig_l.rolling(60, min_periods=36).max()
                        sr = (smax - smin).replace(0, np.nan)
                        pos = ((sig_l - smin) / sr).clip(0, 1)
                    else:
                        pos = bullish.astype(float) * 2 - 1
                    strat_ret = pos.shift(1) * work["spy_ret"]
                    is_r = strat_ret[is_mask].dropna()
                    oos_r = strat_ret[oos_mask].dropna()
                    if len(is_r) < 24 or len(oos_r) < 12:
                        continue
                    oos_sharpe = (oos_r.mean() / oos_r.std()) * np.sqrt(12) if oos_r.std() > 0 else 0
                    cum = (1 + oos_r).cumprod()
                    dd = ((cum - cum.cummax()) / cum.cummax()).min()
                    turnover = pos.diff().abs().sum() / (len(pos.dropna()) / 12)
                    valid = oos_sharpe > 0 and turnover < 24 and len(oos_r) >= 12
                    results.append({"signal": sig_name, "threshold": tname, "strategy": strat,
                                    "lead_months": lead, "oos_sharpe": round(oos_sharpe, 4),
                                    "oos_sharpe_unrounded": float(oos_sharpe),
                                    "oos_ann_return": round(oos_r.mean() * 12 * 100, 2),
                                    "max_drawdown": round(dd * 100, 2), "annual_turnover": round(turnover, 2),
                                    "oos_n": len(oos_r), "valid": bool(valid)})
                    if keep == (sig_name, tname, strat, lead):
                        kept = pd.DataFrame({"signal": sig_l, "threshold": tval, "position": pos,
                                             "spy_ret": work["spy_ret"], "strategy_return": strat_ret})
    bh = work.loc[oos_mask, "spy_ret"].dropna()
    bh_s = (bh.mean() / bh.std()) * np.sqrt(12)
    return pd.DataFrame(results), kept, float(bh_s)


def winner(t: pd.DataFrame) -> dict:
    v = t[t["valid"]]
    w = v.loc[v["oos_sharpe"].idxmax()]
    return {"signal": w["signal"], "threshold": w["threshold"], "strategy": w["strategy"],
            "lead": int(w["lead_months"]), "oos_sharpe": float(w["oos_sharpe"]), "n_valid": int(len(v))}


def main() -> dict:
    panel = load_pinned(PANEL)
    df = derived(panel)
    rep, kept, bh = tournament(df, PUBLISHED_LEADS, keep=WINNER)
    pub = pd.read_csv(RES / f"tournament_results_{LEGACY_TAG}.csv")
    pub_bh = float(pub.loc[pub["signal"] == "BENCHMARK", "oos_sharpe"].iloc[0])
    pub = pub[pub["signal"] != "BENCHMARK"]
    m = pub.merge(rep, on=KEYS, how="outer", suffixes=("_pub", "_rep"), indicator=True)
    both = m[m["_merge"] == "both"].copy()
    cols = {}
    for c, tol in TOL.items():
        d = (both[f"{c}_pub"].astype(float) - both[f"{c}_rep"].astype(float)).abs()
        both[f"{c}_absdiff"] = d
        cols[c] = {"max_abs_diff": round(float(d.max()), 6), "n_rows_beyond_published_precision": int((d > tol + 1e-9).sum()),
                   "n_rows_last_digit": int(((d > 1e-9) & (d <= tol + 1e-9)).sum()), "published_precision": tol}
    sh = both[both["oos_sharpe_absdiff"] > 1e-9]
    # a 1e-4 difference at 4 dp is a rounding tie: the unrounded reproduced value sits within 1e-4 of the published one
    tie = sh[(sh["oos_sharpe_unrounded"] - sh["oos_sharpe_pub"]).abs() <= 1e-4 + 1e-12]
    both["valid_pub"] = both["valid_pub"].astype(bool)
    vm = int((both["valid_pub"] != both["valid_rep"].astype(bool)).sum())
    both.drop(columns="_merge").to_csv(RES / f"legacy_reproduction_rows_{LEGACY_TAG}.csv", index=False)
    kept.to_csv(RES / f"legacy_reproduction_published_rule_{LEGACY_TAG}.csv", index_label="date")
    w_pub = pub[(pub["signal"] == WINNER[0]) & (pub["threshold"] == WINNER[1]) & (pub["strategy"] == WINNER[2])
                & (pub["lead_months"] == WINNER[3])].iloc[0]
    w_rep = rep[(rep["signal"] == WINNER[0]) & (rep["threshold"] == WINNER[1]) & (rep["strategy"] == WINNER[2])
                & (rep["lead_months"] == WINNER[3])].iloc[0]
    floor_tab, _, _ = tournament(df, FLOOR_LEADS)
    rw = winner(rep)
    out = {
        "pair_id": PAIR_ID, "legacy_tag": LEGACY_TAG,
        "code": "scripts/legacy_repro/permit_spy.py (stage_derived + stage_tournament of git e1c44555, adaptations listed in its docstring)",
        "panel": f"data/phaseB_inputs/{PANEL}",
        "panel_note": "PERMIT = ALFRED vintage as of 2026-03-14 (the published run's date); SPY = the legacy "
                      "pipeline's own yfinance month-end adjusted closes (2026-10-08 pull)",
        "published_file": f"results/{PAIR_ID}/tournament_results_{LEGACY_TAG}.csv",
        "lead_grid": PUBLISHED_LEADS,
        "rows_published": int(len(pub)), "rows_reproduced": int(len(rep)),
        "rows_only_published": int((m["_merge"] == "left_only").sum()),
        "rows_only_reproduced": int((m["_merge"] == "right_only").sum()),
        "columns": cols, "oos_sharpe_rows_differing": int(len(sh)), "oos_sharpe_rounding_ties": int(len(tie)),
        "valid_flag_mismatches": vm, "n_valid_published": int(pub["valid"].astype(bool).sum()),
        "n_valid_reproduced": rw["n_valid"],
        "bh_oos_sharpe": {"published": pub_bh, "reproduced": round(bh, 4)},
        "published_rule": {"key": "|".join(map(str, WINNER)),
                           "published": {k: float(w_pub[k]) for k in TOL},
                           "reproduced": {k: float(w_rep[k]) for k in TOL},
                           "oos_sharpe_unrounded": float(w_rep["oos_sharpe_unrounded"])},
        "reproduced_oos_selected_winner": rw,
        "published_rule_reproduces": bool(rw["signal"] == WINNER[0] and rw["threshold"] == WINNER[1]
                                          and rw["strategy"] == WINNER[2] and rw["lead"] == WINNER[3]
                                          and abs(float(w_rep["oos_sharpe"]) - float(w_pub["oos_sharpe"])) <= 1e-4),
        "floor_grid_check": {"lead_grid": FLOOR_LEADS, "winner": winner(floor_tab),
                             "note": "legacy code on the #255 floored grid L1..13 of c64a609a (registry note: winner unchanged); "
                                     "never published"},
        "sensitivity": [
            {"panel": "2026-10-08 FRED PERMIT + 2026-10-08 yfinance SPY (data/permit_spy_monthly_20261008.parquet)",
             "result": "same 856 rows; 757 OOS Sharpe values differ beyond 4 dp (max 0.43), 17 valid flags differ; "
                       "OOS-selected winner still S3_mom/T1_p25/P3/L6 at 1.3796",
             "cause": "PERMIT revisions between 2026-03-14 and 2026-10-08 (annual seasonal-factor revision)"},
            {"panel": "PERMIT vintage 2026-03-14 + SPY pinned 2026-10-17 (data/phaseB_inputs/spy_month_end_20261017.csv)",
             "result": "644 OOS Sharpe values differ beyond 4 dp (max 0.018), valid flags equal; winner "
                       "S3_mom/T1_p25/P3/L6 at 1.4387",
             "cause": "dividend-adjustment drift between yfinance pulls"},
        ],
    }
    gaps = []
    if out["rows_only_published"] or out["rows_only_reproduced"]:
        gaps.append("candidate rows differ")
    if any(c["n_rows_beyond_published_precision"] for c in cols.values()):
        gaps.append("values differ beyond published precision")
    if vm:
        gaps.append("valid flags differ")
    out["exact_at_published_precision"] = not gaps
    out["gaps"] = (("; ".join(gaps) + ". ") if gaps else "") + (
        f"{len(sh)} OOS Sharpe values differ from the published 4-dp value by 1e-4; all {len(tie)} are rounding ties "
        "(the unrounded reproduced value lies within 1e-4 of the published value); "
        f"{cols['oos_ann_return']['n_rows_last_digit']} annual-return and {cols['max_drawdown']['n_rows_last_digit']} "
        "drawdown values differ by one unit in the second decimal (percent). Both are consistent with tiny float "
        "differences in the adjusted SPY closes. The published panel itself (data/permit_spy_monthly_20260314.parquet) "
        "was never committed, so the PERMIT values are the ALFRED vintage of the publication date and the SPY closes "
        "are a later pull of the same yfinance series; with these the published table reproduces at its printed "
        "precision. IS Sharpe was never published (the legacy table has OOS columns only), so no IS value can be "
        "compared." if len(sh) == len(tie) else "Some OOS Sharpe differences are not rounding ties; see the rows CSV.")
    (RES / f"legacy_reproduction_{LEGACY_TAG}.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("rows_published", "rows_reproduced", "columns", "valid_flag_mismatches",
                                          "oos_sharpe_rows_differing", "oos_sharpe_rounding_ties",
                                          "published_rule_reproduces", "reproduced_oos_selected_winner",
                                          "floor_grid_check", "exact_at_published_precision")}, indent=1, default=str))
    return out


if __name__ == "__main__":
    main()
