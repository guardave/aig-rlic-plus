# Acceptance — hy_ig_v2_spy — 2026-04-14

**Gate item:** GATE-23 (Pair Acceptance Checklist)
**Pre-stakeholder draft.** Stakeholder review pending; Lead sign-off contingent on stakeholder approval.

---

## Portal-Wide Quality Checklist

Per `docs/agent-sops/team-coordination.md` Portal-Wide Quality Checklist section.

### Landing Page
- [x] Pair appears as card in filtered view with classification chips (Leading / Credit / Min MDD / Counter-cyclical) — verified Cloud landing page
- [x] Performance badges color-coded (Sharpe 1.27 green, Max DD -10.2% amber)
- [x] Card renders without truncation at 1280×900

### Navigation
- [x] Breadcrumb component renders on all 4 pages (Story → Evidence → Strategy → Methodology)
- [x] Sidebar finding selector includes hy_ig_v2_spy
- [x] All Story/Evidence/Strategy/Methodology page_links work

### Story Page
- [x] Hero chart: dual-panel layout, no inversion, axis labeled "Spread (bps, where 100 bps = 1%)" with values in 147-1531 bps range
- [x] KPI strip with interpretation captions (5 KPIs: Lead Time, GFC Spread Peak, Predicted Drawdowns, Strongest During, OOS Test Period)
- [x] "Where This Fits in the Portal" opener echoes landing exec summary themes (N1)
- [x] "Why this indicator?" context sections present with Merton model and CCC-BB quality spread expanders
- [x] Plain English expander at top (N8)

### Evidence Page
- [x] 8-element template applied to all 8 method blocks
- [x] Difficulty tiers: Level 1 (Correlation, Granger, CCF) and Level 2 (Local Projections, Regime, Quantile, Transfer Entropy, Quartile Returns) (N11)
- [x] "Why we chose this method" rationale present in each block's Method element
- [x] Charts use canonical short names (correlation_heatmap, hmm_regime_probs, etc.) per VIZ-A3
- [x] Unit discipline: heatmap axis labels disclose scale; CCF lag axis labeled in days
- [x] Plain English expander at top (N8)
- [x] Quartile Returns "Why this matters" opener present (N6)

### Strategy Page
- [x] Trading Rule in Plain English appears FIRST (rule-first ordering)
- [x] "How to Use This Indicator Manually" subsection present with 3-step routine + 2020 COVID example + caveats (N2, N4)
- [x] "Execution Points — Actual Trigger Dates" table with 8 historical events (N3)
- [x] KPI cards with interpretation captions
- [x] OOS Return labeled as "OOS Return (arithmetic ann.)" with tooltip (N13)
- [x] Trade log: broker-style CSV (418 rows) + column legend expander + dual download + 10-row preview
- [x] "How to Read the Trade Log" narrative subsection with COVID 2020 concrete example
- [x] Tournament leaderboard shows top 20 + "Explore Alternative Strategies" selector with per-strategy metric comparison (N12)
- [x] Plain English expander at top (N8)

### Methodology Page
- [x] Skeptical reader framing in intro
- [x] Methods table with rationale columns
- [x] Diagnostics summary present
- [x] "References" section with 17-entry bibliography organized into 4 categories (N7)
- [x] Inline [AuthorYear] citations link to bibliography
- [x] Plain English expander at top (N8)
- [x] Return Basis explanation note (CAGR vs arithmetic) present (N13 cross-page)

### Cross-Cutting
- [x] Dual notation (bps + %) on first use of unit-laden values per RES-B1
- [x] Plain English expanders on all 5 narrative pages per N8
- [x] Writing voice consistent across pages (financially-literate-non-quant baseline + plain-English layer)
- [x] Honest caveats present on Strategy page ("Honest assessment", "Important Caveats", caveats in How to Use Manually)
- [x] Regression note `regression_note_20260411.md` documents all changes with Approved By + Unchanged + Impact sections

---

## Reference Pair Comparison

**Compared against:** N/A — HY-IG v2 IS the reference pair (first to be tagged).

**Note:** This is the inaugural reference pair. Future pairs will compare against this one. Per META-RPD, when stakeholder approves, this state is tagged as `hy-ig-v2-reference`.

**design_note.md:** Not required — this is the reference establishment, not a deviation from prior reference.

---

## Regression Note

**Files:** `results/hy_ig_v2_spy/regression_note_20260411.md`

**Sections present:**
- Evan's Changes (2026-04-11) — added CCF, Transfer Entropy, Quartile Returns + tournament_winner.json
- Vera's Changes (2026-04-11) — fixed hero chart axis/units, canonicalized heatmap, 3 new method charts
- Ray's Changes (2026-04-11) — 3 new 8-element blocks + bps dual notation + 5 glossary entries expanded
- Ace's Changes (2026-04-11) — Evidence 5 → 8 tabs + render-time linter
- Ray's Follow-up Changes (2026-04-11) — "How to Read the Trade Log" subsection
- Ace's Follow-up Changes (2026-04-11) — Strategy page legend + dual download
- Ray's Reference-Pair Polish (2026-04-14) — 7 narrative changes for reference quality
- Ace's Reference-Pair Polish (2026-04-14) — 5 portal UX changes for reference quality

**Summary of changes from prior version:** Comprehensive — see individual sections in the regression note. All changes traceable to stakeholder feedback items (N1-N13, F1-F15) and SOP rules (META-PWQ, META-RPD, etc.).

---

## Stakeholder Review

**Reviewed by:** Pending
**Review date:** TBD
**Outstanding issues:** TBD after review

---

## Lead Sign-off

**Approved by:** Lead Lesandro
**Approval date:** Pending stakeholder sign-off
**Tag/commit:** Pending — will tag as `hy-ig-v2-reference` upon stakeholder approval
**Current commit:** `6d40af8` (HY-IG v2 reference-pair polish Wave 2A+2B)

---

## Notes for Stakeholder Review

Open issues flagged by agents during this polish (see Ace's report for full context):

1. **Plain English expanders** rendered as `st.expander` rather than HTML `<details>` tags. Functionally equivalent; if stakeholder prefers exact HTML rendering, a CSS sidecar would be needed.

2. **Granger Causality chart** still falls back to local_projections chart (no standalone Granger bar plot exists). Vera could produce one if requested.

3. **CAGR vs arithmetic gap** is stated as "less than ~50 bps" in Methodology Return Basis note. If stakeholder wants the exact computed difference, Evan can derive from the equity curve.

4. **"Explore Alternative Strategies"** shows metric comparison only — no per-strategy equity curve. Could add if requested.

5. **Landing page** intentionally untouched per Wave 2B scope; pair-card metrics still read from `winner_summary.json` (current values are correct).
