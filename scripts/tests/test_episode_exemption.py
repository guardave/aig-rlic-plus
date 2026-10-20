"""DPS-EP1: an episode is exempt only when the indicator has no data over it (rule-based; QA cement F2)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "scripts"))
from components import episodes  # noqa: E402


def _pair(tmp_path, start, phase_b=True):
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    ws = {"run_tag": "20261020", "tracks": {}} if phase_b else {"winner": {}}
    (d / "winner_summary.json").write_text(json.dumps(ws))
    idx = pd.date_range(start, "2026-09-30", freq="ME")
    pd.DataFrame({"x": np.arange(len(idx), dtype=float)}, index=idx).to_parquet(d / "signals_20261020.parquet")
    return d


def test_only_episodes_before_the_data_are_exempt(tmp_path):
    d = _pair(tmp_path / "a", "2005-11-30")                   # cement: data start 2005-11
    assert episodes.exempt_episodes("toy_spy", d) == ["dotcom"]
    d = _pair(tmp_path / "b", "2010-01-31")
    assert episodes.exempt_episodes("toy_spy", d) == ["dotcom", "gfc"]
    d = _pair(tmp_path / "c", "1993-01-31")
    assert episodes.exempt_episodes("toy_spy", d) == []
    d = _pair(tmp_path / "d", "2005-11-30", phase_b=False)    # legacy pairs are never exempt
    assert episodes.exempt_episodes("toy_spy", d) == []


def test_validator_drops_only_the_exempt_episode(tmp_path, monkeypatch):
    import validate_pair_completeness as V
    _pair(tmp_path, "2005-11-30")
    monkeypatch.setattr(V, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(V, "_CHARTS_DIR", tmp_path / "output" / "charts")
    rep = V._check_episode_zooms("toy_spy", None)
    names = {c.name: c.status for c in rep.checks}
    assert names["history_zoom_dotcom (exempt)"] == "PASS" and "history_zoom_dotcom.json" not in names
    assert names["history_zoom_gfc.json"] == "FAIL"           # a covered episode is still required


def test_a_missing_artifact_fails_with_the_current_run_message(tmp_path):
    # QA cement F6: a config reading data_integrity_<tag>.json at import raised a bare FileNotFoundError
    import pytest
    from components import provenance as P
    d = tmp_path / "results" / "toy_spy"
    d.mkdir(parents=True)
    for load in (P.json_file, P.csv_file):
        with pytest.raises(P.CurrentRunFileError, match=r"Current-run file missing: results/toy_spy/x_20261020\.\w+; "
                                                        r"rebuild with python scripts/pair_pipeline_toy_spy\.py"):
            load(d / f"x_20261020.{'json' if load is P.json_file else 'csv'}")
    with pytest.raises(FileNotFoundError):                    # still a FileNotFoundError for tolerant callers
        P.json_file(d / "absent.json")
