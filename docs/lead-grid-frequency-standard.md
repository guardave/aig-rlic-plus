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

**Principle.** At lead `L` (in the signal's native period), the position held during period `t` uses the reading for reference period `t−L`. That reading is finalised at the end of `t−L` and *published* a lag `Δ` later. The position must be set at the **decision point** — the start of period `t` (= end of `t−1`). The floor is the **smallest `L` such that the publication date of reference period `t−L` falls on or before that decision point**, so the signal is genuinely in hand before the position is taken:

> floor = smallest `L` with `release_date(t−L) ≤ start_of(t)`

Equivalently: the number of whole rebalance periods between a reference period-end and the first period-*start* at which that reading is public. `L0` is still computed and shown, but flagged *coincident / lookahead* whenever the floor is `> L0`.

**Derived floors (monthly-rebalanced pairs), from the official release calendars:**

| Release timing (reference month M) | Derived floor | Sources (examples) |
|---|---|---|
| Real-time market data, observed at close (no publication lag) | **L0** (same-day; state the intraday-availability assumption) | gold/copper, VIX term structure, SOX/SPY |
| Vendor/FRED daily series with a 1-day posting lag | **L1 (days)** | HY-IG & Treasury spreads (ICE BofA / FRED daily) |
| Released **early–mid of month M+1** (≤ ~3 weeks after month-end) | **L1** | ISM (M+1 business day 1–3), BLS import price / IP / retail sales (~mid M+1), employment (1st Fri M+1), permits/starts (~17th), M2, Cass, C&I loans; sentiment surveys released in-month (UMich, NAHB) also floor **L1** (L0 would use an unreleased or mid-month reading) |
| Released **late in M+1 or in M+2** (~5–8 weeks after month-end) | **L2** | Census factory orders / M3 (~5 wk), retail inventories / MTIS (~6 wk), USGS cement (~6–8 wk), new home sales (~end M+1) |
| Weekly data carried to month-end, available within the month | **L0** (documented; e.g. petroleum stocks, days-since-release 0–6) | EIA petroleum inventory |

**Quarterly pairs** apply the same principle on the quarterly calendar: a series released ~1 month after quarter-end (ECI) or in the following quarter (SLOOS, credit-card delinquency) floors at **L1 (quarters)**.

Each pair's source, publication lag, and derived floor are recorded with their release-calendar justification (see "Enforcement" and `docs/data-series-catalog.md`); the floor is auditable, never chosen ad hoc.

**Applying the floor: SHIFT the whole grid, do not truncate it.** The floor is a data-availability *translation* of the entire anchored grid (Step 3), not a deletion of its low points. `lead` conflates two distinct things — the **economic predictive horizon** (how far ahead the signal is tested) and the **publication latency** (when the reading is in hand). The tournament must test the same set of economic horizons `0…H` for every pair; the floor only delays when each becomes executable. So the searched execution-lag grid is the anchored grid **shifted up by the floor**:

> searched grid = `[f, f+1, …, f+H]`  (the anchored `0…H` translated by `f`)

Example (monthly, anchored `L0–12`): floor `L1` → search **`L1–L13`**; floor `L2` → search **`L2–L14`**. The extra one or two months at the top are **publication latency, not economic horizon**: the ~1-year economic-horizon cap (Step 3) is defined on the *pre-shift* horizon and is preserved. The look-ahead short leads below `f` are simply never reachable in real time — they are not "cut", the whole window moves so the economic-horizon count is identical across pairs regardless of floor.

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
- **Existing gates still apply:** GATE-VIZ-LEAD (coherence), GATE-CONSISTENCY (single-source winner), ECON-SR1 reconcile.

## Rollout

1. Daily Class-A pairs (`gold_copper_xli`, `hy_ig_spy`, `vix_vix3m_spy`, `phlxsox_spy`) rebuilt on the daily axis under this standard, `hy_ig` first as the pilot.
2. `umcsent_xlv` conformed: remove the Option-C selection cap, select freely on full L0–12 (winner is unchanged — L6 is already the global max), reframe the narrative from "capped" to "full-grid winner; 2–5mo window is reference the math confirmed."
3. Re-validate the existing monthly pairs against this standard (tracked follow-up issue).
4. **#255 (Alex_UK) — derived-floor re-validation.** Apply the Step 2 temporal-ordering floor (amended 2026-10-06) to every remaining pair: record each source's publication lag and derived floor, and **re-run the tournament wherever the grid currently admits a below-floor (look-ahead) lead** (the math re-selects the winner on the floored full grid; ECON-T5 DATE_TAG bump on any change). Market-data pairs already at the L0 floor need no re-run. The landing "Data Timing" tab reflects each pair's derived floor and live status.
