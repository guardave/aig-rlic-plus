ACE DONE

# AppDev Ace Handoff -- petrol_inv_spy -- 2026-06-17

## Files Created

- `app/pair_configs/petrol_inv_spy_config.py`
- `app/pages/18_petrol_inv_spy_story.py`
- `app/pages/18_petrol_inv_spy_evidence.py`
- `app/pages/18_petrol_inv_spy_strategy.py`
- `app/pages/18_petrol_inv_spy_methodology.py`

## Files Modified

- `app/components/pair_registry.py` -- added `petrol_inv_spy` route:
  `"petrol_inv_spy": "pages/18_petrol_inv_spy",`
- `app/components/display_names.py` -- added petroleum inventory display labels.
- `app/_smoke_tests/smoke_loader.py` -- added APP-PT1 dynamic chart list for
  `petrol_inv_spy` history zoom and cross-period charts.
- `app/components/page_templates.py` -- added configurable title/caption for
  the Strategy confidence slot and taught the template to read
  `winner_summary.lead_value`.
- `app/components/probability_engine_panel.py` -- removed stale XLV target
  hardcode; target overlay/caption now uses `winner_summary.target_symbol`.

## Local Cloud-Verify Slug List

- `petrol_inv_spy_story`
- `petrol_inv_spy_evidence`
- `petrol_inv_spy_strategy`
- `petrol_inv_spy_methodology`

## Verification

- `python -m py_compile ...` -- PASS.
- `python app/_smoke_tests/smoke_loader.py petrol_inv_spy` -- PASS, 20/0.
- `python app/_smoke_tests/smoke_schema_consumers.py --pair-id petrol_inv_spy` -- PASS, 5/0.
- `python app/_smoke_tests/smoke_loader.py --all` -- PASS, 10 pairs, total_failures=0.
- `python scripts/validate_all_schemas.py` -- PASS, pass=37, fail=0, skip=3.
- `python scripts/lint_filename_convention.py` -- PASS, violations=0.
- `python scripts/lint_chart_completeness.py` -- PASS, petrol_inv_spy 17/17, all pairs failures=0.
- Focused local Playwright DOM probe against `http://127.0.0.1:8501`:
  landing + all four petrol pages PASS; Strategy Execute / Performance /
  Confidence tabs individually PASS. Checks included absence of traceback,
  APP-SEV1 fallback strings, `LN/A`, and stale `long XLV` text.

## Notes

- Landing card grid sees `petrol_inv_spy` through `pair_registry`; the
  prospective-pair counter remains 9/116 because the Sample pair
  `hy_ig_v2_spy` is not part of `data/prospective_pairs.csv`.
- Strategy confidence uses the shipped `subperiod_sharpe` chart in a labeled
  "Subperiod Sharpe and Durability" slot. This avoids mislabeling it as a
  walk-forward rolling-Sharpe chart.
