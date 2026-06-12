# QA Verification — busloans_spy (Pair #19, Mode 1) — 2026-06-12, Quincy

Branch: `fix260612_busloans_spy` @ `bda7eb1` (final assertion run includes Ray's mid-flight prose commit `bda7eb1` — front-loaded MANUAL_USE_MD disclosure confirmed in rendered Strategy DOM).
Evidence folder: `temp/260612_qa_busloans/` (dom_text ×8 pages, full-page screenshots ×8, results.json, qa_dom_verify.py). Smoke logs: `app/_smoke_tests/loader_*_20260612.log`, `/tmp/clean_checkout_busloans_spy/app/_smoke_tests/*.log`.

## Summary

Total checks: 38 | PASS: 34 | PASS-with-note: 3 | FAIL: 1 (blocking) | + 1 waived FAIL (DPS-PRE1, Lead waiver)

**Verdict: NOT READY** — sole blocking defect QA-1 (landing card KPIs render as "—" / "Valid 0 / 0"; owner Ace). Everything else green. Narrow re-verify (landing page only) after fix.

## Gate results

| # | Gate | Command | Result |
|---|------|---------|--------|
| 1 | GATE-DPS1 `validate_pair_completeness --pair busloans_spy` | 137 PASS, 0 WARN, 1 FAIL | **PASS-with-waiver** — sole FAIL = DPS-PRE1 (final exam never run; status `found_in_search`). **Lead waiver this wave** per dispatch brief: DPS-FE2 found_in_search KPI routing + `evidence_status.plain_english` disclosure is the compensating control; ECON-FE1 final exam documented as future work in `evidence_status.next_step`. Waiver to be logged by Lead per QA Override Log convention. No other FAIL. |
| 2 | META-CMP T1.1 `validate_all_schemas` | pairs=9 pass=33 fail=0 skip=3 | **PASS** |
| 3 | META-CMP T1.3 `lint_filename_convention` | 397 json checked, violations=0 | **PASS** |
| 4 | META-CMP T2 `lint_chart_completeness` | 9 pairs, refs=117, failures=0 (busloans 17/17) | **PASS** |
| 5 | META-CMP `smoke_loader --all` | 9 pairs, total_failures=0 (busloans 21/21) | **PASS** |
| 6 | GATE-29 clean checkout (`git clone --depth 1` → /tmp/clean_checkout_busloans_spy) | smoke_loader busloans 21/21 passes=21 failures=0; smoke_schema_consumers passes=5 failures=0 | **PASS** — no gitignore-excluded file needed by pages. `git ls-files results/busloans_spy/*.parquet` → `signals_20260612.parquet` + `core_models_20260612/hmm_states.parquet` tracked (GATE-29 parquet check PASS; data-stage parquets local-only by design, pages read CSV/JSON). |
| 7 | GATE-DP1 dual-panel preflight (4 history_zoom JSONs) | 0 failures | **PASS** |
| 8 | GATE-VIZ-NBER2 episode-aware shading preflight | 0 FAIL / 0 WARN (dotcom/gfc/covid shaded; inflation_2022 clean) | **PASS** |
| 9 | GATE-27 perceptual PNG preflight | 19 `_perceptual_check_*.png` committed for busloans | **PASS** |

## Local rendered-DOM verification (LEAD-DOM1) — local Streamlit :8601, headless Chromium

Pages captured: landing, busloans ×4, gold_copper_xli_strategy (regression), hy_ig_v2_spy strategy+story (frozen Sample).

| Page | Errors/Tracebacks | Stubs/pending | Plotly count | Breadcrumb | Verdict |
|------|-------------------|---------------|--------------|------------|---------|
| landing | 0 | 0 | n/a | n/a | **FAIL (QA-1)** — see defects |
| busloans story | 0 | 0 | 6 (≥2 req) | ✓ | PASS |
| busloans evidence | 0 | 0 | 7 (≥7 req), 7 DISTINCT titles | ✓ | PASS |
| busloans strategy | 0 | 0 | 12 (≥4 req) | ✓ | PASS |
| busloans methodology | 0 | 0 | text page | ✓ | PASS |
| gold_copper_xli strategy | 0 | 0 | 14 | ✓ | PASS (no FE2 leakage: 0 "Search-phase" hits) |
| hy_ig_v2_spy strategy/story (Sample) | 0 | 0 (story "pending" hits = benign glossary text) | 7/5 | ✓ | PASS (frozen, untouched, no FE2 leakage) |

Console: zero JS errors except a uniform 2× 404 resource hit on EVERY page incl. frozen Sample (pre-existing static asset, e.g. favicon — not pair-related; non-blocking note).

**Content assertions (busloans):**
- Story: "Search-phase OOS Sharpe (no holdout test yet)" KPI label ✓ (line 70); evidence-status plain-English box with "luckiest of thousands" ✓ (line 68); "Commercial & Industrial Loans (C&I Loans)" first-mention ✓; "How the Signal Performed in Past Crises" (GATE-HZE1) ✓; 4 episode zooms (dotcom/gfc/covid/inflation_2022) ✓.
- Evidence: 7 method blocks, 7 distinct chart titles (corr battery, TY Granger, pre-whitened CCF, local projections, transfer entropy, quantile reg, HMM) ✓; tournament intro "the best of those 4,396" + median "0.74 — below buy-and-hold's 0.89" disclosure ✓; downloads expander = **10 download buttons** (`stDownloadButton` testid ×10) ✓; Level 1 / Level 2 tabs ✓.
- Strategy: search-phase KPI label + st.info disclosure ✓; fragility content — bootstrap p 0.066 ×3, IS Sharpe 0.35 ✓; Confidence tab full CP set — subperiod_sharpe element, rolling-correlation chart, structural-break chart (Quandt-Andrews p=0.30) all in DOM ✓; Tournament Scatter section renders the Sharpe-distribution **histogram** ("The Median Strategy Does NOT Beat Buy & Hold… 4,396 Valid Combos") with median-0.74 annotation ✓; MANUAL_USE_MD front-loaded non-recommendation framing (Ray `bda7eb1`) ✓.
- CP2 absence: clean — `chart_skip_rolling_granger.json` + `chart_skip_rolling_sharpe_cp.json` sidecars present; **zero** "pending"/"coming soon" strings in any busloans page DOM (text + full HTML) ✓.
- Methodology: renders, OOS window 2018-02→2026-05 / 100 obs / 6,100 combos ✓.

**DPS-FE2 first-instance verdict: PASS.** found_in_search routing displays search-phase labels + window on busloans Story & Strategy KPI rows; zero leakage onto the 8 legacy pairs (regression + Sample DOMs contain 0 "Search-phase" hits); smoke --all 9/9 byte-path unaffected.

**HABIT-QA1:** I read DOM text for busloans_spy_story, busloans_spy_evidence, busloans_spy_strategy, busloans_spy_methodology (plus landing, gold_copper_xli_strategy, hy_ig_v2_spy_strategy/story). Findings: only QA-1 (landing) and notes below.

## Numeric spot-triangulation (QA-CL)

| Check | Displayed | Source | Result |
|---|---|---|---|
| Downloads row counts (4 sampled > 3 req) | Granger-by-lag 12; regime quartile 4; rolling corr 370; subperiod 4 | CSV data rows: 12 / 4 / 370 / 4 | **PASS** (4/4 exact) |
| Story/Strategy KPI row | Sharpe 1.50, DD −1.0%, window 2018-02–2026-05, B&H 0.89 / −23.9% | winner_summary.json: 1.4999, −0.0102, 2018-02-28→2026-05-31, 0.8935, −0.2393 | **PASS** |
| Landing card Sharpe vs winner_summary | "—" | 1.50 | **FAIL → QA-1** |
| QA-CL2 T1 Sharpe↔return↔vol | 1.50, 10.67%, implied vol 7.1% | oos_ann_vol 0.0711 | **PASS** |
| QA-CL2 T2 MDD↔vol | MDD 1.0% / vol 7.1% → ratio 0.14 | — | **PASS-with-note** — below [1,6] band, fully explained by mean exposure 0.25 (75% cash); consistent with disclosed min-MDD profile |
| QA-CL2 T3 turnover↔trades | 24 trades / 8.33y = 2.88/yr; annual_turnover 2.88 | invariant expects ×2 | **PASS-with-note** — turnover basis is one-way (trades/yr ≡ turnover exactly); definitional, not a bug; BL-802 schema gap |

APP-DIR1 direction triangulation: winner_summary `countercyclical` = interpretation_metadata `countercyclical` (consistent=true) = narrative frontmatter `direction_asserted: countercyclical` — **PASS**.

## Defects

| ID | Severity | Page | Finding | Root cause (reproduced) | Owner |
|----|----------|------|---------|--------------------------|-------|
| **QA-1** | **BLOCKING (GATE-31)** | Landing card busloans_spy | Card renders Sharpe "—", Max DD "—", "Valid 0 / 0" instead of 1.50/0.89, −1.0%/−23.9%, 4,396/6,100. Nature/type chips (Lagging, Credit, Min MDD) and key_finding correct. | `app/components/pair_registry.py` line ~157: `tourn_files = [f ... if f.startswith("tournament_results")]` then `tourn_files[0]` — busloans is the only pair with a `tournament_results_20260612_manifest.json` sibling (Evan's legit META-CMP manifest); listdir returns the manifest first → `pd.read_csv` ParserError ("Expected 2 fields in line 18, saw 9") → swallowed into integrity-issues → card shows "—". Reproduced deterministically. Fix: filter to `.endswith('.csv')` (and prefer latest-dated). | **Ace** |

Minor notes (non-blocking):
- N-1: tournament_sharpe_dist title renders with nested `<b><b>…</b></b>` (caption-override wrap + loader wrap). Visually clean; cosmetic. Owner: Ace.
- N-2: uniform 2× 404 console resource on every page incl. frozen Sample — pre-existing, not this wave.
- N-3: Evidence tournament intro phrasing is "the best of those 4,396" (dispatch expectation said "best of the 4,396") — content equivalent, no action.

## Verdict

~~**NOT READY** for Lead's dawodev request until QA-1 is fixed by Ace. Re-verify scope after fix: landing page DOM + `load_pair_registry()` unit reproduction only — all pair-page, gate, and triangulation results stand.~~ **Superseded — see QA-1 closure below.**

## QA-1 Closure — Re-verify (2026-06-12, Quincy, post-`d8d656b`)

Ace's fix `d8d656b` (`pair_registry.py` tournament glob restricted to `.csv`, latest-dated selection). Re-verify scope as stated: landing page only. Evidence: `temp/260612_qa_busloans/reverify/` (landing.txt + landing.png).

| Check | Result |
|---|---|
| Unit reproduction: `load_pair_registry()` busloans entry | **PASS** — `{best_oos_sharpe: 1.5, bh_sharpe: 0.89, valid_combos: 4396, max_drawdown: -1.0, bh_drawdown: -23.9, nature: lagging, type: credit, objective: min_mdd}`; integrity issues for busloans: **empty** |
| Landing DOM: busloans card KPIs | **PASS** — Sharpe 1.50 / 0.89, Max DD −1.0% / −23.9%, Valid 4,396 / 6,101, chips Lagging · Credit · Min MDD |
| Other 8 cards vs captured baseline (`dom_text/landing.txt`) | **PASS** — unified diff shows ONLY the busloans KPI rows changed; additionally the "1 pair(s) have incomplete classification metadata" integrity banner disappeared (it was a QA-1 symptom — correct removal) |
| Error banners / "0 / 0" / tracebacks | **PASS** — zero |
| Console errors | **PASS** — zero (the previously-noted 2×404 static-asset hit did not recur this run) |

Note: card denominator shows 6,101 (= tournament CSV rows incl. the valid=False BENCHMARK row) vs winner_summary `total_combos` 6,100 — same display convention as all existing cards (e.g. hy_ig "2,036 / 2,167"); the dispatch-required valid numerator 4,396 is correct. Non-blocking, pre-existing convention.

**QA-1: CLOSED. Updated verdict: READY** for Lead's merge-readiness review / dawodev request.

🤖 Agent: QA Quincy
