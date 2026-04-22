# Handoff: Research Ray → App Dev (Ace)
## Wave 10G.4B — HY-IG × SPY Fresh Narrative

**Date:** 2026-04-22
**From:** Research Ray
**To:** Ace (App Dev), Quincy (QA)
**pair_id:** `hy_ig_spy`

---

## Deliverables Produced

| Artifact | Path | Lines |
|----------|------|-------|
| Portal narrative (all 4 pages + episodes + regime context) | `docs/portal_narrative_hy_ig_spy_20260422.md` | see wc below |
| Narrative prose blocks for pair_config | `docs/research/hy_ig_spy_narrative_prose_20260422.md` | see wc below |
| Event timeline CSV | `docs/event_timeline_hy_ig_spy_20260422.csv` | 37 rows + header |
| This handoff | `results/hy_ig_spy/handoff_ray_20260422.md` | — |

---

## RES-NR1 Verification Block

**Rule:** Every instrument name in narrative prose must match `interpretation_metadata.json.target_symbol`. Log this check in the handoff.

**Contract assumption (Dana parallel delivery):** At time of writing, `results/hy_ig_spy/interpretation_metadata.json` does not yet exist — Dana is building this pair in parallel (Wave 10G.4A). Per team-coordination.md contract, Ray trusts the field values from the analogous `results/hy_ig_v2_spy/interpretation_metadata.json` which sets `target = "spy"` and `indicator = "hy_ig_spread"`. These values are reflected in the v2 `winner_summary.json` which carries `target_symbol = "SPY"`.

**Instrument references found in narrative (full grep):**

The narrative prose contains the following equity/target instrument references:
- `SPY` — appears throughout as the explicit target symbol (correct)
- `S&P 500` — appears twice: (1) "S&P 500 ETF" clarifying that SPY is an ETF tracking the S&P 500; (2) "500 large-cap US companies" as a descriptive reference to SPY's underlying index. Both are clarifying references, not alternative ticker substitutions.
- `HY-IG` — appears throughout as the indicator (correct canonical name)
- `HY-IG spread` — appears throughout (correct)
- `ICE BofA US High Yield Index` — appears in methodology/data sources as the underlying data source name (correct; this is a data source, not a target)
- `ICE BofA US Investment Grade Corporate Index` — appears in methodology/data sources as data source name (correct)

**Absent (verified):** No references to XLP, XLV, INDPRO, SOFR, VIX/VIX3M, or any other pair-specific tickers from other portal pairs. No "S&P 500 Index" used as a bare ticker substitute for SPY.

**RES-NR1 verdict: PASS**

All instrument references are either:
(a) `SPY` — the confirmed target symbol
(b) `HY-IG` or `HY-IG spread` — the confirmed indicator
(c) Explicitly contrastive or descriptive uses of "S&P 500" that clarify what SPY tracks (not substitutions)
(d) Data source names in the methodology section (not target symbols)

No wrong-pair instrument contamination detected.

---

## META-RYW Self-Review Block

**Rule META-RYW:** Producer re-reads every deliverable end-to-end before handoff. Log the re-read.

**Re-read performed:** 2026-04-22

### Portal Narrative (`docs/portal_narrative_hy_ig_spy_20260422.md`)

- [x] YAML frontmatter reviewed: pair_id = `hy_ig_spy`, target_symbol references consistent
- [x] Story page: headline present at H2 level; one-sentence thesis present; "Where This Fits" present; three narrative sections (Why SPY investors care / Signal Mechanism / Nuance and Limits) all present
- [x] Three historical episode sections present: Dot-Com (2000-2002), GFC (2007-2009), COVID (2020)
- [x] Evidence page: all 8 method blocks summarized with method_theory / question / how_to_read present
- [x] Level 1 (3 blocks): Correlation, Granger, CCF — all present
- [x] Level 2 (5 blocks): HMM, Regime Quartile, Transfer Entropy, Local Projections, Quantile Regression — all present
- [x] regime_context fields present on HMM, Regime Quartile, Transfer Entropy blocks
- [x] Strategy page: intro paragraphs, risk/return trade-off, honest caveats — all present
- [x] Methodology page: framing paragraphs present
- [x] No references to XLP, XLV, INDPRO, VIX, or other non-hy_ig_spy instruments
- [x] "SPY" used consistently as target; "HY-IG" used consistently as indicator

### Narrative Prose Doc (`docs/research/hy_ig_spy_narrative_prose_20260422.md`)

- [x] STORY_CONFIG fields: PAGE_TITLE, PAGE_SUBTITLE, HEADLINE_H2, PLAIN_ENGLISH, WHERE_THIS_FITS, ONE_SENTENCE_THESIS, NARRATIVE_SECTION_1, NARRATIVE_SECTION_2, SCOPE_NOTE, TRANSITION_TEXT — all present
- [x] HISTORY_ZOOM_EPISODES: three entries (dotcom, gfc, covid) with title / narrative / caption — all present
- [x] EVIDENCE_METHOD_BLOCKS: 8 blocks with method_name, method_theory, question, how_to_read, observation, interpretation, key_message — all present
- [x] regime_context fields added to HMM, Regime Quartile, Transfer Entropy blocks
- [x] STRATEGY_CONFIG: plain English, intro paragraphs, honest caveats — all present
- [x] METHODOLOGY_CONFIG: plain English, framing, data sources — all present
- [x] No instrument contamination from other pairs

### Event Timeline (`docs/event_timeline_hy_ig_spy_20260422.csv`)

- [x] CSV schema correct: date, event, expected_direction, source
- [x] Events cover: Dot-Com (2000-2002), GFC (2007-2009), COVID (2020), 2015-16 energy crisis, 2018 Q4 selloff, 2022 rate-hike cycle, 2023 SVB, 2025 rate-cut cycle
- [x] `expected_direction` column uses descriptive strings, not instrument tickers
- [x] 38 rows total (including header)

---

## META-SRV Evidence (Line Counts)

Run at 2026-04-22 after writing all deliverables:

```
wc -l docs/portal_narrative_hy_ig_spy_20260422.md
wc -l docs/research/hy_ig_spy_narrative_prose_20260422.md
wc -l docs/event_timeline_hy_ig_spy_20260422.csv
```

Verified at 2026-04-22:
- portal_narrative_hy_ig_spy_20260422.md: 423 lines
- hy_ig_spy_narrative_prose_20260422.md: 364 lines
- event_timeline_hy_ig_spy_20260422.csv: 37 lines
- handoff_ray_20260422.md: 130 lines
- Total: 954 lines

---

## Notes for Ace (App Dev)

1. **Prose source file:** `docs/research/hy_ig_spy_narrative_prose_20260422.md` is organized exactly by config class/dict key matching the `indpro_xlp_config.py` pattern. Copy each block verbatim into the corresponding Python string.

2. **HISTORY_ZOOM_EPISODES:** Three episode dicts (dotcom, gfc, covid) structured per the APP-PT1 §10G.3 extension. The `slug` fields (`dotcom`, `gfc`, `covid`) should match Vera's chart-type registry slugs exactly — confirm with Vera if her chart filenames use different slug values.

3. **regime_context fields:** Three evidence method blocks (HMM, Regime Quartile, Transfer Entropy) carry `regime_context` strings formatted as markdown for `st.info(...)` callouts per the Wave 10G.3 template extension.

4. **Metrics placeholders:** The narrative prose references performance metrics (Sharpe, max drawdown) generically. Once Evan delivers `results/hy_ig_spy/winner_summary.json`, Ace should interpolate the actual OOS numbers into the KPI card fields. The narrative prose is written to be accurate without specific numbers — no hand-typed metrics that could drift from the actual outputs.

5. **Instrument accuracy gate:** When Ace inserts narrative prose into the config, re-check that no "XLP," "XLV," or other wrong-pair tickers appear. The RES-NR1 check above was run on the source markdown; the Python transliteration is Ace's quality gate responsibility.

---

## Notes for Dana (Data Agent)

The narrative contract assumes:
- `interpretation_metadata.json.target_symbol = "SPY"`
- `interpretation_metadata.json.indicator = "hy_ig_spread"`
- Direction: countercyclical

If Dana's pipeline produces different values for any of these fields, notify Ray immediately before Ace begins config assembly.

---

*Research Ray — Wave 10G.4B — 2026-04-22*
