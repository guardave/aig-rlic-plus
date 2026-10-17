# How many variations? The combination space, raw and effective (revision 2)

Branch `research261017_indicator_combos`, 2026-10-17. Author: Research Ray. This is a counting and descriptive
document. No returns were read and no backtests were run.

Scripts and outputs:

| Script | Output |
|--------|--------|
| `scripts/combinatorics_exact.py` | `data/combinatorics_exact.json` |
| `scripts/pit_panel_inspect.py` | `data/effective_dimensionality.json`, `data/panel_*.csv`, `data/spearman_*.csv`, `data/coverage_and_lags.csv` |

Revision 2 replaces three things from revision 1. They were wrong or overstated, as the QA and Codex reviews found:
- the median-grid approximation for the raw count;
- the "5–8 dimensions" average across different estimands;
- the pre/post-2008 claim.

## Executive summary

- **Raw count (exact, § 2).** These are sums over every subset of members of the products of their published grid
  sizes, per operator, after removing duplicate operators.
  - Two-indicator combinations: **2 × 10^10 to 3 × 10^10** configurations per target asset and alignment.
  - If a filter is allowed to re-tune its second member separately in each regime, the count rises to **4 × 10^13
    to 7 × 10^13**.
  - Across 20 assets and 3 alignments: about **1.2 × 10^12 to 1.5 × 10^12** (or 2.6 × 10^15 to 3.9 × 10^15).
  - Three-indicator combinations reach about **10^15 to 10^21** per asset and alignment.
- **Frozen members.** With each member frozen at its published rule, about **17,000 two-indicator and 700,000
  three-indicator** configurations remain per asset and alignment.
  - With one representative per frozen block (8 blocks): **1,484** and **15,120**.
  - The registered question bank tests **76 hypotheses**.
- **Effective dimensionality, primary estimand.**
  - The primary estimand is the participation ratio of the strict point-in-time panel: 10 ALFRED vintage series
    plus 4 unrevised market series, 2001-08 → 2026-05, 298 months.
  - Result: **PR = 5.5, 90% block-bootstrap interval 3.8–6.4.**
  - Independent series with the same serial correlation would give PR ≥ 10.2 (5th percentile of the null), so the
    panel is far more concentrated than chance.
- **Sensitivity.**
  - Parallel analysis with serial-dependence-preserving nulls keeps only **2 factors** (stationary bootstrap) or
    **1** (phase randomisation).
  - Σ min(λ, 1) = 8.0.
  - Clusters at |ρ| ≥ 0.5: 8.
  - Plain reading: there are **one or two strong common factors and about 4–6 effective dimensions in total**.
    The "5–8 independent dimensions" of revision 1 was generous.
- **Power.** At 80% power the minimum detectable Sharpe gap over 8 years is **0.49–0.86** when the strategy's
  returns correlate 0.8–0.9 with its comparator. Over a 3-year forward window it is **0.80–2.14**. Serial
  correlation and multiplicity raise these further (§ 4).

## 1. Dimensions and the member universe

| Dimension | Values | Source |
|-----------|--------|--------|
| Indicators (members) | **26** distinct indicators behind the 35 live pairs. They map to 27 release-calendar series ids; new home sales SA and NSA are counted once | `lead_axis_registry.json` (39 entries = 35 live + 3 archived + 1 superseded) |
| Member grid per indicator | From each pair's latest published tournament CSV, buy-and-hold rows removed: rules m_i, binary states s_i, readings t_i (definitions in the script header). An indicator with several pairs: upper bound = sum of its pairs' grids, lower bound = largest single grid | 35 CSVs; 164,176 rules in total; per-pair median 1,180, mean 4,691 |
| Operators | See the table below, with applicability and deduplication | `TAXONOMY.md` |
| Target assets | 20: SPY, 9 sector SPDRs, their 9 relatives vs SPY, and the cyclical − defensive basket | `etf_prices` (price-only: G17) |
| Alignment | 3: month-end as-of; release-date event; daily as-of | `TAXONOMY.md` § 3 |

**Operators, applicability and deduplication** (k = number of members):

| Operator | Covers | Count per subset S | Applicability / deduplication |
|----------|--------|--------------------|-------------------------------|
| BOOL | R1 confirmation, R2 plain filter, R5 binary divergence, R7 diffusion | (unate Boolean functions on all k inputs) × Π s_i / 2^k → **2 Π s** (k = 2), **9 Π s** (k = 3). Admitting non-unate functions such as XOR adds 0.5 Π s (k = 2) or 18.25 Π s (k = 3) | The grids hold both directions, so functions that differ only by negated inputs coincide. A plain filter equals an AND, and unweighted diffusion equals k-of-n, so neither adds a separate count |
| SEQ | R4 sequencing | k! · 6^(k−1) · Π s | Events are not symmetric under negation |
| REPAR | R2 with regime-specific rules | k = 2: Σ_r (s_r / 2) · m_b (m_b − 1) | Negating the regime gives the same partition, hence the factor 1/2 |
| COMP | R3 composite | 27 · Π t (3 weightings × 3 thresholds × 3 position rules) | Acts on readings, not rules |
| DIVC | R5 continuous gap | 6 · t_a t_b | k = 2 only |
| SIZE | R6 direction/size | 3 · Σ_j t_j · dir_j | Sizing member j; the direction comes from the other members |

Each total is Σ_S Π x_i, computed exactly as an elementary symmetric polynomial.

## 2. Exact counts

**Per target asset and per alignment:**

| Operator | k = 2, lower | k = 2, upper | k = 3, lower | k = 3, upper |
|----------|------:|------:|------:|------:|
| BOOL (unate) | 2.6 × 10^9 | 3.4 × 10^9 | 1.7 × 10^14 | 2.6 × 10^14 |
| SEQ | 1.6 × 10^10 | 2.0 × 10^10 | 4.1 × 10^15 | 6.2 × 10^15 |
| COMP | 3.4 × 10^8 | 4.6 × 10^8 | 5.0 × 10^11 | 7.8 × 10^11 |
| DIVC | 7.5 × 10^7 | 1.0 × 10^8 | — | — |
| SIZE | 7.6 × 10^8 | 1.0 × 10^9 | 3.4 × 10^13 | 5.2 × 10^13 |
| **Total without REPAR** | **1.9 × 10^10** | **2.5 × 10^10** | **4.4 × 10^15** | **6.5 × 10^15** |
| REPAR (regime-specific re-tuning) | 4.4 × 10^13 | 6.6 × 10^13 | 2.0 × 10^21 | 4.0 × 10^21 |
| **Total with REPAR** | **4.4 × 10^13** | **6.6 × 10^13** | **2.0 × 10^21** | **4.0 × 10^21** |

- **Grand total.** Multiply by 60 (20 assets × 3 alignments). For k = 2 this gives 1.2–1.5 × 10^12 without
  REPAR, or 2.6–3.9 × 10^15 with it.
- **Sequencing dominates** the count once regime re-tuning is excluded. Regime re-tuning dominates everything,
  because every regime doubles a member's parameter space.

**Comparison with simple approximations** (k = 2 / k = 3, one rule pair per subset, no operators):

| Approximation | k = 2 | k = 3 |
|---------------|------:|------:|
| Median grid: C(26,k) × 1,180^k | 4.5 × 10^8 | 4.3 × 10^12 |
| Mean grid: C(26,k) × 4,691^k | 7.2 × 10^9 | 2.7 × 10^14 |

The median-grid figure that revision 1 used understated the space by more than an order of magnitude. Grid sizes
are very skewed (96 to 19,344 rules per pair), and Π m_i is driven by the large grids.

**Smaller families** (per asset and alignment):

| Family | Definition | k = 2 | k = 3 |
|--------|------------|------:|------:|
| Frozen members | One published rule per indicator; operators BOOL 2/9, SEQ 12/216, COMP 27, DIVC 6 (k = 2), SIZE 6/18 | 17,225 | 702,000 |
| Frozen block representatives (8 blocks, § 3.4) | C(8,k) × 53 or × 270 | 1,484 | 15,120 |
| Registered bank | — | **76 hypotheses** in total (`registry/families.yaml`) | |

## 3. Effective dimensionality

### 3.1 Pre-specified design (revision 2)

- **Primary panel: strict-PIT-14.** It contains only series that are point-in-time:
  - ALFRED vintages, with the transform recomputed inside each vintage: INDPRO YoY, UNRATE 12-month change, RSXFS
    YoY, UMCSENT, HOUST YoY, PERMIT YoY, new home sales YoY, M2 YoY, BUSLOANS YoY, NEWORDER YoY;
  - unrevised market series: T10Y3M, HY–IG OAS, gold/copper log-ratio YoY, SOX/SPY YoY.
  - This membership was frozen in the script before it was run. Note that SOX/SPY is built from SPY prices.
- **Primary estimand.** The participation ratio PR = (Σλ)² / Σλ² of the Pearson correlation matrix of the
  standardised readings.
  - Its 90% interval comes from a moving-block bootstrap: rows resampled jointly in 24-month blocks, 2000 draws.
  - PR is a continuous "effective number of equally important dimensions". It equals the number of variables when
    they are independent, and 1 when they are perfectly collinear.
- **Sensitivity analyses** (none of them is an estimate of the same quantity; they are not averaged):
  - parallel analysis under two serial-dependence-preserving nulls, each with every column made independent and
    2000 draws: a per-column stationary bootstrap (mean block 24 months) and per-column phase randomisation;
  - the entropy effective rank;
  - M_eff = Σ min(λ, 1);
  - the published Li & Ji (2005) formula;
  - hierarchical clusters;
  - the same statistics on the revised-as-of panels (not point-in-time) and on 3-month changes.
- **The Li & Ji formula.** Li & Ji (2005) define M_eff = Σ [I(λ ≥ 1) + (λ − ⌊λ⌋)]. Revision 1 implemented exactly
  this, giving 13.0 for revised core 23.
  - This formula is not monotone in λ. An eigenvalue of 1.9 counts 1.9, but one of 2.0 counts 1.0.
  - Following the Codex review, revision 2 reports Σ min(λ, 1) as the M_eff figure (10.45 for core 23) and keeps
    the published value for reference. Both are sensitivity measures only.

### 3.2 Results

| Panel | Track | Months | Vars | **PR [90% CI]** | Null PR, 5th percentile | PA (stationary block) | PA (phase) | Entropy rank | Σ min(λ,1) | Li–Ji (published) |
|-------|-------|-------:|-----:|------|------:|---:|---:|------:|------:|------:|
| **strict-PIT-14** (primary) | vintage + market | 298 (2001-08 → 2026-05) | 14 | **5.52 [3.75, 6.35]** | 10.2 | 2 | 1 | 7.81 | 7.97 | 10.0 |
| strict-PIT-14, 3-month changes | vintage + market | 295 | 14 | 6.38 [4.93, 9.08] | 12.6 | 2 | 2 | 9.17 | 9.03 | 11.0 |
| real-time, 10 long-history series | vintage | 304 (2001-06 → 2026-09) | 10 | 4.23 [3.05, 4.99] | 7.9 | 2 | 2 | 5.76 | 5.80 | 6.0 |
| real-time, all 16 | vintage | 160 (2013-06 → 2026-09) | 16 | 4.18 [2.99, 5.08] | 9.8 | 2 | 2 | 6.40 | 7.08 | 9.0 |
| revised-as-of core 23 (not PIT) | revised | 296 (2001-08 → 2026-03) | 23 | 5.59 [3.91, 6.61] | 14.2 | 3 | 2 | 9.11 | 10.45 | 13.0 |
| revised-as-of all 29 (not PIT) | revised | 107 (2017-02 → 2025-12) | 29 | 4.77 [3.41, 5.20] | 11.0 | 2 | 2 | 7.92 | 10.57 | 13.0 |
| revised core 23, 3-month changes | revised | 293 | 23 | 8.58 [6.63, 11.02] | 19.3 | 3 | 3 | 13.25 | 13.67 | 16.0 |

**Reading the table.**
- On the primary panel the first eigenvalue is 4.86 (35% of the variance) and the second is 2.21 (cumulative 51%).
- Only these two factors stand clear of serially-dependent noise.
- The participation ratio says the variance is spread roughly as if over 5–6 equal dimensions, with an interval of
  about 4 to 6.
- The all-29 panel exists only inside the viewed OOS window.
- The revision-1 split before and after 2008 has been withdrawn:
  - its windows had very different lengths (77 vs 219 months), so the comparison was confounded by sample size;
  - the pre-2008 window was an expansion, not a downturn.
  - D2-04 now asks the question properly, with equal-length rolling windows and an interval.

### 3.3 Clusters (sensitivity only)

- **Strict-PIT-14, |ρ| ≥ 0.5, average linkage.** Eight clusters:
  - {RSXFS, NEWORDER, gold/copper}
  - {HOUST, PERMIT, new home sales}
  - {INDPRO, UNRATE}
  - {T10Y3M, HY–IG}
  - {UMCSENT}, {M2}, {BUSLOANS} and {SOX/SPY} on their own.
- **Revised core 23.** 10 clusters at 0.5 and 18 at 0.7.
- **Caution.** Cluster counts depend on the cut and the linkage. They are not an estimate of dimensionality.

### 3.4 Frozen block membership (used by the question bank)

The table below was frozen on 2026-10-17. It merges economic priors with the observed clusters, so any historical
test that relies on it is **exploratory**. It holds 8 blocks and covers all 29 panel indicators.

| Block | Members | Point-in-time representative |
|-------|---------|------------------------------|
| B1 Activity & labour | INDPRO, UNRATE, RSXFS, NEWORDER, AMTMNO, import prices (IR), Cass freight, retail inventories/sales, ECI | INDPRO YoY (vintage) |
| B2 Housing | HOUST, PERMIT, new home sales, NAHB, cement | PERMIT YoY (vintage) |
| B3 Market credit & curve | HY OAS, HY–IG OAS, T10Y3M | HY–IG OAS (market) |
| B4 Bank credit | SLOOS, card delinquency, BUSLOANS | BUSLOANS YoY (vintage; SLOOS vintages only from 2010) |
| B5 Sentiment | UMCSENT, UMich expected business conditions | UMCSENT (vintage) |
| B6 Manufacturing surveys, commodities & energy | ISM manufacturing, ISM services, gold/copper, EIA crude inventories | gold/copper YoY (market; ISM is revised-only historically) |
| B7 Money | M2 | M2 YoY (vintage) |
| B8 Market risk & internals | VIX / VIX3M, SOX/SPY | VIX level (market, 1990+) |

## 4. Power: minimum detectable Sharpe gap

The variance of the difference between two Sharpe ratios is (Jobson–Korkie, with Memmel's 2003 correction; iid,
annualised Sharpe, T in years):

Var(SR₁ − SR₂) ≈ [2(1 − ρ) + ½(SR₁² + SR₂² − 2·SR₁·SR₂·ρ²)] / T

The minimum detectable effect is MDE = (z₁₋α/2m + z₀.₈) · √(VIF · Var), where:
- the test is two-sided at 5% with 80% power;
- m is the number of tests in the family (Bonferroni-equivalent);
- VIF inflates the variance for serial correlation.

The tables assume equal Sharpe ratios for the two strategies, SR = 0.5 / 1.0.

**Table 4a.** m = 1, VIF = 1. Each cell gives SR = 0.5 / SR = 1.0.

| Years | ρ = 0.5 | ρ = 0.7 | ρ = 0.8 | ρ = 0.9 |
|------:|--------:|--------:|--------:|--------:|
| 3 (forward V-C after 3 years) | 1.76 / 2.14 | 1.38 / 1.70 | 1.13 / 1.41 | 0.80 / 1.01 |
| 8 (≈ the viewed OOS window) | 1.08 / 1.31 | 0.84 / 1.04 | **0.69 / 0.86** | **0.49 / 0.62** |
| 16 | 0.76 / 0.93 | 0.60 / 0.74 | 0.49 / 0.61 | 0.35 / 0.44 |
| 25 | 0.61 / 0.74 | 0.48 / 0.59 | 0.39 / 0.49 | 0.28 / 0.35 |

**Table 4b.** ρ = 0.8, SR = 0.5, VIF = 1.5 (moderate serial correlation in monthly overlay returns), by family size m.

| m | 3 years | 8 years | 16 years | 25 years |
|--:|--------:|--------:|---------:|---------:|
| 1 | 1.39 | 0.85 | 0.60 | 0.48 |
| 10 | 1.81 | 1.11 | 0.78 | 0.63 |
| 50 | 2.05 | 1.25 | 0.89 | 0.71 |

- Without the Sharpe-level term, the 8-year MDE would be 0.63 at ρ = 0.8 and 0.44 at ρ = 0.9 (the figures in the
  Codex review).
- Fat tails, negative skew and lower correlations (an overlay against buy-and-hold often correlates only 0.5–0.7)
  push the MDE higher still.
- **Consequences.**
  - A Sharpe gain is very hard to establish on any window we have.
  - The bank's primary endpoints are therefore tail (CVaR), event and calibration measures with explicit margins.
  - D2-09 labels hypotheses whose MDE exceeds twice their margin as "underpowered" in advance, without dropping
    them.
  - The forward window V-C will usually be inconclusive for several years. V-S is what makes confirmatory
    recession questions decidable.

## 5. Limits

1. **Persistence.** YoY and 12-month-difference readings overlap by construction. The block bootstrap (24-month
   blocks) and the serial-dependence-preserving nulls address this, but block length is a choice. The intervals
   are approximate.
2. **Indicator dimension is not predictive dimension.** These numbers describe co-movement among readings. They do
   not describe how much information the readings hold about returns, which is what D2-11 asks.
3. **Standard transforms, not the winners' rules.** Binary bull/bear states can agree more or less often than the
   continuous readings correlate. D2-03 measures the winners' streams once G4 is done.
4. **Grid-based counts depend on published grids.** Grids differ across pipelines (96 to 19,344 rules per pair).
   Merging pairs of the same indicator gives bounds, not a single number. Equivalent position series produced by
   different rules (e.g. thresholds never crossed) are not removed, so the counts are upper bounds on *distinct*
   position series.
5. **Coverage.**
   - The latest Cass vintage starts in 2016.
   - Market series in the local files start in 2000; FRED extends them.
   - VIX3M starts in 2007.
   - Revised-only sources are excluded from the primary panel by design.
