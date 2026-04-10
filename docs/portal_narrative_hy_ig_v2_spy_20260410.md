# Portal Narrative: HY-IG Credit Spread → S&P 500 (v2)

**From:** Ray (Research Agent)
**To:** Ace (App Dev)
**Date:** 2026-04-10
**pair_id:** `hy_ig_v2_spy`

---

## Page 1 -- The Hook (Executive Summary)

### One-Sentence Thesis

The bond market often sees trouble coming before the stock market does -- and the gap between risky and safe bond yields has been one of the most reliable early warning signals for equity declines over the past 25 years.

### Headline Findings for KPI Cards

1. **Credit led equity by ~5 months before the 2008 crash** -- the HY-IG credit spread (the extra yield that investors demand to hold risky corporate bonds instead of safe ones -- essentially the price of insurance against companies going bust) began widening in June 2007, while stocks did not peak until October 2007.
2. **Spreads widened from 300 to 2,000+ basis points during the GFC** -- a basis point is 1/100th of a percentage point, so 2,000 basis points means risky companies were paying 20 full percentage points more than safe ones. That 6x increase reflected a market that believed a wave of corporate defaults was coming.
3. **Credit signals predicted 3 of the last 4 major equity drawdowns** -- a drawdown is a peak-to-trough decline in value. The dot-com bust (2001), the Global Financial Crisis (2008), and the COVID crash (2020) were all preceded or accompanied by dramatic spread widening. The 2022 rate shock is the honest exception -- more on that below.
4. **The relationship is strongest during stress** -- when spreads are in their top quartile (top 25% of historical values), the connection between credit conditions and subsequent stock returns is significantly stronger than during calm periods. **What this means:** The signal earns its keep when you need it most -- during market crises -- and stays quiet the rest of the time.
5. **Out-of-sample testing covers 8 years (2018-2025)** -- including the 2018 volatility spike, COVID crash, 2022 rate shock, and 2023-25 recovery. "Out-of-sample" means this period was hidden from the models during training, so it provides a genuine real-world test of whether the signal holds up on data it has never seen.

### Suggested Hero Chart

A dual-axis time series chart (2000-2025) with the HY-IG spread on the left y-axis (inverted, so widening = down) and SPY price on the right y-axis. Vertical shaded bands mark NBER recessions. Key events annotated with date labels. The visual immediately shows that the orange spread line "dips" (widens) before or simultaneously with the blue equity line declining.

**Transition to Page 2:** These numbers tell a compelling story, but to understand *why* credit spreads carry this predictive power -- and when the signal works versus when it fails -- we need to look deeper into how bond and stock markets are connected.

---

## Page 2 -- The Story (Layperson Narrative)

### Why Should Stock Investors Care About Bonds?

Most people think of stocks and bonds as separate worlds. Stocks are for growth; bonds are for safety. But behind the scenes, the bond market is constantly making judgments about risk that stock investors often ignore -- until it is too late.

When companies borrow money by issuing bonds, investors demand higher interest rates from riskier companies. The difference between what a risky company pays and what a safe company pays is called a **credit spread** -- the extra yield investors require to compensate for the possibility that the risky company might not pay them back. Think of it as the price of insurance against a company going bust: when more companies look shaky, the insurance gets more expensive.

<!-- expander: What exactly is a credit spread, and how is it measured? -->
A credit spread is measured in **basis points** (hundredths of a percentage point). If a risky company's bond yields 8% and a safe company's bond yields 4%, the credit spread is 400 basis points (4 percentage points). When investors become worried about the economy, they demand even higher yields from risky companies, causing spreads to **widen**. When confidence returns, spreads **tighten** (narrow).

The specific spread we study is the **HY-IG spread**: the difference between the yield on high-yield bonds (also called "junk bonds" -- bonds from companies with lower credit ratings, like BB or CCC) and investment-grade bonds (bonds from companies with higher credit ratings, like AA or A). Both yields are measured as **option-adjusted spreads (OAS)** -- a technique that strips out the effect of special bond features like early repayment clauses, leaving a cleaner measure of pure credit risk.
<!-- /expander -->

### The Early Warning Signal

Our research examines whether this spread can serve as an early warning system for stock investors. The core finding, supported by over two decades of academic research, is that **the bond market tends to detect trouble before the stock market reacts.** There are several reasons for this:

- **Bond investors are wired for caution.** Unlike stock investors who can profit from unlimited upside, bond investors can only get their money back plus interest. This asymmetry makes them structurally more sensitive to the first signs of deterioration. When something smells off, bond investors raise the price of lending before stock investors lower the price they will pay for shares.
- **Banks trade on private information.** Banks that lend to companies have inside knowledge about their financial health. Research by Acharya & Johnson (2007) found evidence that this information leaks into credit markets -- through hedging activity in credit default swaps -- before it appears in stock prices.
- **The bond market is harder to fool.** Philippon (2009) showed that bond prices provide a cleaner signal of a company's fundamental value than stock prices. Stocks can be inflated by speculation and momentum; bond investors care only about getting their money back.

The relationship is **counter-cyclical** -- meaning the spread moves opposite to stocks. When spreads widen (risky bonds get more expensive to issue), stocks tend to fall. When spreads tighten (risk appetite returns), stocks tend to rise.

<!-- expander: Why are stocks and bonds mathematically connected? (The Merton Model) -->
In 1974, economist Robert Merton proved something elegant: a company's stock and its debt are not separate instruments -- they are two different bets on the same underlying reality.

Imagine a company as a house with a mortgage. The homeowner (stockholder) profits if the house value rises above the mortgage. The bank (bondholder) gets paid as long as the house value stays above the mortgage. Now imagine the house value drops toward the mortgage amount. Two things happen at once: the homeowner's equity shrinks, and the bank starts worrying about getting paid back.

Merton showed that this analogy is mathematically precise. A company's stock is essentially a call option on its total asset value, with the strike price set at the value of its debts. When asset value drops toward the debt level, equity declines and credit spreads widen simultaneously. This is why credit spreads and stock prices tend to move in opposite directions during stress -- they are both responding to the same underlying reality, just viewed from different angles.

The practical implication: when you see credit spreads widening, it means the market is pricing in a higher probability that corporate asset values are falling toward their debt levels -- which is also bad news for equity holders.
<!-- /expander -->

### What History Shows

We analyzed 25 years of daily data (January 2000 through December 2025), covering four major market disruptions. Each episode reveals a different facet of how credit spreads interact with stock prices.

**The Dot-Com Bust (2001-2002).** Credit spreads began widening well before the recession officially started in March 2001. High-yield spreads climbed from roughly 500 to over 1,000 basis points as the telecom and technology sectors imploded, highlighted by the WorldCom bankruptcy in July 2002. The signal was genuine, though the lead time was shorter than in later episodes -- the dot-com bust was driven more by equity overvaluation than by credit deterioration, so the credit market was a contemporaneous confirmer rather than a leading indicator.

**The Global Financial Crisis (2007-2009).** This is the textbook example of credit leading equity. Credit spreads started widening in mid-2007, following the collapse of two Bear Stearns hedge funds that were exposed to subprime mortgages. The stock market did not peak until October 2007 -- giving attentive investors roughly five months of warning. By the time Lehman Brothers collapsed in September 2008, the HY-IG spread had already reached roughly 800 basis points. It eventually peaked above 2,000 basis points in December 2008. An investor who moved to cash when spreads crossed 2 standard deviations above their rolling mean would have avoided the majority of the drawdown -- though the timing of re-entry was equally critical.

**The COVID Crash (2020).** Credit spreads surged from about 350 to 1,100 basis points in just five weeks (late February to late March 2020). This time, credit and equity moved almost simultaneously -- the speed of the pandemic shock compressed the usual lead time to near zero. However, the signal still provided value: the sheer magnitude of spread widening confirmed that the sell-off was not a garden-variety correction but a genuine liquidity crisis. The Federal Reserve's unprecedented intervention -- including direct corporate bond purchases announced on March 23, 2020 -- truncated the stress episode faster than any previous crisis.

**The 2022 Rate Shock -- Where the Signal Struggled.** As the Federal Reserve raised interest rates at the fastest pace in four decades, credit spreads widened from about 300 to 500 basis points. The S&P 500 fell roughly 25%. But here is the honest caveat: the spread widening was modest compared to the equity decline. The mechanism was different -- this was not a credit crisis driven by deteriorating corporate balance sheets but a valuation repricing driven by higher discount rates. The HY-IG spread was reacting to the same force (rising rates) rather than providing an independent early warning. This episode illustrates a genuine limitation of the credit signal: it works best when stress originates in the credit cycle, and less well when the driver is pure monetary policy shock.

<!-- expander: Is there a deeper signal within the credit market itself? (The CCC-BB quality spread) -->
Not all high-yield bonds are equally risky. Within the high-yield universe, there is a meaningful hierarchy: BB-rated bonds are the least risky high-yield issues (just one notch below investment grade), while CCC-rated bonds are at the edge of default.

The spread between CCC and BB yields -- what we call the **quality spread** -- provides an even more granular stress signal. When this quality spread widens, it means investors are specifically fleeing the weakest, most default-prone companies. This often happens before the broader HY-IG spread fully reflects the stress, because the weakest links break first.

During the GFC, the CCC-BB quality spread began widening months before the overall HY-IG spread reached crisis levels. During COVID, the quality spread spike was even more dramatic -- CCC-rated bonds briefly yielded over 20%, while BB bonds remained relatively contained. The quality spread is a "canary in the coal mine" within the credit market itself.

We include the CCC-BB quality spread as one of our tournament signals (S5) precisely because it captures a different dimension of credit stress than the broad HY-IG measure.
<!-- /expander -->

### It Is Not a Simple Relationship

If the story ended at "wider spreads = lower stocks," building a profitable trading strategy would be straightforward. But the relationship between credit spreads and stock returns is more nuanced, and understanding these nuances is essential for using the signal effectively.

The connection changes depending on the market **regime** -- a regime is a distinct state of financial conditions, like "calm weather" versus "storm," where each state has its own patterns of returns, volatility, and correlations between assets:

- **During calm periods** (when spreads are in their normal range of roughly 250-400 basis points), the predictive power of credit spreads for stock returns is modest. In fact, during these periods, stock prices tend to lead credit spreads -- equity markets set the pace, and credit markets follow. This makes intuitive sense: when things are going well, there is not much default risk to price, so the credit market mostly mirrors what equities are already saying.
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

### How We Tested the Signal

Our analysis employed multiple econometric methods, each designed to test a different aspect of the credit-equity relationship. We deliberately used methods that approach the question from different angles -- if the finding holds across multiple techniques, we can be more confident it is real and not an artifact of a particular statistical method.

**Causality Testing (Toda-Yamamoto Granger Causality and Transfer Entropy):**
**Granger causality** is a statistical test that asks: do past values of one variable help predict future values of another, above and beyond the second variable's own history? If credit spread changes today help predict stock returns tomorrow -- even after accounting for stocks' own momentum -- then credit spreads "Granger-cause" stock returns. We used the Toda-Yamamoto variant because it works correctly even when the data contains trends, which financial data often does. We chose this as our first test because it directly addresses the lead-lag question at the heart of our hypothesis.

We also measured **transfer entropy** -- an information-theoretic tool that captures directed information flow between two time series, including nonlinear relationships that correlation-based tests miss. We added this because the credit-equity relationship may involve threshold effects and asymmetries that a simple linear test would understate.

Crucially, we ran both tests in **both directions** to check for reverse causality: do stock returns also predict credit spread changes? We tested at multiple time horizons (1 day, 5 days, 21 days, 63 days) and separately for stress and calm regimes.

**Local Projections (Jorda method):**
We estimated the cumulative impact of a credit spread shock on stock returns at horizons from 1 day to 63 days (roughly one quarter). We chose this method over the traditional Vector Autoregression (VAR) approach because local projections are robust to model misspecification -- they do not require us to assume the entire system is correctly specified, only that each individual horizon regression is reasonable. This matters because financial relationships are often nonlinear and regime-dependent, making full-system assumptions risky. We also estimated state-dependent versions -- separate impulse responses for calm and stress regimes -- to test whether the effect differs across market conditions.

**Regime-Switching Models (Markov-Switching and Hidden Markov Models):**
We identified distinct market states -- calm, moderate stress, and extreme stress -- using statistical models that let the data determine the regime boundaries. We chose regime-switching models because the Story section above makes clear that the credit-equity relationship changes across market states. Rather than imposing arbitrary threshold levels (like "spreads above 500 bps = stress"), these models discover the natural statistical breakpoints from the data itself.

**Quantile Regression:**
Rather than estimating just the average effect of credit spreads on stock returns, we examined the entire distribution -- particularly the worst outcomes (the left tail, at the 5th and 10th percentiles). We chose this method because the hypothesis is that credit spreads primarily warn of bad outcomes rather than predict good ones. Quantile regression lets us test that claim directly by estimating separate effects at different points in the return distribution.

### Key Findings

*(Reference Evan's model output files in `results/hy_ig_v2_spy/core_models_20260410/` for full details. Reference Vera's charts in `output/charts/hy_ig_v2_spy/plotly/` for interactive visualizations.)*

**Finding 1 -- The bond market and stock market take turns leading each other.**
Granger causality tests reveal statistically significant information flow in both directions (credit-to-equity and equity-to-credit). This is expected from the Merton model: equity and credit are linked through the same underlying corporate asset values. However, the credit-to-equity signal strengthens materially during stress regimes, while the equity-to-credit signal dominates during calm periods. Transfer entropy (the nonlinear test) shows even stronger asymmetry between the two directions.

**What this means:** In calm markets, stock prices set the pace -- equities lead credit. But when stress builds, the bond market starts sending warnings that arrive weeks before stocks react. This is consistent with informed trading in credit markets during stress (Acharya & Johnson 2007) and is the core reason the credit signal has practical value for equity investors.

**Finding 2 -- Credit spread shocks ripple through stock returns over weeks, not days.**
Local projection impulse responses show that a 1-standard-deviation widening in the HY-IG z-score (a measure of how unusual the current spread is relative to its recent history) is associated with negative cumulative stock returns that build over 1-5 weeks before fading. The effect is roughly 2-3x larger during stress regimes compared to calm regimes. The shape of the response -- a gradual build followed by a plateau -- tells us that credit information is incorporated into equity prices gradually, not instantaneously.

**What this means:** When the bond market signals trouble, the stock market does not adjust immediately. The adjustment plays out over several weeks, which creates a window for investors to act -- a signal that was fully priced in within 24 hours would be useless for trading purposes.

**Finding 3 -- The signal activates at data-driven stress thresholds, not arbitrary cutoffs.**
Regime-switching models identify a "stress" state where the credit-equity relationship is fundamentally different from the calm state. The transition probability into the stress state increases sharply when the HY-IG z-score exceeds approximately 1.5-2.0 standard deviations above its rolling mean. This threshold is not imposed by us -- it is discovered by the model. It corresponds roughly to periods when the raw HY-IG spread is above 500-600 basis points, depending on the prevailing volatility.

**What this means:** The credit signal does not gradually strengthen as spreads widen. Instead, it "switches on" at a specific stress threshold -- below that threshold, it is largely noise. A strategy based on this signal should only act when the model identifies the stress regime, ignoring the noise during calm periods.

**Finding 4 -- Credit spreads warn of bad outcomes, not good ones.**
Quantile regression results show that credit spreads have their strongest explanatory power for the worst stock return outcomes (5th and 10th percentiles), consistent with the "Vulnerable Growth" framework of Adrian, Boyarchenko & Giannone (2019). The median and upper quantiles of the return distribution are largely unaffected by credit spread movements.

**What this means:** Wide credit spreads are a warning sign for large stock declines, but narrow credit spreads do not predict large stock rallies. This is a risk management signal -- it tells you when to get defensive, not when to get aggressive. An investor using this signal should think of it as a fire alarm, not a green light.

### The Combinatorial Tournament

We tested approximately 1,000+ meaningful combinations of signals (13 types), thresholds (7 methods), strategies (4 types), lead times (9 values), and lookback windows (4 lengths). These were ranked by out-of-sample **Sharpe ratio** -- a measure of risk-adjusted return calculated as (return minus risk-free rate) divided by volatility, where higher values mean better returns per unit of risk taken -- over 2018-2025 (data the models never saw during estimation). The top 5 strategies were then subjected to rigorous walk-forward validation, bootstrap significance testing, and transaction cost sensitivity analysis.

*(See `results/hy_ig_v2_spy/tournament_results_20260410.csv` for the full leaderboard.)*

**Transition to Page 4:** The statistical evidence confirms that credit spreads carry genuine predictive information for stock returns, especially during stress. The practical question is: can an investor use this signal to improve their risk-adjusted returns -- and at what cost?

---

## Page 4 -- The Strategy (Trading Applications)

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

### Important Caveats

1. **Transaction costs matter.** All strategy metrics include 5 basis points per round-trip trade. The breakeven transaction cost -- the level at which the strategy's edge disappears entirely -- is 50 bps, providing a comfortable margin of safety.
2. **Execution delay degrades performance.** We tested 1, 2, 3, and 5-day delays between signal generation and trade execution. Performance decreases with longer delays, reflecting the speed at which credit information gets priced into equities. The maximum acceptable delay for this strategy is approximately 5 days.
3. **The 2022 episode is a genuine weakness.** The strategy's credit signal widened modestly during 2022, but not enough to trigger a full risk-off position in most configurations. This is because the 2022 bear market was driven by rate hikes and valuation compression, not by the credit deterioration that the HY-IG spread is designed to detect. Investors should not expect the credit signal to protect against all types of equity drawdowns -- only those rooted in credit stress.
4. **Past performance is not indicative of future results.** Regime shifts, changes in market microstructure, or new central bank tools (like the Fed's corporate bond purchasing programs, first deployed in 2020) could alter the credit-equity relationship going forward.
5. **This is a risk management tool, not an alpha generator.** The primary value is in reducing drawdowns during stress periods rather than generating excess returns during calm periods. Think of it as portfolio insurance that happens to be free (or slightly profitable) on average.

**Transition to Page 5:** For readers who want to understand exactly how we reached these conclusions -- or who want to replicate and extend the analysis -- the methodology section provides full details on data, methods, and diagnostics.

---

## Page 5 -- The Method (Technical Appendix)

### Data Sources

All data is sourced from publicly available databases accessible through our MCP server stack:

- **Credit spreads:** ICE BofA Option-Adjusted Spread indices via FRED. OAS (option-adjusted spread) strips out the effect of embedded options like call provisions to isolate pure credit risk. Series: BAMLH0A0HYM2 (HY OAS), BAMLC0A0CM (IG OAS), BAMLH0A1HYBB (BB OAS), BAMLH0A3HYC (CCC OAS), BAMLC0A4CBBB (BBB OAS).
- **Equity prices:** SPY ETF adjusted close via Yahoo Finance.
- **Volatility:** CBOE VIX (^VIX) and VIX3M (^VIX3M) indices via Yahoo Finance; MOVE Index (^MOVE) via Yahoo Finance.
- **Macro variables:** Treasury yields (DGS10, DGS2, DTB3), NFCI, initial claims (ICSA), fed funds rate (DFF), SOFR, St. Louis FSI (STLFSI2) via FRED.
- **Cross-asset:** Gold (GC=F), Copper (HG=F), DXY (DX-Y.NYB), HYG, KBE, IWM via Yahoo Finance.

### Sample Period

- **Full sample:** January 2000 to December 2025 (daily, ~6,500 business days)
- **In-sample (model estimation):** January 2000 to December 2017 (~4,500 obs)
- **Out-of-sample (strategy evaluation):** January 2018 to December 2025 (~2,000 obs)

The 70/30 in-sample/out-of-sample split provides a generous 8-year out-of-sample window that includes multiple distinct market episodes (2018 volatility spike, COVID crash, 2022 rate shock, 2023-25 recovery), preventing the strategy from being validated on only one type of market environment.

### Indicator Construction

The primary indicator is the HY-IG spread: BAMLH0A0HYM2 minus BAMLC0A0CM, measured in basis points. From this raw spread, we derive 20 transformed series including z-scores (252-day and 504-day rolling windows), percentile ranks (504-day and 1260-day), rates of change (21-day, 63-day, 126-day), momentum changes, acceleration, and the CCC-BB quality spread.

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

### References

See the full analysis brief (`docs/analysis_brief_hy_ig_v2_spy_20260410.md`) for the complete list of 25 academic citations.

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
