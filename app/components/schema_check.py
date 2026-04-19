"""Schema-validated JSON loader (APP-WS1 / APP-SEV1 / META-CF).

This module is Ace's consumer-side boundary against producer artifacts that
are governed by JSON Schemas under `docs/schemas/`. It exists to enforce the
rule "validate before use" mandated by META-CF (Contract File Standard) and
to implement the severity policy of APP-SEV1 (no silent fallbacks — every
failure is either a loud error or a loud warning, never a quiet skip).

Rules cited:

- **META-CF** (`docs/agent-sops/team-coordination.md` META-CF section) —
  schemas live at `docs/schemas/{contract_name}.schema.json`; consumers
  validate before use via `scripts.validate_schema.validate_json`.
- **APP-WS1** (`docs/agent-sops/appdev-agent-sop.md`) — `winner_summary.json`
  required-field contract: Ace does NOT render from the winner artifact
  without first validating it against `docs/schemas/winner_summary.schema.json`.
  Replaces the Wave-1.5 `_SIGNAL_CODE_TO_COLUMN` literal-name fallback map.
- **APP-SEV1** (`docs/agent-sops/appdev-agent-sop.md`) — validation severity
  policy: L1 = `st.error` (primary purpose cannot be served), L2 = `st.warning`
  (degraded but recoverable), L3 = `st.caption` (minor gap). Silent skip is
  prohibited — `validate_or_die` implements L1, `validate_soft` implements L2.

Contract:

- `validate_or_die(instance_path, schema_name) -> dict`
  Loads the schema from `docs/schemas/{schema_name}.schema.json`, loads the
  instance JSON, validates, and either returns the instance dict (valid) or
  raises `SchemaValidationError` (invalid) AFTER surfacing the error list via
  `st.error(...)` so the portal user sees the specific schema errors.

- `validate_soft(instance_path, schema_name) -> tuple[dict | None, list[str]]`
  Non-blocking variant. On valid: returns `(data, [])`. On invalid or
  missing instance: returns `(None, errors)`; the caller decides whether to
  raise, warn, or continue with a partial render.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st


_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMAS_DIR = _REPO_ROOT / "docs" / "schemas"


# Make `scripts.validate_schema` importable when the app is run from any cwd.
# The repo layout has `scripts/` as a sibling of `app/`; we add the repo root
# to sys.path once at import time.
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.validate_schema import validate_json  # noqa: E402


class SchemaValidationError(RuntimeError):
    """Raised when an instance fails validation against its declared schema.

    Carries the schema name, instance path, and the list of validator errors
    for upstream diagnostic rendering. Used by `validate_or_die` as the L1
    blocker per APP-SEV1.
    """

    def __init__(self, schema_name: str, instance_path: Path, errors: list[str]):
        self.schema_name = schema_name
        self.instance_path = instance_path
        self.errors = errors
        msg = (
            f"{instance_path} failed schema validation against "
            f"{schema_name}.schema.json: {len(errors)} error(s)"
        )
        super().__init__(msg)


def _schema_path(schema_name: str) -> Path:
    """Resolve the canonical schema path from a contract name."""
    return _SCHEMAS_DIR / f"{schema_name}.schema.json"


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_or_die(instance_path: Path, schema_name: str) -> dict:
    """Load `instance_path`, validate against `docs/schemas/{schema_name}`, return dict.

    On any failure (missing schema, missing instance, malformed JSON, schema
    violation) this function (APP-SEV1 L1 — **loud-error**):

    1. Renders a verbose `st.error(...)` block listing each schema error so
       the stakeholder sees the exact contract gap.
    2. Raises `SchemaValidationError` so the calling component short-circuits
       and does NOT attempt to render from invalid data.

    Callers should let the exception propagate; per APP-SEV1, a silent
    fallback (e.g. `try: validate_or_die(...) except: render_placeholder()`)
    is prohibited.

    Args:
        instance_path: Path to the JSON instance to validate.
        schema_name: Schema basename (e.g. `winner_summary` → resolves to
            `docs/schemas/winner_summary.schema.json`).

    Returns:
        The loaded-and-validated instance as a `dict`.

    Raises:
        SchemaValidationError: instance failed validation or was unloadable.
    """
    schema_path = _schema_path(schema_name)

    # ---- Pre-flight: schema must exist (producer-side META-CF obligation) ----
    if not schema_path.exists():
        errors = [
            f"Schema file missing at {schema_path}. "
            f"META-CF requires every cross-agent JSON contract to have a schema at "
            f"`docs/schemas/{{contract_name}}.schema.json`."
        ]
        st.error(
            f"**Schema `{schema_name}` not found.** Cannot validate "
            f"`{instance_path.name}` — aborting render per APP-SEV1 L1.\n\n"
            + "\n".join(f"- {e}" for e in errors)
        )
        raise SchemaValidationError(schema_name, instance_path, errors)

    # ---- Pre-flight: instance must exist ----
    if not instance_path.exists():
        errors = [f"Instance file missing at {instance_path}."]
        st.error(
            f"**Required artifact missing.** `{instance_path.name}` is required for "
            f"this page but was not found. APP-SEV1 L1 blocks render.\n\n"
            + "\n".join(f"- {e}" for e in errors)
        )
        raise SchemaValidationError(schema_name, instance_path, errors)

    # ---- Load schema + instance ----
    try:
        schema = _load_json(schema_path)
    except json.JSONDecodeError as exc:
        errors = [f"Schema file malformed JSON: {exc}"]
        st.error(
            f"**Schema `{schema_name}` is not valid JSON.** Cannot validate "
            f"`{instance_path.name}`.\n\n"
            + "\n".join(f"- {e}" for e in errors)
        )
        raise SchemaValidationError(schema_name, instance_path, errors) from exc

    try:
        instance = _load_json(instance_path)
    except json.JSONDecodeError as exc:
        errors = [f"Instance file malformed JSON: {exc}"]
        st.error(
            f"**`{instance_path.name}` is not valid JSON.** "
            f"APP-SEV1 L1 blocks render.\n\n"
            + "\n".join(f"- {e}" for e in errors)
        )
        raise SchemaValidationError(schema_name, instance_path, errors) from exc

    # ---- Validate ----
    errors = validate_json(instance, schema)
    if errors:
        # APP-SEV1 L1: render the full error list — no silent fallback.
        bullet_list = "\n".join(f"- `{e}`" for e in errors)
        st.error(
            f"**`{instance_path.name}` does not conform to "
            f"`{schema_name}.schema.json`.** APP-SEV1 L1 blocks render. "
            f"Fix the producer artifact or bump the schema.\n\n"
            f"**Schema errors ({len(errors)}):**\n{bullet_list}"
        )
        raise SchemaValidationError(schema_name, instance_path, errors)

    return instance


def validate_soft(
    instance_path: Path, schema_name: str
) -> tuple[dict | None, list[str]]:
    """Non-blocking schema validation — APP-SEV1 L2 **loud-warning** variant.

    Use for artifacts whose absence or invalidity degrades the page but does
    not prevent the page's primary purpose. The caller decides whether to
    render `st.warning(...)`, fall through to a partial render, or short-circuit.

    Args:
        instance_path: Path to the JSON instance to validate.
        schema_name: Schema basename.

    Returns:
        `(data, [])` on valid; `(None, errors)` on any failure (missing
        schema, missing instance, malformed JSON, schema violation).

    Note:
        This function does NOT render `st.error` / `st.warning` on its own —
        the caller owns the severity rendering. This keeps the helper
        composable for components that want to branch on the error list.
    """
    schema_path = _schema_path(schema_name)

    if not schema_path.exists():
        return None, [f"Schema file missing at {schema_path}"]

    if not instance_path.exists():
        return None, [f"Instance file missing at {instance_path}"]

    try:
        schema = _load_json(schema_path)
    except json.JSONDecodeError as exc:
        return None, [f"Schema file malformed JSON: {exc}"]

    try:
        instance = _load_json(instance_path)
    except json.JSONDecodeError as exc:
        return None, [f"Instance file malformed JSON: {exc}"]

    errors = validate_json(instance, schema)
    if errors:
        return None, errors

    return instance, []
