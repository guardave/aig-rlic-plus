# QA Verification — Wave 6B (2026-04-19, Quincy)

**Role:** Quincy (QA agent) — first production QA run on HY-IG v2 reference-pair candidate.
**Scope:** Wave 6B META-AL retro-apply — Vera's dual-panel zoom rebuild + Ace's loader refactor.
**Authority:** GATE-31 (Independent QA Verification); second line of defense after META-SRV.

---

## Summary

- **Total checks run:** 23 (13 claim-verifications + 10 GATE-31 items; Cloud check explicitly deferred to Wave 6D per scope).
- **PASS:** 20
- **PASS-with-note:** 3
- **FAIL:** 0
- **Blocking:** 0

Verdict: **PASS**. Acceptance sign-off on Wave 6B is unblocked pending central commit by Lead.

---

## Verified claims matrix

### Vera's Wave 6B META-AL retro-apply

| # | Source | Claim | Verification command | Result | Evidence |
|---|--------|-------|----------------------|--------|----------|
| V1 | regression_note §Vera Wave 6B | VIZ-V1 refined to META-AL / dual-panel mandatory / `output/_comparison/` model removed | `grep -n "Abstraction layer discipline\\|META-AL\\|Dual-panel layout (MANDATORY)\\|PROHIBITED" docs/agent-sops/visualization-agent-sop.md` | PASS | All 4 phrases found in §Rule V1 lines 459-491; old two-tier heading replaced |
| V2 | regression_note §Vera Wave 6B | 3 dual-panel zoom JSONs + 3 `_meta.json` sidecars created at `output/charts/hy_ig_v2_spy/plotly/` | `ls -la` + `python3 -c "json.load; len(data), len(shapes), trace names, y-axis"` | PASS | 6 files present (dotcom.json 79KB, gfc.json 115KB, covid.json 79KB + 3 sidecars); each chart has `traces=2` (indicator on y1, target on y2); shape counts dotcom=10, gfc=12, covid=8 match claim; sidecars contain `palette_id=okabe_ito_2026`, `panels=['indicator','target']`, `pair_id=hy_ig_v2_spy`, `episode_slug`, `annotation_strategy_id`, `events`, `data_rows_in_window` |
| V3 | regression_note §Vera Wave 6B | Old `output/_comparison/history_zoom_*.{json,_meta.json,png}` deleted (9 files) | `ls output/_comparison/history_zoom_* 2>&1` + `ls -la output/_comparison/` | PASS | `ls: No such file or directory` for zoom globs; dir present but empty (2 bytes: `.`/`..`) |
| V4 | regression_note §Vera Wave 6B | 3 perceptual-check PNGs regenerated; both panels visible with NBER + event markers | `ls -la output/charts/hy_ig_v2_spy/plotly/_perceptual_check_history_zoom_*.png` + Quincy renders GFC PNG independently and inspects | PASS | 3 PNGs present (dotcom 285KB, gfc 299KB, covid 303KB); QA-rendered GFC (`temp/qa_zoom_render_20260419/history_zoom_gfc.png`) confirms dual panels, shared x-axis, NBER shading on BOTH panels, event markers span both panels (Aug 2007 BNP, Mar 2008 Bear, Sep 2008 Lehman, Mar 2009 SPX trough, Jun 2009 NBER end) |
| V5 | regression_note §Vera Wave 6B | VIZ-V5 smoke test 10/10 PASS in `_smoke_test_wave6b_20260419.log` | `grep "Total:" .../_smoke_test_wave6b_20260419.log` + cat tail | PASS | `Total: 10 charts, 10 pass, 0 fail`; all 3 zoom charts listed as PASS with `traces=2` and correct titles |
| V6 | regression_note §Vera Wave 6B | Events registry (`docs/schemas/history_zoom_events_registry.json`) NOT modified | `git diff --stat docs/schemas/history_zoom_events_registry.json` | PASS | 0 changes; registry x-version unchanged (per Vera's evidence, re-checked here via grep of file existence and timestamp stability) |

### Ace's Wave 6B loader + META-ZI refinement

| # | Source | Claim | Verification command | Result | Evidence |
|---|--------|-------|----------------------|--------|----------|
| A1 | regression_note §Ace Wave 6B | `app/components/charts.py` loader drops `output/_comparison/` fallback | `Grep "output/_comparison" app/components/charts.py` | PASS | **0 hits** in charts.py; `_COMPARISON_DIR` constant removed; `_resolve_history_zoom_paths` now returns single per-pair path |
| A2 | regression_note §Ace Wave 6B | Loader functionally returns dual-panel Figure for all 3 zooms | `python3 -c "sys.path.insert...; load_plotly_chart(f'history_zoom_{ep}', pair_id='hy_ig_v2_spy'); assert len(fig.data)==2"` (keyword form) | PASS | `OK dotcom: traces=2` / `OK gfc: traces=2` / `OK covid: traces=2` |
| A3 | regression_note §Ace Wave 6B | `chart_type_registry.json` history_zoom_* entries → `expected_chart_type=dual_panel`, `override_supported=false` | `Grep "history_zoom_" docs/schemas/chart_type_registry.json -A 6` | PASS | All 5 history_zoom_* entries (dotcom, gfc, covid, taper_2018, inflation_2022) have both fields as claimed; notes text cites META-AL + VIZ-V12 and "No _comparison/ fallback" |
| A4 | regression_note §Ace Wave 6B | META-ZI text in `team-coordination.md` reflects new model | `Grep "_comparison" docs/agent-sops/team-coordination.md -n` | PASS-with-note | 6 residual `_comparison` mentions in that file, but all 6 are in historical/deprecation/anti-pattern context (lines 223, 233, 237, 518, 522, 527, 528 — explicitly labelled "superseded" / "Wrong:" / "Invalidates"). No live-contract reference. See Finding F1. |
| A5 | regression_note §Ace Wave 6B | Story page fallback_text updated away from `canonical path: output/_comparison/…` | `Grep "canonical path" app/pages/9_hy_ig_v2_spy_story.py` + `Grep "_comparison" …_story.py` | PASS | 0 hits for "canonical path"; 0 hits for `_comparison`. Fallback strings now read `expected at: output/charts/hy_ig_v2_spy/plotly/history_zoom_{ep}.json` |
| A6 | regression_note §Ace Wave 6B | smoke_loader.py passes 15/15 | `python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy` | PASS | `# RESULT  passes=15  failures=0`; all 3 history_zoom_* rows show `traces=2` with correct titles |
| A7 | regression_note §Ace Wave 6B | smoke_schema_consumers.py passes 3/3 | `python3 app/_smoke_tests/smoke_schema_consumers.py --pair-id hy_ig_v2_spy` | PASS | `# RESULT  passes=3  failures=0` (APP-WS1 winner_summary + APP-WS1 sibling interpretation_metadata + APP-DIR1 2-way agreement) |
| A8 | regression_note §Ace Wave 6B | APP-SE1 loader-contract note in appdev-agent-sop.md refined | `Read` lines 250-253 | PASS | Line 252 reads: "try `output/charts/{pair_id}/plotly/history_zoom_{episode}.json` only; if missing, render the 'chart pending' placeholder per GATE-25. There is no `output/_comparison/` fallback…" |
| A9 | regression_note §Ace Wave 6B | `chart_type_registry.schema.json` NOT modified (SCHEMA-REQUEST deferred) | `Grep "_comparison/" chart_type_registry.schema.json` | PASS-with-note | 1 hit at line 94 (description text for `override_supported`) still references the legacy META-ZI model. This is the SCHEMA-REQUEST Ace correctly flagged as non-blocking advisory text. See Finding F2. |

---

## GATE-31 Standard Checklist (12 items)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Every regression_note claim has a verification command + result | PASS | 13/13 Vera+Ace claims traced to verification above (V1–V6, A1–A9) with reproducible commands |
| 2 | All schemas validate against their instances | PASS | APP-WS1 (winner_summary vs ECON-H5), APP-WS1 sibling (interpretation_metadata vs DATA-D6) both green in smoke_schema_consumers; `_meta.json` sidecars have no declared schema so fell back to manual field-presence audit (all required META-AL fields present) |
| 3 | smoke_loader.py passes | PASS | 15/15 pass, 0 fail |
| 4 | smoke_schema_consumers.py passes | PASS | 3/3 pass, 0 fail |
| 5 | Cloud pages render for reference pair | DEFERRED | Out of scope for Wave 6B; Wave 6D handles Cloud per task instructions. Local smoke tests are sufficient for GATE-31 sign-off on this wave. |
| 6 | Zero "chart pending" on reference-pair pages (GATE-28) | PASS-with-note | 0 in chart JSON artifacts. 3 "chart pending" strings exist in `9_hy_ig_v2_spy_story.py` lines 284/312/339 as `fallback_text` arguments — these render ONLY if the loader cannot find the chart. Smoke tests confirm all 3 zooms load with `traces=2`, so these strings are dead-branch and never user-visible in the happy path. See Finding F3. |
| 7 | Direction triangulation passes (APP-DIR1) | PASS | winner_summary.direction = `countercyclical`; interpretation_metadata.observed_direction = `countercyclical`; 2-way agreement reported by smoke_schema_consumers |
| 8 | All new stakeholder items addressed in spirit | PASS | Wave 6 motivation (eyeball the pair relationship) is satisfied — see Stakeholder-Spirit Check below |
| 9 | META-XVC cross-version diff: undeclared drift = 0 | PASS (N/A) | Wave 6B is a retro-apply of META-AL on the reference pair itself; there is no successor version to diff against for the zoom-chart rewrite specifically. Existing META-XVC matrix in acceptance.md remains clean. |
| 10 | META-ELI5: no new error strings without plain-English | PASS | No new `st.error`/`st.warning` introduced in Wave 6B. Existing loud-error bodies (5C-era) retain ELI5 blocks per acceptance.md row 13. |
| 11 | Deflection audit (GATE-30): no new deflections introduced | PASS | Wave 6B introduces no new deflection resolutions. S18-2 and S18-4 remain the only two deflected items (both audited PASS in acceptance.md §Deflection Audit). |
| 12 | Any discrepancy recorded with specific evidence | PASS | All 3 PASS-with-note findings below carry file path + exact command + line numbers |
| — | At least one PASS-with-note or FAIL produced (anti-rubber-stamp) | PASS | 3 findings recorded (F1–F3) |

---

## Stakeholder-spirit check

**Wave 6 motivation (per regression_note §Lead's Wave 6A preface + stakeholder finding, 2026-04-19):**
Single-panel zooms on HY-IG v2 hid the credit → equity co-movement that the Story prose asserted. The user asked: *"Can I eyeball the pair relationship from these episode charts?"* Wave 6A set up the META-AL rule; Wave 6B is the first retro-apply against HY-IG v2.

**Verification:** QA independently re-rendered `history_zoom_gfc.png` (`temp/qa_zoom_render_20260419/history_zoom_gfc.png`) from the committed JSON (not Vera's perceptual PNG — an independent render against plotly kaleido). Inspected visually:

- **Top panel:** "HY-IG OAS Spread" (y1, orange Okabe-Ito vermilion `#D55E00`) rises from ~2 to ~15 over 2007-09 trough, peaking in late 2008.
- **Bottom panel:** "SPY Price" (y2, blue Okabe-Ito) falls from ~110 to ~70 over the same window, reaching bottom in Mar 2009.
- **Shared x-axis (2005-2010):** both panels share the date axis; eyeball the lead-lag is immediate.
- **Event markers:** 4 dashed vertical lines (Aug 2007 BNP fund freeze, Mar 2008 Bear Stearns, Sep 2008 Lehman, Mar 2009 SPX trough, Jun 2009 NBER end) span BOTH panels, anchoring the narrative beats to the data.
- **NBER shading:** rose/mauve rectangles on both panels cover the 2007-12 → 2009-06 recession window.

Verdict: **the user CAN eyeball the pair relationship**. Spread spike (top) clearly leads / is concurrent with SPY crash (bottom); the stakeholder concern that motivated Wave 6 is resolved in spirit, not just in letter.

Same pattern confirmed on dotcom and covid renders (both produced at `temp/qa_zoom_render_20260419/`).

**Stakeholder-spirit check: PASS.**

---

## Cross-agent seam audit

| Seam | Path expected by Ace's loader | Path Vera's files actually land at | Match? |
|------|-------------------------------|--------------------------------------|--------|
| history_zoom_dotcom | `output/charts/hy_ig_v2_spy/plotly/history_zoom_dotcom.json` | `output/charts/hy_ig_v2_spy/plotly/history_zoom_dotcom.json` (79KB, 10 shapes, 2 traces) | **YES** |
| history_zoom_gfc | `output/charts/hy_ig_v2_spy/plotly/history_zoom_gfc.json` | `output/charts/hy_ig_v2_spy/plotly/history_zoom_gfc.json` (115KB, 12 shapes, 2 traces) | **YES** |
| history_zoom_covid | `output/charts/hy_ig_v2_spy/plotly/history_zoom_covid.json` | `output/charts/hy_ig_v2_spy/plotly/history_zoom_covid.json` (79KB, 8 shapes, 2 traces) | **YES** |

Including the `/plotly/` subdirectory. No drift. smoke_loader.py runs the loader against Vera's actual artifacts and reports 2 traces per chart in all 3 cases — the happy-path contract holds end-to-end.

**Seam audit: PASS.**

---

## Findings

### F1 — PASS-with-note: `team-coordination.md` retains 6 historical `_comparison` mentions

- **File:** `docs/agent-sops/team-coordination.md`
- **Lines:** 223, 233, 237, 518, 522, 527, 528
- **Observation:** Ace's claim is that META-ZI was rewritten; verified TRUE. However, 6 `_comparison` mentions remain in the document. Each is in explicit historical-deprecation context ("superseded", "Wrong:", "Invalidates", "scheduled for refinement in Wave 6B"). None represents a live contract.
- **Severity:** Advisory. The text reads correctly as "what the old model was, why it failed, what superseded it" — exactly what META-AL §Abstraction-Layer Discipline expects. But a future reader scanning for the current rule may first encounter the historical passages.
- **Recommendation:** Non-blocking. A future Lead housekeeping pass could add an inline "(superseded — see §META-AL)" marker at the first mention, or move the historical passages to a §History appendix.
- **Action:** Added to backlog per META-BL.

### F2 — PASS-with-note: `chart_type_registry.schema.json` description text lags

- **File:** `docs/schemas/chart_type_registry.schema.json`
- **Line:** 94 (`override_supported` description)
- **Observation:** Description still reads "True for charts that support the META-ZI canonical-override protocol… lives under output/_comparison/; pair-specific override under output/charts/{pair_id}/." — which describes the LEGACY model. Instances correctly have `override_supported=false`, so no consumer is misled, but the schema's self-documenting text is stale.
- **Severity:** Advisory (as Ace correctly flagged it via SCHEMA-REQUEST in the dotcom notes field, within Vera's schema-authority boundary).
- **Recommendation:** Non-blocking. Vera to update description text in the next schema version bump; coordinate with META-CF schema-versioning rule.
- **Action:** Confirms Ace's SCHEMA-REQUEST; Vera owns the fix per role separation.

### F3 — PASS-with-note: Story page retains 3 "chart pending" fallback strings

- **File:** `app/pages/9_hy_ig_v2_spy_story.py`
- **Lines:** 284, 312, 339
- **Observation:** Story page passes `fallback_text="Dot-Com zoom chart pending (expected at: …)"` (and GFC/COVID equivalents) as keyword argument to `load_plotly_chart`. These strings are invisible while the chart files exist (smoke tests confirm all 3 load with 2 traces). GATE-28 is satisfied *in the rendered DOM* because the happy path never triggers the fallback branch.
- **Severity:** Advisory. Strictly a dead-branch concern — there IS no "chart pending" in the user-visible output. But if someone ever deletes a zoom JSON (or the loader regresses), the string would re-surface.
- **Recommendation:** Non-blocking. Consider adding a VIZ-V5-style pre-flight assertion in the Story page module that raises if any of the 3 zoom JSONs are missing at import time (fail-fast vs silent-placeholder). Could be a Wave 7 item.
- **Action:** Added to backlog per META-BL.

---

## Additional observation — dual-purpose `_comparison/` directory

**Non-blocking observation for the central commit:** `output/_comparison/` is now empty but still exists. `docs/agent-sops/appdev-agent-sop.md` line 845 describes it as a legitimate location for "cross-pair comparison charts" (a different purpose from the deprecated zoom-chart fallback). If Lead's central commit decides to keep the directory for that cross-pair use, it should stay empty today; if the cross-pair use is itself deprecated, the directory could be removed entirely. Either way this is a Lead-decision housekeeping item, not a QA blocker — Ace already noted it in his regression section.

---

## Sign-off decision

**Decision: PASS.** All producer claims verified. All GATE-31 items PASS or reasonably deferred (Cloud → Wave 6D). 3 PASS-with-note findings recorded — none blocking. Cross-agent seam is clean. Stakeholder-spirit check satisfied (the eyeball-pair-relationship concern that drove Wave 6 is measurably resolved on the reference pair).

- **acceptance.md sign-off unblocked** for Wave 6B central commit. Lead is free to commit and advance the "Current commit" field.
- **Lead override invoked?** No — not required; no FAIL findings.
- **Blocking items returned to producers?** None.

---

## QA sign-off

**Approved by:** Quincy (QA)
**Date:** 2026-04-19
**Notes:**
- First production QA run on the new QA role. Protocol feedback for future waves: running both smoke tests and a Python kwargs-correct loader probe as a triple-check on the loader-seam is a useful pattern — recommend promoting to a reusable QA snippet.
- Observed minor concern (not a finding): the positional-call form `load_plotly_chart('history_zoom_dotcom','hy_ig_v2_spy')` silently returns None because `'hy_ig_v2_spy'` binds to `fallback_text` in the current signature, not `pair_id`. The keyword form is correct and both smoke tests use it correctly — but a future schema bump could consider a positional-only / keyword-only separator to prevent mis-invocation. Out of Wave 6B scope; logging as a Quincy memory for potential rule authorship in a later wave.
- Wave 6C (this run) exits successfully; Wave 6D (Cloud re-verification after central commit) is Lead's to schedule.

**Handoff to Lead:** this file + appended section in `acceptance.md` below.

---

# QA Verification — Wave 7 (2026-04-20, Quincy)

## Summary

**Total checks: 25**
- PASS: 21
- PASS-with-note: 3
- FAIL: 1
- Blocking: 1

**Sign-off decision: BLOCK** — one stakeholder-visible scope-leak contradiction in `app/pages/9_hy_ig_v2_spy_methodology.py` and `app/pages/9_hy_ig_v2_spy_story.py` that directly contradicts Ray's Wave 7B narrative and Evan's `signal_scope.json`. Narrow fix scope; Ace or Ray to remediate (hand-off decision for Lead). Recommend a Wave 7B hotfix and one-shot QA re-verification before the central commit.

## Claims matrix

### Lead (Wave 7A) — ALL PASS

| # | Claim | File | Verification | Result |
|---|-------|------|--------------|--------|
| L1 | 3 new ECON rules (SD/UD/AS) | `docs/agent-sops/econometrics-agent-sop.md` | `grep -n "^### ECON-SD\|^### ECON-UD\|^### ECON-AS"` | 3 lines, in order (991/1022/1058). **PASS** |
| L2 | signal_scope.schema.json + example | `docs/schemas/signal_scope.{schema,examples/signal_scope.example}.json` | `validate_schema.py` default + strict | exit 0 twice. **PASS** |
| L3 | analyst_suggestions.schema.json + example | `docs/schemas/analyst_suggestions.{schema,examples/analyst_suggestions.example}.json` | `validate_schema.py` default + strict | exit 0 twice. **PASS** |
| L4 | 3 rows appended to standards.md | `docs/standards.md` | `grep -n "^| ECON-SD\|^| ECON-UD\|^| ECON-AS"` | 3 lines (102/103/104). **PASS** |
| L5 | team-coordination Scope Discipline subsection | `docs/agent-sops/team-coordination.md:580` | `grep -n "### Scope Discipline"` | 1 line. **PASS** |

### Evan (Wave 7B) — ALL PASS

| # | Claim | File | Verification | Result |
|---|-------|------|--------------|--------|
| E1 | 17 indicator + 10 target derivatives | `results/hy_ig_v2_spy/signal_scope.json` | `python3 -c "json.load ...; len(derivatives)"` | 17 / 10. **PASS** |
| E2 | 5 off-scope suggestions | `results/hy_ig_v2_spy/analyst_suggestions.json` | same | 5 entries. **PASS** |
| E3 | Strict schema validation of both | both | `validate_schema.py ... --strict` | exit 0 twice. **PASS** |

### Vera (Wave 7B) — ALL PASS

| # | Claim | File | Verification | Result |
|---|-------|------|--------------|--------|
| V1 | correlation_heatmap.json has 0 off-scope rows | `output/charts/hy_ig_v2_spy/plotly/correlation_heatmap.json` | regression-note Python snippet | leak=[], 8 rows all in-scope. **PASS** |
| V2 | Title updated to "HY-IG Derivatives vs SPY Forward Returns" | same | JSON field `layout.title.text` | matches verbatim, with sub-title "Top-8 by \|correlation\| at the 63-day horizon, drawn from 17 HY-IG derivatives in signal_scope.json". **PASS** |
| V3 | `_meta.json` carries `signal_scope_ref`, `signal_scope_schema_version`, `palette_id`, `off_scope_signals_removed` | `output/charts/hy_ig_v2_spy/plotly/correlation_heatmap_meta.json` (sidecar filename; the regression-note referred to it as `_meta.json`) | Python dict lookups | all 4 fields present and correct. **PASS-with-note** (filename convention is `<chart>_meta.json`, not a single `_meta.json` — producer regression-note prose uses the shortened name; flag for ECON-UD doc polish, not a defect). |
| V4 | Per-pair-prefixed copy `hy_ig_v2_spy_correlation_heatmap.json` also filtered | same dir | Python load, y-axis rows | identical 8-row label set; title matches. **PASS** |

### Ray (Wave 7B) — 1 FAIL + 1 PASS

| # | Claim | File | Verification | Result |
|---|-------|------|--------------|--------|
| R1 | "Signal Universe" + "Analyst Suggestions for Future Work" sections + frontmatter anchors | `docs/portal_narrative_hy_ig_v2_spy_20260410.md` | section-heading grep + yaml parse | 807/828 sections present; anchors `signal-universe` / `analyst-suggestions` in `pages.methodology.sections`. Frontmatter validates against `docs/schemas/narrative_frontmatter.schema.json` (exit 0). **PASS** |
| R2 | "Off-scope signal references in analytical context: 0 (was 3)" | narrative markdown | grep for CCC-BB / NFCI / BBB-IG in analytical context | narrative `.md` is clean (CCC-BB references are explicitly tagged off-scope per ECON-SD). **PASS for the `.md` artifact.** **FAIL at the stakeholder-visible seam:** the rendered portal pages (`.py`) still assert CCC-BB as in-scope (`app/pages/9_hy_ig_v2_spy_methodology.py:149` — "...acceleration, and the CCC-BB quality spread"; `:352` — table row reads `Signals (13) \| ... quality spread (CCC-BB) ...`; `app/pages/9_hy_ig_v2_spy_story.py:369/380/386` — the CCC-BB expander still claims CCC-BB is "one of our tournament signals (S5)"). Stakeholder who reads the portal still sees the scope leak. |

### Ace (Wave 7B) — ALL PASS

| # | Claim | File | Verification | Result |
|---|-------|------|--------------|--------|
| A1 | signal_universe_table.py renders the registry (150 lines, `validate_or_die` against `signal_scope`) | `app/components/signal_universe_table.py` | wc -l + grep for `validate_or_die(instance_path, "signal_scope")` | 150 lines, validator call present. **PASS** |
| A2 | analyst_suggestions_table.py renders suggestions (129 lines, `validate_or_die` against `analyst_suggestions`) | `app/components/analyst_suggestions_table.py` | wc -l + grep | 129 lines, validator call present. **PASS** |
| A3 | Methodology page calls both renderers | `app/pages/9_hy_ig_v2_spy_methodology.py:171, 191` | grep imports + calls | imports at 21-22, calls at 171 / 191, section headings + intro prose in place. **PASS** |
| A4 | `smoke_loader.py` — 15 passes / 0 failures | same | ran | `passes=15 failures=0`. **PASS** |
| A5 | `smoke_schema_consumers.py` — 5 passes / 0 failures (extended from 3) | same | ran | `passes=5 failures=0` — now includes `ECON-UD: signal_scope` and `ECON-AS: analyst_suggestions`. **PASS** |

## Stakeholder-spirit check (critical for Wave 7)

The stakeholder's Wave 6 ask was: **"If I see a correlation on this heatmap, can I trace it back to a derivative of HY-IG? Can I see the full universe? Can I see what else the team considered?"**

- **Heatmap traceability** — YES. Every row label on `correlation_heatmap.json` maps 1:1 to an in-scope derivative in `signal_scope.json` (verified: all 8 rows are `hy_ig_*` derivatives with `role` ∈ {raw, derivative, diagnostic}; no `NFCI / Bank / Yield Curve / BBB / CCC` signals remain).
- **Full universe disclosure** — YES at the data layer (17 + 10 derivatives in `signal_scope.json`). YES at the Methodology-page-component layer (`signal_universe_table.py` renders both tables via `validate_or_die`). Rendering works on smoke test.
- **Alternatives logged** — YES. `analyst_suggestions.json` has all 5 entries (NFCI, Bank/Small-Cap, Yield Curve, BBB-IG, CCC-BB) with honest caveats and "proposed by evan" attribution. `analyst_suggestions_table.py` surfaces this read-only with the mandated disclaimer.

**Partial fail:** the stakeholder who opens the *rendered* Methodology and Story pages still reads prose that calls CCC-BB an in-scope tournament signal (see R2 FAIL). The contract/data layer is clean; the prose layer on the portal is not. If the stakeholder cross-checks the prose against the rendered Signal Universe table (17 derivatives, none CCC-BB), they will notice the contradiction and re-flag. **Wave 7 scope-discipline claim is not fully satisfied until the .py prose matches the .md narrative.**

## GATE-31 Standard Checklist (12 items)

| # | Item | Result | Evidence |
|---|------|--------|----------|
| 1 | Every regression-note claim has verification command + result | PASS | All 5 producer sections include Verification + Result bullets; this QA report maps each claim to a command |
| 2 | All schemas validate against instances | PASS | 4 validator runs — 2 example + 2 instance — all exit 0; narrative frontmatter validates exit 0 |
| 3 | `smoke_loader.py` failures = 0 | PASS | `passes=15 failures=0` log at `app/_smoke_tests/loader_hy_ig_v2_spy_20260420.log` |
| 4 | `smoke_schema_consumers.py` failures = 0 | PASS | `passes=5 failures=0` log at `app/_smoke_tests/schema_consumers_hy_ig_v2_spy_20260420.log` — 2 new cases added per Ace's extension |
| 5 | Cloud pages render for reference pair | DEFERRED | Wave 7D, per dispatch. Local is this run |
| 6 | Zero "chart pending" on reference-pair pages (GATE-28) | PASS-with-note | 3 matches in `9_hy_ig_v2_spy_story.py` but all are guarded fallback text inside branches that do NOT fire when the JSON artifact exists (loader smoke confirms Dot-Com / GFC / COVID charts all load with traces=2). The guarded strings are pre-existing legit defensive paths, not exposed placeholders |
| 7 | Direction triangulation (APP-DIR1) | PASS | Evan winner_summary.direction=`countercyclical`, Dana interp_metadata.observed_direction=`countercyclical`, Ray frontmatter.direction_asserted=`countercyclical`. 3-way match |
| 8 | Stakeholder items addressed in spirit | PARTIAL | Data + component layer clean; portal .py prose contradicts both. See FAIL R2 |
| 9 | META-XVC cross-version diff | PASS | All 4 producers recorded a Prior-version observation block. Each frames the additive work as improvement over Sample HY-IG v1 rather than drift |
| 10 | META-ELI5 on new Methodology sections + table components | PASS | `signal_universe_table.py` has APP-CC1 "What this shows:" captions above both tables and 1-line takeaway captions below; `analyst_suggestions_table.py` has `st.info` disclaimer, plain-English fallback on missing file and empty array |
| 11 | Deflection audit (GATE-30) | PASS | No new deflections introduced by Wave 7. Existing deflections from prior waves unchanged |
| 12 | Discrepancy recorded with evidence | PASS | R2 FAIL recorded with 5 exact line citations in the .py files |
| — | At least one PASS-with-note (no rubber-stamping) | PASS | V3 (`_meta.json` vs `<chart>_meta.json` naming), GATE-28 (guarded fallback strings), and implicit observations below |

## Cross-Pair Scope-Leak Inventory (flag-only)

I scanned the 6 other completed pairs for off-scope signals in any exploratory correlations file and in any correlation chart y-axis labels:

| Pair | Scope leak in heatmap / correlations chart? | Off-scope signals found | Suggested action |
|------|---------------------------------------------|-------------------------|------------------|
| indpro_spy (Pair #1) | NO | chart `indpro_spy_correlations.json` rows are all `IP *` (accel, contraction, dev_trend, mom, mom_3m, mom_6m, yoy, zscore_60m); `results/indpro_spy/exploratory_20260314/correlations.csv` contains only `indpro_*` signals | none |
| sofr_ted_spy (Pair #2) | NO | chart rows are all spread-derivatives (mom_21d/63d, pctrank_252d, roc_21d/63d, stress, vol_21d, zscore_126d/252d); csv same | none |
| dff_ted_spy (Pair #2 variant) | NO | identical row set; csv same | none |
| ted_spliced_spy (Pair #2 variant) | NO | identical row set; csv same | none |
| permit_spy (Pair #3) | NO | chart rows are all `permit_*` (accel, contraction, dev_trend, mom, mom_3m, mom_6m, yoy, zscore_60m); csv same | none |
| vix_vix3m_spy (Pair #11) | NO | chart rows are all `VR *` + `backwardation / ratio / term_spread` (all VIX-family derivatives); csv same | none |
| hy_ig_spy (sample, Pair #20) | N/A | no correlation chart exists; no `exploratory_*/correlations.csv` under `results/hy_ig_spy/` | retro-apply signal_scope / analyst_suggestions per META-RPD if the sample pair is ever re-ran as a reference |

**Finding:** HY-IG v2 was a unique outlier. It was the only pair whose exploratory phase pulled cross-indicator comparisons (NFCI / Bank-KBE / Yield Curve / BBB / CCC) directly into the correlation chart Vera rendered. Every other pair's correlation chart is already ECON-SD-compliant by construction — their exploratory phase only pulled derivatives of the named indicator.

**Backlog recommendation:** No `BL-00X` entries are warranted from the cross-pair audit alone — the other 5 pairs are clean. The recommended backlog items are instead driven by Wave 7 roll-forward, not by scope leak:

- **BL-701 (proposed):** Retro-produce `signal_scope.json` for the 5 clean pairs (indpro, sofr_ted, dff_ted, ted_spliced, permit_spy, vix_vix3m) — not because of any leak, but to establish uniform ECON-UD compliance across the pair portfolio before more pairs are added. Producer: Evan. Gate: M (medium).
- **BL-702 (proposed):** Author `analyst_suggestions.json` for the same 5 pairs as empty-array placeholders (or lightly populated if the respective pair brief has ideas captured). Producer: Evan. Gate: L (low).

Lead decides whether to file these; per dispatch, QA does NOT write to `docs/backlog.md` directly.

## Observations (QA memory candidates)

1. **Narrative-to-portal seam is implicit.** The project treats `docs/portal_narrative_*_<date>.md` as the canonical prose, but the .py portal pages render their own literal strings. When Ray rewrites the .md, nothing propagates automatically. Wave 7 surfaced this: Ray's cleanup is honest at the .md layer but invisible at the portal layer. **Candidate new rule** (META-NP? RES-??) for Lead/Ray/Ace to discuss: "Every narrative section revision with a scope-discipline label must also update the corresponding portal-page string with a paired diff; QA verifies at both layers." Filing to `~/.claude/agents/qa-quincy/memories.md` after this run.
2. **Chart sidecar filename convention.** Vera's regression-note shorthand `_meta.json` is close to but not the actual filename (`<chart>_meta.json`). Minor doc polish for the ECON-UD/VIZ-V5 sections.
3. **Cross-pair ECON-UD retro.** The 5 clean pairs are ECON-SD-compliant by luck of construction, not by contract. Without a `signal_scope.json` on record, a future pipeline re-run that silently adds a cross-indicator signal to any of those pair's exploratory_*/correlations.csv would NOT be caught by Quincy unless we run a per-pair scope audit every time. Uniform ECON-UD retro (BL-701 above) would make this a schema-enforced guarantee rather than a convention.

## FAIL / BLOCKING items (detail)

**R2 — Ray's Wave 7B claim "off-scope in analytical context: 0 (was 3)" is FAIL at the stakeholder-visible portal layer.**

- **Claim made:** all 3 pre-Wave-7 off-scope references resolved.
- **Evidence:** narrative markdown (`docs/portal_narrative_hy_ig_v2_spy_20260410.md`) is clean. The prose at lines 330-337 explicitly labels CCC-BB as "off-scope for this pair under ECON-SD" with the full disclaimer. Data Sources section at line 748 splits into in-scope / exploratory-only. All of this is correct at the markdown layer.
- **What Quincy found:** portal .py files still carry the stale pre-Wave-7 prose:
  - `app/pages/9_hy_ig_v2_spy_methodology.py:149` — "...acceleration, **and the CCC-BB quality spread.**"
  - `app/pages/9_hy_ig_v2_spy_methodology.py:352` — tournament-design table row reads `Signals (13) | ... **quality spread (CCC-BB)**, HMM stress prob, Markov-switching prob`
  - `app/pages/9_hy_ig_v2_spy_story.py:369` — "*(The CCC-BB quality spread.)*" as an alternative-headline answer
  - `app/pages/9_hy_ig_v2_spy_story.py:380` — "During the GFC, the CCC-BB quality spread began widening months..." (educational prose, can be retained per Ray's own tricky-phrasing decision #1 — but the next line must add the scope disclaimer)
  - `app/pages/9_hy_ig_v2_spy_story.py:386` — "We include the CCC-BB quality spread as one of our tournament signals (S5)..." — this directly contradicts `signal_scope.json` (17 derivatives, none is CCC-BB) and also contradicts the Methodology Signal Universe table Ace renders from that same JSON
- **Severity:** Blocking. A stakeholder opening the portal reads CCC-BB as "one of our 13 tournament signals" and simultaneously reads from the Signal Universe table that there are 17 derivatives, none of which is CCC-BB. Direct internal contradiction at the stakeholder-visible layer.
- **Fix scope (narrow):** 4 tiny .py edits (M:149, M:352, S:369, S:386) to mirror Ray's .md decisions: for expository prose, retain the "canary in coal mine" context + append scope disclaimer + point to `analyst_suggestions.json`; for list membership claims (`:149, :352, :386`), remove CCC-BB from the in-scope enumeration (it is not in `signal_scope.json.indicator_axis`).
- **Owner recommendation:** Lead to dispatch a Wave 7B hotfix. Ace or Ray are both plausible owners — Ace owns the .py files in the conventions tree; Ray owns the prose content. The narrow-fix scope is small enough either can execute; I defer to Lead.
- **Re-verification by QA:** one-shot grep of the 5 citations + one re-run of `smoke_loader.py` (no regression expected because the edits are pure string changes to already-rendered `st.markdown` blocks).

---

## QA sign-off

**Decision: BLOCK.**

**Approved by:** Quincy (QA)
**Date:** 2026-04-20

**Blocking items:**
- R2: CCC-BB prose leak in 2 portal .py files (5 exact citations above). Narrow .py-only fix.

**Non-blocking observations (PASS-with-note, logged for future polish):**
- V3: Vera's regression-note shorthand `_meta.json` (actual filename `correlation_heatmap_meta.json`)
- GATE-28 guarded-fallback strings in story.py (pre-existing; loader proves no exposure)
- Cross-pair ECON-UD retro recommended (BL-701, BL-702 proposed to Lead)

**Handoff to Lead:**
- This file + block above is the full evidence pack.
- Once Ace/Ray fixes R2, re-verification is a 2-minute QA re-run (5 greps + loader smoke).
- `acceptance.md` is NOT updated in this run because sign-off is BLOCK. On re-verification PASS, QA will append a `## QA Verification (Wave 7, <date>)` block there.

---

## Wave 7C-2 Re-Verification (2026-04-20, Quincy)

### Summary of BLOCKING finding from 7C-1

Wave 7C-1 blocked on R2: 5 prose citations in portal `.py` files asserted CCC-BB as an in-scope tournament signal, directly contradicting `signal_scope.json` (17 HY-IG derivatives, none CCC-BB) and the Methodology Signal Universe table Ace rendered from that JSON. A stakeholder reading the portal would have seen the contradiction.

### Ace's remediation (from regression_note §"Ace's Wave 7B fix-up: CCC-BB prose leak")

- `app/pages/9_hy_ig_v2_spy_methodology.py` L149: CCC-BB removed from the in-scope derivative enumeration; replaced with a pointer to `signal_scope.json` + scope disclaimer.
- `app/pages/9_hy_ig_v2_spy_methodology.py` L352: Tournament-design table row hardcoded "Signals (13) | … quality spread (CCC-BB)" replaced with non-counted "Signals | … acceleration, HMM stress/calm probabilities, Markov-switching stress probability. Authoritative list: see Signal Universe rendered from `signal_scope.json`." (CCC-BB removed; count mismatch 13 vs 17 resolved by deferring to Signal Universe.)
- `app/pages/9_hy_ig_v2_spy_story.py` L369: Expander retitled "Deeper dive (background only — out of scope for this pair)"; CCC-BB reframed as "educational background" pointer.
- `app/pages/9_hy_ig_v2_spy_story.py` L380: GFC / COVID quality-spread narrative reframed as "general market observation" not "our analysis".
- `app/pages/9_hy_ig_v2_spy_story.py` L386 (now L387 after edits): final paragraph rewritten to an explicit Scope note pointing to Analyst Suggestions + `signal_scope.json`.
- Bonus audit: Data Sources table at methodology.py L126-144 gated row labels with "in scope" vs "context only" + scope-discipline footnote naming all 5 off-scope signals.

### Re-verification commands + results

| # | Check | Command | Result |
|---|-------|---------|--------|
| 1 | Primary scope grep (was 5 matches) | `grep -n -E "CCC-BB.*signal\|CCC.*S5\|CCC-BB.*tournament\|tournament.*CCC" app/pages/9_hy_ig_v2_spy_story.py app/pages/9_hy_ig_v2_spy_methodology.py` | **0 hits.** PASS |
| 2 | methodology.py L149 | Read file | PASS — enumeration ends at "acceleration"; CCC-BB moved behind scope disclaimer + signal_scope.json pointer. |
| 3 | methodology.py L352 | Read file | PASS — "Signals" row no longer hardcodes a count, omits CCC-BB, defers to Signal Universe. |
| 4 | story.py L369 | Read file | PASS — now reads "The CCC-BB quality spread — educational background" inside an expander titled "Deeper dive (background only — out of scope for this pair)". |
| 5 | story.py L380 | Read file | PASS — "As a general market observation, during the GFC the CCC-BB quality spread…" — properly reframed as general observation, not in-scope claim. |
| 6 | story.py L386 (now L387 region) | Read file | PASS — final block is an explicit Scope note: "The CCC-BB quality spread is **not** part of this pair's analytical universe." + pointer to Analyst Suggestions. |
| 7 | Data Sources gating at methodology.py L126-144 | Read file | PASS — 6 table rows now labelled either **(in scope)** or **(context only)**; scope-discipline footnote cites ECON-SD and names all 5 off-scope signals (NFCI Momentum, Bank/Small-Cap Ratio, Yield Curve 10Y-3M, BBB-IG Spread, CCC-BB Quality Spread) as being routed to Analyst Suggestions. |
| 8 | story.py L213 claim ("pointer to OTHER pairs") | Read file | PASS — lines 208-215 are a Scope note saying "See the separate analyses on **VIX x SPY** and **Yield Curve x SPY** for deep dives on those related signals; here we keep the lens on credit." This is an out-of-pair pointer, not an in-scope claim. |
| 9 | smoke_loader.py | `python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy` | `passes=15 failures=0`. PASS |
| 10 | smoke_schema_consumers.py | `python3 app/_smoke_tests/smoke_schema_consumers.py --pair-id hy_ig_v2_spy` | `passes=5 failures=0`. PASS |

### Observation on rewrite quality (anti-rubber-stamp)

Ace's rewrite is substantively correct, not just scope-compliant. One concrete example: the L352 hardcoded signal count `Signals (13)` contradicted `signal_scope.json` (17 derivatives) independently of the CCC-BB leak. Ace removed the count entirely and deferred to the rendered Signal Universe — which is the right architectural fix because any future schema addition would silently re-break the count. Minor note: the expander heading reframe at L366 uses an em-dash `— out of scope` where the rest of the page uses a `--` double-hyphen (ASCII fallback) — not a defect but a small stylistic inconsistency in the scope-note vocabulary that Vera/Ray could standardise in a future META-ELI5 polish pass. Log to `~/.claude/agents/qa-quincy/memories.md`.

### Updated sign-off

**Decision: PASS** (previously BLOCK on 7C-1).

- All 5 blocking citations resolved; primary grep is now 0 hits.
- Remaining CCC-BB mentions in the two files are all (a) scope-note pointers to Analyst Suggestions, (b) educational-background content explicitly flagged "out of scope for this pair", or (c) Data Sources rows labelled "context only" with ECON-SD footnote.
- Secondary Ace claims (Data Sources gating, story L213 pointer) verified.
- Smoke tests remain green.
- **acceptance.md** Wave 7 section now unblocked for append; updating in this same pass per dispatch instruction.

**Approved by:** Quincy (QA)
**Date:** 2026-04-20
**Wave:** 7C-2 (re-verification after 7C-1 BLOCK)
