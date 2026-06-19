# Pair Pre-Screening — Design Proposal (exploration)

**Status:** Exploratory / for discussion. Thresholds are illustrative and **not yet calibrated** (per stakeholder: "篩選條件同 benchmark 都未成熟"). Does not change the current dev-team workflow until adopted.

**Origin:** Stakeholder proposal (2026-06-19) — add a lightweight **Pair Screening** layer *before* full Dashboard Development, so pairs with limited practical value or poor operational feasibility don't consume the full dashboard + deep-QC cycle.

---

## 1. The problem it solves

The original plan was: build one high-quality dashboard template (HY-IG), then replicate cheaply to other pairs. In practice every pair has its own story/evidence/strategy character, so each needs deep QC — checking Story↔Evidence↔Strategy↔Methodology consistency, whether the Rank-1 strategy logically connects to the other sections, whether the analysis is persuasive, and whether the economic logic holds. That QC is expensive and runs *after* the full build.

**Insight:** most of the information needed to decide "is this pair worth a full build?" is **already produced by the Data (Dana) and Econ (Evan) stages** — i.e. *before* the expensive Charts → Narrative → Portal → deep-QC stages. A screen placed there can park weak pairs early.

## 2. Where it sits in the workflow

```
Phase-0 (source check) → Dana (data) → Evan (econ + tournament)
        │
        ▼
   ┌──────────────────────┐
   │  PRE-SCREEN GATE      │  ← NEW. Uses ONLY Dana+Evan artifacts (≈half the build cost).
   └──────────────────────┘
        │
   PROCEED │ CONDITIONAL          DEFER / DROP
        ▼                              │
 Vera+Ray (charts+narrative)          └─► park in a screened-pairs register;
        → Ace (portal) → deep QC            no dashboard, no deep QC
```

The screen is **cheap** because it consumes artifacts the pipeline already emits; it adds no new heavy computation. It is a **gate**, not a new producer.

## 3. The four dimensions → concrete metrics (all from existing artifacts)

The stakeholder named four dimensions. Each maps to fields we already write:

### D1 — Strategy Performance  *(source: `results/<pair>/winner_summary.json`)*
- OOS Sharpe (absolute) and **uplift vs buy & hold** (`oos_sharpe − bh_sharpe`)
- Drawdown improvement vs B&H (`oos_max_drawdown` vs `bh_max_drawdown`)
- Trade count (`oos_n_trades`) — too few → fragile/overfit; too many → cost drag
- Annual turnover (`annual_turnover`)
- *(Extension, already done for phlxsox):* does it beat a **naive own-momentum benchmark** of the target, not just B&H? Guards against "leveraged-beta dressed as alpha."

### D2 — Operational Practicality  *(source: Dana handoff / data sidecar)*
- **Data availability & freshness** — live API (FRED/Yahoo) vs offline snapshot; how stale is the source?
- **Release lag** — `days_since_release` / the real-time lead floor. Can the signal actually be traded when it fires, with no look-ahead?
- **Execution feasibility** — turnover and trade frequency relative to the lead horizon.

### D3 — Crisis Validation  *(source: `results/<pair>/subperiod_sharpe.csv`)*
- Strategy behaviour across crisis episodes (Dot-Com 2000-02, GFC 2008-09, COVID 2020, 2022 rates shock): did it protect / profit, or lose?
- **Count of crises where it added value vs lost.** (Example caught this session: phlxsox "lost in every pre-OOS crisis" — a screen would flag it.)

### D4 — Durability  *(source: `evidence_status.json` + tournament stats)*
- **IS-vs-OOS Sharpe gap** — a large positive gap (e.g. IS 0.10 vs OOS 1.57 on phlxsox) flags a regime-lucky window, not a stable effect.
- **Bootstrap p-value** — statistical significance of the winner.
- **Median valid-combo Sharpe vs B&H** — is the winner a lone outlier in a sea of losing combos? (If the median combo underperforms B&H, the search mostly found noise.)
- **`evidence_status` durability verdict** — `durable` / `conditionally_durable` / `episode_concentrated`; and `found_in_search` vs `validated`.

## 4. Scorecard & verdict

Each dimension scores **Green / Amber / Red** against (to-be-calibrated) thresholds. Aggregate verdict:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **PROCEED** | Strong performance, durable, crisis-validated, operationally practical | Full dashboard build + deep QC |
| **CONDITIONAL** | Real but caveated (e.g. drawdown control yet `found_in_search`) | Build, but pre-commit to foregrounding the weak dimension in the narrative |
| **DEFER / DROP** | Fails performance OR durability OR operational practicality | Park in the screened register; no dashboard, no deep QC |

The screen does **not** replace deep QC — it decides *whether* a pair earns deep QC. Economic-logic / explainability / consistency review stays in the dashboard cycle for PROCEED/CONDITIONAL pairs.

## 5. Illustrative thresholds (NOT calibrated — for discussion)

These are first-cut, to be tuned against the existing 13 live pairs + stakeholder risk appetite:

- D1: OOS Sharpe ≥ 1.0 **and** uplift vs B&H ≥ +0.3 **and** beats own-momentum benchmark **and** 10 ≤ trades ≤ (cost-reasonable cap). Drawdown improvement vs B&H > 0.
- D2: source is live/refreshable **and** real-time-tradable (no look-ahead) **and** turnover operationally sane.
- D3: added value in ≥ half of testable crises, and no catastrophic crisis loss.
- D4: IS-vs-OOS gap not extreme; bootstrap p < 0.10; winner clearly above the median combo; durability ≠ `episode_concentrated`-only.

## 6. Open questions / known gaps

1. **Thresholds need calibration** — run the screen on the 13 live pairs, eyeball where it puts known-strong vs known-marginal, tune with the stakeholder.
2. **Artifact-completeness gaps** — 7 legacy pairs have `bh_sharpe: null` (uplift not computable) and only the recent DPS-FE2 pairs carry `evidence_status.json`. The screen must degrade gracefully (score "insufficient data" rather than fail) and this argues for back-filling those fields (separate issue).
3. **Crisis-validation rigor** — `subperiod_sharpe.csv` episode coverage varies by pair; need a consistent crisis set + minimum-observation guard.
4. **Own-momentum benchmark** — only computed for phlxsox so far; generalizing it to all pairs is a small Evan extension that materially strengthens D1.
5. **Granularity link (Option D)** — the stakeholder leans Weekly+Monthly. The screen is granularity-agnostic but D2 (release lag / tradability) interacts with frequency; worth aligning once Option D lands.

## 7. POC validation findings (run on the 13 live pairs)

A POC scorecard (`scripts/pair_prescreen.py`) was run against the existing `results/` artifacts. With *first-cut illustrative thresholds*, it produced a believable separation that **matched independent qualitative reads**:

- **DEFER/DROP** flagged for genuine reasons: `ism_services_spy` (D4 — in-sample Sharpe −0.11 → OOS 1.54, i.e. regime-lucky), `phlxsox_spy` / `gold_copper_xli` / `vix_vix3m_spy` (D2 — operationally high turnover, 16–23×/yr).
- **CONDITIONAL** for the solid-but-caveated middle (`busloans_spy` strongest: Sharpe 1.50, +0.61 uplift vs B&H, −1.0% DD vs −23.9%, COVID Sharpe 2.75, turnover 2.9).

**Two systemic findings the screen exposed (more valuable than the per-pair verdicts):**
1. **No pair reaches PROCEED.** Every recent pair is `found_in_search` (no holdout final exam), so D4 durability caps at Amber fleet-wide. A true "PROCEED" requires the **ECON-FE1 final-exam (holdout)** step that doesn't yet exist in the pipeline. The screen makes the "everything is search-phase" reality unmissable.
2. **Every pair shows a large IS→OOS Sharpe gap** (winner in-sample Sharpe ≪ OOS Sharpe). This is structural: the tournament selects on OOS, so the winner's OOS number is upward-biased relative to in-sample. The screen should treat the *gap* (not the OOS level alone) as the durability signal — a small/negative IS Sharpe beside a large OOS is the regime-luck red flag.

**Calibration lesson (validates the stakeholder's "criteria not mature" caveat):** the first threshold set was far too harsh (it dropped `busloans_spy`, a clearly strong pair) — D4 wrongly penalized "median combo < B&H" (normal: most random combos underperform) and over-penalized `found_in_search` to Red. The plumbing is sound; the thresholds are where the human/stakeholder calibration work lives.

## 8. Proposed next step

Build a **POC scorecard** (`scripts/pair_prescreen.py`) that reads the existing `results/<pair>/` artifacts and emits the four-dimension RAG scorecard + verdict for every pair, then run it across the 13 live pairs as a **validation/calibration exercise** — does the screen separate the keepers from the marginal? Iterate thresholds with the stakeholder before wiring it into the workflow.
