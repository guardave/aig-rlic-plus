"""Component-level functional tests for fix260601_rescue (Track C).

Tests each rescued component standalone without requiring page wiring.
Run from repo root:  python _pws/lead-lesandro/regression_260601/run_component_tests.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "app"))


def _print_result(name: str, ok: bool, detail: str = "") -> bool:
    flag = "✓" if ok else "✗"
    status = "PASS" if ok else "FAIL"
    print(f"  {flag} {status}  {name}" + (f"  — {detail}" if detail else ""))
    return ok


def test_data_quality_load_empty() -> bool:
    """Empty warnings template returns 0 entries (smoke)."""
    from components.data_quality import load_data_quality_warnings
    # Clear streamlit cache so we re-read disk
    load_data_quality_warnings.clear()
    warnings = load_data_quality_warnings()
    return _print_result(
        "data_quality.load_data_quality_warnings (empty)",
        warnings == [],
        f"got {len(warnings)} entries",
    )


def test_data_quality_load_payload(tmp_dir: Path) -> bool:
    """A populated warnings file is parsed correctly."""
    from components.data_quality import load_data_quality_warnings
    test_path = REPO / "data" / "data_quality_warnings_99999999.json"
    payload = {
        "warnings": [
            {"id": "t1", "severity": "warning", "title": "T", "message": "M"},
            {"id": "t2", "severity": "info", "title": "T2", "message": "M2", "action": "go"},
        ]
    }
    test_path.write_text(json.dumps(payload))
    try:
        load_data_quality_warnings.clear()
        warnings = load_data_quality_warnings()
        ok = (
            len(warnings) == 2
            and warnings[0].get("id") == "t1"
            and warnings[1].get("severity") == "info"
        )
        return _print_result(
            "data_quality.load_data_quality_warnings (2-entry payload)",
            ok,
            f"got {len(warnings)} entries (sorted by filename — newest wins)",
        )
    finally:
        test_path.unlink(missing_ok=True)
        load_data_quality_warnings.clear()


def test_evidence_status_keys() -> bool:
    """All 4 status copy entries exist with required fields."""
    from components.evidence_status import _STATUS_COPY
    required_keys = {"label", "short", "plain", "background", "color"}
    required_statuses = {"found_in_search", "needs_final_exam", "passed_final_exam", "failed_final_exam"}
    have_statuses = set(_STATUS_COPY.keys())
    if have_statuses != required_statuses:
        return _print_result("evidence_status._STATUS_COPY (4 statuses)", False,
                             f"have {have_statuses}, want {required_statuses}")
    for status, copy in _STATUS_COPY.items():
        if not required_keys.issubset(copy.keys()):
            return _print_result(f"evidence_status._STATUS_COPY[{status}] fields", False,
                                 f"missing {required_keys - copy.keys()}")
    return _print_result("evidence_status._STATUS_COPY (4 statuses × 5 fields)", True)


def test_glossary_inline_load() -> bool:
    """Glossary loads >= 30 terms (sanity threshold)."""
    from components.glossary_inline import _load_glossary
    _load_glossary.cache_clear()
    g = _load_glossary()
    return _print_result(
        "glossary_inline._load_glossary",
        len(g) >= 30,
        f"loaded {len(g)} terms",
    )


def test_glossary_inline_unknown_term() -> bool:
    """info_icon on unknown term must not raise (silent no-op)."""
    from components.glossary_inline import info_icon
    try:
        # info_icon uses st.popover; in bare mode it returns None silently.
        info_icon("__nonexistent_term_xyz__")
        return _print_result("glossary_inline.info_icon (unknown term)", True, "no exception")
    except Exception as e:
        return _print_result("glossary_inline.info_icon (unknown term)", False, str(e))


def test_evidence_status_schema_roundtrip() -> bool:
    """Both schemas validate against their bundled examples."""
    import jsonschema
    pairs = [
        ("docs/schemas/evidence_status.schema.json",
         "docs/schemas/examples/evidence_status.example.json"),
        ("docs/schemas/final_exam_results.schema.json",
         "docs/schemas/examples/final_exam_results.example.json"),
    ]
    all_ok = True
    for schema_rel, example_rel in pairs:
        schema = json.loads((REPO / schema_rel).read_text())
        example = json.loads((REPO / example_rel).read_text())
        try:
            jsonschema.validate(example, schema)
            all_ok = _print_result(f"schema roundtrip — {schema_rel.split('/')[-1]}", True) and all_ok
        except jsonschema.ValidationError as e:
            all_ok = _print_result(f"schema roundtrip — {schema_rel.split('/')[-1]}", False, e.message) and all_ok
    return all_ok


def test_validator_runs_on_three_pairs() -> bool:
    """validate_pair_completeness runs end-to-end on 3 representative pairs without crashing."""
    import subprocess
    pairs = ["indpro_spy", "hy_ig_v2_spy", "gold_copper_xli"]
    all_ok = True
    for pair in pairs:
        r = subprocess.run(
            ["python3", "scripts/validate_pair_completeness.py", "--pair", pair],
            cwd=REPO, capture_output=True, text=True,
        )
        crashed = r.returncode == 2 or "Traceback" in (r.stdout + r.stderr)
        ran_clean = "Overall:" in r.stdout
        ok = ran_clean and not crashed
        passes_fails = ""
        if "Overall:" in r.stdout:
            line = [l for l in r.stdout.splitlines() if "Overall:" in l][0]
            passes_fails = line.split("Overall:")[1].strip()
        all_ok = _print_result(f"validate_pair_completeness --pair {pair}", ok, passes_fails) and all_ok
    return all_ok


def test_validator_json_mode() -> bool:
    """--json mode produces parseable JSON output."""
    import subprocess
    r = subprocess.run(
        ["python3", "scripts/validate_pair_completeness.py", "--pair", "indpro_spy", "--json"],
        cwd=REPO, capture_output=True, text=True,
    )
    if "Traceback" in (r.stdout + r.stderr):
        return _print_result("validate_pair_completeness --json (parseable)", False, "crashed")
    try:
        parsed = json.loads(r.stdout)
        ok = isinstance(parsed, list) and len(parsed) >= 1
        return _print_result("validate_pair_completeness --json (parseable)", ok,
                             f"emitted JSON with {len(parsed)} report(s)")
    except json.JSONDecodeError as e:
        return _print_result("validate_pair_completeness --json (parseable)", False, str(e))


def test_existing_imports_unchanged() -> bool:
    """Importing the major app modules still works (no regression)."""
    try:
        from components.pair_registry import load_pair_registry
        from components.sidebar import _build_findings
        from components.narrative import render_glossary_sidebar  # noqa: F401
        from components.page_templates import render_story_page  # noqa: F401
        from components.display_names import INDICATOR_NAMES, TARGET_NAMES  # noqa: F401
        pairs = load_pair_registry()
        findings = _build_findings()
        ok = len(pairs) == 11 and len(findings) == 11
        return _print_result("existing-module imports + registry counts",
                             ok, f"pairs={len(pairs)}, findings={len(findings)}")
    except Exception as e:
        return _print_result("existing-module imports", False, str(e))


def main() -> int:
    print("=" * 72)
    print("fix260601_rescue — Track C component-level tests")
    print("=" * 72)

    tmp_dir = REPO / "_pws" / "lead-lesandro" / "regression_260601"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    tests = [
        test_existing_imports_unchanged,
        test_data_quality_load_empty,
        lambda: test_data_quality_load_payload(tmp_dir),
        test_evidence_status_keys,
        test_glossary_inline_load,
        test_glossary_inline_unknown_term,
        test_evidence_status_schema_roundtrip,
        test_validator_runs_on_three_pairs,
        test_validator_json_mode,
    ]

    results = []
    for t in tests:
        try:
            results.append(t())
        except Exception as e:
            results.append(_print_result(t.__name__, False, f"EXC: {e}"))

    print()
    print("=" * 72)
    n_pass = sum(1 for r in results if r)
    n_fail = sum(1 for r in results if not r)
    status = "PASS" if n_fail == 0 else "FAIL"
    print(f"Overall: {status}  ({n_pass} pass, {n_fail} fail of {len(results)})")
    print("=" * 72)
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
