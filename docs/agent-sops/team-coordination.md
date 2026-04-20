# Team Coordination Protocol

## Overview

This document defines how agents on the AIG-RLIC+ team coordinate work, hand off outputs, and resolve issues. All agents should read this document at session start alongside their individual SOP.

## Team Structure

```
                       Lesandro (Lead Analyst)
                    ┌────────┼────────┐
                    │        │        │
              ┌─────┴──┐  ┌─┴───┐  ┌─┴──────────┐
              │Research │  │Data │  │Econometrics │
              │  Ray    │  │Dana │  │   Evan      │
              └────┬────┘  └──┬──┘  └──────┬──────┘
                   │          │            │
                   │          └─────┬──────┘
                   │          ┌─────┴──────┐
                   │          │Visualization│
                   │          │    Vera     │
                   │          └──────┬──────┘
                   │                 │
                   └────────┬────────┘
                       ┌────┴─────┐
                       │ App Dev  │
                       │   Ace    │
                       └─────┬────┘
                             │
                       ┌─────┴─────┐
                       │    QA     │
                       │  Quincy   │
                       └───────────┘
```

**Lesandro** (lead) assigns tasks, reviews outputs, and makes final decisions on methodology and interpretation.
**Ace** (app dev) is the integration point — assembles all outputs into the Streamlit portal.
**Quincy** (QA) is the independent verifier — audits every producer's self-report, exercises the portal as a stakeholder, and holds the acceptance gate until evidence is on the table. Per `docs/agent-sops/qa-agent-sop.md`, Quincy runs AFTER all producers and BEFORE Lead acceptance sign-off; GATE-31 makes Quincy's sign-off mandatory.

## Standard Task Flow

A typical analysis follows this sequence:

```
1. Lesandro frames the question and creates tasks
2. Research agent gathers literature and context    ──┐
3. Data agent sources and cleans datasets            ──┤ (parallel)
4. Econometrics agent specifies and estimates models  ←┘ (after 2 & 3)
5. Visualization agent produces charts and tables     ← (after 4)
6. App dev assembles portal with narrative + visuals  ← (after 5, with input from 2 & 3)
7. Each producer self-verifies per META-SRV           ← (each producer at handoff)
8. Browser verification (headless inspect + fix)      ← (after 6)
9. Deliverables completeness gate                     ← (after 8)
10. QA (Quincy) runs independent verification         ← (after 9, per GATE-31)
11. Lesandro signs off on rule-compliance in acceptance.md
12. MRA: Measure, Review, Adjust                      ← (after 11)
13. Stakeholder review (final gate per META-RPT)
14. Lesandro tags the pair reference and delivers
```

Steps 2 and 3 run in parallel. Steps 4, 5, and 6 are sequential dependencies.
Ace can begin scaffolding the portal structure during steps 2-4 while waiting for final outputs.

**Producer → QA → Lead → Stakeholder pipeline (summary).**

1. Producer agents (Dana / Evan / Vera / Ray / Ace) complete their work and each files a regression-note section with META-SRV evidence blocks (first line of defense).
2. Lead coordinates producer handoffs and reviews rule-compliance at each wave.
3. **QA (Quincy) runs independent verification (second line, per `docs/agent-sops/qa-agent-sop.md`)** — re-runs every verification command, audits cross-agent seams, runs Cloud smoke on reference pairs, files findings in regression-note and acceptance.md.
4. `acceptance.md` sign-off requires QA sign-off per GATE-31. Lead cannot sign without QA's findings block in place.
5. Stakeholder review is the final gate (per META-RPT) and gates the promotion of `<pair_id>-reference-candidate` to `<pair_id>-reference`.

## Deliverables Completeness Gate (Step 8)

After browser verification confirms rendering quality, verify that **all deliverables exist** by reconciling against the Analysis Brief Section 9 checklist.

### Why This Is Mandatory

Pair #2 (TED Variants) shipped without a Methodology page because:
- The Analysis Brief listed 4 portal pages, but no one verified all 4 were created
- Browser verification checked rendering quality, not content completeness
- The developer consciously skipped Methodology as a "shortcut" — which a completeness gate would have caught

### Minimum Deliverables Per Pair

Every completed pair must have **all** of the following. Missing any one blocks completion.

| # | Deliverable | Verify How |
|---|------------|-----------|
| 1 | Analysis Brief | `docs/analysis_brief_{id}_{date}.md` exists |
| 2 | Master dataset | `data/{id}_*.parquet` exists, row count > 0 |
| 3 | Stationarity tests | `results/{id}/stationarity_tests_*.csv` exists |
| 4 | Interpretation metadata | `results/{id}/interpretation_metadata.json` exists |
| 5 | Exploratory results | `results/{id}/exploratory_*/correlations.csv` exists |
| 6 | Core model results | `results/{id}/core_models_*/*.csv` — at least 3 files |
| 7 | Tournament results | `results/{id}/tournament_results_*.csv` exists, rows > 0 |
| 8 | Charts | `output/charts/{id}/plotly/*.json` — at least 5 files |
| 9 | Portal: Story page | `app/pages/*_{id}_story.py` or shared page exists |
| 10 | Portal: Evidence page | `app/pages/*_{id}_evidence.py` or shared page exists |
| 11 | Portal: Strategy page | `app/pages/*_{id}_strategy.py` or shared page exists |
| 12 | Portal: Methodology page | `app/pages/*_{id}_methodology.py` or shared page exists |
| 13 | Sidebar navigation | Finding appears in sidebar dropdown |
| 14 | Landing card | Pair appears in dashboard card grid |
| 15 | Catalog status | `docs/priority-combinations-catalog.md` updated to "Completed" |
| 16 | Winner summary | `results/{id}/winner_summary.json` exists, all required fields populated (signal, threshold, strategy display names, OOS metrics) |
| 17 | Winner trade log | `results/{id}/winner_trade_log.csv` exists, rows > 0, columns: `entry_date`, `exit_date`, `direction`, `holding_days`, `trade_return_pct` |
| 18 | Execution notes | `results/{id}/execution_notes.md` exists, non-empty, includes step-by-step execution guidance |
| 19 | `indicator_nature` populated | `results/{id}/interpretation_metadata.json` has `indicator_nature` set to one of `leading`, `coincident`, `lagging`. Missing/empty/`unknown` → pair fails gate. **Owner:** Data Dana |
| 20 | `indicator_type` populated | `results/{id}/interpretation_metadata.json` has `indicator_type` set to EXACTLY one of the canonical 7 values: `price`, `production`, `sentiment`, `rates`, `credit`, `volatility`, `macro`. Near-synonyms (`activity`, `output`, `vol`, `fx`) are REJECTED — map to the canonical value at source. Missing/empty/`unknown` → pair fails gate. **Owner:** Data Dana |
| 21 | `strategy_objective` populated | `results/{id}/interpretation_metadata.json` has `strategy_objective` set to one of `min_mdd`, `max_sharpe`, `max_return`. Missing/empty/`unknown` → pair fails gate. **Owner:** Research Ray (after tournament results known) |
| 22 | Method coverage — no regression | On a pair rerun, the new Evidence section must include every method from the prior version OR the pair includes a `regression_note.md` documenting each drop with rationale. Missing methods without a regression note → pair fails gate. **Owners:** Evan (produces data), Ray (writes narrative), Ace (renders page) |
| 23 | Pair acceptance.md | `results/{id}/acceptance.md` exists with every Portal-Wide Quality Checklist item checked, reference pair comparison documented (see Reference Pair Doctrine), and Lead sign-off. Missing/incomplete → pair fails gate. **Owner:** Lead Lesandro |
| 24 | Chart-Text Coherence Audit | When any chart is modified (axis, labels, values, signal, scale), author must `grep -r "<chart_name>" app/pages/` and update every referenced caption/narrative in the **same commit**. The pair's `regression_note_<date>.md` must list BOTH the chart change AND the narrative change together under a single bullet. Missing narrative diff for a recent chart edit blocks acceptance.md sign-off. **Ownership (clarification, 2026-04-19):** When a chart is modified, **Vera initiates an explicit notification** to Ray at handoff ("chart {name} updated — please re-audit {page} captions"). **Ray proactively diffs** prior narrative against new chart catalog on every rerun, independent of whether Vera signaled. Both responsibilities apply — the notification is the fast path, the proactive diff is the safety net. **Addresses SL-3.** **Owners:** Vera (chart) + Ray (narrative), Ace (render verification) |
| 25 | No Silent Chart Fallbacks | Pages must not silently substitute a different chart when the intended canonical artifact is missing. If the canonical chart for a method does not exist, the page renders a labeled "chart pending" placeholder with an explanation — **never** a lookalike from a different method. acceptance.md must list every method → chart mapping and verify each chart is canonical (not borrowed). Cross-reference: VIZ-V3. **Addresses S18-11.** **Owners:** Vera (canonical artifact), Ace (render path), Lesandro (gate check) |
| 26 | No Silent Content Drops | When a previously-present analysis element (table, chart, subsection, callout) is removed on a rerun or new version, `regression_note_<date>.md` must include an explicit **Removed** section with rationale per item. If no rationale is provided, the content must be restored. Applies across versions of the same pair (e.g., HY-IG v2 losing content that HY-IG v1 had). Cross-reference: VIZ-V4, RES-5. acceptance.md must include a prior-version inventory diff (see "Prior-Version Inventory Check" below). **Addresses S18-8, SL-2, and the silent-content-drop meta-pattern.** **Owners:** Evan + Ray + Ace (producers), Lesandro (gate) |
| 27 | End-to-End Chart Render Test | Every chart referenced by any portal page of a pair under acceptance must: (a) load successfully via `load_plotly_chart(name, pair_id)` and return a non-None Figure object; (b) have at least one data trace; (c) have a non-empty title. Enforcement: Vera runs VIZ-V5 smoke tests on all canonical artifacts; Ace runs a loader smoke-test extension of Defense-2 that exercises `load_plotly_chart()` for every chart referenced by every portal page of the pair. Both agents submit their smoke-test logs as part of acceptance.md. **Blocking:** any chart failing the smoke test blocks acceptance until fixed. **Addresses** the Dot-Com canonical zoom bug where the file existed, the path resolved, and the loader still returned None — a failure mode invisible to file-existence checks alone. **Owners:** Vera (canonical artifacts) + Ace (loader + portal), Lesandro (gate). |
| 28 | Reference-Pair Placeholder Prohibition | On reference-pair pages (see Reference Pair Doctrine), any "chart pending" placeholder (the GATE-25 graceful fallback) is an **acceptance blocker**. Graceful degradation is appropriate for non-reference pairs under development; reference pairs are the gold standard and must render 100% of referenced charts. acceptance.md must assert: zero `chart_pending` placeholders in rendered page DOM, verified via headless-browser DOM audit over every portal page of the reference pair. **Addresses** the gate-level gap that allowed "chart pending" to pass Wave 3 verification on a reference pair. **Owners:** Ace (portal audit) + Lesandro (gate). |
| 29 | Clean-Checkout Deployment Test | Before acceptance, the pair's portal must pass a smoke test run in a **clean checkout that respects `.gitignore`** — a simulation of Streamlit Cloud's deployment environment. Implementation: `git clone --depth 1 "$(git rev-parse --show-toplevel)" /tmp/clean_checkout_{pair_id}` then `cd /tmp/clean_checkout_{pair_id}` then `python3 app/_smoke_tests/smoke_loader.py --pair-id {pair_id}`. Any file referenced by `app/` code that exists in the working tree but NOT in the clean checkout = gate failure (indicates a silent gitignore exclusion or missing `git add -f`). Blocks acceptance for reference pairs. Rationale: `GATE-27` validates rendering in the dev env; `GATE-29` validates deployability. Cross-reference: `ECON-DS2` (Deploy-Required Artifact Allowlist) is the producer-side counterpart; `APP-ST1` is the reusable smoke-test harness. This gate catches the class of bug "works on my laptop, breaks on Cloud" — the symptom is usually a `FileNotFoundError` or `cannot render` error on a deployed page. **Owners:** Ace (smoke test execution) + Lesandro (gate). |
| 30 | Deflection Link Audit | Triggered whenever a stakeholder-feedback item (Sxx-y / SL-n) is closed in `acceptance.md` by deflecting to another page/section rather than by an in-place fix. Rule: (a) the resolution text must explicitly name the target page AND the target section/anchor; (b) the target page/section is **blocking-verified** to exist AND to contain the content claimed — headless-browser DOM assertion on the target anchor and a content-presence assertion on the text that addresses the stakeholder's concern; (c) **Lead sign-off is required** on every deflection-style resolution — agents cannot close a deflection item unilaterally; (d) if the target page is later renamed or restructured, **every deflection reference that pointed at it is automatically re-opened** for re-audit (meta-rule: deflection is a contract between the resolution and the target page, not a one-shot fix). Example: S18-2 (Market Regime section) was closed by deflecting to the Story page regime explainer. GATE-30 requires: (1) the Story page regime explainer exists; (2) it addresses S18-2's concern; (3) if the Story page is later renamed or restructured, S18-2 returns to open status automatically. **Addresses** the Wave-5 audit finding that S18-2 and S18-4 were closed by deflection with no mechanical assertion that the deflection target renders or contains the referenced content. **Owners:** Ace (DOM audit) + Lead Lesandro (sign-off). |
| 31 | Independent QA Verification (Blocking) | Every `acceptance.md` sign-off must have a QA Verification section authored by Quincy per `docs/agent-sops/qa-agent-sop.md`, with at least one finding recorded per mandated category: **(a) artifact verification** (claim-evidence cross-check on every regression-note bullet); **(b) smoke tests** (`smoke_loader.py` + `smoke_schema_consumers.py` exit-0 logs); **(c) stakeholder-spirit check** (every S-item claimed resolved is re-read as the stakeholder); **(d) cross-agent seam audit** (GATE-24/25/26/28/30 + APP-DIR1 + META-XVC cross-version diff). Zero findings = QA wasn't looking; at least one PASS-with-note observation is required per wave even if nothing blocks. Any **FAIL** finding blocks acceptance until producer fix + QA re-verification; Lead override is allowed but requires a rationale block in `docs/pair_execution_history.md` "QA Override Log" section (mirrors META-FRD). Makes QA involvement mandatory, not optional. **Addresses** the Wave-5 reflection finding that producer self-reports were signed off without independent re-verification — unlocking a silent-drift class that META-SRV formalizes at the producer side. **Owners:** Quincy (authors findings) + Lead Lesandro (accepts sign-off / logs override). Added 2026-04-19 (Wave 6A). Cross-ref META-SRV, META-AL, META-RPD, GATE-23..30. |

**Evidence:** HY-IG (pair #5) shipped with a header-only trade log (0 data rows) because items 16–18 were not in the completeness gate. The downstream execution panel showed "Trade log pending" with no data. Nobody caught it until manual inspection.

**Evidence for item 22:** HY-IG v2 (rerun) silently dropped pre-whitened CCF, transfer entropy, and quartile-returns analysis from the Evidence page. These methods existed in v1 but were missing from v2 because Evan's rerun omitted them and Ray wrote the new narrative without comparing to the prior version. A stakeholder caught the regression; the completeness gate did not.

### Tournament Winner JSON Schema

Every pair must produce `results/<pair_id>/tournament_winner.json` with this schema:

```json
{
  "pair_id": "string",
  "winner": {
    "signal": "string",
    "threshold": "string",
    "strategy": "string",
    "oos_sharpe": "number",
    "oos_ann_return": "number",
    "max_drawdown": "number",
    "annual_turnover": "number"
  },
  "benchmark": {
    "name": "Buy & Hold",
    "oos_sharpe": "number",
    "oos_ann_return": "number",
    "max_drawdown": "number"
  },
  "deltas": {
    "delta_sharpe": "number",
    "delta_return": "number",
    "delta_max_drawdown": "number"
  },
  "suggested_strategy_objective": "min_mdd|max_sharpe|max_return"
}
```

`deltas` values are computed as winner minus benchmark (e.g., `delta_sharpe = winner.oos_sharpe - benchmark.oos_sharpe`).

**Owners:** Evan produces it at tournament completion. Ray reads `deltas` and `suggested_strategy_objective` to set the canonical `strategy_objective` in `interpretation_metadata.json` (may override with rationale). Vera and Ace read the schema for rendering.

### "Unknown" Is Not a Display State

> "Unknown" classification is an error signal, not a fallback label. If a pair ships with any classification field set to "unknown," it means upstream work was incomplete. The remedy is to fix the gap at source (Data Dana for data-stage fields, Research Ray for narrative-stage fields) — NOT to accept the label as final.
>
> The runtime fallback in `pair_registry.py` is a safety net that warns via `get_integrity_issues()` — it is not a license to ship incomplete pairs. Gate reviewers MUST reject any pair flagged by the integrity check before delivery.

### Explicit Over Implicit (Meta-Rule)

> **Silent changes are unacceptable.**
>
> Every deliberate deviation from (a) the Standard Chart Catalog (Viz SOP Rule A3), (b) the category-specific mandatory method list (Econometrics SOP Rule C1), (c) a prior version of the same pair, or (d) default unit/scale conventions (Viz SOP Rule A2, Research SOP Rule 4) must be documented in a `design_note.md` or `regression_note.md` as part of the pair's deliverables. If an agent changes something without documenting it, gate reviewers must reject the delivery.
>
> This meta-rule is the organizing principle behind gate items 19–22: classification metadata must be explicit (§19–21), and method/chart coverage must be explicit (§22). The common failure pattern is the same in every case: whenever the portal would show "unknown," drop a method without notice, or silently deviate from a convention, the system failed to capture a required decision. **Fix at source, don't paper over at runtime.**

### Regression Note Format

**Path:** `results/<pair_id>/regression_note_<YYYYMMDD>.md`

**Required sections:**

#### Changes From Prior Version
List every deliberate change, one per bullet. Include:
- What changed (file, field, column, method, chart spec)
- Old value → New value
- Why the change was made (new data, bug fix, stakeholder request)

#### Approved By
Name of the Lead (or designated reviewer) who approved each change before delivery.

#### Unchanged
Brief confirmation that all other methods, charts, columns, and metadata match the prior version. If any silent drift is discovered later, this section is the first thing auditors check.

#### Impact Assessment
One paragraph per change on how it affects downstream consumers (Evan, Ray, Ace, portal users).

#### Removed
List every element (table, chart, subsection, callout, KPI, annotation) that was present in the prior version but is absent in this version. Each entry states:
- What was removed (path, chart_name, section title)
- Why (data now invalid, method retired, stakeholder request, scope reduction)
- Approver and date

This section is the canonical mechanism for declaring intentional removals and is the companion gate to GATE-26. If the section is empty on a rerun, auditors must be able to confirm the prior version's inventory is fully preserved.

**When to write:** On every pair rerun, BEFORE handoff to the next agent in the chain. If there are no deliberate changes, still write the file with "No deliberate changes from prior version" in the Changes section — silence is not acceptance.

### Version-to-Version Content Continuity (Meta-Rule META-VNC)

> **Iterations must be additive or explicitly substitutive — never silently subtractive.**
>
> Every revision of a pair (v1 → v2 → v3) must preserve the prior version's inventory unless a removal is declared in the `regression_note_<date>.md` **Removed** section with rationale. The **Removed** section is the canonical mechanism for declaring intentional removals.
>
> **Content continuity applies across iterations AND across environments (dev → Cloud). An artifact that works locally but doesn't survive a clean checkout is the same class of bug as an artifact silently dropped across iterations — both are violations of META-VNC.** Operationalized across environments by GATE-29 (Clean-Checkout Deployment Test) and ECON-DS2 (Deploy-Required Artifact Allowlist).
>
> Companion to META-RNF (Regression Note Format) and META-SC (Source Citation / upstream attribution). Operationalized by GATE-24 (chart-text coherence), GATE-25 (no silent chart fallbacks), GATE-26 (no silent content drops), and GATE-29 (clean-checkout deployment test).
>
> Applies to all 5 agents (Dana, Evan, Ray, Vera, Ace). Every producer is accountable for the elements they authored or rendered in the prior version.

### Historical Episode Chart Strategy (Meta-Rule META-ZI)

> **Canonical layer is metadata, not pixels. Every pair renders its own dual-panel zoom chart from the shared events registry plus its own indicator + target data.**
>
> Historical episodes (Dot-Com, GFC, COVID, 2018 taper, 2022 inflation shock, etc.) appear in multiple pairs' narratives. The shared, canonical contribution is the **event metadata** (slug, date window, event dates, labels, citations); the **rendered chart** is always pair-specific because it depends on the pair's indicator and target.

**Refined Wave 6B (2026-04-19) per META-AL.** The prior model (canonical rendered chart at `output/_comparison/history_zoom_{episode}.json` with per-pair override) is **superseded**. A rendered chart contains pair-specific data (indicator trace, spread values, HMM overlays) and therefore cannot be "canonical" in the META-AL sense — a pair whose own chart was missing would silently read another pair's overlay data. That failure mode is foreclosed by removing the fallback entirely.

**Canonical (metadata-only) layer:**
- `docs/schemas/history_zoom_events_registry.json` (VIZ-V12) — authoritative episode slugs, date windows, event dates, labels, and source citations. Owner: Vera.
- VIZ-V11 palette (trace colors, NBER rgba) and VIZ-V2 NBER shading rules — canonical styling.
- Slug list (extend via PR to the registry): `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022`.

**Per-pair rendered layer (mandatory, dual-panel):**
- Location: `output/charts/{pair_id}/plotly/history_zoom_{episode_slug}.json`.
- Construction: each pair renders its own chart from the canonical events + the pair's indicator + target series. VIZ-V1 mandates the dual-panel layout (indicator on top, target on bottom; shared x-axis; event annotations + NBER shading on both subplots).
- There is **no** canonical rendered chart to "start from" and no `output/_comparison/` fallback — a pair either ships its own dual-panel chart or it ships a GATE-25 "chart pending" placeholder. For reference pairs (GATE-28), the placeholder path is a drill, not a shipped state.

**Loader contract (Ace, Wave 6B):**
1. Try `output/charts/{pair_id}/plotly/history_zoom_{episode}.json`.
2. If missing → "chart pending" placeholder per GATE-25. No `_comparison/` fallback.

**Cross-references:** META-AL (supersedes canonical-rendered-chart fallback), VIZ-V1 (dual-panel mandate, refined Wave 6B), VIZ-V12 (events registry — canonical metadata), VIZ-V11 (palette), VIZ-V2 (NBER shading), GATE-25 (missing-chart placeholder), GATE-28 (reference pairs have zero placeholders).

**Why this rule exists:** Cross-pair consistency of *events* is free and enforced by the registry; consistency of *rendered chart styling* is free via the palette + dual-panel template; what cannot be made canonical is the rendered data, because it is by construction pair-specific. The old override-with-fallback model saved zero marginal work (every pair still had to render its own dual-panel anyway) while creating a silent cross-pair data-misrepresentation risk. META-AL forecloses the category error; META-ZI is the applied rule.

### Perceptual Validation of Visual Encoding (Meta-Rule META-PV)

> **A rule that was followed but produced the wrong visual is a broken rule. Fix the rule.**
>
> Any chart element that depends on color, alpha, shading, or low-contrast visual encoding for information transfer must have a **perceptual-validation step** in the producing agent's SOP. Validation requires: render the chart to a PNG via `plotly.io.write_image` and visually confirm the encoding is perceivable against realistic backgrounds and data traces. Assume nothing from numeric prescriptions alone.
>
> Rules that prescribe specific numeric values (alpha ranges, stroke widths, font sizes, marker radii, color saturations) must be validated against perceptual output, not assumed to produce the intended visual. If the PNG shows the encoding as invisible or ambiguous, the numeric prescription is wrong — update the rule, not the individual chart.
>
> **Applies to** (non-exhaustive): NBER recession shading (VIZ-V2), regime shading, sparkline thickness, annotation dot size, event-marker opacity, quartile-color gradients, probability-band fill alpha, confidence-interval ribbon fill.
>
> **Validation artifact:** every chart with perceptual-encoding risk ships a `{chart_name}_preview.png` sidecar alongside the Plotly JSON; the producing agent signs off that the encoding is perceptible in the PNG before handoff.
>
> **Companion to** META-VNC (no silent drops) and META-RNF (regression note format). Operationalized by VIZ-V2 (NBER shading), VIZ-V4 (diagnostic charts), GATE-27 (end-to-end render test).
>
> **Addresses** the Wave-2 Hero NBER shading bug: VIZ-V2 prescribed "alpha 0.10–0.15 grey" and the producer complied exactly; the rendered shading was still imperceptible against the dark line trace on a light background. The rule was followed and the visual failed — that is a broken rule, not a broken chart.

### Cross-Version Discipline (Meta-Rule META-XVC)

> **When producing v2+ of a pair, each agent must observe the prior version and attempt to maintain methodological consistency. Improvements are encouraged when supported by strong reasons. Silent divergence is prohibited; documented divergence is welcome.**

Extends META-VNC beyond content-drops to method-drifts. Honors the "Explicit Over Implicit" meta-principle: across versions of the same pair, every method choice that differs from the prior version is either (a) matched to the prior and confirmed silently, or (b) deliberately diverged with full documentation. There is no third option.

**Observation step (mandatory before authoring any v2+ artifact):**

1. Agent reads the prior version's artifact (e.g. v1 of the same pair, or the reference pair's analogous artifact if this is a new-pair dispatch per META-RPD).
2. Agent records "what the prior version did" in `results/{pair_id}/regression_note_{date}.md` under a new `### Prior-version observation` subsection. Minimum content: method family used, key parameters (lags, lookbacks, thresholds), signal definition, chart style.
3. **Default behavior: match prior.** Matching the prior version is silent — no divergence paperwork, no SOP ceremony. The observation subsection alone proves the observation step was performed.

**Justified divergence (optional, heavily documented):**

When an agent deliberately departs from the prior version, `regression_note_{date}.md` must carry a `### Methodological divergence` block for each departure. The block has six required fields:

| Field | Content |
|-------|---------|
| Prior method | Exact method + parameters used in the prior version |
| New method | Exact method + parameters used in this version |
| Strong reason | Why the new method is better — bug fix, stakeholder request, new data, improved theory |
| Expected impact | Qualitative (what changes in outputs) AND quantitative (approximate magnitude of the change in headline metrics) |
| Validation | How the agent verified this is an improvement, not a regression — a/b comparison, stakeholder sign-off, literature citation |
| Cross-reference | Pointer to stakeholder feedback item (Sxx-y / SL-n), commit hash, or design note that authorizes the divergence |

**Traceability:**

- Divergence entries appear in BOTH `regression_note_{date}.md` AND the pair's `acceptance.md` (under a new "Methodological divergence from prior version" subsection, parallel to the existing "Prior-Version Inventory Check").
- The chain is preserved across versions: v3's divergences cite v2's divergences (or note "matches v2"); v2's divergences cite v1 or the reference pair; v1 cites the Analysis Brief.

**Applies to:** all 5 agents. Dana on data transformations; Evan on method specifications; Ray on narrative structure; Vera on chart specs; Ace on rendering patterns.

**Cross-reference:** META-VNC (content continuity), META-RNF (regression note format), META-RPD (reference pair doctrine — the reference pair is the v0 baseline for new-pair dispatches), META-RPT (tagging — the `<pair_id>-reference` tag identifies the baseline each v2+ observes against).

**Why this rule exists:** The Wave-5 audit revealed that "method drift between v1 and v2" was a latent class of regression that META-VNC covered at the content level (charts, tables, subsections) but not at the method level. If v1 used HMM with 2 states and v2 uses HMM with 3 states, v1's content may still be preserved while the comparison is apples-to-oranges. META-XVC forces that comparison to be explicit — either matched or deliberately diverged.

### Force-Redeploy Discipline (Meta-Rule META-FRD)

> **Streamlit Cloud occasionally serves stale code after a `git push` even though HEAD on the remote matches HEAD locally. The operationally-accepted fix is a trivial "no-op" commit (docstring bump, one-line comment) that forces Cloud to rebuild fresh. This rule codifies when and how that fix is permitted.**

**Trigger:**

A force-redeploy commit is permitted only when:

1. The Lead has observed (via Playwright inspection or equivalent) that Streamlit Cloud renders a state inconsistent with the current `main` branch HEAD.
2. At least 7 minutes have elapsed since the most recent push, to rule out in-flight deploy latency.

**How:**

A force-redeploy commit must:

1. Be trivial — a docstring bump or a one-line comment in a file Streamlit Cloud's builder will pick up (e.g. `app/components/pair_registry.py`, per precedent set by `42c0ea7` + `1720c0c`). No functional code changes.
2. Be **alone in the commit** — not batched with any other work. Batching hides the force-redeploy intent and breaks the audit trail.
3. Carry a commit message that names the stale-Cloud observation: "Force-redeploy: Cloud serving stale <component>; trivial bump to trigger rebuild. Observed at <timestamp> via <method>."

**Logging:**

Every force-redeploy gets an entry in `docs/pair_execution_history.md` under a "Force-Redeploy Log" section with fields `{commit_sha, trigger_reason, time_to_rebuild, observed_stale_element, lead_initials}`.

**Threshold / escalation:**

If force-redeploy is invoked more than **2x per quarter**, escalate to a root-cause investigation — it may indicate a deeper CI/CD issue (e.g. a `.gitignore`-excluded file the Cloud builder depends on, a Streamlit config mismatch, a cache-invalidation bug). A META-FRD >2x/quarter trigger is a hard signal that META-VNC's cross-environment clause (GATE-29 + ECON-DS2) is not fully closing the reproducibility gap.

**Why this rule exists:** Commit `1720c0c` was a force-redeploy performed without a documented precedent. The Wave-5 audit flagged this as tribal knowledge that future Leads may either (a) not know to use when they need it, or (b) over-use and normalize as routine. META-FRD makes the pattern deliberate, rare, and audited.

**Cross-reference:** META-VNC (cross-environment content continuity), GATE-29 (clean-checkout deploy test), ECON-DS2 (deploy-required artifact allowlist).

### Reference-Pair Tagging Protocol (Meta-Rule META-RPT)

> **The reference-pair tag is how META-RPD (Reference Pair Doctrine) becomes Git-native. This rule codifies the tag lifecycle: when to create, when to freeze, when to version.**

**Tag convention:**

| Tag form | State | Created when |
|----------|-------|--------------|
| `<pair_id>-reference-candidate` | Pre-approval — Lead has signed `acceptance.md` but stakeholder has not yet reviewed | Automatic at Lead sign-off |
| `<pair_id>-reference` | Post-approval — stakeholder-signed, frozen, immutable | Stakeholder approves; Lead creates tag |

**Approval requirements:**

- Stakeholder sign-off is mandatory. "Sign-off" means a named reviewer + date written into the `acceptance.md` "Stakeholder Review" block.
- Lead endorses the stakeholder sign-off and creates the tag.
- Tag is annotated and carries the sign-off text in its body:

    ```
    git tag -a <pair_id>-reference <commit_sha> \
        -m "Stakeholder approved: <reviewer_name> on <YYYY-MM-DD>. Ref: results/<pair_id>/acceptance.md"
    git push origin <pair_id>-reference
    ```

**Frozen property:**

Once `<pair_id>-reference` exists, it is **immutable**. Future work on the pair does not move the tag.

**Evolution (new reference needed):**

When methodology or presentation has evolved enough to warrant a new reference state:

1. Create a new versioned candidate tag on the new commit: e.g. `<pair_id>-v3-reference-candidate`.
2. Run a fresh stakeholder review on the new version.
3. On approval, promote to `<pair_id>-v3-reference`.
4. **The original `<pair_id>-reference` tag stays put** — it remains the historical reference for v1/v2 comparisons, and for any pair that was benchmarked against it.
5. Update `docs/agent-sops/team-coordination.md` §Reference Pair Doctrine to name the new "current" reference, but do not delete the old tag reference.

**Scope of "approval":** single stakeholder review is sufficient (YYY / 土撥鼠C2 / Rex / AF review group count as independent reviewers). No secondary ratification is required unless the Lead explicitly requests it.

**Cross-reference:** META-RPD (Reference Pair Doctrine — the rule that makes the tag meaningful), META-XVC (the tagged reference is the baseline that v2+ observes against).

**Why this rule exists:** Pre-Wave 5, `META-RPD` referred to `hy-ig-v2-reference` as if it existed, but the actual Git tag had never been created, and the procedure for creating it was tribal. META-RPT makes the tag an artifact, not a vague promise.

### Backlog Discipline (Meta-Rule META-BL)

> **Not every proposed rule deserves to ship immediately. Some are deliberately deferred — they solve a real problem but the cost of codification outweighs current benefit, OR the problem hasn't manifested yet at a scale that justifies the overhead. This rule tracks those proposals so they are not lost and not re-derived.**

**Registry file:** `docs/backlog.md`

**Required columns:** `{ID, proposer_agent, proposed_rule_id, motivation, decision, deferred_reason, reactivation_trigger, date}`

**ID format:** `BL-NNN` — a monotonic three-digit counter, starting at `BL-001`. ID is immutable once assigned.

**Review cadence:**

- At EOD (end of each working session), Lead scans the `reactivation_trigger` column for items whose trigger has fired.
- For each fired trigger, Lead either (a) promotes the item to an SOP (deletes from active, strikes through with pointer to SOP section), OR (b) explicitly re-defers (adds a dated note: "Trigger fired but decision unchanged — re-deferred because …").
- Items without a fired trigger stay in place; no action needed.

**Authority:**

- Only the Lead can promote a backlog item to an SOP. Agents propose; Lead decides.
- Agents may add new backlog entries by proposing them in a session; Lead authors the `docs/backlog.md` row with the agreed text.

**Cross-reference:** SOPs, `docs/standards.md`, `docs/sop-changelog.md` — backlog items that are promoted follow the normal rule-addition workflow (text to SOP, entry to changelog, ID registered in standards).

**Why this rule exists:** Without a backlog, proposed-but-deferred rules vanish between sessions. The Lead re-derives them (wasted effort), or worse, the original proposer re-proposes them unaware they were already discussed (friction + inconsistency).

### Schema Consumer Version Contract (Meta-Rule META-SCV)

> **META-CF introduced schema versioning (`x-version: semver`); META-SCV closes the consumer-side gap. When a consumer reads a schema-validated artifact, it must declare the minimum schema version it understands. The validator enforces compatibility.**

**Principle:**

When a consumer (Ace's component, Evan's downstream script, Ray's narrative extractor) reads an artifact claimed to match a schema, the consumer specifies the schema version it was written against. If the producer has bumped to a higher version, the consumer either:

- **Accepts** if the change is additive (minor bump) — the consumer will ignore new fields it doesn't know about, but required fields it relied on are still present.
- **Raises `SchemaVersionMismatch`** if the change is breaking (major bump) — required fields may have been renamed, removed, or re-typed, and silent acceptance would mean silent data corruption.

**Implementation:**

Extend `validate_or_die` and `validate_soft` in `app/components/schema_check.py` (and the parallel helpers in `scripts/validate_schema.py` for non-Streamlit consumers) to accept a `minimum_x_version` parameter:

    data = validate_or_die(path, "winner_summary", minimum_x_version="1.0.0")

Semantics:

| Producer version | Consumer `minimum_x_version` | Result |
|------------------|------------------------------|--------|
| 1.0.0 | 1.0.0 | OK |
| 1.1.0 (additive bump) | 1.0.0 | OK — consumer reads only the 1.0.0-required fields; new fields ignored |
| 1.0.0 | 1.1.0 | **Raise** — consumer expects a field that may not exist yet in 1.0.0 instances |
| 2.0.0 (breaking) | 1.0.0 | **Raise** `SchemaVersionMismatch` — major version mismatch is always breaking |

The rule is: **consumer's `minimum_x_version` major must equal producer's `x-version` major; consumer's minor must be ≤ producer's minor.**

**Documentation requirement:**

Every `validate_or_die` or `validate_soft` call site must pass an explicit `minimum_x_version`. Defaulting to "1.0.0" silently defeats the rule's purpose. If a consumer does not know which version it was written against, that's a bug to fix, not a case for the default.

**Cross-reference:** META-CF (Contract File Standard — introduced versioning), APP-SEV1 (consumer-side validation severity), APP-WS1 (first consumer contract, currently hard-coded to 1.0.0 — migrate on next revision).

**Why this rule exists:** The Wave-5 audit found that if Evan bumps `winner_summary.schema.json` 1.0.0 → 1.1.0 additively, Ace's consumer will silently accept the new instance. That's fine — until a later consumer, written against 1.1.0-only fields, runs against a 1.0.0 instance and gets `KeyError`. META-SCV moves that check from runtime-surprise to validator-blocking.

### User-Facing Technical Flags → Plain English Explanation (Meta-Rule META-ELI5)

> **Every user-visible flag, warning, error, or status message in the portal must be accompanied by a plain-English explanation targeting an educated non-specialist. Technical shorthand is for agents; ELI5 is for stakeholders.**

**Applies to:**

- `st.error` / `st.warning` / `st.info` callouts (all APP-SEV1 severity levels L1/L2/L3).
- Status labels on artifacts (Available / Pending / Validated / Insufficient / Stale / Draft / Mature / Unknown).
- Validation failure messages emitted by `app/components/schema_check.py`.
- "Pending," "unavailable," "chart pending," and other placeholder states.

**Format:**

Every user-facing flag carries two parts:

| Part | Audience | Style |
|------|----------|-------|
| **Technical label** | Agent / auditor — appears in logs, regression notes | Short string, canonical vocabulary (e.g. `oos_status:"insufficient_sample"`) |
| **ELI5 body** | Stakeholder — appears in portal UI | 1-2 sentences, no formulas, no jargon, grounded in everyday analogies |

**Example:**

- Technical: `oos_status:"insufficient_sample"`
- ELI5: "We only have X years of data for this indicator. To reliably judge whether a strategy works rather than appears lucky, we typically need at least Y years of out-of-sample data the model hasn't seen. Below that threshold, apparent success is hard to distinguish from randomness."

**Ownership:**

- The agent producing the flag carries the ELI5 alongside the technical label. If Ace adds a new `st.error` to a component, Ace authors the ELI5.
- **Ray is the editorial owner of user-facing prose** and reviews tone at handoff. Disagreements on phrasing are resolved by Ray; Ray-authored replacements are final.

**Retroactive check (scheduled for Wave 5C):**

Audit every `st.error` / `st.warning` / `st.info` call site in the HY-IG v2 portal code. Each must have an ELI5 sibling. Gaps are remediated before Wave 5C closes.

**Cross-reference:** RES-1 (Audience Assumption — layperson voice), RES-3 (Method Justification — "why we chose this" sentences), APP-SE5 (Universal Takeaway Caption — extends the same audience-friendly principle to charts/tables), APP-SEV1 (Validation Severity Policy — the technical-flag layer META-ELI5 sits on top of).

**Why this rule exists:** RES-1/RES-3 enforce layman tone in narrative prose. APP-SE5 enforces takeaway captions on charts/tables in the Confidence section. Neither catches in-line flags ("Insufficient OOS," "chart pending," "Direction disagreement: Evan says X, Dana says Y"). Those flags are technically-correct but user-hostile. META-ELI5 closes that layer.

### Contract File Standard (Meta-Rule META-CF)

> **Single authoritative schema per cross-agent artifact. No forks, no inline divergent copies.**

Cross-agent JSON contracts (artifact formats, registries, manifests, metadata
sidecars) live under `docs/schemas/`. Prose dictionaries inside SOPs and partial
inline schema copies diverge silently and are prohibited — SOPs link to the
canonical schema instead.

| Element | Rule |
|---|---|
| Location | `docs/schemas/{contract_name}.schema.json` |
| Format | JSON Schema draft 2020-12 |
| Ownership | Header field `"x-owner": "<agent-id>"` (single agent owns updates; others PR) |
| Versioning | Header field `"x-version": "1.0.0"` semver — breaking change → major bump |
| Example instance | Companion `docs/schemas/examples/{contract_name}.example.json` must validate |
| Validation | `scripts/validate_schema.py` — called by producer before save AND consumer before use |
| Change discipline | Schema change → regression_note entry (per META-VNC) + sop-changelog entry |
| SOP cross-ref | When a new schema is added, every SOP with a producer/consumer role adds a link (no inline schemas allowed in SOPs) |
| Uniqueness | One authoritative schema per artifact — no forks permitted |

**Producer responsibility.**
- Before saving an artifact claimed to match a contract, call
  `scripts/validate_schema.py` and block on failure.
- Ship the schema in the same commit as the artifact whenever the schema is
  modified.

**Consumer responsibility.**
- Before using an artifact claimed to match a contract, call the validator.
- Never silently fall back — raise or render an explicit error (per
  APP-SE1/SE5 severity discipline).

**Cross-reference.** Supersedes inline JSON schemas previously embedded in
SOPs (e.g. the ECON-DS1 signals schema, APP-SE1 signal-column assumptions —
these must migrate to `docs/schemas/` when authored). See
`docs/schemas/README.md` for the evolution workflow.

### Abstraction Layer Discipline (Meta-Rule META-AL)

> **Before abstracting anything as "canonical," ask: does the output vary across consumers? If yes, the canonical layer is the *inputs/rules*, not the output. Making pixels/content canonical when they depend on pair-specific inputs is a category error.**

**Principle.** The boundary between "shareable canonical" and "per-consumer derived" is the presence of consumer-specific data. A schema, registry, template, or parameter is canonical-eligible. A rendered artifact computed from per-pair inputs is not — it is, by construction, pair-specific.

**Application.**

| Layer | Contents | Location pattern |
|-------|----------|------------------|
| Canonical (shareable) | metadata, rules, registries, parameters, templates, schemas | `docs/schemas/`, SOP rule text, `app/components/*` helpers |
| Pair-specific (per-pair) | rendered outputs, derived artifacts, anything computed from pair-specific inputs | `output/charts/{pair_id}/`, `results/{pair_id}/` |

**Test question.** "Does the artifact contain any pair-specific data?" If yes, it **cannot** be "canonical." It may live in a shared directory (e.g. `output/_comparison/`), but only as a pair's own contribution — not as a one-size-fits-all fallback for other pairs.

**Worked example (the zoom-chart lesson).**

- **Wrong:** canonical rendered zoom chart at `output/_comparison/history_zoom_dotcom.json` serves all pairs. Fails in practice — the file only contains one pair's overlay data, so it cannot serve another pair without silently misrepresenting that pair's indicator behavior.
- **Right:** canonical events registry at `docs/schemas/history_zoom_events_registry.json` (metadata only: episode slug, date windows, event dates, labels, citations); each pair renders its own dual-panel chart from events + pair data at `output/charts/{pair_id}/history_zoom_{episode}.json`. The registry is the shared layer; the rendered dual-panel is the per-pair layer.

**Cross-references.**

- **Invalidates the META-ZI canonical-rendered-chart fallback.** META-ZI is scheduled for refinement in Wave 6B: the loader drops the `output/_comparison/` rendered-chart fallback, and the canonical layer shrinks to the events registry (VIZ-V12) plus the per-pair rendering contract.
- Applies to any future shared-artifact proposals. Before a new rule introduces an `output/_comparison/` or `results/_shared/` path, the proposer must pass the test question and write the answer into the proposal.

**Why this rule exists.** Wave 5 reflection revealed that the META-ZI fallback was a silent source of cross-pair data misrepresentation: a pair whose own episode chart was missing would silently read another pair's chart. File-existence gates and loader smoke tests did not catch it because the load technically succeeded. META-AL forecloses that entire failure class by forbidding the abstraction up front.

### Self-Report Verification Discipline (Meta-Rule META-SRV)

> **Every agent self-report must name (a) the file path(s) touched and (b) a machine-checkable verification method. Self-reports without verification evidence are not acceptable for Lead to sign off.**

**Principle.** A claim is not done until it is both stated and verified. Producer agents (Dana, Evan, Vera, Ray, Ace) are the first line: every regression-note entry must carry its own evidence block. QA (Quincy, per `docs/agent-sops/qa-agent-sop.md`) is the second line: re-running the evidence independently.

**Format.** Every regression-note claim follows:

```
### <Agent>'s Wave X (<date>)
Claims:
- <claim 1>: <one sentence>
Evidence:
- File: <absolute path>
- Verification: <command>
- Result: <output / exit code>
```

**Verification methods catalog (examples).**

| Claim type | Verification method |
|------------|---------------------|
| Schema conformance | `python3 scripts/validate_schema.py --schema <name> --instance <path>` → exit 0 |
| Grep absence | `grep -r "old_pattern" app/ scripts/ docs/ | wc -l` → 0 |
| Smoke test | `python3 app/_smoke_tests/smoke_loader.py <pair_id>` → `passes=N/failures=0` |
| File existence | `ls data/manifest.json` → exists |
| Diff count | `git diff HEAD~1 --stat <file>` → non-empty |
| Cloud assertion | Playwright query + expected DOM text / attribute → matches |
| Schema-instance alignment | validator exit 0 AND instance on disk |
| Registry registration | `jq '.entries[] | select(.id=="X")' <registry>` → non-empty |

**Two-line defense.**

1. **First line — producer self-verifies.** Every claim in a producer's regression-note section carries its own evidence block. A claim without evidence is a META-SRV violation and cannot be signed off, even by the producer.
2. **Second line — QA (Quincy) re-verifies independently.** QA re-runs each verification command from a fresh shell, re-derives the result, and files findings per `docs/agent-sops/qa-agent-sop.md`. This catches the self-report blind spot where a producer's own verification drifts silently (e.g., a cached file, an environment variable the producer's shell has but QA's does not).

**Scope.** Applies to all 5 producer agents (Dana, Evan, Vera, Ray, Ace) on every regression-note entry, and to Lead on every acceptance.md sign-off block. QA's findings themselves obey META-SRV — each finding carries its own evidence column.

**Cross-references.**

- `docs/agent-sops/qa-agent-sop.md` — QA is the second line of META-SRV
- `GATE-31` — Independent QA Verification (the blocking gate that makes META-SRV mandatory at acceptance)
- META-RNF — Regression Note Format (the container META-SRV slots into)
- META-CF — Contract File Standard (schema validation is the canonical verification method)
- META-XVC — Cross-Version Discipline (observation subsection is a META-SRV evidence block)

**Why this rule exists.** Wave 5 reflection showed that several upstream claims had passed acceptance because the regression-note entries were clean prose without reproducible verification. In one case, a schema bump was described accurately but no validator run was logged; in another, a chart was claimed to "render cleanly" without a smoke-test log. META-SRV makes the evidence block a first-class part of every regression-note entry — making producer self-reports mechanically auditable and unlocking the independent QA re-verification layer.

### Scope Discipline (ECON-SD / ECON-UD / ECON-AS)

> **A pair's page makes a thematic promise on both axes. Off-scope signals violate that promise silently; disclosure + scope-registry + suggestion-channel operationalize the promise without losing useful observations.**

Pair pages titled "indicator X vs target Y" must honor both axes. Three cross-agent rules — authored by Evan in the Econometrics SOP (see `docs/agent-sops/econometrics-agent-sop.md` §ECON-SD, §ECON-UD, §ECON-AS) — make that honoring mechanical:

| Rule | Short | Blocking? | Anchor file |
|------|-------|-----------|-------------|
| **ECON-SD** | Pair Scope Discipline — only the indicator column + its mathematical derivatives AND the target column + its mathematical derivatives may appear on a pair's Story / Evidence / Strategy page. | Blocking (all pairs) | `results/{pair_id}/signal_scope.json` |
| **ECON-UD** | Universe Disclosure — every pair's Methodology page carries a "Signal Universe" section with two tables (indicator derivatives, target derivatives) rendered from the scope file. | Blocking (reference pairs per META-RPD); recommended (non-reference) | `results/{pair_id}/signal_scope.json` + Methodology page |
| **ECON-AS** | Analyst Suggestions — off-scope-but-interesting observations captured as informational entries (no lifecycle, no status), rendered read-only on Methodology under "Analyst Suggestions for Future Work." | Informational | `results/{pair_id}/analyst_suggestions.json` |

**Downstream impact by agent.**

- **Evan (author, producer).** Maintains `signal_scope.json` as the single source of truth; validates every econometric artifact against it before save. Files ECON-AS suggestions when off-scope signals surface during exploratory work. See ECON-SD producer-side rule.
- **Vera (consumer).** Chart-generation scripts read `signal_scope.json` and refuse to render any chart whose signal is not in scope (ECON-SD enforcement at the chart-save boundary). Cross-ref VIZ-V8 chart_type_registry: only charts referencing in-scope signals are eligible for the canonical filename pattern.
- **Ray (consumer).** Narrative cross-references the Signal Universe when introducing a derivative on Story / Evidence pages; narrative frontmatter (`chart_refs`, per RES-17) aligns with `appears_in_charts` column in the scope registry. ECON-AS rationale text may be Ray-edited for tone (plain-English owner per META-ELI5).
- **Ace (renderer).** Methodology page renders the Signal Universe tables (ECON-UD) and Analyst Suggestions table (ECON-AS) from the two JSON sidecars. Caption prefixes follow APP-CC1 (`"What this shows:"` on the Universe tables; `"How to read it:"` on the Suggestions table). If `analyst_suggestions.json` is absent or its `suggestions` array empty, the Suggestions section is silently omitted — the single sanctioned silent omission (because the rule is informational).
- **Quincy (QA).** GATE-31 verifier: parses chart sidecars and narrative frontmatter; cross-checks every signal name against `signal_scope.json`; any off-scope hit is a FAIL finding that blocks acceptance. Also verifies the Methodology page carries both required sections on reference pairs.

**Contract files (per META-CF).**

| Artifact | Schema | Example instance |
|----------|--------|------------------|
| `results/{pair_id}/signal_scope.json` | `docs/schemas/signal_scope.schema.json` (owner: Evan, v1.0.0) | `docs/schemas/examples/signal_scope.example.json` |
| `results/{pair_id}/analyst_suggestions.json` | `docs/schemas/analyst_suggestions.schema.json` (owner: Evan, v1.0.0) | `docs/schemas/examples/analyst_suggestions.example.json` |

**Why this rule family exists.** HY-IG v2 Wave 7 stakeholder review caught a scope leak on the Evidence-page correlation heatmap (NFCI, Yield Curve, Bank ratio, BBB-IG, CCC-BB all included on a page titled "HY-IG × SPY"). ECON-SD forecloses scope leaks by making the permitted universe a mechanical registry. ECON-UD makes that universe visible to users so they can cross-check nothing is hidden. ECON-AS captures the interesting off-scope observations that would otherwise be smuggled onto the page or forgotten.

### Classification Field Ownership

| Field | Owner | Timing | Source of Truth |
|-------|-------|--------|-----------------|
| `indicator_nature` | Data Dana | During data stage (before tournament) | Economic role of the indicator |
| `indicator_type` | Data Dana | Same time | Economic category of the underlying series |
| `strategy_objective` | Research Ray | After tournament results known | Tournament winner's optimization objective |

### Variant Families

When one priority pair spawns multiple variants (e.g., TED → 3 variants), the deliverables above apply to the **shared pages** — but all 4 page types (Story, Evidence, Strategy, Methodology) must still exist. Sharing pages across variants is acceptable; omitting a page type is not.

## Pipeline Self-Containment Contract (Mandatory)

### Why This Exists

HY-IG (pair #5) required 3 separate scripts run in a specific sequence: `data_pipeline_hy_ig_spy.py` → `stage2_core_models.py` → `tournament_backtest.py`. The HMM probability signal (`hmm_2state_prob_stress`) was computed at runtime inside `tournament_backtest.py` but never persisted. When `generate_winner_outputs.py` ran later as a separate process, it could not find the signal — producing an empty trade log. Fragmented pipelines with runtime-only derived signals create invisible dependencies that break downstream consumers.

### The Contract

Every indicator-target pair must have a **single self-contained pipeline script** (`scripts/pair_pipeline_{id}.py`) that produces ALL artifacts needed by downstream consumers. Specifically, the pipeline must:

1. **Source raw data** from external APIs (FRED, Yahoo Finance, etc.)
2. **Compute and persist ALL derived signals** — including HMM probabilities, Markov states, z-scores, composite scores, and any other signal that could become a tournament winner. These must be saved to `results/{id}/signals_{date}.parquet` per the Econometrics SOP Derived Signal Persistence Rule.
3. **Run the tournament** using signals from the persisted file (not in-memory computation)
4. **Run validation** (walk-forward, bootstrap, stress tests, signal decay, transaction costs)
5. **Generate winner outputs**: `winner_summary.json`, `winner_trade_log.csv`, `execution_notes.md`

### What's Allowed Outside the Pipeline

- **Chart generation** (`generate_charts_{id}.py`) may be a separate script — charts are a rendering concern, not a data pipeline concern
- **Portal page creation** — Streamlit page files are developed separately by Ace

### Verification

After the pipeline runs, the following must be true without running any other script:
- Completeness gate items 1–7 and 16–18 are satisfied from `results/{id}/`
- The signals parquet contains all columns referenced in the tournament results CSV
- A fresh clone can regenerate all data by running only the pipeline script (plus API keys)

**Cross-reference:** See Econometrics SOP, "Derived Signal Persistence Rule" for signal-level requirements.

## Iterative Review: Browser Verification (Mandatory After Portal Assembly)

After every portal page is created or modified, a **headless browser inspection** must be performed before the work is considered complete. This catches rendering issues that are invisible in Python code but visible in the browser.

### Why This Is Mandatory

Pair #1 (INDPRO → SPY) revealed two classes of rendering bugs:
1. **Raw HTML in Streamlit:** `st.markdown(unsafe_allow_html=True)` silently fails on nested HTML (e.g., `<div>` with child `<span>` elements). The HTML appears as literal text instead of rendered markup.
2. **Raw Markdown inside HTML blocks:** Markdown headings (`###`) and bold (`**text**`) inside HTML `<div>` wrappers are not rendered by Streamlit — they display as raw syntax.

These bugs are **invisible during development** (the Python code looks correct) and only appear in the browser.

### Verification Protocol

**Tool:** Playwright headless browser (`temp/inspect_portal.py`)

**Steps:**
1. Launch Streamlit app
2. For each page, navigate and wait for render (4-5s for Streamlit hydration)
3. Take full-page screenshot
4. Extract `body` inner text and scan for:
   - Raw HTML tags: `<div`, `<span`, `<b>`, `<br>`, `</h4>`
   - Raw Markdown syntax: lines starting with `###`, `##`, or containing `**text**`
5. If issues found → fix and re-verify
6. Save screenshots for the record

**When to run:**
- After creating new portal pages
- After modifying `components/narrative.py`, `components/charts.py`, or any component that renders HTML
- After updating the landing page layout
- Before committing any portal changes

### Known Streamlit Rendering Rules

| Pattern | Works? | Fix |
|---------|--------|-----|
| `st.markdown("### Heading")` | Yes | Use directly |
| `st.markdown("<div>### Heading</div>", unsafe_allow_html=True)` | **No** — heading shows as raw `###` | Remove HTML wrapper; use `st.markdown("### Heading")` |
| `st.markdown("<div><span>text</span></div>", unsafe_allow_html=True)` | **Unreliable** — may show as raw tags | Use `st.container()` + native Streamlit components |
| `st.metric("Label", value)` in narrow column | Truncates with `...` | Use fewer columns or markdown tables |
| `st.container(border=True)` | Yes | Preferred for card-like layouts |

## MRA: Measure, Review, Adjust (Mandatory After Browser Verification)

After every pair pipeline + portal + browser verification, conduct **MRA** before the work is considered complete. This is Step 8 in the Standard Task Flow.

### Measure

Record quantitative outcomes in `docs/pair_execution_history.md`:

| What to Measure | Where to Record |
|----------------|-----------------|
| Pipeline wall-clock time per stage | Pipeline Timing table |
| Token usage by component | Token Usage Estimate table |
| Econometric results: best Sharpe, direction, significance | Key Results table |
| Tournament stats: combos tested, valid count, benchmark comparison | Key Results table |
| Portal: rendering issues found and fixed | Key Findings section |
| Deviation from previous pair's cost/timing | Cost Projections section |

### Review

Reflect on what worked and what didn't:

- **Econometric:** Direction surprises, model convergence issues, unexpected insignificance
- **Data:** Sourcing failures, frequency mismatches, sample limitations
- **Portal:** Rendering bugs caught by browser, layout issues, chart quality
- **Process:** Pipeline friction, script adaptation difficulty, documentation gaps

### Adjust

Update artifacts based on the review:

| If This Happened | Then Adjust This |
|-----------------|-----------------|
| New rendering rule discovered | Update viz-agent SOP + appdev SOP |
| Pipeline step failed or was slow | Fix template script + document in lessons |
| Econometric method was unhelpful for this indicator type | Note in econometric-methods-catalog Relevance Matrix |
| Token usage significantly off projection | Revise per-pair estimates in execution history |
| New data source challenge | Update data-agent SOP |
| Direction was surprising | Document in interpretation_metadata.json + lessons |

### Documentation

After MRA, update:
1. `docs/pair_execution_history.md` — full MRA section for this pair
2. File-based memory (`~/.claude/projects/.../memory/`) — new lessons file if significant
3. AutoMem knowledge graph — new entities/observations for major findings
4. SOPs — if any rules changed

**No pair is considered complete until MRA is documented.**

## Phase 0: Analysis Brief (Mandatory Gate)

No agent starts work on a new indicator-target analysis without an approved Analysis Brief. The brief is the single source of truth for:
- Research question and hypotheses
- Indicator and target specification (including expected direction)
- Sample design and data requirements
- Method categories (from Relevance Matrix)
- Tournament design parameters (target-class-specific)
- Computational budget
- Portal specifications

**Gate rule:** Lesandro creates or approves the Analysis Brief. Each agent acknowledges receipt and flags domain-specific concerns before proceeding. The brief template is at `docs/analysis_brief_template.md`.

### Brief Acknowledgment Protocol

When the Analysis Brief is issued:

1. **Each agent reads the brief** within one task cycle
2. **Each agent sends a structured acknowledgment:**
   - "I have read the Analysis Brief for {INDICATOR} → {TARGET}"
   - Domain-specific concerns (e.g., Dana: "I16 is quarterly — will use LVCF alignment"; Evan: "Expected direction is ambiguous — will determine empirically")
   - Blockers (e.g., "Cannot source I13 (ABI) — need alternative")
3. **Lesandro reviews all acknowledgments** and resolves any concerns before giving the go-ahead
4. **No agent proceeds past their intake step** until the go-ahead is issued

## Handoff Protocol

Every handoff follows three rules:
1. **Use the structured template** defined in the sender's SOP
2. **Receiver must acknowledge** within one task cycle (silence ≠ acceptance)
3. **Partial delivery is OK** — mark it clearly and include a manifest of what's missing

### Primary Pipeline Handoffs

#### Research Agent → Econometrics Agent (Two-Stage)

**Stage 1 — Quick Spec Memo (deliver ASAP):**
- 5-bullet specification memo: DV, regressors, instruments, pitfalls, sample conventions
- Naming: `docs/spec_memo_{topic}_{date}.md`

**Stage 2 — Full Research Brief:**
- Complete brief with literature synthesis, specification details table, data sources with series IDs, event timeline, references
- Naming: `docs/research_brief_{topic}_{date}.md`

#### Research Agent → Data Agent

- Data source recommendations table (variable, series ID, MCP server, frequency, availability status)
- Included in the research brief; Dana extracts on receipt

#### Data Agent → Econometrics Agent

- Analysis-ready dataset (`.parquet` or `.csv`)
- Data dictionary with Display Name column (variable name, display name, description, source, series ID, unit, transformation, SA status, known quirks)
- Summary statistics
- Stationarity test results (structured table: variable, test, statistic, p-value, lags, conclusion)
- Handoff message using Data-to-Econ template (see Dana's SOP)
- Naming: `data/{subject}_{frequency}_{start}_{end}.parquet`

#### Econometrics Agent → Visualization Agent

- Fitted model results (`.pkl`)
- Coefficient tables (`.csv`) using standardized schema: `variable`, `coef`, `se`, `t_stat`, `p_value`, `ci_lower`, `ci_upper`
- Diagnostic test results (standardized table: test, statistic, p-value, interpretation)
- **Chart Request Template** (chart type, data source path, key variables, main insight sentence, audience, comparison notes, special annotations)
- Naming: `results/{model_name}_{date}.pkl`, `results/{model_name}_coefficients_{date}.csv`

#### Visualization Agent → Lesandro

- Charts (`.png` and `.svg`) with versioning: `_v{N}`
- Formatted tables (`.md` and `.csv`)
- One-line captions for each chart
- Annotation source tracking table
- Naming: `output/{subject}_{chart_type}_{date}_v{N}.{ext}`

### Direct (Non-Pipeline) Handoffs

#### Data Agent → Visualization Agent

- For exploratory charts, data quality plots, descriptive visualizations
- Dataset with Display Name metadata in data dictionary
- Data quirks relevant to visual interpretation
- See Dana's SOP: Data-to-Viz Handoff section

#### Research Agent → Visualization Agent

- Event timeline (date, event, relevance, type) for chart annotations
- Domain visualization conventions from literature
- See Ray's SOP: Event Timeline section

#### Econometrics Agent → Data Agent (Mid-Analysis)

- Expedited single-variable requests during diagnostics
- Must include: variable name, source preference, urgency flag, econometric rationale
- See Evan's SOP: Mid-Analysis Data Requests section

### Portal Assembly Handoffs

#### Visualization Agent → App Dev

- Plotly figure objects (`.json` or Python code) for interactive charts
- Static chart files (`.png`, `.svg`) for fallback
- Chart specifications (data source, key message, caption)
- See Vera's SOP: Output Standards

#### Research Agent → App Dev

- Narrative text sections (markdown) for each portal page
- Section ordering and storytelling arc
- Plain-English interpretation of findings for layperson audience

#### Data Agent → App Dev

- Data refresh pipeline code or specifications
- Cached dataset locations and update frequency
- Data dictionary for any series displayed in the portal

#### Econometrics Agent → App Dev

- Model result summaries for display (key coefficients, diagnostics, strategy performance)
- Backtest results in tabular format
- Regime/signal status for any live indicators

#### App Dev → Lesandro

- Running portal URL (Streamlit Community Cloud)
- Portal architecture documentation
- User guide for content updates

### Interpretation Annotation Handoffs

When the same indicator is analyzed against multiple targets, interpretation may differ (e.g., VIX/VIX3M rising is bearish for SPY but bullish for TLT). The team must coordinate annotations:

1. **Evan** outputs `interpretation_metadata.json` alongside results: `direction` (+1/-1), `mechanism` (plain English), `confidence` (from analysis)
2. **Ray** validates direction against literature; flags contradictions between empirical and theoretical expectations
3. **Vera** renders direction indicators: solid line = pro-cyclical, dashed = counter-cyclical; inline annotations on multi-pair dashboards
4. **Ace** implements "How to Read This" callout box on each pair's page; "Differs From" notes when same indicator has opposite interpretations across targets on the same dashboard

The `expected_direction` field in the Analysis Brief sets the prior; the `interpretation_metadata.json` from Evan records the empirical finding.

## Shared Workspace Structure

```
/workspaces/aig-rlic-plus/
├── app/               # Streamlit portal source code (Ace owns)
│   ├── app.py         # Main Streamlit entry point
│   ├── pages/         # Multi-page app sections
│   ├── components/    # Reusable UI components
│   └── assets/        # Static assets (images, CSS)
├── data/              # Cleaned, analysis-ready datasets
├── results/           # Model outputs, coefficient tables, diagnostics
├── output/            # Final charts, tables, reports
├── docs/              # Research briefs, documentation
│   └── agent-sops/    # This folder — agent SOPs
├── cache/             # Temporary cached data (auto-cleaned)
├── temp/              # Scratch space (auto-archived)
└── scripts/           # Reusable analysis scripts
```

## Acknowledgment Protocol

Every handoff requires a structured acknowledgment from the receiver:

1. **Sender** delivers output using the handoff template from their SOP
2. **Receiver** acknowledges within one task cycle with:
   - What was received (file list)
   - Whether it meets their needs (accepted / accepted with caveats / blocked — specify what's missing)
   - Any questions or follow-ups
3. **If no acknowledgment** within one task cycle, sender follows up explicitly
4. **Silence is never acceptance** — an unacknowledged handoff is an open loop

## Communication Rules

1. **Use TaskList / TaskUpdate** for tracking — do not rely on messages alone
2. **Be explicit about blockers** — if you need input from another agent, say exactly what you need
3. **Deliver incrementally** — a partial dataset now is better than a perfect one late
4. **Flag surprises immediately** — unexpected data patterns, missing series, test failures
5. **Never overwrite another agent's output** — create versioned files with `_v{N}` suffix
6. **Acknowledge every handoff** — confirm receipt and adequacy (see Acknowledgment Protocol above)
7. **Cite upstream contributions** — reference teammates' deliverables by file path in your output

## Naming Conventions

### Files

| Type | Pattern | Example |
|------|---------|---------|
| Dataset | `data/{subject}_{freq}_{start}_{end}.parquet` | `data/macro_panel_monthly_200001_202312.parquet` |
| Research brief | `docs/research_brief_{topic}_{date}.md` | `docs/research_brief_phillips_curve_20260228.md` |
| Model results | `results/{model}_{date}.pkl` | `results/phillips_ols_20260228.pkl` |
| Coefficients | `results/{model}_coefficients_{date}.csv` | `results/phillips_ols_coefficients_20260228.csv` |
| Chart | `output/{subject}_{type}_{date}.png` | `output/us_inflation_line_20260228.png` |
| Table | `output/{subject}_table_{date}.md` | `output/regression_results_table_20260228.md` |

### Branches (if applicable)

- `analysis/{topic}` for analysis work
- `data/{source}` for data pipeline changes
- `docs/{topic}` for documentation updates

## Escalation Rules

| Situation | Action |
|-----------|--------|
| Missing data for a required variable | Data agent flags to Lesandro; suggests alternatives |
| Model diagnostics fail | Econometrics agent reports to Lesandro with proposed fix |
| Conflicting literature findings | Research agent presents both sides; Lesandro decides |
| Chart request is ambiguous | Visualization agent asks econometrics agent for clarification |
| Any agent is blocked for > 1 task cycle | Escalate to Lesandro immediately |

## Quality Standards (Team-Wide)

- Every output file has a descriptive name following the naming convention
- Every handoff includes a structured message using the sender's SOP template
- Every handoff is acknowledged by the receiver within one task cycle
- No agent delivers output without running their quality gate checklist
- All code is reproducible — another agent should be able to re-run it
- Assumptions are documented, not implicit
- Upstream contributions are cited by file path

### Defense 1: Self-Describing Artifacts (Producer Rule)

**Any artifact that crosses an agent boundary must carry enough context that the consumer cannot misinterpret it.** Implicit assumptions — state labels, sign conventions, units, date ranges, return types, merge keys — are the #1 source of silent errors in multi-agent pipelines.

**Concrete requirements for producers:**

1. **Column names encode meaning, not indices.** Never deliver columns named `state_0`, `regime_1`, `cluster_2`. Use `stress_prob`, `calm_prob`, `high_vol_regime`. If a model assigns numeric labels, rename them before saving the output file.

2. **Units are explicit.** Include units in column names (`spread_bps`, `return_pct`, `vol_annualized`) or in a sidecar metadata file. Never assume the consumer knows your unit convention.

3. **Sign conventions are stated.** Document whether positive means "widening" or "tightening", whether a higher value means "more stressed" or "less stressed". If the convention is non-obvious, add a comment in the data dictionary row.

4. **Date/sample boundaries are in the file.** If an artifact is OOS-only, the filename or metadata must say so. Never rely on the consumer knowing your train/test split.

5. **Sidecar manifest for model artifacts.** Every `.pkl` or `.parquet` model output must be accompanied by a `_manifest.json` that documents: what each column/variable means, what higher/lower values signify, and at least one sanity-check assertion (see Defense 2).

**Why this matters:** When Vera receives `prob_state_0` and `prob_state_1`, she must guess which is stress. If Evan delivers `prob_stress` and `prob_calm`, guessing is impossible. This principle applies to every handoff, not just HMM states — it covers sign conventions, return types (arithmetic vs geometric), threshold directions, and any other implicit assumption.

### Defense 2: Reconciliation at Every Boundary (Consumer + Reviewer Rule)

**Every agent that consumes an upstream artifact must verify that their interpretation produces results consistent with the upstream agent's reported numbers.** Gate reviewers must run automated numerical reconciliation, not just structural checks.

**Concrete requirements:**

**For consumers (Vera, Ace, or any downstream agent):**

1. **Sanity-check on ingestion.** Before using any upstream data, verify at least one known fact. Examples:
   - "During GFC (2008-09), stress probability should be > 0.8" (Example — adjust assertion to match the specific indicator-target pair)
   - "Tournament winner Sharpe should match the value reported in the Analysis Brief's tournament results"
   - "B&H max drawdown should be consistent with the target's historical volatility profile (see Analysis Brief, Section 4)"
   These checks are derived from the upstream agent's summary or handoff message. If the check fails, STOP and ask — do not proceed with a guess.

2. **Cross-check derived outputs against source.** If you compute a drawdown curve from raw data, the max drawdown of that curve must match the number reported in the upstream results CSV (within rounding). If it doesn't, your interpretation of the data is wrong.

3. **When in doubt, verify with a known period.** Pick a well-understood historical episode (GFC, COVID) and confirm your derived series behaves as expected during that period. This catches sign inversions, unit errors, and state label swaps generically.

**For gate reviewers (Lesandro):**

4. **Automated reconciliation script.** Before signing off on any gate, run a script that compares every number displayed in the portal/charts against the source CSV/parquet. This is not optional spot-checking — it is a systematic check that every displayed number traces back to the ground truth.

5. **Reconciliation covers derived quantities.** Don't just check that "Sharpe = 1.17" appears correctly. Recompute the Sharpe from the equity curve data in the chart and verify it matches. This catches errors in the derivation, not just the label.

**Template for a reconciliation script:**

```python
# gate_reconciliation.py — mandatory before Gate 3/4 sign-off
import json, pandas as pd

def reconcile_chart(chart_name, check_fn, tolerance=0.02):
    """Load a chart JSON and run a numerical check against ground truth."""
    with open(f'output/charts/plotly/{chart_name}.json') as f:
        fig = json.load(f)
    result = check_fn(fig)
    assert result, f"RECONCILIATION FAILED: {chart_name}"
    print(f"  OK  {chart_name}")

# Example checks:
# 1. Drawdown chart W1 MDD must match tournament CSV
# 2. Equity curve final value must be consistent with reported annualized return
# 3. HMM stress probability must be high during GFC, low during 2013-2014
# 4. KPI card numbers must match tournament CSV
# ... add one check per chart
```

**Why this matters:** Structural reviews (files exist, parse OK, titles are good) catch ~20% of errors. Numerical reconciliation catches the remaining ~80% — the silent errors where the chart looks plausible but shows the wrong data. The cost of writing these checks is low; the cost of shipping wrong charts is high.

## Task Completion Hooks (Team-Wide Standard)

Every agent must run these two hooks when completing any task. Individual SOPs contain role-specific details; these are the universal minimums.

### Hook 1: Validation & Verification (before marking task done)

1. **Re-read the original request** — does the deliverable actually answer what was asked?
2. **Run your Quality Gates checklist** — every box must be checked
3. **Self-review** — read your output as if you were the receiving agent. Would you accept this?
4. **Verify file naming and location** — follows conventions, saved to correct workspace directory
5. **Send structured handoff message** — use the template from your SOP
6. **Request acknowledgment** — explicitly ask the receiver to confirm

### Hook 2: Reflection & Memory (after every completed task)

1. **What went well? What was harder than expected?**
2. **Did any handoff friction occur?** Note it for SOP improvement
3. **Did you learn something reusable?** (data gotcha, method insight, tool trick, collaboration pattern)
4. **Distill 1-2 key lessons** and update your memories file at `~/.claude/agents/{your-id}/memories.md`
5. **Cross-project lessons** go to `~/.claude/agents/{your-id}/experience.md`
6. **If a lesson affects another agent's workflow**, message them directly — don't assume they'll discover it

These hooks are not optional. They are the mechanism by which the team improves over time. Skipping them to save time is a false economy — the cost shows up as repeated mistakes and handoff friction in future tasks.

## New Agent Onboarding Protocol

When a new agent joins the team (or when the team is first formed), run this cross-review exercise before starting real work:

### Step 1: Cross-Review SOPs
Every agent reads ALL teammates' SOPs plus the team coordination protocol. Each writes a structured review covering:
1. What I learned about each teammate's workflow and pressures
2. Where our handoffs connect and where friction could arise
3. Suggestions for each teammate's SOP (empathy, rapport, handoff clarity)
4. Suggestions for my own SOP (blind spots revealed by reading others')
5. Suggestions for the team coordination protocol

Reviews are saved to `docs/agent-sops/reviews/{agent-id}-review.md`.

### Step 2: Self-Update SOPs
Each agent incorporates the best feedback into their own SOP. Ownership matters — you update your own SOP, not someone else's.

### Step 3: Distill and Remember
Each agent distills key lessons into:
- `~/.claude/agents/{agent-id}/memories.md` (gotchas, insights, commitments)
- `~/.claude/agents/{agent-id}/experience.md` (cross-project patterns)

### Why This Matters
Reading teammates' SOPs reveals handoff gaps, duplicated work, and blind spots that no amount of solo work surfaces. This is not optional — it is the single highest-leverage activity for team cohesion. Do it for every new team or whenever the team composition changes.

---

## Portal-Wide Quality Checklist

Every pair delivery must pass every item below. This is the cross-cutting checklist gate reviewers use during acceptance. Individual agent SOPs own the detailed rules; this document lists the minimum observable outcomes.

### Landing Page
- [ ] Pair appears as a card in filtered view with correct nature/type/objective/direction chips
- [ ] Performance badges (Sharpe, Max DD) use correct color thresholds
- [ ] Card renders without truncation at standard viewport (1280×900)

### Navigation
- [ ] Breadcrumb component at top of every pair page showing Story → Evidence → Strategy → Methodology with current step highlighted
- [ ] Sidebar finding selector includes this pair
- [ ] All Story/Evidence/Strategy/Methodology links work

### Story Page
- [ ] Hero chart: no inverted axes, correct units disclosed in axis label
- [ ] KPI strip with interpretation captions (benchmark + one-sentence meaning per metric)
- [ ] Story narrative flows from the Landing Page executive summary themes
- [ ] "Why this indicator?" context section present
- [ ] Progressive disclosure via expanders

### Evidence Page
- [ ] 8-element template applied to every method block
- [ ] Difficulty tiers: Level 1 (Correlation, Cross-Correlation, Causality) before Level 2 (Regime, Quantile, Local Projections, advanced)
- [ ] Every method has "Why we chose this method" rationale
- [ ] Every method's chart uses canonical filename per VIZ-A3
- [ ] Unit discipline: all axis labels disclose scale

### Strategy Page
- [ ] Trading Rule in Plain English appears FIRST
- [ ] "How to Use This Indicator Manually" tutorial section present (human investor perspective, not just algo description)
- [ ] KPI cards with interpretation captions
- [ ] OOS Return label specifies calculation basis (CAGR, arithmetic, total)
- [ ] Trade log: broker-style CSV + column legend expander + dual download + 10-row preview
- [ ] "How to Read the Trade Log" narrative subsection with concrete example
- [ ] Tournament leaderboard shows top 20 with ability to explore non-winning strategies

### Methodology Page
- [ ] Skeptical reader framing in intro
- [ ] Methods table with "Why We Chose It" column
- [ ] Diagnostics table with "Why It Matters" column
- [ ] References section with full bibliography
- [ ] Inline citations link to bibliography entries

### Cross-Cutting
- [ ] Dual notation on first use of unit-laden values (bps AND %)
- [ ] "Plain English" expander on major sections for simplified explanation
- [ ] Writing voice consistent across pages
- [ ] Honest caveats in every page
- [ ] No silent regressions — deliberate changes documented in `regression_note_<date>.md`

## Reference Pair Doctrine

**HY-IG v2 (tag: `hy-ig-v2-reference` once approved) is the canonical reference pair** for the AIG-RLIC+ portal. It represents the stakeholder-approved gold standard for pair presentation, depth, and audience-friendliness.

### Rules

1. **Comparison is mandatory.** Every new pair dispatch must begin by reading HY-IG v2's equivalent files (narrative, Evidence page, Strategy page, charts directory) for structural and tonal comparison.

2. **Deviations must be documented.** Any deliberate departure from HY-IG v2's pattern requires a `design_note.md` in the pair's results directory with rationale.

3. **Gate reviewers compare side-by-side.** Before accepting a pair as complete, perform a visual side-by-side comparison against HY-IG v2. Divergences without rationale are rejected.

4. **When the reference evolves, flag it.** Stakeholder-prompted changes to HY-IG v2 itself tag a new state (e.g., `hy-ig-v2-reference-v2`); previous tags remain accessible.

### Why

This doctrine turns "good decisions" from tribal knowledge into mechanical artifacts. An agent dispatched for a new pair cannot miss the reference — reading HY-IG v2 is step 1 of the workflow.

### Exception

If a stakeholder explicitly requests a new pair with intentionally different structure, the request itself serves as the design_note rationale.

## Pair Acceptance Checklist

Before any pair is marked "completed," a file `results/<pair_id>/acceptance.md` MUST exist containing the template below, signed off by the Lead. This is a blocking gate item (Gate 23).

### Template (copy to `results/<pair_id>/acceptance.md`)

    # Acceptance — <pair_id> — <YYYY-MM-DD>

    ## Portal-Wide Quality Checklist

    <Copy the Portal-Wide Quality Checklist from team-coordination.md and check every box.
    For items that deliberately deviate, explain why here.>

    ## Reference Pair Comparison

    **Compared against:** HY-IG v2 (tag: hy-ig-v2-reference)
    **Comparison date:** YYYY-MM-DD
    **Key differences:** <list>
    **design_note.md:** <yes/no — if yes, summarize rationale>

    ## Regression Note

    **regression_note_<YYYYMMDD>.md exists:** <yes/no>
    **Summary of changes from prior version:** <brief>
    **Removed section present (if any removals):** <yes/no — cite each removal and rationale>

    ## Blocking Items — GATE-24 / GATE-25 / GATE-26 / GATE-27 / GATE-28 / GATE-29 / GATE-30

    ### GATE-24 — Chart-Text Coherence Audit
    - [ ] For every chart modified since prior version, `grep -r "<chart_name>" app/pages/` was run and every referenced caption/narrative was updated in the **same commit** as the chart change.
    - [ ] regression_note_<date>.md lists each chart change paired with its narrative change under a single bullet.
    - [ ] No dangling narrative references an outdated chart state.

    ### GATE-25 — No Silent Chart Fallbacks
    - [ ] Every Evidence-page method block lists its canonical chart filename (per VIZ-A3 / VIZ-V3) — no borrowed artifacts.
    - [ ] Method → chart mapping table below is filled in.

        | Method | Canonical chart filename | Rendered as canonical? (Y/N) | Placeholder if N? |
        |--------|--------------------------|------------------------------|-------------------|
        | <method> | <filename.json> | <Y/N> | <placeholder text or N/A> |

    - [ ] No page silently substitutes a different method's chart for a missing canonical chart. Missing charts render an explicit "chart pending" placeholder.

    ### GATE-26 — No Silent Content Drops
    - [ ] Prior-Version Inventory Check (below) completed.
    - [ ] Every removed element (vs prior version) is documented in regression_note_<date>.md **Removed** section with rationale and approver.
    - [ ] Any removal without documented rationale has been restored.

    ### GATE-27 — End-to-End Chart Render Test
    - [ ] Vera's VIZ-V5 smoke test log attached: every canonical chart artifact loads via Plotly, has ≥1 data trace, and has a non-empty title.
    - [ ] Ace's loader smoke-test log attached: every chart name referenced in every portal page of this pair resolves successfully via `load_plotly_chart(name, pair_id)` and returns a non-None Figure.
    - [ ] Zero chart loads returned None, zero chart loads returned a Figure with zero traces, zero chart loads returned an empty title.
    - [ ] Any chart failing any of the three checks is listed here with remediation status; no item in this list is marked "deferred" on a reference pair.

    ### GATE-28 — Reference-Pair Placeholder Prohibition
    - [ ] This pair IS a reference pair: <yes/no — if no, write "N/A, gate does not apply" and skip>
    - [ ] Headless-browser DOM audit performed across Story, Evidence, Strategy, Methodology pages.
    - [ ] DOM-audit log attached showing zero occurrences of the "chart pending" placeholder text (or equivalent GATE-25 fallback rendering).
    - [ ] Any `chart_pending` occurrence found by the audit is logged here with a chart name, root cause, and remediation commit — no "known issue / deferred" state is permitted on a reference pair.

    ### GATE-29 — Clean-Checkout Deployment Test
    - [ ] Clean checkout performed via `git clone --depth 1 "$(git rev-parse --show-toplevel)" /tmp/clean_checkout_{pair_id}`.
    - [ ] `python3 app/_smoke_tests/smoke_loader.py --pair-id {pair_id}` executed inside the clean-checkout working directory.
    - [ ] Clean-checkout smoke test log saved to `app/_smoke_tests/clean_checkout_{pair_id}_{date}.log` — zero FileNotFound / zero None-return / zero placeholder must be asserted.
    - [ ] Every file referenced by `app/` code for this pair is present in the clean checkout (no silent `.gitignore` exclusions; no missing `git add -f` for deploy-required artifacts).
    - [ ] Cross-reference: ECON-DS2 (Deploy-Required Artifact Allowlist) producer-side checks confirmed by Evan for this pair.

    ### GATE-30 — Deflection Link Audit
    - [ ] Every stakeholder-feedback item closed in this acceptance via deflection (resolution = "see other page/section") is listed in the table below.
    - [ ] For each deflection, target page AND target section/anchor are explicitly named.
    - [ ] For each deflection, a headless-browser DOM assertion confirms the target anchor renders.
    - [ ] For each deflection, a content-presence assertion confirms the target section contains the content claimed to address the stakeholder's concern.
    - [ ] Lead has signed off on every deflection resolution in this table (not agent-only closure).

        | Stakeholder item | Origin page / section | Deflection target page | Deflection target anchor/section | DOM-renders? (Y/N) | Content-matches? (Y/N) | Lead sign-off? (Y/N) |
        |------------------|----------------------|------------------------|----------------------------------|--------------------|------------------------|----------------------|
        | <e.g. S18-2>     | <e.g. Strategy>      | <e.g. Story>           | <e.g. regime-explainer>          | <Y/N>              | <Y/N>                  | <Y/N>                |

    - [ ] Any N in the table above is a blocker until resolved. If the deflection target is later restructured (anchor renamed, section removed), every row pointing at it is automatically re-opened.

    ### Prior-Version Inventory Check

    Required whenever a prior version of this pair exists. If this is a brand-new pair, write "No prior version — N/A" and skip the bullets.

    **Prior version compared against:** <tag or commit hash>
    **Comparison date:** YYYY-MM-DD

    - **Features retained:** <bulleted list of tables, charts, subsections, callouts that are present in both versions>
    - **Features added:** <bulleted list of new elements in this version>
    - **Features intentionally removed:** <bulleted list; each entry cites the regression_note bullet that justifies removal>

    ## QA Verification (GATE-31)

    **QA agent:** Quincy
    **Verification date:** YYYY-MM-DD
    **Findings link:** `results/<pair_id>/regression_note_<date>.md` § QA Verification — Wave X

    ### Summary
    Total checks: N | PASS: n1 | PASS-with-note: n2 | FAIL: n3 | Blocking: n4

    ### Mandated category coverage (per GATE-31)
    - [ ] Artifact verification: at least one claim-evidence cross-check per producer's regression-note section
    - [ ] Smoke tests: `smoke_loader.py` + `smoke_schema_consumers.py` both `failures=0`
    - [ ] Stakeholder-spirit check: every S-item claimed resolved in this acceptance re-read as the stakeholder
    - [ ] Cross-agent seam audit: GATE-24 / 25 / 26 / 28 / 30 + APP-DIR1 + META-XVC cross-version diff

    ### Sign-off recommendation
    <Approve / Block / Approve with Lead override>

    If Lead override: link to "QA Override Log" entry in `docs/pair_execution_history.md`.

    ## Stakeholder Review

    **Reviewed by:** <name>
    **Review date:** YYYY-MM-DD
    **Outstanding issues:** <list>

    ## Lead Sign-off

    **Approved by:** Lead Lesandro
    **Approval date:** YYYY-MM-DD
    **Tag/commit:** <hash>
    **QA sign-off received:** <yes/no — if no, override rationale and log link required>

---

## Indicator Evaluation Framework

### Purpose

Integrate the Indicator Evaluation Layer into the multi-agent workflow. This layer provides a structured framework for evaluating how indicators interact with market environments and strategy performance.

### Artifacts

- `environment_interaction_scores.json`
- `strategy_survival_scores.json`

### Coordination Responsibilities

- Ensure evaluation-layer tasks are properly assigned across agents (Data validates schema, Econ supplies evidence, Research provides grounding, Viz renders radars, AppDev integrates into portal)
- Monitor completion and integration of evaluation components
- Maintain clear communication between all agents on evaluation-layer deliverables
- Evaluation-layer work follows the same Phase 0 → MRA pipeline as pair analysis

---

## Retrospective

After completing a major analysis (not after every task), the team lead (Lesandro) convenes a brief retrospective:

1. Each agent reviews their Input Quality Log / memories for recurring friction
2. Top 3 improvement suggestions are collected
3. SOPs are updated by their respective owners
4. Team coordination protocol is updated if cross-cutting changes are needed
5. Learnings are promoted to global experience files if cross-project applicable

### Run Registry

The team maintains a "Registered Analysis Runs" table in the Reference Catalogs Index (`docs/reference-catalogs-index.md`). Every completed indicator-target analysis is registered there with: pair ID, date completed, lead agent, and link to results. This is the single source of truth for what has been analyzed.
