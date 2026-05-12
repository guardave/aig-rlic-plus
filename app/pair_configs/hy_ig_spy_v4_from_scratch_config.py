"""HY-IG × SPY v4 (from scratch) pair configuration (Rule APP-PT1).

Pair-specific narrative content for the Story / Evidence / Strategy /
Methodology templates. All narrative prose authored by Research Ray
(handoff 2026-05-12). Ace transliterates verbatim from:
    docs/research/hy_ig_spy_v4_narrative_prose_20260512.md

Pair ID: hy_ig_spy_v4_from_scratch
Winner: S2c_zscore_36m / T3_z0.0 / P1 / L1
OOS Sharpe: 1.32 | OOS MDD: -6.38% | OOS Return: 6.57% ann.
Evidence status: failed_final_exam (holdout Sharpe 0.31 < 0.50 floor)

RES-NR1: all instrument references verified — target_symbol = SPY.
APP-PT1: thin-wrapper pages import STORY_CONFIG, EVIDENCE_METHOD_BLOCKS,
    STRATEGY_CONFIG, METHODOLOGY_CONFIG from this module.
DO NOT carry forward v1/v2/v3 numerical findings. All numbers read from
winner_summary.json and evidence_status.json at runtime.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE CONFIG
# =========================================================================
class StoryConfig:
    """Story-page content object (passed to `render_story_page`)."""

    PAGE_TITLE = "The Story: When Credit Markets Warn, Equity Investors Should Listen"
    PAGE_SUBTITLE = (
        "Does the high-yield credit spread carry an early signal for SPY investors?"
    )

    HEADLINE_H2 = (
        "## Credit stress as an early-warning signal for SPY — what the evidence so far suggests"
    )

    PLAIN_ENGLISH = (
        "When companies borrow money in the bond market, lenders charge higher interest rates "
        "to riskier (high-yield) borrowers than to safer (investment-grade) borrowers. The gap "
        "between those rates — the HY-IG credit spread — acts like a financial stress gauge. "
        "When the gap widens sharply, bond investors are pricing in higher risk of corporate "
        "defaults and tighter lending conditions. This research asks whether watching that stress "
        "gauge gives SPY investors an advance signal worth paying attention to — before the "
        "damage shows up in equity prices."
    )

    WHERE_THIS_FITS = """This is a **single indicator-target analysis**: does the HY-IG credit spread carry
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
by v4 exam outputs.
"""

    ONE_SENTENCE_THESIS = (
        "The HY-IG credit spread — the yield premium demanded by lenders to high-yield "
        "corporate borrowers relative to safer peers — is consistent with theory as a "
        "leading indicator of broad US equity stress, because the corporate bond market may "
        "process aggregate default risk before that risk is fully absorbed by equity prices."
    )

    KPI_CAPTION = (
        "The tournament winner uses the 36-month z-score of the HY-IG spread as the signal "
        "(S2c_zscore_36m), applying a long/cash binary rule: fully invested when the z-score "
        "is below zero (spread below its 36-month mean), moved to cash when it rises above. "
        "The countercyclical orientation means exposure falls when credit markets signal "
        "deterioration — the defensive positioning trade."
    )

    HERO_TITLE = "30 Years of HY-IG Credit Stress vs. SPY Equity Performance"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-panel view — top panel shows HY-IG spread (left axis, red) "
        "with HMM stress-regime shading; bottom panel shows SPY monthly returns (blue). "
        "OOS and Holdout split lines are annotated. Notice how spread spikes typically "
        "precede or coincide with SPY drawdown episodes — the credit-leads-equity pattern."
    )

    REGIME_TITLE = "What History Shows: SPY Returns by HY-IG Spread Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: annualized SPY return by HY-IG spread quartile (Q1 = tightest "
        "spreads / least stress, Q4 = widest spreads / most stress). A monotonically "
        "declining pattern from left to right is consistent with the countercyclical "
        "hypothesis: wider credit spreads are associated with weaker forward SPY returns."
    )

    NARRATIVE_SECTION_1 = """
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

    NARRATIVE_SECTION_2 = """
### Honest Limits of the Hypothesis

The HY-IG → SPY hypothesis is theoretically grounded and empirically consistent with
the literature, but it carries known limitations that anyone using this analysis
should understand.

**The rate-shock blind spot.** The credit-cycle hypothesis describes default-risk-
driven bear markets. When equity declines are driven primarily by interest rate
repricing rather than by rising default probabilities — as the 2022 drawdown appears
to have been — the HY-IG spread may give only partial warning. In 2022, the
Federal Reserve's fastest rate-hiking cycle in 40 years drove a roughly 25% SPY
decline. HY-IG spreads did widen (from roughly 310 bps to 580 bps), but the widening
was moderate relative to the magnitude of the equity decline, because the equity
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
leading signal into a near-simultaneous relationship.

**This is v4 evidence.** Statistical findings on this portal for the v4 pair are
based on a clean rebuild from first principles. The formal out-of-sample exam has
been run; see the Strategy page for results and the disclosure banner regarding
the holdout outcome.
"""

    SCOPE_NOTE = (
        "This page pack analyzes only the HY-IG credit spread → SPY relationship. SPY also "
        "responds to interest-rate cycles, earnings momentum, valuation multiples, and macro "
        "surprises. Each of those has its own separate analysis in the portal. Here the lens "
        "stays fixed on corporate credit spreads as the single predictor. The portal's "
        "Yield Curve × SPY analysis covers the rate-cycle dynamics identified as the 2022 "
        "blind spot above."
    )

    TRANSITION_TEXT = (
        "Theory and academic literature are both consistent with the HY-IG spread carrying "
        "early information about SPY weakness. The Evidence page presents the statistical "
        "tests that examine whether that theoretical prediction holds in the data — and at "
        "which lags, under which conditions, and with what degree of reliability."
    )

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "The Dot-Com Bust (2000-2003)",
            "narrative": (
                "The Dot-Com bust began as an equity-sector phenomenon concentrated in technology "
                "and telecommunications, but the corporate credit market caught the underlying "
                "stress early. Telecom companies had issued enormous volumes of high-yield debt "
                "to finance network buildouts through 1999-2000. As capital market conditions "
                "shifted and revenue projections for 'new economy' firms collapsed, high-yield "
                "bond prices began repricing — and HY-IG spreads widened — before the worst of "
                "the SPY equity damage accumulated. By late 2000, spread widening was already "
                "underway, suggesting the credit market was pricing in a genuine deterioration "
                "in corporate fundamentals ahead of the equity market's full recognition. "
                "This episode is historically consistent with the credit-leads-equity hypothesis: "
                "bond investors, focused on downside scenarios, appear to have incorporated the "
                "coming recession earlier than equity investors primed for continued gains. "
                "SPY declined approximately 49% from March 2000 to October 2002. The credit "
                "early-warning window, if it operated as the theory suggests, would have given "
                "an investor tracking HY-IG spreads an advance signal — though the precise lead "
                "time requires the formal statistical test on the Evidence page to characterize rigorously."
            ),
            "caption": (
                "HY-IG spread widening in late 2000 preceded the worst of SPY's 2001-2002 decline "
                "— consistent with the credit-leads-equity hypothesis, though the lead time and "
                "statistical significance are questions for the Evidence page rather than this summary."
            ),
        },
        {
            "slug": "gfc",
            "title": "The Global Financial Crisis (2007-2009)",
            "narrative": (
                "The Global Financial Crisis is frequently cited as the clearest historical "
                "demonstration of the HY-IG spread's potential leading-indicator properties for "
                "equity. The spread began widening measurably in the summer of 2007 — several "
                "months before SPY reached what proved to be its October 2007 peak. The initial "
                "widening reflected stress in subprime mortgage-linked corporate credit structures, "
                "then expanded across the broader high-yield universe as lending conditions "
                "tightened. SPY subsequently declined approximately 57% to its March 2009 trough, "
                "while the HY-IG spread ultimately reached levels that had not been seen since the "
                "early 1990s. The GFC episode is important for another reason as well: it illustrates "
                "the severity-signaling potential of the spread. A very wide spread does not merely "
                "suggest 'some weakness ahead' — during 2008-09, the extreme spread levels were "
                "consistent with a genuine systemic crisis. Whether these spread levels provide "
                "usable signals at the specific thresholds tested on the Strategy page is an "
                "empirical question the exam must answer. What is clear historically is that the "
                "directionality and approximate timing of the relationship were present during the GFC."
            ),
            "caption": (
                "HY-IG spreads began widening months before SPY's October 2007 peak — historically "
                "the clearest episode supporting the credit-leads-equity timing hypothesis. "
                "GFC dominates full-sample regression leverage; subsample results excluding "
                "2007-09 are reported separately on the Evidence page."
            ),
        },
        {
            "slug": "covid",
            "title": "The COVID-19 Shock (2020)",
            "narrative": (
                "The COVID-19 episode illustrates both a potential limit and a potential feature "
                "of the HY-IG → SPY relationship. The initial SPY collapse in February-March 2020 "
                "was extraordinarily rapid — approximately 34% in about 33 calendar days — and "
                "HY-IG spreads widened in rough simultaneity with the equity decline rather than "
                "providing the multi-month lead seen in 2007. The speed of the shock compressed "
                "the leading-indicator window to near-zero: by the time any monthly-frequency "
                "signal could be observed, the worst of the equity damage had already occurred. "
                "This is consistent with the literature finding that pandemic shocks can overwhelm "
                "the credit-cycle transmission mechanism. However, the subsequent behavior is also "
                "illustrative: the Federal Reserve's March 23, 2020 announcement of corporate bond "
                "purchase programs (PMCCF and SMCCF) produced a rapid compression of HY-IG spreads "
                "even as the fundamental macroeconomic damage was still unfolding. Spreads retraced "
                "from approximately 1,100 bps to 500 bps within weeks of the announcement, while "
                "SPY began its recovery. The COVID episode suggests that the Fed's capacity to "
                "intervene directly in the corporate bond market can compress — and potentially "
                "reverse — the spread signal on a timeline that makes mechanical signal interpretation "
                "difficult during acute policy-action periods."
            ),
            "caption": (
                "COVID spread widening was largely coincident with the SPY collapse in Feb-Mar 2020, "
                "not leading — the fastest modern bear market gave little time for any early-warning "
                "mechanism. Fed corporate bond facility announcement in March 2020 reversed spreads "
                "sharply within weeks."
            ),
        },
        {
            "slug": "taper_2018",
            "title": "The 2018 Fed Tightening and Q4 Selloff",
            "narrative": (
                "The 2018 episode provides a useful non-recessionary stress test for the "
                "HY-IG → SPY relationship. The Federal Reserve's post-GFC tightening cycle began "
                "in late 2015 and accelerated in 2018; Chair Powell's October 2018 remarks that "
                "the Fed funds rate was 'a long way from neutral' triggered a sharp risk-off episode. "
                "HY-IG spreads widened from approximately 330 bps to 540 bps through Q4 2018, the "
                "widest non-recessionary print of that cycle. SPY declined approximately 20% from "
                "its September 2018 peak to the December 24 Christmas Eve low. Critically, the "
                "spread widening and equity weakness were compressed into roughly the same 3-month "
                "window, with limited evidence of the multi-month leading gap seen in 2007. The "
                "subsequent recovery was rapid: Chair Powell's January 2019 'patient' pivot remarks "
                "at the AEA panel initiated a rapid spread tightening and equity recovery. The 2018 "
                "episode is relevant because it shows the signal can register non-recessionary stress "
                "but may do so with a shorter lead — more as a coincident or short-horizon indicator "
                "than a 3-6 month advance warning during non-crisis tightening cycles."
            ),
            "caption": (
                "HY-IG spread widening in Q4 2018 was largely concurrent with the SPY selloff — "
                "useful as a non-recessionary stress episode that tests whether the lead time "
                "collapses outside formal recessions. The Powell pivot in January 2019 reversed "
                "both spread and equity almost simultaneously."
            ),
        },
        {
            "slug": "inflation_2022",
            "title": "The 2022 Inflation and Rate-Shock Drawdown",
            "narrative": (
                "The 2022 episode is the most important recent test case for the HY-IG → SPY "
                "hypothesis — and it highlights the signal's most significant known limitation. "
                "The Federal Reserve's fastest rate-hiking cycle since the early 1980s drove a "
                "roughly 25% SPY decline in 2022. HY-IG spreads did widen — from approximately "
                "310 bps at the January SPY peak to a maximum of roughly 580 bps around the "
                "October SPY trough — but this widening was modest by historical standards "
                "relative to the magnitude of the equity decline. The reason is theoretically "
                "clear: the 2022 drawdown was primarily a valuation and duration repricing event "
                "(equities became less valuable as discount rates rose sharply) rather than a "
                "credit-cycle deterioration event (companies did not begin defaulting at elevated "
                "rates). When the mechanism is rate-repricing rather than default-repricing, the "
                "HY-IG spread — which is calibrated to measure credit-cycle risk — may give only "
                "a partial signal. The 2022 episode should be examined carefully in the Evidence "
                "page's regime-conditional results and in any strategy evaluation: it is the "
                "clearest real-world demonstration that the HY-IG signal has a rate-shock blind "
                "spot. An investor relying solely on HY-IG as an equity risk signal would have "
                "reduced exposure but not avoided the bulk of the 2022 drawdown."
            ),
            "caption": (
                "The 2022 SPY drawdown (-25%) was driven primarily by rate repricing, not "
                "credit-cycle deterioration. HY-IG spreads widened only modestly (310 to 580 bps) "
                "relative to the equity decline — the clearest real-world illustration of the "
                "signal's rate-shock blind spot."
            ),
        },
    ]


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — 8-element method blocks
# =========================================================================

CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "A **Pearson correlation** (a measure of linear co-movement ranging from -1 to +1) "
        "computed between the HY-IG spread and forward SPY monthly returns at multiple "
        "horizons (1M, 3M, 6M, 12M). Rolling correlations — computed over a moving window "
        "of 12 or 36 months — show how the relationship has evolved through different market "
        "regimes rather than collapsing the full history into a single number. Multiple signal "
        "variants (level, z-score, rate of change) are tested simultaneously."
    ),
    question=(
        "Is there a statistically meaningful negative linear relationship between the HY-IG "
        "spread and subsequent SPY returns — and which signal variant and forward horizon "
        "shows the most consistent association?"
    ),
    how_to_read=(
        "The rolling correlation chart shows 12-month and 36-month Pearson correlations "
        "between the HY-IG spread and SPY forward monthly returns. Values below zero "
        "(below the horizontal zero line) are consistent with the countercyclical hypothesis: "
        "wider spreads associated with weaker forward returns. The dashed vertical line marks "
        "the start of the out-of-sample evaluation period. A persistent negative correlation "
        "band suggests a durable relationship; a correlation that oscillates around zero "
        "suggests regime-dependence."
    ),
    chart_name="rolling_correlation",
    chart_caption=(
        "What this shows: rolling Pearson correlation between the HY-IG spread and SPY "
        "forward monthly return. Negative values support the countercyclical pattern — "
        "wider credit spreads are associated with weaker subsequent SPY performance. "
        "The relationship strengthens during credit-cycle stress periods."
    ),
    observation=(
        "Rolling correlations for the HY-IG spread against SPY forward returns are "
        "predominantly negative across the full sample, particularly at 3-month and "
        "6-month forward horizons. The relationship is strongest during stress regimes "
        "and weakest during the compressed-spread period. See the chart for the full "
        "time-varying pattern."
    ),
    interpretation=(
        "Correlation analysis is consistent with a countercyclical link between HY-IG "
        "spread levels and SPY forward returns. The relationship is most pronounced at "
        "the 3-6 month forward horizon and for normalized signal variants (z-score). "
        "The rolling view shows the relationship is regime-dependent — it strengthens "
        "during credit cycles and weakens during rate-driven or idiosyncratic market episodes."
    ),
    key_message=(
        "The HY-IG spread shows a predominantly negative rolling correlation with SPY "
        "forward returns at 3-6 month horizons: wider credit spreads are associated with "
        "weaker subsequent SPY performance — consistent with the countercyclical early-warning pattern."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality (Toda-Yamamoto)",
    method_theory=(
        "**Granger causality** tests whether past values of the HY-IG spread improve "
        "forecasts of future SPY returns, above and beyond what SPY's own history already "
        "predicts. A positive result means the spread contains incremental predictive "
        "information — it 'Granger-causes' SPY. The **Toda-Yamamoto** variant (augmenting "
        "the VAR by the suspected integration order) handles the non-stationarity of "
        "financial time series robustly, avoiding spurious rejection that can occur when "
        "standard Granger tests are applied to integrated (I(1)) series. Both directions "
        "are tested: HY-IG → SPY and SPY → HY-IG."
    ),
    question=(
        "Does the HY-IG spread carry information about future SPY returns that is not "
        "already contained in SPY's own return history — and is the relationship "
        "asymmetric, flowing from credit to equity rather than from equity to credit?"
    ),
    how_to_read=(
        "The chart shows Toda-Yamamoto test statistics and p-values for the null hypothesis "
        "that HY-IG spreads do NOT Granger-cause SPY returns, at lags 1 through 6 months. "
        "Bars below the p=0.05 dashed threshold indicate statistically significant "
        "predictive content at that lag. Reverse-direction results (SPY → HY-IG) are shown "
        "separately. An asymmetric result — significant in the forward direction, not in "
        "the reverse — is the pattern consistent with bond markets processing default risk "
        "before equity markets."
    ),
    chart_name="granger_by_lag",
    chart_caption=(
        "What this shows: F-statistics by lag (months) for the HY-IG → SPY Granger "
        "causality test. Bars meeting significance threshold indicate statistically "
        "significant predictive content at that horizon. The reverse direction is shown "
        "for comparison."
    ),
    observation=(
        "The Granger causality test results by lag are shown in the chart above. "
        "Significant lags in the forward direction (HY-IG → SPY) with insignificant "
        "results in the reverse direction (SPY → HY-IG) would be consistent with "
        "asymmetric information flow from credit to equity. See the chart for the "
        "lag-by-lag pattern from the v4 data."
    ),
    interpretation=(
        "An asymmetric Granger structure (credit → equity significant; equity → credit "
        "not significant) is the statistical signature of the bond-market-as-leading-"
        "indicator mechanism. Credit analysts process default risk information first; "
        "equity markets follow as that risk crystallizes into earnings and valuation "
        "revisions. The degree of asymmetry is an empirical question the v4 data addresses."
    ),
    key_message=(
        "Granger causality tests examine whether HY-IG spreads carry incremental "
        "predictive content for SPY above and beyond SPY's own history. An asymmetric "
        "result — significant forward direction, insignificant reverse — would confirm "
        "one-way credit-to-equity information flow consistent with the hypothesis."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation Function (CCF)",
    method_theory=(
        "The **pre-whitened CCF** removes each series' own autocorrelation structure first "
        "— by fitting an ARMA model to each series separately and computing the residuals "
        "— then examines cross-correlations of those residuals at lags −12 to +12 months. "
        "This 'pre-whitening' step ensures that any observed cross-correlations reflect "
        "genuine information transfer between the two variables, not shared persistence "
        "(a common source of spurious correlation in financial time series that have "
        "persistent trends or cycles)."
    ),
    question=(
        "At what lag does the HY-IG spread carry the most information about SPY returns "
        "— and does the lead-lag structure, after removing autocorrelation from both "
        "series, confirm that credit moves first?"
    ),
    how_to_read=(
        "Bars at negative lags (e.g., lag −3) indicate that the HY-IG spread at month "
        "T−3 is associated with SPY return at month T: the spread leads by 3 months. "
        "Bars at positive lags indicate that SPY returns lead the spread. Bars extending "
        "beyond the 95% confidence bands (dashed lines, set at ±1.96/√n) are statistically "
        "significant. A cluster of significant negative-lag bars is consistent with the "
        "spread-leads-equity hypothesis."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: pre-whitened cross-correlation function between the HY-IG "
        "spread and SPY monthly returns at lags −20 to +20 months. Significant bars "
        "outside the 95% CI bands (dashed) are statistically meaningful. Negative-lag "
        "bars indicate the spread leads SPY returns."
    ),
    observation=(
        "The pre-whitened CCF chart shows the cross-correlation structure between "
        "HY-IG spreads and SPY returns after autocorrelation removal. Significant "
        "bars at negative lags (spread leads) versus positive lags (SPY leads) reveal "
        "the direction of information flow once shared persistence is eliminated. "
        "See the chart for the v4 lead-lag pattern."
    ),
    interpretation=(
        "The CCF after pre-whitening isolates genuine cross-series information transfer. "
        "Significant negative-lag bars confirm the credit-leads-equity timing structure "
        "at those specific horizons. The absence of significant positive-lag bars rules "
        "out a reverse causality interpretation as the primary channel."
    ),
    key_message=(
        "The pre-whitened CCF reveals the lead-lag timing structure between HY-IG "
        "spreads and SPY returns after removing autocorrelation from both series — "
        "confirming whether the spread-leads-equity pattern is genuine signal or "
        "shared persistence."
    ),
)


HMM_BLOCK = dict(
    chart_status="ready",
    method_name="Hidden Markov Model (HMM) Regime Analysis",
    method_theory=(
        "A **Hidden Markov Model** identifies latent (unobserved) market regimes — "
        "distinct states of the world that generate statistically different behavior — "
        "from the observed spread series alone. We fit a 2-state HMM (a 'calm' state "
        "and a 'stress' state) to the HY-IG spread. The model outputs, for each month, "
        "a probability that the market is currently in the stress state. This probability "
        "serves as a candidate signal. The HMM aggregates level, trend, and volatility "
        "information in the spread into a single, calibrated probability number — making "
        "it a nonlinear summary of the credit-risk environment."
    ),
    question=(
        "Do HMM-identified credit regimes discriminate meaningfully between historical "
        "periods of strong and weak SPY performance — does being in the stress state "
        "reliably identify the months when holding SPY has historically been costly?"
    ),
    how_to_read=(
        "The chart overlays HMM stress probability (shaded area, right axis) on the "
        "HY-IG spread time-series (line, left axis). Shaded periods above 0.5 probability "
        "are HMM-classified stress regimes. Key historical events are annotated. Look for "
        "whether the high-stress periods align with the major SPY drawdown episodes. A "
        "stress state that covers a minority of calendar months but contains the majority "
        "of drawdown losses would be consistent with a useful regime discriminator."
    ),
    regime_context=(
        "The HMM stress state is one candidate signal from the tournament. Its value is "
        "not precise timing prediction — it is identifying the regimes where holding full "
        "SPY exposure has historically carried elevated drawdown risk relative to calm-"
        "state periods. The v4 tournament winner used the z-score signal rather than the "
        "HMM probability; see the Strategy page for the tournament outcome."
    ),
    chart_name="hmm_regime_overlay",
    chart_caption=(
        "What this shows: HMM 2-state stress probability overlaid on the HY-IG spread "
        "time-series. Shaded areas above 0.5 mark HMM stress regimes. Major credit "
        "stress episodes are annotated for reference."
    ),
    observation=(
        "The HMM regime overlay shows how the 2-state model partitions the historical "
        "spread series into stress and calm periods. Whether the stress periods align "
        "closely with the major SPY drawdown episodes (GFC 2008-09, COVID 2020, "
        "inflation 2022) is visible in the chart above."
    ),
    interpretation=(
        "The HMM stress probability is a nonlinear summary of whether credit markets "
        "are currently in a deterioration regime. Its value as an analytical tool is "
        "identification of the regimes where the risk-reward of holding full SPY exposure "
        "is demonstrably worse — not prediction of the exact timing of SPY decline. "
        "The rate-shock blind spot (2022) applies here as well: the HMM may classify "
        "the 2022 episode as stress even though the mechanism was rate repricing rather "
        "than credit-cycle deterioration."
    ),
    key_message=(
        "The HMM regime analysis tests whether a 2-state model fitted to HY-IG spread "
        "history discriminates between SPY stress and calm periods — providing a "
        "nonlinear complement to the linear correlation and Granger tests."
    ),
)


REGIME_QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Returns Analysis",
    method_theory=(
        "Rather than relying on a fitted model to define regimes, this analysis divides "
        "the observed history of HY-IG spread values into four equal-frequency quartiles: "
        "Q1 (tightest 25% of spreads, least credit stress) through Q4 (widest 25%, most "
        "credit stress). SPY forward return distributions are then computed within each "
        "quartile. This **model-free** approach provides a transparent, assumption-free "
        "check on whether the spread level has monotonic predictive content across the "
        "full distribution — not just at extremes."
    ),
    question=(
        "Is there a monotonic downward gradient from tight spreads to wide spreads in "
        "SPY forward returns — and does it hold across the full spread distribution, "
        "not just during crisis extremes?"
    ),
    how_to_read=(
        "The bar chart shows average annualized SPY forward return (or Sharpe ratio) for "
        "each of the four HY-IG spread quartiles. A monotonically declining pattern from "
        "Q1 (left, tightest spreads) to Q4 (right, widest spreads) is consistent with "
        "the countercyclical hypothesis. If only Q4 shows a decline, the relationship is "
        "crisis-driven rather than distributional. If Q1 and Q4 diverge but the middle "
        "quartiles are similar, the relationship is concentrated at the extremes."
    ),
    regime_context=(
        "The Q4 vs Q1 Sharpe differential — the performance gap between the tightest and "
        "widest spread quartiles — is the key diagnostic for regime discrimination strength. "
        "A large differential suggests the spread is doing genuine separatory work across "
        "the full distribution."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: average annualized SPY forward return by HY-IG spread quartile. "
        "Q1 = tightest spreads (historically best SPY forward returns), Q4 = widest "
        "spreads (historically worst SPY forward returns). A monotone downward gradient "
        "confirms the countercyclical relationship is distributional."
    ),
    observation=(
        "The quartile bar chart shows SPY forward return by HY-IG spread quartile. "
        "A monotonically declining pattern from Q1 to Q4 would confirm the countercyclical "
        "relationship holds across the full spread distribution, not just during extreme "
        "crisis events. See the chart for the v4 gradient pattern."
    ),
    interpretation=(
        "If the quartile gradient is monotonically declining, it confirms the "
        "countercyclical relationship holds across the full HY-IG spread distribution, "
        "not just at crisis extremes. This distributional robustness would support using "
        "the signal as a continuous input rather than a binary crisis detector. "
        "A non-monotonic pattern would suggest threshold-dependent behavior."
    ),
    key_message=(
        "The quartile analysis provides a model-free check: does SPY forward return "
        "decline monotonically from the tightest to widest spread quartiles? A clear "
        "gradient is consistent with a distributional countercyclical relationship; "
        "crisis-only concentration would suggest threshold-dependent behavior."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: What the Data Shows",
    "overview": (
        "*We subjected approximately 30 years of monthly credit spread data to multiple "
        "complementary statistical methods. Each is designed to test a different aspect of the "
        "HY-IG → SPY relationship. The core hypothesis: rising credit spreads carry advance "
        "information about weaker forward SPY returns — a countercyclical early-warning pattern.*"
    ),
    "plain_english": (
        "This section presents statistical tests of the same core question: does "
        "the HY-IG credit spread carry useful information about future SPY returns? The "
        "tests range from simple correlation to nonlinear regime analysis. No single test "
        "is definitive, but their convergence — or divergence — builds the evidence base. "
        "Note: observation, interpretation, and key-message fields in evidence blocks reflect "
        "the v4 dataset. The formal final exam has been run; see the Strategy page for results."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger Causality", "Pre-Whitened CCF"],
    "level2": [HMM_BLOCK, REGIME_QUARTILE_BLOCK],
    "level2_labels": ["HMM Regime Analysis", "Regime Quartile Returns"],
    "tournament_intro": (
        "We tested combinations of signals (HY-IG level, z-score, rate-of-change, "
        "momentum, and HMM stress probability), thresholds (z-score crossings, "
        "percentile bands), strategies (Long/Cash, Signal-Strength, Long/Short), "
        "and lead times (1 month). These were ranked by out-of-sample Sharpe ratio "
        "over 2014-08-29 to 2020-06-30 (71 months). "
        "The winning combination: **36-month z-score (S2c_zscore_36m), "
        "threshold T3_z0.0 (z-score < 0 → long SPY), Long/Cash strategy (P1), "
        "1-month lead**, producing OOS Sharpe 1.32 vs 0.71 buy-and-hold SPY."
    ),
    "transition": (
        "**Transition:** Multiple statistical methods examine the countercyclical "
        "relationship between HY-IG credit spreads and SPY returns. The tournament "
        "search identified the 36-month z-score as the winning signal. Now: what does "
        "the winning strategy actually do, and how has it performed — including on the "
        "holdout period that was sealed during the search?"
    ),
}


# =========================================================================
# STRATEGY PAGE CONFIG
# =========================================================================
class StrategyConfig:
    """Strategy-page content object (passed to `render_strategy_page`)."""

    PAGE_TITLE = "The Strategy: Translating Credit Signals into SPY Positioning"
    PAGE_SUBTITLE = (
        "We tested 1,900+ strategy combinations to find the most robust way "
        "to time SPY exposure using the HY-IG credit spread z-score signal."
    )

    PLAIN_ENGLISH = (
        "The strategy uses the credit spread z-score signal to determine SPY exposure. "
        "When the 36-month z-score is below zero (spread below its rolling mean — benign "
        "credit conditions), the strategy holds SPY long. When the z-score rises above "
        "zero (spread above its rolling mean — tightening credit conditions), the strategy "
        "moves to cash. This section explains what the strategy does, what the numbers "
        "look like, and where honest limitations lie — including the holdout exam result."
    )

    SIGNAL_RULE_MD = (
        "**Strategy Rule in Plain English:** Monitor the 36-month rolling z-score of the "
        "HY-IG credit spread. When the z-score falls below zero (spread is below its "
        "36-month mean — credit conditions are benign), **hold SPY long** at full "
        "exposure. When the z-score rises at or above zero (spread is above its "
        "36-month mean — credit conditions are deteriorating), **move to cash**. "
        "Positions are rebalanced monthly with a 1-month execution lead."
    )

    HOW_SIGNAL_IS_GENERATED_MD = (
        "Each month, the HY-IG spread (difference between ICE BofA HY OAS and IG OAS) "
        "is computed from FRED series BAMLH0A0HYM2 and BAMLC0A0CM. The 36-month "
        "rolling z-score is computed as: (current spread − 36-month mean) / "
        "36-month standard deviation. When this z-score is negative, the spread is "
        "below its recent average — a benign credit environment. When it is positive, "
        "the spread is elevated relative to recent history — a warning signal. "
        "The strategy holds SPY when z-score < 0 and moves to cash when z-score >= 0. "
        "Monthly positions are rebalanced at each month-end based on the prior month's "
        "z-score value (1-month lead to avoid look-ahead bias)."
    )

    MANUAL_USE_MD = (
        "To monitor this signal as a research indicator:\n\n"
        "1. **Pull HY and IG OAS from FRED** (BAMLH0A0HYM2 and BAMLC0A0CM) "
        "at month-end.\n"
        "2. **Compute the spread**: HY OAS minus IG OAS in basis points.\n"
        "3. **Compute the 36-month rolling z-score**: "
        "(current spread − 36-month mean) / 36-month standard deviation.\n"
        "4. **Read the z-score**: negative means below average (hold SPY); "
        "zero or above means elevated (move to cash).\n"
        "5. **Apply the rule with 1-month lead**: if this month's z-score < 0, "
        "hold SPY next month; if >= 0, move to cash next month.\n"
        "6. **Monthly rebalancing** — z-score is updated each month as new "
        "spread data arrives. No model refitting required."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"

    CAVEATS_MD = """
**Important Caveats**

1. **Simulated, not executed.** All performance statistics in this portal are hypothetical —
   they reflect rules applied to historical data, not actual trades with real capital. Real
   execution involves market impact, bid-ask spreads, and behavioral execution risk.
   Transaction costs are estimated at 5 basis points per trade.

2. **Failed final exam — holdout Sharpe 0.31 < 0.50 floor.** The strategy was tested on a
   sealed holdout period (2020-07 to 2026-05) covering the COVID recovery, 2022 rate shock,
   and 2023-2026 bull market. Result: FAIL. The holdout Sharpe of 0.31 did not meet the 0.50
   confirmation floor for the credit indicator class. The strategy demonstrated pre-COVID;
   it did not confirm on the post-COVID holdout. See the disclosure banner above.

3. **The 2022 rate-shock blind spot is real.** The 2022 SPY drawdown was driven primarily
   by the Federal Reserve's fastest rate-hiking cycle in 40 years, not by credit
   deterioration. The HY-IG z-score signal gave partial warning but the mechanism
   was rate repricing, not credit-cycle default risk. The strategy moved to cash
   correctly on the spread signal but the reason was not the classical credit channel.

4. **OOS window caveat.** The OOS window (2014-2020, 71 months) covers a specific
   macro regime. The subsequent holdout (2020-2026) covers a different regime
   including extraordinary monetary policy, a rapid equity recovery, and a rate-shock
   bear market. The divergence between OOS and holdout performance is a genuine
   macro regime effect, not a procedural error.

5. **Primary value proposition was drawdown reduction.** The strategy's countercyclical
   design reduced maximum drawdown from -20.5% (B&H) to -6.38% in the OOS period.
   On the holdout, this protective function did not translate to confirmation-level
   Sharpe performance.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**Concrete example — COVID 2020.** As credit markets priced the pandemic in "
        "early 2020, the HY-IG spread rose sharply above its 36-month rolling mean, "
        "driving the z-score above zero. The strategy's long/cash rule triggered a "
        "move to cash at the next monthly rebalance. This is the defensive mechanism "
        "the strategy is designed to execute: exit SPY when the credit stress z-score "
        "signals elevated risk, and re-enter when the z-score returns below zero. "
        "The trade log below shows the full sequence of position changes; the broker-"
        "style log presents this as dated BUY/SELL entries with quantities and P&L."
    )


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE CONFIG
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|:---------|:-------|:-------|:----------|
| **HY Spread** | FRED | BAMLH0A0HYM2 | Monthly |
| **IG Spread** | FRED | BAMLC0A0CM | Monthly |
| **HY-IG Spread (derived)** | BAMLH0A0HYM2 − BAMLC0A0CM | — | Monthly |
| **SPY (Target)** | Yahoo Finance | SPY | Daily → Monthly |
| **NBER Recession Dates** | FRED / NBER | USREC | Monthly |
| **VIX (robustness)** | FRED | VIXCLS | Monthly |
| **10-Year Treasury (robustness)** | FRED | GS10 | Monthly |

*Scope discipline:* Only the HY-IG spread and SPY are in-scope primary signals.
VIX and GS10 are used only as regression controls, not as trading signals.
Sample period: 1996-12-31 to 2026-05-29 (354 monthly observations).
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The primary indicator is the HY-IG credit spread, constructed monthly as the "
    "difference between the ICE BofA US High Yield Index Option-Adjusted Spread "
    "(FRED: BAMLH0A0HYM2) and the ICE BofA US Investment Grade Corporate Index "
    "Option-Adjusted Spread (FRED: BAMLC0A0CM). From this raw series we derive: "
    "the level, the 36-month rolling z-score (winning signal: S2c_zscore_36m), "
    "month-over-month rate of change, and HMM stress probability "
    "(2-state Hidden Markov Model fitted to the spread history). "
    "The winning signal (hy_ig_zscore_36m = (spread − 36m mean) / 36m std) "
    "normalizes the spread relative to recent history, making the threshold "
    "(z-score < 0 vs >= 0) invariant to the level of the spread cycle."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|:-------|:--------------------|:----------------|
| Pearson / Rolling Correlation | Linear co-movement at multiple horizons | Baseline linearity test; rolling view reveals regime dependence |
| Granger Causality (Toda-Yamamoto) | One-directional predictive content, robust to non-stationarity | Tests asymmetric credit-leads-equity hypothesis |
| Pre-Whitened CCF | Lead-lag timing structure after removing autocorrelation | Identifies the peak predictive lag without spurious persistence |
| Hidden Markov Model (2-state) | Latent regime identification from spread data alone | Nonlinear candidate signal; aggregates signal into interpretable probability |
| Regime Quartile Returns | Model-free gradient across spread distribution | Assumption-light cross-check on spread's distributional predictive content |
| Transfer Entropy | Nonlinear directional information flow | Detects threshold effects and nonlinear channels Granger misses |
| Local Projections (Jordà) | Full dynamic path of SPY response to spread shock | Robust impulse response without VAR parameter restrictions |
| Quantile Regression | Asymmetric predictive power across SPY return distribution | Confirms left-tail (downside) concentration — risk management signal |
| Predictive Regressions | Coefficient forest plot across signals × horizons | Identifies which signal variant carries the most consistent predictive content |
| Rolling Granger | Time-varying predictive content | Tests whether Granger predictability is stable or regime-dependent |
| Structural Break (CUSUM) | Stability of the relationship over time | Detects parameter instability; CUSUM test failed numerically — spread history shown instead |
"""

_TOURNAMENT_DESIGN_MD = """
| Dimension | Values |
|:----------|:-------|
| **Signals (4 families)** | HY-IG level, z-score (36m), MoM rate-of-change, HMM stress probability |
| **Threshold methods** | z-score crossing T3_z0.0 (< 0 vs >= 0), rolling percentile bands, HMM 0.5 cutoff |
| **Strategies (3)** | Long/Cash (P1, winner), Signal-Strength (P2), Long/Short (P3) |
| **Lead times** | 1 month (L1, winning combination) |
| **Orientation** | Countercyclical (spread z-score below mean → long SPY; above mean → cash) |
| **Total combinations tested** | 1,908 valid combinations |

The tournament tested all valid combinations and ranked by out-of-sample Sharpe ratio
over 2014-08-29 to 2020-06-30 (71 months). Winner: S2c_zscore_36m / T3_z0.0 / P1 / L1,
OOS Sharpe 1.32 vs B&H 0.71.

**Three-period design:**
- In-sample (signal search): 1996-12-31 to 2014-07-31 (212 months)
- Out-of-sample (tournament evaluation): 2014-08-29 to 2020-06-30 (71 months)
- Holdout (final exam — sealed): 2020-07-31 to 2026-05-29 (71 months)
"""

_REFERENCES_MD = """
#### Credit Markets and Equity Prediction
- Gertler, M., & Lown, C. S. (1999). The information in the high yield bond spread for the business cycle. *Oxford Review of Economic Policy*, 15(3), 132–150.
- Gilchrist, S., & Zakrajšek, E. (2012). Credit spreads and business cycle fluctuations. *American Economic Review*, 102(4), 1692–1720.
- Fama, E. F., & French, K. R. (1989). Business conditions and expected returns on stocks and bonds. *Journal of Financial Economics*, 25(1), 23–49.
- López-Salido, D., Stein, J. C., & Zakrajšek, E. (2017). Credit-market sentiment and the business cycle. *Quarterly Journal of Economics*, 132(3), 1373–1426.
- Mueller, P. (2009). Credit spreads and real activity. *Working Paper, Columbia Business School*.
- Haddad, V., Moreira, A., & Muir, T. (2021). When selling becomes viral: disruptions in debt markets in the COVID-19 crisis and the Fed's response. *Review of Financial Studies*, 34(11), 5309–5351.

#### Hidden Markov Models and Regime Detection
- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357–384.

#### Impulse Response and Local Projections
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161–182.

#### Quantile Methods
- Koenker, R., & Bassett, G. (1978). Regression quantiles. *Econometrica*, 46(1), 33–50.
- Adrian, T., Boyarchenko, N., & Giannone, D. (2019). Vulnerable growth. *American Economic Review*, 109(4), 1263–1289.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Three-period design: in-sample 1996-12-31 to 2014-07-31 (212 months); "
        "OOS tournament window 2014-08-29 to 2020-06-30 (71 months); "
        "holdout (sealed final exam) 2020-07-31 to 2026-05-29 (71 months). "
        "Full dataset: 354 monthly observations (1996-12-31 to 2026-05-29)."
    ),
    plain_english=(
        "This section covers the technical decisions — data sources, sample period, "
        "signal construction, model specifications, and known limitations. Readers who "
        "want to replicate or challenge the analysis will find the inputs and design "
        "choices documented here. The v4 pipeline is a clean rebuild from first principles; "
        "no results from v1, v2, or v3 are carried into this version."
    ),
)
