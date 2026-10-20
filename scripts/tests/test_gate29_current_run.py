"""GATE-29 on a Phase B pair checks the CURRENT run's signals parquet, not any signals file (QA permit_yoy F5)."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pytest  # noqa: E402

cv = pytest.importorskip("cloud_verify")


def _git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}     # never the hook's index / dir
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)


def _repo(tmp_path, ws, files):
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    (d / "winner_summary.json").write_text(json.dumps(ws))
    for f in files:
        (d / f).write_bytes(b"x")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "t")
    return tmp_path


def test_phase_b_pair_needs_the_current_run_signals_file(tmp_path):
    old = _repo(tmp_path / "a", {"run_tag": "20261020", "tracks": {}}, ["signals_20261017.parquet"])
    f = cv.gate29_parquet_preflight(["toy_spy"], project_root=str(old))
    assert f and "signals_20261020.parquet" in f[0]["finding"]                      # an older run's file: FAIL
    cur = _repo(tmp_path / "b", {"run_tag": "20261020", "tracks": {}},
                ["signals_20261017.parquet", "signals_20261020.parquet"])
    assert cv.gate29_parquet_preflight(["toy_spy"], project_root=str(cur)) == []
    legacy = _repo(tmp_path / "c", {"winner": {}}, ["signals_20260101.parquet"])     # legacy pair: any file
    assert cv.gate29_parquet_preflight(["toy_spy"], project_root=str(legacy)) == []
    notag = _repo(tmp_path / "d", {"tracks": {}}, ["signals_20261017.parquet"])
    assert "signals_missing" in cv.gate29_parquet_preflight(["toy_spy"], project_root=str(notag))[0]["finding"]
