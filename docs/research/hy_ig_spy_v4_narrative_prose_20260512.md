"""
Narrative prose blocks for `app/pair_configs/hy_ig_spy_v4_from_scratch_config.py`
Author: Research Ray
Date: 2026-05-12 (v4 from scratch)
pair_id: hy_ig_spy_v4_from_scratch
target_symbol: SPY
indicator: hy_ig_spread
Evidence status at time of writing: search-grade (Evan's exam not yet run)
RES-EGL1: applied — all language is search-grade; no validated/durable-edge/high-confidence language

Usage: Ace (App Dev) reads this document and transliterates each block
into the corresponding Python string field in hy_ig_spy_v4_from_scratch_config.py.
Section headings match config class names / dict keys from the APP-PT1 template
pattern (see app/pair_configs/indpro_xlp_config.py for shape reference).

CRITICAL: This is a v4 clean-rebuild brief. Do NOT import numerical findings
(OOS Sharpe, regime stats, tournament results) from hy_ig_spy v1/v2/v3 into this
config. Placeholders are intentional — Evan fills them from v4 exam artifacts.
"""

---

## For STORY_CONFIG

### PAGE_TITLE
"The Story: When Credit Markets Warn, Equity Investors Should Listen"

### PAGE_SUBTITLE
"Does the high-yield credit spread carry an early signal for SPY investors?"

### HEADLINE_H2
"## Credit stress as an early-warning signal for SPY — what the evidence so far suggests"

### PLAIN_ENGLISH
"When companies borrow money in the bond market, lenders charge higher interest rates to riskier (high-yield) borrowers than to safer (investment-grade) borrowers. The gap between those rates — the HY-IG credit spread — acts like a financial stress gauge. When the gap widens sharply, bond investors are pricing in higher risk of corporate defaults and tighter lending conditions. This research asks whether watching that stress gauge gives SPY investors an advance signal worth paying attention to — before the damage shows up in equity prices."

### WHERE_THIS_FITS
"""
This is a **single indicator-target analysis**: does the HY-IG credit spread carry
advance information about SPY returns? The portal contains multiple such pair studies,
each examining a different predictor of US equity performance. Here the lens is on
corporate credit stress — specifically, the option-adjusted yield premium that
high-yield (rated BB and below) corporate borrowers pay relative to investment-grade
(rated BBB and above) borrowers — as a candidate leading indicator for SPY.

**How to navigate the four pages.** The Story page explains the economic mechanism:
why corporate bond yields and equity prices might be related at all. The Evidence page
presents the statistical tests. The Strategy page describes what a signal-based rule
would have looked like historically. The Methodology page is the technical appendix
for readers who want to understand or replicate the analysis.

This is v4, a clean rebuild from first principles. Prior versions (v1–v3) of the
HY-IG × SPY pair have been retired. This version uses updated data through the
present and a fresh analytical framework aligned to the current Dashboard Page
Standard. All prior performance numbers are not carried forward — they are replaced
by v4 exam outputs once available.
"""

### ONE_SENTENCE_THESIS
"""
The HY-IG credit spread — the yield premium demanded by lenders to high-yield
corporate borrowers relative to safer peers — is consistent with theory as a
leading indicator of broad US equity stress, because the corporate bond market may
process aggregate default risk before that risk is fully absorbed by equity prices.
"""

### NARRATIVE_SECTION_1
"""
### Why SPY Investors Might Watch Corporate Bond Spreads

Corporate bond markets and equity markets look at the same companies through
fundamentally different lenses. Equity holders own a call option on company value —
they benefit from upside and can be patient through temporary weakness. Bondholders
are creditors: they care primarily about whether they will be repaid. When
institutional credit analysts — who spend their careers pricing default risk — begin
demanding higher yields, they are making a specific quantitative judgment that the
probability of widespread corporate distress has increased. That judgment may travel
into equity prices with a delay, because equity investors tend to attribute early
spread widening to technical factors or market microstructure noise until the evidence
is unambiguous.

Academic research is consistent with this intuition. Gertler and Lown (1999) document
that the high-yield spread carries non-redundant information about future real
economic activity, above and beyond what the yield curve already predicts. Gilchrist
and Zakrajšek (2012) find that their GZ credit spread — and particularly its
"excess bond premium" component, which strips out expected default losses — suggests
predictive content for US output and equity returns at monthly horizons. The
theoretical channel they identify runs through financial intermediary risk appetite:
when banks and institutional lenders face balance sheet constraints, they tighten
lending terms economy-wide, compressing corporate investment and earnings growth
across the S&P 500 universe. Fama and French (1989) document a related pattern
going back to the 1920s using the yield premium between low-grade and high-grade
bonds as a predictor of stock and bond excess returns.

The HY-IG spread — the difference in option-adjusted spreads between the ICE BofA
US High Yield Index (FRED: BAMLH0A0HYM2) and the ICE BofA US Investment Grade
Corporate Index (FRED: BAMLC0A0CM) — is one accessible, real-time summary of this
aggregate credit condition. The option-adjusted construction controls for embedded
call options in corporate bonds, making the spread comparisons cleaner across the
two index components. The HY component captures the most default-vulnerable segment
of the corporate universe; the IG component provides the risk-free-adjacent baseline.
Their difference isolates the pure credit-cycle risk premium, stripped of duration
effects (since both are measured as spreads over comparable Treasuries).

### Three Hypothesized Channels

The theoretical pathway from HY-IG spread widening to SPY weakness may run through
at least three reinforcing channels, operating at different speeds:

**Channel 1 — Credit-Cycle Tightening (3-12 months).** Rising spreads are
historically consistent with tightening bank lending standards. When spreads widen,
institutional lenders simultaneously tighten credit terms — raising hurdle rates,
reducing revolving credit lines, adding covenant restrictions. This tightening reduces
corporate capital expenditure, slows hiring, and — with a lag — compresses earnings
expectations across the S&P 500. SPY, as an index of 500 large-cap US companies,
is sensitive to this aggregate earnings trajectory.

**Channel 2 — Portfolio Risk Appetite (days to weeks).** Large institutional
portfolios are cross-asset allocators. When credit teams signal that high-yield
risk-reward has deteriorated, the same risk committee that reduces HY exposure
may simultaneously trim equity risk. This portfolio-level de-risking can create
correlated selling across credit and equities that appears near-simultaneous at
weekly resolution but is consistent with credit being the initiating signal.

**Channel 3 — Financial Conditions Transmission (1-6 months).** Composite financial
conditions indexes — such as the Chicago Fed's NFCI — incorporate credit spreads
among their largest components. When spreads widen materially, financial conditions
tighten in a way that research suggests is forward-looking for economic growth and,
therefore, for SPY earnings and valuations.

These channels collectively suggest a **countercyclical** hypothesis:
rising HY-IG spreads → deteriorating financial conditions → weaker forward SPY returns.
This is a hypothesis to be tested — not a result to be assumed.
"""

### NARRATIVE_SECTION_2
"""
### Honest Limits of the Hypothesis

The HY-IG → SPY hypothesis is theoretically grounded and empirically consistent with
the literature, but it carries known limitations that anyone using this analysis
should understand.

**The rate-shock blind spot.** The credit-cycle hypothesis describes default-risk-
driven bear markets. When equity declines are driven primarily by interest rate
repricing rather than by rising default probabilities — as the 2022 drawdown appears
to have been — the HY-IG spread may give only partial warning. In 2022, the
Federal Reserve's fastest rate-hiking cycle in 40 years drove a ~25% SPY decline.
HY-IG spreads did widen (from roughly 310 bps to 580 bps), but the widening was
moderate relative to the magnitude of the equity decline, because the equity
drawdown was primarily a duration/valuation repricing story, not a corporate-default
story. An investor relying solely on the HY-IG signal as an SPY early-warning gauge
would have received a partial signal, not a full one.

**Short-horizon noise.** HY-IG spreads are measured daily, but the literature's
consistent message is that predictive content for equity is most reliable at 1-6
month forward horizons. Day-to-day spread moves are heavily influenced by ETF fund
flows, index rebalancing, and market microstructure effects that do not transmit
to fundamental SPY repricing.

**The compressed-spread era.** The post-GFC period of near-zero interest rates
(approximately 2010-2021) held HY-IG spreads at historically tight levels for
extended periods. During this era, there was less cross-sectional variation in
spread levels for any model to exploit, which may have blunted the signal's
discriminatory power. Regime-conditional evidence on the Evidence page should
be examined for subsample performance.

**Fed backstop risk.** The COVID episode (2020) illustrates that extraordinary
monetary policy interventions — specifically the Federal Reserve's corporate bond
purchase facilities announced in March 2020 — can reverse spread widening on a
timeline of weeks. This compressed what might otherwise have been a multi-month
leading signal into a near-simultaneous relationship. If Fed corporate bond purchase
programs become a standing tool, the historical leading-indicator window may
permanently compress during acute crises.

**This is early evidence.** All statistical findings on this portal for the v4 pair
are search-grade. The formal out-of-sample exam has not yet been run. Readers should
treat every number and chart as hypothesis-motivating evidence, not as a validated
investment signal.
"""

### SCOPE_NOTE
"""
This page pack analyzes only the HY-IG credit spread → SPY relationship. SPY also
responds to interest-rate cycles, earnings momentum, valuation multiples, and macro
surprises. Each of those has its own separate analysis in the portal. Here the lens
stays fixed on corporate credit spreads as the single predictor. The portal's
Yield Curve × SPY analysis covers the rate-cycle dynamics identified as the 2022
blind spot above.
"""

### TRANSITION_TEXT
"""
Theory and academic literature are both consistent with the HY-IG spread carrying
early information about SPY weakness. The Evidence page presents the statistical
tests that examine whether that theoretical prediction holds in the data — and at
which lags, under which conditions, and with what degree of reliability.
"""

---

## HISTORY_ZOOM_EPISODES

(For APP-PT1 HISTORY_ZOOM_EPISODES list. Canonical slugs per history_zoom_events_registry.json v1.1.0.
All five credit_spread category episodes included. Slugs: dotcom, gfc, covid, taper_2018, inflation_2022.)

### slug: dotcom

- title: "The Dot-Com Bust (2000-2003)"
- narrative: "The Dot-Com bust began as an equity-sector phenomenon concentrated in technology and telecommunications, but the corporate credit market caught the underlying stress early. Telecom companies had issued enormous volumes of high-yield debt to finance network buildouts through 1999-2000. As capital market conditions shifted and revenue projections for 'new economy' firms collapsed, high-yield bond prices began repricing — and HY-IG spreads widened — before the worst of the SPY equity damage accumulated. By late 2000, spread widening was already underway, suggesting the credit market was pricing in a genuine deterioration in corporate fundamentals ahead of the equity market's full recognition. This episode is historically consistent with the credit-leads-equity hypothesis: bond investors, focused on downside scenarios, appear to have incorporated the coming recession earlier than equity investors primed for continued gains. SPY declined approximately 49% from March 2000 to October 2002. The credit early-warning window, if it operated as the theory suggests, would have given an investor tracking HY-IG spreads an advance signal — though the precise lead time requires the formal statistical test on the Evidence page to characterize rigorously."
- caption: "HY-IG spread widening in late 2000 preceded the worst of SPY's 2001-2002 decline — consistent with the credit-leads-equity hypothesis, though the lead time and statistical significance are questions for the Evidence page rather than this summary."

### slug: gfc

- title: "The Global Financial Crisis (2007-2009)"
- narrative: "The Global Financial Crisis is frequently cited as the clearest historical demonstration of the HY-IG spread's potential leading-indicator properties for equity. The spread began widening measurably in the summer of 2007 — several months before SPY reached what proved to be its October 2007 peak. The initial widening reflected stress in subprime mortgage-linked corporate credit structures, then expanded across the broader high-yield universe as lending conditions tightened. SPY subsequently declined approximately 57% to its March 2009 trough, while the HY-IG spread ultimately reached levels that had not been seen since the early 1990s. The GFC episode is important for another reason as well: it illustrates the severity-signaling potential of the spread. A very wide spread does not merely suggest 'some weakness ahead' — during 2008-09, the extreme spread levels were consistent with a genuine systemic crisis. Whether these spread levels provide usable signals at the specific thresholds tested on the Strategy page is an empirical question the exam must answer. What is clear historically is that the directionality and approximate timing of the relationship were present during the GFC."
- caption: "HY-IG spreads began widening months before SPY's October 2007 peak — historically the clearest episode supporting the credit-leads-equity timing hypothesis. GFC dominates full-sample regression leverage; subsample results excluding 2007-09 are reported separately on the Evidence page."

### slug: covid

- title: "The COVID-19 Shock (2020)"
- narrative: "The COVID-19 episode illustrates both a potential limit and a potential feature of the HY-IG → SPY relationship. The initial SPY collapse in February-March 2020 was extraordinarily rapid — approximately 34% in about 33 calendar days — and HY-IG spreads widened in rough simultaneity with the equity decline rather than providing the multi-month lead seen in 2007. The speed of the shock compressed the leading-indicator window to near-zero: by the time any monthly-frequency signal could be observed, the worst of the equity damage had already occurred. This is consistent with the literature finding that pandemic shocks can overwhelm the credit-cycle transmission mechanism. However, the subsequent behavior is also illustrative: the Federal Reserve's March 23, 2020 announcement of corporate bond purchase programs (PMCCF and SMCCF) produced a rapid compression of HY-IG spreads even as the fundamental macroeconomic damage was still unfolding. Spreads retraced from approximately 1,100 bps to 500 bps within weeks of the announcement, while SPY began its recovery. The COVID episode suggests that the Fed's capacity to intervene directly in the corporate bond market can compress — and potentially reverse — the spread signal on a timeline that makes mechanical signal interpretation difficult during acute policy-action periods."
- caption: "COVID spread widening was largely coincident with the SPY collapse in Feb-Mar 2020, not leading — the fastest modern bear market gave little time for any early-warning mechanism. Fed corporate bond facility announcement in March 2020 reversed spreads sharply within weeks."

### slug: taper_2018

- title: "The 2018 Fed Tightening and Q4 Selloff"
- narrative: "The 2018 episode provides a useful non-recessionary stress test for the HY-IG → SPY relationship. The Federal Reserve's post-GFC tightening cycle began in late 2015 and accelerated in 2018; Chair Powell's October 2018 remarks that the Fed funds rate was 'a long way from neutral' triggered a sharp risk-off episode. HY-IG spreads widened from approximately 330 bps to 540 bps through Q4 2018, the widest non-recessionary print of that cycle. SPY declined approximately 20% from its September 2018 peak to the December 24 Christmas Eve low. Critically, the spread widening and equity weakness were compressed into roughly the same 3-month window, with limited evidence of the multi-month leading gap seen in 2007. The subsequent recovery was rapid: Chair Powell's January 2019 'patient' pivot remarks at the AEA panel initiated a rapid spread tightening and equity recovery. The 2018 episode is relevant because it shows the signal can register non-recessionary stress but may do so with a shorter lead — more as a coincident or short-horizon indicator than a 3-6 month advance warning during non-crisis tightening cycles."
- caption: "HY-IG spread widening in Q4 2018 was largely concurrent with the SPY selloff — useful as a non-recessionary stress episode that tests whether the lead time collapses outside formal recessions. The Powell pivot in January 2019 reversed both spread and equity almost simultaneously."

### slug: inflation_2022

- title: "The 2022 Inflation and Rate-Shock Drawdown"
- narrative: "The 2022 episode is the most important recent test case for the HY-IG → SPY hypothesis — and it highlights the signal's most significant known limitation. The Federal Reserve's fastest rate-hiking cycle since the early 1980s drove a roughly 25% SPY decline in 2022. HY-IG spreads did widen — from approximately 310 bps at the January SPY peak to a maximum of roughly 580 bps around the October SPY trough — but this widening was modest by historical standards relative to the magnitude of the equity decline. The reason is theoretically clear: the 2022 drawdown was primarily a valuation and duration repricing event (equities became less valuable as discount rates rose sharply) rather than a credit-cycle deterioration event (companies did not begin defaulting at elevated rates). When the mechanism is rate-repricing rather than default-repricing, the HY-IG spread — which is calibrated to measure credit-cycle risk — may give only a partial signal. The 2022 episode should be examined carefully in the Evidence page's regime-conditional results and in any strategy evaluation: it is the clearest real-world demonstration that the HY-IG signal has a rate-shock blind spot. An investor relying solely on HY-IG as an equity risk signal would have reduced exposure but not avoided the bulk of the 2022 drawdown."
- caption: "The 2022 SPY drawdown (-25%) was driven primarily by rate repricing, not credit-cycle deterioration. HY-IG spreads widened only modestly (310 to 580 bps) relative to the equity decline — the clearest real-world illustration of the signal's rate-shock blind spot."

---

## EVIDENCE_METHOD_BLOCKS

(For APP-PT1 Evidence page config. Canonical 8-element structure per RES-EP1.
Observations and interpretations are search-grade placeholders — Evan replaces with
actual v4 findings at exam time. pair_id: hy_ig_spy_v4_from_scratch.)

### Level 1: CORRELATION_BLOCK

- method_name: "Correlation Analysis"
- method_theory: "A **Pearson correlation** (a measure of linear co-movement ranging from -1 to +1) computed between the HY-IG spread and forward SPY monthly returns at multiple horizons (1M, 3M, 6M, 12M). Rolling correlations — computed over a moving window of 12 or 36 months — show how the relationship has evolved through different market regimes rather than collapsing the full history into a single number. Multiple signal variants (level, z-score, rate of change) are tested simultaneously."
- question: "Is there a statistically meaningful negative linear relationship between the HY-IG spread and subsequent SPY returns — and which signal variant and forward horizon shows the most consistent association?"
- how_to_read: "The rolling correlation chart shows 12-month and 36-month Pearson correlations between the HY-IG spread and SPY forward monthly returns. Values below zero (below the horizontal zero line) are consistent with the countercyclical hypothesis: wider spreads associated with weaker forward returns. The dashed vertical line marks the start of the out-of-sample evaluation period. A persistent negative correlation band suggests a durable relationship; a correlation that oscillates around zero suggests regime-dependence."
- observation: "[PLACEHOLDER — Evan to replace with v4 rolling correlation findings from `results/hy_ig_spy_v4_from_scratch/exploratory_*/correlations.csv`]"
- interpretation: "[PLACEHOLDER — Ray to update once v4 findings available. At this stage: if rolling correlations are predominantly negative at 3-6 month forward horizons, this would be consistent with the countercyclical hypothesis documented in Fama & French (1989) and Gilchrist & Zakrajšek (2012). If the correlation is weak or sign-inconsistent across horizons, it suggests the linear specification alone is insufficient to capture the relationship.]"
- key_message: "[PLACEHOLDER — update once v4 data is available. Hypothesis: the HY-IG spread shows a negative correlation with SPY forward returns, most pronounced at 3-6 month horizons, but this must be confirmed against v4 exam outputs before being stated as a finding.]"

### Level 1: GRANGER_BLOCK

- method_name: "Granger Causality (Toda-Yamamoto)"
- method_theory: "**Granger causality** tests whether past values of the HY-IG spread improve forecasts of future SPY returns, above and beyond what SPY's own history already predicts. A positive result means the spread contains incremental predictive information — it 'Granger-causes' SPY. The **Toda-Yamamoto** variant (augmenting the VAR by the suspected integration order) handles the non-stationarity of financial time series robustly, avoiding spurious rejection that can occur when standard Granger tests are applied to integrated (I(1)) series. Both directions are tested: HY-IG → SPY and SPY → HY-IG."
- question: "Does the HY-IG spread carry information about future SPY returns that is not already contained in SPY's own return history — and is the relationship asymmetric, flowing from credit to equity rather than from equity to credit?"
- how_to_read: "The chart shows Toda-Yamamoto test statistics and p-values for the null hypothesis that HY-IG spreads do NOT Granger-cause SPY returns, at lags 1 through 6 months. Bars below the p=0.05 dashed threshold indicate statistically significant predictive content at that lag. Reverse-direction results (SPY → HY-IG) are shown separately. An asymmetric result — significant in the forward direction, not in the reverse — is the pattern consistent with bond markets processing default risk before equity markets."
- observation: "[PLACEHOLDER — Evan to replace with v4 Toda-Yamamoto results from `results/hy_ig_spy_v4_from_scratch/core_models_*/granger_*.csv`]"
- interpretation: "[PLACEHOLDER — Ray to update once v4 findings available. At this stage: if the forward direction (HY-IG → SPY) is significant at lags 1-4 months and the reverse direction is not, this would be consistent with the credit-leads-equity hypothesis. If the reverse direction is also significant, it suggests simultaneous causation that complicates identification.]"
- key_message: "[PLACEHOLDER — update once v4 data is available. Hypothesis: asymmetric Granger structure consistent with one-directional credit-to-equity information flow, but this must be confirmed against v4 exam outputs.]"

### Level 1: CCF_BLOCK

- method_name: "Pre-Whitened Cross-Correlation Function (CCF)"
- method_theory: "The **pre-whitened CCF** removes each series' own autocorrelation structure first — by fitting an ARMA model to each series separately and computing the residuals — then examines cross-correlations of those residuals at lags −12 to +12 months. This 'pre-whitening' step (removing the autocorrelation 'color' from each series) ensures that any observed cross-correlations reflect genuine information transfer between the two variables, not shared persistence (a common source of spurious correlation in financial time series that have persistent trends or cycles)."
- question: "At what lag does the HY-IG spread carry the most information about SPY returns — and does the lead-lag structure, after removing autocorrelation from both series, confirm that credit moves first?"
- how_to_read: "Bars at negative lags (e.g., lag −3) indicate that the HY-IG spread at month T−3 is associated with SPY return at month T: the spread leads by 3 months. Bars at positive lags indicate that SPY returns lead the spread. Bars extending beyond the 95% confidence bands (dashed lines, set at ±1.96/√n) are statistically significant. A cluster of significant negative-lag bars is consistent with the spread-leads-equity hypothesis."
- observation: "[PLACEHOLDER — Evan to replace with v4 pre-whitened CCF results]"
- interpretation: "[PLACEHOLDER — Ray to update once v4 findings available. At this stage: significant negative-lag bars at lags −1 to −4 would be consistent with a 1-4 month credit-leads-equity timing structure, as documented in Gilchrist & Zakrajšek (2012) using related credit spread measures.]"
- key_message: "[PLACEHOLDER — update once v4 data is available. Hypothesis: negative-lag cluster at 1-4 months consistent with the spread-leads-equity pattern, absent of significant positive-lag bars that would indicate reverse causation.]"

### Level 2: HMM_BLOCK

- method_name: "Hidden Markov Model (HMM) Regime Analysis"
- method_theory: "A **Hidden Markov Model** identifies latent (unobserved) market regimes — distinct states of the world that generate statistically different behavior — from the observed spread series alone. We fit a 2-state HMM (a 'calm' state and a 'stress' state) to the HY-IG spread. The model outputs, for each month, a probability that the market is currently in the stress state. This probability serves as the tournament's stress signal. The HMM aggregates level, trend, and volatility information in the spread into a single, calibrated probability number — making it a nonlinear summary of the credit-risk environment."
- question: "Do HMM-identified credit regimes discriminate meaningfully between historical periods of strong and weak SPY performance — does being in the stress state reliably identify the months when holding SPY has historically been costly?"
- how_to_read: "The chart overlays HMM stress probability (shaded area, right axis) on SPY price (line, left axis). Shaded periods above 0.5 probability are HMM-classified stress regimes. Key historical events are annotated. Look for whether the high-stress periods align with the major SPY drawdown episodes. A stress state that covers a minority of calendar months but contains the majority of drawdown losses would be consistent with a useful regime discriminator."
- regime_context: "The HMM stress state is the tournament's candidate signal. Its value is not precise timing prediction — it is identifying the regimes where holding full SPY exposure has historically carried elevated drawdown risk relative to calm-state periods."
- observation: "[PLACEHOLDER — Evan to replace with v4 HMM regime results from `results/hy_ig_spy_v4_from_scratch/core_models_*/hmm_*.csv`]"
- interpretation: "[PLACEHOLDER — Ray to update once v4 findings available. At this stage: if the HMM stress state covers ~25-30% of calendar months but concentrates the majority of SPY drawdown events, this would be consistent with a genuine regime discriminator as hypothesized. The 2022 inflation-shock episode is the critical test: did the HMM classify it as stress, and if so, was the spread signal genuine or a rate-shock artifact?]"
- key_message: "[PLACEHOLDER — update once v4 data is available. Hypothesis: HMM stress periods concentrate SPY drawdown risk, but the rate-shock blind spot in 2022 may mean the stress classification during that episode carries different signal quality than during credit-cycle episodes.]"

### Level 2: REGIME_QUARTILE_BLOCK

- method_name: "Regime Quartile Returns Analysis"
- method_theory: "Rather than relying on a fitted model to define regimes, this analysis divides the observed history of HY-IG spread values into four equal-frequency quartiles: Q1 (tightest 25% of spreads, least credit stress) through Q4 (widest 25%, most credit stress). SPY forward return distributions are then computed within each quartile. This **model-free** approach provides a transparent, assumption-free check on whether the spread level has monotonic predictive content across the full distribution — not just at extremes."
- question: "Is there a monotonic downward gradient from tight spreads to wide spreads in SPY forward returns — and does it hold across the full spread distribution, not just during crisis extremes?"
- how_to_read: "The bar chart shows average annualized SPY forward return (or Sharpe ratio) for each of the four HY-IG spread quartiles. A monotonically declining pattern from Q1 (left, tightest spreads) to Q4 (right, widest spreads) is consistent with the countercyclical hypothesis. If only Q4 shows a decline, the relationship is crisis-driven rather than distributional. If Q1 and Q4 diverge but the middle quartiles are similar, the relationship is concentrated at the extremes."
- regime_context: "The Q4 vs Q1 Sharpe differential — the performance gap between the tightest and widest spread quartiles — is the key diagnostic for regime discrimination strength. A large differential would suggest the spread is doing genuine separatory work across the full distribution."
- observation: "[PLACEHOLDER — Evan to replace with v4 regime quartile results from `results/hy_ig_spy_v4_from_scratch/exploratory_*/regime_quartiles.csv`]"
- interpretation: "[PLACEHOLDER — Ray to update once v4 findings available. At this stage: a clear Q1-to-Q4 monotonic gradient would be consistent with the distributional countercyclical relationship documented implicitly in Fama & French (1989) and explicitly examined in López-Salido et al. (2017) using related credit measures. A non-monotonic pattern would suggest threshold-dependent behavior.]"
- key_message: "[PLACEHOLDER — update once v4 data is available. Hypothesis: SPY forward returns decline from Q1 to Q4 of the HY-IG spread distribution, but the monotonicity and statistical significance must be confirmed from v4 exam outputs.]"

---

## For STRATEGY_CONFIG

### STRATEGY_PLAIN_ENGLISH
"The strategy uses the credit spread signal to scale SPY exposure. When credit stress is elevated, position size is reduced; when conditions are calm, full exposure is restored. This section explains the rule, the historical track record (once v4 exam runs), and the honest limitations every investor should understand."

### STRATEGY_INTRO_PARAGRAPHS
"""
The HY-IG → SPY strategy belongs to the signal-scaling family: rather than switching
all-in or all-out of SPY, the portfolio adjusts SPY exposure proportionally to the
measured level of credit stress. When the HMM stress probability exceeds the signal
threshold (determined by the tournament search), equity exposure is reduced toward a
defensive allocation. When the stress probability falls, exposure is restored toward
full investment.

This design reflects two aspects of the HY-IG signal. First, it provides probabilistic
rather than binary information about credit regime. Second, premature de-risking in a
false-positive regime has a real opportunity cost in a market like SPY that trends
upward over long periods. Scaling preserves upside participation during ambiguous
periods while still providing some protection during high-conviction stress regimes
where the credit signal has historically been most informative.

The strategy's primary hypothesis is drawdown reduction rather than absolute return
enhancement. The HY-IG signal is countercyclical: in theory and in historical patterns
documented in the literature, it suggests reducing exposure during the periods when
SPY buy-and-hold investors accumulate the largest losses. The cost is some return
drag during periods when spreads are elevated but the market advances regardless — a
cost that is unavoidable for any rule-based risk-management approach.

**Important:** At the time this v4 page was built, the formal out-of-sample exam had
not yet been run. All strategy performance numbers shown here are from the v4 exam
once completed. Do not carry over numbers from v1/v2/v3 — they are not v4 findings.
"""

### HONEST_CAVEATS
"""
**Simulated, not executed.** All performance statistics for this pair are
hypothetical — they reflect rules applied to historical data, not actual trades
with real capital. Real execution involves market impact, bid-ask spreads, and
behavioral execution risk that simulated backtests do not capture.

**The 2022 rate-shock blind spot.** The 2022 SPY drawdown was driven primarily by
the Federal Reserve's fastest rate-hiking cycle in 40 years, not by a credit
deterioration cycle. The HY-IG signal may have given only partial warning for that
episode. Investors using this signal in isolation should be aware of this limitation
and consider pairing it with a rate-cycle indicator for the exposure not covered by
the credit channel.

**In-sample HMM fitting.** The HMM stress probability is derived from a model fit on
in-sample data. Live implementation should re-estimate HMM parameters periodically
(annually or after major structural breaks) to avoid regime definitions becoming
stale as the credit environment evolves.

**Search-grade evidence status.** This is a v4 clean rebuild. The evidence status
at publication is search-grade — the formal out-of-sample exam is pending. Do not
interpret any chart or statistic on this portal as a validated investment signal.
Language throughout reflects this status: "is consistent with", "suggests",
"historical pattern" — not "confirmed", "validated", or "durable edge".

**Fed backstop risk.** If the Federal Reserve's corporate bond purchase programs
become a standing policy tool (as COVID suggested they might), future episodes of
HY-IG spread widening may be more quickly reversed by policy intervention, compressing
the leading-indicator window and potentially reducing the signal's practical utility
during acute crises.
"""

---

## For METHODOLOGY_CONFIG

### METHODOLOGY_PLAIN_ENGLISH
"This section covers the technical decisions: data sources, sample period, signal construction, model specifications, and known limitations. Readers who want to replicate or challenge the analysis will find the inputs and design choices documented here."

### METHODOLOGY_FRAMING
"""
The HY-IG → SPY v4 analysis is a clean rebuild from first principles. No results
from v1, v2, or v3 are carried into this version. The pipeline follows the team's
standard stages: data ingestion and stationarity checks (Dana), signal construction
and in-sample econometric estimation (Evan), out-of-sample tournament evaluation
(Evan), visualization (Vera), and narrative assembly (Ray / Ace). Each stage produces
auditable artifacts in `results/hy_ig_spy_v4_from_scratch/`.

The central methodological challenge in this analysis is the GFC dominance problem.
The 2008-2009 financial crisis produced HY-IG spread levels (approximately 2,000 bps
at peak) roughly 4-5 times the level seen in most other episodes. Full-sample
regressions have high leverage on the GFC observations, which can make the
relationship appear stronger or more robust than it would appear in a sample that
excludes that single exceptional episode. The analytical response is transparency:
where GFC influence is material, both full-sample and GFC-excluded estimates are
reported and the difference is explicitly noted.

The second challenge is the non-stationarity question. HY-IG spread levels may
exhibit near-I(1) behavior over some subsamples — particularly during and after the
GFC when spread levels took years to normalize. Standard OLS on I(1) variables
produces spurious regressions. The pipeline handles this by running ADF and KPSS
tests on the spread level and first difference; if the level is non-stationary, the
specification switches to first differences, which changes the economic interpretation
from "level of stress" to "acceleration of stress" and is noted in the results.
"""

### DATA_SOURCES_TEXT
"""
**HY Spread (BAMLH0A0HYM2):** ICE BofA US High Yield Index Option-Adjusted Spread.
Sourced from FRED (Federal Reserve Economic Data, St. Louis Fed). Monthly frequency;
daily available. Series begins January 1997. Measures the average option-adjusted
yield spread of the high-yield (BB and below) US corporate bond universe relative
to comparable-maturity Treasuries.

**IG Spread (BAMLC0A0CM):** ICE BofA US Investment Grade Corporate Index
Option-Adjusted Spread. Sourced from FRED. Monthly frequency; daily available.
Series begins January 1997. Measures the average option-adjusted yield spread of the
investment-grade (BBB and above) US corporate bond universe.

**HY-IG Spread (Derived):** Constructed as BAMLH0A0HYM2 minus BAMLC0A0CM, in
basis points. This difference isolates the pure credit-cycle risk premium: the
incremental yield demanded by lenders to high-yield issuers relative to
investment-grade issuers, with duration effects controlled by the option-adjustment
on both sides.

**SPY (Target):** SPDR S&P 500 ETF Trust total return series (dividend-adjusted
close). Daily prices from Yahoo Finance (ticker: SPY). Monthly log returns computed
from daily adjusted close prices at month-end. SPY launched January 1993; full
data available from 1993 onward, though the analysis begins at HY spread inception
(January 1997).

**NBER Recession Dates:** Binary indicator (USREC from FRED) used for chart
annotations and subsample analysis. Not used as a regressor.

**VIX (Robustness check):** CBOE Volatility Index (VIXCLS from FRED). Used as a
control variable in robustness regressions to test whether the HY-IG spread retains
predictive content for SPY after controlling for the equity implied-volatility signal.

**10-Year Treasury Yield (Robustness check):** US 10-Year Constant Maturity Treasury
yield (GS10 from FRED). Used as a control in robustness regressions to isolate the
credit-spread channel from the rate-cycle channel, given the 2022 rate-shock
confounding risk identified in the literature review.
"""
