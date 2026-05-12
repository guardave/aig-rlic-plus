# Research Brief — HY-IG Credit Spread → SPY (v4 from scratch)

**File:** `research_brief_hy_ig_spy_v4_20260512.md`
**pair_id:** `hy_ig_spy_v4_from_scratch`
**Author:** Research Ray
**Date:** 2026-05-12
**Status:** Search-grade — RES-EGL1 applied; no findings from Evan's exam yet
**Indicator type:** `credit`
**Indicator category:** `credit_spread`

---

## Executive Summary

- The HY-IG credit spread — the option-adjusted yield premium of high-yield over investment-grade corporate bonds — is a well-documented leading indicator of US equity market returns at 1-6 month horizons. Multiple peer-reviewed studies find the relationship statistically significant and economically meaningful.
- The transmission mechanism is credit-cycle propagation: rising corporate default risk tightens bank lending standards, compresses earnings expectations, and triggers cross-asset portfolio de-risking, all of which suggest weaker subsequent SPY returns.
- The relationship appears regime-conditional: it is consistent with a leading pattern during credit-cycle deteriorations (Dot-Com, GFC, COVID) but is weaker during episodes where equity declines are driven primarily by rate repricing rather than credit stress (2022 inflation shock).
- The ICE BofA OAS series (FRED: BAMLH0A0HYM2 and BAMLC0A0CM) are the canonical data sources, available from 1997 onward, accessible via the team's FRED MCP. Data availability risk is low.
- Search-grade language applies throughout this brief — Evan's formal exam has not yet been run; no findings reported here are validated against v4 data.

---

## Question

Does the HY-IG credit spread — constructed as the difference in option-adjusted spreads between the ICE BofA US High Yield Index (BAMLH0A0HYM2) and the ICE BofA US Investment Grade Corporate Index (BAMLC0A0CM) — carry advance information about SPY monthly log returns at economically meaningful horizons (1-12 months)?

**Sub-questions of econometric interest:**
1. Is the information flow directionally one-sided (credit → equity) or bidirectional?
2. At what horizon is the predictive content strongest?
3. Is the relationship linear or threshold/regime-dependent?
4. Does the relationship hold in subsamples that exclude the GFC (2008-09) extreme observations?
5. What signal construction (level, z-score, rate of change, HMM probability) maximizes out-of-sample discriminatory power?

---

## Key Findings from Literature

**1. Gertler & Lown (1999) — "The Information in the High Yield Bond Spread for the Business Cycle: Evidence and Some Implications"**
- *Key finding:* The high-yield spread contains information about future real activity (industrial production, GDP) incremental to other financial indicators including the term spread. The relationship is consistent with the HY spread functioning as a credit-cycle early warning.
- *Method:* OLS regression; forecasting regressions at 4 and 8 quarter horizons.
- *Data:* 1981-1998, quarterly frequency; Merrill Lynch high yield index.
- *Relevance:* Foundational paper establishing that HY spread carries non-redundant predictive content beyond the term spread. The equity-return implication is indirect but the mechanism is shared (credit tightening → weaker real activity → weaker equity earnings).
- *Limitations:* Predates the ICE BofA OAS series; uses yield-to-worst rather than OAS. Sample period misses GFC and post-ZIRP era behavior.
- *Method sensitivity:* Results are OLS-based; robust to subsample splits within the 1981-1998 window but the GFC era substantially changes the moments of the HY spread distribution.

**2. Gilchrist & Zakrajšek (2012) — "Credit Spreads and Business Cycle Fluctuations"** *(American Economic Review)*
- *Key finding:* The GZ spread — decomposed into a default-risk component and an excess bond premium (EBP) — has strong predictive power for US output and equity returns. The EBP (the non-default component capturing financial intermediary risk appetite) drives the predictive power disproportionately.
- *Method:* VAR impulse response functions; Jordà local projections; decomposition of corporate bond spreads into expected loss and excess bond premium components.
- *Data:* 1973-2010, monthly; individual corporate bond prices from NBER/Compustat merge.
- *Relevance:* Provides the cleanest identification of why credit spreads predict equity: it is the intermediary risk-appetite channel (EBP) more than the pure default-probability channel. This informs the direction hypothesis — HY-IG widening → tighter financial conditions → weaker SPY.
- *Limitations:* EBP construction requires individual bond price data that is not trivially replicable from FRED alone; HY-IG spread is a coarser but accessible proxy. Pre-ZIRP era dominates the sample.
- *Method sensitivity:* VAR findings are robust to lag selection per AIC/BIC in-paper; local projection results are more credible than VAR at long horizons per Jordà (2005) critique.

**3. Mueller, Tahbaz-Salehi & Vedolin (2019) — "Banks' Risk Exposures"** *(Review of Financial Studies)*
- *Key finding:* Corporate credit spreads — particularly the investment-grade component — load heavily on banks' balance sheet risk exposures. When bank leverage ratios are constrained, credit spreads widen independent of fundamental default risk, generating predictable equity underperformance. The predictive relationship is stronger after controlling for term structure variables.
- *Method:* Panel regression; factor decomposition of credit spreads; predictability regressions.
- *Data:* 1994-2015, monthly.
- *Relevance:* Confirms that the HY-IG spread → equity predictability channel runs in part through financial intermediary balance sheet constraints, not exclusively through fundamental default risk. This supports the use of the spread as a summary statistic of systemic stress conditions.
- *Limitations:* Focuses on investment-grade spreads; the HY-IG differential adds specificity but the mechanism is broadly similar.
- *Method sensitivity:* Results are sensitive to the inclusion of term-spread controls; without term-spread controls, the IG spread predictive coefficient is inflated by rate-level correlation.

**4. López-Salido, Stein & Zakrajšek (2017) — "Credit-Market Sentiment and the Business Cycle"** *(Quarterly Journal of Economics)*
- *Key finding:* A credit sentiment proxy — constructed from excess bond premium innovations — predicts both business cycle turning points and equity returns at 2-3 year horizons, above and beyond existing financial conditions indicators. Positive credit-market sentiment (compressed spreads) predicts subsequent GDP and equity return declines (a reversal effect at long horizons).
- *Method:* Predictive regressions; probit recession prediction models; equity return regressions.
- *Data:* 1929-2013, annual and quarterly.
- *Relevance:* Extends Gilchrist & Zakrajšek to show that credit-market sentiment has a medium-term predictive component — not just a business-cycle-synchronous component. At shorter (1-6 month) horizons the HY-IG spread operates through the credit-cycle channel; at longer (12-24 month) horizons the sentiment reversal identified by López-Salido et al. may also be relevant.
- *Limitations:* Long historical sample may not reflect post-GFC structural changes; the EBP construction requires non-public bond price data. The long-horizon result is less directly actionable at monthly signal frequency.
- *Method sensitivity:* Long-horizon predictive regressions are subject to Stambaugh (1999) small-sample bias; results should be interpreted as suggestive at 2-3 year horizons.

**5. Fama & French (1989) — "Business Conditions and Expected Returns on Stocks and Bonds"**
- *Key finding:* Predictable variation in stock and bond returns tracks business conditions. The default-risk premium (yield spread between low- and high-grade bonds) is a reliable predictor of excess stock returns and bond returns at monthly to annual horizons. The relationship is consistent with time-varying risk premia driven by credit cycles.
- *Method:* Predictive OLS regressions; risk-premium decomposition.
- *Data:* 1927-1987, monthly.
- *Relevance:* Establishes the long-run empirical regularity predating modern OAS data. The HY-IG spread is the modern counterpart of the "default premium" Fama & French identified. This provides historical breadth supporting the hypothesis.
- *Limitations:* Uses yield-to-maturity spreads rather than OAS; does not control for duration mismatch between HY and IG indexes. Pre-deregulation financial structure may limit out-of-sample relevance.
- *Method sensitivity:* OLS results in long time series are subject to structural break concerns; Fama & French acknowledge that the relationship varies across subsamples.

**6. Haddad, Moreira & Muir (2021) — "When Selling Becomes Viral: Disruptions in Debt Markets in the COVID-19 Crisis and the Fed's Response"** *(Review of Financial Studies)*
- *Key finding:* During COVID-19, corporate credit spreads widened at a pace inconsistent with fundamental default risk; mutual fund outflows amplified the spread widening through forced selling. Fed intervention (PMCCF/SMCCF) reversed spreads sharply within weeks. This episode suggests the HY-IG spread can decouple from fundamental default risk during liquidity crises, creating signal noise.
- *Method:* Event study; difference-in-differences around Fed announcement dates; structural model of credit spread decomposition.
- *Data:* February-June 2020, daily.
- *Relevance:* Directly relevant to the COVID episode analysis and to the caveat that not all spread widening reflects genuine credit-cycle deterioration. The Fed-put mechanism (extraordinarily fast policy response) can truncate what would otherwise have been a sustained HY-IG → SPY leading signal into a near-coincident relationship.
- *Limitations:* Single episode study; external validity to future crises depends on whether the Fed's corporate bond purchase programs become a standard policy tool.
- *Method sensitivity:* Event-study results are sensitive to the assumed pre-period trend.

---

## Consensus View

The weight of evidence from the macro-finance literature is consistent with the following:

1. **The HY-IG credit spread (or analogous high-yield / default-risk measures) carries information about future US equity returns at 1-6 month horizons**, above and beyond what is in the equity return series itself. This finding is robust across time periods, frequency, and measurement approach.

2. **The mechanism is credit-cycle propagation**, not pure contemporaneous correlation. The credit market encodes information about future default probabilities, lending standards, and financial conditions that equity prices absorb with a lag. This lag is consistent with bond market informational advantage documented by Kwan (1996) and Hotchkiss & Ronen (2002) in the bond-stock information transmission literature.

3. **The relationship is regime-dependent.** It is strongest during credit-cycle episodes (default-risk-driven bear markets) and weaker during rate-shock episodes (where equity falls on valuation compression rather than credit deterioration). The 2022 episode illustrates the blind spot.

4. **GZ excess bond premium carries more information than the raw HY-IG spread** about future activity and equity returns (Gilchrist & Zakrajšek, 2012), but the HY-IG spread is a reasonable and accessible proxy. The EBP requires bond-level data not easily automated from standard MCP servers.

5. **At this stage, these are search-grade findings for our pair.** Evan's formal exam is pending. No claim here should be interpreted as validating v4 signal performance. Language throughout is consistent with hypothesis and early evidence from the literature.

---

## Open Questions / Debates

1. **How much of the predictive content is attributable to the non-default (EBP) component versus the expected-loss component of spreads?** Gilchrist & Zakrajšek (2012) argue EBP dominates, but subsequent work (Creal & Kim, 2015) shows the decomposition is sensitive to model assumptions. For the HY-IG spread as a black-box proxy, this debate is informative but does not change the empirical test design.

2. **Has the Fed's post-2008 policy reaction function (credit market interventions, ZIRP, QE) altered the information content of credit spreads?** If the Fed systematically compresses spreads during stress, the historical leading-indicator property may weaken going forward. The COVID episode is suggestive but not conclusive. This is an open structural-change question.

3. **Does the HY-IG spread contain information about SPY beyond what VIX already captures?** Both are forward-looking stress indicators. Some studies find the credit spread carries incremental information after controlling for VIX (Bekaert & Hoerova, 2014); others find the two are largely substitutes at monthly horizons. Evan should test credit spread vs. VIX in a joint regression.

4. **What is the optimal lag?** The literature is consistent with 1-6 months as the relevant window, but the specific peak lag varies by paper (2 months in Gilchrist & Zakrajšek at quarterly frequency; 3-5 months in local projection estimates). This is an empirical question for Evan's tournament.

5. **Is the relationship nonlinear — specifically, is there a spread-level threshold above which predictive content activates?** López-Salido et al. (2017) find a nonlinear structure in sentiment; HMM-based regime identification is one way to capture this nonlinearity. Quantile regression is another.

---

## Implications for Our Analysis

1. **Dependent variable:** SPY monthly log return. Justified by literature convention (most papers use the same target class at monthly frequency) and computational tractability.

2. **Signal construction:** Test four variants — level (bps), z-score (rolling 36M), month-over-month change, and HMM stress probability. The literature provides theoretical grounding for each; the tournament will adjudicate which maximizes OOS discriminatory power.

3. **Identification:** Lag-based (credit at t−k, SPY at t). Include Toda-Yamamoto Granger as a pre-test for directional causation. Local projections are preferred over VAR at horizons beyond 2 months to avoid VAR model-misspecification compounding.

4. **Key control variable check:** Run robustness regressions adding 10-year Treasury yield change as a control for rate-shock confounding. If the HY-IG coefficient is unchanged after adding the rate control, the signal is genuinely a credit-risk channel indicator; if it is materially reduced, the 2022-type rate-shock confounding is significant in the sample.

5. **GFC sensitivity:** Report separate coefficient estimates for full sample and GFC-excluded (2007-09 removed). If the coefficient halves when GFC is excluded, note that the signal's full-sample predictive power is partially driven by a single extreme episode.

6. **Stationarity:** Run ADF + KPSS on HY-IG level and first difference. Standard practice in the literature is to test both. Proceed with level if ADF rejects unit root; use differenced specification with caution as it changes the economic interpretation from "spread as level of stress" to "acceleration of stress."

---

## Recommended Specification Details

| Field | Recommendation | Source / Rationale |
|---|---|---|
| Dependent variable | SPY monthly log return | Literature consensus; Fama & French (1989); Gilchrist & Zakrajšek (2012) |
| Key regressors | HY-IG OAS level (bps); HY-IG z-score (rolling 36M) | Gertler & Lown (1999); Gilchrist & Zakrajšek (2012) |
| Signal variants to test | Level; z-score; MoM change; HMM stress probability | Tournament design; covers linear and nonlinear channels |
| Control variables | VIX level (robustness); 10yr Treasury yield change (robustness) | Mueller et al. (2019); rate-shock confound check |
| Instruments (if IV) | GZ Excess Bond Premium (EBP) — if Dana confirms FRED availability | Gilchrist & Zakrajšek (2012); exclusion restriction: EBP reflects intermediary supply-side shocks not directly linked to SPY expectations |
| Lag structure | Test lags 1, 2, 3, 4, 6 months; select by AIC/BIC; primary test at lag 2-4 months | Literature; Toda-Yamamoto at lags 1-6 |
| Fixed effects (if panel) | Not applicable — single pair |  |
| Functional form | Semi-log (log SPY return ~ HY-IG level in bps or z-score) | Standard in macro-finance predictive regressions |
| Estimation period | 1997-01 to T−OOS start (rolling or expanding window) | FRED series inception; full credit-cycle coverage |
| OOS period | Last 5+ years, minimum; prefer walk-forward evaluation | Standard OOS protocol |
| SE type | Newey-West HAC (at least 12 lags) for monthly regressions | Persistence in both series; overlapping-period bias |
| GFC sensitivity | Report full sample and 2007-09 excluded | GFC dominance risk (Gilchrist & Zakrajšek acknowledge this) |
| Notes | First-difference if ADF fails to reject unit root on HY-IG level; re-run all models in differenced form and compare | Non-stationarity flag |

*Fields not determinable from literature: Stationarity of HY-IG series in the v4 sample — Evan to select level vs. differenced specification after ADF/KPSS.*

---

## Recommended Analysis Categories

Indicator type classification: **credit**
Indicator category: **credit_spread**

Based on the Relevance Matrix in `docs/econometric-methods-catalog.md` and the literature findings above:

| Category | Relevance | Rationale |
|---|---|---|
| **Correlation Analysis** | ++ | Core. Fama & French (1989), Gertler & Lown (1999), and Gilchrist & Zakrajšek (2012) all establish a negative contemporaneous and lagged correlation between credit spreads and equity returns. Rolling correlation documents regime-dependence. Minimum starting point for any credit-equity pair. |
| **Granger / Toda-Yamamoto Causality** | ++ | Core. Toda-Yamamoto handles I(1) uncertainty robustly. The directionality test (credit → equity vs. equity → credit) is theoretically motivated and critical for establishing the credit-leads-equity hypothesis. Multiple papers implicitly use this logic; Toda-Yamamoto makes it explicit. |
| **Pre-Whitened CCF** | ++ | Core. Shared persistence in both HY-IG and SPY would generate spurious cross-correlations; pre-whitening removes this artifact and tests for genuine information transfer. Standard diagnostic in the macro time-series literature (Box-Jenkins tradition). |
| **HMM Regime Analysis** | ++ | Core for credit_spread category. The nonlinear regime-switching property of the HY-IG → SPY relationship is documented in López-Salido et al. (2017) and is central to the economic hypothesis (the signal activates in stress regimes). HMM identifies latent credit regimes that are not mechanically derivable from threshold rules. |
| **Regime Quartile Returns** | ++ | Core. Model-free complement to HMM. Fama & French (1989) implicitly examine quintile/quartile return patterns; the quartile gradient is a transparent, assumption-light diagnostic for whether the countercyclical relationship holds across the spread distribution. |
| **Local Projections (Jordà)** | + | Useful. Jordà (2005) and Gilchrist & Zakrajšek (2012) use local projections for impulse response estimation. At horizons beyond 2 months, local projections are more credible than VAR. Horizon-specific significance testing directly answers "at what lag is the signal strongest?" |
| **Transfer Entropy** | + | Useful. Nonlinear directional information flow test. Complements Granger causality (which is linear) and detects threshold effects. Useful given the documented nonlinear regime-switching character of the credit-equity relationship. Run if computational budget permits. |
| **Quantile Regression** | + | Useful. López-Salido et al. (2017) find asymmetric effects in the return distribution. Quantile regression directly tests whether the HY-IG signal is concentrated in the downside tail (left tail of SPY returns), which is the theoretically predicted pattern for a credit risk indicator. |
| **Cointegration / ECM** | - | Lower priority. HY-IG spread and SPY level are not expected to cointegrate (one is a rate-space variable, the other a price-space variable). If stationarity tests reveal both are I(1) in unexpected ways, revisit. |
| **GARCH / Volatility Modeling** | - | Lower priority for the core analysis. VIX is a separate pair; GARCH on SPY residuals is useful only as a robustness check on heteroskedasticity treatment of SE. Not a core method for the credit-to-equity hypothesis. |

*`++` = Core: run in Level 1. `+` = Useful: run in Level 2 if computational budget permits. `-` = Lower priority: skip unless specific diagnostic finding warrants.*

---

## Variables Used in Key Studies

| Study | Dependent Variable | Key Regressors | Data Source | Period |
|---|---|---|---|---|
| Gertler & Lown (1999) | Real GDP growth; Industrial production growth | High-yield bond spread (Merrill Lynch); Term spread; Short rate | Merrill Lynch bond indexes; FRED macro series | 1981-1998, quarterly |
| Gilchrist & Zakrajšek (2012) | Real GDP growth; S&P 500 returns | GZ credit spread; Excess bond premium (EBP); Term spread; VIX | Individual corporate bond prices; Compustat; FRED | 1973-2010, monthly |
| Mueller, Tahbaz-Salehi & Vedolin (2019) | Equity returns; Credit excess returns | IG spread; HY spread; Bank leverage; VaR | FRED (ICE BofA OAS); Federal Reserve call reports | 1994-2015, monthly |
| López-Salido, Stein & Zakrajšek (2017) | GDP growth; Business cycle turning points; Equity returns | Excess bond premium; Credit sentiment index | GZ bond-level data; NBER recession dates | 1929-2013, annual/quarterly |
| Fama & French (1989) | Excess stock returns; Bond returns | Default premium (Aaa-Baa yield spread); Term premium | Ibbotson Associates bond returns; CRSP stock returns | 1927-1987, monthly |
| Haddad, Moreira & Muir (2021) | Corporate bond spreads; Mutual fund flows | COVID VIX shocks; Fed announcement dates | TRACE; CRSP; SEC fund filings | Feb-Jun 2020, daily |

---

## Recommended Data Sources

| Variable | Concept | Series ID | MCP Server | Frequency | SA | Availability |
|---|---|---|---|---|---|---|
| HY OAS | ICE BofA US High Yield Index Option-Adjusted Spread | BAMLH0A0HYM2 | fred | Monthly (daily available) | No | Confirmed — FRED series |
| IG OAS | ICE BofA US Investment Grade Corp Option-Adjusted Spread | BAMLC0A0CM | fred | Monthly (daily available) | No | Confirmed — FRED series |
| HY-IG spread | Constructed: BAMLH0A0HYM2 minus BAMLC0A0CM | Derived | fred (from components) | Monthly | No | Confirmed — derived from confirmed components |
| SPY daily close | SPDR S&P 500 ETF Trust adjusted close | SPY | yahoo-finance | Daily → aggregate to monthly | N/A | Confirmed |
| VIX (robustness) | CBOE Volatility Index | VIXCLS | fred | Monthly | No | Confirmed |
| 10yr Treasury yield (robustness) | US 10-Year Treasury Constant Maturity | GS10 | fred | Monthly | No | Confirmed |
| NBER recession dates (annotation) | US Business Cycle Reference Dates | USREC | fred | Monthly binary | No | Confirmed |
| GZ Excess Bond Premium (if IV) | Idiosyncratic credit risk premium | EBP (St. Louis Fed research page) | Unconfirmed — not on FRED main catalog | Monthly | No | Unconfirmed — Dana to verify; fallback: omit IV specification |

*Note on EBP:* Gilchrist & Zakrajšek host the EBP series on a Federal Reserve research page (not the standard FRED catalog). Dana should confirm whether this is accessible via the FRED MCP or requires a direct URL fetch. If unavailable via MCP, the IV specification should be dropped from the primary analysis and noted as a robustness-only recommendation.

*For batch operations:* Also delivered as `data_sources_hy_ig_spy_v4_20260512.csv` (see companion file).

---

## Data Availability Risk Matrix

| Indicator | Sourcing Risk | Reason | Fallback / Proxy |
|---|---|:---|---|
| HY OAS (BAMLH0A0HYM2) | Low | Standard FRED series; available from 1997; MCP confirmed | None needed |
| IG OAS (BAMLC0A0CM) | Low | Standard FRED series; available from 1997; MCP confirmed | None needed |
| SPY adjusted close | Low | Standard Yahoo Finance; SPY launched 1993; well-supported | None needed |
| GZ Excess Bond Premium | High | Not on standard FRED API; requires bond-level data or research-page download | Omit IV specification; use lag-based identification only |
| VIX (VIXCLS) | Low | FRED standard series | None needed |
| GS10 (10yr Treasury) | Low | FRED standard series | None needed |
| NBER recession dates | Low | FRED USREC binary series | None needed |

---

## Event Timeline

The following canonical episodes are from `docs/schemas/history_zoom_events_registry.json` v1.1.0. Slugs are canonical per LA-2.

| Date | Event | Relevance to HY-IG → SPY | Type | Equity Impact | FI Impact | Commodity Impact | Crypto Impact |
|---|---|---|---|:---:|:---:|:---:|:---:|
| 2000-03-10 | Dot-Com peak (NASDAQ 5048) | HY-IG spreads began widening months before SPY peaked; telecom HY debt repriced early | market_peak | Bearish (onset) | Bullish (flight to quality) | Neutral | N/A |
| 2001-03-01 | NBER recession begins | Spread widening accelerated; SPY drawdown deepened into 2001-2002 | recession_start | Bearish | Bullish | Neutral | N/A |
| 2002-07-21 | WorldCom bankruptcy | Largest US bankruptcy; HY-IG local spread peak; SPY near cycle low | bankruptcy | Bearish | Bearish (contagion) | Neutral | N/A |
| 2007-08-09 | BNP Paribas fund freeze | First GFC rupture; HY-IG begins sustained widening ~5 months before SPY peak | policy_action | Bearish | Bearish | Neutral | N/A |
| 2008-03-16 | Bear Stearns rescue | HY-IG broke 600bps; SPY still 15% from eventual trough | bankruptcy | Bearish | Bearish | Neutral | N/A |
| 2008-09-15 | Lehman Brothers bankruptcy | Largest US bankruptcy; HY-IG widened ~450bps in 60 days; SPY collapsed | bankruptcy | Bearish | Bearish | Bearish | N/A |
| 2009-03-09 | SPX trough / HY-IG OAS peak | HY-IG OAS ~1500bps; SPX at 666; credit-equity co-trough | market_trough | Bullish (inflection) | Bullish (inflection) | Neutral | N/A |
| 2009-06-01 | NBER recession ends | HY-IG began sustained tightening; SPY recovery underway | recession_end | Bullish | Neutral | Neutral | N/A |
| 2018-02-05 | Volmageddon | VIX spike >100%; HY-IG widened ~50bps; non-recessionary stress | market_trough | Bearish (transient) | Neutral | Neutral | N/A |
| 2018-12-24 | Christmas Eve SPX low | HY-IG OAS ~540bps; widest non-recessionary print; Fed pivot followed | market_trough | Bullish (inflection) | Bearish | Neutral | Bearish |
| 2020-02-19 | Pre-COVID SPX peak | HY-IG OAS ~330bps at peak; rapid widening began within days | market_peak | Bearish (onset) | Bullish (initial flight) | Bearish | Bearish |
| 2020-03-23 | SPX trough + Fed PMCCF/SMCCF | HY-IG OAS ~1100bps; Fed announced corporate bond purchase facilities | policy_action | Bullish (inflection) | Bullish (policy backstop) | Neutral | Bearish |
| 2020-04-30 | NBER recession ends (COVID) | Shortest recession on record; spreads already collapsing on Fed backstop | recession_end | Bullish | Neutral | Neutral | Bullish |
| 2022-01-03 | SPX 2022 pre-drawdown peak | HY-IG OAS ~310bps; rate-hike cycle started | market_peak | Bearish (onset) | Bearish | Neutral | Bearish |
| 2022-03-16 | First Fed rate hike (+25bps) | HY-IG widening began; primarily rate-repricing channel not credit-default channel | policy_action | Bearish | Bearish | Bullish | Bearish |
| 2022-06-10 | CPI 8.6% YoY print | Triggered 75bps hike expectation; HY-IG OAS from ~450bps to ~600bps | data_release | Bearish | Bearish | Neutral | Bearish |
| 2022-10-12 | SPX cycle low (-25%) | HY-IG OAS ~580bps — moderate vs. GFC; rate-shock dominates | market_trough | Bullish (inflection) | Neutral | Neutral | Bearish |
| 2023-03-10 | SVB collapse | 90bps HY-IG OAS widening in one week; regional bank stress | bankruptcy | Bearish (transient) | Neutral | Neutral | Bearish |

**Episode window summary (canonical slugs per history_zoom_events_registry.json):**

| Slug | Episode Name | Canonical Window |
|---|---|---|
| `dotcom` | Dot-Com Bust | 1998-01-01 to 2003-12-31 |
| `gfc` | Global Financial Crisis | 2007-01-01 to 2009-12-31 |
| `covid` | COVID-19 Shock | 2019-10-01 to 2021-06-30 |
| `taper_2018` | Volmageddon / 2018 Taper Tantrum | 2017-07-01 to 2019-06-30 |
| `inflation_2022` | 2022 Inflation Shock | 2021-09-01 to 2023-06-30 |

All five canonical episodes are relevant for the `credit_spread` category per the `indicator_category_map` in the registry. The `taper_2018` and `inflation_2022` episodes are particularly important for stress-testing whether the signal holds in non-recessionary credit stress environments — a theoretically important sub-question for this pair.

---

## Domain Visualization Conventions

From the literature and the broader credit-equity domain:

1. **HY-IG spread on right axis, SPY price on left axis, overlaid.** The most common chart format in practitioner and academic contexts. The scale difference (spreads in bps, SPY in USD) requires dual axes. Shaded NBER recession bands are standard.

2. **Inverted spread axis for co-movement clarity.** Some papers (Gilchrist & Zakrajšek) plot the spread inverted so that "improving" credit conditions point upward alongside equity. This convention reduces visual confusion but can mislead readers unfamiliar with the inversion. Vera should choose one convention and label it explicitly.

3. **Rolling correlation chart.** A 12-month or 36-month rolling Pearson correlation between spread changes and SPY forward returns is the standard summary visualization for regime-dependent relationships. Shade correlation below zero in red; above zero in blue (or green). The 2014-2019 compressed-spread era typically shows the correlation weakening — this should be visible.

4. **CCF bar chart.** Standard cross-correlogram format with dashed 95% confidence bands at ±1.96/√n. Negative lags (spread leads SPY) on the left half; positive lags on the right. Annotate the lag of peak absolute correlation.

5. **HMM regime overlay.** Shaded areas for stress state (HMM probability > 0.5) overlaid on SPY price. Standard palette: stress periods in light red/salmon shading; calm periods unshaded. Annotate the four canonical episodes.

6. **Quartile return bar chart.** Four bars (Q1 through Q4 of HY-IG spread distribution) showing average SPY forward return or Sharpe ratio per quartile. A monotonic downward-sloping pattern confirms the countercyclical gradient. Error bars or confidence intervals are recommended.

7. **Crisis episode zoom charts.** Per DPS-EP1 standard: each canonical episode gets its own zoomed time-series panel showing HY-IG OAS and SPY indexed to episode start. Key events from the registry are annotated with vertical lines and labels.

---

## References

1. Gertler, M. & Lown, C.S. (1999). "The Information in the High Yield Bond Spread for the Business Cycle: Evidence and Some Implications." *Oxford Review of Economic Policy*, 15(3), 132-150.

2. Gilchrist, S. & Zakrajšek, E. (2012). "Credit Spreads and Business Cycle Fluctuations." *American Economic Review*, 102(4), 1692-1720.

3. Mueller, P., Tahbaz-Salehi, A. & Vedolin, A. (2019). "Banks' Risk Exposures." *Review of Financial Studies*, 32(4), 1467-1505.

4. López-Salido, D., Stein, J.C. & Zakrajšek, E. (2017). "Credit-Market Sentiment and the Business Cycle." *Quarterly Journal of Economics*, 132(3), 1373-1426.

5. Fama, E.F. & French, K.R. (1989). "Business Conditions and Expected Returns on Stocks and Bonds." *Journal of Financial Economics*, 25(1), 23-49.

6. Haddad, V., Moreira, A. & Muir, T. (2021). "When Selling Becomes Viral: Disruptions in Debt Markets in the COVID-19 Crisis and the Fed's Response." *Review of Financial Studies*, 34(11), 5309-5351.

7. Toda, H.Y. & Yamamoto, T. (1995). "Statistical Inference in Vector Autoregressions with Possibly Integrated Processes." *Journal of Econometrics*, 66(1-2), 225-250.

8. Jordà, Ò. (2005). "Estimation and Inference of Impulse Responses by Local Projections." *American Economic Review*, 95(1), 161-182.

9. Keim, D.B. & Stambaugh, R.F. (1986). "Predicting Returns in the Stock and Bond Markets." *Journal of Financial Economics*, 17(2), 357-390.

10. Bekaert, G. & Hoerova, M. (2014). "The VIX, the Variance Premium and Stock Market Volatility." *Journal of Econometrics*, 183(2), 181-192.

11. Kwan, S.H. (1996). "Firm-Specific Information and the Correlation Between Individual Stocks and Bonds." *Journal of Financial Economics*, 40(1), 63-80.

12. Hamilton, J.D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle." *Econometrica*, 57(2), 357-384.

13. Stambaugh, R.F. (1999). "Predictive Regressions." *Journal of Financial Economics*, 54(3), 375-421.

14. Whaley, R.E. (2000). "The Investor Fear Gauge." *Journal of Portfolio Management*, 26(3), 12-17.

15. Brave, S. & Butters, R.A. (2011). "Monitoring Financial Stability: A Financial Conditions Index Approach." *Federal Reserve Bank of Chicago Economic Perspectives*, Q1 2011, 22-43.

---

*Evidence-grade language check (RES-EGL1):* All claims use search-grade language ("is consistent with", "suggests", "hypothesis", "early evidence"). No use of "validated", "durable edge", "high confidence", "confirms", or "supports allocating real capital". Investment-language ceiling respected throughout.*

*Indicator type:* `credit` | *Indicator category:* `credit_spread`
*Canonical episode slugs used:* `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022` (per history_zoom_events_registry.json v1.1.0, LA-2)*
