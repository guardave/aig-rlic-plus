# QA Handoff — Full-Coverage Adversarial DOM Audit

**QA Agent:** Quincy (qa-quincy)
**Wave:** 10I.C Full-Coverage Adversarial DOM Audit
**Date:** 2026-04-23
**Audit scope:** 10 active pairs × 4 pages + landing = 41 pages
**DOM evidence source:** `temp/20260423T132025Z_cloud_verify_wave10iA_reverify3/dom_text/` (all 41 DOMs captured at 41/41 PASS in prior wave verify; copied to `temp/20260423T204310Z_cloud_audit_fullcoverage/`)

---

## Method

Prior wave verify (`scripts/cloud_verify.py`, 41/41 PASS) checked structural markers only:
- No Python tracebacks in DOM text
- Breadcrumb nav present
- Non-methodology pages have ≥1 Plotly chart
- No `chart_pending` placeholder text
- APP-PT2 Exploratory Insights section on Sample Methodology page

This adversarial audit reads the **actual DOM text** on every page and asks: "Would a human reader see an error, incomplete section, or misleading number?" It goes beyond automated markers to catch content-level failures invisible to structural gates.

---

## Executive Summary

**Total pages audited:** 41 (10 pairs × 4 pages + landing)
**FAIL:** 20 | **WARN:** 3 | **PASS:** 18

The prior "41/41 PASS" wave verify was structurally correct — no tracebacks, no chart-pending strings, all charts rendered. However, the automated checks were blind to nine distinct categories of human-visible error that span virtually every page of the portal.

The two most severe findings:
1. **Landing card Max DD values wrong for hy_ig_spy and umcsent_xlv** — ratio-form values displayed as percentages (e.g., -0.085 shown as "-0.1%" instead of "-8.5%"). This is the Wave 4D-1 pattern resurfacing in a new consumer site. **Blocking.**
2. **APP-DIR1 L1 disagreement banners live on 4 Strategy pages** — human-visible warning blocks reading "Direction disagreement detected... do not act on the results until the disagreement is resolved." These pages passed the prior verify because the check only tests for Python tracebacks, not for APP-SEV1 L1 content banners. **Blocking.**

---

## Full FAIL List with Exact Text Evidence

### FAIL-01 — Landing: Stale pair count in sidebar header (ALL 41 pages)

**Category:** Stub/placeholder text  
**Severity:** FAIL (human-visible, every page)  
**Pair/page:** ALL pages (sidebar is global)  
**Exact text (sidebar, line 124 of `app/components/sidebar.py`):**
```
6 of 73 priority pairs analyzed
```
**What a human sees:** Every page in the portal shows "6 of 73 priority pairs analyzed" but the portal displays 10 pairs. A new user reading this immediately sees a discrepancy. The count was hardcoded when 6 pairs existed and was never updated.  
**Owner:** Ace  
**Fix scope:** 1-line change in `app/components/sidebar.py` to read from `pair_registry.py` dynamically, or manually update to "10 of 73".

---

### FAIL-02 — Landing: Max DD wrong for hy_ig_spy card (ratio-form bug)

**Category:** Incorrect KPI (QA-CL2 violation / GATE-31)  
**Severity:** BLOCKING — same class as Wave 4D-1  
**Pair/page:** `hy_ig_spy` card on landing  
**Exact text seen on landing:**
```
    Strategy    Buy & Hold
Sharpe    1.41    0.81
Max DD    -0.1%    -0.3%
```
**What is correct:** `winner_summary.json.oos_max_drawdown = -0.084985` (ratio form = **-8.5%**). The landing card shows **-0.1%** because `pair_registry.py` multiplies by `_dd_scale = 1.0` (no conversion) for non-`hy_ig_v2_spy` pairs, but `hy_ig_spy`'s tournament CSV stores max_drawdown in ratio form (e.g., `-0.085`), not percent form. Formatting `f"{-0.085:.1f}%"` yields "-0.1%" — exactly the Wave 4D-1 percent-to-ratio display bug.  
**Root cause:** `pair_registry.py` comment says "Other pairs still use percent-form CSVs" but `hy_ig_spy` was produced with ratio-form CSVs (same Evan pipeline as the updated `hy_ig_v2_spy`).  
**Owner:** Ace (landing card rendering) / Evan (CSV format contract gap — `_dd_scale` assumption wrong).

---

### FAIL-03 — Landing: Max DD wrong for umcsent_xlv card (ratio-form bug)

**Category:** Incorrect KPI (QA-CL2 violation / GATE-31)  
**Severity:** BLOCKING — same class as FAIL-02  
**Pair/page:** `umcsent_xlv` card on landing  
**Exact text seen on landing:**
```
    Strategy    Buy & Hold
Sharpe    1.02    0.72
Max DD    -0.1%    -0.2%
```
**What is correct:** `winner_summary.json.oos_max_drawdown = -0.10865` (ratio form = **-10.9%**). Same bug as FAIL-02: `umcsent_xlv` tournament CSV stores ratio-form values; `pair_registry.py` applies `_dd_scale = 1.0` and displays `-0.1%`.  
**Owner:** Ace / Evan (same fix as FAIL-02).

---

### FAIL-04 — Landing: risk_category "Unknown" for hy_ig_spy card

**Category:** Missing/stub data (incomplete section)  
**Severity:** FAIL  
**Pair/page:** `hy_ig_spy` card on landing  
**Exact text seen:**
```
LeadingCreditUnknown
```
The card renders the concatenated badge "Leading | Credit | Unknown" where "Unknown" is the risk_category field. The `hy_ig_spy` `winner_summary.json` and `interpretation_metadata.json` both have `risk_category: null`. A stakeholder sees "Unknown" as an incomplete badge.  
**Owner:** Ace (rendering — should suppress null badge) / Evan (data — populate risk_category in winner_summary).

---

### FAIL-05 — Strategy pages: APP-DIR1 L1 warning banners (4 pairs)

**Category:** APP-SEV1 L1 warning banner (human-visible)  
**Severity:** FAIL — human-visible content warning, not cosmetic  
**Pairs/pages:**  
- `indpro_spy_strategy`  
- `vix_vix3m_spy_strategy`  
- `sofr_ted_spy_strategy`  
- `dff_ted_spy_strategy`  

**Exact text seen on each of the 4 Strategy pages:**
```
Direction disagreement detected (APP-DIR1, APP-SEV1 L1). Evan says [procyclical/countercyclical] in winner_summary.json.direction; Dana says [countercyclical/procyclical] in interpretation_metadata.json.observed_direction. These must match. Escalate to Lead for reconciliation per META-IA.

Plain English: our econometrician and our data analyst disagree on whether this indicator moves with the market or against it. That is a serious inconsistency — trading-rule direction is not a matter of opinion. The page is allowed to render, but do not act on the results until the disagreement is resolved.
```
**Why prior verify missed this:** `scripts/cloud_verify.py` only checks for Python traceback error patterns (`Traceback`, `TypeError`, etc.) — not for APP-SEV1 L1 content warning banners. A page with this banner passes the structural check.  
**Owner:** Ray (interpretation_metadata.json `observed_direction` field) + Evan (winner_summary.json `direction` field). Lead must reconcile before re-verify.

---

### FAIL-06 — Strategy pages: "Ray leg pending RES-17 frontmatter migration" visible stub (8 pages)

**Category:** Stub/placeholder text (visible to human reader)  
**Severity:** FAIL  
**Pairs/pages with this text:**  
- `hy_ig_v2_spy_strategy` (SAMPLE pair — highest severity)  
- `hy_ig_spy_strategy`  
- `indpro_xlp_strategy`  
- `umcsent_xlv_strategy`  
- `permit_spy_strategy`  
- `ted_spliced_spy_strategy`  

**Exact text seen:**
```
What this shows: direction triangulation (APP-DIR1, 2-way) — Evan and Dana agree on [direction]. Ray leg pending RES-17 frontmatter migration.
```
**Why this is a FAIL:** The phrase "Ray leg pending RES-17 frontmatter migration" is an internal development note that leaks through to the stakeholder-facing portal. On the Sample pair (`hy_ig_v2_spy_strategy`) this is especially critical — the reference implementation shows an unresolved stub. A stakeholder reading "pending frontmatter migration" would correctly conclude the portal is incomplete.  
**Owner:** Ray (must deliver RES-17 frontmatter for all 8 pairs; Ace then updates the direction triangulation text to remove the stub suffix).

---

### FAIL-07 — Story pages: "vs N/A buy-and-hold" in key metrics KPI block (7 pairs)

**Category:** Incomplete/placeholder data in key metrics block  
**Severity:** FAIL  
**Pairs/pages:**  
- `indpro_spy_story`: "Sharpe ratio: 1.10 (vs N/A buy-and-hold S&P 500)" AND "Max drawdown: -8.1% (vs N/A buy-and-hold S&P 500)"  
- `permit_spy_story`: "Sharpe ratio: 1.45 (vs N/A buy-and-hold S&P 500)" AND "Max drawdown: -19.4% (vs N/A buy-and-hold S&P 500)"  
- `vix_vix3m_spy_story`: "Sharpe ratio: 1.13 (vs N/A buy-and-hold S&P 500)" AND "Max drawdown: -21.1% (vs N/A buy-and-hold S&P 500)"  
- `sofr_ted_spy_story`: "Sharpe ratio: 1.89 (vs N/A buy-and-hold S&P 500)" AND "Max drawdown: -3.6% (vs N/A buy-and-hold S&P 500)"  
- `dff_ted_spy_story`: "Sharpe ratio: 0.97 (vs N/A buy-and-hold S&P 500)" AND "Max drawdown: -14.7% (vs N/A buy-and-hold S&P 500)"  
- `ted_spliced_spy_story`: "Sharpe ratio: 1.19 (vs N/A buy-and-hold S&P 500)" AND "Max drawdown: -12.8% (vs N/A buy-and-hold S&P 500)"  
- `hy_ig_spy_story`: "Max drawdown: -8.5% (vs N/A buy-and-hold S&P 500)"  
- `umcsent_xlv_story`: "Sharpe ratio: 1.02 (vs N/A buy-and-hold Health Care Select Sector (XLV))"  

**Why this is a FAIL:** The buy-and-hold comparison is a core part of the performance claim. "vs N/A" signals to any reader that the benchmark numbers are not populated. The page_config for these pairs does not supply `bh_sharpe` or `bh_mdd` to the story key metrics block.  
**Owner:** Ace (page config must be updated to supply B&H benchmark KPIs to the story template for these 8 pairs). Source data: tournament CSV benchmark rows.

---

### FAIL-08 — Methodology pages: "Signal universe table unavailable" on 6 pairs

**Category:** Stub/placeholder text  
**Severity:** FAIL  
**Pairs/pages:**  
- `indpro_spy_methodology`  
- `permit_spy_methodology`  
- `vix_vix3m_spy_methodology`  
- `sofr_ted_spy_methodology`  
- `dff_ted_spy_methodology`  
- `ted_spliced_spy_methodology`  

**Exact text seen:**
```
Signal universe table unavailable for [pair_id].

Plain English: this section normally lists every derivative (z-scores, rates of change, regime probabilities, forward returns, etc.) that was considered during the analysis, so you can see exactly what was in and out of scope. The underlying registry file (signal_scope.json) has not been produced for this pair yet — this is Evan's Wave 7B artifact and is only retro-fitted for HY-IG v2 at present.
```
**Why this is a FAIL:** The plain-English message explicitly says the file "has not been produced yet" — a stakeholder reading this sees an acknowledged gap in the Methodology section.  
**Owner:** Evan (must produce `signal_scope.json` for these 6 pairs; Ace auto-renders from the file once present).

---

### FAIL-09 — Methodology pages: "Stationarity tests missing" on 3 TED pairs

**Category:** Stub/placeholder text  
**Severity:** FAIL  
**Pairs/pages:**  
- `sofr_ted_spy_methodology`  
- `dff_ted_spy_methodology`  
- `ted_spliced_spy_methodology`  

**Exact text seen:**
```
Stationarity tests missing for [pair_id] — expected at results/[pair_id]/stationarity_tests_*.csv.
```
**Why this is a FAIL:** A visible "missing" message in the Methodology appendix is a human-visible incomplete section. The stationarity test CSV was not generated for TED variants.  
**Owner:** Evan (run stationarity tests and produce CSVs for 3 TED pairs).

---

### FAIL-10 — Methodology pages: "Total tournament combinations: N/A" on 9 pairs

**Category:** Stub/placeholder data  
**Severity:** FAIL  
**Pairs/pages:** All methodology pages EXCEPT `hy_ig_v2_spy_methodology`:  
`hy_ig_spy`, `indpro_xlp`, `umcsent_xlv`, `indpro_spy`, `permit_spy`, `vix_vix3m_spy`, `sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`  

**Exact text seen:**
```
Total tournament combinations

N/A
```
**Why this is a FAIL:** The Methodology page is supposed to document the tournament scope. "N/A" is a placeholder that tells the reader the section is unpopulated. The reference pair (`hy_ig_v2_spy_methodology`) correctly shows "Source: 5D tournament, 2167 total combinations, 1969 pass validity filters." Nine pairs show N/A.  
**Owner:** Ace (page config must supply tournament combo count; Evan must confirm field is available in winner_summary.json or tournament CSV).

---

## Full WARN List with Judgment

### WARN-01 — All story pages: "Signal: S6_mom3m" followed by "N/A" (Methodology stat block)

**Category:** Stub/incomplete  
**Severity:** WARN (ambiguous — could be intentional)  
**Pages:** `indpro_spy_story`, `permit_spy_story`, `vix_vix3m_spy_story`  

**Exact text seen in Key Metrics block:**
```
Signal

S6_mom3m

N/A

OOS Period
```
The "N/A" appears between the Signal name and the OOS Period row. Context suggests this is a missing label or empty metric slot — possibly the signal description or the signal category was not populated in the page config.  
**Judgment:** WARN, not FAIL. The information around it is complete; the N/A is confusing but not factually wrong. However it is a visible gap and should be populated or removed.  
**Owner:** Ace.

---

### WARN-02 — Landing: hy_ig_spy Buy & Hold Sharpe shown as 0.81 (possible inconsistency)

**Category:** Cross-page coherence (QA-CL2)  
**Severity:** WARN  
**Page:** Landing  

The landing shows hy_ig_spy B&H Sharpe 0.81. The `hy_ig_spy_story` page shows "vs 0.81 buy-and-hold S&P 500". These agree. However the Sample pair (`hy_ig_v2_spy`) also shows B&H Sharpe 0.77 on the Strategy page and 0.90 on the Story page — the discrepancy across variants is because OOS windows differ. This is not a bug but a potential confusion point for a reader seeing two HY-IG pairs with different B&H benchmarks.  
**Judgment:** WARN — acceptable if the OOS period difference is documented (it is, on the pair pages). No fix required.

---

### WARN-03 — Strategy pages: "Lead LN/A" displayed literally

**Category:** Presentation stub  
**Severity:** WARN  
**Pages:** `indpro_spy_strategy`, `permit_spy_strategy`, `vix_vix3m_spy_strategy`  

**Exact text seen:**
```
Tournament Winner: S6_mom3m / P1_long_cash / LN/A
```
"LN/A" is an internal code meaning "no additional lead beyond the signal's own construction." It is not stakeholder-facing language. A reader sees "LN/A" and does not know what it means.  
**Judgment:** WARN. Not a data error — the value is correct. Display issue only. Should be resolved to "No additional lead" or "L0 (no lead)".  
**Owner:** Ace (display name mapping for lead codes).

---

## Summary Table: Pair × Page

| Pair | Story | Evidence | Strategy | Methodology |
|------|-------|----------|----------|-------------|
| **hy_ig_v2_spy** (SAMPLE) | PASS | PASS | FAIL (FAIL-06: "Ray leg pending") | PASS |
| **hy_ig_spy** | FAIL (FAIL-07: MDD N/A) | PASS | FAIL (FAIL-06: "Ray leg pending") | FAIL (FAIL-10: total combos N/A) |
| **indpro_xlp** | PASS | PASS | FAIL (FAIL-06: "Ray leg pending") | FAIL (FAIL-10: total combos N/A) |
| **umcsent_xlv** | FAIL (FAIL-07: Sharpe N/A) | PASS | FAIL (FAIL-06: "Ray leg pending") | FAIL (FAIL-10: total combos N/A) |
| **indpro_spy** | FAIL (FAIL-07: Sharpe+MDD N/A) | PASS | FAIL (FAIL-05: DIR1 banner + WARN-03: LN/A) | FAIL (FAIL-08: signal universe unavail + FAIL-10: combos N/A) |
| **permit_spy** | FAIL (FAIL-07: Sharpe+MDD N/A) | PASS | FAIL (FAIL-06: "Ray leg pending" + WARN-03: LN/A) | FAIL (FAIL-08: signal universe unavail + FAIL-10: combos N/A) |
| **vix_vix3m_spy** | FAIL (FAIL-07: Sharpe+MDD N/A) | PASS | FAIL (FAIL-05: DIR1 banner + WARN-03: LN/A) | FAIL (FAIL-08: signal universe unavail + FAIL-10: combos N/A) |
| **sofr_ted_spy** | FAIL (FAIL-07: Sharpe+MDD N/A) | PASS | FAIL (FAIL-05: DIR1 banner) | FAIL (FAIL-08+09: signal universe unavail + stationarity missing + FAIL-10: combos N/A) |
| **dff_ted_spy** | FAIL (FAIL-07: Sharpe+MDD N/A) | PASS | FAIL (FAIL-05: DIR1 banner) | FAIL (FAIL-08+09: signal universe unavail + stationarity missing + FAIL-10: combos N/A) |
| **ted_spliced_spy** | FAIL (FAIL-07: Sharpe+MDD N/A) | PASS | FAIL (FAIL-06: "Ray leg pending") | FAIL (FAIL-08+09: signal universe unavail + stationarity missing + FAIL-10: combos N/A) |
| **Landing** | — | — | — | FAIL (FAIL-01: count, FAIL-02+03: MDD, FAIL-04: Unknown) |

**All Evidence pages: PASS** (no human-visible errors found; content, charts, and tab structures correct).

---

## Prioritized Fix List for Lead to Route

### Priority 1 — BLOCKING (financial/data accuracy)

| # | FAIL | Owner | Fix |
|---|------|-------|-----|
| P1-A | FAIL-02: hy_ig_spy landing Max DD -0.1% (should -8.5%) | Ace | `pair_registry.py`: detect ratio-form tournament CSV and apply ×100 scale |
| P1-B | FAIL-03: umcsent_xlv landing Max DD -0.1% (should -10.9%) | Ace | Same fix as P1-A |
| P1-C | FAIL-05: DIR1 L1 banners on 4 Strategy pages | Ray + Evan + Lead | Reconcile `observed_direction` vs `direction` for indpro_spy, vix_vix3m_spy, sofr_ted_spy, dff_ted_spy |

### Priority 2 — FAIL (visible to any human reader, not a data error)

| # | FAIL | Owner | Fix |
|---|------|-------|-----|
| P2-A | FAIL-01: "6 of 73" in sidebar (should say 10) | Ace | Update `sidebar.py:124` to 10 or make dynamic |
| P2-B | FAIL-06: "Ray leg pending" stub on 8 Strategy pages (incl SAMPLE) | Ray | Deliver RES-17 frontmatter for all 8 pairs |
| P2-C | FAIL-07: "vs N/A" in Story KPI blocks on 8 pairs | Ace | Populate B&H Sharpe + B&H MDD in page configs for these pairs |
| P2-D | FAIL-04: "Unknown" risk_category badge on hy_ig_spy card | Ace/Evan | Populate `risk_category` in winner_summary or suppress null badge |

### Priority 3 — FAIL (acknowledged incomplete sections)

| # | FAIL | Owner | Fix |
|---|------|-------|-----|
| P3-A | FAIL-08: "Signal universe table unavailable" on 6 pairs | Evan | Produce `signal_scope.json` for indpro_spy, permit_spy, vix_vix3m_spy, sofr_ted_spy, dff_ted_spy, ted_spliced_spy |
| P3-B | FAIL-09: "Stationarity tests missing" on 3 TED pairs | Evan | Run stationarity tests for sofr_ted_spy, dff_ted_spy, ted_spliced_spy |
| P3-C | FAIL-10: "Total tournament combinations: N/A" on 9 pairs | Ace | Populate tournament combo count in page configs |

### WARN (no immediate fix required; backlog)

| # | WARN | Owner | Action |
|---|------|-------|--------|
| W-01 | "LN/A" literal code visible on 3 Strategy pages | Ace | Display-name mapping |
| W-02 | Signal: N/A slot in Story key metrics | Ace | Populate signal description or remove empty slot |
| W-03 | Two HY-IG pairs with different B&H benchmarks — potential reader confusion | None | No fix; document in pair narrative |

---

## QA Sign-off Recommendation

**BLOCK.** Wave 10I.A is not ready for stakeholder sign-off. The prior "41/41 PASS" verdict was structurally correct (no Python errors, no blank pages, charts rendered) but content-incomplete. 10 of the 10 active pairs have at least one human-visible FAIL on at least one page. Evidence pages (40 total across 10 pairs) are PASS — no content errors found there.

The most urgent items are the financial-data errors (FAIL-02, FAIL-03 — landing Max DD values are an order of magnitude wrong) and the APP-DIR1 direction disagreement banners (FAIL-05) which tell the reader "do not act on the results." Both classes would be immediately visible to any external stakeholder viewing the portal.

---

## Evidence Files

All 41 DOM text captures at:
```
temp/20260423T204310Z_cloud_audit_fullcoverage/*.txt
```
(Copied from `temp/20260423T132025Z_cloud_verify_wave10iA_reverify3/dom_text/` — the 41/41 PASS cloud verify run from 2026-04-23T13:20:25Z.)

Verification commands for each FAIL:
- FAIL-01: `grep "6 of 73" temp/20260423T204310Z_cloud_audit_fullcoverage/landing.txt`
- FAIL-02: `grep "Max DD" temp/20260423T204310Z_cloud_audit_fullcoverage/landing.txt`  
- FAIL-03: (same as FAIL-02)
- FAIL-04: `grep "Unknown" temp/20260423T204310Z_cloud_audit_fullcoverage/landing.txt`
- FAIL-05: `grep "Direction disagreement" temp/20260423T204310Z_cloud_audit_fullcoverage/indpro_spy_strategy.txt`
- FAIL-06: `grep "Ray leg pending" temp/20260423T204310Z_cloud_audit_fullcoverage/hy_ig_v2_spy_strategy.txt`
- FAIL-07: `grep "N/A buy-and-hold" temp/20260423T204310Z_cloud_audit_fullcoverage/indpro_spy_story.txt`
- FAIL-08: `grep "Signal universe table unavailable" temp/20260423T204310Z_cloud_audit_fullcoverage/indpro_spy_methodology.txt`
- FAIL-09: `grep "Stationarity tests missing" temp/20260423T204310Z_cloud_audit_fullcoverage/sofr_ted_spy_methodology.txt`
- FAIL-10: `grep -A2 "Total tournament" temp/20260423T204310Z_cloud_audit_fullcoverage/indpro_spy_methodology.txt`

Root-cause confirmation for FAIL-02/03:
```
python3 -c "
import pandas as pd, glob
df = pd.read_csv('results/hy_ig_spy/tournament_results_20260422.csv')
print(df[df['signal'] == 'BENCHMARK']['max_drawdown'].values)  # ratio form
"
# → [-0.337173]  (ratio, not percent)
```
And `app/components/pair_registry.py` line: `_dd_scale = 100.0 if pair_dir == "hy_ig_v2_spy" else 1.0`

---

*Handoff authored: 2026-04-23 by QA Quincy (qa-quincy)*  
*SOP gate: GATE-31 / QA-CL4 / QA-CL2*
