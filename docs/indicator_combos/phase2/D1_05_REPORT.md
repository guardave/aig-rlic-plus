# Phase 2 — D1-05: term spread × credit spread (Exploratory)

2026-10-20, revised the same day after QA (`QA_D1_05.md`, findings F1–F7). Branch `research261017_indicator_combos`.
Author: Research Ray.

**Status: Exploratory.**
- This is a historical point-in-time run on data that has already been viewed. It is not the V-C evaluation of the
  frozen registry (`d780845f`).
- Numbers only, no verdicts.
- No pre-Phase-B fleet member is used.

Script: `phase2/scripts/d1_05_term_credit.py`; its header holds the full design and both revisions. Outputs are in
`phase2/d1_05/` (`results.json`, `panel_monthly.csv`).

## Question and hypotheses (family F-TC, 4 registered hypotheses)

| Hypothesis | Asset (next-month excess return) | Statistic | Sign tested, margin | Source of the sign |
|------------|----------------------------------|-----------|---------------------|--------------------|
| H1 (confirmatory in the registry) | SPY | d on z(term) × z(credit), expanding z-scores | d < 0, 0.25 pp/month | registered |
| H2 | SPY | d on J = 1{T10Y3M < 0.5} × 1{HY–IG 6-month change > 0}, beyond the two dummies | d < 0, 0.50 pp/month | **inferred by Ray, not registered** |
| H3 | 10-year Treasury proxy (DGS10, gap G6) | as H1 | d > 0, 0.10 pp/month | registered |
| H4 | 10-year Treasury proxy | as H2 | d > 0, 0.20 pp/month | registered |

- **H2 has no registered sign.** Its pass rule (`*pr_inter`) says "registered sign" but gives no value. I test d < 0
  because J = 1 is the joint-distress state. That is my inference, recorded in `KNOWN_LIMITS.md` § 7.
- The registered rule wants the HAC p and the stationary-bootstrap p both ≤ 0.05, the sign, and |d| ≥ margin.
- The registry's correction is a single test for H1 when it is confirmatory (V-C). For this exploratory reading it
  is a Romano-Wolf stepdown over all 4.

## Data and point-in-time handling

- **Signals.** T10Y3M is the pinned FRED file (gap G8). HY–IG OAS is the local ICE BofA file, 2000-01 to 2026-03.
  Both take the value of the trading day before each month-end close. There is no pre-2000 credit series (gap G16),
  so there is no V-B Baa–Aaa supporting run.
- Expanding z-scores use data up to and including t and need 36 months, so the first z is 2002-12.
- **Targets.** SPY dividend-adjusted return, and the 10-year par-bond proxy from DGS10, each over month t+1 (from
  close t to close t+1), minus the 3-month T-bill known at t. The Treasury proxy is priced from the DGS10 values *at*
  the closes t and t+1. The first version used the previous trading day, which shifted the target window one day
  earlier than the decision (QA F5); H3 and H4 moved slightly as a result.
- **Primary window:** one common window for all 4 hypotheses, **2002-12 .. 2026-02, 279 months**, with 2 NBER
  recessions (2008, 2020). Each hypothesis on its own longest window is shown as a sensitivity.
- **Purge.** The registered 1-month purge holds by construction in the real-time loop. A row t enters training at
  the January refit T only if t < T, so its label (the return over t+1) is known by the close of T.
- **Self-check.** z-scores and dummies recomputed with every input set to missing after 2012-12 are identical
  through 2012-12. QA repeated this at 3 cut dates and added a return-poison test on the forecast loop.

## Primary result (common window, 279 months, 2 recessions)

| | H1 SPY, levels | H2 SPY, joint dummy | H3 Treasury, levels | H4 Treasury, joint dummy |
|---|---:|---:|---:|---:|
| d (pp per month) | −0.872 | +1.104 | +0.305 | −0.590 |
| Matches the sign tested | yes | no (sign inferred) | yes | no |
| \|d\| / margin | 3.49 | 2.21 | 3.05 | 2.95 |
| HAC t (NW 6) | −2.06 | 0.71 | 0.84 | −0.93 |
| One-sided HAC p | 0.020 | 0.762 | 0.201 | 0.824 |
| One-sided stationary-bootstrap p | 0.035 | 0.777 | 0.203 | 0.825 |
| **Romano-Wolf adjusted p (over 4, registered)** | **0.145** | **0.962** | **0.453** | **0.962** |
| Holm adjusted p (over 4, larger of the two p) | 0.140 | 1.00 | 0.608 | 1.00 |
| N1 null percentile of the sign-aligned **HC0** t, all 243 offsets (null 5th / 50th / 95th) | 98.4 (−2.03 / −0.11 / 1.72) | 18.1 (−1.52 / 0.10 / 1.81) | 76.5 (−1.71 / 0.10 / 1.75) | 19.3 (−1.58 / −0.09 / 1.62) |
| R² | 0.018 | 0.007 | 0.025 | 0.008 |
| Joint-distress months / episodes | — | 30 / 10 | — | 30 / 10 |

The N1 null shifts term and credit together against the returns. A circular shift on 315 months has 243 admissible
offsets (36 .. n − 37); all of them are used, so the null is exhaustive and has no seed. (The first version drew
500 offsets with replacement and reported 99.0 for H1; QA F2.)

**Reading the table:**
- **H1, family-level.** After the registered exploratory correction, the H1 p is **0.145 (Romano-Wolf over 4)**;
  Holm gives 0.140. At the single-test level, both one-sided p are ≤ 0.05, the sign matches, and |d| = 3.5 × margin.
  That single-test rule is the registry's confirmatory (V-C) correction; it is not the one that applies to this
  exploratory run.
- **N1** puts the H1 HC0 t at the 98.4th percentile of the 243 shifts.
- **Power.** D2-09 MDEs (80% power) against the margins:

  | | H1 | H2 | H3 | H4 |
  |---|---:|---:|---:|---:|
  | MDE (pp/month) | 0.79 | 1.97 | 0.79 | 1.97 |
  | Margin | 0.25 | 0.50 | 0.10 | 0.20 |

  - All four are labelled underpowered.
  - The H3 and H4 MDEs use the SPY σ, which is a D2-09 simplification.
  - At this power, an estimate that reaches p ≤ 0.05 must be large. The size of H1's d = −0.87 is therefore likely
    to be overstated (type-M error; Gelman and Carlin, 2014).
- **H2 and H4** have the sign opposite to the one tested. For H2, that sign is my inference, not the registry's.
- **H3** has the registered sign and p = 0.20.

### What the sign of d means here

The registry text reads the H1 sign as "flat curve with wide spreads worse". In this parameterisation a flat-and-wide
month has z(term) < 0 and z(credit) > 0, so its product is **negative**. A negative d then adds to the forecast in
those months.

| Quadrant (sign of z, primary window) | Months | Mean next-month SPY excess (pp) | Mean next-month Treasury-proxy excess (pp) | Sign of z(term) × z(credit) |
|---|---:|---:|---:|:-:|
| flat, tight | 159 | 0.73 | −0.17 | + |
| flat, wide | 12 | **4.28** | 0.85 | − |
| steep, tight | 72 | 0.51 | 0.44 | − |
| steep, wide | 36 | 0.67 | 0.25 | + |

- "Flat" means below the expanding mean of T10Y3M (about 1.5–2 pp). It does not mean an inverted curve.
- **If H1 were to pass its test, the meaning would be this:** flat-and-wide months forecast **higher** next-month
  SPY returns, i.e. rebounds after spread spikes. That is the **opposite** of the registry's prose story ("flat curve
  with wide spreads worse"). The H1 result does not support that story.
- **The pattern rests on those 12 months:** 6 in 2016, 4 in 2020, 1 in 2011 and 1 in 2022. Without them
  (post-hoc, descriptive; the months are chosen on the signals, not on the returns), d = −0.29 with HAC t −0.63.
- **The other negative-product quadrant does not show the pattern.** Steep-and-tight months average 0.51 pp,
  which is below flat-and-tight months (0.73 pp, positive product).
- **Erratum.** The registry wording misstates its own sign for H1, and likewise for H3 ("flight to quality"). This
  was found after the data were viewed. It is recorded as a dated erratum in `KNOWN_LIMITS.md` § 7 (Lead ruling,
  2026-10-20). The frozen registry is not edited.

## Sensitivities

**Own longest window, per hypothesis:**

| | Window | Months | d | HAC t | Bootstrap p |
|---|---|---:|---:|---:|---:|
| H1 | 2002-12 .. 2026-03 | 280 | −0.880 | −2.09 | 0.042 |
| H2 | 2000-07 .. 2026-03 | 309 | +0.156 | 0.11 | 0.551 |
| H3 | 2002-12 .. 2026-02 | 279 | +0.305 | 0.84 | 0.194 |
| H4 | 2000-07 .. 2026-02 | 308 | −0.323 | −0.55 | 0.715 |

The joint-dummy coefficients depend heavily on whether 2000-07..2002-11 is included (H2: +1.10 vs +0.16).

**N2 null (registered as "random second market member"; the pool below was chosen by Ray and is not registered).**
Credit is replaced by each of 5 other unrevised market series (VIX, DXY, log gold/copper, effective fed funds, log
IWM/SPY), using the continuous design, on their common window (2003-07 .. 2026-03).
- **H1** (273 months): credit has the largest sign-aligned HC0 t of the 6, 1.92; next is VIX, 1.47.
- **H3** (272 months): credit is again first, 0.98; next is IWM/SPY, 0.95.
- With only 5 alternatives, rank 1 of 6 has a 1-in-6 chance under exchangeability.

**Post-hoc, descriptive (no p-values):** d with blocks of rows removed, one at a time.

| | Drop 2008-07..2009-06 (267 months) | Drop 2020-02..2020-06 (274 months) | Drop the 12 flat-and-wide months (267 months) |
|---|---|---|---|
| H1 | −0.876 (HAC t −2.24) | −0.628 (−1.51) | −0.287 (−0.63) |
| H2 | +0.487 (0.33) | +1.915 (1.49) | — |
| H3 | −0.080 (−0.44) | +0.436 (1.07) | +0.513 (1.16) |
| H4 | −0.498 (−0.79) | −0.732 (−1.19) | — |

- H1 does not depend on 2008–09.
- Removing the 5 months of 2020 shrinks H1's d by about 30% (t −1.51). Removing the 12 flat-and-wide months shrinks
  it by about two-thirds (t −0.63).
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

- None of the three regressions forecasts next-month SPY excess returns better than the prevailing mean in real
  time.
- Adding the interaction raises the forecast error relative to the additive model.

**Overlay translation** (long SPY when the forecast ≥ 0, else T-bill; no trading costs):

| Strategy | Ann. excess return % | Sharpe | CVaR 5% (monthly %) | Max drawdown % | Exposure | Switches |
|----------|---------:|------:|------:|------:|------:|------:|
| B1 buy-and-hold SPY | 9.93 | 0.654 | 9.61 | −51.9 | 1.00 | 0 |
| H1 model | 7.57 | 0.546 | 9.20 | −43.0 | 0.90 | 12 |
| B2a best single | 8.43 | 0.581 | 9.32 | −47.7 | 0.95 | 2 |
| B3 naive composite (+term, −credit) | 5.04 | 0.533 | 6.59 | −22.4 | 0.56 | 29 |
| B4 SPY 10-month SMA | 7.17 | 0.677 | 6.74 | −23.6 | 0.80 | 31 |

- The H1 overlay has a lower Sharpe ratio than buy-and-hold, B2a and B4.
- Its CVaR is higher than that of B3 and B4.
- B4 has the highest Sharpe ratio of the five.

## Limits

- The window covers 2 recessions, and **2020 is inside it** (the viewed V-D period). H1 depends partly on the 5
  months 2020-02..06, and mostly on 12 flat-and-wide months.
- Pre-2000 history (V-B) is not available (G16).
- The Treasury proxy has no convexity term and uses a constant-maturity yield (G6).
- H2's tested sign is inferred, not registered.
- The overlay ignores trading costs and is a translation, not a registered endpoint.
- The N2 pool is small (6 members). It was chosen by Ray from the series held locally and is not registered.
- The script header says it was revised before any number was reported. That draft was never committed, so the
  claim cannot be checked from git.

## Files

- `phase2/scripts/d1_05_term_credit.py`
- `phase2/d1_05/results.json`, `phase2/d1_05/panel_monthly.csv`
- `phase2/README_zh_d1_05.html` / `.pdf`
