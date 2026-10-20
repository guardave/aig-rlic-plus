"""R7.1 calibrated reference (option C): path generator, block rule, decision and artifact binding."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))
import r71_calibrate as C  # noqa: E402


def test_resample_path_keeps_blocks_nan_rows_and_pre_is_rows():
    rng = np.random.default_rng(1)
    n = 120
    ret = np.arange(n, dtype=float)
    ret[[0, 50, 100]] = np.nan
    is_rows = (np.arange(n) >= 10) & (np.arange(n) < 80)
    oos_rows = np.arange(n) >= 80
    for kind, L in (("stationary", 4), ("circular", 8)):
        r = C.resample_path(ret, is_rows, oos_rows, L, rng, kind)
        assert np.array_equal(np.isnan(r), np.isnan(ret))                     # NaN rows stay in place
        assert np.array_equal(r[:10], ret[:10], equal_nan=True)                            # rows before training unchanged
        assert set(r[is_rows & ~np.isnan(ret)]) <= set(ret[is_rows & ~np.isnan(ret)])   # IS values from IS only
        assert set(r[oos_rows & ~np.isnan(ret)]) <= set(ret[oos_rows & ~np.isnan(ret)])  # OOS from OOS only


def test_stationary_blocks_have_mean_length_L():
    rng = np.random.default_rng(2)
    idx = np.concatenate([C._stationary_idx(400, 6, rng) for _ in range(200)])
    breaks = np.sum(np.diff(idx) != 1) + 200          # block starts (wrap 399->0 counts as a break: rare)
    assert 5.0 < len(idx) / breaks < 7.5


def test_block_length_rule_floor_and_cap():
    rng = np.random.default_rng(3)
    L, raw = C.block_length(rng.standard_normal(400), oos_n=100)
    assert 3 <= L <= 25 and raw > 0
    x = np.cumsum(rng.standard_normal(400))                 # strongly persistent squares -> long raw block
    L2, raw2 = C.block_length(x, oos_n=16)
    assert L2 == max(3, 16 // 4) or L2 <= 4


def test_end_to_end_tiny_run_writes_a_bound_record(tmp_path):
    from components import provenance as P
    from harness import run as R
    mod = R.load_pair("cc_delinquency_spy")
    rec = C.calibrate_track(mod, "main", B=3, sens_B=2, log=lambda *a: None)
    for k in ("T", "centre", "critical_value", "pass", "p_value", "B", "method", "L", "null_sha256", "sensitivity"):
        assert k in rec
    assert rec["B"] == 3 and rec["sensitivity"]["B"] == 2 and rec["screening_flag"] == (abs(rec["T"]) > 0.10)
    nt = json.loads((R.REPO / "results/cc_delinquency_spy/winner_summary.json").read_text())
    assert rec["T"] == pytest.approx(nt["tracks"]["main"]["null_tournament"]["timing_sharpe_mean"], abs=1e-3)
