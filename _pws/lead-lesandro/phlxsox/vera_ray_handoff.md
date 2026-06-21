# Vera + Ray Handoff — pair `phlxsox_spy` (SOX → SPY), Mode 1 daily

**From:** Viz Vera (charts) + Research Ray (narrative)
**To:** Lead Lesandro (checker) + Ace (portal)
**Date:** 2026-06-19 · **Branch:** `pair260619_phlxsox_spy`

## Framing (binding honesty mandates — ALL covered)
This is a FRAGILE, honest pair. Charts + narrative do NOT oversell:
1. **Signal is SOX/SPY RELATIVE STRENGTH, not raw SOX** — 0.709 daily corr is co-movement (shared beta); the ratio partials it out. Covered in: hero (ratio not raw SOX), correlation_heatmap (forward corrs tiny vs 0.709 same-day), Story §"Why Raw Semiconductors Are Not the Signal" + expander.
2. **Causality is BIDIRECTIONAL feedback, not a clean lead** — Toda-Yamamoto sig BOTH directions all lags. Covered in: granger_f_by_lag (BOTH directions, reverse taller at short lags, title "Feedback, Not a Clean SOX Lead"), ccf_prewhitened (mass on both sides), Story §"Feedback, Not a Clean Lead", Evidence §Lead-Lag.
3. **Edge over SPY-own-momentum is MARGINAL/horizon-dependent** — adds 21d p=0.033, NOT 63d p=0.075, incremental R²~1%. Covered in: incremental_edge chart (dedicated), equity_curves 3-line, Evidence §"Does It Beat SPY's Own Momentum?".
4. **Fragility prominent** — IS 0.10 vs OOS 1.57 (favorable semis bull); median valid combo 0.67 < B&H 0.82; win-rate 0.20; LOST every pre-OOS crisis; bootstrap p=0.041; found_in_search; confidence LOW. Covered in: tournament_sharpe_dist (median below B&H), subperiod_sharpe (crisis losses), Story headline + "Why is confidence low?" expander, Strategy §"The Edge and Its Fragility".

## VERA — charts produced
Path: `output/charts/phlxsox_spy/plotly/` — 20 charts as Plotly JSON + `_meta.json` sidecars + `_perceptual_check_*.png`, all `disposition: consumed`.

`hero, regime_stats, correlation_heatmap, ccf_prewhitened, granger_f_by_lag, incremental_edge, local_projections, quantile_coef, hmm_regime_probs, equity_curves, drawdown, tournament_scatter, tournament_sharpe_dist, rolling_correlation, structural_break, subperiod_sharpe, history_zoom_{dotcom,gfc,covid,inflation_2022}`

Skip sidecars (VIZ-CP1-G): `chart_skip_rolling_sharpe_cp.json`, `chart_skip_rolling_granger.json` — ECON-CP2 durability artifacts intentionally absent (structural_break JSON `cp2_note`: "CP2 skipped — regime_story not set").

### Two binding chart requirements — CONFIRMED
- **equity_curves is a 3-LINE chart**: winner (vermillion, Sharpe 1.57) vs Buy&Hold SPY (grey dash, 0.82) vs SPY-own-momentum (blue dot, 0.83). The SPY-own-momentum benchmark line was reconstructed deterministically from Evan's saved SPY daily returns (long when trailing 63d SPY return > 0, lead 1d) and VERIFIED against `winner_summary.spy_own_momentum_sharpe`: reconstructed 0.826 vs 0.826, |diff|=0.000 (PASS, in `equity_curves_meta.json.reconciliation`). Perceptual PNG inspected — 3 lines clearly distinct.
- **granger_f_by_lag shows BOTH directions**: SOX→SPY (vermillion) AND SPY→SOX (blue) both clear the 5% critical line at every lag; reverse is taller at short lags. Title "Causality Runs BOTH Ways — Feedback, Not a Clean SOX Lead". Perceptual PNG inspected — both-direction grouped bars render correctly.

### Generator + gates
- Producer: `scripts/generate_charts_phlxsox_spy.py` (template = petrol_inv_spy generator).
- In-process gates all PASS: VIZ-IC1 (palette + one-$), VIZ-NBER1 (shading on all 8 calendar-time charts), VIZ-DP1 (dual-panel axis assignment — all history_zoom + regime + LP), perceptual PNGs written, `_meta.json` with disposition + reconciliation.
- VIZ-DP1 explicitly verified on the 3-line equity curve and both-direction Granger (single-panel; no axis-assignment risk).

## RAY — narrative produced
Path: `docs/portal_narrative_phlxsox_spy_20260619.md` (4 pages: Story/Evidence/Strategy/Methodology + glossary + references).

- **Frontmatter (RES-17/META-CF):** validates against `narrative_frontmatter.schema.json` (exit 0). headline_template A. direction_asserted=`procyclical` (matches `winner_summary.json.direction`).
- **chart_refs:** all 20 resolve on disk (0 missing).
- **glossary_terms:** all 19 present in `docs/portal_glossary.json` — added 9 missing terms this handoff (Relative strength, Co-movement, Market beta, Momentum, CCF, Toda-Yamamoto, Procyclical, Overfitting, Feedback).
- **RES-JFU:** every term/abbrev long-form + (abbrev) + plain gloss on first use (SR, MDD, BH, OOS/IS, GC, CCF, LP, QR, TE, HMM, beta, relative strength).
- **RES-11/RES-18:** Story headline-first, Template A, metric/OOS span read from winner_summary + oos_split_record (not hand-typed).
- **RES-20 episode triad:** dotcom=long_lead, covid=coincident, gfc=failure_case, inflation_2022=confirmer. (SOX/Cross-Asset uses the events-registry slugs dotcom/gfc/covid/inflation_2022 — same as brief.)
- **RES-NR1:** target_symbol=spy; narrative references "SPY" throughout, no foreign instrument names. Indicator = PHLX Semiconductor Index (SOX). VERIFIED.
- **RES-VS:** only canonical status label used (`Available`).
- **interpretation_metadata.json** ray fields set + schema-valid (exit 0): strategy_objective=`max_sharpe`, expected_direction=`procyclical`, mechanism, caveats (8-item array), narrative_summary.

## Notes for Ace (display_names gap)
- `app/components/display_names.py` has NO `phlxsox_spy` entry. Proposed canonical forms (used in charts/narrative): indicator long = "PHLX Semiconductor Index", short = "SOX"; relative-strength label = "SOX/SPY relative strength"; target = "SPY". Ace to add the entry when wiring the pair_config.
- `HISTORY_ZOOM_EPISODES` for the pair config (RES-HZE1): slugs dotcom/gfc/covid/inflation_2022; narratives/captions in the Story §"What History Shows" and each `history_zoom_*_meta.json` caption.
- Strategy page needs the dual trade-log download (winner_trades_broker_style.csv + winner_trade_log.csv); "How to Read the Trade Log" subsection is written.

## BLOCKED
None.
