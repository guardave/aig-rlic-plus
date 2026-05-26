# Dashboard Comment-Log Analysis — 2026-05-26

**Source:** `temp/Step C - Dashboard Comment log.xlsx`, sheet `Log`.
**Scope:** 104 issues, 9 active pairs, captured 2026-04-15 → 2026-04-17.
**Status snapshot:** 44 Open, 38 (blank), 8 Closed, 1 ½ Closed, 1 Pending.

---

## 1. Pairs reviewed (by issue count)

| # issues | Pair (log label) | Internal pair_id |
|---:|---|---|
| 33 | Building Permit × SPY | `permit_spy` |
| 14 | SOFR-3M × SPY | `sofr_ted_spy` |
| 12 | HY-IG × SPX | `hy_ig_v2_spy` |
| 12 | UMCSENT × XLV | `umcsent_xlv` |
| 11 | Industrial Production × XLP | `indpro_xlp` |
|  7 | INDPRO × SPY | `indpro_spy` |
|  5 | DFF-TED | `dff_ted_spy` |
|  5 | Spliced TED × SPY | `ted_spliced_spy` |
|  5 | VIX/VIX3M × SPY | `vix_vix3m_spy` |

The `permit_spy` pair is an outlier (33 issues, ~3× the next-busiest pair). Treat its issue list as a both-of source — many of its findings are *template-level* defects surfaced first by the reviewer there.

---

## 2. Where issues live (Section × Pair matrix)

| Section | dff | hy_ig | indpro_s | indpro_x | permit | sofr | ted_spl | umcsent | vix | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Story** | 0 | 2 | 2 | 3 | 6 | 8 | 1 | 5 | 3 | **30** |
| **Evidence** | 3 | 3 | 4 | 3 | 2 | 3 | 0 | 4 | 2 | **24** |
| **Strategy** | 2 | 1 | 0 | 4 | 2 | 3 | 4 | 2 | 0 | **18** |
| Evidence — L1 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 8 |
| Strategy exec panel | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| Strategy — Execute | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 4 |
| Strategy — Performance | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 4 |
| Strategy — Confidence | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 4 |
| Evidence — L2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| All sections | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 |
| Methodology | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 2 |
| Glossary | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

**Story + Evidence + Strategy** together = 72 of 104 issues (69%). Methodology + Glossary are largely fine. The *Strategy execution panel / Execute / Performance / Confidence* sub-tabs are heavily flagged on `permit_spy` and `hy_ig_v2_spy` — those are pairs that use the full instructional-trigger card layout.

---

## 3. Cross-pair issues (TEMPLATE-LEVEL — fix once, affects all dashboards)

These themes reach **≥3 pairs**. They are not pair-specific drift; they are template/contract gaps. **Highest priority** because one fix lands across the portfolio.

### 3.1 — CROSS-T1: ELI5-clarity gaps (7 pairs, ~30 issues)

Most frequent class. Reviewers repeatedly ask for plain-English explanations of jargon used without inline definition: `OOS Sharpe`, `Max Drawdown`, `Turnover`, `Win Rate`, `OOS`, `bps`, `Q1–Q4 quartile`, `contango / backwardation`, `hedging demand`, `option pricing theory`, `regime`, `signal column names`, `pre-whitened CCF`, etc.

Affects: `hy_ig_v2_spy, indpro_spy, indpro_xlp, permit_spy, sofr_ted_spy, umcsent_xlv, vix_vix3m_spy`.

Representative:
- *(umcsent_xlv Strategy)* "For 'How the signal is Generated' section, please add a small statement to explain what is OOS Sharpe, OOS Return, Max Drawdown, Turnover, Win Rate."
- *(vix_vix3m_spy Story)* "Footnote can be added to explain technical terms like 'contango', 'backwardation', 'hedging demand', 'put demand', 'option pricing theory'."

**Template fix.** Add a **First-Use Term Helper** to `page_templates.py`: an automatic glossary-tooltip system that wraps every term in `docs/portal_glossary.json` on first appearance per page with a hover/click definition. Tooltips already exist (glossary sidebar) — what's missing is automatic in-prose injection. Could be a `wrap_terms(markdown_str)` decorator applied to every `st.markdown` call.

---

### 3.2 — CROSS-T2: Metric-presence consistency (8 pairs, 17 issues)

The headline metrics (`OOS Sharpe`, `Max Drawdown`, `Annualized Return`, `Win Rate`, `Turnover`) are present-or-absent inconsistently across pages, and the numbers sometimes disagree between sections (e.g. Story headline Sharpe ≠ Cross-Period Full OOS Sharpe).

Affects: every pair except `indpro_spy`.

Representative:
- *(ted_spliced_spy Story)* "Headline OOS Sharpe = +1.19, but Cross-Period Consistency Full OOS Sharpe = -0.28. These cannot both be true with the same definition."
- *(dff_ted_spy Evidence)* "Which strategy? and it said it used simplified sign(signal)*return — then is it simply returns not sharpe?"

**Template fix.** **Single-source-of-truth metric rendering.** The Story KPI tile, Strategy headline, Cross-Period Sharpe, and Methodology summary table must all read from `winner_summary.json` (and the same OOS window). Build a `render_kpi_block(winner)` component that the four pages all import — no per-page recomputation.

---

### 3.3 — CROSS-T3: Scale / units / dollar-decimal alignment (5 pairs, 17 issues)

Y-axes shown in wrong scale (missing two zeros, inverted axis, raw vs ratio), narrative quoting one unit while chart shows another, decimals rounded inconsistently within the same page.

Affects: `dff_ted_spy, hy_ig_v2_spy, indpro_xlp, permit_spy, vix_vix3m_spy`.

Representative:
- *(hy_ig_v2_spy Story)* "25 years of credit spreads vs S&P 500 圖，左邊Y-axis 係 inverted & 單位欠左2個零" (Y-axis inverted, missing 2 zeros).
- *(ted_spliced_spy Strategy)* "Y-axis values reaching −600,000 are economically impossible for a 21-day rate of change. Data scaling bug."

**Template fix.** Add a **VIZ-UNIT linter** to `scripts/generate_charts_*`: assert per-chart that the y-axis range matches expected units (e.g. `percent: |y| < 100`, `ratio: 0 < y < 10`, `bps: |y| < 5000`). This is the same defect class as the Wave-2A 100× bug; the linter is what made `hy_ig_spread_pct` rename work — extend coverage.

---

### 3.4 — CROSS-T4: Cross-Period Consistency contradictions / data gaps (5 pairs, 8 issues)

Sub-period Sharpe, Rolling Correlation, Rolling Sharpe, Rolling Granger charts: narrative says one thing, chart shows another; "No data" placeholders shown even when data exists; thresholds and break-date flags misaligned with statistical significance.

Affects: `dff_ted_spy, indpro_spy, indpro_xlp, permit_spy, ted_spliced_spy`.

Representative:
- *(permit_spy Evidence-L1)* "Narrative contradictions exist across all 4 charts (sub-period Sharpe / Rolling Correlation / Rolling Sharpe / Rolling Granger). Text consistently describes pattern X but charts show pattern Y."
- *(indpro_xlp Evidence)* "Cross-period consistency chart shows limited data coverage, most historical episodes marked as 'No data'. May give impression of weak validation."

**Template fix.** Two parts. (a) The narrative under each cross-period chart should be **mechanically generated from the chart's data**, not hand-written — eliminates text-vs-chart drift. (b) "No data" placeholders should *only* fire when the underlying CSV is genuinely missing — currently fires when narrative was authored before the chart shipped. This connects to the **VIZ-CP1-G** rule already added today.

---

### 3.5 — CROSS-T5: Regime / quartile labelling (6 pairs, 7 issues)

Q1–Q4 labels confuse non-technical readers; quartile colours sometimes inverted (Q1 green vs Q4 green inconsistent); HMM stress-state legend missing; "regime" used without explanation.

Affects: `hy_ig_v2_spy, indpro_xlp, permit_spy, sofr_ted_spy, umcsent_xlv, vix_vix3m_spy`.

Representative:
- *(indpro_xlp Evidence)* "The quartile labels (Q1–Q4) are not intuitive without context."
- *(umcsent_xlv Evidence)* "For 'Signal Distribution Analysis' section's box plots, please indicate 1st Quartile, 3rd Quartile instead of Q1 and Q3."

**Template fix.** Standard **quartile-label decorator** in `viz.py`: every quartile chart renders with `Q1 (lowest …)`, `Q4 (highest …)` and a hover-tooltip explaining what the variable is. Colour mapping enforced in `color_palette_registry.json` (already exists — extend with `quartile_v1`).

---

### 3.6 — CROSS-T6: Narrative ↔ chart alignment & per-pair contamination (4 pairs, 11 issues)

The text on a page mentions facts that the chart doesn't show, references another pair's instrument, mixes formats across paragraphs of the same page, or duplicates content from another pair.

Affects: `hy_ig_v2_spy, indpro_xlp, permit_spy, umcsent_xlv`.

Representative:
- *(indpro_xlp Story)* "The chart description mentions a dual-axis view with IP YoY growth (left, red) and XLP price (right, blue). However, the IP YoY growth (red line) is not visible in the chart."
- *(permit_spy Story)* "Building Permits YoY Growth vs S&P 500 graph uses YoY, narrative in How the Signal Performed in Past Crises uses different format."
- *(umcsent_xlv Story)* "Please verify and update the number of households participating in the survey. Should state approximately 1,000 households, not 500."

**Template fix.** Two existing rules cover this but aren't being enforced consistently: **GATE-NR** (narrative instrument-reference check, Quincy) needs to extend to numeric facts cited in prose; **APP-DIR1** (3-way direction triangulation) handles direction but not magnitude. A new **GATE-NF (Narrative-Facts)** that grep-checks all numeric claims in the markdown body against the source data would close this.

---

### 3.7 — CROSS-T7: Missing data / "chart pending" placeholders shown (5 pairs, 13 issues)

Charts rendered as "pending" or "no data" even when data exists; or chart placeholders not removed after retro-apply.

Affects: `dff_ted_spy, hy_ig_v2_spy, indpro_spy, permit_spy, sofr_ted_spy`.

Representative:
- *(sofr_ted_spy Strategy)* "Chart missing"
- *(dff_ted_spy Evidence)* "Looks missing data?"

**Template fix.** This is the same class as the GATE-32 / VIZ-CP1-G failure mode from earlier today: placeholder text is too permissive and lets pre-shipped state appear in production. Generalise GATE-32: any `st.info("...pending...")` placeholder in a production-ready section is a FAIL, not a WARN.

---

### 3.8 — CROSS-T8: Axis labels / titles / captions (4 pairs, 8 issues)

Duplicate year ticks ("2000" appearing twice), legends overlapping captions, missing axis titles, captions describing wrong colour.

Affects: `hy_ig_v2_spy, indpro_xlp, permit_spy, ted_spliced_spy`.

**Template fix.** Extend **VIZ-IC1** (the pre-save lint already in `viz.py`) with: (a) reject duplicate tick labels, (b) reject legend bounding boxes overlapping plot area, (c) caption-vs-trace colour assertion.

---

### 3.9 — CROSS-T9: Trade log / Strategy execution panels (3 pairs, 6 issues)

Position Adjustment Panel binary when narrative implies gradual; trade-log CSV missing diagnostic columns; trade-log column dictionary unclear.

Affects: `hy_ig_v2_spy, indpro_xlp, permit_spy`.

**Template fix.** Standard **trade-log schema** with required diagnostic columns (raw signal value, threshold comparison, regime tag) per APP-TL1 — already partially specified; needs strict producer validation.

---

### 3.10 — CROSS-T10: Decimal rounding inconsistency (3 pairs, 5 issues)

Same number rendered with different decimal precision in different parts of the same page.

Affects: `indpro_spy, indpro_xlp, permit_spy`.

**Template fix.** Single rounding helper in `components/fmt.py` (`fmt_pct(x, dp=1)`, `fmt_ratio(x, dp=2)`, `fmt_bps(x, dp=0)`) and a lint rule that any inline `{x:.Nf}` outside that helper is a FAIL.

---

## 4. Pair-specific issues (LOCAL — fix per pair)

These don't fit any cross-pair theme — single-pair authoring drift, content errors, or pair-unique features.

### 4.1 — `permit_spy` (8 pair-local issues — heaviest pair)
- Story sub-section "How to navigate the four pages" was skipped (drop or add consistently — actually a *cross-pair* template question).
- Story opening paragraph references another indicator unnecessarily.
- Evidence-L1: orange break-date flag rendered around 2001 despite p-value showing no significant break (chart-vs-test contradiction).
- Evidence-L1: 4 charts with narrative contradictions (cross-period theme).
- Evidence-L2: text claims effect peaks at 3-6 months, chart shows peak at 12 months.

### 4.2 — `umcsent_xlv` (8 pair-local issues)
- "Please avoid all abbreviations or define on first use" — across all sections.
- Story "Where This Fits in the Portal": remove the first paragraph and keep only the "how to read" portion.
- Verify economic claim: "higher sentiment = lower risk premium" — confirm.
- Rename "Nuance and Limits" → "Key Findings".
- Plain-English numeric: ~1,000 households (not 500).

### 4.3 — `sofr_ted_spy` (6 pair-local issues)
- Story: OOS window stated 2015-01–2025-12 but Methodology says 2023 onwards — internal contradiction.
- Story: explicit "DFF" used without expansion.
- Story: legends and chart overlap.
- Strategy: signal Long/Cash description doesn't match downstream chart.

### 4.4 — `hy_ig_v2_spy` (6 pair-local issues)
- Strategy-execution panel: missing "What this means (in plain English)" column on the trigger table; Available/Pending labels unexplained.
- Glossary: Quantile definition too brief.
- Evidence: signal labels on Negative-Corrections-Strengthen chart were changed between versions — needs sync.
- Some analyses (annualised SPX returns by quartile, pre-whitened CCF) removed from current version — confirm intent.

### 4.5 — `indpro_xlp` (2 pair-local issues)
- Story chart legend "INDPRO Index" and "XLP Price ($)" overlaps annotation/footnote.
- Strategy: "Probability Engine Panel" name misleading since the chart shows raw `indpro_accel` against threshold — relabel or restructure.

### 4.6 — `indpro_spy` (2 pair-local issues)
- Story: index name not standardised (INDPRO Index vs Industrial Production vs INDPRO) — pick one.
- Methodology: "who are the team members related to our study" — content request.

### 4.7 — `ted_spliced_spy` (2 pair-local issues)
- Strategy: tournament ranks 1-6 have identical KPIs across different threshold parameters (data bug — likely threshold not actually varying).
- Default heuristic (0.5) used because actual threshold is on legacy schema — known migration debt (BL-LEGACY-WINNER-SUMMARY-SHAPE).

### 4.8 — `dff_ted_spy` (2 pair-local issues)
- Evidence: difference between ROC (rate of change) and MOM (momentum) clarified later in Methodology but should be inline at first use.
- Strategy: "can't load" (likely the cross-period or schema bug class).

### 4.9 — `vix_vix3m_spy` (2 pair-local issues)
- Story: VIX term structure explanation can be richer ("there is more than 1 VIX: 30-day, 60-day, 3-month, …").
- Evidence: requests longer explanation with more detail.

---

## 5. Prioritised action plan

### Tier A — Template fixes (one fix lands across all 9 active pairs + future pairs)

| Priority | Theme | Effort | Owner |
|---|---|---|---|
| **A1** | CROSS-T1 ELI5: automatic first-use glossary tooltip injection in `page_templates.py` | M | Ace |
| **A2** | CROSS-T2 metric-presence: single-source KPI block read from `winner_summary.json` | M | Ace |
| **A3** | CROSS-T3 scale/units: VIZ-UNIT linter (per-chart type, expected-range assertion) | M | Vera |
| **A4** | CROSS-T6 narrative facts: GATE-NF — grep numeric claims in prose against source data | M | Quincy |
| **A5** | CROSS-T5 quartile labelling: decorator + extended palette | S | Vera |
| **A6** | CROSS-T8 axis sanity: extend VIZ-IC1 with duplicate-tick, legend-overlap, caption-colour rules | S | Vera |
| **A7** | CROSS-T10 rounding: centralised `fmt` helper + lint | S | Ace |
| **A8** | CROSS-T4 cross-period narrative: data-driven captions (auto-generated) | L | Ray + Vera |
| **A9** | CROSS-T7 missing-data: generalise GATE-32 to all placeholder classes | S | Quincy |
| **A10** | CROSS-T9 trade-log: producer validation of diagnostic columns | S | Evan + Ace |

### Tier B — Per-pair fixes (one PR per pair, post-template)

After Tier A lands, each pair gets a focused remediation pass with the issues listed in §4. Suggested order:

1. **`permit_spy`** first (33 issues — biggest reduction; will surface remaining template issues earliest).
2. **`umcsent_xlv`** (8 local items, abbreviations sweep).
3. **`sofr_ted_spy`** (OOS-window contradiction is data-level; needs Dana/Evan).
4. **`hy_ig_v2_spy`** (Sample pair — fix carefully since it sets benchmarks).
5. Remaining 5 pairs (each ≤2 local items).

---

## 6. Cross-cutting observations

1. **Story page is the most-flagged section (30 issues).** Narrative + chart caption alignment dominates. Tier-A4 (GATE-NF) is the highest-leverage fix here.
2. **`permit_spy` is a stress test.** Its 33 issues include 8 in Evidence-L1, 4 each in Strategy Execute/Performance/Confidence. If `permit_spy` were template-clean, the overall comment count would roughly halve.
3. **No mention of HMM / Local Projection / Quantile Regression / Transfer Entropy** in the comment log. These are the heavy Evidence-L2 methods we shipped for gold_copper_xli today; the reviewer hasn't encountered them yet on pairs that have them. Will likely generate fresh comments on next review pass.
4. **The new gold_copper_xli pair is NOT in this log** (review was 2026-04-15..17; pair shipped 2026-05-26). Today's fixes already pre-empted several Tier-A items (VIZ-CP1-G, GATE-32 flip, integrity gate, producer schema validation).
5. **Closed items:** all 8 already-closed items are in `hy_ig_v2_spy` — the team has been actively iterating on Sample. Pair-by-pair triage is the natural extension.

---

## 7. Tracking artefacts

- Raw issue extract: `/tmp/issues.json` (structured JSON, 104 entries).
- Cross-pair signature dump: `/tmp/cross_sigs.json` (empty — verbatim text never matched across pairs; thematic classification used instead).
- This report: `docs/dashboard_review_20260526.md`.
- Source file (not in git): `temp/Step C - Dashboard Comment log.xlsx`.

---

*Generated by Lesandro 2026-05-26 on branch `fix260526` for triage planning.*
