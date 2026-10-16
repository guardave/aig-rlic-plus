# pkg12 — Point-in-time impact scan (read-only)

Econ Evan, 2026-10-16. Produced by `src/impact_scan.py`; per-pair data in `IMPACT.csv`, every breaching winner period in `IMPACT_breaches.csv`. No pipeline was rerun and no published file was changed. Winner-selection rules are left exactly as each pair publishes them, and D9 (lead plateau) is not applied.

## Bottom line

- **14 of 35 live pairs are clean.** No period breaches at any searched lead, so as-of alignment gives bit-identical tournaments and no rerun is needed: busloans, cc_delinquency, eci, hy_ig, ism_mfg, ism_services, m2sl, petrol, phlxsox, sloos, t10y3m_rebuilt, unrate, vix_vix3m, wells_fargo.
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

- **15 pairs breach only at non-winner grid leads.** Their winners are clean, but the tournament scored the breaching leads with some unreleased readings. Only a rerun shows whether an as-of-corrected breaching lead overtakes the winner. Counts below are per lead, over the backtest rows: m = measured (ALFRED / USGS), s = sibling, r = rule, f = fallback.

| Pair | Searched-grid breaches | Driven by |
|---|---|---|
| housing_starts_rebuilt_spy | L2:12 L3:4 L4:1 (all m) | 1995-96, 2013, 2018-19, 2025-26 shutdowns |
| permit_yoy_spy | L2:5 (m3/s2) | same |
| permit_spy (no strategy_returns CSV) | L1+1:7 L2+1:1 | same |
| nhs_rebuilt_spy / nhs_saar_rebuilt_spy | L2:100/101 L3:86/87 L4:82/83 (m12-21, rest f) | HSN1F pre-1999 fallback (105 d); measured: shutdowns and 1999-2001 late prints |
| rsxfs_spy | L2:112 (m9/f103) | RSXFS pre-2001-06 fallback (56 d) |
| retail_inv_sales_spy | L3:51 (m3/f48) | RETAILIRSA pre-1996-10 fallback (86 d) |
| mfg_new_orders_spy | L3:226 (m3/f223) | AMTMNO pre-2011-05 fallback (79 d) |
| cass_freight_spy | L2:250 (m4/f246) | Cass pre-2013-06 fallback (49 d) |
| umcsent_spy | L1:109 (m41/f68) L2:1 (f) | UMCSENT first vintages 1-4 d after month-end (1998-2008; 2018-03 +27 d) |
| indpro_spy / indpro_xlp | L0+1:432/336 L1+1:2 L2+1:1 (m) | legacy grid incl. L0 with shift 1 = E1; 2025 shutdown |
| t10y3m_spy | L0+1:395 (r) | legacy L0 with shift 1 = E1 on a next-day series |
| umcsent_xlv | L0+1:40 (m) | stale second grid 0..12 in code |
| import_price_spy | L2:208 L3:209 (all f) | **Fallback only** (IR has no vintages before 2010-03); clean with any fallback ≤ 28 d (the non-shutdown max is 19 d) |
| cement_spy (grid) | L5:196 L6:197 (f), L7-L14: the 1 unmeasured month | **Fallback only** (pre-2021-09 at 165 d) |

## Which pairs need a full rerun

- **Rerun, winner affected:** gold_copper_xli, nhs_spy, nhs_saar_spy, consumer_sentiment_spy, housing_starts_spy. Of these, gold_copper, nhs_spy, nhs_saar_spy and housing_starts_spy are legacy or pkg4 pairs already slated for retirement or rebuild, and their rebuilt siblings exist (nhs_saar_rebuilt, housing_starts_rebuilt).
- **Rerun, grid-only breaches on dated releases:** housing_starts_rebuilt, permit_yoy, permit_spy, nhs_rebuilt, nhs_saar_rebuilt, rsxfs, retail_inv_sales, mfg_new_orders, cass_freight, umcsent_spy, indpro_spy, indpro_xlp, t10y3m_spy, umcsent_xlv. For the last four, part of the breach is the legacy sub-floor grid already flagged by the floor gate.
- **Conditional on the fallback decision (Q1):** import_price_spy and cement_spy. They are clean under any non-shutdown fallback for IR; cement L5 still breaches at 126 d.
- **No rerun:** the 14 clean pairs above.

Expected size: the monthly breaches are a few shutdown months in a 30-year sample, plus pre-vintage fallback rows. For the winners measured here, the as-of effect is ≤ 0.01 Sharpe whenever the breach is a handful of measured periods (housing_starts, consumer_sentiment). It is large only when the lag is structural (L0 same-bar: gold_copper, nhs_spy) or concentrated (nhs_saar_spy, with 80 fallback periods).

## Method and caveats

- **Breach:** the fixed lag at return row t uses reading t−E, where E = L + the code-detected position shift, and that reading's first release is after the close that opens row t's window. Rows are the pipeline's own `strategy_returns` rows. `unrate_spy` and `nhs_saar_spy` drop the 2025-10 row, which removes the never-published reading from their own index (see DESIGN §3).
- **As-of positions without a rerun:** committed traded position at row t−(k_t−E), where k_t comes from `_pit_align.asof_lags`. This is exact for stateless rules whose inputs at a row use data up to that row (signal and rolling threshold lagged together). It is not exact for path-dependent sizing (none among these winners as far as I can see), or where the committed positions themselves leak (the HMM smoothed-probability lookahead in nhs_spy and eci is out of scope here).
- **Not measurable:** permit_spy has no strategy_returns CSV, so its breaches are counted on the trade-log date range and there is no Sharpe. The cement 2023-11 publication date is missing (S3 403). UMCSENT ALFRED dates are FRED posting dates (upper bound). ISM, NAHB and EIA dates are calendar rules.
- **Selection objective:** 14 pairs are IS-selected and 21 OOS-selected as currently published (`selection.objective` in winner_summary). The brief says "argmax IS Sharpe"; I used each pair's own published objective for the margin column and did not re-select anything.
- The **runner-up margin** is only a heuristic. Every breaching combo moves too, so "winner changes" is a judgement, not a measurement, until the rerun.
