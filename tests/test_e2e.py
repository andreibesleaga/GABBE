import unittest
import os
import sqlite3
import shutil
import tempfile
from pathlib import Path
from gabbe.database import init_db, get_db
# We need to mock the PROJECT_ROOT in config or monkeypatch it
# Since config.py sets PROJECT_ROOT = Path(os.getcwd()) at module level,
# we might need to reload module or patch it.
from unittest.mock import patch
import gabbe.config
import gabbe.sync

class TestGabbeE2E(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir)
        
        # Patch gabbe.config (though less useful due to direct imports)
        self.config_patcher = patch('gabbe.config.PROJECT_ROOT', self.project_root)
        self.mock_root = self.config_patcher.start()
        
        # Calculate temp paths
        temp_gabbe_dir = self.project_root / ".gabbe"
        temp_db_path = temp_gabbe_dir / "state.db"
        temp_tasks_file = self.project_root / "TASKS.md"
        
        # PATCH 1: gabbe.database.GABBE_DIR and DB_PATH
        self.db_dir_patcher = patch('gabbe.database.GABBE_DIR', temp_gabbe_dir)
        self.db_dir_patcher.start()
        
        self.db_path_patcher = patch('gabbe.database.DB_PATH', temp_db_path)
        self.db_path_patcher.start()
        
        # PATCH 2: gabbe.sync.TASKS_FILE
        self.sync_tasks_patcher = patch('gabbe.sync.TASKS_FILE', temp_tasks_file)
        self.sync_tasks_patcher.start()

        # Init DB in the temp dir
        init_db()
        self.conn = get_db()
        
    def tearDown(self):
        self.conn.close()
        self.config_patcher.stop()
        self.db_dir_patcher.stop()
        self.db_path_patcher.stop()
        self.sync_tasks_patcher.stop()
        shutil.rmtree(self.test_dir)
        
    def test_01_sync_import(self):
        """Scenario 1: Import tasks from Markdown to DB."""
        print("\n=== Test 01: Markdown -> DB Import ===")
        # 1. Create TASKS.md
        tasks_md = self.project_root / "TASKS.md"
        tasks_md.write_text("- [ ] Task A\n- [x] Task B\n")
        
        # 2. Run sync
        gabbe.sync.sync_tasks()
        
        # 3. Verify DB
        c = self.conn.cursor()
        c.execute("SELECT * FROM tasks ORDER BY title")
        rows = c.fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['title'], 'Task A')
        self.assertEqual(rows[0]['status'], 'TODO')
        self.assertEqual(rows[1]['title'], 'Task B')
        self.assertEqual(rows[1]['status'], 'DONE')
        print("✓ Verified DB content matches file")

    def test_02_sync_export(self):
        """Scenario 2: Export tasks from DB to Markdown."""
        print("\n=== Test 02: DB -> Markdown Export ===")
        # 1. Populate DB
        c = self.conn.cursor()
        c.execute("INSERT INTO tasks (title, status) VALUES ('Task C', 'IN_PROGRESS')")
        self.conn.commit()
        
        # 2. Run sync
        gabbe.sync.sync_tasks()
        
        # 3. Verify File
        tasks_md = self.project_root / "TASKS.md"
        content = tasks_md.read_text()
        self.assertIn("- [/] Task C", content)
        print("✓ Verified File content matches DB")
        
    def test_03_brain_evolve(self):
        """Scenario 6: Evolutionary Prompt Optimization."""
        from gabbe.brain import evolve_prompts
        print("\n=== Test 03: Brain Evolve ===")
        
        # 1. Run evolution
        evolve_prompts("test-skill")
        
        # 2. Verify DB genes
        c = self.conn.cursor()
        c.execute("SELECT * FROM genes WHERE skill_name='test-skill'")
        rows = c.fetchall()
        self.assertTrue(len(rows) >= 1) # Initial + Mutation
        print("✓ Verified Genes creation")

    def test_04_cost_router(self):
        """Scenario 7: Cost Router."""
        from gabbe.route import route_request
        print("\n=== Test 04: Cost Router ===")
        
        res1 = route_request("Simple typo fix")
        self.assertEqual(res1, "LOCAL")
        
        # Make it complex: >100 words, Keywords, Code block
        complex_prompt = "I need to architect a distributed system. " * 20 
        complex_prompt += "It requires a security audit and data migration. "
        complex_prompt += "Here is the code: ```python\ndef foo(): pass\n```"
        
        res2 = route_request(complex_prompt)
        self.assertEqual(res2, "REMOTE")
        print("✓ Verified Routing logic")

    def test_05_status(self):
        """Test gabbe status."""
        from gabbe.status import show_dashboard
        print("\n=== Test 05: Status Dashboard ===")
        # Just ensure it runs without error
        try:
            show_dashboard()
            print("✓ Dashboard ran successfully")
        except Exception as e:
            self.fail(f"Dashboard failed: {e}")

    def test_06_verify(self):
        """Test gabbe verify."""
        from gabbe.verify import run_verification, REQUIRED_FILES
        print("\n=== Test 06: Verify ===")
        
        # 1. Create dummy required files
        (self.project_root / ".agents").mkdir(exist_ok=True)
        (self.project_root / ".agents/AGENTS.md").touch()
        (self.project_root / ".agents/CONSTITUTION.md").touch()
        (self.project_root / "TASKS.md").touch()
        
        # 2. Run verify - Should Pass
        result = run_verification()
        self.assertTrue(result)
        
        # 3. Delete a file - Should Fail
        (self.project_root / "TASKS.md").unlink()
        result_fail = run_verification()
        self.assertFalse(result_fail)
        print("✓ Verified Integrity Check")

    def test_07_brain_activate(self):
        """Test brain activate."""
        from gabbe.brain import activate_brain
        print("\n=== Test 07: Brain Activate ===")
        activate_brain()
        print("✓ Brain active inference loop ran")

    def test_08_brain_heal(self):
        """Test brain heal."""
        from gabbe.brain import run_healer
        print("\n=== Test 08: Brain Heal ===")
        run_healer()
        print("✓ Healer ran")

if __name__ == '__main__':
    unittest.main()
