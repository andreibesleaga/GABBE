#!/bin/sh
# state_import.sh — hydrate GABBE working state from a portable bundle produced by
# state_export.sh, so work continues in THIS agent exactly where another left off.
#
# Safe by default: extracts to a staging dir and reports what would change. Pass
# --apply to actually merge into the project. Never silently overwrites newer
# local state — conflicts are surfaced for the human/agent to resolve.
#
# Usage:
#   sh agents/scripts/state_import.sh gabbe-state-<stamp>.tar.gz [KIT_ROOT]          # dry-run
#   sh agents/scripts/state_import.sh --apply gabbe-state-<stamp>.tar.gz [KIT_ROOT]  # merge

set -eu

APPLY=0
if [ "${1:-}" = "--apply" ]; then APPLY=1; shift; fi

BUNDLE=${1:?usage: state_import.sh [--apply] <bundle.tar.gz> [KIT_ROOT]}
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
KIT_ROOT=${2:-$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)}

[ -f "$BUNDLE" ] || { echo "ERROR: bundle not found: $BUNDLE" >&2; exit 1; }

# mktemp must succeed — a predictable fixed fallback (/tmp/gabbe-import-stage) is a
# symlink/pre-seed target an attacker could exploit, then rm -rf would follow it.
# Use an explicit template: bare `mktemp -d` is non-portable under BSD/macOS sh,
# which requires a template (the XXXXXX keeps the dir name unpredictable).
STAGE=$(mktemp -d "${TMPDIR:-/tmp}/gabbe-import.XXXXXX") || { echo "ERROR: mktemp failed; refusing to use a predictable temp dir." >&2; exit 1; }

# Fail the link/path checks if any stage of the pipeline errors (e.g. corrupt archive).
set -o pipefail 2>/dev/null || true

# The bundle is untrusted input. Reject any member with an absolute path or a
# ".." traversal component BEFORE extracting, so a crafted archive cannot write
# outside $STAGE. (GNU tar's --no-absolute-names is not portable, so validate.)
if tar -tzf "$BUNDLE" | grep -qE '^/|(^|/)\.\.(/|$)'; then
    echo "ERROR: archive contains unsafe paths (absolute or '..'); refusing to extract." >&2
    rm -rf "$STAGE"
    exit 1
fi
# Reject symlink/hardlink members too: a link member plus a write-through member
# can redirect a write outside $STAGE (matches the Python extractor's guard). In
# tar's verbose listing the type char is the first column (l=symlink, h=hardlink).
if tar -tvzf "$BUNDLE" 2>/dev/null | grep -qE '^[lh]'; then
    echo "ERROR: archive contains symlink/hardlink members; refusing to extract." >&2
    rm -rf "$STAGE"
    exit 1
fi
# --no-same-owner/--no-same-permissions: never honor a crafted archive's uid/gid or
# setuid bits (matters if ever run as root); the Python extractor is the safer model.
tar --no-same-owner --no-same-permissions -xzf "$BUNDLE" -C "$STAGE"

echo "Staged bundle contents:"
( cd "$STAGE" && find . -type f | sed 's/^/  /' | head -60 )
echo ""

# Integrity hint: warn if instruction files differ (must be human-reviewed, not auto-clobbered).
for f in agents/AGENTS.md agents/CONSTITUTION.md; do
    if [ -f "$STAGE/$f" ] && [ -f "$KIT_ROOT/$f" ]; then
        if ! cmp -s "$STAGE/$f" "$KIT_ROOT/$f"; then
            echo "  [REVIEW] $f differs from local — instruction files are NOT auto-overwritten."
        fi
    fi
done

if [ "$APPLY" -eq 0 ]; then
    echo ""
    echo "Dry run. Re-run with --apply to merge memory + tasks + config into the project."
    echo "  sh agents/scripts/state_import.sh --apply $BUNDLE"
    echo "Staging dir: $STAGE"
    exit 0
fi

# --apply: merge memory/tasks/config. Memory is additive; back up anything replaced.
BACKUP="$KIT_ROOT/agents/memory/.import-backup-$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null || echo bak)"
copy_in() {
    # $1 = relative path under bundle/project
    SRC="$STAGE/$1"; DST="$KIT_ROOT/$1"
    [ -e "$SRC" ] || return 0
    if [ -e "$DST" ] && ! cmp -s "$SRC" "$DST" 2>/dev/null; then
        mkdir -p "$BACKUP/$(dirname "$1")"
        cp -R "$DST" "$BACKUP/$1" 2>/dev/null || true
        echo "  backed up existing $1 -> $BACKUP/$1"
    fi
    mkdir -p "$(dirname "$DST")"
    cp -R "$SRC" "$DST"
    echo "  imported $1"
}

# Merge the memory tree and task/config; leave AGENTS/CONSTITUTION to human review.
( cd "$STAGE/agents/memory" 2>/dev/null && find . -type f | while read -r rel; do
    copy_in "agents/memory/${rel#./}"
done ) || true
copy_in "project/TASKS.md"
copy_in "project/gabbe.config.json"

echo ""
echo "Hydrated. Now run session-resume.skill then preflight.skill to continue from NEXT ACTION."
[ -d "$BACKUP" ] && echo "Replaced files were backed up under: $BACKUP"
