#!/usr/bin/env python3
"""Reproducibility check of the pinned legacy panel (QA_VERIFY_B1 L2).

Runs the VERBATIM published tournament code (scripts/pair_pipeline_umcsent_xlv.py at c64a609a, the commit that
produced tournament_results_20261008.csv) on data/phaseB_inputs/umcsent_xlv_monthly_legacy_20261008.csv, with
the derived signals computed by that code's own stage-2 formulas on the pinned UMCSENT column, and compares every
row with the published table. Writes results/umcsent_xlv/legacy_pin_check_20261008.json.

The pinned panel is the published run's own monthly panel (rows from 1998-12, after its XLV-start trim). Feeding
the legacy stage-2 alignment with raw series instead (e.g. UMCSENT from before 1998-12) changes the first rows of
the rolling transforms and hence some in-sample columns; that is a different input, not the published one.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LEGACY_COMMIT = "c64a609a"
PIN = REPO / "data" / "phaseB_inputs" / "umcsent_xlv_monthly_legacy_20261008.csv"
PUB = REPO / "results" / "umcsent_xlv" / "tournament_results_20261008.csv"
OUT = REPO / "results" / "umcsent_xlv" / "legacy_pin_check_20261008.json"


def main() -> int:
    src = subprocess.run(["git", "-C", str(REPO), "show", f"{LEGACY_COMMIT}:scripts/pair_pipeline_umcsent_xlv.py"],
                         check=True, capture_output=True, text=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "legacy_umcsent_xlv.py"
        f.write_text(src)
        spec = importlib.util.spec_from_file_location("legacy_umcsent_xlv", f)
        L = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(L)
        L.RESULTS_DIR, L.DATE_TAG = tmp, "pin_check"
        d = pd.read_csv(PIN, index_col=0, parse_dates=True, float_precision="round_trip")
        u = d["umcsent"]                                   # legacy stage-2 formulas, verbatim
        d["umcsent_yoy"] = (u / u.shift(12) - 1) * 100
        d["umcsent_mom"] = (u / u.shift(1) - 1) * 100
        rm36 = u.rolling(36, min_periods=24)
        d["umcsent_zscore"] = (u - rm36.mean()) / rm36.std()
        d["umcsent_3m_ma"] = u.rolling(3, min_periods=2).mean()
        d["umcsent_direction"] = np.sign(d["umcsent_mom"])
        d["umcsent_dev_ma"] = u - d["umcsent_3m_ma"]
        n = len(d.dropna(subset=["umcsent"]))             # legacy ECON-OOS2 split
        oos = min(max(36, round(n * 0.25)), 120)
        dates = d.dropna(subset=["umcsent"]).index
        L.IS_END, L.OOS_START = dates[n - oos - 1], dates[n - oos]
        t = L.stage_tournament(d, None)
    p = pd.read_csv(PUB)
    same = len(t) == len(p) and all((t[c].values == p[c].values).all()
                                    for c in ("signal", "threshold", "strategy", "lead_months"))
    cols = {}
    for c in ("is_sharpe", "oos_sharpe", "is_n", "oos_n", "annual_turnover", "max_drawdown", "valid"):
        dd = np.abs(t[c].astype(float).to_numpy() - p[c].astype(float).to_numpy())
        cols[c] = {"max_abs_diff": float(np.nanmax(dd)), "rows_differing": int((dd > 1e-9).sum())}
    out = {"pair_id": "umcsent_xlv", "legacy_commit": LEGACY_COMMIT, "pinned_panel": str(PIN.relative_to(REPO)),
           "published_table": str(PUB.relative_to(REPO)), "rows": int(len(t)), "same_rows_in_order": bool(same),
           "is_end": str(L.IS_END.date()), "oos_start": str(L.OOS_START.date()), "columns": cols,
           "pass": bool(same and all(v["rows_differing"] == 0 for v in cols.values()))}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
