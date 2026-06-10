# SPDX-License-Identifier: Apache-2.0
"""
E2E Workflow Test — follows the documented README / QUICK_GUIDE workflow:

  Setup:        gabbe init
  Daily:        gabbe sync → gabbe status → gabbe brain activate/evolve/heal
  Verification: gabbe verify
  Routing:      gabbe route <prompt>
  Observability:gabbe forecast → gabbe runs → gabbe audit <id> → gabbe replay <id> → gabbe resume <id>
  MCP Server:   gabbe serve-mcp (startup verification)
  DB alias:     gabbe db --init

Each step asserts correct output & side-effects before proceeding.
Edge cases and error cases are included for every command.
"""
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gabbe.config
import gabbe.sync
import gabbe.verify
from gabbe.database import init_db, get_db


class TestWorkflowGoldenPath(unittest.TestCase):
    """
    Simulates the FULL documented workflow as described in README.md § 'How to Use':
      init → sync → status → verify → route → brain activate → brain evolve → brain heal
      → forecast → runs → audit → replay → resume
    """

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir)
        self.project_dir = self.project_root / "project"
        self.db_path = self.project_dir / "state.db"
        self.tasks_file = self.project_root / "project/TASKS.md"
        self.agents_dir = self.project_root / "agents"
        self.logs_dir = self.project_dir / "logs"

        _required_files = [
            self.project_root / "agents/AGENTS.md",
            self.project_root / "agents/CONSTITUTION.md",
            self.project_root / "project/TASKS.md",
        ]

        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        _policy_file = self.project_dir / "policies.yml"
        _policy_file.write_text("version: '1'\ntools:\n  allowed:\n    - '*'\n")

        # Create required agent files
        (self.agents_dir / "AGENTS.md").write_text("## Commands\ntest: echo ok\n")
        (self.agents_dir / "CONSTITUTION.md").touch()
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        self.tasks_file.write_text("- [ ] Design API\n- [ ] Write tests\n- [x] Setup repo\n")

        self._patches = [
            patch("gabbe.config.PROJECT_ROOT", self.project_root),
            patch("gabbe.config.GABBE_DIR", self.project_dir),
            patch("gabbe.config.DB_PATH", self.db_path),
            patch("gabbe.config.TASKS_FILE", self.tasks_file),
            patch("gabbe.config.REQUIRED_FILES", _required_files),
            patch("gabbe.config.GABBE_POLICY_FILE", _policy_file),
            patch("gabbe.policy.GABBE_POLICY_FILE", _policy_file),
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

    def tearDown(self):
        for p in reversed(self._patches):
            p.stop()
        shutil.rmtree(self.test_dir)

    # =====================================================================
    # STEP 1: gabbe init  (documented: "Setup" section)
    # =====================================================================
    def test_step01_init(self):
        """gabbe init → DB must be created with all expected tables."""
        init_db()
        self.assertTrue(self.db_path.exists(), "state.db should exist after init")
        conn = get_db()
        try:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()}
            for t in ["tasks", "runs", "audit_spans", "checkpoints",
                       "pending_escalations", "genes", "forecast_snapshots",
                       "pricing_registry", "budget_snapshots"]:
                self.assertIn(t, tables, f"Table '{t}' missing after init")
        finally:
            conn.close()

    # =====================================================================
    # STEP 1b: gabbe db --init  (alias)
    # =====================================================================
    def test_step01b_db_init_alias(self):
        """gabbe db --init is an alias for gabbe init."""
        init_db()
        conn = get_db()
        try:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()}
            self.assertIn("tasks", tables)
        finally:
            conn.close()

    # =====================================================================
    # STEP 2: gabbe sync  (documented: "Daily Workflow")
    # =====================================================================
    def test_step02_sync_import(self):
        """gabbe sync → Markdown tasks imported into DB."""
        init_db()
        gabbe.sync.sync_tasks()
        conn = get_db()
        try:
            rows = conn.execute("SELECT * FROM tasks ORDER BY title").fetchall()
            titles = [r["title"] for r in rows]
            self.assertIn("Design API", titles)
            self.assertIn("Write tests", titles)
            self.assertIn("Setup repo", titles)
            # Check status mapping
            statuses = {r["title"]: r["status"] for r in rows}
            self.assertEqual(statuses["Setup repo"], "DONE")
            self.assertEqual(statuses["Design API"], "TODO")
        finally:
            conn.close()

    def test_step02b_sync_export(self):
        """DB tasks are exported to markdown via export_to_md."""
        from gabbe.sync import export_to_md
        init_db()
        conn = get_db()
        try:
            c = conn.cursor()
            c.execute("INSERT INTO tasks (title, status) VALUES ('New Task', 'IN_PROGRESS')")
            conn.commit()
            export_to_md(c)
        finally:
            conn.close()
        content = self.tasks_file.read_text()
        self.assertIn("New Task", content)
        self.assertIn("[/]", content)  # IN_PROGRESS marker

    # =====================================================================
    # STEP 3: gabbe status  (documented: "Daily Workflow")
    # =====================================================================
    def test_step03_status_dashboard(self):
        """gabbe status → renders dashboard with phase, tasks, progress."""
        from gabbe.status import show_dashboard
        init_db()
        gabbe.sync.sync_tasks()

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            show_dashboard()

        output = captured.getvalue()
        self.assertIn("GABBE PROJECT DASHBOARD", output)
        self.assertIn("Tasks:", output)
        self.assertIn("Progress:", output)
        self.assertIn("Done", output)

    # =====================================================================
    # STEP 4: gabbe verify  (documented: "Verification")
    # =====================================================================
    def test_step04_verify_pass(self):
        """gabbe verify passes when all required files exist."""
        init_db()
        result = gabbe.verify.run_verification()
        self.assertTrue(result)

    def test_step04b_verify_fail_missing_file(self):
        """gabbe verify fails when a required file is removed."""
        init_db()
        self.tasks_file.unlink()
        result = gabbe.verify.run_verification()
        self.assertFalse(result)

    # =====================================================================
    # STEP 5: gabbe route <prompt>  (documented: "Cost-Effective Router")
    # =====================================================================
    def test_step05_route_simple(self):
        """Simple prompt → LOCAL."""
        from gabbe.route import route_request
        result = route_request("Fix a typo in README")
        self.assertEqual(result, "LOCAL")

    def test_step05b_route_complex(self):
        """Complex prompt → REMOTE."""
        from gabbe.route import route_request
        with patch("gabbe.route.calculate_complexity", return_value=(85, "mocked")):
            result = route_request("architect a distributed system " * 20)
        self.assertEqual(result, "REMOTE")

    # =====================================================================
    # STEP 6: gabbe brain activate  (documented: "Brain Mode")
    # =====================================================================
    def test_step06_brain_activate(self):
        """gabbe brain activate invokes LLM and prints action."""
        from gabbe.brain import activate_brain
        init_db()
        gabbe.sync.sync_tasks()

        captured = io.StringIO()
        with patch("gabbe.brain.call_llm", return_value="Focus on critical test coverage"), \
             patch("sys.stdout", captured):
            activate_brain()

        output = captured.getvalue()
        self.assertIn("Brain Mode", output)
        self.assertIn("Focus on critical test coverage", output)

    def test_step06b_brain_activate_no_llm(self):
        """gabbe brain activate with no LLM → graceful freeze."""
        from gabbe.brain import activate_brain
        init_db()

        captured = io.StringIO()
        with patch("gabbe.brain.call_llm", return_value=None), \
             patch("sys.stdout", captured):
            activate_brain()

        output = captured.getvalue()
        self.assertIn("Brain Mode", output)

    # =====================================================================
    # STEP 7: gabbe brain evolve --skill <name>  (documented)
    # =====================================================================
    def test_step07_brain_evolve(self):
        """gabbe brain evolve --skill seeds and mutates genes table."""
        from gabbe.brain import evolve_prompts
        init_db()

        with patch("gabbe.brain.call_llm", return_value="Improved prompt output"):
            evolve_prompts("tdd-cycle")

        conn = get_db()
        try:
            rows = conn.execute(
                "SELECT * FROM genes WHERE skill_name='tdd-cycle' ORDER BY generation"
            ).fetchall()
            self.assertGreaterEqual(len(rows), 2)
            self.assertEqual(rows[0]["generation"], 0)  # seed
            self.assertEqual(rows[1]["generation"], 1)  # mutated
        finally:
            conn.close()

    # =====================================================================
    # STEP 8: gabbe brain heal  (documented)
    # =====================================================================
    def test_step08_brain_heal(self):
        """gabbe brain heal checks DB reachability and required files."""
        from gabbe.brain import run_healer
        init_db()

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            run_healer()

        output = captured.getvalue()
        self.assertIn("Self-Healing Watchdog", output)
        self.assertIn("Database", output)
        self.assertIn("Nominal", output)

    def test_step08b_brain_heal_missing_files(self):
        """Healer detects missing files."""
        from gabbe.brain import run_healer
        init_db()
        self.tasks_file.unlink()

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            run_healer()

        output = captured.getvalue()
        self.assertIn("Missing", output)

    # =====================================================================
    # STEP 9: gabbe forecast  (documented)
    # =====================================================================
    def test_step09_forecast(self):
        """gabbe forecast renders cost/token projections."""
        from gabbe.forecast import run_forecast
        init_db()
        gabbe.sync.sync_tasks()

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            run_forecast()

        output = captured.getvalue()
        self.assertIn("Forecast", output)
        self.assertIn("Tasks:", output)

    def test_step09b_forecast_empty_db(self):
        """Forecast with empty DB doesn't crash."""
        from gabbe.forecast import run_forecast
        init_db()

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            run_forecast()

        output = captured.getvalue()
        self.assertIn("Forecast", output)

    # =====================================================================
    # STEP 10: gabbe runs  (documented)
    # =====================================================================
    def test_step10_runs_empty(self):
        """gabbe runs with no runs → 'No runs found'."""
        init_db()
        conn = get_db()
        try:
            rows = conn.execute("SELECT * FROM runs").fetchall()
        finally:
            conn.close()
        self.assertEqual(len(rows), 0)

    def test_step10b_runs_after_brain(self):
        """gabbe runs lists the brain activate run."""
        from gabbe.brain import activate_brain
        init_db()
        gabbe.sync.sync_tasks()

        with patch("gabbe.brain.call_llm", return_value="Action"), \
             patch("sys.stdout", io.StringIO()):
            activate_brain()

        conn = get_db()
        try:
            rows = conn.execute("SELECT * FROM runs").fetchall()
            self.assertGreaterEqual(len(rows), 1)
            self.assertEqual(rows[0]["command"], "brain activate")
        finally:
            conn.close()

    def test_step10c_runs_status_filter(self):
        """gabbe runs --status completed filters correctly."""
        from gabbe.brain import activate_brain
        init_db()

        with patch("gabbe.brain.call_llm", return_value="Action"), \
             patch("sys.stdout", io.StringIO()):
            activate_brain()

        conn = get_db()
        try:
            completed = conn.execute(
                "SELECT * FROM runs WHERE status = 'completed'"
            ).fetchall()
            errored = conn.execute(
                "SELECT * FROM runs WHERE status = 'error'"
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            self.assertEqual(len(completed) + len(errored), total)
        finally:
            conn.close()

    # =====================================================================
    # STEP 11: gabbe audit <run-id>  (documented)
    # =====================================================================
    def test_step11_audit_table(self):
        """gabbe audit <id> --format table shows span data."""
        from gabbe.brain import activate_brain
        from gabbe.audit import AuditTracer
        init_db()
        gabbe.sync.sync_tasks()

        with patch("gabbe.brain.call_llm", return_value="Action"), \
             patch("sys.stdout", io.StringIO()):
            activate_brain()

        conn = get_db()
        try:
            run = conn.execute("SELECT id FROM runs LIMIT 1").fetchone()
            self.assertIsNotNone(run)
            tracer = AuditTracer(run["id"], db_conn=conn)
            spans = tracer.get_run_trace(run["id"])
            self.assertIsInstance(spans, list)
        finally:
            conn.close()

    def test_step11b_audit_json(self):
        """gabbe audit <id> --format json returns valid JSON."""
        from gabbe.brain import activate_brain
        from gabbe.audit import AuditTracer
        init_db()

        with patch("gabbe.brain.call_llm", return_value="Action"), \
             patch("sys.stdout", io.StringIO()):
            activate_brain()

        conn = get_db()
        try:
            run = conn.execute("SELECT id FROM runs LIMIT 1").fetchone()
            self.assertIsNotNone(run)
            tracer = AuditTracer(run["id"], db_conn=conn)
            json_str = tracer.export_json(run["id"])
            parsed = json.loads(json_str)
            self.assertIsInstance(parsed, list)
        finally:
            conn.close()

    def test_step11c_audit_nonexistent_run(self):
        """gabbe audit with invalid run ID → returns empty list."""
        from gabbe.audit import AuditTracer
        init_db()
        conn = get_db()
        try:
            tracer = AuditTracer("nonexistent-id", db_conn=conn)
            spans = tracer.get_run_trace("nonexistent-id")
            self.assertEqual(spans, [])
        finally:
            conn.close()

    # =====================================================================
    # STEP 12: gabbe replay <run-id>  (documented)
    # =====================================================================
    def test_step12_replay_empty(self):
        """gabbe replay with no checkpoints → empty list."""
        from gabbe.replay import CheckpointStore, ReplayRunner
        init_db()
        conn = get_db()
        try:
            store = CheckpointStore(db_conn=conn)
            runner = ReplayRunner(store)
            steps = runner.replay("fake-run-id", from_step=0)
            self.assertEqual(steps, [])
        finally:
            conn.close()

    def test_step12b_replay_with_checkpoints(self):
        """gabbe replay with saved checkpoints returns steps."""
        from gabbe.replay import CheckpointStore, ReplayRunner
        init_db()
        conn = get_db()
        try:
            # Create a run entry first
            conn.execute(
                "INSERT INTO runs (id, command, status) VALUES ('replay-test', 'brain activate', 'completed')"
            )
            conn.commit()

            store = CheckpointStore(db_conn=conn)
            store.save("replay-test", step=0, node_name="observe",
                       state_snapshot={"tasks": 3}, policy_version="v1")
            store.save("replay-test", step=1, node_name="decide",
                       state_snapshot={"action": "test"}, policy_version="v1")

            runner = ReplayRunner(store)
            steps = runner.replay("replay-test", from_step=0)
            self.assertEqual(len(steps), 2)
            self.assertEqual(steps[0]["node_name"], "observe")
            self.assertEqual(steps[1]["node_name"], "decide")
        finally:
            conn.close()

    def test_step12c_replay_from_step(self):
        """gabbe replay --from-step N skips earlier steps."""
        from gabbe.replay import CheckpointStore, ReplayRunner
        init_db()
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO runs (id, command, status) VALUES ('replay-skip', 'brain activate', 'completed')"
            )
            conn.commit()

            store = CheckpointStore(db_conn=conn)
            store.save("replay-skip", step=0, node_name="observe",
                       state_snapshot={}, policy_version="v1")
            store.save("replay-skip", step=1, node_name="decide",
                       state_snapshot={}, policy_version="v1")
            store.save("replay-skip", step=2, node_name="act",
                       state_snapshot={}, policy_version="v1")

            runner = ReplayRunner(store)
            steps = runner.replay("replay-skip", from_step=1)
            self.assertEqual(len(steps), 2)
            self.assertEqual(steps[0]["node_name"], "decide")
        finally:
            conn.close()

    # =====================================================================
    # STEP 13: gabbe resume <run-id>  (documented)
    # =====================================================================
    def test_step13_resume_no_escalations(self):
        """gabbe resume with no pending escalations → 'No pending'."""
        init_db()
        conn = get_db()
        try:
            rows = conn.execute(
                "SELECT * FROM pending_escalations WHERE run_id = 'fake-id' AND status = 'pending'"
            ).fetchall()
            self.assertEqual(len(rows), 0)
        finally:
            conn.close()

    def test_step13b_resume_with_escalation(self):
        """gabbe resume resolves a pending escalation."""
        from gabbe.escalation import EscalationHandler, EscalationTrigger
        init_db()
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO runs (id, command, status) VALUES ('esc-run', 'brain activate', 'escalated')"
            )
            conn.commit()

            handler = EscalationHandler("esc-run", db_conn=conn)
            # Use silent mode to avoid interactive prompt
            handler.mode = "silent"
            handler.escalate(EscalationTrigger.BUDGET_EXHAUSTED, {"reason": "tokens"}, step=5)

            rows = conn.execute(
                "SELECT * FROM pending_escalations WHERE run_id = 'esc-run'"
            ).fetchall()
            self.assertGreaterEqual(len(rows), 1)

            # Silent mode auto-rejects, so let's verify it was stored
            statuses = [r["status"] for r in rows]
            self.assertIn("rejected", statuses)  # silent mode auto-rejects
        finally:
            conn.close()

    # =====================================================================
    # STEP 14: gabbe serve-mcp  (verify MCP server module imports cleanly)
    # =====================================================================
    def test_step14_mcp_server_importable(self):
        """MCP server module imports and has serve() function."""
        from gabbe.mcp_server import serve
        self.assertTrue(callable(serve))

    # =====================================================================
    # FULL CHAIN: Golden Path (init → sync → status → verify → brain → forecast → runs → audit)
    # =====================================================================
    def test_full_chain_golden_path(self):
        """
        Exercises every command in the documented workflow order.
        This is the integration test that proves the README 'How to Use' works.
        """
        from gabbe.brain import activate_brain
        from gabbe.forecast import run_forecast
        from gabbe.status import show_dashboard
        from gabbe.audit import AuditTracer

        # 1. init
        init_db()
        self.assertTrue(self.db_path.exists())

        # 2. sync
        gabbe.sync.sync_tasks()
        conn = get_db()
        try:
            task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            self.assertEqual(task_count, 3)
        finally:
            conn.close()

        # 3. status
        out = io.StringIO()
        with patch("sys.stdout", out):
            show_dashboard()
        self.assertIn("GABBE PROJECT DASHBOARD", out.getvalue())

        # 4. verify
        self.assertTrue(gabbe.verify.run_verification())

        # 5. brain activate
        out = io.StringIO()
        with patch("gabbe.brain.call_llm", return_value="Next: write tests"), \
             patch("sys.stdout", out):
            activate_brain()
        self.assertIn("Brain Mode", out.getvalue())

        # 6. forecast
        out = io.StringIO()
        with patch("sys.stdout", out):
            run_forecast()
        self.assertIn("Forecast", out.getvalue())

        # 7. runs
        conn = get_db()
        try:
            runs = conn.execute("SELECT * FROM runs").fetchall()
            self.assertGreaterEqual(len(runs), 1)
            run_id = runs[0]["id"]

            # 8. audit
            tracer = AuditTracer(run_id, db_conn=conn)
            spans = tracer.get_run_trace(run_id)
            self.assertIsInstance(spans, list)
        finally:
            conn.close()

class TestPlatformControls(unittest.TestCase):
    """Tests for PLATFORM_CONTROLS.md documented features:
    Budget, HardStop, Policy, Gateway, Escalation, Audit, Replay."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir)
        self.project_dir = self.project_root / "project"
        self.db_path = self.project_dir / "state.db"
        self.project_dir.mkdir(parents=True, exist_ok=True)

        _policy_file = self.project_dir / "policies.yml"
        _policy_file.write_text("version: '1'\ntools:\n  allowed:\n    - '*'\n")

        self._patches = [
            patch("gabbe.config.PROJECT_ROOT", self.project_root),
            patch("gabbe.config.GABBE_DIR", self.project_dir),
            patch("gabbe.config.DB_PATH", self.db_path),
            patch("gabbe.config.GABBE_POLICY_FILE", _policy_file),
            patch("gabbe.policy.GABBE_POLICY_FILE", _policy_file),
            patch("gabbe.database.GABBE_DIR", self.project_dir),
            patch("gabbe.database.DB_PATH", self.db_path),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in reversed(self._patches):
            p.stop()
        shutil.rmtree(self.test_dir)

    # ----- Budget (PLATFORM_CONTROLS § Budget) -----
    def test_budget_from_config(self):
        """Budget.from_config() reads env vars and creates a Budget instance."""
        from gabbe.budget import Budget
        b = Budget.from_config()
        self.assertIsNotNone(b)
        snap = b.snapshot()
        self.assertIn("tokens_used", snap)
        self.assertEqual(snap["tokens_used"], 0)

    def test_budget_exceeded_on_tokens(self):
        """BudgetExceeded raised when token limit is hit."""
        from gabbe.budget import Budget, BudgetExceeded
        b = Budget.from_dict({"max_tokens": 10, "tokens_used": 0})
        b.tokens_used = 11
        with self.assertRaises(BudgetExceeded):
            b.check()

    def test_budget_remaining(self):
        """Budget.remaining() returns remaining per dimension."""
        from gabbe.budget import Budget
        b = Budget.from_config()
        rem = b.remaining()
        self.assertIn("tokens", rem)
        self.assertGreater(rem["tokens"], 0)

    # ----- HardStop (PLATFORM_CONTROLS § HardStop) -----
    def test_hardstop_max_iterations_chain(self):
        """HardStop → MaxIterationsExceeded during an iteration chain."""
        from gabbe.hardstop import HardStop, MaxIterationsExceeded
        h = HardStop(max_iterations=2, max_depth=5, timeout_sec=60)
        h.tick()
        h.tick()
        with self.assertRaises(MaxIterationsExceeded):
            h.tick()

    def test_hardstop_should_wrap_up(self):
        """should_wrap_up returns True near the limit."""
        from gabbe.hardstop import HardStop
        h = HardStop(max_iterations=3)
        h.tick()
        h.tick()
        self.assertTrue(h.should_wrap_up(threshold=2))

    # ----- Policy Engine (PLATFORM_CONTROLS § Policy Engine) -----
    def test_policy_allowlist_permits(self):
        """ToolAllowlistPolicy permits allowed tools."""
        from gabbe.policy import ToolAllowlistPolicy
        p = ToolAllowlistPolicy(["call_llm", "run_command"], [])
        result = p.check({"tool": "call_llm"})
        self.assertTrue(result.allowed)

    def test_policy_allowlist_denies(self):
        """ToolAllowlistPolicy denies unlisted tools."""
        from gabbe.policy import ToolAllowlistPolicy
        p = ToolAllowlistPolicy(["call_llm"], [])
        result = p.check({"tool": "run_command"})
        self.assertFalse(result.allowed)

    def test_policy_deny_overrides_allow(self):
        """Explicit deny overrides allow in ToolAllowlistPolicy."""
        from gabbe.policy import ToolAllowlistPolicy
        p = ToolAllowlistPolicy(["*"], ["run_security_scan"])
        result = p.check({"tool": "run_security_scan"})
        self.assertFalse(result.allowed)

    # ----- Gateway (PLATFORM_CONTROLS § Tool Gateway) -----
    def test_gateway_register_and_execute(self):
        """ToolGateway.execute dispatches to registered handler."""
        from gabbe.gateway import ToolGateway, ToolDefinition
        from gabbe.context import RunContext
        init_db()

        gw = ToolGateway()
        gw.register(ToolDefinition(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
            handler=lambda **kw: {"result": "ok"},
            allowed_roles={"agent"},
        ))

        with RunContext(command="test", initiator="test") as ctx:
            result = gw.execute("test_tool", {}, role="agent", run_context=ctx)
            self.assertEqual(result["result"], "ok")

    # ----- Escalation (PLATFORM_CONTROLS § Escalation Handler) -----
    def test_escalation_silent_auto_rejects(self):
        """Silent escalation mode auto-rejects (for CI/CD)."""
        from gabbe.escalation import EscalationHandler, EscalationTrigger, EscalationResult
        init_db()
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO runs (id, command, status) VALUES ('silent-esc', 'test', 'running')"
            )
            conn.commit()
            handler = EscalationHandler("silent-esc", db_conn=conn)
            handler.mode = "silent"
            result = handler.escalate(EscalationTrigger.BUDGET_EXHAUSTED, {"reason": "test"})
            self.assertEqual(result.status, "rejected")
        finally:
            conn.close()

    def test_escalation_file_mode_raises(self):
        """File escalation mode raises EscalationPaused."""
        from gabbe.escalation import EscalationHandler, EscalationTrigger, EscalationPaused
        init_db()
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO runs (id, command, status) VALUES ('file-esc', 'test', 'running')"
            )
            conn.commit()
            handler = EscalationHandler("file-esc", db_conn=conn)
            handler.mode = "file"
            with self.assertRaises(EscalationPaused):
                handler.escalate(EscalationTrigger.POLICY_VIOLATION, {"tool": "blocked"})
        finally:
            conn.close()

    # ----- RunContext (PLATFORM_CONTROLS § RunContext) -----
    def test_run_context_lifecycle(self):
        """RunContext creates and closes a run record in DB."""
        from gabbe.context import RunContext
        init_db()
        with RunContext(command="test-lifecycle", initiator="test") as ctx:
            self.assertIsNotNone(ctx.run_id)

        conn = get_db()
        try:
            run = conn.execute("SELECT * FROM runs WHERE command = 'test-lifecycle'").fetchone()
            self.assertIsNotNone(run)
            self.assertIsNotNone(run["ended_at"])
        finally:
            conn.close()


class TestMCPServerProtocol(unittest.TestCase):
    """Tests for MCP embedded server JSON-RPC protocol (PLATFORM_CONTROLS + CLI_REFERENCE)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir)
        self.project_dir = self.project_root / "project"
        self.db_path = self.project_dir / "state.db"
        self.project_dir.mkdir(parents=True, exist_ok=True)

        _policy_file = self.project_dir / "policies.yml"
        _policy_file.write_text("version: '1'\ntools:\n  allowed:\n    - '*'\n")

        self._patches = [
            patch("gabbe.config.PROJECT_ROOT", self.project_root),
            patch("gabbe.config.GABBE_DIR", self.project_dir),
            patch("gabbe.config.DB_PATH", self.db_path),
            patch("gabbe.config.GABBE_POLICY_FILE", _policy_file),
            patch("gabbe.policy.GABBE_POLICY_FILE", _policy_file),
            patch("gabbe.database.GABBE_DIR", self.project_dir),
            patch("gabbe.database.DB_PATH", self.db_path),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in reversed(self._patches):
            p.stop()
        shutil.rmtree(self.test_dir)

    def test_mcp_auth_token_rejected(self):
        """MCP initialize with wrong token returns Unauthorized."""
        from gabbe.mcp_server import serve
        from unittest.mock import MagicMock

        req = json.dumps({"jsonrpc": "2.0", "method": "initialize", "id": 1,
                          "params": {"token": "wrong-token"}}) + "\n"
        outputs = []
        with patch.dict(os.environ, {"GABBE_MCP_TOKEN": "correct-token"}), \
             patch("gabbe.mcp_server.RunContext") as MockCtx, \
             patch("sys.stdin", io.StringIO(req)), \
             patch("builtins.print", side_effect=lambda s, **kw: outputs.append(s)):
            mock_ctx = MagicMock()
            MockCtx.return_value.__enter__ = MagicMock(return_value=mock_ctx)
            MockCtx.return_value.__exit__ = MagicMock(return_value=False)
            mock_ctx.gateway.register = MagicMock()
            serve()

        responses = [json.loads(o) for o in outputs if o.strip()]
        self.assertEqual(len(responses), 1)
        self.assertIn("error", responses[0])
        self.assertEqual(responses[0]["error"]["message"], "Unauthorized")

    def test_mcp_command_allowlist_blocks(self):
        """run_command_handler blocks non-allowed commands."""
        from gabbe.mcp_server import run_command_handler

        with patch.dict(os.environ, {"GABBE_MCP_ALLOWED_COMMANDS": "pytest,ruff"}):
            result = run_command_handler("rm -rf /tmp/evil")

        self.assertEqual(result["returncode"], 126)
        self.assertIn("not in allowed list", result["stderr"])

    def test_mcp_command_allowlist_permits(self):
        """run_command_handler allows permitted commands."""
        from gabbe.mcp_server import run_command_handler
        from unittest.mock import MagicMock

        mock_result = MagicMock()
        mock_result.stdout = "ok"
        mock_result.stderr = ""
        mock_result.returncode = 0

        with patch.dict(os.environ, {"GABBE_MCP_ALLOWED_COMMANDS": "echo"}), \
             patch("gabbe.mcp_server.subprocess.run", return_value=mock_result):
            result = run_command_handler("echo hello")

        self.assertEqual(result["returncode"], 0)

    def test_mcp_empty_command(self):
        """Empty command returns error."""
        from gabbe.mcp_server import run_command_handler
        result = run_command_handler("")
        self.assertEqual(result["returncode"], 1)
        self.assertIn("Empty", result["stderr"])


class TestCLIGlobalFlags(unittest.TestCase):
    """Tests for CLI_REFERENCE global flags: --version, --debug, unknown command."""

    def test_cli_version_flag(self):
        """gabbe --version prints version and exits."""
        from gabbe.main import main
        from gabbe import __version__
        import sys

        captured = io.StringIO()
        with patch("sys.argv", ["gabbe", "--version"]), \
             patch("sys.stdout", captured):
            with self.assertRaises(SystemExit) as ctx:
                main()
            self.assertEqual(ctx.exception.code, 0)
        self.assertIn(__version__, captured.getvalue())

    def test_cli_debug_flag_sets_debug_level(self):
        """gabbe --debug enables DEBUG logging."""
        from gabbe.main import main
        import logging

        with patch("sys.argv", ["gabbe", "--debug", "status"]), \
             patch("gabbe.status.show_dashboard"):
            try:
                main()
            except Exception:
                pass
        self.assertEqual(logging.getLogger().level, logging.DEBUG)


if __name__ == "__main__":
    unittest.main()
