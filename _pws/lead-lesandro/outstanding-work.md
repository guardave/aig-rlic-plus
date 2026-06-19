# Lead Lesandro — Outstanding Work

## Current open items (as of 2026-06-19 checkpoint)

**Shipped this session (all live on production, full-fleet sweep 53 PASS/0 FAIL):** pairs #23 `m2sl_yoy_spy` (`9808b56`) + #24 `phlxsox_spy` (`345dbc9`) — both Mode 1 — and **umcsent winner-refresh** (`7b0a1f2`, stakeholder-approved; corrected 1.16 winner now live, stale-1.02 defect resolved). New-pair queue EXHAUSTED. umcsent branch `fix260619_umcsent_winner_refresh` KEPT (per user, not deleted).

**📋 NEW POLICY (2026-06-19): document new findings/deferred work as GitHub ISSUES, not docs/backlog.md rows.** backlog.md = historical only. (memory: feedback_gh_issues_over_backlog)

**Open GitHub issues:**
- **#12** — GATE-VIZ-NBER2 dotcom NBER shading WARN (Vera; 6 fixable pairs + frozen hy_ig_v2 EXEMPT). Non-blocking, from the 2026-06-19 fleet sweep.
- **#4** — Storytelling architecture review (pre-existing).

**Candidate issues NOT yet filed (offered to user, awaiting word):**
- Legacy `signal_code_registry` non-conforming entries (`ism_services_above_50` etc., non-enum `source_method`) — triple-confirmed (umcsent + M2 + SOX Evan stages).
- Wave D prose-vs-data lint (validated design; can land blocking now umcsent is fixed).

**Wave D (META-CMP Tier-3 SOP-hardening) — IN FLIGHT, paused:**
- Scope chosen: focused D-1 = scoped BL-PROSE-DATA-GREP + BL-APP-DR1 + verify/close BL-VIZ-DC1. Mode: Mode-1 Lead direct. Needs a fresh branch (`fix260618_meta_cmp_tier3` was created empty + deleted at EOD — nothing written yet).
- **Validated lint design (don't re-derive):** prose-vs-data lint scoped to OOS Sharpe only (every config quotes it numerically); check winner `oos_sharpe` (2dp or 1dp) appears in config text. B&H Sharpe stated qualitatively in some pairs (gold_copper "about twice the buy-and-hold ratio") → do NOT require its literal value. Legacy `bh_sharpe: null` pairs skip. New gate can't go blocking until umcsent is fixed (else blocks all commits).
- DEFER to D-2: BL-APP-NUM1 (179-hit noisy surface), BL-VIZ-LO1, BL-CHART-CONTRACT (Vera-owned chart introspection).

**User-side action pending:**
- **dawodev preview app** — still tracks the now-DELETED `feat_ism_services_spy` branch; errors until repointed (to `main`, or hold for next pair). User-side Streamlit Cloud action.

**Done this session:** pair #22 ism_services_spy shipped+merged (`4e6f329`); branch deleted. Codex dispatch skill installed (`0548b80`); dispatch policy + tmux relaxation to memory. Backlog Wave A shipped (BL-ECON-SD-PORTAL `b890718`; BL-CARD-DENOM closed; BL-PLOTLY-TITLE-WRAP annotated).

**Housekeeping (no user input needed):**
- tmux `ism` session idle (panes returned to prompt) — can be killed.
- Untracked scratch: `_pws/lead-lesandro/mode3_ism_services/*pane.log`, `streamlit_local.log`, `app/_smoke_tests/loader_*_20260618.log`. Briefs committed at checkpoint.

**Recurring tooling debt (non-blocking):**
- `cloud_verify.py` + local DOM checker time out (30s, "element is not visible") clicking hidden/nested sub-tab handles. Screenshot/click false-negatives only — DOM content checks PASS. Candidate fix: skip non-visible tab handles before click.

**Standing / suspended:**
- `fix260613_lead_horizon` spec-memo (suspended).
- BL-ECON-SD-PORTAL backlog.
- Next prospective pair: see `data/prospective_pairs.csv` (priority order).

---

## Archived: fix260601_chart_hygiene plan (superseded)

# Outstanding work — Lead Lesandro

Last updated: 2026-06-12 EOD.

---

## ✅ CLOSED 2026-06-13 — production verify of c8f73a6

`busloans_spy` production sweep ran 2026-06-13 11:30 UTC against `https://aig-rlic-plus.streamlit.app`: **ALL PASS (30/30)** — landing card (1.50 / −1.0% / 4,396, Lagging chip), all 4 pages, DPS-FE2 search-phase routing live with zero leakage to other pairs, regression pairs + frozen Sample clean. Evidence content-presence checks corrected to probe frame HTML (collapsed-expander lesson). Production was already current (auto-deploy/reboot caught up post-EOD). Evidence script: /tmp/busloans_prod.py.

## Items added/updated 2026-06-12

- **busloans_spy shipped** (Pair #19, 9th portal pair, first full Mode-1 pair pipeline). DPS-PRE1 waiver recorded in pair_execution_history; **ECON-FE1 final exam = the pair's next milestone** (documented in `results/busloans_spy/evidence_status.json` next_step) — natural trigger: enough post-search data or a holdout protocol decision.
- **`fix260612_busloans_spy` branch:** merged, NOT yet deleted — ask user per LEAD-BD1 next session.
- **META-A2A live** (team-coordination §META-A2A, standards §5.7).
- Backlog +3: BL-EPISODE-SLUGS (slug vocabulary reconciliation wave), BL-PLOTLY-TITLE-WRAP (cosmetic), BL-CARD-DENOM (cosmetic). Dana's note: `scripts/build_prospective_pairs.py` may reintroduce the ci_loan mislabel on regeneration — fold a generator-side fix into the next data-infra touch (not yet a BL row; add if the generator is touched first).
- Vera flagged her `_LOCAL_INDICATOR_LABELS` fallback in the SR1 chart script as removable now display_names has busloans entries — fold into her next touch.

---

## Items added/updated 2026-06-11 (post fix260611_meta_cmp / GH #7)

- **GH #7 CLOSED** — META-CMP Tier 1+2 + ECON-SR1 rehab merged at `6301e13`, production-verified. Only GH #4 remains open.
- **Pre-commit hook now ACTIVE in this clone** (`core.hooksPath scripts/hooks`). Every future commit runs T1.1/T1.3/T2 (+T1.2 on app/charts staging). New clones must run `git config core.hooksPath scripts/hooks` — documented in team-standards §5.6.
- **`fix260602_pair4_prep` resume scope grows again:** crude_oil_xle must now ALSO pass the four META-CMP gates (its results dir will be schema-validated by T1.1 once registered — its known schema violations will be caught mechanically, which is helpful) and follow ECON-SR1 if any series reconstruction happens. Running total of retrofit standards: 6 from 2026-06-10 + META-CMP compliance + ECON-SR1.
- **META-CMP Tier 3** (text-vs-data citation lint) — deferred; trigger tracked via BL-PROSE-DATA-GREP. This session's "Long/Cash beside verified numbers" miss strengthens the case; propose as its own issue when the next prose-drift surfaces or when a SOP-hardening slot opens.
- **BL-XLP-WS-LEGACY** — indpro_xlp winner_summary legacy shape (missing threshold_code, ambiguous threshold_value, non-direction-adjusted threshold_rule). Triggers: xlp threshold display misbehaves / next winner_summary schema wave / pair4_prep resume.
- **Stale code comments** flagged by Vera (indpro_spy config ~594-595, vix config ~476 — "no charts on disk" now false): trivial, not user-facing; fold into Ace's next config touch.

---

---

## Items added/updated 2026-06-10 evening (post fix260610_audit_q)

- **GH #9-11 CLOSED** — fixed in `fix260610_audit_q`, merged at `53c1e73`, production-verified. Branch deleted (owner consent given).
- **`fix260602_pair4_prep` resume scope expanded AGAIN:** crude_oil_xle on resume must also satisfy the three audit_q standards — ECON-T4 (benchmark row `valid=False` in its tournament CSV), ECON-H5 (canonical `oos_max_drawdown` only — note its winner_summary defect list already includes schema violations), DPS-SCD1/VIZ-SCD1 (tournament_intro position disclosure + dist-chart annotation).
- **BL-801 / BL-DUP-13 residue** — tournament-CSV *column* naming variance (`max_drawdown` percent vs `oos_max_drawdown`; META-UC scale detection in pair_registry) is the remaining drawdown-related scope, still bundled with BL-801. winner_summary side fully resolved.
- Open GH issues remaining: #4 (storytelling architecture review), #7 (META-CMP forcing functions) — both pre-existing.

---

## Items added/updated 2026-06-10

- **`fix260602_pair4_prep` resume scope EXPANDED.** On resume, crude_oil_xle additionally needs the three cross-pair standards shipped 2026-06-10: CP section on Strategy/Confidence (not Evidence), VIZ-QR1 dual-panel regime chart (use `scripts/_quartile_chart.py` helper; its regime axis is vol-regime, NOT quartiles — apply on the native axis like hy_ig_spy did with HMM, do not force quartiles), DPS-LF1 long-form naming, and the Downloads expander on Evidence. Original schema-defect list below still stands.
- **BL-PERMIT-CHARTS-EXCEPTION — likely closable.** vichua4b's `3c8b10d` landed equity_curves/drawdown/walk_forward charts for permit_spy. Confirm with vichua before striking the backlog row.
- **Branch state at 2026-06-10 EOD:** `main` at `f1acc27` (both fix260610 branches merged, production-verified). Remote branches: `main`, `fix260602_pair4_prep` (SUSPENDED, preserved), `feature/hy_ig_execution_panel` + `feature/indicator-evaluation-sop` (YYY's — restored after LEAD-BD1 incident), `rescue-my-work` (Rex's — restored). Deleted for good: both fix260610 branches, `fix260602_prospective_pairs`, `fix260603_prod_dawo`.
- **LEAD-BD1** recorded in memories.md — branch deletion requires tip-author ownership check + per-branch owner consent.

---

## TOP — `fix260602_pair4_prep` SUSPENDED — schema-violations to fix before resuming

**Branch state.** `fix260602_pair4_prep` at `0f9293b` on origin. 12 commits ahead of `main` at session end. **NOT merged.** Earlier attempt to merge was reverted (`aa5a404` → `8e86f60`) after user-side DOM probe surfaced multiple production-breaking defects that the round-4 four-checker PASS had missed.

**Why the round-4 PASS was a false positive.** My checker subagent prompts asked agents to read producer files (JSON, configs, scripts) and verify self-consistency. None of the prompts asked agents to drive Playwright against the rendered DOM. The consumer-side `validate_or_die` in `app/components/schema_check.py` runs at render time against `docs/schemas/*.schema.json` — schemas that GATE-CMP1's `_check_backlog_hygiene` doesn't load. Multiple producer artefacts that I emitted PASSED my mechanical checks while VIOLATING the consumer-side schema contract.

**Defects to fix before resume:**

| Surface | Defect | Root cause | Schema or evidence |
|---|---|---|---|
| Strategy | 3 red error panels: "winner_summary.json does not conform to winner_summary.schema.json" | (a) missing `signal_code` required field; (b) `direction: "long_when_high_vol_regime"` not in enum `["procyclical","countercyclical","mixed"]`; (c) `strategy_family: "wti_high_vol_long"` not in enum `["P1_long_cash","P2_signal_strength","P3_long_short"]` | `docs/schemas/winner_summary.schema.json:11-25` |
| Strategy | "Position exposure cannot be derived without valid signal values" (yellow panel) | Cascade from missing `signal_code` (the panel can't look up the parquet column) | same |
| Methodology | "signal_scope.json does not conform" — 6 required fields missing (`schema_version`, `indicator_axis`, `target_axis`, `last_updated_by`, `last_updated_at`, `owner`) | I emitted a free-form JSON without consulting the schema | `docs/schemas/signal_scope.schema.json` |
| Methodology | "analyst_suggestions.json does not conform" — 2 required fields missing (`schema_version`, `last_updated_at`) | same | `docs/schemas/analyst_suggestions.schema.json` |
| Evidence | 3 Level-1 method blocks (Correlation, Lead-lag, Stationarity) all render the SAME `rolling_correlation` chart — I gave each block the same `chart_name` | Each block must point at a distinct chart slug | — |
| Strategy / Evidence | "Cross-period analysis pending — Rolling Sharpe chart not yet available" placeholder | Pair lacks `rolling_sharpe` + `rolling_granger` charts | Either generate or codify omission per user-confirmed standard "placeholders not acceptable quality" |
| All pages | 7 console 404s | Likely missing asset paths (PNG or page-resource) | Diagnose with browser devtools/playwright |

**Plan to resume (DOM-first, per LEAD-DOM1):**

1. Read `docs/schemas/winner_summary.schema.json`, `signal_scope.schema.json`, `analyst_suggestions.schema.json`, `signal_code_registry.json` in full. Identify the canonical enum values, required fields, and signal_code conventions for a vol-regime strategy. Likely choices: `direction: "procyclical"` (vol-regime signal is positive-cyclical for energy), `strategy_family: "P1_long_cash"` (binary long/cash), `signal_code: "S_vol_pctile"` (new entry — registry is append-only).
2. Update `scripts/pair_pipeline_crude_oil_xle.py` to emit the three artefacts in their schema-conformant shape. Re-run the pipeline.
3. Update `EVIDENCE_METHOD_BLOCKS` so each Level-1 block has a distinct `chart_name`.
4. Decide disposition for the Cross-period placeholders: (a) generate the charts (likely needs new chart-generation code), or (b) codify omission in pair_config so the section doesn't render. User standard says placeholders are not acceptable.
5. Investigate the 7 console 404s.
6. **Drive Playwright against the rendered DOM** for every page; LEAD-DOM1 assertion checklist must pass. Iterate the producer until clean.
7. Ask user for explicit merge authorisation per LEAD-MA1.

Branch is on origin awaiting resume. Do NOT merge anything from this branch until the above is done.

---

## Branch state at session end

| Branch | State | Tip | Notes |
|---|---|---|---|
| `main` | clean, deployed, verified | `95e159b` | Carries fix260603_prod_dawo + LEAD-MA1 + LEAD-DOM1 SOP additions |
| `fix260603_prod_dawo` | merged + safe to delete | `078ce14` | 7 KS/YYY issues closed; production-verified clean |
| `fix260602_pair4_prep` | **SUSPENDED — DO NOT MERGE** | `0f9293b` | See defects above |

**dawodev** currently pointed at `fix260603_prod_dawo` (now merged). Repoint to whichever branch is in flight when resumed.

---

## SOFR-TED comment-log items #38-51 (user-owned)

User explicitly opted to handle the 14 SOFR-TED items' disposition in the original Excel, not in the temp/ copy I have access to. They want to wait for others' comments to land before shipping a new version of the comment log. **I do not touch `temp/Step C - Dashboard Comment log (2606031212BST).xlsx`.**

---

## PRIOR ENTRY (kept for reference)

Last updated: 2026-06-01 EOD (chart-hygiene branch: Wave 1 done; Wave 2 paused at scope-creep discovery; Wave 3 pending).

## Branch state

**`main`** at `c4615c9` (backlog status snapshot, post-fix260601_rescue merge).

**Active feature branch:** `fix260601_chart_hygiene` at `0c82281`, 2 commits ahead of main, pushed to `origin/fix260601_chart_hygiene`:
1. `d7971a0` — **Wave 1 done.** BL-VIZ-CHART-PREFIX-LEGACY: renamed 20 chart JSONs + 20 perceptual_check PNGs across `indpro_spy` / `permit_spy` / `vix_vix3m_spy` from pair-id-prefixed to canonical bare names; updated 3 pair_config.py files. Validator delta: 934 PASS / 184 FAIL → 954 PASS / 164 FAIL (−20 FAILs cleared, exactly matching the per-pair chart-name mismatches). Local Streamlit sweep: 45/45 PASS, **zero byte drift on rendered DOM** vs fix260601_rescue baseline. Renames invisible to users.
2. `0c82281` — ECON-BM1 SOP tightening (replaces 5-case if-table with single rule: "the pair's target is the buy-and-hold benchmark, no special cases") + `_pws/lead-lesandro/memories.md` "Mode 2 hat-wearing discipline" entry.

## Wave 2 paused — scope creep discovery (handover detail)

**Original Wave 2 plan:** BL-CHART-GAPS-LEGACY back-generation. 4 pairs (`permit_spy`, `sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`) lack `equity_curves.json` / `drawdown.json` / `walk_forward.json`. The plan was: render the 3 charts × 4 pairs from existing strategy-return time series using `scripts/tournament.py::compute_buy_and_hold_stats` + chart layout helpers.

**Discovery (Evan hat):** The 4 pairs' `winner_trade_log.csv` files have **`trade_return_pct = 0` for every trade row**. So the strategy-return time series **doesn't exist** in usable form. To render the 3 charts properly, would need to:
1. Re-derive strategy positions from `winner_summary.json` (signal_column + threshold + lead + strategy_family)
2. Apply positions to daily target returns (the signals parquet has *forward* returns at given horizons, not daily raw returns — needs the master parquet)
3. Compute strategy returns + cumulative equity + drawdowns + per-year Sharpe
4. Emit broker-style APP-TL1 CSVs (these pairs also lack `winner_trades_broker_style.csv`)
5. Populate `bh_sharpe` / `bh_max_drawdown` (same gap as the gold_copper_xli case that closed BL-GC-BH via `scripts/tournament.py` migration)

**This is half of BL-DUP-5 pipeline consolidation, not chart hygiene.** Closer to a separate `fix260601_legacy_pipeline_rehab` branch than a sub-wave of chart hygiene.

**Three options surfaced to user (still awaiting decision):**

| Option | Scope | Effort |
|---|---|---|
| **2c** Drop the 3 chart slots from the 4 pair configs entirely; add a Strategy-page section note "Performance charts coming with pipeline rebuild — see backlog" | In-branch hygiene close | 30 min |
| **2b'** Open separate branch `fix260601_legacy_pipeline_rehab` to rebuild 4 pipelines properly (DUP-5 partial) | New branch, 1–2 sessions | bigger |
| **2d** Block the 4 pages from rendering at all (page-level "this pair is being rebuilt" banner) | Pulls 4 pages from prod | 20 min |

**User has not yet picked.** EOD called before answer received.

## Wave 3 pending — BL-VIZ-O1-LEGACY

35 chart JSONs across 6 legacy pair directories (`dff_ted_spy`, `indpro_spy`, `permit_spy`, `sofr_ted_spy`, `ted_spliced_spy`, `vix_vix3m_spy`) lack matching `_meta.json` sidecars per VIZ-O1 (Disposition Mandate). Programmatic backfill: for each chart JSON without a sidecar, create the `_meta.json` with `{"disposition": "consumed", "rules_applied": [...], "generated_at": iso_utc_now()}` + narrative_alignment_note derived from chart title.

Estimated ~30 min. **Not started.**

## Active questions / pending decisions (carried forward)

- **Wave 2 option choice** (2c / 2b' / 2d) — see above
- **GH #4 close decision** — verdict comment posted, awaiting stakeholder
- **GH #7 META-CMP** — Tier 1+2 forcing functions queued for dedicated SOP-hardening branch (now has working scaffold from fix260601_rescue: `scripts/validate_pair_completeness.py` + `docs/dashboard-page-standard.md`)

## Recently closed this session (2026-06-01)

| Item | Result |
|---|---|
| `target260501` | Rescued into fix260601_rescue + deleted from remote |
| `260430` | Tier-1 durable infra rescued into fix260601_rescue + deleted from remote (HSN1F pair + HY-IG v3/v4/v5/v6 experiments + Tier-2 chart-generator changes all discarded per user decision) |
| `fix260601_rescue` | Merged to main at `41545cb` (3-track regression: 45/45 local + 9/9 components + 45/45 cloud); branch deleted post-verify |
| `docs/backlog.md` Status snapshot | Added — marks BL-DUP-1/4/8/11/15 as 🟡 PARTIAL and BL-META-CMP/BL-DUP-6 as 🟢 SCAFFOLDED |

## Repeated lesson this session (worth crystallising in memories.md)

**Mode 2 hat-wearing discipline.** When authoring artifacts that fall in a role's lane, open the relevant role SOP and scan for the directly-relevant rule. NOT a preemptive load of every role SOP at SOD (~50k+ tokens of waste). Crystallised by: asked user "should the benchmark be SPY?" — rule was already in `econometrics-agent-sop.md:847` ("benchmark = buy-and-hold of the target"). Asked because I was authoring an econometric artifact (chart back-generation) without putting Evan's hat on. User's reaction: *"If you ask me this, does it mean there is no such knowledge in the context?"* — correctly identifying the procedural gap.

## Backlog state (snapshot)

- 40 active deferrals, 3 closed (BL-PERM-SUBAGENT, BL-APP-PR1 promoted, BL-GC-BH)
- 4 🟡 PARTIAL (BL-DUP-1/4/11/15; BL-DUP-8 also partial via DUP-4 helper)
- 2 🟢 SCAFFOLDED (BL-META-CMP / BL-DUP-6 — validator scaffold in tree)
- No new BL-* rows added this session

## Untracked working state

- `_pws/qa-queenie/` exists as untracked. Belongs to QA agent.
- Many `_pws/lead-lesandro/chart_hygiene_260601/*.txt` working logs from Wave 1 (baseline + after-Wave-1 validator counts).
- `temp/*` working files (gitignored).

## Sequenced plan for next session (continuing from here)

1. **Lead receives Wave 2 decision** (2c / 2b' / 2d) — short user message.
2. If 2c: drop 3 chart slots from 4 configs + add planned-rebuild note to Strategy page; ~30 min + verify.
3. If 2b': open new branch `fix260601_legacy_pipeline_rehab`, leave `fix260601_chart_hygiene` to ship without Wave 2.
4. If 2d: block 4 pages with banner + add planned-rebuild backlog entry.
5. Execute Wave 3 (VIZ-O1 sidecar backfill, ~30 min) regardless of 2c/2b'/2d choice.
6. Full local sweep + cloud preview + merge `fix260601_chart_hygiene` to main.
