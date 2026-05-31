# Key Memories — Lead Lesandro

## Lead Discipline (most important — re-read at every SOD)

**LEAD-DL1: Lead never writes to files owned by role agents.** Wave 10H.1 self-correction: I drifted into agent work ("it's faster", "I have the context"); user caught it, reverted 70+ files, asked me to build a durable mechanism. The mechanism is `docs/agent-sops/lead-agent-sop.md` + `lead_delegation_discipline.md` auto-memory. Pre-edit gate on every write: *who owns this file?* If not Lead → dispatch. Exceptions are narrow (emergency, user override, self-revert). "Pragmatic" / "faster" / "small edit" are not exceptions — they are the drift tells.

**Lead-owned write categories ONLY:** `docs/agent-sops/*.md`, `docs/team-standards.md`, `docs/sop-changelog.md`, `docs/relnotes.md`, `docs/pair_execution_history.md`, `docs/backlog.md`, `_pws/_team/*`, `_pws/lead-lesandro/*`, git tags, `.claude/settings.json` (infrastructure, check with user first). Everything else → dispatch.

**Self-audit at wave closure:** `git log --author="Lead Lesandro" --since=<wave-start> --name-only` — every path must be in the Ownership Map's Lead category. Wave 10H.1 final audit: 6 Lead commits, all compliant.

## Confirmed Patterns (high confidence, 3+ pairs)
1. **RoC/momentum signals beat level signals** — every pair (INDPRO, TED, Permits) won with rate-of-change. Stationary transforms predict better.
2. **6-month lead for monthly indicators** — publication lag + economic transmission time. L6 should be default.
3. **Streamlit rendering is fragile** — never use raw HTML divs; always native components + Playwright verification after every change.

## Process Rules Learned
4. **MRA after every pair** — Measure, Review, Adjust. No exceptions.
5. **Deliverables Completeness Gate** — 12-item checklist before MRA. Browser verification ≠ completeness.
6. **Variant families** — when indicator has measurement alternatives, run all in one pipeline, count as 1 priority pair.
7. **Always kill Streamlit before restart** — use port 8501 consistently.
8. **`bool()` cast** needed for numpy booleans before JSON serialization.

## User Preferences (Lesandro)
9. Always use headless browser verification — "Every time."
10. Don't truncate finding text — align cards to tallest instead.
11. Hover hints on direction badges for layman audience.
12. Track token usage including viz stage.
13. Update SOPs immediately when lessons are learned.
14. TED variants = 1 priority pair, not 3.
15. HY-IG (#20) counts in the priority pair total.

---

## fix260531 (2026-05-31) — refactor pattern + Plotly paper-coord gotcha + META-CMP confirmation

7. **Plotly paper coords are plot-area-relative, NOT chart-container-relative.** This caused 6 iterations of caption-layout fixes before settling. Recipe that works: `xref="paper", x=0, xanchor="left", xshift=-margin.l, yshift=CAPTION_Y_SHIFT_PX`. The `xshift = -margin.l` reads each figure's margin and shifts left to chart-container edge. Fixed-pixel xshift breaks on wide-margin charts (subperiod_sharpe l=200 vs rolling l=70). Centering (`x=0.5, xanchor="center"`) sidesteps the issue but was visually rejected by user.

8. **`except Exception: pass` is META-CMP class bug masking.** gold_copper dashboard "—" was caused by a column-name drift (`oos_max_drawdown` vs `max_drawdown`) hitting KeyError → silently swallowed → loader returned None for all metrics → card rendered dashes. Always replace bare except with `except Exception as e: <log to integrity_issues>` so future drift surfaces at next wave closure instead of hiding for weeks.

9. **Refactor pattern that scales: helper module + selective consumer migration.** Five helper modules shipped this session (`_chart_layout`, `_nber`, `_stamp`, `display_names`, `tournament`), each following the recipe: (a) create helper with canonical constants/functions, (b) migrate 2-3 pilot consumers, (c) verify pilot with numeric/visual diff, (d) leave remaining consumers alone, (e) log backlog entry with trigger conditions for bulk migration. This resolves DUP classes incrementally without bulk-migration risk.

10. **Zero-numeric-drift gate for pipeline migrations.** DUP-11 migration on gold_copper used: stash old CSV → run migrated pipeline → compare row-by-row with `(old[col] - new[col]).abs().max()` → require 0.000000 on all stat columns before declaring safe. This is the template for any pipeline refactor where the user is currently seeing the displayed numbers and the refactor must not change them. Applied per-column: `oos_sharpe`, `oos_ann_return`, `oos_max_drawdown`.

11. **Streamlit Cloud production reboot required for `.py` changes.** Auto-redeploy on `git push` is reliable for static assets (chart JSONs, schema files) but unreliable for Python module reloads. Both `narrative.py` reload (mid-branch) and the post-merge production redeploy needed user-side manual reboot (Manage app → Reboot app). Document in any future hand-off: every `.py`-touching merge requires production reboot after push.

12. **The "audit → backlog → ship smallest N → defer rest" pattern (Option B).** When user asked about DUP-11, I offered A/B/C with risk tiers. User picked B (ship helper + migrate 1 pair). This pattern generalises: when faced with a structural refactor that touches many places, offer (A) helper-only zero-migration, (B) helper + 1 pilot migration, (C) full migration with diff gates. B is almost always the right answer — it proves the helper works end-to-end without bulk-migration risk.

---

## fix260526 (2026-05-26 / 2026-05-27) — process lessons crystallised

1. **The deep_inspect canonical "wave clean" gate.** Narrow-marker checks (e.g. "did these 3 fixes land?") are a *fix-confirmation* test, not a *wave-clean* test. For wave-clean, walk every page × every tab × wide error-marker grep. Recipe lives at `temp/fix260526/deep_inspect.py`; the iframe + URL-slug + hydration-polling pattern follows `scripts/cloud_verify.py::get_dom()`. Adopt for any future wave that touches user-rendered surfaces.

2. **"Pre-existing" doesn't change reader impact.** A defect is a defect if it fails any of correctness / completeness / consistency / ELI5. Provenance is for blame-tracking, not scope. When tempted to defer something because "it predates this work" — apply the 4-dim test instead.

3. **Text-vs-data drift is the durable Mode 2 risk.** Three confirmed instances now (gold_copper_xli winner mismatch; indpro_spy Pearson observation; indpro_spy CCF observation backwards). The pattern: narrative authored ahead of or independently of data verification → silent drift. Cure: prose with explicit numeric citations from the source CSV, validated by grep at commit time.

4. **Read existing helpers before writing new ones.** Repeated wins this session: `scripts/cloud_verify.py` (iframe Playwright pattern), `scripts/viz_cp_retro_apply.py` (single place to land Granger/sub-period cross-pair fixes), `scripts/synthesize_broker_trade_log.py` (existing broker-log generator). The team's existing code is usually the right starting point.

5. **Producer reads canonical contracts, not file-order heuristics.** Several chart producers use `valid_strats.iloc[0]` (first row of CSV) to pick the "winner" — incorrect when CSV row order ≠ Sharpe order. The right pattern: read `winner_summary.json` (APP-WS1) with a fallback to `nlargest(1, "oos_sharpe")` if exact match fails (legacy null-fields case). Confirmed broken on indpro_xlp; likely also affects other pairs — schedule audit.

6. **Per-pair component overrides via signal-type discriminators.** When a generic component (`Probability Engine Panel`) is wrong for some pairs, the per-pair config-override route is heavier than discriminating by signal-type semantics (e.g. `_PROBABILITY_PREFIXES` tuple in `probability_engine_panel.py`). The latter scales automatically with new pairs without per-pair edits.
