#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
#
# GABBE bootstrap installer (POSIX sh).
#
#   curl -fsSL https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.sh | sh
#
# Picks the best available installer for your machine:
#   1. Node present  -> `npx --yes gabbe-kit@<this release> init` (Python-independent path).
#   2. Else python3  -> `python3 scripts/init.py` (the interactive wizard), only from a
#                       GABBE checkout: run `sh install.sh` from a file, not piped.
#
# It performs no destructive operations: it only runs an installer that copies
# the kit into the CURRENT directory. Extra arguments are passed to the installer,
# e.g.  `sh install.sh init --agents claude --yes`.
#
# The kit version this script belongs to is the line below (the release gate checks it
# against package.json). GABBE_KIT_VERSION overrides it; `latest` means the newest release.

GABBE_KIT_DEFAULT_VERSION="1.1.4"

set -eu

PROG="install.sh"

usage() {
  cat <<'EOF2'
GABBE bootstrap installer

Usage:
  sh install.sh [init] [installer-args...]

Behavior:
  - If Node is installed, runs:   npx --yes gabbe-kit@<this release> init [args...]
  - Else if python3 is installed and this script is run from a GABBE checkout:
                                  python3 scripts/init.py [--force] [--hooks]
    (the wizard has only --force and --hooks; other arguments are ignored and listed)
  - Otherwise, prints how to install Node or Python and exits non-zero.

Options:
  --help, -h    Show this help and exit.

Environment:
  GABBE_KIT_VERSION   Install that exact gabbe-kit version (for example 1.2.0) instead of
                      the release this script belongs to. `latest` means the newest
                      release on npm, unpinned.

Examples:
  sh install.sh init --agents claude,cursor --yes
  curl -fsSL https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.sh | sh
EOF2
}

# --help short-circuit (only when it is the first argument).
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

have() {
  command -v "$1" >/dev/null 2>&1
}

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

# `init` is the installer's default command: drop a leading one so it is not given twice.
if [ "${1:-}" = "init" ]; then
  shift
fi

# The directory this script lives in, only when it runs from a file named install.sh.
# Piped through `curl | sh` there is no file and no checkout; a scripts/init.py in the
# current project must never be run by accident.
SCRIPT_DIR=""
case "$0" in
  *install.sh)
    if [ -f "$0" ]; then
      SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
    fi
    ;;
esac

echo "GABBE installer: detecting runtime..."

if have npx; then
  if have node; then
    echo "→ Node detected ($(node --version)). Using: npx --yes $KIT_SPEC init"
  else
    echo "→ npx detected. Using: npx --yes $KIT_SPEC init"
  fi
  # npx prefers a gabbe-kit of the same name and version found in the project's own
  # node_modules; that is why the version is fixed.
  exec npx --yes "$KIT_SPEC" init "$@"
fi

if have python3; then
  if [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/scripts/init.py" ]; then
    echo "Error: python3 was found but Node was not, and there is no GABBE checkout here" >&2
    echo "(this script was piped, or scripts/init.py is not next to it)." >&2
    echo "Install Node.js >= 16 and re-run, or clone the repository and run:" >&2
    echo "  git clone https://github.com/andreibesleaga/GABBE && python3 GABBE/scripts/init.py" >&2
    exit 1
  fi
  if [ ! -t 0 ]; then
    echo "Error: the Python wizard asks questions and needs a terminal; input is not a terminal." >&2
    echo "Install Node.js >= 16 for an install without questions: npx gabbe-kit init --yes" >&2
    exit 1
  fi
  # The wizard knows --force and --hooks only; say what is left out.
  FORCE=""
  HOOKS=""
  IGNORED=""
  for arg in "$@"; do
    if [ "$arg" = "--force" ]; then
      FORCE="--force"
    elif [ "$arg" = "--hooks" ]; then
      HOOKS="--hooks"
    else
      IGNORED="$IGNORED $arg"
    fi
  done
  if [ -n "$IGNORED" ]; then
    echo "! The wizard does not take these arguments; ignored:$IGNORED" >&2
  fi
  echo "→ Node not found; python3 detected. Using: python3 $SCRIPT_DIR/scripts/init.py $FORCE $HOOKS"
  # Unquoted on purpose: each variable is empty or one fixed flag.
  # shellcheck disable=SC2086
  exec python3 "$SCRIPT_DIR/scripts/init.py" $FORCE $HOOKS
fi

echo "Error: neither Node nor python3 was found on PATH." >&2
echo "Install one of the following, then re-run $PROG:" >&2
echo "  - Node.js >= 16   (https://nodejs.org)  then: npx gabbe-kit init" >&2
echo "  - Python >= 3.9   (https://python.org)   then: python3 scripts/init.py" >&2
exit 1
