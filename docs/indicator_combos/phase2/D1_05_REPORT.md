# Phase 2 — D1-05: term spread × credit spread (Exploratory)

2026-10-20. Branch `research261017_indicator_combos`. Author: Research Ray.

**Status: Exploratory.**
- This is a historical point-in-time run on data that has already been viewed. It is not the V-C evaluation of the
  frozen registry (`d780845f`).
- Numbers only, no verdicts.
- No pre-Phase-B fleet member is used.

Script: `phase2/scripts/d1_05_term_credit.py`; its header holds the full design. Outputs are in `phase2/d1_05/`
(`results.json`, `panel_monthly.csv`).

## Question and registered hypotheses (family F-TC, 4 hypotheses)

| Hypothesis | Asset (next-month excess return) | Statistic | Registered sign, margin |
|------------|----------------------------------|-----------|-------------------------|
| H1 (confirmatory in the registry) | SPY | d on z(term) × z(credit), expanding z-scores | d < 0, 0.25 pp/month |
| H2 | SPY | d on J = 1{T10Y3M < 0.5} × 1{HY–IG 6-month change > 0}, beyond the two dummies | d < 0, 0.50 pp/month |
| H3 | 10-year Treasury proxy (DGS10, gap G6) | as H1 | d > 0, 0.10 pp/month |
| H4 | 10-year Treasury proxy | as H2 | d > 0, 0.20 pp/month |

The registered rule wants the HAC p and the stationary-bootstrap p both ≤ 0.05, the registered sign, and |d| ≥ margin.
The registry's correction is a single test for H1 when it is confirmatory, and a Romano-Wolf stepdown over all 4 for
the exploratory reading.

## Data and point-in-time handling

- T10Y3M: the pinned FRED file (gap G8, see the batch-1 report), value of the trading day before each month-end close.
- HY–IG OAS: the local ICE BofA file, same timing. It runs 2000-01 to 2026-03 (gap G16: no pre-2000 series, so no
  V-B Baa–Aaa supporting run).
- Expanding z-scores use data up to and including t and need 36 months, so the first z is 2002-12.
- Targets: SPY dividend-adjusted return, and the 10-year par-bond proxy from DGS10, each over month t+1, minus the
  3-month T-bill known at t.
- **Primary window:** one common window for all 4 hypotheses, **2002-12 .. 2026-02, 279 months**. It covers 2
  NBER recessions (2008, 2020). Each hypothesis on its own longest window is shown as a sensitivity.
- The D2-09 budget gave D1-05 a 255-month window (2005-01 .. 2026-03, after its generic 60-month start) and an H1
  MDE of 0.79 pp/month, labelled underpowered (MDE > 2 × 0.25).
- Self-check: z-scores and dummies recomputed with every input set to missing after 2012-12 are identical through
  2012-12.

## Primary result (common window, 279 months, 2 recessions)

| | H1 SPY, levels | H2 SPY, joint dummy | H3 Treasury, levels | H4 Treasury, joint dummy |
|---|---:|---:|---:|---:|
| d (pp per month) | −0.872 | +1.104 | +0.303 | −0.390 |
| Sign as registered | yes | no | yes | no |
| \|d\| / margin | 3.49 | 2.21 | 3.03 | 1.95 |
| HAC t (NW 6) | −2.06 | 0.71 | 0.79 | −0.59 |
| One-sided HAC p | 0.020 | 0.762 | 0.214 | 0.723 |
| One-sided stationary-bootstrap p | 0.035 | 0.777 | 0.214 | 0.728 |
| **Romano-Wolf adjusted p (over 4, registered)** | **0.151** | **0.914** | **0.490** | **0.914** |
| Holm adjusted p (over 4, larger of the two p) | 0.138 | 1.00 | 0.642 | 1.00 |
| N1 null percentile of the sign-aligned t (null 5th / 50th / 95th) | 99.0 (−2.15 / −0.07 / 1.71) | 16.8 (−1.40 / −0.01 / 1.72) | 76.0 (−1.73 / 0.03 / 1.75) | 29.6 (−1.65 / −0.19 / 1.56) |
| R² | 0.018 | 0.007 | 0.023 | 0.007 |
| Joint-distress months / episodes | — | 30 / 10 | — | 30 / 10 |

**Reading the table:**
- **H1.** On its own, H1 meets the numbers of the registered single-test rule on this viewed sample: both
  one-sided p ≤ 0.05, the registered sign, and |d| = 3.5 × margin. Romano-Wolf over the 4 hypotheses of the family
  gives 0.151; Holm gives 0.138. The N1 null puts the t at the 99th percentile.
- **H1 power.** D2-09 put the H1 MDE at 0.79 pp/month. In a design at that power, an estimate that reaches
  p ≤ 0.05 must be large, so the size of d = −0.87 is likely to be overstated (type-M error; Gelman and Carlin, 2014).
- **H2 and H4** have the sign opposite to the one registered. **H3** has the registered sign and p = 0.21.

### What the sign of d means here

The registry text reads the H1 sign as "flat curve with wide spreads worse". In this parameterisation a flat-and-wide
month has z(term) < 0 and z(credit) > 0, so its product is **negative**. A negative d then adds to the forecast in
those months. The data line up with that arithmetic, not with the registry text:

| Quadrant (sign of z, primary window) | Months | Mean next-month SPY excess (pp) | Mean next-month Treasury-proxy excess (pp) | Sign of z(term) × z(credit) |
|---|---:|---:|---:|:-:|
| flat, tight | 158 | 0.75 | −0.18 | + |
| flat, wide | 12 | **4.28** | 0.91 | − |
| steep, tight | 73 | 0.47 | 0.49 | − |
| steep, wide | 36 | 0.67 | 0.17 | + |

- "Flat" means below the expanding mean of T10Y3M (about 1.5–2 pp). It does not mean an inverted curve.
- The 12 flat-and-wide months are 2011-12, 2016-01..06, 2020-03..06 and 2022-06. These are months right after
  credit-spread spikes, and they are followed by rebounds; 2020-03 is followed by +12.7 pp.
- **What a significant H1 means.** The registered numerical sign (d < 0) is the test of record. A d < 0 that clears
  it means that **flat-and-wide months forecast HIGHER next-month SPY returns**: rebounds after spread spikes. In
  this sample that rests on 12 months: 6 in 2016, 4 in 2020, 1 in 2011 and 1 in 2022. This is the **opposite** of
  the registry's prose story ("flat curve with wide spreads worse"), and the H1 result does not support that story.
- **Erratum.** The registry wording misstates its own sign for H1, and likewise for H3 ("flight to quality"). This
  was found after the data were viewed. It is recorded as a dated erratum in `KNOWN_LIMITS.md` § 7 (Lead ruling,
  2026-10-20). The frozen registry is not edited.

## Sensitivities

**Own longest window, per hypothesis:**

| | Window | Months | d | HAC t | Bootstrap p |
|---|---|---:|---:|---:|---:|
| H1 | 2002-12 .. 2026-03 | 280 | −0.880 | −2.09 | 0.041 |
| H2 | 2000-07 .. 2026-03 | 309 | +0.156 | 0.11 | 0.551 |
| H3 | 2002-12 .. 2026-02 | 279 | +0.303 | 0.79 | 0.208 |
| H4 | 2000-07 .. 2026-02 | 308 | −0.139 | −0.23 | 0.604 |

The joint-dummy coefficients depend heavily on whether 2000-07..2002-11 is included (H2: +1.10 vs +0.16).

**N2 null (registered: random second market member).** The pool below was chosen by Ray and is not registered.
Credit is replaced by each of 5 other unrevised market
series (VIX, DXY, log gold/copper, effective fed funds, log IWM/SPY), using the continuous design. On the common N2
window (2003-07 .. 2026-03, 273 months for H1; 272 for H3), credit has the largest sign-aligned t of the 6 for both
H1 (1.92; next VIX 1.47) and H3 (0.96; next IWM/SPY 0.86). With only 5 alternatives, rank 1 of 6 has a 1-in-6 chance
under exchangeability.

**Post-hoc, descriptive (no p-values):** d with crisis rows removed, one block at a time.

| | Drop 2008-07..2009-06 (267 months) | Drop 2020-02..2020-06 (274 months) |
|---|---|---|
| H1 | −0.874 (HAC t −2.23) | −0.628 (HAC t −1.51) |
| H2 | +0.487 (0.33) | +1.915 (1.49) |
| H3 | −0.087 (−0.48) | +0.445 (1.04) |
| H4 | −0.270 (−0.41) | −0.581 (−0.93) |

- H1 does not depend on 2008–09. Removing the 5 months of 2020 shrinks d by about 30%, and its t falls to −1.5.
- H3 changes sign without 2008–09.

## Against naive baselines (real time, SPY, 2006-01 .. 2026-03, 243 months)

Expanding regressions are re-estimated each January on rows whose next-month return is already known.

**Out-of-sample forecast R² against the prevailing mean:**

| Model | OOS R² |
|-------|-------:|
| H1 interaction model | −0.073 |
| Additive model (term + credit) | −0.055 |
| B2a best single (in-fold) | −0.071 |
| Interaction vs additive | −0.017 |

None of the three regressions forecasts next-month SPY excess returns better than the prevailing mean in real time.
Adding the interaction raises the forecast error relative to the additive model.

**Overlay translation** (long SPY when the forecast ≥ 0, else T-bill; no trading costs):

| Strategy | Ann. excess return % | Sharpe | CVaR 5% (monthly %) | Max drawdown % | Exposure | Switches |
|----------|---------:|------:|------:|------:|------:|------:|
| B1 buy-and-hold SPY | 9.93 | 0.654 | 9.61 | −51.9 | 1.00 | 0 |
| H1 model | 7.57 | 0.546 | 9.20 | −43.0 | 0.90 | 12 |
| B2a best single | 8.43 | 0.581 | 9.32 | −47.7 | 0.95 | 2 |
| B3 naive composite (+term, −credit) | 5.04 | 0.533 | 6.59 | −22.4 | 0.56 | 29 |
| B4 SPY 10-month SMA | 7.17 | 0.677 | 6.74 | −23.6 | 0.80 | 31 |

- The H1 overlay has a lower Sharpe ratio than buy-and-hold, B2a and B4, and a higher CVaR than B3 and B4.
- B4 has the highest Sharpe ratio of the five.

## Limits

- The window covers 2 recessions, and **2020 is inside it** (the viewed V-D period). The H1 result depends partly on
  the 5 months 2020-02..06.
- Pre-2000 history (V-B) is not available (G16).
- The Treasury proxy has no convexity term and uses a constant-maturity yield (G6).
- The overlay ignores trading costs and is a translation, not a registered endpoint.
- The N2 pool is small (6 members). It was chosen by Ray from the series held locally and is not registered.

## Files

- `phase2/scripts/d1_05_term_credit.py`
- `phase2/d1_05/results.json`, `phase2/d1_05/panel_monthly.csv`
- `phase2/README_zh_d1_05.html` / `.pdf`
