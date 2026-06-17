# SPDX-License-Identifier: Apache-2.0
"""Chaos / fault-injection tests (Track B Phase 2).

Inject realistic faults (subprocess timeout, sqlite OperationalError mid-txn, LLM
failure, repeated tool failure) and assert GABBE degrades gracefully — timeout
codes, handled DB errors, heuristic fallback, and escalation — never an
unhandled crash or infinite loop. These map fault recipes to expected recovery,
the discipline taught by `chaos-fault-injection.skill`.
"""

import sqlite3
import subprocess
from unittest.mock import MagicMock, patch

from gabbe.escalation import EscalationHandler, EscalationTrigger


def test_mcp_command_timeout_returns_124(tmp_project):
    from gabbe.mcp_server import run_command_handler

    with patch.dict("os.environ", {"GABBE_MCP_ALLOWED_COMMANDS": "sleep"}):
        with patch(
            "gabbe.mcp_server.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="sleep", timeout=1),
        ):
            result = run_command_handler("sleep 999")
    assert result["returncode"] == 124  # graceful timeout, not a hang/crash


def test_sqlite_operationalerror_during_escalation_is_handled(tmp_project):
    # A DB fault mid-escalation must be caught (logged), not propagated as a crash.
    bad_conn = MagicMock()
    bad_conn.cursor.side_effect = sqlite3.OperationalError("disk I/O error")
    with patch("gabbe.escalation.GABBE_ESCALATION_MODE", "silent"):
        handler = EscalationHandler("run-chaos-db", db_conn=bad_conn)
        result = handler.escalate(EscalationTrigger.POLICY_VIOLATION, {"x": 1})
    # Returns a normal silent-mode result despite the injected DB failure.
    assert result.status == "rejected"


def test_llm_failure_falls_back_to_heuristic(tmp_project):
    from gabbe import route

    long_prompt = "architect a large distributed system. " + ("detail " * 120)
    with patch.object(route, "call_llm", side_effect=RuntimeError("provider down")):
        score, reason = route.calculate_complexity(long_prompt)
    # The fallback heuristic still produces a usable REMOTE-grade score, no crash.
    assert score >= 60
    assert "Fallback" in reason


def test_repeated_tool_failure_escalates(tmp_project, db_conn):
    failures = 0
    with patch("gabbe.escalation.GABBE_ESCALATION_MODE", "silent"):
        handler = EscalationHandler("run-chaos-repeat", db_conn=db_conn)
        for _ in range(3):
            failures += 1  # simulate a tool that keeps failing
        if failures >= 3:
            handler.escalate(EscalationTrigger.REPEATED_TOOL_FAILURE, {"failures": failures})
    rows = db_conn.execute(
        "SELECT trigger FROM pending_escalations WHERE run_id='run-chaos-repeat'"
    ).fetchall()
    assert any(r["trigger"] == EscalationTrigger.REPEATED_TOOL_FAILURE.value for r in rows)
