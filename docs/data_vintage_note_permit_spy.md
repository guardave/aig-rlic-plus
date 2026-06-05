# Data-vintage note — permit_spy

**Status:** Open methodological note. Last updated 2026-06-05 (Lead).
**Audience:** internal — agents touching `permit_spy` artifacts; users
asking why a freshly-fetched FRED `PERMIT` series does not numerically
match what the dashboard's tournament was scored on.

## TL;DR

The Building Permits (FRED `PERMIT`) series is **revised retrospectively**
by the U.S. Census Bureau. The committed tournament results
(`results/permit_spy/tournament_results_20260314.csv`,
`winner_summary.json`, `signals_20260423.parquet`) are scored on the
**April 2026 vintage** of the FRED data. A pull on **2026-06-05** sees
revised values for ~16% of monthly observations, with all of the drift
concentrated in **2018-onwards**. The in-sample tournament window
(1990-01 → 2017-12) is unchanged to four decimal places.

## Quantitative summary

Comparison of `permit_mom` (1-month MoM growth) at every monthly date
where both vintages have a value:

| Statistic | Value |
|---|---|
| Overlapping observations | 431 |
| Mean difference (master − signals) | +0.004 percentage points |
| Median difference | 0.000 pp |
| Standard deviation of difference | 0.47 pp |
| Maximum absolute difference | 2.60 pp |
| Observations with \|diff\| > 0.01 pp | 16.2% |
| Observations with \|diff\| > 0.5 pp  | 10.7% |
| Observations with \|diff\| > 1.0 pp  | 6.5% |
| Direction sign-flips (signal flips trade direction) | 5 of 431 (1.2%) |

Era breakdown:

| Era | Obs | Mean diff | Max abs diff |
|---|---|---|---|
| Pre-2018 (in-sample tournament window) | 335 | 0.0000 pp | 0.0000 pp |
| 2018-onwards (OOS window) | 96 | +0.017 pp | 2.60 pp |

**Reading.** The Census Bureau routinely revises permit data backward
as additional reports flow in from local jurisdictions. Revisions
beyond ~5–7 years are negligible (Pre-2018 row above), so the
econometric battery, stationarity tests, and the in-sample tournament
selection are unaffected by the revision pattern. The OOS window does
drift, but with median revision of 0.0 pp and only 5 trade-direction
sign-flips out of 96 OOS months, the strategy ranking and Sharpe-based
leaderboard are not materially dependent on the vintage chosen.

## Why this note exists

When the master parquet `data/permit_spy_monthly_*.parquet` was
regenerated on 2026-06-05 (to fix the phantom 0% trade-log entries
from 1990–1992 — see `META-FRD` in `docs/agent-sops/team-coordination.md`),
the rebuild used:

- **FRED** (via `fredapi`) for `PERMIT`, `UNRATE`, `HOUST`, `DGS10`,
  `DTB3`, `DFF`. Same vendor, same series IDs, fresh pull.
- **mqr_datalayer** (`Id.BloombergCode` → `Pricing.AdjustedPrice`) for
  `SPY`. Substituted for Yahoo Finance after this host's IP was
  rate-limited by `yfinance`. The substitution is documented as the
  canonical fallback in `.claude/CLAUDE.md` ("Always use mqr_datalayer
  for all data loading operations").

A diff against `results/permit_spy/signals_20260423.parquet` then showed
the divergence above on the `permit_mom` / `permit_mom1m` column.
SPY-derived columns (`spy_ret`, `spy_fwd_*`) match the existing data to
floating-point tolerance — vendor swap is clean.

**Therefore the divergence is purely a FRED-vintage effect, not a
vendor or methodology change.**

## Decision: Option B — vintage-stable trade log

Rather than re-run the entire econometric battery and tournament on the
2026-06-05 vintage (which would create cascading invalidation across
Evidence and Methodology pages and is not actually warranted by the
revision magnitudes above), we adopted **Option B**:

- The **signal column** for trade-log generation is read from the
  existing `results/permit_spy/signals_20260423.parquet` —
  the same April-2026 vintage that the tournament was scored on. This
  keeps the trade log mathematically consistent with the leaderboard,
  Sharpe, MaxDD, and every other tournament-derived number on the
  Strategy page.
- The **price column** for returns and P&L is read from the freshly
  rebuilt master parquet. SPY adjusted closes are point-in-time
  immutable — the rebuild matches public adjusted-close history at
  every landmark date checked (1993-01-29 / 2000-01-31 / 2008-09-30 /
  2009-03-31 / 2020-03-31 / 2025-12-31).

In short: **April-2026 signal × current price**. The combination is
internally consistent because price is not subject to revision and the
signal is pinned to the vintage the tournament saw.

## When this note becomes obsolete

It becomes obsolete the next time the entire `permit_spy` pipeline is
re-run end-to-end on a single vintage (data → tournament → trade log →
charts → narrative). At that point, the vintage of the signal column,
the tournament results, and the trade log all collapse to one
timestamp, and the Option-B split disappears. Until that wave is
scheduled, this note is the canonical record of the vintage seam.

## See also

- `scripts/pair_pipeline_permit_spy.py` — the canonical pipeline. Its
  Stage 1 currently uses `fredapi` + `yfinance`. The mqr_datalayer
  substitution applied on 2026-06-05 was a one-shot data-restoration
  helper at `/tmp/refresh_permit_master.py` (not committed; transient
  by design — re-create from this note if it needs to run again).
- `.claude/CLAUDE.md` (project) — "Primary Data Source" section
  declaring `mqr_datalayer` canonical.
- `docs/agent-sops/team-coordination.md` — `META-FRD` (full-rebuild
  discipline) for the criteria that would trigger a coherent
  end-to-end re-run.
