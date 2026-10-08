"""Portland Cement Shipments x SPY pair configuration (Rule APP-PT1).

New pair, MONTHLY construction-activity pair. Portland Cement Shipments
(nominal $, monthly; Data Master) is a LEADING, production-class indicator
whose economic PRIOR is PROCYCLICAL (firm/rising shipment growth -> risk-on).
The nominal-dollar LEVEL is non-stationary (ADF fails to reject a unit root,
p = 0.22; KPSS rejects stationarity), so every tested signal is a growth
transform (MoM/3m/6m/YoY %, YoY z-score, acceleration).

HONEST FRAMING (binding). This is a FOUND-IN-SEARCH candidate at LOW
confidence, not a validated or deployable edge, and -- unusually -- its
direction CONTRADICTS the economic prior. Every number below is sourced from
results/cement_spy/*:
  - The tournament winner (`cement_yoy` YoY growth / T_roll_p25 rolling-25th-
    percentile / COUNTERCYCLICAL / L4 months / P1_long_cash; OOS Sharpe 1.253
    vs 0.935 buy-and-hold) is the grid maximum over 468 combinations (all 468
    valid). The MEDIAN valid combo scores 0.656 -- it UNDERPERFORMS buy-and-
    hold (0.935) (winner_summary.json). The typical rule built on this
    indicator subtracts value.
  - DIRECTION CONTRADICTS THE PRIOR (the key caution). Cement-shipment growth
    is procyclical, but the search selected a COUNTERCYCLICAL / contrarian
    rule: it holds SPY when cement YoY growth FOUR MONTHS EARLIER was AT OR
    BELOW its rolling 25th percentile -- i.e. when construction activity was
    VERY WEAK. `interpretation_metadata.json` records expected_direction
    procyclical, observed_direction countercyclical, direction_consistent =
    false, confidence = low. Economically this can be rationalised (deep
    construction weakness tends to precede policy accommodation and marks a
    cyclical trough, and the 4-month lead gives a recovery time to reach
    equities), but a search maximum that reverses the prior is a reason for
    caution, not a selling point.
  - THE LEAD IS A SEARCH-SELECTED PARAMETER, NOT A VALIDATED FORECAST. The
    winner sits at L4 (it uses cement YoY from four months earlier), so it does
    make a nominal forward-lead claim -- but the formal lead-lag tests find no
    predictive content to support it: cement growth does NOT Granger-cause SPY
    at any tested lag (minimum p = 0.14 at lag 2) (granger_by_lag.csv);
    forward-return correlations are near zero at every horizon for the winning
    YoY signal (|r| <= 0.07), and the largest cell anywhere is acceleration vs
    1-month-forward SPY, r = 0.12, p = 0.085 -- not significant
    (core_models_20261008/correlations.csv); local projections are null at
    every horizon (no coefficient significant; trivial R^2)
    (local_projections.csv); and the pre-whitened cross-correlation has NO
    significant bar at any offset, lead or lag (ccf_prewhitened.csv). Read the
    4-month lead as a fitted parameter, not a proven forecast horizon.
  - The concurrent evidence is broadly PROCYCLICAL and therefore runs OPPOSITE
    to the winner: sorting months by cement YoY growth, the weakest-growth
    quartile Q1 has the worst concurrent SPY Sharpe (0.33) and the strongest
    quartile Q4 the best (1.12), with a non-monotonic middle (Q2 1.06, Q3 0.62)
    (regime_quartile_returns.csv). That the contemporaneous sort is procyclical
    while the winning rule is a lagged contrarian bet is an internal tension to
    disclose, not reconcile away.
  - The winner wins on RISK, not raw return: OOS annualized return is LOWER
    than buy-and-hold (12.1% vs 14.6%), but max drawdown is far smaller
    (-8.3% vs -23.9%) and volatility is low (9.5%), which is why the Sharpe
    (1.253 vs 0.935), Sortino (1.98) and Calmar (1.46) beat buy-and-hold. The
    win rate is BELOW 50% (31.4%): it earns its edge by sitting out drawdowns,
    not by winning most months. Turnover is moderate-to-high (3.5/yr, 30 OOS
    trades): an active in/out rule, not a set-and-forget overlay.
  - Stress behavior now favors the rule, because it is contrarian. It was flat
    (in cash, subperiod Sharpe 0.0) through the GFC and COVID windows while
    buy-and-hold fell (-1.03 and -0.66), and it did MUCH BETTER than
    buy-and-hold in the 2022 rate shock (+0.75 vs -0.76; +9.6% vs -18.2%),
    because firm nominal cement growth kept it in cash during the equity
    de-rating (subperiod_sharpe.csv). Note the GFC window predates the
    2017-start OOS sample.
  - Status is `found_in_search` (evidence_status.json): the winner still needs
    a frozen-rule holdout / final exam, and the adjacent-lead durability of the
    L4 choice should be checked (issue #28).
  - CAVEATS: the sample is SHORT, starting 2005-11 (SPY-and-cement overlap; no
    Dot-Com coverage). Cement shipments are NOT a Conference Board LEI
    component and NOT "new orders" -- they are a construction-activity series.
    The figures are nominal (not inflation-adjusted): in 2022 nominal sales
    stayed firm on rising prices even as equities de-rated. COVID 2020-21 is an
    extreme in-window outlier that can dominate the fit.

MONTHLY conventions: leads in MONTHS (winner L4, floored grid L2-14, no
look-ahead L0/L1); Sharpe annualized by sqrt(12); OOS window 2017-01-31 ->
2025-06-30 (102 months). Numbers sourced from results/cement_spy/
(winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, core_models_20261008/*,
regime_quartile_returns.csv, subperiod_sharpe.csv, granger_by_lag.csv,
stationarity_tests_20261008.csv, structural_break_cement_spy.json,
tournament_results_20261008.csv, tournament_validation_20261008/bootstrap.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Cement Shipments as a Contrarian SPY Overlay"
    PAGE_SUBTITLE = (
        "Portland Cement Shipments (Data Master) x S&P 500 (SPY), monthly "
        "construction-activity growth signals tested against SPY returns."
    )

    HEADLINE_H2 = (
        "## A search-phase rule with OOS Sharpe 1.25 vs 0.93 buy-and-hold -- "
        "but COUNTERCYCLICAL (it buys SPY after very weak cement growth), which "
        "CONTRADICTS the procyclical prior, and found-in-search on a short "
        "2005-start sample with no formal predictive edge"
    )

    PLAIN_ENGLISH = (
        "Portland Cement Shipments is the volume of cement U.S. producers ship "
        "each month -- an input to construction and infrastructure. Because "
        "cement is poured into projects that track the real-investment cycle, "
        "it is a LEADING, construction-activity indicator, and the economic "
        "prior is procyclical: firm, rising shipment growth signals an "
        "investment upswing and risk-on equities. The surprise here is that the "
        "winning rule runs the OTHER way -- it is COUNTERCYCLICAL. It holds SPY "
        "when cement year-on-year growth FOUR MONTHS EARLIER was at or below "
        "its rolling 25th percentile (construction activity was very weak), and "
        "otherwise sits in cash. The contrarian story is that deeply weak "
        "construction tends to mark a cyclical trough and precede policy "
        "support, with the 4-month lead giving a recovery time to reach stocks. "
        "Take this as a caution flag, not a strength: it reverses the prior, "
        "the formal lead-lag tests find no predictive edge, and it is a "
        "grid-search candidate at LOW confidence, not a validated or deployable "
        "edge."
    )

    WHERE_THIS_FITS = (
        "This is a construction-activity overlay for broad U.S. equities, and "
        "it belongs in the portal with a prominent caveat: the direction the "
        "search selected (buy SPY after very weak cement growth) CONTRADICTS "
        "the procyclical economic prior and the procyclical concurrent "
        "quartiles. It is a contrarian, found-in-search candidate on a short "
        "sample, not an early-warning forecast and not a validated edge. "
        "Readers should weigh the direction inconsistency, the sub-50% win "
        "rate, and the fact that the rule earns its Sharpe by cutting drawdowns "
        "(not by beating buy-and-hold on raw return) before taking it as "
        "anything more than a candidate."
    )

    ONE_SENTENCE_THESIS = (
        "Cement-shipment growth is procyclical with equities CONCURRENTLY "
        "(weakest-growth quartile has the worst SPY Sharpe, 0.33; strongest "
        "the best, 1.12) yet does NOT lead SPY in any formal test -- Granger is "
        "insignificant at every lag (min p = 0.14), local projections are null, "
        "and the pre-whitened cross-correlation has no significant bar at any "
        "offset -- so the search's best rule, a COUNTERCYCLICAL 4-month-lead "
        "long/cash filter that buys SPY after very weak cement growth with OOS "
        "Sharpe 1.25 vs 0.93, both CONTRADICTS the procyclical prior and is "
        "found-in-search on a short 2005-start sample, not a validated edge."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 102-month window (2017-01-31 -> 2025-06-30). The winner was found "
        "as the best of 468 valid combinations, and the MEDIAN valid combo "
        "(0.656) UNDERPERFORMS buy-and-hold (0.935) -- the typical rule "
        "subtracts value. The winner wins on RISK, not raw return: OOS "
        "annualized return is LOWER than buy-and-hold (12.1% vs 14.6%), but max "
        "drawdown is far smaller (-8.3% vs -23.9%) and volatility is 9.5%, so "
        "the Sharpe (1.25 vs 0.93) beats buy-and-hold by cutting losses. The "
        "win rate is only 31.4% -- it earns its edge by sitting out drawdowns. "
        "Turnover is moderate-to-high (3.5/yr, 30 trades). Read the Sharpe as a "
        "single-sample search result from a rule that CONTRADICTS the "
        "procyclical prior, not a proven edge. Sharpe ratios use monthly "
        "sqrt(12) annualization."
    )

    HERO_TITLE = "Portland Cement Shipments vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the cement-shipment level (nominal $, left axis) is "
        "shown with SPY on the same time axis, NBER recessions shaded. The "
        "series begins in 2005 (SPY-and-cement overlap), so there is no "
        "Dot-Com coverage. The traded signal is not the level (it is "
        "non-stationary) but its year-on-year (YoY) growth. Watch the shaded "
        "recessions -- cement shipments collapsed through the 2008-09 housing "
        "bust and dipped in the 2020 COVID shock."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Cement-Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest cement-shipment "
        "growth) to Q4 (strongest), with concurrent SPY Sharpe in each. The "
        "weakest-growth quartile Q1 is the worst (Sharpe 0.33) and the "
        "strongest Q4 the best (1.12). Q2 is also strong (1.06) and Q3 weaker "
        "(0.62), so the middle is non-monotonic rather than a smooth step-up. "
        "The contemporaneous message is PROCYCLICAL -- but note this runs "
        "OPPOSITE to the winning rule, which is COUNTERCYCLICAL on a 4-month "
        "lag (it buys SPY after weak growth). That tension is the pair's key "
        "caution. Descriptive and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **countercyclical, 4-month-lead cement-growth filter**. It holds SPY when cement year-on-year growth four months earlier was at or *below* its five-year rolling 25th percentile (i.e. when construction-activity growth was *very weak*), and holds cash otherwise. Out-of-sample (2017-01 to 2025-06, 102 months), this rule earns a Sharpe of 1.25 versus 0.93 for buy-and-hold. It does so by cutting risk, not by compounding faster: its annualized return is actually *lower* than buy-and-hold (12.1% versus 14.6%), but its maximum drawdown is far smaller (-8.3% versus -23.9%) and its volatility is only 9.5%. The win rate is 31.4% -- below half -- so it wins by sitting out drawdowns, not by being right most months. The direction **contradicts** the economic prior, which is the pair's main caution, and the rule is a **found-in-search** candidate on a short sample, not a validated edge.

### The Construction-Activity Hypothesis (and why the winner reverses it)

Portland cement shipments measure the flow of cement into U.S. construction and infrastructure. Because cement is poured into projects that move with the real-investment cycle, it is a **leading, construction-activity** indicator, and the economic prior is that cement-shipment growth is **procyclical**: firm, rising shipments are risk-on for equities; slowing shipments are an early sign that construction and investment are cooling. The concurrent evidence supports that prior: sort months by cement growth and the weakest-growth quartile has the worst concurrent SPY Sharpe (0.33), while the strongest-growth quartile has the best (1.12).

The tournament's winning rule runs the **opposite** way. It is contrarian: it buys SPY precisely when cement growth four months earlier was *very weak*. The defensible economic story is that deeply weak construction tends to mark a cyclical trough and precede policy accommodation, and a 4-month lead gives the subsequent recovery time to show up in equities. But we flag this as a **caution, not a strength**: a search maximum that reverses the prior and also runs opposite to the procyclical concurrent sort deserves more skepticism, not less.

### Why This Is Not a Validated Forecast

The winner sits at a 4-month lead, so unlike a concurrent filter it does make a nominal forward-lead claim. The formal lead-lag tests do not support it. Cement-shipment growth does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.14 at lag 2; the lag-4 p-value is 0.31), forward-return correlations are near zero at every horizon for the winning YoY signal (|r| <= 0.07; the largest cell anywhere, acceleration vs 1-month-forward SPY, is r = 0.12 and not significant at 5%), and local projections are essentially null. The pre-whitened cross-correlation has **no** significant bar at any offset. So the 4-month lead is best read as a *search-selected parameter*, not a proven forecast horizon; this dashboard treats the rule as a contrarian construction-activity overlay whose status is found-in-search, not deployable.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Cement shipments collapsed through 2008-09 as the housing "
                "bust seized up construction. This window predates the "
                "2017-start out-of-sample period, so the strategy curve is flat "
                "here (subperiod Sharpe 0.0) while buy-and-hold fell sharply "
                "(-1.03). Read it as context for how extreme the cement "
                "collapse was, not as a traded result."
            ),
            "caption": "GFC: cement shipments collapsed with the housing bust 2008-09 (pre-OOS context; strategy untraded, buy-and-hold -1.03).",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Cement YoY growth dipped around the 2020 shock, but the plot "
                "does not show a clean sustained rebound afterward. The series "
                "stayed choppy and spent much of 2021 below zero, so the right "
                "interpretation is lingering disruption rather than a simple "
                "V-shaped cement recovery. Through this window the rule sat in "
                "cash and was flat (subperiod Sharpe 0.0) while buy-and-hold "
                "lost ground (-0.66). This is an extreme, exogenous in-window "
                "episode that can dominate the backtest fit -- read any rule "
                "that leans on it with caution."
            ),
            "caption": "COVID: cement YoY dipped then stayed choppy; the rule sat in cash (flat) while buy-and-hold fell -0.66.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Nominal cement sales stayed firm through 2022 because prices "
                "were rising, even as equities de-rated under higher interest "
                "rates. Because the rule is COUNTERCYCLICAL, firm cement growth "
                "is a reason for it to be in CASH -- and that is exactly where "
                "it sat during the 2022 selloff, so it dodged the drawdown. "
                "That is why it did much better than buy-and-hold here "
                "(subperiod Sharpe +0.75 vs -0.76; return +9.6% vs -18.2%). "
                "The nominal-dollar quirk that hurt a procyclical reading -- "
                "inflation keeping the growth signal firm while the market "
                "falls -- happens to help the contrarian rule, which treats "
                "firm growth as a signal to step aside."
            ),
            "caption": "2022: nominal sales stayed firm on inflation; the countercyclical rule held cash and dodged the selloff (+0.75 vs -0.76).",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show how a contrarian rule behaves across episodes. Two of the windows -- the GFC and COVID -- show the strategy flat (subperiod Sharpe 0.0): the GFC predates the 2017-start out-of-sample sample, and through COVID the rule sat in cash while buy-and-hold fell (-0.66). The decisive episode is the 2022 rate shock. Nominal cement sales stayed firm because inflation supported dollar sales, even while higher discount rates hurt equities. A procyclical rule would have read firm growth as a reason to stay long and would have been punished; the countercyclical winner did the opposite, treating firm growth as a reason to be in cash, and so it sat out the drawdown and **beat** buy-and-hold (+0.75 vs -0.76; +9.6% vs -18.2%). The sample starts in 2005, so there is no Dot-Com coverage. The honest reading is not "weak cement predicts rallies"; it is that a contrarian filter which steps aside when nominal cement growth is firm happened to avoid the 2022 equity de-rating -- a favorable but single-episode outcome on a short sample, from a rule that reverses the economic prior.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this construction-activity story "
        "survives correlation, lead-lag, regime, and strategy checks. The "
        "concurrent regime sort is procyclical, but the winning rule is "
        "countercyclical and the formal lead-lag evidence is absent -- so the "
        "winner is a contrarian, direction-inconsistent, found-in-search "
        "candidate, not a validated forecast."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether cement-shipment growth and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does faster cement-shipment growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values "
        "mean stronger cement growth lines up with stronger future SPY "
        "returns; pale cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the linear association is essentially zero at every "
        "tradeable horizon. The winning YoY-growth row is near zero at every "
        "horizon (|r| <= 0.07), and the largest cell anywhere is cement "
        "acceleration vs the 1-month-forward SPY return (r = 0.12, p = 0.085) "
        "-- not significant at 5%, and not a usable forecasting signal."
    ),
    observation=(
        "No transform shows a material linear association with forward SPY; the "
        "winning YoY-growth cells are near zero (|r| <= 0.07), and the largest "
        "cell anywhere is acceleration vs 1-month-forward SPY at r = 0.12 "
        "(p = 0.085)."
    ),
    interpretation=(
        "Correlation alone does not support trading the pair as a forecast. The "
        "winner's apparent 4-month lead is not backed by any linear predictive "
        "association; it is a search-selected parameter."
    ),
    key_message="Cement growth is not a linear SPY predictor at any tradeable horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does cement-shipment growth lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across lags 1-12 is 0.14 (lag 2), and the winner's own lag 4 is 0.31 "
        "-- cement growth does not Granger-cause SPY returns."
    ),
    observation=(
        "Across all twelve monthly lags the cement->SPY p-value never falls "
        "below 0.14 (lag 2); at the winner's 4-month lead p = 0.31. The "
        "F-statistics are small. There is no formal evidence of lead-lag "
        "causality."
    ),
    interpretation=(
        "This rules out a causal forecast claim, including at the winner's "
        "4-month lead. The strategy must be framed as a searched, contrarian "
        "construction-activity overlay, not proof that weak cement growth "
        "causes better future SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.14, lag-4 p = 0.31); cement does not lead SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by cement YoY growth and compares "
        "concurrent SPY returns across construction-activity regimes."
    ),
    question="Do weak and strong construction-activity regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the weakest-growth regime; Q4 is the strongest. Compare Sharpe, "
        "average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: concurrently PROCYCLICAL -- the weakest-growth "
        "quartile Q1 has the worst concurrent SPY Sharpe (0.33) and the "
        "strongest Q4 the best (1.12), with a non-monotonic middle (Q2 1.06, "
        "Q3 0.62). Note this runs OPPOSITE to the winning rule, which is "
        "countercyclical on a 4-month lag."
    ),
    observation=(
        "Concurrent SPY Sharpe is lowest in the weakest-growth quartile "
        "(Q1 0.33) and highest in the strongest (Q4 1.12); the middle is "
        "non-monotonic (Q2 1.06, Q3 0.62). Each quartile has 56 months."
    ),
    interpretation=(
        "The concurrent pattern fits a procyclical construction-activity story "
        "-- but it is DIRECTION-INCONSISTENT with the tournament winner, which "
        "buys SPY after weak growth on a 4-month lag. That the contemporaneous "
        "sort and the winning rule point in opposite directions is a caution: "
        "the winner's contrarian edge is not corroborated by the concurrent "
        "regime evidence."
    ),
    key_message="Stronger cement growth coincides with better SPY conditions -- procyclical, the OPPOSITE of the countercyclical winner's direction.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does cement growth line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "cement leads; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: NO bar is significant at any offset -- neither a "
        "cement-leads-SPY nor a SPY-leads-cement signal survives filtering for "
        "autocorrelation. There is no coherent lead-lag echo, including at the "
        "winner's 4-month offset."
    ),
    observation=(
        "Every cross-correlation, lead-side and lag-side, sits inside the "
        "confidence band; the largest magnitude anywhere (~0.11 at offset -10) "
        "is not significant."
    ),
    interpretation=(
        "There is no window in which cement growth foreshadows SPY, and none in "
        "which SPY foreshadows cement. Consistent with the null Granger and "
        "local-projection results, the pair carries no forecasting lead to "
        "justify the winner's 4-month lag."
    ),
    key_message="No cross-correlation is significant at any offset; the pair shows no lead-lag forecast.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the cement-growth signal."
    ),
    question="How does SPY respond after cement growth changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "cement-growth signal. Coefficients near zero mean no detectable "
        "effect."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are essentially zero across all "
        "horizons (1, 3, 6, 12 months), none statistically significant "
        "(p from 0.28 to 0.99), with negligible R^2."
    ),
    observation=(
        "Point estimates are near zero at every horizon and no coefficient is "
        "significant; the explained variance is trivial throughout (max R^2 "
        "about 0.005 at horizon 1)."
    ),
    interpretation=(
        "There is essentially no linear predictive content at any horizon. "
        "Nothing here rescues a forward-looking reading of the indicator or "
        "the winner's 4-month lead."
    ),
    key_message="Local projections are null; cement growth carries no useful linear forecast for SPY.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the cement signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does cement growth behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: real quantile-regression slopes are small but NOT "
        "constant -- they drift from mildly positive in the lower (deep-selloff) "
        "tail to mildly negative in the upper tail. A formal cross-quantile "
        "equality test REJECTS a uniform slope (Wald p=0.004)."
    ),
    observation=(
        "No individual quantile slope is statistically significant, but a "
        "bootstrap Wald test rejects equality of the slopes across quantiles "
        "(p=0.004): the coefficient falls monotonically from about +0.0002 at "
        "tau=0.10 to about -0.0001 at tau=0.90."
    ),
    interpretation=(
        "The cement-SPY association is state-dependent rather than flat: it is "
        "weakly supportive in deep-selloff states and weakly adverse in strong-up "
        "states. The individual effects are too small and imprecise to trade, but "
        "the earlier 'flat / no tail sensitivity' claim does not hold -- it came "
        "from a bug (OLS repeated across quantiles), and the real test rejects it."
    ),
    key_message="Cement growth's SPY association varies across return quantiles (Wald p=0.004) -- small and untradeable, but not the uniform null the chart previously implied.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Cement Is Procyclical Context, but the Winner Is Contrarian and Not a Forecast",
    "overview": (
        "The evidence supports, at most, a cautious contrarian overlay -- and "
        "flags a direction inconsistency. The strategy winner improves "
        "search-phase OOS Sharpe (1.25 vs 0.93), but its COUNTERCYCLICAL "
        "direction (buy SPY after very weak cement growth) CONTRADICTS both the "
        "procyclical prior and the procyclical concurrent quartiles, and the "
        "formal lead-lag evidence is absent (Granger min p = 0.14, lag-4 "
        "p = 0.31; local projections null; CCF has no significant bar at any "
        "offset). The 4-month lead is a search-selected parameter, not a "
        "validated forecast horizon."
    ),
    "plain_english": (
        "This page asks whether cement-shipment growth helps time SPY. The "
        "answer is: as a contrarian overlay, maybe, but with caveats; as a "
        "forecast, no. The concurrent quartiles are procyclical (weak growth = "
        "worse market), yet the winning rule runs the OPPOSITE way -- it buys "
        "SPY four months after growth was very weak. The causal tests find no "
        "lead. Treat it as a contrarian, direction-inconsistent candidate, not "
        "an early-warning system, and note it is found-in-search."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 468 strategy combinations (all 468 valid) "
        "across six cement growth transforms, fixed and rolling thresholds, "
        "procyclical/countercyclical orientations, and a publication-lag-"
        "floored lead grid from 2 to 14 months (no look-ahead L0/L1). The "
        "selected winner is `cement_yoy / T_roll_p25 / P1_long_cash "
        "countercyclical / L4`, with OOS Sharpe 1.253. The MEDIAN valid combo "
        "scores 0.656 -- below buy-and-hold's 0.935 -- and the runner-up "
        "(`mom / T_roll_p25 / countercyclical / L4`, 1.182) shares the same "
        "rolling-25th-percentile threshold, contrarian orientation and 4-month "
        "lead, so the top of the surface is a small cluster of contrarian "
        "rolling-threshold rules rather than a single fragile cell. That is "
        "mildly reassuring, but the median result still shows the typical rule "
        "subtracts value, and the winning direction reverses the prior."
    ),
    "transition": (
        "**Transition:** the evidence is procyclical context but a contrarian, "
        "direction-inconsistent winner, and it is not causal. The Strategy page "
        "shows the exact long/cash rule, its risk-reducing (not "
        "return-enhancing) edge over buy-and-hold, the sub-50% win rate, the "
        "turnover, and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Countercyclical, 4-Month-Lead Cement-Growth Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using YoY cement-shipment growth, a "
        "rolling 25th-percentile threshold, a COUNTERCYCLICAL orientation, and "
        "a 4-month lead -- it buys SPY after very weak cement growth, which "
        "CONTRADICTS the procyclical prior; found-in-search on a short sample, "
        "active, and risk-reducing rather than return-enhancing."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when cement year-on-year growth four months earlier "
        "was at or BELOW its five-year rolling 25th percentile (i.e. when "
        "construction-activity growth was very weak); otherwise it holds cash. "
        "This is a COUNTERCYCLICAL / contrarian construction-activity filter -- "
        "the OPPOSITE of the procyclical prior for a leading indicator -- not a "
        "real-time recession forecast. Judge it by how it earns its edge: it "
        "gives up some raw return (12.1% vs 14.6% buy-and-hold) in exchange for "
        "a much smaller drawdown (-8.3% vs -23.9%) and low volatility (9.5%), "
        "for a higher Sharpe (1.25 vs 0.93). The win rate is only 31.4% -- it "
        "wins by avoiding drawdowns -- it is found-in-search, and it trades "
        "actively (turnover 3.5/yr)."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/cement_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/cement_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/cement_spy/tournament_results_20261008.csv"},
        {"label": "Stationarity tests", "path": "results/cement_spy/stationarity_tests_20261008.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when cement year-on-year growth *four months ago* is at or BELOW its five-year rolling 25th percentile (i.e. when construction-activity growth was *very weak*); otherwise hold cash. This is a countercyclical / contrarian rule, and it REVERSES the procyclical prior.

If-then form:
- **IF** `cement_yoy` (lagged 4 months) is at or below its 60-month rolling 25th percentile -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-01-31 to 2025-06-30, 102 months): Sharpe 1.25 versus 0.93 buy-and-hold; annualized return 12.1% versus 14.6% (LOWER than buy-and-hold); maximum drawdown -8.3% versus -23.9% (much smaller); annualized volatility 9.5%; win rate 31.4% (below half -- it wins by avoiding drawdowns); 30 trades; annual turnover 3.5 (an active in/out rule). The edge over buy-and-hold is a risk-reduction edge, the direction contradicts the prior, and the result is found-in-search.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads Portland Cement Shipments (nominal $) at month-end. Second, it computes year-on-year growth (`cement_yoy`, the 12-month percent change). Third, that growth, *lagged four months*, is compared with its 60-month rolling 25th percentile: when the lagged growth is at or BELOW that threshold (construction was very weak four months ago), hold SPY; otherwise hold cash (the countercyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return (here lower than buy-and-hold). Maximum Drawdown is the largest peak-to-trough loss (here much smaller than buy-and-hold). Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return (here below half -- the edge comes from avoiding drawdowns, not from winning most months).
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read Portland Cement Shipments at month end.
2. Compute year-on-year (12-month) percent growth.
3. Take the value from FOUR months ago and compare it with its trailing 60-month rolling 25th percentile.
4. Hold SPY when that lagged growth is at or BELOW the rolling 25th percentile (construction was very weak four months ago); otherwise hold cash.
5. Recheck monthly. Turnover is 3.5/yr: the rule flips exposure several times a year, so transaction costs matter.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The contrarian rule was flat (in cash, "
        "Sharpe 0.0) through the pre-OOS GFC and the COVID window while "
        "buy-and-hold fell (-1.03 and -0.66), and it did MUCH BETTER than "
        "buy-and-hold in the 2022 rate shock (+0.75 vs -0.76), when firm "
        "nominal cement sales kept the contrarian rule in cash and out of the "
        "equity de-rating. Dot-Com is omitted because the cement/SPY overlap "
        "starts in 2005. The stress record favors the rule -- but note it rests "
        "heavily on the single 2022 episode."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: this chart tracks the rolling correlation between "
            "Cement Shipment Growth and SPY returns. The correlation is weak "
            "and changes sign, ranging from about -0.22 to +0.18, so one fixed "
            "linear relationship may hide periods when the two move together "
            "and periods when they move in opposite directions. A single "
            "model therefore needs checks across different periods before "
            "being treated as representative of the whole sample; many "
            "crossings are close to zero and may reflect sampling noise. "
            "This chart alone does not establish a structural break or "
            "forecasting skill, and even stable correlation would not by "
            "itself validate a fixed model."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "cement/SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. A larger break statistic "
            "means the relationship shifted more materially across periods "
            "(here the max absolute rolling-correlation z-score reaches 2.9)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead (the grid is floored at lead 2 -- no look-ahead "
        "L0/L1). The winner (1.25) is a right-tail maximum at lead 4; the "
        "median valid combo (0.656) sits BELOW buy-and-hold (0.935), so the "
        "typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The winning DIRECTION contradicts the prior. Cement is procyclical, but the search selected a COUNTERCYCLICAL rule (buy SPY after very weak cement growth), which also runs opposite to the procyclical concurrent quartiles. `interpretation_metadata.json` records direction_consistent = false, confidence = low. Treat the contrarian edge as a caution, not a selling point.
2. The result is marked `found_in_search` at LOW confidence: the median valid combo (0.656) underperforms buy-and-hold (0.935), and the winner still needs a frozen-rule holdout confirmation. The adjacent-lead durability of the L4 choice should also be checked (issue #28).
3. This is not a validated forecast. Granger causality is insignificant at every lag (min p = 0.14; lag-4 p = 0.31), local projections are null, and the pre-whitened CCF has no significant bar at any offset -- the 4-month lead is a search-selected parameter, not a proven forecast horizon.
4. The edge is risk-reduction, not higher return: OOS return is LOWER than buy-and-hold (12.1% vs 14.6%); the Sharpe edge comes from a much smaller drawdown (-8.3% vs -23.9%) and low volatility (9.5%). The win rate is only 31.4% -- the rule wins by sitting out drawdowns.
5. Turnover is moderate-to-high (3.5/yr, 30 OOS trades): this is an active in/out rule and transaction costs matter more than for a set-and-forget overlay.
6. The sample is SHORT, starting 2005-11 (SPY-and-cement overlap; no Dot-Com coverage), and the favorable stress record leans heavily on the single 2022 episode. Cement shipments are nominal: in 2022 inflation kept the growth signal firm, which (for a contrarian rule) kept it in cash during the selloff. COVID 2020-21 is an extreme in-window outlier that can dominate the fit. Cement is a construction-activity series -- NOT a Conference Board LEI component and NOT "new orders".
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when cement YoY growth (lagged four months) crossed at or below "
        "its rolling 25th-percentile threshold -- i.e. when construction "
        "activity had been very weak -- taking exposure from 0% to 100% SPY. A "
        "SELL moves back to cash when that lagged growth rose above the "
        "threshold."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2010-02-28",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: cement_yoy countercyclical rule crossed T_roll_p25; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master | Portland Cement Shipments (nominal $, SA) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is Portland Cement Shipments in nominal $ (seasonally "
    "adjusted). The level is non-stationary (ADF fails to reject a unit root, "
    "p = 0.22; KPSS rejects stationarity), so the pipeline constructs growth "
    "transforms -- month-over-month, three-month, and six-month percent "
    "changes; twelve-month (YoY) growth; a 60-month rolling YoY z-score; and "
    "YoY acceleration -- all of which are stationary. The winning signal is "
    "`cement_yoy`, the year-on-year growth, used with a 4-month lead, a "
    "60-month rolling 25th-percentile threshold, and a countercyclical "
    "orientation (long SPY when the lagged growth is at or BELOW the "
    "threshold)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does cement growth move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong construction-activity regimes behave differently? | Makes the procyclical/contrarian story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past cement information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: cement growth transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x a publication-lag-floored lead grid (2-14 months, no look-ahead L0/L1). The final tournament has 468 combinations, all 468 valid. The winning rule is `cement_yoy / T_roll_p25 / P1_long_cash countercyclical / L4`, the maximum OOS Sharpe (1.253). The median valid combo (0.656) underperforms buy-and-hold (0.935), and the runner-up (`mom / T_roll_p25 / countercyclical / L4`, 1.182) shares the winner's rolling-25th-percentile threshold, contrarian orientation and 4-month lead -- read the winner as the top of a small contrarian rolling-threshold cluster, but one whose direction REVERSES the procyclical prior and that remains a selection maximum on a short sample, not a validated edge.
"""

_REFERENCES_MD = """
1. Data Master (internal panel), Portland Cement Shipments (nominal $, SA).
2. U.S. Geological Survey, Mineral Commodity Summaries: Cement (context on cement as a construction-activity gauge).
3. Yahoo Finance, SPY adjusted price history.
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
        "Monthly sample from 2005-11-30 to 2025-06-30, with out-of-sample "
        "window 2017-01-31 to 2025-06-30 (102 months). The SPY-and-cement "
        "overlap limits the usable sample to a short 2005 start, with no "
        "Dot-Com coverage."
    ),
    plain_english=(
        "This page documents how Portland Cement Shipments was turned into "
        "stationary growth signals, how the econometric checks were run, and "
        "how the tournament selected the final SPY allocation rule -- along "
        "with the honest caveat that the selection maximum is a COUNTERCYCLICAL "
        "rule whose direction CONTRADICTS the procyclical prior, is a "
        "contrarian found-in-search candidate on a short sample, and is not yet "
        "a validated edge."
    ),
)
