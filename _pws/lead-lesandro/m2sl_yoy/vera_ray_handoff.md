# Vera + Ray Handoff — m2sl_yoy_spy (M2 Money Supply YoY → SPY)

**Stage:** Charts + 4-section narrative (Mode 1, stage 3). Branch `pair260619_m2sl_yoy_spy`.
**Date:** 2026-06-19. Roles: Viz Vera (charts) + Research Ray (narrative). Manager + sole checker: Lead Lesandro.

## ============ VERA (charts) ============

Producer: `scripts/generate_charts_m2sl_yoy_spy.py` (adapted from the petrol_inv_spy template).
Output dir: `output/charts/m2sl_yoy_spy/plotly/`. Palette `okabe_ito_2026` (VIZ-V11).

**20 charts produced** (all `.json` + `_meta.json` sidecar + `_perceptual_check_*.png`, disposition=consumed):

| Chart | Note |
|-------|------|
| hero | M2 YoY level vs SPY; 0% line marked; **2020-21 surge (~27%) and first-ever 2022-23 YoY contraction annotated**; caption clarifies the winner trades the acceleration transform, not the level |
| equity_curves | Winner vs B&H, OOS shaded from 2018-01; title carries the "OOS dominated by 2020/2022 regime" caveat |
| drawdown | -4.0% vs -23.9% OOS; titled "episode-shaped" |
| correlation_heatmap | weak forward correlations |
| ccf_prewhitened | no clean forward lead |
| **granger_f_by_lag** | **BOTH directions shown. REVERSE (SPY→M2, dark blue) is visually dominant and clears the 5% line at lags [1,2,3,4,5,8]; FORWARD (M2→SPY, pale blue) clears at NONE.** Title: "Causality Runs in REVERSE: The Market Moves First, M2 Responds" |
| hmm_regime_probs | high-variance regime pins ~1.0 through 2020-21 surge (manifest assertion verified) |
| local_projections | forward n.s. at all horizons (min p≈0.62) — corroborates reverse-only |
| quantile_coef | most negative in low return quantiles |
| transfer_entropy | forward p≈0.20 n.s.; reverse p≈0.03 sig — reinforces reverse-only |
| regime_stats | LEVEL quartiles; **Q4 (high money growth) is RISKIEST: Sharpe 0.53, -47% DD**; framed separate from acceleration winner |
| tournament_scatter | 4,720 combos (3,369 valid) |
| tournament_sharpe_dist | winner=max of 3,369; median below B&H; bootstrap p=0.025 disclosed |
| rolling_correlation | sign stability 0.50, moderately-stable |
| structural_break | Quandt-Andrews, no break (p=0.28) |
| subperiod_sharpe | only COVID evaluable in 2018+ OOS; others insufficient_data → ties to conditionally_durable |
| history_zoom_{dotcom,gfc,covid,inflation_2022} | dual-panel, 0% line on M2 panel, NBER both panels where applicable |

Plus `chart_skip_{rolling_sharpe_cp,rolling_granger}.json` (CP2 absent: regime_story=false in signal_scope.json).

**Both-direction Granger CONFIRMED** (per binding mandate): reverse trace is primary/dominant; forward trace present but n.s. at every lag. Reconciliation block in `granger_f_by_lag_meta.json`: `{forward_significant_lags: [], reverse_significant_lags: [1,2,3,4,5,8], verdict: "reverse_only"}`.

**Gates (all PASS, in-process):**
- VIZ-IC1 (palette + VIZ-TX1 one-$): PASS on all 20.
- VIZ-NBER1: PASS on all calendar-time charts (hero, equity_curves, drawdown, hmm_regime_probs, rolling_correlation, structural_break, history_zoom_{dotcom,gfc,covid}). history_zoom_inflation_2022 legitimately carries 0 NBER rects (no recession in window) — `nber_required=False`.
- **VIZ-DP1 (axis discipline, binding):** PASS — all dual-panel charts (regime_stats, local_projections, 4 history_zoom) have correct x/x2/y/y2 assignment; verified explicitly. inflation_2022 spot-checked: top trace x/y, bottom trace x2/y2.
- Perceptual PNGs rendered for all 20 (VIZ-CV1). Hero and Granger visually inspected — surge/contraction/0%-line and reverse-dominance render correctly.

**VIZ-HZE1 gate — m2sl_yoy_spy:** Required slugs (macro/activity-adjacent): [dotcom, gfc, covid, inflation_2022]. Coverage: M2 data spans 1993-2026 → all four PASS. Disk check: all four `history_zoom_*.json` present. Gate verdict: **PASS**.

**Ace notes:** `app/components/display_names.py` has no `m2sl_yoy_spy` entry yet (same gap class flagged on petrol). Proposed canonical forms: indicator long="M2 Money Supply (YoY growth)", short="M2 YoY growth"; target="SPY". Chart filenames are bare keys matching `load_plotly_chart("{chart_type}", pair_id="m2sl_yoy_spy")`.

## ============ RAY (narrative) ============

Narrative: **`docs/portal_narrative_m2sl_yoy_spy_20260619.md`** (4 sections: Story, Evidence, Strategy, Methodology).
Frontmatter validates: `scripts/validate_schema.py --schema docs/schemas/narrative_frontmatter.schema.json` → **PASS**.
Headline template: **A** (metric-first). `direction_asserted: procyclical` matches `winner_summary.json.direction`.

interpretation_metadata.json — Ray-owned fields filled: `mechanism`, `caveats`, `narrative_summary` (strategy_objective=max_sharpe and expected_direction=procyclical already set). last_updated_by=ray.

**Honesty reconciliation (Lead mandate) — ALL FOUR points covered:**
1. **Acceleration, not level** — Story §"Acceleration, Not Level" + expander "Why acceleration, not the level?". Explains plainly that "is money growth speeding up or slowing down?" beat "is money growth high or low?"; the level quartiles (Evidence) show high money growth is the riskiest regime, kept as a separate story.
2. **Lead with reverse causality** — Story §"The Honest Headline: Causality Runs in Reverse" is the second section, before mechanism. States M2→SPY n.s. at all lags; SPY→M2 sig at [1,2,3,4,5,8]; M2 is coincident/lagging; "not evidence that M2 leads equities." Repeated in Evidence §Lead-Lag and Methodology §Limitations.
3. **Mechanism as HYPOTHESIS** — explicitly labeled hypothesis in Story §Acceleration and interpretation_metadata.mechanism; references 2020-21 surge + 2022-23 contraction as vivid but regime-concentrated episodes.
4. **Fragility caveats prominent** — Strategy §"Tradeoff and Fragility" carries bootstrap p=0.025 (search-selected), found_in_search (no final exam), confidence LOW, conditionally_durable, OOS dominated by 2020/2022 regime, drawdown win "episode-shaped". Plus expander "Why is confidence low?".

**RES-20 lagging-pair variant applied:** reverse-only causality → no `long_lead` episode invented. Triad = COVID (coincident), GFC + inflation_2022 (failure_case), Dot-Com (confirmer). Documented in frontmatter `selection_rationale_note` citing the Granger artifact.

**RES-JFU:** YoY, OOS, Granger, bps, ETF, API, HMM, LP, CCF, TE all long-form + (abbrev) + gloss on first use.
**RES-NR1 check:** target_symbol=SPY; narrative references verified — only "SPY" and "M2/M2SL"; zero cross-pair instrument leaks (grep clean).
**RES-VS:** status labels used = {Available, Validated} — both canonical.
**Glossary:** added 3 terms to `docs/portal_glossary.json` (Ray-owned): "Money supply (M2)", "Money-growth acceleration", "Pro-cyclical". JSON re-validated.

**CONFIG-PARSE-CHECK:** N/A this cycle — no `app/pair_configs/m2sl_yoy_spy_config.py` authored (Ace builds the config; HISTORY_ZOOM_EPISODES translation from frontmatter `historical_episodes_referenced` is Ace's next-stage input — frontmatter triad provided).

## BLOCKED
- None blocking. Carry-forward (pre-existing, not this stage): Evan flagged `docs/schemas/signal_code_registry.json` fails its own schema at HEAD due to legacy ism_services entries — separate cleanup wave.
