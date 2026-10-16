# ALFRED full vintage histories (pkg12 D8 vintage check)

One gzipped CSV per FRED series: every (observation date, realtime_start, realtime_end, value) row from ALFRED
(`fred/series/observations`, `realtime_start=1776-07-04`, `realtime_end=9999-12-31`, `observation_start=1980-01-01`),
pulled 2026-10-16. The value of observation M "as known at date t" is the row with realtime_start <= t <= realtime_end
(9999-12-31 = still current). Observations absent from every vintage before their first release, so presence in the
vintage at t also means "released by t". Rebuild: `python _pws/lead-lesandro/pkg12_pit_release/src/pull_vintages.py`.
