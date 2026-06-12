# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from .config import GABBE_DIR, GABBE_OTEL_ENABLED
from .database import get_db

# Set up local text logger
logger = logging.getLogger("gabbe.audit")

# ---------------------------------------------------------------------------
# OpenTelemetry GenAI semantic conventions (book idea 9).
#
# These are the canonical OTel `gen_ai.*` attribute names. Exposing them as
# module-level constants (and a flat dict) keeps observability standards-aligned
# and lets budget/llm callers attach standard attributes without hard-coding
# magic strings. See:
#   https://opentelemetry.io/docs/specs/semconv/gen-ai/
# ---------------------------------------------------------------------------

# Identity / request / response attributes.
GEN_AI_SYSTEM = "gen_ai.system"
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_RESPONSE_MODEL = "gen_ai.response.model"

# Token usage attributes.
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_USAGE_TOTAL_TOKENS = "gen_ai.usage.total_tokens"
# Reasoning tokens (o1/o3-class "thinking" tokens) are a subset of the output
# tokens; reported separately for cost attribution.
GEN_AI_USAGE_REASONING_TOKENS = "gen_ai.usage.reasoning_tokens"
# Cached input tokens — a subset of input tokens served from a prompt cache
# (OpenAI prompt_tokens_details.cached_tokens / Anthropic cache_read_input_tokens).
GEN_AI_USAGE_CACHED_INPUT_TOKENS = "gen_ai.usage.cached_input_tokens"

# Optional content attributes (only set when content capture is enabled).
GEN_AI_PROMPT = "gen_ai.prompt"
GEN_AI_COMPLETION = "gen_ai.completion"

# Flat registry of every GenAI attribute name we emit, keyed by a short logical
# name. Reusable by callers that want to iterate or validate attribute keys.
GEN_AI_ATTRIBUTES: dict[str, str] = {
    "system": GEN_AI_SYSTEM,
    "operation": GEN_AI_OPERATION_NAME,
    "request_model": GEN_AI_REQUEST_MODEL,
    "response_model": GEN_AI_RESPONSE_MODEL,
    "input_tokens": GEN_AI_USAGE_INPUT_TOKENS,
    "output_tokens": GEN_AI_USAGE_OUTPUT_TOKENS,
    "total_tokens": GEN_AI_USAGE_TOTAL_TOKENS,
    "reasoning_tokens": GEN_AI_USAGE_REASONING_TOKENS,
    "cached_input_tokens": GEN_AI_USAGE_CACHED_INPUT_TOKENS,
    "prompt": GEN_AI_PROMPT,
    "completion": GEN_AI_COMPLETION,
}

# Default GenAI system identifier for spans we emit. Callers may override.
GEN_AI_DEFAULT_SYSTEM = "gabbe"

# Extra secret patterns beyond config.PII_PATTERNS (which covers email/phone/
# SSN/credit-card/credential-assignments) — common bearer/API-key token shapes.
_SECRET_PATTERNS = [
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}\b"),  # OpenAI-style keys
    re.compile(r"\bsk-or-v1-[A-Za-z0-9]{16,}\b"),  # OpenRouter keys
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}\b"),  # GitHub tokens
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id
]
_REDACTION = "[REDACTED]"


def _redact_text(value: str) -> str:
    from .config import PII_PATTERNS

    for pat in list(PII_PATTERNS) + _SECRET_PATTERNS:
        value = pat.sub(_REDACTION, value)
    return value


def _redact(obj: Any) -> Any:
    """Recursively redact PII/secret-looking strings in a JSON-able structure
    before it is written to the audit log (honors CONSTITUTION 'no PII logged')."""
    if isinstance(obj, str):
        return _redact_text(obj)
    if isinstance(obj, dict):
        return {k: _redact(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_redact(v) for v in obj]
    if isinstance(obj, (int, float, bool)) or obj is None:
        return obj  # JSON primitives carry no free text to redact
    # Any other type is not guaranteed JSON-serializable. Stringify THEN redact here,
    # so a later json.dumps(..., default=str) can't smuggle PII/secrets through an
    # object's __str__ output without passing through _redact_text().
    return _redact_text(str(obj))


def should_capture_content() -> bool:
    """Whether prompt/response *content* may be captured on GenAI spans.

    Privacy-first: defaults to OFF. Prompts and completions can contain PII or
    secrets, so per the OTel GenAI conventions content capture is opt-in. Enable
    by setting ``GABBE_OTEL_CAPTURE_CONTENT`` to a truthy value (1/true/yes).

    Read from ``os.environ`` directly (not a new config global) so this addition
    stays self-contained inside audit.py and backward-compatible.
    """
    return os.environ.get("GABBE_OTEL_CAPTURE_CONTENT", "false").lower() in (
        "1",
        "true",
        "yes",
    )


def genai_usage_attributes(
    model: str | None,
    usage_dict: dict[str, Any] | None,
    system: str | None = None,
    operation: str | None = None,
    response_model: str | None = None,
) -> dict[str, Any]:
    """Map a usage dict into OTel GenAI semantic-convention attributes.

    ``usage_dict`` follows the same shape ``budget.record_llm_usage`` consumes:
        - total_tokens / prompt_tokens / completion_tokens
        - completion_tokens_details.reasoning_tokens
        - prompt_tokens_details.cached_tokens OR cache_read_input_tokens

    Returns a flat dict keyed by the canonical ``gen_ai.*`` attribute names,
    suitable for ``span.set_attribute`` calls. Pure and easily unit-tested; no
    content is ever included here (only identity + token counts).
    """
    usage_dict = usage_dict or {}

    prompt_tokens = usage_dict.get("prompt_tokens", 0)
    completion_tokens = usage_dict.get("completion_tokens", 0)
    total_tokens = usage_dict.get("total_tokens", 0)
    # Reasoning tokens are reported inside completion_tokens for o1/o3-class models.
    reasoning_tokens = usage_dict.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    # Cached input tokens: OpenAI -> prompt_tokens_details.cached_tokens;
    # Anthropic-style -> cache_read_input_tokens. Support both (mirrors budget.py).
    cached_input_tokens = usage_dict.get("prompt_tokens_details", {}).get(
        "cached_tokens", 0
    ) or usage_dict.get("cache_read_input_tokens", 0)

    attrs: dict[str, Any] = {
        GEN_AI_SYSTEM: system or GEN_AI_DEFAULT_SYSTEM,
        GEN_AI_USAGE_INPUT_TOKENS: prompt_tokens,
        GEN_AI_USAGE_OUTPUT_TOKENS: completion_tokens,
        GEN_AI_USAGE_TOTAL_TOKENS: total_tokens,
        GEN_AI_USAGE_REASONING_TOKENS: reasoning_tokens,
        GEN_AI_USAGE_CACHED_INPUT_TOKENS: cached_input_tokens,
    }
    if model is not None:
        attrs[GEN_AI_REQUEST_MODEL] = model
    if response_model is not None:
        attrs[GEN_AI_RESPONSE_MODEL] = response_model
    if operation is not None:
        attrs[GEN_AI_OPERATION_NAME] = operation
    return attrs


if GABBE_OTEL_ENABLED:
    try:
        from opentelemetry import trace
        from opentelemetry.trace import Status, StatusCode

        otel_tracer = trace.get_tracer("gabbe.tracer")
    except ImportError:
        otel_tracer = None
        logger.warning("OpenTelemetry enabled but SDK not installed.")
else:
    otel_tracer = None


class AuditTracer:
    def __init__(self, run_id: str, db_conn: sqlite3.Connection | None = None) -> None:
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

    def __del__(self) -> None:
        if getattr(self, "_owns_db", False) and getattr(self, "db_conn", None):
            self.db_conn.close()

    def _log_jsonl(self, record: dict[str, Any]) -> None:
        try:
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(_redact(record), default=str) + "\n")
        except Exception as e:
            logger.error(f"Failed to write JSONL log: {e}")

    def start_span(
        self,
        event_type: str,
        node_name: str,
        input_data: dict[str, Any],
        parent_span_id: str | None = None,
    ) -> dict[str, Any]:
        span_id = uuid.uuid4().hex[:16]
        start_time = time.monotonic()
        # Capture wall-clock start time so the DB timestamp reflects when the span began.
        start_wall_time = datetime.now(timezone.utc)

        # OTel Span
        db_otel_span = None
        if otel_tracer:
            # Use start_span (not start_as_current_span) to avoid mutating the OTel
            # context stack, since we manage span lifecycle manually.
            db_otel_span = otel_tracer.start_span(f"{event_type}:{node_name}")
            db_otel_span.set_attribute("gabbe.run_id", self.run_id)
            db_otel_span.set_attribute("gabbe.span_id", span_id)
            db_otel_span.set_attribute("gabbe.input", json.dumps(_redact(input_data), default=str))

        return {
            "span_id": span_id,
            "start_time": start_time,
            "start_wall_time": start_wall_time,
            "event_type": event_type,
            "node_name": node_name,
            "input_data": input_data,
            "parent_span_id": parent_span_id,
            "_otel_span": db_otel_span,
        }

    def end_span(
        self,
        span_ctx: dict[str, Any],
        output_data: dict[str, Any] | None = None,
        reasoning_content: str | None = None,
        model_name: str | None = None,
        token_usage: dict[str, Any] | None = None,
        cost_usd: float = 0.0,
        status: str = "ok",
        metadata: dict[str, Any] | None = None,
    ) -> None:

        duration_ms = (time.monotonic() - span_ctx["start_time"]) * 1000
        # Use the wall-clock time captured at span start so the DB timestamp reflects
        # when the operation began, not when it was recorded.
        timestamp = span_ctx.get("start_wall_time", datetime.now(timezone.utc)).isoformat()

        token_usage = token_usage or {}
        p_tokens = token_usage.get("prompt_tokens", 0)
        c_tokens = token_usage.get("completion_tokens", 0)
        r_tokens = token_usage.get("reasoning_tokens", 0)
        ch_tokens = token_usage.get("cache_hit_tokens", 0)

        # 1. SQLite Write
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_spans 
                (run_id, span_id, parent_span_id, timestamp, event_type, node_name, 
                 input_data, output_data, reasoning_content, model_name, 
                 prompt_tokens, completion_tokens, reasoning_tokens, cache_hit_tokens, 
                 cost_usd, duration_ms, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.run_id,
                    span_ctx["span_id"],
                    span_ctx["parent_span_id"],
                    timestamp,
                    span_ctx["event_type"],
                    span_ctx["node_name"],
                    json.dumps(span_ctx["input_data"]) if span_ctx["input_data"] else None,
                    json.dumps(output_data) if output_data else None,
                    reasoning_content,
                    model_name,
                    p_tokens,
                    c_tokens,
                    r_tokens,
                    ch_tokens,
                    cost_usd,
                    duration_ms,
                    status,
                    json.dumps(metadata) if metadata else None,
                ),
            )
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
                "reasoning_tokens": r_tokens,
            },
            "status": status,
            "metadata": metadata,
        }
        self._log_jsonl(record)

        # 3. Simple Text Log
        logger.info(
            f"[{span_ctx['event_type']}] {span_ctx['node_name']} completed in {duration_ms:.2f}ms with status {status}. Cost: ${cost_usd:.6f}"
        )

        # 4. OTel Complete
        if span_ctx.get("_otel_span"):
            otel_span = span_ctx["_otel_span"]
            if status != "ok":
                otel_span.set_status(Status(StatusCode.ERROR))
            otel_span.set_attribute("gabbe.output", json.dumps(_redact(output_data), default=str))
            otel_span.set_attribute("gabbe.cost_usd", cost_usd)
            otel_span.end()

    def snapshot_budget(self, step: int, budget: Any) -> None:
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO budget_snapshots
                (run_id, step, tokens_used, tool_calls_used, wall_time_sec, iterations)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    self.run_id,
                    step,
                    budget.tokens_used,
                    budget.tool_calls_used,
                    budget.snapshot()["wall_time_sec"],
                    budget.iterations,
                ),
            )
            self.db_conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to snapshot budget: {e}")

    def record_genai_usage(
        self,
        run_id: str,
        model: str | None,
        usage_dict: dict[str, Any] | None,
        system: str | None = None,
        operation: str | None = None,
        response_model: str | None = None,
        span: object | None = None,
        prompt: str | None = None,
        completion: str | None = None,
    ) -> dict[str, Any]:
        """Attach OTel GenAI semantic-convention attributes for an LLM call.

        Additive companion to ``end_span`` — does NOT alter existing span
        recording. Computes the canonical ``gen_ai.*`` attributes via
        ``genai_usage_attributes`` and, when an OTel span object is available
        (the ``span`` arg, or the ``_otel_span`` of a span context returned by
        ``start_span``), sets them on that span. Prompt/response *content* is
        only attached when ``should_capture_content()`` is True (privacy-first,
        off by default).

        Returns the flat attribute dict so callers (budget/llm) can also use it
        even when no live OTel backend is configured. ``run_id`` is accepted for
        symmetry with other tracer methods and span correlation.
        """
        attrs = genai_usage_attributes(
            model,
            usage_dict,
            system=system,
            operation=operation,
            response_model=response_model,
        )

        # Resolve a live OTel span: accept either a raw OTel span or a span
        # context dict (as produced by start_span) carrying "_otel_span".
        otel_span = None
        if isinstance(span, dict):
            otel_span = span.get("_otel_span")
        elif span is not None:
            otel_span = span

        capture = should_capture_content()
        if capture:
            if prompt is not None:
                attrs[GEN_AI_PROMPT] = _redact_text(prompt)
            if completion is not None:
                attrs[GEN_AI_COMPLETION] = _redact_text(completion)

        if otel_span is not None:
            try:
                otel_span.set_attribute("gabbe.run_id", run_id)
                for key, value in attrs.items():
                    if value is not None:
                        otel_span.set_attribute(key, value)
            except Exception as e:  # pragma: no cover - defensive, backend-specific
                logger.warning(f"Failed to set GenAI attributes on OTel span: {e}")

        return attrs

    def get_run_trace(self, run_id: str) -> list[dict[str, Any]]:
        """Return all audit spans for a run as a list of dicts, ordered by timestamp."""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                SELECT * FROM audit_spans WHERE run_id = ? ORDER BY id ASC
            """,
                (run_id,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to get run trace: {e}")
            return []

    def export_json(self, run_id: str) -> str:
        """Return the full run trace as a JSON string."""
        return json.dumps(self.get_run_trace(run_id), default=str, indent=2)
