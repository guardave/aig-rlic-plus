# Superseded umcsent_xlv artifacts (retired 2026-10-17, Phase B B1)

Kept unchanged for audit. No app page, gate or pipeline reads them as current results.

- `lead_*_20260620.*`: the GH#13 lead-coherence artifacts derived from the pre-floor L0-12 tournament by
  `scripts/refresh_umcsent_xlv_lead_artifacts.py` (retired). They describe the OOS-selected winner
  S3_mom / T3_zscore_1.0 / P1 / L6 on a grid that included L0 with position.shift(1).
- The lead curve and stable lead range are now written by the harness: `lead_curve_20261017.csv`
  (as known at the time) and `hindsight_lead_curve_20261017.csv` (as revised today), charted as
  `lead_plateau`.
