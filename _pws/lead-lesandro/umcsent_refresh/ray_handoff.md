# Research Ray Handoff - UMCSENT x XLV Winner Refresh

RAY DONE

## Scope

Updated Ray-owned source narrative and Ray-owned interpretation metadata for `umcsent_xlv` to match Evan's corrected winner. I did not edit `app/pair_configs/umcsent_xlv_config.py`; the dispatch explicitly reserves config wiring for Ace.

## Files Changed

- `docs/portal_narrative_umcsent_xlv_20260423.md`
- `results/umcsent_xlv/interpretation_metadata.json`
- `_pws/lead-lesandro/umcsent_refresh/ray_handoff.md`

## Sections Rewritten

- Narrative frontmatter: version bumped to `1.1.0`; corrected page headlines, section anchors, chart refs, glossary terms, and `direction_asserted: procyclical`.
- Story: replaced stub with corrected UMCSENT 3-month momentum thesis and hypothesis/caveat framing.
- Evidence: added concise evidence summary that preserves existing indicator-level evidence as context, not regenerated proof.
- Strategy: added corrected winning rule and corrected performance table.
- Methodology: documented refresh scope and authoritative sources.
- Metadata: added Ray-owned `mechanism`, `caveats`, and `narrative_summary`; kept Evan's `key_finding` content unchanged; corrected `owner_writes` to assign `key_finding` to Evan and Ray-owned prose fields to Ray.

## Corrected Winner Facts For Ace

- Signal: UMCSENT 3-month momentum (`S3_mom` / `umcsent_mom`).
- Threshold: rolling z-score > +1.0.
- Lead: 6 months.
- Strategy: P1 Long/Cash, long XLV when triggered, otherwise cash.
- Direction: procyclical.
- OOS period: 2019-04-30 to 2025-12-31.
- OOS Sharpe: 1.16.
- OOS annual return: +7.95%.
- OOS max drawdown: -0.7%.
- Calmar: 11.3.
- Sortino: 1.61.
- Annual volatility: 6.9%.
- Win rate: 16%.
- Annual turnover: 3.29.

## RES-JFU Compliance

First user-facing technical-term uses now include long-form plus plain-English glosses:

- University of Michigan Consumer Sentiment (UMCSENT) -- monthly survey of household confidence.
- Out-of-sample (OOS) -- tested on data not used to pick the rule.
- Sharpe ratio -- return earned per unit of volatility.
- Z-score -- how many standard deviations above or below the recent average.
- Max drawdown -- worst peak-to-trough loss.
- Calmar ratio -- annual return divided by max drawdown risk.

## Validation

- `python scripts/validate_schema.py --schema docs/schemas/interpretation_metadata.schema.json --instance results/umcsent_xlv/interpretation_metadata.json` - exit 0.
- `python scripts/validate_schema.py --schema docs/schemas/narrative_frontmatter.schema.json --instance temp/2606190930_umcsent_ray/frontmatter_umcsent_xlv.json` - exit 0.
- Stale-winner grep over the Ray narrative and interpretation metadata - no matches.

## Ace Wiring Note

`app/pair_configs/umcsent_xlv_config.py` still contains the old rendered winner text and old metrics. That is intentionally not changed in this Ray handoff. Ace should wire the config from `docs/portal_narrative_umcsent_xlv_20260423.md`, `results/umcsent_xlv/interpretation_metadata.json`, and `results/umcsent_xlv/winner_summary.json`.
