"""ISM Services PMI x SPY pair configuration (Rule APP-PT1).

Pair `ism_services_spy`, Mode 3. Prose is sourced from Research Ray's
`docs/portal_narrative_ism_services_spy_20260618.md`; this file wires that
prose to the shared Streamlit templates and Vera's bare-name chart artifacts.

Evidence status is `found_in_search`, so headline performance is labelled as
"Search-phase OOS Sharpe (no holdout final exam yet)" by the template.
Headline values come from `results/ism_services_spy/winner_summary.json`.

This is the lowest-confidence winner in the pair series: the lead-lag evidence
runs in reverse (SPY predicts the survey, not the other way around), in-sample
Sharpe is negative, and the out-of-sample result is episode-concentrated. The
config deliberately frames the pair as a contrarian drawdown overlay, NOT as
evidence that ISM Services PMI leads the S&P 500.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: ISM Services PMI as a Contrarian Drawdown Overlay"
    PAGE_SUBTITLE = (
        "ISM Services PMI (project Data Master workbook) x S&P 500 (SPY), "
        "monthly decision rules with release-lag discipline."
    )

    HEADLINE_H2 = (
        "## OOS Sharpe 1.54 with low confidence: ISM Services PMI is a "
        "contrarian drawdown overlay, not a leading SPY signal"
    )

    PLAIN_ENGLISH = (
        "The Institute for Supply Management (ISM) Services PMI is a monthly "
        "survey diffusion index where 50 separates expansion from contraction. "
        "The natural prior is procyclical: stronger services activity should "
        "support stocks. The searched winner does the opposite -- it buys SPY "
        "when services sentiment is unusually weak. It reduces drawdown, but it "
        "gives up annual return, it is not statistically significant, and the "
        "lead-lag evidence actually runs backward: SPY predicts the survey "
        "more than the survey predicts SPY."
    )

    WHERE_THIS_FITS = (
        "This is a sentiment-survey macro signal tested against broad U.S. "
        "equities. The honest reading is narrow: the rule is a searched "
        "defensive overlay that manages drawdown in certain shocks. It is not "
        "evidence that ISM Services PMI leads the S&P 500."
    )

    ONE_SENTENCE_THESIS = (
        "The winning ISM Services rule improves risk-adjusted return mainly by "
        "reducing drawdown, contradicts its own economic prior, fails the "
        "lead-lag test, and should be treated as a low-confidence searched "
        "candidate awaiting a final exam."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final "
        "holdout result. The winner was selected from 3,385 valid strategy "
        "combinations, with bootstrap p=0.073, a negative in-sample Sharpe, "
        "and low confidence."
    )

    HERO_TITLE = "ISM Services PMI vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the ISM Services PMI is shown against SPY on a shared "
        "time axis with the 50 expansion/contraction line marked. The signal "
        "fires when services sentiment falls well below its own recent norm -- "
        "a contrarian 'buy weakness' trigger, not a 'buy strength' one."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by ISM Services Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by ISM Services "
        "level quartile. The gradient is NOT clean -- Q1 (weakest services) "
        "has the worst forward Sharpe (0.21) and a -60% drawdown, while Q3 is "
        "best (1.00). This non-monotonic pattern is itself a caution flag."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used as the initial in-sample fit -- the winning ISM Services rule earns a Sharpe ratio -- return per unit of volatility -- of 1.54 versus 0.88 for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- improves to -3.8% from -23.9%. But the strategy gives up return: 9.8% annualized versus 15.1% for buy-and-hold. This is a risk-control result, not an alpha story.

### Natural Prior vs Tournament Winner

The natural prior is procyclical -- a services-sector survey above 50 signals expansion, which should support equities. The tournament winner goes the other way. It is countercyclical: it goes long SPY when services sentiment is unusually weak, specifically when the ISM Services PMI gap to 50 falls below a rolling z-score threshold of -1.0 after a 3-month lag. The plain-English version is "buy after services fear," not "buy because services strength leads stocks."

### Why This Is Not a Leading Signal

The single most important result on this page is the lead-lag test. Toda-Yamamoto Granger causality -- a test of whether one series' past improves forecasts of another's future -- finds NO significant forward signal from ISM Services PMI to SPY at any lag from 1 to 12 months. The reverse direction, SPY predicting the survey, is significant at every lag. The honest reading is that ISM Services PMI behaves as a coincident or lagging reflection of conditions equities already price. Any tradable edge is therefore suspect, likely regime-driven, and not evidence that the survey leads the stock market.

<!-- expander: Why does the in-sample Sharpe matter? -->
The in-sample (IS) period is the earlier window used to select the rule; the out-of-sample (OOS) period is the later window used to evaluate it. Here the IS Sharpe is negative (-0.11) while the OOS Sharpe is strong (1.54). A rule that loses money in-sample but wins out-of-sample is usually riding a few specific episodes rather than a stable effect -- a red flag for fragility, not a sign of strength.
<!-- /expander -->
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "The Dot-Com episode mostly sits before the OOS test window. "
                "Read it as contextual background, not as validation for the "
                "OOS winner."
            ),
            "caption": "Contextual background; predates the OOS test window.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "During the Global Financial Crisis, ISM Services fell with "
                "the market, not ahead of it -- the survey was coincident with "
                "the equity collapse, illustrating why it does not provide a "
                "clean long lead."
            ),
            "caption": "GFC shows the survey moving coincident with the crash.",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "Coronavirus disease 2019 (COVID-19) is the episode that helps "
                "explain the OOS result. Services sentiment collapsed and "
                "recovered quickly, and the defensive rule avoided much of the "
                "drawdown. Much of the headline OOS performance concentrates "
                "here."
            ),
            "caption": "COVID is the concentrated episode behind much of the OOS result.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022 inflation shock, the Long/Cash rule mostly "
                "stayed defensive and avoided drawdown. That is a cash-overlay "
                "result, not proof of services leadership."
            ),
            "caption": "2022 is a cash-overlay example, not proof of leadership.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The history-zoom charts make the caveat tangible. In the GFC the survey fell with the market rather than leading it. COVID-19 is the concentrated episode that explains much of the OOS result: services sentiment collapsed and recovered quickly, and the defensive rule sidestepped drawdown. The 2022 inflation shock is better read as a cash-overlay example than as proof of services leadership, and the Dot-Com episode predates the OOS window. Together these episodes support the low-confidence story: the rule can manage drawdown in certain shocks, but it is not a general leading indicator.
"""

    TRANSITION_TEXT = (
        "The historical story is a drawdown-management one, so the full "
        "evidence suite matters. The Evidence page leads with the causality "
        "result -- which runs backward -- before the supporting checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_CHART_NAME = "correlation_heatmap"
GRANGER_CHART_NAME = "granger_f_by_lag"
CCF_CHART_NAME = "ccf_prewhitened"
LOCAL_PROJECTIONS_CHART_NAME = "local_projections"
QUANTILE_CHART_NAME = "quantile_coef"
TRANSFER_ENTROPY_CHART_NAME = "transfer_entropy"
HMM_REGIME_CHART_NAME = "hmm_regime_probs"


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag (Both Directions)",
    method_theory=(
        "Toda-Yamamoto Granger causality tests whether past values of one "
        "series improve forecasts of the other beyond its own history, in a "
        "form robust to integration order."
    ),
    question="Does ISM Services PMI lead SPY -- or does SPY lead the survey?",
    how_to_read=(
        "Bars are F-statistics by monthly lag; bars above the dashed line are "
        "significant at the 5% level. Compare the forward (PMI to SPY) and "
        "reverse (SPY to PMI) directions."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: the forward direction (ISM Services to SPY) clears "
        "the line at NO lag; the reverse direction (SPY to ISM Services) is "
        "significant at every lag 1-12."
    ),
    observation=(
        "Forward Granger support is absent at all lags; reverse SPY-to-survey "
        "support is present at all lags 1-12."
    ),
    deep_dive_title="Why is reverse causality the headline?",
    deep_dive_content=(
        "If SPY moves first and the survey follows, the survey is summarizing "
        "conditions investors have already priced. That makes ISM Services a "
        "coincident/lagging reflection of the market, not a leading indicator "
        "of it -- so any forward-trading edge is suspect."
    ),
    interpretation=(
        "The lead-lag evidence points backward. This is the central reason "
        "confidence is low despite the headline Sharpe."
    ),
    key_message="Causality runs from SPY to the survey, not the reverse.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quartile Gradient",
    method_theory=(
        "Quartile analysis sorts months into four buckets by ISM Services "
        "level and compares subsequent SPY performance."
    ),
    question="Do weaker or stronger services readings line up with better future SPY returns?",
    how_to_read=(
        "Read the bars from Q1 (weakest services) to Q4 (strongest). A clean "
        "monotonic gradient would support a simple directional story; an "
        "irregular pattern argues against one."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Q1 Sharpe 0.21 (with a -60% drawdown), Q2 0.77, "
        "Q3 1.00, Q4 0.86 -- non-monotonic, with the middle quartile best."
    ),
    observation=(
        "The gradient is not monotonic. The weakest-services quartile has the "
        "worst forward Sharpe and the deepest drawdown, while the best bucket "
        "is the third, not an extreme."
    ),
    interpretation=(
        "This does not cleanly support the contrarian winner at the quartile "
        "level. It reinforces that the OOS edge is concentrated in specific "
        "extreme/episode conditions, not a smooth state relationship."
    ),
    key_message=(
        "The quartile sort is irregular -- a caution flag, not clean support."
    ),
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation removes each series' own persistence "
        "before checking whether one echoes the other at monthly offsets."
    ),
    question="Is there a clean forward lead-lag echo after removing autocorrelation?",
    how_to_read=(
        "Bars outside the confidence band indicate statistically meaningful "
        "offsets. Positive lags would mark ISM Services leading SPY."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the CCF does not establish a clean forward lead from "
        "ISM Services to SPY, consistent with the Granger result."
    ),
    observation=(
        "The cross-correlation does not produce a clean forward-lead signal."
    ),
    interpretation=(
        "The CCF reinforces the same conclusion as Granger: there is no "
        "reliable forward lead from the survey to SPY."
    ),
    key_message="The cross-correlation check does not support a forward lead.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate the forward SPY response at several "
        "horizons after a move in the survey."
    ),
    question="Does an ISM Services move produce statistically clear forward SPY responses?",
    how_to_read=(
        "The line is the estimated response and the band is statistical "
        "uncertainty. Bands crossing zero mean weak evidence."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: forward ISM-to-SPY responses are not statistically "
        "distinguishable from zero; reverse SPY-to-ISM responses are "
        "significant at 1, 3, 6, and 12 months."
    ),
    observation=(
        "Forward responses are insignificant; reverse responses are "
        "significant at several horizons."
    ),
    interpretation=(
        "Local projections tell the same backward-causality story as Granger "
        "and CCF."
    ),
    key_message="Local projections also point backward, not forward.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression asks whether the relationship differs in weak, "
        "normal, and strong SPY-return environments."
    ),
    question="Is the signal coherent across the return distribution?",
    how_to_read=(
        "Read coefficient estimates across return quantiles. Stable signs "
        "would suggest a coherent channel; sign flips suggest instability."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: coefficients are sign-unstable -- some lower-tail "
        "estimates are positive while median/upper-tail estimates are negative."
    ),
    observation=(
        "Coefficient signs are unstable across quantiles."
    ),
    interpretation=(
        "That instability does not support a simple, coherent economic "
        "channel from the survey to SPY."
    ),
    key_message="Quantile evidence is sign-unstable, not supportive.",
)

TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy is a nonlinear information-flow check that can catch "
        "relationships missed by linear tests."
    ),
    question="Is there nonlinear directed information flow, and in which direction?",
    how_to_read=(
        "Small permutation p-values indicate genuine directed information "
        "flow. Compare the forward and reverse channels."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "What this shows: forward ISM-to-SPY is marginal (p=0.064); reverse "
        "SPY-to-ISM is stronger (p=0.002)."
    ),
    observation=(
        "The reverse channel is the stronger one even under a nonlinear test."
    ),
    interpretation=(
        "Transfer entropy is reverse-heavy too, consistent with the rest of "
        "the evidence bundle."
    ),
    key_message="Even the nonlinear check is reverse-heavy.",
)

HMM_BLOCK = dict(
    chart_status="ready",
    method_name="HMM Regime Map",
    method_theory=(
        "A Hidden Markov Model (HMM) maps the survey series into latent "
        "high-variance regimes."
    ),
    question="When did ISM Services sit in unusual regimes?",
    how_to_read=(
        "Higher regime probability marks months where survey behavior looks "
        "unusual relative to the long sample."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the HMM is useful as context, not as the winning "
        "trading signal."
    ),
    observation=(
        "The HMM highlights stress and high-variance survey environments, "
        "including major crisis windows."
    ),
    interpretation=(
        "The regime map helps explain context, but the winning rule is the "
        "gap-to-50 z-score threshold, not HMM probability."
    ),
    key_message="The HMM explains backdrop; it does not validate the winner.",
)

EVIDENCE_METHOD_BLOCKS = {
    "title": "Evidence leads with causality -- and the causality runs backward",
    "overview": (
        "The headline lead-lag tests find no forward signal from ISM Services "
        "to SPY, while SPY predicts the survey at every lag. Supporting checks "
        "(local projections, transfer entropy, quantile regression) tell the "
        "same backward, low-confidence story."
    ),
    "plain_english": (
        "This section asks whether ISM Services PMI really helps predict "
        "future SPY performance. The tests point the other way: the market "
        "appears to lead the survey, not vice versa. That is why the strong "
        "headline Sharpe is treated as a low-confidence searched result."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag (12 rows)", "path": "results/ism_services_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns (4 rows)", "path": "results/ism_services_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod Sharpe checks (4 rows)", "path": "results/ism_services_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/ism_services_spy/rolling_correlation_ism_services_spy.csv"},
        {"label": "Stationarity tests (10 rows)", "path": "results/ism_services_spy/stationarity_tests_20260618.csv"},
    ],
    "level1": [GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Granger Causality", "Quartile Gradient", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, TRANSFER_ENTROPY_BLOCK, HMM_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression", "Transfer Entropy", "HMM Regimes"],
    "tournament_intro": (
        "The tournament tested 4,880 benchmark-excluded strategy combinations, "
        "of which 3,385 passed validity filters. The winning rule is the best "
        "of that valid searched set, so its Sharpe advantage must be read with "
        "the search-position warning attached."
    ),
    "transition": (
        "**Transition:** the evidence does not support a forward-leading "
        "signal. The strategy page shows what the rule actually is: a sparse "
        "contrarian Long/Cash overlay that trades return for drawdown control."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Contrarian ISM Services Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched defensive overlay: better Sharpe and drawdown than "
        "buy-and-hold, but lower annual return, a negative in-sample Sharpe, "
        "and low statistical confidence."
    )

    PLAIN_ENGLISH = (
        "The rule is contrarian: when the ISM Services PMI gap to 50 falls "
        "more than one rolling standard deviation below its own recent norm, "
        "the rule prepares to hold SPY after a 3-month lag; otherwise it holds "
        "cash. It reduced drawdown in the search-phase OOS window, but it did "
        "so by sitting out much of the market and giving up annual return."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the ISM Services PMI gap to 50, measured as a rolling z-score over a 120-month window, is below -1.0 (applied with a 3-month lead); otherwise hold cash.

If-then form:
- **IF** `ism_services_gap_50` rolling z-score (120-month) is **below -1.0** -> hold SPY after the lag.
- **ELSE** -> hold cash.

Search-phase OOS results (2018-10-31 to 2025-10-31, no holdout final exam yet): Sharpe 1.54 vs 0.88 buy-and-hold; annualized return 9.8% vs 15.1%; maximum drawdown -3.8% vs -23.9%; 17 OOS position changes; annual turnover 2.4; OOS win rate 23.5%.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the ISM Services PMI from the project Data Master workbook (the relevant ISM series is not available on the public FRED API) and carries the latest released monthly value forward to the decision date. Second, it computes the gap to 50 (PMI minus 50), the natural expansion/contraction distance. Third, it standardizes that gap as a rolling z-score over a 120-month window and compares it with the -1.0 threshold, applying a 3-month lead before converting the comparison into a SPY-or-cash position.

This is intentionally simple. It does not forecast the services economy or model the survey's components. It asks whether unusually weak services sentiment has historically lined up with a better defensive SPY allocation.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read ISM Services PMI from the project data bundle (Data Master workbook, `ISM PMI` sheet).
2. Compute the gap to 50 (PMI minus 50).
3. Standardize as a rolling 120-month z-score.
4. Apply the 3-month lead before making the monthly SPY allocation decision.
5. Hold SPY when the lagged z-score is below -1.0; otherwise hold cash.

The warning label is central: this is `found_in_search`, not confirmed by a holdout final exam, and the lead-lag evidence runs from SPY to the survey, not the reverse.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe by stress episode. Protection is "
        "episode-dependent and concentrated, with COVID strong and several "
        "windows limited by insufficient OOS rows."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 3,385 valid "
        "searched combinations (median 0.77). The winner's 1.54 Sharpe is the "
        "maximum of the search, not a typical result."
    )

    CAVEATS_MD = """
**Why confidence is low:**

1. The lead-lag evidence runs backward: SPY Granger-predicts the survey at every lag 1-12, while the survey predicts SPY at none. ISM Services behaves as a coincident/lagging reflection of the market.
2. In-sample Sharpe is negative (-0.11) while OOS Sharpe is 1.54 -- a classic fragility red flag, suggesting the OOS edge rides specific episodes (notably COVID-19).
3. Bootstrap p-value is 0.073, which is suggestive but not significant at the 5% level.
4. A structural break is flagged at 2009-03, and cross-period durability is episode_concentrated.
5. The winner contradicts its own economic prior (procyclical expected, countercyclical observed).
6. The strategy improves drawdown but gives up annualized return versus buy-and-hold.

**What this means:** use the page as evidence for a candidate contrarian drawdown overlay, not as proof that ISM Services PMI leads the S&P 500.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the lagged 120-month rolling z-score of the ISM Services gap "
        "to 50 falls below -1.0, moving from 0% to 100% SPY exposure, and a "
        "SELL back to cash when the z-score recovers above the threshold. Over "
        "the OOS window the rule made only 17 such position changes -- a sparse "
        "overlay."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-04-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: ism_services_gap_50 z-score < -1.0; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Project Data Master.xlsx (`ISM PMI` sheet); not on FRED | ISM Services PMI (headline) | Monthly |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily and monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw ISM Services PMI level is a bounded diffusion index that is "
    "stationary in levels (no differencing required). It is transformed into a "
    "gap to 50 (PMI minus 50), a 3-month change, a 6-month change, a first "
    "difference, and a rolling z-score. The winning signal is "
    "`ism_services_gap_50` evaluated as a rolling 120-month z-score below "
    "-1.0. The daily panel carries the latest released monthly value forward "
    "with a `days_since_release` feature, so the strategy does not use future "
    "survey information."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation / quartile sorting | Is the raw direction procyclical or counter-cyclical? | Simple descriptive check before inference |
| Pre-whitened CCF | At which offsets do the series echo each other? | Filters autocorrelation that can fake lead-lag structure |
| Toda-Yamamoto Granger | Do lagged survey values improve SPY forecasts -- or the reverse? | Formal lead-lag test, robust to integration order |
| Local projections | What is the forward SPY response across horizons? | Horizon-by-horizon response check |
| Quantile regression | Does the signal work differently in weak vs strong markets? | Separates tail-risk from upside-state behavior |
| Transfer entropy | Is there nonlinear information flow, and in which direction? | Model-free nonlinear robustness check |
| HMM regimes | Which months are unusual survey regimes? | Backdrop and regime context, not the winning signal |
| Structural break / cross-period | Is the relationship stable over time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: ISM Services transforms x threshold rules x strategy families x orientations x leads x lookbacks. The final tournament file has 4,880 benchmark-excluded strategy combinations plus one BENCHMARK row. Of those, 3,385 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `ism_services_gap_50 / T3_zscore_neg_1.0 / P1_long_cash / L3 / LB120`.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/ism_services_spy/evidence_status.json` marks the pair `found_in_search`. The lead-lag evidence runs from SPY to the survey, reinforcing the low-confidence label.
"""

_REFERENCES_MD = """
1. Institute for Supply Management, Services (Non-Manufacturing) PMI report.
2. Yahoo Finance, SPY adjusted price history.
3. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
4. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
6. Simonsohn, U., Simmons, J. P. & Nelson, L. D. (2020). "Specification curve analysis."
7. Bailey, D. H. & Lopez de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Out-of-sample window 2018-10-31 to 2025-10-31, 85 monthly "
        "observations; in-sample ends 2018-09-30. Total tournament count is "
        "4,880 benchmark-excluded strategy combinations; 3,385 are valid. "
        "Evidence status: found_in_search."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the ISM Services analysis. The most "
        "important limitation is that the lead-lag tests point backward (SPY "
        "predicts the survey), the in-sample Sharpe is negative, and the "
        "winning rule still needs a frozen-rule holdout test."
    ),
)
