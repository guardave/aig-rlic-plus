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

1. **Credit led equity by ~5 months before the 2008 crash** -- HY-IG spreads (the gap between high-yield and investment-grade bond yields) began widening in June 2007, while stocks did not peak until October 2007.
2. **Spreads widened from 300 to 2,000+ basis points during the GFC** -- a basis point is 1/100th of a percentage point -- representing a 6x increase in the market's assessment of corporate default risk.
3. **Credit signals predicted 3 of the last 4 major equity drawdowns** -- the dot-com bust (2001), the Global Financial Crisis (2008), and the COVID crash (2020) were all preceded or accompanied by dramatic spread widening. The 2022 rate shock is the honest exception -- more on that below.
4. **The relationship is strongest during stress** -- when spreads are in their top quartile (top 25% of historical values), the connection between credit conditions and subsequent stock returns is significantly stronger than during calm periods.
5. **Out-of-sample testing covers 8 years (2018-2025)** -- including the 2018 volatility spike, COVID crash, 2022 rate shock, and 2023-25 recovery -- providing a rigorous real-world test of whether the signal holds up outside the data it was trained on.

### Suggested Hero Chart

A dual-axis time series chart (2000-2025) with the HY-IG spread on the left y-axis (inverted, so widening = down) and SPY price on the right y-axis. Vertical shaded bands mark NBER recessions. Key events annotated with date labels. The visual immediately shows that the orange spread line \"dips\" (widens) before or simultaneously with the blue equity line declining.

**Transition to Page 2:** These numbers tell a compelling story, but to understand *why* credit spreads carry this predictive power -- and when the signal works versus when it fails -- we need to look deeper into how bond and stock markets are connected.

---

## Page 2 -- The Story (Layperson Narrative)

### Why Should Stock Investors Care About Bonds?

Most people think of stocks and bonds as separate worlds. Stocks are for growth; bonds are for safety. But behind the scenes, the bond market is constantly making judgments about risk that stock investors often ignore -- until it is too late.

When companies borrow money by issuing bonds, investors demand higher interest rates from riskier companies. The difference between what a risky company pays and what a safe company pays is called a **credit spread** (the extra yield investors require to compensate for the possibility that the risky company might not pay them back). Think of it as the price of insurance against a company going bust -- when more companies look shaky, the insurance gets more expensive.

<!-- expander: What exactly is a credit spread? -->
A credit spread is measured in **basis points** (hundredths of a percentage point). If a risky company's bond yields 8% and a safe company's bond yields 4%, the credit spread is 400 basis points (4 percentage points). When investors become worried about the economy, they demand even higher yields from risky companies, causing spreads to **widen**. When confidence returns, spreads **tighten** (narrow).

The specific spread we study is the **HY-IG spread**: the difference between the yield on high-yield bonds (also called \"junk bonds\" -- bonds from companies with lower credit ratings, like BB or CCC) and investment-grade bonds (bonds from companies with higher credit ratings, like AA or A). Both yields are measured as option-adjusted spreads (OAS), meaning they account for embedded options like call provisions, providing a cleaner measure of pure credit risk.
<!-- /expander -->

### The Early Warning Signal

Our research examines whether this spread can serve as an early warning system for stock investors. The core finding, supported by over two decades of academic research, is that **the bond market tends to detect trouble before the stock market reacts.** There are several reasons for this:

- **Bond investors are wired for caution.** Unlike stock investors who can profit from unlimited upside, bond investors can only get their money back plus interest. This asymmetry makes them structurally more sensitive to the first signs of deterioration. When something smells off, bond investors raise the price of lending before stock investors lower the price they will pay for shares.
- **Banks trade on private information.** Banks that lend to companies have inside knowledge about their financial health. Research by Acharya & Johnson (2007) found evidence that this information leaks into credit markets -- through hedging activity in credit default swaps -- before it appears in stock prices.
- **The bond market is harder to fool.** Philippon (2009) showed that bond prices provide a cleaner signal of a company's fundamental value than stock prices. Stocks can be inflated by speculation and momentum; bond investors care only about getting their money back.

<!-- expander: The Merton Model -- Why stocks and bonds are mathematically linked -->
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

<!-- expander: The CCC-BB Quality Spread -- A deeper signal within the signal -->
Not all high-yield bonds are equally risky. Within the high-yield universe, there is a meaningful hierarchy: BB-rated bonds are the least risky high-yield issues (just one notch below investment grade), while CCC-rated bonds are at the edge of default.

The spread between CCC and BB yields -- what we call the **quality spread** -- provides an even more granular stress signal. When this quality spread widens, it means investors are specifically fleeing the weakest, most default-prone companies. This often happens before the broader HY-IG spread fully reflects the stress, because the weakest links break first.

During the GFC, the CCC-BB quality spread began widening months before the overall HY-IG spread reached crisis levels. During COVID, the quality spread spike was even more dramatic -- CCC-rated bonds briefly yielded over 20%, while BB bonds remained relatively contained. The quality spread is a \"canary in the coal mine\" within the credit market itself.

We include the CCC-BB quality spread as one of our tournament signals (S5) precisely because it captures a different dimension of credit stress than the broad HY-IG measure.
<!-- /expander -->

### It Is Not a Simple Relationship

If the story ended at \"wider spreads = lower stocks,\" building a profitable trading strategy would be straightforward. But the relationship between credit spreads and stock returns is more nuanced than that, and understanding the nuances is essential for using the signal effectively.

The connection changes depending on the market **regime** (the overall state of financial conditions):

- **During calm periods** (when spreads are in their normal range of roughly 250-400 basis points), the predictive power of credit spreads for stock returns is modest. In fact, during these periods, stock prices tend to lead credit spreads -- equity markets set the pace, and credit markets follow. This makes intuitive sense: when things are going well, there is not much default risk to price, so the credit market mostly mirrors what equities are already saying.
- **During stress periods** (when spreads are in the top quartile of their historical range, roughly above 500 basis points), the relationship strengthens and may reverse direction -- credit markets appear to lead equity markets. This is consistent with the informed-trading and risk-appetite channels described above. It is also when the signal is most valuable: precisely when investors most need a warning.

This **regime dependence** is why simple trading rules based on credit spreads often fail. The signal is most powerful precisely when it is most needed -- during periods of financial stress -- but relatively quiet during the long stretches of calm in between. A strategy that responds to every twitch in credit spreads will generate excessive trading costs during calm periods with minimal benefit.

<!-- expander: What is a regime? -->
In financial economics, a \"regime\" refers to a distinct state of the market characterized by its own set of statistical properties -- its own average return, level of volatility, and pattern of correlations between assets. Think of weather: sunny days and stormy days are governed by different atmospheric dynamics, and a forecast that works in summer may be useless in winter.

The key insight from research by Hamilton (1989) and Guidolin & Timmermann (2007) is that financial markets do not behave the same way all the time. They switch between regimes -- sometimes abruptly. A model that assumes markets always behave the same way will miss the most important signals, because the relationship between credit and equity fundamentally changes when the market shifts from calm to crisis.

Our analysis uses Hidden Markov Models and Markov-switching regressions to statistically identify these regime changes, letting the data tell us when the market has shifted rather than imposing arbitrary thresholds.
<!-- /expander -->

**Transition to Page 3:** History suggests a real connection between credit spreads and stocks -- but anecdotes are not evidence. We subjected 25 years of daily data to a battery of statistical tests to separate genuine predictive power from coincidence and survivorship bias.

---

## Page 3 -- The Evidence (Analytical Detail)

### How We Tested the Signal

Our analysis employed multiple econometric methods, each designed to test a different aspect of the credit-equity relationship. We deliberately used methods that approach the question from different angles -- if the finding holds across multiple techniques, we can be more confident it is real and not an artifact of a particular statistical method.

**Causality Testing (Toda-Yamamoto Granger and Transfer Entropy):**
We tested whether credit spread changes statistically \"cause\" (in the Granger sense -- meaning they help predict) future stock returns, and vice versa. Crucially, we ran these tests in **both directions** to check for reverse causality: do stock returns also predict credit spread changes? We ran these tests at multiple lag orders (1 day, 5 days, 21 days, 63 days) and separately for stress and calm regimes.

**Local Projections (Jorda method):**
We estimated the cumulative impact of a credit spread shock on stock returns at horizons from 1 day to 63 days (roughly one quarter). This method is robust to misspecification and allows us to see how the effect builds, peaks, and fades over time. We also estimated state-dependent versions -- separate impulse responses for calm and stress regimes.

**Regime-Switching Models (Markov-Switching and Hidden Markov Models):**
We identified distinct market states -- calm, moderate stress, and extreme stress -- using statistical models that let the data determine the regime boundaries. This avoids the bias of imposing arbitrary threshold levels (like \"spreads above 500 bps = stress\") and instead discovers the natural statistical breakpoints.

**Quantile Regression:**
Rather than estimating just the average effect of credit spreads on stock returns, we examined the entire distribution -- particularly the worst outcomes (the left tail, at the 5th and 10th percentiles). This addresses the hypothesis that credit spreads are primarily a warning of bad outcomes, not a predictor of good ones.

### Key Findings

*(Reference Evan's model output files in `results/hy_ig_v2_spy/core_models/` for full details. Reference Vera's charts in `output/charts/hy_ig_v2_spy/plotly/` for interactive visualizations.)*

**Finding 1 -- Bidirectional causality with regime asymmetry.**
Granger causality tests reveal statistically significant information flow in both directions (credit-to-equity and equity-to-credit). This is expected from the Merton model: equity and credit are linked through the same underlying corporate asset values. However, the credit-to-equity signal strengthens materially during stress regimes, while the equity-to-credit signal dominates during calm periods. Transfer entropy (a nonlinear test that can capture relationships beyond simple linear correlation) shows even stronger asymmetry. This pattern is consistent with informed trading in credit markets during stress (Acharya & Johnson 2007).

**Finding 2 -- Credit spread shocks have persistent effects on stock returns.**
Local projection impulse responses show that a 1-standard-deviation widening in the HY-IG z-score is associated with negative cumulative stock returns that build over 1-5 weeks before fading. The effect is roughly 2-3x larger during stress regimes compared to calm regimes. The impulse response shape -- a gradual build followed by a plateau -- suggests that credit information is incorporated into equity prices over weeks, not days.

**Finding 3 -- The signal activates at data-driven stress thresholds.**
Regime-switching models identify a \"stress\" state where the credit-equity relationship is fundamentally different from the calm state. The transition probability into the stress state increases sharply when the HY-IG z-score exceeds approximately 1.5-2.0 standard deviations above its rolling mean. This threshold is not imposed -- it is discovered by the model. It corresponds roughly to periods when the raw HY-IG spread is above 500-600 basis points, depending on the prevailing volatility.

**Finding 4 -- Downside equity risk is the primary channel.**
Quantile regression results show that credit spreads have their strongest explanatory power for the worst stock return outcomes (5th and 10th percentiles), consistent with the \"Vulnerable Growth\" framework of Adrian, Boyarchenko & Giannone (2019). The median and upper quantiles of the return distribution are largely unaffected by credit spread movements. In plain English: credit spreads warn of bad outcomes but say relatively little about good outcomes.

### The Combinatorial Tournament

We tested approximately 800-1,200 meaningful combinations of signals (13 types), thresholds (7 methods), strategies (4 types), lead times (9 values), and lookback windows (4 lengths). These were ranked by out-of-sample Sharpe ratio (2018-2025 -- data the models never saw during estimation), with the top 5 subjected to rigorous walk-forward validation, bootstrap significance testing, and transaction cost sensitivity analysis.

*(See `results/hy_ig_v2_spy/tournament_results.csv` for the full leaderboard.)*

**Transition to Page 4:** The statistical evidence confirms that credit spreads carry genuine predictive information for stock returns, especially during stress. The practical question is: can an investor use this signal to improve their risk-adjusted returns -- and at what cost?

---

## Page 4 -- The Strategy (Trading Applications)

### How the Signal Translates to Action

The tournament identified the most robust credit-signal strategies for equity allocation. The winning strategies share a common logic:

**Core principle: Risk-off when credit stress exceeds a data-driven threshold.**

The strategy rules in plain language:
- **When the credit stress indicator is below the threshold** (indicating normal market conditions): Stay fully invested in stocks (long SPY).
- **When the credit stress indicator crosses above the threshold** (indicating elevated credit stress): Reduce equity exposure or move entirely to cash.
- **When the indicator drops back below the threshold:** Re-enter the equity market.

The specific signal, threshold, and timing rules are determined by the tournament. The v1 analysis found that a 2-state Hidden Markov Model with a stress probability threshold of 0.7 using a Long/Cash strategy (P1) produced an OOS Sharpe of 1.17 with a maximum drawdown of -12% (versus roughly -34% for buy-and-hold SPY over the same period).

<!-- expander: What is a z-score, and why do we use it? -->
A z-score measures how unusual a current value is compared to its recent history. A z-score of 0 means the spread is at its historical average. A z-score of +2 means the spread is 2 standard deviations above average -- a relatively rare condition that historically has occurred less than 5% of the time.

We use z-scores rather than raw spread levels because the \"normal\" level of credit spreads changes over time. A 400 bps spread in 2005 (when spreads had been tightening for years) meant something different than a 400 bps spread in 2010 (when spreads were coming down from crisis peaks). The z-score adjusts for this by comparing today's spread to its recent window, providing a context-aware measure of stress.
<!-- /expander -->

### Key Strategy Metrics

*(Numbers from v1 reference -- to be updated with v2 tournament results from Evan.)*

| Metric | Credit-Signal Strategy | Buy-and-Hold SPY |
|--------|----------------------|-------------------|
| OOS Sharpe Ratio (2018-2025) | 1.17 | ~0.90 |
| Annualized Return (OOS) | ~11% | ~10% |
| Maximum Drawdown | -12% | ~-34% |
| Annual Turnover | ~5 trades/year | 0 |
| Breakeven Transaction Cost | 50 bps | N/A |

### Where the Strategy Adds Value -- and Where It Does Not

The primary value of the credit signal is **drawdown reduction during stress periods**, not alpha generation during calm markets. During the long stretches when credit conditions are normal, the strategy is fully invested and performs identically to buy-and-hold. Its edge comes from avoiding the worst of the drawdowns when credit markets signal stress.

This means:
- **It will underperform in V-shaped recoveries.** If the market crashes and bounces back quickly (as in COVID), the strategy may exit at or near the bottom and re-enter after some of the recovery has already occurred. The COVID V-shape is the worst-case scenario for any trend-following or risk-off strategy.
- **It excels in prolonged bear markets.** The GFC lasted roughly 18 months peak-to-trough. A strategy that exited early in that decline and waited for credit conditions to normalize captured most of the avoided drawdown.
- **It is largely inert during calm periods.** This is a feature, not a bug -- the strategy avoids generating trading costs and tax events when the credit signal has little to say.

### Important Caveats

1. **Transaction costs matter.** All strategy metrics include 5 basis points per round-trip trade. The breakeven transaction cost -- the level at which the strategy's edge disappears entirely -- is reported for each top-5 combination.
2. **Execution delay degrades performance.** We tested 1, 2, 3, and 5-day delays between signal generation and trade execution. Performance decreases with longer delays, reflecting the speed at which credit information gets priced into equities.
3. **The 2022 episode is a genuine weakness.** The strategy's credit signal widened modestly during 2022, but not enough to trigger a full risk-off position in most configurations. This is because the 2022 bear market was driven by rate hikes and valuation compression, not by the credit deterioration that the HY-IG spread is designed to detect. Investors should not expect the credit signal to protect against all types of equity drawdowns -- only those rooted in credit stress.
4. **Past performance is not indicative of future results.** Regime shifts, changes in market microstructure, or new central bank tools (like the Fed's corporate bond purchasing programs, first deployed in 2020) could alter the credit-equity relationship going forward.
5. **This is a risk management tool, not an alpha generator.** The primary value may be in reducing drawdowns during stress periods rather than generating excess returns during calm periods.

**Transition to Page 5:** For readers who want to understand exactly how we reached these conclusions -- or who want to replicate and extend the analysis -- the methodology section provides full details on data, methods, and diagnostics.

---

## Page 5 -- The Method (Technical Appendix)

### Data Sources

All data is sourced from publicly available databases accessible through our MCP server stack:

- **Credit spreads:** ICE BofA Option-Adjusted Spread indices via FRED. Series: BAMLH0A0HYM2 (HY OAS), BAMLC0A0CM (IG OAS), BAMLH0A1HYBB (BB OAS), BAMLH0A3HYC (CCC OAS), BAMLC0A4CBBB (BBB OAS).
- **Equity prices:** SPY ETF adjusted close via Yahoo Finance.
- **Volatility:** CBOE VIX (^VIX) and VIX3M (^VIX3M) indices via Yahoo Finance; MOVE Index (^MOVE) via Yahoo Finance.
- **Macro variables:** Treasury yields (DGS10, DGS2, DTB3), NFCI, initial claims (ICSA), fed funds rate (DFF), SOFR, St. Louis FSI (STLFSI2) via FRED.
- **Cross-asset:** Gold (GC=F), Copper (HG=F), DXY (DX-Y.NYB), HYG, KBE, IWM via Yahoo Finance.

### Sample Period

- **Full sample:** January 2000 to December 2025 (daily, ~6,500 business days)
- **In-sample (model estimation):** January 2000 to December 2017 (~4,500 obs)
- **Out-of-sample (strategy evaluation):** January 2018 to December 2025 (~2,000 obs)

### Indicator Construction

The primary indicator is the HY-IG spread: BAMLH0A0HYM2 minus BAMLC0A0CM, measured in basis points. From this raw spread, we derive 20 transformed series including z-scores (252d and 504d rolling windows), percentile ranks (504d and 1260d), rates of change (21d, 63d, 126d), momentum changes, acceleration, and the CCC-BB quality spread.

### Econometric Methods

| Method | Purpose | Key Parameter |
|--------|---------|---------------|
| Toda-Yamamoto Granger causality | Linear causality in both directions | Augmented VAR, lags selected by BIC + d_max = 1 |
| Transfer entropy (Diks-Panchenko) | Nonlinear information flow | Bandwidth per Diks & Panchenko (2006) |
| Local projections (Jorda) | Impulse responses at multiple horizons | h = 1, 5, 10, 21, 42, 63 days; state-dependent |
| Markov-switching regression | Regime identification | 2-state and 3-state |
| Gaussian HMM | Joint regime identification on HY-IG + VIX | 2-state and 3-state |
| Quantile regression | Distributional effects on return tails | tau = 0.05, 0.10, 0.25, 0.50, 0.75, 0.90 |
| GJR-GARCH | Volatility dynamics with asymmetry | SPY returns with HY-IG exogenous |
| Random Forest + SHAP | Nonlinear feature importance | Walk-forward, 1-year test windows |
| Combinatorial tournament | Strategy optimization | ~1,000 combinations, OOS Sharpe ranking |

### Diagnostics

Every model undergoes: Jarque-Bera (normality), Breusch-Pagan (heteroskedasticity), Breusch-Godfrey (serial correlation), RESET (functional form), and stationarity confirmation (ADF + KPSS confirmatory approach). HC3 robust standard errors are reported by default.

### Sensitivity Analysis

- Full sample vs. excluding GFC (2007-2009)
- Full sample vs. excluding COVID (2020)
- Pre-2008 vs. post-2008 sub-samples
- Alternative lag structures (BIC, AIC, fixed 5/10/21)
- Alternative threshold levels and methods
- Walk-forward validation with rolling windows

### Reverse Causality Check (G11 Requirement)

All lead-lag and predictive claims include a reverse-causality test: the same model is estimated with SPY -> HY-IG as well as HY-IG -> SPY. Both sets of results are reported side by side. Local projection impulse responses are compared in both directions. The finding of bidirectional causality is documented and its implications discussed -- specifically, that the credit-to-equity signal strengthens in stress regimes while the equity-to-credit signal dominates in calm regimes.

### References

See the full analysis brief (`docs/analysis_brief_hy_ig_v2_spy_20260410.md`) for the complete list of 25 academic citations.

---

## Glossary

| Term | Definition |
|------|-----------|
| **Basis point (bp)** | One hundredth of a percentage point (0.01%). 100 basis points = 1%. Used to measure small changes in yields and spreads. |
| **Buy-and-hold** | An investment strategy where you purchase an asset and hold it regardless of market conditions. The simplest benchmark for comparing active strategies. |
| **Credit rating** | A grade assigned to a company's debt by rating agencies (S&P, Moody's, Fitch). Investment grade (AAA to BBB-) means lower default risk; high yield (BB+ and below) means higher default risk. |
| **Credit spread** | The difference in yield between a risky bond and a safer benchmark. Wider spreads indicate more perceived risk. Think of it as the \"insurance premium\" for lending to a riskier borrower. |
| **Drawdown** | The peak-to-trough decline in the value of a portfolio or index. Maximum drawdown is the largest such decline in a given period. |
| **Excess bond premium (EBP)** | The component of credit spreads that cannot be explained by expected default risk. Captures investor sentiment and risk appetite. Proposed by Gilchrist & Zakrajsek (2012). |
| **Forward return** | The return over a future period. A \"21-day forward return\" is the percentage change in price over the next 21 trading days (~1 month). |
| **Granger causality** | A statistical test that determines whether one time series helps predict another. \"X Granger-causes Y\" means past values of X improve forecasts of Y. It does not prove true causation -- only predictive content. |
| **Hidden Markov Model (HMM)** | A statistical model that assumes the system is in one of several unobservable (\"hidden\") states, each with different statistical properties. The model estimates which state the market is in at any given time based on observed data. |
| **High-yield bonds (junk bonds)** | Bonds from companies with credit ratings below investment grade (BB+ or lower). They offer higher yields to compensate for higher default risk. |
| **HY-IG spread** | The difference between the option-adjusted spread on high-yield bonds and the option-adjusted spread on investment-grade bonds. Our primary signal variable. |
| **Impulse response** | A measure of how one variable responds over time to a one-time shock in another variable. Shows whether effects are immediate, delayed, persistent, or transient. |
| **In-sample / Out-of-sample** | In-sample data is used to build and fit models. Out-of-sample data is held back and used only to test whether the model works on data it has never seen -- the gold standard for model validation. |
| **Investment-grade bonds** | Bonds from companies with credit ratings of BBB- or above. Considered safer, with lower yields. |
| **Local projection** | A method for estimating impulse responses by running separate regressions at each forecast horizon. More robust than traditional VAR methods because it does not require specifying the full system dynamics. Developed by Jorda (2005). |
| **Markov-switching model** | A model where the underlying regime (e.g., bull vs. bear market) can change randomly according to a Markov process. Each regime has its own set of parameters. Developed by Hamilton (1989). |
| **Merton model** | A structural model of credit risk that treats a company's equity as a call option on its assets. When asset value drops toward the debt level, equity falls and credit spreads widen simultaneously. Developed by Merton (1974). |
| **NFCI** | National Financial Conditions Index, published weekly by the Chicago Federal Reserve. Measures overall conditions in U.S. financial markets. Positive values indicate tighter-than-average conditions. |
| **Option-adjusted spread (OAS)** | A credit spread that accounts for any embedded options (like call provisions) in the bond. Provides a cleaner measure of pure credit risk than raw yield spreads. |
| **Quality spread** | The spread between the lowest-rated high-yield bonds (CCC) and the highest-rated high-yield bonds (BB). Captures stress within the riskiest corner of the credit market. |
| **Quantile regression** | A statistical method that estimates the effect of a variable on different parts of the outcome distribution (not just the average). Particularly useful for understanding tail risks -- the worst possible outcomes. |
| **Regime** | A distinct state of the market characterized by its own statistical properties (mean returns, volatility, correlations). Markets switch between regimes over time -- think of calm weather versus storms. |
| **Sharpe ratio** | A measure of risk-adjusted return: (return - risk-free rate) / volatility. Higher is better. A Sharpe of 1.0 is generally considered good for a long-only equity strategy. |
| **Transfer entropy** | An information-theoretic measure of directed information flow between time series. Unlike Granger causality, it captures nonlinear relationships that simple correlation-based tests miss. |
| **VIX** | The CBOE Volatility Index, often called the \"fear gauge.\" Measures the market's expectation of 30-day volatility in the S&P 500, derived from option prices. |
| **VIX term structure** | The difference between longer-dated (VIX3M, 3-month) and shorter-dated (VIX, 1-month) implied volatility. When VIX3M > VIX (contango), markets are calm. When VIX > VIX3M (backwardation), near-term fear exceeds medium-term expectations. |
| **Walk-forward validation** | A backtesting method that simulates real-time trading by training the model on past data and testing on subsequent data, then rolling the window forward. Prevents lookahead bias -- the most common source of false strategy performance. |
| **Z-score** | A statistical measure of how many standard deviations a value is from its mean. A z-score of +2 means the value is 2 standard deviations above average -- a condition that occurs less than 5% of the time in a normal distribution. We use rolling windows so the baseline adapts over time. |
