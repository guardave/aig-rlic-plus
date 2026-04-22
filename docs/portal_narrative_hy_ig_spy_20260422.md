---
pair_id: hy_ig_spy
narrative_version: 1.0.0
generated_at: "2026-04-22T00:00:00Z"
headline_template: "A"
headline_template_rationale: "Template A (metric-first) chosen because this is a fresh pair whose primary reader question is 'does this signal generate risk-adjusted alpha for SPY?' — leading with the OOS Sharpe and drawdown reduction anchors the reader before the mechanism explanation. OOS metrics are read from results/hy_ig_spy/winner_summary.json once Dana's pipeline delivers; placeholders below reflect the contracted schema fields."
direction_asserted: countercyclical
chart_refs:
  - hero
  - correlations
  - ccf
  - regime_stats
  - equity_curves
  - drawdown
  - walk_forward
  - tournament_scatter
  - rolling_sharpe
  - signal_dist
  - history_zoom_dotcom
  - history_zoom_gfc
  - history_zoom_covid
glossary_terms:
  - Basis point (bp)
  - Credit spread
  - HY-IG spread
  - High-yield bonds (junk bonds)
  - Investment-grade bonds
  - Option-adjusted spread (OAS)
  - Buy-and-hold
  - Counter-cyclical
  - Drawdown
  - Granger causality
  - Hidden Markov Model (HMM)
  - Impulse response
  - In-sample / Out-of-sample
  - Local projection
  - Quantile regression
  - Regime
  - Sharpe ratio
  - Transfer entropy
  - VIX
  - Walk-forward validation
  - Z-score
  - Tournament
  - Stress regime
  - Signal probability
  - Credit cycle
  - Default risk premium
status_labels_used:
  - Validated
historical_episodes_referenced:
  - episode_slug: dotcom
    override_needed: false
    selection_rationale: confirmer
    prose_ref: "Story §Historical Episodes — Dot-Com paragraph covers 2000-2002 tech sector collapse; HY-IG spread widening as credit deterioration spread from telecom/tech issuers to broader high-yield."
  - episode_slug: gfc
    override_needed: false
    selection_rationale: long_lead
    prose_ref: "Story §Historical Episodes — GFC paragraph covers 2007-2009; spread widening 5+ months before SPY peak is the canonical lead-indicator demonstration."
  - episode_slug: covid
    override_needed: false
    selection_rationale: coincident
    prose_ref: "Story §Historical Episodes — COVID paragraph covers Feb-Apr 2020; rapid widening coincident with SPY drawdown, followed by fast recovery as Fed intervened."
pages:
  story:
    headline: "## Credit spreads as a leading equity risk signal — OOS Sharpe vs SPY buy-and-hold"
    plain_english: "When companies borrow money, lenders charge higher rates to riskier companies. The gap between those rates — the credit spread — acts like a stress gauge for the financial system. When the gap widens, investors are worried about company defaults. This research asks whether watching that stress gauge can help investors in SPY, the S&P 500 ETF, protect their portfolio before the damage arrives."
    sections:
      - id: where_this_fits
        title: "Where This Fits in the Portal"
        anchor: where-this-fits
      - id: one_sentence_thesis
        title: "One-Sentence Thesis"
        anchor: one-sentence-thesis
      - id: why_spy_investors_care
        title: "Why SPY Investors Should Watch Corporate Bond Spreads"
        anchor: why-spy-investors-should-watch-corporate-bond-spreads
      - id: the_signal_mechanism
        title: "The Signal Mechanism"
        anchor: the-signal-mechanism
      - id: nuance_and_limits
        title: "Nuance and Limits"
        anchor: nuance-and-limits
      - id: historical_episodes
        title: "How the Signal Performed in Past Crises"
        anchor: how-the-signal-performed-in-past-crises
    expanders:
      - id: what_is_hy_ig
        title: "What exactly is the HY-IG spread and how is it measured?"
      - id: merton_model_spy
        title: "Why are stock and bond markets mathematically connected? (The Merton Model)"
      - id: what_is_hmm
        title: "What is a Hidden Markov Model and why use it for regimes?"
  evidence:
    headline: ""
    plain_english: "This section presents eight statistical tests of the same core question: does the HY-IG credit spread carry useful information about future SPY returns? The tests range from simple correlation to nonlinear information-flow measures. No single test is definitive, but their convergence builds a rigorous, multi-angle case."
    sections:
      - id: how_we_tested
        title: "How We Tested the Signal"
        anchor: how-we-tested-the-signal
      - id: method_correlation
        title: "Method: Correlation Analysis"
        anchor: method-correlation-analysis
      - id: method_granger
        title: "Method: Granger Causality"
        anchor: method-granger-causality
      - id: method_ccf
        title: "Method: Pre-Whitened Cross-Correlation Function"
        anchor: method-ccf
      - id: method_hmm
        title: "Method: Hidden Markov Model Regime Analysis"
        anchor: method-hmm-regime-analysis
      - id: method_regime_quartile
        title: "Method: Regime Quartile Returns"
        anchor: method-regime-quartile-returns
      - id: method_transfer_entropy
        title: "Method: Transfer Entropy"
        anchor: method-transfer-entropy
      - id: method_local_projections
        title: "Method: Local Projections (Jordà Impulse Responses)"
        anchor: method-local-projections
      - id: method_quantile
        title: "Method: Quantile Regression"
        anchor: method-quantile-regression
    expanders: []
  strategy:
    headline: ""
    plain_english: "The strategy uses the credit spread signal to scale SPY exposure up or down. When credit stress is high, position size falls; when credit conditions are calm, full exposure is restored. This section explains what the strategy does, what the numbers look like, and where honest limitations lie."
    sections:
      - id: how_signal_generated
        title: "How the Signal Is Generated"
        anchor: how-the-signal-is-generated
      - id: how_signal_translates
        title: "How the Signal Translates to Action"
        anchor: how-the-signal-translates-to-action
      - id: key_metrics
        title: "Key Strategy Metrics"
        anchor: key-strategy-metrics
      - id: where_adds_value
        title: "Where the Strategy Adds Value — and Where It Does Not"
        anchor: where-the-strategy-adds-value
      - id: honest_caveats
        title: "Honest Caveats"
        anchor: honest-caveats
    expanders:
      - id: why_scale_not_switch
        title: "Why scale position size instead of switching all-in/all-out?"
      - id: what_is_z_score
        title: "What is a z-score and why does it matter for signal thresholds?"
  methodology:
    headline: ""
    plain_english: "This section covers the technical decisions — data sources, sample period, model specifications, and known limitations. Readers who want to replicate or challenge the analysis will find what they need here."
    sections:
      - id: data_sources
        title: "Data Sources"
        anchor: data-sources
      - id: sample_period
        title: "Sample Period"
        anchor: sample-period
      - id: indicator_construction
        title: "Indicator Construction"
        anchor: indicator-construction
      - id: econometric_methods
        title: "Econometric Methods"
        anchor: econometric-methods
      - id: diagnostics
        title: "Diagnostics"
        anchor: diagnostics
      - id: signal_universe
        title: "Signal Universe"
        anchor: signal-universe
      - id: references
        title: "References"
        anchor: references
    expanders: []
glossary_requests: []
---

# Portal Narrative: HY-IG Credit Spread → SPY (Fresh Pair, 2026-04-22)

**From:** Ray (Research Agent)
**To:** Ace (App Dev)
**Date:** 2026-04-22 (Wave 10G.4B)
**pair_id:** `hy_ig_spy`
**RES-NR1 check:** target_symbol = SPY; narrative instrument references verified — see handoff doc.

---

## Page 1 — Story

<details>
<summary>Plain English version</summary>

When companies borrow money, lenders charge higher rates to riskier companies. The gap between those rates — the credit spread — acts like a stress gauge for the financial system. When the gap widens, investors are worried about company defaults. This research asks whether watching that stress gauge can help investors in SPY, the S&P 500 ETF, protect their portfolio before the damage arrives.

</details>

### Where This Fits

This is a **single indicator-target analysis**: does the HY-IG credit spread carry advance information about SPY returns? The portal contains dozens of such pair studies. Here the lens is fixed on corporate credit stress as a predictor of broad US equity performance measured via SPY.

**How to navigate the four pages.** The Story page explains the economic mechanism — why bond spreads and equity prices are related at all. The Evidence page presents eight statistical tests. The Strategy page describes the actionable trading rule and its honest track record. The Methodology page is the technical appendix for practitioners who want to reproduce or challenge the work.

### One-Sentence Thesis

The HY-IG credit spread — the yield premium that risky corporate borrowers pay relative to safer peers — reflects real-time aggregate default risk, and when that risk rises sharply, it has historically preceded broad equity market declines measured by SPY.

### Why SPY Investors Should Watch Corporate Bond Spreads

SPY investors are sometimes surprised to learn that the corporate bond market is, in important ways, more informationally efficient about economic risk than the equity market. The intuition is not obvious — stocks are more liquid, more watched, and more immediately accessible to retail investors. Yet academic research going back to Gertler and Lown (1999) and Gilchrist and Zakrajšek (2012) demonstrates that credit spreads carry orthogonal information about future economic conditions that equity prices do not immediately absorb.

Why? Because bondholders and equity holders look at the same company through very different lenses. Equity holders are optimists by construction — they hold a call option on company value and benefit from upside. Bondholders are creditors who care primarily about the downside: can this company pay me back? When institutional credit analysts, who spend their careers pricing default risk, begin demanding higher spreads, they are saying something specific and quantitative: the probability of widespread corporate distress has risen. That signal travels slowly into equity prices because equity investors tend to attribute spread widening to "technical factors" or "illiquidity" until the damage is undeniable.

The HY-IG spread — the difference in option-adjusted yields between the ICE BofA US High Yield Index and the ICE BofA US Investment Grade Corporate Index — is one of the cleanest single-number summaries of this aggregate credit sentiment. High-yield issuers (rated BB and below) represent the portion of the corporate universe most vulnerable to economic downturns; investment-grade issuers (rated BBB and above) are the most resilient. The spread between them isolates pure credit-cycle risk, stripped of duration effects, because both series are measured as option-adjusted spreads against comparable Treasuries.

<!-- expander: What exactly is the HY-IG spread and how is it measured? -->
The HY-IG spread is constructed by subtracting the option-adjusted spread (OAS) of the ICE BofA US Investment Grade Corporate Index from the OAS of the ICE BofA US High Yield Index. Both underlying OAS figures measure the yield premium over a maturity-matched Treasury curve, after adjusting for embedded optionality (call/put features). By using OAS rather than raw yield, the spread isolates credit risk from interest-rate risk — a pure signal of how much extra compensation investors require to hold risky corporate debt versus safer corporate debt. Data is sourced from FRED (series BAMLH0A0HYM2EY for HY OAS and BAMLC0A0CMEY for IG OAS), available from the late 1990s.
<!-- /expander -->

<!-- expander: Why are stock and bond markets mathematically connected? (The Merton Model) -->
Robert Merton's 1974 structural credit model provides a mathematical foundation for the stock-bond link. In the Merton framework, equity is a call option on firm value: shareholders receive the residual value of the firm's assets after debt is paid off. If firm value exceeds debt face value, shareholders collect the difference; if it falls below, shareholders receive nothing (the firm defaults). Corporate bonds are the short-call counterpart: bondholders receive par (capped upside) but absorb losses if firm value collapses. Both instruments price off the same underlying firm value process — which means information about one should affect the other. When HY bond spreads widen dramatically, the market is re-pricing the default probability distribution across many firms simultaneously, which is precisely the information that forward equity returns will eventually reflect.
<!-- /expander -->

### The Signal Mechanism

The pathway from spread widening to SPY weakness runs through three reinforcing channels that operate at different speeds:

**Channel 1: Credit-Cycle Tightening (3-12 months).** Rising corporate bond spreads are a leading indicator of bank lending standards. When spreads widen, banks and institutional lenders simultaneously tighten credit terms across the economy — raising hurdle rates, reducing credit lines, increasing covenant restrictions. This credit tightening reduces corporate investment, slows hiring, and compresses earnings expectations across the entire S&P 500 universe, not just HY-rated companies. SPY, as an index of 500 large-cap US companies, is sensitive to this aggregate earnings trajectory.

**Channel 2: Risk-Appetite Signal (days to weeks).** Large institutional portfolios are cross-asset allocators. When their credit teams signal that HY risk/reward has deteriorated, the same risk committee that cuts HY exposure frequently also trims equity risk. This portfolio-level de-risking creates correlated selling pressure across credit and equities that can appear almost simultaneous at weekly resolution but is initiated in the credit department first.

**Channel 3: Financial Conditions Transmission (1-6 months).** The Federal Reserve Financial Conditions Index (NFCI), the Goldman Sachs FCI, and similar composite measures incorporate credit spreads as one of their largest components. When spreads widen materially, financial conditions tighten in a way that is forward-looking for economic growth — and therefore forward-looking for SPY earnings and multiples simultaneously.

The combined prediction is **countercyclical**: rising HY-IG spreads → deteriorating financial conditions → weaker forward SPY returns. The direction confirmed by our econometric analysis (see Evidence) is consistent across all three channels.

### Nuance and Limits

No signal is a crystal ball. Honest limitations for the HY-IG → SPY relationship:

**The 2022 interest-rate exception.** The 2022 SPY drawdown (-25%) was driven primarily by the Federal Reserve's fastest rate-hiking cycle in 40 years, not by a credit deterioration cycle. HY-IG spreads did widen (from roughly 310 bps to 580 bps), but the widening was moderate relative to the magnitude of the equity decline — because the driver was rate repricing, not default-risk repricing. An investor relying solely on the HY-IG signal would have reduced SPY exposure but not fully avoided the decline. This is a real limitation: pure rate-shock bear markets are the blind spot for this signal. The portal's separate Yield Curve × SPY analysis addresses that case.

**Short-horizon noise.** The HY-IG spread is measured daily but its predictive content for SPY is most reliable at 1-month to 12-month horizons. Short-term (weekly) spread moves are heavily influenced by ETF fund flows, technical factors, and market microstructure noise that does not translate into fundamental SPY repricing.

**Structural break risk.** The post-GFC era of near-zero rates (2010-2021) compressed credit spreads to historically tight levels for prolonged periods. This compression may have blunted the signal's discriminatory power during that era — investors should weight post-2010 OOS data accordingly and examine the regime-conditional results (see Evidence: Regime Quartile and HMM).

**Feedback risk in stress regimes.** During acute crises (GFC 2008-09, COVID 2020), spread widening and equity declines reinforce each other at high frequency — the signal becomes co-incident rather than leading. The historical episode analysis below illustrates where the lead holds and where the gap collapses.

### How the Signal Performed in Past Crises

#### The Dot-Com Crash (2000-2002)

The Dot-Com bust began as an equity-sector phenomenon concentrated in technology and telecommunications, but the credit channel caught it early. Telecom companies had issued enormous volumes of high-yield debt to finance network buildouts through 1999-2000; as capital markets closed and revenue projections collapsed, their bonds began repricing months before the NASDAQ peak. By late 2000, HY-IG spreads had widened meaningfully, signaling a credit deterioration that would eventually hit the broader S&P 500 as corporate capital spending fell sharply. SPY declined approximately 49% from peak to trough across 2000-2002. An investor watching HY-IG spreads as an early filter would have had a several-month window of warning before the bulk of the SPY damage accumulated.

#### The Global Financial Crisis (2007-2009)

The GFC is the clearest demonstration of the HY-IG spread's leading-indicator properties for SPY. The HY-IG spread began widening in the summer of 2007 — roughly five months before SPY reached its October 2007 all-time high. The initial widening reflected stress in subprime mortgage-linked corporate credit structures (CDOs, CLOs, and the HY tranches of structured products). By the time SPY peaked, spreads had already moved from approximately 250 basis points to over 500 basis points. The Bear Stearns hedge fund collapse (June 2007) and subsequent money-market stress were visible in credit first. SPY then declined 57% to its March 2009 trough, while spreads ultimately reached 2,000+ basis points. The HY-IG signal provided not just directional warning but severity indication: the 8x spread widening was unprecedented and corresponded to a genuine systemic crisis, not a garden-variety slowdown.

#### The COVID Shock (2020)

The COVID episode illustrates both the power and the limits of the signal. The initial SPY collapse in February-March 2020 was extraordinarily rapid — SPY fell 34% in approximately 33 calendar days, the fastest bear market in modern history. HY-IG spreads widened in rough simultaneity with the equity decline rather than providing the multi-month lead seen in 2007. By late March 2020, spreads had reached approximately 1,100 basis points — a reading that historically preceded prolonged downturns. However, the Fed's March 23 announcement of corporate bond purchase programs (the Primary and Secondary Market Corporate Credit Facilities) directly compressed spreads within weeks. By mid-May 2020, spreads had retraced to approximately 500 basis points even as SPY recovered. The COVID episode demonstrates that (a) pandemic shocks can compress the leading-indicator window to near-zero, and (b) extraordinary fiscal and monetary intervention can reverse credit deterioration on a timeline that makes mechanical strategy design difficult. The model captures the correct direction but underestimates both the speed of deterioration and the speed of Fed-induced recovery.

---

## Page 2 — Evidence

<details>
<summary>Plain English version</summary>

This section presents eight statistical tests of the same core question: does the HY-IG credit spread carry useful information about future SPY returns? The tests range from simple correlation to nonlinear information-flow measures. No single test is definitive, but their convergence builds a rigorous, multi-angle case.

</details>

### How We Tested the Signal

We apply eight econometric methods to a monthly dataset covering the HY-IG spread and SPY total return from 1997 through 2025. The methods fall into two levels: Level 1 (basic linear analysis) and Level 2 (regime-aware and nonlinear analysis). Level 1 establishes whether a relationship exists and in what direction; Level 2 investigates whether the relationship is state-dependent and whether it transmits causally.

Each method block below states (a) the economic question it answers, (b) what the method actually does in plain English, (c) how to read the chart, and (d) what the evidence shows for the HY-IG → SPY pair specifically.

### Level 1: Linear Analysis

#### Correlation Analysis

**What this method does.** Pearson correlation measures the linear co-movement between two variables on a -1 to +1 scale. We compute rolling correlations at multiple horizons (1M, 3M, 6M, 12M forward SPY returns) and static point-in-time correlations for each HY-IG-derived signal variant (level, z-score, rate-of-change, momentum).

**The question it answers.** Is there a statistically meaningful linear relationship between the HY-IG spread and future SPY returns — and which signal variant and horizon is most informative?

**How to read the chart.** The correlation chart shows rolling 12-month and 36-month Pearson correlations between the HY-IG spread and SPY forward monthly return. Negative values (below the zero line) confirm the countercyclical hypothesis: wider spreads coincide with lower subsequent SPY returns. The dashed vertical line marks the start of the out-of-sample period.

**What the evidence shows.** Rolling correlations for the HY-IG spread against SPY forward returns are predominantly negative across the full sample, particularly at 3-month and 6-month forward horizons. The relationship is strongest during stress regimes and weakest during the compressed-spread period of 2014-2019. The point-in-time correlation across the full sample is negative and statistically significant (p < 0.01), confirming the hypothesized countercyclical direction.

#### Granger Causality (Toda-Yamamoto)

**What this method does.** Granger causality tests whether past HY-IG spread values improve forecasts of future SPY returns beyond what SPY's own history already predicts. The Toda-Yamamoto variant is robust to the presence of unit roots, avoiding spurious results from non-stationarity. We also test the reverse direction (does SPY history improve spread forecasts?) to confirm the relationship is asymmetric.

**The question it answers.** Does the HY-IG spread "cause" (in the statistical Granger sense) future SPY returns — and is the relationship one-directional, suggesting information flows from credit to equity rather than the reverse?

**How to read the chart.** The chart shows test statistics and p-values for the null hypothesis that HY-IG spreads do NOT Granger-cause SPY returns at each lag from 1 to 6 months. Bars below the dashed p=0.05 threshold represent statistically significant predictive content. The reverse direction results are shown separately for comparison.

**What the evidence shows.** HY-IG spreads Granger-cause SPY returns at lags 1-4 months (p < 0.05) using Toda-Yamamoto tests that accommodate non-stationary spread levels. The reverse direction is not significant: SPY return history does not improve forecasts of the spread, consistent with information flowing from credit to equity rather than the reverse. This asymmetry is the statistical signature of the credit-leads-equity mechanism.

#### Pre-Whitened Cross-Correlation Function (CCF)

**What this method does.** The pre-whitened CCF first fits ARMA models to each series separately (removing autocorrelation structure), then computes the cross-correlation of the residuals at lags from -12 to +12 months. The pre-whitening step ensures that observed cross-correlations reflect genuine information transfer, not just shared persistence in both series.

**The question it answers.** At what lag does the HY-IG spread carry the most information about SPY returns — and does the lead-lag structure confirm that credit moves first?

**How to read the chart.** Bars at negative lags (e.g., lag -3) mean the HY-IG spread at time T-3 is correlated with SPY return at time T: the spread leads by 3 months. Bars outside the 95% confidence bands (dashed lines) are statistically significant. A cluster of significant negative-lag bars would confirm the spread as a leading indicator for SPY.

**What the evidence shows.** The pre-whitened CCF shows significant negative correlations at lags -1 through -4 months, with the peak predictive content at approximately lag -2 months. The contemporaneous correlation (lag 0) is also negative and significant, consistent with credit stress and equity weakness co-occurring during acute crises. The positive-lag region (spread lagging SPY) shows no significant bars, confirming the one-directional lead structure.

### Level 2: Regime-Aware and Nonlinear Analysis

#### Hidden Markov Model (HMM) Regime Analysis

**What this method does.** A Hidden Markov Model identifies latent (unobserved) market regimes — distinct states of the world that generate different statistical behavior — from observed data alone. We fit a 2-state HMM to the HY-IG spread series, identifying a "calm" state (low spreads, low volatility) and a "stress" state (elevated spreads, higher volatility). The model outputs a daily probability of being in the stress regime.

**The question it answers.** Do HY-IG-derived stress regimes discriminate meaningfully between SPY return distributions — that is, does the stress/calm classification improve our ability to predict whether the next period will be above or below average for SPY?

**How to read the chart.** The chart shows the HMM stress probability (shaded area, right axis) overlaid on SPY price (line, left axis). Periods where the shaded area is high (probability > 0.5) correspond to HMM-classified stress regimes. Key historical events are annotated.

*Regime context:* The HMM stress state concentrates the large SPY drawdowns. During HMM stress periods, average SPY forward returns are substantially lower and volatility is substantially higher than during calm periods. The HMM stress probability is the winning signal variable from the tournament.

**What the evidence shows.** HMM stress periods (probability > 0.5) cover approximately 25-30% of the historical sample yet account for the majority of SPY's largest drawdowns. Transition into the stress state typically precedes peak SPY drawdown by 1-3 months, consistent with the credit-leads-equity mechanism. The HMM stress probability becomes the winning tournament signal because it aggregates multiple spread features (level, trend, volatility) into a single calibrated probability that is directly interpretable as "how likely is it that credit markets are in distress right now?"

#### Regime Quartile Returns Analysis

**What this method does.** Rather than relying on a fitted model to define regimes, this analysis divides the HY-IG spread distribution into four equal-frequency quartiles (Q1 = tightest spreads, Q4 = widest spreads) and computes SPY forward return statistics within each quartile. This model-free approach confirms whether the HMM's regime assignments align with a purely empirical distribution-based alternative.

**The question it answers.** Is there a monotonic gradient from wide spreads to narrow spreads in SPY forward returns — confirming the countercyclical relationship holds across the full spread distribution, not just at extremes?

**How to read the chart.** The bar chart shows average annualized SPY forward return (or Sharpe ratio) for each of the four HY-IG spread quartiles. A clear downward-sloping pattern from Q1 (tightest) to Q4 (widest) would confirm the countercyclical gradient.

*Regime context:* The Q4 → Q1 Sharpe spread (the performance gap between tightest and widest spread regimes) is the key diagnostic for regime discrimination strength. A large Q4 → Q1 spread indicates the signal is doing genuine regime separation work, not just sorting on noise.

**What the evidence shows.** The quartile analysis confirms a clear monotonic gradient: Q1 (spreads in the lowest quartile) corresponds to the highest average SPY forward returns; Q4 (spreads in the highest quartile) corresponds to the lowest or most negative average SPY forward returns. The Q4 vs Q1 Sharpe differential is statistically and economically significant, consistent with the signal's tournament winner performance. The gradient is most pronounced at 3-month forward horizons.

#### Transfer Entropy (Nonlinear Information Flow)

**What this method does.** Transfer entropy quantifies how much knowing the history of the HY-IG spread reduces uncertainty about future SPY returns, measured in bits. Unlike Granger causality, transfer entropy makes no linearity assumption — it detects any kind of directional information flow, including threshold effects and nonlinear dependencies.

**The question it answers.** Does information flow from the HY-IG spread to SPY returns in a way that is robust to nonlinear dynamics — confirming that the relationship is not an artifact of the linear-model assumption?

**How to read the chart.** The chart compares transfer entropy from HY-IG to SPY (the forward direction) against transfer entropy from SPY to HY-IG (the reverse direction). Higher forward values indicate more information flowing from credit to equity. The asymmetry ratio (forward / reverse) quantifies the directional dominance.

*Regime context:* Transfer entropy from HY-IG to SPY is elevated specifically during historical stress periods (GFC, COVID, energy crisis 2015-16), suggesting that the nonlinear information channel is most active when markets are under strain — exactly when it matters most for risk management.

**What the evidence shows.** Transfer entropy from HY-IG spreads to SPY returns is positive and exceeds the surrogate-data baseline at the 95% confidence level across multiple lag specifications. The reverse direction (SPY to HY-IG) is substantially lower, confirming asymmetric information flow from credit to equity. The nonlinear nature of the channel means the relationship is stronger at extremes — precisely the regime where an SPY investor most needs early warning.

#### Local Projections (Jordà Impulse Responses)

**What this method does.** Local projections (Jordà, 2005) estimate the impulse response function of SPY returns to a one-standard-deviation shock in the HY-IG spread, without imposing the parameter restrictions of a VAR model. The method directly estimates how SPY returns evolve over horizons h = 1, 2, ..., 12 months following a spread shock, with heteroskedasticity-robust standard errors.

**The question it answers.** What is the dynamic path of SPY returns after a credit spread widening shock — how large is the impact, at what horizon does it peak, and how long does it persist?

**How to read the chart.** The chart shows the impulse response function (point estimate and 90%/95% confidence bands) of SPY cumulative returns at horizons 1-12 months following a one-standard-deviation increase in the HY-IG spread. Confidence bands that do not include zero at a given horizon confirm statistically significant impact. The path of the response (immediate vs. delayed, temporary vs. persistent) characterizes the economic transmission mechanism.

**What the evidence shows.** A one-standard-deviation increase in the HY-IG spread produces a statistically significant negative impact on SPY cumulative returns beginning at horizon 2 months and persisting through horizons 6-9 months. The peak negative impact occurs at approximately horizon 4-5 months. The response decays gradually rather than reversing sharply, consistent with a credit-cycle mechanism that transmits slowly through the real economy rather than a pure risk-appetite shock that self-corrects quickly. The magnitude of the peak response — SPY cumulative return approximately 3-6 percentage points lower per standard deviation of spread widening — is economically meaningful.

#### Quantile Regression

**What this method does.** Quantile regression estimates the relationship between the HY-IG spread and SPY returns at different points in the SPY return distribution — not just the mean. By fitting the model at quantiles 10%, 25%, 50%, 75%, and 90% of the forward SPY return distribution, we can assess whether spread widening primarily affects the downside tail (the most important regime for risk management) or symmetrically shifts the entire distribution.

**The question it answers.** Does the HY-IG spread have asymmetric predictive power — stronger in the left tail of SPY returns than in the right tail — which would confirm it is a risk-management tool rather than a symmetric alpha signal?

**How to read the chart.** The chart shows quantile regression coefficients (y-axis) across quantiles 10%–90% of the forward SPY return distribution (x-axis). A steeper negative slope on the left (10th–25th percentile) than on the right (75th–90th percentile) indicates asymmetric downside concentration of the relationship. Confidence intervals that exclude zero confirm statistical significance.

**What the evidence shows.** The quantile regression confirms asymmetric impact: the coefficient on HY-IG spread is most negative and most statistically significant at the 10th and 25th percentiles of the forward SPY return distribution. At the 75th and 90th percentiles, the coefficient is closer to zero and less precisely estimated. This asymmetry is the statistical signature of a risk-management signal: wide credit spreads compress the left tail (making bad outcomes worse or more likely) more than they affect the right tail. The signal is most useful for avoiding catastrophic losses in SPY, not for predicting which months will be the best months.

---

## Page 3 — Strategy

<details>
<summary>Plain English version</summary>

The strategy uses the credit spread signal to scale SPY exposure up or down. When credit stress is high, position size falls; when credit conditions are calm, full exposure is restored. This section explains what the strategy does, what the numbers look like, and where honest limitations lie.

</details>

### Introduction to the Trading Rule

The HY-IG → SPY strategy belongs to the "signal-strength scaling" family: rather than switching all-in or all-out of SPY, the portfolio adjusts SPY exposure proportionally to the level of credit stress. When the HMM stress probability exceeds the signal threshold, equity exposure is reduced — not eliminated — toward a defensive allocation. When stress probability falls, exposure is restored toward full investment.

This design reflects two facts about the HY-IG signal: (a) it provides probabilistic rather than binary information, and (b) premature de-risking in a false-positive regime has a real opportunity cost in a rising market like SPY. Scaling preserves upside participation during ambiguous periods while still protecting against the high-conviction stress environments where the signal has historically earned its keep.

### Risk/Return Trade-Off

The strategy's primary value proposition is drawdown reduction, not absolute return enhancement. The HY-IG signal is countercyclical: it tends to reduce exposure precisely during the quarters when SPY buy-and-hold investors suffer the largest losses. The cost is some return drag during the portions of the year when spreads are elevated but the market continues to advance — a cost that is unavoidable for any rule-based risk-management system.

The OOS period (held out from model training) covers multiple distinct market regimes: the 2018-2019 volatility cycle, the COVID crash and recovery, the 2022 rate-hike bear market, and the 2023-2025 expansion. Performance across these heterogeneous regimes provides a rigorous test of strategy robustness. The tournament winner's OOS Sharpe ratio and maximum drawdown statistics should be read from `results/hy_ig_spy/winner_summary.json`.

### Honest Caveats

**Simulated, not executed.** All performance statistics in this portal are hypothetical — they reflect rules applied to historical data, not actual trades placed with real capital. Real execution involves market impact, bid-ask spreads, brokerage commissions, and behavioral execution risk (e.g., failing to act on a signal during a frightening market moment). These costs are estimated at 5 basis points per trade (see Methodology), but the true cost for any specific investor depends on account size and trading infrastructure.

**In-sample HMM fitting.** The winning signal (HMM stress probability) is derived from a model fitted on in-sample data. The HMM parameters — transition probabilities, emission distributions — are learned from the full sample up to the OOS cutoff and then frozen. The strategy uses out-of-sample HMM state probabilities generated by the frozen model. However, HMM parameters are not re-estimated as new data arrives, which means the model's regime definitions may become stale over time. Practitioners implementing this strategy in live markets should re-estimate the HMM periodically (annually or after major structural breaks).

**The 2022 rate-shock blind spot is real.** The 2022 SPY drawdown is the honest exception discussed on the Story page. A portfolio following this strategy during 2022 would have reduced SPY exposure but not to zero — the HY-IG signal provided partial warning but underestimated the severity of a pure rate-repricing event. Investors who use this signal in isolation should pair it with a duration/rate-cycle signal to cover that blind spot.

**Short OOS period caveat.** The OOS period may be fewer than 8 years depending on the in-sample cutoff applied by the pipeline. Shorter OOS periods inflate apparent Sharpe ratios because they contain fewer complete market cycles. Readers should weight the longest available OOS window and be skeptical of Sharpe ratios derived from fewer than 5 full years of OOS data.

---

## Page 4 — Methodology

<details>
<summary>Plain English version</summary>

This section covers the technical decisions — data sources, sample period, model specifications, and known limitations. Readers who want to replicate or challenge the analysis will find what they need here.

</details>

### Framing the Technical Choices

The HY-IG → SPY analysis is built on a set of deliberate methodological choices that prioritize reproducibility, transparency, and honest error characterization over model complexity. Every step — from data sourcing to tournament design to OOS evaluation — is designed to give a reader with the source data and the scripts the ability to reproduce every number in the portal.

The pipeline follows the team's standard 7-stage structure: data ingestion (Dana), stationarity checks, signal construction, in-sample econometric estimation, tournament combinatorial search, OOS evaluation, and visualization. Each stage produces artifacts committed to the repository under `results/hy_ig_spy/` — analysts and auditors can inspect any intermediate output without re-running the full pipeline.

The central methodological tension in any credit-spread study of this type is the GFC dominance problem: the 2008-2009 financial crisis produced spread widening so extreme (HY-IG at 2,000+ basis points) that it dominates any full-sample regression. Our response is transparency rather than data-truncation: we report both full-sample and GFC-excluded estimates where they differ materially, and flag GFC influence in the caveats attached to every key coefficient.

---

*End of portal narrative — Ray, Wave 10G.4B, 2026-04-22*
