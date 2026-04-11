# Session Notes — Lead Lesandro

## Session: 2026-04-11 (SOP hardening Part D+E + trade log UX)

### Context
Full-day session responding to stakeholder dashboard review (pptx comments from 2026-03-21 and 2026-03-28). Major themes: audience-friendliness, 8-element Evidence template, landing page filters, SOP regression prevention, trade log presentation.

### Commits (8 today)
- `17f1690` Fix StreamlitPageNotFoundError on Cloud (try/except fallback on page_link)
- `8767a8a` Fix chart rendering filename mismatch (Vera prefixed vs Ace unprefixed)
- `61efe7d` SOP: Writing Voice & Audience rules (Research + AppDev)
- `d9aeaff` HY-IG v2 narrative + pages rewritten with audience-friendly rules
- `c5bf1a9` SOP hardening Part D (8-element template + landing filters + classification schema)
- `42c0ea7` Force Cloud redeploy (docstring expansion of pair_registry)
- `62c60e9` SOP hardening Part E (9 stakeholder rules + 15 self-review + 10 cross-review)
- `b6dd6a9` Retroactive HY-IG v2 fixes (unit audit, method coverage, canonical charts)
- `8ef55c5` Trade log UX fix (broker-style CSV + column legend + narrative)

### Tag
- `sop-hardening-partE` — snapshot of SOPs after Parts D+E, before retroactive fixes

### Backup
- `temp/backups/workspace_backup_20260411_213715_62c60e9_sop-hardening-partE.zip` (199 MB, 2078 files, includes .git)

### Key Accomplishments

**Part D (stakeholder presentation fixes):**
- 8-element Evidence template (Method/Question/How-to-Read/Graph/Observation/Deep Dive/Interpretation/Key Message) added to Research + AppDev SOPs
- Classification metadata schema extended (indicator_nature, indicator_type, strategy_objective) with 8 pairs backfilled
- Landing page enhanced: exec summary, 5-column filter row, classification chips, color-coded Sharpe/MDD badges, integrity warning

**Part E (SOP hardening from stakeholder bug review):**
- Wave 1: 9 stakeholder-driven rules + "Explicit Over Implicit" meta-rule across 4 SOPs (+164 lines)
- Wave 2: Phase 1 self-review by 5 agents in parallel, each added 3 targeted rules to their own SOP (+213 lines)
- Wave 3: Phase 2 Path B consolidated cross-review — 10 contract fixes across 5 SOPs in one pass (+136 lines)
- Total +513 lines across 6 SOP files

**Retroactive HY-IG v2 application (validates hardened SOPs):**
- Evan: CCF + Transfer Entropy + Quartile Returns data + tournament_winner.json + regression note
- Vera: Hero chart unit audit revealed data was 100x too small (percent under "bps" label); fixed to 147-1531 bps range with dual-panel layout. Canonicalized correlation heatmap.
- Ray: 3 new 8-element method blocks, bps dual notation throughout, 5 glossary entries expanded per 4-element rubric
- Ace: Evidence page 5 tabs → 8 tabs, render-time 8-element linter implemented

**Trade log UX fix (3-layer fix based on stakeholder complaint):**
- Econometrics Rule C4: dual trade log output (internal position log + broker-style discrete trade log)
- AppDev §3.8 #5: column legend required for any downloadable artifact
- Research: "How to Read the Trade Log" mandatory subsection on Strategy page
- HY-IG v2 pilot: Evan produced winner_trades_broker_style.csv (418 rows, 10 columns), Ray wrote subsection using COVID 2020 concrete example, Ace rebuilt Strategy page with legend + dual downloads + preview dataframe

### Lessons Learned

1. **Agent delegation is load-bearing.** User corrected me twice when I started doing agent-level work manually. Lead role = diagnose + decide + coordinate, never implement. Even "trivial" rewrites (chart file copies, SOP edits) should be dispatched.

2. **SOPs are the right intervention for stakeholder complaints.** The 2026-03-21/28 review had 9 distinct complaints, and every one was a gap in the SOP rules. Fixing the SOPs systematically (rather than one-off patches) is both more maintainable AND validates that the agent team can deliver quality when the rules are clear.

3. **"Silent changes are unacceptable" is the meta-pattern.** Every stakeholder-visible bug (axis inversion, unit mismatch, dropped methods, heatmap signals changed) was an agent making a deliberate decision without documenting it. The fix is always to make the deviation explicit via regression_note.md — not to patch the display layer.

4. **Phase 1 self-review > Phase 2 cross-review** for ROI. When each agent self-reviews and lists "gaps belonging to other agents," you get 80% of the cross-review value at 20% of the dispatch cost. Skipped Phase 2 cross-review entirely and went straight to consolidation — saved 5 dispatches.

5. **Streamlit Cloud needs forced redeploy sometimes.** Pushing code doesn't always trigger a clean redeploy — cached pair_registry.py served stale ImportError. Fixed via trivial docstring change that forced a rebuild.

6. **Playwright text-content checks fail on Streamlit Cloud.** Streamlit renders content inside iframes/shadow DOM that `content` property can't penetrate. Must use tall viewports (6000px) with `full_page=True` screenshots and verify visually.

7. **Hero chart unit audit caught a 100x bug.** The A2 Unit Discipline rule worked on first production use — Vera's new pre-save audit found the percent-vs-bps mismatch that had been in the chart since the 2026-04-10 v2 run. SOP rules validate themselves when agents actually follow them.

### Status
- 5 of 73 pairs completed (HY-IG has both sample and v2, v2 now has 8-method Evidence + broker-style trade log)
- SOPs deeply hardened: 6 SOPs, +513 lines of Part E rules, 3 new trade-log rules
- Cloud portal verified live with all fixes (6 findings, 8-tab HY-IG v2 Evidence, new Strategy trade log section)
- Next: Pair #4 US10Y-US3M, OR cross-pair rollout of trade log UX, OR glossary architecture migration

---

## Session: 2026-04-10

### Context

### Context
SOD checkpoint. Pulled 5 new commits from remote (another session's work on HY-IG execution panel, trade log CSV, bug fixes). No new work done yet in this session.

### New Commits Since Last Session (from remote)
- `dd6d15c` HY-IG SPY execution panel (Phase A-C, 7/8 components)
- `507b115` Fix StreamlitDuplicateElementId in charts
- `8596afa` Fix invalid key in page_link
- `78f0d54`/`bdc997f` Fix trade log path resolution
- `aab9fd0` Add trade log CSV for dashboard display

### Status
- 5 of 73 pairs completed (#1 INDPRO, #2 TED, #3 Permits, #11 VIX/VIX3M, #20 HY-IG)
- FOMC SEP sub-project: viewer functional, 70 meetings indexed
- Next: Pair #4 US10Y-US3M → SPY

### Session Summary
(See 2026-04-10 session below)

---

## Session: 2026-04-10

### Context
SOP hardening Part C: full multi-agent re-run of HY-IG v2, then audience-friendliness improvements.

### Commits (4 today)
- `b009674` HY-IG v2: full multi-agent pipeline test of hardened SOPs (40 files, +12,414 lines)
- `17f1690` Fix StreamlitPageNotFoundError on Cloud (try/except fallback)
- `8767a8a` Fix chart rendering: filename mismatch between Vera and Ace
- `61efe7d` SOP: add audience-friendliness rules to Research and AppDev SOPs (+130 lines)
- `d9aeaff` HY-IG v2: rewrite narrative and pages with audience-friendly SOP rules (+548/-266)

### Key Accomplishments
1. Full 5-agent pipeline re-run of HY-IG v2 (Ray → Dana → Evan → Vera → Ace)
   - Winner: HMM stress / T4_0.5 / P2 Signal Strength (Sharpe 1.27 vs ref 1.17)
   - 18-item completeness gate: 17/17 PASS
2. Diagnosed and fixed 2 Cloud deployment issues:
   - st.page_link fails on Cloud (try/except fallback)
   - Chart filenames: Vera used pair_id prefix, Ace didn't (charts.py now tries both)
3. Comparative analysis: v2 pages vs sample pages — identified 5 audience-friendliness gaps
4. Added 7 new SOP rules across Research + AppDev SOPs
5. Re-ran Ray + Ace with new SOPs — pages now have inline definitions, translation bridges, rule-first layout

### Lessons Learned
1. **Agent delegation**: User corrected me twice for doing agent-level work manually. Lead role = coordinate and decide, not implement.
2. **Chart naming convention needs SOP rule**: Vera and Ace used different naming (prefixed vs unprefixed). Fixed in charts.py loader, but should standardize in team-coordination SOP.
3. **Streamlit Cloud differs from local**: page_link path resolution, version differences. Always test on Cloud, not just locally.
4. **Audience-friendliness is a process gap, not a content gap**: The v2 data was good; the prose style was the problem. SOP rules fix this systematically.
5. **Translation bridges are high-ROI**: Adding "What this means:" after findings dramatically improves readability at minimal cost.

### Status
- 6 of 73 pairs: #1 INDPRO, #2 TED (3 variants), #3 Permits, #11 VIX/VIX3M, #20 HY-IG (sample + v2)
- SOPs now include audience-friendliness rules
- Next: Pair #4 US10Y-US3M → SPY
Brief session — context refresh and sync only. No code changes, no new analysis.

---

## Session: 2026-03-14

### Context
Continued from prior session that completed the multi-indicator enhancement framework and cross-review. This session executed the first 4 priority pairs from the 73-pair catalog.

### Accomplished

**Pair #1: INDPRO → SPY** (commits dd702b6 → ce4da73)
- Full 7-stage pipeline: data → alignment → stationarity → exploratory → 9 models → 1,666-combo tournament → validation
- Surprise: z-score counter-cyclical at extremes (peak-cycle mean-reversion, p=0.007)
- Best OOS Sharpe 1.10 (3M momentum, L6, Long/Cash) vs 0.90 B&H
- 10 Plotly charts, 4 portal pages, landing page redesigned as filterable card grid

**Pair #2: TED Variants → SPY** (commits 6fe3195 → a8ca9f6)
- Splice analysis revealed SOFR ≠ LIBOR (r=-0.04). DFF-DTB3 is canonical TED proxy (r=+0.63)
- Ran 3 variants: SOFR Sharpe 1.89 (inflated, 3yr OOS), DFF 0.97 (robust), Spliced 1.19
- Introduced "variant family" pattern for one-question-multiple-measurements

**Pair #3: Building Permits → SPY** (commits e1c4455 → 01fbb4a)
- Best OOS Sharpe 1.45 (MoM, P25, Long/Short, L6) vs 0.90 B&H
- Pro-cyclical confirmed, first P3 (Long/Short) win
- Pipeline: 7.0s, 856 combos, 675 valid

**Infrastructure & SOP improvements:**
- Landing page: filterable card grid with hover hints on direction badges
- Sidebar: dropdown selector replacing congested flat page list
- Auto-nav hidden via `showSidebarNavigation = false`
- CSS: equal-height cards via flexbox stretch
- Rendering fixes: `render_narrative()` no HTML wrapper; markdown tables for narrow columns
- SOPs updated: MRA protocol (Step 9), Deliverables Completeness Gate (Step 8), Iterative Browser Review (Step 7), Viz Preferences
- Persona renamed Alex → Lesandro

### Key Patterns Confirmed (3/3 pairs)
1. **RoC/momentum signals > level signals** — every pair won with rate-of-change
2. **6-month lead for monthly indicators** — consistent across INDPRO, TED, Permits
3. **Streamlit HTML rendering is unreliable** — always use native components + Playwright verification

### What Worked Well
- Pipeline template reuse (7s for pair #3 vs 13s for pair #1)
- Completeness gate caught the missing TED methodology page pattern
- Variant family approach for SOFR/LIBOR disambiguation
- MRA process improving quality with each iteration

### What Didn't Work Well
- Port proliferation when restarting Streamlit (fixed: always reuse 8501)
- NumPy bool JSON serialization bug (needs `bool()` cast in template)
- First landing page used raw HTML divs (Streamlit silently fails)
- TED methodology page was skipped until user caught it
