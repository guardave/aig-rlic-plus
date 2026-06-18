#!/usr/bin/env bash
# Codex session completion monitor (pane-quiescence detector).
#
# Watches a detached tmux session's pane; prints IDLE when output goes
# stable, TIMEOUT on the cap, SESSION GONE if the pane vanishes.
#
# Original logic authored by the user (temp/monitor-script.sh, 2026-06-18).
# Adapted for aig-rlic-plus: thresholds are env-overridable so long maker
# stages (tournament, chart battery) don't trip the default 10-min cap.
#
#   SESSION     tmux session name            (default: codex-label)
#   IDLE_TICKS  stable ticks before IDLE     (default: 2  → 10s)
#   MAX_TICKS   ticks before TIMEOUT         (default: 120 → 10min)
#   TICK_SECS   seconds per tick             (default: 5)
#
# NOTE (aig-rlic-plus SOP): pane-quiescence is a BACKSTOP, not the primary
# completion signal. The primary signal is a line-anchored sentinel the
# maker prints (e.g. `^DANA DONE` / `^DANA BLOCKED`) — grep the tee log for
# that. Idle can false-fire when a maker reasons silently, and "idle" does
# not mean "succeeded". See reference_codex_tmux_dispatch memory.

SESSION=${SESSION:-codex-label}
IDLE_TICKS=${IDLE_TICKS:-2}
MAX_TICKS=${MAX_TICKS:-120}
TICK_SECS=${TICK_SECS:-5}

prev_hash=""
stable_streak=0
seen_change=0
tick=0

while true; do
  tick=$((tick + 1))
  pane=$(tmux capture-pane -t "$SESSION" -p -S -200 2>/dev/null) || {
    echo "SESSION GONE"
    exit 1
  }
  cur_hash=$(printf '%s' "$pane" | md5sum | cut -d' ' -f1)

  if [ -z "$prev_hash" ]; then
    prev_hash="$cur_hash"
  elif [ "$cur_hash" = "$prev_hash" ]; then
    stable_streak=$((stable_streak + 1))
  else
    seen_change=1
    stable_streak=0
    prev_hash="$cur_hash"
  fi

  if [ "$seen_change" -eq 1 ] && [ "$stable_streak" -ge "$IDLE_TICKS" ]; then
    echo "IDLE session finished at ~$((tick * TICK_SECS))s"
    exit 0
  fi

  if [ $((tick % 60)) -eq 0 ]; then
    echo "HEARTBEAT $((tick * TICK_SECS))s elapsed, still working"
  fi

  if [ "$tick" -gt "$MAX_TICKS" ]; then
    echo "TIMEOUT $((MAX_TICKS * TICK_SECS / 60))min"
    exit 2
  fi

  sleep "$TICK_SECS"
done
