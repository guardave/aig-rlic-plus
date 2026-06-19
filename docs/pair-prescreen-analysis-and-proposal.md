# Pair Pre-Screening: Analysis & Proposal

**Prepared for:** Stakeholder discussion
**Author:** Lesandro (Lead) · 2026-06-19
**Status:** For discussion. Recommendations are actionable; the numeric thresholds are deliberately left for stakeholder calibration.
**Companion (technical):** `docs/pair-prescreen-proposal.md` (design detail) · `scripts/pair_prescreen.py` (working POC)

---

## Executive summary

A stakeholder proposed inserting a **lightweight Pair Screening step before full dashboard development**, so that pairs with limited practical value or poor operational feasibility do not consume the full dashboard-build + deep-QC cycle. This paper tests that idea against our existing portfolio of 13 live pairs.

**Finding:** the proposal is sound and **immediately feasible at near-zero added cost.** All four screening dimensions the stakeholder named map directly onto data we *already produce* in the Data and Econometrics stages — i.e. **before** the expensive charting, narrative, portal-assembly and deep-QC stages. A screen placed there can divert weak pairs early and roughly **halve the build cost of every pair that gets rejected.**

**Recommendation:** adopt the screen as a gate after the Econometrics stage, but calibrate its thresholds collaboratively — and, more importantly, act on two structural findings the screening exercise surfaced (below), which matter more than any individual pair verdict.

---

## 1. Background

Our original operating thesis was to build one high-quality dashboard (HY-IG) and replicate it cheaply across pairs. In practice, each pair has its own story, evidence and strategy logic, so each requires its own deep quality review — checking that Story, Evidence, Strategy and Methodology are mutually consistent, that the rank-1 strategy connects logically to the rest, that the analysis is persuasive, and that the economic logic holds. **That review is expensive, and today it happens only *after* a pair is fully built.**

The stakeholder's proposal: assess pairs at a higher level *first*, on four dimensions —

1. **Strategy Performance** — trade count, Sharpe, drawdown vs. benchmark;
2. **Operational Practicality** — data release delay, data availability, execution feasibility;
3. **Crisis Validation** — did the signal work across different market crises;
4. **Durability** — effective only in one period, or persistent across regimes.

— and only invest the full build + QC cycle in pairs that clear the bar.

## 2. The proposal in one picture

The key realisation is that the four dimensions are **already measured** by the time the Econometrics stage finishes. The screen therefore needs no new analysis — it reads existing outputs and renders a verdict:

```
  Data sourcing → Data build → Econometrics + strategy tournament
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │   PAIR PRE-SCREEN      │   ← reads existing outputs only
                              └───────────────────────┘
                                          │
              PROCEED / CONDITIONAL ◄──────┴──────► DEFER / DROP
                       │                                 │
         full dashboard build + deep QC        parked; no dashboard, no deep QC
```

| Dimension | What we already produce that measures it |
|-----------|------------------------------------------|
| Strategy Performance | Out-of-sample Sharpe, uplift vs. buy-and-hold, drawdown reduction, trade count, turnover |
| Operational Practicality | Data source type & freshness, signal release lag, real-time tradability, turnover |
| Crisis Validation | Per-crisis strategy performance (Dot-Com, GFC, COVID, 2022) |
| Durability | In-sample vs. out-of-sample gap, statistical significance, winner-vs-field comparison, validation status |

**Verdict model:** each dimension is scored Green / Amber / Red; the pair is then **PROCEED** (build), **CONDITIONAL** (build, but commit upfront to foregrounding the weak dimension), or **DEFER/DROP** (park, do not build). The screen does **not** replace deep QC — it decides *which pairs earn it*.

## 3. Analysis: what the portfolio tells us

We built a working scorecard and ran it across all 13 live pairs. With a first, deliberately rough threshold set, the screen produced a **credible separation that matched independent expert judgement**:

| Verdict | Pairs | Why |
|---------|-------|-----|
| **DEFER/DROP** | ism_services, phlxsox, gold_copper, vix_vix3m | ism_services: in-sample Sharpe **−0.11** vs. out-of-sample 1.54 — a regime-lucky window, not a stable edge. The others: operationally heavy turnover (16–23×/year) that erodes practicality. |
| **CONDITIONAL** | busloans, hy_ig (×2), indpro (×2), m2sl, permit, petrol, umcsent | Real, useful edges with caveats. `busloans` is strongest: Sharpe 1.50, +0.61 over buy-and-hold, −1.0% drawdown vs. −23.9%, COVID-period Sharpe 2.75, low turnover. |
| **PROCEED** | *(none)* | See finding (a) below. |

That the automated screen independently flagged the same pairs an analyst would is the central feasibility result: **the signal needed to triage pairs is already in our data.**

### Two structural findings — more important than the verdicts

**(a) Not one pair qualifies as fully "PROCEED" — because none has passed a true final exam.**
Every recent pair is labelled *found-in-search*: its headline performance comes from the same data used to *select* the strategy, with no untouched holdout test. The screen makes this portfolio-wide reality impossible to ignore. A genuine "PROCEED" verdict requires a **final-exam (holdout) step that does not yet exist in our pipeline.** This is the single most consequential gap the exercise revealed.

**(b) Every pair shows a large jump from in-sample to out-of-sample Sharpe.**
This is structural: because the strategy tournament *selects* on out-of-sample performance, the winner's out-of-sample number is upward-biased. The practical implication for screening: **durability should be judged on the in-sample-to-out-of-sample *gap*, not the out-of-sample level alone.** A strong out-of-sample Sharpe sitting on a negative in-sample Sharpe (as in ism_services) is a red flag, not a green light.

### A calibration caution

Our first threshold set was **too strict** — it would have dropped `busloans`, one of our best pairs. The fix was straightforward (two thresholds were economically wrong), but the episode confirms the stakeholder's own caveat: **the framework is robust; the thresholds are where judgement and risk-appetite live, and they must be set with stakeholders, not by the tool.**

## 4. Recommendations

1. **Adopt the pre-screen as a gate after the Econometrics stage.** It is cheap (reads existing outputs), and it protects the most expensive part of the process (full build + deep QC).
2. **Calibrate thresholds collaboratively.** Use the working scorecard as a live instrument: run it on the existing 13 pairs, agree where the Green/Amber/Red lines sit, and encode the stakeholders' risk appetite rather than a developer's guess.
3. **Build the missing final-exam (holdout) step.** This is the highest-value structural improvement the exercise surfaced — without it, no pair can be more than provisionally trusted, and "Durability" can never be fully green. It also directly answers the stakeholder's "is it persistent across regimes?" question.
4. **Judge durability on the in-sample-to-out-of-sample gap**, not the out-of-sample headline. Make this an explicit screen rule.
5. **Generalise the operational and benchmark checks.** Two cheap upgrades materially strengthen the screen: (i) a uniform "does it beat a naive own-momentum benchmark?" test (already done for one pair) to catch leveraged-beta masquerading as alpha; (ii) capturing data-source freshness and release lag as structured fields so Operational Practicality scores without manual input.

## 5. Decision points for stakeholders

1. **Risk appetite / thresholds** — where should the Green/Amber/Red lines fall for Sharpe, uplift, turnover, crisis behaviour, and the in-sample/out-of-sample gap?
2. **Final-exam step** — do we commit to building the holdout test? (Recommended; it is the gating dependency for any real "PROCEED".)
3. **Treatment of already-built marginal pairs** — several live pairs would screen as DEFER/CONDITIONAL today. Do we retro-apply the screen (relabel/retire), or apply it only going forward?
4. **Granularity (Option D)** — the stakeholder leans Weekly + Monthly. The screen is granularity-agnostic, but Operational Practicality (release lag, tradability) interacts with frequency; we recommend aligning the screen once Option D is settled.
5. **Gate strictness** — should DEFER be a hard stop, or a "review before proceeding" soft gate that a human can override?

## 6. Bottom line

The stakeholder's instinct is correct and the cost of acting on it is low. Most of the screening machinery already exists; what is missing is (1) agreed thresholds and (2) a true holdout final exam. The screening exercise has, as a by-product, told us something uncomfortable but valuable: **our current portfolio is entirely search-phase, and we have been judging strategies on numbers that are upward-biased by construction.** Pre-screening is worth adopting — but its greatest immediate value is having made that gap visible.

---

### Appendix — POC scorecard (13 live pairs, illustrative thresholds)

Dimensions: **P** Strategy Performance · **O** Operational Practicality · **C** Crisis Validation · **D** Durability. (🟢 strong · 🟡 caveated · 🔴 fails · ⚪ insufficient data)

| Pair | P | O | C | D | Verdict |
|------|---|---|---|---|---------|
| busloans_spy | 🟢 | 🟢 | 🟡 | 🟡 | CONDITIONAL |
| gold_copper_xli | 🟢 | 🔴 | ⚪ | 🟡 | DEFER/DROP |
| hy_ig_spy | 🟢 | 🟢 | ⚪ | 🟡 | CONDITIONAL |
| hy_ig_v2_spy | 🟢 | 🟢 | ⚪ | 🟡 | CONDITIONAL |
| indpro_spy | 🟡 | 🟢 | ⚪ | 🟡 | CONDITIONAL |
| indpro_xlp | 🟡 | ⚪ | ⚪ | 🟡 | CONDITIONAL |
| ism_services_spy | 🟢 | 🟢 | 🟡 | 🔴 | DEFER/DROP |
| m2sl_yoy_spy | 🟢 | 🟢 | 🟡 | 🟡 | CONDITIONAL |
| permit_spy | 🟡 | 🟡 | ⚪ | 🟡 | CONDITIONAL |
| petrol_inv_spy | 🟢 | 🟢 | 🟡 | 🟡 | CONDITIONAL |
| phlxsox_spy | 🟢 | 🔴 | 🟡 | 🟡 | DEFER/DROP |
| umcsent_xlv | 🟡 | 🟢 | ⚪ | 🟡 | CONDITIONAL |
| vix_vix3m_spy | 🟡 | 🔴 | ⚪ | 🟡 | DEFER/DROP |

*Reproduce: `python scripts/pair_prescreen.py`. Thresholds are illustrative and uncalibrated; the table demonstrates feasibility and separation, not final verdicts.*
