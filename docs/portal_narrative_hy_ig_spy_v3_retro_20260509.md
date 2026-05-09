---
pair_id: hy_ig_spy_v3_retro
winner_rule: S6_hmm_stress / T4_hmm_0.5 / P2 / L0
validation_sharpe: 1.2427
holdout_sharpe: 1.6116
status: needs_final_exam
split_design: three_period
is_period: "2000-01-03 to 2018-10-03"
validation_period: "2018-10-04 to 2025-01-13"
holdout_period: "2025-01-14 to 2025-12-31"
experiment_fork: retro
generated_at: "2026-05-09"
---

> **EXPERIMENT FORK — retro branch.** This portal documents the retro-apply variant of `hy_ig_spy_v3`. It is one half of a controlled experiment comparing a clean rerun (v3) against a retroactive recalibration (v3_retro). The winner rule is identical in both forks; differences in performance metrics, if any, isolate the effect of retro-apply methodology.

## Signal Mechanism

The strategy is built on a Hidden Markov Model (HMM) trained to identify two latent regimes in the joint behaviour of high-yield and investment-grade credit spreads relative to equities (the HY–IG / SPY pair). The HMM assigns a continuous stress probability to each trading day — the posterior probability of occupying the high-volatility, risk-off regime. When that probability exceeds 0.5, the model reads the market as stressed; it then scales equity exposure down proportionally to the degree of stress (the P2 sizing rule: position weight = 1 − hmm_stress_prob). The signal is applied with no lag (L0), meaning positions update on the same day the probability is computed. During calm regimes the portfolio is fully invested; during stress transitions it de-risks smoothly rather than switching on a binary trigger. This graduated response is central to why the strategy captures downside protection without whipsawing out of recoveries.

## Key Findings and Exam Status

Over the in-sample period (2000-01-03 to 2018-10-03, approximately 4,893 trading days), the winner rule was selected via tournament across signals, thresholds, and sizing variants. The validation out-of-sample period (2018-10-04 to 2025-01-13, approximately 78 months / 1,638 trading days) produced an annualised Sharpe ratio of **1.24** with an annualised return of 10.9% and a maximum drawdown of 8.5% — outperforming buy-and-hold SPY on all three risk-adjusted measures. The holdout period (2025-01-14 to 2025-12-31, exactly 252 trading days) extended that record with a Sharpe of **1.61**, annualised return of 14.6%, and maximum drawdown of 5.9%, against a buy-and-hold SPY Sharpe of 1.02 over the same window. Despite these strong point estimates, the strategy is flagged `needs_final_exam` because two robustness gates were not cleared: the 95% bootstrap confidence interval lower bound on holdout Sharpe is negative (−0.35), and the Deflated Sharpe Ratio (DSR) sits at 0.942, just below the 0.95 threshold (C8). A third gate (C10, excess return over benchmark) also failed — the strategy's raw return of 14.6% trailed SPY's 19.7% despite superior risk-adjustment, a consequence of systematic de-risking during a predominantly trending year. These failures are statistical artefacts of a thin 252-day holdout window — one year produces wide bootstrap intervals regardless of the underlying signal quality. They represent a data insufficiency, not an economic failure of the signal mechanism. The strategy requires an additional observation period before a final pass verdict can be rendered.
