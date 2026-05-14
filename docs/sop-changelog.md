# AIG-RLIC+ SOP Changelog

Chronological record of every rule addition and modification across the AIG-RLIC+ agent SOP system. New rules are entered here first, then registered in [`docs/standards.md`](standards.md) and/or [`docs/team-standards.md`](team-standards.md).

Entries are listed newest-first. Each entry cites the commit hash (when available), date, scope, and summarizes what changed.

**SOD read protocol (added Wave 10F):** every agent, at session start, reads this file from the top down to the first entry whose date is earlier than the timestamp in `~/.claude/agents/<role>-<name>/last_seen`. Every entry above that line is a rule added while the agent was away — apply if scope matches.

---

## 2026-05-13 — Sequential wave model: ECON-CAP1, VIZ-CAP1, RES-CAP1, APP-PLB1, QA-CAP1, LEAD-FR1, DPS-FE2 (cross-SOP coordinated change)

**Trigger.** The v4 reference dashboard surfaced a class of defect that the prior parallel-with-Lead-review workflow could not catch: cross-page reconciliation failures where each producer's domain-local output was internally consistent but the assembled portal made contradictory claims. Canonical case: `evidence_status.status = failed_final_exam` with `final_exam_results.holdout_sharpe = 0.31`, but the Story page headlined `OOS Sharpe 1.32` (the tournament-OOS number from `winner_summary.json`) — because no rule said "for failed-exam pairs, holdout numbers are the headline" and no checkpoint forced framing review before Ray and Ace had already wired the wrong number through.

**Diagnosis:** three structural gaps in the prior workflow:

1. Vera owned interpretive chart captions despite not owning the numbers, producing template-boilerplate captions that contradicted visible data ("Consistent positive bars indicate a robust signal" on a chart with a clearly-negative GFC bar).
2. Ray drafted narrative against `analysis_brief` rather than committed `winner_summary` + `evidence_status` + chart outputs, producing prose that framed the wrong window as the headline.
3. Ace silently made content decisions about KPI source selection because no rule routed `evidence_status.status` to a KPI source.

**Changes — sequential wave model with per-step verifier gates (team-coordination.md Standard Task Flow rewritten):**

- **Standard Task Flow rewritten** (`team-coordination.md`) — old 15-step model with single-pass parallel producers + Lead META-CDR at step 10 replaced with **7-step sequential model**: Step 0 Lesandro frames → Step 1 Evan designs tournament → Step 2 Dana collects to spec → Step 3 Evan crunches + writes captions → Step 4 Vera renders → Step 5 Ray narrates → Step 6 Ace plumbs → Step 7 Lesandro META-CDR. Each step produces a named prerequisite artefact; downstream producers cannot begin until upstream artefact is committed and its verifier gate has passed.

**Changes — caption ownership (Evan-owned, with Vera passthrough and Ray voice softening):**

- **ECON-CAP1** (`econometrics-agent-sop.md`) — Evan owns every chart caption that makes a quantitative or interpretive claim. Authored at Step 3 in `results/{pair_id}/chart_captions.json` alongside `winner_summary.json` and `evidence_status.json`. Schema: `{chart_name: {how_to_read, finding, caption_owner: "evan"}}`. Every quantitative reference in a `finding` must be verifiable against `winner_summary.json` or `final_exam_results.json`.
- **VIZ-CAP1** (`visualization-agent-sop.md`) — Vera passthrough contract supersedes Rule A5 for new pairs. Vera copies `chart_captions.json` entries verbatim into `_meta.json` sidecars; cannot paraphrase. Vera authors `caption.what_this_shows` only (provenance). Pre-render check: halt rendering if `chart_captions.json` is missing or incomplete.
- **RES-CAP1** (`research-agent-sop.md`) — Ray's narrative phase begins only after Step 4 commits. Ray may soften Evan's clinical captions for reader voice in Story prose but cannot change quantitative claims. Failed-exam framing rule: when `evidence_status.status == "failed_final_exam"`, Story headline KPIs and lede sentence must reference the holdout result, not the tournament-OOS result.

**Changes — Ace plumbing-only role:**

- **APP-PLB1** (`appdev-agent-sop.md`) — Ace makes no content decisions at portal assembly. Every reader-facing string, number, and display selection traces back to a producer-owned artefact. Content-routing contract names which artefact owns each reader-facing element. Forbidden: Ace selecting KPI source based on which field happens to be populated; Ace softening producer wording; Ace writing fallback strings. Failed-exam KPI routing per DPS-FE2 is the canonical worked example.

**Changes — verifier gates per step:**

- **QA-CAP1** (`qa-agent-sop.md`) — Quincy verifies caption claims at three gates: Gate 1 (Step 3) reads every numeric reference in `chart_captions.json` and confirms it appears in `winner_summary.json` or `final_exam_results.json`; Gate 2 (Step 4) confirms Vera's sidecar copies match `chart_captions.json` verbatim; Gate 3 (Step 5) confirms Ray's narrative-softened phrasing still supports the same quantitative claim. Each gate is blocking for the next producer step.
- **LEAD-FR1** (`lead-agent-sop.md`) — Lead framing review at three checkpoints, not one: Checkpoint 1 (Step 1 tournament design review), Checkpoint 2 (Step 3 framing review — the highest-leverage Lead intervention; verifies `evidence_status.status` is honest and `chart_captions.json` framing matches), Checkpoint 3 (Step 5 GATE-RW1 reader walk). Old META-CDR review at Step 7 becomes safety net, not primary catch.

**Changes — dashboard standard:**

- **DPS-FE2** (`dashboard-page-standard.md`) — Failed-final-exam KPI routing rule. When `evidence_status.status == "failed_final_exam"`, Story and Strategy headline KPIs must show holdout numbers, not tournament-OOS. Includes routing matrix for all 5 status values and window-labelling rule (every KPI labelled with its window in the row, not in body prose).

**Backward compatibility.** Pairs 1-11 are grandfathered — no retroactive caption migration required. Any caption modification after 2026-05-13 must follow the new ownership rules; the modified caption is authored by Evan and lands in `chart_captions.json`. New pairs (Pair #4 — `t10y3m_spy` — onward) use the full 7-step sequence end-to-end.

**Open items for next session:** v4 hot-fix against DPS-FE2 (currently shipping with tournament-OOS Sharpe headlined despite `failed_final_exam` status). Filed the rule first; hot-fix dispatched as separate wave.

---

## 2026-05-12 — DPS-PRE1: Final Exam Hard Gate + failed_final_exam status (new rule + schema v1.2.0)

**Trigger.** The final exam was not codified as a hard gate — pairs could sit at `found_in_search` indefinitely without being blocked from production. A failed exam should still be visible to stakeholders as informational disclosure rather than hidden.

**Changes:**

- **DPS-PRE1** (`dashboard-page-standard.md`) — Hard gate: `found_in_search` and `needs_final_exam` block production registration. `passed_final_exam` and `failed_final_exam` are both production-eligible. The gate is whether the exam was run, not the outcome.
- **`evidence_status.schema.json` v1.2.0** — Added `failed_final_exam` to the status enum. Added `failure_reasons` array field (required for `failed_final_exam`). New allOf constraint requires `confirmation_test`, `technical_note`, `plain_english`, `failure_reasons`, `owner`, and `final_exam` block when status is `failed_final_exam`.
- **`validate_pair_completeness.py`** — New "Prerequisites — Final Exam" check group runs first. FAIL if status is `found_in_search`/`needs_final_exam`. WARN (not FAIL) if `failed_final_exam`, with note that disclosure banner is required.
- **`app/components/evidence_status.py`** — Added `failed_final_exam` to `_STATUS_COPY`. `render_evidence_status_note()` now emits an APP-SEV1 L2 `st.warning` disclosure banner for `failed_final_exam` pairs, surfacing `failure_reasons` verbatim and a "Technical detail" expander for `technical_note`.

---

## 2026-05-12 — GATE-DPS1: Pair Completeness Validation Script (new gate)

**Trigger.** Dashboard Page Standard v1.0.0 defines mandatory sections but had no automated way to verify compliance before render time. Gaps were only discoverable by a stakeholder opening the page.

**Gate added:** `scripts/validate_pair_completeness.py`

- Validates artifacts, config attributes, method block counts, episode slugs, and glossary coverage for any registered pair
- Exit code 0 = PASS, 1 = any FAIL — usable in CI and by Quincy as part of GATE-31
- Ace must run and show clean PASS before META-SRV handoff; Quincy runs independently at GATE-31
- First run against `hy_ig_spy` found 4 real FAILs: `evidence_status` not `passed_final_exam`, `inflation_2022` episode missing from config and chart artifacts

---

## 2026-05-12 — dashboard-page-standard.md: Dashboard Page Standard v1.0.0 (new document)

**Trigger.** V3 experiment forks were accepted at ~17% of production quality because no document explicitly defined which sections are mandatory vs optional. Ace produced what the template would accept without error, not what production quality requires.

**Document created:** `docs/dashboard-page-standard.md` (v1.0.0)

- All page sections declared **mandatory** with the following exceptions: scope note (Story), rolling Sharpe CP / rolling Granger (Evidence cross-period), exploratory insights (Methodology), Dana evaluation radar artifacts
- **DPS-EP1:** Crisis-episode zoom charts — minimum 4 canonical episodes (Dotcom 2000–2002, GFC 2008–2009, COVID 2020, Inflation 2022); all mandatory; pair configs may add more
- **DPS-II1:** Info icon convention — `st.popover("ⓘ")` beside every defined technical term in headings, labels, and KPI cards; implemented via `info_icon(term_key)` in `app/components/glossary_inline.py`; terms sourced from `docs/portal_glossary.json`
- **SOP cross-reference:** APP-PT1 in `appdev-agent-sop.md` now points to this document as the authoritative section spec

---

## 2026-05-12 — APP-NAV1: Cross-Page Navigation Must Use `st.page_link` (new rule)

**Trigger.** Wave v3-EXP-RERUN post-mortem: Ace used `st.markdown("[Label](page_name)")` for breadcrumb and bottom-nav links. These silently 404'd in production — bare markdown hrefs do not route in Streamlit multi-page apps.

**Rule added:**

- **APP-NAV1** (`appdev-agent-sop.md`) — All cross-page navigation MUST use `st.page_link("pages/filename.py", label="Label")`. Bare markdown link syntax for portal pages is prohibited. Gate command: `grep -rn "st.markdown.*\[.*\](" app/pages/ | grep -v "http"` — any non-HTTP markdown link is a violation.

**Template fix:** APP-TT1 compliance now implemented in `page_templates.py` (all four render functions), making it automatically enforced for all pairs that use the template — eliminating the need for per-pair compliance audits.

---

## 2026-05-11 — APP-TT1: Pair Title at Page Top (new rule)

**Trigger.** User observed that navigating to a non-story page provided no immediate visual anchor for which pair was being viewed — banners and breadcrumbs appeared before the pair name.

**Rule added:**

- **APP-TT1** (`appdev-agent-sop.md`) — `st.title(display_name)` must be the first content element after `st.set_page_config()` on every page (Story, Evidence, Strategy, Methodology). No banner, breadcrumb, or warning may precede it. Raw `pair_id` slug as title is prohibited — must use human-readable display name.

**Artifact fix:** All 8 v3 experiment fork pages updated to comply (story pages: title moved above banner; evidence/strategy/methodology: title moved above banner and raw pair_id replaced with display_name).

---

## 2026-05-11 — META-CDR: Cross-Domain Review (new meta-rule)

**Trigger.** Wave 10I post-mortem (2026-05-09): producers completed their tasks and self-verified, but cross-domain issues (PAGE_ROUTING gap, evidence_status.json schema mismatch, column name mismatch `val_sharpe` vs `oos_sharpe`, display_name not wired to card title) were only caught after cloud deploy — not by any single producer's gate. No rule required Lead to audit cross-agent seams *before* Quincy.

**Rule added:**

- **META-CDR** (`team-coordination.md`) — New meta-rule. After producers self-verify (META-SRV) and before QA (GATE-31), Lead runs a structured cross-domain review: seam audit, silently-skipped task check, cross-domain consistency spot-check, CDR verdict logged in wave note. QA is not invoked until CDR passes. Blocking behavior: producers fix CDR findings, re-self-verify, Lead re-runs CDR, then QA.

**Standard Task Flow updated:** Step 10 added ("Lead cross-domain review per META-CDR"); former steps 10–14 renumbered 11–15. Pipeline summary updated from "Producer → QA → Lead" to "Producer → Lead CDR → QA → Lead acceptance."

**Files changed:** `docs/agent-sops/team-coordination.md`, `docs/agent-sops/lead-agent-sop.md`.

---

## 2026-05-09 — ECON-OOS4 retro-apply constraint

**Trigger.** Controlled experiment (`hy_ig_spy_v3_rerun` vs `hy_ig_spy_v3_retro`): same data, same grid, same holdout window — clean rerun selected `S2a_zscore_252d / P1`, retro-apply inherited `S6_hmm_stress / P2`. Different signal families, holdout Sharpe 0.85 vs 1.61. The retro fork's "winner unchanged" confirmation check is not equivalent to blind re-selection on the shortened validation window.

**Rule updated:**

- **ECON-OOS4** (`econometrics-agent-sop.md`, `standards.md`) — Added retro-apply constraint. For any `found_in_search` pair being migrated from two-period to three-period, the full tournament MUST be re-run blind on the shortened validation window. Inheriting the prior winner is prohibited. If the new winner differs, the old winner is retired and all downstream artifacts must reflect the new winner.

**Empirical basis:** `temp/20260509_rerun_vs_retro_comparison/report.html`

---

## 2026-05-08 — GATE-NR-SOP wave — Fix Two Producer-Side SOP Gaps Causing Systematic GATE-NR Failures

**Trigger.** Cloud verify (2026-05-08T20:58Z) returned 14 FAILs across all 10 pairs — every story page and 4 evidence pages — all driven by `gate_nr_result = FAIL`. Root cause: two SOP gaps, not narrative defects.

Gap 1: `target_symbol` blank in `interpretation_metadata.json` for 3 pairs (`hy_ig_v2_spy`, `indpro_xlp`, `umcsent_xlv`). DATA-D6 named `target_symbol` as Dana's field but did not require it to be non-blank. With `target_symbol = ""`, GATE-NR's allow-list contains only the indicator_id, so any mention of the target ETF in the narrative fails.

Gap 2: `gate_nr_comparison_whitelist` never populated on any pair. RES-NR1 required instrument *accuracy* but not whitelist population for legitimate comparative references (e.g., "S&P 500" on SPY-target pairs, "VIX" as economic context). QA-CL5/GATE-NR documented the whitelist mechanism reactively but imposed no delivery gate.

**Rules added/updated:**

- **DATA-D6** (`data-agent-sop.md`) — Added non-blank requirement for `target_symbol`. An empty string is blocking; Dana must populate before handoff. Added checklist bullet.
- **RES-NR1** (`research-agent-sop.md`) — Added whitelist obligation. When narrative legitimately references an out-of-pair instrument for comparison, Ray must add it to `gate_nr_comparison_whitelist` before handoff. Added checklist bullet and handoff log format.
- **QA-CL5/GATE-NR** (`qa-agent-sop.md`) — Added delivery gate. Quincy rejects any pair for cloud verify if `target_symbol` is blank or whitelist is incomplete for confirmed comparative references.

**Artifacts:** `_pws/lead-lesandro/gate_nr_sop_wave_plan_20260508.md`

**Post-wave obligation:** Artifact backfill wave (separate) — Dana populates `target_symbol` for 3 pairs; Ray reviews all 10 pairs and populates `gate_nr_comparison_whitelist`; Quincy re-runs cloud verify targeting 0 GATE-NR FAILs.

---

## 2026-05-08 — META-DM wave — Dispatch Matrix & EOD Dispatch Gate

**Trigger.** After promoting `hy_ig_v2_spy` to `passed_final_exam` via the three-period re-run, the qualitative narrative (Ray) was not reviewed for reconciliation — no SOP rule required it. Per-agent rules would have been combinatorially expensive and drift-prone (META-NCD). A static dispatch matrix in `team-coordination.md` plus a two-item universal EOD extension is the minimal correct fix.

**Rules added:**

- **META-DM** (`team-coordination.md`, `standards.md`) — Dispatch Matrix. Static table mapping producer-artifact changes to downstream agents that must review. Lead consults at every wave closure; dispatches or records skip rationale. Wave may not be marked CLOSED until all obligations resolved.
- **EOD-Lightweight step 5** (`team-coordination.md`) — Universal dispatch gate added to the mandatory EOD block. Agents flag META-DM obligations in their handoff; Lead routes.
- **Lead SOP wave-closure gate** (`lead-agent-sop.md`) — META-DM check added to the self-audit sequence at wave closure.
- **Role SOPs (×6)** — One cross-reference line to META-DM added to each EOD-Lightweight section. No table duplicated (META-NCD).

**Design decisions recorded:** Flag mechanism rejected (runtime state overhead); per-agent checklists rejected (combinatorial, drift-prone); role-specific EOD items rejected (duplicate existing phase checklists); global SOP chosen as canonical home (META-NCD).

**Artifacts:** `_pws/lead-lesandro/meta_dm_wave_plan_20260508.md`

**Post-wave obligation:** `hy_ig_v2_spy` three-period re-run changed `oos_split_record.json` and promoted `evidence_status.json`. META-DM requires Ray, Vera, Ace, Quincy consequential review → ECON-3PERIOD-DOWNSTREAM wave queued.

---

## 2026-05-08 — ECON-3PERIOD wave — Three-Period Split as Required Default

**Trigger.** Retro-apply of ECON-FE1 to `hy_ig_v2_spy` produced `needs_final_exam` because the tournament OOS window (2018–2025) was reused as the confirmation window — the same data that ranked the winner cannot independently confirm it (ECON-FE1 condition 2). No fresh holdout existed because the dataset ends 2025-12-31 and only ~85 post-OOS trading days have elapsed. Root cause: two-period IS/OOS design conflates validation (selection) and confirmation (test) into a single window. User decision: three-period design (IS / Validation OOS / Confirmation holdout) is the required default.

**Rules added/updated:**

- **ECON-OOS4** (`econometrics-agent-sop.md`, `standards.md`) — Three-Period Split Policy. Three-period design required when `total_sample_months >= 84`. Confirmation holdout carved from chronological data end before ECON-OOS2 formula applied to remainder. Minimum holdout: 252 trading days (daily equity/rates/credit). Two-period fallback permitted only when `total_sample_months < 84`; records `split_design: "two_period_data_constrained"`; pair permanently capped at `needs_final_exam`.
- **ECON-FE1 condition 2** (`econometrics-agent-sop.md`) — Updated to make the three-period/two-period distinction explicit. Three-period design structurally guarantees condition 2 via sealed holdout. Two-period design cannot satisfy condition 2 regardless of numeric outcomes; permanently barred from `passed_final_exam`.
- **ECON-OOS1 field table** (`econometrics-agent-sop.md`) — Added `split_design`, `holdout_start`, `holdout_end`, `holdout_n_obs` fields to `oos_split_record.json`. Clarified that `oos_start`/`oos_end` = validation window in three-period design.
- **`final_exam_results.schema.json`** bumped to v1.1.0 — `split_design` required in `sample` block; `validation_start`/`validation_end` optional; `holdout_type` enum extended with `three_period_holdout` and `two_period_data_constrained`.
- **`docs/glossary.md`** — OOS window entry updated to distinguish validation OOS from confirmation holdout. New entry **Validation OOS** added. Confirmation window entry updated to explain three-period vs two-period behaviour and the permanent `needs_final_exam` cap.

**Artifacts:** `_pws/lead-lesandro/econ_3period_wave_plan_20260508.md`

---

## 2026-05-08 — META-AVD added (Acceptance Verification Discipline) — post-BL-SOP-NORMALIZE retro

**Trigger.** User asked: "I wonder if you run their scripts blindly, it implies an unconditional trust on them. Correct?" Lead conceded the gap: BL-SOP-NORMALIZE wave plan specified only positive-pattern acceptance commands. A Layer-3 spot-check after the audit closed confirmed the agents had also retired duplicates, but the confirmation came from ad-hoc grepping, not from the plan's specified criteria. If the agents had been less careful, the wave would have audited PASS while inline duplicates remained alongside the new cross-references.

**Rule added:**

- **META-AVD** (`team-coordination.md` + `standards.md`) — Acceptance Verification Discipline. Wave plans for mechanically-auditable removal/retirement/migration work specify BOTH a positive-pattern acceptance check (what should now exist) AND a negative-pattern check (what should no longer exist). Both run by agent and Lead; both must match. Positive-only audit defends Layers 1 and 2 of trust (no fabrication, well-designed test) but leaves Layer 3 (semantic correctness) on unconditional trust.

**Three layers of trust framing (codified in META-AVD body):**

- Layer 1 — did the agent run the command and report real output? Defended by Lead re-running.
- Layer 2 — does the command measure the right thing? Defended by Lead authoring the commands.
- Layer 3 — does the metric reflect real semantic work? Only defended when both positive and negative checks are specified.

**Pattern templates documented in the rule:** glossary consolidation (positive `grep -c "docs/glossary.md"` ≥ N + negative `grep -c "<term> is/=/—"` = 0); registry deprecation (new canonical exists + 0 references to old path in active prose); canonical-set centralization (single canonical reference + 0 enumerations in non-canonical SOPs); schema bump (per META-SBP — all instances re-validated + 0 instances at old version).

**Companion rules:** META-SRV (verification evidence), META-NCD (failure class this protects against), META-SBP (one specific application of two-sided pattern for schema bumps).

---

## 2026-05-08 — BL-SOP-NORMALIZE Wave (META-NCD + glossary + canonical SSoTs)

**Trigger.** Following the six-phase SOP review, user identified that the deeper risk is duplication structure (drift over time degrades quality), not raw token count. Lead authored a formal change plan with pre-stated mechanical acceptance commands per item; six agents executed in parallel; Lead audit closed.

**Verification mechanism (new pattern).** Each NORM item carried a deterministic shell command + expected output. Agents ran the command after applying changes, pasted output verbatim. Lead re-ran every command in the closing audit. Outputs matched exactly. No prose self-attestation accepted. This adapts META-SRV from per-claim to per-wave-item.

**Rules added:**

- **META-NCD** (`team-coordination.md` + `standards.md`) — Normalization & Concept Discipline. Any concept used in 2+ rulebooks declares one canonical location; other locations cross-reference. Generalizes META-AL from data files to prose.

**Artifacts created:**

- `docs/glossary.md` — single source of truth for cross-SOP terms; 16 entries covering OOS window, Confirmation window, Perceptual render, Thin wrapper, Page template, Pair config module, Sidecar, Disposition, Tournament winner, Block bootstrap, Smoke test, PASS-with-note, Trigger card, `_REPO_ROOT` anchor, Narrative instrument reference, Episode triad.
- `_pws/lead-lesandro/sop_normalize_wave_plan_20260508.md` — change plan with 8 NORM items.
- `_pws/lead-lesandro/sop_normalize_audit_20260508.md` — closing audit (every item PASS).

**Canonical SSoTs ratified:**

- Status vocabulary canonical at `docs/portal_glossary.json._status_vocabulary` (via RES-10 / RES-VS / DATA-VS). Five role SOPs retired prose enumerations; Ray retains one canonical citation.
- L1/L2/L3 severity scheme canonical at APP-SEV1. Five role SOPs replaced paraphrases with cross-references.
- Cross-SOP terminology canonical at `docs/glossary.md`. Each role SOP refactored inline definitions to glossary cross-references; canonical authorities (e.g., VIZ-CV1 for perceptual render, RES-NR1 for narrative instrument reference) retain operational rules with "see glossary" pointers.

**Process meta-event.** Wave closed first-pass clean — zero residue items at Lead audit. Contrast with the six-phase review wave, which required a Phase-5 fix-up dispatch for four residues caught only by ad-hoc Lead grep. The difference is the pre-stated mechanical acceptance command: agents had a deterministic target before starting, Lead had a deterministic check at audit, no interpretation gap in either direction. Pattern adopted for future mechanically-auditable waves.

**Anti-filler note (per user request 2026-05-08).** All agents and Lead drop filler words and ceremonial openings in handoff prose, summaries, and status-board entries. Substance only.

**Out of scope (deferred to backlog):**
- BL-VIZ-V11-LINT — VIZ-V11 palette lint script externalization (pseudocode → real script).
- BL-GATE-CL-AUDIT — GATE-CL family audit script.
- Schema field enumeration replacement in rule prose (substantial; separate wave).
- Cross-reference list compression (low drift risk; defer).

---

## 2026-05-08 — Six-Phase SOP Review Wave

**Trigger.** User dispatched a full six-phase SOP review (intra → Lead protocol → cross-review → fixes → Lead review → token/rapport pass).

**Phase counts.** Phase 1 intra-SOP review: ~90 findings across six role SOPs. Phase 2 Lead protocol/global review: 10 binding arbitrations (LA-1..LA-10), 6 backlog items. Phase 3 cross-review: ~133 handoff findings across six pairs of cross-reviews. Phase 4: ~117 SOP edits + 8 schema/registry edits + standards.md batch + META-SBP promotion.

**Lead arbitrations promoted to binding.**

- **LA-1** — `docs/schemas/history_zoom_events_registry.json` is the canonical episode registry. `docs/schemas/episode_registry.json` deprecated and converted to thin pointer.
- **LA-2** — Canonical episode slug set: `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`. Non-canonical (`dot_com`, `rates_2022`, `taper_2013`, etc.) prohibited. `china_2015` promoted to registry by Vera based on existing pair coverage; `ukraine` documented as non-canonical until promotion PR.
- **LA-3** — `HISTORY_ZOOM_EPISODES` is the canonical pair-config attribute for zoom narratives. `ZOOM_EPISODE_NARRATIVES` retired.
- **LA-4** — `observed_direction` ownership clarified: Evan writes post-tournament; Dana leaves absent at data-stage handoff. APP-DIR1, ECON-DIR1, DATA-D6 all updated accordingly.
- **LA-5** — `docs/standards.md` batch update registering all unregistered rules (DATA-D6b, DATA-EV1, ECON-T4, ECON-INF1, ECON-DIR2, ECON-OOS3, ECON-C2a, ECON-BUMP1, VIZ-IC1, VIZ-O1, VIZ-E1, VIZ-NBER1, VIZ-ZOOM1, VIZ-HZE1, VIZ-DP1, VIZ-NM1, VIZ-CP1, VIZ-CV1, RES-NR1, RES-EGL1, RES-OD1, RES-CPC1, RES-CP1, RES-CP2, RES-HZE1, RES-ZOOM1, APP-PT1, APP-PT2, APP-TL1, APP-PR1, APP-RL1, APP-SS1, ACE-HZE1, GATE-DP1, GATE-HZE1, GATE-VIZ-NBER1, GATE-VIZ-NBER2, GATE-VIZ-ZOOM1, GATE-CL6, GATE-CL7, GATE-CL8, GATE-NR, GATE-SD1, META-SBP).
- **LA-6** — GATE-CL family (CL1–CL8) registered under GATE prefix in `docs/standards.md`.
- **LA-7** — `memories.md` requirement removed from research-agent-sop.md; Ray consolidates to `experience.md`. META-AM amended with Ray exemption.
- **LA-8** — Schema-bump propagation rule promoted from Evan-side to cross-agent META rule (META-SBP) in `team-coordination.md`.
- **LA-9** — ECON-SD audit gate (GATE-SD1) added to QA SOP and `cloud_verify.py`.
- **LA-10** — Stale items retired: matplotlib palette table (Vera), v1.0.0 schema citation (Evan), pre-migration list (Ace), "Unlike earlier phrasing" sentence (Vera).

**Files changed (summary).**

- 6 role SOPs (data, econometrics, visualization, research, appdev, qa) — ~117 fixes applied across all six.
- 5 schemas updated: `final_exam_results.schema.json` (1.0.0 → 1.0.1 with `minimum_confirmation_n_obs`), `history_zoom_events_registry.json` + schema (1.0.0 → 1.1.0 with `indicator_category_map` and `china_2015`), `color_palette_registry.json` (1.1.0 → 1.2.0 with `matplotlib_legacy` exception palette), `episode_registry.json` (converted to thin pointer per LA-1).
- `scripts/cloud_verify.py` — significant additions (~366 lines): `gate_hze1_preflight`, `gate_sd1_preflight`, `_gate_nr_check`, `check_evidence_status_promotion`, level-1/2 tab structure check, GATE-DP1 abort enforcement, `gate27_png_warnings` → `gate27_png_failures` rename, RECESSION_SLUGS canonicalization.
- `docs/standards.md` — 44 new rule rows registered + ECON-H5 v1.0.0→v1.1.0 + META-AM Ray exemption.
- `docs/agent-sops/team-coordination.md` — META-SBP section authored.

**Process meta-event.** First time the team executed a structured 6-phase SOP review with parallel agent dispatch in each agent-side phase. Outcome validates the pattern for future SOP-hardening waves: ~90 + 133 = 223 distinct findings surfaced and triaged in roughly 6 sequential agent-wave cycles. SOP-first remediation principle held — no product/artifact remediation in scope.

---

## 2026-05-08 — SOP Cross-Review Reconciliation

**Trigger.** Cross-review of the SOP-first remediation patch found protocol
drift between role SOPs, standards registration, and Lead ownership rules.

**Rules updated:**

- **APP-DIR1** (`standards.md`): registered reader-safe direction-mismatch
  language and canonical direction enum use.
- **VIZ-CP1** (`standards.md`): corrected the duplicate/stale standards entry
  so VIZ-CP1 refers to cross-period chart consistency; palette authority remains
  VIZ-V11.
- **META-AL / META-ZI** (`standards.md`, `team-coordination.md`): removed stale
  future-scheduled wording and confirmed the current pair-specific zoom-chart
  contract.
- **GATE-28 / GATE-29** (`team-coordination.md`): aligned the team checklist
  with current delivered-page scope and clean-checkout scope.
- **LEAD-DL1 ownership map** (`lead-agent-sop.md`): recorded the narrow
  APP-TL1 split where Ray owns narrative constants currently stored in Ace's
  `page_templates.py`, while Ace owns template mechanics.

---

## 2026-05-07 — Four-Page Dashboard Consistency Gate

**Trigger.** User asked whether the SOPs explicitly check that a pair's four
standard dashboard pages tell a consistent story. Existing rules covered
direction triangulation, chart-text coherence, and rerun regression, but not
same-dashboard narrative consistency across Story, Evidence, Strategy, and
Methodology.

**Rule added:**

- **META-DASH1** (`team-coordination.md`): canonical four-page consistency
  checklist covering thesis, direction/sign, evidence status, key metrics,
  caveats/confidence, terminology, signal/strategy identity, and action
  language.

**Role hooks added:**

- Ray owns author-side narrative consistency.
- Ace owns rendered label/status/navigation consistency.
- Quincy independently verifies four-page DOM/read-through consistency.
- Lead routes unresolved cross-role conflicts to role owners.

---

## 2026-05-07 — SOP-First Remediation + Token Discipline

**Trigger.** Review of current implemented pairs found product, methodology,
manifest, chart, language, and QA issues. User set the remediation principle:
fix the rule system first, cross-review it, let Lead check global coherence and
token efficiency, then update products/artifacts under the updated SOPs.

**Rules updated/added:**

- **META-NMF** (`team-coordination.md`): expanded from "No Manual Fix" into the
  9-step SOP-first remediation protocol. Findings are classified as SOP
  missing, SOP unclear, SOP present but unenforced, or execution failure under
  an existing rule. Role owners fix their SOPs first; cross-review and Lead
  global/token-efficiency review precede artifact remediation.
- **META-TD1** (`team-coordination.md`): token-efficient communication rule.
  Agents skip filler affirmations, ceremonial openings, repeated prompt
  restatements, and duplicated rule prose; reports focus on decisions,
  evidence, blockers, and next actions.
- **LEAD-SOP1** (`lead-agent-sop.md`): Lead owns SOP mapping, global-picture
  review, return of global issues to role owners, final review, and
  token-efficiency review before artifact work.
- All role SOPs now cross-reference META-NMF and META-TD1 with one compact
  ownership rule.

---

## 2026-05-01 — APP-DIR1 ELI5 Copy Gate

**Trigger.** The Strategy DOM showed an accurate but cryptic engineering
diagnostic: "Ray leg: no narrative file found (RES-17 stub expected)". Evan and
Dana agreed on direction, so the page was usable, but the visible explanation
leaked agent/ticket/file language to readers.

**Rule updated:**

- **GATE-CL1** (`appdev-agent-sop.md`): user-facing APP-DIR1 gaps must explain
  the state in reader language. If the optional story cross-check is absent,
  the page says that plainly and does not mention Ray, RES IDs, stubs, or file
  paths.
- **GATE-28 / HABIT-QA1** (`qa-agent-sop.md`): cloud DOM review and
  `scripts/cloud_verify.py` now treat "Ray leg", "RES-17", "stub expected", and
  "no narrative file found" as internal diagnostic leaks.

**Retro-test.** `app/_smoke_tests/smoke_schema_consumers.py` now renders the
APP-DIR1 caption with a Streamlit stub and fails if those internal tokens appear
in user-facing text.

---

## 2026-05-01 — Final-Exam Confirmation Contract

**Trigger.** After APP-LP8 made search-grade evidence visible, Lead dispatched one
Evan and one Quincy, each with mandatory SOD/EOD, to define the next layer:
what it takes to move a pair beyond `found_in_search`.

**Rules added:**

- **ECON-FE1 Final-Exam Confirmation Contract** (`econometrics-agent-sop.md`):
  Evan may recommend `passed_final_exam` only after a frozen-rule confirmation
  passes sample separation, target-class Sharpe floor, positive after-cost
  excess return, delta-Sharpe, drawdown tolerance, block-bootstrap uncertainty,
  multiple-testing/luck adjustment, machine-readable artifact validation, and
  Quincy replay.
- **GATE-ES1 Evidence-Status Promotion Verification** (`qa-agent-sop.md`):
  Quincy independently blocks any promotion above `found_in_search` unless
  `evidence_status.json` and the referenced final-exam evidence validate,
  anti-gaming checks pass, reproducibility evidence exists, and landing/Strategy
  DOM copy matches the artifact status.

**Schemas added/changed.**

- `docs/schemas/evidence_status.schema.json` bumped to v1.1.0 with optional
  `final_exam` lineage block. `passed_final_exam` now requires confirmation
  fields plus `final_exam.qa_status = "qa_passed"`.
- `docs/schemas/final_exam_results.schema.json` added for the detailed
  confirmation metric artifact.

No pair status was upgraded in this wave.

---

## 2026-05-01 — BL-ELI5-EVIDENCE-STATUS First Land

**Trigger.** The 2026-04-30 review concluded current tournament winners are discovery-grade unless they have a post-selection confirmation test. The portal needed to say that plainly instead of letting Sharpe cards imply confirmed prediction.

**Rule added:**

- **APP-LP8 Evidence-Status Honesty Label** (`appdev-agent-sop.md` Landing Page 8): landing cards and Strategy-page Tournament Winner sections show an evidence-status label. Optional artifact: `results/{pair_id}/evidence_status.json`, schema `docs/schemas/evidence_status.schema.json`. Missing artifact defaults to `found_in_search` / **Best rule found in the search**. Schema-invalid artifacts degrade to the same conservative default with APP-SEV1 L2 warning.

**Implementation first land.** Added reusable loader/render helper in `app/components/evidence_status.py`, landing-card badge/caption, Strategy-page status note, schema, and example. No pair artifacts or pipeline reruns required.

---

## 2026-04-23 — Wave 10I.C Closure: Quality Gate Overhaul + 6 New SOP Rules

**Final verify (commit `0cedde6`):** 41/41 PASS. 10 visible-error failure classes eliminated. Quality gate rebuilt from structural-marker checking to adversarial DOM content inspection.

**New rules — binding immediately:**

- **HABIT-QA1** (Quincy / `qa-agent-sop.md`): After every cloud verify run, Quincy reads ≥3 Strategy-page DOM text files and writes one-sentence sign-off in session-notes. Script PASS is necessary but not sufficient for wave closure.
- **ECON-UD blocking** (Evan / `econometrics-agent-sop.md`): `signal_scope.json` is now a blocking required artifact for ALL pairs, not reference pairs only. Prior "strongly recommended" classification caused 6 Methodology pages to show unavailability banners.
- **ECON-DIR1** (Evan / `econometrics-agent-sop.md`): Before handoff, reconcile `observed_direction` in `interpretation_metadata.json` against `winner_summary.json.direction`. Include economic interpretation of threshold orientation — a positive OLS coefficient does not imply procyclical if the strategy threshold inverts the direction.
- **RES-OD1** (Ray / `research-agent-sop.md`): After any write to `interpretation_metadata.json`, assert `observed_direction == winner_summary.direction` before committing. "Preserve verbatim" is not safe for derived assertions.
- **GATE-CL1-5** (Ace / `appdev-agent-sop.md`): Pre-handoff content audit — check for N/A KPI slots, stub text, sidebar count, label map completeness, and scaling logic correctness before filing handoff.
- **Pattern 24** (Quincy / `qa-agent-sop.md`): When cloud traceback line-number disagrees with HEAD source at that line, suspect stale Cloud deploy — escalate for manual reboot before further code patches.

**Verify script upgrades (Quincy `0c2b92a`):** `APP_SEV1_PATS` for soft-error banners, `STUB_PATS` for placeholder text, `gate29_parquet_preflight()` pre-browser check, screenshot-all-tabs workflow with shared `index.md` evidence package.

**What agents need to know going forward:**
- Every agent must verify their own output renders correctly before handoff — not just that artifacts exist or smoke passes.
- The screenshot evidence package (Quincy's `index.md`) is the shared inspection surface. Each agent inspects their own domain pages from it.
- `signals_*.parquet` is a deploy-required artifact for every pair that shows a Strategy page. ECON-DS2 (Evan) and GATE-29 (Quincy) both enforce this.

---

## 2026-04-23 — Wave 10I.A Closure: Legacy Migration + Schema-Drift Backfill Shipped + Pattern 24 Codified

**Final cloud verify (commit `e11dc20`):** 41/41 PASS. 6 legacy hand-written pages (`indpro_spy`, `permit_spy`, `vix_vix3m_spy`, `sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`) migrated onto APP-PT1 template. Three layered schema-drift defects resolved: `winner_summary.json` v1.1.0 backfill (Evan `a5952e2`), `interpretation_metadata.json` v1.0.0 backfill (Ray `8fc4270`), consumer defensive coerce (Ace `5f2e50d` + `ccb0d5f`, activated by Lead's Cloud reboot after reverify #2 diagnosed staleness).

**Pattern 24 codified** (pending write into `qa-agent-sop.md`): *when cloud traceback line-number disagrees with HEAD source at that line (e.g., traceback points at a line that is a comment at HEAD), suspect stale Cloud deploy before further code patches — escalate to Lead for manual reboot.* Direct analog of Pattern 22/23 but for deploy-layer staleness rather than DOM-traversal artifacts.

**Schema version bumps shipped:**
- `docs/schemas/winner_summary.schema.json` 1.0.0 → 1.1.0 (`threshold_value` null-tolerant). 6 legacy pairs backfilled to v1.1.0 shape.
- `docs/schemas/interpretation_metadata.schema.json` — no schema change; 6 legacy pairs backfilled to v1.0.0 shape.

**What agents need to know going forward:**
- Any future legacy-page migration MUST run strict `jsonschema.validate` against ALL pair artifacts (not just `winner_summary.json`) before cloud verify. Producer-side drift beyond the one visible consumer path is the norm, not the exception, for pre-template pairs. Tracked as proposed `BL-LEGACY-MIGRATION-AUDIT-GATE`.
- Artifact-only commits (results/*.json) may not trigger Streamlit Cloud auto-redeploy. When a code fix landed but verify shows the pre-fix behavior, diff the cloud traceback line number against HEAD before dispatching more code patches.
- Consumer-side defensive coerce (APP-SEV1 L2) is only effective when reachable. If an upstream `validate_or_die` gate fails first, the downstream coerce is dead code for that pair. Fix the producer, not the consumer, in that class.

**Git tag:** `wave-10i-a-complete` recommended at `e11dc20`.

---

## 2026-04-23 — Wave 10I: APP-PR1 Path Resolution Discipline

**Trigger.** Opening a hygiene wave (Cluster A from backlog review) to address the central silent-regression class: legacy hand-written pages that bypass `render_*_page()` templates. Before beginning the legacy-page migration (BL-APP-PT1-LEGACY + BL-APP-PT1-UMCSENT + Sample Strategy decommission), codify APP-PR1 so all migrated pages ship compliant with the path-resolution discipline from day one.

**Rule added:**

- **`docs/agent-sops/appdev-agent-sop.md` — APP-PR1 Path Resolution Discipline.** Binding: every file read under `app/components/**` and `app/pages/**` targeting a project-relative path MUST resolve via `_REPO_ROOT = Path(__file__).resolve().parents[N]`. Bare relatives (`Path("results") / ...`, `open("results/...")`, `pd.read_csv("results/...")`) are prohibited. Pairs with APP-SEV1: resolved-but-unparseable required artifacts surface as L2 warnings with the resolved absolute path; silent skip permitted ONLY for optional artifacts whose path does not exist. Grep-checkable CI pattern provided for future enforcement. Ace's Wave 10H.1 audit of `page_templates.py` already showed zero bare-relative instances; rule is prophylactic and becomes mandatory for the legacy-page migration work.

**Closes backlog item:** `BL-APP-PR1` (proposed by Ace in Wave 10H.1 follow-up handoff).

**What agents need to know going forward.** Any new `app/` helper that reads a project artifact must use `_REPO_ROOT`. Any migration of a legacy hand-written page to a thin template wrapper (Wave 10I scope) must audit for bare-relative reads as part of the migration.

---

## 2026-04-23 — Wave 10H.2 Closure: APP-TL1 Shipped + Pattern 23 Codified

**Final cloud verify (commit `8e743ce`):** 17/17 PASS. APP-TL1 retro-applied to `hy_ig_spy` and `indpro_xlp`. Regression gate holds for Sample (legacy page) and umcsent_xlv (tracked as BL-APP-PT1-UMCSENT).

**Pattern 23 codified** in `qa-agent-sop.md` §Cloud Visual Smoke item 4: `frame.inner_text("body")` does NOT traverse hidden `st.tabs` panel content — only the active tab's text is returned. Fix: use `frame.content()` HTML for tab-gated markers; retain `inner_text` for unconditionally-visible surfaces. Direct analog of Pattern 22.

**What agents need to know going forward:**
- Every pair added from Wave 10H.2 onward ships APP-TL1-compliant Strategy page via the template, with `TRADE_LOG_EXAMPLE_MD` as a required pair-config narrative anchor.
- Sample legacy Strategy page decommission tracked as follow-on (sibling to BL-APP-PT1-LEGACY).
- QA verify scripts: for Strategy-page markers (and any marker inside `st.tabs`), use `frame.content()` not `frame.inner_text()`.

**Git tag:** `wave-10h2-complete` pinned at `8e743ce`.

---

## 2026-04-23 — Wave 10H.2: APP-TL1 Trade Log Rendering Contract

**Trigger.** User surfaced a regression after Wave 10H.1 shipped: the newly-rebuilt `hy_ig_spy` (on APP-PT1 template) has a "Download Trading History" section less rich than Sample (`hy_ig_v2_spy`, hand-written legacy). Sample has dual downloads (broker-style + researcher position log), multi-paragraph narrative scaffold, column glossary, concrete example, always-visible preview. Template has a single generic `st.download_button` with no prose. Every template-based pair inherited the regressed view. Direct mirror of `BL-APP-PT1-LEGACY`: reference richer than template.

**Discovery dispatch (Ace, commit `3d6f096`):** full delta report at `results/_cross_agent/ace_discovery_trade_log_20260423.md`. Blast radius: 3 template-based pairs (`hy_ig_spy` — pure renderer gap; `indpro_xlp`, `umcsent_xlv` — renderer + data gap, broker-style CSV missing). Sample itself retains richer legacy page.

**Rule added:**

- **`docs/agent-sops/appdev-agent-sop.md` — APP-TL1 Trade Log Rendering Contract.** Binding: `render_strategy_page()` MUST invoke `_render_trade_log_block(pair_id, config)` helper producing the full Trading History block — dual CSV artifacts (`winner_trades_broker_style.csv` primary + `winner_trade_log.csv` secondary), fixed 5-element narrative scaffold (heading, simulated-vs-real disclosure, two-file model, column glossary, pair-specific example), column-dictionary expander, two-column download layout (primary broker + secondary researcher), always-visible 10-row preview with captions. APP-SEV1 alignment: both missing = L1 short-circuit; one missing = L2 degraded render; malformed = L2 warning + healthy-pane render; missing pair-specific example = L3 caption coda. Ownership: Ace (structure), Ray (narrative defaults + pair example via `TRADE_LOG_EXAMPLE_MD` config anchor), Evan (broker-style CSV production), Dana (schema), Quincy (QA gate). Migration: 6-step protocol; first land scope = 3 template pairs + template upgrade + narrative canon + data backfill + QA verify. Sample decommission + legacy-pair audit deferred as follow-ons.

**What changes for agents going forward.** Every new pair from Wave 10H.2 onward ships with APP-TL1-compliant Strategy page by default via the template. Existing template-based pairs (`hy_ig_spy`, `indpro_xlp`, `umcsent_xlv`) retro-apply in this wave. Pair configs gain `TRADE_LOG_EXAMPLE_MD` as a required narrative anchor.

**Open scope (retro-apply, dispatched Wave 10H.2):** Ace template structure + Ray narrative + Evan data + Quincy verify.

---

## 2026-04-23 — Wave 10H.1 Closure: Chart Governance Framework Shipped End-to-End

**Scope.** No new rules this entry — this records the implementation closure of the rules shipped in Wave 10H (paper SOPs) and Wave 10H.0 (Lead discipline). Purpose: tell future agents the framework is now live.

**Final cloud verify (commit `aca5602`):** 17/17 PASS on all active pairs × 4 pages + landing.

**What agents need to know going forward:**

1. **VIZ-O1 disposition** is now enforced — every `*_meta.json` sidecar in `output/charts/*/plotly/` must carry `disposition: "consumed" | "suggested" | "retired"`. Quincy's `scripts/cloud_verify.py` audits this on active pairs; GATE-28 scope now includes it. Vera writes the field at production time on 3 of 7 pair generators; the other 4 are flagged as `BL-VIZ-SIDECAR-HELPER` for a hygiene wave.

2. **VIZ-E1 exploration zone** is now routable — Vera's `exploratory_charts` entries in `results/{pair_id}/analyst_suggestions.json` auto-render on the Methodology page (for pair pages that use the template). Each entry carries ELI5 `narrative_alignment_note` (blocking requirement) + `vera_rationale`. Feedback loop: users see the section, tell the team which to promote.

3. **APP-PT2 Methodology Exploratory Insights** is live on Sample pair. For pairs using `render_methodology_page()` it is automatic. For the 5 legacy Methodology pages that bypass the template (`BL-APP-PT1-LEGACY`), the helper must be called directly from the page file until migration. This is a silent-regression risk class — agent briefs for any Methodology-page rule addition MUST explicitly list bypass pages requiring defensive direct calls.

4. **Pattern 22 fix** is now canonical — use `query_selector_all(".js-plotly-plot")` on the DOM tree, never `inner_text.count("js-plotly-plot")`. Playwright `page.frames` iteration races Streamlit frame registration; use `wait_for_selector('iframe[title="streamlitApp"]').content_frame()` instead. Codified in qa-agent-sop.md.

5. **LEAD-DL1 is validated in practice.** Wave 10H.1 end-to-end: 3 agent dispatches (Ace, Vera, Quincy) + 1 follow-up Ace dispatch + 1 Quincy re-verify dispatch, zero Lead commits touching agent-owned files post the initial revert. Lead commits in the wave touch only `docs/` + `.claude/settings.json` (infrastructure). Self-audit at closure: `git log --author='Lead' --since='Wave 10H start' --name-only` confirms compliance.

6. **Permissions syntax (infrastructure).** `settings.json` entries targeting absolute paths must use double-slash prefix (`Write(//home/vscode/.claude/agents/**)`). Single-slash is project-relative per Claude Code docs. Fix `b3facc8` validated twice — global-profile writes succeed without prompt on current subagent dispatches.

**Open backlog (Wave 10H.2/10I candidates):** `BL-VIZ-O1-LEGACY` (35 legacy-pair sidecars), `BL-VIZ-SIDECAR-HELPER` (4 generator refactors), `BL-APP-PR1` (path resolution discipline), `BL-APP-PT1-LEGACY` (5-Methodology-page template migration). All bundleable into one hygiene wave.

**Git tag.** `wave-10h1-complete` pinned at `aca5602`.

---

## 2026-04-22 — Wave 10H.0: Lead Delegation Discipline (LEAD-DL1)

**Scope:** Lead agent only. Affects every future wave's execution-vs-authorship boundary.

**Trigger.** During Wave 10H.1 planning I accepted a user ask to "proceed as suggested" and then implemented the framework myself — Ace's template helper, Vera's sidecar backfill + ELI5 exploratory-chart authoring, Quincy's Pattern 22 script fix — 70+ files under Lead identity. User reverted it: *"Drilling into execution often blurs your vision into the bigger picture. Please find a way to maintain this discipline so that you grow into a genuine leader."*

**Rule added (new Lead SOP):**

- **`docs/agent-sops/lead-agent-sop.md` (new file) — LEAD-DL1 Delegation Discipline.** Binding: Lead never writes to files owned by role agents. Lead-owned write categories are explicitly enumerated (SOPs, coordination docs, meta docs, `_pws/_team/`, `_pws/lead-lesandro/`, git tags). Everything else → dispatch. Pre-edit gate, narrow exceptions (emergency / user override / self-revert), File Ownership Map covering all 6 agents + shared-key files (analyst_suggestions.json, pair_config.py), self-audit protocol at wave closure (`git diff --stat` against Ownership Map).

**Memory trigger added:**

- `memory/lead_delegation_discipline.md` — loaded at every SOD via `MEMORY.md` index.

**What this changes going forward.** Every Lead action that would touch a file now runs the pre-edit gate: *who owns this file?* If not Lead → stop and dispatch. Wave closures include a Lead-commit self-audit step. Any drift surfaces as a "Lessons" entry in relnotes and a PWS escalation.

---

## 2026-04-22 — Wave 10H: Chart Governance + Exploration Framework

**Scope:** visualization agent (VIZ-O1, VIZ-E1), app dev agent (APP-PT2), QA agent (Pattern 22 fix, QA-CL2 P2 exception). Affects Vera, Ace, and Quincy. Lead-authored.

**Rules added:**

- **VIZ-O1 — Chart Disposition Mandate (`visualization-agent-sop.md`):** Every chart Vera produces must receive one of three dispositions before handoff: `consumed` (page template references it), `suggested` (routes to Methodology Exploratory Insights section per APP-PT2), or `retired` (logged with reason, not shipped). Disposition is recorded in the chart's `_meta.json` sidecar. Missing or blank disposition is a GATE-28 failure. Closes the chart evaporation gap exposed by the 3 orphaned Sample charts.

- **VIZ-E1 — Exploration Zone + Sidecar Spec (`visualization-agent-sop.md`):** Vera is not confined to the core chart set. Every pair_config has a Core zone (mandatory named slots) and an Exploration zone (open — Vera produces any chart she judges analytically valuable). Exploratory charts get `"exploratory": true, "disposition": "suggested"` in their `_meta.json` sidecar. Mandatory sidecar fields: `narrative_alignment_note` (ELI5 plain-English explanation, **no jargon**, displayed verbatim on Methodology page), `vera_rationale` (one-line analyst note, italicized below ELI5 caption). The ELI5 field is a blocking handoff requirement for exploratory charts.

- **APP-PT2 — Methodology Page Exploratory Insights Section (`appdev-agent-sop.md`):** `render_methodology_page()` must render an "Exploratory Insights" section at page bottom when `results/{pair_id}/analyst_suggestions.json` has ≥1 entry under `"exploratory_charts"`. Section renders: section heading → `st.info` callout (non-quant framing + feedback invitation) → for each chart: rendered chart + ELI5 caption (`st.caption`) + Vera's rationale (italic) + feedback prompt. Non-blocking default: charts ship automatically without editorial gate. Promotion to core template slot happens at wave closure. Backward-compatible: older pairs with no `exploratory_charts` key render Methodology page identically.

- **Pattern 22 fix — QA cloud verify (`qa-agent-sop.md`):** DOM chart detection via `.count("js-plotly-plot")` on `page.inner_text()` always returns 0 — CSS class names are not included in extracted text. Correct approach: `page.query_selector_all(".js-plotly-plot")` on the DOM tree, or text-marker heuristics (axis labels, date strings). False-negative trap removed from cloud verify protocol.

- **QA-CL2 P2 exception (`qa-agent-sop.md`):** Triangulation 3 (annual turnover ↔ trade count ↔ horizon) is not applicable to P2 continuous-rebalancing strategies (`position_sizing = "proportional"` or `"signal_strength"`). For these strategies, `annual_turnover` is portfolio-change-weighted and `oos_n_trades` counts daily rebalances — incommensurate quantities. Quincy skips T3 and records "N/A — P2 continuous rebalancing" in findings. Schema gap (no `turnover_basis` enum) tracked in backlog BL-802.

---

## 2026-04-22 — Wave 10G: Sample Ratification + Archive + New HY-IG × SPY

**Scope:** sample governance, namespace management, template extensions, full pair pipeline. Affects ALL agents for discoverability; Lead owns ratification, dispatches agents for new pair build.

**Sub-phases committed so far:**

- **Wave 10G.1 (commit `02251bd`):** v1 `hy_ig_spy` archived to `_v1` suffix. All artifacts moved via `git mv` (history preserved): `results/`, `data/`, `scripts/`, `docs/`, `app/pages/`. `app/pages_archive/` created (Streamlit does not auto-scan). `app/components/pair_registry.py` hardcoded v1 block removed; auto-discovery loop now skips any directory ending in `_v1` or `_archived`. Legacy flat-layout conditionals in `execution_panel.py` and `generate_winner_outputs.py` remapped from `pair_id == "hy_ig_spy"` to `pair_id == "hy_ig_spy_v1"` to isolate legacy logic and prevent false-matching the fresh `hy_ig_spy` pair created in Wave 10G.4.

- **Wave 10G.2:** `hy_ig_v2_spy` ratified as the **Sample / canonical reference pair**. Git tag `sample-v1.0`. `pair_registry.py` now flags it with `is_sample=True` and renders a blue SAMPLE badge on its landing-page card. Every future pair is quality-compared against Sample (feature set: probability engine, position adjustment, trigger cards, 3-way direction check, 8-element Evidence, historical zoom charts, etc.). Sample pair_id and on-disk paths unchanged — display-layer rename only.

**Planned sub-phases (to be completed in this session or next wave):**

- **Wave 10G.3 (DONE — 2026-04-22):** extended `app/components/page_templates.py` with two optional config fields: `HISTORY_ZOOM_EPISODES` (list of crisis-episode dicts on Story page, renders "How the Signal Performed in Past Crises" section with per-episode chart via `load_plotly_chart`, APP-SEV1 L2 on missing artifact) and `regime_context` (optional markdown string on Evidence method block dict, renders `st.info(...)` callout between theory and chart). Both additive/optional — existing pairs render identically. APP-PT1 supplement added to `appdev-agent-sop.md`. smoke_loader: indpro_xlp 8/0, umcsent_xlv 7/0, hy_ig_v2_spy 15/0.

- **Wave 10G.4A–F:** full 5-agent pipeline (Dana → Ray → Evan → Vera → Ace → Quincy) to build a fresh `hy_ig_spy` pair using the latest SOPs + extended templates. Targets Sample-quality feature parity via template (no hand-coded pages).

- **Wave 10G.5 (COMPLETE — 2026-04-22):** cloud verify exposed two class-of-duplication bugs + one raw-column-leak content bug. All resolved:
  - `_page_prefix()` duplicate routing dict in page_templates.py → APP-RL1 added + merged to pair_registry (`35bb008`).
  - Missing `hy_ig_spy` entry in `indicator_names` → fixed same commit.
  - `interpretation_metadata.key_finding` leaked column identifiers (`hy_ig_spread_pct`, `spy_fwd_63d`) → DATA-D6b added, Dana rewrote to human-readable (`3c37d96`).
  - Final cloud verify (`bd3wvyjep`): landing PASS, all 4 hy_ig_spy pages zero-traceback / breadcrumb-present / no-prefix-pending.
  - **Pattern 22 (new):** DOM chart detection via `.count("js-plotly-plot")` on `inner_text` always returns 0 — CSS class names don't appear in extracted text. Use text markers (axis labels, month-year patterns, chart titles) or query the DOM structure via `query_selector_all`.
- **Wave 10G.5 (IN PROGRESS — 2026-04-22):** cloud verify exposed two class-of-duplication bugs:
  - `_page_prefix()` in `page_templates.py` had a duplicate routing dict that Ace missed when adding `hy_ig_spy` to `pair_registry.py`'s routing dict → `StreamlitPageNotFoundError` on Story + Evidence pages.
  - `indicator_names` dict in `pair_registry.py` missing `hy_ig_spy` entry → landing-page card displayed the raw column identifier `"hy_ig_spread_pct"` instead of a human label.
  **SOP additions in response:**
  - **APP-RL1 (appdev-agent-sop.md, ace):** single-source routing / label maps — no duplicate dicts across modules. Detection grep + canonical-location list. Pattern 14 sibling.
  - **GATE-28 scope extension (qa-agent-sop.md, quincy):** cloud verify now covers ALL active pairs × ALL 4 pages with zero-Python-error requirement. Partial pass → wave does not close. Rationale: the Wave 10G incident where a fix for one page didn't re-verify the others.

## 2026-04-20 — Wave 10F: Standardization Infrastructure (Lead)

**Scope:** team-coordination.md + new project-local /sod + new hooks + new team-standards.md. Affects ALL agents.

**Additions:**

- **META-RYW (team-coordination.md, ALL agents)** — **Read Your Own Work before handoff.** Every producer re-reads their deliverable end-to-end (prose word-by-word, each chart matched against its description, each numeric claim against its source, each instrument/date/direction word against interpretation_metadata.json) and logs the re-read in the handoff note. Closes the class of bug where agents ship artifacts without looking at them (Wave 10E "S&P 500 on XLP page" was the proximate trigger).
- **VIZ-IC1 (visualization-agent-sop.md, vera)** — **Pre-save intra-chart consistency check.** Before saving any chart JSON, Vera asserts: title↔axes coherence; legend↔data series match; annotations↔data range match; palette registry conformance (role-based aliases); unit discipline in tick formatters; narrative-alignment note in chart _meta.json sidecar.
- **Project-local `/sod` (new `.claude/commands/sod.md`, ALL agents)** — project override of the global `/sod` skill. Defines the 7-step SOD procedure for this project: identity → global profile → PWS → core project docs + team-standards.md → sop-changelog.md since last_seen → team status → acknowledge. Updates `last_seen` at end.
- **SOD / EOD hooks moved into repo (`scripts/hooks/`)** — `check-agent-sod.sh` (new PreToolUse) + `check-agent-eod.sh` (moved from ~/.claude/hooks). `.claude/settings.json` uses repo-relative paths. Portable across clones; single source of truth.
- **Mandatory Dispatch Template extended** — every dispatch prompt must now contain `## SOD Block` in addition to the existing `AGENT_ID:` line and `## MANDATORY EOD` block. PreToolUse hook warns if SOD block absent.
- **`docs/team-standards.md` (stub)** — new canonical cross-agent conventions file (directory layout, filename conventions, sidecar schema, palette roles, handoff contracts, deploy-required artifact registry, dispatch template). Sections marked `[TO BE POPULATED BY CROSS-REVIEW]` are held for the next wave's parallel agent audit.

**Commit:** `90cadd4` (infrastructure portions); this changelog update is part of the same wave.

---

## 2026-04-20 — Wave 10E: Template Abstraction + Narrative Accuracy + ECON-DS2 Gap (Multi-agent)

**Scope:** appdev-agent-sop.md + research-agent-sop.md + qa-agent-sop.md + econometrics-agent-sop.md + team-coordination.md. Affects ALL agents.

**Additions:**

- **APP-PT1 (ace)** — **Page Template Abstraction.** New pair portal pages MUST be thin wrappers calling `app/components/page_templates.py`. Pair-specific content lives in `app/pair_configs/{pair_id}_config.py`. Any `st.*` call in a page file (other than the template call) is a gate failure. Eliminates copy-paste drift across pairs.
- **APP-PT1 supplement (ace + ray)** — **Narrative authorship.** Narrative prose in `pair_configs/` MUST be authored by Ray, not Ace. Ace renders structure only; narrative fields are explicit placeholders until Ray delivers. Prevents the Wave-10E "wrong instrument in narrative" class of bug.
- **APP-SS1 (ace)** — **signal_scope.json consumer contract.** Methodology page readers MUST use the `indicator_axis.derivatives` / `target_axis.derivatives` schema, not the legacy `in_scope.*` flat arrays. Empty Signal Universe columns = L1 st.error + short-circuit.
- **RES-NR1 (ray)** — **Narrative instrument reference accuracy.** All instrument names in narrative prose must match `interpretation_metadata.json.target_symbol`. Log RES-NR1 check in handoff. Ray owns all narrative prose for a pair (no copy-paste from other pairs without pair-specific re-authoring).
- **GATE-NR / QA-CL5 (quincy)** — **Narrative instrument reference check.** DOM scan of Story/Evidence pages for wrong-pair instrument names. Blocking at GATE-31.
- **META-NMF (team-coordination.md, ALL)** — **No Manual Fix (inviolable).** Every fix flows through SOP update first, then agent dispatch. Lead included. No ad-hoc shortcuts.
- **ECON-DS2 explicit quality gate (evan)** — `git ls-files results/{pair_id}/signals_*.parquet` must return ≥1 file before handoff. Rule existed in prose; now a named checklist item.
- **GATE-29 parquet check (quincy)** — clean-checkout test extended to explicitly verify `signals_*.parquet` is committed. Missing = GATE-29 FAIL even when smoke_loader passes.

**Commits:** `bfb1b70` (APP-PT1), `a9ae669` (RES-NR1/GATE-NR), `dadd8f5` (ECON-DS2 gap), `e1cff0f` (Evan's signals parquet retro-fix).

---

## 2026-04-20 — Wave 10D: Cloud Verify Structural Enforcement (Multi-agent)

**Scope:** appdev-agent-sop.md + qa-agent-sop.md. Affects ace, quincy.

**Additions:**

- **AppDev Quality Gate extensions (ace)** — new checklist items: breadcrumb nav present on all 4 pages; Evidence page tab structure matches reference pair (Level 1 / Level 2); new pages MUST be derived from canonical reference template, not built from scratch; Signal Universe section renders non-empty.
- **GATE-28 structural parity (quincy)** — cloud DOM audit now asserts breadcrumb present (all 4 section labels in DOM) AND Evidence tabs contain "Level 1" or "Basic Analysis" text. Missing/wrong = GATE-28 FAIL.
- **QA-CL4 (quincy)** — named cloud verify gate (GATE-27 + GATE-28 + GATE-29). Previously ad-hoc Lead-owned; now Quincy-owned, evidence-gated.

**Commits:** `eb023f9` (fix + SOP tightening), `a815fde` (final cloud verify PASS).

---

## 2026-04-19 — HY-IG v2 Stakeholder Review Follow-Up: VIZ-V2 Revision + VIZ-V5 Added (Vera)

**Scope:** visualization-agent-sop.md + docs/standards.md. No other agent SOPs touched.

**Bug observed:** HY-IG v2 stakeholder review flagged two bugs the existing SOPs failed to prevent. (1) NBER recession shading at grey alpha 0.12 was imperceptible against the Streamlit off-white background; caption correctly disclosed shading but shading itself was invisible. (2) In the dual-panel hero chart (two x-axes: `xaxis`, `xaxis2`), the 3 shading rects had `xref='x'` only, so the bottom SPY panel had no shading at all. Both bugs cleared prior Quality Gates because the rule as written was wrong, not because it was unfollowed.

**Revised (VIZ-V2):**

- **Alpha + color prescription corrected.** Prior text "alpha 0.1–0.15, grey" replaced with "alpha 0.20–0.28, `rgba(150,120,120,0.22)` faded red-brown or equivalent — must be perceptible against the Streamlit background at standard zoom. Plain grey at alpha < 0.18 is prohibited."
- **Subplot handling clause added.** When `layout` contains multiple x-axes (`xaxis`, `xaxis2`, …), Vera must emit one shading shape per panel per recession; total shape count = n_recessions × n_panels.
- **Perceptual-validation step added.** After saving JSON, Vera renders chart to PNG via kaleido (`fig.write_image`) and visually confirms shading is perceptible. PNG saved as `_perceptual_check_{chart}.png` in the same plotly directory. Charts where shading cannot be seen at standard zoom fail **GATE-27 (End-to-End Chart Render Test)**.

**Added (VIZ-V5):**

- **End-to-End Chart Load Smoke Test.** Before handoff to Ace, Vera runs a smoke-test script per chart: (1) `plotly.io.read_json` loads without exception, (2) `len(fig.data) > 0`, (3) `fig.layout.title.text` non-empty. Log saved to `output/charts/{pair_id}/plotly/_smoke_test_{YYYYMMDD}.log`. Any failure blocks handoff.

**Retro-applied to HY-IG v2:** 4 charts updated (hero dual-panel → 6 shading shapes; 3 canonical zoom charts → stronger faded-red-brown alpha). Perceptual check PNGs and smoke test log produced per the new rule. Change recorded in `results/hy_ig_v2_spy/regression_note_20260419.md`.

**Rationale:** "Rule was followed; rule was wrong. Fix the rule." Both bugs were 100% preventable had VIZ-V2 carried (a) a perceptible alpha, (b) a subplot clause, and (c) a perceptual-validation step. V5 smoke test catches the orthogonal structural-integrity failure mode. Operationalizes the learning that quality gates must include a rendered-output check, not only spec-conformance checks.

---

## 2026-04-12 — Regression-Proofing Infrastructure (this session)

**Scope:** team-coordination.md + new docs/standards.md + new docs/sop-changelog.md. No changes to agent-specific SOPs.

**Added to team-coordination.md:**

- **META-PWQ / Portal-Wide Quality Checklist** — cross-cutting acceptance checklist applied to every pair. Covers Landing Page, Navigation, Story, Evidence, Strategy, Methodology pages, and cross-cutting items (dual notation, plain-English expanders, honest caveats, no silent regressions).
- **META-RPD / Reference Pair Doctrine** — HY-IG v2 (tag: hy-ig-v2-reference once approved) established as canonical reference pair. Every new pair dispatch begins with comparison; deviations require design_note.md.
- **META-PAC / Pair Acceptance Checklist** — new template for results/<pair_id>/acceptance.md with Portal-Wide Quality Checklist, Reference Pair Comparison, Regression Note, Stakeholder Review, Lead Sign-off sections.
- **GATE-23** — new gate row for Pair Acceptance.md (blocking); owner Lead Lesandro.

**Created:**

- **docs/standards.md** — canonical rule registry with stable IDs for every blocking rule across DATA, ECON, VIZ, RES, APP, GATE, and META prefixes.
- **docs/sop-changelog.md** — this file.

**Rationale:** Regression-proofs the SOP system. Future agent dispatches can cite rules by stable ID (GATE-23, META-RPD, APP-AF2, etc.) rather than quoting SOP prose. The Reference Pair Doctrine and Pair Acceptance Checklist together turn tribal knowledge about pair-quality decisions into mechanical artifacts that reviewers and future agents cannot miss.

---

## 2026-04-11 — EOD Checkpoint (commit 93ed4b2)

**Scope:** EOD checkpoint capturing SOP hardening Parts D+E + trade log UX in a single marker. No new rules, but consolidates the day session work.

**Referenced:**

- SOP hardening Part D (c5bf1a9)
- SOP hardening Part E (62c60e9)
- Trade log UX fix (8ef55c5)
- HY-IG v2 retroactive fixes (b6dd6a9)

---

## 2026-04-11 — Trade Log UX (commit 8ef55c5)

**Scope:** Econometrics + Research + AppDev SOPs.

**Added:**

- **ECON-C4 / Rule C4** — Dual Trade Log Output (Internal + Broker-Style). Winner trade log produced in both internal schema and broker-style CSV for downstream consumers.
- **RES-PA3** — How to Read the Trade Log subsection mandatory on Strategy page narrative.
- **APP-AF5** — Column Legend Requirement for Downloadable Artifacts. Every CSV download must have an adjacent column-legend expander.

**Rationale:** HY-IG (pair #5) shipped a header-only trade log; downstream users had no way to interpret columns. Fix makes the trade log self-describing at three layers: file (broker CSV), portal (expander), narrative (worked example).

---

## 2026-04-11 — HY-IG v2 Retroactive Fixes (commit b6dd6a9)

**Scope:** No new SOP rules. Applied the hardened SOPs retroactively to HY-IG v2 to close stakeholder-reported gaps. Retroactive fixes served as the integration test for the new rule set.

**Validated rules:** GATE-22 (method coverage no regression), RES-EP1 (8-element template), VIZ-A3 (canonical chart catalog), META-RNF (regression note format), APP-EP4 (chart filename contract).

---

## 2026-04-11 — SOP Hardening Part E (commit 62c60e9)

**Scope:** Stakeholder-driven + self-review + cross-review fixes across all SOPs.

**10 stakeholder-driven rules added:**

- **RES-EP1** — Evidence Page 8-Element Template (Why / How / Method / Graph / Observation / Interpretation / Caveats / Link-back).
- **RES-EP2** — chart_status field mandatory in each method block.
- **RES-EP3** — Missing-Element Fallback Protocol (escalate before dropping).
- **RES-EP4** — Drop Only With Regression Note.
- **APP-EP1..EP5** — Render-side rules for 8-element template, caption fallback chain, render-time completeness check, chart filename contract (3.9a), missing-element fallback (3.9b).
- **GATE-22** — Method coverage no-regression gate item.

**15 self-review rules added:**

- **DATA-D3** — Classification Decision Procedure (mandatory workflow).
- **RES-B5** — Strategy Objective Classification.
- **ECON-C3** — Producer-Side Rerun Regression Check (method and numeric diff).
- **VIZ-A4** — Chart Regression Report with Spec Diff section.
- **RES-5b** — Regression Prevention Recipe (filesystem diff).
- plus audience-friendly refinements across AppDev SOP §3.8.

**10 cross-review fixes:**

- META-EOI expanded to cover prior-pair-version deviations and unit/scale conventions.
- META-UNK formalized: unknown classification is an error signal, not a fallback label.
- META-CFO formalized classification field ownership (Dana owns nature/type; Ray owns objective).
- VIZ-A2 + RES-4 cross-referenced for dual-notation consistency.
- GATE-19/20/21 ownership explicitly named on gate rows.

---

## 2026-04-10 — SOP Hardening Part D (commit c5bf1a9)

**Scope:** classification schema, 8-element template intro, landing page filters.

**Added:**

- **DATA-D3 / Classification Decision Procedure (first version)** — mandatory workflow for indicator_nature and indicator_type.
- **DATA-D2 / Default Unit Convention Registry** — canonical units per column suffix; rules for one unit per canonical name.
- **RES-IT1** — Indicator Type Classification in research brief with controlled vocabulary.
- **APP-LP1..LP7** — Landing Page Design Rules (executive summary, multi-dimensional filters, card numbering, performance badges, classification chips, metadata source, filter behavior for Unknown).
- **META-TWJ** — Tournament Winner JSON Schema formalized.

**Rationale:** Portal landing page needed filterable classification. Classification became the linchpin coordinating Dana, Ray, Evan, Vera, Ace.

---

## 2026-04-10 — HY-IG v2 Narrative Rewrite (commit d9aeaff)

**Scope:** No new rules. First full exercise of the audience-friendly rules on an existing pair.

**Validated:** RES-1, RES-2, RES-3, RES-4, APP-AF1..AF5.

---

## 2026-04-09 — Audience-Friendliness Rules (commit 61efe7d)

**Scope:** Research + AppDev SOPs.

**Added:**

- **RES-1** — Audience Assumption (write for layperson who knows markets).
- **RES-2** — Translation Bridge (plain-English on first use).
- **RES-3** — Method Justification (Why we chose this method sentence).
- **RES-4** — Unit Discipline — Inline Dual Notation (bps and percent on first use).
- **RES-6** — Glossary Quality Rubric (4-element standard).
- **APP-AF1** — Expander Philosophy: Defer Do not Expand.
- **APP-AF2** — Rule-First Strategy Cards.
- **APP-AF3** — Metric Interpretation Rule (interpretation caption on every KPI).
- **APP-AF4** — Translation Bridge Rendering.

**Rationale:** Stakeholder feedback that portal was too quant-dense for intended audience. Ray now assumes layperson; Ace renders with progressive disclosure.

---

## 2026-04-09 — Chart Rendering Fix (commit 8767a8a)

**Scope:** AppDev + Visualization contract.

**Added:**

- **APP-EP4 / Chart Filename Contract (Rule 3.9a)** — loader uses canonical filename only; no fallback to alternate filenames.
- **VIZ-NM1** — pair_id appears ONLY in directory path, NEVER in filename.

**Rationale:** Filename mismatch between Vera outputs and Ace loader was the single most common portal bug. Rule removes silent fallback behavior.

---

## 2026-04-08 — HY-IG v2 Full Pipeline Test (commit b009674)

**Scope:** No new rules. Full multi-agent pipeline test of hardened SOPs.

**Validated:** META-PSC (pipeline self-containment), ECON-DS1 (derived signal persistence), RES-EP1 (8-element template), VIZ-A3 (standard chart catalog).

---

## 2026-04-07 — SOP Hardening Core (commit 6cb5b4c)

**Scope:** Team coordination + Econometrics + AppDev + Research SOPs.

**Added:**

- **META-PSC / Pipeline Self-Containment Contract** — every pair has single self-contained pipeline script producing ALL downstream artifacts.
- **ECON-DS1 / Derived Signal Persistence Rule** — HMM probs, Markov states, z-scores, composites persisted to results/{id}/signals_{date}.parquet.
- **APP-RP1** — Rendering Patterns for Presentation Quality (st.container(border=True), no nested HTML, no markdown inside HTML wrappers).
- **RES-PA2** — Presentation Quality Patterns (skeptical reader framing, progressive disclosure, honest caveats).

**Rationale:** HY-IG (pair #5) required 3 separate scripts in specific sequence. HMM probability signal computed inside tournament but never persisted. Fragmented pipelines created invisible dependencies.

---

## 2026-03-20 — Deliverables Completeness Gate (commit a8ca9f6)

**Scope:** team-coordination.md.

**Added:**

- **GATE-1..GATE-18** — Deliverables Completeness Gate Step 8 with 18 gate items across analysis brief, dataset, stationarity, interpretation metadata, exploratory results, core models, tournament, charts, portal pages, navigation, catalog status, winner summary/trade log/execution notes.
- **META-MRA / MRA Mandatory** — Measure, Review, Adjust step after browser verification.
- **META-BV / Browser Verification Mandatory** — Playwright headless inspection after every portal change.
- **META-VF / Variant Families** — sharing pages across variants acceptable; omitting page type not.

**Rationale:** Pair #2 (TED Variants) shipped without Methodology page because no one verified all 4 pages existed. Browser verification checked rendering, not completeness.

---

## 2026-03-14 — Multi-Indicator Enhancement Framework (commit c367347)

**Scope:** All 6 SOPs.

**Added:**

- **ECON-C1 / Category-Specific Mandatory Method Catalog** — every indicator_type routes to a mandatory method list.
- **ECON-C2 / Mandatory Output Schema Per Method** — exact column schema for each mandatory method.
- **META-P0 / Phase 0: Analysis Brief Gate** — no agent starts work without approved brief.
- **ECON-T1 / Tournament Design Parameters** — target-class-aware tournament parameters.
- **ECON-T2 / Target-Class-Aware Backtest Parameters** — backtest parameters match target class.
- **RES-MS1 / Multi-Indicator Scaling** — tiered literature review, batch spec memos, canonical glossary, master event database.
- **RES-MS2 / Batch Direction Annotation Delivery** — direction annotations batched across pairs.
- **DATA-B1 / DATA-B2** — batch data availability pre-check and shared indicator deduplication.

**Rationale:** Scaling the team from single-pair analysis to 73-pair portfolio required framework generalization. Econometric catalog expanded 52 to 95 methods with 6 new categories and Relevance Matrix; data series catalog added 31 indicators and 35 targets.

---

## 2026-03-14 — Cross-Review Update (commit 9364b2c)

**Scope:** All 5 agent SOPs.

**Added (via self-update after cross-review):**

- **META-NO / New Agent Onboarding Protocol** — cross-review SOPs, self-update, distill lessons.
- **META-TCH1 / META-TCH2** — Task Completion Hooks (Validation/Verification and Reflection/Memory).
- **META-HO / META-ACK** — Handoff Protocol and Acknowledgment Protocol (silence is never acceptance).

**Rationale:** Cross-review surfaced handoff gaps that solo work missed.

---

## 2026-03-01 — HY-IG Initial Analysis (commit e2a4c65)

**Scope:** No SOP changes. First end-to-end pair.

**Surfaced issues later fixed:** HMM state inversion (commit 2c9368d), pipeline fragmentation (later META-PSC), header-only trade log (later ECON-C4).

---

## 2026-02-28 — Defensive Rules (commits 22ac0bf, efccb3b)

**Scope:** All agent SOPs.

**Added:**

- **META-D1 / Defense 1: Self-Describing Artifacts** — producer rule: meaningful column names, units, sign conventions, boundaries, sidecar manifest.
- **META-D2 / Defense 2: Reconciliation at Every Boundary** — consumer + reviewer rule: known-fact sanity checks, derived-quantity cross-check, automated reconciliation script.

**Rationale:** Prevent implicit-assumption errors at every agent boundary. HMM state inversion was the archetypal failure mode.

---

## 2026-02-15 — Visualization Integrity Rules (commit series)

**Scope:** Visualization SOP.

**Added:**

- **VIZ-A1** — No Inverted Axes on Financial Dashboards.
- **VIZ-A2** — Unit Discipline: Axis Labels Must Match Data Values.
- **VIZ-A3** — Standard Chart Catalog with Canonical Signal Selection.
- **VIZ-A5** — Caption Ownership (Ray displays, Vera audits).
- **VIZ-CP1** — Color Palette Mandatory (colorblind-friendly, consistent).
- **VIZ-CS1** — Standard Chart Set Per Pair (canonical 10-chart set).

**Rationale:** Consistent chart specifications across pairs. Canonical chart catalog prevents ad-hoc rerun drift.

---

## 2026-02-01 — App Dev Integration (commit 04c8f67, e9c6467)

**Scope:** New AppDev SOP + cross-review round 2.

**Added:**

- **APP-PA1 / APP-SF1 / APP-DA1 / APP-SP1** — Portal Architecture, Storytelling Flow, Direction Annotation, Strategy Execution Panel standards.
- **META-IA / Interpretation Annotation Handoffs** — four-agent protocol for same-indicator / different-target direction differences.

**Rationale:** Streamlit portal became canonical delivery surface.

---

## 2026-01-20 — Research Catalogs (commits 155204b, ef5b83b)

**Scope:** docs/ reference catalogs.

**Created:**

- data-series-catalog.md
- econometric-methods-catalog.md
- backtesting-approaches-catalog.md
- threshold-regime-methods-catalog.md
- reference-catalogs-index.md (with Run Registry — META-REG)

**Rationale:** Standing references that all agents consult.

---

## 2026-01-10 — Initial SOP Foundation (commits 10f4b0a, 652d1b5, 1156869)

**Scope:** First agent SOP set.

**Created:**

- data-agent-sop.md (Data Dana)
- econometrics-agent-sop.md (Econ Evan)
- visualization-agent-sop.md (Viz Vera) — early Rules A1/A2 form
- research-agent-sop.md (Research Ray)
- team-coordination.md — early handoff specifications, escalation rules

**Foundational rules established:**

- **DATA-DD1** — Data Dictionary (Display Name, Direction Convention, Effective Start, Unit, SA status, known quirks).
- **DATA-DD3** — Stationarity Test Delivery (ADF/KPSS/PP).
- **DATA-H1..H3** — handoff specifications.
- **ECON-SS1 / ECON-ES1 / ECON-DG1 / ECON-SA1** — Model Specification, Estimation Standards (HC3 default), Diagnostics Mandatory, Sensitivity Analysis.
- **RES-B1** — Two-Stage Delivery Protocol (spec memo + full brief).
- **META-CR** — Communication Rules (7-point).
- **META-ER** — Escalation Rules.
- **META-QS** — Quality Standards (team-wide).

---

## Appendix: Rule-to-Commit Cross-Reference

For rules whose source commit predates this changelog or is distributed across multiple commits, see git log and the originating SOP section. This changelog captures rule IDs going forward; earlier rules are registered in standards.md with their current SOP section as source.

## Appendix: How to Add an Entry

1. Identify the SOP(s) being changed.
2. Name each new or modified rule by ID (if new, pick an ID that fits the prefix scheme in standards.md).
3. Write a one-paragraph summary per rule: what changed, why, and what upstream evidence (commit, bug, stakeholder feedback) drove it.
4. Commit the SOP change, standards.md update, and this changelog entry together.
5. Entries are newest-first.
