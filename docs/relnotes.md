# Release Notes

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
