"""UNRATE x SPY pair configuration (Rule APP-PT1)."""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "Unemployment Rate and SPY"
    PAGE_SUBTITLE = (
        "Can the U.S. unemployment rate be used to confirm a recession and "
        "a recovery in the S&P 500 (SPY) cycle?"
    )

    HEADLINE_H2 = ""

    PLAIN_ENGLISH = (
        "UNRATE is the U.S. civilian unemployment rate. It measures the share "
        "of the labor force that is unemployed and actively looking for work. "
        "This pair tests whether unemployment level and change signals can "
        "improve SPY timing. Because unemployment is usually lagging, the "
        "result should be read as regime context, not as an early recession "
        "alarm."
    )

    WHERE_THIS_FITS = (
        "This is a labor-market stress signal for broad U.S. equities. It "
        "belongs in the portal as a defensive macro overlay: useful for "
        "context and drawdown control, but not a standalone forecast."
    )

    ONE_SENTENCE_THESIS = (
        "This pair tests whether the U.S. unemployment rate can help confirm "
        "recession and recovery phases for SPY: rising unemployment points to "
        "labor-market stress, while stabilizing or falling unemployment can "
        "support a recovery read."
    )

    KPI_CAPTION = (
        "the search-phase OOS winner uses the current 6-month change in "
        "UNRATE and a rolling 60-month 75th percentile threshold. It earns "
        "Sharpe 1.11 versus 0.99 for buy-and-hold."
    )

    HERO_TITLE = "U.S. Unemployment Rate vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: UNRATE is shown with SPY on the same time axis. "
        "Recession bands show National Bureau of Economic Research recession "
        "periods for historical context."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by UNRATE Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1, the lowest unemployment "
        "regime, to Q4, the highest unemployment regime. In this sample, "
        "higher UNRATE quartiles have higher forward SPY Sharpe, which fits "
        "a lagging-cycle or recovery setup more than a clean warning signal."
    )

    NARRATIVE_SECTION_1 = """
### The Hypothesis

The unemployment rate measures the share of the labor force that is unemployed and actively looking for work. It is a direct labor-market stress indicator. When demand slows, companies often try to protect margins by delaying hiring, cutting hours, or reducing headcount. When demand starts to recover, companies usually wait until sales, orders, and cash flow look more stable before they hire aggressively again.

The hypothesis is that the unemployment rate can help confirm recession and recovery phases for SPY. A rising unemployment rate can confirm recession stress because it shows that weaker demand has reached company staffing decisions. A stabilizing or falling unemployment rate can support a recovery read because it suggests the labor market is no longer deteriorating and companies may be moving from cost control back toward growth. For SPY, the signal is therefore tested as a confirmation and timing overlay, not as an early warning indicator.

### Why Timing Is Difficult

UNRATE can stay elevated while SPY rallies. It can also rise sharply during recessions, when equity risk is still high. This dashboard therefore treats the pair as a searched labor-cycle overlay. The result is useful because the backtest found a smoother long/cash path, but the economics should not be overstated as direct causality.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "UNRATE rose after the equity bear market had already begun. "
                "This episode shows why labor data can confirm stress rather "
                "than warn before the first market move."
            ),
            "caption": "Dot-Com: labor stress followed the market break.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The unemployment rate climbed through the Global Financial "
                "Crisis and remained high into the early recovery. The signal "
                "is useful for stress context, but exact equity timing is hard."
            ),
            "caption": "GFC: clear stress signal, late market timing.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "UNRATE spiked suddenly during coronavirus disease 2019 "
                "(COVID-19). The shock was exogenous, and the labor-market "
                "series moved too abruptly to be a normal cycle guide."
            ),
            "caption": "COVID: extreme labor shock, fast market recovery.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "During the 2022 rate-hike shock, unemployment stayed low "
                "while SPY sold off. This is the key caveat: labor data can "
                "miss valuation-driven equity drawdowns."
            ),
            "caption": "2022: low unemployment did not prevent an equity drawdown.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is useful but imperfect. UNRATE confirms recessions and labor stress clearly, but it often arrives after markets have moved. The strongest reading is not "unemployment predicts every drawdown"; it is that labor-market regimes can help size equity exposure after stress has become visible.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this labor-market story survives "
        "correlation, lead-lag, regime, and strategy checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Mechanism: correlation compares one unemployment signal with future "
        "SPY returns and asks whether they tend to move in the same direction. "
        "This is a basic linear test. It does not prove causality; it only "
        "checks whether higher or lower unemployment readings are associated "
        "with later SPY performance."
    ),
    question="Does a higher unemployment rate line up with better or worse future SPY returns?",
    how_to_read=(
        "Read each cell as a correlation coefficient and P-value pair. The "
        "correlation coefficient ranges from -1 to +1: positive means the "
        "unemployment signal and future SPY returns move together; negative "
        "means they move in opposite directions; values near zero mean the "
        "linear relationship is weak. The P-value measures how likely it is "
        "to see a relationship this large if there were no real relationship. "
        "A P-value below 0.05 is usually treated as statistically meaningful."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: unemployment level has positive and statistically "
        "meaningful correlations with 3-, 6-, and 12-month forward SPY returns."
    ),
    observation=(
        "The strongest basic result is the unemployment-rate level versus "
        "12-month forward SPY return: correlation is about 0.21 with P-value "
        "near 0.00003. The 6-month forward result is also positive at about "
        "0.17 with P-value near 0.0008. Shorter 1-month results are weak and "
        "not statistically meaningful."
    ),
    interpretation=(
        "The result supports a lagging-cycle interpretation. High unemployment "
        "does not mean SPY must immediately fall; by the time unemployment is "
        "high, markets may already be pricing policy support or recovery. "
        "Correlation alone is still insufficient for trading, because it does "
        "not handle timing, thresholds, or regime changes."
    ),
    key_message="Basic correlation says unemployment is useful as recovery-cycle context, not as a simple immediate SPY warning signal.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Mechanism: Granger causality tests whether past unemployment values "
        "add forecasting information for SPY returns after SPY's own past "
        "returns are already considered. Despite the name, this is a "
        "forecasting test, not proof of economic cause and effect."
    ),
    question="Does UNRATE lead SPY returns in a formal lag test?",
    how_to_read=(
        "Each bar is an F-statistic for one monthly lag. A larger F-statistic "
        "means past unemployment added more forecasting power in that test. "
        "The P-value is the decision metric: P-value below 0.05 means the lag "
        "is statistically meaningful; P-value above 0.05 means the test does "
        "not provide strong evidence that unemployment leads SPY at that lag."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: no tested monthly lag has a statistically meaningful "
        "UNRATE-to-SPY Granger result."
    ),
    observation=(
        "Across lags 1 through 12, P-values are all far above 0.05. The first "
        "five lags have P-values around 0.75, 0.61, 0.75, 0.74, and 0.67. "
        "That means the test does not find reliable direct forecasting power "
        "from unemployment to SPY monthly returns."
    ),
    interpretation=(
        "This weakens any claim that unemployment is a clean leading indicator "
        "for SPY. The useful story is more modest: unemployment can confirm "
        "where the economy sits in the cycle, while the strategy search tests "
        "whether a threshold rule can turn that confirmation into a "
        "portfolio overlay."
    ),
    key_message="Granger evidence is weak, so the dashboard should frame UNRATE as confirmation context rather than proven prediction.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Mechanism: quartile analysis sorts history into four groups based on "
        "the unemployment-rate level, then compares SPY returns inside each "
        "group. This is a basic regime test: it asks whether low, middle, and "
        "high unemployment environments have different market outcomes."
    ),
    question="Do low and high unemployment regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the lowest unemployment regime and Q4 is the highest "
        "unemployment regime. Mean return is the average monthly SPY return "
        "inside the bucket. Sharpe is risk-adjusted return: higher means more "
        "return per unit of volatility. Sample size shows how many months are "
        "in each bucket."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Q4 has the highest forward SPY Sharpe in this "
        "sample, followed by Q3, Q2, then Q1."
    ),
    observation=(
        "Forward SPY Sharpe rises from about 0.60 in Q1 to 0.93 in Q4. "
        "Average monthly return also rises from about 0.78% in Q1 to about "
        "1.25% in Q4."
    ),
    interpretation=(
        "This does not mean high unemployment is good in a simple economic "
        "sense. It means the stock market may begin recovering while labor "
        "data still look bad. That is exactly why unemployment is better read "
        "as a confirmation and recovery-cycle signal than as an early warning "
        "signal."
    ),
    key_message="The regime result supports the recovery-confirmation hypothesis: high unemployment often appears after markets have already started looking forward.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Mechanism: pre-whitened cross-correlation first removes persistence "
        "from the unemployment signal, then checks whether cleaned changes in "
        "unemployment line up before or after SPY returns. This helps avoid "
        "mistaking slow-moving labor data for a real lead-lag relationship."
    ),
    question="At which offsets does the unemployment signal line up with SPY returns?",
    how_to_read=(
        "Lag tells where the relationship appears in time. A bar outside the "
        "confidence band means the correlation is unusually large relative to "
        "noise. Positive bars mean the two series move together; negative bars "
        "mean they move opposite ways. The confidence band is similar in "
        "spirit to a significance threshold."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the relationship is timing-sensitive and should "
        "not be read as a stable clock."
    ),
    observation=(
        "Most lags are inside the confidence band, but lags -4, -3, and -2 "
        "are significant and negative, with the strongest reading near -0.23 "
        "at lag -3."
    ),
    interpretation=(
        "The significant negative readings indicate that the timing "
        "relationship is not a simple one-way leading signal. The result is "
        "consistent with labor data reacting around market-cycle turning "
        "points rather than reliably forecasting each next SPY move."
    ),
    key_message="Cross-correlation says timing is irregular; unemployment helps frame the cycle, but it is not a precise market clock.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Mechanism: local projections estimate the SPY return response at "
        "several future horizons after a change in the unemployment signal. "
        "Instead of one average relationship, this method asks whether the "
        "effect appears after 1, 3, 6, or 12 months."
    ),
    question="How does SPY respond after the unemployment rate changes?",
    how_to_read=(
        "Each point is a coefficient, which estimates the future SPY return "
        "change associated with a one-unit move in the unemployment-change "
        "signal. The P-value shows whether that coefficient is statistically "
        "meaningful. R-squared measures how much of future SPY return "
        "variation the model explains; values near zero mean weak explanatory "
        "power."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: the local-projection results test the raw labor "
        "signal, not the final tournament rule."
    ),
    observation=(
        "The coefficients are positive but small across 1-, 3-, 6-, and "
        "12-month horizons. P-values are all above 0.05, and R-squared values "
        "are near zero."
    ),
    interpretation=(
        "The advanced test does not show a strong direct response from SPY to "
        "the raw unemployment-change signal. This is important because it "
        "separates the simple macro relationship from the final strategy: the "
        "winner depends on a threshold and portfolio rules, not on a strong "
        "raw local-projection effect."
    ),
    key_message="Local projections do not confirm a strong standalone unemployment-change effect; the useful result comes from the no-lag threshold strategy.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Mechanism: quantile regression checks whether the unemployment signal "
        "matters differently in weak, normal, and strong SPY return "
        "environments. It is an advanced tail-risk test: the signal might be "
        "irrelevant on average but useful in bad or very strong markets."
    ),
    question="Does UNRATE behave differently in market tails?",
    how_to_read=(
        "Compare the coefficient across quantiles. The 0.25 quantile describes "
        "weaker SPY return states, 0.50 is the middle, and 0.75 is stronger "
        "return states. The coefficient shows direction and size of the "
        "relationship. The P-value shows whether the coefficient is "
        "statistically meaningful."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the signal can matter differently across weak and "
        "strong return states."
    ),
    observation=(
        "The generated table shows the same small positive coefficient, about "
        "0.0042, at the 0.25, 0.50, and 0.75 quantiles, with P-value around "
        "0.27."
    ),
    interpretation=(
        "This does not provide strong evidence that the raw unemployment "
        "signal behaves differently across weak, normal, and strong SPY "
        "return states. The finding points back to the strategy layer: any "
        "edge is more likely coming from the threshold rule and the "
        "cycle-confirmation setup than from a broad quantile effect."
    ),
    key_message="Quantile regression is weak here; it does not show a reliable tail-specific unemployment effect.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Basic and Advanced Analysis",
    "overview": (
        "The evidence is organized as a step-by-step test of the unemployment "
        "rate and SPY relationship. First, the basic analysis checks whether "
        "unemployment levels or changes line up with later SPY returns through "
        "correlation, regime quartiles, and cross-correlation. Then the "
        "advanced analysis tests whether that relationship survives stricter "
        "methods: Granger causality, local projections, quantile regression, "
        "rolling correlation, and structural-break checks. The combined result "
        "supports a cautious cycle-confirmation overlay, not a strong causal "
        "forecast."
    ),
    "plain_english": (
        "How to read this page: each method starts with the mechanism, meaning "
        "what the test is trying to measure and why it is used. It then "
        "defines the main components. A coefficient shows the direction and "
        "size of the relationship. A P-value shows whether the result is "
        "statistically meaningful, with values below 0.05 usually treated as "
        "stronger evidence. R-squared shows how much of SPY return variation "
        "the model explains. An F-statistic measures whether lagged "
        "unemployment information improves a forecasting model. A confidence "
        "band marks the range where noise is expected, while Sharpe compares "
        "return with volatility and quartiles split the unemployment history "
        "into four regimes. After those definitions, each block states the "
        "actual result, explains what is behind the result, and connects the "
        "finding back to the hypothesis that unemployment is more useful for "
        "confirming recession and recovery phases than for forecasting every "
        "SPY move in advance."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "Cross-Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 45 strategy combinations with no extra "
        "tournament lag. It included seven UNRATE threshold transforms plus "
        "2-, 3-, and 4-month consecutive rise/fall trigger rules. The selected "
        "winner is `unrate_6m_chg / T_roll_p75 / P1_long_cash / L0`."
    ),
    "transition": (
        "**Transition:** the evidence is useful but not causal. The Strategy "
        "page shows the exact long/cash rule, threshold, and deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A No-Lag UNRATE Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the current 6-month change in "
        "UNRATE and a rolling 75th percentile threshold."
    )

    PLAIN_ENGLISH = (
        "After the tournament was conducted, the selected rule holds SPY when "
        "the current 6-month change in unemployment is above its rolling "
        "threshold. Otherwise it holds cash. The tournament also tested a "
        "streak strategy that sells after consecutive UNRATE increases and "
        "buys after consecutive UNRATE decreases."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/unrate_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/unrate_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/unrate_spy/tournament_results_20260717.csv"},
        {"label": "Stationarity tests", "path": "results/unrate_spy/stationarity_tests_20260717.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the current 6-month change in UNRATE is above its rolling 60-month 75th percentile threshold; otherwise hold cash.

**Tournament update:** the conducted tournament scanned 45 combinations with lead fixed at `L0`, so no extra tournament lag is applied. The grid included seven UNRATE threshold transforms plus a new consecutive-rise/fall strategy. The selected winner was `unrate_6m_chg / T_roll_p75 / P1_long_cash / L0`, meaning the strategy uses the current 6-month change in unemployment and compares it with the rolling 75th percentile threshold.

**Streak strategy tested:** the new candidate rule holds SPY by default, sells SPY after UNRATE rises for 2, 3, or 4 consecutive months, and buys SPY after UNRATE falls for the same number of consecutive months. In the OOS window, the 3-month streak candidate reached Sharpe 0.86 and the 2-month streak candidate reached Sharpe 0.72; the 4-month streak candidate behaved like buy-and-hold with no OOS trades and was not treated as a valid active strategy.

If-then form:
- **IF** current `unrate_6m_chg` is above the rolling 75th percentile threshold -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-01-31 to 2026-06-30): Sharpe 1.11 versus 0.99 buy-and-hold; annualized return 11.8% versus 15.4%; maximum drawdown -13.5% versus -23.9%; 27 OOS trades; annual turnover 2.87.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the U.S. unemployment rate (`UNRATE`) and converts it to month-end observations. Second, it computes the 6-month change in the unemployment rate. Third, it compares the current 6-month change with a rolling 60-month 75th percentile threshold. The tournament does not add a separate lag to the strategy rule. Separately, the tournament also tests whether 2, 3, or 4 consecutive monthly increases in UNRATE should sell SPY and whether the same number of consecutive monthly decreases should buy SPY.

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read UNRATE at month end.
2. Compute the 6-month change in UNRATE.
3. Compare the current value with its rolling 60-month 75th percentile threshold.
4. Hold SPY when the current signal is above the threshold; otherwise hold cash.
5. Recheck monthly.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The rule reduces damage in several "
        "periods, but it is not designed to make every crisis profitable."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the 6-month change in the U.S. "
            "unemployment rate; the target is SPY returns. The rolling "
            "correlation tests whether their linear relationship is stable "
            "through time. Large swings mean the strategy needs rolling "
            "thresholds and ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break test asks whether the "
            "UNRATE-SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. A larger break statistic "
            "means the relationship changed more materially across periods."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid no-lag "
        "strategy combinations. The grid includes threshold rules and "
        "consecutive UNRATE rise/fall trigger rules."
    )

    CAVEATS_MD = """
**Main caveats:**

1. UNRATE is lagging; it often confirms stress after markets have already moved.
2. Granger causality is weak in the generated test results, so this is not a proven causal forecast.
3. The result is marked `found_in_search`; it still needs a frozen-rule holdout confirmation.
4. SPY price sourcing can fall back to an existing local monthly panel if the live Yahoo Finance call is rate-limited.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the current 6-month UNRATE-change signal moves above its "
        "rolling 75th percentile threshold, taking exposure from 0% to 100% "
        "SPY. A SELL moves back to cash when the condition no longer holds."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: current unrate_6m_chg above rolling p75; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED | `UNRATE`, civilian unemployment rate | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the U.S. civilian unemployment rate, in percent. "
    "The pipeline constructs one-month, three-month, six-month, and "
    "twelve-month changes; a 60-month rolling z-score; a Sahm-style labor "
    "stress measure; and a recession-style labor stress flag. The Methodology "
    "page describes these signal transforms as current observable labor-market "
    "features. It does not assume that the test must use data from a fixed "
    "number of months earlier."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does UNRATE move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do low and high unemployment regimes behave differently? | Makes the labor-cycle story interpretable |
| Pre-whitened CCF | Is the timing relationship stable after filtering persistence? | Reduces false timing signals from autocorrelation |
| Granger causality | Does UNRATE information improve SPY forecasts? | Formal forecasting check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: UNRATE transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations, with lead fixed at `L0`. The tournament also tests a consecutive-rise/fall trigger strategy: sell SPY after UNRATE rises for 2, 3, or 4 consecutive months, and buy SPY after UNRATE falls for the same number of months. The Methodology page treats unemployment as an observable macro indicator and does not build the research design around a confirmation hypothesis or a fixed "from X months earlier" testing assumption.
"""

_REFERENCES_MD = """
1. Federal Reserve Economic Data (FRED), `UNRATE`, Civilian Unemployment Rate.
2. Yahoo Finance, SPY adjusted price history.
3. Sahm, C. (2019). "Direct Stimulus Payments to Individuals."
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
5. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Monthly sample from 1993-01-31 to 2026-06-30, with out-of-sample "
        "window 2017-01-31 to 2026-06-30. SPY history limits the usable "
        "sample even though UNRATE begins earlier."
    ),
    plain_english=(
        "This page documents how UNRATE was turned into testable signals, "
        "how the econometric checks were run, and how the tournament selected "
        "the final SPY allocation rule. The methodology is framed as a test "
        "of unemployment-rate information for SPY, not as a confirmation-only "
        "hypothesis and not as a requirement to use data from a fixed number "
        "of months earlier."
    ),
)
