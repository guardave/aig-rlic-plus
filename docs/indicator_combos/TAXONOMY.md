# Taxonomy of indicator combinations (組合拳)

Phase 1 drafting document, branch `research261017_indicator_combos`, 2026-10-17. Author: Research Ray.
No backtests were run. The correlations quoted come from the descriptive panel in
`data/effective_dimensionality.json` (script `scripts/pit_panel_inspect.py`).

## Executive summary

- A combination is defined by three things: **which indicators** go in, **which role** each plays, and **the operator**
  that joins them. Most of the risk of overfitting sits in the role and operator choices. Picking the indicators is
  only part of it.
- Six roles cover every combination we expect to test: **confirmation (AND / k-of-n)**, **filter or regime
  conditioning**, **composite (z-average or factor)**, **sequencing (lead-lag chain)**, **divergence**, and
  **direction-vs-sizing split**. A seventh role, **diffusion (breadth)**, is a composite counted as a vote, and we
  list it separately because it reads differently in use.
- Each role has a natural use case, a natural metric and a typical failure mode. These are tabulated below, and
  the question bank (`QUESTION_BANK.md`) uses the same role codes (R1–R7).
- Role codes do not depend on the indicator. Each one costs a known number of extra free parameters
  ("degrees of freedom", DoF). `COMBINATORICS.md` uses those DoF to size the search space.
- Every operator has to respect point-in-time timing. A combination is only as timely as its **slowest** member
  at each rebalance date, unless the operator is designed to work with stale inputs (the "as-of" rule, § 3).

## 1. Building blocks

| Term | Meaning in this project |
|------|-------------------------|
| Indicator | One published series (e.g. `PERMIT`, `ISM_MFG`, HY OAS). 29 are in the descriptive panel, and 26 distinct underlying series feed the 35 live single-indicator pairs. |
| Transform | The derived reading used as a signal: level, m/m, 3m/6m change, YoY, YoY acceleration, z-score over 60m/126d/252d, deviation from trend, contraction flag. The fleet uses about 8–15 per series. |
| Single rule | (transform, threshold, direction, lead, position rule P1/P2/P3). This is the unit the single-indicator tournaments select. 29 pairs searched about **144,000** such configurations in total (median 1,008 per pair; `results/*/winner_summary.json` `total_combos`). |
| State | The output of a single rule at a date: bull / bear (binary), or a continuous score in [−1, 1] (P2-style strength). |
| Combination | A function that maps the states (or raw readings) of k ≥ 2 indicators to one position or one classification. |

## 2. The roles

### R1 — Confirmation (AND, k-of-n vote)

- **Definition.** Act (e.g. go to cash) only when at least k of n member states agree. AND is k = n, OR is k = 1,
  majority is k = ⌈n/2⌉.
- **Economic rationale.** Each indicator has its own idiosyncratic noise (survey error, weather, strikes,
  seasonal-adjustment revisions). When two indicators with *different* measurement processes agree, the reading
  is more likely to be the common business-cycle signal. This is the logic behind the Conference Board LEI
  diffusion and the NBER's "breadth" criterion.
- **Our examples.**
  - Housing contraction (`permit_spy`, `housing_starts_spy`, `nhs_spy`) AND credit widening (`hy_ig_spy`,
    `sloos_ci_small_spy`).
  - 2-of-3 within housing (starts / permits / new home sales; pairwise Spearman 0.61–0.82, the most redundant
    block in the panel).
- **DoF added.** k (one integer) and the choice of members. If each member reuses its own frozen single-indicator
  rule, nothing else is added.
- **Failure mode.** AND trades false alarms for late signals. With slow members (cement at a 72-day median lag,
  retail inventories/sales at 45 days) the confirmation may arrive after the drawdown. Correlated members (houst +
  permit, ρ = 0.82) add little real confirmation.
- **Natural metric.** False-alarm rate, signal lag relative to the market peak, max drawdown, and time invested.

### R2 — Filter / regime conditioning

- **Definition.** Indicator A defines a regime. Indicator B's rule is applied only inside a regime, or with a
  regime-specific threshold or direction. Formally pos = f_B(x_B | s_A), where s_A ∈ {calm, stress} or {early,
  mid, late cycle}.
- **Economic rationale.** Predictive relations are state-dependent. Macro news moves equities more in recessions
  and stress episodes. Credit conditions amplify real shocks (the financial accelerator; Gilchrist & Zakrajšek
  2012). A fast market regime variable (VIX term structure, HY–IG spread) can tell a slow macro signal *when* to
  matter.
- **Our examples.**
  - ISM manufacturing 1m diff (`ism_mfg_spy`) applied only when VIX/VIX3M > 1 (backwardation) or HY–IG z > 1.
  - Yield-curve signal conditioned on the credit regime.
  - Causal HMM / Markov-switching stress probabilities (`scripts/_regime_causal.py`, IS-frozen, filtered) as the
    regime variable.
- **DoF added.** The regime definition (variable, threshold or number of states) and whether B's rule is
  re-estimated per regime. Per-regime re-estimation doubles B's DoF and halves its sample. This is the most
  overfit-prone variant.
- **Failure mode.** Regimes are rare (stress is roughly 10–20% of months), so per-regime estimates rest on a handful
  of episodes, often 3–5 recessions. Smoothed regime probabilities leak the future (project memory: 14/17 HMM/MS
  pipelines did this). Only *filtered*, IS-frozen probabilities are admissible.
- **Natural metric.** The conditional return spread (regime on vs off), max drawdown and CVaR inside stress.

### R3 — Composite (z-average, factor, diffusion score)

- **Definition.** Standardise each member reading (expanding-window z-score, sign fixed by economic prior) and
  average them, either equal-weighted, inverse-variance weighted or by the first principal component estimated in
  real time. Act on the composite with one threshold.
- **Economic rationale.** Diffusion-index forecasting (Stock & Watson 2002) shows that a few common factors
  summarise large macro panels. Forecast-combination studies find that simple equal weights are hard to beat
  (Timmermann 2006, the "forecast combination puzzle"). Rapach, Strauss & Zhou (2010) find that combining
  individually weak equity-premium predictors gives stable out-of-sample gains, where the individual predictors
  fail (Welch & Goyal 2008).
- **Our examples.**
  - Equal-weight composite of one representative per correlation cluster (§ 4 of `COMBINATORICS.md`).
  - Housing composite (houst, permit, nhs, nahb, cement).
  - Real-time PC1 of the 10 long-history ALFRED series (it explains 41% of variance on the real-time track).
- **DoF added.** Equal weight with prior signs: only the membership and one threshold. Estimated weights add
  k − 1 parameters per re-estimation. PCA adds a rotation, a sign convention and the number of factors.
- **Failure mode.** Mixing very different release lags into one number hides staleness. A composite dominated by
  one cluster just re-labels that cluster (e.g. 4 activity series + 1 credit series ≈ an activity signal).
  Expanding-window z-scores are non-stationary early in the sample.
- **Natural metric.** Gain over the best single indicator *selected in the same training fold*, and over the
  naive equal-weight composite when the weights are estimated.

### R4 — Sequencing (lead-lag chain)

- **Definition.** A then B within a window: pos changes when A fires and B confirms within w periods
  (A_t ∧ B_{t+j}, 0 < j ≤ w), or a staged exposure (reduce on A, exit on B, re-enter on C).
- **Economic rationale.** Cycles propagate in a broadly regular order:
  - credit conditions tighten, then housing and durable orders fall (Leamer 2007: "housing is the business cycle"),
  - then manufacturing activity falls, then labour market slack rises,
  - then earnings decline.
  On the way up the order roughly reverses: the curve steepens, then orders recover, then employment.
- **Our examples.**
  - SLOOS tightening or HY OAS widening → ISM manufacturing < 50 within 3–9 months.
  - Permits YoY < 0 → UNRATE 6m change > 0.2pp (a Sahm-type rise).
  - Recovery: curve steepening + new orders rising → re-enter.
- **DoF added.** The window w, the order, and the gap per link. A 3-link chain with 6 window choices per link
  already has 216 timing variants.
- **Failure mode.** The empirical order is not stable across cycles (2001 was investment-led, 2008 housing/credit,
  2020 an exogenous shock). Release lags differ: a "B confirms" event can be known only 1–2 months after its
  reference month. With fewer than about 6 completed cycles in a PIT sample, chain parameters cannot be estimated,
  only pre-registered.
- **Natural metric.** Lead time relative to the market peak / trough and to NBER dates, missed-rally cost on
  re-entry, and drawdown avoided.

### R5 — Divergence

- **Definition.** A signal is generated by *disagreement*: sign(z_A) ≠ sign(z_B) or |z_A − z_B| > c. It is used
  either as a warning (reduce risk) or as a forecast of which side converges.
- **Economic rationale.**
  - Soft data (surveys) react to news and expectations. Hard data (production, sales) record activity.
  - Market prices (credit spreads, gold/copper, SOX/SPY) discount the future.
  - Persistent divergence carries information about which side is wrong, about a turning point, or about a
    sentiment overshoot.
- **Our examples.**
  - Sentiment (UMCSENT, UMich expectations, NAHB) vs hard data (RSXFS, INDPRO).
  - Market stress (HY–IG, VIX ratio, gold/copper) vs slow macro (ISM, UNRATE).
  - SOX/SPY momentum vs ISM manufacturing for XLK vs SPY.
- **DoF added.** The divergence measure (sign or gap), the threshold c, the persistence requirement, and the
  convergence direction assumed.
- **Failure mode.** Two noisy series diverge often by chance. A divergence rule needs a null built from
  independently shifted members (N2 in the question bank). Low-correlation pairs diverge most often and carry the
  least information.
- **Natural metric.** Forward return conditional on divergence vs on agreement, and the hit rate of the
  convergence direction.

### R6 — Direction-vs-sizing split

- **Definition.** One indicator (or a composite) sets the **sign** of exposure, and another sets the **size**:
  w_t = d_t(A) · g(B_t), with g decreasing in risk (volatility, stress probability, signal strength).
- **Economic rationale.** Slow macro data have low turnover and some information about the sign of the equity
  premium over months. Fast market risk measures carry information about near-term volatility, which predicts
  risk better than returns. Volatility-managed portfolios improve risk-adjusted returns (Moreira & Muir 2017;
  contested out of sample by Cederburg et al. 2020). Splitting the two jobs lets each indicator do what it is
  good at.
- **Our examples.**
  - Sign from a curve + ISM composite, size from VIX/VIX3M or realised volatility.
  - Sign from `t10y3m_spy`, size scaled by a causal HMM P(stress).
  - Conviction sizing: size = share of agreeing indicators (a vote count; links R1/R3).
- **DoF added.** The sizing map g (linear, step, inverse volatility), a cap and floor, and a volatility window.
- **Failure mode.** Leverage and turnover creep in. A sizing rule that uses the asset's own realised volatility is
  partly a trend rule, so it must be compared against a pure volatility-target baseline as well as against buy-and-
  hold.
- **Natural metric.** CVaR (5%), max drawdown, Sharpe, turnover, and the gain over direction-only and over
  sizing-only.

### R7 — Diffusion / breadth (vote share)

- **Definition.** The share of N indicators currently in a bearish state, D_t = (1/N) Σ 1{state_i = bear}, used as
  a level ("> 60% bearish") or as a change.
- **Economic rationale.** This is the NBER-style breadth idea and the Conference Board diffusion index. It is
  robust to any single indicator's idiosyncratic failure.
- **Our examples.** The share of the 29 single-indicator winners (frozen rules) in risk-off state at each month-end.
  This is a purely descriptive tool and is cheap to build.
- **DoF added.** One threshold. The membership is fixed by the fleet.
- **Failure mode.** Breadth is dominated by the largest correlated cluster. 10 of the 35 live pairs are housing
  (new home sales ×4, starts ×2, permits ×2, NAHB, cement), so housing gets about 30% of the vote. Fix this by weighting by cluster (one vote per cluster).
- **Natural metric.** AUROC for recession months and for 12-month-ahead drawdowns > 15%.

## 3. Cross-cutting operator rules (point-in-time)

| Rule | Statement |
|------|-----------|
| As-of evaluation | At each rebalance close t, each member uses its latest reading with `available_date ≤ t` (`scripts/_pit_align.py`, `pit_shift` / `realtime_apply`). Members are never forced onto a common reference month. The composite at t mixes, for example, ISM for month m−1 (1-day lag) with new home sales for m−2 (25-day median lag). |
| Staleness flag | Record each member's age in days at t. Pre-register whether a member older than X days is dropped, carried or down-weighted. Cement (72-day median, up to 165 days since 2025-07) and retail inventories/sales (45 days) need this. |
| Common-start rule | The combination starts at the latest PIT start among its members. The coverage table (`data/coverage_and_lags.csv`) gives each start. Pre-register whether a late member enters when available (unbalanced) or the whole combination waits (balanced). |
| Frozen members | In "cheap" families each member keeps its published single-indicator rule, which is frozen. In "re-search" families member rules are re-selected inside the training fold only. The two families are never mixed in one test. |
| Real-time vs revised | ALFRED series use vintages (track b) where available. ISM, NAHB, UMich expectations, cement and EIA have no archive and are revised-only, which is disclosed per question. Revision gaps can be large: real-time vs revised correlation is 0.90 for NEWORDER YoY, 0.93 for INDPRO YoY and 0.94 for new home sales YoY (`realtime_vs_revised` in the JSON). |
| Mixed frequency | Daily market members are sampled at the rebalance close (HY/IG OAS at t−1 business day, posted next day). Quarterly members (SLOOS, card delinquency, ECI) are carried forward as-of. A daily-rebalanced combination re-evaluates monthly members only on their release dates. |

## 4. Mapping roles to use cases and metrics

| Use case | Typical roles | Primary metric | Secondary |
|----------|---------------|----------------|-----------|
| U1 Risk-off overlay (asset vs cash) | R1, R2, R3, R7 | Max drawdown, CVaR 5% (monthly) | Calmar, upside capture, time invested, Sharpe |
| U2 Allocation tilt (equity weight 0.5–1.0, or equity vs bonds/T-bills) | R3, R6 | Return per unit of tracking error vs a static weight; CVaR | Turnover, Sharpe |
| U3 Sector rotation / relative return | R2, R5, R3 | Relative return (sector − SPY, cyclical − defensive basket); IR | Sign hit rate |
| U4 Recession / regime classification | R1, R4, R7, R3 | AUROC vs NBER months; lead time; false alarms per decade | Brier score; recession-month hit rate |
| U5 Entry timing (re-entry after risk-off) | R4, R5 | Return 6/12m after the entry signal vs unconditional; missed-rally cost | Time to recovery |

## 5. Literature anchors (credibility-ranked)

- **Peer-reviewed.**
  - Estrella & Mishkin (1998): term spread for recessions.
  - Gilchrist & Zakrajšek (2012): credit spreads and the business cycle.
  - Stock & Watson (2002): diffusion indexes.
  - Timmermann (2006): forecast combinations.
  - Rapach, Strauss & Zhou (2010): combination forecasts of the equity premium.
  - Welch & Goyal (2008): out-of-sample failure of single predictors.
  - Moreira & Muir (2017): volatility-managed portfolios.
  - Harvey, Liu & Zhu (2016): multiple testing in factor research.
  - White (2000): reality check.
  - Hansen (2005): SPA test.
  - Romano & Wolf (2005): stepwise multiple testing.
  - Bailey & López de Prado (2014): deflated Sharpe ratio.
  - Bailey, Borwein, López de Prado & Zhu (2017): probability of backtest overfitting.
  - Croushore & Stark (2001): real-time data.
  - Hamilton (1989): Markov switching.
  - Chauvet & Piger (2008): real-time turning points.
  - Leamer (2007): housing and the cycle.
- **Working paper or practitioner.**
  - Novy-Marx (2015/2016), "Testing strategies based on multiple signals": combining signals that were each
    selected in-sample inflates t-statistics far beyond the single-signal case. This is directly relevant to
    building combinations from fleet winners.
  - Sahm (2019): the unemployment-rise rule.
  - Faber (2007): 10-month moving-average timing (a trend baseline).
- **Consensus.** Combining forecasts tends to help mostly by reducing variance, not by finding new signals.
  Individual macro predictors of equity returns are weak and unstable out of sample.
- **Debate.** Whether regime conditioning adds value beyond simple combination is unsettled, as is whether
  volatility management survives realistic costs.
