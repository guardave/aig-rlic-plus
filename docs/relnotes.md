# Release Notes

## 2026-04-22 — Wave 10F: Standardization Infrastructure + Cross-Review + Migration — **COMPLETE**

**Final cloud verify (Quincy, post-reboot):** indpro_xlp_story PASS (2 charts), indpro_xlp_evidence PASS (3 charts), hy_ig_v2_spy_story PASS (5 charts). All 7 assertions clean on first attempt. No retries needed.

**Two new patterns absorbed during closure:**
- **Pattern 19 (Quincy):** identical DOM across retries = stable stale Cloud deployment; divergent DOM = mid-deploy transient. Distinguishes "wait longer" from "needs manual reboot."
- **Pattern 20 (Quincy):** manual Streamlit Cloud reboot is the definitive fix for stuck auto-redeploy — clean first attempt after reboot, no ambiguity.

**Second code-deletion-gate violation caught during closure:** Ace's item-6 fix to `charts.py` did not catch 6 sibling `getattr` defaults in `page_templates.py` that used the same deprecated `f"{pair_id}_X"` form. Fixed in `a74364f`. Reinforces Pattern 14: VIZ-NM1 deletion gate must be project-wide (`grep -rn 'pair_id}_' app/`), not scoped to the most obvious call site.

**Final commit count:** 10 commits across Wave 10F (90cadd4 → a74364f + closure commits).



### New Infrastructure (team-wide enforcement)

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| Project-local `/sod` | `.claude/commands/sod.md` | Overrides global skill inside repo; 7-step procedure (identity → profile → PWS → project docs + team-standards.md → sop-changelog.md since `last_seen` → team status → acknowledge) |
| PreToolUse hook | `scripts/hooks/check-agent-sod.sh` | Warns Lead if Agent dispatch prompt lacks `## SOD Block` |
| PostToolUse hook | `scripts/hooks/check-agent-eod.sh` (moved from `~/.claude/hooks`) | Warns Lead if dispatched agent didn't update global profile |
| Canonical cross-agent conventions | `docs/team-standards.md` | Single source of truth for filenames, sidecars, palette, handoff contracts, deploy artifacts |
| Changelog | `docs/sop-changelog.md` | Append-only rule log; read-since-last_seen at every SOD |
| Dispatch template extension | `## SOD Block` now mandatory in every agent prompt | Enforced via PreToolUse hook |

Hooks now live in `scripts/hooks/` (repo-local, portable); settings reference repo-relative paths. Single source of truth.

### New Rules

| Rule | SOP | Scope | Purpose |
|------|-----|-------|---------|
| META-RYW | team-coordination.md | ALL | Read Your Own Work before handoff — log chart/numeric/instrument re-read in handoff note |
| META-NMF | team-coordination.md | ALL | No ad-hoc/manual fix ever — every fix flows SOP-first, dispatch-second |
| META-AM sandbox fallback | team-coordination.md | ALL | Session-notes fallback when sandbox denies home-dir writes; temporary, not equivalent to profile |
| VIZ-IC1 | visualization-agent-sop.md | Vera | Pre-save intra-chart consistency: title-axes, legend-data, annotations-data, palette aliases, units, narrative-alignment note |
| RES-NR1 | research-agent-sop.md | Ray | Narrative instrument references must match `interpretation_metadata.target_symbol` |
| GATE-NR / QA-CL5 | qa-agent-sop.md | Quincy | DOM scan of Story/Evidence pages for wrong-pair instrument names |
| APP-PT1 supplement | appdev-agent-sop.md | Ace + Ray | Narrative prose in pair_configs must be authored by Ray, not Ace |
| APP-SS1 | appdev-agent-sop.md | Ace | `signal_scope.json` consumer uses `indicator_axis.derivatives` / `target_axis.derivatives` schema |
| ECON-DS2 quality gate | econometrics-agent-sop.md | Evan | Explicit checklist item: `git ls-files signals_*.parquet` ≥1 before handoff |
| GATE-29 parquet check | qa-agent-sop.md | Quincy | Clean-checkout test now explicitly verifies signals parquet committed |

### Cross-Review Outputs (6 agents in parallel, Opus min)

Each agent produced a structured findings doc at `_pws/_team/cross-review-20260420-<role>-<name>.md`. Consensus decisions ratified in `docs/team-standards.md` §2.1, §3, §4:

- **§2.1 Chart filenames:** bare-name canonical (`{chart_type}.json`); pair-prefixed deprecated. Unanimous.
- **§3 Sidecar schema:** `_meta.json` for charts (Vera), `_manifest.json` for datasets/models (Dana/Evan) — deliberate split, two classes. Unanimous.
- **§4 Color palette v1.1.0:** added `benchmark_trace` (`#6C7A89` muted slate) + `aliases` block (`indicator`/`target`/`benchmark` → visual keys). Majority (3/6).

### Migrations Executed

| Pair | Chart files | Sidecars added | Status |
|------|-------------|----------------|--------|
| hy_ig_v2_spy | 17 unique charts (5 deprecated duplicates deleted, 12 renamed prefixed → bare-name) | 12 new sidecars | All bare-name ✓ |
| indpro_xlp | 10 renamed prefixed → bare-name | 10 new sidecars | All bare-name ✓ |
| umcsent_xlv | 10 renamed prefixed → bare-name | 10 new sidecars | All bare-name ✓ |

Loader pair-prefix fallback at `charts.py:106-113` **removed** after all three pairs confirmed bare-name-only. 13-day violation of VIZ-NM1 closed.

### Dead Letters Identified (backlog for future waves)

- DATA-D12 (column suffix linter) — no script exists
- DATA-D13 (manifest.json + display_name_registry.csv) — files absent
- META-XVC (cross-version diff) — no diff tool, rubber-stamped
- GATE-30 (deflection audit) — 0 FAILs in 7 runs
- `chart_manifest.json` documented but absent on disk
- 3 HY-IG v2 charts with zero consumer references (`hero_spread_vs_spy`, `spread_history_annotated`, `tournament_sharpe_dist`) — candidate for deletion after audit
- HY-IG v2 pages not yet migrated to APP-PT1 templates (item 8, separate wave)

### Bug Fixes (Wave 10F)

| Fix | Where |
|-----|-------|
| VIZ-IC1 §6 sidecar name `_manifest.json` → `_meta.json` | visualization-agent-sop.md:962 |
| VIZ-IC1 §4 palette reference uses aliases | visualization-agent-sop.md:960 |
| Deprecated `output/_comparison/` path corrected | research-agent-sop.md:672 |
| `interpretation_metadata.json` producer: Evan → Dana | research-agent-sop.md:1000 |
| Loader pair-prefix fallback removed | app/components/charts.py |
| Permission allow-list extended (Edit, Bash tee -a, cat >>) | .claude/settings.json |

### Commits (in order)

`90cadd4` → `f1d78bb` → `85ee737` → `daea311` → `beb84a5` → `3c6bb50` → `27fb01f` → `cc99fc4` (+ checkpoint commit).

### Lessons (to absorb into future waves)

| # | Pattern | Evidence |
|---|---------|----------|
| 14 | Rule adoption without code-deletion gate leaves dead violators alive | Loader fallback persisted 13 days after VIZ-NM1 was ratified |
| 15 | Permission allow-lists must enumerate every tool that might be used (Write ≠ Edit ≠ Bash append) | 5 of 6 cross-reviewers hit home-dir write denials despite `Write(...)` in allow-list |
| 16 | Cross-review surfaces silent-weakening bugs invisible in single-wave work | Quincy found 12 SW observations (META-XVC, GATE-30, META-NMF, QA-CL3 all rubber-stamped to some degree) |
| 17 | "Missed read" risk solved by project-local command override, not global skill extension | Global `/sod` + `team-coordination.md` split would scatter concepts; single project-local file keeps it canonical |
| 18 | Two-name sidecar split (_meta.json / _manifest.json) is not a conflict — different classes need different names | Apparent conflict turned out to be a single-line drafting slip in VIZ-IC1 §6 |

---

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
