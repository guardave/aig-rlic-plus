# Evan Handoff — pair `phlxsox_spy` (SOX → SPY), daily, Mode 1

**From:** Econ Evan · **To:** Lead Lesandro (+ Vera, Ray) · **Date:** 2026-06-19
**Branch:** `pair260619_phlxsox_spy`

## TL;DR verdict (the central honesty challenge)
- **Contemporaneous daily corr(SOX, SPY) = 0.709 → CO-MOVEMENT (shared beta), NOT a forecast.** Established as the trap up front and confirmed in CCF lag-0 (0.69).
- **Granger is BIDIRECTIONAL, not a clean SOX→SPY lead.** Toda-Yamamoto SOX→SPY significant at every tested lag {1,2,3,5,10,21}; SPY→SOX *also* significant at every lag. This is **feedback** (two high-beta equity series push each other), not a one-way semiconductor lead. Pre-whitened CCF shows significant mass on BOTH the lead (lag>0) and lag (lag<0) sides.
- **Does the SOX signal beat SPY's OWN momentum?** On the headline OOS Sharpe, *yes but fragile*: winner 1.57 vs SPY-own-momentum 0.83 vs B&H 0.82. **HOWEVER the win is an overfit artifact, not a validated edge** (see flags). Honest read: there is a weak, genuine *predictive* relationship (lagged relative-strength momentum predicts forward SPY with t-stats 5–9 but R²~1%), and it adds marginally over SPY-own-momentum in a HAC local projection (p=0.033 at 21d). But the tournament winner's risk-adjusted advantage is **not robust**.

## Winner spec
`phlxsox_rs_mom6m / T2_roll_p75 / P1_long_cash (pro) / L63 / LB63`
- signal_column = `sox_spy_ratio_mom_6m_pct` (relative-strength, partials out common beta) — exists in `signals_20260619.parquet` ✔
- Rule: long SPY when lagged (63 td) SOX/SPY 6-month relative-strength momentum > rolling-75th-pct (LB63); else cash. threshold_rule=`gt`, latest threshold_value=30.68.
- OOS (2021-06-11 → 2026-06-17, 1260 td): **Sharpe 1.57**, ann ret 13.0%, max DD **-9.7%**.
- Benchmarks: **B&H Sharpe 0.82** (DD -24.5%); **SPY-own-momentum Sharpe 0.83** (DD -23.7%). beats_buy_and_hold=True, beats_spy_own_momentum=True.
- Direction: procyclical (consistent with Ray/Dana prior). Tournament: 6760 strategy combos, **4607 valid**; +2 benchmark rows (BENCHMARK buy&hold + SPY_OWN_MOMENTUM), both valid=False, excluded from combo counts (ECON-T4).

## Recompute guardrail (umcsent precedent)
PASS, twice. (1) In-pipeline ECON-SR1 reconciliation on the native series. (2) Independent POST-WRITE guardrail: re-read winner_summary, re-read signals parquet (confirmed signal_column present), re-read strategy_returns CSV, recomputed OOS Sharpe with the encoded rule = **1.5700 vs headline 1.5700, |diff|=0.0000 ≤ 0.03**. Encoding (signal/threshold/lead/lookback/orientation) faithfully reflects the selected tournament row.

## Overfitting flags (why confidence = LOW, evidence_status = found_in_search)
- **IS Sharpe 0.10 vs OOS 1.57** — huge gap; the OOS window 2021–2026 was a strong-semis bull, a favorable draw.
- **Median valid combo OOS Sharpe = 0.674, BELOW B&H 0.819** — the search mostly found losers; the winner is plausibly the luckiest of thousands of tries.
- **Win-rate 0.20**, and the winner **LOST in every pre-OOS crisis** (Dot-Com -40%, GFC -43%, COVID -17%) per stress_tests.csv.
- Winner bootstrap p = 0.041 (marginally significant vs resampled B&H); rolling-corr sign stability 0.42 (`sign_unstable`); CP1 durability `conditionally_durable` (only 1 OOS episode evaluable). No structural break flagged (sup-F p=0.665).

## SOX-leads-or-not (for Ray's narrative — reconcile carefully)
**Not a clean lead — feedback.** The honest framing: semiconductors and the broad market co-move ~71% intraday from shared beta; Granger runs both ways; the only *forecast* content is a weak relative-strength momentum effect (small R², survives over SPY-own-momentum only marginally). Do NOT narrate "SOX predicts SPY" as a strong leading-indicator story. Narrate: high co-movement, bidirectional feedback, a fragile search-found relative-strength tilt that beat benchmarks in one bull window but failed in every prior crisis.

## evidence_status
`found_in_search` (schema-valid). plain_english spells out the co-movement-vs-lead distinction, the SPY-own-momentum comparison, the bull-window/crisis-loss caveat, and the bidirectional-feedback point. next_step = ECON-FE1 final exam on an untouched window.

## Charts Vera needs (per-method artifacts, all `ready`)
| method | result_file | expected_chart |
|---|---|---|
| Pre-whitened CCF | `core_models_20260619/ccf_prewhitened.csv` | CCF stem plot lags -20..+20 with ±CI bands (emphasize symmetric/bidirectional mass) |
| Toda-Yamamoto Granger | `core_models_20260619/granger_causality.csv` + `granger_by_lag.csv` | F-stat by lag, BOTH directions side-by-side |
| Incremental-edge | `core_models_20260619/incremental_edge_vs_spy_momentum.csv` | rel-strength coef + incremental R² over SPY-own-momentum |
| Forward correlations | `core_models_20260619/correlations.csv` | predictive (forward) corr by horizon — label clearly NOT contemporaneous |
| Quartile returns | `regime_quartile_returns.csv` | Q1–Q4 ann SPY return by lagged-rel-strength quartile |
| Equity curve | `strategy_returns_20260619.csv` | winner vs B&H **vs SPY-own-momentum** (3-line) — the SPY-own-momentum line is essential context |
| Stress | `tournament_validation_20260619/stress_tests.csv` | winner vs B&H per crisis (shows winner losing pre-OOS) |
| HMM | `core_models_20260619/hmm_states.parquet` | regime overlay |

## Reconciliation Ray must narrate
1. 0.709 corr = co-movement, not edge. 2. Bidirectional Granger = feedback, not lead. 3. Winner beats both benchmarks on headline Sharpe BUT IS 0.10 / median-below-BH / crisis losses = overfit; treat as search-found. 4. Relative-strength is the only signal family with even marginal incremental forecast content.

## Files committed under `results/phlxsox_spy/`
Full ECON artifact set (tournament_results+manifest, tournament_winner, winner_summary, both trade logs, strategy_returns+meta, oos_split_record, evidence_status, granger_by_lag, rolling_correlation, regime_quartile_returns+manifest, structural_break, subperiod_sharpe, signals+manifest, signal_scope, core_models_20260619/ [13 method files], design_note, kpis, analyst_suggestions, interpretation_metadata updated). winner_summary + evidence_status + signal_scope + interpretation_metadata + analyst_suggestions all schema-valid (exit 0). signal_code `phlxsox_rs_mom6m` appended to registry (schema-conforming).
Producer: `scripts/pair_pipeline_phlxsox_spy.py`.
