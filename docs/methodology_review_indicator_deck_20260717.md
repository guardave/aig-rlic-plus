# Methodology review — stakeholder indicator deck vs. our quantitative findings

**Author:** Lesandro (Lead) · **Date:** 2026-07-17 · **Status:** review memo, analysis only (no code changes)
**Source:** `temp/_userComments/AIG Economic Indicator Study_SPY.pptx` (66 slides, ~60 indicators vs SPY)

---

## What this document is

The deck is an **upstream indicator survey** — external chart exports annotated with qualitative lead/lag reads (Diverge/Converge/Uncorrelated tags, period-by-period LE/CI/LG tables, "Fundamental Justifications"). It is *not* dashboard feedback and none of its slides are portal screenshots. It predates and feeds pair selection.

Governing principle, unchanged (`docs/lead-grid-frequency-standard.md`): **the deck is reference, never a selection constraint.** Where the deck and the math disagree, the math decides and we adjudicate the gap. The deck's value here is twofold: (1) as an independent qualitative prior to reconcile against our winners, and (2) as a source of *methodological challenges* — three of which expose real gaps in our own approach, one of them in the standard I wrote.

**Caveat on the source, stated up front.** The deck is qualitative chart-eyeballing: no formal inference, no multiple-testing correction, no out-of-sample discipline, and obvious hindsight risk (every "leads the recession" call is made looking back at known recessions). Its claims are **hypotheses to test, not findings to adopt.** This memo treats them accordingly.

---

## Part 1 — Reconciliation: deck's qualitative call vs. our tournament winner

For the 14 deck indicators that map to a live pair. "Our lead" and "Our OOS Sharpe" are read from each pair's `winner_summary.json` (2026-07-17).

| Deck slide / indicator | Deck's qualitative call | Our winner: lead | OOS Sharpe | Agreement |
|---|---|---|---|---|
| S3 Industrial Production → (XLP) | Leading into recession, lagging out | **L4 months** | 1.23 | ✓ leading |
| S5 Building Permits | Coincident; leading in '08 only | **L6 months** | 1.45 | partial — we find a lead |
| S6 10Y-3M Treasury | Leading recession indicator | **L6 months** (lagged) | 1.32 | ✓ leading |
| S7 UMCSENT → (XLV) | Leading→coincident; slow in recovery | **L6 months** | 1.16 | ✓ leading |
| S8 New Home Sales | Leads in bear markets, erratic | **L0 months** | 1.49 | ✗ we find coincident |
| S10 ISM Services PMI | Leading/coinciding | **L3 months** | 1.54 | ✓ leading |
| S11 PHLX SOX | "Leading the SPY **all time**" | **L63 days (~3mo)** | 1.57 | ⚠ lead real but thin, not "all time" |
| S13 VIX/VIX3M | Coincident + lagging in recovery | **L0 days** | 1.13 | ✓ coincident |
| S15 M2 YoY | Leads pre-recession; lags in recovery | **L2 months** | 1.69 | ✓ leading |
| S33 Cass Freight | Directional in recessions, noisy | **L3 months** | 2.49 | ✓ leading |
| S38 C&I Loans | Follows, doesn't lead | **L6 months** (state, not forecast) | 1.50 | ✓ not a forecast |
| S39 HY-IG | Diverges; spikes every recession | **L0 days** | 1.41 | ⚠ see Part 2 (Granger defect) |
| S53 Petroleum Inv. | Peaks lead SPX by **24–36 months** | **L11 months** | 1.53 | ✗ grid cannot reach 24–36mo |
| S66 Wells Fargo Housing | Leads/coincides in housing recessions | **L7 months** | 1.43 | ✓ leading |

**Reading the table.** Broad qualitative agreement on *direction* for the monthly pairs — where the deck says "leading," our tournament also finds a positive monthly lead. The interesting rows are the disagreements, and they cluster into the three challenges below rather than being one-off noise:

- **S11 SOX "all time"** — our finding (genuine 63d lead, but thin alpha, bidirectional Granger, lost every pre-OOS stress episode) is *more skeptical* than the deck. The stakeholders' own `Assessment` sheet reaches the same skeptical verdict independently (4🔴/1🟡/3🟢). Two methods, one conclusion; the deck's "all time" is the outlier.
- **S8 NHS, S13 VIX** — deck says "leads in downturns"; we find L0. This is exactly the **state-dependent lead** pattern (Challenge 2).
- **S53 Petroleum** — deck says 24–36 months; our grid stops at 12 (Challenge 1).

---

## Part 2 — The three methodological challenges

Each is stated as a **testable proposition**, not an accepted fact.

### Challenge 1 — Our monthly lead grid has an unjustified ceiling *and* the wrong shape

**Filed as issue #23.** This is the sharpest point in the deck and it is self-critical — it exposes two inconsistencies in `docs/lead-grid-frequency-standard.md`, a document I wrote and gated.

- **The ceiling.** `scripts/lead_horizon_sweep.py:37` hardcodes `LEADS = list(range(0, 13))`. The standard's Step 3 is titled *"NO CAPS"* and we retired the `umcsent` window-cap on exactly that principle — yet the grid itself caps at 12 months, with no rationale anywhere in the docs (ECON-LL1 only ever *states* it). Our own cited anchor, **Moskowitz-Ooi-Pedersen `{1,3,6,9,12,24,36,48}`**, runs to 48. Slide 53's 24–36 month petroleum claim is **structurally invisible** to us: we would report "no lead there" without having tested it.
- **The shape.** The daily grid is sparse and anchored (`{0,1,5,21,63,126,252}`) because Boudoukh-Richardson-Whitelaw show adjacent overlapping horizons are ~99% correlated. The monthly grid is **contiguous L0–12** — dense. We apply the sparse-is-more-rigorous principle to daily and violate it on monthly.

**Testable proposition:** extending the monthly grid to an anchored set reaching ~36–48 months either (a) surfaces a genuine long-horizon lead the current grid misses (as slide 53 predicts for petroleum), or (b) confirms nothing beyond 12 months, in which case the ceiling is empirically justified and should be *documented* as such rather than inherited.

**Cost:** re-runs winner selection fleet-wide; needs its own wave and sign-off. Not a side effect to absorb.

### Challenge 2 — State-dependent (asymmetric) lead may explain our own L0 results

**Filed as issue #24.** The deck's single most-repeated claim, across independent indicators and three languages: indicators **lead into recessions but lag out of recoveries** (S3 INDPRO, S7 UMCSENT, S12 cement, S13 VIX, S24 permits).

The mechanism matters to us because our tournament fits **one symmetric lead over the full sample.** If the true relationship is "leads down, lags up," a symmetric fit averages the two and lands near **L0** — which is exactly what our three daily pairs returned (hy_ig, gold_copper, vix_vix3m all coincident). The deck supplies a candidate mechanism for our own null result.

**Corroborating signal:** once the HY-IG Granger aggregation bug (#21) is corrected, the spread Granger-causes SPY at lags 4–12 months — in a pair we labelled coincident. So there may be conditional-mean predictability we are averaging away.

**Testable proposition:** condition the lead sweep on market state (drawdown/expansion regime, or the existing HMM states) and re-run the grid within each state. If a lead appears in the down-state and vanishes/inverts in the up-state, our pooled L0 is a **fitting artifact** and the "coincident" narrative on those pairs needs rewriting.

**Guard:** Granger predictability ≠ tradable alpha. The daily tournament already tested 126d/252d and still picked L0 on Sharpe. A significant conditional-mean lead with no Sharpe edge is the phlxsox pattern — *the lead is real; the alpha is thin* — a real finding, but not a strategy. This bears on GH#13's narrative, not necessarily its winners.

### Challenge 3 — Absolute economic thresholds vs. our rolling percentiles

**Not yet filed — recommend filing.** The deck's rules use economically meaningful *levels*: VIX ratio **1.05** (S13), PMI **50** (S9), spread **< 0** and "three successive months below zero" (S6, Estrella-Trubin). Our threshold families are **rolling quantiles** (`T2_roll_p25`).

A rolling percentile **cannot express** "PMI below 50" — it drifts with the window, so "the bottom quartile of the last 36 months" is a moving target, not a fixed economic line. If the true signal is an absolute level (50 is a genuine expansion/contraction boundary, not a relative one), our grid does not span the real rule and the tournament cannot find it.

**Testable proposition:** add an absolute-threshold family (`T_abs`) — fixed economic levels where theory names one — to the tournament for the pairs where an absolute boundary is economically motivated (VIX ratio, ISM PMI, yield-curve sign). Either it wins (our rolling-only grid was missing the real rule) or it loses (rolling percentiles were an adequate proxy). Both outcomes are informative.

---

## Part 3 — Lesser points (noted, not yet actioned)

- **Two-stage conditional triggers.** The deck repeatedly describes "reach a new high *then* drop sharply" rules (S3, S4, S53). Our tournament spans single-threshold rules only; a peak-then-reversal shape is not in the grid. Worth a scoping note before deciding whether it's worth the combinatorial cost.
- **Sign-flipping sub-periods.** The period-by-period LE/CI/LG tables (S5, S7, S8) tabulate windows where the correlation **changes sign** (e.g. permits: +ve CI 1993–98, then NA, then +ve LE 2003–10, then −ve 2010–11). A single global winner cannot represent a relationship that inverts across regimes — related to Challenge 2, and a caution against over-trusting any full-sample point estimate.
- **Frequency mismatch in the deck's own evidence.** Most of the deck's domain claims (VIX, credit, gold/copper, momentum) are monthly-frequency observations mapped to daily via ~21 days/month. Our daily pairs are genuinely daily. Some apparent disagreements may be frequency artifacts, not substantive.

---

## Recommendations

1. **File Challenge 3** (absolute-threshold family) as a tracked issue, joining #23 (grid) and #24 (state-dependent lead). These three are the deck's substantive methodological yield.
2. **Do not retrofit any deck claim into the pairs now.** Per the standard, each becomes a *test*, adjudicated by the math, in its own wave — not a narrative edit. The state-dependent-lead question (Challenge 2) in particular bears on GH#13's published conclusions and must be run, not asserted.
3. **Record the SOX corroboration.** The deck's "SOX leads all time" is refuted by both our tournament and the stakeholders' own Assessment rubric. That convergence is worth citing when the phlxsox narrative is questioned — the skeptical read is doubly independent.
4. **The 24–36 month petroleum claim (S53) is the single highest-value test** to run first if only one is chosen: it is concrete, falsifiable, sits exactly at the grid ceiling Challenge 1 identifies, and would validate or kill the grid-extension question in one run.

---

## Appendix — deck indicators with no live pair (candidate backlog, not scope)

~45 surveyed indicators are not in the portal. A partial list of the more strongly-tagged ones, for a future pair-selection wave: Portland Cement Shipments (S12, "leads recession"), Manufacturers' New Orders (S21, "clear leading both ends"), Retailers Inventories/Sales (S20), Architecture Billings (S32/S46), Import Price Index (S19), Disposable Personal Income (S35). These are leads to *evaluate*, not adopt — same discipline as everything above.
