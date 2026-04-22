#!/bin/bash
# META-AM enforcement: PostToolUse hook on the Agent tool.
# After every Agent tool call, checks whether the dispatched agent updated
# experience.md and memories.md during the dispatch. If not, warns Lead.
# Re-dispatch is NOT auto-triggered (context is lost; recovery must be manual).
#
# Convention: agent dispatch prompts must include a line "AGENT_ID: <role>-<name>"
# so this script can identify which agent's files to check.

set -euo pipefail

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', ''))
except Exception:
    print('')
" 2>/dev/null)

if [ "$TOOL_NAME" != "Agent" ]; then
    exit 0
fi

PROMPT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('prompt', ''))
except Exception:
    print('')
" 2>/dev/null)

# Extract AGENT_ID from prompt (required convention: line starting with "AGENT_ID:")
AGENT_ID=$(echo "$PROMPT" | grep -m1 "^AGENT_ID:" | sed 's/^AGENT_ID:[[:space:]]*//' | tr -d '[:space:]')

if [ -z "$AGENT_ID" ]; then
    # No AGENT_ID found — dispatch did not follow convention; skip silently.
    exit 0
fi

AGENTS_DIR="$HOME/.claude/agents"
EXPERIENCE_FILE="$AGENTS_DIR/$AGENT_ID/experience.md"
MEMORIES_FILE="$AGENTS_DIR/$AGENT_ID/memories.md"

# Files modified within the last 60 minutes are considered updated this session.
THRESHOLD=3600

check_file() {
    local file="$1"
    local label="$2"
    if [ ! -f "$file" ]; then
        echo "⚠  META-AM | $AGENT_ID | MISSING: $label (file does not exist)"
        return 1
    fi
    local mtime now age
    mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
    now=$(date +%s)
    age=$((now - mtime))
    if [ "$age" -gt "$THRESHOLD" ]; then
        local mins=$(( age / 60 ))
        echo "⚠  META-AM | $AGENT_ID | STALE: $label (last modified ${mins}m ago — not updated this dispatch)"
        return 1
    fi
    return 0
}

FAIL=0
check_file "$EXPERIENCE_FILE" "experience.md" || FAIL=1
check_file "$MEMORIES_FILE"   "memories.md"   || FAIL=1

if [ "$FAIL" -eq 1 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "META-AM AUDIT FAIL — $AGENT_ID did not update global profile."
    echo "Context is now lost. Recovery options:"
    echo "  1. Read _pws/$AGENT_ID/session-notes.md + git diff to reconstruct."
    echo "  2. Re-dispatch $AGENT_ID with explicit EOD-only scope."
    echo "  3. Escalate to Quincy (QA-CL3) at next wave closure."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

exit 0
