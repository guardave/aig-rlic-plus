# Q6 — Sample loss from truncating at the first ALFRED vintage (read-only)

**Summary.** 23 pairs have an ALFRED-archived source:
- 9 lose no IS rows; 12 keep at least 90% of IS; 15 keep at least 50%.
- 2 fall below IS eligibility: cass_freight_spy and retail_inv_sales_spy keep 57 and 47 rows, against the 60-month minimum.
- 6 pairs lose the 2001 and 2008-09 recessions from IS entirely: nhs_spy, nhs_rebuilt_spy, eci_total_comp_spy, cc_delinquency_spy, sloos_ci_small_spy and import_price_spy. So do the two ineligible pairs.
- The 6 market-data pairs are unaffected.
- The 6 no-archive pairs (Q7) cannot be truncated, because they have no vintages.

Econ Evan, 2026-10-17. Script: `src/q6_sample_loss.py`. Data: `Q6_SAMPLE_LOSS.csv`. First-vintage dates come from `data/release_calendar/alfred_first_vintage_dates.csv` (FRED `vintagedates` API). Nothing was rerun.

## Method
- **Truncated start:** the first return row whose window opens on or after the first ALFRED vintage. The vintage on that date carries the series' full history, so rolling thresholds need no extra warm-up. IS and OOS ends are unchanged.
- **Current IS:** the published common IS window for the IS-selected pairs. For the others (marked `*`), IS is the `strategy_returns` rows before the published OOS start, because those pairs do not publish an IS window.
- **Eligibility:** IS rows on the truncated common IS window must be at least 60 (monthly) or 20 (quarterly): the protocol's IS eligibility rule (n ≥ 60 monthly / 20 quarterly; not every pipeline encodes it as a constant).
- **Recessions:** NBER recessions 1990-07..1991-03, 2001-03..2001-11, 2007-12..2009-06 and 2020-02..2020-04. A recession counts as lost if it was inside the current IS and the truncated IS no longer contains it, fully or in part.
- **OOS:** OOS rows are unchanged for every pair, because every first vintage precedes 2017.

## Pairs with an ALFRED source (sorted by IS loss)

| Pair | Series | First ALFRED vintage | Current IS (rows) | Truncated IS (rows) | IS lost | Current OOS (rows) | Truncated OOS rows | Eligible after truncation | Recessions dropped from IS |
|---|---|---|---|---|---|---|---|---|---|
| cass_freight_spy | FRGSHPUSM649NCIS | 2013-06-04 | 1993-02-28 → 2018-03-31 (302)* | 2013-07-31 → 2018-03-31 (57) | **81.1%** | 2018-04-30 → 2026-07-31 (100) | 100 | **NO** (<60) | 2001 (fully), 2008-09 (GFC) (fully) |
| retail_inv_sales_spy | RETAILIRSA | 2013-06-13 | 1998-01-31 → 2017-05-31 (233) | 2013-07-31 → 2017-05-31 (47) | **79.8%** | 2017-06-30 → 2025-07-31 (98) | 98 | **NO** (<60) | 2001 (fully), 2008-09 (GFC) (fully) |
| nhs_spy | HSN1FNSA | 2011-05-24 | 1993-02-28 → 2018-01-31 (300)* | 2011-06-30 → 2018-01-31 (80) | **73.3%** | 2018-02-28 → 2026-05-31 (100) | 100 | yes | 2001 (fully), 2008-09 (GFC) (fully) |
| nhs_rebuilt_spy | HSN1FNSA | 2011-05-24 | 1993-02-28 → 2018-03-31 (302)* | 2011-06-30 → 2018-03-31 (82) | **72.8%** | 2018-04-30 → 2026-08-31 (101) | 101 | yes | 2001 (fully), 2008-09 (GFC) (fully) |
| eci_total_comp_spy | ECIALLCIV | 2013-07-31 | 2001-06-30 → 2019-12-31 (75)* | 2013-12-31 → 2019-12-31 (25) | **66.7%** | 2020-03-31 → 2026-03-31 (25) | 25 | yes | 2001 (fully), 2008-09 (GFC) (fully) |
| cc_delinquency_spy | DRCCLACBN | 2011-05-24 | 1999-12-31 → 2017-06-30 (71) | 2011-09-30 → 2017-06-30 (24) | **66.2%** | 2017-09-30 → 2025-06-30 (32) | 32 | yes | 2001 (fully), 2008-09 (GFC) (fully) |
| sloos_ci_small_spy | DRTSCILM | 2010-04-20 | 1999-12-31 → 2017-09-30 (72) | 2010-09-30 → 2017-09-30 (29) | **59.7%** | 2017-12-31 → 2025-09-30 (32) | 32 | yes | 2001 (fully), 2008-09 (GFC) (fully) |
| import_price_spy | IR | 2010-03-16 | 2000-12-31 → 2016-12-31 (193) | 2010-04-30 → 2016-12-31 (81) | **58.0%** | 2017-01-31 → 2025-08-31 (104) | 104 | yes | 2001 (fully), 2008-09 (GFC) (fully) |
| nhs_saar_spy | HSN1F | 1999-07-30 | 1993-01-31 → 2016-12-31 (288)* | 1999-08-31 → 2016-12-31 (209) | **27.4%** | 2017-01-31 → 2026-06-30 (113) | 113 | yes | none |
| permit_spy | PERMIT | 1999-08-17 | 1993-02-28 → 2017-12-31 (299)* | 1999-09-30 → 2017-12-31 (220) | **26.4%** | 2018-01-01 → 2025-12-31 (96) | 96 | yes | none |
| busloans_spy | BUSLOANS | 1996-12-13 | 1993-02-28 → 2018-01-31 (300)* | 1997-01-31 → 2018-01-31 (253) | **15.7%** | 2018-02-28 → 2026-05-31 (100) | 100 | yes | none |
| permit_yoy_spy | PERMIT | 1999-08-17 | 1997-12-31 → 2017-06-30 (235) | 1999-09-30 → 2017-06-30 (214) | **8.9%** | 2017-07-31 → 2025-08-31 (98) | 98 | yes | none |
| rsxfs_spy | RSXFS | 2001-06-13 | 2000-12-31 → 2016-12-31 (193) | 2001-07-31 → 2016-12-31 (186) | **3.6%** | 2017-01-31 → 2026-09-30 (117) | 117 | yes | 2001 (partly) |
| consumer_sentiment_spy | UMCSENT | 1998-07-31 | 1997-12-31 → 2018-03-31 (244) | 1998-08-31 → 2018-03-31 (236) | **3.3%** | 2018-04-30 → 2026-08-31 (101) | 101 | yes | none |
| umcsent_xlv | UMCSENT | 1998-07-31 | 1998-12-31 → 2019-03-31 (244)* | 1998-12-31 → 2019-03-31 (244) | **0.0%** | 2019-04-30 → 2025-12-31 (81) | 81 | yes | none |
| mfg_new_orders_spy | NEWORDER | 1997-03-06 | 2001-01-31 → 2016-12-31 (192) | 2001-01-31 → 2016-12-31 (192) | **0.0%** | 2017-01-31 → 2025-08-31 (104) | 104 | yes | none |
| nhs_saar_rebuilt_spy | HSN1F | 1999-07-30 | 2000-01-31 → 2016-12-31 (204) | 2000-01-31 → 2016-12-31 (204) | **0.0%** | 2017-01-31 → 2026-08-31 (116) | 116 | yes | none |
| m2sl_yoy_spy | M2SL | 1980-02-08 | 1993-02-28 → 2017-12-31 (299)* | 1993-02-28 → 2017-12-31 (299) | **0.0%** | 2018-01-31 → 2026-04-30 (100) | 100 | yes | none |
| indpro_xlp | INDPRO | 1927-01-26 | 1998-01-31 → 2018-12-31 (252)* | 1998-01-31 → 2018-12-31 (252) | **0.0%** | 2019-01-31 → 2025-12-31 (84) | 84 | yes | none |
| indpro_spy | INDPRO | 1927-01-26 | 1990-01-31 → 2017-12-31 (336)* | 1990-01-31 → 2017-12-31 (336) | **0.0%** | 2018-01-01 → 2025-12-31 (96) | 96 | yes | none |
| housing_starts_spy | HOUST | 1960-07-21 | 1993-02-28 → 2018-02-28 (301)* | 1993-02-28 → 2018-02-28 (301) | **0.0%** | 2018-03-31 → 2026-06-30 (100) | 100 | yes | none |
| housing_starts_rebuilt_spy | HOUST | 1960-07-21 | 1993-02-28 → 2018-03-31 (302)* | 1993-02-28 → 2018-03-31 (302) | **0.0%** | 2018-04-30 → 2026-08-31 (101) | 101 | yes | none |
| unrate_spy | UNRATE | 1960-03-15 | 1999-12-31 → 2016-12-31 (205) | 1999-12-31 → 2016-12-31 (205) | **0.0%** | 2017-01-31 → 2026-09-30 (116) | 116 | yes | none |

`*` IS window derived (the pair does not publish one).

## Not affected

| Pair | Source | Status |
|---|---|---|
| cement_spy | USGS_CEMENT_MIS | not applicable: no ALFRED archive (Q7: disclosed as revised values) |
| gold_copper_xli | rule:market_close | unaffected: market data (not revised) |
| hy_ig_spy | rule:next_business_day | unaffected: market data (not revised) |
| ism_mfg_spy | ISM_MFG | not applicable: no ALFRED archive (Q7: disclosed as revised values) |
| ism_services_spy | ISM_SERVICES | not applicable: no ALFRED archive (Q7: disclosed as revised values) |
| petrol_inv_spy | EIA_WPSR_WTTSTUS1 | not applicable: no ALFRED archive (Q7: disclosed as revised values) |
| phlxsox_spy | rule:market_close | unaffected: market data (not revised) |
| t10y3m_rebuilt_spy | T10Y3M_ME | unaffected: market data (not revised) |
| t10y3m_spy | T10Y3M_ME | unaffected: market data (not revised) |
| umcsent_spy | UMCSENT | not applicable: no ALFRED archive (Q7: disclosed as revised values) |
| vix_vix3m_spy | rule:market_close | unaffected: market data (not revised) |
| wells_fargo_housing_spy | NAHB_HMI | not applicable: no ALFRED archive (Q7: disclosed as revised values) |

## Caveats
- For the pairs that do not publish an IS window (marked `*`), the derived IS includes the pipelines' warm-up rows. Their true common-IS row counts are somewhat lower, so the % lost is approximate. The eligibility verdicts are not marginal except cass_freight (57 rows).
- permit_spy has no `strategy_returns` CSV, so its rows are month-ends over the trade-log range.
- Truncation assumes track (b). Under track (a), first prints exist only from the same first vintage, so the loss is identical.
