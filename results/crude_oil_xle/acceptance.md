# Acceptance — `crude_oil_xle`

**Pair status:** Mode-2 build, checker phase in progress.
**Date:** 2026-06-03 (initial; updated as checker phase resolves).
**Lead:** Lesandro.

## Build summary

| Field | Value |
|---|---|
| Mode | Mode 2 (single maker, multiple checkers) |
| Winner | `wti_high_vol_long` (long XLE when WTI 13-week realized vol percentile > 0.75 in trailing 5-year rolling window) |
| OOS Sharpe | 0.47 vs XLE buy-and-hold 0.04 |
| OOS max drawdown | −26.3% vs XLE buy-and-hold −74.1% |
| OOS annual turnover | 3.7 |
| OOS trades | 20 (over 2015-01 to 2025-10, ~10.7 years) |
| Commission basis | 5 bps per unit of \|Δposition\| |

## Acceptance against Portal-Wide Quality Checklist

| Item | Status | Notes |
|---|---|---|
| GATE-CMP1 PASS | 🟡 in progress | Post-extension gate FAILed 6/137; resolution underway in current session (2026-06-03). |
| Mode-2 four-checker exit | 🟡 in progress | First checker dispatch returned mixed; Categories A + C fixes applied; re-dispatch pending. |
| Cloud render verify | 🟢 PASS | Verified clean on dawodev preview slot 2026-06-02 (steady state at t+3s after cold start). |
| Reference-pair comparison | 🟡 partial | Sample (`hy_ig_v2_spy`) is frozen by user direction; comparison is implicit (this pair shares the APP-PT1 template + 5-bps commission + 60/40 split conventions). |
| Stakeholder sign-off | 🔵 pending | Awaits final ratification after checker-phase exit clean. |

## Lead sign-off

To be filled at final ratification (post-checker-clean GATE-CMP1 PASS):

- [ ] All 4 checker subagents report clean.
- [ ] GATE-CMP1 exit 0 on the latest commit.
- [ ] Production cloud render verified clean (post-merge).
- [ ] `docs/pair_execution_history.md` entry added.
- [ ] `[[lessons_crude_oil_xle]]` auto-memory written.

— Lead Lesandro
