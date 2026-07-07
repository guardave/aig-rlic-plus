#!/usr/bin/env python3
"""GH #13 — regenerate lead-coherence artifacts for an already-published pair.

Emits, per pair, WITHOUT re-selecting or mutating the frozen winner:

  1. results/{pair}/lead_winner_curve_{date}.csv   — the published winner combo's
     OWN OOS-Sharpe-by-lead curve (re-scored at each lead of the chart grid via the
     pair's NATIVE derive_winner_series; peaks at/near the winner's lead by design).
  2. results/{pair}/lead_clean_envelope_{date}.csv — the cross-signal best-per-lead
     envelope. None of the 11 GH#13 rollout pairs carry seasonally-contaminated
     signals, so best_clean == best_raw by construction (columns emitted for schema
     parity with the cass reference).
  3. patches results/{pair}/lead_sweep_manifest_{date}.json with the coherent-view
     fields (lead_winner_curve_file, lead_clean_envelope_file, best_clean_*,
     winner_curve_peak_lead, assertions).

FROZEN-WINNER SAFETY. The winner combo is read from the pair's own tournament_results
CSV (native naming). derive_winner_series only RE-SCORES that fixed combo at other
leads; it never re-selects. Hard acceptance gate: the curve's value AT the winner's
own lead must reconcile to winner_summary.oos_sharpe within RECONCILE_TOL, else the
pair BLOCKS (non-zero exit) and writes nothing.

NO LLM anywhere — pure pandas/numpy, portable for every dev.

Usage:  python scripts/refresh_lead_coherence_artifacts.py <pair> [<pair> ...]
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]

RECONCILE_TOL = 0.03  # |curve@winner_lead - winner_summary.oos_sharpe| must be <= this
LOOKBACKS = {"LB36": 36, "LB60": 60, "LB120": 120}


def _sharpe_monthly(rets: pd.Series) -> float:
    # mirror native ann_metrics: degenerate (empty or zero-vol) series -> 0.0,
    # NOT NaN — otherwise degenerate combos become invisible to gate 2.
    r = rets.dropna()
    if len(r) == 0 or r.std() == 0:
        return 0.0
    return float(r.mean() / r.std() * np.sqrt(12))


def derive_winner_position(work: pd.DataFrame, winner: dict, split: dict,
                           signal_col: str) -> pd.Series:
    """Reconstruct the winner combo's position series at winner['lead_months'].

    Verbatim port of the shared cass/monthly-template rule used by the native
    pipelines (pair_pipeline_*.derive_winner_series). Pure pandas — no pipeline
    import, no scipy. Per-pair correctness is guaranteed by the reconciliation
    gate in refresh(), which reproduces winner_summary.oos_sharpe at the winner's
    own lead before trusting the curve at any other lead.
    """
    is_mask = work.index <= split["in_sample_end"]
    sig = work[signal_col].shift(int(winner["lead_months"]))
    thr_name, lb_name = str(winner["threshold"]), str(winner["lookback"])
    if thr_name.startswith("T1_fixed_p"):
        thr = sig[is_mask].dropna().quantile(int(thr_name.split("p")[-1]) / 100)
    elif thr_name == "T4_zero":
        thr = 0.0
    elif thr_name == "T4_gap50":
        thr = 50.0
    elif thr_name == "T4_above50":
        thr = 0.5
    elif thr_name.startswith("T2_roll_p"):
        lb = LOOKBACKS[lb_name]
        thr = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24)).quantile(
            int(thr_name.split("p")[-1]) / 100)
    elif thr_name.startswith("T3_zscore"):
        lb = LOOKBACKS[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24))
        k = float(thr_name.split("_")[-1])
        thr = roll.mean() - k * roll.std() if "neg_" in thr_name else roll.mean() + k * roll.std()
    else:
        raise ValueError(f"unrecognised threshold {thr_name!r}")
    above = sig < thr if "neg_" in thr_name else sig > thr
    strat, orientation = str(winner["strategy"]).rsplit("_", 1)
    pos_bool = ~above if orientation == "counter" else above
    if strat == "P1_long_cash":
        position = pos_bool.astype(float)
    elif strat == "P2_signal_strength":
        lb = LOOKBACKS[lb_name]
        roll = sig.rolling(lb, min_periods=max(int(lb * 0.6), 24))
        rng = (roll.max() - roll.min()).replace(0, np.nan)
        raw = ((sig - roll.min()) / rng).clip(0, 1)
        position = 1 - raw if orientation == "counter" else raw
    else:  # P3_long_short
        position = pos_bool.astype(float) * 2 - 1
    return position


def _split_from_work(work: pd.DataFrame, target_col: str) -> dict:
    """ECON-OOS2 v1_max36_25pct_cap120 — the universal monthly split policy."""
    w = work.dropna(subset=[target_col])
    n = len(w)
    oos_n = int(min(max(36, round(n * 0.25)), 120))
    return {
        "in_sample_end": w.index[-(oos_n + 1)],
        "oos_start": w.index[-oos_n],
        "oos_end": w.index[-1],
    }


def score_combo(work: pd.DataFrame, combo: dict, lead: int, split: dict,
                tgt_ret: pd.Series, signal_col: str) -> dict:
    """Score one combo at one lead exactly as the native monthly tournament does:
    strat_ret = position * tgt_ret (signal pre-lagged by `lead` -> no lookahead for
    lead>=1), OOS on [oos_start:oos_end], valid = sharpe>0.3 & turnover<24 & oos_n>=24.
    """
    position = derive_winner_position(work, dict(combo, lead_months=lead), split, signal_col)
    strat = position * tgt_ret
    oos_mask = (strat.index >= split["oos_start"]) & (strat.index <= split["oos_end"])
    is_mask = strat.index <= split["in_sample_end"]
    is_r, oos_r = strat[is_mask].dropna(), strat[oos_mask].dropna()
    if len(is_r) < 60 or len(oos_r) < 24:
        return dict(oos_sharpe=float("nan"), valid=False, oos_n=len(oos_r))
    sharpe = _sharpe_monthly(oos_r)
    pos_oos = position[oos_mask]
    n_trades = int((pos_oos.diff().abs() > 1e-9).sum())
    years = len(pos_oos.dropna()) / 12
    turnover = n_trades / years if years > 0 else 999
    valid = bool(sharpe > 0.3 and turnover < 24 and len(oos_r) >= 24)
    return dict(oos_sharpe=round(sharpe, 4), valid=valid, oos_n=len(oos_r))


def parse_signal_cols(pipeline_src: Path) -> dict:
    """Extract the SIGNAL_COLS {code -> parquet column} map from pipeline source,
    without importing it (the pipelines pull in scipy/statsmodels at import time)."""
    src = pipeline_src.read_text()
    block = re.search(r"SIGNAL_COLS\s*=\s*\{(.*?)\n\}", src, re.S).group(1)
    pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', block)
    return dict(pairs)


# ── per-pair config ───────────────────────────────────────────────────────────
# Monthly-native pairs whose winner follows the shared cass/monthly template.
# `work_parquet` must carry every signal column AND the target-return column.
ADAPTERS = {
    "ism_services_spy": dict(
        work_parquet="data/ism_services_spy_monthly_latest.parquet",
        signals_parquet="results/ism_services_spy/signals_20260618.parquet",  # derived cols (HMM/markov)
        target_col="spy_ret",
        pipeline="scripts/pair_pipeline_ism_services_spy.py",
    ),
}


def _winner_row(pair: str, ws: dict) -> pd.Series:
    """The frozen winner row in NATIVE tournament naming (source of the combo spec).

    Identify the published combo by its winner_summary fields (signal_code,
    threshold_code, strategy_family) rather than blind argmax — the published winner
    may be a robustness/tie-break pick that is NOT the top-Sharpe row for its
    signal/lead. Falls back to argmax only if the exact combo is absent, and the
    caller's reconciliation gate is the backstop either way.
    """
    tr = sorted(glob.glob(str(REPO / f"results/{pair}/tournament_results_*.csv")))
    df = pd.read_csv(tr[-1])
    lead = int(ws["lead_value"])
    cand = df[(df.lead_months == lead) & df.get("valid", True)]
    sig_native = ws["signal_code"].replace(f"{pair.rsplit('_', 1)[0]}_", "")
    m = cand[cand.signal == sig_native]
    if ws.get("threshold_code"):
        m = m[m.threshold == ws["threshold_code"]]
    if ws.get("strategy_family"):  # strategy carries an orientation suffix (_pro/_counter)
        m = m[m.strategy.str.startswith(ws["strategy_family"])]
    pool = m if len(m) else cand[cand.signal == sig_native] if len(cand[cand.signal == sig_native]) else cand
    return pool.sort_values("oos_sharpe", ascending=False).iloc[0]


def refresh(pair: str) -> int:
    ad = ADAPTERS[pair]
    results = REPO / "results" / pair

    ws = json.load(open(results / "winner_summary.json"))
    work = pd.read_parquet(REPO / ad["work_parquet"])
    work = work[~work.index.duplicated(keep="last")].sort_index()
    if ad.get("signals_parquet"):  # merge in derived signal cols missing from the target parquet
        sig_df = pd.read_parquet(REPO / ad["signals_parquet"])
        sig_df = sig_df[~sig_df.index.duplicated(keep="last")].sort_index()
        for c in sig_df.columns:
            if c not in work.columns:
                work[c] = sig_df[c].reindex(work.index)
    tgt = ad["target_col"]
    # align the scoring frame to the native tournament exactly: it scores on
    # df.dropna(subset=[target]) (target availability bounds the sample), so drop
    # leading target-NaN rows before split/rolling/quantile computation.
    work = work.dropna(subset=[tgt])
    split = _split_from_work(work, tgt)
    tgt_ret = work[tgt]
    signal_col = ws["signal_column"]

    win = _winner_row(pair, ws)
    winner = {"signal": win.signal, "threshold": win.threshold, "strategy": win.strategy,
              "lookback": win.lookback}
    win_lead = int(ws["lead_value"])
    signal_cols = parse_signal_cols(REPO / ad["pipeline"])

    # native combo universe = this pair's OWN tournament grid (already validity- and
    # methodology-defined); re-scored at every lead by the shared native rule.
    tr = pd.read_csv(sorted(glob.glob(str(results / "tournament_results_*.csv")))[-1])
    tr = tr[tr.signal != "BENCHMARK"]
    combos = tr[["signal", "threshold", "strategy", "lookback"]].drop_duplicates().to_dict("records")
    native_leads = sorted(int(x) for x in tr.lead_months.unique() if int(x) >= 1)

    # monthly tradable grid: L1 (real-time floor) .. L12. L0 excluded — for a monthly
    # signal L0 is contemporaneous (lookahead), which is why the native tournament
    # never scores it.
    leads = list(range(1, 13))
    man_path = Path(sorted(f for f in glob.glob(str(results / "lead_sweep_manifest_*.json"))
                           if "weekly" not in f)[-1])
    date_tag = re.search(r"(\d{8})", man_path.name).group(1)

    def col_of(sig_code: str) -> str:
        return signal_cols.get(sig_code, sig_code)

    # ── acceptance gate 1: reproduce the frozen winner Sharpe at its own lead ──
    got = score_combo(work, winner, win_lead, split, tgt_ret, col_of(winner["signal"]))["oos_sharpe"]
    ref = float(ws["oos_sharpe"])
    if not (abs(got - ref) <= RECONCILE_TOL):
        print(f"[{pair}] BLOCKED — winner reconciliation failed: {got:.4f} vs "
              f"winner_summary {ref:.4f} (tol {RECONCILE_TOL})", file=sys.stderr)
        return 2

    # ── acceptance gate 2: reproduce native tournament_results per-combo at native
    #    leads (validates the whole envelope reconstruction, not just the winner) ──
    mism = 0
    for r in tr.itertuples():
        s = score_combo(work, {"signal": r.signal, "threshold": r.threshold,
                               "strategy": r.strategy, "lookback": r.lookback},
                        int(r.lead_months), split, tgt_ret, col_of(r.signal))["oos_sharpe"]
        # count NaN as a mismatch too: a combo that native scored but the
        # reconstruction cannot must not be silently excused.
        if pd.isna(s) or abs(s - float(r.oos_sharpe)) > 0.02:
            mism += 1
    rate = mism / len(tr)
    if rate > 0.02:
        print(f"[{pair}] BLOCKED — envelope reconstruction mismatch {mism}/{len(tr)} "
              f"({rate:.1%}) vs tournament_results (>2%)", file=sys.stderr)
        return 2
    print(f"[{pair}] reconcile OK @ L{win_lead}: {got:.4f} vs {ref:.4f}; "
          f"per-combo match {len(tr)-mism}/{len(tr)}")

    # ── artifact 1: winner curve (native rule, L1..12) ──
    wc = pd.DataFrame([
        {"lead_months": L,
         "oos_sharpe": score_combo(work, winner, L, split, tgt_ret, col_of(winner["signal"]))["oos_sharpe"],
         "is_published_winner": bool(L == win_lead)}
        for L in leads])
    wc_path = results / f"lead_winner_curve_{date_tag}.csv"
    wc.to_csv(wc_path, index=False)
    peak_lead = int(wc.loc[wc.oos_sharpe.idxmax(), "lead_months"]) if wc.oos_sharpe.notna().any() else -1

    # ── artifact 2: native clean envelope (best VALID combo per lead; clean==raw,
    #    no contamination on these pairs). Same grid as the winner curve. ──
    env_rows = []
    for L in leads:
        best_s, best_sig = float("nan"), ""
        for c in combos:
            sc = score_combo(work, c, L, split, tgt_ret, col_of(c["signal"]))
            if sc["valid"] and (pd.isna(best_s) or sc["oos_sharpe"] > best_s):
                best_s, best_sig = sc["oos_sharpe"], col_of(c["signal"])
        env_rows.append({"lead_months": L, "best_oos_sharpe": best_s, "best_signal": best_sig,
                         "best_is_clean": True, "best_clean_oos_sharpe": best_s,
                         "best_clean_signal": best_sig})
    env = pd.DataFrame(env_rows)
    env_path = results / f"lead_clean_envelope_{date_tag}.csv"
    env.to_csv(env_path, index=False)

    # ── coherence invariant: envelope >= winner curve at every lead ──
    merged = wc.merge(env[["lead_months", "best_oos_sharpe"]], on="lead_months")
    bad = merged[merged.oos_sharpe > merged.best_oos_sharpe + 1e-6]
    if len(bad):
        print(f"[{pair}] BLOCKED — winner curve exceeds envelope at leads "
              f"{bad.lead_months.tolist()} (grid inconsistency)", file=sys.stderr)
        wc_path.unlink(missing_ok=True); env_path.unlink(missing_ok=True)
        return 2
    L_star_native = int(env.loc[env.best_oos_sharpe.idxmax(), "lead_months"])

    # envelope flatness + ground-truth honesty: only native_leads carry per-combo
    # ground truth (validated by gate 2); other leads are interpolations of the
    # SAME native scoring rule and must be labelled as such.
    interp_leads = [L for L in leads if L not in native_leads]
    env_vals = env.best_oos_sharpe.dropna()
    env_top2 = env_vals.sort_values(ascending=False).head(2).tolist()
    peak_margin = round(env_top2[0] - env_top2[1], 4) if len(env_top2) == 2 else None
    env_flat = bool(peak_margin is not None and peak_margin < 0.10)  # < recon noise band

    # ── manifest patch ──
    # `L_star` (pre-existing) is the exploratory monthly SWEEP peak — left untouched.
    man = json.load(open(man_path))
    best_env = float(env.best_oos_sharpe.max())
    man.update({
        "lead_winner_curve_file": f"{pair}/{wc_path.name}",
        "lead_clean_envelope_file": f"{pair}/{env_path.name}",
        "clean_envelope_note": "No seasonally-contaminated signals -> clean == raw envelope. "
                               "Winner curve and envelope use the NATIVE scoring rule; "
                               "envelope >= winner curve at every lead where a valid combo exists.",
        "winner_curve_peak_lead": peak_lead,
        "coherent_envelope_L_star": L_star_native,
        "coherent_envelope_peak_margin": peak_margin,
        "coherent_envelope_is_flat": env_flat,
        "native_ground_truth_leads": native_leads,
        "interpolated_leads": interp_leads,
        "best_clean_oos_sharpe_at_grid": round(best_env, 4),
        "best_clean_oos_sharpe_at_grid_signal": env.loc[env.best_oos_sharpe.idxmax(), "best_signal"],
    })
    flat_clause = (f" the native envelope is nearly flat (top-two margin "
                   f"{peak_margin}, within reconstruction/OOS noise), so L{L_star_native} is a "
                   f"marginal peak, not a decisive one;" if env_flat else "")
    asserts = man.get("assertions", [])
    note = (f"[GH#13] published winner ({winner['signal']}/{winner['threshold']}/"
            f"{winner['strategy']}/L{win_lead}, OOS {ref:.4f}) selected for risk-adjusted "
            f"robustness. On the native scoring rule its own curve peaks at L{peak_lead} and "
            f"the cross-signal envelope peaks at L{L_star_native};{flat_clause} ground-truth "
            f"leads {native_leads} (gate-2 validated vs tournament_results), leads {interp_leads} "
            f"interpolated by the same rule -> lead_winner_curve_{date_tag}.csv.")
    if note not in asserts:
        asserts.append(note)
    man["assertions"] = asserts
    json.dump(man, open(man_path, "w"), indent=2)

    print(f"[{pair}] wrote {wc_path.name} (winner peak L{peak_lead}), {env_path.name} "
          f"(envelope L*={L_star_native}, margin {peak_margin}, flat={env_flat}); "
          f"ground-truth {native_leads}, interp {interp_leads}.")
    return 0


def main() -> int:
    pairs = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not pairs:
        print("usage: refresh_lead_coherence_artifacts.py <pair> [<pair> ...]", file=sys.stderr)
        return 1
    rc = 0
    for p in pairs:
        if p not in ADAPTERS:
            print(f"[{p}] no adapter registered — skipping", file=sys.stderr)
            rc = max(rc, 1)
            continue
        rc = max(rc, refresh(p))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
