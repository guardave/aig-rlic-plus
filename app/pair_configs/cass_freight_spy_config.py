"""Cass Freight Index (Shipments) × SPY pair configuration (Rule APP-PT1).

Rebuilt 20260829 after the Step C #198 Data Master history splice extended the
pair from 2016-2026 to **1990-2026** (~33 years; the aligned analytical panel
begins 1993 where SPY starts). The pipeline was re-run and every number below is
sourced from results/cass_freight_spy/ (winner_summary.json, kpis.json,
evidence_status.json, interpretation_metadata.json, core_models_20260829/*,
structural_break_cass_freight_spy.json, tournament_results_20260829.csv,
strategy_returns_20260829.csv, lead_correlation_20260829.csv,
lead_tournament_20260829.csv, winner_trades_broker_style.csv).

HONEST FRAMING (binding).
  * The pair has **GRADUATED** from the old "short-OOS (<5yr)" caveat: the OOS
    window is now **2018-04-30 → 2026-07-31 = 100 months ≈ 8.3 years**, clearing
    the five-year reliability floor. The earlier 36-month framing is retired.
  * The winner is STILL a **found-in-search CANDIDATE, not a validated edge**:
    the median valid combo (OOS Sharpe 0.77) UNDERPERFORMS buy-and-hold (0.93) —
    the typical rule subtracts value; the winner is the right tail of a
    16,080-combo search (11,501 valid); bootstrap p = 0.0852 (not significant at
    5%); IS Sharpe 0.61 vs OOS 1.30; and there is no fresh final-exam holdout.
  * **Freight does NOT lead SPY.** Toda-Yamamoto Granger finds NO significant
    forward lag (Cass→SPY min p = 0.39) while the REVERSE (SPY→Cass) is
    significant at lags [1,2,3,5,6]; pre-whitened CCF is significant only on the
    stocks-lead side (lags −16,−14,−12) → the pipeline classifies the lead-lag as
    **lagging/coincident**. Present freight as a procyclical demand/activity
    overlay, NOT a forecast.
  * **Winner:** cass_freight_contraction (the freight-recession flag) /
    T3_zscore_neg_1.0 / P1 Long-Cash, **procyclical** direction / lead **L9** /
    LB36. OOS Sharpe 1.30 vs B&H 0.93; annualized return 17.4% vs 15.4%; maximum
    drawdown **−19.5% vs −23.9%**. The **drawdown reduction is the defensible
    virtue** — read the Sharpe edge as volatility avoidance (sitting out deep
    freight-contraction months), not directional forecasting.
  * The **L9 lead is a likely search artifact** (freight is coincident/lagging;
    issue #28 tracks the fleet-wide L9 pattern) — flag adjacent-lead durability
    as a caution.
  * NSA: the Cass source is NOT seasonally adjusted, so MoM/3M/6M/level-zscore
    signals are seasonally contaminated. The winner (contraction) is on the
    seasonally-CLEAN set. The globally highest-raw combo
    (accel/T2_roll_p25/P3_long_short_pro/L3, OOS Sharpe 1.47) rides a
    contaminated signal and is EXCLUDED by design (see winner_summary
    objective_runner_up_divergence).
  * History now spans dot-com, GFC, COVID and 2022. But the STRATEGY's OOS window
    is 2018+, so the dot-com and GFC subperiods remain `insufficient_data` for the
    strategy (they are in-sample); only the INDICATOR history charts
    (history_zoom_dotcom / history_zoom_gfc) now show those episodes.

Winner-rule mechanics (resolved against winner_trades_broker_style.csv): the
position keys off the freight-contraction flag as it stood **9 months earlier**.
Over the OOS window the rule holds SPY when that 9-month-lagged flag is on
(position 100%) and is mostly cash when it is off (avg exposure ~74%). Because
freight does not lead SPY and L9 is a likely artifact, this is best read as a
found-in-search STATE overlay whose payoff is drawdown reduction — not a
real-time timing mechanism. The pipeline's `direction: procyclical` label
reflects the INDICATOR (regime quartiles: strong freight → better concurrent
equity conditions, Q4 Sharpe 1.15 vs Q1 0.34), not a clean tradable forecast.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Freight That Moves With the Market, Not Before It"
    PAGE_SUBTITLE = (
        "Cass Freight Index: Shipments (FRED FRGSHPUSM649NCIS) × S&P 500 "
        "(SPY) — monthly, history 1990-2026 (aligned panel from 1993). A "
        "NOT-seasonally-adjusted goods-economy gauge."
    )

    HEADLINE_H2 = (
        "## An 8.3-year out-of-sample Sharpe of 1.30 vs 0.93 buy-and-hold — now "
        "past the 5-year reliability floor — but the lead-lag tests still find NO "
        "forward causality (freight does not lead stocks), the median search rule "
        "underperforms buy-and-hold, and the edge is almost entirely lower "
        "drawdown, so the winner is a found-in-search CANDIDATE, not a validated "
        "edge (bootstrap p = 0.085, n.s.)"
    )

    PLAIN_ENGLISH = (
        "The Cass Freight Index measures how much stuff is physically being "
        "shipped around the United States — a direct read on the goods economy. "
        "It is intuitive to think shipping activity should lead the stock market. "
        "We tested that every way we know how, and the honest answer is modest: "
        "freight and the S&P 500 (SPY) move *together* (if anything the market "
        "moves first), not one reliably ahead of the other. A strategy search "
        "surfaced a rule that beats buy-and-hold on an 8.3-year out-of-sample "
        "window — but it wins almost entirely by taking *less* risk (a −19.5% "
        "worst drawdown versus −23.9%), the typical rule in the search actually "
        "underperforms buy-and-hold, and no forward-causality mechanism sits "
        "behind it. So we present it as a candidate with its warning labels "
        "attached, not as a proven edge."
    )

    WHERE_THIS_FITS = (
        "This is a page about a *coincident/lagging* indicator that now has a "
        "long, honest history. With the 1990-2026 data the out-of-sample test "
        "finally clears the five-year floor, which is a genuine improvement over "
        "the old short-window version of this pair. But length is not the same as "
        "an edge: knowing that freight *confirms* rather than *forecasts* the "
        "market is the real, useful takeaway. Investors wanting genuine advance "
        "warning should look to leading measures (e.g. the high-yield credit "
        "spread in the HY-IG pair) rather than shipment volumes."
    )

    ONE_SENTENCE_THESIS = (
        "Freight shipments move with the stock market rather than ahead of it "
        "(lead-lag tests find no forward causality, and the market if anything "
        "leads freight); a strategy search found a rule that beats buy-and-hold "
        "over 8.3 years of out-of-sample data (Sharpe 1.30 vs 0.93) mostly by "
        "cutting drawdown, but the median rule underperforms and the result is "
        "not statistically significant (bootstrap p = 0.085), so it is a "
        "found-in-search candidate, not a validated forecasting edge."
    )

    KPI_CAPTION = (
        "every performance number on this page is an out-of-sample figure over "
        "2018-04 → 2026-07 (100 months ≈ 8.3 years — now past the 5-year "
        "reliability floor). The winner was found as the best seasonally-clean of "
        "11,501 valid combinations, where the *median* valid rule (Sharpe 0.77) "
        "actually underperforms buy-and-hold (0.93); bootstrap p = 0.085, not "
        "significant at the 5% level. Treat it as a candidate, not a verdict."
    )

    HERO_TITLE = "Cass Freight Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — year-over-year Cass Freight shipment "
        "growth and the S&P 500 (SPY) on a common time axis back to the early "
        "1990s, NBER recessions shaded. The two series broadly rise and fall "
        "together (the 2009 GFC trough and the 2022-24 freight recession are the "
        "clearest episodes) — the visual signature of a coincident/lagging, not a "
        "leading, indicator."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Freight-Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: concurrent S&P 500 (SPY) performance in each quartile "
        "of freight growth, from weakest (Q1) to strongest (Q4) — annualized "
        "Sharpe and return. The gradient is broadly procyclical: Sharpe is lowest "
        "when freight growth is weakest (Q1 = 0.34) and highest when it is "
        "strongest (Q4 = 1.15), with a mild wobble between Q2 (1.00) and Q3 "
        "(0.88). Descriptive and concurrent — a state description, not a forecast."
    )

    NARRATIVE_SECTION_1 = """
### Freight as a coincident gauge of the goods economy

The Cass Freight Index tracks the dollar-normalized volume of shipments moving
through the freight networks of hundreds of US shippers — a hands-on measure of
how much physical stuff the economy is moving. When factories are busy and
retailers are restocking, shipments rise; when the goods economy cools, they
fall. It is a genuine real-economy signal.

The intuitive hope is that freight *leads* the stock market — that trucks and
rail cars slow before equities do. We tested that hypothesis directly, and the
data does not support it. Across every lead-lag test on the Evidence page,
freight growth and the S&P 500 (SPY) move essentially *together*; if anything the
formal tests show the market moving **first** (equities Granger-cause freight at
several lags, not the other way round). Freight is a **coincident/lagging**
indicator here, not a leading one.

**What this means:** freight shipments are a good confirmation of where the goods
economy stands right now, but not a dependable early-warning system for stocks.
That is worth knowing on its own — but it also means any timing rule built on
this series is reading a contemporaneous (or trailing) echo, not a forecast.

<!-- expander: What exactly is the Cass Freight Index? -->
The Cass Freight Index: Shipments (FRED series `FRGSHPUSM649NCIS`) is a monthly
index of North American freight shipment *volumes* compiled by Cass Information
Systems from the freight bills it processes for a large panel of shippers. It is
reported **not seasonally adjusted (NSA)**, which matters for the statistics: raw
month-over-month changes carry a seasonal pattern, so we lean on year-over-year
and trend/regime transforms that wash the seasonality out.
<!-- /expander -->

### A long history now — but length is not an edge

The 1990-2026 Data Master splice gives this pair a real history: after carving
out an in-sample period, the out-of-sample window is now **100 months (about 8.3
years, 2018-04 → 2026-07)** — comfortably past the five-year floor we use before
trusting a backtested Sharpe. That is a genuine improvement over the old
short-window version of this pair, and we say so plainly.

But a long window is not the same as a validated edge. In this search the
*median* valid rule scores an out-of-sample Sharpe of **0.77 — below the 0.93 of
simply buying and holding SPY**. The typical rule you could have built here
*subtracts* value; the published winner is the best tail of a 16,080-combination
search, and a bootstrap re-shuffle puts the odds of a result this good arising by
chance at about 8.5% — above the 5% bar. So every number on the Strategy page is
still labelled a *candidate found in search*.
"""

    # All four history-zoom episodes now have data (1990+ splice). The dot-com and
    # GFC charts show the INDICATOR history; the STRATEGY's OOS window is 2018+, so
    # those two episodes remain in-sample / insufficient_data for the strategy.
    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Bust (1998-2003)",
            "narrative": (
                "With the 1990+ history now in the dataset, the dot-com episode "
                "is a real chart for the first time. Freight growth and equities "
                "cooled together into the 2001 recession and recovered together — "
                "coincident, with no clear freight lead. Note this window predates "
                "the strategy's 2018+ out-of-sample period, so it informs the "
                "indicator story, not the backtest."
            ),
            "caption": (
                "Coincident cooling — freight and SPY softened together into 2001 "
                "(indicator history; pre-dates the strategy OOS window)"
            ),
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007-2009)",
            "narrative": (
                "Shipment volumes fell hard alongside the 2008-09 equity "
                "collapse and troughed with the market in early 2009 — a "
                "textbook coincident downturn, not a freight-led one. Like the "
                "dot-com window this is in-sample for the strategy (OOS begins "
                "2018), so it is shown as indicator context."
            ),
            "caption": (
                "Freight and SPY collapsed and troughed together in 2008-09 "
                "(indicator history; in-sample for the strategy)"
            ),
        },
        {
            "slug": "covid",
            "title": "COVID Freight Collapse (2020)",
            "narrative": (
                "Shipment volumes crashed in April-May 2020 as goods demand and "
                "production seized, then rebounded with the broader recovery. "
                "Freight and equities moved together through the shock — "
                "coincident, with no clear lead either way. This episode falls "
                "inside the strategy's OOS window."
            ),
            "caption": (
                "Coincident shock — freight and SPY fell and recovered together "
                "in 2020"
            ),
        },
        {
            "slug": "inflation_2022",
            "title": "2022-2024 Freight Recession",
            "narrative": (
                "A prolonged goods-economy downturn kept year-over-year "
                "shipments negative for an extended stretch while equities "
                "de-rated in 2022 and then recovered. Freight weakness coincided "
                "with the equity drawdown rather than preceding it."
            ),
            "caption": (
                "Freight recession overlapped the 2022 equity drawdown — "
                "concurrent, not leading"
            ),
        },
    ]

    NARRATIVE_SECTION_2 = """
### "Coincident, not leading" — so how can there be a timing strategy?

This is the fair question, and it deserves a straight answer before we show the
rule. The Evidence page confirms there is no reliable way to use *today's* freight
growth to *forecast* tomorrow's stock returns — if anything the market leads
freight. The strategy on the next page does not contradict that; it does not
claim to forecast.

What the search found is a *state* rule: the position keys off the
freight-contraction flag as it stood some months earlier, and standing in the
market in those states has historically coincided with better *risk-adjusted*
(not higher) equity outcomes. The rule's edge over buy-and-hold is almost
entirely lower drawdown (−19.5% versus −23.9%) at a similar return — it wins by
sitting out some deep-contraction months, i.e. by avoiding volatility, not by
calling market direction. Because the underlying relationship is
coincident/lagging and one lead in particular (nine months) is doing the work, we
treat the result as a candidate pattern, not a discovered predictive edge.

### What the search surfaced: a candidate overlay, honestly labelled

Across **16,080 strategy combinations** (11,501 passing validity filters, of
which 6,181 use seasonally-clean signals), the best *seasonally-clean* rule was:
be long the S&P 500 (SPY) when the freight-contraction flag — viewed at a
9-month lag — indicates the recent freight-contraction state, and hold cash
otherwise. Over the 8.3-year out-of-sample window it scored an OOS Sharpe of 1.30
versus 0.93 for buy-and-hold, annualized 17.4% versus 15.4%, with a maximum
drawdown of −19.5% versus −23.9%.

This finding comes with non-negotiable context, stated here rather than in a
footnote:

- **The median rule loses to buy-and-hold.** The typical valid combination scores
  an OOS Sharpe of 0.77, below buy-and-hold's 0.93. The winner is the right tail
  of a large search, not a representative result.
- **No forward causality.** Every lead-lag test says freight and stocks are
  coincident/lagging (the market, not freight, is the one that leads); there is
  no forecasting mechanism behind the rule.
- **Not significant.** A bootstrap re-shuffle puts the probability of a result
  this good arising by chance at about 8.5% — above the 5% bar.
- **The 9-month lead is a likely artifact.** For a coincident/lagging series the
  choice of a 9-month lead is not economically motivated; adjacent leads score
  unevenly, so treat the specific L9 as fragile (issue #28 tracks this
  fleet-wide pattern).
- **Seasonality excluded by design.** The globally highest-scoring raw combo (OOS
  Sharpe 1.47) rides a seasonally-contaminated signal (the Cass index is not
  seasonally adjusted) and was thrown out; the published winner is the best
  *clean* rule.

**What this means:** treat this as *"a candidate pattern found by search, whose
one defensible feature is lower drawdown"* — not a validated trading edge.
Expectations for a frozen-rule hold-out test should be calibrated low.

### What this means for investors

- **Do not use freight growth as an early-warning signal for stocks** — the tests
  find it coincident/lagging, not leading.
- **Read the winner's Sharpe as volatility avoidance** — its edge is a smaller
  worst-case drawdown, not a higher return, and the median search rule loses to
  buy-and-hold.
- **Freight is a good confirmation of the goods economy's current state** —
  useful for context, not for forecasting equity returns.
"""

    TRANSITION_TEXT = (
        "One question, attacked several independent ways: *does Cass Freight "
        "growth carry information about future S&P 500 (SPY) returns — or do the "
        "two simply move together?* Methods that agree from different angles are "
        "far more convincing than any single test. Here they converge on the same "
        "modest answer: coincident/lagging, with no confirmed forward edge."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks
# =========================================================================
CORRELATION_CHART_NAME = "correlation_heatmap"
GRANGER_CHART_NAME = "granger_f_by_lag"
CCF_CHART_NAME = "ccf_prewhitened"
LOCAL_PROJECTIONS_CHART_NAME = "local_projections"
TRANSFER_ENTROPY_CHART_NAME = "transfer_entropy"
QUANTILE_CHART_NAME = "quantile_coef"
HMM_REGIME_CHART_NAME = "hmm_regime_probs"


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Battery",
    method_theory=(
        "Pearson, Spearman, and distance correlations between every "
        "freight-growth transform (year-over-year, month-over-month, "
        "trend-deviation, z-scores, contraction flag) and forward SPY returns at "
        "1/3/6/12-month horizons."
    ),
    question=(
        "Is there any raw statistical association between freight growth today "
        "and stock returns tomorrow?"
    ),
    how_to_read=(
        "Rows are signal transforms, columns are forward-return horizons; each "
        "cell's color shows the correlation — deeper color = stronger. Pale cells "
        "mean no association."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        "What this shows: correlations between freight-growth transforms and "
        "forward S&P 500 (SPY) returns across horizons. Every cell is small — the "
        "strongest is only about r = 0.13."
    ),
    observation=(
        "The whole grid is pale. The single largest cell is the 3-month freight "
        "change versus 3-month-forward returns (Pearson r = +0.13, p ≈ 0.01 on "
        "400 overlapping observations) — but that transform is one of the "
        "seasonally-CONTAMINATED signals (the Cass series is NSA), so even this "
        "small reading is not a clean tradable edge. The seasonally-clean "
        "year-over-year and trend transforms are near zero at every horizon."
    ),
    deep_dive_title="Why treat the heatmap as triage rather than proof?",
    deep_dive_content=(
        "Forward returns at overlapping horizons induce serial correlation in the "
        "cells, and the largest cell here sits on a seasonally-contaminated "
        "transform. Treat the heatmap as descriptive triage; the formal tests "
        "below carry the inferential weight."
    ),
    interpretation=(
        "There is no sizeable, clean linear association at any tradeable horizon "
        "— consistent with a coincident/lagging goods-economy gauge rather than a "
        "short-horizon forecaster."
    ),
    key_message=(
        "At every tradeable horizon the raw association between freight growth "
        "and future stock returns is close to zero, and the one non-trivial cell "
        "rides a seasonally-contaminated signal."
    ),
)


CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "For a monthly-rebalanced strategy the decision is: how stale should the "
        "signal be allowed to get before we trade on it? This block computes "
        "Pearson correlations between each Cass Freight signal lagged L = 0…12 "
        "months and the SPY 1-month forward return. **Caveat for this pair:** the "
        "causality tests find NO forward causality (Cass→SPY insignificant at "
        "every lag), so this lead view is expected to show little genuine "
        "predictive content at any lead — and honest reporting requires us to "
        "show that, not hide it."
    ),
    question=(
        "Does lagging the freight signal by any number of months recover real "
        "predictive content for SPY — or does the coincident/lagging character "
        "mean no lead works?"
    ),
    how_to_read=(
        "Rows are Cass Freight signal variants; columns are signal lead in MONTHS "
        "(L0 = contemporaneous, L12 = 12 months ago). Forward horizon fixed at 1 "
        "month. Cell shading is Pearson r against `spy_fwd_1m`. Stars: `*` "
        "p<0.05."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "Pearson correlations between **signal lagged L months** and **SPY "
        "1-month forward return**. Cells are small at nearly every lead; the few "
        "starred cells are scattered and inconsistent in sign — the signature of "
        "a coincident/lagging series with no stable predictive lead."
    ),
    observation=(
        "Reading across the rows, correlations are small (|r| mostly < 0.1) and "
        "the handful that clear p<0.05 are scattered across leads and flip sign "
        "between transforms — no coherent, repeatable predictive lead emerges. "
        "The traded signal, the freight-contraction flag, is weak across its "
        "whole row and peaks only at L9 (r ≈ +0.07). **There is no lead at which "
        "freight cleanly predicts next-month SPY.**"
    ),
    interpretation=(
        "This is an **honest near-null result**, and stating it is the point. No "
        "lead carries stable forward content. **In plain English:** freight moves "
        "with the economy and the market rather than leading them, so you cannot "
        "reliably trade SPY by lagging the freight signal. That the winner's own "
        "signal peaks at L9 — with a correlation of only ~0.07 — is exactly why "
        "we flag the deployed 9-month lead as a likely search artifact."
    ),
    key_message=(
        "No lead works cleanly: the traded contraction signal is weak and "
        "inconsistent across L = 0…12, peaking only weakly at L9. This confirms "
        "the coincident/lagging verdict — freight responds to the cycle, it does "
        "not lead SPY."
    ),
)


LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This block sweeps the monthly lead grid L = 1…12 and plots the best OOS "
        "Sharpe at each lead against the reference line of SPY buy-and-hold "
        "(Sharpe 0.93). Read it alongside the coincident/lagging verdict: any "
        "Sharpe here comes from a search over a state overlay, not from forward "
        "causality."
    ),
    question=(
        "Where does the traded 9-month lead sit on the sweep — and is its Sharpe "
        "a robust ridge or a fragile artefact of a coincident series with no "
        "genuine forward edge?"
    ),
    how_to_read=(
        "Bars: best OOS Sharpe among seasonally-CLEAN combos at each monthly "
        "lead. The vermillion line traces the published winner's own signal (the "
        "contraction flag) across leads; the star marks the deployed lead.\n\n"
        "Why the tallest raw bar is not the published winner: the grey dotted "
        "line shows the best OOS Sharpe *any* signal reached at each lead — it "
        "peaks higher at L3 (1.47), but that peak belongs to an acceleration "
        "signal that is seasonally contaminated (the Cass index is not seasonally "
        "adjusted), which we exclude by design. The published winner is the best "
        "*clean* combo, and its lead (L9) is genuinely fragile: adjacent leads "
        "score unevenly, which is why we call L9 a likely artifact."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "Best OOS Sharpe per monthly lead with the winner's own curve traced "
        "across leads. The published winner sits at L9 (1.30); the globally "
        "tallest raw bar at L3 (1.47) is a seasonally-contaminated combo excluded "
        "by design. On a coincident/lagging series with no forward causality, "
        "read any Sharpe here as a search-found state overlay."
    ),
    observation=(
        "The published winner (`cass_freight_contraction / T3_zscore_neg_1.0 / "
        "P1_long_cash` procyclical, L9, OOS Sharpe 1.30) is the best "
        "SEASONALLY-CLEAN combo. The highest raw bar (accel/L3, 1.47) is excluded "
        "as seasonally contaminated. Across the clean winner-signal curve the "
        "profile is uneven (e.g. L6 ≈ 1.08, L8 ≈ 0.93, L9 ≈ 1.30, L10 ≈ 1.21), "
        "which — combined with the lead-correlation near-null — reads as a "
        "search-found regularity, not a stable predictive ridge."
    ),
    interpretation=(
        "The honest summary: with no forward causality, a contaminated combo "
        "scoring even higher, and an uneven adjacent-lead profile, the traded L9 "
        "Sharpe should be read as riding a search-found state pattern — weight it "
        "accordingly. Honesty over polish."
    ),
    key_message=(
        "The published L9 winner (1.30) is the best seasonally-CLEAN combo, not "
        "the raw maximum (an excluded contaminated L3 combo at 1.47). With no "
        "forward causality and an uneven lead profile, treat the specific "
        "9-month lead as a likely artifact."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality (Toda-Yamamoto)",
    method_theory=(
        "Granger causality (a statistical test of whether one series helps "
        "forecast another beyond the other's own history), in the Toda-Yamamoto "
        "form that stays valid even if the series' trends are imperfectly "
        "removed."
    ),
    question="Who moves first — freight shipments or the stock market?",
    how_to_read=(
        "Bars show the test statistic at each lag from 1 to 12 months, both "
        "directions; bars clearing the dashed significance line indicate "
        "forecasting power at that lag."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: Granger F-statistics by lag, both directions, with the "
        "per-lag 5% critical line. The forward (freight → SPY) direction clears "
        "the line at NO lag; the reverse (SPY → freight) clears it at several."
    ),
    observation=(
        "In the freight → SPY direction, no bar at any of the 12 lags clears the "
        "line (smallest p-value 0.39). In the SPY → freight direction the test IS "
        "significant, at lags [1, 2, 3, 5, 6] (smallest p-value 0.011). The "
        "market forecasts freight, not the other way round."
    ),
    deep_dive_title="Why Toda-Yamamoto instead of plain Granger?",
    deep_dive_content=(
        "Plain Granger tests can produce spurious results when series have unit "
        "roots or borderline stationarity; Toda-Yamamoto augments the model with "
        "extra lags so the statistic keeps its standard distribution regardless. "
        "We run it on the stationary year-over-year transform."
    ),
    interpretation=(
        "This is the fingerprint of a lagging (not leading) indicator: equities "
        "help predict freight, but freight carries no forward information about "
        "equities. Freight responds to the same goods-economy conditions the "
        "market has already priced."
    ),
    key_message=(
        "Freight does not Granger-cause the stock market at any lag; the market "
        "Granger-causes freight at several — a lagging, not leading, "
        "relationship."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "A pre-whitened Cross-Correlation Function (CCF) — correlation between "
        "the two series at every monthly offset from −18 to +18, after filtering "
        "each series' own autocorrelation so trends cannot masquerade as lead-lag "
        "structure."
    ),
    question=(
        "At which specific monthly offsets, if any, do the two series echo each "
        "other?"
    ),
    how_to_read=(
        "The X-axis is the offset in months — on this chart's convention a "
        "negative offset means the market moves before freight (freight lags), a "
        "positive offset means freight moves before the market. Bars outside the "
        "dashed band are significant at 95% confidence."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: pre-whitened cross-correlation at 37 monthly offsets "
        "with 95% confidence bands. The only significant bars sit at negative "
        "offsets (−16, −14, −12 — the market-leads side); nothing is significant "
        "on the freight-leads side."
    ),
    observation=(
        "Of 37 offsets, three bars clear the band — at −16, −14 and −12 months, "
        "all on the side where the market leads freight. Nothing is significant "
        "on the freight-leads side at any offset."
    ),
    interpretation=(
        "Every significant offset is on the wrong side for a leading indicator — "
        "the market edges the freight series, not the reverse. The CCF "
        "corroborates the Granger result: no freight-leads structure at any "
        "monthly offset."
    ),
    key_message=(
        "Across 37 monthly offsets there is no credible window in which freight "
        "growth foreshadows stock returns; the only echoes run the other way "
        "(the market leads freight by roughly a year)."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections (a horizon-by-horizon regression technique that traces "
        "how one variable responds after a movement in another), with HAC "
        "standard errors robust to overlapping horizons."
    ),
    question=(
        "If freight growth jumps today, where is the stock market 1, 3, 6, and 12 "
        "months later?"
    ),
    how_to_read=(
        "Each panel plots the estimated response (line) with its confidence band "
        "(shading) across horizons; a band that straddles zero means no "
        "detectable effect."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: impulse-response panels, forward and reverse. In the "
        "freight → SPY panel the confidence band straddles zero at every horizon; "
        "the reverse (market → freight) direction is where the significant "
        "responses appear."
    ),
    observation=(
        "In the freight → SPY panel the band straddles zero at 1, 3, 6 and 12 "
        "months (p-values 0.59, 0.70, 0.98, 0.58) — no detectable forward effect "
        "at any horizon. The reverse direction (market → freight) is significant "
        "at the 6- and 12-month horizons, mirroring the Granger picture."
    ),
    interpretation=(
        "At the horizons a monthly strategy actually trades, there is no "
        "detectable forward effect of freight on equities; the detectable "
        "impulse runs from the market to freight, not the reverse."
    ),
    key_message=(
        "A jump in freight growth tells you nothing statistically useful about "
        "where stocks will be over the next year; the response that survives runs "
        "from the market to freight."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy — a model-free measure of directed information flow "
        "that can detect *non-linear* relationships ordinary correlation misses "
        "(estimated on tercile-binned data with 500 permutations)."
    ),
    question=(
        "Could freight predict stocks in some curvy, non-linear way the linear "
        "tests can't see?"
    ),
    how_to_read=(
        "Two bars — one per direction; the annotation shows each bar's "
        "permutation p-value. A small p-value (under 0.05) would indicate genuine "
        "information flow."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "What this shows: bidirectional transfer entropy with permutation "
        "p-values. Freight → SPY is clearly insignificant (p = 0.44); SPY → "
        "freight is insignificant too (p = 0.67)."
    ),
    observation=(
        "Freight → SPY: p = 0.44. SPY → freight: p = 0.67. Neither direction "
        "clears the 5% bar."
    ),
    deep_dive_title="Could a non-linear channel be hiding here?",
    deep_dive_content=(
        "On a coarsely tercile-binned monthly sample transfer entropy has low "
        "power, but here both readings sit far above 0.05 and agree with the "
        "sharper linear tests (Granger, CCF, local projections). There is no "
        "hidden non-linear channel to rescue."
    ),
    interpretation=(
        "No non-linear channel rescues the indicator: both directions are clearly "
        "insignificant."
    ),
    key_message=(
        "There is no non-linear escape hatch — the absence of forward "
        "predictability is robust to how you look."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression — instead of asking how freight growth affects the "
        "*average* future return, it asks how it affects the *worst* and *best* "
        "outcomes (the tails), where risk signals usually earn their keep."
    ),
    question=(
        "Does freight growth at least predict tail risk — the really bad months — "
        "even if it can't predict the average?"
    ),
    how_to_read=(
        "The X-axis runs across outcome percentiles (5th = worst months, 95th = "
        "best); the line is the estimated effect at each percentile with its "
        "confidence band. A risk signal typically shows a significant effect at "
        "the left tail."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: quantile-regression coefficient by percentile with "
        "confidence band. Only the two lowest quantiles (5th, 10th) are "
        "significant, and the effect is small."
    ),
    observation=(
        "The coefficient is significant only at the 5th and 10th percentiles "
        "(p = 0.011 and 0.020), and both effects are small and positive; from the "
        "25th percentile upward the band straddles zero (all p-values ≥ 0.12)."
    ),
    interpretation=(
        "There is a faint, small left-tail association but nothing a strategy "
        "could lean on — freight growth does not meaningfully flag elevated crash "
        "risk. It fails at the mean and is only marginal at the extreme tail."
    ),
    key_message=(
        "Freight growth predicts neither average stock returns nor tail risk in "
        "any tradeable way; only a faint effect survives at the extreme left "
        "tail."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Context (HMM and Quartiles)",
    method_theory=(
        "A two-state Hidden Markov Model (HMM — a statistical model that infers "
        "unobserved \"calm\" vs \"stressed\" regimes from the data's behavior) "
        "fitted to the freight series, plus a simple sort of history into "
        "quartiles of freight growth with the concurrent SPY return in each."
    ),
    question=(
        "Even without prediction, do states of the freight cycle coincide with "
        "systematically different stock-market environments?"
    ),
    how_to_read=(
        "The HMM panel shades periods by inferred regime probability over time; "
        "the quartile chart (on the Story page) shows annualized concurrent SPY "
        "returns in four bars, sorted from weakest (Q1) to strongest (Q4) freight "
        "growth."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: HMM-inferred high-variance regime probability over "
        "time, NBER recessions shaded. The high-variance state (about 32% of "
        "months) aligns with the GFC, the 2020 shock and the 2022-24 freight "
        "recession. The quartile view of the same story is on the Story page."
    ),
    observation=(
        "The HMM's high-variance state (31.9% of months) aligns with the "
        "goods-economy downturns (GFC, 2020 shock, 2022-24 freight recession). "
        "The quartile bars are broadly procyclical: concurrent returns are best "
        "when freight growth is strongest (Q4 Sharpe 1.15 vs Q1 0.34), with a "
        "mild wobble at Q2 (1.00) / Q3 (0.88)."
    ),
    deep_dive_title="How stable is the relationship over time?",
    deep_dive_content=(
        "The rolling 24-month correlation between the two series is sign-stable "
        "(stability score 0.76, verdict `sign_stable` in "
        "`structural_break_cass_freight_spy.json`). On the longer 1993+ sample "
        "the structural-break test now DOES flag a candidate break at 2020-04 "
        "(sup-F 5.11, bootstrap p = 0.08) — the COVID dislocation is detectable "
        "in the longer history. The state relationship is directionally "
        "consistent, but it is coincident, and cross-COVID results should be read "
        "with that break in mind."
    ),
    interpretation=(
        "This is the constructive reading of a coincident/lagging series: strong "
        "freight growth describes a healthy goods-economy state that has "
        "coincided with better equity conditions. Descriptive, concurrent — not a "
        "forecast."
    ),
    key_message=(
        "Freight growth doesn't forecast the market, but its strongest readings "
        "have coincided with better equity conditions — the broadly procyclical "
        "regularity the strategy search latched onto."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The tests converge: freight and the stock market move together — if anything the market leads",
    "overview": (
        "*One question, attacked several independent ways: does Cass Freight "
        "growth carry information about future S&P 500 (SPY) returns — or do the "
        "two simply move together? Methods that agree from different angles are "
        "far more convincing than any single test. Here they converge on the same "
        "modest answer: coincident/lagging, with no confirmed forward edge — and "
        "the market, not freight, is the one that leads.*\n\n"
        "All statistics computed on monthly data over the 1990-2026 history "
        "(aligned panel from 1993), from "
        "`results/cass_freight_spy/core_models_20260829/`."
    ),
    "plain_english": (
        "This section shows the statistical evidence on whether freight shipments "
        "predict the stock market. The lead-lag tests — correlation, Granger "
        "causality, pre-whitened cross-correlation, local projections, and "
        "transfer entropy — converge: freight and the S&P 500 (SPY) move "
        "together, and where anything leads it is the market leading freight, not "
        "the reverse. The one regularity that survives (strong freight growth "
        "coinciding with better concurrent equity conditions) is descriptive — it "
        "is what the strategy search on the next page latched onto."
    ),
    # Row counts VERIFIED by reading each file at authoring time (2026-08-29);
    # counts exclude the header row.
    "downloads": [
        {"label": "Granger causality, both directions × 12 lags (24 rows)",
         "path": "results/cass_freight_spy/core_models_20260829/granger_causality.csv"},
        {"label": "Granger F-statistics by lag, freight → SPY (12 rows)",
         "path": "results/cass_freight_spy/granger_by_lag.csv"},
        {"label": "Correlation battery, signal × horizon × metric (176 rows)",
         "path": "results/cass_freight_spy/core_models_20260829/correlations.csv"},
        {"label": "Pre-whitened CCF, offsets −18..+18 (37 rows)",
         "path": "results/cass_freight_spy/core_models_20260829/ccf_prewhitened.csv"},
        {"label": "Local projections, forward + reverse × 4 horizons (8 rows)",
         "path": "results/cass_freight_spy/core_models_20260829/local_projections.csv"},
        {"label": "Transfer entropy, both directions (2 rows)",
         "path": "results/cass_freight_spy/core_models_20260829/transfer_entropy.csv"},
        {"label": "Quantile regression, 7 quantiles (7 rows)",
         "path": "results/cass_freight_spy/core_models_20260829/quantile_regression.csv"},
        {"label": "Regime quartile returns, Q1–Q4 (4 rows)",
         "path": "results/cass_freight_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe, episodes (4 rows)",
         "path": "results/cass_freight_spy/subperiod_sharpe.csv"},
        {"label": "Rolling 24-month correlation (351 rows)",
         "path": "results/cass_freight_spy/rolling_correlation_cass_freight_spy.csv"},
    ],
    "level1": [CORRELATION_BLOCK, CORRELATION_LEAD_VIEW_BLOCK, LEAD_TOURNAMENT_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Lead Analysis", "Lead Tournament", "Granger Causality", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, TRANSFER_ENTROPY_BLOCK,
               QUANTILE_BLOCK, REGIME_BLOCK],
    "level2_labels": ["Local Projections", "Transfer Entropy",
                      "Quantile Regression", "Regime Context (HMM)"],
    "tournament_intro": (
        "The statistical tests above ask whether the indicator *predicts*. The "
        "tournament asks a more pragmatic question: across every reasonable "
        "trading rule you could build from this series, does *any* of them beat "
        "simply holding the S&P 500 (SPY)?\n\n"
        "We tested a grid of **16,080 strategy combinations** — signal transforms "
        "× threshold schemes × strategy families × orientations × leads L1..L12 × "
        "lookback windows — of which **11,501 passed validity filters** (the "
        "buy-and-hold benchmark row is excluded from this count). Because the "
        "Cass series is NOT seasonally adjusted, the winner-selection objective is "
        "restricted to the **6,181 seasonally-CLEAN combinations**. The crucial "
        "honesty check: the *median* valid combination scores an out-of-sample "
        "Sharpe of just **0.77 — below the 0.93 of buy-and-hold**. The typical "
        "rule subtracts value; the headline rule on the Strategy page is the best "
        "clean tail of that distribution, and the globally highest raw score "
        "(1.47) came from a seasonally-CONTAMINATED signal and was excluded by "
        "design. In plain English: on an 8.3-year window the winner is a candidate "
        "found in search — not a validated edge."
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is coincident/lagging — freight and "
        "stocks move together, and the market is the one that leads. What remains "
        "is the pragmatic question the tournament answered: the next page shows "
        "the one candidate rule the search surfaced, with every fragility flag "
        "attached."
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = (
        "The Strategy: A Long-or-Cash Overlay Whose Edge Is Lower Drawdown"
    )
    PAGE_SUBTITLE = (
        "— it beats buy-and-hold over an 8.3-year out-of-sample window (past the "
        "5-year floor), but almost entirely by cutting drawdown, on a "
        "coincident/lagging indicator with no confirmed forward edge, and the "
        "median search rule underperforms. No fresh hold-out test has been run."
    )

    PLAIN_ENGLISH = (
        "The best seasonally-clean rule from a 16,080-combination search: hold "
        "the S&P 500 (SPY) when the freight-contraction flag — viewed with a "
        "9-month delay — indicates the recent freight-contraction state, and hold "
        "cash otherwise. Over the 8.3-year out-of-sample window (2018-04 → "
        "2026-07) it scored a Sharpe of 1.30 versus 0.93 for buy-and-hold, "
        "annualized 17.4% versus 15.4%, with a −19.5% maximum drawdown versus "
        "−23.9%. The window now clears the five-year floor — a real improvement "
        "over the old short-history version of this pair — but the lead-lag tests "
        "find no forward causality, the median rule in the search underperforms "
        "buy-and-hold, and it fails the standard significance test (bootstrap "
        "p = 0.085). Its one defensible feature is the smaller drawdown. Read it "
        "as a candidate overlay found by search — its final exam on untouched data "
        "has not been run."
    )

    SIGNAL_RULE_MD = """
**Rule:** Hold the S&P 500 (SPY) **when the freight-contraction flag (`cass_freight_contraction`, = 1 when year-over-year freight growth is negative), viewed at a 9-month lag, sits above its rolling z-score threshold — i.e. the flag as it stood nine months ago indicates the freight-contraction state. Otherwise hold cash.** (Family: Long/Cash; signal `cass_freight_contraction`, rolling z-score threshold T3, lead L9, lookback LB36 — per `winner_summary.json`; `direction: procyclical`.)

If-then form (as executed in `winner_trades_broker_style.csv`):
- **IF** the 9-month-lagged contraction flag is on (above its rolling threshold) → **BUY/HOLD SPY (100% invested)**.
- **ELSE** (flag off) → **HOLD CASH (0% invested)**.

Search-phase results (OOS 2018-04-30 → 2026-07-31, 100 months ≈ 8.3 years — **now past the 5-year floor, but no fresh hold-out test yet**): OOS Sharpe 1.30 vs 0.93 buy-and-hold; annualized return 17.4% vs 15.4%; maximum drawdown −19.5% vs −23.9%; 5 OOS trades (turnover 0.6/yr); average exposure ~74% (win rate 52%).

**Read this as a candidate, not a validated edge.** The indicator is coincident/lagging (no forward causality), the *median* rule in the search underperforms buy-and-hold (0.77 vs 0.93), the result is not statistically significant (bootstrap p = 0.085), and the 9-month lead is a likely search artifact. This pair's `strategy_objective` (per `interpretation_metadata.json`) is **max_sharpe**: with a return close to buy-and-hold (17.4% vs 15.4%), the winner's edge is overwhelmingly risk reduction — a lower drawdown (−19.5% vs −23.9%) and lower volatility, achieved by sitting out some deep-contraction months. Read the Sharpe as volatility avoidance, not directional forecasting.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
No formulas — three steps:

**What changes in the world:** the physical goods economy speeds up or slows down — factories, retailers, and distributors ship more or less freight. The Cass Freight Index measures that shipment volume each month.

**What the signal measures:** each month, the rule looks at the freight-contraction flag — a simple 1/0 marker of whether year-over-year freight growth was negative — as it stood nine months ago (the nine-month delay is what the tournament happened to score highest; it is not economically motivated, which is exactly why we flag it as a likely artifact). It then compares that lagged reading to its rolling z-score threshold.

**What decision it drives:** lagged flag on (the freight-contraction state) → be in the market; lagged flag off → hold cash. Because the relationship is coincident/lagging — freight does not lead the market, if anything the market leads freight — this is best understood as a *state* overlay whose payoff is a smoother ride (lower drawdown), not a forecast of where stocks are going.
"""

    MANUAL_USE_MD = (
        "First, the framing: what follows describes how the backtested rule works "
        "so you can replicate and audit it — it is **not** a recommendation to "
        "trade it. This rule is a search-phase candidate (best clean combo of "
        "11,501 valid, where the median rule underperforms buy-and-hold; 8.3-year "
        "OOS but no fresh hold-out test; bootstrap p = 0.085, not significant at "
        "5%; no confirmed forward causality; a 9-month lead that is likely an "
        "artifact). With that understood, the monthly routine — no code required "
        "— is:\n\n"
        "1. **Pull the freight series** — FRED series `FRGSHPUSM649NCIS` (Cass "
        "Freight Index: Shipments, NSA; published ~mid-month for the prior "
        "month).\n"
        "2. **Compute year-over-year growth and the contraction flag** — the flag "
        "is 1 when the 12-month change is negative, 0 otherwise.\n"
        "3. **Apply the 9-month delay** — the reading the rule acts on this month "
        "is the contraction flag from nine months ago.\n"
        "4. **Compare to its rolling threshold** — is that delayed flag above its "
        "rolling z-score threshold (window per the LB36 lookback)? See "
        "`winner_trade_log.csv` for the full threshold path.\n"
        "5. **Take the position** — lagged flag above threshold → hold SPY (100% "
        "invested); below → hold cash (0% invested). Re-evaluate once a month.\n\n"
        "Remember the warning labels: coincident/lagging indicator, median rule "
        "underperforms, not statistically significant, a 9-month lead that is "
        "likely an artifact."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    # Distribution histogram (not a scatter) — the caption describes elements that
    # actually exist on the tournament_sharpe_dist chart.
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution of the valid strategy "
        "combinations. The winner line (1.30) is the right tail; the median valid "
        "combo (0.77) sits BELOW buy-and-hold (0.93) — the typical rule subtracts "
        "value, so the winner is a found-in-search draw, not a representative "
        "result."
    )

    CAVEATS_MD = """
**Why we do not call this a validated edge** — flags, none softened (all from `winner_summary.json`, `evidence_status.json`, and the tournament artifacts):

1. **The median rule loses to buy-and-hold.** The median valid combination scores an OOS Sharpe of **0.77 — below buy-and-hold's 0.93**. The winner is the right tail of a 16,080-combo search (11,501 valid), which is the textbook setup for an over-fit result.
2. **No forward causality.** Every lead-lag test (Granger, CCF, local projections, transfer entropy) says freight and stocks are coincident/lagging — freight does not forecast the market, and if anything the market leads freight (Granger SPY→Cass significant at lags [1,2,3,5,6]). The rule reads a state, not a forecast.
3. **Not statistically significant.** A bootstrap re-shuffle puts the probability of a result this good arising by chance at about **8.5%** — above the 5% threshold. Not significant.
4. **In-sample vs out-of-sample gap.** The rule scored Sharpe **0.61 in-sample** and 1.30 out-of-sample; an OOS figure well above the IS figure suggests a favorable draw, not a stable property.
5. **The 9-month lead is a likely artifact.** For a coincident/lagging series a 9-month lead has no economic motivation; adjacent leads score unevenly (issue #28 tracks this fleet-wide pattern). Do not rely on L9 durability.
6. **Seasonality excluded by design.** The source is NOT seasonally adjusted; the globally highest-scoring raw combo (Sharpe 1.47, an acceleration signal) is seasonally contaminated and was excluded. The published winner is the best *clean* combo.

**What it does have going for it:** the out-of-sample window is now **100 months (≈8.3 years, past the 5-year floor)** — a real improvement over the old short-history version of this pair — and the one defensible virtue is **drawdown reduction (−19.5% vs −23.9%)** at a similar return, i.e. the Sharpe edge is volatility avoidance. The honest label, from `evidence_status.json`, is still a **found-in-search CANDIDATE**. The prescribed next step is a final exam: freeze this rule and test it once on an untouched window.

**Further caveats:**

- **The edge is risk, not return.** The winner beats buy-and-hold mostly on drawdown (−19.5% vs −23.9%) and volatility with a similar return (17.4% vs 15.4%). That defensive profile is the strongest thing about it — but it was earned on a window that, while long, still may not resemble the next bear market.
- **A structural break IS now flagged.** On the longer 1993+ sample the Quandt-Andrews test flags a candidate break at **2020-04** (sup-F 5.11, bootstrap p = 0.08); the rolling correlation is sign-stable (0.76). Cross-COVID results should be read with that break in mind.
- **Costs.** Returns are gross of costs; at 5 basis points per trade and only ~0.6 trades/yr the haircut is negligible (see `tournament_validation_20260829/`) — cost drag is not this pair's problem; the coincidence and the found-in-search selection are.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair's out-of-sample window:** on "
        "**2021-07-31** the broker-style log records a SELL — the 9-month-lagged "
        "contraction reading (0.000) had fallen below its rolling threshold "
        "(0.117), so the flag was off and the position moved from 100% to 0% "
        "(cash). The matching BUY appears on **2022-10-31**, when the delayed "
        "reading (1.000) came back above its rolling threshold (0.083) — the "
        "contraction state was flagged and the strategy returned to the market. "
        "You can find both rows in the broker-style CSV."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2021-07-31",
        "side": "SELL",
        "instrument": "SPY",
        "quantity_pct": "0.0",
        "commission_bps": "5",
        "reason": (
            "9-month-lagged contraction flag 0.000 vs rolling threshold 0.117 — "
            "exit to cash"
        ),
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED — Cass Information Systems | `FRGSHPUSM649NCIS` (Cass Freight Index: Shipments, NSA index) | Monthly (from 1990) |
| Target | Yahoo Finance | SPY (SPDR S&P 500 ETF, dividend-adjusted) | Monthly (from 1993) |

Dataset extended to **1990-2026** by the Step C #198 Data Master splice; the aligned analytical panel begins 1993 where SPY starts. The source is **not seasonally adjusted**, so year-over-year and regime transforms are preferred over raw month-over-month changes.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw shipments index is non-stationary in levels and NOT seasonally "
    "adjusted, so analysis runs on transforms: year-over-year % change (the "
    "seasonally-robust cycle gauge), the % deviation of the level from its "
    "12-month moving average, 3- and 6-month momentum, rolling z-scores, an "
    "acceleration term, and a contraction flag (= 1 when year-over-year growth is "
    "negative — the WINNING signal). Non-YoY-family momentum and level-z-score "
    "transforms carry a seasonal component and are flagged seasonally-contaminated; "
    "the tournament objective is restricted to seasonally-clean signals. The Cass "
    "publication lag (~2 weeks) makes a 1-month signal delay the real-time floor; "
    "the tradeable lead grid therefore starts at L1 (L0 appears only as a "
    "non-tradable diagnostic)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation battery (Pearson/Spearman/distance) | Any raw association at any horizon? | Cheap triage before formal tests |
| Toda-Yamamoto Granger causality | Who forecasts whom? | Robust to unit-root ambiguity in macro series |
| Pre-whitened CCF | At which monthly offsets do the series echo? | Filters autocorrelation that fakes lead-lag patterns |
| Local projections (HAC errors) | Where is SPY h months after a freight move? | Horizon-by-horizon honesty; robust to overlapping returns |
| Transfer entropy (500 permutations) | Any non-linear information flow? | Model-free check the linear tests can't provide |
| Quantile regression | Does the signal at least predict tail risk? | Cyclical signals sometimes work at the left tail only |
| Two-state HMM + quartile sorts | Do freight-cycle states coincide with distinct market environments? | The descriptive/regime reading appropriate to a coincident series |
| Structural break (sup-F, bootstrap) | Did the relationship change mid-sample? | Guards against averaging two different regimes |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: signal transforms (data transforms + contraction/HMM/Markov regime states) × threshold schemes (fixed percentiles, rolling percentiles, z-score bands, zero-line) × 6 strategy families × 2 orientations (procyclical/countercyclical) × leads {1…12} months × lookbacks {24, 36, 60} months = **16,080 combinations** plus a buy-and-hold benchmark row. Validity filters (OOS Sharpe > 0.3, turnover < 24/yr, ≥ 24 OOS months) → **11,501 valid**, whose MEDIAN OOS Sharpe is 0.77 — below buy-and-hold's 0.93. Because the source is NOT seasonally adjusted, the winner-selection objective is restricted to the **6,181 seasonally-CLEAN** valid combinations (median clean OOS Sharpe 0.76). Out-of-sample split: in-sample through 2018-03, out-of-sample **2018-04-30 → 2026-07-31 (100 months ≈ 8.3 years — past the 5-year floor)**. Winner selected by the standard cascade; the globally highest raw-Sharpe combo (accel/L3, 1.47) was EXCLUDED as seasonally contaminated, and the published winner (contraction/L9, 1.30) is the best clean combo. Runner-up: yoy / T3_zscore_1.0 / P3_long_short_counter / L10 (Sharpe 1.25) — a different construction. All tournament CSV metrics are decimal ratios.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_cass_freight_spy.py` — deterministic, fixed seeds. The canonical monthly return series for chart producers is `strategy_returns_20260829.csv`; its Sharpe/drawdown/return reconcile with `winner_summary.json`. Stationarity tests were produced by the data stage and confirmed, not re-run, by the econometrics stage.
"""

_REFERENCES_MD = """
1. Cass Information Systems, *Cass Freight Index Report* — methodology and coverage of the Shipments component.
2. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes." *Journal of Econometrics*, 66(1–2), 225–250.
3. Jordà, Ò. (2005). "Estimation and inference of impulse responses by local projections." *American Economic Review*, 95(1), 161–182.
4. Stock, J. H. & Watson, M. W. (1999). "Business cycle fluctuations in US macroeconomic time series." *Handbook of Macroeconomics* — coincident vs leading indicator classification.
5. Simonsohn, U., Simmons, J. P. & Nelson, L. D. (2020). "Specification curve analysis." *Nature Human Behaviour*, 4, 1208–1214 — basis for the best-of-N position disclosure.
6. Bailey, D. H. & López de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality." *Journal of Portfolio Management*, 40(5), 94–107.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "Monthly data; history 1990-2026 (aligned analytical panel from 1993 "
        "where SPY starts). Out-of-sample split: in-sample through 2018-03, "
        "out-of-sample 2018-04-30 → 2026-07-31 (100 months ≈ 8.3 years). The OOS "
        "window now CLEARS the 5-year reliability floor — but the winner remains "
        "found-in-search (the median valid combo underperforms buy-and-hold; "
        "bootstrap p = 0.085; no fresh hold-out)."
    ),
    plain_english=(
        "One monthly data series (the Cass Freight Index of US shipment volumes, "
        "now back to 1990) and the S&P 500 ETF (SPY, from 1993). We turned the "
        "freight index into growth, trend and regime transforms, ran several "
        "independent lead-lag tests (all agree: freight and stocks move together, "
        "and if anything the market leads freight), then searched over 16,000 "
        "trading-rule combinations on data split so rules were built on pre-2018 "
        "history and scored on an 8.3-year 2018-2026 window. Every number on "
        "these pages can be reproduced by one deterministic script, and every "
        "number is labelled a candidate because the median rule underperforms "
        "buy-and-hold and the indicator is coincident/lagging."
    ),
)
