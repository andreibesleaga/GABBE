# SPDX-License-Identifier: Apache-2.0
"""Tests for gabbe.forecast.run_forecast()."""

from gabbe.database import get_db


def test_forecast_runs_on_empty_db(tmp_project, capsys):
    """run_forecast() should succeed and print output even with no tasks or runs."""
    from gabbe.forecast import run_forecast

    run_forecast()
    out = capsys.readouterr().out
    assert "Forecast" in out or "forecast" in out.lower()
    assert "Total spent" in out


def test_forecast_shows_zero_costs_on_empty_db(tmp_project, capsys):
    """With no runs, total cost and tokens are zero."""
    from gabbe.forecast import run_forecast

    run_forecast()
    out = capsys.readouterr().out
    assert "$0.0000" in out


def test_forecast_shows_task_counts(tmp_project, capsys):
    from gabbe.forecast import run_forecast

    conn = get_db()
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T1', 'DONE')")
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T2', 'TODO')")
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T3', 'IN_PROGRESS')")
    conn.commit()
    conn.close()

    run_forecast()
    out = capsys.readouterr().out
    assert "1 DONE" in out
    assert "1 IN_PROGRESS" in out
    assert "1 TODO" in out


def test_forecast_computes_avg_cost_per_task(tmp_project, capsys):
    """Average cost per task is total_cost / done_count."""
    from gabbe.forecast import run_forecast

    conn = get_db()
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T1', 'DONE')")
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T2', 'TODO')")
    # One completed run with $1.00 cost
    conn.execute(
        "INSERT INTO runs (id, command, status, total_cost_usd, total_tokens_used) VALUES (?, ?, ?, ?, ?)",
        ("run-1", "brain activate", "completed", 1.0, 1000),
    )
    conn.commit()
    conn.close()

    run_forecast()
    out = capsys.readouterr().out
    # 1 done task, $1 spent → avg $1.0000 per task; 1 remaining → projected $1.0000
    assert "$1.0000" in out


def test_forecast_zero_done_tasks_no_div_zero(tmp_project, capsys):
    """With tasks all TODO and no runs, no division-by-zero should occur."""
    from gabbe.forecast import run_forecast

    conn = get_db()
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T1', 'TODO')")
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T2', 'TODO')")
    conn.commit()
    conn.close()

    run_forecast()  # must not raise
    out = capsys.readouterr().out
    assert "0 DONE" in out


def test_forecast_inserts_snapshot(tmp_project):
    """run_forecast() must insert a row into forecast_snapshots."""
    from gabbe.forecast import run_forecast

    run_forecast()

    conn = get_db()
    row = conn.execute("SELECT * FROM forecast_snapshots WHERE run_id = 'forecast_cmd'").fetchone()
    conn.close()
    assert row is not None
    assert row["step"] == 0
    assert row["projected_cost"] >= 0.0


def test_forecast_snapshot_reflects_projections(tmp_project):
    """The snapshot cost matches what is printed."""
    from gabbe.forecast import run_forecast

    conn = get_db()
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T1', 'DONE')")
    conn.execute("INSERT INTO tasks (title, status) VALUES ('T2', 'TODO')")
    conn.execute(
        "INSERT INTO runs (id, command, status, total_cost_usd, total_tokens_used) VALUES (?, ?, ?, ?, ?)",
        ("run-x", "brain activate", "completed", 2.0, 500),
    )
    conn.commit()
    conn.close()

    run_forecast()

    conn = get_db()
    snap = conn.execute("SELECT * FROM forecast_snapshots WHERE run_id = 'forecast_cmd'").fetchone()
    conn.close()
    # 1 done task, $2 total → avg $2/task; 1 remaining → projected $2
    assert abs(snap["projected_cost"] - 2.0) < 0.001
    assert snap["projected_tokens"] == 500
