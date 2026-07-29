"""UNRATE x SPY pair configuration (Rule APP-PT1)."""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "Unemployment Rate and SPY"
    PAGE_SUBTITLE = (
        "Can the U.S. unemployment rate be used to confirm a recession and "
        "a recovery in the S&P 500 (SPY) cycle?"
    )

    HEADLINE_H2 = (
        "## Sharpe 1.55 OOS: the searched rule holds SPY after labor-market "
        "stress has already moved through the cycle"
    )

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
        "The U.S. unemployment rate works best here as a delayed confirmation "
        "signal: when the 6-month change in unemployment has risen enough and "
        "is viewed with a 9-month lag, it can help identify recession stress "
        "and later recovery conditions for SPY."
    )

    KPI_CAPTION = (
        "the search-phase OOS winner uses the 6-month change in UNRATE, a "
        "rolling 60-month 75th percentile threshold, and a 9-month lead. It "
        "earns Sharpe 1.55 versus 0.99 for buy-and-hold."
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

The unemployment rate measures the share of the labor force that is unemployed and actively looking for work. It is a clear labor-market stress indicator, but it usually moves after the economy has already started to slow. When demand weakens, companies often protect margins by slowing hiring, reducing hours, or cutting jobs. When demand starts to recover, companies usually wait for evidence that sales and cash flow are improving before hiring aggressively again.

The hypothesis is that the unemployment rate can help confirm where the economy is in the recession-and-recovery cycle. A rising unemployment rate can confirm recession stress because it shows that weak demand has reached the labor market. A stabilizing or delayed unemployment signal can also help confirm recovery because equity markets may begin to look past the worst labor data once companies stop cutting jobs and investors expect earnings to improve. For SPY, the signal is therefore tested as a confirmation and timing overlay, not as an early warning indicator.

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
        "whether a delayed threshold rule can turn that confirmation into a "
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
        "signal, not the final lagged tournament rule."
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
        "winner depends on a threshold, a 9-month lag, and portfolio rules, "
        "not on a strong raw local-projection effect."
    ),
    key_message="Local projections do not confirm a strong standalone unemployment-change effect; the useful result comes from the delayed threshold strategy.",
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
        "edge is more likely coming from the delayed threshold rule and the "
        "cycle-confirmation setup than from a broad quantile effect."
    ),
    key_message="Quantile regression is weak here; it does not show a reliable tail-specific unemployment effect.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: UNRATE Is Useful, but Mostly as Lagging Regime Context",
    "overview": (
        "The evidence is organized from basic to advanced analysis. Basic "
        "tests ask whether unemployment regimes line up with future SPY "
        "returns. Advanced tests ask whether the relationship survives formal "
        "lead-lag, horizon-response, and tail-risk checks. The combined result "
        "supports a cautious cycle-confirmation overlay, not a strong causal "
        "forecast."
    ),
    "plain_english": (
        "This page first explains how each analysis works, then defines the "
        "main components such as coefficient, confidence band, F-statistic, "
        "P-value, R-squared, Sharpe, and quartile. After that, it states the "
        "actual result and what the finding means for the unemployment-rate "
        "and SPY hypothesis."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "Cross-Correlation"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 294 valid strategy combinations across seven "
        "UNRATE transforms, fixed and rolling thresholds, and leads from 0 to "
        "12 months. The selected winner is `unrate_6m_chg / T_roll_p75 / "
        "P1_long_cash / L9`."
    ),
    "transition": (
        "**Transition:** the evidence is useful but not causal. The Strategy "
        "page shows the exact long/cash rule, threshold, and deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged UNRATE Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the 6-month change in UNRATE, "
        "a rolling 75th percentile threshold, and a 9-month lead."
    )

    PLAIN_ENGLISH = (
        "After the tournament was conducted, the selected rule holds SPY when "
        "the 6-month change in unemployment from nine months earlier is above "
        "its rolling threshold. Otherwise it holds cash. This is a lagged "
        "labor-cycle rule, not a real-time recession forecast."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/unrate_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/unrate_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/unrate_spy/tournament_results_20260717.csv"},
        {"label": "Stationarity tests", "path": "results/unrate_spy/stationarity_tests_20260717.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the lagged 6-month change in UNRATE is above its rolling 60-month 75th percentile threshold; otherwise hold cash.

**Tournament update:** the conducted tournament scanned 294 valid combinations across seven UNRATE transforms, fixed and rolling thresholds, and monthly leads of 0, 1, 2, 3, 6, 9, and 12 months. The selected winner was `unrate_6m_chg / T_roll_p75 / P1_long_cash / L9`, meaning the strategy uses the 6-month change in unemployment, compares it with the rolling 75th percentile threshold, and applies the signal with a 9-month delay.

If-then form:
- **IF** `unrate_6m_chg` from 9 months earlier is above the rolling 75th percentile threshold -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-01-31 to 2026-06-30): Sharpe 1.55 versus 0.99 buy-and-hold; annualized return 13.0% versus 15.4%; maximum drawdown -9.8% versus -23.9%; 25 OOS trades; annual turnover 2.65.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the U.S. unemployment rate (`UNRATE`) and converts it to month-end observations. Second, it computes the 6-month change in the unemployment rate. Third, it applies a 9-month lag before the SPY allocation is set. Finally, the lagged signal is compared with a rolling 60-month 75th percentile threshold.

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read UNRATE at month end.
2. Compute the 6-month change in UNRATE.
3. Compare the value from 9 months earlier with its rolling 60-month 75th percentile threshold.
4. Hold SPY when the lagged signal is above the threshold; otherwise hold cash.
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
        "What this shows: OOS Sharpe distribution across valid searched "
        "strategy combinations, with the selected rule highlighted as the "
        "best search-phase result."
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
        "BUY when the lagged 6-month UNRATE-change signal moves above its "
        "rolling 75th percentile threshold, taking exposure from 0% to 100% "
        "SPY. A SELL moves back to cash when the condition no longer holds."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: lagged unrate_6m_chg above rolling p75; position 0% to 100%",
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
    "stress measure; and a recession-style labor stress flag. The winning "
    "signal is `unrate_6m_chg`, the 6-month change in unemployment, used with "
    "a 9-month lead and a rolling 60-month 75th percentile threshold."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does UNRATE move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do low and high unemployment regimes behave differently? | Makes the labor-cycle story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past UNRATE information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: UNRATE transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x lead times. The final tournament has 294 valid strategy combinations. The winning rule is `unrate_6m_chg / T_roll_p75 / P1_long_cash / L9`.
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
        "the final SPY allocation rule."
    ),
)
