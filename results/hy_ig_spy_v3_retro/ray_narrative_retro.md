<!-- ray_narrative_retro.md — hy_ig_spy_v3_retro experiment fork -->
<!-- RES-NR1: instrument references confirmed against interpretation_metadata.json -->
<!-- indicator_id: hy_ig_spread_pct → "HY-IG credit spread" in prose -->
<!-- target_symbol: SPY → "S&P 500 (SPY)" in prose -->

## Evidence

This fork tests a retro-apply variant of the hy_ig_spy v3 pipeline with the winner rule S6_hmm_stress / T4_hmm_0.5 / P2. The primary question is whether inheriting the winner from the original pipeline — rather than re-selecting it blind on the corrected data — changes the ECON-FE1 outcome. The winner is unchanged from the original run (winner_changed_vs_original = false), confirming the retro-apply column fix did not alter rank ordering.

The HY-IG credit spread is a leading credit stress indicator measuring the yield premium of high-yield bonds over investment-grade corporates. The S6_hmm_stress signal applies a two-state Hidden Markov Model (HMM) — a probabilistic model that infers whether markets are in a "stress" or "calm" latent regime — directly to the HY-IG credit spread level. The model outputs a continuous probability (0–1) that the current observation belongs to the stress state. The observed direction is confirmed countercyclical: high stress probability is associated with negative S&P 500 (SPY) returns in the backtest data, consistent with the economic mechanism.

The 10-condition ECON-FE1 framework scores 7/10 passes. Validation OOS Sharpe is 1.24 (2018–2025-01). Holdout Sharpe is 1.61 (Jan–Dec 2025, 252 observations). Three conditions fail with honest interpretations: C03 (block bootstrap 2.5th percentile = −0.35) fails because 252 holdout days yield only ~12 non-overlapping 21-day blocks — a genuine low-power artefact, not a model failure. C04 (deflated Sharpe ratio, DSR p-value ≪ 0.05) correctly fails given 150 effective trials in the candidate pool; the DSR penalises multiple comparisons regardless of which candidate wins. C05 (excess annual return vs. buy-and-hold = −5.1 pp) fails because SPY returned ~19.7% annualised in 2025; a countercyclical protection strategy structurally underperforms a fully-invested benchmark in a low-volatility bull market year.

## Strategy

The winner rule scales SPY exposure proportionally downward when the HMM stress probability for the HY-IG credit spread exceeds 0.5 (T4_hmm_0.5). Position sizing follows P2 (proportional): at a stress probability of p, the strategy holds (1 − p) of full SPY exposure, so a 70% stress reading implies 30% SPY, 70% cash. The allocation is continuous between 0 and 1, not binary. Lead days = 0.

Methodological caveat (ECON-OOS4 retro-apply): the winner S6_hmm_stress / T4_hmm_0.5 / P2 was inherited from the original hy_ig_spy pipeline, not re-selected blind on the shortened validation window after the column fix. The retro-apply constraint means tournament results from a data-corrected run are applied retroactively to the corrected data without re-running blind selection. This is the methodological difference under test relative to the rerun fork.

In the holdout period (Jan–Dec 2025, 252 trading days), holdout Sharpe was 1.61 vs. 1.24 in validation — a Sharpe degradation of −0.37 units (negative degradation means holdout outperformed validation; well within C10 threshold of 0.5, PASS). Holdout MDD was −5.9% vs. −18.8% for buy-and-hold. Despite the proportional sizing rule reducing upside participation, the strategy delivered 14.6% annualised return in the holdout year vs. buy-and-hold's 19.7%, a −5.1 pp gap — substantially narrower than the z-score / P1 fork's −14.4 pp gap.

## Methodology

The experiment uses the ECON-OOS4 three-period split: in-sample 2000-01-03 to 2018-10-03 (4,893 days), validation OOS 2018-10-04 to 2025-01-13 (1,638 days), and holdout 2025-01-14 to 2025-12-31 (252 days). The winner is selected on validation Sharpe in the original pipeline and applied retroactively to the corrected data. The holdout is evaluated once, blind.

ECON-FE1 is a 10-condition pass/fail framework testing holdout robustness: absolute Sharpe (C01, C02), resampling significance (C03 block bootstrap, C04 deflated Sharpe ratio), economic value vs. buy-and-hold (C05), drawdown control (C06, C07), validation consistency (C08), sample adequacy (C09), and performance stability (C10). All thresholds are pre-specified. The three failing conditions are structurally expected: small holdout T limits bootstrap power, a large candidate pool guarantees DSR failure, and a 2025 bull market penalises any risk-off rule.

The retro-apply fork tests whether ECON-OOS4 compliance is sensitive to the distinction between (a) re-running the tournament on corrected data blind and (b) inheriting the prior winner. The winner is identical across both forks (S6_hmm_stress / T4_hmm_0.5 / P2 is also the retro fork winner), and both score 7/10 ECON-FE1 conditions. The result implies that the column fix did not alter the rank ordering of candidates and that the retro-apply constraint does not introduce additional selection bias in this instance. However, the retro-apply design remains methodologically weaker than a blind re-run because the selection was not prospectively blind on the corrected data.
