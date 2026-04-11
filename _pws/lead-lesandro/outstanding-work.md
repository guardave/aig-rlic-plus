# Outstanding Work — Lead Lesandro

## Next Priority Pair
- **Pair #4: US10Y-US3M → SPY** (yield curve slope, daily, Yield Curve/Rates type)
- This is a well-studied indicator with strong literature (Estrella & Hardouvelis 1991)
- Expected: counter-cyclical (inverted curve → recession → equity weakness)

## Remaining Pairs (68 of 73)
- 5 completed: #1 INDPRO, #2 SOFR/TED (3 variants), #3 Permits, #11 VIX/VIX3M, #20 HY-IG (sample + v2)
- Next SPY pairs: #4 T10Y3M, #5 UMCSENT, #6 HSN1F, #7 ISM_MFG_PMI, ...
- Full list in `docs/priority-combinations-catalog.md`

## Pipeline Template Fixes Needed
- [ ] Add `bool()` cast for numpy bool in JSON serialization (pair_pipeline_permit_spy.py has the fix)
- [ ] Standardize L6 as default lead for monthly indicators in tournament grid
- [ ] Consider creating a truly generic `pair_pipeline_generic.py` that reads config from Analysis Brief

## SOP Improvements To Consider
- [x] Add audience-friendliness rules to Research + AppDev SOPs (done 2026-04-10)
- [ ] Codify "variant family" pattern formally in team-coordination SOP
- [ ] Add short-OOS auto-flag (< 5 years) to econometrics SOP
- [ ] Update Relevance Matrix with RoC signal preference note
- [ ] Add chart naming convention to team-coordination SOP (Vera prefix vs Ace no-prefix)

## Portal Improvements To Consider
- [ ] Auto-generate sidebar FINDINGS list from pair_registry instead of hardcoding
- [ ] Add cross-pair comparison page when 10+ pairs completed
- [ ] Consider template-based pages instead of per-pair files (per appdev SOP guidance for 10+ pairs)
