# Chart Regression Note — indpro_xlp — 2026-06-20

**Author:** Vera (Visualization agent)
**Branch:** `fix260620_lead_horizon`
**Trigger:** ECON-LT1 lead-horizon re-run changed the tournament winner. Charts derived
from the winner / canonical strategy-returns series must be regenerated.

## Winner change (upstream, Evan)

| Field | Prior (published) | New (20260620) |
|-------|-------------------|----------------|
| Signal | S8_accel (Acceleration) | **S3_mom (INDPRO 1-month momentum)** |
| Threshold | T2_roll_p75 | **T1_fixed_p50** |
| Strategy | P3_long_short_counter | **P1_long_cash (pro-cyclical)** |
| Lead | L3 | **L11** |
| OOS Sharpe | 1.1147 | **1.3282** |
| OOS max drawdown | -13.5% | **-6.3%** |

Source of truth: `results/indpro_xlp/strategy_returns_20260620.csv` (+ `_meta.json`,
ECON-SR1 reconciled) and `results/indpro_xlp/winner_summary.json`.

## Charts Changed

Regenerated via `scripts/generate_strategy_perf_charts.py indpro_xlp` (ECON-SR1
canonical consumer — reads the latest `strategy_returns_*.csv`, never re-derives
positions from signals):

- `equity_curves`
- `drawdown`
- `walk_forward`
- `subperiod_sharpe`

## Spec Diff

| Chart | Field | Old → New |
|-------|-------|-----------|
| equity_curves | strategy trace label | "Strategy: Acceleration Long/Short" → "Strategy: INDPRO 1-month momentum Long/Cash" |
| equity_curves | winner final cumret (OOS) | 2.53 → **2.12** (BH unchanged 1.85) |
| drawdown | winner max drawdown | -13.3% → **-6.3%** |
| walk_forward | reported-OOS-Sharpe reference line | 1.11 → **1.33** |
| subperiod_sharpe | Full-OOS Sharpe + per-episode bars | recomputed from regenerated `subperiod_sharpe.csv` (Jun-20) |

All four reconcile to `winner_summary.json` within ECON-SR1 tolerance
(Sharpe 1.3282, max DD -6.3%, ann ret 11.1%). Palette `okabe_ito_2026`,
NBER shading, VIZ-IC1 pre-save assertions all PASS.

## Winner-INDEPENDENT charts (correctly left untouched)

Descriptive / model charts do not depend on the winner and were NOT regenerated:
`hero`, `correlations`, `ccf`, `regime_stats`, `rolling_sharpe` (benchmark-only —
shows Buy & Hold XLP, no strategy trace), `rolling_correlation`, `rolling_granger`,
`structural_break`, `history_zoom_*`.

## Outstanding (NOT regenerated this pass — escalated to Lead)

Three winner-DEPENDENT, portal-consumed charts are NOT produced by the canonical
ECON-SR1 generator and remain STALE (still encode the displaced S8_accel winner):

- `rolling_sharpe_cp` — "Rolling 24-Month Strategy Sharpe" (re-simulates winner)
- `signal_dist` — titled "INDPRO **Acceleration** Signal Distribution"; new winner
  signal is `indpro_mom`, so the histogrammed signal is now WRONG
- `tournament_scatter` — Top-5 / winner marker reflects the old grid

Their only existing producer is the legacy `scripts/generate_charts_indpro_xlp.py`,
which is SUPERSEDED and DEFECTIVE (see Rationale). Regenerating them needs a
canonical, winner-consuming path — flagged to Lead, not hot-patched (META-NMF).

## Rationale

`scripts/generate_charts_indpro_xlp.py` (the legacy per-pair generator) must NOT be
run: it (a) hardcodes `DATE_TAG="20260420"` and reads the superseded tournament CSV;
(b) re-simulates the winner position from signal+threshold heuristics instead of
consuming the ECON-SR1 canonical series (the exact class of bug ECON-SR1 was created
to eliminate); (c) hardcodes `indpro_accel` in `signal_dist`; and (d) would clobber
the correct NBER/canonical `equity_curves.json` + `drawdown.json` regenerated here.
The ECON-SR1 consumer `generate_strategy_perf_charts.py` is the correct producer for
the strategy-performance charts.

## Approved By

Vera self-approved (winner change is upstream/Evan-driven, ECON-LT1). Flagged for
Lesandro review — esp. the three outstanding stale charts and the two SPY blockers
(see handoff note).

---

## Appendix — Systemic 3-chart pass (2026-06-21, ECON-SR3 sidecars)

Regenerated from Evan's gap sidecars (`gap_sidecars_indpro_xlp_meta.json`) via the
ECON-SR3 consumer-side twin (VIZ-SR3T), no re-simulation:

| Chart | Source sidecar | Old → New |
|-------|----------------|-----------|
| `rolling_sharpe_cp` | `rolling_sharpe_indpro_xlp.csv` | re-rendered off canonical strategy_return (reconciles OOS 1.3282) |
| `signal_dist` | `signal_dist_indpro_xlp.csv` | histogrammed column **indpro_accel → indpro_mom**; title "INDPRO Acceleration…" → "INDPRO 1-Month Momentum Signal Distribution"; x-axis fixed |
| `tournament_scatter` | `tournament_scatter_indpro_xlp.csv` | population = immutable coarse grid (3,331 / 2,691 valid); added labeled overlay "Winner (L11, extended grid)" at (turnover 5.57, Sharpe 1.3282) |

**Disposition correction:** `signal_dist` was mislabeled `consumed` at HEAD but is
referenced by no page/config — corrected to `suggested` + `exploratory: true` (VIZ-O1/E1).
Routing into the Methodology Exploratory section is flagged to Lead/Ace.

**Process note (no artifact impact):** an unguarded import of `viz_cp_retro_apply.py`
side-effect-reran all 10 pairs' CP charts; reverted via `git checkout` and re-ran the
intended work in isolation. Captured as the VIZ-SR3T "unguarded module import" caution.
