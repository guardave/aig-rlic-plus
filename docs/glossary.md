# AIG-RLIC+ Glossary

Single source of truth for terms used across two or more AIG-RLIC+ SOPs. Owned by Lead; per-domain entries reviewed and amended by the relevant role agent. New terms added here when they cross the 2-SOP threshold (per META-NCD in `team-coordination.md`).

**Canonical authority** column names the rule (or registry, or schema) where the *operational behavior* of the concept lives. The glossary entry is the **definition** only — for usage rules, see the canonical authority.

**Cross-reference convention.** Rule bodies in role SOPs cite glossary terms as: `see [docs/glossary.md § <term>](../glossary.md#<term-anchor>)` (or any equivalent inline link). Inline use of the term in prose is fine; redefining it locally is a META-NCD violation.

---

## OOS window

**Definition.** Out-of-sample window: the time range whose returns are excluded from tournament model fitting so that reported performance metrics estimate genuine forward-looking edge rather than in-sample fit. In a **three-period design** (ECON-OOS4), this refers specifically to the **validation OOS** — the second period used by the tournament to rank and select rules. It is exposed to selection and cannot serve as the confirmation holdout. In a **two-period design** (data-constrained fallback), the single OOS window is exposed to selection; no clean confirmation holdout exists. Sized by the `min(max(36, round(N × 0.25)), 120)` formula in months per ECON-OOS2.

**Canonical authority.** ECON-OOS1 (ownership), ECON-OOS2 (sizing), ECON-OOS4 (three-period policy), `docs/schemas/oos_split_record.schema.json` (artifact).

**Owner of this entry.** Evan.

**See also.** Validation OOS, Confirmation window (ECON-FE1), Tournament winner.

---

## Validation OOS

**Definition.** The second period in a three-period design (ECON-OOS4). Used by the tournament to rank competing rules and select the winner. Chronologically between the in-sample (IS) period and the confirmation holdout. Because tournament search ranks rules by their performance on this window, the validation OOS is **exposed to selection** and cannot independently confirm the winner — that role belongs to the confirmation holdout (third period). In a two-period design, this concept does not exist as a separate window; the single OOS window plays both roles and consequently cannot satisfy ECON-FE1 condition 2.

**Canonical authority.** ECON-OOS4, ECON-OOS1 (field table: `oos_start`/`oos_end` in three-period design = validation window).

**Owner of this entry.** Evan.

**See also.** OOS window, Confirmation window, Tournament winner.

---

## Confirmation window

**Definition.** The post-selection time range used by ECON-FE1 (Final-Exam Confirmation Contract) to test whether a tournament-selected rule survives a frozen, non-cherry-picked test. Must not overlap any OOS window used during selection. In a **three-period design** (ECON-OOS4), this is the confirmation holdout — the third period, chronologically last, sealed before tournament search begins. Structural separation guarantees condition 2 of ECON-FE1. In a **two-period design**, no clean confirmation window exists; condition 2 cannot be satisfied and the pair is permanently capped at `needs_final_exam`. Minimum size by frequency class: daily equity/rates/credit ≥ 24 months and 252 trading days; monthly macro ≥ 36 observations; crypto daily ≥ 18 months and 365 calendar days.

**Canonical authority.** ECON-FE1, ECON-OOS4, `docs/schemas/final_exam_results.schema.json` (`sample.confirm_*` and `sample.holdout_*` fields).

**Owner of this entry.** Evan.

**See also.** OOS window, Validation OOS, Tournament winner.

---

## Perceptual render

**Definition.** A static PNG of a Plotly chart rendered via the `kaleido` library, used to verify visual correctness independently of the browser. Filename: `_perceptual_check_<chart_name>.png`. Committed to git per VIZ-CV1 (mandatory) and verified by GATE-27-PNG. Catches the "data present in JSON ≠ data visible on screen" failure class (e.g., axis-misassignment bugs that look fine to schema validators).

**Canonical authority.** VIZ-CV1.

**Owner of this entry.** Vera.

**See also.** Smoke test, Disposition.

---

## Thin wrapper

**Definition.** A page file in `app/pages/` that contains only (a) the `sys.path` shim, (b) the import of a render function, and (c) a single call to that render function with the pair config. All pair-specific content lives in `app/pair_configs/<pair_id>_config.py`; structural content lives in `app/components/page_templates.py`. The wrapper is "thin" because it carries no business logic.

**Canonical authority.** APP-PT1.

**Owner of this entry.** Ace.

**See also.** Page template, Pair config module.

---

## Page template

**Definition.** A render function in `app/components/page_templates.py` that produces one of the four canonical page types (Story, Evidence, Strategy, Methodology) by reading from a pair config. Page templates implement structural rules (breadcrumb, section ordering, NBER shading mandate, etc.); pair configs supply the pair-specific data. Adding a feature to the page template should reach all pairs that use the template — pages that bypass the template (hand-written legacy pages) require defensive direct calls per ACE-HZE1 / APP-PT1 migration protocol.

**Canonical authority.** APP-PT1, APP-PT2.

**Owner of this entry.** Ace.

**See also.** Thin wrapper, Pair config module.

---

## Pair config module

**Definition.** A Python module at `app/pair_configs/<pair_id>_config.py` that defines all pair-specific content (narrative strings, chart names, episode entries, KPI labels) consumed by `page_templates.py`. The module exports a config object/dict; the page template reads the config and renders. Pair configs are the data layer; page templates are the rendering layer.

**Canonical authority.** APP-PT1.

**Owner of this entry.** Ace.

**See also.** Thin wrapper, Page template, `HISTORY_ZOOM_EPISODES` (per ACE-HZE1 / RES-HZE1).

---

## Sidecar

**Definition.** A small JSON file that accompanies a primary artifact and carries metadata not held in the primary. Two-name split (per Wave 10F):
- `_meta.json` — chart sidecar; one per chart JSON; declares `palette_id`, `disposition`, `caption_text`, `source`, `source_sample_period`, `annotation_strategy_id`.
- `_manifest.json` — dataset sidecar (`data/{subject}_{frequency}_schema.json`); one per parquet; declares `schema_ref`, columns, units (from the DATA-D2 controlled enum), `display_name`, `direction`, `dtype`, and optional `refresh_ttl_days`. Regenerated on every rerun; a drifted or missing sidecar is a gate failure. The machine contract for unit, display name, and refresh TTL — the markdown data dictionary is the human-readable companion only.

**Canonical authority.** VIZ-O1 (chart sidecars + disposition), DATA-D5 (dataset sidecar schema contract), DATA-D13 (manifest + display-name registry bootstrap).

**Owner of this entry.** Dana (dataset side), Vera (chart side).

**See also.** Disposition, `data/manifest.json` (DATA-D13).

---

## Disposition

**Definition.** Per-chart enum declared in the chart's `_meta.json` sidecar; takes one of `consumed` (chart is referenced by a delivered portal page), `suggested` (chart is in the exploration zone — Methodology Exploratory Insights), or `retired` (chart is preserved on disk but no longer surfaced). Closes the chart-evaporation gap where a chart could exist on disk without any indication of whether it should be loaded.

**Canonical authority.** VIZ-O1, VIZ-E1.

**Owner of this entry.** Vera.

**See also.** Sidecar.

---

## Tournament winner

**Definition.** The single rule (signal × threshold × strategy family × lead/lag combination) selected from the full tournament search as the best-performing on the OOS window per ECON-T3 tie-break cascade. Persisted as `results/<pair_id>/winner_summary.json` per ECON-H5. Discovery-grade evidence by default; only promotes to `passed_final_exam` after ECON-FE1 conditions are met and Quincy verifies via GATE-ES1.

**Data-side note (Dana).** The tournament winner is downstream of Dana's delivered parquet: the OOS split boundary is traceable to `results/{pair_id}/oos_split_record.json` (ECON-OOS1) per DATA-FE1 provenance requirement. Dana ensures the delivered dataset clearly documents the in-sample/OOS boundary so the sample-separation claim in ECON-FE1 is traceable to data provenance. The `winner_summary.json.threshold_value` is consumed by portal components (e.g., Trigger card) and is not authored by Dana.

**Canonical authority.** ECON-T3 (selection), ECON-H5 (artifact), `docs/schemas/winner_summary.schema.json`.

**Owner of this entry.** Evan (selection + artifact); Dana (data-provenance traceability to OOS split).

**See also.** OOS window, Confirmation window, Final-exam contract.

---

## Block bootstrap

**Definition.** A resampling method that preserves serial dependence by resampling contiguous blocks rather than individual observations. Two variants: **stationary** (random block start, random block length drawn from a geometric distribution; preferred when autocorrelation structure is uncertain) and **circular block** (fixed block length, blocks wrap around the series end; preferred when the series has a dominant seasonal frequency). Default block lengths: daily 21 trading days, monthly 6 months, crypto 30 calendar days.

**Canonical authority.** ECON-FE1 condition 7 (use), ECON-INF1 (robust inference), `docs/schemas/final_exam_results.schema.json` (`uncertainty.bootstrap_method`).

**Owner of this entry.** Evan.

**See also.** OOS window, Confirmation window.

---

## Smoke test

**Definition.** Pre-handoff producer-side check that exercises the import + load path of an artifact without performing full rendering. Distinct from preflight (gate-specific structural check before browser pass) and cloud verify (Playwright DOM read of the deployed Streamlit app). The three terms are *not* synonyms:
- **Smoke test** — `app/_smoke_tests/smoke_loader.py` per pair; AST-parses pages, mocks Streamlit, asserts charts load. In the Wave 10J taxonomy: Ace's check is called "portal lint" (APP-ST1); Vera's check is called "chart rendering validation" (VIZ-CV1). Both feed into GATE-27, which QA re-runs independently.
- **Preflight** — gate-specific JSON-structural checks (GATE-DP1, GATE-VIZ-NBER2, GATE-29) that run inside `scripts/cloud_verify.py` before opening a browser session. No Playwright required.
- **Cloud verify** — full end-to-end run of `scripts/cloud_verify.py`: all preflights + headless Playwright browser pass + DOM capture + screenshot evidence. HABIT-QA1 mandates a human DOM read after every cloud verify run.

**Canonical authority.** APP-ST1 (portal lint / smoke), VIZ-CV1 (chart rendering validation), QA-CL4 / GATE-27 / GATE-DP1 / GATE-VIZ-NBER2 (preflights), HABIT-QA1 (cloud verify).

**Owner of this entry.** Quincy.

**See also.** PASS-with-note, Perceptual render.

---

## PASS-with-note

**Definition.** QA verdict for an item that meets the gate threshold but carries a residual non-blocking observation worth recording. Distinct from PASS (no observation) and FAIL (blocking). Used when (a) a first occurrence of an issue would be FAIL on subsequent occurrence per QA-CL3, (b) a gap is visible but explicitly within an approved exception, or (c) the gate is satisfied but the producer should be aware of an adjacent improvement opportunity. Recorded in the QA findings table with a one-sentence rationale.

**Canonical authority.** QA-FF1, QA-CL3.

**Owner of this entry.** Quincy.

**See also.** Smoke test, GATE-31.

---

## Trigger card

**Definition.** A compact scenario card on the Strategy page (implemented with `st.container(border=True)` inside a `st.columns(...)` row) that illustrates one signal-to-action scenario (BUY, REDUCE, or HOLD) using a mini-chart snippet and plain-English rule. 2–4 cards per Strategy page. Reads `winner_summary.json.threshold_value` to populate the trigger probabilities; falls back to a default heuristic (0.5) with an APP-SEV1 L3 caption when `threshold_value` is null or unparseable.

**Canonical authority.** APP-SE3.

**Owner of this entry.** Ace.

**See also.** Page template, Pair config module.

---

## `_REPO_ROOT` anchor

**Definition.** The pattern `_REPO_ROOT = Path(__file__).resolve().parents[N]` used in `app/components/**` and `app/pages/**` to anchor file reads to the repo root rather than the current working directory. Required by APP-PR1 because Streamlit Cloud executes pages with a cwd that may not equal the repo root, and bare relative paths (e.g., `open("results/...")`) silently read from the wrong location.

**Canonical authority.** APP-PR1.

**Owner of this entry.** Ace.

**See also.** Page template.

---

## Narrative instrument reference

**Definition.** Any financial instrument name (ETF ticker, index name, asset class label) that appears in user-facing Story or Evidence prose. Per RES-NR1, every such reference must match the pair's `target_symbol` and indicator scope; cross-instrument references are permitted only as historically contextual asides (e.g., a paragraph about a prior crisis episode), never as the dashboard's claimed instrument.

**Canonical authority.** RES-NR1, GATE-NR.

**Owner of this entry.** Ray.

**See also.** Episode triad.

---

## Episode triad

**Definition.** The three-part historical-episode selection mandated by RES-20: (a) **long-lead** — indicator led equity by 6+ months (e.g., GFC for credit), (b) **coincident** — indicator moved with equity (e.g., COVID), (c) **failure-case** — indicator did NOT signal a drawdown it should have caught (e.g., 2022 for credit). Optional fourth confirmer allowed. The failure-case slot is the discipline that prevents promotional-tone narrative; institutionalized intellectual honesty.

**Canonical authority.** RES-20, RES-HZE1, `docs/schemas/history_zoom_events_registry.json` (slug authority per LA-1).

**Owner of this entry.** Ray.

**See also.** Narrative instrument reference, Disposition (chart-side analog).

---

*Glossary terms are added when a concept crosses the two-SOP threshold (per META-NCD). New entries proposed by any agent in their wave handoff; consolidated by Lead at wave closure.*
