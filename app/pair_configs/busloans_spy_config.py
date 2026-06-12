"""C&I Loans (BUSLOANS) × SPY pair configuration (Rule APP-PT1).

Pair #19, Mode 1, branch fix260612_busloans_spy. All ELI5 prose was
pre-authored by Research Ray in
`docs/portal_narrative_busloans_spy_20260612.md` (narrative_version 1.0.0)
and is ported VERBATIM here; this file wires it into the template-expected
structure (Ace's lane: structure, chart-name constants, downloads list).

Evidence status (binding): `results/busloans_spy/evidence_status.json` =
`found_in_search`. Every performance number is a SEARCH-PHASE OOS figure
(2018-02..2026-05, 100 months); no holdout test has been run. KPI routing
per DPS-FE2 is handled at template level (APP-PLB1, page_templates.py).

Chart names per Vera's handoff
(`results/_cross_agent/handoff_lead_busloans_spy_20260612_vera.md` §5):
quantile block uses the registry-canonical `quantile_coef` (NOT
gold_copper's `quantile_regression`); tournament distribution chart is
`tournament_sharpe_dist`; walk-forward is `walk_forward`.
"""

from __future__ import annotations

from components.page_templates import MethodologyConfig


# =========================================================================
# STORY PAGE
# =========================================================================
class StoryConfig:
    PAGE_TITLE = "The Story: The Bank-Loan Paradox"
    PAGE_SUBTITLE = (
        "Commercial & Industrial Loans (C&I Loans, FRED series BUSLOANS) × "
        "S&P 500 (SPY) — monthly, indicator history from 1947, SPY-bound "
        "analytical sample 1993-02 onward (400 months)."
    )

    # Ray's Story headline, verbatim (headline_template A).
    HEADLINE_H2 = (
        "## Search-phase OOS Sharpe 1.50 vs 0.89 buy-and-hold, max drawdown "
        "−1.0% vs −23.9% (search window 2018-02–2026-05; no holdout test "
        "yet) — business loans turn out to FOLLOW the stock market, not "
        "lead it; what survives is a defensive overlay found by search, "
        "not a validated forecasting signal"
    )

    # Ray: story_md_intro (verbatim).
    PLAIN_ENGLISH = (
        "In the spring of 2020, while the stock market was crashing, "
        "American businesses were borrowing from their banks at the fastest "
        "pace ever recorded. That paradox is the key to this page: business "
        "loans don't predict the market — they respond to it. We tested the "
        "relationship every way we know how, and the verdict is unusually "
        "clean: the S&P 500 (SPY) forecasts Commercial & Industrial (C&I) "
        "loans at every horizon; the loans forecast nothing. What survives "
        "is a modest defensive pattern found by search — presented here "
        "with its warning labels attached."
    )

    # Ray: Story §hook "What this means" paragraph (verbatim).
    WHERE_THIS_FITS = (
        "This is a page about a *confirming* indicator, not a *warning* "
        "indicator. That is itself valuable knowledge — knowing which "
        "signals NOT to trade on is half of risk management. And, as we "
        "show on the Strategy page, a tournament search did surface one "
        "defensive use for the series — with caveats we spell out in full. "
        "Investors needing advance warning should look to leading credit "
        "measures such as the high-yield spread (covered in the HY-IG "
        "pair) instead."
    )

    # Composed from Ray's headline (structural rearrangement only, flagged
    # in handoff): the page's verdict in one sentence.
    ONE_SENTENCE_THESIS = (
        "Business loans turn out to FOLLOW the stock market, not lead it — "
        "what survives is a defensive overlay found by search (search-phase "
        "OOS Sharpe 1.50 vs 0.89 buy-and-hold, max drawdown −1.0% vs "
        "−23.9%, window 2018-02–2026-05; no holdout test yet), not a "
        "validated forecasting signal."
    )

    # From Ray's binding evidence-status note + headline finding #1
    # (verbatim fragments).
    KPI_CAPTION = (
        "every performance number on this page is a search-phase "
        "out-of-sample figure (window 2018-02 → 2026-05, 100 months); no "
        "holdout / final-exam test has been run yet. The winner was found "
        "as the best of 4,396 valid combinations; bootstrap p = 0.066, not "
        "significant at the 5% level."
    )

    HERO_TITLE = "C&I Loan Growth vs the S&P 500 (SPY)"
    HERO_CHART_NAME = "hero"
    HERO_CAPTION = (
        "How to read it: dual-axis view — year-over-year C&I loan growth "
        "and the S&P 500 (SPY) on a common time axis, NBER recessions "
        "shaded. Notice the COVID paradox annotated in 2020: loan growth "
        "spiked above +30% year-over-year while the market crashed — firms "
        "drawing emergency credit lines, not expressing confidence."
    )

    REGIME_TITLE = "What History Shows: SPY Performance by Loan-Growth Quartile"
    REGIME_CHART_NAME = "regime_stats"
    # Describes BOTH dual-panel values (VIZ-QR1), per Ray's regime block.
    REGIME_CAPTION = (
        "What this shows: forward S&P 500 (SPY) performance in each "
        "quartile of loan growth, from weakest (Q1) to strongest (Q4) — "
        "annualized Sharpe ratio (left panel) and annualized return (right "
        "panel). Both panels show the pattern the tournament later "
        "exploits: forward returns are healthiest when loan growth sits in "
        "its weakest quartile — historically the late, post-stress stage "
        "of the cycle. Descriptive, conditional, and regime-dependent — "
        "not a forecast."
    )

    # Ray: Story §hook + §mechanism with their two expanders (verbatim).
    NARRATIVE_SECTION_1 = """
### The bank-loan paradox

Here is a fact that surprises almost everyone the first time: in the spring of 2020, while the S&P 500 (SPY) was crashing 30%, American businesses were borrowing from their banks at the fastest pace ever recorded — Commercial & Industrial (C&I) loan growth spiked above +30% year-over-year in May 2020. Loans boomed *while* the market collapsed. If you had treated rising business lending as a sign of economic health, you would have been buying confidence at exactly the wrong moment.

That paradox is the key to this entire page. We set out to test whether C&I loan growth predicts the stock market. The honest answer from every statistical test we ran: **it does not — the prediction runs the other way.** The stock market moves first, and bank loan books respond afterwards. C&I loans are, in fact, an official component of the Conference Board's *Lagging* Economic Index — and our data agrees with that classification emphatically.

**What this means:** this is a page about a *confirming* indicator, not a *warning* indicator. That is itself valuable knowledge — knowing which signals NOT to trade on is half of risk management. And, as we show on the Strategy page, a tournament search did surface one defensive use for the series — with caveats we spell out in full.

<!-- expander: What exactly is a Commercial & Industrial loan? -->
A Commercial & Industrial (C&I) loan is money a bank lends directly to a business — to fund inventory, payroll, equipment, or general operations. The Federal Reserve tallies the total outstanding across all US commercial banks every week in its H.8 release (FRED series `BUSLOANS`, in billions of dollars, seasonally adjusted). Think of it as the running balance on corporate America's collective credit card. Crucially, much of it is drawn from pre-arranged *credit lines* — which is why the balance can jump precisely when times get bad.
<!-- /expander -->

### Why loans lag: the credit-line mechanism

Think of a business credit line like a homeowner's emergency credit card. You arrange it when times are good, and you *max it out* when trouble hits. That is exactly what firms do in aggregate:

- **Into a downturn**, firms draw down pre-arranged credit lines to stockpile cash ("revolver drawdowns") — so measured loan balances *rise* as the economy and the stock market fall. COVID is the textbook case (see the zoom-in chart below).
- **After a recession ends**, firms repay debt and banks tighten standards — so loan growth keeps *falling* well into the recovery. After the Global Financial Crisis (GFC), loan growth did not bottom until February 2010 (−20.2% year-over-year), almost a year after stocks had already turned up in March 2009 (see the GFC zoom-in chart).

**In plain English:** loan balances are a *thermometer reading taken after the fever* — they tell you how bad things were, not how bad they are about to get. The economically interesting *leading* series in this family is not the loans themselves but the banks' willingness to lend (the Fed's Senior Loan Officer Opinion Survey on lending standards) — a candidate flagged for a future pair in `analyst_suggestions.json`.

<!-- expander: Why would a 'lagging' indicator still be worth a dashboard page? -->
Three reasons. First, honesty: a leading-indicator catalogue earns trust by documenting what *doesn't* lead with the same rigor as what does. Second, confirmation value: a lagging series helps you date the cycle in hindsight and confirms whether a market move had a real-economy echo. Third, the search finding: even a lagging series can carry a usable *state* description — "loan growth is unusually weak" turns out to coincide with periods where holding equities was unusually safe in our 2018–2026 search window. Whether that survives a true holdout test is exactly the open question this page is careful not to prejudge.
<!-- /expander -->
"""

    # Ray: config prose block HISTORY_ZOOM_EPISODES (verbatim; slugs match
    # Vera's filenames: dotcom / gfc / covid / inflation_2022).
    HISTORY_ZOOM_EPISODES = [
        {
            "slug": "dotcom",
            "title": "Dot-Com Crash (2000–2002)",
            "narrative": (
                "Loan growth peaked three months AFTER the equity top "
                "(Jun-2000) and bottomed two and a half years later, right "
                "at the equity trough — textbook lagging behavior. A reader "
                "waiting for loan weakness as a warning was warned only "
                "once the bear market was nearly over."
            ),
            "caption": (
                "Loan growth peaked after the SPY top — confirmation in "
                "arrears, no warning"
            ),
        },
        {
            "slug": "gfc",
            "title": "GFC (2007–2009)",
            "narrative": (
                "Loan growth was still accelerating four months into the "
                "recession as firms drew credit lines, then collapsed for "
                "two years, troughing 11 months after equities had already "
                "bottomed. As a forward signal this is the failure case: "
                "bullish into the crash, bearish through the recovery."
            ),
            "caption": (
                "Failure case — loans accelerated into the crash, troughed "
                "after the recovery began"
            ),
        },
        {
            "slug": "covid",
            "title": "COVID Shock (2020)",
            "narrative": (
                "C&I loans spiked at a record pace while SPY crashed — "
                "firms maxing out emergency credit lines, not expressing "
                "confidence. Loans and equities moved violently in opposite "
                "directions at the same time: coincident-inverse, with no "
                "lead either way."
            ),
            "caption": (
                "Coincident-inverse — record loan spike during the equity "
                "crash (credit-line drawdowns)"
            ),
        },
        {
            "slug": "inflation_2022",
            "title": "2022 Rates Shock",
            "narrative": (
                "Loan growth rose through the entire Fed-driven equity "
                "drawdown, giving no warning and no echo. The strategy sat "
                "in cash all year by construction (flat, not a loss) — "
                "spared the bear market without the indicator deserving "
                "any predictive credit."
            ),
            "caption": (
                "Failure case — loan growth rose while SPY fell ~24%; "
                "strategy was in cash throughout"
            ),
        },
    ]

    # Ray: Story §what_survives + §takeaway (verbatim).
    NARRATIVE_SECTION_2 = """
### What survives: a defensive overlay, honestly labelled

After 6,100 strategy combinations were searched (4,396 passing validity filters), the best rule found was: **be long the S&P 500 (SPY) only when month-over-month loan growth — observed with a 6-month delay — is in the bottom quartile of its trailing 36-month range; otherwise hold cash.** In the search window (2018-02 to 2026-05) that rule produced a Sharpe ratio of 1.50 versus 0.89 for buy-and-hold, with a maximum drawdown of just −1.0% versus −23.9%.

But this finding comes with non-negotiable context, stated here rather than in a footnote:

- It is the **best of 4,396** — and the **median** valid combination scored 0.74, *below* buy-and-hold's 0.89. Most things you could have tried with this indicator lose to doing nothing. The winner is the far tail of a large search.
- A bootstrap re-shuffle test puts the probability of a result this good arising by chance at **6.6%** — above the 5% bar we would want before calling it real.
- The rule looked unimpressive on pre-2018 data (in-sample Sharpe 0.35), its edge is concentrated in one episode (the COVID recovery), and it was in the market only 25% of the time.

**What this means:** treat this as *"a defensive pattern found by search, awaiting its final exam"* — not as a validated trading edge. The next step (per `evidence_status.json`) is a frozen-rule holdout test, and expectations for it should be calibrated low.

### What this means for investors

- **Do not use C&I loan growth as an early-warning signal** — in four major drawdowns since 2000 it warned of none of them; investors needing advance warning should look to leading credit measures such as the high-yield spread (covered in the HY-IG pair) instead.
- **Rising loan balances during a crash are not a bullish sign** — they are firms drawing emergency credit lines; investors should resist reading the COVID-style loan spike as corporate confidence.
- **Very weak loan growth has historically marked the *late* stage of the damage** — in the search window, being long equities only in such periods captured the recovery while avoiding turbulence; investors may treat depressed loan growth as one input to a "the worst may be behind us" checklist, not as a standalone trigger.
- **The strategy's profile is drawdown-avoidance, not return-seeking** — it gave up 4.2 percentage points of annual return versus buy-and-hold (10.7% vs 14.8%) in exchange for a 23-point smaller maximum drawdown; investors whose priority is compounding total return would have been better off holding the index.
"""

    # Ray: Evidence §evidence-overview, first paragraph (verbatim) — used
    # as the Story → Evidence transition.
    TRANSITION_TEXT = (
        "One question, attacked five independent ways: *does C&I loan "
        "growth carry information about future S&P 500 (SPY) returns — or "
        "is it the other way round?* Methods that agree from different "
        "angles are far more convincing than any single test. Here, all "
        "five angles agree — in the direction nobody trades on."
    )


STORY_CONFIG = StoryConfig()


# =========================================================================
# EVIDENCE PAGE — 7 method blocks (Ray's 8-element blocks, verbatim).
# Chart-name constants per Vera's handoff §5 — one DISTINCT chart per
# block; declared as module constants so smoke_loader's AST scan
# (*_CHART_NAME assigns) covers every evidence chart.
# =========================================================================
CORRELATION_CHART_NAME = "correlation_heatmap"
GRANGER_CHART_NAME = "granger_f_by_lag"
CCF_CHART_NAME = "ccf_prewhitened"
LOCAL_PROJECTIONS_CHART_NAME = "local_projections"
TRANSFER_ENTROPY_CHART_NAME = "transfer_entropy"
QUANTILE_CHART_NAME = "quantile_coef"  # registry canonical (Vera §5)
HMM_REGIME_CHART_NAME = "hmm_regime_probs"


CORRELATION_BLOCK = dict(
    chart_status="ready",
    method_name="Correlation Battery",
    method_theory=(
        "Pearson and Spearman correlations between every loan-growth "
        "transform (month-over-month, year-over-year, z-scores, "
        "contraction flags) and forward SPY returns at 1/3/6/12-month "
        "horizons."
    ),
    question=(
        "Is there any raw statistical association between loan growth "
        "today and stock returns tomorrow?"
    ),
    how_to_read=(
        "Rows are signal transforms, columns are forward-return horizons; "
        "each cell's color shows the correlation — red negative, blue "
        "positive, deeper color = stronger. Values near zero (pale cells) "
        "mean no association."
    ),
    chart_name=CORRELATION_CHART_NAME,
    chart_caption=(
        "What this shows: correlations between loan-growth transforms and "
        "forward S&P 500 (SPY) returns across horizons. The grid is "
        "overwhelmingly pale — near-zero association at every tradeable "
        "horizon."
    ),
    observation=(
        "The grid is overwhelmingly pale. The strongest cell is the "
        "60-month z-score of year-over-year growth versus 12-month forward "
        "returns, at r = 0.225 — modest, positive, and only at the longest "
        "horizon."
    ),
    deep_dive_title="Why treat the heatmap as triage rather than proof?",
    deep_dive_content=(
        "Forward returns at overlapping horizons induce serial correlation "
        "in the cells; treat the heatmap as descriptive triage rather than "
        "inference — the formal tests below carry the inferential weight."
    ),
    interpretation=(
        "The one modest cell is a *level-of-cycle* effect: when loan "
        "growth has been depressed for years (deeply negative z-score), "
        "the economy is typically late in a recession and subsequent "
        "multi-year equity returns are above average. That is consistent "
        "with the lagging story, not with short-horizon predictability."
    ),
    key_message=(
        "At every tradeable horizon, the raw association between loan "
        "growth and future stock returns is close to zero."
    ),
)


GRANGER_BLOCK = dict(
    chart_status="ready",
    method_name="Granger Causality (Toda-Yamamoto)",
    method_theory=(
        "Granger causality (a statistical test of whether one series helps "
        "forecast another beyond the other's own history), in the "
        "Toda-Yamamoto form that stays valid even if the series' trends "
        "are imperfectly removed."
    ),
    question="Who moves first — business loans or the stock market?",
    how_to_read=(
        "Bars show the test statistic at each lag from 1 to 12 months, "
        "one panel per direction; bars clearing the dashed significance "
        "line indicate forecasting power at that lag."
    ),
    chart_name=GRANGER_CHART_NAME,
    chart_caption=(
        "What this shows: Granger F-statistics by lag, both directions, "
        "with the per-lag 5% critical line. Loans → SPY clears the line at "
        "no lag; SPY → loans clears it at every lag."
    ),
    observation=(
        "In the loans → SPY direction, no bar at any of the 12 lags clears "
        "the line (smallest p-value 0.257, at lag 5). In the SPY → loans "
        "direction, *every* bar from lag 1 to 12 clears it (largest "
        "p-value 0.0115)."
    ),
    deep_dive_title="Why Toda-Yamamoto instead of plain Granger?",
    deep_dive_content=(
        "Plain Granger tests can produce spurious results when series have "
        "unit roots or borderline stationarity; Toda-Yamamoto augments the "
        "underlying model with extra lags (d_max = 1 here) so the test "
        "statistic keeps its standard distribution regardless. We run it "
        "on the stationary year-over-year transform."
    ),
    interpretation=(
        "This is as one-sided as lead-lag evidence gets: a clean reject in "
        "one direction at every lag, a clean non-reject in the other at "
        "every lag. Stock prices aggregate forward-looking information in "
        "real time; loan books respond with the mechanical delays of "
        "corporate borrowing decisions and bank credit committees."
    ),
    key_message=(
        "The stock market predicts business loans at every lag tested; "
        "business loans predict the stock market at none."
    ),
)


CCF_BLOCK = dict(
    chart_status="ready",
    method_name="Pre-Whitened Cross-Correlation",
    method_theory=(
        "A pre-whitened Cross-Correlation Function (CCF) — correlation "
        "between the two series at every monthly offset from −20 to +20, "
        "after filtering each series' own autocorrelation so trends cannot "
        "masquerade as lead-lag structure."
    ),
    question=(
        "At which specific monthly offsets, if any, do the two series "
        "echo each other?"
    ),
    how_to_read=(
        "The X-axis is the offset in months — negative offsets mean loans "
        "move before stocks, positive offsets mean stocks move before "
        "loans. Bars outside the dashed band are statistically significant "
        "at 95% confidence."
    ),
    chart_name=CCF_CHART_NAME,
    chart_caption=(
        "What this shows: pre-whitened cross-correlation at 41 monthly "
        "offsets with 95% confidence bands. A single stray bar at +17 "
        "months on the stocks-lead side is noise; nothing is significant "
        "on the loans-lead side."
    ),
    observation=(
        "Of 41 offsets, a single bar (+17 months, correlation 0.119) "
        "pokes above the band on the stocks-lead side; nothing is "
        "significant on the loans-lead side."
    ),
    interpretation=(
        "With 41 offsets tested at 95% confidence, roughly two false "
        "alarms are expected by chance alone — one stray bar at an "
        "economically arbitrary +17 months is noise, not signal. The CCF "
        "therefore corroborates the Granger result: no loans-lead "
        "structure exists at any monthly offset."
    ),
    key_message=(
        "Across 41 monthly offsets, there is no credible window in which "
        "loan growth foreshadows stock returns."
    ),
)


LOCAL_PROJECTIONS_BLOCK = dict(
    chart_status="ready",
    method_name="Local Projections",
    method_theory=(
        "Local projections (a horizon-by-horizon regression technique that "
        "traces how one variable responds after a movement in another), "
        "with HAC standard errors robust to overlapping horizons."
    ),
    question=(
        "If loan growth jumps today, where is the stock market 1, 3, 6, "
        "and 12 months later?"
    ),
    how_to_read=(
        "Each panel plots the estimated response (line) with its "
        "confidence band (shading) across horizons; a band that straddles "
        "zero means no detectable effect."
    ),
    chart_name=LOCAL_PROJECTIONS_CHART_NAME,
    chart_caption=(
        "What this shows: impulse-response panels, forward and reverse. "
        "In the loans → SPY panel the confidence band straddles zero at "
        "every horizon."
    ),
    observation=(
        "In the loans → SPY panel the band straddles zero everywhere (all "
        "p-values above 0.81). Point estimates in the reverse direction "
        "are negative at short horizons but also not significant."
    ),
    interpretation=(
        "Even granting the indicator its best shot — any horizon, robust "
        "errors — there is no detectable forward effect. The translation: "
        "nothing here for a forecaster."
    ),
    key_message=(
        "A jump in loan growth tells you nothing statistically useful "
        "about where stocks will be up to a year later."
    ),
)


TRANSFER_ENTROPY_BLOCK = dict(
    chart_status="ready",
    method_name="Transfer Entropy",
    method_theory=(
        "Transfer entropy — a model-free measure of directed information "
        "flow that can detect *non-linear* relationships ordinary "
        "correlation misses (estimated on tercile-binned data with 500 "
        "permutations)."
    ),
    question=(
        "Could loans predict stocks in some curvy, non-linear way the "
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
        "p-values. Neither direction is significant — no hidden non-linear "
        "channel."
    ),
    observation=(
        "Loans → SPY: p = 0.81. SPY → loans: p = 0.50. Neither direction "
        "is significant."
    ),
    deep_dive_title=(
        "Why is the reverse direction insignificant here but strongly "
        "significant under Granger?"
    ),
    deep_dive_content=(
        "That the reverse direction is also insignificant here, while "
        "strongly significant under Granger, simply reflects transfer "
        "entropy's lower power on 400 coarsely-binned monthly observations "
        "— the linear test is the sharper instrument for the reverse "
        "channel."
    ),
    interpretation=(
        "No hidden non-linear channel rescues the indicator."
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
        "Quantile regression — instead of asking how loan growth affects "
        "the *average* future return, it asks how it affects the *worst* "
        "and *best* outcomes (the tails), where risk signals usually earn "
        "their keep."
    ),
    question=(
        "Does weak loan growth at least predict tail risk — the really "
        "bad months — even if it can't predict the average?"
    ),
    how_to_read=(
        "The X-axis runs across outcome percentiles (5th = worst months, "
        "95th = best); the line is the estimated effect at each percentile "
        "with its confidence band. A risk signal typically shows a "
        "significant effect at the left tail."
    ),
    chart_name=QUANTILE_CHART_NAME,
    chart_caption=(
        "What this shows: quantile-regression coefficient by percentile "
        "with confidence band. The band straddles zero everywhere — no "
        "tail-risk channel either."
    ),
    observation=(
        "The confidence band straddles zero at every percentile from the "
        "5th to the 95th."
    ),
    interpretation=(
        "Many credit indicators fail at the mean but work at the left "
        "tail. This one fails at both — loan growth does not even flag "
        "elevated crash risk."
    ),
    key_message=(
        "Loan growth predicts neither average stock returns nor tail risk."
    ),
)


REGIME_BLOCK = dict(
    chart_status="ready",
    method_name="Regime Context (HMM and Quartiles)",
    method_theory=(
        "A two-state Hidden Markov Model (HMM — a statistical model that "
        "infers unobserved \"calm\" vs \"stressed\" regimes from the "
        "data's behavior) fitted to the loan series, plus a simple sort of "
        "history into quartiles of loan growth with the forward SPY return "
        "reported in each."
    ),
    question=(
        "Even without prediction, do states of the loan cycle coincide "
        "with systematically different stock-market environments?"
    ),
    how_to_read=(
        "The HMM panel shades periods by inferred regime probability over "
        "time; the quartile chart shows annualized forward SPY returns in "
        "four bars, sorted from weakest (Q1) to strongest (Q4) loan "
        "growth."
    ),
    chart_name=HMM_REGIME_CHART_NAME,
    chart_caption=(
        "What this shows: HMM-inferred regime probability over time, NBER "
        "recessions shaded. The 'stressed' state aligns with the "
        "aftermaths of recessions (2002–04, 2009–11, 2020–21), not their "
        "onsets. The quartile view of the same regime story is on the "
        "Story page (loan-growth quartile chart)."
    ),
    observation=(
        "The HMM's stressed state aligns with the *aftermaths* of "
        "recessions (2002–04, 2009–11, 2020–21) rather than their onsets. "
        "The quartile bars show the pattern the tournament later exploits: "
        "forward returns are healthiest when loan growth sits in its "
        "weakest quartile."
    ),
    deep_dive_title="How stable is the relationship over time?",
    deep_dive_content=(
        "Rolling 24-month correlation between the two series flips sign "
        "repeatedly across the sample (sign-agreement score 0.42 in "
        "`rolling_correlation_busloans_spy.csv`) — the *state* "
        "relationship is real but its month-to-month direction is "
        "unstable, one of the fragility flags carried to the Strategy "
        "page."
    ),
    interpretation=(
        "This is the constructive reading of a lagging series: weak loan "
        "growth describes a *post-stress* state of the world in which much "
        "of the equity damage has already happened. Descriptive, "
        "conditional, and regime-dependent — not a forecast."
    ),
    key_message=(
        "Loan growth doesn't predict the market, but its weakest readings "
        "have historically marked late-stage damage — the one regularity "
        "the strategy search latched onto."
    ),
)


EVIDENCE_METHOD_BLOCKS = {
    # Ray's Evidence headline (verbatim).
    "title": "Five independent tests agree: the stock market moves first, loan books respond",
    # Ray: Evidence §evidence-overview (verbatim).
    "overview": (
        "*One question, attacked five independent ways: does C&I loan "
        "growth carry information about future S&P 500 (SPY) returns — or "
        "is it the other way round? Methods that agree from different "
        "angles are far more convincing than any single test. Here, all "
        "five angles agree — in the direction nobody trades on.*\n\n"
        "All statistics computed on monthly data, SPY-bound sample 1993-02 "
        "→ 2026-05 (400 months), from "
        "`results/busloans_spy/core_models_20260612/`."
    ),
    "plain_english": (
        "This section shows the statistical evidence on whether business "
        "loans predict the stock market. Five independent lead-lag tests — "
        "correlation, Granger causality, pre-whitened cross-correlation, "
        "local projections, and transfer entropy — all agree: the S&P 500 "
        "(SPY) moves first and loan books respond afterwards; loan growth "
        "predicts neither average returns nor tail risk. The one "
        "regularity that survives (weak loan growth marking the late, "
        "post-stress stage of the cycle) is descriptive, not predictive — "
        "it is what the strategy search on the next page latched onto."
    ),
    # DPS mandatory downloads row. Row counts VERIFIED by reading each file
    # at authoring time (2026-06-12) — counts exclude the header row.
    "downloads": [
        {"label": "Granger causality, both directions × 12 lags (24 rows)",
         "path": "results/busloans_spy/core_models_20260612/granger_causality.csv"},
        {"label": "Granger F-statistics by lag, loans → SPY (12 rows)",
         "path": "results/busloans_spy/granger_by_lag.csv"},
        {"label": "Correlation battery, signal × horizon × metric (160 rows)",
         "path": "results/busloans_spy/core_models_20260612/correlations.csv"},
        {"label": "Pre-whitened CCF, offsets −20..+20 (41 rows)",
         "path": "results/busloans_spy/core_models_20260612/ccf_prewhitened.csv"},
        {"label": "Local projections, forward + reverse × 4 horizons (8 rows)",
         "path": "results/busloans_spy/core_models_20260612/local_projections.csv"},
        {"label": "Transfer entropy, both directions (2 rows)",
         "path": "results/busloans_spy/core_models_20260612/transfer_entropy.csv"},
        {"label": "Quantile regression, 7 quantiles (7 rows)",
         "path": "results/busloans_spy/core_models_20260612/quantile_regression.csv"},
        {"label": "Regime quartile returns, Q1–Q4 (4 rows)",
         "path": "results/busloans_spy/regime_quartile_returns.csv"},
        {"label": "Sub-period Sharpe, 4 episodes (4 rows)",
         "path": "results/busloans_spy/subperiod_sharpe.csv"},
        {"label": "Rolling 24-month correlation (370 rows)",
         "path": "results/busloans_spy/rolling_correlation_busloans_spy.csv"},
    ],
    "level1": [CORRELATION_BLOCK, GRANGER_BLOCK, CCF_BLOCK],
    "level1_labels": ["Correlation", "Granger Causality", "Pre-Whitened CCF"],
    "level2": [LOCAL_PROJECTIONS_BLOCK, TRANSFER_ENTROPY_BLOCK,
               QUANTILE_BLOCK, REGIME_BLOCK],
    "level2_labels": ["Local Projections", "Transfer Entropy",
                      "Quantile Regression", "Regime Context (HMM)"],
    # Ray: Evidence §tournament-intro (verbatim; DPS-SCD1 compliant).
    "tournament_intro": (
        "The statistical tests above ask whether the indicator *predicts*. "
        "The tournament asks a more pragmatic question: across every "
        "reasonable trading rule you could build from this series, does "
        "*any* of them beat simply holding the S&P 500 (SPY)?\n\n"
        "We tested a grid of **6,100 strategy combinations** — 11 signal "
        "transforms × multiple threshold schemes × 3 strategy families × "
        "2 orientations × 5 signal delays × 3 lookback windows — of which "
        "**4,396 passed validity filters** (out-of-sample Sharpe above "
        "0.3, fewer than 24 trades per year, at least 24 out-of-sample "
        "months; the buy-and-hold benchmark row is excluded from this "
        "count). The headline rule on the Strategy page is the **best of "
        "those 4,396** — rank 1, with no ties. Position disclosure, per "
        "our specification-curve standard: the **median** valid "
        "combination scored an out-of-sample Sharpe of just **0.74 — "
        "below buy-and-hold's 0.89**. In plain English: most rules you "
        "could have built from this indicator lose to doing nothing, and "
        "the winner is the far tail of a large search. That is exactly "
        "why the next page reports it as \"found in search, not yet "
        "validated out of search.\""
    ),
    "transition": (
        "**Transition:** the lead-lag verdict is settled — loans follow "
        "stocks. What remains is the pragmatic question the tournament "
        "answered: the next page shows the one defensive rule the search "
        "surfaced, with every fragility flag attached."
    ),
}


# =========================================================================
# STRATEGY PAGE
# =========================================================================
class StrategyConfig:
    PAGE_TITLE = (
        "The Strategy: A Long-or-Cash Overlay That Sat Out Most of the "
        "Last Eight Years"
    )
    PAGE_SUBTITLE = (
        "— and avoided nearly all of the drawdown. Found by a "
        "4,396-combination search; no holdout test has been run yet."
    )

    # Ray: strategy_eli5_winner (verbatim).
    PLAIN_ENGLISH = (
        "The winning rule from a 4,396-combination search: hold the "
        "S&P 500 (SPY) only when monthly loan growth — viewed with a "
        "6-month delay — is in the weakest quarter of its past three "
        "years; otherwise hold cash. In the search window (2018–2026) it "
        "scored a Sharpe ratio of 1.50 versus 0.89 for buy-and-hold and "
        "lost at most 1% from peak versus 24% — but it earned less in "
        "total (10.7% vs 14.8% a year), sat in cash 75% of the time, and "
        "fails the standard significance test (bootstrap p = 0.066). The "
        "typical rule in the same search scored *below* buy-and-hold. "
        "Read it as a drawdown-avoidance overlay found by search — its "
        "final exam on untouched data has not yet been run."
    )

    # Ray: §winner-overview (verbatim).
    SIGNAL_RULE_MD = """
**Rule:** Hold the S&P 500 (SPY) **only when month-over-month C&I loan growth — observed with a 6-month delay — sits in the bottom quartile of its own trailing 36-month range. Otherwise hold cash.** (Family: Long/Cash, countercyclical orientation; signal `busloans_mom`, threshold T2 rolling 25th percentile, lead L6, lookback LB36 — per `winner_summary.json`.)

If-then form:
- **IF** the 6-month-old reading of monthly loan growth is in the weakest 25% of its last 36 months → **BUY/HOLD SPY (100% invested)**.
- **ELSE** → **HOLD CASH (0% invested)**.

Search-phase results (2018-02 → 2026-05, 100 months — **no holdout test yet**): Sharpe 1.50 vs 0.89 buy-and-hold; annualized return 10.7% vs 14.8% (the strategy *gives up* 4.2 points of return); maximum drawdown −1.0% vs −23.9%; 24 position changes (turnover 2.88 per year); average market exposure 25%.

**The character of this rule is drawdown-avoidance, not return-seeking.** It is in cash three-quarters of the time, accepts a lower total return, and wins on risk-adjusted terms almost entirely by missing the bad stretches. That is why this pair's `strategy_objective` is classified as **min_mdd** (minimize maximum drawdown).
"""

    # Ray: §signal-generation (verbatim).
    HOW_SIGNAL_IS_GENERATED_MD = """
No formulas — three steps:

**What changes in the world:** businesses collectively slow their bank borrowing — typically late in a downturn, after the damage is done, when firms are repaying emergency credit-line drawdowns and banks have tightened standards.

**What the signal measures:** each month, the rule looks at the *month-over-month* change in total C&I loans as it stood six months ago (the delay reflects both the realistic information lag and, mainly, the tournament's finding that the 6-month-old reading worked best in search). It then asks one question: is that reading among the weakest quarter of the past three years?

**What decision it drives:** weakest-quarter reading → be in the market; anything stronger → stay in cash. The logic the search stumbled onto is the regime pattern from the Evidence page: deeply depressed loan growth has historically marked the *aftermath* of stress, when recoveries were under way — while "normal or booming" loan growth carried no such safety stamp.
"""

    # Manual-use steps. NOTE (flagged in handoff): Ray's narrative doc has
    # no manual-use section; DPS requires one with no generic fallback.
    # Steps below are assembled strictly from facts in Ray's
    # §winner-overview / §signal-generation and the Methodology data table
    # (no new claims) — pending Ray review.
    MANUAL_USE_MD = (
        "If you want to track this signal yourself — no code required — "
        "the monthly routine is:\n\n"
        "1. **Pull the loan series** — FRED series `BUSLOANS` (C&I loans "
        "outstanding, all commercial banks, seasonally adjusted; the H.8 "
        "release publishes with a ~2–3 week lag).\n"
        "2. **Compute month-over-month % change** of the series.\n"
        "3. **Apply the 6-month delay** — the reading the rule acts on "
        "this month is the month-over-month change from six months ago.\n"
        "4. **Compare to its trailing range** — is that delayed reading "
        "in the weakest 25% of its own last 36 monthly readings? (The "
        "threshold is a rolling 25th percentile, recomputed each month — "
        "see `winner_trade_log.csv` for the full threshold path.)\n"
        "5. **Take the position** — weakest-quartile reading → hold SPY "
        "(100% invested); anything stronger → hold cash (0% invested). "
        "Re-evaluate once a month.\n\n"
        "Remember the warning labels: this rule is search-phase only "
        "(no holdout test yet), was in the market just 25% of the time, "
        "and its edge is concentrated in the COVID-recovery episode."
    )

    EQUITY_CHART_NAME = "equity_curves"
    DRAWDOWN_CHART_NAME = "drawdown"
    WALK_FORWARD_CHART_NAME = "walk_forward"
    # Distribution histogram, not a scatter — generic stars/diamond caption
    # would describe elements that don't exist (gold_copper precedent).
    TOURNAMENT_SCATTER_CHART_NAME = "tournament_sharpe_dist"
    TOURNAMENT_SCATTER_CAPTION = (
        "What this shows: the OOS Sharpe distribution of all 4,396 valid "
        "strategy combinations. The vertical line marks the winner (1.50) "
        "— the maximum of the search, not a typical result: the median "
        "combination scored 0.74, below buy-and-hold's 0.89."
    )

    # Ray: §fragility (5 flags) + §caveats (verbatim).
    CAVEATS_MD = """
**Why we do not call this a validated edge** — five flags, none softened (all from `winner_summary.json` and the tournament validation set):

1. **Search-position.** Best of 4,396 valid combinations; the median combination (Sharpe 0.74) *underperforms* buy-and-hold (0.89). The winner is the extreme tail of a wide search, which is precisely the condition under which lucky rules look brilliant.
2. **Bootstrap p = 0.066.** A re-shuffle test says a result this good arises by chance about 6.6% of the time — above the conventional 5% threshold. Not statistically significant.
3. **In-sample vs out-of-sample inversion.** The rule scored Sharpe 0.35 on pre-2018 data and 1.50 after. Robust edges usually look at least decent in both windows; an OOS figure four times the IS figure suggests a favorable draw, not a stable property.
4. **Episode concentration.** The durability check classifies the edge as `episode_concentrated`: the COVID-recovery sub-period delivered Sharpe 2.75; the 2022 episode was spent entirely in cash (Sharpe 0.00 — flat, not a loss); Dot-Com and GFC fall outside the search window entirely (insufficient data).
5. **Sign instability.** The rolling 24-month correlation between indicator and market flips sign chronically (sign-agreement 0.42) — the relationship the rule rides is not even directionally stable over time.

**What this means:** the honest label, from `evidence_status.json`, is **`found_in_search`** — "the best rule we found by searching, not a rule that has passed an independent test." The prescribed next step is a final exam: freeze this rule, wait for (or carve out) a window the search never touched, and test it once. Given the flags above and the lagging-indicator verdict, expectations should be calibrated low.

**Further caveats:**

- **No forward causality.** Every lead-lag test on the Evidence page says the market leads the loans. Any rule built on this series is reading the market's own echo at a delay.
- **Search-phase numbers only.** Selection and evaluation share the same 2018–2026 window; no holdout exam has been run. The Sharpe 1.50 headline is a candidate, not a verdict.
- **Low exposure profile.** At 25% average exposure, results are dominated by *when the rule happened to be in* — a handful of months drive everything.
- **Return give-up.** The rule trails buy-and-hold by 4.2 points of annual return; it is a drawdown-avoidance overlay, unsuitable as a core compounding strategy.
- **Costs.** Returns are gross of costs; at the assumed 5 basis points per trade and 2.88 trades per year, the haircut is negligible (see `tournament_validation_20260612/transaction_costs.csv`) — cost drag is *not* one of this pair's problems.
- **No structural break flagged** (sup-F test p = 0.30), so the fragility flags above cannot be excused by a regime change in the data.
"""

    # Ray: §trade_log_howto, intro + columns + concrete example (verbatim).
    TRADE_LOG_EXAMPLE_MD = (
        "**A concrete example from this pair:** on **2020-04-30** the log "
        "records a BUY — the 6-month-lagged monthly loan growth reading "
        "(0.000) had fallen below its rolling bottom-quartile threshold "
        "(0.101), so the position moved from 0% to 100% just as the "
        "post-COVID recovery began. The matching SELL appears on "
        "**2020-09-30**, when the lagged window caught the +9.1% COVID "
        "credit-line spike and the signal jumped far above threshold, "
        "sending the strategy back to cash. You can find both rows in the "
        "broker-style CSV."
    )

    # Pair-specific column-dictionary example overrides (from Ray's
    # §trade_log_howto facts; broker-style CSV verified 84 events).
    TRADE_LOG_COLUMN_EXAMPLES = {
        "trade_date": "2020-04-30",
        "side": "BUY",
        "instrument": "SPY",
        "quantity_pct": "100.0",
        "commission_bps": "5",
        "reason": (
            "lagged MoM loan growth 0.000 below rolling bottom-quartile "
            "threshold 0.101 — enter market"
        ),
    }


STRATEGY_CONFIG = StrategyConfig()


# =========================================================================
# METHODOLOGY PAGE — all prose Ray's (verbatim).
# =========================================================================
_DATA_SOURCES_MD = """
| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED — Federal Reserve H.8, Assets & Liabilities of Commercial Banks | `BUSLOANS` (C&I loans outstanding, all commercial banks, $bn, seasonally adjusted) | Monthly (from 1947-01) |
| Target | Yahoo Finance | SPY (SPDR S&P 500 ETF, dividend-adjusted) | Monthly (from 1993-02) |

Dataset: `data/busloans_spy_monthly_19470131_20260531.parquet` (Dana; episode-verified against the COVID spike, the 2009-10 trough, and z-score recomputation).
"""

_INDICATOR_CONSTRUCTION_MD = (
    "Raw loans outstanding are non-stationary in levels, so all analysis "
    "runs on growth-rate transforms: month-over-month % change "
    "(`busloans_pct_mom` — the winning signal), year-over-year % change "
    "(the cycle gauge), 3-month annualized growth, rolling z-scores at "
    "multiple windows, and binary contraction flags. The publication lag "
    "of the H.8 release (~2–3 weeks) means a 1-month signal delay is the "
    "real-time floor; the tournament grid therefore starts at lead L1."
)

_METHODS_TABLE_MD = """
| Method | Question It Answers | Why We Chose It |
|---|---|---|
| Correlation battery (Pearson/Spearman) | Any raw association at any horizon? | Cheap triage before formal tests |
| Toda-Yamamoto Granger causality | Who forecasts whom? | Robust to unit-root ambiguity in macro levels series |
| Pre-whitened CCF | At which monthly offsets do the series echo? | Filters autocorrelation that fakes lead-lag patterns |
| Local projections (HAC errors) | Where is SPY h months after a loan-growth move? | Horizon-by-horizon honesty; robust to overlapping returns |
| Transfer entropy (500 permutations) | Any non-linear information flow? | Model-free check the linear tests can't provide |
| Quantile regression | Does the signal at least predict tail risk? | Credit signals often work at the left tail only |
| Two-state HMM + quartile sorts | Do loan-cycle states coincide with distinct market environments? | The descriptive/regime reading appropriate to a lagging series |
| Structural break (sup-F, bootstrap) | Did the relationship change mid-sample? | Guards against averaging two different regimes |
"""

_TOURNAMENT_DESIGN_MD = """
Grid: 11 signals (9 data transforms + HMM stress state + Markov regime) × threshold schemes (fixed percentiles, rolling percentiles, z-score bands, zero-line) × 3 strategy families (Long/Cash, signal-strength scaling, Long/Short) × 2 orientations (procyclical/countercyclical — both tested per the mixed prior) × leads {1, 2, 3, 6, 12} months × lookbacks {36, 60, 120} months = 6,100 combinations plus a buy-and-hold benchmark row. Validity filters: OOS Sharpe > 0.3, turnover < 24/yr, ≥ 24 OOS months → 4,396 valid. Out-of-sample split per policy `v1_max36_25pct_cap120`: in-sample through 2018-01, out-of-sample 2018-02 → 2026-05 (100 of 400 SPY-bound months). Winner selected by the standard cascade, resolved at step 1 with no tie. All metrics in the tournament CSV are decimal ratios, not percentages.

**Reproducibility notes.** Producer script: `scripts/pair_pipeline_busloans_spy.py` — deterministic, fixed seeds; a rerun reproduces every number on this page. The canonical monthly return series for chart producers is `strategy_returns_20260612.csv` (position on row *t* is the accrual weight for month *t*, signal already lagged 6 months); its Sharpe/drawdown/return reconcile with `winner_summary.json` to within 1e-4. Stationarity tests were produced by the data stage and confirmed, not re-run, by the econometrics stage.
"""

_REFERENCES_MD = """
1. Conference Board, *Business Cycle Indicators Handbook* — C&I loans outstanding as a component of the Lagging Economic Index.
2. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes." *Journal of Econometrics*, 66(1–2), 225–250.
3. Jordà, Ò. (2005). "Estimation and inference of impulse responses by local projections." *American Economic Review*, 95(1), 161–182.
4. Ivashina, V. & Scharfstein, D. (2010). "Bank lending during the financial crisis of 2008." *Journal of Financial Economics*, 97(3), 319–338 — credit-line drawdowns rising into downturns.
5. Li, L., Strahan, P. E. & Zhang, S. (2020). "Banks as lenders of first resort: evidence from the COVID-19 crisis." *Review of Corporate Finance Studies*, 9(3), 472–500 — the 2020 revolver-drawdown spike.
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
        "Monthly data; indicator history from 1947-01, SPY-bound "
        "analytical sample 1993-02 → 2026-05 (400 months). Out-of-sample "
        "split per policy v1_max36_25pct_cap120: in-sample through "
        "2018-01, out-of-sample 2018-02 → 2026-05 (100 months). "
        "Search-phase only — no holdout window has been carved out yet."
    ),
    # Ray: methodology_eli5 (verbatim).
    plain_english=(
        "One monthly data series from the Federal Reserve (total business "
        "loans at US banks, back to 1947) and the S&P 500 ETF (SPY, back "
        "to 1993). We turned the loans into growth rates, ran five "
        "independent lead-lag tests (all agree: stocks lead, loans "
        "follow), then searched 6,100 trading-rule combinations on data "
        "split so that rules were built on pre-2018 history and scored on "
        "2018–2026. Every number on these pages can be reproduced by one "
        "deterministic script."
    ),
)
