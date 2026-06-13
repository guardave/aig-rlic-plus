# Portal Narrative — Lead Analysis + Lead Tournament Blocks (fix260613_lead_horizon)

**Author:** Research Ray <research-ray@idficient.com>
**Date:** 2026-06-13
**Branch:** `fix260613_lead_horizon` — Mode 1, Track A
**Rules:** ECON-LA1, ECON-LT1, ECON-LL1 (universal monthly lead grid L=0..12), DPS-CPX1 (CP relocation, §B below).
**Scope:** the 8 non-frozen pairs. Frozen Sample `hy_ig_v2_spy` EXEMPT. `permit_spy` is the REFERENCE — its two blocks already exist (vichua, gold standard); leave as-is. Prose below is delivered for the other 7 pairs.

**Grounding:** every number and every categorical "which lead wins" claim re-read at authoring time from `results/{pair}/lead_correlation_20260613.csv` and `results/{pair}/lead_tournament_20260613.csv`, cross-checked against `results/_cross_agent/lead_horizon_gate_20260613.csv`. Per prose-vs-data, the WORDS ("wins", "diverges", "agrees") are data-derived, not assumed.

---

## Gate summary (the honest spine of this wave)

| Pair | Published lead | Tournament L\* (L0-12) | Best Sharpe @ L\* | Published Sharpe | Decision | Corr best-lead region |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| indpro_spy | 6 | **12** | 1.374 | 1.104 | **RE-RUN** | L4 (mom), broad |
| permit_spy *(ref)* | 6 | 6 | 1.445 | 1.445 | CHARTS-ONLY | L8-9 |
| vix_vix3m_spy | 0 | **3** | 1.869 | 1.130 | CHARTS-ONLY | L5-6 |
| indpro_xlp | 3 | **8** | 1.423 | 1.115 | **RE-RUN** | L3/L8 (accel) |
| hy_ig_spy | 0 | **1** | 1.439 | 1.408 | CHARTS-ONLY | L1-2 |
| umcsent_xlv | 6 | **11** | 1.188 | 1.020 | **RE-RUN** | L4-5 |
| gold_copper_xli | 0 | **10** | 1.370 | 1.273 | **RE-RUN** | L0 / L5 |
| busloans_spy | 6 | 5 | 1.500 | 1.500 | CHARTS-ONLY | L5-6 (weak) |

**Honest framing per gate (ECON-LT1):** L\* ∈ {7..12} → the extended grid found a better winner the published report missed → **RE-RUN** (4 pairs). L\* ∈ {0..6} → published winner's lead region still wins → **CHARTS-ONLY** (4 pairs: vix, hy_ig_spy, busloans, permit-ref). Note `vix` and `hy_ig_spy` move L\* (3 and 1) but stay in the ≤6 region, so they are charts-only — the better-Sharpe lead is still inside the published lead's region, not in the {7..12} band that would force a re-run.

**RE-RUN flag for Ace/Lead:** the four RE-RUN pairs' Lead-Tournament blocks below are written to be TRUTHFUL NOW about the *analysis finding* (a better lead exists at L\*). Their FINAL published numbers (winner Sharpe, signal/threshold/strategy at the adopted lead, max DD) are **PENDING the Track-B re-run** — these blocks must be refreshed with the re-run's `winner_summary.json` before acceptance. Each is tagged `[NUMBERS PENDING RE-RUN]`. The charts-only pairs are final NOW.

---

## A. Lead Analysis + Lead Tournament block prose (per pair)

Each pair gets two 8-element Evidence method blocks (`Lead Analysis` → chart `correlations_lead_view`; `Lead Tournament` → chart `lead_sharpe_distribution`). Element order matches the reference: `method_theory`, `question`, `how_to_read`, `chart_name`, `chart_caption`, `observation`, `interpretation`, `key_message`. Ace ports these into each config's `EVIDENCE_METHOD_BLOCKS.level1` list (append after the Correlation block, mirroring permit_spy's `level1` + `level1_labels`).

---

### A.1 indpro_spy — INDPRO → SPY  **[RE-RUN — NUMBERS PENDING RE-RUN]**

#### CORRELATION_LEAD_VIEW_BLOCK ("Lead Analysis")

- **method_theory:** "The Correlation block above varies the forward-return horizon (1m/3m/6m/12m) at zero signal lag — the economist's question. A monthly-rebalanced strategy needs a different answer: how stale may the Industrial Production signal get before we trade on it? That is a *lead* question. For each INDPRO transform we compute Pearson r between the signal lagged L = 0..12 months and SPY's 1-month forward return, then read off the lead that maximises predictive content."
- **question:** "If we trade against next month's SPY return, how many months should we lag the INDPRO signal — and does the tournament's published lead of 6 months line up with the data?"
- **how_to_read:** "Rows are INDPRO signal transforms; columns are signal lead in months (L0 = contemporaneous, L12 = signal from a year ago). Forward-return horizon is fixed at 1 month. Cell shading is Pearson r against `spy_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01. The 'best lead' for a row is the column with the largest |r|."
- **chart_name:** `correlations_lead_view`
- **chart_caption:** "Pearson r between INDPRO signal lagged L months (columns, L=0..12) and SPY 1-month forward return. The single strongest cell in the whole grid is `indpro_mom` at **L4 (r=+0.150**)** — the only highly-significant positive lead. Most other transforms are weak and unsigned-stable across leads; `indpro_accel` shows a significant *negative* cell at L3 (−0.144**) and a significant positive at L4 (+0.123*); `indpro_contraction` turns weakly positive far out (L11, +0.108*)."
- **observation:** "Reading the chart directly: the predictive content is thin and scattered, not concentrated at one clean lead. The one robust positive signal is `indpro_mom` at L4 (r=+0.150**). At L6 — the published tournament lead — every transform is weak: `indpro_yoy` −0.025, `indpro_mom` −0.023, `indpro_zscore_60m` −0.063 (the row's own peak, but tiny), `indpro_contraction` +0.018. There is no L6 correlation peak to speak of."
- **interpretation:** "Two implications. First, the correlation diagnostic does **not** endorse the published L=6 lead — the strongest linear signal sits at **L=4** on momentum, and the published lead's column is among the weakest. Second — and this is the finding that drives the gate — when the full tournament is swept across L=0..12 (next block), the best risk-adjusted lead is **not** L6 either: it migrates all the way to **L=12**. The correlation view says 'short lead on momentum'; the tournament says 'long lead on a different transform'. The two diagnostics disagree on the exact lead, but they **agree the published L=6 is not the natural choice** — which is why this pair is being re-run."
- **key_message:** "The lead-correlation view diverges from the published 6-month lead: the cleanest linear signal is `indpro_mom` at **L=4**, and no transform peaks at L=6. Combined with the tournament's L=12 winner (next block), the published lead is stale — **this pair is being re-run** on the extended grid."

#### LEAD_TOURNAMENT_BLOCK ("Lead Tournament")  **[NUMBERS PENDING RE-RUN]**

- **method_theory:** "The Lead Analysis shows what the correlations prefer; this block shows what the *tournament* prefers when lead is swept exhaustively. We re-ran the full (signal × threshold × strategy × lookback) tournament across the complete monthly grid L=0..12 (the original tested only a coarse subset). The chart plots, per lead, the single best OOS Sharpe at that lead (bar) over the cloud of all valid combos (strip), with SPY buy-and-hold (0.90) dashed."
- **question:** "Is the published L=6 winner a tall single peak, or does a better lead exist further out that the original coarse grid missed?"
- **how_to_read:** "Bars: max OOS Sharpe at each lead. Strip dots: every valid combination at that lead. A tall thin spike is a single lucky combo; a flat-wide cloud is a robust regime."
- **chart_name:** `lead_sharpe_distribution`
- **chart_caption:** "Best OOS Sharpe per lead (bars) over the full combo distribution (strip). The maximum across the whole grid is **L=12 (1.374)**, not the published L=6 (1.128). A second high cluster sits at **L=8 (1.349)**. Leads L=4 (1.174), L=7 (1.169) and L=11 (1.265) also clear the published L=6. Every lead beats buy-and-hold (0.90)."
- **observation:** "Reading the bars: L=12 is the single highest (1.374), with L=8 close behind (1.349) and L=11 third (1.265). The published L=6 (1.128) is mid-pack — it is beaten by **six** other leads (L4, L7, L8, L9, L11, L12). Reading the strip: the median valid combo rises with lead (0.64 at L0 → 0.71-0.79 at L8-12), so longer leads are not just luckier peaks — the whole cloud lifts."
- **interpretation:** "The extended grid found a winner the published report missed: **L=12 at Sharpe 1.374 (`indpro_mom_6m` / Tp75_lo / P2)** versus the published L=6 winner at 1.128. Because L\*=12 lands in the {7..12} band, the ECON-LT1 gate fires — the published winner is stale and **the pair is being re-run** to adopt the extended-grid winner. **[NUMBERS PENDING RE-RUN]** — the final winner Sharpe, signal/threshold/strategy and max DD at the adopted lead will be reconciled from the re-run's `winner_summary.json`; treat 1.374 / L12 / mom_6m as the *analysis finding*, not the final published figure."
- **key_message:** "Sweeping the full L=0..12 grid moves the best lead from the published **6** to **12** (Sharpe 1.13 → 1.37), with a secondary peak at L=8. The published lead is no longer the winner — **this pair is being re-run** to adopt the L=12 configuration."

---

### A.2 vix_vix3m_spy — VIX/VIX3M → SPY  **[CHARTS-ONLY — FINAL]**

#### CORRELATION_LEAD_VIEW_BLOCK ("Lead Analysis")

- **method_theory:** "The Correlation block above fixes the signal at zero lag and varies the forward horizon. A daily-rebalanced overlay still has to answer a monthly *lead* question (ECON-LL1: one month of lead ≈ 21 trading days, so the daily ratio is shifted by L×21 days). For each VIX-term-structure transform we compute Pearson r between the signal lagged L=0..12 months and SPY's 1-month forward return."
- **question:** "How stale may the VIX/VIX3M signal get before it stops predicting next month's SPY return — and does the data support the published same-day (L=0) lead?"
- **how_to_read:** "Rows are VIX term-structure transforms; columns are signal lead in months. Forward horizon fixed at 1 month. Shading is Pearson r against `spy_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
- **chart_name:** `correlations_lead_view`
- **chart_caption:** "Pearson r between VIX-term-structure signal lagged L months and SPY 1-month forward return. The strongest cells sit at **L=5-6**: `vix_ratio_zscore_126d` at L6 is −0.194**, `vix_ratio_roc_21d` at L5 is +0.179**, `vix_ratio_mom_21d` at L5 +0.172*, `vix_term_spread` at L6 +0.151*. The contemporaneous column (L0, the published lead) is uniformly weak (|r| < 0.08)."
- **observation:** "Reading directly: the level/z-score transforms (`vix_ratio`, `vix_ratio_zscore_126d`, `pctrank_252d`) all carry their strongest cell as a **negative** r at **L6** (more backwardation 6 months ago → lower forward returns, the counter-cyclical sign). The momentum/RoC transforms peak **positive at L5**. At L0 — where the published winner trades — correlations are near zero, consistent with VIX term-structure being a fast, noisy same-day signal whose linear predictive content actually concentrates a few months out."
- **interpretation:** "The lead-correlation view diverges from the published **L=0** lead: linear predictability concentrates at **L=5-6**, not contemporaneously. But — crucially — this divergence does **not** trigger a re-run. The tournament (next block) finds its best Sharpe at **L=3**, still inside the published lead's near-term region (L\* ≤ 6), so the published winner's lead region holds and this pair is **charts-only**. The honest read: the *correlation* is strongest at a 5-6 month lead, while the *traded edge* is a fast same-day-to-quarterly signal — two different lenses on a counter-cyclical relationship, neither of which dethrones the published configuration."
- **key_message:** "Linear correlation peaks at **L=5-6** (counter-cyclical), diverging from the published same-day lead — but the tournament's best Sharpe stays in the near-term region (L=3 ≤ 6), so the published winner's lead region still wins. **Charts-only; no re-run.**"

#### LEAD_TOURNAMENT_BLOCK ("Lead Tournament")  **[FINAL]**

- **method_theory:** "We re-ran the full tournament across L=0..12 (monthly grid, daily signal shifted by L×21 trading days per ECON-LL1). The chart plots best OOS Sharpe per lead over the full combo cloud, with SPY buy-and-hold (1.13 over this OOS) dashed."
- **question:** "Does a longer lead beat the published same-day (L=0) winner — or is the near-term region still where the edge lives?"
- **how_to_read:** "Bars: max OOS Sharpe per lead. Strip: all valid combos at that lead. Tall-thin = single combo; flat-wide = robust regime."
- **chart_name:** `lead_sharpe_distribution`
- **chart_caption:** "Best OOS Sharpe per lead. The grid maximum is **L=3 (1.869)** — a tall spike from `vix_ratio_pctrank_252d` / Tp10_hi / P2 — with secondary peaks at L=6 (1.649) and L=5 (1.483). The published L=0 winner (1.068) is the *lowest* peak on the whole grid. Leads beyond L=7 decay toward buy-and-hold."
- **observation:** "Reading the bars: a clear near-term ridge — L1 (1.283), L3 (1.869), L5 (1.483), L6 (1.649) — then a steady decay through L7-L12 back toward 1.0. The L=3 spike is the standout. Reading the strip: at L6 the median combo (0.93) is the highest of any lead, suggesting L5-6 is a genuine ridge, not a single lucky point; the L3 maximum is taller but its cloud is wider."
- **interpretation:** "The extended grid lifts the achievable Sharpe well above the published L=0 figure (1.07 → 1.87 at L=3), but the gate keys on **where** the best lead sits: **L\*=3 ∈ {0..6}**, so the published winner's lead *region* still wins and no full re-run is required. This is the honest, economically sensible result — VIX term-structure stress predicts equities over the next one-to-six months, with the risk-adjusted sweet spot around a quarter (L=3) and a robust ridge at L=5-6. The published same-day winner is conservative within that region. **Charts-only.**"
- **key_message:** "Best Sharpe across L=0..12 is **L=3 (1.87)**, with a robust L=5-6 ridge — all inside the published lead's near-term region (L\* ≤ 6). The published winner is not dethroned; **charts-only, no re-run.**"

---

### A.3 indpro_xlp — INDPRO → XLP (Consumer Staples)  **[RE-RUN — NUMBERS PENDING RE-RUN]**

#### CORRELATION_LEAD_VIEW_BLOCK ("Lead Analysis")

- **method_theory:** "The Correlation block fixes signal lag at zero and varies the forward horizon. The monthly-strategy question is a *lead* question: how stale may the INDPRO signal get before trading XLP? For each transform we compute Pearson r between the signal lagged L=0..12 months and XLP's 1-month forward return. Note XLP is the defensive consumer-staples sector, so the expected sign is counter-cyclical — strong IP should *hurt* staples relative to growth."
- **question:** "How many months should we lag the INDPRO signal to time XLP — and does the published L=3 lead match the data?"
- **how_to_read:** "Rows are INDPRO transforms; columns are signal lead in months. Forward horizon fixed at 1 month against `xlp_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
- **chart_name:** `correlations_lead_view`
- **chart_caption:** "Pearson r between INDPRO signal lagged L months and XLP 1-month forward return. The standout transform is `indpro_accel`, which carries the two largest cells in the grid: a significant **negative** at L3 (−0.164**) and a significant **positive** at L8 (+0.149**). `indpro_mom` also peaks significantly at **L8 (+0.139*)**. The published lead L3 *is* significant — but with the counter-cyclical (negative) sign on acceleration."
- **observation:** "Reading directly: `indpro_accel` is the informative row. At **L3** its r is −0.164** — strong IP acceleration three months ago precedes XLP weakness (the counter-cyclical channel: factories humming → investors rotate out of defensives). But the same transform flips to +0.149** at **L8**, and `indpro_mom` reaches +0.139* at L8. So the data carries *two* significant leads with *opposite* signs: a counter-cyclical L3 and a pro-cyclical L8."
- **interpretation:** "The correlation view partially agrees with the published **L=3** lead (it is a real, significant counter-cyclical cell on acceleration) — but it is not the *only* significant lead, and the tournament (next block) finds its best risk-adjusted lead further out at **L=8**. Because L\*=8 ∈ {7..12}, the gate fires: a better winner exists past the coarse grid the original run used, so **this pair is being re-run**. The honest read: the published L=3 captures the counter-cyclical acceleration effect, but the extended sweep surfaces a stronger L=8 configuration the original missed."
- **key_message:** "The data supports the published L=3 counter-cyclical lead on acceleration (−0.164**) — but a second significant lead exists at L=8 (+0.139*/+0.149**), and the tournament's best Sharpe lands there. **This pair is being re-run** to adopt the L=8 winner."

#### LEAD_TOURNAMENT_BLOCK ("Lead Tournament")  **[NUMBERS PENDING RE-RUN]**

- **method_theory:** "We re-ran the full (signal × threshold × strategy × lookback) tournament across L=0..12. The chart plots best OOS Sharpe per lead over the combo cloud, with XLP buy-and-hold dashed."
- **question:** "Does a lead beyond the published L=3 produce a better risk-adjusted winner?"
- **how_to_read:** "Bars: max OOS Sharpe per lead. Strip: all valid combos. Tall-thin = single combo; flat-wide = robust regime."
- **chart_name:** `lead_sharpe_distribution`
- **chart_caption:** "Best OOS Sharpe per lead. The grid maximum is **L=8 (1.423, `indpro_accel` / Tp10_hi / P2)**, beating the published L=3 (1.048). A second cluster sits at L=5 (1.260), L=6 (1.302) and L=11 (1.236). L=0-2 and L=9, L=12 sit below 1.0."
- **observation:** "Reading the bars: L=8 is the clear single peak (1.423), with a supporting mid-grid cluster at L5-6 (1.26-1.30). The published L=3 (1.048) is modest — beaten by L4 (1.136), L5, L6, L8, L10 and L11. Reading the strip: medians are low across the board (0.54-0.61), so XLP is a hard target — the L=8 peak is a genuine standout above a noisy cloud rather than one lift among many."
- **interpretation:** "The extended grid found a better winner the published report missed: **L=8 at Sharpe 1.423** versus the published L=3 at 1.048 — and L=8 agrees with the L=8 *positive* correlation cell on the same `indpro_accel` transform. With L\*=8 ∈ {7..12}, the gate fires and **this pair is being re-run**. **[NUMBERS PENDING RE-RUN]** — final winner Sharpe / signal / threshold / strategy / max DD to be reconciled from the re-run's `winner_summary.json`."
- **key_message:** "The full grid moves the best lead from the published **3** to **8** (Sharpe 1.05 → 1.42), and L=8 agrees with the lead-correlation diagnostic. **This pair is being re-run** to adopt the L=8 configuration."

---

### A.4 hy_ig_spy — HY-IG credit spread → SPY  **[CHARTS-ONLY — FINAL]**

#### CORRELATION_LEAD_VIEW_BLOCK ("Lead Analysis")

- **method_theory:** "The Correlation block fixes signal lag at zero and varies the forward horizon. The monthly-strategy *lead* question (daily signal resampled to a monthly L=0..12 grid per ECON-LL1): how stale may the credit-spread signal get before trading SPY? For each transform we compute Pearson r between the signal lagged L months and SPY's 1-month forward return. The expected sign is counter-cyclical — wider HY-IG spreads precede equity weakness."
- **question:** "How many months should we lag the credit-spread signal — and does the published same-day (L=0) lead match the data?"
- **how_to_read:** "Rows are HY-IG spread transforms; columns are signal lead in months. Forward horizon fixed at 1 month. Stars: `*` p<0.05, `**` p<0.01."
- **chart_name:** `correlations_lead_view`
- **chart_caption:** "Pearson r between HY-IG spread signal lagged L months and SPY 1-month forward return. The strongest cells are short-lead and counter-cyclical: `hy_ig_mom_21d` at **L2 (−0.222**)**, `hy_ig_mom_63d` at **L1 (−0.160**)** and L0 (−0.117*), `hy_ig_roc_21d` at L2 (−0.126*). The HMM stress probability peaks at L6 (−0.137*). The published L=0 lead is significant on `hy_ig_mom_63d` (−0.117*)."
- **observation:** "Reading directly: the predictive content is concentrated at **very short leads (L1-2)** with the correct counter-cyclical negative sign — a momentum/RoC spike (recent spread widening) one-to-two months ago precedes lower forward SPY returns. `hy_ig_mom_21d` at L2 (−0.222**) is the single strongest cell in the grid. Longer leads (L7-12) are mostly noise."
- **interpretation:** "The lead-correlation view broadly agrees with the published **L=0** lead — the signal is genuinely fast. The strongest *linear* cell sits one-to-two months out (L1-2), a mild divergence from exactly-zero, but the tournament (next block) confirms the near-term region wins: best Sharpe at **L=1**. Because L\*=1 ∈ {0..6}, no re-run is required. Honest read: credit spreads are a short-horizon early-warning signal; the published same-day winner sits at the fast end of a one-to-two-month predictive window — close enough that the published lead region holds. **Charts-only.**"
- **key_message:** "Linear predictability is short-lead and counter-cyclical, peaking at **L=1-2** (strongest cell `hy_ig_mom_21d` L2, −0.222**) — essentially agreeing with the published same-day lead. The tournament's best Sharpe at L=1 stays in-region. **Charts-only, no re-run.**"

#### LEAD_TOURNAMENT_BLOCK ("Lead Tournament")  **[FINAL]**

- **method_theory:** "We re-ran the full tournament across L=0..12 (daily signal resampled to the monthly grid). The chart plots best OOS Sharpe per lead over the combo cloud, with SPY buy-and-hold dashed."
- **question:** "Does any lead beat the published same-day (L=0) winner — or is the fast near-term region still the edge?"
- **how_to_read:** "Bars: max OOS Sharpe per lead. Strip: all valid combos. Tall-thin = single combo; flat-wide = robust regime."
- **chart_name:** `lead_sharpe_distribution`
- **chart_caption:** "Best OOS Sharpe per lead. The maximum is **L=1 (1.439, `hy_ig_roc_21d` / Tp10_hi / P2)**, fractionally above the published L=0 (1.420). The two are effectively tied at the top; L=11 (1.362) and L=9 (1.304) form a weaker far cluster. Every lead clears buy-and-hold comfortably (most combos sit 0.7-0.9 median)."
- **observation:** "Reading the bars: L=0 (1.420) and L=1 (1.439) are a near-tie at the peak, with a gentle decay through the mid-grid and a small far-out bump at L=11. The published L=0 is essentially the winner — it is beaten only by L=1, and only by 0.019 Sharpe. Reading the strip: clouds are tight and uniformly high (medians 0.69-0.78), indicating credit spreads are a broadly robust signal across leads, not a single lucky grid point."
- **interpretation:** "The extended grid confirms rather than overturns the published result: the best lead is **L=1 (1.439)**, a hair above the published **L=0 (1.420)** — both in the {0..6} region, so the gate does **not** fire and no re-run is required. The 0.019 Sharpe gap between L0 and L1 is well inside noise; the published same-day winner is sound. Honest read: this is the cleanest of the eight pairs — the published lead was already at (or one month from) the optimum. **Charts-only.**"
- **key_message:** "Best Sharpe across L=0..12 is **L=1 (1.44)**, statistically tied with the published **L=0 (1.42)** — the published winner's lead region wins handily. **Charts-only, no re-run.**"

---

### A.5 umcsent_xlv — UMich Consumer Sentiment → XLV (Health Care)  **[RE-RUN — NUMBERS PENDING RE-RUN]**

#### CORRELATION_LEAD_VIEW_BLOCK ("Lead Analysis")

- **method_theory:** "The Correlation block fixes signal lag at zero and varies the forward horizon. The monthly-strategy *lead* question: how stale may the consumer-sentiment signal get before trading XLV? For each transform we compute Pearson r between the signal lagged L=0..12 months and XLV's 1-month forward return."
- **question:** "How many months should we lag the UMCSENT signal to time XLV — and does the published L=6 lead match the data?"
- **how_to_read:** "Rows are UMCSENT transforms; columns are signal lead in months. Forward horizon fixed at 1 month against `xlv_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
- **chart_name:** `correlations_lead_view`
- **chart_caption:** "Pearson r between UMCSENT signal lagged L months and XLV 1-month forward return. The strongest cells cluster at **L4-5**: `umcsent_dev_ma` at L5 (+0.137*), `umcsent_mom` at L5 (+0.133*), `umcsent_direction` at L5 (+0.132*), `umcsent_zscore` at L4 (+0.097). A second significant cell for `umcsent_direction` appears at L10 (+0.113*). The published L=6 column is uniformly weak (|r| ≤ 0.07)."
- **observation:** "Reading directly: predictive content is positive (pro-cyclical — rising sentiment precedes stronger XLV) and concentrates at **L=4-5**, where three transforms reach significance simultaneously. At **L6** — the published lead — every transform is weak: `umcsent_mom` +0.023, `umcsent_direction` −0.015, `umcsent_dev_ma` +0.013. There is no L6 correlation peak."
- **interpretation:** "The lead-correlation view **diverges** from the published **L=6** lead: the cleanest linear signal sits at **L=4-5**, and the published lead's column is among the weakest. The tournament (next block) pushes the best risk-adjusted lead even further out, to **L=11**. As with indpro_spy, the correlation and tournament diagnostics disagree on the exact lead but **agree the published L=6 is not the natural choice**. With L\*=11 ∈ {7..12}, the gate fires and **this pair is being re-run**."
- **key_message:** "The lead-correlation view diverges from the published 6-month lead: predictability is strongest (pro-cyclical) at **L=4-5**, and L=6 carries no peak. The tournament's best lead is L=11. **This pair is being re-run.**"

#### LEAD_TOURNAMENT_BLOCK ("Lead Tournament")  **[NUMBERS PENDING RE-RUN]**

- **method_theory:** "We re-ran the full tournament across L=0..12. The chart plots best OOS Sharpe per lead over the combo cloud, with XLV buy-and-hold dashed. Note the valid-combo count per lead is modest (74-85), so far-out peaks deserve extra scrutiny."
- **question:** "Does a lead beyond the published L=6 produce a better risk-adjusted winner?"
- **how_to_read:** "Bars: max OOS Sharpe per lead. Strip: all valid combos. Tall-thin = single combo; flat-wide = robust regime."
- **chart_name:** `lead_sharpe_distribution`
- **chart_caption:** "Best OOS Sharpe per lead. The maximum is **L=11 (1.188, `umcsent_zscore` / Tp10_lo / P1)**, beating the published L=6 (1.107). A near-tie cluster sits at L=7 (1.176) and L=8 (1.149). Short leads L0-L4 sit at or below 1.0; L=4 (0.786) and L=12 (0.961) are the weakest."
- **observation:** "Reading the bars: a rising staircase from L0 (0.96) to a plateau at **L7-11 (1.15-1.19)**, then a drop at L12. The published L=6 (1.107) sits just below this plateau — beaten by L7, L8 and L11. The peaks are close together (1.107 to 1.188 across L6-L11), so this is more a broad far-lead ridge than a single dominant spike. Reading the strip: medians are modest (0.55-0.65) and combo counts are low — the noisiest of the four re-run pairs."
- **interpretation:** "The extended grid found a better winner the published report missed: **L=11 at Sharpe 1.188** versus the published L=6 at 1.107. With L\*=11 ∈ {7..12} the gate fires and **this pair is being re-run**. Honest caveat to carry into the re-run: the L6-L11 Sharpes are tightly bunched (a ~0.08 spread) and combo counts are low, so the L=11 'win' is narrow — the re-run should treat the far-lead region as a ridge and apply the ECON-T3 tie-break carefully. **[NUMBERS PENDING RE-RUN.]**"
- **key_message:** "The full grid moves the best lead from the published **6** to **11** (Sharpe 1.11 → 1.19), within a bunched L7-L11 ridge. **This pair is being re-run** — the narrow margin and low combo counts are flagged for the re-run's tie-break."

---

### A.6 gold_copper_xli — Gold/Copper ratio → XLI (Industrials)  **[RE-RUN — NUMBERS PENDING RE-RUN]**

#### CORRELATION_LEAD_VIEW_BLOCK ("Lead Analysis")

- **method_theory:** "The Correlation block fixes signal lag at zero and varies the forward horizon. The monthly-strategy *lead* question (daily ratio resampled to a monthly L=0..12 grid per ECON-LL1): how stale may the gold/copper signal get before trading XLI? For each transform we compute Pearson r between the signal lagged L months and XLI's 1-month forward return. Gold/copper is a risk-appetite proxy — a rising ratio (fear-metal over industrial-metal) is counter-cyclical for industrials."
- **question:** "How many months should we lag the gold/copper signal to time XLI — and does the published same-day (L=0) lead match the data?"
- **how_to_read:** "Rows are gold/copper transforms; columns are signal lead in months. Forward horizon fixed at 1 month against `xli_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
- **chart_name:** `correlations_lead_view`
- **chart_caption:** "Pearson r between gold/copper signal lagged L months and XLI 1-month forward return. The significant cells are **short-lead and counter-cyclical**: `gold_copper_roc_63d` at **L0 (−0.162**)** and L1 (−0.126*), `gold_copper_mom_63d` at L0 (−0.155**), `gold_copper_roc_21d` at L0 (−0.127*) and L1/L12. The level/z-score transforms turn weakly *positive* around L5 (`gold_copper_pctrank_504d` +0.107, `zscore_126d` +0.106) but none reach significance."
- **observation:** "Reading directly: the momentum/RoC transforms carry significant **negative** cells at **L0-L1** — a recent rise in the gold/copper ratio precedes XLI weakness, the expected counter-cyclical sign. The smoothed level transforms hint at a weak positive ridge around L5 but stay below significance. So the *significant* linear content is contemporaneous-to-one-month, agreeing with the published L=0 lead."
- **interpretation:** "Here the lead-correlation view **agrees** with the published **L=0** lead — the only significant cells are at L0-L1 with the correct counter-cyclical sign. The divergence is on the *tournament* side: when swept across L=0..12, the best OOS Sharpe migrates to **L=10** (next block). So the correlation says 'fast signal, L=0 is right' while the tournament says 'a far-lead configuration scores higher' — a genuine analysis tension. Because the tournament's L\*=10 ∈ {7..12}, the gate fires on the Sharpe criterion and **this pair is being re-run**, even though the correlation diagnostic endorsed the published lead."
- **key_message:** "The lead-correlation view **agrees** with the published L=0 lead (significant counter-cyclical cells at L0-L1). But the tournament's best Sharpe sits far out at L=10 — so on the gate's Sharpe criterion **this pair is being re-run**, despite the correlation endorsing L=0. State the tension honestly."

#### LEAD_TOURNAMENT_BLOCK ("Lead Tournament")  **[NUMBERS PENDING RE-RUN]**

- **method_theory:** "We re-ran the full tournament across L=0..12 (daily ratio resampled to the monthly grid). The chart plots best OOS Sharpe per lead over the combo cloud, with XLI buy-and-hold dashed."
- **question:** "Does a lead beyond the published same-day (L=0) produce a better risk-adjusted winner?"
- **how_to_read:** "Bars: max OOS Sharpe per lead. Strip: all valid combos. Tall-thin = single combo; flat-wide = robust regime."
- **chart_name:** `lead_sharpe_distribution`
- **chart_caption:** "Best OOS Sharpe per lead. The maximum is **L=10 (1.370, `gold_copper_pctrank_504d` / Tfix07_hi / P1)**, beating the published L=0 (1.016). A second peak sits at **L=5 (1.315)**. L=1 (1.195), L=11 (1.125) and L=6 (1.117) form a supporting cluster; L=3 (0.883) and L=7 (0.937) are the weakest."
- **observation:** "Reading the bars: two distinct peaks — **L=5 (1.315)** and **L=10 (1.370)** — separated by a mid-grid dip (L7-L9 around 0.94-0.99). The published L=0 (1.016) is near the bottom of the grid, beaten by most leads. The L=10 peak comes from a `pctrank_504d` percentile signal, a different transform from the published momentum winner. Reading the strip: the L=10 cloud is comparatively wide at the top (p75 = 1.005), suggesting the far-lead peak has some support rather than being one isolated combo."
- **interpretation:** "The extended grid found a better winner the published report missed: **L=10 at Sharpe 1.370** versus the published L=0 at 1.016. With L\*=10 ∈ {7..12} the gate fires and **this pair is being re-run**. Honest tension to carry forward: the *correlation* diagnostic favoured L=0 (the published lead) while the *tournament* favours L=10 — the L=10 edge rides a smoothed percentile transform, not the fast momentum signal the correlations lit up. The re-run should reconcile which signal the adopted L=10 winner uses. **[NUMBERS PENDING RE-RUN.]**"
- **key_message:** "The full grid moves the best lead from the published **0** to **10** (Sharpe 1.02 → 1.37), with a secondary L=5 peak — though the correlation diagnostic still favours L=0. **This pair is being re-run** to adopt the L=10 configuration, with the signal-vs-lead tension flagged."

---

### A.7 busloans_spy — C&I Loans → SPY  **[CHARTS-ONLY — FINAL; lagging-pair, reverse-only causality]**

> **Lagging-pair note (RES-20 variant, busloans_spy precedent):** the econometric verdict for this pair is **reverse-only causality** — the stock market leads loan books, not the other way round. A genuine "lead" claim is therefore structurally constrained: any apparent predictive lead is descriptive of a *lagging* series, not a forecast. The blocks below state this honestly; the strategy is a drawdown-avoidance overlay riding a late-cycle regularity, not an early-warning signal.

#### CORRELATION_LEAD_VIEW_BLOCK ("Lead Analysis")

- **method_theory:** "The Correlation block fixes signal lag at zero and varies the forward horizon. The monthly-strategy *lead* question: how stale may the loan-growth signal get before trading SPY? For each transform we compute Pearson r between the signal lagged L=0..12 months and SPY's 1-month forward return. Read this in light of the pair's reverse-only causality verdict — loans lag the market, so any 'lead' here is a property of a lagging indicator, not a forecasting signal."
- **question:** "If we trade against next month's SPY return, how many months should we lag the loan-growth signal — and does the published L=6 lead reflect any real predictive content, given loans are a lagging series?"
- **how_to_read:** "Rows are C&I loan-growth transforms; columns are signal lead in months. Forward horizon fixed at 1 month against `spy_fwd_1m`. Stars: `*` p<0.05, `**` p<0.01."
- **chart_name:** `correlations_lead_view`
- **chart_caption:** "Pearson r between loan-growth signal lagged L months and SPY 1-month forward return. The grid is almost entirely insignificant — consistent with a lagging series. The single significant cell is `busloans_accel_pct` at **L5 (−0.135**)**; every other transform stays within |r| < 0.08 at every lead. The published L=6 column is uniformly near-zero."
- **observation:** "Reading directly: this is the weakest lead-correlation grid of the eight pairs — exactly what reverse-only causality predicts. Only one cell clears significance (`busloans_accel_pct` at L5, −0.135**), and it is isolated. At the published **L6**, all transforms are essentially zero (`busloans_pct_mom` +0.039, `busloans_6m_pct` +0.032, `busloans_zscore_60m` +0.011). There is no meaningful linear lead."
- **interpretation:** "The lead-correlation view confirms the pair's character: loan growth carries **almost no linear predictive content** for forward SPY at any lead — as expected for a Conference Board *lagging*-index component. The published L=6 lead is not endorsed by correlation (nor is any other lead), but this is not a divergence that triggers a re-run: the tournament (next block) finds its best Sharpe at **L=5**, inside the published lead's region (L\* ≤ 6). The honest read is that the strategy does not ride a predictive correlation — it rides a *descriptive* regime regularity (weak loan growth marks late-stage, post-stress states). **Charts-only.**"
- **key_message:** "The lead-correlation grid is near-empty (one significant cell, `busloans_accel_pct` L5 −0.135**) — exactly as a lagging series should be. No real predictive lead exists; the strategy is descriptive, not predictive. Tournament best lead (L=5) stays in-region. **Charts-only, no re-run.**"

#### LEAD_TOURNAMENT_BLOCK ("Lead Tournament")  **[FINAL]**

- **method_theory:** "We re-ran the full tournament across L=0..12. The chart plots best OOS Sharpe per lead over the combo cloud, with SPY buy-and-hold (0.89) dashed. For a lagging series, a high tournament Sharpe reflects regime-conditional drawdown avoidance, not predictive lead — read the bars with that caveat."
- **question:** "Does any lead beat the published L=6 winner — and is the edge a predictive lead or a regime artefact?"
- **how_to_read:** "Bars: max OOS Sharpe per lead. Strip: all valid combos. Tall-thin = single combo; flat-wide = robust regime."
- **chart_name:** `lead_sharpe_distribution`
- **chart_caption:** "Best OOS Sharpe per lead. The maximum is **L=5 (1.500, `busloans_pct_mom` / Trp25_lo / P1)** — the published winner — with **L=4 close behind (1.424)**. A secondary far cluster sits at L=9 (1.319) and L=11 (1.271). The published L=6 (1.125) is, notably, *not* the grid peak; the L=5 winner edges it. All leads clear buy-and-hold (0.89)."
- **observation:** "Reading the bars: the peak is **L=5 (1.500)**, flanked by a strong L=4 (1.424); the published L=6 (1.125) sits a step below its own near-neighbours. A second, lower cluster appears far out at L9-L11. The L=5 spike is tall but its neighbour L=4 is close, so the near-term region is a small ridge rather than a single isolated point. Reading the strip: medians are high and rise with lead (0.64 at L0 → 0.74 at L10), but for a lagging series this reflects the broad availability of defensive (mostly-cash) combos, not predictive content."
- **interpretation:** "The extended grid's best Sharpe is **L=5 (1.500)**, inside the published lead region (L\* ≤ 6), so the gate does **not** fire — **charts-only**. A subtlety worth stating: the published configuration sits at L=6 (1.125) while the grid peak is one month shorter at L=5; both are in-region, so no re-run, but the chart honestly shows the near-term ridge centred at L4-L5 rather than exactly at the published L6. Crucially, this Sharpe is a **drawdown-avoidance artefact of a lagging series** — the strategy sits in cash ~75% of the time and fails the bootstrap significance test (p=0.066, per `winner_summary.json`). The high Sharpe is real but it is not evidence of a predictive lead. **Charts-only.**"
- **key_message:** "Best Sharpe across L=0..12 is **L=5 (1.50)**, with L=4 close behind — inside the published lead region, so **charts-only, no re-run**. The edge is regime-conditional drawdown avoidance on a lagging series (75% cash, bootstrap p=0.066), not a predictive lead."

---

## B. Cross-Period prose relocation spec (DPS-CPX1)

**Background.** The 2026-06-10 relocation (`fix260610_xpair_general`) moved the five Cross-Period Consistency charts (`subperiod_sharpe`, `rolling_correlation`, `structural_break`, `rolling_sharpe_cp`, `rolling_granger`) off the Evidence page and into `render_strategy_page()`'s **Confidence tab** (`app/components/page_templates.py::_render_cross_period_consistency`, lines ~990-1054). Any narrative that *described those charts* and stayed behind on the Evidence page is now orphaned — it points at charts the reader can no longer see on that page.

**Finding (whole-fleet scan).** Of the 8 non-frozen pairs, **only `permit_spy` (the reference pair) carries orphan Cross-Period narrative.** It sits in `EVIDENCE_METHOD_BLOCKS["transition"]` (lines 547-581 of `app/pair_configs/permit_spy_config.py`) — the "**Honest read on the cross-period charts above**" block (sub-period Sharpe, rolling 24M correlation, rolling Granger F, rolling 24M Sharpe, structural break) plus the "**Putting it together**" coda. The phrase "the cross-period charts **above**" is the smoking gun: there are no cross-period charts above it anymore.

The other **7 pairs are already CP-clean** on the Evidence page:
- `indpro_spy`, `vix_vix3m_spy`, `indpro_xlp`, `hy_ig_spy`, `umcsent_xlv`, `gold_copper_xli` — each has a short, single-paragraph Evidence→Strategy `transition` bridge with **no** cross-period chart description. Verified by grep (no "cross-period charts above", "Putting it together", or rolling-window enumerations in any Evidence-page field).
- `busloans_spy` — built fresh on 2026-06-12, **after** the relocation, so it never accumulated orphan prose. Its only CP-adjacent Evidence text is a per-method `deep_dive_content` inside `REGIME_BLOCK` (line ~571) that references rolling-correlation sign-instability as a *fragility flag carried to the Strategy page* — this is correct cross-referencing, not an orphan chart description. Leave as-is. (The `downloads[]` CSV links to `rolling_correlation_*.csv` and `subperiod_sharpe_*.csv` are audit-trail download links, not chart narrative — also fine.)

> **Note on the renderer.** `_render_cross_period_consistency` currently emits the five charts with *generic, hardcoded* "How to read it" captions and **no per-pair narrative slot**. To land the moved permit_spy prose where the reader can see it, Ace needs a per-pair CP-narrative hook in the Confidence tab (e.g. a new optional `StrategyConfig.CROSS_PERIOD_NARRATIVE_MD` rendered immediately under the `### Cross-Period Consistency` heading, before the first chart). That wiring is Ace's call; the prose below is authored to drop into that slot. If Lead prefers not to add a slot this wave, the minimum acceptable action is to strip the orphan prose from the Evidence `transition` and replace it with the one-line bridge in B.2 — so no pair ships narrative pointing at absent charts.

### B.1 permit_spy — prose to MOVE (Evidence `transition` → Strategy Confidence-tab Cross-Period section)

Move the following (authored/lightly rewritten by Ray so it reads correctly in its new home — "charts above" → "charts on this tab", present tense, self-contained). This is the body for `StrategyConfig.CROSS_PERIOD_NARRATIVE_MD` (or equivalent), rendered under `### Cross-Period Consistency` in the Confidence tab:

> **Honest read on the cross-period charts on this tab.** The relationship between Building Permits and SPY is real and pro-cyclical, but it is not steady across history:
>
> - **Sub-period Sharpe.** The strategy is *negative* in three of the four labelled crisis sub-periods (Dot-Com −0.38, GFC −0.36, China/EM −1.20) and roughly flat through COVID (−0.07). The full-OOS bar (+1.41) carries the headline; the crisis bars do not.
> - **Rolling 24-month correlation.** The line ranges from about −0.36 to +0.42 with a mean near zero. Only ~54% of 24-month windows are positive. The relationship is regime-dependent, not stationary.
> - **Rolling Granger F.** Average F is 3.16 — just below the 3.84 critical value at 5% — and the rolling p-value averages 0.20. Granger-causality is *not* persistently significant across windows; it appears in pockets.
> - **Rolling 24-month Sharpe.** Range −2.0 to +2.0, mean ~0.0. The strategy's edge is concentrated in specific regimes, not earned evenly through time.
> - **Structural break.** The QLR-proxy p-value is 0.27 — *not* significant at the 5% level — so the relationship is treated as stationary across the sample for tournament purposes; the break-date flag is suppressed and the test annotation is marked not-significant. Recession-shaded rectangles remain for context.
>
> **Putting it together.** These cross-period diagnostics support a genuine pro-cyclical relationship between Building Permits and equity returns, with the strongest *linear* co-movement at a 12-month horizon on smoothed transforms — but they also show the edge is regime-dependent, not a stationary law. The 6-month lead and 1-month-momentum signal that won the tournament reflect out-of-sample Sharpe optimisation, not a claim that the relationship is uniform across regimes or guaranteed to persist evenly. Read the strategy's headline Sharpe with these caveats in mind.

### B.2 permit_spy — NEW one-line Evidence→Strategy `transition` (replaces the moved block)

Replace `EVIDENCE_METHOD_BLOCKS["transition"]` (lines 547-581) with a single forward-looking bridge that no longer references any chart:

> The in-sample econometric case for a pro-cyclical permits-equity relationship is established. The practical question is whether an investor can turn it into an execution-ready strategy — and how robust that edge is across regimes, which the next page's Confidence tab examines directly.

(Rationale: this matches the clean one-line `transition` pattern the other 7 pairs already use, and explicitly hands the regime/cross-period question forward to the Confidence tab where the charts now live — closing the orphan loop.)

### B.3 The other 7 pairs — relocation status

| Pair | Orphan CP prose on Evidence? | Action |
|---|---|---|
| indpro_spy | No | **Already clean** — no change |
| vix_vix3m_spy | No | **Already clean** — no change |
| indpro_xlp | No | **Already clean** — no change |
| hy_ig_spy | No | **Already clean** — no change |
| umcsent_xlv | No | **Already clean** — no change |
| gold_copper_xli | No | **Already clean** — no change |
| busloans_spy | No (fresh post-relocation build) | **Already clean** — no change |

Only **permit_spy** requires the B.1 + B.2 relocation.

---

## Handoff notes

- **RES-NR1 instrument check:** target symbols confirmed against `results/{pair}/interpretation_metadata.json.target_symbol` where populated (indpro_spy=SPY, vix_vix3m_spy=SPY, hy_ig_spy=SPY, gold_copper_xli=XLI); indpro_xlp/umcsent_xlv/busloans_spy had null `target_symbol` in metadata at authoring time — targets sourced from the pair-id convention and existing config page titles (XLP, XLV, SPY respectively) and flagged to Lead/Dana as a metadata-completeness gap (A2A item below). All instrument names in the prose above match the pair's actual target.
- **Prose-vs-data:** every numeric value and every "wins / diverges / agrees / in-region" categorical claim re-read from the 2026-06-13 lead CSVs and the gate table at authoring time.
- This doc is the per-pair section inventory for Ace: A.1-A.7 = lead blocks (port into `EVIDENCE_METHOD_BLOCKS.level1`); B.1-B.2 = permit_spy CP relocation (port into StrategyConfig Confidence-tab narrative + rewrite Evidence transition).
