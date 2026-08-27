# Portal Narrative — Housing Starts (SAAR) → SPY (`housing_starts_spy`)

**Author:** Research Ray | **Date:** 2026-08-14 | **Mode:** 2 | **Evidence status:** found_in_search (low confidence)

> Source prose for the `housing_starts_spy` portal pages. Headline numbers come from
> `results/housing_starts_spy/winner_summary.json`. The pair is `found_in_search`, so all
> performance is labelled "search-phase OOS (no holdout final exam yet)".

## One-sentence thesis

The prior was procyclical-leading; the data disagrees. The best searched rule is a **countercyclical**
Long/Cash overlay — hold SPY when the 3-month change in Housing Starts is *below* its median (2-month
lag) — earning search-phase OOS Sharpe **1.37 vs 0.91** buy-and-hold with a shallower drawdown
(**-13% vs -24%**); but forward causality is absent, the reverse (market→starts) channel is pervasive,
and the edge is a large-search tail with a non-significant bootstrap p, so it is a low-confidence timing
overlay, not a forecast.

## What the indicator is

Housing Starts (FRED `HOUST`) — total new privately-owned housing units started, thousands of units,
**Seasonally Adjusted Annual Rate**. Because it is SA at source, month-over-month change is a valid
momentum input and **no deseasonalisation is applied** (this is the key contrast with `nhs_spy`, which
uses the NSA new-home-sales series). The raw SAAR level is trend-dominated and non-stationary
(augmented Dickey-Fuller does not reject a unit root), so it is provenance-only; every traded signal is
a stationary growth transform (YoY, MoM, 3-month change, 3-month-average YoY, YoY acceleration, and a
rolling z-score of YoY).

## The direction surprise

The natural prior — housing starts as a rate-sensitive early-cycle leading indicator — points
procyclical. The tournament says otherwise. The regime quartiles (concurrent, on YoY growth) are
**non-monotonic**: Sharpe is highest in the middle (Q2 1.06) and lowest at the strong-growth extreme
(Q4 0.64), with the weak-growth quartile (Q1 0.65) carrying by far the deepest drawdown (-51%). The
searched winner is a **counter** orientation: long SPY when the 3-month change in starts is *below* its
median. Economically this reads as a peak-cycle mean-reversion / "bad-news-is-good-news" rate channel —
softening construction foreshadows easier policy — mirroring the INDPRO precedent where the level story
inverted at extremes.

## Why confidence is low

1. **No forward causality.** Toda-Yamamoto Granger finds Housing Starts do **not** lead SPY at any lag
   1-12. The **reverse** channel (SPY → starts) is significant at **every** lag 1-12 — equities and
   financial conditions lead construction, not the other way round. Local projections, the pre-whitened
   CCF, and transfer entropy all corroborate the weak-forward reading.
2. **Search-tail winner.** The rule is the best of 4,850 valid searched combinations; its re-shuffle
   bootstrap p-value is **0.127**, well above the 5% bar.
3. **Instability.** A structural break is flagged at **2009-03** (GFC) and the rolling signal-return
   correlation is **sign-unstable** (full-sample r ≈ 0.02).
4. **Short, episode-heavy OOS.** Durability is only **conditionally_durable** — COVID-2020 is the sole
   evaluable stress episode inside the 2018-onward OOS window; Dot-Com, GFC and China-2015 predate it.
5. **found_in_search.** No frozen-rule holdout final exam has been run; in-sample Sharpe is materially
   below OOS.

## How to read the pages

- **Story:** the honest headline — a countercyclical timing overlay that beats buy-and-hold on Sharpe
  and drawdown in the search-phase OOS window, framed as a search result, not a validated forecaster.
- **Evidence:** the non-monotonic quartiles alongside the empty forward-Granger / pervasive reverse-
  Granger result that keeps confidence low; supporting LP / CCF / transfer-entropy / quantile checks.
- **Strategy:** the exact rule (long SPY when lagged 3-month starts change is below its p50 threshold,
  L2), its search-phase OOS metrics, and the full caveat stack.
- **Methodology:** data provenance (HOUST live FRED, SA at source), the transform set, the method
  battery, and the tournament design.

## Episodes (history-zoom)

- **GFC (2007-09):** starts collapsed ~75% from their 2006 peak, turning down well ahead of the equity
  bear — the textbook leading-indicator picture, and the reason a naive procyclical prior is tempting.
- **COVID (2020):** starts dipped then surged on record-low rates as SPY crashed and recovered — the
  only evaluable OOS stress episode.
- **2022-24 rate shock:** the mortgage-rate shock cut starts materially — the strong recent regime that
  dominates the OOS window and much of the strategy's drawdown avoidance.
- **Dot-Com:** continuity confirmer for the portal's standard episode set; contextual, not validation.
