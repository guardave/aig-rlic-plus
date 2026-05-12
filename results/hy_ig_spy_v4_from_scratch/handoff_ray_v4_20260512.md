# Handoff: Research Ray → Team
## HY-IG × SPY v4 from scratch — Wave 2026-05-12

**Date:** 2026-05-12
**From:** Research Ray
**To:** Evan (Econometrics), Dana (Data), Ace (App Dev)
**pair_id:** `hy_ig_spy_v4_from_scratch`

---

## Deliverables Table

| Artifact | Path | Lines |
|---|---|---|
| Stage 1: Spec memo | `results/hy_ig_spy_v4_from_scratch/spec_memo_hy_ig_spy_v4_20260512.md` | 80 |
| Stage 2: Full research brief | `results/hy_ig_spy_v4_from_scratch/research_brief_hy_ig_spy_v4_20260512.md` | 322 |
| Stage 3: Narrative prose for pair config | `docs/research/hy_ig_spy_v4_narrative_prose_20260512.md` | 434 |
| Data sources CSV | `results/hy_ig_spy_v4_from_scratch/data_sources_hy_ig_spy_v4_20260512.csv` | 9 rows + header |
| This handoff | `results/hy_ig_spy_v4_from_scratch/handoff_ray_v4_20260512.md` | — |

---

## RES-NR1 Instrument Reference Check

**Rule:** Every instrument name in narrative prose must match `interpretation_metadata.json.target_symbol`. Log this check in the handoff.

**Contract assumption:** At time of writing, `results/hy_ig_spy_v4_from_scratch/interpretation_metadata.json` does not yet exist — Dana has not yet run the v4 data pipeline. Per team protocol, Ray anchors to the canonical pair spec: target = `SPY`, indicator = `hy_ig_spread`.

**Instrument references found in narrative prose (full scan):**

- `SPY` — used consistently as the explicit target symbol throughout all narrative blocks. Correct.
- `S&P 500` — appears only as a descriptive reference to what SPY tracks ("SPDR S&P 500 ETF Trust", "500 large-cap US companies"). Not used as an alternative ticker.
- `HY-IG` / `HY-IG spread` — used consistently as the indicator throughout. Correct.
- `ICE BofA US High Yield Index` — appears in methodology as a data source name. Correct.
- `ICE BofA US Investment Grade Corporate Index` — appears in methodology as a data source name. Correct.
- `BAMLH0A0HYM2`, `BAMLC0A0CM` — appear in data sources as series IDs. Correct.

**Absent (verified):** No references to XLP, XLV, INDPRO, VIX (outside robustness note context), SOFR, GS10 (outside robustness note), or any other pair-specific instrument from other portal analyses. No bare `^GSPC` or `S&P 500 Index` used as a target substitute.

**RES-NR1 verdict: PASS**

All instrument references are:
- `SPY` — confirmed target
- `HY-IG` / `hy_ig_spread` — confirmed indicator
- Descriptive clarifications of what SPY tracks
- Methodology data source names (not target instruments)

---

## META-RYW Self-Review Block

**Rule META-RYW:** Producer re-reads every deliverable end-to-end before handoff.

**Re-read performed:** 2026-05-12

### Spec Memo (`spec_memo_hy_ig_spy_v4_20260512.md`)

- [x] 5 bullets present: DV, regressors, instruments, pitfalls, sample period conventions
- [x] Table formats correct; pair_id `hy_ig_spy_v4_from_scratch` used where applicable
- [x] No v1/v2/v3 numerical findings imported
- [x] Correct series IDs: BAMLH0A0HYM2, BAMLC0A0CM, SPY

### Full Research Brief (`research_brief_hy_ig_spy_v4_20260512.md`)

- [x] Executive Summary: present, 5 bullets, search-grade language
- [x] Question: present, including 5 sub-questions
- [x] Key Findings: 6 cited studies (Gertler & Lown 1999, Gilchrist & Zakrajšek 2012, Mueller et al. 2019, López-Salido et al. 2017, Fama & French 1989, Haddad et al. 2021)
- [x] Consensus View: present, search-grade
- [x] Open Questions: present, 5 items
- [x] Implications for Our Analysis: present, 6 specific implications
- [x] Specification table: present, all required fields
- [x] Analysis categories table: 10 rows with `++` / `+` / `-` and rationale citing papers
- [x] Variables Used in Key Studies table: 6 studies
- [x] Data Sources table: 8 rows with exact series IDs and MCP server
- [x] Data Availability Risk Matrix: 7 rows including EBP flagged High risk
- [x] Event Timeline: 18 events spanning dotcom through 2023
- [x] Episode window summary table: all 5 credit_spread canonical slugs present (dotcom, gfc, covid, taper_2018, inflation_2022)
- [x] Domain Visualization Conventions: 7 conventions documented
- [x] References: 15 cited works
- [x] RES-EGL1 footer note present
- [x] No v1/v2/v3 numerical findings imported

### Narrative Prose (`hy_ig_spy_v4_narrative_prose_20260512.md`)

- [x] STORY_CONFIG: PAGE_TITLE, PAGE_SUBTITLE, HEADLINE_H2, PLAIN_ENGLISH, WHERE_THIS_FITS, ONE_SENTENCE_THESIS, NARRATIVE_SECTION_1, NARRATIVE_SECTION_2, SCOPE_NOTE, TRANSITION_TEXT — all present
- [x] HISTORY_ZOOM_EPISODES: 5 episodes present (dotcom, gfc, covid, taper_2018, inflation_2022) — each with title, narrative, caption
- [x] Canonical slugs used: `dotcom`, `gfc`, `covid`, `taper_2018`, `inflation_2022` per history_zoom_events_registry.json v1.1.0 LA-2
- [x] Non-canonical slugs absent: no `dot_com`, `rates_2022`, `taper_2013`
- [x] EVIDENCE_METHOD_BLOCKS: 3 Level-1 (Correlation, Granger/Toda-Yamamoto, Pre-Whitened CCF) + 2 Level-2 (HMM, Regime Quartile) — 5 blocks total, all with method_name, method_theory, question, how_to_read, observation (placeholder), interpretation (placeholder), key_message (placeholder)
- [x] regime_context fields present on HMM and Regime Quartile blocks
- [x] STRATEGY_CONFIG: plain English, intro paragraphs, honest caveats — all present
- [x] METHODOLOGY_CONFIG: plain English, framing, data sources — all present
- [x] pair_id `hy_ig_spy_v4_from_scratch` used in header; no `hy_ig_spy` (old pair) used as pair_id
- [x] No instrument contamination from other pairs
- [x] All observation/interpretation/key_message placeholders labeled `[PLACEHOLDER]` for Evan to replace
- [x] No v1/v2/v3 numerical findings imported

---

## RES-EGL1 Self-Check

Evidence-grade language review:

| Check | Status |
|---|---|
| No "validated" in user-facing prose | PASS |
| No "durable edge" | PASS |
| No "high confidence" | PASS |
| No "confirms" used for results | PASS |
| No "supports allocating real capital" | PASS |
| "Suggests", "is consistent with", "hypothesis" used throughout | PASS |
| All 4 DPS-EP1 canonical episodes present in HISTORY_ZOOM_EPISODES | PASS (all 5 credit_spread episodes present: dotcom, gfc, covid, taper_2018, inflation_2022) |
| `hy_ig_spy_v4_from_scratch` as pair_id where required | PASS |
| Placeholder blocks clearly labeled for Evan | PASS |

---

## Data Request (for Dana)

- **Requester:** Research Ray
- **Variables needed:**
  - HY spread: ICE BofA US High Yield Index OAS (FRED: BAMLH0A0HYM2)
  - IG spread: ICE BofA US Investment Grade Corporate OAS (FRED: BAMLC0A0CM)
  - SPY: daily adjusted close (Yahoo Finance: SPY)
  - VIX: CBOE Volatility Index (FRED: VIXCLS) — for robustness regressions
  - 10yr Treasury: US 10-Year CMT yield (FRED: GS10) — for robustness regressions
  - NBER recession dates: binary indicator (FRED: USREC) — for annotations
  - GZ Excess Bond Premium: St. Louis Fed research page (if accessible via MCP) — for IV robustness; flag as unconfirmed
- **Frequency:** Monthly (HY/IG from FRED monthly series; SPY monthly from daily close; VIX and GS10 from FRED monthly)
- **Sample period:** 1997-01-01 to present
- **Transformations:**
  - HY-IG spread = BAMLH0A0HYM2 minus BAMLC0A0CM (level, bps)
  - SPY monthly log return = log(SPY_t / SPY_{t-1}) using month-end adjusted close
  - VIX: level (monthly average or end-of-month)
  - GS10: level (monthly average)
- **Acceptable proxies:** No — BAMLH0A0HYM2 and BAMLC0A0CM are the canonical sources per the literature
- **Priority:** Standard
- **Source preference:** FRED MCP for spreads, VIX, GS10, USREC; Yahoo Finance MCP for SPY
- **Stationarity tests needed:** Yes — ADF and KPSS on HY-IG spread level and first difference, and on SPY log returns. Report test statistics and p-values.
- **GZ EBP:** Attempt FRED MCP access; if unavailable, flag as High sourcing risk and skip IV specification

---

## Notification

**Dana:** Data request above. Standard priority.

**Evan:** Spec memo (`spec_memo_hy_ig_spy_v4_20260512.md`) and full research brief (`research_brief_hy_ig_spy_v4_20260512.md`) are ready. Key specifications:
- DV: SPY monthly log return
- Primary regressors: HY-IG OAS level and z-score (rolling 36M)
- Signal variants to tournament: level, z-score, MoM change, HMM stress probability
- Identification: lag-based; Toda-Yamamoto Granger pre-test; Local Projections at horizons 1-12M
- Control robustness: add VIX and GS10 change as controls
- GFC sensitivity: report full sample + GFC-excluded (2007-09 removed)
- Stationarity: ADF + KPSS; switch to first-difference spec if level is I(1)
- SE: Newey-West HAC, 12 lags

**Ace:** Narrative prose (`docs/research/hy_ig_spy_v4_narrative_prose_20260512.md`) is structured exactly per the `indpro_xlp_config.py` pattern. Observation/interpretation/key_message fields in all 5 evidence blocks are placeholders labeled `[PLACEHOLDER]` — do NOT render placeholder text to users; use the template's "pending" state for those fields until Evan delivers v4 exam outputs.

---

*Research Ray — 2026-05-12*
