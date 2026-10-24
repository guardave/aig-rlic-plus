# Phase 2, batch 1 — D2-09 and D1-27 (Exploratory)

2026-10-18, revised 2026-10-20 after Lead QA (`QA_BATCH1.md`, findings F1–F8). Branch
`research261017_indicator_combos`. Author: Research Ray.

**Status: Exploratory.**
- These are historical point-in-time runs. They are not V-C or V-S evaluations of the frozen registry (`d780845f`).
- Numbers only, no verdicts.
- Pre-Phase-B fleet members: none are used in this batch.

## Data used

- **Point-in-time inputs:** described in `phase2/data/DATA_DICTIONARY.md`.
- **One external pull (gap G8, accepted by the Lead):**
  - FRED `T10Y3M` daily, pulled 2026-10-17 17:46 UTC;
  - 11,685 observations, 1982-01-04 .. 2026-10-16;
  - sha256 `7bf269c5bd78a19d26172e9d5cb1af6efeacebff632e833bc0457fc8dadd36dc`;
  - pinned at `phase2/data/pinned/fred_T10Y3M_20261017.csv`.
- **Not acquired:** G5, G13, G15, G16 and G17.
- **Credit spread span:** the HY–IG OAS starts 2000-01 (no pre-2000 series, gap G16). Its last valid month-end is
  2026-03 (the file ends 2026-04-22, before the 2026-04 close).

---

## D2-09 — sample and power budget (Exploratory, descriptive)

`phase2/d2_09/budget.csv` has one row per registered hypothesis, 76 rows. Each row gives:
- the common point-in-time window, and the evaluable window. The evaluable window starts after a generic 60-month
  initial training span. It ends at the earlier of (a) the last month with all predictors and (b) the last month whose
  label horizon is fully observed (2026-09 minus the horizon);
- the number of recessions in that window, and whether 2020 is among them;
- SPY drawdown episodes of 15% or more;
- 10-month-SMA exit episodes;
- the minimum detectable effect (MDE) at 80% power, with the method used;
- for CVaR rows, the MDE from each of 3 Monte Carlo seeds (4,000 simulations each; the median is reported) and
  whether the label changes across the seeds;
- the label set by the registered D2-09 rule.

**Labels across the 76 hypotheses:**

| Label | Count |
|-------|------:|
| Blocked by a data gap: G17 (no total-return sector series) | 24 |
| Blocked by a data gap: G15 (NFCI vintages; D1-28.H1) | 1 |
| Underpowered (MDE > 2 × margin) | 20, of which 2 are also event-limited and 9 have regime episodes not counted |
| MDE ≤ 2 × margin (still above the margin) | 16, of which 5 are event-limited |
| No MDE method (recession, re-entry and log-score endpoints) | 15, of which 8 are event-limited |

**Monte Carlo sensitivity of the CVaR rows.** The CVaR MDE lies on a 0.025 grid. For 5 rows (D1-01.H2, D1-12.H1,
D1-12.H2, D1-12.H3, D2-06.H2) the median MDE sits exactly at 2 × margin, and one of the 3 seeds gives one grid step
more. Those rows are labelled "MDE ≤ 2 × margin" at the median and "underpowered" at the highest seed. The two
counts are therefore **16 / 20 at the median, and 11 / 25 if every seed-sensitive row is counted as underpowered**.
(The first version used a single stream of 1,500 simulations and reported 13 / 23.)
CVaR rows outside these 5 can also move by one grid step under other seeds, without changing their label. For
example, D1-12.H5 is 0.25 at all 3 seeds used here, but the QA recheck got 0.225 with different seeds. `budget.csv`
gives each row's minimum and maximum over the 3 seeds used.

**Facts behind the labels:**
- **No hypothesis reaches an MDE at or below its own margin** (0 of the 36 rows with an MDE).
  - The closest are the CVaR overlays on SPY: their MDE is a 20.0–32.5% reduction in CVaR, against margins of 10–15%.
  - The interaction endpoints have MDEs of 0.79–7.23 pp per month, against margins of 0.1–1.5.
  - The forward-return-difference endpoint (D1-16.H1, 6-month horizon) has an MDE of 12.25 pp, against a margin of
    2.0 pp.
- **The recession questions have few usable events.** Their evaluable windows hold 2 to 4 NBER recessions, and 2020
  is always among them. 2020 sits in the viewed window V-D.
- **The D2-09 window is a budget, not the run window.** D2-09 applies one generic 60-month start to every hypothesis.
  The D1-27 run (below) starts at the first January refit with at least 2 labelled recession months: its evaluated
  window is 2006-01..2025-09 (237 months) for H1/H3, against D2-09's 2005-01..2025-09 (249 months). The ends now agree;
  the recession count (2) is the same.

**Method limits** (recorded in `KNOWN_LIMITS.md` § 3):
- the CVaR MDE assumes iid Student-t returns;
- the interaction MDE uses a binary contrast;
- no MDE is computed for Brier-score endpoints;
- σ = 4.5 pp per month and the 60-month initial training span are stated assumptions.

---

## D1-27 — real-time recession-probability horse race (Exploratory)

**Design.** The full design is in the header of `phase2/scripts/d1_27_recession_probit.py`, fixed before the first
run.
- **Model:** expanding-window probit, refitted every January.
- **Predictors:** as known at each month-end close.
- **Label:** a recession in the next 12 months.
- **Training labels:** a row's label is used only 12 + 24 months later (to allow for NBER announcement lags).
- **Primary endpoint:** Brier skill score (BSS) against the term-only probit fitted on the same rows.
- **Test:** one-sided block-bootstrap test (block length 24, 2000 draws).
- **Family:** F-REC holds **7 registered hypotheses**. Correction is Holm over all 7, with the hypotheses not run
  counted as p = 1. (The registry also defines a confirmatory-only Holm over 4; under it H3 would be 0.446.)
- **Null:** the added predictors are circularly shifted together, K = 500.

**Why H1 and H3 start in 2006.** The credit spread starts 2000-01 (gap G16). A row's label enters training only 36
months later (12 + 24), and a fit needs at least 36 rows and 2 positive labels. The first January refit that
qualifies is 2006-01. That first fit trains on **37 rows (2000-01..2003-01), 19 of them positive, all from one
recession (2001)**, with 2 (H1) or 4 (H3) predictors. A training set this small and this one-episode is a plausible
contributor to the overconfident calibration below; this has not been tested separately.

### Primary result (full window)

| | H1 term + credit | H2 term + Sahm gap | H3 term + credit + Sahm + permits |
|---|---|---|---|
| Window | 2006-01 .. 2025-09 (237 months) | 1988-01 .. 2025-09 (453 months) | 2006-01 .. 2025-09 (237 months) |
| Recessions covered | 2 (2008, 2020) | 4 (1990, 2001, 2008, 2020) | 2 (2008, 2020) |
| Brier, model | 0.2098 | 0.1935 | 0.1605 |
| BSS vs term-only, same rows (primary) | +0.085 | −0.165 | +0.300 |
| Raw one-sided p | 0.329 | 0.870 | 0.112 |
| **Holm-adjusted p (m = 7)** | **1.00** | **1.00** | **0.78** |
| Null-tournament percentile of the BSS (null 95th percentile) | 90.4 (0.215) | 39.6 (0.015) | 100.0 (0.101) |
| BSS vs term-only, full history | −0.167 | −0.165 | +0.108 |
| BSS vs B1 base rate | −0.388 | −0.271 | **−0.062** |
| BSS vs B2a best single (in-fold) | +0.050 | −0.069 | +0.123 |
| BSS vs B3 naive equal-weight composite | −0.012 | −0.137 | **−0.110** |
| Calibration slope (1 = calibrated) | 0.15 | 0.13 | 0.23 |
| Per-episode log-score gain vs term-only | 2008: −35.9; 2020: +0.3 | 1990: −27.4; 2001: −0.6; 2008: +15.5; 2020: +1.3 | 2008: +32.2; 2020: −65.0 |

**Reading the table:**
- **H3 has the lowest Brier score of the three models**, but it is higher than both the constant base rate (BSS
  −0.06) and the naive composite (BSS −0.11). After Holm the p-value is 0.78.
- **Its gain against term-only depends on which term-only model is used.** Against term-only trained on the same
  rows (2000+) the BSS is +0.30; against term-only trained on its full history from 1982 it is +0.11.
- **The null percentile and the bootstrap p disagree for H3** (100.0 vs raw p 0.11). The null median BSS is
  negative (−0.26): shifted noise predictors cost skill, so a high percentile mostly measures that cost. Both are
  shown; neither is adjusted for the other.
- **All three models are overconfident** (calibration slopes 0.13–0.23).

### The SPY 10-month trend flag (B4, unregistered baseline)

B4 is a comparison baseline, not a registered hypothesis. The flag starts 1993-10; with the 36-month label lag, its
first January refit with at least 36 training rows and 2 positive labels is 2004-01.
`phase2/d1_27/matched_b4.json` scores every model and baseline on the rows where all 7 have a prediction. These rows are **not** the primary windows above when the hypothesis window starts earlier
(H2: primary 1988-01, 453 months, 4 recessions; matched 2004-01, 261 months, 2 recessions).

| Matched rows | Months | Recessions | B4 Brier | B4 rank (of 7) | Lowest Brier among the other 6 |
|--------------|-------:|-----------|---------:|---------------:|-------------------------------|
| H1 models: 2006-01 .. 2025-09 | 237 | 2 (2008, 2020) | 0.148 | 1 | B1 base rate, 0.151 |
| H2 models: 2004-01 .. 2025-09 | 261 | 2 (2008, 2020) | 0.129 | 1 | B1 base rate, 0.140 |
| H3 models: 2006-01 .. 2025-09 | 237 | 2 (2008, 2020) | 0.148 | 2 | B3 naive composite, 0.145 |

- On the H1 and H2 matched rows, B4 has a lower Brier score than all 6 others: the hypothesis model, term-only on the
  same rows and on full history, B1, B2a and B3.
- On the H3 matched rows, B3 (the naive equal-weight composite of the four H3 predictors, itself mapped through a
  one-slope probit) has a lower Brier score than B4: 0.145 against 0.148.
- These comparisons cover 2 recessions. No test or multiplicity correction is applied to B4.

### Post-hoc sensitivity (not pre-registered)

The frozen registry defines no excluding-2020 sensitivity for D1-27. It lists 2020 only under V-D, as descriptive.
The variant below was written into the script header before the first run, but that header was not committed
beforehand. **It is therefore post-hoc** and is shown only for the per-episode picture.

Rows t ≤ 2019-02, so that no label window reaches the 2020 recession. The Holm row applies the same 7-hypothesis
correction to the post-hoc p-values. It does **not** account for the choice of the window itself, which was made
with 2020 already known, so it understates the true multiplicity. The null uses the same 500 shifts as the primary
run, rescored on this window.

| | H1 term + credit | H2 term + Sahm gap | H3 four predictors |
|---|---|---|---|
| Window | 2006-01 .. 2019-02 (158 months) | 1988-01 .. 2019-02 (374 months) | 2006-01 .. 2019-02 (158 months) |
| Recessions covered | 1 (2008) | 3 (1990, 2001, 2008) | 1 (2008) |
| BSS vs term-only, same rows | +0.297 | +0.020 | +0.749 |
| Raw one-sided p | 0.111 | 0.446 | 0.003 |
| Holm-adjusted p (m = 7, post-hoc window) | 0.67 | 1.00 | 0.021 |
| Null-tournament percentile (null 95th) | 98.6 (0.199) | 96.4 (0.002) | 100.0 (0.105) |
| BSS vs B1 base rate | +0.050 | +0.024 | +0.661 |
| BSS vs B3 naive composite | +0.058 | −0.124 | +0.315 |
| Brier, model / B4 flag (B4 on its own rows) | 0.150 / 0.142 | 0.152 / 0.116 (B4: 182 rows) | 0.054 / 0.142 |

- The whole difference from the primary result for H3 comes from the 2020 episode. H3's log score in 2020 is 65.0
  below term-only; in 2008 it is 32.2 above.
- For H1 and H3 only 2008 is left in the window: one episode.

## Files

- `phase2/scripts/d2_09_budget.py`
- `phase2/scripts/d1_27_recession_probit.py`
- `phase2/scripts/d1_27_matched_b4.py`
- `phase2/scripts/p2data.py`
- `phase2/d2_09/` (budget.csv, summary.json)
- `phase2/d1_27/` (results.json, predictions.csv, matched_b4.json, panel_pit_monthly.csv)
- `phase2/data/DATA_DICTIONARY.md`
- `phase2/README_zh.html` / `.pdf`
