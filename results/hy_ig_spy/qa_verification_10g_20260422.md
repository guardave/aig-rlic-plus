# QA Verification — Wave 10G.4F — hy_ig_spy

**QA Agent:** Quincy  
**Date:** 2026-04-22  
**Wave:** 10G.4F  
**Scope:** Local pre-cloud QA gate sweep (Cloud verification deferred to Phase 5)

---

## Summary

| Total checks | PASS | PASS-with-note | FAIL |
|-------------|------|----------------|------|
| 9 | 8 | 1 | 0 |

**Sign-off: APPROVE for cloud verification** (no blocking findings)

---

## Check-by-Check Results

### Check 1 — GATE-27 Local Smoke (smoke_loader + smoke_schema_consumers)

| Command | Result |
|---------|--------|
| `python3 app/_smoke_tests/smoke_loader.py hy_ig_spy` | PASS — 6/6 charts, failures=0 |
| `python3 app/_smoke_tests/smoke_schema_consumers.py --pair-id hy_ig_spy` | PASS — 5/5 checks, failures=0 |
| `python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy` (regression) | PASS — 15/15 checks, failures=0 |
| `python3 app/_smoke_tests/smoke_loader.py indpro_xlp` (regression) | PASS — 8/8 checks, failures=0 |
| `python3 app/_smoke_tests/smoke_loader.py umcsent_xlv` (regression) | PASS — 7/7 checks, failures=0 |

**Verdict: PASS**  
All 5 smoke targets pass with zero failures. No regressions on existing pairs.

---

### Check 2 — GATE-29 Clean-Checkout + Signals Parquet

```
git clone --depth 1 /workspaces/aig-rlic-plus /tmp/clean_hy_ig_spy_10G
cd /tmp/clean_hy_ig_spy_10G
git ls-files results/hy_ig_spy/signals_*.parquet  → results/hy_ig_spy/signals_20260422.parquet
git ls-files results/hy_ig_spy/*.parquet           → results/hy_ig_spy/signals_20260422.parquet
python3 app/_smoke_tests/smoke_loader.py hy_ig_spy → 6 PASS, 0 FAIL
```

All 6 deploy-required artifacts per team-standards §5.2 confirmed committed:
- `signals_20260422.parquet` ✓
- `winner_summary.json` ✓
- `signal_scope.json` ✓
- `interpretation_metadata.json` ✓
- `tournament_results_20260422.csv` ✓
- `analyst_suggestions.json` ✓

**Verdict: PASS**  
Signals parquet present and committed. Clean-checkout smoke passes.

---

### Check 3 — Schema Validation Sweep

All 4 canonical instance files validated against their registered schemas via `jsonschema`:

| Instance file | Schema | Result |
|---------------|--------|--------|
| `winner_summary.json` | `winner_summary.schema.json` | PASS |
| `interpretation_metadata.json` | `interpretation_metadata.schema.json` | PASS |
| `signal_scope.json` | `signal_scope.schema.json` | PASS |
| `analyst_suggestions.json` | `analyst_suggestions.schema.json` | PASS |

Direction triangulation (schema-consumer smoke): `winner_summary.direction=countercyclical` == `interpretation_metadata.observed_direction=countercyclical` ✓

**Verdict: PASS**  
All 4 instance files conform to their registered schemas.

---

### Check 4 — QA-CL2 Semantic KPI Triangulation

**Source:** `winner_summary.json`  
**Evan-reported:** Sharpe 1.41, ann_return 11.7%, MDD -8.5%, 387 trades  
**OOS window:** 2019-10-01 → 2026-04-22 = 6.6 years

| KPI check | Computed | Tolerance | Result |
|-----------|----------|-----------|--------|
| Implied vol (rf=4%, Sharpe formula) | 5.5% | — | Plausible for HMM signal-strength strategy |
| Drawdown-vol ratio \|MDD\|/vol | 1.55 | [1, 6] for equity | PASS |
| Turnover from n_trades/years | 59.0 trades/year | — | Note (see below) |
| annual_turnover field × 2 | 7.7 (round-trips/year) | — | — |

**Turnover note (PASS-with-note):** The `annual_turnover` field (3.84) represents portfolio-fraction turnover (a continuous metric), while `oos_n_trades` (387) counts discrete trade entries from the winner_trade_log. These are incommensurate metrics and should not be triangulated against each other. The winner_trade_log confirms 387 rows over 6.6 years = 58.7 position adjustments/year, consistent with a daily signal-strength strategy (P2) that resizes positions daily. The `annual_turnover=3.84` means the strategy rotates its full portfolio value approximately 3.84x per year — both are self-consistent with an HMM signal-strength approach. **No anomaly; QA-CL2 formula's trade-count/turnover check is inapplicable to continuous-scaling strategies.**

**Verdict: PASS-with-note**  
All triangulable KPIs pass. The turnover-trade-count check is not applicable to signal-strength (proportional position sizing) strategies; documentation note added above.

---

### Check 5 — APP-DIR1 Direction Triangulation (3-Way)

| Source | Field | Value |
|--------|-------|-------|
| `winner_summary.json` | `direction` | `countercyclical` |
| `interpretation_metadata.json` | `observed_direction` | `countercyclical` |
| `docs/portal_narrative_hy_ig_spy_20260422.md` | `direction_asserted` (frontmatter line 7) | `countercyclical` |

All three sides agree. Cross-agent seam is clean.

**Verdict: PASS**  
3-way direction consensus confirmed: Evan, Dana (updated), Ray all assert `countercyclical`.

---

### Check 6 — GATE-NR Narrative Instrument Scan (Local DOM Approximation)

**Scanned:** `app/pair_configs/hy_ig_spy_config.py` + `docs/portal_narrative_hy_ig_spy_20260422.md`

```
grep -E "(XLV|XLP|DIA|QQQ|IWM)" hy_ig_spy_config.py    → 0 matches
grep -E "(XLV|XLP|DIA|QQQ|IWM)" portal_narrative_*.md   → 0 matches
```

One "bonds" mention in config (line 202): "their bonds began repricing" — this is historical narrative about HY bond repricing in the Dot-Com context, not an instruction for bond exposure. Correct instrument: SPY is the only equity ticker throughout.

SPY appears as target throughout. "S&P 500" appears correctly as SPY's descriptive label. No cross-pair ticker contamination found.

**Verdict: PASS**  
No non-target instrument tickers. Bond language is narrative-contextual (credit mechanism explanation), not exposure-indicating.

---

### Check 7 — Stakeholder-Spirit Review

**Story headline/thesis (from narrative frontmatter):**  
"Credit spreads as a leading equity risk signal — OOS Sharpe vs SPY buy-and-hold"

**Non-quant reader test:**
- Signal explained in plain terms: "When corporate junk bonds demand a much higher yield premium over investment-grade bonds, equity markets typically suffer" — ✓ accessible
- Trading rule explained: HMM stress probability > 0.5 → reduce SPY exposure proportionally to stress level — ✓ concrete
- Numbers visible: OOS Sharpe 1.41 vs 0.81 B&H, MDD -8.5%, return 11.7% — ✓ in narrative frontmatter and config
- Historical episodes (3): Dot-Com, GFC, COVID — ✓ grounded in real events a non-quant reader will recognise
- The 2022 rate-shock limitation is explicitly flagged — ✓ appropriate intellectual honesty
- Numeric claims in prose consistent with winner_summary: Sharpe 1.41, MDD -8.5%, Return 11.7% — all match ✓

One observation: the narrative notes "OOS Sharpe 1.41 vs 0.81 B&H" but the B&H ann_return (16.1%) is higher than the strategy return (11.7%). The Sharpe win is driven by lower volatility and smaller drawdown, not higher absolute return — this is correctly reflected in the narrative's MDD comparison (-8.5% vs higher B&H drawdown) and the "risk-adjusted alpha" framing. No misrepresentation.

**Verdict: PASS**  
Non-quant reader can understand signal and trading rule in under 5 minutes. Numeric claims consistent. Instrument names correct throughout. Appropriate caveats for rate-shock environment.

---

### Check 8 — APP-PT1 Thin-Wrapper Gate

```
grep -cE "^[[:space:]]*st\." app/pages/15_hy_ig_spy_*.py
15_hy_ig_spy_evidence.py:    0
15_hy_ig_spy_methodology.py: 0
15_hy_ig_spy_strategy.py:    0
15_hy_ig_spy_story.py:       0
```

**Verdict: PASS**  
All 4 pages are pure thin wrappers. Zero direct `st.*` calls.

---

### Check 9 — Feature Parity vs Sample (14-Item)

| # | Feature | Evidence | Result |
|---|---------|----------|--------|
| 1 | Probability Engine Panel | `render_probability_engine_panel` called at line 993 in template Strategy block | PASS |
| 2 | Position Adjustment Panel | `render_position_adjustment_panel` called at line 996 | PASS |
| 3 | Instructional Trigger Cards | `render_instructional_trigger_cards` called at line 999 | PASS |
| 4 | Live Execution Placeholder | `render_live_execution_placeholder` called at line 1111 | PASS |
| 5 | 3-Way Direction Check (APP-DIR1) | `render_direction_check(pair_id)` called at template line 893 | PASS |
| 6 | 8-element Evidence blocks | 3 level-1 (Correlation, Granger, CCF) + 5 level-2 (HMM, Regime Quartile, Transfer Entropy, LP, Quantile) = 8 blocks confirmed in EVIDENCE_METHOD_BLOCKS | PASS |
| 7 | Historical Zoom (3 episodes) | `HISTORY_ZOOM_EPISODES` = 3 (dotcom, gfc, covid) confirmed in config | PASS |
| 8 | HMM regime subtabs | `HMM_BLOCK` present in level2 with `regime_context` field populated | PASS |
| 9 | Breadcrumb nav | `render_breadcrumb` imported and called in template Story and Evidence | PASS |
| 10 | Glossary sidebar | `render_glossary_sidebar()` called at template line 318 | PASS |
| 11 | Execute/Performance/Confidence tabs | `st.tabs(["Execute", "Performance", "Confidence"])` at template line 974 | PASS |
| 12 | Level 1 / Level 2 tabs | `level1_blocks` / `level2_blocks` processing at template lines 783-784 | PASS |
| 13 | Signal Universe | `render_signal_universe` imported and called at template line 1298 | PASS |
| 14 | Analyst Suggestions | `render_analyst_suggestions(pair_id)` called at template line 1347 | PASS |

**All 14/14 features verified via config + template inspection.**

**Verdict: PASS**

---

## Cross-Claim Verification Notes

1. **Sharpe claim consistency:** winner_summary.oos_sharpe=1.4083, narrative=1.41, config=1.41 — all rounded consistently ✓
2. **Tournament valid combos:** smoke_loader reports "2036 Valid Combos" in tournament_scatter title vs Evan's handoff listing oos_n_trades=387. These are distinct counts (combos tested vs trades executed) — no conflict ✓
3. **OOS window:** 2019-10-01 to 2026-04-22 = 6.6 years per ECON-OOS2 (79 months) ✓
4. **smoke_schema_consumers APP-DIR1 note:** "Ray=pending RES-17" — this refers to the smoke test not yet reading Ray's frontmatter file. Quincy independently confirmed Ray's frontmatter direction_asserted=countercyclical at line 7 of the narrative doc. 3-way check confirmed PASS.

---

## Sign-off Recommendation

**APPROVE for cloud verification**

No blocking findings. All 9 checks pass (8 clean PASS, 1 PASS-with-note on KPI triangulation method applicability). The pair is ready for Phase 5 cloud verify after user reboots Streamlit.

**Next action for Lead:** Reboot Streamlit, navigate to pair 15 (hy_ig_spy), and perform cloud DOM verification against the 14-item feature parity list.

---

*Report generated: 2026-04-22T11:06:00Z*  
*Agent: QA Quincy (qa-quincy@idficient.com)*
