# Team Status Board

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
