# Handoff — Viz Vera — Wave 10H.1

**Date:** 2026-04-22
**Agent:** Viz Vera
**Rules implemented:** VIZ-O1 (disposition mandate), VIZ-E1 (exploration zone + sidecar spec)
**Consumer rule:** APP-PT2 (Ace, in parallel)

---

## Scope

Three deliverables per dispatch:

1. **Idempotent backfill script** — add `disposition` field to every existing chart `_meta.json`.
2. **`exploratory_charts` entries** — surface the three Sample-pair orphans to the Methodology page via `results/hy_ig_v2_spy/analyst_suggestions.json`.
3. **Generator-script updates** — emit the `disposition` field on future runs.

---

## Files touched

### New

- `scripts/backfill_chart_dispositions.py`

### Modified — data (chart sidecars, 65 files)

All `output/charts/{pair_id}/plotly/*_meta.json` across 5 pair directories:

| Pair | Sidecars updated | Default disposition |
|------|------------------|--------------------|
| `hy_ig_spy` | 23 | consumed |
| `hy_ig_v2_spy` | 22 (19 consumed + 3 suggested) | see orphan list |
| `indpro_xlp` | 10 | consumed |
| `umcsent_xlv` | 10 | consumed |

Three orphans in `hy_ig_v2_spy` marked `"disposition": "suggested"` + `"exploratory": true`:

- `hero_spread_vs_spy_meta.json`
- `spread_history_annotated_meta.json`
- `tournament_sharpe_dist_meta.json`

### Modified — analyst_suggestions

- `results/hy_ig_v2_spy/analyst_suggestions.json` — added top-level `"exploratory_charts"` key (3 entries). Evan's `"suggestions"` array untouched (LEAD-DL1 shared-file split respected).

### Modified — generator scripts

- `scripts/generate_charts_hy_ig_spy.py` — `_save_chart()` now emits `"disposition": "consumed"` and adds `VIZ-O1` to `rules_applied`.
- `scripts/retro_fix_hy_ig_v2_vera_20260411.py` — `save_chart()` now emits `"disposition": "consumed"` (this script is the source of the existing `hy_ig_v2_spy` sidecars).
- `scripts/generate_charts.py` — original legacy generator also emits `"disposition": "consumed"`.

### NOT modified (refactor candidate — flag for follow-up wave)

The remaining per-pair generators (`generate_charts_indpro_spy.py`, `generate_charts_indpro_xlp.py`, `generate_charts_ted_variants.py`, `generate_charts_umcsent_xlv.py`) currently use a simple `fig.write_json(...)` pattern without any sidecar-writing code path — their sidecars were written by some other path (likely pipeline orchestrators or one-shot retro scripts). No surgical edit was warranted because there is no sidecar-writer function to patch. **Follow-up refactor candidate:** introduce a shared `scripts/_chart_sidecar.py` helper that all generators (new and legacy) call, so VIZ-O1 is enforced at one place rather than N. Flagged here, not in scope for 10H.1.

---

## Backfill script evidence

First run (on pristine sidecars):

```json
{"consumed": 62, "suggested": 3, "unchanged": 0, "errors": 0}
```

Second run (idempotency check):

```json
{"consumed": 0, "suggested": 0, "unchanged": 65, "errors": 0}
```

Matches the dispatch expectation (62 consumed + 3 suggested on first run; safe to rerun).

---

## Generator-edit diff summary (one exemplar)

`scripts/generate_charts_hy_ig_spy.py::_save_chart()` — fields added to the `meta` dict:

```diff
-        "rules_applied": RULES_APPLIED,
+        "rules_applied": RULES_APPLIED + ["VIZ-O1"],
+        "disposition": "consumed",
```

Plus an explanatory comment pointing future authors at VIZ-E1 / APP-PT2 for the exploratory path.

---

## ELI5 blobs for Ray/Lead review

(These are the `narrative_alignment_note` strings written verbatim into `exploratory_charts`. No jargon, no model names. Target: smart non-quant reader. 2–4 sentences each.)

### 1. `hero_spread_vs_spy` → Story

> Two lines on one chart over the last 25 years: how nervous bond investors are about risky companies (left axis) and the US stock market (right axis). When the bond-worry line jumps up, it is usually warning that a stock-market drop is coming or is already underway. Look at 2008 and 2020 — the worry line spiked first and stocks followed. This is the single clearest picture of why we pay attention to credit stress when thinking about equities.

**Vera rationale:** Single-panel dual-axis view lets the reader see credit stress leading equity drawdowns without needing a second chart.

### 2. `spread_history_annotated` → Story

> The same bond-worry line as above, but now with real historical events labelled directly on the chart: the dot-com bust, the 2008 Lehman collapse, the 2020 COVID crash, and the 2022 rate shock. Seeing each big worry-spike tied to a named crisis makes the pattern memorable — stress in credit markets is not a statistical curiosity, it is the fingerprint of every major market episode in living memory.

**Vera rationale:** Event-labelled spread history grounds the abstract signal in concrete crises for non-specialist readers.

### 3. `tournament_sharpe_dist` → Methodology

> We tested nearly 2,000 different trading rules against the same data. This chart shows how well each one performed, ranked from worst to best. Most rules are mediocre — they cluster in the middle. The strategy we picked sits out at the right-hand edge, in the top 2. The shape of this chart is the honest answer to the question most readers ask: did you get lucky, or is this rule genuinely strong? The tail tells you our winner is unusually good, not a fluke in the middle of the pack.

**Vera rationale:** Distribution view contextualises the winner against the full search space and directly answers the data-mining-risk question.

---

## Note to Quincy — cloud verification checklist

Please verify on the deployed Streamlit Cloud instance (after Ace's APP-PT2 commit also lands):

1. `hy_ig_v2_spy` Methodology page renders an **"Exploratory Insights"** section at the bottom with exactly 3 charts in this order: `hero_spread_vs_spy`, `spread_history_annotated`, `tournament_sharpe_dist`.
2. Each chart is followed by the ELI5 caption (st.caption) and a second italic caption with the Vera rationale.
3. Every other pair (`hy_ig_spy`, `indpro_xlp`, `umcsent_xlv`, plus the TED variants and any SPY-only pairs) renders their Methodology page **unchanged** — no exploratory section appears because they have no `exploratory_charts` key. This is the backward-compat guarantee in APP-PT2 and must be verified.
4. GATE-28: spot-check that every `.json` chart file in any `output/charts/{pair_id}/plotly/` directory has a sibling `_meta.json` with a `disposition` field set to one of `consumed | suggested | retired`.

---

## Parallel-landing safety

Ace is editing `app/components/page_templates.py` in parallel. The two code paths are decoupled:

- Ace's template reads `analyst_suggestions.json` → `exploratory_charts`. If Vera's commit lands first, his code reads the key normally. If his commit lands first, the key reads as present but the renderer was not yet deployed — no harm, the portal just keeps rendering the Methodology page without the section.
- Vera's sidecar `disposition` field is consumed only by GATE-28 (Quincy) and the backfill script itself. Ace does not read it.

---

## Follow-ups flagged

- **Refactor candidate:** consolidate sidecar-writing across all 7 generator scripts behind a single helper (`scripts/_chart_sidecar.py` or similar) so VIZ-O1 enforcement lives in one place. Current state: three generators patched, four more have no sidecar-writing function to patch (their sidecars originate elsewhere). Propose a Wave 10H.2 or 10I ticket.
- **Promotion path:** once user feedback accumulates on the 3 exploratory charts, Lead can decide whether to promote any of them to core-zone slots in `pair_config` (which would flip their disposition from `suggested` to `consumed` and require a page_template slot).
