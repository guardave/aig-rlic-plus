# Monthly snapshots of the no-archive (revised-only) sources

Six sources have no vintage archive: ISM manufacturing and services PMIs, the NAHB/Wells Fargo HMI, the UMich expected business conditions index, USGS Portland cement shipments, and EIA WTTSTUS1. Our pipelines therefore only ever use their latest **revised** values. The registry discloses this as `value_vintage: revised_no_archive` (pkg12 Q7).

Snapshotting them every month builds our own vintage history from now on. The archive cannot recover the past: the first snapshot is 2026-10-16.

## How to run (monthly, by hand; no scheduled job exists)

1. Refresh `data/Data Master.xlsx` as usual, so it holds the latest values.
2. From the repo root, run:

   ```bash
   python scripts/snapshot_revised_sources.py
   ```

   The run takes about 30 s. It writes `data/release_calendar/snapshots/<YYYYMMDDTHHMMSSZ>/`, which contains one `<SOURCE>.csv` per source (`ref_date,value`) and a `manifest.json`. The manifest records the UTC time, the workbook SHA-256, the sheet, column and pair loader for each source, and whether each source changed since the previous snapshot.
3. Commit the new folder: `git add data/release_calendar/snapshots && git commit`.

Good timing is shortly after the monthly ISM release (first business days of the month) and after Data Master is refreshed. Run it again whenever Data Master is updated. A snapshot is cheap (about 20 KB), and an unchanged one is recorded as such in the manifest.

Options: `--master PATH` (a different workbook), `--out DIR` (a different archive folder).

## Reading a snapshot as a vintage

The values that a past run held are the vintage as of its `snapshot_utc`. A later backtest can take, for each date `t`, the latest snapshot taken on or before `t`. That is track (b) of the pkg12 design, but only for dates after the first snapshot.
