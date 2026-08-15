"""NAHB/Wells Fargo Housing Market Index (HMI) × SPY pair configuration (Rule APP-PT1).

New pair, branch feat260706_wells_fargo_housing_spy — MONTHLY
bounded-diffusion-index pair (integer 0-100 HMI). Structure wired by Ace
(chart-name constants, downloads list, monthly-unit conventions);
user-facing narrative across Story / Evidence / Strategy / Methodology is
the FINISHED pass by Research Ray (2026-07-06), every cited number verified
against the results artifacts listed below. Do NOT oversell: the lagging /
reverse-dominant finding is the headline, and the strategy's defensible
virtue is the drawdown, not the Sharpe.

HONEST FRAMING (binding). Empirical verdict for this pair is **LAGGING /
reverse-dominant — builder sentiment does NOT lead the market**:
  - Toda-Yamamoto Granger: SPY→HMI significant at ALL 12 monthly lags
    (p ≈ 0.000 at lags 1-3, all 12 significant); HMI→SPY significant at
    lag 5 ONLY (p = 0.0279; lag-1 borderline 0.0546). Transfer entropy:
    reverse-only (SPY→HMI p = 0.000; HMI→SPY p = 0.386). Pre-whitened CCF:
    scattered borderline bars on both sides (lead(+) lags 1, 5, 12, 13;
    lag(−) −10, −1) → Evan classifies the pair `bidirectional`
    reverse-dominant, schema class `lagging` (interpretation_metadata).
  - Era battery NULL in all four eras since 1993: pre-GFC, GFC-bust, QE
    era, post-COVID — no |pearson_r| above 0.13, no p below 0.31, for
    either `level` or the traded `diff_12m` (era_correlations.csv).
  - The tournament winner (diff_12m 12-month point-change / T2_roll_p25 /
    P1_long_cash pro / L7 MONTHS / LB60; OOS Sharpe 1.43 vs B&H 0.94) sits
    on an 8.2-YEAR (98-month) OOS window — ABOVE the 5-year floor, long by
    fleet standards — but the winner's own lead-curve is a SPIKE at L7,
    not a ridge (L6 1.00 → L7 1.43 → L8 0.93; adjacent-lead durability
    False, ECON-LT2 FAIL), and bootstrap p = 0.1272 (n.s. at 5%) →
    found-in-search CANDIDATE.
  - **The defensible virtue is DRAWDOWN REDUCTION, not the Sharpe**: OOS
    max drawdown −8.1% vs −23.9% for buy-and-hold, at essentially the SAME
    annualized return (15.2% vs 15.4%). KPI and headline emphasis goes to
    the drawdown; the Sharpe edge is volatility-avoidance, and it is
    search-conditioned.

MONTHLY conventions: leads in MONTHS (winner L7 ≈ 7 months); Sharpe
annualized by √12; OOS window = 98 months (2017-09-30 → 2025-10-31);
tradable lead grid L1..L12 (grid floors at L1 by fleet convention although
NAHB's mid-month release FOR the current month makes even L0
lookahead-free). STATIC SOURCE: Data Master sheet WFHMI ends 2025-10
(~9 months stale at run date); FRED delisted NAHBHMI for licensing.

Numbers sourced from results/wells_fargo_housing_spy/ (winner_summary.json,
kpis.json, evidence_status.json, oos_split_record.json,
interpretation_metadata.json, core_models_20260706/*,
structural_break_wells_fargo_housing_spy.json,
tournament_validation_20260706/bootstrap.csv, granger_by_lag.csv,
lead_correlation_20260706.csv, lead_winner_curve_20260706.csv,
regime_quartile_returns.csv, subperiod_sharpe.csv,
winner_trades_broker_style.csv).

GH #13 framing: LEAD_TOURNAMENT_BLOCK["how_to_read"] carries Ray's
plain-English framing (rendered before the lead_sharpe_distribution
chart): the bars are a best-of-any-signal envelope (search-conditioned at
every lead); the honest comparison is the winner's OWN curve
(lead_winner_curve_20260706.csv), which peaks at its published L7 but
collapses either side (L6 1.00 / L8 0.93) — a spike, not a ridge
(ECON-LT2 FAIL; bootstrap p = 0.1272, n.s.).

Winner-rule direction (VERIFIED against winner_trades_broker_style.csv
before authoring): LONG SPY (100%) when the 7-month-lagged HMI 12-month
point-change (`diff_12m`) is ABOVE its rolling 25th-percentile threshold
(LB60 window; latest rolling value −14.0); CASH (0%) when below. Long/CASH
(P1), monthly rebalance, PROCYCLICAL — e.g. 1996-08-31 BUY (signal 14.000
vs threshold −12.000, position 0% → 100%) and 1997-11-30 SELL to cash
(−4.000 vs −4.000 not above, 100% → 0%). No short leg anywhere in the log.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = (
        "The Story: Builder Confidence Follows the Market — "
        "Its Value Is Damage Control"
    )
    PAGE_SUBTITLE = (
        "NAHB/Wells Fargo Housing Market Index (HMI) × S&P 500 (SPY) — "
        "MONTHLY, analytical sample 1993-02 → 2025-10 (393 months of "
        "HMI × SPY overlap; static source ends 2025-10)."
    )

    HEADLINE_H2 = (
        "## The causality tests run backwards: SPY "
        "predicts builder sentiment at all 12 tested monthly lags, while "
        "builder sentiment predicts SPY at one isolated lag (5 months) "
        "only. The search's best rule kept pace with buy-and-hold's return "
        "(15.2% vs 15.4% a year) while cutting the worst drawdown from "
        "−23.9% to −8.1% — the honest headline is the drawdown, not the "
        "Sharpe (1.43 vs 0.94, bootstrap p = 0.13, n.s.)."
    )

    PLAIN_ENGLISH = (
        "The NAHB/Wells Fargo Housing Market Index "
        "(HMI) asks home builders every month how sales look now and six "
        "months out — a 0-100 confidence score. Housing is folklore's "
        "great leading sector, so the hope is that builder mood warns "
        "about the stock market. Tested directly, the information mostly "
        "flows the OTHER way: the S&P 500 (SPY) helps predict builder "
        "sentiment at every tested lag out to a year, while sentiment "
        "helps predict the market at a single isolated 5-month lag — too "
        "thin to call a leading indicator. What the strategy search found "
        "instead is a defensive use: stepping to cash when the 12-month "
        "change in builder mood was deeply negative would have roughly "
        "matched buy-and-hold's return over the last 8.2 years while "
        "taking one-third of the worst-case loss. That drawdown reduction "
        "— not the headline Sharpe — is the defensible finding."
    )

    WHERE_THIS_FITS = (
        "This page is about a LAGGING (reverse-"
        "dominant) sentiment gauge whose practical value, if any, is "
        "defensive. Readers wanting genuine advance warning should look at "
        "the leading pairs in the catalog (e.g. HY-IG credit spread, "
        "Building Permits); the housing-activity cousin pairs "
        "(permit_spy, nhs_spy) make an instructive comparison — hard "
        "housing DATA vs soft housing MOOD."
    )

    ONE_SENTENCE_THESIS = (
        "Builder sentiment (NAHB HMI) follows the stock market rather "
        "than leading it — SPY Granger-causes HMI at all 12 tested "
        "monthly lags, HMI→SPY only at an isolated lag 5 — and the "
        "search's best rule is a drawdown-reduction overlay (−8.1% vs "
        "−23.9% max drawdown at near-identical return), a found-in-search "
        "candidate whose L7 lead is a spike, not a ridge (bootstrap "
        "p = 0.13, n.s.)."
    )

    KPI_CAPTION = (
        "every performance number on this page is a SEARCH-PHASE, "
        "out-of-sample figure on a 98-MONTH window (2017-09-30 → "
        "2025-10-31, ~8.2 years — above the 5-year reliability floor, so "
        "the small-sample caveat is weaker than for short-history pairs). "
        "But the winner was found as the best of 12,980 valid combinations "
        "out of 17,856 scanned; bootstrap p = 0.1272, not significant at "
        "5%; its L7 lead is a one-lead spike (ECON-LT2 fail); and the "
        "indicator is empirically LAGGING. The defensible number is the "
        "max drawdown (−8.1% vs −23.9%) at essentially buy-and-hold's "
        "return — read the Sharpe as volatility avoidance, not stock-"
        "picking skill. Sharpe ratios use monthly √12 annualization."
    )

    HERO_TITLE = "Builder Confidence (NAHB HMI) vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — the NAHB "
        "HMI level (0-100, monthly) and the S&P 500 (SPY) on a common "
        "time axis, NBER recessions shaded. Watch the big swings: the "
        "2005-09 housing bust (HMI ~70s → record-low 8), the 2020 COVID "
        "whipsaw (30 → record 90), and the 2022 rate shock (83 → 31). "
        "Sentiment swings are huge — but the statistical tests say the "
        "market's moves help predict the mood, more than the mood "
        "predicts the market."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Builder-Sentiment Quartile"
    REGIME_CHART_NAME = "regime_stats"
    REGIME_CAPTION = (
        "What this shows: concurrent S&P 500 (SPY) "
        "performance in each quartile of the HMI, from most pessimistic "
        "(Q1) to most optimistic (Q4) — annualized Sharpe and return. The "
        "pattern is NON-MONOTONIC: Q2 is best (Sharpe 1.47), Q3 worst "
        "(0.27), with Q1 (0.74) and Q4 (0.71) in between — no clean "
        "'confident builders = good market' story. Descriptive and "
        "concurrent, not a tradable lead."
    )

    NARRATIVE_SECTION_1 = """
### Builder mood: famous, volatile — and it follows

The NAHB/Wells Fargo Housing Market Index has asked home builders every
month since 1985 how the single-family market feels — a 0-100 confidence
score (this pair's tradable sample starts in 1993, when SPY begins). It
is famous for one episode: the 2005-09 housing bust, when the index slid
from the 70s to a record-low 8 in January 2009. Housing, the folklore
says, IS the business cycle — so builder sentiment ought to lead the
stock market. That is the hypothesis this pair tests.

What the tests found instead — the causality mostly runs the OTHER way:
SPY Granger-causes the HMI at ALL 12 tested monthly lags (Toda-Yamamoto,
p ≈ 0.000 at lags 1-3); the HMI Granger-causes SPY at lag 5 only
(p = 0.0279, with lag 1 borderline at 0.0546). Transfer entropy agrees and
is starker: information flow SPY→HMI is decisive (p = 0.000), HMI→SPY is
absent (p = 0.386). The pre-whitened CCF shows only scattered, borderline
bars on both sides. And the era battery is null in ALL FOUR eras since
1993 (pre-GFC, GFC-bust, QE era, post-COVID; no p < 0.31) — there is no
era in which builder mood reliably predicted next-month stock returns.

**What this means:** builders read the same economy the market has
already priced — and their mood is itself moved by the market. The HMI is
a rear-view mirror with a megaphone: dramatic, headline-grabbing, and
late. This is now the third sentiment-flavored indicator in this catalog
(after the wage-growth ECI pair) where the stock market turns out to be
the leading indicator of the survey rather than the other way around —
an instructive pattern: surveys aggregate what markets have already
priced.

<!-- expander: What exactly is the NAHB Housing Market Index? -->
The NAHB/Wells Fargo Housing Market Index is a
monthly survey of home builders scoring current single-family sales,
sales expectations six months ahead, and buyer traffic, combined into a
0-100 diffusion index (above 50 = more builders rate conditions good than
poor). It is released mid-month FOR the current month, so it is one of
the timeliest housing gauges — even a zero-month lag would be
lookahead-free, though this pair's tournament floors the lead grid at L1
by fleet convention. Sourced from the project Data Master (sheet WFHMI);
FRED delisted the NAHBHMI series for licensing, and the static extract
ends 2025-10.
<!-- /expander -->

### A long test window — and what survived it

One thing this pair has that most recent pairs do not: time. Its
out-of-sample window is 98 months (~8.2 years, 2017-09 → 2025-10) — the
best OOS window of the recent pairs and comfortably above the 5-year
reliability floor — spanning the 2018 volatility shocks, COVID, the 2021
housing boom, the 2022 rate shock (HMI 83 → 31) and the 2023-25
high-rate regime. That strengthens the sample-size arithmetic. It does
not rescue the causality verdict, and the winning rule carries its own
fragility flags, detailed below.
"""

    # ALL FOUR history zooms exist for this pair (dotcom / gfc / covid /
    # inflation_2022). rolling_sharpe_cp + rolling_granger are chart-skipped
    # (skip records exist) — do NOT reference them.
    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Bust (2000–2002)",
            "narrative": (
                "The dot-com bear was a tech-led, non-housing recession: "
                "builder sentiment held comparatively high while SPY fell "
                "for roughly two and a half years — housing wasn't the "
                "epicentre, and mood and market simply decoupled. The "
                "rolling-p25 rule whipsawed through the noise rather than "
                "calling the bear (broker log: 2000-05 SELL → 2001-10 BUY "
                "→ 2002-05 SELL → 2002-07 BUY)."
            ),
            "caption": (
                "A tech-led bear that housing sentiment largely sat out "
                "— decoupling, not leadership"
            ),
        },
        {
            "slug": "gfc",
            "title": "Housing Bust and GFC (2006–2009)",
            "narrative": (
                "The one episode where the housing-leads story LOOKS "
                "right: the HMI turned down from the 70s in 2005, was "
                "collapsing roughly two years before the equity peak "
                "(Oct-2007), and bottomed at a record 8 in January 2009 — "
                "AFTER the market crash was well underway. The broker log "
                "shows the rule stepping to cash on 2006-06-30 and "
                "largely side-stepping 2008's worst (a brief 2008-01 → "
                "2008-08 re-entry aside); the honest counterweight is "
                "that this one spectacular episode does not survive the "
                "full-sample tests — the Granger/TE verdict stays "
                "reverse-dominant and the era battery is null even in "
                "the GFC-bust era (diff_12m r = 0.12, p = 0.31)."
            ),
            "caption": (
                "Builder mood collapsed ~2 years before equities — a "
                "one-off the full-sample tests refuse to generalize"
            ),
        },
        {
            "slug": "covid",
            "title": "COVID Whipsaw (2020)",
            "narrative": (
                "The HMI crashed to 30 in April 2020 and V-recovered to "
                "a record 90 by November 2020 on the rates-driven "
                "housing boom — but the equity crash and rebound "
                "happened FIRST, inside two months; sentiment chased the "
                "market in both directions. This is the only stress "
                "episode with validated strategy data (annualized Sharpe "
                "1.70 across the window, max drawdown −6.1%, per "
                "subperiod_sharpe.csv)."
            ),
            "caption": (
                "Sentiment chased the market down and up — a whipsaw "
                "the market traded first"
            ),
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rate Shock",
            "narrative": (
                "Mortgage rates doubled and the HMI collapsed 83 → 31 "
                "over 2022 while equities de-rated CONCURRENTLY — no "
                "lead on either side. The 12-month point-change signal "
                "went deeply negative and the rolling-p25 rule held cash "
                "through much of the bear — the single episode that "
                "contributes most of the OOS drawdown advantage "
                "(−8.1% vs −23.9%)."
            ),
            "caption": (
                "Builder mood and equities fell together in 2022 — the "
                "cash-step here is where the drawdown advantage was "
                "earned"
            ),
        },
    ]

    NARRATIVE_SECTION_2 = """
### "Lagging" — so what is the strategy actually doing?

How can a lagging indicator produce a high-scoring rule? Because the
rule does not forecast; it REACTS. When the 12-month change in builder
mood is deeply negative (below its rolling 25th percentile), stress is
usually already underway — stepping to cash then is damage control, not
prediction. Over 2017-2025 that reaction cut the worst drawdown to −8.1%
vs −23.9% while matching buy-and-hold's return (15.2% vs 15.4% a year).
The Sharpe gap (1.43 vs 0.94) is entirely volatility avoidance.

### What the search surfaced: a long/cash candidate, honestly labelled

Across **17,856 strategy combinations** (12,980 valid)
on the monthly lead grid L1..L12, the best rule: LONG the S&P 500 (SPY)
when the 7-month-lagged 12-month point-change in the HMI is above its
rolling 25th-percentile threshold (60-month lookback); CASH when below.
Procyclical long/cash. OOS Sharpe 1.43 vs 0.94, max drawdown −8.1% vs
−23.9%, annualized return 15.2% vs 15.4%.

Non-negotiable context, stated here rather than in a footnote:

- **The causality runs backwards.** SPY→HMI at all 12 lags; HMI→SPY at
  one isolated lag; transfer entropy reverse-only; era battery null in
  all four eras since 1993.
- **The L7 lead is a SPIKE, not a ridge.** The winner's own signal scores
  1.00 at L6 and 0.93 at L8 vs 1.43 at L7 — adjacent-lead durability
  FAILS (ECON-LT2). A robust mechanism should not care whether the
  signal is 6, 7, or 8 months old.
- **Not significant.** Bootstrap p = 0.1272 vs resampled buy-and-hold.
- **Return did NOT beat buy-and-hold.** 15.2% vs 15.4% annualized — the
  entire edge is lower volatility and shallower drawdown.
- **One validated stress episode.** Of the standard episodes, only COVID
  falls inside usable strategy history (durability
  'conditionally_durable'); dot-com and GFC are insufficient_data for
  the OOS strategy record.
- **Static, stale source.** Data Master ends 2025-10 (~9 months stale at
  run date); live use requires a data refresh path.

Mitigating (report honestly in BOTH directions): the 8.2-year OOS window
is ABOVE the 5-year floor; IS Sharpe 0.75 vs OOS 1.43 (no sign flip, no
in-sample loss); the rolling correlation is sign_stable (0.819); and no
structural break is flagged (Quandt-Andrews p = 0.35). That makes this a
more respectable candidate than the recent short-window sentiment pairs
— but still a candidate.

### What this means for investors

- Do not use builder sentiment as an early-warning signal — the tests
  say the market warns about builder mood, not the reverse.
- The defensible use is DEFENSIVE: a deeply negative 12-month change in
  the HMI has coincided with stress regimes worth de-risking into —
  after the fact, as damage control.
- Judge the rule by its drawdown (−8.1% vs −23.9%), not its Sharpe; the
  return match with buy-and-hold means it never generated excess return,
  it avoided losses.
"""

    TRANSITION_TEXT = (
        "One question, attacked several independent "
        "ways: *does builder sentiment carry information about future "
        "S&P 500 (SPY) returns — or does the market move first?* Methods "
        "that agree from different angles are far more convincing than "
        "any single test. Here they converge: the market leads builder "
        "mood; the mood's one forward blip (lag 5) is isolated and "
        "uncorroborated."
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
        "Pearson, Spearman, and distance correlations "
        "between every HMI transform (level, month/3-month/12-month "
        "point-changes, YoY %, z-scores, acceleration, regime states) and "
        "forward SPY returns at 1-, 3-, 6- and 12-month horizons."
    ),
    question=(
        "Is there any raw statistical association between builder "
        "sentiment today and stock returns over the coming months?"
    ),
    how_to_read=(
        "Rows are signal transforms, columns are forward-return horizons "
        "in MONTHS; each cell's color shows the correlation — deeper "
        "color = stronger. Pale cells mean no association."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        "What this shows: correlations between HMI "
        "transforms and forward S&P 500 (SPY) returns across monthly "
        "horizons. The grid is weak throughout — e.g. the raw level vs "
        "1-month-forward Pearson is 0.02 (p = 0.69) on 393 months. "
        "Nothing here supports a tradable linear association."
    ),
    observation=(
        "No transform shows a strong linear "
        "association with forward SPY at any monthly horizon (full grid "
        "of 208 signal × horizon × metric cells in correlations.csv). "
        "The raw level vs 1-month-forward cell is r = 0.02, p = 0.69."
    ),
    deep_dive_title="Why treat the heatmap as triage rather than proof?",
    deep_dive_content=(
        "Overlapping forward returns induce serial "
        "correlation in the cells, and the HMI is an integer-valued "
        "bounded 0-100 index, so %-change transforms are level-dependent. "
        "Treat the heatmap as descriptive triage; the formal tests below "
        "carry the inferential weight."
    ),
    interpretation=(
        "The tradeable-horizon cells are weak — "
        "consistent with a sentiment gauge that reflects conditions the "
        "market has already priced."
    ),
    key_message=(
        "At every tradeable monthly horizon the raw "
        "association between builder sentiment and future stock returns "
        "is weak."
    ),
)


CORRELATION_LEAD_VIEW_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Analysis",
    method_theory=(
        "For a monthly-rebalanced strategy the "
        "decision is: how stale should the signal be allowed to get "
        "before we trade on it? This block computes Pearson correlations "
        "between each HMI transform lagged L = 0…12 MONTHS and the SPY "
        "1-month forward return. **Caveat for this pair:** the causality "
        "tests find the information flowing the OTHER way (SPY→HMI), so "
        "this lead view is expected to show little genuine predictive "
        "content at any lead — honest reporting requires us to show "
        "that, not hide it."
    ),
    question=(
        "Does lagging the sentiment signal by any number of months "
        "recover real predictive content for SPY — or does the lagging "
        "character mean no lead works?"
    ),
    how_to_read=(
        "Rows are HMI signal variants; columns are signal lead in MONTHS "
        "(L0 = contemporaneous, L12 = one year ago). Forward horizon "
        "fixed at 1 month. Cell shading is Pearson r against "
        "`spy_fwd_1m`."
    ),
    chart_name="correlations_lead_view",
    chart_caption=(
        "Pearson correlations between **signal lagged L months** and "
        "**SPY 1-month forward return**. Cells are tiny at every lead "
        "(best |r| = 0.12 anywhere on the grid); the traded `diff_12m` "
        "row never exceeds r = +0.09 at any lead — weak, and the "
        "signature of a lagging series with no reliable predictive lead."
    ),
    observation=(
        "Reading across the rows, correlations are small everywhere "
        "(per lead_correlation_20260706.csv the best cell on the whole "
        "13-transform × L0..L12 grid is |r| = 0.12). The traded "
        "12-month point-change (`diff_12m`) reads r = +0.084 at the "
        "winner's L7 (its best is +0.089 at L4); the raw level never "
        "exceeds +0.032 at any lead. **There is no lead at which "
        "builder sentiment cleanly predicts next-month SPY.**"
    ),
    interpretation=(
        "This is an honest near-null result, and "
        "stating it is the point. **In plain English:** builder mood "
        "follows the economy and the market rather than leading them, so "
        "you cannot reliably trade SPY by lagging the sentiment signal. "
        "The strategy on the next page earns its keep (if at all) as a "
        "defensive damage-control overlay, and the lead view makes that "
        "limitation explicit."
    ),
    key_message=(
        "No lead works cleanly: the traded 12-month point-change never "
        "exceeds r = +0.09 across L = 0…12 months. "
        "This corroborates the lagging verdict — builder mood responds "
        "to the cycle, it does not lead SPY."
    ),
)


LEAD_TOURNAMENT_BLOCK = dict(
    chart_status="ready",
    method_name="Lead Tournament",
    method_theory=(
        "This block sweeps the MONTHLY lead grid "
        "L = 1…12 and plots the best OOS Sharpe at each lead against all "
        "valid combos; the reference line is SPY buy-and-hold (Sharpe "
        "0.94, √12 monthly annualization). Read it alongside the lagging "
        "verdict: any Sharpe here comes from a search over 17,856 "
        "combinations, not from forward causality."
    ),
    question=(
        "Where does the traded 7-month lead sit on the sweep — and is "
        "its Sharpe a robust ridge or a fragile one-lead spike?"
    ),
    how_to_read=(
        "Bars: max OOS Sharpe at each monthly lead (L1..L12). "
        "Strip/cloud: valid combinations at that lead. A tall thin spike "
        "is a single combo; a flat-but-wide cloud is a more robust "
        "regime.\n\n"
        "One honesty note before the chart. The bars are a "
        "best-of-search ENVELOPE — at each lead they show the single "
        "best OOS Sharpe that *any* signal achieved, so of course they "
        "all clear buy-and-hold; that uniform strength is what selection "
        "bias looks like, not evidence that every lead works. The honest "
        "comparison is the published winner's OWN signal traced across "
        "leads (lead_winner_curve_20260706.csv): 0.79 at L1, 0.69-0.85 "
        "across L2-L4, 1.05 at L5, 1.00 at L6, then the published peak "
        "of 1.43 at L7 — collapsing straight back to 0.93 at L8 and "
        "decaying to 0.43-0.63 by L10-L12. The winner's own curve does "
        "peak at its published L7, so the choice is internally "
        "consistent — but a 1.43 sandwiched between a 1.00 and a 0.93 "
        "is a SPIKE, not a ridge (adjacent-lead durability FAILS, "
        "ECON-LT2), and the search-conditioned bootstrap p = 0.1272 is "
        "not significant. A rule whose merit vanishes if the signal is "
        "one month fresher or one month staler is a pattern to be "
        "suspicious of — not evidence of a forecasting mechanism."
    ),
    chart_name="lead_sharpe_distribution",
    chart_caption=(
        "Best OOS Sharpe per monthly lead (bars) "
        "with the full distribution. The published winner sits at L7 "
        "months (1.43); its own signal scores 1.00 at L6 and 0.93 at L8 "
        "— a one-lead spike. On a search of 17,856 combinations with the "
        "causality running SPY→HMI, read any Sharpe here as "
        "search-conditioned and descriptive."
    ),
    observation=(
        "The published winner (`diff_12m / "
        "T2_roll_p25 / P1_long_cash` pro, L7 months, LB60, OOS Sharpe "
        "1.43) is the grid maximum, and the winner's own lead-curve "
        "peaks at the published L7 (no staleness). But the peak is not "
        "durable to its neighbours: L6 1.00, L7 1.43, L8 0.93 "
        "(ECON-LT2 adjacent-lead durability FAIL). The runner-up is a "
        "different signal entirely (level_zscore_60m at L6, 1.42) — "
        "near-identical score from a different construction, the "
        "classic signature of a search surface rather than a mechanism."
    ),
    interpretation=(
        "The honest summary: an 8.2-year OOS window "
        "earns this pair more sample-size credibility than most, but the "
        "one-lead spike, the n.s. bootstrap (p = 0.1272), and the "
        "reverse-dominant causality all point the same way — the traded "
        "L7 Sharpe rides a search-conditioned pattern. Weight it "
        "accordingly. Honesty over polish."
    ),
    key_message=(
        "The published L7 winner (1.43) is a spike, "
        "not a ridge — its own signal drops to 1.00 at L6 and 0.93 at "
        "L8. Treat the edge as descriptive, not predictive."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality (Toda-Yamamoto)",
    method_theory=(
        "Granger causality (a statistical test of "
        "whether one series helps forecast another beyond the other's "
        "own history), in the Toda-Yamamoto form that stays valid even "
        "if the series' trends are imperfectly removed. Run on monthly "
        "data, lags 1-12 months, in both directions."
    ),
    question="Who moves first — builder sentiment or the stock market?",
    how_to_read=(
        "Bars show the test statistic at each lag from 1 to 12 MONTHS, "
        "one panel per direction; bars clearing the dashed significance "
        "line indicate forecasting power at that lag."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: Granger F-statistics by "
        "monthly lag, both directions, with the 5% critical line. The "
        "SPY → HMI panel clears the line at EVERY one of the 12 lags "
        "(F = 47.2 at lag 1, p ≈ 0.000); the HMI → SPY panel clears it "
        "at lag 5 only (p = 0.0279)."
    ),
    observation=(
        "In the sentiment → SPY direction, exactly "
        "one of 12 lags is significant (lag 5, p = 0.0279; lag 1 is "
        "borderline at 0.0546, the rest range 0.06-0.24). In the "
        "SPY → sentiment direction, EVERY lag from 1 to 12 is "
        "significant, with enormous statistics at short lags (F = 47.2 "
        "at lag 1). The asymmetry is overwhelming."
    ),
    deep_dive_title="Does the lag-5 blip rescue a leading-indicator reading?",
    deep_dive_content=(
        "One significant lag out of 12, at the 2.8% "
        "level, with 12 tests run, is roughly what multiple testing "
        "hands out for free — and no other method corroborates it "
        "(transfer entropy forward p = 0.386; era battery null "
        "everywhere; lead correlations ≤ 0.10). We report it, and we "
        "decline to build a story on it. The reverse direction needs no "
        "such charity: significant at every lag with p ≈ 0."
    ),
    interpretation=(
        "The market forecasts builder mood — "
        "powerfully, at every tested horizon. Builder mood forecasts the "
        "market at one isolated lag that nothing else corroborates. This "
        "is the fingerprint of a lagging indicator, and it is the "
        "headline finding of this pair."
    ),
    key_message=(
        "The stock market Granger-causes builder "
        "sentiment at all 12 tested monthly lags; sentiment "
        "Granger-causes the market at one isolated lag (5) only. "
        "Sentiment follows equities."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "A pre-whitened Cross-Correlation Function "
        "(CCF) — correlation between the two series at every monthly "
        "offset from −24 to +24, after filtering each series' own "
        "autocorrelation (AR(12)) so trends cannot masquerade as "
        "lead-lag structure."
    ),
    question=(
        "At which specific monthly offsets, if any, do the two series "
        "echo each other?"
    ),
    how_to_read=(
        "The X-axis is the offset in MONTHS — positive offsets mean "
        "sentiment moves before stocks, negative offsets mean stocks "
        "move before sentiment. Bars outside the dashed band are "
        "significant at 95% confidence."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: pre-whitened "
        "cross-correlation at 49 monthly offsets with 95% confidence "
        "bands (±0.10). A handful of bars just graze the band on both "
        "sides (sentiment-leads offsets +1, +5, +12, +13; market-leads "
        "offsets −1, −10) — all barely past |r| ≈ 0.10-0.14, scattered "
        "rather than clustered."
    ),
    observation=(
        "Of 49 offsets, six bars marginally clear "
        "the ±0.1004 band — split across both sides and none reaching "
        "|r| = 0.14. With ~49 tests at the 5% level, two to three false "
        "positives are expected by chance; there is no coherent cluster "
        "of lead-side significance."
    ),
    interpretation=(
        "After stripping each series' own memory, "
        "no convincing lead-lag echo survives on either side — the "
        "scattered borderline bars are why Evan's formal classification "
        "is 'bidirectional', and why the DOMINANT direction (from the "
        "Granger and transfer-entropy tests) still reads market → "
        "sentiment."
    ),
    key_message=(
        "Across 49 monthly offsets there is no "
        "coherent window in which builder sentiment foreshadows stock "
        "returns — only scattered borderline echoes on both sides."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections (a horizon-by-horizon "
        "regression technique that traces how one variable responds "
        "after a movement in another), with HAC standard errors robust "
        "to overlapping monthly horizons."
    ),
    question=(
        "If builder sentiment jumps today, where is the stock market 1, "
        "3, 6, and 12 months later?"
    ),
    how_to_read=(
        "Each panel plots the estimated response (line) with its "
        "confidence band (shading) across monthly horizons; a band that "
        "straddles zero means no detectable effect."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: impulse-response panels, "
        "forward and reverse. In the sentiment → SPY panel the "
        "confidence band straddles zero at every horizon (p = 0.78, "
        "0.95, 0.88, 0.93 at 1, 3, 6, 12 months); the reverse panel is "
        "also insignificant horizon-by-horizon (smallest p = 0.11)."
    ),
    observation=(
        "In the sentiment → SPY panel the band "
        "straddles zero at 1, 3, 6, and 12 months — point estimates are "
        "essentially zero. The reverse direction is not significant at "
        "any single horizon either (the Granger result pools lags "
        "jointly, which is where the SPY → HMI power shows up)."
    ),
    interpretation=(
        "At the horizons a monthly strategy "
        "actually trades, a builder-sentiment surprise tells you nothing "
        "statistically useful about where stocks will be. Nothing here "
        "rescues a forward-looking reading of the indicator."
    ),
    key_message=(
        "A jump in builder sentiment carries no "
        "statistically detectable information about stock returns over "
        "the following year."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy — a model-free measure of "
        "directed information flow that can detect *non-linear* "
        "relationships ordinary correlation misses (estimated on "
        "tercile-binned monthly data with 500 permutations; the HMI's "
        "integer values make tie handling explicit)."
    ),
    question=(
        "Could builder sentiment predict stocks in some curvy, "
        "non-linear way the linear tests can't see?"
    ),
    how_to_read=(
        "Two bars — one per direction; the annotation shows each bar's "
        "permutation p-value. A small p-value (under 0.05) would "
        "indicate genuine information flow."
    ),
    chart_name=TRANSFER_ENTROPY_CHART_NAME,
    chart_caption=(
        "What this shows: bidirectional transfer "
        "entropy with permutation p-values. Sentiment → SPY: p = 0.386 "
        "(nothing). SPY → sentiment: p = 0.000 (decisive) — the "
        "information flows ONLY in the reverse direction."
    ),
    observation=(
        "Builder sentiment → SPY: TE = 0.017, "
        "p = 0.386 — clearly insignificant. SPY → builder sentiment: "
        "TE = 0.045, p = 0.000 — unambiguous. This is the starkest "
        "one-way reading in the pair's whole battery."
    ),
    interpretation=(
        "No non-linear channel rescues the "
        "indicator: even model-free information flow runs exclusively "
        "from the market to builder mood — corroborating the Granger "
        "asymmetry with a method that assumes nothing about linearity."
    ),
    key_message=(
        "There is no non-linear escape hatch — "
        "model-free information flow is reverse-only: stocks inform "
        "builder mood, never the other way."
    ),
)


QUANTILE_BLOCK = dict(
    chart_status="ready",
    method_name="Quantile Regression",
    method_theory=(
        "Quantile regression — instead of asking "
        "how builder sentiment affects the *average* future return, it "
        "asks how it affects the *worst* and *best* outcomes (the "
        "tails), where risk signals usually earn their keep."
    ),
    question=(
        "Does builder sentiment at least predict tail risk — the really "
        "bad months — even if it can't predict the average?"
    ),
    how_to_read=(
        "The X-axis runs across outcome percentiles (5th = worst "
        "months, 95th = best); the line is the estimated effect at each "
        "percentile with its confidence band. A risk signal typically "
        "shows a significant effect at the left tail."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: quantile-regression "
        "coefficient by percentile with confidence band. The band "
        "straddles zero at every percentile from the 5th to the 95th — "
        "no tail-risk channel (the closest is the 10th percentile at "
        "p = 0.077, still short of 5%)."
    ),
    observation=(
        "The confidence band straddles zero at all "
        "seven tested percentiles (p-values from 0.077 at the 10th to "
        "0.95 at the 75th). The mildly positive left-tail point "
        "estimates never reach significance."
    ),
    interpretation=(
        "Many indicators fail at the mean but work "
        "at the left tail. This one fails at both — builder sentiment "
        "does not flag elevated crash risk either. (Note the irony for "
        "the strategy page: the rule's OOS drawdown virtue is a "
        "descriptive, regime-coincidence property, not a tail-forecast "
        "the quantile test can find.)"
    ),
    key_message=(
        "Builder sentiment predicts neither average "
        "stock returns nor tail risk."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Context (HMM and Quartiles)",
    method_theory=(
        "A two-state Hidden Markov Model (HMM — a "
        "statistical model that infers unobserved 'optimism' vs "
        "'pessimism' regimes from the data's behavior) fitted to the "
        "HMI series, plus a simple sort of history into quartiles of "
        "concurrent builder sentiment with SPY performance in each."
    ),
    question=(
        "Even without prediction, do states of builder mood coincide "
        "with systematically different stock-market environments?"
    ),
    how_to_read=(
        "The HMM panel shades periods by inferred regime probability "
        "over time; the quartile chart on the Story page shows "
        "concurrent SPY Sharpe/return in four bars, sorted from most "
        "pessimistic (Q1) to most optimistic (Q4) builder sentiment."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: HMM-inferred builder-"
        "pessimism regime probability over time, NBER recessions "
        "shaded. The pessimism state (mean HMI ≈ 39, ~42% of the "
        "sample) captures the GFC housing bust and the 2022-25 "
        "high-rate era; mean monthly SPY returns were actually HIGHER "
        "in the pessimism state (1.09% vs 0.84%) — no simple "
        "'confidence = good market' mapping."
    ),
    observation=(
        "The HMM separates a builder-optimism state "
        "(mean HMI ≈ 61, ~58% of months) from a pessimism state "
        "(≈ 39, ~42%). Mean monthly SPY returns were slightly higher in "
        "the PESSIMISM state (1.09% vs 0.84%, at higher vol), and the "
        "quartile sort is non-monotonic: Q2 Sharpe 1.47, Q3 0.27, with "
        "Q1 0.74 and Q4 0.71 — no clean concurrent gradient in either "
        "direction."
    ),
    deep_dive_title="How stable is the relationship over time?",
    deep_dive_content=(
        "More stable than most lagging pairs, for "
        "what it's worth: the rolling 36-month correlation is "
        "sign_stable (0.819 sign-stability), and Quandt-Andrews does "
        "NOT flag a structural break (sup-F 2.96 at 2009-03, bootstrap "
        "p = 0.35). But 'stably weak' is still weak: the era battery "
        "finds no significant signal-return correlation in any of the "
        "four eras since 1993 (all p ≥ 0.31)."
    ),
    interpretation=(
        "Builder-mood states describe the housing "
        "cycle, not the equity outlook: even concurrently, the "
        "quartile pattern is non-monotonic and the state-conditional "
        "return gap runs mildly the 'wrong' way. Descriptive context, "
        "not an edge."
    ),
    key_message=(
        "Builder-sentiment regimes track the "
        "housing cycle but map onto equity performance non-monotonically "
        "— there is no clean 'optimistic builders = good market' "
        "gradient, concurrent or leading."
    ),
)


TOURNAMENT_DIST_BLOCK = dict(
    chart_status="ready",
    method_name="Search Distribution",
    method_theory=(
        "The distribution of out-of-sample Sharpe "
        "ratios across all 12,980 valid strategy combinations in the "
        "monthly tournament — the context that shows how far the "
        "published winner sits into the right tail of its own search."
    ),
    question=(
        "Is the winner's Sharpe typical of what this indicator supports "
        "— or the extreme right tail of a search over thousands of "
        "variants?"
    ),
    how_to_read=(
        "Histogram of OOS Sharpe across valid combos; vertical markers "
        "show the median valid combo (0.79), buy-and-hold (0.94), and "
        "the published winner (1.43). All figures use monthly √12 "
        "annualization on the 98-month OOS window."
    ),
    chart_name=TOURNAMENT_DIST_CHART_NAME,
    chart_caption=(
        "Distribution of OOS Sharpe across 12,980 "
        "valid combos with median (0.79), buy-and-hold (0.94) and the "
        "winner (1.43) marked — the winner is the right tail of a "
        "17,856-combination search, not an out-of-sample forecast."
    ),
    observation=(
        "The median valid combination (0.79) "
        "UNDERPERFORMS buy-and-hold (0.94): the typical rule built on "
        "this indicator subtracts value. The published winner (1.43) is "
        "the distribution's extreme, its bootstrap p-value against "
        "resampled buy-and-hold is 0.1272 (n.s.), and the top four "
        "search results (1.43, 1.42, 1.41, 1.39) come from FOUR "
        "different signal/threshold constructions — a crowded, "
        "flat-topped search surface."
    ),
    interpretation=(
        "When the median strategy loses to "
        "buy-and-hold and near-identical scores come from unrelated "
        "constructions, the correct prior is that the maximum is "
        "selection effect. This is the best-of-N disclosure rendered as "
        "a picture."
    ),
    key_message=(
        "The typical HMI-based rule underperforms "
        "buy-and-hold; the published winner is the right tail of a "
        "17,856-combination search (bootstrap p = 0.1272, n.s.)."
    ),
)


# Step C #202 (KS): two leaderboard rows — `yoy` and `diff_12m`, both at the
# `T4_zero` threshold, 7-month lead — post identical Sharpe/return/drawdown/
# turnover/win-rate. Rendered as a caption under the leaderboard via the
# LEADERBOARD_NOTE_MD hook in page_templates. Explains it is mathematically
# expected (equal-at-zero transforms), not a data error.
LEADERBOARD_NOTE_MD = (
    "**Why some rows share identical numbers.** A few rows show the *same* "
    "Sharpe, return, drawdown, turnover and win rate as another row with a "
    "different signal name — e.g. `yoy` and `diff_12m` (both at the `T4_zero` "
    "threshold, 7-month lead), and likewise `mom3m` and `diff_3m`. This is "
    "expected, not a data error. At a **zero** threshold, a 12-month *percentage* "
    "change and a 12-month *point* change of the same index cross zero at exactly "
    "the same moment — both are really asking \"is HMI above where it was 12 "
    "months ago?\" — so they hold identical positions and post identical results. "
    "They are the same rule under two names: they pad the raw combination count "
    "but are not independent strategies. (Only the zero threshold does this; "
    "percentile and z-score thresholds separate the two transforms again.)"
)


EVIDENCE_METHOD_BLOCKS = {
    "title": (
        "The tests point one way: the market leads, builder mood follows"
    ),
    "overview": (
        "*One question, attacked several independent "
        "ways: does builder sentiment carry information about future "
        "S&P 500 (SPY) returns — or does the market move first? Methods "
        "that agree from different angles are far more convincing than "
        "any single test. Here they converge on a directional answer: "
        "SPY predicts the HMI at all 12 tested monthly lags; the HMI "
        "predicts SPY at one isolated lag that nothing else "
        "corroborates.*\n\n"
        "All statistics computed on MONTHLY data, analytical sample "
        "1993-02 → 2025-10 (393 months), from "
        "`results/wells_fargo_housing_spy/core_models_20260706/`."
    ),
    "plain_english": (
        "This section shows the statistical evidence "
        "on whether builder sentiment predicts the stock market. The "
        "lead-lag tests — correlation, Granger causality, pre-whitened "
        "cross-correlation, local projections, and transfer entropy — "
        "converge on a reversal: the S&P 500 (SPY) helps predict builder "
        "mood at every tested lag out to a year, while builder mood "
        "helps predict the market at a single isolated 5-month lag with "
        "no corroboration from any other method. The era battery finds "
        "no era since 1993 in which the relationship was significant. "
        "Builder sentiment is a lagging indicator; the strategy on the "
        "next page should be read as a defensive, after-the-fact "
        "overlay, not a forecast."
    ),
    # Row counts VERIFIED by wc -l at authoring time (2026-07-06);
    # counts exclude the header row.
    "downloads": [
        {"label": "Granger causality (Toda-Yamamoto), both directions × 12 monthly lags (24 rows)",
         "path": "results/wells_fargo_housing_spy/core_models_20260706/granger_causality.csv"},
        {"label": "Granger F-statistics by lag, HMI → SPY (12 rows)",
         "path": "results/wells_fargo_housing_spy/granger_by_lag.csv"},
        {"label": "Correlation battery, signal × horizon × metric (208 rows)",
         "path": "results/wells_fargo_housing_spy/core_models_20260706/correlations.csv"},
        {"label": "Pre-whitened CCF, monthly offsets −24..+24 (49 rows)",
         "path": "results/wells_fargo_housing_spy/core_models_20260706/ccf_prewhitened.csv"},
        {"label": "Local projections, forward + reverse × 4 monthly horizons (8 rows)",
         "path": "results/wells_fargo_housing_spy/core_models_20260706/local_projections.csv"},
        {"label": "Transfer entropy, both directions (2 rows)",
         "path": "results/wells_fargo_housing_spy/core_models_20260706/transfer_entropy.csv"},
        {"label": "Quantile regression, 7 quantiles (7 rows)",
         "path": "results/wells_fargo_housing_spy/core_models_20260706/quantile_regression.csv"},
        {"label": "Era-battery correlations, 2 signals × 4 eras (8 rows)",
         "path": "results/wells_fargo_housing_spy/core_models_20260706/era_correlations.csv"},
        {"label": "Lead-correlation grid, 13 transforms × leads L0..L12 months (12 rows)",
         "path": "results/wells_fargo_housing_spy/lead_correlation_20260706.csv"},
        {"label": "Regime quartile returns, Q1–Q4 (4 rows)",
         "path": "results/wells_fargo_housing_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe, episodes (4 rows)",
         "path": "results/wells_fargo_housing_spy/subperiod_sharpe.csv"},
        {"label": "Rolling 36-month correlation (326 rows)",
         "path": "results/wells_fargo_housing_spy/rolling_correlation_wells_fargo_housing_spy.csv"},
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
        "The statistical tests above ask whether the "
        "indicator *predicts* — and answer no (the causality runs the "
        "other way, and no era since 1993 shows a significant "
        "relationship). The tournament asks a more pragmatic question: "
        "across every reasonable MONTHLY trading rule you could build "
        "from this series, does *any* of them beat simply holding the "
        "S&P 500 (SPY)?\n\n"
        "We tested a grid of **17,856 strategy combinations** — 13 "
        "signal transforms × 12 threshold schemes × 6 strategy families "
        "× monthly leads L1..L12 — of which **12,980 passed validity "
        "filters** (the buy-and-hold benchmark row is excluded from "
        "this count). The median valid combination scored an OOS Sharpe "
        "of 0.79, BELOW buy-and-hold's 0.94. The headline rule on the "
        "Strategy page is the search maximum (1.43) on a 98-MONTH "
        "(~8.2-year) out-of-sample window — a long window by fleet "
        "standards — with bootstrap p = 0.1272 and a one-lead-spike "
        "L7. In plain English: the winner is a candidate found in "
        "search whose real virtue is its drawdown profile — not a "
        "validated forecasting edge."
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is "
        "lagging — the market moves first and builder mood follows. "
        "What remains is the pragmatic question the tournament "
        "answered: the next page shows the one candidate rule the "
        "search surfaced — a defensive long/cash overlay whose "
        "defensible virtue is drawdown reduction — with every fragility "
        "flag attached."
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = (
        "The Strategy: A Long/Cash Overlay Whose Virtue Is the Drawdown"
    )
    PAGE_SUBTITLE = (
        "— the search maximum on a LAGGING indicator: same return as "
        "buy-and-hold (15.2% vs 15.4% a year) with one-third of the "
        "worst drawdown (−8.1% vs −23.9%) over an 8.2-year OOS window. "
        "Sharpe 1.43 vs 0.94, but bootstrap p = 0.1272 (n.s.) and the "
        "L7 lead is a one-lead spike. No hold-out test has been run yet."
    )

    PLAIN_ENGLISH = (
        "The best rule from a 17,856-combination "
        "monthly search: hold the S&P 500 (SPY) when the 12-month change "
        "in builder sentiment — viewed with a 7-MONTH delay — sits above "
        "its rolling 25th-percentile threshold, and step to CASH when it "
        "sits below (i.e. only exit when builder mood has deteriorated "
        "unusually hard even by its own recent standards). Over the "
        "8.2-year test window (2017-2025) it MATCHED buy-and-hold's "
        "return (15.2% vs 15.4% a year) while cutting the worst "
        "peak-to-trough loss from −23.9% to −8.1% — that drawdown "
        "reduction is the whole story; the Sharpe edge (1.43 vs 0.94) is "
        "volatility avoidance, not extra profit. And the warning labels "
        "are real: the causality tests say the market leads builder mood "
        "(not the reverse), the rule's 7-month delay is a one-lead spike "
        "the neighbouring leads don't support, and the result fails the "
        "standard significance test (bootstrap p = 0.13). Read it as a "
        "defensive candidate found by search — its final exam on "
        "untouched data has not been run."
    )

    SIGNAL_RULE_MD = """
**Rule:** Hold the S&P 500 (SPY) **when the 7-MONTH-lagged 12-month point-change in the NAHB HMI (`diff_12m` — this month's builder-sentiment index minus its value 12 months earlier, in index points) is above its ROLLING 25th-percentile threshold (computed over the trailing 60 months; latest value −14.0). When it is below, hold CASH (0%).** This is a **procyclical long/cash** rule: it stays invested through normal and even mildly-deteriorating sentiment, and steps aside only when the 12-month mood change is deeply negative by its own recent standards. It never goes short. (Family: Long/Cash P1; signal `diff_12m`, rolling threshold T2_roll_p25 over LB60, lead L7 MONTHS — per `winner_summary.json`; `direction: procyclical`, confirmed against every row of `winner_trades_broker_style.csv`: BUY = position 0% → 100% when the lagged signal is above threshold, SELL = 100% → 0% when it is not.)

If-then form (evaluated once per month):
- **IF** the 7-month-old 12-month change in the HMI is above its rolling 25th percentile → **LONG SPY (100% invested)**.
- **ELSE** → **CASH (0%)**.

Search-phase results (2017-09-30 → 2025-10-31, 98 MONTHS ≈ 8.2 years — above the 5-year floor, but **no hold-out test yet**; Sharpe annualized by √12): OOS Sharpe 1.43 vs 0.94 buy-and-hold; annualized return 15.2% vs 15.4% (the rule did NOT out-earn the index); **maximum drawdown −8.1% vs −23.9% — the defensible virtue**; 16 trades in the OOS window (turnover 1.96/yr); monthly win rate 45%.

**Read this as a defensive candidate, not a validated edge.** The indicator is empirically LAGGING (the market predicts builder mood at all 12 tested lags, not the reverse), the L7 lead is a spike (L6 1.00 / L7 1.43 / L8 0.93 — adjacent-lead durability FAILS), and the result is not statistically significant (bootstrap p = 0.1272). This pair's `strategy_objective` (per `interpretation_metadata.json`) is **max_sharpe**, but the honest reading of what was maximized is drawdown avoidance through the 2018, 2020 and 2022 stress windows.
"""

    HOW_SIGNAL_IS_GENERATED_MD = """
No formulas — three steps:

**What changes in the world:** home builders' confidence in the
single-family market rises and falls with mortgage rates, buyer traffic
and the broader cycle. The NAHB/Wells Fargo survey scores that mood 0-100
every MONTH (released mid-month for the current month).

**What the signal measures:** each month, the rule takes the 12-month
point-change in the index (this month's reading minus a year ago — did
builder mood improve or deteriorate over the past year?) — as that
reading stood **seven months ago** (not a publication-lag necessity; L7
is the lead the tournament scored best, and its one-lead-spike shape is
itself a caution). It then asks whether that stale reading is above its
own rolling 25th percentile over the trailing five years.

**What decision it drives:** above the threshold (mood not unusually
deteriorated) → be LONG the market; below it (mood deteriorating hard
even by recent standards) → step to CASH. Because the causality tests
find the market leads builder mood, this is best understood as a
*stress-regime confirmation* that de-risks after trouble is underway —
damage control, not a forecast.
"""

    MANUAL_USE_MD = (
        "First, the framing: what follows describes "
        "how the backtested rule works so you can replicate and audit it "
        "— it is **not** a recommendation to trade it. This rule is a "
        "search-phase candidate (best of 12,980 valid; 98-month OOS; no "
        "hold-out test yet; bootstrap p = 0.1272, not significant at 5%; "
        "one-lead-spike L7; empirically LAGGING indicator; STATIC data "
        "source ending 2025-10). With that understood, the monthly "
        "routine — no code required — is:\n\n"
        "1. **Pull the sentiment series** — the NAHB/Wells Fargo Housing "
        "Market Index (published mid-month by NAHB; this project reads "
        "it from the Data Master workbook, sheet WFHMI, because FRED "
        "delisted the series for licensing).\n"
        "2. **Compute the 12-month point-change** — this month's index "
        "value minus the value 12 months earlier (index points, not %).\n"
        "3. **Apply the 7-month delay** — the reading the rule acts on "
        "this month is the 12-month change from seven months ago.\n"
        "4. **Compute the rolling threshold** — the 25th percentile of "
        "that same signal over the trailing 60 months (the latest "
        "rolling value is −14.0; see `winner_trade_log.csv` for the full "
        "signal/threshold path).\n"
        "5. **Compare** — is the delayed 12-month change above the "
        "rolling threshold?\n"
        "6. **Take the position** — above → LONG SPY (100%); below → "
        "CASH (0%). Re-evaluate once a MONTH.\n\n"
        "Remember the warning labels: lagging indicator (the causality "
        "runs the other way), one-lead-spike L7, not statistically "
        "significant, return only MATCHES buy-and-hold (the virtue is "
        "the −8.1% vs −23.9% drawdown) — and the source data is a "
        "static extract ending 2025-10."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    WALK_FORWARD_CAPTION = (
        "What this shows: rolling 24-month "
        "annualized Sharpe over the OOS window versus the reported "
        "headline 1.43. Read it as a stability sniff-test: the edge is "
        "episodic — it concentrates in the stress windows (2018, 2020, "
        "2022) where the cash-step avoided losses — not a steady "
        "month-in month-out advantage."
    )
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_scatter"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: all 17,856 tournament "
        "combinations by annual turnover vs OOS Sharpe (monthly √12 "
        "annualization); the star marks the published winner (1.43), "
        "the diamond buy-and-hold (0.94). Search-conditioned on a "
        "98-month window, bootstrap p = 0.1272 — the winner is the "
        "right tail of its own search, and the median valid combo "
        "(0.79) sits BELOW buy-and-hold."
    )

    # Cross-Period Consistency trio (Strategy → Confidence tab).
    # subperiod_sharpe uses the template default caption; the two below
    # carry pair-specific numbers.
    CROSS_PERIOD_CAPTIONS = {
        "rolling_correlation": (
            "How to read it: the indicator is the "
            "NAHB HMI signal; the target is SPY returns. The rolling "
            "36-month correlation tests whether their linear "
            "relationship is stable through time. For this pair the "
            "line is comparatively steady — sign-stability 0.819, "
            "verdict `sign_stable` — but steady around a WEAK level: "
            "stability of a near-zero relationship is not evidence of "
            "predictive power (the era battery is null in all four eras "
            "since 1993)."
        ),
        "structural_break": (
            "How to read it: the Quandt-Andrews "
            "test asks whether the sentiment-SPY relationship changed "
            "suddenly at some point in the sample. For this pair NO "
            "break is flagged (sup-F 2.96 at 2009-03-31, bootstrap "
            "p = 0.35): the relationship — weak as it is — has been "
            "consistent across the 1993-2025 sample. That is honest in "
            "both directions: no break to blame, and no era in which "
            "the signal secretly worked."
        ),
    }

    CAVEATS_MD = """
**Why we do not call this a validated edge** — flags, none softened (all from `winner_summary.json`, `evidence_status.json`, `structural_break_wells_fargo_housing_spy.json`, `lead_winner_curve_20260706.csv`, and `tournament_validation_20260706/bootstrap.csv`):

1. **The causality runs backwards.** Toda-Yamamoto Granger finds SPY → HMI significant at ALL 12 tested monthly lags and HMI → SPY at one isolated lag (5) only; transfer entropy is reverse-only (SPY→HMI p = 0.000, HMI→SPY p = 0.386); the era battery is null in all four eras since 1993. The indicator is LAGGING — the rule reads an old echo of a cycle the market already priced.
2. **The L7 lead is a SPIKE, not a ridge.** The winner's own signal scores OOS Sharpe 1.00 at L6 and 0.93 at L8 versus 1.43 at the published L7 — adjacent-lead durability FAILS (ECON-LT2). A robust mechanism should not care whether the signal is 6, 7, or 8 months stale.
3. **Not statistically significant.** Bootstrap p = **0.1272** versus resampled buy-and-hold — above the 5% threshold.
4. **The return did not beat buy-and-hold.** 15.2% vs 15.4% annualized. The entire Sharpe edge is volatility/drawdown avoidance — which is also why the honest headline is the **−8.1% vs −23.9% max drawdown**, not the Sharpe.
5. **Found-in-search by construction.** Best of 12,980 valid combos from 17,856 scanned; the median valid combo (0.79) underperforms buy-and-hold (0.94); the runner-up (1.42) is a DIFFERENT signal/threshold construction — a flat-topped search surface, the signature of selection rather than mechanism.
6. **One validated stress episode.** Of the standard episodes, only COVID has usable strategy data (subperiod ann. Sharpe 1.70, max drawdown −6.1%); dot-com and GFC are `insufficient_data`. Durability verdict: `conditionally_durable`.
7. **Static, stale source.** The Data Master extract ends 2025-10 (~9 months stale at run date); FRED delisted the NAHBHMI series for licensing, so live use needs a refresh path before this rule could even be followed.
8. **Bounded integer index.** The HMI is a 0-100 integer diffusion index: %-change transforms are level-dependent and threshold ties are common (handled deterministically; the winner's `bounded_pct_risk` flag is False since `diff_12m` is a point-change, but the family caveat stands).

**What survives honestly** (report both directions): the 98-month (~8.2-year) OOS window is ABOVE the 5-year reliability floor — long by fleet standards; IS Sharpe 0.75 vs OOS 1.43 (consistent sign, no in-sample loss); rolling correlation `sign_stable` (0.819); structural break NOT flagged (p = 0.35). None of that rescues the causality verdict or the lead spike.

**What this means:** the honest label is a **found-in-search DEFENSIVE candidate on a lagging indicator** — "the best damage-control overlay we found by searching, whose drawdown profile is genuinely attractive but whose selection is unproven." The prescribed next step is a final exam: freeze this rule and test it once on an untouched window. Expectations should be calibrated to the drawdown claim, not the Sharpe.

**Further caveats:**

- **The edge is episodic.** 16 trades in 98 months; the outperformance concentrates in three stress windows (2018 vol, 2020 COVID, the 2022 rate shock) where the cash-step avoided losses — one class of episode, repeated.
- **Costs.** Returns are gross of costs; at 5 bps per trade and 1.96 trades/yr the haircut is small (see `tournament_validation_20260706/transaction_costs.csv`) — cost drag is not this pair's problem; the lagging verdict and the lead spike are.
"""

    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** on "
        "**2006-06-30** the broker-style log records a SELL — the "
        "7-month-lagged 12-month change in builder sentiment (−9.000) "
        "sat below its rolling 25th-percentile threshold (−2.000), "
        "moving the position from 100% long to CASH ahead of the "
        "housing-bust bear market. The matching re-entry sequence "
        "(2008-01-31 BUY at signal −14.000 vs threshold −14.500, then "
        "2008-08-31 SELL, then **2008-11-30 BUY** near the crisis "
        "trough at signal −13.000 vs threshold −16.000) shows both "
        "faces of the rule: it can step aside for a long bust, and it "
        "can whipsaw back in early. Every row is in the broker-style "
        "CSV — and note the direction in each: BUY = signal ABOVE "
        "threshold → long; SELL = signal below → cash. Never short."
    )

    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2006-06-30",
        "side": "SELL",
        "instrument": "SPY",
        "quantity_pct": "0.0",
        "commission_bps": "5",
        "reason": (
            "P1_long_cash_pro: diff_12m (nahb_hmi_diff_12m) = -9.000 vs "
            "threshold -2.000 — position 100% -> 0%"
        ),
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | Data Master workbook, sheet `WFHMI` (NAHB/Wells Fargo Housing Market Index; FRED delisted `NAHBHMI` for licensing) | `WFHMI!RE - Wells Fargo H Indx` — builder-sentiment diffusion index, 0-100 | **Monthly** (HMI history from 1985-01; tradable pair sample 1993-02 → 2025-10, 393 months, capped by SPY inception) |
| Target | Yahoo Finance | SPY (SPDR S&P 500 ETF, dividend-adjusted) | Monthly (month-end) |

Dataset produced by Dana for the feat260706_wells_fargo_housing_spy wave. **STATIC SOURCE:** the Data Master extract ends 2025-10 (~9 months stale at run date); refresh requires a Master update. The HMI is an integer-valued, bounded 0-100 diffusion index — %-change transforms are level-dependent (flagged per tournament row) and threshold ties are handled deterministically. NAHB releases the index mid-month FOR the current month, so even L0 would be lookahead-free; the tournament grid nevertheless floors at L1 by fleet convention.
"""

_INDICATOR_CONSTRUCTION_MD = (
    "The raw HMI level is a bounded 0-100 diffusion "
    "index; analysis runs on the level plus monthly transforms: 1-, 3- "
    "and 12-month point-changes (`diff_12m` — the winning signal — is "
    "this month's index minus its value 12 months earlier, in index "
    "points, sidestepping the bounded-index %-change problem), MoM/YoY % "
    "changes, deviation from moving average, 60-month rolling z-scores, "
    "acceleration, and HMM/Markov regime states — 13 transforms in all. "
    "The tradable lead grid runs L1..L12 MONTHS (L0 appears only as a "
    "non-tradable diagnostic; NAHB's mid-month release for the current "
    "month would make even L0 lookahead-free, but the grid floors at L1 "
    "by fleet convention)."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation battery (Pearson/Spearman/distance) | Any raw association at any monthly horizon? | Cheap triage before formal tests |
| Toda-Yamamoto Granger causality (lags 1–12m, both directions) | Who forecasts whom? | Robust to unit-root ambiguity; the decisive test for a suspected-lagging indicator |
| Pre-whitened CCF (offsets −24..+24 months, AR(12) filter) | At which monthly offsets do the series echo? | Filters autocorrelation that fakes lead-lag patterns |
| Local projections (HAC errors) | Where is SPY h months after a sentiment move? | Horizon-by-horizon honesty; robust to overlapping returns |
| Transfer entropy (500 permutations, tercile bins, integer-tie handling) | Any non-linear information flow? | Model-free check the linear tests can't provide — and here the starkest reverse-only verdict |
| Quantile regression | Does the signal at least predict tail risk? | Sentiment signals sometimes work at the left tail only |
| Two-state HMM + quartile sorts | Do builder-mood states coincide with distinct market environments? | The descriptive/regime reading appropriate to a lagging series |
| Era battery (4 eras since 1993) + structural break (Quandt-Andrews) + rolling correlation | Did the relationship hold in ANY era, and did it change mid-sample? | It held in none (all p ≥ 0.31) and no break is flagged (p = 0.35) — stably weak |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: 13 signals (monthly HMI transforms + HMM/Markov regime states) × 12 threshold schemes (fixed percentiles, rolling percentiles, z-score bands, zero-line) × 6 strategy families × MONTHLY leads {1…12} = **17,856 combinations** plus a buy-and-hold benchmark row (valid=False per ECON-T4). Validity filters → **12,980 valid**; median valid OOS Sharpe 0.7901 (below buy-and-hold's 0.94). The source is seasonally adjusted, so no seasonal-cleanliness restriction applies; the objective is max OOS Sharpe (√12 MONTHLY annualization) over the full valid population, ties resolved by the ECON-T3 cascade (resolved at step 1; one tie at step 1 — integer-granularity index, ties expected). Full grid scanned natively over L1..L12 (GH #13: no staleness possible; ECON-LT1 pass). Out-of-sample split per policy `v1_max36_25pct_cap120` on the 393-month overlap: in-sample through 2017-08-31 (295 months, spanning the 1990s expansion, dot-com bust, the classic 2005-09 housing bust, and the QE era), out-of-sample 2017-09-30 → 2025-10-31 (**98 MONTHS ≈ 8.2 years — ABOVE the 5-year reliability floor**, spanning 2018 vol, COVID, the 2021 housing boom, the 2022 rate shock and the 2023-25 high-rate regime). Winner: `diff_12m / T2_roll_p25 / P1_long_cash` pro (procyclical), lead L7 months, LB60; OOS Sharpe 1.4291, IS Sharpe 0.75, bootstrap p = 0.1272; **adjacent-lead durability FAILS** (L6 1.00 / L8 0.93 — one-lead spike, ECON-LT2). All tournament CSV metrics are decimal ratios.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_wells_fargo_housing_spy.py` — deterministic, fixed seeds. The canonical monthly return series for chart producers is `strategy_returns_20260706.csv`; its Sharpe/drawdown/return reconcile with `winner_summary.json`.
"""

_REFERENCES_MD = """
1. National Association of Home Builders / Wells Fargo, *Housing Market Index* — survey methodology (current sales, 6-month expectations, buyer traffic; 0-100 diffusion index).
2. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes." *Journal of Econometrics*, 66(1–2), 225–250.
3. Jordà, Ò. (2005). "Estimation and inference of impulse responses by local projections." *American Economic Review*, 95(1), 161–182.
4. Leamer, E. E. (2007). "Housing IS the business cycle." *NBER Working Paper 13428* — the housing-leads-the-cycle hypothesis this pair tests (and, for equities, rejects).
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
        "MONTHLY data; analytical sample 1993-02 → 2025-10 (393 months of "
        "HMI × SPY overlap; the HMI itself extends back to 1985 but SPY "
        "inception caps the pair). Out-of-sample split per policy "
        "v1_max36_25pct_cap120: in-sample through 2017-08-31, "
        "out-of-sample 2017-09-30 → 2025-10-31 (98 months ≈ 8.2 years — "
        "ABOVE the 5-year reliability floor). Sharpe ratios use √12 "
        "annualization; leads are in months (winner L7). STATIC SOURCE: "
        "the Data Master extract ends 2025-10 (~9 months stale at run "
        "date)."
    ),
    plain_english=(
        "One MONTHLY survey series (the NAHB/Wells "
        "Fargo builder-confidence index, from 1985) and the S&P 500 ETF "
        "(SPY, from 1993). We turned the sentiment index into "
        "point-change and z-score transforms, ran several independent "
        "lead-lag tests (they agree — and point the other way: the "
        "market predicts builder mood at every tested lag; builder mood "
        "predicts the market at one isolated lag nothing corroborates), "
        "then searched 17,856 monthly trading-rule combinations on data "
        "split so rules were built on pre-2017 history and scored on "
        "2017–2025 (~8.2 years). Every number on these pages can be "
        "reproduced by one deterministic script, and the winner is "
        "labelled a defensive candidate because the indicator is "
        "lagging, its lead is a one-lead spike, and its genuine virtue "
        "is the drawdown, not the Sharpe."
    ),
)
