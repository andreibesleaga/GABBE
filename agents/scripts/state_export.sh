#!/bin/sh
# state_export.sh — dehydrate GABBE working state into a portable, agent-agnostic
# bundle so the user can continue in ANY other coding agent or LLM.
#
# Produces:
#   STATE_HANDOFF.md          — one self-contained Markdown file (paste into any LLM)
#   gabbe-state-<stamp>.tar.gz — lossless bundle (memory + tasks + config + instructions)
#
# Python-independent on purpose. The Markdown memory IS the state; this just
# packages it. Secrets are never exported (.env and friends are excluded).
#
# Usage:  sh agents/scripts/state_export.sh [KIT_ROOT] [OUT_DIR]

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
KIT_ROOT=${1:-$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)}
OUT_DIR=${2:-$KIT_ROOT}
AGENTS_DIR="$KIT_ROOT/agents"
MEM_DIR="$AGENTS_DIR/memory"

# Timestamp: prefer a real clock, but stay deterministic-friendly if unavailable.
STAMP=$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null || echo "export")
HANDOFF="$OUT_DIR/STATE_HANDOFF.md"
BUNDLE="$OUT_DIR/gabbe-state-$STAMP.tar.gz"

emit_file() {
    # $1 = label, $2 = path
    echo "## $1"
    if [ -f "$2" ]; then
        echo '```markdown'
        cat "$2"
        echo '```'
    else
        echo "_(not present)_"
    fi
    echo ""
}

KIT_VERSION=$(grep -o 'GABBE Kit version: [0-9.]*' "$AGENTS_DIR/CONSTITUTION.md" 2>/dev/null | head -1 | grep -o '[0-9.]*' || echo "unknown")
AUTONOMY="hybrid"
CFG="$KIT_ROOT/project/gabbe.config.json"
if [ -f "$CFG" ]; then
    VAL=$(grep -o '"autonomy"[[:space:]]*:[[:space:]]*"[a-z]*"' "$CFG" 2>/dev/null | grep -o '[a-z]*"$' | tr -d '"' || true)
    [ -n "${VAL:-}" ] && AUTONOMY="$VAL"
fi

# --- 1. STATE_HANDOFF.md (single portable file, any LLM can read) ---
{
    echo "# STATE_HANDOFF — GABBE portable state"
    echo "- Generated: $STAMP   Kit version: $KIT_VERSION   Autonomy: $AUTONOMY"
    echo ""
    echo "## How to continue (any agent or LLM)"
    echo "1. Load agents/AGENTS.md (operating loop) and CONSTITUTION.md (project law)."
    echo "2. Run session-resume.skill, then preflight.skill."
    echo "3. Start from the NEXT ACTION in the RESUME POINTER below."
    echo ""
    emit_file "RESUME POINTER" "$MEM_DIR/RESUME_POINTER.md"
    emit_file "PROJECT STATE" "$MEM_DIR/PROJECT_STATE.md"
    emit_file "CONTINUITY (past failures to avoid)" "$MEM_DIR/CONTINUITY.md"
    emit_file "OPEN TASKS" "$KIT_ROOT/project/TASKS.md"
    SNAP_DIR="$MEM_DIR/episodic/SESSION_SNAPSHOT"
    if [ -d "$SNAP_DIR" ]; then
        LATEST=$(ls -1t "$SNAP_DIR" 2>/dev/null | head -1 || true)
        [ -n "${LATEST:-}" ] && emit_file "LATEST SNAPSHOT ($LATEST)" "$SNAP_DIR/$LATEST"
    fi
} > "$HANDOFF"

# --- 2. Lossless bundle (excludes secrets) ---
# Build a relative file list from KIT_ROOT so the tar is portable.
( cd "$KIT_ROOT" && tar \
    --exclude='*.env' --exclude='.env' --exclude='*secret*' --exclude='*.key' \
    --exclude='.preflight_skill_count' --exclude='.import-backup*' \
    -czf "$BUNDLE" \
    agents/AGENTS.md agents/CONSTITUTION.md \
    agents/memory \
    project/TASKS.md \
    $( [ -f "project/gabbe.config.json" ] && echo project/gabbe.config.json ) \
    2>/dev/null ) || echo "  (bundle: some paths missing; STATE_HANDOFF.md is still complete)"

echo "Dehydrated state:"
echo "  - $HANDOFF   (portable single file — paste into any agent/LLM)"
[ -f "$BUNDLE" ] && echo "  - $BUNDLE   (lossless bundle — import with state_import.sh)"
echo "Next: continue in any agent → run session-resume.skill then preflight.skill."
