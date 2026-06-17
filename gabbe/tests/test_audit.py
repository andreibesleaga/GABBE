# SPDX-License-Identifier: Apache-2.0
"""Unit tests for gabbe.audit."""

import json

import pytest

from gabbe.audit import AuditTracer
from gabbe.budget import Budget


def test_start_end_span_writes_to_db(tmp_project, db_conn):
    tracer = AuditTracer("run-audit-1", db_conn=db_conn)
    span = tracer.start_span("llm_call", "test_node", {"prompt": "hello"})
    tracer.end_span(span, output_data={"response": "world"}, status="ok")

    rows = db_conn.execute("SELECT * FROM audit_spans WHERE run_id = 'run-audit-1'").fetchall()
    assert len(rows) == 1
    assert rows[0]["event_type"] == "llm_call"
    assert rows[0]["node_name"] == "test_node"
    assert rows[0]["status"] == "ok"
    assert rows[0]["duration_ms"] is not None


def test_start_end_span_writes_jsonl(tmp_project, db_conn):
    tracer = AuditTracer("run-jsonl-1", db_conn=db_conn)
    span = tracer.start_span("tool_call", "my_tool", {"arg": 1})
    tracer.end_span(span, output_data={"result": "done"}, status="ok")

    assert tracer.jsonl_path.exists()
    with open(tracer.jsonl_path, "r") as f:
        lines = f.readlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["event_type"] == "tool_call"
    assert record["node_name"] == "my_tool"
    assert record["status"] == "ok"


def test_span_captures_token_usage(tmp_project, db_conn):
    tracer = AuditTracer("run-tokens-1", db_conn=db_conn)
    span = tracer.start_span("llm_call", "llm", {})
    tracer.end_span(
        span,
        token_usage={"prompt_tokens": 100, "completion_tokens": 50},
        cost_usd=0.005,
        status="ok",
    )
    row = db_conn.execute("SELECT * FROM audit_spans WHERE run_id='run-tokens-1'").fetchone()
    assert row["prompt_tokens"] == 100
    assert row["completion_tokens"] == 50
    assert row["cost_usd"] == pytest.approx(0.005, abs=1e-6)


def test_end_span_error_status(tmp_project, db_conn):
    tracer = AuditTracer("run-err-1", db_conn=db_conn)
    span = tracer.start_span("tool_call", "fail_tool", {})
    tracer.end_span(span, output_data={"error": "timeout"}, status="error")
    row = db_conn.execute("SELECT * FROM audit_spans WHERE run_id='run-err-1'").fetchone()
    assert row["status"] == "error"


def test_snapshot_budget(tmp_project, db_conn):
    tracer = AuditTracer("run-snap-1", db_conn=db_conn)
    b = Budget(max_tokens=1000)
    b.tokens_used = 200
    b.tool_calls_used = 5
    tracer.snapshot_budget(step=3, budget=b)

    row = db_conn.execute("SELECT * FROM budget_snapshots WHERE run_id='run-snap-1'").fetchone()
    assert row["step"] == 3
    assert row["tokens_used"] == 200
    assert row["tool_calls_used"] == 5


def test_get_run_trace(tmp_project, db_conn):
    tracer = AuditTracer("run-trace-1", db_conn=db_conn)
    for i in range(3):
        span = tracer.start_span("step", f"node_{i}", {"i": i})
        tracer.end_span(span, status="ok")

    trace = tracer.get_run_trace("run-trace-1")
    assert len(trace) == 3
    assert all(t["run_id"] == "run-trace-1" for t in trace)
    node_names = [t["node_name"] for t in trace]
    assert "node_0" in node_names
    assert "node_2" in node_names


def test_get_run_trace_empty(tmp_project, db_conn):
    tracer = AuditTracer("run-notexist", db_conn=db_conn)
    trace = tracer.get_run_trace("run-notexist")
    assert trace == []


def test_export_json(tmp_project, db_conn):
    tracer = AuditTracer("run-json-1", db_conn=db_conn)
    span = tracer.start_span("policy_check", "p1", {})
    tracer.end_span(span, status="ok")

    result = tracer.export_json("run-json-1")
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["event_type"] == "policy_check"


def test_multiple_runs_isolated(tmp_project, db_conn):
    tracer_a = AuditTracer("run-A", db_conn=db_conn)
    tracer_b = AuditTracer("run-B", db_conn=db_conn)

    span_a = tracer_a.start_span("step", "node_a", {})
    tracer_a.end_span(span_a, status="ok")

    span_b = tracer_b.start_span("step", "node_b", {})
    tracer_b.end_span(span_b, status="ok")

    trace_a = tracer_a.get_run_trace("run-A")
    trace_b = tracer_b.get_run_trace("run-B")

    assert len(trace_a) == 1 and trace_a[0]["node_name"] == "node_a"
    assert len(trace_b) == 1 and trace_b[0]["node_name"] == "node_b"


# R20: audit-log PII/secret redaction
def test_audit_jsonl_redacts_secrets(tmp_project, tmp_path):
    import json as _json

    from gabbe.audit import AuditTracer

    tracer = AuditTracer(run_id="redact-test")
    tracer._log_jsonl(
        {
            "event_type": "tool_call",
            "input_data": {"prompt": "key sk-or-v1-deadbeefdeadbeef12 email x@y.com"},
            "output_data": {"text": "Bearer abc123tokenvalue9999"},
            "count": 7,
        }
    )
    line = tracer.jsonl_path.read_text().strip()
    rec = _json.loads(line)
    blob = _json.dumps(rec)
    assert "sk-or-v1-" not in blob
    assert "x@y.com" not in blob
    assert "Bearer abc123" not in blob
    assert "[REDACTED]" in blob
    assert rec["count"] == 7  # non-string values preserved


def test_redact_stringifies_and_redacts_non_serializable_objects():
    """A non-JSON-serializable object's __str__ must be redacted by _redact itself,
    so a later json.dumps(default=str) can't smuggle PII/secrets past redaction."""
    from gabbe.audit import _redact

    class Leaky:
        def __str__(self):
            return "email leak@evil.com token sk-or-v1-deadbeefdeadbeef12"

    out = _redact({"obj": Leaky(), "n": 3, "ok": None})
    assert isinstance(out["obj"], str) and "[REDACTED]" in out["obj"]
    assert "leak@evil.com" not in out["obj"] and "sk-or-v1-" not in out["obj"]
    assert out["n"] == 3 and out["ok"] is None  # JSON primitives untouched
    json.dumps(out)  # fully JSON-able after redaction


def test_db_span_redacts_pii_and_secrets(tmp_project, db_conn):
    """Regression: input/output/reasoning/metadata written to the SQLite audit_spans
    table must be redacted (the durable store), matching the JSONL/OTel paths.
    Previously the DB write bypassed _redact(), leaking PII/secrets to state.db."""
    tracer = AuditTracer("redact-db", db_conn=db_conn)
    span = tracer.start_span(
        "llm_call", "node", {"prompt": "key sk-or-v1-deadbeefdeadbeef12 mail x@y.com"}
    )
    tracer.end_span(
        span,
        output_data={"text": "Bearer abc123tokenvalue9999"},
        reasoning_content="contact a@b.com",
        metadata={"note": "AKIAIOSFODNN7EXAMPLE"},
        status="ok",
    )
    row = db_conn.execute(
        "SELECT input_data, output_data, reasoning_content, metadata FROM audit_spans "
        "WHERE run_id='redact-db'"
    ).fetchone()
    blob = " ".join(str(c) for c in row)
    assert "sk-or-v1-" not in blob
    assert "x@y.com" not in blob and "a@b.com" not in blob
    assert "Bearer abc123" not in blob
    assert "AKIAIOSFODNN7EXAMPLE" not in blob
    assert "[REDACTED]" in blob
