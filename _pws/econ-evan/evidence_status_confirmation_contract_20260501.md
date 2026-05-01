# Evidence-Status Confirmation-Test Contract Draft

**Author:** econ-evan  
**Date:** 2026-05-01  
**Audience:** Lead Lesandro, QA Quincy  
**Scope:** Methodological contract for moving a pair from `found_in_search` to `needs_final_exam` or `passed_final_exam`. This draft proposes exact criteria and artifact shape. It does not edit shared schemas or upgrade any pair status.

## 1. Status Semantics

### `found_in_search`

Use when the displayed winner was selected from the broad tournament/search layer and has no post-selection confirmation record.

Sufficient evidence:
- Tournament/search results exist and identify a winner.
- The winner may have OOS metrics from the same search protocol, but those metrics were part of model/recipe selection or winner ranking.

Insufficient for upgrade:
- High OOS Sharpe alone.
- Good in-sample diagnostics.
- A large leaderboard delta versus buy-and-hold.
- A single OOS period that was also used to choose among many signals, thresholds, leads, or strategy rules.

### `needs_final_exam`

Use when a final-exam protocol has been declared, or partial confirmation artifacts exist, but the pair has not passed all gates.

Sufficient evidence:
- A frozen winning rule is named before confirmation starts.
- The confirmation window or walk-forward design is recorded.
- Search-space size and adjustment plan are recorded.
- One or more required final-exam artifacts are missing, incomplete, failed, or pending QA replay.

This is the correct status for a pair queued for confirmation work.

### `passed_final_exam`

Use only after the frozen winner passes a fresh post-selection confirmation test and QA can replay the evidence.

Minimum sufficient evidence:
- Frozen rule identity is unchanged from tournament winner: signal, transform, lead/lag, threshold rule/value, position rule, cost assumption, benchmark, and target class parameters.
- Confirmation sample was not used to select, tune, narratively rescue, or threshold the winner.
- All required metric thresholds below pass.
- Multiple-testing/luck adjustment is documented and passes.
- Time-series uncertainty is estimated with a block bootstrap or stationary bootstrap.
- Artifacts are present under `results/{pair_id}/` and machine-readable.
- Quincy verifies artifact presence, schema validity, and at least one independent recomputation or checksum-level replay.

## 2. Recommended Final-Exam Designs

Preferred order:

1. **Untouched chronological holdout.** Best option. Reserve the most recent contiguous block before any tournament rerun. The winner is selected on the training/search window, then evaluated once on the holdout.
2. **Nested walk-forward final exam.** Acceptable when sample is too short for a single holdout. At each fold, the search is run only on past data, the local winner is frozen, and performance is measured on the next fold. The final selected production rule must be compared against the distribution of fold winners and against buy-and-hold.
3. **Locked-rule forward validation.** Acceptable for legacy pairs when a rule was already selected and cannot be re-created with a pristine holdout. Freeze the existing rule, then evaluate only on data added after the freeze date. Until enough new observations accrue, status remains `needs_final_exam`.

Not sufficient:
- Re-splitting after looking at the current winner's performance.
- Reusing the tournament OOS slice as the final exam if that OOS slice influenced recipe choice.
- Changing thresholds, direction, lead, costs, or benchmark after seeing confirmation results.

## 3. Sample and Holdout Constraints

Minimum confirmation sample:

| Target / frequency class | Minimum holdout length | Minimum observations | Notes |
|---|---:|---:|---|
| Daily equity / rates / credit strategy | 24 months | 252 trading days | Prefer 36+ months when feasible. |
| Monthly macro-to-ETF strategy | 36 months | 36 monthly observations | Prefer 60+ months or walk-forward folds. |
| Crypto / 24-7 daily strategy | 18 months | 365 calendar days | Higher noise; require stricter drawdown and turnover review. |

Holdout quality constraints:
- Holdout must be chronologically after the search window.
- No overlap between observations used for threshold estimation and confirmation returns, except for rolling features computed using only past values.
- All feature transforms must be causal: no centered filters, full-sample z-scores, or percentile thresholds estimated with future data.
- Transaction costs and benchmark must match the target-class parameters in the econometrics SOP.
- Confirmation must include at least 5 non-zero position changes for trade-based strategies. If fewer, pass/fail must rely more heavily on return/drawdown metrics and the note must flag low trading evidence.

## 4. Required Metrics

Every final exam should report these metrics for the frozen winner and benchmark:

- `confirm_ann_return`
- `confirm_sharpe`
- `confirm_sortino`
- `confirm_max_drawdown`
- `confirm_calmar`
- `confirm_hit_rate`
- `confirm_turnover`
- `confirm_n_trades`
- `confirm_excess_ann_return`
- `confirm_delta_sharpe`
- `confirm_delta_max_drawdown`
- `confirm_cost_bps`
- `confirm_benchmark_sharpe`
- `confirm_benchmark_ann_return`
- `confirm_benchmark_max_drawdown`

Required uncertainty metrics:

- `bootstrap_ci_sharpe`: 2.5%, 50%, 97.5% confidence interval.
- `bootstrap_ci_excess_return`: 2.5%, 50%, 97.5%.
- `bootstrap_prob_sharpe_gt_benchmark`: probability winner Sharpe exceeds benchmark Sharpe under resampling.
- `bootstrap_prob_return_gt_benchmark`: probability winner annualized return exceeds benchmark.
- `bootstrap_prob_mdd_not_worse`: probability winner max drawdown is no worse than benchmark by more than the allowed tolerance.
- `deflated_sharpe_ratio` or `probabilistic_sharpe_ratio_adjusted`: adjustment for many recipes tried.
- `n_trials_effective`: effective number of recipes tested after collapsing highly correlated variants.
- `n_trials_raw`: raw tournament rows considered.

## 5. Pass Threshold Recommendations

### General pass thresholds

A pair passes final exam only if all are true:

- Confirmation Sharpe meets target-class validity floor: equity >= 0.30, fixed income/rates/credit >= 0.50, crypto >= 0.20.
- `confirm_delta_sharpe >= +0.10` versus benchmark.
- `confirm_excess_ann_return >= 0.00` after costs.
- `confirm_max_drawdown <= benchmark_max_drawdown + 0.05` in absolute drawdown terms. Example: if benchmark MDD is -15%, winner must not be worse than -20%.
- Bootstrap median `confirm_delta_sharpe > 0`.
- Lower 5% one-sided bootstrap bound for `confirm_delta_sharpe` is not severely negative: must be greater than -0.10.
- `bootstrap_prob_sharpe_gt_benchmark >= 0.60`.
- Multiple-testing-adjusted `p_value <= 0.10` or `deflated_sharpe_ratio >= 0.50`.
- No unflagged causal leakage, cost mismatch, benchmark mismatch, or target-class parameter mismatch.

### Strong pass flag

Optional stronger tier for Lead/Ray wording, not a separate app status yet:

- `confirm_delta_sharpe >= +0.20`.
- `bootstrap_prob_sharpe_gt_benchmark >= 0.70`.
- Multiple-testing-adjusted `p_value <= 0.05` or `deflated_sharpe_ratio >= 0.70`.
- Drawdown improves versus benchmark or is no worse by more than 2 percentage points.

### Fail / remain `needs_final_exam`

Remain `needs_final_exam` when any of these are true:

- Holdout too short.
- Rule was changed after confirmation started.
- Effective trial count is unknown.
- Bootstrap uncertainty is missing.
- Adjusted p-value / deflated Sharpe is missing.
- Confirmation metric passes point estimate but fails uncertainty or luck adjustment.
- QA cannot replay the artifact lineage.

## 6. Multiple-Testing and Luck Adjustment

Recommended default:

1. Record `n_trials_raw` as the number of tournament result rows eligible to win after basic validity filters.
2. Estimate `n_trials_effective` by clustering strategy return series or signal-return series with absolute correlation >= 0.90, then counting clusters. If return series are unavailable, use a conservative fallback: `n_trials_effective = ceil(sqrt(n_trials_raw))`, with a note that this is approximate.
3. Compute a Deflated Sharpe Ratio (DSR) or equivalent Probabilistic Sharpe Ratio adjusted for `n_trials_effective`, skew, kurtosis, and sample length.
4. Also compute a bootstrap max-statistic p-value: resample blocks, evaluate the frozen winner and a representative set of searched alternatives, and estimate how often the best noise-adjusted alternative beats the observed winner.

If only one adjustment can ship in P2, ship DSR plus raw/effective trial counts. Quincy can gate on presence and threshold before requiring the heavier max-statistic bootstrap.

## 7. Bootstrap and Time-Series Uncertainty

Default uncertainty treatment:

- Use stationary bootstrap or circular block bootstrap on aligned daily/monthly return rows.
- Set expected block length by frequency:
  - Daily: 21 trading days default; sensitivity at 5 and 63 days.
  - Monthly: 6 months default; sensitivity at 3 and 12 months.
  - Crypto daily: 30 calendar days default; sensitivity at 7 and 90 days.
- Use at least 1,000 bootstrap replications for routine confirmation, 5,000 for reference-pair promotion.
- Resample paired rows of strategy return and benchmark return together, preserving dependence.
- Recompute Sharpe, return, drawdown, and deltas inside each bootstrap sample.

Do not bootstrap raw observations independently day-by-day without blocks; that understates uncertainty for autocorrelated strategies.

## 8. Proposed Artifact Shape

### Minimal extension to `results/{pair_id}/evidence_status.json`

Current schema v1.0.0 can only hold summary strings. I recommend a v1.1.0 additive schema change adding a compact `final_exam` object while keeping existing display fields.

Proposed patch text for schema, not applied:

```json
{
  "final_exam": {
    "type": "object",
    "required": [
      "frozen_rule_id",
      "frozen_at",
      "search_window",
      "confirmation_window",
      "n_trials_raw",
      "n_trials_effective",
      "primary_metric",
      "thresholds_version",
      "result_artifact",
      "qa_status"
    ],
    "properties": {
      "frozen_rule_id": { "type": "string" },
      "frozen_at": { "type": "string", "format": "date-time" },
      "search_window": {
        "type": "object",
        "required": ["start", "end"],
        "properties": {
          "start": { "type": "string", "format": "date" },
          "end": { "type": "string", "format": "date" }
        },
        "additionalProperties": false
      },
      "confirmation_window": {
        "type": "object",
        "required": ["start", "end", "n_obs"],
        "properties": {
          "start": { "type": "string", "format": "date" },
          "end": { "type": "string", "format": "date" },
          "n_obs": { "type": "integer", "minimum": 1 }
        },
        "additionalProperties": false
      },
      "n_trials_raw": { "type": "integer", "minimum": 1 },
      "n_trials_effective": { "type": "integer", "minimum": 1 },
      "primary_metric": {
        "type": "string",
        "enum": ["delta_sharpe", "excess_ann_return", "min_drawdown"]
      },
      "thresholds_version": { "type": "string" },
      "result_artifact": { "type": "string" },
      "qa_status": {
        "type": "string",
        "enum": ["not_started", "pending_quincy", "qa_passed", "qa_failed"]
      }
    },
    "additionalProperties": false
  }
}
```

Example compact status file:

```json
{
  "pair_id": "hy_ig_v2_spy",
  "schema_version": "1.1.0",
  "status": "passed_final_exam",
  "updated_at": "2026-05-01T00:00:00Z",
  "confirmation_test": "locked_rule_chronological_holdout_v1",
  "confirmation_window": { "start": "2026-01-01", "end": "2026-12-31" },
  "plain_english": "This rule passed a fresh final exam on data that did not help choose it.",
  "technical_note": "Frozen winner beat benchmark after costs; DSR and block-bootstrap thresholds passed.",
  "next_step": "Keep status under review on scheduled rerun.",
  "owner": "evan",
  "final_exam": {
    "frozen_rule_id": "S2_yoy__T4_zero__P1_long_cash__L6",
    "frozen_at": "2026-05-01T00:00:00Z",
    "search_window": { "start": "1998-01-31", "end": "2025-12-31" },
    "confirmation_window": { "start": "2026-01-01", "end": "2026-12-31", "n_obs": 252 },
    "n_trials_raw": 1305,
    "n_trials_effective": 115,
    "primary_metric": "delta_sharpe",
    "thresholds_version": "final_exam_thresholds_v1",
    "result_artifact": "results/hy_ig_v2_spy/final_exam_results_20260501.json",
    "qa_status": "qa_passed"
  }
}
```

### Detailed companion artifact

Use `results/{pair_id}/final_exam_results_{YYYYMMDD}.json` for full metrics. This avoids bloating the display-oriented status file.

Required top-level fields:

```json
{
  "pair_id": "string",
  "schema_version": "1.0.0",
  "generated_at": "date-time",
  "owner": "evan",
  "status_recommendation": "found_in_search|needs_final_exam|passed_final_exam",
  "frozen_rule": {
    "rule_id": "string",
    "signal_column": "string",
    "threshold_rule": "string",
    "threshold_value": "number|null",
    "lead_lag": "integer",
    "strategy_family": "string",
    "position_rule": "string",
    "cost_bps": "number",
    "benchmark": "string"
  },
  "sample": {
    "search_start": "date",
    "search_end": "date",
    "confirm_start": "date",
    "confirm_end": "date",
    "confirm_n_obs": "integer",
    "frequency": "daily|monthly|weekly|crypto_daily",
    "holdout_type": "chronological|nested_walk_forward|locked_rule_forward"
  },
  "metrics": {},
  "uncertainty": {},
  "multiple_testing": {},
  "pass_fail": {
    "overall_pass": "boolean",
    "failed_gates": ["string"],
    "warnings": ["string"]
  },
  "artifact_lineage": {
    "tournament_results": "path",
    "winner_summary": "path",
    "winner_trade_log": "path",
    "code_version": "git sha or script hash"
  },
  "qa": {
    "quincy_status": "not_started|pending|passed|failed",
    "qa_artifact": "path|null"
  }
}
```

## 9. Quincy Gate Recommendations

Quincy should be able to reject upgrades mechanically when:

- `status = passed_final_exam` but `final_exam` block is missing.
- `status = passed_final_exam` but referenced `result_artifact` does not exist.
- `qa_status != qa_passed`.
- `status_recommendation` in the companion artifact disagrees with `evidence_status.json`.
- Required metrics are absent or null.
- Any pass/fail gate is false without Lead override.
- `n_trials_effective` is absent, zero, or greater than `n_trials_raw`.
- Confirmation window overlaps the search window.
- Frozen rule fields differ from `winner_summary.json` / `tournament_winner.json` without a regression note and Lead approval.

## 10. SOP Change Recommendation

Recommended new Econometrics SOP rule text, proposed only:

> **ECON-FE1 - Final-Exam Confirmation Contract.** Tournament winners are discovery-grade until a frozen-rule final exam is recorded. Evan may set `evidence_status.status = passed_final_exam` only when the frozen winner passes the target-class Sharpe floor, positive after-cost excess return, delta-Sharpe, drawdown, block-bootstrap uncertainty, and multiple-testing/luck-adjustment gates documented in `final_exam_results_{YYYYMMDD}.json`. Missing, partial, or QA-unverified confirmation artifacts must use `needs_final_exam`, not `passed_final_exam`. Existing pairs without confirmation artifacts remain `found_in_search`.

Recommended Team Coordination gate text, proposed only:

> **GATE-32 - Evidence-Status Confirmation Replay.** Quincy must independently verify every `passed_final_exam` status by validating `evidence_status.json`, opening the referenced final-exam artifact, checking sample separation, confirming frozen-rule consistency against winner artifacts, and replaying or spot-recomputing the headline pass/fail metrics. Any failed check downgrades the pair to `needs_final_exam` until Evan repairs the artifact and Lead accepts the rerun.

