# Validation Audit 2026-04-19 — Research Ray

**Reviewer:** Research Ray
**Scope:** Validation audit of the HY-IG v2 narrative on two axes — reproducibility (would another Ray write similar prose?) and stakeholder resolution (do shipped rules actually satisfy S18-* / SL-* in spirit?).
**Artifacts audited:**
- `docs/portal_narrative_hy_ig_v2_spy_20260410.md` (current narrative, 649 lines)
- `docs/portal_glossary.json` (3 terms + 7 status labels)
- `docs/schemas/narrative_frontmatter.schema.json` + example
- `docs/stakeholder-feedback/20260418-batch.md` (S18-* / SL-*)
- `docs/agent-sops/research-agent-sop.md` + `docs/standards.md` RES section
- `docs/cross-review-20260419-ray.md`

---

## Axis 1 — Reproducibility Audit

Would another Ray, given the same artifacts + SOP, write recognisably similar prose? **Deterministic** = rule constrains output closely enough that two Rays converge. **Discretionary** = two reasonable Rays will diverge on wording or content selection.

### Narrative elements audited (17)

| Narrative element | SOP rule | Deterministic? | Discretion point | Captured in schema? | Proposed fix |
|---|---|---|---|---|---|
| Story page headline structure (position, H2, em-dash-one-liner) | RES-11 | Partial | "2-3 KPI metrics" — which 2-3? Current: Sharpe+OOS window+one-liner | `headline` in `narrative_frontmatter` (prose only, no field split) | RES-18 (below): mandate KPI-trio and word-order template |
| Headline exact phrasing ("Sharpe 1.27 over 8-year OOS — credit spreads as…" vs "15-year Sharpe 1.27: credit spreads warn…") | RES-11 | **Discretionary** | Sentence structure and order | No | RES-18: offer 2 sanctioned templates rather than free-form |
| Plain English hook (`<details><summary>🧒 Plain English</summary>`) wording | Rule 1 / RES-PA1 | **Discretionary** | Tone register + length | `plain_english` field exists in schema but is free-form | Template with fixed 2-3 sentence structure |
| "What this means for investors" clause wording | RES-9 | Partial (mandates presence) | Verb choice ("trimmed" vs "de-risked" vs "rotated"); action specificity | No | RES-19 (below): 3 archetype templates (Drawdown-avoidance / Re-entry / Regime-filter) |
| Bullet structure (historical observation + action clause) | RES-9 | Deterministic on structure | Observation depth, example choice (e.g. "crossing stress band in mid-2007" vs "June-2007 BBB widening") | No | Already covered by RES-9 format; leave open |
| Historical-episode selection (Dot-Com + GFC + COVID + 2022 mention) | RES-8 + META-ZI | **Discretionary** | Which episodes + how many? Current narrative picks 4, another Ray could add 2018 or 2015 Shanghai devaluation | `historical_episodes_referenced` in frontmatter (enum includes taper_2018, inflation_2022) — structural presence captured, selection not | RES-20 (below): codify selection criteria (coverage-of-drawdown-types × signal-behaviour variety) |
| Zoom-chart cross-reference format (in-paragraph `(see ... — path — with labelled markers at …)`) | RES-8 | Partial | Parenthetical vs named link vs image-embed; which format per episode? | Yes (`override_needed` + `override_reason`) | Pick one canonical format per register |
| Bibliography entries (17 papers across 4 categories: Credit/Method/Regime/HY-IG-specific) | RES-PA1 + "Bibliography Scale" | **Discretionary** | Which 17 of ~40 candidate papers? | No | RES-21 (below): "must-cite" vs "may-cite" split tied to method list |
| Inline-definition vs glossary-link choice | Rule 1 + Rule 2 + Rule 6 | **Discretionary** | "basis point" inline on first use AND in glossary — overlap acceptable? Current narrative defines inline and also adds glossary entry | `glossary_terms` lists what's invoked, not what's defined inline | Add decision rule: first occurrence = inline-short + tooltip link; repeat occurrences = tooltip only |
| Method Justification "Why we chose this method" sentence | Rule 3 | Deterministic on presence | Exact wording | No | Leave as-is (Rule 3 is example-driven) |
| 8-element block structure (Why / How / Method / Graph / Obs / Interp / Caveats / Link-back) | RES-EP1 | Deterministic | Prose length per element | Partial (section `id`) | Word-count floor/ceiling per element |
| Transition sentences between pages ("Transition to Page N:…") | RES-PA1 | **Discretionary** | Which sentence? Length? Hook? | No | Template: "These numbers… but to understand X we need to…" pattern OR leave free |
| "How the Signal is Generated" plain-English walkthrough (HMM explained without formula) | Rule 7 / RES-7 | Partial (mandates no-formula + 3-step narrative) | Analogy choice ("stress meter" vs "weather station" vs "traffic signal") | Anchor `how_signal_generated` | Offer 2 sanctioned analogies or leave free |
| "How to Read the Trade Log" subsection | RES-PA3 | Deterministic on presence | Concrete example choice (COVID 2020 currently; GFC or 2022 equally valid) | Anchor `how_to_read_trade_log` | Leave free |
| Status vocabulary usage (when to label something "Validated" vs "Available" vs "Mature") | RES-10 / RES-VS | **Discretionary on usage** | Deterministic only on label set, not on when each applies | `status_labels_used` enum | RES-22 (below): decision table for status assignment |
| Scope-note prose ("This page focuses on credit alone; see VIX × SPY for…") | RES-PA1 | **Discretionary** | Inclusion + pair-cross-reference style | No | Template with required cross-refs to related pairs |
| Caveat ordering on Strategy page (5 caveats currently, which order?) | none | **Discretionary** | Which 5? Which order? | No | RES-23 (below): 4 required caveat archetypes + optional 5th |

### Reproducibility gaps by severity

- **High-severity (another Ray meaningfully diverges):** headline exact phrasing, historical-episode selection, bibliography entries, caveat ordering, status-label usage.
- **Medium-severity (wording differs but content stays):** investor-impact clause wording, transition sentences, HMM analogy, scope note.
- **Low-severity (rule is tight enough):** 8-element block structure, Rule 7 no-formula constraint, Rule 9 bullet structure, zoom-chart cross-reference presence.

---

## Axis 2 — Stakeholder Resolution Audit

| Stakeholder item | Claimed SOP rule | HY-IG v2 narrative evidence | Spirit met? | Gap |
|---|---|---|---|---|
| **S18-1** Probability Engine + Position panels + plain-English signal-gen | RES-7 + APP-SE1 + APP-SE2 | Strategy page §"How the Signal is Generated" + §"How the Signal Translates to Action". No formula; 3-step narrative (world→detect→act); uses "stress meter" analogy. | **Yes** (narrative side). The Ace panel side is covered by APP-SE1/SE2 — not Ray's concern. | Ray's contribution is good; risk is Ace's Streamlit panel diverging from Ray's prose. No contract between the two. |
| **S18-12** Investor-impact bullet clauses | RES-9 | Sampled 5 bullets: (1) "Credit led equity by ~5 months — investor would have had nearly half a year to trim"; (2) "Spreads widened from 300 to 2,000+ — rotate to cash before Lehman"; (3) "Predicted 3 of 4 major drawdowns — pair with separate yield-curve signal"; (4) "Relationship strongest during stress — signal earns keep during crises"; (5) "OOS 8 years — evidence of durable edge, allocate real capital". | **Yes** — all 5 carry concrete action clauses ("trim", "rotate", "pair with", "earns keep", "allocate real capital"). Bullet 4 is the weakest (slightly phatic: "earns its keep" is generic) but still carries implicit action ("follow without return drag"). | Bullet 4 phrasing borders on generic — risks becoming a template phrase re-used across pairs without thought. |
| **SL-1** Headline-first structure | RES-11 | Story page opens: `## Sharpe 1.27 over 8-year OOS — credit spreads as a multi-month early-warning signal for equity drawdowns` followed by `**Key metrics (OOS 2018-2025):** Sharpe 1.27 / ann ret 11.3% / max DD -10.2%`. Hook paragraph and narrative arc follow. | **Yes** — headline is genuinely the punchline (risk-adjusted outperformance vs buy-and-hold with dramatically lower drawdown). Reader gets the numerical stakes in <10 words. | Note: **MEMORY says "Sharpe 1.27 over 15-year OOS"** per my project memory; narrative says **"8-year OOS (2018-2025)"**. OOS window claim is inconsistent across artifacts. **See Question 1 to Lesandro.** |
| **SL-4** Dot-Com zoom-in cross-reference | RES-8 + META-ZI + VIZ-V1 | Story §What History Shows — Dot-Com paragraph: `(see the Dot-Com zoom-in chart below -- output/_comparison/history_zoom_dotcom.json -- with labelled markers at Mar 2000, Aug 2000, Mar 2001, and Jul 2002)`. Markers match the stakeholder's worked sketch. | **Yes** — genuinely helpful, not pro-forma; stakeholder's specific dates (Mar 2000, Jul 2002 WorldCom) are all cited. | In frontmatter the Dot-Com entry has `override_needed=false` but the prose references HY-IG widening specifically ("spreads climbed from 500 to 1,000+ bps") — this is an indicator-tied reference per META-ZI §3, should be `override_needed=true`. Mechanical inconsistency between prose and frontmatter assertion. |
| **SL-5** GFC zoom-in cross-reference | RES-8 + META-ZI + VIZ-V1 | Story §What History Shows — GFC paragraph references `output/_comparison/history_zoom_gfc.json` with markers at Oct 2007, Sep 2008, Dec 2008. Stakeholder sketch called for Oct 2007, Dec 2007 (~9 mo window before recession). Current narrative covers Oct 2007 + Sep 2008 + Dec 2008 — Dec 2007 (the stakeholder's second requested anchor) is **not** marked. | **Partial** — GFC marker set diverges from stakeholder's requested set. `override_needed=true` in frontmatter correctly flags this as indicator-tied. | Marker-date selection: Ray picked canonical crisis dates; stakeholder sketched the lead-lag pre-recession window. Both valid; stakeholder intent favours lead-lag anchors. |
| **RES-3 writing voice** (Part D/E) | Rule 3 — method justification | Every method block carries "Why we chose this method" prose (Toda-Yamamoto → "works correctly with non-stationary data"; Jorda → "robust to misspecification"; HMM → "lets data find the regime boundaries"). | **Yes** — consistent and connected to the economic question. | — |
| **RES-4 unit discipline** (Part D/E) | Rule 4 — dual notation | First occurrences carry dual notation: `300 to 2,000+ basis points (3% to 20%+)`; `5 basis points (0.05%)`; `43 bps per trading day`. | **Yes** — systematic. | Spot: "annualized return +18.4%" (Quartile Returns §5) has no bps equivalent — but per Rule 4 "subsequent occurrences can drop one form"; this is 10+ occurrences into the narrative so compliant. |
| **RES-5 storytelling arc** (Part D/E) | RES-PA1 — Hook / Story / Evidence / Strategy / Method | Five page types present with explicit transitions. "Transition to Page N:…" sentences bridge all four breaks. | **Yes** — arc is complete. | Transitions are discretionary (see Axis 1). |
| **RES-6 glossary 4-element rubric** (Part D/E) | Rule 6 | `portal_glossary.json` has 3 term entries. Sampling: **Basis point (bp)** has plain_english + why_it_matters + example (3 of 4; no formula — acceptable per Rule 6: formula is optional). **Credit spread** has 3 elements. **HMM stress probability** has 3 elements. | **Yes** for the 3 defined entries. | **But narrative invokes many more terms not in portal_glossary.json**: counter-cyclical, Merton model, OAS, HMM (as a separate entry from "HMM stress probability"), Jorda local projections, quantile regression, transfer entropy, pre-whitening, Toda-Yamamoto, HC3, HAC/Newey-West, GJR-GARCH, SHAP. The in-body "Glossary" table on Page 5 covers most, but `portal_glossary.json` (the tooltip-rendering source of truth) is drastically under-populated. This is a **RES-6 spirit violation** — the rubric applies per-entry but the JSON is missing 20+ entries that the narrative uses. |
| **S18-4 follow-up** Status vocabulary | RES-10 + RES-VS | `portal_glossary.json` has all 7 canonical status labels defined. Narrative `chart_status: "ready"` appears 7 times — **but "ready" is NOT in the canonical list** (Available / Pending / Validated / Stale / Draft / Mature / Unknown). | **Partial violation** — "ready" used in narrative is not defined in portal_glossary.json. Either (a) add "ready" to canonical list (probably meaning "Available"), or (b) replace all 7 occurrences with "Available". | Strict RES-VS violation: pre-handoff self-check should have caught "ready". Currently un-defined at render time. **See Question 2 to Lesandro.** |

### Stakeholder-resolution gaps (summary)

1. **OOS window inconsistency** — narrative says 8-year OOS (2018-2025); project MEMORY and prior task context say 15-year OOS. Which is canonical?
2. **`chart_status: "ready"`** is not in the canonical status vocabulary — RES-VS violation at the prose layer.
3. **`portal_glossary.json` is drastically under-populated** — 3 term entries defined; narrative invokes ~20 terms that tooltip rendering (APP-SE5 L1) would currently fail on.
4. **Dot-Com `override_needed=false` in frontmatter** but prose is indicator-tied → META-ZI contract violation (should be `true`).
5. **GFC marker set** diverges from stakeholder SL-5 sketch (missing Dec 2007 lead-lag anchor).

---

## Axis 3 — Proposed SOP fixes (6 RES-* proposals)

### Proposed RES-18 — Headline Template Constraint

**Rule text:** Story headline (RES-11) must instantiate ONE of two templates verbatim (keyword-substituted):
- Template A: `## {metric_trio} — {mechanism one-liner}` where `metric_trio = "Sharpe X.XX over N-year OOS"` (OOS window MUST match `results/{id}/winner_summary.json.oos_period_start/_end`).
- Template B: `## {N-year} Sharpe X.XX: {one-liner}` (compact form for dashboards).
Ray picks by register (Template A for primary research pair, Template B for portfolio-level dashboards). Any other form requires design_note.md rationale.
**Closes:** Axis 1 high-severity (headline phrasing discretion). **Cross-ref:** RES-11, ECON-H5 (winner_summary.json OOS field).

### Proposed RES-19 — Investor-Impact Clause Archetype Templates

**Rule text:** Every RES-9 "what this means for investors" clause instantiates one of 3 archetypes:
- **Drawdown-avoidance** — "would have trimmed/rotated X exposure before the Y drawdown"
- **Re-entry / signal-off** — "would have re-added exposure when {signal} crossed back below {threshold}"
- **Regime-filter complement** — "pair with {other signal} to cover {drawdown type} the credit signal cannot see"
Each bullet explicitly cites the archetype in a machine-readable `{{archetype:drawdown-avoidance}}` comment. Bullets that instantiate none are gate failures.
**Closes:** Axis 1 medium-severity (investor-impact wording); locks template quality without forcing robotic prose.
**Cross-ref:** RES-9, GATE-26.

### Proposed RES-20 — Historical-Episode Selection Criterion

**Rule text:** The set of episodes a narrative references (per RES-8) MUST cover both (a) drawdown-type variety and (b) signal-behaviour variety. Concretely, the episode set MUST include at least one episode where the signal:
1. **Gave a long lead** (e.g. GFC — months of warning),
2. **Coincided with equity move** (e.g. COVID — simultaneous),
3. **Failed or under-performed** (e.g. 2022 rate shock for credit).
A fourth optional "confirmer" episode (e.g. Dot-Com for credit pairs) may be added. Selection rationale is recorded in `historical_episodes_referenced` via new `selection_reason` field (enum: `long_lead / coincident / failure_case / confirmer`).
**Closes:** Axis 1 high-severity (episode selection discretion). **Cross-ref:** RES-8, META-ZI, schema update to narrative_frontmatter.

### Proposed RES-21 — Bibliography Must-Cite Manifest

**Rule text:** Bibliography entries split into **must-cite** (tied to method choices) and **may-cite** (background). Must-cite is mechanically derived: for every method in `results/{id}/core_models_*/` manifest, the method's seminal paper is auto-required via a lookup table `docs/bibliography_method_map.json` (Ray-owned, META-CF). Additional may-cites at Ray's discretion capped at 40% of total. Thin must-cite coverage (< method count) blocks acceptance.
**Closes:** Axis 1 high-severity (bibliography discretion). **Cross-ref:** RES-PA1, ECON-C1, META-CF.

### Proposed RES-22 — Status-Label Assignment Decision Table

**Rule text:** The mapping from artifact condition → status label is deterministic, in a new `docs/portal_status_label_rules.json` (Ray-owned):
| Condition | Label |
|---|---|
| smoke test pass + Defense-2 pass + GATE-27 pass | `Available` |
| smoke test pass + Defense-2 pass + 2+ acceptance cycles with no regression | `Mature` |
| Defense-1 only (producer self-check) | `Draft` |
| Defense-1 + Defense-2 | `Validated` |
| artifact exists but data stale (> 90 days) | `Stale` |
| render-time classification fails | `Unknown` |
| scheduled but not produced | `Pending` |
Narrative uses whichever label the condition satisfies; novel condition requires canonical-list amendment first. Retires the prose `"ready"` anti-pattern.
**Closes:** Axis 1 high-severity (status usage) + Axis 2 `"ready"` gap.
**Cross-ref:** RES-10, RES-VS, DATA-VS, META-UNK.

### Proposed RES-23 — Strategy-Page Caveat Archetype Set

**Rule text:** The "Important Caveats" section on the Strategy page MUST instantiate these 4 archetypes, in order:
1. **Transaction-cost sensitivity** — quote the backtest assumption + breakeven cost
2. **Execution-delay sensitivity** — quote the maximum acceptable delay
3. **Regime-dependence failure** — cite the historical episode where the signal under-performed
4. **Model-drift / structural-break** — cite at least one post-sample development (Fed tool, microstructure, etc.) that could alter the relationship
Optional 5th slot for pair-specific caveats. Current HY-IG v2 has all 4 + 1 — compliant. Missing archetype = gate failure.
**Closes:** Axis 1 high-severity (caveat ordering/selection).
**Cross-ref:** RES-PA2 (skeptical reader framing), RES-EP1 Element 7.

---

## Axis 4 — Questions to Lesandro

1. **OOS window canonical value.** Narrative says 8-year OOS (2018-2025); project MEMORY.md says "Sharpe 1.27 over 15-year OOS"; `winner_summary.json` OOS dates are the ground truth (ECON-H5). Which number should the headline carry? If 15-year, narrative needs revision; if 8-year, MEMORY needs correction.
2. **`chart_status: "ready"` fate.** Is "ready" an undeclared synonym for "Available" (and therefore a RES-VS violation to be swept to "Available") OR a genuinely separate state (producer has finished but Defense-2 pending) that should be added to the canonical 7-label list as an 8th label? This is a style/taste call — either direction is defensible.
3. **Historical-episode selection philosophy.** Should RES-20 mandate "failure-case" coverage (forcing 2022 to always appear for credit pairs), or is including a failure case author's judgment? "Failure case" inclusion exposes humility but dilutes the pitch.
4. **Bibliography must-cite automation.** Is a `docs/bibliography_method_map.json` lookup too mechanical for a humanities-adjacent deliverable, or is determinism more important than author voice in bibliography selection?
5. **Headline templates — one or two?** RES-18 proposes two templates. Is that richness worth the compliance cost, or should we converge on one template across the entire portal for brand consistency?

---

## Deliverable Summary (≤250 words)

1. **Narrative elements audited:** 17 discrete elements across 5 narrative pages + 1 glossary JSON + 1 frontmatter schema instance.
2. **Reproducibility gaps by severity:** 5 high (headline phrasing, episode selection, bibliography entries, caveat ordering, status-label usage); 4 medium (investor-impact wording, transitions, HMM analogy, scope note); 4 low (8-element structure, Rule 7 no-formula, Rule 9 bullet structure, zoom-chart cross-ref presence).
3. **Stakeholder-resolution gaps:** (a) OOS-window inconsistency between narrative (8-year) and MEMORY (15-year) — headline veracity at risk; (b) `chart_status: "ready"` is a RES-VS violation — "ready" is not canonical; (c) `portal_glossary.json` under-populated — only 3 term entries for a narrative invoking ~20+ jargon terms, tooltip rendering would fail; (d) Dot-Com `override_needed=false` in frontmatter contradicts indicator-tied prose (META-ZI violation); (e) GFC marker set diverges from stakeholder SL-5 sketch (missing Dec 2007 anchor).
4. **Top 3 rule proposals:** RES-18 headline template constraint (closes highest-severity reproducibility gap); RES-20 historical-episode selection criterion (closes discretionary episode picking); RES-22 status-label assignment decision table (closes both Axis 1 discretion and the Axis 2 "ready" violation simultaneously).
5. **Top question for Lesandro:** OOS window canonical value — narrative says 8-year, memory says 15-year; headline veracity blocks acceptance until resolved.

---

**File length:** ~240 lines (under 500-line cap).
