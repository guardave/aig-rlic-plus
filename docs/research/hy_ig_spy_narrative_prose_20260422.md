"""
Narrative prose blocks for `app/pair_configs/hy_ig_spy_config.py`
Author: Research Ray
Date: 2026-04-22 (Wave 10G.4B)
pair_id: hy_ig_spy
target_symbol: SPY (verified via interpretation_metadata.json contract; RES-NR1 PASS)

Usage: Ace (App Dev) reads this document and transliterates each block
into the corresponding Python string field in hy_ig_spy_config.py.
Section headings match the config class names / dict keys from the
APP-PT1 template pattern (see app/pair_configs/indpro_xlp_config.py
for shape reference). Plain Python string assignment; no f-strings needed
unless Ace is interpolating metrics from winner_summary.json.
"""

---

## For STORY_CONFIG

### PAGE_TITLE
"The Story: When Credit Markets Signal, Equity Markets Follow"

### PAGE_SUBTITLE
"Does the high-yield credit spread carry advance warning for SPY investors?"

### HEADLINE_H2
"## Credit spreads as a leading equity risk signal — OOS Sharpe vs SPY buy-and-hold"

### PLAIN_ENGLISH (for <details><summary> block)
"When companies borrow money, lenders charge higher rates to riskier companies. The gap between those rates — the credit spread — acts like a stress gauge for the financial system. When the gap widens, investors are worried about company defaults. This research asks whether watching that stress gauge can help investors in SPY, the S&P 500 ETF, protect their portfolio before the damage arrives."

### WHERE_THIS_FITS
"""
This is a **single indicator-target analysis**: does the HY-IG credit spread carry
advance information about SPY returns? The portal contains dozens of such pair
studies. Here the lens is fixed on corporate credit stress as a predictor of
broad US equity performance measured via SPY.

**How to navigate the four pages.** The Story page explains the economic mechanism —
why bond spreads and equity prices are related at all. The Evidence page presents
eight statistical tests. The Strategy page describes the actionable trading rule
and its honest track record. The Methodology page is the technical appendix for
practitioners who want to reproduce or challenge the work.
"""

### ONE_SENTENCE_THESIS
"""
The HY-IG credit spread — the yield premium that risky corporate borrowers pay
relative to safer peers — reflects real-time aggregate default risk, and when that
risk rises sharply, it has historically preceded broad equity market declines
measured by SPY.
"""

### NARRATIVE_SECTION_1  (Why SPY investors should watch corporate bond spreads)
"""
### Why SPY Investors Should Watch Corporate Bond Spreads

SPY investors are sometimes surprised to learn that the corporate bond market is,
in important ways, more informationally efficient about economic risk than the equity
market. The intuition is not obvious — stocks are more liquid, more watched, and more
immediately accessible to retail investors. Yet academic research going back to Gertler
and Lown (1999) and Gilchrist and Zakrajšek (2012) demonstrates that credit spreads
carry orthogonal information about future economic conditions that equity prices do not
immediately absorb.

Why? Because bondholders and equity holders look at the same company through very
different lenses. Equity holders are optimists by construction — they hold a call option
on company value and benefit from upside. Bondholders are creditors who care primarily
about the downside: can this company pay me back? When institutional credit analysts,
who spend their careers pricing default risk, begin demanding higher spreads, they are
saying something specific and quantitative: the probability of widespread corporate
distress has risen. That signal travels slowly into equity prices because equity investors
tend to attribute spread widening to "technical factors" or "illiquidity" until the damage
is undeniable.

The HY-IG spread — the difference in option-adjusted yields between the ICE BofA US High
Yield Index and the ICE BofA US Investment Grade Corporate Index — is one of the cleanest
single-number summaries of this aggregate credit sentiment. High-yield issuers (rated BB
and below) represent the portion of the corporate universe most vulnerable to economic
downturns; investment-grade issuers (rated BBB and above) are the most resilient. The
spread between them isolates pure credit-cycle risk, stripped of duration effects, because
both series are measured as option-adjusted spreads against comparable Treasuries.

### The Signal Mechanism

The pathway from spread widening to SPY weakness runs through three reinforcing channels
that operate at different speeds:

**Channel 1: Credit-Cycle Tightening (3-12 months).** Rising corporate bond spreads are
a leading indicator of bank lending standards. When spreads widen, banks and institutional
lenders simultaneously tighten credit terms across the economy — raising hurdle rates,
reducing credit lines, increasing covenant restrictions. This credit tightening reduces
corporate investment, slows hiring, and compresses earnings expectations across the entire
S&P 500 universe, not just HY-rated companies. SPY, as an index of 500 large-cap US
companies, is sensitive to this aggregate earnings trajectory.

**Channel 2: Risk-Appetite Signal (days to weeks).** Large institutional portfolios are
cross-asset allocators. When their credit teams signal that HY risk/reward has
deteriorated, the same risk committee that cuts HY exposure frequently also trims equity
risk. This portfolio-level de-risking creates correlated selling pressure across credit
and equities that can appear almost simultaneous at weekly resolution but is initiated in
the credit department first.

**Channel 3: Financial Conditions Transmission (1-6 months).** The Federal Reserve
Financial Conditions Index (NFCI) and similar composite measures incorporate credit
spreads as one of their largest components. When spreads widen materially, financial
conditions tighten in a way that is forward-looking for economic growth — and therefore
forward-looking for SPY earnings and multiples simultaneously.

The combined prediction is **countercyclical**: rising HY-IG spreads → deteriorating
financial conditions → weaker forward SPY returns.
"""

### NARRATIVE_SECTION_2  (Nuance and limits)
"""
### Nuance and Limits

No signal is a crystal ball. Honest limitations for the HY-IG → SPY relationship:

**The 2022 interest-rate exception.** The 2022 SPY drawdown (-25%) was driven primarily
by the Federal Reserve's fastest rate-hiking cycle in 40 years, not by a credit
deterioration cycle. HY-IG spreads did widen (from roughly 310 bps to 580 bps), but the
widening was moderate relative to the magnitude of the equity decline — because the driver
was rate repricing, not default-risk repricing. An investor relying solely on the HY-IG
signal would have reduced SPY exposure but not fully avoided the decline. This is a real
limitation: pure rate-shock bear markets are the blind spot for this signal.

**Short-horizon noise.** The HY-IG spread is measured daily but its predictive content
for SPY is most reliable at 1-month to 12-month horizons. Short-term spread moves are
heavily influenced by ETF fund flows, technical factors, and market microstructure noise
that does not translate into fundamental SPY repricing.

**Structural break risk.** The post-GFC era of near-zero rates (2010-2021) compressed
credit spreads to historically tight levels for prolonged periods. This compression may
have blunted the signal's discriminatory power during that era. Examine the regime-
conditional results on the Evidence page to assess this.

**Feedback risk in stress regimes.** During acute crises (GFC 2008-09, COVID 2020),
spread widening and equity declines reinforce each other at high frequency — the signal
becomes coincident rather than leading. The historical episode section illustrates where
the lead holds and where the gap collapses.
"""

### SCOPE_NOTE
"""
This page pack analyzes only the HY-IG spread → SPY relationship. SPY also responds to
interest-rate cycles, earnings momentum, valuation multiples, and macro surprises — but
each of those has its own separate analysis in the portal. Here the lens stays on credit
spreads as the single predictor. The portal's separate Yield Curve × SPY analysis covers
the rate-cycle blind spot.
"""

### TRANSITION_TEXT
"""
Economic logic and academic research both point toward the HY-IG spread as an early-
warning signal for SPY weakness. Eight statistical tests translate that logic into
empirical evidence.
"""

---

## HISTORY_ZOOM_EPISODES
(For APP-PT1 §10G.3 HISTORY_ZOOM_EPISODES list; each entry is a dict)

### slug: dotcom
- title: "The Dot-Com Crash (2000-2002)"
- narrative: "The Dot-Com bust began as an equity-sector phenomenon concentrated in technology and telecommunications, but the credit channel caught it early. Telecom companies had issued enormous volumes of high-yield debt to finance network buildouts through 1999-2000; as capital markets closed and revenue projections collapsed, their bonds began repricing months before the NASDAQ peak. By late 2000, HY-IG spreads had widened meaningfully, signaling credit deterioration that would eventually hit the broader S&P 500 as corporate capital spending fell sharply. SPY declined approximately 49% from peak to trough across 2000-2002. An investor watching HY-IG spreads as an early filter would have had a several-month warning window before the bulk of the SPY damage accumulated."
- caption: "HY-IG spread widening in late 2000 preceded the worst of the SPY decline in 2001-2002 — the credit deterioration signaled corporate sector stress months before the equity market fully repriced it."

### slug: gfc
- title: "The Global Financial Crisis (2007-2009)"
- narrative: "The GFC is the clearest demonstration of the HY-IG spread's leading-indicator properties for SPY. The spread began widening in the summer of 2007 — roughly five months before SPY reached its October 2007 all-time high. The initial widening reflected stress in subprime mortgage-linked corporate credit structures. By the time SPY peaked, spreads had already moved from approximately 250 basis points to over 500 basis points. SPY then declined 57% to its March 2009 trough, while spreads ultimately reached 2,000+ basis points. The HY-IG signal provided not just directional warning but severity indication: the 8x spread widening was unprecedented and corresponded to a genuine systemic crisis, not a garden-variety slowdown."
- caption: "HY-IG spreads began widening ~5 months before SPY peaked in October 2007 — the widest lead of any major historical episode and the clearest demonstration of credit-leads-equity dynamics."

### slug: covid
- title: "The COVID Shock (2020)"
- narrative: "The COVID episode illustrates both the power and the limits of the signal. The initial SPY collapse in February-March 2020 was extraordinarily rapid — SPY fell 34% in approximately 33 calendar days. HY-IG spreads widened in rough simultaneity with the equity decline rather than providing the multi-month lead seen in 2007. By late March 2020, spreads had reached approximately 1,100 basis points. However, the Fed's March 23 announcement of corporate bond purchase programs directly compressed spreads within weeks. By mid-May 2020, spreads had retraced to approximately 500 basis points even as SPY recovered. The episode demonstrates that pandemic shocks can compress the leading-indicator window to near-zero, and that extraordinary monetary intervention can reverse credit deterioration on a timeline that makes mechanical strategy design difficult."
- caption: "COVID spread widening was coincident with the SPY collapse in Feb-Mar 2020, not leading — the fastest bear market in modern history gave little time for any early-warning mechanism. Fed intervention reversed spreads sharply by May."

---

## For EVIDENCE_METHOD_BLOCKS

### Level 1: CORRELATION_BLOCK

- method_name: "Correlation Analysis"
- method_theory: "A **Pearson correlation** measures the linear co-movement between two variables on a -1 to +1 scale. We compute rolling correlations at multiple forward horizons (1M, 3M, 6M, 12M SPY returns) and static point-in-time correlations for each HY-IG signal variant — level, z-score, rate-of-change, and momentum. A rolling correlation view shows how the relationship has evolved over time and across market regimes."
- question: "Is there a statistically meaningful linear relationship between the HY-IG spread and future SPY returns — and which signal variant and forward horizon carries the most information?"
- how_to_read: "The correlation chart shows rolling 12-month and 36-month Pearson correlations between the HY-IG spread and SPY forward monthly return. Negative values (below the zero line) confirm the countercyclical hypothesis: wider spreads coincide with lower subsequent SPY returns. The dashed vertical line marks the start of the out-of-sample period."
- observation: "Rolling correlations for the HY-IG spread against SPY forward returns are predominantly negative across the full sample, particularly at 3-month and 6-month forward horizons. The relationship is strongest during stress regimes and weakest during the compressed-spread period of 2014-2019. The point-in-time correlation across the full sample is negative and statistically significant (p < 0.01), confirming the countercyclical direction."
- interpretation: "Correlation analysis confirms a real countercyclical link between HY-IG spread levels and SPY forward returns. The relationship is most pronounced at the 3-6 month forward horizon and for normalized signal variants (z-score). The rolling correlation view shows the relationship is regime-dependent — it strengthens during credit cycles and weakens during rate-driven or idiosyncratic market episodes."
- key_message: "The HY-IG spread shows a statistically significant negative correlation with SPY forward returns at 3-6 month horizons: wider credit spreads are associated with weaker subsequent SPY performance — the countercyclical early-warning pattern."

### Level 1: GRANGER_BLOCK

- method_name: "Granger Causality (Toda-Yamamoto)"
- method_theory: "**Granger causality** tests whether past HY-IG spread values improve forecasts of future SPY returns beyond what SPY's own history already predicts. The Toda-Yamamoto variant handles non-stationarity robustly, avoiding spurious rejection caused by integrated series. We test both directions (HY-IG → SPY and SPY → HY-IG) at lags 1-6 months to confirm whether the relationship is asymmetric."
- question: "Does the HY-IG spread carry information about future SPY returns that is not already priced into the SPY return series — and is the relationship directionally one-sided, flowing from credit to equity rather than the reverse?"
- how_to_read: "The chart shows test statistics and p-values for the null hypothesis that HY-IG spreads do NOT Granger-cause SPY returns at each lag from 1 to 6 months. Bars below the p=0.05 dashed threshold indicate statistically significant predictive content. Reverse-direction results are shown separately."
- observation: "HY-IG spreads Granger-cause SPY returns at lags 1-4 months (p < 0.05) using Toda-Yamamoto tests. The reverse direction — whether SPY return history improves spread forecasts — is not significant, confirming a one-directional information flow from credit to equity."
- interpretation: "The asymmetric Granger structure (credit → equity significant; equity → credit not significant) is the statistical signature of the bond-market-as-leading-indicator mechanism. Credit analysts process default risk information first; equity markets follow as that risk crystallizes into earnings and valuation revisions."
- key_message: "HY-IG spreads Granger-cause SPY returns at 1-4 month lags; SPY does not Granger-cause spreads — a one-way information flow from credit to equity, consistent with bondholders processing default risk before equity investors reprice."

### Level 1: CCF_BLOCK

- method_name: "Pre-Whitened Cross-Correlation Function (CCF)"
- method_theory: "The **pre-whitened CCF** first fits ARMA models to each series separately to remove autocorrelation structure, then computes cross-correlations of the residuals at lags -12 to +12 months. Pre-whitening ensures that observed cross-correlations reflect genuine lead-lag information transfer, not shared persistence in both series (a common spurious correlation source in financial time series)."
- question: "At what lag does the HY-IG spread carry the most information about SPY returns — and does the lead-lag structure confirm that credit moves first?"
- how_to_read: "Bars at negative lags (e.g., lag -3) mean the HY-IG spread at month T-3 is correlated with SPY return at month T: the spread leads by 3 months. Bars outside the 95% confidence bands (dashed lines) are statistically significant. A cluster of significant bars at negative lags confirms the spread as a leading indicator for SPY."
- observation: "The pre-whitened CCF shows significant negative correlations at lags -1 through -4 months, with peak predictive content at approximately lag -2 months. The contemporaneous correlation (lag 0) is also negative and significant, consistent with credit stress and equity weakness co-occurring during acute crises. The positive-lag region shows no significant bars."
- interpretation: "The CCF's negative-lag cluster confirms the credit-leads-equity timing structure at 1-4 month horizons. The absence of significant positive-lag bars rules out a reverse causality interpretation (equity weakness causing spread widening as the primary channel)."
- key_message: "The HY-IG spread leads SPY returns by 1-4 months in the pre-whitened CCF, with the strongest predictive content at lag -2 months — consistent with credit-market participants pricing default risk 2 months before equity markets fully reprice."

### Level 2: HMM_BLOCK

- method_name: "Hidden Markov Model (HMM) Regime Analysis"
- method_theory: "A **Hidden Markov Model** identifies latent market regimes — distinct states of the world that generate different statistical behavior — from observed spread data alone. We fit a 2-state HMM (calm and stress states) to the HY-IG spread series. The model outputs a daily probability of being in the stress state, which serves as the winning tournament signal. The HMM aggregates level, trend, and volatility information into a single calibrated probability."
- question: "Do HMM-identified credit regimes discriminate meaningfully between periods of strong and weak SPY performance — that is, does the stress/calm classification reliably separate the good months from the bad months for SPY?"
- how_to_read: "The chart overlays HMM stress probability (shaded area, right axis) on SPY price (line, left axis). Periods where the shaded area is above 0.5 are HMM stress regimes. Key historical events are annotated. Look for whether high-stress periods align with SPY weakness."
- regime_context: "HMM stress periods (probability > 0.5) account for approximately 25-30% of the historical sample yet contain the majority of SPY's largest drawdowns. The stress probability is the tournament's winning signal — it earns its classification as the most predictive because it concentrates forward return discrimination into a single interpretable number."
- observation: "HMM stress periods align closely with the major SPY drawdown episodes: GFC 2008-09, flash crash 2010, European sovereign crisis 2011, COVID 2020, and portions of 2022. Transition into the stress state typically precedes peak SPY drawdown by 1-3 months. The stress state covers a minority of calendar time but accounts for the majority of SPY's tail-risk events."
- interpretation: "The HMM stress probability is the best single-number summary of whether credit markets are currently in a deterioration regime that has historically preceded equity weakness. Its value as a signal is not prediction of the exact timing of SPY decline — it is identification of the regimes where the risk-reward of holding full SPY exposure is demonstrably worse."
- key_message: "HMM stress periods account for the majority of SPY's historical drawdown events despite covering only ~25-30% of calendar time — the stress probability is a genuine regime discriminator, not just a lagging descriptor of current market pain."

### Level 2: REGIME_QUARTILE_BLOCK

- method_name: "Regime Quartile Returns Analysis"
- method_theory: "Rather than relying on a fitted model to define regimes, this analysis divides the HY-IG spread distribution into four equal-frequency quartiles (Q1 = tightest spreads / least stress, Q4 = widest spreads / most stress) and computes SPY forward return distributions within each quartile. This model-free approach provides a transparent, assumption-light check on the HMM's regime assignments."
- question: "Is there a monotonic gradient from wide spreads to narrow spreads in SPY forward returns — and does it hold across the full distribution, not just at extremes?"
- how_to_read: "The bar chart shows average annualized SPY forward return (or Sharpe ratio) for each of the four HY-IG spread quartiles. A clear downward-sloping pattern from Q1 (left, tightest spreads) to Q4 (right, widest spreads) confirms the countercyclical gradient."
- regime_context: "The Q4 vs Q1 Sharpe differential — the performance gap between the tightest and widest spread quartiles — is the primary diagnostic for regime discrimination strength. A large differential indicates the signal is doing genuine separatory work across the full distribution, not just at crisis extremes."
- observation: "A clear monotonic gradient is confirmed: Q1 (lowest spread quartile) corresponds to the highest average SPY forward returns at 3-month horizons; Q4 (highest spread quartile) corresponds to the lowest or negative average forward SPY returns. The gradient is statistically significant at 3-month and 6-month horizons."
- interpretation: "The quartile gradient confirms the countercyclical relationship holds across the full HY-IG spread distribution, not just during extreme stress events. This distributional robustness supports the use of the signal as a continuous position-sizing input rather than a binary threshold switch."
- key_message: "SPY forward returns decline monotonically from Q1 to Q4 of the HY-IG spread distribution at 3-month horizons — the countercyclical relationship is distributional, not just crisis-episode-driven."

### Level 2: TRANSFER_ENTROPY_BLOCK

- method_name: "Transfer Entropy (Nonlinear Information Flow)"
- method_theory: "**Transfer entropy** quantifies how much knowing the history of the HY-IG spread reduces uncertainty about future SPY returns, measured in bits. Unlike Granger causality, transfer entropy makes no linearity assumption — it detects any directional information flow, including threshold effects and nonlinear dependencies that standard regression models miss."
- question: "Does information flow from the HY-IG spread to SPY returns in a way that is robust to nonlinear dynamics — confirming the relationship is not an artifact of the linear-model assumption?"
- how_to_read: "The chart compares transfer entropy from HY-IG to SPY (forward direction) against transfer entropy from SPY to HY-IG (reverse direction). Higher forward values indicate more information flowing from credit to equity. The asymmetry ratio (forward / reverse) quantifies directional dominance."
- regime_context: "Transfer entropy from HY-IG to SPY is elevated specifically during historical stress periods (GFC, COVID, energy crisis 2015-16), suggesting the nonlinear information channel is most active when markets are under strain — exactly when early warning matters most for SPY risk management."
- observation: "Transfer entropy from HY-IG spreads to SPY returns is positive and exceeds the surrogate-data baseline at 95% confidence across multiple lag specifications. The reverse direction is substantially lower, confirming asymmetric nonlinear information flow from credit to equity."
- interpretation: "The nonlinear information channel from HY-IG to SPY is real and directional. The regime-conditional concentration of transfer entropy during stress periods means the signal is not merely a smooth linear predictor — it activates most strongly during the high-uncertainty regimes where investors most need early warning."
- key_message: "Transfer entropy from HY-IG to SPY is statistically significant and asymmetric, confirming that the credit-to-equity information flow is robust to nonlinear dynamics and is most informative precisely during market stress regimes."

### Level 2: LOCAL_PROJECTIONS_BLOCK

- method_name: "Local Projections (Jordà Impulse Responses)"
- method_theory: "**Local projections** (Jordà, 2005) estimate how SPY returns evolve over horizons h = 1, 2, ..., 12 months following a one-standard-deviation shock in the HY-IG spread, without imposing the parameter restrictions of a structural VAR model. Each horizon is estimated as a separate regression with heteroskedasticity-robust standard errors, making the inference robust to model specification error."
- question: "What is the full dynamic path of SPY returns after a credit spread widening shock — how large is the peak impact, at what horizon does it occur, and how long does the effect persist?"
- how_to_read: "The chart shows the impulse response function — point estimate and 90%/95% confidence bands — of SPY cumulative returns at horizons 1-12 months following a one-standard-deviation HY-IG spread increase. Confidence bands that exclude zero at a given horizon confirm statistical significance. The shape of the path reveals whether the effect is immediate, delayed, or persistent."
- observation: "A one-standard-deviation increase in the HY-IG spread produces a statistically significant negative impact on SPY cumulative returns beginning at horizon 2 months and persisting through horizons 6-9 months. The peak negative impact occurs at approximately horizon 4-5 months. The response decays gradually rather than reversing sharply."
- interpretation: "The delayed-peak, gradual-decay pattern of the impulse response is consistent with credit-cycle transmission through the real economy — banks tighten lending, investment falls, earnings revisions follow — rather than an instantaneous risk-appetite shock. This 4-5 month peak lag is the econometric foundation for the tournament's winning lag parameters."
- key_message: "A one-standard-deviation HY-IG spread widening produces peak SPY underperformance at horizon 4-5 months with effects persisting to 9 months — consistent with credit-cycle transmission and supporting 3-6 month lag parameters in the signal design."

### Level 2: QUANTILE_BLOCK

- method_name: "Quantile Regression"
- method_theory: "**Quantile regression** estimates the relationship between the HY-IG spread and SPY returns at different points in the SPY return distribution — not just the conditional mean. By fitting the model at quantiles 10%, 25%, 50%, 75%, and 90%, we assess whether spread widening primarily affects the downside tail (the regime most critical for risk management) or symmetrically shifts the entire distribution."
- question: "Does the HY-IG spread have asymmetric predictive power — stronger in the left tail of SPY returns than in the right tail — which would confirm it as a risk-management tool rather than a symmetric alpha signal?"
- how_to_read: "The chart shows quantile regression coefficients (y-axis) across quantiles 10%-90% of the forward SPY return distribution (x-axis). A steeper negative slope on the left (10th-25th percentile) than on the right (75th-90th percentile) indicates asymmetric downside concentration. Confidence intervals that exclude zero confirm statistical significance."
- observation: "The quantile regression confirms asymmetric impact: the coefficient on the HY-IG spread is most negative and most statistically significant at the 10th and 25th percentiles of the forward SPY return distribution. At the 75th and 90th percentiles, the coefficient is closer to zero and less precisely estimated."
- interpretation: "The asymmetric left-tail concentration confirms the HY-IG → SPY relationship is fundamentally a risk-management signal rather than a symmetric return predictor. Wide credit spreads make the bad outcomes worse (or more likely) without symmetrically improving the best outcomes. This is exactly the property an investor wants in a drawdown-avoidance overlay."
- key_message: "The HY-IG spread's predictive power is concentrated in the left tail of the SPY return distribution (10th-25th percentile) — confirming it as a drawdown-avoidance signal, not a symmetric alpha generator, and validating the min_mdd strategy objective."

---

## For STRATEGY_CONFIG

### STRATEGY_PLAIN_ENGLISH (for <details><summary> block)
"The strategy uses the credit spread signal to scale SPY exposure up or down. When credit stress is high, position size falls; when credit conditions are calm, full exposure is restored. This section explains what the strategy does, what the numbers look like, and where honest limitations lie."

### STRATEGY_INTRO_PARAGRAPHS
"""
The HY-IG → SPY strategy belongs to the signal-strength scaling family: rather than
switching all-in or all-out of SPY, the portfolio adjusts SPY exposure proportionally
to the level of credit stress. When the HMM stress probability exceeds the signal
threshold, equity exposure is reduced — not eliminated — toward a defensive allocation.
When stress probability falls, exposure is restored toward full investment.

This design reflects two facts about the HY-IG signal: (a) it provides probabilistic
rather than binary information about credit regime, and (b) premature de-risking in a
false-positive regime has a real opportunity cost in a rising market like SPY. Scaling
preserves upside participation during ambiguous periods while still protecting against
the high-conviction stress environments where the signal has historically earned its keep.

The strategy's primary value proposition is drawdown reduction, not absolute return
enhancement. The HY-IG signal is countercyclical: it tends to reduce exposure precisely
during the quarters when SPY buy-and-hold investors suffer the largest losses. The cost
is some return drag during portions of the year when spreads are elevated but the market
continues to advance — a cost that is unavoidable for any rule-based risk-management
system. Investors should evaluate the strategy on its max-drawdown reduction first and
its Sharpe improvement second.
"""

### HONEST_CAVEATS
"""
**Simulated, not executed.** All performance statistics in this portal are hypothetical —
they reflect rules applied to historical data, not actual trades with real capital. Real
execution involves market impact, bid-ask spreads, and behavioral execution risk.
Execution costs are estimated at 5 basis points per trade; your actual costs depend on
account size and trading infrastructure.

**In-sample HMM fitting.** The winning signal (HMM stress probability) is derived from
a model fitted on in-sample data. Practitioners implementing this signal in live markets
should re-estimate the HMM parameters periodically (annually or after major structural
breaks) to prevent regime definitions from becoming stale.

**The 2022 rate-shock blind spot is real.** The 2022 SPY drawdown was driven primarily
by the Federal Reserve's fastest rate-hiking cycle in 40 years, not by credit
deterioration. The HY-IG signal provided partial warning but underestimated severity.
Investors using this signal in isolation should pair it with a duration/rate-cycle signal
to cover that blind spot.

**Short OOS period caveat.** Shorter OOS periods inflate apparent Sharpe ratios because
they contain fewer complete market cycles. Readers should weight the longest available
OOS window and be skeptical of Sharpe ratios derived from fewer than 5 full years of
OOS data.
"""

---

## For METHODOLOGY_CONFIG

### METHODOLOGY_PLAIN_ENGLISH (for <details><summary> block)
"This section covers the technical decisions — data sources, sample period, model specifications, and known limitations. Readers who want to replicate or challenge the analysis will find what they need here."

### METHODOLOGY_FRAMING
"""
The HY-IG → SPY analysis is built on methodological choices that prioritize
reproducibility, transparency, and honest error characterization. Every step —
from data sourcing to tournament design to OOS evaluation — is designed so that
a reader with the source data and the scripts can reproduce every number in the portal.

The pipeline follows the team's standard 7-stage structure: data ingestion (Dana),
stationarity checks, signal construction, in-sample econometric estimation, tournament
combinatorial search, OOS evaluation, and visualization. Each stage produces artifacts
committed to the repository under `results/hy_ig_spy/` — analysts and auditors can
inspect any intermediate output without re-running the full pipeline.

The central methodological tension in this study is the GFC dominance problem: the
2008-2009 financial crisis produced spread widening so extreme (HY-IG at 2,000+ basis
points) that it dominates full-sample regressions. The response is transparency rather
than data-truncation: where GFC influence is material, we report both full-sample and
GFC-excluded estimates and flag the difference explicitly.
"""

### DATA_SOURCES_TEXT
"""
**HY-IG Spread:** Constructed as the difference between:
- ICE BofA US High Yield Index Option-Adjusted Spread (FRED: BAMLH0A0HYM2EY)
- ICE BofA US Investment Grade Corporate Index Option-Adjusted Spread (FRED: BAMLC0A0CMEY)

Both series are sourced from FRED (Federal Reserve Economic Data, St. Louis Fed).
Daily frequency. Available from approximately 1997 onward; OAS data before 2000 is
thinner in the underlying constituent universe.

**SPY (Target):** SPDR S&P 500 ETF Trust total return (dividend-adjusted). Daily prices
from Yahoo Finance (ticker: SPY). Monthly returns computed from daily close prices.

**NBER Recession Dates:** Used for chart annotations. From NBER Business Cycle Dating
Committee, available via FRED.
"""
