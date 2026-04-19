# Tournament Tie-Break Note — HY-IG v2 × SPY

**Pair:** `hy_ig_v2_spy`
**Source:** `results/hy_ig_v2_spy/tournament_results_20260410.csv` (2167 rows, 1970 valid)
**Top `oos_sharpe`:** 1.274
**Tie threshold (ε):** 0.01
**Generated:** 2026-04-19 (Wave 5C retro-apply of ECON-T3)

## Near-tie candidate set (rows within ε = 0.01 of top oos_sharpe)

| Rank | signal_code (pipeline) | threshold | strategy | lead_days | oos_sharpe | oos_ann_return | oos_max_drawdown | oos_n_trades | annual_turnover |
|------|------------------------|-----------|----------|-----------|-----------:|---------------:|-----------------:|-------------:|----------------:|
| 1    | S6_hmm_stress          | T4_hmm_0.7 | P2      | 0         | 1.2740     | 11.33          | -10.20           | 6004         | 3.78            |
| 2    | S6_hmm_stress          | T4_hmm_0.5 | P2      | 0         | 1.2740     | 11.33          | -10.20           | 6004         | 3.78            |

## ECON-T3 cascade simulation

| Step | Criterion | Result |
|------|-----------|--------|
| 1 | Higher `oos_sharpe` | TIE at 1.2740 (both rows) — advance |
| 2 | Higher `oos_ann_return` | TIE at 11.33 — advance |
| 3 | Lower absolute `oos_max_drawdown` (closer to zero) | TIE at -10.20 — advance |
| 4 | Higher `oos_n_trades` | TIE at 6004 — advance |
| 5 | Lexicographic ascending of `signal_code` | Both rows share `signal_code = S6_hmm_stress`; identical key. |

## Resolution

Because both candidates share the same `signal_code` and identical OOS metrics across the entire cascade, ECON-T3's five-step chain does not produce a unique winner on `signal_code` alone. Economic interpretation of the two threshold parameters:

- Both rows are P2 (signal-strength) strategies. Under P2, position size scales continuously with the raw HMM stress probability. The threshold (`0.5` vs `0.7`) is nominal only — P2 sizing ignores it (entry/exit are not gated on the threshold when the strategy weight is a function of signal magnitude rather than a binary crossing). This explains the identical oos_sharpe / oos_ann_return / oos_max_drawdown / oos_n_trades across the two rows: the two thresholds produce identical position paths under P2 sizing.
- The shipped `winner_summary.json` uses `threshold_value = 0.5` (the `T4_hmm_0.5` row). Selection was by pandas sort stability in the original pipeline. Under a literal ECON-T3 reading (step 5 lexicographic on `signal_code` only), the tie is unbroken and an auxiliary lexicographic tiebreak on `threshold` (secondary key) was used: `T4_hmm_0.5 < T4_hmm_0.7` lexicographically, so `T4_hmm_0.5` wins.
- The P1 variants at rows 3-4 (`T4_hmm_0.7` P1 Sharpe 1.1749, `T4_hmm_0.5` P1 Sharpe 1.1611) are NOT in the ε-band and are excluded from tie consideration.

## Cascade level reached

**Level 5+ (lexicographic on auxiliary key `threshold`).** The shipped winner (`threshold_value = 0.5`, `threshold_rule = "gte"`) is the lexicographically smaller of the two P2 threshold variants that produce identical OOS performance, and is a defensible selection since the two candidates are observationally equivalent under P2 sizing.

## Out-of-cascade observation

Neither candidate dominates on turnover, trade count, or max drawdown — they are literal duplicates under P2 sizing. Under P1 sizing (binary long/cash), the two thresholds DO differentiate (rows 3-4 above), with `T4_hmm_0.7` slightly outperforming `T4_hmm_0.5` at the P1 level (1.1749 vs 1.1611). A future methodology revision could prefer the P1 `T4_hmm_0.7` row on interpretability grounds (probability > 0.7 is a cleaner stress-regime declaration than > 0.5), but that is a separate cascade (introducing a P1-preferred tiebreak is NOT part of v1 ECON-T3) and would require a rule revision with META-XVC divergence declaration.
