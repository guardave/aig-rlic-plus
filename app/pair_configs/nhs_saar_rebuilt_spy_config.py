"""New Home Sales (SAAR, rebuilt, floored) x SPY pair configuration (Rule APP-PT1).

Pair `nhs_saar_rebuilt_spy`, page 41. This is the #255 publication-lag-floored
REBUILD of the existing `nhs_saar_spy` pair.

================================  READ FIRST  ================================
A PARALLEL ORIGINAL pair `nhs_saar_spy` ALREADY EXISTS on the portal, authored
by **Vichua4b** with data via **Dana's** pipeline. That original is left
COMPLETELY UNTOUCHED. `nhs_saar_rebuilt_spy` is the #255 publication-lag-floored
rebuild: the New Home Sales (SAAR) series was reconstructed from the live FRED
API (`HSN1F`) plus Yahoo Finance SPY on 2026-10-08, and the lead axis is FLOORED
to L2 (floor grid [2..14]) to respect the ~4-week Census publication lag. The
reader is meant to COMPARE the two side by side: the original (`nhs_saar_spy`,
winner `nhs_mom / T_roll_p50 / P1_long_cash / L2`) vs this floored rebuild
(`nhs_saar_rebuilt_spy`, winner `nhs_6m_chg / T_roll_p25 / P1_long_cash / L14`).
The comparison is the entire point of this pair.
=============================================================================

Framing (binding -- procyclical but grid-ceiling, LOW confidence):
  * Winner is the 6-month CHANGE in the New Home Sales level (`nhs_6m_chg`),
    rule `gte` against a rolling 25th-percentile threshold (`T_roll_p25`,
    latest value approximately -56), **P1 long/cash**, **procyclical**,
    lookback LB60, **lead L14 (14 months)**. OOS Sharpe 1.50 vs B&H 1.00,
    maximum drawdown -9.8% vs -23.9%, annualized return 18.3% vs 15.4%.
  * The winner sits at **L14 -- the very TOP of the floored grid [2..14]**. Per
    the Lead-Grid Frequency Standard Step 4, a grid-ceiling / long-lead winner
    must be ADJUDICATED, not rubber-stamped: it is flagged as likely fragile /
    possibly multiple-testing noise, pending an adjacent-lead durability check.
    Worse, the 14-month lead sits BEYOND the Granger lag window (tested to 12),
    where forward significance actually appears at SHORT lags (1-2, 5-7) -- so
    the winning lead does not coincide with any measured forward channel.
  * HONEST COUNTERPOINT: unlike the countercyclical `nhs_rebuilt_spy` sibling
    (bootstrap p=0.069, not significant), THIS rebuild's winner clears the
    bootstrap bar -- re-shuffle p=0.002 (significant at 5%) -- and its direction
    is PROCYCLICAL, consistent with the early-cycle housing prior. Turnover is
    also low (18 trades, ~1.9/year), far below the original nhs_saar_spy's
    ~7.2/year. These are genuine points in its favour.
  * BUT confidence stays LOW: the result is `found_in_search` (no holdout final
    exam), the lead is a grid ceiling that fails the Granger-coincidence check,
    and this pair's own regime quartiles are HUMP-SHAPED (Q2 strongest, 1.12;
    not a clean monotonic rise), so the economics are regime-dependent.
  * Data rebuilt from FRED `HSN1F` (SAAR, already seasonally adjusted) +
    yfinance SPY on 2026-10-08. Values come from
    `results/nhs_saar_rebuilt_spy/winner_summary.json` (DATE_TAG 20261008).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# Shared banner surfaced in Story + Methodology so the reader always knows the
# parallel original exists and that the two are meant to be compared.
_PARALLEL_NOTE = (
    "**Compare with the original `nhs_saar_spy` pair.** A parallel original New "
    "Home Sales (SAAR) x SPY pair (`nhs_saar_spy`), authored by Vichua4b with "
    "data via Dana's pipeline, already exists on this portal and is left "
    "COMPLETELY UNTOUCHED. THIS pair (`nhs_saar_rebuilt_spy`) is the #255 "
    "publication-lag-floored REBUILD: the New Home Sales (SAAR) series is "
    "reconstructed from the live FRED API (`HSN1F`) plus Yahoo Finance SPY, and "
    "the signal lead is floored to L2 to respect the ~4-week Census release "
    "lag. Read the two together: the original's winner deploys the one-month "
    "home-sales momentum (`nhs_mom`) at a 2-month lead (L2); this rebuild's "
    "winner trades the 6-month change in the level (`nhs_6m_chg`) at a 14-month "
    "lead (L14), the top of the floored grid. Both land on a procyclical "
    "long/cash construction, but the transform, threshold, and lead all differ "
    "-- and the side-by-side comparison of the two is the whole purpose of this "
    "page."
)


class StoryConfig:
    PAGE_TITLE = (
        "The Story: New Home Sales (SAAR, Rebuilt, Floored) as a Long-Lead SPY "
        "Timing Overlay -- a Procyclical but Grid-Ceiling Rebuild"
    )
    PAGE_SUBTITLE = (
        "New Home Sales, seasonally adjusted annual rate (FRED HSN1F, rebuilt "
        "from the live API) x S&P 500 (SPY), monthly decision rules with a "
        "floored (L2) release-lag discipline. The #255 rebuild of the parallel "
        "original nhs_saar_spy pair."
    )

    HEADLINE_H2 = (
        "## Sharpe 1.50 OOS, drawdown -9.8%: a 14-month-lead housing-level "
        "overlay -- procyclical and bootstrap-significant, but a grid-ceiling "
        "winner that sits beyond the Granger window, so read it as a cautionary "
        "rebuild, not a validated edge"
    )

    PLAIN_ENGLISH = (
        "New Home Sales is an early-cycle housing indicator: buyers commit "
        "before construction, so sales lead starts, permits, and the jobs and "
        "spending they drive. The natural prior is PROCYCLICAL -- stronger "
        "home-sales demand should coincide with better equities -- and the rule "
        "the search picked here DOES point that way: it holds SPY when the "
        "6-month change in home-sales (lagged 14 months) is at or above its "
        "rolling 25th-percentile band, and moves to cash otherwise. That "
        "procyclical direction, a bootstrap p-value that clears the 5% bar "
        "(0.002), and low turnover (about two trades a year) are all genuine "
        "points in its favour. BUT the winning lead sits at the very TOP of the "
        "floored grid (14 months of [2..14]) -- the classic shape of a "
        "search artefact -- and 14 months is beyond the horizon where the "
        "formal lead-lag tests find any forward signal (those sit at 1-2 and "
        "5-7 months). Treat this as a cautionary search result awaiting a "
        "durability check, not a forecast.\n\n"
        + _PARALLEL_NOTE
    )

    WHERE_THIS_FITS = (
        "This is a housing leading-indicator signal tested against broad U.S. "
        "equities -- and, more importantly, it is a METHOD-COMPARISON pair. "
        + _PARALLEL_NOTE
        + "\n\nThe honest reading of the rebuilt winner: it beats buy-and-hold "
        "on Sharpe and drawdown in the out-of-sample window, its direction is "
        "procyclical (coherent with the prior), and its bootstrap p-value is "
        "significant -- but it sits at the very top of the floored lead grid "
        "(L14 of [2..14]), that 14-month lead lies beyond the Granger window "
        "where forward significance actually appears, the regime quartiles are "
        "hump-shaped rather than monotonic, and it has not faced a frozen-rule "
        "final exam. Confidence is LOW."
    )

    ONE_SENTENCE_THESIS = (
        "The rebuilt New-Home-Sales (SAAR) winner improves OOS Sharpe and "
        "drawdown versus buy-and-hold with a procyclical, bootstrap-significant "
        "(p=0.002), low-turnover long/cash rule -- but it is a grid-ceiling "
        "(L14), found-in-search result whose lead sits beyond the Granger "
        "window, so it is a low-confidence, cautionary rebuild of the untouched "
        "original nhs_saar_spy, to be compared against it and adjudicated, not "
        "deployed."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final holdout "
        "result. The winner was selected from 468 valid strategy combinations, "
        "sits at L14 -- the top of the floored lead grid [2..14] -- and carries "
        "LOW confidence despite a significant bootstrap p-value (0.002), because "
        "the 14-month lead sits beyond the Granger window and the regime "
        "quartiles are hump-shaped. Its direction is procyclical, consistent "
        "with the housing prior."
    )

    HERO_TITLE = "New Home Sales (SAAR) vs the S&P 500 (SPY) -- Rebuilt Data"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: New Home Sales at a seasonally adjusted annual rate "
        "(FRED HSN1F, rebuilt from the live API) is shown against SPY on a "
        "shared time axis. Gray bands are NBER recessions; pink bands mark "
        "periods when home sales were contracting year over year. The winning "
        "rule trades the 6-month CHANGE in this level, lagged 14 months, not "
        "the raw level itself."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by New Home Sales Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: months are sorted from Q1 (lowest home-sales regime) "
        "to Q4 (highest). Forward SPY Sharpe is HUMP-SHAPED -- weakest in Q1 "
        "(0.38) and strongest in the middle regime Q2 (1.12), then easing "
        "through Q3 (0.93) and Q4 (0.78) -- rather than rising cleanly, which "
        "is why the tradable rule uses the change in home sales rather than the "
        "raw level, and why confidence stays low."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- the winning rule earns a Sharpe ratio -- return per unit of volatility -- of 1.50 versus 1.00 for buy-and-hold (staying invested in SPY throughout). Its maximum drawdown -- the largest peak-to-trough loss -- improves to -9.8% from -23.9%, and annualized return is higher, 18.3% versus 15.4%. The OOS win rate is 57.8% over just 18 trades (annual turnover 1.9 -- roughly a quarter of the original nhs_saar_spy's ~7.2).

**Read every one of those numbers as search-found, not validated.** They come from the window used to SELECT the rule, not from an untouched final exam. The result is marked `found_in_search`.

### A Rebuild, Meant to be Compared

This pair is the #255 publication-lag-floored REBUILD of the parallel original `nhs_saar_spy` (authored by Vichua4b, data via Dana's pipeline), which is left untouched. The data here is reconstructed from the live FRED API (`HSN1F`, seasonally adjusted) plus Yahoo Finance SPY on 2026-10-08, and the signal lead is floored to L2 to respect the ~4-week Census release lag. The original deploys its winner (one-month momentum) at L2; this rebuild's winner (the 6-month change in the level) sits at L14. Both are procyclical long/cash, but the transform, threshold, and lead differ. The intended use is the side-by-side comparison of the two.

### The Winner is a Grid-Ceiling Rule -- Handle With Care

The winning rule trades the **6-month change in the New Home Sales level** -- how many more (or fewer) thousands of homes are selling now than half a year ago -- lagged **14 months**, against a rolling 25th-percentile band. It holds SPY LONG when the lagged change is at or above the band (not in the worst quarter of declines) and moves to cash otherwise -- a procyclical orientation. Two things cut in its favour and two against:

**In favour:** (1) the direction is PROCYCLICAL, consistent with both the housing prior; (2) the bootstrap re-shuffle p-value is 0.002 -- comfortably significant at 5% -- and turnover is low.

**Against:** (1) **L14 is the very TOP of the floored lead grid [2..14].** Per the Lead-Grid Frequency Standard (Step 4), a grid-ceiling / long-lead winner must be adjudicated -- it is the classic shape of a multiple-testing artefact and needs an adjacent-lead durability check. (2) That 14-month lead sits BEYOND the Granger lag window (tested to 12 months), where forward significance actually appears at SHORT lags (1-2 and 5-7). A winning lead that does not coincide with any measured forward channel is a fragility flag.

<!-- expander: Why surface a grid-ceiling result at all? -->
Because the comparison is the point. The original `nhs_saar_spy` found a procyclical momentum rule at L2 (near the release-lag floor); this floored rebuild, searching the same shifted grid on independently reconstructed data, lands on a procyclical change-in-level rule at the grid ceiling (L14). That the two AGREE on direction and family but disagree on transform, threshold, and lead is itself the finding: it tells you how much of each "winner" is mechanism and how much is search luck. We report the rebuilt winner honestly, with the grid-ceiling and Granger-coincidence flags attached, precisely so it can be weighed against the original.
<!-- /expander -->
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "Housing held up relatively well while equities fell through "
                "the dot-com bear market. New Home Sales stayed firm on low "
                "rates, so the housing signal did not warn of the equity "
                "drawdown. Read it as contextual background (pre-OOS), not the "
                "strongest validation case."
            ),
            "caption": "Dot-Com: housing stayed firm as equities fell (pre-OOS context).",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "New Home Sales collapsed ahead of and through the Global "
                "Financial Crisis -- the textbook case for housing as an early-"
                "cycle signal. But it predates the 2017+ OOS window, so it "
                "informs the story, not the strategy's measured performance."
            ),
            "caption": "GFC: home sales collapsed early and hard -- the leading case (pre-OOS).",
        },
        {
            "slug": "covid",
            "title": "COVID Shock",
            "narrative": (
                "During coronavirus disease 2019 (COVID-19), New Home Sales "
                "dropped abruptly and then rebounded sharply as mortgage rates "
                "fell. The move was fast and policy-driven. COVID is the one "
                "stress episode that falls inside the OOS window and is "
                "evaluable."
            ),
            "caption": "COVID: a sharp drop then a rapid rate-driven rebound -- the one evaluable OOS episode.",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "In the 2022-23 rate-hike cycle, higher mortgage rates slowed "
                "New Home Sales while SPY also sold off -- housing weakness and "
                "equity weakness moved together. This is the recent regime that "
                "dominates the out-of-sample window."
            ),
            "caption": "2022-23: higher rates slowed sales as equities fell -- the dominant OOS regime.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The zoom charts show why the signal is useful but imperfect. New Home Sales was highly informative in the **2008-09 Global Financial Crisis**, when it collapsed early (but that episode predates the 2017+ OOS window). It held firm through the **dot-com** equity bear market, dropped then rebounded abruptly during **COVID-19** (the one evaluable OOS stress episode), and slowed with higher mortgage rates in the **2022-23 rate shock** -- the regime that dominates the out-of-sample window. The strongest reading is not "housing predicts every drawdown"; it is that home-sales momentum can help size equity exposure through the housing cycle -- with the caveat that this rebuild's winner leans on a 14-month lead the formal tests do not corroborate.
"""

    TRANSITION_TEXT = (
        "The historical story is a genuine early-cycle-housing one, and the "
        "direction is procyclical as expected -- but the winner is long-lead at "
        "the grid ceiling and its lead sits beyond the Granger window. The "
        "Evidence page lays the hump-shaped quartiles alongside the lead-lag "
        "tests, and the Methodology page spells out the rebuild and the "
        "comparison with the untouched original nhs_saar_spy."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Analysis",
    method_theory=(
        "Correlation measures whether New Home Sales signals and future SPY "
        "returns move together in a roughly linear way."
    ),
    question="Does faster home-sales growth line up with better or worse future SPY returns?",
    how_to_read=(
        "Read the heatmap by horizon and signal. Positive values mean stronger "
        "home-sales growth lines up with stronger future SPY returns; negative "
        "values mean the opposite."
    ),
    chart_name="correlation_heatmap",
    chart_caption=(
        "What this shows: the raw linear relationship is modest, which is why "
        "the tradable rule uses a lagged change-in-level threshold rather than "
        "the correlation directly."
    ),
    observation=(
        "New Home Sales growth is noisy, so the linear correlation with "
        "forward SPY returns is modest and depends on the horizon."
    ),
    interpretation=(
        "Correlation alone is not enough to trade the pair. The more relevant "
        "question is whether a lagged home-sales threshold improves portfolio "
        "behavior."
    ),
    key_message="New Home Sales is useful as early-cycle context, not as a simple linear SPY predictor.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of one series improve "
        "forecasts of another after accounting for its own history."
    ),
    question="Does New Home Sales lead SPY returns in a formal lag test -- and at the winner's 14-month lead?",
    how_to_read=(
        "Bars show p-values by monthly lag. Values below the 0.05 line mark "
        "lags where past home-sales information adds statistically significant "
        "forecast information."
    ),
    chart_name="granger_f_by_lag",
    chart_caption=(
        "What this shows: New Home Sales-to-SPY p-values are significant at "
        "short lags (1-2 months, p=0.024/0.034) and again at 5-7 months "
        "(p=0.011/0.019/0.036), fading at longer lags. The window is tested "
        "only to 12 months -- so the winner's 14-month lead sits BEYOND it."
    ),
    observation=(
        "The Granger table shows significant home-sales-to-SPY evidence at lags "
        "1-2 and 5-7, fading beyond; the maximum tested lag is 12, so the "
        "winning 14-month lead is outside the measured forward window entirely."
    ),
    deep_dive_title="Why does the winner's lead failing to coincide with the Granger lags matter?",
    deep_dive_content=(
        "A robust leading indicator clears the significance line across a band "
        "of plausible horizons, and a tradable rule ideally deploys at a lead "
        "inside that band. Here the forward signal is concentrated at 1-2 and "
        "5-7 months, yet the winner deploys at 14 -- beyond the tested window. "
        "That mismatch is consistent with the 14-month lead being a search "
        "artefact (the grid ceiling happened to score best out-of-sample) "
        "rather than a dependable forward channel."
    ),
    interpretation=(
        "Forward causality is present but short-to-mid horizon; the winner's "
        "14-month lead does not coincide with it. This is a central reason "
        "confidence is low despite the strong headline Sharpe and the "
        "procyclical direction."
    ),
    key_message="Forward causality sits at 1-2 and 5-7 months, not at the winner's 14 -- confidence stays low.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts months by the New Home Sales level and "
        "compares subsequent SPY returns across housing regimes."
    ),
    question="Do low and high home-sales regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the lowest home-sales regime; Q4 is the highest. Compare "
        "Sharpe, average return, and sample size across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: forward SPY Sharpe is hump-shaped -- lowest in Q1 "
        "(0.38) and highest in the middle regime Q2 (1.12), not rising cleanly "
        "to Q4 (0.78)."
    ),
    observation=(
        "Forward SPY Sharpe rises from about 0.38 in Q1 to a peak near 1.12 in "
        "Q2, then eases through Q3 (0.93) and Q4 (0.78)."
    ),
    interpretation=(
        "The raw level is not cleanly monotonic, which is why the tradable rule "
        "uses the change in home sales rather than the level -- and why the "
        "economics are regime-dependent rather than a clean procyclical ramp."
    ),
    key_message="Home-sales momentum is more informative than the raw level; the regime gradient is hump-shaped, not monotonic.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters persistence before testing "
        "whether one series tends to move before or after the other."
    ),
    question="At which offsets does the home-sales signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the confidence band mark unusual lead-lag correlation "
        "after filtering autocorrelation."
    ),
    chart_name="ccf_prewhitened",
    chart_caption=(
        "What this shows: the relationship is timing-sensitive and should not "
        "be read as a stable clock, consistent with the short-horizon Granger "
        "result."
    ),
    observation=(
        "New Home Sales growth is noisy, so most cross-correlation bars sit "
        "inside the confidence band; the informative offsets are short."
    ),
    interpretation=(
        "The chart supports treating the pair as a short-horizon overlay with "
        "variable timing rather than a mechanical 14-month-lead forecast."
    ),
    key_message="Housing-to-equity timing is short-horizon and irregular -- not a clean 14-month clock.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "multiple horizons after a change in the home-sales growth signal."
    ),
    question="How does SPY respond after New Home Sales growth changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a one-unit move in "
        "the 6-month New Home Sales growth signal. The sign shows the direction "
        "of the response by horizon."
    ),
    chart_name="local_projections",
    chart_caption=(
        "What this shows: the local-projection results test the raw home-sales "
        "signal, not the final lagged tournament rule."
    ),
    observation=(
        "The chart helps separate raw housing relationships from the searched "
        "allocation rule."
    ),
    interpretation=(
        "If the response varies by horizon, that supports using explicit lead "
        "times in the tournament instead of assuming an immediate effect."
    ),
    key_message="The horizon matters for New Home Sales signals.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the home-sales signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does New Home Sales behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A larger "
        "coefficient means the home-sales signal has a stronger association "
        "with that part of the SPY return distribution."
    ),
    chart_name="quantile_coef",
    chart_caption=(
        "What this shows: real quantile-regression slopes are tail-dependent. "
        "They are positive and significant in the lower (weak-return) tail "
        "(+0.0016 at tau=0.10, p=0.010; +0.0009 at tau=0.25, p=0.037) and fade "
        "toward zero at higher quantiles. A cross-quantile equality test "
        "REJECTS a uniform slope (Wald p=0.007)."
    ),
    observation=(
        "The home-sales signal has a state-dependent association with SPY: "
        "significant in the lower tails and near zero in the upper quantiles. A "
        "bootstrap Wald test rejects equality of the slopes across quantiles "
        "(p=0.007), confirming the effect is not constant across the "
        "distribution."
    ),
    interpretation=(
        "New Home Sales is most informative in weak-return states -- consistent "
        "with housing turns mattering around recessions and recoveries -- "
        "rather than carrying one constant effect across all markets."
    ),
    key_message="New Home Sales has a tail-concentrated SPY association -- significant in weak-return states and fading at higher quantiles (Wald p=0.007).",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: a procyclical, bootstrap-significant winner -- but a grid-ceiling lead the lead-lag tests do not corroborate",
    "overview": (
        "The evidence supports a cautious early-cycle housing overlay. The "
        "winner improves search-phase OOS Sharpe, its direction is procyclical, "
        "its bootstrap p-value clears 5% (0.002), and turnover is low. But the "
        "raw regime relationship is hump-shaped (Q2 strongest) rather than "
        "monotonic, and forward Granger significance sits at short lags (1-2, "
        "5-7 months) -- NOT at the winner's 14-month lead, which is beyond the "
        "tested window. So the headline Sharpe is treated as a low-confidence "
        "searched result."
    ),
    "plain_english": (
        "This page asks whether New Home Sales helps with SPY timing. The "
        "answer is: partly, and in a coherent (procyclical) direction -- but "
        "the best rule deploys at a 14-month lead that the formal lead-lag "
        "tests do not back up, and it sits at the top of the searched lead "
        "grid, so it is treated as a low-confidence searched overlay, not a "
        "forecast."
    ),
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "tournament_intro": (
        "The tournament tested 468 valid strategy combinations across six New "
        "Home Sales transforms, fixed and rolling thresholds, procyclical and "
        "countercyclical orientations, and FLOORED monthly leads (L2-14, floor "
        "L2). The selected winner is `nhs_6m_chg / T_roll_p25 / P1_long_cash / "
        "L14` with a procyclical orientation, selected by max OOS Sharpe -- and "
        "it sits at L14, the TOP of the floored lead grid [2..14]. The median "
        "valid combo scored just 0.71."
    ),
    "transition": (
        "**Transition:** the direction is procyclical and the bootstrap is "
        "significant, but the winner is long-lead at the grid ceiling and its "
        "lead sits beyond the Granger window. The Strategy page shows the exact "
        "long/cash rule, threshold, and deployment caveats -- and why the "
        "verdict is a low-confidence candidate, to be compared against the "
        "untouched original nhs_saar_spy."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A 14-Month-Lead New Home Sales Change-in-Level Long/Cash Overlay"
    PAGE_SUBTITLE = (
        "A searched SPY allocation rule using the 6-month change in New Home "
        "Sales (SAAR), a rolling 25th-percentile threshold, and a 14-month "
        "lead -- procyclical and bootstrap-significant, but at L14 (grid "
        "ceiling), found_in_search. Low confidence."
    )

    PLAIN_ENGLISH = (
        "The rule holds SPY when the 6-month change in New Home Sales (SAAR) "
        "from 14 months earlier is at or above its rolling 25th-percentile "
        "threshold (that is, not in the worst quarter of six-month declines); "
        "otherwise it holds cash. This is a lagged housing-change rule in a "
        "procyclical direction, not a real-time recession forecast -- and it "
        "deploys at the top of the floored lead grid, so it carries a "
        "grid-ceiling warning."
    )

    DOWNLOADS = [
        {"label": "Granger causality by lag", "path": "results/nhs_saar_rebuilt_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/nhs_saar_rebuilt_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/nhs_saar_rebuilt_spy/tournament_results_20261008.csv"},
        {"label": "Stationarity tests", "path": "results/nhs_saar_rebuilt_spy/stationarity_tests_20261008.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule in plain English:** hold SPY when the lagged 6-month change in New Home Sales (SAAR) is at or above its rolling 25th-percentile threshold; otherwise hold cash.

If-then form:
- **IF** `nhs_6m_chg` from 14 months earlier is at or above its rolling 25th-percentile threshold (latest value approximately -56) -> hold SPY.
- **ELSE** -> hold cash.

This is a procyclical, long/cash construction (strategy family P1), lookback LB60, at a 14-month lead (L14).

Search-phase OOS results (2017-01-31 to 2026-08-31, 116 months, no holdout final exam yet): Sharpe 1.50 vs 1.00 buy-and-hold; annualized return 18.3% vs 15.4%; maximum drawdown -9.8% vs -23.9%; 18 trades; annual turnover 1.9; OOS win rate 57.8%.

**Two warnings travel with this rule:** (1) L14 is the TOP of the floored lead grid [2..14] -- a grid-ceiling / long-lead winner that the Lead-Grid Standard (Step 4) requires be adjudicated, not rubber-stamped; (2) 14 months is BEYOND the Granger lag window (tested to 12), where forward significance actually sits at short lags (1-2, 5-7) -- so the winning lead does not coincide with any measured forward channel. In its favour: the direction is procyclical, the bootstrap p-value is 0.002 (significant), and turnover is low.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process reads New Home Sales at a seasonally adjusted annual rate (`HSN1F`) FROM THE LIVE FRED API (this rebuild does NOT reuse Dana's committed `nhs_saar_spy` parquet) and converts it to month-end observations. Because HSN1F is already seasonally adjusted, no deseasonalisation is applied. Second, it computes the 6-month change in the level (this month's sales minus sales six months ago). Third, it lags that change 14 months (the winning lead), compares it to a rolling 25th-percentile threshold, and converts the comparison into a LONG-or-cash SPY position.

OOS Sharpe means out-of-sample risk-adjusted return. OOS Return is the annualized out-of-sample return. Maximum Drawdown is the largest peak-to-trough loss. Turnover is how often the strategy changes exposure each year. Win Rate is the share of out-of-sample months with positive strategy return.
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read New Home Sales (SAAR, `HSN1F`) from the live FRED API at month end (this rebuild does NOT use Dana's committed parquet).
2. Compute the 6-month change in the level (this month minus six months ago).
3. Compare the value from 14 months earlier with its rolling 25th-percentile threshold.
4. Hold SPY when the lagged change is at or above the threshold; otherwise hold cash.
5. Recheck monthly.

The warning label is central: this is `found_in_search`, NOT confirmed by a holdout final exam; the winner sits at the top of the floored lead grid (L14 of [2..14]); and its 14-month lead sits beyond the Granger window. Compare it against the untouched original `nhs_saar_spy` (L2, procyclical momentum, long/cash) rather than reading it in isolation.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: Sharpe is return per unit of volatility. The "
        "subperiod chart compares the searched rule with buy-and-hold SPY "
        "during major stress windows. Only COVID 2020 falls inside the "
        "2017-onward OOS window and is evaluable (strategy Sharpe ~2.0); the "
        "Dot-Com and GFC episodes predate the OOS split, so durability is only "
        "conditionally established."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the 6-month growth in New Home "
            "Sales; the target is SPY returns. The rolling correlation tests "
            "whether their linear relationship is stable through time. Large "
            "swings mean the strategy needs rolling thresholds and ongoing "
            "monitoring."
        ),
        "structural_break": (
            "How to read it: the structural break test asks whether the New "
            "Home Sales-SPY relationship changes enough that one fixed model "
            "is unlikely to describe the whole sample. A larger break "
            "statistic means the relationship changed more materially across "
            "periods."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 468 valid searched "
        "strategy combinations by lead, with the selected rule highlighted as "
        "the best search-phase result. The winner's 1.50 Sharpe is the maximum "
        "of the search (median valid combo 0.71), not a typical result -- and "
        "it sits at the L14 grid ceiling."
    )

    CAVEATS_MD = """
**Why confidence is low (even though several signs are favourable):**

1. **Grid-ceiling lead.** The winner sits at L14 -- the very TOP of the floored lead grid [2..14]. Per the Lead-Grid Frequency Standard (Step 4), a grid-ceiling / long-lead winner must be adjudicated, not rubber-stamped: it is the classic shape of a multiple-testing artefact and needs an adjacent-lead durability check.
2. **The winning lead sits beyond the Granger window.** Toda-Yamamoto-style Granger finds NHS-to-SPY significance at short lags (1-2 and 5-7 months); the maximum tested lag is 12, so the 14-month lead is outside the measured forward window entirely. A winning lead that does not coincide with any measured forward channel is a fragility flag.
3. **Hump-shaped regime gradient.** This pair's own descriptive quartiles are hump-shaped (Q1 0.38, Q2 1.12, Q3 0.93, Q4 0.78) rather than a clean monotonic rise -- the economics are regime-dependent.
4. **Search-found.** Marked `found_in_search`; it has NOT been confirmed on an untouched final-exam window.
5. **Short, episode-heavy OOS.** The OOS window (2017-2026, 116 months) is dominated by the 2022-23 rate shock; COVID is the only evaluable stress episode.

**Points in its favour (reported honestly):** the direction is PROCYCLICAL, consistent with the early-cycle housing prior; the bootstrap re-shuffle p-value is 0.002 (significant at 5%, unlike the countercyclical `nhs_rebuilt_spy` sibling at 0.069); and turnover is low (18 trades, ~1.9/year, roughly a quarter of the original nhs_saar_spy's ~7.2).

**What this means:** use this page as a CAUTIONARY rebuild to be compared against the untouched original `nhs_saar_spy` -- not as proof that New Home Sales forecasts the S&P 500. The honest verdict is a low-confidence, search-found candidate awaiting a frozen-rule final exam and an adjacent-lead durability check.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 14-month-lagged 6-month change in New Home Sales moves to "
        "or above its rolling 25th-percentile threshold, taking exposure from "
        "0% to 100% SPY. A SELL moves back to cash when the condition no longer "
        "holds. Over the OOS window the rule made just 18 such trades (annual "
        "turnover 1.9)."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-08-31",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: lagged nhs_6m_chg (L14) >= rolling p25; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Census / Federal Reserve via live FRED API (REBUILT 2026-10-08, NOT Dana's committed parquet) | `HSN1F`, New Home Sales, seasonally adjusted annual rate | Monthly |
| Target | Yahoo Finance | SPY adjusted close / monthly returns | Monthly |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "This pair is the #255 publication-lag-floored REBUILD of `nhs_saar_spy`. "
    "The New Home Sales series was reconstructed from the live FRED API "
    "(`HSN1F`, seasonally adjusted annual rate) plus Yahoo Finance SPY on "
    "2026-10-08 -- it does NOT reuse Dana's committed `nhs_saar_spy` parquet, so "
    "the two pairs can be compared as independent builds. Because HSN1F is "
    "already seasonally adjusted, no deseasonalisation is applied (unlike the "
    "not-seasonally-adjusted `nhs_spy` pair). The pipeline constructs one-month, "
    "three-month, six-month, and twelve-month growth rates; a 60-month rolling "
    "z-score; a six-month change in the level; and a housing-contraction flag. "
    "The winning signal is `nhs_6m_chg`, the six-month change in the New Home "
    "Sales level, used with a 14-month lead and a rolling 25th-percentile "
    "threshold, traded long/cash (P1, procyclical), lookback LB60. The lead axis "
    "is FLOORED to L2 (grid [2..14]) to respect the ~4-week Census release lag "
    "(approximately the fourth Tuesday of the following month), so the strategy "
    "does not use future information. New home sales are heavily revised; the "
    "live FRED API is treated as ground truth."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation analysis | Does New Home Sales move linearly with future SPY returns? | Simple baseline before richer tests |
| Regime quartiles | Do low and high home-sales regimes behave differently? | Makes the housing-cycle story interpretable |
| Pre-whitened CCF | Where is the lead-lag relationship strongest after filtering persistence? | Reduces false lead-lag signals from autocorrelation |
| Granger causality | Does past New Home Sales information improve SPY forecasts, and at what lag? | Formal lead-lag check (exposes the 14-month-lead mismatch) |
| Local projections | How does SPY respond over future horizons? | Shows horizon-specific effects |
| Quantile regression | Is the effect different in weak or strong market states? | Tests tail and regime sensitivity |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: New Home Sales transforms x fixed and rolling thresholds x long/cash strategy x procyclical/countercyclical orientations x FLOORED monthly leads (L2-14, floor L2) x lookbacks. The final tournament has 468 valid strategy combinations. The winning rule is `nhs_6m_chg / T_roll_p25 / P1_long_cash / L14` with a procyclical orientation, selected by max OOS Sharpe. The median valid combo scored 0.71; the winner's 1.50 is the search maximum.

**Grid-ceiling flag (binding).** The winner sits at L14 -- the very top of the floored lead grid [2..14]. Per the Lead-Grid Frequency Standard (Step 4), a grid-ceiling / long-lead winner is adjudicated, not accepted at face value: it is flagged as likely fragile / possibly multiple-testing noise and needs an adjacent-lead durability check. Reinforcing the caution, forward Granger significance sits at short lags (1-2, 5-7 months) and the window is tested only to 12, so the 14-month lead is outside the measured forward window.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/nhs_saar_rebuilt_spy/evidence_status.json` marks the pair `found_in_search`. In its favour, the bootstrap re-shuffle p-value is 0.002 (significant at 5%) and the direction is procyclical, consistent with the housing prior.
"""

_REFERENCES_MD = """
1. Federal Reserve Economic Data (FRED), `HSN1F`, New One Family Houses Sold: United States (SAAR).
2. Yahoo Finance, SPY adjusted price history.
3. U.S. Census Bureau and U.S. Department of Housing and Urban Development, New Residential Sales.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
5. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
6. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
7. Bailey, D. H. & Lopez de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "This pair is the #255 publication-lag-floored REBUILD of the parallel "
        "original nhs_saar_spy (authored by Vichua4b, data via Dana's "
        "pipeline), which is left untouched; the two are meant to be compared. "
        "Monthly sample from 1993-01-31 to 2026-08-31, with out-of-sample "
        "window 2017-01-31 to 2026-08-31 (116 observations). The final "
        "tournament has 468 valid strategy combinations. The winner sits at "
        "L14, the top of the floored lead grid [2..14]. Evidence status: "
        "found_in_search; bootstrap p=0.002 (significant); confidence low on "
        "the grid-ceiling and Granger-coincidence flags."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the REBUILT New Home Sales (SAAR) analysis. "
        + _PARALLEL_NOTE
        + " The most important points: because HSN1F is already seasonally "
        "adjusted, signals are used directly; the direction is procyclical and "
        "the bootstrap is significant; but the regime quartiles are hump-shaped, "
        "the winning rule deploys at the top of the floored lead grid (L14) at a "
        "lead the Granger tests do not corroborate, and it still needs a "
        "frozen-rule holdout test and an adjacent-lead durability check."
    ),
)
