"""Shared tournament-winner + benchmark primitives (DUP-11 consolidation).

Several `pair_pipeline_*.py` and `econ_pipeline_*.py` scripts re-implement
the same "pick the best non-benchmark strategy" + "compute buy-and-hold
reference" logic inline. The fix260531 code-review audit (BL-DUP-11)
counted 35+ duplicated sites across 3+ pipelines.

This module is the canonical home for those primitives. New pipelines
should call these functions; old pipelines should migrate when next
touched. The intent is that no pipeline ever silently ships a tournament
CSV without a BENCHMARK row, or a winner_summary without bh_* fields.

The functions are deliberately small and self-contained — they do not
import from the project's other modules. They only depend on numpy and
pandas, so they can be used at any stage of any pipeline without import
cycles.

Public API:
    select_winner(tdf, *, score, exclude_benchmark, valid_only)
    compute_buy_and_hold_stats(target_returns, oos_start, oos_end)
    emit_benchmark_row(target_returns, oos_start, oos_end, *, columns_template)

Conventions:
- "Buy and hold" means: hold the target asset's daily return series for
  the full OOS window, no entry/exit. This is the universal benchmark
  every pair should report against.
- Buy-and-hold stats are returned in canonical units used in
  winner_summary.json: sharpe is unitless, ann_return is a ratio
  (0.0765 for 7.65%), max_drawdown is a ratio (-0.082 for -8.2%).
- The BENCHMARK row in the tournament CSV uses the same column shape
  as strategy rows so consumers can iterate uniformly. Stats are
  scaled to PERCENT form there (oos_ann_return = 7.65 not 0.0765,
  oos_max_drawdown = -8.20 not -0.082) to match the historical
  convention some pipelines were already using.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


# ─── Winner selection ────────────────────────────────────────────────────


def select_winner(
    tdf: pd.DataFrame,
    *,
    score: str = "oos_sharpe",
    exclude_benchmark: bool = True,
    valid_only: bool = True,
) -> pd.Series:
    """Return the single best row from a tournament results DataFrame.

    Tie-break: the FIRST row in argmax order wins. Callers that need a
    deterministic secondary tie-break should sort `tdf` before calling.

    Parameters
    ----------
    tdf : pd.DataFrame
        Tournament results. Must contain at least the ``score`` column.
        If ``exclude_benchmark`` and ``valid_only`` are True (defaults),
        also expects ``signal`` and ``valid`` columns.
    score : str
        Column to maximise. Defaults to ``"oos_sharpe"`` per the project
        convention.
    exclude_benchmark : bool
        If True, skip any row whose ``signal`` is the literal string
        ``"BENCHMARK"``. This is the convention used by the dashboard
        consumer (``pair_registry.py``).
    valid_only : bool
        If True, restrict candidates to rows where ``valid == True``.
        Mirrors the per-pipeline filter most callers were applying
        inline.

    Returns
    -------
    pd.Series
        The winning row. Raises ``ValueError`` if no candidates remain
        after filtering.
    """
    cand = tdf
    if exclude_benchmark and "signal" in cand.columns:
        cand = cand[cand["signal"] != "BENCHMARK"]
    if valid_only and "valid" in cand.columns:
        cand = cand[cand["valid"].astype(bool)]
    if len(cand) == 0:
        raise ValueError(
            "select_winner: no candidate rows remain after filtering "
            f"(exclude_benchmark={exclude_benchmark}, valid_only={valid_only}). "
            f"Source frame had {len(tdf)} rows."
        )
    if score not in cand.columns:
        raise KeyError(
            f"select_winner: score column {score!r} not found in tournament "
            f"frame. Available columns: {list(cand.columns)}"
        )
    return cand.loc[cand[score].idxmax()]


# ─── Buy-and-hold stats ──────────────────────────────────────────────────


def compute_buy_and_hold_stats(
    target_returns: pd.Series,
    oos_start: str,
    oos_end: str,
) -> dict:
    """Compute Sharpe / annualised return / max drawdown for a buy-and-hold
    of ``target_returns`` over the OOS window ``[oos_start, oos_end]``.

    Returns canonical (winner_summary-style) units:
        bh_sharpe       : float (unitless)
        bh_ann_return   : float (ratio, e.g. 0.1451 for 14.51%)
        bh_max_drawdown : float (ratio, e.g. -0.4233 for -42.33%)
        bh_oos_n        : int (number of return observations in window)

    Convention: 252 trading days/year. Daily returns assumed.
    """
    oos_ret = target_returns.loc[oos_start:oos_end].dropna()
    n = len(oos_ret)
    if n == 0:
        return {
            "bh_sharpe": None,
            "bh_ann_return": None,
            "bh_max_drawdown": None,
            "bh_oos_n": 0,
        }

    ann_ret_arith = oos_ret.mean() * 252
    ann_vol = oos_ret.std() * np.sqrt(252)
    sharpe = float(ann_ret_arith / ann_vol) if ann_vol > 0 else None

    # Compound annualised return (matches the strategy-side convention).
    ann_ret = float((1 + oos_ret).prod() ** (252 / n) - 1)

    # Max drawdown
    equity = (1 + oos_ret).cumprod()
    peak = equity.cummax()
    dd_series = (equity - peak) / peak
    max_dd = float(dd_series.min()) if len(dd_series) else None

    return {
        "bh_sharpe": round(sharpe, 4) if sharpe is not None else None,
        "bh_ann_return": round(ann_ret, 4),
        "bh_max_drawdown": round(max_dd, 4) if max_dd is not None else None,
        "bh_oos_n": int(n),
    }


# ─── BENCHMARK row for tournament CSV ────────────────────────────────────


def emit_benchmark_row(
    target_returns: pd.Series,
    oos_start: str,
    oos_end: str,
    *,
    columns_template: Iterable[str] = (),
    stats_in_percent: bool = True,
) -> dict:
    """Build a single dict suitable for appending to a tournament results
    DataFrame as the BENCHMARK reference row.

    The row's ``signal`` is the literal string ``"BENCHMARK"`` — this is
    the marker that ``select_winner`` and ``pair_registry`` look for.
    Strategy/threshold/lead fields are blanked (None or NaN); only the
    OOS stat columns are populated.

    Parameters
    ----------
    target_returns : pd.Series
        Daily target asset returns indexed by date.
    oos_start, oos_end : str
        ISO-format OOS window bounds (inclusive).
    columns_template : iterable of str, optional
        If given, the returned dict will contain exactly these columns
        (with None for any not derivable from the B&H computation).
        Use this to match the existing tournament CSV's column order.
    stats_in_percent : bool
        If True (default), ``oos_ann_return`` and ``oos_max_drawdown``
        are scaled ×100 to match the historical per-pair convention
        most pipelines were already writing. If False, ratio form.

    Returns
    -------
    dict
        Row ready to append to a tournament DataFrame.
    """
    bh = compute_buy_and_hold_stats(target_returns, oos_start, oos_end)
    scale = 100.0 if stats_in_percent else 1.0
    row: dict = {
        "signal": "BENCHMARK",
        "threshold": None,
        "threshold_value": None,
        "strategy": None,
        "lead_days": None,
        "lead_months": None,
        "oos_sharpe": bh["bh_sharpe"],
        "oos_ann_return": (
            round(bh["bh_ann_return"] * scale, 2)
            if bh["bh_ann_return"] is not None else None
        ),
        "oos_max_drawdown": (
            round(bh["bh_max_drawdown"] * scale, 2)
            if bh["bh_max_drawdown"] is not None else None
        ),
        "max_drawdown": (
            round(bh["bh_max_drawdown"] * scale, 2)
            if bh["bh_max_drawdown"] is not None else None
        ),
        "annual_turnover": 0.0,        # B&H has no turnover
        "oos_n": bh["bh_oos_n"],
        "valid": True,
    }
    cols = list(columns_template) if columns_template is not None else []
    if cols:
        # Re-order + drop unknown keys to match the caller's CSV shape.
        row = {c: row.get(c) for c in cols}
    return row


__all__ = (
    "select_winner",
    "compute_buy_and_hold_stats",
    "emit_benchmark_row",
)
