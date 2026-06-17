#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
#
# GABBE uninstaller (POSIX sh).
#
#   sh uninstall.sh [--dry-run] [--agents claude,cursor] [--purge] [--dir PATH]
#
# Reverses a GABBE install from its .gabbe/manifest.json: removes exactly what was
# installed, restores any .bak backups, and never touches unrelated files. It is
# manifest-driven and isolated — nothing outside the target is changed.
#
# Resolution order for the uninstall engine:
#   1. `gabbe` console script on PATH  -> `gabbe uninstall "$@"`
#   2. python3 + repo checkout         -> `python3 -m gabbe.main uninstall "$@"`
set -eu

if command -v gabbe >/dev/null 2>&1; then
  exec gabbe uninstall "$@"
elif command -v python3 >/dev/null 2>&1; then
  exec python3 -m gabbe.main uninstall "$@"
else
  echo "uninstall.sh: need either the 'gabbe' CLI or python3 on PATH." >&2
  echo "Manual fallback: delete the paths listed in .gabbe/manifest.json." >&2
  exit 2
fi
