"""UNRATE x SPY pair configuration (Rule APP-PT1)."""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Unemployment Rate as a Defensive SPY Timing Signal"
    PAGE_SUBTITLE = (
        "U.S. unemployment rate (FRED UNRATE) x S&P 500 (SPY), monthly "
        "labor-market stress signals tested against SPY returns."
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
        "SPY timing improves in the searched sample when the 6-month change "
        "in unemployment is filtered through a 9-month lag, but the economics "
        "are lagging and regime-dependent."
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
        "Recession bands and Sahm-style labor-stress shading show when the "
        "labor market was under pressure."
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
### Headline Findings

The winning strategy is a **6-month unemployment-change rule**. It looks at the 6-month change in UNRATE, waits nine months before applying the signal, and holds SPY only when the lagged signal is above its rolling 60-month 75th percentile threshold. Out-of-sample, this rule earns a Sharpe ratio of 1.55 versus 0.99 for buy-and-hold, with maximum drawdown of -9.8% versus -23.9%.

### The Labor-Market Hypothesis

The unemployment rate is one of the clearest indicators of economic stress, but it usually moves late. Companies tend to cut jobs after demand has already slowed, and unemployment can keep rising after markets have started to recover.

That makes the hypothesis different from a classic leading indicator. A rising unemployment signal may identify a stressed regime, but the best equity opportunity can arrive after the stress is visible and policy or market expectations have already adjusted. The selected 9-month lag supports that interpretation: the rule is not buying the first unemployment uptick; it is acting after the signal has aged.

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
        "Correlation measures whether UNRATE and future SPY returns move "
        "together in a roughly linear way."
    ),
    question="Does a higher unemployment rate line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and correlation type. Positive values "
        "mean higher labor stress lines up with stronger future SPY returns; "
        "negative values mean the opposite."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the relationship is not a simple recession-warning "
        "line. The pair behaves more like a lagged cycle signal."
    ),
    observation=(
        "UNRATE is persistent and lagging, so the linear relationship depends "
        "on horizon and on whether the market is already looking past the "
        "labor downturn."
    ),
    interpretation=(
        "Correlation alone is not enough to trade the pair. The more relevant "
        "question is whether a lagged unemployment-change threshold improves "
        "portfolio behavior."
    ),
    key_message="UNRATE is useful as regime context, not as a simple linear SPY predictor.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does UNRATE lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show F-statistics by monthly lag. The source CSV p-values show "
        "whether the relationship is statistically meaningful."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: UNRATE-to-SPY p-values are not significant at lags "
        "1-5 in the generated table."
    ),
    observation=(
        "The generated Granger table shows weak UNRATE-to-SPY evidence across "
        "lags 1-5."
    ),
    interpretation=(
        "This prevents a strong causal claim. The strategy should be framed "
        "as a searched allocation overlay, not proof that unemployment causes "
        "future SPY returns."
    ),
    key_message="Formal lead-lag evidence is weak; use the signal cautiously.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by UNRATE level and compares "
        "subsequent SPY returns across labor-market regimes."
    ),
    question="Do low and high unemployment regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the lowest unemployment regime; Q4 is the highest unemployment "
        "regime. Compare Sharpe, average return, and sample size across the "
        "four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: Q4 has the highest forward SPY Sharpe in this "
        "sample, followed by Q3, Q2, then Q1."
    ),
    observation=(
        "Forward SPY Sharpe rises from about 0.56 in Q1 to 0.93 in Q4."
    ),
    interpretation=(
        "This is consistent with a lagging-cycle setup: by the time "
        "unemployment is high, equity markets may already be pricing recovery "
        "or policy support."
    ),
    key_message="High unemployment regimes are not automatically bad for forward SPY returns.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters persistence before testing "
        "whether one series tends to move before or after the other."
    ),
    question="At which offsets does the unemployment signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the confidence band mark unusual lead-lag correlation "
        "after filtering autocorrelation."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the relationship is timing-sensitive and should "
        "not be read as a stable clock."
    ),
    observation=(
        "UNRATE is highly persistent, so filtering persistence is important "
        "before reading lead-lag bars."
    ),
    interpretation=(
        "The chart supports treating the pair as a regime overlay with "
        "variable timing rather than a mechanical forecast."
    ),
    key_message="Labor-cycle timing is irregular.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the unemployment signal."
    ),
    question="How does SPY respond after the unemployment rate changes?",
    how_to_read=(
        "Each point is an estimated future SPY response after a one-unit move "
        "in the 6-month UNRATE change signal. Confidence bands show estimation "
        "uncertainty."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: the local-projection results test the raw labor "
        "signal, not the final lagged tournament rule."
    ),
    observation=(
        "The chart helps separate raw macro relationships from the searched "
        "allocation rule."
    ),
    interpretation=(
        "If the response varies by horizon, that supports using explicit "
        "lead times in the tournament instead of assuming an immediate effect."
    ),
    key_message="The horizon matters for UNRATE signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the unemployment signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does UNRATE behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means the unemployment signal has a stronger association "
        "with that part of the SPY return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the signal can matter differently across weak and "
        "strong return states."
    ),
    observation=(
        "Tail sensitivity is important because labor stress is most relevant "
        "around recessions and recoveries."
    ),
    interpretation=(
        "A state-dependent result is more plausible than one constant UNRATE "
        "effect across all markets."
    ),
    key_message="UNRATE should be read through regimes and tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: UNRATE Is Useful, but Mostly as Lagging Regime Context",
    "overview": (
        "The evidence supports a cautious labor-cycle overlay. The strategy "
        "winner improves search-phase OOS Sharpe, but formal lead-lag evidence "
        "is weak and the indicator is economically lagging."
    ),
    "plain_english": (
        "This page asks whether the unemployment rate helps with SPY timing. "
        "The answer is: partly. The best rule uses a delayed unemployment "
        "change, so it should be treated as a regime and recovery signal, not "
        "as an early warning system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
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
        "The rule holds SPY when the 6-month change in unemployment from nine "
        "months earlier is above its rolling threshold. Otherwise it holds "
        "cash. This is a lagged labor-cycle rule, not a real-time recession "
        "forecast."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/unrate_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/unrate_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/unrate_spy/tournament_results_20260717.csv"},
        {"label": "Stationarity tests", "path": "results/unrate_spy/stationarity_tests_20260717.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the lagged 6-month change in UNRATE is above its rolling 60-month 75th percentile threshold; otherwise hold cash.

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
