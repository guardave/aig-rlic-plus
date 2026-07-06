"""Employment Cost Index (Total Compensation) × SPY pair configuration (Rule APP-PT1).

New pair, branch feat260705_eci_spy — the fleet's FIRST QUARTERLY pair.
Structure wired by Ace (chart-name constants, downloads list, quarterly-unit
conventions); user-facing narrative across Story / Evidence / Strategy /
Methodology is HONEST PLACEHOLDER prose pending Research Ray's finished pass.
Do NOT oversell: the lagging / reverse-causality finding is the headline.

HONEST FRAMING (binding). Empirical verdict for this pair is **LAGGING —
wages follow equities, not the reverse**:
  - Toda-Yamamoto Granger: SPY→ECI significant at ALL tested quarterly lags
    (1..4; p = 0.0135/0.0132/0.0037/0.0029); ECI→SPY significant at NONE
    (smallest p = 0.5048). Pre-whitened CCF: the only significant offset is
    lag 0 (r = −0.251, contemporaneous); nothing on either lead side →
    classified `lagging` (interpretation_metadata.key_finding).
  - The tournament winner (yoy_zscore_20q / T1_fixed_p75 / P3_long_short pro
    / L6 QUARTERS / LB_NA; OOS Sharpe 1.60 vs B&H 0.80) is a FOUND-IN-SEARCH
    **CANDIDATE**: 25-QUARTER OOS window (small sample, caveat STRONGER than
    any monthly pair); bootstrap p = 0.12 (not significant at 5%); IS Sharpe
    −0.23 vs OOS 1.60 (huge IS/OOS gap); winner signal stationarity class
    `regime_contaminated` (KPSS reject); rolling correlation `sign_unstable`
    (0.42); structural break FLAGGED (sup-F p = 0.0267, break 2009-06-30);
    durability `conditionally_durable` on ONE validated episode (COVID).
  - Direction: the winner is PROCYCLICAL (high/accelerating wage growth =
    long), CONTRADICTING the countercyclical wage-inflation prior
    (direction_consistent = false). Flag, never smooth over.

QUARTERLY conventions (first quarterly pair — make units explicit
EVERYWHERE): leads are in QUARTERS (L6q ≈ 18 months); Sharpe annualized by
√4; OOS window = 25 quarters (2020-03-31 → 2026-03-31); tradable lead grid
L1..L8 quarters (L1 = ~1-month BLS publication-lag floor).

Numbers sourced from results/eci_total_comp_spy/ (winner_summary.json,
kpis.json, evidence_status.json, oos_split_record.json,
interpretation_metadata.json, core_models_20260706/*,
structural_break_eci_total_comp_spy.json, tournament_validation_20260706/
bootstrap.csv, lead_correlation_20260706.csv, lead_winner_curve_20260706.csv,
regime_quartile_returns.csv, winner_trades_broker_style.csv,
tournament_tie_note.md).

GH #13 framing: LEAD_TOURNAMENT_BLOCK["how_to_read"] carries the framing
slot marked [[GH#13 FRAMING SLOT — RAY]] (rendered before the
lead_sharpe_distribution chart): the winner's own lead-curve peaks at its
published L6q; every point on the sweep is search-conditioned; short leads
(L1..L3 quarters) are NEGATIVE-Sharpe.

Winner-rule direction (resolved against winner_trades_broker_style.csv):
LONG SPY when the 6-quarter-lagged ECI YoY wage-growth z-score (20-quarter
window) is ABOVE its fixed 75th-percentile threshold (0.259, IS-calibrated);
SHORT SPY when it is below. Long/SHORT (P3), quarterly rebalance —
PROCYCLICAL, e.g. 2022-03-31 SELL (signal −0.275 < 0.259, position 100% →
−100%) and 2022-12-31 BUY (0.983 ≥ 0.259, −100% → 100%).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: Wages Follow the Market — They Do Not Lead It"
    PAGE_SUBTITLE = (
        "Employment Cost Index: Total Compensation (FRED ECIALLCIV, "
        "seasonally adjusted) × S&P 500 (SPY) — QUARTERLY, analytical sample "
        "2001-Q1 → 2026-Q1 (~101 quarters). The portal's first quarterly "
        "pair: all leads and windows are in QUARTERS."
    )

    # [PLACEHOLDER — RAY] Honest lagging/reversal framing; do not oversell.
    HEADLINE_H2 = (
        "## The causality tests run BACKWARDS: the stock market predicts "
        "wage growth at every tested quarterly lag, while wage growth "
        "predicts the market at none. The search's best rule (OOS Sharpe "
        "1.60 vs 0.80 buy-and-hold) sits on a 25-QUARTER window with "
        "bootstrap p = 0.12 (n.s.) — a found-in-search CANDIDATE on a "
        "lagging indicator."
    )

    # [PLACEHOLDER — RAY]
    PLAIN_ENGLISH = (
        "The Employment Cost Index (ECI) measures how fast total worker "
        "compensation — wages plus benefits — is growing in the US. The "
        "intuitive hope is that wage inflation warns about the stock market "
        "(wage pressure → Fed tightening → equity trouble). We tested that "
        "every way we know how, and the answer is the reverse: the S&P 500 "
        "(SPY) helps predict wage growth one to four quarters ahead, while "
        "wage growth predicts the market at no tested lag. Wages are a "
        "**lagging** indicator here — they follow the cycle the market has "
        "already priced. A strategy search still surfaced a high-scoring "
        "quarterly rule, but on a 25-quarter test window, without forward "
        "causality behind it, and short of statistical significance — so we "
        "present it as a candidate with its warning labels attached."
    )

    # [PLACEHOLDER — RAY]
    WHERE_THIS_FITS = (
        "This page is about a *lagging* indicator — the most honest verdict "
        "in the catalog so far, because the information flows the wrong way "
        "for forecasting. Knowing that wage growth trails equities is "
        "useful macro knowledge (it is why the Fed watches ECI and markets "
        "front-run the Fed), but investors wanting advance warning should "
        "look to leading measures (e.g. the HY-IG credit spread pair) "
        "rather than labor-cost data."
    )

    # [PLACEHOLDER — RAY]
    ONE_SENTENCE_THESIS = (
        "Wage growth (ECI total compensation) LAGS the stock market — "
        "SPY Granger-causes ECI at every tested quarterly lag and ECI "
        "Granger-causes SPY at none — and the search's best quarterly rule "
        "(OOS Sharpe 1.60 vs 0.80 buy-and-hold on 25 quarters) is a "
        "found-in-search candidate, not a validated edge (bootstrap "
        "p = 0.12, n.s.)."
    )

    KPI_CAPTION = (
        "every performance number on this page is a SEARCH-PHASE, "
        "out-of-sample figure on a 25-QUARTER window (2020-03-31 → "
        "2026-03-31) — a small quarterly sample whose caveat is STRONGER "
        "than any monthly pair to date. The winner was found as the best of "
        "1,268 valid combinations; bootstrap p = 0.12, not significant at "
        "5%; the indicator itself is empirically LAGGING. Sharpe ratios use "
        "quarterly √4 annualization. Treat it as a candidate, not a verdict."
    )

    HERO_TITLE = "ECI Total-Compensation Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — year-over-year ECI total-"
        "compensation growth (quarterly) and the S&P 500 (SPY) on a common "
        "time axis, NBER recessions shaded. Watch the turning points: the "
        "market turns first and wage growth follows quarters later — the "
        "visual signature of a lagging indicator."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Wage-Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: concurrent S&P 500 (SPY) performance in each "
        "quartile of ECI YoY wage growth, from slowest (Q1) to fastest "
        "(Q4) — annualized Sharpe and return. Returns have been better when "
        "wage growth was SLOW (Q1 Sharpe 1.17) than fast (Q4 0.67, Q3 "
        "−0.15) — a mildly countercyclical concurrent pattern. Descriptive "
        "and concurrent, not a tradable lead; note the published winner "
        "trades the opposite (procyclical) orientation at a 6-quarter lag."
    )

    # [PLACEHOLDER — RAY] Honest lagging framing throughout.
    NARRATIVE_SECTION_1 = """
### Wage growth: a textbook lagging indicator, tested honestly

The Employment Cost Index (ECI) is the BLS's cleanest quarterly measure of
total compensation growth — wages plus benefits, controlled for the mix of
jobs. It matters enormously for policy: the 2021–23 wage surge (ECI YoY
peaking near 5.1%) was the wage-price-spiral scare that drove Fed
tightening.

The intuitive hypothesis is countercyclical: accelerating wage inflation →
tighter Fed → margin compression → risk-off. We tested it directly, and the
data returned something more interesting: **the causality runs the other
way**. The stock market helps forecast wage growth one to four quarters
ahead; wage growth forecasts the market at no tested lag. Labor costs turn
*after* the cycle — exactly what the business-cycle textbooks say about
lagging indicators.

**What this means:** ECI is a rear-view mirror for equities. It confirms
what the market has already priced — useful macro context, not an
early-warning system.

<!-- expander: What exactly is the Employment Cost Index? -->
The Employment Cost Index: Total Compensation: All Civilian (FRED series
`ECIALLCIV`) is a quarterly, seasonally adjusted BLS index (Dec 2005 = 100)
of employers' total compensation costs — wages, salaries, and benefits —
holding the occupational mix constant, which makes it the preferred gauge of
underlying wage-inflation pressure. It is released about one month after
each quarter ends, so the real-time floor for any trading rule is a
one-quarter lag (L1).
<!-- /expander -->

### The first quarterly pair — small samples, explicit units

This is the portal's first QUARTERLY pair, and the units matter. Leads are
in quarters (the winner's L6 lead ≈ 18 months); Sharpe ratios are annualized
by √4; and the out-of-sample window is just **25 quarterly observations**
(2020-Q1 → 2026-Q1). Twenty-five data points is a small sample — smaller in
effective terms than any monthly pair to date — so every performance number
on these pages carries a found-in-search candidate label.
"""

    # Three history-zoom charts exist for this pair (gfc, covid,
    # inflation_2022); dot-com is chart-skipped (z-score signals not yet
    # warm in 2000–02), as are rolling_granger / rolling_sharpe_cp.
    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": (
                "[PLACEHOLDER — RAY] Equities collapsed through 2008 while "
                "ECI wage growth was still decelerating well into 2009–10 "
                "(YoY falling toward ~1.4%) — the market moved first, wages "
                "followed with a lag of several quarters. The clearest "
                "single illustration of the lagging relationship."
            ),
            "caption": (
                "Wages lagged the crash — SPY fell first, ECI growth "
                "decelerated quarters later"
            ),
        },
        {
            "slug": "covid",
            "title": "COVID Shock and Reopening (2020)",
            "narrative": (
                "[PLACEHOLDER — RAY] The equity crash and rebound of 2020 "
                "played out within two quarters; compensation growth barely "
                "flinched on the way down and only accelerated later as the "
                "reopening labor shortage built — wages again moved after "
                "the market."
            ),
            "caption": (
                "A two-quarter equity round-trip that quarterly wage data "
                "largely slept through"
            ),
        },
        {
            "slug": "inflation_2022",
            "title": "2021–23 Wage-Inflation Surge and the 2022 Bear",
            "narrative": (
                "[PLACEHOLDER — RAY] ECI YoY surged toward ~5.1% by "
                "mid-2022 — the wage-price-spiral scare feeding Fed "
                "tightening — while equities de-rated through 2022 and "
                "recovered from late 2022. Peak wage growth arrived around "
                "the equity trough, not before the drawdown: concurrent-to-"
                "lagging, not leading."
            ),
            "caption": (
                "Peak wage inflation coincided with the 2022 equity trough "
                "— it did not warn of the drawdown"
            ),
        },
    ]

    # [PLACEHOLDER — RAY]
    NARRATIVE_SECTION_2 = """
### "Lagging" — so how can there be a timing strategy at all?

The fair question first. The Evidence page shows the information flows from
the market to wages, not the reverse. The rule on the Strategy page does not
contradict that — it does not claim to forecast. What the search found is a
*state* description on a short window: quarters in which the (18-month-old)
wage-growth z-score sat in its upper range have, in the 2020–2026 window,
coincided with strong equity performance, and quarters below it with weak
performance. Mechanizing that split scored well *in that window*. Because
the indicator is lagging, the signal is regime-contaminated, and the window
is only 25 quarters, we treat the result as a candidate pattern awaiting a
frozen-rule hold-out exam — not a discovered predictive edge.

### What the search surfaced: a long/short candidate, honestly labelled

Across **2,336 strategy combinations** (1,268 passing validity filters) on
the quarterly lead grid L1..L8, the best rule was: be LONG the S&P 500 (SPY)
when the 6-quarter-lagged ECI YoY wage-growth z-score is above its fixed
75th-percentile threshold, and SHORT when below — a **procyclical**
orientation (strong wage growth = risk-on) that *contradicts* the
countercyclical wage-inflation prior. In the 25-quarter search window it
scored an OOS Sharpe of 1.60 versus 0.80 for buy-and-hold, with a maximum
drawdown of −4.3% versus −23.9%.

This finding comes with non-negotiable context, stated here rather than in a
footnote:

- **Small quarterly sample.** The out-of-sample test is 25 QUARTERS — a
  handful of independent observations; Sharpe ratios this unstable are
  routinely over-optimistic. Any winner here is FOUND-IN-SEARCH by
  construction.
- **The causality runs backwards.** Every lead-lag test says the market
  leads wages; there is no forecasting mechanism behind the rule.
- **Not significant.** Bootstrap p = 0.12 — above the 5% bar.
- **In-sample it LOST.** The same rule scored Sharpe −0.23 in-sample vs
  1.60 out-of-sample: an OOS figure that dwarfs a negative IS figure on a
  short window is the signature of a favorable draw, not a stable property.
- **Procyclical, against the prior.** The winner's direction contradicts
  the countercyclical hypothesis the pair was designed to test
  (`direction_consistent: false`).
- **Regime-contaminated signal.** The 20-quarter z-score fails the KPSS
  stationarity check, and a structural break IS flagged (2009-Q2,
  p = 0.027); the rolling correlation is sign-unstable (0.42).

**What this means:** treat this as *"a candidate pattern found by search on
a lagging indicator, awaiting its final exam"* — expectations for a
frozen-rule hold-out test should be calibrated low.

### What this means for investors

- **Do not use wage growth as an early-warning signal for stocks** — the
  tests find it lagging; if anything, the market warns about wages.
- **Do not over-weight the headline Sharpe** — 25 quarterly observations,
  bootstrap p = 0.12, and a negative in-sample Sharpe.
- **ECI remains first-rate macro context** — for reading Fed pressure and
  the wage-price dynamic — just not a forecasting input for equities.
"""

    TRANSITION_TEXT = (
        "One question, attacked several independent ways: *does wage-"
        "inflation momentum carry information about future S&P 500 (SPY) "
        "returns — or does the market move first?* Methods that agree from "
        "different angles are far more convincing than any single test. "
        "Here they converge on a directional answer: the market leads, "
        "wages lag."
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
TOURNAMENT_DIST_CHART_NAME = "tournament_sharpe_dist"


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Battery",
    method_theory=(
        "Pearson, Spearman, and distance correlations between every ECI "
        "wage-growth transform (quarter-over-quarter, year-over-year, "
        "trend-deviation, 20-quarter z-scores, acceleration, regime states) "
        "and forward SPY returns at 1-, 2-, and 4-quarter horizons."
    ),
    question=(
        "Is there any raw statistical association between wage growth today "
        "and stock returns over the coming quarters?"
    ),
    how_to_read=(
        "Rows are signal transforms, columns are forward-return horizons in "
        "QUARTERS; each cell's color shows the correlation — deeper color = "
        "stronger. Pale cells mean no association."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        "[PLACEHOLDER — RAY] What this shows: correlations between ECI "
        "transforms and forward S&P 500 (SPY) returns across quarterly "
        "horizons. The grid is weak throughout; the few standout cells are "
        "regime-state distance correlations (~0.35) and a negative "
        "HMM-stress vs 4-quarter-forward cell (Pearson −0.26, p = 0.011) — "
        "modest, long-horizon, and descriptive."
    ),
    observation=(
        "No transform shows a strong linear association with forward SPY at "
        "any quarterly horizon. The largest cells are distance correlations "
        "of coarse regime states (~0.35, no p-value under the distance "
        "metric) and a mild negative Pearson between the HMM wage-stress "
        "state and 4-quarter-forward returns (−0.26, p = 0.011) on ~93 "
        "overlapping quarterly observations."
    ),
    deep_dive_title="Why treat the heatmap as triage rather than proof?",
    deep_dive_content=(
        "Forward returns at overlapping quarterly horizons induce serial "
        "correlation in the cells, and ~95 quarterly observations is a small "
        "sample for correlation inference. Treat the heatmap as descriptive "
        "triage; the formal tests below carry the inferential weight."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] The tradeable-horizon cells are weak, and the "
        "few that stand out are slow regime-state associations — consistent "
        "with a lagging labor-cost gauge, not a forecaster of equity "
        "returns."
    ),
    key_message=(
        "At every tradeable quarterly horizon the raw association between "
        "wage growth and future stock returns is weak."
    ),
)


CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "For a quarterly-rebalanced strategy the decision is: how stale "
        "should the signal be allowed to get before we trade on it? This "
        "block computes Pearson correlations between each ECI signal lagged "
        "L = 0…8 QUARTERS and the SPY 1-quarter forward return. **Caveat for "
        "this pair:** the causality tests find the information flowing the "
        "OTHER way (SPY→ECI), so this lead view is expected to show little "
        "genuine predictive content at any lead — honest reporting requires "
        "us to show that, not hide it."
    ),
    question=(
        "Does lagging the wage signal by any number of quarters recover real "
        "predictive content for SPY — or does the lagging character mean no "
        "lead works?"
    ),
    how_to_read=(
        "Rows are ECI signal variants; columns are signal lead in QUARTERS "
        "(L0 = contemporaneous, L8 = two years ago). Forward horizon fixed "
        "at 1 quarter. Cell shading is Pearson r against `spy_fwd_1q`."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "[PLACEHOLDER — RAY] Pearson correlations between **signal lagged L "
        "quarters** and **SPY 1-quarter forward return**. Cells are small at "
        "every lead (|r| < 0.2 throughout); short leads tend mildly "
        "negative, long leads mildly positive — weak and unstable, the "
        "signature of a lagging series with no reliable predictive lead."
    ),
    observation=(
        "Reading across the rows, correlations are small everywhere "
        "(|r| < 0.2; none starred). The traded signal "
        "`eci_total_comp_yoy_zscore_20q` is slightly negative at short "
        "leads (L1 −0.093), drifts positive with distance, and peaks at L8 "
        "(r = 0.177) with the published L6 at r = 0.108 — weak, and the "
        "sign flip across the row is itself a fragility warning. **There is "
        "no lead at which wage growth cleanly predicts next-quarter SPY.**"
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] This is an **honest near-null result**, and "
        "stating it is the point. **In plain English:** wage growth follows "
        "the economy and the market rather than leading them, so you cannot "
        "reliably trade SPY by lagging the wage signal. The strategy on the "
        "next page rides a short-window descriptive regularity, and the "
        "lead view makes that limitation explicit."
    ),
    key_message=(
        "No lead works cleanly: the traded 20-quarter z-score is weak and "
        "sign-unstable across L = 0…8 quarters. This corroborates the "
        "lagging verdict — wages respond to the cycle, they do not lead SPY."
    ),
)


LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This block sweeps the QUARTERLY lead grid L = 1…8 and plots the "
        "best OOS Sharpe at each lead against all valid combos; the "
        "reference line is SPY buy-and-hold (Sharpe 0.80, √4 quarterly "
        "annualization). Read it alongside the lagging verdict: any Sharpe "
        "here comes from a 25-quarter descriptive regularity, not from "
        "forward causality."
    ),
    question=(
        "Where does the traded 6-quarter (~18-month) lead sit on the sweep — "
        "and is its Sharpe a robust ridge or a fragile artefact of a small "
        "quarterly sample with the causality running backwards?"
    ),
    how_to_read=(
        "[[GH#13 FRAMING SLOT — RAY]] [PLACEHOLDER — RAY, honest framing] "
        "Bars: max OOS Sharpe at each quarterly lead (L1..L8). Strip/cloud: "
        "valid combinations at that lead. A tall thin spike is a single "
        "combo; a flat-but-wide cloud is a more robust regime.\n\n"
        "How to read the published winner against this sweep: the winner's "
        "own signal, traced across leads, peaks at its published L6 "
        "quarters (Sharpe 1.60) — but every point on that curve is "
        "search-conditioned (each lead's value is the best the search found "
        "at that lead, so the whole curve inherits selection bias). At "
        "short leads the winner's curve is NEGATIVE (L1 −0.31, L2 −0.51, "
        "L3 −0.26), turning positive only from L5 (0.87) to the L6 peak, "
        "then fading (L7 1.31, L8 0.75). A rule that only works when the "
        "signal is a year-and-a-half old, on a lagging indicator, is a "
        "pattern to be suspicious of — not evidence of a forecasting "
        "mechanism."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "[PLACEHOLDER — RAY] Best OOS Sharpe per quarterly lead (bars) with "
        "the full distribution. The published winner sits at L6 quarters "
        "(1.60, ≈18 months); short leads are negative for the winner's own "
        "signal family. On a 25-quarter window with the causality running "
        "SPY→ECI, read any Sharpe here as search-conditioned and "
        "descriptive."
    ),
    observation=(
        "The published winner (`yoy_zscore_20q / T1_fixed_p75 / "
        "P3_long_short` pro, L6 quarters, OOS Sharpe 1.60) is the grid "
        "maximum; the winner's own lead-curve peaks at the published L6 "
        "(no staleness). The curve's shape is the caution: negative at "
        "L1–L3, a steep rise into L6, decay after — combined with the "
        "lead-correlation near-null, this reads as a small-sample "
        "descriptive regularity, not a stable predictive ridge."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] The honest summary: on 25 quarterly "
        "observations, with the causality tests pointing the other way and "
        "short leads scoring negative, the traded L6q Sharpe should be read "
        "as riding a search-conditioned, short-window pattern — weight it "
        "accordingly. Honesty over polish."
    ),
    key_message=(
        "The published L6-quarter winner (1.60) tops a sweep whose every "
        "point is search-conditioned; the same signal is NEGATIVE at short "
        "leads. On a 25-quarter window with reverse causality, treat the "
        "edge as descriptive, not predictive."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality (Toda-Yamamoto)",
    method_theory=(
        "Granger causality (a statistical test of whether one series helps "
        "forecast another beyond the other's own history), in the "
        "Toda-Yamamoto form that stays valid even if the series' trends are "
        "imperfectly removed. Run on quarterly data, lags 1–4 quarters, in "
        "both directions."
    ),
    question="Who moves first — wage growth or the stock market?",
    how_to_read=(
        "Bars show the test statistic at each lag from 1 to 4 QUARTERS, one "
        "panel per direction; bars clearing the dashed significance line "
        "indicate forecasting power at that lag."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "[PLACEHOLDER — RAY] What this shows: Granger F-statistics by "
        "quarterly lag, both directions, with the 5% critical line. The "
        "ECI → SPY panel clears the line at NO lag; the SPY → ECI panel "
        "clears it at EVERY lag — the causality runs from the market to "
        "wages."
    ),
    observation=(
        "In the wage-growth → SPY direction, no bar at any of the 4 "
        "quarterly lags comes close to significance (smallest p-value "
        "0.50). In the SPY → wage-growth direction, EVERY lag is "
        "significant (p = 0.0135, 0.0132, 0.0037, 0.0029 at lags 1–4). The "
        "asymmetry is total."
    ),
    deep_dive_title="Why Toda-Yamamoto instead of plain Granger?",
    deep_dive_content=(
        "Plain Granger tests can produce spurious results when series have "
        "unit roots or borderline stationarity; Toda-Yamamoto augments the "
        "model with extra lags so the statistic keeps its standard "
        "distribution regardless. We run it on the stationary year-over-"
        "year transform. The finding also makes economic sense: equity "
        "prices embed expectations of the labor cycle, while compensation "
        "adjusts through annual reviews and renegotiations — with a lag."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] This is the cleanest reverse-causality result "
        "in the catalog: the market forecasts wages, wages do not forecast "
        "the market. It is exactly the fingerprint of a LAGGING indicator — "
        "and it is the headline finding of this pair."
    ),
    key_message=(
        "The stock market Granger-causes wage growth at every tested "
        "quarterly lag; wage growth Granger-causes the market at none. "
        "Wages follow equities."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "A pre-whitened Cross-Correlation Function (CCF) — correlation "
        "between the two series at every quarterly offset from −8 to +8, "
        "after filtering each series' own autocorrelation so trends cannot "
        "masquerade as lead-lag structure."
    ),
    question=(
        "At which specific quarterly offsets, if any, do the two series "
        "echo each other?"
    ),
    how_to_read=(
        "The X-axis is the offset in QUARTERS — negative offsets mean wage "
        "growth moves before stocks, positive offsets mean stocks move "
        "before wages. Bars outside the dashed band are significant at 95% "
        "confidence."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "[PLACEHOLDER — RAY] What this shows: pre-whitened cross-"
        "correlation at 17 quarterly offsets with 95% confidence bands. The "
        "single significant bar is at offset 0 (r = −0.251) — a "
        "contemporaneous, negative echo. Nothing is significant on either "
        "lead side."
    ),
    observation=(
        "Of 17 offsets, exactly one bar clears the band: offset 0 "
        "(r = −0.251) — contemporaneous, not a lead in either direction. No "
        "wages-lead offset and no stocks-lead offset is individually "
        "significant after pre-whitening."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] After stripping each series' own memory, "
        "there is no lead-lag echo at all — only a same-quarter negative "
        "co-movement. Combined with the Granger result (which pools lags "
        "and finds SPY→ECI), the picture is: the market's influence on "
        "wages is spread over several quarters, while wages carry no "
        "forward information about the market at any single offset."
    ),
    key_message=(
        "Across 17 quarterly offsets there is no window in which wage "
        "growth foreshadows stock returns; the only significant echo is "
        "contemporaneous."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections (a horizon-by-horizon regression technique that "
        "traces how one variable responds after a movement in another), "
        "with HAC standard errors robust to overlapping quarterly horizons."
    ),
    question=(
        "If wage growth jumps today, where is the stock market 1, 2, and 4 "
        "quarters later?"
    ),
    how_to_read=(
        "Each panel plots the estimated response (line) with its confidence "
        "band (shading) across quarterly horizons; a band that straddles "
        "zero means no detectable effect."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "[PLACEHOLDER — RAY] What this shows: impulse-response panels, "
        "forward and reverse. In the wage-growth → SPY panel the confidence "
        "band straddles zero at every horizon (1, 2, and 4 quarters); the "
        "reverse panel is also insignificant horizon-by-horizon."
    ),
    observation=(
        "In the wage-growth → SPY panel the band straddles zero at 1, 2, "
        "and 4 quarters (p-values 0.25, 0.31, 0.54; point estimates mildly "
        "negative). The reverse direction is not significant at any single "
        "horizon either (the Granger result pools lags jointly, which is "
        "where the SPY → ECI power shows up)."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] At the horizons a quarterly strategy actually "
        "trades, a wage-growth surprise tells you nothing statistically "
        "useful about where stocks will be. Nothing here rescues a "
        "forward-looking reading of the indicator."
    ),
    key_message=(
        "A jump in wage growth carries no statistically detectable "
        "information about stock returns over the following year."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy — a model-free measure of directed information "
        "flow that can detect *non-linear* relationships ordinary "
        "correlation misses (estimated on tercile-binned quarterly data "
        "with 500 permutations; low power at ~96 observations)."
    ),
    question=(
        "Could wage growth predict stocks in some curvy, non-linear way the "
        "linear tests can't see?"
    ),
    how_to_read=(
        "Two bars — one per direction; the annotation shows each bar's "
        "permutation p-value. A small p-value (under 0.05) would indicate "
        "genuine information flow."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "[PLACEHOLDER — RAY] What this shows: bidirectional transfer "
        "entropy with permutation p-values. Wages → SPY: p = 0.17 (not "
        "significant). SPY → wages: p = 0.054 (borderline) — once again the "
        "nearly-significant direction is the REVERSE one."
    ),
    observation=(
        "Wage growth → SPY: p = 0.17 — clearly insignificant. SPY → wage "
        "growth: p = 0.054 — borderline, just above the 5% bar, and on the "
        "same side as the significant Granger result."
    ),
    deep_dive_title="Does the borderline reverse-direction reading matter?",
    deep_dive_content=(
        "On ~96 tercile-binned quarterly observations transfer entropy has "
        "low power and noisy permutation p-values, so we treat it as a "
        "directional check only (per evidence_status.json). Read this way, "
        "it is corroboration: the direction that approaches significance "
        "(SPY → wages, p = 0.054) is the one the Granger test finds, while "
        "the forecasting direction the pair was designed to test (wages → "
        "SPY, p = 0.17) shows nothing."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] No non-linear channel rescues the indicator: "
        "the forward direction is flatly insignificant, and what weak "
        "information flow exists points from the market to wages."
    ),
    key_message=(
        "There is no non-linear escape hatch — even model-free information "
        "flow runs (weakly) from stocks to wages, not the other way."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression — instead of asking how wage growth affects "
        "the *average* future return, it asks how it affects the *worst* "
        "and *best* outcomes (the tails), where risk signals usually earn "
        "their keep."
    ),
    question=(
        "Does wage growth at least predict tail risk — the really bad "
        "quarters — even if it can't predict the average?"
    ),
    how_to_read=(
        "The X-axis runs across outcome percentiles (5th = worst quarters, "
        "95th = best); the line is the estimated effect at each percentile "
        "with its confidence band. A risk signal typically shows a "
        "significant effect at the left tail."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "[PLACEHOLDER — RAY] What this shows: quantile-regression "
        "coefficient by percentile with confidence band. The band straddles "
        "zero at every percentile — no tail-risk channel (the closest is "
        "the 25th percentile at p = 0.075, still short of 5%)."
    ),
    observation=(
        "The confidence band straddles zero at every percentile from the "
        "5th to the 95th (all p-values ≥ 0.075; most far higher). The "
        "mildly negative point estimates in the lower-middle of the "
        "distribution never reach significance."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] Many indicators fail at the mean but work at "
        "the left tail. This one fails at both — wage growth does not flag "
        "elevated crash risk either."
    ),
    key_message=(
        "Wage growth predicts neither average stock returns nor tail risk."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Context (HMM and Quartiles)",
    method_theory=(
        "A two-state Hidden Markov Model (HMM — a statistical model that "
        "infers unobserved \"high\" vs \"low\" wage-inflation regimes from "
        "the data's behavior) fitted to the ECI series, plus a simple sort "
        "of history into quartiles of concurrent wage growth with SPY "
        "performance in each."
    ),
    question=(
        "Even without prediction, do states of the wage cycle coincide with "
        "systematically different stock-market environments?"
    ),
    how_to_read=(
        "The HMM panel shades periods by inferred regime probability over "
        "time; the quartile chart on the Story page shows concurrent SPY "
        "Sharpe/return in four bars, sorted from slowest (Q1) to fastest "
        "(Q4) wage growth."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "[PLACEHOLDER — RAY] What this shows: HMM-inferred wage-inflation "
        "regime probability over time, NBER recessions shaded. The "
        "high-wage-inflation state covers ~47% of the sample (notably the "
        "2021–23 surge); SPY returns have been better in the LOW-wage-"
        "inflation state."
    ),
    observation=(
        "The HMM separates a low-wage-inflation state (mean YoY ≈ 2.2%, "
        "~53% of quarters) from a high state (≈ 3.7%, ~47%). Concurrent SPY "
        "performance is better in the low state, and the quartile sort "
        "agrees: Q1 (slowest wage growth) Sharpe 1.17 vs Q4 0.67 and Q3 "
        "−0.15 — a mildly countercyclical CONCURRENT pattern. Note the "
        "tension: the tournament winner trades the OPPOSITE (procyclical) "
        "orientation at a 6-quarter lag on a different transform."
    ),
    deep_dive_title="How stable is the relationship over time?",
    deep_dive_content=(
        "Not stable. The rolling 20-quarter correlation flips sign "
        "repeatedly (sign-stability 0.42, verdict `sign_unstable` in "
        "`structural_break_eci_total_comp_spy.json`), and the Quandt-"
        "Andrews test FLAGS a structural break at 2009-Q2 (sup-F 6.97, "
        "bootstrap p = 0.027). Cross-period results should be read with "
        "caution — the concurrent pattern above is regime-dependent, and "
        "the winner's 20-quarter z-score signal is itself flagged "
        "regime-contaminated (KPSS reject)."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] The constructive reading of a lagging series: "
        "wage-inflation states describe distinct macro environments — but "
        "here even the concurrent pattern is sign-unstable with a flagged "
        "2009 break, and it points the opposite way from the strategy the "
        "search picked. Descriptive, conditional, and fragile."
    ),
    key_message=(
        "Wage-inflation states have coincided with different equity "
        "environments (slow wage growth = better returns), but the "
        "relationship is sign-unstable with a flagged structural break — "
        "and the strategy search latched onto the opposite orientation."
    ),
)


TOURNAMENT_DIST_BLOCK = dict(
    chart_status="ready",
    method_name="Search Distribution",
    method_theory=(
        "The distribution of out-of-sample Sharpe ratios across all 1,268 "
        "valid strategy combinations in the quarterly tournament — the "
        "context that shows how far the published winner sits into the "
        "right tail of its own search."
    ),
    question=(
        "Is the winner's Sharpe typical of what this indicator supports — "
        "or the extreme right tail of a search over thousands of variants?"
    ),
    how_to_read=(
        "Histogram of OOS Sharpe across valid combos; vertical markers show "
        "the median valid combo (0.72), buy-and-hold (0.80), and the "
        "published winner (1.60). All figures use quarterly √4 "
        "annualization on the 25-quarter OOS window."
    ),
    chart_name=TOURNAMENT_DIST_CHART_NAME,
    chart_caption=(
        "[PLACEHOLDER — RAY] Distribution of OOS Sharpe across 1,268 valid "
        "combos with median (0.72), buy-and-hold (0.80) and the winner "
        "(1.60) marked — the winner is the right tail of a search, not an "
        "out-of-sample forecast."
    ),
    observation=(
        "The median valid combination (0.72) UNDERPERFORMS buy-and-hold "
        "(0.80): the typical rule built on this indicator subtracts value. "
        "The published winner (1.60) is the extreme of the distribution, "
        "and its bootstrap p-value against resampled buy-and-hold is 0.12 — "
        "not significant at 5%."
    ),
    interpretation=(
        "[PLACEHOLDER — RAY] When the median strategy loses to buy-and-hold "
        "and only the search maximum looks good, the correct prior is that "
        "the maximum is selection effect. This is the best-of-N disclosure "
        "rendered as a picture."
    ),
    key_message=(
        "The typical ECI-based rule underperforms buy-and-hold; the "
        "published winner is the right tail of a 1,268-combination search "
        "(bootstrap p = 0.12, n.s.)."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": (
        "The tests point one way: the market leads, wages follow"
    ),
    "overview": (
        "*One question, attacked several independent ways: does wage-"
        "inflation momentum carry information about future S&P 500 (SPY) "
        "returns — or does the market move first? Methods that agree from "
        "different angles are far more convincing than any single test. "
        "Here they converge on a directional answer: SPY predicts ECI at "
        "every tested quarterly lag; ECI predicts SPY at none.*\n\n"
        "All statistics computed on QUARTERLY data, analytical sample "
        "2001-Q1 → 2026-Q1 (~101 quarters), from "
        "`results/eci_total_comp_spy/core_models_20260706/`."
    ),
    "plain_english": (
        "This section shows the statistical evidence on whether wage growth "
        "predicts the stock market. The lead-lag tests — correlation, "
        "Granger causality, pre-whitened cross-correlation, local "
        "projections, and transfer entropy — converge on a reversal: the "
        "S&P 500 (SPY) helps predict wage growth one to four quarters "
        "ahead, while wage growth predicts the market at no tested lag. "
        "Wages are a lagging indicator. The concurrent regularity that "
        "remains (slow wage growth coinciding with better equity "
        "conditions) is descriptive, sign-unstable, and — notably — points "
        "the opposite way from the procyclical rule the strategy search on "
        "the next page latched onto."
    ),
    # Row counts VERIFIED by reading each file at authoring time (2026-07-06);
    # counts exclude the header row.
    "downloads": [
        {"label": "Granger causality (Toda-Yamamoto), both directions × 4 quarterly lags (8 rows)",
         "path": "results/eci_total_comp_spy/core_models_20260706/granger_causality.csv"},
        {"label": "Granger F-statistics by lag, ECI → SPY (4 rows)",
         "path": "results/eci_total_comp_spy/granger_by_lag.csv"},
        {"label": "Correlation battery, signal × horizon × metric (120 rows)",
         "path": "results/eci_total_comp_spy/core_models_20260706/correlations.csv"},
        {"label": "Pre-whitened CCF, quarterly offsets −8..+8 (17 rows)",
         "path": "results/eci_total_comp_spy/core_models_20260706/ccf_prewhitened.csv"},
        {"label": "Local projections, forward + reverse × 3 quarterly horizons (6 rows)",
         "path": "results/eci_total_comp_spy/core_models_20260706/local_projections.csv"},
        {"label": "Transfer entropy, both directions (2 rows)",
         "path": "results/eci_total_comp_spy/core_models_20260706/transfer_entropy.csv"},
        {"label": "Quantile regression, 7 quantiles (7 rows)",
         "path": "results/eci_total_comp_spy/core_models_20260706/quantile_regression.csv"},
        {"label": "Lead-correlation grid, 8 transforms × leads L0..L8 quarters (8 rows)",
         "path": "results/eci_total_comp_spy/lead_correlation_20260706.csv"},
        {"label": "Regime quartile returns, Q1–Q4 (4 rows)",
         "path": "results/eci_total_comp_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe, episodes (4 rows)",
         "path": "results/eci_total_comp_spy/subperiod_sharpe.csv"},
        {"label": "Rolling 20-quarter correlation (64 rows)",
         "path": "results/eci_total_comp_spy/rolling_correlation_eci_total_comp_spy.csv"},
    ],
    "level1": [CORRELATION_BLOCK, CORRELATION_LEAD_VIEW_BLOCK,
               LEAD_TOURNAMENT_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Lead Analysis", "Lead Tournament",
                      "Granger Causality", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, TRANSFER_ENTROPY_BLOCK,
               QUANTILE_BLOCK, REGIME_BLOCK, TOURNAMENT_DIST_BLOCK],
    "level2_labels": ["Local Projections", "Transfer Entropy",
                      "Quantile Regression", "Regime Context (HMM)",
                      "Search Distribution"],
    "tournament_intro": (
        "The statistical tests above ask whether the indicator *predicts* — "
        "and answer no (the causality runs the other way). The tournament "
        "asks a more pragmatic question: across every reasonable QUARTERLY "
        "trading rule you could build from this series, does *any* of them "
        "beat simply holding the S&P 500 (SPY)?\n\n"
        "We tested a grid of **2,336 strategy combinations** — 10 signal "
        "transforms × 8 threshold schemes × 4 strategy families × quarterly "
        "leads L1..L8 — of which **1,268 passed validity filters** (the "
        "buy-and-hold benchmark row is excluded from this count). The "
        "median valid combination scored an OOS Sharpe of 0.72, BELOW "
        "buy-and-hold's 0.80. The headline rule on the Strategy page is the "
        "search maximum (1.60) on a 25-QUARTER out-of-sample window, with "
        "bootstrap p = 0.12. In plain English: on a small quarterly sample, "
        "with the causality running backwards, the winner is a candidate "
        "found in search — not a validated edge."
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is lagging — the market "
        "moves first and wages follow. What remains is the pragmatic "
        "question the tournament answered: the next page shows the one "
        "candidate rule the search surfaced, with every fragility flag "
        "attached."
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = (
        "The Strategy: A Long/Short Overlay Found on 25 Quarters"
    )
    PAGE_SUBTITLE = (
        "— the search maximum on a LAGGING indicator with the causality "
        "running the other way: a 25-quarter (quarterly) candidate, "
        "bootstrap p = 0.12, in-sample Sharpe NEGATIVE. No hold-out test "
        "has been run yet."
    )

    # [PLACEHOLDER — RAY]
    PLAIN_ENGLISH = (
        "The best rule from a 2,336-combination quarterly search: hold the "
        "S&P 500 (SPY) when the ECI wage-growth z-score — viewed with a "
        "6-QUARTER (~18-month) delay — sits above its fixed 75th-percentile "
        "threshold (strong wage growth = risk-on), and hold a SHORT SPY "
        "position when it sits below. In the 25-quarter search window "
        "(2020–2026) it scored a Sharpe ratio of 1.60 versus 0.80 for "
        "buy-and-hold, with a −4.3% maximum drawdown versus −23.9%. But the "
        "window is 25 quarterly observations, the causality tests say the "
        "market leads wages (not the reverse), the same rule LOST money on "
        "a risk-adjusted basis in-sample (Sharpe −0.23), and it fails the "
        "standard significance test (bootstrap p = 0.12). Read it as a "
        "candidate overlay found by search — its final exam on untouched "
        "data has not been run."
    )

    SIGNAL_RULE_MD = """
**Rule:** Hold the S&P 500 (SPY) **when the 6-QUARTER-lagged ECI wage-growth signal (`eci_total_comp_yoy_zscore_20q`, the year-over-year total-compensation growth rate expressed as a z-score against its own trailing 20-quarter window) is above its fixed threshold of 0.259 (the in-sample 75th percentile). When it is below, hold a SHORT SPY position.** This is a **procyclical** orientation: strong/accelerating wage growth = risk-on, weak wage growth = short. It **contradicts the countercyclical wage-inflation prior** the pair was designed to test (`direction_consistent: false` in `interpretation_metadata.json`) — flagged, not smoothed over. (Family: Long/Short P3; signal `yoy_zscore_20q`, fixed threshold T1_fixed_p75 = 0.259, lead L6 QUARTERS ≈ 18 months, no rolling lookback (LB_NA) — per `winner_summary.json`; `direction: procyclical`, confirmed by every row of the broker-style trade log.)

If-then form (evaluated once per quarter):
- **IF** the 6-quarter-old wage-growth z-score is above 0.259 → **LONG SPY (100% invested)**.
- **ELSE** → **SHORT SPY (−100%)**.

Search-phase results (2020-03-31 → 2026-03-31, 25 QUARTERS — **small sample, no hold-out test yet**; Sharpe annualized by √4): OOS Sharpe 1.60 vs 0.80 buy-and-hold; annualized return 24.1% vs 14.5%; maximum drawdown −4.3% vs −23.9%; 3 trades in the OOS window (turnover 0.48/yr); quarterly win rate 88%.

**Read this as a candidate, not a validated edge.** The window is 25 quarterly observations, the indicator is empirically LAGGING (the market predicts wages, not the reverse), the same rule scored Sharpe **−0.23 in-sample**, and the result is not statistically significant (bootstrap p = 0.12). This pair's `strategy_objective` (per `interpretation_metadata.json`) is **max_sharpe**; note that as a long/SHORT rule its OOS edge came largely from being short through the 2022 bear — one episode, in one window.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
No formulas — three steps:

**What changes in the world:** employers' total compensation costs — wages plus benefits — accelerate or decelerate with the labor cycle. The BLS's Employment Cost Index measures that growth each QUARTER (released ~1 month after quarter end).

**What the signal measures:** each quarter, the rule takes the year-over-year ECI growth rate and asks how unusual it is against its own trailing 20-quarter (~5-year) history, expressed as a z-score — as that reading stood **six quarters (~18 months) ago** (the delay is not a publication-lag necessity; it is the lead the tournament scored best, which on a lagging indicator is itself a caution). It then compares that stale reading to a fixed threshold (0.259, the in-sample 75th percentile).

**What decision it drives:** above the threshold (wage growth running unusually hot 18 months ago) → be LONG the market; below it → be SHORT. Because the causality tests find the market leads wages, this is best understood as a *state* description that happened to sort the 2020–2026 window well — not a forecast of where stocks are going.
"""

    # [PLACEHOLDER — RAY]
    MANUAL_USE_MD = (
        "First, the framing: what follows describes how the backtested rule "
        "works so you can replicate and audit it — it is **not** a "
        "recommendation to trade it. This rule is a small-sample search-"
        "phase candidate (best of 1,268 valid; 25-QUARTER OOS; no hold-out "
        "test yet; bootstrap p = 0.12, not significant at 5%; in-sample "
        "Sharpe −0.23; empirically LAGGING indicator). With that "
        "understood, the quarterly routine — no code required — is:\n\n"
        "1. **Pull the wage series** — FRED series `ECIALLCIV` (Employment "
        "Cost Index: Total compensation: All Civilian, SA; published ~1 "
        "month after each quarter ends).\n"
        "2. **Compute year-over-year growth** — the % change of the index "
        "versus the same quarter one year earlier.\n"
        "3. **Standardize it** — express that YoY growth as a z-score "
        "against its own trailing 20-quarter (~5-year) mean and standard "
        "deviation.\n"
        "4. **Apply the 6-quarter delay** — the reading the rule acts on "
        "this quarter is the z-score from six quarters (~18 months) ago.\n"
        "5. **Compare to the fixed threshold** — is that delayed z-score "
        "above 0.259 (the in-sample 75th percentile)? See "
        "`winner_trade_log.csv` for the full signal/threshold path.\n"
        "6. **Take the position** — above the threshold → LONG SPY (100%); "
        "below → SHORT SPY (−100%). Re-evaluate once a QUARTER.\n\n"
        "Remember the warning labels: 25-quarter window, lagging indicator "
        "(the causality runs the other way), negative in-sample Sharpe, "
        "not statistically significant — and a short leg that has only "
        "been \"tested\" by one bear market (2022)."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    WALK_FORWARD_CAPTION = (
        "What this shows: rolling 8-quarter (2-year) annualized Sharpe over "
        "the OOS window versus the reported headline 1.60. With only 18 "
        "rolling points on 25 quarters, the path is noisy by construction — "
        "read it as a stability sniff-test, not confirmation."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: all 2,336 tournament combinations by annual "
        "turnover vs OOS Sharpe (quarterly √4 annualization); the star "
        "marks the published winner (1.60), the diamond buy-and-hold "
        "(0.80). Search-conditioned on a 25-quarter window, bootstrap "
        "p = 0.12 — the winner is the right tail of its own search, and "
        "the median valid combo (0.72) sits BELOW buy-and-hold."
    )

    CAVEATS_MD = """
**Why we do not call this a validated edge** — flags, none softened (all from `winner_summary.json`, `evidence_status.json`, `structural_break_eci_total_comp_spy.json`, and `tournament_validation_20260706/bootstrap.csv`):

1. **Small quarterly out-of-sample sample.** The test window is **25 QUARTERS** (2020-03-31 → 2026-03-31). That is a handful of independent quarterly observations — a caveat STRONGER than any monthly pair to date. Any winner here is FOUND-IN-SEARCH by construction.
2. **The causality runs backwards.** Toda-Yamamoto Granger finds SPY → ECI significant at ALL tested quarterly lags and ECI → SPY at NONE; the pre-whitened CCF finds no lead on either side. The indicator is LAGGING — the rule is reading an old echo of a cycle the market already priced.
3. **Not statistically significant.** Bootstrap p = **0.12** versus resampled buy-and-hold — above the 5% threshold.
4. **In-sample the rule LOST.** IS Sharpe **−0.23** vs OOS 1.60. An out-of-sample figure that dwarfs a negative in-sample figure on a small window is the signature of a favorable draw, not a stable property.
5. **Direction contradicts the prior.** The pair was designed around a countercyclical wage-inflation hypothesis; the winner is PROCYCLICAL (`direction_consistent: false`), and the concurrent quartile evidence points the countercyclical way — the search picked the orientation that fit the window.
6. **Regime-contaminated signal.** The 20-quarter z-score transform fails the KPSS stationarity check (winner stationarity class `regime_contaminated`); the 2021–23 wage surge dominates its recent distribution.
7. **Structural break flagged; relationship sign-unstable.** Quandt-Andrews FLAGS a break at 2009-Q2 (sup-F 6.97, bootstrap p = 0.027) and rolling-correlation sign-stability is only 0.42 (`sign_unstable`).
8. **Durability: conditionally durable on ONE episode.** Of the standard stress episodes, only COVID falls inside usable history with data (ann. Sharpe 0.63); dot-com and GFC are `insufficient_data` for the strategy. The short leg has met exactly one bear market (2022).

**What this means:** the honest label is a **found-in-search CANDIDATE on a lagging indicator** — "the best rule we found by searching a small quarterly window, not a rule that has passed an independent test." The prescribed next step is a final exam: freeze this rule and test it once on an untouched window. Given the flags above and the reverse-causality verdict, expectations should be calibrated LOW.

**Further caveats:**

- **The edge is concentrated.** Only 3 trades occur in the OOS window; the headline outperformance rests heavily on being short through the 2022 bear and long through the recoveries — one regime sequence.
- **Quarterly units throughout.** Sharpe ratios use √4 annualization; with 25 observations the sampling error on a quarterly Sharpe is large even before selection effects.
- **Costs.** Returns are gross of costs; at 5 bps per trade and 0.48 trades/yr the haircut is negligible (see `tournament_validation_20260706/transaction_costs.csv`) — cost drag is not this pair's problem; the small sample and reverse causality are.
"""

    # [PLACEHOLDER — RAY]
    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** on **2022-03-31** the "
        "broker-style log records a SELL — the 6-quarter-lagged wage-growth "
        "z-score (−0.275) sat below the fixed threshold (0.259), flipping "
        "the position from 100% long to −100% SHORT just as the 2022 bear "
        "unfolded. The matching BUY appears on **2022-12-31**, when the "
        "delayed reading (0.983, reflecting the wage surge ~18 months "
        "earlier) rose back above the threshold and the strategy returned "
        "to 100% long near the market trough. Both rows are in the "
        "broker-style CSV — and both illustrate the point: the rule was "
        "reading a stale wage echo that happened to line up with the "
        "2022–23 regime sequence."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2022-03-31",
        "side": "SELL",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": (
            "lagged yoy_zscore_20q −0.275 vs fixed threshold 0.259 — "
            "position 100% → −100% (short)"
        ),
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED — BLS | `ECIALLCIV` (Employment Cost Index: Total compensation: All Civilian, SA, index Dec 2005 = 100) | **Quarterly** (2001-Q1 → 2026-Q1, ~101 quarters) |
| Target | Yahoo Finance | SPY (SPDR S&P 500 ETF, dividend-adjusted) | Quarterly (quarter-end) |

Dataset produced by Dana for the feat260705_eci_spy wave — the fleet's **first QUARTERLY pair**: the series is native quarterly (quarter-end, QE-DEC), so the monthly template was adapted, not copied (20-quarter z-score windows instead of 60-month; quarterly forward returns `spy_fwd_1q/2q/4q`; lead grid in QUARTERS). The source is seasonally adjusted, so no seasonal-contamination restriction applies (unlike the NSA Cass Freight pair).
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw ECI level is non-stationary, so analysis runs on quarterly "
    "transforms: quarter-over-quarter, 2-quarter, and year-over-year % "
    "growth; % deviation from an 8-quarter (~2-year) moving average; "
    "20-quarter (~5-year) rolling z-scores of level and YoY growth "
    "(`eci_total_comp_yoy_zscore_20q` — the winning signal); growth "
    "acceleration; and HMM/Markov regime states. Growth-family transforms "
    "test borderline-persistent, and the 20-quarter z-scores are flagged "
    "**regime-contaminated** (KPSS reject — the 2021–23 wage surge "
    "dominates their recent distribution); the winner carries that flag. "
    "The BLS publication lag (~1 month after quarter end) makes a "
    "1-QUARTER signal delay the real-time floor; the tradeable lead grid "
    "therefore runs L1..L8 QUARTERS (L0 appears only as a non-tradable "
    "diagnostic)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation battery (Pearson/Spearman/distance) | Any raw association at any quarterly horizon? | Cheap triage before formal tests |
| Toda-Yamamoto Granger causality (lags 1–4q, both directions) | Who forecasts whom? | Robust to unit-root ambiguity; the decisive test for a suspected-lagging indicator |
| Pre-whitened CCF (offsets −8..+8 quarters) | At which quarterly offsets do the series echo? | Filters autocorrelation that fakes lead-lag patterns |
| Local projections (HAC errors) | Where is SPY h quarters after a wage-growth move? | Horizon-by-horizon honesty; robust to overlapping returns |
| Transfer entropy (500 permutations) | Any non-linear information flow? | Model-free check the linear tests can't provide (low power at ~96 obs — directional check only) |
| Quantile regression | Does the signal at least predict tail risk? | Cyclical signals sometimes work at the left tail only |
| Two-state HMM + quartile sorts | Do wage-inflation states coincide with distinct market environments? | The descriptive/regime reading appropriate to a lagging series |
| Structural break (Quandt-Andrews sup-F, bootstrap) + rolling correlation | Did the relationship change mid-sample? | It did: break flagged at 2009-Q2 (p = 0.027), sign-stability 0.42 |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: 10 signals (quarterly data transforms + HMM/Markov regime states) × 8 threshold schemes (fixed percentiles, rolling percentiles, z-score bands, zero-line) × 4 strategy families × QUARTERLY leads {1…8} = **2,336 combinations** plus a buy-and-hold benchmark row (valid=False per ECON-T4). Validity filters → **1,268 valid**; median valid OOS Sharpe 0.7179 (below buy-and-hold's 0.80). Because the source is seasonally adjusted, no seasonal-cleanliness restriction applies; the objective is max OOS Sharpe (√4 QUARTERLY annualization) over the full valid population, ties resolved by the ECON-T3 cascade (2 combos tied at step 1; resolved at step 5 — see `tournament_tie_note.md`). Out-of-sample split per policy `v1_max36_25pct_cap120` applied in native quarterly units: in-sample through 2019-Q4 (75 quarters), out-of-sample 2020-03-31 → 2026-03-31 (**25 QUARTERS** — a small sample; any winner is found-in-search). Winner: `yoy_zscore_20q / T1_fixed_p75 / P3_long_short` (procyclical), lead L6 quarters; OOS Sharpe 1.5952, IS Sharpe −0.23, bootstrap p = 0.12. All tournament CSV metrics are decimal ratios.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_eci_total_comp_spy.py` — deterministic, fixed seeds. The canonical quarterly return series for chart producers is `strategy_returns_20260706.csv`; its Sharpe/drawdown/return reconcile with `winner_summary.json`. Stationarity tests were produced by the data stage and confirmed, not re-run, by the econometrics stage.
"""

_REFERENCES_MD = """
1. U.S. Bureau of Labor Statistics, *Employment Cost Index* — methodology (fixed-weight occupational mix; total compensation = wages + benefits).
2. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes." *Journal of Econometrics*, 66(1–2), 225–250.
3. Jordà, Ò. (2005). "Estimation and inference of impulse responses by local projections." *American Economic Review*, 95(1), 161–182.
4. Stock, J. H. & Watson, M. W. (1999). "Business cycle fluctuations in US macroeconomic time series." *Handbook of Macroeconomics* — leading vs lagging indicator classification (labor costs classically lag).
5. Andrews, D. W. K. (1993). "Tests for parameter instability and structural change with unknown change point." *Econometrica*, 61(4), 821–856.
6. Simonsohn, U., Simmons, J. P. & Nelson, L. D. (2020). "Specification curve analysis." *Nature Human Behaviour*, 4, 1208–1214 — basis for the best-of-N position disclosure.
7. Bailey, D. H. & López de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality." *Journal of Portfolio Management*, 40(5), 94–107.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "QUARTERLY data (first quarterly pair); analytical sample 2001-Q1 → "
        "2026-Q1 (~101 quarters). Out-of-sample split per policy "
        "v1_max36_25pct_cap120 in native quarterly units: in-sample through "
        "2019-Q4, out-of-sample 2020-03-31 → 2026-03-31 (25 QUARTERS). "
        "Sharpe ratios use √4 annualization; leads are in quarters "
        "(winner L6q ≈ 18 months). SMALL-SAMPLE pair — the 25-quarter OOS "
        "window makes any winner found-in-search, not validated."
    ),
    plain_english=(
        "One QUARTERLY data series (the Employment Cost Index of total "
        "worker compensation, from 2001) and the S&P 500 ETF (SPY). We "
        "turned the wage index into growth and z-score transforms, ran "
        "several independent lead-lag tests (they agree — and point the "
        "other way: the market predicts wages, wages do not predict the "
        "market), then searched 2,336 quarterly trading-rule combinations "
        "on data split so rules were built on pre-2020 history and scored "
        "on 2020–2026 — just 25 quarterly observations. Every number on "
        "these pages can be reproduced by one deterministic script, and "
        "every number is labelled a candidate because the sample is small "
        "and the indicator is lagging."
    ),
)
