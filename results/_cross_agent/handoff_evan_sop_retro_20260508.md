# Evan SOP Retro Handoff — 2026-05-08

## Scope

Pairs checked: `hy_ig_v2_spy`, `hy_ig_spy`, `indpro_xlp`, `indpro_spy`, `umcsent_xlv`, `dff_ted_spy`, `ted_spliced_spy`, `sofr_ted_spy`, `permit_spy`, `vix_vix3m_spy`.

Rules applied: ECON-FE1, ECON-OOS1/OOS2/OOS3, ECON-C1/C2/C2a, ECON-C4, ECON-T4, ECON-DIR2, ECON-INF1, ECON-SD, META-NMF, META-TD1, META-DASH1.

## Files Changed

- `results/*/evidence_status.json`: added schema-valid FE1 status records. All scoped pairs are `found_in_search`; no pair has a schema-valid final-exam artifact with Quincy replay.
- `results/*/winner_summary.json`: added `oos_n_obs`; set `oos_n_trades_source`; corrected true broker-derived `oos_n_trades` where deterministic.
- `results/*/core_models_*/method_coverage_manifest.json`: added retro method coverage manifests from existing artifacts.
- `results/permit_spy/signal_scope.json`: aligned persisted winner signal names with `signals_20260423.parquet`, including `permit_mom1m`.

## OOS Count Audit

| Pair | `oos_n_obs` | `oos_n_trades` after audit | Source / status |
|---|---:|---:|---|
| `hy_ig_v2_spy` | 2088 | 169 | Broker-style OOS rows |
| `hy_ig_spy` | 1712 | 225 | Broker-style OOS rows |
| `indpro_xlp` | 84 | 43 | Broker-style OOS rows |
| `umcsent_xlv` | 81 | 15 | Broker-style OOS rows |
| `indpro_spy` | 96 | 96 | Legacy count retained; true events blocked by missing broker log |
| `dff_ted_spy` | 1981 | 1981 | Legacy count retained; true events blocked by missing broker log |
| `ted_spliced_spy` | 2088 | 2088 | Legacy count retained; true events blocked by missing broker log |
| `sofr_ted_spy` | 783 | 783 | Legacy count retained; true events blocked by missing broker log |
| `permit_spy` | 96 | 96 | Legacy count retained; true events blocked by missing broker log |
| `vix_vix3m_spy` | 1566 | 1566 | Legacy count retained; true events blocked by missing broker log |

## Method Coverage

| Pair | Produced from existing artifacts | Missing blocker |
|---|---|---|
| `hy_ig_v2_spy` | correlations, distance correlation, CCF, Granger, transfer entropy, local projections, quantile regression, HMM/regime | none |
| `hy_ig_spy` | correlations, distance correlation, Granger, local projections, quantile regression, HMM/regime | CCF, transfer entropy |
| `indpro_xlp` | correlations, Granger, local projections, quantile regression | none |
| `indpro_spy` | correlations, Granger, local projections, quantile regression | none |
| `umcsent_xlv` | correlations, Granger, HMM/regime, quantile regression | none |
| `dff_ted_spy` | correlations, Granger, local projections | CCF, yield-curve decomposition |
| `ted_spliced_spy` | correlations, Granger, local projections | CCF, yield-curve decomposition |
| `sofr_ted_spy` | correlations, Granger, local projections | CCF, yield-curve decomposition |
| `permit_spy` | correlations, Granger, local projections, quantile regression | none |
| `vix_vix3m_spy` | correlations, distance correlation | VIX term-structure analysis, vol decomposition |

Missing blocker means no artifact and no C2 skip-file existed. I did not invent skip records after the fact.

## Direction / Signal Alignment

- `winner_summary.direction` values use canonical enums: `procyclical`, `countercyclical`, or `mixed`.
- `winner_summary.signal_column` is present in `signal_scope.json` for all scoped pairs after the `permit_spy` signal-scope fix.
- ECON-DIR2 horizon/sign alignment is not fully confirmable from current artifacts for legacy pairs because several `winner_summary.json` files were backfilled from tournament CSVs without full rule manifests.

## FE1 / Evidence Status

All scoped pairs are discovery-grade:

- No `final_exam_results_YYYYMMDD.json` files were present.
- No pair has FE1-required block-bootstrap uncertainty, multiple-testing/luck adjustment, frozen-rule lineage, and Quincy replay.
- All `evidence_status.json` files therefore use `status = "found_in_search"`.

## Leakage / Robust Inference Blockers

- ECON-T4 train-only fitting proof is incomplete for HMM, Markov, GMM/Jenks, rolling thresholds, and scalers. Existing artifacts do not consistently record train-only fit lineage, frozen parameters, or OOS-only scoring. Recompute or producer manifests are required before stronger claims.
- ECON-INF1 robust inference inputs are incomplete. Current method artifacts do not consistently record HAC lag, block-bootstrap method/length, bootstrap replications, or whether headline claims survive robust inference.
- OOS split records exist for `hy_ig_v2_spy` and `hy_ig_spy` only. The other eight pairs need `oos_split_record.json` before OOS window ownership is fully compliant.
- C4 broker-style logs are missing for `indpro_spy`, `dff_ted_spy`, `ted_spliced_spy`, `sofr_ted_spy`, `permit_spy`, and `vix_vix3m_spy`; true trade-event counts and user-facing trade logs require regeneration from the tournament pipeline.

## Verification

Commands run:

```bash
for p in hy_ig_v2_spy hy_ig_spy indpro_xlp indpro_spy umcsent_xlv dff_ted_spy ted_spliced_spy sofr_ted_spy permit_spy vix_vix3m_spy; do
  python3 scripts/validate_schema.py --schema docs/schemas/winner_summary.schema.json --instance results/$p/winner_summary.json
done
```

Result: all 10 `winner_summary.json` files conformed.

```bash
for p in hy_ig_v2_spy hy_ig_spy indpro_xlp indpro_spy umcsent_xlv dff_ted_spy ted_spliced_spy sofr_ted_spy permit_spy vix_vix3m_spy; do
  python3 scripts/validate_schema.py --schema docs/schemas/evidence_status.schema.json --instance results/$p/evidence_status.json
done
```

Result: all 10 `evidence_status.json` files conformed.

Additional checks:

- Parsed all retro `method_coverage_manifest.json` files as JSON.
- Checked `winner_summary.signal_column` against `signal_scope.json` derivative names after the `permit_spy` correction.
- Confirmed `git diff --check -- results` passed.
