"""RSXFS (Advance Retail Sales) x SPY pair configuration (Rule APP-PT1).

New pair, MONTHLY consumer-demand pair. RSXFS ("Advance Retail Sales: Retail
Trade", FRED, SA, nominal $millions, 1993-2026) is a broadly COINCIDENT
consumer-demand indicator, NOT a leading one. The nominal-dollar level is
non-stationary, so every tested signal is a growth transform (MoM/3m/6m/YoY %,
YoY z-score, acceleration).

HONEST FRAMING (binding). Empirical verdict: retail-sales growth does NOT lead
SPY. Every number below is sourced from results/rsxfs_spy/*:
  - Granger RSXFS->SPY is INSIGNIFICANT at every tested lag (minimum
    p = 0.47 at lag 4); retail-sales growth does not Granger-cause SPY returns
    (granger_by_lag.csv / core_models_20260827/granger_causality.csv).
  - Local projections show essentially no linear predictive content:
    coefficients near zero, only the 12-month horizon is marginally
    significant (p = 0.007) with a trivial R^2 = 0.019 (local_projections.csv).
  - Concurrent YoY-growth quartiles vs SPY are roughly procyclical but
    NON-MONOTONIC: Q1 Sharpe 0.28, Q2 0.70, Q3 1.42 (best), Q4 0.89
    (regime_quartile_returns.csv).
  - The tournament winner (`mom` MoM growth / T0_zero growth>0 / procyclical /
    L9 months / P1_long_cash; OOS Sharpe 1.36 vs B&H 0.99) is the grid maximum
    over 252 combinations (238 valid). The MEDIAN valid combo scores 0.712 --
    it UNDERPERFORMS buy-and-hold (0.99). The runner-up is a completely
    different construction (yoy_zscore_60m / T_z_1.0 / countercyclical / L12,
    Sharpe 1.289) -> a crowded, flat-topped search surface. This is a
    found-in-search CANDIDATE, not a validated edge: no frozen-rule holdout /
    final exam has been run (evidence_status.json = found_in_search).
  - The defensible virtue is DRAWDOWN REDUCTION (OOS max drawdown -9.6% vs
    -23.9% for buy-and-hold) and stress-period defense, NOT the headline
    Sharpe -- read the Sharpe as volatility avoidance. Annual turnover is high
    (6.78/yr), the fingerprint of noise-driven flipping.
  - The L9 lead is economically implausible for a coincident indicator and is
    likely a search artifact; adjacent-lead durability is unchecked for this
    pair.
  - COVID 2020-21 is an extreme in-window outlier that can dominate the fit.

MONTHLY conventions: leads in MONTHS (winner L9); Sharpe annualized by sqrt(12);
OOS window 2017-01-31 -> 2026-07-31 (115 months). Numbers sourced from
results/rsxfs_spy/ (winner_summary.json, kpis.json, evidence_status.json,
interpretation_metadata.json, core_models_20260827/*, regime_quartile_returns.csv,
subperiod_sharpe.csv, granger_by_lag.csv, stationarity_tests_20260827.csv,
structural_break_rsxfs_spy.json, tournament_results_20260827.csv).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: Retail-Sales Growth as a Defensive SPY Overlay"
    PAGE_SUBTITLE = (
        "U.S. Advance Retail Sales (FRED RSXFS) x S&P 500 (SPY), monthly "
        "consumer-demand growth signals tested against SPY returns."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.36 OOS, but the honest headline is the drawdown: the "
        "searched rule cut the worst loss from -23.9% to -9.6% while retail "
        "sales did NOT lead the market"
    )

    PLAIN_ENGLISH = (
        "RSXFS is U.S. Advance Retail Sales -- roughly how much Americans "
        "spent at stores and restaurants each month, in nominal dollars. It is "
        "one of the cleanest reads on consumer demand, the largest part of the "
        "economy. Because spending tracks the cycle as it happens, retail "
        "sales is a COINCIDENT indicator, not an early-warning one. This pair "
        "tests whether retail-sales growth can improve SPY timing. The result "
        "should be read as procyclical demand context and drawdown control, "
        "not as a forecast: the formal lead-lag tests find no predictive edge."
    )

    WHERE_THIS_FITS = (
        "This is a procyclical consumer-demand overlay for broad U.S. "
        "equities. It belongs in the portal as a defensive context signal: "
        "useful for drawdown control in the searched sample, but not a "
        "standalone forecast. Readers wanting genuine advance warning should "
        "look at the leading pairs in the catalog; retail sales is a "
        "coincident cousin of the harder demand data."
    )

    ONE_SENTENCE_THESIS = (
        "Retail-sales growth is procyclical with equities but does NOT lead "
        "SPY -- Granger is insignificant at every lag (min p = 0.47) and "
        "local projections are essentially null -- so the search's best rule "
        "is a drawdown-reduction candidate (-9.6% vs -23.9% max drawdown), a "
        "found-in-search maximum whose 9-month lead is likely an artifact of a "
        "coincident indicator."
    )

    KPI_CAPTION = (
        "every performance number here is a SEARCH-PHASE, out-of-sample figure "
        "on a 115-month window (2017-01-31 -> 2026-07-31). The winner was "
        "found as the best of 238 valid combinations out of 252 scanned, and "
        "the MEDIAN valid combo (0.712) UNDERPERFORMS buy-and-hold (0.99) -- "
        "the typical rule subtracts value. The defensible number is the max "
        "drawdown (-9.6% vs -23.9%) at a comparable return -- read the Sharpe "
        "(1.36 vs 0.99) as volatility avoidance, not stock-picking skill. "
        "Sharpe ratios use monthly sqrt(12) annualization."
    )

    HERO_TITLE = "U.S. Advance Retail Sales vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the retail-sales level (nominal $, left axis) is "
        "shown with SPY on the same time axis, NBER recessions shaded. Both "
        "trend up over decades; the traded signal is not the level (it is "
        "non-stationary) but its month-over-month growth. Watch the shaded "
        "recessions -- retail sales fell during them, but it fell alongside "
        "the market, not before it."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Retail-Sales Growth Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (weakest retail-sales "
        "growth) to Q4 (strongest), with concurrent SPY Sharpe in each. The "
        "pattern is roughly procyclical but NON-MONOTONIC: Q3 is best "
        "(Sharpe 1.42), ahead of Q4 (0.89), with Q1 (0.28) and Q2 (0.70) "
        "below -- there is no clean 'stronger consumer = better market' "
        "gradient. Descriptive and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

The winning rule is a **month-over-month retail-sales-growth filter**. It holds SPY when retail-sales growth from nine months earlier was positive (above zero), and holds cash otherwise. Out-of-sample (2017-01 to 2026-07), this rule earns a Sharpe of 1.36 versus 0.99 for buy-and-hold, with a maximum drawdown of **-9.6% versus -23.9%** at an annualized return of 16.9% versus 15.2%. Read that as the honest headline: the rule's edge is a much shallower worst-case loss, not a return advantage.

### The Consumer-Demand Hypothesis

Retail sales measures household consumption, the largest component of GDP. A strong consumer is a risk-on signal for equities; softening spending is an early sign that demand is cooling. That is the economic prior this pair tests: retail-sales growth should be **procyclical** with SPY.

The prior is broadly borne out concurrently -- strong-growth quartiles carry higher SPY Sharpe than weak-growth ones -- but the relationship is non-monotonic (Q3 beats Q4), and, crucially, it is **coincident**, not leading. Retail sales moves with the cycle, not ahead of it.

### Why This Is Not a Forecast

The formal lead-lag tests are blunt. Retail-sales growth does **not** Granger-cause SPY returns at any tested lag (minimum p = 0.47), and local projections find essentially no linear predictive content (only the 12-month horizon is marginally significant, with a trivial R^2 of 0.019). So the 9-month lead the search selected is economically implausible for a coincident indicator -- it is most likely a search artifact, and the high 6.78-per-year turnover is the fingerprint of a rule flipping on noise. This dashboard therefore treats the pair as a searched, procyclical demand overlay whose value, if any, is defensive.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession",
            "narrative": (
                "Consumer spending softened as the tech bubble unwound, but "
                "retail-sales growth moved alongside the equity downturn rather "
                "than warning ahead of it -- the coincident character is "
                "visible here."
            ),
            "caption": "Dot-Com: consumer demand softened with the market, not before it.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "Retail sales fell sharply through the Global Financial Crisis "
                "as the consumer retrenched. The drop confirmed the recession; "
                "it did not precede the equity peak."
            ),
            "caption": "GFC: retail sales fell sharply, coincident with the bust.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "Retail sales collapsed in spring 2020 and rebounded violently "
                "on stimulus and reopening. This is an extreme, exogenous "
                "in-window outlier that can dominate the backtest fit -- read "
                "any rule that leans on it with caution."
            ),
            "caption": "COVID: extreme collapse and rebound, an outlier that can dominate the fit.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Nominal retail sales stayed high through 2022 because prices "
                "were rising, even as equities de-rated. This is the key "
                "caveat of a nominal-dollar series: inflation can keep the "
                "growth signal positive while the market falls."
            ),
            "caption": "2022: nominal sales stayed high on inflation while SPY sold off.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The stress charts show why the signal is procyclical but imperfect. Retail sales fell during the Dot-Com, GFC and COVID recessions -- but coincidentally with the market, not ahead of it. And in 2022 the nominal series stayed high on inflation while SPY sold off, exactly when a demand signal would have been most useful. The strongest honest reading is not "retail sales predicts drawdowns"; it is that a lagged, positive-growth filter happened to step to cash during several stress windows, which is where its drawdown advantage was earned.
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this consumer-demand story survives "
        "correlation, lead-lag, regime, and strategy checks. It largely does "
        "not survive as a forecast -- the value is defensive, not predictive."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether retail-sales growth and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does faster retail-sales growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal transform. Positive values "
        "mean stronger retail-sales growth lines up with stronger future SPY "
        "returns; pale cells mean no association."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the linear association is weak at every tradeable "
        "horizon. The clearest cell is a mild NEGATIVE reading of YoY growth "
        "vs 12-month-forward SPY (r = -0.14), which is not a procyclical "
        "forecasting signal."
    ),
    observation=(
        "No transform shows a strong linear association with forward SPY at "
        "short horizons; the only non-trivial cell is YoY growth vs the "
        "12-month-forward return (r = -0.14, p = 0.007)."
    ),
    interpretation=(
        "Correlation alone does not support trading the pair. The more "
        "relevant question is whether a lagged growth filter improves "
        "portfolio behavior in the searched sample."
    ),
    key_message="Retail-sales growth is not a simple linear SPY predictor at any tradeable horizon.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does retail-sales growth lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show p-values by monthly lag; the dashed line marks the 5% "
        "significance level. Bars ABOVE the line are insignificant."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: every lag is insignificant. The smallest p-value "
        "across lags 1-12 is 0.47 -- retail-sales growth does not "
        "Granger-cause SPY returns."
    ),
    observation=(
        "Across all twelve monthly lags the RSXFS->SPY p-value never falls "
        "below 0.47; the F-statistics are tiny. There is no formal evidence "
        "of lead-lag causality."
    ),
    interpretation=(
        "This rules out a causal claim. The strategy must be framed as a "
        "searched procyclical overlay, not proof that retail sales causes "
        "future SPY returns."
    ),
    key_message="Formal lead-lag evidence is absent (min p = 0.47); retail sales does not lead SPY.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by retail-sales YoY growth and "
        "compares concurrent SPY returns across consumer-demand regimes."
    ),
    question="Do weak and strong consumer-demand regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the weakest-growth regime; Q4 is the strongest. Compare "
        "Sharpe, average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: broadly procyclical but NON-MONOTONIC -- Q3 has the "
        "highest concurrent SPY Sharpe (1.42), ahead of Q4 (0.89), with Q1 "
        "(0.28) and Q2 (0.70) below."
    ),
    observation=(
        "Concurrent SPY Sharpe rises from 0.28 in Q1 to a peak of 1.42 in Q3, "
        "then eases to 0.89 in Q4 -- higher growth generally coincides with "
        "better equity conditions, but not monotonically."
    ),
    interpretation=(
        "The pattern fits a procyclical consumer-demand story, but the "
        "non-monotonicity (Q3 > Q4) and its concurrent nature mean it is "
        "descriptive context, not a tradable lead."
    ),
    key_message="Stronger consumer demand coincides with better SPY conditions, but non-monotonically and concurrently.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' own persistence "
        "before testing whether one tends to move before or after the other."
    ),
    question="At which offsets does retail-sales growth line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Positive offsets mean "
        "retail sales leads; negative offsets mean SPY leads."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: there is no coherent, clustered lead-side window in "
        "which retail-sales growth foreshadows SPY returns -- consistent with "
        "a coincident indicator."
    ),
    observation=(
        "The cross-correlation does not resolve into a stable lead structure; "
        "any bars near the band are scattered rather than clustered on the "
        "lead side."
    ),
    interpretation=(
        "The chart supports treating the pair as a coincident/contemporaneous "
        "relationship rather than a mechanical forecast with a fixed lead."
    ),
    key_message="There is no coherent lead window; the relationship is coincident.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the retail-sales-growth signal."
    ),
    question="How does SPY respond after retail-sales growth changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a move in the "
        "retail-sales-growth signal. Coefficients near zero mean no "
        "detectable effect."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: coefficients are essentially zero across horizons; "
        "only the 12-month horizon is marginally significant (p = 0.007) with "
        "a trivial R^2 of 0.019."
    ),
    observation=(
        "Point estimates are near zero at 1, 3 and 6 months; the only "
        "significant horizon is 12 months, and even there the explained "
        "variance is negligible (R^2 = 0.019)."
    ),
    interpretation=(
        "There is essentially no linear predictive content. The lone "
        "12-month result is economically trivial and does not rescue a "
        "forward-looking reading of the indicator."
    ),
    key_message="Local projections are near-null; retail-sales growth carries no useful linear forecast for SPY.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the retail-sales signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does retail-sales growth behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means a stronger association with that part of the SPY "
        "return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: the coefficient is close to zero across quantiles -- "
        "no material tail sensitivity for the retail-sales signal."
    ),
    observation=(
        "The estimated coefficient is small and flat across the tested "
        "quantiles, consistent with the near-null correlation and local "
        "projection results."
    ),
    interpretation=(
        "Retail-sales growth does not flag elevated crash risk or "
        "exceptional upside -- there is no tail channel to trade."
    ),
    key_message="Retail-sales growth shows no material state-dependent effect across SPY return tails.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: Retail Sales Is Procyclical Context, Not a SPY Forecast",
    "overview": (
        "The evidence supports a cautious, procyclical consumer-demand "
        "overlay -- and nothing stronger. The strategy winner improves "
        "search-phase OOS Sharpe, but formal lead-lag evidence is absent "
        "(Granger min p = 0.47; local projections near-null) and the "
        "indicator is economically coincident."
    ),
    "plain_english": (
        "This page asks whether retail-sales growth helps time SPY. The "
        "answer is: not as a forecast. Concurrent quartiles are broadly "
        "procyclical, but the causal tests find no lead. The best rule uses a "
        "delayed growth filter, so it should be treated as a defensive, "
        "after-the-fact overlay, not an early-warning system."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 252 strategy combinations (238 valid) across "
        "six retail-sales growth transforms, fixed and rolling thresholds, "
        "procyclical/countercyclical orientations, and leads from 0 to 12 "
        "months. The selected winner is `mom / T0_zero / P1_long_cash "
        "procyclical / L9`, with OOS Sharpe 1.36. The MEDIAN valid combo "
        "scores 0.712 -- below buy-and-hold's 0.99 -- and the runner-up is a "
        "different construction entirely (`yoy_zscore_60m / T_z_1.0 / "
        "countercyclical / L12`, 1.289), the signature of a crowded, "
        "flat-topped search surface."
    ),
    "transition": (
        "**Transition:** the evidence is procyclical context, not causation. "
        "The Strategy page shows the exact long/cash rule, the drawdown "
        "advantage that is its real virtue, and the deployment caveats."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Lagged Retail-Sales Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using month-over-month retail-sales "
        "growth, a positive-growth threshold, and a 9-month lead -- valued "
        "for drawdown reduction, not for its Sharpe."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when month-over-month retail-sales growth from "
        "nine months earlier was positive; otherwise it holds cash. This is a "
        "lagged, procyclical consumer-demand filter, not a real-time recession "
        "forecast. Judge it by its shallower drawdown (-9.6% vs -23.9%), not "
        "by the headline Sharpe."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/rsxfs_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/rsxfs_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/rsxfs_spy/tournament_results_20260827.csv"},
        {"label": "Stationarity tests", "path": "results/rsxfs_spy/stationarity_tests_20260827.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the 9-month-lagged month-over-month change in retail sales was positive (growth at or above zero); otherwise hold cash.

If-then form:
- **IF** `rsxfs_mom` from 9 months earlier is at or above zero -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2017-01-31 to 2026-07-31, 115 months): Sharpe 1.36 versus 0.99 buy-and-hold; annualized return 16.9% versus 15.2%; **maximum drawdown -9.6% versus -23.9%**; win rate 49.6%; annual turnover 6.78 (high). The drawdown reduction, not the Sharpe, is the defensible result.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads U.S. Advance Retail Sales (`RSXFS`) at month-end. Second, it computes the month-over-month percent change in retail sales (`rsxfs_mom`). Third, it applies a 9-month lag before the SPY allocation is set. Finally, the lagged signal is compared with a fixed zero threshold: positive growth -> SPY, otherwise cash.

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read Advance Retail Sales (RSXFS) at month end.
2. Compute the month-over-month percent change.
3. Take the value from 9 months earlier and check whether it was positive (at or above zero).
4. Hold SPY when that lagged growth was positive; otherwise hold cash.
5. Recheck monthly. Note the high turnover (6.78/yr): the rule flips often.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. The rule loses less in the Dot-Com "
        "(-0.55 vs -0.70) and GFC (-0.77 vs -1.03) bears and turns POSITIVE "
        "in COVID (+0.53 vs -0.66) and the 2022 rate shock (+0.18 vs -0.76) -- "
        "the stress-defense that underlies the drawdown story."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is retail-sales growth; the target "
            "is SPY returns. The rolling correlation tests whether their "
            "linear relationship is stable through time. Large swings mean the "
            "relationship is unstable and the rule needs ongoing monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break proxy asks whether the "
            "retail-sales/SPY relationship changes enough that one fixed model "
            "is unlikely to describe the whole sample. A larger break "
            "statistic means the relationship shifted more materially across "
            "periods."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across valid searched "
        "combinations. The winner (1.36) is the right-tail maximum; the median "
        "valid combo (0.712) sits BELOW buy-and-hold (0.99), so the typical "
        "rule built on this indicator subtracts value."
    )

    CAVEATS_MD = """
**Main caveats:**

1. Retail sales is broadly COINCIDENT; the 9-month lead is economically implausible and is most likely a search artifact.
2. Granger causality is insignificant at every lag (min p = 0.47) and local projections are near-null, so this is not a proven causal forecast.
3. The result is marked `found_in_search`; the median valid combo underperforms buy-and-hold, and the winner still needs a frozen-rule holdout confirmation.
4. Annual turnover is high (6.78/yr) -- the signature of noise-driven flipping and a real transaction-cost drag beyond the 5 bps assumed.
5. RSXFS is nominal: in 2022 inflation kept the growth signal positive while equities fell, and advance figures are revised in later releases.
6. COVID 2020-21 is an extreme in-window outlier that can dominate the fit.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 9-month-lagged month-over-month retail-sales growth was "
        "positive, taking exposure from 0% to 100% SPY. A SELL moves back to "
        "cash when the lagged growth was not positive."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-12-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: lagged rsxfs_mom positive; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED | `RSXFS`, Advance Retail Sales: Retail Trade (nominal $, SA) | Monthly |
| Target | Yahoo Finance or local SPY monthly fallback panel | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is U.S. Advance Retail Sales, in nominal $ millions "
    "(seasonally adjusted). The level is non-stationary (ADF fails to reject a "
    "unit root; KPSS rejects stationarity), so the pipeline constructs growth "
    "transforms -- month-over-month, three-month, six-month, and twelve-month "
    "percent changes; a 60-month rolling YoY z-score; and YoY acceleration -- "
    "all of which are stationary. The winning signal is `rsxfs_mom`, the "
    "month-over-month growth, used with a 9-month lead and a fixed "
    "positive-growth (zero) threshold."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does retail-sales growth move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do weak and strong consumer-demand regimes behave differently? | Makes the procyclical story interpretable |
| Pre-whitened CCF | Is there any lead-lag echo after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past retail-sales information improve SPY forecasts? | Formal lead-lag check |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: retail-sales growth transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x lead times (0-12 months). The final tournament has 252 combinations, 238 valid. The winning rule is `rsxfs_mom / T0_zero / P1_long_cash procyclical / L9`, the maximum OOS Sharpe (1.36). The median valid combo (0.712) underperforms buy-and-hold (0.99), and the runner-up (`yoy_zscore_60m / T_z_1.0 / countercyclical / L12`, 1.289) is a different construction -- read the winner as a selection maximum, not a validated edge.
"""

_REFERENCES_MD = """
1. Federal Reserve Economic Data (FRED), `RSXFS`, Advance Retail Sales: Retail Trade.
2. U.S. Census Bureau, Advance Monthly Retail Trade Report (source of RSXFS).
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
        "Monthly sample from 1993-01-31 to 2026-07-31, with out-of-sample "
        "window 2017-01-31 to 2026-07-31 (115 months). SPY history limits the "
        "usable sample even though RSXFS begins in 1992."
    ),
    plain_english=(
        "This page documents how RSXFS was turned into stationary growth "
        "signals, how the econometric checks were run, and how the tournament "
        "selected the final SPY allocation rule -- along with the honest "
        "caveat that the selection maximum is not yet a validated edge."
    ),
)
