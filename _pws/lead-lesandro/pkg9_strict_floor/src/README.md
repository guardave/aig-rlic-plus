# pkg9 strict lead floor - evidence sources

Run order (from this folder, FRED_API_KEY set): `python alfred_pull.py alfred_first_release.csv`,
`python evidence.py` (writes release_gaps_by_period.csv + series_summary.csv), then from the repo root
`python <this folder>/registry_update.py` (expects release_gaps_by_period.csv next to it).

- `alfred_first_release.csv`: ALFRED first-vintage `realtime_start` per reference period (pulled 2026-10-16).
  Daily series (T10Y3M, BAMLH0A0HYM2) are included for completeness only: ALFRED stamps their realtime_start at the
  observation date, so they cannot measure the posting lag; those floors use the documented next-business-day posting.
- `usgs_cement_publication_dates.txt`: Last-Modified of the USGS "Cement in <month>" Mineral Industry Survey PDFs
  (`d9-wret.s3.us-west-2.amazonaws.com/.../mis-YYYYMM-cemen.pdf`), used as the publication date. Cross-check: S&P Global
  reported April-2025 data published 2025-07-24, matching the file date.
- ISM, NAHB HMI and the EIA weekly report are not on FRED: their dates are generated from the publisher calendars in
  `evidence.py` (business day 1 / 3 of M+1; ~11th business day of M; Wednesday after the week-ending Friday).
