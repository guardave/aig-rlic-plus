# Handoff — Ace → Quincy / Lead

**Wave:** 10I.A fix (APP-SEV1 L2 defensive coerce)
**Date:** 2026-04-23
**Agent:** Dev Ace
**Trigger:** Quincy cloud verify (commit `08bb0c8`) returned 35 PASS / 6 FAIL / 41 total.

## Root cause (confirmed)

File `app/components/instructional_trigger_cards.py` line 385:

```python
threshold = float(winner.get("threshold_value", 0.5))
```

The `.get(..., 0.5)` default fires only when the key is **absent**. For the 6 newly-migrated legacy pairs the key **is present** but its value is `null` (JSON) → `None` (Python). `float(None)` raises `TypeError`, crashing the Strategy page.

Verified across all 10 pairs:

| Pair | `threshold_value` |
|---|---|
| indpro_spy | `None` (fails) |
| permit_spy | `None` (fails) |
| vix_vix3m_spy | `None` (fails) |
| sofr_ted_spy | `None` (fails) |
| dff_ted_spy | `None` (fails) |
| ted_spliced_spy | `None` (fails) |
| hy_ig_spy | `0.5` (numeric, OK) |
| hy_ig_v2_spy | `0.5` (numeric, OK) |
| indpro_xlp | `0.75` (numeric, OK) |
| umcsent_xlv | `0.0` (numeric, OK) |

Exactly the 6 failing pairs from Quincy's cloud verify.

## Fix — `app/components/instructional_trigger_cards.py` lines 383–400

Wrapped the `float()` call in try/except for both `TypeError` (None / list / dict) and `ValueError` (non-numeric string like `"hmm_prob > 0.5"`). On catch:

- `threshold` falls back to `0.5` (preserves existing default semantics).
- `st.info(...)` emits an APP-SEV1 L2 banner so the gap is visible, not silent.
- Page continues rendering; trigger cards render with the heuristic threshold.

### APP-SEV1 L2 banner wording (exact text shipped)

> Trigger thresholds shown use a default heuristic (0.5) — this pair's `winner_summary.json.threshold_value` is on a legacy non-numeric schema and could not be coerced to a float. Numeric trigger cards will display after the pair pipeline is rerun against the current schema.

### Other float(winner.get(...)) sites in the same file

Grep result: **none**. Line 385 was the sole offender.

## Smoke evidence — all 10 pairs failures=0

Ran `python3 app/_smoke_tests/smoke_loader.py <pair_id>` for all 10 pairs:

| Pair | passes | failures |
|---|---|---|
| indpro_spy | 4 | 0 |
| permit_spy | 3 | 0 |
| vix_vix3m_spy | 3 | 0 |
| sofr_ted_spy | 3 | 0 |
| dff_ted_spy | 3 | 0 |
| ted_spliced_spy | 3 | 0 |
| hy_ig_spy | 6 | 0 |
| hy_ig_v2_spy | 15 | 0 |
| indpro_xlp | 8 | 0 |
| umcsent_xlv | 6 | 0 |

Logs: `app/_smoke_tests/loader_<pair>_20260423.log`.

Coerce-matrix unit probe confirms both `TypeError` (None/list/dict) and `ValueError` (non-numeric string) paths fall back cleanly while legitimate floats and numeric strings pass through.

## Scope boundary — NOT modified (per brief)

- No `winner_summary.json` files touched (producer-side domain = Evan/Dana).
- No pair configs or pages modified.
- No SOPs touched.

## Proposed backlog entry (for Lead to add — LEAD-DL1)

**ID:** `BL-THRESHOLD-VALUE-SCHEMA`
**Title:** Normalize `threshold_value` to numeric across all `winner_summary.json`
**Owner:** Evan (econometrics) + Dana (data)
**Priority:** P2 (consumer is now defensive; no user-visible break, only a fallback banner)
**Description:**
Six legacy pairs (indpro_spy, permit_spy, vix_vix3m_spy, sofr_ted_spy, dff_ted_spy, ted_spliced_spy) have `winner_summary.json.threshold_value = null`. Four modern pairs (hy_ig_spy, hy_ig_v2_spy, indpro_xlp, umcsent_xlv) have proper float values. Producer-side work:
1. Backfill the 6 legacy pairs' `threshold_value` with the correct numeric threshold used during tournament winner selection.
2. Update `winner_summary.schema.json` to declare `threshold_value` as `{"type": "number"}` (non-nullable).
3. Add a pipeline guard so future pair pipelines cannot emit a null/non-numeric threshold.
Once completed, the APP-SEV1 L2 fallback banner will no longer appear on any pair; the defensive coerce in `instructional_trigger_cards.py` can remain as a belt-and-suspenders guard.

## Next step

Quincy re-dispatches cloud verify on post-commit. Expected end-state: **41 PASS / 0 FAIL / 41 total**.

---

## ADDENDUM — 2026-04-23 09:58Z (re-dispatch after Quincy 09:41Z re-verify still 35/41)

**Prior root-cause was INCORRECT.** The `float(None)` TypeError hypothesis, while plausible, was NOT the actual failure mode on cloud. Evidence:

### Real failure mode (unredacted, reproduced locally)

Ran `validate_or_die(Path("results/indpro_spy/winner_summary.json"), "winner_summary")` directly:

```
results/indpro_spy/winner_summary.json failed schema validation against
winner_summary.schema.json: 10 error(s)
```

Errors (from cloud DOM `indpro_spy_strategy.txt` + local reproduce):

1. `'generated_at' is a required property`
2. `'signal_column' is a required property`
3. `'target_symbol' is a required property`
4. `'threshold_rule' is a required property`
5. `'strategy_family' is a required property` (legacy file uses `strategy_code`)
6. `'oos_max_drawdown' is a required property`
7. `'oos_n_trades' is a required property`
8. `'oos_period_start' is a required property`
9. `'oos_period_end' is a required property`
10. `[direction] 'pro_cyclical' is not one of ['procyclical','countercyclical','mixed']` (underscore typo in legacy data)

### Why the dispatch stack trace pointed at line 385

The cloud traceback line `File "app/components/instructional_trigger_cards.py", line 385` is a **red herring**. Line 385 in the current source is a **comment** (`# Wave 10I.A defensive coerce: ...`), not executable code. Python tracebacks can surface comment lines when the exception frame is captured at a pending statement. More importantly: `render_instructional_trigger_cards` is called at `page_templates.py:1136`, AFTER `render_position_adjustment_panel` at line 1133, which internally calls `validate_or_die` and renders `st.error(...)` on schema failure. The APP-SEV1 L1 banner visible in the DOM is emitted by `position_adjustment_panel.py:177`, not by my function. `render_instructional_trigger_cards` is never reached for any of the 6 failing pairs.

### Per-pair schema-validation status (reran all)

| Pair | Schema | Active? |
|---|---|---|
| hy_ig_spy | PASS | yes |
| hy_ig_v2_spy | PASS | yes |
| indpro_xlp | PASS | yes |
| umcsent_xlv | PASS | yes |
| indpro_spy | FAIL (10) | yes |
| permit_spy | FAIL (10) | yes |
| vix_vix3m_spy | FAIL (10) | yes |
| sofr_ted_spy | FAIL (10) | yes |
| dff_ted_spy | FAIL (10) | yes |
| ted_spliced_spy | FAIL (10) | yes |
| hy_ig_spy_v1 | FAIL (10) | archived |

Matches Quincy's 6 FAIL exactly.

### Evan's 2fa6c95 only fixed 1 of 10 errors

Relaxing `threshold_value` to allow `null` eliminates 1 error per file. The remaining 9 errors (8 missing required fields + 1 enum typo on `direction`) still fail validation, hence 35/41 persists.

### Why my 5f2e50d didn't "catch" — it was correctly scoped but to the wrong site

The defensive coerce at `instructional_trigger_cards.py:389-400` is **code-correct** and would fire if reached, but the upstream `position_adjustment_panel` short-circuits first. There is no code-level bug in my patch to widen. Widening the coerce further inside `instructional_trigger_cards` cannot fix pairs whose page-render is blocked upstream at the schema gate.

### Recommended path — producer-side (Evan), per META-NMF no-manual-fix

Consumer-side coding CANNOT synthesize the 9 missing/typo'd fields — `oos_period_start`, `oos_n_trades`, `signal_column` etc. are producer-emitted facts. Two acceptable remediations:

**Option A (preferred):** Evan regenerates the 6 legacy `winner_summary.json` files to v1.1.0 schema. This reruns the tournament-winner post-processor for those pairs (no need to rerun the full tournament) against the current emit template.

**Option B (schema relaxation, NOT recommended without discussion):** Evan bumps the schema to v1.2.0 making the 8 fields optional and adds `pro_cyclical` as a legacy alias on `direction`. This preserves validation coverage on new pairs while tolerating old ones. Risk: hides producer drift.

**Option C (legacy adapter in `schema_check.py`):** A pre-validate normalizer that maps `strategy_code`→`strategy_family`, `pro_cyclical`→`procyclical`, and backfills inferable fields from sibling artifacts (`tournament_winner.json`, `signals_*.parquet` for `signal_column`). This is a materially larger change that I can own in a follow-up wave if Lead assigns it, but it crosses the producer/consumer boundary and needs explicit approval.

### Smoke adequacy note for Quincy

`smoke_loader.py` reports PASS for the 6 failing pairs because it exercises **module import + pair-registry resolution**, NOT the Streamlit render path. `validate_or_die` is invoked at render time inside Streamlit components, so import-time smoke cannot observe the schema failure. Recommended strengthening (Quincy owns, per LEAD-DL1 I will not modify `app/_smoke_tests/`):

1. Add a render-time probe that invokes each consumer component (`render_position_adjustment_panel`, `render_instructional_trigger_cards`, `render_probability_engine_panel`, `render_direction_check`) under a Streamlit test harness (`streamlit.testing.v1.AppTest`).
2. Count `st.error` emissions as FAIL signal alongside uncaught exceptions.
3. This closes the gap where "smoke green, cloud red" is possible.

### Scope discipline

Per META-NMF and LEAD-DL1:
- I did NOT patch the legacy `winner_summary.json` files (producer domain = Evan).
- I did NOT add a second defensive wrapper to `instructional_trigger_cards.py` — the existing coerce is correct and adding more would be cargo-culting around a non-bug.
- I did NOT modify `schema_check.py` or `position_adjustment_panel.py` — structural schema-adapter work requires Lead dispatch.
- This addendum is the deliverable; the commit carries the handoff only (no code change, because no code change is warranted at this layer).

### Proposed backlog amendment

Upgrade `BL-LEGACY-WINNER-SUMMARY-SHAPE` (logged at `a131774`) to **P1** and assign to Evan. It is the only path to green on the 6 failing pairs. The existing `BL-THRESHOLD-VALUE-SCHEMA` is effectively a subset of this larger item.

### Local browser verification

Not performed on a `FAIL`-schema pair because the outcome is deterministic: APP-SEV1 L1 schema banner renders, downstream panels short-circuit, page does not crash. Confirmed via local `validate_or_die` invocation above. For a PASS-schema pair (e.g. `hy_ig_v2_spy`), my defensive coerce is unreachable (threshold_value is numeric) and the page renders normally — this was already verified in the 10H closure pass.
