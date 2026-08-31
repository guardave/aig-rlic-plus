"""Import Price Index x SPY pair configuration (Rule APP-PT1).

MONTHLY inflation/cost pair. The Import Price Index (BLS Import/Export Price
Indexes, series `IR` in Data Master; nominal price index, monthly) is a
COINCIDENT PRICE / inflation gauge -- NOT a production or Conference Board LEI
indicator. The nominal index LEVEL is non-stationary (ADF fails to reject a unit
root, p = 0.70; KPSS rejects stationarity), so every tested signal is a growth
transform (MoM/3m/6m/YoY %, YoY z-score, acceleration).

HONEST FRAMING (binding). This is a found-in-search CANDIDATE, confidence LOW --
NOT a validated, deployable edge. Every number below is sourced from
results/import_price_spy/*:
  - The tournament winner (`yoy` YoY growth / T_roll_p50 rolling-median /
    COUNTERCYCLICAL / L2 months / P1_long_cash; OOS Sharpe 1.37 vs 0.96 B&H) is
    the grid maximum over 252 combinations (all 252 valid). The MEDIAN valid
    combo scores 0.690 -- it UNDERPERFORMS buy-and-hold (0.96)
    (winner_summary.json). A higher OOS Sharpe than buy-and-hold over this ONE
    104-month sample is not "beating the market"; it is a search-phase result
    that still needs a fresh holdout (final exam).
  - DIRECTION AGREES WITH THE PRIOR. The economic prior for an import-price
    gauge is COUNTERCYCLICAL: rising import-price growth is imported
    inflation / cost pressure that tightens financial conditions and weighs on
    equity valuations, so favor SPY when import-price growth is LOW or falling.
    The search selected a COUNTERCYCLICAL rule (hold SPY when 2-month-lagged YoY
    import-price growth is at or below its five-year rolling median), which is
    the SAME direction as the prior. `interpretation_metadata.json` records
    expected_direction countercyclical, observed_direction countercyclical,
    direction_consistent = true, confidence = low.
  - The supporting evidence is unusually coherent for this fleet, but it is
    still not a deployment proof. Concurrent quartiles lean countercyclical: the
    STRONGEST import-price-growth quartile Q4 has the WORST concurrent SPY
    Sharpe (0.19), while the weakest-growth quartile Q1 is healthy (0.91)
    (regime_quartile_returns.csv) -- though the pattern is non-monotone (Q3 is
    the best, 1.26). Forward correlations are negative and significant at every
    horizon (YoY vs 1/3/6/12-month-forward SPY: r = -0.14, -0.26, -0.34, -0.33;
    the strongest single cell is the YoY z-score vs 12-month-forward SPY at
    r = -0.42) (core_models_20260830/correlations.csv). Local projections are
    negative and significant at every horizon (coef -0.0009 to -0.0086, all
    p < 0.01, R^2 rising to ~0.11 at 6 months) (local_projections.csv).
  - Some lead evidence exists, but it FADES fast. New import-price growth does
    Granger-cause SPY at SHORT lags (p = 0.008 at lag 1, p = 0.003 at lag 2),
    but the effect decays and is insignificant from lag ~6 onward (p = 0.14 at
    lag 12) (granger_by_lag.csv). The pre-whitened cross-correlation shows
    significant NEGATIVE bars on the lead side (import prices leading SPY, e.g.
    ccf = -0.16 at +3 months) AND significant POSITIVE bars on the SPY-leads
    side (-12 to -7 months) -- a two-sided pattern, not a clean one-directional
    forecast (ccf_prewhitened.csv). This is consistent with a coincident cost
    gauge whose growth carries a modest, short-lived negative signal for
    forward equities.
  - The defensible virtue is DRAWDOWN / VOLATILITY REDUCTION: OOS max drawdown
    -8.3% vs -23.9% for buy-and-hold, at a slightly LOWER annual return (13.5%
    vs 14.8%) and much lower volatility (9.6%). Read the Sharpe (1.37 vs 0.96)
    as volatility avoidance, not a return advantage. Turnover is moderate
    (1.5/yr, 13 OOS trades). A stationary block bootstrap puts the winner's
    Sharpe at p = 0.00 (tournament_validation_20260830/bootstrap.csv), but that
    is an in-sample significance check, not out-of-sample validation.
  - Status is `found_in_search` (evidence_status.json): the winner still needs a
    frozen-rule holdout / final exam, plus an adjacent-lead durability check
    (analyst_suggestions.json).
  - Nominal (not inflation-adjusted), revised in later BLS releases; the COVID
    2020-21 collapse/rebound is an extreme in-window outlier that can dominate
    the fit.

MONTHLY conventions: leads in MONTHS (winner L2); Sharpe annualized by sqrt(12);
OOS window 2017-01-31 -> 2025-08-31 (104 months). Numbers sourced from
results/import_price_spy/ (winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, core_models_20260830/*, regime_quartile_returns.csv,
subperiod_sharpe.csv, granger_by_lag.csv, stationarity_tests_20260830.csv,
structural_break_import_price_spy.json, tournament_results_20260830.csv,
tournament_validation_20260830/bootstrap.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Import-Price Growth as a Countercyclical SPY Overlay"
    PAGE_SUBTITLE = (
        "Import Price Index (BLS Import/Export Price Indexes) x S&P 500 (SPY), "
        "monthly imported-inflation growth signals tested against SPY returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.37 OOS vs 0.96 buy-and-hold on this single sample -- the "
        "honest headline is the drawdown (-8.3% vs -23.9%), and unlike most of "
        "the fleet the winning rule is COUNTERCYCLICAL, the SAME direction the "
        "economics predict for an imported-inflation gauge"
    )

    PLAIN_ENGLISH = (
        "The Import Price Index measures the dollar cost of goods the U.S. buys "
        "from abroad. It is a coincident PRICE / inflation gauge -- not a "
        "production indicator and not a Leading Economic Index component. The "
        "economic prior is countercyclical: rising import-price growth is "
        "imported inflation and cost pressure that tightens financial "
        "conditions and weighs on equity valuations, so equities tend to do "
        "better when import-price growth is LOW or falling. This pair tests "
        "whether that cost signal can improve SPY timing. Read the result as an "
        "inflation-cost overlay and drawdown control, not as a precise "
        "forecast: the supporting evidence points the right (countercyclical) "
        "way, but it is search-selected, confidence is low, and it still needs "
        "a fresh final exam before any claim of edge."
    )

    WHERE_THIS_FITS = (
        "This is an imported-inflation overlay for broad U.S. equities. It "
        "belongs in the portal as a countercyclical context signal: useful for "
        "drawdown control in the searched sample and, unusually for this fleet, "
        "pointing the same way the economics predict. But it is not a validated "
        "standalone forecast -- the median searched rule underperforms "
        "buy-and-hold, and the winner has not passed a frozen-rule holdout."
    )

    ONE_SENTENCE_THESIS = (
        "Import-price growth is countercyclical with equities -- the "
        "strongest-growth quartile has the worst concurrent SPY Sharpe (0.19), "
        "forward correlations are negative at every horizon (down to -0.34), and "
        "growth Granger-causes SPY at short lags (p = 0.003 at lag 2) -- so the "
        "search's best rule, a countercyclical filter at a 2-month lead, is a "
        "direction-consistent, drawdown-reducing candidate (-8.3% vs -23.9% max "
        "drawdown) that is still found-in-search and needs holdout validation."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 104-month window (2017-01-31 -> 2025-08-31). The winner was found "
        "as the best of 252 valid combinations, and the MEDIAN valid combo "
        "(0.690) UNDERPERFORMS buy-and-hold (0.96) -- the typical rule "
        "subtracts value. The defensible number is the max drawdown (-8.3% vs "
        "-23.9%) at a slightly LOWER return (13.5% vs 14.8%) and much lower "
        "volatility (9.6%) -- read the Sharpe (1.37 vs 0.96) as volatility "
        "avoidance, not stock-picking skill, and note a higher Sharpe than "
        "buy-and-hold over one sample is not proof of a durable edge. Sharpe "
        "ratios use monthly sqrt(12) annualization."
    )

    HERO_TITLE = "Import Price Index vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the import-price level (nominal index, left axis) is "
        "shown with SPY on the same time axis, NBER recessions shaded. The "
        "traded signal is not the level (it is non-stationary) but its "
        "year-over-year growth. Watch the shaded recessions -- import prices "
        "fell as global demand cratered in each, and spiked with imported "
        "inflation in 2021-22 as equities de-rated."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Import-Price Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest import-price "
        "growth) to Q4 (strongest), with concurrent SPY Sharpe in each. The "
        "strongest-growth quartile Q4 is the worst (Sharpe 0.19) and the "
        "weakest-growth quartile Q1 is healthy (0.91) -- broadly "
        "COUNTERCYCLICAL, the same direction as the winner and the economic "
        "prior. The pattern is non-monotone (Q3 is best, 1.26), so read it as "
        "directional context, not a precise dose-response."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **countercyclical, 2-month-lagged import-price-growth filter**. It holds SPY when year-over-year import-price growth from two months earlier was at or below its five-year rolling median, and holds cash otherwise. Out-of-sample (2017-01 to 2025-08), this rule earns a Sharpe of 1.37 versus 0.96 for buy-and-hold, with a maximum drawdown of **-8.3% versus -23.9%** at an annualized return of 13.5% versus 14.8%. Read that as the honest headline: the rule's edge is a much shallower worst-case loss and lower volatility, **not** a return advantage -- and a higher Sharpe than buy-and-hold over one sample is not the same as proof of a durable edge.

### The Imported-Inflation Hypothesis

The Import Price Index measures the dollar cost of imported goods. It is a **coincident price / inflation gauge** -- not a production indicator and not a Leading Economic Index component. The economic prior is that import-price growth is **countercyclical** for equities: fast-rising import prices signal imported inflation and cost pressure, which tightens financial conditions and compresses equity valuations; low or falling import-price growth is supportive.

The concurrent evidence supports that prior: sort months by import-price growth and the **strongest**-growth quartile has the worst concurrent SPY Sharpe (0.19), while the weakest-growth quartile is healthy (0.91). Crucially, the tournament's winning rule runs the **same** way -- it buys SPY when growth is *low* -- and at a short 2-month lead. That direction-and-lead combination **agrees** with the economic prior, which is unusual for this fleet and a point in the pair's favor.

### Why It Is Still Only a Candidate

The forecasting evidence is real but modest and short-lived. Import-price growth does Granger-cause SPY returns at short lags (p = 0.008 at lag 1, p = 0.003 at lag 2), but the effect **decays**: it is insignificant from about lag 6 onward (p = 0.14 at lag 12). Forward-return correlations are negative and significant at every horizon (down to -0.34), and local projections are negative and significant throughout -- all pointing the countercyclical way. But the pre-whitened cross-correlation is two-sided (significant negative bars where import prices lead SPY *and* significant positive bars where SPY leads import prices), the winner is search-selected, the median valid combo underperforms buy-and-hold, and the rule has not passed a frozen-rule holdout. This dashboard therefore treats the pair as a **direction-consistent but not-yet-validated** imported-inflation overlay whose defensible value is defensive.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "Import prices fell as global demand cratered. The searched "
                "rule did NOT protect here -- its subperiod Sharpe (-0.98) was "
                "worse than buy-and-hold (-0.70) in this window."
            ),
            "caption": "Dot-Com: import prices fell with global demand; the rule did not defend here.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Import prices collapsed through 2008-09 as the global goods "
                "economy seized up. The rule held up far better than "
                "buy-and-hold in this window (Sharpe 0.24 vs -1.03), part of "
                "its drawdown story."
            ),
            "caption": "GFC: import prices collapsed 2008-09; the rule lost far less than SPY.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Import prices collapsed in spring 2020 and rebounded "
                "violently. This is an extreme, exogenous in-window outlier "
                "that can dominate the backtest fit -- read any rule that leans "
                "on it with caution, even though the rule scored well here."
            ),
            "caption": "COVID: extreme collapse and rebound, an outlier that can dominate the fit.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Imported inflation spiked in 2021-22 exactly as equities "
                "de-rated -- the cleanest illustration of the countercyclical "
                "channel. The rule sat in cash (flat) through the 2022 "
                "drawdown while SPY fell."
            ),
            "caption": "2022: imported inflation spiked while SPY sold off; the rule sat in cash.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the countercyclical channel is economically sensible but the protection is uneven. Import prices fell during the Dot-Com, GFC and COVID downturns, and spiked with imported inflation in 2021-22. The searched rule's defense was uneven: it did **worse** than buy-and-hold in the Dot-Com bear (-0.98 vs -0.70), but held up far better in the GFC (0.24 vs -1.03), scored well through the COVID outlier (2.0 vs -0.66), and sat in cash (flat) through the 2022 rate shock while SPY fell (0.0 vs -0.76). The 2022 episode is the clearest illustration of the mechanism: fast import-price growth coincided with a falling market. The strongest honest reading is not "import prices predict drawdowns"; it is that a lagged, countercyclical cost filter stepped to cash during several stress windows, which is where its drawdown advantage was earned.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this imported-inflation story survives "
        "correlation, lead-lag, regime, and strategy checks. It survives better "
        "than most -- the direction is consistent and the short-lead evidence "
        "is real -- but the value is still defensive and not yet validated out "
        "of sample."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether import-price growth and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does faster import-price growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Negative values "
        "mean stronger import-price growth lines up with WEAKER future SPY "
        "returns; pale cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the association is consistently NEGATIVE and "
        "significant -- YoY import-price growth vs 1/3/6/12-month-forward SPY "
        "is r = -0.14, -0.26, -0.34, -0.33. Stronger imported inflation lines "
        "up with weaker forward equities, exactly the countercyclical prior."
    ),
    observation=(
        "Every growth transform shows a negative correlation with forward SPY "
        "that strengthens with horizon; the YoY-vs-6-month cell is -0.34 and "
        "the strongest cell anywhere is the YoY z-score vs 12-month-forward SPY "
        "at r = -0.42."
    ),
    interpretation=(
        "The linear evidence supports a countercyclical reading: high "
        "import-price growth precedes weaker SPY. That is directionally "
        "consistent with the winner, though the magnitudes are modest and do "
        "not by themselves prove a tradeable edge."
    ),
    key_message="Import-price growth is negatively correlated with forward SPY at every horizon -- countercyclical, matching the winner.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does import-price growth lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars BELOW the line are significant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: import-price growth Granger-causes SPY at SHORT lags "
        "(p = 0.008 at lag 1, p = 0.003 at lag 2, significant through lag 5) "
        "but the effect FADES -- it is insignificant from lag ~6 onward "
        "(p = 0.14 at lag 12)."
    ),
    observation=(
        "The signal_to_SPY p-value is below 0.05 for lags 1 through 5 (minimum "
        "0.003 at lag 2, matching the winner's 2-month lead) and above 0.05 "
        "from lag 6, decaying to 0.14 by lag 12."
    ),
    interpretation=(
        "There is genuine short-horizon lead-lag content -- and it peaks near "
        "the winner's 2-month lead -- but it is not persistent. This supports a "
        "short-lead countercyclical overlay, not a long-horizon forecast."
    ),
    key_message="Short-lag Granger evidence is real (min p = 0.003 at lag 2) but fades by ~6 months.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by import-price YoY growth and "
        "compares concurrent SPY returns across imported-inflation regimes."
    ),
    question="Do low and high imported-inflation regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the weakest-growth (low imported-inflation) regime; Q4 is the "
        "strongest. Compare Sharpe, average return, and sample size across the "
        "four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: broadly COUNTERCYCLICAL -- the strongest-growth "
        "quartile Q4 has the worst concurrent SPY Sharpe (0.19) and the "
        "weakest-growth quartile Q1 is healthy (0.91). The pattern is "
        "non-monotone (Q3 best, 1.26), so read it as directional, not a precise "
        "dose-response."
    ),
    observation=(
        "Concurrent SPY Sharpe is far lower in the strongest import-price-growth "
        "quartile (Q4 0.19) than in the weakest (Q1 0.91); Q2 is 0.67 and Q3 is "
        "1.26 -- higher imported-inflation growth generally coincides with worse "
        "equity conditions, though non-monotonically."
    ),
    interpretation=(
        "The concurrent pattern fits a countercyclical imported-inflation "
        "story and points the SAME way as the tournament winner. That "
        "coherence is a point in the pair's favor, unlike the fleet's many "
        "direction-contradicting winners."
    ),
    key_message="Higher imported inflation coincides with worse SPY conditions -- countercyclical, same direction as the winner.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does import-price growth line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "import prices lead; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: a two-sided pattern. On the lead side (import prices "
        "leading SPY) the significant bars are NEGATIVE (e.g. -0.16 at +3 "
        "months), consistent with the countercyclical channel; on the "
        "SPY-leads side (-12 to -7 months) the significant bars are POSITIVE. "
        "It is not a clean one-directional forecast."
    ),
    observation=(
        "Significant negative correlations appear at positive lags +1 to +6 "
        "(import prices leading SPY, ccf down to ~-0.16), and significant "
        "positive correlations at negative lags -12 to -7 (SPY leading import "
        "prices, ccf up to ~0.16)."
    ),
    interpretation=(
        "The lead-side (import-prices-lead) bars are negative, which agrees "
        "with the countercyclical winner; but the two-sided structure means "
        "the lead-lag relationship is entangled with the coincident nature of "
        "a price gauge, so treat the forecast content as modest."
    ),
    key_message="Import prices lead SPY negatively at short offsets (countercyclical), but the CCF is two-sided, not a clean forecast.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the import-price-growth signal."
    ),
    question="How does SPY respond after import-price growth changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "import-price-growth signal. Negative bars mean higher import-price "
        "growth is followed by weaker SPY."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are NEGATIVE and significant at every "
        "horizon (1, 3, 6, 12 months; coef -0.0009 to -0.0086, all p < 0.01), "
        "with R^2 rising to ~0.11 at 6 months -- higher import-price growth is "
        "followed by weaker SPY."
    ),
    observation=(
        "Point estimates are negative and grow more negative with horizon, all "
        "statistically significant (p from 0.008 down to 2e-11); explained "
        "variance rises from ~0.02 at 1 month to ~0.11 at 6 months."
    ),
    interpretation=(
        "There is genuine, if modest, negative predictive content across "
        "horizons -- the same countercyclical direction as the winner. It is "
        "the strongest single piece of forecasting evidence in this pair, but "
        "the R^2 values are small."
    ),
    key_message="Local projections are negative and significant at every horizon -- countercyclical predictive content, modest in size.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the import-price signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does import-price growth behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A more "
        "negative coefficient means a stronger inverse association with that "
        "part of the SPY return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is negative (about -0.003) and flat "
        "across the tested quantiles -- a consistent inverse association with "
        "no strong tail asymmetry."
    ),
    observation=(
        "The estimated coefficient is negative and essentially unchanged across "
        "the tested quantiles, consistent with the negative correlation and "
        "local-projection results."
    ),
    interpretation=(
        "Import-price growth's inverse relationship with SPY is broadly "
        "uniform across the return distribution rather than concentrated in a "
        "crash tail -- consistent countercyclical context, not a specific tail "
        "hedge."
    ),
    key_message="Import-price growth is uniformly, mildly negative across SPY return quantiles -- no strong tail asymmetry.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Import Prices Are Countercyclical Context, Direction-Consistent but Not Yet Validated",
    "overview": (
        "The evidence supports a countercyclical imported-inflation overlay -- "
        "and, unusually for this fleet, points the SAME way as the winner. "
        "Forward correlations are negative at every horizon (down to -0.34), "
        "local projections are negative and significant, concurrent quartiles "
        "lean countercyclical (strongest-growth quartile worst), and Granger is "
        "significant at short lags (p = 0.003 at lag 2, near the winner's L2). "
        "But the effect fades beyond ~6 months, the median searched rule "
        "underperforms buy-and-hold, and the winner is still found-in-search."
    ),
    "plain_english": (
        "This page asks whether import-price growth helps time SPY. The answer "
        "is: yes, weakly, and in the economically sensible direction. High "
        "imported inflation tends to precede weaker equities over the next few "
        "months; the best rule runs that way at a 2-month lag. Treat it as a "
        "direction-consistent defensive overlay that still needs a final exam, "
        "not a precise early-warning system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 252 strategy combinations (all 252 valid) across "
        "six import-price growth transforms, fixed and rolling thresholds, "
        "procyclical/countercyclical orientations, and leads from 0 to 12 "
        "months. The selected winner is `yoy / T_roll_p50 / P1_long_cash "
        "countercyclical / L2`, with OOS Sharpe 1.37. The MEDIAN valid combo "
        "scores 0.690 -- below buy-and-hold's 0.96 -- and the runner-up "
        "(`yoy / T0_zero / countercyclical / L2`, 1.321) shares the winner's "
        "YoY signal, countercyclical direction and 2-month lead, so the search "
        "surface concentrates on short-lead countercyclical rules -- a coherent "
        "cluster, but still one that needs out-of-sample confirmation."
    ),
    "transition": (
        "**Transition:** the evidence is countercyclical context that points "
        "the same way as the winner, but it is modest and not yet validated. "
        "The Strategy page shows the exact long/cash rule, the drawdown "
        "advantage that is its real virtue, and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Countercyclical, Lagged Import-Price Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using year-over-year import-price "
        "growth, a rolling-median threshold, a countercyclical orientation, "
        "and a 2-month lead -- valued for drawdown reduction, direction-"
        "consistent with the imported-inflation prior, but still "
        "found-in-search and awaiting a final exam."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when year-over-year import-price growth from two "
        "months earlier was at or below its five-year rolling median; "
        "otherwise it holds cash. This is a lagged, COUNTERCYCLICAL "
        "imported-inflation filter -- the same direction as the economic prior "
        "for a price gauge -- not a precise real-time recession forecast. Judge "
        "it by its shallower drawdown (-8.3% vs -23.9%) and lower volatility, "
        "not by the headline Sharpe."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/import_price_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/import_price_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/import_price_spy/tournament_results_20260830.csv"},
        {"label": "Stationarity tests", "path": "results/import_price_spy/stationarity_tests_20260830.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 2-month-lagged year-over-year change in import prices was at or below its five-year rolling median (i.e. when imported-inflation growth was *low* two months earlier); otherwise hold cash. This is a countercyclical rule and it runs the same way as the imported-inflation prior.

If-then form:
- **IF** `import_price_yoy` from 2 months earlier is at or below its 60-month rolling median -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-01-31 to 2025-08-31, 104 months): Sharpe 1.37 versus 0.96 buy-and-hold; annualized return 13.5% versus 14.8%; **maximum drawdown -8.3% versus -23.9%**; annualized volatility 9.6%; win rate 30.8%; 13 trades; annual turnover 1.5. The drawdown and volatility reduction, not the Sharpe or return, is the defensible result.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads the Import Price Index (`IR`, nominal price index) at month-end. Second, it computes the year-over-year percent change in import prices (`import_price_yoy`). Third, it applies a 2-month lag before the SPY allocation is set. Finally, the lagged signal is compared with its 60-month rolling median: when the lagged growth is at or below that median, hold SPY; otherwise cash (the countercyclical orientation).

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return (low here partly because the rule sits in cash for stretches).
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read the Import Price Index (IR) at month end.
2. Compute the year-over-year percent change.
3. Take the value from 2 months earlier and compare it with its trailing 60-month rolling median.
4. Hold SPY when that lagged growth was at or below the rolling median; otherwise hold cash.
5. Recheck monthly. Turnover is moderate (1.5/yr): the rule changes exposure a few times a year.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The rule holds up far better in the GFC "
        "(0.24 vs -1.03), scores well through the COVID outlier (2.0 vs -0.66), "
        "and sits in cash (flat, Sharpe 0.0) through the 2022 rate shock while "
        "SPY fell -- but it does WORSE than buy-and-hold in the Dot-Com bear "
        "(-0.98 vs -0.70). The stress defense is real but uneven."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is import-price growth; the target "
            "is SPY returns. The rolling correlation tests whether their "
            "linear relationship is stable through time. Large swings mean the "
            "relationship is unstable and the rule needs ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "import-price/SPY relationship changes enough that one fixed model "
            "is unlikely to describe the whole sample. A larger break "
            "statistic means the relationship shifted more materially across "
            "periods (here the max absolute rolling-correlation z-score reaches "
            "2.55)."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations by lead. The winner (1.37) is a right-tail maximum; the "
        "median valid combo (0.690) sits BELOW buy-and-hold (0.96), so the "
        "typical rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. The result is marked `found_in_search`: the median valid combo underperforms buy-and-hold (0.690 vs 0.96), and the winner still needs a frozen-rule holdout confirmation. The bootstrap p = 0.00 is an in-sample significance check, not out-of-sample validation.
2. The winner is COUNTERCYCLICAL at a 2-month lead, which AGREES with the imported-inflation prior -- a point in its favor -- but adjacent-lead durability should still be checked (analyst_suggestions.json), because even a direction-consistent short lead can be a fitting artifact.
3. The lead-lag evidence fades fast: Granger is significant only through lag ~5 (p = 0.003 at lag 2) and insignificant by lag 12, and the pre-whitened CCF is two-sided. This is a short-horizon overlay, not a long-range forecast.
4. The defensible virtue is drawdown and volatility reduction, not return: annualized return (13.5%) is slightly BELOW buy-and-hold (14.8%).
5. Import prices are nominal and revised in later BLS releases; the growth signal reflects imported inflation, which is exactly why it was firm in 2021-22 as equities fell.
6. COVID 2020-21 is an extreme in-window outlier that can dominate the fit -- the rule's strong COVID subperiod Sharpe (2.0) should be read with that in mind.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 2-month-lagged year-over-year import-price growth crossed "
        "at or below its rolling median, taking exposure from 0% to 100% SPY. "
        "A SELL moves back to cash when the lagged growth rose above the "
        "rolling median."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "1997-02-28",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: yoy countercyclical rule crossed T_roll_p50; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master (BLS Import/Export Price Indexes) | `IR`, Import Price Index (all imports, nominal index) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the Import Price Index, a nominal price index for "
    "U.S. imports. The level is non-stationary (ADF fails to reject a unit "
    "root, p = 0.70; KPSS rejects stationarity), so the pipeline constructs "
    "growth transforms -- month-over-month, three-month, six-month, and "
    "twelve-month percent changes; a 60-month rolling YoY z-score; and YoY "
    "acceleration -- all of which are stationary. The winning signal is "
    "`import_price_yoy`, the year-over-year growth, used with a 2-month lead, a "
    "60-month rolling-median threshold, and a countercyclical orientation (long "
    "SPY when lagged growth is at or below the median)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does import-price growth move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do low and high imported-inflation regimes behave differently? | Makes the countercyclical story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past import-price information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: import-price growth transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x lead times (0-12 months). The final tournament has 252 combinations, all 252 valid. The winning rule is `import_price_yoy / T_roll_p50 / P1_long_cash countercyclical / L2`, the maximum OOS Sharpe (1.37). The median valid combo (0.690) underperforms buy-and-hold (0.96), and the runner-up (`import_price_yoy / T0_zero / countercyclical / L2`, 1.321) shares the winner's YoY signal, countercyclical direction and 2-month lead -- read the winner as a selection maximum in a coherent short-lead countercyclical cluster whose direction agrees with the imported-inflation prior, but which is not yet validated out of sample.
"""

_REFERENCES_MD = """
1. U.S. Bureau of Labor Statistics, Import/Export Price Indexes (MXP program), all-imports index.
2. Data Master.xlsx, series `IR` (BLS Import Price Index).
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
        "Monthly sample from 1993-01-31 to 2025-08-31, with out-of-sample "
        "window 2017-01-31 to 2025-08-31 (104 months). SPY history limits the "
        "usable sample even though the import-price index begins earlier."
    ),
    plain_english=(
        "This page documents how the Import Price Index was turned into "
        "stationary growth signals, how the econometric checks were run, and "
        "how the tournament selected the final SPY allocation rule -- along "
        "with the honest caveat that the selection maximum, although "
        "direction-consistent with the countercyclical imported-inflation "
        "prior, is still found-in-search and not yet a validated edge."
    ),
)
