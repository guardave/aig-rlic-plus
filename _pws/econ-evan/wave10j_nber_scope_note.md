# NBER Shading Scope Note — Wave 10J
**From:** Econ Evan
**To:** Viz Vera
**Date:** 2026-04-24
**Subject:** Which ECON-CP output artifacts require NBER recession shading

---

## Ruling

| Artifact | NBER Shading Required? | Rationale |
|----------|----------------------|-----------|
| **Rolling 24M correlation** (`rolling_correlation_{pair_id}.csv`) | **Yes** | A rolling correlation chart is a time-series of signal stability. Knowing whether correlation reversals co-occur with recessions is central to interpreting whether they reflect genuine structural breaks or just macro-regime noise. Without shading, the reader cannot distinguish "signal weakened because of structural change" from "signal weakened because we were in a recession-phase where the mechanism is inherently different." |
| **Rolling 24M Sharpe** (`rolling_sharpe_{pair_id}.csv`, CP2 only) | **Yes** | Strategy performance through time is the primary artifact for communicating durability to a non-technical audience. Recession shading makes it immediately legible whether Sharpe spikes and collapses are concentrated in crisis episodes or are pervasive across the cycle. Without shading, readers may misattribute cyclical weakness as signal failure. |
| **Rolling Granger causality** (`rolling_granger_{pair_id}.csv`, CP2 only) | **Yes** | The whole point of rolling Granger is to detect instability in the causal link over time. Recession periods are the most plausible break points (information content of macro indicators collapses when transmission channels seize up). Shading allows the reader to read "F-stat dropped below critical value during GFC" directly from the chart. Without it, readers must cross-reference a separate NBER date table. |
| **Sub-period Sharpe decomposition chart** (`subperiod_sharpe.csv` rendered as bar chart) | **No** | The sub-period chart is already episode-labeled (Dot-Com, GFC, COVID, 2022 Rates Shock) — each episode IS the equivalent of recession context. NBER shading would be redundant and potentially confusing (some episodes, e.g., 2022 Rates Shock, are not NBER recessions). Use episode labels on bar x-axis instead. |

## Summary

Rolling time-series charts (correlation, Sharpe, Granger) all require NBER shading because the primary analytical question for each is "does the pattern break, and if so, when?" Recession bands answer this question visually without requiring the reader to cross-reference dates. The sub-period bar chart is exempt because episode labels are more informative than shading for discrete comparison charts.

## Implementation note for Vera

NBER recession dates are available from FRED series `USREC` (monthly binary) or from the `pandas_datareader` NBER shading convention. The standard shading style is light grey fill (`alpha=0.15`, `color='grey'`) applied between NBER peak and trough dates. Please apply consistently across all three rolling charts so readers can compare the series visually.
