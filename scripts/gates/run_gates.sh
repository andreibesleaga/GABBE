#!/usr/bin/env bash
# Verification gate runner for the strict-compat audit.
#
# Gates (per OpenSourceAudit framework):
#   1. API surface diff empty or additive
#   2. CLI --help byte-equal vs baselines (modulo documented additive flags)
#   3. Config schema superset-only (config keys + DB schema)
#   4. Emitter fixture vault green (manifest comparison, additive-only)
#   5. Benchmarks within 5% of baseline (informational here; run bench separately)
#   6. CVE delta non-positive
#
# Exit code 0 = all checked gates pass.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${PY:-$ROOT/.venv/bin/python}"
BASE="$ROOT/scripts/gates/baselines"
FAIL=0
cd "$ROOT"

note() { printf '%s\n' "$*"; }
fail() { printf 'GATE FAIL: %s\n' "$*"; FAIL=1; }

note "== Gate 1: API surface =="
"$PY" "$ROOT/scripts/gates/dump_api.py" > /tmp/gabbe-api-current.json
"$PY" - "$BASE/api-surface.json" /tmp/gabbe-api-current.json <<'EOF' || FAIL=1
import json, sys
base = json.load(open(sys.argv[1])); cur = json.load(open(sys.argv[2]))
bad = []
for mod, names in base.items():
    if mod not in cur:
        bad.append(f"module removed: {mod}"); continue
    for name, desc in names.items():
        if name not in cur[mod]:
            bad.append(f"removed: {mod}.{name}")
        elif cur[mod][name] != desc:
            bad.append(f"changed: {mod}.{name}: {desc} -> {cur[mod][name]}")
added = [f"{m}.{n}" for m, ns in cur.items() for n in ns if m not in base or n not in base.get(m, {})]
if added:
    print(f"  additive: {len(added)} new public names (allowed)")
if bad:
    print("GATE FAIL: API surface:"); [print("   ", b) for b in bad]; sys.exit(1)
print("  PASS")
EOF

note "== Gate 2: CLI --help byte-equal =="
HELP_DIR="$ROOT/gabbe/tests/baselines/cli_help"
G2=0
check_help() {
  local name="$1"; shift
  COLUMNS=80 "$PY" -m gabbe.main "$@" --help > "/tmp/gabbe-help-$name.txt" 2>&1
  if ! diff -q "$HELP_DIR/$name.txt" "/tmp/gabbe-help-$name.txt" >/dev/null 2>&1; then
    fail "help text changed: $name (diff $HELP_DIR/$name.txt /tmp/gabbe-help-$name.txt)"; G2=1
  fi
}
check_help root
check_help init init; check_help db db; check_help sync sync; check_help verify verify
check_help status status; check_help route route; check_help brain brain
check_help brain_activate brain activate; check_help brain_evolve brain evolve
check_help brain_heal brain heal; check_help serve-mcp serve-mcp
check_help forecast forecast; check_help runs runs; check_help audit audit
check_help replay replay; check_help resume resume
check_help registry registry; check_help registry_publish registry publish
check_help registry_add registry add; check_help setup setup
[ "$G2" -eq 0 ] && note "  PASS"

note "== Gate 3: Config schema superset-only =="
"$PY" - "$BASE/config-schema.json" <<'EOF' || FAIL=1
import json, sys
base = json.load(open(sys.argv[1]))
import gabbe.config as c
cur = {}
for name in sorted(dir(c)):
    if name.startswith("_"): continue
    val = getattr(c, name)
    if callable(val) or type(val).__name__ == "module": continue
    cur[name] = type(val).__name__
bad = [f"removed: {k}" for k in base if k not in cur]
bad += [f"retyped: {k} {base[k]} -> {cur[k]}" for k in base if k in cur and cur[k] != base[k]]
if bad:
    print("GATE FAIL: config schema:"); [print("   ", b) for b in bad]; sys.exit(1)
added = [k for k in cur if k not in base]
if added: print(f"  additive: {added}")
print("  PASS")
EOF

note "== Gate 3b: DB schema superset-only =="
"$PY" - "$BASE/db-schema.sql" <<'EOF' || FAIL=1
import os, sqlite3, subprocess, sys, tempfile
from pathlib import Path
baseline = Path(sys.argv[1]).read_text()
with tempfile.TemporaryDirectory() as tmp:
    proj = Path(tmp)
    (proj/"project").mkdir(); (proj/"agents").mkdir()
    (proj/"agents/AGENTS.md").write_text("#"); (proj/"agents/CONSTITUTION.md").write_text("#")
    (proj/"project/TASKS.md").write_text("")
    subprocess.run([sys.executable, "-m", "gabbe.main", "db", "--init"], cwd=proj, capture_output=True)
    con = sqlite3.connect(proj/"project/state.db")
    rows = con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type, name").fetchall()
current = "\n".join(r[0] + ";" for r in rows) + "\n"
def norm(text):
    return " ".join(text.split())
cur_norm = norm(current)
missing = [s for s in baseline.strip().split(";") if s.strip() and norm(s) not in cur_norm]
if missing:
    print("GATE FAIL: DB schema lost statements:"); [print("   ", m.strip()[:120]) for m in missing]; sys.exit(1)
print("  PASS")
EOF

note "== Gate 4: Emitter fixture vault =="
"$PY" "$ROOT/scripts/gates/capture_emitter_baseline.py" /tmp/gabbe-vault-current >/dev/null 2>&1
"$PY" - "$ROOT/scripts/tests/golden/baseline_v0.8.0" /tmp/gabbe-vault-current <<'EOF' || FAIL=1
import gzip, json, sys
from pathlib import Path
def load(d):
    gz = d / "manifest.json.gz"
    if gz.exists():
        return json.loads(gzip.decompress(gz.read_bytes()).decode("utf-8"))
    return json.loads((d / "manifest.json").read_text())
base_root, cur_root = Path(sys.argv[1]), Path(sys.argv[2])
bad, added = [], 0
for plat_dir in sorted(base_root.iterdir()):
    if not ((plat_dir / "manifest.json.gz").exists() or (plat_dir / "manifest.json").exists()): continue
    plat = plat_dir.name
    base = load(plat_dir)
    cur = load(cur_root / plat)
    for rel, desc in base.items():
        if rel not in cur:
            bad.append(f"{plat}: artifact removed: {rel}")
        elif cur[rel] != desc:
            bad.append(f"{plat}: artifact changed: {rel}")
    added += sum(1 for rel in cur if rel not in base)
if added: print(f"  additive: {added} new artifacts (allowed)")
if bad:
    print("GATE FAIL: emitter vault:"); [print("   ", b) for b in bad[:20]]
    if len(bad) > 20: print(f"    ... and {len(bad)-20} more")
    sys.exit(1)
print("  PASS")
EOF

note "== Gate 6: CVE delta non-positive =="
if "$PY" -m pip_audit --format json > /tmp/gabbe-cve-current.json 2>/dev/null; then
  "$PY" - "$BASE/cve-baseline.json" /tmp/gabbe-cve-current.json <<'EOF' || FAIL=1
import json, sys
def vulns(path):
    d = json.load(open(path)); deps = d.get("dependencies", d if isinstance(d, list) else [])
    return {(p["name"], v["id"]) for p in deps for v in p.get("vulns", [])}
base, cur = vulns(sys.argv[1]), vulns(sys.argv[2])
new = cur - base
if new:
    print("GATE FAIL: new CVEs:"); [print("   ", n) for n in new]; sys.exit(1)
print(f"  PASS ({len(cur)} total, {len(base - cur)} resolved)")
EOF
else
  note "  SKIP (pip-audit unavailable/offline)"
fi

note ""
if [ "$FAIL" -eq 0 ]; then note "ALL GATES PASS"; else note "GATE FAILURES PRESENT"; exit 1; fi
