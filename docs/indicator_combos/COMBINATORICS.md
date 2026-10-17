# How many variations? The combination space, raw and effective

Phase 1 drafting document, branch `research261017_indicator_combos`, 2026-10-17. Author: Research Ray.
The numbers in § 3 come from `scripts/pit_panel_inspect.py`, which writes to `data/effective_dimensionality.json`,
`data/coverage_and_lags.csv` and `data/spearman_*.csv`. The run is descriptive only: no asset returns were read
and no backtests were run.

## Executive summary

- **Raw count.** Re-searching every member rule, two-indicator combinations alone span about **8 × 10^11**
  configurations, and three-indicator combinations about **4 × 10^16**. Even with every member frozen at its
  published single-indicator rule, about **8 × 10^5** pairs and **4 × 10^7** triples remain.
  - These counts cover 26 series, 41 (k = 2) or 267 (k = 3) operator structures, 20 target assets and 3 alignment
    variants.
- **Effective count.** The 29 indicators carry roughly **5–8 independent dimensions** in their point-in-time level
  readings.
  - **Parallel analysis:** 3–5 factors above noise.
  - **Participation ratio:** 4.2–5.6.
  - **Entropy effective rank:** 5.8–9.1.
  - **Clusters:** 7–10 at |ρ| ≥ 0.5.
  - On short-horizon (3-month) changes the count rises to about 9–13, but those changes are noisier and not
    necessarily more informative.
- **Working answer.** The economically distinct menu is about **7 blocks**. With one representative per block that
  gives 21 block-pairs and 35 block-triples, and about **860 pair configurations per asset per alignment** across
  all operators. That is about 9 orders of magnitude fewer than the raw count, and it is the size of family a
  multiple-testing correction can survive.
- **Dimensionality is not constant.**
  - **Before 2008:** about 3.5 by participation ratio and 2 by parallel analysis.
  - **From 2008:** about 5.2 by participation ratio and 5 by parallel analysis.
  - When the cycle turns the indicators move together, and diversification from combining is smallest exactly when
    it is wanted most (question D2-04 tests this).
- **Common sample shrinks fast.**
  - **All 29 indicators complete-case:** only 2017-02 → 2025-12 (107 months), which is almost exactly the
    already-viewed out-of-sample (OOS) window.
  - **Core 23:** 2001-08 → 2026-03 (296 months).
  - **Strict real-time with ALFRED vintages for all 16 vintage series:** only from 2013-06 (160 months).

## 1. Dimensions of the space

| # | Dimension | Values used for the count | Source |
|---|-----------|---------------------------|--------|
| 1 | Indicator series | 26 distinct series behind the 35 live pairs (29 in the descriptive panel) | `docs/schemas/lead_axis_registry.json` |
| 2 | Member rule (transform × threshold × lead × direction × position rule) | Fleet median **1,008** candidates per pair (min 96, max 19,344; 144,098 over 29 pairs) | `results/*/winner_summary.json` `total_combos` |
| 3 | Number of members k | 2, 3 (4+ shown for scale) | — |
| 4 | Role / operator structure (see `TAXONOMY.md`) | k = 2: **41**; k = 3: **267**; k = 4: 5,260 | Formula below |
| 5 | Target asset | 20: SPY, 9 original sector SPDRs (XLK XLF XLV XLE XLY XLI XLU XLP XLB, live since 1998-12), their 9 relatives vs SPY, 1 cyclical − defensive basket | `data/Data Master.xlsx` sheet `etf_prices` |
| 6 | Alignment / rebalance | 3: month-end as-of, release-date event, daily as-of | `TAXONOMY.md` § 3 |
| 7 | Use case (metric) | 5 (U1–U5). This multiplies the number of *tests*, not configurations. | `TAXONOMY.md` § 4 |

**Operator structures for k members** (w = 6 window choices per sequencing link, 3 regime definitions, 3 sizing
maps, 3 composite weightings × 3 thresholds):

| Role | Count formula | k = 2 | k = 3 |
|------|---------------|------:|------:|
| R1 confirmation (k-of-n) | k | 2 | 3 |
| R2 filter (which member is the regime × 3 regime definitions) | 3k | 6 | 9 |
| R3 composite (3 weightings × 3 thresholds) | 9 | 9 | 9 |
| R4 sequencing (orderings × windows per link) | k! · w^(k−1) | 12 | 216 |
| R5 divergence (member pairs × 2 measures × 3 thresholds) | 6 · C(k,2) | 6 | 18 |
| R6 direction/sizing split (which sets direction × 3 maps) | 3k | 6 | 9 |
| R7 diffusion (3 thresholds; k ≥ 3) | 3 | — | 3 |
| **Total** | | **41** | **267** |

Sequencing dominates as k grows: 216 of the 267 structures at k = 3, and 5,184 of the 5,260 at k = 4. This is
the strongest argument for pre-registering chain orders from economic theory rather than searching them.

## 2. Raw counts

| Family | Definition | k = 2 | k = 3 |
|--------|------------|------:|------:|
| Full re-search | C(26,k) × 1,008^k × structures × 20 assets × 3 alignments | 8.1 × 10^11 | 4.3 × 10^16 |
| Frozen members | Each member = its published winner rule; only membership, operator, asset and alignment vary | 8.0 × 10^5 | 4.2 × 10^7 |
| Block representatives (7 blocks), frozen | C(7,k) × structures × 20 × 3 | 51,660 | 560,700 |
| Block representatives, SPY only, one alignment | C(7,k) × structures | **861** | 9,345 |
| Pre-registered question bank | About 37 questions × 2–6 pre-declared variants each | — | **~100–200 tests in total** |

Subset counts for reference: C(26,k) = 325 / 2,600 / 14,950 / 65,780 for k = 2…5, and C(7,k) = 21 / 35 / 35 / 21.

**Reading the table.**
- The fleet's single-indicator search already used about 1.4 × 10^5 configurations, and the published winners are
  the best of each.
- Combining winners re-uses those selections, so a combination built from winners inherits the selection bias of
  all its members.
- Novy-Marx (2015/2016) shows that this "multiple-signal" bias grows quickly with k. A frozen-member combination
  must therefore be tested against a null that **re-runs the member selection** inside each null draw, not
  against a null that takes the members as given.

## 3. Effective dimensionality from point-in-time data

### 3.1 Method

1. **Panel.** At the close of the last trading day of each month (1985-01 → 2026-09), take each indicator's latest
   reading with `available_date ≤ t` from `data/release_calendar/release_calendar.csv` (revised values, "revised
   as-of" track).
   - The 16 ALFRED series are also built on the **real-time** track: the vintage visible at t, with the transform
     recomputed inside that vintage.
   - Market series are unrevised. The HY/IG OAS uses the value from t−1 business day (FRED posts it the next day).
2. **Transforms.** One standard transform per indicator, chosen *before* looking at correlations:
   - YoY % for activity, housing, money and credit volumes, import prices and gold/copper (log-ratio change),
   - a 12-month (4-quarter) difference for UNRATE, retail inventories/sales and card delinquency,
   - the level for surveys, SLOOS, spreads and the VIX ratio.
   These are *not* the fleet winners' transforms (see the limits below).
3. **Statistics** on the standardised complete-case panel:
   - eigenvalues of the correlation matrix,
   - the number of PCs needed for 80% / 90% of variance,
   - the Kaiser count (λ > 1),
   - Horn (1965) parallel analysis (200 column-wise permutations, seed 20261017, 95th percentile),
   - the participation ratio (Σλ)²/Σλ²,
   - the entropy effective rank exp(−Σ p log p),
   - Nyholt (2004) and Li & Ji (2005) M_eff,
   - average-linkage clustering on 1 − |Spearman ρ| cut at |ρ| = 0.7 and 0.5.
4. **Robustness variants:** 3-month changes of the same readings; sub-periods before and from 2008; the
   real-time track.

### 3.2 Results

| Variant | Months (window) | Vars | PCs 80% | PCs 90% | Kaiser | Parallel analysis | Participation ratio | Entropy rank | Li–Ji M_eff | Clusters at 0.5 |
|---------|-----------------|-----:|--------:|--------:|-------:|---------:|-------:|-------:|-------:|-------:|
| Revised as-of, core 23 | 296 (2001-08 → 2026-03) | 23 | 6 | 10 | 6 | **5** | **5.6** | 9.1 | 13 | **10** |
| Revised as-of, all 29 | 107 (2017-02 → 2025-12) | 29 | 6 | 9 | 6 | 3 | 4.8 | 7.9 | 13 | 7 |
| Core 23, 3-month changes | 293 (2001-11 → 2026-03) | 23 | 10 | 14 | 7 | 5 | 8.6 | 13.3 | 16 | 21 |
| Core 23, before 2008 | 77 (2001-08 → 2007-12) | 23 | 4 | 6 | 5 | 2 | 3.5 | 5.6 | 9 | — |
| Core 23, from 2008 | 219 (2008-01 → 2026-03) | 23 | 6 | 9 | 5 | 5 | 5.2 | 8.4 | 12 | — |
| Real-time ALFRED, 10 long-history series | 304 (2001-06 → 2026-09) | 10 | 4 | 6 | 3 | 2 | 4.2 | 5.8 | 6 | — |
| Real-time ALFRED, all 16 | 160 (2013-06 → 2026-09) | 16 | 4 | 7 | 4 | 3 | 4.2 | 6.4 | 9 | — |

- **Core 23** leaves out ECI, the VIX ratio, Cass, retail inventories/sales, cement and ISM services, to keep a
  2001+ sample.
- **The 10 long-history series** are indpro, unrate, rsxfs, umcsent, houst, permit, nhs, m2, busloans and neworder.
- **First eigenvalue.** It takes 35% of variance (core 23) and 42% (real-time 16): one dominant cycle factor
  plus a few secondary ones.

### 3.3 The blocks (core 23, |ρ| ≥ 0.5, average linkage)

| Cluster | Members | Economic label |
|---------|---------|----------------|
| C1 | indpro, unrate, rsxfs, neworder, amtmno, import_px, cc_delinq, sloos | Real activity, labour and bank credit standards (the cycle factor) |
| C2 | houst, permit, nhs | Housing activity |
| C3 | t10y3m, hy_oas, hy_ig | Rates and credit market pricing |
| C4 | umcsent, nahb | Household and builder sentiment |
| C5 | ism_mfg, gold_copper | Manufacturing survey and commodity cyclicality (ρ = −0.70 at the pairwise level) |
| singletons | m2, busloans, umich_exp, crude_inv, sox_spy | Money, bank lending volume, business-condition expectations, energy inventories, equity internals |

**Most redundant pairs** (pairwise Spearman, ≥ 60 overlapping months):

| Pair | ρ |
|------|--:|
| hy_oas – hy_ig | 0.99 |
| houst – permit | 0.82 |
| neworder – amtmno | 0.80 |
| amtmno – import_px | 0.77 |
| cass – ism_mfg | 0.74 |
| ism_mfg – ism_svc | 0.73 |
| unrate – sloos | 0.71 |
| indpro – neworder | 0.70 |
| permit – nhs | 0.65 |
| houst – nhs | 0.61 |

New home sales is noticeably less redundant with starts and permits than starts and permits are with each other.

**Proposed working blocks for the question bank** (empirical clusters merged with economic priors; 7 to 8 blocks):

- **B1 activity & labour:** INDPRO, UNRATE, RSXFS, NEWORDER/AMTMNO, import prices, Cass, inventories/sales.
- **B2 housing:** HOUST, PERMIT, HSN1F, NAHB, cement.
- **B3 market credit & curve:** HY OAS, HY–IG, T10Y3M.
- **B4 bank credit:** SLOOS, card delinquency, BUSLOANS.
- **B5 sentiment:** UMCSENT, UMich expectations.
- **B6 manufacturing surveys & commodity:** ISM manufacturing, ISM services, gold/copper.
- **B7 money:** M2.
- **B8 market risk & internals:** VIX/VIX3M, SOX/SPY.
- **Energy (crude inventories)** sits on its own and is weak a priori; it is kept as a "placebo-like" block.

B4 is split from B1 on economic grounds even though SLOOS clusters with activity empirically. The real question is
whether credit *leads* activity (sequencing, D1-12), and that question needs them separate.

### 3.4 What this means for "how many variations"

- On level readings, about **5–8** genuinely independent indicator dimensions exist, depending on the statistic.
  - Parallel analysis is the most conservative (2–5).
  - The entropy rank and Li–Ji count are the most generous (6–13).
- A combination search that treats 26 series as 26 independent ideas over-counts the idea space by roughly 3–5×.
  It under-counts the *trial* space, because member rules, operators and assets multiply on top.
- For multiple-testing corrections the relevant number is the effective count of **strategy-return streams**,
  which is not yet measured (question D2-03). Indicator-level dimensionality gives a lower bound on idea diversity,
  not the trial count for a deflated Sharpe ratio.

## 4. Power: what difference can the samples detect?

The standard error of a Sharpe-ratio difference between two strategies whose returns correlate at ρ is roughly
√(2(1 − ρ)/T) per year of data (Jobson–Korkie / Memmel approximation, Sharpe ratios near 0.5–1). Two standard
errors give the smallest annualised Sharpe gap distinguishable from zero at about 5% (two-sided, 50% power):

| Years of data | ρ = 0.5 | ρ = 0.8 | ρ = 0.9 |
|---------------|--------:|--------:|--------:|
| 8 (≈ the existing OOS window) | 0.71 | 0.45 | 0.32 |
| 10 | 0.63 | 0.40 | 0.28 |
| 16 (≈ the fleet IS window, or real-time all-16 from 2013) | 0.50 | 0.32 | 0.22 |
| 25 (2001 → 2026) | 0.40 | 0.25 | 0.18 |

- A combination and its best single member usually correlate at 0.8–0.9.
- On the existing roughly 8-year OOS window, a gain under about 0.3–0.45 Sharpe is therefore indistinguishable
  from noise *before* any multiple-testing correction.
- This is why the question bank leans on tail metrics, on the long backward holdout and on breadth across assets,
  rather than on OOS Sharpe alone.

## 5. Limits of this estimate

1. **Persistence.** Level readings are highly autocorrelated (YoY and 12-month differences overlap by construction).
   The effective number of independent months is far below the count of months, which makes the eigenvalues less
   stable than the tables suggest. Parallel analysis by column permutation ignores autocorrelation and is
   therefore *too generous* to noise eigenvalues. A block-permutation version is a Phase 2 item.
2. **Complete-case selection.** The all-29 panel exists only for 2017-02 → 2025-12, inside the already-viewed OOS
   window. The core-23 numbers are preferred for that reason.
3. **Transform choice.** Changes give a higher dimension than levels (8.6 vs 5.6 participation ratio). The fleet
   winners use a mix of levels, changes, z-scores and flags, so their effective dimension lies somewhere between
   the two. It should be measured on the actual winner states (D2-03).
4. **Linear vs threshold.** Correlation of continuous readings is not correlation of binary bull/bear states. Two
   series with ρ = 0.6 can produce states that agree 90% of the time, or 60%.
5. **Revised vs real-time.** Most rows rely on revised data with release-date masking. The real-time track (10–16
   series) gives similar or lower dimension (4.2 participation ratio). Revisions add noise that slightly reduces
   measured correlation.
6. **Coverage holes.**
   - The latest Cass vintage starts in 2016, so the revised Cass track starts in 2017. Older Cass vintages go back
     to 1990 and could be spliced.
   - Market series in the local parquets start in 2000. FRED holds T10Y3M from 1982 and the ICE BofA OAS from
     1996–97.
   - The VIX3M series starts in 2007.
7. **Indicator dimension ≠ predictive dimension.** Two independent indicators may carry the same (or no)
   information about returns. The effective dimension of *return-relevant* information is the quantity D2-11
   proposes to estimate. It is likely lower than the indicator dimension.
