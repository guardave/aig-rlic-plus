# Discovery: Sample vs Template Trade-Log Regression Delta + APP-TL1 Spec Proposal

**Author:** Dev Ace (AppDev agent)
**Date:** 2026-04-23
**Wave:** 10H.2 discovery (no implementation)
**Scope:** Compare Sample pair `hy_ig_v2_spy` legacy Strategy page against template-based pairs' Strategy page render, specifically the Trading History / trade log block. Propose a canonical spec (draft rule APP-TL1) for Lead to author.

---

## 1. Files Inspected

| Role | Path | Lines |
|------|------|-------|
| Sample legacy page (reference impl.) | `/workspaces/aig-rlic-plus/app/pages/9_hy_ig_v2_spy_strategy.py` | 965 |
| Template wrapper (regression victim) | `/workspaces/aig-rlic-plus/app/pages/15_hy_ig_spy_strategy.py` | 17 |
| Template implementation | `/workspaces/aig-rlic-plus/app/components/page_templates.py::render_strategy_page` | §918–1193 |
| Other template pairs | `/workspaces/aig-rlic-plus/app/pages/14_indpro_xlp_strategy.py`, `10_umcsent_xlv_strategy.py` | thin wrappers |

Artifacts inventory (trade-log related):

| Pair | `winner_trade_log.csv` | `winner_trades_broker_style.csv` |
|------|:-:|:-:|
| `hy_ig_v2_spy` (Sample) | present | present |
| `hy_ig_spy` (new) | **present** | **present** |
| `indpro_xlp` | present | **missing** |
| `umcsent_xlv` | present | **missing** |

Confirmation: the broker-style artifact already exists for `hy_ig_spy` — the template simply does not consume it. So `hy_ig_spy`'s regression is purely a renderer/contract gap. For `indpro_xlp` / `umcsent_xlv` the regression is *both* a renderer gap and a data-gap (Evan/Dana-owned to produce the broker-style variant).

---

## 2. Side-by-Side Delta: Trade-Log Block

### 2.1 Sample legacy — `9_hy_ig_v2_spy_strategy.py`, Performance tab, lines 473–617

What renders, in order:

1. **`### How to Read the Trade Log` heading + 3-paragraph narrative** (ll. 474–490):
   - Simulated-vs-real disclosure ("These are simulated trades from a backtest, not actual broker executions. 5 bps round-trip commission, $10k starting stake.")
   - Two-file explanation: broker-style (user-friendly) vs position log (researcher/debugging).
2. **`Key columns in the broker-style log:` bulleted glossary** (ll. 491–507): trade_date, side, quantity_pct, price/notional_usd, commission_bps/commission_usd, cum_pnl_pct, reason — each with plain-English meaning.
3. **Bordered concrete example** (ll. 509–519): COVID-2020 single-day 91.4% → 0% move, cites actual SPY price `$294.65`, ties to -10.2% vs -34% drawdown.
4. **`#### Download Trading History` sub-heading** (l. 521).
5. **"How to read this chart" expander** with 10-row markdown column-dictionary table (ll. 523–541): type / meaning / example for every column.
6. **Two-column download layout** (ll. 554–608):
   - Left: `Download trade log (broker-style)` primary button, reads `winner_trades_broker_style.csv` with `comment="#"`, caption `"{N} executions, one row per trade"`.
   - Right: `Download position log (researcher)` secondary button, reads `winner_trade_log.csv`, caption `"{N} position-weight change rows"`.
   - Each pane has its own APP-SEV1 L2 `st.info(...)` fallback with Plain English when the CSV is missing.
7. **Preview block** (ll. 610–617): "first 10 rows of the broker-style log" `st.dataframe` + caption explaining that each row is a scale-up/scale-down.

### 2.2 Template — `page_templates.py::render_strategy_page`, Performance tab, lines 1097–1115

What renders, in order:

1. `### Trading History` heading (l. 1097).
2. Reads `winner_trade_log.csv` only (hard-coded, no broker-style path).
3. Single `st.download_button(...)` (neutral style, no `type="primary"`).
4. Preview is hidden behind a collapsed `st.expander("Preview (first 20 rows)")`; dataframe only, no captions.
5. Missing-file branch: single `st.warning(...)` — single generic message, no Plain English coda.

### 2.3 Delta summary (what's missing in template)

| Element present in Sample | Present in template? | Severity |
|---|:-:|---|
| Narrative section heading (`### How to Read the Trade Log`) | No | High — kills the narrative thread into the data |
| Simulated-vs-real trades disclosure paragraph | No | **High (compliance/honesty)** |
| Two-file model explanation (broker-style vs researcher log) | No | High — template cannot even show two files today |
| `Key columns` bulleted glossary | No | Medium |
| Bordered concrete example (COVID 2020) | No | Medium — pair-specific but exemplifies pattern |
| `#### Download Trading History` sub-heading | No | Low |
| "How to read this chart" expander + column dictionary table | No | Medium |
| Broker-style CSV download (`winner_trades_broker_style.csv`) | **No — not even read from disk** | **Critical** |
| Primary-styled, full-width download button | No (neutral, default width) | Low |
| Position log (researcher) download with caption showing row count | No (single generic button) | Medium |
| Row-count captions on each download | No | Low |
| Always-visible first-10-row preview with caption | No — hidden in expander, 20 rows, no caption | Medium |
| APP-SEV1 L2 Plain-English fallback for each missing artifact | Half (one warning covers both) | Medium |

### 2.4 Narrative / prose difference

Sample leads with a disclosure paragraph that matters for compliance ("simulated trades from a backtest, not actual broker executions"). The template has **zero prose** around the trade log. This is the primary reason user describes Sample as having "very good narratives" and the template as "less rich."

### 2.5 Data source / schema difference

- Sample reads **two CSVs** (`winner_trades_broker_style.csv` with `comment="#"` + `winner_trade_log.csv`).
- Template reads **one CSV** (`winner_trade_log.csv` only).
- The broker-style CSV has header comments (hence `comment="#"`). Template would break on it today even if the path were added, unless `comment="#"` is passed.
- `winner_trades_broker_style.csv` schema referenced in Sample column-dictionary: `trade_date, side, instrument, quantity_pct, price, notional_usd, commission_bps, commission_usd, cum_pnl_pct, reason`. The researcher log (`winner_trade_log.csv`) has a different/wider schema (position-weight change rows).

### 2.6 UX / presentation difference

- Sample: two-column download layout, primary styling on broker button, full-width buttons, always-visible preview, captions on every widget.
- Template: single button, collapsed expander for preview, no captions, no styling.

---

## 3. Blast Radius

**3 template-based pairs affected**, with graded severity:

| Pair | Renderer gap | Data gap | Effective status |
|------|:-:|:-:|---|
| `hy_ig_spy` | yes | no (both CSVs exist) | **Pure renderer regression** — upgrade template and it's fixed |
| `indpro_xlp` | yes | yes (no broker-style CSV) | Template must render, **and** Evan/Dana must produce the broker-style artifact |
| `umcsent_xlv` | yes | yes (no broker-style CSV) | Same as indpro_xlp |

Sample (`hy_ig_v2_spy`) itself is unaffected — it retains the richer legacy page. Pairs #5–#8 (`indpro_spy`, `ted_variants`, `permit_spy`, `vix_vix3m_spy`) are legacy hand-written pages and out of scope for this discovery (each would need its own audit to confirm parity with Sample — flag as follow-up).

This is a direct mirror of **BL-APP-PT1-LEGACY**: the reference implementation is richer than the template. Every new pair pinned to APP-PT1 today inherits a regressed Strategy page.

---

## 4. Draft SOP Rule — Proposal for Lead

### Proposed ID: **APP-TL1 — Trade Log Rendering Contract**

**One-paragraph preview:** The Strategy page's Trading History block must render both a broker-style execution log (user-facing, one row per trade) and a researcher position log (one row per position-weight change), each with its own download button, row-count caption, and SEV1-L2 Plain-English fallback when the artifact is missing. The block is preceded by a fixed narrative scaffold — simulated-trades disclosure, two-file explanation, column glossary — with pair-specific content injected through named config anchors (Ray-owned). The broker-style CSV is consumed with `pd.read_csv(path, comment="#")` (schema-versioned header comments are required per META-UC). Preview is always visible, first 10 rows, with a caption. Missing-artifact severity matches APP-SEV1: missing broker-style CSV = L2 (warn + fallback to position log only); missing both = L1 (error + short-circuit the Trading History block).

**Core requirements (5 bullets, for Lead to lift into SOP text):**

1. **Dual-artifact contract.** Template must read both `winner_trades_broker_style.csv` (primary, user-facing, `comment="#"`) and `winner_trade_log.csv` (secondary, researcher). Two independent download buttons, two independent fallbacks.
2. **Narrative scaffold is non-optional.** Five elements render before the downloads, in fixed order: (a) `### How to Read the Trade Log` heading, (b) simulated-vs-real disclosure paragraph, (c) two-file model explanation, (d) `Key columns` bulleted glossary, (e) pair-specific concrete example (bordered container). Items (a)–(d) come from canonical defaults in the template; item (e) is injected via `config.TRADE_LOG_EXAMPLE_MD` (Ray-owned narrative anchor).
3. **Column-dictionary expander.** `#### Download Trading History` sub-heading followed by an expander labelled "How to read this chart" with a 10-row markdown table (Column / Type / Meaning / Example). Canonical copy lives in the template; pair-specific examples optionally override via config.
4. **Preview and captions mandatory.** First-10-row `st.dataframe` preview always visible (not expander-gated), with a caption explaining what each row represents. Each download button carries a caption stating the row count.
5. **APP-SEV1 alignment.** Missing `winner_trades_broker_style.csv` → L2 `st.info(...)` with Plain-English explanation, render the position-log download only. Missing both CSVs → L1 `st.error(...)` and short-circuit the Trading History block. Malformed CSV → L2 `st.warning(...)` and continue with the other pane.

### Required config anchors (pair-specific content)

| Attribute | Owner | Content |
|---|---|---|
| `TRADE_LOG_EXAMPLE_MD` | Ray | Bordered concrete example — pair-specific crisis event, actual signal values, before/after position weights, source-row pointer |
| `TRADE_LOG_COLUMN_EXAMPLES` (optional) | Ray | Override default example values in the column-dictionary expander when pair's schema differs |

### Required data artifacts

| File | Producer | Schema |
|---|---|---|
| `results/{pair_id}/winner_trades_broker_style.csv` | Evan (pipeline) | `trade_date, side, instrument, quantity_pct, price, notional_usd, commission_bps, commission_usd, cum_pnl_pct, reason` |
| `results/{pair_id}/winner_trade_log.csv` | Evan (pipeline) | existing position-log schema (one row per weight change) |

### Severity for missing-artifact cases (per APP-SEV1)

| Condition | Severity | Behaviour |
|---|---|---|
| Both CSVs missing | L1 | `st.error`, short-circuit Trading History block, continue to Confidence tab |
| Broker-style CSV missing, position log present | L2 | `st.info` explaining gap + Plain English, render position-log pane only |
| Broker-style CSV present, position log missing | L2 | `st.info` + render broker-style pane only |
| Either CSV unreadable / malformed | L2 | `st.warning` with exception class + render the healthy pane |

### Ownership split

| Layer | Owner | Responsibility |
|---|---|---|
| Structure (section order, widget layout, dual downloads, preview) | **Ace** | Extend `render_strategy_page` to call a new `_render_trade_log_block(pair_id, config)` helper |
| Narrative defaults (disclosure paragraph, two-file explanation, column glossary copy) | **Ray** | Author canonical defaults once in `page_templates.py`; pair overrides optional |
| Pair-specific concrete example (`TRADE_LOG_EXAMPLE_MD`) | **Ray** | Add to every pair config |
| Broker-style CSV production | **Evan** (pipeline), **Dana** (data plumbing) | Ensure `winner_trades_broker_style.csv` is emitted with `comment="#"` header for every pair that runs the tournament |
| QA gate | **Quincy** | Add a checklist item: "Strategy page Trading History block shows two download buttons + preview + all five narrative scaffold items" |

### Migration protocol

1. **Template upgrade (Ace).** Add `_render_trade_log_block` helper to `page_templates.py`. Wire it into `render_strategy_page` replacing the current ll. 1097–1115 block. Add config anchors.
2. **Narrative canon (Ray).** Author canonical defaults for items (a)–(d) in the template. Add `TRADE_LOG_EXAMPLE_MD` to each existing pair config (`hy_ig_spy_config.py`, `indpro_xlp_config.py`, `umcsent_xlv_config.py`).
3. **Data backfill (Evan/Dana).** Produce `winner_trades_broker_style.csv` for `indpro_xlp` and `umcsent_xlv`. `hy_ig_spy` already has it.
4. **QA re-verify (Quincy).** Browser-verify all three template pairs + run the new checklist item.
5. **Sample page decommission (Ace, post-APP-TL1).** Once template parity is proven, migrate `hy_ig_v2_spy` from legacy page to template + rich config, closing BL-APP-PT1-LEGACY for this page. (Decommission step is out of scope for APP-TL1's first land; track as follow-on backlog.)
6. **Legacy pair audit (Ace).** Separate sweep: audit pairs #5–#8 legacy hand-written Strategy pages for the same trade-log richness regression vs Sample; log any additional deltas as follow-on backlog items (not APP-TL1 scope).

---

## 5. Appendix — Exact Line References

- Sample narrative scaffold: `app/pages/9_hy_ig_v2_spy_strategy.py:473-519`
- Sample dual-download block: `app/pages/9_hy_ig_v2_spy_strategy.py:521-608`
- Sample preview: `app/pages/9_hy_ig_v2_spy_strategy.py:610-617`
- Template trade-log block (the regression): `app/components/page_templates.py:1097-1115`
- Template thin wrapper: `app/pages/15_hy_ig_spy_strategy.py:14-17`
- `comment="#"` usage (schema signal): `app/pages/9_hy_ig_v2_spy_strategy.py:548`

---

*End of discovery. No SOP file was edited; no implementation performed. Awaiting Lead decision on whether to author APP-TL1 as-is or adjust.*
