# AGENTS.md — Codex entry point for AIG-RLIC+

> **This file is a pointer, not a source.** It carries no persona or protocol text of
> its own. Everything authoritative lives in the Claude-side files referenced below;
> read those each run so nothing here can drift from them.

You are operating in the **AIG-RLIC+** project as a member of a multi-agent team that
also runs on the `claude` CLI. When dispatched via Codex (work Modes 3, 4, 5 in
`docs/agent-sops/lead-agent-sop.md` §LEAD-WM1), adopt the persona you are assigned and
follow the same SOPs a Claude agent would.

## Before acting, read (in order)

1. **Global protocol** — `~/.claude/CLAUDE.md` (cross-project agent identity protocol,
   general rules, memory rules). Also reachable via the global `~/.codex/AGENTS.md` pointer.
2. **Project instructions** — `./CLAUDE.md` (project persona, toolkit, conventions,
   deployment, verification gates).
3. **Your role SOP** — derive your role from the dispatch brief's identity tag
   (e.g. `[Lead Lesandro]`, `[Econ Evan]`, `[Data Dana]`, `[Viz Vera]`,
   `[Research Ray]`, `[AppDev Ace]`, `[QA Quincy]`) and read the matching SOP under
   `docs/agent-sops/`:
   - Lead → `lead-agent-sop.md`
   - Econometrics → `econometrics-agent-sop.md`
   - Data → `data-agent-sop.md`
   - Visualization → `visualization-agent-sop.md`
   - Research → `research-agent-sop.md`
   - App Dev → `appdev-agent-sop.md`
   - QA → `qa-agent-sop.md`
   - plus the cross-cutting `docs/agent-sops/team-coordination.md` and `docs/team-standards.md` (note: `team-standards.md` is at `docs/`, not under `docs/agent-sops/`).
4. **Your persona profile** — `~/.agents/profiles/<role>-<name>/` (`profile.md`,
   `experience.md`, `memories.md`, and `projects/aig-rlic-plus.md` if present).

## Binding regardless of model family or dispatch mechanism

The dispatch brief states which work mode is live. Whatever your role, these bind
identically to how they bind for a Claude agent:

- Handoff schemas (`*-HZE1`), the completeness gates (`GATE-CMP1` / META-CMP — run via
  the repo pre-commit hook), and `LEAD-DOM1` rendered-DOM verification.
- The delegation, quality-focus, merge-authority, and commit-push rules
  (`LEAD-DL1`, `LEAD-QF1`, `LEAD-MA1`, `META-CPD`) when you wear the Lead hat.
- The "never hot-patch — fix the SOP/producer first" discipline (META-NMF / SOP-first).

If anything here conflicts with the canonical files above, the canonical files win —
report the discrepancy rather than acting on this pointer.
