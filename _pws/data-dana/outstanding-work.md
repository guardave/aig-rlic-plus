# Data Dana — Outstanding Work

**Last updated:** 2026-04-24 (Wave 10J/10K checkpoint)

---

## P1 — Open Backlog Items

### BL-D12-LINTER: `scripts/lint_column_suffixes.py` — DATA-D12 enforcement script

**Status:** Dead letter. Rule authored Wave 5B-2, retro-applied manually Wave 5C, flagged missing in Wave 10F cross-review. Script does not exist as of today.
**Impact:** DATA-D12 (column-suffix canon) is unenforceable without the script. Manual linting is error-prone and not repeatable.
**Awaiting:** Lead dispatch or explicit de-prioritization.
**Lesson:** Rule authored without script = debt. Write enforcement tool in same commit as rule.

---

### BL-D13-MANIFEST: DATA-D13 manifest stale for legacy pairs

**Status:** `data/manifest.json` has HY-IG v2 entries only. 6 legacy pairs (INDPRO, VIX/VIX3M, PERMIT, SOFR/TED variants) have no manifest entry.
**Impact:** Cross-pair data provenance unverifiable. DATA-D13 is a paper rule for legacy pairs.
**Awaiting:** Lead dispatch.

---

### BL-D-ENUM: `indicator_type: "production"` outside controlled vocabulary

**Status:** `results/indpro_spy/interpretation_metadata.json` has `indicator_type: "production"`. Schema enum is `{macro, credit, volatility, rates, survey, housing}`. Not schema-bump-coordinated with Evan.
**Impact:** Latent correctness risk if Evan's Rule C1 branches on this field. Low urgency — no active failure today.
**Awaiting:** Coordination with Evan; may require schema version bump.

---

### BL-D-LEGACY-V1: HY-IG v1 parquet DATA-D12 rename

**Status:** v1 HY-IG parquet still carries `hy_ig_spread` (not `hy_ig_spread_pct`). Grandfathered per DATA-D12 clause at time of retro-apply.
**Impact:** Inconsistency between v1 and v2 column naming. Low urgency unless v1 is reactivated.
**Resolution:** Next v1 rerun must rename `hy_ig_spread` → `hy_ig_spread_pct`.

---

## Resolved / Closed

- DATA-D5 sidecar for HY-IG v2 — CLOSED Wave 5C
- DATA-D6 `interpretation_metadata.json` migration — CLOSED Wave 4D-1
- DATA-D12 retro-apply (manual) — CLOSED Wave 5C
- DATA-D13 manifest + registry bootstrap for HY-IG v2 — CLOSED Wave 5C
- FRED OAS truncation documented and spliced — CLOSED Wave 10G.4A
- Orphan-artifact hygiene (indpro_xlp / umcsent_xlv) — CLOSED Wave 10H.1
- DATA-D6b plain-English field rewrite for `hy_ig_spy` — CLOSED Wave 10G.5
- META-CPD cross-reference added to SOP — CLOSED Wave 10J (commit `d013b08`)
