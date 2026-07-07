# Spec Memo — GH #13 Lead-Coherence Rollout (11 pairs)

**Date:** 2026-07-07 · **Branch:** `feat260707_lead_coherence_rollout` · **Owner:** Lesandro
**Closes:** GH #13 (rollout portion) · **Reference impl:** `cass_freight_spy` (main, commits `b696791c` + `37d73810`)

---

## 1. Objective

On each pair page the reader flows *Evidence (lead tournament) → Strategy*. The
`lead_sharpe_distribution` chart shows the **cross-signal envelope** (best OOS Sharpe of *any*
signal at each lead), so the tallest bar draws the eye — but the **published winner** is a
specific combo chosen on risk-adjusted + robustness + tie-break criteria, so its lead
systematically need not sit on the envelope peak. Reading order makes the report look
self-contradictory. GH #13 fixes the *presentation*, never the frozen winner.

**Scope of this memo:** retro-apply the cass pilot pattern to the **11 remaining diverging
pairs**. `cass_freight_spy` (pilot) and the 2 matching pairs (`permit_spy`, `t10y3m_spy`) are
out of scope.

| Class | Pairs | Winner lead → tournament peak L\* |
|---|---|---|
| **A — daily, different axis (4)** | gold_copper_xli, hy_ig_spy, vix_vix3m_spy, phlxsox_spy | L0→L\*17, L0→L\*50, L0→L\*16, L63→L\*36 (L\* from **weekly** diagnostic sweep) |
| **B — monthly, genuine divergence (7)** | indpro_spy, ism_services_spy, umcsent_xlv, indpro_xlp, petrol_inv_spy, busloans_spy, m2sl_yoy_spy | L4→12, L3→9, L6→11, L11→8, L12→10, L6→5, L2→1 |

*(All 14 leads/L\* values in GH #13 were verified against on-disk artifacts on 2026-07-07.)*

---

## 2. Reference implementation = the per-pair work unit

The cass pilot delivered five things per pair. This memo generalizes them:

1. **Two new artifacts** in `results/{pair}/`:
   - `lead_winner_curve_{date}.csv` — the **fixed winner combo's own** OOS-Sharpe-by-lead curve (peaks at/near the winner's lead). Columns: `lead_months, oos_sharpe, is_published_winner`.
   - `lead_clean_envelope_{date}.csv` — cross-signal envelope with clean/raw split. Columns: `lead_months, best_oos_sharpe, best_signal, best_is_clean, best_clean_oos_sharpe, best_clean_signal`.
2. **Manifest patch** (`lead_sweep_manifest_{date}.json`): add `L_star`, `winner_curve_file`, `clean_envelope_file`, `best_clean_oos_sharpe_at_grid(_signal)`, and corrected `assertions[]`.
3. **Chart regen** (`output/charts/{pair}/plotly/lead_sharpe_distribution.json` + `_meta.json`): overlay the winner curve as the **primary** series, fade the envelope to context, mark the winner explicitly.
4. **Narrative framing** in `app/pair_configs/{pair}_config.py`: the "tallest bar is not the winner — by design" sentence *before* the chart.
5. **Class A only:** label the weekly/monthly sweep a **diagnostic**, distinct from the traded (daily/L0) latency.

---

## 3. Readiness — all 11 start at zero

Measured 2026-07-07: **none** of the 11 have a coherent manifest, winner-curve, or
clean-envelope. There is no partial-credit tier — every pair needs the full treatment.

| Precondition (present today) | Status |
|---|---|
| `winner_summary.json` (frozen winner combo) | ✅ all 11 |
| `lead_tournament_{date}.csv` (best-per-lead) | ✅ all 11 |
| `pair_pipeline_{pair}.py` (per-pair signal logic) | ✅ all 11 |
| Weekly diagnostic manifest (Class A) | ✅ all 4 Class A |
| `lead_winner_curve` / `lead_clean_envelope` | ❌ 0/11 |
| Coherent manifest fields | ❌ 0/11 |

**Critical data-generation finding.** The two new artifacts are **NOT derivable from on-disk
CSVs.** `lead_tournament_*.csv` stores only the single best combo per lead; the winner-curve
needs the *fixed winner combo* re-scored across the whole lead grid, and the clean-envelope
needs *every signal's* per-lead Sharpe. `lead_horizon_sweep.py` produces `lead_tournament`, not
these. → **each artifact requires re-scoring via the pair's `pair_pipeline` module.**

**Simplification finding.** `seasonally_contaminated_signals` is **empty for all 11** — the
seasonal-exclusion story is cass-specific (Cass is NSA). Therefore for every one of the 11:
- `best_clean == best_raw` → the clean-envelope collapses to the raw envelope (still emit the
  columns for schema parity, but `best_is_clean` is all-True).
- GH #13 **point 4 (provenance "clean-max not raw-max" correction) does not apply.**
- Narrative framing is the **general** "selected for reliability, not the single highest score"
  version — *not* cass's seasonal-exclusion wording.

---

## 4. Work breakdown

### Phase 0 — Build the reusable generator (one-time; the backbone)
`scripts/refresh_lead_coherence_artifacts.py <pair> [--weekly]`, generalizing what cass's build
did and following the `refresh_umcsent_winner_artifacts.py` import-the-pipeline pattern:
1. Load frozen winner combo from `winner_summary.json` (never re-selects).
2. Import `pair_pipeline_{pair}` and re-score **the winner combo** across the lead grid → `lead_winner_curve`.
3. Re-score the **full signal set** across the grid; compute raw + clean best → `lead_clean_envelope` (clean==raw for these 11).
4. Compute `L_star` = argmax of the envelope; patch the manifest fields + assertions.
5. Emit deterministic, frozen-safe output (idempotent; byte-stable when re-run).
- **Validate against cass:** running it on `cass_freight_spy` must reproduce the committed cass CSVs (minus the seasonal split). This is the acceptance gate for Phase 0.

### Phase 1 — Per-pair artifact regen (×11)
Run the Phase-0 tool per pair (Class A also `--weekly` for the diagnostic curve). Schema-validate
each new manifest/CSV against `docs/schemas/`.

### Phase 2 — Chart regen (×11)
Via `scripts/generate_lead_charts.py` (extend if needed) — winner curve primary, envelope faded,
winner marked. Emit `_meta.json` with the coherent-view flag.

### Phase 3 — Narrative framing (×11, pair-specific)
Add the framing sentence to each `{pair}_config.py`. **Not boilerplate** — each pair's "why the
winner is off-peak" must name that pair's real selection reason (robustness / tie-break / vol
target), grounded in its `selection` block. Class A additionally gets the diagnostic-sweep label.

### Phase 4 — Codify the SOP
Add a **VIZ-LEAD** rule (chart: winner-curve overlay mandatory when winner lead ≠ L\*) and a
**narrative** rule (framing sentence required) to `docs/agent-sops/lead-agent-sop.md` +
`docs/agent-sops/visualization-agent-sop.md`, so future pairs comply by construction.

### Phase 5 — Verify & close
Per pair: (1) local `jsonschema`; (2) cloud DOM render via `scripts/cloud_verify.py` on the
dawodev preview (repoint it to this branch first — see CLAUDE.md). Then close GH #13 with the
per-pair evidence table.

---

## 5. Sequencing

1. **Phase 0 + one Class B pair as the rollout-pilot** — recommend **`indpro_spy`** (largest
   divergence, Δ8 months, L4→12; the most visually jarring, so the best stress test of the
   overlay). Proves the generalized tool end-to-end before batching.
2. **Batch remaining Class B** (6): ism, umcsent, indpro_xlp, petrol, busloans, m2sl.
3. **Class A** (4): gold_copper, hy_ig, vix, phlxsox — last, because they add the weekly-diagnostic
   framing wrinkle on top of the common pattern.
4. **Phase 4 SOP + Phase 5 close.**

Divergence magnitude (Class B, for prioritizing narrative care):
`indpro Δ8 > ism Δ6 > umcsent Δ5 > indpro_xlp Δ3 > petrol Δ2 > busloans Δ1 ≈ m2sl Δ1`.

---

## 6. Effort & risk

- **Dominant cost is Phase 0** (the generalized re-scoring tool). After that, per-pair is
  run-tool + pair-specific narrative + verify — mechanical, parallelizable across the viz/lead agents.
- **Risk — frozen-winner safety:** the tool must re-score, never re-select. Guard: assert the
  winner-curve's `is_published_winner` row equals `winner_summary.json` exactly; fail loud otherwise.
- **Risk — cloud-sync lag (META-FRD):** verify against the correct preview branch/commit; reboot,
  not just push. Confirm "Last deploy" SHA before declaring any render verified.
- **Risk — Class A units confusion:** the diagnostic L\* lives in the *weekly* manifest; keep the
  traded latency (daily/L0) and the diagnostic sweep visually and textually distinct.

## 7. Open decisions for the user

1. **Build now or approve scope first?** This memo assumes I build Phase 0 next.
2. **Rollout-pilot pair** — I recommend `indpro_spy`; confirm or substitute.
3. **Agent fan-out** — batch Phases 1–3 across the viz/lead agent team (parallel) vs. sequential
   by me. Fan-out is faster; sequential keeps tighter narrative control.
4. **Preview branch** — OK to repoint the dawodev preview to `feat260707_lead_coherence_rollout`
   for cloud verification?
