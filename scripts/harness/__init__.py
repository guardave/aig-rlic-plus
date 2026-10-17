"""Phase B shared tournament harness (design: _pws/lead-lesandro/pkg14_phaseB/PHASE_B_PLAN.md section 1).

A pair pipeline declares a `PairSpec` (signals, thresholds, grid, timing) and calls `run.run_pair`; everything
else (alignment, candidate manifest, positions, scoring, D9 plateau selection, null tournament, bootstrap,
artifacts) is shared and unit-tested here.

Tracks (plan section 0):
  * real_time  (MAIN when the series has an ALFRED archive): each rebalance uses the vintage published when the
    return window opens; signal and rolling threshold are computed inside that vintage.
  * revised    (COMPARISON, hindsight): today's revised values with point-in-time release timing (as-of shift).
  * market / no-archive pairs run one track (revised values or unrevised market data) labelled MAIN.
"""
