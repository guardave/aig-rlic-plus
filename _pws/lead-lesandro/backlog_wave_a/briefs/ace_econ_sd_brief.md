[App Dev Ace] — one-shot Mode-3 dispatch — backlog BL-ECON-SD-PORTAL

You are App Dev Ace. Resolve persona via `./AGENTS.md`: read `~/.claude/CLAUDE.md`, `./CLAUDE.md`, SOP `docs/agent-sops/appdev-agent-sop.md`, and `~/.claude/agents/appdev-ace/`. Lead Lesandro (Claude) is manager + sole checker.

## Task — BL-ECON-SD-PORTAL (user-facing jargon cleanup)
The internal econometrics code `(ECON-SD)` leaks into user-facing "Scope discipline" prose in active pair configs. Strip the internal code; keep the prose plain English. Match the reference cleanup already done for gold_copper.

### Reference (already clean — do NOT edit, just mirror its style)
`app/pair_configs/gold_copper_xli_config.py:1031` reads:
`*Scope discipline.* This analysis keeps the trading signal narrow: only the gold/copper ratio and its transformations are in-scope primary signals.`
Note: it says `*Scope discipline.*` — NO `(ECON-SD)` parenthetical.

### Files to fix (10 instances across 6 ACTIVE configs)
- `app/pair_configs/indpro_spy_config.py` (lines ~131, ~660)
- `app/pair_configs/indpro_xlp_config.py` (line ~626)
- `app/pair_configs/permit_spy_config.py` (lines ~144, ~782)
- `app/pair_configs/umcsent_xlv_config.py` (lines ~151, ~638)
- `app/pair_configs/vix_vix3m_spy_config.py` (lines ~184, ~545)
- `app/pair_configs/hy_ig_spy_config.py` (line ~879)

### The change
In each instance, change `*Scope discipline (ECON-SD).*` → `*Scope discipline.*`. That is the only required edit — the surrounding sentence ("Only INDPRO and SPY are in-scope primary signals." etc.) is already plain English and must be preserved verbatim. Do a final grep to confirm ZERO remaining `ECON-SD` tokens in `app/pair_configs/` (the frozen exemption below is in `app/pages/`, not configs, so configs should be fully clean).

## BINDING exemption
- **Frozen Sample `hy_ig_v2_spy` is UNTOUCHABLE.** Do NOT edit `app/pages/9_hy_ig_v2_spy_methodology.py` or any `hy_ig_v2` artifact. It keeps its `(ECON-SD)` text. (feedback_sample_frozen.)
- Do NOT touch any other pair's logic, charts, or data. Prose-token edit only.

## Gates
- META-CMP pre-commit gates must pass (T1.1 schema, T1.2 loader smoke, T1.3 filename, T2 chart completeness). Run `git commit` (the hook runs them); if any fail, fix at source.
- Commit your edits with a clear message referencing BL-ECON-SD-PORTAL. Author: App Dev Ace.

## Output
- Print `ACE DONE` at line start when finished, with the list of files changed + the confirming grep result (should show only the frozen hy_ig_v2 page, if anything). Or `ACE BLOCKED: <reason>`.

Begin now.
