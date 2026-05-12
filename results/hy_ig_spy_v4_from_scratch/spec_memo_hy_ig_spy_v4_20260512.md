# Specification Memo — HY-IG Credit Spread → SPY (v4 from scratch)

**File:** `spec_memo_hy_ig_spy_v4_20260512.md`
**pair_id:** `hy_ig_spy_v4_from_scratch`
**Author:** Research Ray
**Date:** 2026-05-12
**Purpose:** Quick-unblock memo for Evan (econometrics) and Dana (data). Full research brief follows.

---

## 1. Recommended Dependent Variable

**SPY monthly log return** — computed from daily adjusted-close prices (dividend-reinvested). Monthly granularity matches the data-update cadence of the FRED spread series and the horizon over which credit-cycle effects transmit to equity prices (Gilchrist & Zakrajšek, 2012 find the GZ spread leads output and equity by 1-6 months at monthly resolution). Log returns are preferred over arithmetic returns for their additive properties over multi-month horizons and better approximation of normality at the monthly frequency.

*Alternative considered and not recommended:* S&P 500 Index total return (^GSPC). SPY adjusted close is preferred because it directly reflects what a real investor would hold and has dividend-reinvestment embedded in the price series from Yahoo Finance. The difference is small but matters for precise OOS P&L accounting.

---

## 2. Key Regressors from the Literature

| Regressor | Concept | Construction | Primary citation(s) |
|---|---|---|---|
| **HY-IG spread (level)** | Aggregate credit-cycle risk premium | BAMLH0A0HYM2 minus BAMLC0A0CM (OAS, bps) | Gertler & Lown (1999); Gilchrist & Zakrajšek (2012) |
| **HY-IG spread (z-score)** | Normalized stress level vs own history | Rolling 36-month z-score of HY-IG level | Mueller, Tahbaz-Salehi & Vedolin (2019) |
| **HY-IG spread (rate of change, MoM)** | Momentum / acceleration of credit tightening | First difference of HY-IG level | Fama & French (1989); Keim & Stambaugh (1986) |
| **GZ excess bond premium (EBP)** | Idiosyncratic credit risk stripped of systematic compensation | Residual from fitted credit spread model | Gilchrist & Zakrajšek (2012) — primary instrument series |
| **NFCI (Chicago Fed)** | Broad financial conditions composite | FRED: NFCI | Brave & Butters (2011); IMF World Economic Outlook 2017 |
| **VIX** | Equity implied volatility / risk appetite | FRED: VIXCLS (or CBOE direct) | Whaley (2000); Bekaert, Hoerova & Lo Duca (2013) |

*Evan:* For the primary specification, start with HY-IG spread level and z-score. The NFCI and VIX serve as robustness checks and controls for omitted risk-appetite variation. EBP is the theoretically cleanest regressor but is available at monthly frequency only from the GZ dataset (St. Louis Fed research page); Dana should verify current availability before Evan depends on it.

---

## 3. Common Instruments or Identification Strategies

The endogeneity concern in HY-IG → SPY is two-way: credit spreads widen when equities fall (simultaneous causation), meaning OLS coefficients may be biased. Literature responses:

| Strategy | Description | Papers using it |
|---|---|---|
| **Lag-based identification** | Use lagged spread values as regressors; sufficient if spreads are predetermined at monthly frequency | Most VAR-based studies; Fama & French (1989) |
| **Toda-Yamamoto Granger** | Tests predictive content in a VAR augmented by max-integration-order lags; robust to I(1)/I(0) uncertainty | Toda & Yamamoto (1995); applied in credit-equity literature as a pre-test |
| **GZ Excess Bond Premium** | The EBP isolates the idiosyncratic (non-default) component of corporate spreads; arguably more exogenous to contemporaneous equity moves | Gilchrist & Zakrajšek (2012); López-Salido, Stein & Zakrajšek (2017) |
| **Local Projections (Jordà)** | Horizon-by-horizon OLS with lagged controls; avoids VAR coefficient restrictions; identification by lag | Jordà (2005); Favara & Imbs (2015) |
| **HMM regime label** | Latent regime identification removes estimation-window simultaneity bias | Hamilton (1989); applied to credit regimes |

*Evan:* For v4, the recommended primary approach is Local Projections with a lag-based identification assumption (spread in month t−k, SPY return in month t). This avoids the lag-selection sensitivity of VAR and is transparent. Add Toda-Yamamoto Granger as a pre-test. IV using the EBP is preferred if Dana can confirm the series through 2025.

---

## 4. Known Identification Pitfalls / Method Sensitivities

1. **Non-stationarity of spread levels.** The HY-IG spread level is plausibly I(1) or near-I(1) over some subsamples (GFC era produces persistent deviations). Spurious regression risk is real. Evan must run ADF + KPSS on both the level and first difference and select the specification accordingly. First-differenced spread may be stationary throughout; level may require detrending.

2. **GFC dominance.** The 2008-09 episode contributes spread levels 3-5x normal. Full-sample OLS will have leverage points at 2008-09 observations. Report full-sample and GFC-excluded estimates side by side; flag any coefficient that changes sign or halves in magnitude.

3. **Regime-switching of the relationship.** The HY-IG → SPY lead can compress from months to days during acute crises (COVID 2020). Standard OLS assumes time-invariant parameters. Use rolling-window or HMM regime-conditional estimates to expose this non-stationarity.

4. **Look-ahead bias in z-score construction.** Rolling z-scores use in-sample mean and variance. Evan must ensure any z-score used in the OOS tournament is computed with an expanding window, not a full-sample normalization, to prevent look-ahead bias.

5. **Rate-shock confounding.** The 2022 SPY drawdown was interest-rate-driven, not credit-cycle-driven, yet HY-IG spreads did widen. OLS will attribute some of SPY's 2022 decline to HY-IG even though the channel was largely rate repricing. Control variables: 10yr Treasury yield level or yield change is recommended for robustness checks.

---

## 5. Sample Period Conventions in the Literature

| Convention | Rationale | Representative papers |
|---|---|---|
| **1997-present** (full FRED availability) | ICE BofA OAS series begin in Jan 1997; full credit cycle coverage including dotcom, GFC, COVID, inflation-2022 | Gilchrist & Zakrajšek (2012) use 1973-2010; later replications typically start at series inception |
| **2000-present** | Start post-dotcom bubble buildup to avoid potential survivorship bias in early HY universe | Some SSRN working papers on credit-equity timing |
| **GFC split: pre-2007 / 2010-present** | Isolate post-ZIRP behavior; many papers note GFC-era parameter shifts | Mueller et al. (2019); López-Salido et al. (2017) |
| **Monthly frequency** | Matches FRED series availability and credit-cycle transmission horizon; avoids microstructure noise in daily spreads | Consensus across macro-finance literature |

*Recommended for v4:* 1997-01 to present, monthly. Report full-sample plus subsample splits at GFC divide and post-2010 (ZIRP era). This gives the broadest credit-cycle coverage while allowing subsample robustness checks that the literature calls for.

---

*Full research brief follows in `research_brief_hy_ig_spy_v4_20260512.md`.*

*Dana: data request is in `handoff_ray_v4_20260512.md`.*
*Evan: spec memo is ready — you can begin specifying the model. Full brief forthcoming.*
