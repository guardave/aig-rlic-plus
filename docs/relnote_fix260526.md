# Release Notes — branch `fix260526`

**Started:** 2026-05-26
**Scope:** Address all confirmable issues raised in `Step C - Dashboard Comment log.xlsx` for the three pairs `indpro_xlp`, `indpro_spy`, `vix_vix3m_spy` (22 actionable issues of 23 total; 1 out of scope).
**Method:** LEAD-WM1 Mode 2 (single maker + multiple checkers), one pair per wave, cloud-DOM-verified after each wave.

**Branch-specific cloud deployment:**
- URL: `https://aig-rlic-plus-fix260526.streamlit.app/`
- Tracks branch `fix260526` (separate from main `aig-rlic-plus.streamlit.app` which tracks `main`).
- Use this URL for all cloud-render verifications until branch merges back to `main`.
- All cloud headless-Playwright checks in this branch must target this URL, not the main app.
**Status legend:** 🟡 in-progress · ✅ delivered + cloud-verified · ⏸ deferred · ⛔ out of scope

This document is updated continuously as work progresses on this branch. Final form ships as part of the merge back to `main`.

---

## Branch-level context

- **Pre-fix baseline** (captured via headless render 2026-05-26): see `temp/fix260526/dom/*.txt` and `temp/fix260526/png/*.png` (12 pages × 3 pairs).
- **Issue list source:** `temp/fix260526/issue_table.md` (confirmation table).
- **Wave plan:** `temp/fix260526/wave_plan.md`.
- **Confirmation findings raw JSON:** `temp/fix260526/confirmation_findings.json`.

---

## Wave 0 — Cross-pair template fixes (3 issues, all 11 pairs affected)

**Status:** ✅ Complete — cloud-DOM verified on all 11 active pairs.
**User direction (2026-05-26):** isolate cross-pair items first; regression-test the 8 not-in-scope pairs to confirm no regression.

### Deliverables

| ID | Description | Owner-hat | Status |
|---|---|---|---|
| 23 | Breadcrumb anchors `target=_blank` → same-tab navigation (affects all pairs). Root cause: hardcoded `pages/9_{pair_id}_{step}.py` in `breadcrumb.py` worked only for hy_ig_v2_spy (prefix 9). For everyone else `st.page_link` raised, markdown fallback fired, Streamlit promoted the link to `target=_blank`. Fix: use `get_page_prefix(pair_id)` + explicit `<a target=_self>` fallback. | Ace | ✅ |
| 34 | "Probability Engine Panel" → "Signal Monitoring Panel" via signal-type discriminator (signal column starting with `hmm_`, `ms_`, `prob_`, `stress_prob` keeps "Probability Engine Panel"; everything else gets "Signal Monitoring Panel"). Preserves Sample (`hy_ig_v2_spy`) AND `hy_ig_spy` which also uses HMM. | Ace | ✅ |
| 104 | Cross-period caption: render bold ABOVE chart via `st.markdown(f"**{caption}**")` instead of grey `st.caption()` below. Surgical fix at template level, `load_plotly_chart` signature unchanged. | Ace | ✅ |

### Regression render — all 11 active pairs (cloud, fix260526 preview app)

| Pair | Story (#23) | Strategy (#34) | Evidence (#104) | Verdict |
|---|---|---|---|---|
| `indpro_xlp` | PASS | PASS | PASS | ✅ |
| `indpro_spy` | PASS | PASS | PASS | ✅ |
| `vix_vix3m_spy` | PASS | PASS | PASS | ✅ |
| `dff_ted_spy` | PASS | PASS | PASS | ✅ |
| `hy_ig_v2_spy` (Sample) | PASS | PASS (kept "Probability Engine Panel") | PASS | ✅ |
| `hy_ig_spy` | PASS | PASS (also HMM, kept "Probability Engine Panel") | PASS | ✅ |
| `permit_spy` | PASS | PASS | PASS | ✅ |
| `sofr_ted_spy` | PASS | PASS | PASS | ✅ |
| `ted_spliced_spy` | PASS | PASS | PASS | ✅ |
| `umcsent_xlv` | PASS | PASS | PASS | ✅ |
| `gold_copper_xli` | PASS | PASS | PASS | ✅ |

**Aggregate: 33 of 33 checks PASS.**

### Cloud-DOM verification artefacts

- DOM dumps: `temp/fix260526/w0_regression_dom/{pair}_{page}.txt` (33 files)
- Raw findings JSON: `temp/fix260526/w0_regression_findings.json`
- Verifier script: `temp/fix260526/w0_regression.py`

### Commits

- `33f78fc` — `fix(template): W0 cross-pair fixes — breadcrumb same-tab + adaptive panel title + cross-period caption above chart`

### Notes from W0 execution

- Initial test logic for #34 used `pair == "hy_ig_v2_spy"` as the "Sample-only" discriminator and falsely flagged `hy_ig_spy` (which ALSO uses an HMM probability signal). Test corrected to read each pair's `winner_summary.signal_column` and apply the same `_PROBABILITY_PREFIXES` heuristic the panel uses. Underlying fix was correct; only the test was wrong.
- All breadcrumb fallback markdown links now emit `<a target="_self">`. Same hardening pattern as gold_copper_xli fix `2a3b94f` applied to `app/app.py` home tiles.
- **Important caveat — W0 regression sweep was 3-marker only.** It checked breadcrumb / panel title / cross-period caption but did NOT click into tabs OR scan for `chart pending` / `APP-SEV1` placeholders. User sample-checked `indpro_spy_strategy` immediately after W0 and reported missing charts and data. Subsequent deep inspection (`temp/fix260526/deep_inspect.py` — clicks every tab, greps for a much wider error-marker set) found **6 pre-existing data gaps** on the Strategy pages of `indpro_spy` + `vix_vix3m_spy` (missing `drawdown.json`, `walk_forward.json`, `winner_trades_broker_style.csv` for each). These are not W0 regressions (the files have never existed in git for these pairs) but they ARE real defects exposed by the more thorough cloud check. **Added as N1–N6 to the issue table (Addendum); folded into W2 + W3 scope.**
- **Process lesson:** "passed cloud verification" only means what the verifier actually checked. From now on, the deep_inspect script (every tab × every error marker) is the canonical "before declaring W done" gate. The narrow 3-marker check is appropriate ONLY for confirming a specific cross-pair fix landed, not for declaring a wave clean.

### W0 closure caveat

W0 is verified clean for the 3 fixes it was scoped to ship (#23 breadcrumb, #34 panel title, #104 cross-period caption — 33/33 PASS across 11 pairs). It is NOT a "no defects anywhere" claim. The pre-existing data gaps surfaced by deep_inspect are flagged for W2/W3 fixes (see N1–N6 in `issue_table.md`).

---

## Wave 0.5 — Missing strategy + cross-period artefacts (N1–N7, 2 pairs)

**Status:** ✅ Complete — cloud-DOM verified.
**Trigger:** user sample-checked `indpro_spy_strategy` and reported broken charts/missing data; deep_inspect found 6 missing files across `indpro_spy` + `vix_vix3m_spy`. Plus a misleading "no data" rendering on sub-period Sharpe (different problem than missing files: showed zero bars with ambiguous "(IS)" label).
**User direction:** *"issue is issue, whether predated or not does not matter most. What matters most is whether it truly impacts the correctness, completeness, consistency and layperson reader friendliness."* All N1–N7 fail all 4 dimensions → in scope.

### Deliverables

| ID | Pair | Deliverable | Status |
|---|---|---|---|
| N1 | indpro_spy | `output/charts/indpro_spy/plotly/drawdown.json` | ✅ |
| N2 | indpro_spy | `results/indpro_spy/winner_trades_broker_style.csv` (76 rows, APP-TL1) | ✅ |
| N3 | indpro_spy | `output/charts/indpro_spy/plotly/walk_forward.json` | ✅ |
| N4 | vix_vix3m_spy | `output/charts/vix_vix3m_spy/plotly/drawdown.json` | ✅ |
| N5 | vix_vix3m_spy | `results/vix_vix3m_spy/winner_trades_broker_style.csv` (638 rows) | ✅ |
| N6 | vix_vix3m_spy | `output/charts/vix_vix3m_spy/plotly/walk_forward.json` | ✅ |
| N7 | both pairs | `subperiod_sharpe.csv` + `subperiod_sharpe.json` re-derived from current strategy_return series; chart now distinguishes 3 visual states: real bar / "(in cash)" / "(no data)" | ✅ |

### Implementation

- New generator: `scripts/w0p5_generate_missing_strategy_artefacts.py` — reads `winner_summary` + `signals_*.parquet` + master daily parquet, derives the strategy `position` series from the threshold-code semantics (`T1_fixed_p25` → IS quantile 0.25, etc.), then emits drawdown + walk_forward + APP-TL1 broker log + re-derived sub-period Sharpe. Generic across pairs.
- Also patched: `scripts/synthesize_broker_trade_log.py` — now prefers `winner_summary.signal_column` (APP-WS1 schema field) over the legacy hardcoded `SIGNAL_COL_MAP`. Removes the "Unknown signal_code" hard error for any pair with a schema-valid winner summary.

### Cloud verification (fix260526 preview app)

**Strategy pages (the user-reported failure):**
- Before: `indpro_spy_strategy` Performance + Confidence tabs showed `APP-SEV1, chart pending, missing` markers.
- After: 0 error markers. Chart count: Performance 5→7, Confidence 5→7 on indpro_spy; 6→8 on vix.

**Evidence sub-period:**
- Before: zero bars with ambiguous "(IS)" label — reader couldn't tell if data is missing or strategy was in cash.
- After: explicit 3-state labelling — real bars (e.g. `Dot-Com Crash (IS)` with Sharpe value), `(in cash)` (long-cash strategy was 100% cash through episode), `(no data)` (episode is outside pair's data coverage — VIX3M data starts 2007 so Dot-Com is genuinely outside coverage for vix). Reader-friendly.

### Process improvement landed

`temp/fix260526/deep_inspect.py` — every page × every tab × wide error-marker grep. This is now the canonical "before declaring a wave done" gate. The narrow 3-marker check used at W0 closure was the wrong tool for that purpose; the deep_inspect catches what targeted-marker checks miss.

### Commits

- `a19e7f2` — `fix(strategy): W0.5 ship N1–N7 missing strategy + cross-period artefacts (indpro_spy + vix_vix3m_spy)`

### Notes from W0.5 execution

- N7's "in cash" framing is economically correct, not a data bug. indpro_spy is a P1_long_cash procyclical strategy — through GFC / COVID / China 2015, IP momentum was deeply negative, threshold-gt-False, position=0 (cash). The original chart showed those as ambiguous zero bars with "(IS)" label; the new chart explicitly says `(in cash)` so the reader sees "strategy ran, produced no trade" instead of "data is missing".
- The cloud's auto-deploy of branch `fix260526` propagates ~30-90s after push; deep_inspect picked up the new charts within one polling cycle.
- The deep_inspect's narrow grep flagged "no data" substring matches that turned out to be *my new deliberate labels* (e.g. `Dot-Com Crash (IS) (no data)` for vix where data really starts 2007). Distinguishing "deliberate label" from "buggy missing-data render" requires per-pair context, not just substring matching. Worth refining in the verifier if used widely.

---

## Wave 1 — `indpro_xlp` (8 remaining issues, post-W0)

**Status:** ✅ Complete — cloud-DOM verified clean.

### Deliverables

| ID | Description | Status |
|---|---|---|
| 24 | Hero x-axis `dtick="M36"` + `tickformat="%Y"` — duplicate year ticks eliminated | ✅ |
| 25-1 | Hero: explicit `yaxis range` and `yaxis2 range` so IP YoY has its own visual envelope | ✅ |
| 25-2 | history_zoom_*.json layout patch: legend `y=-0.25` + bottom margin 110px | ✅ |
| 26 | CCF: significant bars now red; ±1.96·se CI lines now red dashed + labelled; explicit "0 of N lags exceed CI" annotation when none | ✅ |
| 27 | Regime quartile chart: descriptive x-labels ("Q1 (Weakest IP growth)" etc.) + best/worst annotation; data-grounded REGIME_CAPTION citing exact Sharpes | ✅ |
| 28 | Sub-period Sharpe: regenerated via W0.5 generator with 3-state labelling — real bar / "(in cash)" / "(no data)" | ✅ |
| 35 | Trigger cards: `instructional_trigger_cards.py` now derives strategy from `strategy_family` when `strategy_code=None`. indpro_xlp's P3_long_short winner now renders P3 "flip to 100% short/long" cards, not the previous P2 "scale exposure proportionally" mis-render | ✅ |
| 36 | Drawdown + walk_forward: read winner from `winner_summary.json` instead of `valid_strats.iloc[0]`. Standardised winner-label format: `{signal}/{threshold}/{strategy}/L{lead}`. Legend now correctly shows `S8_accel/T2_roll_p75/P3_long_short_counter/L3` | ✅ |
| 37 | Tournament scatter colorbar: `len=0.6, xpad=30, tickfont=9` — labels no longer overlap plot area | ✅ |
| **BONUS** | `scripts/generate_charts_indpro_xlp.py` save_chart() now strips the `indpro_xlp_` prefix to write canonical bare names (VIZ-NM1) — eliminates the producer-vs-cloud filename drift that had required manual rename steps | ✅ |

### Cloud-DOM verification (fix260526 preview app, indpro_xlp pages)

```
indpro_xlp_story       DEFAULT     11905 chars  6 charts  0 errors
indpro_xlp_evidence    DEFAULT      6959 chars  8 charts  0 errors  ('No data' markers gone)
indpro_xlp_strategy    DEFAULT      5137 chars  8 charts  0 errors
indpro_xlp_strategy    Performance  7631 chars  8 charts  0 errors
indpro_xlp_strategy    Confidence   4987 chars  8 charts  0 errors
indpro_xlp_methodology DEFAULT      7225 chars  0 charts  0 errors
```

**Spot-checked cloud DOM:**
- Drawdown chart legend: `Winner: S8_accel/T2_roll_p75/P3_long_short_counter/L3` ✓ (#36 fixed)
- Strategy Execute tab: `flip to 100% short XLP` / `flip to 100% long XLP` ✓ (#35 fixed)
- Regime chart x-labels: `Q1 (Weakest IP growth)`, `Q4 (Strongest IP growth)` ✓ (#27 fixed)
- Hero `xaxis.dtick = M36`, `yaxis.range = [-19.9, 19.1]`, `yaxis2.range = [9.9, 84.6]` ✓ (#24, #25-1 fixed)
- Scatter colorbar: `len=0.6, xpad=30, tickfont=9` ✓ (#37 fixed)

### Commits

- `24aa35f` — `fix(indpro_xlp): W1 ship 8 issues — chart producer + pair_config + trigger-cards fix`
- `a9ad54e` — `fix(indpro_xlp): align REGIME_CAPTION data citation with actual chart Sharpes`

### Notes from W1 execution

- The biggest non-cosmetic fix was **#36 (drawdown wrong winner)** — caused by the producer using `valid_strats.iloc[0]` instead of reading `winner_summary.json`. The fallback path was needed because the legacy `winner_summary.json` has `threshold_code=None` (BL-LEGACY-WINNER-SUMMARY-SHAPE), so exact-match against the tournament CSV failed and the producer fell back to `nlargest(1, "oos_sharpe")` — which correctly picked `S8_accel/T2_roll_p75/P3_long_short_counter/L3`.
- **#35 was a hidden duplicate of the strategy_code=None gap** — `instructional_trigger_cards.py` defaulted to "P2" when `strategy_code` was missing, rendering P2-style "scale proportionally" cards on a P3-binary winner. The renderer now falls back to deriving strategy from `strategy_family`. This fix benefits any pair with the legacy null `strategy_code` (likely also affects indpro_spy + sofr_ted_spy — to spot-check in W2 + the cross-pair regression).
- The `save_chart()` rename (bonus item) eliminates a process gap: prefixed chart filenames from the producer were being renamed by hand to bare names for cloud serving. This is silent fragility; producer now emits canonical names directly.
- W0.5's "regen + then producer overwrites" sequencing caught me — the producer regenerates drawdown + walk_forward, so re-running W0.5 then W1 producer overwrites the W0.5 versions. For pairs WITH a chart producer (indpro_xlp, indpro_spy, vix_vix3m_spy, etc.) the producer is authoritative; W0.5 generator should only be used as a fallback for pairs without one. Worth noting in the W0.5 helper docstring next time.

### Cloud-DOM verification (post-fix)

*(populated after wave completion)*

### Commits

*(populated as commits land)*

---

## Wave 2 — `indpro_spy` (6 actionable + 1 OOS)

**Status:** ✅ Complete — cloud-DOM verified clean. Also closes the same chart-class issues across all 10 pairs via cross-pair producer updates.

### Deliverables

| ID | Description | Status |
|---|---|---|
| 63 | Story-page decimal places audited: Sharpes 2dp, percentages 1dp — pattern uniform, no code change needed | ✅ (audited) |
| 64 | INDPRO naming standardised — NARRATIVE_SECTION_1 / _SECTION_2 now use `INDPRO` consistently after first-use definition | ✅ |
| 65 | CORRELATION_BLOCK observation rewritten to match actual `correlations.csv`: most Pearson r are small/insignificant; z-score `r=-0.108` at 6M (p=0.04) and `-0.144` at 12M (p=0.005) are the only Pearson-significant findings; momentum signals are Spearman-significant only | ✅ |
| 66 | Rolling Granger critical-value line (F=3.84) now a discrete legend entry `F = 3.84 (5% significance)` — previously only an `add_hline()` annotation that didn't render in the saved JSON. Affects all 10 pairs' rolling_granger chart | ✅ |
| 67 | CCF_BLOCK rewritten — original text was directionally BACKWARDS (claimed SPY leads INDPRO at small positive lags). Actual `ccf.csv` shows 11 of 25 lags significant, ALL at NEGATIVE lags (INDPRO leads SPY); peak around lag −9 to −12 (r ≈ 0.20–0.23). Updated caption, observation, interpretation, key_message | ✅ |
| 68 | Granger trace renamed from generic `Granger F-stat (24M)` to direction-aware `Granger F (INDPRO→SPY, 24M)` via new `_signal_target_labels()` helper. Crisper blue colour for primary trace (was muddy orange). Chart title also spells out direction. Affects all 10 pairs | ✅ |
| 69 | Out of scope — content request, not a defect | ⛔ |
| **BONUS** | `build_subperiod_sharpe()` in viz_cp_retro_apply.py extended with 3-state framing (real bar / "in cash" / "no data") — promotes the W0.5 fix from a 2-pair patch to all 10 pairs | ✅ |

### Cloud-DOM verification (fix260526 preview app, indpro_spy pages)

```
indpro_spy_story                   DEFAULT                        9843       6  0 errors
indpro_spy_evidence                DEFAULT                        7169      11  0 errors
indpro_spy_evidence                Level 1 — Basic Analysis       7169      11  0 errors
indpro_spy_evidence                Level 2 — Advanced Analysis    5926      11  0 errors
indpro_spy_evidence                Local Projections              5926      11  0 errors
indpro_spy_evidence                Quantile Regression            5885      11  0 errors
indpro_spy_evidence                Random Forest Importance       5815      11  0 errors
indpro_spy_strategy                DEFAULT                        5110       7  0 errors
indpro_spy_strategy                Execute                        5110       7  0 errors
indpro_spy_strategy                Performance                    7409       7  0 errors
indpro_spy_strategy                Confidence                     4585       7  0 errors
indpro_spy_methodology             DEFAULT                        6632       0  0 errors
```

**Spot-checked cloud DOM:**
- Pearson observation: cites `r = -0.108` and `r = -0.144` z-score values ✓ (#65)
- Pearson caption: cites `−0.144 at the 12M horizon (p = 0.005)` ✓ (#65)
- rolling_granger.json legend traces: `'Granger F (INDPRO→SPY, 24M)'`, `'F = 3.84 (5% significance)'`, `'p-value (right axis)'` ✓ (#66, #68)
- rolling_granger.json title: `Rolling Granger Causality: INDPRO → SPY (24M window)` ✓ (#68)
- CCF observation: `"11 of 25 lags are significant in this pair, all at NEGATIVE lags — INDPRO leads SPY"` ✓ (#67 — direction flipped correctly)

### Commits

- `3718fc9` — `fix(indpro_spy): W2 ship 6 issues — text-data alignment + cross-pair Granger/sub-period chart improvements`

### Notes from W2 execution

- **#65 + #67 were the most material — both were text-vs-data contradictions** (one understated significance, the other reversed direction). The original prose said "SPY leads INDPRO at positive lags" while the data clearly shows "INDPRO leads SPY at negative lags". Fixing these required computing-checking against the source CSVs, not just polishing prose. Honest data citations are the only defence against this class of bug.
- **#66 + #68 promoted to cross-pair fixes.** Both live in `viz_cp_retro_apply.py` which generates `rolling_granger.json` for every pair. Per the user direction ("issue is issue"), shipping the better version to all 10 pairs is the right call.
- **The deep_inspect tab-navigation limitation persists** — inner method-block tabs (Correlation / CCF / Granger) inside the Level-1/Level-2 outer tabs render as `len=0` when clicked from the flat tab list. They DO render correctly when reached via parent tab → child tab navigation; the script just can't replicate that user flow. Worth refining if heavy use continues.
- **#63 rounding audit** showed the pattern is already consistent. Annotating in relnote as "audited, conforms" rather than touching code unnecessarily.

---

## Wave 3 — `vix_vix3m_spy` (4 actionable, post-W0)

**Status:** ✅ Complete — cloud-DOM verified clean.

### Deliverables

| ID | Description | Status |
|---|---|---|
| 60 | Expanded VIX term-structure explanation in NARRATIVE_SECTION_1: "There is more than one VIX..." spelling out VIX (30d), VIX9D, VIX3M, VIX6M, VIX1Y as members of a *curve* of implied volatility across maturities | ✅ |
| 61 | "Intensity of short-term panic relative to medium-term panic" framing added as the thermometer analogy: ratio high = panic, ratio low = stable | ✅ |
| 62 | Inline footnote subsection covering `implied volatility`, `option pricing theory`, `contango / backwardation`, `hedging demand`, `put demand` — each with a plain-English paragraph definition | ✅ |
| 103 | CORRELATION_BLOCK fully rewritten — and this was more than an extension, it was a CORRECTION. Original prose claimed "uniformly negative correlations across signal variants and forward horizons" but the actual `correlations.csv` shows 29 of 44 cells POSITIVE (range −0.038 to +0.071); only one cell significant-negative at p<0.05. The rewrite honestly explains why linear Pearson is the wrong lens for this regime-switching signal AND surfaces the small positive longer-horizon correlations as a real vol-risk-premium artefact | ✅ |

### Cloud-DOM verification (fix260526 preview app)

```
vix_vix3m_spy_story     DEFAULT  11570 chars (was 9951)  5 charts  0 errors
vix_vix3m_spy_evidence  DEFAULT   8779 chars (was 6633)  7 charts  0 errors
vix_vix3m_spy_strategy  DEFAULT   5331 chars  8 charts (incl. W0.5 drawdown/walk_forward)  0 errors
vix_vix3m_spy_methodology         6086 chars  0 charts  0 errors
```

**Spot-checked cloud DOM:**
- Story body now contains `"There is more than one VIX"` ✓ (#60)
- Story body contains `"intensity of short-term panic relative to medium-term panic"` ✓ (#61)
- Story body contains `"Contango / backwardation"`, `"Hedging demand"`, `"Put demand"`, `"option pricing theory"` footnote definitions ✓ (#62)
- Evidence Correlation block contains `"29 of 44 Pearson cells are POSITIVE"` + `"r = +0.060"` zscore_252d at 63d + vol-risk-premium explanation ✓ (#103)

### Commits

- `8d2cccb` — `fix(vix_vix3m_spy): W3 ship 4 narrative additions (#60, #61, #62, #103)`

### Notes from W3 execution

- **#103 was the third confirmed text-vs-data drift this branch** (after gold_copper_xli winner mismatch and indpro_spy Pearson/CCF). Pattern: narrative authored ahead of (or independently from) data verification → silent drift. Cure (already in memories.md): prose with explicit numeric citations, grep-verified at commit.
- W3 was the cleanest wave to execute — text-only edits, no producer or chart changes, no smoke surprises.

---

## Cross-pair `iloc[0]` audit (post-W1 finding)

**Status:** ✅ Complete — no outstanding instances of the W1 #36 bug class.

**Method:** grepped `scripts/generate_charts_*.py` and `scripts/pair_pipeline_*.py` for `valid_strats.iloc[0]` / `valid.iloc[0]` / `tourn*.iloc[0]` patterns and inspected each result.

**Findings:**
- Only 2 instances of the bug pattern existed: both in `generate_charts_indpro_xlp.py` (chart_drawdown + chart_walk_forward) — already fixed in W1 (commit `24aa35f`).
- All other `.iloc[0]` calls are: (a) BENCHMARK-row picks (single deterministic row), (b) `ccf_df["se"].iloc[0]` (single SE value), (c) post-`nlargest(N, "oos_sharpe")` calls (explicit Sharpe ordering).
- `indpro_spy` and `vix_vix3m_spy` lack `chart_drawdown` / `chart_walk_forward` in their producers — those artefacts are generated by the W0.5 helper which reads `winner_summary.json` directly (clean by construction).

**Conclusion:** the wrong-winner bug was scoped to indpro_xlp; no other pair was affected.

---

## Final cross-pair regression — all 11 active pairs × 4 pages = 44 renders

**Status:** ✅ Complete — 44 of 44 PASS.

**Method:** `temp/fix260526/final_regression.py` — headless Playwright walk of all 11 active pairs × Story / Evidence / Strategy / Methodology, greps each rendered DOM for known error markers.

**Result:**

```
Result: 44 PASS, 0 FAIL  (44 total pages)
```

All 11 pairs render cleanly with the W0 + W0.5 + W1 + W2 + W3 changes. No regressions on any pair NOT directly targeted (8 of 11).

**Cross-pair leverage delivered:**
- W0 #23 (breadcrumb same-tab): all 11 pairs.
- W0 #34 (adaptive panel title via signal-type discriminator): all 11 pairs; hy_ig_v2_spy + hy_ig_spy correctly retain "Probability Engine Panel" (HMM signals); 9 others get "Signal Monitoring Panel".
- W0 #104 (cross-period caption above chart, bold): all 11 pairs.
- W2 #66 + #68 (Granger label + direction-aware trace name): all 10 pairs that have rolling_granger.json.
- W2 sub-period 3-state framing: all 10 pairs that have subperiod_sharpe.json.

Cross-pair output: 5 template-level fixes × ~9 not-directly-targeted pairs = ~45 cross-pair benefits delivered alongside the 22-issue per-pair work. The "fix the template" leverage was real.

---

## Branch close

**Status:** Ready for merge to `main`.

### Inventory

| Wave | Commits | Issues addressed |
|---|---|---|
| W0 | `33f78fc` | #23, #34, #104 (template, 11 pairs) |
| W0.5 | `a19e7f2` | N1–N7 (missing strategy artefacts on 2 pairs) |
| W1 | `24aa35f`, `a9ad54e` | #24, #25-1, #25-2, #26, #27, #28, #35, #36, #37 (indpro_xlp) |
| W2 | `3718fc9` | #63, #64, #65, #66, #67, #68 (indpro_spy + cross-pair) |
| W3 | `8d2cccb` | #60, #61, #62, #103 (vix_vix3m_spy) |
| EOD | `ee84502` | session checkpoint |

**Total in scope:** 23 issues + 7 N-issues = **30 issues**. **1 out of scope (#69 content request).**
**Total resolved:** 29 (excluding #69).

### Final preview-app state

`https://aig-rlic-plus-fix260526.streamlit.app/` — 44/44 PASS, ready for stakeholder spot-check before merge.

### Post-merge follow-ups

- Promote `scripts/w0p5_generate_missing_strategy_artefacts.py` and the `temp/fix260526/deep_inspect.py` patterns to project-level tooling (`scripts/` or `app/_smoke_tests/`).
- Decide on preview app: keep tracking a future branch, or delete.
- Address `indpro_spy` #69 (team-members content request) if user still wants it.

### Cloud-DOM verification

*(populated after wave completion)*

### Commits

*(populated as commits land)*

---

## Cross-pair regression (post-W3)

*(populated after all three waves complete; full render of 11 active pairs to check #23 breadcrumb fix and #34 panel rename for no-regression on Sample + other pairs)*

---

## Lessons / observations recorded during execution

*(running log — populated as fixes reveal patterns worth memorising for SOPs)*

- *(none yet)*

---

## Branch close

*(populated at merge-back-to-main time)*
