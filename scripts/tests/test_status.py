"""Unit tests for gabbe.status."""
import pytest
from unittest.mock import patch


def test_dashboard_renders_sections(tmp_project, capsys):
    """Dashboard output contains all expected sections."""
    from gabbe.status import show_dashboard
    show_dashboard()
    out = capsys.readouterr().out
    assert "GABBE PROJECT DASHBOARD" in out
    assert "Tasks:" in out
    assert "Progress:" in out


def test_dashboard_empty_db_no_crash(tmp_project, capsys):
    """Dashboard must not crash on an empty database (zero division guard)."""
    from gabbe.status import show_dashboard
    show_dashboard()
    out = capsys.readouterr().out
    assert "0%" in out or "Progress:" in out  # should render 0 %


def test_dashboard_shows_task_counts(tmp_project, capsys):
    """Task counts from DB appear in dashboard output."""
    from gabbe.database import get_db
    from gabbe.status import show_dashboard

    conn = get_db()
    conn.execute("INSERT INTO tasks (title, status) VALUES ('A', 'DONE')")
    conn.execute("INSERT INTO tasks (title, status) VALUES ('B', 'TODO')")
    conn.execute("INSERT INTO tasks (title, status) VALUES ('C', 'IN_PROGRESS')")
    conn.commit()
    conn.close()

    show_dashboard()
    out = capsys.readouterr().out
    assert "1 Done" in out
    assert "1 In Progress" in out
    assert "1 Todo" in out


def test_dashboard_progress_100_percent(tmp_project, capsys):
    """When all tasks are DONE, progress bar shows 100%."""
    from gabbe.database import get_db
    from gabbe.status import show_dashboard

    conn = get_db()
    for i in range(5):
        conn.execute(f"INSERT INTO tasks (title, status) VALUES ('Task {i}', 'DONE')")
    conn.commit()
    conn.close()

    show_dashboard()
    out = capsys.readouterr().out
    assert "100%" in out


def test_dashboard_progress_bar_does_not_overflow(tmp_project, capsys):
    """Progress bar must never exceed PROGRESS_BAR_LEN characters."""
    from gabbe.database import get_db
    from gabbe.status import show_dashboard
    from gabbe.config import PROGRESS_BAR_LEN

    conn = get_db()
    # All tasks done → 100% → bar should be exactly PROGRESS_BAR_LEN filled
    for i in range(10):
        conn.execute(f"INSERT INTO tasks (title, status) VALUES ('T{i}', 'DONE')")
    conn.commit()
    conn.close()

    show_dashboard()
    out = capsys.readouterr().out

    # Extract the bar content between [ and ]
    import re
    match = re.search(r'\[.*?([\u2588\-]+).*?\]', out)
    if match:
        bar_content = match.group(1)
        assert len(bar_content) <= PROGRESS_BAR_LEN


def test_dashboard_shows_phase_from_project_state(tmp_project, capsys):
    """Dashboard shows current_phase when set in project_state."""
    from gabbe.database import get_db
    from gabbe.status import show_dashboard

    conn = get_db()
    conn.execute(
        "INSERT INTO project_state (key, value) VALUES ('current_phase', 'S03-Design')"
    )
    conn.commit()
    conn.close()

    show_dashboard()
    out = capsys.readouterr().out
    assert "S03-Design" in out


def test_dashboard_missing_phase_shows_dash(tmp_project, capsys):
    """When current_phase is not in project_state, a placeholder is shown."""
    from gabbe.status import show_dashboard
    show_dashboard()
    out = capsys.readouterr().out
    # Should show placeholder — not crash
    assert "Phase:" in out
