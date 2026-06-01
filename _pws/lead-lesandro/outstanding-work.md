# Outstanding work — Lead Lesandro

Last updated: 2026-06-01 SOD (fix260526 decommissioned + GH #8 closed).

## Branch state

**`main`** is the active branch. Tip: `aed4ce8` (merge of `fix260531`, 22 commits). `fix260531` branch deleted (local + remote) after production cloud-verify pass.

## Recent closed work (this session — fix260531)

### Comment-log triage (user re-raised after fix260526 falsely closed them)
| # | Result | Commit |
|---|---|---|
| #63 indpro_spy KPI rounding mismatch (+7.6% vs +7.7%) | Aligned all 3 hand-typed strings to +7.6% (matches `_format_ratio_pct` output) | `50c68b8` |
| #64 indpro_spy INDPRO naming | Canonical `INDPRO` in chart titles/axes/legends/prose; cloud-verify caught one leftover hero title (`9cb63e1`) | `50c68b8`, `9cb63e1` |
| #68 indpro_spy Granger colour + leading-direction | `cause = direction.split("->")[0]` fix; new how-to-read annotation | `50c68b8` |

### Cross-pair viz hygiene
| Class | Scope | Commit |
|---|---|---|
| Legend/caption overlap | 60 charts, 10 pairs | `6084999` |
| Right-side vertical legend rollout | 123 charts + 10 generators | `544b77a` |
| X-axis title vs caption layout | 48 charts via `_chart_layout::apply_caption_layout` | `6cb6545`, `97a3456`, `d1be5d7`, `bdff83f`, `7798977`→`23541ad` (reverted center→left), `436af45` |
| subperiod_sharpe axis vs caption | 11 charts | `4a251ec` |
| Caption position via xshift=-margin.l | All captioned charts | `bdff83f`, `23541ad` |
| Font standardisation (title/axis/tick/legend/caption) | 209 charts | `ca985ae` |

### App-layer
| What | Commit |
|---|---|
| Sidebar dynamic (7→11 pairs via `pair_registry`) | `ec59104` |
| Glossary text_input + Material `close` clear-X + CSS via `st-key-glossary_clear` | `90e4b76`, `29290a5`, `792062b` |
| gold_copper_xli dashboard card (was showing "—") | `13a313e`, `2546e69` |

### Refactor — single-source-of-truth modules created
| Module | DUP | Consumers migrated |
|---|---|---|
| `scripts/_chart_layout.py` | X-axis/caption + font sizes | `viz_cp_retro_apply.py` (5 builders) |
| `app/components/display_names.py` | DUP-1 (indicator/target names) | pair_registry, page_templates, sidebar |
| `scripts/_nber.py` | DUP-4 (recession lists) | viz_cp_retro_apply, generate_history_zoom_charts |
| `scripts/_stamp.py` | DUP-15 (utcnow deprecation) | 5 sites (`generate_charts_hy_ig_spy.py`, `pair_pipeline_hy_ig_spy.py` ×2, `generate_history_zoom_charts.py`) |
| `scripts/tournament.py` | DUP-11 (select_winner + bh stats + benchmark row) | `econ_pipeline_gold_copper_xli.py` (closes BL-GC-BH) |

### Audit + backlog
- 3-agent code-review found 17 DUP/divergence classes. All logged as `BL-DUP-1..17` in `docs/backlog.md`.
- 5 SOP rule proposals logged: `BL-APP-NUM1`, `BL-VIZ-NS1`, `BL-VIZ-DC1`, `BL-VIZ-LO1`, `BL-APP-DR1`.
- `BL-GC-BH` opened then closed in same session (proper pipeline-side fix shipped).
- `BL-DUP-11` updated with partial-progress note + 8 remaining pipelines flagged for bulk migration with per-pair numeric-diff gates.

### META-CMP root cause documented
fix260526's W2 commit `3718fc9` listed `#63, #64, #65, #66, #67, #68` in the commit message but the diff only touched `#64, #65, #66, #67`. The commit-vs-claim drift was the bug META-CMP (GH #7) is designed to catch. Documented in `docs/relnotes.md` fix260531 entry.

## Active questions / pending decisions (carried forward)

- **GH #4 close decision** — stakeholder hasn't said yet whether to close or add "Investment Clock" cross-reference.
- **GH #7 META-CMP** — Tier 1+2 forcing functions queued for dedicated SOP-hardening branch. Reinforced by fix260531's discovery that fix260526's W2 commit claimed to close 6 IDs but the diff only touched 4 (#63 / #68 left untouched). META-CMP is the forcing-function class designed to catch that.
- ~~**GH #8 stabilization**~~ — **CLOSED 2026-06-01.** Observation period concluded clean. Branch `fix260526` deleted (local + remote). Preview Streamlit Cloud app `aig-rlic-plus-fix260526.streamlit.app` deleted by user 2026-06-01.
- ~~Indpro_spy #69~~ — closed stakeholder-side 2026-05-30.

## Backlog awaiting a future branch (newly logged this session)

| ID | Class |
|---|---|
| BL-APP-NUM1 | Numeric Format Single Source (helper-injected percent strings) |
| BL-VIZ-NS1 | Indicator Naming Standard (signal_scope-driven display_names) |
| BL-VIZ-DC1 | Bidirectional Chart Colour Discipline |
| BL-VIZ-LO1 | Legend / Caption Vertical Separation |
| BL-APP-DR1 | Dynamic Registry Discipline (forbid hand-list pair_ids) |
| BL-DUP-1..17 | 17 duplication/divergence classes from code-review audit |

3 of the 17 DUP entries partially shipped (DUP-1 / DUP-4 / DUP-15) with the helper modules; the remaining 14 await dedicated branches.

## Untracked working state

- `_pws/qa-queenie/` exists as untracked. Belongs to another agent (Quincy / QA); not mine to commit.
- Many `temp/fix260531/*.png` working screenshots — gitignored, not for commit.

## Broader cross-project tracking

- The "single-source-of-truth helper + migrate consumers" pattern proved high-leverage this session — 5 helper modules shipped, replacing duplicated logic that had drifted across files. Continue applying this pattern.
- Per-pair numeric-diff gate validated on gold_copper_xli (0 drift on 90 strategy rows after migration). Use this template for any future pipeline-refactor work — diff each column max-abs before declaring migration safe.
