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


def test_decide_arithmetic_on_small_arrays():
    # T* = s / c per path; centre = median; q = 0.95 quantile of |T* - centre|; add-one p
    s = np.array([0.0, 0.2, -0.3, 0.4, 0.1])
    c = np.array([2, 2, 3, 4, 1])
    Ts = s / c                                             # 0, 0.1, -0.1, 0.1, 0.1 -> centre 0.1
    rec = C.decide(0.32, s, c)
    dev = np.abs(Ts - 0.1)                                 # 0.1, 0, 0.2, 0, 0
    assert rec["centre"] == pytest.approx(0.1)
    assert rec["critical_value"] == pytest.approx(np.quantile(dev, 0.95))
    assert rec["pass"] is False                            # |0.32 - 0.1| = 0.22 > q = 0.18
    assert rec["p_value"] == round(1 / 6, 4)          # no |T* - c| >= 0.22: (1 + 0) / (5 + 1)
    assert C.decide(0.25, s, c)["p_value"] == round(2 / 6, 4)   # 0.15: one path (0.2) at least as far
    assert C.decide(0.25, s, c)["pass"] is True
    assert rec["p_resolution"] == round(1 / 6, 4)
    assert rec["tail_paths"] == int(np.sum(dev > rec["critical_value"])) == 1
    assert rec["selected_draws"] == {"min": 1, "max": 4, "distribution": {"1": 1, "2": 2, "3": 1, "4": 1}}
    assert rec["margin_ratio"] == pytest.approx(abs(0.22 - rec["critical_value"]) / rec["critical_value"], abs=1e-4)


def test_a_path_without_a_selected_winner_is_an_error_not_zero():
    # Codex option-C C4: s / max(c, 1) silently set T* = 0
    with pytest.raises(C.ZeroWinnerPathError, match="1 of 3"):
        C.decide(0.1, np.array([0.3, 0.0, 0.2]), np.array([3, 0, 2]))


def test_escalation_rule():
    base = {"pass": True, "margin_ratio": 0.5}
    assert C.needs_escalation(base, dict(base)) == (False, "")
    assert C.needs_escalation(base, {"pass": False, "margin_ratio": 0.5})[0]           # disagreement
    assert C.needs_escalation({"pass": True, "margin_ratio": 0.19}, base)[0]           # primary near the boundary
    assert C.needs_escalation(base, {"pass": True, "margin_ratio": 0.1})[0]            # sensitivity near it
    assert not C.needs_escalation(base, {"pass": True, "margin_ratio": 0.2})[0]         # boundary itself: < 0.20 only
    assert "0.2" in C.ESCALATION_RULE and "99" in C.ESCALATION_RULE and "199" in C.ESCALATION_RULE


def test_escalation_uses_the_unrounded_margin():
    # Codex closure E1: 0.19996 was rounded to 0.2000 before the strict < 0.20 test and skipped escalation
    near = {"pass": True, "margin_ratio": round(0.19996, 4), "_margin_ratio": 0.19996}
    assert near["margin_ratio"] == 0.2
    esc, why = C.needs_escalation(near, {"pass": True, "margin_ratio": 0.5, "_margin_ratio": 0.5})
    assert esc and "0.19996" in why
    # decide() carries the unrounded value next to the rounded field
    s, c = np.array([0.0, 0.2, -0.3, 0.4, 0.1]), np.array([2, 2, 3, 4, 1])
    rec = C.decide(0.32, s, c)
    assert rec["_margin_ratio"] == pytest.approx(abs(0.22 - 0.18) / 0.18) and rec["margin_ratio"] == round(
        rec["_margin_ratio"], 4)


def test_harness_commit_is_never_blank(monkeypatch):
    import subprocess
    assert C.harness_commit("abc1234") == "abc1234" and C.harness_commit(" abc1234\n") == "abc1234"
    for blank in ("", "   ", "\n\t"):                                   # Codex closure C7-E
        with pytest.raises(ValueError, match="blank"):
            C.harness_commit(blank)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          env={k: v for k, v in __import__("os").environ.items() if not k.startswith("GIT_")},
                          check=True).stdout.strip()
    assert C.harness_commit() == head and len(head) == 40

    def fail(*a, **k):
        raise subprocess.CalledProcessError(128, a[0])
    monkeypatch.setattr(C.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):                   # not a git checkout: loud, not ""
        C.harness_commit()

    class Empty:
        stdout = "\n"
    monkeypatch.setattr(C.subprocess, "run", lambda *a, **k: Empty())
    with pytest.raises(RuntimeError, match="--harness-commit"):
        C.harness_commit()


PAIR = "cc_delinquency_spy"


def _tiny(**kw):
    from harness import run as R
    return C.calibrate_track(R.load_pair(PAIR), "main", log=lambda *a: None, **kw)


def test_producer_binds_the_current_null_file_shares_paths_and_uses_the_v4_window(monkeypatch):
    import hashlib
    import pandas as pd
    from harness import run as R
    import chart_provenance
    rdir = R.REPO / "results" / PAIR
    ws = json.loads((rdir / "winner_summary.json").read_text())
    nf = rdir / f"null_tournament_{chart_provenance.run_tag_of(ws, rdir)}.csv"
    null = pd.read_csv(nf)
    K = len(null)
    calls, paths = [], []
    real_rt, real_rp = C.run_tournament, C.resample_path

    def spy_rt(spec, ti, *a, **k):
        if k.get("_positions") is not None:
            calls.append((id(ti.ret), k.get("_null_is_start")))
        return real_rt(spec, ti, *a, **k)

    def spy_rp(ret, is_rows, oos_rows, L, rng, kind="stationary"):
        paths.append((L, kind))
        return real_rp(ret, is_rows, oos_rows, L, rng, kind)
    monkeypatch.setattr(C, "run_tournament", spy_rt)
    monkeypatch.setattr(C, "resample_path", spy_rp)
    monkeypatch.setattr(C, "needs_escalation", lambda p, s: (True, "forced in test"))
    rec = _tiny(B=3, sens_B=2, sens_B_max=3)
    # exact hash binding and T from the current null file
    assert rec["null_file"] == nf.name and rec["null_sha256"] == hashlib.sha256(nf.read_bytes()).hexdigest()
    assert rec["T"] == pytest.approx(round(float(null["timing_sharpe"].dropna().mean()), 4), abs=0)
    assert rec["harness_commit"] and len(rec["harness_commit"]) == 40
    assert "_margin_ratio" not in rec and "_margin_ratio" not in rec["sensitivity"]
    # paths: B stationary of mean L, sens_B_max circular of 2L, drawn once up front
    L = rec["L"]
    assert paths == [(L, "stationary")] * 3 + [(2 * L, "circular")] * 3
    assert rec["sensitivity"]["block"] == 2 * L
    # every re-scoring is on the real winner's calendar window (v4) ...
    act = real_rt(R.load_pair(PAIR).SPEC, R.build_tracks(R.load_pair(PAIR))["main"], full_table=False)
    assert {s for _i, s in calls} == {act.common_is_start}
    # ... and each path is ONE array shared by all K draws (cross-draw dependence kept)
    from collections import Counter
    per_path = Counter(i for i, _s in calls)
    assert len(per_path) == 3 + 3 and set(per_path.values()) == {K}
    # escalation: the default 2 sensitivity paths plus the next one of the same stream
    sn = rec["sensitivity"]
    assert sn["B"] == 3 and sn["B_default"] == 2 and sn["escalated"] and sn["escalation_reason"] == "forced in test"
    assert rec["escalation_rule"] == C.ESCALATION_RULE
    assert sum(sn["selected_draws"]["distribution"].values()) == 3
    assert rec["screening_flag"] == (abs(rec["T"]) > 0.10) and rec["screening_threshold"] == 0.10


def test_producer_is_reproducible_from_its_seed():
    a, b = _tiny(B=2, sens_B=2, sens_B_max=2), _tiny(B=2, sens_B=2, sens_B_max=2)
    a.pop("seconds"), b.pop("seconds")
    assert a == b
    nt = json.loads((C.R.REPO / "results" / PAIR / "winner_summary.json").read_text())
    assert a["T"] == pytest.approx(nt["tracks"]["main"]["null_tournament"]["timing_sharpe_mean"], abs=1e-3)
    from gate_consistency import _r71_record_errors
    assert _r71_record_errors(a) == []


def test_construction_review_annotation_needs_a_current_raised_record(tmp_path):
    out = tmp_path / "r71_calibration_20261020.json"
    doc = {"run_tag": "20261020", "tracks": {"main": {"T": -0.196, "pass": False, "screening_flag": True},
                                             "comparison": {"T": 0.02, "pass": True, "screening_flag": False}}}
    assert C.annotate_review(doc, out, "20261020", "main", "the construction-review note in this section") == 0
    rec = json.loads(out.read_text())["tracks"]["main"]
    assert rec["construction_review"]["status"] == "completed" and rec["pass"] is False      # outcome unchanged
    for args in (("20261021", "main"), ("20261020", None), ("20261020", "comparison")):
        with pytest.raises(SystemExit):
            C.annotate_review(doc, out, args[0], args[1], "x")
