"""Employment Cost Index (Total Compensation) × SPY pair configuration (Rule APP-PT1).

Quarterly pair. Narrative rewritten for the 20261016 run (causal regime port + in-sample
selection, branch fix261016_hmm_port_eci_nhs). Every number below is read from the
results artifacts listed at the end of this docstring.

What changed on 2026-10-16:
  - The 20261008 winner (hmm_stress / T3_zscore_1.0 / LB12 / P1_long_cash counter / L4
    quarters, OOS Sharpe 1.41, HAC t 3.04) traded a 2-state HMM probability that was fit on
    the full sample and read with forward-backward smoothing, so each quarter's value used
    later quarters (look-ahead). It was also selected by OOS Sharpe.
  - Causal rule (scripts/_regime_causal.py): fit on in-sample rows only, forward filter.
    A traded fit needs >= 100 in-sample rows; ECI has 72 in-sample quarters, so the HMM and
    Markov-switching signals are not in the 20261016 tournament. The same superseded rule
    on a causal diagnostic HMM (72 quarters, not traded) scores OOS Sharpe 1.03 (HAC t 2.42).
  - Selection is now by in-sample Sharpe on the common IS window 2008-12-31..2019-12-31
    (45 quarters). Winner: growth_2q (eci_total_comp_pct_2q) / T1_fixed_p50 /
    P1_long_cash counter / L2 quarters. IS Sharpe 1.19 (B&H 0.79); OOS Sharpe 0.70
    (B&H 0.80), HAC t 1.33; OOS annualized return 4.3% vs 14.5%; max drawdown 0.0% vs
    −23.9%; long SPY in 3 of 25 OOS quarters, cash since 2021-Q3.

Lead-lag evidence is unchanged (same data, same code): Toda-Yamamoto Granger SPY→ECI
significant at lags 1-4 (p = 0.0135/0.0132/0.0037/0.0029), ECI→SPY at none (smallest
p = 0.5048); pre-whitened CCF significant only at offset 0 (r = −0.251).

Numbers sourced from results/eci_total_comp_spy/ (winner_summary.json, kpis.json,
evidence_status.json, oos_split_record.json, hmm_lookahead_audit_20261016.json,
legacy_oos_selection_20261016.csv, core_models_20261016/*,
structural_break_eci_total_comp_spy.json, subperiod_sharpe.csv,
tournament_results_20261016.csv, tournament_validation_20261016/*,
lead_winner_curve_20261016.csv, lead_correlation_20261016.csv,
regime_quartile_returns.csv, winner_trades_broker_style.csv).
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

    # Metrics read from winner_summary.json / granger_by_lag.csv, not hand-typed.
    HEADLINE_H2 = (
        "## The causality tests run from the stock market to wages: SPY "
        "predicts ECI wage growth at every tested quarterly lag, and ECI "
        "predicts SPY at none. The rule with the best in-sample Sharpe scores "
        "an out-of-sample Sharpe of 0.70 against 0.80 for buy-and-hold over "
        "25 quarters."
    )

    PLAIN_ENGLISH = (
        "The Employment Cost Index (ECI) measures how fast total worker "
        "compensation (wages plus benefits) is growing in the US. One "
        "hypothesis is that wage inflation warns about the stock market "
        "(wage pressure → Fed tightening → equity trouble). The tests find "
        "the reverse direction: the S&P 500 (SPY) helps predict wage growth "
        "one to four quarters ahead, while wage growth predicts the market "
        "at no tested lag. A search over 1,180 quarterly rules picked the one "
        "with the best in-sample record; over the 2020–2026 test window it "
        "earned a Sharpe ratio of 0.70 versus 0.80 for holding SPY, mostly by "
        "sitting in cash."
    )

    WHERE_THIS_FITS = (
        "This page covers a *lagging* indicator: the information flows from "
        "the market to wages. Knowing that wage growth trails equities is "
        "macro context (it is one reason the Fed watches ECI and markets "
        "move ahead of the Fed). For advance warning, the catalog's leading "
        "measures are the relevant comparison, not labor-cost data."
    )

    ONE_SENTENCE_THESIS = (
        "Wage growth (ECI total compensation) lags the stock market — SPY "
        "Granger-causes ECI at every tested quarterly lag and ECI "
        "Granger-causes SPY at none — and the in-sample-selected quarterly "
        "rule (long SPY when 2-quarter wage growth, lagged two quarters, is "
        "at or below its in-sample median; cash otherwise) has an "
        "out-of-sample Sharpe of 0.70 versus 0.80 for buy-and-hold."
    )

    KPI_CAPTION = (
        "the rule was chosen by its in-sample Sharpe (2008-12-31 → "
        "2019-12-31, 45 quarters) and every out-of-sample number is scored "
        "on 2020-03-31 → 2026-03-31 (25 quarters). Over that window the rule "
        "held SPY in 3 quarters and cash in 22. Sharpe ratios use quarterly "
        "√4 annualization."
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
        "wage growth was slow (Q1 Sharpe 1.17) than fast (Q4 0.67, Q3 "
        "−0.15). This sort is concurrent and descriptive, not a tradable "
        "lead. The selected rule has the same orientation (long when lagged "
        "wage growth is low, cash when high) at a 2-quarter lag."
    )

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

The hero chart on this page shows the clearest recent example. The wage-growth
line peaks at **5.11% year-over-year in June 2022 (2022-Q2)** — roughly
two quarters *after* the S&P 500 (SPY) had already peaked and begun its
2022 drawdown at the start of that year. Anyone waiting for the ECI to
signal trouble got the news after the bear market was well underway; anyone
watching the market got an early read on where wage growth was heading.
That single episode is the whole lagging verdict in one picture.

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
in quarters (the selected rule's L2 lead ≈ 6 months); Sharpe ratios are annualized
by √4; and the out-of-sample window is just **25 quarterly observations**
(2020-Q1 → 2026-Q1). Twenty-five data points is a small sample — smaller in
effective terms than any monthly pair to date — so every out-of-sample
number on these pages has wide sampling error.
"""

    # Three history-zoom charts exist for this pair (gfc, covid,
    # inflation_2022); dot-com is chart-skipped (z-score signals not yet
    # warm in 2000–02), as are rolling_granger / rolling_sharpe_cp.
    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": (
                "SPY peaked in late 2007 and collapsed through 2008, "
                "bottoming in early 2009 — while ECI wage growth kept "
                "decelerating long after, not reaching its trough (~1.4% "
                "YoY) until the end of 2009, quarters after equities had "
                "already turned back up. The market moved first at the top "
                "AND at the bottom; wages followed both turns with a lag of "
                "several quarters — the clearest single illustration of the "
                "lagging relationship."
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
                "The equity crash and rebound of 2020 played out within two "
                "quarters; quarterly compensation growth barely flinched — "
                "ECI YoY drifted from ~2.9% in 2020-Q1 to ~2.5% by 2020-Q3 "
                "and back — and only accelerated in 2021 as the reopening "
                "labor shortage built. A fast market shock moved far too "
                "quickly for a quarterly wage gauge to register; wages again "
                "moved after the market."
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
                "ECI YoY climbed from 2.8% in mid-2021 to its 5.11% peak in "
                "2022-Q2 — the wage-price-spiral scare feeding Fed "
                "tightening — but SPY had already peaked and begun falling "
                "at the start of 2022, two quarters before wage growth "
                "topped out. Peak wage inflation arrived near the equity "
                "trough, not before the drawdown: concurrent-to-lagging, "
                "not leading."
            ),
            "caption": (
                "Peak wage inflation coincided with the 2022 equity trough "
                "— it did not warn of the drawdown"
            ),
        },
    ]

    NARRATIVE_SECTION_2 = """
### "Lagging" — what does a timing rule on this indicator measure?

The Evidence page shows the information flowing from the market to wages.
A timing rule built on ECI therefore does not forecast through a wage →
equity channel; it can only sort periods by an old reading of wage growth.

### What the search selected

We scored **1,180 quarterly rule combinations** (8 ECI transforms, fixed
percentile, zero-line and rolling z-score thresholds, long/cash and
long/short, leads of 1 to 5 quarters); **1,080 passed the in-sample
validity checks**. The rule was chosen by the highest **in-sample**
Sharpe on 2008-12-31 → 2019-12-31 (45 quarters), before any
out-of-sample result was looked at:

- **Rule:** hold the S&P 500 (SPY) when ECI 2-quarter growth, as it stood
  **two quarters (~6 months) earlier**, is at or below **1.315%** (its
  in-sample median); otherwise hold cash. Countercyclical.
- **In-sample:** Sharpe **1.19** versus 0.79 for buy-and-hold.
- **Out-of-sample (2020-03-31 → 2026-03-31, 25 quarters):** Sharpe
  **0.70** versus **0.80** for buy-and-hold (HAC t 1.33); annualized
  return **4.3%** versus 14.5%; maximum drawdown **0.0%** versus −23.9%.
  The rule was long SPY in 3 of the 25 quarters (2020-Q4 to 2021-Q2) and
  has been in cash since 2021-Q3, because lagged 2-quarter wage growth has
  stayed above 1.315%.

### Correction to the earlier version of this page

This page previously reported a rule on a Hidden Markov Model (HMM)
"wage-stress probability" with an out-of-sample Sharpe of **1.41**. That
probability was estimated on the whole 2001–2026 sample and smoothed with
later data, so each quarter's value used information from after that
quarter (look-ahead), and the rule was picked by its out-of-sample score.
Rebuilt without look-ahead, the HMM can only be fitted on the 72
in-sample quarters, below the 100-observation minimum we require for a
traded regime signal, so it is no longer in the search. As a diagnostic
only, the same rule on an in-sample-fitted, forward-filtered HMM scores
**1.03** (`hmm_lookahead_audit_20261016.json`).

### What this means for investors

- The lead-lag tests find wage growth **lagging** equities.
- The selected rule's out-of-sample Sharpe (0.70) is below buy-and-hold
  (0.80), its return is about a third of buy-and-hold's, and its
  out-of-sample record rests on 3 invested quarters.
- ECI remains useful macro context for reading Fed pressure and the
  wage-price dynamic.
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
        "What this shows: Pearson correlations between eight ECI transforms "
        "and forward S&P 500 (SPY) returns at 1-, 2- and 4-quarter "
        "horizons. Every cell lies between −0.19 and +0.06; none of the 72 "
        "Pearson/Spearman/Kendall tests is significant at 5%."
    ),
    observation=(
        "No transform shows a significant linear association with forward "
        "SPY at any quarterly horizon. The largest Pearson cell is "
        "quarter-on-quarter growth vs 4-quarter-forward returns (−0.19, "
        "p = 0.070, n = 96); the largest distance correlation is 0.27 "
        "(2-quarter growth vs 4-quarter-forward). The regime-model rows "
        "shown in an earlier version were built from look-ahead regime "
        "probabilities and have been removed."
    ),
    deep_dive_title="Why treat the heatmap as triage rather than proof?",
    deep_dive_content=(
        "Forward returns at overlapping quarterly horizons induce serial "
        "correlation in the cells, and ~95 quarterly observations is a small "
        "sample for correlation inference. Treat the heatmap as descriptive "
        "triage; the formal tests below carry the inferential weight."
    ),
    interpretation=(
        "The tradeable-horizon cells are weak and none is significant, "
        "consistent with a lagging labor-cost gauge rather than a forecaster "
        "of equity returns."
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
        "Pearson correlations between **signal lagged L "
        "quarters** and **SPY 1-quarter forward return**. Cells are small at "
        "every lead (|r| < 0.2 throughout); short leads tend mildly "
        "negative, long leads mildly positive — weak and unstable, the "
        "signature of a lagging series with no reliable predictive lead."
    ),
    observation=(
        "Reading across the rows, correlations are small everywhere "
        "(|r| < 0.2; none starred). The raw YoY z-score transform "
        "`eci_total_comp_yoy_zscore_20q`, for example, is slightly negative "
        "at short leads (L1 −0.093), drifts positive with distance, and "
        "peaks only at L8 (r = 0.177); the sign changes along the row. The "
        "selected rule's signal, 2-quarter growth, is −0.072 at L2. **No "
        "lead gives a raw wage-growth transform a significant correlation "
        "with next-quarter SPY.**"
    ),
    interpretation=(
        "A near-null result. **In plain English:** wage growth follows the "
        "economy and the market rather than leading them, and lagging a raw "
        "wage signal does not produce a significant linear relationship "
        "with next-quarter SPY at any lead from 0 to 8 quarters."
    ),
    key_message=(
        "No lead works cleanly: the raw wage-growth transforms are weak and "
        "sign-unstable across L = 0…8 quarters. This corroborates the "
        "lagging verdict — wages respond to the cycle, they do not lead SPY."
    ),
)


LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This block evaluates the selected rule at every lead of the floored "
        "QUARTERLY grid L = 1…5 and shows, for context, the best OOS Sharpe "
        "of any IS-valid combo at each lead. The rule and its lead were "
        "chosen by in-sample Sharpe; the reference line is SPY buy-and-hold "
        "(OOS Sharpe 0.80, √4 quarterly annualization)."
    ),
    question=(
        "How does the selected rule's Sharpe change if the 2-quarter lead is "
        "moved to 1, 3, 4 or 5 quarters?"
    ),
    how_to_read=(
        "Dotted line: the selected rule's in-sample Sharpe at each lead "
        "(L1 0.93, L2 1.19, L3 1.12, L4 0.88, L5 1.02). Solid line: its OOS "
        "Sharpe at each lead (L1 0.70, L2 0.70, L3 −0.07, L4 0.68, L5 0.43). "
        "Bars: the best OOS Sharpe of any IS-valid combo at that lead; they "
        "are chosen after seeing OOS results, so they are context, not a "
        "selection."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "The selected rule's in-sample and OOS Sharpe across the floored "
        "quarterly grid L1–L5, with the per-lead best OOS Sharpe of any "
        "IS-valid combo as bars. The rule was selected at L2 by in-sample "
        "Sharpe (1.19); its OOS Sharpe at L2 is 0.70 vs 0.80 buy-and-hold."
    ),
    observation=(
        "In-sample, L2 is the highest point of the rule's lead curve (1.19). "
        "Out-of-sample, L1 and L2 are almost equal (0.70), L3 is negative "
        "(−0.07) and L5 is 0.43; no lead of this rule beats buy-and-hold "
        "out-of-sample."
    ),
    interpretation=(
        "The out-of-sample result moves by 0.77 Sharpe between adjacent "
        "leads (L2 0.70 to L3 −0.07), which on 25 quarters reflects how few "
        "invested quarters drive the number."
    ),
    key_message=(
        "Selected at L2 by in-sample Sharpe (1.19); OOS 0.70 against 0.80 "
        "buy-and-hold; no lead of this rule beats buy-and-hold out of sample."
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
        "What this shows: Granger F-statistics by "
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
        "This is the cleanest reverse-causality result "
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
        "What this shows: pre-whitened cross-"
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
        "After stripping each series' own memory, "
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
        "What this shows: impulse-response panels, "
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
        "At the horizons a quarterly strategy actually "
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
        "What this shows: bidirectional transfer "
        "entropy with permutation p-values. Wages → SPY: p = 0.26 (not "
        "significant). SPY → wages: p = 0.16 (not significant). Neither "
        "direction clears the 5% bar on the new run."
    ),
    observation=(
        "Wage growth → SPY: p = 0.26 — clearly insignificant. SPY → wage "
        "growth: p = 0.16 — also insignificant, though still the smaller of "
        "the two and on the same side as the significant Granger result."
    ),
    deep_dive_title="Does either transfer-entropy reading matter?",
    deep_dive_content=(
        "On ~97 tercile-binned quarterly observations transfer entropy has "
        "low power and noisy permutation p-values, so we treat it as a "
        "directional check only (per evidence_status.json). Read this way, "
        "it adds nothing that overturns the linear tests: neither direction "
        "is significant (wages → SPY p = 0.26; SPY → wages p = 0.16), and "
        "the smaller p-value is still on the reverse (market → wages) side "
        "the Granger test finds."
    ),
    interpretation=(
        "No non-linear channel rescues the indicator: "
        "the forward direction is flatly insignificant, and the reverse "
        "direction — while also insignificant here — is the one that carries "
        "any weak information flow."
    ),
    key_message=(
        "There is no non-linear escape hatch — model-free information flow "
        "is insignificant both ways, and what little there is leans from "
        "stocks to wages, not the other way."
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
        "What this shows: quantile-regression "
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
        "Many indicators fail at the mean but work at "
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
        "infers unobserved \"high\" vs \"low\" wage-inflation states from "
        "the data) on ECI year-over-year growth, fitted on the 72 in-sample "
        "quarters only and read with a forward filter (each quarter's value "
        "uses data up to that quarter), plus a sort of history into "
        "quartiles of concurrent wage growth with SPY performance in each. "
        "The HMM is a diagnostic: it is not a tournament signal, because a "
        "traded regime signal needs at least 100 in-sample observations."
    ),
    question=(
        "Do states of the wage cycle coincide with different stock-market "
        "environments?"
    ),
    how_to_read=(
        "The HMM panel shows the filtered probability of the high-wage-"
        "inflation state over time; the vertical line marks the start of the "
        "out-of-sample window, after which the model parameters are frozen. "
        "The quartile chart on the Story page shows concurrent SPY "
        "Sharpe/return in four bars, from slowest (Q1) to fastest (Q4) wage "
        "growth."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: in-sample-fitted, forward-filtered HMM probability "
        "of the high-wage-inflation state, NBER recessions shaded. The high "
        "state covers 63% of quarters (mean YoY 3.5%) and the low state 37% "
        "(mean YoY 2.0%); the probability rounds to 1.00 in every quarter "
        "from 2021-Q2 to 2023-Q4."
    ),
    observation=(
        "Mean concurrent quarterly SPY return is 1.9% in the high state and "
        "3.8% in the low state. The quartile sort points the same way: Q1 "
        "(slowest wage growth) Sharpe 1.17 vs Q4 0.67 and Q3 −0.15. Both "
        "are concurrent, not lagged. An earlier version of this chart showed "
        "a full-sample, smoothed HMM (a 47% / 53% split) that used later "
        "data at each point; it has been replaced."
    ),
    deep_dive_title="How stable is the relationship over time?",
    deep_dive_content=(
        "The 16-quarter rolling correlation between the selected signal "
        "(lagged two quarters) and next-quarter SPY agrees with its "
        "full-sample sign in 52% of windows (verdict `moderately_stable` in "
        "`structural_break_eci_total_comp_spy.json`). The Quandt-Andrews "
        "test does not flag a structural break (candidate 2020-Q2, sup-F "
        "3.32, bootstrap p = 0.38)."
    ),
    interpretation=(
        "Wage-inflation states coincide with different concurrent equity "
        "returns (slow wage growth, better returns). This is descriptive; "
        "it is not a forecast."
    ),
    key_message=(
        "Slow-wage-growth periods have coincided with better concurrent "
        "equity returns; the regime model is shown as a causal diagnostic "
        "and is not traded."
    ),
)


TOURNAMENT_DIST_BLOCK = dict(
    chart_status="ready",
    method_name="Search Distribution",
    method_theory=(
        "The distribution of out-of-sample Sharpe ratios across all 1,080 "
        "IS-valid combinations in the quarterly tournament, with the "
        "in-sample-selected rule marked."
    ),
    question=(
        "Where does the selected rule's OOS Sharpe sit among all the rules "
        "the search could have picked?"
    ),
    how_to_read=(
        "Histogram of OOS Sharpe across IS-valid combos; vertical markers "
        "show the median (0.40), buy-and-hold (0.80) and the selected rule "
        "(0.70). All figures use quarterly √4 annualization on the "
        "25-quarter OOS window."
    ),
    chart_name=TOURNAMENT_DIST_CHART_NAME,
    chart_caption=(
        "Distribution of OOS Sharpe across 1,080 IS-valid combos with the "
        "median (0.40), buy-and-hold (0.80) and the selected rule (0.70) "
        "marked; 127 combos have a higher OOS Sharpe than buy-and-hold."
    ),
    observation=(
        "The median IS-valid combination (0.40) is below buy-and-hold "
        "(0.80). The selected rule (0.70) is at the 73rd percentile. The "
        "rank correlation between in-sample and OOS Sharpe across the grid "
        "is 0.52."
    ),
    interpretation=(
        "Most rules built on this indicator scored below buy-and-hold in the "
        "test window, and the rule chosen in-sample did too."
    ),
    key_message=(
        "The typical ECI-based rule underperforms buy-and-hold out of "
        "sample; the in-sample-selected rule sits at the 73rd percentile "
        "(0.70 vs 0.80)."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    "title": (
        "The tests point one way: the market leads, wages follow"
    ),
    "overview": (
        "*One question, attacked several independent ways: does wage-"
        "inflation momentum carry information about future S&P 500 (SPY) "
        "returns — or does the market move first? SPY predicts ECI at every "
        "tested quarterly lag; ECI predicts SPY at none.*\n\n"
        "All statistics computed on QUARTERLY data, analytical sample "
        "2001-Q1 → 2026-Q1 (~101 quarters), from "
        "`results/eci_total_comp_spy/core_models_20261016/`.\n\n"
        "The Strategy page reports the rule with the best in-sample Sharpe: "
        "its out-of-sample Sharpe is 0.70 against 0.80 for buy-and-hold, and "
        "the median rule in the search scores 0.40."
    ),
    "plain_english": (
        "This section shows the statistical evidence on whether wage growth "
        "predicts the stock market. The lead-lag tests — correlation, "
        "Granger causality, pre-whitened cross-correlation, local "
        "projections, and transfer entropy — point the same way: the "
        "S&P 500 (SPY) helps predict wage growth one to four quarters ahead, "
        "while wage growth predicts the market at no tested lag. Wages are a "
        "lagging indicator. Slow wage growth has coincided with better "
        "concurrent equity returns, which is descriptive, not predictive."
    ),
    # Row counts VERIFIED against the 20261016 artifacts; counts exclude the header row.
    "downloads": [
        {"label": "Granger causality (Toda-Yamamoto), both directions × 4 quarterly lags (8 rows)",
         "path": "results/eci_total_comp_spy/core_models_20261016/granger_causality.csv"},
        {"label": "Granger F-statistics by lag, ECI → SPY (4 rows)",
         "path": "results/eci_total_comp_spy/granger_by_lag.csv"},
        {"label": "Correlation battery, signal × horizon × metric (96 rows)",
         "path": "results/eci_total_comp_spy/core_models_20261016/correlations.csv"},
        {"label": "Pre-whitened CCF, quarterly offsets −8..+8 (17 rows)",
         "path": "results/eci_total_comp_spy/core_models_20261016/ccf_prewhitened.csv"},
        {"label": "Local projections, forward + reverse × 3 quarterly horizons (6 rows)",
         "path": "results/eci_total_comp_spy/core_models_20261016/local_projections.csv"},
        {"label": "Transfer entropy, both directions (2 rows)",
         "path": "results/eci_total_comp_spy/core_models_20261016/transfer_entropy.csv"},
        {"label": "Quantile regression, 7 quantiles (7 rows)",
         "path": "results/eci_total_comp_spy/core_models_20261016/quantile_regression.csv"},
        {"label": "Lead-correlation grid, 8 transforms × leads L0..L8 quarters (8 rows)",
         "path": "results/eci_total_comp_spy/lead_correlation_20261016.csv"},
        {"label": "Regime quartile returns, Q1–Q4 (4 rows)",
         "path": "results/eci_total_comp_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe, episodes (4 rows)",
         "path": "results/eci_total_comp_spy/subperiod_sharpe.csv"},
        {"label": "Rolling 16-quarter correlation, selected signal vs next-quarter SPY (81 rows)",
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
    # fix Step C #187 — integrated synthesis rendered AFTER the Level-2
    # sub-tabs (page_templates method_blocks["level2_summary"]). The five+
    # tests above read as independent silos without a closing bottom line;
    # this states, in one paragraph, what they jointly conclude. Every claim
    # traces to results/eci_total_comp_spy/*.
    "level2_summary": {
        "title": "What the evidence adds up to",
        "body": (
            "The correlation battery and the lead view find no significant "
            "association at any quarterly horizon or lead (|r| < 0.2 across "
            "L0–L8). Toda-Yamamoto Granger is one-directional: the S&P 500 "
            "forecasts wage growth at every tested quarterly lag "
            "(p = 0.014/0.013/0.004/0.003), while wage growth forecasts the "
            "market at none (smallest p = 0.50). The pre-whitened CCF finds "
            "no lead on either side — only a contemporaneous negative echo at "
            "offset 0 (r = −0.25). Local projections, transfer entropy and "
            "quantile regression find no forward effect; transfer entropy is "
            "insignificant both ways (SPY → wages p = 0.16, wages → SPY "
            "p = 0.26). The regime work shows slow wage growth coinciding "
            "with better concurrent returns, with no flagged structural "
            "break. In the search, the median IS-valid rule (0.40) scores "
            "below buy-and-hold (0.80). **Bottom line:** the tests classify "
            "ECI total compensation as a lagging wage indicator — the market "
            "leads wages."
        ),
        "key_message": (
            "The tests converge: ECI is lagging (SPY leads wages). The next "
            "page's in-sample-selected rule scores 0.70 out of sample "
            "against 0.80 for buy-and-hold."
        ),
    },
    "tournament_intro": (
        "The statistical tests above ask whether the indicator *predicts*. "
        "The tournament asks a practical question: across a grid of "
        "QUARTERLY trading rules built from this series, which rule had the "
        "best in-sample record, and how did it do afterwards?\n\n"
        "We tested **1,180 strategy combinations** — 8 signal transforms × "
        "threshold schemes × 4 strategy families × the floored quarterly "
        "lead grid L1..L5 — of which **1,080 passed in-sample validity "
        "checks** (the buy-and-hold benchmark row is excluded from this "
        "count). The winner was chosen by in-sample Sharpe on 2008-12-31 → "
        "2019-12-31 and scored on 2020-03-31 → 2026-03-31: OOS Sharpe 0.70 "
        "versus 0.80 for buy-and-hold. The median IS-valid combination "
        "scored 0.40."
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is lagging — the market moves "
        "first and wages follow. The next page shows the rule the search "
        "selected in-sample and its out-of-sample record against "
        "buy-and-hold."
    ),
}

# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = (
        "The Strategy: An In-Sample-Selected Wage-Growth Rule for SPY"
    )
    PAGE_SUBTITLE = (
        "1,180 quarterly rule combinations were scored. The one with the best "
        "in-sample Sharpe is reported here, with its out-of-sample record "
        "against buy-and-hold."
    )

    STATISTICAL_FRAMING_BANNER = (
        "Correction (2026-10-16). This page previously reported hmm_stress / "
        "T3_zscore_1.0 / Long/Cash / L4 quarters with an OOS Sharpe of 1.41 "
        "(HAC t 3.04). That result relied on HMM probabilities fitted on the "
        "full sample and smoothed with future data (look-ahead), and the rule "
        "was picked by its OOS score. Rebuilt without look-ahead and with "
        "in-sample selection, the winner below has an OOS Sharpe of 0.70 "
        "against 0.80 for SPY buy-and-hold."
    )

    PLAIN_ENGLISH = (
        "The rule moves between SPY and cash once a quarter. It holds SPY "
        "when ECI 2-quarter wage growth, as it stood two quarters earlier, "
        "is at or below 1.315% (its in-sample median), and holds cash "
        "otherwise. It was chosen because it had the highest in-sample "
        "Sharpe (1.19 vs 0.79 for buy-and-hold, 2008–2019). Out of sample "
        "(2020-03-31 → 2026-03-31, 25 quarters) it scored a Sharpe of 0.70 "
        "versus 0.80 for buy-and-hold, an annualized return of 4.3% versus "
        "14.5%, and no drawdown versus −23.9%. It was invested in 3 of the "
        "25 quarters and has been in cash since 2021-Q3."
    )

    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="Candidate",
        status_detail=(
            "Selected by in-sample Sharpe from a 1,180-rule quarterly search "
            "and scored on a 25-quarter out-of-sample window (2020-Q1 → "
            "2026-Q1). No frozen-rule confirmation test has been run."
        ),
        strengths=[
            "Selection used in-sample data only (2008-12-31 → 2019-12-31): "
            "IS Sharpe 1.19 vs 0.79 for buy-and-hold, IS HAC t 4.84.",
            "Out of sample the rule had no drawdown (0.0% vs −23.9% for "
            "buy-and-hold); it was in cash for 22 of 25 quarters, including "
            "2022.",
            "Costs are negligible at 0.32 trades per year (OOS Sharpe 0.67 "
            "at 50 bps per trade, `transaction_costs.csv`).",
        ],
        risks=[
            "Out of sample the rule's Sharpe (0.70) is below buy-and-hold "
            "(0.80) and its annualized return (4.3%) is below buy-and-hold "
            "(14.5%); OOS HAC t 1.33 (p = 0.18).",
            "The OOS record rests on 3 invested quarters (2020-Q4 to "
            "2021-Q2); moving the lead from 2 to 3 quarters changes the OOS "
            "Sharpe from 0.70 to −0.07.",
            "The causality runs from the market to wages: Toda-Yamamoto "
            "Granger finds ECI → SPY significant at no quarterly lag and "
            "SPY → ECI significant at lags 1–4.",
            "1,080 distinct rules were compared; the expected maximum |z| "
            "under no skill is about 3.31, against the winner's in-sample "
            "HAC t of 4.84.",
        ],
        conclusion=(
            "The in-sample-selected rule (lagged 2-quarter wage growth at or "
            "below its in-sample median → long SPY, otherwise cash) earned an "
            "OOS Sharpe of 0.70 against 0.80 for buy-and-hold over 25 "
            "quarters, with a 4.3% annualized return against 14.5% and no "
            "drawdown against −23.9%. The previously published 1.41 relied on "
            "a look-ahead HMM signal and is withdrawn."
        ),
    )

    SIGNAL_RULE_MD = """
**Rule:** each quarter, take ECI 2-quarter compensation growth (`eci_total_comp_pct_2q`, the % change of the Employment Cost Index over two quarters) **as it stood two quarters earlier** (lead L2 ≈ 6 months). If it is **at or below 1.315%** — the median of the lagged series over the in-sample quarters (threshold T1_fixed_p50, fixed) — hold **100% SPY**; otherwise hold **cash**. Countercyclical orientation: slower wage growth = invested. (Family: Long/Cash P1; per `winner_summary.json`.)

If-then form (evaluated once per quarter):
- **IF** 2-quarter ECI growth from two quarters ago ≤ 1.315% → **LONG SPY (100% invested)**.
- **ELSE** → **CASH (0% invested)**.

Selection: highest in-sample Sharpe among 1,080 IS-valid rules on 2008-12-31 → 2019-12-31 (45 quarters): 1.19 vs 0.79 for buy-and-hold.

Out-of-sample (2020-03-31 → 2026-03-31, 25 quarters; Sharpe annualized by √4): Sharpe 0.70 vs 0.80 buy-and-hold (HAC t 1.33); annualized return 4.3% vs 14.5%; maximum drawdown 0.0% vs −23.9%; 2 trades (turnover 0.32/yr); long in 3 quarters (2020-Q4, 2021-Q1, 2021-Q2), cash since 2021-Q3.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
No formulas — three steps:

**What changes in the world:** employers' total compensation costs — wages plus benefits — accelerate or decelerate with the labor cycle. The BLS Employment Cost Index measures them each QUARTER (released ~1 month after quarter end).

**What the signal measures:** the percentage change in the index over the last two quarters, read as it stood **two quarters (~6 months) ago**. The two-quarter delay is the lead with the highest in-sample Sharpe for this rule in a grid of 1 to 5 quarters.

**What decision it drives:** if that reading is at or below 1.315% (the in-sample median) → be LONG SPY; above it → CASH. The Evidence page finds that the market leads wages, so the rule sorts quarters by an old wage reading rather than forecasting through a wage → equity channel.
"""

    MANUAL_USE_MD = (
        "This describes how the backtested rule works so you can replicate "
        "and audit it; it is not a recommendation to trade it. Out of sample "
        "it scored a Sharpe of 0.70 against 0.80 for buy-and-hold. The "
        "quarterly routine is:\n\n"
        "1. **Pull the wage series** — FRED series `ECIALLCIV` (Employment "
        "Cost Index: Total compensation: All Civilian, SA; published ~1 "
        "month after each quarter ends).\n"
        "2. **Compute 2-quarter growth** — 100 × (index this quarter / index "
        "two quarters earlier − 1).\n"
        "3. **Apply the 2-quarter delay** — the reading the rule acts on this "
        "quarter is the 2-quarter growth from two quarters ago.\n"
        "4. **Compare to the threshold** — is it at or below 1.315%? See "
        "`winner_trade_log.csv` for the full signal path.\n"
        "5. **Take the position** — at or below → LONG SPY (100%); above → "
        "CASH (0%). Re-evaluate once a QUARTER."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    WALK_FORWARD_CAPTION = (
        "What this shows: rolling 8-quarter (2-year) annualized Sharpe over "
        "the OOS window versus the reported 0.70. Windows in which the rule "
        "was in cash throughout have no defined Sharpe and are left blank."
    )
    CROSS_PERIOD_CAPTIONS = {
        "subperiod_sharpe": (
            "How to read it: each bar is the STRATEGY's Sharpe in a distinct "
            "historical episode. Only COVID (2020) falls inside the OOS "
            "window (Sharpe 1.00; the rule was invested in one of its four "
            "quarters). Dot-com (2000–02), GFC (2007–09) and China 2015 are "
            "marked `insufficient_data` because they predate the strategy's "
            "out-of-sample window (2020-Q1 onward); the ECI and SPY data "
            "exist for those years."
        ),
    }

    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the 1,080 IS-valid combinations by in-sample Sharpe "
        "(the selection objective) and OOS Sharpe; the star marks the "
        "selected rule (IS 1.19, OOS 0.70), dashed lines buy-and-hold "
        "(IS 0.79, OOS 0.80). Spearman rank correlation between IS and OOS "
        "Sharpe: 0.52."
    )

    CAVEATS_MD = """
**Limitations** (from `winner_summary.json`, `hmm_lookahead_audit_20261016.json`, `structural_break_eci_total_comp_spy.json` and `tournament_validation_20261016/`):

1. **Below buy-and-hold out of sample.** OOS Sharpe 0.70 vs 0.80; annualized return 4.3% vs 14.5%; OOS HAC t 1.33 (p = 0.18).
2. **Few invested quarters.** The rule was long SPY in 3 of the 25 OOS quarters and has been in cash since 2021-Q3. Its OOS Sharpe is computed mostly on zero-return cash quarters; moving the lead from 2 to 3 quarters gives −0.07.
3. **Small quarterly sample.** The OOS window is 25 quarters (2020-03-31 → 2026-03-31) and the common in-sample window 45 quarters (2008-12-31 → 2019-12-31).
4. **Selection.** 1,180 combinations were scored (1,080 IS-valid). The expected maximum |z| among 1,080 unrelated rules with no skill is about 3.31. Across the grid, in-sample and OOS Sharpe have a rank correlation of 0.52; the median IS-valid rule scores 0.40 out of sample.
5. **The causality runs from the market to wages.** Toda-Yamamoto Granger finds SPY → ECI significant at lags 1–4 and ECI → SPY at none; the pre-whitened CCF finds no lead on either side.
6. **Regime signals withdrawn.** The earlier winner (HMM wage-stress probability, OOS Sharpe 1.41) used a full-sample, smoothed HMM. A causal HMM cannot be fitted to the 100-observation minimum on 72 in-sample quarters, so regime signals are not in this search. The same old rule on a 72-quarter causal diagnostic HMM scores 1.03.
7. **Stability.** No structural break is flagged (candidate 2020-Q2, sup-F 3.32, bootstrap p = 0.38); rolling-correlation sign agreement 0.52 (`moderately_stable`). Only the COVID episode falls inside the OOS window.

**Further notes:**

- **Lead floor.** The lead grid starts at one quarter (registry floor L1). ECI is released about one month after quarter end, so at L1 the first month of each holding quarter would precede the release; the selected L2 rule is not affected.
- **Quarterly units throughout.** Sharpe ratios use √4 annualization.
- **Costs.** Returns are gross of costs; at 50 bps per trade the OOS Sharpe is 0.67 (`tournament_validation_20261016/transaction_costs.csv`).
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records "
        "a BUY dated **2020-12-31** — the 2-quarter ECI growth read two "
        "quarters earlier (1.296%) was at or below the 1.315% threshold, so "
        "the position for that quarter moved from 0% to 100% SPY. The "
        "matching SELL is dated **2021-09-30**, when the delayed reading "
        "(1.627%) was above the threshold; the rule has held cash since. "
        "Each row's date is the end of the quarter the position applies to."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2021-09-30",
        "side": "SELL",
        "instrument": "SPY",
        "quantity_pct": "0.0",
        "commission_bps": "5",
        "reason": (
            "growth_2q (eci_total_comp_pct_2q) = 1.627 vs threshold 1.315 — "
            "position 100% → 0%"
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
    "20-quarter (~5-year) rolling z-scores of level and YoY growth; and "
    "growth acceleration. The selected signal is **2-quarter growth** "
    "(`eci_total_comp_pct_2q`), stationarity class `borderline_persistent`. "
    "The raw 20-quarter z-scores are flagged **regime-contaminated** (KPSS "
    "reject). Regime-model signals (HMM, Markov-switching) are not in the "
    "tournament: fitted causally on in-sample quarters only, they would rest "
    "on 72 observations, below the 100-observation minimum for a traded "
    "regime signal. The BLS publication lag is ~1 month after quarter end; "
    "the tradeable lead grid runs L1..L5 QUARTERS (registry floor L1)."
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
| Two-state HMM (in-sample fit, forward filter; diagnostic) + quartile sorts | Do wage-inflation states coincide with distinct market environments? | The descriptive/regime reading appropriate to a lagging series |
| Structural break (Quandt-Andrews sup-F, bootstrap) + rolling correlation | Did the relationship change mid-sample? | No break flagged (candidate 2020-Q2, p = 0.38); rolling-correlation sign agreement 0.52 (moderately stable) |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: 8 signals (quarterly ECI transforms) × threshold schemes (in-sample fixed percentiles 25/50/75, zero-line for sign-meaningful signals, rolling z-score ±1.0 over 12 or 20 quarters) × 4 strategy families (long/cash and long/short, each pro- and countercyclical) × the floored QUARTERLY lead grid {1…5} = **1,180 combinations** plus a buy-and-hold benchmark row (valid=False per ECON-T4).

**Selection (2026-10-16).** Validity uses in-sample data only: at least 20 in-sample quarters, in-sample exposure between 5% and 95%, turnover below 6 position changes per year → **1,080 IS-valid**. The winner is the IS-valid row with the highest in-sample Sharpe on the common window 2008-12-31 → 2019-12-31 (45 quarters; the start is set by the latest-starting signal, the 20-quarter YoY z-score at lead 5); ties are broken by in-sample return, drawdown and trade count. Out-of-sample metrics are reported for that row only. Out-of-sample split per policy `v1_max36_25pct_cap120` in native quarterly units: 2020-03-31 → 2026-03-31 (25 QUARTERS).

Winner: `growth_2q / T1_fixed_p50 / P1_long_cash` (countercyclical), lead L2 quarters; IS Sharpe 1.19 (B&H 0.79), OOS Sharpe 0.70 (B&H 0.80). For comparison only: the highest OOS Sharpe on this grid is growth_2q / T3_zscore_1.0 / LB12 / long-cash countercyclical / L5 (1.30), which ranks 164th in-sample (`legacy_oos_selection_20261016.csv`).

**Regime signals.** The HMM and Markov-switching probabilities are produced by `scripts/_regime_causal.py` (in-sample fit, in-sample standardisation, forward filter, no target return in the likelihood). Both require at least 100 in-sample rows for a traded signal; ECI has 72, so neither enters the grid. The 20261008 winner used a full-sample, smoothed HMM (look-ahead) and was selected by OOS Sharpe; its replay and the causal diagnostic are in `hmm_lookahead_audit_20261016.json`.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_eci_total_comp_spy.py` — deterministic, fixed seeds (DATE_TAG 20261016). Charts are (re)generated by `scripts/generate_charts_eci_total_comp_spy.py`. The canonical quarterly return series for chart producers is `strategy_returns_20261016.csv`; its Sharpe/drawdown/return reconcile with `winner_summary.json`. All tournament CSV metrics are decimal ratios.
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
        "QUARTERLY data. Four distinct periods, kept separate on purpose:\n\n"
        "(a) **Full analytical dataset** — 2001-Q1 → 2026-Q1 (~100 "
        "quarters); the span on which the lead-lag statistics are computed.\n\n"
        "(b) **In-sample / model-development period** — up to 2019-Q4. "
        "Thresholds (e.g. the winner's 1.315% in-sample median) are set on "
        "these quarters, and rules are compared on the common in-sample "
        "window 2008-12-31 → 2019-12-31 (45 quarters), where every candidate "
        "has a defined signal. The winner's in-sample Sharpe there is 1.19 "
        "(buy-and-hold 0.79).\n\n"
        "(c) **Out-of-sample window** — 2020-03-31 → 2026-03-31 (25 "
        "QUARTERS), split per policy v1_max36_25pct_cap120 in native "
        "quarterly units. Every headline performance number is scored here.\n\n"
        "(d) **Research workflow: search → select → evaluate.** We searched "
        "1,180 quarterly rule combinations, SELECTED the winner by in-sample "
        "Sharpe (window b), then scored it once on window (c). A frozen-rule "
        "test on quarters released after this run has not yet been done.\n\n"
        "Sharpe ratios use √4 annualization; leads are in quarters (winner "
        "L2 ≈ 6 months)."
    ),
    plain_english=(
        "One QUARTERLY data series (the Employment Cost Index of total "
        "worker compensation, from 2001) and the S&P 500 ETF (SPY). Four "
        "things are kept separate: the FULL dataset (2001–2026) used by the "
        "lead-lag tests; the IN-SAMPLE period up to 2019, where rules are "
        "built and compared; the OUT-OF-SAMPLE window, 2020 to 2026 (25 "
        "quarters), where the chosen rule is scored; and the WORKFLOW: we "
        "searched 1,180 rule combinations and picked the one with the best "
        "in-sample record before looking at 2020–2026. The lead-lag tests "
        "agree that the market predicts wages, not the reverse. Every number "
        "on these pages is produced by one deterministic script."
    ),
)
