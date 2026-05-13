# Key Memories — Lead Lesandro

## Lead Discipline (most important — re-read at every SOD)

**LEAD-DL1: Lead never writes to files owned by role agents.** Wave 10H.1 self-correction: I drifted into agent work ("it's faster", "I have the context"); user caught it, reverted 70+ files, asked me to build a durable mechanism. The mechanism is `docs/agent-sops/lead-agent-sop.md` + `lead_delegation_discipline.md` auto-memory. Pre-edit gate on every write: *who owns this file?* If not Lead → dispatch. Exceptions are narrow (emergency, user override, self-revert). "Pragmatic" / "faster" / "small edit" are not exceptions — they are the drift tells.

**Lead-owned write categories ONLY:** `docs/agent-sops/*.md`, `docs/team-standards.md`, `docs/sop-changelog.md`, `docs/relnotes.md`, `docs/pair_execution_history.md`, `docs/backlog.md`, `_pws/_team/*`, `_pws/lead-lesandro/*`, git tags, `.claude/settings.json` (infrastructure, check with user first). Everything else → dispatch.

**Self-audit at wave closure:** `git log --author="Lead Lesandro" --since=<wave-start> --name-only` — every path must be in the Ownership Map's Lead category. Wave 10H.1 final audit: 6 Lead commits, all compliant.

**User principle — SOP-first remediation:** For every issue, first map it to SOP coverage: missing, unclear, present-but-unenforced, or execution failure under an existing rule. Role agents fix their own SOPs before product/artifact remediation. Cross-review catches protocol and consistency issues. Lead reviews global coherence, returns global issues to role owners, performs final review, then runs a token-efficiency pass before any artifact work. Product fixes happen only after the updated SOP system is accepted.

**Token discipline:** Avoid low-signal affirmations and filler such as "Great idea" or ceremonial openings. Spend tokens on decisions, evidence, blockers, ownership, and next actions. Keep shared protocols canonical in one place and cross-reference instead of duplicating prose. **Per user 2026-05-08:** filler-removal applies to ALL agents in ALL responses, not just Lead — instruct in every dispatch.

**Wave-plan acceptance discipline (META-AVD, 2026-05-08):** for any mechanically-auditable wave whose intent includes a removal/retirement/migration component, the wave plan MUST specify BOTH a positive-pattern acceptance check (what should now exist) AND a negative-pattern check (what should no longer exist). Both run by agent post-change, both re-run by Lead at audit, both must match. Positive-only checks confirm the work was attempted but cannot confirm the duplicate it was meant to replace is gone — that's unconditional Layer-3 trust admitted into the audit. BL-SOP-NORMALIZE wave plan (2026-05-08) had positive-only checks; the audit passed only because the agents happened to be careful, not because the verification spec was complete. User caught the gap with: "running their scripts blindly implies unconditional trust on them, correct?" Codified as META-AVD in `team-coordination.md` + `standards.md`.

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

Phase 5 fix-up: PHASE5-F1 + PHASE5-F2 closed.

## Plotly + Streamlit Hard-Won Rules (2026-05-13)

10. **`@st.cache_resource` doesn't watch file mtime.** Editing a chart JSON without restarting Streamlit means the old cached figure is served. Kill + restart the server after every chart JSON change. Took two iterations of user reporting "no change" to internalize.

11. **`overlaying: "y"` is a trap.** When two series have very different ranges (e.g. credit spread 3-13% vs SPY return -55% to 0), Plotly aligns zero lines and clips one series out of the visible plot area entirely. Always use separate vertical `domain` slices for indicator-target pairs.

12. **Single xaxis on a stacked chart puts date labels in the middle.** Plotly renders tick labels at the anchored y-axis position. yaxis with domain [0.43, 1.0] → labels at y=0.43 → inside the chart. Use two synchronised xaxes (`xaxis.matches="x2"`, top hidden). Codified in VIZ-TS1.

13. **Cross-panel shapes must be duplicated.** A shape with `yref="paper"` works only if you literally want it spanning the full paper. For panel-bounded shapes (NBER recession, peak stress), write two: one with `xref="x", yref="y domain"` and one with `xref="x2", yref="y2 domain"`.

14. **Lessons-learned only helps if it gets read.** Auto-memory `MEMORY.md` is truncated at 200 lines. The Plotly dual-axis rule had been hit twice before but wasn't anywhere a future agent would consult. Fix: project file in git + CLAUDE.md mandatory-read directive + role SOP rule + cross-reference from page standard. Three orthogonal entry points.

15. **Lead self-verifies via Playwright.** Don't delegate browser verification post-fact to a subagent that already declared completion. Screenshot the actual `.js-plotly-plot` elements directly using `scroll_into_view_if_needed` — `window.scrollTo` doesn't work reliably through the Streamlit iframe.
