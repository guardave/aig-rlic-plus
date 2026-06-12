---
pair_id: busloans_spy
narrative_version: 1.0.0
generated_at: "2026-06-12T00:00:00Z"
generated_by: "Research Ray"
direction_asserted: countercyclical
headline_template: "A"
indicator_category: credit
chart_refs:
  - hero
  - correlation
  - ccf
  - granger
  - local_projections
  - transfer_entropy
  - quantile
  - regime
  - quartile_returns
  - signal_timeseries
  - position_timeseries
  - equity_curves
  - equity_drawdown
  - tournament_scatter
  - trade_log_preview
  - history_zoom_dotcom
  - history_zoom_gfc
  - history_zoom_covid
  - history_zoom_inflation_2022
glossary_terms:
  - Buy-and-hold
  - Counter-cyclical
  - Drawdown
  - Forward return
  - Granger causality
  - Hidden Markov Model (HMM)
  - In-sample / Out-of-sample
  - Local projection
  - Quantile regression
  - Regime
  - Sharpe ratio
  - Tournament
  - Transfer entropy
  - Walk-forward validation
  - Z-score
  - Lagging indicator
  - Bootstrap p-value
  - Commercial & Industrial loans (C&I loans)
  - Credit-line drawdown
  - Specification curve
  - Exposure
historical_episodes_referenced:
  - episode_slug: dotcom
    override_needed: true
    override_reason: "Story §How the signal behaved in past crises — prose ties loan-growth peak (Jun-2000, after the SPY top) to the pair's own indicator series; pair-specific dual-panel overlay required."
    selection_rationale: confirmer
    prose_ref: "Story — Dot-Com paragraph"
  - episode_slug: gfc
    override_needed: true
    override_reason: "Story §How the signal behaved in past crises — prose cites the pair's indicator path (+21.5% YoY Apr-2008, −20.2% trough Feb-2010); pair-specific overlay required."
    selection_rationale: failure_case
    prose_ref: "Story — GFC paragraph"
  - episode_slug: covid
    override_needed: true
    override_reason: "Story §How the signal behaved in past crises — prose cites the pair's indicator spike (+30.1% YoY May-2020) against the SPY crash; pair-specific overlay required."
    selection_rationale: coincident
    prose_ref: "Story — COVID paragraph"
  - episode_slug: inflation_2022
    override_needed: true
    override_reason: "Story §How the signal behaved in past crises — prose cites the pair's indicator path (YoY rising to +14.6% Nov-2022 through the equity drawdown); pair-specific overlay required."
    selection_rationale: failure_case
    prose_ref: "Story — 2022 Rates Shock paragraph"
pages:
  story:
    headline: "Search-phase OOS Sharpe 1.50 vs 0.89 buy-and-hold, max drawdown −1.0% vs −23.9% (search window 2018-02–2026-05; no holdout test yet) — business loans turn out to FOLLOW the stock market, not lead it; what survives is a defensive overlay found by search, not a validated forecasting signal"
    sections:
      - {id: headline_findings, title: "Headline findings", anchor: "headline-findings"}
      - {id: hook, title: "The bank-loan paradox", anchor: "hook"}
      - {id: mechanism, title: "Why loans lag: the credit-line mechanism", anchor: "mechanism"}
      - {id: history_zoom, title: "How the signal behaved in past crises", anchor: "history-zoom"}
      - {id: what_survives, title: "What survives: a defensive overlay, honestly labelled", anchor: "what-survives"}
      - {id: takeaway, title: "What this means for investors", anchor: "takeaway"}
    expanders:
      - {id: what_is_a_ci_loan, title: "What exactly is a Commercial & Industrial loan?"}
      - {id: why_page_for_lagging_indicator, title: "Why would a 'lagging' indicator still be worth a dashboard page?"}
  evidence:
    headline: "Five independent tests agree: the stock market moves first, loan books respond"
    sections:
      - {id: evidence_overview, title: "What we tested and why", anchor: "evidence-overview"}
      - {id: correlation, title: "Correlation battery", anchor: "correlation"}
      - {id: granger, title: "Granger causality (Toda-Yamamoto)", anchor: "granger"}
      - {id: ccf, title: "Pre-whitened cross-correlation", anchor: "ccf"}
      - {id: local_projections, title: "Local projections", anchor: "local-projections"}
      - {id: transfer_entropy, title: "Transfer entropy", anchor: "transfer-entropy"}
      - {id: quantile, title: "Quantile regression", anchor: "quantile"}
      - {id: regime, title: "Regime context (HMM and quartiles)", anchor: "regime"}
      - {id: tournament_intro, title: "From evidence to strategy: the tournament", anchor: "tournament-intro"}
    expanders:
      - {id: what_is_prewhitening, title: "What does 'pre-whitened' mean, and why does it matter?"}
      - {id: why_toda_yamamoto, title: "Why Toda-Yamamoto instead of plain Granger?"}
  strategy:
    headline: "A long-or-cash overlay that sat out most of the last eight years — and avoided nearly all of the drawdown"
    sections:
      - {id: winner_overview, title: "The winning rule in plain English", anchor: "winner-overview"}
      - {id: signal_generation, title: "How the Signal is Generated", anchor: "signal-generation"}
      - {id: fragility, title: "Why we do not call this a validated edge", anchor: "fragility"}
      - {id: trade_log_howto, title: "How to Read the Trade Log", anchor: "trade-log-howto"}
      - {id: caveats, title: "Caveats", anchor: "caveats"}
    expanders:
      - {id: why_lower_return_higher_sharpe, title: "Why does the strategy give up return and still score a higher Sharpe ratio?"}
  methodology:
    headline: "How this page was built: data, transforms, tests, tournament"
    sections:
      - {id: data_sources, title: "Data sources", anchor: "data-sources"}
      - {id: indicator_construction, title: "Indicator construction", anchor: "indicator-construction"}
      - {id: methods_table, title: "Econometric methods", anchor: "methods-table"}
      - {id: tournament_design, title: "Tournament design", anchor: "tournament-design"}
      - {id: references, title: "References", anchor: "references"}
    expanders:
      - {id: reproducibility_notes, title: "Reproducibility notes"}
---

# Portal Narrative: busloans_spy

**Pair.** Commercial & Industrial Loans (C&I Loans, FRED series `BUSLOANS`) → S&P 500 (SPY). Monthly; indicator history from 1947, SPY-bound analytical sample 1993-02 onward (400 months). Mode 1, branch `fix260612_busloans_spy`.

**Evidence status (binding, per `results/busloans_spy/evidence_status.json`):** `found_in_search`. Every performance number on this page is a **search-phase** out-of-sample figure (window 2018-02-28 → 2026-05-31, 100 months, per `oos_split_record.json`). No holdout / final-exam test has been run yet. All KPI captions must carry the label **"Search-phase OOS Sharpe (no holdout test yet)"** per DPS-FE2 routing for this status.

**Direction asserted.** Countercyclical (the traded transform: the winning rule is long equities when loan growth is *weak*).

**RES-20 deviation (deliberate, flagged for Lead):** the episode set carries no `long_lead` entry because this pair's honest verdict is that the indicator has **no** lead — Granger, local projections, cross-correlation and transfer entropy all agree it lags. Asserting a long-lead episode would contradict the page's own evidence. Triad slots used: coincident (COVID), failure_case (GFC, 2022), confirmer (Dot-Com).

---

## Page 1+2 — The Story

### Headline findings (KPI card copy)

1. **Search-phase OOS Sharpe 1.50 vs 0.89 buy-and-hold** *(search 2018-02–2026-05; no holdout test yet)* — found as the best of 4,396 valid combinations; bootstrap p = 0.066, not significant at the 5% level.
2. **Max drawdown −1.0% vs −23.9% for buy-and-hold** *(search 2018-02–2026-05)* — almost the entire advantage comes from sitting in cash 75% of the time.
3. **Zero forward predictive power found** — loan growth did not help forecast S&P 500 (SPY) returns at any horizon from 1 to 12 months; the reverse relationship (stocks predicting loans) is significant at *every* lag.

### The bank-loan paradox (hook) {#hook}

Here is a fact that surprises almost everyone the first time: in the spring of 2020, while the S&P 500 (SPY) was crashing 30%, American businesses were borrowing from their banks at the fastest pace ever recorded — Commercial & Industrial (C&I) loan growth spiked above +30% year-over-year in May 2020. Loans boomed *while* the market collapsed. If you had treated rising business lending as a sign of economic health, you would have been buying confidence at exactly the wrong moment.

That paradox is the key to this entire page. We set out to test whether C&I loan growth predicts the stock market. The honest answer from every statistical test we ran: **it does not — the prediction runs the other way.** The stock market moves first, and bank loan books respond afterwards. C&I loans are, in fact, an official component of the Conference Board's *Lagging* Economic Index — and our data agrees with that classification emphatically.

**What this means:** this is a page about a *confirming* indicator, not a *warning* indicator. That is itself valuable knowledge — knowing which signals NOT to trade on is half of risk management. And, as we show on the Strategy page, a tournament search did surface one defensive use for the series — with caveats we spell out in full.

<!-- expander: What exactly is a Commercial & Industrial loan? -->
A Commercial & Industrial (C&I) loan is money a bank lends directly to a business — to fund inventory, payroll, equipment, or general operations. The Federal Reserve tallies the total outstanding across all US commercial banks every week in its H.8 release (FRED series `BUSLOANS`, in billions of dollars, seasonally adjusted). Think of it as the running balance on corporate America's collective credit card. Crucially, much of it is drawn from pre-arranged *credit lines* — which is why the balance can jump precisely when times get bad.
<!-- /expander -->

### Why loans lag: the credit-line mechanism {#mechanism}

Think of a business credit line like a homeowner's emergency credit card. You arrange it when times are good, and you *max it out* when trouble hits. That is exactly what firms do in aggregate:

- **Into a downturn**, firms draw down pre-arranged credit lines to stockpile cash ("revolver drawdowns") — so measured loan balances *rise* as the economy and the stock market fall. COVID is the textbook case (see the zoom-in chart below).
- **After a recession ends**, firms repay debt and banks tighten standards — so loan growth keeps *falling* well into the recovery. After the Global Financial Crisis (GFC), loan growth did not bottom until February 2010 (−20.2% year-over-year), almost a year after stocks had already turned up in March 2009 (see the GFC zoom-in chart).

**In plain English:** loan balances are a *thermometer reading taken after the fever* — they tell you how bad things were, not how bad they are about to get. The economically interesting *leading* series in this family is not the loans themselves but the banks' willingness to lend (the Fed's Senior Loan Officer Opinion Survey on lending standards) — a candidate flagged for a future pair in `analyst_suggestions.json`.

<!-- expander: Why would a 'lagging' indicator still be worth a dashboard page? -->
Three reasons. First, honesty: a leading-indicator catalogue earns trust by documenting what *doesn't* lead with the same rigor as what does. Second, confirmation value: a lagging series helps you date the cycle in hindsight and confirms whether a market move had a real-economy echo. Third, the search finding: even a lagging series can carry a usable *state* description — "loan growth is unusually weak" turns out to coincide with periods where holding equities was unusually safe in our 2018–2026 search window. Whether that survives a true holdout test is exactly the open question this page is careful not to prejudge.
<!-- /expander -->

### How the signal behaved in past crises {#history-zoom}

Four episodes, each with its zoom-in chart. Note what's missing from this list by design: there is **no episode where loans gave advance warning** — that's the verdict, not an omission.

**Dot-Com (2000-03 → 2002-10) — the lag, confirmed.** Year-over-year loan growth *peaked* at +11.9% in June 2000 — three months *after* the S&P 500 (SPY) had already topped in March 2000 — and then ground down for two years, bottoming at −8.8% in September 2002, essentially at the equity trough. A trader waiting for loan weakness as a sell signal would have been warned only after the bear market was nearly over — investors needed to act on other signals; this one confirmed the damage in arrears (see the Dot-Com zoom-in chart).

**GFC (2007-12 → 2009-06) — the failure case for forward warning.** The recession began in December 2007, yet loan growth was still *accelerating* to +21.5% year-over-year in April 2008 — partly genuine late-cycle borrowing, partly firms drawing credit lines as funding markets froze. The series then collapsed for two years, troughing at −20.2% in February 2010 — eleven months *after* equities had bottomed. An investor using loan growth as a health gauge would have been bullish into the crash and bearish through the recovery — the exact wrong posture both times (see the GFC zoom-in chart).

**COVID (2020-02 → 2020-12) — the signature coincident-inverse episode.** As the S&P 500 (SPY) fell ~34% top-to-bottom in five weeks, C&I loans spiked +25% to +30% year-over-year (peak +30.1% in May 2020) as firms drew their revolvers en masse. Loans and stocks moved violently in *opposite* directions at the *same* time — no lead either way. For the strategy on this page, the aftermath of this episode is where most of its measured edge lives: the rule went long SPY on 2020-04-30 (after the lagged signal entered its bottom quartile) and rode the recovery, posting an annualized Sharpe of 2.75 in this sub-period (per `subperiod_sharpe.csv`) — investors following the rule re-entered the market early in the rebound rather than predicting the crash (see the COVID zoom-in chart).

**2022 Rates Shock (2022-01 → 2022-12) — the failure case, again.** The Fed's fastest hiking cycle in four decades dragged the S&P 500 (SPY) down roughly 24% peak-to-trough, yet loan growth *rose* through the year to +14.6% by November 2022. No warning, no echo — the indicator was pro-cyclically cheerful through the whole bear market. The strategy happened to sit in cash for the entire episode (sub-period Sharpe 0.00 — flat, not a loss), avoiding the drawdown by construction rather than by foresight — investors following the rule were spared the bear market, but the *indicator* deserves no credit for predicting it (see the 2022 Rates Shock zoom-in chart).

### What survives: a defensive overlay, honestly labelled {#what-survives}

After 6,100 strategy combinations were searched (4,396 passing validity filters), the best rule found was: **be long the S&P 500 (SPY) only when month-over-month loan growth — observed with a 6-month delay — is in the bottom quartile of its trailing 36-month range; otherwise hold cash.** In the search window (2018-02 to 2026-05) that rule produced a Sharpe ratio of 1.50 versus 0.89 for buy-and-hold, with a maximum drawdown of just −1.0% versus −23.9%.

But this finding comes with non-negotiable context, stated here rather than in a footnote:

- It is the **best of 4,396** — and the **median** valid combination scored 0.74, *below* buy-and-hold's 0.89. Most things you could have tried with this indicator lose to doing nothing. The winner is the far tail of a large search.
- A bootstrap re-shuffle test puts the probability of a result this good arising by chance at **6.6%** — above the 5% bar we would want before calling it real.
- The rule looked unimpressive on pre-2018 data (in-sample Sharpe 0.35), its edge is concentrated in one episode (the COVID recovery), and it was in the market only 25% of the time.

**What this means:** treat this as *"a defensive pattern found by search, awaiting its final exam"* — not as a validated trading edge. The next step (per `evidence_status.json`) is a frozen-rule holdout test, and expectations for it should be calibrated low.

### What this means for investors (takeaway bullets) {#takeaway}

- **Do not use C&I loan growth as an early-warning signal** — in four major drawdowns since 2000 it warned of none of them; investors needing advance warning should look to leading credit measures such as the high-yield spread (covered in the HY-IG pair) instead.
- **Rising loan balances during a crash are not a bullish sign** — they are firms drawing emergency credit lines; investors should resist reading the COVID-style loan spike as corporate confidence.
- **Very weak loan growth has historically marked the *late* stage of the damage** — in the search window, being long equities only in such periods captured the recovery while avoiding turbulence; investors may treat depressed loan growth as one input to a "the worst may be behind us" checklist, not as a standalone trigger.
- **The strategy's profile is drawdown-avoidance, not return-seeking** — it gave up 4.2 percentage points of annual return versus buy-and-hold (10.7% vs 14.8%) in exchange for a 23-point smaller maximum drawdown; investors whose priority is compounding total return would have been better off holding the index.

---

## Page 3 — The Evidence

### What we tested and why {#evidence-overview}

One question, attacked five independent ways: *does C&I loan growth carry information about future S&P 500 (SPY) returns — or is it the other way round?* Methods that agree from different angles are far more convincing than any single test. Here, all five angles agree — in the direction nobody trades on.

All statistics computed on monthly data, SPY-bound sample 1993-02 → 2026-05 (400 months), from `results/busloans_spy/core_models_20260612/`.

### Method block: Correlation battery {#correlation}

1. **The Method:** Pearson and Spearman correlations between every loan-growth transform (month-over-month, year-over-year, z-scores, contraction flags) and forward SPY returns at 1/3/6/12-month horizons.
2. **The Question It Answers:** *Is there any raw statistical association between loan growth today and stock returns tomorrow?*
3. **How to Read the Graph:** Rows are signal transforms, columns are forward-return horizons; each cell's color shows the correlation — red negative, blue positive, deeper color = stronger. Values near zero (pale cells) mean no association.
4. **[Graph: correlation heatmap]** `chart_status: "ready"`
5. **Observation:** The grid is overwhelmingly pale. The strongest cell is the 60-month z-score of year-over-year growth versus 12-month forward returns, at r = 0.225 — modest, positive, and only at the longest horizon.
6. **Deep Dive (expander):** Forward returns at overlapping horizons induce serial correlation in the cells; treat the heatmap as descriptive triage rather than inference — the formal tests below carry the inferential weight.
7. **Interpretation:** The one modest cell is a *level-of-cycle* effect: when loan growth has been depressed for years (deeply negative z-score), the economy is typically late in a recession and subsequent multi-year equity returns are above average. That is consistent with the lagging story, not with short-horizon predictability.
8. **Key Message:** **At every tradeable horizon, the raw association between loan growth and future stock returns is close to zero.**

### Method block: Granger causality (Toda-Yamamoto) {#granger}

1. **The Method:** Granger causality (a statistical test of whether one series helps forecast another beyond the other's own history), in the Toda-Yamamoto form that stays valid even if the series' trends are imperfectly removed.
2. **The Question It Answers:** *Who moves first — business loans or the stock market?*
3. **How to Read the Graph:** Bars show the test statistic at each lag from 1 to 12 months, one panel per direction; bars clearing the dashed significance line indicate forecasting power at that lag.
4. **[Graph: Granger by-lag bars, both directions]** `chart_status: "ready"`
5. **Observation:** In the loans → SPY direction, no bar at any of the 12 lags clears the line (smallest p-value 0.257, at lag 5). In the SPY → loans direction, *every* bar from lag 1 to 12 clears it (largest p-value 0.0115).
6. **Deep Dive (expander):** Why Toda-Yamamoto instead of plain Granger? Plain Granger tests can produce spurious results when series have unit roots or borderline stationarity; Toda-Yamamoto augments the underlying model with extra lags (d_max = 1 here) so the test statistic keeps its standard distribution regardless. We run it on the stationary year-over-year transform.
7. **Interpretation:** This is as one-sided as lead-lag evidence gets: a clean reject in one direction at every lag, a clean non-reject in the other at every lag. Stock prices aggregate forward-looking information in real time; loan books respond with the mechanical delays of corporate borrowing decisions and bank credit committees.
8. **Key Message:** **The stock market predicts business loans at every lag tested; business loans predict the stock market at none.**

### Method block: Pre-whitened cross-correlation {#ccf}

1. **The Method:** A pre-whitened Cross-Correlation Function (CCF) — correlation between the two series at every monthly offset from −20 to +20, after filtering each series' own autocorrelation so trends cannot masquerade as lead-lag structure.
2. **The Question It Answers:** *At which specific monthly offsets, if any, do the two series echo each other?*
3. **How to Read the Graph:** The X-axis is the offset in months — negative offsets mean loans move before stocks, positive offsets mean stocks move before loans. Bars outside the dashed band are statistically significant at 95% confidence.
4. **[Graph: CCF bars ±CI]** `chart_status: "ready"`
5. **Observation:** Of 41 offsets, a single bar (+17 months, correlation 0.119) pokes above the band on the stocks-lead side; nothing is significant on the loans-lead side.
6. **Interpretation:** With 41 offsets tested at 95% confidence, roughly two false alarms are expected by chance alone — one stray bar at an economically arbitrary +17 months is noise, not signal. The CCF therefore corroborates the Granger result: no loans-lead structure exists at any monthly offset.
7. **Key Message:** **Across 41 monthly offsets, there is no credible window in which loan growth foreshadows stock returns.**

### Method block: Local projections {#local-projections}

1. **The Method:** Local projections (a horizon-by-horizon regression technique that traces how one variable responds after a movement in another), with HAC standard errors robust to overlapping horizons.
2. **The Question It Answers:** *If loan growth jumps today, where is the stock market 1, 3, 6, and 12 months later?*
3. **How to Read the Graph:** Each panel plots the estimated response (line) with its confidence band (shading) across horizons; a band that straddles zero means no detectable effect.
4. **[Graph: impulse-response panels, forward + reverse]** `chart_status: "ready"`
5. **Observation:** In the loans → SPY panel the band straddles zero everywhere (all p-values above 0.81). Point estimates in the reverse direction are negative at short horizons but also not significant.
6. **Interpretation:** Even granting the indicator its best shot — any horizon, robust errors — there is no detectable forward effect. The translation: nothing here for a forecaster.
7. **Key Message:** **A jump in loan growth tells you nothing statistically useful about where stocks will be up to a year later.**

### Method block: Transfer entropy {#transfer-entropy}

1. **The Method:** Transfer entropy — a model-free measure of directed information flow that can detect *non-linear* relationships ordinary correlation misses (estimated on tercile-binned data with 500 permutations).
2. **The Question It Answers:** *Could loans predict stocks in some curvy, non-linear way the linear tests can't see?*
3. **How to Read the Graph:** Two bars — one per direction; the annotation shows each bar's permutation p-value. A small p-value (under 0.05) would indicate genuine information flow.
4. **[Graph: two-bar TE comparison]** `chart_status: "ready"`
5. **Observation:** Loans → SPY: p = 0.81. SPY → loans: p = 0.50. Neither direction is significant.
6. **Interpretation:** No hidden non-linear channel rescues the indicator. (That the reverse direction is also insignificant here, while strongly significant under Granger, simply reflects transfer entropy's lower power on 400 coarsely-binned monthly observations — the linear test is the sharper instrument for the reverse channel.)
7. **Key Message:** **There is no non-linear escape hatch — the absence of forward predictability is robust to how you look.**

### Method block: Quantile regression {#quantile}

1. **The Method:** Quantile regression — instead of asking how loan growth affects the *average* future return, it asks how it affects the *worst* and *best* outcomes (the tails), where risk signals usually earn their keep.
2. **The Question It Answers:** *Does weak loan growth at least predict tail risk — the really bad months — even if it can't predict the average?*
3. **How to Read the Graph:** The X-axis runs across outcome percentiles (5th = worst months, 95th = best); the line is the estimated effect at each percentile with its confidence band. A risk signal typically shows a significant effect at the left tail.
4. **[Graph: coefficient-by-tau with CI band]** `chart_status: "ready"`
5. **Observation:** The confidence band straddles zero at every percentile from the 5th to the 95th.
6. **Interpretation:** Many credit indicators fail at the mean but work at the left tail. This one fails at both — loan growth does not even flag elevated crash risk.
7. **Key Message:** **Loan growth predicts neither average stock returns nor tail risk.**

### Method block: Regime context (HMM and quartiles) {#regime}

1. **The Method:** A two-state Hidden Markov Model (HMM — a statistical model that infers unobserved "calm" vs "stressed" regimes from the data's behavior) fitted to the loan series, plus a simple sort of history into quartiles of loan growth with the forward SPY return reported in each.
2. **The Question It Answers:** *Even without prediction, do states of the loan cycle coincide with systematically different stock-market environments?*
3. **How to Read the Graph:** The HMM panel shades periods by inferred regime probability over time; the quartile chart shows annualized forward SPY returns in four bars, sorted from weakest (Q1) to strongest (Q4) loan growth.
4. **[Graph: HMM regime timeline; regime quartile return bars]** `chart_status: "ready"`
5. **Observation:** The HMM's stressed state aligns with the *aftermaths* of recessions (2002–04, 2009–11, 2020–21) rather than their onsets. The quartile bars show the pattern the tournament later exploits: forward returns are healthiest when loan growth sits in its weakest quartile.
6. **Deep Dive (expander):** Rolling 24-month correlation between the two series flips sign repeatedly across the sample (sign-agreement score 0.42 in `rolling_correlation_busloans_spy.csv`) — the *state* relationship is real but its month-to-month direction is unstable, one of the fragility flags carried to the Strategy page.
7. **Interpretation:** This is the constructive reading of a lagging series: weak loan growth describes a *post-stress* state of the world in which much of the equity damage has already happened. Descriptive, conditional, and regime-dependent — not a forecast.
8. **Key Message:** **Loan growth doesn't predict the market, but its weakest readings have historically marked late-stage damage — the one regularity the strategy search latched onto.**

### From evidence to strategy: the tournament {#tournament-intro}

The statistical tests above ask whether the indicator *predicts*. The tournament asks a more pragmatic question: across every reasonable trading rule you could build from this series, does *any* of them beat simply holding the S&P 500 (SPY)?

We tested a grid of **6,100 strategy combinations** — 11 signal transforms × multiple threshold schemes × 3 strategy families × 2 orientations × 5 signal delays × 3 lookback windows — of which **4,396 passed validity filters** (out-of-sample Sharpe above 0.3, fewer than 24 trades per year, at least 24 out-of-sample months; the buy-and-hold benchmark row is excluded from this count). The headline rule on the Strategy page is the **best of those 4,396** — rank 1, with no ties. Position disclosure, per our specification-curve standard: the **median** valid combination scored an out-of-sample Sharpe of just **0.74 — below buy-and-hold's 0.89**. In plain English: most rules you could have built from this indicator lose to doing nothing, and the winner is the far tail of a large search. That is exactly why the next page reports it as "found in search, not yet validated out of search."

---

## Page 4 — The Strategy

### The winning rule in plain English {#winner-overview}

**Rule:** Hold the S&P 500 (SPY) **only when month-over-month C&I loan growth — observed with a 6-month delay — sits in the bottom quartile of its own trailing 36-month range. Otherwise hold cash.** (Family: Long/Cash, countercyclical orientation; signal `busloans_mom`, threshold T2 rolling 25th percentile, lead L6, lookback LB36 — per `winner_summary.json`.)

If-then form:
- **IF** the 6-month-old reading of monthly loan growth is in the weakest 25% of its last 36 months → **BUY/HOLD SPY (100% invested)**.
- **ELSE** → **HOLD CASH (0% invested)**.

Search-phase results (2018-02 → 2026-05, 100 months — **no holdout test yet**): Sharpe 1.50 vs 0.89 buy-and-hold; annualized return 10.7% vs 14.8% (the strategy *gives up* 4.2 points of return); maximum drawdown −1.0% vs −23.9%; 24 position changes (turnover 2.88 per year); average market exposure 25%.

**The character of this rule is drawdown-avoidance, not return-seeking.** It is in cash three-quarters of the time, accepts a lower total return, and wins on risk-adjusted terms almost entirely by missing the bad stretches. That is why this pair's `strategy_objective` is classified as **min_mdd** (minimize maximum drawdown).

<!-- expander: Why does the strategy give up return and still score a higher Sharpe ratio? -->
The Sharpe ratio rewards return *per unit of volatility*. Cash has almost no volatility, so a strategy that is long only 25% of the time and picks a calm-but-rising stretch (here, mostly the post-COVID recovery) earns a modest return at a tiny volatility — 7.1% annualized versus roughly triple that for the index. Divide a decent numerator by a small denominator and the ratio looks excellent. This is legitimate as far as it goes, but it means the Sharpe figure should not be read as "this rule beats the market" — an investor compounding wealth got 10.7% per year from the rule versus 14.8% from buy-and-hold.
<!-- /expander -->

### How the Signal is Generated {#signal-generation}

No formulas — three steps:

**What changes in the world:** businesses collectively slow their bank borrowing — typically late in a downturn, after the damage is done, when firms are repaying emergency credit-line drawdowns and banks have tightened standards.

**What the signal measures:** each month, the rule looks at the *month-over-month* change in total C&I loans as it stood six months ago (the delay reflects both the realistic information lag and, mainly, the tournament's finding that the 6-month-old reading worked best in search). It then asks one question: is that reading among the weakest quarter of the past three years?

**What decision it drives:** weakest-quarter reading → be in the market; anything stronger → stay in cash. The logic the search stumbled onto is the regime pattern from the Evidence page: deeply depressed loan growth has historically marked the *aftermath* of stress, when recoveries were under way — while "normal or booming" loan growth carried no such safety stamp.

### Why we do not call this a validated edge {#fragility}

Five flags, none softened (all from `winner_summary.json` and the tournament validation set):

1. **Search-position.** Best of 4,396 valid combinations; the median combination (Sharpe 0.74) *underperforms* buy-and-hold (0.89). The winner is the extreme tail of a wide search, which is precisely the condition under which lucky rules look brilliant.
2. **Bootstrap p = 0.066.** A re-shuffle test says a result this good arises by chance about 6.6% of the time — above the conventional 5% threshold. Not statistically significant.
3. **In-sample vs out-of-sample inversion.** The rule scored Sharpe 0.35 on pre-2018 data and 1.50 after. Robust edges usually look at least decent in both windows; an OOS figure four times the IS figure suggests a favorable draw, not a stable property.
4. **Episode concentration.** The durability check classifies the edge as `episode_concentrated`: the COVID-recovery sub-period delivered Sharpe 2.75; the 2022 episode was spent entirely in cash (Sharpe 0.00 — flat, not a loss); Dot-Com and GFC fall outside the search window entirely (insufficient data).
5. **Sign instability.** The rolling 24-month correlation between indicator and market flips sign chronically (sign-agreement 0.42) — the relationship the rule rides is not even directionally stable over time.

**What this means:** the honest label, from `evidence_status.json`, is **`found_in_search`** — "the best rule we found by searching, not a rule that has passed an independent test." The prescribed next step is a final exam: freeze this rule, wait for (or carve out) a window the search never touched, and test it once. Given the flags above and the lagging-indicator verdict, expectations should be calibrated low.

### How to Read the Trade Log {#trade-log-howto}

This is a **simulated** backtest record — no real trades were executed. Two files are available for download: the **broker-style log** (`winner_trades_broker_style.csv`, 84 events — user-friendly, one row per buy or sell with prices and running profit) and the **position log** (`winner_trade_log.csv`, 400 rows — one row per month, for researchers who want to verify the signal arithmetic).

Key broker-style columns: `trade_date` (when the position changed), `side` (BUY = move into SPY, SELL = move to cash), `quantity_pct` (the resulting exposure, 100% or 0%), `price` (SPY at execution), `commission_bps` (the 5-basis-point assumed cost), `cum_pnl_pct` (cumulative profit on $10,000 starting capital), and `reason` (the signal reading that triggered the change).

**A concrete example from this pair:** on **2020-04-30** the log records a BUY — the 6-month-lagged monthly loan growth reading (0.000) had fallen below its rolling bottom-quartile threshold (0.101), so the position moved from 0% to 100% just as the post-COVID recovery began. The matching SELL appears on **2020-09-30**, when the lagged window caught the +9.1% COVID credit-line spike and the signal jumped far above threshold, sending the strategy back to cash. You can find both rows in the broker-style CSV.

### Caveats {#caveats}

- **No forward causality.** Every lead-lag test on the Evidence page says the market leads the loans. Any rule built on this series is reading the market's own echo at a delay.
- **Search-phase numbers only.** Selection and evaluation share the same 2018–2026 window; no holdout exam has been run. The Sharpe 1.50 headline is a candidate, not a verdict.
- **Low exposure profile.** At 25% average exposure, results are dominated by *when the rule happened to be in* — a handful of months drive everything.
- **Return give-up.** The rule trails buy-and-hold by 4.2 points of annual return; it is a drawdown-avoidance overlay, unsuitable as a core compounding strategy.
- **Costs.** Returns are gross of costs; at the assumed 5 basis points per trade and 2.88 trades per year, the haircut is negligible (see `tournament_validation_20260612/transaction_costs.csv`) — cost drag is *not* one of this pair's problems.
- **No structural break flagged** (sup-F test p = 0.30), so the fragility flags above cannot be excused by a regime change in the data.

---

## Page 5 — The Methodology

### Data sources {#data-sources}

| Category | Source | Series | Frequency |
|---|---|---|---|
| Indicator | FRED — Federal Reserve H.8, Assets & Liabilities of Commercial Banks | `BUSLOANS` (C&I loans outstanding, all commercial banks, $bn, seasonally adjusted) | Monthly (from 1947-01) |
| Target | Yahoo Finance | SPY (SPDR S&P 500 ETF, dividend-adjusted) | Monthly (from 1993-02) |

Dataset: `data/busloans_spy_monthly_19470131_20260531.parquet` (Dana; episode-verified against the COVID spike, the 2009-10 trough, and z-score recomputation).

### Indicator construction {#indicator-construction}

Raw loans outstanding are non-stationary in levels, so all analysis runs on growth-rate transforms: month-over-month % change (`busloans_pct_mom` — the winning signal), year-over-year % change (the cycle gauge), 3-month annualized growth, rolling z-scores at multiple windows, and binary contraction flags. The publication lag of the H.8 release (~2–3 weeks) means a 1-month signal delay is the real-time floor; the tournament grid therefore starts at lead L1.

### Econometric methods {#methods-table}

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

### Tournament design {#tournament-design}

Grid: 11 signals (9 data transforms + HMM stress state + Markov regime) × threshold schemes (fixed percentiles, rolling percentiles, z-score bands, zero-line) × 3 strategy families (Long/Cash, signal-strength scaling, Long/Short) × 2 orientations (procyclical/countercyclical — both tested per the mixed prior) × leads {1, 2, 3, 6, 12} months × lookbacks {36, 60, 120} months = 6,100 combinations plus a buy-and-hold benchmark row. Validity filters: OOS Sharpe > 0.3, turnover < 24/yr, ≥ 24 OOS months → 4,396 valid. Out-of-sample split per policy `v1_max36_25pct_cap120`: in-sample through 2018-01, out-of-sample 2018-02 → 2026-05 (100 of 400 SPY-bound months). Winner selected by the standard cascade, resolved at step 1 with no tie. All metrics in the tournament CSV are decimal ratios, not percentages.

<!-- expander: Reproducibility notes -->
Producer script: `scripts/pair_pipeline_busloans_spy.py` — deterministic, fixed seeds; a rerun reproduces every number on this page. The canonical monthly return series for chart producers is `strategy_returns_20260612.csv` (position on row *t* is the accrual weight for month *t*, signal already lagged 6 months); its Sharpe/drawdown/return reconcile with `winner_summary.json` to within 1e-4. Stationarity tests were produced by the data stage and confirmed, not re-run, by the econometrics stage.
<!-- /expander -->

### References {#references}

1. Conference Board, *Business Cycle Indicators Handbook* — C&I loans outstanding as a component of the Lagging Economic Index.
2. Toda, H. Y. & Yamamoto, T. (1995). "Statistical inference in vector autoregressions with possibly integrated processes." *Journal of Econometrics*, 66(1–2), 225–250.
3. Jordà, Ò. (2005). "Estimation and inference of impulse responses by local projections." *American Economic Review*, 95(1), 161–182.
4. Ivashina, V. & Scharfstein, D. (2010). "Bank lending during the financial crisis of 2008." *Journal of Financial Economics*, 97(3), 319–338 — credit-line drawdowns rising into downturns.
5. Li, L., Strahan, P. E. & Zhang, S. (2020). "Banks as lenders of first resort: evidence from the COVID-19 crisis." *Review of Corporate Finance Studies*, 9(3), 472–500 — the 2020 revolver-drawdown spike.
6. Simonsohn, U., Simmons, J. P. & Nelson, L. D. (2020). "Specification curve analysis." *Nature Human Behaviour*, 4, 1208–1214 — basis for the best-of-N position disclosure.
7. Bailey, D. H. & López de Prado, M. (2014). "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality." *Journal of Portfolio Management*, 40(5), 94–107.

---

## Config prose blocks (for Ace's `app/pair_configs/busloans_spy_config.py` — APP-PT1)

Ace ports these verbatim; structural config is Ace's lane.

### HISTORY_ZOOM_EPISODES

```python
HISTORY_ZOOM_EPISODES = [
    {
        "slug": "dotcom",
        "title": "Dot-Com Crash (2000–2002)",
        "narrative": "Loan growth peaked three months AFTER the equity top (Jun-2000) and bottomed two and a half years later, right at the equity trough — textbook lagging behavior. A reader waiting for loan weakness as a warning was warned only once the bear market was nearly over.",
        "caption": "Loan growth peaked after the SPY top — confirmation in arrears, no warning",
    },
    {
        "slug": "gfc",
        "title": "GFC (2007–2009)",
        "narrative": "Loan growth was still accelerating four months into the recession as firms drew credit lines, then collapsed for two years, troughing 11 months after equities had already bottomed. As a forward signal this is the failure case: bullish into the crash, bearish through the recovery.",
        "caption": "Failure case — loans accelerated into the crash, troughed after the recovery began",
    },
    {
        "slug": "covid",
        "title": "COVID Shock (2020)",
        "narrative": "C&I loans spiked at a record pace while SPY crashed — firms maxing out emergency credit lines, not expressing confidence. Loans and equities moved violently in opposite directions at the same time: coincident-inverse, with no lead either way.",
        "caption": "Coincident-inverse — record loan spike during the equity crash (credit-line drawdowns)",
    },
    {
        "slug": "inflation_2022",
        "title": "2022 Rates Shock",
        "narrative": "Loan growth rose through the entire Fed-driven equity drawdown, giving no warning and no echo. The strategy sat in cash all year by construction (flat, not a loss) — spared the bear market without the indicator deserving any predictive credit.",
        "caption": "Failure case — loan growth rose while SPY fell ~24%; strategy was in cash throughout",
    },
]
```

### story_md_intro

> In the spring of 2020, while the stock market was crashing, American businesses were borrowing from their banks at the fastest pace ever recorded. That paradox is the key to this page: business loans don't predict the market — they respond to it. We tested the relationship every way we know how, and the verdict is unusually clean: the S&P 500 (SPY) forecasts Commercial & Industrial (C&I) loans at every horizon; the loans forecast nothing. What survives is a modest defensive pattern found by search — presented here with its warning labels attached.

### story_md_mechanism

> Think of a business credit line as a company's emergency credit card: arranged in good times, maxed out when trouble hits. So when the economy turns down, measured loan balances *rise* (firms drawing emergency cash), and after recessions end they keep *falling* (repayment and tighter bank standards) long into the recovery. The thermometer reads the fever after it has broken. That is why C&I loans sit in the Conference Board's *Lagging* Economic Index — and why this page is honest about being a study of a confirming indicator, not a warning one.

### strategy_eli5_winner

> The winning rule from a 4,396-combination search: hold the S&P 500 (SPY) only when monthly loan growth — viewed with a 6-month delay — is in the weakest quarter of its past three years; otherwise hold cash. In the search window (2018–2026) it scored a Sharpe ratio of 1.50 versus 0.89 for buy-and-hold and lost at most 1% from peak versus 24% — but it earned less in total (10.7% vs 14.8% a year), sat in cash 75% of the time, and fails the standard significance test (bootstrap p = 0.066). The typical rule in the same search scored *below* buy-and-hold. Read it as a drawdown-avoidance overlay found by search — its final exam on untouched data has not yet been run.

### methodology_eli5

> One monthly data series from the Federal Reserve (total business loans at US banks, back to 1947) and the S&P 500 ETF (SPY, back to 1993). We turned the loans into growth rates, ran five independent lead-lag tests (all agree: stocks lead, loans follow), then searched 6,100 trading-rule combinations on data split so that rules were built on pre-2018 history and scored on 2018–2026. Every number on these pages can be reproduced by one deterministic script.
