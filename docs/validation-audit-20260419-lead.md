# System-Level Validation Audit — Lead Lesandro — 2026-04-19

**Auditor:** Lead-assist (system-level scope)
**Scope:** Gates, meta-rules, and coordination contracts (NOT agent-lane work — that is covered by the 5 parallel agent audits)
**Input:** `docs/agent-sops/team-coordination.md`, `docs/standards.md`, `docs/sop-changelog.md`, `docs/stakeholder-feedback/20260418-batch.md`, `results/hy_ig_v2_spy/acceptance.md`, `results/hy_ig_v2_spy/regression_note_20260419.md`, `git log -20`
**Output:** This file only. No SOP, code, or artifact edits.

---

## Axis 1 — Reproducibility at the System Level

### Central question
If HY-IG v2 were re-run from a clean repo, would the 12-commit sequence (`6bcb5e2` → `416ba94`) be reproduced? The answer is **no** — and this is the single most serious reproducibility gap.

### Commit sequence analysis

The 12 commits fall into **three functional waves** that are order-dependent, but **within each wave** the ordering is discretionary:

| Wave | Commits | Order dependency |
|---|---|---|
| 1 — Stakeholder ingestion + SOP Part F | `27c6182`, `6bcb5e2`, `b7ee4ba` | 27c6182 must precede 6bcb5e2 (draft acceptance before stakeholder feedback); 1.5 patches must follow 1.0 |
| 2 — Retro-apply to HY-IG v2 | `b9730cb`, `1f864e8`, `beca5aa` | 2A artifacts/charts/narrative → 2B portal rebuild → acceptance verify |
| 3-4 — Bug fixes + coordination | `519d042`, `1720c0c`, `f295073`, `e28dd3d`, `cc3f551`, `416ba94` | Wave 3 before 4A; 4C-1 (META-CF) before 4C-2 (concrete schemas); 4C-2 before 4D; 4D before 4E verification |

**Within-wave commit batching is undocumented.** Wave 2A batches artifacts + charts + narrative into ONE commit (`b9730cb`); it could equally have been three. Wave 4D batches Dana's and Evan's migrations into one commit (`cc3f551`); they could have been separate. There is **no META-rule** prescribing commit granularity.

### Gate determinism table

| System element | SOP rule | Deterministic? | Discretion point | Captured? | Proposed fix |
|---|---|---|---|---|---|
| Commit sequence | (none) | **No** | Wave ordering, commit batching | Not captured | **META-WCO** (Wave Commit Ordering) |
| GATE-1 (Analysis Brief) | team-coord §Phase 0 | Yes (file-exists) | — | Yes | — |
| GATE-2..8 (dataset, stationarity, results, charts) | team-coord §Deliverables | Yes (file-exists + row count) | — | Yes | — |
| GATE-9..14 (portal + nav) | team-coord §Deliverables | Yes (file-exists + render) | — | Yes | — |
| GATE-15 (catalog status) | — | Yes (string match) | — | Yes | — |
| GATE-16..18 (winner summary + trade log + exec notes) | team-coord §Deliverables | Yes (schema + rows) | — | Yes | — |
| GATE-19..21 (classification) | DATA-D3, RES-B5, DATA-D6 | Yes (enum check) | — | Yes | — |
| GATE-22 (method coverage no-regression) | ECON-C3, RES-5, VIZ-A4 | Partial | "regression note may declare removal with rationale" — rationale is judgment | Gap | **META-RRA** (Removal Rationale Adequacy) |
| GATE-23 (acceptance.md) | META-PAC | Partial | "Lead sign-off" is judgment | Gap | See **META-LSC** below |
| GATE-24 (chart-text coherence) | team-coord §GATE-24 | Yes (grep + same-commit check) | — | Yes | — |
| GATE-25 (no silent chart fallback) | VIZ-V3 | Yes (loader code path) | — | Yes | — |
| GATE-26 (no silent content drop) | META-VNC | Partial | Rationale adequacy | Gap | **META-RRA** |
| GATE-27 (E2E chart render) | VIZ-V5, APP-ST1 | Yes (smoke test log) | — | Yes | — |
| GATE-28 (reference-pair placeholder prohibition) | — | Yes (DOM grep = 0) | — | Yes | — |
| GATE-29 (clean-checkout deploy test) | ECON-DS2 | Yes (exit code) | — | Yes | — |
| acceptance.md 13 compliance rows | META-PAC template | **Partial** | "verification evidence cited" is prose-level; "Stakeholder Review" is human | Gap | **META-EVC** (Evidence Verification Completeness) |
| Wave ordering (which wave first) | META-RPD | **No** | Session-discretionary | Not captured | See **META-WCO** |
| Regression note format (META-RNF) | team-coord §Regression Note Format | Partial | Subsection content is prose | Gap | Adequate for human audit; mechanization not cost-effective |
| Multi-writer merge (interpretation_metadata) | DATA-D6 owner_writes | Yes (dana→evan→ray fixed) | — | **Now yes** (Wave 4C-2) | — |
| Force-redeploy trigger (1720c0c) | (none) | **No** | Lead judgment when Cloud cache stale | Not captured | **META-FRD** (Force-Redeploy Discipline) |

### Acceptance.md mechanical verifiability

Of the 13 compliance-row families in `results/hy_ig_v2_spy/acceptance.md`:
- **Portal-Wide Quality Checklist** (~35 rows): each row is a DOM-presence or file-path check — mechanical.
- **Wave 2/3/4 verification** (~30 rows): each cites a screenshot or results JSON path — mechanical in principle, but "verified Cloud" is a one-shot manual Playwright run; **no machine-readable verification record is archived** beyond the `cloud_wave*_results.json` in `temp/` (which is gitignored).
- **Stakeholder Review** row: **explicitly human** ("Reviewed by: Pending").
- **Lead Sign-off** row: **explicitly human**.

**Net:** 80% mechanical, 20% human. The human 20% is load-bearing (stakeholder judgment is by design); the gap is that the mechanical 80% relies on ephemeral `temp/` artifacts. **Proposed:** mandate `results/{pair_id}/acceptance_verification/` as a gitignore'd-but-tracked directory (or commit the JSON manifests).

### Regression-note format reproducibility

Two different Leads given the same Wave-3 bugs would produce structurally similar regression notes (Changes / Approved By / Unchanged / Impact / Removed sections are prescribed by META-RNF) **but content divergence within each section is unbounded**. E.g., the Wave-4 "Gate-failure learning" subsections are Lead-authored prose. This is appropriate for learning capture but means reproducibility is only structural, not textual. No fix proposed — textual reproducibility is not worth the overhead.

---

## Axis 2 — Stakeholder Resolution Completeness

Earlier stakeholder feedback: 2026-04-18 batch is the **only** batch file in `docs/stakeholder-feedback/`. Prior items (N1-N13, F1-F15 referenced in `regression_note_20260411.md`) are inventoried in regression notes, not in stakeholder-feedback. **First meta-gap: stakeholder feedback directory is not comprehensive.**

### 17-item audit (12 S18-* + 5 SL-*)

| Item | Status | Evidence | Gates passed | Weak resolution? |
|---|---|---|---|---|
| S18-1 | Closed (W2B) | APP-SE1, APP-SE2 rendered; Cloud screenshot | GATE-22, 27 | No |
| S18-2 | Closed (pre-W1) | "user can go back to Story page" | None specific | **YES — deflection not fix** |
| S18-3 | Closed (W2B) | APP-SE5 universal caption on Confidence section | GATE-22 | No |
| S18-4 | Closed (W1) | Cross-link to Evidence page + RES-10 glossary | None | **Partial — deflection + glossary** |
| S18-5 | Closed (Part E) | Hero dual-panel + VIZ-A2 bps label | Pre-gate | No |
| S18-6 | Closed (Part E) | RES-6 glossary expanded | None | No |
| S18-7 | Closed (W1) | Superseded by event | None | No (accepted as-is) |
| S18-8 | Closed (W2A+W2B) | regime_quartile_returns.{csv,json}; ECON-E2 | GATE-22, 26 | No |
| S18-9 | Closed (W2B) | APP-SE3 trigger cards rendered | GATE-22 | No |
| S18-10 | Deferred (by policy) | APP-SE4 placeholder + acceptance open-item | GATE-22 | **Partial — by-design, flagged open** |
| S18-11 | Closed (W2A+W2B) | granger_f_by_lag.{csv,json}; ECON-E1, VIZ-V3 | GATE-22, 25, 27 | No |
| S18-12 | Closed (W2) | RES-9 investor-impact + regime_quartile chart | GATE-22 | No |
| SL-1 | Closed (W2) | RES-11 headline-first; cloud-verified | GATE-23 | No |
| SL-2 | Closed (W3) | VIZ-V2 rev + META-PV + perceptual PNGs | GATE-27 | No |
| SL-3 | Closed (W3) | GATE-24 ownership clarification | GATE-24 | No |
| SL-4 | Closed (W2A+W2B) | META-ZI canonical zoom; RES-8 | GATE-25, 27 | No |
| SL-5 | Closed (W2A+W2B) | Same as SL-4, GFC episode | GATE-25, 27 | No |

### Weak resolutions (2 items)

**S18-2** (regime summary): resolved by "user can go back to Story page" — this is **deflection, not fix**. The stakeholder asked for regime summary IN the strategy context; the response says "find it elsewhere." No SOP rule captures this; no regression-note entry. If Story page is later restructured, the deflection breaks silently.

**S18-4** (Evidence Sources Table): resolved "via cross-link to Evidence page" + RES-10 glossary. Same pattern — the cross-link is the fix. If Evidence page link changes, deflection breaks silently.

**Proposed:** **GATE-30 (Deflection Link Audit)** — any acceptance item whose resolution is "see other page" must have a DOM-link assertion in acceptance.md verifying the target anchor renders AND the redirect text exists on the originating page. One-line addition to the Pair Acceptance Checklist.

### Implicit-resolution risk (items potentially regressive)

Several rules address items indirectly. E.g., APP-SE5 (universal caption) addresses S18-3 AND any future "takeaway missing" complaint; **RES-10 + RES-VS + DATA-VS** collectively address S18-4 AND the broader novel-status-label risk. If APP-SE5 is later scoped down to "Confidence tab only," S18-3-style regressions can recur elsewhere. **Traceability at rule level is sound** (every new rule cites item IDs in both the changelog and standards.md); **traceability at renderer level is weaker** — no test asserts "S18-3 is closed by component X."

### Traceability audit (rule → stakeholder item)

Sampled 10 new rules added 2026-04-19:
- APP-SE1..SE5 → S18-1/3/9/10/4 — all cited in SOP text
- VIZ-V2 rev → SL-2 — cited
- VIZ-V5 → prevention, no specific item — cited in changelog
- GATE-27/28/29 → Dot-Com bug + NBER bug + Cloud parquet bug — cited
- META-PV → Hero NBER bug — cited
- META-CF → Wave 4B cross-review — cited
- ECON-DS2 → Cloud parquet bug — cited
- ECON-E1, E2, H4, H5 → S18-8, S18-11 — cited
- RES-7..11, RES-17, RES-VS → various S18-/SL- — cited
- DATA-VS, DATA-D5, D6 → S18-4 / Wave-2A / ECON-CFO-1 — cited

**Traceability completeness: strong.** Every new rule has a provenance line. No silent rule additions observed.

---

## Axis 3 — Meta-Gaps (between-agent issues)

### Cross-agent boundary bugs (Wave 4B pattern)

Pre-Wave-4B bugs surfaced at boundaries: method-chart mapping forked across Evan/Vera/Ace prose, winner_summary field inventory forked between Evan and Ace, signal_column resolution had a fallback map, direction enum spelling forked (`counter_cyclical` vs `countercyclical`). **Wave 4C-1 (META-CF) + Wave 4C-2 (5 schemas) + Wave 4D-2 (consumer validation)** closes the boundary. However:

- **Only 5 schemas exist**: winner_summary, chart_type_registry, narrative_frontmatter, data_subject, interpretation_metadata. **Not covered**: `tournament_winner.json` (META-TWJ has an inline prose schema — this is the next fork hazard), `execution_notes.md` (no schema, prose-only), `granger_by_lag.csv` + `regime_quartile_returns.csv` (column contracts inline in SOP text, not JSON).
- **APP-DIR1 is 2-way, not 3-way.** Ray's `direction_asserted` leg is stubbed pending narrative-frontmatter migration. **If Evan and Dana both migrate to a new direction value before Ray's narrative migrates, the check cannot detect a 3-way mismatch.**

### Schema versioning coordination

META-CF requires `x-version: semver`. **Unresolved:** what happens when Evan bumps `winner_summary.schema.json` 1.0.0 → 1.1.0 additively? Consumers (Ace) assumed 1.0.0 shape; additive fields are non-breaking, but **there is no `validate_or_die` contract for minor-version drift detection**. If a consumer's validator silently accepts 1.1.0 because it's a superset, a future consumer may rely on a 1.1.0-only field against a 1.0.0 instance. **Proposed:** extend META-CF with a `minimum_schema_version` field on consumer calls. One-line change to `validate_or_die(path, schema_name, minimum_x_version=...)`.

### Cloud stale-cache + force-redeploy (commit 1720c0c)

You pushed a trivial `pair_registry` docstring bump to force a Streamlit Cloud rebuild. This was a one-off; **no META-rule covers the pattern**. Risks:
- Future Leads may not know force-redeploy is a valid tool.
- The trigger condition (Cloud appears stale) is not mechanized — rely on Lead's Playwright inspection.
- **Long-term red flag:** if this becomes routine, the real bug (Cloud cache inconsistency with GitHub push) goes unfixed.

**Proposed:** **META-FRD (Force-Redeploy Discipline)** — a force-redeploy commit must cite the observation (Cloud ≠ HEAD via Playwright), have body text that says "trivial change to trigger rebuild," and be the ONLY change in the commit. Prevents normalization of the pattern.

### MRA (Measure, Review, Adjust) protocol

META-MRA is a mandatory step (`docs/pair_execution_history.md` must be updated). **Audit result: no MRA entry for this HY-IG v2 session.** `docs/pair_execution_history.md` exists but has not been touched in this session's commits (by file-listing grep — file not in the 12-commit diff). This is a **live META-MRA violation**.

**Proposed:** **GATE-23 extension (or GATE-31)** — acceptance.md must cite the MRA entry line in `docs/pair_execution_history.md`. Since Lead signs acceptance.md, Lead enforces MRA.

### Reference-pair tagging procedure

`hy-ig-v2-reference` tag is mentioned 6+ times in acceptance.md as "pending stakeholder approval." **META-RPD says:** "When the reference evolves, flag it." — but the **actual tagging procedure is undefined.** Specifically:
- Who issues `git tag`?
- Is the tag annotated (`-a`) with sign-off text?
- Is the tag pushed (`git push --tags`)?
- What happens to `hy-ig-v2-reference` when HY-IG v3 ships? Does it become `hy-ig-v2-reference-v1` or stay put?

**Proposed:** **META-RPT (Reference-Pair Tagging Protocol)** — 3-bullet procedure: Lead issues annotated tag on stakeholder-approval commit; tag body cites acceptance.md commit + stakeholder name + date; tag pushed in same operation; on reference evolution, OLD tag renamed to `{slug}-v{N}` (preserved).

---

## Axis 4 — Proposed Gates / Meta-Rules

Top four, ordered by coordination-fabric leverage:

### 1. **META-FRD (Force-Redeploy Discipline)** — HIGH
Any commit whose sole purpose is to trigger a Cloud rebuild must (a) be trivial (docstring, comment, whitespace), (b) cite the stale-Cloud observation in the commit body, (c) be alone in the commit (not batched with other work). Rationale: 1720c0c is currently undocumented as a pattern; risks normalization. One paragraph in team-coordination.md §Deploy Verification.

### 2. **META-RPT (Reference-Pair Tagging Protocol)** — HIGH
Codify the `hy-ig-v2-reference` tag procedure: annotated tag, body cites acceptance commit + stakeholder reviewer + approval date, pushed same operation, evolution preserves old tags as `{slug}-v{N}`. Rationale: today this is tribal knowledge; META-RPD refers to the tag but does not specify how to create it.

### 3. **META-SCV (Schema Consumer Version Contract)** — MEDIUM
Extend `validate_or_die(path, schema_name)` signature to `validate_or_die(path, schema_name, minimum_x_version="1.0.0")`. Consumer declares the minimum version it understands; validator blocks on newer major, warns on newer minor, blocks on older minor (missing required fields). Rationale: Evan bumping winner_summary to 1.1.0 additively could break a consumer that assumes 1.0.0 exactly; today this is undefined.

### 4. **GATE-30 (Deflection Link Audit)** — MEDIUM
Any stakeholder item resolved as "see other page" requires: (a) DOM-link assertion target anchor renders, (b) originating-page text contains the redirect, (c) both assertions logged in acceptance.md verification matrix. Closes the S18-2 / S18-4 deflection gap. Single row addition to Pair Acceptance Checklist template.

### (Honorable mentions)

- **META-MRA enforcement via acceptance.md** — acceptance.md cites MRA entry path; gate check is file-exists + today's date in body. Addresses the current live META-MRA violation.
- **META-WCO (Wave Commit Ordering)** — codify the 3-wave structure (ingestion → retro-apply → bug-fix/coordination) as reproducibility scaffold. Lower priority — session-discretionary ordering is arguably a feature, not a bug.
- **META-RRA (Removal Rationale Adequacy)** — GATE-22 / GATE-26 rationale is prose-level; would benefit from a minimum-rationale-length rule or structured-reason enum. Lower priority — risks bureaucratization.

---

## Axis 5 — Decisions for Lesandro

Two genuinely Lead-level calls the system cannot mechanize:

### Decision 1: Is force-redeploy (1720c0c) an acceptable long-term pattern?
Three options:
- **(a) Accept and codify** via META-FRD — pragmatic, low-overhead, preserves current practice.
- **(b) Treat as incident** — investigate Streamlit Cloud cache semantics; fix root cause; ban future force-redeploys.
- **(c) Automate** — CI hook that detects Cloud ≠ HEAD and auto-pushes a trivial bump. Risk: normalizes the pattern further.
**Recommendation:** (a) for now, revisit if it happens >2x/quarter. The underlying Cloud behavior is outside our control; a disciplined META-rule is the right first layer.

### Decision 2: Reference-pair tagging — when, and how strict?
- **Timing:** tag NOW (pre-stakeholder) as `hy-ig-v2-reference-candidate`, promote to `hy-ig-v2-reference` on approval? OR wait for approval and tag once?
- **Strictness:** is `hy-ig-v2-reference` a moving tag (always points to the latest approved state) OR a frozen tag (points to specific commit; v2 approval issues `hy-ig-v2-reference-v1`)?
- **Scope of "approval":** stakeholder sign-off ONLY, or stakeholder + one independent review?
**Recommendation:** frozen tag, stakeholder-only approval, pre-approval `-candidate` suffix. Rationale: frozen tags are Git-native; candidate suffix makes the gate visible; single-reviewer approval matches current practice (one stakeholder = YYY / 土撥鼠C2 / Rex / AF review group).

### Honorable mentions (lower stakes)
- Is MRA violation acceptable for this session given scope? (Lead judgment — system says no.)
- Should `docs/stakeholder-feedback/` be backfilled for earlier batches (N1-N13, F1-F15)? Low value; regression-notes already capture them.

---

## Appendix: System elements audited (count)

- **Gates:** 29 (GATE-1 through GATE-29)
- **Meta-rules:** 27 (META-EOI through META-CF in standards.md)
- **Stakeholder items:** 17 (12 S18-* + 5 SL-*)
- **Commits in HY-IG v2 sequence:** 12 (`6bcb5e2` through `416ba94`)
- **Schemas (META-CF):** 5 (winner_summary, chart_type_registry, narrative_frontmatter, data_subject, interpretation_metadata)
- **Agent lanes (covered by parallel audits):** 5 (Dana, Evan, Vera, Ray, Ace)

Total system elements in audit scope: ~90. Severity of gaps found: 2 HIGH (force-redeploy undocumented, reference-pair tagging undefined), 2 MEDIUM (schema version consumer contract, deflection link audit), 1 LIVE violation (META-MRA), plus numerous low-severity items captured in Axis 1 table.
