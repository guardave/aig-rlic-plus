# Wave Plan: ECON-3PERIOD — Three-Period Split as Default Design
**Date:** 2026-05-08  
**Lead:** Lesandro  
**Status:** OPEN

## Motivation

The current two-period IS/OOS design uses the OOS window for both tournament ranking (winner selection) and reported performance. This means the "OOS Sharpe" is not a clean holdout — the tournament searched over it. A pair can never satisfy ECON-FE1 condition 2 ("confirmation window did not help select the rule") on two-period data. Three-period design (IS / Validation OOS / Confirmation holdout) provides a genuinely sealed third window untouched by selection, enabling clean `passed_final_exam` promotion.

**Decision (2026-05-08):** Three-period is the required default. Two-period is a data-constrained fallback only, permanently capped at `needs_final_exam`.

---

## Change Items

### NORM-3P-01 — New rule ECON-OOS4 in Evan SOP
**Owner:** Evan  
**File:** `docs/agent-sops/econometrics-agent-sop.md`  
**Change:** Add rule ECON-OOS4 — Three-Period Split Policy, immediately after ECON-OOS2.

Content:
- Three-period split is the required design when `total_sample_months >= 84`.
- Periods:
  - **In-sample (IS):** used to fit models and compute signals.
  - **Validation OOS:** used by the tournament to rank rules and select the winner. Sized by ECON-OOS2 formula applied to (total_sample_months − holdout_months).
  - **Confirmation holdout:** sealed until final exam. Minimum size: 252 trading days (daily equity/rates/credit), 36 observations (monthly macro), 365 calendar days (crypto_daily). Carved from the chronological end of available data.
- When `total_sample_months < 84`: two-period fallback is permitted. `oos_split_record.json` must record `split_design: "two_period_data_constrained"` with explicit justification. Pair is permanently capped at `needs_final_exam` — it may never be promoted to `passed_final_exam` regardless of numeric performance.
- Holdout sizing: confirmation holdout = max(252 trading days, 12 calendar months) for daily equity class. Carved before applying ECON-OOS2 formula to the remainder.
- `oos_split_record.json` gains new fields per NORM-3P-02.

**Acceptance (positive):**  
`grep -c "ECON-OOS4" docs/agent-sops/econometrics-agent-sop.md` → ≥ 1  
`grep -c "two_period_data_constrained" docs/agent-sops/econometrics-agent-sop.md` → ≥ 1  
`grep -c "total_sample_months >= 84\|total_sample_months < 84" docs/agent-sops/econometrics-agent-sop.md` → ≥ 1

**Acceptance (negative):**  
`grep -c "two.period.*first.class\|two-period.*default\|two.period is.*default" docs/agent-sops/econometrics-agent-sop.md` → 0

---

### NORM-3P-02 — Update ECON-OOS1 field table in Evan SOP
**Owner:** Evan  
**File:** `docs/agent-sops/econometrics-agent-sop.md`  
**Change:** Add four optional fields to the `oos_split_record.json` field table under ECON-OOS1:

| Field | Type | Description |
|-------|------|-------------|
| `split_design` | string | `"three_period"` or `"two_period_data_constrained"` |
| `holdout_start` | date | First date of the confirmation holdout (three-period only) |
| `holdout_end` | date | Last date of the confirmation holdout (three-period only) |
| `holdout_n_obs` | integer | Trading-day count of the confirmation holdout |

Existing `oos_start`/`oos_end` map to the **validation OOS** in a three-period design. Add clarifying note: "In three-period design, `oos_start`/`oos_end` = validation window; `holdout_start`/`holdout_end` = confirmation holdout."

**Acceptance (positive):**  
`grep -c "split_design\|holdout_start\|holdout_end\|holdout_n_obs" docs/agent-sops/econometrics-agent-sop.md` → ≥ 4

**Acceptance (negative):**  
`grep -c "oos_start.*confirmation\|oos_end.*confirmation" docs/agent-sops/econometrics-agent-sop.md` → 0  
(The old conflation of oos_start with confirmation start must be absent.)

---

### NORM-3P-03 — Update ECON-FE1 condition 2 in Evan SOP
**Owner:** Evan  
**File:** `docs/agent-sops/econometrics-agent-sop.md`  
**Change:** Extend condition 2 with explicit language: "In a three-period design, the confirmation window = holdout period (third period); it is structurally separated from the validation OOS and cannot have informed selection. In a two-period design, condition 2 cannot be fully satisfied — the pair is permanently capped at `needs_final_exam` regardless of other numeric outcomes."

**Acceptance (positive):**  
`grep -c "three.period.*holdout\|three-period.*holdout" docs/agent-sops/econometrics-agent-sop.md` → ≥ 1  
`grep -c "permanently capped\|two.period.*needs_final_exam\|two-period.*needs_final_exam" docs/agent-sops/econometrics-agent-sop.md` → ≥ 1

**Acceptance (negative):**  
`grep -n "condition 2" docs/agent-sops/econometrics-agent-sop.md | grep -c "two.period.*passed_final_exam\|two-period.*passed_final_exam"` → 0

---

### NORM-3P-04 — Update `final_exam_results.schema.json` sample block
**Owner:** Evan  
**File:** `docs/schemas/final_exam_results.schema.json`  
**Change:**
1. Bump `x-version` from `1.0.1` to `1.1.0`.
2. Add `holdout_type` enum values: `"three_period_holdout"` and `"two_period_data_constrained"` (alongside existing `"chronological"`, `"nested_walk_forward"`, `"locked_rule_forward"`).
3. Add optional fields to `sample` block: `validation_start` (date), `validation_end` (date) — populated in three-period designs to record the validation OOS window explicitly.
4. Add `split_design` (string, enum: `"three_period"`, `"two_period_data_constrained"`) as required field in `sample` block.

**Acceptance (positive):**  
`python3 -c "import json; s=json.load(open('docs/schemas/final_exam_results.schema.json')); print(s['x-version'])"` → `1.1.0`  
`grep -c "three_period_holdout\|two_period_data_constrained" docs/schemas/final_exam_results.schema.json` → ≥ 2  
`grep -c "validation_start\|validation_end\|split_design" docs/schemas/final_exam_results.schema.json` → ≥ 3

**Acceptance (negative):**  
`python3 -c "import json; s=json.load(open('docs/schemas/final_exam_results.schema.json')); assert s['x-version'] != '1.0.1', 'old version still present'"` → no AssertionError

---

### NORM-3P-05 — Update `docs/glossary.md` (Lead-owned)
**Owner:** Lead  
**File:** `docs/glossary.md`  
**Change:**
1. Update **OOS window** entry: clarify it refers to the validation OOS (second period) in a three-period design — not the confirmation holdout.
2. Update **Confirmation window** entry: clarify it refers to the holdout (third period) in a three-period design; in a two-period design, no clean confirmation window exists and the pair is capped at `needs_final_exam`.
3. Add new entry **Validation OOS**: the second period in a three-period design, used by the tournament to rank and select rules. Exposed to selection; cannot serve as a confirmation holdout.

**Acceptance (positive):**  
`grep -c "## Validation OOS" docs/glossary.md` → 1  
`grep -c "three.period\|three-period" docs/glossary.md` → ≥ 2

**Acceptance (negative):**  
`grep -c "OOS window.*confirmation\|confirmation.*OOS window" docs/glossary.md` → 0  
(The old conflation of OOS window with confirmation window must be gone.)

---

### NORM-3P-06 — Register ECON-OOS4 in `docs/standards.md` (Lead-owned)
**Owner:** Lead  
**File:** `docs/standards.md`  
**Change:** Add ECON-OOS4 row to the standards table under §ECON-OOS.

**Acceptance (positive):**  
`grep -c "ECON-OOS4" docs/standards.md` → 1

**Acceptance (negative):**  
`grep -c "ECON-OOS4" docs/standards.md` ≠ 0 is the positive check — negative is confirmed by the positive being exactly 1 (no duplicate rows).  
`grep -c "ECON-OOS4" docs/standards.md` → exactly 1

---

## Execution order
1. Evan: NORM-3P-01, 02, 03, 04 (can be done in a single dispatch — all Evan-owned files)
2. Lead: NORM-3P-05, 06 (glossary + standards — Lead-owned, done after Evan confirms)
3. Lead: Update `docs/sop-changelog.md`
4. Lead audit: re-run all acceptance commands; verify no negative patterns present

## What this wave does NOT cover
- Re-running the `hy_ig_v2_spy` tournament on the three-period split — that is a separate wave (ECON-3PERIOD-APPLY) dispatched after these SOPs are accepted.
- Backfilling other existing pairs — deferred; existing pairs remain at current status.
