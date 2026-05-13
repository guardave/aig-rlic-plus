# Session Notes — Lead Lesandro
**Date:** 2026-05-13
**Branch:** 260430

## Session Accomplishments

### 1. Reader-facing portal fixes — v4 scratch dashboard

Continuation of the v4 wave. User reported three issues from a reader walk:
1. Page titles show narrative headline only — pair not visible
2. Episode charts don't match reference (no NBER shading on non-recession episodes; HY-IG line invisible)
3. IS / OOS jargon not explained

**Landed (10 commits, all in `260430`):**

- **DPS-PI1** — pair caption (`Pair: HY-IG Credit Spread × SPY`) added unconditionally below `st.title` on all 4 page templates (`page_templates.py`).
- **Strategy heading reader-friendly** — `Tournament Winner: S2c_zscore_36m / P1_long_cash / L0 (no additional lead)` → `Best Strategy Found: S2C Zscore 36M — Long / Cash Switch, Countercyclical`. Uses `signal_display_name` and a family label map. Commit `e6c013d`.
- **Dynamic glossary search** — replaced static sidebar expander with text-input field + relevance ranking (exact key → starts-with → key substring → definition → full-text). Up to 8 results in collapsible expanders. Commit `044cf68`.
- **Removed ⓘ info bubbles** from page templates — glossary search covers the use case. Commit `6544b6a`.
- **Episode chart fixes (5 JSONs)** — three iterations:
  1. `a8863dc` — explicit y-axis ranges (didn't work, overlaying clipped data)
  2. `f7965a1` — switched from `overlaying:y` to separate vertical domains [0.43,1.0] / [0.0,0.38]
  3. `7f2470d` — two-xaxis design (`xaxis.matches=x2`, `showticklabels=false` on top) so date labels appear only below bottom panel
  4. `76321b0` — reader captions moved to inter-panel gap (y=0.405 paper, white bg); amber stress shading consistency; sparkline labels; exposure chart title; Strategy subtitle softened to acknowledge failed final exam.

### 2. Lessons-learned promoted to standards

The Plotly dual-axis issue had happened before but wasn't documented. User asked whether agents are likely to forget. Result:

- **Lesson 13** added to `.claude/memory/lessons-learned.md` covering both the domain-separation rule AND the two-xaxis companion rule (`09dde65`, `7f2470d`).
- **CLAUDE.md updated** — `lessons-learned.md` marked **MANDATORY** reading at SOD and before any visualization work, not just "consult before infra changes" (`a5e0753`).
- **VIZ-TS1 rule** added to `visualization-agent-sop.md` and cross-referenced from `dashboard-page-standard.md` (`7f3b64b`). Codifies the time-axis sync requirement for all multi-panel time-series charts. Includes canonical layout, forbidden patterns, cross-panel shape duplication rule, and verification script. Marked BLOCKING pre-handoff gate.
- Auto-memory entry `feedback_plotly_dual_axis.md` written as backup.

### 3. Multi-agent inspection + parallel fix

After standards landed, Lead ran a structured Playwright walk of all 4 v4 pages — 11 findings (F1–F11), severity P1–P3. Dispatched two agents in parallel:

- **Vera (Viz)** — fixed F1/F2 (caption overlap on dotcom, gfc, covid, taper, inflation episode charts) and F3 (amber stress shading consistency across both panels).
- **Ace (App Dev)** — fixed F4 (sparkline titles + threshold value labels), F5 (exposure step chart title), F11 (Strategy page subtitle tone — added "did not pass holdout test" caveat).

Lead verified live via fresh Playwright screenshots before committing — bundle commit `76321b0`.

## Key Decisions

- **VIZ-TS1 applies project-wide** — not just episode zoom. Hero dual-panel and equity-curves with stacked indicator panel are explicitly in-scope.
- **Standards live in `docs/`, lessons live in `.claude/memory/`** — auto-memory was insufficient (truncation + not consistently consulted). Project files in git survive context compaction, agent handoffs, and new sessions.
- **The two-x-axis pattern is BLOCKING, not advisory** — pasted verification output required in handoff notes alongside VIZ-DP1.
- **Lead self-verifies via Playwright before commits** — no longer delegating browser checks to subagents post-fact. Server restart is a Lead action between every JSON edit because `@st.cache_resource` doesn't watch file mtime.

## Outstanding / Deferred

- **F6** — rolling correlation chart (Evidence): three overlapping lines are hard to read. Recommend small-multiples or single-window with band. P3.
- **F7** — rolling Granger p-value chart (Evidence): no interpretation overlay. Shade p<0.05 zones. P3.
- **F9** — minor inconsistency: Evidence/Strategy show breadcrumb "you are here" caption on a separate row, Methodology has it inline. P3.
- **F10** — sidebar "Glossary" heading visual hierarchy. P3.
- **Existing pairs retroactive GATE-RW1 walk** — deferred from prior session.
- **Existing pairs retroactive GATE-DPS1 uplift** — deferred from prior session.
- **Existing pairs retroactive VIZ-TS1 audit** — new. Run the VIZ-TS1 verification script across all `history_zoom_*.json` files in the repo to find lurking pre-fix charts.

## Process Note

The Plotly dual-axis issue surfaced twice because the lesson wasn't recorded in a place agents reliably consult. The fix is structural: lesson in `.claude/memory/lessons-learned.md` (read at SOD per CLAUDE.md), rule in `visualization-agent-sop.md` (read by Vera per role SOP), cross-reference from `dashboard-page-standard.md` (read by anyone touching Story page). Three orthogonal entry points so the lesson can't slip through.

---

## Late-Evening Backlog Clearance Wave (2026-05-13 EOD continuation)

Lead surveyed all 7 role PWS outstanding-work files and dispatched 3 agents to close immediately-actionable items:

### Closed
- **Ace** — Committed 3 smoke-test loader logs (v3_rerun, v3_retro, v4_from_scratch) (`5870151`). Ran **VIZ-TS1 retroactive audit** across all `history_zoom_*.json` files: **104/104 PASS** across 11 pairs (`6e28bfb`). Today's reader-walk fixes brought the codebase into universal compliance with the new rule on first day.
- **Quincy** — Verified the 3 smoke logs against current `app/pages/` (`8205394`). Flagged v3_rerun + v3_retro logs as WARN — they reference `90_*` and `91_*` page files retired during v4 cutover. Logs preserved as historical audit trail. Closed **OW-2: GATE-VIZ-NBER1 WARN → FAIL severity flip** in `scripts/cloud_verify.py` (`1dd65e3`).
- **Vera** — Closed **OW-1 P1 perceptual-PNG backlog**: 197 sidecars already on disk across all 9 legacy pairs from prior waves. The OW item was stale. Spot-checked renders are clean. Updated PWS (`f9e6aaa`).

### Lead disposition decisions
- **v3 smoke logs (WARN)**: leave in place as historical artifacts. Audit trail is complete via Quincy's verification note + git history. No rename needed — adding metadata would just be noise.
- **Quincy's WARN flag for legacy perceptual PNGs**: stale per Vera's audit. Quincy can re-run her perceptual gate to clear it on next QA cycle.

### Items deferred (not dispatched tonight — bigger windows needed)
- Ace P0: GATE-HZE1 implementation in `cloud_verify.py` (needs Quincy pseudocode review coordination)
- Ace P1: APP-PT1 retro-apply for `hy_ig_v2_spy` (last reference pair)
- Dana P1: BL-D12-LINTER + BL-D13-MANIFEST (batch with Wave 10H.2/10I hygiene wave)
- Evan P1: BL-LEGACY-WINNER-SUMMARY-SHAPE (waiting on FE1 contract arbitration)
- Ray: Pair #4 dispatch + RES-OD1 fix (next priority pair wave)

5 agent commits + 1 Lead update pushed to origin in this clearance wave.
