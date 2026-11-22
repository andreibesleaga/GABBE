#!/bin/sh
# GABBE-HOOK installer. Run from inside the project:
#   sh agents/hooks/git/install.sh            copy pre-commit and pre-push into .git/hooks
#   sh agents/hooks/git/install.sh uninstall  remove them (only files that carry the GABBE-HOOK mark)
# It never overwrites a hook it did not install. If one exists, it stops and says how to chain.
set -u
here=$(cd "$(dirname "$0")" && pwd) || exit 1
gitdir=$(git rev-parse --git-common-dir 2>/dev/null) || { echo "gabbe hooks: not inside a git repository." >&2; exit 1; }
if [ -n "$(git config --get core.hooksPath 2>/dev/null)" ]; then
  echo "gabbe hooks: core.hooksPath is set. Chain the two scripts from your hook manager instead:" >&2
  echo "  call $here/pre-commit and $here/pre-push from your own hooks (push hook: pass stdin and arguments on)." >&2
  exit 1
fi
dest="$gitdir/hooks"
mark='GABBE-HOOK'
mode=${1:-install}
status=0
for h in pre-commit pre-push; do
  t="$dest/$h"
  case $mode in
    uninstall)
      if [ -f "$t" ] && [ ! -L "$t" ] && grep -q "$mark" "$t"; then rm -f "$t" && echo "removed $t"
      elif [ -e "$t" ]; then echo "left $t alone (not installed by GABBE)"
      fi ;;
    install)
      # A link (also a dangling one: [ -e ] is false for it) is never written through.
      if [ -L "$t" ]; then
        echo "gabbe hooks: $t is a link. Not overwritten; nothing is written through it." >&2
        status=1
        continue
      fi
      if [ -e "$t" ] && ! grep -q "$mark" "$t"; then
        echo "gabbe hooks: $t already exists and is not GABBE's. Not overwritten." >&2
        echo "  To chain: add a line to it that runs  $here/$h \"\$@\"  (pre-push: keep stdin flowing, e.g. use exec or tee)." >&2
        status=1
        continue
      fi
      if mkdir -p "$dest" && cp "$here/$h" "$t" && chmod +x "$t"; then
        echo "installed $t"
      else
        echo "gabbe hooks: could not install $t." >&2
        status=1
      fi ;;
    *) echo "usage: sh install.sh [install|uninstall]" >&2; exit 2 ;;
  esac
done
exit $status
