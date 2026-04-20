# Release Notes

## 2026-04-20 — Wave 9/10: New Pairs + Enforcement Infrastructure

### New Features

**2 new pairs delivered (of 73 total):**
- **umcsent_xlv** — Michigan Consumer Sentiment × XLV (Health Care). Signal: umcsent_yoy crosses_up 0.0, P1_long_cash, procyclical, L6. OOS Sharpe 1.02, ann return 11.9%, max drawdown -10.9%, 81 OOS months (2019-04 to 2026-01). Portal: pages 10.
- **indpro_xlp** — Industrial Production × XLP (Consumer Staples). Signal: indpro_accel gt 0.75, P3_long_short, countercyclical, L3. OOS Sharpe 1.11, ann return 14.1%, max drawdown -13.5%, 84 OOS months (2019-01 to 2026-01). Portal: pages 14.

**Each pair includes:** 7-stage pipeline script, 10 Plotly charts, 4 portal pages, winner_summary, signal_scope, analyst_suggestions, trade log, tournament CSV (3,332 rows for indpro_xlp).

### Enforcement Infrastructure (3-Layer META-AM)

| Layer | Mechanism | Trigger |
|-------|-----------|---------|
| L1 | Mandatory dispatch template (AGENT_ID + 4-step EOD block) | Structural — every dispatch |
| L2 | PostToolUse hook `check-agent-eod.sh` | Automated — fires after every Agent tool call |
| L3 | QA-CL3 checklist item (now active) | Verified — per-wave QA audit |

**QA-CL4 (Cloud Verify)** added with GATE-27 (chart render), GATE-28 (headless browser no "chart pending"), GATE-29 (clean-checkout smoke test).

### Bug Fixes

| ID | Fix |
|----|-----|
| BL-803 | smoke_loader page glob `9_{pair_id}_*.py` → `*_{pair_id}_*.py` |
| — | EVIDENCE_DYNAMIC_CHARTS: global list → per-pair dict (fixes 8 false-positive failures per new pair) |
| — | umcsent_xlv_regime_stats chart: patched missing `layout.title.text` |
| — | settings.json: 36→19 allow entries, double-slash typo fixed, FRED MCP allow-listed |

### Lessons Learned

| # | Pattern | Evidence |
|---|---------|----------|
| 10 | Schema lag is the dominant QA failure mode at scale | 6 sidecar files required structural fix across 2 pairs |
| 11 | Commit before cloud verify, not after | GATE-28/29 require live cloud pages; order matters |
| 12 | Re-dispatch after context loss is lossy; L1 dispatch template is the only live enforcement mechanism | L2 hook fires post-window-close |
| 13 | Per-pair EVIDENCE_DYNAMIC_CHARTS scoping prevents cross-pair chart name contamination | Global list caused 8 false-positives per pair |

---

## 2026-03-14 — Priority Pair Execution (Pairs #1-3 + #20)

### New Features

**4 priority pairs completed** (of 73 total):
- **#1 INDPRO → SPY** — Industrial Production, OOS Sharpe 1.10 (3M momentum, L6)
- **#2 SOFR/TED → SPY** — 3 variants (SOFR 1.89, DFF-TED 0.97, Spliced 1.19). Splice analysis showed SOFR ≠ LIBOR.
- **#3 Building Permits → SPY** — OOS Sharpe 1.45 (MoM momentum, L6, Long/Short)
- **#20 HY-IG → SPY** — OOS Sharpe 1.17 (pre-existing reference implementation)

**Portal redesigned:**
- Landing page: filterable card grid with 3 columns, equal-height cards, hover hints on direction badges
- Sidebar: dropdown selector ("Choose a finding...") replacing congested flat page list
- Auto-generated Streamlit nav hidden
- Per-pair pages: Story, Evidence, Strategy, Methodology (4 pages each)

**Execution tracking:**
- `docs/pair_execution_history.md` — token usage, timing, MRA sections per pair
- `docs/priority-combinations-catalog.md` — status tracking with comparison notes

### SOP Updates

| Step | SOP Section | What Changed |
|------|------------|-------------|
| 7 | Browser Verification | Mandatory Playwright headless inspection after every portal change |
| 8 | Deliverables Completeness Gate | 15-item checklist (datasets, models, charts, 4 portal pages, sidebar, catalog) |
| 9 | MRA (Measure, Review, Adjust) | Mandatory post-pair reflection with documentation and memory updates |
| — | Viz Preferences | 10 standard charts, color palette, naming convention, Streamlit rendering rules |
| — | Persona | Alex → Lesandro |

### Confirmed Patterns

| # | Pattern | Evidence | Pairs |
|---|---------|----------|:-----:|
| 1 | RoC/momentum signals > level signals | Every tournament won by rate-of-change variant | 3/3 |
| 2 | 6-month lead for monthly indicators | INDPRO, TED, Permits all won with L6 | 3/3 |
| 3 | Streamlit HTML rendering unreliable | `unsafe_allow_html` fails on nested divs | — |

### Lessons Learned

1. **Direction can surprise** — INDPRO z-score was counter-cyclical at extremes (peak-cycle effect)
2. **SOFR ≠ LIBOR** — different risk types (secured vs unsecured), r=-0.04. DFF-DTB3 is the proxy.
3. **Browser verification ≠ completeness** — rendering quality check misses missing pages
4. **`st.metric` truncates** in narrow columns — use markdown tables instead
5. **NumPy bools** aren't JSON serializable — wrap in `bool()`
6. **Don't increment Streamlit ports** — kill old process, reuse 8501

### Infrastructure

- Pipeline scripts: `scripts/pair_pipeline_{indicator}_{target}.py` (per-pair)
- Chart scripts: `scripts/generate_charts_{pair_id}.py` (per-pair)
- Browser verification: `temp/inspect_portal.py` (Playwright, gitignored)
- Memory: file-based (`~/.claude/projects/.../memory/`) + AutoMem MCP
