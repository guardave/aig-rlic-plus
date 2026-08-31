"""Credit-Card Delinquency Rate × SPY config (Rule APP-PT1).

QUARTERLY pair, page-38 prefix. Templated on the quarterly credit archetype
(sloos_ci_small_spy_config.py): explicit quarterly units everywhere,
EXECUTIVE_CONFIDENCE_SUMMARY, honest found-in-search framing. The chart set
matches the simpler credit family (no lead-tournament / transfer-entropy / HMM
blocks — those artifacts do not exist for this pair).

HONEST FRAMING (binding). Every number below is verbatim from
results/cc_delinquency_spy/* (winner_summary.json, kpis.json,
evidence_status.json, interpretation_metadata.json,
core_models_20260831/*, granger_by_lag.csv, regime_quartile_returns.csv,
subperiod_sharpe.csv, tournament_validation_20260831/bootstrap.csv,
stationarity_tests_20260831.csv, structural_break_cc_delinquency_spy.json).
Do NOT oversell:

  - The winner (`diff_1q / T0_zero / procyclical / L4 QUARTERS`; OOS Sharpe 1.37
    vs B&H 0.87) is a FOUND-IN-SEARCH CANDIDATE. The median valid combo (0.63)
    UNDERPERFORMS buy-and-hold (0.87); the OOS window is just 32 QUARTERS
    (~8 years); there is no untouched holdout. Bootstrap p = 0.0 is reported,
    but the winner IS the grid maximum, so that p is selection-biased — it is
    NOT independent validation.
  - The winner's DIRECTION CONTRADICTS the economic prior. The household-credit-
    stress prior is COUNTERCYCLICAL (reduce SPY when delinquency is high or
    rising), yet the search selected a PROCYCLICAL rule — long SPY when the
    quarter-on-quarter CHANGE in delinquency was >= 0 (i.e. delinquency RISING)
    four quarters (~1 year) ago. This is flagged as a likely search artifact /
    small-sample fragility (fleet-wide long-lead pattern is issue #28) — NOT as
    evidence that rising delinquency is bullish. A plausible post-hoc read is
    that a year after delinquency starts rising, equities are already in a
    post-stress recovery, so the L4 signal is catching rebounds — but that is a
    RATIONALIZATION of a search-selected rule on a small sample with few
    distinct credit cycles. Note the tension, never smooth it. The concurrent
    quartiles (Q4, highest delinquency, worst SPY Sharpe 0.50 vs 1.23 in Q1) DO
    support the countercyclical reading.
  - The defensible virtue is DRAWDOWN reduction (OOS -4.9% vs -23.9%); read the
    Sharpe as volatility avoidance, not forecasting skill (OOS return 13.4% is
    actually BELOW B&H 14.3%).
  - Credit-card delinquency does NOT Granger-cause SPY at the tested quarterly
    lags (min p 0.33); present it as a lagging credit-stress CONTEXT overlay,
    not a validated forecast.
  - The raw delinquency LEVEL tests NON-stationary over this sample (ADF p 0.37,
    KPSS rejects), so the TRADED transform is the quarter-on-quarter CHANGE
    (diff_1q), which is stationary (ADF p < 0.001). Delinquency is a LAGGING
    credit measure; few credit cycles → the lead rests on a handful of episodes.

QUARTERLY conventions: leads in QUARTERS (winner L4q ≈ 12 months); Sharpe
annualized by √4; OOS window = 32 quarters (2017-09-30 → 2025-06-30); grid of
110 valid combos out of 120 (leads L0..L4).
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: A Credit-Stress Overlay Whose Winner Runs the Wrong Way"
    PAGE_SUBTITLE = (
        "Credit-Card Delinquency Rate (FRB series DRCCLACBS, % of balances "
        "30+ days past due) × S&P 500 (SPY). QUARTERLY, analytical sample "
        "1993-Q1 → 2025-Q2 (~130 quarters). A LAGGING CREDIT indicator: all "
        "leads and windows are in QUARTERS."
    )

    HEADLINE_H2 = (
        "## The credit prior is countercyclical — rising delinquency signals "
        "household stress, so trim equity — yet the search's best rule (OOS "
        "Sharpe 1.37 vs 0.87 buy-and-hold) is PROCYCLICAL at a 4-quarter lead, "
        "going long AFTER delinquency rises. On a 32-quarter window whose median "
        "rule UNDERPERFORMS buy-and-hold, treat that winner as a found-in-search "
        "candidate, not a validated edge."
    )

    PLAIN_ENGLISH = (
        "The credit-card delinquency rate is the share of card balances at least "
        "30 days past due — a clean quarterly read on household financial stress. "
        "The economic prior is countercyclical: when delinquency is high or "
        "rising, consumers are struggling, recession risk is elevated, and you "
        "would want LESS equity, not more. We tested that, and the honest result "
        "is two-sided. The concurrent evidence supports the prior — the quarters "
        "with the HIGHEST delinquency have the WORST SPY Sharpe. But the strategy "
        "search latched onto the opposite orientation (procyclical): it goes long "
        "the S&P 500 a full year AFTER the delinquency rate starts rising. That "
        "runs against the prior, and it sits on a small 32-quarter window where "
        "the typical rule loses to simply holding SPY. So we present the rule as "
        "a candidate with its warning labels attached, and read its main benefit "
        "as drawdown control rather than forecasting. A charitable story — a year "
        "after stress begins, equities are often already recovering — is a "
        "post-hoc rationalization of a search-selected rule, not a confirmed "
        "mechanism."
    )

    WHERE_THIS_FITS = (
        "This is a lagging CREDIT-STRESS context overlay for broad U.S. "
        "equities. It belongs in the portal as macro context — rising "
        "credit-card delinquency is a genuine household-stress gauge that "
        "climbed into the 2001, 2008, and post-2022 stress episodes — not as a "
        "validated timing signal. The formal tests do not find delinquency "
        "Granger-causing SPY, so use it to read the credit cycle, not to time "
        "the market."
    )

    ONE_SENTENCE_THESIS = (
        "Credit-card delinquency is a lagging household-credit-stress gauge "
        "whose concurrent evidence is countercyclical (highest-delinquency "
        "quarters have the weakest SPY Sharpe), yet the search's best QUARTERLY "
        "rule is a procyclical 4-quarter-lag candidate (OOS Sharpe 1.37 vs 0.87) "
        "on a 32-quarter window whose median rule underperforms buy-and-hold — a "
        "found-in-search candidate, not a validated edge."
    )

    KPI_CAPTION = (
        "every performance number on this page is a SEARCH-PHASE, "
        "out-of-sample figure on a 32-QUARTER window (2017-09-30 → "
        "2025-06-30 ≈ 8 years) — a small quarterly sample. The winner was "
        "found as the best of 110 valid combinations; the MEDIAN valid combo "
        "scored 0.63, BELOW buy-and-hold's 0.87. The winner's direction "
        "(procyclical, L4q) contradicts the countercyclical credit prior. "
        "Sharpe ratios use quarterly √4 annualization. Treat it as a "
        "candidate, not a verdict."
    )

    HERO_TITLE = "Credit-Card Delinquency Rate vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — the credit-card delinquency rate "
        "(% of balances 30+ days past due, quarterly) and the S&P 500 (SPY) on "
        "a common time axis, NBER recessions shaded. Watch the peaks: "
        "delinquency climbed through the 2001 and 2008 downturns and again after "
        "2022 — the visual signature of a lagging credit-stress gauge."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Delinquency-Level Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: concurrent S&P 500 (SPY) performance in each "
        "quartile of the credit-card delinquency LEVEL, from lowest (Q1) to "
        "highest (Q4) — annualized Sharpe and return. The highest-delinquency "
        "quartile (Q4) has the WORST Sharpe (0.50) versus 1.23 in the "
        "lowest-delinquency quartile (Q1) — a clean countercyclical concurrent "
        "pattern that fits the credit prior. Note the tension: the published "
        "winner trades the OPPOSITE (procyclical) orientation at a 4-quarter "
        "lag. Descriptive and concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Credit-card delinquency: a lagging credit-stress gauge, tested honestly

The credit-card delinquency rate (FRB series `DRCCLACBS`) is the percentage of
credit-card loan balances at commercial banks that are at least 30 days past
due. It is one of the cleanest quarterly reads on household financial stress:
when families fall behind on cards, their balance sheets are already strained.
Because it is a lagging-to-coincident credit measure, it tends to rise into and
through recessions rather than ahead of them.

The economic prior is **countercyclical**: when delinquency is high or rising,
consumer distress is building, recession and earnings risk rise, and equity
exposure should be REDUCED. Historically the delinquency rate climbed through
the 2001 and 2008 downturns and rose again through the 2022–24 stress.

**What the concurrent evidence says:** it supports the prior. Sorting quarters
by the delinquency level, the highest-delinquency quartile (Q4) delivered the
weakest concurrent SPY Sharpe (0.50) versus 1.23 in the lowest-delinquency
quartile (Q1), with a clean monotone decline in between (1.23 → 0.69 → 0.53 →
0.50). High delinquency coincides with poor equity conditions — exactly the
countercyclical reading.

**What the strategy search did instead:** it selected the OPPOSITE orientation.
The best rule on the 32-quarter out-of-sample window is *procyclical* — long SPY
when the quarter-on-quarter CHANGE in delinquency, viewed with a 4-quarter
(~1-year) lag, is on the favorable side of zero (i.e. delinquency was rising a
year ago), cash otherwise. We flag that contradiction rather than paper over it
(see the Strategy page); on a small quarterly sample it is most plausibly a
search artifact / small-sample fragility, not evidence that rising delinquency
is bullish.

<!-- expander: What exactly is the credit-card delinquency series? -->
The delinquency rate on credit-card loans (FRED/FRB series `DRCCLACBS`) is the
ratio of credit-card balances 30+ days past due to total credit-card balances at
all commercial banks, expressed as a percentage. It is quarterly, seasonally
adjusted, and can be revised. It is a LAGGING credit measure: households fall
behind after their finances deteriorate, so the rate tends to peak during or
after recessions, not before them. Higher readings mean more household distress.
<!-- /expander -->

### A quarterly credit pair — small samples, few cycles, explicit units

Leads are in QUARTERS (the winner's L4 lead ≈ 12 months); Sharpe ratios are
annualized by √4; and the out-of-sample window is **32 quarterly observations**
(2017-Q3 → 2025-Q2, ~8 years). Just as important, credit-stress episodes are
FEW — a handful of cycles over the whole sample — so any lead estimate rests on
a small number of episodes. Every performance number on these pages carries a
found-in-search candidate label.
"""

    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Recession (2001)",
            "narrative": (
                "Credit-card delinquency drifted higher into and through the "
                "2001 downturn, the lagging-stress signature the credit prior "
                "expects. The market weakened as household and corporate credit "
                "conditions deteriorated."
            ),
            "caption": "Dot-Com: delinquency drifted higher through the downturn.",
        },
        {
            "slug": "gfc",
            "title": "Global Financial Crisis (2007–2009)",
            "narrative": (
                "Credit-card delinquency spiked to its highest levels in the "
                "sample as household balance sheets buckled — the clearest "
                "single illustration of delinquency as a credit-stress gauge. "
                "It rose alongside and after the deepest equity drawdown in the "
                "sample, confirming its lagging character."
            ),
            "caption": "GFC: delinquency spiked to sample highs.",
        },
        {
            "slug": "covid",
            "title": "COVID Shock (2020)",
            "narrative": (
                "Fiscal support kept measured delinquency subdued in 2020 even "
                "as the equity crash and rebound played out within two quarters "
                "— far faster than a quarterly, lagging credit series can time. "
                "A reminder that the signal reads the credit cycle, not fast "
                "market shocks."
            ),
            "caption": "COVID: support programs kept delinquency subdued.",
        },
        {
            "slug": "rate_hike_2022",
            "title": "2022–24 Delinquency Upturn (Post-Pandemic Normalization)",
            "narrative": (
                "Delinquency climbed steadily off pandemic lows through the "
                "2022 rate-hike cycle and beyond. In this window the "
                "procyclical rule was long for part of the recovery and avoided "
                "part of the 2022 equity drawdown — the drawdown-control virtue "
                "at work, on a single episode."
            ),
            "caption": "2022–24: delinquency normalized higher; the rule leaned long.",
        },
    ]

    NARRATIVE_SECTION_2 = """
### "Lagging credit gauge" — so why is the winning rule procyclical?

The fair question. The Evidence page shows the concurrent relationship is
countercyclical (highest delinquency → worst SPY), and the formal lead-lag tests
do not find delinquency forecasting SPY (Granger min p 0.33). The rule on the
Strategy page does not overturn that — it does not claim a validated forecast.
What the search found is a *state* description on a short window: quarters in
which the (1-year-old) quarter-on-quarter delinquency change sat on the rising
side of zero coincided, in the 2017–2025 window, with strong equity
performance. Mechanizing that split scored well *in that window*. The charitable
economic story — a year after delinquency starts rising, equities are often
already in a post-stress recovery — is a plausible RATIONALIZATION, not a
confirmed mechanism. Because the direction contradicts the prior, the sample is
only 32 quarters with few distinct credit cycles, and the median searched rule
loses to buy-and-hold, we treat the result as a candidate pattern awaiting a
frozen-rule hold-out exam — and we note it is part of the fleet-wide long-lead
pattern flagged as issue #28.

### What the search surfaced: a long/cash candidate, honestly labelled

Across **110 valid strategy combinations** (of 120 scanned) on the quarterly
lead grid L0..L4, the best rule was: hold the S&P 500 (SPY) when the
4-quarter-lagged quarter-on-quarter change in delinquency is on the favorable
(rising) side of its zero threshold, and hold cash otherwise — a **procyclical**
orientation that CONTRADICTS the countercyclical credit prior. In the 32-quarter
window it scored an OOS Sharpe of 1.37 versus 0.87 for buy-and-hold, with a
maximum drawdown of −4.9% versus −23.9%.

This finding comes with non-negotiable context, stated here rather than in a
footnote:

- **Small quarterly sample.** The out-of-sample test is 32 QUARTERS — a
  handful of independent observations; quarterly Sharpe ratios this unstable
  are routinely over-optimistic. Any winner here is FOUND-IN-SEARCH by
  construction, and there is no untouched holdout yet.
- **The median rule loses.** The median of the 110 valid combinations scored
  0.63 — BELOW buy-and-hold's 0.87. The winner is the right tail of its own
  search.
- **No forecasting mechanism.** Delinquency does not Granger-cause SPY at any
  tested quarterly lag (min p 0.33); the pre-whitened CCF shows only a mild
  inverse echo at 2–4 quarter offsets, no clean predictive lead.
- **Direction contradicts the prior.** The winner is procyclical
  (`direction_consistent: false`); the concurrent quartile evidence points the
  countercyclical way. The search picked the orientation that fit the window.
- **Bootstrap p = 0.0 — but it is the grid maximum.** The winner beat resampled
  buy-and-hold in every draw, yet it was SELECTED as the best of 110 valid
  combos, so that p is selection-biased and is NOT independent validation.
- **Few credit cycles.** Quarterly, revised data with only a handful of
  delinquency cycles; the lead rests on those few cycles.

**What this means:** treat this as *"a candidate pattern found by search on a
small quarterly window, running against its own prior, awaiting its final
exam"* — expectations for a frozen-rule hold-out test should be calibrated low.

### What this means for investors

- **Read delinquency as credit-cycle context, not a market-timing signal** —
  rising credit-card delinquency is a genuine household-stress warning, but the
  tests do not find it forecasting SPY.
- **Do not read the winner as "rising delinquency is bullish."** Its procyclical
  direction contradicts the prior and the concurrent evidence; it is most
  plausibly a small-sample artifact.
- **The defensible benefit is drawdown control** — OOS −4.9% versus −23.9%.
  Read the Sharpe as volatility avoidance, not forecasting skill (OOS return
  13.4% is actually BELOW buy-and-hold's 14.3%).
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
        "Pearson correlations between every delinquency transform (level, "
        "quarter-on-quarter change, 4-quarter change, 20-quarter z-score) and "
        "forward SPY returns at 1-, 2-, and 4-quarter horizons."
    ),
    question=(
        "Is there any raw statistical association between credit-card "
        "delinquency today and stock returns over the coming quarters?"
    ),
    how_to_read=(
        "Rows are delinquency transforms, columns are forward-return horizons "
        "in QUARTERS; each cell's color shows the correlation — deeper color = "
        "stronger. Pale cells mean no association."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        "What this shows: correlations between delinquency transforms and "
        "forward S&P 500 (SPY) returns across quarterly horizons. The grid is "
        "weak throughout (|r| < 0.10) — the LEVEL cells are mildly NEGATIVE "
        "(the countercyclical sign), the CHANGE cells mildly positive — far too "
        "weak to trade."
    ),
    observation=(
        "No transform shows a strong linear association with forward SPY at any "
        "quarterly horizon. Level-vs-forward cells are mildly negative "
        "(−0.04 to −0.09), change-vs-forward cells mildly positive (+0.04 to "
        "+0.07); none is statistically significant (smallest p ≈ 0.33) on ~120 "
        "overlapping quarterly observations."
    ),
    interpretation=(
        "The mildly negative LEVEL sign is directionally consistent with the "
        "countercyclical credit prior, but the magnitudes are too small and the "
        "p-values too weak to support a linear trading rule. Treat the heatmap "
        "as descriptive triage; the formal tests carry the weight."
    ),
    key_message=(
        "At every tradeable quarterly horizon the raw association between "
        "delinquency and future stock returns is weak (|r| < 0.10)."
    ),
)

GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality by Lag",
    method_theory=(
        "Granger causality tests whether past values of the delinquency signal "
        "improve forecasts of SPY returns after accounting for SPY's own "
        "history, across quarterly lags 1–4."
    ),
    question="Does credit-card delinquency lead SPY returns in a formal lag test?",
    how_to_read=(
        "Bars show the p-value at each quarterly lag; a bar below the dashed "
        "0.05 line would indicate a statistically meaningful lead. None is."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: delinquency-to-SPY p-values are insignificant at "
        "every tested quarterly lag (min p 0.33) — delinquency does not "
        "Granger-cause SPY."
    ),
    observation=(
        "Across lags 1–4 quarters, delinquency → SPY p-values are 0.72, 0.91, "
        "0.46, 0.33 — none below 0.05. The smallest is 0.33."
    ),
    interpretation=(
        "This prevents any causal-forecasting claim. Delinquency should be "
        "framed as a lagging credit-stress CONTEXT overlay, not proof that it "
        "forecasts SPY. The strategy on the next page is a searched allocation "
        "overlay, not a validated forecast."
    ),
    key_message="Formal lead-lag evidence is absent (min p 0.33); use the signal as context only.",
)

QUARTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Quartile Analysis",
    method_theory=(
        "Quartile analysis sorts quarters by the credit-card delinquency level "
        "and compares concurrent SPY returns across credit regimes."
    ),
    question="Do low- and high-delinquency regimes produce different SPY outcomes?",
    how_to_read=(
        "Q1 is the lowest-delinquency regime; Q4 is the highest-delinquency "
        "regime. Compare Sharpe and average return across the four buckets."
    ),
    chart_name="regime_stats",
    chart_caption=(
        "What this shows: the highest-delinquency quartile (Q4) has the WORST "
        "concurrent SPY Sharpe (0.50) versus 1.23 (Q1), 0.69 (Q2), 0.53 (Q3) — "
        "a clean, monotone countercyclical pattern."
    ),
    observation=(
        "Concurrent SPY Sharpe is 1.23 / 0.69 / 0.53 / 0.50 from Q1 (lowest "
        "delinquency) to Q4 (highest delinquency); the highest-delinquency "
        "quartile is clearly the weakest for equities."
    ),
    interpretation=(
        "This is the cleanest evidence FOR the countercyclical credit prior — "
        "and it points the OPPOSITE way from the procyclical rule the search "
        "selected on the next page. The tension is real and is flagged, not "
        "smoothed over."
    ),
    key_message="High-delinquency regimes are worst for concurrent SPY — the countercyclical prior holds here.",
)

CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "Pre-whitened cross-correlation filters each series' persistence before "
        "testing whether the delinquency signal tends to move before or after "
        "SPY returns."
    ),
    question="At which quarterly offsets does the delinquency signal line up with SPY returns?",
    how_to_read=(
        "Bars outside the dashed confidence band mark unusual lead-lag "
        "correlation after filtering autocorrelation. Negative offsets are the "
        "signal's past relative to the return."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: the only bars breaching the band sit at offsets −2, "
        "−3 and −4 (r ≈ −0.19 to −0.22), a mild INVERSE echo consistent with "
        "the countercyclical prior — not a clean predictive lead on the "
        "forecasting side."
    ),
    observation=(
        "After pre-whitening, the significant offsets (−2, −3, −4 quarters) "
        "carry a negative sign consistent with the countercyclical prior, but "
        "the near and forecasting-side offsets are inside the band — no clean "
        "positive predictive lead."
    ),
    interpretation=(
        "The CCF corroborates a countercyclical inverse echo with no clean "
        "forward lead — supporting a credit-context reading rather than a "
        "mechanical forecast."
    ),
    key_message="A mild inverse echo at 2–4 quarter offsets, no clean predictive lead.",
)

LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections estimate how future SPY returns respond across 1-, "
        "2-, and 4-quarter horizons after a change in the delinquency signal."
    ),
    question="How does SPY respond after credit-card delinquency changes?",
    how_to_read=(
        "Each bar is an estimated future SPY response after a rise in the "
        "4-quarter delinquency change. Bars near zero mean little measurable "
        "response."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: local-projection coefficients are near zero and "
        "insignificant across horizons (R² < 0.01) — no robust dynamic "
        "response."
    ),
    observation=(
        "Coefficients are tiny (0.004 to 0.015) with p-values 0.73 / 0.53 / "
        "0.54 and R² below 0.01 at every horizon — no measurable forward "
        "response."
    ),
    interpretation=(
        "Consistent with the Granger and CCF results: the raw macro "
        "relationship carries no exploitable forward signal. Any edge in the "
        "tournament comes from a state split on a short window, not a dynamic "
        "response."
    ),
    key_message="SPY shows no robust dynamic response to credit-card delinquency changes.",
)

QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression checks whether the delinquency signal matters "
        "differently in weak, normal, and strong SPY return environments."
    ),
    question="Does credit-card delinquency behave differently in market tails?",
    how_to_read=(
        "Compare the signal coefficient across return quantiles. A flat line "
        "near zero means the signal has no state-dependent association."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: the delinquency coefficient is flat and near zero "
        "across the return distribution — no tail or state-dependent content."
    ),
    observation=(
        "The coefficient is essentially constant and near zero across the "
        "0.25 / 0.50 / 0.75 quantiles (p ≈ 0.53) — no evidence the signal "
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
        "*One question, attacked several independent ways: does credit-card "
        "delinquency carry information about FUTURE S&P 500 (SPY) returns? The "
        "tests converge on: not as a forecast. The concurrent relationship is "
        "countercyclical (highest delinquency → worst SPY), but delinquency "
        "does not Granger-cause SPY at any tested quarterly lag (min p 0.33), "
        "and the cross-correlation shows only a mild inverse echo.*\n\n"
        "All statistics computed on QUARTERLY data from "
        "`results/cc_delinquency_spy/core_models_20260831/` and companion "
        "artifacts.\n\n"
        "**Read this page before the Strategy page.** The Strategy page reports "
        "an out-of-sample Sharpe of 1.37 for a searched rule — do NOT read that "
        "as a validated predictive edge. These tests find no forecasting lead, "
        "the MEDIAN searched rule (0.63) UNDERPERFORMS buy-and-hold (0.87), and "
        "the winner's direction (procyclical) contradicts the countercyclical "
        "prior the concurrent evidence supports. The 1.37 is a found-in-search "
        "CANDIDATE whose only defensible virtue is drawdown control (-4.9% vs "
        "-23.9%); read its Sharpe as volatility avoidance, not forecasting "
        "skill (its OOS return, 13.4%, is actually BELOW buy-and-hold's 14.3%)."
    ),
    "plain_english": (
        "This page asks whether credit-card delinquency helps forecast the "
        "stock market. The answer is: not as a forecast. When we sort quarters "
        "by how high delinquency was, the highest-delinquency quarters had the "
        "WORST concurrent equity performance — the countercyclical pattern the "
        "credit prior expects. But the formal lead-lag tests (Granger, "
        "cross-correlation, local projections) find no reliable way to forecast "
        "SPY from delinquency at any quarterly lag. The strategy the search "
        "surfaces on the next page leans the OPPOSITE (procyclical) way on a "
        "small window; we flag that contradiction rather than hide it."
    ),
    "downloads": [
        {"label": "Granger F-statistics by lag, delinquency → SPY (4 rows)",
         "path": "results/cc_delinquency_spy/granger_by_lag.csv"},
        {"label": "Correlation battery, signal × horizon (12 rows)",
         "path": "results/cc_delinquency_spy/core_models_20260831/correlations.csv"},
        {"label": "Pre-whitened CCF, quarterly offsets −4..+4 (9 rows)",
         "path": "results/cc_delinquency_spy/core_models_20260831/ccf_prewhitened.csv"},
        {"label": "Local projections, 1/2/4-quarter horizons (3 rows)",
         "path": "results/cc_delinquency_spy/core_models_20260831/local_projections.csv"},
        {"label": "Quantile regression, 3 quantiles (3 rows)",
         "path": "results/cc_delinquency_spy/core_models_20260831/quantile_regression.csv"},
        {"label": "Regime quartile returns, Q1–Q4 (4 rows)",
         "path": "results/cc_delinquency_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe, credit-stress episodes (4 rows)",
         "path": "results/cc_delinquency_spy/subperiod_sharpe.csv"},
        {"label": "Rolling correlation (delinquency vs SPY)",
         "path": "results/cc_delinquency_spy/rolling_correlation_cc_delinquency_spy.csv"},
        {"label": "Stationarity tests (ADF/KPSS)",
         "path": "results/cc_delinquency_spy/stationarity_tests_20260831.csv"},
    ],
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, QUARTILE_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger", "Quartiles", "CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, QUANTILE_BLOCK],
    "level2_labels": ["Local Projections", "Quantile Regression"],
    "level2_summary": {
        "title": "What the evidence adds up to",
        "body": (
            "Put the tests side by side and they tell one consistent story. "
            "The correlation battery finds only weak cells at every tradeable "
            "quarterly horizon (|r| < 0.10, none significant) — mildly negative "
            "on the level, mildly positive on the change. Granger causality is "
            "decisive in the negative: delinquency → SPY is insignificant at "
            "every tested lag (p = 0.72/0.91/0.46/0.33), so there is no "
            "forecasting lead. The pre-whitened CCF adds only a mild INVERSE "
            "echo at offsets −2 to −4 (r ≈ −0.19 to −0.22), with nothing on the "
            "forecasting side. Local projections and quantile regression both "
            "come back near zero. The one clear signal is CONCURRENT and "
            "countercyclical: the highest-delinquency quartile has the worst "
            "SPY Sharpe (0.50 vs 1.23) — which points the OPPOSITE way from the "
            "procyclical rule the search selected. And the search distribution "
            "shows the median valid combo (0.63) UNDERPERFORMS buy-and-hold "
            "(0.87). **Bottom line:** credit-card delinquency is a genuine "
            "lagging credit-STRESS gauge but a non-forecasting one for SPY; the "
            "concurrent evidence is countercyclical. The strategy on the next "
            "page is best understood as a searched procyclical overlay on a "
            "small quarterly window whose only defensible edge is drawdown "
            "control, not a validated forecasting signal."
        ),
        "key_message": (
            "No forecasting lead (Granger min p 0.33); the clean signal is a "
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
        "We tested a grid of **110 valid combinations** (of 120 scanned) — 4 "
        "signal transforms × threshold schemes × long/cash strategy × quarterly "
        "leads L0..L4. The MEDIAN valid combination scored an OOS Sharpe of "
        "0.63, BELOW buy-and-hold's 0.87. The headline rule on the Strategy "
        "page is the search MAXIMUM (1.37) on a 32-QUARTER out-of-sample "
        "window. In plain English: on a small quarterly sample, with no "
        "forecasting lead and a direction that contradicts the prior, the "
        "winner is a candidate found in search — not a validated edge."
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is no forecasting lead, and the "
        "one clean signal (concurrent, countercyclical) points the opposite way "
        "from the winner. The next page shows the single candidate rule the "
        "search surfaced, with every fragility flag attached. Carry one "
        "guard-rail across: its 1.37 Sharpe is NOT a validated predictive edge "
        "— it is a found-in-search candidate whose defensible virtue is the "
        "shallow drawdown, so read the Sharpe as volatility avoidance."
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
        "32-quarter candidate whose median peer rule underperforms buy-and-hold. "
        "No frozen-rule hold-out test has been run yet."
    )

    PLAIN_ENGLISH = (
        "The best rule from a 110-combination quarterly search: hold the S&P "
        "500 (SPY) when the quarter-on-quarter CHANGE in credit-card "
        "delinquency — viewed with a 4-QUARTER (~1-year) delay — is on the "
        "favorable (rising) side of its zero threshold, and hold CASH "
        "otherwise. In the 32-quarter search window (2017-Q3 → 2025-Q2) it "
        "scored a Sharpe of 1.37 versus 0.87 for buy-and-hold, with a −4.9% "
        "maximum drawdown versus −23.9%. But the window is 32 quarterly "
        "observations, the tests find no forecasting lead (Granger min p 0.33), "
        "the median searched rule (0.63) LOSES to buy-and-hold, and the "
        "direction is PROCYCLICAL — the opposite of the countercyclical credit "
        "prior the concurrent evidence supports. Read it as a candidate overlay "
        "found by search — its final exam on untouched data has not been run. "
        "And read the Sharpe honestly: the defensible virtue here is the "
        "shallow drawdown (-4.9% vs -23.9%), i.e. volatility avoidance — not a "
        "forecasting edge (OOS return 13.4% is actually BELOW B&H 14.3%)."
    )

    EXECUTIVE_CONFIDENCE_SUMMARY = dict(
        status="Candidate",
        status_detail=(
            "A low-confidence, FOUND-IN-SEARCH candidate whose direction "
            "CONTRADICTS the countercyclical credit prior — NOT a validated, "
            "deployable predictive edge. It has not faced a frozen-rule "
            "hold-out final exam, and it is read on a 32-QUARTER out-of-sample "
            "window (2017-Q3 → 2025-Q2, ~8 years)."
        ),
        strengths=[
            "Shallow drawdown is the one defensible virtue: max drawdown -4.9% "
            "vs -23.9% buy-and-hold over the OOS window. Read the Sharpe (1.37 "
            "vs 0.87) as volatility/drawdown avoidance, not evidence of "
            "forecasting skill — the OOS return is actually BELOW buy-and-hold "
            "(13.4% vs 14.3%).",
            "The traded transform is well-behaved statistically: the "
            "quarter-on-quarter delinquency change (diff_1q) is stationary "
            "(ADF p < 0.001, KPSS not rejected), so no regime-contamination "
            "flag on the traded signal — even though the raw LEVEL tests "
            "non-stationary over this sample (ADF p 0.37).",
            "Credit-card delinquency is a genuine lagging credit-STRESS gauge — "
            "it climbed through the 2001 and 2008 recessions and again after "
            "2022 — so as credit-cycle CONTEXT (not a forecast) the series has "
            "real economic content.",
        ],
        risks=[
            "No forecasting mechanism. Delinquency does not Granger-cause SPY at "
            "any tested quarterly lag (min p 0.33); the pre-whitened CCF shows "
            "only a mild inverse echo at 2–4 quarter offsets, no predictive "
            "lead. The rule is a state split, not a forecast.",
            "Tiny out-of-sample sample: 32 QUARTERS (~8 years), on a series "
            "with only a handful of credit cycles; the quarterly Sharpe is "
            "high-variance and found-in-search by construction, with no "
            "untouched hold-out yet.",
            "Selection / overfitting flags: the winner is the MAXIMUM of 110 "
            "valid combos while the MEDIAN valid combo (0.63) LOST to "
            "buy-and-hold (0.87). Bootstrap p = 0.0 is reported, but because "
            "the winner IS the grid maximum that p is selection-biased — not "
            "independent validation.",
            "Direction contradicts the prior (procyclical vs the "
            "countercyclical credit hypothesis, `direction_consistent: "
            "false`); the concurrent quartile evidence (Q4 highest-delinquency "
            "= worst SPY Sharpe 0.50) points the OTHER way. This is most "
            "plausibly a small-sample search artifact — part of the fleet-wide "
            "long-lead pattern flagged as issue #28.",
            "The rolling correlation is sign-unstable through time and a "
            "structural-break proxy flags a large shift (max |z| = 2.95); the "
            "edge leans on few episodes, including a relatively high turnover "
            "(1.6x/yr, 13 OOS trades) for a quarterly rule.",
        ],
        conclusion=(
            "In one paragraph: this long/cash overlay is a low-confidence, "
            "found-in-search CANDIDATE. Its only defensible virtue is drawdown "
            "control (-4.9% vs -23.9%); the 1.37 Sharpe should be read as "
            "volatility avoidance, not a predictive edge, because the tests "
            "find no forecasting lead (Granger min p 0.33) and the return is "
            "actually below buy-and-hold (13.4% vs 14.3%). It sits on just 32 "
            "quarterly observations, the median of its own search lost to "
            "buy-and-hold, and its procyclical direction contradicts the pair's "
            "countercyclical prior (and the concurrent quartile evidence). It "
            "has not passed a frozen-rule hold-out. Treat it as a candidate "
            "pattern awaiting its final exam, not proof that credit-card "
            "delinquency times the S&P 500."
        ),
    )

    DOWNLOADS = [
        {"label": "Winner summary", "path": "results/cc_delinquency_spy/winner_summary.json"},
        {"label": "Granger causality by lag", "path": "results/cc_delinquency_spy/granger_by_lag.csv"},
        {"label": "Regime quartile returns", "path": "results/cc_delinquency_spy/regime_quartile_returns.csv"},
        {"label": "Tournament results", "path": "results/cc_delinquency_spy/tournament_results_20260831.csv"},
        {"label": "Bootstrap validation", "path": "results/cc_delinquency_spy/tournament_validation_20260831/bootstrap.csv"},
        {"label": "Stationarity tests", "path": "results/cc_delinquency_spy/stationarity_tests_20260831.csv"},
        {"label": "Winner trade log (broker style)", "path": "results/cc_delinquency_spy/winner_trades_broker_style.csv"},
    ]

    SIGNAL_RULE_MD = """
**Rule:** Hold the S&P 500 (SPY) **when the 4-QUARTER-lagged quarter-on-quarter CHANGE in the credit-card delinquency rate is on the favorable side of its zero threshold (i.e. delinquency was RISING a year ago); otherwise hold CASH.** This is a **procyclical** orientation. It **contradicts the countercyclical credit-stress prior** the pair was designed to test (`direction_consistent: false` in `interpretation_metadata.json`) — flagged, not smoothed over. (Family: P1 long/cash; signal `diff_1q` (quarter-on-quarter change), threshold T0_zero (gte 0), lead L4 QUARTERS ≈ 12 months — per `winner_summary.json`; `direction: procyclical`.)

If-then form (evaluated once per quarter):
- **IF** the 4-quarter-old delinquency CHANGE is ≥ 0 (delinquency was rising) → **HOLD SPY (100% invested)**.
- **ELSE** → **HOLD CASH**.

Search-phase results (2017-09-30 → 2025-06-30, 32 QUARTERS — **small sample, no hold-out test yet**; Sharpe annualized by √4): OOS Sharpe 1.37 vs 0.87 buy-and-hold; annualized return 13.4% vs 14.3% (BELOW buy-and-hold); maximum drawdown −4.9% vs −23.9%; 13 trades in the OOS window (annual turnover 1.6x); quarterly win rate 50%.

**Read this as a candidate, not a validated edge.** The window is 32 quarterly observations, the tests find NO forecasting lead (Granger min p 0.33), the median of the 110 valid combos (0.63) LOSES to buy-and-hold, and the direction contradicts the countercyclical prior. This pair's `strategy_objective` (per `interpretation_metadata.json`) is **countercyclical_protection**; the fact that the max-Sharpe search selected a *procyclical* rule instead is itself a caution — most plausibly a small-sample artifact (issue #28), not a sign that rising delinquency is bullish. The charitable read — a year after delinquency starts rising, equities are already recovering — is a post-hoc rationalization, not a confirmed mechanism.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
No formulas — three steps:

**What changes in the world:** households fall further behind on their credit-card payments, so the delinquency rate (share of balances 30+ days past due) rises; or they catch up, and it falls. The Federal Reserve reports this quarterly (series `DRCCLACBS`), with a lag and subject to revision.

**What the signal measures:** each quarter, the rule takes the quarter-on-quarter CHANGE in the delinquency rate as it stood **four quarters (~1 year) ago** and asks which side of zero it sits on (rising vs falling). The raw level is persistent and tests non-stationary over this sample, so the CHANGE is used — it is stationary (ADF p < 0.001).

**What decision it drives:** a rising (favorable, per the search) reading → HOLD the market; otherwise → HOLD cash. Because the causality tests find no forecasting lead, this is best understood as a *state* description that happened to sort the 2017–2025 window well — not a forecast of where stocks are going, and running procyclically against the pair's own countercyclical prior.
"""

    MANUAL_USE_MD = (
        "First, the framing: what follows describes how the backtested rule "
        "works so you can replicate and audit it — it is **not** a "
        "recommendation to trade it. This rule is a small-sample search-phase "
        "candidate (best of 110 valid; 32-QUARTER OOS; no hold-out test yet; no "
        "forecasting lead, Granger min p 0.33; median valid combo LOSES to "
        "buy-and-hold; direction contradicts the countercyclical prior). With "
        "that understood, the quarterly routine — no code required — is:\n\n"
        "1. **Pull the credit series** — FRB/FRED series `DRCCLACBS` "
        "(delinquency rate on credit-card loans, all commercial banks; "
        "released quarterly, with a lag).\n"
        "2. **Compute the quarter-on-quarter change** — this quarter's level "
        "minus last quarter's (the level itself tests non-stationary, so the "
        "change is the traded transform).\n"
        "3. **Apply the 4-quarter delay** — the reading the rule acts on this "
        "quarter is the change from four quarters (~1 year) ago.\n"
        "4. **Check the zero threshold** — was that delayed change ≥ 0 "
        "(delinquency rising)? See `winner_trade_log.csv` for the full "
        "signal/threshold path.\n"
        "5. **Take the position** — favorable (rising) → HOLD SPY (100%); "
        "otherwise → HOLD cash. Re-evaluate once a QUARTER.\n\n"
        "Remember the warning labels: 32-quarter window, no forecasting lead, a "
        "median searched rule that loses to buy-and-hold, and a procyclical "
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
        "strategy's 2017-Q3 out-of-sample window, so the durability read rests "
        "on a handful of cycles — treat it as a stability sniff-test, not "
        "confirmation."
    )
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the credit-card delinquency "
            "rate; the target is SPY returns. The rolling correlation tests "
            "whether their linear relationship is stable through time. The sign "
            "swings, so the strategy needs ongoing monitoring rather than one "
            "fixed model."
        ),
        "structural_break": (
            "How to read it: the structural-break proxy asks whether the "
            "delinquency-SPY relationship changes enough that one fixed model "
            "is unlikely to describe the whole sample. A larger statistic means "
            "a larger shift; here max |z| = 2.95."
        ),
    }
    SHOW_TOURNAMENT_SCATTER = True
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: OOS Sharpe distribution across the 110 valid searched "
        "combinations, with the selected rule highlighted as the best "
        "search-phase result (1.37). The dashed line marks buy-and-hold (0.87); "
        "the median valid combo (0.63) sits BELOW it — the winner is the right "
        "tail of its own search."
    )

    CAVEATS_MD = """
**Why we do not call this a validated edge** — flags, none softened (all from `winner_summary.json`, `evidence_status.json`, `granger_by_lag.csv`, `stationarity_tests_20260831.csv`, `structural_break_cc_delinquency_spy.json`, and `tournament_validation_20260831/bootstrap.csv`):

1. **Small quarterly out-of-sample sample.** The test window is **32 QUARTERS** (2017-09-30 → 2025-06-30, ~8 years). That is a handful of independent quarterly observations, on a series with only a few credit cycles. Any winner here is FOUND-IN-SEARCH by construction, and there is no untouched hold-out yet.
2. **No forecasting lead.** Delinquency → SPY Granger causality is insignificant at every tested quarterly lag (p = 0.72/0.91/0.46/0.33, min 0.33); the pre-whitened CCF shows only a mild inverse echo at 2–4 quarter offsets, no predictive lead. The rule reads a *state*, it does not forecast.
3. **The median searched rule loses.** The median of the 110 valid combinations scored OOS Sharpe 0.63 — BELOW buy-and-hold's 0.87. The winner is the maximum of its own search.
4. **Bootstrap significance is selection-biased.** `bootstrap.csv` reports p = 0.0 (significant at 5%), but that test is run on the SELECTED winner — the grid maximum of 110 valid combos — so it does not correct for selection and is NOT independent validation.
5. **Direction contradicts the prior.** The pair was designed around a countercyclical credit-stress hypothesis (`strategy_objective: countercyclical_protection`); the winner is PROCYCLICAL (`direction_consistent: false`), going long a year AFTER delinquency rises, and the concurrent quartile evidence (Q4 highest-delinquency = worst SPY Sharpe 0.50) points the countercyclical way. Most plausibly a small-sample search artifact — part of the fleet-wide long-lead pattern (issue #28) — not a sign that rising delinquency is bullish.
6. **Relationship not stable through time.** A structural-break proxy flags a large shift (max |z| = 2.95) and the rolling correlation is sign-unstable — one fixed model is unlikely to hold across the whole sample.
7. **Data character.** Credit-card delinquency is QUARTERLY, revised, and LAGGING (households fall behind after their finances deteriorate, so the rate peaks during/after recessions). The raw level tests non-stationary here (ADF p 0.37), so the traded transform is the quarter-on-quarter change. The lead rests on a small number of credit cycles.

**What this means:** the honest label is a **found-in-search CANDIDATE** — "the best rule we found by searching a small quarterly window, running against its own prior, not a rule that has passed an independent test." The prescribed next step is a final exam: freeze this rule and test it once on an untouched window. Given the flags above and the absence of a forecasting lead, expectations should be calibrated LOW.

**Further caveats:**

- **The edge is drawdown control, not return.** OOS annualized return (13.4%) is actually BELOW buy-and-hold (14.3%); the Sharpe gap comes entirely from lower volatility and a shallow drawdown (−4.9% vs −23.9%), including sitting in cash through part of the 2022 drawdown — one regime sequence.
- **Quarterly units throughout.** Sharpe ratios use √4 annualization; with 32 observations the sampling error on a quarterly Sharpe is large even before selection effects.
- **Costs.** Returns are gross of costs; at 5 bps per trade and 1.6x turnover/yr the haircut is small (see `tournament_validation_20260831/transaction_costs.csv`, gross Sharpe 1.367) — cost drag is not this pair's problem; the small sample, missing forecasting lead, and against-prior direction are.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** the broker-style log records a "
        "BUY when the 4-quarter-lagged delinquency CHANGE moves to the "
        "favorable (rising, ≥ 0) side of the zero threshold, taking exposure "
        "from 0% to 100% SPY. A SELL moves back to cash when the lagged reading "
        "crosses to the falling side. Every row is in "
        "`winner_trades_broker_style.csv`."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-06-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": "diff_1q procyclical rule crossed T0_zero; position 0% to 100%",
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master.xlsx (Federal Reserve / FRED) | `DRCCLACBS` (Delinquency rate on credit-card loans, all commercial banks, %) | **Quarterly** (1993-Q1 → 2025-Q2, ~130 quarters) |
| Target | Yahoo Finance | SPY (SPDR S&P 500 ETF, dividend-adjusted, quarter-end) | Quarterly (quarter-end) |

QUARTERLY credit pair. The delinquency series is native quarterly and lagging (households fall behind after their finances deteriorate). The raw LEVEL tests non-stationary over this sample (ADF p 0.37; KPSS rejects), so the traded transform is the quarter-on-quarter CHANGE (diff_1q), which is stationary (ADF p < 0.001; KPSS not rejected).
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw indicator is the credit-card delinquency rate (% of balances 30+ "
    "days past due). Because the raw level is persistent and tests "
    "non-stationary over this sample, the pipeline works with transforms: the "
    "quarter-on-quarter change (diff_1q, the WINNING traded signal), the "
    "4-quarter change, and a 20-quarter rolling z-score — all of which test "
    "stationary. Credit-card delinquency is reported quarterly with a "
    "publication lag, which makes a signal delay realistic; the tradeable lead "
    "grid runs L0..L4 QUARTERS, and the winner uses L4."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation battery (Pearson) | Any raw association at any quarterly horizon? | Cheap triage before formal tests |
| Granger causality (lags 1–4q) | Does past delinquency forecast SPY? | Formal lead-lag check; the decisive test for a suspected credit-context indicator |
| Regime quartiles | Do low- and high-delinquency regimes behave differently? | Makes the countercyclical credit story interpretable |
| Pre-whitened CCF (offsets −4..+4q) | At which quarterly offsets do the series echo? | Filters autocorrelation that fakes lead-lag patterns |
| Local projections | Where is SPY h quarters after a delinquency move? | Horizon-by-horizon honesty; robust to overlapping returns |
| Quantile regression | Does the signal predict tail risk? | Cyclical signals sometimes work at the left tail only |
| Structural break / rolling correlation | Is the relationship stable across time? | Durability and overfit guard |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: 4 signal transforms (quarter-on-quarter change, level, 4-quarter change, 20-quarter z-score) × threshold schemes (zero-line, rolling percentiles, z-score bands) × the long/cash strategy family × procyclical/countercyclical orientations × QUARTERLY leads {0…4} = **110 valid combinations** (of 120 scanned) plus a buy-and-hold benchmark row (valid=False per ECON-T4). Median valid OOS Sharpe 0.63 (below buy-and-hold's 0.87). The objective is max OOS Sharpe (√4 QUARTERLY annualization) over the full valid population. Out-of-sample window 2017-09-30 → 2025-06-30 (**32 QUARTERS** — a small sample; any winner is found-in-search). Winner: `diff_1q / T0_zero / P1_long_cash` (procyclical), lead L4 quarters; OOS Sharpe 1.3673, bootstrap p = 0.0 on the selected row (selection-biased — the winner is the grid maximum, so this is not independent validation). Runner-up: `diff_1q / T_roll_p75 / P1_long_cash`, L4, objective 1.259.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_cc_delinquency_spy.py` — deterministic, fixed seeds. The canonical quarterly return series for chart producers is `strategy_returns_20260831.csv`; its Sharpe/drawdown/return reconcile with `winner_summary.json`. Charts are produced by `scripts/generate_charts_cc_delinquency_spy.py`.
"""

_REFERENCES_MD = """
1. Board of Governors of the Federal Reserve System, *Charge-Off and Delinquency Rates on Loans and Leases at Commercial Banks* — methodology for the credit-card delinquency series.
2. Federal Reserve Economic Data (FRED), series `DRCCLACBS`, Delinquency Rate on Credit Card Loans, All Commercial Banks.
3. Yahoo Finance, SPY adjusted price history.
4. Granger, C. W. J. (1969). "Investigating Causal Relations by Econometric Models and Cross-spectral Methods." *Econometrica*, 37(3), 424–438.
5. Mian, A. & Sufi, A. (2010). "Household Leverage and the Recession of 2007–09." *IMF Economic Review*, 58(1), 74–117.
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
        "QUARTERLY credit pair. Keep three periods separate:\n\n"
        "(a) **Full analytical dataset** — 1993-Q1 → 2025-Q2 (~130 quarters); "
        "the span on which the lead-lag statistics are computed.\n\n"
        "(b) **Out-of-sample validation window** — 2017-09-30 → 2025-06-30 "
        "(32 QUARTERS ≈ 8 years). This is where every headline number is "
        "scored. Thirty-two quarterly observations — on a series with only a "
        "handful of credit cycles — is a SMALL sample.\n\n"
        "(c) **Research workflow: search → select → validate.** We searched "
        "110 valid quarterly rule combinations, then SELECTED the winner by "
        "maximizing OOS Sharpe. Because the same window is used to pick the "
        "winner, it is a selection set, not an untouched hold-out — which is "
        "exactly why the winner is labelled found-in-search / CANDIDATE. The "
        "final validate step — freezing the rule and scoring it once on a "
        "genuinely untouched window — has NOT yet been run.\n\n"
        "Sharpe ratios use √4 annualization; leads are in quarters (winner "
        "L4q ≈ 12 months)."
    ),
    plain_english=(
        "One QUARTERLY credit series (the credit-card delinquency rate — the "
        "share of card balances 30+ days past due, from 1993) and the S&P 500 "
        "ETF (SPY). Keep three things separate. First, the FULL dataset: every "
        "quarter from 1993 to 2025, which is what the lead-lag tests use. "
        "Second, the OUT-OF-SAMPLE window, 2017 to 2025 — just 32 quarters — "
        "where we score how the rules actually did. Third, the WORKFLOW: we "
        "searched 110 valid quarterly rule combinations, then picked the winner "
        "by its score on that window. Because we used that same window to "
        "choose the winner, it is a candidate found by search, not a rule that "
        "has passed an independent final exam — that untouched hold-out test is "
        "still to come. The lead-lag tests find no reliable way to forecast SPY "
        "from delinquency; the one clean signal is concurrent and "
        "countercyclical (high delinquency lines up with weak equity "
        "conditions), which points the opposite way from the procyclical rule "
        "the search selected. Every number on these pages can be reproduced by "
        "one deterministic script, and every number is labelled a candidate "
        "because the sample is small and there is no forecasting lead."
    ),
)
