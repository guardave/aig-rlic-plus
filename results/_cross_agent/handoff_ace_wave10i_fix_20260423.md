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
