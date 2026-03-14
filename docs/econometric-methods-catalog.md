# Econometric & Statistical Methods Catalog
## Multi-Indicator Analysis Framework — Reference Appendix

Here is a comprehensive catalogue of **90+ candidate econometric and statistical methods** organized by category, with relevance to indicator-to-target analysis across credit, macro, volatility, sentiment, and cross-asset dimensions.

---

## 1. Correlation and Dependence

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 1 | **Spearman Rank Correlation** | Non-parametric monotonic association; no normality assumption needed | Captures monotonic but non-linear co-movement between spreads and returns | `scipy.stats.spearmanr` | Straightforward | Spearman (1904) |
| 2 | **Kendall's Tau** | Rank-based concordance measure; robust to outliers | More robust than Pearson when spread/equity data have fat tails or outliers | `scipy.stats.kendalltau` | Straightforward | Kendall (1938) |
| 3 | **Rolling / Expanding Window Correlation** | Time-varying Pearson or rank correlation over rolling windows | Reveals how the spread-equity relationship strengthens during stress periods | `pandas.DataFrame.rolling().corr()` | Straightforward | — |
| 4 | **Dynamic Conditional Correlation (DCC-GARCH)** | Multivariate GARCH that estimates time-varying correlations between series | Shows how credit-equity correlation spikes during crises; core tool for contagion analysis | `arch` (via `rmgarch` in R; custom in Python), or `mgarch` | Advanced | [Engle (2002)](https://www.researchgate.net/publication/5000337_Dynamic_Conditional_Correlation_-_A_Simple_Class_of_Multivariate_GARCH_Models) |
| 5 | **Gaussian Copula** | Models joint distribution with flexible marginals; measures dependence structure | Separates marginal behavior of spreads/equity from their dependence structure | [`pycop`](https://pypi.org/project/pycop/), [`copul`](https://pypi.org/project/copul/) | Moderate | [Embrechts, McNeil & Straumann (2002)](https://people.math.ethz.ch/~embrecht/ftp/copchapter.pdf) |
| 6 | **Student-t Copula** | Like Gaussian copula but captures symmetric tail dependence | Better than Gaussian copula when spreads and equities crash together (tail co-dependence) | `pycop`, `copul` | Moderate | Demarta & McNeil (2005) |
| 7 | **Clayton / Gumbel Copula** | Asymmetric copulas capturing lower-tail (Clayton) or upper-tail (Gumbel) dependence | Clayton captures joint distress (widening spreads + falling equities); Gumbel captures joint euphoria | `pycop`, `copul` | Moderate | [Nelsen (2006), *An Introduction to Copulas*](https://freakonometrics.hypotheses.org/2435) |
| 8 | **Time-Varying Copula** | Copula parameters evolve over time (e.g., via GAS or DCC dynamics) | Models how the dependence structure between spreads and equities shifts across regimes | `pycop`, custom implementation | Advanced | [Oh & Patton (2013)](https://ideas.repec.org/p/duk/dukeec/13-30.html) |
| 9 | **Tail Dependence Coefficients** | Probability that both series are in extreme quantiles simultaneously | Quantifies whether spread spikes and equity crashes tend to co-occur in the tails | `copul` (lambda_L, lambda_U), `pycop` | Moderate | Joe (1997), *Multivariate Models and Dependence Concepts* |
| 10 | **Distance Correlation (dCor)** | Measures both linear and non-linear dependence; equals zero iff independent | Detects non-linear spread-equity relationships that Pearson misses entirely | `dcor` | Moderate | Szekely, Rizzo & Bakirov (2007) |

---

## 2. Lead-Lag and Causality

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 11 | **Toda-Yamamoto Granger Causality** | Granger test valid even with non-stationary / cointegrated data (augmented lag approach) | Avoids pre-testing for unit roots in spread/equity levels; more robust than standard Granger | `statsmodels` (manual augmented VAR) | Moderate | Toda & Yamamoto (1995) |
| 12 | **Nonlinear Granger Causality** | Tests whether past values of X help predict Y beyond a linear model | Detects if credit spreads predict equity crashes through non-linear channels | Custom (kernel-based), `nolitsa` | Advanced | [Diks & Panchenko (2006)](https://www.nature.com/articles/s41598-021-87316-6) |
| 13 | **Spectral / Frequency-Domain Granger Causality** | Decomposes causality by frequency band (short-run vs. long-run) | Separates whether spreads predict equity at business-cycle frequencies vs. high-frequency noise | `spectral_connectivity_measures`, custom | Advanced | Breitung & Candelon (2006) |
| 14 | **Transfer Entropy** | Model-free, information-theoretic measure of directional information flow | Captures both linear and [non-linear causal flows from credit to equity markets](https://link.springer.com/article/10.1007/s10260-021-00614-1) without specifying a model | `pyinform`, `PyCausality`, [`TransferEntropy`](https://bookdown.org/souzatharsis/open-quant-live-book/how-to-measure-statistical-causality-a-transfer-entropy-approach-with-financial-applications.html) | Advanced | Schreiber (2000) |
| 15 | **Wavelet Coherence** | Time-frequency decomposition of co-movement; shows lead-lag at different scales | Reveals if spread-to-equity prediction is stronger at weekly vs. monthly vs. quarterly horizons | `pywt`, `waipy`, custom (Morlet wavelet) | Advanced | Torrence & Compo (1998); Grinsted et al. (2004) |
| 16 | **Cross-Correlation Function (CCF) with Pre-whitening** | Identifies optimal lag structure between two pre-whitened series | Simple first pass to find the lag at which spreads most predict returns | `statsmodels.tsa.stattools.ccf` | Straightforward | Box & Jenkins (1976) |
| 17 | **Convergent Cross Mapping (CCM)** | Detects causality in dynamical systems; works for weakly coupled non-separable systems | Alternative to Granger when spread-equity system has complex feedback loops | `pyEDM` | Advanced | Sugihara et al. (2012) |

---

## 3. Regime Identification

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 18 | **Markov-Switching Dynamic Regression (MS-DR)** | Regime-switching model where regression coefficients shift between states | Tests whether the spread-equity beta differs in crisis vs. calm regimes | `statsmodels.tsa.regime_switching.markov_regression` | Moderate | [Hamilton (1989)](https://homepage.ntu.edu.tw/~ckuan/pdf/Lec-Markov_note.pdf) |
| 19 | **Markov-Switching VAR (MS-VAR)** | VAR whose parameters switch between regimes governed by a Markov chain | Allows the entire spread-equity VAR dynamics (IRFs, etc.) to change across regimes | Custom, `statsmodels` (limited) | Advanced | Krolzig (1997), *Markov-Switching VARs* |
| 20 | **Hidden Markov Model (HMM)** | Unsupervised identification of latent states from observable data | Classifies market [into bull/bear/neutral regimes](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/) using returns + spreads as observables | [`hmmlearn`](https://datadave1.medium.com/detecting-market-regimes-hidden-markov-model-2462e819c72e) | Moderate | Rabiner (1989); [Ang & Bekaert (2002)](https://www.nber.org/system/files/working_papers/w17182/w17182.pdf) |
| 21 | **Threshold Autoregression (TAR / SETAR)** | Regime switch is triggered when an observable variable crosses a threshold | Tests if equity predictability "turns on" when spreads exceed a crisis threshold | `statsmodels` (manual), `tsDyn` (R) | Moderate | Tong (1978); Hansen (1999) |
| 22 | **Smooth Transition Autoregression (STAR / LSTAR)** | Like TAR but with gradual transition between regimes | Captures the gradual shift in spread-equity dynamics rather than an abrupt switch | Custom, `statsmodels` (limited) | Advanced | Terasvirta (1994); [Van Dijk et al. (2002)](https://www.mdpi.com/2227-7390/13/7/1128) |
| 23 | **Change-Point Detection (PELT / Binary Segmentation)** | Identifies structural breaks in mean, variance, or distribution | Detects when the [spread-equity relationship fundamentally changes](https://dl.acm.org/doi/10.1145/3773365.3773532) (e.g., GFC, COVID) | [`ruptures`](https://centre-borelli.github.io/ruptures-docs/) | Moderate | [Killick et al. (2012)](https://github.com/deepcharles/ruptures) |
| 24 | **CUSUM / MOSUM Tests** | Sequential tests for parameter constancy over time | Monitors in real time whether the spread-equity regression is stable or breaking down | `statsmodels.stats.diagnostic` | Straightforward | Brown, Durbin & Evans (1975) |

---

## 4. Time-Series Modeling

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 25 | **VECM (Vector Error Correction Model)** | VAR for cointegrated series; decomposes dynamics into short-run adjustment and long-run equilibrium | If spreads and equity are cointegrated, VECM captures the error-correction channel | [`statsmodels.tsa.vector_ar.vecm.VECM`](https://www.statsmodels.org/dev/generated/statsmodels.tsa.vector_ar.vecm.VECM.html) | Moderate | Johansen (1991); [Engle & Granger (1987)](https://mdpi.com/2079-3197/10/9/155/htm) |
| 26 | **Structural VAR (SVAR)** | VAR with contemporaneous restrictions derived from economic theory | Imposes structural identification (e.g., spreads react to equity within the day but not vice versa) | [`statsmodels.tsa.vector_ar.svar_model`](https://www.statsmodels.org/stable/vector_ar.html) | Moderate | Sims (1980); Blanchard & Quah (1989) |
| 27 | **Factor-Augmented VAR (FAVAR)** | Extracts latent factors from large panel of variables, includes them in VAR | Incorporates macro factors (inflation, industrial production) that jointly drive spreads and equities | Custom (PCA + VAR), [`TVP_FAVAR_Kalman_Filter`](https://github.com/fawdywahyu18/TVP_FAVAR_Kalman_Filter) | Advanced | [Bernanke, Boivin & Eliasz (2005)](https://hoagiet.github.io/portfolio/portfolio-6/) |
| 28 | **TVP-VAR (Time-Varying Parameter VAR)** | VAR where coefficients evolve over time via state-space / Kalman filter | Captures how the [spread-to-equity transmission mechanism changes](https://www.sciencedirect.com/science/article/abs/pii/S1057521918307555) across decades | Custom (Kalman), [`bvar`](https://blog.quantinsti.com/tvp-var-stochastic-volatility/) | Advanced | Primiceri (2005) |
| 29 | **Bayesian VAR (BVAR)** | VAR estimated with priors (Minnesota, SSVS, etc.) to handle over-parameterization | Better out-of-sample forecasting than unrestricted VAR when the spread-equity system has many lags/variables | `bvar`, custom (PyMC) | Advanced | Litterman (1986); [Koop & Korobilis (2010)](https://www.tandfonline.com/doi/full/10.1080/15140326.2024.2395114) |
| 30 | **Local Projections (Jorda)** | Directly estimates impulse responses at each horizon without VAR specification | More robust IRFs for the spread-to-equity effect; works with non-linearities and state dependence | Custom (OLS at each horizon), `linearmodels` | Moderate | Jorda (2005) |

---

## 5. Volatility and Risk

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 31 | **EGARCH** | Asymmetric GARCH; log-volatility ensures positivity; captures leverage effect | Models how equity volatility responds asymmetrically to spread shocks (bad news amplified) | [`arch`](https://arch.readthedocs.io/en/latest/univariate/univariate_volatility_modeling.html) | Moderate | Nelson (1991) |
| 32 | **GJR-GARCH (Threshold GARCH)** | Adds asymmetric term for negative shocks to conditional variance | [Captures the leverage effect](https://blog.quantinsti.com/garch-gjr-garch-volatility-forecasting-python/) where equity vol rises more after spread widening than spread tightening | `arch` | Moderate | Glosten, Jagannathan & Runkle (1993) |
| 33 | **DCC-GARCH** | Dynamic conditional correlations between multiple GARCH processes | The cornerstone model for tracking time-varying credit-equity correlation | `arch` (partial), `rmgarch` (R), custom Python | Advanced | Engle (2002) |
| 34 | **Realized Volatility (RV)** | Non-parametric volatility from high-frequency intraday returns | Provides a model-free benchmark for equity volatility; compare against spread-implied signals | `arch` (realized measures), `numpy` | Straightforward | Andersen & Bollerslev (1998) |
| 35 | **Stochastic Volatility (SV)** | Volatility follows its own latent stochastic process | More flexible than GARCH for modeling [equity volatility persistence and spread co-movement](https://github.com/ArturSepp/StochVolModels) | [`stochvolmodels`](https://pypi.org/project/stochvolmodels/), [`svolfit`](https://pypi.org/project/svolfit/), `PyMC` | Advanced | Taylor (1986); [Heston (1993)](https://www.codearmo.com/python-tutorial/heston-model-simulation-python) |
| 36 | **GARCH-MIDAS** | Decomposes volatility into short-run (daily GARCH) and long-run (macro) components | Long-run equity volatility component can be driven by credit spreads at lower frequency | `arch` (partial), custom | Advanced | Engle, Ghysels & Sohn (2013) |

---

## 6. Nonlinear and Machine Learning Methods

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 37 | **Random Forest + SHAP** | Ensemble tree model for feature importance and non-linear prediction | [Identifies which spread metrics](https://www.researchgate.net/publication/352394963_Credit_spread_approximation_and_improvement_using_random_forest_regression) (level, change, curvature) matter most for equity prediction; SHAP provides interpretability | `scikit-learn`, `shap` | Moderate | Breiman (2001); Lundberg & Lee (2017) |
| 38 | **Gradient Boosting (XGBoost / LightGBM)** | Sequential tree boosting with regularization; state-of-the-art tabular prediction | Best-in-class for [non-linear credit-spread-to-equity prediction](https://www.sciencedirect.com/science/article/abs/pii/S1544612323006451) with many candidate features; SHAP for explainability | `xgboost`, `lightgbm`, `shap` | Moderate | Chen & Guestrin (2016) |
| 39 | **LSTM (Long Short-Term Memory)** | Recurrent neural network for sequence prediction; captures long-range dependencies | Models complex temporal patterns in the spread-equity relationship that linear models miss | `tensorflow.keras`, `pytorch` | Advanced | Hochreiter & Schmidhuber (1997) |
| 40 | **Quantile Regression** | Estimates conditional quantiles rather than conditional mean | Asks: "Does a spread spike predict the 5th percentile of equity returns?" (tail risk focus) | [`statsmodels.regression.quantile_regression`](https://scikit-learn.org/stable/auto_examples/linear_model/plot_quantile_regression.html), `scikit-learn` | Moderate | Koenker & Bassett (1978) |
| 41 | **Quantile Random Forest** | Random forest that estimates the full conditional distribution | Combines non-linear flexibility of RF with distributional analysis of quantile regression | [`scikit-garden`](https://scikit-garden.github.io/examples/QuantileRegressionForests/), `quantile-forest` | Moderate | Meinshausen (2006) |

---

## 7. Signal Extraction and Filtering

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 42 | **Hodrick-Prescott Filter** | Decomposes series into trend and cycle components | Extracts the cyclical component of credit spreads that correlates with equity cycle | [`statsmodels.tsa.filters.hp_filter.hpfilter`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.filters.hp_filter.hpfilter.html) | Straightforward | Hodrick & Prescott (1997) |
| 43 | **Baxter-King Band-Pass Filter** | Isolates fluctuations within a specified frequency band | Extracts business-cycle-frequency movements in spreads (e.g., 6-32 quarters) for equity prediction | [`statsmodels.tsa.filters.bk_filter.bkfilter`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.filters.bk_filter.bkfilter.html) | Straightforward | Baxter & King (1999) |
| 44 | **Christiano-Fitzgerald Filter** | Asymmetric band-pass filter; works on full sample; handles random walks | [More flexible than Baxter-King](https://www.statsmodels.org/dev/generated/statsmodels.tsa.filters.cf_filter.cffilter.html) for non-stationary spread series; uses entire sample | `statsmodels.tsa.filters.cf_filter.cffilter` | Straightforward | Christiano & Fitzgerald (2003) |
| 45 | **Wavelet Decomposition (DWT/CWT)** | Multi-resolution analysis; decomposes into scale-specific approximations and details | Separates spread signal into [short-term noise vs. medium-term cycles vs. long-term trends](https://abouttrading.substack.com/p/financial-signal-processing-in-python-dd0) for equity forecasting | `pywt` (PyWavelets) | Moderate | Mallat (1989); Percival & Walden (2000) |
| 46 | **Kalman Filter / State-Space Model** | Optimal recursive estimation of unobserved states from noisy observations | Extracts the "true" unobservable credit risk signal from noisy spread data; time-varying parameter estimation | `statsmodels.tsa.statespace`, `filterpy` | Advanced | Kalman (1960); Harvey (1989) |
| 47 | **Hamilton Filter** | Regression-based alternative to HP filter; avoids spurious cyclicality | Cleaner business-cycle extraction from spreads than HP filter (which can create artificial cycles) | Custom (OLS), `statsmodels` | Moderate | Hamilton (2018) |

---

## 8. Event Study / Threshold / Tail Analysis

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 48 | **Extreme Value Theory (EVT) — Peaks Over Threshold** | Models the tail distribution of extreme events using Generalized Pareto Distribution | Estimates the probability that spread spikes exceed crisis thresholds and the associated equity tail risk | `pyextremes`, `scipy.stats.genpareto` | Moderate | McNeil & Frey (2000); Coles (2001) |
| 49 | **Kernel Density Estimation (KDE)** | Non-parametric estimation of the probability density function | Identifies the empirical distribution of spread changes; [locates regime boundaries as density modes](https://jakevdp.github.io/PythonDataScienceHandbook/05.13-kernel-density-estimation.html) | `scipy.stats.gaussian_kde`, `scikit-learn.neighbors.KernelDensity` | Straightforward | Silverman (1986) |
| 50 | **Quantile-Based Threshold Rules** | Define signal thresholds at percentiles of the spread distribution | Creates trading signals: "when spreads exceed the 90th percentile, equity returns are predictably negative" | `numpy.percentile`, `pandas.quantile` | Straightforward | — |
| 51 | **Event Study (Abnormal Returns)** | Measures cumulative abnormal returns around identified events | Quantifies equity market reaction around credit-spread-spike events (e.g., +2 sigma widening) | Custom (OLS market model), `eventstudy` | Moderate | MacKinlay (1997) |
| 52 | **Block Maxima / GEV Distribution** | Fits Generalized Extreme Value distribution to period maxima | Models the distribution of worst monthly spread widenings and their equity co-movement | `pyextremes`, `scipy.stats.genextreme` | Moderate | Fisher & Tippett (1928); Gnedenko (1943) |

---

## 9. Cointegration & Equilibrium

| # | Method | What It Does / When to Use | Relevance to Indicator-Target Analysis | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|---------------------------------------|----------------|------------|---------------|
| 53 | **Engle-Granger Two-Step Cointegration** | Tests for a single cointegrating relationship between two I(1) series | Determines whether an indicator and target share a long-run equilibrium; prerequisite for VECM | `statsmodels.tsa.stattools.coint` | Straightforward | Engle & Granger (1987) |
| 54 | **Johansen Cointegration Test** | Tests for multiple cointegrating vectors in a system of I(1) variables | Handles multivariate systems (e.g., indicator + target + controls); provides rank and cointegrating vectors | `statsmodels.tsa.vector_ar.vecm.coint_johansen` | Moderate | Johansen (1991) |
| 55 | **ARDL Bounds Test** | Tests for cointegration when variables have mixed orders of integration I(0)/I(1) | Useful when indicator is I(0) but target is I(1), or vice versa; avoids pre-testing pitfalls | `statsmodels` (manual), `ardl` | Moderate | Pesaran, Shin & Smith (2001) |
| 56 | **Phillips-Ouliaris Cointegration Test** | Residual-based cointegration test with improved power vs Engle-Granger | More robust to serial correlation in residuals than basic Engle-Granger | `arch.unitroot.PhillipsPerron`, custom | Moderate | Phillips & Ouliaris (1990) |
| 57 | **DOLS (Dynamic OLS)** | Estimates the cointegrating vector with leads and lags to correct for endogeneity | Provides efficient, median-unbiased estimates of the long-run equilibrium between indicator and target | `statsmodels` (manual OLS with leads/lags) | Moderate | Stock & Watson (1993) |
| 58 | **FMOLS (Fully Modified OLS)** | Non-parametric correction for serial correlation and endogeneity in cointegrating regression | Alternative to DOLS; better in small samples when dynamics are complex | Custom, `statsmodels` (limited) | Moderate | Phillips & Hansen (1990) |
| 59 | **Threshold Cointegration (TAR/M-TAR)** | Tests whether adjustment to equilibrium is asymmetric (faster in one direction) | Captures asymmetric correction — e.g., indicator-target spread adjusts faster when overshooting than undershooting | Custom implementation | Advanced | Enders & Siklos (2001) |

---

## 10. Network & Spillover

| # | Method | What It Does / When to Use | Relevance to Indicator-Target Analysis | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|---------------------------------------|----------------|------------|---------------|
| 60 | **Diebold-Yilmaz Spillover Index** | Measures total and directional volatility/return spillovers using VAR forecast error variance decomposition | Quantifies how much of the target's forecast error variance is explained by the indicator (and vice versa) | `statsmodels` (VAR FEVD), custom | Moderate | Diebold & Yilmaz (2012) |
| 61 | **Generalized FEVD (GFEVD)** | Order-invariant forecast error variance decomposition | Solves the Cholesky ordering problem in standard FEVD; gives symmetric spillover measures | `statsmodels` (custom from VAR), `networkx` for visualization | Moderate | Pesaran & Shin (1998) |
| 62 | **Granger Causality Network** | Constructs a directed network where edges represent significant Granger causality | Maps information flow among multiple indicators and targets; identifies hub indicators | `statsmodels` (pairwise Granger tests), `networkx` | Moderate | Billio et al. (2012) |
| 63 | **Partial Correlation Network** | Constructs undirected network of partial correlations (controls for all other variables) | Identifies direct vs. indirect indicator-target relationships in a multi-variable system | `sklearn.covariance.GraphicalLassoCV`, `networkx` | Moderate | — |
| 64 | **Connectedness Table** | Matrix summarizing pairwise directional spillovers with FROM/TO/NET rows/columns | Provides a compact summary of which indicators are net transmitters vs. receivers of shocks to targets | Custom from GFEVD output | Moderate | Diebold & Yilmaz (2014) |
| 65 | **Time-Varying Connectedness** | Rolling-window estimation of the Diebold-Yilmaz spillover index | Captures how indicator-target connectedness changes over time (e.g., spikes during crises) | Custom (rolling VAR + GFEVD) | Advanced | Antonakakis et al. (2020) |
| 66 | **Systemic Risk Measures (CoVaR, MES, SRISK)** | Measures contribution of one entity/asset to system-wide risk | Quantifies how an indicator's stress state contributes to tail risk in the target asset | Custom, `numpy`, `scipy` | Advanced | Adrian & Brunnermeier (2016) |

---

## 11. Factor Decomposition

| # | Method | What It Does / When to Use | Relevance to Indicator-Target Analysis | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|---------------------------------------|----------------|------------|---------------|
| 67 | **Principal Component Analysis (PCA)** | Extracts orthogonal latent factors from a panel of variables | Reduces dimensionality when using many indicators; first PC often captures common macro factor | `sklearn.decomposition.PCA` | Straightforward | Pearson (1901); Hotelling (1933) |
| 68 | **Factor Analysis (ML / MAP)** | Estimates latent factors with explicit factor loadings and unique variances | Provides interpretable factor loadings showing how each indicator loads onto common factors | `factor_analyzer`, `sklearn.decomposition.FactorAnalysis` | Moderate | — |
| 69 | **Sparse PCA** | PCA with L1 penalty to produce sparse (interpretable) factor loadings | Identifies which subset of indicators dominates each latent factor — more interpretable than standard PCA | `sklearn.decomposition.SparsePCA` | Moderate | Zou, Hastie & Tibshirani (2006) |
| 70 | **Independent Component Analysis (ICA)** | Finds statistically independent (not just uncorrelated) components | Separates non-Gaussian mixed signals; useful when indicator signals have non-normal distributions | `sklearn.decomposition.FastICA` | Moderate | Hyvarinen & Oja (2000) |
| 71 | **Gaussian Mixture Model (GMM) Clustering** | Fits a mixture of Gaussians to identify latent subpopulations | Identifies regime clusters in indicator-target space without imposing sequential (Markov) structure; threshold method T5 | `sklearn.mixture.GaussianMixture` | Moderate | McLachlan & Peel (2000) |
| 72 | **Jenks Natural Breaks** | Optimizes class boundaries by minimizing within-class variance and maximizing between-class variance | Data-driven threshold identification for indicator regimes; threshold method T4 | `jenkspy` | Straightforward | Jenks (1967) |
| 73 | **K-Means / Hierarchical Clustering** | Partitions observations into k clusters based on distance metrics | Groups indicator-target observations into regimes based on multiple features simultaneously | `sklearn.cluster.KMeans`, `scipy.cluster.hierarchy` | Straightforward | MacQueen (1967) |

---

## 12. Distributional & Higher-Moment

| # | Method | What It Does / When to Use | Relevance to Indicator-Target Analysis | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|---------------------------------------|----------------|------------|---------------|
| 74 | **CRPS (Continuous Ranked Probability Score)** | Scores probabilistic forecasts against realized outcomes | Evaluates the full distributional forecast quality — not just point forecast accuracy | `properscoring`, `scipy` | Moderate | Gneiting & Raftery (2007) |
| 75 | **Probability Integral Transform (PIT) Histogram** | Tests whether forecast CDF values are uniformly distributed (calibration check) | Verifies that indicator-based probability forecasts are well-calibrated across the distribution | `numpy`, custom | Straightforward | Diebold, Gunther & Tay (1998) |
| 76 | **Conditional Skewness Regression** | Regresses realized skewness of target returns on indicator levels | Tests whether an indicator predicts asymmetric risk (left tail vs right tail) in the target | `statsmodels`, custom | Moderate | Harvey & Siddique (1999) |
| 77 | **Conditional Kurtosis Analysis** | Analyzes how target return kurtosis varies with indicator state | Identifies whether indicator stress regimes are associated with fat-tailed target returns | `scipy.stats.kurtosis`, custom | Moderate | — |
| 78 | **Density Forecasting (KDE-based)** | Produces full conditional density forecasts using kernel methods | Provides richer information than point forecasts — shows how the entire return distribution shifts with indicator | `scipy.stats.gaussian_kde`, `sklearn.neighbors.KernelDensity` | Moderate | Amisano & Giacomini (2007) |
| 79 | **Expected Shortfall (CVaR) Regression** | Regresses expected shortfall of target on indicator values | Tests whether indicator predicts the severity of tail losses, not just their frequency | `numpy`, custom | Moderate | Rockafellar & Uryasev (2002) |
| 80 | **Quantile Crossing Test** | Tests whether indicator-based quantile forecasts violate monotonicity | Quality check for quantile regression models — ensures predicted quantiles don't cross | `statsmodels`, custom | Straightforward | Chernozhukov, Fernandez-Val & Galichon (2010) |
| 81 | **Berkowitz Test** | Likelihood ratio test for density forecast calibration | Formal statistical test of whether density forecasts match realized outcomes | Custom (LR test on transformed residuals) | Moderate | Berkowitz (2001) |

---

## 13. Forecast Evaluation

| # | Method | What It Does / When to Use | Relevance to Indicator-Target Analysis | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|---------------------------------------|----------------|------------|---------------|
| 82 | **Diebold-Mariano Test** | Tests whether two competing forecasts have equal predictive accuracy | Compares indicator-based forecast against benchmark (e.g., random walk, AR); formal significance test | `statsmodels` (custom), `arch` | Straightforward | Diebold & Mariano (1995) |
| 83 | **Clark-West Test** | Modified DM test for nested models; accounts for estimation error in larger model | Tests whether adding indicator variables significantly improves forecast over a parsimonious baseline | Custom (adjusted MSPE differential) | Moderate | Clark & West (2007) |
| 84 | **Giacomini-White Test** | Tests conditional predictive ability — allows comparison to depend on information set | Tests whether forecast superiority is conditional on market state (e.g., indicator only helps in stress) | Custom | Moderate | Giacomini & White (2006) |
| 85 | **Model Confidence Set (MCS)** | Identifies the set of "best" models from a collection, with confidence level | From a tournament of indicator-based strategies, determines which are statistically indistinguishable from the best | Custom, `arch` | Advanced | Hansen, Lunde & Nason (2011) |
| 86 | **CUSUM-based Forecast Monitoring** | Sequential monitoring of forecast performance for structural change | Detects in real-time when an indicator-based model's forecast quality deteriorates | `statsmodels.stats.diagnostic`, custom | Straightforward | Chu, Stinchcombe & White (1996) |
| 87 | **Encompassing Test** | Tests whether forecast A contains all information in forecast B | Determines whether indicator A's signal subsumes indicator B's signal (or vice versa) | `statsmodels` (OLS), custom | Straightforward | Harvey, Leybourne & Newbold (1998) |
| 88 | **Fluctuation Test for Forecast Breakdown** | Tests whether out-of-sample forecast performance is stable over time | Detects periods where the indicator-target relationship breaks down out-of-sample | Custom (rolling DM statistics) | Moderate | Giacomini & Rossi (2009) |

---

## 14. Liquidity & Microstructure

| # | Method | What It Does / When to Use | Relevance to Indicator-Target Analysis | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|---------------------------------------|----------------|------------|---------------|
| 89 | **Amihud Illiquidity Ratio** | Absolute daily return divided by daily dollar volume; measures price impact per unit of trading | Identifies whether target illiquidity amplifies indicator signals — thin markets may overreact to indicator changes | `numpy`, `pandas` | Straightforward | Amihud (2002) |
| 90 | **Roll Spread Estimator** | Estimates effective bid-ask spread from serial covariance of price changes | Proxy for transaction costs in the target asset; affects backtest realism and strategy net returns | `numpy` | Straightforward | Roll (1984) |
| 91 | **Kyle's Lambda** | Estimates price impact coefficient from regression of price change on signed volume | Measures information asymmetry in the target market; high lambda = indicators may be priced in slowly | Custom (OLS regression) | Moderate | Kyle (1985) |
| 92 | **Corwin-Schultz Spread** | Estimates bid-ask spread from daily high-low prices | Alternative spread estimator using only OHLC data; useful when tick data is unavailable | `numpy`, custom | Straightforward | Corwin & Schultz (2012) |
| 93 | **Volume-Synchronized Probability of Informed Trading (VPIN)** | Measures probability of informed trading using volume-bucketed analysis | Detects whether indicator information is being front-run by informed traders | Custom | Advanced | Easley, Lopez de Prado & O'Hara (2012) |
| 94 | **Turnover Rate Analysis** | Trading volume relative to shares outstanding over time | Identifies whether indicator signals coincide with elevated target trading activity (market attention) | `pandas` | Straightforward | — |
| 95 | **Hasbrouck Information Share** | Decomposes price discovery across multiple venues or related assets | For pairs where the indicator IS a traded asset (e.g., HY ETF, VIX futures), measures which leads in price discovery | Custom (VECM-based) | Advanced | Hasbrouck (1995) |

---

## Summary Statistics

| Category | Count | Complexity Distribution |
|----------|-------|------------------------|
| Correlation & Dependence | 10 | 3 straightforward, 4 moderate, 3 advanced |
| Lead-Lag & Causality | 7 | 1 straightforward, 1 moderate, 5 advanced |
| Regime Identification | 7 | 1 straightforward, 4 moderate, 2 advanced |
| Time-Series Modeling | 6 | 0 straightforward, 3 moderate, 3 advanced |
| Volatility & Risk | 6 | 1 straightforward, 2 moderate, 3 advanced |
| Nonlinear & ML | 5 | 0 straightforward, 3 moderate, 2 advanced |
| Signal Extraction | 6 | 3 straightforward, 2 moderate, 1 advanced |
| Event Study / Tail | 5 | 2 straightforward, 3 moderate, 0 advanced |
| Cointegration & Equilibrium | 7 | 1 straightforward, 5 moderate, 1 advanced |
| Network & Spillover | 7 | 0 straightforward, 5 moderate, 2 advanced |
| Factor Decomposition | 7 | 3 straightforward, 4 moderate, 0 advanced |
| Distributional & Higher-Moment | 8 | 2 straightforward, 5 moderate, 1 advanced (counted from entries above) |
| Forecast Evaluation | 7 | 3 straightforward, 3 moderate, 1 advanced |
| Liquidity & Microstructure | 7 | 4 straightforward, 1 moderate, 2 advanced |
| **Total** | **95** | **24 straightforward, 45 moderate, 26 advanced** |

---

## Recommended Prioritization

For maximum analytical value with manageable implementation effort, I would sequence the expansion as follows:

**Phase 1 — Quick wins (straightforward, high value):**
- Spearman/Kendall rank correlations (#1, #2)
- Rolling window correlation (#3)
- HP and CF filters (#42, #44)
- KDE for regime boundaries (#49)
- Quantile-based threshold rules (#50)

**Phase 2 — Core enhancements (moderate, fills major gaps):**
- VECM for cointegration (#25)
- Markov-Switching regression (#18)
- HMM for regime detection (#20)
- GJR-GARCH / EGARCH for asymmetric volatility (#31, #32)
- Change-point detection via `ruptures` (#23)
- Quantile regression (#40)
- Random Forest + SHAP (#37)

**Phase 3 — Advanced methods (high complexity, differentiated insights):**
- DCC-GARCH for time-varying correlation (#33)
- TVP-VAR for evolving transmission (#28)
- Transfer entropy for non-linear causality (#14)
- Wavelet coherence for multi-scale lead-lag (#15)
- Copula models with tail dependence (#5-9)
- EVT for tail risk (#48)

**Phase 4 — New categories (extends the toolkit for multi-indicator analysis):**
- Engle-Granger / Johansen cointegration (#53, #54) — essential for I(1) indicator-target pairs
- Diebold-Yilmaz spillover index (#60) — quantifies directional information flow
- PCA / Factor Analysis (#67, #68) — dimensionality reduction when using many indicators
- GMM clustering (#71) — data-driven regime identification (tournament threshold T5)
- Jenks natural breaks (#72) — alternative threshold method (tournament threshold T4)
- Diebold-Mariano test (#82) — formal forecast comparison
- CUSUM forecast monitoring (#86) — real-time model stability check (tournament threshold T7)
- Amihud illiquidity (#89) — target liquidity filter for backtest realism

---

## Appendix: Relevance Matrix

Maps indicator types to analysis categories. Scores: `++` core (run first), `+` useful (run if budget permits), `-` low priority, `--` not applicable.

| Indicator Type | 1. Corr | 2. Lead-Lag | 3. Regime | 4. TimeSeries | 5. Vol | 6. ML | 7. Signal | 8. Event/Tail | 9. Coint | 10. Network | 11. Factor | 12. Distrib | 13. FcstEval | 14. Liquidity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Credit Spread** (I19) | ++ | ++ | ++ | ++ | + | + | + | ++ | ++ | + | + | ++ | ++ | - |
| **Volatility/Options** (I22) | ++ | + | ++ | + | ++ | + | + | ++ | - | + | + | ++ | + | + |
| **Activity/Survey** (I1, I2, I3, I4, I6-I8) | + | ++ | + | ++ | - | ++ | + | + | + | + | ++ | + | ++ | - |
| **Yield Curve/Rates** (I17, I18) | + | ++ | + | ++ | - | + | ++ | + | ++ | - | + | + | ++ | - |
| **Sentiment/Flow** (I14, I15, I16) | ++ | + | + | - | + | + | + | + | - | + | ++ | + | + | ++ |
| **Cross-Asset** (I28, I30) | + | + | + | + | + | ++ | + | + | + | ++ | ++ | + | + | + |
| **Microstructure** (I20, I25, I27) | + | - | - | - | ++ | - | + | - | - | + | - | + | - | ++ |

### Fallback: Category Selection Heuristic

When the Relevance Matrix gives ambiguous guidance (multiple `+` categories), apply these rules in order:

**Rule A (Stationarity):** If both indicator and target are I(1) → prioritize Category 9 (Cointegration). If both are I(0) → skip Category 9.

**Rule B (Frequency):** If indicator is lower frequency than target (e.g., monthly indicator vs. daily target) → prioritize Categories 2 (Lead-Lag) and 7 (Signal Extraction) over Category 1 (Correlation).

**Rule C (Type):** Apply the indicator type row from the matrix above. Start with `++` categories, then add `+` until computational budget is reached.

**Rule D (Uncertainty):** If expected direction (from Analysis Brief) is `ambiguous` or `conditional` → add Category 3 (Regime) and Category 12 (Distributional) regardless of other scores.

**Worked examples:**
- **ISM Manufacturing PMI (I2) → SPY:** Activity/Survey type → Rule C: Lead-Lag (++), TimeSeries (++), ML (++), Factor (++), FcstEval (++) are core. Regime (+), Signal (+) are secondary. Start with Lead-Lag + TimeSeries.
- **VIX/VIX3M (I22) → TLT:** Volatility/Options type → Rule C: Corr (++), Regime (++), Vol (++), Event/Tail (++) are core. Rule D: expected direction is `conditional` (bearish for equity, bullish for bonds) → add Regime and Distributional. Start with Regime + Event/Tail.
- **HY-IG Spread (I19) → SPY:** Credit Spread type → Rule C: Corr (++), Lead-Lag (++), Regime (++), TimeSeries (++), Event/Tail (++), Coint (++), Distrib (++), FcstEval (++) are all core. Rule A: both I(1) → add Cointegration. Apply computational budget to subset.

---

### Sources

- [Engle (2002) — Dynamic Conditional Correlation](https://www.researchgate.net/publication/5000337_Dynamic_Conditional_Correlation_-_A_Simple_Class_of_Multivariate_GARCH_Models)
- [Oh & Patton (2013) — Time-Varying Copula for CDS Spreads](https://ideas.repec.org/p/duk/dukeec/13-30.html)
- [Credit Spreads, Leverage and Volatility: A Cointegration Approach](https://mdpi.com/2079-3197/10/9/155/htm)
- [Effective Transfer Entropy in Credit Markets](https://link.springer.com/article/10.1007/s10260-021-00614-1)
- [Transfer Entropy for Financial Applications (Open Quant Live Book)](https://bookdown.org/souzatharsis/open-quant-live-book/how-to-measure-statistical-causality-a-transfer-entropy-approach-with-financial-applications.html)
- [Ang & Bekaert (2002) — Regime Changes and Financial Markets (NBER)](https://www.nber.org/system/files/working_papers/w17182/w17182.pdf)
- [QuantStart — HMM for Market Regime Detection](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)
- [Predicting Equity Returns with TVP-VAR](https://www.sciencedirect.com/science/article/abs/pii/S1057521918307555)
- [FAVAR — Bernanke, Boivin & Eliasz](https://hoagiet.github.io/portfolio/portfolio-6/)
- [GARCH vs GJR-GARCH in Python](https://blog.quantinsti.com/garch-gjr-garch-volatility-forecasting-python/)
- [arch package — Volatility Modeling](https://arch.readthedocs.io/en/latest/univariate/univariate_volatility_modeling.html)
- [StochVolModels — Python SV implementation](https://github.com/ArturSepp/StochVolModels)
- [Credit Spread Approximation with Random Forest](https://www.researchgate.net/publication/352394963_Credit_spread_approximation_and_improvement_using_random_forest_regression)
- [XGBoost + SHAP for Sovereign Risk Determinants](https://www.sciencedirect.com/science/article/abs/pii/S1544612323006451)
- [Quantile Regression Forests — scikit-garden](https://scikit-garden.github.io/examples/QuantileRegressionForests/)
- [statsmodels — HP Filter](https://www.statsmodels.org/stable/generated/statsmodels.tsa.filters.hp_filter.hpfilter.html)
- [statsmodels — CF Filter](https://www.statsmodels.org/dev/generated/statsmodels.tsa.filters.cf_filter.cffilter.html)
- [statsmodels — BK Filter](https://www.statsmodels.org/stable/generated/statsmodels.tsa.filters.bk_filter.bkfilter.html)
- [ruptures — Change Point Detection](https://centre-borelli.github.io/ruptures-docs/)
- [PELT for Financial Time Series](https://dl.acm.org/doi/10.1145/3773365.3773532)
- [Wavelet Data Denoising for Finance](https://abouttrading.substack.com/p/financial-signal-processing-in-python-dd0)
- [Copula Tail Dependence](https://freakonometrics.hypotheses.org/2435)
- [pycop — Python Copula Package](https://pypi.org/project/pycop/)
- [copul — Python Copula Analysis](https://pypi.org/project/copul/)
- [KDE in Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/05.13-kernel-density-estimation.html)
- [Embrechts et al. — Dependence Modeling with Copulas](https://people.math.ethz.ch/~embrecht/ftp/copchapter.pdf)
- [statsmodels — VECM](https://www.statsmodels.org/dev/generated/statsmodels.tsa.vector_ar.vecm.VECM.html)
- [statsmodels — VAR/SVAR](https://www.statsmodels.org/stable/vector_ar.html)

---
*Generated: 2026-02-28 | Updated: 2026-03-14 | Source: Web research across academic papers, econometrics textbooks, and quant finance literature*
*Status: Reference catalog — methods selected per analysis based on data structure and research question. Multi-indicator framework expansion.*
