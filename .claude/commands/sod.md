# Start of Day (SOD) Procedure — aig-rlic-plus Project

This is the **project-local SOD** for aig-rlic-plus. It overrides the global `/sod` skill while an agent session operates inside this repo. All SOD behavior for this project is defined here — there is no split between global and project SOD.

Perform these steps at the start of every agent session (Lead's own and every subagent dispatch):

## 1. Confirm identity (MANDATORY FIRST STEP)

- Check the dispatch prompt / compaction summary for an `AGENT_ID:` line (format `AGENT_ID: <role>-<name>`, e.g. `AGENT_ID: viz-vera`).
- If missing, derive from first message convention: `[Dev Alice]` → `dev-alice`.
- If still unclear, STOP and ask the user: "Which agent am I?"

## 2. Re-read global profile (if exists)

```
~/.claude/agents/<role>-<name>/profile.md
~/.claude/agents/<role>-<name>/experience.md
~/.claude/agents/<role>-<name>/memories.md
~/.claude/agents/<role>-<name>/last_seen   (timestamp file — used in step 5)
```

If any are missing, create them after reading your PWS (see `docs/agent-sops/team-coordination.md` §New Agent Onboarding Protocol).

## 3. Re-read project PWS

```
_pws/<role>-<name>/README.md
_pws/<role>-<name>/session-notes.md
_pws/<role>-<name>/outstanding-work.md   (if exists)
```

## 4. Read core project docs (MANDATORY)

- `CLAUDE.md` — project instructions
- `docs/agent-sops/team-coordination.md` — cross-agent contracts (read ALL of it, not just your role's section)
- `docs/agent-sops/<your-role>-agent-sop.md` — your individual SOP
- `docs/team-standards.md` — team-wide conventions (filename, sidecar, palette, handoff contracts)

## 5. Read the SOP changelog since your last session

```
docs/sop-changelog.md
```

Focus on entries since the timestamp in `~/.claude/agents/<role>-<name>/last_seen`. Every entry since that timestamp is a rule that landed while you were away — you must apply it.

After reading, update `last_seen` to current date:
```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > ~/.claude/agents/<role>-<name>/last_seen
```

## 6. Read relevant team status

- `_pws/_team/status-board.md` — recent team activity
- `_pws/_team/user-notes.md` (if exists) — user preferences / stakeholder expectations

## 7. Acknowledge

Report back in 2-3 lines: your identity, the last 2-3 changelog entries you applied, and your first planned action. This acknowledgment is the evidence that SOD was actually performed (not just claimed).

---

## Why this file exists (do not remove)

The global `/sod` skill is generic across all projects. This project has specific SOD requirements (team-standards.md, sop-changelog.md, last_seen file) that don't apply elsewhere. Splitting these between the global skill and project files caused "missed read" failures in the past — agents would execute the global skill without discovering the project-specific extensions. This project-local command is the single authoritative definition: when running inside aig-rlic-plus, this overrides the global `/sod`.

Companion enforcement: `/home/vscode/.claude/hooks/check-agent-sod.sh` is a PreToolUse hook on the Agent tool that verifies every agent dispatch prompt contains a `## SOD Block` acknowledging this procedure. Missing SOD block → warning to Lead.

Cross-references:
- `docs/agent-sops/team-coordination.md` §Mandatory Dispatch Template (SOD block required)
- `docs/team-standards.md` (cross-agent conventions read during step 4)
- `docs/sop-changelog.md` (rules since last_seen, step 5)
