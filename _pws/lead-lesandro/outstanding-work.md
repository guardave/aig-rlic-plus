# Outstanding work — Lead Lesandro

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
