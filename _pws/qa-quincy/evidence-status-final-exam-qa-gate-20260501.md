# Evidence Status Final-Exam QA Gate Draft

**Agent:** qa-quincy  
**Date:** 2026-05-01  
**Scope:** QA wording for promotion of `results/{pair_id}/evidence_status.json` from `found_in_search` to `needs_final_exam` or `passed_final_exam`.  
**Position:** Quincy verifies promotion evidence; Quincy does not generate confirmation metrics or fix producer artifacts.

## Gate Name

**GATE-ES1 — Evidence-Status Promotion Verification**

This gate applies only when a pair has an explicit `results/{pair_id}/evidence_status.json` or when a producer/Lead asks to promote a pair above the conservative default `found_in_search`. Missing files remain allowed and continue to default to `found_in_search`; they do not trigger this gate.

## Required Producer Evidence Before QA Starts

A promotion request must include:

1. The changed `results/{pair_id}/evidence_status.json`.
2. A producer evidence note, preferably `results/{pair_id}/evidence_status_confirmation_<YYYYMMDD>.md`, containing:
   - prior status and proposed new status;
   - exact final-exam method name;
   - confirmation window start/end;
   - data cutoff discipline: evidence that the final-exam window did not help select the winning rule;
   - exact command(s) that regenerate the confirmation metrics;
   - metric table with rule, benchmark, deltas, pass/fail thresholds, and raw artifact paths;
   - statement of any failed/partial confirmation attempt.
3. Machine-readable confirmation output, for example `results/{pair_id}/final_exam_confirmation.json`, if Evan defines a schema later.
4. Updated portal evidence if the status is meant to render on landing and Strategy pages.

QA blocks immediately if the promotion request has no reproducible command, no confirmation window, or no artifact tying the selected rule to the claimed final-exam result.

## Verification Commands And Checks

Run these from repo root, replacing `<pair_id>` and filenames as needed.

### 1. Schema validation

```bash
python3 scripts/validate_schema.py --schema docs/schemas/evidence_status.schema.json --instance results/<pair_id>/evidence_status.json
```

Expected: exit 0. Non-zero exit is **FAIL** and blocks promotion.

Also verify the instance identity:

```bash
python3 - <<'PY'
import json
from pathlib import Path
pair_id = "<pair_id>"
path = Path("results") / pair_id / "evidence_status.json"
data = json.loads(path.read_text())
assert data["pair_id"] == pair_id
assert data["status"] in {"needs_final_exam", "passed_final_exam"}
if data["status"] == "passed_final_exam":
    for key in ["confirmation_test", "confirmation_window", "technical_note", "owner"]:
        assert key in data and data[key], key
    assert {"start", "end"} <= set(data["confirmation_window"]), data["confirmation_window"]
PY
```

Expected: exit 0. Any assertion failure is **FAIL**.

### 2. Artifact existence and traceability

```bash
test -s results/<pair_id>/evidence_status.json
test -s results/<pair_id>/evidence_status_confirmation_<YYYYMMDD>.md
rg -n "<pair_id>|confirmation|final exam|holdout|window|status|passed|needs" results/<pair_id>/evidence_status_confirmation_<YYYYMMDD>.md
```

For `passed_final_exam`, QA also verifies every raw artifact cited in the evidence note exists and is non-empty. A citation to a metric with no raw artifact is **FAIL**. A prose-only claim is **FAIL**.

### 3. Reproducibility

Re-run the producer command(s) from the evidence note exactly. The rerun must either:

- reproduce the stated final-exam metrics byte-for-byte or within a declared deterministic tolerance; or
- explain expected nondeterminism with a fixed seed, stored run log, and stable pass/fail decision.

Required QA record:

```text
Command: <exact command>
Exit code: <0/nonzero>
Output artifact(s): <paths>
Metric comparison: <expected vs observed>
Verdict: PASS/PASS-with-note/FAIL
```

Any command that cannot be rerun from a clean repo checkout, depends on uncommitted local files, or silently fetches revised data without a frozen data cutoff is **FAIL** for `passed_final_exam`.

### 4. Anti-gaming checks

QA must look for evidence that the final exam is genuinely post-selection and not just another search pass.

Blocking anti-gaming failures:

- confirmation window overlaps the original tournament selection/search window without an explicit pre-registered split;
- final-exam data was used to choose the winning signal, threshold, lead, direction, strategy family, or benchmark;
- producer changed the winning rule, threshold, direction, filters, transaction-cost assumption, benchmark, or data cleaning after seeing final-exam performance and still calls the result a final exam;
- multiple final-exam variants were tried and only the winner is reported;
- losing or failed confirmation attempts are omitted;
- status is `passed_final_exam` but the technical note says "planned", "pending", "queued", "partial", or equivalent;
- status is `needs_final_exam` but portal copy or acceptance wording implies confirmation has already passed.

PASS-with-note anti-gaming findings:

- final-exam split is valid but short, regime-specific, or low power;
- pass threshold is plausible but not yet standardized in an SOP;
- data cutoff is documented but requires manual verification rather than an automated manifest.

### 5. DOM and dashboard checks

Run or extend cloud/local verification to assert the status is visible where APP-LP8 requires it.

Required rendered-DOM assertions:

- landing card for `<pair_id>` contains the exact canonical label for the status;
- Strategy page contains `Evidence status: <label>` near the Tournament Winner section;
- invalid status files produce an APP-SEV1 L2 warning and the conservative `found_in_search` label;
- no page displays stronger language than the artifact status supports.

Suggested command shape:

```bash
python3 scripts/cloud_verify.py --pair-id <pair_id> --check evidence_status
```

If `scripts/cloud_verify.py` does not yet support this flag, QA may use a focused Playwright script that captures landing and Strategy DOM text into `temp/qa_evidence_status_<pair_id>_<YYYYMMDD>/dom_text/`.

Manual DOM-read requirement:

```text
I read DOM text for landing and <pair_id>_strategy. I found the status label "<label>" and no contradictory confirmation wording.
```

This mirrors HABIT-QA1: script PASS gathers evidence; Quincy still reads the DOM text before signing.

## Result Criteria

### PASS

Use only when all are true:

- schema validation passes;
- status value matches the requested promotion;
- confirmation artifacts exist and are reproducible;
- anti-gaming checks find no blocking issue;
- landing and Strategy DOM render the correct label;
- copy does not overclaim beyond the status.

For `passed_final_exam`, PASS additionally requires a fresh holdout or equivalent post-selection confirmation result with documented pass thresholds and a stable rerun.

### PASS-with-note

Use when the promotion is valid but has a non-blocking caveat, such as:

- confirmation window is short but honestly disclosed;
- pass threshold is not yet standardized but was declared before the confirmation run;
- DOM renders correctly, but the artifact would benefit from a richer `technical_note`;
- `needs_final_exam` is accurate, but the next-step wording is vague.

PASS-with-note may allow `needs_final_exam` and, if Lead accepts the caveat, may allow `passed_final_exam`. The note must be explicit enough for Lead to arbitrate.

### FAIL

Use when any required check fails. FAIL blocks promotion. The pair remains or reverts to `found_in_search` unless Lead writes an override.

Examples:

- schema-invalid status file;
- no reproducible confirmation command;
- final-exam window helped choose the winner;
- confirmation output cannot be tied to the selected rule;
- portal displays `Passed final exam` but the artifact says `needs_final_exam` or is missing;
- status text is correct in JSON but absent from landing or Strategy DOM.

## Blocking Conditions

Block `needs_final_exam` when:

- the artifact is schema-invalid;
- the pair identity is wrong;
- the note does not say what final exam is needed;
- the portal implies the exam already passed.

Block `passed_final_exam` when:

- any `needs_final_exam` blocker applies;
- no post-selection final-exam artifact exists;
- QA cannot reproduce the confirmation result;
- rule/threshold/direction/benchmark changed after seeing holdout results;
- multiple final exams were searched without full disclosure;
- pass/fail thresholds were chosen after results were known;
- DOM/dashboard copy overstates the evidence.

## Evidence Format For QA Findings

```markdown
## QA Verification — GATE-ES1 Evidence-Status Promotion (<date>, Quincy)

### Summary
Pair: <pair_id>
Requested promotion: <old_status> -> <new_status>
Verdict: PASS / PASS-with-note / FAIL
Blocking findings: <n>

### Detailed findings
| # | Category | Check | Result | Evidence | Action |
|---|----------|-------|--------|----------|--------|
| 1 | Schema | evidence_status validates | PASS | `python3 scripts/validate_schema.py ...` exit 0 | none |
| 2 | Artifact | confirmation note + raw outputs exist | PASS | `<paths>` | none |
| 3 | Repro | final-exam command rerun | PASS | `<command>`, metrics expected vs observed | none |
| 4 | Anti-gaming | holdout did not select winner | PASS-with-note | split/cutoff evidence | Lead review |
| 5 | DOM | landing + Strategy show canonical label | PASS | DOM text files in `temp/...` | none |
```

## Proposed QA SOP Patch Text

Do not edit the shared SOP until Lead arbitrates. Proposed insertion after QA-CL2 or in the Standard QA Checklist:

```markdown
### GATE-ES1 — Evidence-Status Promotion Verification

When `results/{pair_id}/evidence_status.json` promotes a pair above the default
`found_in_search`, Quincy independently verifies the promotion before Lead
acceptance. Missing files remain allowed and default to `found_in_search`.

Required checks:
- validate `results/{pair_id}/evidence_status.json` against
  `docs/schemas/evidence_status.schema.json`;
- confirm `pair_id`, `schema_version`, `status`, `updated_at`, and for
  `passed_final_exam`, non-empty `confirmation_test`, `confirmation_window`,
  `technical_note`, and `owner`;
- verify a producer confirmation note and raw metric artifacts exist;
- rerun the stated confirmation command(s) and compare metrics to the claim;
- perform anti-gaming review: the confirmation window did not help select the
  winner, thresholds/rules were not changed after seeing holdout performance,
  failed variants are disclosed, and pass/fail thresholds were pre-declared;
- verify landing-card and Strategy-page DOM show the canonical APP-LP8 label and
  contain no stronger claim than the artifact supports;
- record the finding using PASS / PASS-with-note / FAIL.

Blocking:
- schema invalidity, missing reproducible evidence, selection leakage into the
  final-exam window, undisclosed variant shopping, or DOM/status mismatch blocks
  promotion. The conservative fallback is `found_in_search` unless Lead records
  an override.
```

## Proposed `cloud_verify.py` Hook Shape

```python
def gate_es1_evidence_status(pair_id: str, rendered: dict[str, str]) -> list[GateResult]:
    status, schema_errors = load_status_json(pair_id)
    if schema_errors:
        return [fail(pair_id, "GATE-ES1", "schema invalid; must render conservative fallback")]

    label = APP_LP8_LABELS[status.value]
    results = []
    if label not in rendered["landing"]:
        results.append(fail(pair_id, "GATE-ES1", f"landing card missing {label!r}"))
    if f"Evidence status: {label}" not in rendered["strategy"]:
        results.append(fail(pair_id, "GATE-ES1", f"strategy page missing {label!r}"))
    if status.value != "passed_final_exam" and "confirmed" in rendered["strategy"].lower():
        results.append(fail(pair_id, "GATE-ES1", "strategy copy overclaims confirmation"))
    return results
```

This hook should be DOM-only. It verifies display honesty, not the econometric final-exam math. The reproducibility and anti-gaming checks stay in Quincy's evidence review until Evan defines a stable confirmation-output schema.

## Quincy Recommendation

Adopt GATE-ES1 before any pair is promoted to `passed_final_exam`. Allow `needs_final_exam` only when the artifact names the intended exam and the portal does not imply a pass. Keep all current pairs at the conservative `found_in_search` default until Evan/Lead define the statistical thresholds and a reproducible confirmation artifact.
