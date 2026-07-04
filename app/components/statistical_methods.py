"""Canonical single-source reference for the statistical methods used across the
AIG-RLIC+ portal.

This module is the DRY source of truth for the prose that describes every
statistical / econometric method genuinely used in the indicator->target
lead/lag research pipeline. Previously this prose was duplicated across the
Evidence method blocks (``method_theory`` / ``how_to_read`` fields) of the 14
``app/pair_configs/*_config.py`` files. Consolidating it here means the
Statistical Methods page (``app/pages/1_Statistical_Methods.py``) and any pair
page can render one authoritative, econometrically-vetted description per
method instead of re-authoring it per pair.

Scope discipline: this file records ONLY methods actually rendered somewhere in
the portal (Evidence blocks, Strategy/Confidence machinery, or Methodology
method tables). It is deliberately NOT a copy of the 95-method
``docs/econometric-methods-catalog.md`` catalog; it is the used-in-anger subset.

Design contract:
- Pure data + tiny helpers. NO Streamlit / pandas / plotting imports, so any
  page (or a test) can import it cheaply.
- ``METHODS`` is an ordered ``list[dict]``; each dict carries the three
  stakeholder-requested fields (``what_for``, ``why_applicable``,
  ``how_to_interpret``) plus display metadata.
- Claims are kept generic and correct (this is a reference page, not a
  pair-specific results page) -- no pair-specific numbers live here.

Field schema (every entry):
    slug              str  -- stable machine key (safe for anchors / dict keys)
    name              str  -- display name
    category          str  -- portal tier (see CATEGORIES)
    catalog_ref       str  -- cross-reference into econometric-methods-catalog.md
    what_for          str  -- the question the method answers / what it measures
    why_applicable    str  -- why it is the right tool for indicator->target
                              lead/lag work; states assumptions & when it applies
    how_to_interpret  str  -- how to read the output AND the honest caveats
                              (what a result does and does NOT prove)

Sources consolidated (best generic prose lifted and de-pair-specified from):
    app/pair_configs/gold_copper_xli_config.py  (10 Evidence blocks: CORRELATION,
        CORRELATION_LEAD_VIEW, LEAD_TOURNAMENT, GRANGER, CCF, REGIME, HMM,
        LOCAL_PROJECTIONS, QUANTILE_REGRESSION, TRANSFER_ENTROPY)
    app/pair_configs/indpro_spy_config.py        (RF_BLOCK; lead-view prose)
    app/pair_configs/phlxsox_spy_config.py       (INCREMENTAL_EDGE_BLOCK)
    app/pair_configs/hy_ig_spy_config.py         (_METHODS_TABLE_MD; CAVEATS_MD)
    app/pair_configs/ism_services_spy_config.py  (_METHODS_TABLE_MD; bootstrap /
        subperiod / structural-break prose)
    app/pair_configs/m2sl_yoy_spy_config.py      (bootstrap search-conditioned prose)
    app/pair_configs/indpro_xlp_config.py        (Johansen cointegration row)
Definitions cross-checked against docs/econometric-methods-catalog.md
    (#11 Toda-Yamamoto, #14 Transfer Entropy, #16 Pre-whitened CCF, #20 HMM,
     #30 Local Projections, #37 Random Forest, #40 Quantile Regression,
     #53/#54 Engle-Granger/Johansen cointegration).
"""

from __future__ import annotations

# Portal tiers, in render order. These match how the Evidence page groups
# methods (Level 1 basic / Level 2 advanced) plus the Strategy/Confidence
# validation family.
CATEGORIES: tuple[str, ...] = (
    "Level 1 — Basic",
    "Level 2 — Advanced",
    "Strategy validation",
)


METHODS: list[dict] = [
    # ------------------------------------------------------------------ #
    # Level 1 — Basic (descriptive / linear lead-lag first pass)
    # ------------------------------------------------------------------ #
    {
        "slug": "correlation_battery",
        "name": "Pearson Correlation Battery",
        "category": "Level 1 — Basic",
        "catalog_ref": "Catalog §1 (Correlation and Dependence)",
        "what_for": (
            "Measures the strength and direction of the linear relationship "
            "between an indicator-derived signal (z-score windows, percentile "
            "rank, rate-of-change) and the target's forward return, on a scale "
            "from -1 (perfectly opposing) to +1 (perfectly aligned). We test "
            "several signal transforms against several forward horizons "
            "(e.g. 5d / 21d / 63d / 126d, or 1m / 3m / 6m / 12m) and, where "
            "informative, complement Pearson with rank-based Spearman and "
            "Kendall (monotonic, outlier-robust) and distance correlation "
            "(sensitive to non-linear dependence)."
        ),
        "why_applicable": (
            "It is the honest first pass: cheap, assumption-light, and it fixes "
            "the sign of the relationship before any modelling. Pearson assumes "
            "an approximately linear, roughly homoskedastic (the scatter stays "
            "about the same width across the range) relationship, so the "
            "rank measures are run alongside it precisely because indicator->"
            "target links are often monotonic-but-non-linear or driven by a few "
            "extreme observations. It sets the directional prior the "
            "regime, tournament and information-theoretic tests then stress-test."
        ),
        "how_to_interpret": (
            "Read the sign first, magnitude second. A consistent negative column "
            "confirms a countercyclical link; positive, procyclical. Crucially, "
            "magnitude is easy to over-read: r ≈ 0.2 means the signal explains "
            "only r² ≈ 4% of the variation in returns (about 96% is left "
            "unexplained). A SMALL linear correlation does NOT "
            "rule out a profitable strategy -- if the signal's information lives "
            "in the tails or in a threshold regime, linear correlation "
            "(which weights calm and extreme days equally) will understate it. "
            "Correlation is association, not causation, and not predictive "
            "precedence -- it says nothing about which series moves first."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "correlation_heatmap",
            "caption": (
                "How to read this example: each cell is the correlation "
                "between one signal transform (row) and one forward-return "
                "horizon (column) — read the colour's SIGN first (one hue = "
                "countercyclical, the other = procyclical), its depth second. "
                "In this example pair most cells are pale, i.e. the linear "
                "links are weak (r ≈ 0.2 is only ~4% of return variance), so "
                "treat the map as fixing the direction, not as proof of a "
                "tradable edge — the tail/threshold tests come next."
            ),
        },
    },
    {
        "slug": "lead_correlation",
        "name": "Rolling / Lead Correlation",
        "category": "Level 1 — Basic",
        "catalog_ref": "Catalog §1–2 (Correlation; Lead-Lag)",
        "what_for": (
            "Answers the staleness question a rebalanced strategy actually faces: "
            "how far ahead does the indicator lead the target? The signal is "
            "shifted by lead L = 0…12 periods and correlated against a FIXED "
            "short forward return, tracing out at which lead predictive content "
            "peaks. A rolling-window variant instead recomputes correlation "
            "through time to expose regime dependence of the relationship."
        ),
        "why_applicable": (
            "A monthly-rebalanced rule does not need the best cumulative horizon; "
            "it needs to know how stale the signal may become before it is traded. "
            "That is a lead question, not a horizon question, and the lead grid "
            "answers it directly. Rolling correlation is the right tool when the "
            "relationship is suspected to be unstable -- a single full-sample "
            "number would average a strong regime and a dead one into a "
            "misleading middle."
        ),
        "how_to_interpret": (
            "On the lead grid, find the lead where correlation is strongest and "
            "check it is stable across neighbouring leads (a lone spike is likely "
            "noise; a broad plateau is a robust regime). A sign flip across leads "
            "signals a regime-/threshold-conditional relationship rather than a "
            "clean linear lead-lag. Honest caveat for daily pairs: a "
            "monthly-resampled lead grid is a comparability diagnostic, not the "
            "traded latency -- a daily rule may execute same-day (L0) even when "
            "the monthly grid peaks elsewhere, because monthly resampling discards "
            "the within-month reaction the daily rule monetises."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "correlations_lead_view",
            "caption": (
                "How to read this example: the curve is the correlation with a "
                "FIXED forward return as the signal is pushed back lead by lead "
                "(L = 0…12) — look for where it peaks and, more importantly, "
                "whether the peak is a broad plateau (a robust lead you can rely "
                "on) or a lone spike (likely noise). A sign flip across leads "
                "warns the relationship is regime-conditional, not a clean "
                "linear lead. For a daily pair the monthly grid is a "
                "comparability diagnostic, not the latency actually traded."
            ),
        },
    },
    {
        "slug": "lead_tournament",
        "name": "Lead Tournament",
        "category": "Level 1 — Basic",
        "catalog_ref": "Catalog §8 (Event/Threshold) + §13 (Forecast Evaluation)",
        "what_for": (
            "A grid search over the strategy design space -- signal transform × "
            "threshold rule × strategy family × orientation × lead × lookback -- "
            "scoring each combination by out-of-sample Sharpe and selecting the "
            "winner. The lead slice plots the best OOS Sharpe attainable at each "
            "lead against the buy-and-hold benchmark."
        ),
        "why_applicable": (
            "Linear correlation summarises the average relationship; the "
            "tournament finds the threshold-and-timing structure that a linear "
            "average misses. It is the right tool when the edge is believed to be "
            "regime-conditional -- the signal matters only once it crosses a tuned "
            "cutoff -- because it explicitly searches the non-linear activation "
            "rule rather than assuming a linear one."
        ),
        "how_to_interpret": (
            "A tall thin spike at one lead is a single lucky combination; a "
            "flat-but-wide cloud of high scores is a robust regime worth trusting. "
            "The dominant caveat is SEARCH-CONDITIONED bias: the winning Sharpe is "
            "the maximum over thousands of combinations, so it is optimistically "
            "biased by multiple testing / backtest overfitting. A tournament "
            "winner is a hypothesis to be validated (walk-forward, bootstrap, "
            "subperiod durability), NOT a confirmed edge -- headline performance "
            "marked `found_in_search` is search-phase OOS, not a fresh holdout "
            "exam."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "lead_sharpe_distribution",
            "caption": (
                "How to read this example: each point is the BEST out-of-sample "
                "Sharpe the grid search could find at that lead, with the "
                "buy-and-hold line for reference. Trust a flat-but-wide band of "
                "high scores (a robust regime) far more than a tall thin spike "
                "at one lead (one lucky combination). Remember every point is "
                "the max over thousands of combos, so it is search-conditioned "
                "and optimistically biased — read it as a hypothesis to be "
                "validated by walk-forward, not as a confirmed edge."
            ),
        },
    },
    {
        "slug": "granger_causality",
        "name": "Granger Causality (Toda-Yamamoto)",
        "category": "Level 1 — Basic",
        "catalog_ref": "Catalog §2 #11 (Toda-Yamamoto Granger)",
        "what_for": (
            "Tests whether past values of the indicator improve forecasts of the "
            "target's future return BEYOND what the target's own recent history "
            "already predicts, via F-tests on augmented regressions across a set "
            "of lags. The Toda-Yamamoto augmented-lag variant keeps the test "
            "valid even when the series are non-stationary or cointegrated, "
            "avoiding fragile unit-root pre-testing."
        ),
        "why_applicable": (
            "It is the formal, asymmetric lead-lag test: it distinguishes "
            "indicator->target predictive precedence from the reverse channel, "
            "which a symmetric correlation cannot. Running BOTH directions is the "
            "reverse-causality guard -- if the target Granger-causes the indicator "
            "more than vice versa, the apparent 'signal' may be an echo of the "
            "market itself."
        ),
        "how_to_interpret": (
            "A p-value below 0.05 at a lag means the indicator significantly "
            "improves the forecast at that lag (a result this strong would show "
            "up by chance less than 1 time in 20 if there were no real link); a "
            "cluster of significant lags "
            "supports a genuine lead. The essential caveat is in the name: "
            "'Granger causality' is PREDICTIVE PRECEDENCE, not economic causation "
            "-- both series can be driven by a common third factor. It is also a "
            "linear conditional-mean test, so it can miss threshold-activated or "
            "regime-conditional relationships that are real but non-linear; "
            "moderate Granger evidence alongside strong tournament/transfer-"
            "entropy evidence is the fingerprint of exactly that non-linearity."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "granger_f_by_lag",
            "caption": (
                "How to read this example: each bar is the Granger F-statistic "
                "at one lag — bars poking above the dashed significance line are "
                "lags where the indicator's past improves the target forecast "
                "beyond the target's own history (a link that strong would "
                "appear by chance under 1 time in 20). A CLUSTER of significant "
                "bars supports a genuine lead; one lone bar is weaker. Read it "
                "as predictive precedence, NOT economic cause — and because the "
                "test is linear it can miss real threshold-activated effects."
            ),
        },
    },
    {
        "slug": "prewhitened_ccf",
        "name": "Pre-Whitened Cross-Correlation (CCF)",
        "category": "Level 1 — Basic",
        "catalog_ref": "Catalog §2 #16 (CCF with Pre-whitening)",
        "what_for": (
            "Identifies the lead-lag timing structure between two series AFTER "
            "removing each series' tendency to move like its own recent past. "
            "Pre-whitening fits an autoregressive filter (e.g. AR(1)) to strip out "
            "self-memory; the cross-correlation of the residuals gives the cleaner "
            "picture of at which lag one series genuinely leads the other."
        ),
        "why_applicable": (
            "Rolling z-score signals are persistent by construction and equity "
            "returns have mild serial dependence, so a raw CCF shows non-zero "
            "correlation at many lags purely because each series remembers itself "
            "-- not because they interact. Pre-whitening is the standard fix for "
            "lead-lag analysis between persistent macro/financial series: it "
            "removes the autocorrelation that would otherwise manufacture spurious "
            "lead-lag bars."
        ),
        "how_to_interpret": (
            "Bars are the cross-correlation at each lag; negative lags = target "
            "leads signal, positive lags = signal leads target. Bars that poke "
            "past the ±1.96/√n dashed band (the standard rule-of-thumb "
            "noise threshold) are unlikely to be chance. A cluster of significant "
            "bars at small positive lags corroborates a short-horizon indicator->"
            "target lead. Caveat: even a correctly pre-whitened CCF is a bivariate, "
            "linear measure computed on a chosen (often in-sample) window; a small "
            "significant bar confirms a real but modest lead, not a large tradable "
            "effect on its own."
        ),
        "example": {
            "pair": "gold_copper_xli",
            "chart": "ccf_prewhitened",
            "caption": (
                "How to read this example: each bar is the cross-correlation at "
                "one lag AFTER stripping out each series' self-memory — negative "
                "lags mean the target leads, positive lags mean the signal "
                "leads. Only bars poking past the ±1.96/√n dashed band are "
                "unlikely to be chance; a cluster of them at small positive lags "
                "corroborates a short-horizon indicator→target lead. Even so, a "
                "small significant bar confirms a real but modest lead on a "
                "chosen window, not a large tradable effect by itself."
            ),
        },
    },

    # ------------------------------------------------------------------ #
    # Level 2 — Advanced (regime, dynamic, distributional, non-linear, ML)
    # ------------------------------------------------------------------ #
    {
        "slug": "regime_quartile",
        "name": "Regime / Quartile-Gradient Analysis",
        "category": "Level 2 — Advanced",
        "catalog_ref": "Catalog §3 (Regime Identification); §8 (Threshold)",
        "what_for": (
            "The simplest possible regime test: sort every observation into "
            "quartiles (or other buckets) of the indicator signal and compare the "
            "target's mean forward return in each bucket. It asks how different "
            "next-period returns look conditional only on 'which signal regime are "
            "we in today', with no model-imposed structure."
        ),
        "why_applicable": (
            "It is the assumption-light cross-check on model-based regime work "
            "(HMM) and the natural home for threshold effects that linear methods "
            "dilute. Because it imposes no functional form, a clean gradient here "
            "is hard-to-argue-with, model-free evidence; a broken gradient exposes "
            "a failure mode directly."
        ),
        "how_to_interpret": (
            "A monotonic gradient across buckets (returns rising or falling "
            "steadily from Q1 to Q4) confirms the directional hypothesis cleanly. "
            "A reversal at an extreme bucket (e.g. Q4 rebounding) is not noise to "
            "be smoothed over -- it is often the statistical fingerprint of a "
            "specific failure case (a period where the indicator was extreme for "
            "the 'wrong', non-risk reason). Caveats: bucket means are sensitive to "
            "sample composition, are in-sample descriptive statistics, and carry no "
            "standard error unless one is added -- treat the gradient as direction "
            "evidence, not as a calibrated forecast."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "regime_quartile_returns",
            "caption": (
                "How to read this example: each bar is the target's average "
                "forward return when the signal sat in that quartile (Q1 = "
                "lowest signal, Q4 = highest). A staircase that climbs or falls "
                "steadily Q1→Q4 is clean, model-free evidence for the "
                "directional hypothesis; a reversal at an extreme bucket (say Q4 "
                "rebounding) is usually a real failure-case fingerprint, not "
                "noise to smooth. These are in-sample bucket means with no error "
                "bars — read the gradient as direction, not a calibrated forecast."
            ),
        },
    },
    {
        "slug": "hmm_regime",
        "name": "Hidden Markov Model (HMM) Regime Identification",
        "category": "Level 2 — Advanced",
        "catalog_ref": "Catalog §3 #20 (Hidden Markov Model)",
        "what_for": (
            "Lets the data sort each date into one of a few unobservable states "
            "(e.g. 'calm' vs 'stress'). A 2-state HMM learns each state's mean and "
            "variance and how persistent (sticky) each state is, then reports the "
            "smoothed probability P(state | full data) that a given date belonged "
            "to each regime."
        ),
        "why_applicable": (
            "Regimes in financial series are latent -- you never observe a label, "
            "only returns and spreads -- which is exactly what an HMM is built for. "
            "It aggregates level, trend and volatility information into a single "
            "calibrated probability, and its learned transition matrix encodes how "
            "long regimes tend to last, giving an interpretable, sticky signal "
            "well suited to a scale-in/scale-out trading rule."
        ),
        "how_to_interpret": (
            "P(stress) near 1 means the model is confident the date is in the "
            "stress regime; near 0, calm. Validate by eye against known crisis "
            "windows -- stress probability SHOULD spike during documented "
            "episodes; if it does not, the state labels may be inverted or the fit "
            "poor. Note that separation is often by VARIANCE, not mean, so 'stress' "
            "means turbulence, not necessarily a lower average return. Caveats: HMM "
            "parameters are typically fitted IN-SAMPLE, so live use requires "
            "periodic re-estimation to avoid stale regime definitions; and the "
            "number of states is a modelling choice, not a fact."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "hmm_regime_probs",
            "caption": (
                "How to read this example: the line is the model's smoothed "
                "probability that each date sat in the 'stress' regime — near 1 "
                "the model is confident it was stress, near 0 calm. Sanity-check "
                "it by eye: the spikes SHOULD line up with documented crisis "
                "windows; if they don't, the state labels may be inverted. "
                "Separation is often by volatility not mean, so 'stress' means "
                "turbulence, not necessarily lower average returns — and the fit "
                "is in-sample, so live use needs periodic re-estimation."
            ),
        },
    },
    {
        "slug": "local_projections",
        "name": "Local Projections (Jordà)",
        "category": "Level 2 — Advanced",
        "catalog_ref": "Catalog §4 #30 (Local Projections)",
        "what_for": (
            "Traces the dynamic path of the target's response to a shock in the "
            "indicator: after the signal jumps by one standard deviation today, "
            "what is the cumulative target return at horizons 1, 5, 21, 63, 126 "
            "days? Each horizon is estimated by its own regression rather than by "
            "extrapolating one big model."
        ),
        "why_applicable": (
            "Local projections give robust impulse responses without imposing a "
            "full VAR's parameter restrictions, and they tolerate non-linearities "
            "and state dependence that a VAR-IRF would force into a single "
            "propagation mechanism. Because multi-day cumulative returns overlap, "
            "HAC (Newey-West) standard errors are used so the error bars stay "
            "honest under that overlap and under heteroskedasticity (error bars "
            "corrected for the fact that overlapping windows share data and that "
            "return scatter is uneven). The same "
            "machinery run in reverse (target -> indicator) is the mandatory "
            "reverse-causality diagnostic."
        ),
        "how_to_interpret": (
            "The line is the estimated cumulative response by horizon; the shaded "
            "band is the 95% HAC confidence interval. A band that stays on one side "
            "of zero is a statistically clear response; horizons where the band "
            "straddles zero are weak evidence. The SHAPE matters -- a response that "
            "builds to a peak then decays maps to the horizon a strategy should "
            "trade. Caveat: LP estimates a conditional-mean response on a chosen "
            "sample; wide bands at long horizons reflect genuine uncertainty from "
            "overlapping data, and a significant reverse-direction response is a "
            "feedback / reverse-causality flag, not a bonus signal."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "local_projections",
            "caption": (
                "How to read this example: the line traces the target's "
                "cumulative return at each horizon after the signal jumps one "
                "standard deviation today; the shaded band is the 95% HAC "
                "confidence interval. Horizons where the whole band sits on one "
                "side of zero are a statistically clear response — where it "
                "straddles zero the evidence is weak. The SHAPE points at the "
                "horizon to trade (build-then-decay). Wide bands far out are "
                "genuine uncertainty, and a significant reverse-direction "
                "response would be a feedback flag, not a bonus signal."
            ),
        },
    },
    {
        "slug": "quantile_regression",
        "name": "Quantile Regression",
        "category": "Level 2 — Advanced",
        "catalog_ref": "Catalog §6 #40 (Quantile Regression)",
        "what_for": (
            "Instead of asking how the indicator moves the AVERAGE target return, "
            "it fits a separate slope at different points of the outcome "
            "distribution -- the worst months (5th/10th percentile), the median, "
            "and the best months (90th/95th percentile). This reveals whether the "
            "signal bites harder in bad months than in typical ones."
        ),
        "why_applicable": (
            "Investors care most about the tails, and a single OLS slope collapses "
            "the whole distribution into one number that hides tail behaviour. "
            "Quantile regression is the right tool when the hypothesis is about "
            "CRASH RISK or asymmetry -- 'does a signal spike predict the 5th "
            "percentile of returns?' -- which is common for risk-off indicators "
            "whose value is downside management rather than upside capture."
        ),
        "how_to_interpret": (
            "Read the slopes left-to-right across outcome quantiles. Slopes that "
            "fan out -- steep and negative in the lower tail, flat at the median, "
            "possibly positive in the upper tail -- mean the signal governs the "
            "WIDTH of the outcome range, not the average. A larger absolute slope "
            "in the lower tail than the upper tail is downside asymmetry, which is "
            "what justifies a step-aside rule. This is the bridge that reconciles a "
            "weak average correlation with a strong tournament Sharpe: the signal "
            "lives in the tails. Caveat: tail-quantile estimates use fewer "
            "effective observations and so are noisier; and, like the others, this "
            "is predictive association, not proof of a causal channel."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "quantile_regression",
            "caption": (
                "How to read this example: each point is the signal's slope "
                "estimated at a different point of the outcome distribution — "
                "the bad months (5th/10th pct) on the left, the median in the "
                "middle, the best months (90th/95th) on the right. Slopes that "
                "fan out — steep and negative in the lower tail, flat at the "
                "median — mean the signal governs the WIDTH of outcomes, not the "
                "average; a bigger tail slope than upper slope is the downside "
                "asymmetry that justifies a step-aside rule. Tail estimates use "
                "fewer points, so they are noisier, and it is association not cause."
            ),
        },
    },
    {
        "slug": "transfer_entropy",
        "name": "Transfer Entropy",
        "category": "Level 2 — Advanced",
        "catalog_ref": "Catalog §2 #14 (Transfer Entropy)",
        "what_for": (
            "A model-free, information-theoretic measure of DIRECTED information "
            "flow: it asks whether knowing the indicator's past reduces "
            "uncertainty about the target's future, beyond what the target's own "
            "past already tells you -- without assuming any straight-line "
            "relationship. Computed both directions and compared to a shuffled "
            "null; the unit is bits."
        ),
        "why_applicable": (
            "It is the non-linear analogue of Granger causality. Where Granger "
            "tests a linear conditional expectation and dilutes a threshold-"
            "activated effect across all observations, transfer entropy discretises "
            "the series into bins and captures the joint distribution "
            "non-parametrically, detecting any pattern where certain signal bins "
            "co-occur with certain forward-return bins. That makes it the right "
            "robustness check precisely for the regime/threshold signals this "
            "research favours."
        ),
        "how_to_interpret": (
            "Compare TE(indicator -> target) against the upper 95% bound of a "
            "shuffle-based null distribution: a value well above the null with an "
            "empirical p near zero (a value this large almost never appears when "
            "the link is scrambled away) is significant directed information "
            "flow. The "
            "DESIRED pattern is the forward direction above the null AND the reverse "
            "direction (target -> indicator) indistinguishable from it. Caveats: TE "
            "estimates are sensitive to the binning scheme and need adequate sample "
            "size; magnitude in bits is not directly a trading return; and, as "
            "with Granger, directed predictive information is not proof of an "
            "economic causal mechanism."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "transfer_entropy",
            "caption": (
                "How to read this example: the two bars are the directed "
                "information flow (in bits) each way — indicator→target and "
                "target→indicator — against the shaded shuffle-based null band. "
                "The pattern you want is the forward bar poking clearly ABOVE "
                "the null (with an empirical p near zero) while the reverse bar "
                "sits INSIDE it, i.e. information runs one way. This is the "
                "non-linear cousin of Granger, so it catches threshold effects a "
                "linear test misses; but the size in bits is not a return, and "
                "directed information is still not proof of economic causation."
            ),
        },
    },
    {
        "slug": "random_forest_importance",
        "name": "Random Forest Feature Importance",
        "category": "Level 2 — Advanced",
        "catalog_ref": "Catalog §6 #37 (Random Forest + SHAP)",
        "what_for": (
            "An ensemble-tree cross-check: a Random Forest classifier is "
            "walk-forward-validated across rolling train/test windows to predict "
            "the sign of the target's forward return, and feature importances are "
            "averaged across windows to rank which indicator transforms are most "
            "informative."
        ),
        "why_applicable": (
            "It is a non-linear, interaction-aware second opinion on which "
            "transforms carry signal, free of the linear-form assumptions of "
            "correlation and Granger. Walk-forward validation (rather than a single "
            "in-sample fit) is used so the importance ranking reflects genuine "
            "out-of-sample informativeness, not in-sample memorisation. It is a "
            "cross-check on the econometric pipeline, not a replacement for it."
        ),
        "how_to_interpret": (
            "Longer bars = more informative features averaged across windows; read "
            "which family (momentum, z-score, level) rises to the top. Judge the "
            "model against the honest 50% coin-flip baseline: walk-forward accuracy "
            "modestly above 50% is a real but weak edge, and consistency with the "
            "tournament's winning transform family is the reassuring signal. "
            "Caveats: importance measures can be inflated for high-cardinality / "
            "correlated features, they rank relevance without giving direction or a "
            "tradable rule, and a high in-sample accuracy that does not survive "
            "walk-forward is overfitting."
        ),
        "example": {
            "pair": "indpro_spy",
            "chart": "rf_importance",
            "caption": (
                "How to read this example: each bar is one indicator transform's "
                "importance, averaged across the walk-forward windows — the "
                "longer the bar, the more that feature helped the forest predict "
                "the target's next-period sign out-of-sample. Read which FAMILY "
                "(momentum, z-score, level) rises to the top and check it agrees "
                "with the tournament's winning transform. Judge accuracy against "
                "the honest 50% coin-flip: modestly above is a real but weak edge. "
                "Importances can inflate for correlated features and give no "
                "direction or tradable rule — this is a cross-check, not a signal."
            ),
        },
    },

    # ------------------------------------------------------------------ #
    # Strategy validation (does the searched edge survive scrutiny?)
    # ------------------------------------------------------------------ #
    {
        "slug": "walk_forward",
        "name": "Walk-Forward / Out-of-Sample Validation",
        "category": "Strategy validation",
        "catalog_ref": "Catalog §13 (Forecast Evaluation)",
        "what_for": (
            "Re-estimates and evaluates the strategy on data it never saw during "
            "fitting: the model is trained on an early window and scored on a "
            "later window (often rolled forward across several successive "
            "train/test splits). Reported Sharpe, return and drawdown are the "
            "out-of-sample (OOS) figures."
        ),
        "why_applicable": (
            "Any tournament winner is selected by maximising over many "
            "combinations, so its in-sample performance is optimistically biased. "
            "Walk-forward validation is the primary defence against backtest "
            "overfitting: it measures whether the rule keeps working after the "
            "search, which is the only performance figure a user should lean on."
        ),
        "how_to_interpret": (
            "Prefer OOS metrics to in-sample ones, and weight the LONGEST available "
            "OOS window most -- short OOS periods (< ~5 years) contain few complete "
            "market cycles and systematically INFLATE apparent Sharpe. A rule whose "
            "edge collapses out-of-sample was an artefact of the search. Remember "
            "all figures are simulated (no market impact, assumed transaction "
            "costs), and search-phase OOS is still weaker evidence than a fresh, "
            "never-touched holdout exam."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "walk_forward",
            "caption": (
                "How to read this example: the curve is the strategy's "
                "performance ONLY on data it never saw while fitting — each "
                "segment was scored on a window held out after training on the "
                "earlier one. This is the figure to lean on, not the in-sample "
                "backtest: a rule whose edge holds up here survived the search, "
                "one whose edge collapses was an artefact of it. Weight the "
                "LONGEST out-of-sample stretch most (short <5yr windows inflate "
                "Sharpe), and remember all figures are simulated (no market impact)."
            ),
        },
    },
    {
        "slug": "bootstrap_significance",
        "name": "Bootstrap Significance Test",
        "category": "Strategy validation",
        "catalog_ref": "Catalog §13 (Forecast Evaluation) / deflated Sharpe",
        "what_for": (
            "Puts a p-value on the winning strategy's performance by resampling "
            "the return series many times to build an empirical distribution of "
            "the performance statistic under the null of no edge, then locating the "
            "observed statistic within it."
        ),
        "why_applicable": (
            "Sharpe ratios are noisy and non-normal, so a point estimate alone "
            "cannot say whether an edge is real. Bootstrapping makes minimal "
            "distributional assumptions and is the natural way to attach "
            "uncertainty to a backtest statistic when analytic standard errors are "
            "unreliable."
        ),
        "how_to_interpret": (
            "A bootstrap p below 0.05 means the performance is unlikely under the "
            "no-edge null; p around 0.07 is suggestive but not significant. The "
            "decisive honesty point: when the strategy was chosen by a large grid "
            "search, the bootstrap p is SEARCH-CONDITIONED -- it does not correct "
            "for the multiple comparisons that produced the winner, so it is not a "
            "fresh confirmation. Read it together with a deflated-Sharpe / "
            "specification-curve mindset (methods that discount the winner for how "
            "many candidates were tried, and that show where it sits among all "
            "of them): clearing the 5% bar on a search-selected "
            "winner is necessary, not sufficient."
        ),
        # No standalone bootstrap-distribution chart is produced for any pair
        # (the bootstrap p-value is reported inline in Strategy/Confidence text,
        # not as a JSON figure). Rather than leave ``example`` as None (which the
        # renderer can't display), we keep the dict shape with null pair/chart so
        # the page shows a caption-only note and no broken embed.
        "example": {
            "pair": None,
            "chart": None,
            "caption": (
                "How to read this example: there is no standalone figure for the "
                "bootstrap test — its p-value is reported inline on each "
                "Strategy/Confidence page rather than as a chart. To SEE "
                "out-of-sample robustness visually, look instead at the "
                "Walk-Forward example (performance on data never fitted on) and "
                "the Subperiod example (Sharpe across economic episodes). Note "
                "the bootstrap p on a search-selected winner is "
                "search-conditioned: clearing 5% is necessary, not sufficient."
            ),
        },
    },
    {
        "slug": "subperiod_durability",
        "name": "Subperiod / Durability Analysis",
        "category": "Strategy validation",
        "catalog_ref": "Catalog §13 (Forecast Evaluation); §3 (Regime)",
        "what_for": (
            "Splits the sample into economic sub-periods or episodes (e.g. GFC, "
            "the 2010s expansion, COVID, the 2022 rate shock) and reports the "
            "strategy's Sharpe within each, testing whether the edge is broad-based "
            "or concentrated in one lucky window."
        ),
        "why_applicable": (
            "A single full-sample Sharpe can be carried by one extraordinary "
            "episode. Subperiod analysis is the durability/overfit guard: it "
            "distinguishes a relationship that is stable across regimes from one "
            "that is `episode_concentrated`, which is exactly the fragility a "
            "search can accidentally reward."
        ),
        "how_to_interpret": (
            "Positive, similar Sharpe across most sub-periods is durable evidence; "
            "performance that lives in one episode and disappears elsewhere is a "
            "concentration warning to be labelled, not buried. Use it to set "
            "confidence: an `episode_concentrated` durability tag should pull the "
            "overall confidence rating down regardless of a strong headline number. "
            "Caveat: sub-period Sharpes are computed on ever-shorter windows and so "
            "are individually noisier -- read the pattern across episodes, not any "
            "one cell."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "subperiod_sharpe",
            "caption": (
                "How to read this example: each bar is the strategy's Sharpe "
                "inside one economic episode (GFC, 2010s expansion, COVID, the "
                "2022 rate shock). Bars that are positive and SIMILAR height "
                "across most episodes are a durable edge; a single tall bar with "
                "the rest near zero is a concentration warning — the edge lived "
                "in one lucky window and should pull the confidence rating down "
                "however strong the headline number. Each bar is a short, "
                "individually noisy window, so read the pattern, not any one cell."
            ),
        },
    },
    {
        "slug": "structural_break_cointegration",
        "name": "Structural-Break & Cointegration Checks",
        "category": "Strategy validation",
        "catalog_ref": "Catalog §9 #53–54 (Engle-Granger, Johansen); break tests",
        "what_for": (
            "Two situational stability tests. Structural-break / change-point "
            "detection (e.g. a break flagged at a date, or PELT change-points) asks "
            "whether the indicator->target relationship shifted at some point in "
            "history. Cointegration tests (Engle-Granger two-step, Johansen) ask "
            "whether the indicator and target levels share a long-run equilibrium "
            "they revert toward."
        ),
        "why_applicable": (
            "These are applied conditionally, not to every pair. Structural-break "
            "testing matters whenever the relationship is suspected to be "
            "non-stationary in time -- a break invalidates a model estimated as if "
            "the world were constant. Cointegration is the right (and only "
            "appropriate) test when BOTH series are integrated of order one, I(1) "
            "(each series wanders like a random walk on its own, but a "
            "combination of the two stays anchored): it is the prerequisite for an "
            "error-correction view (a model where the two levels are pulled back "
            "toward their shared trend) and guards against "
            "spurious regression between two trending levels. Both are stability / "
            "durability guards rather than headline signals."
        ),
        "how_to_interpret": (
            "A detected structural break means subsample analysis is required and "
            "any full-sample statistic should be read with caution around the break "
            "date. A significant cointegration test says a long-run tie exists "
            "(supporting an equilibrium-reversion interpretation); an insignificant "
            "one does NOT mean 'no relationship' -- it only means no LEVELS "
            "equilibrium, and a short-horizon return-predictability edge can still "
            "exist. Caveats: cointegration tests have low power in short samples "
            "and are meaningless for I(0) pairs; break tests can over-flag on noisy "
            "series. Treat both as context that qualifies confidence, not as the "
            "trading signal itself."
        ),
        "example": {
            "pair": "hy_ig_spy",
            "chart": "structural_break",
            "caption": (
                "How to read this example: the series is the indicator→target "
                "relationship through time with the detected change-point(s) "
                "marked by a vertical line — those dates flag where the link may "
                "have STRUCTURALLY shifted, meaning any full-sample statistic "
                "spanning the break should be read with caution and subsample "
                "analysis is warranted. Break tests can over-flag on noisy "
                "series, and the companion cointegration check is a separate, "
                "conditional question (do the two levels share a long-run "
                "equilibrium?) — both qualify confidence, they aren't the signal."
            ),
        },
    },
]


def methods_by_category() -> "dict[str, list[dict]]":
    """Return METHODS grouped by category, preserving CATEGORIES order and the
    within-category order of METHODS.

    The returned mapping is ordered: iterating it yields categories in the
    canonical CATEGORIES sequence, and only categories that actually have
    methods are included. This is the render-friendly grouping a page uses to
    lay out one section per tier.
    """
    grouped: dict[str, list[dict]] = {cat: [] for cat in CATEGORIES}
    for method in METHODS:
        grouped.setdefault(method["category"], []).append(method)
    # Drop empty categories while keeping canonical order.
    return {cat: items for cat, items in grouped.items() if items}


def method_by_slug(slug: str) -> "dict | None":
    """Return the single method dict with the given slug, or None if absent."""
    for method in METHODS:
        if method["slug"] == slug:
            return method
    return None


# Field keys every METHODS entry is guaranteed to carry (documents the schema
# for consumers and enables a cheap integrity check in tests / at import).
REQUIRED_FIELDS: tuple[str, ...] = (
    "slug",
    "name",
    "category",
    "catalog_ref",
    "what_for",
    "why_applicable",
    "how_to_interpret",
)
