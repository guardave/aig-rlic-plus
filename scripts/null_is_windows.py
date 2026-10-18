#!/usr/bin/env python3
"""Training window (IS start, IS rows) of every draw of a pair's null tournament, and of the actual tournament.

The real-time null shifts reference-period values inside each vintage; at large offsets the early vintages lose
readings and the common IS start moves later, so a draw can train on a much shorter window than the real winner
(QA B1 umcsent_xlv M1). Runs recorded since harness.null.draw_record gained is_start / is_n carry this per draw;
this script back-fills it for existing null CSVs by rebuilding each draw's inputs and re-scoring the window (no
selection is re-run). Output: results/<pair>/null_is_windows_<tag>.csv for the MAIN (headline) track: draw,
offset, is_start, is_n_draw (training rows of each draw), is_n_actual (one row, draw = -1: the actual tournament).
Separate columns keep the draws' min / max and the actual value readable as tagged column statistics
(components.provenance colmin / colmax) by the chance-check panel.

Usage: python scripts/null_is_windows.py <pair> [--tag YYYYMMDD] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import run as R  # noqa: E402
from harness.engine import run_tournament  # noqa: E402

NULL_FILE = {"main": "null_tournament_{tag}.csv", "comparison": "hindsight_null_tournament_{tag}.csv"}


def windows(pair: str, tag: str, roles=("main",), log=print) -> pd.DataFrame:
    mod = R.load_pair(pair)
    tracks = R.build_tracks(mod)
    rows = []
    for role in roles:
        ti = tracks.get(role)
        f = R.REPO / "results" / pair / NULL_FILE[role].format(tag=tag)
        if ti is None or not f.exists():
            continue
        act = run_tournament(mod.SPEC, ti, full_table=False)
        rows.append({"track": role, "draw": -1, "offset": 0, "is_start": str(act.common_is_start.date())
                     if act.common_is_start is not None else None, "is_n": int(np.sum(act.is_mask))})
        null = pd.read_csv(f)
        if {"is_start", "is_n"} <= set(null.columns):       # recorded per draw since draw_record v2: no rebuild
            rows += [{"track": role, "draw": int(d), "offset": int(k), "is_start": s, "is_n": int(n)}
                     for d, k, s, n in zip(null["draw"], null["offset"], null["is_start"], null["is_n"])]
            continue
        make, _n = R.null_maker(mod, role, ti)
        for d, k in zip(null["draw"], null["offset"]):
            res = run_tournament(mod.SPEC, make(int(k)), full_table=False)
            rows.append({"track": role, "draw": int(d), "offset": int(k),
                         "is_start": str(res.common_is_start.date()) if res.common_is_start is not None else None,
                         "is_n": int(np.sum(res.is_mask))})
            log(f"  {pair} {role} draw {d} offset {k}: IS from {rows[-1]['is_start']}, {rows[-1]['is_n']} rows")
    out = pd.DataFrame(rows)
    out["is_n_draw"] = out["is_n"].where(out["draw"] >= 0)
    out["is_n_actual"] = out["is_n"].where(out["draw"] < 0)
    return out.drop(columns=["is_n", "track"])[["draw", "offset", "is_start", "is_n_draw", "is_n_actual"]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pair")
    ap.add_argument("--tag")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    tag = a.tag
    if not tag:
        ws = json.loads((R.REPO / "results" / a.pair / "winner_summary.json").read_text())
        import chart_provenance
        tag = chart_provenance.run_tag_of(ws, R.REPO / "results" / a.pair)
    out = Path(a.out) if a.out else R.REPO / "results" / a.pair / f"null_is_windows_{tag}.csv"
    windows(a.pair, tag).to_csv(out, index=False)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
