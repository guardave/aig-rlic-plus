# Question bank — indicator combinations (組合拳)

Phase 1 drafting document, branch `research261017_indicator_combos` (cut from `int261017_phaseB` @ 3d735ec7),
2026-10-17. Author: Research Ray. **Pre-registration draft: no question below has been tested.** No backtests, no
strategy search, and no asset returns were read while drafting. Descriptive facts quoted (coverage, lags,
correlations) come from `data/coverage_and_lags.csv` and `data/effective_dimensionality.json`.

## Executive summary

- **37 questions:** 25 under Direction 1 (useful combinations for real use cases) and 12 under Direction 2 (how many
  variations, and how many of them are real).
- **Direction 1 is grouped by role** (R1–R7, see `TAXONOMY.md`). Every question names a use case (U1–U5) with its
  own primary metric. Sharpe is never the only yardstick.
- **Every question is compared with four baselines:**
  - B1, buy-and-hold;
  - B2, the best single indicator, selected fold-honestly;
  - B3, a naive equal-weight composite of the same indicators;
  - B4, a trend/volatility baseline, because many overlays turn out to be trend proxies.
- **Every question carries a null check:**
  - N1, a joint block shift of the indicator panel;
  - N2, random-member combinations;
  - N3, a re-selection null for frozen fleet winners;
  - N4, family-wise control.
- **Validation does not reuse the fleet's out-of-sample window** (OOS, about 2017→2026), which has been viewed many
  times; it is reported as descriptive only (V-D). The primary designs are:
  - V-A, nested purged walk-forward inside the fleet's in-sample window (IS, about 1998→2016);
  - V-B, a backward holdout over 1980/85→1997 that the fleet never used;
  - V-C, a frozen forward paper-trade from 2026-11.
- **The top-10 by priority are in § 3.** Foundations first: the effective number of strategy streams (D2-03) and
  the power and common-sample budget (D2-09). Then the low-degree-of-freedom combinations:
  - a block-representative equal-weight composite (D1-08),
  - macro conditioned on market stress (D1-04),
  - a curve + labour recession classifier (D1-02),
  - a direction-vs-sizing split (D1-19),
  - and others.

---

## 0. Common protocol (referenced by every question)

### 0.1 Pre-registration (P)

- **P1.** Before any run, commit a spec file per question: members, transforms, thresholds, operator, lead, asset,
  metric, baselines, validation design and the null. The commit hash is the registration.
- **P2.** Any change after the first run is logged as a new version, and every version is reported, including the
  failed ones.
- **P3.** Questions are a closed family. Ideas that emerge during Phase 2 go into a *new* family with its own
  correction, never into this one.

### 0.2 Point-in-time rules (T)

- **T1.** A reading enters at the first trading close t with `available_date ≤ t`.
  - Revised-as-of track: `data/release_calendar/release_calendar.csv`.
  - Real-time track: the ALFRED vintage visible at t.
  - Implementation: `scripts/_pit_align.py` (`pit_shift`, `realtime_apply`) and the harness `align.py`.
- **T2.** A position decided at close t earns the t → t+1 return (`position_shift = 1`, the strict lead floor).
- **T3.** ALFRED series run both tracks.
  - ALFRED series: INDPRO, UNRATE, RSXFS, UMCSENT, HOUST, PERMIT, HSN1F, M2SL, BUSLOANS, NEWORDER, AMTMNO, IR,
    Cass, RETAILIRSA, DRCCLACBN and DRTSCILM.
  - The real-time track is primary wherever the vintage history covers the window.
  - No-archive sources (ISM, NAHB, UMich expectations, USGS cement, EIA) are revised-only, which is disclosed.
- **T4.** Regime variables are IS-frozen fits with *filtered* probabilities only (`scripts/_regime_causal.py`).
  Smoothed probabilities are banned.
- **T5.** Combinations start at the latest member start (balanced). An unbalanced variant must be pre-registered
  separately.

### 0.3 Baselines (B), all reported for every question

| Code | Baseline | Note |
|------|----------|------|
| B1 | Buy-and-hold of the target (or the static benchmark weight for U2 and U3) | Always |
| B2a | **Best single indicator, fold-honest:** the best member, selected by the same procedure on the same training fold | The primary comparison for "does combining add value" |
| B2b | Published fleet winner of the best member (`results/*/winner_summary.json` @ 3d735ec7) | Labelled *contaminated*, descriptive only |
| B3 | **Naive equal-weight composite:** expanding z-scores of the same members, signs fixed by economic prior, threshold 0 (or majority vote for binary states) | No fitted parameters |
| B4 | Trend / volatility baseline: 10-month SMA on the target (Faber 2007) for U1/U5; a 10%-volatility target for U2 (R6) | Checks whether the combination only rediscovers trend |

### 0.4 Validation designs (V)

| Code | Design | Window | When usable |
|------|--------|--------|-------------|
| **V-A** | **Nested, purged walk-forward CV inside the fleet IS.** Outer: expanding window, 5 blocked test folds over about 1998→2016. Inner: selection only within each outer training span. 12-month purge plus 12-month embargo around each test fold (López de Prado 2018) | About 1998 → 2016 | Default for every question |
| **V-B** | **Backward holdout, never used by the fleet.** Fleet IS starts about 1997–2002 (`is_period_start`). | 1980/85 → 1997 | Members with long history: real-time INDPRO, UNRATE, HOUST, M2SL (ALFRED from 1980); revised ISM, NAHB; T10Y3M from FRED. Needs an S&P 500 total-return proxy before 1993 (gap G5 in `DATA_TOOL_INVENTORY.md`). Sectors: S&P 500 GICS sector price indices exist from 1989-09 in `etf_prices` (price only); Fama–French industry portfolios are needed for before 1989 |
| **V-C** | **Forward paper-trade.** Freeze the spec (hash), record live positions monthly from 2026-11, evaluate at 12/24/36 months | 2026-11 → | Every pre-registered finalist; low power, acknowledged |
| V-D | Existing fleet OOS (about 2017 → 2026) | — | **Descriptive only**, never for selection; flagged as viewed many times |

### 0.5 Null and multiple-testing checks (N)

| Code | Check | What it rules out |
|------|-------|-------------------|
| N1 | **Joint circular block shift** of the whole indicator panel against the returns, K ≥ 500 (harness `null.py` logic, extended from one series to a panel). It keeps the cross-indicator correlation and breaks the link to returns. | Chance alignment of the combination with a few episodes |
| N2 | **Random-member null:** replace members with random draws from the same blocks or other blocks, same operator | "Any combination would do", i.e. the gain comes from the operator alone |
| N3 | **Re-selection null** for frozen fleet winners: inside each N1 draw, re-run each member's single-indicator selection, then combine | Novy-Marx (2015/16) multiple-signal bias |
| N4 | Family-wise control over the whole bank: Romano–Wolf stepdown or Hansen SPA on the primary metric; deflated Sharpe ratio (Bailey & López de Prado 2014) with N_eff from D2-03; probability of backtest overfitting (PBO) by CSCV (Bailey et al. 2017) for any question that searches more than 20 configurations | Survivorship within the family |

### 0.6 Use cases and primary metrics (U)

| Code | Use case | Primary metric | Secondary |
|------|----------|----------------|-----------|
| U1 | Risk-off overlay (asset vs T-bills) | Max drawdown, monthly CVaR 5% | Calmar, upside capture, time invested, Sharpe |
| U2 | Allocation tilt (equity weight 0.5–1.0) | Return per unit of tracking error vs a static weight; CVaR | Turnover, Sharpe |
| U3 | Sector rotation / relative return | Relative return and IR vs SPY or vs the basket | Sign hit rate |
| U4 | Recession / regime classification | AUROC vs NBER months; lead time; false alarms per decade | Brier score; recession-month hit rate |
| U5 | Entry timing (re-entry after risk-off) | Forward 6m/12m return after the signal vs unconditional; missed-rally cost | Time to recovery |

### 0.7 Shorthand for availability

The start dates are the first month-end reading on the revised-as-of / real-time tracks, from
`data/coverage_and_lags.csv`. Assets: SPY from 1993-01; the 9 original sector SPDRs from 1998-12.

| Start | Indicators |
|-------|------------|
| From 1985 (revised) | indpro, unrate, umcsent, houst, permit, nhs, m2, busloans, ism_mfg, nahb, umich_exp, import_px |
| From the 1990s | sloos 1990, cc_delinq 1992, rsxfs / neworder / amtmno / inv_sales 1993, sox_spy 1995, ism_svc 1997, crude_inv 1991 |
| From 2000+ (local files) | t10y3m, hy_oas, hy_ig 2000; gold_copper 2001; eci 2002; vix_ratio 2007; cement 2007; Cass 2017 (revised track truncated) |
| Real-time vintages from | 1985 for indpro / unrate / houst / m2; busloans 1996; neworder 1997; umcsent 1998; permit / nhs 1999; rsxfs 2001; sloos 2010; import_px 2010; cc_delinq / amtmno 2011; Cass / inv_sales 2013 |

---

## 1. Direction 1 — combinations that serve real use cases

### R1 Confirmation

#### D1-01 — Housing contraction confirmed by credit widening (risk-off)
- **Question.** Over IS-nested folds, does moving SPY to T-bills only when a housing contraction state AND a credit
  widening state hold together reduce max drawdown and CVaR relative to each signal alone, at no worse than a
  20% loss of upside capture?
  - Housing contraction: permits YoY < 0, as known at t.
  - Credit widening: HY–IG spread 63-day change > 0 and z(252d) > 1.
- **Use case.** U1 risk-off overlay.
- **Indicators and roles.** PERMIT (cycle lead, housing block B2) AND HY–IG (market confirmation, B3). Variant:
  SLOOS net tightening > 0 instead of HY–IG (bank-credit confirmation, B4).
- **Assets.** SPY; secondary XLY, XLF, XHB.
- **Combination type.** R1 confirmation, 2-of-2 (OR shown for contrast).
- **Metric and baselines.** Max drawdown, CVaR 5%, time invested, false exits per decade; B1, B2a (each member),
  B3, B4.
- **Data / PIT.** PERMIT real-time from 1999 (revised from 1985); HY–IG from 2000 locally (FRED ICE BofA from
  1996–97). Common: 2000-01 (real-time from 2000).
- **MT / validation.** 2 variants × 2 operators = 4 tests; V-A primary, V-D descriptive, V-C if it passes; N1, N2.
- **Feasibility.** H. Both series are already in the pipelines.
- **Priority.** P2. A clean confirmation test, but it overlaps D1-04 and D1-12.

#### D1-02 — Curve inversion plus labour deterioration as a recession classifier
- **Question.** In real time, does a two-condition rule classify NBER recession months with a higher AUROC and fewer
  false alarms per decade than either the curve rule or the Sahm-type rule alone, at an equal or longer lead time?
  - Curve: T10Y3M < 0 at any time in the past 12 months.
  - Labour: UNRATE 3-month average minus its 12-month low ≥ 0.3pp, real-time vintage.
- **Use case.** U4 classification; overlay variant U1 (SPY to T-bills when the classifier is on).
- **Indicators and roles.** T10Y3M (early warning, B3); UNRATE real-time (confirmation, B1).
- **Assets.** NBER recession months (label); SPY for the overlay variant.
- **Combination type.** R1 confirmation (with an R4 time window: the curve inverted within the last 12 months).
- **Metric and baselines.** AUROC, lead time from the NBER peak, false alarms per decade, Brier score; overlay: max
  drawdown, CVaR. Baselines: each member alone, B3 (z-average of −curve and ΔUNRATE), B4.
- **Data / PIT.** UNRATE vintages from 1980; T10Y3M from FRED back to 1982 (local file 2000+). NBER dates are
  announced with a 6–18 month lag: used only as an *ex-post label*, never as an input. Common: 1982 (V-B covers
  1982–1997, with recessions in 1990–91 only; 1981–82 is partly covered).
- **MT / validation.** 3 rule variants (window 6/12/18 months); V-B and V-A; event count is small (2001, 2008, 2020
  in V-A; 1990 in V-B), so report each episode, not only averages; N1 on the panel.
- **Feasibility.** H.
- **Priority.** **P1.** Strong literature prior (Estrella & Mishkin 1998; Sahm 2019), few degrees of freedom and a
  long real-time history.

#### D1-03 — 2-of-3 within the housing block as noise reduction
- **Question.** Does requiring 2 of the 3 housing contraction flags lower the false-exit rate of a risk-off overlay
  without increasing max drawdown, compared with any single housing flag?
  - The three flags: starts YoY < 0, permits YoY < 0, new home sales YoY < 0.
- **Use case.** U1.
- **Indicators and roles.** HOUST, PERMIT, HSN1F: three noisy measures of one block (B2).
- **Assets.** SPY, XHB (sensitivity).
- **Combination type.** R1 k-of-n within one block.
- **Metric and baselines.** False exits per decade, max drawdown, CVaR; B2a, B3 (housing z-average), B4.
- **Data / PIT.** Real-time from 1999 (permits and new home sales), revised from 1985. Release lags 18 / 18 / 25
  days median. Note revision noise: real-time vs revised correlation is 0.94 for new home sales YoY.
- **MT / validation.** k ∈ {1,2,3}: 3 tests; V-A, V-B (revised track only); N2 (random 3-of-block from other
  blocks).
- **Feasibility.** H.
- **Priority.** P3. Informative for the redundancy question (D2-06) but unlikely to change practice.

### R2 Filter / regime conditioning

#### D1-04 — Do monthly macro signals matter only in market stress?
- **Question.** Is the spread in next-month SPY returns between bullish and bearish macro states larger when the
  market-stress filter is on than when it is off?
  - Macro states: the frozen ISM manufacturing 1m-diff rule and the new-orders YoY z rule.
  - Stress filter: VIX/VIX3M ≥ 1, or HY–IG z(252d) > 1, at the rebalance close.
- And does a filtered overlay (act on macro only in stress) improve CVaR relative to the unfiltered macro rule?
- **Use case.** U1; insight for U5.
- **Indicators and roles.** ISM_MFG, NEWORDER (direction signal); VIX ratio or HY–IG (regime filter).
- **Assets.** SPY.
- **Combination type.** R2 filter (binary regime). Variant: the causal 2-state HMM filtered P(stress) > 0.5 on
  VIX ratio and HY–IG features.
- **Metric and baselines.** Conditional return spread with a HAC t-statistic; overlay CVaR and max drawdown; B2a
  (macro alone), B3, B4.
- **Data / PIT.** VIX3M from 2007 limits the VIX-ratio variant to 2007+ (inside the viewed window). The HY–IG
  variant covers 2000+, so it is preferred. ISM is revised-only; NEWORDER is real-time from 1997.
- **MT / validation.** 2 macro signals × 2 filters (+ HMM) = 6 tests; V-A; stress months are about 10–20% of the
  sample, so report the number of stress episodes; N1, N2 (random filter of equal frequency).
- **Feasibility.** H.
- **Priority.** **P1.** It tests a central claim (state dependence) with few extra parameters, and it uses existing
  causal regime code.

#### D1-05 — Is the yield-curve signal conditional on the credit regime?
- **Question.** Does the curve rule (t10y3m 3-month change > threshold, procyclical, the frozen fleet winner)
  predict SPY returns only when credit spreads are widening (HY OAS 63-day change > 0)?
- **Use case.** U1 / U4.
- **Indicators and roles.** T10Y3M (signal); HY OAS (regime).
- **Assets.** SPY.
- **Combination type.** R2 filter.
- **Metric and baselines.** Conditional return spread; overlay max drawdown and CVaR; B2a, B3, B4.
- **Data / PIT.** 2000+ locally; FRED extends HY OAS to 1997. Both daily, sampled at month-end.
- **MT / validation.** 2 tests (filter on / off rules); V-A, V-D; N1, N3 (the curve member is a fleet winner).
- **Feasibility.** H.
- **Priority.** P2.

#### D1-06 — Monetary regime as a filter for the M2 signal
- **Question.** Is the M2 YoY-acceleration rule's information about SPY returns different when the fed funds rate is
  rising (12-month change > 0) than when it is falling?
- **Use case.** U2 allocation tilt.
- **Indicators and roles.** M2SL real-time (signal); fed funds 12-month change (regime).
- **Assets.** SPY.
- **Combination type.** R2 filter.
- **Metric and baselines.** Tracking-error-adjusted return vs a static 0.75 weight; conditional spread; B2a (M2
  alone), B3, B4.
- **Data / PIT.** M2 real-time from 1985; M2 is published after the close until 2021-02 (after-close rule in
  `release_calendar_meta.json`); fed funds is a market rate. V-B is possible from 1985.
- **MT / validation.** 2 tests; V-B and V-A; N1.
- **Feasibility.** H.
- **Priority.** P3. The fleet winner `m2sl_yoy_spy` is strong in the viewed OOS, so this is a check on whether it
  is regime-bound.

#### D1-07 — Late-cycle regime and defensive vs cyclical sectors
- **Question.** In a pre-registered late-cycle regime, does an equal-weight defensive basket (XLV, XLP, XLU)
  outperform an equal-weight cyclical basket (XLI, XLY, XLB, XLF) over the next 3 months, and is that relative
  return larger than the one implied by either condition alone?
  - Late-cycle definition: T10Y3M < 0.5pp AND ISM manufacturing 3-month change < 0.
- **Use case.** U3 sector rotation.
- **Indicators and roles.** T10Y3M, ISM_MFG (regime definition by confirmation).
- **Assets.** The defensive − cyclical basket spread; single sectors as secondary.
- **Combination type.** R2 regime + R1 definition.
- **Metric and baselines.** Relative return, IR, sign hit rate; B1 (equal-weight all 9 sectors), B2a, B3. B4 here
  is the relative-momentum rule (12-month relative return).
- **Data / PIT.** Sectors from 1999 (12-month warm-up for momentum); 1989–1998 via the S&P 500 sector price indices in `etf_prices` (no dividends).
- **MT / validation.** 3 tests (basket, two single-sector checks); V-A over 1999–2016; N2.
- **Feasibility.** M. Sector data are in `etf_prices`, but no sector pipeline exists yet.
- **Priority.** P2. Sector rotation over the cycle has weak support in the literature (e.g. Stangl, Jacobsen &
  Visaltanachoti 2009), so expect a null result. Either answer is useful.

### R3 Composite

#### D1-08 — Block-representative equal-weight composite vs the best single indicator
- **Question.** Does an equal-weight composite of one pre-chosen representative per block deliver a lower max
  drawdown and CVaR than (a) the best single representative selected fold-honestly and (b) a PCA-weighted
  composite estimated in real time?
  - The composite: z-scores with prior signs, threshold 0.
  - Representatives: B1 INDPRO YoY, B2 PERMIT YoY, B3 HY–IG, B4 SLOOS, B5 UMCSENT, B6 ISM_MFG, B7 M2 YoY.
- **Use case.** U1; U2 variant (weight = clip(0.75 + 0.25·composite, 0.5, 1)).
- **Indicators and roles.** 7 representatives, one per block; equal weight.
- **Assets.** SPY; then all 9 sectors (breadth of result).
- **Combination type.** R3 composite.
- **Metric and baselines.** Max drawdown, CVaR, upside capture; tracking-error-adjusted return for U2; B1, B2a, B3
  (here the composite *is* B3, so the test is B3 vs B2a, then vs the PCA weighting), B4.
- **Data / PIT.** Common start 2000 (HY–IG); real-time members from 1999 (permits); V-B without HY–IG (replace it
  with T10Y3M) from 1985.
- **MT / validation.** 2 composites × 2 use cases = 4 tests; V-A, V-B, V-C; N1, N2 (random representatives within
  the same blocks: is the choice of representative material?).
- **Feasibility.** H.
- **Priority.** **P1.** Lowest-DoF test of the "forecast combination puzzle" (Timmermann 2006; Rapach, Strauss &
  Zhou 2010), with no tuning.

#### D1-09 — Diffusion index of the fleet's frozen rules
- **Question.** Does the cluster-weighted share of frozen fleet single-indicator rules that are in a risk-off state
  at month-end predict the next 12 months' SPY drawdown > 15% and NBER recession months better than any single
  rule?
  - Cluster weighting: one vote per correlation block.
- **Use case.** U4, then a U1 overlay (exposure = 1 − share).
- **Indicators and roles.** All registered winners (35 live pairs, deduplicated to one per series), frozen as of
  3d735ec7.
- **Assets.** SPY.
- **Combination type.** R7 diffusion (R1 generalised).
- **Metric and baselines.** AUROC; overlay max drawdown and CVaR; B2a, B3, B4.
- **Data / PIT.** The common sample is short if all members must exist (about 2007+); use an unbalanced breadth
  (share of *available* members) as a pre-registered variant.
- **MT / validation.** The members are already-selected winners, so **N3 is mandatory**: inside each null draw,
  re-select every member. V-A cannot be used directly, because the members were selected on IS + OOS. Use V-B (for
  members with long history) and V-C. 2 tests.
- **Feasibility.** M. It needs every pair's position series in one PIT frame.
- **Priority.** **P1** as a *descriptive tool* (cheap, intuitive, user-facing); P3 as a strategy claim.

#### D1-10 — Does estimating weights beat fixed equal weights?
- **Question.** With the D1-08 members fixed, does any estimated-weight composite beat the fixed equal-weight
  composite out-of-fold on CVaR and tracking-error-adjusted return?
  - Estimated weights: expanding-window ridge logit on 12-month drawdown events, expanding real-time PC1, or
    inverse-variance weights.
- **Use case.** U2.
- **Indicators and roles.** Same 7 representatives.
- **Assets.** SPY.
- **Combination type.** R3 estimated vs fixed weights.
- **Metric and baselines.** Out-of-fold CVaR and tracking-error-adjusted return; B3 (fixed equal weight) is the
  key baseline.
- **Data / PIT.** As D1-08.
- **MT / validation.** 3 weightings; V-A nested (weights estimated only on inner folds); PBO by CSCV; N1.
- **Feasibility.** H.
- **Priority.** P2. It completes D1-08.

#### D1-11 — A housing composite vs single housing indicators
- **Question.** Does an equal-weight housing composite improve risk-off performance for SPY and relative
  performance for housing-sensitive sectors over the best single housing indicator?
  - Composite members: HOUST, PERMIT, HSN1F YoY, NAHB level, cement YoY.
  - Housing-sensitive sectors: XHB, XLB, XLY vs SPY.
- **Use case.** U1 and U3.
- **Indicators and roles.** Five housing series (B2), equal-weight composite.
- **Assets.** SPY, XHB, XLB, XLY (relative).
- **Combination type.** R3 within one block.
- **Metric and baselines.** Max drawdown and CVaR (SPY); relative return and IR (sectors); B2a, B4.
- **Data / PIT.** Cement has a 72-day median lag, up to 165 days since 2025-07: the staleness rule (T5) matters.
  It starts in 2007, so a 4-member variant without cement is pre-registered for 1999+.
- **MT / validation.** 2 composites × 4 assets = 8 tests; V-A; N2.
- **Feasibility.** H.
- **Priority.** P2. Ten fleet pairs are housing-based, so this directly asks whether that effort collapses to one
  signal (Leamer 2007).

### R4 Sequencing

#### D1-12 — Credit → manufacturing chain
- **Question.** Does a sequence rule give earlier and more reliable SPY risk-off timing than either step alone or
  their simultaneous AND?
  - Sequence: bank credit tightening (SLOOS net tightening > 20) OR HY OAS widening, followed within 3–9 months by
    ISM manufacturing < 50.
- **Use case.** U1 and U4.
- **Indicators and roles.** SLOOS / HY OAS (first link: credit); ISM_MFG (second link: manufacturing). An optional
  third link, INDPRO YoY < 0, stands in for earnings. Earnings data are a gap.
- **Assets.** SPY; XLI (relative).
- **Combination type.** R4 sequencing with a pre-registered order and windows {3, 6, 9}.
- **Metric and baselines.** Lead time from the market peak, max drawdown, false exits; B2a (each link), B3
  (simultaneous AND / composite), B4.
- **Data / PIT.** SLOOS is quarterly, published *inside* the reference quarter (median −56 days vs quarter-end);
  real-time from 2010, revised from 1990. ISM is revised-only from 1948. Common: 1990 (revised), with V-B over
  1990–1997 covering the 1990–91 recession.
- **MT / validation.** 3 windows × 2 credit variants = 6 tests; V-A, V-B; event-level reporting; N1, N2 (random
  ordering: is the order material?).
- **Feasibility.** M.
- **Priority.** P2. It is economically the most interesting chain, but has few cycles.

#### D1-13 — Housing → labour sequencing for recession calls
- **Question.** Does "permits YoY < 0, followed within 12 months by a real-time UNRATE rise ≥ 0.3pp" identify NBER
  recessions with fewer false alarms than the Sahm-type rule alone, and earlier than it?
- **Use case.** U4.
- **Indicators and roles.** PERMIT (first link); UNRATE (second link).
- **Assets.** NBER label; SPY overlay variant.
- **Combination type.** R4.
- **Metric and baselines.** AUROC, lead time, false alarms per decade; B2a, B3.
- **Data / PIT.** Real-time UNRATE from 1980, PERMIT from 1999 (revised from 1985). V-B covers 1985–1997.
- **MT / validation.** 2 windows; V-A, V-B; N1.
- **Feasibility.** H.
- **Priority.** P2. Pair it with D1-02 as competing recession classifiers.

#### D1-14 — Re-entry timing after a risk-off episode
- **Question.** After an overlay has moved to cash, does re-entering when ≥ 2 of 3 early-cycle signals turn reduce
  the missed-rally cost over the next 12 months compared with re-entering on any single signal or on the 10-month
  SMA?
  - Early-cycle signals: T10Y3M 3-month change > 0.5pp (steepening), new orders YoY z rising for 2 months, HY–IG
    63-day change < 0.
- **Use case.** U5 entry timing.
- **Indicators and roles.** T10Y3M, NEWORDER, HY–IG (re-entry vote); the exit rule is held fixed (B4 SMA exit).
- **Assets.** SPY.
- **Combination type.** R4 staged (exit fixed, re-entry by R1 vote).
- **Metric and baselines.** Missed-rally cost, forward 6m/12m return after entry, time to recovery; B4 re-entry is
  the key baseline.
- **Data / PIT.** 2000+; NEWORDER real-time from 1997.
- **MT / validation.** 3 tests; few episodes (2002–03, 2009, 2020, 2022–23), so report per episode; N2.
- **Feasibility.** M.
- **Priority.** **P1.** Re-entry is the weakest part of most overlays and a real practitioner pain point.

#### D1-15 — Is the lead order among our indicators stable across cycles?
- **Question.** For each indicator, where does its cyclical turning point fall relative to NBER peaks and troughs in
  1990, 2001, 2008 and 2020 (on the PIT panel), and is the rank order of leads stable enough (Kendall W > 0.5) to
  justify any pre-registered chain?
  - Turning-point dating: Bry–Boschan.
- **Use case.** A process prerequisite for U4 and U5 (sequencing).
- **Indicators and roles.** All 29.
- **Assets.** None (descriptive).
- **Combination type.** A diagnostic for R4.
- **Metric and baselines.** Lead (months) per indicator per cycle; Kendall's W concordance; a random-order null.
- **Data / PIT.** Revised-as-of panel (built); real-time sensitivity on ALFRED series.
- **MT / validation.** Descriptive; a permutation null for W.
- **Feasibility.** H. The panel exists.
- **Priority.** **P1.** Cheap, and it gates D1-12, D1-13 and D1-14: if the order is unstable, sequencing questions
  are demoted.

### R5 Divergence

#### D1-16 — Soft vs hard data divergence
- **Question.** When survey data diverge from hard data, which converges to which over the next 6 months, and does
  the divergence state predict SPY returns or the XLY − XLP relative return?
  - Divergence: the z-gap |z(soft) − z(hard)| > 1 with persistence of at least 2 months.
  - Survey data: UMCSENT, UMich expectations, NAHB.
  - Hard data: RSXFS YoY, INDPRO YoY.
- **Use case.** U3; insight for U2.
- **Indicators and roles.** A soft composite vs a hard composite.
- **Assets.** SPY, XLY − XLP.
- **Combination type.** R5 divergence.
- **Metric and baselines.** Convergence direction hit rate; conditional forward return; B1, B3 (soft + hard
  average).
- **Data / PIT.** From 1993 (RSXFS revised) / 2001 (RSXFS real-time); UMCSENT real-time from 1998.
- **MT / validation.** 2 thresholds × 2 targets = 4 tests; **N2** (divergence between independently shifted members
  is common by chance); V-A, V-B.
- **Feasibility.** H.
- **Priority.** P2.

#### D1-17 — Market stress vs slow macro: false alarm or early warning?
- **Question.** When market stress indicators flag stress but slow macro indicators do not, what are the next 3- and
  12-month SPY returns, and in what share of episodes did macro later confirm?
  - Market stress: HY–IG z > 1, VIX/VIX3M ≥ 1, gold/copper YoY > 20%.
  - Slow macro: ISM manufacturing > 50, UNRATE 6-month change ≤ 0.
- **Use case.** U5 (buy the false alarm) and U1 (respect the early warning).
- **Indicators and roles.** A market composite vs a macro composite.
- **Assets.** SPY.
- **Combination type.** R5.
- **Metric and baselines.** Forward returns by divergence state; confirmation rate; B1, B4.
- **Data / PIT.** 2000+ (2007+ with the VIX ratio).
- **MT / validation.** 2 horizons; descriptive plus N1; V-A.
- **Feasibility.** H.
- **Priority.** P2. The answer is directly usable as a rule of thumb.

#### D1-18 — Equity internals vs manufacturing for tech relative returns
- **Question.** When SOX/SPY 6-month momentum is strong (> 0) but ISM manufacturing is falling (3-month change < 0),
  does XLK underperform SPY over the next 3 months relative to periods when the two agree?
- **Use case.** U3.
- **Indicators and roles.** SOX/SPY (market internals); ISM_MFG (macro).
- **Assets.** XLK − SPY; QQQ − SPY.
- **Combination type.** R5.
- **Metric and baselines.** Relative return, IR; B1 (equal weight), B2a, B4 (relative momentum).
- **Data / PIT.** From 1999 (XLK).
- **MT / validation.** 2 tests; V-A; N2.
- **Feasibility.** H.
- **Priority.** P3.

### R6 Direction-vs-sizing split

#### D1-19 — Macro sets the direction, market risk sets the size
- **Question.** Does an exposure rule improve CVaR and max drawdown over (a) direction-only, (b) sizing-only and
  (c) a pure 10%-volatility target, without lowering the Sharpe ratio?
  - Exposure: w_t = d_t · g_t.
  - Direction d_t ∈ {0, 1}, from the D1-08 composite.
  - Size g_t = clip(target vol / forecast vol, 0.25, 1). The volatility forecast comes from the VIX level, or from
    21-day realised volatility of SPY.
- **Use case.** U2 (and U1).
- **Indicators and roles.** Macro composite (direction); VIX or realised volatility (size).
- **Assets.** SPY; then XLI, XLY.
- **Combination type.** R6.
- **Metric and baselines.** CVaR, max drawdown, Sharpe, turnover; baselines (a), (b), (c), B1. (c) is the B4
  variant for R6.
- **Data / PIT.** VIX from 1990 (in the `hy_ig` parquet from 2000); realised volatility from SPY 1993.
- **MT / validation.** 2 volatility sources × 2 caps = 4 tests; V-A, V-C; N1 on the direction member only (sizing
  has no lookahead by construction; check the realised-volatility window ends at t).
- **Feasibility.** H.
- **Priority.** **P1.** It matches how practitioners actually run overlays, and it guards against crediting a
  volatility effect to macro data (Moreira & Muir 2017; Cederburg et al. 2020).

#### D1-20 — Conviction sizing by vote count
- **Question.** Does sizing exposure by the share of agreeing block representatives (0, ¼, ½, ¾, 1) beat the binary
  majority rule on CVaR and tracking-error-adjusted return?
- **Use case.** U2.
- **Indicators and roles.** The 7 representatives (vote) → size.
- **Assets.** SPY.
- **Combination type.** R6 with R7 sizing.
- **Metric and baselines.** CVaR, tracking-error-adjusted return; B3 (binary majority), B1.
- **Data / PIT.** As D1-08.
- **MT / validation.** 2 tests; V-A; N1.
- **Feasibility.** H.
- **Priority.** P3.

### Cross-asset and process questions

#### D1-21 — Do combinations improve defensive-sector timing beyond the existing XLV/XLP pairs?
- **Question.** Does adding a second indicator with a different role improve the XLV and XLP relative-return IR
  over the fleet's single-indicator pairs (`umcsent_xlv`, `indpro_xlp`), fold-honestly?
  - XLP: a credit filter, HY–IG z > 1.
  - XLV: a curve filter, T10Y3M < 0.5pp.
- **Use case.** U3.
- **Indicators and roles.** UMCSENT / INDPRO (direction) + HY–IG / T10Y3M (filter).
- **Assets.** XLV − SPY, XLP − SPY, XLU − SPY.
- **Combination type.** R2.
- **Metric and baselines.** Relative return, IR; B2a (the single pair re-selected in-fold); B2b (published,
  contaminated).
- **Data / PIT.** From 1999.
- **MT / validation.** 3 assets × 2 filters = 6 tests; V-A; N3 (members are fleet pairs).
- **Feasibility.** M.
- **Priority.** P3.

#### D1-22 — Cyclical − defensive basket: which role helps most?
- **Question.** For the cyclical − defensive basket spread, which single role gives the largest out-of-fold IR gain
  over the best single indicator: confirmation (D1-01 type), filter (D1-07), composite (D1-08) or divergence
  (D1-16)?
- **Use case.** U3.
- **Indicators and roles.** As in the referenced questions (no new members).
- **Assets.** The basket spread.
- **Combination type.** A comparison across R1, R2, R3 and R5.
- **Metric and baselines.** IR; B2a, B3.
- **Data / PIT.** From 1999.
- **MT / validation.** 4 tests, counted within the family; V-A; N4.
- **Feasibility.** M. It depends on D1-07 and D1-08 infrastructure.
- **Priority.** P3.

#### D1-23 — A calibrated real-time recession probability as an overlay
- **Question.** Does a small real-time logit (T10Y3M, UNRATE change, PERMIT YoY, HY–IG; expanding-window
  estimation) produce calibrated recession probabilities (Brier score, reliability curve), and does the overlay
  w = 1 − P(recession) beat the binary D1-02 rule on CVaR?
- **Use case.** U4 → U1.
- **Indicators and roles.** Four members in a probabilistic composite.
- **Assets.** NBER label; SPY.
- **Combination type.** R3 (estimated) with R6 sizing.
- **Metric and baselines.** Brier score, AUROC; overlay CVaR; baselines: D1-02 (binary), B3, B4.
- **Data / PIT.** From 1999/2000 for all members (real-time permits); V-B with the curve + UNRATE subset from 1982.
- **MT / validation.** 2 tests; V-A (expanding fits), V-B; N1.
- **Feasibility.** H.
- **Priority.** P2.

#### D1-24 — Daily updating of a monthly combination
- **Question.** For the D1-08 composite, does re-evaluating the composite daily beat monthly rebalancing on max
  drawdown after realistic costs (5–10 bp per trade)?
  - Daily evaluation: daily market members are updated at each close; monthly members only on their release dates
    (as-of).
- **Use case.** U1. A process question about mixed frequency.
- **Indicators and roles.** As D1-08.
- **Assets.** SPY.
- **Combination type.** Any; alignment variant A3 (daily as-of).
- **Metric and baselines.** Max drawdown, turnover, cost-adjusted Sharpe; the monthly version is the baseline.
- **Data / PIT.** `release_calendar.csv` gives exact dates (after-close rule for BUSLOANS and pre-2021 M2).
- **MT / validation.** 2 tests; V-A; N1.
- **Feasibility.** M. The harness is single-frequency per pair.
- **Priority.** P3.

#### D1-25 — Does revision noise inflate composites?
- **Question.** For each D1 finalist, how large is the performance gap between the real-time-vintage version and the
  revised-as-of version, and is the gap larger for composites than for their single members?
  - Revision gaps are large for INDPRO, NEWORDER and new home sales (real-time vs revised correlation 0.90–0.94).
- **Use case.** All (a process / robustness question).
- **Indicators and roles.** ALFRED members of each finalist.
- **Assets.** As in each finalist.
- **Combination type.** Any.
- **Metric and baselines.** The primary metric's gap (revised − real-time); single members' gaps as baselines.
- **Data / PIT.** Vintages exist (`data/release_calendar/vintages/`); no-archive members cannot be tested, which is
  disclosed.
- **MT / validation.** Not a selection exercise; reported for every finalist.
- **Feasibility.** H. Harness track (b) does this.
- **Priority.** P2 (mandatory reporting, not a separate search).

---

## 2. Direction 2 — how many variations, and how many are real?

#### D2-01 — Raw size of the combination space
- **Question.** Counting each dimension (series, member rule, k, operator structure, asset, alignment), how many
  distinct combination configurations exist for k = 2, 3, 4?
- **Use case.** Planning the search budget.
- **Indicators and roles.** All.
- **Assets.** All 20 targets.
- **Combination type.** All roles.
- **Metric and baselines.** Counts. **Preliminary answer** (`COMBINATORICS.md` § 2): about 8 × 10^11 (k = 2) and
  4 × 10^16 (k = 3) with re-searched members; 8 × 10^5 and 4 × 10^7 with frozen members.
- **Data / PIT.** Registry and winner summaries.
- **MT / validation.** None (descriptive).
- **Feasibility.** H. Done in draft.
- **Priority.** P1 (complete; refresh when the registry changes).

#### D2-02 — Effective number of independent indicator dimensions under PIT
- **Question.** How many independent dimensions do the PIT indicator readings span, on the real-time vs revised
  tracks and on levels vs changes, and which blocks do they form?
- **Use case.** Defining blocks; sizing a plausible "idea space".
- **Indicators and roles.** 29 indicators.
- **Assets.** None.
- **Combination type.** —
- **Metric and baselines.** Parallel analysis, participation ratio, entropy rank, M_eff, clusters. **Preliminary
  answer:** about 5–8 on levels (parallel analysis 5, participation ratio 5.6, 10 clusters at |ρ| ≥ 0.5; core 23,
  2001–2026); about 4–6 on the real-time ALFRED track. Phase 2 adds a block-permutation parallel analysis that
  respects autocorrelation.
- **Data / PIT.** Built (`data/panel_*`).
- **MT / validation.** Sub-period stability (done: before 2008 vs from 2008).
- **Feasibility.** H.
- **Priority.** P1 (draft done; the refinement is cheap).

#### D2-03 — Effective number of independent strategy-return streams
- **Question.** Across the 29 frozen fleet winners, how many effectively independent *strategy-return* and position
  streams are there? This is the N_eff to use in the deflated Sharpe ratio and the family-wise correction for every
  combination question.
  - Measured by eigenvalues of the return correlation matrix on the common window, and by Li–Ji M_eff.
- **Use case.** Calibrating the multiple-testing machinery.
- **Indicators and roles.** 29 winners' positions (P1/P2/P3 as published).
- **Assets.** SPY mostly; XLI, XLP, XLV for the cross-asset pairs.
- **Combination type.** —
- **Metric and baselines.** M_eff and participation ratio of position and return correlations; compare with D2-02.
- **Data / PIT.** Needs each pair's position series on a common PIT month-end frame. They exist in pipeline outputs
  but are not consolidated.
- **MT / validation.** Descriptive.
- **Feasibility.** H/M.
- **Priority.** **P1.** It is the denominator for every later correction.

#### D2-04 — Does dimensionality collapse in downturns?
- **Question.** On a rolling 60-month window, does the effective dimension (participation ratio) of the PIT panel
  fall in and around recessions? If so, combinations diversify least when they are needed most.
- **Use case.** Risk awareness for U1 and U4.
- **Indicators and roles.** Core 23.
- **Assets.** None.
- **Combination type.** —
- **Metric and baselines.** Rolling participation ratio; the difference between NBER and non-NBER windows; block
  bootstrap CI. Preliminary hint: 3.5 before 2008 vs 5.2 from 2008. The pre-2008 window includes the 2001 cycle,
  and its sample is small.
- **Data / PIT.** Built.
- **MT / validation.** Descriptive with a bootstrap.
- **Feasibility.** H.
- **Priority.** P2.

#### D2-05 — Marginal value of the k-th indicator
- **Question.** Adding block representatives one at a time in a pre-registered order, where does the out-of-fold
  CVaR and max-drawdown improvement of the equal-weight composite plateau, and does the plateau coincide with the
  effective dimension (about 5–8)?
  - Order: by block, by economic prior.
- **Use case.** U1. It answers "how many indicators is enough".
- **Indicators and roles.** The 7–8 representatives.
- **Assets.** SPY, then sectors.
- **Combination type.** R3, k = 1…8.
- **Metric and baselines.** The CVaR / max drawdown curve vs k; B2a (k = 1); the random-order null (N2: 100
  random orders).
- **Data / PIT.** As D1-08.
- **MT / validation.** One pre-registered order is the test; random orders give the null; V-A, V-B.
- **Feasibility.** H.
- **Priority.** **P1.** It answers Direction 2 in practical terms.

#### D2-06 — Within-block redundancy: does a second member add anything?
- **Question.** Within each multi-member block (housing, activity, credit market, sentiment), does adding a second
  member to the best member improve out-of-fold U1/U4 metrics? Is the identity of the "best" member stable across
  folds?
- **Use case.** Pruning; deciding which pairs are substitutes.
- **Indicators and roles.** Block members.
- **Assets.** SPY.
- **Combination type.** R3 / R1 within a block.
- **Metric and baselines.** Incremental AUROC / CVaR; selection stability (the share of folds that choose the same
  member).
- **Data / PIT.** Built.
- **MT / validation.** 4 blocks; V-A; N2.
- **Feasibility.** H.
- **Priority.** P2. Relevant to the 10 housing pairs.

#### D2-07 — Which matters more: the members or the operator?
- **Question.** For fixed member sets, how much of the variance of outcomes across configurations is explained by
  the operator (R1/R2/R3/R5/R6) vs by member choice? This is a variance decomposition over a small pre-registered
  grid: 7 representatives, pairs, 5 operators, i.e. 21 × 5 = 105 configurations.
- **Use case.** Planning; it tells us where the degrees of freedom are.
- **Indicators and roles.** The 7 representatives.
- **Assets.** SPY.
- **Combination type.** All.
- **Metric and baselines.** ANOVA share of the primary metric; PBO of the grid.
- **Data / PIT.** As D1-08.
- **MT / validation.** **Run only on V-A inner folds.** No selection is made from it.
- **Feasibility.** H.
- **Priority.** P2.

#### D2-08 — How wide can a search be before it is mostly overfit?
- **Question.** As the searched family grows (10 → 100 → 1,000 → 10,000 configurations, nested), how does the
  probability of backtest overfitting (CSCV) and the deflated Sharpe ratio of the best configuration evolve, and at
  what breadth does PBO exceed 0.5?
- **Use case.** Setting the admissible search budget for Phase 2+.
- **Indicators and roles.** Block representatives with a growing operator / threshold grid.
- **Assets.** SPY.
- **Combination type.** All.
- **Metric and baselines.** PBO, deflated Sharpe ratio, performance degradation (IS → out-of-fold).
- **Data / PIT.** As D1-08.
- **MT / validation.** It is itself the multiple-testing study; V-A only.
- **Feasibility.** M (compute).
- **Priority.** **P1.** It converts "how many variations" into "how many we may afford to try".

#### D2-09 — Common-sample and power budget by k
- **Question.** For each candidate member set, what common PIT sample remains (balanced), and what is the minimum
  detectable improvement on each primary metric at that length, given typical correlation with the best single
  member?
- **Use case.** A gatekeeper: questions whose detectable effect is implausibly large are demoted before any run.
- **Indicators and roles.** All.
- **Assets.** SPY, sectors.
- **Combination type.** —
- **Metric and baselines.** Months available; the minimum detectable Sharpe difference (draft: about 0.3–0.45 on 8
  years at ρ = 0.8–0.9; about 0.2–0.25 on 25 years); minimum detectable max drawdown / CVaR difference by block
  bootstrap.
- **Data / PIT.** The coverage table is built. All 29 complete-case gives only 2017-02 → 2025-12 (107 months); core
  23 gives 2001-08 → 2026-03; real-time all 16 starts 2013-06.
- **MT / validation.** Descriptive.
- **Feasibility.** H.
- **Priority.** **P1.**

#### D2-10 — Alignment variants: how many, and do they change conclusions?
- **Question.** How many materially different timing conventions exist for a mixed-frequency combination, and does
  the sign of the D1-08 result change across them?
  - Conventions: month-end as-of; release-date event; daily as-of; fallback vs harsh release dates; real-time vs
    revised.
- **Use case.** A process / robustness question.
- **Indicators and roles.** As D1-08.
- **Assets.** SPY.
- **Combination type.** —
- **Metric and baselines.** The primary metric across 2 × 3 × 2 variants.
- **Data / PIT.** `release_calendar.csv` (both `available_date` and `available_date_harsh`).
- **MT / validation.** Robustness, not selection: report all.
- **Feasibility.** H.
- **Priority.** P3.

#### D2-11 — Is the useful combination the same across assets?
- **Question.** In IS folds, are the indicators' predictive slopes (sign and size) for next-quarter returns highly
  correlated across the 9 sector ETFs? A small effective rank of the slope matrix means one combination serves all
  assets; a large rank means asset-specific combinations, which multiplies the variation count.
- **Use case.** Deciding between a single overlay and per-asset designs.
- **Indicators and roles.** 7 representatives.
- **Assets.** 9 sectors + SPY.
- **Combination type.** —
- **Metric and baselines.** Effective rank of the (assets × indicators) slope matrix; bootstrap CI; null from N1.
- **Data / PIT.** From 1999.
- **MT / validation.** V-A IS only.
- **Feasibility.** H.
- **Priority.** P2.

#### D2-12 — Do frozen fleet winners capture most of the benefit?
- **Question.** Does the "cheap" family (members frozen at their published winner rules; only membership and
  operator vary) capture most of the out-of-fold benefit of a full re-search family in which member rules are
  re-selected inside folds? If so, the practical variation count is the cheap family's (about 10^3 per asset), not
  10^11.
- **Use case.** Deciding the Phase 2 architecture.
- **Indicators and roles.** Block representatives.
- **Assets.** SPY.
- **Combination type.** R1 / R3 (two operators only).
- **Metric and baselines.** The primary metric gap between the families; N3 applied to the cheap family.
- **Data / PIT.** The frozen family's members were chosen with the OOS window visible, so it can be evaluated
  honestly only on V-B and V-C.
- **MT / validation.** V-B, V-C, N3.
- **Feasibility.** M.
- **Priority.** P2.

---

## 3. Priority ranking

**P1 = do first** (foundation, or low-DoF and high-value); **P2 = next wave**; **P3 = only if earlier results justify
them.**

| Rank | ID | Short name | Why now |
|-----:|----|------------|---------|
| 1 | D2-03 | N_eff of strategy streams | Denominator for every multiple-testing correction |
| 2 | D2-09 | Common-sample and power budget | Gatekeeper: demotes questions that cannot be answered |
| 3 | D1-15 | Stability of lead order | Cheap; gates all sequencing questions |
| 4 | D1-08 | Block equal-weight composite vs best single | Zero-tuning test of the combination puzzle |
| 5 | D1-04 | Macro conditional on market stress | Central state-dependence claim; existing causal regime code |
| 6 | D1-02 | Curve + labour recession classifier | Strong prior, long real-time history, usable V-B |
| 7 | D1-19 | Direction (macro) × size (risk) | How overlays are actually run; separates vol effect from macro effect |
| 8 | D2-05 | Marginal value of the k-th indicator | Practical "how many is enough" |
| 9 | D2-08 | Search breadth vs PBO | Sets the search budget |
| 10 | D1-14 | Re-entry timing | The practitioner pain point; weak spot of all overlays |
| 11 | D1-09 | Fleet diffusion index (descriptive tool) | Cheap user-facing tool; strategy claim only with N3 |
| — | D2-01, D2-02 | Raw and effective counts | Draft answers already delivered here |

**P2:** D1-01, D1-05, D1-07, D1-10, D1-11, D1-12, D1-13, D1-16, D1-17, D1-23, D1-25, D2-04, D2-06, D2-07, D2-11,
D2-12.
**P3:** D1-03, D1-06, D1-18, D1-20, D1-21, D1-22, D1-24, D2-10.

**Count.** Direction 1: 25 (R1 3, R2 4, R3 4, R4 4, R5 3, R6 2, cross-asset/process 5). Direction 2: 12.
**Total: 37.** If every question runs, the "MT / validation" counts sum to about **85 pre-declared tests**. That
excludes the D2-07 and D2-08 grids, which run on inner folds and select nothing. These 85 tests are the family for
N4. The P1 subset alone is about 23 tests.

## 4. Open questions for the user

1. **The forward window (V-C).** Can we start a frozen paper-trade from 2026-11? It is the only truly unseen
   period, but it gives little power for 2–3 years.
2. **The backward holdout (V-B).** May we add an S&P 500 total-return series (pre-1993) and Fama–French industry portfolios (pre-1989)
   for 1980–1998? They are not ETFs, but they are the only way to test on a window the fleet never touched.
3. **Bonds as an asset.** Should U2 tilt between equities and Treasuries (needs a Treasury ETF / index series), or
   between equities and T-bills only?
4. **Frozen winners as members.** Several winners are labelled provisional (e.g. `gold_copper_xli`, pending Phase B
   rebuilds). Should the cheap family wait for Phase B to finish, or use the 3d735ec7 snapshot as frozen?
5. **Scope of the family.** Should all 37 questions (about 85 tests) form one corrected family? The alternative is
   to run the P1 subset (about 23 tests) first as its own family, with P2 as a separately corrected second family.
   That gives more power per test, but the second family must be registered before the first family's results
   are seen.
