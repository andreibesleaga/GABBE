#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Workstream F (visual): record terminal casts of the key GABBE flows as CI
# artifacts / docs assets. Best-effort and non-gating: uses asciinema when
# available to produce .cast files, otherwise falls back to a plain text
# transcript (`script`/tee) so a regenerable demo always exists.
#
# Usage: scripts/record_demos.sh [OUT_DIR]   (default: docs/assets/demos)
set -u

OUT_DIR="${1:-docs/assets/demos}"
mkdir -p "$OUT_DIR"

GABBE_BIN="${GABBE_BIN:-gabbe}"
have() { command -v "$1" >/dev/null 2>&1; }

# Each demo: a label and the command to capture.
record() {
  local name="$1"; shift
  local cmd="$*"
  echo ">> recording: $name -> $cmd"
  if have asciinema; then
    asciinema rec --overwrite --command "$cmd" "$OUT_DIR/$name.cast" || \
      echo "   (asciinema failed for $name; continuing)"
  else
    # Fallback: capture a plain transcript so the demo is still regenerated.
    { echo "\$ $cmd"; eval "$cmd"; } >"$OUT_DIR/$name.txt" 2>&1 || true
  fi
}

# Sandbox so we never touch the caller's project.
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
pushd "$WORK" >/dev/null

record "doctor"       "$GABBE_BIN doctor"
record "version"      "$GABBE_BIN --version"
record "help"         "$GABBE_BIN --help"
# Non-interactive Node install demo (if the kit installer is present).
if have npx; then
  record "npx-install" "npx --yes gabbe-kit init --yes --agents claude"
fi

popd >/dev/null
echo "Demos written to: $OUT_DIR"
if ! have asciinema; then
  echo "note: asciinema not installed — wrote plain-text transcripts (.txt) instead of .cast files."
fi
