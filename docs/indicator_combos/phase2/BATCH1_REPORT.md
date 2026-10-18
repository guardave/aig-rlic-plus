# Phase 2, batch 1 — D2-09 and D1-27 (Exploratory)

2026-10-18. Branch `research261017_indicator_combos`. Author: Research Ray.

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

---

## D2-09 — sample and power budget (Exploratory, descriptive)

`phase2/d2_09/budget.csv` has one row per registered hypothesis, 76 rows. Each row gives:
- the common point-in-time window, and the evaluable window (after a 60-month initial training span and the label
  horizon);
- the number of recessions in that window, and whether 2020 is among them;
- SPY drawdown episodes of 15% or more;
- 10-month-SMA exit episodes;
- the minimum detectable effect (MDE) at 80% power, with the method used;
- the label set by the registered D2-09 rule.

**Labels across the 76 hypotheses:**

| Label | Count |
|-------|------:|
| Blocked by a data gap: G17 (no total-return sector series) | 24 |
| Blocked by a data gap: G15 (NFCI vintages; D1-28.H1) | 1 |
| Underpowered (MDE > 2 × margin) | 23, of which 4 are also event-limited and 9 have regime episodes not counted |
| MDE ≤ 2 × margin | 13, of which 3 are event-limited |
| No MDE method (recession, re-entry and log-score endpoints) | 15, of which 8 are event-limited |

**Facts behind the labels:**
- **No hypothesis reaches an MDE at or below its own margin.**
  - The closest are the CVaR overlays on SPY: their MDE is a 22.5–32.5% reduction in CVaR, against margins of 10–15%.
  - The interaction endpoints have MDEs of 0.8–7.3 pp per month, against margins of 0.1–1.5.
- **The recession questions have few usable events.** Their evaluable windows hold 2 to 4 NBER recessions, and 2020
  is always among them. 2020 sits in the viewed window V-D.

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
  counted as p = 1.
- **Null:** the added predictors are circularly shifted together, K = 500.

### Primary result (full window)

| | H1 term + credit | H2 term + Sahm gap | H3 term + credit + Sahm + permits |
|---|---|---|---|
| Window | 2006-01 .. 2025-09 (237 months) | 1988-01 .. 2025-09 (453 months) | 2006-01 .. 2025-09 (237 months) |
| Recessions covered | 2 (2008, 2020) | 4 (1990, 2001, 2008, 2020) | 2 (2008, 2020) |
| Brier, model | 0.2098 | 0.1935 | 0.1605 |
| BSS vs term-only, same rows (primary) | +0.085 | −0.165 | +0.300 |
| Raw one-sided p | 0.329 | 0.870 | 0.112 |
| **Holm-adjusted p (m = 7)** | **1.00** | **1.00** | **0.78** |
| Null-tournament percentile of the BSS | 90.4 | 39.6 | 100.0 (null 95th percentile 0.101) |
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
- **All three models are overconfident** (calibration slopes 0.13–0.23).

### The SPY 10-month trend flag (B4)

`phase2/d1_27/matched_b4.json` scores every model and baseline on the same rows where the flag exists:

| Window | Rows | B4 Brier | B4 rank (of 7) | Best macro Brier |
|--------|------|---------:|---------------:|-----------------|
| H1 window | 2006-01 .. 2025-09 | 0.148 | 1 | — |
| H2 window | 2004-01 .. 2025-09 | 0.129 | 1 | — |
| H3 window | 2006-01 .. 2025-09 | 0.148 | 2 | naive composite B3, 0.145 |

- **The flag beats every estimated macro probit in every window where it exists:** H1–H3, term-only on the same rows
  and on full history, and the best single predictor. It also beats the base rate.
- **The one exception** is the naive equal-weight composite of the four H3 predictors in 2006–2025: Brier 0.145
  against 0.148.

### Post-hoc sensitivity (not pre-registered)

The frozen registry defines no excluding-2020 sensitivity for D1-27. It lists 2020 only under V-D, as descriptive.
The variant below was written into the script header before the first run, but that header was not committed
beforehand. **It is therefore post-hoc** and is shown only for the per-episode picture.

Rows t ≤ 2019-02, so that no label window reaches the 2020 recession:

| Hypothesis | BSS vs term-only, same rows | Raw p (no correction) | BSS vs B1 | BSS vs B3 |
|------------|----------------------------:|----------------------:|----------:|----------:|
| H3 | +0.749 | 0.003 | +0.661 | +0.315 |
| H1 | +0.297 | 0.111 | — | — |
| H2 | +0.020 | 0.446 | — | — |

- The whole difference from the primary result comes from the 2020 episode. H3's log score in 2020 is 65.0 below
  term-only; in 2008 it is 32.2 above.
- With only 2008 left in the window, this is one episode.

## Files

- `phase2/scripts/d2_09_budget.py`
- `phase2/scripts/d1_27_recession_probit.py`
- `phase2/scripts/d1_27_matched_b4.py`
- `phase2/scripts/p2data.py`
- `phase2/d2_09/` (budget.csv, summary.json)
- `phase2/d1_27/` (results.json, predictions.csv, matched_b4.json, panel_pit_monthly.csv)
- `phase2/data/DATA_DICTIONARY.md`
- `phase2/README_zh.html` / `.pdf`
