# Lead-Grid Frequency Standard

**Status:** Adopted 2026-07-14 (stakeholder-agreed). Governs how every pair's **lead grid** (the set of horizons at which a signal is lagged before forming a position) is chosen, and how the lead tournament / coherent lead chart are built. Applies to all pairs and all future pairs. Rollout is gradual: the daily Class-A pairs adopt it first; existing pairs are re-validated against it as a tracked follow-up.

Born from the GH#13 lead-coherence rollout — specifically the `hy_ig_spy` failure (a **monthly** L0–12 lead sweep bolted onto a **daily**-traded 0-day-lead winner) and the `umcsent_xlv` cap debate.

---

## Core principle

**The math decides the winner on the full grid. Economic priors are reference, never a selection constraint.**

If a signal genuinely predicts a target at some horizon, the full-grid tournament will find it; if an economic prior is correct, the math reconciles with it (shows nothing where the prior says nothing). We therefore never pre-exclude a lead because a qualitative view deems it implausible — we test it, and if the math surfaces something unexpected we *adjudicate* it (below), we do not ignore it.

---

## The decision tree

Given a signal → target pair:

### Step 1 — Signal release frequency sets the lead **axis** (HARD RULE, gate-enforced)

The lead axis unit equals the signal's **native release/update frequency**. You may not test a lead finer than the signal updates, and you may not resample to a **coarser** frequency — resampling builds a *second* tournament whose winner differs from the deployed strategy (this is exactly the `hy_ig` bug: a monthly sweep on a daily signal).

| Signal type | Axis | Grid |
|---|---|---|
| Daily market data (VIX/VIX3M, credit spreads, gold/copper, SOX relative strength) | **daily** | `{0, 1, 5, 21, 63, 126, 252}` trading days |
| Weekly (jobless claims, some Fed series) | weekly | `{0, 1, 2, 4, 8, 13, 26, 52}` weeks |
| Monthly (ISM, INDPRO, UMCSENT, M2, BUSLOANS, sentiment/survey) | **monthly** | contiguous `L0–12` |
| Quarterly (ECI, GDP) | quarterly | `L0–4` (extend to `L0–8` only with rationale) |

A **pre-commit gate** enforces that a pair's lead artifacts (lead tournament, coherent lead chart, lead correlation) are on the axis implied by its recorded signal frequency. See "Enforcement."

### Step 2 — Publication lag sets the real-time floor (derived per source, not a default)

**The floor is derived from the data's actual release calendar by one temporal-ordering principle — there is no blanket default.** (Amended 2026-10-06, stakeholder decision: the earlier "floor at L1" wording was a shortcut that is wrong for sources released later than the next period-start; a default that contradicts the principle is not acceptable — the principle governs, per source.)

**Principle (strict; amended 2026-10-16, stakeholder decision).** The reading for reference period `M` may only drive a position whose **return window starts after that reading is publicly released**. Positions are rebalanced at period-end closes, and a position set at the close of period-end `e` earns the return `e → next period-end`. Let the **effective lag** be

> `E = L + position_shift`

where `L` is the lead in the grid and `position_shift` (0 or 1, recorded in the registry and detected in code by `gate_lead_floor.py`) is any extra `pos.shift(1)` applied before multiplying by the return. At effective lag `E`, the reading for `M` drives the return window that **opens at the period-end of `M+E−1`**. The strict floor is

> floor `E*` = smallest `E` with `first_release(M) ≤ period_end(M+E−1)`

measured against **actual first-release dates** (ALFRED first-vintage `realtime_start` for FRED series; the publisher's calendar or file-publication date otherwise). A reading released on the window-start date itself counts as available. The registry stores `lead_floor_effective = E*` and `lead_floor = E* − position_shift` (the smallest admissible grid lead). `L0` is still computed in lead-correlation diagnostics, but it is never a traded lead when `E* > position_shift`.

**Decision rule on observed release dates.** `E*` is the smallest `E` at which the gap `first_release(M) − period_end(M+E−1)` is `≤ 0` at the 90th percentile of reference periods 2018-01 → 2026-09 (or the series' available history). Residual exceptions (almost all from the Oct-2025 → Apr-2026 federal-shutdown backlog) are disclosed in the evidence file, not used to lower the floor. Where a source has only a 1-3-day lag past period-end (ISM), the floor still moves to the next period: the stakeholder chose the conservative option (2026-10-16) rather than assume an intraday execution delay.

Evidence: `_pws/lead-lesandro/pkg9_strict_floor/release_lag_evidence.csv` (per pair: release dates, lags, gap at each `E`); independent QA in `_pws/lead-lesandro/protocol/QA_floor_claim.md`.

**Derived strict floors (monthly-rebalanced pairs).** Lag = days from reference period-end to first release, ALFRED 2018-2026 median / p90 unless stated.

| Release timing (reference month M) | Lag band | Strict floor `E*` | Sources (evidence) |
|---|---|---|---|
| Real-time market data, observed at the close (no publication lag) | 0 d | **E1** (L0 with `pos.shift(1)`, or L1) | gold/copper, VIX/VIX3M, SOX/SPY |
| Vendor / FRED daily series posted after the close (next business day on FRED) | ~1 business day | **E2** (days for a daily-axis pair; months for a month-end-sampled pair) | ICE BofA HY/IG OAS (FRED posts next day); 10Y-3M Treasury spread sampled at month-end (Treasury posts the par curve after the close, FRED next day) |
| Released **within month M itself** (in-month surveys) | ≤ 0 d | **E1** | UMich sentiment incl. expectations components (UMCSENT final at or before month-end: median −3.5 d, p90 0 d); NAHB/Wells Fargo HMI (~mid-month M, ~−15 d) |
| Released **in month M+1, any day** (1-31 d after month-end) | 1-31 d | **E2** | ISM manufacturing (business day 1 of M+1, 1-3 d), ISM services (business day 3, 3-5 d), employment / UNRATE (1st Friday, 5 / 8 d), BUSLOANS H.8 (12 / 15 d), Cass freight (14 / 18 d), import prices IR (15 / 17 d), retail sales RSXFS (16 / 18 d), INDPRO (16 / 18 d), permits PERMIT / starts HOUST (18 / 21 d), M2SL (23 / 28 d), new home sales HSN1F (25 / 29 d), EIA weekly stocks monthly mean (last weekly print released the Wednesday after the last Friday of M, 2 / 5 d) |
| Released **in month M+2** (32-61 d) | 32-61 d | **E3** | Census M3 factory orders AMTMNO (34 / 40 d), retail inventories/sales MTIS RETAILIRSA (46 / 49 d) |
| Released **in month M+3 or later** (> 61 d) | > 61 d | **E4+** (per source) | USGS Mineral Industry Surveys, cement (file-publication dates 2021-09 → 2026-06: median 72 d, p90 122 d; 2025-07 onward a 95-165 d backlog) → **E5** |
| Weekly data carried to month-end | — | as for the release of the **last** weekly print in the month | EIA petroleum inventories (see the M+1 row) |

**Quarterly pairs** apply the same rule on quarter-ends (window opens at the quarter-end of `Q+E−1`): Fed SLOOS (DRTSCIS) is published inside the following quarter's first ~5 weeks but **before** the quarter it is stamped to ends (lag −56 d) → **E1**; ECI (ECIALLCIV, ~1 month, 30.5 / 31 d) → **E2**; credit-card delinquency (DRCCLACBS, ~7 weeks, 51 / 55 d) → **E2**.

Each pair's source, publication lag, strict floor and evidence are recorded in the Lead-Axis Registry (`publication_lag`, `lead_floor`, `lead_floor_effective`, `position_shift`, `floor_basis`); the floor is auditable, never chosen ad hoc.

**Applying the floor.** For a NEW pair, the searched grid is the anchored grid translated to start at the floor: `[f, f+1, …, f+H]` with `f = lead_floor` (e.g. monthly anchored `L0–12`, `f = 2` → `L2–L14`). The extra months at the top are publication latency, not economic horizon. **For an existing pair whose floor is raised after its grid was frozen** (protocol D2, "freeze the grid"), sub-floor leads are **truncated from the bottom** and the top is **not** extended: adding candidates after results have been seen is a researcher degree of freedom. Because the maximum lead is unchanged, the common in-sample start is unchanged, and any winner already at or above the floor is unchanged by construction (verified by rerun in the 2026-10-16 strict-floor package).

### Step 3 — Full anchored grid; the math selects the winner (NO CAPS)

Use the sparse, anchored grid for the axis (Step 1), extending to ~1 year of **economic horizon** (the pre-shift window; Step 2's floor then translates the whole grid up by the publication latency). Do **not** add idiosyncratic fill-in points. The literature review (see `docs/` research note) found:
- Horizon conventions are anchored to trading-period multiples — week (5d), month (~21d), quarter (~63d), half-year (~126d), year (~252d) — never dense even spacing.
- Adjacent overlapping horizons are ~99% correlated (Boudoukh-Richardson-Whitelaw): closely-spaced extra points add **no** independent information and only enlarge the multiple-testing surface.
- Idiosyncratic calendar-day points (7, 14, 30, 50 trading days) appear in **no** surveyed paper.

**No economic-window cap on selection.** The winner is the global max valid combo over the full grid. (This retires the interim `umcsent` "Option-C capped-selection" pattern.)

### Step 4 — Adjudicate outliers; never pre-exclude

If the full-grid winner lands at a long or economically-surprising lead, do not reject it and do not rubber-stamp it — **adjudicate** (ECON-T5):
- Degeneracy check (deployable-series scoring; the P2/P3-on-binary trap — see the degeneracy note).
- Overlapping-return inference: HAC / Newey-West or Hodrick(1992) standard errors.
- Raised significance hurdle: **t > 3.0** (Harvey-Liu-Zhu) after multiple-horizon testing, with joint inference across horizons.
- A plausible economic mechanism. Absent one, treat a lone long-lead hit as likely multiple-testing noise, but say so on the evidence of the *math*, not the prior.

### Step 5 — Economic/expected-horizon window = reference only

Record the pair's economically-motivated horizon window (e.g. UMCSENT→XLV at 2–5 months) as **interpretive context** in the narrative. It informs *how we read* the result; it never constrains *what is selected*.

---

## Enforcement & artifacts

- **Per-pair frequency record.** Each pair records its signal release frequency, **publication lag and derived floor (with its release-calendar justification, per Step 2)**, chosen lead axis, and grid (in the registry / pair config) so the treatment is auditable and reproducible — not decided ad hoc.
- **Axis-matches-frequency gate.** A pre-commit check (`scripts/gate_lead_axis.py`, to be built) blocks any commit where a pair's lead artifacts are on an axis inconsistent with its recorded signal frequency. This is the systematic fix for the `hy_ig` class of error.
- **Lead-floor gate.** `scripts/gate_lead_floor.py [pair ...]` (`--json OUT`; pure Python, no LLM) enforces the *values*, not just the axis. For every live pair (has `app/pages/*_{pair}_*.py`) it requires registry membership and statically parses every traded lead-grid definition in `scripts/pair_pipeline_{pair}.py`, `scripts/econ_pipeline_{pair}.py`, `scripts/refresh_{pair}_lead_artifacts.py` (and other `scripts/*{pair}*.py` that define a grid and a `pos*return`): assignments to `leads`/`lead_times`/`lead_grid`/`DAILY_LEADS`/..., `"leads": ...` dict entries, and `for lead in [...]` loops that call `.shift(lead)` (diagnostic CCF/Granger loops are ignored). FAIL on: no grid found, unparseable grid or syntax error (path:line), inconsistent duplicate grids, pipeline grid != registry `lead_grid`, and the strict-floor rules on the **effective lag** `E = L + position_shift`: every grid lead (hence `min(grid)`) and the published `winner_summary.json` lead must satisfy `L + position_shift >= lead_floor_effective`. The registry declares `position_shift` (0|1, default 0 = the extra `pos.shift(1)` applied before multiplying by the return), `lead_floor_effective` (the strict floor `E*`) and `lead_floor = E* - position_shift`; the gate FAILs when these disagree, and detects the shift in code and FAILs on disagreement ("alignment mismatch"; mixed/undetectable => WARN). When `lead_floor_effective` is absent it is taken as `lead_floor + position_shift`. Independently, effective lag must always be >= 1 (L0 with no extra shift earns the same bar it observes = lookahead, so a real-time daily pair needs `pos.shift(1)` or a grid starting at L1). Note a `sig.shift(lead)` + `pos.shift(1)` pair is a double shift: the published lead L really trades at L+1. Data-derived grids (`sorted(df.x.unique())`) are WARN-only. No pair-name special-casing. Not yet wired into pre-commit (fails on known debt pending pair fixes). **Per-period mode (default since 2026-10-16, pkg12 Phase A; `--mode floor` keeps the fixed effective-lag check above):** the registry-floor comparisons are replaced by a count, per grid lead and winner, of the backtest periods in which the fixed lag uses a reading of the pair's `release_calendar_series` whose `available_date` (`data/release_calendar/release_calendar.csv`, built by `scripts/build_release_calendar.py`: the first-release date, or the next trading day for releases after the 16:00 ET close; pre-vintage rows at the max lag excluding shutdown windows) is after the close that opens the return window; any breaching period FAILs. The registry floor checks above also stay in force (grids start at the p90 floor, truncate only). A pair whose registry `alignment` is `pit_asof` passes the count only with a real `scripts/_pit_align.pit_shift` call driven by the traded lead-loop variable (as-of alignment: latest reading released before the window opens), which has zero breaches by construction. Design: `_pws/lead-lesandro/pkg12_pit_release/DESIGN.md`.
- **Existing gates still apply:** GATE-VIZ-LEAD (coherence), GATE-CONSISTENCY (single-source winner), ECON-SR1 reconcile.

## Rollout

1. Daily Class-A pairs (`gold_copper_xli`, `hy_ig_spy`, `vix_vix3m_spy`, `phlxsox_spy`) rebuilt on the daily axis under this standard, `hy_ig` first as the pilot.
2. `umcsent_xlv` conformed: remove the Option-C selection cap, select freely on full L0–12 (winner is unchanged — L6 is already the global max), reframe the narrative from "capped" to "full-grid winner; 2–5mo window is reference the math confirmed."
3. Re-validate the existing monthly pairs against this standard (tracked follow-up issue).
4. **#255 (Alex_UK) — derived-floor re-validation.** Apply the Step 2 temporal-ordering floor (amended 2026-10-06) to every remaining pair: record each source's publication lag and derived floor, and **re-run the tournament wherever the grid currently admits a below-floor (look-ahead) lead** (the math re-selects the winner on the floored full grid; ECON-T5 DATE_TAG bump on any change). Market-data pairs already at the L0 floor need no re-run. The landing "Data Timing" tab reflects each pair's derived floor and live status.

## Change log

- **2026-10-16 — point-in-time release calendar + per-period gate (pkg12 Phase A, design only).** Per-series, per-period first-release calendar; shared as-of helper `scripts/_pit_align.py`; `gate_lead_floor.py --mode per-period` (default) counts breaching periods instead of relying on the p90 floor. Floors, grids and published winners unchanged; no pair rerun.
- **2026-10-16 — strict floor (stakeholder-approved).** Step 2 restated on the effective lag `E = L + position_shift`, with the rule "the reading for M may only drive a position whose return window starts after the reading is public". The derived-floor table contradicted the principle (it listed mid-M+1 releases at L1, late-M+1/M+2 releases at L2, and ECI / credit-card delinquency at L1 quarters, each one period too low). Rebuilt as release-lag bands from ALFRED first-vintage dates (2018-2026) and publisher calendars; ISM moves to E2 by stakeholder choice (1-3 d lookahead at E1); USGS cement to E5. "Applying the floor" now distinguishes new pairs (translate the grid) from existing frozen grids (truncate the bottom, never extend the top; protocol D2). `gate_lead_floor.py` enforces the effective-lag floor on every grid lead and the winner. Evidence: `_pws/lead-lesandro/pkg9_strict_floor/`.
- 2026-10-06 — Step 2 floor derived per source from the release calendar (no blanket L1 default); grids shifted by the floor (#255).
- 2026-07-14 — standard adopted.
