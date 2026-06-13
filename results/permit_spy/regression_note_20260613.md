# permit_spy chart regression note — 2026-06-13 (VIZ-LEAD1 conformance)

Branch `fix260613_lead_horizon`. Vera regenerated the two lead-analysis charts for
consistency with the other 7 non-frozen pairs and to close the missing-registry /
missing-sidecar gap (vichua's original delivery).

## Charts Changed
- `lead_sharpe_distribution`
- `correlations_lead_view`

## Spec Diff

| Field | Old (vichua) | New (this wave) |
|-------|-------------|-----------------|
| sharpe traces | All valid combos (scatter), Best Sharpe per lead (bar), Buy & Hold | p25-p75 band, Median strip, Best Sharpe per lead (bar), Buy & Hold |
| sharpe bar values | from an earlier tournament run (e.g. L6=1.373) | re-read from `lead_tournament_20260613.csv` (L6=1.4454) — current authoritative source |
| sharpe max annotation | manual L6/L8-10 callouts | data-driven `max L{lead}` arrow + spike-vs-ridge caption |
| corr cell stars | present (RdBu_r, zmid=0) | present (RdBu_r, zmid=0) — shape preserved |
| _meta.json sidecar | ABSENT | added (disposition consumed, palette okabe_ito_2026, VIZ-LEAD1) |
| source note | absent | added |

## Rationale
The old `lead_sharpe_distribution` bar heights diverged from the current
`lead_tournament_20260613.csv` — Evan's authoritative artifact for this wave. The
regeneration re-reads numbers from that CSV at generation time (META-A2A: artifact is
source of truth) and standardizes the trace set across all 8 pairs (p25-p75 band +
median strip + best-bar + dashed B&H) per VIZ-LEAD1. The correlations heatmap shape was
already conformant; it was regenerated for uniform styling and to receive its missing
`_meta.json` sidecar and registry binding.

## Approved By
Vera self-approves under the Lead dispatch ("verify they conform to VIZ-LEAD1 and
regenerate only if needed for consistency; its main gap is the missing registry entry").
Flagged for Lesandro review: permit's old chart was stale vs the current tournament CSV.
