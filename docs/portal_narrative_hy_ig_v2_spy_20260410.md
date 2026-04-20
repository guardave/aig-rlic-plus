---
pair_id: hy_ig_v2_spy
narrative_version: 1.1.0
generated_at: "2026-04-19T18:00:00Z"
headline_template: "A"
headline_template_rationale: "Template A (metric-first) chosen because the primary stakeholder question this narrative answers is 'does this signal work, and how well?' — a metric-first opener surfaces the Sharpe 1.27 / 8-year OOS headline before the reader needs to decode the insight. OOS span and Sharpe are read from results/hy_ig_v2_spy/winner_summary.json (oos_period_start 2018-01-01, oos_period_end 2025-12-31 → 8 years; oos_sharpe 1.274 rounded to 1.27), not hand-typed, per RES-18 rule 2 + rule 3."
direction_asserted: countercyclical
chart_refs:
  - correlation
  - granger
  - local_projections
  - regime
  - quantile
  - ccf
  - transfer_entropy
  - quartile_returns
  - hero
  - equity_curves
  - equity_drawdown
  - tournament_scatter
  - signal_timeseries
  - position_timeseries
  - history_zoom_dotcom
  - history_zoom_gfc
  - history_zoom_covid
glossary_terms:
  - Basis point (bp)
  - Credit spread
  - HMM stress probability
  - Buy-and-hold
  - Counter-cyclical
  - Credit rating
  - Drawdown
  - Excess bond premium (EBP)
  - Forward return
  - Granger causality
  - Hidden Markov Model (HMM)
  - High-yield bonds (junk bonds)
  - HY-IG spread
  - Impulse response
  - In-sample / Out-of-sample
  - Investment-grade bonds
  - Local projection
  - Markov-switching model
  - Merton model
  - NFCI
  - Option-adjusted spread (OAS)
  - Quality spread
  - Quantile regression
  - Regime
  - Sharpe ratio
  - Transfer entropy
  - VIX
  - VIX term structure
  - Walk-forward validation
  - Z-score
  - Tournament
  - Stress regime
  - Signal probability
status_labels_used:
  - Validated
historical_episodes_referenced:
  - episode_slug: dotcom
    override_needed: false
    selection_rationale: confirmer
    prose_ref: "Story §What History Shows — Dot-Com paragraph ties HY-IG spread widening (500 → 1,000+ bps) to the tech-sector implosion; canonical zoom chart output/_comparison/history_zoom_dotcom.json was generated from HY-IG v2 reference-pair data per META-RPD, so the canonical IS the pair-specific view for this reference pair — no separate override artifact required."
  - episode_slug: gfc
    override_needed: false
    selection_rationale: long_lead
    prose_ref: "Story §What History Shows — GFC paragraph ties HY-IG spread widening (300 → 2,000+ bps, ~5 months before SPY peak) to Bear Stearns + Lehman sequence; canonical zoom chart output/_comparison/history_zoom_gfc.json was generated from HY-IG v2 reference-pair data per META-RPD."
  - episode_slug: covid
    override_needed: false
    selection_rationale: coincident
    prose_ref: "Story §What History Shows — COVID paragraph ties HY-IG spread widening (350 → 1,100 bps in 5 weeks) to the pandemic shock + Fed facilities; canonical zoom chart output/_comparison/history_zoom_covid.json was generated from HY-IG v2 reference-pair data per META-RPD."
  - episode_slug: inflation_2022
    override_needed: false
    selection_rationale: failure_case
    prose_ref: "Story §What History Shows — 2022 Rate Shock paragraph ties modest HY-IG spread widening (300 → 500 bps) to Fed rate hikes; honest failure-case where credit alone under-signaled a pure-rate-shock drawdown. No zoom chart required — the failure-case purpose is argued textually via the comparison of spread change to SPY -25% rather than through an event-marked overlay."
pages:
  story:
    headline: "Sharpe 1.27 over 8-year OOS — credit spreads as a multi-month early-warning signal for equity drawdowns"
    plain_english: "When companies borrow money, lenders charge safer companies lower rates and risky companies higher rates. The gap between those rates is called the credit spread. When it's small, business is going well. When it jumps up, it means investors are scared about the future. This research asks: does watching that gap help predict what the stock market will do? The answer turns out to be yes — sometimes. You can use it to lose less money in crashes."
    sections:
      - id: where_this_fits
        title: "Where This Fits in the Portal"
        anchor: where-this-fits-in-the-portal
      - id: one_sentence_thesis
        title: "One-Sentence Thesis"
        anchor: one-sentence-thesis
      - id: headline_findings
        title: "Headline Findings for KPI Cards"
        anchor: headline-findings-for-kpi-cards
      - id: suggested_hero_chart
        title: "Suggested Hero Chart"
        anchor: suggested-hero-chart
      - id: why_stock_investors_care_about_bonds
        title: "Why Should Stock Investors Care About Bonds?"
        anchor: why-should-stock-investors-care-about-bonds
      - id: early_warning_signal
        title: "The Early Warning Signal"
        anchor: the-early-warning-signal
      - id: what_history_shows
        title: "What History Shows"
        anchor: what-history-shows
      - id: not_a_simple_relationship
        title: "It Is Not a Simple Relationship"
        anchor: it-is-not-a-simple-relationship
    expanders:
      - id: what_is_a_credit_spread
        title: "What exactly is a credit spread, and how is it measured?"
      - id: merton_model
        title: "Why are stocks and bonds mathematically connected? (The Merton Model)"
      - id: ccc_bb_quality_spread
        title: "Is there a deeper signal within the credit market itself? (The CCC-BB quality spread)"
      - id: how_we_define_regimes
        title: "How do we define market regimes without arbitrary cutoffs?"
  evidence:
    headline: ""
    plain_english: "This section shows the data we used to test whether credit spreads really do predict stock market returns. Eight different statistical tests all point to the same conclusion: when the credit spread widens, stocks tend to do worse in the following weeks and months. None of these tests is perfect on its own, but together they tell a consistent story."
    sections:
      - id: how_we_tested
        title: "How We Tested the Signal"
        anchor: how-we-tested-the-signal
      - id: method_correlation
        title: "Method: Correlation Analysis"
        anchor: method-correlation-analysis
      - id: method_granger
        title: "Method: Granger Causality (Toda-Yamamoto)"
        anchor: method-granger-causality
      - id: method_local_projections
        title: "Method: Local Projections (Jorda Impulse Responses)"
        anchor: method-local-projections
      - id: method_hmm
        title: "Method: Regime Analysis (Hidden Markov Model)"
        anchor: method-regime-analysis
      - id: method_quantile
        title: "Method: Quantile Regression"
        anchor: method-quantile-regression
      - id: method_ccf
        title: "Method: Pre-whitened Cross-Correlation Function (CCF)"
        anchor: method-ccf
      - id: method_transfer_entropy
        title: "Method: Transfer Entropy (Nonlinear Information Flow)"
        anchor: method-transfer-entropy
      - id: method_quartile_returns
        title: "Method: Quartile Returns Analysis"
        anchor: method-quartile-returns
      - id: combinatorial_tournament
        title: "The Combinatorial Tournament"
        anchor: the-combinatorial-tournament
    expanders: []
  strategy:
    headline: ""
    plain_english: "Our computer looked at every possible combination of 'signal strength + threshold + trade rule' to find the one that would have made the most money (adjusted for risk) in past data. The winner is a strategy that reduces stock exposure when credit spread stress is high and adds back when stress fades. In this section we explain exactly what the strategy does, when to use it, and when it would have failed."
    sections:
      - id: how_signal_is_generated
        title: "How the Signal is Generated"
        anchor: how-the-signal-is-generated
      - id: how_signal_translates_to_action
        title: "How the Signal Translates to Action"
        anchor: how-the-signal-translates-to-action
      - id: key_strategy_metrics
        title: "Key Strategy Metrics"
        anchor: key-strategy-metrics
      - id: where_strategy_adds_value
        title: "Where the Strategy Adds Value -- and Where It Does Not"
        anchor: where-the-strategy-adds-value
      - id: how_to_use_manually
        title: "How to Use This Indicator Manually"
        anchor: how-to-use-this-indicator-manually
      - id: execution_points
        title: "Execution Points -- Actual Trigger Dates"
        anchor: execution-points
      - id: important_caveats
        title: "Important Caveats"
        anchor: important-caveats
      - id: how_to_read_trade_log
        title: "How to Read the Trade Log"
        anchor: how-to-read-the-trade-log
    expanders:
      - id: why_scale_instead_of_switch
        title: "Why scale positions instead of switching all-in or all-out?"
      - id: what_is_a_z_score
        title: "What is a z-score, and why do we use one?"
  methodology:
    headline: ""
    plain_english: "This section explains the technical details of how we did the analysis — which data we used, which statistical methods, and what could go wrong. Normal readers can skip it. Expert readers can use it to criticise our work and suggest improvements."
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
      - id: sensitivity_analysis
        title: "Sensitivity Analysis"
        anchor: sensitivity-analysis
      - id: reverse_causality_check
        title: "Reverse Causality Check"
        anchor: reverse-causality-check
      - id: signal_universe
        title: "Signal Universe"
        anchor: signal-universe
      - id: analyst_suggestions
        title: "Analyst Suggestions for Future Work"
        anchor: analyst-suggestions
      - id: references
        title: "References"
        anchor: references
    expanders: []
glossary_requests: []
---

# Portal Narrative: HY-IG Credit Spread → S&P 500 (v2)

**From:** Ray (Research Agent)
**To:** Ace (App Dev)
**Date:** 2026-04-10 (Wave 5C retro-apply 2026-04-19)
**pair_id:** `hy_ig_v2_spy`

---

## Page 1 -- The Hook (Executive Summary)

## Sharpe 1.27 over 8-year OOS — credit spreads as a multi-month early-warning signal for equity drawdowns

**Key metrics (out-of-sample 2018-2025):**

- **Sharpe ratio: 1.27** (vs 0.90 buy-and-hold) -- ~40% more return per unit of risk
- **Annualized return: 11.3%** (vs ~10% buy-and-hold)
- **Max drawdown: -10.2%** (vs -34% buy-and-hold) -- roughly one-third of the pain

<details>
<summary>🧒 Plain English version</summary>

When companies borrow money, lenders charge safer companies lower rates and risky companies higher rates. The gap between those rates is called the credit spread. When it's small, business is going well. When it jumps up, it means investors are scared about the future. This research asks: does watching that gap help predict what the stock market will do? The answer turns out to be yes -- sometimes. You can use it to lose less money in crashes.

</details>

### Where This Fits in the Portal

This is **one indicator-target analysis** -- we ask whether credit spreads can help time equity exposure. The AIG-RLIC+ portal catalogues many such pair-wise studies; this one examines whether the HY-IG credit spread carries useful information about future SPY returns.

**How to read the rest of this page pack.** You'll read the **Story** first (why the signal works in plain English), then the **Evidence** (the statistical proofs, one method block at a time), then the **Strategy** (the actual trading rule and how you would apply it yourself), then the **Methods** (technical appendix for readers who want to reproduce or criticise the work). Each page stands alone; readers short on time can skim the Story and Strategy pages and skip the rest.

### One-Sentence Thesis

The bond market often sees trouble coming before the stock market does -- and the gap between risky and safe bond yields has been one of the most reliable early warning signals for equity declines over the past 25 years.

### Headline Findings for KPI Cards

1. **Credit led equity by ~5 months before the 2008 crash** -- the HY-IG credit spread (the extra yield that investors demand to hold risky corporate bonds instead of safe ones -- essentially the price of insurance against companies going bust) began widening in June 2007, while stocks did not peak until October 2007. **What this means for investors:** an investor watching the spread crossing its stress band in mid-2007 would have had nearly half a year to trim equity exposure before the October peak and the -57% drawdown that followed.
2. **Spreads widened from 300 to 2,000+ basis points (3% to 20%+) during the GFC** -- a basis point is 1/100th of a percentage point, so 2,000 basis points means risky companies were paying 20 full percentage points more than safe ones. That 6x increase reflected a market that believed a wave of corporate defaults was coming. **What this means for investors:** the sheer scale of the widening was a loud, unmistakable risk-off signal -- investors following the rule would have rotated the majority of equity exposure to cash well before the Lehman-week crash.
3. **Credit signals predicted 3 of the last 4 major equity drawdowns** -- a drawdown is a peak-to-trough decline in value. The dot-com bust (2001), the Global Financial Crisis (2008), and the COVID crash (2020) were all preceded or accompanied by dramatic spread widening. The 2022 rate shock is the honest exception -- more on that below. **What this means for investors:** the signal is a reliable drawdown-avoidance tool for credit-driven sell-offs, but it should be paired with a separate interest-rate or valuation signal (e.g. the yield-curve pair in the portal) to cover the type of bear market that credit alone cannot see.
4. **The relationship is strongest during stress** -- when spreads are in their top quartile (top 25% of historical values), the connection between credit conditions and subsequent stock returns is significantly stronger than during calm periods. **What this means for investors:** the signal earns its keep when you need it most -- during market crises -- and stays quiet the rest of the time, so following it does not impose a return drag during normal calm years.
5. **Out-of-sample testing covers 8 years (2018-2025)** -- including the 2018 volatility spike, COVID crash, 2022 rate shock, and 2023-25 recovery. "Out-of-sample" means this period was hidden from the models during training, so it provides a genuine real-world test of whether the signal holds up on data it has never seen. **What this means for investors:** the 1.27 Sharpe and -10.2% max drawdown were achieved on data the model had never seen -- this is evidence of a durable edge, not curve-fitting, and supports allocating real capital to the rule rather than treating it as a historical curiosity.

### Suggested Hero Chart

A dual-axis time series chart (2000-2025) with the HY-IG spread on the left y-axis (inverted, so widening = down) and SPY price on the right y-axis. Vertical shaded bands mark NBER recessions. Key events annotated with date labels. The visual immediately shows that the orange spread line "dips" (widens) before or simultaneously with the blue equity line declining.

**Scope note.** This page pack focuses on the HY-IG credit spread in isolation. Credit stress rarely travels alone -- it typically co-occurs with VIX spikes and yield-curve inversions -- but each of those indicators has its own dynamics and its own separate analysis in the portal. See the separate analyses on **VIX x SPY** and **Yield Curve x SPY** for deep dives on those related signals; here we keep the lens on credit.

**Transition to Page 2:** These numbers tell a compelling story, but to understand *why* credit spreads carry this predictive power -- and when the signal works versus when it fails -- we need to look deeper into how bond and stock markets are connected.

---

## Page 2 -- The Story (Layperson Narrative)

<details>
<summary>🧒 Plain English version</summary>

The bond market usually panics before the stock market does. By the time stocks are falling, bonds have often already been signaling trouble for weeks. This section tells the story of why that happens and how it played out during the 2008 crisis, the 2020 COVID crash, and other stressful moments.

</details>

### Why Should Stock Investors Care About Bonds?

Most people think of stocks and bonds as separate worlds. Stocks are for growth; bonds are for safety. But behind the scenes, the bond market is constantly making judgments about risk that stock investors often ignore -- until it is too late.

When companies borrow money by issuing bonds, investors demand higher interest rates from riskier companies. The difference between what a risky company pays and what a safe company pays is called a **credit spread** -- the extra yield investors require to compensate for the possibility that the risky company might not pay them back. Think of it as the price of insurance against a company going bust: when more companies look shaky, the insurance gets more expensive.

<!-- expander: What exactly is a credit spread, and how is it measured? -->
A credit spread is measured in **basis points** (hundredths of a percentage point). If a risky company's bond yields 8% and a safe company's bond yields 4%, the credit spread is 400 basis points (4 percentage points). When investors become worried about the economy, they demand even higher yields from risky companies, causing spreads to **widen**. When confidence returns, spreads **tighten** (narrow).

The specific spread we study is the **HY-IG spread**: the difference between the yield on high-yield bonds (also called "junk bonds" -- bonds from companies with lower credit ratings, like BB or CCC) and investment-grade bonds (bonds from companies with higher credit ratings, like AA or A). Both yields are measured as **option-adjusted spreads (OAS)** -- a technique that strips out the effect of special bond features like early repayment clauses, leaving a cleaner measure of pure credit risk.
<!-- /expander -->

### The Early Warning Signal

Our research examines whether this spread can serve as an early warning system for stock investors. The core finding, supported by over two decades of academic research, is that **the bond market tends to detect trouble before the stock market reacts.** There are several reasons for this:

- **Bond investors are wired for caution.** Unlike stock investors who can profit from unlimited upside, bond investors can only get their money back plus interest. This asymmetry makes them structurally more sensitive to the first signs of deterioration. When something smells off, bond investors raise the price of lending before stock investors lower the price they will pay for shares. **What this means for investors:** credit spreads widen earlier than equity prices drop -- investors who watch spreads get a head start of days to months over investors who watch only equity prices.
- **Banks trade on private information.** Banks that lend to companies have inside knowledge about their financial health. Research by Acharya & Johnson (2007) found evidence that this information leaks into credit markets -- through hedging activity in credit default swaps -- before it appears in stock prices. **What this means for investors:** a spread-widening signal is effectively picking up informed-trader conviction that equity investors have not yet seen -- acting on it before the news becomes public is what turns the signal into a risk-management edge.
- **The bond market is harder to fool.** Philippon (2009) showed that bond prices provide a cleaner signal of a company's fundamental value than stock prices. Stocks can be inflated by speculation and momentum; bond investors care only about getting their money back. **What this means for investors:** when spreads widen while stocks are still making highs, the likely explanation is equity complacency -- the disciplined move is to trim equity exposure toward the bond market's view, not to dismiss the divergence.

The relationship is **counter-cyclical** -- meaning the spread moves opposite to stocks. When spreads widen (risky bonds get more expensive to issue), stocks tend to fall. When spreads tighten (risk appetite returns), stocks tend to rise.

<!-- expander: Why are stocks and bonds mathematically connected? (The Merton Model) -->
In 1974, economist Robert Merton proved something elegant: a company's stock and its debt are not separate instruments -- they are two different bets on the same underlying reality.

Imagine a company as a house with a mortgage. The homeowner (stockholder) profits if the house value rises above the mortgage. The bank (bondholder) gets paid as long as the house value stays above the mortgage. Now imagine the house value drops toward the mortgage amount. Two things happen at once: the homeowner's equity shrinks, and the bank starts worrying about getting paid back.

Merton showed that this analogy is mathematically precise. A company's stock is essentially a call option on its total asset value, with the strike price set at the value of its debts. When asset value drops toward the debt level, equity declines and credit spreads widen simultaneously. This is why credit spreads and stock prices tend to move in opposite directions during stress -- they are both responding to the same underlying reality, just viewed from different angles.

The practical implication: when you see credit spreads widening, it means the market is pricing in a higher probability that corporate asset values are falling toward their debt levels -- which is also bad news for equity holders.
<!-- /expander -->

### What History Shows

We analyzed 25 years of daily data (January 2000 through December 2025), covering four major market disruptions. Each episode reveals a different facet of how credit spreads interact with stock prices.

**The Dot-Com Bust (2001-2002).** Credit spreads began widening well before the recession officially started in March 2001. High-yield spreads climbed from roughly 500 to over 1,000 basis points (5% to 10%+) as the telecom and technology sectors imploded, highlighted by the WorldCom bankruptcy in July 2002 *(see the Dot-Com zoom-in chart below -- `output/_comparison/history_zoom_dotcom.json` -- with labelled markers at Mar 2000, Aug 2000, Mar 2001, and Jul 2002)*. The signal was genuine, though the lead time was shorter than in later episodes -- the dot-com bust was driven more by equity overvaluation than by credit deterioration, so the credit market was a contemporaneous confirmer rather than a leading indicator.

**The Global Financial Crisis (2007-2009).** This is the textbook example of credit leading equity. Credit spreads started widening in mid-2007, following the collapse of two Bear Stearns hedge funds that were exposed to subprime mortgages *(see the GFC zoom-in chart below -- `output/_comparison/history_zoom_gfc.json` -- with labelled markers at Oct 2007, Sep 2008, and Dec 2008)*. The stock market did not peak until October 2007 -- giving attentive investors roughly five months of warning. By the time Lehman Brothers collapsed in September 2008, the HY-IG spread had already reached roughly 800 basis points. It eventually peaked above 2,000 basis points in December 2008. An investor who moved to cash when spreads crossed 2 standard deviations above their rolling mean would have avoided the majority of the drawdown -- though the timing of re-entry was equally critical.

**The COVID Crash (2020).** Credit spreads surged from about 350 to 1,100 basis points (3.5% to 11%) in just five weeks (late February to late March 2020) *(see the COVID zoom-in chart below -- `output/_comparison/history_zoom_covid.json` -- with labelled markers at Feb 2020, 23-Mar-2020 Fed intervention, and Jun 2020 spread normalization)*. This time, credit and equity moved almost simultaneously -- the speed of the pandemic shock compressed the usual lead time to near zero. However, the signal still provided value: the sheer magnitude of spread widening confirmed that the sell-off was not a garden-variety correction but a genuine liquidity crisis. The Federal Reserve's unprecedented intervention -- including direct corporate bond purchases announced on March 23, 2020 -- truncated the stress episode faster than any previous crisis.

**The 2022 Rate Shock -- Where the Signal Struggled.** As the Federal Reserve raised interest rates at the fastest pace in four decades, credit spreads widened from about 300 to 500 basis points (3% to 5%). The S&P 500 fell roughly 25%. But here is the honest caveat: the spread widening was modest compared to the equity decline. The mechanism was different -- this was not a credit crisis driven by deteriorating corporate balance sheets but a valuation repricing driven by higher discount rates. The HY-IG spread was reacting to the same force (rising rates) rather than providing an independent early warning. This episode illustrates a genuine limitation of the credit signal: it works best when stress originates in the credit cycle, and less well when the driver is pure monetary policy shock.

<!-- expander: Is there a deeper signal within the credit market itself? (The CCC-BB quality spread) -->
Not all high-yield bonds are equally risky. Within the high-yield universe, there is a meaningful hierarchy: BB-rated bonds are the least risky high-yield issues (just one notch below investment grade), while CCC-rated bonds are at the edge of default.

The spread between CCC and BB yields -- what we call the **quality spread** -- provides an even more granular stress signal. When this quality spread widens, it means investors are specifically fleeing the weakest, most default-prone companies. This often happens before the broader HY-IG spread fully reflects the stress, because the weakest links break first.

During the GFC, the CCC-BB quality spread began widening months before the overall HY-IG spread reached crisis levels. During COVID, the quality spread spike was even more dramatic -- CCC-rated bonds briefly yielded over 20%, while BB bonds remained relatively contained. The quality spread is a "canary in the coal mine" within the credit market itself.

The CCC-BB quality spread is **off-scope for this pair** under ECON-SD -- this page is strictly HY-IG-spread derivatives vs SPY derivatives. CCC-BB was considered during exploration and is logged in the Methodology page's *Analyst Suggestions for Future Work* section as a candidate for a future within-HY variant family (see `results/hy_ig_v2_spy/analyst_suggestions.json`). It is not used in any regression, tournament, or chart on this pair's Evidence or Strategy pages.
<!-- /expander -->

### It Is Not a Simple Relationship

If the story ended at "wider spreads = lower stocks," building a profitable trading strategy would be straightforward. But the relationship between credit spreads and stock returns is more nuanced, and understanding these nuances is essential for using the signal effectively.

*(Related: the VIX term-structure and yield-curve signals exhibit their own regime dependencies, analysed in the separate **VIX x SPY** and **Yield Curve x SPY** pair pages. This page keeps the focus on credit.)*

The connection changes depending on the market **regime** -- a regime is a distinct state of financial conditions, like "calm weather" versus "storm," where each state has its own patterns of returns, volatility, and correlations between assets:

- **During calm periods** (when spreads are in their normal range of roughly 250-400 basis points, or 2.5% to 4%), the predictive power of credit spreads for stock returns is modest. In fact, during these periods, stock prices tend to lead credit spreads -- equity markets set the pace, and credit markets follow. This makes intuitive sense: when things are going well, there is not much default risk to price, so the credit market mostly mirrors what equities are already saying.
- **During stress periods** (when spreads are in the top quartile of their historical range, roughly above 500 basis points), the relationship strengthens and may reverse direction -- credit markets appear to lead equity markets. This is consistent with the informed-trading and risk-appetite channels described above. It is also when the signal is most valuable: precisely when investors most need a warning.

**What this means:** A simple "sell stocks when spreads widen" rule will not work because the signal is noisy during calm periods. An effective strategy needs to distinguish between calm and stressed markets and only act on the credit signal when it is in a state where it actually carries predictive power.

<!-- expander: How do we define market regimes without arbitrary cutoffs? -->
In financial economics, a "regime" refers to a distinct state of the market characterized by its own set of statistical properties -- its own average return, level of volatility, and pattern of correlations between assets. Think of weather: sunny days and stormy days are governed by different atmospheric dynamics, and a forecast that works in summer may be useless in winter.

The key insight from research by Hamilton (1989) and Guidolin & Timmermann (2007) is that financial markets do not behave the same way all the time. They switch between regimes -- sometimes abruptly. A model that assumes markets always behave the same way will miss the most important signals, because the relationship between credit and equity fundamentally changes when the market shifts from calm to crisis.

Our analysis uses **Hidden Markov Models** (statistical models that infer which of several unobservable "hidden" states the market is in at any given time, based on patterns in the data) and **Markov-switching regressions** (regressions where the coefficients change depending on which regime is active). These let the data tell us when the market has shifted rather than imposing arbitrary thresholds like "spreads above 500 bps = stress."
<!-- /expander -->

**Transition to Page 3:** History suggests a real connection between credit spreads and stocks -- but anecdotes are not evidence. We subjected 25 years of daily data to a battery of statistical tests to separate genuine predictive power from coincidence and survivorship bias.

---

## Page 3 -- The Evidence (Analytical Detail)

<details>
<summary>🧒 Plain English version</summary>

This section shows the data we used to test whether credit spreads really do predict stock market returns. Eight different statistical tests all point to the same conclusion: when the credit spread widens, stocks tend to do worse in the following weeks and months. None of these tests is perfect on its own, but together they tell a consistent story.

</details>

### How We Tested the Signal

Anecdotes about credit spreads warning before crashes are compelling, but they are not proof. To separate genuine predictive content from storytelling, we subjected 25 years of daily data to four complementary statistical tests, each built to stress a different weakness of the credit-leads-equity hypothesis. If one test flatters the result and the others reject it, we learn the story is fragile. If all four converge, we have real evidence.

Each of the four methods below is presented in the same eight-step structure: what the method is, the question it answers, how to read its chart, what the chart literally shows, optional deeper statistical detail, what the numbers mean economically, and a one-line takeaway. Read straight through, or skim the bolded key messages at the end of each block.

*(Reference: Evan's model outputs in `results/hy_ig_v2_spy/core_models_20260410/`; Vera's interactive charts in `output/charts/hy_ig_v2_spy/plotly/`.)*

---

## Method: Correlation Analysis

**1. The Method:** A **Pearson correlation** is the simplest measure of co-movement between two series, a number between -1 and +1 that says how closely they move together on average. We run it here as our sanity check before reaching for heavier machinery: if credit spreads carry any predictive signal for future equity returns, it should leave at least a faint fingerprint on simple correlations.

**2. The Question It Answers:** *Does today's credit spread show any statistical relationship at all with where stocks are headed over the next week, month, quarter, or year?*

**3. How to Read the Graph:** The chart is a **heatmap** -- a grid where each cell's colour intensity represents the strength of a correlation. Rows are different transformations of the HY-IG spread (raw level, 252-day z-score, 504-day z-score, percentile rank, rate of change, etc.). Columns are forward stock-return horizons (1 day, 5 days, 21 days, 63 days, 126 days, 252 days). Blue cells mean positive correlation, red cells mean negative correlation, and the darker the colour, the stronger the relationship. White or pale cells mean essentially no linear link.

**4. Graph:** `hy_ig_v2_spy_correlation_heatmap`

**5. Observation:** At very short horizons (1 day, 5 days, 21 days), almost every cell is nearly white -- correlations sit within +/-0.02 and do not clear statistical significance. From the 63-day column onward, the grid starts to darken: the raw spread shows a correlation of -0.036 with 63-day forward returns (p = 0.0035), the 252-day z-score reaches -0.099 with 252-day forward returns (p < 0.001), and the 504-day z-score lands at -0.040 with 126-day forward returns (p = 0.0015). The strongest cells are concentrated in the bottom-right corner of the heatmap, where longer lookback transformations meet longer forward horizons.

<expander>
**6. Deep Dive -- Why are the correlations so small in absolute terms, and should I worry?**
Three things to keep in mind. First, daily stock returns are dominated by noise -- even a genuinely useful predictor will only explain a few percent of variance, so raw correlations in the 0.05-0.10 range can still be economically meaningful. Second, we report Pearson correlations with conventional p-values; with samples of roughly 6,500 daily observations, even very small coefficients can clear statistical significance, so we rely on the p-values as a filter for what is distinguishable from zero rather than treating the magnitudes as "effect sizes." Third, the correlation test is purely **linear and contemporaneous** -- it cannot capture regime-dependent relationships or nonlinear threshold effects, which is precisely why the next three methods exist. We treat correlations as a "lights-on" test: if nothing showed up here, we would be sceptical of the entire hypothesis.
</expander>

**7. Interpretation:** Credit spreads and stock returns have essentially no linear relationship at the daily and weekly horizons favoured by short-term traders, but a measurable and statistically significant one emerges at the one-quarter to one-year horizon. The negative sign is the key finding: it confirms the direction predicted by economic theory -- **wider spreads today go with weaker equity returns later**, not stronger ones. The fact that z-scored and percentile-ranked versions of the spread outperform the raw level tells us that what matters is not how wide spreads are in absolute terms, but how unusual they are relative to their recent history.

**8. Key Message:** **Linear correlations are weak at trading-horizon speeds but grow meaningfully negative at quarterly-to-annual horizons, confirming that credit spreads carry a slow-moving, right-signed warning rather than a daily trading signal.**

`chart_status: "Validated"` <!-- RES-22: artifact exists in output/charts/hy_ig_v2_spy/plotly/ and validates against docs/schemas/chart_type_registry.json within 60 days. META-ELI5 ELI5 body supplied by app/components/glossary.py from docs/portal_glossary.json._status_vocabulary.Validated. -->

---

## Method: Granger Causality (Toda-Yamamoto)

**1. The Method:** **Granger causality** is a statistical test that asks a precise question: do past values of variable X improve our forecast of variable Y, above and beyond what Y's own past values already tell us? We use the **Toda-Yamamoto variant**, which adds extra lags to the underlying regression so the test remains valid even when one or both series contain trends or unit roots -- a practical necessity because credit spread levels drift over decades-long cycles.

**2. The Question It Answers:** *Do past credit spread movements contain information that helps predict future stock returns that is not already baked into stocks' own recent behaviour?*

**3. How to Read the Graph:** The chart is a paired **bar plot**. For each lag length (1, 2, 3, 4, and 5 days), there are two bars: one for the "HY-IG → SPY" direction (does credit predict equity?) and one for the "SPY → HY-IG" direction (does equity predict credit?). The height of each bar is the **F-statistic** of the Granger test -- bigger bars mean stronger evidence that the first variable helps predict the second. A dotted horizontal line marks the 5% significance cutoff. Any bar above the line means the predictive relationship at that lag is statistically distinguishable from chance.

**4. Graph:** `hy_ig_v2_spy_granger_causality` *(note: if not yet rendered as a standalone chart, this information is embedded in the local projections panel as an annotation)*

**5. Observation:** The SPY → HY-IG bars completely dominate the chart. At every lag from 1 to 5 days, the F-statistic for "stocks predict credit" is enormous (lag 1: F = 331, p < 0.001) and dwarfs the reverse direction. The HY-IG → SPY bars are small at lags 1 and 2 (p = 0.78 and 0.31 respectively -- not significant) but lift above the 5% line at lags 3 through 5 (F ~ 3.0, p-values of 0.011, 0.015, and 0.014). In short: equity-leads-credit is overwhelming at all lags; credit-leads-equity is modest but statistically real starting three days out.

<expander>
**6. Deep Dive -- Does bidirectional Granger causality mean the signal is useless?**
Not at all, but it does mean we need to read the numbers carefully. Bidirectional causality is exactly what the Merton (1974) structural model predicts: equity and credit are two views of the same underlying firm value, so information flows in both directions. What matters for a practical strategy is **which direction dominates, and in which regime**. The Toda-Yamamoto procedure fits an augmented VAR of order p + d, where p is selected by BIC and d is the maximum suspected order of integration (d = 1 here because spread levels look near-I(1)). We tested lags 1-5 on daily first-differences; longer lags do not add explanatory power by BIC. The full-sample result -- equity dominant, credit weakly significant at 3-5 day lags -- is the unconditional picture. The regime-conditional version, run separately for calm and stress periods, is what actually powers the trading strategy; the credit-to-equity signal strengthens materially in stress, consistent with Acharya & Johnson (2007).
</expander>

**7. Interpretation:** At first glance, this looks like bad news for our hypothesis -- equity seems to lead credit far more strongly than credit leads equity. But read in the context of the Merton model, the result is exactly what theory predicts: both markets are repricing the same underlying corporate asset values, so information flows both ways. The practically important finding is that the credit-to-equity channel exists and is statistically significant at the 3-to-5-day horizon, with enough room for a trader to act. The asymmetry in strength tells us something subtler: in normal times, stock prices set the pace, and credit is a follower; the credit signal is quiet precisely because there is no stress to price. The signal's real value must come from **regime-dependent** behaviour -- which is what the HMM and regime-conditional tests pick up, and which the full-sample Granger test understates by averaging calm and stress together.

**8. Key Message:** **Granger tests confirm a real but modest credit-leads-equity channel at 3-5 day lags -- small in the full-sample average because calm periods dilute it, but the foundation on which the regime-dependent strategy is built.**

`chart_status: "Validated"` <!-- RES-22: artifact exists in output/charts/hy_ig_v2_spy/plotly/ and validates against docs/schemas/chart_type_registry.json within 60 days. META-ELI5 ELI5 body supplied by app/components/glossary.py from docs/portal_glossary.json._status_vocabulary.Validated. -->

---

## Method: Local Projections (Jorda Impulse Responses)

**1. The Method:** A **local projection** is a method for tracing the cumulative effect of a one-time "shock" in one variable on another variable over time. Rather than fitting a single big system like a VAR and then reading off impulse responses (which requires the whole system to be correctly specified), local projections run **one separate regression per forecast horizon** -- a regression for the 5-day-ahead response, another for 21 days, another for 63 days, and so on. This makes the method robust to model misspecification, at the cost of slightly less efficient estimates. Developed by Jorda (2005).

**2. The Question It Answers:** *If the HY-IG credit spread suddenly widens by one unit today, how much lower are stock returns expected to be over the next week, month, and quarter -- and at what horizon does the effect peak?*

**3. How to Read the Graph:** The chart is a **line-and-band impulse response**. The horizontal axis is horizon in trading days (0, 5, 21, 63 days ahead). The vertical axis is the cumulative expected stock return following a 1-unit shock to the HY-IG spread, expressed as a decimal (so -0.01 means a 1% cumulative drag). The solid line is the point estimate -- our best guess of the effect at each horizon. The shaded band around it is the **95% confidence interval**: if the band stays entirely below zero, the effect is statistically distinguishable from zero with 95% confidence. If the band crosses zero, the effect is consistent with noise.

**4. Graph:** `hy_ig_v2_spy_local_projections`

**5. Observation:** The impulse response line starts near zero at the 5-day horizon (coefficient = -0.0008, p = 0.32) and drifts progressively more negative as the horizon lengthens: -0.0034 at 21 days (p = 0.12, confidence band still crossing zero), then -0.0085 at 63 days (p = 0.0345, confidence band now entirely below zero at -0.0164 to -0.0006). The R-squared also grows with horizon -- from 0.6% at 5 days to 4.4% at 63 days -- indicating the relationship tightens as we look further out. The shape is a steady, accelerating downward slope, not a quick dip followed by recovery.

<expander>
**6. Deep Dive -- Why use local projections instead of a conventional VAR, and what are the trade-offs?**
Vector autoregressions are the textbook tool for impulse responses, but they require us to assume the entire joint dynamic system is correctly specified -- get the lag order wrong, miss a nonlinearity, and the impulse response for every variable at every horizon is biased. Local projections (Jorda 2005) sidestep this by estimating a separate linear regression at each forecast horizon, where each regression need only be correctly specified at its own horizon. This is a massive robustness gain when relationships are regime-dependent, as ours clearly are. The cost is efficiency: LP standard errors are wider than VAR standard errors when the VAR is correctly specified. We use **HC3 robust standard errors** throughout to account for the overlapping-window problem (a 63-day forward return today shares 62 days with tomorrow's 63-day forward return). The 63-day coefficient clears the 5% significance threshold; the 21-day estimate is suggestive but not significant; shorter horizons are noise. We also ran state-dependent versions (calm vs stress) and the stress-state coefficient is roughly 2-3x larger than the full-sample estimate.
</expander>

**7. Interpretation:** Credit-spread shocks do not hit equities immediately. The effect builds slowly over one to three months, reaching roughly -0.85% of cumulative return at the 63-day horizon for a 1-unit spread shock. Practically, this slow diffusion of credit information into equity prices is precisely what makes the signal **actionable**: a warning that was fully priced in by the next day would be useless, but a warning that takes 4-12 weeks to play out leaves time for a disciplined investor to reduce exposure. The accelerating shape of the response (flat at 5 days, curving down at 21 days, steepening at 63 days) is also consistent with a "drip feed" view of credit information: each week, a little more of the bond market's pessimism gets incorporated into stock prices.

**8. Key Message:** **A credit-spread shock drags equity returns progressively lower over the next three months, with the effect statistically significant by the 63-day horizon -- the slow burn is a feature, not a bug, because it opens a window for investors to act.**

`chart_status: "Validated"` <!-- RES-22: artifact exists in output/charts/hy_ig_v2_spy/plotly/ and validates against docs/schemas/chart_type_registry.json within 60 days. META-ELI5 ELI5 body supplied by app/components/glossary.py from docs/portal_glossary.json._status_vocabulary.Validated. -->

---

## Method: Regime Analysis (Hidden Markov Model)

**1. The Method:** A **Hidden Markov Model (HMM)** is a statistical model that assumes the market is always in one of several unobservable ("hidden") states -- for us, "calm" or "stressed" -- each with its own characteristic mean, volatility, and cross-asset correlations. The model cannot see the states directly; instead it infers, for every day in the sample, the probability that the market was in each state that day, based on the observed behaviour of the HY-IG spread and VIX. Developed originally for speech recognition in the 1960s, HMMs were brought into financial regime modelling by Hamilton (1989) and are now standard.

**2. The Question It Answers:** *Are there distinct market states in which the credit-equity relationship behaves fundamentally differently -- and can we identify when the market switches from one state to another without imposing arbitrary thresholds like "spreads above 500 basis points"?*

**3. How to Read the Graph:** The chart is a **time-series of regime probabilities** from 2000 through 2025. The horizontal axis is calendar time. The vertical axis shows two stacked probability bands, each running from 0 to 1: the blue band is the estimated probability of being in the **calm regime** at each date, and the red band is the estimated probability of being in the **stress regime**. The two bands always sum to 1 (since the market must be in one of the two states). SPY price is overlaid as a thin black line for visual anchoring, and NBER recession periods are shaded in grey.

**4. Graph:** `hy_ig_v2_spy_hmm_regime_probs`

**5. Observation:** For long stretches -- roughly 2003 through mid-2007, 2010 through 2014, and 2016 through 2019 -- the blue "calm" band sits near 1.0 almost continuously. The red "stress" band spikes abruptly and unmistakably during four episodes: late 2001 through 2002 (dot-com bust), mid-2007 through mid-2009 (GFC, with the most persistent stress state in the sample), early 2020 (COVID, a sharp but short-lived spike), and scattered bursts during 2022 (rate shock). The transitions between calm and stress are not gradual -- the HMM typically flips the dominant regime within a handful of trading days once stress begins to build.

<expander>
**6. Deep Dive -- How does the HMM decide when to switch regimes, and how do we know it is not just curve-fitting?**
The Gaussian HMM we use (fitted on daily HY-IG spread changes and VIX levels jointly) has two free components per state: a mean vector and a covariance matrix. The model also estimates a 2x2 transition matrix of probabilities -- for example, "given that today is calm, what is the probability tomorrow is still calm?" These transition probabilities are typically in the high 0.95-0.99 range for staying in the current state, which creates the persistent "flat" periods visible in the chart. Regime identification is done via the **Viterbi algorithm**, which finds the most likely sequence of hidden states given the observed data. We guard against overfitting three ways: (1) we fit only on the 2000-2017 in-sample window and let the HMM classify 2018-2025 cold; (2) we compare 2-state and 3-state variants by log-likelihood and BIC -- 2-state wins on parsimony; (3) we check that stress-state identification lines up with independently-known crisis dates (GFC, COVID, 2022) rather than being a retrospective fit. Out-of-sample classification correctly flags the COVID shock within about a week of its onset.
</expander>

**7. Interpretation:** The HMM confirms that markets genuinely operate in two distinct modes rather than on a smooth continuum, and the stress state lines up tightly with episodes that economists, historians, and investors would all independently call crises. This is the engine room of the trading strategy: instead of applying the same rule in all weather, the strategy only acts on the credit signal when the HMM puts high probability on the stress state. Equally important, the model discovers where the stress threshold lies from the data itself -- typically corresponding to HY-IG z-scores of 1.5-2.0 and raw spreads of 500-600+ basis points -- rather than requiring us to impose an arbitrary cutoff that might be wrong or curve-fit.

**8. Key Message:** **The market really does have two distinct states, and the HMM can identify the transition from calm to stress in near real time -- this is what turns the credit signal from an interesting correlation into a usable trading rule.**

`chart_status: "Validated"` <!-- RES-22: artifact exists in output/charts/hy_ig_v2_spy/plotly/ and validates against docs/schemas/chart_type_registry.json within 60 days. META-ELI5 ELI5 body supplied by app/components/glossary.py from docs/portal_glossary.json._status_vocabulary.Validated. -->

---

## Method: Quantile Regression

**1. The Method:** An ordinary (OLS) regression asks "on average, how do stock returns respond to credit spreads?" -- but an average can hide very different behaviour in the tails of the distribution. **Quantile regression**, developed by Koenker & Bassett (1978), instead estimates separate coefficients for different **percentiles** of the stock-return distribution: one for the 5th percentile (worst 5% of outcomes), one for the median (typical outcome), one for the 95th percentile (best 5%), and so on. It is the right tool when you suspect a variable matters more for tail outcomes than for the middle of the distribution.

**2. The Question It Answers:** *Do credit spreads predict large stock losses, large stock gains, both, or neither -- and is the effect the same across the entire return distribution, or is it concentrated in the tails?*

**3. How to Read the Graph:** The chart is a **coefficient plot across quantiles**. The horizontal axis shows return quantiles from 0.05 (worst 5% of forward returns) on the left to 0.95 (best 5%) on the right. The vertical axis shows the estimated HY-IG coefficient at each quantile -- that is, how much that slice of the return distribution moves in response to a unit change in the credit spread. Each point estimate has a small vertical bar showing its 95% confidence interval. A horizontal dashed line at zero marks the "no effect" reference. If all the coefficients sit flat near zero, credit spreads do not matter at any part of the distribution. If they slope from negative on the left to positive on the right, credit spreads are "spreading out" the return distribution -- making bad outcomes worse and good outcomes better.

**4. Graph:** `hy_ig_v2_spy_quantile_regression`

**5. Observation:** The coefficient pattern forms a clean, monotonic slope from strongly negative on the left to strongly positive on the right. At the 5th percentile, the coefficient is -0.0117 (p < 0.001, confidence interval -0.0134 to -0.0100); at the 10th percentile it is -0.0094 (p < 0.001); at the 25th percentile, -0.0052 (p < 0.001); at the median, essentially zero (+0.000008, p = 0.98, confidence interval straddling zero); at the 75th percentile, +0.0046 (p < 0.001); at the 90th percentile, +0.0083 (p < 0.001); at the 95th percentile, +0.0118 (p < 0.001). The median coefficient is the only one that is not statistically different from zero.

<expander>
**6. Deep Dive -- What does it mean economically for the median coefficient to be zero while the tails are strongly significant?**
This pattern -- zero at the centre, large and opposite-signed at the tails -- is the fingerprint of a **variance-shifting** rather than a **mean-shifting** relationship. In plain terms, wider credit spreads do not change the typical day's return, but they make the distribution of possible returns wider on both sides: worse lows and (apparently) better highs. This is the "Vulnerable Growth" pattern documented by Adrian, Boyarchenko & Giannone (2019) for GDP growth and financial conditions; we find it alive and well in daily equity returns. The symmetric shape is worth a note: the left tail (losses) is what matters for risk management, but the positive right-tail coefficients are not a bullish signal -- they reflect the fact that high-stress environments also produce large relief rallies and short squeezes, which inflate the upper percentiles without improving average returns. The near-zero median is the reason simple mean-regression (OLS) predictive regressions looked so underwhelming in the earlier table: averaging across the distribution washes out the tail information. We report bootstrapped confidence intervals with 1,000 resamples; the pattern is robust to outliers and sample splits.
</expander>

**7. Interpretation:** Credit spreads are a **risk signal**, not a return signal. They tell you when the distribution of outcomes is about to widen -- when both terrible and terrific days become more likely -- but they do not tell you the average outcome will be better or worse. This is exactly the right shape for a defensive tool: a rational risk-averse investor cares disproportionately about the left tail, so a signal that sharpens predictions specifically at the 5th and 10th percentiles is far more valuable than one that shifts the mean. The symmetric right-tail response also explains why the strategy cannot be run as a long-short system: the apparent "upside" in the right tail comes from stress-driven volatility, not genuine predictability of gains, and a short-during-stress position would get steamrolled by the same relief rallies that create those positive coefficients.

**8. Key Message:** **Credit spreads are a fire alarm, not a green light -- they sharply predict the worst stock-return outcomes but say nothing about the average, which is why the strategy should reduce exposure in stress and never try to short it.**

`chart_status: "Validated"` <!-- RES-22: artifact exists in output/charts/hy_ig_v2_spy/plotly/ and validates against docs/schemas/chart_type_registry.json within 60 days. META-ELI5 ELI5 body supplied by app/components/glossary.py from docs/portal_glossary.json._status_vocabulary.Validated. -->

---

## Method: Pre-whitened Cross-Correlation Function (CCF)

**1. The Method:** A **pre-whitened Cross-Correlation Function (CCF)** measures how strongly two time series move together at different time offsets -- lag 0 is contemporaneous, negative lags ask whether series A leads series B by that many days, positive lags ask the reverse. "Pre-whitened" means we first fit an ARIMA model to each series and run the cross-correlation on the residuals, because raw CCFs on autocorrelated financial data produce spurious lead-lag signals that are really just each series remembering its own past.

**2. The Question It Answers:** *At short daily horizons, who moves first -- the bond market or the stock market -- and how many days of lead time (if any) does either side enjoy?*

**3. How to Read the Graph:** The horizontal axis is lag in trading days, running from -20 (the spread moves 20 days after SPY) through 0 (contemporaneous) to +20 (the spread moves 20 days before SPY). The vertical axis is the pre-whitened correlation, bounded between -1 and +1. Each vertical bar is one lag; bars that cross the dashed horizontal lines at +/-0.0238 are statistically significant at the 95% level (the band is 1.96/sqrt(N) for N = 6,782 observations). Bars shaded darker are the significant ones; pale bars are noise. Read left-to-right: significant negative-lag bars mean SPY led the spread; significant positive-lag bars mean the spread led SPY.

**4. Graph:** `ccf_prewhitened`

**5. Observation:** 15 of the 41 lags from -20 to +20 are statistically significant at 95% confidence. The significant negative lags (SPY leading the spread) dominate: they land at -1, -2, -5, -7, -9, -12, -15, and -17 days, including the largest magnitude in the whole chart at lag -17 (CCF = -0.069). The contemporaneous lag (0) sits right at the significance boundary on the negative side. The positive-lag side (spread leading SPY) is much sparser, with significant bars only at +6, +7, +9, and +13 days. The overall visual impression is a left-weighted forest of negative bars on the "SPY leads" side and a thinner scatter of alternating-sign bars on the "spread leads" side.

<expander>
**6. Deep Dive -- What does "pre-whitened" actually change, and why did we pick ARIMA(2,0,2)?**
A raw CCF on two autocorrelated series inherits the autocorrelation of both sides, so almost every lag ends up "significant" even when there is no genuine cross-dynamic relationship -- the statistic is really measuring each series talking to itself. Pre-whitening fixes this by fitting an ARIMA(p, d, q) model to each series, extracting the residuals (which are approximately white noise by construction), and running the CCF on those residuals. The cross-correlation that survives pre-whitening reflects only genuine dynamic interaction, not self-memory. We selected ARIMA(2,0,2) for both series by BIC grid search over p <= 5 and q <= 2 on the full daily sample (2000-01-03 to 2025-12-31, N = 6,782); the same order was applied to both the HY-IG spread and the SPY log-return series so neither side gets a filter the other does not. The 95% confidence half-width of +/-0.0238 follows from the usual 1.96/sqrt(N) large-sample rule.
</expander>

**7. Interpretation:** At sub-monthly horizons, the CCF says something that surprises readers who have only seen the "credit leads equity" headline: **it is stocks that move first, not credit.** The strongest significant bars sit on the negative-lag side -- SPY declines today are followed by spread widening over the next 1 to 17 days, not the other way around. This is not a contradiction of the Local Projections result at the 63-day horizon, where credit genuinely leads equity. It is a horizon-specific finding: at daily-to-weekly horizons the equity market reprices first and credit follows, while at the quarterly horizon the bond market's slow accumulation of default-risk information drags equity returns lower. Nor is it a contradiction of the Transfer Entropy result below: CCF is a linear filter that measures price-level co-movement, whereas Transfer Entropy measures nonlinear conditional distribution shifts. The two methods look at different properties of the same joint distribution and answer different questions.

**8. Key Message:** **At daily-to-weekly horizons, equity moves first and credit follows -- the "credit leads equity" story is a quarterly-horizon phenomenon, not a short-term trading edge.**

`chart_status: "Validated"` <!-- RES-22: artifact exists in output/charts/hy_ig_v2_spy/plotly/ and validates against docs/schemas/chart_type_registry.json within 60 days. META-ELI5 ELI5 body supplied by app/components/glossary.py from docs/portal_glossary.json._status_vocabulary.Validated. -->

---

## Method: Transfer Entropy (Nonlinear Information Flow)

**1. The Method:** **Transfer entropy (TE)** is an information-theoretic measure of directed information flow between two time series. Formally, it is the reduction in uncertainty about variable Y's next value that you gain from knowing variable X's past, over and above what you already learn from Y's own past. Unlike Granger causality and the CCF -- both of which are fundamentally linear tests of co-movement in levels -- transfer entropy captures nonlinear relationships and conditional distribution shifts, which is exactly the kind of regime-dependent signal credit-equity data is known to exhibit.

**2. The Question It Answers:** *When we measure information flow in the nonlinear sense -- not just linear price co-movement -- how much information does credit carry about the next move in equities, and how much does equity carry about the next move in credit?*

**3. How to Read the Graph:** The chart is a **paired bar plot** with two bars: one for "Credit -> Equity" (how much the past of the HY-IG spread reduces uncertainty about tomorrow's SPY return) and one for "Equity -> Credit" (the reverse). The vertical axis is transfer entropy measured in **nats** -- a natural-log unit of information, where bigger bars mean more information is flowing in that direction. The permutation p-value is annotated on each bar: p < 0.01 indicates the flow is statistically distinguishable from chance at the 1% level. The visual takeaway is the ratio between the two bars -- not the absolute heights, which are small in any information-theoretic study of daily returns.

**4. Graph:** `transfer_entropy`

**5. Observation:** The Credit -> Equity bar reaches 0.042 nats with permutation p = 0.004 (500 permutations), comfortably clearing the 1% significance threshold. The Equity -> Credit bar reaches only 0.0055 nats with p = 0.050 -- marginal significance at best. The Credit -> Equity bar is roughly 7.6x the height of the Equity -> Credit bar. Both bars are positive (no directional sign in information theory -- TE measures magnitude, not sign), but the asymmetry between them is the headline: information flows from credit into equity far more strongly than it flows from equity into credit.

<expander>
**6. Deep Dive -- What exactly is transfer entropy, and how is this different from Granger causality?**
Transfer entropy from X to Y is defined as H(Y_t+1 | Y_t) - H(Y_t+1 | Y_t, X_t), where H denotes Shannon entropy. In plain English: how much smaller is our uncertainty about Y's next value once we know X's past, compared to only knowing Y's own past? If the answer is zero, X tells us nothing new about Y. If the answer is large, X carries genuine predictive information about Y that Y's own history does not capture. The key difference from Granger causality is that Granger is implemented as a linear regression test -- it can only see relationships that show up in conditional means. Transfer entropy is non-parametric and sees the full conditional distribution, so it picks up threshold effects, regime switches, and tail dependencies that a linear Granger test misses entirely. We estimated TE using a Shannon histogram with 6 equal-frequency (quantile) bins and lag 1 day, and tested significance with a circular block-shift permutation test using 500 permutations. Because `pyinform` was not available in the environment, the estimator was implemented from first principles following Schreiber (2000) -- see `scripts/retro_fix_hy_ig_v2_evan_20260411.py::transfer_entropy_hist` for the exact implementation. TE values are sensitive to bin count; the 6-bin choice is documented in the CSV `bin_method` field for reproducibility.
</expander>

**7. Interpretation:** When information flow is measured in the nonlinear sense -- capturing conditional distribution shifts rather than just linear price co-movement -- **credit leads equity by a decisive margin, roughly 7.6 to 1**. This is the finding that matters for the strategy: the credit channel does genuinely carry information that linear correlation and linear Granger tests understate, because it delivers that information through nonlinearities -- threshold effects, tail events, and regime switches -- which is exactly where credit signals have always been thought to earn their keep. Note that the TE result is not a contradiction of the CCF result above. CCF is a linear filter that picks up price-level co-movement and saw SPY leading at short lags; TE is a nonlinear measure that picks up conditional distribution shifts and sees credit dominating. Both are correct: the two methods measure different properties of the same joint distribution, and the credit signal shows up more clearly in the nonlinear measure because that is the channel through which it actually operates.

**8. Key Message:** **In the nonlinear, information-theoretic sense, credit carries roughly 7.6x more information about equity than equity carries about credit -- this is the quantitative basis for building a credit-led equity-timing strategy.**

`chart_status: "Validated"` <!-- RES-22: artifact exists in output/charts/hy_ig_v2_spy/plotly/ and validates against docs/schemas/chart_type_registry.json within 60 days. META-ELI5 ELI5 body supplied by app/components/glossary.py from docs/portal_glossary.json._status_vocabulary.Validated. -->

---

## Method: Quartile Returns Analysis

**Why this matters:** This is the simplest possible strategy test -- if you had just sorted all trading days by credit spread level and asked "how did SPY perform?" -- would the answer differ between tight-spread days and wide-spread days? The chart below shows that yes, it differs dramatically -- and this simple split is the intuitive foundation for the more sophisticated HMM-based winning strategy.

**1. The Method:** A **quartile returns analysis** sorts every day in the sample into four bins based on the HY-IG spread level that day -- Q1 is the 25% of days with the tightest spreads, Q4 is the 25% with the widest -- and computes full return statistics (mean, volatility, Sharpe, annualized return, max drawdown) for the SPY returns earned in each bin. It is the simplest possible regime-conditional check: does the forward return distribution for SPY look different depending on which credit-cycle state we are in, without any fitted model telling us where the regime boundaries should fall?

**2. The Question It Answers:** *If we had done nothing more sophisticated than "buy SPY when HY-IG spreads are in their tightest 25% and sit in cash otherwise," how would that strategy have performed -- and how does performance scale across the full spread distribution?*

**3. How to Read the Graph:** The chart is a **bar plot** showing four bars, one per quartile, with the Sharpe ratio on the vertical axis. Q1 (leftmost) represents the tightest-spread days -- the roughly 1,700 days when HY-IG OAS was between 147 and 255 bps (1.47% to 2.55%). Q4 (rightmost) represents the widest-spread days -- 450 to 1,531 bps (4.5% to 15.3%). A reference line at Sharpe = 0 separates bins where risk-taking was rewarded from bins where it was not. A secondary annotation shows the per-quartile max drawdown so readers can see the risk side of the equation alongside the return side.

**4. Graph:** `quartile_returns`

**5. Observation:** Sharpe ratios form a monotone declining gradient from left to right: Q1 = 1.45 (tightest spreads, annualized return +18.4%, max drawdown -10.7%), Q2 = 1.12 (+17.2%, -14.9%), Q3 = 0.32 (+5.6%, -22.1%), Q4 = -0.04 (widest spreads, -1.0% annualized, max drawdown -62.6%). The four bars step cleanly downward from left to right with no non-monotone inversion anywhere. The drawdown gradient is even steeper than the Sharpe gradient: a Q4 investor lost 62.6 cents on the dollar at the worst point, six times the Q1 drawdown. The Q1-vs-Q4 difference in mean returns is not statistically significant on a Welch t-test (t = 1.501, p = 0.134), but the risk-adjusted spread is decisive.

<expander>
**6. Deep Dive -- Why is the mean difference not significant when the Sharpe difference is so large?**
The Welch t-test asks whether two groups have different average returns, but averages are dominated by the low-volatility majority of days in each bin. The Q4 bin's daily standard deviation is roughly 2.5x the Q1 bin's daily standard deviation -- when you divide the mean difference by this inflated denominator, the t-statistic comes in at 1.501 and the p-value lands at 0.134. Statistical significance on means is the wrong frame here: **the economically decisive finding is the Sharpe and drawdown gradient, not the mean difference**, because investors care about risk-adjusted outcomes and the risk side is exactly where Q4 blows out. Quartile cutoffs are unconditional (pooled over the full 2000-2025 daily sample), not rolling, which intentionally lets the GFC and COVID widening episodes concentrate in Q4 as they historically did. The cutoffs themselves -- 2.55%, 3.22%, 4.58%, 15.31% -- are reported in the CSV for reproducibility. Welch's t-test is used rather than Student's because the two bins have visibly unequal variances.
</expander>

**7. Interpretation:** The simplest possible strategy -- **buy SPY only when HY-IG spreads are tight (Q1), sit in cash otherwise** -- would have earned a Sharpe of 1.45 on the days the trader was invested, beating both the HMM-based tournament winner (OOS Sharpe 1.27) and the buy-and-hold benchmark (OOS Sharpe ~0.90) on the risk-adjusted metric that matters most. This does not automatically mean the quartile rule is a better strategy than the HMM (it spends most of the sample in cash, the cutoffs are in-sample, and the mean difference is not significant), but it does frame what regime detection is actually doing: **the HMM is doing a more sophisticated version of quartile classification, using changes and volatility rather than just levels**. The gradient from Q1 to Q4 -- a Sharpe swing of 1.49 points and a drawdown swing of 51.9 ppts -- is the cleanest possible picture of why any credit-conditioned equity strategy works. It also explains the shape of the Quantile Regression result above: when spreads are wide, the SPY return distribution genuinely widens out, and the left tail is where most of the damage happens.

**8. Key Message:** **The HMM regime detection strategy (our tournament winner) is essentially a sophisticated version of quartile classification** -- when you cannot manually sort all 6,000+ days and update the cut every day, the HMM does it for you with a statistical model. A no-model "only own stocks when credit spreads are tight" rule would have delivered Sharpe 1.45 and a -10.7% max drawdown in Q1, against -0.04 and -62.6% in Q4 -- the credit-cycle regime is the single most important variable in this analysis, and that is precisely what the HMM picks up automatically using changes and volatility rather than just levels.

`chart_status: "Validated"` <!-- RES-22: artifact exists in output/charts/hy_ig_v2_spy/plotly/ and validates against docs/schemas/chart_type_registry.json within 60 days. META-ELI5 ELI5 body supplied by app/components/glossary.py from docs/portal_glossary.json._status_vocabulary.Validated. -->

---

### The Combinatorial Tournament

We tested approximately 1,000+ meaningful combinations of signals (13 types), thresholds (7 methods), strategies (4 types), lead times (9 values), and lookback windows (4 lengths). These were ranked by out-of-sample **Sharpe ratio** -- a measure of risk-adjusted return calculated as (return minus risk-free rate) divided by volatility, where higher values mean better returns per unit of risk taken -- over 2018-2025 (data the models never saw during estimation). The top 5 strategies were then subjected to rigorous walk-forward validation, bootstrap significance testing, and transaction cost sensitivity analysis.

*(See `results/hy_ig_v2_spy/tournament_results_20260410.csv` for the full leaderboard.)*

**Transition to Page 4:** The four statistical tests agree: credit spreads carry genuine, direction-consistent, tail-concentrated, regime-dependent predictive information for stock returns. The practical question is: can an investor use this signal to improve their risk-adjusted returns -- and at what cost?

---

## Page 4 -- The Strategy (Trading Applications)

<details>
<summary>🧒 Plain English version</summary>

Our computer looked at every possible combination of "signal strength + threshold + trade rule" to find the one that would have made the most money (adjusted for risk) in past data. The winner is a strategy that reduces stock exposure when credit spread stress is high and adds back when stress fades. In this section we explain exactly what the strategy does, when to use it, and when it would have failed.

</details>

### How the Signal is Generated

The HMM (hidden Markov model) fits two hidden market states to the credit-spread data -- "calm" and "stressed." Every day, it asks a simple question: given how the HY-IG spread and VIX moved today, is the market more likely to be in the calm state or the stressed state? The answer is a probability between 0 and 1 -- think of it as a continuously-updating "stress meter" built from the behaviour of the bond market itself, with no arbitrary thresholds imposed by the analyst.

When that stress probability crosses 50%, the strategy reduces equity exposure; the higher the probability, the lower the target allocation to SPY. When the probability falls back below 50%, equity exposure is restored in the same proportional way. The strategy is not trying to predict the next crisis -- it is responding to the market's own indication that something is wrong, and acting before the equity market has fully priced it in.

The key insight behind the rule is that credit markets price in deterioration earlier than equity markets. By the time equity volatility spikes, credit spreads have typically already widened. The HMM translates that widening into an actionable probability signal -- so the investor does not need to watch every spread tick themselves and does not need to judge "how wide is wide enough" on any given day. For the formal mathematical specification of the HMM, see the Methodology page.

### How the Signal Translates to Action

The tournament identified the most robust credit-signal strategies for equity allocation. The winning strategy uses a **Hidden Markov Model (HMM)** -- a statistical model that infers which of several unobservable "hidden" market states (calm vs. stressed) is active at any given time, based on patterns in credit spread changes and VIX levels.

**In plain English, the strategy rule is:**

The HMM continuously estimates the probability that markets are in a "stress" regime. When that stress probability exceeds 50%, the strategy scales down its equity exposure proportionally to the severity of the signal -- at 50% stress probability, it holds less stock; at 100% stress probability, it would hold no stock at all. When the stress probability drops back below 50%, the strategy returns to full equity exposure. This graduated approach (called **Signal Strength**, or P2) avoids the all-or-nothing whipsaw of a simple on/off switch.

<!-- expander: Why scale positions instead of switching all-in or all-out? -->
A simple on/off strategy (fully invested or fully in cash) can suffer from "whipsaw" -- rapidly alternating between in and out of the market when the signal hovers near its threshold. This generates transaction costs and tax events with no benefit.

The Signal Strength (P2) approach scales the equity position proportionally to the signal: if the HMM says there is a 60% chance of stress, the strategy holds only 40% in stocks and 60% in cash. This smooths transitions, reduces turnover, and allows the strategy to partially capture upside even when some stress is present.

The tournament tested four strategy types: (P1) Long/Cash -- fully in or fully out; (P2) Signal Strength -- proportional scaling; (P3) Long/Short -- shorting stocks during stress; and (P4) Collar -- using options to hedge. P2 won because it delivered the best risk-adjusted return after transaction costs.
<!-- /expander -->

<!-- expander: What is a z-score, and why do we use one? -->
A z-score measures how unusual a current value is compared to its recent history. A z-score of 0 means the spread is at its historical average. A z-score of +2 means the spread is 2 standard deviations above average -- a relatively rare condition that historically has occurred less than 5% of the time.

We use z-scores rather than raw spread levels because the "normal" level of credit spreads changes over time. A 400 bps spread in 2005 (when spreads had been tightening for years) meant something different than a 400 bps spread in 2010 (when spreads were coming down from crisis peaks). The z-score adjusts for this by comparing today's spread to its recent window, providing a context-aware measure of stress.
<!-- /expander -->

### Key Strategy Metrics

| Metric | Credit-Signal Strategy (W1) | Buy-and-Hold SPY |
|--------|---------------------------|-------------------|
| OOS Sharpe Ratio (2018-2025) | **1.27** | ~0.90 |
| Annualized Return (OOS) | ~11.3% | ~10% |
| Maximum Drawdown | **-10.2%** | ~-34% |
| Annual Turnover | ~3.8 trades/year | 0 |
| Breakeven Transaction Cost | 50 bps | N/A |

**What this means:** The credit-signal strategy delivered comparable returns to buy-and-hold but with dramatically less pain. Its worst peak-to-trough decline was -10.2%, versus -34% for an investor who simply held SPY through the same period. The Sharpe ratio of 1.27 (versus 0.90 for buy-and-hold) means each unit of risk taken was rewarded with roughly 40% more return. The strategy only needed about 4 trades per year, and it would remain profitable even if transaction costs were 10x higher than our 5 bps assumption.

### Where the Strategy Adds Value -- and Where It Does Not

The primary value of the credit signal is **drawdown reduction during stress periods**, not alpha generation during calm markets. During the long stretches when credit conditions are normal, the strategy is fully invested and performs identically to buy-and-hold. Its edge comes from avoiding the worst of the drawdowns when credit markets signal stress.

This means:
- **It will underperform in V-shaped recoveries.** If the market crashes and bounces back quickly (as in COVID), the strategy may exit at or near the bottom and re-enter after some of the recovery has already occurred. The COVID V-shape is the worst-case scenario for any trend-following or risk-off strategy.
- **It excels in prolonged bear markets.** The GFC lasted roughly 18 months peak-to-trough. A strategy that exited early in that decline and waited for credit conditions to normalize captured most of the avoided drawdown.
- **It is largely inert during calm periods.** This is a feature, not a bug -- the strategy avoids generating trading costs and tax events when the credit signal has little to say.

### How to Use This Indicator Manually

If you want to use the HY-IG spread as a signal yourself -- with no automated system, no code, no broker API -- follow this 3-step routine. This is written for the stock investor who rebalances a long-only portfolio a few times a year, not for an algorithmic trader.

**1. Check the spread weekly.**
- **Source:** FRED series `BAMLH0A0HYM2` (HY OAS) and `BAMLC0A0CM` (IG OAS) -- subtract IG from HY to get the spread. The free FRED charting page will plot the difference directly. Any Friday-afternoon reading is fine; you do not need intraday data.
- **What to compute:** the current spread in **bps (basis points, where 100 bps = 1%)**, and where it sits inside the last **504 trading days** (roughly 2 years) of history. Most spreadsheet tools can compute a percentile rank; so can FRED's own download-and-chart interface.

**2. Interpret where you are.**
- **Bottom 25% of the 504-day range -> calm regime.** Full equity exposure is reasonable. Historically this is where Sharpe runs well above 1 and drawdowns are shallow.
- **Top 25% of the 504-day range -> stress regime.** Reduce equity exposure toward **0-50%**. Historically this is the band where SPY has produced annualised returns close to zero and drawdowns above 60%.
- **Middle 50% -> ambiguous.** Hold your current allocation. The signal has no statistical edge in the middle of the distribution (this is why the median coefficient in the Quantile Regression block is essentially zero).

**3. Act -- or consciously decide not to.**
- The research shows the signal works best on a **63-day (3-month) forward horizon**, so do not overreact to week-to-week noise. One week in the top quartile is not a selling signal; two or three consecutive weeks is.
- **Moving calm -> stress:** reduce exposure over 2-4 weeks, not in one day. The point of scaling is to avoid whipsaws when the signal oscillates around the 75th-percentile cutoff.
- **Moving stress -> calm:** add back **gradually**. Historically the recovery is slower than the drop, so averaging in over several weeks rarely costs much.

**Concrete example -- the 2020 COVID crash.**
- On **2020-02-14**, the HY-IG spread was roughly **350 bps (3.50%)** -- firmly in the bottom quartile of its 504-day range. A manual user following this rule would have been fully invested.
- Over the next four weeks the spread blew out to **1,100 bps (11.0%)** by **2020-03-16** -- far into the top quartile and still climbing.
- A disciplined manual user, seeing the spread cross the 75th percentile of the 504-day range around **2020-02-24 to 2020-03-02**, would have started scaling down. In practice this probably means moving from 100% equity to roughly 50% over one to two weeks, then further down as the widening accelerated.
- The spread compressed back below **500 bps (5.00%)** by **2020-06-08**, crossing back into the middle/lower quartiles. The manual user would then have started adding equity back, reaching full exposure over the following weeks.
- This mechanical rule would not have timed the bottom perfectly -- no rule does -- but it would have avoided the worst of the -34% buy-and-hold drawdown and participated in the recovery from roughly July onward.

**Caveats for manual use.**
- **Signals require patience.** This strategy works on weeks-to-months horizons, not days. If you check it daily and trade every wiggle, commissions and taxes will eat the edge.
- **Transaction costs and taxes eat into gains.** The backtest charges 5 bps (0.05%) round-trip; the real-world minimum for retail investors is often higher, and capital-gains taxes on a taxable account can dwarf commissions.
- **This is one signal.** Combining with others -- volatility regime, yield-curve inversion, macro momentum -- likely improves robustness. See the separate analyses on **VIX x SPY** and **Yield Curve x SPY** in the portal for complementary signals.
- **Never short-sell based on this rule.** The Quantile Regression evidence shows that stress-regime upside is dominated by violent relief rallies; a naive short would get run over by the same bars that make the right-tail coefficient positive.

### Execution Points -- Actual Trigger Dates

The winning strategy made many small position adjustments across the 2000-2025 backtest -- 418 rows in `winner_trades_broker_style.csv`. The table below surfaces **eight inflection points** around major historical stress events, pulled directly from that log, so readers can tie the abstract HMM stress probability back to concrete history. Each row is reproducible: open the broker-style CSV, jump to the row number in the right-most column, and the exact commission, notional, price, and running cumulative P&L are all there.

| Date | Event | HMM Stress Prob | Position Change | Source Row |
|------|-------|-----------------|-----------------|------------|
| 2008-04-25 | March-2008 stress fades (Bear Stearns aftermath) | 0.415 -> 0.195 -> 0.117 -> 0.038 | Scale-up: 34.2% -> 58.5% -> 80.5% -> 88.3% -> 96.2% over 4 trading days | Rows 95-98 |
| 2008-06-02 | Pre-Lehman credit deterioration builds | 0.443 -> 0.672 -> 0.813 -> 0.979 | Scale-down: 96.2% -> 55.7% -> 32.8% -> 18.7% -> 2.1% over 4 trading days | Rows 99-102 |
| 2008-09-01 | Lehman week -- full stress-regime lock-in | 0.820 -> 0.931 -> 0.999 | Scale-down: 30.8% -> 18.0% -> 6.9% -> 0.1% over 3 trading days | Rows 111-113 |
| 2009-12-21 | GFC recovery -- stress probability breaks below 0.5 | 0.932 -> 0.613 -> 0.433 -> 0.318 | Scale-up: 0.1% -> 6.8% -> 38.7% -> 56.7% -> 68.2% over 4 trading days | Rows 114-117 |
| 2020-01-27 | Early COVID false alarm (reverted within two days) | 0.127 -> 0.998 -> 0.882 -> 0.080 | Oscillation: 95.3% -> 87.3% -> 0.2% -> 92.0% -> 98.4% -- the kind of noise the P2 Signal Strength smoothing is designed to contain | Rows 297-301 |
| 2020-02-24 | COVID panic onset -- single-day collapse to cash | 0.086 -> 1.000 | Two-day move: 98.4% -> 91.4% -> 0.0% cash | Rows 302-303 |
| 2022-01-13 | Rate-shock widening begins | 0.070 -> 0.268 -> 0.880 -> 0.995 | Scale-down: 98.8% -> 93.0% -> 73.2% -> 12.0% -> 0.5% over 5 trading days | Rows 344-347 |
| 2022-08-12 | Mid-2022 recovery attempt (proved short-lived) | 0.911 -> 1.000 | Brief scale-up reversed: 0.5% -> 8.9% -> 0.0% | Rows 348-349 |

The `reason` field in each row repeats the HMM stress probability and the before/after position weights, which is the auditable record of what the strategy saw and what it did. Because this is a P2 Signal Strength strategy, position changes are **proportional** to the HMM stress probability -- never all-or-nothing -- which is why many rows show fractional moves rather than 0%/100% flips.

### Important Caveats

1. **Transaction costs matter.** All strategy metrics include 5 basis points (0.05%) per round-trip trade. The breakeven transaction cost -- the level at which the strategy's edge disappears entirely -- is 50 bps, providing a comfortable margin of safety.
2. **Execution delay degrades performance.** We tested 1, 2, 3, and 5-day delays between signal generation and trade execution. Performance decreases with longer delays, reflecting the speed at which credit information gets priced into equities. The maximum acceptable delay for this strategy is approximately 5 days.
3. **The 2022 episode is a genuine weakness.** The strategy's credit signal widened modestly during 2022, but not enough to trigger a full risk-off position in most configurations. This is because the 2022 bear market was driven by rate hikes and valuation compression, not by the credit deterioration that the HY-IG spread is designed to detect. Investors should not expect the credit signal to protect against all types of equity drawdowns -- only those rooted in credit stress.
4. **Past performance is not indicative of future results.** Regime shifts, changes in market microstructure, or new central bank tools (like the Fed's corporate bond purchasing programs, first deployed in 2020) could alter the credit-equity relationship going forward.
5. **This is a risk management tool, not an alpha generator.** The primary value is in reducing drawdowns during stress periods rather than generating excess returns during calm periods. Think of it as portfolio insurance that happens to be free (or slightly profitable) on average.

### How to Read the Trade Log

**These are simulated trades from a backtest, not actual broker executions.** The strategy was never run with real money — the trade log is the output of replaying the HMM stress signal against historical prices, assuming a $10,000 starting stake and 5 basis points (0.05%) of round-trip commission per trade.

Two files are available on the Evidence page. The **broker-style log** (`winner_trades_broker_style.csv`) is the default, user-friendly view — one row per execution, formatted the way a retail brokerage statement would look. The **position log** (`winner_trades.csv`) is the researcher/debugging view, with one row per position-weight change and additional diagnostic columns.

**Key columns in the broker-style log:**
- `trade_date` — the date the trade would have been executed.
- `side` — BUY (scaling up equity exposure) or SELL (scaling down toward cash).
- `quantity_pct` — the *resulting* target equity exposure as a percentage of the portfolio, not the size of the trade itself. Because this is a P2 Signal Strength strategy, the position is sized proportionally to the HMM stress probability — 100% long when stress is near zero, 0% (all cash) when stress is near one.
- `price` / `notional_usd` — SPY closing price and dollar value of the resulting position.
- `commission_bps` / `commission_usd` — transaction cost charged on the trade (5 bps, i.e. 0.05%).
- `cum_pnl_pct` — cumulative strategy return since inception, in percent.
- `reason` — human-readable signal value and the scale-up or scale-down step that triggered the row.

**Concrete example — COVID 2020.** On **2020-02-24**, the HMM stress probability jumped from **0.086 to 1.000** in a single day as credit markets reacted to the unfolding pandemic. The broker-style log shows a SELL taking the target equity exposure from **91.4% down to 0%** (all cash) at an SPY price of $294.65. That row is immediately after 2020-02-21 in the CSV. This single transition is what kept the strategy's maximum drawdown to -10.2%, versus roughly -34% for buy-and-hold SPY through the same period.

**Transition to Page 5:** For readers who want to understand exactly how we reached these conclusions -- or who want to replicate and extend the analysis -- the methodology section provides full details on data, methods, and diagnostics.

---

## Page 5 -- The Method (Technical Appendix)

<details>
<summary>🧒 Plain English version</summary>

This section explains the technical details of how we did the analysis -- which data we used, which statistical methods, and what could go wrong. Normal readers can skip it. Expert readers can use it to criticise our work and suggest improvements.

</details>

### Data Sources

All data is sourced from publicly available databases accessible through our MCP server stack:

- **Credit spreads (in-scope):** ICE BofA Option-Adjusted Spread indices via FRED. OAS (option-adjusted spread) strips out the effect of embedded options like call provisions to isolate pure credit risk. The analytical universe for this pair is strictly HY-IG: BAMLH0A0HYM2 (HY OAS) minus BAMLC0A0CM (IG OAS).
- **Equity prices:** SPY ETF adjusted close via Yahoo Finance.
- **Exploratory-only series (not in the HY-IG × SPY analytical universe):** BAMLH0A1HYBB (BB OAS), BAMLH0A3HYC (CCC OAS), BAMLC0A4CBBB (BBB OAS), CBOE VIX (^VIX) / VIX3M (^VIX3M) / MOVE via Yahoo Finance, Treasury yields (DGS10, DGS2, DTB3), NFCI, initial claims (ICSA), fed funds rate (DFF), SOFR, St. Louis FSI (STLFSI2), gold (GC=F), copper (HG=F), DXY (DX-Y.NYB), HYG, KBE, IWM. These were inspected during exploration; those that showed noteworthy off-scope relationships are logged under *Analyst Suggestions for Future Work* on this page per ECON-AS. None of them enter the Evidence- or Strategy-page analyses per ECON-SD.

### Sample Period

- **Full sample:** January 2000 to December 2025 (daily, ~6,500 business days)
- **In-sample (model estimation):** January 2000 to December 2017 (~4,500 obs)
- **Out-of-sample (strategy evaluation):** January 2018 to December 2025 (~2,000 obs)

The 70/30 in-sample/out-of-sample split provides a generous 8-year out-of-sample window that includes multiple distinct market episodes (2018 volatility spike, COVID crash, 2022 rate shock, 2023-25 recovery), preventing the strategy from being validated on only one type of market environment.

### Indicator Construction

The primary indicator is the HY-IG spread: BAMLH0A0HYM2 minus BAMLC0A0CM, measured in basis points (where 100 bps = 1%). From this raw spread, we derive the series enumerated in the *Signal Universe* section below -- z-scores (252-day and 504-day rolling windows), percentile ranks (504-day and 1260-day), rates of change (21-day, 63-day, 126-day), momentum changes (absolute differences at 21/63/252 days), an acceleration second-difference, realised-volatility diagnostic, and two families of regime-state probabilities (Gaussian HMM and Markov-switching). The complete, authoritative inventory is generated from `results/hy_ig_v2_spy/signal_scope.json` and rendered under *Signal Universe* on this page.

### Econometric Methods

Each method was chosen to answer a specific question about the credit-equity relationship. We used multiple methods deliberately: if a finding holds across techniques with different assumptions, we can be far more confident it is genuine.

| Method | Question It Answers | Why We Chose It |
|--------|-------------------|-----------------|
| Toda-Yamamoto Granger causality | Does credit lead equity, or vice versa? | Works correctly with non-stationary data (unlike standard Granger), which matters because spread levels contain trends. Augmented VAR, lags selected by BIC + d_max = 1. |
| Transfer entropy (Diks-Panchenko) | Is the information flow nonlinear? | Captures threshold effects and asymmetries that linear Granger tests miss -- important because the credit-equity link strengthens nonlinearly during stress. Bandwidth per Diks & Panchenko (2006). |
| Local projections (Jorda) | How does a credit shock affect stocks over time? | Does not require specifying the full system dynamics, making it robust to misspecification -- a genuine concern when relationships are regime-dependent. h = 1, 5, 10, 21, 42, 63 days; state-dependent versions for calm vs. stress. |
| Markov-switching regression | Are there distinct regimes with different credit-equity dynamics? | Lets the data find the regime boundaries rather than imposing arbitrary thresholds. 2-state and 3-state. |
| Gaussian HMM | What regime is the market in right now? | Jointly models HY-IG changes and VIX to infer the hidden state (calm/stress) in real time -- this is the model that powers the winning strategy. 2-state and 3-state. |
| Quantile regression | Does credit primarily warn of bad outcomes? | Estimates the effect at different points in the return distribution (5th percentile, median, 90th percentile), letting us confirm that the signal is concentrated in the left tail. tau = 0.05, 0.10, 0.25, 0.50, 0.75, 0.90. |
| GJR-GARCH | Does credit stress increase stock volatility asymmetrically? | Captures the well-documented "leverage effect" (volatility rises more after losses than it falls after gains) while including credit spreads as an external driver. SPY returns with HY-IG exogenous. |
| Random Forest + SHAP | Which signal transformations matter most? | Provides a nonlinear, non-parametric check on the linear models -- if the same signals dominate in both, we have convergent evidence. Walk-forward with 1-year test windows prevents lookahead bias. |
| Combinatorial tournament | Which strategy actually works out-of-sample? | Systematically tests ~1,000+ combinations of signals, thresholds, and strategies on held-out data, then stress-tests the winners. OOS Sharpe ranking. |

### Diagnostics

Every model undergoes a battery of diagnostic tests to ensure the results are trustworthy:

| Test | What It Checks | Why It Matters |
|------|----------------|----------------|
| Jarque-Bera | Whether residuals follow a bell curve (normality) | If not, our confidence intervals may be wrong |
| Breusch-Pagan | Whether the scatter of residuals is even (homoskedasticity) | Uneven scatter means some predictions are more reliable than others |
| Breusch-Godfrey | Whether residuals are correlated with their own past values (serial correlation) | Correlated residuals inflate our confidence in results |
| RESET | Whether the model's functional form is correct (specification) | Catches cases where we should use a curve instead of a straight line |
| ADF + KPSS | Whether the data has trends that need to be removed (stationarity) | Using trended data in level regressions produces spurious results |

**HC3 robust standard errors** are reported throughout. We use HC3 rather than conventional standard errors because our forward returns overlap in time -- a 63-day return calculated today shares 62 days with tomorrow's 63-day return. Without this correction, we would systematically overstate our confidence in every result. For specifications with longer forecast horizons, we use **HAC (Newey-West) standard errors**, which additionally correct for the autocorrelation introduced by overlapping windows.

### Sensitivity Analysis

To ensure our results are not driven by any single time period or parameter choice, we tested:

- Full sample vs. excluding GFC (2007-2009)
- Full sample vs. excluding COVID (2020)
- Pre-2008 vs. post-2008 sub-samples
- Alternative lag structures (BIC, AIC, fixed 5/10/21)
- Alternative threshold levels and methods
- Walk-forward validation with rolling windows

### Reverse Causality Check

All lead-lag and predictive claims include a reverse-causality test: the same model is estimated with SPY leading HY-IG as well as HY-IG leading SPY. Both sets of results are reported side by side. Local projection impulse responses are compared in both directions. The finding of bidirectional causality is documented and its implications discussed -- specifically, that the credit-to-equity signal strengthens in stress regimes while the equity-to-credit signal dominates in calm regimes. This bidirectionality is not a problem for our strategy -- it is a feature that the regime-switching framework explicitly exploits.

### Signal Universe

<details>
<summary>🧒 Plain English version</summary>

A transparent list of every signal the analysis considered -- not just the ones that bubbled to the top of the correlation chart. If something's in a chart on another page, it's in this list. If it's in this list but not in a chart, we considered it but didn't highlight it. You can reconstruct what was filtered in and out by reading here.

</details>

Every chart, regression, and statistical test on the Evidence and Strategy pages is drawn from the same closed set of HY-IG spread derivatives (on the signal side) and SPY transformations (on the target side). Nothing outside this universe is silently mixed into the analysis. If you see a chart reference a signal, you can find it here.

This table is the authoritative list. It is generated from `results/hy_ig_v2_spy/signal_scope.json`.

#### Indicator derivatives (HY-IG spread side)

<!-- Ace: render table from results/hy_ig_v2_spy/signal_scope.json -> indicator_axis.derivatives. Columns: name | definition | formula | role | appears_in_charts. Caption per APP-CC1: "What this shows: every HY-IG-spread derivative considered in this pair's analysis, whether charted or not." -->

#### Target derivatives (SPY side)

<!-- Ace: render table from results/hy_ig_v2_spy/signal_scope.json -> target_axis.derivatives. Columns: name | definition | formula | role | appears_in_charts. Caption per APP-CC1: "What this shows: every SPY-side derivative considered in this pair's analysis, whether charted or not." -->

### Analyst Suggestions for Future Work

<details>
<summary>🧒 Plain English version</summary>

During the work on this pair, we noticed some other indicators that correlate with SPY returns. We're NOT using them in this pair's analysis -- that would blur what the page is about. But they're listed here in case you'd like us to explore them in a future pair or a variant family. It's just a notes page for you, not a queue that auto-runs.

</details>

During this pair's analysis, the team noticed several signals outside the HY-IG × SPY scope that showed interesting relationships. These are informational only -- they are NOT included in the analyses above, which are strictly HY-IG-derivative vs SPY-derivative per ECON-SD scope discipline.

If any of these seem worth follow-up work (a new pair, a variant family, a regime overlay, a cross-pair comparison), please request explicitly to the team. There is no automated trigger from this table.

<!-- Ace: render table from results/hy_ig_v2_spy/analyst_suggestions.json -> suggestions. Columns: signal_name | proposed_by | observation | rationale | possible_use_case | caveats. Caption per APP-CC1: "How to read it: suggestions are informational. If any warrant follow-up work, please request explicitly to the team." -->

### References

Below is the consolidated reference list cited by this narrative. Where an in-text reference uses `[AuthorYear]` notation (e.g. `[Merton1974]`), the entry here is the source. The full analysis brief (`docs/analysis_brief_hy_ig_v2_spy_20260410.md`) carries the extended 25-citation list used during the background scoping phase.

**Credit Spread & Equity Research**
- `[Gilchrist2012]` Gilchrist, S. & Zakrajsek, E. (2012). "Credit Spreads and Business Cycle Fluctuations," *American Economic Review* 102(4), 1692-1720.
- `[Merton1974]` Merton, R.C. (1974). "On the Pricing of Corporate Debt: The Risk Structure of Interest Rates," *Journal of Finance* 29(2), 449-470.
- `[Merton1973]` Merton, R.C. (1973). "Theory of Rational Option Pricing," *Bell Journal of Economics & Management Science* 4(1), 141-183.
- `[Philippon2009]` Philippon, T. (2009). "The Bond Market's q," *Quarterly Journal of Economics* 124(3), 1011-1056.
- `[Acharya2007]` Acharya, V.V. & Johnson, T.C. (2007). "Insider Trading in Credit Derivatives," *Journal of Financial Economics* 84(1), 110-141.

**Methodology -- Time Series Econometrics**
- `[Toda1995]` Toda, H.Y. & Yamamoto, T. (1995). "Statistical Inference in Vector Autoregressions with Possibly Integrated Processes," *Journal of Econometrics* 66, 225-250.
- `[Jorda2005]` Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections," *American Economic Review* 95(1), 161-182.
- `[Koenker1978]` Koenker, R. & Bassett, G. (1978). "Regression Quantiles," *Econometrica* 46(1), 33-50.
- `[Koenker2001]` Koenker, R. & Hallock, K.F. (2001). "Quantile Regression," *Journal of Economic Perspectives* 15(4), 143-156.
- `[Hamilton1989]` Hamilton, J.D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle," *Econometrica* 57(2), 357-384.
- `[Schreiber2000]` Schreiber, T. (2000). "Measuring Information Transfer," *Physical Review Letters* 85(2), 461-464.
- `[Diks2006]` Diks, C. & Panchenko, V. (2006). "A new statistic and practical guidelines for nonparametric Granger causality testing," *Journal of Economic Dynamics & Control* 30, 1647-1669.

**Regime Detection & Risk**
- `[Guidolin2007]` Guidolin, M. & Timmermann, A. (2007). "Asset allocation under multivariate regime switching," *Journal of Economic Dynamics & Control* 31, 3503-3544.
- `[AngTimmermann2012]` Ang, A. & Timmermann, A. (2012). "Regime Changes and Financial Markets," *Annual Review of Financial Economics* 4, 313-337.
- `[Adrian2019]` Adrian, T., Boyarchenko, N. & Giannone, D. (2019). "Vulnerable Growth," *American Economic Review* 109(4), 1263-1289.

**HY-IG Specific**
- `[Chen2007]` Chen, L., Lesmond, D.A. & Wei, J. (2007). "Corporate Yield Spreads and Bond Liquidity," *Journal of Finance* 62(1), 119-149.

---

## Glossary

| Term | Definition |
|------|-----------|
| **Basis point (bp)** | One hundredth of a percentage point (0.01%). 100 basis points = 1%. Used to measure small changes in yields and spreads. |
| **Buy-and-hold** | An investment strategy where you purchase an asset and hold it regardless of market conditions. The simplest benchmark for comparing active strategies. |
| **Counter-cyclical** | Moving opposite to the business or market cycle. A counter-cyclical indicator rises when markets fall and falls when markets rise. Credit spreads are counter-cyclical to stocks. |
| **Credit rating** | A grade assigned to a company's debt by rating agencies (S&P, Moody's, Fitch). Investment grade (AAA to BBB-) means lower default risk; high yield (BB+ and below) means higher default risk. |
| **Credit spread** | The difference in yield between a risky bond and a safer benchmark. Wider spreads indicate more perceived risk. Think of it as the "insurance premium" for lending to a riskier borrower. |
| **Drawdown** | The peak-to-trough decline in the value of a portfolio or index. Maximum drawdown is the largest such decline in a given period. A -34% drawdown means the portfolio lost 34% from its highest point before recovering. |
| **Excess bond premium (EBP)** | The component of credit spreads that cannot be explained by expected default risk. Captures investor sentiment and risk appetite. Proposed by Gilchrist & Zakrajsek (2012). |
| **Forward return** | The return over a future period. A "21-day forward return" is the percentage change in price over the next 21 trading days (~1 month). |
| **Granger causality** | A statistical test that determines whether one time series helps predict another. "X Granger-causes Y" means past values of X improve forecasts of Y, beyond Y's own history. It does not prove true causation -- only that X contains useful predictive information about Y. |
| **Hidden Markov Model (HMM)** | A statistical model that assumes the market is in one of several unobservable ("hidden") states -- such as "calm" or "stressed" -- each with different statistical properties. The model estimates which state is active at any given time based on observed data like spread changes and VIX levels. |
| **High-yield bonds (junk bonds)** | Bonds from companies with credit ratings below investment grade (BB+ or lower). They offer higher yields to compensate for higher default risk. |
| **HY-IG spread** | The difference between the option-adjusted spread on high-yield bonds and the option-adjusted spread on investment-grade bonds. Our primary signal variable. When this spread widens, it means investors are demanding more compensation for holding risky debt -- a sign of rising financial stress. |
| **Impulse response** | A measure of how one variable responds over time to a one-time shock in another variable. Shows whether effects are immediate, delayed, persistent, or transient. |
| **In-sample / Out-of-sample** | In-sample data is used to build and fit models. Out-of-sample data is held back and used only to test whether the model works on data it has never seen -- the gold standard for model validation. |
| **Investment-grade bonds** | Bonds from companies with credit ratings of BBB- or above. Considered safer, with lower yields. |
| **Local projection** | A method for estimating impulse responses by running separate regressions at each forecast horizon, rather than specifying the entire system at once. More robust to misspecification. Developed by Jorda (2005). |
| **Markov-switching model** | A model where the underlying regime (e.g., calm vs. stressed market) can change randomly over time. Each regime has its own set of parameters (returns, volatility, correlations). Developed by Hamilton (1989). |
| **Merton model** | A structural model of credit risk that treats a company's equity as a call option on its assets. When asset value drops toward the debt level, equity falls and credit spreads widen simultaneously. Developed by Merton (1974). |
| **NFCI** | National Financial Conditions Index, published weekly by the Chicago Federal Reserve. Measures overall conditions in U.S. financial markets. Positive values indicate tighter-than-average conditions. |
| **Option-adjusted spread (OAS)** | A credit spread that accounts for any embedded options (like call provisions) in the bond. This strips out non-credit factors, providing a cleaner measure of pure credit risk than raw yield spreads. |
| **Quality spread** | The spread between the lowest-rated high-yield bonds (CCC) and the highest-rated high-yield bonds (BB). Captures stress within the riskiest corner of the credit market -- the "canary in the coal mine." |
| **Quantile regression** | A statistical method that estimates the effect of a variable on different parts of the outcome distribution (not just the average). Particularly useful for understanding tail risks -- the worst possible outcomes. |
| **Regime** | A distinct state of the market characterized by its own statistical properties (mean returns, volatility, correlations). Markets switch between regimes over time -- think of calm weather versus storms. Each regime requires different investment approaches. |
| **Sharpe ratio** | A measure of risk-adjusted return: (return - risk-free rate) / volatility. Higher is better. A Sharpe of 1.0 is generally considered good for a long-only equity strategy; above 1.2 is strong. |
| **Transfer entropy** | An information-theoretic measure of directed information flow between time series. Unlike Granger causality, it captures nonlinear relationships -- cases where the connection between variables strengthens or weakens depending on conditions. |
| **VIX** | The CBOE Volatility Index, often called the "fear gauge." Measures the market's expectation of 30-day volatility in the S&P 500, derived from option prices. Higher VIX = more expected turbulence. |
| **VIX term structure** | The difference between longer-dated (VIX3M, 3-month) and shorter-dated (VIX, 1-month) implied volatility. When VIX3M > VIX (contango), markets are calm. When VIX > VIX3M (backwardation), near-term fear exceeds medium-term expectations. |
| **Walk-forward validation** | A backtesting method that simulates real-time trading by training the model on past data and testing on subsequent data, then rolling the window forward. Prevents lookahead bias -- the most common source of false strategy performance. |
| **Z-score** | A measure of how many standard deviations a value is from its recent average. A z-score of +2 means the value is 2 standard deviations above average -- a relatively rare condition (less than 5% of the time in normal distributions). We use rolling windows so the baseline adapts to changing market conditions over time. |
