from __future__ import annotations
import json
import logging
import sqlite3
import time
import uuid
from functools import wraps
from datetime import datetime, timezone
from .database import get_db
from .config import GABBE_DIR, GABBE_OTEL_ENABLED

# Set up local text logger
logger = logging.getLogger("gabbe.audit")

if GABBE_OTEL_ENABLED:
    try:
        from opentelemetry import trace  # type: ignore
        from opentelemetry.trace import Status, StatusCode  # type: ignore
        otel_tracer = trace.get_tracer("gabbe.tracer")
    except ImportError:
        otel_tracer = None
        logger.warning("OpenTelemetry enabled but SDK not installed.")
else:
    otel_tracer = None


class AuditTracer:
    def __init__(self, run_id: str, db_conn=None):
        self.run_id = run_id
        # We use a new connection if none provided
        self._owns_db = False
        if db_conn is None:
            self.db_conn = get_db()
            self._owns_db = True
        else:
            self.db_conn = db_conn

        self.log_dir = GABBE_DIR / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.log_dir / f"run_{self.run_id}.jsonl"

    def __del__(self):
        if getattr(self, "_owns_db", False) and getattr(self, "db_conn", None):
            self.db_conn.close()

    def _log_jsonl(self, record):
        try:
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, default=str) + "\n")
        except Exception as e:
            logger.error(f"Failed to write JSONL log: {e}")

    def start_span(self, event_type: str, node_name: str, input_data: dict, parent_span_id: str | None = None):
        span_id = uuid.uuid4().hex[:16]
        start_time = time.monotonic()
        
        # OTel Span
        db_otel_span = None
        if otel_tracer:
            # We don't yield context here to keep it simple, just start and store
            db_otel_span = otel_tracer.start_span(f"{event_type}:{node_name}")
            db_otel_span.set_attribute("gabbe.run_id", self.run_id)
            db_otel_span.set_attribute("gabbe.span_id", span_id)
            db_otel_span.set_attribute("gabbe.input", json.dumps(input_data))

        return {"span_id": span_id, "start_time": start_time, "event_type": event_type, 
                "node_name": node_name, "input_data": input_data, "parent_span_id": parent_span_id,
                "_otel_span": db_otel_span}

    def end_span(self, span_ctx: dict, output_data: dict | None = None, reasoning_content: str | None = None, 
                 model_name: str | None = None, token_usage: dict | None = None, cost_usd: float = 0.0, 
                 status: str = "ok", metadata: dict | None = None):
        
        duration_ms = (time.monotonic() - span_ctx["start_time"]) * 1000
        timestamp = datetime.now(timezone.utc).isoformat()
        
        token_usage = token_usage or {}
        p_tokens = token_usage.get("prompt_tokens", 0)
        c_tokens = token_usage.get("completion_tokens", 0)
        r_tokens = token_usage.get("reasoning_tokens", 0)
        ch_tokens = token_usage.get("cache_hit_tokens", 0)

        # 1. SQLite Write
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO audit_spans 
                (run_id, span_id, parent_span_id, timestamp, event_type, node_name, 
                 input_data, output_data, reasoning_content, model_name, 
                 prompt_tokens, completion_tokens, reasoning_tokens, cache_hit_tokens, 
                 cost_usd, duration_ms, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.run_id, span_ctx["span_id"], span_ctx["parent_span_id"], timestamp, 
                span_ctx["event_type"], span_ctx["node_name"],
                json.dumps(span_ctx["input_data"]) if span_ctx["input_data"] else None,
                json.dumps(output_data) if output_data else None,
                reasoning_content, model_name,
                p_tokens, c_tokens, r_tokens, ch_tokens,
                cost_usd, duration_ms, status, 
                json.dumps(metadata) if metadata else None
            ))
            self.db_conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to record audit span to DB: {e}")

        # 2. JSONL Write
        record = {
            "run_id": self.run_id,
            "span_id": span_ctx["span_id"],
            "parent_span_id": span_ctx["parent_span_id"],
            "timestamp": timestamp,
            "event_type": span_ctx["event_type"],
            "node_name": span_ctx["node_name"],
            "input_data": span_ctx["input_data"],
            "output_data": output_data,
            "reasoning_content": reasoning_content,
            "metrics": {
                "duration_ms": duration_ms,
                "cost_usd": cost_usd,
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "reasoning_tokens": r_tokens
            },
            "status": status,
            "metadata": metadata
        }
        self._log_jsonl(record)
        
        # 3. Simple Text Log
        logger.info(f"[{span_ctx['event_type']}] {span_ctx['node_name']} completed in {duration_ms:.2f}ms with status {status}. Cost: ${cost_usd:.6f}")

        # 4. OTel Complete
        if span_ctx.get("_otel_span"):
            otel_span = span_ctx["_otel_span"]
            if status != "ok":
                otel_span.set_status(Status(StatusCode.ERROR))
            otel_span.set_attribute("gabbe.output", json.dumps(output_data))
            otel_span.set_attribute("gabbe.cost_usd", cost_usd)
            otel_span.end()
            
    def snapshot_budget(self, step: int, budget):
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO budget_snapshots
                (run_id, step, tokens_used, tool_calls_used, wall_time_sec, iterations)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.run_id, step, budget.tokens_used, budget.tool_calls_used,
                budget.snapshot()["wall_time_sec"], budget.iterations
            ))
            self.db_conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to snapshot budget: {e}")

    def get_run_trace(self, run_id: str) -> list:
        """Return all audit spans for a run as a list of dicts, ordered by timestamp."""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT * FROM audit_spans WHERE run_id = ? ORDER BY id ASC
            """, (run_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to get run trace: {e}")
            return []

    def export_json(self, run_id: str) -> str:
        """Return the full run trace as a JSON string."""
        return json.dumps(self.get_run_trace(run_id), default=str, indent=2)


def traced(event_type: str, node_name: str | None = None):
    """Decorator that wraps a function in an audit span if run_context is passed as kwarg."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            run_context = kwargs.get("run_context")
            if run_context is None:
                # Try positional arg that has a .tracer attribute
                for a in args:
                    if hasattr(a, "tracer"):
                        run_context = a
                        break
            if run_context is not None:
                name = node_name or func.__name__
                span = run_context.tracer.start_span(event_type, name, {})
                try:
                    result = func(*args, **kwargs)
                    run_context.tracer.end_span(span, output_data={"ok": True}, status="ok")
                    return result
                except Exception as exc:
                    run_context.tracer.end_span(span, output_data={"error": str(exc)}, status="error")
                    raise
            return func(*args, **kwargs)
        return wrapper
    return decorator
