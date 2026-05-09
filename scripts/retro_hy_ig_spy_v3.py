#!/usr/bin/env python3
"""
Retro-apply ECON-OOS4 three-period split to hy_ig_spy artifacts.
Pair ID: hy_ig_spy_v3_retro

Steps:
1. Compute three-period split (IS / Validation / Holdout) per ECON-OOS4
2. Re-tournament on IS + Validation only (excludes holdout)
3. Final exam on holdout (ECON-FE1, schema v1.1.0)
4. evidence_status.json
5. Handoff note

Author: Econ Evan (econ-evan)
Date: 2026-05-09
"""

import os, json, warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────────────
BASE_DIR   = str(Path(__file__).resolve().parents[1])
DATA_DIR   = os.path.join(BASE_DIR, "data")
SRC_DIR    = os.path.join(BASE_DIR, "results", "hy_ig_spy")
OUT_DIR    = os.path.join(BASE_DIR, "results", "hy_ig_spy_v3_retro")
os.makedirs(OUT_DIR, exist_ok=True)

PAIR_ID    = "hy_ig_spy_v3_retro"
DATE_TAG   = datetime.now().strftime("%Y%m%d")
NOW_ISO    = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ─── Signal / strategy column maps (same as original pipeline) ─
SIGNAL_COL_MAP = {
    "S1_spread_level":   "hy_ig_spread_pct",
    "S2a_zscore_252d":   "hy_ig_zscore_252d",
    "S2b_zscore_504d":   "hy_ig_zscore_504d",
    "S3a_pctrank_504d":  "hy_ig_pctrank_504d",
    "S3b_pctrank_1260d": "hy_ig_pctrank_1260d",
    "S4a_roc_21d":       "hy_ig_roc_21d",
    "S4b_roc_63d":       "hy_ig_roc_63d",
    "S4c_roc_126d":      "hy_ig_roc_126d",
    "S5_ccc_bb_spread":  "ccc_bb_spread_pct",
    "S6_hmm_stress":     "hmm_2state_prob_stress",
    "S7_ms_stress":      "ms_2state_stress_prob",
    "S10_mom_21d":       "hy_ig_mom_21d",
    "S11_mom_63d":       "hy_ig_mom_63d",
    "S12_mom_252d":      "hy_ig_mom_252d",
    "S13_acceleration":  "hy_ig_acceleration",
}


# ═══════════════════════════════════════════════════════════════
# STEP 1 — THREE-PERIOD SPLIT (ECON-OOS4)
# ═══════════════════════════════════════════════════════════════

def compute_split(df: pd.DataFrame) -> dict:
    """
    Three-period split for hy_ig_spy_v3_retro:
      - Total sample: 2000-01-03 to 2025-12-31 (6783 trading days)
      - Holdout = last 252 trading days from end of sample
      - Pre-holdout = everything before holdout
      - ECON-OOS2 formula applied to pre-holdout to derive Validation span
      - IS = pre-holdout minus Validation
    """
    all_dates = df.index.sort_values()
    total_days = len(all_dates)

    # Holdout: last 252 trading days
    holdout_start_date = all_dates[-252]
    holdout_end_date   = all_dates[-1]
    # Pre-holdout
    pre_holdout = all_dates[all_dates < holdout_start_date]
    pre_holdout_months = round(len(pre_holdout) / 21)  # approx months

    # ECON-OOS2 on pre-holdout span
    val_months = min(max(36, round(pre_holdout_months * 0.25)), 120)
    val_days   = val_months * 21  # approx trading days

    val_start_date = pre_holdout[-val_days] if val_days < len(pre_holdout) else pre_holdout[0]
    val_end_date   = pre_holdout[-1]

    is_end_date    = pre_holdout[pre_holdout < val_start_date][-1]
    is_start_date  = all_dates[0]

    split = {
        "pair_id":             PAIR_ID,
        "split_design":        "three_period",
        "total_trading_days":  total_days,
        "sample_start":        str(is_start_date.date()),
        "sample_end":          str(holdout_end_date.date()),
        # IS
        "is_start":            str(is_start_date.date()),
        "is_end":              str(is_end_date.date()),
        "is_days":             int((all_dates <= is_end_date).sum()),
        # Validation
        "val_start":           str(val_start_date.date()),
        "val_end":             str(val_end_date.date()),
        "val_months_approx":   val_months,
        "val_days_approx":     int((all_dates >= val_start_date).sum() - 252),
        # Holdout
        "holdout_start":       str(holdout_start_date.date()),
        "holdout_end":         str(holdout_end_date.date()),
        "holdout_days":        252,
        "pre_holdout_months_approx": pre_holdout_months,
        "econ_oos2_formula":   f"val_months = min(max(36, round({pre_holdout_months}×0.25)), 120) = {val_months}",
        "generated_at":        NOW_ISO,
    }
    return split


# ═══════════════════════════════════════════════════════════════
# HELPERS: threshold + position replay
# ═══════════════════════════════════════════════════════════════

def compute_threshold(is_signal, threshold_name, signal_series):
    if threshold_name.startswith("T1_p"):
        pct = int(threshold_name.split("p")[1])
        return float(is_signal.quantile(pct / 100))
    elif threshold_name.startswith("T2_rp"):
        pct = int(threshold_name.split("rp")[1])
        return signal_series.rolling(504, min_periods=400).quantile(pct / 100)
    elif threshold_name.startswith("T3_z"):
        return float(threshold_name.split("z")[1])
    elif threshold_name.startswith(("T4_", "T5_")):
        return float(threshold_name.rsplit("_", 1)[1])
    return None


def replay(work, sig_col, threshold_name, threshold_val, strategy, lead=0):
    signal = work[sig_col].shift(lead) if lead > 0 else work[sig_col]
    if isinstance(threshold_val, pd.Series):
        threshold_val = threshold_val.reindex(work.index)

    if threshold_name.startswith("T3_z"):
        rm = signal.rolling(504, min_periods=400).mean()
        rs = signal.rolling(504, min_periods=400).std().replace(0, np.nan)
        bullish = (signal - rm) / rs < threshold_val
    else:
        bullish = signal < threshold_val

    if strategy == "P1":
        pos = bullish.astype(float)
    elif strategy == "P2":
        smin = signal.rolling(504, min_periods=400).min()
        smax = signal.rolling(504, min_periods=400).max()
        sr   = (smax - smin).replace(0, np.nan)
        pos  = (1 - (signal - smin) / sr).clip(0, 1)
    elif strategy == "P3":
        pos = bullish.astype(float) * 2 - 1
    else:
        pos = bullish.astype(float)

    strat_ret = pos.shift(1) * work["spy_ret"]
    return pos, strat_ret


def sharpe(r: pd.Series) -> float:
    r = r.dropna()
    if len(r) < 10 or r.std() == 0:
        return 0.0
    return float(r.mean() / r.std() * np.sqrt(252))


def mdd(r: pd.Series) -> float:
    r = r.dropna()
    if len(r) == 0:
        return 0.0
    cum = (1 + r).cumprod()
    dd  = ((cum - cum.cummax()) / cum.cummax()).min()
    return float(dd)


def ann_return(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.mean() * 252)


# ═══════════════════════════════════════════════════════════════
# STEP 2 — RE-TOURNAMENT on IS + Validation
# ═══════════════════════════════════════════════════════════════

def run_tournament(work, split, original_winner):
    is_end   = pd.Timestamp(split["is_end"])
    val_end  = pd.Timestamp(split["val_end"])
    # Holdout excluded from tournament
    tourn_mask = work.index <= val_end
    tourn_work = work[tourn_mask].copy()

    is_mask  = tourn_work.index <= is_end
    oos_mask = tourn_work.index > is_end  # = validation window

    results = []
    leads = [0, 1, 5, 10, 21, 63]

    for sig_name, sig_col in SIGNAL_COL_MAP.items():
        if sig_col not in tourn_work.columns:
            continue
        signal = tourn_work[sig_col]
        if signal.notna().sum() < 200:
            continue

        for lead in leads:
            sig_l    = signal.shift(lead) if lead > 0 else signal
            is_sig   = sig_l[is_mask].dropna()
            if len(is_sig) < 100:
                continue

            # Build thresholds
            thresholds = {}
            if sig_name in ("S6_hmm_stress", "S7_ms_stress"):
                for p in [0.5, 0.7]:
                    pfx = "T4" if sig_name == "S6_hmm_stress" else "T5"
                    sfx = "hmm" if "hmm" in sig_name else "ms"
                    thresholds[f"{pfx}_{sfx}_{p}"] = p
            else:
                for pct in [75, 85, 95]:
                    thresholds[f"T1_p{pct}"] = is_sig.quantile(pct / 100)
                for pct in [75, 85, 95]:
                    thresholds[f"T2_rp{pct}"] = sig_l.rolling(504, min_periods=400).quantile(pct / 100)
                for z in [1.5, 2.0, 2.5]:
                    thresholds[f"T3_z{z}"] = z

            for tname, tval in thresholds.items():
                for strat in ["P1", "P2", "P3"]:
                    try:
                        _, strat_ret = replay(tourn_work, sig_col, tname, tval, strat, lead)
                        is_r  = strat_ret[is_mask].dropna()
                        oos_r = strat_ret[oos_mask].dropna()
                        if len(is_r) < 100 or len(oos_r) < 50:
                            continue

                        oos_sharpe_ = sharpe(oos_r)
                        oos_dd      = mdd(oos_r)
                        oos_ann_ret = ann_return(oos_r)
                        pos_col     = replay(tourn_work, sig_col, tname, tval, strat, lead)[0]
                        turnover    = pos_col.diff().abs().sum() / max(len(pos_col.dropna()) / 252, 1)
                        n_trades    = int(pos_col.diff().abs().gt(0.05).sum())
                        win_rate    = float((oos_r > 0).sum() / len(oos_r))
                        valid_flag  = (oos_sharpe_ > 0 and turnover < 24 and n_trades >= 10)

                        results.append({
                            "signal":         sig_name,
                            "threshold":      tname,
                            "strategy":       strat,
                            "lead_days":      lead,
                            "val_sharpe":     round(oos_sharpe_, 4),
                            "val_ann_return": round(oos_ann_ret, 6),
                            "max_drawdown":   round(oos_dd, 6),
                            "win_rate":       round(win_rate, 4),
                            "n_trades":       n_trades,
                            "annual_turnover":round(turnover, 2),
                            "valid":          valid_flag,
                            "val_n":          len(oos_r),
                        })
                    except Exception:
                        continue

    rdf = pd.DataFrame(results)
    # Benchmark (B&H on validation window)
    bh_r = tourn_work.loc[oos_mask, "spy_ret"].dropna()
    if len(bh_r) > 0:
        bh_cum = (1 + bh_r).cumprod()
        bh_dd  = float(((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min())
        rdf = pd.concat([rdf, pd.DataFrame([{
            "signal": "BENCHMARK", "threshold": "BUY_HOLD", "strategy": "BH",
            "lead_days": 0, "val_sharpe": round(sharpe(bh_r), 4),
            "val_ann_return": round(ann_return(bh_r), 6), "max_drawdown": round(bh_dd, 6),
            "win_rate": round(float((bh_r > 0).mean()), 4), "n_trades": 1,
            "annual_turnover": 0.0, "valid": True, "val_n": len(bh_r),
        }])], ignore_index=True)

    # Save
    fname = f"tournament_results_retro_{DATE_TAG}.csv"
    rdf.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"  Tournament saved: {fname} ({len(rdf)-1} combos)")

    # Pick winner (ECON-T3 tie-break)
    valid_df = rdf[rdf["valid"] & (rdf["signal"] != "BENCHMARK")]
    if len(valid_df) == 0:
        raise RuntimeError("No valid combos in re-tournament.")
    winner = valid_df.sort_values(
        ["val_sharpe", "val_ann_return", "max_drawdown", "n_trades", "signal"],
        ascending=[False, False, True, False, True]
    ).iloc[0]

    orig_sig   = original_winner["winner_signal"]
    orig_thr   = original_winner["winner_threshold"]
    orig_strat = original_winner["winner_strategy"]
    orig_lead  = original_winner.get("lead_days", 0)

    winner_changed = not (
        winner["signal"]    == orig_sig   and
        winner["threshold"] == orig_thr   and
        winner["strategy"]  == orig_strat and
        int(winner["lead_days"]) == int(orig_lead)
    )

    return rdf, winner, winner_changed


# ═══════════════════════════════════════════════════════════════
# STEP 3 — FINAL EXAM ON HOLDOUT (ECON-FE1)
# ═══════════════════════════════════════════════════════════════

def run_final_exam(work, split, winner_row, bm_row_val):
    holdout_start = pd.Timestamp(split["holdout_start"])
    holdout_end   = pd.Timestamp(split["holdout_end"])
    val_start     = pd.Timestamp(split["val_start"])
    is_end        = pd.Timestamp(split["is_end"])

    holdout_mask = (work.index >= holdout_start) & (work.index <= holdout_end)
    holdout_work = work[holdout_mask].copy()

    sig_name = winner_row["signal"]
    sig_col  = SIGNAL_COL_MAP.get(sig_name)
    if sig_col is None or sig_col not in work.columns:
        raise RuntimeError(f"Signal column missing: {sig_name} -> {sig_col}")

    tname = winner_row["threshold"]
    strat = winner_row["strategy"]
    lead  = int(winner_row["lead_days"])

    # Compute threshold value using IS data only
    is_mask   = work.index <= is_end
    is_signal = work.loc[is_mask, sig_col].dropna()
    tval      = compute_threshold(is_signal, tname, work[sig_col])

    # Compute position on full dataset (needed so rolling lookbacks are populated),
    # then slice returns to the holdout window only.
    _, full_strat_ret = replay(work, sig_col, tname, tval, strat, lead)
    holdout_ret = full_strat_ret[holdout_mask].dropna()

    fe_sharpe  = sharpe(holdout_ret)
    fe_mdd     = mdd(holdout_ret)
    fe_ann_ret = ann_return(holdout_ret)

    # Buy-and-hold on holdout
    bh_ret  = holdout_work["spy_ret"].dropna()
    bh_sh   = sharpe(bh_ret)
    bh_ann  = ann_return(bh_ret)
    bh_mdd  = mdd(bh_ret)

    # Bootstrap CI (10,000 draws)
    rng = np.random.RandomState(42)
    n   = len(holdout_ret)
    arr = holdout_ret.values
    boot_sharpes = np.array([
        (s.mean() / s.std() * np.sqrt(252) if s.std() > 0 else 0)
        for s in (rng.choice(arr, size=n, replace=True) for _ in range(10000))
    ])
    ci_lo = float(np.percentile(boot_sharpes, 2.5))
    ci_hi = float(np.percentile(boot_sharpes, 97.5))
    pct_positive_boot = float((boot_sharpes > 0).mean())

    # DSR (Deflated Sharpe Ratio) — Bailey & López de Prado
    # DSR = Phi[(SR_hat * sqrt(T-1) - SR_0 * sqrt(1 - skew*SR_hat + (kurt-1)/4 * SR_hat^2)) /
    #            sqrt(1 - skew*SR_hat + (kurt/4)*SR_hat^2)]
    # Simplified: account for number of trials in validation
    n_trials = 1  # frozen winner, no additional search on holdout
    sr_hat   = fe_sharpe / np.sqrt(252)  # daily Sharpe
    skew_r   = float(stats.skew(arr))
    kurt_r   = float(stats.kurtosis(arr, fisher=True))  # excess kurtosis
    sr_0     = 0.0  # null: Sharpe = 0
    denom = np.sqrt(1 - skew_r * sr_hat + (kurt_r / 4) * sr_hat**2)
    numer = (sr_hat * np.sqrt(n - 1) - sr_0 * np.sqrt(1 - skew_r * sr_hat + ((kurt_r - 1) / 4) * sr_hat**2))
    if denom > 0 and not np.isnan(numer):
        dsr = float(stats.norm.cdf(numer / denom))
    else:
        dsr = float(stats.norm.cdf(sr_hat * np.sqrt(n)))

    # ── 10 ECON-FE1 conditions ──
    # C1: Holdout Sharpe > 0
    c1 = bool(fe_sharpe > 0)
    # C2: Holdout Sharpe > 0.5 (minimum economically meaningful threshold)
    c2 = bool(fe_sharpe > 0.5)
    # C3: Holdout Sharpe beats B&H Sharpe
    c3 = bool(fe_sharpe > bh_sh)
    # C4: MDD < 20% (ratio form: -0.20)
    c4 = bool(fe_mdd > -0.20)
    # C5: MDD better than B&H MDD
    c5 = bool(fe_mdd > bh_mdd)
    # C6: Bootstrap CI lower bound > 0
    c6 = bool(ci_lo > 0)
    # C7: Bootstrap pct positive > 90%
    c7 = bool(pct_positive_boot > 0.90)
    # C8: DSR > 0.95
    c8 = bool(dsr > 0.95)
    # C9: Ann return > 0 (holdout)
    c9 = bool(fe_ann_ret > 0)
    # C10: Ann return > B&H (holdout) — alpha
    c10 = bool(fe_ann_ret > bh_ann)

    conditions = {
        "C1_sharpe_positive":      c1,
        "C2_sharpe_gt_0.5":        c2,
        "C3_beats_bh_sharpe":      c3,
        "C4_mdd_lt_20pct":         c4,
        "C5_mdd_better_than_bh":   c5,
        "C6_boot_ci_lo_positive":  c6,
        "C7_boot_pct_pos_gt90":    c7,
        "C8_dsr_gt_0.95":          c8,
        "C9_ann_return_positive":  c9,
        "C10_alpha_positive":      c10,
    }
    conditions_passed = sum(conditions.values())
    conditions_total  = len(conditions)

    result = {
        "schema_version":        "v1.1.0",
        "split_design":          "three_period",
        "pair_id":               PAIR_ID,
        "generated_at":          NOW_ISO,
        "winner_signal":         sig_name,
        "winner_threshold":      tname,
        "winner_strategy":       strat,
        "lead_days":             lead,
        # Holdout metrics
        "holdout_start":         split["holdout_start"],
        "holdout_end":           split["holdout_end"],
        "holdout_n_days":        len(holdout_ret),
        "holdout_sharpe":        round(fe_sharpe, 4),
        "holdout_ann_return":    round(fe_ann_ret, 6),
        "holdout_mdd":           round(fe_mdd, 6),
        # Bootstrap
        "bootstrap_n":           10000,
        "boot_ci_lo_2.5":        round(ci_lo, 4),
        "boot_ci_hi_97.5":       round(ci_hi, 4),
        "boot_pct_positive":     round(pct_positive_boot, 4),
        # DSR
        "dsr":                   round(dsr, 4),
        "dsr_n_trials":          n_trials,
        "skewness":              round(skew_r, 4),
        "excess_kurtosis":       round(kurt_r, 4),
        # B&H benchmark (holdout)
        "bh_holdout_sharpe":     round(bh_sh, 4),
        "bh_holdout_ann_return": round(bh_ann, 6),
        "bh_holdout_mdd":        round(bh_mdd, 6),
        "bh_holdout_n_days":     len(bh_ret),
        # Conditions
        "conditions":            conditions,
        "conditions_passed":     conditions_passed,
        "conditions_total":      conditions_total,
        "conditions_pass_rate":  round(conditions_passed / conditions_total, 4),
    }

    fname = f"final_exam_results_{DATE_TAG}.json"
    with open(os.path.join(OUT_DIR, fname), "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Final exam saved: {fname}")
    print(f"  Holdout Sharpe={fe_sharpe:.4f}  MDD={fe_mdd*100:.1f}%  DSR={dsr:.4f}")
    print(f"  Conditions passed: {conditions_passed}/{conditions_total}")

    return result


# ═══════════════════════════════════════════════════════════════
# STEP 4 — EVIDENCE STATUS
# ═══════════════════════════════════════════════════════════════

def build_evidence_status(fe_result):
    passed = fe_result["conditions_passed"]
    total  = fe_result["conditions_total"]
    fe_sh  = fe_result["holdout_sharpe"]
    dsr    = fe_result["dsr"]
    conds  = fe_result["conditions"]

    # Status logic
    if passed == total:
        status = "STRONG_PASS"
        narrative = "All 10 ECON-FE1 conditions satisfied. Strategy passes final exam with full confidence."
    elif passed >= 8 and conds["C8_dsr_gt_0.95"] and conds["C6_boot_ci_lo_positive"]:
        status = "PASS"
        narrative = f"{passed}/{total} conditions met including DSR and bootstrap CI. Acceptable evidence."
    elif passed >= 6 and fe_sh > 0:
        status = "CONDITIONAL_PASS"
        narrative = f"{passed}/{total} conditions met but key robustness gates (DSR/CI) may be borderline."
    elif fe_sh > 0:
        status = "WEAK_PASS"
        narrative = f"Holdout Sharpe positive but only {passed}/{total} conditions met. Treat with caution."
    else:
        status = "FAIL"
        narrative = f"Holdout Sharpe ≤ 0 or insufficient conditions ({passed}/{total}). Do not deploy."

    ev = {
        "pair_id":              PAIR_ID,
        "generated_at":         NOW_ISO,
        "split_design":         "three_period",
        "evidence_status":      status,
        "conditions_passed":    passed,
        "conditions_total":     total,
        "holdout_sharpe":       fe_result["holdout_sharpe"],
        "holdout_ann_return":   fe_result["holdout_ann_return"],
        "holdout_mdd":          fe_result["holdout_mdd"],
        "dsr":                  fe_result["dsr"],
        "boot_ci_lo":           fe_result["boot_ci_lo_2.5"],
        "boot_pct_positive":    fe_result["boot_pct_positive"],
        "narrative":            narrative,
    }
    with open(os.path.join(OUT_DIR, "evidence_status.json"), "w") as f:
        json.dump(ev, f, indent=2)
    print(f"  Evidence status: {status}")
    return ev


# ═══════════════════════════════════════════════════════════════
# STEP 5 — HANDOFF NOTE
# ═══════════════════════════════════════════════════════════════

def write_handoff(split, original_winner, winner_row, winner_changed,
                  original_val_sharpe, new_val_sharpe, fe_result, ev):
    conds = fe_result["conditions"]
    lines = [
        f"# Evan Handoff — hy_ig_spy_v3_retro",
        f"",
        f"Generated: {NOW_ISO}",
        f"",
        f"## Split Dates (Three-Period, ECON-OOS4)",
        f"",
        f"| Period | Start | End | Days |",
        f"|--------|-------|-----|------|",
        f"| In-Sample (IS) | {split['is_start']} | {split['is_end']} | {split['is_days']} |",
        f"| Validation | {split['val_start']} | {split['val_end']} | ~{split['val_days_approx']} |",
        f"| Holdout | {split['holdout_start']} | {split['holdout_end']} | {split['holdout_days']} |",
        f"",
        f"ECON-OOS2 formula: {split['econ_oos2_formula']}",
        f"",
        f"## Original hy_ig_spy Winner Rule",
        f"",
        f"- Signal: {original_winner['winner_signal']}",
        f"- Threshold: {original_winner['winner_threshold']}",
        f"- Strategy: {original_winner['winner_strategy']}",
        f"- Lead days: {original_winner.get('lead_days', 0)}",
        f"- Original OOS Sharpe (2019-10-01 to 2026-04-22): {original_winner['oos_sharpe']}",
        f"",
        f"## Re-Tournament Result (IS + Validation Only)",
        f"",
        f"- New winner: {winner_row['signal']} / {winner_row['threshold']} / {winner_row['strategy']} / L{int(winner_row['lead_days'])}",
        f"- Validation Sharpe (new window): {winner_row['val_sharpe']}",
        f"- Validation Ann Return: {winner_row['val_ann_return']*100:.2f}%",
        f"- Validation MDD: {winner_row['max_drawdown']*100:.1f}%",
        f"",
        f"**Winner changed vs original hy_ig_spy: {'YES' if winner_changed else 'NO'}**",
        f"",
        f"| | Original OOS Sharpe | New Validation Sharpe |",
        f"|--|---------------------|----------------------|",
        f"| {original_winner['winner_signal']}/{original_winner['winner_threshold']}/{original_winner['winner_strategy']} | {original_val_sharpe:.4f} | {new_val_sharpe:.4f} |",
        f"",
        f"## Final Exam — Holdout ({split['holdout_start']} to {split['holdout_end']})",
        f"",
        f"| Metric | Strategy | B&H |",
        f"|--------|----------|-----|",
        f"| Sharpe | {fe_result['holdout_sharpe']} | {fe_result['bh_holdout_sharpe']} |",
        f"| Ann Return | {fe_result['holdout_ann_return']*100:.2f}% | {fe_result['bh_holdout_ann_return']*100:.2f}% |",
        f"| MDD | {fe_result['holdout_mdd']*100:.1f}% | {fe_result['bh_holdout_mdd']*100:.1f}% |",
        f"| DSR | {fe_result['dsr']} | — |",
        f"| Boot CI 95% | [{fe_result['boot_ci_lo_2.5']:.3f}, {fe_result['boot_ci_hi_97.5']:.3f}] | — |",
        f"| Boot % positive | {fe_result['boot_pct_positive']*100:.1f}% | — |",
        f"",
        f"## ECON-FE1 Condition Results ({fe_result['conditions_passed']}/{fe_result['conditions_total']} passed)",
        f"",
        f"| Condition | Result |",
        f"|-----------|--------|",
    ]
    for k, v in conds.items():
        lines.append(f"| {k} | {'PASS' if v else 'FAIL'} |")

    lines += [
        f"",
        f"## Evidence Status",
        f"",
        f"**{ev['evidence_status']}** — {ev['narrative']}",
        f"",
        f"## Output Files",
        f"",
        f"- `results/hy_ig_spy_v3_retro/oos_split_record.json`",
        f"- `results/hy_ig_spy_v3_retro/tournament_results_retro_{DATE_TAG}.csv`",
        f"- `results/hy_ig_spy_v3_retro/winner_summary.json`",
        f"- `results/hy_ig_spy_v3_retro/final_exam_results_{DATE_TAG}.json`",
        f"- `results/hy_ig_spy_v3_retro/evidence_status.json`",
        f"- `results/hy_ig_spy_v3_retro/evan_handoff_retro.md`",
    ]

    with open(os.path.join(OUT_DIR, "evan_handoff_retro.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("  Handoff note written: evan_handoff_retro.md")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  hy_ig_spy_v3_retro — Three-Period Retro Pipeline")
    print("=" * 60)

    # Load data
    df = pd.read_parquet(os.path.join(DATA_DIR, "hy_ig_spy_daily_latest.parquet"))
    print(f"  Data: {df.index.min().date()} → {df.index.max().date()}  ({len(df)} rows)")

    # Attach HMM/MS from existing signals parquet (IS-fitted, reuse for continuity)
    sig_existing = pd.read_parquet(os.path.join(SRC_DIR, "signals_20260422.parquet"))
    for col in ["hmm_2state_prob_stress", "ms_2state_stress_prob"]:
        if col in sig_existing.columns:
            df[col] = sig_existing[col].reindex(df.index)
            print(f"  Attached {col} from existing signals parquet "
                  f"({df[col].notna().sum()} non-null in new date range)")

    if "spy_ret" not in df.columns:
        df["spy_ret"] = df["spy"].pct_change()

    # STEP 1
    print("\n--- STEP 1: Three-Period Split ---")
    split = compute_split(df)
    with open(os.path.join(OUT_DIR, "oos_split_record.json"), "w") as f:
        json.dump(split, f, indent=2)
    print(f"  IS:    {split['is_start']} → {split['is_end']} ({split['is_days']} days)")
    print(f"  Val:   {split['val_start']} → {split['val_end']}")
    print(f"  Hold:  {split['holdout_start']} → {split['holdout_end']} (252 days)")

    # Load original winner
    with open(os.path.join(SRC_DIR, "tournament_winner.json")) as f:
        original_winner = json.load(f)
    print(f"\n  Original winner: {original_winner['winner_signal']} / "
          f"{original_winner['winner_threshold']} / {original_winner['winner_strategy']}")
    print(f"  Original OOS Sharpe: {original_winner['oos_sharpe']}")

    # STEP 2
    print("\n--- STEP 2: Re-Tournament (IS + Validation) ---")
    tourn_df, winner_row, winner_changed = run_tournament(df, split, original_winner)

    # Compute original winner's Sharpe on new validation window for comparison
    val_start = pd.Timestamp(split["val_start"])
    val_end   = pd.Timestamp(split["val_end"])
    is_end    = pd.Timestamp(split["is_end"])
    val_mask  = (df.index >= val_start) & (df.index <= val_end)

    orig_sig_col = SIGNAL_COL_MAP.get(original_winner["winner_signal"])
    orig_is_sig  = df.loc[df.index <= is_end, orig_sig_col].dropna() if orig_sig_col else pd.Series()
    orig_tval    = compute_threshold(orig_is_sig, original_winner["winner_threshold"],
                                     df[orig_sig_col]) if orig_sig_col else None

    if orig_sig_col and orig_tval is not None:
        _, orig_val_ret = replay(df[val_mask], orig_sig_col,
                                  original_winner["winner_threshold"], orig_tval,
                                  original_winner["winner_strategy"],
                                  int(original_winner.get("lead_days", 0)))
        original_val_sharpe = sharpe(orig_val_ret.dropna())
    else:
        original_val_sharpe = float("nan")

    new_val_sharpe = float(winner_row["val_sharpe"])

    # Save winner_summary.json
    winner_summary = {
        "pair_id":           PAIR_ID,
        "generated_at":      NOW_ISO,
        "split_design":      "three_period",
        "winner_signal":     winner_row["signal"],
        "winner_threshold":  winner_row["threshold"],
        "winner_strategy":   winner_row["strategy"],
        "lead_days":         int(winner_row["lead_days"]),
        "val_sharpe":        float(winner_row["val_sharpe"]),
        "val_ann_return":    float(winner_row["val_ann_return"]),
        "val_mdd":           float(winner_row["max_drawdown"]),
        "val_n_trades":      int(winner_row["n_trades"]),
        "val_period_start":  split["val_start"],
        "val_period_end":    split["val_end"],
        "winner_changed_vs_original": winner_changed,
        "original_winner_signal":    original_winner["winner_signal"],
        "original_winner_threshold": original_winner["winner_threshold"],
        "original_winner_strategy":  original_winner["winner_strategy"],
    }
    with open(os.path.join(OUT_DIR, "winner_summary.json"), "w") as f:
        json.dump(winner_summary, f, indent=2)
    print(f"  Winner: {winner_row['signal']} / {winner_row['threshold']} / "
          f"{winner_row['strategy']} / L{int(winner_row['lead_days'])}")
    print(f"  Val Sharpe: {new_val_sharpe:.4f}  | Changed: {winner_changed}")

    # STEP 3
    print("\n--- STEP 3: Final Exam on Holdout ---")
    bm_row_val = tourn_df[tourn_df["signal"] == "BENCHMARK"].iloc[0] if len(
        tourn_df[tourn_df["signal"] == "BENCHMARK"]) > 0 else None
    fe_result = run_final_exam(df, split, winner_row, bm_row_val)

    # STEP 4
    print("\n--- STEP 4: Evidence Status ---")
    ev = build_evidence_status(fe_result)

    # STEP 5
    print("\n--- STEP 5: Handoff Note ---")
    write_handoff(split, original_winner, winner_row, winner_changed,
                  original_val_sharpe, new_val_sharpe, fe_result, ev)

    print("\n" + "=" * 60)
    print("  COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
