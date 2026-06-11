#!/bin/sh
# preflight_summary.sh — print a compact knowledge + cost summary for preflight.skill.
#
# Python-independent on purpose: the Markdown preflight.skill is primary; this
# helper just prints the same SESSION_PREFLIGHT facts so any agent (or a human)
# can see the inventory + cost posture without the optional gabbe CLI.
#
# Usage:  sh agents/scripts/preflight_summary.sh [KIT_ROOT]
#   KIT_ROOT defaults to the directory two levels up from this script (repo root).

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
KIT_ROOT=${1:-$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)}
AGENTS_DIR="$KIT_ROOT/agents"
MEM_DIR="$AGENTS_DIR/memory"

count() { find "$1" -name "$2" 2>/dev/null | wc -l | tr -d ' '; }

echo "## SESSION_PREFLIGHT (summary)"
echo ""

echo "### Inventory"
echo "- Skills:    $(count "$AGENTS_DIR/skills" '*.skill.md')"
echo "- Guides:    $(count "$AGENTS_DIR/guides" '*.md')"
echo "- Templates: $(count "$AGENTS_DIR/templates" '*')"
echo "- Personas:  $(count "$AGENTS_DIR/personas" '*.md')"
echo ""

echo "### Cost posture"
# Autonomy: project/gabbe.config.json wins, then env, else default hybrid.
AUTONOMY="hybrid"
CFG="$KIT_ROOT/project/gabbe.config.json"
if [ -f "$CFG" ]; then
    VAL=$(grep -o '"autonomy"[[:space:]]*:[[:space:]]*"[a-z]*"' "$CFG" 2>/dev/null | grep -o '[a-z]*"$' | tr -d '"' || true)
    [ -n "${VAL:-}" ] && AUTONOMY="$VAL"
fi
[ -n "${GABBE_AUTONOMY:-}" ] && AUTONOMY="$GABBE_AUTONOMY"
echo "- Autonomy: $AUTONOMY (ask | auto | hybrid; default hybrid)"
echo "- Budget: markdown-enforced unless the optional gabbe CLI reports live limits"
echo "- Cost levers: prompt-caching, context-budgeting, model-tiering, batching"
echo ""

echo "### Memory headers"
if [ -f "$MEM_DIR/PROJECT_STATE.md" ]; then
    PHASE=$(grep -i -m1 'phase' "$MEM_DIR/PROJECT_STATE.md" 2>/dev/null || true)
    echo "- PROJECT_STATE: ${PHASE:-present}"
else
    echo "- PROJECT_STATE: (none — fresh project)"
fi
if [ -f "$MEM_DIR/CONTINUITY.md" ]; then
    echo "- CONTINUITY: present (read before acting — past failures to avoid)"
else
    echo "- CONTINUITY: (none)"
fi
SNAP_DIR="$MEM_DIR/episodic/SESSION_SNAPSHOT"
if [ -d "$SNAP_DIR" ]; then
    LATEST=$(ls -1t "$SNAP_DIR" 2>/dev/null | head -1 || true)
    echo "- Latest snapshot: ${LATEST:-none}"
fi
echo ""

# New/changed skills vs last preflight (best-effort, stored under memory/).
echo "### New/changed since last preflight"
STAMP="$MEM_DIR/.preflight_skill_count"
NOW=$(count "$AGENTS_DIR/skills" '*.skill.md')
if [ -f "$STAMP" ]; then
    PREV=$(cat "$STAMP" 2>/dev/null || echo 0)
    if [ "$NOW" != "$PREV" ]; then
        echo "- Skill count changed: $PREV -> $NOW (run update-scan.skill to review)"
    else
        echo "- No change in skill count ($NOW)"
    fi
else
    echo "- First preflight (baseline $NOW skills recorded)"
fi
# Record the current count for next time (best-effort; ignore failure on read-only fs).
printf '%s' "$NOW" > "$STAMP" 2>/dev/null || true
echo ""
echo "> Markdown preflight.skill is authoritative; this is a convenience summary."
