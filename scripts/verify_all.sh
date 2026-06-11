#!/usr/bin/env bash
# verify_all.sh — one-stop verification for GABBE.
#
# Runs every quality gate, the test suite, linters/type-check, the kit
# validators, and install + registry smoke tests. Optional tools (node, pip-audit)
# are detected and skipped-with-a-note when absent, so this never fails for a
# reason outside your control. Exits non-zero if any REQUIRED check fails.
#
# Usage:  bash scripts/verify_all.sh   (run from the repo root)
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

# Prefer the project venv if present.
if [ -x ".venv/bin/python" ]; then PY=".venv/bin/python"; else PY="python3"; fi

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
PASS=0; FAIL=0; SKIP=0
fails=""

run() {   # run "<label>" <command...>
    label="$1"; shift
    printf "${BLUE}» %s${NC}\n" "$label"
    if "$@" >/tmp/verify_all_last.log 2>&1; then
        printf "  ${GREEN}PASS${NC} %s\n" "$label"; PASS=$((PASS+1))
    else
        printf "  ${RED}FAIL${NC} %s (see output below)\n" "$label"; FAIL=$((FAIL+1))
        fails="$fails\n  - $label"
        tail -15 /tmp/verify_all_last.log | sed 's/^/      /'
    fi
}
skip() { printf "  ${YELLOW}SKIP${NC} %s (%s)\n" "$1" "$2"; SKIP=$((SKIP+1)); }

echo "=================================================================="
echo " GABBE verify_all — $(date 2>/dev/null || echo)"
echo " python: $PY"
echo "=================================================================="

# --- 1. Lint + type-check ---
run "black --check"      $PY -m black --check gabbe scripts agents/scripts
run "ruff"               $PY -m ruff check gabbe scripts agents/scripts
run "mypy"               $PY -m mypy gabbe

# --- 2. Unit / integration tests ---
run "pytest (full suite)" $PY -m pytest -q

# --- 3. Backward-compat gates (API/CLI/config/db/emitter/CVE) ---
run "gates (run_gates.sh)" bash scripts/gates/run_gates.sh

# --- 4. Kit validators ---
run "validate_skills"     $PY agents/scripts/validate_skills.py
run "validate_links"      $PY agents/scripts/validate_links.py
run "verify_use_cases"    $PY agents/scripts/verify_use_cases.py
run "validate_integrity"  $PY agents/scripts/validate_integrity.py

# --- 5. Registry round-trip smoke (export -> import dry-run) ---
printf "${BLUE}» registry round-trip${NC}\n"
if $PY scripts/registry_export.py --out /tmp/gabbe_verify_reg >/tmp/verify_all_last.log 2>&1 \
   && $PY scripts/registry_import.py /tmp/gabbe_verify_reg/skills --namespace ext >>/tmp/verify_all_last.log 2>&1; then
    printf "  ${GREEN}PASS${NC} registry export+import\n"; PASS=$((PASS+1))
else
    printf "  ${RED}FAIL${NC} registry export+import\n"; FAIL=$((FAIL+1)); fails="$fails\n  - registry"
    tail -15 /tmp/verify_all_last.log | sed 's/^/      /'
fi
rm -rf /tmp/gabbe_verify_reg

# --- 6. Install smoke (Node path optional; POSIX install.sh syntax) ---
run "install.sh syntax (sh -n)" sh -n install.sh
if command -v node >/dev/null 2>&1; then
    run "node bin/install.js --help" node bin/install.js --help
    # Wire a throwaway project and confirm the universal targets are emitted.
    T=$(mktemp -d 2>/dev/null || echo /tmp/gabbe-npx-smoke); rm -rf "$T"; mkdir -p "$T"
    if (cd "$T" && node "$ROOT/bin/install.js" init --agents claude --yes >/tmp/verify_all_last.log 2>&1 \
        && [ -e "$T/AGENTS.md" ] && [ -d "$T/.agents/skills" ] && [ -e "$T/.claude/CLAUDE.md" ]); then
        printf "  ${GREEN}PASS${NC} npx install smoke (AGENTS.md + .agents/skills + .claude/CLAUDE.md)\n"; PASS=$((PASS+1))
    else
        printf "  ${RED}FAIL${NC} npx install smoke\n"; FAIL=$((FAIL+1)); fails="$fails\n  - npx install smoke"
        tail -15 /tmp/verify_all_last.log | sed 's/^/      /'
    fi
    rm -rf "$T"
else
    skip "npx / node install path" "node not installed — test in a Node environment"
fi

echo "=================================================================="
printf " ${GREEN}PASS=%d${NC}  ${RED}FAIL=%d${NC}  ${YELLOW}SKIP=%d${NC}\n" "$PASS" "$FAIL" "$SKIP"
if [ "$FAIL" -ne 0 ]; then
    printf "${RED}FAILURES:${NC}$fails\n"
    echo "=================================================================="
    exit 1
fi
echo " ALL REQUIRED CHECKS PASSED"
echo "=================================================================="
