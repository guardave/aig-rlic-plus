"""PHLX Semiconductor Index (SOX) x SPY pair configuration (Rule APP-PT1).

Pair `phlxsox_spy`, Mode 1 daily. Prose is sourced from Research Ray's
`docs/portal_narrative_phlxsox_spy_20260619.md`; this file wires that prose
to the shared Streamlit templates and Vera's bare-name chart artifacts.

Evidence status is `found_in_search`, so headline performance is labelled as
"Search-phase OOS Sharpe (no holdout final exam yet)" by the template.
Headline values come from `results/phlxsox_spy/winner_summary.json`.

This is a fragile, low-confidence winner (modelled on `m2sl_yoy_spy_config.py`
and `ism_services_spy_config.py`). The binding honesty mandates are:

1. The tradable signal is SOX/SPY RELATIVE STRENGTH, not raw SOX -- the 0.709
   same-day daily-return correlation is co-movement (shared market beta), not
   a forecast; dividing by SPY partials out the shared tide.
2. Causality is BIDIRECTIONAL feedback, not a clean SOX lead -- Toda-Yamamoto
   Granger is significant in BOTH directions at every lag, and the reverse
   (SPY->SOX) is taller at short lags.
3. The edge over SPY's OWN momentum is MARGINAL and horizon-dependent --
   significant at 21 days (p=0.033), NOT at 63 days (p=0.075); incremental
   R^2 about one percentage point.
4. Fragility is prominent -- IS Sharpe 0.10 vs OOS 1.57 (a favorable 2021-26
   semis bull window), the median valid combo (0.67) lost to B&H (0.82), win
   rate 0.20, the rule LOST in every pre-OOS crisis, bootstrap p=0.041,
   found_in_search, confidence LOW.

The config deliberately frames the pair as a fragile, search-found
relative-strength tilt, NOT as evidence that semiconductors lead the market.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


class StoryConfig:
    PAGE_TITLE = "The Story: A Fragile Relative-Strength Tilt, Not a Semiconductor Lead"
    PAGE_SUBTITLE = (
        "PHLX Semiconductor Index (SOX, Yahoo Finance ^SOX) x S&P 500 (SPY), "
        "daily decision rules with a one-day real-time lead floor."
    )

    HEADLINE_H2 = (
        "## OOS Sharpe 1.57 vs ~0.82 for both benchmarks -- but an in-sample "
        "Sharpe of 0.10 and crisis losses say read it with caution"
    )

    PLAIN_ENGLISH = (
        "Semiconductors and the broad stock market move together most of the "
        "time, so a rising chip index is rarely a forecast of anything -- it is "
        "mostly the same market move seen twice. This analysis instead tracks "
        "whether chips are out- or under-performing the market (the SOX/SPY "
        "relative-strength ratio), and finds a weak, fragile edge that beat the "
        "market in one favorable stretch but failed in every prior crisis."
    )

    WHERE_THIS_FITS = (
        "This is a cross-asset, equity-vs-equity relative-strength signal "
        "tested against broad U.S. equities. The honest reading is narrow: the "
        "rule is a searched relative-strength tilt whose edge is concentrated "
        "in one favorable 2021-26 semiconductor bull window. It is NOT evidence "
        "that semiconductors lead the S&P 500."
    )

    ONE_SENTENCE_THESIS = (
        "The winning SOX/SPY relative-strength momentum rule beats both "
        "benchmarks out-of-sample, but it trades a co-movement-adjusted ratio "
        "rather than raw chips, the causality runs both ways (feedback, not a "
        "clean lead), its edge over SPY's own momentum is marginal, and it "
        "should be treated as a low-confidence searched candidate awaiting a "
        "final exam."
    )

    KPI_CAPTION = (
        "the headline Sharpe is search-phase out-of-sample, not a final "
        "holdout result. The winner was the best of 4,607 valid strategy "
        "combinations, with bootstrap p=0.041, an in-sample Sharpe of just "
        "0.10, and low confidence -- and the lead-lag evidence is bidirectional "
        "feedback, not a clean semiconductor lead."
    )

    HERO_TITLE = "SOX/SPY Relative Strength vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: the chart shows the SOX/SPY RELATIVE-STRENGTH ratio "
        "(not raw SOX) against SPY on a shared time axis. Dividing by SPY "
        "cancels the shared market move (the 0.709 same-day co-movement) and "
        "leaves the only question that could forecast anything: are "
        "semiconductors leading or lagging the market? The winning rule trades "
        "the 6-month momentum of this ratio."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Relative-Strength Regime"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: subsequent SPY performance sorted by SOX/SPY "
        "relative-strength regime. Read it as descriptive context for the "
        "signal, not as the trading rule -- the OOS edge is concentrated in "
        "specific episodes, not a smooth state relationship."
    )

    NARRATIVE_SECTION_1 = """
### Headline Findings

Out-of-sample (OOS) -- tested on data not used to pick the rule -- the winning strategy earns a Sharpe ratio (SR) -- return per unit of volatility -- of 1.57, versus 0.82 for buy-and-hold (BH) -- staying fully invested in SPY throughout -- and 0.83 for a SPY-own-momentum benchmark (a rule that buys SPY simply when SPY itself has been rising). Its maximum drawdown (MDD) -- the largest peak-to-trough loss -- is -9.7% (970 basis points) versus -24.5% for buy-and-hold.

That looks impressive, and it is the honest headline number. But three facts sit right next to it and must be read together: the in-sample (IS) Sharpe -- measured on the data used to build and pick the rule -- was just 0.10; the median rule in the search scored 0.67, below buy-and-hold's 0.82; and the rule lost money in every market crisis before the test window began. The strong out-of-sample number rests on a favorable 2021-2026 semiconductor bull market. Treat this as a fragile, search-found result, not a validated edge.

### Why Raw Semiconductors Are Not the Signal

The PHLX Semiconductor Index (SOX) -- a basket of major chip stocks -- and SPY are both equity indices, and they move up and down together about 71% of the time on a daily basis. That number (a daily-return correlation of 0.709) is co-movement -- shared market beta (how much an asset swings when the whole market swings) -- not a forecast. If you used a high reading of raw SOX as a "buy" signal for SPY, you would mostly be reacting to a market move that already happened in both at once.

To find any genuine forecasting content, the analysis trades **relative strength** -- one index's price divided by another's, here SOX divided by SPY. Dividing by SPY cancels out the shared market move and leaves only the question that could actually predict something: are semiconductors leading or lagging the market right now? The hero chart shows this ratio, not raw SOX.

<!-- expander: Why divide SOX by SPY instead of using SOX directly? -->
Imagine two boats rising and falling on the same tide. Watching one boat tells you almost nothing about the other's extra movement -- the tide moves both. Dividing SOX by SPY is like measuring one boat's height relative to the other, removing the tide. What is left is whether semiconductors are climbing faster or slower than the market. Only that residual has any chance of being a forecast; the raw level is dominated by the shared "tide" of overall market beta.
<!-- /expander -->

### Feedback, Not a Clean Lead

It is tempting to tell a tidy story -- "semiconductors are the economy's canary, so chips lead the market." The data do not support that clean version. Granger causality (GC) -- a test of whether past values of one series improve forecasts of another -- is significant from SOX to SPY at every horizon tested, but it is also significant from SPY back to SOX at every horizon, and the reverse direction is actually stronger at short lags. **What this means:** the two markets feed back into each other (bidirectional causality) because both are high-beta equity indices pushing one another around -- not because chips cleanly lead. The pre-whitened cross-correlation tells the same story, with significant links on both the lead and the lag side.

So the tradable content is not "chips predict the market." It is a weak relative-strength momentum (MOM) -- the tendency of a recent trend to persist -- effect: when semiconductors have recently been outpacing the market, the market has tended to do slightly better over the following weeks.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash",
            "narrative": (
                "In the Dot-Com bust (2000-02), semiconductors did roll over "
                "before the broad market -- the closest thing to a genuine long "
                "lead, and the reason chips have their canary reputation. But "
                "the relative-strength rule itself was deeply negative through "
                "the episode (Sharpe -1.16) -- a failure case for the strategy."
            ),
            "caption": "Dot-Com: chips led on the way down, but the rule lost (Sharpe -1.16).",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis",
            "narrative": (
                "The Global Financial Crisis (GFC, 2007-09) is the failure "
                "case: the relative-strength rule was deeply negative through "
                "it (Sharpe -1.06, about -43% in simulation). Chips gave no "
                "clean advance warning that the rule could profit from."
            ),
            "caption": "GFC: the failure case -- the rule lost about 43% (Sharpe -1.06).",
        },
        {
            "slug": "covid",
            "title": "COVID Demand Shock",
            "narrative": (
                "In the coronavirus disease 2019 (COVID-19) crash (2020), chips "
                "and the market fell together within days; the relative-strength "
                "signal moved with the crash, not ahead of it -- a coincident "
                "episode, not a warning. The rule was negative here too "
                "(Sharpe -0.95)."
            ),
            "caption": "COVID: coincident, not a warning -- the rule lost (Sharpe -0.95).",
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "The 2022 rates shock is a confirmer that the signal can stay "
                "defensive in a grinding bear market -- it is the one episode "
                "where the rule was positive (Sharpe +0.36), and it sits inside "
                "the in-sample window."
            ),
            "caption": "2022: a confirmer -- the rule's only positive crisis (Sharpe +0.36).",
        },
    ]

    NARRATIVE_SECTION_2 = """
### What History Shows

The pair-specific history-zoom charts make the fragility tangible. In the Dot-Com bust (2000-02), semiconductors did roll over before the broad market -- the closest thing to a genuine long lead, and the reason chips have their canary reputation. In the COVID crash (2020), chips and the market fell together within days; the relative-strength signal moved with the crash, not ahead of it -- a coincident episode, not a warning. The Global Financial Crisis (GFC, 2007-09) is the failure case: the relative-strength rule was deeply negative through it (about -43% in simulation). The 2022 rates shock is a confirmer that the signal can stay defensive in a grinding bear market. The honest summary across episodes: this signal sometimes leads, sometimes coincides, and sometimes fails -- which is exactly why its confidence rating is low.

<!-- expander: Why is confidence low? -->
The winning rule was the single best of 4,607 valid searched combinations. When you search thousands of rules, the best one can look good purely by luck. Three independent checks flag that risk here: the in-sample Sharpe was 0.10 (the rule did not work on the data used to build it), the median searched rule lost to buy-and-hold, and a bootstrap (resampling) test gives p = 0.041 -- barely under the 5% line. The rule has also not yet faced a frozen "final exam" on an untouched window. All of this earns the label found_in_search, the weakest evidence tier.
<!-- /expander -->
"""

    TRANSITION_TEXT = (
        "The historical story is a fragile, episode-dependent one, so the full "
        "evidence suite matters. The Evidence page leads with the distinction "
        "between co-movement and forecast, then shows the causality runs both "
        "ways before the supporting checks."
    )


STORY_CONFIG = StoryConfig()


CORRELATION_CHART_NAME = "correlation_heatmap"
GRANGER_CHART_NAME = "granger_f_by_lag"
CCF_CHART_NAME = "ccf_prewhitened"
INCREMENTAL_EDGE_CHART_NAME = "incremental_edge"
LOCAL_PROJECTIONS_CHART_NAME = "local_projections"
QUANTILE_CHART_NAME = "quantile_coef"
HMM_REGIME_CHART_NAME = "hmm_regime_probs"


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Co-movement Versus Forecast",
    method_theory=(
        "The correlation heatmap separates the same-day correlation (shared "
        "market beta) from the forward correlations between today's lagged "
        "signal and SPY's future returns."
    ),
    question="Is the big SOX-SPY correlation a forecast, or just co-movement?",
    how_to_read=(
        "The same-day SOX-SPY cell is large; the forward cells (lagged signal "
        "vs SPY's future returns) are what would matter for trading. Look at "
        "how much smaller the forward cells are than the same-day cell."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        "What this shows: the same-day SOX-SPY correlation is 0.709 -- large, "
        "but that is co-movement (shared beta), not predictive power. The "
        "forward correlations are an order of magnitude smaller (best cell "
        "around r=0.10, implied R^2 near 1%)."
    ),
    observation=(
        "The same-day correlation is 0.709; the forward correlations are an "
        "order of magnitude smaller, with the best cell only around r=0.10."
    ),
    interpretation=(
        "The big number everyone notices is not a forecast; the genuine "
        "forecasting signal is small. Relative-strength rows carry slightly "
        "more of that forward signal than raw-SOX rows, which is why the "
        "strategy uses the ratio."
    ),
    key_message="The 0.709 correlation is co-movement, not a forecast.",
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag (Both Directions)",
    method_theory=(
        "Toda-Yamamoto Granger causality tests whether past values of one "
        "series improve forecasts of the other beyond its own history, in a "
        "form robust to integration order."
    ),
    question="Does SOX lead SPY -- or do the two markets feed back into each other?",
    how_to_read=(
        "Bars are F-statistics by lag; bars above the dashed line are "
        "significant at the 5% level. Vermillion bars are SOX leading SPY; "
        "blue bars are SPY leading SOX. A clean leading indicator would show "
        "tall bars in only one color -- here both colors clear the line, and "
        "the blue (reverse) bars are taller at short lags."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: Toda-Yamamoto is significant in BOTH directions at "
        "every lag (SOX->SPY and SPY->SOX), with the reverse direction taller "
        "at short lags -- the definition of feedback, not a clean lead."
    ),
    observation=(
        "Both directions clear the 5% line at every lag tested "
        "[1, 2, 3, 5, 10, 21]; the reverse (SPY->SOX) is stronger at short lags."
    ),
    deep_dive_title="How should I read the Granger chart?",
    deep_dive_content=(
        "The chart plots two sets of bars. Vermillion bars are SOX leading "
        "SPY; blue bars are SPY leading SOX. A bar above the dashed line is "
        "statistically meaningful at the 5% level. Both colors clear the line "
        "at every lag, and the blue (reverse) bars are actually taller at "
        "short lags. That two-sided pattern is the definition of feedback; a "
        "clean leading indicator would show tall bars in only one color."
    ),
    interpretation=(
        "The two markets feed back into each other because both are high-beta "
        "equity indices pushing one another around -- not because chips cleanly "
        "lead. This is a central reason confidence is low."
    ),
    key_message="Causality runs BOTH ways -- feedback, not a clean SOX lead.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation removes each series' own persistence "
        "before checking whether one echoes the other at daily offsets."
    ),
    question="After removing each series' own trend, is the link one-sided or two-sided?",
    how_to_read=(
        "Bars outside the confidence band indicate statistically meaningful "
        "offsets. Positive lags would mark SOX leading SPY; negative lags mark "
        "SPY leading SOX. A clean lead would put the mass on one side."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: once the dominant same-day spike is set aside, "
        "significant cells appear on BOTH the lead and the lag side -- "
        "consistent with the bidirectional Granger result."
    ),
    observation=(
        "Significant cross-correlation cells appear on both the lead side "
        "(SOX leads, lags [4, 6, 8, 12, 15, 16]) and the lag side."
    ),
    interpretation=(
        "The CCF reinforces the Granger conclusion: the relationship is "
        "feedback between two high-beta equity series, not a one-way "
        "semiconductor lead."
    ),
    key_message="The cross-correlation has mass on both sides -- feedback, not a lead.",
)

INCREMENTAL_EDGE_BLOCK = dict(
    chart_status="ready",
    method_name="Does It Beat SPY's Own Momentum?",
    method_theory=(
        "The incremental-edge regression asks whether the lagged "
        "relative-strength signal adds forecasting power over and above SPY's "
        "own trailing momentum -- because a rule that just follows SPY's recent "
        "trend already earns a Sharpe of 0.83."
    ),
    question="Does relative strength add anything over simply riding SPY's own trend?",
    how_to_read=(
        "Compare the added explanatory power and significance at each forecast "
        "horizon. A robust edge would be significant and material across "
        "horizons; a fragile one would be significant at some and not others."
    ),
    chart_name=INCREMENTAL_EDGE_CHART_NAME,
    chart_caption=(
        "What this shows: relative strength adds a statistically significant "
        "increment at the 21-day horizon (p=0.033) but NOT at the 63-day "
        "horizon (p=0.075); the extra explanatory power is only about one "
        "percentage point of R^2 either way."
    ),
    observation=(
        "Significant increment at 21 days (p=0.033), not significant at 63 "
        "days (p=0.075); incremental R^2 about 1%."
    ),
    interpretation=(
        "There is a genuine but thin and horizon-dependent edge over simply "
        "riding SPY's trend -- real enough to detect, too small to lean on "
        "heavily."
    ),
    key_message="The edge over SPY-own-momentum is marginal and horizon-dependent.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections (LP) estimate the forward SPY response at several "
        "horizons after a move in the relative-strength signal, with "
        "HAC standard errors."
    ),
    question="Does a relative-strength move produce statistically clear forward SPY responses?",
    how_to_read=(
        "The line is the estimated response and the band is statistical "
        "uncertainty. Bands crossing zero mean weak evidence."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: forward coefficients are positive and grow with "
        "horizon but never reach 5% significance (minimum p approximately "
        "0.10); the bands include zero throughout. The reverse panel shows a "
        "significant negative one-day coefficient -- the market's move feeds "
        "back into relative strength."
    ),
    observation=(
        "Forward responses are insignificant at every horizon; the reverse "
        "one-day coefficient is significantly negative."
    ),
    interpretation=(
        "Local projections tell the same feedback story: no clean forward "
        "predictive content, and the reverse channel reappears."
    ),
    key_message="Local projections also point to feedback, not a forward lead.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression (QR) runs separate regressions for weak, normal, "
        "and strong SPY-return outcomes."
    ),
    question="Where in the return distribution does the signal carry information?",
    how_to_read=(
        "Read coefficient estimates across return quantiles. Significance in "
        "the lower (downside) quantiles points to downside-management content."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: the signal is significant in the lower (downside) "
        "return quantiles and fades to zero in the upside."
    ),
    observation=(
        "Coefficients are significant in the lower return quantiles and fade "
        "in the upper quantiles."
    ),
    interpretation=(
        "The signal's information is more about avoiding bad outcomes than "
        "chasing big up-moves -- a downside-tilt, not a broad forward predictor."
    ),
    key_message="The signal's content is concentrated in the downside, not the upside.",
)

HMM_BLOCK = dict(
    chart_status="ready",
    method_name="HMM Regime Map",
    method_theory=(
        "A Hidden Markov Model (HMM) splits the sample into latent calm and "
        "high-variance regimes."
    ),
    question="When did the relationship sit in calm versus high-variance regimes?",
    how_to_read=(
        "Higher regime probability marks periods where behavior looks unusual "
        "relative to the long sample."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: the HMM is used here only as a regime map for "
        "context, not as the winning trading signal."
    ),
    observation=(
        "The HMM highlights high-variance regimes, including major crisis "
        "windows."
    ),
    interpretation=(
        "The regime map helps explain context, but the winning rule is the "
        "relative-strength momentum threshold, not HMM probability."
    ),
    key_message="The HMM explains backdrop; it does not validate the winner.",
)

CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "This pair trades **daily**, but for cross-pair comparability the lead "
        "grid here is **monthly-resampled**: the SOX/SPY relative-strength "
        "momentum signal is shifted L = 0…12 calendar months and correlated "
        "against SPY's 1-month forward return. **State this honestly:** the "
        "production rule executes daily; this monthly grid is a comparability "
        "diagnostic. Given this pair's already-thin forecast content (see the "
        "Co-movement vs Forecast block), the lead view is a check on whether "
        "any lead carries more signal than the near-contemporaneous reading."
    ),
    question=(
        "On a monthly-resampled grid, does lagging the chip relative-strength "
        "signal recover any predictive content — or is the thin signal "
        "concentrated at the front of the grid?"
    ),
    how_to_read=(
        "Rows are SOX/SPY signal variants; columns are signal lead in MONTHS "
        "(L0 = contemporaneous, L12 = 12 months ago). Forward horizon fixed at "
        "1 month. Cell shading is Pearson r (linear co-movement, -1 to +1) "
        "against `spy_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "Pearson correlations between **signal lagged L months** and **SPY "
        "1-month forward return**. The traded signal "
        "`sox_spy_ratio_mom_6m_pct` peaks at **L0 (r=+0.078)** and decays "
        "monotonically to negative by L12 — consistent with a thin, "
        "near-contemporaneous signal, not a delayed lead. No lead recovers "
        "stronger content than the front of the grid."
    ),
    observation=(
        "Reading the row directly: the signal is strongest at **L0 (+0.078)** "
        "and falls steadily (L1 +0.060, L3 +0.034, L6 +0.001, L12 −0.062). "
        "There is **no hidden lead** — content is concentrated at the front of "
        "the grid and decays, and even the peak is small (|r| < 0.08, not "
        "significant). This is consistent with the rest of this pair's "
        "evidence: the forward forecast content is thin (about 1% of return "
        "variation), and lagging the signal does not improve it."
    ),
    interpretation=(
        "The lead view reinforces the candid story told elsewhere on this "
        "page: **the SOX/SPY signal is near-contemporaneous and thin.** No "
        "month-scale lead unlocks a stronger relationship; the modest content "
        "lives at L0 and fades. **In plain English:** chips and the market "
        "move together more than chips lead the market, so there is no "
        "reliable 'lag the signal by N months' edge to exploit. The traded "
        "rule's low lead is appropriate, but the underlying signal is weak — "
        "read the strategy with that caveat."
    ),
    key_message=(
        "The traded signal peaks at **L0 (r=+0.078)** and decays with lead — "
        "thin and near-contemporaneous, with no hidden multi-month lead. "
        "Consistent with this pair's broader finding that the forward forecast "
        "content is small; lagging the signal does not help."
    ),
)

LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This block sweeps the monthly lead grid L = 0…12 and plots the best "
        "OOS Sharpe at each lead (blue bar) against all valid combos (grey "
        "strip); the dashed orange line is SPY buy-and-hold (Sharpe 0.82). "
        "**Honesty note (daily pair):** the lead axis is monthly-resampled for "
        "comparability even though the pair executes daily; the published "
        "winner trades at a 3-month lead on its daily series."
    ),
    question=(
        "On the monthly grid, is the winner's lead a robust ridge or an "
        "isolated point — and does the sweep reinforce the 'thin edge' "
        "caveat that runs through this pair?"
    ),
    how_to_read=(
        "Bars: max OOS Sharpe at each monthly lead. Strip dots: every valid "
        "combination at that lead. A tall thin spike is a single combo; a "
        "flat-but-wide cloud is a robust regime."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "Best OOS Sharpe per monthly lead (blue bars) and the full "
        "distribution (grey strip). The low-lead region is the strongest: "
        "L0 (1.43), L3 (1.37) and L9 (1.35) lead, and the traded **L3 sits on "
        "a broad L0–L4 ridge** above buy-and-hold (0.82). The lead choice is "
        "robust to perturbation, even though the underlying signal is thin."
    ),
    observation=(
        "Reading the monthly bars: **L0 (1.43) and L3 (1.37) anchor a high, "
        "broad ridge across L0–L4** (all ≥1.24), with a secondary bump at L9 "
        "(1.35). The traded winner's lead, **L3 (1.37)**, is well inside that "
        "ridge — its neighbours L2 (1.26) and L4 (1.32) are close behind, so "
        "the lead is not a fragile spike.\n\n"
        "The published winner (`sox_spy_ratio_mom_6m_pct / T2_roll_p75 / "
        "P1_long_cash`, OOS Sharpe **1.57**) trades at L3. **But durability of "
        "the lead is not the same as durability of the edge:** as the "
        "Incremental Edge and sub-period blocks show, much of this pair's OOS "
        "Sharpe owes to a chip-friendly test window. The lead is robust; the "
        "alpha is thin. Both statements are true and both are stated here for "
        "honesty."
    ),
    interpretation=(
        "The honest summary has two parts. First, **the lead is a robust "
        "ridge, not a spike** — L0–L4 all clear ~1.24+ and the traded L3 sits "
        "comfortably among them. Second, **a robust lead does not rescue a "
        "thin signal**: the lead-correlation content is small and "
        "near-contemporaneous, and the pair's wider evidence flags the edge as "
        "window-dependent. A reader should take the lead choice as sound and "
        "the strategy's alpha as low-confidence — exactly the framing the rest "
        "of this Evidence page carries."
    ),
    key_message=(
        "The traded 3-month lead sits on a broad, robust L0–L4 ridge (all "
        "≥~1.24; L0 1.43, L3 1.37) — not a fragile spike. The published winner "
        "scores OOS Sharpe 1.57, but per this pair's other blocks the edge is "
        "thin and window-dependent: the lead is durable, the alpha is not."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The forecast content is real but thin; the winner's edge is not robust",
    "overview": (
        "The headline distinction is co-movement versus forecast: the same-day "
        "SOX-SPY correlation is 0.709 (shared beta), while the forward "
        "forecasting signal is about 1% of return variation. The lead-lag "
        "tests show bidirectional feedback (both Granger directions significant "
        "at every lag), the edge over SPY's own momentum is marginal and "
        "horizon-dependent, and the supporting checks confirm the same thin, "
        "low-confidence story."
    ),
    "plain_english": (
        "Eight tests point the same way: chips and the market feed back into "
        "each other, the genuine forward-looking signal in relative strength is "
        "small (about 1% of return variation), and the winning strategy beat "
        "the market mostly because it was tested in a chip-friendly window."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag", "path": "results/phlxsox_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/phlxsox_spy/regime_quartile_returns.csv"},
        {"label": "Subperiod (crisis) Sharpe checks", "path": "results/phlxsox_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation", "path": "results/phlxsox_spy/rolling_correlation_phlxsox_spy.csv"},
        {"label": "Stationarity tests", "path": "results/phlxsox_spy/stationarity_tests_20260619.csv"},
    ],
    "level1": [CORRELATION_BLOCK, CORRELATION_LEAD_VIEW_BLOCK, LEAD_TOURNAMENT_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Co-movement vs Forecast", "Lead Analysis", "Lead Tournament", "Granger Causality", "Pre-Whitened CCF"],
    "level2": [INCREMENTAL_EDGE_BLOCK, LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK, HMM_BLOCK],
    "level2_labels": ["Incremental Edge", "Local Projections", "Quantile Regression", "HMM Regimes"],
    "tournament_intro": (
        "The tournament tested 6,760 benchmark-excluded strategy combinations, "
        "of which 4,607 passed validity filters. The winning rule is the best "
        "of that valid searched set -- and the median valid combo scored 0.67, "
        "below buy-and-hold's 0.82 -- so its Sharpe advantage must be read with "
        "the search-position warning attached."
    ),
    "transition": (
        "**Transition:** the evidence supports only a thin, feedback-driven "
        "signal. The strategy page shows what the rule actually is: a "
        "search-found relative-strength Long/Cash tilt whose OOS edge leans on "
        "a favorable semiconductor-bull window."
    ),
}


class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Fragile Relative-Strength Long/Cash Tilt"
    PAGE_SUBTITLE = (
        "A searched relative-strength tilt: better Sharpe and drawdown than "
        "both benchmarks in the OOS window -- but bidirectional causality, a "
        "marginal edge over SPY's own momentum, found_in_search, and low "
        "statistical confidence."
    )

    PLAIN_ENGLISH = (
        "The rule is simple: hold SPY when the 6-month momentum of the SOX/SPY "
        "relative-strength ratio -- observed about three months earlier -- was "
        "above its rolling 75th percentile; otherwise hold cash. It beat both "
        "benchmarks in the search-phase OOS window, but the lead-lag tests show "
        "feedback rather than a clean lead, the edge over SPY's own momentum is "
        "marginal, and the rule lost in every pre-test crisis."
    )

    SIGNAL_RULE_MD = """
**Rule in plain English:** when semiconductors have recently been outpacing the market by enough, own SPY; otherwise stand aside. Specifically: hold SPY when the 6-month momentum of the SOX/SPY relative-strength ratio, observed 63 trading days (about three months) earlier, is above its rolling 75th percentile (latest threshold value 30.68); otherwise hold cash.

If-then form:
- **IF** `sox_spy_ratio_mom_6m_pct` from 63 trading days ago is **above its rolling 75th percentile** -> hold SPY.
- **ELSE** -> hold cash.

Search-phase OOS results (2021-06-11 to 2026-06-17, 1,260 trading days, no holdout final exam yet): Sharpe 1.57 vs 0.82 buy-and-hold and 0.83 SPY-own-momentum; annualized return 13.0% vs 14.0% buy-and-hold; maximum drawdown -9.7% vs -24.5%; 114 OOS trades; annual turnover 22.8; OOS win rate 20%.

The lead grid deliberately starts at one trading day, never zero: a same-day SOX reading shares the day's market move with SPY, so it is co-movement, not a forecast.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
First, the data process divides the semiconductor index by SPY each day to get the relative-strength ratio, which removes the shared market move and leaves only whether chips are leading or lagging. Second, it measures how much that ratio has changed over the past six months -- its momentum. Third, it compares the value from about three months earlier (respecting a one-day real-time floor, so no contemporaneous co-movement leaks in) against a rolling 75th-percentile threshold and converts that comparison into a position: long SPY if relative-strength momentum was strong, cash if it was weak.

This is intentionally simple. It does not forecast chip demand, model the semiconductor cycle, or pick individual stocks. It asks one question: has the chip sector's recent strength relative to the market historically lined up with a better SPY allocation?
"""

    MANUAL_USE_MD = """
This describes the backtested rule so it can be audited; it is not a trading recommendation.

1. Read SOX (`^SOX`) and SPY daily closes from Yahoo Finance.
2. Form the SOX/SPY relative-strength ratio each day (this removes shared market beta).
3. Compute the 6-month momentum of that ratio.
4. Apply the 63-trading-day lead (and the one-day real-time floor) before making the daily SPY allocation decision.
5. Hold SPY when the lagged relative-strength momentum is above its rolling 75th percentile; otherwise hold cash.

The warning label is central: this is `found_in_search`, not confirmed by a holdout final exam, and the lead-lag evidence is bidirectional feedback, not a clean semiconductor lead.
"""

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_TITLE = "Crisis Sharpe and Durability"
    WALK_FORWARD_CHART_NAME = "subperiod_sharpe"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy Sharpe by crisis episode. The winner was "
        "deeply negative in the Dot-Com bust (-1.16), the GFC (-1.06), and "
        "COVID (-0.95), and positive only in the in-sample 2022 rates shock "
        "(+0.36). The headline OOS Sharpe is carried by the benign 2021-26 "
        "window, not by crisis resilience."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution across 4,607 valid "
        "searched combinations, with the median (0.67) BELOW buy-and-hold "
        "(0.82). The winner's 1.57 Sharpe is the maximum of the search, not a "
        "typical result -- most searched rules lost to the index."
    )

    CAVEATS_MD = """
**Why confidence is low:**

1. The tradable signal is SOX/SPY RELATIVE STRENGTH, not raw SOX: the same-day SOX-SPY correlation is 0.709, which is co-movement (shared market beta), not a forecast. The ratio is used precisely to partial that out.
2. The lead-lag evidence is BIDIRECTIONAL feedback: Toda-Yamamoto Granger is significant in both directions at every lag, with the reverse (SPY->SOX) taller at short lags. This is not a clean semiconductor lead.
3. The edge over SPY's OWN momentum is marginal and horizon-dependent: significant at 21 days (p=0.033) but NOT at 63 days (p=0.075), with incremental R^2 of about one percentage point.
4. In-sample Sharpe is 0.10 versus OOS 1.57 -- a large gap. The OOS window (2021-2026) was a strong semiconductor bull, a favorable draw.
5. The median valid combo scored 0.67, below buy-and-hold's 0.82 -- the search mostly found losers. Win rate is 20%.
6. The rule LOST in every pre-OOS crisis (Dot-Com -1.16, GFC -1.06, COVID -0.95). Bootstrap p-value is 0.041 (just under 5%), and the rule is marked `found_in_search` -- not yet confirmed on an untouched final-exam window. Rolling-correlation sign is unstable (agrees with the full-sample sign only 42% of the time).

**What this means:** use the page as evidence for a candidate search-found relative-strength tilt, not as proof that semiconductors lead the S&P 500.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the lagged SOX/SPY relative-strength momentum crosses back "
        "above its rolling 75th-percentile threshold, moving from 0% to 100% "
        "SPY exposure, and a SELL back to cash when it falls below. Over the "
        "OOS window the rule made 114 such position changes."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2021-09-15",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: sox_spy_ratio_mom_6m_pct > roll_p75; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Yahoo Finance | `^SOX` PHLX Semiconductor Index (back to 1994) | Daily |
| Target | Yahoo Finance | SPY adjusted close / returns | Daily |
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The tradable construction is the SOX/SPY RELATIVE-STRENGTH ratio, not raw "
    "SOX: the same-day SOX-SPY daily-return correlation is 0.709 (co-movement / "
    "shared market beta), so dividing by SPY partials out the shared move and "
    "leaves only whether semiconductors are leading or lagging the market. "
    "Daily transforms include 1/3/6/12-month momentum of both raw SOX and the "
    "SOX/SPY ratio, plus 126- and 252-day z-scores and 21-day realized "
    "volatility. The winning signal is `sox_spy_ratio_mom_6m_pct` (6-month "
    "momentum of the ratio) evaluated against a rolling 75th-percentile "
    "threshold with a 63-trading-day lead. A discipline point specific to this "
    "pair: the lead grid starts at one trading day, never zero -- a same-day "
    "SOX reading shares the day's market move with SPY, so using it would be "
    "co-movement masquerading as a forecast."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation (same-day + forward) | Is the big SOX-SPY number a forecast or co-movement? | Separates shared beta from forward signal |
| Pre-whitened CCF | At which offsets do the series echo each other? | Filters autocorrelation that can fake lead-lag structure |
| Toda-Yamamoto Granger (both directions) | Does SOX lead SPY, or do they feed back? | Formal lead-lag test, robust to integration order |
| Incremental-edge regression | Does relative strength beat SPY's OWN momentum? | The toughest, fairest benchmark for a tilt |
| Local projections (HAC) | What is the forward SPY response across horizons? | Horizon-by-horizon response check |
| Quantile regression | Does the signal work differently in weak vs strong markets? | Separates downside-management from upside-chasing |
| Transfer entropy | Is there nonlinear information flow, and in which direction? | Model-free nonlinear robustness check |
| HMM regimes | Which periods are unusual high-variance regimes? | Backdrop and regime context, not the winning signal |
| Rolling correlation / structural break | Is the relationship stable over time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: SOX and SOX/SPY-ratio transforms x threshold rules x strategy families x orientations x leads (starting at L1, never L0) x lookbacks. The final tournament file has 6,760 benchmark-excluded strategy combinations plus benchmark rows (valid=False per ECON-T4). Of those, 4,607 strategy combinations pass validity filters and are eligible for winner selection. The winning rule is `sox_spy_ratio_mom_6m_pct / T2_roll_p75 / P1_long_cash / procyclical / L63 / LB63`.

All headline performance on the portal is search-phase OOS, not a holdout final exam. This distinction is binding for the pair because `results/phlxsox_spy/evidence_status.json` marks the pair `found_in_search`. The lead-lag evidence is bidirectional feedback, the edge over SPY's own momentum is marginal, and the median valid combo (0.67) lost to buy-and-hold (0.82) -- all reinforcing the low-confidence label.
"""

_REFERENCES_MD = """
1. Yahoo Finance, `^SOX` PHLX Semiconductor Index and SPY price history.
2. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes."
3. Jorda, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections."
4. Moskowitz, T., Ooi, Y. H. & Pedersen, L. H. (2012). "Time series momentum."
5. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods."
6. Bailey, D. H., Borwein, J., Lopez de Prado, M. & Zhu, Q. J. (2014). "Pseudo-mathematics and financial charlatanism: the effects of backtest overfitting on out-of-sample performance."
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Out-of-sample window 2021-06-11 to 2026-06-17, 1,260 trading days "
        "(about five years); in-sample ends 2021-06-10. Total tournament count "
        "is 6,760 benchmark-excluded strategy combinations; 4,607 are valid. "
        "Evidence status: found_in_search. The OOS window is a single "
        "semiconductor-bull regime, which is the main reason confidence is low."
    ),
    plain_english=(
        "This page explains the data, transformations, econometric tests, and "
        "tournament design behind the SOX/SPY relative-strength analysis. The "
        "most important limitations are that the tradable signal is "
        "relative strength (not raw SOX, because of the 0.709 co-movement), the "
        "lead-lag tests show bidirectional feedback rather than a clean "
        "semiconductor lead, the edge over SPY's own momentum is marginal, and "
        "the winning rule still needs a frozen-rule holdout test."
    ),
)
