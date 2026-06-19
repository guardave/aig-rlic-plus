[Data Dana] — Mode-3 session dispatch — pair `m2sl_yoy_spy` (stage 1, REVISED)

You are Data Dana. (Persona via `./AGENTS.md` as before.) Lead Lesandro is manager + sole checker.

## Your BLOCK was correct — here is Lead's adjudication
You blocked on the Data Master cross-check (max level diff 108.5, YoY diff 0.52pp). Good call to escalate. Lead investigated:
- FRED M2SL (2025-06/07/08) = 21938.8 / 22020.0 / 22086.9.
- Data Master M2SL (same months) = 22022.1 / 22115.8 / 22195.4.
- Data Master runs **consistently ~0.4–0.5% ABOVE FRED, and the gap GROWS toward recent dates** (83 → 96 → 108.5). This is the textbook signature of **M2 seasonal-adjustment / benchmark REVISIONS** (largest at the most recent observations). The Data Master is a stale-vintage snapshot (ends 2025-08); FRED carries the current revised vintage.

**Verdict: benign vintage/revision drift, NOT a computation error or wrong series. FRED M2SL is GROUND TRUTH.** Proceed.

## Corrected instruction — relax the cross-check, build from FRED
1. **Source of truth = FRED `M2SL`** (live, current vintage, 1959-01 → 2026-04). Build the indicator from it. Compute `m2sl_yoy` = 12-month % change.
2. **Cross-check = SOFT sanity check, NOT a hard equality gate.** M2 SA is heavily revised. Replace the hard-fail cross-check with: confirm (a) Pearson correlation of overlapping M2SL levels ≥ 0.999, AND (b) YoY trajectories agree in shape/sign over the overlap. Tolerate level diffs up to ~1% and YoY diffs up to ~1pp (concentrated at recent dates) as expected revision drift — log them as an informational note, do NOT block. Only escalate again if the series DIVERGE in shape/sign (which would indicate a wrong series or a YoY-method bug), not on revision-magnitude diffs.
3. Everything else in the original brief stands (`_pws/lead-lesandro/m2sl_yoy/briefs/dana_brief.md`): monthly + daily LVCF datasets, `days_since_release`, stationarity battery (level non-stationary → use YoY/transforms; flag 2020 surge + 2022-23 first-ever contraction), surgical `prospective_pairs.csv` edit to `in_progress` (NO regen), schema-valid sidecar (DATA gate exit 0), stationarity CSV, manifest update, handoff. Direction prior: procyclical (empirical).

## Output
- Print `DANA DONE` at line start + artifact list when finished, or `DANA BLOCKED: <reason>` (only for a genuine shape/sign divergence, not revision drift).

Begin now.
