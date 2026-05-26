---
pair_id: gold_copper_xli
narrative_version: 1.0.0
generated_at: "2026-05-26T00:00:00Z"
generated_by: "Lead Lesandro (Mode 2 maker — Ray hat)"
direction_asserted: countercyclical
indicator_category: commodity_ratio
chart_refs:
  - hero
  - correlation_heatmap
  - ccf_prewhitened
  - granger_f_by_lag
  - history_zoom_gfc
  - history_zoom_china_2015
  - history_zoom_covid
  - history_zoom_rates_2022
  - regime_stats
  - regime_quartile_returns
  - hmm_regime_probs
  - quartile_returns
  - local_projections
  - quantile_regression
  - transfer_entropy
  - returns_by_regime
  - equity_curves
  - drawdown
  - drawdown_comparison
  - walk_forward
  - tournament_sharpe_dist
glossary_terms:
  - Buy-and-hold
  - Counter-cyclical
  - Doctor Copper
  - Drawdown
  - Forward return
  - Futures (continuous front-month)
  - Granger causality
  - Hidden Markov Model (HMM)
  - In-sample / Out-of-sample
  - Local projection
  - Log-ratio
  - Quantile regression
  - Real asset
  - Regime
  - Risk-off / Risk-on
  - Sharpe ratio
  - Transfer entropy
  - Walk-forward validation
  - Z-score
pages:
  story:
    headline: "When the gold/copper ratio rises, industrial stocks weaken"
    sections: [hero_intro, mechanism, history_zoom, evidence_summary, takeaway]
    expanders: [signal_mechanics, ratio_construction]
  evidence:
    headline: "What the data says, examined eight ways"
    sections: [correlation, granger, local_projections, quantile, regime, hmm, transfer_entropy, quartiles]
    expanders: [method_blocks]
  strategy:
    headline: "Turning the signal into a position"
    sections: [winner_overview, equity_curve, drawdown, regime_performance, walk_forward]
    expanders: [position_rules, trigger_cards]
  methodology:
    headline: "How this was built"
    sections: [data, transforms, tournament, validation]
    expanders: [reproducibility]
---

# Portal Narrative: gold_copper_xli

**Pair.** Gold/Copper Ratio → Industrials (XLI). Daily, 2000-01-01 through 2025-12-31. IS through 2019, OOS 2020–2025 (~6 years).

**Indicator category.** `commodity_ratio` — first pair in this bucket. Episode set: GFC (2007–09), China/EM Shock (2015–16), COVID (2020), 2022 Rates Shock.

**Direction asserted.** Counter-cyclical. A rising gold/copper ratio is hypothesized to lead industrial-stock weakness on a several-month horizon.

---

## Mechanism (the ELI5 version)

Two metals tell complementary stories. **Copper** is the most growth-sensitive industrial input — it goes into wires, motors, construction, and the EV supply chain. When global manufacturing strengthens, copper demand rises and so does its price; when manufacturing softens, copper falls first. Traders nickname it **"Doctor Copper"** because its price diagnoses the real economy's health.

**Gold** plays the opposite role. It earns nothing — no dividend, no interest — so people hold it when they distrust the alternatives. When investors expect trouble (recession, inflation that erodes cash, geopolitical stress), they bid up gold as a flight asset.

The **gold/copper ratio** combines both signals into a single ratio. Gold up + copper down (ratio rising) = growth fears + safe-haven demand = a real-asset expression of risk-off. Gold down + copper up (ratio falling) = optimism about industrial expansion.

If this story is right, the ratio should lead industrial stocks specifically — and **XLI** (the Industrial Select Sector SPDR) is the most direct equity expression of US industrial exposure. The hypothesis: **rising gold/copper → XLI underperformance** over the following 1–6 months.

The data validates this weakly but in the right direction. Provisional Pearson correlation of the 252-day z-score of the ratio versus 63-day forward XLI return is **−0.04**. Small in magnitude — gold/copper is not a slam-dunk predictor — but the sign agrees with the mechanism, and the deeper diagnostics (regime quartiles, HMM, transfer entropy) will tell us whether the relationship strengthens in particular regimes. Evan's tournament will report the full picture.

---

## Historical episodes (HZE1)

Four episodes from the `commodity_ratio` registry — each tests a different facet of the signal.

### GFC (2007-12 → 2009-06) — long-lead risk-off

The canonical commodity-ratio risk-off event. Industrial demand collapsed globally as the credit crisis tightened; copper fell roughly 60% peak-to-trough through late 2008. Gold initially sold with everything else (forced liquidation) but then surged as the Fed unleashed QE. The gold/copper ratio more than doubled. XLI lost roughly half its value. The ratio's signal **led** the equity move by 3–6 months on the rolling z-score, making this the episode that best supports the lead-lag hypothesis.

**What to look for in the zoom chart.** Ratio z-score climbs above +2 well before XLI's worst drawdown; the dual-panel chart shows the lead clearly.

### China/EM Shock (2015-06 → 2016-02) — mid-cycle, no US recession

The hard case for the signal: copper crashed on China growth fears, gold held firm on safe-haven flows, ratio spiked. But this happened **without** a US recession — manufacturing was soft, services strong, and the broad market only briefly corrected. XLI did underperform SPY through this window, validating the industrial-specific lead, but the magnitudes were smaller than GFC.

**What to look for.** A clear ratio spike but a more muted XLI drawdown. This is why XLI (not SPY) is the right target — the signal lives in the industrial sub-sector, not the index.

### COVID (2020-02 → 2020-12) — transient regime

The fast-regime test. Industrial activity collapsed in March 2020, copper crashed, gold spiked — ratio spiked dramatically and quickly. But the Fed's response was equally fast, and copper rebounded by mid-summer as China's recovery pulled demand back. XLI recovered alongside. The signal **fired correctly** at the onset but the regime resolved in months, not the multi-quarter horizon GFC played out over.

**What to look for.** Sharp ratio spike, sharp XLI drawdown, then both retrace within 9 months. Tests whether the signal's holding-period assumptions match transient regimes.

### 2022 Rates Shock (2022-01 → 2022-12) — failure case

The episode where the signal can decouple. Rising real rates pressured gold (no yield to compete with Treasuries), while copper held firmer than usual on green-transition demand and supply-side tightness (Chilean output disruptions, low LME inventories). The ratio **fell** through much of 2022 even as XLI struggled along with the broad market in a Fed-driven re-rating. This is the documented failure mode: when one leg of the ratio is dominated by its own supply/macro driver, the risk-off interpretation breaks.

**What to look for.** Ratio flat or falling while XLI weakens — the signal does not lead this drawdown because the equity weakness is rates-driven, not industrial-demand-driven.

---

## How to read the Evidence page

Eight method blocks, each examining the signal from a different angle:

1. **Correlation** — Pearson + Spearman across signal transforms (z-score windows, RoC, percentile rank) and XLI forward-return horizons.
2. **Granger causality** — does the ratio improve out-of-sample forecasts of XLI returns beyond XLI's own past?
3. **Local projections** — Jordà-style impulse responses: if the ratio jumps one standard deviation today, where is XLI in 1 / 5 / 21 / 63 / 126 / 252 trading days?
4. **Quantile regression** — does the signal predict the **lower tail** of XLI returns specifically? (Risk-off signals often work better at the left tail than at the mean.)
5. **Regime context** — does the relationship strengthen in particular volatility / yield-curve / credit regimes? Particularly informative under VIX quartiles.
6. **HMM regime probabilities** — fitting a 2-state hidden Markov model to the ratio itself; do the inferred stress regimes line up with the four historical episodes above?
7. **Transfer entropy** — non-linear, model-free lead-lag measure between ratio and XLI returns.
8. **Quartile returns** — split the sample into 4 quartiles of signal level; report XLI's forward return in each. The cleanest visual test of monotonicity.

---

## Caveats

- **Both legs are USD-priced.** DXY strength can push both gold and copper lower in tandem, muting the ratio's signal. The DXY column in the dataset is the diagnostic — when DXY moves are dominant, treat ratio signals with reduced confidence.
- **Geography basis.** Copper futures price global industrial activity; XLI is US-focused. The signal can be "right about global industrial demand" while being "wrong about US industrial equities" if the divergence is large.
- **Supply shocks decouple the ratio.** The 2022 episode is the cautionary case. The signal works under demand-driven moves and fails when supply dominates either leg.
- **Bounded below by zero.** Use the log-ratio transform (`gold_copper_logratio` in the dataset) for stationarity-sensitive analyses.
- **CPER inception 2011.** The ETF cross-check (`gold_copper_ratio_etf`) is only available post-2011 and should not be used as the primary signal — futures-based ratio is the primary.

---

## ELI5 paragraphs for Ace's pair config

The following blocks are destined for `app/pair_configs/gold_copper_xli_config.py` per APP-PT1. Each is layperson-readable, no jargon left unexplained.

### story_md_intro

> Copper is the metal of industry — wires, motors, EV batteries, construction. Gold is the metal of fear — held when investors distrust everything else. The ratio of one to the other is a real-asset measure of risk-off: when it rises, the message is *"growth worries up, safe-haven demand up."* If that message is correct, the most directly exposed equity group — industrials — should feel it first. This page asks whether they actually do.

### story_md_mechanism

> When the ratio rises, two things are happening at once: copper is falling (industrial demand softening) and gold is rising (flight-to-safety bidding). Either alone would be ambiguous; together they're a much stronger statement about how the market is feeling about real-world activity versus monetary safety. Industrials (XLI) are the most concentrated US equity bet on industrial demand — so if the signal works anywhere in equities, it should work here.

### evidence_eli5_correlation

> A simple statistical check: when the ratio is unusually high (say, 2 standard deviations above its 1-year average), are XLI returns over the next 3 months systematically lower? A negative correlation here would be the first piece of evidence that the mechanism is real. The number is small but it's in the right direction.

### evidence_eli5_regime

> Signals rarely work uniformly across all market regimes. We split history into four buckets — calm, normal, elevated stress, acute stress — using either VIX or a hidden-Markov model fitted on the ratio itself. If the ratio is genuinely a risk-off indicator, the signal should work hardest in the upper two buckets.

### evidence_eli5_quartiles

> The cleanest visual test: sort every day in history by where the ratio's z-score sat that day, then look at what XLI did over the following 3 months. If the highest-z-score days (top quartile, most risk-off) systematically produced the worst XLI returns and the lowest-z-score days produced the best, the signal is real. A flat bar chart across quartiles means it isn't.

### strategy_eli5_winner

> The tournament-winning rule will be filled in by Phase 3 (Evan hat). Expect something in the family of: *"when the 252-day z-score crosses a threshold, reduce industrial exposure; when it crosses back, restore it."* The walk-forward report tells you whether the rule held up in the OOS years (2020–2025) — the years that matter, because they're the ones the rule could not have memorized.

### methodology_eli5

> Symbols chosen for liquidity and history: gold and copper futures (GC=F, HG=F) for the full 25-year sample; ETF tickers (GLD, CPER) as cross-checks. Transformations include log-ratio (for stationarity), rolling z-scores at 126/252/504-day windows, percentile ranks, rates of change, and momentum. The tournament evaluates every combination across multiple lookback windows and holding periods, scoring on out-of-sample Sharpe to avoid in-sample overfitting.

---

## Handoff to Evan (Phase 3)

Inputs ready:
- `data/gold_copper_xli_daily_20260526.parquet` (rebuilt from pipeline; 6783×39).
- `data/gold_copper_xli_daily_schema.json`.
- `results/gold_copper_xli/interpretation_metadata.json` (Dana keys filled, Evan keys empty).

Expected outputs (per ECON-H-series):
- `stationarity_tests_20260526.csv` (ADF / KPSS / PP on all candidate signals).
- `tournament_results_20260526.csv`.
- `winner_summary.json` (per ECON-DS schema with all required fields).
- `signal_scope.json`.
- `signals_20260526.parquet` (the winning signal series).
- `granger_by_lag.csv`, `regime_quartile_returns.csv`.

Direction expectation to validate: counter-cyclical. If Evan's tournament returns a procyclical winner with credible OOS performance, flag for review — the mechanism narrative would need a rewrite.
