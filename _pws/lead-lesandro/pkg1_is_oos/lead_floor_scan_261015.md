# Fleet L0 scan — 2026-10-15 (haiku scan, Lead spot-checked nhs_spy + gate scope)
Refs: main, fix261006_255_leadfloor_rerun (fix).
- main: 25/33 pipelines have L0; 15 L0 pairs not in lead_axis_registry (13 live). Monthly L0 published winners: cement_spy, ism_mfg_spy, nhs_spy.
- fix: 12/37 have L0; live monthly L0: housing_starts, nhs_saar, nhs_spy, t10y3m, indpro_spy, indpro_xlp, petrol_inv (+ daily vix/hy_ig/gold_copper = OK).
  Most have *_rebuilt floored twins (nhs, nhs_saar, housing_starts, t10y3m) but legacy pages still live.
- CONFIRMED by Lead: fix nhs_spy grid [0,1,2,3,6,9,12] (scripts/pair_pipeline_nhs_spy.py:607) while registry floor is L2 -> published winner L0 still live.
- umcsent_xlv on fix: lead_times floored at :1096 but leftover range(0,13) at :1511.
- indpro_spy/xlp: lead_times=[0,1,2,3,6] both refs; registry on fix says [1..13] (mismatch).
- GATE GAP (confirmed scripts/gate_lead_axis.py:11-30): checks lead AXIS unit only, only registered pairs; does NOT check grid min >= floor or grid == registry.
Proposed: gate_lead_floor — for every live pair, pipeline grid min >= registry lead_floor and grid == registry grid; unregistered live pair = FAIL.

## Gate verifier findings (2026-10-15, sonnet; Lead verified gold_copper)
- gate_lead_floor: 0 false negatives on 26 PASS pipelines; 0 false positives; 7/8 FAIL = real sub-floor; phlxsox = registry wrong.
- CONFIRMED BY LEAD: gold_copper_xli winner L0 is LOOKAHEAD. econ_pipeline_gold_copper_xli.py:149-153 pos=(sig<=t).shift(lead), strat=pos*xli_ret; xli_ret == xli.pct_change() same-day (corr 1.0, data/gold_copper_xli_daily_20260526.parquet). Published OOS Sharpe 1.273 invalid. Live on main AND floor. Gate can't see it (grid in refresh_gold_copper_xli_lead_artifacts.py:45, registry floor 0).
- petrol_inv_spy: registry floor 0 wrong -> 1 (monthly mean of weekly stocks; last week released ~Wed of M+1). Winner L11 unaffected.
- phlxsox_spy: pipeline [1,5,..] correct (no pos shift); registry floor/grid 0 wrong.
- permit_spy (:395), t10y3m_rebuilt_spy (:337,:426): pos.shift(1) on top of signal.shift(lead) -> double shift; no lookahead but published lead mislabelled by +1 (L6 is really L7).
- hy_ig, vix_vix3m: pos.shift(1) -> L0 legit.
- Gate gaps: scans only pair_pipeline_*.py (misses econ_pipeline_/refresh_*_lead_artifacts); unparseable/missing grid = WARN not FAIL; floor is alignment-dependent (needs "effective lag" = lead + position shift).
