---
name: codex
description: >-
  Drive an OpenAI Codex CLI as a worker Claude controls — send prompts, detect
  completion, read back results. Use for Mode-3/4/5 maker dispatch and any task
  delegated to Codex in this project. ADAPTED for the aig-rlic-plus nested
  devcontainer: every invocation uses --dangerously-bypass-approvals-and-sandbox,
  completion is detected via line-anchored sentinel markers (monitor script is a
  backstop), logs go under temp/ or _pws/, and briefs resolve persona via
  ./AGENTS.md.
---

# Codex Skill — Cookbook (aig-rlic-plus)

Spin up an OpenAI Codex CLI as a worker that Claude (Lead) drives: send prompts,
detect when it's done, read results. Two modes — pick before you start.

> **Project context.** This skill encodes Mode-3/4/5 maker dispatch under the
> project's work model (LEAD-WM1) and delegation discipline (LEAD-DL1): Codex
> makers do the work, **Lead stays the sole checker**, and every maker resolves
> its persona via `./AGENTS.md`. It is intentionally project-scoped — the
> environment facts and SOPs below do not apply outside this repo.

> **Environment fact (binding).** This repo runs inside a nested devcontainer.
> `bwrap` fails, so **every** `codex` / `codex exec` call MUST pass
> `--dangerously-bypass-approvals-and-sandbox` (the devcontainer is already the
> external sandbox). `~/.codex/config.toml` `trust_level="trusted"` relaxes
> approval prompts only — it does NOT fix the sandbox. Omitting the flag is the
> #1 cause of a dead pane here.

## 0. Prereqs
- `codex` CLI installed and logged in: `codex exec --dangerously-bypass-approvals-and-sandbox 'say hi'` works.
- `tmux` installed (session mode): `command -v tmux`.
- This skill present (`/codex` or "use the codex skill").
- Watch the Codex **usage quota** — a wave can stall mid-pipeline with "You've
  hit your usage limit … try again at <time>". Fallback: wait, or Lead-assembles
  the blocked stage with explicit user authorization (precedent: pair #22 Ace).

## Mode picker
- **One-shot** — a single self-contained prompt; run it, read the log, done.
- **Session** — multi-turn, audit/fix loops, or context must persist. Detached tmux session.
  Rule of thumb: if the same task needs a 2nd prompt, you should've used a session.

---

## Recipe A — One-shot (our Mode-3 per-pane pattern)
```bash
mkdir -p temp/codex-logs
codex exec --dangerously-bypass-approvals-and-sandbox -m <model> '<self-contained prompt>' \
  > temp/codex-logs/<label>.log 2>&1
```
- Run in background (Bash tool `run_in_background: true`) for long prompts.
- Batch independent items with `xargs -P <n>`.

The Mode-3 maker form (one pane per role), with a `tee` log and marker:
```bash
tmux send-keys -t <session> "codex exec --dangerously-bypass-approvals-and-sandbox \
  'Read the brief at <PATH> and execute it fully; resolve persona via ./AGENTS.md' \
  2>&1 | tee _pws/lead-lesandro/<wave>/<role>_pane.log" C-m
```
Completion via line-anchored marker grep (Hard rule 4), NOT idle-watching.

---

## Recipe B — Session (interactive REPL, persistent context)

### 1. Pick a label & check it's free
```bash
tmux has-session -t codex-<label> 2>/dev/null && echo EXISTS || echo FREE
```

### 2. Create the detached session + logging
```bash
tmux new-session -d -s codex-<label> -x 220 -y 50
LOG=temp/codex-logs/codex-<label>.log   # or _pws/<role>/<wave>/sessions/...
mkdir -p "$(dirname "$LOG")"
tmux pipe-pane -t codex-<label> -O "cat >> '$LOG'"
```

### 3. Start the CLI WITH the bypass flag, confirm startup
```bash
tmux send-keys -t codex-<label> 'codex --dangerously-bypass-approvals-and-sandbox' Enter
sleep 3
tmux capture-pane -t codex-<label> -p     # check for a startup/sandbox error
```

### 4. Send a prompt — text and Enter are SEPARATE calls
```bash
tmux send-keys -t codex-<label> -l "<short prompt>"
tmux capture-pane -t codex-<label> -p | tail -n 5    # confirm text visible
tmux send-keys -t codex-<label> Enter
tmux capture-pane -t codex-<label> -p | tail -n 5    # confirm submission
```

### 5. Wait for completion — PRIMARY: marker; BACKSTOP: monitor
**Primary (maker dispatch):** instruct the worker to print a line-anchored
sentinel; poll the log for it:
```bash
grep -qE "^<ROLE> (DONE|BLOCKED)" "$LOG"
```
**Backstop (free-form work without a marker):**
```bash
SESSION=codex-<label> bash "$CLAUDE_SKILL_DIR/reference/monitor-script.sh"
```
- Launch with Bash tool `run_in_background: true`. Prints `IDLE`/`TIMEOUT`/`SESSION GONE`.
- One monitor at a time; don't poll the pane manually while it runs.
- Tune for long stages: `MAX_TICKS=240` (20min), `IDLE_TICKS=3` (15s). Defaults
  120/2 (10min/10s) are too short/aggressive for tournament & chart batteries.

### 6. Read results
```bash
tmux capture-pane -t codex-<label> -p -S -200 | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g'
```

### 7. Kill only when fully done
```bash
tmux kill-session -t codex-<label>
```

---

## Recipe C — Long prompt / brief (>~500 chars)
Don't paste big briefs into the terminal — they fragment. Write a file, send a pointer.
```bash
cat > _pws/lead-lesandro/<wave>/briefs/<role>_brief.md <<'EOF'
[Role Name] — <work packet>
Resolve persona via ./AGENTS.md (read ~/.claude/CLAUDE.md, ./CLAUDE.md, your SOP
docs/agent-sops/<role>-agent-sop.md, and ~/.agents/profiles/<role>-<name>/).
Print `<ROLE> DONE` at line start when finished, or `<ROLE> BLOCKED: <reason>`.
<the brief>
EOF
tmux send-keys -t codex-<label> -l "Read the brief at <PATH> and follow it verbatim."
tmux capture-pane -t codex-<label> -p | tail -n 5
tmux send-keys -t codex-<label> Enter
```

---

## Hard rules (the ones that bite)
1. **Always pass `--dangerously-bypass-approvals-and-sandbox`** — bare `codex`/`codex exec` fails the bwrap sandbox in this nested devcontainer.
2. Never bundle prompt text + Enter in one `send-keys`. Separate calls.
3. Prompts >~500 chars → file + pointer (Recipe C).
4. **Completion detection: line-anchored markers are PRIMARY** (`grep -qE "^ROLE (DONE|BLOCKED)"`). Un-anchored grep false-positives on the echoed brief text. `monitor-script.sh` idle-detection is a BACKSTOP only — "idle" ≠ "succeeded", and a maker reasoning silently can trip it. **Gate the next maker on pane-return-to-bash-prompt**, not just the marker line (the marker can print while Codex is still committing post-DONE).
5. Monitor runs `run_in_background: true`, one at a time, never foreground.
6. Reuse one session across related prompts; don't open a fresh one each turn.
7. Model names go stale — probe first: `codex exec --dangerously-bypass-approvals-and-sandbox -m <model> 'say hi'`. Omit `-m` for the configured default.
8. Don't kill a session mid-workstream.
9. **Lead stays the checker.** Maker "DONE + gates pass" is necessary, not sufficient — Lead verifies between stages (LEAD-DL1, GATE-CMP1). Keep makers in their lanes; route gaps to the field's owner. Logs go under `temp/` or `_pws/` (NOT `tmp/`) per project CLAUDE.md.

## Attach / detach cheatsheet
```
Attach:  tmux attach -t codex-<label>
Detach:  Ctrl-b then d
Scroll:  Ctrl-b then [   (q to exit)
Kill:    tmux kill-session -t codex-<label>
```

## See also
- Project memory `reference_codex_tmux_dispatch` — the Mode-3 dispatch recipe this skill encodes.
- `docs/agent-sops/team-coordination.md` — handoff formats, completeness gate.
- `docs/agent-sops/lead-agent-sop.md` — LEAD-WM1 work model, LEAD-DL1 delegation discipline.
- `./AGENTS.md` — persona role-resolver every maker reads.
