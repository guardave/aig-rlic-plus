# Viz Vera — Phase 1 Intra-SOP Review

**Date:** 2026-05-08
**Reviewer:** Viz Vera (viz-vera)
**Scope:** `docs/agent-sops/visualization-agent-sop.md` only — no edits made (LEAD-DL1 binding).
**SOP version read:** current HEAD on branch 260430.

---

## Findings

### F-01 — Stale palette table directly contradicts VIZ-V11 (FAIL)

**Rule/section:** "Viz Preferences — Color Palette (Mandatory)" (near line 1590)
**Problem:** The "Standard Chart Set Per Pair" section carries a `### Color Palette (Mandatory)` table assigning matplotlib-default colors: Indicator = `#d62728`, Target = `#1f77b4`, Strategy = `#2ca02c`, Benchmark = `#7f7f7f`. VIZ-V11 explicitly classifies all of those exact hex values as **prohibited raw defaults** that trigger a blocking pre-save lint error. VIZ-V11 also states: "Prose-only palette specifications are prohibited; this registry is the single source of truth." The table heading "Mandatory" further implies these colors must be used, directly undermining VIZ-V11's authority.
**Severity proposal:** FAIL — active contradiction between an inline table and the rule that governs it. A new Vera reading the SOP top-to-bottom would hit the "Mandatory" table in the Preferences section and build charts with colors that fail VIZ-V11 lint.
**Suggested fix (Phase 4):** Remove or replace the `### Color Palette (Mandatory)` table with a pointer to `docs/schemas/color_palette_registry.json` and the `okabe_ito_2026` palette ID. Add a note that the palette in that section was the Wave-1 baseline, now superseded by VIZ-V11.

---

### F-02 — `output/_comparison/` referenced for live chart saves despite META-AL prohibition (FAIL)

**Rule/section:** VIZ-V11 pre-save lint preamble (line 1111), §8 Deliver — Directory structure (line 1246), Comparison Dashboard Charts (lines 1390, 1395)
**Problem:** Three locations in the SOP instruct Vera to save chart JSON files to `output/_comparison/`:
- VIZ-V11 lint header: "before saving any chart JSON under `output/charts/**/plotly/` or `output/_comparison/`"
- §8 Deliver: "Cross-pair charts go in `output/_comparison/`"
- Comparison Dashboard: two save paths at `output/_comparison/{indicator_id}_all_targets_...` and `output/_comparison/all_indicators_{target_id}_...`

VIZ-V1 explicitly states that `output/_comparison/history_zoom_*.json` is **REMOVED** per META-AL and that emitting one is a META-AL violation. META-ZI in standards.md also says there is no `output/_comparison/` fallback. The three remaining `_comparison/` references concern cross-pair comparison dashboards (not zoom charts), but the VIZ-V11 lint preamble also lists `output/_comparison/` as in-scope for chart saves, and the Deliver section gives no exemption. The result is ambiguous: is `output/_comparison/` allowed for non-zoom comparison charts or not?
**Severity proposal:** FAIL — the contradiction is present between VIZ-V1/META-AL and §8/VIZ-V11/Comparison Dashboard sections. Needs explicit carve-out or prohibition.
**Suggested fix (Phase 4):** Add a scoping note clarifying that `output/_comparison/` remains valid **only** for cross-pair comparison charts (not history_zoom charts). Update VIZ-V11 lint preamble to reflect this. Remove the `output/_comparison/` reference from the lint header or note it is scoped to non-zoom comparisons.

---

### F-03 — VIZ-DP1 kaleido commit status: internal contradiction with older VIZ-DP1 text (WARN)

**Rule/section:** VIZ-DP1 (line 875) vs. VIZ-CV1/Rule V5 (line 1034)
**Problem:** Rule V5 (line 1034) explicitly notes: "Unlike the earlier phrasing in VIZ-DP1 (which called the PNG a 'working artifact, not committed'), perceptual PNGs are now committed to git." However, searching the current SOP text, there is no surviving "working artifact, not committed" phrase in VIZ-DP1 — that prior phrasing appears to have been superseded in place. The V5 clarification therefore references a ghost: it cites a prior VIZ-DP1 position that no longer exists in the text. This orphan reference is confusing and may cause a reader to go looking for the superseded wording and doubt whether the commit requirement is truly current.
**Severity proposal:** WARN — no actual contradiction in the current rules (both VIZ-DP1 and V5 say "committed"), but the self-referential "unlike earlier phrasing" text should be removed now that the superseded wording is gone.
**Suggested fix (Phase 4):** Delete the "Unlike the earlier phrasing in VIZ-DP1..." sentence from VIZ-CV1/Rule V5. The rule stands on its own; the historical note no longer helps.

---

### F-04 — VIZ-V5 (VIZ-CV1) check #6 references "source/sample period in visible chart text" but the gate checklist does not close this (WARN)

**Rule/section:** VIZ-CV1 Rule V5 check 6 (line 1012) and Quality Gates checklist (line 1509)
**Problem:** VIZ-CV1 check 6 mandates that "the chart has visible source/sample text: either figure subtitle/source note/footer contains `source` and `source_sample_period`, or the title explicitly includes the sample window where space is constrained." The Quality Gates checklist line reads: "Source/sample period appears in visible chart text and in `_meta.json`." This is consistent. However, the VIZ-IC1 pre-save assertion list (6 checks, lines 1476–1482) does not include a source/sample-period check — VIZ-IC1 covers title-axes, legend-data, annotations-data, palette, and unit discipline, but not the visible source note. A chart could pass all 6 VIZ-IC1 checks and still fail VIZ-CV1 check 6.
**Severity proposal:** WARN — gap between VIZ-IC1 and VIZ-CV1, not a contradiction, but VIZ-IC1 is presented as the "pre-save" gate and VIZ-CV1 as the "post-save" gate. Moving source/sample enforcement to VIZ-IC1 would catch it earlier. Currently a producer could save and commit a chart before realising the source note is missing.
**Suggested fix (Phase 4):** Add a seventh VIZ-IC1 check: "Source note / visible provenance — chart includes source attribution and `source_sample_period` in figure text (subtitle, footer, or compact title notation)."

---

### F-05 — Episode slug names inconsistent between VIZ-V1 and VIZ-ZOOM1 (FAIL)

**Rule/section:** VIZ-V1 canonical slugs (line 552) vs. VIZ-ZOOM1 required episodes (line 641)
**Problem:**
- VIZ-V1 lists canonical slugs as: `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`
- VIZ-ZOOM1 lists required episodes as: `dotcom`, `gfc`, `covid`, `inflation_2022` (four episodes, no `taper_2018`)
- VIZ-ZOOM1 table header column is titled "2022" implying the fourth episode is `inflation_2022`
- VIZ-ZOOM1's optional rule says `inflation_2022` is optional for activity-survey pairs but never mentions `taper_2018` as an episode at all

Additionally, the session notes reference a `taper` episode slug for some pairs (e.g., `sofr_ted_spy: covid, taper, ukraine`) and the outstanding-work file mentions `ukraine` — neither `taper` nor `ukraine` appears in the SOP's canonical slug list. VIZ-ZOOM1 is silent on these additional slugs, and VIZ-HZE1's example gate record uses `[dotcom, gfc, covid, inflation_2022]` — omitting `taper_2018` entirely.

The status-board entry (2026-04-24, Quincy GATE-VIZ-NBER2) hardcodes recession slugs as `{dot_com, gfc, covid}` using `dot_com` (with underscore) rather than `dotcom` (no underscore), which conflicts with VIZ-V12's registered `dotcom` slug.
**Severity proposal:** FAIL — inconsistent slug naming creates silent production errors. VIZ-HZE1 gate enumerates slugs from `episode_registry.json` but the SOP itself has three different slug-naming norms.
**Suggested fix (Phase 4):** Establish one canonical slug list in VIZ-ZOOM1 explicitly including `taper_2018` with its optionality rule, and add a cross-reference to VIZ-V12 as the ground truth. Remove the `dot_com` variant usage (status board is outside Vera's Phase 1 scope, but flag for cross-review in Phase 3). Add a note that `ukraine` and `taper` are non-canonical slugs that require a registry PR before chart production.

---

### F-06 — VIZ-IC1 cross-references non-existent rules: META-RYW and QA-CL6/GATE-NC (WARN)

**Rule/section:** VIZ-IC1 cross-references (line 1493)
**Problem:** The cross-reference block for VIZ-IC1 cites `META-RYW (team-level self-review — VIZ-IC1 is its chart-specific instance)` and `QA-CL6/GATE-NC (QA cross-checks narrative claims against chart data at acceptance)`. Neither `META-RYW`, `QA-CL6`, nor `GATE-NC` appears anywhere in `docs/standards.md` or in the QA SOP as currently read. These are dangling references that cannot be resolved.
**Severity proposal:** WARN — unresolvable cross-references mean a producer following "see QA-CL6" has nowhere to go.
**Suggested fix (Phase 4):** Remove or replace with the closest real equivalents: `META-QS` (team quality standards) for META-RYW, and `QA-CL1` (QA standard checklist) for QA-CL6. Flag to Lead whether GATE-NC was ever defined or is a draft ID that should be backlogged under META-BL.

---

### F-07 — VIZ-IC1 is not registered in `docs/standards.md` (WARN)

**Rule/section:** VIZ-IC1 rule body (line 1471); `docs/standards.md` VIZ section
**Problem:** The VIZ standards table in `docs/standards.md` lists VIZ-A1 through VIZ-V13, VIZ-O1, VIZ-E1, VIZ-NBER1, VIZ-ZOOM1, VIZ-HZE1, VIZ-DP1, VIZ-NM1, etc. — but **VIZ-IC1** does not appear. The SOP itself flags this at line 498: "Standards registry follow-up (do not block this SOP edit): team standards still need explicit registry entries for VIZ-O1, VIZ-E1, VIZ-NBER1, VIZ-ZOOM1, VIZ-HZE1, VIZ-DP1, and VIZ-CP1." However VIZ-O1, VIZ-E1, VIZ-NBER1, VIZ-ZOOM1, VIZ-HZE1, and VIZ-DP1 *are* now registered in standards.md. VIZ-IC1 is the only one still missing.
**Severity proposal:** WARN — gap between SOP coverage and standards registration. VIZ-IC1 is a blocking rule (it blocks chart saves) so its absence from the canonical registry is a discoverability gap for Quincy and Lead.
**Suggested fix (Phase 4):** Add VIZ-IC1 to `docs/standards.md` VIZ table. Also remove the stale self-flagging note at SOP line 498 since the other rules it lists are now registered.

---

### F-08 — GATE-VIZ-NBER1, GATE-VIZ-ZOOM1, GATE-HZE1, GATE-DP1 not in GATE section of standards (WARN)

**Rule/section:** Cross-references in VIZ-NBER1, VIZ-ZOOM1, VIZ-HZE1, VIZ-DP1; `docs/standards.md` GATE section
**Problem:** Multiple VIZ rules cite downstream QA gates by name:
- VIZ-NBER1 cites `GATE-VIZ-NBER1` (line 611)
- VIZ-ZOOM1 cites `GATE-VIZ-ZOOM1` (line 671)
- VIZ-HZE1 cites `APP-EP4 / GATE-25` (line 740, legitimate) and implies a VIZ-HZE1 companion gate

None of `GATE-VIZ-NBER1`, `GATE-VIZ-NBER2`, `GATE-VIZ-ZOOM1`, or `GATE-HZE1` appears in `docs/standards.md`'s GATE section (which ends at GATE-31). They exist only in the QA SOP. This means the standards index does not reflect the complete gate set.
**Severity proposal:** WARN — cross-reference resolves by navigating to the QA SOP, but the GATE registry in standards.md is meant to be the complete gate index. A Lead or new agent consulting standards.md cannot enumerate all blocking gates from that file alone.
**Suggested fix (Phase 4):** Flag to Lead for standards maintenance. Vera's scope: add GATE-VIZ-NBER1, GATE-VIZ-NBER2, GATE-VIZ-ZOOM1, and GATE-HZE1 to the GATE section of standards.md as VIZ-owned blocking gates. (This is a standards.md edit — confirm scope with Lead before Phase 4 execution.)

---

### F-09 — VIZ-DP1 upstream check does not include `equity_curves.json` in the dual-panel batch (WARN)

**Rule/section:** VIZ-DP1 — "How to apply the gate in a handoff batch" (lines 825–850)
**Problem:** The VIZ-DP1 batch verification code enumerates:
```python
dual_panel_patterns = [
    f"output/charts/{pair_id}/plotly/history_zoom_*.json",
    f"output/charts/{pair_id}/plotly/hero.json",
]
```
`equity_curves.json` uses a dual-panel layout (equity curve on top, drawdown on bottom, shared x-axis) as mandated by VIZ-V1 and the Standard Chart Set notes (line 349). The hero and history_zoom charts are covered by the snippet, but `equity_curves.json` is not. If a generator assigns the drawdown panel's traces to the wrong xaxis, VIZ-DP1 would not catch it.
**Severity proposal:** WARN — the check covers the highest-risk charts but misses `equity_curves.json`, which is also dual-panel and at risk of the same axis-assignment bug.
**Suggested fix (Phase 4):** Add `f"output/charts/{pair_id}/plotly/equity_curves.json"` to the `dual_panel_patterns` list in the VIZ-DP1 batch snippet.

---

### F-10 — VIZ-CV1 (Rule V5) skip-condition only exempts `_meta.json` and `_smoke_test_*` but not perceptual PNG files themselves (WARN)

**Rule/section:** VIZ-CV1 / Rule V5 skip condition (line 1036) and the procedural code (line 1051)
**Problem:** The skip condition states: "If a `.json` file is a `_meta.json` sidecar or a `_smoke_test_*.log`, no perceptual PNG is required." The code snippet correctly skips filenames that end in `_meta` or start with `_smoke_test`. However, it does not skip `_perceptual_check_*.png` files if they somehow acquired a `.json` extension (unlikely), nor does it skip the `_smoke_test_{YYYYMMDD}.log` — those are `.log` files, not `.json`. The skip condition text says `.json` files but the log files are `.log`. This is a trivial mismatch (the code `glob(*.json)` would never match a `.log` file), but the prose description is slightly misleading: "if a `.json` file is a `_meta.json` sidecar or a `_smoke_test_*.log`" implies smoke test logs could be `.json`, when they're always `.log`.
**Severity proposal:** WARN (low) — no functional gap, but the prose should not mention `.log` files in the context of `.json` file checks. Clarity issue.
**Suggested fix (Phase 4):** Restate the skip condition as: "Skip files whose basename ends in `_meta` (sidecars) or starts with `_smoke_test` (log files are `.log`, not `.json`, so this pattern is a belt-and-suspenders guard)."

---

### F-11 — VIZ-V11 pre-save lint is described as a manual Vera procedure but no implementation script is referenced (WARN)

**Rule/section:** VIZ-V11 "Producer validation (Vera, pre-save lint)" (lines 1109–1117)
**Problem:** VIZ-V11 mandates a pre-save lint that extracts every concrete color from a Plotly figure and compares it to the registered palette. This is described as a blocking check ("blocks the save with a clear error"), but unlike VIZ-IC1 (which references `validate_intra_chart_consistency()`), VIZ-V5 (which references `_smoke_test_{YYYYMMDD}.log`), and VIZ-DP1 (which provides full Python code), VIZ-V11 does not name a script, helper function, or reference implementation. The rule also mentions `scripts/viz_ic1_check.py` was flagged as a P4 follow-up in the session notes (Wave 10F cross-review), but this script does not appear to be referenced from the SOP either.
**Severity proposal:** WARN — the check cannot be reproduced without a reference implementation, making it a paper rule. The session notes flagged this as a top-5 priority fix.
**Suggested fix (Phase 4):** Add a `scripts/viz_v11_palette_lint.py` reference to VIZ-V11, analogous to VIZ-DP1's inline code. Alternatively, confirm VIZ-IC1 check 4 (palette registry conformance) is the implementation vehicle and make that cross-reference explicit.

---

### F-12 — Indicator Evaluation Framework section uses non-canonical filename pattern (WARN)

**Rule/section:** Indicator Evaluation Framework → "Follow standard chart naming:" (line 1467)
**Problem:** The Indicator Evaluation Framework section states: "Follow standard chart naming: `{pair_id}_env_radar.json`, `{pair_id}_strategy_radar.json`." This naming includes the `pair_id` prefix in the filename, which VIZ-A3/VIZ-NM1 explicitly prohibits: "Do NOT prefix the pair_id into the filename — the pair_id lives in the directory path, not the filename." The correct canonical paths would be `env_radar.json` and `strategy_radar.json` at `output/charts/{pair_id}/plotly/`.
**Severity proposal:** WARN — the contradiction is buried in a secondary section that may not be in active use, but if a generator were built from this spec it would produce pair-prefixed filenames that fail GATE at handoff.
**Suggested fix (Phase 4):** Correct to `env_radar.json` and `strategy_radar.json` (bare names) with the note that pair_id is in the directory path per VIZ-NM1.

---

### F-13 — "Perceptual render" and "disposition" are used without definition sections (WARN)

**Rule/section:** Throughout SOP, terms introduced without a definitions block.
**Problem:** The SOP uses several technical terms that are project-specific and have precise meaning but are never formally defined in a "Definitions" or "Glossary" section:
- **"perceptual render"** / **"perceptual PNG"** — introduced in VIZ-V2 but never defined. Understood from context (kaleido PNG render), but a new Vera would need to infer the term.
- **"disposition"** — used from VIZ-O1 onward; defined implicitly by its three enum values in that rule's table, but not in a definitions section or upfront glossary.
- **"exploration zone"** — defined inline in VIZ-E1 but a formal definition block would improve navigability.
- **"kaleido PNG"** — used interchangeably with "perceptual render PNG"; the kaleido library is not introduced before its first use in V2.

The SOP has no top-level "Definitions" section. This is a navigability and onboarding gap.
**Severity proposal:** WARN — no logical contradiction, but the absence of a definitions section makes the SOP harder to onboard from cold start.
**Suggested fix (Phase 4):** Add a brief "Key Definitions" section after the Identity block, covering: perceptual render, disposition, exploration zone, kaleido, VIZ-CV1, canonical filename, sidecar.

---

### F-14 — VIZ-V11 grandfathering clause contradicts VIZ-V5 smoke check requirement (WARN)

**Rule/section:** VIZ-V11 "Legacy charts" (line 1117) vs. VIZ-V5 (line 1121)
**Problem:** VIZ-V11 states: "Legacy charts that cannot be rebuilt immediately may be grandfathered by declaring `palette_id: 'matplotlib_legacy'`... but the lint still reports them as audit-flagged until rebuilt." VIZ-V5 (line 1121) then says: "A chart whose sidecar has no `palette_id`, or whose `palette_id` is not in the registry, fails VIZ-V5 chart rendering validation (VIZ-CV1)."

The grandfathering clause implies `matplotlib_legacy` is an accepted value in the registry and won't fail VIZ-CV1. But the VIZ-V5 text says "whose `palette_id` is not in the registry" — if `matplotlib_legacy` is not registered in `color_palette_registry.json`, the chart would fail VIZ-CV1. The SOP doesn't confirm whether `matplotlib_legacy` is a registered palette ID.
**Severity proposal:** WARN — if `matplotlib_legacy` is not in the registry file, grandfathered charts fail VIZ-CV1 despite the grandfathering clause, making the clause toothless and the rule contradictory.
**Suggested fix (Phase 4):** Clarify that `matplotlib_legacy` MUST be registered in `color_palette_registry.json` (even as a named exception-palette) for the grandfathering clause to work with VIZ-CV1. Alternatively, specify that VIZ-CV1 accepts `matplotlib_legacy` as a special sentinel without registry lookup.

---

### F-15 — VIZ-ZOOM1 `episode_registry.json` reference does not match VIZ-V12 registry name (WARN)

**Rule/section:** VIZ-ZOOM1 "Episode selection for zoom charts" (line 637) vs. VIZ-V12 (line 1125)
**Problem:** VIZ-ZOOM1 says: "Read from `docs/schemas/episode_registry.json` keyed on `interpretation_metadata.indicator_category`." VIZ-V12 defines the authoritative events registry as `docs/schemas/history_zoom_events_registry.json`. These are two different file names. The SOP does not clarify whether `episode_registry.json` and `history_zoom_events_registry.json` are the same file (renamed), two different files with different content, or whether `episode_registry.json` is an as-yet uncreated file.

VIZ-HZE1 also references: "Read `docs/schemas/episode_registry.json`, find the entry keyed on the pair's `interpretation_metadata.indicator_category`" — the same potentially non-existent file.
**Severity proposal:** WARN — if the two registry names refer to different files, VIZ-ZOOM1/VIZ-HZE1 and VIZ-V12 have different authoritative sources for episode data. If they're the same file, one of the names is wrong. Either way, the SOP is ambiguous.
**Suggested fix (Phase 4):** Resolve whether `episode_registry.json` is an alias for `history_zoom_events_registry.json` or a separate file (with `indicator_category` keying). Update VIZ-ZOOM1 and VIZ-HZE1 to use the same file name as VIZ-V12.

---

## Strengths Worth Preserving

1. **VIZ-DP1 inline Python code** — providing the full `check_dual_panel_axis_assignment()` implementation directly in the rule text is exemplary. No ambiguity about what "verify axis assignments" means. Other rules (VIZ-V11, VIZ-IC1) should adopt the same pattern.

2. **VIZ-HZE1 skip protocol** — the structured skip-entry format with `reason`, `episode_slug`, `skipped_by`, and `wave` fields is specific, auditable, and prevents silent omissions from being confused with production failures. This is the right level of formalism for a gate with high consequence.

3. **Three-tier handoff pathway model** (Econ-to-Viz, Data-to-Viz, Research-to-Viz) — explicit, covers real workflows, and names the non-standard paths (direct-from-Dana, annotation-from-Ray) that would otherwise cause coordination failures. The Acknowledgment Template complements this well.

4. **VIZ-O1 disposition mandate** — the three-enum model (`consumed`, `suggested`, `retired`) is exhaustive, mutually exclusive, and closes the chart-evaporation gap cleanly. The requirement that every chart in the output directory have a disposition sidecar is unambiguous.

5. **Annotation strategy registry (VIZ-V13)** — the named strategy approach (`descending_stair`, `top_right_uniform`, `alternating_top_bottom`) makes annotation layouts reproducible across Vera instances. The `manual_override` requirement for hand-tuned layouts with a regression_note entry is the right escape hatch.

6. **VIZ-V2 subplot handling rule** — the explicit "total shape count = n_recessions × n_panels" formulation removes all ambiguity about multi-panel NBER shading. The example failure case (HY-IG v2 hero) is instructive.

7. **Rule A4 regression report structure** — requiring a side-by-side old-spec → new-spec table for every changed chart on a rerun is strong discipline that makes visual regressions auditable.

8. **VIZ-IC1 six-check structure** — even though VIZ-IC1 is not yet registered in standards.md and missing a source-note check, the six-check enumeration (title-axes, legend-data, annotations-data, palette, unit discipline, narrative-alignment note) is well-reasoned and covers the common pre-save failure modes.

---

## Items Deferred to Phase 3 Cross-Review

1. **GATE-VIZ-NBER2 uses `dot_com` slug** — the status-board entry for Quincy's GATE-VIZ-NBER2 implementation hardcodes `dot_com` (with underscore), conflicting with VIZ-V12's registered `dotcom` slug. Quincy owns the QA SOP; this is a cross-agent slug-naming consistency issue.

2. **APP-PT2 only informally defined** — VIZ-O1 and VIZ-E1 cross-reference APP-PT2 (Methodology page Exploratory Insights renderer) extensively, but APP-PT2 does not appear in the Ace SOP or standards.md as a named rule. Ace owns APP-PT2; needs verification in Phase 3.

3. **APP-EP4 placeholder vs VIZ-HZE1 skip protocol tension** — VIZ-HZE1 mandates a structured skip entry in `_meta.json` when a zoom chart is omitted for data-coverage reasons. Ace's APP-EP4 / GATE-25 placeholder behavior applies when a chart file is missing. The two protocols cover different causes (data gap vs. chart-not-built), but the SOP does not clarify how Ace distinguishes between a VIZ-HZE1-authorized skip and an unintentional missing chart. Cross-review needed with Ace SOP.

4. **VIZ-CP1 standards.md entry mismatch** — the sop-changelog entry for 2026-05-08 says VIZ-CP1 in standards.md was corrected to refer to cross-period chart consistency. The current standards.md entry reads "Cross-Period Consistency Chart Types — current/reference and cross-period comparisons must use registry-approved chart types...". The SOP VIZ-CP1 rule defines 5 specific chart types with detailed specs. Whether standards.md adequately represents VIZ-CP1 is a cross-review item for Lead standards maintenance.

5. **`ukraine` episode slug produced in Wave 10J but not in canonical registry** — Session notes show `ukraine` zoom charts were produced for several pairs. VIZ-ZOOM1 lists only `dotcom`, `gfc`, `covid`, `inflation_2022`. If `ukraine` charts were produced and committed, they either need registry promotion or a skip/retire protocol. This requires Lead visibility.

6. **Ray's narrative missing-chart-gap request protocol (VIZ-SOP §Chart-gap requests from Research Ray)** — this section requires Vera to update Ray's `chart_status` field. The Research SOP's `chart_status` field definition should be cross-checked in Phase 3 to confirm the two SOPs use the same field schema.

---

*Written: 2026-05-08 — Phase 1 intra-SOP review (no SOP edits)*
