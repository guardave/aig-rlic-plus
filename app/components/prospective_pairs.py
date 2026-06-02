"""Prospective-pairs loader + Status-tab pivot.

Reads `data/prospective_pairs.csv` (produced by
`scripts/build_prospective_pairs.py`) and cross-references the live pair
registry to compute per-cell render status:

  - completed             — a results dir exists for this pair_id
  - archived_deprecated   — marked deprecated in indicator_map.yaml
                            (regardless of whether results exist)
  - not_started           — appears in the prospective catalog but has
                            no results dir

The Status tab pivots this into rows × 9 sector ETF columns, with
display_name annotated inline as "Name (also: alias1, alias2)" when an
indicator has aliases in the source CSV matrix.
"""

from __future__ import annotations

import os
from functools import lru_cache

import pandas as pd

_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")
_CSV = os.path.join(_BASE, "data", "prospective_pairs.csv")

TARGET_ORDER = ["SPY", "XLP", "XLE", "XLI", "XLC", "XLY", "XLK", "XLF", "XLV"]

STATUS_BADGES = {
    "completed": "✅",
    "archived_deprecated": "🚫",
    "not_started": "·",
    "not_in_universe": "",
}


@lru_cache(maxsize=1)
def _load_raw() -> pd.DataFrame:
    if not os.path.exists(_CSV):
        return pd.DataFrame(
            columns=[
                "indicator_id",
                "display_name",
                "category",
                "target",
                "pair_id",
                "status",
                "primary_csv_ticker",
                "aliases",
                "contributing_csv_ticker",
                "source_csv_rows",
            ]
        )
    df = pd.read_csv(_CSV, dtype=str).fillna("")
    return df


def load_prospective_pairs(completed_pair_ids: set[str] | None = None) -> pd.DataFrame:
    """Return a copy of the catalog with `status` overlaid by completion state.

    `completed_pair_ids` is an optional set of pair_ids known to be completed
    (i.e. discovered by load_pair_registry()). If a row's pair_id is in this
    set, its status is upgraded to `completed` UNLESS it is already marked
    `archived_deprecated` (deprecation takes precedence — a deprecated pair
    that still has results stays badged as deprecated, not completed).
    """
    df = _load_raw().copy()
    if completed_pair_ids:
        mask = df["pair_id"].isin(completed_pair_ids) & (df["status"] != "archived_deprecated")
        df.loc[mask, "status"] = "completed"
    return df


def n_universe() -> int:
    """Total prospective pairs in the catalog (dynamic denominator)."""
    return len(_load_raw())


def n_completed(completed_pair_ids: set[str]) -> int:
    """Count rows whose pair_id is in the completed set (deprecation excluded)."""
    df = _load_raw()
    return int(
        ((df["pair_id"].isin(completed_pair_ids)) & (df["status"] != "archived_deprecated")).sum()
    )


def build_status_pivot(completed_pair_ids: set[str] | None = None) -> pd.DataFrame:
    """Pivot the catalog: rows = indicator, columns = 9 sector ETFs.

    Each cell shows a status badge. Indicator label is formatted inline as
    "display_name (also: alias1, alias2)" when aliases is non-empty.
    Rows sorted by category then display_name.
    """
    df = load_prospective_pairs(completed_pair_ids)
    if df.empty:
        return pd.DataFrame()

    indicators = (
        df[["indicator_id", "display_name", "category", "primary_csv_ticker", "aliases"]]
        .drop_duplicates(subset=["indicator_id"])
        .copy()
    )

    def _row_label(row):
        name = row["display_name"]
        if row["aliases"]:
            return f"{name} (also: {row['aliases'].replace(',', ', ')})"
        return name

    indicators["row_label"] = indicators.apply(_row_label, axis=1)
    indicators = indicators.sort_values(["category", "display_name"]).reset_index(drop=True)

    status_lookup = {(r["indicator_id"], r["target"]): r["status"] for _, r in df.iterrows()}

    pivot_rows = []
    for _, ind_row in indicators.iterrows():
        iid = ind_row["indicator_id"]
        cells = {"Indicator": ind_row["row_label"], "Category": ind_row["category"]}
        for tgt in TARGET_ORDER:
            status = status_lookup.get((iid, tgt), "not_in_universe")
            cells[tgt] = STATUS_BADGES.get(status, status)
        pivot_rows.append(cells)

    return pd.DataFrame(pivot_rows, columns=["Indicator", "Category"] + TARGET_ORDER)
