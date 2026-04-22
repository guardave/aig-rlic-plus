# Handoff — Ace, Wave 10H.1 (APP-PT2)

**Date:** 2026-04-22
**Agent:** Dev Ace (appdev-ace)
**Scope:** Implement Rule APP-PT2 — "Exploratory Insights" section on the Methodology page — in the centralised template.

---

## Summary

Added `_render_exploratory_insights(pair_id)` helper in
`app/components/page_templates.py` and wired it into `render_methodology_page()`
between the Analyst Suggestions section (13) and the References section (14).

Backward-compatible: legacy pairs without `exploratory_charts` in their
`analyst_suggestions.json` render identically to before (helper silently
returns). No modifications to `analyst_suggestions.json` (Vera's key),
chart sidecars, pair_config narrative, QA scripts, or hand-written legacy
pages.

## Files touched

- `app/components/page_templates.py` — added `_render_exploratory_insights`
  helper (~63 lines, placed near `_load_interpretation_metadata`) and one
  call-site in `render_methodology_page` (replaced section 14 lead-in
  with a new 13b block; helper emits its own trailing `---`).

## Implementation notes

- Reads `results/{pair_id}/analyst_suggestions.json`. Wraps the read in a
  `try/except (json.JSONDecodeError, OSError)` that returns silently —
  preserves backward compatibility for legacy files without the key.
- Missing file / missing key / empty list → silent no-op. No section
  heading, no separator.
- For each entry: resolves `load_plotly_chart(chart_name, pair_id, chart_key=...)`.
  If `chart_key` collides across repeated Methodology page loads it is
  pre-keyed as `exploratory_{pair_id}_{chart_name}_{idx}` to match the
  pattern used by the rest of the template.
- Missing chart artifact → APP-SEV1 L2 `st.warning(...)` then `continue`
  (does NOT short-circuit the section). Per APP-PT2 §3a.
- Missing `chart_name` → skipped via `continue` (entry is unrenderable).
- `narrative_alignment_note` rendered with canonical APP-CC1 prefix
  `"What this shows:"` via `st.caption`.
- `vera_rationale` rendered via `st.markdown` italic (`_Analytical note: ..._`)
  — matches APP-PT2 §3c.
- Feedback prompt caption appended after every successfully rendered entry.
- Blank/missing `narrative_alignment_note` or `vera_rationale` on an entry
  are skipped individually — the entry still renders whatever is present.

## Smoke evidence

### `python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy`

```
# RESULT  passes=15  failures=0
Log written: /workspaces/aig-rlic-plus/app/_smoke_tests/loader_hy_ig_v2_spy_20260422.log
```

### `python3 app/_smoke_tests/smoke_loader.py hy_ig_spy`

```
# RESULT  passes=6  failures=0
Log written: /workspaces/aig-rlic-plus/app/_smoke_tests/loader_hy_ig_spy_20260422.log
```

### Helper dry-run (`temp/260422_app_pt2/dry_run_helper.py`)

Stubbed `streamlit` + `load_plotly_chart`, drove 4 scenarios:

- (a) missing file → **0 st.\* calls** (silent skip) ✓
- (b) JSON present, `exploratory_charts` key absent → **0 st.\* calls** ✓
- (c) JSON with 2 entries → heading + info callout + 2 × (caption + italic + caption) + trailing separator = 9 calls ✓
- (d) first entry chart missing → `st.warning` emitted, second entry still renders ✓

```
ALL SCENARIOS PASS
```

At wave dispatch time, no pair has yet shipped `exploratory_charts` entries
in `analyst_suggestions.json` (Vera's Wave 10H.1 deliverable is in flight).
Smoke evidence therefore exercises the **backward-compat branch** (key
absent → silent skip) on all live pairs, plus the fully-populated branch
through the mocked dry-run harness.

## Notes for Quincy (cloud verify)

Once Vera lands the `exploratory_charts` key for a pair, Quincy should
verify on the Methodology DOM:

1. **Section heading** — `### Exploratory Insights` (h3) must appear
   between the "Analyst Suggestions for Future Work" block and the
   "References" block. Use DOM position, not text search, to confirm
   ordering.
2. **Intro callout** — `st.info(...)` block with text starting
   *"The following charts were generated as exploratory findings beyond
   the standard analytical set…"* and closing *"let the team know."*
   (APP-PT2 §2 verbatim). Rendered as a blue info banner by Streamlit.
3. **Per-entry block** — in list order from the JSON:
   - Plotly chart container (`.js-plotly-plot` via `query_selector_all` —
     Pattern 22 fix: do NOT `.count()` on `inner_text`).
   - Caption starting `**What this shows:**` (bold prefix) with the
     `narrative_alignment_note` text.
   - Italic paragraph starting `Analytical note: …` (rendered from
     `_Analytical note: …_`).
   - Caption `Useful? Let the team know if you'd like this included as a
     standard view.`
4. **Missing chart graceful** — if Vera ships an entry whose chart is not
   on disk, expect an `st.warning` "Exploratory chart '<name>' not found."
   (yellow banner) and the next entry rendering normally after it.
5. **Legacy pairs unaffected** — pairs with no `exploratory_charts` key
   (hy_ig_v2_spy, indpro_xlp, umcsent_xlv, hy_ig_spy at current state)
   must show **no** "Exploratory Insights" heading between Analyst
   Suggestions and References. Regression gate.

## Commit

Single commit staged with only `app/components/page_templates.py`, the
handoff doc, `_pws/appdev-ace/`, and `_pws/_team/status-board.md`. No
sidecar JSON, no pair_config, no QA script, no chart artifact touched.

🤖 Agent: Dev Ace
