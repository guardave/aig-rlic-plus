# Cross-Review — Econ Evan — 2026-04-20

**Reviewer:** econ-evan
**Scope:** All 7 SOPs in `docs/agent-sops/` + `docs/team-standards.md` (Wave 10F skeleton), read against
`docs/sop-changelog.md` since 2026-04-12.
**Posture:** Findings only. No SOPs were edited.
**Anchors:** The three Vera-VIZ-IC1 open questions flagged in `team-standards.md §2.1/§3/§4` are the
proximate trigger; my broader goal is to surface any rule whose content is undefined, duplicated, or
silently weakened — with emphasis on econometrics-facing artifacts (signals parquet, schema sidecars,
`interpretation_metadata.json`, tournament artifacts).

---

## Section 1 — Conflicts

### 1.1 Sidecar naming conflict WITHIN VIZ-IC1 itself

- `visualization-agent-sop.md:960` (VIZ-IC1 step 4) says palette conformance is checked against
  `_meta.json.palette_id` (see also line 613 "Every chart's `_meta.json` sidecar (per VIZ-SD1) MUST carry
  `palette_id`"), but
- `visualization-agent-sop.md:962` (VIZ-IC1 step 6) says the `narrative_alignment_note` goes in
  **`_manifest.json`**.

A single rule emits two names for the same artifact. This is the single most damaging conflict because
VIZ-IC1 is the new blocking pre-save rule — Vera's linter cannot know which file to write. Cross-check
`appdev-agent-sop.md:830` ("`_meta.json` per chart") and `visualization-agent-sop.md:735/827`
("`{chart_name}_meta.json`"): the strong majority says `_meta.json` for chart sidecars. VIZ-IC1 step 6 is
the outlier.

### 1.2 `interpretation_metadata.json` ownership — three SOPs disagree

- **Dana** claims producer ownership at `data-agent-sop.md:133-151, 201, 482-486` and DATA-D6 §516 (`owner_writes`
  is `dana → evan → ray`, Dana writes first).
- **`team-standards.md:80`** (§5.1 handoff registry) lists **Producer = Dana**, schema DATA-D6.
- **Ray** (`research-agent-sop.md:287-293`) claims ownership of `strategy_objective` inside the same file
  (consistent with DATA-D6).
- **Ray** also claims at `research-agent-sop.md:1000` that *"Vera may begin charting using Evan's
  `interpretation_metadata.json`"* — naming Evan, not Dana, as the producer. This is stale prose from an
  earlier wave (pre-DATA-D6).

Consequence: a new dispatch reading only Ray's SOP will look for the file under Evan's outputs and miss
Dana's DATA-D6 schema validation. Fix at Ray's line 1000 — it is the only concrete "wrong owner" claim
still in force.

### 1.3 Chart filename canonicalisation

- `team-standards.md:35` (§2.1) says bare-name is canonical per "VIZ-NM1" but holds the rule open pending
  cross-review.
- `visualization-agent-sop.md:483` uses pair-less filenames *within* a `{pair_id}` folder
  (`output/charts/{pair_id}/plotly/history_zoom_{episode_slug}.json`).
- HY-IG v2 on disk carries BOTH bare and `hy_ig_v2_spy_`-prefixed copies (status-board / prior audits).
- `indpro_xlp`, `umcsent_xlv` ship bare-name only.

Canonical: bare-name under a `{pair_id}/` folder (the folder IS the prefix). Prefixed duplicates are
deprecated. Document this in §2.1.

### 1.4 `signal_code` vs `signal_column` disambiguation absent from non-Evan SOPs

Evan's SOP + `ECON-DS2` + `winner_summary.schema.json` are explicit that `signal_code` is the stable
registry key (e.g. `hmm_stress`) and `signal_column` is the parquet column name (e.g.
`hmm_2state_prob_stress`). But:

- `appdev-agent-sop.md` references chart metadata but never names the distinction.
- `qa-agent-sop.md:308` reads `target_symbol`/`indicator_id` but never cross-checks `signal_code` ∈
  `docs/schemas/signal_code_registry.json`.
- `team-standards.md §5.1` says *"column names match tournament CSV `signal_code`"* — which on a strict
  reading contradicts Evan's rule (parquet column is `signal_column`, not `signal_code`).

### 1.5 "interpretation_metadata is Evan's" contradiction in RES-17 chain

`econometrics-agent-sop.md:1009` asserts QA parses chart `_meta.json` for signal names and cross-checks
`signal_scope.json`. But `qa-agent-sop.md` does not currently name `signal_scope.json` in any gate (Grep
confirmed), even though ECON-SD is blocking. Signal-scope is the only enforcement path for Evan's
Evidence/Methodology boundary — a silent dead-letter.

---

## Section 2 — Redundancies (with canonical location)

| Rule / content | Duplicated in | Canonical home |
|----------------|---------------|----------------|
| Unit registry (bps/pct/ratio/…) | data-agent-sop.md (DATA-D2) + econometrics-agent-sop.md (§ unit discipline) + visualization-agent-sop.md (VIZ-A2) | **DATA-D2** (data SOP); `team-standards.md §X` should link, not copy |
| Column-suffix vocabulary (`_bps`, `_pct`, `_ret`, …) | DATA-D12 + DATA-D2 + VIZ-A2 | **DATA-D12** |
| Sidecar schema names (`_meta.json` for charts; `_manifest.json` for model artifacts) | viz-sop (many places) + econ-sop (§Defense 1) + appdev-sop (§Chart metadata sidecar) + team-standards.md §3 (stub) | **`team-standards.md §3`** — promote here and de-duplicate in SOPs |
| Deploy-required artifact list (signals parquet + 5 JSONs + tournament CSV) | ECON-DS2 + GATE-29 + team-standards.md §5.2 | **`team-standards.md §5.2`** (already correctly hosted) |
| Chart filename convention (`output/charts/{pair_id}/plotly/{chart_type}.json`) | visualization-agent-sop.md (VIZ-V8) + team-standards.md §2.1 (stub) + appdev-sop (§PT1) | **`team-standards.md §2.1`** |
| Palette registry path + role keys | visualization-agent-sop.md + team-standards.md §4 | **`team-standards.md §4`** |
| `interpretation_metadata.json` field ownership (`owner_writes`) | DATA-D6 + research-sop §strategy_objective + team-coordination.md §19-21 | **`docs/schemas/interpretation_metadata.schema.json` `owner_writes`** (the schema IS the contract); SOPs should cite, not restate |
| "Unknown is not a display state" meta-rule | team-coordination.md (§160-164) + appdev-sop + research-sop | **team-coordination.md** |
| EOD block (four mandatory files) | team-coordination.md + every agent SOP tail | **team-coordination.md** — agent SOPs should link |

---

## Section 3 — Rules That Belong in `team-standards.md`

Currently the skeleton holds Directory Layout, Filename Conventions, Sidecar Schema, Palette, Handoff
Contracts, Deploy-Required artifacts, Profile files, Dispatch Template. The following additions would
cover the rest of the cross-agent surface area:

1. **Sidecar artifact-type registry (populate §3).** One name per artifact *type*:
   - Chart sidecars → `{chart_name}_meta.json` (Vera, per VIZ-V8).
   - Dataset / model-output sidecars → `{artifact}_manifest.json` (Evan/Dana, per ECON-DS2 + DATA-D5).
   - Schema sidecar (per-parquet column contract) → `{subject}_{frequency}_schema.json` (Dana, DATA-D5).
   Three names, three owners, no overlap.
2. **Palette role-alias registry (populate §4).** Add `indicator` / `target` / `benchmark` aliases so VIZ-IC1
   step 4 is mechanically verifiable. Map:
   - `indicator` → `primary_data_trace`
   - `target` → `secondary_data_trace`
   - `benchmark` → NEW key (visually distinct from `equity_curve`; proposal below).
3. **Column-naming convention cross-agent.** DATA-D12 suffix vocabulary promoted here; every agent SOP cites.
4. **Schema version contract (META-SCV).** Already in team-coordination; hoist a one-line
   pointer into `team-standards.md §3` so it sits with sidecar discussion.
5. **Signal-code vs signal-column distinction.** One sentence, referenced by Evan / Ace / Vera / QA to
   resolve §1.4.
6. **`interpretation_metadata.json` owner-writes mapping.** Copy `owner_writes` from schema into §5 as
   a quick-lookup table. Ownership drift (Ray §1000) stops being possible.
7. **Regression-note naming / path convention.** `regression_note_<YYYYMMDD>.md` lives at
   `results/{pair_id}/` — currently scattered across META-RNF + data / econ / research SOPs.
8. **OOS-window policy pointer.** ECON-OOS1/OOS2 is Evan-local today but consumed by Ace (portal labels)
   and Ray (narrative) — it belongs in the shared registry.

---

## Section 4 — Silent Weakening (rules with no enforcement)

| Rule | Where declared | Why it is dead-letter |
|------|---------------|-----------------------|
| **VIZ-IC1 step 4 (palette aliases)** | visualization-agent-sop.md:960 | `color_palette_registry.json` lacks `indicator` / `target` / `benchmark` keys — the assertion cannot fire. The rule says "use X" but X does not exist. |
| **VIZ-IC1 step 6 (narrative-alignment note)** | visualization-agent-sop.md:962 | Writes to `_manifest.json` but every other Vera rule writes `_meta.json`. The note goes to a file nothing else reads. |
| **ECON-SD signal-scope audit by QA** | econometrics-agent-sop.md:1009 | `qa-agent-sop.md` has no checklist line that parses `signal_scope.json`. Evan's scope discipline relies on a QA step QA does not actually perform. |
| **DATA-D13 manifest bootstrap** | data-agent-sop.md:586 | `data/manifest.json` and `data/display_name_registry.csv` do not exist on disk today (Wave-5C deferred). Rule references them as authoritative — every consumer currently hardcodes around their absence. |
| **DATA-D11 reference-pair sidecar gate** | data-agent-sop.md:528 | Gate depends on `data/{pair_id}_schema.json` existing; HY-IG v2 shipped without one and was accepted. Rule exists; enforcement did not stop acceptance. |
| **META-RYW "Read Your Own Work"** | team-coordination.md (Wave 10F) + every producer SOP | No artifact — handoff notes do not have a machine-checkable re-read field. It is a promise, not a gate. |
| **GATE-24 chart-text coherence "same commit"** | team-coordination.md item 24 | There is no pre-commit hook that verifies a chart file and a page caption are modified together. Evidence is manual. |
| **META-FRD 2x/quarter cap** | team-coordination.md | No counter exists in `docs/pair_execution_history.md`; the rule says "escalate at >2x" but the count is never tallied. |
| **RES-VS / DATA-VS status-vocabulary self-check** | data/research SOPs | `docs/portal_glossary.json` (the supposed canonical list) has not been updated as part of either SOP's workflow. |
| **QA-CL6/GATE-NC cross-check** | referenced in VIZ-IC1 and ECON-SD | Not independently defined in `qa-agent-sop.md` top-level gate list (Grep finds only `QA-CL3/CL4/CL5`). Dangling cross-reference. |

---

## Section 5 — Evan-Specific Observations (econometrics angle)

### 5.1 ECON-DS2 surface is now clean, but the carve-out is brittle

The `.gitignore` line `!results/**/signals_*.parquet` exists and Wave 10E added an explicit gate. Good.
Remaining risk: any future carve-out pattern (e.g. `tournament_manifest.json` if we ever gitignore JSON)
will repeat the Wave-4A failure. Recommendation: promote the deploy-required artifact list (team-standards
§5.2) from informational to **`scripts/hooks/check-deploy-artifacts.sh`** run on every commit that touches
`results/*/`. Today §5.2 is prose.

### 5.2 Signals parquet column-naming contract

Evan's MEMORY §ECON-DS2 + `winner_summary.schema.json` say the parquet must contain BOTH `signal_code`
columns AND an alias column using `winner_summary.signal_column`. This is *producer-only knowledge* — Ace's
loader in `app/pages/*_strategy.py` reads `signal_column`, so a producer that forgets the alias breaks the
Probability Engine Panel silently. Rule is correct; it just sits inside Evan's head, not in a reader-facing
schema. Proposal: add `signals_schema.json` (new) naming required columns = `{union of signal_codes,
signal_column}`.

### 5.3 Schema contracts: `owner_writes` is the right idea; cite it once

DATA-D6's `owner_writes` should be the canonical ownership map for every multi-author file:

- `interpretation_metadata.json` — today.
- `acceptance.md` — candidate (Lead/Quincy/producers all write sections).
- `regression_note_<date>.md` — candidate (all producers append `### Prior-version observation`).

A single META-OW ("Ownership Writes") meta-rule naming the schema `owner_writes` pattern and listing every
file it governs would kill the "who writes what into which file" question permanently.

### 5.4 Tournament artifacts — dual-log contract (ECON-C4) is solid; the broker log needs a schema

`winner_trades_broker_style.csv` schema is fully specified in prose (ECON-C4 columns + synthesis algorithm
+ disclaimer). But no JSON-Schema. If Ace ever renders it in a KPI card, a schema drift is undetectable.
Proposal: ship `docs/schemas/broker_trade_log.schema.json` + wire it into GATE-27 smoke test.

### 5.5 `interpretation_metadata` `owner_writes` enum vs `indicator_type` canonical 7

Team-coordination §20 enumerates the 7 canonical types (`price/production/sentiment/rates/credit/
volatility/macro`). Evan's Rule C1 routes mandatory methods on these 7. If Dana ever introduces a new type
(e.g. `liquidity` in DATA-D3 step 3), Evan's Rule C1 routing has no method list → silent drop. Proposal:
DATA-D3 + Rule C1 should jointly require a method-routing entry before the type enum is extended. Today
only DATA-D3 has that gate.

### 5.6 OOS window persistence (ECON-OOS1) — not yet consumed

`oos_split_record.json` is Evan-authored; no other agent currently reads it. Proposal: Ace's Methodology
page should display the `split_policy_id` and `justification` fields. Today those values exist and are
never shown to the stakeholder — defeats the purpose of persisting them.

### 5.7 `analyst_suggestions.json` lifecycle

Specified in ECON-AS as *informational, no status field, no lifecycle*. Correct for a suggestion bin —
but `team-standards.md §5.2` lists it as deploy-required. If it must ship, it should also be observable by
users somewhere (Methodology appendix?). Today it's required to exist and nobody reads it.

---

## Section 6 — Open Questions from Vera's VIZ-IC1 retro-apply

### 6.1 Chart filename: bare-name vs pair-prefixed

**Answer:** **Bare-name under `output/charts/{pair_id}/plotly/`**. The folder IS the namespace. Prefixed
duplicates are deprecated; on rerun Vera should delete the prefixed copy in the same commit that writes
the bare-name canonical. Document in `team-standards.md §2.1`.

**Reasoning:** (a) `pair_id` is already encoded in the path so the prefix is redundant; (b) Vera's chart
catalog and Ace's loader both key off chart-type strings (`history_zoom_{episode}`, `hero_dual_panel`,
etc.) that are naturally reusable across pairs; (c) 5 of 6 pairs on disk already use bare-name — the
prefixed duplicate is the outlier.

### 6.2 Sidecar naming: `_meta.json` vs `_manifest.json`

**Answer (my pick):** **Use both, but for different artifact types.**

| Artifact type | Sidecar name | Owner | Purpose |
|---------------|-------------|-------|---------|
| Plotly chart JSON | `{chart_name}_meta.json` | Vera | Display-side metadata: caption, audience_tier, palette_id, annotation_strategy_id, events_registry_version |
| Dataset / parquet / CSV model output | `{artifact}_manifest.json` | Dana / Evan | Producer-side contract: column semantics, units, sign conventions, ≥3 sanity-check assertions |

**Reasoning:** (a) I already use `_manifest.json` for every model artifact (econ-sop §Defense 1 — 3+
assertions minimum). (b) Vera's tooling already uses `_meta.json` for every chart sidecar (VIZ-V5, VIZ-V8,
VIZ-V11, VIZ-V12, VIZ-SD1 all cite `_meta.json`). (c) The two sidecars have genuinely different shapes:
chart meta is display metadata (no assertions); model-output manifest is producer contract (assertions
required). One name for two shapes would invite schema drift.

**Consequence for VIZ-IC1 step 6:** the `narrative_alignment_note` belongs in `_meta.json`, not
`_manifest.json`. Fix VIZ-IC1 step 6 — it is the source of §1.1 internal contradiction. Populate
`team-standards.md §3` with the two-type rule above.

### 6.3 Palette role aliases — should the registry gain `indicator` / `target` / `benchmark`?

**Answer: YES**, and failure to add them is what silently weakens VIZ-IC1 step 4.

Proposed mapping (populates `team-standards.md §4`):

- `indicator` → existing `primary_data_trace`.
- `target` → existing `secondary_data_trace`.
- `benchmark` → **new key** `benchmark_trace`, visually distinct from `equity_curve` (which is
  pair-specific strategy P&L, not a passive benchmark). My suggestion: dashed or semi-transparent version
  of `secondary_data_trace` so B&H vs winner remains visually paired but legible. Ace + Vera should
  confirm a hex; I have no strong preference as long as it's distinct.

**Why new key rather than reusing `equity_curve`:** benchmark is a passive reference line; `equity_curve` is
the active strategy outcome. On Strategy pages these must not collide visually.

---

## Section 7 — Priority Ranking (top 5 fixes)

Ordered by "blast radius × cheapness to fix":

1. **Fix VIZ-IC1 step 6 sidecar name to `_meta.json`** (1-line edit). Removes the single most damaging
   in-rule contradiction and lets Vera's pre-save linter actually run. Cross-ref §1.1 / §6.2.
2. **Add `indicator` / `target` / `benchmark_trace` role aliases to `color_palette_registry.json`** and
   populate `team-standards.md §4`. Without this VIZ-IC1 step 4 cannot fire on any chart. Cross-ref §6.3.
3. **Edit `research-agent-sop.md:1000`** so the sentence names **Dana** as producer of
   `interpretation_metadata.json` (not Evan). Removes the only live ownership-drift misstatement.
   Cross-ref §1.2.
4. **Populate `team-standards.md §3` with the two-sidecar rule** (`_meta.json` for charts, `_manifest.json`
   for datasets / model outputs) and promote DATA-D12 suffix vocabulary reference. This kills the §2
   redundancy and makes future SOP edits cite a single home.
5. **Add `signal_scope.json` parsing to `qa-agent-sop.md`** as a named checklist line (QA-CL6 or similar).
   Closes the Evan-side ECON-SD enforcement gap — today the only thing stopping off-scope correlations is a
   QA step QA does not perform. Cross-ref §1.5 / §4.

Runners-up (would fix next): (6) hoist `owner_writes` concept into a META-OW meta-rule; (7) build
`scripts/hooks/check-deploy-artifacts.sh` so §5.2 becomes enforceable; (8) bootstrap DATA-D13
manifest + display-name registry so DATA-D11 stops being paper.

---

## Summary

Three findings matter most from the econometrics bench:

- Vera's three VIZ-IC1 open questions are answerable today with low-cost decisions (bare-name,
  two-sidecar split, three role aliases) — the blocker is not debate but unpopulated stubs in
  `team-standards.md`.
- `interpretation_metadata.json` ownership is correctly codified in DATA-D6's `owner_writes` but a
  single stale sentence in Ray's SOP still names Evan. One-line fix prevents future drift.
- Several new rules (META-RYW, GATE-24, META-FRD cap, DATA-D11, ECON-SD) are declared but have no
  machine enforcement — they live and die by human attention. The highest-leverage next step is to
  promote one or two (e.g. ECON-SD scope parsing) from prose into `scripts/hooks/` or QA's named
  checklist.

Word count ≈ 2,050.
