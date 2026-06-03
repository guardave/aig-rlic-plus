# Acceptance — `crude_oil_xle`

**Pair status:** Mode-2 build — checker phase exited clean round-4.
**Date:** 2026-06-03 (ratified).
**Lead:** Lesandro.

## Build summary

| Field | Value |
|---|---|
| Mode | Mode 2 (single maker, multiple checkers) |
| Winner | `wti_high_vol_long` (long XLE when WTI 13-week realized vol percentile > 0.75 in trailing 5-year rolling window) |
| OOS Sharpe | 0.47 vs XLE buy-and-hold 0.04 |
| OOS max drawdown | −24.5% vs XLE buy-and-hold −68.8% |
| OOS annual turnover | 3.7 |
| OOS trades | 20 (over 2015-01 to 2025-10, ~10.7 years) |
| Commission basis | 5 bps per unit of \|Δposition\| |

## Acceptance against Portal-Wide Quality Checklist

| Item | Status | Notes |
|---|---|---|
| GATE-CMP1 PASS | 🟢 PASS | 137/137 checks PASS at branch tip 23b4404 (extension to 14 backlog-hygiene checks all clean). |
| Mode-2 four-checker exit | 🟢 PASS (round 4) | All 4 checker subagents returned PASS in the same iteration. Trajectory: R1 4 FAIL → R2 1 PASS + 3 FAIL_WITH_WARN → R3 2 PASS + 2 FAIL_WITH_WARN (minor only) → R4 4 PASS. |
| Cloud render verify | 🟢 PASS | dawodev verified after user-triggered reboot, 2026-06-03. All 4 crude pages render clean; Pearson 0.26 propagated; max DD -24.5% propagated. |
| Reference-pair comparison | 🟡 partial | Sample (`hy_ig_v2_spy`) is frozen by user direction; comparison is implicit (this pair shares the APP-PT1 template + 5-bps commission + 60/40 split conventions). |
| Stakeholder sign-off | 🟢 PASS | Lead ratified 2026-06-03 (Mode-2 single-maker; user-confirmed at checker exit). |

## Lead sign-off

- [x] All 4 checker subagents report clean (round-4 dispatch, 2026-06-03).
- [x] GATE-CMP1 exit 0 on the latest commit (`23b4404`).
- [x] dawodev cloud render verified clean after user-triggered reboot.
- [ ] Production cloud render verified clean (post-merge — pending).
- [ ] `docs/pair_execution_history.md` entry added (post-merge).
- [ ] `[[lessons_crude_oil_xle]]` auto-memory written (post-merge).

— Lead Lesandro, 2026-06-03

## Mode-2 maker-phase note

This pair was the validation case for the `fix260602_pair4_prep` SOP
infrastructure (LEAD-NPB1 + GATE-CMP1 + prospective_pairs.csv-as-SSoT).
Four checker-dispatch rounds were required to exit clean. Pattern observed:
each round resolved its own findings but exposed parallel jargon / stale-number
locations one layer deeper. The mechanical GATE-CMP1 caught structural issues
from round-1; the human checkers caught the prose / cross-layer-consistency
issues that the mechanical gate doesn't reach. The trajectory R1→R4 is the
expected shape for the first Mode-2 build under a new SOP — subsequent
pairs should converge faster.
