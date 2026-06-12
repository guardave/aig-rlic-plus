# Viz Vera — Session Notes

**Project:** AIG-RLIC+
**Session window:** 48-hour continuous run, 2026-04-18 → 2026-04-20
**Agent identity:** Vera (Viz specialist)
**Current branch:** `main`

## Wave 10H.1 Session — 2026-04-22

**Task:** VIZ-O1 (disposition mandate) + VIZ-E1 (exploratory sidecar spec) first implementation.

**Delivered:**
1. `scripts/backfill_chart_dispositions.py` — idempotent migration. First run: `{"consumed":62,"suggested":3,"unchanged":0,"errors":0}`. Rerun: all 65 unchanged.
2. `results/hy_ig_v2_spy/analyst_suggestions.json` — added top-level `exploratory_charts` key (3 entries) alongside Evan's existing `suggestions` array (LEAD-DL1 shared-file split honoured).
3. Generator updates: `generate_charts_hy_ig_spy.py`, `retro_fix_hy_ig_v2_vera_20260411.py`, `generate_charts.py` — now emit `"disposition": "consumed"` on future runs. Four other per-pair generators have no sidecar-writer function to patch — flagged as follow-up refactor candidate.

**ELI5 authorship:** 3 orphan charts each got a 3-4 sentence plain-English caption (no jargon, no model names) + a one-line analyst rationale. Lead earlier flagged the audit on these three; now surfaced through the Methodology-page Exploratory Insights section rather than deleted.

**Handoff:** `results/_cross_agent/handoff_vera_wave10h1_20260422.md`. Parallel: Ace implementing APP-PT2 consumer — both commits are backward-compatible either order.

**Learning:** the dispatch said "65 sidecars" but the glob `output/charts/*/plotly/*_meta.json` currently matches exactly 65 across 5 pair dirs (the 19 files under `metadata/` are outside that glob — they're an older convention and will be handled in a future wave if needed).

## Wave 10F Session — 2026-04-22

**Task:** Complete HY-IG v2 bare-name migration (deferred from commit 3c6bb50).
**Outcome:** 12 charts + 12 _meta.json sidecars renamed via `git mv`. No conflicts found. Zero consumer code hits on prefixed chart names. Smoke tests: hy_ig_v2_spy 15/0, indpro_xlp 8/0, umcsent_xlv 7/0. Committed 27fb01f and pushed.
**Flagged for audit:** `hero_spread_vs_spy`, `spread_history_annotated`, `tournament_sharpe_dist` — zero references in consumer code, possibly stale.
**Unblocked:** Ace can now remove the loader fallback (Wave 10F item 6).

wc -l evidence (pre-session): experience.md 87L, memories.md 88L, session-notes.md 109L.

## Session Summary

This session covered Waves 3 through 7B of the HY-IG v2 reference-pair hardening, plus the Wave 9B memory-catch-up that produced this file. The common thread: **converting prose-specified visual conventions into machine-readable contracts with perceptual validation gates**, and **retro-applying those contracts to the reference pair** so future pairs inherit a clean template.

## Commits with Vera-Touched Files (recent)

| Commit | Description | Vera touch |
|--------|-------------|-----------|
| `a2f6570` | Wave 7: ECON scope discipline — filter correlation heatmap to pair derivatives | Regenerated `correlation_heatmap.json`, renamed title to "HY-IG Derivatives vs SPY Forward Returns", added `signal_scope_ref` to sidecar. |
| `fbb834a` | Wave 6D: dual-panel zooms verified on Cloud + META-FRD escalation | Perceptual verification of the Wave 6B dual-panel rebuilds on Streamlit Cloud. |
| `17a73ce` | Wave 6: QA role + META-AL/SRV + dual-panel zoom retro-fix | Rebuilt 3 zoom charts as dual-panel per META-AL; deleted 3 old single-panel canonical files from `output/_comparison/`. |
| `049fa3f` | Wave 5D: Cloud verification PASS after manual Reboot + late artifacts | Cloud verification of Wave 5C retro-apply. |
| `f7587a3` | Wave 5C: retro-apply 24 new Wave-5B rules to HY-IG v2 | Migrated 6 HY-IG v2 chart JSONs to `okabe_ito_2026` palette + registered events + named annotation strategies; palette lint passes; smoke 10/10. |
| `342f48c` | Wave 5B: 24 new rules + 10 new schemas/registries from validation audits | Authored VIZ-V11, V12, V13 + `color_palette_registry.json` + `history_zoom_events_registry.json` + schemas + examples. |
| `d6e4f02` | Wave 5 validation audits | Reviewed `docs/validation-audit-20260419-vera.md` — 3 HIGH-severity reproducibility gaps flagged that became V11 / V12 / V13. |
| `519d042` | SOP Part F Wave 3: gate fixes + retro-apply (stakeholder bugs) | Revised VIZ-V2 (NBER alpha 0.20–0.28, subplot rule, META-PV perceptual check); authored V3 (no silent fallbacks), V4 (no silent drops), V5 (smoke test). |

## Wave-by-Wave Summary

**Wave 3** — Stakeholder review surfaced SL-2 (NBER shading imperceptible on HY-IG v2 hero) and S18-8 / S18-11 (silent chart drops + silent fallbacks). Revised VIZ-V2 alpha prescription; added VIZ-V3, V4, V5. First chart-level rebuild of the hero (perceptible shading + caption disclosure + annualized-return callout + subplot coverage on both panels).

**Wave 5B-2** — Authored the three registry-backed rules (V11 palette, V12 events, V13 annotation strategies). Bootstrapped both registries with the `okabe_ito_2026` palette and the 5-episode event set. All schemas validated exit-0.

**Wave 5C** — Retro-applied the three new rules to 6 existing HY-IG v2 chart JSONs via in-place JSON mutation. Declared methodological divergence from v1 (which shipped matplotlib defaults) in the regression note. Palette lint passes; smoke 10/10; perceptual PNGs regenerated.

**Wave 6B** — META-AL (abstraction-layer discipline) killed the canonical-rendered-chart fallback. Rebuilt 3 zoom charts as dual-panel (indicator on top, target on bottom, shared x-axis, markers + shading on both panels). Deleted 9 files from the now-defunct `output/_comparison/` tier. Perceptual PNGs confirm dual-panel structure.

**Wave 7B** — Evan's scope-discipline rule (ECON-SD) required me to drop 5 off-scope traces (NFCI, Bank/Small-Cap, Yield Curve 10y-3m, BBB-IG, CCC-BB) from the correlation heatmap and honestly rename the title. Sidecar now records `signal_scope_ref` + `off_scope_signals_removed` list for audit.

**Wave 9B (this dispatch)** — Memory catch-up. Updated global `experience.md` (timeless patterns), global `memories.md` (specific incidents), project file `aig-rlic-plus.md` (current VIZ rule set + HY-IG v2 chart inventory), and authored this session-notes file.

## Key Cross-Agent Coordination

- **Evan (Wave 7A)** authored ECON-SD + signal_scope.json — I consumed it in Wave 7B to filter the heatmap.
- **Ray** flags historical episodes in narrative; I render the dual-panel zoom per episode. Ray may propose registry additions via PR; I own the merge + `x-version` bump.
- **Ace** consumes my chart JSONs via `load_plotly_chart("{chart_type}", pair_id="{pair_id}")`. Filename canon is rigid: `output/charts/{pair_id}/plotly/{chart_type}.json` — pair_id is in the path only.
- **Quincy (QA)** runs GATE-24, GATE-25, GATE-27, GATE-29, GATE-31 against my deliveries. VIZ-V5 smoke log + perceptual PNG sidecars are required before handoff.

## Open Items for Next Session

- **Legacy pair-id-prefixed filenames** (e.g., `hy_ig_v2_spy_correlation_heatmap.json`) still exist alongside the canonical `correlation_heatmap.json`. They are audit-trail residues from earlier runs and do not block the loader; housekeeping question for central commit decision.
- **`output/_comparison/` directory** is empty post-Wave-6B but still exists. Directory removal left for Quincy/central commit.
- **Ray's GFC 2-sigma band overlay candidate** (flagged low-priority in Wave 2 coherence review) — produce only if stakeholder upgrades priority.
- **RES-20** (Ray's episode-selection criterion) remains pending; new episodes proposed via PR against `history_zoom_events_registry.json`.
- **kaleido deprecation warnings** during perceptual-check PNG rendering — upstream upgrade is a separate track.

---
*Written: 2026-04-20 (Wave 9B memory catch-up)*

---

## 2026-04-24 — Wave 10J/10K Checkpoint

**Identity:** Viz Vera (viz-vera)
**Wave context:** 10J self-reflection + 10K retro-apply

### Contributions

1. **VIZ-HZE1 rule authored** — new pre-handoff gate in `docs/agent-sops/visualization-agent-sop.md`. Mandates `git ls-files` verification per required zoom slug before dispatch; structured skip protocol for data-coverage gaps (`_meta.json` with `"skip": true`). Fills the structural blind spot where SOP had no production enumeration gate.

2. **29 history_zoom charts generated** across 8 pairs (commit `20669d9`):
   - `dff_ted_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `hy_ig_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `indpro_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `indpro_xlp` — 3 charts (gfc, covid, taper — ukraine omitted: no SPY divergence)
   - `permit_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `sofr_ted_spy` — 3 charts (covid, taper, ukraine — gfc skip: SOFR data starts 2018)
   - `ted_spliced_spy` — 4 charts (gfc, covid, taper, ukraine)
   - `umcsent_xlv` — 3 charts (gfc, covid, taper)
   (31 `_meta.json` sidecars also generated)

3. **vix_vix3m_spy dot_com skip** (commit `2f15547`) — `history_zoom_dot_com_meta.json` structured skip entry; VIX3M data starts 2007, predates dot-com episode 1999-2002. Documented skip.

4. **META-CPD cross-reference** (commit `da8f534`) — added cross-reference to META-CPD in Viz Vera SOP deployment rules section.

5. **Experience entry promoted** to `~/.claude/agents/viz-vera/experience.md` — failure mode class: "SOP rule without production enumeration gate."

### Documented skips
| Pair | Episode | Reason |
|------|---------|--------|
| sofr_ted_spy | gfc | SOFR data starts 2018 (post-GFC) |
| vix_vix3m_spy | dot_com | VIX3M data starts 2007; episode 1999-2002 |

### Wave 10J Phase 5 Quincy verify result
60/60 PASS — wave APPROVED (all 10 pairs × 6 gates per pair).

### Outstanding item flagged
- **Perceptual PNGs (kaleido renders):** only `hy_ig_v2_spy` has them. 9 other pairs at WARN. Lead decision pending on whether to assign a wave target for backfill.

*Written: 2026-04-24 (Wave 10J/10K checkpoint)*

---

## 2026-04-22 — Wave 10F Cross-Review Dispatch

**Task:** Cross-review all team SOPs from viz perspective; deliver authoritative answers to the three open questions that triggered this wave (filename convention, sidecar naming, palette aliases).

**Deliverable:** `_pws/_team/cross-review-20260420-viz-vera.md` (240 lines, ~2650 words, 7 sections).

**Key recommendations:**
1. Bare-name filenames are canonical; migrate indpro_xlp + umcsent_xlv (20 renames) and delete HY-IG v2 prefixed duplicates (13 deletes). Add producer-side pre-commit enforcement.
2. `_meta.json` for charts, `_manifest.json` for datasets — distinct classes, stay distinct. Fix VIZ-IC1 §6 `_manifest.json` → `_meta.json` (drafting slip). Create `docs/schemas/chart_sidecar.schema.json`.
3. Add `aliases` block (`indicator`/`target`/`benchmark` → canonical keys) to `color_palette_registry.json`. Do not rewrite VIZ-IC1; the two-level semantic/visual split is the point.

**Additional findings flagged:** VIZ-IC1 ships as silent no-op today (schema gaps); `matplotlib_legacy` grandfather clause vs VIZ-V5 smoke rule contradiction; `chart_manifest.json` index documented but not on disk; indpro_xlp + umcsent_xlv have zero `_meta.json` sidecars.

**Top-5 priority fixes:** (P1) filename migration, (P2) palette aliases, (P3) VIZ-IC1 §6 fix + sidecar schema, (P4) `scripts/viz_ic1_check.py` reference impl, (P5) sidecar retro-apply for the two prefixed pairs.

**Evidence:** `wc -l _pws/_team/cross-review-20260420-viz-vera.md` → 240. META-AM updates: global experience.md appended (3 new patterns), memories.md appended (Wave 10F-CR incident), this file appended. Global `last_seen` updated to 2026-04-22T00:00:00Z.

**PROMOTED 2026-04-22T00:00:00Z** — experience.md: 65→79 lines (+3 patterns). memories.md: 51→70 lines (+1 incident block).

---

## 2026-04-22 — Wave 10F Filename Migration Session

**Identity:** Viz Vera (viz-vera)
**SOD performed:** Yes — read sod.md, team-standards.md §2.1/§3/§4, sop-changelog.md, experience.md, memories.md.

### Phase-by-phase counts

| Phase | Action | Count |
|-------|--------|-------|
| 1 | HY-IG v2 pair-prefixed duplicates deleted (git rm) | 5 |
| 2a | indpro_xlp charts renamed to bare-name (git mv) | 10 |
| 2b | umcsent_xlv charts renamed to bare-name (git mv) | 10 |
| 3 | _meta.json sidecars created | 32 |
| 3 | _meta.json sidecars pre-existing (skipped) | 10 |
| + | Consumer files updated (pages + config + smoke_loader) | 5 |
| 4 | Smoke tests: hy_ig_v2_spy passes | 15/0 |
| 4 | Smoke tests: indpro_xlp passes | 8/0 |
| 4 | Smoke tests: umcsent_xlv passes | 7/0 |

### Commit
- SHA: 3c6bb50
- 65 files changed, +516/-34
- Pushed to remote main

### Key finding
Consumer-side references (portal pages, pair config class attributes, smoke_loader registry) are not updated by `git mv`. All 5 consumer files required explicit sed updates to pass smoke tests. This is now documented in experience.md as a mandatory migration step.

### wc -l evidence (META-AM)
- experience.md: 79 → 93 lines
- memories.md: 70 → 103 lines

---

## Session: 2026-04-22 Wave 10G.4D — Fresh hy_ig_spy 22-Chart Suite

### Identity
Agent: Viz Vera | Pair: hy_ig_spy | Wave: 10G.4D

### Task
Produce Sample-parity 22-chart suite for fresh `hy_ig_spy` pair (bare pair_id, Wave 10G.4C Evan outputs at fb49123).

### Completed

| Step | Item | Count |
|------|------|-------|
| 1 | Chart generation script written | 1 script (~500 lines) |
| 2 | Charts produced | 23 (22 required + 1 bonus) |
| 3 | _meta.json sidecars | 23 |
| 4 | VIZ-V5 smoke: hy_ig_spy | 23/23 PASS |
| 5 | smoke_loader: hy_ig_v2_spy | 15/0 PASS |
| 5 | smoke_loader: indpro_xlp | 8/0 PASS |
| 5 | smoke_loader: umcsent_xlv | 7/0 PASS |
| 6 | Handoff vera_20260422.md | written |
| 7 | Commit + push | c525470 |

### Data Sources Used
- Master: `data/hy_ig_spy_daily_20000101_20260422.parquet` (6,863 × 50 cols)
- Signals: `results/hy_ig_spy/signals_20260422.parquet` (17 cols)
- Models: `core_models_20260422/`, `exploratory_20260422/`, `tournament_validation_20260422/`
- Events: `docs/event_timeline_hy_ig_spy_20260422.csv` (Ray)
- Winner: S6_hmm_stress / T4_hmm_0.5 / P2 / L0 → OOS Sharpe 1.41

### Key decisions
- `regime_quartile_returns` produced from `results/hy_ig_spy/regime_quartile_returns.csv` (separate from `quartile_returns` which adds vol overlay)
- `transfer_entropy` computed inline (no pre-built artifact) via rolling conditional correlation proxy
- `walk_forward` filtered rank==1 only to get winner series

### wc -l evidence
- memories.md: ~119 lines (before 94 → after ~119)

---

## 2026-06-11 — vix_vix3m_spy equity_curves.json (META-CMP T2 gap) — STOPPED, escalated to Lead

### Dispatch
Produce missing `output/charts/vix_vix3m_spy/plotly/equity_curves.json` consistent with sibling `drawdown.json`/`walk_forward.json`. Branch `fix260611_meta_cmp`.

### Provenance found
Siblings generated 2026-05-26 by `scripts/w0p5_generate_missing_strategy_artefacts.py` ("fix260526 W0.5 (Lead-as-Vera)" in `_meta.json`). That script reconstructs the winner strategy series from winner_summary + signals parquet and already computes `equity_curve`/`buy_and_hold_equity` columns — it simply has no equity-curves chart producer.

### Consistency check — exact reproduction, but the series is WRONG
- Re-ran `make_strategy_returns("vix_vix3m_spy")` from the W0.5 script: implied drawdown matches shipped `drawdown.json` traces **bit-for-bit (max abs diff = 0.0, both traces, 4,956 points)**.
- BUT the reconstructed series shows strategy full-sample equity $1 → $0.036 (−96.4%), min drawdown **−96.9%**, OOS MDD −83.2% — vs winner_summary OOS Sharpe 1.1295 / MDD −21.15% and the live page caption "strategy limits drawdown to -21.15%". SOP "Data Ingestion Validation #4" + mandatory Numerical Reconciliation gate → DO NOT PROCEED.

### Root cause (two producer bugs in `derive_position`, w0p5 script)
1. `parse_threshold_code("T2_rp75")` returns **None** — parser looks for substring "roll" but the code is "rp75" → falls back to IS-median threshold instead of rolling 75th percentile.
2. **Double direction inversion** — winner_summary's `threshold_rule: "lt"` was already direction-adjusted at Wave 10I.A backfill ("inferred from T2_rp75 + direction=countercyclical"), but `derive_position` applies the countercyclical flip AGAIN → long during panic, cash otherwise → −96%.

### Authoritative series recovered (validation, not shipped)
Daily positions rebuilt from `results/vix_vix3m_spy/winner_trade_log.csv` (459 rows, original pipeline) with convention "return accrues day after entry through exit", OOS from **2020-01-01**, reconcile to winner_summary within rounding: Sharpe 1.13 (rep. 1.1295), MDD −21.1% (rep. −21.15%), ann. return 15.5% (rep. 15.31%).
→ Side-finding: winner_summary `oos_period_start: "2015-01-01"` (Wave 10I.A backfill) is wrong; true OOS start = 2020-01-01 (matches Methodology page prose).

### Blast radius (all from same W0.5 reconstruction)
- `vix_vix3m_spy`: drawdown.json, walk_forward.json (user-visible wrong: drawdown chart shows −96.9% under caption claiming −21.15%), winner_trades_broker_style.csv, subperiod_sharpe.{csv,json}
- `indpro_spy`: same artifact set — reconstructed OOS Sharpe 0.25 vs reported 1.10
- `indpro_xlp`: same artifact set — reconstructed OOS Sharpe 0.14 / MDD −36.4% vs reported 1.11 / −13.5%

### Why STOPPED
Shipping equity_curves consistent with siblings = chart showing −96% under prose claiming +15.3%/yr (prose-vs-data, blocked by SOP reconciliation gate). Shipping the correct (trade-log) curve = contradicts sibling drawdown.json on the same Performance tab (blocked by dispatch brief). Only SOP-compliant action: STOP + escalate. Recommended fix: rebuild the strategy series in the producer from `winner_trade_log.csv` (or fix `derive_position` + OOS dates), regenerate all 4 artifacts × 3 pairs, THEN add the equity_curves producer (trivial once series is right).

### Evidence
`temp/260611_vix_equity_consistency/` — check_consistency.py, diagnose.py, tradelog_check.py, xlp_check.py (temp/, gitignored; outputs reproduced in this note).

### Config check (dispatch item 5)
Confirmed: `app/pair_configs/vix_vix3m_spy_config.py` declares no `EQUITY_CHART_NAME`; `page_templates.py:1306` getattr default resolves to "equity_curves" — no config change needed once the file exists. Stale comment at config lines 476-478 ("No equity_curves / drawdown / walk_forward charts on disk") is outdated (Ray/Ace-owned; flagged, not edited).

---

## 2026-06-11 (part 2) — ECON-SR1 chart regeneration ×3 pairs + vix equity_curves (T2 gap closed)

### Dispatch
Lead, post-STOP disposition. Consume Evan's reconciled canonical series (`results/{pair}/strategy_returns_20260611.csv`, commit 108b091) and regenerate the defective strategy-performance charts for vix_vix3m_spy / indpro_spy / indpro_xlp.

### Shipped
New producer `scripts/generate_strategy_perf_charts.py` (ECON-SR1 consumer; never re-derives positions — META-NMF). Per pair: `equity_curves.json`, `drawdown.json`, `walk_forward.json`, `subperiod_sharpe.json` + `_meta.json` sidecars (palette_id okabe_ito_2026, disposition consumed, per-chart reconciliation block, Rule-A5 caption) + perceptual PNGs. 12 charts total. Rule A4 regression notes ×3 at `results/{pair}/regression_note_20260611.md`.

### Gates (all PASS)
- ECON-SR1 reconciliation (blocking, in-producer): 9/9 metrics PASS (Sharpe/MDD/annret ×3 pairs); vix 1.1295/−0.2115/0.1548 vs reported 1.1295/−0.2115/0.1531.
- Per-chart: drawdown min == oos_max_drawdown ×3 EXACT; equity implied DD == oos_max_drawdown ×3 EXACT.
- VIZ-IC1 in-producer (palette/legend/unit/title) 12/12; VIZ-NBER1 shapes present on all 9 calendar-time charts (subperiod categorical = exempt).
- T2 lint_chart_completeness: 98 refs / 0 failures (vix now PASS — placeholder gone).
- smoke_loader --all: 8/8 pairs, 0 failures. Loader harness via charts.py::_load_plotly_json: 12/12 Figures with traces.
- Perceptual (VIZ-CV1): PNGs eyeballed — caught and fixed a real defect: paired "$" in Plotly titles triggers MathJax ("$1 into $2.43" rendered as garbled math). Rule of thumb recorded: max ONE literal $ per Plotly/Streamlit text element.

### Provenance verdicts (dispatch item 2)
- indpro_spy equity_curves: PREDATES W0.5 (original tournament-era chart) but winner trace did NOT reconcile — endpoint 1.519 vs canonical 1.711 (11.2% off), implied Sharpe 0.90 vs reported 1.1036. B&H trace was exact. REGENERATED.
- indpro_xlp equity_curves: PREDATES W0.5 (2026-04-22) but winner trace 13.6% off endpoint (2.187 vs 2.531), implied Sharpe 0.97 vs 1.1147. REGENERATED.
- Content change: old equity charts showed top-3 strategies; new show winner vs B&H (canonical artifact covers winner only; template caption already promises "tournament winner compared to buy-and-hold"). Documented in regression notes, flagged to Lead. If top-3 view wanted back, Evan must first produce reconciled series for combos #2/#3.

### Other
- indpro_xlp legacy winner_summary lacks *_display_name → added humanised code-label fallback in producer + assert against raw-token leakage (VIZ-NS1).
- subperiod charts built from Evan's round-2 CSVs (landed 03efc78 mid-dispatch).
- Ray's parallel b99b432 prose fixes reviewed — complementary, no chart conflicts.

---

## 2026-06-12 — busloans_spy full standard chart set (Pair #19, Mode 1, stage 3a)

### Dispatch
Lead: full standard set + ECON-H4 table (14 rows) for busloans_spy on `fix260612_busloans_spy`. Binding framing: lagging/reverse-only Granger; tournament fragility disclosed.

### Delivered (commit 949a113, pushed)
- New producer `scripts/generate_charts_busloans_spy.py` — 18 charts (incl. 4 history zooms + 2 CP2 chart_skip sidecars). In-process gates: VIZ-IC1 (+VIZ-TX1 one-$ lint), VIZ-NBER1, VIZ-DP1, perceptual PNG per chart.
- SR1 charts (equity_curves/drawdown/walk_forward) via `generate_strategy_perf_charts.py` — reconcile-or-die PASS ×3; script extended with `--no-subperiod` + `_LOCAL_INDICATOR_LABELS` VIZ-NS1 fallback (busloans_spy → "C&I Loans").
- chart_type_registry → v1.1.0 (`tournament_distribution` entry, VIZ-V8 compliance) + sop-changelog.
- VIZ-CV1 21/21 PASS; VIZ-HZE1 PASS (4/4 slugs); lint_chart_completeness SKIP for busloans_spy (no pair_config yet — expected), smoke_loader 0 pages (expected).
- Handoff: `results/_cross_agent/handoff_lead_busloans_spy_20260612_vera.md`.

### Perceptual-eyeball catches (the step keeps paying)
1. Legend↔title collision on granger_f_by_lag + tournament_scatter (horizontal top legend vs long subtitle) → legends moved below plot.
2. CI-band traces without `mode="lines"` render stray default-palette markers at band vertices (local_projections, quantile_coef) — invisible to the color lint because marker.color is None (Plotly default). Added to lint awareness.
3. VIZ-QR1 helper emits no `layout.title` (only subplot titles) → fails VIZ-CV1 title check; caller must add the main title.

### Open / for others
- Ace: display_names.py needs busloans_spy entries (proposed in handoff §5); config chart names listed there (quantile_coef, granger_f_by_lag, ccf_prewhitened, walk_forward).
- Lead: episode slug vocabulary split (dot_com/rates_2022 vs dotcom/inflation_2022) — echoed Ray's A2A flag.
