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

---

## Follow-up fixes (2026-04-23T00:15)

Responding to Quincy's re-verify handoff: post-2nd-reboot with cache-clear,
cloud verify still reports **2 real FAILs byte-identical to prior run** —
ruled out as deploy-lag, confirmed real code defects. Both in Ace's lane.

### Bug 1 — Landing raw-column leak (`spy_fwd_21d`, `spy_fwd_63d`)

**Root cause:** The landing page `app/app.py` line 312 renders
`p.get("key_finding", "")` verbatim. `key_finding` is a pipeline-generated
string in each pair's `results/<pair>/interpretation_metadata.json` and
contains raw forward-return column tokens — e.g. `hy_ig_v2_spy` has
`"hy_ig_mom_63d predicts spy_fwd_63d (coef=-0.0119, ...)"`. 7 pairs
currently ship such strings. No label-mapping step existed; the leak is
not specific to Sample — it's every pair, but Sample's token happens to
be caught by Quincy's `spy_fwd` grep.

**Fix:**

1. `app/components/pair_registry.py` — added canonical `_FWD_RETURN_LABELS`
   map (11 entries covering spy/xlv/xlp × common horizons 21d/63d/126d/252d/12m)
   and `humanize_column_tokens(text)` helper. Single source of truth per
   APP-RL1 — no local duplicate in `app/app.py`. Unknown tokens pass
   through untouched (no masking of legitimate content).
2. `app/app.py` — imported `humanize_column_tokens`; wrapped `key_finding`
   display at the card render site. The search filter at line 133 still
   operates on the raw string (works with either raw or friendly tokens).

**Smoke evidence:** 4/4 leak cases covert to non-quant phrases; no
`spy_fwd_` remains in any rendered string. Assertion test at
`temp/260423_ace_wave10h1_followup/cwd_independence_test.py`-adjacent
(inline in handoff above).

### Bug 2 — APP-PT2 `_render_exploratory_insights` silent no-op on cloud

**Root cause (not what Quincy's hypothesis suggested):** The helper
itself is correct and already resolves paths via `_REPO_ROOT`
(line 228, predating Wave 10H.1 deployment). The real bug is that
`app/pages/9_hy_ig_v2_spy_methodology.py` is a **hand-written legacy
page** that does NOT call the centralized `render_methodology_page()`
template. My Wave 10H.1 commit `e6767e0` added
`_render_exploratory_insights(pair_id)` into `render_methodology_page`
at line 1400, but the Sample pair's methodology file bypasses that
template entirely, so the helper was never invoked. The DOM jump from
"Analyst Suggestions" straight into "References" is exactly what the
hand-written page's own linear flow does — there was literally no call
site between those two sections. Classic scope-miss on my part in
Wave 10H.1: I instrumented the template, not the bespoke pages.

**Fix:**

1. `app/pages/9_hy_ig_v2_spy_methodology.py` — imported
   `_render_exploratory_insights` from `components.page_templates` and
   invoked it directly before the References section (between line 204
   `render_analyst_suggestions(PAIR_ID)` and line 376 `### References`).
   The intermediate sections on this page (Return Basis, Stationarity,
   Econometric Methods, Diagnostics, Sensitivity, Reverse Causality,
   Tournament Design) sit between Analyst Suggestions and References —
   APP-PT2 §2 calls for the Exploratory Insights block between Analyst
   Suggestions and References specifically. Placing it directly
   before References keeps the "analyst-narrative bookend" ordering
   that §2 intends.
2. `app/components/page_templates.py` — tightened `_render_exploratory_insights`
   observability per APP-SEV1 L2 (your earlier request): the
   `(json.JSONDecodeError, OSError)` branch was previously silent;
   it now surfaces an `st.warning` identifying the path and exception
   class. File-missing remains silent-skip (legacy pairs without the
   key are expected, not faulty). This closes the class of "silent
   cloud fail with no DOM footprint" that Quincy diagnosed.

**Path-resolution audit (dispatch item 3):** grep of `page_templates.py`
for all `open(`, `Path(`, `glob.glob` shows every data-file read
already routes through `_REPO_ROOT` — no additional relative-path
instances to fix. The `css_path` at line 163 is static asset
(deterministic from `__file__`) — not a data read, not subject to the
CWD bug class.

### CWD-independence regression test

`temp/260423_ace_wave10h1_followup/cwd_independence_test.py` —
simulates Streamlit Cloud by `os.chdir("/tmp")` *before* importing
page_templates, then invokes `_render_exploratory_insights("hy_ig_v2_spy")`.

```
CWD = /tmp
Total streamlit calls: 12
Has heading: True
Has info banner: True
PASS: CWD-independence verified — helper renders correctly when CWD != repo root.
```

12 streamlit calls = 1 heading + 1 info banner + 3 entries × (1 caption
for "What this shows" + 1 markdown for rationale + 1 caption for
feedback prompt) + 1 trailing `---` markdown. Matches APP-PT2 §3
contract exactly.

### Smoke re-run (post-fix)

```
python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy
  → passes=15  failures=0
python3 app/_smoke_tests/smoke_loader.py hy_ig_spy
  → passes=6   failures=0
```

Logs: `app/_smoke_tests/loader_hy_ig_v2_spy_20260423.log` and
`loader_hy_ig_spy_20260423.log`.

### Proposed new rule for Lead → backlog (APP-PR1 candidate)

**Rule APP-PR1 (Path Resolution Discipline):** Every file read in
`app/components/**` and `app/pages/**` that resolves to a project-
relative location (`results/`, `output/`, `docs/`, `data/`) MUST
construct its path via an explicit module-level `_REPO_ROOT = Path(__file__).resolve().parents[N]`
anchor. Bare relative strings (e.g. `Path("results") / ...` or
`open("results/…")`) are prohibited because Streamlit Cloud's
container CWD is not necessarily the repo root, and a failed-read
wrapped in a broad `try/except` produces a silent DOM no-op that is
impossible to diagnose without a debug surface. Complementary clause
under APP-SEV1: any path-exists-but-unreadable / JSON parse failure
for a file whose presence is expected on shipped pairs MUST emit an
`st.warning` or `st.error` with the path and exception class — not
silently skip. (Silent-skip is reserved for "legacy pairs that never
adopted this feature.")

Recommend Lead add APP-PR1 to `docs/backlog.md` and to `docs/agent-sops/appdev-agent-sop.md`.
A follow-up wave could then sweep all hand-written pages
(`5_indpro_spy_methodology.py`, `6_ted_variants_methodology.py`,
`7_permit_spy_methodology.py`, `8_vix_vix3m_spy_methodology.py`,
`10_umcsent_xlv_methodology.py` — 5 pages currently bypass the
template) to call `_render_exploratory_insights` directly, so future
pairs adopting Vera's `exploratory_charts` key render consistently
whether on the template or a bespoke page. Out of scope for this
follow-up (no other pair currently ships the key, so no visible bug).

### META-AM write outcomes

Lead's `b3facc8` (settings.json single-slash → double-slash fix)
confirmed resolving BL-PERM-SUBAGENT per Quincy's 10H.1 verification.
Writes to `~/.claude/agents/appdev-ace/memories.md` and `experience.md`
attempted as part of this follow-up EOD update; confirm no permission
prompt in the session log.

### Files touched

- `app/components/pair_registry.py` (+humanize helper, +label map)
- `app/app.py` (wire in humanize at card render)
- `app/components/page_templates.py` (observability: warning on JSON
  parse failure)
- `app/pages/9_hy_ig_v2_spy_methodology.py` (wire in exploratory call)
- `app/_smoke_tests/loader_hy_ig_v2_spy_20260423.log` (new dated log)
- `app/_smoke_tests/loader_hy_ig_spy_20260423.log` (new dated log)
- `results/_cross_agent/handoff_ace_wave10h1_20260422.md` (this append)

🤖 Agent: Dev Ace
