# SPDX-License-Identifier: Apache-2.0
"""Gate 3 contract test: config constants and DB schema evolve superset-only.

Every baseline config constant must still exist with the same Python type,
and every baseline SQL statement must still be present in a freshly
initialized database. Additions are allowed.
"""
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BASELINES = REPO_ROOT / "scripts" / "gates" / "baselines"


def test_config_constants_superset():
    import gabbe.config as config

    baseline = json.loads((BASELINES / "config-schema.json").read_text())
    current = {}
    for name in dir(config):
        if name.startswith("_"):
            continue
        val = getattr(config, name)
        if callable(val) or type(val).__name__ == "module":
            continue
        current[name] = type(val).__name__

    problems = [f"removed: {k}" for k in baseline if k not in current]
    problems += [
        f"retyped: {k} {baseline[k]} -> {current[k]}"
        for k in baseline
        if k in current and current[k] != baseline[k]
    ]
    assert not problems, "config schema regression:\n" + "\n".join(problems)


def test_db_schema_superset(tmp_path):
    baseline = (BASELINES / "db-schema.sql").read_text()
    (tmp_path / "project").mkdir()
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "AGENTS.md").write_text("#")
    (tmp_path / "agents" / "CONSTITUTION.md").write_text("#")
    (tmp_path / "project" / "TASKS.md").write_text("")
    subprocess.run(
        [sys.executable, "-m", "gabbe.main", "db", "--init"],
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )
    con = sqlite3.connect(tmp_path / "project" / "state.db")
    rows = con.execute(
        "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type, name"
    ).fetchall()
    con.close()
    current_norm = " ".join("\n".join(r[0] + ";" for r in rows).split())

    missing = [
        stmt.strip()[:120]
        for stmt in baseline.strip().split(";")
        if stmt.strip() and " ".join(stmt.split()) not in current_norm
    ]
    assert not missing, "DB schema lost statements:\n" + "\n".join(missing)
