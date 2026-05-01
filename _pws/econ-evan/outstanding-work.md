# Econ Evan — Outstanding Work

_Last updated: 2026-05-01 evidence-status contract draft_

## Active Backlog (Evan's lane)

### Evidence-status final-exam contract [Drafted 2026-05-01 — awaiting Lead/Quincy arbitration]
Draft note exists at `_pws/econ-evan/evidence_status_confirmation_contract_20260501.md`.

Action: Lead and Quincy decide whether to:
- Promote proposed ECON-FE1 and GATE-32 wording into SOPs.
- Add the proposed `final_exam` object to `docs/schemas/evidence_status.schema.json` v1.1.0.
- Create a separate `docs/schemas/final_exam_results.schema.json` for detailed confirmation metrics.

No pair should be upgraded to `passed_final_exam` until this contract is accepted and a QA replay gate exists.

### BL-LEGACY-WINNER-SUMMARY-SHAPE [Wave 10K — FIRST DISPATCH]
6 legacy pairs (`indpro_spy`, `permit_spy`, `vix_vix3m_spy`, `sofr_ted_spy`, `dff_ted_spy`, `ted_spliced_spy`) have `winner_summary.json` files missing 7+ required fields versus schema v1.1.0 shape. Fields typically absent:
- `generated_at`, `signal_column`, `target_symbol`, `threshold_rule`, `strategy_family`
- `oos_max_drawdown`, `oos_n_trades`, `oos_period_start`, `oos_period_end`

Legacy extras that may still be present: `threshold_code`, `strategy_code`, `*_display_name`, `lead_*`, `win_rate`.

Action: Produce compliant `winner_summary.json` for each pair via reconstruction from existing artifacts (tournament CSV, trade log, parquet). Run `validate_schema.py` against each before committing.

---

### CP1 methodology_note [Next pair — before Vera handoff]
Every `subperiod_sharpe.csv` handoff to Vera and Ray MUST include a methodology annotation:
> "Sub-period Sharpes reflect directional durability only (sign(signal) × return), NOT replication of tournament execution mechanics. Use tournament OOS Sharpe as the point-estimate reference."

Add this as a mandatory field in the handoff note template AND as a rule in `econometrics-agent-sop.md` under ECON-CP1.

---

### BL-OOS-SPLIT-LEGACY [Deferred — on future tournament rerun]
6 backfilled legacy pairs lack `oos_split_record.json`. Emit this artifact on any future tournament rerun for these pairs.

---

### BL-801 [Backlog — low urgency]
`app/pages/9_hy_ig_v2_spy_strategy.py:197` uses `_winner.get("max_drawdown", -0.102)` but schema field is `oos_max_drawdown`. Fix: rename producer field OR update consumer + add producer-side keys-in-use check. Reactivation trigger: next consumer-audit wave or Pair #4 start.

---

### BL-802 [Backlog — schema gap]
Turnover basis declaration: 2.8× mismatch between HY-IG v2 `annual_turnover=3.78/yr` and implied turnover `10.57/yr`. Not a bug (different basis) but a schema gap. Proposal: add `turnover_basis` enum to `winner_summary.schema.json` + augment QA-CL2.

---

### interpretation_metadata.schema.json [Authoring task — Wave 10K]
`interpretation_metadata.json` has no formal JSON schema — vocabulary drift is undetectable programmatically. Author `docs/schemas/interpretation_metadata.schema.json` and wire into smoke_loader or validate_schema.py.

---

## SOP Rules Requiring Retro-Apply

| Rule | Status |
|------|--------|
| ECON-CP1 methodology_note | Not yet in SOP — must add before Pair #4 handoff |
| ECON-DIR1 | Live in SOP (Wave 10I.C); consumer-gatekeeper framing confirmed Wave 10J |
| ECON-UD | Live and blocking for all pairs (Wave 10I.C) |
| ECON-SD audit | Dead-letter — Quincy SOP does not name this check; escalate to Lead |
