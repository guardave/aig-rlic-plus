"""Cass Freight Index (Shipments) × SPY pair configuration (Rule APP-PT1).

New pair, Mode 1, branch feat260705_cass_freight_spy. Structure wired by
Ace (chart-name constants, downloads list); user-facing narrative across
Story / Evidence / Strategy / Methodology authored by Research Ray
(feat260705 finished pass). Honest coincident/candidate framing throughout
— deliberately does NOT oversell.

HONEST FRAMING (binding). Empirical verdict for this pair is
**coincident / no confirmed forward edge**:
  - Toda-Yamamoto Granger finds NO significant lag in either direction
    (Cass→SPY and SPY→Cass); pre-whitened CCF significant only at lag −2
    (target-leads side), none on the loans/freight-leads side →
    classified `coincident_or_none`.
  - The tournament winner (dev_trend / T3_zscore_neg_1.0 / P1 Long-Cash
    counter / L3 / LB36, OOS Sharpe 2.49 vs B&H 1.67) is a SHORT-OOS
    (36-month, <5yr) FOUND-IN-SEARCH **candidate**, not a validated edge;
    bootstrap p = 0.10 (not significant at 5%); durability
    `insufficient_data`.
  - Source series is NSA → non-YoY-family transforms are seasonally
    contaminated. The published winner is seasonally CLEAN; the globally
    highest-raw-Sharpe combo (mom3m/L2, 2.60) was EXCLUDED as
    seasonally-contaminated (see winner_summary objective_runner_up_divergence).

Numbers sourced from results/cass_freight_spy/ (winner_summary.json,
kpis.json, evidence_status.json, core_models_20260705/*, structural_break,
tournament_validation_20260705/bootstrap.csv, lead_correlation_20260705.csv,
lead_winner_curve_20260705.csv).

GH #13 framing: LEAD_TOURNAMENT_BLOCK["how_to_read"] carries Ray's
plain-English framing (rendered before the lead_sharpe_distribution chart)
explaining why the published winner's lead (L3) can sit below the chart's
tallest bar (an excluded seasonally-contaminated L2 combo).

Winner-rule direction (resolved against winner_trades_broker_style.csv):
LONG SPY when the 3-month-lagged dev_trend signal is at/above its rolling
z-score threshold (freight near/above trend = risk-on); CASH when it falls
below (freight contracting). This is PROCYCLICAL (matches
winner_summary.direction and interpretation_metadata.expected_direction).
The raw code `P1_long_cash_counter` / `threshold_rule=lt` encode the base
Long/Cash family BEFORE the counter inversion; the net economic orientation
is procyclical, as every row of the broker-style trade log confirms
(signal below threshold -> position 100%->0%).
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
        "(SPY) — monthly, analytical sample 2016-01 → 2026-05 (~124 months). "
        "A SHORT-history, NOT-seasonally-adjusted goods-economy gauge."
    )

    # Ray-authored (feat260705) — honest candidate framing, RES-11/RES-18 Template A.
    HEADLINE_H2 = (
        "## Search-phase OOS Sharpe 2.49 vs 1.67 buy-and-hold on a 36-month "
        "(<5yr) window — but the lead-lag tests find NO forward causality "
        "(freight and stocks move together, not one before the other), so "
        "the winner is a found-in-search CANDIDATE, not a validated edge "
        "(bootstrap p = 0.10, n.s.)"
    )

    PLAIN_ENGLISH = (
        "The Cass Freight Index measures how much stuff is physically being "
        "shipped around the United States — a direct read on the goods "
        "economy. It is intuitive to think shipping activity should lead the "
        "stock market. We tested that every way we know how, and the honest "
        "answer is more modest: freight and the S&P 500 (SPY) move *together*, "
        "not one reliably ahead of the other. A strategy search did surface a "
        "high-scoring timing rule, but on a short (36-month) test window and "
        "with no confirmed forward causality behind it — so we present it as a "
        "candidate with its warning labels attached, not as a proven edge."
    )

    WHERE_THIS_FITS = (
        "This is a page about a *coincident* indicator with a short usable "
        "history — the kind where honesty about limits matters more than a "
        "headline Sharpe. Knowing that freight confirms rather than forecasts "
        "the market is useful risk knowledge in itself. Investors wanting "
        "genuine advance warning should look to leading measures (e.g. the "
        "high-yield credit spread in the HY-IG pair) rather than shipment "
        "volumes."
    )

    ONE_SENTENCE_THESIS = (
        "Freight shipments move with the stock market rather than ahead of it "
        "(lead-lag tests find no forward causality); a strategy search found a "
        "high-scoring rule (OOS Sharpe 2.49 vs 1.67 buy-and-hold) but only on "
        "a 36-month window, so it is a found-in-search candidate — not a "
        "validated forecasting edge (bootstrap p = 0.10, n.s.)."
    )

    KPI_CAPTION = (
        "every performance number on this page is a SEARCH-PHASE, "
        "out-of-sample figure on a SHORT window (2023-06 → 2026-05, 36 "
        "months, below the 5-year reliability floor). The winner was found as "
        "the best of 9,556 valid combinations; bootstrap p = 0.10, not "
        "significant at the 5% level. Treat it as a candidate, not a verdict."
    )

    HERO_TITLE = "Cass Freight Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — year-over-year Cass Freight "
        "shipment growth and the S&P 500 (SPY) on a common time axis, NBER "
        "recessions shaded. The two series broadly rise and fall together — "
        "the visual signature of a coincident, not a leading, indicator."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Freight-Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: forward S&P 500 (SPY) performance in each quartile "
        "of freight growth, from weakest (Q1) to strongest (Q4) — annualized "
        "Sharpe and return. Forward returns are somewhat better when freight "
        "growth is in its strongest quartile (Q4 Sharpe 1.39 vs Q1 0.80), "
        "consistent with a procyclical read. Descriptive and regime-dependent "
        "on a short sample — not a forecast."
    )

    # Ray-authored (feat260705) — honest, no overselling.
    NARRATIVE_SECTION_1 = """
### Freight as a coincident gauge of the goods economy

The Cass Freight Index tracks the dollar-normalized volume of shipments
moving through the freight networks of hundreds of US shippers — a hands-on
measure of how much physical stuff the economy is moving. When factories are
busy and retailers are restocking, shipments rise; when the goods economy
cools, they fall. It is a genuine real-economy signal.

The intuitive hope is that freight *leads* the stock market — that trucks and
rail cars slow before equities do. We tested that hypothesis directly, and the
data does not support it. Across every lead-lag test on the Evidence page,
freight growth and the S&P 500 (SPY) move essentially *together*: neither one
reliably forecasts the other. Freight is a **coincident** indicator here, not a
leading one.

**What this means:** freight shipments are a good confirmation of where the
goods economy stands right now, but not a dependable early-warning system for
stocks. That is worth knowing on its own — but it also means any timing rule
built on this series is reading a contemporaneous echo, not a forecast.

<!-- expander: What exactly is the Cass Freight Index? -->
The Cass Freight Index: Shipments (FRED series `FRGSHPUSM649NCIS`) is a monthly
index of North American freight shipment *volumes* compiled by Cass Information
Systems from the freight bills it processes for a large panel of shippers. It is
reported **not seasonally adjusted (NSA)**, which matters for the statistics: raw
month-over-month changes carry a seasonal pattern, so we lean on
year-over-year and trend-deviation transforms that wash the seasonality out.
<!-- /expander -->

### A short history — read the numbers with caution

The usable monthly sample here runs only from 2016, giving about ten years of
data and — after carving out a hold-out — just a **36-month out-of-sample
window**. That is below the five-year floor we use before trusting a backtested
Sharpe ratio. Short windows inflate and destabilize performance statistics, so
every number on the Strategy page is labelled a *candidate* found in search.
"""

    # Only two history-zoom charts exist for this pair (covid,
    # inflation_2022); dot-com and GFC precede the sample (chart-skipped).
    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "covid",
            "title": "COVID Freight Collapse (2020)",
            "narrative": (
                "Shipment volumes crashed in April–May 2020 as goods demand "
                "and production seized, then rebounded with the broader "
                "recovery. Freight and equities moved together through the "
                "shock — coincident, with no clear lead either way."
            ),
            "caption": (
                "Coincident shock — freight and SPY fell and recovered "
                "together in 2020"
            ),
        },
        {
            "slug": "inflation_2022",
            "title": "2022–2024 Freight Recession",
            "narrative": (
                "A prolonged goods-economy downturn kept year-over-year "
                "shipments negative for an extended stretch while equities "
                "de-rated in 2022 and then recovered. Freight weakness "
                "coincided with the equity drawdown rather than preceding it."
            ),
            "caption": (
                "Freight recession overlapped the 2022 equity drawdown — "
                "concurrent, not leading"
            ),
        },
    ]

    # Ray-authored (feat260705).
    NARRATIVE_SECTION_2 = """
### "Coincident, not leading" — so how can there be a timing strategy?

This is the fair question, and it deserves a straight answer before we show the
rule. The Evidence page confirms there is no reliable way to use *today's*
freight growth to *forecast* tomorrow's stock returns. The strategy on the next
page does not contradict that — it does not claim to forecast.

What the search found is a *state* description: periods where the freight-trend
signal sits in a particular part of its range have historically coincided with
better risk-adjusted equity conditions in this short sample. The rule mechanizes
standing in those periods and stepping aside otherwise. Because the underlying
relationship is coincident and the test window is short, we treat the result as
a candidate pattern awaiting a proper hold-out exam — not a discovered
predictive edge.

### What the search surfaced: a candidate overlay, honestly labelled

Across **13,524 strategy combinations** (9,556 passing validity filters, of
which 4,316 use seasonally-clean signals), the best *seasonally-clean* rule
was: be long the S&P 500 (SPY) when the 3-month-lagged freight trend-deviation
signal sits at or above its rolling z-score threshold (freight running near or
above its recent trend); step to cash only when freight has fallen well below
trend — a procyclical, risk-on-when-freight-is-healthy overlay. In the
36-month search window it scored an OOS Sharpe of 2.49 versus 1.67 for
buy-and-hold, with a maximum drawdown of −2.4% versus −8.3%.

This finding comes with non-negotiable context, stated here rather than in a
footnote:

- **Short window.** The out-of-sample test is only 36 months — below the
  five-year floor. Sharpe ratios on windows this short are high-variance and
  routinely over-optimistic.
- **No forward causality.** Every lead-lag test says freight and stocks are
  coincident; there is no forecasting mechanism behind the rule.
- **Not significant.** A bootstrap re-shuffle puts the probability of a result
  this good arising by chance at about 10% — above the 5% bar.
- **Seasonality excluded by design.** The globally highest-scoring raw combo
  (OOS Sharpe 2.60) was thrown out because it rides a seasonally-contaminated
  signal; the published winner is the best *clean* rule, a candidate on the
  same short window.

**What this means:** treat this as *"a candidate pattern found by search,
awaiting its final exam"* — not a validated trading edge. Expectations for a
frozen-rule hold-out test should be calibrated low.

### What this means for investors

- **Do not use freight growth as an early-warning signal for stocks** — the
  tests find it coincident, not leading.
- **Do not over-weight the headline Sharpe** — it comes from a 36-month window
  and fails the standard significance test.
- **Freight is a good confirmation of the goods economy's current state** —
  useful for context, not for forecasting equity returns.
"""

    TRANSITION_TEXT = (
        "One question, attacked several independent ways: *does Cass Freight "
        "growth carry information about future S&P 500 (SPY) returns — or do "
        "the two simply move together?* Methods that agree from different "
        "angles are far more convincing than any single test. Here they "
        "converge on the same modest answer: coincident, with no confirmed "
        "forward edge."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — method blocks (chart-name constants as module vars so
# smoke_loader's AST scan of *_CHART_NAME assigns covers each evidence chart)
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
        "trend-deviation, z-scores, contraction flags) and forward SPY "
        "returns at 1/3/6/12-month horizons."
    ),
    question=(
        "Is there any raw statistical association between freight growth "
        "today and stock returns tomorrow?"
    ),
    how_to_read=(
        "Rows are signal transforms, columns are forward-return horizons; "
        "each cell's color shows the correlation — deeper color = stronger. "
        "Pale cells mean no association."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        "What this shows: correlations between freight-growth transforms and "
        "forward S&P 500 (SPY) returns across horizons. Short-horizon cells "
        "are near zero; the only sizeable cells are at the 12-month horizon."
    ),
    observation=(
        "At the tradeable 1–6-month horizons the grid is pale — near-zero "
        "association. The strongest cell is year-over-year growth versus "
        "12-month-forward returns (Pearson r = −0.58), but only at the "
        "longest horizon and on heavily overlapping data (101 monthly "
        "observations). **Why the 12-month cell is not a tradable edge:** it "
        "is a single long-horizon, negative (mean-reverting) relationship "
        "estimated on overlapping windows in a short sample — descriptive of "
        "late-cycle dynamics, not a month-to-month signal you could position "
        "on."
    ),
    deep_dive_title="Why treat the heatmap as triage rather than proof?",
    deep_dive_content=(
        "Forward returns at overlapping horizons induce serial correlation "
        "in the cells, and the 12-month column has the fewest independent "
        "observations. Treat the heatmap as descriptive triage; the formal "
        "tests below carry the inferential weight."
    ),
    interpretation=(
        "The near-zero short-horizon cells are the tradeable ones and they "
        "show nothing. The lone 12-month cell is a slow, mean-reverting "
        "late-cycle effect, consistent with a coincident goods-economy gauge "
        "rather than a short-horizon forecaster."
    ),
    key_message=(
        "At every tradeable horizon the raw association between freight "
        "growth and future stock returns is close to zero."
    ),
)


CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "For a monthly-rebalanced strategy the decision is: how stale should "
        "the signal be allowed to get before we trade on it? This block "
        "computes Pearson correlations between each Cass Freight signal "
        "lagged L = 0…12 months and the SPY 1-month forward return. **Caveat "
        "for this pair:** the causality tests find NO forward causality "
        "(Cass→SPY insignificant at every lag), so this lead view is expected "
        "to show little genuine predictive content at any lead — and honest "
        "reporting requires us to show that, not hide it."
    ),
    question=(
        "Does lagging the freight signal by any number of months recover real "
        "predictive content for SPY — or does the coincident character mean "
        "no lead works?"
    ),
    how_to_read=(
        "Rows are Cass Freight signal variants; columns are signal lead in "
        "MONTHS (L0 = contemporaneous, L12 = 12 months ago). Forward horizon "
        "fixed at 1 month. Cell shading is Pearson r against `spy_fwd_1m`. "
        "Stars: `*` p<0.05, `**` p<0.01."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "Pearson correlations between **signal lagged L months** and **SPY "
        "1-month forward return**. Cells are small at nearly every lead; the "
        "few starred cells are scattered and inconsistent in sign — the "
        "signature of a coincident series with no stable predictive lead."
    ),
    observation=(
        "Reading across the rows, correlations are small (|r| mostly < 0.2) "
        "and the handful that clear p<0.05 are scattered across leads and "
        "flip sign between transforms — no coherent, repeatable predictive "
        "lead emerges. The traded signal `cass_freight_dev_trend_pct` peaks "
        "at L9 (r = −0.205) but is weak and inconsistent across the row. "
        "**There is no lead at which freight growth cleanly predicts "
        "next-month SPY.**"
    ),
    interpretation=(
        "This is an **honest near-null result**, and stating it is the point. "
        "Unlike pairs where a lead-correlation peak corroborates the traded "
        "lead, here no lead carries stable forward content. **In plain "
        "English:** freight moves with the economy and the market rather than "
        "leading them, so you cannot reliably trade SPY by lagging the "
        "freight signal. The strategy on the next page rides a short-window "
        "descriptive regularity, and the lead view makes that limitation "
        "explicit."
    ),
    key_message=(
        "No lead works cleanly: the traded `dev_trend` signal is weak and "
        "inconsistent across L = 0…12. This confirms the coincident verdict — "
        "freight responds to the cycle, it does not lead SPY."
    ),
)


LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This block sweeps the monthly lead grid L = 1…12 and plots the best "
        "OOS Sharpe at each lead against all valid combos; the reference line "
        "is SPY buy-and-hold (Sharpe 1.67). Read it alongside the coincident "
        "verdict: any Sharpe here comes from a short-window descriptive "
        "regularity, not from forward causality."
    ),
    question=(
        "Where does the traded 3-month lead sit on the sweep — and is its "
        "Sharpe a robust ridge or a fragile artefact of a short-history pair "
        "with no genuine forward edge?"
    ),
    how_to_read=(
        "Bars: max OOS Sharpe at each monthly lead. Strip/cloud: valid "
        "combinations at that lead. A tall thin spike is a single combo; a "
        "flat-but-wide cloud is a more robust regime.\n\n"
        "Why the tallest bar is not the published winner: the bars show the "
        "best OOS Sharpe *any* signal reached at each lead, while the "
        "highlighted line is our published strategy's own signal — a "
        "seasonally-clean freight-trend measure — traced across leads, which "
        "peaks at its chosen lead L3 (2.49). We pick a strategy for "
        "reliability, not for the single highest score: the taller bar near "
        "L2 (2.60) belongs to a momentum signal that is seasonally "
        "contaminated (the Cass index is not seasonally adjusted), which we "
        "exclude by design. So the published winner's lead can legitimately "
        "sit below the tallest bar — that gap is the seasonal filter doing "
        "its job, not a mistake."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "Best OOS Sharpe per monthly lead (bars) with the full distribution. "
        "The clean published winner sits at L3 (2.49); the globally tallest "
        "raw bar near L2 (2.60) is a seasonally-contaminated combo excluded "
        "by design. On a 36-month window and with no forward causality, read "
        "any Sharpe here as short-window and descriptive."
    ),
    observation=(
        "The published winner (`cass_freight_dev_trend / T3_zscore_neg_1.0 / "
        "P1_long_cash` counter, L3, OOS Sharpe 2.49) is the best SEASONALLY-"
        "CLEAN combo. The highest raw bar (mom3m/L2, 2.60) is excluded as "
        "seasonally contaminated. Across the clean winner-family curve the "
        "profile is uneven (L2 2.27, L3 2.49, then a dip through the mid-"
        "leads), which — combined with the lead-correlation near-null — reads "
        "as a short-window descriptive regularity, not a stable predictive "
        "ridge."
    ),
    interpretation=(
        "The honest summary: on a 36-month window, with no forward causality "
        "and a seasonally-contaminated combo scoring even higher, the traded "
        "L3 Sharpe should be read as riding a short-window descriptive "
        "pattern — weight it accordingly. Honesty over polish."
    ),
    key_message=(
        "The published L3 winner (2.49) is the best seasonally-CLEAN combo, "
        "not the raw maximum (an excluded contaminated L2 combo at 2.60). On "
        "a <5yr window with no forward causality, treat the edge as "
        "descriptive and short-window, not predictive."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality (Toda-Yamamoto)",
    method_theory=(
        "Granger causality (a statistical test of whether one series helps "
        "forecast another beyond the other's own history), in the "
        "Toda-Yamamoto form that stays valid even if the series' trends are "
        "imperfectly removed."
    ),
    question="Who moves first — freight shipments or the stock market?",
    how_to_read=(
        "Bars show the test statistic at each lag from 1 to 12 months, one "
        "panel per direction; bars clearing the dashed significance line "
        "indicate forecasting power at that lag."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: Granger F-statistics by lag, both directions, with "
        "the per-lag 5% critical line. Neither direction clears the line at "
        "any lag."
    ),
    observation=(
        "In the freight → SPY direction, no bar at any of the 12 lags clears "
        "the line (smallest p-value 0.80). In the SPY → freight direction, no "
        "bar clears it either (smallest p-value 0.061, at lag 3). Neither "
        "direction shows significant forecasting power."
    ),
    deep_dive_title="Why Toda-Yamamoto instead of plain Granger?",
    deep_dive_content=(
        "Plain Granger tests can produce spurious results when series have "
        "unit roots or borderline stationarity; Toda-Yamamoto augments the "
        "model with extra lags (d_max = 1 here) so the statistic keeps its "
        "standard distribution regardless. We run it on the stationary "
        "year-over-year transform."
    ),
    interpretation=(
        "This is the fingerprint of a coincident relationship: neither series "
        "reliably forecasts the other. Freight volumes and equity prices "
        "respond to the same underlying goods-economy conditions at roughly "
        "the same time."
    ),
    key_message=(
        "Neither freight nor the stock market Granger-causes the other — "
        "consistent with a coincident, not leading, relationship."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "A pre-whitened Cross-Correlation Function (CCF) — correlation "
        "between the two series at every monthly offset from −18 to +18, "
        "after filtering each series' own autocorrelation so trends cannot "
        "masquerade as lead-lag structure."
    ),
    question=(
        "At which specific monthly offsets, if any, do the two series echo "
        "each other?"
    ),
    how_to_read=(
        "The X-axis is the offset in months — negative offsets mean freight "
        "moves before stocks, positive offsets mean stocks move before "
        "freight. Bars outside the dashed band are significant at 95% "
        "confidence."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: pre-whitened cross-correlation at 37 monthly "
        "offsets with 95% confidence bands. The single significant bar sits "
        "at lag −2 (the stocks-lead side); nothing is significant on the "
        "freight-leads side."
    ),
    observation=(
        "Of 37 offsets, one bar (−2 months, r = 0.201) pokes above the band — "
        "on the side where the market leads freight. Nothing is significant "
        "on the freight-leads side at any offset."
    ),
    interpretation=(
        "The one significant offset is on the wrong side for a leading "
        "indicator — if anything, the market edges the freight series by "
        "about two months, not the reverse. The CCF corroborates the Granger "
        "result: no freight-leads structure at any monthly offset."
    ),
    key_message=(
        "Across 37 monthly offsets there is no credible window in which "
        "freight growth foreshadows stock returns; the only echo runs the "
        "other way (stocks lead by ~2 months)."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections (a horizon-by-horizon regression technique that "
        "traces how one variable responds after a movement in another), with "
        "HAC standard errors robust to overlapping horizons."
    ),
    question=(
        "If freight growth jumps today, where is the stock market 1, 3, 6, "
        "and 12 months later?"
    ),
    how_to_read=(
        "Each panel plots the estimated response (line) with its confidence "
        "band (shading) across horizons; a band that straddles zero means no "
        "detectable effect."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: impulse-response panels, forward and reverse. In "
        "the freight → SPY panel the confidence band straddles zero at the "
        "1/3/6-month horizons; only the 12-month point is significant (and "
        "negative)."
    ),
    observation=(
        "In the freight → SPY panel the band straddles zero at 1, 3, and 6 "
        "months (p-values 0.36, 0.33, 0.11). Only the 12-month horizon is "
        "significant and it is *negative* (coef −0.009, p < 0.001) — a slow "
        "mean-reverting effect, not a tradeable short-horizon forecast. The "
        "reverse direction is not significant at any horizon."
    ),
    interpretation=(
        "At the horizons a monthly strategy actually trades, there is no "
        "detectable forward effect. The lone significant 12-month response is "
        "negative and slow — the late-cycle mean reversion also seen in the "
        "correlation battery, not a forecasting signal."
    ),
    key_message=(
        "A jump in freight growth tells you nothing statistically useful "
        "about where stocks will be over the next six months; only a slow, "
        "negative 12-month effect survives."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy — a model-free measure of directed information flow "
        "that can detect *non-linear* relationships ordinary correlation "
        "misses (estimated on tercile-binned data with 500 permutations)."
    ),
    question=(
        "Could freight predict stocks in some curvy, non-linear way the "
        "linear tests can't see?"
    ),
    how_to_read=(
        "Two bars — one per direction; the annotation shows each bar's "
        "permutation p-value. A small p-value (under 0.05) would indicate "
        "genuine information flow."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "What this shows: bidirectional transfer entropy with permutation "
        "p-values. Freight → SPY is borderline (p = 0.06) but not significant "
        "at 5%; SPY → freight is clearly insignificant (p = 0.42)."
    ),
    observation=(
        "Freight → SPY: p = 0.06 (borderline, not significant at 5%). "
        "SPY → freight: p = 0.42. Neither direction clears the 5% bar."
    ),
    deep_dive_title="Is the borderline p = 0.06 a hidden non-linear signal?",
    deep_dive_content=(
        "On a ~120-observation, coarsely tercile-binned sample transfer "
        "entropy has low power and its permutation p-values are noisy; a "
        "single borderline reading that the sharper linear tests (Granger, "
        "CCF, local projections) all contradict is best treated as noise, not "
        "a discovered non-linear channel."
    ),
    interpretation=(
        "No non-linear channel rescues the indicator: the one borderline "
        "reading is unsupported by every linear test and sits above the 5% "
        "threshold."
    ),
    key_message=(
        "There is no reliable non-linear escape hatch — the absence of "
        "forward predictability is robust to how you look."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression — instead of asking how freight growth affects "
        "the *average* future return, it asks how it affects the *worst* and "
        "*best* outcomes (the tails), where risk signals usually earn their "
        "keep."
    ),
    question=(
        "Does freight growth at least predict tail risk — the really bad "
        "months — even if it can't predict the average?"
    ),
    how_to_read=(
        "The X-axis runs across outcome percentiles (5th = worst months, "
        "95th = best); the line is the estimated effect at each percentile "
        "with its confidence band. A risk signal typically shows a "
        "significant effect at the left tail."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: quantile-regression coefficient by percentile with "
        "confidence band. The band straddles zero at every percentile — no "
        "tail-risk channel."
    ),
    observation=(
        "The confidence band straddles zero at every percentile from the 5th "
        "to the 95th (all p-values ≥ 0.30)."
    ),
    interpretation=(
        "Many indicators fail at the mean but work at the left tail. This one "
        "fails at both — freight growth does not flag elevated crash risk "
        "either."
    ),
    key_message=(
        "Freight growth predicts neither average stock returns nor tail risk."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Context (HMM and Quartiles)",
    method_theory=(
        "A two-state Hidden Markov Model (HMM — a statistical model that "
        "infers unobserved \"calm\" vs \"stressed\" regimes from the data's "
        "behavior) fitted to the freight series, plus a simple sort of "
        "history into quartiles of freight growth with the forward SPY return "
        "in each."
    ),
    question=(
        "Even without prediction, do states of the freight cycle coincide "
        "with systematically different stock-market environments?"
    ),
    how_to_read=(
        "The HMM panel shades periods by inferred regime probability over "
        "time; the quartile chart shows annualized forward SPY returns in "
        "four bars, sorted from weakest (Q1) to strongest (Q4) freight "
        "growth."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: HMM-inferred regime probability over time, NBER "
        "recessions shaded. The 'stressed' state aligns with the 2020 shock "
        "and the 2022–24 freight recession. The quartile view of the same "
        "story is on the Story page."
    ),
    observation=(
        "The HMM's stressed state aligns with the goods-economy downturns "
        "(2020 shock, 2022–24 freight recession). The quartile bars show a "
        "mildly procyclical pattern: forward returns are best when freight "
        "growth is strongest (Q4 Sharpe 1.39 vs Q1 0.80)."
    ),
    deep_dive_title="How stable is the relationship over time?",
    deep_dive_content=(
        "The rolling 24-month correlation between the two series is "
        "sign-stable (stability score 0.80, verdict `sign_stable` in "
        "`structural_break_cass_freight_spy.json`), and the structural-break "
        "test does not flag a break (sup-F p = 0.81). The state relationship "
        "is directionally consistent — but it is coincident, and the sample "
        "is short."
    ),
    interpretation=(
        "This is the constructive reading of a coincident series: strong "
        "freight growth describes a healthy goods-economy state that has "
        "coincided with better equity conditions. Descriptive, conditional, "
        "and on a short sample — not a forecast."
    ),
    key_message=(
        "Freight growth doesn't forecast the market, but its strongest "
        "readings have coincided with better equity conditions — the mildly "
        "procyclical regularity the strategy search latched onto."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The tests converge: freight and the stock market move together, not one before the other",
    "overview": (
        "*One question, attacked several independent ways: does Cass Freight "
        "growth carry information about future S&P 500 (SPY) returns — or do "
        "the two simply move together? Methods that agree from different "
        "angles are far more convincing than any single test. Here they "
        "converge on the same modest answer: coincident, with no confirmed "
        "forward edge.*\n\n"
        "All statistics computed on monthly data, analytical sample 2016-01 "
        "→ 2026-05 (~124 months), from "
        "`results/cass_freight_spy/core_models_20260705/`."
    ),
    "plain_english": (
        "This section shows the statistical evidence on whether freight "
        "shipments predict the stock market. The lead-lag tests — correlation, "
        "Granger causality, pre-whitened cross-correlation, local "
        "projections, and transfer entropy — converge: freight and the S&P "
        "500 (SPY) move together, and neither reliably forecasts the other. "
        "The one regularity that survives (strong freight growth coinciding "
        "with better equity conditions) is descriptive and on a short sample "
        "— it is what the strategy search on the next page latched onto."
    ),
    # Row counts VERIFIED by reading each file at authoring time (2026-07-05);
    # counts exclude the header row.
    "downloads": [
        {"label": "Granger causality, both directions × 12 lags (24 rows)",
         "path": "results/cass_freight_spy/core_models_20260705/granger_causality.csv"},
        {"label": "Granger F-statistics by lag, freight → SPY (12 rows)",
         "path": "results/cass_freight_spy/granger_by_lag.csv"},
        {"label": "Correlation battery, signal × horizon × metric (160 rows)",
         "path": "results/cass_freight_spy/core_models_20260705/correlations.csv"},
        {"label": "Pre-whitened CCF, offsets −18..+18 (37 rows)",
         "path": "results/cass_freight_spy/core_models_20260705/ccf_prewhitened.csv"},
        {"label": "Local projections, forward + reverse × 4 horizons (8 rows)",
         "path": "results/cass_freight_spy/core_models_20260705/local_projections.csv"},
        {"label": "Transfer entropy, both directions (2 rows)",
         "path": "results/cass_freight_spy/core_models_20260705/transfer_entropy.csv"},
        {"label": "Quantile regression, 7 quantiles (7 rows)",
         "path": "results/cass_freight_spy/core_models_20260705/quantile_regression.csv"},
        {"label": "Regime quartile returns, Q1–Q4 (4 rows)",
         "path": "results/cass_freight_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe, episodes (4 rows)",
         "path": "results/cass_freight_spy/subperiod_sharpe.csv"},
        {"label": "Rolling 24-month correlation (89 rows)",
         "path": "results/cass_freight_spy/rolling_correlation_cass_freight_spy.csv"},
    ],
    "level1": [CORRELATION_BLOCK, CORRELATION_LEAD_VIEW_BLOCK, LEAD_TOURNAMENT_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Lead Analysis", "Lead Tournament", "Granger Causality", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, TRANSFER_ENTROPY_BLOCK,
               QUANTILE_BLOCK, REGIME_BLOCK],
    "level2_labels": ["Local Projections", "Transfer Entropy",
                      "Quantile Regression", "Regime Context (HMM)"],
    "tournament_intro": (
        "The statistical tests above ask whether the indicator *predicts*. "
        "The tournament asks a more pragmatic question: across every "
        "reasonable trading rule you could build from this series, does *any* "
        "of them beat simply holding the S&P 500 (SPY)?\n\n"
        "We tested a grid of **13,524 strategy combinations** — 10 signal "
        "transforms × multiple threshold schemes × 6 strategy families × 2 "
        "orientations × leads L1..L12 × 3 lookback windows — of which "
        "**9,556 passed validity filters** (out-of-sample Sharpe above 0.3, "
        "turnover under 24/yr, at least 24 out-of-sample months; the "
        "buy-and-hold benchmark row is excluded from this count). Because the "
        "Cass series is NOT seasonally adjusted, the objective is restricted "
        "to the **4,316 seasonally-CLEAN combinations** — whose median "
        "out-of-sample Sharpe is 1.55. The headline rule on the Strategy page "
        "is the best of those clean combinations. The globally highest raw "
        "score (2.60) came from a seasonally-CONTAMINATED signal and was "
        "excluded by design. In plain English: on a short 36-month test "
        "window, the winner is a candidate found in search — not a validated "
        "edge."
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is coincident — freight and "
        "stocks move together. What remains is the pragmatic question the "
        "tournament answered: the next page shows the one candidate rule the "
        "search surfaced, with every fragility flag attached."
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = (
        "The Strategy: A Long-or-Cash Overlay Found on a Short Window"
    )
    PAGE_SUBTITLE = (
        "— high-scoring in search, but a 36-month (<5yr) candidate on a "
        "coincident indicator with no confirmed forward edge. No hold-out "
        "test has been run yet."
    )

    PLAIN_ENGLISH = (
        "The best seasonally-clean rule from a 13,524-combination search: "
        "hold the S&P 500 (SPY) when the freight trend-deviation signal — "
        "viewed with a 3-month delay — sits at or above its rolling z-score "
        "threshold (freight running near or above its recent trend); "
        "otherwise, when freight has fallen well below trend, hold cash. In "
        "the 36-month search window "
        "(2023–2026) it scored a Sharpe ratio of 2.49 versus 1.67 for "
        "buy-and-hold, with a −2.4% maximum drawdown versus −8.3%. But the "
        "test window is short, the lead-lag tests find no forward causality, "
        "and it fails the standard significance test (bootstrap p = 0.10). "
        "Read it as a candidate overlay found by search — its final exam on "
        "untouched data has not yet been run."
    )

    SIGNAL_RULE_MD = """
**Rule:** Hold the S&P 500 (SPY) **when the 3-month-lagged Cass Freight trend-deviation signal (`cass_freight_dev_trend_pct`, the % deviation of the shipments index from its 12-month moving average) sits at or above its rolling z-score threshold — i.e. freight is running near or above its recent trend. When freight instead falls well below trend, hold cash.** This is a **procyclical** orientation: expanding freight = risk-on, contracting freight = step aside. (Family: Long/Cash; signal `cass_freight_dev_trend`, rolling z-score threshold T3, lead L3, lookback LB36 — per `winner_summary.json`; `direction: procyclical`. The raw tournament code `P1_long_cash_counter` names the encoding relative to the Long/Cash base family, not an economic countercyclical stance — the net orientation is procyclical, as the trade log confirms.)

If-then form:
- **IF** the 3-month-old freight trend-deviation reading is at or above its rolling z-score threshold → **BUY/HOLD SPY (100% invested)**.
- **ELSE** (freight well below trend) → **HOLD CASH (0% invested)**.

Search-phase results (2023-06 → 2026-05, 36 months — **short window, no hold-out test yet**): OOS Sharpe 2.49 vs 1.67 buy-and-hold; annualized return 23.2% vs 22.1%; maximum drawdown −2.4% vs −8.3%; 8 trades (turnover 2.67/yr); average exposure ~75% (win rate 61%).

**Read this as a candidate, not a validated edge.** The window is below the five-year floor, the indicator is coincident (no forward causality), and the result is not statistically significant. This pair's `strategy_objective` (per `interpretation_metadata.json`) is **max_sharpe**: with a return almost identical to buy-and-hold (23.2% vs 22.1%), the winner's entire edge is risk reduction — far lower volatility and a −2.4% drawdown versus −8.3% — achieved by sitting out the deep-contraction months.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
No formulas — three steps:

**What changes in the world:** the physical goods economy speeds up or slows down — factories, retailers, and distributors ship more or less freight. The Cass Freight Index measures that shipment volume each month.

**What the signal measures:** each month, the rule looks at how far the freight index sits above or below its own 12-month moving average (its "trend deviation"), as that reading stood three months ago (the delay reflects both the ~2-week publication lag and, mainly, the tournament's finding that the 3-month-old reading scored best in search). It then asks whether that reading is at or above its rolling z-score threshold.

**What decision it drives:** at-or-above-threshold reading (freight near or above its recent trend) → be in the market; a reading that has dropped well below threshold (freight contracting) → hold cash. Because the relationship is coincident, this is best understood as a *state* description (where the goods cycle sits right now) rather than a forecast of where stocks are going.
"""

    MANUAL_USE_MD = (
        "First, the framing: what follows describes how the backtested rule "
        "works so you can replicate and audit it — it is **not** a "
        "recommendation to trade it. This rule is a short-window search-phase "
        "candidate (best clean combo of 9,556 valid; 36-month OOS; no hold-out "
        "test yet; bootstrap p = 0.10, not significant at 5%; no confirmed "
        "forward causality). With that understood, the monthly routine — no "
        "code required — is:\n\n"
        "1. **Pull the freight series** — FRED series `FRGSHPUSM649NCIS` "
        "(Cass Freight Index: Shipments, NSA; published ~mid-month for the "
        "prior month).\n"
        "2. **Compute the trend deviation** — the % gap between the current "
        "index level and its trailing 12-month moving average.\n"
        "3. **Apply the 3-month delay** — the reading the rule acts on this "
        "month is the trend deviation from three months ago.\n"
        "4. **Compare to its rolling threshold** — is that delayed reading "
        "at or above its rolling z-score threshold (window per the LB36 "
        "lookback)? See `winner_trade_log.csv` for the full threshold path.\n"
        "5. **Take the position** — at-or-above-threshold reading (freight "
        "near or above trend) → hold SPY (100% invested); a reading well "
        "below threshold (freight contracting) → hold cash (0% invested). "
        "Re-evaluate once a month.\n\n"
        "Remember the warning labels: short (36-month) window, coincident "
        "indicator, not statistically significant."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    # Distribution histogram (not a scatter) — mirror busloans precedent so
    # the caption describes elements that actually exist.
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution of the valid strategy "
        "combinations. The vertical line marks the winner (2.49) — the "
        "maximum among seasonally-clean combos on a short 36-month window, "
        "not a typical result: the median clean combination scored 1.55."
    )

    CAVEATS_MD = """
**Why we do not call this a validated edge** — flags, none softened (all from `winner_summary.json`, `evidence_status.json`, and the tournament validation set):

1. **Short out-of-sample window.** The test window is only **36 months** (2023-06 → 2026-05), below the five-year reliability floor. Sharpe ratios on windows this short are high-variance and routinely over-optimistic. Any winner here is FOUND-IN-SEARCH by construction.
2. **No forward causality.** Every lead-lag test (Granger, CCF, local projections, transfer entropy) says freight and stocks are coincident — neither forecasts the other. The rule is reading a contemporaneous state, not a forecast.
3. **Not statistically significant.** A bootstrap re-shuffle puts the probability of a result this good arising by chance at about **10%** — above the 5% threshold. Not significant.
4. **In-sample vs out-of-sample gap.** The rule scored roughly Sharpe 1.0 in-sample and 2.49 out-of-sample; an OOS figure well above the IS figure on a short window suggests a favorable draw, not a stable property.
5. **Durability insufficient.** The sub-period durability check returns `insufficient_data` — the pre-2016 stress episodes (dot-com, GFC) fall entirely outside this series' short history, so the rule cannot be stress-tested across cycles.
6. **Seasonality excluded by design.** The source is NOT seasonally adjusted; the globally highest-scoring raw combo (Sharpe 2.60) rides a seasonally-contaminated signal and was excluded. The published winner is the best *clean* combo — still on the same short window.

**What this means:** the honest label, from `evidence_status.json`, is a **found-in-search CANDIDATE** — "the best clean rule we found by searching, not a rule that has passed an independent test." The prescribed next step is a final exam: freeze this rule and test it once on an untouched window. Given the flags above and the coincident verdict, expectations should be calibrated low.

**Further caveats:**

- **Return give-up is small but so is the edge.** The winner beats buy-and-hold mostly on drawdown (−2.4% vs −8.3%) with a similar return (23.2% vs 22.1%) over a benign window — a profile that may not survive a real bear market it never saw.
- **No structural break flagged** (sup-F p = 0.81) and the rolling correlation is sign-stable (0.80) — but on a short sample, absence of a detected break is weak reassurance.
- **Costs.** Returns are gross of costs; at 5 basis points per trade and 2.67 trades/yr the haircut is negligible (see `tournament_validation_20260705/transaction_costs.csv`) — cost drag is not this pair's problem; the short window and coincidence are.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** on **2019-02-28** the "
        "broker-style log records a SELL — the 3-month-lagged freight "
        "trend-deviation reading (−4.336) had dropped below its rolling "
        "threshold (−1.190), signalling freight well under trend and moving "
        "the position from 100% to 0% (cash). The matching BUY appears on "
        "**2019-06-30**, when the delayed reading (−1.122) came back above "
        "its rolling threshold (−2.653) and the "
        "strategy returned to the market. You can find both rows in the "
        "broker-style CSV."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2019-02-28",
        "side": "SELL",
        "instrument": "SPY",
        "quantity_pct": "0.0",
        "commission_bps": "5",
        "reason": (
            "lagged dev_trend −4.336 vs rolling threshold −1.190 — exit to "
            "cash"
        ),
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED — Cass Information Systems | `FRGSHPUSM649NCIS` (Cass Freight Index: Shipments, NSA index) | Monthly (from 1990; usable analytical span from 2016) |
| Target | Yahoo Finance | SPY (SPDR S&P 500 ETF, dividend-adjusted) | Monthly |

Dataset produced by Dana for the feat260705_cass_freight_spy wave; analytical sample 2016-01 → 2026-05 (~124 months). The source is **not seasonally adjusted**, so year-over-year and trend-deviation transforms are preferred over raw month-over-month changes.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw shipments index is non-stationary in levels and NOT seasonally "
    "adjusted, so analysis runs on transforms: year-over-year % change (the "
    "seasonally-robust cycle gauge), the % deviation of the level from its "
    "12-month moving average (`cass_freight_dev_trend_pct` — the winning "
    "signal), 3- and 6-month momentum, rolling z-scores, and a contraction "
    "flag. Non-YoY-family momentum transforms carry a seasonal component and "
    "are flagged seasonally-contaminated; the tournament objective is "
    "restricted to seasonally-clean signals. The H.8-style publication lag "
    "(~2 weeks) makes a 1-month signal delay the real-time floor; the "
    "tradeable lead grid therefore starts at L1 (L0 appears only as a "
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
Grid: 10 signals (data transforms + contraction/HMM/Markov regime states) × threshold schemes (fixed percentiles, rolling percentiles, z-score bands, zero-line) × 6 strategy families × 2 orientations (procyclical/countercyclical) × leads {1…12} months × lookbacks {24, 36, 60} months = 13,524 combinations plus a buy-and-hold benchmark row. Validity filters: OOS Sharpe > 0.3, turnover < 24/yr, ≥ 24 OOS months → 9,556 valid. Because the source is NOT seasonally adjusted, the winner-selection objective is restricted to the **4,316 seasonally-CLEAN** valid combinations (median clean OOS Sharpe 1.55). Out-of-sample split per policy `v1_max36_25pct_cap120`: in-sample through 2023-05, out-of-sample 2023-06 → 2026-05 (36 of ~124 months — a SHORT window, below the 5-year floor). Winner selected by the standard cascade; the globally highest raw-Sharpe combo (mom3m/L2, 2.60) was EXCLUDED as seasonally contaminated, and the published winner (dev_trend/L3, 2.49) is the best clean combo (Δ −0.11). All tournament CSV metrics are decimal ratios.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_cass_freight_spy.py` — deterministic, fixed seeds. The canonical monthly return series for chart producers is `strategy_returns_20260705.csv`; its Sharpe/drawdown/return reconcile with `winner_summary.json`. Stationarity tests were produced by the data stage and confirmed, not re-run, by the econometrics stage.
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
        "Monthly data; analytical sample 2016-01 → 2026-05 (~124 months). "
        "Out-of-sample split per policy v1_max36_25pct_cap120: in-sample "
        "through 2023-05, out-of-sample 2023-06 → 2026-05 (36 months). "
        "SHORT-history pair — the 36-month OOS window is below the 5-year "
        "reliability floor, so any winner is found-in-search, not validated."
    ),
    plain_english=(
        "One monthly data series (the Cass Freight Index of US shipment "
        "volumes, usable from 2016) and the S&P 500 ETF (SPY). We turned the "
        "freight index into growth and trend-deviation transforms, ran "
        "several independent lead-lag tests (all agree: freight and stocks "
        "move together, neither leads), then searched over 13,000 "
        "trading-rule combinations on data split so rules were built on "
        "pre-2023 history and scored on 2023–2026 — a short 36-month window. "
        "Every number on these pages can be reproduced by one deterministic "
        "script, and every number is labelled a candidate because the window "
        "is short and the indicator is coincident."
    ),
)
