# pkg12 — Point-in-time impact scan (read-only)

Econ Evan, 2026-10-16. Re-run 2026-10-17 after the QA fixes and Lead decisions:
- fallback = max lag excluding shutdown windows (Q1);
- after-close releases count from the next trading day (Q3);
- verified publisher dates;
- cement 2023-11 data hole now a fallback row (MED-4);
- NEWORDER / DRCCLACBN / DRTSCILM.

Produced by `src/impact_scan.py`, with per-pair data in `IMPACT.csv` and every breaching winner period in `IMPACT_breaches.csv`. Nothing was rerun and no published result changed. Winner rules are left as each pair publishes them, and D9 is not applied.

## Bottom line

- **16 of 35 live pairs are clean.** No backtest period breaches at any searched lead, so as-of alignment gives bit-identical tournaments and there is no rerun on timing grounds: busloans, cc_delinquency, eci, hy_ig, import_price, ism_mfg, ism_services, m2sl, mfg_new_orders, petrol, phlxsox, sloos, t10y3m_rebuilt, unrate, vix_vix3m, wells_fargo. import_price is clean under the default fallback: IR's non-shutdown max lag is 19 d. D8 (below) still applies to these pairs.
- **5 published winners breach.** The table gives their as-of Sharpe, with positions recomputed for the winner only. Every number is shown under both fallbacks: default (shutdown-excluded) / harsh (shutdown-inclusive).

| Pair | Winner (L+shift) | Breaching periods: total (measured / sibling / fallback) | IS Sharpe published → as-of (default / harsh) | OOS Sharpe published → as-of (default / harsh) | B&H OOS | Objective; top-2 margin | Winner likely to change? |
|---|---|---|---|---|---|---|---|
| gold_copper_xli | L0+0 (daily) | all 6,782 rows (same bar) | 1.009 → 0.491 / 0.491 (pre-OOS) | **1.273 → 0.430 / 0.430** | 0.656 | OOS; 0.018 | **Yes.** Known pkg4 L0 lookahead |
| nhs_spy | L0+0 | 400 (181 / 142 / 77) | 0.808 → 0.726 / 0.712 | **1.485 → 0.930 / 0.930** | 0.894 | OOS; 0.024 | **Yes.** Known L0 legacy |
| nhs_saar_spy | L2+0 | 100 (20 / 0 / 80) | **0.278 → 0.220 / 0.372** | **1.450 → 1.328 / 1.328** | 0.991 | OOS; **0.003** | **Likely** (OOS drop is 40× the margin) |
| consumer_sentiment_spy | L1+0 | 108 (40 / 0 / 68) | 0.881 → 0.872 / 0.872 | 0.184 → 0.160 / 0.160 | 0.954 | IS; 0.023 | Unlikely on its own number (−0.009 < margin); the L1 runners-up also move |
| housing_starts_spy | L2+0 | 12 (12 / 0 / 0) | 0.456 → 0.488 / 0.488 | 1.373 → 1.379 / 1.379 | 0.908 | OOS; 0.030 | Unlikely (+0.006) |

**Materially affected by magnitude:** gold_copper, nhs_spy and nhs_saar_spy (QA's reading, confirmed). consumer_sentiment and housing_starts_spy move by ≤ 0.03.

**The fallback choice matters for one winner number.** nhs_saar_spy IS is 0.220 under the default fallback and 0.372 under the harsh one. Every other winner number is identical under both fallbacks, and every OOS number is identical. The previous version's claim that the sensitivity "changes none of the winner numbers" was false (QA MED-6) and has been removed.

**Cement is no longer in the list.** Its only winner breach was the 2023-11 S3 hole, which is now a flagged fallback row (MED-4). Its winner L8 is clean.

**UMCSENT dates (MED-5).** ALFRED's first-vintage dates for UMCSENT agree with UMich's own final-release dates on 28 of 29 months checked against press/news archives (`data/release_calendar/publisher_release_dates.csv`, 2006–2025). The exception is 2018-03: ALFRED shows 2018-04-27, but UMich released it on 2018-03-29. That month is now `publisher_verified` and is excluded from the fallback statistic. The 40 measured consumer_sentiment breaches are therefore genuine finals released 1–4 days after month-end, e.g. March 2016 on 2016-04-01. The 68 fallback breaches cover 1993-01 → 1998-07, before UMCSENT has ALFRED vintages. They are dated at period end + 4 d, the non-shutdown max, so they assume early finals were never later than recent ones. That is an assumption, not a measurement.

The published Sharpe columns reproduce the committed `strategy_returns` exactly: every published OOS Sharpe, and the IS Sharpe wherever one is published.

- **13 pairs breach only at non-winner grid leads.** Their winners are clean, but the tournament scored the breaching leads with some unreleased readings. Only a rerun shows whether an as-of-corrected breaching lead overtakes the winner. Counts are over backtest rows: m = measured (ALFRED / USGS / publisher-verified), s = sibling, r = rule, f = fallback. The harsh column is the shutdown-inclusive sensitivity.

| Pair | Searched-grid breaches (default) | Harsh fallback | Driven by |
|---|---|---|---|
| housing_starts_rebuilt_spy | L2:12 L3:4 L4:1 (all m) | same | 1995-96, 2013, 2018-19, 2025-26 shutdowns |
| permit_yoy_spy | L2:5 (m3/s2) | same | same |
| permit_spy (no strategy_returns CSV: trade-log range, WARN) | L1+1:7 L2+1:1 | same | same |
| nhs_rebuilt_spy | L2:100 (m12/s9/f79) L3:6 L4:1 | L2:100 L3:86 L4:82 | HSN1F pre-1999-07 fallback (37 d default, 105 d harsh) plus shutdowns |
| nhs_saar_rebuilt_spy | L2:101 (m21/f80) L3:6 L4:1 | L2:101 L3:87 L4:83 | same |
| cass_freight_spy | L2:156 (m4/f152) | L2:250 | Cass pre-2013-06 fallback (31 d default, 49 d harsh) |
| rsxfs_spy | L2:9 (all m) | L2:112 | measured shutdown months; the harsh fallback adds 103 |
| retail_inv_sales_spy | L3:3 (all m) | L3:51 | same pattern |
| umcsent_spy | L1:108 (m40/f68) | same | UMich finals 1-4 d after month-end (see MED-5 above) |
| indpro_spy / indpro_xlp | L0+1:432/336, L1+1:2, L2+1:1 (m) | same | legacy grid incl. L0 with shift 1 (E1), plus the 2025 shutdown |
| t10y3m_spy | L0+1:395 (r) | same | legacy L0 with shift 1 = E1 on a next-day series |
| umcsent_xlv | L0+1:39 (m) | same | stale second grid 0..12 in the code |
| cement_spy (grid) | L5:196 (f) | same | **Fallback only**: pre-2021-09 rows at 126 d default (165 d harsh); conditional on Q1 |

## Which pairs need a full rerun (timing)

- **Rerun, winner affected:** gold_copper_xli, nhs_spy, nhs_saar_spy, consumer_sentiment_spy, housing_starts_spy. gold_copper, nhs_spy, nhs_saar_spy and housing_starts_spy are legacy / pkg4 pairs with rebuilt siblings.
- **Rerun, grid-only breaches on dated releases:** housing_starts_rebuilt, permit_yoy, permit_spy, nhs_rebuilt, nhs_saar_rebuilt, cass_freight, rsxfs, retail_inv_sales, umcsent_spy, indpro_spy, indpro_xlp, t10y3m_spy, umcsent_xlv.
- **Conditional on the fallback (fallback-only breaches):** cement_spy (L5).
- **Not on timing grounds:** the 16 clean pairs above. Under D8 track (b), reruns are needed anyway (section below).
- **Rerun item, pre-existing:** unrate_spy and nhs_saar_spy drop the 2025-10 row before shifting. That creates a two-month return row and a lead one month longer across the gap. Reindex to the full period index in the rerun.

## Method and caveats

- **Breach:** the fixed lag at return row t uses reading t−E, where E = L + the code-detected position shift, and that reading's `available_date` is after the close that opens row t's window. Rows are the pipeline's own `strategy_returns` rows.
- **As-of positions without a rerun:** the committed traded position at row t−(k_t−E). This is exact for stateless rules (signal and rolling threshold lagged together). It is not exact for path-dependent sizing, or for HMM winners whose committed positions themselves leak (nhs_spy, eci).
- **Not measurable:**
  - permit_spy has no strategy_returns CSV, so breaches are counted on its trade-log range and there is no Sharpe.
  - ISM, NAHB and EIA outside the 381 verified dates are rule outputs. The rules are tightened so that no verified date is later than the rule date; the only exceptions are EIA 2012-11 (Hurricane Sandy) and 2018-12 (national day of mourning), and both are overridden by their verified dates.
  - Fallback rows are assumptions by construction.
- **Selection objective:** 14 pairs are IS-selected and 21 OOS-selected as published. The Lead's Q4 decision moves Phase B reruns to IS argmax on the common IS start; nothing is re-selected here.
- The **runner-up margin** is only a heuristic. Every breaching combo moves too.

## D8 — revised values paired with first-release timing

*Re-run 2026-10-17 (QA2 M-1): the real-time track no longer sees an after-close vintage on its posting date. BUSLOANS (H.8, 16:15 ET) moves from 0.98 to 1.00 OOS; M2SL (H.6 at 16:30 ET until the monthly 13:00 ET release from 2021-02-23) is unchanged. No other pair is after-close.*

**Flag.** Every macro pair's published winner uses **revised (near-latest-vintage) values with first-release timing**. That is 29 of 35 pairs; only the 6 market-data pairs are exempt (gold_copper, vix_vix3m, phlxsox, t10y3m, t10y3m_rebuilt, and hy_ig, whose ICE OAS revisions cannot be measured). Sources and vintages are in DESIGN §8 and `VINTAGE_SOURCE.csv`.

**Quantified where feasible** (`src/vintage_gap.py` → `VINTAGE_GAP.csv`; read-only, winner only). A pair counts as feasible when:
- it has an ALFRED series,
- a committed `strategy_returns` file exists, and
- a re-implementation of the winner rule on the pipeline's own panel matches the committed positions on ≥ 98% of post-warm-up rows. It matched 100% for 16 pairs and 98.5% for mfg_new_orders.

The comparison is decomposed so that each step is a single change:
- **Ĉ:** the replicated committed rule.
- **N:** the panel's own values, each reading used only once it is in the ALFRED vintage at the window open (timing only).
- **R:** values and timing exactly as known at the window open (track b).
- **F:** first prints on the first-release calendar (track a).

N − Ĉ is zero wherever the per-period gate found no breach. The exceptions are consumer_sentiment (its known L1 breaches) and unrate, where the pipeline dropped the 2025-10 row (row lead vs calendar lead), so N reproduces the timing scan independently. **R − N is the pure revision effect.** Sharpe is measured on the rows where real time is defined (window opens on/after the first vintage, after warm-up), split by the published IS/OOS dates.

| Pair | Series | R window (IS/OOS rows) | R vs N positions agree | IS Sharpe Ĉ → R (revision) | OOS Sharpe Ĉ → R (revision) | Track F IS / OOS | Objective; top-2 margin |
|---|---|---|---|---|---|---|---|
| busloans_spy | BUSLOANS | 1998-08..2026-05 (234/100) | 88% | 0.20 → 0.10 (-0.10) | **1.50 → 1.00 (-0.50)** | 0.36 / 0.54 | OOS; 0.023 |
| m2sl_yoy_spy | M2SL | 1998-04..2026-04 (237/100) | 88% | 0.22 → 0.22 (0.00) | **1.69 → 1.22 (−0.47)** | 0.16 / 1.08 | OOS; 0.036 |
| indpro_spy | INDPRO | 1995-06..2025-12 (271/96) | 87% | 0.67 → 0.56 (−0.10) | **1.23 → 1.02 (−0.21)** | 0.48 / 0.47 | OOS; 0.000 |
| indpro_xlp | INDPRO | 2004-01..2025-12 (180/84) | 86% | **0.96 → 0.60 (−0.36)** | 1.33 → 1.33 (0.00) | 0.71 / 0.81 | OOS; 0.090 |
| unrate_spy | UNRATE | 1998-05..2026-09 (205/115) | 90% | **0.93 → 0.62 (−0.31)** | 0.79 → 0.81 (+0.08; timing −0.06) | 0.64 / 0.76 | **IS; 0.025** |
| mfg_new_orders_spy | NEWORDER | 2000-06..2025-08 (192/104) | 91% | 0.81 → 0.67 (−0.14) | 0.37 → 0.54 (+0.17) | 0.38 / 0.70 | IS; 0.048 |
| retail_inv_sales_spy | RETAILIRSA | 2013-07..2025-07 (47/98) | 90% | 1.36 → 1.26 (−0.10) | 0.73 → 1.04 (+0.31) | 1.26 / 0.86 | IS; 0.144 |
| nhs_saar_rebuilt_spy | HSN1F | 1999-08..2026-08 (204/116) | 94% | 0.98 → 1.00 (+0.02) | 0.92 → 0.81 (−0.11) | 0.68 / 0.89 | IS; 0.013 |
| rsxfs_spy | RSXFS | 2001-07..2026-09 (186/117) | 96% | 0.90 → 0.94 (+0.04) | 0.73 → 0.84 (+0.12) | 0.79 / 0.74 | IS; 0.045 |
| housing_starts_rebuilt_spy | HOUST | 1998-10..2026-08 (234/101) | 98% | 0.19 → 0.12 (−0.07) | 1.45 → 1.48 (+0.03) | 0.10 / 1.05 | OOS; 0.000 |
| permit_yoy_spy | PERMIT | 1999-09..2025-08 (214/98) | 98% | 0.93 → 0.89 (−0.04) | 0.20 → 0.14 (−0.06) | 1.01 / 0.19 | **IS; 0.010** |
| consumer_sentiment_spy | UMCSENT | 1998-08..2026-08 (236/101) | 100% | 0.83 → 0.82 (timing −0.01) | 0.18 → 0.16 (timing −0.02) | 0.82 / 0.16 | IS; 0.023 |
| cass_freight_spy, cc_delinquency_spy, nhs_rebuilt_spy, sloos_ci_small_spy, umcsent_xlv | Cass, DRCCLACBN, HSN1FNSA, DRTSCILM, UMCSENT | from 2011-13 (Cass, cc, nhs_rebuilt, sloos) or 2004 (umcsent_xlv) | 100% | no change | no change | = | — |

**Reading.**
- **Revisions matter more than release timing.** For 11 of 17 quantified winners, real-time vintages flip 2-14% of positions and move Sharpe by 0.04-0.50, versus ≤ 0.03 for timing alone on the same pairs (0.06 for unrate, which is the dropped-row artifact).
- **The largest hits are OOS-selected winners.** busloans OOS −0.50 (margin 0.023) and m2sl −0.47 (0.036): their published OOS edge over B&H (0.89-0.90) shrinks to about +0.11 for busloans and +0.32 for m2sl. indpro_spy is −0.21 with a zero margin (a tie).
- **IS-selected winners:** unrate IS −0.31 against a 0.025 margin, so the winner is very likely to change under track (b). mfg_new_orders −0.14 (0.048) and permit_yoy −0.04 (0.010) are at risk. retail, rsxfs and nhs_saar_rebuilt move by less than their margins or upward.
- **Not uniformly downward.** retail OOS +0.31, mfg OOS +0.17 and rsxfs +0.12 gain. These are signal-noise strategies, and revisions re-shuffle which months are flagged.
- **Track (a), first prints, is not a safe default.** It is often the worst of the three (busloans OOS 0.54, indpro_spy 0.47) because yoy and threshold windows built from first prints mix vintages. That supports track (b).

**Not quantified (flagged, revised values):**
- No ALFRED archive for the source: ism_mfg, ism_services, wells_fargo_housing, umcsent_spy, cement, petrol_inv.
- HMM-based winners whose state model would itself need real-time refits: eci_total_comp, nhs_spy.
- No committed panel or strategy_returns locally: housing_starts_spy, nhs_saar_spy, permit_spy.
- Rule replication only 96.6%, below the 98% bar: import_price_spy.

**Rerun consequence.** If D8 adopts track (b), every quantified pair with a non-zero revision effect needs a full rerun: busloans, m2sl, indpro_spy, indpro_xlp, unrate, mfg_new_orders, retail_inv_sales, nhs_saar_rebuilt, rsxfs, housing_starts_rebuilt, permit_yoy. So do all unquantified macro pairs, because threshold and transform inputs change for every candidate, not only the winner. The pairs with no change here are only unchanged at the winner and on the real-time window.

**Caveats.**
- Real time is only defined from each series' first ALFRED vintage, so for IR, RETAILIRSA, Cass, DRCCLACBN, DRTSCILM and HSN1FNSA the IS window is partial or short (24-82 rows).
- The rule replication is a re-implementation and was validated on positions, not on the pipelines' code.
- The ALFRED dates are FRED posting dates.
- The real-time track uses calendar-month leads. It differs from the pipelines' row leads only around unrate's dropped 2025-10 row, and `_pit_align.realtime_apply` matched the scan's positions on unrate on every row but that one.
