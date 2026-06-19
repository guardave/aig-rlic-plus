[Econ Evan] — Mode-3 session dispatch — umcsent_xlv WINNER REFRESH (stage 1, REVISED)

You are Econ Evan. Resolve persona via `./AGENTS.md`. Lead Lesandro (Claude) is manager + sole checker.

## Why this is revised — your previous BLOCK was CORRECT
You correctly found that `winner_summary.json`'s literal rule (`umcsent_mom > 6.95316`, no lead) recomputes to OOS Sharpe 0.116, NOT 1.16. Diagnosis confirmed by Lead: **winner_summary.json is CORRUPTED** — it carries the right headline metrics but the WRONG threshold/lead encoding. GROUND TRUTH is the tournament CSV winning row, which you and the CSV agree on.

### TRUE winner — tournament row 777 (this is ground truth)
- signal `S3_mom` (= `umcsent_mom`, 3-month momentum of UMCSENT)
- threshold `T3_zscore_1.0` — a **rolling z-score > +1.0** rule (NOT a fixed `gt 6.95316` level)
- **lead_months = 6** (NOT None — this is the key correction)
- strategy `P1_long_cash`
- Metrics: oos_sharpe 1.1586, oos_sortino 1.6121, oos_calmar 11.3449, oos_ann_return 0.079494, oos_ann_vol 0.068615, max_drawdown -0.007007, win_rate 0.1605, annual_turnover 3.29, is_n 243, oos_n 81, is_sharpe 0.2825. OOS window 2019-04-30 → 2025-12-31. Target XLV.

## Task (do all 4; tournament is NOT re-run — the winner row is fixed)

### 1. CORRECT `results/umcsent_xlv/winner_summary.json` to match row 777
- Encode the threshold like the reference pair `ism_services_spy` does for a rolling z-score (which uses `threshold_code="T3_zscore_neg_1.0"`, a materialized `threshold_value`, and a `threshold_note` that the threshold is rolling per lookback). For umcsent: `threshold_code="T3_zscore_1.0"`, `threshold_rule="gt"`, `threshold_value=<the materialized rolling z-score-1.0 threshold value in signal units>`, add the rolling `threshold_note`.
- Set `lead_value=6`, `lead_unit="months"`, `lead_description` accordingly.
- Carry the row's metrics (oos_sortino/calmar/ann_vol/win_rate/annual_turnover/is_n in addition to the ones already present). Keep `signal_column="umcsent_mom"`, `signal_code="S3_mom"`.
- Schema-validate against `docs/schemas/winner_summary.schema.json` — exit 0.

### 2. FIX THE PRODUCER (root cause — META-NMF, SOP-first)
`scripts/pair_pipeline_umcsent_xlv.py` wrote the wrong threshold/lead into winner_summary. Find the winner_summary serialization in that script and fix it so the selected tournament row's `threshold` (code → rule/value/note) and `lead_months` are written FAITHFULLY (no defaulting to `gt`/`None`). A re-run must reproduce the corrected winner_summary, not the corruption. If the bug is structural (shared writer), note it for Lead but fix the umcsent path at minimum.

### 3. REGENERATE winner-specific downstream artifacts for the CORRECTED rule (z-score>1.0, **lead 6**)
- `strategy_returns_<date>.csv` (MISSING) — per-period strategy returns for S3_mom / rolling-z>1.0 / P1_long_cash / **6-month lead** applied to XLV.
- `winner_trades_broker_style.csv` (STALE Apr 23) — regenerate via `scripts/_trade_log_broker.py` for the corrected winner.
- `winner_trade_log.csv` — confirm it matches the corrected rule (regenerate if it was for the wrong encoding).

### 4. FIX `interpretation_metadata.json` `key_finding` (your owned field)
Currently cites the old "umcsent_zscore predicts xlv_fwd_6m" basis. Rewrite to describe the corrected winner: UMCSENT 3-month momentum (S3_mom), rolling z-score > 1.0 trigger, **6-month lead**, P1 Long/Cash, OOS Sharpe ~1.16, min-MDD. Preserve other owned fields; don't touch Dana/Ray fields.

## Verify before handoff (Lead re-checks)
- Recompute OOS Sharpe from your regenerated `strategy_returns` over 2019-04-30→2025-12-31 using the CORRECTED rule (z-score>1.0, **lead 6**). It MUST now be ≈ 1.16 (±0.03). If it still isn't, print `EVAN BLOCKED: <details>` and STOP — do not fudge.
- All JSON you touch schema-validates exit 0.

## Conventions
- Repo root, project Python, seed 42. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable.
- Handoff `_pws/lead-lesandro/umcsent_refresh/evan_handoff.md`: corrected winner facts for Vera/Ray (signal=UMCSENT 3-month momentum, rolling z-score>1.0 trigger, **6-month lead**, Sharpe 1.16, return 7.95%, max DD -0.7%, calmar 11.3), recomputed OOS Sharpe, and what changed in the producer.
- Print `EVAN DONE` at line start + artifact list, or `EVAN BLOCKED: <reason>`.

Begin now.
