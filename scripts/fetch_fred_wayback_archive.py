#!/usr/bin/env python3
"""
Fetch public Wayback snapshots for legacy ICE BofA OAS FRED pages.

The ICE BofA OAS series were truncated on FRED in late 2025/early 2026.
This helper can rebuild a small local archive from public Wayback captures so
future live refreshes can fill legacy history. Review the upstream ICE/FRED
terms before using the output; the script requires an explicit acceptance flag.
"""

from __future__ import annotations

import argparse
import gzip
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "legacy_fred_archive" / "ice_bofa_oas_wayback.csv"

CAPTURES = [
    ("hy_oas", "BAMLH0A0HYM2", "https://web.archive.org/web/20251104204105id_/https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2", "csv"),
    ("ig_oas", "BAMLC0A0CM", "https://web.archive.org/web/20240927002955id_/https://fred.stlouisfed.org/data/BAMLC0A0CM", "html_table"),
    ("bb_hy_oas", "BAMLH0A1HYBB", "https://web.archive.org/web/20241102020850id_/https://fred.stlouisfed.org/data/BAMLH0A1HYBB", "html_table"),
    ("ccc_hy_oas", "BAMLH0A3HYC", "https://web.archive.org/web/20240914183324id_/https://fred.stlouisfed.org/data/BAMLH0A3HYC", "html_table"),
    ("bbb_oas", "BAMLC0A4CBBB", "https://web.archive.org/web/20241027011210id_/https://fred.stlouisfed.org/data/BAMLC0A4CBBB", "html_table"),
]


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "aig-rlic-plus-archive/1.0"})
    with urlopen(req, timeout=60) as resp:
        raw = resp.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def parse_capture(name: str, series_id: str, url: str, kind: str) -> pd.Series:
    text = fetch_text(url)
    if kind == "csv":
        df = pd.read_csv(StringIO(text))
        date_col = df.columns[0]
        value_col = series_id if series_id in df.columns else df.columns[-1]
        s = pd.Series(pd.to_numeric(df[value_col].replace(".", pd.NA), errors="coerce"), index=pd.to_datetime(df[date_col]), name=name)
    else:
        tables = pd.read_html(StringIO(text))
        table = next((t for t in tables if {"DATE", "VALUE"}.issubset(set(map(str, t.columns)))), None)
        if table is None:
            raise RuntimeError(f"No DATE/VALUE table found for {series_id}")
        s = pd.Series(pd.to_numeric(table["VALUE"].replace(".", pd.NA), errors="coerce"), index=pd.to_datetime(table["DATE"]), name=name)
    s = s.dropna().sort_index()
    print(f"  {series_id:12s} -> {name:12s}: {len(s):5d} rows  {s.index.min().date()} to {s.index.max().date()}")
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accept-ice-terms", action="store_true", help="Confirm you have reviewed and accept applicable source data terms.")
    parser.add_argument("--output", type=Path, default=OUT, help="Output CSV path.")
    args = parser.parse_args()

    if not args.accept_ice_terms:
        parser.error("Refusing to fetch archived ICE/FRED data unless --accept-ice-terms is supplied.")

    print("Fetching archived FRED captures from the Internet Archive...")
    cols = [parse_capture(*capture) for capture in CAPTURES]
    out = pd.concat(cols, axis=1).sort_index()
    out.index.name = "date"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output)
    print(f"Wrote {args.output} with shape {out.shape}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
