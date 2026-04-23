# Handoff — Ray → Lead (Wave 10I.A Part 3a: narrative port for 4 non-TED pairs)

**Author:** Research Ray (research-ray)
**Date:** 2026-04-23
**Wave:** 10I.A Part 3a
**Governing rules:** APP-PT1 (template abstraction), APP-TL1 (trade log contract), RES-NR1 (narrative ownership), META-ELI5.
**Scope:** Replace all TODO-Ray stubs in 4 pair configs with proper narrative prose ported from legacy hand-written pages (pre-migration commit 24e2f16~1).

---

## Summary

- **190 TODO-Ray stubs filled (100%).** All 4 configs now have zero remaining TODO-Ray tokens.
- **4/4 smoke tests PASS with failures=0** (16 total passes across 4 pairs).
- **Content sourced from legacy `app/pages/{N}_{pair}_*.py` via `git show 24e2f16~1:...`**, then lightly edited for META-ELI5 compliance and Wave 10H+ editorial voice. Pair-specific factual content (crisis episodes, signal definitions, thresholds, regime Sharpe numbers) preserved verbatim.
- **KPI cross-check against `winner_summary.json`:** all four pairs re-validated; no corrections needed — the structural `_TOURNAMENT_DESIGN_MD` skeletons Ace filled from `docs/pair_execution_history.md` were already consistent with the authoritative `winner_summary.json`. I did enrich each `_TOURNAMENT_DESIGN_MD` with the full numeric record directly from `winner_summary.json` (OOS return, max DD, turnover, win rate, Sortino/Calmar where present).

## Per-pair fills

| Pair | TODO-Ray stubs (before → after) | Smoke passes | KPI corrections vs stale history |
|---|---:|---:|---|
| `indpro_spy`     | 65 → 0 | 4 / 0 fail | None — history numbers (Sharpe 1.10 / OOS +7.7% / DD −8.1%) match `winner_summary.json` (1.1036 / +7.65% / −8.07%). Enriched design table with win rate 19.8% and breakeven-cost 50 bps from JSON. |
| `permit_spy`     | 37 → 0 | 3 / 0 fail | None — history numbers (Sharpe 1.45 / +22.7% / −19.4%) match JSON (1.4454 / +22.66% / −19.42%). Enriched with annual turnover 9.06. |
| `vix_vix3m_spy`  | 37 → 0 | 3 / 0 fail | None — history numbers (Sharpe 1.13 / +15.3% / −21.2% / turnover 23.3) match JSON (1.1295 / +15.31% / −21.15% / 23.34). Regime spread Q1 6.53 / Q4 −2.38 retained verbatim from legacy. |
| `umcsent_xlv`    | 51 → 0 | 6 / 0 fail | None — history numbers (Sharpe 1.02 / +11.9% / −10.9%) match JSON (1.0202 / +11.93% / −10.87%). Enriched with Sortino 2.01, Calmar 1.10, OOS vol 11.7%, 81 trades, win rate 37.0%, benchmark BH Sharpe 0.72 / DD −15.6%. |
| **Total** | **190 → 0** | **16 / 0 fail** | **No corrections required; 4 enrichments.** |

## TRADE_LOG_EXAMPLE_MD — per-pair crisis anchors

| Pair | Crisis anchor | Source file actually used | Broker-style CSV status |
|---|---|---|---|
| `indpro_spy`     | **2020 COVID** — rule in Cash 2019-03-31 → 2021-01-31 (672 days). Avoided full COVID drawdown, cost of caution is rally miss. | `results/indpro_spy/winner_trade_log.csv` | **NOT PRESENT.** Flagged for Vera/Ace. |
| `permit_spy`     | **2008 GFC** — Short 2008-06-30 → 2008-10-31 (+26.65% over 123 days); then whipsaw Long 2008-10-31 → 2009-01-31 (−13.76%). Honest on both the capture and the whipsaw. | `results/permit_spy/winner_trade_log.csv` | **NOT PRESENT.** Flagged for Vera/Ace. |
| `vix_vix3m_spy`  | **2020 COVID** — Cash 2020-01-24 → 2020-04-03 (70 days, avoided crash); Long 2020-04-03 → 2020-10-06 (+36.09% over 186 days). Archetypal L0 use case. | `results/vix_vix3m_spy/winner_trade_log.csv` | **NOT PRESENT.** Flagged for Vera/Ace. |
| `umcsent_xlv`    | **Feb 2020 COVID entry** — BUY XLV 2020-02-29 at $83.70 with signal rationale UMCSENT YoY = +7.676%, cum P&L +14.25% at entry. Honest case study of the 6-month-lag limit. | `results/umcsent_xlv/winner_trades_broker_style.csv` (the only present broker-style artefact) | **PRESENT** — shipped Wave 10H.2, commit 2c11046. |

**Gap flagged (not a regression):** Only `umcsent_xlv` has the canonical `winner_trades_broker_style.csv` APP-TL1 artefact. The other three pairs rely on the older `winner_trade_log.csv` columns (`entry_date, exit_date, direction, holding_days, trade_return_pct`) which lack broker-style fields (side/price/notional/cum P&L). Each pair's `TRADE_LOG_EXAMPLE_MD` explicitly notes this gap and asks Vera/Ace to promote the three non-umcsent pairs to the broker-style set in a future wave.

## What I did NOT touch

- `app/components/*` (template code — Ace's scope).
- TED pair configs (`sofr_ted_spy_config.py`, `dff_ted_spy_config.py`, `ted_spliced_spy_config.py`) — Ray-B's scope.
- Sample pages or Sample config (Wave 10I.B).
- Chart artefacts under `output/charts/`, pipeline scripts, SOPs, catalogs.

## Smoke logs

Produced at `app/_smoke_tests/loader_{pair_id}_20260423.log`:

- `loader_indpro_spy_20260423.log` — 4 passes.
- `loader_permit_spy_20260423.log` — 3 passes.
- `loader_vix_vix3m_spy_20260423.log` — 3 passes.
- `loader_umcsent_xlv_20260423.log` — 6 passes.

(Pass counts differ because AST-covered literal chart names differ per pair; permit and vix lack equity/drawdown/walk-forward charts on disk, which is the pre-existing data gap flagged in Ace's Part-1 handoff.)

## Editorial conventions applied

- **META-ELI5.** Every narrative section opens with a plain-English framing sentence; technical terms are introduced with context. Story pages emphasise "what it is / why care / what the data says" before any Greek letters.
- **Honest caveats.** Every `CAVEATS_MD` retains (or strengthens) the legacy honest-assessment tone. For `umcsent_xlv`, the direction-surprise framing is preserved verbatim because it is the defining feature of the pair.
- **Cross-pair voice consistency.** All four `SCOPE_NOTE` fields use the `*Scope discipline (ECON-SD).*` idiom. All four `sample_period_note` fields follow the same Full / In-sample / Out-of-sample pattern.
- **No fabricated numbers.** Every numeric claim in prose is either (a) from the legacy page, (b) from `winner_summary.json`, or (c) from direct inspection of `winner_trade_log.csv` / `winner_trades_broker_style.csv`.

## Next-step suggestions (for Lead discretion)

1. **Broker-style CSV gap** — 3 of 4 non-TED pairs (indpro, permit, vix) lack `winner_trades_broker_style.csv`. Dispatch to Vera (or Dana) to generate from existing `winner_trade_log.csv` + pipeline signals.
2. **Performance-tab chart gap** — `permit_spy` and `vix_vix3m_spy` have no `equity_curves`, `drawdown`, or `walk_forward` charts on disk. Ace's Part-1 handoff flagged this as pre-existing; Vera would be the owner if prioritised.
3. **Chart-filename drift** — `indpro_spy`, `permit_spy`, `vix_vix3m_spy` retain legacy pair-id-prefixed chart filenames (`indpro_spy_hero.json` rather than bare `hero.json`). `umcsent_xlv` is canonical. A cleanup wave could rename these and drop the chart-name attrs from the configs.

## Commit

Single commit with pair configs + this handoff + PWS/status-board updates. No SOP changes required for this narrative port.
