# Handoff — Ray → Lead / Quincy (Wave 10I.A Part 3b: TED variants narrative port)

**Author:** Research Ray (research-ray)
**Date:** 2026-04-23
**Wave:** 10I.A Part 3b
**Governing rules:** RES-NR1 (narrative authoring), APP-PT1 (template abstraction — content-only writes)
**Scope:** Replace all 111 TODO-Ray stubs across 3 TED-variant pair configs with pair-specific narrative prose.

---

## Summary

- **3 configs fully narrative-populated:** `sofr_ted_spy_config.py`, `dff_ted_spy_config.py`, `ted_spliced_spy_config.py`.
- **111 / 111 TODO-Ray stubs replaced** (37 per pair), zero remaining (`grep "TODO Ray" app/pair_configs/{sofr,dff,ted_spliced}_ted_spy_config.py` returns no matches).
- **Smoke tests green:** all 3 pairs `passes=3 failures=0` via `app/_smoke_tests/smoke_loader.py`.
- **Source content:** retrieved via `git show a9d493e~1:app/pages/6_ted_variants_{story,evidence,strategy,methodology}.py` per Ace's handoff instructions; distributed pair-specifically per Ace's composite→per-pair mapping table.
- **Zero scope bleed:** touched only the 3 TED configs. Did not touch `page_templates.py`, pages, components, scripts, results, or SOPs.

## Per-pair stub fill count

| Pair | Stubs filled | Remaining |
|---|---:|---:|
| `sofr_ted_spy` | 37 | 0 |
| `dff_ted_spy` | 37 | 0 |
| `ted_spliced_spy` | 37 | 0 |
| **Total** | **111** | **0** |

## KPI verification vs `winner_summary.json`

All prose KPIs cross-checked against each pair's `results/{pair_id}/winner_summary.json`:

| Pair | Signal | Threshold | Strategy | Lead | OOS Sharpe | OOS Return | Max DD | Turnover |
|---|---|---|---|---:|---:|---:|---:|---:|
| `sofr_ted_spy` | Spread 63-Day ROC | T1_p25 | Long/Cash (P1) | 10d | **1.89** | +8.15% | −3.58% | 23.4 |
| `dff_ted_spy` | Spread 21-Day ROC | T1_p25 | Signal Strength (P2) | 5d | **0.97** | +11.04% | −14.71% | 10.0 |
| `ted_spliced_spy` | Spread 21-Day ROC | T1_p25 | Signal Strength (P2) | 1d | **1.19** | +13.42% | −12.78% | 14.2 |

Narrative-cited numbers match JSON canon. The memory index's earlier note ("SOFR 1.89, DFF 0.97, Spliced 1.19") is confirmed accurate.

## Trade-example citations (per-variant, from each `winner_trade_log.csv`)

All 3 pairs have populated `winner_trade_log.csv`. No trade-example gaps to flag.

| Pair | Episode cited | Entry → Exit | Direction | Return | Notes |
|---|---|---|---|---:|---|
| `sofr_ted_spy` | Post-COVID recovery | 2020-05-12 → 2020-07-01 | Long | **+8.80%** | Largest single trade in log (n=188). March-2020 spike itself produced a −9.3% counter-cyclical cost (trade id 46). |
| `dff_ted_spy` | GFC rally (Oct-2008) | 2008-10-10 → 2008-10-13 | Long | **+10.50%** | Largest single trade in log (n=7,499). Demonstrates the counter-cyclical mechanism during GFC. |
| `ted_spliced_spy` | GFC rally (late-Oct-2008) | 2008-10-27 → 2008-10-28 | Long | **+10.09%** | Largest single trade in log (n=7,493). Pre-2022 → uses authentic LIBOR-based TEDRATE data, not the spliced extension. |

## Smoke test results

| Pair | passes | failures | Log |
|---|---:|---:|---|
| `sofr_ted_spy` | 3 | 0 | `app/_smoke_tests/loader_sofr_ted_spy_20260423.log` |
| `dff_ted_spy` | 3 | 0 | `app/_smoke_tests/loader_dff_ted_spy_20260423.log` |
| `ted_spliced_spy` | 3 | 0 | `app/_smoke_tests/loader_ted_spliced_spy_20260423.log` |

## Narrative-distribution choices (how I honoured the "don't conflate variants" instruction)

- **Variant A (SOFR)** — framed as the *modern purist, short sample* variant. Caveats emphasize the ~2,000-obs sample size, one-regime concern, wide confidence intervals around the 1.89 Sharpe. Repo-collateral mechanism (vs credit) highlighted. Crisis-trade citation is COVID-era only (no GFC data available).
- **Variant B (DFF)** — framed as the *longest-history, conservative* variant. Caveats emphasize DFF being a *proxy* (not the original LIBOR-TED), overlap correlation r = +0.63 against TEDRATE as the justification. Crisis-trade citation is GFC (authentic long-history evidence). "RoC-dominates-level" point highlighted with regime-shift explanation (zero-rate vs pre-GFC Fed Funds levels).
- **Variant C (Spliced)** — framed as the *extended-history continuity* variant. Structural-assumption caveat (affine `scale × + shift` calibration, and its OOS-validity risk) is given its own section. Crisis-trade citation is GFC using the authentic pre-splice TEDRATE portion of the series — explicitly noted. Strongest impulse-response evidence of the three is claimed, consistent with the richer crisis content of the spliced sample.

All three thesis paragraphs differ from each other in substance, not just phrasing. Cross-reference sentences appear in `WHERE_THIS_FITS` and `NARRATIVE_SECTION_2` to orient readers comparing siblings on the landing page.

## Flags for downstream agents

### Quincy (cloud verify)

All 3 exploded TED surfaces now carry full narrative; previously visible TODO-Ray placeholder strings should be gone. Cloud verify should check:
- `pages/6_sofr_ted_spy_{story,evidence,strategy,methodology}.py` — renders SOFR-specific prose, no TODO strings.
- `pages/11_dff_ted_spy_{...}.py` — DFF-specific prose.
- `pages/12_ted_spliced_spy_{...}.py` — Spliced-specific prose.
- Landing page: 3 TED cards resolve to their respective story pages.
- Sidebar: 3 distinct TED entries.

### Evan / Vera (chart gaps — already tracked)

Strategy pages still carry "chart pending" placeholders for `equity_curves`, `drawdown`, `walk_forward` on all 3 TED variants. Tracked under `BL-CHART-GAPS-LEGACY`. I wrote explicit "Missing artefacts" bullets into each pair's `CAVEATS_MD` so end-users see honest framing pending backfill.

### Lead

No SOP gaps encountered; RES-NR1 discipline (pair-specific prose, verified KPIs, crisis-trade citations from actual logs) applied cleanly. No blocking issues for Quincy's cloud verify.

## Scope-discipline confirmations

- Wrote only to: 3 pair-config files, this handoff, and Ray PWS + team status-board.
- Did **not** touch `page_templates.py`, any page, any component, any script, any result artifact.
- Did **not** re-create the deleted composite files.
- Did **not** touch Ray-A's 4 non-TED configs.
- Used `git show a9d493e~1:…` (Ace's prescribed retrieval path) for composite source prose; all port is pair-specific, no verbatim triple-paraphrase.

## META-AM confirmation

No ad-hoc / manual fixes or workarounds. Narrative authoring is the legitimate Ray role under RES-NR1; configs are the designated surface for pair-specific prose under APP-PT1. No patches, no hot-fixes, no bypasses.
