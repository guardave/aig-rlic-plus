# Contract File Standard (`docs/schemas/`)

**Governing meta-rule:** `META-CF` — Contract File Standard.
See `docs/agent-sops/team-coordination.md` (META-CF section) and `docs/standards.md`.

## Purpose

This directory is the **single source of truth for cross-agent JSON contracts**.
Every artifact that crosses an agent boundary — and whose shape matters to more
than one agent — is governed here by a versioned JSON Schema. Prose dictionaries
inside SOPs and partial inline schema copies are prohibited; they fork silently
and diverge.

## What lives here

- Schemas for artifact formats that cross agent boundaries
  (e.g. `winner_summary.schema.json`, `chart_type_registry.schema.json`,
  `narrative_frontmatter.schema.json`, `data_subject.schema.json`).
- Schemas for registries and manifests that any agent reads.
- Schemas for metadata sidecars that travel with primary artifacts.
- Companion reference instances under `examples/`.

## What does NOT live here

- Runtime data (CSVs, parquets, cached datasets) — these are instances, not schemas.
- Rendered results output (`results/<pair_id>/…`) — instances.
- Plotly chart JSONs (`output/charts/…`) — instances of an external library's schema.
- Per-pair narrative markdown — authored content, not a contract shape.

## Naming

| Kind | Path |
|------|------|
| Schema | `docs/schemas/{contract_name}.schema.json` |
| Reference instance | `docs/schemas/examples/{contract_name}.example.json` |

`{contract_name}` is snake_case and matches the artifact's canonical filename
stem (e.g. `winner_summary` for `results/<pair_id>/winner_summary.json`).

## How to add a new schema

1. Draft the schema as JSON Schema draft 2020-12.
2. Add the required header fields: `"x-owner"` (single agent id), `"x-version"` (semver).
3. Validate at least one real existing instance of the artifact against it:
   `python3 scripts/validate_schema.py --schema docs/schemas/foo.schema.json --instance results/<pair>/foo.json`.
4. Commit the schema together with its example instance under `examples/`.
5. Register the schema in `docs/standards.md` under the appropriate agent block (or in a new `SCHEMA-*` sub-block).
6. Cross-link from the owner's SOP and from every consumer's SOP
   (no inline schemas allowed in SOPs — link only).

## How to evolve a schema

- Schema changes require a **semver bump** of `x-version`:
  - Patch (1.0.0 → 1.0.1): clarification, no structural change.
  - Minor (1.0.0 → 1.1.0): additive (new optional field).
  - Major (1.0.0 → 2.0.0): breaking change (renamed / removed / newly-required field).
- Every change produces a `regression_note_<date>.md` entry per META-VNC.
- Every change produces a `sop-changelog.md` entry.
- A major bump requires the Lead's explicit approval before merge.

## Validation tool

All schemas are validated by `scripts/validate_schema.py` (producer before
save, consumer before use). See META-CF producer/consumer responsibilities.
