"""evidence_status.json is covered by the T1.1 schema gate (scripts/validate_all_schemas.py).

Regression for the gap that let four pairs ship a schema-invalid evidence_status.json: every gate
was green while the app's validate_or_die rejected the file and showed a yellow banner.

Run:  python -m pytest tests/test_evidence_status_gate.py
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vas = _load("validate_all_schemas")
esu = _load("evidence_status_util")

LEGACY_BLOCKS = {"pair_id": "fx_spy", "generated_at": "2026-10-08T23:44:26Z", "generated_by": "evan",
                 "blocks": {"tournament": "ready", "hmm_states": "skipped_short_sample"},
                 "caveats": ["OOS <5yr -> winner is a found-in-search CANDIDATE"]}
LEGACY_V100 = {"schema_version": "1.0.0", "pair_id": "fx_spy", "status": "found_in_search",
               "confidence": "medium", "generated_at": "2026-06-19T14:53:21Z",
               "updated_at": "2026-06-19T14:53:21Z", "notes": "no untouched final exam yet."}


def _run_gate(monkeypatch, tmp_path, instance, capsys):
    (tmp_path / "fx_spy").mkdir()
    (tmp_path / "fx_spy" / "evidence_status.json").write_text(json.dumps(instance))
    monkeypatch.setattr(vas, "_RESULTS_DIR", str(tmp_path))
    monkeypatch.setattr(vas, "registered_pair_ids", lambda: ["fx_spy"])
    monkeypatch.setattr(vas, "CANONICAL_ARTIFACTS", ["evidence_status"])
    rc = vas.main()
    return rc, capsys.readouterr().out


def test_gate_lists_evidence_status():
    assert "evidence_status" in vas.CANONICAL_ARTIFACTS


def test_gate_fails_legacy_shapes(monkeypatch, tmp_path, capsys):
    for legacy in (LEGACY_BLOCKS, LEGACY_V100):
        sub = tmp_path / legacy["schema_version"] if "schema_version" in legacy else tmp_path / "blocks"
        sub.mkdir()
        rc, out = _run_gate(monkeypatch, sub, legacy, capsys)
        assert rc == 1, out
        assert "evidence_status.json" in out and "FAIL" in out


def test_converted_legacy_passes_gate_and_keeps_facts(monkeypatch, tmp_path, capsys):
    for i, legacy in enumerate((LEGACY_BLOCKS, LEGACY_V100)):
        sub = tmp_path / str(i)
        sub.mkdir()
        fixed = esu.to_v12(legacy)
        assert fixed["status"] == "found_in_search" and fixed["schema_version"] == "1.2.0"
        rc, out = _run_gate(monkeypatch, sub, fixed, capsys)
        assert rc == 0, out
    assert "found-in-search CANDIDATE" in esu.to_v12(LEGACY_BLOCKS)["technical_note"]
    assert "no untouched final exam yet" in esu.to_v12(LEGACY_V100)["technical_note"]


def test_to_v12_is_idempotent_on_valid_input():
    valid = {"pair_id": "fx_spy", "schema_version": "1.2.0", "status": "found_in_search",
             "updated_at": "2026-06-12T08:58:44Z", "owner": "evan"}
    assert esu.to_v12(valid) == valid


def test_committed_evidence_status_files_conform(capsys):
    assert vas.main() == 0, capsys.readouterr().out
