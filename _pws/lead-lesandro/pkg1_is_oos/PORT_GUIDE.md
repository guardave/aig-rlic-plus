# PORT GUIDE — GH #251/#268 IS-selected winner + common IS start

Reference implementation: `scripts/pair_pipeline_ism_mfg_spy.py` on branch
`spike261015_is_oos_floor` (`run_tournament`). Infra (schema `max_is_sharpe` enum +
`gate_consistency.py` check-B IS branch) is already on this branch; do not re-port it.

## Target pairs (12) and lineage

| Lineage | oos_start | Pairs | Lead col | PPY | OOS-valid min n (keep as-is) |
|---|---|---|---|---|---|
| (a) 25%-clamp: `oos_n = min(max(K, round(n*.25)), CAP)`; `oos_start = work.index[-oos_n]` | data-dependent | consumer_sentiment_spy, permit_yoy_spy, retail_inv_sales_spy, umcsent_spy (monthly, K=60, CAP=120) | `lead_months` | 12 | 20 |
| (a) quarterly | data-dependent | cc_delinquency_spy, sloos_ci_small_spy (K=20, CAP=40) | `lead_quarters` | 4 | 20 |
| (b) fixed | `pd.Timestamp("2017-01-31")` | cement_spy, import_price_spy, mfg_new_orders_spy, rsxfs_spy, unrate_spy, **nhs_saar_rebuilt_spy** | `lead_months` | 12 (hardcoded `/ 12` in turnover) | 60 |

- nhs_saar: port `scripts/pair_pipeline_nhs_saar_rebuilt_spy.py` (floored L2..14), NOT legacy `pair_pipeline_nhs_saar_spy.py`.
- Lineage (b) has no `work` frame; add `work = df.dropna(subset=["spy_ret"])` at the top of `run_tournament`. Variable names differ (`winner_idx`/`winner_row`, `metrics`, `thresh`); map them.
- nhs_saar_rebuilt keeps a `strategy_series[key] = rets` dict used downstream — preserve it inside pass 2.
- Keep the floored `leads` grid exactly as on this branch. Never re-introduce L0.
- MIN_IS_N: 60 for monthly; **20 for quarterly** (5 years). Exposure band 0.05–0.95 on the IS window.
- Quarterly pairs: rolling-threshold warm-ups are in quarters; common start may sit several years in — check `is_n >= 20` survives for most of the grid, report the count.
- Pipelines that compute the signal AFTER the 1993 cut (as ism does) push the common start out further (ism: 1997-12, driven by zscore_60m x T_roll_p50 x L13). Report which candidate family sets the common start.

## Block 1 — tournament loop (two passes)

Replace the whole `rows = [] ... tourn = pd.DataFrame(rows)` region. `LEAD_COL`, `PPY`,
`MIN_IS_N`, `MIN_OOS_N` are per-pair constants (table above).

```python
    cands = []
    for signal_code, col in SIGNALS.items():
        raw = df[col].astype(float)
        for tcode in threshold_codes_for(signal_code):
            threshold = build_threshold(raw, tcode)
            for direction in ["countercyclical", "procyclical"]:
                for lead in leads:
                    sig = raw.shift(lead)
                    thr = threshold.shift(lead) if isinstance(threshold, pd.Series) else threshold
                    pos = make_position(sig, thr, direction)
                    rets = (pos * df["spy_ret"]).dropna()
                    cands.append((signal_code, col, tcode, direction, lead, pos, rets))
    # COMMON IS START: latest first-valid-return date across the whole grid
    common_is_start = max(c[6].index.min() for c in cands)
    is_mask_bh = (work.index >= common_is_start) & (work.index < oos_start)
    bh_is = ann_metrics(work.loc[is_mask_bh, "spy_ret"].dropna())
    bh = ann_metrics(df.loc[oos_start:, "spy_ret"].dropna())

    def _is_block(rets, pos, start):
        r = rets.loc[(rets.index >= start) & (rets.index < oos_start)]
        p = pos.loc[(pos.index >= start) & (pos.index < oos_start)].dropna()
        expo = p.mean() if len(p) else np.nan
        ok = bool(len(r) >= MIN_IS_N and 0.05 <= expo <= 0.95 and r.std() > 0)
        return r, expo, ok

    rows = []
    for signal_code, col, tcode, direction, lead, pos, rets in cands:
        is_rets, is_exposure, is_valid = _is_block(rets, pos, common_is_start)
        own_rets, _own_expo, own_valid = _is_block(rets, pos, rets.index.min())  # sensitivity only
        oos = rets.loc[rets.index >= oos_start]
        pos_oos = pos.loc[pos.index >= oos_start].dropna()
        exposure = pos_oos.mean() if len(pos_oos) else np.nan
        n_trades = int(pos_oos.diff().abs().fillna(0).sum())
        oos_valid = bool(len(oos) >= MIN_OOS_N and 0.05 <= exposure <= 0.95 and oos.std() > 0)  # legacy/info only
        mi, mo, m = ann_metrics(is_rets), ann_metrics(own_rets), ann_metrics(oos)
        rows.append({"signal": signal_code, "signal_column": col, "threshold": tcode,
                     "strategy": "P1_long_cash", LEAD_COL: lead, "direction": direction,
                     "is_sharpe": mi["oos_sharpe"], "is_ann_return": mi["oos_ann_return"],
                     "is_max_drawdown": mi["max_drawdown"], "is_exposure": is_exposure,
                     "is_start": is_rets.index.min().date().isoformat() if len(is_rets) else None,
                     "is_end": is_rets.index.max().date().isoformat() if len(is_rets) else None,
                     "common_is_start": common_is_start.date().isoformat(),
                     "own_is_start": own_rets.index.min().date().isoformat() if len(own_rets) else None,
                     "own_is_sharpe": mo["oos_sharpe"], "own_is_n": mo["oos_n"], "own_is_valid": own_valid,
                     "oos_sharpe": m["oos_sharpe"], "oos_sortino": m["oos_sortino"],
                     "oos_calmar": m["oos_calmar"], "oos_ann_return": m["oos_ann_return"], "oos_ann_vol": m["oos_ann_vol"],
                     "max_drawdown": m["max_drawdown"], "win_rate": m["win_rate"], "n_trades": n_trades,
                     "annual_turnover": n_trades / max(len(pos_oos) / PPY, 1),
                     "is_n": mi["oos_n"], "oos_n": m["oos_n"], "is_valid": is_valid, "oos_valid": oos_valid,
                     "valid": is_valid})  # selection validity = IS (common window) only
    rows.append({"signal": "BENCHMARK", "signal_column": "spy", "threshold": "BUY_HOLD", "strategy": "BUY_HOLD",
                 LEAD_COL: 0, "direction": "benchmark", "is_sharpe": bh_is["oos_sharpe"], "is_ann_return": bh_is["oos_ann_return"],
                 "is_max_drawdown": bh_is["max_drawdown"], "is_exposure": 1.0,
                 "is_start": common_is_start.date().isoformat(), "is_end": work.index[is_mask_bh][-1].date().isoformat(),
                 "common_is_start": common_is_start.date().isoformat(), "own_is_start": None,
                 "own_is_sharpe": np.nan, "own_is_n": 0, "own_is_valid": False,
                 "oos_sharpe": bh["oos_sharpe"], "oos_sortino": bh["oos_sortino"], "oos_calmar": bh["oos_calmar"],
                 "oos_ann_return": bh["oos_ann_return"], "oos_ann_vol": bh["oos_ann_vol"], "max_drawdown": bh["max_drawdown"],
                 "win_rate": bh["win_rate"], "n_trades": 0, "annual_turnover": 0.0, "is_n": bh_is["oos_n"],
                 "oos_n": bh["oos_n"], "is_valid": False, "oos_valid": False, "valid": False})
    tourn = pd.DataFrame(rows)
```

If the pair's loop carries extra columns (e.g. `lookback`, `strategy_series`), keep them.
Direction order in the loop does not matter (selection is argmax), but keep the pair's original
order so `source_row_index` stays comparable to older files.

## Eligibility before alignment (fleet rule, Lead decision 2026-10-15)

Applies to EVERY port (first hit: cement_spy, where one short-history family pushed the
common start to 2013-11 and left 0 IS-valid rows). Keep `oos_start`, grid, `MIN_IS_N` unchanged.

1. A candidate is **IS-eligible** only if its OWN first-valid-return date leaves
   `>= MIN_IS_N` observations before `oos_start` (`n_own = (rets.index < oos_start).sum()`).
2. `common_is_start` = latest first-valid-return date among **eligible** candidates only.
3. Ineligible candidates stay in `tournament_results_*.csv` with `is_valid=False`,
   `is_eligible=False` and `is_ineligible_reason="insufficient IS history: n_own=.. < MIN_IS_N=.."`.
4. `selection.is_window` records `min_is_n`, `n_candidates`, `n_eligible`,
   `n_ineligible_short_history`; the `rule` string says "eligibility before alignment".
5. Raise only if NO candidate is eligible.

```python
    def _own_is_n(rets):
        return int((rets.index < oos_start).sum())
    eligible = [_own_is_n(c[6]) >= MIN_IS_N for c in cands]
    n_ineligible = int(len(cands) - sum(eligible))
    common_is_start = max(c[6].index.min() for c, ok in zip(cands, eligible) if ok)
    # pass 2: iterate zip(cands, eligible); is_valid = is_valid and elig; add is_eligible / is_ineligible_reason
```
Reference: `scripts/pair_pipeline_cement_spy.py::run_tournament`. On the 12 pairs already
ported (2026-10-15 CSVs) every candidate has own IS n >= MIN_IS_N, so the rule is a no-op
there (no rerun needed); it binds only for short-history signals.

## Block 2 — selection (primary / sensitivity / legacy) and side CSV

Move the `tourn.to_csv(...)` call to AFTER the rank columns are added.

```python
    valid = tourn[(tourn["valid"]) & (tourn["signal"] != "BENCHMARK")]
    if valid.empty:
        raise RuntimeError("No valid tournament strategies")
    wi = valid["is_sharpe"].idxmax()                                   # PRIMARY (no OOS consulted)
    own_pool = tourn[(tourn["own_is_valid"]) & (tourn["signal"] != "BENCHMARK")]
    oi = own_pool["own_is_sharpe"].idxmax()                            # SENSITIVITY: no common start
    legacy_pool = tourn[(tourn["oos_valid"]) & (tourn["signal"] != "BENCHMARK")]
    li = legacy_pool["oos_sharpe"].idxmax()                            # LEGACY: pre-#251 OOS argmax
    nb = tourn["signal"] != "BENCHMARK"
    tourn["is_rank"] = tourn["is_sharpe"].where(nb).rank(ascending=False, method="min")
    tourn["oos_rank"] = tourn["oos_sharpe"].where(nb).rank(ascending=False, method="min")
    tourn.to_csv(RES / f"tournament_results_{DATE_TAG}.csv", index=False)
    side_cols = ["signal", "threshold", "direction", LEAD_COL, "is_start", "is_end", "is_n", "is_sharpe",
                 "own_is_start", "own_is_n", "own_is_sharpe", "oos_sharpe", "oos_ann_return",
                 "max_drawdown", "n_trades", "oos_n", "is_rank", "oos_rank"]
    pd.DataFrame([dict(role="primary_is_selected_common_start", **tourn.loc[wi, side_cols].to_dict()),
                  dict(role="sensitivity_is_selected_own_start", **tourn.loc[oi, side_cols].to_dict()),
                  dict(role="legacy_oos_selected", **tourn.loc[li, side_cols].to_dict())]
                 ).to_csv(RES / f"legacy_oos_selection_{DATE_TAG}.csv", index=False)
    wr = tourn.loc[wi].copy()          # lineage (b): winner_idx = wi; winner_row = wr
```

Acceptance check: `legacy_oos_selected` row must reproduce the previously published winner
(combo + OOS Sharpe to 1e-6). If not, data drifted — stop and report before anything else.

## Block 3 — runner-up and is_window

```python
    runner = valid.drop(index=wi).sort_values("is_sharpe", ascending=False).head(1)
    runner_obj = None
    if not runner.empty:
        r = runner.iloc[0]
        runner_obj = {"signal": str(r["signal"]), "threshold": str(r["threshold"]), "strategy": str(r["strategy"]),
                      "lead_value": int(r[LEAD_COL]), "objective_value": round(float(r["is_sharpe"]), 6),
                      "oos_sharpe": round(float(r["oos_sharpe"]), 6)}
    is_window = {"start": str(wr["is_start"]), "end": str(wr["is_end"]), "n": int(wr["is_n"]),
                 "common_is_start": common_is_start.date().isoformat(), "oos_start": oos_start.date().isoformat(),
                 "rule": "common_is_start = latest first-valid-return date across all grid candidates; "
                         "IS metrics for every candidate computed on [common_is_start, oos_start)",
                 "bh_is_sharpe": round(float(bh_is["oos_sharpe"]), 6)}
```

## Block 4 — winner_summary fields (add/replace)

Top level (next to `notes`):
```python
        "is_sharpe": round(float(wr["is_sharpe"]), 6), "is_n": int(wr["is_n"]),
        "is_period_start": is_window["start"], "is_period_end": is_window["end"],
```
`selection` dict:
```python
        "objective": "max_is_sharpe",
        "objective_formula": "in-sample (common window [common_is_start, OOS start)) <freq> mean/std*sqrt(PPY); winner evaluated on OOS window",
        "is_window": is_window,
        # grid_scanned.median_valid_objective -> valid["is_sharpe"].median()
        "runner_up": runner_obj,
        "rationale": "Winner is the IS-valid row with the highest IN-SAMPLE Sharpe (common IS window) over the published grid; OOS metrics are reported for that row only (no OOS look-ahead in selection).",
        "legacy_oos_selected_row": {"signal": str(tourn.loc[li, "signal"]), "threshold": str(tourn.loc[li, "threshold"]),
                                    "direction": str(tourn.loc[li, "direction"]), "lead_value": int(tourn.loc[li, LEAD_COL]),
                                    "oos_sharpe": round(float(tourn.loc[li, "oos_sharpe"]), 6),
                                    "note": f"Pre-GH#251 OOS-argmax selection, comparison only; see legacy_oos_selection_{DATE_TAG}.csv"},
        "sensitivity_own_is_start_row": {"signal": str(tourn.loc[oi, "signal"]), "threshold": str(tourn.loc[oi, "threshold"]),
                                         "direction": str(tourn.loc[oi, "direction"]), "lead_value": int(tourn.loc[oi, LEAD_COL]),
                                         "own_is_start": str(tourn.loc[oi, "own_is_start"]),
                                         "own_is_sharpe": round(float(tourn.loc[oi, "own_is_sharpe"]), 6),
                                         "note": "IS argmax without common-start alignment; sensitivity only"},
```
OOS winner metrics (`oos_sharpe` etc., computed from the deployable cash-fill series) are
unchanged code — gate check A still matches them to the tournament row.

## Block 5 — wording

- `notes`: drop any hardcoded winner description (e.g. "the traded winner is diff_1m"); use an
  f-string with `wr['signal']` and the IS window; say "selected by in-sample Sharpe ... evaluated
  on the held-out OOS window".
- `evidence_status.technical_note`: "Winner selected by in-sample Sharpe (common pre-OOS window)
  from the {DATE_TAG} ... tournament and evaluated on the held-out OOS window".
- grep the pipeline for `OOS Sharpe` / `selected by` / `highest` in any rationale string.
- Do NOT edit `app/pair_configs/*_config.py` narrative — list stale line numbers only; just bump
  dated download paths (`tournament_results_*`, `stationarity_tests_*`).
  **A ported pair is NOT publishable until its narrative is rewritten** (separate narrative pass
  after fan-out; Lead decision 2026-10-15). The gate_consistency E soft warn is a real blocker
  for cloud push, not cosmetic.
- PPY check: confirm `ann_metrics` (used for BOTH IS and OOS metrics) annualises with the pair's
  own periods-per-year — sqrt(4) for quarterly (cc_delinquency, sloos_ci_small), sqrt(12)
  monthly. Some lineage-(b) pipelines hardcode `sqrt(12)`/`/12`; report the path:line you checked.

## Run / verify checklist

1. `DATE_TAG = "20261015"` (or the run date) in pipeline + `generate_charts_<pair>.py`; ECON-T5: never overwrite old dated files.
2. Run pipeline then charts. Perceptual-PNG `RuntimeError` skips are pre-existing (no chromium).
3. Gates: `validate_all_schemas.py`; `validate_schema.py --schema docs/schemas/winner_summary.schema.json --instance results/<pair>/winner_summary.json` (+ evidence_status, signal_scope, interpretation_metadata, analyst_suggestions); `gate_consistency.py <pair>`; `gate_lead_axis.py`; `validate_pair_completeness.py --pair <pair>`. Baseline at HEAD in a scratch `git worktree` to separate pre-existing fails. Expected new soft warn: gate_consistency E (config prose cites stale Sharpe) until narrative is rewritten.
4. Report: common IS window + n, OOS window + n, #IS-valid, 4-row compare (floor_published / new_primary / new_no_common_start / legacy_recomputed), B&H IS+OOS Sharpe on the same windows, Spearman(is_sharpe, oos_sharpe) across the grid.
5. Note `bootstrap.csv` p-value (`valid.oos_sharpe >= winner.oos_sharpe`) becomes the OOS percentile of an IS-selected winner — no longer a selection-bias statistic; flag, do not change in the port.
