#!/usr/bin/env python3
"""R7.1 calibrated reference (user decision 2026-10-20, option C; design R71_CALIBRATION_PROPOSAL.md).

Statistic T = mean OOS timing Sharpe of the selected winners over the K null draws of one track (the pair's
CURRENT null file, null v4: every draw scored on the real winner's calendar training window).

Reference: B synthetic target-return paths. Each path is one stationary bootstrap (Politis & Romano 1994) of the
target returns, resampled separately inside the training block [real common IS start, OOS start) and inside the
OOS block (the IS/OOS split is kept); rows before the training block and undefined (NaN) return rows stay in place.
All K draws of a path share that path (the cross-draw dependence is kept), with the same offsets, inputs, selection
rule and v4 window as the real null. T*_b = mean timing Sharpe of the K winners on path b.

Block length, fixed in advance: L = the Politis-White (2004, Patton-Politis-White 2009 correction) automatic
stationary-bootstrap block length of the full-sample SQUARED target returns (arch.bootstrap.optimal_block_length),
floored at 3 periods and capped at a quarter of the OOS length. Sensitivity: a circular moving-block bootstrap with
fixed blocks of 2L (reported, not used for the outcome).

Decision: centre c = median(T*); critical value q = empirical 0.95 quantile of |T* - c|; R7.1 passes iff
|T - c| <= q; p = (1 + #{|T* - c| >= |T - c|}) / (B + 1). Positions are built once per draw and re-scored on every
path (engine.positions_for; exactness test test_r71_speedup.py).

Output: results/<pair>/r71_calibration_<run_tag>.json, one record per track, hash-bound to the null file
(components.provenance.r71_calibration). Usage: r71_calibrate.py <pair> [--track main|comparison] [--B 199]
[--sens-B 199] [--out PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import null as NL  # noqa: E402
from harness import run as R  # noqa: E402
from harness.engine import TrackInputs, positions_for, run_tournament  # noqa: E402

NULL_FILE = {"main": "null_tournament_{tag}.csv", "comparison": "hindsight_null_tournament_{tag}.csv"}
METHOD = ("stationary bootstrap of the target returns (Politis-Romano), resampled within the training and test "
          "blocks separately, shared by all draws of a path; null v4 calendar window")
SENS_METHOD = "circular moving-block bootstrap, fixed blocks of 2L (sensitivity)"


def block_length(ret: np.ndarray, oos_n: int) -> tuple[int, float]:
    """(L used, raw Politis-White estimate) from the squared returns: floor 3, cap a quarter of the OOS length."""
    from arch.bootstrap import optimal_block_length
    x = ret[~np.isnan(ret)]
    raw = float(optimal_block_length(x ** 2)["stationary"].iloc[0])
    cap = max(3, oos_n // 4)
    return int(min(max(3, round(raw)), cap)), raw


def _stationary_idx(n: int, L: float, rng) -> np.ndarray:
    """Indices 0..n-1 of one stationary-bootstrap resample (geometric blocks with mean L, circular wrap)."""
    out = np.empty(n, int)
    i, p = 0, 1.0 / L
    while i < n:
        s = rng.integers(n)
        m = min(rng.geometric(p), n - i)
        out[i:i + m] = (s + np.arange(m)) % n
        i += m
    return out


def _circular_idx(n: int, b: int, rng) -> np.ndarray:
    """Indices of one circular moving-block resample with fixed block length b."""
    out = np.empty(n, int)
    i = 0
    while i < n:
        s = rng.integers(n)
        m = min(b, n - i)
        out[i:i + m] = (s + np.arange(m)) % n
        i += m
    return out


def resample_path(ret: np.ndarray, is_rows: np.ndarray, oos_rows: np.ndarray, L: float, rng,
                  kind: str = "stationary") -> np.ndarray:
    """One synthetic return path: within the training block and within the test block separately, the defined
    (non-NaN) returns are resampled and written back to the defined positions; everything else is unchanged."""
    r = ret.copy()
    for rows in (is_rows, oos_rows):
        pos = np.flatnonzero(rows & ~np.isnan(ret))
        if len(pos) < 2:
            continue
        idx = _stationary_idx(len(pos), L, rng) if kind == "stationary" else _circular_idx(len(pos), int(L), rng)
        r[pos] = ret[pos[idx]]
    return r


def calibrate_track(mod, track: str, B: int, sens_B: int, log=print) -> dict:
    spec = mod.SPEC
    tracks = R.build_tracks(mod)
    ti = tracks[track]
    rdir = R.REPO / "results" / spec.pair_id
    ws = json.loads((rdir / "winner_summary.json").read_text())
    import chart_provenance
    tag = chart_provenance.run_tag_of(ws, rdir)            # the same run tag the page and the gate resolve
    if not tag:
        raise SystemExit(f"{spec.pair_id}: winner_summary names no run tag (rerun the pipeline first)")
    nf = rdir / NULL_FILE[track].format(tag=tag)
    null = pd.read_csv(nf)
    act = run_tournament(spec, ti, full_table=False)
    is_rows, oos_rows = act.is_mask.copy(), act.oos_mask.copy()
    T = float(null["timing_sharpe"].dropna().mean())
    L, L_raw = block_length(ti.ret, int(oos_rows.sum()))
    seed = zlib.crc32(f"{spec.pair_id}|{track}|r71".encode()) & 0x7FFFFFFF
    rng = np.random.default_rng(seed)
    paths = [resample_path(ti.ret, is_rows, oos_rows, L, rng) for _ in range(B)]
    rng2 = np.random.default_rng(seed + 1)
    spaths = [resample_path(ti.ret, is_rows, oos_rows, 2 * L, rng2, "circular") for _ in range(sens_B)]
    make, _n = R.null_maker(mod, track, ti)
    sums, cnts = np.zeros(B), np.zeros(B)
    ssums, scnts = np.zeros(sens_B), np.zeros(sens_B)
    t0 = time.time()
    offsets = [int(k) for k in null["offset"]]
    for d, k in enumerate(offsets):
        x = make(k)
        pos = positions_for(spec, x)
        for group, acc_s, acc_c in ((paths, sums, cnts), (spaths, ssums, scnts)):
            for b, r in enumerate(group):
                res = run_tournament(spec, TrackInputs(x.name, x.index, r, x.lagged, x.meta), full_table=False,
                                     _null_is_start=act.common_is_start, _positions=pos)
                ts = NL.draw_record(res)["timing_sharpe"]
                if ts is not None and not np.isnan(ts):
                    acc_s[b] += ts
                    acc_c[b] += 1
        log(f"  {spec.pair_id} {track} draw {d + 1}/{len(offsets)} ({time.time() - t0:.0f} s)")

    def decide(s, c):
        Ts = s / np.maximum(c, 1)
        centre = float(np.median(Ts))
        dev = np.abs(Ts - centre)
        q = float(np.quantile(dev, 0.95))
        p = float((1 + np.sum(dev >= abs(T - centre))) / (len(Ts) + 1))
        return {"centre": round(centre, 4), "critical_value": round(q, 4), "pass": bool(abs(T - centre) <= q),
                "p_value": round(p, 4), "sd": round(float(np.std(Ts, ddof=1)), 4)}
    main = decide(sums, cnts)
    sens = decide(ssums, scnts) if sens_B else None
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=R.REPO, capture_output=True,
                                text=True).stdout.strip()
    except OSError:
        commit = None
    return {"null_file": nf.name, "null_sha256": hashlib.sha256(nf.read_bytes()).hexdigest(), "T": round(T, 4),
            "K": int(null["timing_sharpe"].notna().sum()), "method": METHOD, "B": B,
            "block_rule": "Politis-White stationary block length of squared target returns, floor 3, cap OOS/4",
            "L": L, "L_raw": round(L_raw, 3), "seed": seed, **main,
            "sensitivity": {"method": SENS_METHOD, "B": sens_B, "block": 2 * L, **sens} if sens else None,
            "screening_flag": bool(abs(T) > 0.10), "harness_commit": commit,
            "seconds": round(time.time() - t0, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pair")
    ap.add_argument("--track", choices=("main", "comparison"))
    ap.add_argument("--B", type=int, default=199)
    ap.add_argument("--sens-B", type=int, default=199)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    mod = R.load_pair(a.pair)
    rdir = R.REPO / "results" / a.pair
    ws = json.loads((rdir / "winner_summary.json").read_text())
    import chart_provenance
    tag = chart_provenance.run_tag_of(ws, rdir)
    out = Path(a.out) if a.out else rdir / f"r71_calibration_{tag}.json"
    doc = json.loads(out.read_text()) if out.exists() else {"pair_id": a.pair, "run_tag": tag, "tracks": {}}
    if doc.get("run_tag") != tag:
        doc = {"pair_id": a.pair, "run_tag": tag, "tracks": {}}
    tracks = [a.track] if a.track else [t for t, rec in (ws.get("tracks") or {}).items()
                                        if (rec or {}).get("null_tournament")]
    for t in tracks:
        doc["tracks"][t] = calibrate_track(mod, t, a.B, a.sens_B)
    doc["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
