# Release Notes

## 2026-04-24 — Wave 10J/10K: META-CPD Discipline + Self-Reflection Round — **COMPLETE**

**Final verify: 60/60 PASS** (Quincy `3086bb7`). Wave 10J closes with all agents having completed a structured self-reflection round and the META-CPD (Commit-Push Discipline) rule propagated to all five agent SOPs.

### What changed

**New rule: META-CPD — Commit-Push Discipline** (added to `docs/agent-sops/team-coordination.md` and all 5 agent SOPs)
- Every `git commit` MUST be immediately followed by `git push origin main` within the same turn.
- No deferred pushes. No "push at EOD" accumulation.
- Motivation: agents were committing silently without pushing; downstream agents and cloud deploys operated on stale HEAD.

**Self-reflection round (all 5 agents):**
Each agent authored a structured reflection covering: what went well, what fell short, lesson retention, cross-agent friction, open debates, and key lessons to carry forward. Highlights:
- **Dana:** DATA-D12 linter script is a persistent dead letter (rule without enforcement). Cross-review findings not converted to BL entries — escalation discipline gap.
- **Evan:** ECON-UD "optional for non-reference pairs" was a process debt. Direction reconciliation (ECON-DIR1) now mandatory. Added `indicator_category` field to all 10 `interpretation_metadata.json` files (rates / production / sentiment / credit / volatility); reran `subperiod_sharpe` for 5 reclassified pairs using correct episode sets per Ray's domain verdicts. META-CPD cross-reference added to econometrics SOP (commit `57e53b5`).
- **Ray:** RES-17 was a TODO block that lived too long. RES-OD1 direction reconciliation gate added.
- **Vera:** VIZ-HZE1 retro-apply forced. ACE-HZE1 triggered by gap in three-agent chart chain.
- **Ace:** ACE-HZE1 authored — `HISTORY_ZOOM_EPISODES` must be populated whenever upstream data exists; silent omission prohibited.

### HZE1 retro-apply (Vera + Ray + Ace)

- Vera: `history_zoom` charts generated for 8 pairs (29 charts + 31 sidecars, commit `20669d9`)
- Ray: `HISTORY_ZOOM_EPISODES` narratives authored for 8 pairs (commit `00f27d9`); episode registry designed and implemented (`docs/schemas/episode_registry.json`); pair reclassification confirmed — `dff_ted_spy`/`sofr_ted_spy` → rates, `ted_spliced_spy` → credit. RES-20 triad verified across all 8 pairs.
- Ace: `HISTORY_ZOOM_EPISODES` wired into 8 pair configs (`816444f`)
- Exception: `vix_vix3m_spy` dot_com episode skipped per VIZ-HZE1 rationale; `_meta.json` documents decision (`2f15547`)

### Commits (chronological)

`20669d9` Vera HZE1 retro-apply (8 pairs) · `816444f` Ace HZE1 config wire-up · `2f15547` Vera vix dot_com skip · `d99e7da` Ace note for dot_com omission · `3086bb7` Quincy 60/60 wave verify · SOP commits: `da8f534` (Vera) · `d013b08` (Dana) · `00f27d9` (Ray) · `57e53b5` (Evan) · `66b58d3` (Ace)

### Lessons

- **A rule without an enforcement script is debt.** DATA-D12 (column-suffix canon) had no linter; manually applied once, silently violated thereafter. Author the tool in the same commit as the rule.
- **Three-agent chains need a closing rule.** Ray provides frontmatter → Vera generates charts → Ace populates config. Without ACE-HZE1, the last link was advisory. Silent omission propagated to 8 pairs with no error.
- **Cross-review findings are backlog candidates, not observations.** Dana found the HZE1 gap in Wave 10F cross-review and logged it as a finding, not a BL entry. Ray backfilled reactively after Quincy's cloud-verify failures.

---

## 2026-04-23 — Wave 10I.C: Quality Gate Overhaul + Portal Error Elimination — **COMPLETE**

**Final verify: 41/41 PASS** (Quincy `0cedde6`). User inspection triggered a comprehensive adversarial DOM audit that exposed 20 visible failures across 9 classes — all invisible to the prior structural verify. Wave 10I.C resolves every failure class and rebuilds the quality gate from the ground up.

### What users see now

All 10 pairs × 4 pages render without red banners, stub text, wrong numbers, or tracebacks. Probability Engine Panel active on all Strategy pages. Direction triangulation now 3-way (Evan + Dana + Ray). Landing card Max DD correct for all pairs. Sidebar shows accurate pair count.

### Failures resolved

| Class | Pairs affected | Root cause | Fix |
|-------|---------------|------------|-----|
| Missing signals parquet | 6 legacy pairs (Strategy) | Never generated post-migration | Evan `625a86e`: regenerated from existing data parquets |
| Python traceback (threshold_value None) | indpro_spy, vix_vix3m_spy | Wrong file patched in Wave 10I.A | Ace `fb101e5`: fixed `probability_engine_panel.py` |
| Signal magnitude sanity check rejection | umcsent_xlv + 4 TED/permit pairs | ±20 bound designed for z-scores, applied to all | Ace `fb101e5`: check restricted to z-score columns |
| Direction disagreement banners (APP-DIR1) | indpro_spy, vix_vix3m_spy, sofr_ted_spy, dff_ted_spy | `observed_direction` not reconciled vs tournament winner | Ray `e0a342d`: 4 files corrected |
| "Ray leg pending" stub on all Strategy pages | All 10 pairs | RES-17 frontmatter migration never implemented in code | Ray `f8fa75d`: 3-way direction_check live |
| Max DD wrong scale (-0.1% instead of -8.5%) | hy_ig_spy, umcsent_xlv | Hardcoded pair-name scaling logic | Ace `27fb460`: auto-detect from data shape |
| "vs N/A buy-and-hold" KPI | 8 pairs Story | bh_sharpe/bh_max_drawdown absent from legacy winner_summary | Ace `27fb460`: backfill from tournament CSV on load |
| Signal universe unavailable (Methodology) | 6 legacy pairs | ECON-UD classified optional for non-reference pairs | Evan `86d13f7`: all 6 signal_scope.json produced |
| Stationarity tests missing (Methodology) | 3 TED pairs | Pipeline printed to stdout, never saved CSV | Evan `86d13f7`: ADF+KPSS CSVs saved for all 3 |
| Sidebar "6 of 73" stale count | All pages | Hardcoded, never updated as pairs were added | Ace `27fb460`: updated to 10 |

### New quality gate standard

**Quincy `0c2b92a` — verify script upgraded:**
- `APP_SEV1_PATS`: catches user-visible soft-error banners ("cannot render", "No signals_", etc.) — not just Python exception class names
- `STUB_PATS`: catches placeholder text ("vs N/A", "Ray leg pending", "TODO", "Signal universe unavailable")
- `gate29_parquet_preflight()`: checks `git ls-files results/{pair_id}/signals_*.parquet` before browser opens — hard FAIL if missing
- Screenshot-all-tabs workflow: default state + every tab state captured per page; `index.md` shared evidence package for all agents

**HABIT-QA1 (new binding SOP rule):** after every verify run, Quincy reads ≥3 Strategy-page DOM text files and writes a one-sentence sign-off in session-notes. Script PASS is necessary but not sufficient.

### Process reform: agents own their own failures

Each agent diagnosed their own gap from the audit evidence — Lead did not hand them the analysis:
- **Quincy**: found that DOM evidence was on disk but never read; script treated as ceiling not floor
- **Ace**: found 6 failures in her own code; committed to content audit before every handoff; no more hardcoded pair names in scaling logic
- **Evan**: found ECON-UD was "optional" for non-reference pairs; pipeline printed instead of saved; ECON-UD now blocking for all pairs; ECON-DIR1 direction reconciliation gate added
- **Ray**: found RES-17 implementation was a TODO block that was never completed; committed to cross-checking `observed_direction` against tournament ground truth after every write (RES-OD1)

### SOP rules added this wave

- **HABIT-QA1** (Quincy): DOM text read + sign-off mandatory after every verify run
- **ECON-UD** (Evan): signal_scope.json blocking for ALL pairs, not reference pairs only
- **ECON-DIR1** (Evan): direction reconciliation gate — cross-check `observed_direction` vs `winner_summary.direction` before handoff
- **RES-OD1** (Ray): after any write to `interpretation_metadata.json`, assert `observed_direction == winner_summary.direction` before committing
- **GATE-CL1-5** (Ace): content audit gates — N/A slots, stub text, sidebar count, label maps, scaling logic all checked before handoff
- **Pattern 24** (Quincy): traceback line vs HEAD mismatch → suspect stale Cloud deploy, escalate for reboot before more patches

### Lessons

- **The verify script was the ceiling, not the floor.** Every agent treated passing an automated check as done. The right habit: automated checks gather evidence; human judgment closes the loop.
- **"Preserve verbatim" is not safe for derived fields.** Ray's backfill preserved `observed_direction` without checking it against Evan's tournament output. Derived assertions must be reconciled, not just preserved.
- **Print ≠ save.** Evan's stationarity pipeline wrote results to stdout. Three Methodology pages had no artifact. Any pipeline output that feeds a rendered page must be saved to disk and `os.path.exists()` asserted before advancing.
- **One screenshot once, shared.** 116 screenshots from a single Playwright run replaced five separate agent browser sessions. Token-efficient and consistent — all agents inspect the same evidence.

### Commits (chronological)

`d925db9` Quincy adversarial audit · `0c2b92a` Quincy script upgrade + HABIT-QA1 · `e0a342d` Ray direction fixes · `27fb460` Ace 6 display fixes · `86d13f7` Evan signal_scope + stationarity · `625a86e` Evan signals parquets · `6bf0956` Quincy screenshot-all-tabs verify · `fb101e5` Ace traceback + sanity check · `f8fa75d` Ray RES-17 3-way direction · `0cedde6` Quincy 41/41 final verify · `e8e5b8c` Ace APP-PR1 path confirmation

---

## 2026-04-23 — Wave 10I.A: Legacy-Page Migration + Schema-Drift Backfill — **COMPLETE**

**Final verify: 41/41 PASS on cloud** (Quincy commit `e11dc20`). Wave 10I.A migrates 6 legacy hand-written pages (`indpro_spy`, `permit_spy`, `vix_vix3m_spy`, `sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`) onto the APP-PT1 template and resolves three layered schema-drift defects that surfaced on the Strategy render path. APP-PR1 path-resolution discipline codified as prophylactic SOP before the migration.

### What users see now

All 10 active pair cards on the landing page route to template-based Story / Evidence / Strategy / Methodology pages. The 6 legacy TED/INDPRO/PERMIT/VIX pairs now carry the same Strategy-page surface as the Wave 10H.2 template set — probability engine panel, position adjustment panel, instructional trigger cards, APP-TL1 Trade Log block (where broker CSV exists, L2 banner where it doesn't). No crashes. No broken breadcrumbs. Regression gate: Sample + 4 prior-template pairs still 17/17 identical.

### New rule

**APP-PR1 — Path Resolution Discipline** (`docs/agent-sops/appdev-agent-sop.md`). Binding: every file read under `app/components/**` and `app/pages/**` MUST resolve via `_REPO_ROOT = Path(__file__).resolve().parents[N]`. Bare-relative reads prohibited. Rule is prophylactic; zero violations in current code. Becomes mandatory for all future legacy-page migrations.

### Key commits (chronological)

| Commit | Author | Content |
|--------|--------|---------|
| (prior) | Lead | APP-PR1 SOP authored; 7 legacy pages migrated to template via Ace/Ray dispatches |
| `08bb0c8` | Quincy | First cloud verify — 35/41 PASS, 6 Strategy FAIL (threshold_value `None` crash) |
| `5f2e50d` | Ace | Defensive-coerce `threshold_value` in `instructional_trigger_cards.py` (APP-SEV1 L2) |
| `2fa6c95` | Evan | Relax `winner_summary.schema` to tolerate `threshold_value: null` |
| `ccb0d5f` | Ace | Widen defensive coerce — root-cause diagnosis: 10-error schema failure upstream |
| `a5952e2` | Evan | Backfill 6 legacy `winner_summary.json` to v1.1.0 (9 missing fields + enum fixes + percent→ratio) |
| `9e30a8c` | Quincy | Reverify #1 — still 35/6; new failure class surfaced (`interpretation_metadata.json` drift) |
| `8fc4270` | Ray | Backfill 6 legacy `interpretation_metadata.json` to v1.0.0 (`pair_id`, `schema_version`, `owner_writes`, `last_updated_*`, enum fixes) |
| `6335674` | Quincy | Reverify #2 — still 35/6; diagnosed Cloud-bundle staleness (traceback pointed at comment line) |
| `e11dc20` | Quincy | Reverify #3 after Lead reboot — **41/41 PASS**, closure-ready |
| `<this>` | Lead | Closure: relnotes + sop-changelog |

### Lessons

- **Three-layer schema drift is a single class, not three bugs.** The Strategy page fails on `winner_summary.json` → consumer coerce → `interpretation_metadata.json` → Cloud bundle staleness, in that order. Each fix surfaced the next latent defect. The underlying class: **legacy artifacts co-evolved with their hand-written page consumers; template consumers impose stricter uniform validation the legacy data was never checked against.** Wave 10I's migration is the only realistic audit gate — propose `BL-LEGACY-MIGRATION-AUDIT-GATE` (Quincy handoff) to front-load all producer-side schema validation on any future migration wave.
- **Traceback vs HEAD line-number check caught the stale deploy.** Quincy's reverify #2 noticed the exception traceback pointed at `instructional_trigger_cards.py:385` but HEAD at that line was a comment. That's only possible if Cloud is running a pre-fix bundle. Escalated for manual reboot; reverify #3 immediately green. Codify as Pattern 24 in `qa-agent-sop.md` — *when cloud traceback line disagrees with HEAD source, suspect stale deploy before further code patches.*
- **Artifact-only commits may not trigger Cloud redeploy.** Evan's and Ray's backfill commits touched only `results/*.json` and did not rebundle the Python app. Ace's earlier `ccb0d5f` code-change commit appears to have been missed by the auto-deploy as well (reason unknown). Lead's manual reboot was the only way to pick up the new bundle. Flag as `BL-CLOUD-REDEPLOY-TRIGGER` for investigation.
- **META-NMF and LEAD-DL1 held across a 6-commit chase.** Every fix landed via the responsible agent (Evan → schema + data; Ray → narrative metadata; Ace → consumer coerce; Quincy → verify). Lead wrote zero agent-owned files across the wave. Backfills were framed as "recoverable from existing artifacts without tournament rerun" — no hot-patches, no synthesized data.
- **Judgment calls to carry forward:** `signal_column` values are synthesized snake_case (reconcile on producer rerun); `threshold_rule` inferred from direction+percentile (legacy never recorded comparator); `oos_period_start/end` reconstructed from defaults (log `BL-OOS-SPLIT-LEGACY`); `threshold_value` left null on all 6 (Ace's Defense-2 handles downstream).

### Backlog opened / proposed

- `BL-LEGACY-MIGRATION-AUDIT-GATE` (Quincy) — strict jsonschema.validate sweep across all pair artifacts as a mandatory pre-cloud-verify step on any migration wave.
- `BL-CLOUD-REDEPLOY-TRIGGER` (Lead) — investigate why artifact-only commits (and ccb0d5f) didn't trigger Streamlit Cloud auto-redeploy; codify reboot-required rule.
- `BL-OOS-SPLIT-LEGACY` (Evan) — emit `oos_split_record.json` on future tournament reruns for the 6 backfilled pairs.
- `BL-SIGNAL-COLUMN-RECONCILE` (Evan/Dana) — synthesized `signal_column` values on 6 pairs should reconcile with actual signals parquet when producer reruns.
- Prior open items unchanged: BL-APP-PT1-LEGACY, BL-APP-PT1-UMCSENT, BL-BROKER-CSV-LEGACY, BL-CHART-GAPS-LEGACY, BL-VIZ-O1-LEGACY, BL-VIZ-SIDECAR-HELPER, BL-DATA-DICT-APPTL1, BL-COMMISSION-BASIS, BL-THRESHOLD-VALUE-SCHEMA (superseded by closed BL-LEGACY-WINNER-SUMMARY-SHAPE).

### Next

Wave 10I.B (Sample migration) — decommission `hy_ig_v2_spy`'s hand-written Strategy page onto the APP-PT1 template. Expected to surface more legacy-artifact drift on the reference pair itself.

---

## 2026-04-23 — Wave 10H.2: APP-TL1 Trade Log Rendering Contract — **COMPLETE**

**Final verify: 17/17 PASS on cloud** (Quincy commit `8e743ce`). Wave 10H.2 closes the Trade Log regression surfaced by user after Wave 10H.1: template-based pairs (`hy_ig_spy`, `indpro_xlp`) now render a Strategy-page Trading History block at parity with Sample (`hy_ig_v2_spy`) — dual downloads, five-element narrative scaffold, column dictionary, always-visible preview.

### New rule

**APP-TL1 — Trade Log Rendering Contract** (`docs/agent-sops/appdev-agent-sop.md`). Binding: `render_strategy_page()` must invoke `_render_trade_log_block(pair_id, config)` helper producing dual CSV downloads (broker-style + researcher position log), narrative scaffold (heading → simulated-vs-real disclosure → two-file explanation → column glossary → pair-specific example), `#### Download Trading History` sub-heading, column-dictionary expander (10-row Column/Type/Meaning/Example), two-column download layout with row-count captions, always-visible 10-row preview. APP-SEV1-aligned: both missing = L1 short-circuit; one missing = L2 degraded; malformed = L2 warning + healthy-pane; missing pair example = L3 caption coda. Ownership split: Ace (structure), Ray (narrative defaults + `TRADE_LOG_EXAMPLE_MD` anchor), Evan (broker-style CSV), Dana (schema doc), Quincy (QA gate).

### What users see now

On `hy_ig_spy` and `indpro_xlp` Strategy page → Performance tab:
- Heading `### How to Read the Trade Log` followed by compliance-explicit simulated-trade disclosure (Ray canonical copy, not real broker executions).
- Two-file model explanation (broker-style vs researcher position log).
- `Key columns` bulleted glossary of the 10 APP-TL1 canonical columns.
- Pair-specific concrete example in bordered container — e.g. hy_ig_spy: COVID 2020-02-24 HMM stress prob 0.09→1.00 SELL at SPY $294.65 (`trade_id=282` in the broker-style log).
- `#### Download Trading History` sub-heading.
- "How to read this chart" expander with full 10-row column dictionary.
- Two download buttons: left primary `Download trade log (broker-style)` with row-count caption; right secondary `Download position log (researcher)`.
- Always-visible 10-row preview of broker-style log.

Previously: a single generic `st.download_button` with no prose.

### Commits

| Commit | Author | Content |
|--------|--------|---------|
| `3d6f096` | Ace | Discovery report: Sample-vs-template delta + spec proposal |
| `7364585` | Lead | APP-TL1 SOP authorship + sop-changelog entry |
| `a32eaff` | Ace | Structural skeleton: `_render_trade_log_block` helper + `StrategyConfig` fields + TODO-Ray narrative stubs |
| `2c11046` | Evan | Shared `scripts/_trade_log_broker.py` helper + broker-style CSV for `indpro_xlp` + `umcsent_xlv` |
| `76b6e06` | Lead | Backlog: BL-DATA-DICT-APPTL1, BL-COMMISSION-BASIS |
| `fc17274` | Ray | Narrative canonical defaults (4 constants) + `TRADE_LOG_EXAMPLE_MD` for `hy_ig_spy`, `indpro_xlp` |
| `ed1f484` | Lead | Backlog: BL-APP-PT1-UMCSENT |
| `2574d83` | Evan | Regenerate `hy_ig_spy` broker-style CSV to 10-col APP-TL1 schema (was 12-col legacy) |
| `8e743ce` | Quincy | Cloud verify + APP-TL1 DOM markers + Pattern 23 discovery |
| `<this>` | Lead | Closure: relnotes + sop-changelog + Pattern 23 codification + tag |

### Lessons

- **Inverted legacy risk class.** BL-APP-PT1-LEGACY catalogued "legacy pages bypass the template." Wave 10H.2 surfaced the mirror: "reference implementation is richer than the template." Every rule addition risks this asymmetry. Mitigation: at wave closure, Lead audits the reference pair's layer against the template output; if Sample has prose or structure the template lacks, log a BL item.
- **Pattern 23 — hidden `st.tabs` content is invisible to `inner_text`.** Quincy's first pass false-FAILed the APP-TL1 markers because the Trade Log lives in the "Performance" tab while the default-active tab is "Execute." Fix: use `frame.content()` HTML for tab-gated markers; retain `inner_text` for unconditionally-visible surfaces. Codified in `qa-agent-sop.md` alongside Pattern 22.
- **Schema audits must actually read the file.** Evan's §6 of his first handoff claimed `hy_ig_spy` broker CSV was "already compliant." Ray's narrative pass caught a 12-col-vs-10-col mismatch by actually running `pd.read_csv(comment="#")`. Evan captured the lesson in his PWS: compliance audits must check the column list with a parser, not eyeball. Applies to every future schema-compliance check — don't trust "looks right."
- **Lead self-audit held again.** 4 Lead commits this wave (`7364585`, `76b6e06`, `ed1f484`, closure). All in `docs/`. Zero agent-owned file writes. LEAD-DL1 mechanism continues to hold.
- **Shared helper hoisting pays off.** Evan consolidated broker-style logic into `scripts/_trade_log_broker.py` at first use (two new pairs). When a third pair needed regeneration (`hy_ig_spy`), the helper didn't fit its trade-pair format — so Evan wrote a one-off converter in `temp/` rather than bending the shared helper. Correct judgment: preserve the helper for the common path; handle the outlier with a local script.

### Backlog opened / updated

- `BL-APP-PT1-UMCSENT` — `umcsent_xlv` Strategy page is hand-rolled, bypasses template. Narrow subset of `BL-APP-PT1-LEGACY`.
- `BL-DATA-DICT-APPTL1` — per-pair data dictionaries for APP-TL1 schema (Dana, non-blocking).
- `BL-COMMISSION-BASIS` — `commission_bps` field on `winner_summary.json` (latent display-lie class; Evan audit).
- Plus the Wave 10H.1 backlog (BL-VIZ-O1-LEGACY, BL-VIZ-SIDECAR-HELPER, BL-APP-PR1, BL-APP-PT1-LEGACY) still open.

---

## 2026-04-23 — Wave 10H.1: Chart Governance Framework (Implementation) — **COMPLETE**

**Final verify: 17/17 PASS on cloud** (Quincy commit `aca5602`). Wave 10H.1 implements the rules shipped as paper SOPs in Wave 10H — chart disposition, exploration-zone, Methodology-page Exploratory Insights, Pattern 22 verify fix — across Ace's template, Vera's sidecars, and Quincy's verify tooling.

### New features / artifacts shipped

**Methodology page — Exploratory Insights section (APP-PT2):**
- New `_render_exploratory_insights(pair_id)` helper in `app/components/page_templates.py` wired into `render_methodology_page()` section 13b. Reads `results/{pair_id}/analyst_suggestions.json` → `exploratory_charts` list, renders each with ELI5 "What this shows" caption (`narrative_alignment_note`) + italic analyst note (`vera_rationale`) + feedback invitation. Silent skip when the key is absent (backward-compatible for pre-Wave-10H pairs).
- Sample pair (`hy_ig_v2_spy`): 3 orphan charts (`hero_spread_vs_spy`, `spread_history_annotated`, `tournament_sharpe_dist`) promoted from silent-void to Exploratory Insights, each with ELI5 + rationale authored by Vera.

**Chart disposition mandate (VIZ-O1) + Exploration zone (VIZ-E1):**
- Idempotent backfill script `scripts/backfill_chart_dispositions.py` stamped `disposition` on all 65 existing sidecars across 4 active pairs (62 `consumed`, 3 `suggested`).
- Generator updates on 3 pair-generator scripts so future runs emit the field by default.
- Chart generators that currently bypass the shared sidecar path (4 pairs) flagged to `BL-VIZ-SIDECAR-HELPER` for a future hygiene wave.

**Cloud verify — Pattern 22 fix + APP-PT2 check:**
- `scripts/cloud_verify.py` promoted from `temp/` to canonical location. DOM-tree `query_selector_all(".js-plotly-plot")` replaces the `inner_text.count()` pattern that always returned 0. Iframe resolution switched from `page.frames` iteration (raced Streamlit's frame registration) to `wait_for_selector('iframe[title="streamlitApp"]').content_frame()`. 60s goto + 45s body-hydrate + 20s chart-stability polls.
- New APP-PT2 render check: Sample Methodology must contain "Exploratory Insights" section + 3 unique ELI5 markers; other pairs' Methodology pages must NOT (regression gate).
- QA-CL2 P2 exception applied to continuous-rebalancing strategies.

**Bug fixes discovered during rollout:**
- Landing page raw-column leak (`spy_fwd_21d`/`63d` tokens from `interpretation_metadata.key_finding`). Fixed by new `humanize_column_tokens()` helper in `app/components/pair_registry.py` routed through the existing APP-RL1 single-source map; display layer wrapped in `app/app.py`.
- APP-PT2 section absent on Sample Methodology despite correct template wiring. Root cause: `app/pages/9_hy_ig_v2_spy_methodology.py` is a hand-written legacy page that bypasses `render_methodology_page()`. 5 other Methodology pages share the same pattern. Fix: direct `_render_exploratory_insights(PAIR_ID)` call added to the Sample page. The broader legacy-page migration is tracked as `BL-APP-PT1-LEGACY`.

### Governance / discipline shipped mid-wave

**Wave 10H.0 — LEAD-DL1 (Lead Delegation Discipline):** new dedicated Lead SOP `docs/agent-sops/lead-agent-sop.md` with pre-edit gate, File Ownership Map covering all 6 agents + shared-key files (`analyst_suggestions.json`, `pair_config.py`), narrow exceptions, wave-closure self-audit via `git diff --stat` against the Ownership Map. Triggered by a self-caught drift earlier in Wave 10H.1 where Lead did Ace+Vera+Quincy work across 70+ files; user reverted and asked for a durable mechanism. Rule loaded at every SOD via `lead_delegation_discipline.md` auto-memory.

**Permissions syntax fix (`b3facc8`):** single-slash absolute paths in `.claude/settings.json` (`Write(/home/vscode/.claude/agents/**)`) were being interpreted as project-relative per Claude Code docs, causing subagents to hit sandbox denial on global-profile writes (all 3 Wave 10H.1 dispatches affected). Converted to double-slash (`Write(//home/vscode/.claude/agents/**)`). Validated twice — Quincy's 3rd attempt and Ace's follow-up dispatch both wrote to `~/.claude/agents/<role>-<name>/memories.md` + `experience.md` without prompt. `BL-PERM-SUBAGENT` closed.

### Backlog items opened

- `BL-VIZ-O1-LEGACY` — 35 chart JSONs on 6 legacy pairs lack `_meta.json` sidecars; VIZ-O1 retro-apply scheduled for Wave 10H.2/10I.
- `BL-VIZ-SIDECAR-HELPER` — 4 generators bypass the shared sidecar path; refactor candidate bundled with BL-VIZ-O1-LEGACY.
- `BL-APP-PR1` — path resolution discipline rule (proposed by Ace); prophylactic, bundles with legacy-page migration.
- `BL-APP-PT1-LEGACY` — 5 Methodology pages still bypass `render_methodology_page()`; migration wave scheduled.

### Commits

| Commit | Author | Content |
|--------|--------|---------|
| `e6767e0` | Ace | APP-PT2 helper + methodology wiring |
| `c9f4d47` | Vera | VIZ-O1/E1 backfill + Sample exploratory_charts + generator updates |
| `f0fcd02` | Quincy | canonical cloud_verify.py + GATE-28 verification |
| `a74fedf` | Lead | backlog: BL-VIZ-O1-LEGACY, BL-VIZ-SIDECAR-HELPER, BL-PERM-SUBAGENT |
| `b3facc8` | Lead | settings.json permission path syntax fix |
| `c91e32b` | Lead | Wave 10H.0 Lead Delegation Discipline SOP |
| `44a487a` | Quincy | cloud_verify iframe resolution fix (3rd attempt) |
| `b86f960` | Lead | close BL-PERM-SUBAGENT |
| `387062f` | Ace | fix landing raw-col leak + Sample Methodology Exploratory Insights direct call |
| `6e3e821` | Lead | backlog: BL-APP-PR1, BL-APP-PT1-LEGACY |
| `aca5602` | Quincy | final re-verify — 17/17 PASS |

### Lessons

- **Pattern 22 is a class of bug, not an isolated one.** Playwright's `inner_text` strips CSS markup; any check assuming class names appear in extracted text is doomed. Lesson codified in qa-agent-sop.md cloud-visual-smoke protocol.
- **Playwright `page.frames` iteration races Streamlit frame registration.** Use selector-based discovery (`wait_for_selector('iframe[title=...]').content_frame()`) for reliability. Codified in Quincy's SOP.
- **A centralised template only protects pages that actually use it.** APP-PT1 migration is incomplete — 5 of 7 Methodology pages are hand-written, so Wave 10H.1's new helper was silently absent there despite being "wired correctly". Any future APP-* rule touching a non-thin page will repeat this bug class. `BL-APP-PT1-LEGACY` exists to close the gap; in the interim, agent briefs for any Methodology-page rule must explicitly list bypass pages that need defensive direct calls.
- **Path-resolution discipline matters more on cloud than local.** Streamlit Cloud's runtime CWD differs from the repo root; bare relative paths (`Path("results") / ...`) silently fail. Anchor to `_REPO_ROOT = Path(__file__).resolve().parents[N]` or equivalent. Codified as `BL-APP-PR1` for a future SOP.
- **Settings file syntax: double-slash = absolute, single-slash = project-relative.** Confirmed from official Claude Code docs; fix validated twice. Worth noting in team-standards.
- **Lead drift is the dominant failure mode.** The wave's governance meta-event was Lead doing agent work, noticed by the user. The LEAD-DL1 SOP + auto-memory trigger + wave-closure self-audit is the durable mitigation. The test of whether this holds is whether future wave closures show Lead commits touching only category-1-to-6 paths.

### Sample of what users see now

Opening the Sample Methodology page, scrolling past "Analyst Suggestions for Future Work", the user now sees:

> ### Exploratory Insights
> ℹ️ The following charts were generated as exploratory findings beyond the standard analytical set. Each captures an angle our team found potentially useful. If you find any of these views valuable and would like them included as a standard view for all pairs, let the team know.
>
> [hero_spread_vs_spy chart]
> **What this shows:** A dual-axis 25-year picture of credit-market stress vs the S&P 500…
> *Analytical note: Dual-axis rendering makes the co-movement visually direct…*
> ↳ Useful? Let the team know if you'd like this included as a standard view.
>
> [spread_history_annotated chart]
> **What this shows:** The same spread history with crisis episodes labelled inline…
>
> [tournament_sharpe_dist chart]
> **What this shows:** A distribution view of how every candidate strategy performed…

Before this wave, these 3 charts existed on disk under `output/charts/hy_ig_v2_spy/plotly/` but no page rendered them — silent evaporation. VIZ-O1 (disposition mandate) + APP-PT2 (Methodology consumer) closes the class of bug; this is the first pair where the framework ships end-to-end.

---

## 2026-04-22 — Wave 10G: Sample Ratification + New HY-IG × SPY Dashboard — **COMPLETE**

### New Features

**HY-IG × SPY dashboard rebuilt from scratch** using the latest SOPs + APP-PT1 templates:
- Winner: HMM stress-regime probability (S6_hmm_stress, T4_hmm_0.5, P2 signal-strength, L0 lead)
- OOS Sharpe 1.41, ann return 11.7%, max drawdown −8.5%, 387 trades over 2019-10 to 2026-04
- Buy-and-hold SPY benchmark: Sharpe 0.81, max drawdown −33.7%
- 2166 tournament combos (2036 valid)
- 22 charts under `output/charts/hy_ig_spy/plotly/` (bare-name, all with `_meta.json` sidecars)
- 4 portal pages as APP-PT1 thin wrappers (pages `15_hy_ig_spy_{story,evidence,strategy,methodology}.py`)
- Matches Sample (hy_ig_v2_spy) feature set through the template — no hand-coded pages

**Sample ratification:**
- `hy_ig_v2_spy` promoted as the canonical quality benchmark. All future pairs quality-compared to this.
- Git tag `sample-v1.0` pinned.
- Landing card renders blue ★ SAMPLE badge.
- pair_id unchanged on disk; display-layer rename only.

**v1 archived:**
- `results/hy_ig_spy_v1/`, `data/hy_ig_spy_v1_*`, `app/pages_archive/hy_ig_spy_v1_*`, `scripts/archive/`, `docs/archive/`
- Files preserved for historical reference.
- Namespace `hy_ig_spy` freed for the new pair.

### New SOP Rules

| Rule | SOP | Purpose |
|------|-----|---------|
| APP-RL1 | AppDev | Single-source routing / label maps — no duplicate dicts across modules. Root cause of the 10G.4E `StreamlitPageNotFoundError`. |
| DATA-D6b | Data Dana | User-facing text fields in `interpretation_metadata.json` (`key_finding`, `mechanism`, `caveats`) must use human-readable instrument/signal names, not raw column identifiers. Root cause of the landing-card `hy_ig_spread_pct` leak. |
| GATE-28 scope extension | QA Quincy | Cloud verify now covers ALL active pairs × ALL 4 pages. Partial pass → wave does not close. No more "fixed 3 of 4 pages and forgot the 4th." |
| HISTORY_ZOOM_EPISODES + regime_context (APP-PT1 supplement) | AppDev | Template optional fields so new pairs can render crisis-episode zooms + regime callouts via config, without hand-coding. |

### Migrations / Refactors

- `_page_prefix()` duplicate dict in `page_templates.py` **deleted** — template now imports `get_page_prefix(pair_id)` from `pair_registry.py` (single source per APP-RL1).
- `probability_engine_panel._validate_signal` handles both tuple-form and dict-form stress-episode registries (backward-compat normaliser added).
- Chart loader pair-prefix fallback finally buried — new pair inherits bare-name-only contract automatically.

### Patterns Absorbed (21–22)

| # | Pattern | Evidence |
|---|---------|----------|
| 21 | QA-CL2 turnover-trade-count triangulation needs a P2 strategy-class exception — `annual_turnover` and `oos_n_trades` are incommensurate when the signal rebalances continuously | Quincy Wave 10G.4F (commit `b72a293`) |
| 22 | DOM chart detection via `"js-plotly-plot"` in `inner_text` always returns 0 — CSS classes aren't in extracted text. Use axis-label / month-year text patterns or `query_selector_all` instead. | Wave 10G.5 full-verify false negative on 3 structurally-clean pages |

### Commits (in order)

`02251bd` (10G.1 archive v1) → `567b711` (10G.2 Sample + tag `sample-v1.0`) → `cfe66fb` (10G.3 template extensions) → `b15c1d1` (10G.4A Dana) → `1561370` (10G.4B Ray) → `fb49123` (10G.4C Evan) → `c525470` (10G.4D Vera) → `4e45eb0` (10G.4E Ace) → `b72a293` (10G.4F Quincy local QA) → `75d6574` (10G.4E-fix Ace partial) → `9ba3649` (10G.5 SOPs: APP-RL1, GATE-28 scope) → `35bb008` (10G.5-fix APP-RL1 merged) → `236bce3` (DATA-D6b SOP) → `3c37d96` (Dana DATA-D6b fix applied).

---

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
