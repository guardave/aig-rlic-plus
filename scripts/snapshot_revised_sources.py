#!/usr/bin/env python3
"""Snapshot the current values of the six no-archive (revised-only) sources, with a timestamp (pkg12 Q7).

ISM manufacturing / services PMI, NAHB/Wells Fargo HMI, UMich expected business conditions, USGS Portland cement
shipments and EIA WTTSTUS1 have no ALFRED vintage archive, so the pipelines only ever see their latest revised
values. Running this monthly builds our own vintage archive going forward: each run writes one CSV per source to
data/release_calendar/snapshots/<YYYYMMDDTHHMMSSZ>/<SOURCE>.csv (ref_date, value) with the values exactly as the
pipelines read them from data/Data Master.xlsx (same sheets / columns as the pair loaders), plus manifest.json (UTC
snapshot time, workbook SHA-256, sheet/column/loader, change vs the previous snapshot). How to run: data/release_calendar/snapshots/README.md. No scheduled job is created here.

Usage:  python scripts/snapshot_revised_sources.py [--master PATH] [--out DIR]
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
MASTER = REPO / "data" / "Data Master.xlsx"
OUT = REPO / "data" / "release_calendar" / "snapshots"
# source -> (sheet, value column: header name or 1 = second column), as read by the pair loaders
SOURCES = {
    "ISM_MFG": ("ISM Manufacturing PMI", 1, "scripts/pair_pipeline_ism_mfg_spy.py read_master"),
    "ISM_SERVICES": ("ISM PMI", "CDis, CSta - ISM Services PMI", "scripts/pair_data_ism_services_spy.py read_ism_services"),
    "NAHB_HMI": ("WFHMI", "RE - Wells Fargo H Indx", "scripts/pair_data_wells_fargo_housing_spy.py fetch_master_hmi"),
    "UMICH_EXP_BUS_COND": ("UoM_ExptdChgBinesCyle", 1, "scripts/pair_pipeline_umcsent_spy.py read_master"),
    "USGS_CEMENT": ("Portland Cement", 1, "scripts/pair_pipeline_cement_spy.py read_neworders_master"),
    "EIA_WTTSTUS1": ("WTTSTUS1", "WTTSTUS1", "scripts/pair_data_petrol_inv_spy.py read_data_master_wttstus1"),
}


def read_source(wb, sheet: str, col) -> pd.Series:
    """(date, value) rows of one sheet; col = header name, or 1 = the column after the date (as the loaders read)."""
    rows = wb[sheet].iter_rows(values_only=True)
    header = list(next(rows))
    j = col if isinstance(col, int) else header.index(col)
    out = {pd.Timestamp(r[0]): float(r[j]) for r in rows
           if r and r[0] is not None and hasattr(r[0], "year") and isinstance(r[j], (int, float))}
    return pd.Series(out).sort_index()


def main(argv) -> int:
    master, out = MASTER, OUT
    it = iter(argv)
    for a in it:
        if a == "--master":
            master = Path(next(it))
        elif a == "--out":
            out = Path(next(it))
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    sha = hashlib.sha256(master.read_bytes()).hexdigest()
    import openpyxl
    wb = openpyxl.load_workbook(master, read_only=True, data_only=True)
    run = out / stamp
    run.mkdir(parents=True, exist_ok=False)
    prev_runs = sorted(p for p in out.iterdir() if p.is_dir() and p != run)
    manifest = {"snapshot_utc": now.isoformat(timespec="seconds"),
                "source_file": str(master.relative_to(REPO)) if master.is_relative_to(REPO) else str(master),
                "source_sha256": sha, "sources": {}}
    for name, (sheet, col, loader) in SOURCES.items():
        s = read_source(wb, sheet, col)
        df = pd.DataFrame({"ref_date": s.index.strftime("%Y-%m-%d"), "value": s.values})
        df.to_csv(run / f"{name}.csv", index=False)
        note = ""
        if prev_runs and (prev_runs[-1] / f"{name}.csv").exists():
            p = pd.read_csv(prev_runs[-1] / f"{name}.csv")
            note = "unchanged vs " if p.equals(df) else "CHANGED vs "
            note += prev_runs[-1].name
        manifest["sources"][name] = {"sheet": sheet, "column": str(col), "pair_loader": loader, "n_obs": len(df),
                                     "first": df.ref_date.iloc[0], "last": df.ref_date.iloc[-1], "vs_previous": note}
        print(f"{name:20s} {len(df):4d} obs {df.ref_date.iloc[0]}..{df.ref_date.iloc[-1]} {note}")
    (run / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"-> {run.relative_to(REPO) if run.is_relative_to(REPO) else run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
