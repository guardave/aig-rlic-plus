#!/usr/bin/env python3
"""Validate a JSON instance against a JSON Schema (draft 2020-12).

Implements the producer/consumer validation contract mandated by META-CF
(Contract File Standard). See `docs/schemas/README.md` and
`docs/agent-sops/team-coordination.md` META-CF section.

Usage (CLI):
    python3 scripts/validate_schema.py \
        --schema docs/schemas/winner_summary.schema.json \
        --instance results/hy_ig_v2_spy/winner_summary.json

Usage (library):
    from scripts.validate_schema import validate_json
    errors = validate_json(instance_dict, schema_dict)
    if errors:
        raise ValueError("\\n".join(errors))

Exit codes:
    0 - valid
    1 - invalid (errors printed to stderr)
    2 - schema or instance file missing / malformed
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError:  # pragma: no cover
    print("ERROR: jsonschema package not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


def _fmt_path(path) -> str:
    return "/".join(str(p) for p in path) or "<root>"


def validate_json(instance: Any, schema: dict, *, strict: bool = False) -> list[str]:
    """Validate instance against schema. Return list of human-readable error strings (empty = valid).

    strict=True fails on additionalProperties not declared in the schema.
    """
    working = dict(schema)
    if strict and working.get("type") == "object" and "additionalProperties" not in working:
        working = {**working, "additionalProperties": False}
    try:
        validator = Draft202012Validator(working)
    except SchemaError as exc:
        return [f"Schema is not a valid JSON Schema draft 2020-12: {exc.message}"]
    errors = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        errors.append(f"[{_fmt_path(err.absolute_path)}] {err.message}")
    return errors


def _load_json(path: Path, label: str) -> Any:
    if not path.exists():
        print(f"ERROR: {label} file not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: {label} is not valid JSON ({path}): {exc}", file=sys.stderr)
        sys.exit(2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a JSON instance against a JSON Schema.")
    parser.add_argument("--schema", required=True, help="Path to JSON Schema file")
    parser.add_argument("--instance", required=True, help="Path to instance file to validate")
    parser.add_argument("--strict", action="store_true", help="Fail on additional properties not declared in schema")
    args = parser.parse_args(argv)

    schema = _load_json(Path(args.schema), "schema")
    instance = _load_json(Path(args.instance), "instance")

    errors = validate_json(instance, schema, strict=args.strict)
    if errors:
        print(f"INVALID: {args.instance} does not conform to {args.schema}", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: {args.instance} conforms to {args.schema}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
