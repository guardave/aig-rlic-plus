# Lead-Horizon Phase 2 — Weekly Sweep + Native-Confirmation Verdicts

**Wave:** `fix260620_lead_horizon` Phase 2 (the WEEKLY half of the stakeholder's Option D = Weekly + Monthly).
**Author:** Econ Evan · **Date:** 2026-06-21 · **Rule:** ECON-LT2 (native confirmation + ±0.03 margin + ≥2-adjacent-lead durability).

## Headline

**Zero native-confirmed lead-horizon upgrades.** Across the 4 daily pairs (weekly sweep) and `petrol_inv_spy` (monthly re-run suspect), **every flagged candidate failed native confirmation** — two on the durability test (isolated single-lead spikes), three on the margin test (native best ≤ published). **Every pair keeps its current published winner.** No downstream render (Vera → Ray → Ace) is triggered by Phase 2.

This is the intended, useful result: the cheap sweep's `|Sharpe|` polarity-scan grid has a polarity-mirror / lucky-window false-positive mode, and the native tournament is the only safe gate (ECON-LT2). The same discipline caught 2 of 3 monthly phantoms earlier this wave.

## Method (per ECON-LT2)

1. **Exploratory sweep** (`scripts/lead_horizon_sweep.py --weekly`): W-FRI weekly frame, leads 1..52 weeks, ann=52, polarity-agnostic P1/P2 + hi/lo grid. Emits `CANDIDATE-WEEKLY` / `NO-WEEKLY-EDGE` flags — never an actionable winner.
2. **Native confirmation** (`temp/260620211849_leadrerun/native_weekly_tournament.py`): each pair's OWN native grid with its **native FIXED direction** (no hi/lo scan), W-FRI frame, weekly leads, published OOS window. vix / gold_copper / hy_ig are countercyclical-fixed natively (so the sweep's polarity scan is what manufactures phantoms); phlxsox natively scans both orientations.
3. **Durability scrutiny:** a real edge spreads its out-performing combos across ≥2 adjacent leads; an isolated single-lead spike is a lucky-window overfit artifact → reject.

## Per-pair verdicts (weekly)

| Pair | Published OOS Sharpe | Native-weekly best | Combo | Verdict |
|------|----------------------|--------------------|-------|---------|
| `vix_vix3m_spy`   | 1.1295 | 1.4405 @ **L8w**  | vix_backwardation / T1_p25 / P2          | **PHANTOM** (isolated spike) |
| `gold_copper_xli` | 1.2730 | 1.2706 @ L1w      | gold_copper_mom_63d / T1_p25 / P1        | NO UPGRADE (best < published) |
| `hy_ig_spy`       | 1.4083 | 1.6564 @ **L39w** | hy_ig_mom_63d / T2_rp50 / P1             | **PHANTOM** (isolated spike) |
| `phlxsox_spy`     | 1.5700 | 1.4646 @ L39w     | sox_spy_ratio_mom_12m_pct / T1_p75 / P1_counter | NO UPGRADE (best < published) |

### Durability evidence — why vix & hy_ig are phantoms despite a raw Sharpe-beat

**`vix_vix3m_spy` — vix_backwardation / T1_p25 / P2 — Sharpe by lead (weeks):**

| Lead (w) | 1 | 2 | 4 | **8** | 13 | 26 | 39 | 52 |
|----------|---|---|---|-------|----|----|----|----|
| OOS Sharpe | 0.89 | 0.80 | 0.78 | **1.44** | 0.55 | 0.58 | 0.77 | 0.55 |

All **6** valid combos that beat the published 1.1295 sit at exactly **one lead (L8w)**. The best combo spikes at L8 and reverts to 0.55 at L13 — an isolated peak on a fast-mean-reverting vol-backwardation flag. Not a durable horizon edge.

**`hy_ig_spy` — hy_ig_mom_63d / T2_rp50 / P1 — Sharpe by lead (weeks):**

| Lead (w) | 1 | 2 | 4 | 8 | 13 | 26 | **39** | 52 |
|----------|---|---|---|---|----|----|--------|----|
| OOS Sharpe | 0.45 | 0.47 | 0.35 | 0.33 | 1.06 | 0.75 | **1.66** | **−0.01** |

All **4** valid combos that beat the published 1.4083 sit at exactly **one lead (L39w ≈ 9 months)**. The best combo beats every neighbour by ~0.9 Sharpe and **flips sign one step later (L52 = −0.01)**. A 9-month lead on a credit-momentum signal is economically implausible and statistically a lone spike. Reject.

`gold_copper_xli` and `phlxsox_spy` never beat published at any weekly lead, so no durability test is needed.

## petrol_inv_spy — monthly re-run suspect

**Framing decision.** Petroleum inventory is natively WEEKLY EIA data, but this pair is **built and published as a MONTHLY pair** (signal `petrol_3m` = 3-month %chg, lead in months, monthly `winner_summary`). The suspect to settle is the **monthly** sweep's `RE-RUN` flag, so the correct native gate is the **monthly native tournament at the published granularity** (ECON-LT2 granularity-of-gate note). A weekly reframe would be a different pair (different signals/OOS/winner), out of scope for confirming this suspect.

**Native monthly re-run** (`temp/260620211849_leadrerun/native_petrol_rerun.py`, petrol's own grid extended to L0..12, frozen monthly parquet, published OOS 2017-08-31..2025-09-30):

- Published winner: `petrol_3m / T1_fixed_p50 / P1_long_cash / L12` — OOS Sharpe **1.4779**.
- Native-extended best: `petrol_level_z60 / T2_roll_p25 / P1_long_cash_pro / **L11**` — OOS Sharpe **1.5273** (+0.0494, +3.3%).

**Best-combo Sharpe by lead (months):**

| Lead (m) | 9 | 10 | **11** | 12 |
|----------|---|----|--------|----|
| OOS Sharpe | 1.00 | 1.25 | **1.53** | 0.95 |

Only **2** valid combos beat published, **both at L11** (a lead the published `{0,1,2,3,6,12}` grid never scanned). Best-per-lead across the whole grid hovers 1.27–1.45, all ≤ published except the lone L11 outlier. Margin +0.05 is within the **±0.03 guardrail noise band**. The sweep even **mis-located** the spike (it reported L*=10; native L10 is only 1.245) — textbook polarity-mirror false positive.

**Verdict: PHANTOM (isolated spike + sub-margin). Keep published `petrol_3m / L12` (1.4779).**

## Net effect on the wave

The lead-horizon wave's confirmed winner-changes remain the **2 monthly re-runs already shipped** (`indpro_spy` → S3_mom/T2_roll_p75/P1/L4, 1.2301; `indpro_xlp` → S3_mom/T1_fixed_p50/P1_long_cash_pro/L11, 1.3282). **The weekly half adds none.**

## Artifact index

- Weekly sweep (durable, committed): `results/{pair}/lead_correlation_weekly_20260620.csv`, `lead_tournament_weekly_20260620.csv`, `lead_sweep_manifest_weekly_20260620.json` for the 4 daily pairs; `results/_cross_agent/lead_horizon_gate_weekly_20260620.csv`.
- Native confirmation (working detail): `temp/260620211849_leadrerun/native_weekly_{pair}.csv` + `native_weekly_{pair}_verdict.json`; `native_petrol_extended.csv` + `native_petrol_verdict.json`. (temp/ is gitignored — this `.md` is the durable summary of those runs.)
- Code path: `scripts/lead_horizon_sweep.py` `--weekly` flag (FreqSpec). SOP: ECON-LT2 in `docs/agent-sops/econometrics-agent-sop.md`.
