# User Notes — stakeholder conventions

Single source of truth for stakeholder-set conventions every agent should
know. Read at every SOD by every role.

## Cloud preview slots

| Slot | URL | What it tracks | Repoint policy |
|---|---|---|---|
| **WIP preview** | `https://aig-rlic-plus-dawodev.streamlit.app/` | Whichever feature branch is in flight | **User repoints** on request — agents do not create new preview apps per branch |
| **Production** | `https://aig-rlic-plus.streamlit.app/` | `main` (auto-deploy with reboot lag) | Stable; never repointed |

**Workflow for branch verification (Quincy, Lead, anyone running cloud sweep):**
1. Push the working branch to `origin`
2. **Signal the user** to repoint the WIP slot: *"Please repoint aig-rlic-plus-dawodev.streamlit.app to <branch>"*
3. Wait for user confirmation (Streamlit Cloud redeploy takes ~60–90s after repoint)
4. Run cloud Track B sweep against the WIP URL
5. After merge to main, verify on **production**, not the WIP slot (the WIP slot still points at the merged branch but production is the source of truth post-merge)

**Decided:** 2026-06-02 (user direction during fix260601_chart_hygiene Wave 3 cloud verify): *"Use https://aig-rlic-plus-dawodev.streamlit.app/ from now on for all branch wip and signal me to repoint at times"*

## Quality standards

### Placeholders are not acceptable user-facing quality

A "chart pending" / "coming soon" / "section incomplete" placeholder on a published page fails three of the four quality dimensions:
- **Completeness** — the page contract claims the section exists
- **Consistency** — other pairs have the section; the gap is user-visible
- **ELI5** — a layman shouldn't have to decide whether incomplete = wrong vs incomplete = unfinished

For any incomplete surface: either **ship complete** or **remove the surface from production**. Don't shim with placeholders.

**Decided:** 2026-06-01 (user direction during fix260601_chart_hygiene Wave 2 scoping discovery).

**Single documented exception:** `BL-PERMIT-CHARTS-EXCEPTION` — `permit_spy`'s 3 missing Strategy-page charts. User has external work in flight; the standard applies to all other pairs uniformly.

### Pre-existing doesn't change reader impact

A defect is a defect if it fails any of correctness / completeness / consistency / ELI5. Provenance is for blame-tracking, not scope. When tempted to defer something because "it predates this work" — apply the 4-dimension test instead.

**Decided:** earlier (fix260526 lessons crystallised in `_pws/lead-lesandro/memories.md`).

## Agent dispatching conventions

### Mode 1 vs Mode 2 (LEAD-WM1)

| Mode | When | Who decides at SOD |
|---|---|---|
| Mode 1: multi-agent, single checker | Default | Lead dispatches role agents; each operates in own SOP |
| Mode 2: single maker, multiple checkers | When the work is tightly coupled in one context (tactical fix, refactor across multiple roles' lanes) | Lead wears role hats sequentially; checker subagents dispatched at the end |

### Mode 2 hat-wearing discipline

When Mode 2 is in play and Lead is authoring an artifact in a role's lane:
- **Before authoring**, open the relevant role SOP and scan for the directly-relevant rule
- This is a **targeted read at hat-wearing time**, NOT a preemptive load of every role SOP at SOD (would waste ~50k+ tokens per session)
- Role-to-SOP mapping (see also `_pws/lead-lesandro/memories.md`):
  - Econometrics / B&H / tournament → `docs/agent-sops/econometrics-agent-sop.md` (Evan)
  - Chart layout / palette / sidecar → `docs/agent-sops/visualization-agent-sop.md` (Vera)
  - Page wiring / config / KPI → `docs/agent-sops/appdev-agent-sop.md` (Ace)
  - Data ingest / schema → `docs/agent-sops/data-agent-sop.md` (Dana)
  - Narrative / glossary → `docs/agent-sops/research-agent-sop.md` (Ray)
  - Cloud verify / QA → `docs/agent-sops/qa-agent-sop.md` (Quincy)

**Decided:** 2026-06-01 (user feedback during fix260601_chart_hygiene Wave 2 scoping: *"If you ask me this, does it mean there is no such knowledge in the context?"* — correctly identifying procedural gap).

## SOP clarity

When an SOP rule prose feels like it's restating the same fact in N different cases, the rule needs tightening. Verbose rules invite hypothetical edge-case questions; tight rules close them by construction.

**Example (decided 2026-06-02):** the 5-case benchmark-selection if-table at `econometrics-agent-sop.md:847` was correct but verbose. Tightened to single sentence (ECON-BM1): *"The pair's target is the buy-and-hold benchmark. No special cases by asset class."* User: *"The logic is too clumsy. The target is taken as the buy-and-hold target. That's it."*
