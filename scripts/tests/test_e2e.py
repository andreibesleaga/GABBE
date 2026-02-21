"""End-to-end tests for the GABBE CLI toolkit."""
import unittest
import os
import io
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
import gabbe.config
import gabbe.sync
import gabbe.verify
from gabbe.database import init_db, get_db


class TestGabbeE2E(unittest.TestCase):

    def setUp(self):
        # Temporary project directory
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir)
        self.project_dir = self.project_root / "project"
        self.db_path = self.project_dir / "state.db"
        self.tasks_file = self.project_root / "project/TASKS.md"

        # Patch all module-level path constants
        _required_files = [
            self.project_root / "agents/AGENTS.md",
            self.project_root / "agents/CONSTITUTION.md",
            self.project_root / "project/TASKS.md",
        ]
        self._patches = [
            patch("gabbe.config.PROJECT_ROOT", self.project_root),
            patch("gabbe.config.GABBE_DIR", self.project_dir),
            patch("gabbe.config.DB_PATH", self.db_path),
            patch("gabbe.config.TASKS_FILE", self.tasks_file),
            patch("gabbe.config.REQUIRED_FILES", _required_files),
            patch("gabbe.database.GABBE_DIR", self.project_dir),
            patch("gabbe.database.DB_PATH", self.db_path),
            patch("gabbe.sync.TASKS_FILE", self.tasks_file),
            patch("gabbe.verify.PROJECT_ROOT", self.project_root),
            patch("gabbe.verify.GABBE_DIR", self.project_dir),
            patch("gabbe.verify.REQUIRED_FILES", _required_files),
            patch("gabbe.brain.PROJECT_ROOT", self.project_root),
            patch("gabbe.brain.REQUIRED_FILES", _required_files),
        ]
        for p in self._patches:
            p.start()

        init_db()
        self.conn = get_db()

    def tearDown(self):
        self.conn.close()
        for p in reversed(self._patches):
            p.stop()
        shutil.rmtree(self.test_dir)

    # ------------------------------------------------------------------
    # Scenario 1: Markdown → DB import
    # ------------------------------------------------------------------
    def test_01_sync_import(self):
        """Import tasks from Markdown to DB."""
        self.tasks_file.write_text("- [ ] Task A\n- [x] Task B\n")

        gabbe.sync.sync_tasks()

        c = self.conn.cursor()
        c.execute("SELECT * FROM tasks ORDER BY title")
        rows = c.fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["title"], "Task A")
        self.assertEqual(rows[0]["status"], "TODO")
        self.assertEqual(rows[1]["title"], "Task B")
        self.assertEqual(rows[1]["status"], "DONE")

    # ------------------------------------------------------------------
    # Scenario 2: DB → Markdown export
    # ------------------------------------------------------------------
    def test_02_sync_export(self):
        """Export tasks from DB to Markdown."""
        c = self.conn.cursor()
        c.execute("INSERT INTO tasks (title, status) VALUES ('Task C', 'IN_PROGRESS')")
        self.conn.commit()

        gabbe.sync.sync_tasks()

        content = self.tasks_file.read_text()
        self.assertIn("- [/] Task C", content)
        self.assertIn("# Project Tasks", content)

    # ------------------------------------------------------------------
    # Scenario 3: Brain evolve (LLM mocked)
    # ------------------------------------------------------------------
    def test_03_brain_evolve(self):
        """Evolutionary Prompt Optimization seeds the genes table."""
        from gabbe.brain import evolve_prompts

        with patch("gabbe.brain.call_llm", return_value="Improved prompt text here."):
            evolve_prompts("test-skill")

        c = self.conn.cursor()
        c.execute("SELECT * FROM genes WHERE skill_name='test-skill' ORDER BY generation")
        rows = c.fetchall()
        # At least 2 rows: seed gene (gen 0) + mutated gene (gen 1)
        self.assertGreaterEqual(len(rows), 2)
        gen_values = [r["generation"] for r in rows]
        self.assertIn(0, gen_values)
        self.assertIn(1, gen_values)

    # ------------------------------------------------------------------
    # Scenario 4: Cost router
    # ------------------------------------------------------------------
    def test_04_cost_router(self):
        """Simple prompts route LOCAL; complex ones route REMOTE."""
        from gabbe.route import route_request

        res_simple = route_request("Fix typo")
        self.assertEqual(res_simple, "LOCAL")

        # Force complex routing by monkeypatching complexity
        with patch("gabbe.route.calculate_complexity", return_value=(80, "mocked")):
            res_complex = route_request("architect " * 30)
        self.assertEqual(res_complex, "REMOTE")

    # ------------------------------------------------------------------
    # Scenario 5: Status dashboard
    # ------------------------------------------------------------------
    def test_05_status(self):
        """Dashboard renders expected sections."""
        from gabbe.status import show_dashboard
        import io, sys

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            show_dashboard()

        output = captured.getvalue()
        self.assertIn("GABBE PROJECT DASHBOARD", output)
        self.assertIn("Tasks:", output)
        self.assertIn("Progress:", output)

    # ------------------------------------------------------------------
    # Scenario 6: Verify
    # ------------------------------------------------------------------
    def test_06_verify(self):
        """Integrity check passes with all required files and fails without."""
        from gabbe.verify import run_verification

        # Create required files
        agents = self.project_root / "agents"
        agents.mkdir(exist_ok=True)
        (agents / "AGENTS.md").write_text("## Commands\n")
        (agents / "CONSTITUTION.md").touch()
        self.tasks_file.touch()

        self.assertTrue(run_verification())

        # Remove a file → should fail
        self.tasks_file.unlink()
        self.assertFalse(run_verification())

    # ------------------------------------------------------------------
    # Scenario 7: Brain activate (LLM mocked)
    # ------------------------------------------------------------------
    def test_07_brain_activate(self):
        """Brain activate calls LLM and prints an action."""
        from gabbe.brain import activate_brain
        import io, sys

        captured = io.StringIO()
        with patch("gabbe.brain.call_llm", return_value="Focus on critical path"), \
             patch("sys.stdout", captured):
            activate_brain()

        output = captured.getvalue()
        self.assertIn("Brain Mode", output)
        self.assertIn("Focus on critical path", output)

    # ------------------------------------------------------------------
    # Scenario 8: Brain heal
    # ------------------------------------------------------------------
    def test_08_brain_heal(self):
        """Healer reports DB as reachable and lists file statuses."""
        from gabbe.brain import run_healer
        import io, sys

        # Create required files so healer finds them
        agents = self.project_root / "agents"
        agents.mkdir(exist_ok=True)
        (agents / "AGENTS.md").touch()
        (agents / "CONSTITUTION.md").touch()
        self.tasks_file.touch()

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            run_healer()

        output = captured.getvalue()
        self.assertIn("Self-Healing Watchdog", output)
        self.assertIn("Database", output)
        self.assertIn("Nominal", output)


if __name__ == "__main__":
    unittest.main()
