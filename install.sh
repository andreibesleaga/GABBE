#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
#
# GABBE bootstrap installer (POSIX sh).
#
#   curl -fsSL https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.sh | sh
#
# Picks the best available installer for your machine:
#   1. Node present  -> `npx --yes gabbe init` (Python-independent path).
#   2. Else python3  -> `python3 scripts/init.py` (the interactive wizard).
#
# It performs no destructive operations: it only runs an installer that copies
# the kit into the CURRENT directory. Pass extra args through to the installer,
# e.g.  `sh install.sh init --agents claude --yes`.

set -eu

PROG="install.sh"

usage() {
  cat <<'EOF'
GABBE bootstrap installer

Usage:
  sh install.sh [installer-args...]

Behavior:
  - If Node is installed, runs:   npx --yes gabbe init [args...]
  - Else if python3 is installed: python3 scripts/init.py
  - Otherwise, prints how to install Node or Python and exits non-zero.

Options:
  --help, -h    Show this help and exit.

Examples:
  sh install.sh init --agents claude,cursor --yes
  curl -fsSL https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.sh | sh
EOF
}

# --help short-circuit (only when it is the first argument).
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

have() {
  command -v "$1" >/dev/null 2>&1
}

# Resolve the directory this script lives in so the Python fallback can find
# scripts/init.py even when invoked from elsewhere. (When piped via curl there
# is no script file; we then rely on PATH / the local checkout's cwd.)
SCRIPT_DIR=""
if [ -n "${0:-}" ] && [ -f "$0" ]; then
  SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
fi

echo "GABBE installer: detecting runtime..."

if have node && have npx; then
  echo "→ Node detected ($(node --version)). Using: npx --yes gabbe init"
  exec npx --yes gabbe init "$@"
fi

if have npx; then
  echo "→ npx detected. Using: npx --yes gabbe init"
  exec npx --yes gabbe init "$@"
fi

if have python3; then
  INIT="scripts/init.py"
  if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/scripts/init.py" ]; then
    INIT="$SCRIPT_DIR/scripts/init.py"
  fi
  if [ -f "$INIT" ]; then
    echo "→ Node not found; python3 detected. Using: python3 $INIT"
    exec python3 "$INIT"
  fi
  echo "→ python3 detected but $INIT was not found."
  echo "  Run this from a GABBE checkout, or install Node and re-run."
  exit 1
fi

echo "Error: neither Node nor python3 was found on PATH." >&2
echo "Install one of the following, then re-run $PROG:" >&2
echo "  - Node.js >= 16   (https://nodejs.org)  then: npx gabbe-kit init" >&2
echo "  - Python >= 3.9   (https://python.org)   then: python3 scripts/init.py" >&2
exit 1
