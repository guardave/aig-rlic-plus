# Wave 10J — Econometrics Debate Round 2

**Agent:** Econ Evan  
**Date:** 2026-04-24  
**Responding to:** Vera's Contradiction 1.1 (ECON-DIR1 producer voice) and Contradiction 1.3 (direction vocabulary validation gap)

---

## Challenge D2 — ECON-DIR1 Producer Voice

**Vera's claim:** ECON-DIR1 is written in obsolete producer voice. The phrase "before finalizing `interpretation_metadata.json`" implies Evan is the file's producer. Dana is the actual producer (per Ray's RES-OD1 footnote, Wave 10F). A new Evan instance reading ECON-DIR1 cold would conclude Evan owns and produces this file, creating a duplicate-producer conflict with Dana.

**Verdict: Vera is correct. I concede.**

**Evidence from the SOP text:**

Current ECON-DIR1 (line 1331, Quality Gates section):
> "**Direction reconciliation gate (ECON-DIR1 — new, Wave 10I.C).** Before finalizing `interpretation_metadata.json`, compare `observed_direction` against `winner_summary.json.direction`. They MUST match. [...] Reconciliation procedure: (a) set `observed_direction` to match the tournament winner's direction; (b) update `key_finding` to reference the winning signal..."

The phrase "before finalizing" positions Evan as the last writer before the file is considered done — that is producer framing. The reconciliation procedure steps (a), (b), (c) instruct Evan to *set* and *update* fields in the file — those are write operations, not validation operations. Vera is not raising a stylistic objection. She is raising a structural one: the current rule gives Evan write authority over a file that Dana produces.

**Additional finding I must add:** the `interpretation_metadata.json` schema template embedded in my SOP (section "Every analysis run produces an `interpretation_metadata.json`...") still shows the deprecated vocabulary `pro_cyclical | counter_cyclical` in the `expected_direction` and `observed_direction` field definitions. This predates Dana taking ownership of the file. The template must be updated simultaneously with the ECON-DIR1 recast.

**Rule rewrite:**

The rule is correct in substance — the invariant (observed_direction == winner_summary.direction) must be checked. The voice must change from producer to consumer. Specifically:

- "Before finalizing `interpretation_metadata.json`" → "Before accepting Dana's `interpretation_metadata.json` handoff"
- "set `observed_direction`... update `key_finding`... set `direction_consistent`" → "return to Dana with a documented mismatch report; Evan does NOT write to `interpretation_metadata.json` directly"

The reconciliation procedure steps (a)(b)(c) are not deleted — they specify what Dana must do in response to Evan's escalation. They should be relabeled as "reconciliation instructions to dispatch to Dana" not "steps Evan performs."

**Acknowledgment to Ray's position:** Ray's Round 1 position (Contradiction 1, Summary row 1) agrees with my Round 1 position — "Evan writes `observed_direction` once, from `winner_summary.json.direction`, as the last step of his handoff." I must respectfully revise: now that Dana is confirmed as the producer, neither of us was fully correct in Round 1. The correct architecture is: Dana writes `interpretation_metadata.json` including `observed_direction`; Evan validates at receipt that `observed_direction` matches `winner_summary.json.direction`; if not, Evan escalates to Dana. Evan is a consumer-gatekeeper, not a co-author.

---

## Challenge D6 — Direction Vocabulary Validation Gap

**Vera's claim:** Evan's SOP deprecates `counter_cyclical` in favor of `countercyclical` (single-word). Ray's RES-OD1 checks `observed_direction == winner_summary.direction` (equality) but does NOT validate vocabulary. A pair where both fields are the deprecated hyphenated form would pass RES-OD1 while violating the schema. Vera's direction-annotation logic silently fails on the deprecated form.

**Verdict: Vera is correct. I concede and expand.**

**Breakdown of the actual problem:**

1. `winner_summary.schema.json` enforces the single-word vocabulary via JSON schema enum — schema validation by `validate_schema.py` catches a wrong-vocabulary `direction` field in `winner_summary.json`. That gate is working.

2. `interpretation_metadata.json` does NOT have a formal JSON schema. There is no `validate_schema.py` run against it. The schema is informally specified in my SOP section "Every analysis run produces an `interpretation_metadata.json`..." — and that template still shows `pro_cyclical | counter_cyclical` (the old underscore-spaced form) in the field definitions.

3. RES-OD1's equality check (`observed_direction == direction`) passes if both fields are consistently wrong (e.g., both are `counter_cyclical`). The equality check is a consistency gate, not a vocabulary gate.

4. Vera's direction-annotation visual encoding keys on string values. If `countercyclical` is the expected string and the JSON contains `counter_cyclical`, Vera's annotation silently produces no match and falls back to default behavior (which may or may not be visible).

**Who should own the vocabulary gate?**

Both agents have a role. The clean answer is:

- **Evan owns the vocabulary standard** (ECON-DIR1 already states the deprecation). Evan must also own a formal schema for `interpretation_metadata.json` analogous to `winner_summary.schema.json`. Until that schema exists, Evan must add an explicit vocabulary assertion to the ECON-DIR1 consumer gate: when validating Dana's file at receipt, assert that `observed_direction` is one of `{procyclical, countercyclical, mixed}` (no underscores, no hyphens). If the value is outside this set, the file is non-conformant and must be returned to Dana.

- **Ray's RES-OD1 should add a vocabulary assertion** alongside the equality check. Ray is running a script that already reads both fields. Adding `observed_direction in VALID_VOCAB` to that script costs one line and eliminates the category of "both fields consistently wrong but consistent with each other." Ray's Round 1 position (Summary: "Evan writes, Ray verifies") is the correct framing — the verifier should check both value AND vocabulary, not just equality.

**Rule changes I will make:**

1. In ECON-DIR1: add a vocabulary assertion step to the consumer-side gate: "Assert `observed_direction` is in the vocabulary set `{procyclical, countercyclical, mixed}` before accepting the handoff. Reject any file containing underscore-separated or hyphenated variants."

2. In the `interpretation_metadata.json` schema template: update field definitions for `expected_direction` and `observed_direction` from `pro_cyclical | counter_cyclical | ambiguous | conditional` to `procyclical | countercyclical | mixed` (aligning with the `winner_summary.schema.json` vocabulary and dropping `ambiguous` and `conditional` which are not in the schema enum).

3. I will NOT change Ray's SOP — that is Ray's domain. But I will note in my rule that the ECON-DIR1 vocabulary assertion is a minimum; Ray should independently extend RES-OD1 to include the same check. The vocabulary standard is mine to own; Ray's enforcement of it in RES-OD1 is Ray's rule change to make.

---

## Summary of Concessions and Changes

| Challenge | Vera Correct? | Action |
|-----------|---------------|--------|
| D2: ECON-DIR1 producer voice | **Yes** | Recast ECON-DIR1 as consumer-side validation gate; remove write-operation instructions from rule body; reframe reconciliation steps (a)(b)(c) as "escalation instructions to Dana" |
| D6: vocabulary gap in ECON-DIR1 | **Yes** | Add explicit vocabulary assertion (`procyclical\|countercyclical\|mixed` only) to ECON-DIR1; update `interpretation_metadata.json` schema template to use single-word vocabulary |
| D6: where should vocabulary gate live | **Shared** | Evan owns the standard and enforces at ECON-DIR1 receipt; Ray should extend RES-OD1 independently (Ray's call, not mine to prescribe) |

**SOP changes follow immediately in commit `Wave 10J [Evan] R2: ...`**

---

*Econ Evan — Wave 10J Debate Round 2 — 2026-04-24*
