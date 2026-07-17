# Pilot 260717 — Lead-Grid Ceiling Test

**Question:** Does extending the monthly lead grid beyond L12 surface a signal the current `L0–12` cap hides? Motivated by stakeholder deck slide 53 (petroleum inventory claimed to lead SPX by 24–36 months) and issue #23 (the ceiling is convention, not justification).

**Pair:** `petrol_inv_spy` — the deck's strongest a-priori long-lead candidate.

**Verdict: the extension surfaces nothing.** The winner is unchanged at **L11, OOS Sharpe 1.5273**; no lead beyond L12 beats it. L24 is the single worst horizon on the grid (1.2003), L18 second-worst (1.2037). The long-lead top entries are degeneracies — large clusters pinned exactly at the buy-and-hold Sharpe 0.9315 (L18: 28, L24: 20, L36: 20 combos) plus P2-on-binary threshold-insensitive ties — not discoveries. Nothing approaches the incumbent, so the t>3.0 hurdle never engages. **The L0–12 ceiling is empirically justified for this pair.**

## Files

- `petrol_grid_ceiling_pilot_summary.pdf` — 1-page A4 executive summary (and `.png` preview).
- `petrol_tournament_L0-36_pilot260717.csv` — the full extended leaderboard (19,712 strategy rows, grid `L0–12 + {18,24,36}`). Evidence artifact; **not** a production tournament — kept out of `results/` on purpose so no loader/glob picks it up.
- `build_pilot260717_summary_pdf.py` (in `scripts/pilots/`) — rebuilds the PDF from the CSV; nothing hardcoded that the CSV derives.

## How to reproduce

The pilot changes exactly one line — `scripts/pair_pipeline_petrol_inv_spy.py`, the tournament grid:

```python
leads = list(range(0, 13)) + [18, 24, 36]   # pilot: ceiling extension
```

petrol's grid is self-contained in its own pipeline (unlike the monthly pairs that route through the shared `lead_horizon_sweep.py`), so this edit is isolated to the one pair. `main()` cannot be run to regenerate in place — the ECON-T5 §4 immutability guard in `_tournament_io.write_tournament` refuses to overwrite the frozen production tournament. The pilot was therefore run via an isolated harness that imports the pipeline's own `load_data` / `add_regime_signals` / `tournament` with output roots redirected to a scratchpad, so the scoring is exactly production (ECON-T4 deployable cash-fill confirmed: `oos_r = strat_ret[oos_mask].fillna(0.0)`). The committed CSV is that harness's output.

## Scope & caveats

- Tests the **tradable** long lead (Sharpe on the deployable series). A complete test of slide 53 would also check raw lead-lag predictability (correlation / Granger) at 24–36 months, which the tournament does not isolate.
- One pair is not dispositive. The grid **shape** question (dense contiguous vs sparse anchored — the other half of #23) is untested here. A second pair, `indpro_xlp` (winner at L11, hardest test), is under separate pilot.
