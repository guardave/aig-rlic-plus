# Data and tool inventory for the combination study

Phase 1 drafting document (revision 3), branch `research261017_indicator_combos` (from `int261017_phaseB` @ 3d735ec7),
2026-10-17. Author: Research Ray. Read-only survey: nothing on other branches was modified. The harness was read
from branch `feat261017_phaseB_harness` with `git show`.

## Executive summary

- **Reusable as-is.**
  - The point-in-time machinery: `release_calendar.csv` (26 series), 19 ALFRED vintage files and
    `scripts/_pit_align.py`.
  - The causal regime fits (`scripts/_regime_causal.py`) and the NBER dates (`scripts/_nber.py`).
  - The ETF and sector price sheet, with S&P 500 sector *indices* back to 1989-09. All of it is **price-only**
    (verified), so it serves breadth and trend measures; relative returns need total-return series (G17).
  - The harness modules for metrics, inference and leak tests.
- **Needs extending.** The harness is **one indicator per pair**: `PairSpec` has one `release_series` and one
  `vintage_series`. Combinations need per-member release series and vintages, a multi-member reading frame, a panel
  version of the circular-shift null, and new operator code.
- **Gaps.**
  - No multiple-testing correction exists anywhere in the repo: no deflated Sharpe ratio, White reality check,
    Hansen SPA, Romano–Wolf or PBO/CSCV.
  - No consolidated position series exists for the 35 fleet winners.
  - No S&P 500 total-return series before SPY (1993).
  - No Treasury bond return series.
  - No earnings data.
  - The current Cass vintage is truncated to 2016+.
  - No sequestered confirmatory dataset (G14), no pre-1980 real-time data (G13), no NFCI vintages (G15), no
    pre-1997 credit spread (G16).
  - Asset breadth beyond US equities is thin: gold (spot, 2000+), HYG (2007+), and a Treasury proxy still to be
    built (G6). International assets: none.

## 1. Data

| Asset | Path | Coverage | Status for combinations |
|-------|------|----------|-------------------------|
| Release calendar | `data/release_calendar/release_calendar.csv` (+ `_meta.json`) | 26 series, ref periods from 1985 (ISM services 1997, NEWORDER/AMTMNO 1992, RETAILIRSA/RSXFS 1992, cement 1998); built through 2026-10-16; `available_date` and `available_date_harsh`; after-close rules (BUSLOANS; M2SL until 2021-02-23) | **As-is.** Note: release dates before each series' `first_own_measured_ref` are fallback max-lag dates (conservative), e.g. IR before 2010, Cass before 2013, cement before 2021 |
| ALFRED vintages | `data/release_calendar/vintages/*.csv.gz` (19 files) | First real-time vintage: INDPRO / UNRATE / HOUST / M2SL 1980; BUSLOANS 1996; NEWORDER 1997; UMCSENT 1998; PERMIT / HSN1F 1999; RSXFS 2001; IR / DRTSCILM / DRTSCIS 2010; AMTMNO / DRCCLACBN / DRCCLACBS / HSN1FNSA 2011; Cass / RETAILIRSA 2013 | **As-is.** No vintage file for ECIALLCIV (revised only, release dates known) |
| No-archive snapshots | `data/release_calendar/snapshots/20261016T232733Z/` | ISM manufacturing (1948+), ISM services (1997+), NAHB (1985+), UMich expected business conditions (1978+), USGS cement (2005-11+), EIA WTTSTUS1 weekly (1990+) | **Revised only, so historically NOT point-in-time.** Delaying today's values to the release date ("revised-as-of") removes the timing lookahead but not the revision lookahead. Historical use is exploratory only. Point-in-time vintages accumulate from 2026-10 (`scripts/snapshot_revised_sources.py`, monthly by hand), which makes these sources usable in the forward period V-C |
| Market daily panels | `data/hy_ig_spy_daily_20000101_20260422.parquet` (HY/IG/BB/CCC/BBB OAS, DGS10, DTB3, DGS2, NFCI, fed funds, FSI, claims, VIX, VIX3M, MOVE, gold, copper, DXY, HYG, KBE, IWM, SPY); `vix_vix3m_spy_daily_20260314.parquet` (2007+); `gold_copper_xli_daily_20260526.parquet` (2000+); `phlxsox_spy_*` (1994+) | 2000 → 2026-04 (HY/IG file) | **As-is** for 2000+. Extend from FRED for V-B: T10Y3M (1982+), ICE BofA OAS (1996–97+) |
| Pair panels | `data/*_monthly_latest.parquet`, pair builders `scripts/build_*`, `data/phaseB_inputs/` (harness branch: SPY month-end, UNRATE / card delinquency legacy panels) | Per pair | Reusable for member features; each pair panel has its own index conventions, so a combination should rebuild members from the calendar and vintages, not join pair panels |
| ETF / sector prices | `data/Data Master.xlsx` sheet `etf_prices` | SPY 1993-01; XLK XLF XLV XLE XLY XLI XLU XLP XLB 1998-12; QQQ 1999-03; XHB / XBI / XSD 2006; KRE / XME / XOP / XRT 2006; KBE / KIE / KCE 2005; XLC 2018-06; **S&P 500 sector indices (11 GICS) from 1989-09** (Real Estate 2001) | **Price-only, verified.** The SPY close on 1993-01-29 is the raw 43.94, not a dividend-adjusted value. Relative-return work therefore needs total-return series even after 1999 (G17). The 1989+ sector indices are also price-only: usable for breadth or trend counts (e.g. the D1-28 FCI breadth member), **not** for relative-return validation, because missing dividends bias against high-yield sectors (XLU, XLP) |
| Other Data Master sheets | `INDPRO`, `M2SL`, `OASHY_IG`, `H Permit / Started / Sold`, `ISM PMI`, `ICSA`, `CCSA`, `JTSJOL`, `PCEPI`, `Phila Mnufturing Indx`, `ECI`, … | Varies | Candidate extra members (claims, JOLTS, Philly Fed) are present, but **outside the PIT calendar**. Adding them needs calendar rows and vintages first |
| Descriptive PIT panel (this branch) | `docs/indicator_combos/data/panel_revised_asof_monthly.csv`, `panel_realtime_alfred_monthly.csv` | 29 indicators, month-end 1985-01 → 2026-09 | **Built here.** For inspection only. Standard transforms, not the winners' transforms |
| Registry | `docs/schemas/lead_axis_registry.json` (v1.5.0) | 39 entries (35 live + archived / v1); per pair: frequency, publication lag, lead floor, position shift, release-calendar series, alignment, `value_vintage` | **As-is** for member metadata |
| Winners | `results/<pair>/winner_summary.json` | 39 files; signal, threshold, strategy, direction, OOS start (about 2017–2020), IS start (about 1997–2011), `total_combos` | **As-is** for the frozen-member family (snapshot at 3d735ec7). Several winners are provisional pending Phase B rebuilds |

## 2. Tools

| Tool | Path | What it gives | Status |
|------|------|---------------|--------|
| PIT alignment | `scripts/_pit_align.py` | `load_release`, `pit_shift` (as-of lag), `realtime_apply` (per-row vintage recomputation), `load_vintages`, `vintage_asof`, `after_close_rule`, `visible_on`, `breaches`, the trading-day calendar | **As-is per member.** A combination calls it once per member and joins on the rebalance index |
| Causal regimes | `scripts/_regime_causal.py` | `fit_hmm_causal`, `fit_ms_causal`: IS-frozen parameters, forward-filtered probabilities, `forward_filter`, a guard against target leakage (`_check_no_target`) | **As-is** for R2 regime variables |
| NBER dates | `scripts/_nber.py` | Canonical recession periods | **As-is** for U4 labels (ex-post) |
| Quantile regression | `scripts/_quantile_regression.py` | Real QuantReg (replaces the old OLS-tripled bug) | Optional for tail-conditional analysis |
| Tournament I/O guard | `scripts/_tournament_io.py` | Immutability of published tournament CSVs | Pattern to copy for pre-registration records |
| Gates | `scripts/gate_consistency.py`, `gate_lead_axis.py`, `gate_lead_floor.py`, `gate_viz_lead.py` | Winner consistency, axis = release frequency, lead floor / lookahead, lead-chart coherence | **Pattern only.** Single-pair assumptions; `gate_lead_floor` logic is directly relevant per member |
| Revised-source snapshots | `scripts/snapshot_revised_sources.py` | Monthly snapshot of the 6 no-archive sources | **As-is.** Keep running: it is the only way to get real-time ISM / NAHB in future (V-C) |
| Harness `align.py` | `feat261017_phaseB_harness:scripts/harness/align.py` | `lag_fixed`, `lag_asof`, `realtime_frames` (cached vintage frames, all leads in one pass) | Reusable per member |
| Harness `spec.py` | `…/spec.py` | `PairSpec`: one `release_series`, one `vintage_series`, multiple `level_columns` / `signals` from the *same* source | **Extend:** a `ComboSpec` with per-member `release_series` / `vintage_series` and an operator |
| Harness `positions.py` | `…/positions.py` | P1 / P2 / P3 position matrices on lagged frames; IS-quantile thresholds | Reusable for members; operators (AND, vote, filter, sizing) are new code |
| Harness `metrics.py` | `…/metrics.py` | Deployable vs dropna scoring, Sharpe, performance block, exposure, trades | **Extend:** CVaR, upside/downside capture, AUROC, Brier score, lead time, missed-rally cost |
| Harness `selection.py` | `…/selection.py` | Common IS start, raw argmax, D9 lead-plateau selection | Reusable for re-search families; no trial counting or correction |
| Harness `null.py` | `…/null.py` | Circular-shift null over the raw inputs of *one* indicator; real-time track shifts the vintage panel as a block; seed 20261016 + k | **Extend:** shift a multi-member panel jointly (N1), and re-run member selection inside each draw (N3) |
| Harness `inference.py` | `…/inference.py` | Paired circular block bootstrap of the OOS Sharpe gap vs buy-and-hold; Newey–West HAC t | Reusable; extend to gaps vs B2a and B3 and to non-Sharpe metrics |
| Harness `leak.py` | `…/leak.py` | Truncation and perturbation-of-the-future leak tests | **Reuse as-is per combination.** Essential, because operators can introduce lookahead (e.g. regime fits, expanding z-scores) |
| Harness `regime.py` | `…/regime.py` | `hmm_stress`, `ms_stress` wrappers (re-estimated inside null draws) | As-is |
| Harness `engine.py`, `candidates.py`, `run.py`, `artifacts.py`, `charts.py`, `prose.py` | — | One tournament per pair; manifest; artifact and prose writers | Pattern only; the portal-facing writers are out of scope (this project does not ship to the app) |

## 3. Gaps and proposed fixes (for Phase 2 scoping; nothing built yet)

| # | Gap | Needed by | Proposed fix | Effort |
|---|-----|-----------|--------------|--------|
| G1 | No multiple-testing correction in the repo (a grep for deflated Sharpe, reality check, SPA, Romano–Wolf, Holm, BH and PBO finds only keyword lists) | Every family (`registry/families.yaml`) | A small `combo/mt.py`: Romano–Wolf stepdown (stationary bootstrap), Holm on episode-level exact p-values, Hansen SPA, a deflated Sharpe ratio using the family's actual configuration count, CSCV-PBO | M |
| G2 | The harness is single-indicator | All D1 | `ComboSpec` + member loop over `align.py`; operator functions R1–R7 | M |
| G3 | The null shifts one series only | N1, N3 | Joint panel shift (keep inter-member offsets); member re-selection inside draws (expensive: K × members × grid) | M/H (compute) |
| G4 | No consolidated position history of the 35 winners | D1-09, D2-03, D2-12 | Re-run the frozen winners on one PIT month-end frame and store positions (read-only use of Phase B outputs once they land) | M |
| G5 | No pre-1993 equity return | V-B | S&P 500 total return (e.g. Shiller monthly data, or FRED/CRSP-style index) and Fama–French 10/12 industry portfolios (Ken French library) | L/M; licensing is fine for research |
| G6 | No bond return series | U2 equity–bond tilt | Constant-maturity Treasury return proxy from DGS10 (duration approximation), or add IEF / TLT prices (2002+) | L |
| G7 | Cass revised track truncated to 2016+ | Members using Cass | Splice the earlier ALFRED vintages (data back to 1990) | L |
| G8 | Market series start 2000 locally | V-B for B3 members | Pull FRED T10Y3M (1982+), BAMLH0A0HYM2 / BAMLC0A0CM (1996–97+) | L |
| G9 | No earnings data | D1-12 third link | Shiller S&P EPS (monthly, revised), or drop the link and use INDPRO | L |
| G10 | Extra candidate members (claims, JOLTS, Philly Fed) have no calendar or vintages | Optional | Calendar rows + ALFRED vintages (ICSA, JTSJOL are on ALFRED) | L each |
| G11 | Pre-registration registry | P1–P5 | **Done in draft (rev3):** `registry/hypotheses.yaml` (one object per hypothesis), `registry/families.yaml`, `registry/schema.json`, the gate `scripts/gate_combo_registry.py` and its 29 mutation tests (`tests/`). The branch pre-commit hook runs the gate on the staged files. Limits: the hook is active only when `core.hooksPath` is `scripts/hooks`; `git commit --no-verify` bypasses it; declared labels are checked for consistency, not truth. Still to do: a hash log at registration and an immutability guard modelled on `_tournament_io.py` | L |
| G12 | Effective-dimension estimate uses standard transforms, not winners' states | D2-02, D2-03 | Done after G4 | L |
| G13 | Real-time unemployment and output before 1980 | D1-02, D1-27 LORO event count | Philadelphia Fed Real-Time Data Set for Macroeconomists (RTDSM; unemployment vintages from 1965) | L/M |
| G14 | No sequestered confirmatory dataset | V-S (all confirmatory recession questions) | G7-ex-US real-time vintages (OECD MEI Original Release Data and Revisions; EABCN real-time database; Bank of England real-time database), local total-return equity indices, local recession dates. Acquired and frozen under a blind protocol: specs hashed before any return is read | H |
| G15 | No NFCI vintages | D1-28 benchmark | ALFRED NFCI vintages (published weekly; revised) | L |
| G16 | No credit spread before 1996–97 | D1-05, D1-27, D1-28 in V-B | Moody's Baa and Aaa yields (FRED, unrevised market data) as a pre-registered proxy | L |
| G17 | `etf_prices` is price-only | Every relative-return (U3) question; sector rows of D1-08 | Adjusted-close (total-return) series for SPY, the sector SPDRs, XHB and QQQ | L |

## 4. Constraints to carry into Phase 2

- **Common sample.** All 29 indicators complete-case gives only 2017-02 → 2025-12, inside the viewed OOS window.
  Every question therefore names a member subset with an earlier common start. The strict point-in-time panel
  (10 vintage + 4 market series) runs 2001-08 → 2026-05.
- **Mixed frequency.**
  - Quarterly members are SLOOS (published inside its quarter), card delinquency (about 50 days after quarter-end)
    and ECI (about 30 days).
  - Daily members are the spreads, VIX, gold/copper and SOX.
  - Monthly lags range from −11 days (NAHB) to 72 days (cement, median).
- **Revised-only members.** ISM, NAHB, UMich expectations, cement and EIA cannot be tested in real time
  historically. Any historical question that uses them is exploratory (gate rule R7). They become point-in-time in
  V-C through the snapshots.
- **Phase B dependency.** The frozen winners may change as Phase B rebuilds pairs. The frozen-member family must pin
  a snapshot hash.
