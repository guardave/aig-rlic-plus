# AIG-RLIC+ SOP Changelog

Chronological record of every rule addition and modification across the AIG-RLIC+ agent SOP system. New rules are entered here first, then registered in [`docs/standards.md`](standards.md) and/or [`docs/team-standards.md`](team-standards.md).

Entries are listed newest-first. Each entry cites the commit hash (when available), date, scope, and summarizes what changed.

**SOD read protocol (added Wave 10F):** every agent, at session start, reads this file from the top down to the first entry whose date is earlier than the timestamp in `~/.claude/agents/<role>-<name>/last_seen`. Every entry above that line is a rule added while the agent was away — apply if scope matches.

---

## 2026-04-23 — Wave 10H.2 Closure: APP-TL1 Shipped + Pattern 23 Codified

**Final cloud verify (commit `8e743ce`):** 17/17 PASS. APP-TL1 retro-applied to `hy_ig_spy` and `indpro_xlp`. Regression gate holds for Sample (legacy page) and umcsent_xlv (tracked as BL-APP-PT1-UMCSENT).

**Pattern 23 codified** in `qa-agent-sop.md` §Cloud Visual Smoke item 4: `frame.inner_text("body")` does NOT traverse hidden `st.tabs` panel content — only the active tab's text is returned. Fix: use `frame.content()` HTML for tab-gated markers; retain `inner_text` for unconditionally-visible surfaces. Direct analog of Pattern 22.

**What agents need to know going forward:**
- Every pair added from Wave 10H.2 onward ships APP-TL1-compliant Strategy page via the template, with `TRADE_LOG_EXAMPLE_MD` as a required pair-config narrative anchor.
- Sample legacy Strategy page decommission tracked as follow-on (sibling to BL-APP-PT1-LEGACY).
- QA verify scripts: for Strategy-page markers (and any marker inside `st.tabs`), use `frame.content()` not `frame.inner_text()`.

**Git tag:** `wave-10h2-complete` pinned at `8e743ce`.

---

## 2026-04-23 — Wave 10H.2: APP-TL1 Trade Log Rendering Contract

**Trigger.** User surfaced a regression after Wave 10H.1 shipped: the newly-rebuilt `hy_ig_spy` (on APP-PT1 template) has a "Download Trading History" section less rich than Sample (`hy_ig_v2_spy`, hand-written legacy). Sample has dual downloads (broker-style + researcher position log), multi-paragraph narrative scaffold, column glossary, concrete example, always-visible preview. Template has a single generic `st.download_button` with no prose. Every template-based pair inherited the regressed view. Direct mirror of `BL-APP-PT1-LEGACY`: reference richer than template.

**Discovery dispatch (Ace, commit `3d6f096`):** full delta report at `results/_cross_agent/ace_discovery_trade_log_20260423.md`. Blast radius: 3 template-based pairs (`hy_ig_spy` — pure renderer gap; `indpro_xlp`, `umcsent_xlv` — renderer + data gap, broker-style CSV missing). Sample itself retains richer legacy page.

**Rule added:**

- **`docs/agent-sops/appdev-agent-sop.md` — APP-TL1 Trade Log Rendering Contract.** Binding: `render_strategy_page()` MUST invoke `_render_trade_log_block(pair_id, config)` helper producing the full Trading History block — dual CSV artifacts (`winner_trades_broker_style.csv` primary + `winner_trade_log.csv` secondary), fixed 5-element narrative scaffold (heading, simulated-vs-real disclosure, two-file model, column glossary, pair-specific example), column-dictionary expander, two-column download layout (primary broker + secondary researcher), always-visible 10-row preview with captions. APP-SEV1 alignment: both missing = L1 short-circuit; one missing = L2 degraded render; malformed = L2 warning + healthy-pane render; missing pair-specific example = L3 caption coda. Ownership: Ace (structure), Ray (narrative defaults + pair example via `TRADE_LOG_EXAMPLE_MD` config anchor), Evan (broker-style CSV production), Dana (schema), Quincy (QA gate). Migration: 6-step protocol; first land scope = 3 template pairs + template upgrade + narrative canon + data backfill + QA verify. Sample decommission + legacy-pair audit deferred as follow-ons.

**What changes for agents going forward.** Every new pair from Wave 10H.2 onward ships with APP-TL1-compliant Strategy page by default via the template. Existing template-based pairs (`hy_ig_spy`, `indpro_xlp`, `umcsent_xlv`) retro-apply in this wave. Pair configs gain `TRADE_LOG_EXAMPLE_MD` as a required narrative anchor.

**Open scope (retro-apply, dispatched Wave 10H.2):** Ace template structure + Ray narrative + Evan data + Quincy verify.

---

## 2026-04-23 — Wave 10H.1 Closure: Chart Governance Framework Shipped End-to-End

**Scope.** No new rules this entry — this records the implementation closure of the rules shipped in Wave 10H (paper SOPs) and Wave 10H.0 (Lead discipline). Purpose: tell future agents the framework is now live.

**Final cloud verify (commit `aca5602`):** 17/17 PASS on all active pairs × 4 pages + landing.

**What agents need to know going forward:**

1. **VIZ-O1 disposition** is now enforced — every `*_meta.json` sidecar in `output/charts/*/plotly/` must carry `disposition: "consumed" | "suggested" | "retired"`. Quincy's `scripts/cloud_verify.py` audits this on active pairs; GATE-28 scope now includes it. Vera writes the field at production time on 3 of 7 pair generators; the other 4 are flagged as `BL-VIZ-SIDECAR-HELPER` for a hygiene wave.

2. **VIZ-E1 exploration zone** is now routable — Vera's `exploratory_charts` entries in `results/{pair_id}/analyst_suggestions.json` auto-render on the Methodology page (for pair pages that use the template). Each entry carries ELI5 `narrative_alignment_note` (blocking requirement) + `vera_rationale`. Feedback loop: users see the section, tell the team which to promote.

3. **APP-PT2 Methodology Exploratory Insights** is live on Sample pair. For pairs using `render_methodology_page()` it is automatic. For the 5 legacy Methodology pages that bypass the template (`BL-APP-PT1-LEGACY`), the helper must be called directly from the page file until migration. This is a silent-regression risk class — agent briefs for any Methodology-page rule addition MUST explicitly list bypass pages requiring defensive direct calls.

4. **Pattern 22 fix** is now canonical — use `query_selector_all(".js-plotly-plot")` on the DOM tree, never `inner_text.count("js-plotly-plot")`. Playwright `page.frames` iteration races Streamlit frame registration; use `wait_for_selector('iframe[title="streamlitApp"]').content_frame()` instead. Codified in qa-agent-sop.md.

5. **LEAD-DL1 is validated in practice.** Wave 10H.1 end-to-end: 3 agent dispatches (Ace, Vera, Quincy) + 1 follow-up Ace dispatch + 1 Quincy re-verify dispatch, zero Lead commits touching agent-owned files post the initial revert. Lead commits in the wave touch only `docs/` + `.claude/settings.json` (infrastructure). Self-audit at closure: `git log --author='Lead' --since='Wave 10H start' --name-only` confirms compliance.

6. **Permissions syntax (infrastructure).** `settings.json` entries targeting absolute paths must use double-slash prefix (`Write(//home/vscode/.claude/agents/**)`). Single-slash is project-relative per Claude Code docs. Fix `b3facc8` validated twice — global-profile writes succeed without prompt on current subagent dispatches.

**Open backlog (Wave 10H.2/10I candidates):** `BL-VIZ-O1-LEGACY` (35 legacy-pair sidecars), `BL-VIZ-SIDECAR-HELPER` (4 generator refactors), `BL-APP-PR1` (path resolution discipline), `BL-APP-PT1-LEGACY` (5-Methodology-page template migration). All bundleable into one hygiene wave.

**Git tag.** `wave-10h1-complete` pinned at `aca5602`.

---

## 2026-04-22 — Wave 10H.0: Lead Delegation Discipline (LEAD-DL1)

**Scope:** Lead agent only. Affects every future wave's execution-vs-authorship boundary.

**Trigger.** During Wave 10H.1 planning I accepted a user ask to "proceed as suggested" and then implemented the framework myself — Ace's template helper, Vera's sidecar backfill + ELI5 exploratory-chart authoring, Quincy's Pattern 22 script fix — 70+ files under Lead identity. User reverted it: *"Drilling into execution often blurs your vision into the bigger picture. Please find a way to maintain this discipline so that you grow into a genuine leader."*

**Rule added (new Lead SOP):**

- **`docs/agent-sops/lead-agent-sop.md` (new file) — LEAD-DL1 Delegation Discipline.** Binding: Lead never writes to files owned by role agents. Lead-owned write categories are explicitly enumerated (SOPs, coordination docs, meta docs, `_pws/_team/`, `_pws/lead-lesandro/`, git tags). Everything else → dispatch. Pre-edit gate, narrow exceptions (emergency / user override / self-revert), File Ownership Map covering all 6 agents + shared-key files (analyst_suggestions.json, pair_config.py), self-audit protocol at wave closure (`git diff --stat` against Ownership Map).

**Memory trigger added:**

- `memory/lead_delegation_discipline.md` — loaded at every SOD via `MEMORY.md` index.

**What this changes going forward.** Every Lead action that would touch a file now runs the pre-edit gate: *who owns this file?* If not Lead → stop and dispatch. Wave closures include a Lead-commit self-audit step. Any drift surfaces as a "Lessons" entry in relnotes and a PWS escalation.

---

## 2026-04-22 — Wave 10H: Chart Governance + Exploration Framework

**Scope:** visualization agent (VIZ-O1, VIZ-E1), app dev agent (APP-PT2), QA agent (Pattern 22 fix, QA-CL2 P2 exception). Affects Vera, Ace, and Quincy. Lead-authored.

**Rules added:**

- **VIZ-O1 — Chart Disposition Mandate (`visualization-agent-sop.md`):** Every chart Vera produces must receive one of three dispositions before handoff: `consumed` (page template references it), `suggested` (routes to Methodology Exploratory Insights section per APP-PT2), or `retired` (logged with reason, not shipped). Disposition is recorded in the chart's `_meta.json` sidecar. Missing or blank disposition is a GATE-28 failure. Closes the chart evaporation gap exposed by the 3 orphaned Sample charts.

- **VIZ-E1 — Exploration Zone + Sidecar Spec (`visualization-agent-sop.md`):** Vera is not confined to the core chart set. Every pair_config has a Core zone (mandatory named slots) and an Exploration zone (open — Vera produces any chart she judges analytically valuable). Exploratory charts get `"exploratory": true, "disposition": "suggested"` in their `_meta.json` sidecar. Mandatory sidecar fields: `narrative_alignment_note` (ELI5 plain-English explanation, **no jargon**, displayed verbatim on Methodology page), `vera_rationale` (one-line analyst note, italicized below ELI5 caption). The ELI5 field is a blocking handoff requirement for exploratory charts.

- **APP-PT2 — Methodology Page Exploratory Insights Section (`appdev-agent-sop.md`):** `render_methodology_page()` must render an "Exploratory Insights" section at page bottom when `results/{pair_id}/analyst_suggestions.json` has ≥1 entry under `"exploratory_charts"`. Section renders: section heading → `st.info` callout (non-quant framing + feedback invitation) → for each chart: rendered chart + ELI5 caption (`st.caption`) + Vera's rationale (italic) + feedback prompt. Non-blocking default: charts ship automatically without editorial gate. Promotion to core template slot happens at wave closure. Backward-compatible: older pairs with no `exploratory_charts` key render Methodology page identically.

- **Pattern 22 fix — QA cloud verify (`qa-agent-sop.md`):** DOM chart detection via `.count("js-plotly-plot")` on `page.inner_text()` always returns 0 — CSS class names are not included in extracted text. Correct approach: `page.query_selector_all(".js-plotly-plot")` on the DOM tree, or text-marker heuristics (axis labels, date strings). False-negative trap removed from cloud verify protocol.

- **QA-CL2 P2 exception (`qa-agent-sop.md`):** Triangulation 3 (annual turnover ↔ trade count ↔ horizon) is not applicable to P2 continuous-rebalancing strategies (`position_sizing = "proportional"` or `"signal_strength"`). For these strategies, `annual_turnover` is portfolio-change-weighted and `oos_n_trades` counts daily rebalances — incommensurate quantities. Quincy skips T3 and records "N/A — P2 continuous rebalancing" in findings. Schema gap (no `turnover_basis` enum) tracked in backlog BL-802.

---

## 2026-04-22 — Wave 10G: Sample Ratification + Archive + New HY-IG × SPY

**Scope:** sample governance, namespace management, template extensions, full pair pipeline. Affects ALL agents for discoverability; Lead owns ratification, dispatches agents for new pair build.

**Sub-phases committed so far:**

- **Wave 10G.1 (commit `02251bd`):** v1 `hy_ig_spy` archived to `_v1` suffix. All artifacts moved via `git mv` (history preserved): `results/`, `data/`, `scripts/`, `docs/`, `app/pages/`. `app/pages_archive/` created (Streamlit does not auto-scan). `app/components/pair_registry.py` hardcoded v1 block removed; auto-discovery loop now skips any directory ending in `_v1` or `_archived`. Legacy flat-layout conditionals in `execution_panel.py` and `generate_winner_outputs.py` remapped from `pair_id == "hy_ig_spy"` to `pair_id == "hy_ig_spy_v1"` to isolate legacy logic and prevent false-matching the fresh `hy_ig_spy` pair created in Wave 10G.4.

- **Wave 10G.2:** `hy_ig_v2_spy` ratified as the **Sample / canonical reference pair**. Git tag `sample-v1.0`. `pair_registry.py` now flags it with `is_sample=True` and renders a blue SAMPLE badge on its landing-page card. Every future pair is quality-compared against Sample (feature set: probability engine, position adjustment, trigger cards, 3-way direction check, 8-element Evidence, historical zoom charts, etc.). Sample pair_id and on-disk paths unchanged — display-layer rename only.

**Planned sub-phases (to be completed in this session or next wave):**

- **Wave 10G.3 (DONE — 2026-04-22):** extended `app/components/page_templates.py` with two optional config fields: `HISTORY_ZOOM_EPISODES` (list of crisis-episode dicts on Story page, renders "How the Signal Performed in Past Crises" section with per-episode chart via `load_plotly_chart`, APP-SEV1 L2 on missing artifact) and `regime_context` (optional markdown string on Evidence method block dict, renders `st.info(...)` callout between theory and chart). Both additive/optional — existing pairs render identically. APP-PT1 supplement added to `appdev-agent-sop.md`. smoke_loader: indpro_xlp 8/0, umcsent_xlv 7/0, hy_ig_v2_spy 15/0.

- **Wave 10G.4A–F:** full 5-agent pipeline (Dana → Ray → Evan → Vera → Ace → Quincy) to build a fresh `hy_ig_spy` pair using the latest SOPs + extended templates. Targets Sample-quality feature parity via template (no hand-coded pages).

- **Wave 10G.5 (COMPLETE — 2026-04-22):** cloud verify exposed two class-of-duplication bugs + one raw-column-leak content bug. All resolved:
  - `_page_prefix()` duplicate routing dict in page_templates.py → APP-RL1 added + merged to pair_registry (`35bb008`).
  - Missing `hy_ig_spy` entry in `indicator_names` → fixed same commit.
  - `interpretation_metadata.key_finding` leaked column identifiers (`hy_ig_spread_pct`, `spy_fwd_63d`) → DATA-D6b added, Dana rewrote to human-readable (`3c37d96`).
  - Final cloud verify (`bd3wvyjep`): landing PASS, all 4 hy_ig_spy pages zero-traceback / breadcrumb-present / no-prefix-pending.
  - **Pattern 22 (new):** DOM chart detection via `.count("js-plotly-plot")` on `inner_text` always returns 0 — CSS class names don't appear in extracted text. Use text markers (axis labels, month-year patterns, chart titles) or query the DOM structure via `query_selector_all`.
- **Wave 10G.5 (IN PROGRESS — 2026-04-22):** cloud verify exposed two class-of-duplication bugs:
  - `_page_prefix()` in `page_templates.py` had a duplicate routing dict that Ace missed when adding `hy_ig_spy` to `pair_registry.py`'s routing dict → `StreamlitPageNotFoundError` on Story + Evidence pages.
  - `indicator_names` dict in `pair_registry.py` missing `hy_ig_spy` entry → landing-page card displayed the raw column identifier `"hy_ig_spread_pct"` instead of a human label.
  **SOP additions in response:**
  - **APP-RL1 (appdev-agent-sop.md, ace):** single-source routing / label maps — no duplicate dicts across modules. Detection grep + canonical-location list. Pattern 14 sibling.
  - **GATE-28 scope extension (qa-agent-sop.md, quincy):** cloud verify now covers ALL active pairs × ALL 4 pages with zero-Python-error requirement. Partial pass → wave does not close. Rationale: the Wave 10G incident where a fix for one page didn't re-verify the others.

## 2026-04-20 — Wave 10F: Standardization Infrastructure (Lead)

**Scope:** team-coordination.md + new project-local /sod + new hooks + new team-standards.md. Affects ALL agents.

**Additions:**

- **META-RYW (team-coordination.md, ALL agents)** — **Read Your Own Work before handoff.** Every producer re-reads their deliverable end-to-end (prose word-by-word, each chart matched against its description, each numeric claim against its source, each instrument/date/direction word against interpretation_metadata.json) and logs the re-read in the handoff note. Closes the class of bug where agents ship artifacts without looking at them (Wave 10E "S&P 500 on XLP page" was the proximate trigger).
- **VIZ-IC1 (visualization-agent-sop.md, vera)** — **Pre-save intra-chart consistency check.** Before saving any chart JSON, Vera asserts: title↔axes coherence; legend↔data series match; annotations↔data range match; palette registry conformance (role-based aliases); unit discipline in tick formatters; narrative-alignment note in chart _meta.json sidecar.
- **Project-local `/sod` (new `.claude/commands/sod.md`, ALL agents)** — project override of the global `/sod` skill. Defines the 7-step SOD procedure for this project: identity → global profile → PWS → core project docs + team-standards.md → sop-changelog.md since last_seen → team status → acknowledge. Updates `last_seen` at end.
- **SOD / EOD hooks moved into repo (`scripts/hooks/`)** — `check-agent-sod.sh` (new PreToolUse) + `check-agent-eod.sh` (moved from ~/.claude/hooks). `.claude/settings.json` uses repo-relative paths. Portable across clones; single source of truth.
- **Mandatory Dispatch Template extended** — every dispatch prompt must now contain `## SOD Block` in addition to the existing `AGENT_ID:` line and `## MANDATORY EOD` block. PreToolUse hook warns if SOD block absent.
- **`docs/team-standards.md` (stub)** — new canonical cross-agent conventions file (directory layout, filename conventions, sidecar schema, palette roles, handoff contracts, deploy-required artifact registry, dispatch template). Sections marked `[TO BE POPULATED BY CROSS-REVIEW]` are held for the next wave's parallel agent audit.

**Commit:** `90cadd4` (infrastructure portions); this changelog update is part of the same wave.

---

## 2026-04-20 — Wave 10E: Template Abstraction + Narrative Accuracy + ECON-DS2 Gap (Multi-agent)

**Scope:** appdev-agent-sop.md + research-agent-sop.md + qa-agent-sop.md + econometrics-agent-sop.md + team-coordination.md. Affects ALL agents.

**Additions:**

- **APP-PT1 (ace)** — **Page Template Abstraction.** New pair portal pages MUST be thin wrappers calling `app/components/page_templates.py`. Pair-specific content lives in `app/pair_configs/{pair_id}_config.py`. Any `st.*` call in a page file (other than the template call) is a gate failure. Eliminates copy-paste drift across pairs.
- **APP-PT1 supplement (ace + ray)** — **Narrative authorship.** Narrative prose in `pair_configs/` MUST be authored by Ray, not Ace. Ace renders structure only; narrative fields are explicit placeholders until Ray delivers. Prevents the Wave-10E "wrong instrument in narrative" class of bug.
- **APP-SS1 (ace)** — **signal_scope.json consumer contract.** Methodology page readers MUST use the `indicator_axis.derivatives` / `target_axis.derivatives` schema, not the legacy `in_scope.*` flat arrays. Empty Signal Universe columns = L1 st.error + short-circuit.
- **RES-NR1 (ray)** — **Narrative instrument reference accuracy.** All instrument names in narrative prose must match `interpretation_metadata.json.target_symbol`. Log RES-NR1 check in handoff. Ray owns all narrative prose for a pair (no copy-paste from other pairs without pair-specific re-authoring).
- **GATE-NR / QA-CL5 (quincy)** — **Narrative instrument reference check.** DOM scan of Story/Evidence pages for wrong-pair instrument names. Blocking at GATE-31.
- **META-NMF (team-coordination.md, ALL)** — **No Manual Fix (inviolable).** Every fix flows through SOP update first, then agent dispatch. Lead included. No ad-hoc shortcuts.
- **ECON-DS2 explicit quality gate (evan)** — `git ls-files results/{pair_id}/signals_*.parquet` must return ≥1 file before handoff. Rule existed in prose; now a named checklist item.
- **GATE-29 parquet check (quincy)** — clean-checkout test extended to explicitly verify `signals_*.parquet` is committed. Missing = GATE-29 FAIL even when smoke_loader passes.

**Commits:** `bfb1b70` (APP-PT1), `a9ae669` (RES-NR1/GATE-NR), `dadd8f5` (ECON-DS2 gap), `e1cff0f` (Evan's signals parquet retro-fix).

---

## 2026-04-20 — Wave 10D: Cloud Verify Structural Enforcement (Multi-agent)

**Scope:** appdev-agent-sop.md + qa-agent-sop.md. Affects ace, quincy.

**Additions:**

- **AppDev Quality Gate extensions (ace)** — new checklist items: breadcrumb nav present on all 4 pages; Evidence page tab structure matches reference pair (Level 1 / Level 2); new pages MUST be derived from canonical reference template, not built from scratch; Signal Universe section renders non-empty.
- **GATE-28 structural parity (quincy)** — cloud DOM audit now asserts breadcrumb present (all 4 section labels in DOM) AND Evidence tabs contain "Level 1" or "Basic Analysis" text. Missing/wrong = GATE-28 FAIL.
- **QA-CL4 (quincy)** — named cloud verify gate (GATE-27 + GATE-28 + GATE-29). Previously ad-hoc Lead-owned; now Quincy-owned, evidence-gated.

**Commits:** `eb023f9` (fix + SOP tightening), `a815fde` (final cloud verify PASS).

---

## 2026-04-19 — HY-IG v2 Stakeholder Review Follow-Up: VIZ-V2 Revision + VIZ-V5 Added (Vera)

**Scope:** visualization-agent-sop.md + docs/standards.md. No other agent SOPs touched.

**Bug observed:** HY-IG v2 stakeholder review flagged two bugs the existing SOPs failed to prevent. (1) NBER recession shading at grey alpha 0.12 was imperceptible against the Streamlit off-white background; caption correctly disclosed shading but shading itself was invisible. (2) In the dual-panel hero chart (two x-axes: `xaxis`, `xaxis2`), the 3 shading rects had `xref='x'` only, so the bottom SPY panel had no shading at all. Both bugs cleared prior Quality Gates because the rule as written was wrong, not because it was unfollowed.

**Revised (VIZ-V2):**

- **Alpha + color prescription corrected.** Prior text "alpha 0.1–0.15, grey" replaced with "alpha 0.20–0.28, `rgba(150,120,120,0.22)` faded red-brown or equivalent — must be perceptible against the Streamlit background at standard zoom. Plain grey at alpha < 0.18 is prohibited."
- **Subplot handling clause added.** When `layout` contains multiple x-axes (`xaxis`, `xaxis2`, …), Vera must emit one shading shape per panel per recession; total shape count = n_recessions × n_panels.
- **Perceptual-validation step added.** After saving JSON, Vera renders chart to PNG via kaleido (`fig.write_image`) and visually confirms shading is perceptible. PNG saved as `_perceptual_check_{chart}.png` in the same plotly directory. Charts where shading cannot be seen at standard zoom fail **GATE-27 (End-to-End Chart Render Test)**.

**Added (VIZ-V5):**

- **End-to-End Chart Load Smoke Test.** Before handoff to Ace, Vera runs a smoke-test script per chart: (1) `plotly.io.read_json` loads without exception, (2) `len(fig.data) > 0`, (3) `fig.layout.title.text` non-empty. Log saved to `output/charts/{pair_id}/plotly/_smoke_test_{YYYYMMDD}.log`. Any failure blocks handoff.

**Retro-applied to HY-IG v2:** 4 charts updated (hero dual-panel → 6 shading shapes; 3 canonical zoom charts → stronger faded-red-brown alpha). Perceptual check PNGs and smoke test log produced per the new rule. Change recorded in `results/hy_ig_v2_spy/regression_note_20260419.md`.

**Rationale:** "Rule was followed; rule was wrong. Fix the rule." Both bugs were 100% preventable had VIZ-V2 carried (a) a perceptible alpha, (b) a subplot clause, and (c) a perceptual-validation step. V5 smoke test catches the orthogonal structural-integrity failure mode. Operationalizes the learning that quality gates must include a rendered-output check, not only spec-conformance checks.

---

## 2026-04-12 — Regression-Proofing Infrastructure (this session)

**Scope:** team-coordination.md + new docs/standards.md + new docs/sop-changelog.md. No changes to agent-specific SOPs.

**Added to team-coordination.md:**

- **META-PWQ / Portal-Wide Quality Checklist** — cross-cutting acceptance checklist applied to every pair. Covers Landing Page, Navigation, Story, Evidence, Strategy, Methodology pages, and cross-cutting items (dual notation, plain-English expanders, honest caveats, no silent regressions).
- **META-RPD / Reference Pair Doctrine** — HY-IG v2 (tag: hy-ig-v2-reference once approved) established as canonical reference pair. Every new pair dispatch begins with comparison; deviations require design_note.md.
- **META-PAC / Pair Acceptance Checklist** — new template for results/<pair_id>/acceptance.md with Portal-Wide Quality Checklist, Reference Pair Comparison, Regression Note, Stakeholder Review, Lead Sign-off sections.
- **GATE-23** — new gate row for Pair Acceptance.md (blocking); owner Lead Lesandro.

**Created:**

- **docs/standards.md** — canonical rule registry with stable IDs for every blocking rule across DATA, ECON, VIZ, RES, APP, GATE, and META prefixes.
- **docs/sop-changelog.md** — this file.

**Rationale:** Regression-proofs the SOP system. Future agent dispatches can cite rules by stable ID (GATE-23, META-RPD, APP-AF2, etc.) rather than quoting SOP prose. The Reference Pair Doctrine and Pair Acceptance Checklist together turn tribal knowledge about pair-quality decisions into mechanical artifacts that reviewers and future agents cannot miss.

---

## 2026-04-11 — EOD Checkpoint (commit 93ed4b2)

**Scope:** EOD checkpoint capturing SOP hardening Parts D+E + trade log UX in a single marker. No new rules, but consolidates the day session work.

**Referenced:**

- SOP hardening Part D (c5bf1a9)
- SOP hardening Part E (62c60e9)
- Trade log UX fix (8ef55c5)
- HY-IG v2 retroactive fixes (b6dd6a9)

---

## 2026-04-11 — Trade Log UX (commit 8ef55c5)

**Scope:** Econometrics + Research + AppDev SOPs.

**Added:**

- **ECON-C4 / Rule C4** — Dual Trade Log Output (Internal + Broker-Style). Winner trade log produced in both internal schema and broker-style CSV for downstream consumers.
- **RES-PA3** — How to Read the Trade Log subsection mandatory on Strategy page narrative.
- **APP-AF5** — Column Legend Requirement for Downloadable Artifacts. Every CSV download must have an adjacent column-legend expander.

**Rationale:** HY-IG (pair #5) shipped a header-only trade log; downstream users had no way to interpret columns. Fix makes the trade log self-describing at three layers: file (broker CSV), portal (expander), narrative (worked example).

---

## 2026-04-11 — HY-IG v2 Retroactive Fixes (commit b6dd6a9)

**Scope:** No new SOP rules. Applied the hardened SOPs retroactively to HY-IG v2 to close stakeholder-reported gaps. Retroactive fixes served as the integration test for the new rule set.

**Validated rules:** GATE-22 (method coverage no regression), RES-EP1 (8-element template), VIZ-A3 (canonical chart catalog), META-RNF (regression note format), APP-EP4 (chart filename contract).

---

## 2026-04-11 — SOP Hardening Part E (commit 62c60e9)

**Scope:** Stakeholder-driven + self-review + cross-review fixes across all SOPs.

**10 stakeholder-driven rules added:**

- **RES-EP1** — Evidence Page 8-Element Template (Why / How / Method / Graph / Observation / Interpretation / Caveats / Link-back).
- **RES-EP2** — chart_status field mandatory in each method block.
- **RES-EP3** — Missing-Element Fallback Protocol (escalate before dropping).
- **RES-EP4** — Drop Only With Regression Note.
- **APP-EP1..EP5** — Render-side rules for 8-element template, caption fallback chain, render-time completeness check, chart filename contract (3.9a), missing-element fallback (3.9b).
- **GATE-22** — Method coverage no-regression gate item.

**15 self-review rules added:**

- **DATA-D3** — Classification Decision Procedure (mandatory workflow).
- **RES-B5** — Strategy Objective Classification.
- **ECON-C3** — Producer-Side Rerun Regression Check (method and numeric diff).
- **VIZ-A4** — Chart Regression Report with Spec Diff section.
- **RES-5b** — Regression Prevention Recipe (filesystem diff).
- plus audience-friendly refinements across AppDev SOP §3.8.

**10 cross-review fixes:**

- META-EOI expanded to cover prior-pair-version deviations and unit/scale conventions.
- META-UNK formalized: unknown classification is an error signal, not a fallback label.
- META-CFO formalized classification field ownership (Dana owns nature/type; Ray owns objective).
- VIZ-A2 + RES-4 cross-referenced for dual-notation consistency.
- GATE-19/20/21 ownership explicitly named on gate rows.

---

## 2026-04-10 — SOP Hardening Part D (commit c5bf1a9)

**Scope:** classification schema, 8-element template intro, landing page filters.

**Added:**

- **DATA-D3 / Classification Decision Procedure (first version)** — mandatory workflow for indicator_nature and indicator_type.
- **DATA-D2 / Default Unit Convention Registry** — canonical units per column suffix; rules for one unit per canonical name.
- **RES-IT1** — Indicator Type Classification in research brief with controlled vocabulary.
- **APP-LP1..LP7** — Landing Page Design Rules (executive summary, multi-dimensional filters, card numbering, performance badges, classification chips, metadata source, filter behavior for Unknown).
- **META-TWJ** — Tournament Winner JSON Schema formalized.

**Rationale:** Portal landing page needed filterable classification. Classification became the linchpin coordinating Dana, Ray, Evan, Vera, Ace.

---

## 2026-04-10 — HY-IG v2 Narrative Rewrite (commit d9aeaff)

**Scope:** No new rules. First full exercise of the audience-friendly rules on an existing pair.

**Validated:** RES-1, RES-2, RES-3, RES-4, APP-AF1..AF5.

---

## 2026-04-09 — Audience-Friendliness Rules (commit 61efe7d)

**Scope:** Research + AppDev SOPs.

**Added:**

- **RES-1** — Audience Assumption (write for layperson who knows markets).
- **RES-2** — Translation Bridge (plain-English on first use).
- **RES-3** — Method Justification (Why we chose this method sentence).
- **RES-4** — Unit Discipline — Inline Dual Notation (bps and percent on first use).
- **RES-6** — Glossary Quality Rubric (4-element standard).
- **APP-AF1** — Expander Philosophy: Defer Do not Expand.
- **APP-AF2** — Rule-First Strategy Cards.
- **APP-AF3** — Metric Interpretation Rule (interpretation caption on every KPI).
- **APP-AF4** — Translation Bridge Rendering.

**Rationale:** Stakeholder feedback that portal was too quant-dense for intended audience. Ray now assumes layperson; Ace renders with progressive disclosure.

---

## 2026-04-09 — Chart Rendering Fix (commit 8767a8a)

**Scope:** AppDev + Visualization contract.

**Added:**

- **APP-EP4 / Chart Filename Contract (Rule 3.9a)** — loader uses canonical filename only; no fallback to alternate filenames.
- **VIZ-NM1** — pair_id appears ONLY in directory path, NEVER in filename.

**Rationale:** Filename mismatch between Vera outputs and Ace loader was the single most common portal bug. Rule removes silent fallback behavior.

---

## 2026-04-08 — HY-IG v2 Full Pipeline Test (commit b009674)

**Scope:** No new rules. Full multi-agent pipeline test of hardened SOPs.

**Validated:** META-PSC (pipeline self-containment), ECON-DS1 (derived signal persistence), RES-EP1 (8-element template), VIZ-A3 (standard chart catalog).

---

## 2026-04-07 — SOP Hardening Core (commit 6cb5b4c)

**Scope:** Team coordination + Econometrics + AppDev + Research SOPs.

**Added:**

- **META-PSC / Pipeline Self-Containment Contract** — every pair has single self-contained pipeline script producing ALL downstream artifacts.
- **ECON-DS1 / Derived Signal Persistence Rule** — HMM probs, Markov states, z-scores, composites persisted to results/{id}/signals_{date}.parquet.
- **APP-RP1** — Rendering Patterns for Presentation Quality (st.container(border=True), no nested HTML, no markdown inside HTML wrappers).
- **RES-PA2** — Presentation Quality Patterns (skeptical reader framing, progressive disclosure, honest caveats).

**Rationale:** HY-IG (pair #5) required 3 separate scripts in specific sequence. HMM probability signal computed inside tournament but never persisted. Fragmented pipelines created invisible dependencies.

---

## 2026-03-20 — Deliverables Completeness Gate (commit a8ca9f6)

**Scope:** team-coordination.md.

**Added:**

- **GATE-1..GATE-18** — Deliverables Completeness Gate Step 8 with 18 gate items across analysis brief, dataset, stationarity, interpretation metadata, exploratory results, core models, tournament, charts, portal pages, navigation, catalog status, winner summary/trade log/execution notes.
- **META-MRA / MRA Mandatory** — Measure, Review, Adjust step after browser verification.
- **META-BV / Browser Verification Mandatory** — Playwright headless inspection after every portal change.
- **META-VF / Variant Families** — sharing pages across variants acceptable; omitting page type not.

**Rationale:** Pair #2 (TED Variants) shipped without Methodology page because no one verified all 4 pages existed. Browser verification checked rendering, not completeness.

---

## 2026-03-14 — Multi-Indicator Enhancement Framework (commit c367347)

**Scope:** All 6 SOPs.

**Added:**

- **ECON-C1 / Category-Specific Mandatory Method Catalog** — every indicator_type routes to a mandatory method list.
- **ECON-C2 / Mandatory Output Schema Per Method** — exact column schema for each mandatory method.
- **META-P0 / Phase 0: Analysis Brief Gate** — no agent starts work without approved brief.
- **ECON-T1 / Tournament Design Parameters** — target-class-aware tournament parameters.
- **ECON-T2 / Target-Class-Aware Backtest Parameters** — backtest parameters match target class.
- **RES-MS1 / Multi-Indicator Scaling** — tiered literature review, batch spec memos, canonical glossary, master event database.
- **RES-MS2 / Batch Direction Annotation Delivery** — direction annotations batched across pairs.
- **DATA-B1 / DATA-B2** — batch data availability pre-check and shared indicator deduplication.

**Rationale:** Scaling the team from single-pair analysis to 73-pair portfolio required framework generalization. Econometric catalog expanded 52 to 95 methods with 6 new categories and Relevance Matrix; data series catalog added 31 indicators and 35 targets.

---

## 2026-03-14 — Cross-Review Update (commit 9364b2c)

**Scope:** All 5 agent SOPs.

**Added (via self-update after cross-review):**

- **META-NO / New Agent Onboarding Protocol** — cross-review SOPs, self-update, distill lessons.
- **META-TCH1 / META-TCH2** — Task Completion Hooks (Validation/Verification and Reflection/Memory).
- **META-HO / META-ACK** — Handoff Protocol and Acknowledgment Protocol (silence is never acceptance).

**Rationale:** Cross-review surfaced handoff gaps that solo work missed.

---

## 2026-03-01 — HY-IG Initial Analysis (commit e2a4c65)

**Scope:** No SOP changes. First end-to-end pair.

**Surfaced issues later fixed:** HMM state inversion (commit 2c9368d), pipeline fragmentation (later META-PSC), header-only trade log (later ECON-C4).

---

## 2026-02-28 — Defensive Rules (commits 22ac0bf, efccb3b)

**Scope:** All agent SOPs.

**Added:**

- **META-D1 / Defense 1: Self-Describing Artifacts** — producer rule: meaningful column names, units, sign conventions, boundaries, sidecar manifest.
- **META-D2 / Defense 2: Reconciliation at Every Boundary** — consumer + reviewer rule: known-fact sanity checks, derived-quantity cross-check, automated reconciliation script.

**Rationale:** Prevent implicit-assumption errors at every agent boundary. HMM state inversion was the archetypal failure mode.

---

## 2026-02-15 — Visualization Integrity Rules (commit series)

**Scope:** Visualization SOP.

**Added:**

- **VIZ-A1** — No Inverted Axes on Financial Dashboards.
- **VIZ-A2** — Unit Discipline: Axis Labels Must Match Data Values.
- **VIZ-A3** — Standard Chart Catalog with Canonical Signal Selection.
- **VIZ-A5** — Caption Ownership (Ray displays, Vera audits).
- **VIZ-CP1** — Color Palette Mandatory (colorblind-friendly, consistent).
- **VIZ-CS1** — Standard Chart Set Per Pair (canonical 10-chart set).

**Rationale:** Consistent chart specifications across pairs. Canonical chart catalog prevents ad-hoc rerun drift.

---

## 2026-02-01 — App Dev Integration (commit 04c8f67, e9c6467)

**Scope:** New AppDev SOP + cross-review round 2.

**Added:**

- **APP-PA1 / APP-SF1 / APP-DA1 / APP-SP1** — Portal Architecture, Storytelling Flow, Direction Annotation, Strategy Execution Panel standards.
- **META-IA / Interpretation Annotation Handoffs** — four-agent protocol for same-indicator / different-target direction differences.

**Rationale:** Streamlit portal became canonical delivery surface.

---

## 2026-01-20 — Research Catalogs (commits 155204b, ef5b83b)

**Scope:** docs/ reference catalogs.

**Created:**

- data-series-catalog.md
- econometric-methods-catalog.md
- backtesting-approaches-catalog.md
- threshold-regime-methods-catalog.md
- reference-catalogs-index.md (with Run Registry — META-REG)

**Rationale:** Standing references that all agents consult.

---

## 2026-01-10 — Initial SOP Foundation (commits 10f4b0a, 652d1b5, 1156869)

**Scope:** First agent SOP set.

**Created:**

- data-agent-sop.md (Data Dana)
- econometrics-agent-sop.md (Econ Evan)
- visualization-agent-sop.md (Viz Vera) — early Rules A1/A2 form
- research-agent-sop.md (Research Ray)
- team-coordination.md — early handoff specifications, escalation rules

**Foundational rules established:**

- **DATA-DD1** — Data Dictionary (Display Name, Direction Convention, Effective Start, Unit, SA status, known quirks).
- **DATA-DD3** — Stationarity Test Delivery (ADF/KPSS/PP).
- **DATA-H1..H3** — handoff specifications.
- **ECON-SS1 / ECON-ES1 / ECON-DG1 / ECON-SA1** — Model Specification, Estimation Standards (HC3 default), Diagnostics Mandatory, Sensitivity Analysis.
- **RES-B1** — Two-Stage Delivery Protocol (spec memo + full brief).
- **META-CR** — Communication Rules (7-point).
- **META-ER** — Escalation Rules.
- **META-QS** — Quality Standards (team-wide).

---

## Appendix: Rule-to-Commit Cross-Reference

For rules whose source commit predates this changelog or is distributed across multiple commits, see git log and the originating SOP section. This changelog captures rule IDs going forward; earlier rules are registered in standards.md with their current SOP section as source.

## Appendix: How to Add an Entry

1. Identify the SOP(s) being changed.
2. Name each new or modified rule by ID (if new, pick an ID that fits the prefix scheme in standards.md).
3. Write a one-paragraph summary per rule: what changed, why, and what upstream evidence (commit, bug, stakeholder feedback) drove it.
4. Commit the SOP change, standards.md update, and this changelog entry together.
5. Entries are newest-first.
