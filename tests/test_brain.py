"""Unit tests for gabbe.brain."""
import io
import pytest
from pathlib import Path
from unittest.mock import patch


# ---------------------------------------------------------------------------
# activate_brain
# ---------------------------------------------------------------------------

def test_activate_brain_prints_action(tmp_project, capsys):
    from gabbe.brain import activate_brain
    with patch("gabbe.brain.call_llm", return_value="Focus on critical path"):
        activate_brain()
    out = capsys.readouterr().out
    assert "Brain Mode" in out
    assert "Focus on critical path" in out


def test_activate_brain_handles_empty_tasks(tmp_project, capsys):
    """activate_brain should not crash on an empty task table."""
    from gabbe.brain import activate_brain
    with patch("gabbe.brain.call_llm", return_value="No tasks, initialise project"):
        activate_brain()
    out = capsys.readouterr().out
    assert "Brain Mode" in out


def test_activate_brain_handles_llm_none(tmp_project, capsys):
    """When call_llm returns None, Brain Freeze message is shown."""
    from gabbe.brain import activate_brain
    with patch("gabbe.brain.call_llm", return_value=None):
        activate_brain()
    out = capsys.readouterr().out
    assert "Brain Freeze" in out


def test_activate_brain_with_tasks_in_db(tmp_project, capsys):
    """activate_brain observes real task stats from DB."""
    from gabbe.database import get_db
    from gabbe.brain import activate_brain
    conn = get_db()
    conn.execute("INSERT INTO tasks (title, status) VALUES ('Task A', 'DONE')")
    conn.execute("INSERT INTO tasks (title, status) VALUES ('Task B', 'TODO')")
    conn.commit()
    conn.close()

    with patch("gabbe.brain.call_llm", return_value="Ship it") as mock_llm:
        activate_brain()

    # The prompt passed to the LLM must mention the DB counts
    prompt_arg = mock_llm.call_args[0][0]
    assert "DONE" in prompt_arg or "1" in prompt_arg


# ---------------------------------------------------------------------------
# evolve_prompts
# ---------------------------------------------------------------------------

def test_evolve_prompts_seeds_gene_pool(tmp_project):
    """First call creates the seed gene (generation 0) and mutates it."""
    from gabbe.brain import evolve_prompts
    from gabbe.database import get_db

    with patch("gabbe.brain.call_llm", return_value="Better prompt"):
        evolve_prompts("my-skill")

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM genes WHERE skill_name='my-skill' ORDER BY generation"
    ).fetchall()
    conn.close()

    gens = [r["generation"] for r in rows]
    assert 0 in gens  # seed gene
    assert 1 in gens  # mutated gene


def test_evolve_prompts_existing_gene_increments_generation(tmp_project):
    """If a gene already exists, evolve_prompts creates generation + 1."""
    from gabbe.brain import evolve_prompts
    from gabbe.database import get_db

    # Seed manually at generation 5
    conn = get_db()
    conn.execute(
        "INSERT INTO genes (skill_name, prompt_content, generation, success_rate) VALUES (?, ?, ?, ?)",
        ("skill-x", "Old prompt", 5, 0.9),
    )
    conn.commit()
    conn.close()

    with patch("gabbe.brain.call_llm", return_value="Improved prompt"):
        evolve_prompts("skill-x")

    conn = get_db()
    rows = conn.execute(
        "SELECT generation FROM genes WHERE skill_name='skill-x' ORDER BY generation DESC"
    ).fetchall()
    conn.close()

    generations = [r["generation"] for r in rows]
    assert 6 in generations


def test_evolve_prompts_llm_none_does_not_insert(tmp_project):
    """When call_llm returns None, no new gene must be inserted."""
    from gabbe.brain import evolve_prompts
    from gabbe.database import get_db

    with patch("gabbe.brain.call_llm", return_value=None):
        evolve_prompts("null-skill")

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM genes WHERE skill_name='null-skill' AND prompt_content IS NULL"
    ).fetchall()
    conn.close()

    assert rows == [], "None must never be stored as prompt_content"


def test_evolve_prompts_gene_content_is_not_none(tmp_project):
    """Stored gene must have non-NULL prompt_content."""
    from gabbe.brain import evolve_prompts
    from gabbe.database import get_db

    with patch("gabbe.brain.call_llm", return_value="Valid prompt text"):
        evolve_prompts("good-skill")

    conn = get_db()
    rows = conn.execute(
        "SELECT prompt_content FROM genes WHERE skill_name='good-skill'"
    ).fetchall()
    conn.close()

    for row in rows:
        assert row["prompt_content"] is not None


# ---------------------------------------------------------------------------
# run_healer
# ---------------------------------------------------------------------------

def test_run_healer_all_clear(tmp_project, capsys):
    """Healer reports nominal when DB reachable and all files exist."""
    from gabbe.brain import run_healer

    agents = tmp_project / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "AGENTS.md").touch()
    (agents / "CONSTITUTION.md").touch()
    (tmp_project / "project/TASKS.md").touch()

    required = [
        tmp_project / "agents/AGENTS.md",
        tmp_project / "agents/CONSTITUTION.md",
        tmp_project / "project/TASKS.md",
    ]
    with patch("gabbe.config.REQUIRED_FILES", required):
        run_healer()

    out = capsys.readouterr().out
    assert "Nominal" in out
    assert "Reachable" in out


def test_run_healer_missing_files(tmp_project, capsys):
    """Healer reports issues when required files are missing."""
    from gabbe.brain import run_healer

    required = [
        tmp_project / "agents/AGENTS.md",  # does not exist
        tmp_project / "project/TASKS.md",            # does not exist
    ]
    with patch("gabbe.config.REQUIRED_FILES", required):
        run_healer()

    out = capsys.readouterr().out
    assert "Missing" in out
    assert "Health Issues" in out


def test_run_healer_db_unreachable(tmp_project, capsys):
    """Healer reports DB issue when get_db raises."""
    from gabbe.brain import run_healer

    with patch("gabbe.brain.get_db", side_effect=Exception("locked")), \
         patch("gabbe.config.REQUIRED_FILES", []):
        run_healer()

    out = capsys.readouterr().out
    assert "Database" in out
    assert "locked" in out
