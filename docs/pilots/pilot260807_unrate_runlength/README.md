# Pilot 260807 — Run-length ("3-up / 3-down") regime derivative on UNRATE × SPY

**Question (Q1 / methodology-memo Challenge 3):** the stakeholder deck uses run-length
rule *shapes* — "three successive months below zero" (Estrella-Trubin) — that the current
signal grid does not span. Does a "3 consecutive rises / 3 consecutive falls in the
unemployment level → regime switch" derivative add anything on `unrate_spy`?

**Pair choice:** `unrate_spy` — the unemployment pair. Monthly, self-contained lead grid,
DATE_TAG `20260717` matches the live tournament (reproduces the incumbent combo-for-combo,
verified — see the harness's built-in gate), and it already carries regime-state precedent
(Sahm signal), so a run-length regime rule sits naturally alongside.

## Verdict: NEGATIVE under both framings — with a known mechanism.

The idea was tested two ways. Both say the run-length derivative does not beat what already
exists on this pair, and we can say *why*.

### Framing 1 — latched signed regime state (`run_pilot260807_unrate_runlength.py`)

Design (stakeholder-fixed): +1 after 3 consecutive monthly rises ("rising-unemployment
regime"), −1 after 3 consecutive falls, latched with hysteresis; k = 3, no sweep.

- **Reproduction gate PASSES** — the in-memory grid regenerates the live winner
  `chg_6m/T_roll_p75/procyclical/L9 = 1.5510` exactly, so the pilot is comparable.
- Best valid run-length combo (`countercyclical / P1_long_cash / L0`, the economically
  correct direction — long only when unemployment is *falling*): **OOS Sharpe 0.86** —
  below the incumbent (1.55), Sahm (1.21), **and even buy-and-hold (0.99)**, with worse
  drawdown (−23.9% vs −9.8%). Every lead trails B&H.
- **Mechanism:** the latch is pathologically coarse — 7 switches in 33 years — and can lock
  into the *wrong* regime for years. A transient 3-month uptick in early 2016 flipped it to
  "rising", and because unemployment is reported to 0.1% there were ~20 flat months in
  2010–16 that keep breaking the "3-consecutive-fall" run, so the latch stayed stuck at the
  wrong +1 from 2016 to 2020 while unemployment fell to a 50-year low. Not just weak —
  intermittently inverted. (`unrate_runlen3_pilot260807.png`, panel A annotates this.)

### Framing 2 — event study (`run_pilot260807_unrate_event_study.py`)

The stakeholder's own upgrade: drop the persistent state; treat the *completion* of a 3-run
as a dated **event**, then ask which horizon `h` after the event has the best SPY forward
performance. Method: episode-onset events (no double-counting), entry at event + 1-month
publication lag, **abnormal = conditional CAR(h) − unconditional CAR(h)** (removes the equity
risk premium), 3-up and 3-down analysed separately, event-resample bootstrap 90% CI.

- Two event definitions: `strict` (monotonic; N = 6 up / 12 down — tiny, because flat
  months break runs) and `cum0.2` (rounding-aware, |3-month Δ| ≥ 0.2pp; N = 24 up / 53 down).
- **Signs are economically sensible:** 3-up → SPY *underperforms* over the following year
  (abnormal CAR down to ≈ −7%); 3-down → SPY *outperforms* (mildly positive). The signal is
  not random.
- **But NO horizon's 90% CI clears zero** once the risk premium is removed. The lone
  `cum0.2` 3-down hit at h = 8 (+2.1%) is a multiple-testing artifact — 1 marginal point out
  of ~96 tests (24 horizons × 2 directions × 2 definitions), isolated rather than a ridge,
  naive t ≈ 0.9, nowhere near the Harvey-Liu-Zhu t > 3 hurdle.
  (`unrate_event_study_pilot260807.png`.)

## Takeaway

On `unrate_spy` the run-length regime idea is a clean negative under both a stateful and an
event-study treatment. The **useful positive by-product**: the abnormal-return *signs* line
up with economic priors (unemployment up → equities weak; down → strong), so the null is
"too small / too noisy to trade", not "no relationship". Worth recording against Challenge 3.

## Files

| File | What |
|---|---|
| `run_pilot260807_unrate_runlength.py` | Framing-1 harness (reproduction gate + latched-state scoring, production-identical) |
| `viz_pilot260807_unrate_runlength.py` | Framing-1 figure builder |
| `unrate_runlen3_pilot260807.{csv,png}` | Framing-1 leaderboard + 4-panel figure |
| `run_pilot260807_unrate_event_study.py` | Framing-2 harness (event detection, CAR, bootstrap CI) |
| `viz_pilot260807_unrate_event_study.py` | Framing-2 figure builder |
| `unrate_event_study_pilot260807.{csv,png}` | Framing-2 abnormal-CAR table + figure |

## Reproduce

```bash
python3 scripts/pilots/run_pilot260807_unrate_runlength.py      # framing 1 (+ reproduction gate)
python3 scripts/pilots/viz_pilot260807_unrate_runlength.py
python3 scripts/pilots/run_pilot260807_unrate_event_study.py    # framing 2
python3 scripts/pilots/viz_pilot260807_unrate_event_study.py
```

Both harnesses import only the pipeline's **pure** helpers and read the committed
`data/unrate_spy_monthly_latest.parquet`; neither calls `run_tournament` or writes anything
under `results/` — the frozen production tournament is untouched (ECON-T5 immutability).

## Scope & caveats

- One pair. k fixed at 3 (no sweep, per instruction) — so this does not test whether k = 2/4
  behave differently.
- Tests the **tradable** content (Sharpe / abnormal CAR). Full-sample descriptive event study;
  a tradable OOS-only version would have too few events to say anything.
- 3-up events cluster in recessions (2001/2008/2020), so the up-event forward return is partly
  a recession-timing proxy — acknowledged, not separately deconfounded.
