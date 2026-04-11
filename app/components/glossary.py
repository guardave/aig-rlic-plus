"""Glossary definitions extracted from portal_narrative_hy_ig_spy_20260228.md."""

GLOSSARY: dict[str, str] = {
    "Basis point (bp)": (
        "One hundredth of a percentage point. 1 bp = 0.01%, 100 bps = 1%, "
        "and 10,000 bps = 100%. "
        "Why it matters: yields, spreads, and fees in fixed income often move "
        "in fractions of a percent, so rounding to whole percentages loses "
        "meaningful information -- a 25 bp rate cut (0.25%) and a 50 bp cut "
        "(0.50%) are very different policy actions. Using bps also avoids the "
        "'percentage of a percentage' confusion when a yield rises from 4% to "
        "5%: that is a 100 bp increase, not a 25% increase (even though "
        "5/4 - 1 = 25%). "
        "Example: when the HY-IG spread moves from 400 bps to 800 bps, it has "
        "widened by 400 bps (4 percentage points), doubling the extra yield "
        "investors demand for holding risky debt. Conversion: divide bps by "
        "100 to get percent, or multiply percent by 100 to get bps."
    ),
    "Buy-and-hold": (
        "An investment strategy where you purchase an asset and hold it regardless of "
        "market conditions. The simplest benchmark for comparing active strategies."
    ),
    "Credit rating": (
        "A grade assigned to a company's debt by rating agencies (S&P, Moody's, Fitch). "
        "Investment grade (AAA to BBB-) means lower default risk; high yield (BB+ and below) "
        "means higher default risk."
    ),
    "Credit spread": (
        "The difference in yield between a risky bond and a risk-free benchmark. "
        "Wider spreads indicate more perceived risk."
    ),
    "Drawdown": (
        "The peak-to-trough decline in the value of a portfolio or index. "
        "Maximum drawdown is the largest such decline in a given period."
    ),
    "Excess bond premium (EBP)": (
        "The component of credit spreads that cannot be explained by expected default risk. "
        "Captures investor sentiment and risk appetite. Proposed by Gilchrist & Zakrajsek (2012)."
    ),
    "Forward return": (
        "The return over a future period. A '21-day forward return' is the percentage change "
        "in price over the next 21 trading days (~1 month)."
    ),
    "Granger causality": (
        "A statistical test that determines whether one time series helps predict another. "
        "'X Granger-causes Y' means past values of X improve forecasts of Y. "
        "It does not prove true causation."
    ),
    "Hidden Markov Model (HMM)": (
        "A statistical model that assumes the system is in one of several unobservable "
        "('hidden') states, each with different statistical properties. The model estimates "
        "which state the market is in at any given time."
    ),
    "High-yield bonds (junk bonds)": (
        "Bonds from companies with credit ratings below investment grade (BB+ or lower). "
        "They offer higher yields to compensate for higher default risk."
    ),
    "HY-IG spread": (
        "The difference between the option-adjusted spread on high-yield bonds and the "
        "option-adjusted spread on investment-grade bonds. Our primary signal variable."
    ),
    "Impulse response": (
        "A measure of how one variable responds over time to a one-time shock in another "
        "variable. Shows whether effects are immediate, delayed, or persistent."
    ),
    "In-sample / Out-of-sample": (
        "In-sample data is used to build and fit models. Out-of-sample data is held back "
        "and used to test whether the model works on data it has never seen."
    ),
    "Investment-grade bonds": (
        "Bonds from companies with credit ratings of BBB- or above. Considered safer, "
        "with lower yields."
    ),
    "Local projection": (
        "A method for estimating impulse responses that does not require specifying a full "
        "multivariate model. More robust than traditional VAR methods. Developed by Jorda (2005)."
    ),
    "Markov-switching model": (
        "A model where the underlying regime (e.g., bull vs. bear market) can change randomly "
        "according to a Markov process. Each regime has its own set of parameters. "
        "Developed by Hamilton (1989)."
    ),
    "NFCI": (
        "National Financial Conditions Index, published weekly by the Chicago Federal Reserve. "
        "Measures overall conditions in U.S. financial markets. Positive values indicate "
        "tighter-than-average conditions."
    ),
    "Option-adjusted spread (OAS)": (
        "A credit spread that accounts for any embedded options (like call provisions) in the bond. "
        "Provides a cleaner measure of pure credit risk than raw yield spreads."
    ),
    "Quantile regression": (
        "A variant of regression analysis that estimates how a predictor affects "
        "**different percentiles** of the outcome distribution, not just the average. "
        "Why it matters: standard regression tells you the effect on an average day, "
        "but financial risk is about bad days -- quantile regression lets us say "
        "'this signal predicts losses in the worst 5% of days, not just average losses.' "
        "Example: if we find that wider credit spreads have a coefficient of -0.01 at "
        "the 5% quantile but 0.00 at the median, it means spreads warn of tail risk "
        "without predicting normal-day moves -- a fire alarm, not a return forecast. "
        "Formula: minimize the tilted absolute loss sum rho_tau(y - X*beta), where "
        "rho_tau penalises positive and negative residuals asymmetrically so that the "
        "fitted line passes through the tau-th percentile of the conditional distribution."
    ),
    "Regime": (
        "A distinct state of the market characterized by its own statistical properties "
        "(mean returns, volatility, correlations). Markets switch between regimes over time."
    ),
    "Sharpe ratio": (
        "A measure of risk-adjusted return: (return - risk-free rate) / volatility. "
        "Higher is better. A Sharpe of 1.0 is generally considered good."
    ),
    "Transfer entropy": (
        "An information-theoretic measure of directed information flow between two time "
        "series, measured in nats (natural-log units of information). It answers: how "
        "much does knowing X's past reduce our uncertainty about Y's next value, over "
        "and above what we already learn from Y's own past? "
        "Why it matters: Granger causality is a linear test -- it only sees relationships "
        "that show up in conditional means. Transfer entropy is non-parametric and sees "
        "the full conditional distribution, so it captures threshold effects, regime "
        "switches, and tail dependencies that linear tests miss entirely. For credit-equity "
        "data, where the signal operates through nonlinearities, TE often finds information "
        "flow that Granger tests understate. "
        "Example: for HY-IG spreads and SPY returns, credit-to-equity transfer entropy is "
        "0.042 nats (p=0.004) while equity-to-credit is 0.0055 nats (p=0.050) -- roughly "
        "7.6x more information flows from credit to equity than the reverse, which would "
        "not show up in a linear Granger test on the same data. "
        "Formula: TE(X->Y) = H(Y_t+1 | Y_t) - H(Y_t+1 | Y_t, X_t), where H is Shannon entropy."
    ),
    "Cross-correlation function (CCF)": (
        "A statistical tool that measures how strongly two time series co-move at "
        "**different time offsets** -- lag 0 is contemporaneous, negative lags ask whether "
        "series A leads series B by that many periods, positive lags ask the reverse. "
        "The output is a chart of correlations against lag, bounded between -1 and +1. "
        "Why it matters: a plain correlation tells you whether two series move together, "
        "but not which one moves first. CCF is the simplest way to diagnose lead-lag "
        "structure, which is the foundation of any predictive signal. "
        "Example: if the CCF between credit spreads and SPY shows the largest negative "
        "bar at lag -17 (SPY leading the spread by 17 days), it says equity moves first "
        "at that horizon and credit follows -- the opposite of a naive 'credit leads' "
        "story. CCFs on raw financial data are prone to spurious signals because of "
        "autocorrelation, which is why we always use the pre-whitened variant. "
        "Formula: rho_XY(k) = Cov(X_t, Y_t+k) / (sigma_X * sigma_Y), evaluated at each "
        "integer lag k."
    ),
    "Pre-whitening": (
        "A pre-processing step applied before running a cross-correlation function: "
        "fit an ARIMA model to each series, extract the residuals (which are "
        "approximately white noise by construction), and run the CCF on those residuals "
        "instead of the raw data. "
        "Why it matters: raw financial series are strongly autocorrelated -- today's "
        "spread looks a lot like yesterday's spread -- and a raw CCF inherits that "
        "self-memory from both sides, producing 'significant' cross-correlations even "
        "when no genuine dynamic relationship exists. Pre-whitening strips out the "
        "self-memory so that surviving correlations reflect only the true dynamic link "
        "between the two series. Without it, CCF results on financial data are almost "
        "always misleading. "
        "Example: an unfiltered CCF on the HY-IG spread and SPY would show significant "
        "bars at almost every lag (dominated by each series' own persistence). After "
        "pre-whitening with ARIMA(2,0,2), only 15 of 41 lags remain significant -- and "
        "those 15 are the ones that actually matter. "
        "Convention: the ARIMA order is usually selected by BIC grid search, and the "
        "same order is applied to both series so neither side gets a filter the other "
        "does not."
    ),
    "VIX": (
        "The CBOE Volatility Index, often called the 'fear gauge.' Measures the market's "
        "expectation of 30-day volatility in the S&P 500, derived from option prices."
    ),
    "VIX term structure": (
        "The difference between longer-dated (VIX3M, 3-month) and shorter-dated (VIX, 1-month) "
        "implied volatility. When VIX3M > VIX (contango), markets are calm. When VIX > VIX3M "
        "(backwardation), markets are stressed."
    ),
    "Walk-forward validation": (
        "A backtesting method that simulates real-time trading by training the model on past "
        "data and testing on subsequent data, then rolling the window forward. Prevents "
        "lookahead bias."
    ),
    "Yield curve slope": (
        "The difference between long-term and short-term interest rates (e.g., 10-year minus "
        "3-month Treasury yields). An inverted yield curve (negative slope) has historically "
        "preceded recessions."
    ),
    "Z-score": (
        "A statistical measure of how many standard deviations a value is from its mean. "
        "A z-score of 2 means the value is 2 standard deviations above average -- an unusual reading."
    ),
}
