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
fixed blocks of 2L (reported, not used for the outcome), B=99 by default with a pre-specified escalation to 199
(ESCALATION_RULE: the primary and the sensitivity disagree, or ||T - c| - q| / q < 0.20 on either).

Decision: centre c = median(T*); critical value q = empirical 0.95 quantile of |T* - c|; R7.1 passes iff
|T - c| <= q; p = (1 + #{|T* - c| >= |T - c|}) / (B + 1). Positions are built once per draw and re-scored on every
path (engine.positions_for; exactness test test_r71_speedup.py). A path on which no draw selects a winner is an
error (ZeroWinnerPathError), never a T* of 0; the per-path selected-draw counts are recorded. The fixed |T| > 0.10
screening flag is recorded separately and never feeds the pass / fail.

Output: results/<pair>/r71_calibration_<run_tag>.json, one record per track, hash-bound to the null file
(components.provenance.r71_calibration). Usage: r71_calibrate.py <pair> [--track main|comparison] [--B 199]
[--sens-B 99]
[--sens-B-max 199] [--harness-commit SHA] [--out PATH]; a completed construction review is recorded with
r71_calibrate.py <pair> --track T --construction-review WHERE (annotation only, no recomputation).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
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
BLOCK_RULE = "Politis-White stationary block length of squared target returns, floor 3, cap OOS/4"
SCREEN = 0.10                 # fixed screening threshold on |T| (option C): diagnostic, never part of the decision
ESCALATE_MARGIN = 0.20
L_FLOOR = 3
ESCALATION_RULE = (f"sensitivity B=99 by default, extended to 199 (the next 100 paths of the same seeded stream) "
                   f"when the primary and the sensitivity disagree or when ||T - c| - q| / q < {ESCALATE_MARGIN} on "
                   f"either; fixed before the fleet run (Lead 2026-10-20, Codex option-C review)")


def block_length(ret: np.ndarray, oos_n: int) -> tuple[int, float]:
    """(L used, raw Politis-White estimate) from the squared returns: floor 3, cap a quarter of the OOS length."""
    from arch.bootstrap import optimal_block_length
    x = ret[~np.isnan(ret)]
    raw = float(optimal_block_length(x ** 2)["stationary"].iloc[0])
    cap = max(L_FLOOR, oos_n // 4)
    return int(min(max(L_FLOOR, round(raw)), cap)), raw


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


class ZeroWinnerPathError(RuntimeError):
    """A synthetic path on which no null draw selected a winner: T* (the mean timing Sharpe of the selected
    winners) is undefined there, and it is never replaced by a number (Codex option-C C4)."""


def decide(T: float, s: np.ndarray, c: np.ndarray) -> dict:
    """Decision on one reference: s / c = per-path sum / count of the selected winners' timing Sharpe. Raises
    ZeroWinnerPathError when any path has no selected winner. centre = median(T*); q = empirical 0.95 quantile of
    |T* - centre|; pass iff |T - centre| <= q; add-one p = (1 + #{|T* - centre| >= |T - centre|}) / (B + 1)."""
    c = np.asarray(c, int)
    if (c == 0).any():
        raise ZeroWinnerPathError(f"{int((c == 0).sum())} of {len(c)} synthetic paths have no selected winner "
                                  f"(paths {np.flatnonzero(c == 0)[:10].tolist()})")
    Ts = np.asarray(s, float) / c
    centre = float(np.median(Ts))
    dev = np.abs(Ts - centre)
    q = float(np.quantile(dev, 0.95))
    d = abs(T - centre)
    vals, freq = np.unique(c, return_counts=True)
    return {"centre": round(centre, 4), "critical_value": round(q, 4), "pass": bool(d <= q),
            "p_value": round(float((1 + np.sum(dev >= d)) / (len(Ts) + 1)), 4), "sd": round(float(np.std(Ts, ddof=1)), 4),
            "p_resolution": round(1.0 / (len(Ts) + 1), 4), "tail_paths": int(np.sum(dev > q)),
            "margin_ratio": round(abs(d - q) / q, 4) if q > 0 else None,
            "selected_draws": {"min": int(c.min()), "max": int(c.max()),
                               "distribution": {str(int(v)): int(f) for v, f in zip(vals, freq)}}}


def needs_escalation(prim: dict, sens: dict) -> tuple[bool, str]:
    """ESCALATION_RULE, fixed before any fleet run: the sensitivity is extended when the primary and the sensitivity
    disagree, or when either margin ||T - c| - q| / q is below ESCALATE_MARGIN."""
    why = []
    if prim["pass"] != sens["pass"]:
        why.append("primary and sensitivity disagree")
    for name, r in (("primary", prim), ("sensitivity", sens)):
        if r["margin_ratio"] is None or r["margin_ratio"] < ESCALATE_MARGIN:
            why.append(f"{name} margin {r['margin_ratio']} < {ESCALATE_MARGIN}")
    return bool(why), "; ".join(why)


def score_paths(spec, make, offsets, groups, is_start, log=print, tag="") -> list[tuple[np.ndarray, np.ndarray]]:
    """Per path group: (sum, count) of the selected winners' timing Sharpe over the null draws. Positions are built
    once per draw (engine.positions_for) and the draw is re-scored on every path of every group, on the real
    winner's calendar training window (null v4 _null_is_start)."""
    acc = [(np.zeros(len(g)), np.zeros(len(g), int)) for g in groups]
    t0 = time.time()
    for d, k in enumerate(offsets):
        x = make(k)
        pos = positions_for(spec, x)
        for g, (acc_s, acc_c) in zip(groups, acc):
            for b, r in enumerate(g):
                res = run_tournament(spec, TrackInputs(x.name, x.index, r, x.lagged, x.meta), full_table=False,
                                     _null_is_start=is_start, _positions=pos)
                ts = NL.draw_record(res)["timing_sharpe"]
                if ts is not None and not np.isnan(ts):
                    acc_s[b] += ts
                    acc_c[b] += 1
        log(f"  {spec.pair_id} {tag} draw {d + 1}/{len(offsets)} ({time.time() - t0:.0f} s)")
    return acc


def harness_commit(explicit: str | None = None) -> str:
    """The harness commit the artifact is computed with: --harness-commit for a controlled overlay, otherwise
    `git rev-parse HEAD` of the repo, which must succeed (Codex option-C C7: never blank provenance)."""
    if explicit:
        return explicit
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=R.REPO, env=env, capture_output=True, text=True,
                         check=True).stdout.strip()
    if not out:
        raise RuntimeError("git rev-parse HEAD returned nothing; pass --harness-commit")
    return out


def calibrate_track(mod, track: str, B: int = 199, sens_B: int = 99, sens_B_max: int = 199, log=print,
                    commit: str | None = None) -> dict:
    spec = mod.SPEC
    commit = harness_commit(commit)
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
    # all sens_B_max sensitivity paths are drawn up front from one stream: the escalated reference is the default
    # one plus the next paths of the same stream (no re-draw after looking at a result)
    rng2 = np.random.default_rng(seed + 1)
    spaths = [resample_path(ti.ret, is_rows, oos_rows, 2 * L, rng2, "circular") for _ in range(max(sens_B, sens_B_max))]
    if sens_B < 2 or B < 2:
        raise ValueError("B and the sensitivity B must each be at least 2")
    make, _n = R.null_maker(mod, track, ti)
    offsets = [int(k) for k in null["offset"]]
    t0 = time.time()
    (ps, pc), (ss, sc) = score_paths(spec, make, offsets, [paths, spaths[:sens_B]], act.common_is_start, log,
                                     f"{track} B={B}+{sens_B}")
    prim = decide(T, ps, pc)
    sens = decide(T, ss, sc)
    esc, why = needs_escalation(prim, sens)
    if esc and sens_B_max > sens_B:
        log(f"  escalating the sensitivity to {sens_B_max} paths: {why}")
        ((xs, xc),) = score_paths(spec, make, offsets, [spaths[sens_B:sens_B_max]], act.common_is_start, log,
                                  f"{track} sensitivity +{sens_B_max - sens_B}")
        ss, sc = np.concatenate([ss, xs]), np.concatenate([sc, xc])
        sens = decide(T, ss, sc)
    sB = len(ss)
    return {"null_file": nf.name, "null_sha256": hashlib.sha256(nf.read_bytes()).hexdigest(), "T": round(T, 4),
            "K": int(null["timing_sharpe"].notna().sum()), "method": METHOD, "B": B,
            "block_rule": BLOCK_RULE, "L": L, "L_raw": round(L_raw, 3), "L_floor": L_FLOOR,
            "L_cap": max(L_FLOOR, int(oos_rows.sum()) // 4), "seed": seed, **prim,
            "sensitivity": {"method": SENS_METHOD, "B": sB, "B_default": sens_B, "block": 2 * L, "seed": seed + 1,
                            "escalation_triggered": esc, "escalated": bool(esc and sens_B_max > sens_B),
                            "escalation_reason": why or None,
                            **sens},
            "escalation_rule": ESCALATION_RULE,
            "screening_threshold": SCREEN, "screening_flag": bool(abs(T) > SCREEN),
            "screening_note": "diagnostic only, never part of the pass / fail; raised -> construction review",
            "harness_commit": commit, "seconds": round(time.time() - t0, 1)}


def annotate_review(doc: dict, out: Path, tag: str, track: str | None, where: str) -> int:
    """Record a completed construction review on the current calibration record of one track (the screen was raised;
    option C). The record must exist for this run; the review never changes the outcome."""
    rec = (doc.get("tracks") or {}).get(track or "")
    if not track or doc.get("run_tag") != tag or not rec:
        raise SystemExit(f"--construction-review needs --track and a current calibration record ({out.name})")
    if not rec.get("screening_flag"):
        raise SystemExit(f"the {track} screening flag is not raised; nothing to review")
    rec["construction_review"] = {"status": "completed", "ref": where,
                                  "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    out.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"annotated {out} ({track})")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pair")
    ap.add_argument("--track", choices=("main", "comparison"))
    ap.add_argument("--B", type=int, default=199)
    ap.add_argument("--sens-B", type=int, default=99)
    ap.add_argument("--sens-B-max", type=int, default=199, help="escalated sensitivity size (ESCALATION_RULE)")
    ap.add_argument("--harness-commit", help="harness commit of a controlled overlay that is not a git checkout")
    ap.add_argument("--construction-review", metavar="WHERE",
                    help="annotate only (no recomputation): the --track record's screening flag has a completed "
                         "construction review, stated on the page as 'see WHERE' (a place on the page, not a file)")
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
    if a.construction_review:
        return annotate_review(doc, out, tag, a.track, a.construction_review)
    tracks = [a.track] if a.track else [t for t, rec in (ws.get("tracks") or {}).items()
                                        if (rec or {}).get("null_tournament")]
    for t in tracks:
        doc["tracks"][t] = calibrate_track(mod, t, a.B, a.sens_B, a.sens_B_max, commit=a.harness_commit)
    doc["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
