# Number-provenance gate (v5.3): SOP and disclosed residuals

`scripts/gate_number_provenance.py` renders every page of each schema-1.3 pair and checks that every number a
reader sees comes from a current artifact of that pair. Status: **closed at v5.3** (Codex accepted d5d89e04;
4eae1e5b adds the bootstrap token to chart records). Reopen only for a new class of defect.

```bash
python scripts/gate_number_provenance.py                 # every pair with winner_summary 1.3.x
python scripts/gate_number_provenance.py unrate_spy      # one pair
```

## What each surface must satisfy

| Surface | Rule |
|---|---|
| Prose, runtime charts, unsourced tables | Every number carries a provenance tag (`components/provenance` loaders, `field_text`, `span_years`, ...), is part of an allowlisted descriptive phrase, or is a definition bound to its own spec code. Anything else fails as `UNTAGGED-TEMPLATE`. There is no value-matching fallback. |
| Sourced tables (`table_source`) | Every row is ONE row of a current source file. Each numeric cell is checked against the single source column its displayed column is bound to. A percent display may show x100 only of a ratio-kind column. A numeric cell in an unbound column fails. |
| Derived table columns | Only checker-owned rank rules (`RANK_RULES`: `is_rank` from `is_sharpe`, `oos_rank` from `oos_sharpe`). The checker recomputes the rank. `None` or any other column fails. |
| Chart files | A provenance record in `output/charts/<pair>/chart_provenance.json` that is current: unchanged chart file, current run tag, every recorded input present with the recorded hash, and the record made under the producer bootstrap. |
| Numeric leaves | Every artifact leaf a page formats has a declared kind in `provenance_units.json`. Its value must fit the kind. Only ratio kinds may be shown x100. |

## Producer SOP

1. **Charts.** Produce a chart only by running its producer script (`python scripts/generate_charts_<pair>.py`, the pair
   pipeline, `generate_lead_charts.py`, `viz_cp_retro_apply.py`).
   - A repo script that imports `chart_provenance` re-executes itself through `scripts/_cp_boot.py`. The boot installs
     the read recorder before any script code runs, and the record carries `recorder: entry-point:scripts/_cp_boot.py`.
   - A record made any other way (an interactive session, a notebook, a script outside `scripts/`) is rejected. Regenerate the chart by running its producer.
2. **Tables.** Wrap a displayed table in `table_source(df, <source path>[#json pointer], columns={...}, derived={...})`.
   - Name every displayed column whose header is not the source column's name in `columns=`. For example
     `"OOS Return": "oos_ann_return"`. A header like "OOS Sharpe" binds to `oos_sharpe` by itself.
   - A cell the template composes with a number must come from a mapped column, or carry no digits. The buy-and-hold row's turnover reads "none (held)" for this reason.
3. **Template text.** Format result numbers from tagged loaders only. Never hand-type a result into a template string.
4. **New artifact leaves.** Add a kind rule to `provenance_units.json` before a page shows the leaf. The gate fails a numeric leaf whose kind is `unknown` or whose value is inconsistent with its kind.
5. **Allowlist.** `number_provenance_allowlist.json` is for descriptive constants only: template layout, methodology conventions, definitions, citations. Never put a result number there.

## Disclosed residuals (accepted; not checked by the gate)

1. **Sign words.** A number is checked with its sign, but sign carried by words is not parsed: "minus", "down",
   "pp lower", accounting parentheses `(0.25)`. Prose such as "down 0.25" next to a tagged +0.25
   passes. Accepted by Lead ruling (Codex L2v4 onward).
2. **Boot flag.** The bootstrap token proves the recorder ran from the entry point. It is not tamper-proof:
   - A script that sets `sys._aig_cp_booted` itself before reading data, or a hand-edited manifest, defeats it.
   - That is deliberate falsification, not an accident. Committed manifests and producer code are reviewed.
3. **Plotly raw numeric arrays.** Charts built at render time have every visible string checked:
   - titles, axis and colorbar titles, tick text, prefixes and suffixes;
   - annotations, shape labels, legend and trace names;
   - text / texttemplate, hover templates, customdata strings, table-trace strings.
   The raw numeric data arrays (`x`, `y`, `z`, `values`) are not checked. Chart *files* are covered by their provenance record instead: inputs and freshness, not the correctness of the producer's arithmetic.
4. **Allowlisted descriptive phrases.** `number_provenance_allowlist.json` entries are matched by regex and their numbers are not tagged:
   - `portal_progress`, `grey_zone_band`, `bibliographic_citation`, `trade_log_definitions`;
   - `page_structure`, `rule_mechanics`, `cost_convention`, `threshold_rule_wording`;
   - `signal_label`, `series_definition`, `recession_names`.

   Each entry states its reason. The gate prints how many tokens each pair accepts this way.
   - A citation entry blanks the whole reference: author(s) (year), title, *journal*, volume(issue), pages. So a number inside a cited title is not checked.
5. **Provenance records prove reads, not use.** A record shows which inputs the producer process read and that they are unchanged. It does not prove the producer code used them correctly; producer code is reviewed code. A record may also list more inputs than the chart uses (everything the process read under `data/` or `results/<pair>/`). That is conservative: it can only make a chart look stale, never fresh.
6. **Native reads.** The recorder sees Python `open()` (audit hook) and `pandas.read_parquet`. Other native readers that bypass `open()` are captured only when the producer declares them as sources.
7. **Definitions.** Keyed definitions and categorical labels bind to their own code's spec parameters. Unbound methodology tokens are reported with their measured random-token acceptance (printed per pair). They are bounded, not zero.

## History

| Version | Commit | Change |
|---|---|---|
| v1 | e9ebba18 | Structured-prose layer 2: every rendered number must resolve to the pair's artifacts (value matching) |
| v2 | 31908bd0 | Provenance sentinels at render; authored numbers carry their source |
| v2.1 | a1f125aa | Codex L2v2 F1-F11: no self-minted tags, confined sources, charts, tables, units |
| v4 | 5f94fb92, 8cbe297f | Codex L2v3 N1-N5; headline numbers tagged; definition pool restricted to spec/manifest/registry |
| v5 | 6a1eed64 | Chart and table provenance (records, row-bound tables); true residuals measured (QA L2v4) |
| v5.1 | 8304c14a, 79b928bf, fbc0fa1b | Shared-template result numbers tagged; records verifiable from a fresh clone |
| v5.2 | baa70dc1 | Codex L2v5.1 V51-1..7: no value matching at all; ratio-only x100; verified ranks; declared inputs must exist |
| v5.3 | d5d89e04, 4eae1e5b | Codex L2v5.2 V52-1..4: recorder at the process entry point plus bootstrap token; column-bound table cells; checker-owned rank; author-and-year citations. Codex ACCEPT. |
