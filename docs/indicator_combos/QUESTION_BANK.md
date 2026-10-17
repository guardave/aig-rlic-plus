# Question bank — indicator combinations (組合拳), revision 3

Branch `research261017_indicator_combos` (cut from `int261017_phaseB` @ 3d735ec7), 2026-10-17. Author: Research
Ray.

- **Status: draft for pre-registration.** Nothing below has been tested, and nothing is registered until the user
  approves and the hash of `registry/hypotheses.yaml` is recorded.
- No backtests, strategy searches or asset-return reads were done in drafting.
- Revision 3 answers the second reviews: Claude QA (`QA_VERIFY_2.md`, pass with fixes) and Codex
  (`CODEX_REVIEW_2.md`, major revision). § 5 maps each item to its change.

## Executive summary

- **Size of the bank.** 40 questions: 28 in Direction 1 (useful combinations) and 12 in Direction 2 (how many
  variations).
  - They hold **76 hypotheses in 13 families**.
  - Each hypothesis is its own object in the ledger. It records its own status, asset, endpoint, pass rule (margin,
    named test, α or interval level), minimum event count, horizon, purge, family, and rule parameters with their
    sources.
- **Confirmatory hypotheses.** Only **9 hypotheses in 5 questions (4 families)** are confirmatory:
  - D1-01.H1, D1-01.H2
  - D1-02.H1
  - D1-05.H1
  - D1-27.H1–H3
  - D1-28.H1, D1-28.H2

  They are labelled **discovery-informed prospective confirmations**.
  - **Not snooping-free.** The designer had seen post-1997 history and the fleet's single-indicator results, so the
    designs are not free of data snooping.
  - **What protects them.** Every rule parameter is either cited from the literature or "natural" (a zero or sign
    threshold, a year-over-year change, a level, equal weights, an expanding window). Each verdict is read only on
    data nobody had seen at freeze time: the frozen forward period (V-C) or a sequestered international dataset
    (V-S).
- **Demoted in revision 3.** Every hypothesis with a parameter of our own choosing is now exploratory:
  - the 0.30 pp Sahm variant (D1-02.H2, D1-13);
  - D1-04's 80th-percentile stress cut;
  - D1-14's three vote thresholds;
  - D1-05's joint-distress dummy and its Treasury hypotheses.
- **Compliance tables and the gate.** `COMPLIANCE.md` and `registry/compliance.csv` give one row per hypothesis. A
  gate checks the ledger (`scripts/gate_combo_registry.py`):
  - it validates against `registry/schema.json` (JSON Schema);
  - it applies 17 semantic rules;
  - it is covered by 29 mutation tests, which include every QA and Codex mutation.
  - **Limits.** The gate reads the staged files in the branch's pre-commit hook. It is active only when
    `core.hooksPath` is set to `scripts/hooks`, and `git commit --no-verify` bypasses it. It checks that the declared
    labels are consistent with each other and with the data files, not that the labels are true.
- **Power.** At 80% power on monthly data, the minimum detectable Sharpe gap over 8 years is about **0.45–0.65**
  for strategies whose returns correlate 0.8–0.9 with the comparator. Over 3 years it is **0.73–1.06**.
  - The tail-risk (CVaR), Brier-score and interaction endpoints are weaker still (COMBINATORICS.md § 4).
  - Most confirmatory hypotheses will be "inconclusive" for years.

---

## 0. Protocol

### 0.1 Registration, status and provenance

- **P1. Registration.** The ledger `registry/hypotheses.yaml` is the registration. Every later change creates a new
  version, and every version is reported.
- **P2. Status.** Every hypothesis carries a status field:
  - **Confirmatory (discovery-informed prospective confirmation).** All four conditions must hold (gate rule R7):
    - every rule parameter is `citation` or `natural`;
    - every member is on a vintage, market or forward-snapshot track;
    - the question has no fleet-winner members and no recorded influence;
    - the primary validation is V-C and/or V-S only.
  - **Exploratory.** Historical evidence only. A hypothesis reaches V-C only through a new registration after its
    historical results are known.
  - A question without hypotheses is **descriptive**: an estimand with an interval and a decision rule.
- **P3. Provenance.** Every question records what the designer knew (`provenance.designer_knowledge`) and the
  freeze date. Every parameter records its `source_type` (`citation`, `natural`, `convention` or `data_chosen`)
  and its source. Margins in pass rules are decision thresholds, not rule parameters; they are fixed in the ledger.
- **P4. No gating by diagnostics.**
  - D1-15 (lead-order stability) gates nothing.
  - D2-09 (power) only labels a hypothesis "underpowered" in advance. It never drops one.
- **P5. One endpoint per hypothesis.** Secondary metrics are descriptive.

### 0.2 Point-in-time data rules

- **T1. Confirmatory evidence** may use only:
  - ALFRED vintages (`data/release_calendar/vintages/`, read through `scripts/_pit_align.py`). A pending vintage
    pull must be declared with `pending_gap` and closed before any evaluation; for example the NFCI vintages, G15.
  - unrevised market data;
  - no-archive sources from their prospective snapshots onwards (from 2026-10-16).
  - Gate rule R17 checks each declared track against the actual vintage files, the release calendar, the snapshot
    manifest and a market whitelist.
- **T2. Revised-as-of data are not point-in-time.** These are today's revised values delayed to their release date.
  They are sensitivity analysis only.
- **T3. Timing.** A position decided at close t earns the t → t+1 return.
- **T4. Regimes.** Regime fits are frozen in-sample and use filtered probabilities only.
- **T5. Historical start.** Vintage series that start in 1980 (INDPRO, UNRATE, HOUST, M2SL) allow strict
  point-in-time work from 1981-02. The release calendar and the descriptive panel start in 1985.

### 0.3 Baselines (B)

| Code | Baseline |
|------|----------|
| B1 | Buy-and-hold for U1 and U5. For U2, a static weight at the strategy's average exposure. For U3, equal-weight sectors. For U4, a constant base-rate classifier |
| B2a | The best single member, selected on the same training folds by the same procedure |
| B3 | A naive equal-weight composite of the same members (expanding z-scores, prior signs, threshold 0), or a majority vote for binary states |
| B4 | A trend or volatility baseline: 10-month SMA (Faber 2007); a 10% volatility target (U2); 12-month relative momentum (U3) |

**Rows with "n/a".** Thirteen question rows mark at least one baseline "n/a", each with a reason:
- the 10 descriptive questions (all four baselines);
- D2-04, an estimate-type hypothesis (all four baselines);
- the B3 column of D1-08 and D1-11, where the tested composite *is* B3.

### 0.4 Validation designs (V)

| Code | Design | Role |
|------|--------|------|
| **V-C** | **Frozen forward period.** The spec is frozen by hash, positions are logged monthly from 2026-11, and the verdict is read at 12, 24 and 36 months, up to 10 years. Below the minimum event count the verdict is "inconclusive". | Confirmatory |
| **V-S** | **Sequestered international dataset.** Not yet acquired (G14): G7-ex-US real-time vintages, local total-return equity indices and recession dates. No project artifact uses non-US data (repository grep, 2026-10-17). It must be acquired under a blind protocol: specs are hashed before any return is read. | Confirmatory |
| V-A | **Nested expanding walk-forward on pre-2017 history.** The purge equals each endpoint's label horizon (gate rule R5 derives it from the endpoint's own definition). There is no post-test embargo. Recessions inside V-A: 2001 (only when training starts before about 1996) and 2008. | Supporting / exploratory |
| V-B | **Historical external validation, 1981–1997.** Frozen before its returns are read. Never used for relative returns (R13). | Supporting |
| LORO | **Leave-one-recession-out.** Each held-out fold purges 12 months before the peak. It reports episode-level hits and false alarms with exact intervals. Only 1990, 2001 and 2008 qualify for curve + labour rules until G13 is filled. | Supporting, U4 |
| V-D | The fleet's viewed out-of-sample window, about 2017–2026. **Descriptive only** (R8). | Descriptive |

### 0.5 Nulls (N) and multiplicity

| Code | Null |
|------|------|
| N1 | Circular block shift of the whole indicator panel against returns (K ≥ 500) |
| N2 | Random members, regimes or orders of equal frequency |
| N3 | Re-selection null for fleet-winner members (Novy-Marx 2015/16) |

**Corrections are per family and per evaluation dataset.** The method is one of an enumerated set (gate rule R15):

| Family | Confirmatory hypotheses | Correction |
|--------|------------------------:|------------|
| F-REC | 4 | Holm |
| F-TC | 1 | Single test |
| F-FCI | 2 | Romano–Wolf |
| F-RISKOFF | 2 | Romano–Wolf |

- The exploratory side of each family has its own correction, listed in `families.yaml`.
- The deflated Sharpe ratio is used only where a family searches (D1-10, D1-29).
- **4 families hold confirmatory hypotheses.** Each is a separate claim. As a sensitivity check, a Bonferroni split
  across them (**α = 0.05 / 4 = 0.0125**) is also reported.

### 0.6 Use cases and endpoint templates

| Code | Use case | Primary endpoint (exact wording in the ledger) |
|------|----------|-------------------------------------------------|
| U1 | Risk-off overlay | Monthly CVaR(5%) falls by ≥ 15% against both B2a and B3. Stationary-bootstrap p ≤ 0.05 after family correction. Guardrail: return shortfall vs B1 ≤ 2 pp per year. Requires ≥ 3 drawdowns of ≥ 15% |
| U2 | Allocation tilt | CVaR reduction at matched average exposure, margin 10–15% |
| U3 | Relative return | Information ratio ≥ 0.30 (or an IR gain ≥ 0.20), total-return series only |
| U4 | Recession classification | **Binary rules (D1-02.H1):** false-alarm episodes cut by ≥ 50% against curve alone, tested by an exact McNemar test on discordant episodes (Holm within F-REC). Recall must be non-inferior, with a Clopper–Pearson 95% lower bound ≥ 0.5. The median signal must come no later than the NBER peak + 6 months. **Probabilistic rules (D1-27):** Brier skill score ≥ 0.10, tested by a block-bootstrap Diebold–Mariano test, with a calibration guardrail |
| U5 | Entry timing | Missed-rally cost falls by ≥ 25% against B4, tested by an exact sign test over episodes |
| — | State dependence | The interaction d in r(t+1) = a + b·s + c·g + d·s·g. Requires HAC and stationary-bootstrap p ≤ 0.05, a margin and ≥ 5 regime episodes |

### 0.7 Assets: breadth is limited

- **Most questions target SPY.** The sector questions share SPY's beta.
- **The ETF price sheet is price-only**, so total-return series are required (G17).
- **Beyond US equities:**
  - Only the D1-05 Treasury-proxy hypotheses (exploratory) and the D2-11 estimand (gold, Treasury proxy) go beyond
    US equities.
  - HYG is price-only, and its distributions are large, so it is excluded.
  - International assets are reserved for V-S.
- **This is a real limitation.** The bank cannot yet say whether any combination works outside US equities.

---

## 1. Direction 1 — combinations for real use cases

Each hypothesis's full specification is in `COMPLIANCE.md` (one row per hypothesis).

### Family F-REC — recession classification

#### D1-02 — Does requiring a prior curve inversion cut the false alarms of a labour trigger? *(H1 confirmatory, H2 exploratory)*
- **H1 (confirmatory).** Rule: T10Y3M inverted at some month-end in the last 12 months **and** the Sahm rule fires
  at 0.50 pp. Compared with curve alone, does it cut false-alarm episodes by at least half without losing recall?
  - Curve parameters: Estrella & Mishkin 1998; Estrella & Trubin 2006. Sahm threshold: Sahm 2019.
  - Test: exact McNemar on discordant episodes.
  - Purge: 12 months, matching the recall window that starts 12 months before the peak.
- **H2 (exploratory).** Does the 0.30 pp variant signal ≥ 2 months earlier than the 0.50 pp rule alone (exact sign
  test)? Its threshold is our own choice, so it is exploratory.
- **Why.** The curve warns early but with a long, variable lead. The Sahm rule is reliable but late.

#### D1-13 — Permits fall, then unemployment rises *(exploratory)*
- **Question.** Permits YoY < 0, followed within 12 months by a Sahm gap ≥ 0.30 pp, compared against the 0.50 pp
  Sahm rule. Exact sign test on signal dates.
- **Why exploratory.** The 0.30 trigger and the 12-month window are conventions. It is registered regardless of
  D1-15.

#### D1-27 — Real-time recession-probability horse race *(confirmatory; Codex Q1)*
- **Question.** Expanding-window probits, 12 months ahead. Do these augmented models beat the term-only probit?
  - Model 1: term + credit.
  - Model 2: term + Sahm gap.
  - Model 3: term + credit + Sahm gap + permits.
- **Pass.** Brier skill score ≥ 0.10 (block-bootstrap Diebold–Mariano), log score better in ≥ 70% of held-out
  recessions, and calibration slope in [0.7, 1.3].
- **Disclosed choice.** The credit proxy switches from Baa − Aaa to HY–IG in 1997. This is a data-availability
  choice.

#### D1-23 — Recession probability as an equity overlay *(exploratory)*
- **Question.** Overlay w = 1 − P from D1-27 model 3. The purge is 12 months, because the model's label horizon is
  12 months.

### Family F-STATE — state dependence (all exploratory since revision 3)

#### D1-04 — Do new orders matter more when credit is stressed?
- **Question.** Interaction of the NEWORDER YoY sign (vintage) with a stress regime: HY–IG OAS above its expanding
  80th percentile. A second hypothesis uses ISM instead of NEWORDER.
- **Why exploratory.** The 80th percentile is our convention. A textbook stress definition could be registered for
  V-C later.

#### D1-17 — Market stress without macro weakness: false alarm or early warning?
- **Question.** The 3-month interaction of market stress with macro weakness.
- **Why exploratory.** It uses revised ISM, and VIX3M starts in 2007.

#### D1-06 — Monetary regime and the M2 signal
- **Why exploratory.** It was prompted by a fleet result we had already seen.

#### D1-30 — Filtered Markov switching with term- and credit-driven transitions *(Codex Q5)*
- **Question.** Does the model's out-of-fold log score gain ≥ 0.02 nats per month against fixed-transition Markov
  switching and against the linear interaction?

### Family F-TC — term × credit

#### D1-05 — Do term and credit spreads carry complementary information? *(H1 confirmatory; absorbs Codex Q2)*
- **H1 (confirmatory).** Is there a negative linear interaction of T10Y3M level × HY–IG OAS level (expanding
  z-scores) in next-month SPY excess returns, of at least 0.25 pp per month per 1 s.d. × 1 s.d.?
  - It has no thresholds. Levels follow Estrella & Mishkin (1998) and Gilchrist & Zakrajšek (2012).
- **H2 (exploratory).** The joint-distress state, 1{T10Y3M < 0.5 pp} × 1{HY–IG 6-month change > 0}, beyond the
  additive dummies.
- **H3, H4 (exploratory).** The same two tests on a Treasury return proxy (G6), with their own Treasury endpoints
  and margins.

### Family F-FCI — financial conditions

#### D1-28 — Point-in-time FCI vs a published FCI *(confirmatory; Codex Q3)*
- **H1.** Equal-weight point-in-time FCI (T10Y3M, HY–IG, VIX, sector breadth above the 10-month SMA) vs an overlay
  on the as-published NFCI (G15). Equal weights follow Timmermann (2006); the 10-month SMA follows Faber (2007).
- **H2.** Real-time PC1 weights (Stock & Watson 2002) vs equal weights.

### Family F-RISKOFF — confirmation and chains

#### D1-01 — Housing contraction confirmed by credit *(confirmatory)*
- **H1.** Cash when permits YoY < 0 **and** the HY–IG OAS YoY change > 0.
- **H2.** Cash when permits YoY < 0 **and** SLOOS net tightening > 0 (Lown & Morgan 2006).
- **Changed in revision 3.** Only zero thresholds on year-over-year changes are used; revision 2 used a 6-month
  change.

#### D1-12 — Credit, then manufacturing *(exploratory)*
- **Question.** SLOOS > 20 or HY OAS widening, followed by ISM < 50 within w ∈ {3, 6, 9} months.
- **Notes.** The SLOOS > 20 cut is flagged ad hoc, and ISM is revised-only.

### Family F-REENTRY

#### D1-14 — Re-entry by a 2-of-3 early-cycle vote *(exploratory since revision 3)*
- **Rule.** The exit is fixed: leave when SPY falls below its 10-month SMA (Faber 2007). Re-entry happens when at
  least 2 of 3 signals agree:
  - T10Y3M 3-month change > +0.50 pp;
  - new orders rising for 2 releases;
  - HY–IG 63-day change < 0.
- **Pass.** Missed-rally cost down ≥ 25% against SMA re-entry (exact sign test). At least 5 episodes are required.
- **Why exploratory.** The three vote thresholds are conventions.

### Family F-COMP — composites (exploratory: blocks informed by full-sample correlations)

The frozen point-in-time representatives (COMBINATORICS.md § 3.4):

| Block | Representative |
|-------|----------------|
| B1 | INDPRO YoY |
| B2 | PERMIT YoY |
| B3 | HY–IG |
| B4 | BUSLOANS YoY |
| B5 | UMCSENT |
| B6 | gold/copper YoY |
| B7 | M2 YoY |
| B8 | VIX |

#### D1-08 — Equal-weight block composite vs the best single representative
- **Assets.** SPY and 9 sector ETFs, total return; 10 hypotheses.

#### D1-10 — Do estimated weights beat equal weights?
- **Weightings tested.** Ridge logit, real-time PC1, inverse variance.
- **Guardrail.** Deflated Sharpe with N = the number of configurations fitted.

#### D1-19 — The composite sets the direction, market risk sets the size
- **Sizing tested.** VIX or realised volatility, compared against direction-only and a 10% volatility target.

#### D1-20 — Conviction sizing by vote count

#### D1-24 — Daily as-of updating of the monthly composite

#### D1-29 — Ragged-edge mixed-frequency dynamic factor vs PCA vs equal weights *(Codex Q4)*

### Family F-SECT — sectors (exploratory; total-return series needed, G17)

#### D1-07 — Late-cycle regime: defensive vs cyclical
- **Assets.** The defensive-minus-cyclical basket, plus XLU and XLI vs SPY.
- **Notes.** D1-22 is merged here.

#### D1-18 — Equity internals vs manufacturing for tech
- **Assets.** XLK and QQQ vs SPY.

#### D1-21 — A second indicator for the existing defensive pairs
- **Notes.** The members are fleet winners, so the N3 null is mandatory.

### Family F-HOUS — housing (exploratory)

#### D1-03 — k-of-3 within housing

#### D1-11 — Housing composite vs single housing indicators
- **Scope.** 3- and 5-member composites; SPY plus XHB, XLB and XLY relative returns.

### Family F-DIV

#### D1-16 — Soft vs hard data divergence *(exploratory)*

### Family F-FLEET (fleet-winner members; N3 mandatory)

#### D1-09 — Diffusion index of the frozen fleet rules *(exploratory)*

### Family F-REV (robustness, every finalist)

#### D1-25 — Real-time vs revised gap for every finalist *(descriptive)*

### Family F-SPACE (diagnostic)

#### D1-15 — Stability of the lead order across cycles *(descriptive; gates nothing)*

---

## 2. Direction 2 — how many variations, and how many are real?

#### D2-01 — Raw size of the space *(descriptive)*
- **Answer.** Two-indicator combinations come to 1.9–2.5 × 10^10 per asset and alignment (COMBINATORICS.md § 2).

#### D2-02 — Effective dimensionality *(descriptive)*
- **Answer.** The participation ratio is 5.5. Its 90% interval is 3.8–6.4 with 24-month blocks, and 3.6–6.4 across
  block lengths of 12–48 months.

#### D2-03 — Dependence among fleet winners' return streams *(descriptive)*
- **Use.** Only as an input to the deflated Sharpe of fleet-member families.

#### D2-04 — Is dimensionality lower around recessions? *(exploratory)*

#### D2-05 — Marginal value of the k-th representative *(exploratory, F-COMP)*

#### D2-06 — Does a second member of a block add anything? *(exploratory, F-HOUS)*

#### D2-07 — Members or operator: which matters more? *(descriptive, inner folds only)*

#### D2-08 — How wide can a search be before it is mostly overfit? *(descriptive)*

#### D2-09 — Common-sample and power budget *(descriptive)*
- **Rule.** A hypothesis whose minimum detectable effect is more than 2× its margin is labelled "underpowered" in
  advance. It is never dropped.

#### D2-10 — Alignment variants *(descriptive, F-REV)*

#### D2-11 — Is the useful combination the same across assets? *(descriptive)*

#### D2-12 — Do frozen fleet winners capture most of the benefit? *(exploratory, F-FLEET)*

---

## 3. Priority ranking (exactly 10)

| Rank | ID | Confirmatory hypotheses | Short name |
|-----:|----|------------------------:|------------|
| 1 | D2-09 | — | Power and common-sample budget |
| 2 | D1-27 | 3 | Recession-probability horse race |
| 3 | D1-05 | 1 | Term × credit interaction (parameter-free) |
| 4 | D1-28 | 2 | Point-in-time FCI vs NFCI |
| 5 | D1-01 | 2 | Permits confirmed by credit |
| 6 | D1-02 | 1 | Curve inversion + Sahm 0.50 vs curve alone |
| 7 | D1-04 | 0 | New orders × credit stress (exploratory) |
| 8 | D1-14 | 0 | Re-entry vote (exploratory) |
| 9 | D1-08 | 0 | Block composite vs best single (exploratory) |
| 10 | D2-08 | — | Search breadth vs PBO |

## 4. Counts (reconciled)

| Object | Count |
|--------|------:|
| Registry entries | 39 = 35 live + 3 archived + 1 superseded |
| Live pairs with a tournament grid | 35 (164,176 rules) |
| Indicators behind the live pairs | 26 |
| Indicators in the descriptive panel | 29 |
| Strict point-in-time panel | 14 |
| Questions | 40 (28 + 12) |
| Families | 13 |
| Hypotheses | 76 |
| Confirmatory hypotheses | 9, in 5 questions and 4 families |
| Gate mutation tests | 29 (run in the hook with GIT_* variables stripped) |

## 5. Changes in revision 3, by Lead item

| Item | Change |
|------|--------|
| 1 Provenance | The confirmatory set is relabelled "discovery-informed prospective confirmations". Parameter provenance (`source_type`, source) and question provenance are recorded. Demoted: Sahm 0.30 (D1-02.H2, D1-13), D1-04 (80th percentile), D1-14 (vote thresholds), D1-05.H2–H4. D1-01 now uses YoY zero thresholds. Count: 14 → 9 hypotheses, 8 → 5 questions, 6 → 4 families. The Bonferroni split is 0.05 / 4. |
| 2 Granularity | Every hypothesis is a structured object with its own hid, status, asset, endpoint, pass rule (enumerated test, α or interval), min_events, horizon, purge and family. The D1-05 Treasury hypotheses now have Treasury endpoints. |
| 3 Gate | JSON Schema validation (no KeyError). Semantic checks: numeric Sahm = 0.50; an enumerated correction method, never "none" where hypotheses exist; family references; enumerated tests. Tracks are checked against vintage files, the release calendar, the snapshot manifest and the market whitelist (R17). Purge is derived from the endpoint's label definition (R5). The gate reads staged blobs (`--staged`, used by the hook). 29 mutation tests. The `--no-verify` bypass is documented. |
| 4 D1-02 / D1-13 | Exact McNemar and exact sign tests with α. Purge 12 to match the recall window. |
| 5 Power | Monthly annualisation fixed (quadratic Sharpe term ÷ 12). 8-year range 0.45–0.65; 3-year range 0.73–1.06 (ρ 0.8–0.9). Synthetic power notes for CVaR, interaction and episode tests (`scripts/power_notes.py`). |
| 6 PR CI | Block lengths 12 / 24 / 36 / 48 give intervals from [3.63, 6.31] to [3.94, 6.41]. |
| 7 Assets | The limitation is stated in § 0.7 and README_zh. The only non-equity hypotheses are D1-05.H3 and H4 (Treasury proxy, exploratory). |
| 8 Low | 1.9–2.5 × 10^10. D1-05 typo fixed. README_zh corrected: the n/a baselines and the gate's real scope are stated, the glossary is extended, the PDF is regenerated and the HTML is checked at A4 width. Li–Ji: 13.0 (published formula) is the M_eff figure; Σ min(λ, 1) is labelled an ad hoc capped-eigenvalue sum. |

## 6. Open questions for the user

1. **V-S.** May we acquire a sequestered international real-time dataset under a blind protocol? Without it, the
   recession questions cannot be decided for many years.
2. **V-C.** Should the frozen forward log start in 2026-11?
3. **Data.** May we add G5 (S&P 500 total return before 1993), G13 (Philadelphia Fed real-time data), G15 (NFCI
   vintages, needed by D1-28), G16 (Baa / Aaa) and G17 (total-return ETF series)?
4. **Corrections.** Is per-family correction, with a 0.05 / 4 Bonferroni sensitivity check, acceptable? Or should
   all 9 confirmatory hypotheses be corrected together?
5. **Promotion.** Should any exploratory question be promoted later with a cited parameter? For example, D1-04
   could use a published stress threshold.
