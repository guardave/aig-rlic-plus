# Research note — daily lead/lag horizon-grid conventions in the literature

**Purpose:** evidence base for the daily-lead grid `{0,1,5,21,63,126,252}` adopted in [`lead-grid-frequency-standard.md`](lead-grid-frequency-standard.md). Compiled 2026-07-14 via a multi-source fact-checked review (20 sources fetched, 23 verified findings; 2 candidate claims refuted). Prioritized peer-reviewed / working-paper sources.

## Headline

The literature does **not** use dense, evenly-spaced daily-horizon grids. It converges on small, **non-linearly-spaced** grids anchored to trading-period multiples — week (5d), month (~21d), quarter (~63d), half-year (~126d), year (~252d) — unit steps at the short end, widening jumps at the long end. Canonical templates: **Moskowitz-Ooi-Pedersen** {1,3,6,9,12,24,36,48} months (*Time Series Momentum*, JFE 2012); **Jegadeesh-Titman** {3,6,9,12} months (1993).

## Grid assessment for our use case

- **Well-grounded:** `{0, 1, 5, 21, 63, 126, 252}` — the trading-day anchors plus same-day / next-day.
- **Idiosyncratic (no literature basis, dropped):** 7, 14, 30, 50 trading days — calendar-day intuitions that map to no conventional anchor and appear in no surveyed paper. (10 ≈ 2wk is borderline-optional.)
- **Why sparser is more rigorous:** Boudoukh-Richardson-Whitelaw (NBER w11841) — overlapping multi-horizon estimates are ~99% correlated across horizons under the null; adjacent points are near-duplicates, not independent evidence. Denser grids add no information and enlarge the multiple-testing surface.

## Domain-specific horizons (bears on our 0-day winners)

Predictability for these signal families is concentrated at **intermediate (quarter-to-year)** horizons; short horizons show **reversal**, not continuation:
- **Credit spreads** — Gilchrist-Zakrajšek (AER 2012): 3-month / 1–4-quarter horizons; no daily lead-lag grid.
- **VIX term structure** — Johnson (RFS): 1/3/6/12-month; predictability is either 1-day (futures mean-reversion) **or** monthly-plus — not intermediate daily lags.
- **Gold/copper ratio** — Roh et al. (SSRN 2025): 1/3/6/12/24/36-month; concentrated at 6mo–1yr; explicitly "no strong 1-month-ahead predictability." (cf. gold/platinum, Huang-Kilic, JFE 2019.)
- **Lead-lag microstructure** — Chordia-Swaminathan (JF 2000): daily VAR uses K=5 lags (~1 trading week); more lags "only add noise."
- **Momentum** — 3–12 months = continuation; 1 week / 1 month = reversal (sign flips).

**Implication:** our three daily pairs with 0-day-lead winners are most likely capturing same-day co-movement / mean-reversion, not a genuine lead — corroborating the "coincident, not leading" reframing.

## Methodological cautions (mandatory guards)

- **Overlapping returns → HAC inference.** Local-projection residual at horizon h is MA(h) (Jordà); use Newey-West or Hodrick(1992). Commodity-ratio studies use Hodrick(1992) t-stats.
- **Multiple horizons are not independent tests.** Joint / simultaneous inference across horizons (Jordà-Taylor); pointwise bands mislead.
- **Raised t-hurdle.** Harvey-Liu-Zhu: after data-mining, require **t > 3.0**, not 2.0 — "most claimed research findings in financial economics are likely false" without correction.
- **Long-horizon predictability is often illusory** (Boudoukh-Richardson-Whitelaw); standard overlap adjustments overstate t-stats.

## Caveats on the evidence

Frequency mismatch is the central caveat: most domain evidence (VIX, credit, gold/copper, momentum) is **monthly**-frequency, mapped to trading-day equivalents via ~21 days/month. Genuinely daily-native results are thin (Chordia-Swaminathan K=5; a next-day-VIX-futures ML study). For HY-IG→SPY and SOX→SPY specifically, no named daily-frequency horizon-grid paper was located — those rest on analogy. Two sub-claims were refuted in verification: that lead-lag *dominates* own-autocorrelation, and that a single VIX level has *essentially no* 1–3mo predictive power.
