# Question bank — indicator combinations (組合拳), revision 2

Branch `research261017_indicator_combos` (cut from `int261017_phaseB` @ 3d735ec7), 2026-10-17. Author: Research
Ray. **Draft for pre-registration: nothing below has been tested, and nothing is registered until the user
approves.** Registration happens when the hash of `registry/hypotheses.yaml` is recorded. No backtests, strategy
searches or asset-return reads were done in drafting.

Revision 2 answers two independent reviews: Claude QA (`QA_VERIFY.md`, pass with fixes) and Codex (`CODEX_REVIEW.md`,
major revision). § 5 maps every finding to its change.

## Executive summary

- **The bank has 40 questions:** 28 in Direction 1 (useful combinations) and 12 in Direction 2 (how many variations).
  - They are grouped into **13 hypothesis families** with **76 registered hypotheses**.
  - Each hypothesis is one fully specified configuration with one primary endpoint. The count includes every grid
    variant, extra asset, horizon and variant threshold.
- **Only 14 hypotheses in 8 questions are confirmatory.** Each of them meets all of these conditions:
  - its members are strictly point-in-time (ALFRED vintages, unrevised market prices, or snapshots taken from now
    on);
  - its rules are textbook rules, with no parameter chosen from our data;
  - it was not shaped by the viewed out-of-sample window, by full-sample correlations or by turning-point
    diagnostics.
- **Confirmatory verdicts come only from two data sources:**
  - a frozen forward period (V-C, from 2026-11);
  - a sequestered dataset that nobody on the project has examined (V-S, international real-time data).
- **All historical evidence is supporting or exploratory.** "Revised-as-of" data are not point-in-time and never
  count as confirmatory evidence. (Revised-as-of means today's revised values, each delayed to its original release
  date.)
- **Every question has a full compliance row**, in `COMPLIANCE.md` and `registry/compliance.csv`, both generated
  from `registry/hypotheses.yaml`. A row gives:
  - the use case and the single primary endpoint;
  - a numeric pass rule with its margin and the minimum event count;
  - all four baselines (B1, B2a, B3, B4), each either named or marked "n/a" with a reason;
  - the null design, the validation design, the family and the status.
- **A gate checks these rules on every commit** that touches this folder:
  `scripts/gate_combo_registry.py`, rules R1–R16.
- **Statistical power is low on any short window.** At 80% power the minimum detectable Sharpe gap over 8 years
  is about **0.5–0.9**, and over a 3-year forward window it is about **0.8–2.1** (COMBINATORICS.md § 4). Many
  confirmatory hypotheses will therefore stay "inconclusive" for years. This is stated in advance rather than
  hidden.

---

## 0. Protocol

### 0.1 Registration and status

- **P1. Registration.** The ledger `registry/hypotheses.yaml` is the registration. Registration happens when the
  user approves and its commit hash is recorded. Any later change creates a new version, and every version is
  reported.
- **P2. Status.** Each question has one status:
  - **Confirmatory:** decided only on V-C and/or V-S, under gate rule R7.
  - **Exploratory:** produces historical evidence only. It can reach V-C only through a *new* registration made
    after its historical results are known. This is the two-stage exploratory → confirmatory route.
  - **Descriptive:** an estimate with an interval. It selects nothing.
- **P3. No gating by diagnostics.** Diagnostics never decide which registered hypotheses are tested.
  - D1-15 (lead-order stability) is reported only.
  - D2-09 (power) can only label a hypothesis "underpowered" in advance. It cannot drop the hypothesis.
- **P4. One endpoint per hypothesis.** Each hypothesis has one primary endpoint. Secondary metrics are descriptive.
  Margins and thresholds are fixed in the ledger.

### 0.2 Point-in-time data rules

- **T1. Confirmatory evidence** may use only:
  - ALFRED vintages (`data/release_calendar/vintages/`, read through `scripts/_pit_align.py`);
  - unrevised market data;
  - the no-archive sources (ISM, NAHB, UMich expectations, USGS cement, EIA) *from their prospective snapshots
    onwards*. The first snapshot is 2026-10-16.
- **T2. Revised-as-of data are not point-in-time.** These are today's revised values delayed to their release
  date. They are sensitivity analysis only.
- **T3. Timing.** A position decided at close t earns the t → t+1 return (`position_shift = 1`).
- **T4. Regime variables.** These are IS-frozen fits with filtered probabilities only (`scripts/_regime_causal.py`).
- **T5. Historical start.** The four vintage series that start in 1980 (INDPRO, UNRATE, HOUST, M2SL) support strict
  point-in-time work from 1981-02, once the 12-month transforms have a full year of data.
  - The release calendar and the descriptive panel start in 1985.
  - The two dates are not in conflict. The 1980 date is when the vintage data begin; the 1985 date is when the
    calendar begins.

### 0.3 Baselines (B)

Every compliance row names all four baselines, or marks one "n/a" with a reason.

| Code | Baseline |
|------|----------|
| B1 | Buy-and-hold for U1 and U5. For U2, a static weight at the strategy's average exposure. For U3, equal-weight sectors. For U4, a constant base-rate classifier |
| B2a | The best single member, selected on the same training folds by the same procedure |
| B3 | A naive equal-weight composite of the same members: expanding z-scores, signs set by economic prior, threshold 0. For binary states, a majority vote |
| B4 | A trend or volatility baseline. Options: 10-month SMA (U1, U5, and a U4 flag); a 10% volatility target (U2, R6); 12-month relative momentum (U3) |

The fleet's published winner (former "B2b") is shown only as a descriptive comparison and never decides anything.

### 0.4 Validation designs (V)

| Code | Design | Role |
|------|--------|------|
| **V-C** | **Frozen forward period.** The spec is frozen by hash, positions are logged monthly from 2026-11, and the verdict is read at 12, 24 and 36 months, up to a 10-year horizon. If the minimum event count has not been reached, the verdict is "inconclusive". | **Confirmatory** |
| **V-S** | **Sequestered international dataset.** It is not yet acquired. It would hold G7-ex-US real-time vintages (OECD MEI Original Release Data and Revisions, the EABCN real-time database, the Bank of England real-time database), local total-return equity indices and local recession dates. No project artifact uses non-US data (repository grep, 2026-10-17). The data must be acquired and frozen under a blind protocol: the specs are fixed and hashed before anyone reads the returns. | **Confirmatory** |
| V-A | **Nested expanding walk-forward on pre-2017 history.** It starts at each question's data start. The outer test folds are the last 60% of the span, and the inner folds handle all selection. **The purge equals the outcome's maximum label horizon** (1 month for next-month returns, 3 for quarterly returns, 12 for 12-month recession or forward-return labels). There is no post-test embargo in an expanding design. Recessions inside V-A: 2001 (only when the training data start before about 1996) and 2008. **2020 is not in V-A.** | Supporting or exploratory |
| V-B | **Historical external validation, 1981–1997.** It was never used by the fleet, but our rules were designed knowing later history, so it is not a pristine holdout. All choices are frozen before its returns are read. Usable members: vintage INDPRO, UNRATE, HOUST, M2SL; market T10Y3M (GS10 − TB3MS before 1982); Moody's Baa − Aaa as a credit proxy (gap G16); VIX from 1990. Equity returns need an S&P 500 total-return series before 1993 (G5). **It is not used for relative returns**, because the pre-1999 sector indices are price-only. | Supporting |
| LORO | **Leave-one-recession-out** over the historical recessions in which every member is observable in real time for 24 months before the peak. 2020 is excluded (it is in V-D). The design reports episode-level hits and false alarms with exact (Clopper–Pearson) intervals. Without G13 (Philadelphia Fed real-time data set) only 1990, 2001 and 2008 qualify for curve + labour rules. | Supporting, U4 |
| V-D | The fleet's out-of-sample window (about 2017–2026), viewed many times. **Descriptive only**, never primary (gate rule R8). | Descriptive |

### 0.5 Nulls (N) and multiplicity

| Code | Null | Rules out |
|------|------|-----------|
| N1 | A circular block shift of the whole indicator panel against returns (K ≥ 500). It keeps the correlation among indicators. | Chance alignment with a few episodes |
| N2 | Random members from the same or other blocks, or random regimes and orders of equal frequency | "Any combination would do" |
| N3 | Re-selection null: fleet-winner members are re-selected inside each N1 draw | The multiple-signal selection bias (Novy-Marx 2015/16) |

Multiplicity is controlled **per family and per evaluation dataset** (`registry/families.yaml`):

- **Return endpoints:** a Romano–Wolf stepdown with a stationary bootstrap.
- **Event endpoints:** Holm correction on episode-level exact p-values.
- **"Best of family vs B2a":** Hansen SPA.
- **The deflated Sharpe ratio** is used only where a family actually searches (D1-10, D1-29). Its N is the number of
  configurations fitted there.

There is **no single N_eff "denominator" for every correction.** D2-03 estimates dependence among fleet streams,
and its only use is the deflated Sharpe ratio of fleet-member families.

Across the 8 confirmatory families, each family is a separate claim. As a sensitivity check, a Bonferroni split of
α across the families (0.05 / 8) is also reported.

### 0.6 Use cases and endpoint templates

| Code | Use case | Primary endpoint template (exact wording in the ledger) |
|------|----------|---------------------------------------------------------|
| U1 | Risk-off overlay | Monthly CVaR(5%) must fall by ≥ 15% against **both** B2a and B3, with family-adjusted p ≤ 0.05. Guardrail: return shortfall vs B1 ≤ 2.0 pp per year. Requires ≥ 3 drawdowns of ≥ 15%. |
| U2 | Allocation tilt | CVaR reduction at matched average exposure. Margin 10–15%. |
| U3 | Relative return | IR ≥ 0.30, total-return series only. |
| U4 | Recession classification | Binary rules use a lexicographic endpoint (recall non-inferior, false alarms non-inferior, ≥ 2 months earlier). Probabilistic rules use the Brier skill score (≥ 0.10) with a calibration guardrail. Both use LORO. |
| U5 | Entry timing | Missed-rally cost must fall by ≥ 25% against B4 and in ≥ 2/3 of episodes. Requires ≥ 4 episodes. |
| Interaction | State dependence | d in r(t+1) = a + b·s + c·g + d·s·g. Requires the registered sign, \|d\| ≥ 0.50 pp per month, HAC and stationary-bootstrap p ≤ 0.05, and ≥ 5 regime episodes. A fold with no episode contributes to a and b only. |

### 0.7 Assets: what breadth exists

- **SPY:** from 1993. Before 1993, an S&P 500 total-return series is needed (G5).
- **Nine sector SPDRs:** from 1998-12.
  - The `etf_prices` sheet in `data/Data Master.xlsx` is **price-only**. The SPY close on 1993-01-29 is the raw
    43.94, not a dividend-adjusted value.
  - Total-return series are therefore needed even after 1999 (G17).
  - The S&P sector price indices from 1989 are usable for breadth and trend counts, but not for relative returns.
- **Beyond US equities:**
  - gold (spot, 2000+);
  - HYG (2007+);
  - a Treasury proxy built from DGS10 (G6).
  - International assets are not used now; they are reserved for V-S.
- **This breadth is limited.** Most questions are about SPY. Sector questions share SPY's beta.

---

## 1. Direction 1 — combinations for real use cases

Each question gives the precise question and its economic logic. Its compliance row (endpoint, pass rule, events,
baselines, null, validation, hypotheses) is in `COMPLIANCE.md`.

### Family F-REC — recession classification

#### D1-02 — Does a prior curve inversion let a lower, earlier labour trigger work? *(confirmatory)*
- **Question.** If a recession call requires the yield curve (T10Y3M) to have been inverted at some month-end in the
  last 12 months, can the Sahm gap trigger at 0.30 pp instead of the standard 0.50 pp?
  - The Sahm gap is the 3-month average of UNRATE (vintage) minus the minimum of the previous 12 months' 3-month
    averages.
  - Success means signalling at least 2 months earlier than the standard Sahm rule (0.50 pp), with no lost recall
    and no extra false alarms.
  - The 0.50 pp version of the combination is registered too.
- **Why.** The curve gives early warning with a long and variable lead (Estrella & Mishkin 1998). The Sahm rule is
  reliable but fires about 3 months into a recession (Sahm 2019). The curve's earlier warning may make a lower
  labour threshold safe.
- **Notes.** The 0.30 pp trigger is a labelled variant; the published rule is 0.50 pp. Historical LORO is
  supporting only, with 3 usable recessions until gap G13 is filled. V-S provides most of the events.

#### D1-13 — Do falling permits followed by rising unemployment beat the Sahm rule alone? *(confirmatory)*
- **Question.** The rule: permits YoY < 0 (vintage), followed within 12 months by a Sahm gap ≥ 0.30 pp. Does it
  meet the same lexicographic standard against the standard Sahm rule?
- **Why.** Housing leads the cycle (Leamer 2007). The chain order comes from theory, and it is registered whatever
  D1-15 finds.
- **Notes.** PERMIT vintages start in 1999, so only 2001 and 2008 are available historically.

#### D1-27 — Real-time recession-probability horse race *(confirmatory; added from Codex Q1)*
- **Question.** Expanding-window probits, with predictors as known in real time, forecast a recession within 12
  months. Do three augmented models beat the term-spread-only probit? Success requires a Brier skill score ≥ 0.10,
  better log scores in ≥ 70% of held-out recessions, and calibration slope in [0.7, 1.3].
  - Model 1: term + credit (HY–IG; Baa − Aaa before 1997).
  - Model 2: term + Sahm gap.
  - Model 3: term + credit + Sahm gap + permits.
- **Why.** Credit spreads add information beyond the curve (Gilchrist & Zakrajšek 2012). A continuous score with
  calibration is more informative than the AUROC of a binary rule.

#### D1-23 — Recession probability as an equity overlay *(exploratory)*
- **Question.** Does the overlay w = 1 − P(recession), using D1-27 model 3, reduce CVaR against the binary D1-02
  overlay, B2a and B3?
- **Notes.** It is a secondary translation of D1-27. It can be promoted to confirmatory only by a new registration
  after D1-27 is decided.

### Family F-STATE — state dependence

#### D1-04 — Do new orders matter more when credit is stressed? *(confirmatory)*
- **Question.** In a predictive regression for next-month SPY excess returns, is the interaction d positive, and at
  least 0.50 pp per month?
  - Signal: NEWORDER YoY sign (vintage; +1 bull, −1 bear).
  - Stress regime: HY–IG OAS above its expanding-window 80th percentile.
- **Changed from revision 1.** The textbook sign rule replaces the fleet ISM and new-orders winner rules, which were
  selected with the viewed OOS window. The ISM version is kept as an exploratory hypothesis, because ISM is
  historically revised-only.
- **Why.** Macro news moves equities more in bad times; credit amplifies real shocks.
- **Notes.** At least 5 stress episodes are required; V-C will need many years to reach that.

#### D1-17 — Market stress without macro weakness: false alarm or early warning? *(exploratory)*
- **Question.** In market-stress months, is the next-3-month SPY return at least 1.5 pp lower when macro data are
  also weak (ISM < 50 or UNRATE rising)? This is tested as an interaction.
- **Status.** Exploratory: it uses revised ISM, and the VIX3M series starts in 2007, inside the viewed window.

#### D1-06 — Monetary regime and the M2 signal *(exploratory)*
- **Question.** Does the M2 YoY-acceleration signal interact with a tightening regime (fed funds up over 12 months)?
- **Status.** Exploratory: the question was prompted by the fleet M2 winner's viewed OOS result.

#### D1-30 — Filtered Markov switching with term- and credit-driven transitions *(exploratory; added from Codex Q5)*
- **Question.** The model is a 2-regime Markov-switching model of SPY excess returns. Its transition probabilities
  depend on T10Y3M and HY–IG; its parameters are frozen in-sample, and it uses filtered probabilities. Does it
  improve the out-of-fold predictive log density by ≥ 0.02 nats per month against two models: a fixed-transition MS
  model, and the D1-04-style linear interaction?

### Family F-TC — term × credit

#### D1-05 — Do term and credit spreads carry complementary information? *(confirmatory; absorbs Codex Q2)*
- **Question.** For next-month SPY excess returns, are either of these present beyond the additive model?
  - a negative linear term × credit interaction;
  - a joint-distress state, 1{T10Y3M < 0.5 pp} × 1{HY–IG 6-month change > 0).
- **Treasury returns.** The same two tests on a Treasury return proxy are registered as exploratory (G6).
- **Why.** A flat curve says growth is weakening; widening credit says the weakness is turning into financial
  distress. The combination may be worse than the sum.
- **Notes.** Market data only, so the question is strictly point-in-time. V-B uses Baa − Aaa as the credit proxy
  before 1997.

### Family F-FCI — financial conditions

#### D1-28 — Point-in-time FCI vs a published FCI *(confirmatory; added from Codex Q3)*
- **Question.** Does an equal-weight point-in-time financial-conditions index reduce overlay CVaR against an
  overlay on the Chicago Fed NFCI *as published at the time* (ALFRED vintages, G15)?
  - Index members: T10Y3M, HY–IG (Baa − Aaa before 1997), VIX, and the share of S&P 500 sectors above their
    10-month SMA.
  - A second hypothesis: does a real-time PCA-weighted version beat the equal-weight one?
- **Why.** Published FCIs are revised and partly model-based. A simple point-in-time index is what a user could
  actually have run.

### Family F-RISKOFF — confirmation and chains

#### D1-01 — Housing contraction confirmed by credit widening *(confirmatory)*
- **Question.** Does going to cash only when both of these hold cut SPY CVaR by ≥ 15% against both the best single
  member and the equal-weight composite?
  - permits YoY < 0 (vintage);
  - HY–IG 6-month change > 0. A variant uses SLOOS net tightening > 0 (vintage) instead.
- **Changed from revision 1.** Sign rules replace the ad hoc z > 1 threshold, so no constant is chosen from data.

#### D1-12 — Credit, then manufacturing *(exploratory)*
- **Question.** Bank or market credit tightening, followed within w ∈ {3, 6, 9} months by ISM manufacturing < 50.
  Does the sequence improve overlay CVaR against each link alone and against their simultaneous AND?
- **Notes.** The SLOOS > 20 threshold is an a priori choice with no published source; it is flagged as ad hoc. ISM
  is historically revised-only, so the question is exploratory. The chain is registered regardless of D1-15.

### Family F-REENTRY

#### D1-14 — Re-entry by a 2-of-3 early-cycle vote *(confirmatory)*
- **Question.** The exit rule is fixed: leave when SPY falls below its 10-month SMA. Re-entry happens when at least
  2 of 3 signals agree:
  - T10Y3M 3-month change > +0.50 pp;
  - new orders YoY rising for 2 releases (vintage);
  - HY–IG 63-day change < 0.
  Does this reduce the mean missed-rally cost by ≥ 25% against SMA re-entry, and in ≥ 2/3 of episodes?
- **Validation.**
  - V-C and V-S are primary.
  - Supporting: V-A (2002–03, 2009) and V-B (1982, 1991; needs G5).
  - 2020 and 2022–23 are in V-D and are descriptive only.
  - At least 4 episodes are required.

### Family F-COMP — composites (all exploratory: the blocks were informed by full-sample correlations)

The block-membership table is frozen in COMBINATORICS.md § 3.4: 8 blocks, B1–B8. The point-in-time representatives
are:

| Block | Representative | Data |
|-------|----------------|------|
| B1 | INDPRO YoY | vintage |
| B2 | PERMIT YoY | vintage |
| B3 | HY–IG | market |
| B4 | BUSLOANS YoY | vintage |
| B5 | UMCSENT | vintage |
| B6 | gold/copper YoY | market |
| B7 | M2 YoY | vintage |
| B8 | VIX | market |

#### D1-08 — Equal-weight block composite vs the best single representative
- **Question.** Does the equal-weight composite of the 8 representatives reduce CVaR by ≥ 15% against the best
  single representative chosen on the training folds?
- **Assets.** SPY and each of 9 sectors (total return), so 10 hypotheses in all.
- **Why.** This is the forecast-combination puzzle (Timmermann 2006; Rapach, Strauss & Zhou 2010).

#### D1-10 — Do estimated weights beat equal weights?
- **Question.** Do ridge-logit, real-time PC1 or inverse-variance weights beat fixed equal weights on CVaR at matched
  exposure?
- **Notes.** Deflated Sharpe uses N = the number of configurations fitted; PBO is estimated by CSCV.

#### D1-19 — The composite sets the direction, market risk sets the size
- **Question.** Does sizing by VIX or by 21-day realised volatility beat direction-only by ≥ 15% and a pure 10%
  volatility target by ≥ 10% on CVaR?
- **Why.** This separates a macro effect from a volatility effect (Moreira & Muir 2017; Cederburg et al. 2020).

#### D1-20 — Conviction sizing by vote count
- **Question.** Does sizing by the share of agreeing representatives beat a binary majority vote?

#### D1-24 — Daily as-of updating of the monthly composite
- **Question.** After 10 bp per trade, does updating the composite on each member's release date beat month-end
  rebalancing?

#### D1-29 — Ragged-edge mixed-frequency dynamic factor vs PCA vs equal weights *(added from Codex Q4)*
- **Question.** A Kalman-filtered single factor uses the representatives plus quarterly SLOOS and card delinquency,
  and handles the latest releases that are still missing. Does its overlay beat both the equal-weight and the
  real-time PCA composites?

### Family F-SECT — sectors (exploratory; needs total-return series, G17)

#### D1-07 — Late-cycle regime: defensive vs cyclical
- **Question.** In the regime T10Y3M < 0.5 pp and ISM 3-month change < 0, does the defensive-minus-cyclical basket
  earn an IR ≥ 0.30 over the following 3 months?
  - Defensive basket: XLV, XLP, XLU. Cyclical basket: XLI, XLY, XLB, XLF.
  - XLU and XLI are also tested as single sectors.
- **Notes.** The former D1-22 ("which role helps the basket most") is retired as a question. It becomes the
  family-level summary of F-SECT and adds no tests.
- **Prior.** Expect a null result (Stangl, Jacobsen & Visaltanachoti 2009).

#### D1-18 — Equity internals vs manufacturing for tech
- **Question.** Is the 3-month relative return of XLK (and of QQQ) against SPY different when SOX/SPY momentum
  disagrees with ISM?

#### D1-21 — A second indicator for the existing defensive pairs
- **Question.** Does a credit or curve filter raise the relative IR of XLV, XLP and XLU by ≥ 0.20?
- **Notes.** The members are fleet winners, so the N3 null is mandatory.

### Family F-HOUS — housing

#### D1-03 — k-of-3 within housing
- **Question.** Starts, permits and new home sales each give a YoY < 0 flag (vintages). Does requiring 2 or 3 of the
  flags cut false exits by ≥ 30% without worsening CVaR by more than 5%?

#### D1-11 — Housing composite vs single housing indicators
- **Question.** Does a housing composite beat the best single housing indicator?
  - Two composites: 3 members (vintages), and 5 members adding NAHB and cement (revised).
  - Assets: SPY (U1) and XHB, XLB, XLY relative returns (U3).

### Family F-DIV

#### D1-16 — Soft vs hard data divergence
- **Question.** When UMCSENT and hard data (RSXFS YoY, INDPRO YoY; all vintages) diverge by |z| > 1 for at least 2
  months, is the following 6-month return (SPY; XLY − XLP) different by ≥ 2 pp?

### Family F-FLEET (fleet-winner members; N3 is mandatory)

#### D1-09 — Diffusion index of the frozen fleet rules
- **Question.** Does the cluster-weighted share of fleet rules in a risk-off state forecast recessions (Brier skill
  score) better than the best single rule, after N3?

### Family F-REV (robustness, reported for every finalist)

#### D1-25 — Real-time vs revised gap for every finalist
- **Question.** For every finalist, what is the gap in its primary endpoint between the revised-as-of and vintage
  versions?
- **Rule.** A gap larger than 50% of the finalist's own effect flags it as revision-dependent.
- **Why.** Revision gaps are large for INDPRO, NEWORDER and new home sales: real-time vs revised correlations are
  0.90–0.94.

### Family F-SPACE (diagnostic)

#### D1-15 — Stability of the lead order across cycles
- **Question.** How concordant are indicator lead ranks across 1990, 2001 and 2008 (Kendall's W, Bry–Boschan
  dating)?
- **Reported only. It gates nothing** (P3).

---

## 2. Direction 2 — how many variations, and how many are real?

#### D2-01 — Raw size of the space *(descriptive, answered)*
- **Answer.** Exact counts by operator are in COMBINATORICS.md § 2.

#### D2-02 — Effective dimensionality under point-in-time data *(descriptive, answered in draft)*
- **Estimand.** Participation ratio on the strict-PIT-14 panel.
- **Answer.** 5.5, with a 90% block-bootstrap interval of 3.8–6.4.

#### D2-03 — Dependence among fleet winners' return streams *(descriptive)*
- **Use.** Feeds only the deflated Sharpe ratio of fleet-member families. It is not a global denominator.

#### D2-04 — Is dimensionality lower around recessions? *(exploratory)*
- **Question.** Measured with rolling equal-length windows and a bootstrap interval. Revision 1's pre/post-2008
  claim is withdrawn, because it was confounded by sample size.
- **Expectation.** With 2 recessions in the strict-PIT window, the answer is likely inconclusive.

#### D2-05 — Marginal value of the k-th representative *(exploratory, F-COMP)*
- **Question.** In a frozen economic order, at what k does adding another representative stop helping? The
  hypothesis is that the plateau k* is ≤ 4.

#### D2-06 — Does a second member of a block add anything? *(exploratory, F-HOUS)*
- **Scope.** Four blocks: housing, activity, market credit and sentiment.

#### D2-07 — Members or operator: which matters more? *(descriptive, inner folds only)*

#### D2-08 — How wide can a search be before it is mostly overfit? *(descriptive)*
- **Rule.** The Phase 3 budget is the largest search breadth with PBO ≤ 0.25.

#### D2-09 — Common-sample and power budget *(descriptive)*
- **Content.** The MDE per hypothesis, with Memmel's term, 80% power, serial correlation and the family's
  multiplicity.
- **Rule.** A hypothesis whose MDE is more than 2× its margin is labelled "underpowered" before any run. It is never
  dropped.

#### D2-10 — Alignment variants *(descriptive, F-REV)*
- **Rule.** A finalist whose endpoint changes sign in 2 or more of 6 alignment variants is flagged
  "alignment-fragile".

#### D2-11 — Is the useful combination the same across assets? *(descriptive)*
- **Assets.** SPY, sectors (total return), gold, HYG and the Treasury proxy.
- **Rule.** If the slope-matrix participation ratio is ≤ 2, Phase 3 uses one overlay design for all assets.

#### D2-12 — Do frozen fleet winners capture most of the benefit? *(exploratory, F-FLEET)*
- **Question.** Does the frozen family capture at least 80% of the improvement from a full re-search? Tested on V-B
  with N3.

---

## 3. Priority ranking (exactly 10)

**Rationale.** First, the power budget, because it governs everything else. Then the confirmatory questions, ranked
by evidential value per unit of cost. Last, one exploratory composite and the search-budget study.

| Rank | ID | Status | Short name | Why |
|-----:|----|--------|------------|-----|
| 1 | D2-09 | descriptive | Power and common-sample budget | Labels underpowered hypotheses before any run |
| 2 | D1-27 | confirmatory | Recession-probability horse race | Continuous, calibrated endpoint; strong literature prior; V-S can supply many recessions |
| 3 | D1-02 | confirmatory | Curve inversion enables an earlier labour trigger | Few degrees of freedom; standard Sahm rule as comparator |
| 4 | D1-05 | confirmatory | Term × credit interaction | Market data only, so strictly point-in-time; long history through proxies |
| 5 | D1-04 | confirmatory | New orders × credit stress | Tests the central state-dependence claim with textbook rules |
| 6 | D1-28 | confirmatory | PIT FCI vs published NFCI | A user-facing tool with a published benchmark |
| 7 | D1-14 | confirmatory | Re-entry vote | Weakest link of most overlays |
| 8 | D1-01 | confirmatory | Permits confirmed by credit | Cleanest confirmation design |
| 9 | D1-08 | exploratory | Block composite vs best single | Generates the composite to register for V-C later |
| 10 | D2-08 | descriptive | Search breadth vs PBO | Sets the Phase 3 search budget |

**Next wave.** D1-13 (confirmatory, but only 2 historical recessions); D1-19, D1-29, D2-03, D2-05, D1-11, D1-12.

## 4. Counts (reconciled)

| Object | Count | Source |
|--------|------:|--------|
| Registry entries | 39 | `lead_axis_registry.json`: 35 live + 3 archived (`*_archived`) + 1 superseded (`hy_ig_spy_v1`) |
| Live pairs with a published tournament grid | 35 | `results/<pair>/tournament_results_*.csv` (164,176 rules; median 1,180; mean 4,691) |
| Live pairs whose `winner_summary.json` carries `total_combos` | 29 | Revision 1's "144,098 configurations" figure covers only these |
| Distinct indicators behind the live pairs | 26 | 27 release-calendar series ids; new home sales SA and NSA counted once |
| Indicators in the descriptive panel | 29 | The 26 fleet indicators plus AMTMNO, UMich expectations and HY OAS |
| Strict point-in-time panel (primary for dimensionality) | 14 | 10 vintage + 4 market series |
| Questions / families / hypotheses / confirmatory | 40 / 13 / 76 / 14 | `registry/` |

## 5. Changes in revision 2, by finding

| Lead item | Change |
|-----------|--------|
| 1 | Machine-readable ledger `registry/hypotheses.yaml` with a family file; generated `COMPLIANCE.md` and `registry/compliance.csv`; gate `scripts/gate_combo_registry.py` (R1–R16), registered in the branch pre-commit hook for this folder. |
| 2 | Status per question. Revised-as-of data are exploratory or sensitivity only (T2). The no-archive sources are point-in-time only from their snapshots on. D1-06, D1-08 (and all of F-COMP), D1-17, D1-21 and F-FLEET are exploratory. D1-15 gates nothing (P3). |
| 3 | V-B renamed "historical external validation" and frozen before its returns are read. Confirmatory status reserved for V-C and V-S. LORO with exact intervals for U4. V-A recessions are 2001 and 2008 (2020 removed). Purge = label horizon (gate R5). D1-14 now has V-C, V-S, V-A and V-B. |
| 4 | The "N_eff denominator" claim is dropped. Corrections are per family and endpoint (§ 0.5). The count is honest: 76 hypotheses, including assets, variants and horizons. Overlaps are consolidated into families F-COMP, F-SECT and F-STATE; D1-22 is merged into F-SECT. |
| 5 | Primary estimand: participation ratio on the strict-PIT panel, with a block bootstrap. Nulls preserve serial dependence (stationary bootstrap, phase randomisation; 2000 draws). M_eff = Σ min(λ, 1). Clusters are sensitivity only. Blocks are frozen at 8. The pre/post-2008 claim is removed. |
| 6 | Exact Σ_S Π m_i by operator, with deduplication; median- and mean-grid approximations shown for comparison (COMBINATORICS.md § 2). |
| 7 | MDE table with Memmel's term, 80% power, serial correlation (VIF) and multiplicity (COMBINATORICS.md § 4). |
| 8 | No V-B for relative returns. `etf_prices` found to be price-only, so total-return series are needed (G17). Asset breadth stated plainly (§ 0.7). Standard Sahm rule = 0.50 pp (gate R12). |
| 9 | Interaction endpoints with HAC and bootstrap inference, ≥ 5 episodes and a fold rule, for D1-04, D1-05, D1-06 and D1-17 (gate R11). |
| 10 | D1-02 and D1-13 use lexicographic endpoints with margins. D1-27 uses BSS with calibration. |
| 11 | Added D1-27 (horse race), D1-28 (FCI), D1-29 (DFM) and D1-30 (MS-TVTP). Codex Q2 (term × credit) is absorbed into D1-05. |
| 12 | Counts reconciled (§ 4). The 1980 and 1985 dates are explained (T5). The ranking has exactly 10. The `spy_fwd` columns are no longer loaded. README_zh rewritten. |

## 6. Open questions for the user

1. **V-S.** May we acquire a sequestered international real-time dataset under the blind protocol (§ 0.4)? Without
   it, most confirmatory recession questions cannot be decided for many years.
2. **V-C.** Should the frozen forward log start in 2026-11? We expect it to be inconclusive for at least 2–3 years.
3. **Data for supporting evidence.** May we add the following?
   - an S&P 500 total-return series before 1993 (G5);
   - total-return sector series (G17);
   - the Philadelphia Fed real-time data set (G13);
   - NFCI vintages (G15);
   - Moody's Baa/Aaa (G16).
4. **Families.** Is per-family control (with a Bonferroni sensitivity split across families) acceptable, or does
   the user want one correction across all 14 confirmatory hypotheses?
5. **Fleet winners.** Fleet-winner members are exploratory only. Should they wait for Phase B, or use the 3d735ec7
   snapshot?
