# pkg12 — Point-in-time impact scan (read-only)

Econ Evan, 2026-10-16. Produced by `src/impact_scan.py`; per-pair data in `IMPACT.csv`, every breaching winner period in `IMPACT_breaches.csv`. No pipeline was rerun and no published file was changed. Winner-selection rules are left exactly as each pair publishes them, and D9 (lead plateau) is not applied.

## Bottom line

- **15 of 35 live pairs are clean.** No period breaches at any searched lead, so as-of alignment gives bit-identical tournaments and no rerun is needed: busloans, cc_delinquency, eci, hy_ig, ism_mfg, ism_services, m2sl, mfg_new_orders, petrol, phlxsox, sloos, t10y3m_rebuilt, unrate, vix_vix3m, wells_fargo.
- **6 published winners breach.** Their as-of Sharpe, with positions recomputed for the winner only:

| Pair | Winner (L+shift) | Breaching periods (measured / fallback / other) | IS Sharpe (published → as-of) | OOS Sharpe (published → as-of) | B&H OOS | Objective; top-2 margin | Winner likely to change? |
|---|---|---|---|---|---|---|---|
| gold_copper_xli | L0+0 (daily) | all 6,782 rows (same bar) | 1.009 → 0.491 (pre-OOS) | **1.273 → 0.430** | 0.656 | OOS; 0.018 | **Yes.** Known pkg4 L0 lookahead |
| nhs_spy | L0+0 | 400 (181 / 77 / 142 sibling) | 0.808 → 0.712 | **1.485 → 0.930** | 0.894 | OOS; 0.024 | **Yes.** Known L0 legacy |
| nhs_saar_spy | L2+0 | 100 (20 / 80) | 0.278 → 0.372 | **1.450 → 1.328** | 0.991 | OOS; **0.003** | **Likely** (the drop is 40× the margin) |
| consumer_sentiment_spy | L1+0 | 109 (41 / 68) | 0.881 → 0.872 | 0.184 → 0.160 | 0.954 | IS; 0.023 | Unlikely on its own number (−0.008 < margin); runners-up at L1 also move |
| housing_starts_spy | L2+0 | 12 (12 / 0) | 0.456 → 0.488 | 1.373 → 1.379 | 0.908 | OOS; 0.030 | Unlikely (+0.006) |
| cement_spy | L8+0 | 1 (cement 2023-11: no USGS file date measurable) | 1.632 → 1.632 | 0.580 → 0.580 | 0.935 | IS; 0.163 | No (no position changes) |

The "published" columns reproduce the committed `strategy_returns` exactly: every published OOS Sharpe, and every published IS Sharpe where one exists. The fallback sensitivity (max lag excluding shutdown windows) changes none of the six winner numbers.

- **14 pairs breach only at non-winner grid leads.** Their winners are clean, but the tournament scored the breaching leads with some unreleased readings. Only a rerun shows whether an as-of-corrected breaching lead overtakes the winner. Counts below are per lead, over the backtest rows: m = measured (ALFRED / USGS), s = sibling, r = rule, f = fallback.

| Pair | Searched-grid breaches | Driven by |
|---|---|---|
| housing_starts_rebuilt_spy | L2:12 L3:4 L4:1 (all m) | 1995-96, 2013, 2018-19, 2025-26 shutdowns |
| permit_yoy_spy | L2:5 (m3/s2) | same |
| permit_spy (no strategy_returns CSV) | L1+1:7 L2+1:1 | same |
| nhs_rebuilt_spy / nhs_saar_rebuilt_spy | L2:100/101 L3:86/87 L4:82/83 (m12-21, rest f) | HSN1F pre-1999 fallback (105 d); measured: shutdowns and 1999-2001 late prints |
| rsxfs_spy | L2:112 (m9/f103) | RSXFS pre-2001-06 fallback (56 d) |
| retail_inv_sales_spy | L3:51 (m3/f48) | RETAILIRSA pre-1996-10 fallback (86 d) |
| cass_freight_spy | L2:250 (m4/f246) | Cass pre-2013-06 fallback (49 d) |
| umcsent_spy | L1:109 (m41/f68) L2:1 (f) | UMCSENT first vintages 1-4 d after month-end (1998-2008; 2018-03 +27 d) |
| indpro_spy / indpro_xlp | L0+1:432/336 L1+1:2 L2+1:1 (m) | legacy grid incl. L0 with shift 1 = E1; 2025 shutdown |
| t10y3m_spy | L0+1:395 (r) | legacy L0 with shift 1 = E1 on a next-day series |
| umcsent_xlv | L0+1:40 (m) | stale second grid 0..12 in code |
| import_price_spy | L2:208 L3:209 (all f) | **Fallback only** (IR has no vintages before 2010-03); clean with any fallback ≤ 28 d (the non-shutdown max is 19 d) |
| cement_spy (grid) | L5:196 L6:197 (f), L7-L14: the 1 unmeasured month | **Fallback only** (pre-2021-09 at 165 d) |

## Which pairs need a full rerun

- **Rerun, winner affected:** gold_copper_xli, nhs_spy, nhs_saar_spy, consumer_sentiment_spy, housing_starts_spy. Of these, gold_copper, nhs_spy, nhs_saar_spy and housing_starts_spy are legacy or pkg4 pairs already slated for retirement or rebuild, and their rebuilt siblings exist (nhs_saar_rebuilt, housing_starts_rebuilt).
- **Rerun, grid-only breaches on dated releases:** housing_starts_rebuilt, permit_yoy, permit_spy, nhs_rebuilt, nhs_saar_rebuilt, rsxfs, retail_inv_sales, cass_freight, umcsent_spy, indpro_spy, indpro_xlp, t10y3m_spy, umcsent_xlv. For the last four, part of the breach is the legacy sub-floor grid already flagged by the floor gate.
- **Conditional on the fallback decision (Q1):** import_price_spy and cement_spy. They are clean under any non-shutdown fallback for IR; cement L5 still breaches at 126 d.
- **No rerun on timing grounds:** the 15 clean pairs above. D8 below still applies to them. mfg_new_orders is clean once it is timed on the series its panel actually holds (NEWORDER, advance durable-goods report, median 26 d), not AMTMNO.

Expected size: the monthly breaches are a few shutdown months in a 30-year sample, plus pre-vintage fallback rows. For the winners measured here, the as-of effect is ≤ 0.01 Sharpe whenever the breach is a handful of measured periods (housing_starts, consumer_sentiment). It is large only when the lag is structural (L0 same-bar: gold_copper, nhs_spy) or concentrated (nhs_saar_spy, with 80 fallback periods).

## Method and caveats

- **Breach:** the fixed lag at return row t uses reading t−E, where E = L + the code-detected position shift, and that reading's first release is after the close that opens row t's window. Rows are the pipeline's own `strategy_returns` rows. `unrate_spy` and `nhs_saar_spy` drop the 2025-10 row, which removes the never-published reading from their own index (see DESIGN §3).
- **As-of positions without a rerun:** committed traded position at row t−(k_t−E), where k_t comes from `_pit_align.asof_lags`. This is exact for stateless rules whose inputs at a row use data up to that row (signal and rolling threshold lagged together). It is not exact for path-dependent sizing (none among these winners as far as I can see), or where the committed positions themselves leak (the HMM smoothed-probability lookahead in nhs_spy and eci is out of scope here).
- **Not measurable:** permit_spy has no strategy_returns CSV, so its breaches are counted on the trade-log date range and there is no Sharpe. The cement 2023-11 publication date is missing (S3 403). UMCSENT ALFRED dates are FRED posting dates (upper bound). ISM, NAHB and EIA dates are calendar rules.
- **Selection objective:** 14 pairs are IS-selected and 21 OOS-selected as currently published (`selection.objective` in winner_summary). The brief says "argmax IS Sharpe"; I used each pair's own published objective for the margin column and did not re-select anything.
- The **runner-up margin** is only a heuristic. Every breaching combo moves too, so "winner changes" is a judgement, not a measurement, until the rerun.

## D8 — revised values paired with first-release timing

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
| busloans_spy | BUSLOANS | 1998-08..2026-05 (234/100) | 89% | 0.20 → 0.11 (−0.09) | **1.50 → 0.98 (−0.52)** | 0.36 / 0.54 | OOS; 0.023 |
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
- **Revisions matter more than release timing.** For 11 of 17 quantified winners, real-time vintages flip 2-14% of positions and move Sharpe by 0.04-0.52, versus ≤ 0.03 for timing alone on the same pairs (0.06 for unrate, which is the dropped-row artifact).
- **The largest hits are OOS-selected winners.** busloans OOS −0.52 (margin 0.023) and m2sl −0.47 (0.036): their published OOS edge over B&H (0.89-0.90) shrinks to about +0.09 for busloans and +0.32 for m2sl. indpro_spy is −0.21 with a zero margin (a tie).
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
