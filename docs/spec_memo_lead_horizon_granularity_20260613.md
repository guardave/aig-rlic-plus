# Lead-Horizon Granularity: Decision Memo for Stakeholders

**Author:** Lead Lesandro
**Date:** 2026-06-13
**Branch:** `fix260613_lead_horizon`
**Status:** Decision required before daily-pair lead execution proceeds

---

## 1. Executive Summary

This memo presents findings from the lead-horizon wave (`fix260613_lead_horizon`) and lays out a decision for stakeholders on how to analyse lead time for daily-data pairs.

**What we set out to do:** extend the lead-analysis horizon from 6 months to 12 months across all pairs, make Lead Analysis and Lead Tournament mandatory Evidence components, and re-run tournaments where the extended grid revealed a better winner.

**What we found:** the approach works cleanly for monthly-data pairs (INDPRO, Permits, UMCSENT, C&I Loans) but produces methodology artifacts for daily-data pairs (VIX/VIX3M, Gold/Copper, HY-IG). A pilot re-run on Gold/Copper exposed the gap concretely and was reverted. Three monthly pairs are ready to proceed with re-runs; three daily pairs need a design decision on lead granularity before their analysis is actionable.

**The decision:** for daily-data pairs, should the lead analysis use monthly granularity (L=0..12 months, already done), weekly granularity (L=1..52 weeks), daily granularity (L=1..30 days), or a combination? Each has different tradeoffs in resolution, overfitting risk, interpretability, and execution cost.

---

## 2. Background: Why Lead-Horizon Analysis Matters

### The lead question

Every pair in the portal uses a **signal lead** — the delay between observing the indicator and acting on it. For example, Building Permits uses a 6-month lead (L6): the strategy reads January's permit number and uses it to position in July.

The original tournament for each pair tested a **coarse** lead grid — typically {0, 1, 2, 3, 6} months. This left the L7–L12 region completely unexplored. Were we missing better strategies at longer leads?

### The catalyst

Collaborator vichua4b's work on the Permits pair revealed that the data's "natural lead" (the lag at which signal-to-return correlations peak) is L8–9 months — substantially longer than the tournament's L6 winner. The tournament's L6 choice was an artifact of the coarse grid, not a principled lead selection.

### Stakeholder direction (2026-06-13)

1. Add **Lead Analysis** (signal-return correlation heatmap across leads) and **Lead Tournament** (best OOS Sharpe per lead) as mandatory Evidence components for all pairs.
2. Extend the lead horizon from 6 months to 12 months in all analysis.
3. Use an **economical, analysis-gated approach**: run the analysis first; only re-run the tournament if the extended grid produces a better winner (best lead lands at L7–L12).
4. Apply **universal monthly granularity** — even daily-data pairs — because physical lead time depends on data availability, reporting lag, and market reaction time, not sampling frequency.

---

## 3. What the Gating Analysis Found

We ran Lead Analysis + Lead Tournament across all 9 active pairs on the extended L=0..12 monthly grid. Results:

### 3.1 The gate table

| Pair | Data freq | Published lead | Best lead L* (L0..12) | Best Sharpe at L* | Published Sharpe | Gap | Decision |
|---|---|---|---|---|---|---|---|
| **indpro_spy** | Monthly | L6 | **L12** | 1.374 | 1.104 | +24% | **RE-RUN** |
| **indpro_xlp** | Monthly | L3 | **L8** | 1.423 | 1.115 | +28% | **RE-RUN** |
| **umcsent_xlv** | Monthly | L6 | **L11** | 1.188 | 1.020 | +16% | **RE-RUN** |
| **gold_copper_xli** | Daily | L0 | **L10** | 1.370 | 1.273 | +8% | **RE-RUN** |
| permit_spy | Monthly | L6 | L6 | 1.445 | 1.445 | 0% | Charts-only |
| vix_vix3m_spy | Daily | L0 | L3 | 1.869 | 1.130 | +65% | Charts-only* |
| hy_ig_spy | Daily | L0 | L1 | 1.439 | 1.408 | +2% | Charts-only |
| busloans_spy | Monthly | L6 | L5 | 1.500 | 1.500 | 0% | Charts-only |
| hy_ig_v2_spy | Daily (frozen) | L0 | L2 | 1.546 | 1.274 | +21% | Exempt |

*VIX shows a 65% gap at L3 — flagged but not gated for re-run because L3 is within {0..6}. See §5.

**4 pairs gate to RE-RUN** (best lead in L7–12). **5 pairs are charts-only** (best lead in L0–6, so the published winner's lead region still wins).

### 3.2 Monthly pairs: clean, proceeding as designed

The 3 monthly RE-RUN pairs (INDPRO × SPY, INDPRO × XLP, UMCSENT × XLV) have genuine findings: the extended L7–12 grid uncovered materially better strategies the coarse original grid missed. Both the gating sweep and the native tournament run monthly — no methodology gap. These re-runs are ready to execute.

Permit and busloans confirmed their published winners exactly — no re-run needed.

---

## 4. The Gold/Copper Pilot: What Went Wrong and What We Learned

### 4.1 What happened

We piloted the re-run cascade on Gold/Copper (daily data, gating sweep found L10 as best). The native daily tournament was re-run on the extended lead grid. It found a winner, but **not the one the gating sweep predicted**:

| | Gating sweep (monthly-resampled) | Native daily tournament |
|---|---|---|
| Best signal | pctrank_504d | **roc_5d** (5-day rate of change) |
| Best lead | L10 (10 months) | **L0** (same day) |
| Strategy | — | **Long/Short** |
| OOS Sharpe | 1.370 | **1.510** |
| Max drawdown | — | **-22.7%** (was -8.3%) |
| Turnover | — | **89/yr** (was 16/yr) |

### 4.2 Why the results diverged

The gating sweep and native tournament found different winners because they are **different analysis instruments**:

- The **gating sweep** resamples daily data to month-end, then tests a standardized comparator across leads. This is correct for comparing lead values apples-to-apples, but the monthly resampling compresses daily dynamics and can create artifacts.
- The **native tournament** runs the pair's full signal/threshold/strategy/lookback space at daily resolution. It explores a richer combination space and captures daily dynamics the monthly resampling loses.

For monthly-data pairs, both instruments run at the same frequency — they agree. For daily-data pairs, they diverge.

### 4.3 Why the native winner was rejected

The native tournament's "winner" (roc_5d, L0, Long/Short, Sharpe 1.510) was economically dubious for a macro-overlay pair:
- **5-day signal** on a commodity ratio that measures macro regime shifts — the signal horizon doesn't match the economic mechanism
- **89 turnovers/year** — approaching the validity ceiling; each turnover costs transaction fees
- **Max drawdown nearly tripled** (-8.3% → -22.7%) — the Sharpe gain came partly from the Long/Short leverage amplifying returns, not from a better signal
- The old winner (zscore_126d, L0, Long/Cash, Sharpe 1.273, DD -8.3%) is a more sensible macro overlay

**Decision:** the re-run was reverted; the old winner was restored. The lead analysis charts were published with honest disclosure.

### 4.4 The lesson

The pilot validated the approach for monthly pairs and identified a genuine methodology gap for daily pairs: **monthly resampling of daily data creates artifacts that make the gating sweep's lead-region findings unreliable for daily pairs.** A different lead granularity is needed.

---

## 5. The VIX Gap: A Gate Design Limitation

The gate triggers re-runs only when the best lead lands in L7–12 (the extended region the old tournament didn't test). But the gate table reveals a case where the gate **misses** a massive untapped improvement:

**VIX/VIX3M:** sweep best Sharpe = **1.869** at L3 vs published = **1.130** — a **65% improvement**. But L3 is within {0..6}, so the gate says "charts only."

This exposes a design gap: the gate catches "the extended region has something new" but not "the old tournament's lead grid was too coarse within its own region." VIX's original tournament may have tested only L0 — the entire L1–L6 region is unexplored.

**However**, VIX is a daily pair. The same monthly-resampling methodology gap from Gold/Copper applies: the sweep's 1.869 at "L3 months" is on monthly-resampled data; a native daily re-run at L3 (~63 trading days) could produce a completely different result. So the 65% gap is real in the analysis but **not safely actionable** until the daily-pair lead methodology is resolved.

---

## 6. The Open Question: Lead Granularity for Daily Pairs

For the 3 daily-data pairs (VIX/VIX3M, Gold/Copper, HY-IG), the monthly grid (L=0..12 months) serves **cross-pair comparability** but doesn't match the data's native dynamics. Three alternative granularities are on the table:

### Option A: Daily leads (L=1..30 days)

| Dimension | Assessment |
|---|---|
| **Resolution** | Maximum — matches the data's native frequency |
| **What it answers** | "Does the market need 1, 5, or 20 days to price this signal?" — a momentum-horizon question |
| **Overfitting risk** | **Extreme.** 30 daily leads × hundreds of signal/threshold/strategy combos = tens of thousands of specifications. L=13 days vs L=12 days is almost certainly noise. The "winner" at any specific day has no economic rationale |
| **Interpretability** | Low — "the best lead is 13 days" has no natural economic explanation for a macro-overlay pair; the practical advice maps to weeks or months |
| **Economic justification** | Weak for macro overlays — there's no publication lag to resolve, so the analysis becomes a momentum-horizon study (a different question from lead analysis). Relevant only for options-market microstructure or high-frequency overlays, which this portal doesn't serve |
| **Computational cost** | Low (30 grid points) |

### Option B: Weekly leads (L=1..52 weeks)

| Dimension | Assessment |
|---|---|
| **Resolution** | High — resolves monthly grid's coarseness (is VIX's "L3 months" really 10 weeks or 15 weeks?) |
| **What it answers** | "At what weekly horizon does the signal's predictive power peak?" — maps to real decision-making timescales (weekly rebalance, weekly risk committees, weekly options cycles) |
| **Overfitting risk** | Moderate — 52 grid points is large but each week is a meaningfully different timescale; weekly option expiry cycles ARE a real market rhythm |
| **Interpretability** | Medium — "the best lead is 12 weeks" is less intuitive than "3 months" for a layperson, but asset allocators think in weeks naturally |
| **Economic justification** | Good — weekly intervals correspond to real calendar/business rhythms (weekly data releases, options expiry, monthly rolling boundaries, quarterly earnings); the resolution genuinely helps distinguish short-term microstructure effects from medium-term macro effects |
| **Computational cost** | Moderate (52 grid points × full tournament per point) |

### Option C: Monthly leads only (L=0..12 months) — current state

| Dimension | Assessment |
|---|---|
| **Resolution** | Moderate — sufficient for monthly macro indicators; coarse for daily data |
| **What it answers** | "At what monthly lag does the signal peak?" — the macro-cycle question |
| **Overfitting risk** | Low — 12 grid points, well-separated; adjacent months are meaningfully different timescales |
| **Interpretability** | **High** — months are how asset allocators, central banks, and the financial press think about macro cycles |
| **Economic justification** | **Strong** for monthly indicators (publication lag + macro-cycle timescales). Weaker for daily data (resampling creates artifacts, as the Gold/Copper pilot proved) |
| **Computational cost** | Low |

### Option D: Combined (weekly + monthly)

Run **both** weekly (L=1..52 weeks) and monthly (L=0..12 months) for daily pairs; monthly only for monthly pairs.

| Dimension | Assessment |
|---|---|
| **Resolution** | Best of both — weekly resolves daily-pair dynamics; monthly provides cross-pair comparability |
| **Overfitting risk** | Moderate (the weekly grid's risk, since the monthly is already computed) |
| **Interpretability** | High — readers get the intuitive monthly view AND the precise weekly view; the contrast itself is informative ("the monthly grid says L3; the weekly grid resolves it to L=10–13 weeks") |
| **Evidence-page cost** | +1 block per daily pair (3 pairs × 1 additional "Lead Analysis — Weekly Resolution" block + 1 chart); 2 additional blocks if Lead Tournament is also weekly |
| **Computational cost** | Moderate (52-point sweep ×3 daily pairs) |

### Comparison matrix

| | Daily (1–30d) | Weekly (1–52w) | Monthly (0–12m) | Weekly + Monthly |
|---|---|---|---|---|
| Resolution for daily pairs | Very high | **High** | Low | **High** |
| Overfitting risk | **Extreme** | Moderate | Low | Moderate |
| ELI5 interpretability | Low | Medium | **High** | **High** (both views) |
| Economic justification | Weak | **Good** | Moderate | **Good** |
| Cross-pair comparability | None | Partial | **Universal** | **Universal** (monthly layer) |
| Actionable for re-runs? | Risky | **Yes** | Artifacts for daily | **Yes** (weekly layer) |
| Execution cost (this wave) | Low | Moderate | Already done | Moderate |

---

## 7. What Has Already Been Shipped (Track A)

Regardless of the daily-pair granularity decision, the following is built and verified on the branch:

1. **SOP rules authored:** ECON-LL1 (universal monthly lead granularity), ECON-LA1 (Lead Analysis mandatory), ECON-LT1 (Lead Tournament + analysis-gated conditional re-run), DPS-LEAD1 (mandatory Evidence blocks), DPS-CPX1 (narrative travels with its section), VIZ-LEAD1 (two chart standards).
2. **Lead Analysis + Lead Tournament charts** generated for all 8 non-frozen pairs (16 charts).
3. **Lead blocks wired** for the 4 charts-only-FINAL pairs: VIX, HY-IG, busloans (newly wired) + permit (already had them via vichua).
4. **ELI5 "daily data has no publication lag"** concept embedded in all 3 daily pairs' lead blocks — the reader understands why L0 dominance is expected for these pairs vs the genuine lead puzzle on monthly pairs.
5. **Cross-Period prose relocation** (DPS-CPX1): permit's orphan "Honest read on the cross-period charts above" narrative moved from Evidence to Strategy/Confidence (the only pair that had it).
6. **Chart-type registry** updated (v1.2.0): Lead Analysis + Lead Tournament methods registered, closing the unregistered-chart gap.
7. **Gold/Copper pilot re-run:** executed, evaluated, reverted — the methodology gap is documented, not papered over.

## 8. What Awaits the Decision

| Item | Depends on daily-pair granularity decision? | Status |
|---|---|---|
| 3 monthly RE-RUN pairs (INDPRO×SPY L12, INDPRO×XLP L8, UMCSENT×XLV L11) | **No** — proceed regardless | Ready to execute |
| Daily-pair lead blocks finalised | **Yes** — the weekly grid would add/refine their analysis | Blocked |
| Daily-pair tournament re-runs (VIX L3, Gold/Copper L10) | **Yes** — weekly grid provides the principled re-run basis | Blocked |
| ECON-LT1 gate amendment (second criterion for sweep-vs-published gap) | **Yes** — the right threshold depends on the granularity chosen | Blocked |
| Comprehensive verify + merge of the full branch | Depends on which items above are in scope | Waiting |

---

## 9. Recommendation (Advisory)

**Option D (Weekly + Monthly)** is the strongest combination for daily pairs:
- Weekly resolution answers the genuine question ("at what weekly horizon does the signal peak?") without the extreme overfitting risk of daily
- Monthly preservation maintains cross-pair comparability (every pair has L0–12 months; daily pairs additionally have L1–52 weeks)
- The weekly grid becomes the principled basis for any future daily-pair re-runs — no monthly-resampling artifacts
- The contrast between the two views is itself informative and teachable

**Daily (Option A) is not recommended** — extreme overfitting, no economic question to answer for macro overlays, and the resolution gain over weekly doesn't justify the noise.

**However**, this is a scope and resource decision. Option D adds a ~1-session Evan sweep (52 weekly leads ×3 daily pairs) + Vera charts + Ray narrative per pair. The decision should weigh whether that insight is worth the execution cost now, or whether to ship the monthly-only analysis for daily pairs and queue the weekly enhancement.

---

## 10. Decision Required

1. **For daily-data pairs (VIX/VIX3M, Gold/Copper, HY-IG), which lead granularity?**
   - A: Daily (1–30 days) — not recommended
   - B: Weekly (1–52 weeks) — recommended as an addition
   - C: Monthly only (0–12 months) — current state; adequate for cross-pair comparability but coarse for daily data
   - D: Weekly + Monthly — recommended (best of both)

2. **Should the 3 monthly RE-RUN pairs proceed now** (independent of the daily-pair decision)?

3. **Should the daily-pair weekly analysis (if chosen) ride this wave or be a follow-up?**

---

## 11. Stakeholder Decision (received 2026-06-20)

The wave was suspended 2026-06-13 and resumed 2026-06-20. Stakeholder decisions:

1. **Daily-pair lead granularity → Option D (Weekly + Monthly).** For the daily pairs (VIX/VIX3M, Gold/Copper, HY-IG), run a weekly sweep (L=1..52 weeks) in addition to the existing monthly grid. The weekly layer becomes the principled basis for any daily-pair re-runs; the monthly layer is retained for cross-pair comparability.
2. **The 3 monthly RE-RUN pairs proceed now** (INDPRO×SPY→L12, INDPRO×XLP→L8, UMCSENT×XLV→L11) — independent of the daily-pair decision.
3. **Reconciliation: fresh branch off current main** (`fix260620_lead_horizon`). The original `fix260613_lead_horizon` (73 commits behind main after the Sample archival + pairs #22–24) is preserved as reference; durable work is re-applied on today's code.

### Resume-time deltas vs the 2026-06-13 memo
- **Sample `hy_ig_v2_spy` is RETIRED/archived** (2026-06-20) — dropped from all lead-horizon scope (was "Exempt (frozen)"; now out of discovery entirely).
- **3 new pairs shipped post-suspend** (ism_services_spy, m2sl_yoy_spy — monthly; phlxsox_spy — daily). Under the "Lead Analysis + Lead Tournament mandatory for all pairs" rule, these now require lead blocks; phlxsox (daily) falls under Option D. Scope inclusion confirmed with stakeholder at resume.
- Permit's cross-period prose relocation (memo §7.5) already landed independently on main 2026-06-20.

*Decision recorded by Lead Lesandro on resume.*
