"""Build data/prospective_pairs.csv from CSV + indicator_map.yaml.

Idempotent generator. Read sources, dedupe on (indicator_id, target), emit
the prospective-pairs catalog used by the Status tab on the landing page.

Sources:
  docs/Indicator x Target.csv      — raw user-curated matrix; Done-Y cells
                                     mark prospective pairs
  config/indicator_map.yaml        — CSV-ticker → canonical indicator_id map,
                                     plus deprecated_pair_ids overlay

Output:
  data/prospective_pairs.csv       — columns: indicator_id, display_name,
                                     category, target, pair_id, status,
                                     primary_csv_ticker (canonical name for
                                     the indicator: first CSV ticker that
                                     maps to this indicator_id, in CSV
                                     row order),
                                     aliases (other CSV tickers that map
                                     to the same indicator_id; comma-joined,
                                     blank if none — Status tab renders as
                                     "display_name (also: alias1, alias2)"),
                                     contributing_csv_ticker (the specific
                                     CSV ticker whose Done-Y cell produced
                                     THIS row's target),
                                     source_csv_rows (semicolon-joined CSV
                                     line numbers for traceability)

Halts on any CSV ticker missing from indicator_map.yaml.
"""

from __future__ import annotations

import csv
import sys
from collections import OrderedDict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CSV_SRC = ROOT / "docs" / "Indicator x Target.csv"
MAP_SRC = ROOT / "config" / "indicator_map.yaml"
OUT = ROOT / "data" / "prospective_pairs.csv"

DONE_TOKEN = "done - y"
TARGET_COL_PREFIX = "Step B "
TARGET_COL_SUFFIX = " Progress"


def _norm_cell(v: str | None) -> str:
    return (v or "").strip().lower()


def _is_done_y(v: str | None) -> bool:
    return _norm_cell(v) == DONE_TOKEN


def main() -> int:
    if not CSV_SRC.exists():
        print(f"ERROR: missing {CSV_SRC}", file=sys.stderr)
        return 1
    if not MAP_SRC.exists():
        print(f"ERROR: missing {MAP_SRC}", file=sys.stderr)
        return 1

    with MAP_SRC.open() as f:
        ymap = yaml.safe_load(f)
    indicators = ymap.get("indicators", {})
    targets_map = ymap.get("targets", {})
    deprecated = set(ymap.get("deprecated_pair_ids", []))

    with CSV_SRC.open(encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)
    header = rows[0]

    target_cols: list[tuple[int, str, str]] = []
    for i, h in enumerate(header):
        if h.startswith(TARGET_COL_PREFIX) and h.endswith(TARGET_COL_SUFFIX):
            tkr = h[len(TARGET_COL_PREFIX) : -len(TARGET_COL_SUFFIX)]
            if tkr not in targets_map:
                continue
            target_cols.append((i, tkr, targets_map[tkr]))

    if not target_cols:
        print("ERROR: no Step B target columns matched the map's targets:", file=sys.stderr)
        print(f"  header sample: {header[:6]}", file=sys.stderr)
        return 1

    indicator_tickers: dict[str, list[str]] = OrderedDict()
    for csv_line, r in enumerate(rows[1:], start=2):
        if not r or not r[0].strip():
            continue
        ticker = r[0].strip()
        if ticker not in indicators:
            continue
        spec = indicators[ticker]
        iid = spec.get("indicator_id")
        if not iid or iid == "TODO_review":
            continue
        indicator_tickers.setdefault(iid, [])
        if ticker not in indicator_tickers[iid]:
            indicator_tickers[iid].append(ticker)

    accum: dict[tuple[str, str], dict] = OrderedDict()
    missing: list[tuple[int, str]] = []
    todo_review: list[tuple[int, str]] = []

    for csv_line, r in enumerate(rows[1:], start=2):
        if not r or not r[0].strip():
            continue
        ticker = r[0].strip()

        done_targets = [
            (target_tkr, target_lc)
            for (col_idx, target_tkr, target_lc) in target_cols
            if col_idx < len(r) and _is_done_y(r[col_idx])
        ]
        if not done_targets:
            continue

        if ticker not in indicators:
            missing.append((csv_line, ticker))
            continue
        spec = indicators[ticker]
        indicator_id = spec.get("indicator_id")
        if not indicator_id or indicator_id == "TODO_review":
            todo_review.append((csv_line, ticker))
            continue
        display_name = spec.get("display_name", ticker)
        category = spec.get("category", "")

        for target_tkr, target_lc in done_targets:
            key = (indicator_id, target_lc)
            pair_id = f"{indicator_id}_{target_lc}"
            status = "archived_deprecated" if pair_id in deprecated else "not_started"

            if key in accum:
                bucket = accum[key]
                if ticker not in bucket["csv_tickers"]:
                    bucket["csv_tickers"].append(ticker)
                if csv_line not in bucket["source_csv_rows"]:
                    bucket["source_csv_rows"].append(csv_line)
            else:
                accum[key] = {
                    "indicator_id": indicator_id,
                    "display_name": display_name,
                    "category": category,
                    "target": target_tkr,
                    "pair_id": pair_id,
                    "status": status,
                    "csv_tickers": [ticker],
                    "source_csv_rows": [csv_line],
                }

    if missing or todo_review:
        if missing:
            print(
                f"ERROR: {len(missing)} CSV ticker(s) not found in indicator_map.yaml:",
                file=sys.stderr,
            )
            for ln, tkr in missing[:20]:
                print(f"  line {ln}: {tkr!r}", file=sys.stderr)
        if todo_review:
            print(
                f"ERROR: {len(todo_review)} CSV ticker(s) flagged TODO_review in map:",
                file=sys.stderr,
            )
            for ln, tkr in todo_review[:20]:
                print(f"  line {ln}: {tkr!r}", file=sys.stderr)
        print("Resolve in config/indicator_map.yaml, then rerun.", file=sys.stderr)
        return 2

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = [
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
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for bucket in accum.values():
            iid = bucket["indicator_id"]
            all_tickers = indicator_tickers.get(iid, bucket["csv_tickers"])
            primary = all_tickers[0] if all_tickers else ""
            aliases = ",".join(t for t in all_tickers if t != primary)
            contributing = bucket["csv_tickers"][0]
            rows_joined = ";".join(str(n) for n in bucket["source_csv_rows"])
            w.writerow(
                [
                    iid,
                    bucket["display_name"],
                    bucket["category"],
                    bucket["target"],
                    bucket["pair_id"],
                    bucket["status"],
                    primary,
                    aliases,
                    contributing,
                    rows_joined,
                ]
            )

    n_total = len(accum)
    n_dep = sum(1 for b in accum.values() if b["status"] == "archived_deprecated")
    indicators_with_aliases = sum(1 for iid, ts in indicator_tickers.items() if len(ts) > 1)
    print(f"OK: wrote {OUT.relative_to(ROOT)}")
    print(f"  rows: {n_total}")
    print(f"  archived_deprecated: {n_dep}")
    print(f"  indicators with aliases (>=2 CSV tickers ever map here): {indicators_with_aliases}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
