# Known limits (recorded, not fixed)

2026-10-17, at the close of Phase 1 (`d780845f`). Source: `_pws/lead-lesandro/research_combos/CODEX_REVIEW_3.md`
(verdict: major revision). On the Lead's instruction these points are recorded here and **not** fixed. The project
is now exploratory (`REGISTRY_FROZEN.md`).

## 1. Provenance gaps

- **"Every parameter has provenance" is not true.** Several design constants sit outside the sourced `parameters`
  objects:
  - pass-rule margins (CVaR −15% / −10%; interaction 0.25 / 0.50 pp; BSS 0.10; IR 0.30);
  - the CVaR level (5%);
  - the 15% drawdown event definition;
  - year-over-year horizons;
  - event definitions;
  - calibration bands ([0.7, 1.3]);
  - guardrails (2 pp return shortfall and others).
  All of these are our conventions.
- **The cited papers cover less than our use of them.** The citations are real (Estrella–Mishkin, Estrella–Trubin,
  Gilchrist–Zakrajšek, Timmermann, Stock–Watson, Lown–Morgan, Faber, Sahm), but:
  - **D1-02.H1:** a 4-quarter forecast horizon does not justify the rule "inverted at any month-end in the prior 12
    months".
  - **D1-27:** the HY–IG / Baa–Aaa proxy and its 1997 splice, the continuous Sahm gap, permits YoY, the BSS margin and
    the guardrails are all unsourced.
  - **D1-05.H1:** the literature supports spread levels as predictors. It does not support this interaction on SPY,
    or the 0.25 pp margin.
  - **D1-28:** equal-weight forecast combination and an asset-price SMA do not justify this FCI weighting or the
    sector-breadth transform. Stock–Watson supports PC forecasting, not a PC1 trading overlay.
  - **D1-01:** the zero signs are natural, but the YoY horizons and the overlay design are ours. Lown–Morgan supports
    net tightening as a measure, not this overlay.
- **Consequence.** The 9 hypotheses are prospective tests of designs informed by our discovery. They are not tests of
  textbook rules.

## 2. Evaluability

- **V-C is very unlikely to settle these hypotheses within 3–5 years.** It cannot supply enough recessions or 15%
  drawdowns in that time, nor the power to detect the registered margins.
- **V-S is the only route** that could make the recession hypotheses (D1-02.H1, D1-27) evaluable. It has not been
  acquired.

## 3. Simplifications in the power methods (`scripts/power_notes.py`)

| Endpoint | Simplification |
|----------|----------------|
| CVaR | Assumes iid, globally scaled Student-t returns. It does not simulate the registered state-dependent overlay or the stationary bootstrap. |
| Interaction | A binary-group contrast. It is not the continuous product regression (term × credit) registered for D1-05.H1. |
| BSS | No minimum detectable effect is computed. |
| Exact tests | The episode-count note gives the minimum number of episodes for an all-favourable rejection. It is not an 80%-power calculation. |

## 4. Gate evasions (`scripts/gate_combo_registry.py`)

Three mutations pass the gate when they should fail:

1. **Fabricated citations.** A `source_type: citation` with an invented reference passes. The gate checks label
   consistency, not truth.
2. **Fabricated vintage series.** A `track: vintage` member with an arbitrary `pending_gap` passes, even when no such
   series or gap exists.
3. **Family mismatch.** A question family that differs from its hypotheses' families passes.

Also: `--help` is not implemented (it runs the gate), and there is no path option.

## 5. Data gaps and the analyses they block (nothing acquired)

| Gap | Data | Blocks |
|-----|------|--------|
| G5 | S&P 500 total return before 1993 | V-B (1981–1997) for every SPY overlay: D1-01, D1-05, D1-14 (1982 and 1991 episodes), D1-23, D1-28, D1-30, D2-05, D2-12. Also the B4 trend flag (SMA) before 1993 in D1-02, D1-13 and D1-27 |
| G13 | Philadelphia Fed real-time data (RTDSM), 1965–1980 | More LORO recessions for D1-02 and D1-27 H2 / H3. Without it only 1990, 2001 and 2008 qualify (1981–82 only partly, curve from 1982) |
| G15 | NFCI vintages (ALFRED) | **D1-28.H1 entirely**: its comparator is the as-published NFCI. D1-28.H2 does not need it. |
| G16 | Moody's Baa / Aaa (FRED) | Credit before 1997 for D1-05 (V-B), D1-27 H1 / H3 (LORO for 1990), D1-28 (V-B) and D1-30 (V-B). After 1997 HY–IG is available locally from 2000 only, so 1997–1999 also needs a source |
| G17 | Total-return sector / ETF series | Every relative-return question: D1-07, D1-11 sector rows, D1-16.H2, D1-18, D1-21; the D1-08 sector rows (H02–H10); D2-11. SPY itself is covered by the dividend-adjusted month-end series pinned in Phase B (`data/phaseB_inputs/spy_month_end_20261017.csv` on `feat261017_phaseB_harness`) |

## 6. Process lesson recorded

The rev3 gate tests ran inside the pre-commit hook. There they inherited `GIT_INDEX_FILE` and `GIT_DIR`, which did
two things:
- overwrote the index of this worktree (the discarded commit fa3528e4);
- set `core.bare = true` in the main repository's config. This was restored to `false` on 2026-10-17.

**Rule.** Every test that calls git unsets all `GIT_*` variables. The tests in `tests/` do this with an autouse
fixture.

## 7. Erratum: D1-05 sign wording (recorded 2026-10-20, Lead ruling; registry not edited)

- **What is wrong.** In the frozen registry (`d780845f`) the pass-rule wording for D1-05.H1, "sign d < 0 (flat
  curve with wide spreads worse)", misstates its own sign. The statistic is d on z(term) × z(credit). A month with
  a flat curve and wide spreads has z(term) < 0 and z(credit) > 0, so the product is negative. With d < 0, those
  months get a HIGHER forecast, not a lower one. D1-05.H3 has the same problem: "sign d > 0 (flight to quality)"
  gives flat-and-wide months a LOWER Treasury-proxy forecast.
- **What stays.** The registered numerical signs (H1 d < 0, H3 d > 0) remain the tests of record. Only the prose
  reading is in error.
- **When it was found.** After the data were viewed, during the exploratory D1-05 run of 2026-10-20
  (`phase2/D1_05_REPORT.md`, quadrant table). It is therefore not a pre-registered correction.
- **Consequence for reporting.** A d < 0 for H1 that clears the test means flat-and-wide months forecast higher
  next-month SPY returns. That is the opposite of the registry's prose story, and it must not be presented as
  confirming it.
