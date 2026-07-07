# Statistical Methods — Example-Chart Fact Sheets

**Author:** Econ Evan · **Branch:** `feat260704_method_examples` · **Date:** 2026-07-04

Single source of truth for the Statistical Methods reference page example charts. Every number below is **decoded from the actual chart JSON** on disk (base64 typed-array decode, same path as `app/components/charts.py`), not recalled. Vera anchors ①②③ from the callout specs; Ray cites only from the "citable numbers" lists.

**Chart-slug reminder:** `example.chart` must name a slug that EXISTS in `output/charts/{pair}/plotly/{chart}.json`. All chosen slugs below were confirmed present.

---

## Pair-choice summary (15 methods)

| # | slug | chosen pair | chart slug | current pair | CHANGED? |
|---|------|-------------|-----------|--------------|----------|
| 1 | correlation_battery | hy_ig_spy | correlation_heatmap | hy_ig_spy | keep |
| 2 | lead_correlation | hy_ig_spy | correlations_lead_view | hy_ig_spy | keep (see flag) |
| 3 | lead_tournament | hy_ig_spy | lead_sharpe_distribution | hy_ig_spy | keep |
| 4 | granger_causality | **phlxsox_spy** | granger_f_by_lag | hy_ig_spy | **CHANGED** |
| 5 | prewhitened_ccf | gold_copper_xli | ccf_prewhitened | gold_copper_xli | keep (see flag) |
| 6 | regime_quartile | hy_ig_spy | regime_quartile_returns | hy_ig_spy | keep |
| 7 | hmm_regime | hy_ig_spy | hmm_regime_probs | hy_ig_spy | keep |
| 8 | local_projections | hy_ig_spy | local_projections | hy_ig_spy | keep |
| 9 | quantile_regression | hy_ig_spy | quantile_regression | hy_ig_spy | keep |
| 10 | transfer_entropy | **gold_copper_xli** | transfer_entropy | hy_ig_spy | **CHANGED** |
| 11 | random_forest_importance | indpro_spy | rf_importance | indpro_spy | keep (only pair with chart) |
| 12 | walk_forward | hy_ig_spy | walk_forward | hy_ig_spy | keep |
| 13 | bootstrap_significance | None | None | None | keep (no chart exists) |
| 14 | subperiod_durability | **gold_copper_xli** | subperiod_sharpe | hy_ig_spy | **CHANGED** |
| 15 | structural_break_cointegration | **gold_copper_xli** | structural_break | hy_ig_spy | **CHANGED** |

**4 changed:** granger_causality, transfer_entropy, subperiod_durability, structural_break_cointegration — each moved OFF a null/concentrated example ONTO a clear positive result.

**Flags for Lead (no clean positive, or caveat):**
- **prewhitened_ccf** — NO pair shows a clean significant *forward-lag* spike. The only dramatic spikes are at **lag 0 (contemporaneous, not a lead)**. Decision needed (see §5).
- **granger_causality (phlxsox)** — forward SOX→SPY IS significant at every lag, but the **reverse (SPY→SOX) is also significant** → it is a feedback pair, not a one-way lead. Honest and still a strong positive "bars clear the line" teaching chart, but Ray must state the bidirectionality.
- **lead_correlation (hy_ig)** — the chart is a **heatmap** (signals × leads), but the current METHODS caption describes a single "curve." Form mismatch — Ray/Vera should phrase callouts as "read across a row" (see §2).

---

## 1. correlation_battery — Pearson Correlation Battery
**Chosen:** hy_ig_spy / `correlation_heatmap` (KEEP). Pairs with this chart: busloans, gold_copper_xli, hy_ig, ism_services, m2sl_yoy, nhs, petrol_inv, phlxsox, t10y3m.
**Why this pair:** readable 20×6 = 120-cell heatmap with a single visibly-deepest cell AND a broad pale near-zero majority — the "even the strongest is modest" lesson. Grid is contiguous (1D…252D), labels legible. No better heatmap found; keep the pilot.

**Verified facts (decoded):** matrix shape (20, 6) = 120 cells. Min z = **−0.3719** at (`bank_smallcap_ratio`, 252D). Max z = **+0.2077** at (`bbb_ig_spread_pct`, 252D). Cells with |r| < 0.05: **86 of 120** (confirmed by count). r² of strongest = 0.372² = **0.138 ≈ 14%**.

**Callout specs (①②③):**
- ① Deepest cell → row `bank_smallcap_ratio`, column **252D**, value **r = −0.37** → strongest single link, still only r² ≈ 14%.
- ② The broad pale band → **86 of 120 cells sit below |r| = 0.05** → magnitude is easy to over-read.
- ③ Colour = sign (blue negative/countercyclical, red positive/procyclical); the 252D column flips from blue at top (`bank_smallcap_ratio` −0.37) to red (`bbb_ig_spread_pct` +0.21) → read sign before magnitude.

**Citable numbers:** strongest r = −0.37 (r²≈14%, ~86% unexplained); 86/120 below |0.05|; 120 total cells; strongest positive r = +0.21; horizons 1D/5D/21D/63D/126D/252D; 20 signal transforms.

---

## 2. lead_correlation — Rolling / Lead Correlation
**Chosen:** hy_ig_spy / `correlations_lead_view` (KEEP).
**Why this pair:** current pilot; shows the L0…L12 lead axis with a legible winner-signal peak. **FLAG:** chart is a HEATMAP (10 signals × 13 leads), not a single curve — caption/annotations should say "read across a row to find where that signal's correlation peaks."

**Verified facts (decoded):** z shape (10, 13); leads L0…L12; 10 signal rows. Strongest single cell by |r| = **−0.222** at (`hy_ig_mom_21d`, **L2**). Winner-signal row `hmm_2state_prob_stress` across L0…L12 = [−0.007, −0.005, 0.021, −0.011, −0.029, 0.040, **−0.137**, −0.015, −0.031, −0.071, −0.063, −0.049, −0.010] → peaks at **L6, r = −0.137**. (Daily-executed pair; monthly L0…L12 axis is a comparability view, per sub-title.)

**Callout specs (①②③):**
- ① Strongest cell overall → `hy_ig_mom_21d` at **L2**, r = **−0.222** → where short-momentum lead is tightest.
- ② Winner-signal row `hmm_2state_prob_stress` → correlation deepens to **−0.137 at L6** then fades → a single-lead peak, not a broad plateau (treat with caution).
- ③ Sign is negative across most of the winner row → countercyclical lead; the monthly axis is a comparability diagnostic, not the traded (daily, L0) latency.

**Citable numbers:** strongest cell −0.222 (mom_21d, L2); winner row peak −0.137 (L6); 13 leads L0–L12; 10 signals.

---

## 3. lead_tournament — Lead Tournament
**Chosen:** hy_ig_spy / `lead_sharpe_distribution` (KEEP). (Alternative with a more dramatic spike: vix_vix3m_spy, best 1.87 at L3.)
**Why this pair:** pilot; has the full furniture — best-OOS-Sharpe bars per lead, a grey p25–p75 IQR band + median dots for valid combos, and the dashed B&H line. Clean teaching of "trust a wide band over a lone spike; every point is search-conditioned."

**Verified facts (decoded):** best-OOS-Sharpe per lead L0…L12 = [1.420, **1.439**, 1.321, 1.089, 1.213, 1.270, 1.170, 1.120, 1.283, 1.304, 1.260, 1.362, 1.144]. Peak = **1.44 at L1** (`hy_ig_roc_21d × P2`, per sub-title). Median-of-valid-combos per lead ≈ 0.69–0.78 (e.g. L1 = 0.708). B&H SPY OOS Sharpe (dashed) = **0.8129** (sub-title rounds to 0.81). Published daily winner = 1.41 at L0 (off this monthly axis).

**Callout specs (①②③):**
- ① Tallest bar → **L1, best OOS Sharpe 1.44** → the single lucky combo (`hy_ig_roc_21d × P2`).
- ② Grey IQR band + median (~0.70–0.78 across leads) sits far below the best bars → the typical combo is mediocre; the max is optimistic.
- ③ Dashed B&H line at **0.81** → best-at-each-lead clears B&H everywhere, but every bar is the max over thousands of combos → hypothesis, not confirmed edge.

**Citable numbers:** best 1.44 at L1; B&H 0.81; median-combo ~0.70–0.78; range of best bars 1.09–1.44; 13 leads.

---

## 4. granger_causality — Granger Causality (Toda-Yamamoto)  ⟵ CHANGED (was hy_ig_spy, a null)
**Chosen:** **phlxsox_spy** / `granger_f_by_lag`. Pairs with this chart: busloans, gold_copper_xli, hy_ig, ism_services, m2sl_yoy, nhs, petrol_inv, phlxsox, t10y3m.
**Why this pair:** the forward direction **SOX → SPY clears the 5% critical line at every tested lag** — bars tower over the threshold (F = 24 vs crit 3.84 at lag 1), the clearest "significant lead" chart in the fleet. hy_ig (old pick) was a clean NULL (tallest bar F≈1.36, nothing clears). **CAVEAT for Ray:** the reverse SPY → SOX is *also* significant at every lag (even larger F) → this is a **feedback** pair, not a one-way lead; the chart title already says so.

**Verified facts (decoded):** lags x = [1, 2, 3, 5, 10, 21].
- Forward **SOX → SPY** F = [**24.33, 13.49, 8.85, 5.58, 3.06, 2.10**].
- Reverse **SPY → SOX** F = [39.87, 19.75, 13.08, 8.17, 5.24, 3.34].
- 5% critical value per lag = [3.843, 2.997, 2.606, 2.215, 1.832, 1.557].
- Forward clears critical at **all 6 lags** (24.33>3.84, 13.49>3.00, 8.85>2.61, 5.58>2.22, 3.06>1.83, 2.10>1.56). y-axis is log-scale F.

**Callout specs (①②③):**
- ① Lag 1 forward bar **F = 24.33** towering over the 5% line at **3.84** → a strong, real lead (would occur by chance ≪ 1 in 20).
- ② Forward bars clear the per-lag critical line at **every lag (1→21)** → a cluster of significant lags, not a lone spike.
- ③ Reverse bars (SPY → SOX) also clear the line (F = 39.87 at lag 1 > 24.33) → causality runs BOTH ways (feedback) → predictive precedence, not economic cause.

**Citable numbers:** forward F at lags 1/2/3/5/10/21 = 24.3/13.5/8.85/5.58/3.06/2.10; crit 3.84 (lag1); reverse F 39.9/19.7/… all significant; log-scale axis.

---

## 5. prewhitened_ccf — Pre-Whitened Cross-Correlation  ⚑ FLAG
**Chosen:** gold_copper_xli / `ccf_prewhitened` (KEEP). Pairs with this chart: busloans, gold_copper_xli, ism_services, m2sl_yoy, nhs, petrol_inv, phlxsox, t10y3m.
**Why this pair:** clearest, most dramatic spike that pokes far past the ±1.96/√n band — but it sits at **lag 0 (contemporaneous)**.
**⚑ FLAG for Lead — no clean FORWARD-lead example exists.** Decoded scan of all candidates:
- gold_copper_xli: dominant bar **lag 0 = −0.281** (band ±0.0282) → huge, but contemporaneous.
- phlxsox_spy: dominant bar **lag 0 = +0.7088** (band ±0.0218) → even bigger, contemporaneous; title itself says "mass on BOTH sides — feedback."
- petrol_inv_spy: the ONLY genuine forward-lag significant bar → **lag +6 = −0.1204** (band ±0.1018) → real but marginal (barely clears), title "imprecise 6-month lead."
- ism/busloans/m2sl/nhs/t10y3m: essentially null (0–1 significant lag, treated as noise).
**Recommendation:** keep gold_copper_xli for the visually unambiguous "spike vs band" teaching, and have Ray write it honestly as a **contemporaneous** coupling (the CCF's job is timing structure; here the timing is lag 0). If Lead prefers a genuine *forward* lead, switch to petrol_inv (+6) but accept a marginal, less dramatic bar.

**Verified facts (gold_copper, decoded):** 61 lags (−30…+30). Significance band (dotted) = **±0.02816**. Peak |CCF| = **−0.281 at lag 0**. Next-largest bars are all |r| < ~0.038 (e.g. lag −18 = +0.0322, lag −12 = −0.0375) → nothing else clears meaningfully. Negative lags = target (XLI) leads; positive lags = signal leads.

**Callout specs (①②③):**
- ① The one tall bar at **lag 0, CCF = −0.28** piercing the ±0.028 band → strong contemporaneous co-movement after self-memory is stripped.
- ② Every other bar hugs the ±0.028 band (|r| < 0.04) → no significant lead or lag bar away from zero → the timing is "together," not "ahead."
- ③ Band is the ±1.96/√n noise threshold → only bars poking past it are non-chance; magnitude here confirms coupling, not a tradable forward lead.

**Citable numbers:** peak −0.281 at lag 0; band ±0.028; 61 lags (−30…+30); no non-zero-lag bar clears materially. (petrol_inv alt: +6, r=−0.120, band ±0.102.)

---

## 6. regime_quartile — Regime / Quartile-Gradient Analysis
**Chosen:** hy_ig_spy / `regime_quartile_returns` (KEEP). Only two pairs have this chart: hy_ig (clean monotone) and gold_copper_xli (non-monotone, Q1 3.93 → Q3 0.92 → Q4 2.92 reversal).
**Why this pair:** a textbook **monotone descending staircase** Q1→Q4 with Sharpe labels — the cleanest model-free gradient available.

**Verified facts (decoded):** annualized return (%) by quartile, Q1→Q4 = [**+18.73, +18.35, +8.86, −10.20**]; embedded Sharpe text = [1.71, 1.67, 0.63, −0.49]. Median trace = [n/a here — trace1 was Ann.Return]. Q1 = tightest spreads (bullish), Q4 = widest (bearish). Monthly data.

**Callout specs (①②③):**
- ① Q1 bar **+18.7% (Sharpe 1.71)** → tightest-spread regime, strongly positive forward returns.
- ② Monotone step-down **Q1 +18.7 → Q2 +18.3 → Q3 +8.9 → Q4 −10.2** → clean, model-free directional gradient.
- ③ Q4 bar **−10.2% (Sharpe −0.49)** → widest-spread regime flips negative → the countercyclical hypothesis confirmed without a model.

**Citable numbers:** Q1 +18.7% (Sharpe 1.71); Q2 +18.3% (1.67); Q3 +8.9% (0.63); Q4 −10.2% (−0.49); Q1−Q4 spread ≈ 29 pts; monthly, in-sample bucket means (no error bars).

---

## 7. hmm_regime — Hidden Markov Model Regime Identification
**Chosen:** hy_ig_spy / `hmm_regime_probs` (KEEP).
**Why this pair:** title "HMM Stress Probability > 0.5 Correctly Flags Every Major Drawdown" — the stress line pins to ~1.0 in documented crises, the ideal "sanity-check by eye" positive. Other pairs' HMM is a variance-regime map that spends most of the sample in "stress" (busloans 73%, nhs 80%) — less clean.

**Verified facts (decoded):** trace `P(Stress State)`, n = 6863 daily points, range 0.0–1.0. Peaks to **1.0** (e.g. 2020-05-04, COVID). Fraction of dates with P(stress) > 0.5 = **0.378 (≈38%)**. Layout has drawdown shading rects incl. **GFC 2007-10→2009-12** and **COVID 2020-02→2020-04** — stress line spikes inside both.

**Callout specs (①②③):**
- ① Stress probability pinned near **1.0 through 2008–09 (GFC shaded band)** → model confidently flags the crisis.
- ② A second spike to **1.0 in 2020 (COVID shaded band)** → regimes recur and align with documented episodes → passes the eye-check.
- ③ Line sits near 0 through calm expansions; **~38% of dates are "stress"** → separation is by turbulence, and the fit is in-sample (needs periodic re-estimation).

**Citable numbers:** P(stress) 0→1; ~38% of dates >0.5; peaks to 1.0 at 2008–09 GFC and 2020 COVID; 6863 daily obs; 2-state.

---

## 8. local_projections — Local Projections (Jordà)
**Chosen:** hy_ig_spy / `local_projections` (KEEP).
**Why this pair:** the 95% HAC band **leaves zero at the 63-day horizon** — title "Significant at 63 Days" — a clean "response leaves the band" positive. Checked alternatives: gold_copper, vix, indpro, petrol_inv all have bands straddling zero at every horizon (nulls); phlxsox/ism forward not significant.

**Verified facts (decoded):** horizons x = [5, 21, 63]. Coefficient (cumulative response) = [−0.000762, −0.003215, **−0.008287**]. 95% CI polygon → at **h = 63: upper = −0.000473, lower = −0.016101** → entire band below zero. At h = 5 and 21 the band spans zero (h21: +0.001012 to −0.007443). Response builds monotonically more negative with horizon.

**Callout specs (①②③):**
- ① The line falls monotonically **−0.0008 (5d) → −0.0032 (21d) → −0.0083 (63d)** → the impact builds over weeks.
- ② At **63 days the whole 95% HAC band [−0.0161, −0.0005] sits below zero** → a statistically clear (negative) response — the horizon to trade.
- ③ At 5d and 21d the band straddles zero → weak evidence early; the shape (build-then-significant) points at the ~63-day horizon.

**Citable numbers:** coef −0.0083 at 63d; 63d CI [−0.0161, −0.0005] (excludes zero); coef −0.0008 (5d), −0.0032 (21d); bands straddle zero at 5d/21d; 1-SD shock, HAC/Newey-West SEs.

---

## 9. quantile_regression — Quantile Regression
**Chosen:** hy_ig_spy / `quantile_regression` (KEEP). Pairs with `quantile_regression` slug: gold_copper_xli, hy_ig, indpro. (Others use `quantile_coef`.)
**Why this pair:** a clean monotone **fan-out** with CI bands: negative slope in the lower tail, ~0 at the median, positive in the upper tail — the "signal governs the WIDTH of outcomes" pattern, exactly what the caption teaches. gold_copper shows stronger downside asymmetry (q05 −2.72 vs q95 +1.16) but has NO CI bands; hy_ig's CI bands make it the better teaching chart.

**Verified facts (decoded):** quantiles τ = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]. QR coefficient = [**−0.01168**, −0.00905, −0.00503, +0.00029, +0.00468, +0.00835, **+0.01184**]. 95% CI present (e.g. τ0.05 CI [−0.01168 lower arm shown; upper −0.01004], τ0.95 upper +0.01271). Monotone increasing across τ; near-symmetric magnitude (|−0.0117| ≈ |+0.0118|) → "V-shape," width-governing.

**Callout specs (①②③):**
- ① Lower-tail slope **τ=0.05 → −0.0117** (steep negative) → in the worst months a spread signal bites hardest downward.
- ② Median slope **τ=0.50 ≈ +0.0003 (flat)** → almost no effect on the typical month → the signal is about the tails, not the average.
- ③ Upper-tail slope **τ=0.95 → +0.0118** → slopes fan out symmetrically → the signal governs the WIDTH/spread of outcomes (bridges weak average r with strong tournament Sharpe).

**Citable numbers:** slope −0.0117 (5th pct), +0.0003 (median), +0.0118 (95th pct); 7 quantiles; monotone fan; tail estimates noisier (fewer obs).

---

## 10. transfer_entropy — Transfer Entropy  ⟵ CHANGED (was hy_ig_spy, a time-series scatter)
**Chosen:** **gold_copper_xli** / `transfer_entropy`. Pairs with this chart: busloans, gold_copper_xli, hy_ig, ism_services, m2sl_yoy, nhs, petrol_inv.
**Why this pair:** the ONLY pair matching the **desired two-bar pattern** — forward TE clearly ABOVE the null with p≈0, reverse TE INSIDE the null. hy_ig (old pick) is a 303-point *time-series* scatter ("proxy TE"), a different chart form entirely. Other pairs are nulls or reverse-dominant: ism_services (fwd p=0.064 marginal, reverse p=0.002 dominant), m2sl (reverse-only significant), busloans/petrol_inv/nhs (both directions insignificant).

**Verified facts (decoded):** two bars. **TE(signal → return) = 0.01478**; **TE(return → signal) = 0.00350**. 95% null CI upper (annotation) = **0.00797**. Empirical p (title) = **0.000**. Forward bar (0.0148) is **above** the null (0.0080); reverse bar (0.0035) is **below** the null → clean directional asymmetry. Binned, N=4.

**Callout specs (①②③):**
- ① Forward bar **TE(signal→return) = 0.0148** poking **above the null CI upper of 0.0080** (p = 0.000) → significant directed information flow, indicator → target.
- ② Reverse bar **TE(return→signal) = 0.0035**, sitting **inside/below the null band** → no reverse flow → information runs one way (the desired pattern).
- ③ Null line at **0.0080** is the 95% shuffle bound → only bars above it are non-chance; magnitude is in bits, not a trading return.

**Citable numbers:** forward TE 0.0148 (p≈0.000); reverse TE 0.0035; null 95% upper 0.0080; unit = bits; binning N=4. Forward ≈ 4.2× reverse.

---

## 11. random_forest_importance — Random Forest Feature Importance
**Chosen:** indpro_spy / `rf_importance` (KEEP — the ONLY pair that renders this chart).
**Why this pair:** clean horizontal bar ranking of 10 transforms from the last walk-forward window; a legible top-to-bottom importance ordering.

**Verified facts (decoded):** horizontal bars (orient=h), 10 features. Importance (ascending, as stored) with labels:
IP accel 0.0678 · IP mom_3m 0.0820 · vix 0.0829 · IP mom 0.0841 · IP yoy 0.0844 · IP mom_6m 0.0874 · unrate 0.0984 · caput 0.1274 · **IP zscore_60m 0.1341** · **10y3m 0.1515 (top)**. Title: "(Last Walk-Forward Window)."

**Callout specs (①②③):**
- ① Longest bar → **`10y3m` importance 0.152** → yield-curve slope is the single most informative feature.
- ② Second → **`IP zscore_60m` 0.134** → the z-score transform family ranks high, corroborating the tournament's z-score/level winner.
- ③ Shortest bars → momentum transforms (`IP accel` 0.068, `IP mom_3m` 0.082) cluster at the bottom → importance ranks relevance only (no direction / tradable rule); judge accuracy vs the 50% coin-flip.

**Citable numbers:** top `10y3m` 0.152; `IP zscore_60m` 0.134; `caput` 0.127; `unrate` 0.098; bottom `IP accel` 0.068; 10 features; range 0.068–0.152.

---

## 12. walk_forward — Walk-Forward / Out-of-Sample Validation
**Chosen:** hy_ig_spy / `walk_forward` (KEEP).
**Why this pair:** title "Positive in 14/17 Years; Strategy Robust" — annual OOS Sharpe bars mostly clearing B&H, a clean durable-OOS positive.

**Verified facts (decoded):** annual OOS Sharpe 2010→2026 (17 bars) = [1.981, 0.735, 0.907, 2.579, 1.086, 0.033, 1.252, **2.906**, 0.185, 2.221, −0.028, 2.113, **−1.241**, 1.878, 1.828, 1.367, 1.413]. Positive years = **14 of 17**; negative = 3 (2015 ≈ +0.03 barely, 2020 −0.028, 2022 −1.241). B&H Sharpe (annotation) = **0.81**. Best year 2017 = 2.91; worst 2022 = −1.24.

**Callout specs (①②③):**
- ① Most bars positive → **14 of 17 years positive OOS** → edge persists on data never fitted on.
- ② Best bar **2017 = +2.91** vs the dashed **B&H 0.81** line → clears the benchmark in the large majority of years.
- ③ Negative bars **2022 = −1.24** (and 2020 ≈ 0) → real drawdown years; all figures simulated, weight the longest OOS stretch most.

**Citable numbers:** 14/17 years positive; B&H 0.81; best +2.91 (2017); worst −1.24 (2022); 17 annual bars 2010–2026.

---

## 13. bootstrap_significance — Bootstrap Significance Test
**Chosen:** **None** (caption-only) — KEEP. **Confirmed:** no standalone bootstrap/distribution chart exists in any pair's `plotly/` directory (scanned all 20 pair dirs; the bootstrap p-value is reported inline in Strategy/Confidence text, never as a JSON figure). No decode possible/needed. The existing caption correctly redirects readers to the Walk-Forward and Subperiod examples.

---

## 14. subperiod_durability — Subperiod / Durability Analysis  ⟵ CHANGED (was hy_ig_spy, episode-concentrated)
**Chosen:** **gold_copper_xli** / `subperiod_sharpe`.
**Why this pair:** the ONLY pair whose sub-periods are **all positive and similar** — the textbook DURABLE edge. Decoded alternatives were all concentration/null cases:
- gold_copper_xli: 2000-04 **+0.87**, 2005-09 **+0.81**, 2010-14 **+1.74**, 2015-19 **+0.76**, 2020-25 **+1.27** → all positive, durable. ✅
- hy_ig (old pick): Dot-Com −0.60, GFC −0.06, COVID +0.15, 2022 −1.24, Full OOS +1.41 → per-episode weak/negative, edge only in Full OOS → **concentration**, wrong lesson for a "durable" headline.
- ism_services: literally titled "The Edge Is One Episode" (COVID +1.78, rest cash/no-data).
- phlxsox: "LOST in Every Pre-OOS Crisis" (−1.16/−1.06/−0.95/+0.36).
- t10y3m: all four episodes negative.

**Verified facts (decoded):** horizontal bars, 5 sub-periods = ['2000-2004', '2005-2009', '2010-2014', '2015-2019', '2020-2025']; Sharpe = [**0.868, 0.815, 1.736, 0.756, 1.273**]. All > 0; min 0.76, max 1.74. Title: "Strategy Sharpe by historical sub-period."

**Callout specs (①②③):**
- ① Every bar positive → **all five sub-periods Sharpe 0.76 → 1.74** → the edge shows up in each era, not one lucky window → durable.
- ② Tallest **2010–2014 = +1.74**; shortest **2015–2019 = +0.76** → similar order of magnitude, no single bar carrying the result.
- ③ Recent **2020–2025 = +1.27** stays strong → durability holds out-of-sample; each window is short/noisy, so read the pattern, not one cell.

**Citable numbers:** sub-period Sharpes 0.87/0.81/1.74/0.76/1.27 (all positive); min 0.76, max 1.74; 5 windows 2000–2025; durable (not episode-concentrated).

---

## 15. structural_break_cointegration — Structural-Break & Cointegration Checks  ⟵ CHANGED (was hy_ig_spy, insignificant break)
**Chosen:** **gold_copper_xli** / `structural_break`.
**Why this pair:** its Quandt-Andrews sup-F test is **SIGNIFICANT** with a clear change-point — a real break to point at. hy_ig (old pick) was a NULL (Quandt-Andrews **F=0.03, p=0.769**, break-flag suppressed). Scanned all pairs; only two show a significant break:
- gold_copper_xli: title "max F = **252.89, SIGNIFICANT**"; break dot at **2009-01-19**; 5% crit = 8.85. ✅ (most dramatic)
- ism_services_spy: break March 2009, sup-F 12.77, **bootstrap p = 0.000** (good alternative).
- All others insignificant (phlxsox p=0.67, m2sl p=0.28, busloans p=0.30, petrol_inv p=0.64, nhs p=0.32, permit p=0.267, indpro p=0.114, vix p=0.931, indpro_xlp p=0.200, umcsent p=0.139).

**Verified facts (gold_copper, decoded):** trace = rolling sup-F statistic (n=318 points from 2005-01). Annotations: **"5% critical value = 8.85"** and **"sup-F candidate = 2009-01-19."** Title max F = **252.89** (≫ crit 8.85). Vertical dot line at **2009-01-19**. y-axis = F-statistic.

**Callout specs (①②③):**
- ① The F-statistic line spikes to a peak (**max sup-F = 252.89**) far above the **5% critical line at 8.85** → a strongly significant structural break.
- ② Vertical marker at **2009-01-19** → the estimated break date (post-GFC) → the indicator→target link shifted here.
- ③ Any full-sample statistic spanning this date should be read with caution → subsample analysis warranted; the companion cointegration question (shared long-run equilibrium) is separate/conditional.

**Citable numbers:** max sup-F 252.89 vs 5% crit 8.85; break date 2009-01-19; n=318 rolling points from 2005. (ism_services alt: sup-F 12.77, p=0.000, break 2009-03.)

---

## Confirmation
- All 15 chosen chart files were decoded from their actual JSON on disk (typed-array base64 decode); every number above is read from the data, not recalled.
- Chart files exist for all chosen pairs/slugs (bootstrap_significance intentionally None — no chart exists anywhere, re-confirmed).
- 4 mapping changes (granger→phlxsox, transfer_entropy→gold_copper, subperiod→gold_copper, structural_break→gold_copper), each moving off a null/concentrated case onto a decoded positive result.
- 1 method with NO clean positive example: **prewhitened_ccf** (only contemporaneous lag-0 spikes; petrol_inv +6 is the sole genuine-but-marginal forward lead) — Lead decision requested.
