"""SLOOS C&I Lending Standards (Small Firms, net-% tightening) × SPY config (Rule APP-PT1).

QUARTERLY pair, page-31 prefix. Templated on the quarterly archetype
(eci_total_comp_spy_config.py): explicit quarterly units everywhere,
EXECUTIVE_CONFIDENCE_SUMMARY, honest found-in-search framing. The chart set
matches the simpler unrate_spy family (no lead-tournament / transfer-entropy /
HMM blocks — those artifacts do not exist for this pair).

HONEST FRAMING (binding). Every number below is verbatim from
results/sloos_ci_small_spy/* (winner_summary.json, kpis.json,
evidence_status.json, interpretation_metadata.json,
core_models_20260830/*, granger_by_lag.csv, regime_quartile_returns.csv,
subperiod_sharpe.csv, tournament_validation_20260830/bootstrap.csv,
structural_break_sloos_ci_small_spy.json). Do NOT oversell:

  - The winner (`level / T0_zero / procyclical / L3 QUARTERS`; OOS Sharpe 1.51
    vs B&H 0.89) is a FOUND-IN-SEARCH CANDIDATE. The median valid combo (0.60)
    UNDERPERFORMS buy-and-hold (0.89); the OOS window is just 32 QUARTERS
    (~8 years); there is no untouched holdout. Bootstrap p = 0.0 is reported,
    but the winner IS the grid maximum, so that p is selection-biased — it is
    NOT independent validation.
  - The winner's DIRECTION CONTRADICTS the economic prior. The credit-crunch
    prior is COUNTERCYCLICAL (reduce SPY when tightening rises), yet the search
    selected a PROCYCLICAL rule at a 3-quarter lead. This is flagged as a
    likely search artifact / small-sample fragility (fleet-wide long-lead
    pattern is issue #28) — NOT as evidence that tightening is bullish. The
    concurrent quartiles (Q4, most tightening, worst SPY Sharpe 0.31) DO
    support the countercyclical reading; note the tension, never smooth it.
  - The defensible virtue is DRAWDOWN reduction (OOS -4.3% vs -23.9%); read the
    Sharpe as volatility avoidance, not forecasting skill (OOS return 15.1% is
    barely above B&H 14.8%).
  - SLOOS does NOT Granger-cause SPY at the tested quarterly lags (min p 0.23);
    present it as a leading credit-stress CONTEXT overlay, not a validated
    forecast.
  - Quarterly, NSA, revised; few credit cycles → the lead rests on a handful of
    episodes.

QUARTERLY conventions: leads in QUARTERS (winner L3q ≈ 9 months); Sharpe
annualized by √4; OOS window = 32 quarters (2017-12-31 → 2025-09-30);
grid of 120 valid combos (leads L0..L4).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: A Credit-Tightening Overlay Whose Winner Runs the Wrong Way"
    PAGE_SUBTITLE = (
        "Fed Senior Loan Officer Survey (SLOOS) — net % of banks tightening "
        "C&I standards to SMALL firms (series DRTSCIS, NSA) × S&P 500 (SPY). "
        "QUARTERLY, analytical sample 1993-Q1 → 2025-Q3 (~131 quarters). A "
        "leading CREDIT indicator: all leads and windows are in QUARTERS."
    )

    HEADLINE_H2 = (
        "## The credit prior is countercyclical — tighten lending, trim equity "
        "— yet the search's best rule (OOS Sharpe 1.51 vs 0.89 buy-and-hold) "
        "is PROCYCLICAL at a 3-quarter lead. On a 32-quarter window whose "
        "median rule UNDERPERFORMS buy-and-hold, treat that winner as a "
        "found-in-search candidate, not a validated edge."
    )

    PLAIN_ENGLISH = (
        "The Fed's Senior Loan Officer Opinion Survey (SLOOS) asks banks each "
        "quarter whether they are tightening or easing the credit standards "
        "they apply to business (C&I) loans. This pair uses the net percentage "
        "tightening toward SMALL firms — the borrowers most exposed to a credit "
        "squeeze. The economic prior is countercyclical: when banks tighten, "
        "credit-dependent activity slows and recession risk rises, so you would "
        "want LESS equity, not more. We tested that, and the honest result is "
        "two-sided. The concurrent evidence supports the prior — the quarters "
        "with the MOST tightening have the WORST SPY Sharpe. But the strategy "
        "search latched onto the opposite orientation (procyclical) at a "
        "3-quarter lag, on a small 32-quarter window where the typical rule "
        "loses to simply holding SPY. So we present the rule as a candidate "
        "with its warning labels attached, and read its main benefit as "
        "drawdown control rather than forecasting."
    )

    WHERE_THIS_FITS = (
        "This is a leading CREDIT-STRESS context overlay for broad U.S. "
        "equities. It belongs in the portal as macro context — rising "
        "small-firm tightening has historically preceded credit crunches — "
        "not as a validated timing signal. The formal tests do not find SLOOS "
        "Granger-causing SPY, so use it to read the credit cycle, not to time "
        "the market."
    )

    ONE_SENTENCE_THESIS = (
        "Small-firm credit tightening is a leading credit-stress gauge whose "
        "concurrent evidence is countercyclical (most-tightening quarters have "
        "the weakest SPY Sharpe), yet the search's best QUARTERLY rule is a "
        "procyclical 3-quarter-lag candidate (OOS Sharpe 1.51 vs 0.89) on a "
        "32-quarter window whose median rule underperforms buy-and-hold — a "
        "found-in-search candidate, not a validated edge."
    )

    KPI_CAPTION = (
        "every performance number on this page is a SEARCH-PHASE, "
        "out-of-sample figure on a 32-QUARTER window (2017-12-31 → "
        "2025-09-30 ≈ 8 years) — a small quarterly sample. The winner was "
        "found as the best of 120 valid combinations; the MEDIAN valid combo "
        "scored 0.60, BELOW buy-and-hold's 0.89. The winner's direction "
        "(procyclical, L3q) contradicts the countercyclical credit prior. "
        "Sharpe ratios use quarterly √4 annualization. Treat it as a "
        "candidate, not a verdict."
    )

    HERO_TITLE = "SLOOS C&I Tightening (Small Firms) vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — net % of banks tightening C&I "
        "standards to small firms (quarterly) and the S&P 500 (SPY) on a "
        "common time axis, NBER recessions shaded. Watch the spikes: "
        "net-tightening surged into every recession (2001, 2008, 2020) — the "
        "visual signature of a leading credit-stress gauge."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by SLOOS-Tightening Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: concurrent S&P 500 (SPY) performance in each "
        "quartile of SLOOS net-% tightening, from least (Q1) to most (Q4) — "
        "annualized Sharpe and return. The most-tightening quartile (Q4) has "
        "the WORST Sharpe (0.31) versus 0.78–1.00 in Q1–Q3 — a clean "
        "countercyclical concurrent pattern that fits the credit prior. Note "
        "the tension: the published winner trades the OPPOSITE (procyclical) "
        "orientation at a 3-quarter lag. Descriptive and concurrent, not a "
        "tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Small-firm credit tightening: a leading credit-stress gauge, tested honestly

The Fed's Senior Loan Officer Opinion Survey (SLOOS) is the cleanest quarterly
read on whether bank credit is loosening or tightening. This pair uses the net
percentage of banks tightening C&I lending standards toward SMALL firms — the
borrowers with the fewest alternatives to a bank loan, and therefore the first
to feel a credit squeeze. Because the series is a bounded, mean-reverting net
percentage, its level is stationary and is used directly (ADF p < 0.001).

The economic prior is **countercyclical**: when banks pull back, credit-
dependent activity slows, recession and earnings risk rise, and equity exposure
should be REDUCED. Historically net-tightening leads the cycle by roughly one to
four quarters — it spiked ahead of the 2001, 2008, and 2020 downturns.

**What the concurrent evidence says:** it supports the prior. Sorting quarters
by how much banks were tightening, the most-tightening quartile (Q4) delivered
the weakest concurrent SPY Sharpe (0.31) versus 0.78–1.00 in the calmer
quartiles. High tightening coincides with poor equity conditions — exactly the
countercyclical reading.

**What the strategy search did instead:** it selected the OPPOSITE orientation.
The best rule on the 32-quarter out-of-sample window is *procyclical* — long SPY
when the 3-quarter-lagged tightening signal is favorable (easy credit), cash
otherwise. We flag that contradiction rather than paper over it (see the
Strategy page); on a small quarterly sample it is most plausibly a search
artifact / small-sample fragility, not evidence that tightening is bullish.

<!-- expander: What exactly is the SLOOS small-firm C&I series? -->
The Senior Loan Officer Opinion Survey on Bank Lending Practices (FRED series
`DRTSCIS`) reports the NET percentage of domestic banks reporting tighter
standards on commercial & industrial loans to small firms (firms with under
$50 million in annual sales). It is quarterly, NOT seasonally adjusted, and is
qualitative (a diffusion index of banker sentiment, not a hard activity
measure). Positive readings mean net tightening; negative mean net easing. The
survey is released a few weeks after each quarter's reference period.
<!-- /expander -->

### A quarterly credit pair — small samples, few cycles, explicit units

Leads are in QUARTERS (the winner's L3 lead ≈ 9 months); Sharpe ratios are
annualized by √4; and the out-of-sample window is **32 quarterly observations**
(2017-Q4 → 2025-Q3, ~8 years). Just as important, credit-tightening episodes are
FEW — a handful of cycles over the whole sample — so any lead estimate rests on
a small number of episodes. Every performance number on these pages carries a
found-in-search candidate label.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession (2001)",
            "narrative": (
                "Net-tightening toward small firms rose sharply ahead of the "
                "2001 downturn, an early credit-stress warning consistent with "
                "the leading-indicator reading. The market weakened as credit "
                "conditions deteriorated."
            ),
            "caption": "Dot-Com: tightening rose ahead of the downturn.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": (
                "Net-tightening spiked to RECORD highs as the banking system "
                "seized up — the clearest single illustration of SLOOS as a "
                "credit-stress gauge. Tightening led and then confirmed the "
                "deepest equity drawdown in the sample."
            ),
            "caption": "GFC: net-tightening spiked to record highs.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock (2020)",
            "narrative": (
                "Banks tightened sharply in 2020-Q2 as the pandemic hit. The "
                "equity crash and rebound played out within two quarters, far "
                "faster than a quarterly survey can time — a reminder that the "
                "signal reads the credit cycle, not fast market shocks."
            ),
            "caption": "COVID: banks tightened sharply in 2020-Q2.",
        },
        {
            "slug": "rate_hike_2022",
            "title": "2022–23 Tightening (Post-SVB Credit Squeeze)",
            "narrative": (
                "Net-tightening climbed through the 2022 rate-hike cycle and "
                "the March 2023 regional-bank stress. In this window the "
                "procyclical rule sat in cash and avoided part of the 2022 "
                "equity drawdown — the drawdown-control virtue at work, on a "
                "single episode."
            ),
            "caption": "2022–23: post-SVB credit squeeze; the rule sat defensive.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### "Leading credit gauge" — so why is the winning rule procyclical?

The fair question. The Evidence page shows the concurrent relationship is
countercyclical (most tightening → worst SPY), and the formal lead-lag tests do
not find SLOOS forecasting SPY (Granger min p 0.23). The rule on the Strategy
page does not overturn that — it does not claim a validated forecast. What the
search found is a *state* description on a short window: quarters in which the
(9-month-old) tightening level sat on the easy-credit side of zero coincided,
in the 2017–2025 window, with strong equity performance. Mechanizing that split
scored well *in that window*. Because the direction contradicts the prior, the
sample is only 32 quarters, and the median searched rule loses to buy-and-hold,
we treat the result as a candidate pattern awaiting a frozen-rule hold-out
exam — and we note it is part of the fleet-wide long-lead pattern flagged as
issue #28.

### What the search surfaced: a long/cash candidate, honestly labelled

Across **120 valid strategy combinations** on the quarterly lead grid L0..L4,
the best rule was: hold the S&P 500 (SPY) when the 3-quarter-lagged SLOOS
tightening level is on the easy-credit side of its zero threshold, and hold
cash otherwise — a **procyclical** orientation that CONTRADICTS the
countercyclical credit prior. In the 32-quarter window it scored an OOS Sharpe
of 1.51 versus 0.89 for buy-and-hold, with a maximum drawdown of −4.3% versus
−23.9%.

This finding comes with non-negotiable context, stated here rather than in a
footnote:

- **Small quarterly sample.** The out-of-sample test is 32 QUARTERS — a
  handful of independent observations; quarterly Sharpe ratios this unstable
  are routinely over-optimistic. Any winner here is FOUND-IN-SEARCH by
  construction, and there is no untouched holdout yet.
- **The median rule loses.** The median of the 120 valid combinations scored
  0.60 — BELOW buy-and-hold's 0.89. The winner is the right tail of its own
  search.
- **No forecasting mechanism.** SLOOS does not Granger-cause SPY at any tested
  quarterly lag (min p 0.23); the pre-whitened CCF shows only a mild inverse
  concurrent echo, no clean predictive lead.
- **Direction contradicts the prior.** The winner is procyclical
  (`direction_consistent: false`); the concurrent quartile evidence points the
  countercyclical way. The search picked the orientation that fit the window.
- **Bootstrap p = 0.0 — but it is the grid maximum.** The winner beat resampled
  buy-and-hold in every draw, yet it was SELECTED as the best of 120 combos, so
  that p is selection-biased and is NOT independent validation.
- **Few credit cycles.** Quarterly, NSA, revised data with only a handful of
  tightening episodes; the lead rests on those few cycles.

**What this means:** treat this as *"a candidate pattern found by search on a
small quarterly window, running against its own prior, awaiting its final
exam"* — expectations for a frozen-rule hold-out test should be calibrated low.

### What this means for investors

- **Read SLOOS as credit-cycle context, not a market-timing signal** — rising
  small-firm tightening is a genuine credit-stress warning, but the tests do
  not find it forecasting SPY.
- **Do not read the winner as "tightening is bullish."** Its procyclical
  direction contradicts the prior and the concurrent evidence; it is most
  plausibly a small-sample artifact.
- **The defensible benefit is drawdown control** — OOS −4.3% versus −23.9%.
  Read the Sharpe as volatility avoidance, not forecasting skill (OOS return
  15.1% barely clears buy-and-hold's 14.8%).
"""

    TRANSITION_TEXT = (
        "The Evidence page tests whether this credit-stress story survives "
        "correlation, Granger, regime-quartile, cross-correlation, "
        "local-projection, and quantile checks — and whether any searched rule "
        "beats simply holding SPY."
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
QUANTILE_CHART_NAME = "quantile_coef"


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Battery",
    method_theory=(
        "Pearson correlations between every SLOOS tightening transform "
        "(level, quarter-on-quarter change, 4-quarter change, 20-quarter "
        "z-score) and forward SPY returns at 1-, 2-, and 4-quarter horizons."
    ),
    question=(
        "Is there any raw statistical association between small-firm credit "
        "tightening today and stock returns over the coming quarters?"
    ),
    how_to_read=(
        "Rows are SLOOS transforms, columns are forward-return horizons in "
        "QUARTERS; each cell's color shows the correlation — deeper color = "
        "stronger. Pale cells mean no association."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        "What this shows: correlations between SLOOS transforms and forward "
        "S&P 500 (SPY) returns across quarterly horizons. The grid is weak "
        "throughout (|r| < 0.15) and mostly mildly NEGATIVE — the sign the "
        "countercyclical prior expects, but far too weak to trade."
    ),
    observation=(
        "No transform shows a strong linear association with forward SPY at "
        "any quarterly horizon. Cells are small (|r| < 0.15) and mostly "
        "mildly negative; none is statistically significant (smallest p ≈ "
        "0.12) on ~120 overlapping quarterly observations."
    ),
    interpretation=(
        "The negative sign is directionally consistent with the "
        "countercyclical credit prior, but the magnitudes are too small and "
        "the p-values too weak to support a linear trading rule. Treat the "
        "heatmap as descriptive triage; the formal tests carry the weight."
    ),
    key_message=(
        "At every tradeable quarterly horizon the raw association between "
        "credit tightening and future stock returns is weak (and mildly "
        "negative, per the prior)."
    ),
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of SLOOS tightening "
        "improve forecasts of SPY returns after accounting for SPY's own "
        "history, across quarterly lags 1–4."
    ),
    question="Does SLOOS tightening lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show the p-value at each quarterly lag; a bar below the dashed "
        "0.05 line would indicate a statistically meaningful lead. None is."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: SLOOS-to-SPY p-values are insignificant at every "
        "tested quarterly lag (min p 0.23) — SLOOS does not Granger-cause SPY."
    ),
    observation=(
        "Across lags 1–4 quarters, SLOOS → SPY p-values are 0.34, 0.23, 0.34, "
        "0.50 — none below 0.05. The smallest is 0.23."
    ),
    interpretation=(
        "This prevents any causal-forecasting claim. SLOOS should be framed "
        "as a leading credit-stress CONTEXT overlay, not proof that tightening "
        "forecasts SPY. The strategy on the next page is a searched allocation "
        "overlay, not a validated forecast."
    ),
    key_message="Formal lead-lag evidence is absent (min p 0.23); use the signal as context only.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts quarters by SLOOS tightening level and "
        "compares concurrent SPY returns across credit regimes."
    ),
    question="Do low- and high-tightening regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the least-tightening regime; Q4 is the most-tightening regime. "
        "Compare Sharpe and average return across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: the most-tightening quartile (Q4) has the WORST "
        "concurrent SPY Sharpe (0.31) versus 0.78 (Q1), 1.00 (Q2), 0.98 "
        "(Q3) — a clean countercyclical pattern."
    ),
    observation=(
        "Concurrent SPY Sharpe is 0.78 / 1.00 / 0.98 / 0.31 from Q1 (least "
        "tightening) to Q4 (most tightening); the highest-tightening quartile "
        "is clearly the weakest for equities."
    ),
    interpretation=(
        "This is the cleanest evidence FOR the countercyclical credit prior — "
        "and it points the OPPOSITE way from the procyclical rule the search "
        "selected on the next page. The tension is real and is flagged, not "
        "smoothed over."
    ),
    key_message="High-tightening regimes are worst for concurrent SPY — the countercyclical prior holds here.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' persistence "
        "before testing whether tightening tends to move before or after SPY "
        "returns."
    ),
    question="At which quarterly offsets does the tightening signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Negative offsets are the "
        "signal's past relative to the return."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the only bars breaching the band sit at offsets −1 "
        "and −2 (r ≈ −0.25), a mild INVERSE concurrent echo — not a clean "
        "predictive lead on the forecasting side."
    ),
    observation=(
        "After pre-whitening, the significant offsets (−1, −2 quarters) carry "
        "a negative sign consistent with the countercyclical prior, but there "
        "is no positive predictive lead; the forecasting-side offsets are "
        "inside the band."
    ),
    interpretation=(
        "The CCF corroborates a countercyclical concurrent echo with no clean "
        "forward lead — supporting a credit-context reading rather than a "
        "mechanical forecast."
    ),
    key_message="A mild inverse concurrent echo, no clean predictive lead.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across "
        "1-, 2-, and 4-quarter horizons after a change in the SLOOS tightening "
        "signal."
    ),
    question="How does SPY respond after credit tightening changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a rise in the "
        "4-quarter SLOOS tightening change. Bars near zero mean little "
        "measurable response."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: local-projection coefficients are near zero and "
        "insignificant across horizons (R² < 0.01) — no robust dynamic "
        "response."
    ),
    observation=(
        "Coefficients are tiny (order 1e-4) with p-values 0.33 / 0.65 / 0.45 "
        "and R² below 0.01 at every horizon — no measurable forward response."
    ),
    interpretation=(
        "Consistent with the Granger and CCF results: the raw macro "
        "relationship carries no exploitable forward signal. Any edge in the "
        "tournament comes from a state split on a short window, not a dynamic "
        "response."
    ),
    key_message="SPY shows no robust dynamic response to SLOOS tightening changes.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the tightening signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does SLOOS behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A flat line "
        "near zero means the signal has no state-dependent association."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: the SLOOS coefficient is flat and near zero across "
        "the return distribution — no tail or state-dependent content."
    ),
    observation=(
        "The coefficient is essentially constant and near zero across the "
        "0.25 / 0.50 / 0.75 quantiles (p ≈ 0.65) — no evidence the signal "
        "sharpens in market tails."
    ),
    interpretation=(
        "There is no left-tail rescue for the signal; it does not become "
        "informative in weak markets. This reinforces the context-only "
        "reading."
    ),
    key_message="No state-dependent or tail predictive content.",
)


EVIDENCE_METHOD_BLOCKS = {
    "title": "The Evidence: A Countercyclical Concurrent Signal With No Forecasting Lead",
    "overview": (
        "*One question, attacked several independent ways: does small-firm "
        "credit tightening carry information about FUTURE S&P 500 (SPY) "
        "returns? The tests converge on: not as a forecast. The concurrent "
        "relationship is countercyclical (most tightening → worst SPY), but "
        "SLOOS does not Granger-cause SPY at any tested quarterly lag "
        "(min p 0.23), and the cross-correlation shows only a mild inverse "
        "concurrent echo.*\n\n"
        "All statistics computed on QUARTERLY data from "
        "`results/sloos_ci_small_spy/core_models_20260830/` and companion "
        "artifacts.\n\n"
        "**Read this page before the Strategy page.** The Strategy page "
        "reports an out-of-sample Sharpe of 1.51 for a searched rule — do NOT "
        "read that as a validated predictive edge. These tests find no "
        "forecasting lead, the MEDIAN searched rule (0.60) UNDERPERFORMS "
        "buy-and-hold (0.89), and the winner's direction (procyclical) "
        "contradicts the countercyclical prior the concurrent evidence "
        "supports. The 1.51 is a found-in-search CANDIDATE whose only "
        "defensible virtue is drawdown control (-4.3% vs -23.9%); read its "
        "Sharpe as volatility avoidance, not forecasting skill."
    ),
    "plain_english": (
        "This page asks whether small-firm credit tightening helps forecast "
        "the stock market. The answer is: not as a forecast. When we sort "
        "quarters by how much banks were tightening, the most-tightening "
        "quarters had the WORST concurrent equity performance — the "
        "countercyclical pattern the credit prior expects. But the formal "
        "lead-lag tests (Granger, cross-correlation, local projections) find "
        "no reliable way to forecast SPY from SLOOS at any quarterly lag. The "
        "strategy the search surfaces on the next page leans the OPPOSITE "
        "(procyclical) way on a small window; we flag that contradiction "
        "rather than hide it."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag, SLOOS → SPY (4 rows)",
         "path": "results/sloos_ci_small_spy/granger_by_lag.csv"},
        {"label": "Correlation battery, signal × horizon (12 rows)",
         "path": "results/sloos_ci_small_spy/core_models_20260830/correlations.csv"},
        {"label": "Pre-whitened CCF, quarterly offsets −4..+4 (9 rows)",
         "path": "results/sloos_ci_small_spy/core_models_20260830/ccf_prewhitened.csv"},
        {"label": "Local projections, 1/2/4-quarter horizons (3 rows)",
         "path": "results/sloos_ci_small_spy/core_models_20260830/local_projections.csv"},
        {"label": "Quantile regression, 3 quantiles (3 rows)",
         "path": "results/sloos_ci_small_spy/core_models_20260830/quantile_regression.csv"},
        {"label": "Regime quartile returns, Q1–Q4 (4 rows)",
         "path": "results/sloos_ci_small_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe, credit-stress episodes (4 rows)",
         "path": "results/sloos_ci_small_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation (SLOOS vs SPY)",
         "path": "results/sloos_ci_small_spy/rolling_correlation_sloos_ci_small_spy.csv"},
        {"label": "Stationarity tests (ADF/KPSS)",
         "path": "results/sloos_ci_small_spy/stationarity_tests_20260830.csv"},
    ],
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "level2_summary": {
        "title": "What the evidence adds up to",
        "body": (
            "Put the tests side by side and they tell one consistent story. "
            "The correlation battery finds only weak, mildly negative cells at "
            "every tradeable quarterly horizon (|r| < 0.15, none significant). "
            "Granger causality is decisive in the negative: SLOOS → SPY is "
            "insignificant at every tested lag (p = 0.34/0.23/0.34/0.50), so "
            "there is no forecasting lead. The pre-whitened CCF adds only a "
            "mild INVERSE concurrent echo at offsets −1 and −2 (r ≈ −0.25), "
            "with nothing on the forecasting side. Local projections and "
            "quantile regression both come back near zero. The one clear "
            "signal is CONCURRENT and countercyclical: the most-tightening "
            "quartile has the worst SPY Sharpe (0.31 vs 0.78–1.00) — which "
            "points the OPPOSITE way from the procyclical rule the search "
            "selected. And the search distribution shows the median valid "
            "combo (0.60) UNDERPERFORMS buy-and-hold (0.89). **Bottom line:** "
            "SLOOS is a genuine leading credit-STRESS gauge but a "
            "non-forecasting one for SPY; the concurrent evidence is "
            "countercyclical. The strategy on the next page is best understood "
            "as a searched procyclical overlay on a small quarterly window "
            "whose only defensible edge is drawdown control, not a validated "
            "forecasting signal."
        ),
        "key_message": (
            "No forecasting lead (Granger min p 0.23); the clean signal is a "
            "CONCURRENT countercyclical one (Q4 worst). The next page's rule "
            "runs procyclical against that prior — read its Sharpe as "
            "drawdown/volatility avoidance, not a forecasting edge."
        ),
    },
    "tournament_intro": (
        "The statistical tests above ask whether the indicator *forecasts* — "
        "and answer no. The tournament asks a more pragmatic question: across "
        "every reasonable QUARTERLY trading rule you could build from this "
        "series, does *any* of them beat simply holding the S&P 500 (SPY)?\n\n"
        "We tested a grid of **120 valid combinations** — 4 signal transforms "
        "× threshold schemes × long/cash strategy × quarterly leads L0..L4. "
        "The MEDIAN valid combination scored an OOS Sharpe of 0.60, BELOW "
        "buy-and-hold's 0.89. The headline rule on the Strategy page is the "
        "search MAXIMUM (1.51) on a 32-QUARTER out-of-sample window. In plain "
        "English: on a small quarterly sample, with no forecasting lead and a "
        "direction that contradicts the prior, the winner is a candidate found "
        "in search — not a validated edge."
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is no forecasting lead, and the "
        "one clean signal (concurrent, countercyclical) points the opposite "
        "way from the winner. The next page shows the single candidate rule "
        "the search surfaced, with every fragility flag attached. Carry one "
        "guard-rail across: its 1.51 Sharpe is NOT a validated predictive "
        "edge — it is a found-in-search candidate whose defensible virtue is "
        "the shallow drawdown, so read the Sharpe as volatility avoidance."
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = "The Strategy: A Procyclical Long/Cash Overlay Found on 32 Quarters"
    PAGE_SUBTITLE = (
        "— the search maximum on a quarterly credit series with NO forecasting "
        "lead and a direction that CONTRADICTS the countercyclical prior: a "
        "32-quarter candidate whose median peer rule underperforms buy-and-"
        "hold. No frozen-rule hold-out test has been run yet."
    )

    PLAIN_ENGLISH = (
        "The best rule from a 120-combination quarterly search: hold the S&P "
        "500 (SPY) when the SLOOS tightening level — viewed with a 3-QUARTER "
        "(~9-month) delay — is on the easy-credit side of its zero threshold, "
        "and hold CASH otherwise. In the 32-quarter search window (2017-Q4 → "
        "2025-Q3) it scored a Sharpe of 1.51 versus 0.89 for buy-and-hold, "
        "with a −4.3% maximum drawdown versus −23.9%. But the window is 32 "
        "quarterly observations, the tests find no forecasting lead (Granger "
        "min p 0.23), the median searched rule (0.60) LOSES to buy-and-hold, "
        "and the direction is PROCYCLICAL — the opposite of the countercyclical "
        "credit prior the concurrent evidence supports. Read it as a candidate "
        "overlay found by search — its final exam on untouched data has not "
        "been run. And read the Sharpe honestly: the defensible virtue here is "
        "the shallow drawdown (-4.3% vs -23.9%), i.e. volatility avoidance — "
        "not a forecasting edge (OOS return 15.1% barely clears B&H 14.8%)."
    )

    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="Candidate",
        status_detail=(
            "A low-confidence, FOUND-IN-SEARCH candidate whose direction "
            "CONTRADICTS the countercyclical credit prior — NOT a validated, "
            "deployable predictive edge. It has not faced a frozen-rule "
            "hold-out final exam, and it is read on a 32-QUARTER out-of-sample "
            "window (2017-Q4 → 2025-Q3, ~8 years)."
        ),
        strengths=[
            "Shallow drawdown is the one defensible virtue: max drawdown "
            "-4.3% vs -23.9% buy-and-hold over the OOS window. Read the Sharpe "
            "(1.51 vs 0.89) as volatility/drawdown avoidance, not evidence of "
            "forecasting skill — the OOS return edge is negligible (15.1% vs "
            "14.8%).",
            "The signal itself is well-behaved statistically: the SLOOS level "
            "is stationary (ADF p < 0.001, KPSS not rejected), so no "
            "regime-contamination flag on the traded transform.",
            "SLOOS is a genuine leading credit-STRESS gauge — net-tightening "
            "spiked ahead of the 2001, 2008, and 2020 recessions — so as "
            "credit-cycle CONTEXT (not a forecast) the series has real "
            "economic content.",
        ],
        risks=[
            "No forecasting mechanism. SLOOS does not Granger-cause SPY at any "
            "tested quarterly lag (min p 0.23); the pre-whitened CCF shows "
            "only a mild inverse concurrent echo, no predictive lead. The "
            "rule is a state split, not a forecast.",
            "Tiny out-of-sample sample: 32 QUARTERS (~8 years), on a series "
            "with only a handful of credit-tightening cycles; the quarterly "
            "Sharpe is high-variance and found-in-search by construction, with "
            "no untouched hold-out yet.",
            "Selection / overfitting flags: the winner is the MAXIMUM of 120 "
            "combos while the MEDIAN valid combo (0.60) LOST to buy-and-hold "
            "(0.89). Bootstrap p = 0.0 is reported, but because the winner IS "
            "the grid maximum that p is selection-biased — not independent "
            "validation.",
            "Direction contradicts the prior (procyclical vs the "
            "countercyclical credit hypothesis, `direction_consistent: "
            "false`); the concurrent quartile evidence (Q4 most-tightening = "
            "worst SPY Sharpe 0.31) points the OTHER way. This is most "
            "plausibly a small-sample search artifact — part of the "
            "fleet-wide long-lead pattern flagged as issue #28.",
            "The rolling correlation is sign-unstable through time and a "
            "structural-break proxy flags a large shift (max |z| = 2.41); the "
            "edge leans on few episodes, including the strategy sitting in "
            "cash through part of the 2022 drawdown.",
        ],
        conclusion=(
            "In one paragraph: this long/cash overlay is a low-confidence, "
            "found-in-search CANDIDATE. Its only defensible virtue is drawdown "
            "control (-4.3% vs -23.9%); the 1.51 Sharpe should be read as "
            "volatility avoidance, not a predictive edge, because the tests "
            "find no forecasting lead (Granger min p 0.23) and the return edge "
            "is negligible (15.1% vs 14.8%). It sits on just 32 quarterly "
            "observations, the median of its own search lost to buy-and-hold, "
            "and its procyclical direction contradicts the pair's "
            "countercyclical prior (and the concurrent quartile evidence). It "
            "has not passed a frozen-rule hold-out. Treat it as a candidate "
            "pattern awaiting its final exam, not proof that credit tightening "
            "times the S&P 500."
        ),
    )

    DOWNLOADS = [
        {"label": "Winner summary", "path": "results/sloos_ci_small_spy/winner_summary.json"},
        {"label": "Granger causality by lag", "path": "results/sloos_ci_small_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/sloos_ci_small_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/sloos_ci_small_spy/tournament_results_20260830.csv"},
        {"label": "Bootstrap validation", "path": "results/sloos_ci_small_spy/tournament_validation_20260830/bootstrap.csv"},
        {"label": "Stationarity tests", "path": "results/sloos_ci_small_spy/stationarity_tests_20260830.csv"},
        {"label": "Winner trade log (broker style)", "path": "results/sloos_ci_small_spy/winner_trades_broker_style.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule:** Hold the S&P 500 (SPY) **when the 3-QUARTER-lagged SLOOS net-% tightening level (small firms) is on the easy-credit side of its zero threshold (i.e. the lagged signal is favorable); otherwise hold CASH.** This is a **procyclical** orientation (easy credit = risk-on). It **contradicts the countercyclical credit-crunch prior** the pair was designed to test (`direction_consistent: false` in `interpretation_metadata.json`) — flagged, not smoothed over. (Family: P1 long/cash; signal `level`, threshold T0_zero (gte), lead L3 QUARTERS ≈ 9 months — per `winner_summary.json`; `direction: procyclical`.)

If-then form (evaluated once per quarter):
- **IF** the 3-quarter-old SLOOS tightening level is on the easy-credit side of the zero threshold → **HOLD SPY (100% invested)**.
- **ELSE** → **HOLD CASH**.

Search-phase results (2017-12-31 → 2025-09-30, 32 QUARTERS — **small sample, no hold-out test yet**; Sharpe annualized by √4): OOS Sharpe 1.51 vs 0.89 buy-and-hold; annualized return 15.1% vs 14.8%; maximum drawdown −4.3% vs −23.9%; 6 trades in the OOS window (annual turnover 0.75); quarterly win rate 50%.

**Read this as a candidate, not a validated edge.** The window is 32 quarterly observations, the tests find NO forecasting lead (Granger min p 0.23), the median of the 120 valid combos (0.60) LOSES to buy-and-hold, and the direction contradicts the countercyclical prior. This pair's `strategy_objective` (per `interpretation_metadata.json`) is **countercyclical_protection**; the fact that the max-Sharpe search selected a *procyclical* rule instead is itself a caution — most plausibly a small-sample artifact (issue #28), not a sign that tightening is bullish.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
No formulas — three steps:

**What changes in the world:** banks tighten or ease the credit standards they apply to small-firm business (C&I) loans. The Fed's quarterly SLOOS captures that as a NET percentage tightening (released a few weeks after each quarter's reference period).

**What the signal measures:** each quarter, the rule takes the SLOOS net-% tightening LEVEL as it stood **three quarters (~9 months) ago** and asks which side of zero it sits on (net easing vs net tightening). The level is bounded and mean-reverting, so it is used directly (it is stationary — ADF p < 0.001).

**What decision it drives:** favorable/easy-credit reading → HOLD the market; otherwise → HOLD cash. Because the causality tests find no forecasting lead, this is best understood as a *state* description that happened to sort the 2017–2025 window well — not a forecast of where stocks are going, and running procyclically against the pair's own countercyclical prior.
"""

    MANUAL_USE_MD = (
        "First, the framing: what follows describes how the backtested rule "
        "works so you can replicate and audit it — it is **not** a "
        "recommendation to trade it. This rule is a small-sample search-phase "
        "candidate (best of 120 valid; 32-QUARTER OOS; no hold-out test yet; "
        "no forecasting lead, Granger min p 0.23; median valid combo LOSES to "
        "buy-and-hold; direction contradicts the countercyclical prior). With "
        "that understood, the quarterly routine — no code required — is:\n\n"
        "1. **Pull the credit series** — FRED series `DRTSCIS` (SLOOS net % of "
        "banks tightening C&I standards to small firms; released a few weeks "
        "after each quarter).\n"
        "2. **Read the level** — the net-% tightening value itself (no "
        "transform; the level is stationary and used directly).\n"
        "3. **Apply the 3-quarter delay** — the reading the rule acts on this "
        "quarter is the level from three quarters (~9 months) ago.\n"
        "4. **Check the zero threshold** — is that delayed level on the "
        "easy-credit (favorable) side of zero? See `winner_trade_log.csv` for "
        "the full signal/threshold path.\n"
        "5. **Take the position** — favorable → HOLD SPY (100%); otherwise → "
        "HOLD cash. Re-evaluate once a QUARTER.\n\n"
        "Remember the warning labels: 32-quarter window, no forecasting lead, "
        "a median searched rule that loses to buy-and-hold, and a procyclical "
        "direction that runs against the pair's countercyclical prior — the "
        "defensible benefit is drawdown control, not forecasting."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    WALK_FORWARD_TITLE = "Subperiod Sharpe and Durability"
    WALK_FORWARD_CAPTION = (
        "What this shows: strategy vs buy-and-hold Sharpe across major "
        "credit-stress episodes. Several episodes (Dot-Com, GFC) precede the "
        "strategy's 2017-Q4 out-of-sample window, so the durability read rests "
        "on a handful of cycles — treat it as a stability sniff-test, not "
        "confirmation."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the SLOOS net-% tightening "
            "level; the target is SPY returns. The rolling correlation tests "
            "whether their linear relationship is stable through time. The "
            "sign swings, so the strategy needs ongoing monitoring rather than "
            "one fixed model."
        ),
        "structural_break": (
            "How to read it: the structural-break proxy asks whether the "
            "SLOOS-SPY relationship changes enough that one fixed model is "
            "unlikely to describe the whole sample. A larger statistic means a "
            "larger shift; here max |z| = 2.41."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across the 120 valid "
        "searched combinations, with the selected rule highlighted as the best "
        "search-phase result (1.51). The dashed line marks buy-and-hold "
        "(0.89); the median valid combo (0.60) sits BELOW it — the winner is "
        "the right tail of its own search."
    )

    CAVEATS_MD = """
**Why we do not call this a validated edge** — flags, none softened (all from `winner_summary.json`, `evidence_status.json`, `granger_by_lag.csv`, `structural_break_sloos_ci_small_spy.json`, and `tournament_validation_20260830/bootstrap.csv`):

1. **Small quarterly out-of-sample sample.** The test window is **32 QUARTERS** (2017-12-31 → 2025-09-30, ~8 years). That is a handful of independent quarterly observations, on a series with only a few credit-tightening cycles. Any winner here is FOUND-IN-SEARCH by construction, and there is no untouched hold-out yet.
2. **No forecasting lead.** SLOOS → SPY Granger causality is insignificant at every tested quarterly lag (p = 0.34/0.23/0.34/0.50, min 0.23); the pre-whitened CCF shows only a mild inverse concurrent echo, no predictive lead. The rule reads a *state*, it does not forecast.
3. **The median searched rule loses.** The median of the 120 valid combinations scored OOS Sharpe 0.60 — BELOW buy-and-hold's 0.89. The winner is the maximum of its own search.
4. **Bootstrap significance is selection-biased.** `bootstrap.csv` reports p = 0.0 (significant at 5%), but that test is run on the SELECTED winner — the grid maximum of 120 combos — so it does not correct for selection and is NOT independent validation.
5. **Direction contradicts the prior.** The pair was designed around a countercyclical credit-crunch hypothesis (`strategy_objective: countercyclical_protection`); the winner is PROCYCLICAL (`direction_consistent: false`), and the concurrent quartile evidence (Q4 most-tightening = worst SPY Sharpe 0.31) points the countercyclical way. Most plausibly a small-sample search artifact — part of the fleet-wide long-lead pattern (issue #28) — not a sign that tightening is bullish.
6. **Relationship not stable through time.** A structural-break proxy flags a large shift (max |z| = 2.41) and the rolling correlation is sign-unstable — one fixed model is unlikely to hold across the whole sample.
7. **Data character.** SLOOS is QUARTERLY, NOT seasonally adjusted, revised, and qualitative (a diffusion index of banker sentiment, not a hard activity measure). The lead rests on a small number of credit cycles.

**What this means:** the honest label is a **found-in-search CANDIDATE** — "the best rule we found by searching a small quarterly window, running against its own prior, not a rule that has passed an independent test." The prescribed next step is a final exam: freeze this rule and test it once on an untouched window. Given the flags above and the absence of a forecasting lead, expectations should be calibrated LOW.

**Further caveats:**

- **The edge is drawdown control, not return.** OOS annualized return (15.1%) is barely above buy-and-hold (14.8%); the Sharpe gap comes from lower volatility and a shallow drawdown, partly from sitting in cash through part of the 2022 drawdown — one regime sequence.
- **Quarterly units throughout.** Sharpe ratios use √4 annualization; with 32 observations the sampling error on a quarterly Sharpe is large even before selection effects.
- **Costs.** Returns are gross of costs; at 5 bps per trade and 0.75 turnover/yr the haircut is negligible (see `tournament_validation_20260830/transaction_costs.csv`) — cost drag is not this pair's problem; the small sample, missing forecasting lead, and against-prior direction are.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 3-quarter-lagged SLOOS tightening level moves to the "
        "easy-credit (favorable) side of the zero threshold, taking exposure "
        "from 0% to 100% SPY. A SELL moves back to cash when the lagged "
        "reading crosses to the net-tightening side. Every row is in "
        "`winner_trades_broker_style.csv`."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "P1_long_cash: lagged SLOOS level favorable vs T0_zero; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED — Federal Reserve SLOOS | `DRTSCIS` (Net % of banks tightening C&I standards to SMALL firms, NSA) | **Quarterly** (1993-Q1 → 2025-Q3, ~131 quarters) |
| Target | Yahoo Finance | SPY (SPDR S&P 500 ETF, dividend-adjusted, quarter-end) | Quarterly (quarter-end) |

QUARTERLY credit-survey pair. The series is native quarterly and NOT seasonally adjusted (a diffusion index of banker sentiment, not a hard activity measure). Because net-% is bounded and mean-reverting, the LEVEL is stationary (ADF p < 0.001; KPSS not rejected) and is used directly — no differencing required for the traded transform.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the SLOOS net percentage of banks tightening C&I "
    "standards to small firms. Because the net-% level is bounded and "
    "mean-reverting it is stationary and used directly (the winning signal is "
    "`level`). The pipeline also constructs a 1-quarter change, a 4-quarter "
    "change, and a 20-quarter rolling z-score as alternative signal transforms "
    "— all of which test stationary. The survey's publication schedule (a few "
    "weeks after each quarter) makes a short signal delay realistic; the "
    "tradeable lead grid runs L0..L4 QUARTERS, and the winner uses L3."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation battery (Pearson) | Any raw association at any quarterly horizon? | Cheap triage before formal tests |
| Granger causality (lags 1–4q) | Does past tightening forecast SPY? | Formal lead-lag check; the decisive test for a suspected credit-context indicator |
| Regime quartiles | Do low- and high-tightening regimes behave differently? | Makes the countercyclical credit story interpretable |
| Pre-whitened CCF (offsets −4..+4q) | At which quarterly offsets do the series echo? | Filters autocorrelation that fakes lead-lag patterns |
| Local projections | Where is SPY h quarters after a tightening move? | Horizon-by-horizon honesty; robust to overlapping returns |
| Quantile regression | Does the signal predict tail risk? | Cyclical signals sometimes work at the left tail only |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: 4 signal transforms (level, 1-quarter change, 4-quarter change, 20-quarter z-score) × threshold schemes (zero-line, rolling percentiles, z-score bands) × the long/cash strategy family × procyclical/countercyclical orientations × QUARTERLY leads {0…4} = **120 valid combinations** plus a buy-and-hold benchmark row (valid=False per ECON-T4). Median valid OOS Sharpe 0.60 (below buy-and-hold's 0.89). The objective is max OOS Sharpe (√4 QUARTERLY annualization) over the full valid population. Out-of-sample window 2017-12-31 → 2025-09-30 (**32 QUARTERS** — a small sample; any winner is found-in-search). Winner: `level / T0_zero / P1_long_cash` (procyclical), lead L3 quarters; OOS Sharpe 1.5085, bootstrap p = 0.0 on the selected row (selection-biased — the winner is the grid maximum, so this is not independent validation).

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_sloos_ci_small_spy.py` — deterministic, fixed seeds. The canonical quarterly return series for chart producers is `strategy_returns_20260830.csv`; its Sharpe/drawdown/return reconcile with `winner_summary.json`. Charts are produced by `scripts/generate_charts_sloos_ci_small_spy.py`.
"""

_REFERENCES_MD = """
1. Board of Governors of the Federal Reserve System, *Senior Loan Officer Opinion Survey on Bank Lending Practices* (SLOOS) — methodology and net-percentage construction.
2. Federal Reserve Economic Data (FRED), series `DRTSCIS`, Net Percentage of Domestic Banks Tightening Standards for C&I Loans to Small Firms.
3. Yahoo Finance, SPY adjusted price history.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods." *Econometrica*, 37(3), 424–438.
5. Lown, C. & Morgan, D. P. (2006). "The Credit Cycle and the Business Cycle: New Findings Using the Loan Officer Opinion Survey." *Journal of Money, Credit and Banking*, 38(6), 1575–1597.
6. Jordà, Ò. (2005). "Estimation and inference of impulse responses by local projections." *American Economic Review*, 95(1), 161–182.
7. Bailey, D. H. & López de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality." *Journal of Portfolio Management*, 40(5), 94–107.
"""

METHODOLOGY_CONFIG = MethodologyConfig(
    data_sources_table_md=_DATA_SOURCES_MD,
    indicator_construction_md=_INDICATOR_CONSTRUCTION_MD,
    methods_table_md=_METHODS_TABLE_MD,
    tournament_design_md=_TOURNAMENT_DESIGN_MD,
    references_md=_REFERENCES_MD,
    sample_period_note=(
        "QUARTERLY credit-survey pair. Keep three periods separate:\n\n"
        "(a) **Full analytical dataset** — 1993-Q1 → 2025-Q3 (~131 quarters); "
        "the span on which the lead-lag statistics are computed.\n\n"
        "(b) **Out-of-sample validation window** — 2017-12-31 → 2025-09-30 "
        "(32 QUARTERS ≈ 8 years). This is where every headline number is "
        "scored. Thirty-two quarterly observations — on a series with only a "
        "handful of credit cycles — is a SMALL sample.\n\n"
        "(c) **Research workflow: search → select → validate.** We searched "
        "120 quarterly rule combinations, then SELECTED the winner by "
        "maximizing OOS Sharpe. Because the same window is used to pick the "
        "winner, it is a selection set, not an untouched hold-out — which is "
        "exactly why the winner is labelled found-in-search / CANDIDATE. The "
        "final validate step — freezing the rule and scoring it once on a "
        "genuinely untouched window — has NOT yet been run.\n\n"
        "Sharpe ratios use √4 annualization; leads are in quarters (winner "
        "L3q ≈ 9 months)."
    ),
    plain_english=(
        "One QUARTERLY credit-survey series (the Fed's SLOOS net-% of banks "
        "tightening loan standards to small firms, from 1993) and the S&P 500 "
        "ETF (SPY). Keep three things separate. First, the FULL dataset: every "
        "quarter from 1993 to 2025, which is what the lead-lag tests use. "
        "Second, the OUT-OF-SAMPLE window, 2017 to 2025 — just 32 quarters — "
        "where we score how the rules actually did. Third, the WORKFLOW: we "
        "searched 120 quarterly rule combinations, then picked the winner by "
        "its score on that window. Because we used that same window to choose "
        "the winner, it is a candidate found by search, not a rule that has "
        "passed an independent final exam — that untouched hold-out test is "
        "still to come. The lead-lag tests find no reliable way to forecast "
        "SPY from tightening; the one clean signal is concurrent and "
        "countercyclical (heavy tightening lines up with weak equity "
        "conditions), which points the opposite way from the procyclical rule "
        "the search selected. Every number on these pages can be reproduced by "
        "one deterministic script, and every number is labelled a candidate "
        "because the sample is small and there is no forecasting lead."
    ),
)
