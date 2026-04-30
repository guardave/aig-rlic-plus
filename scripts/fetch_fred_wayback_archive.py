#!/usr/bin/env python3
"""Fetch legacy ICE/BofA OAS observations from public Wayback captures.

The FRED pages for these ICE-owned series now expose only about three years of
observations. This script can reconstruct a local research archive from older
public Wayback captures, but it does not grant redistribution rights. Review the
ICE/FRED terms before using the output beyond personal/internal research.
"""

import argparse
import gzip
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "legacy_fred_archive" / "ice_bofa_oas_wayback.csv"

CAPTURES = {
    "hy_oas": {
        "series_id": "BAMLH0A0HYM2",
        "url": "https://web.archive.org/web/20251104204105id_/https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2",
        "kind": "csv",
    },
    "ig_oas": {
        "series_id": "BAMLC0A0CM",
        "url": "https://web.archive.org/web/20240927002955id_/https://fred.stlouisfed.org/data/BAMLC0A0CM",
        "kind": "html_table",
    },
    "bb_hy_oas": {
        "series_id": "BAMLH0A1HYBB",
        "url": "https://web.archive.org/web/20241102020850id_/https://fred.stlouisfed.org/data/BAMLH0A1HYBB",
        "kind": "html_table",
    },
    "ccc_hy_oas": {
        "series_id": "BAMLH0A3HYC",
        "url": "https://web.archive.org/web/20240914183324id_/https://fred.stlouisfed.org/data/BAMLH0A3HYC",
        "kind": "html_table",
    },
    "bbb_oas": {
        "series_id": "BAMLC0A4CBBB",
        "url": "https://web.archive.org/web/20241027011210id_/https://fred.stlouisfed.org/data/BAMLC0A4CBBB",
        "kind": "html_table",
    },
}


def fetch_text(url: str) -> str:
    raw = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def parse_capture(name: str, spec: dict) -> pd.Series:
    text = fetch_text(spec["url"])
    if spec["kind"] == "csv":
        df = pd.read_csv(StringIO(text))
        date_col = df.columns[0]
        value_col = spec["series_id"]
        if value_col not in df.columns:
            value_col = df.columns[1]
        out = df[[date_col, value_col]].rename(columns={date_col: "date", value_col: name})
    else:
        tables = pd.read_html(StringIO(text))
        table = next((t for t in tables if list(t.columns) == ["DATE", "VALUE"]), None)
        if table is None:
            raise ValueError(f"No DATE/VALUE table found for {name}")
        out = table.rename(columns={"DATE": "date", "VALUE": name})

    out["date"] = pd.to_datetime(out["date"])
    out[name] = pd.to_numeric(out[name].replace(".", pd.NA), errors="coerce")
    s = out.drop_duplicates("date").set_index("date")[name].sort_index()
    print(f"{name:12s} {spec['series_id']:12s} rows={len(s):5d} nonmissing={s.notna().sum():5d} "
          f"range={s.index.min().date()}..{s.index.max().date()}")
    return s


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument(
        "--accept-ice-terms",
        action="store_true",
        help="Acknowledge ICE/FRED terms and create the local research archive.",
    )
    args = parser.parse_args()

    if not args.accept_ice_terms:
        raise SystemExit(
            "Refusing to fetch ICE-owned archived data without --accept-ice-terms. "
            "Review the FRED/ICE notes before using or sharing the output."
        )

    series = [parse_capture(name, spec) for name, spec in CAPTURES.items()]
    df = pd.concat(series, axis=1).sort_index()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index_label="date")
    print(f"Saved {args.output} with shape {df.shape}")


if __name__ == "__main__":
    main()
