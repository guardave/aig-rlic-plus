# Pair Brief — `us10y_us3m_spy` (Pair #4)

**Status:** scheduled — not yet started.
**Authored:** 2026-06-02 by Lead Lesandro.
**Rule:** [LEAD-NPB1](../../../docs/agent-sops/lead-agent-sop.md) New-Pair Brief Discipline.

---

## 1. Pair identity (LEAD-DV1)

| Field | Value |
|---|---|
| **`pair_id`** | `us10y_us3m_spy` |
| **Indicator → target** | 10Y−3M Treasury Spread → SPY |
| **Source CSV row** | `data/prospective_pairs.csv` line 63 (also XLP, XLE, XLI, XLY, XLK, XLF, XLV — 7 targets total; this brief covers SPY only — see §5) |
| **Source CSV ticker** | `G - (US10Y-US3M)` |
| **Indicator category** | rates |
| **Pre-master row 2** | col 72, sheet `US10Y-3M` col B — "10-Year Treasury Constant Maturity Minus 3-Month Treasury Constant Maturity, Units: Percent, Not Seasonally Adjusted, Daily, 18 Nov 2020 – 17 Nov 2025, from FRED" |
| **FRED series** | `T10Y3M` (verify with Dana at first dispatch) |
| **Frequency** | Daily |
| **Units** | Percent (spread, can go negative — inversion is the leading-recession signal) |
| **SA** | NSA |

**Domain notes (Lesandro):**
- The 10Y−3M term-premium spread is the canonical leading-recession indicator (Estrella & Mishkin, 1998; NY Fed yield-curve recession model). Inversion (negative spread) typically precedes recessions by 6–18 months.
- For SPY: pro-cyclical via the growth-expectation channel, but the *level* of the spread is noisy. The signal-rich transformation is **inversion duration** and **months-since-uninverted**, not the raw level.
- Two econometric pitfalls to flag for Evan:
  1. The spread is mean-reverting around 0; raw z-scores will saturate at the tails.
  2. The "leading window" varies across cycles (6m for 2007, 18m for 2000). Static lag specification (L0 / L6 / L12) will under-fit; ECON catalog's distributed-lag specification or rolling-Granger is more appropriate.

---

## 2. Active backlog items binding this pair

The following deferred backlog items name "next pair" / "Pair #4 start" / "new pair start" in their reactivation trigger. They bind `us10y_us3m_spy` from the first dispatch.

| BL-ID | Owner | What this pair must do |
|---|---|---|
| **BL-002** | Quincy → Evan | Emit `results/us10y_us3m_spy/signal_scope.json` per ECON-UD. Universe-disclosure JSON must list every candidate strategy considered, not just the winner. |
| **BL-003** | Quincy → Evan | Emit `results/us10y_us3m_spy/analyst_suggestions.json` per ECON-AS. If no suggestions exist at pipeline-end, emit a placeholder `{"suggestions": []}` with the schema; do not omit the file. |
| **BL-004** | Lead → Ace | APP-NP1 page-prose discipline. **`app/pages/N_us10y_us3m_spy_*.py` files must contain ZERO `st.markdown()` calls.** All prose sources from `docs/portal_narrative_us10y_us3m_spy.md` (Ray) via `app/pair_configs/us10y_us3m_spy_config.py` (Ace). Page files are pure template wrappers. |
| **BL-801** | Lead → Ace | winner_summary consumer key discipline. **No `winner.get("max_drawdown", <hardcoded_fallback>)` patterns.** Use `winner.get("oos_max_drawdown", winner.get("max_drawdown"))` exactly, matching `app/components/page_templates.py:548`. Hardcoded numeric fallbacks are forbidden. |
| **BL-APP-PT1-LEGACY** | Lead → Ace | All four pages (`_story`, `_evidence`, `_strategy`, `_methodology`) MUST be thin APP-PT1 wrappers calling `render_<page>_page()`. NOT hand-written. Page file body is ≤10 lines (sys.path shim + import + one template call). |
| **BL-DUP-11** | Lead → Evan | Pipeline tournament-winner selection uses `from scripts.tournament import select_winner` instead of inline `df[df["valid"] & ...].loc[idxmax("oos_sharpe")]`. The helper exists; new pipelines should not re-introduce the pattern. |
| **BL-DUP-15** | Lead → Evan | Pipeline run-stamps use `from scripts._stamp import iso_utc_now`. No `datetime.utcnow()` or hand-formatted `now(timezone.utc).strftime(...)`. |
| **BL-DUP-4** | Lead → Vera | Chart generators that need NBER recession shading use `from scripts._nber import add_nber_shading, RECESSIONS`. No inline `RECESSIONS = [...]` tuples. |
| **BL-COMMISSION-BASIS** | Lead → Evan | `winner_summary.json` MUST carry `commission_bps` field. Confirm the tournament basis BEFORE writing (5 bps matches Sample if no domain reason to deviate). Do not silently default. |

Items NOT binding for this pair (legacy-pair retro-applies, not new-build): BL-VIZ-O1-LEGACY, BL-VIZ-CHART-PREFIX-LEGACY, BL-LEGACY-WINNER-SUMMARY-SHAPE, BL-THRESHOLD-VALUE-SCHEMA, BL-BROKER-CSV-LEGACY, BL-CHART-GAPS-LEGACY, BL-PERMIT-CHARTS-EXCEPTION, BL-DUP-1 (display_names — already wired into pair_registry), BL-DUP-13/14 (Sample-page hygiene).

---

## 3. Acceptance gate (GATE-CMP1)

The pair must pass producer-side completeness validation before Lead ratifies.

```bash
python3 scripts/gate_pair_completeness.py us10y_us3m_spy
```

Exit code 0 (no FAIL checks) is required. Exit code 1 blocks ratification.

If a documented exception applies (none currently anticipated for this pair), use:

```bash
python3 scripts/gate_pair_completeness.py us10y_us3m_spy \
  --allow-partial \
  --partial-reason "BL-<ID>: <human-readable justification>"
```

An exception requires a matching `BL-*-EXCEPTION` row in `docs/backlog.md`. Do not use `--allow-partial` to silence legitimate drift.

**Cross-check before declaring complete:**
- All mandatory artifacts in `results/us10y_us3m_spy/` (interpretation_metadata, winner_summary, evidence_status, signal_scope, winner_trade_log, winner_trades_broker_style, plus glob matches).
- All mandatory charts in `output/charts/us10y_us3m_spy/plotly/` (hero, regime_stats, equity_curves, drawdown, walk_forward, tournament_scatter, subperiod_sharpe, rolling_correlation, structural_break, plus 4 crisis-episode zooms: dotcom, gfc, covid, inflation_2022).
- Pair config at `app/pair_configs/us10y_us3m_spy_config.py` per DPS standard.
- Glossary entries for any new technical terms (yield-curve inversion, term premium, recession-probability model).

---

## 4. Work-mode recommendation (LEAD-WM1)

**Recommended mode: Mode 1 (multiple makers, single checker).**

**Reasoning:**
- **Novelty.** Rates is an established category (TED variants, though archived, exercised it). But the 10Y−3M curve has its own econometric playbook (yield-curve recession model, distributed lags, inversion-duration signal) that is NEW to this team. Evan needs to think hard about method selection; Mode 1's agent reflection is the right surface.
- **SOP-rule risk.** Likely. This pair will exercise the new GATE-CMP1 gate for the first time on a freshly-built pair, BL-004's first new-pair test, and the first pipeline using `scripts/tournament.py::select_winner` end-to-end. Several SOP edges will get tested; agent-level reflection is how the rules get refined.
- **Benchmark status.** Not flagged as Sample / external deliverable. But the *first new pair built under LEAD-NPB1* — meta-quality matters.

**User override available** — if you want Mode 2 (Lead wears all hats sequentially with checker dispatch at the end), say so at SOD; I'll comply and document the choice.

---

## 5. Scope note — single target first

`us10y_us3m` appears Done-Y for 7 sector ETFs in the source CSV (SPY, XLP, XLE, XLI, XLY, XLK, XLF, XLV). This brief covers SPY only — the canonical first build. Sector variants come AFTER `us10y_us3m_spy` ratifies, as separate per-sector pair briefs (each a thin override of this one). Do not bundle the 7 in one pipeline; the per-pair brief discipline is the unit.

---

## 6. Dispatch checklist (Lead's order of operations)

When ready to start this pair:

- [ ] Confirm pair identity + Pre-master row 2 details unchanged.
- [ ] SOD conversation with user — work-mode decision recorded in `docs/pair_execution_history.md`.
- [ ] Dana dispatch — pull T10Y3M from FRED, daily, full history. Dictionary entry.
- [ ] Evan dispatch — analysis brief specifying:
  - Distributed-lag specification candidates
  - Inversion-duration signal construction
  - Tournament categories (level, lagged level, inversion duration, months-since-uninverted, rolling z-score)
  - Use `scripts.tournament.select_winner` (BL-DUP-11)
  - Use `scripts._stamp.iso_utc_now` (BL-DUP-15)
  - Emit `signal_scope.json` (BL-002), `analyst_suggestions.json` (BL-003), `commission_bps` (BL-COMMISSION-BASIS)
- [ ] Vera dispatch — 10-chart set, use `scripts._nber.add_nber_shading` (BL-DUP-4), 4 crisis-episode zooms (DPS-EP1).
- [ ] Ray dispatch — narrative markdown at `docs/portal_narrative_us10y_us3m_spy.md`, including ELI5 and 4 crisis-episode narratives.
- [ ] Ace dispatch — pair_config + 4 thin-wrapper pages. ZERO `st.markdown()` in pages (BL-004). Use `oos_max_drawdown` key (BL-801).
- [ ] Quincy dispatch — 15-item completeness gate + GATE-CMP1 + cloud verify.
- [ ] Lead ratification — GATE-CMP1 clean run + cloud-DOM verify on production URL + memory updates.

---

*Brief authored under LEAD-NPB1 (binding, every new pair at Phase 0). When pair ratifies, copy lessons-learned into `[[lessons_pair4_us10y_us3m_spy]]` auto-memory.*
