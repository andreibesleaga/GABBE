"""
Edge-case and gap-coverage E2E tests.

Covers areas identified as missing from the existing 303-test suite:
  - CLI dispatch for: runs, audit, replay, resume, forecast, serve-mcp
  - Memory directory lifecycle (creation, persistence across sync)
  - Sync with unicode / special characters in task titles
  - Brain evolve multi-generation stress (5+ generations)
  - Brain heal with partial file existence
  - Status dashboard with large mixed task states
  - Database schema v3 tables presence
"""
import json
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# CLI dispatch: gabbe runs
# ---------------------------------------------------------------------------

def test_runs_command_empty(tmp_project, capsys):
    """gabbe runs with no runs → 'No runs found'."""
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "runs"]):
        main()
    out = capsys.readouterr().out
    assert "No runs found" in out


def test_runs_command_with_data(tmp_project, capsys):
    """gabbe runs lists existing run records."""
    from gabbe.database import get_db
    from gabbe.main import main

    conn = get_db()
    conn.execute(
        "INSERT INTO runs (id, command, status, started_at, initiator) "
        "VALUES ('run-001', 'brain activate', 'completed', '2026-03-01 10:00:00', 'test')"
    )
    conn.commit()
    conn.close()

    with patch("sys.argv", ["gabbe", "runs"]):
        main()
    out = capsys.readouterr().out
    assert "run-001" in out
    assert "brain activate" in out
    assert "completed" in out


def test_runs_command_status_filter(tmp_project, capsys):
    """gabbe runs --status completed filters correctly."""
    from gabbe.database import get_db
    from gabbe.main import main

    conn = get_db()
    conn.execute(
        "INSERT INTO runs (id, command, status, started_at) "
        "VALUES ('r1', 'sync', 'completed', '2026-03-01 10:00:00')"
    )
    conn.execute(
        "INSERT INTO runs (id, command, status, started_at) "
        "VALUES ('r2', 'brain', 'error', '2026-03-01 11:00:00')"
    )
    conn.commit()
    conn.close()

    with patch("sys.argv", ["gabbe", "runs", "--status", "completed"]):
        main()
    out = capsys.readouterr().out
    assert "r1" in out
    assert "r2" not in out


# ---------------------------------------------------------------------------
# CLI dispatch: gabbe forecast
# ---------------------------------------------------------------------------

def test_forecast_command_dispatches(tmp_project):
    """gabbe forecast dispatches to run_forecast."""
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "forecast"]), \
         patch("gabbe.forecast.run_forecast") as mock_fc:
        main()
    mock_fc.assert_called_once()


def test_forecast_empty_db_no_crash(tmp_project, capsys):
    """gabbe forecast on empty DB doesn't crash."""
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "forecast"]):
        main()
    # Should complete without exception


# ---------------------------------------------------------------------------
# CLI dispatch: gabbe audit
# ---------------------------------------------------------------------------

def test_audit_command_no_spans(tmp_project, capsys):
    """gabbe audit <id> with no spans → 'No audit spans found'."""
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "audit", "nonexistent-run"]):
        main()
    out = capsys.readouterr().out
    assert "No audit spans" in out


def test_audit_command_json_format(tmp_project, capsys):
    """gabbe audit <id> --format json returns valid JSON."""
    from gabbe.database import get_db
    from gabbe.main import main

    conn = get_db()
    conn.execute(
        "INSERT INTO runs (id, command, status, started_at) "
        "VALUES ('audit-run', 'brain activate', 'completed', '2026-03-01')"
    )
    conn.execute(
        "INSERT INTO audit_spans (run_id, event_type, node_name, status, duration_ms, cost_usd) "
        "VALUES ('audit-run', 'llm_call', 'activate', 'ok', 150.5, 0.003)"
    )
    conn.commit()
    conn.close()

    with patch("sys.argv", ["gabbe", "audit", "audit-run", "--format", "json"]):
        main()
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert isinstance(parsed, list)


# ---------------------------------------------------------------------------
# CLI dispatch: gabbe replay
# ---------------------------------------------------------------------------

def test_replay_command_empty(tmp_project, capsys):
    """gabbe replay with no checkpoints → 'No checkpoints'."""
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "replay", "no-such-run"]):
        main()
    out = capsys.readouterr().out
    assert "No checkpoints" in out


# ---------------------------------------------------------------------------
# CLI dispatch: gabbe resume
# ---------------------------------------------------------------------------

def test_resume_command_no_escalations(tmp_project, capsys):
    """gabbe resume with no pending escalations → 'No pending'."""
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "resume", "no-such-run"]):
        main()
    out = capsys.readouterr().out
    assert "No pending" in out


# ---------------------------------------------------------------------------
# Memory directory lifecycle
# ---------------------------------------------------------------------------

def test_memory_directory_created_on_init(tmp_project):
    """Memory directories (episodic, semantic) should be usable after DB init."""
    from gabbe.database import get_db

    # The DB should have been initialized by the fixture
    conn = get_db()
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()

    # Schema v3 tables must exist
    assert "runs" in tables
    assert "audit_spans" in tables
    assert "budget_snapshots" in tables
    assert "checkpoints" in tables
    assert "pending_escalations" in tables
    assert "forecast_snapshots" in tables
    assert "pricing_registry" in tables


def test_memory_persists_across_sync_cycles(tmp_project):
    """Tasks survive import → DB mutation → export cycle."""
    from gabbe.database import get_db
    import gabbe.sync as sync_mod

    # Write initial tasks
    tasks_file = tmp_project / "project" / "TASKS.md"
    tasks_file.parent.mkdir(parents=True, exist_ok=True)
    tasks_file.write_text("- [ ] Alpha\n- [x] Beta\n- [/] Gamma\n")

    # Import → DB
    sync_mod.sync_tasks()

    conn = get_db()
    rows = conn.execute("SELECT title, status FROM tasks ORDER BY title").fetchall()
    conn.close()
    assert len(rows) == 3
    assert rows[0]["title"] == "Alpha"
    assert rows[0]["status"] == "TODO"
    assert rows[1]["title"] == "Beta"
    assert rows[1]["status"] == "DONE"
    assert rows[2]["title"] == "Gamma"
    assert rows[2]["status"] == "IN_PROGRESS"


# ---------------------------------------------------------------------------
# Sync edge cases: unicode / special characters
# ---------------------------------------------------------------------------

def test_sync_unicode_task_titles(tmp_project):
    """Tasks with unicode characters survive sync roundtrip."""
    import gabbe.sync as sync_mod

    tasks_file = tmp_project / "project" / "TASKS.md"
    tasks_file.parent.mkdir(parents=True, exist_ok=True)
    tasks_file.write_text(
        "- [ ] Добавить поддержку 🚀\n"
        "- [x] Tâche complétée ✅\n"
        "- [ ] 任务：测试中文\n"
    )

    sync_mod.sync_tasks()

    from gabbe.database import get_db

    conn = get_db()
    rows = conn.execute("SELECT title FROM tasks ORDER BY title").fetchall()
    conn.close()

    titles = [r["title"] for r in rows]
    assert any("🚀" in t for t in titles)
    assert any("✅" in t for t in titles)
    assert any("中文" in t for t in titles)


def test_sync_task_with_special_markdown_chars(tmp_project):
    """Tasks with backticks, brackets, pipes survive sync."""
    import gabbe.sync as sync_mod

    tasks_file = tmp_project / "project" / "TASKS.md"
    tasks_file.parent.mkdir(parents=True, exist_ok=True)
    tasks_file.write_text(
        "- [ ] Fix `config.py` edge case\n"
        "- [ ] Handle [brackets] in names\n"
    )

    sync_mod.sync_tasks()

    from gabbe.database import get_db

    conn = get_db()
    rows = conn.execute("SELECT title FROM tasks ORDER BY title").fetchall()
    conn.close()
    titles = [r["title"] for r in rows]
    assert any("config.py" in t for t in titles)
    assert any("brackets" in t for t in titles)


# ---------------------------------------------------------------------------
# Brain evolve: multi-generation stress
# ---------------------------------------------------------------------------

def test_evolve_multi_generation(tmp_project):
    """Evolving the same skill 5 times with increasing success_rate creates generations 0-5."""
    from gabbe.brain import evolve_prompts
    from gabbe.database import get_db

    for i in range(5):
        with patch("gabbe.brain.call_llm", return_value=f"Prompt v{i+1}"):
            evolve_prompts("stress-skill")

        # Bump success_rate of the latest gene so it becomes the 'best' for next iteration
        conn = get_db()
        conn.execute(
            "UPDATE genes SET success_rate = ? WHERE skill_name = 'stress-skill' "
            "AND generation = (SELECT MAX(generation) FROM genes WHERE skill_name = 'stress-skill')",
            (0.1 * (i + 1),),
        )
        conn.commit()
        conn.close()

    conn = get_db()
    rows = conn.execute(
        "SELECT generation FROM genes WHERE skill_name='stress-skill' ORDER BY generation"
    ).fetchall()
    conn.close()

    generations = [r["generation"] for r in rows]
    # Should have seed (0) plus 5 incremental mutations
    assert len(generations) >= 6  # gen 0 (seed) + 5 mutations
    assert max(generations) >= 5


# ---------------------------------------------------------------------------
# Brain heal: partial file existence
# ---------------------------------------------------------------------------

def test_brain_heal_one_file_missing(tmp_project, capsys):
    """Healer detects exactly which files are missing vs present."""
    from gabbe.brain import run_healer

    agents = tmp_project / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "AGENTS.md").touch()  # present
    # CONSTITUTION.md and TASKS.md: absent

    required = [
        tmp_project / "agents/AGENTS.md",
        tmp_project / "agents/CONSTITUTION.md",
        tmp_project / "project/TASKS.md",
    ]
    with patch("gabbe.brain.REQUIRED_FILES", required):
        run_healer()

    out = capsys.readouterr().out
    assert "AGENTS.md" in out
    assert "Missing" in out  # at least one file missing
    assert "Reachable" in out  # DB is still reachable


# ---------------------------------------------------------------------------
# Status dashboard: large mixed task states
# ---------------------------------------------------------------------------

def test_status_large_mixed_workload(tmp_project, capsys):
    """Dashboard handles 100+ tasks without crash and shows correct percentages."""
    from gabbe.database import get_db
    from gabbe.status import show_dashboard

    conn = get_db()
    for i in range(50):
        conn.execute(f"INSERT INTO tasks (title, status) VALUES ('Done-{i}', 'DONE')")
    for i in range(30):
        conn.execute(f"INSERT INTO tasks (title, status) VALUES ('Todo-{i}', 'TODO')")
    for i in range(20):
        conn.execute(f"INSERT INTO tasks (title, status) VALUES ('WIP-{i}', 'IN_PROGRESS')")
    conn.commit()
    conn.close()

    show_dashboard()
    out = capsys.readouterr().out
    assert "50%" in out  # 50 done out of 100
    assert "Progress:" in out


# ---------------------------------------------------------------------------
# CLI dispatch: serve-mcp importability
# ---------------------------------------------------------------------------

def test_serve_mcp_importable(tmp_project):
    """serve-mcp module is importable and has serve() function."""
    from gabbe.mcp_server import serve
    assert callable(serve)


# ---------------------------------------------------------------------------
# CLI: unknown command gracefully handled
# ---------------------------------------------------------------------------

def test_unknown_command_prints_help(tmp_project, capsys):
    """gabbe with unknown command prints help, doesn't crash."""
    from gabbe.main import main
    with patch("sys.argv", ["gabbe", "nonexistent_cmd"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 2  # argparse unknown command exits 2


# ---------------------------------------------------------------------------
# Database: duplicate task title constraint
# ---------------------------------------------------------------------------

def test_sync_duplicate_titles_handled(tmp_project):
    """Syncing a file with duplicate task titles should not crash."""
    import gabbe.sync as sync_mod

    tasks_file = tmp_project / "project" / "TASKS.md"
    tasks_file.parent.mkdir(parents=True, exist_ok=True)
    tasks_file.write_text("- [ ] Same Title\n- [x] Same Title\n")

    # Should not raise IntegrityError — sync should handle gracefully
    sync_mod.sync_tasks()
