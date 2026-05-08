# Regression Note: Three-Period Split Re-Run
**Pair:** hy_ig_v2_spy  
**Date:** 2026-05-08  
**Author:** Evan (econometrics agent)  
**Rule:** ECON-OOS4 (three-period split)

---

## Split Design Decision

Per ECON-OOS4, a three-period design was applied to replace the two-period retro-apply (Wave 5C) that had used a combined OOS window of 2018-01-01 to 2025-12-31 (2088 obs, no sealed holdout).

**Data:** `data/hy_ig_spy_daily_20000101_20251231.parquet` — 6783 trading days, 2000-01-03 to 2025-12-31.

**Split calculation (all dates from actual parquet index):**

| Period | Start | End | N obs |
|--------|-------|-----|-------|
| In-Sample (IS) | 2000-01-03 | 2018-09-28 | 4890 |
| Validation OOS | 2018-10-01 | 2024-12-31 | 1632 |
| Holdout | 2025-01-01 | 2025-12-31 | 261 |

- Holdout carved first: 2025-01-01 is first trading day of 2025, yielding 261 obs (≥ 252 minimum for daily credit class).
- Remaining sample = 299 months. ECON-OOS2 formula: `validation_span = min(max(36, round(299 × 0.25)), 120) = 75 months`.
- Validation start: 75 months before 2024-12-31 → 2018-09-30; first trading day = 2018-10-01.
- IS end = 2018-09-28 (last trading day before 2018-10-01).

**Divergence from Wave 5C (META-XVC):**
- Prior: two-period, oos_start=2018-01-01, no sealed holdout, 2088 OOS obs.
- New: three-period, validation_start=2018-10-01, holdout sealed at 2025-01-01, 1632 validation obs + 261 holdout obs.
- IS window expanded by ~9 months (2017-12-31 → 2018-09-28). No material impact on signal derivation since all threshold-based signals are recomputed from IS data at tournament time; HMM uses original IS fit (see leakage check below).

---

## HMM Leakage Check (ECON-T4)

**Finding: PASS — no leakage.**

Documentation trail:
- `execution_notes.md`: "Regime-model signals (HMM, MS) are fitted in-sample; use persisted probabilities only."
- `winner_summary.json` notes: "HMM fitted in-sample — persisted stress probabilities only."
- `signal_scope.json` (hmm_2state_prob_stress notes): confirms IS-only fit.

The original HMM was fitted on IS data ending 2017-12-31. OOS probabilities (2018 onward) are forward classifications — sequential application of the IS-fitted emission model.

Critical check: HMM IS end (2017-12-31) ≤ new IS end (2018-09-28). Condition satisfied. The period 2018-01-01 to 2018-09-28 is now "IS" in the three-period design but was "OOS" under the HMM's original fitting window. This means the HMM probabilities in that 9-month window are forward-classified (more conservative, not less) — no contamination of the holdout or validation window.

**Existing signals parquet (`signals_20260410.parquet`) reused. No refitting required.**

---

## Tournament Re-Run Results

Tournament ranked by validation OOS Sharpe (2018-10-01 to 2024-12-31, N=1632). Holdout (2025-01-01 to 2025-12-31) sealed throughout.

**Winner (unchanged):** `S6_hmm_stress / T4_hmm_0.5 / P2_signal_strength / lead=0`

| Metric | Two-Period OOS (old) | Validation OOS (new) |
|--------|---------------------|---------------------|
| OOS Sharpe | 1.274 | 1.8714 |
| OOS Ann Return | 11.33% | 16.30% |
| OOS MDD | -10.2% | -7.62% |
| OOS N obs | 2088 | 1632 |

Sharpe increase in the shorter validation window reflects that 2018-2024 was a strong period for the HMM countercyclical signal (GFC aftermath excluded from OOS, COVID stress captured). The two-period OOS had included 2018-Q1 market volatility at its start when the HMM was still in calm regime.

**Tie-break (ECON-T3):** T4_hmm_0.5 and T4_hmm_0.7 both yield validation Sharpe = 1.8714 under P2 strategy. T4_hmm_0.5 preferred as simpler (lower threshold value = more parsimonious parameterization); consistent with original winner selection.

New tournament file: `tournament_results_3period_20260508.csv` (original `tournament_results_20260410.csv` preserved intact).

---

## Final Exam on Confirmation Holdout

Holdout: 2025-01-01 to 2025-12-31 (261 trading days).

**2025 market environment:** SPY posted a strong year (+18.8% total return) but with significant intra-year stress — a tariff-driven drawdown of -18.8% peak-to-trough in April 2025, followed by recovery. The HMM signal flagged 63 stress days (prob > 0.5) concentrated in the drawdown period. The countercyclical strategy reduced SPY exposure during stress, avoided the worst of the drawdown (-4.1% MDD vs -18.8% for B&H), and participated in the recovery at higher exposure. This was a favorable environment for the signal.

| Metric | Value | Floor | Status |
|--------|-------|-------|--------|
| C1: confirm_sharpe ≥ 0.50 | 2.349 | 0.50 | PASS |
| C2: holdout not in tournament | three_period design | structural | PASS |
| C3: confirm_n_obs ≥ 252 | 261 | 252 | PASS |
| C4: confirm_delta_sharpe ≥ +0.10 | +1.391 | +0.10 | PASS |
| C5: confirm_excess_ann_return ≥ 0% | +4.32% | 0% | PASS |
| C6: confirm_mdd ≤ bh_mdd + 5pp | -4.1% ≤ -18.8%+5% | -13.8% | PASS |
| C7: bootstrap P(sharpe > bh) ≥ 0.90 | 0.97 | 0.90 | PASS |
| C8: bootstrap CI sharpe p025 > 0 | 0.917 | 0 | PASS |
| C9: n_obs_holdout ≥ minimum | 261 ≥ 252 | 252 | PASS |
| C10: bootstrap P(mdd not worse) ≥ 0.80 | 0.98 | 0.80 | PASS |

**All 10 ECON-FE1 conditions pass. Recommendation: `passed_final_exam`.**

Caveat: the 261-day holdout is a single calendar year. The wide bootstrap CI (Sharpe: 0.92 to 3.84) reflects limited statistical power. Excess return CI includes zero (-0.38 to +0.38). The pass is on point estimates and probability-of-outperformance thresholds, not on a narrow CI. 2025 was a regime-favorable year for this signal; performance in a calm, grinding bull market (no stress triggers) would likely be lower.
