# Handoff — Evan, Wave 10H.2 (APP-TL1 broker-style CSV data backfill)

**Author:** Econ Evan
**Date:** 2026-04-23
**Wave:** 10H.2
**Scope:** Produce `winner_trades_broker_style.csv` for `indpro_xlp` and `umcsent_xlv` per APP-TL1 spec. Do not touch `hy_ig_spy` or Sample (both already compliant). Do not touch `app/` or SOPs.

---

## 1. Discovery — broker-style CSV producer

Prior producer: `scripts/synthesize_broker_trade_log.py`. Generic across pairs *in the HY-IG daily family* — it replays the tournament winner from scratch using:

- `SIGNAL_COL_MAP` hard-coded to HY-IG signals (S1…S13 → `hy_ig_*` columns).
- Daily master parquet (`data/{pair}_daily_*.parquet`).
- Pipeline conventions `spy` / `spy_ret`, IS end `2015-12-31`, P1/P2/P3 replay math.

Not usable as-is for the two open pairs because:

| Concern | `indpro_xlp` / `umcsent_xlv` |
|---|---|
| Frequency | **monthly**, not daily (no daily parquet exists) |
| Signal columns | `indpro_accel`, `umcsent_yoy` — not in `SIGNAL_COL_MAP` |
| Target instrument | **XLP / XLV**, not SPY |
| Authoritative backtest artifact | pipelines already ship `winner_trade_log.csv` as the canonical daily-of-position + strategy-return series |

## 2. Refactor — shared helper hoisted

New file: **`scripts/_trade_log_broker.py`**
Public API: `synthesize_from_position_log(pair_id, position_col, strat_ret_col, price_col, signal_col=..., signal_display=..., commission_bps=5, starting_capital=10_000)`.

Design: trusts `winner_trade_log.csv` as the authoritative position series (it already encodes the winning strategy's replayed position), emits a broker event whenever `position` changes, pulls `price` from the master monthly parquet (`data/{pair}_monthly_*.parquet`), computes cumulative P&L from the strategy-return column, and annotates each row with a human-readable reason string citing the signal value at that date.

This complements the existing HY-IG synthesizer rather than replacing it. Two distinct producers now exist:

| Producer | Use when |
|---|---|
| `scripts/synthesize_broker_trade_log.py` | HY-IG daily family (replay from signal + threshold) |
| `scripts/_trade_log_broker.py::synthesize_from_position_log` | Pairs whose pipeline already emits `winner_trade_log.csv` as authoritative positions (monthly macro→sector pairs today) |

I did **not** refactor the HY-IG pipeline's inline emitter (`pair_pipeline_hy_ig_spy.py:1376`) nor the standalone `synthesize_broker_trade_log.py` — both are shipping today and not in scope for this wave. A future hygiene pass could unify all three under a single interface; logged as an observation only, no backlog entry opened.

## 3. Outputs — two CSVs produced

| Path | Rows | First trade | Last trade | Final cum P&L | Strategy / direction |
|---|---:|---|---|---:|---|
| `results/indpro_xlp/winner_trades_broker_style.csv` | 43 | 2019-01-31 | 2025-10-31 | +52.46 % | P3 long/short, countercyclical |
| `results/umcsent_xlv/winner_trades_broker_style.csv` | 15 | 2019-04-30 | 2025-07-31 | +77.14 % | P1 long/cash, procyclical |

Both well within the APP-TL1 typical-count band (~10–100 trades over OOS).

Invocation (reproducible):

```bash
python3 scripts/_trade_log_broker.py indpro_xlp \
    --position-col position --strat-ret-col strategy_return \
    --price-col xlp --signal-col indpro_accel \
    --signal-display "INDPRO acceleration"

python3 scripts/_trade_log_broker.py umcsent_xlv \
    --position-col position --strat-ret-col strat_ret \
    --price-col xlv --signal-col umcsent_yoy \
    --signal-display "UMCSENT YoY"
```

## 4. Schema verification — APP-TL1 compliance

Both CSVs carry the mandated header:

```
trade_date, side, instrument, quantity_pct, price,
notional_usd, commission_bps, commission_usd, cum_pnl_pct, reason
```

plus a single `#`-prefixed metadata line consumed via `pd.read_csv(path, comment="#")` (simulated-trade disclosure, starting capital, commission, strategy, signal). Matches the reference `hy_ig_spy/winner_trades_broker_style.csv` layout.

Spot-check of first few rows of each file confirmed BUY on initial entry, SELL on exit-to-cash, correct `cum_pnl_pct` progression, and reason strings that cite the actual signal value at the trade date.

## 5. Caveats / open items

- **P3_long_short on indpro_xlp.** The strategy can flip long↔short. In the current position log the winning config only actually enters long and cash (no short positions realized in OOS). The helper handles flip-to-short paths as well, but those code paths were not exercised on this data. If a future reselection surfaces a short regime, verify the reason string renders cleanly.
- **Commission rate.** Hard-coded to 5 bps per APP-TL1 default. Neither pair's `winner_summary.json` carries a `commission_bps` field — if the pipeline tournament used a different cost tier, the broker-style `commission_usd` column will be off. **→ Dana:** please confirm whether monthly pairs' tournaments use the same 5 bps tier as HY-IG; if not, add `commission_bps` to `winner_summary.json` and I will rerun.
- **Starting capital.** 10 000 USD (matches Sample). Same defaulting; same surface area if a pair runs a different stake.
- **Data dictionary gap.** There is **no** `data/data_dictionary_indpro_xlp_*.csv` or `…_umcsent_xlv_*.csv` in the repo today (only `data_dictionary_hy_ig_spy_v1_20260228.csv` exists). The broker-style schema itself is documented centrally in APP-TL1 and in the column-dictionary expander on the Strategy page (Ray-owned), so the user-facing surface is covered. **→ Dana:** if pair-level data dictionaries are planned per pair, please include the broker-style CSV columns in the new dictionary files for these two pairs. I did **not** edit the existing HY-IG dictionary to avoid touching Dana-owned artifacts.

## 6. What I did not touch

- `app/**` — Ace's domain.
- `docs/agent-sops/**` — Lead's authorship.
- `results/hy_ig_spy/winner_trades_broker_style.csv` — already compliant.
- `results/hy_ig_v2_spy/winner_trades_broker_style.csv` (Sample) — already compliant.
- `scripts/pair_pipeline_indpro_xlp.py` — the broker-style CSV is produced by the shared helper as a post-pipeline step (matches how `synthesize_broker_trade_log.py` is invoked for HY-IG variants). No pipeline rerun needed; the tournament winner is unchanged.
- Data dictionary files — Dana-owned; flagged above.
