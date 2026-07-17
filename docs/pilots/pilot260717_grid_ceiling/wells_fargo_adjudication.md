# Pilot 260717 — Grid-Ceiling Test, pair 2: wells_fargo_housing_spy

**Question (same as petrol):** does extending the monthly lead grid beyond L12 surface a signal the `L0–12` cap hides? (issue #23)

**Why this pair:** its published winner sits at **L7** — the highest lead among the *reproducible* monthly pairs — so it is the best structural test after indpro_xlp (winner at L11) turned out to be non-reproducible (#26). Housing also has a genuine economic prior for a long lead (~2 years — HMI turned down ~2 yrs before the GFC equity peak), unlike petroleum's slide-53 claim.

## Verdict: the extension surfaced a nominal new max — and adjudication REJECTED it. Winner stays L7.

This is the more instructive of the two ceiling pilots: unlike petrol (a clean null), the extension here **did** produce a new global argmax, and the standard's Step-4 adjudication (ECON-T5) correctly rejected it as a multiple-testing artifact rather than propagating it.

### Step 1 — provenance: PASSES (exact reproduction)
The committed `scripts/pair_pipeline_wells_fargo_housing_spy.py` (`run_lead_grid`, `LEADS = list(range(1, 13))` at line 129) reproduces the live winner **combo-for-combo**: `diff_12m / T2_roll_p25 / P1_long_cash_pro / L7 / LB60`, OOS Sharpe **1.4291**; grid counts match `winner_summary.json` exactly (17,856 rows / 12,980 valid). Contrast the two indpro pairs (#26), which do not reproduce. So this pilot is comparable to the incumbent.

### Step 2 — ceiling extension `L1–12 + {18,24,36}`
Per-lead best valid OOS Sharpe:

| L1 | L2 | L3 | L4 | L5 | L6 | **L7** | L8 | L9 | L10 | L11 | L12 | **L18** | L24 | L36 |
|----|----|----|----|----|----|--------|----|----|-----|-----|-----|---------|-----|-----|
|1.372|1.337|1.332|1.269|1.288|1.422|**1.429**|1.310|1.185|1.277|1.244|1.407|**1.507**|1.290|1.246|

**New global argmax:** `accel / T2_roll_p75 / P1_long_cash_pro / L18 / LB60`, OOS **1.5074** (+0.078 over L7). L24 and L36 are both below L7 — a lone L18 spike, not a rising plateau.

### Adjudication (ECON-T5): rejected on four independent grounds
1. **Exclusion is dispositive.** The result rests entirely on `accel` (`nahb_hmi_accel_pct`), a 2nd-difference of a bounded 0–100 diffusion index — the pipeline's own `BOUNDED_PCT_RISK` flag fires on it (10/15 of the top-15 carry the flag). **Excluding all bounded_pct_risk signals, the best clean combo beyond L12 is 1.3349 — below the L7 incumbent. Nothing clean beats L7 at any long horizon.**
2. **Non-durability.** The winning combo's own lead curve is a lone spike: ~0.87 at valid neighbours L10/L11, and its two nearest scanned horizons L12 (0.27) and L24 (0.20) are **invalid**. A genuine lead is a ridge, not an isolated point (Boudoukh-Richardson-Whitelaw: adjacent overlapping horizons ~99% correlated).
3. **Order-statistic bias.** Naive Sharpe t = 4.31 vs the incumbent's 4.08 — statistically indistinguishable; the +0.078 gap is what argmax over 16,185 valid combos yields under the null. HAC/Newey-West correction for the overlapping lead structure would only lower 4.31.
4. **IS/OOS inversion.** IS 0.4273 → OOS 1.5074: the rule failed in-sample and "worked" out-of-sample — and OOS Sharpe *is* the selection criterion. The signature of fitting OOS noise. The incumbent is consistent across both (0.75 → 1.43).

**Economic prior resolves against the hit:** a real ~2-year housing lead would appear in the clean level/momentum signals — and those do **not** beat L7 at L18. The signal shows up *only* in an artifact-flagged transform. So the prior argues against this specific result, not for it.

## Scope & notes
- Tests the **tradable** long lead (Sharpe). Raw lead-lag predictability (correlation/Granger) at 24–36mo not separately isolated.
- **Scoring gap (fleet-consistency, routed to #15):** this pipeline scores with `dropna` (`run_lead_grid` line 740), not ECON-T4 `fillna`-cash. Harmless here — `oos_n = 98` for every combo at every lead, so no in-window NaN exists to drop and the two are identical — but inconsistent with petrol's fillna. The L18 result is **not** a dropna artifact.
- L36 validity: no starvation (oos_n=98 throughout; 0 combos below the 36-month floor).

## Conclusion for issue #23 (ceiling half)
Two reproducible pairs now tested — petroleum (strongest a-priori long-lead claim; clean null) and wells_fargo (highest reproducible lead + genuine 2-year housing prior; nominal max rejected on adjudication). **Neither yields a durable, clean signal beyond L12. The L0–12 ceiling holds under proper adjudication.** The grid-*shape* question (dense contiguous vs sparse anchored — the other half of #23) remains untested.

## Reproduce
One-line change to the committed pipeline, then re-score in isolation (the ECON-T5 §4 immutability guard forbids overwriting the frozen production tournament in place):
```python
# scripts/pair_pipeline_wells_fargo_housing_spy.py:129
LEADS = list(range(1, 13)) + [18, 24, 36]
```
Extended leaderboard: `wells_fargo_tournament_L1-36_pilot260717.csv` (22,320 strategy rows).
