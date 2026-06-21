---
{
  "pair_id": "phlxsox_spy",
  "narrative_version": "1.0.0",
  "generated_at": "2026-06-19T00:00:00Z",
  "headline_template": "A",
  "pages": {
    "story": {
      "headline": "OOS Sharpe 1.57 vs ~0.82 for both benchmarks — but an in-sample Sharpe of 0.10 and crisis losses say read it with caution",
      "plain_english": "Semiconductors and the broad stock market move together most of the time, so a rising chip index is rarely a forecast of anything — it is mostly the same market move seen twice. This analysis instead tracks whether chips are out- or under-performing the market, and finds a weak, fragile edge that beat the market in one favorable stretch but failed in every prior crisis.",
      "sections": [
        {"id": "headline_findings", "title": "Headline Findings", "anchor": "headline-findings"},
        {"id": "co_movement_not_lead", "title": "Why Raw Semiconductors Are Not the Signal", "anchor": "why-raw-semiconductors-are-not-the-signal"},
        {"id": "direction_reconciliation", "title": "Feedback, Not a Clean Lead", "anchor": "feedback-not-a-clean-lead"},
        {"id": "what_history_shows", "title": "What History Shows", "anchor": "what-history-shows"}
      ],
      "expanders": [
        {"id": "why_ratio_not_raw", "title": "Why divide SOX by SPY instead of using SOX directly?"},
        {"id": "why_low_confidence", "title": "Why is confidence low?"}
      ]
    },
    "evidence": {
      "headline": "The forecast content is real but thin; the tournament winner's risk-adjusted edge is not robust",
      "plain_english": "Eight tests point the same way: chips and the market feed back into each other, the genuine forward-looking signal in relative strength is small (about 1% of return variation), and the winning strategy beat the market mostly because it was tested in a chip-friendly window.",
      "sections": [
        {"id": "co_movement_vs_forecast", "title": "Co-movement Versus Forecast", "anchor": "co-movement-versus-forecast"},
        {"id": "lead_lag_tests", "title": "Lead-Lag Tests", "anchor": "lead-lag-tests"},
        {"id": "incremental_edge", "title": "Does It Beat SPY's Own Momentum?", "anchor": "does-it-beat-spys-own-momentum"},
        {"id": "model_diagnostics", "title": "Model Diagnostics", "anchor": "model-diagnostics"},
        {"id": "cross_period_checks", "title": "Cross-Period Checks", "anchor": "cross-period-checks"}
      ],
      "expanders": [
        {"id": "how_to_read_granger", "title": "How should I read the Granger chart?"}
      ]
    },
    "strategy": {
      "headline": "A fragile, search-found relative-strength tilt — not a validated all-weather rule",
      "sections": [
        {"id": "rule_summary", "title": "Rule Summary", "anchor": "rule-summary"},
        {"id": "how_signal_is_generated", "title": "How the Signal is Generated", "anchor": "how-the-signal-is-generated"},
        {"id": "tradeoff", "title": "The Edge and Its Fragility", "anchor": "the-edge-and-its-fragility"},
        {"id": "how_to_read_trade_log", "title": "How to Read the Trade Log", "anchor": "how-to-read-trade-log"}
      ],
      "expanders": [
        {"id": "why_search_found", "title": "What does \"found in search\" mean?"}
      ]
    },
    "methodology": {
      "headline": "Daily lead-grid starts at L1: a same-day chip reading is co-movement, not a forecast",
      "sections": [
        {"id": "data_sources", "title": "Data Sources", "anchor": "data-sources"},
        {"id": "model_suite", "title": "Model Suite", "anchor": "model-suite"},
        {"id": "limitations", "title": "Limitations", "anchor": "limitations"}
      ],
      "expanders": [
        {"id": "why_not_causal", "title": "Why is this not a causal claim?"}
      ]
    }
  },
  "chart_refs": [
    "hero",
    "regime_stats",
    "correlation_heatmap",
    "ccf_prewhitened",
    "granger_f_by_lag",
    "incremental_edge",
    "local_projections",
    "quantile_coef",
    "hmm_regime_probs",
    "equity_curves",
    "drawdown",
    "tournament_scatter",
    "tournament_sharpe_dist",
    "rolling_correlation",
    "structural_break",
    "subperiod_sharpe",
    "history_zoom_dotcom",
    "history_zoom_gfc",
    "history_zoom_covid",
    "history_zoom_inflation_2022"
  ],
  "glossary_terms": [
    "Relative strength",
    "Co-movement",
    "Market beta",
    "Momentum",
    "Sharpe ratio",
    "Drawdown",
    "Buy-and-hold",
    "Out-of-sample",
    "Granger causality",
    "Toda-Yamamoto Granger test",
    "Cross-correlation function (CCF)",
    "Local projection",
    "Quantile regression",
    "Transfer entropy",
    "Hidden Markov Model (HMM)",
    "Bootstrap p-value",
    "Procyclical",
    "Overfitting",
    "Feedback (bidirectional causality)"
  ],
  "direction_asserted": "procyclical",
  "historical_episodes_referenced": [
    {"episode_slug": "dotcom", "override_needed": false, "selection_rationale": "long_lead"},
    {"episode_slug": "covid", "override_needed": false, "selection_rationale": "coincident"},
    {"episode_slug": "gfc", "override_needed": false, "selection_rationale": "failure_case"},
    {"episode_slug": "inflation_2022", "override_needed": false, "selection_rationale": "confirmer"}
  ],
  "status_labels_used": ["Available"]
}
---

> Direction asserted: **procyclical** (matches `winner_summary.json.direction`). Confidence: **low**, evidence status **found_in_search**. This pair is deliberately framed as fragile and honest — see the Strategy and Methodology pages for the full caveats.

## Story

### Headline Findings

Out-of-sample (OOS) — tested on data not used to pick the rule — the winning strategy earns a Sharpe ratio (SR) — return per unit of volatility — of 1.57, versus 0.82 for buy-and-hold (BH) — staying fully invested in SPY throughout — and 0.83 for a SPY-own-momentum benchmark (a rule that buys SPY simply when SPY itself has been rising). Its maximum drawdown (MDD) — the largest peak-to-trough loss — is -9.7% (970 basis points) versus -24.5% for buy-and-hold.

That looks impressive, and it is the honest headline number. But three facts sit right next to it and must be read together: the in-sample (IS) Sharpe — measured on the data used to build and pick the rule — was just 0.10; the median rule in the search scored 0.67, below buy-and-hold's 0.82; and the rule lost money in every market crisis before the test window began. The strong out-of-sample number rests on a favorable 2021–2026 semiconductor bull market. Treat this as a fragile, search-found result, not a validated edge.

### Why Raw Semiconductors Are Not the Signal

The PHLX Semiconductor Index (SOX) — a basket of major chip stocks — and SPY are both equity indices, and they move up and down together about 71% of the time on a daily basis. That number (a daily-return correlation of 0.709) is co-movement — shared market beta (how much an asset swings when the whole market swings) — not a forecast. If you used a high reading of raw SOX as a "buy" signal for SPY, you would mostly be reacting to a market move that already happened in both at once.

To find any genuine forecasting content, the analysis trades **relative strength** — one index's price divided by another's, here SOX ÷ SPY. Dividing by SPY cancels out the shared market move and leaves only the question that could actually predict something: *are semiconductors leading or lagging the market right now?* The hero chart shows this ratio, not raw SOX.

<!-- expander: Why divide SOX by SPY instead of using SOX directly? -->
Imagine two boats rising and falling on the same tide. Watching one boat tells you almost nothing about the other's *extra* movement — the tide moves both. Dividing SOX by SPY is like measuring one boat's height *relative to the other*, removing the tide. What is left is whether semiconductors are climbing faster or slower than the market. Only that residual has any chance of being a forecast; the raw level is dominated by the shared "tide" of overall market beta.
<!-- /expander -->

### Feedback, Not a Clean Lead

It is tempting to tell a tidy story — "semiconductors are the economy's canary, so chips lead the market." The data do not support that clean version. Granger causality (GC) — a test of whether past values of one series improve forecasts of another — is significant from SOX to SPY at every horizon tested, but it is *also* significant from SPY back to SOX at every horizon, and the reverse direction is actually stronger at short lags. **What this means:** the two markets feed back into each other (bidirectional causality) because both are high-beta equity indices pushing one another around — not because chips cleanly lead. The pre-whitened cross-correlation tells the same story, with significant links on both the lead and the lag side.

So the tradable content is not "chips predict the market." It is a weak relative-strength momentum (MOM) — the tendency of a recent trend to persist — effect: when semiconductors have recently been outpacing the market, the market has tended to do slightly better over the following weeks.

### What History Shows

The pair-specific history-zoom charts make the fragility tangible. In the **Dot-Com bust (2000–02)**, semiconductors did roll over before the broad market — the closest thing to a genuine long lead, and the reason chips have their canary reputation. In the **COVID crash (2020)**, chips and the market fell together within days; the relative-strength signal moved *with* the crash, not ahead of it — a coincident episode, not a warning. The **Global Financial Crisis (GFC, 2007–09)** is the failure case: the relative-strength rule was deeply negative through it (the rule lost about 43% in that window in simulation). The **2022 rates shock** is a confirmer that the signal can stay defensive in a grinding bear market. The honest summary across episodes: this signal sometimes leads, sometimes coincides, and sometimes fails — which is exactly why its confidence rating is low.

<!-- expander: Why is confidence low? -->
The winning rule was the single best of 4,607 valid searched combinations. When you search thousands of rules, the best one can look good purely by luck. Three independent checks flag that risk here: the in-sample Sharpe was 0.10 (the rule did not work on the data used to build it), the median searched rule lost to buy-and-hold, and a bootstrap (resampling) test gives p = 0.041 — barely under the 5% line. The rule has also not yet faced a frozen "final exam" on an untouched window. All of this earns the label found_in_search, the weakest evidence tier.
<!-- /expander -->

## Evidence

### Co-movement Versus Forecast

The correlation heatmap separates two very different numbers. The same-day correlation between SOX and SPY returns is 0.709 — large, but that is co-movement (shared beta), not predictive power. The *forward* correlations — between today's lagged signal and SPY's *future* returns — are an order of magnitude smaller, with the best cell only around r = 0.10 and an implied R² (share of return variation explained) near 1%. **In plain English:** the big number everyone notices is not a forecast; the genuine forecasting signal is small. Relative-strength rows carry slightly more of that forward signal than raw-SOX rows, which is why the strategy uses the ratio.

### Lead-Lag Tests

Two tests probe direction and timing. The Toda-Yamamoto Granger test (a trend-robust version of Granger causality) is significant in *both* directions at every lag — SOX helps forecast SPY and SPY helps forecast SOX. The pre-whitened cross-correlation function (CCF) — the correlation between the two series at various time offsets after removing each one's own trend — shows significant cells on both the lead side and the lag side once the dominant same-day spike is set aside. **What this means:** the relationship is feedback between two high-beta equity series, not a one-way semiconductor lead.

<!-- expander: How should I read the Granger chart? -->
The chart plots two sets of bars. Vermillion bars are SOX leading SPY; blue bars are SPY leading SOX. A bar above the dashed line is statistically meaningful at the 5% level. The key observation is that *both* colors clear the line at every lag — and the blue (reverse) bars are actually taller at short lags. That two-sided pattern is the definition of feedback. A clean leading indicator would show tall bars in only one color.
<!-- /expander -->

### Does It Beat SPY's Own Momentum?

The toughest test is whether the relative-strength signal adds anything over SPY's *own* momentum — because a rule that just follows SPY's recent trend already earns a Sharpe of 0.83. The incremental-edge chart answers this directly: relative strength adds a statistically significant increment at the 21-day horizon (p = 0.033) but **not** at the 63-day horizon (p = 0.075), and the extra explanatory power is only about one percentage point of R² either way. **In plain English:** there is a genuine but thin and horizon-dependent edge over simply riding SPY's trend — real enough to detect, too small to lean on heavily.

### Model Diagnostics

Local projections (LP) — impulse-response regressions over several horizons with heteroskedasticity- and autocorrelation-consistent (HAC) standard errors — give positive forward coefficients that grow with horizon but never reach 5% significance (minimum p ≈ 0.10); their confidence bands include zero throughout. The reverse panel shows a significant *negative* one-day coefficient — the market's own move feeds back into relative strength, reinforcing the feedback story. Quantile regression (QR) — separate regressions for weak, normal, and strong return outcomes — shows the signal is significant in the lower (downside) return quantiles and fades to zero in the upside, so its information is more about avoiding bad outcomes than chasing big up-moves. The Hidden Markov Model (HMM) — a model that splits the sample into latent calm and high-variance regimes — is used here only as a regime map, not as the winning signal. Transfer entropy was computed for completeness as a nonlinear information-flow check.

### Cross-Period Checks

The rolling correlation between the relative-strength signal and SPY returns is sign-unstable: its sign agrees with the full-sample value only 42% of the time, so the relationship flips too often to trust blindly. The Quandt-Andrews structural-break test points to a March 2020 candidate date but does **not** reject stability (sup-F 2.12, bootstrap p = 0.67) — the instability shows up as a wandering sign, not a one-time regime break. Most importantly, the crisis Sharpe chart shows the winner deeply negative in the Dot-Com bust (-1.16), the GFC (-1.06), and COVID (-0.95), and positive only in the in-sample 2022 rates shock (+0.36). The headline OOS Sharpe is carried by the benign 2021–26 window, not by crisis resilience.

## Strategy

### Rule Summary

The selected strategy is Long/Cash — hold SPY when the lagged signal is favorable, otherwise hold cash. The signal is the 6-month momentum of the SOX ÷ SPY relative-strength ratio. The rule goes long SPY when that signal — observed 63 trading days (about three months) earlier — is above its rolling 75th percentile, and steps to cash otherwise. In plain terms: *when semiconductors have recently been outpacing the market by enough, own SPY; otherwise stand aside.* The lead grid deliberately starts at one day, never zero, because a same-day chip reading is co-movement, not a forecast.

### How the Signal is Generated

First, the data process divides the semiconductor index by SPY each day to get the relative-strength ratio, which removes the shared market move and leaves only whether chips are leading or lagging. Second, it measures how much that ratio has changed over the past six months — its momentum. Third, it compares the value from about three months earlier against a rolling 75th-percentile threshold and converts that comparison into a position: long SPY if relative-strength momentum was strong, cash if it was weak.

This is intentionally simple. It does not forecast chip demand, model the semiconductor cycle, or pick individual stocks. It asks one question: has the chip sector's recent strength relative to the market historically lined up with a better SPY allocation?

### The Edge and Its Fragility

The honest read is a thin, fragile edge. The rule's out-of-sample Sharpe of 1.57 beats both benchmarks — buy-and-hold at 0.82 and SPY-own-momentum at 0.83 — and it cut the worst drawdown to -9.7% (970 basis points) from -24.5%. But the in-sample Sharpe was only 0.10, the median of the 4,607 searched rules (0.67) lost to buy-and-hold, the win rate was 20%, and the rule lost in every pre-test crisis. The bootstrap p-value — a resampling test of whether the result could arise by chance — is 0.041, only just under 5%. **What this means:** the strategy beat the benchmarks in the backtest, but most of that came from being tested in a chip-friendly stretch, and the statistical edge over simply riding SPY's own trend is marginal (significant at 21 days, not at 63). Size the conviction accordingly.

<!-- expander: What does "found in search" mean? -->
"Found in search" is the weakest of the evidence tiers. It means the rule was selected as the best performer out of thousands of candidate combinations, but has not yet been confirmed on a fresh, untouched window (a "final exam"). Because searching many rules makes a lucky winner likely, a found-in-search result is a hypothesis to be tested further, not a validated strategy. The next step for this pair is exactly that frozen-window confirmation.
<!-- /expander -->

### How to Read the Trade Log

The trade log is a simulated backtest record, not a record of real executed trades. Two files are available: a broker-style log (user-friendly, one row per position change) and a position log (for researcher debugging). The key columns in the broker-style log are the date of each exposure change, the position taken (long SPY or cash), and the signal value that triggered it. For example, when the lagged relative-strength momentum signal fell back below its rolling 75th-percentile threshold, the strategy moved from fully long SPY to 100% cash on the next decision date — you can trace each such switch as a row in the broker-style CSV. Use the log to audit when and why exposure changed; do not read it as broker-confirmed fills.

## Methodology

### Data Sources

The indicator is the PHLX Semiconductor Index (SOX), pulled from Yahoo Finance (series `^SOX`) as a live daily series back to 1994. The target is SPY, the exchange-traded fund (ETF) used as the investable proxy for the United States equity market. Daily transformations include 1/3/6/12-month momentum of both raw SOX and the SOX ÷ SPY relative-strength ratio, plus 126- and 252-day z-scores (standardized values measured in standard-deviation units) and 21-day realized volatility.

A discipline point specific to this pair: the lead grid starts at one trading day, never zero. A same-day SOX reading shares the day's market move with SPY, so using it would be co-movement masquerading as a forecast. Enforcing a one-day floor keeps the test honest.

### Model Suite

The evidence suite includes Pearson correlation (contemporaneous and forward), pre-whitened cross-correlation, Toda-Yamamoto Granger causality in both directions, an incremental-edge regression versus SPY-own-momentum, local projections with HAC standard errors, quantile regression, transfer entropy, a Hidden Markov regime model, rolling correlation, a Quandt-Andrews structural-break test, and a 6,760-combination tournament with bootstrap and transaction-cost validation (5 basis points per trade). The in-sample period ends 2021-06-10; the out-of-sample window runs 2021-06-11 through 2026-06-17 (1,260 trading days, about five years). The OOS window is a single semiconductor-bull regime, which is the main reason confidence is low.

### Limitations

This is not a causal claim. The relationship between semiconductors and the broad market is bidirectional feedback between two high-beta equity indices, not a structural model in which chip strength makes the market rise. The forward forecasting content is small (about 1% of return variation), the edge over SPY's own momentum is marginal and horizon-dependent, the rolling correlation's sign is unstable, and the headline out-of-sample performance leans on a favorable 2021–26 window during which the rule never had to survive a crisis. The result is best treated as a fragile, search-found hypothesis pending a frozen final-exam confirmation.

### References

- Toda, H. Y., & Yamamoto, T. (1995). Statistical inference in vector autoregressions with possibly integrated processes. *Journal of Econometrics*, 66(1–2), 225–250.
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.
- Moskowitz, T., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250.
- Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2014). Pseudo-mathematics and financial charlatanism: the effects of backtest overfitting on out-of-sample performance. *Notices of the AMS*, 61(5), 458–471.
- Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. *Econometrica*, 37(3), 424–438.

### Glossary

- **Relative strength** — one index's price divided by another's (here SOX ÷ SPY); rises when semiconductors outperform the market.
- **Co-movement** — two assets moving together day to day; here ~71%, which is shared market beta, not a forecast.
- **Market beta** — how much an asset swings when the whole market swings.
- **Momentum** — the tendency of a recent trend to continue.
- **Sharpe ratio (SR)** — return per unit of volatility.
- **Maximum drawdown (MDD)** — the largest peak-to-trough loss.
- **Buy-and-hold (BH)** — staying fully invested in SPY throughout.
- **Out-of-sample (OOS) / In-sample (IS)** — data not used / used to pick the rule.
- **Granger / Toda-Yamamoto causality** — tests of whether past values of one series improve forecasts of another.
- **Cross-correlation function (CCF)** — correlation between two series at various time offsets.
- **Local projection (LP)** — impulse-response regression over several horizons.
- **Quantile regression (QR)** — separate regressions for weak, normal, and strong outcomes.
- **Transfer entropy (TE)** — a nonlinear information-flow check.
- **Hidden Markov Model (HMM)** — a model that splits the sample into latent regimes.
- **Bootstrap p-value** — a resampling test of whether a result could arise by chance.
- **Procyclical** — moving in the same direction as the market cycle.
- **Overfitting** — a rule that fits the build data but fails on fresh data.
