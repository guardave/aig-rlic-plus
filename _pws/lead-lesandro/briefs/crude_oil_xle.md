# Pair Brief — `crude_oil_xle`

**Status:** scheduled — not yet started. First pair built under LEAD-NPB1.
**Authored:** 2026-06-02 by Lead Lesandro.
**Rule:** [LEAD-NPB1](../../../docs/agent-sops/lead-agent-sop.md) New-Pair Brief Discipline.

---

## 1. Pair identity (LEAD-DV1)

| Field | Value |
|---|---|
| **`pair_id`** | `crude_oil_xle` |
| **Indicator → target** | Crude Oil Price (WTI) → XLE (Energy Select Sector SPDR) |
| **Source CSV row** | `data/prospective_pairs.csv` line 39 (single Done-Y target — no per-sector family for this indicator) |
| **Source CSV ticker** | `En - Crude Oil $` |
| **Indicator category** | energy |
| **Pre-master row 2** | col 76, sheet `WCOILWTICO` col B — "Crude Oil Prices: West Texas Intermediate (WTI), Units: Dollars per Barrel, Not Seasonally Adjusted, Weekly, Jan 1986 – Oct 2025" |
| **FRED series** | `WCOILWTICO` (verify with Dana at first dispatch — Pre-master sheet name matches FRED series ID) |
| **Frequency** | Weekly |
| **Units** | USD per barrel (level, NSA) |
| **SA** | NSA |

**Indicator-vs-other-crude-series disambiguation.** Pre-master has TWO crude-related columns. This pair uses the **price** series (`WCOILWTICO`, col 76), NOT the **inventory** series (`WTTSTUS1`, col 40, Thousand Barrels). `wttstus1_spy` is a separate pair in the catalog. Do not conflate.

**Domain notes (Lesandro):**
- Crude price → XLE (energy sector ETF) is the canonical pro-cyclical sector pair. Mechanism is direct: XLE constituents' revenue is denominated in oil prices, so equity values track underlying barrel value with a sector beta typically > 1.
- Three econometric pitfalls to flag for Evan:
  1. **Frequency mismatch.** XLE is daily; WTI is weekly in the source. Either resample XLE to weekly (cleaner, smaller sample) or forward-fill WTI to daily (avoid look-ahead by lagging the fill). Document the choice in `signal_scope.json`.
  2. **Regime non-stationarity.** WTI level has had several structural breaks (1986 collapse, 2008 spike+crash, 2014 shale-glut, 2020 negative-price episode, 2022 invasion spike). Level-based regressions will misbehave; RoC, log-return, or rolling z-score are more useful signals.
  3. **Reverse-causality risk.** Oil price moves and energy-sector equity moves can be near-simultaneous on news days. Granger causality tests should be 5d / 10d / 20d lags, not 1d (autocorrelation at 1d ≈ contemporaneous).
- **Expected direction:** pro-cyclical (rising oil → rising XLE). Confidence: high (mechanism is mechanical; published literature is dense).

---

## 2. Active backlog items binding this pair

The following deferred backlog items name "next pair" / "new pair start" / "new pair build" in their reactivation trigger. They bind `crude_oil_xle` from the first dispatch.

| BL-ID | Owner | What this pair must do |
|---|---|---|
| **BL-002** | Quincy → Evan | Emit `results/crude_oil_xle/signal_scope.json` per ECON-UD. Universe-disclosure JSON must list every candidate strategy considered, not just the winner. |
| **BL-003** | Quincy → Evan | Emit `results/crude_oil_xle/analyst_suggestions.json` per ECON-AS. If no suggestions exist at pipeline-end, emit a placeholder `{"suggestions": []}` with the schema; do not omit the file. |
| **BL-004** | Lead → Ace | APP-NP1 page-prose discipline. **`app/pages/N_crude_oil_xle_*.py` files must contain ZERO `st.markdown()` calls.** All prose sources from `docs/portal_narrative_crude_oil_xle.md` (Ray) via `app/pair_configs/crude_oil_xle_config.py` (Ace). Page files are pure template wrappers. |
| **BL-801** | Lead → Ace | winner_summary consumer key discipline. **No `winner.get("max_drawdown", <hardcoded_fallback>)` patterns.** Use `winner.get("oos_max_drawdown", winner.get("max_drawdown"))` exactly, matching `app/components/page_templates.py:548`. Hardcoded numeric fallbacks are forbidden. |
| **BL-APP-PT1-LEGACY** | Lead → Ace | All four pages (`_story`, `_evidence`, `_strategy`, `_methodology`) MUST be thin APP-PT1 wrappers calling `render_<page>_page()`. NOT hand-written. Page file body is ≤10 lines (sys.path shim + import + one template call). |
| **BL-DUP-11** | Lead → Evan | Pipeline tournament-winner selection uses `from scripts.tournament import select_winner` instead of inline `df[df["valid"] & ...].loc[idxmax("oos_sharpe")]`. The helper exists; new pipelines should not re-introduce the pattern. |
| **BL-DUP-15** | Lead → Evan | Pipeline run-stamps use `from scripts._stamp import iso_utc_now`. No `datetime.utcnow()` or hand-formatted `now(timezone.utc).strftime(...)`. |
| **BL-DUP-4** | Lead → Vera | Chart generators that need NBER recession shading use `from scripts._nber import add_nber_shading, RECESSIONS`. No inline `RECESSIONS = [...]` tuples. |
| **BL-COMMISSION-BASIS** | Lead → Evan | `winner_summary.json` MUST carry `commission_bps` field. Confirm the tournament basis BEFORE writing (5 bps matches Sample if no domain reason to deviate; XLE is liquid so 5 bps is reasonable). Do not silently default. |

Items NOT binding for this pair (legacy-pair retro-applies, not new-build): BL-VIZ-O1-LEGACY, BL-VIZ-CHART-PREFIX-LEGACY, BL-LEGACY-WINNER-SUMMARY-SHAPE, BL-THRESHOLD-VALUE-SCHEMA, BL-BROKER-CSV-LEGACY, BL-CHART-GAPS-LEGACY, BL-PERMIT-CHARTS-EXCEPTION, BL-DUP-1 (display_names — already wired into pair_registry), BL-DUP-13/14 (Sample-page hygiene).

---

## 3. Acceptance gate (GATE-CMP1)

The pair must pass producer-side completeness validation before Lead ratifies.

```bash
python3 scripts/gate_pair_completeness.py crude_oil_xle
```

Exit code 0 (no FAIL checks) is required. Exit code 1 blocks ratification.

If a documented exception applies (none currently anticipated for this pair), use:

```bash
python3 scripts/gate_pair_completeness.py crude_oil_xle \
  --allow-partial \
  --partial-reason "BL-<ID>: <human-readable justification>"
```

An exception requires a matching `BL-*-EXCEPTION` row in `docs/backlog.md`. Do not use `--allow-partial` to silence legitimate drift.

**Cross-check before declaring complete:**
- All mandatory artifacts in `results/crude_oil_xle/` (interpretation_metadata, winner_summary, evidence_status, signal_scope, winner_trade_log, winner_trades_broker_style, plus glob matches).
- All mandatory charts in `output/charts/crude_oil_xle/plotly/` (hero, regime_stats, equity_curves, drawdown, walk_forward, tournament_scatter, subperiod_sharpe, rolling_correlation, structural_break, plus 4 crisis-episode zooms: dotcom, gfc, covid, inflation_2022).
- Pair config at `app/pair_configs/crude_oil_xle_config.py` per DPS standard.
- Glossary entries for any new technical terms (contango/backwardation if discussed, refining-margin proxy, energy sector beta).

---

## 4. Work-mode recommendation (LEAD-WM1)

**Recommended mode: Mode 1 (multiple makers, single checker).**

**Reasoning:**
- **Novelty.** Energy is a fresh category for this team (no prior energy pair completed). Evan should think hard about WTI frequency handling and structural-break treatment — a Mode-1 dispatch surfaces those design questions properly.
- **SOP-rule risk.** High. This is the FIRST pair built under LEAD-NPB1 + GATE-CMP1; multiple SOP edges will get exercised at once. Mode 1's agent-level reflection produces the rule-refinement signal we want.
- **Verification value.** User explicitly chose `crude_oil_xle` to **verify the LEAD-NPB1 + GATE-CMP1 + prospective_pairs.csv-as-SSoT changes from `fix260602_pair4_prep`.** The verification needs every layer of the new discipline to fire under realistic conditions. Mode 1 is the realistic case.
- **Benchmark status.** Not flagged as Sample / external deliverable.

**User override available** — if you want Mode 2 (Lead wears all hats sequentially with checker dispatch at the end), say so at SOD; I'll comply and document the choice.

---

## 5. Scope note — single target only

Unlike `us10y_us3m` (Done-Y for 7 sector ETFs), `crude_oil` has exactly ONE Done-Y target in the source CSV: XLE. No per-sector follow-up pairs are in scope from this pair's completion. (Other crude-related sector pairs exist as separate indicators — e.g. `wttstus1` (crude inventory) → SPY appears in the catalog under a different `pair_id`.)

---

## 6. Dispatch checklist (Lead's order of operations)

When ready to start this pair:

- [ ] Confirm pair identity + Pre-master row 2 details unchanged.
- [ ] SOD conversation with user — work-mode decision recorded in `docs/pair_execution_history.md`.
- [ ] Dana dispatch — pull `WCOILWTICO` from FRED, weekly, full history (1986-01 → latest). Resolve daily-vs-weekly alignment with XLE at the brief; flag at dispatch which side resamples. Dictionary entry.
- [ ] Evan dispatch — analysis brief specifying:
  - Stationarity choice (level vs RoC vs log-return vs rolling z-score)
  - Tournament categories (return-based, momentum, mean-reversion, regime-switching given the structural breaks)
  - Granger causality at 5d / 10d / 20d lags
  - Use `scripts.tournament.select_winner` (BL-DUP-11)
  - Use `scripts._stamp.iso_utc_now` (BL-DUP-15)
  - Emit `signal_scope.json` (BL-002), `analyst_suggestions.json` (BL-003), `commission_bps` (BL-COMMISSION-BASIS)
- [ ] Vera dispatch — 10-chart set, use `scripts._nber.add_nber_shading` (BL-DUP-4), 4 crisis-episode zooms (DPS-EP1). Special attention to the 2020 negative-price episode and 2022 invasion spike — these are not NBER recessions but ARE crude-specific shocks; flag if zoom set should be augmented.
- [ ] Ray dispatch — narrative markdown at `docs/portal_narrative_crude_oil_xle.md`, including ELI5 and 4 crisis-episode narratives.
- [ ] Ace dispatch — pair_config + 4 thin-wrapper pages. ZERO `st.markdown()` in pages (BL-004). Use `oos_max_drawdown` key (BL-801).
- [ ] Quincy dispatch — 15-item completeness gate + GATE-CMP1 + cloud verify.
- [ ] Lead ratification — GATE-CMP1 clean run + cloud-DOM verify on production URL + memory updates.
- [ ] **Verification debrief** — after pair ratifies, document which LEAD-NPB1 / GATE-CMP1 / prospective_pairs.csv-as-SSoT mechanisms fired correctly vs which need refinement. This pair is the validation case for the `fix260602_pair4_prep` branch.

---

*Brief authored under LEAD-NPB1 (binding, every new pair at Phase 0). When pair ratifies, copy lessons-learned into `[[lessons_crude_oil_xle]]` auto-memory.*
