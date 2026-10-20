"""R7.1 calibration speed-up (side branch): positions are built once per null draw and the draw is re-scored on
each synthetic return path. Exactness (Codex / Lead: 1e-12): the refactored run_tournament equals the pre-refactor
implementation, and the cached re-scoring equals a fresh run on the same synthetic path."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from harness import null as NL  # noqa: E402
from harness import run as R  # noqa: E402
from harness.engine import TrackInputs, positions_for, run_tournament  # noqa: E402

REF_COMMIT = "c936621e"
NULL_FILE = {"main": "null_tournament_{tag}.csv", "comparison": "hindsight_null_tournament_{tag}.csv"}


def _reference_engine(tmp_path):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    src = subprocess.run(["git", "show", f"{REF_COMMIT}:scripts/harness/engine.py"], cwd=ROOT, env=env,
                         capture_output=True, text=True, check=True).stdout
    f = tmp_path / "_engine_ref.py"
    f.write_text(src)
    spec = importlib.util.spec_from_file_location("harness._engine_ref", f)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "harness"
    sys.modules["harness._engine_ref"] = mod
    spec.loader.exec_module(mod)
    return mod


def _eq(x, y, what):
    """Exact (1e-12) equality of two results' fields: arrays, frames, dicts, scalars, NaN = NaN."""
    if isinstance(x, pd.DataFrame):
        assert list(x.columns) == list(y.columns) and len(x) == len(y), what
        for c in x.columns:
            _eq(x[c].to_numpy(), y[c].to_numpy(), f"{what}.{c}")
    elif isinstance(x, np.ndarray):
        assert x.shape == y.shape, what
        if x.dtype.kind in "fc":
            assert np.allclose(x, y, rtol=0, atol=1e-12, equal_nan=True), what
        elif x.dtype.kind == "O":
            for i, (u, v) in enumerate(zip(x, y)):
                _eq(u, v, f"{what}[{i}]")
        else:
            assert np.array_equal(x, y), what
    elif isinstance(x, dict):
        assert set(x) == set(y), what
        for k in x:
            _eq(x[k], y[k], f"{what}.{k}")
    elif isinstance(x, (list, tuple)):
        assert len(x) == len(y), what
        for i, (u, v) in enumerate(zip(x, y)):
            _eq(u, v, f"{what}[{i}]")
    elif isinstance(x, (float, np.floating)) and not isinstance(x, bool):
        assert (np.isnan(x) and np.isnan(y)) or abs(x - y) <= 1e-12, what
    else:
        assert x == y or (x is None and y is None), (what, x, y)


FIELDS = ("name", "cands", "positions", "returns", "table", "common_is_start", "is_mask", "oos_mask", "selection",
          "raw_idx", "bh_is", "bh_oos", "n_distinct", "collapse", "meta")


def _same(a, b):
    """The complete scoring / selection output (Codex option-C S3): positions, strategy-return matrix, full table,
    selection (winner, score, plateau_j ...), raw_idx, windows, buy-and-hold and the distinct-series collapse."""
    for f in FIELDS:
        _eq(getattr(a, f), getattr(b, f), f)
    assert NL.draw_record(a).keys() == NL.draw_record(b).keys()
    _eq(dict(NL.draw_record(a)), dict(NL.draw_record(b)), "draw_record")


@pytest.mark.parametrize("pair,track", [("unrate_spy", "main"), ("unrate_spy", "comparison"),
                                        ("cc_delinquency_spy", "main"), ("permit_spy", "main")])
def test_refactored_tournament_equals_the_reference_and_cached_rescoring_is_exact(tmp_path, pair, track):
    """Every offset of the pair's CURRENT null file (all draws, Codex option-C S3; AIG_FULL_TESTS=1, cc always),
    full tables, re-scored on a synthetic path with the positions built once."""
    import json
    import chart_provenance
    ref = _reference_engine(tmp_path)
    mod = R.load_pair(pair)
    ti = R.build_tracks(mod)[track]
    _same(run_tournament(mod.SPEC, ti), ref.run_tournament(mod.SPEC, ti))            # real tournament
    act = run_tournament(mod.SPEC, ti, full_table=False)
    rdir = R.REPO / "results" / pair
    tag = chart_provenance.run_tag_of(json.loads((rdir / "winner_summary.json").read_text()), rdir)
    offsets = [int(k) for k in pd.read_csv(rdir / NULL_FILE[track].format(tag=tag))["offset"]]
    assert len(offsets) >= 20
    if pair != "cc_delinquency_spy" and os.environ.get("AIG_FULL_TESTS") != "1":
        offsets = offsets[::max(1, len(offsets) // 6)]   # routine runs: a spread of offsets (cc: all of them);
        # AIG_FULL_TESTS=1 runs every offset of every case (the acceptance sweep, ~20 min on the shared host)
    make, _n = R.null_maker(mod, track, ti)
    rng = np.random.default_rng(20261020)
    for k in offsets:
        x = make(k)
        pos = positions_for(mod.SPEC, x)
        r = x.ret.copy()                         # a synthetic path: permuted returns, NaN rows kept in place
        ok = ~np.isnan(r)
        r[ok] = rng.permutation(r[ok])
        xs = TrackInputs(x.name, x.index, r, x.lagged, x.meta)
        fresh = ref.run_tournament(mod.SPEC, xs, full_table=True, _null_is_start=act.common_is_start)
        cached = run_tournament(mod.SPEC, xs, full_table=True, _null_is_start=act.common_is_start, _positions=pos)
        _same(cached, fresh)
