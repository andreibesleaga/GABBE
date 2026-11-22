#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
#
# GABBE uninstaller (POSIX sh). Run it in the project that has the kit.
#
#   sh uninstall.sh [--dry-run] [--agents claude,cursor] [--purge] [--dir PATH] [--global]
#
# Reverses a GABBE install from its .gabbe/manifest.json: removes exactly what was
# installed, restores the files that were backed up, and never touches unrelated files.
# Nothing outside the project is changed. The arguments go to the tool that runs, and
# its exit status is this script's exit status.
#
# npx runs from a new, empty temporary folder, never from the project, and gets the project
# as `--dir <absolute path>`: the project's own .npmrc (registry, node-options) and
# node_modules then do not decide what runs. Your own ~/.npmrc still applies.
#
# The tool, in this order:
#   1. Node present   -> `gabbe-kit uninstall` (this package's bin/install.js when it is
#                        next to this script, else `npx --yes gabbe-kit@<this release> uninstall`)
#   2. Python present -> the `gabbe` command of `pip install gabbe`, else that package run
#                        by python3 without the current folder on its path (a `gabbe/`
#                        folder in the project is never imported)
#   3. neither        -> prints the manual steps
# `--global` is a Python CLI option: with it, Python is tried first.
#
# The kit version this script belongs to is the line below (the release gate checks it
# against package.json). GABBE_KIT_VERSION overrides it; `latest` means the newest release.

GABBE_KIT_DEFAULT_VERSION="1.2.0"

set -eu

have() {
  command -v "$1" >/dev/null 2>&1
}

# Where this script lives, when it runs from a file (before any --dir change of folder).
SCRIPT_DIR=""
case "$0" in
  *uninstall.sh)
    if [ -f "$0" ]; then
      SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
    fi
    ;;
esac

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'EOF3'
GABBE uninstaller. Run it in the project that has the kit.

Usage:
  sh uninstall.sh [--dry-run] [--agents claude,cursor] [--purge] [--dir PATH] [--global]

Removes exactly what .gabbe/manifest.json records and restores backed-up files.
Uses Node (npx gabbe-kit@<this release> uninstall --dir <project>, run from a temporary
folder) when present, else the Python CLI (gabbe), else prints the manual steps. The exit
status is that of the tool that ran. --dir PATH names the project (default: the current
folder); a relative PATH is made absolute first.

Environment:
  GABBE_KIT_VERSION   Run that gabbe-kit version (for example 1.2.0) instead of the
                      release this script belongs to. `latest` means the newest
                      release on npm, unpinned.
EOF3
  exit 0
fi

# True for a plain version: 1.2.0 or 1.2.0-rc.1 (shell builtins only: no grep on PATH needed).
kit_version_ok() {
  v=$1
  case "$v" in
    '' | *[!0-9A-Za-z.-]*) return 1 ;;
  esac
  core=${v%%-*}
  pre=""
  case "$v" in
    *-*) pre=${v#*-}; has_pre=1 ;;
    *) has_pre=0 ;;
  esac
  case "$core" in
    '' | *[!0-9.]* | .* | *. | *..*) return 1 ;;
    *.*.*) ;;
    *) return 1 ;;
  esac
  case "${core#*.*.}" in
    *.*) return 1 ;;
  esac
  if [ "$has_pre" -eq 1 ]; then
    case "$pre" in
      '' | *-* | .* | *. | *..*) return 1 ;;
    esac
  fi
  return 0
}

# The npm package spec: the release this script belongs to, unless GABBE_KIT_VERSION
# says otherwise. Only a plain version (1.2.0, 1.2.0-rc.1) or `latest` is accepted, so
# the value cannot add anything to the command.
KIT_VERSION="${GABBE_KIT_VERSION:-$GABBE_KIT_DEFAULT_VERSION}"
KIT_SPEC="gabbe-kit"
if [ "$KIT_VERSION" != "latest" ]; then
  if ! kit_version_ok "$KIT_VERSION"; then
    echo "Error: GABBE_KIT_VERSION must be a version such as 1.2.0, or latest." >&2
    exit 1
  fi
  KIT_SPEC="gabbe-kit@$KIT_VERSION"
fi

# `--dir PATH` names the project folder (made absolute here: npx runs from another folder, and
# the Python CLI acts on the current folder, so it is entered before that tool runs).
# `--global` is only known to the Python CLI.
WANT_PYTHON=0
DIR=""
HAVE_DIR=0
N=$#
while [ "$N" -gt 0 ]; do
  arg=$1
  shift
  N=$((N - 1))
  case "$arg" in
    --dir)
      if [ "$N" -eq 0 ]; then
        echo "uninstall.sh: --dir needs a path" >&2
        exit 2
      fi
      DIR=$1
      HAVE_DIR=1
      shift
      N=$((N - 1))
      ;;
    --dir=*)
      DIR=${arg#--dir=}
      HAVE_DIR=1
      ;;
    --global)
      WANT_PYTHON=1
      set -- "$@" "$arg"
      ;;
    *) set -- "$@" "$arg" ;;
  esac
done
if [ "$HAVE_DIR" -eq 1 ]; then
  PROJECT_ABS=$(CDPATH= cd -- "$DIR" 2>/dev/null && pwd) || {
    echo "uninstall.sh: --dir: there is no such folder: $DIR" >&2
    exit 2
  }
else
  PROJECT_ABS=$(pwd)
fi

run_node() {
  if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/bin/install.js" ]; then
    exec node "$SCRIPT_DIR/bin/install.js" uninstall "$@" --dir "$PROJECT_ABS"
  fi
  # npx reads the .npmrc of the folder it runs in and prefers a gabbe-kit of the same name and
  # version in that folder's node_modules. So it runs from a new empty folder, never from the
  # project, and the project is named with --dir. The version is fixed as well.
  WORK_DIR=$(mktemp -d 2>/dev/null) || {
    echo "Error: could not make a temporary folder (mktemp)." >&2
    exit 1
  }
  trap 'rm -rf -- "$WORK_DIR"' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM HUP
  rc=0
  (cd -- "$WORK_DIR" && npx --yes "$KIT_SPEC" uninstall "$@" --dir "$PROJECT_ABS") || rc=$?
  exit "$rc"
}

# python3 without the project on its import path. A `gabbe/` folder in the current
# project must never be imported (it would run that project's code). Python 3.11+ has
# -P (no current folder on the path; the user site of `pip install --user` stays) and
# -E (no PYTHON* variables). Older Pythons have only -I, which also drops the user site;
# there the `gabbe` command, used first, covers `pip install --user`.
py_isolated() {
  if python3 -E -P -c 'pass' >/dev/null 2>&1; then
    python3 -E -P "$@"
  else
    python3 -I "$@"
  fi
}

# The `gabbe` command of the Python package (its first line names python); the npm
# package has a command of the same name that starts with node.
has_gabbe_command() {
  gabbe_path=$(command -v gabbe 2>/dev/null) || return 1
  [ -f "$gabbe_path" ] || return 1
  IFS= read -r first_line <"$gabbe_path" || [ -n "$first_line" ] || return 1
  case "$first_line" in
    *python*) return 0 ;;
  esac
  return 1
}

run_python() {
  cd -- "$PROJECT_ABS" || exit 2
  if has_gabbe_command; then
    exec gabbe uninstall "$@"
  fi
  rc=0
  py_isolated -m gabbe.main uninstall "$@" || rc=$?
  exit "$rc"
}

has_node() { have node && have npx; }
has_python() {
  has_gabbe_command || { have python3 && py_isolated -c "import gabbe" >/dev/null 2>&1; }
}

if [ "$WANT_PYTHON" -eq 1 ] && has_python; then
  run_python "$@"
fi
if [ "$WANT_PYTHON" -eq 0 ] && has_node; then
  run_node "$@"
fi
if has_python; then
  run_python "$@"
fi

cat >&2 <<'EOF2'
uninstall.sh: found neither Node (npx) nor the Python CLI (pip install gabbe).
Install one, then run this again. Or remove the kit by hand:
  - read .gabbe/manifest.json: it lists every path the installer wrote;
  - delete those paths (agents/, .agents/skills/, the per-agent folders and links such
    as .claude/skills/<kit skill>/, .cursor/rules/<kit skill>.mdc, .cursorrules, GEMINI.md);
  - take the block between "GABBE-KIT:BEGIN" and "GABBE-KIT:END" out of your own
    instruction files, or restore them from <name>.gabbe-bak (or <name>.bak);
  - finally delete .gabbe/ and any empty folders left.
See docs/INSTALL.md, "Uninstalling".
EOF2
exit 2
