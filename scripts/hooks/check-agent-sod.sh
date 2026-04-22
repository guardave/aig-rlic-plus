#!/bin/bash
# SOD enforcement: PreToolUse hook on the Agent tool.
# Before every Agent tool dispatch, checks whether the dispatch prompt
# contains an SOD Block referencing the project-local /sod procedure.
# If not, warns Lead so the dispatch can be augmented (or retried).
#
# Convention: agent dispatch prompts MUST include:
#   - "AGENT_ID: <role>-<name>"   (for EOD audit by check-agent-eod.sh)
#   - "## SOD Block"               (for SOD audit by this script)
#
# The SOD block should instruct the agent to run the project-local /sod
# procedure (read team-standards.md, sop-changelog.md since last_seen, etc.)
# before starting work.
#
# Mirrors the pattern of check-agent-eod.sh (PostToolUse EOD audit).

# Lenient: this is a warning-only hook; do not use `set -e` because grep
# returning non-zero (no match) is the normal path, not an error.
set -uo pipefail

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

# Extract AGENT_ID from prompt
AGENT_ID=$(echo "$PROMPT" | grep -m1 "^AGENT_ID:" | sed 's/^AGENT_ID:[[:space:]]*//' | tr -d '[:space:]')

# Check for SOD Block marker (case-insensitive, allows variations)
# Note: guarded with || true because set -e would otherwise exit on grep's no-match
SOD_FOUND=0
if echo "$PROMPT" | grep -qiE "^##[[:space:]]*SOD[[:space:]]*Block|^##[[:space:]]*Start[[:space:]]*of[[:space:]]*Day|Run SOD:|project-local /sod|docs/sop-changelog\.md|docs/team-standards\.md" 2>/dev/null; then
    SOD_FOUND=1
else
    SOD_FOUND=0
fi
# Ensure we reach the warning logic even if grep returned non-zero
true

if [ "$SOD_FOUND" -eq 0 ]; then
    echo "⚠  SOD AUDIT | ${AGENT_ID:-unknown} | MISSING: dispatch prompt has no SOD Block"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Expected: '## SOD Block' section referencing project-local /sod."
    echo "  Impact:   Agent will not re-read team-standards.md or sop-changelog.md."
    echo "  Fix:      Lead should cancel and re-dispatch with SOD block,"
    echo "            OR accept that this dispatch skips SOD (log rationale)."
    echo "  Reference: .claude/commands/sod.md (project-local SOD procedure)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Warn only; do not block. Lead decides whether to proceed.
exit 0
