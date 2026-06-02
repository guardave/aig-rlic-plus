# Outstanding work — Lead Lesandro

Last updated: 2026-06-02 EOD.

---

## TOP — `fix260602_pair4_prep` checker findings (resume here next session)

**Branch state.** `fix260602_pair4_prep` at `c59f0c2`, 6 commits ahead of main, pushed. Held unmerged pending checker-finding resolution. Production (`main`) unaffected — `fix260602_prospective_pairs` was the merged piece earlier today (`2510ba0`).

**Mode 2 exit criteria: NOT MET.** Three of four checkers returned FAIL or FAIL_WITH_WARNINGS on `crude_oil_xle`. Per LEAD-WM1, must resolve and re-dispatch until all four return clean.

**User-pending decision** (paste of unresolved end-of-session question):

> Category A (real bugs) — fix immediately.
> Category B (gate-coverage gaps the completeness checker found) — three options:
>   (a) Fill the missing artifacts now (analysis_brief, core_models dir, acceptance.md, etc.)
>   (b) Extend GATE-CMP1 to catch these mechanically as a refinement
>   (c) Mark as documented exceptions for this verification build
> My recommendation was **(b)+(c) combined**: extend the gate so the next pair build doesn't repeat the gap; don't backfill retroactively, document the gap as a debrief outcome.

Resume by getting the user's Category B disposition decision.

### Category A — real bugs to fix (Lead → Evan/Ace hat work)

| ID | Severity | File | Issue | Fix |
|---|---|---|---|---|
| A1 | BLOCKER | `app/pair_configs/crude_oil_xle_config.py:139`, `docs/portal_narrative_crude_oil_xle.md:68`, `:306`, `crude_oil_xle_config.py:330-332` | Pearson 0.55 claimed in 4 prose locations; data says 0.26 | Replace 4×: 0.55 → 0.26 (Spearman is 0.40 — neither is 0.55) |
| A2 | MAJOR | `scripts/pair_pipeline_crude_oil_xle.py:417-462` | winner_trade_log P&L attribution off-by-one vs `_strategy_stats` | Re-slice `pos*ret-cost` per trade window (use `pos==entry_pos` boundary, not inclusive `loc[entry:exit]`) |
| A3 | MAJOR | `scripts/generate_charts_crude_oil_xle.py:86-114` | Equity / drawdown / walk-forward / subperiod-Sharpe charts gross-of-cost; headline stats net-of-cost. Strategy lines overstate by ~25% terminal | Add cost model in `_equity_from_position` matching `_strategy_stats` |
| A4 | MAJOR | `app/pair_configs/crude_oil_xle_config.py:362-365` | Evidence lead_lag.observation says "Max R² at lag 0 (~0.30)"; data says 0.07 | Replace "~0.30" with "~0.07" |
| A5 | MAJOR | `docs/portal_narrative_crude_oil_xle.md:46-49` | Story narrative says "four pure-momentum / two long-short" but actually 3/3 | Fix to "three pure-momentum variants" + "three long-short sign variants" |
| A6 | MAJOR | `scripts/pair_pipeline_crude_oil_xle.py:464-480` | Broker CSV `pnl_pct` ≠ from displayed entry/exit prices | Either compute pnl_pct from prices, or drop price columns and document |
| A7 | MAJOR | `scripts/pair_pipeline_crude_oil_xle.py:182-209` | `(1+log_return).cumprod()` mixes log + simple returns | Pick one: `exp(r)-1` then cumprod, or `exp(cumsum)` everywhere |
| A8 | MINOR | `winner_summary.json` keys | `oos_n_trades=41` counts state transitions not trades; `oos_win_rate=0.1821` is period win-rate not trade win-rate | Rename or recompute |
| A9 | MINOR | `interpretation_metadata.json` | `indicator_nature=coincident`, `expected_direction=pro_cyclical` hardcoded; doesn't match vol-regime winner | Qualify in key_finding or derive from winner |

### Category B — GATE-CMP1 gap items (5 found by Completeness checker)

| Missing artifact | Required by | Disposition pending |
|---|---|---|
| `docs/analysis_brief_crude_oil_xle_*.md` | team-coordination.md row 1 | User decision |
| `data/crude_oil_xle_*.parquet` (master joined dataset) | team-coordination.md row 2 | User decision |
| `results/crude_oil_xle/exploratory_*/correlations.csv` shape | team-coordination.md row 5 | User decision |
| `results/crude_oil_xle/core_models_*/` dir with ≥3 CSVs | team-coordination.md row 6 | User decision |
| `results/crude_oil_xle/acceptance.md` | GATE-23 | User decision |
| `tournament_winner.json` (separate from `winner_summary.json`) | team-coordination.md "Tournament Winner JSON Schema" | User decision |
| portal_glossary.json entries for "Realized volatility" + "Quartile rank" | DPS-II1 | User decision |

If user picks (b), extend `_check_backlog_hygiene` with checks for each. If (a), Lead authors / dispatches. If (c), document as known debrief outcomes in the LEAD-NPB1 lessons-learned memory.

### Category C — ELI5 polish (find-and-replace scale)

| Loc | Issue | One-line rewrite |
|---|---|---|
| StoryConfig.PLAIN_ENGLISH | "Sharpe of about 0.47" undefined on first mention | Append "(a measure of return per unit of risk — higher is better; 0.5 is decent, 1.0 is very good)" |
| StrategyConfig.PLAIN_ENGLISH | "Sharpe ratio" + "drawdowns" both undefined | Append "(drawdown = how far the strategy fell from its previous peak)" |
| StoryConfig.ONE_SENTENCE_THESIS | "realized volatility / top quartile / risk-adjusted return" all jargon | Replace with "When crude oil has been unusually choppy over the past three months (top 25% of the last five years), energy stocks tend to deliver better return-per-unit-of-risk." |
| CAVEATS_MD | "OOS / multiple-comparisons risk / upper bound on OOS expectation" | Replace with "We tested 12 rules and kept the best one. When you pick the winner from a contest, the winner usually looks better than it will be in real life — so treat the 0.47 number as an optimistic ceiling, not a forecast." |
| EVIDENCE_METHOD_BLOCKS.plain_english | "Pearson / Lead-lag / CUSUM / quartile" pile-up | Replace second half with layperson restatement (see ELI5 checker report) |
| Evidence level1 lead_lag.how_to_read | Assumes R² + p-value literacy | Replace with bar-chart interpretation language (see ELI5 checker report) |
| StoryConfig.HERO_CAPTION | "dual-axis / NBER recession bands / volatility clustering" undefined | Add "(grey bands = US recessions)" and replace "volatility clustering" with "lines go quiet in calm years, wild in stressed years" |

### Mode-2 exit replay plan

1. Lead fixes Category A (single commit, hat = Evan + Ace)
2. Re-dispatch Correctness + Consistency checkers → expect PASS
3. User decides Category B disposition
4. Lead fixes Category C (single commit, hat = Ray)
5. Re-dispatch ELI5 checker → expect PASS
6. Re-run GATE-CMP1 → expect PASS
7. Cloud re-verify on dawodev
8. Merge `fix260602_pair4_prep` → main

### Branch-state summary at session end

| Branch | Status | Tip |
|---|---|---|
| `main` | clean, deployed | `2510ba0` (fix260602_prospective_pairs merged earlier today) |
| `fix260602_pair4_prep` | held, pushed | `c59f0c2` (6 commits ahead) |
| `fix260602_prospective_pairs` | merged + safe to delete | `34da1ab` |

dawodev currently pointed at `fix260602_pair4_prep` per user repoint earlier today.

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
