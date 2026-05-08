# Final Exam Handoff — hy_ig_v2_spy → Quincy (QA)

**Date:** 2026-05-08  
**From:** Econ Evan  
**To:** Quincy (QA Agent)  
**Pair:** hy_ig_v2_spy  
**Task:** ECON-FE1 Final Exam — Pilot Retro-Apply

---

## Artifact

`results/hy_ig_v2_spy/final_exam_results_20260508.json`  
Schema: `docs/schemas/final_exam_results.schema.json` v1.0.1

---

## Status Recommendation

**`needs_final_exam`**

Two conditions prevent upgrade to `passed_final_exam`:

1. **C2 BORDERLINE** — No fresh holdout exists (only ~85 post-OOS trading days as of 2026-05-08, below the 252-day floor). The confirmation window reuses the tournament OOS window (2018-01-01 to 2025-12-31). Winner was selected on OOS Sharpe — this window informed the selection. FE1 condition 2 cannot be fully satisfied in this pilot retro-apply.

2. **C5 FAIL** — `confirm_excess_ann_return = -3.42%` (winner 11.33% ann return < benchmark B&H 14.75%). Falls below the ≥ 0.00% floor. The strategy achieves its value via tail-risk reduction (MDD -10.2% vs B&H -33.7%), not excess return.

---

## Key Metrics

| Metric | Value | Floor | Status |
|--------|-------|-------|--------|
| confirm_sharpe | 1.274 | ≥ 0.50 | PASS |
| confirm_excess_ann_return | -3.42% | ≥ 0.00% | **FAIL** |
| confirm_delta_sharpe | +0.5014 | ≥ +0.10 | PASS |
| confirm_max_drawdown | -10.2% | ≤ BH -33.7% + 5% | PASS |
| confirm_n_obs | 2088 | ≥ 252 | PASS |
| Confirmation window = OOS window | yes | must be fresh | **BORDERLINE** |

**Bootstrap (stationary, block=21, n=1000):**
- Sharpe 95% CI: [0.895, 1.664]
- Excess return 95% CI: [-8.3%, +10.9%]
- P(winner Sharpe > benchmark): 100%
- P(winner return > benchmark): 63.1%
- P(winner MDD ≤ benchmark + 5%): 100%

**Multiple testing:**
- n_trials_raw: 2167, n_trials_effective: 150
- Method: deflated_sharpe_ratio
- DSR: 0.0 (adjusted_p_value: 1.0 under independence assumption)
- Caveat: all strategies test same asset with high cross-strategy correlation; true effective N << 2167. DSR result is mechanically severe, not definitive evidence of pure data-mining.

---

## C2 Borderline — Evidence

The tournament had no IS-only selection metric. `tournament_results_20260410.csv` contains only OOS metrics (`oos_sharpe`, `oos_ann_return`, `max_drawdown`). The winner (`S6_hmm_stress / T4_hmm_0.5 / P2 / lead=0`, OOS Sharpe 1.274) was ranked second-best on OOS Sharpe (behind `S7_ms_stress / P1 / lead=1` at 1.717, which was not selected — reason documented in `tournament_tie_note.md`). The OOS window directly informed the selection rank. This disqualifies the OOS window as a clean holdout.

---

## Validation Command

```bash
cd /workspaces/aig-rlic-plus
python3 -c "import json,jsonschema; schema=json.load(open('docs/schemas/final_exam_results.schema.json')); data=json.load(open('results/hy_ig_v2_spy/final_exam_results_20260508.json')); jsonschema.validate(data, schema); print('PASS')"
```

Expected output: `PASS`

---

## GATE-ES1 Acceptance Command

```bash
# Positive pattern: artifact present and schema-valid
python3 -c "import json,jsonschema; schema=json.load(open('docs/schemas/final_exam_results.schema.json')); data=json.load(open('results/hy_ig_v2_spy/final_exam_results_20260508.json')); jsonschema.validate(data, schema); assert data['status_recommendation']=='needs_final_exam'; assert data['sample']['confirm_n_obs'] >= data['sample']['minimum_confirmation_n_obs']; assert data['qa']['quincy_status']=='not_started'; print('GATE-ES1 ACCEPT')"

# Negative pattern: artifact must NOT claim passed_final_exam (fresh holdout absent)
python3 -c "import json; data=json.load(open('results/hy_ig_v2_spy/final_exam_results_20260508.json')); assert data['status_recommendation'] != 'passed_final_exam', 'FAIL: should not be passed_final_exam without fresh holdout'; print('GATE-ES1 NEGATIVE PASS')"
```

---

## QA Actions Required

1. Replay schema validation (command above).
2. Verify `confirm_n_obs = 2088 >= minimum_confirmation_n_obs = 252` (F-01).
3. Verify `status_recommendation = needs_final_exam` is appropriate given C2 borderline and C5 failure.
4. Confirm `pass_fail.failed_gates` accurately lists C2 and C5 as blockers.
5. Review DSR caveat in warnings — confirm the multiple-testing note is adequate.
6. Set `qa.quincy_status` to `passed` or `failed` and record `qa_artifact` path in the JSON after QA replay.
7. Update `evidence_status.json` for this pair per team coordination protocol.

---

## Notes on C5 Interpretation

The strategy is classified as `min_mdd` objective (per `tournament_winner.json`). Under a pure return-maximization objective, C5 would fail. Under a risk-reduction mandate, the MDD improvement (+23.5 pp better than B&H) is the primary value. Quincy should document this objective context in the QA artifact — the numeric floor failure is real but must be interpreted against the declared mandate.
