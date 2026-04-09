# Session Notes — Lead Lesandro

## Session: 2026-04-09

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
