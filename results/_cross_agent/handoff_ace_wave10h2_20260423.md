# Handoff — Ace → Ray (Wave 10H.2, APP-TL1 structural skeleton)

**Date:** 2026-04-23
**From:** Dev Ace (appdev agent)
**To:** Research Ray (narrative agent)
**Rule:** APP-TL1 (Trade Log Rendering Contract, `docs/agent-sops/appdev-agent-sop.md` line 1155+)
**Discovery ref:** `results/_cross_agent/ace_discovery_trade_log_20260423.md`

## What Ace shipped

Structural implementation of APP-TL1 in `app/components/page_templates.py`. Prose is intentionally stubbed — Ray authors the words.

### 1. New helper `_render_trade_log_block(pair_id, config)`

- **Location:** `app/components/page_templates.py` line **1311**.
- Implements the 9-step fixed render order from APP-TL1:
  1. `### How to Read the Trade Log` heading
  2. Disclosure paragraph (from `_TRADE_LOG_DISCLOSURE_MD` — Ray stub)
  3. Two-file model (from `_TRADE_LOG_TWO_FILE_MODEL_MD` — Ray stub)
  4. Column glossary (from `_TRADE_LOG_COLUMN_GLOSSARY_MD` — Ray stub)
  5. Pair-specific example — reads `config.TRADE_LOG_EXAMPLE_MD` inside `st.container(border=True)`. If empty → APP-SEV1 L3 caption coda.
  6. `#### Download Trading History` sub-heading
  7. `st.expander("How to read this chart")` with 10-row markdown table built from `_TRADE_LOG_COLUMN_DICT_DEFAULTS` (Ray stub). Pair config may override per-key via optional `TRADE_LOG_COLUMN_EXAMPLES: dict[str, str]`.
  8. Two-column `st.columns(2)` layout: left primary broker-style download + `"{N} executions, one row per trade"` caption; right secondary position-log download + `"{N} position-weight change rows"` caption. Widget keys `tl_dl_broker_{pair_id}` / `tl_dl_position_{pair_id}` to prevent collisions.
  9. Always-visible first-10-row preview of broker-style log + explanatory caption.
- APP-SEV1 branching:
  - Both missing → `st.error` + early `return` (L1).
  - One missing → `st.info` on the affected pane + healthy pane renders (L2).
  - Malformed CSV → `st.warning` with exception class (L2).
  - `TRADE_LOG_EXAMPLE_MD` absent → `st.caption` coda (L3).
- Path resolution via `_REPO_ROOT` (APP-PR1).
- Uses `pd.read_csv(broker_path, comment="#")` per APP-TL1 spec for the broker-style file's comment headers.

### 2. Wired into `render_strategy_page()`

- **Call site:** `app/components/page_templates.py` line **1149**.
- The previous inline single-download block (~20 lines) is replaced by a single call: `_render_trade_log_block(pair_id, config)`.

### 3. StrategyConfig fields

Ace did NOT edit any `app/pair_configs/*_config.py`. Rationale from dispatch: each pair's `StrategyConfig` is its own class (not a shared dataclass), and the helper reads new fields via `getattr(config, "TRADE_LOG_EXAMPLE_MD", "")` and `getattr(config, "TRADE_LOG_COLUMN_EXAMPLES", {}) or {}`. This means:

- Nothing breaks without config edits (absence triggers the intentional L3 coda).
- **Ray's action:** add `TRADE_LOG_EXAMPLE_MD` class attribute to:
  - `app/pair_configs/hy_ig_spy_config.py` → `class StrategyConfig` (line 734)
  - `app/pair_configs/indpro_xlp_config.py` → `class StrategyConfig` (line 412)
  - `app/pair_configs/umcsent_xlv_config.py` → create if missing (per dispatch; pair_configs folder currently only has the two above).
- Optional: `TRADE_LOG_COLUMN_EXAMPLES` dict override (only when schema example values differ meaningfully per pair).

## The four `# TODO Ray` markers

All in `app/components/page_templates.py`. Grep anchor: `grep -n "TODO Ray" app/components/page_templates.py`.

| Line | Constant | What Ray writes | Discovery-doc ref |
|---|---|---|---|
| **114** | `_TRADE_LOG_DISCLOSURE_MD` | APP-TL1 step 2 — simulated-vs-real disclosure paragraph. Compliance-critical. | §2.1 |
| **120** | `_TRADE_LOG_TWO_FILE_MODEL_MD` | APP-TL1 step 3 — plain-English contrast between broker-style and researcher position log. | §2.2 |
| **127** | `_TRADE_LOG_COLUMN_GLOSSARY_MD` | APP-TL1 step 4 — bulleted glossary of the 10 canonical broker-style columns. | §2.3 |
| **139** | `_TRADE_LOG_COLUMN_DICT_DEFAULTS` | APP-TL1 step 7 — replace the 10 × `"TODO Ray: meaning"` / `"TODO Ray: example"` strings with canonical values. Keep keys (`trade_date`, `side`, ... `reason`) unchanged. | §2.4 |

Each constant is a bare string / dict literal so a simple `Edit` operation replaces them cleanly.

## Smoke evidence

```
$ python3 app/_smoke_tests/smoke_loader.py hy_ig_v2_spy
# RESULT  passes=15  failures=0

$ python3 app/_smoke_tests/smoke_loader.py hy_ig_spy
# RESULT  passes=6   failures=0
```

Both clean. Strategy page will render with visible `TODO Ray` placeholders until Ray's pass — expected and intentional pre-Ray state.

## Out of scope for Ray (other agents)

- `winner_trades_broker_style.csv` production for `indpro_xlp` / `umcsent_xlv`: **Evan / Dana**.
- Cloud verify: **Quincy**, last in the serial chain.
- Sample legacy-page decommission (`hy_ig_v2_spy`): deferred follow-on (bundled with `BL-APP-PT1-LEGACY`).

## LEAD-DL1 compliance

Ace touched only files on the Ace ownership map: `app/components/page_templates.py` (Ace-structure), the handoff doc (cross-agent scratch), PWS + team status. No pair config edits, no narrative prose edits, no scripts/pipelines touched.
