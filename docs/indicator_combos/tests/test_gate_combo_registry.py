"""Mutation tests for gate_combo_registry.py: every mutation raised by QA (QA_VERIFY_2.md) and Codex
(CODEX_REVIEW_2.md) must FAIL the gate with the expected rule, without crashing.

Run from the repo root:  python -m pytest -q docs/indicator_combos/tests
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "docs" / "indicator_combos" / "scripts"))
import gate_combo_registry as g  # noqa: E402

SUB = Path("docs/indicator_combos")


@pytest.fixture(autouse=True)
def isolated_git(monkeypatch):
    """Inside a git hook, git exports GIT_INDEX_FILE / GIT_DIR / GIT_WORK_TREE. Any git call made by a test would
    then act on the REAL repository's index (this happened once: commit fa3528e4, discarded). Strip every GIT_*
    variable so test git calls only ever touch the temporary repository."""
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k, raising=False)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A minimal copy of the repository: the ledger, the bank, the compliance tables, the release calendar, the
    snapshot manifest and empty placeholders named like the ALFRED vintage files."""
    for rel in ["registry/hypotheses.yaml", "registry/families.yaml", "registry/schema.json",
                "registry/compliance.csv", "QUESTION_BANK.md", "COMPLIANCE.md"]:
        (tmp_path / SUB / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / SUB / rel, tmp_path / SUB / rel)
    for rel in ["data/release_calendar/release_calendar.csv",
                "data/release_calendar/snapshots/20261016T232733Z/manifest.json"]:
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / rel, tmp_path / rel)
    vdir = tmp_path / "data/release_calendar/vintages"
    vdir.mkdir(parents=True, exist_ok=True)
    for f in (REPO / "data/release_calendar/vintages").glob("*.csv.gz"):
        (vdir / f.name).write_bytes(b"")
    return tmp_path


def load(repo: Path, name: str) -> dict:
    return yaml.safe_load((repo / SUB / "registry" / f"{name}.yaml").read_text())


def save(repo: Path, name: str, d: dict) -> None:
    (repo / SUB / "registry" / f"{name}.yaml").write_text(yaml.safe_dump(d, sort_keys=False))


def q(d: dict, qid: str) -> dict:
    return next(x for x in d["questions"] if x["id"] == qid)


def h(d: dict, hid: str) -> dict:
    return next(y for x in d["questions"] for y in x["hypotheses"] if y["hid"] == hid)


def rules(repo: Path) -> set[str]:
    return {e.split()[0] for e in g.check(repo)}


def test_baseline_passes(repo):
    assert g.check(repo) == []


def mutate(repo, fn, name="hypotheses"):
    d = load(repo, name)
    fn(d)
    save(repo, name, d)


CASES = {
    # Codex review 2
    "codex_revised_member_on_confirmatory": (lambda d: q(d, "D1-01")["members"]["permit"].update(track="revised"), "R7"),
    "codex_pass_rule_deleted": (lambda d: h(d, "D1-01.H1").pop("pass_rule"), "S0"),
    "codex_sahm_0.40": (lambda d: h(d, "D1-02.H1")["parameters"][2].update(value=0.40), "R12"),
    # QA review 2
    "qa_margin_not_numeric": (lambda d: h(d, "D1-05.H1")["pass_rule"].update(margin="better than B3"), "S0"),
    "qa_test_free_text": (lambda d: h(d, "D1-05.H1")["pass_rule"].update(test="better than B3 in 1 of 1 window"), "S0"),
    "qa_exploratory_to_confirmatory_revised": (lambda d: (h(d, "D1-17.H1").update(status="confirmatory"),
                                                          q(d, "D1-17").update(status="confirmatory")), "R7"),
    "qa_relabel_revised_as_vintage": (lambda d: q(d, "D1-17")["members"]["ism"].update(track="vintage"), "R17"),
    "qa_relabel_revised_as_market": (lambda d: q(d, "D1-17")["members"]["ism"].update(track="market"), "R17"),
    "qa_sahm_050_removed": (lambda d: h(d, "D1-13.H1")["endpoint"]["params"].pop("comparator_sahm_threshold_pp"), "R12"),
    "qa_sahm_text_not_number": (lambda d: h(d, "D1-02.H1")["parameters"][2].update(value="0.50x"), "R12"),
    "qa_question_family_missing": (lambda d: q(d, "D1-05").update(family="F-NONEXISTENT"), "R2"),
    "qa_purge_ne_horizon": (lambda d: h(d, "D1-27.H1").update(purge_months=1), "R5"),
    "qa_purge_and_horizon_both_changed": (lambda d: h(d, "D1-27.H1").update(purge_months=1, label_horizon_months=1), "R5"),
    "qa_purge_and_horizon_both_zero_lexicographic": (lambda d: h(d, "D1-02.H1").update(purge_months=0, label_horizon_months=0), "R5"),
    "qa_primary_validation_vd": (lambda d: q(d, "D1-08")["validation"].update(primary="V-D"), "R8"),
    "qa_baseline_maybe": (lambda d: q(d, "D1-08")["baselines"].update(B3="maybe"), "S0"),
    "qa_interaction_renamed": (lambda d: h(d, "D1-05.H1")["endpoint"].update(type="information_ratio"), "R11"),
    # Lead revision-3 rules
    "convention_parameter_on_confirmatory": (lambda d: h(d, "D1-01.H1")["parameters"][0].update(source_type="convention"), "R7"),
    "influenced_confirmatory": (lambda d: q(d, "D1-28").update(influenced_by=["viewed_oos"]), "R9"),
    "eleven_ranks": (lambda d: q(d, "D1-13").update(rank=10), "R14"),
    "question_field_deleted": (lambda d: q(d, "D1-14").pop("null_design"), "S0"),
    "status_inconsistent": (lambda d: q(d, "D1-14").update(status="confirmatory"), "R6"),
    "u3_uses_vb": (lambda d: q(d, "D1-16")["validation"].update(supporting="V-B"), "R13"),
}

FAMILY_CASES = {
    "qa_family_correction_none": (lambda d: d["families"]["F-REC"]["correction_confirmatory"].update(method="none"), "R15"),
    "qa_family_correction_empty": (lambda d: d["families"]["F-TC"]["correction_confirmatory"].update(method=""), "S0"),
    "qa_family_correction_deleted": (lambda d: d["families"]["F-FCI"].pop("correction_confirmatory"), "S0"),
    "family_count_wrong": (lambda d: d["families"]["F-COMP"].update(n_total=19), "R15"),
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_hypothesis_mutation_fails(repo, case):
    fn, rule = CASES[case]
    mutate(repo, fn)
    got = rules(repo)
    assert rule in got, f"{case}: expected {rule}, got {sorted(got)}"


@pytest.mark.parametrize("case", sorted(FAMILY_CASES))
def test_family_mutation_fails(repo, case):
    fn, rule = FAMILY_CASES[case]
    mutate(repo, fn, "families")
    got = rules(repo)
    assert rule in got, f"{case}: expected {rule}, got {sorted(got)}"


def test_reads_staged_blob_not_worktree(repo):
    assert not any(k.startswith("GIT_") for k in os.environ)
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
    run("init", "-q")
    assert (repo / ".git").is_dir()
    run("add", "-A")
    # good index, bad working tree -> --staged passes, worktree mode fails
    mutate(repo, lambda d: q(d, "D1-08")["validation"].update(primary="V-D"))
    assert g.check(repo, staged=True) == []
    assert "R8" in rules(repo)
    # bad index, good working tree -> --staged fails
    run("add", "-A")
    shutil.copy(REPO / SUB / "registry/hypotheses.yaml", repo / SUB / "registry/hypotheses.yaml")
    assert "R8" in {e.split()[0] for e in g.check(repo, staged=True)}
    assert g.check(repo) == []
