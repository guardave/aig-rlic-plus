#!/usr/bin/env python3
"""Refresh UMCSENT x XLV winner-specific artifacts from the fixed tournament row."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import pair_pipeline_umcsent_xlv as pipe
from _trade_log_broker import synthesize_from_position_log


REPO_ROOT = Path(__file__).resolve().parents[1]
PAIR_ID = "umcsent_xlv"
DATE_TAG = pipe.DATE_TAG
RESULTS = REPO_ROOT / "results" / PAIR_ID
DATA = REPO_ROOT / "data" / "umcsent_xlv_monthly_19980101_20251231.parquet"
TOURNAMENT = RESULTS / f"tournament_results_{DATE_TAG}.csv"
WINNER_SUMMARY = RESULTS / "winner_summary.json"
INTERPRETATION = RESULTS / "interpretation_metadata.json"
SCHEMA_DIR = REPO_ROOT / "docs" / "schemas"


def _annualized_metrics(returns: pd.Series) -> dict[str, float]:
    returns = returns.dropna()
    cum = (1.0 + returns).cumprod()
    dd = cum / cum.cummax() - 1.0
    downside = returns[returns < 0].std() * np.sqrt(12) if len(returns[returns < 0]) > 1 else np.nan
    return {
        "sharpe": float(returns.mean() / returns.std() * np.sqrt(12)),
        "ann_return": float(returns.mean() * 12),
        "ann_vol": float(returns.std() * np.sqrt(12)),
        "max_drawdown": float(dd.min()),
        "sortino": float((returns.mean() * 12) / downside) if pd.notna(downside) and downside > 0 else 0.0,
        "calmar": float((returns.mean() * 12) / abs(dd.min())) if abs(dd.min()) > 0 else 0.0,
        "win_rate": float((returns > 0).mean()),
        "n": int(len(returns)),
    }


def _split(work: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    n = len(work)
    oos_months = min(max(36, round(n * 0.25)), 120)
    is_months = n - oos_months
    return work.index[is_months - 1], work.index[is_months]


def _schema_validate(name: str, path: Path) -> None:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "validate_schema.py"),
        "--schema",
        str(SCHEMA_DIR / f"{name}.schema.json"),
        "--instance",
        str(path),
    ]
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def main() -> int:
    work = pd.read_parquet(DATA).dropna(subset=["umcsent"]).sort_index()
    pipe.IS_END, pipe.OOS_START = _split(work)

    tournament = pd.read_csv(TOURNAMENT)
    winner = tournament.iloc[777]
    expected = {
        "signal": "S3_mom",
        "threshold": "T3_zscore_1.0",
        "strategy": "P1_long_cash",
        "lead_months": 6,
    }
    for key, value in expected.items():
        if winner[key] != value:
            raise RuntimeError(f"row 777 mismatch for {key}: got {winner[key]!r}, expected {value!r}")

    position, strategy_return, signal_for_rule, threshold, threshold_value, threshold_note = pipe.derive_winner_series(
        work,
        winner,
    )

    oos_mask = work.index >= pipe.OOS_START
    oos_returns = strategy_return[oos_mask].dropna()
    metrics = _annualized_metrics(oos_returns)
    if abs(metrics["sharpe"] - float(winner["oos_sharpe"])) > 0.03:
        print(
            "EVAN BLOCKED: recomputed Sharpe "
            f"{metrics['sharpe']:.4f} differs from row 777 {float(winner['oos_sharpe']):.4f}",
            file=sys.stderr,
        )
        return 2

    bh = tournament[tournament["signal"] == "BENCHMARK"].iloc[0]
    oos_position = position[oos_mask].dropna()
    threshold_path = threshold.reindex(work.index) if isinstance(threshold, pd.Series) else pd.Series(threshold, index=work.index)

    strategy_returns = pd.DataFrame({
        "date": work.index.strftime("%Y-%m-%d"),
        "signal_value": signal_for_rule.reindex(work.index).values,
        "threshold_value": threshold_path.values,
        "position": position.reindex(work.index).fillna(0.0).values,
        "strategy_return": strategy_return.reindex(work.index).fillna(0.0).values,
        "bh_return": work["xlv_ret"].values,
    })
    strategy_returns_path = RESULTS / f"strategy_returns_{DATE_TAG}.csv"
    strategy_returns.to_csv(strategy_returns_path, index=False)

    oos_data = work[oos_mask].copy()
    oos_data["signal_value"] = signal_for_rule[oos_mask]
    oos_data["threshold"] = threshold_path[oos_mask]
    oos_data["position"] = position[oos_mask].fillna(0.0)
    oos_data["strat_ret"] = strategy_return[oos_mask].fillna(0.0)
    oos_data["strategy_return"] = oos_data["strat_ret"]
    oos_data["xlv_return"] = oos_data["xlv_ret"]
    oos_data["cum_return"] = (1 + oos_data["strat_ret"]).cumprod()
    oos_data["cumulative_return"] = oos_data["cum_return"] - 1
    trade_log = oos_data[
        [
            "signal_value",
            "threshold",
            "position",
            "xlv_return",
            "strat_ret",
            "strategy_return",
            "cum_return",
            "cumulative_return",
            "xlv",
        ]
    ].copy()
    trade_log.index.name = "date"
    trade_log_path = RESULTS / "winner_trade_log.csv"
    trade_log.to_csv(trade_log_path)

    threshold_note_contract = f"{threshold_note} - see winner_trade_log.csv for the full threshold path"
    winner_summary = {
        "pair_id": PAIR_ID,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "signal_column": "umcsent_mom",
        "signal_code": "S3_mom",
        "signal_display_name": "UMCSENT 3-month momentum",
        "target_symbol": "XLV",
        "threshold_code": "T3_zscore_1.0",
        "threshold_value": round(float(threshold_value), 6),
        "threshold_rule": "gt",
        "threshold_note": threshold_note_contract,
        "strategy_family": "P1_long_cash",
        "strategy_code": "P1",
        "strategy_display_name": "Long/Cash",
        "strategy_description": "Long XLV when the 6-month-lagged UMCSENT 3-month momentum is above its rolling z-score +1.0 threshold; otherwise cash.",
        "direction": "procyclical",
        "signal": "S3_mom",
        "threshold": "T3_zscore_1.0",
        "strategy": "P1_long_cash",
        "lead_months": 6,
        "lead_value": 6,
        "lead_unit": "months",
        "lead_description": "Signal lead = 6 month(s) before the rule is applied",
        "oos_sharpe": round(float(winner["oos_sharpe"]), 4),
        "oos_ann_return": round(float(winner["oos_ann_return"]), 6),
        "oos_ann_vol": round(float(winner["oos_ann_vol"]), 6),
        "oos_sortino": round(float(winner["oos_sortino"]), 4),
        "oos_calmar": round(float(winner["oos_calmar"]), 4),
        "oos_max_drawdown": round(float(winner["max_drawdown"]), 6),
        "oos_n_trades": int(oos_position.diff().abs().fillna(0).gt(0).sum()),
        "oos_period_start": pipe.OOS_START.strftime("%Y-%m-%d"),
        "oos_period_end": work[oos_mask].index.max().strftime("%Y-%m-%d"),
        "max_drawdown": round(float(winner["max_drawdown"]), 6),
        "win_rate": round(float(winner["win_rate"]), 4),
        "oos_win_rate": round(float(winner["win_rate"]), 4),
        "annual_turnover": round(float(winner["annual_turnover"]), 2),
        "cost_assumption_bps": 5,
        "is_n": int(winner["is_n"]),
        "oos_n": int(winner["oos_n"]),
        "bh_oos_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_sharpe": round(float(bh["oos_sharpe"]), 4),
        "bh_ann_return": round(float(bh["oos_ann_return"]), 6),
        "bh_max_drawdown": round(float(bh["max_drawdown"]), 6),
        "oos_start": pipe.OOS_START.strftime("%Y-%m-%d"),
        "is_end": pipe.IS_END.strftime("%Y-%m-%d"),
        "schema_version": "1.1.0",
        "notes": (
            "Ground truth is tournament row 777. "
            f"Winning threshold uses {threshold_note_contract}. "
            "Signal is lagged by 6 months before the rule is applied."
        ),
    }
    WINNER_SUMMARY.write_text(json.dumps(winner_summary, indent=2) + "\n")

    interp = json.loads(INTERPRETATION.read_text())
    interp["key_finding"] = (
        "UMCSENT 3-month momentum (S3_mom) with a rolling z-score > +1.0 trigger, "
        "6-month lead, and P1 Long/Cash sizing delivers OOS Sharpe 1.16, "
        "7.95% annualized return, and max drawdown -0.70% for XLV."
    )
    interp["last_updated_by"] = "evan"
    interp["last_updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    INTERPRETATION.write_text(json.dumps(interp, indent=2) + "\n")

    synthesize_from_position_log(
        PAIR_ID,
        "position",
        "strat_ret",
        price_col="xlv",
        signal_col="umcsent_mom",
        signal_display="6-month-lagged UMCSENT 3-month momentum",
        commission_bps=5,
    )

    _schema_validate("winner_summary", WINNER_SUMMARY)
    _schema_validate("interpretation_metadata", INTERPRETATION)

    print(f"Recomputed OOS Sharpe: {metrics['sharpe']:.4f}")
    print(f"Strategy returns: {strategy_returns_path.relative_to(REPO_ROOT)}")
    print(f"Winner trade log: {trade_log_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
