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
NUM = ["is_sharpe", "oos_sharpe", "is_exposure", "is_annual_turnover", "is_ann_return", "is_max_drawdown"]


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


def _same(a, b):
    ta, tb = a.table, b.table
    assert list(ta["key"]) == list(tb["key"])
    for c in NUM + ["valid", "is_eligible", "is_n", "oos_n", "is_n_trades"]:
        x, y = ta[c].to_numpy(), tb[c].to_numpy()
        if x.dtype.kind == "f":
            assert np.allclose(x, y, rtol=0, atol=1e-12, equal_nan=True), c
        else:
            assert (x == y).all(), c
    assert (a.selection or {}).get("winner") == (b.selection or {}).get("winner")
    assert abs((a.selection or {}).get("score", 0) - (b.selection or {}).get("score", 0)) <= 1e-12
    assert np.array_equal(a.is_mask, b.is_mask)


@pytest.mark.parametrize("pair,track", [("unrate_spy", "main"), ("unrate_spy", "comparison"),
                                        ("cc_delinquency_spy", "main")])
def test_refactored_tournament_equals_the_reference_and_cached_rescoring_is_exact(tmp_path, pair, track):
    ref = _reference_engine(tmp_path)
    mod = R.load_pair(pair)
    ti = R.build_tracks(mod)[track]
    _same(run_tournament(mod.SPEC, ti), ref.run_tournament(mod.SPEC, ti))            # real tournament
    act = run_tournament(mod.SPEC, ti, full_table=False)
    make, n_span = R.null_maker(mod, track, ti)
    rng = np.random.default_rng(20261020)
    for k in NL.offsets(n_span, mod.SPEC.ppy, 3):
        x = make(int(k))
        pos = positions_for(mod.SPEC, x)
        for _b in range(2):                     # synthetic paths: permuted returns, NaN rows kept in place
            r = x.ret.copy()
            ok = ~np.isnan(r)
            r[ok] = rng.permutation(r[ok])
            xs = TrackInputs(x.name, x.index, r, x.lagged, x.meta)
            fresh = ref.run_tournament(mod.SPEC, xs, full_table=False, _null_is_start=act.common_is_start)
            cached = run_tournament(mod.SPEC, xs, full_table=False, _null_is_start=act.common_is_start,
                                    _positions=pos)
            _same(cached, fresh)
            assert NL.draw_record(cached)["timing_sharpe"] == pytest.approx(NL.draw_record(fresh)["timing_sharpe"],
                                                                            abs=1e-12, nan_ok=True)
