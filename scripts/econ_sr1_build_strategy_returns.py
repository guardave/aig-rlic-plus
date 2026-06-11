#!/usr/bin/env python3
"""ECON-SR1 builder: reconciled canonical strategy-return series for the 3 pairs
whose fix260526 W0.5 reconstruction was defective (vix_vix3m_spy, indpro_spy,
indpro_xlp).

Per ECON-SR1 (econometrics-agent-sop.md, added 2026-06-11):
  1. Preferred reconstruction source is `results/{pair}/winner_trade_log.csv`
     (replay of recorded positions) — no threshold/direction parameterisation
     to get wrong.
  2. The replayed series MUST reconcile to winner_summary.json headline
     metrics (oos_sharpe ±0.01, oos_max_drawdown ±0.5pp, oos_ann_return
     ±0.5pp) BEFORE any downstream artifact is emitted from it.
  3. Output: results/{pair}/strategy_returns_{date}.csv with columns
     [date, position, strategy_return, bh_return]. One series, many
     consumers (charts, broker CSVs, subperiod tables read this file;
     they never re-run derivation code).

Position semantics (IMPORTANT for consumers):
  `position` on row t is the RETURN-ACCRUAL WEIGHT for period t — i.e. the
  exposure that earns that row's `bh_return`. This already embeds the
  pipelines' `position.shift(1)` execution-lag convention
  (strategy_return = position * bh_return holds row-wise, exactly).

Replay conventions (mirror the original producers):
  - vix_vix3m_spy / indpro_spy trade logs (generate_winner_outputs.py):
    each row spans [entry_date, exit_date) of a constant position;
    returns accrue on dates in (entry_date, exit_date] at that position
    (Vera-validated "convention A", 2026-06-11).
  - indpro_xlp trade log is already a monthly series with columns
    [date, signal_value, position, xlp_return, strategy_return] — direct
    pass-through (covers the OOS window only, 2019-01..2025-12).

Reconciliation metric formulas mirror each pair's tournament code:
  sharpe   = oos_ret.mean()/oos_ret.std() * sqrt(ann)      (ann=252 daily, 12 monthly)
  ann_ret  = oos_ret.mean() * ann                          (arithmetic)
  max_dd   = min drawdown of (1+oos_ret).cumprod() within the OOS window

True OOS windows (verified against pipeline code, 2026-06-11 audit):
  vix_vix3m_spy : 2020-01-01 .. 2025-12-31  (pair_pipeline_vix_vix3m_spy.py:24)
  indpro_spy    : 2018-01-01 .. 2025-12-31  (pair_pipeline_indpro_spy.py:44)
  indpro_xlp    : 2019-01-31 .. 2025-12-31  (formula split, n=336 -> oos_n=84)

Author: Evan (Econometrics Agent) — fix260611_meta_cmp
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/workspaces/aig-rlic-plus")
DATE_TAG = "20260611"

# Tolerances per ECON-SR1
TOL_SHARPE = 0.01
TOL_PP = 0.005  # 0.5 percentage points, on decimal-fraction metrics

PAIRS = {
    "vix_vix3m_spy": {
        "data": "data/vix_vix3m_spy_daily_20260314.parquet",
        "ret_col": "spy_ret",
        "price_col": "spy",
        "ann": 252,
        "oos_start": "2020-01-01",
        "oos_end": "2025-12-31",
        "source": "trade_log_span_replay",
    },
    "indpro_spy": {
        "data": "data/indpro_spy_monthly_19900101_20251231.parquet",
        "ret_col": "spy_ret",
        "price_col": "spy",
        "ann": 12,
        "oos_start": "2018-01-01",
        "oos_end": "2025-12-31",
        "source": "trade_log_span_replay",
    },
    "indpro_xlp": {
        "data": "data/indpro_xlp_monthly_19980101_20251231.parquet",
        "ret_col": "xlp_ret",
        "price_col": "xlp",
        "ann": 12,
        "oos_start": "2019-01-31",
        "oos_end": "2025-12-31",
        # Trade log on disk is a {0,1} long/cash series — it is NOT the
        # tournament winner (S8_accel / T2_roll_p75 / P3_long_short_counter /
        # L3, positions in {-1,+1}). Replay reconciliation FAILED (Sharpe
        # 0.6352 vs 1.1147) -> ECON-SR1 §2 fallback: repaired re-derivation
        # mirroring pair_pipeline_indpro_xlp.py stage_tournament exactly.
        "source": "repaired_signal_rederivation",
    },
}

DIR_WEIGHT = {"Long": 1.0, "Cash": 0.0, "Short": -1.0}


def load_returns(cfg: dict) -> pd.Series:
    df = pd.read_parquet(REPO / cfg["data"])
    if cfg["ret_col"] in df.columns:
        ret = df[cfg["ret_col"]]
    else:
        ret = df[cfg["price_col"]].pct_change()
    return ret.fillna(0.0).astype(float)


def replay_span_log(pair: str, cfg: dict) -> pd.DataFrame:
    """Replay a span-format trade log (entry_date/exit_date/direction rows).

    Position weight applies to returns on dates in (entry_date, exit_date]
    — the producers' position.shift(1) convention."""
    ret = load_returns(cfg)
    tl = pd.read_csv(REPO / "results" / pair / "winner_trade_log.csv",
                     parse_dates=["entry_date", "exit_date"])
    pos = pd.Series(0.0, index=ret.index)
    for _, r in tl.iterrows():
        w = DIR_WEIGHT.get(r.direction)
        if w is None:
            raise ValueError(f"{pair}: unknown direction {r.direction!r}")
        idx = ret.index[(ret.index > r.entry_date) & (ret.index <= r.exit_date)]
        pos.loc[idx] = w
    return pd.DataFrame({
        "position": pos,
        "strategy_return": pos * ret,
        "bh_return": ret,
    })


def passthrough_series_log(pair: str, cfg: dict) -> pd.DataFrame:
    """indpro_xlp: trade log already is the monthly OOS strategy series."""
    tl = pd.read_csv(REPO / "results" / pair / "winner_trade_log.csv",
                     parse_dates=["date"]).set_index("date")
    # Integrity: strategy_return must equal position * target return row-wise
    resid = (tl["strategy_return"] - tl["position"] * tl[f"{cfg['price_col']}_return"]).abs().max()
    if resid > 1e-9:
        raise AssertionError(f"{pair}: trade-log internal inconsistency (max resid {resid:.2e})")
    return pd.DataFrame({
        "position": tl["position"].astype(float),
        "strategy_return": tl["strategy_return"].astype(float),
        "bh_return": tl[f"{cfg['price_col']}_return"].astype(float),
    })


def rederive_indpro_xlp(pair: str, cfg: dict) -> pd.DataFrame:
    """Repaired re-derivation of the indpro_xlp winner
    (S8_accel / T2_roll_p75 / P3_long_short_counter / lead 3), mirroring
    pair_pipeline_indpro_xlp.py::stage_tournament line-for-line:

        signal_lagged = indpro_accel.shift(3)
        thresh        = signal_lagged.rolling(60, min_periods=36).quantile(0.75)
        above         = signal_lagged > thresh
        position(t)   = (~above)*2 - 1            # counter orientation, P3
        strat_ret(t)  = position(t-1) * xlp_ret(t)

    Early-sample masking: where signal_lagged or thresh is NaN at decision
    time, the tournament's `~(NaN > NaN)` evaluates True -> +1 long, a NaN
    artifact, not a signal. The persisted artifact sets those accrual
    weights to 0 (flat). This affects only the pre-2003 in-sample warm-up;
    the OOS window (2019-01..2025-12) is fully defined, so reconciliation
    is unaffected (verified by the reconciliation gate below)."""
    df = pd.read_parquet(REPO / cfg["data"])
    work = df.dropna(subset=["indpro"])
    sig_lagged = work["indpro_accel"].shift(3)
    thresh = sig_lagged.rolling(60, min_periods=36).quantile(0.75)
    above = sig_lagged > thresh
    position_held = (~above).astype(float) * 2.0 - 1.0
    defined = sig_lagged.notna() & thresh.notna()
    position_held = position_held.where(defined, 0.0)
    pos_accrual = position_held.shift(1).fillna(0.0)
    ret = work[cfg["ret_col"]].fillna(0.0).astype(float)
    return pd.DataFrame({
        "position": pos_accrual,
        "strategy_return": pos_accrual * ret,
        "bh_return": ret,
    })


def metrics(sr: pd.Series, ann: int) -> dict:
    sharpe = sr.mean() / sr.std() * np.sqrt(ann) if sr.std() > 0 else 0.0
    eq = (1.0 + sr).cumprod()
    mdd = float(((eq / eq.cummax()) - 1.0).min())
    return {
        "oos_sharpe": float(sharpe),
        "oos_max_drawdown": mdd,
        "oos_ann_return": float(sr.mean() * ann),
        "n_obs": int(len(sr)),
    }


def run(pair: str) -> bool:
    cfg = PAIRS[pair]
    w = json.loads((REPO / "results" / pair / "winner_summary.json").read_text())
    if cfg["source"] == "trade_log_span_replay":
        df = replay_span_log(pair, cfg)
    elif cfg["source"] == "repaired_signal_rederivation":
        df = rederive_indpro_xlp(pair, cfg)
    else:
        df = passthrough_series_log(pair, cfg)

    oos = df.loc[cfg["oos_start"]:cfg["oos_end"], "strategy_return"]
    m = metrics(oos, cfg["ann"])

    rows, ok = [], True
    for key, tol in (("oos_sharpe", TOL_SHARPE),
                     ("oos_max_drawdown", TOL_PP),
                     ("oos_ann_return", TOL_PP)):
        rep, comp = float(w[key]), m[key]
        diff = comp - rep
        passed = abs(diff) <= tol
        ok &= passed
        rows.append((key, comp, rep, diff, tol, "PASS" if passed else "FAIL"))

    print(f"\n=== {pair} — source: {cfg['source']} | "
          f"OOS {cfg['oos_start']}..{cfg['oos_end']} (n={m['n_obs']}, ann={cfg['ann']}) ===")
    print(f"{'metric':22s}{'computed':>12s}{'reported':>12s}{'diff':>10s}{'tol':>8s}  verdict")
    for key, comp, rep, diff, tol, verdict in rows:
        print(f"{key:22s}{comp:12.4f}{rep:12.4f}{diff:+10.4f}{tol:8.3f}  {verdict}")

    if not ok:
        print(f"  ECON-SR1 RECONCILIATION FAILED for {pair} — artifact NOT written (STOP).")
        return False

    out = REPO / "results" / pair / f"strategy_returns_{DATE_TAG}.csv"
    df.index.name = "date"
    df.round(10).to_csv(out)
    meta = {
        "pair_id": pair,
        "artifact": out.name,
        "produced_by": "scripts/econ_sr1_build_strategy_returns.py",
        "rule": "ECON-SR1",
        "source": cfg["source"],
        "source_file": (f"results/{pair}/winner_trade_log.csv"
                         if cfg["source"] != "repaired_signal_rederivation"
                         else "scripts/pair_pipeline_indpro_xlp.py::stage_tournament "
                              "(exact re-derivation; trade log on disk is not the winner combo)"),
        "returns_file": cfg["data"],
        "coverage_start": str(df.index.min().date()),
        "coverage_end": str(df.index.max().date()),
        "frequency": "daily" if cfg["ann"] == 252 else "monthly",
        "oos_start": cfg["oos_start"],
        "oos_end": cfg["oos_end"],
        "position_semantics": ("position on row t is the return-accrual weight "
                                "for period t (execution lag already applied); "
                                "strategy_return = position * bh_return row-wise"),
        "reconciliation": {
            key: {"computed": round(comp, 6), "reported_winner_summary": rep,
                  "diff": round(diff, 6), "tolerance": tol, "verdict": verdict}
            for key, comp, rep, diff, tol, verdict in rows
        },
        "generated_at": "2026-06-11",
        "generated_by": "Econ Evan (fix260611_meta_cmp)",
    }
    (REPO / "results" / pair / f"strategy_returns_{DATE_TAG}_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n")
    print(f"  wrote {out.relative_to(REPO)}  ({len(df)} rows) + _meta.json")
    return True


if __name__ == "__main__":
    pairs = sys.argv[1:] or list(PAIRS)
    results = {p: run(p) for p in pairs}
    print("\nSummary:", {p: ("RECONCILED" if v else "STOP") for p, v in results.items()})
    sys.exit(0 if all(results.values()) else 1)
