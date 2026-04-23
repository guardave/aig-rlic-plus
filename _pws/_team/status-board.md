# Team Status Board

## 2026-04-23 — Dev Ace (Wave 10I.A Part 1 — 4 legacy-pair migrations COMPLETE)

**Status:** 4 of 5 non-Sample legacy pair surfaces migrated to APP-PT1 thin-wrapper pattern. TED composite explode is separate Ace-B dispatch.

**Shipped:**
- 4 new pair configs: `indpro_spy_config.py`, `permit_spy_config.py`, `vix_vix3m_spy_config.py`, `umcsent_xlv_config.py` (1,334 lines, 190 TODO-Ray narrative stubs).
- 16 legacy pages rewritten as 18-line thin wrappers (3,622 → 288 lines; -3,334 page-file lines).
- Handoff doc: `results/_cross_agent/handoff_ace_wave10i_partA_20260423.md`.

**Smoke evidence (all PASS):**
- indpro_spy: passes=4, failures=0
- permit_spy: passes=3, failures=0
- vix_vix3m_spy: passes=3, failures=0
- umcsent_xlv: passes=6, failures=0

**Ready for Ray:** Narrative content port — 190 stubs with explicit source-line hints. Greppable via `grep "TODO Ray (Wave 10I.A)" app/pair_configs/*_config.py`.

**Discovery observations Lead may want to triage:**
- Chart filename drift on 3 pairs (pair-id-prefixed on disk, not canonical bare-name) — future Vera rename wave could canonicalise.
- permit_spy and vix_vix3m_spy lack equity_curves / drawdown / walk_forward chart files — pre-existing data gap, Evan/Vera backlog candidate.

**LEAD-DL1 self-check:** Ace wrote zero narrative prose. All prose fields are TODO-Ray stubs. Structural content (chart names, tables, references) is the Ace ownership.

---

## 2026-04-23 — Dev Ace (Wave 10I discovery — legacy-page migration scope)

**Status:** Discovery report shipped per Lead dispatch. No implementation (per LEAD-DL1 handoff contract).

**Top-line numbers:**
- 19 files / 5,829 lines to migrate (15 hand-written + 1 hybrid + 4 TED composite = 5 pair surfaces + Sample).
- 8 pair configs to create (7 non-Sample + 1 Sample reference).
- **0 template extensions needed.** `page_templates.py` already supports every Sample-exclusive component.
- Ballpark: **14 agent-waves total** (8 Ace, 3 Ray, 1 Evan, 0 Dana, 2 Quincy). ~500K–700K tokens.

**Phasing recommendation:** Two waves. 10I.A = non-Sample (5 surfaces in parallel lanes, umcsent is the long pole). 10I.B = Sample (reference-defining port, regression parity vs. sample-v1.0 gate).

**Gate for Lead:** TED composite decision (explode to 3 × 4 pages or preserve composite with tab-safe template mode) is a prerequisite before Wave 10I.A scoping finalises. Recommendation: explode — keeps 1-pair-per-card-per-4-pages invariant and needs zero template changes.

**Report:** `results/_cross_agent/ace_discovery_legacy_migration_20260423.md`

**APP-PR1 audit:** zero bare-relative `results/` reads in any `app/pages/` file. Migration removes all 16 non-canonical `os.path.join(dirname, "..", ...)` idioms by deletion.

---

## 2026-04-23 — Lead Lesandro (Wave 10H.1 CLOSED ✅ — EOD)

**Status:** Wave 10H.1 complete. Git tag `wave-10h1-complete` pinned at Quincy's final verify `aca5602`. Closure commit `08546f3` (relnotes + sop-changelog).

**Shipped end-to-end:** VIZ-O1 chart disposition + VIZ-E1 exploration zone (Vera); APP-PT2 Methodology Exploratory Insights (Ace); Pattern 22 verify fix + canonical `scripts/cloud_verify.py` (Quincy); LEAD-DL1 Lead delegation discipline + File Ownership Map (Lead); `.claude/settings.json` permission-syntax fix (Lead).

**LEAD-DL1 self-audit clean:** 6 Lead commits across Wave 10H/10H.1 touched only category-1/6 paths (`docs/`, `.claude/settings.json`). Zero drift after initial revert.

**Meta-event of the wave:** user caught Lead drifting into agent work, asked for durable discipline mechanism. LEAD-DL1 SOP + auto-memory + wave-closure self-audit is the result. Framework validated through the rest of the wave — 5 clean agent dispatches, no further drift.

**Backlog opened for Wave 10H.2/10I hygiene:** BL-VIZ-O1-LEGACY, BL-VIZ-SIDECAR-HELPER, BL-APP-PR1, BL-APP-PT1-LEGACY. All bundleable.

**Team insights — 2026-04-23:**
- Pattern 22 (CSS class names not in `inner_text`) formally codified; future cloud verify scripts must use DOM-tree queries.
- Playwright `page.frames` iteration races Streamlit frame registration → use `wait_for_selector('iframe[title=...]').content_frame()`.
- `.claude/settings.json` double-slash = absolute, single-slash = project-relative (Claude Code docs).
- Centralised template only protects pages that actually use it — 5 Methodology pages still hand-written. Agent briefs for any future Methodology-rule addition must list bypass pages requiring defensive direct calls until migration.

---

## 2026-04-23T00:16Z — QA Quincy (Wave 10H.1 FINAL re-verify — 17/17 PASS ✅)

**Status:** **Wave 10H.1 QA COMPLETE.** Cloud verify on HEAD `387062f` returned 17 PASS / 0 FAIL / 17 TOTAL.

- Bug 1 (landing raw-col leak) — FIXED: `leak=False`, `humanize_column_tokens()` live.
- Bug 2 (APP-PT2 absent on Sample Methodology) — FIXED: `section=True`, eli5=3/3; DOM grew 14,138→17,356 chars on `hy_ig_v2_spy_methodology`.
- Streamlit Cloud auto-redeploy confirmed working (~75s window post-commit, no manual reboot required).
- Artifacts: `temp/20260423T001633Z_cloud_verify/`, handoff `results/_cross_agent/handoff_quincy_wave10h1_20260422.md` final section appended.

No residual FAILs, no deferred QA items from this wave.

## 2026-04-23 — Dev Ace (Wave 10H.1 follow-up — both FAILs fixed)

**Status:** Both cloud-verify FAILs fixed. Awaiting Quincy re-verify.

- **Bug 1 landing raw-col leak — FIXED.** Root cause: `key_finding` string in `interpretation_metadata.json` carries raw `spy_fwd_*d` tokens; `app/app.py` rendered verbatim. Added `humanize_column_tokens()` + canonical `_FWD_RETURN_LABELS` map in `pair_registry.py` (APP-RL1 SSoT), wrapped the display site. 7 pairs covered, no other pair's cards regressed.
- **Bug 2 APP-PT2 silent no-op — FIXED.** Root cause ≠ Quincy's hypothesis: helper was already using `_REPO_ROOT` correctly. Real cause: `app/pages/9_hy_ig_v2_spy_methodology.py` is hand-written legacy and bypasses `render_methodology_page`, where `_render_exploratory_insights` was wired in Wave 10H.1. Added direct call before References section. Also tightened observability (APP-SEV1 L2): JSON parse failure now surfaces `st.warning` instead of silent return.
- **CWD-independence regression test:** `temp/260423_ace_wave10h1_followup/cwd_independence_test.py` simulates `os.chdir('/tmp')` before importing — 12 streamlit calls emitted, heading present, info banner present. PASS.
- **Smoke:** `hy_ig_v2_spy` 15/0, `hy_ig_spy` 6/0.
- **Proposed rule for Lead:** **APP-PR1 Path Resolution Discipline** — mandate `_REPO_ROOT` anchors in `app/components/**` + `app/pages/**`; require surfaced warnings on unreadable files of shipped pairs. 5 other hand-written methodology pages currently bypass the template (no visible bug today but pre-positioned to silently drop future `exploratory_charts` adoption).
- Handoff follow-up appended to `results/_cross_agent/handoff_ace_wave10h1_20260422.md`.

---

## 2026-04-23 — QA Quincy (Wave 10H.1 Re-verify, post-2nd-reboot)

**Status:** Re-verify complete. **15 PASS / 2 FAIL / 17** — identical to attempt 3; user's 2nd Streamlit Cloud reboot with cache-clear did not change the outcome.

- **FAIL `landing`**: raw-column leak (`spy_fwd_21d`, `spy_fwd_63d`) unchanged. Display-standard bug, owner Ace.
- **FAIL `hy_ig_v2_spy_methodology`**: APP-PT2 Exploratory Insights section still absent (section=False, eli5=0/3). **Cache-clear reboot rules out deploy-lag** → confirmed code defect in `_render_exploratory_insights`, owner Ace.
- **Verdict:** (c) Both FAILs need Ace dispatch in Wave 10H.2 / 10I. My verify script is sound; findings are genuine cloud-side code defects.
- Evidence: `temp/20260423T000315Z_cloud_verify/`. Handoff `Re-verify` section appended to `results/_cross_agent/handoff_quincy_wave10h1_20260422.md`.

---

## 2026-04-22 — QA Quincy (Wave 10H.1)

**Status:** Completed with blocker. Cloud verify BLOCKED on Streamlit app hibernation (Pattern 19/20) — needs user reboot.

- **Deliverable A:** `scripts/cloud_verify.py` canonical + Pattern 22 fix + APP-PT2 Sample Methodology check + backward-compat regression gate.
- **Deliverable B:** 17/17 FAIL (no_iframe) × 2 runs. Probe confirms hibernating body stub. Did not retry in tight loop.
- **VIZ-O1:** 65/65 focus-pair sidecars PASS. 35 missing on 6 legacy pairs (Vera pre-flagged). Proposed BL-VIZ-O1-LEGACY for Wave 10H.2/10I.
- **GATE-28 / APP-PT2 render:** BLOCKED until reboot. Regression gate structurally safe (only hy_ig_v2_spy has `exploratory_charts` key).
- **QA-CL2 T3:** N/A per new P2 continuous-rebalancing exception.
- **Handoff:** `results/_cross_agent/handoff_quincy_wave10h1_20260422.md`.

---

## 2026-04-22 — Viz Vera (Wave 10H.1)

**Status:** Completed.

**Accomplished:**
- `scripts/backfill_chart_dispositions.py` (new) — idempotent. First run: 62 consumed + 3 suggested on 65 existing sidecars. Rerun: 65 unchanged.
- `results/hy_ig_v2_spy/analyst_suggestions.json` — added top-level `exploratory_charts` key (3 entries with ELI5 captions + Vera rationales). Evan's `suggestions` array untouched (LEAD-DL1 split honoured).
- Generator scripts updated to emit `"disposition": "consumed"` on future runs: `generate_charts_hy_ig_spy.py`, `retro_fix_hy_ig_v2_vera_20260411.py`, `generate_charts.py`.
- Handoff: `results/_cross_agent/handoff_vera_wave10h1_20260422.md`.

**Follow-up flagged:** 4 other per-pair generators have no sidecar-writer function to patch — refactor candidate for a shared `_chart_sidecar.py` helper.

**Next:** Ace's APP-PT2 renderer lands in parallel; Quincy verifies Exploratory Insights section on cloud.

---

## 2026-04-22 — Lead Lesandro (Wave 10F closure)

**Status:** Completed (pending final cloud verify by Quincy, in flight)

**Accomplished:**
- **Standardization infrastructure shipped:** project-local `/sod` (`.claude/commands/sod.md`), PreToolUse SOD hook + PostToolUse EOD hook both in repo (`scripts/hooks/`), `docs/team-standards.md` as cross-agent SSoT, `docs/sop-changelog.md` with SOD read protocol, dispatch template extended with mandatory `## SOD Block`.
- **Cross-review executed** — 6 agents in parallel (Opus min): findings docs at `_pws/_team/cross-review-20260420-*.md`. Identified 6 conflicts, 5 redundancies, 12 silent-weakening observations, 3 Vera open questions — all resolved.
- **Team-standards ratified:** §2.1 bare-name chart filenames; §3 two-name sidecar split (`_meta.json` chart / `_manifest.json` dataset); §4 palette v1.1.0 with `benchmark_trace` key + semantic aliases.
- **New rules:** META-RYW (read your own work), META-NMF (no manual fix), VIZ-IC1 (intra-chart consistency), RES-NR1 (narrative instrument accuracy), GATE-NR/QA-CL5 (DOM instrument check), APP-PT1 supplement (Ray authors narrative).
- **Migrations executed (3 pairs):** 5 HY-IG v2 prefixed duplicates deleted, 22 prefixed files renamed to bare-name, 32 `_meta.json` sidecars added, loader pair-prefix fallback removed (VIZ-NM1 closure after 13-day violation).
- **Permission fix:** `.claude/settings.json` allow-list extended — unblocked 5 of 6 cross-reviewers who hit sandbox denials. Memory promotion sweep completed for all 5.
- **Self-contradictions fixed:** VIZ-IC1 §4 + §6, research SOP L672 + L1000.
- 8 commits: 90cadd4 → f1d78bb → 85ee737 → daea311 → beb84a5 → 3c6bb50 → 27fb01f → cc99fc4.

**Discoveries & Insights:**
- **Rule adoption without a code-deletion gate leaves dead violators alive.** VIZ-NM1 ratified 2026-04-09; loader fallback persisted 13 days. Every new SOP rule needs a follow-up grep/AST audit confirming the prior code path is deleted.
- **Permission allow-lists must enumerate every tool.** `Write(...)` alone is insufficient — Edit and Bash append are separate checks. Five of six cross-reviewers hit denials despite `Write(...)` being allowed.
- **Cross-review surfaces silent-weakening invisible in single-wave work.** Quincy's audit found 12 SW observations across META-XVC, GATE-30, META-NMF, QA-CL3.
- **Project-local command override beats global-skill extension** for per-project conventions. Splitting SOD between global skill and team-coordination.md would have recreated the "missed read" pattern we were trying to solve.
- **Two-name sidecar pattern is a feature, not a bug.** The apparent conflict was a single-line drafting slip.

**Blockers:** Cloud verify in flight (Quincy dispatch `a55c9dc3`).

**Next Steps:**
- **Wave 10G candidate:** HY-IG v2 migration to APP-PT1 templates (item 8 from earlier plan; risky, separate wave).
- **Backlog:** DATA-D12 linter, DATA-D13 manifest bootstrap, META-XVC diff tool, 3 unreferenced HY-IG v2 charts audit.

---

## Team Insights — 2026-04-22

**QA Quincy — Wave 10F Cloud Closure Verify**

- **HY-IG v2 + UMCSENT: APPROVED.** All 8 pages structurally clean — zero errors, breadcrumb nav OK, evidence structure OK, signal universe OK, charts loading correctly (5–8 per page on story/evidence/strategy).
- **INDPRO XLP: BLOCKED (story + evidence).** Both pages render "chart pending" with pair-prefix fallback paths (`indpro_xlp_hero.json`, `indpro_xlp_correlations.json`). Root cause: Cloud app appears to be resolving HERO_CHART_NAME to the pre-`3c6bb50` value ("indpro_xlp_hero") despite the config file setting HERO_CHART_NAME="hero" at HEAD. Possible causes: (a) Streamlit partial-redeploy state mixing bfb1b70-era config with renamed chart files; (b) STORY_CONFIG import failure causing `getattr` to fall back to the `f"{pair_id}_hero"` default. INDPRO strategy page PASSES (5 charts), indicating the pair's bare-name setup for strategy charts is working; the issue is specific to story/evidence config resolution.
- **Methodology pages (all 3): PASS-with-note.** No charts by design — Signal Universe, FAQ text, and tables only. Chart-render criterion (≥1 per page) does not apply to methodology pages. Criterion gap logged: future QA specs should scope chart-render probe to story/evidence/strategy only.
- **GATE-NR: PASS** on all 6 story + evidence pages. Three PASS-with-note comparative references (S&P 500 on indpro_xlp_story, DIA + SPY on umcsent_xlv_story) — all legitimately contrastive. First occurrence of DIA in umcsent_xlv narrative; advisory to Ray to standardize benchmark to SPY.
- **New process pattern (Pattern 17 candidate):** Chart-render criteria must be scoped to page types that actually render charts. Blanket "≥1 chart per page" specifications will false-FAIL methodology pages on every cloud run.
- **QA report:** `results/qa_verification_wave10f_20260422.md`

---

## Wave 10G.4F — QA Quincy (2026-04-22)

**Status:** Completed — APPROVE for cloud verify

**Accomplished:**
- Full pre-cloud QA sweep on new `hy_ig_spy` pair (Waves 10G.4A-4E deliverables).
- **9 checks executed: 8 PASS, 1 PASS-with-note, 0 FAIL.**
- GATE-27: smoke_loader 6/6 + schema_consumers 5/5; all 4 regression pairs clean.
- GATE-29: signals_20260422.parquet committed; clean-checkout smoke passes; all 6 §5.2 deploy-required artifacts present.
- Schema validation: all 4 JSON instances conform to registered schemas.
- APP-DIR1: 3-way direction consensus (Evan + Dana + Ray all = `countercyclical`).
- APP-PT1: 0 `st.*` calls in all 4 page files.
- GATE-NR: zero non-target tickers; "bonds" language is historical narrative, not bond exposure.
- Feature parity: 14/14 features verified via config + template inspection.
- Stakeholder-spirit: numeric claims consistent (Sharpe 1.41, return 11.7%, MDD -8.5%); B&H alpha win correctly framed as risk-adjusted (Sharpe), not absolute return.

**One note (non-blocking):** QA-CL2 turnover-trade-count triangulation is not applicable to signal-strength (P2 continuous proportional sizing) strategies. annual_turnover (3.84x portfolio/year) and oos_n_trades (387 daily rebalances) are incommensurate metrics. SOP should note this class exception.

**QA report:** `results/hy_ig_spy/qa_verification_10g_20260422.md`

**Next action for Lead:** Reboot Streamlit → navigate to pair 15 (hy_ig_spy) → Phase 5 cloud DOM verify.

---

## 2026-04-20 — Lead Lesandro

**Status:** Completed (Checkpoint — awaiting cloud reboot for Wave 10D)

**Accomplished:**
- **Two new pairs delivered end-to-end** (Wave 9/10):
  - `umcsent_xlv`: Michigan Consumer Sentiment × XLV — OOS Sharpe 1.02, Sortino 2.01, 81 OOS months
  - `indpro_xlp`: Industrial Production × XLP — OOS Sharpe 1.11, Sortino 2.07, 84 OOS months
  - Each: 7-stage pipeline script, 10 Plotly charts, 4 portal pages, full sidecar set
- **QA GATE-31 PASS** on both pairs: smoke_loader 0 failures, schema_consumers 5/5 pass
- **Enforcement infrastructure shipped** (3-layer META-AM system):
  - L1: Mandatory dispatch template with AGENT_ID + 4-step EOD block
  - L2: PostToolUse hook (`check-agent-eod.sh`) audits experience.md/memories.md mtime
  - L3: QA-CL3 (agent memory discipline) activated in qa-agent-sop.md
- **QA-CL4 (cloud verify)** added as named checklist item with GATE-27/28/29 protocol
- **smoke_loader hardening**: dynamic page prefix (`*_{pair_id}_*.py`) + per-pair EVIDENCE_DYNAMIC_CHARTS dict
- **settings.json cleanup**: 36→19 entries, double-slash typo fixed, FRED MCP allow-listed
- **Commit d4df8b9** pushed — 98 files, 14,330 insertions

**Discoveries & Insights:**
- **Schema lag is the dominant failure mode at scale.** As pair count grows, pipeline agents generate sidecars from pre-schema templates. Winner_summary, signal_scope, analyst_suggestions all required structural updates. Pattern 10 (Quincy classification): schema compliance checks must be part of the standard QA gate.
- **Re-dispatch after context loss is lossy.** L2 hook fires after the agent window closes; by then context is gone. L1 (dispatch template) is the only mechanism that acts while context is live — make it mandatory and auditable.
- **EVIDENCE_DYNAMIC_CHARTS must be per-pair.** The original global list applied HY-IG v2 chart names to all pairs, causing 8 false-positive failures per new pair.
- **Commit before cloud verify, not after.** GATE-28/29 require the cloud app to have the new pages. Correct order: commit → push → reboot → verify.

**Blockers:** Waiting for user to reboot cloud Streamlit app (Wave 10D GATE-28/29 pending)

**Next Steps:**
- Wave 10D: GATE-28 (headless browser, zero "chart pending" on 8 new pages) + GATE-29 (smoke_loader clean-checkout)
- Agent global profile writes (econ-evan, qa-quincy experience.md / memories.md) — permission fix in settings.json, needs verification

---

## Team Insights — 2026-04-20

- **[Ace]** Template discipline: new pair pages built from scratch instead of derived from `9_hy_ig_v2_spy_story.py` silently drop mandatory components (breadcrumb, `render_method_block` evidence structure) — always derive from the reference template, not from scratch.

---

## 2026-04-11 — Lead Lesandro

**Status:** Completed (EOD)

**Accomplished:**
- Part D: 8-element Evidence template, classification metadata schema, landing page filters + chips + badges (+650 lines across SOPs + metadata + app)
- Part E: SOP hardening from stakeholder bug review — 9 stakeholder rules + 15 self-review rules (5 agents in parallel) + 10 cross-review contract fixes (+513 lines across 6 SOPs)
- Retroactive HY-IG v2 application: CCF + Transfer Entropy + Quartile Returns added, hero chart unit bug fixed (data was 100x too small), canonical heatmap, 8-tab Evidence, broker-style trade log with column legend and COVID 2020 concrete example
- Trade log UX fix: 3-layer (schema/rendering/explanation) with new Econometrics C4, AppDev §3.8 #5, Research "How to Read" rules
- 8 commits pushed; tag `sop-hardening-partE`; backup zip created (199 MB)

**Discoveries & Insights:**
- **Meta-rule: "Silent changes are unacceptable."** Every stakeholder-visible bug (axis inversion, unit mismatch, dropped methods, heatmap signals) was an agent making a deliberate decision without documentation. Fix at source via regression_note.md.
- **A2 Unit Discipline caught a 100× bug on first production use.** Hero chart had data in percent under a "bps" axis label — Vera's pre-save audit found it.
- **Phase 1 self-review > Phase 2 cross-review** for ROI. Agents self-flag "gaps belonging to others" during self-review; straight to consolidation saves 5 dispatches.
- **Cross-agent boundary contracts are the #1 source of bugs.** Chart filenames, caption ownership, trade log schema — every bug was at a handoff point where neither agent's SOP committed to an explicit contract.
- **Streamlit Cloud can serve stale cached modules** even after push. Fix: trivial docstring change forces a clean redeploy.

**Blockers:** None

**Next Steps:**
- Cross-pair rollout of trade log UX fix to 5 other pairs (reusable script ready)
- Pair #4: US10Y-US3M → SPY (first pair on fully hardened SOPs)
- Glossary architecture migration (docs/portal_glossary.json as source of truth)

---

## 2026-04-10 — Lead Lesandro

**Status:** Completed

**Accomplished:**
- SOP Hardening Part C: Full 5-agent pipeline re-run of HY-IG v2 (Sharpe 1.27)
- Fixed 2 Cloud deployment bugs (page_link fallback, chart filename mismatch)
- Comparative analysis: v2 vs sample pages → identified 5 audience-friendliness gaps
- Added 7 SOP rules across Research + AppDev SOPs (writing voice, rendering patterns)
- Re-ran Ray + Ace with new SOPs → pages now have inline definitions, translation bridges, rule-first layout
- 5 commits pushed, all verified with headless browser

**Discoveries & Insights:**
- Lead role = coordinate + decide. Don't do agent-level implementation work.
- Chart naming needs convention: agents use different prefixes. Fixed in loader, needs SOP rule.
- Streamlit Cloud page_link resolution differs from local — always verify on Cloud.
- Translation bridges ("What this means:") are highest-ROI readability improvement.
- Audience-friendliness is a process/SOP gap, not a content gap — rules fix it systematically.

**Blockers:** None

**Next Steps:**
- Pair #4: US10Y-US3M → SPY (yield curve slope)
- Continue systematic pair execution with updated SOPs
- Consider chart naming convention SOP addition

---

## 2026-04-09 — Lead Lesandro

**Status:** SOD Checkpoint

**Accomplished:**
- Pulled 5 new commits from remote (HY-IG execution panel + bug fixes from another session)
- Local now at `aab9fd0`, synced with origin, clean tree
- Reviewed PWS, memories, and outstanding work — all current

**Discoveries & Insights:**
- VIX/VIX3M pair (#11) was completed in prior session (Sharpe 1.13, strongest regime discriminator)
- HY-IG execution panel added externally with trade log CSV download feature

**Blockers:** None

**Next Steps:**
- Pair #4: US10Y-US3M → SPY (yield curve slope)
- Continue systematic pair execution with MRA
- FOMC SEP: Era A PDF extraction when time permits

---

## 2026-03-14 — Lead Lesandro

**Status:** Completed / Checkpoint

**Accomplished:**
- Executed priority pairs #1 (INDPRO), #2 (SOFR/TED, 3 variants), #3 (Building Permits), with #20 (HY-IG) pre-existing
- 4 of 73 priority pairs now completed
- Full pipeline per pair: data → models → tournament → charts → portal → browser verify → completeness gate → MRA
- Landing page: filterable card grid with hover hints, dropdown sidebar, equal-height cards
- SOPs updated: MRA protocol (Step 9), Deliverables Completeness Gate (Step 8), Browser Verification (Step 7), Viz Preferences, persona rename (Alex → Lesandro)

**Discoveries & Insights:**
- RoC/momentum signals beat level signals (confirmed 3/3 pairs)
- 6-month lead is default for monthly indicators (confirmed 3/3 pairs)
- SOFR ≠ LIBOR (r=-0.04); DFF-DTB3 is the canonical TED proxy (r=+0.63)
- Streamlit `unsafe_allow_html` silently fails on nested HTML — use native components
- Browser verification catches rendering bugs; completeness gate catches missing pages
- ~150K tokens per recurring pair; pipeline 7-14s wall-clock

**Blockers:** None

**Next Steps:**
- Pair #4: US10Y-US3M → SPY (yield curve slope)
- Continue systematic pair execution with MRA
- Consider template-based portal pages at 10+ pairs

---

## Team Insights — 2026-04-22 (Wave 10F Re-verify)

**QA Quincy re-verify (post `a74364f`):** BLOCK persisting — `indpro_xlp` story/evidence still serving pair-prefix chart paths (`indpro_xlp_hero.json`, `indpro_xlp_correlations.json`) on Cloud after 2×60s retry; fix is on GitHub (`origin/main` = `a74364f`) but Streamlit Cloud has NOT redeployed `indpro_xlp_config.py` — manual Cloud reboot required before Wave 10F can close as COMPLETE. HY-IG v2 story sanity regression: PASS (5 charts, clean).

**QA Quincy re-verify AFTER cloud reboot (09:31 UTC):** ALL 3 PAGES PASS — `indpro_xlp_story` (7,777 chars, 2 charts), `indpro_xlp_evidence` (4,695 chars, 3 charts), `hy_ig_v2_spy_story` (17,059 chars, 5 charts). Zero chart-pending, zero errors, zero pair-prefix matches. Wave 10F COMPLETE.

---

## 2026-04-22 — Wave 10H.1 [Ace] APP-PT2 landed

**Status:** READY FOR CLOUD VERIFY.

- `app/components/page_templates.py`: added `_render_exploratory_insights(pair_id)` helper + wired into `render_methodology_page` as section 13b.
- Backward-compatible: legacy pairs (no `exploratory_charts` key) render identically — verified via smoke_loader (hy_ig_v2_spy 15/0, hy_ig_spy 6/0) and via 4-scenario dry-run harness under `temp/260422_app_pt2/`.
- Awaiting Vera (`exploratory_charts` authoring in `analyst_suggestions.json` + sidecar backfill per VIZ-O1/VIZ-E1) and Quincy (cloud DOM verify per handoff notes).
- Handoff: `results/_cross_agent/handoff_ace_wave10h1_20260422.md`.

## 2026-04-22T23:50Z — Quincy (Wave 10H.1 attempt 3)

- scripts/cloud_verify.py patched — selector-based iframe discovery (replaces page.frames race).
- Full verify: **15/17 PASS**. Real FAILs on landing (raw-col leak, Ace) and hy_ig_v2_spy_methodology (APP-PT2 section absent — suspect cloud deployment lag).
- META-AM: b3facc8 slash fix validated. BL-PERM-SUBAGENT → RESOLVED.
- Handoff appended: results/_cross_agent/handoff_quincy_wave10h1_20260422.md §"Post-reboot verify (attempt 3)".

## 2026-04-23 — Wave 10H.2 [Evan] APP-TL1 data backfill COMPLETE

- New shared helper: `scripts/_trade_log_broker.py` (monthly-pair broker CSV synthesis from position log).
- `results/indpro_xlp/winner_trades_broker_style.csv` — 43 rows.
- `results/umcsent_xlv/winner_trades_broker_style.csv` — 15 rows.
- Schema APP-TL1 compliant; `comment="#"` header row as reference.
- Two items flagged to Dana: per-pair data dictionaries missing; `commission_bps` absent from `winner_summary.json` (defaulted 5 bps).
- Handoff: `results/_cross_agent/handoff_evan_wave10h2_20260423.md`.
- Ace unblocked on template-side APP-TL1 rollout for these two pairs.

## 2026-04-23 — Wave 10H.2 [Ace] APP-TL1 structural skeleton LANDED

**Status:** READY FOR RAY (narrative fill).

- `app/components/page_templates.py`:
  - 4 narrative constants (stubs with `# TODO Ray`) at lines 114, 120, 127, 139.
  - New helper `_render_trade_log_block(pair_id, config)` at line 1311 — 9-step APP-TL1 render order, APP-SEV1 L1/L2/L3 branching, unique widget keys, `_REPO_ROOT` path resolution, dual-CSV loading with `comment="#"` on broker-style.
  - Wired into `render_strategy_page` at line 1149 (replaces prior inline block).
- Config anchors read via `getattr` defaults — **no pair_config edits made** (Ray's territory).
- Smoke: hy_ig_v2_spy 15/0 PASS, hy_ig_spy 6/0 PASS. Strategy page will show visible `TODO Ray` placeholders until Ray's pass — expected.
- Handoff: `results/_cross_agent/handoff_ace_wave10h2_20260423.md` (includes exact line numbers + per-constant Ray assignments).
- Awaiting: Ray narrative fill (4 constants + 3 pair_config `TRADE_LOG_EXAMPLE_MD` fields); Quincy cloud verify last.

## 2026-04-23 — Wave 10H.2 [Ray] APP-TL1 narrative fill COMPLETE

**Status:** READY FOR QUINCY (cloud verify).

- `app/components/page_templates.py`: all 4 Ray-owned narrative constants filled.
  - `_TRADE_LOG_DISCLOSURE_MD` (line 114): simulated-vs-real compliance paragraph (214 → 572 bytes).
  - `_TRADE_LOG_TWO_FILE_MODEL_MD` (line 126): broker-style vs position-log contrast (336 → 710 bytes).
  - `_TRADE_LOG_COLUMN_GLOSSARY_MD` (line 141): 10-col bulleted glossary (251 → 992 bytes).
  - `_TRADE_LOG_COLUMN_DICT_DEFAULTS` (line 168): canonical 10-row dict, example values anchored on 2020-02-24 COVID trade.
- `TRADE_LOG_EXAMPLE_MD` added to 2 pair configs:
  - `hy_ig_spy_config.py` (StrategyConfig): COVID 2020-02-24 HMM stress 0.09→1.00 → 91.5%→0% at $294.65.
  - `indpro_xlp_config.py` (StrategyConfig): COVID 2020 industrial cycle, 2020-02-29 SELL / 2020-03-31 BUY / 2020-05-31 SELL.
- **umcsent_xlv_config.py NOT created** — flagged to Lead. Pages bypass `render_strategy_page`, so no helper call site exists; creating config would produce orphan code. Suggest backlog item `BL-APP-PT1-UMCSENT`.
- Heads-up to Evan/Dana: `results/hy_ig_spy/winner_trades_broker_style.csv` still uses legacy 12-col schema (`trade_id/entry_date/exit_date/direction/...`) — does not match APP-TL1 canonical 10-col schema. Regeneration needed for UX consistency of the column-dictionary expander. Not blocking Ray.
- Smoke: hy_ig_spy 6/0 PASS · hy_ig_v2_spy 15/0 PASS · indpro_xlp 8/0 PASS · umcsent_xlv 7/0 PASS.
- Handoff: `results/_cross_agent/handoff_ray_wave10h2_20260423.md`.
- Skipped `TRADE_LOG_COLUMN_EXAMPLES` per-pair override — canonical defaults read cleanly for both active pairs.

---

## 2026-04-23 — Econ Evan (Wave 10H.2 follow-up — hy_ig_spy broker CSV schema fix)

**Status:** Done. Ray's APP-TL1 narrative authoring surfaced that `results/hy_ig_spy/winner_trades_broker_style.csv` was on the legacy 12-col schema (Wave 10G artifact). Regenerated to APP-TL1 10-col schema (774 rows = 387 trade-pairs × {BUY,SELL}). Commission 5 bps (pulled from `winner_summary.json::cost_assumption_bps`). Smoke: `passes=6 failures=0`. Addendum appended to `results/_cross_agent/handoff_evan_wave10h2_20260423.md` (corrects prior §6 claim that file was already compliant).

Shared helper untouched — `hy_ig_spy/winner_trade_log.csv` ships in trade-pair format (not position-log format like indpro_xlp / umcsent_xlv), so a one-off converter in `temp/260423_hyig_broker_regen.py` was the right tool. No pipeline rerun.

---

## 2026-04-23 — Wave 10H.2 [Quincy] APP-TL1 cloud verify COMPLETE

**Status:** WAVE 10H.2 READY TO CLOSE. 17/17 PASS.

- Cloud verify HEAD `2574d83` on `https://aig-rlic-plus.streamlit.app`: **17 PASS / 0 FAIL / 17 TOTAL**.
- APP-TL1 markers present on both retro-applied pairs' Strategy pages:
  - `hy_ig_spy`: heading ✓, broker button ✓, position button ✓, preview ✓
  - `indpro_xlp`: heading ✓, broker button ✓, position button ✓, preview ✓
- Regression gate: Sample (`hy_ig_v2_spy`) and `umcsent_xlv` Strategy pages unchanged (both bypassed — hand-rolled / pending BL-APP-PT1-UMCSENT).
- Smoke: all 4 pairs failures=0 (hy_ig_v2_spy 15, hy_ig_spy 6, indpro_xlp 8, umcsent_xlv 7).
- Script extensions: `scripts/cloud_verify.py` — APP-TL1 marker constants, `app_tl1_check` result field, `get_dom` now returns `(text, src, plotly_count, html)` with `frame.content()` captured, `check_page` uses HTML source for APP-TL1 assertions.
- **Pattern 23 discovered** (tab-panel lazy-hide): Streamlit `st.tabs` hides inactive panels via CSS; Playwright `inner_text` does NOT traverse them. First verify pass false-FAILed both retro-applied pairs (Trade Log lives in "Performance" tab; default-active is "Execute"). Fix: use `frame.content()` HTML for tab-content markers. Will codify in qa-agent-sop.md at next SOP revision.
- Handoff: `results/_cross_agent/handoff_quincy_wave10h2_20260423.md`.
- Artifacts: `temp/20260423T075033Z_cloud_verify_wave10h2/`.
