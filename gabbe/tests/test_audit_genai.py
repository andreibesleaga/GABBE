# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the OpenTelemetry GenAI semantic-convention additions in
gabbe.audit (book idea 9). Hermetic: no network, no real OTel backend."""

import gabbe.audit as audit
from gabbe.audit import (
    GEN_AI_ATTRIBUTES,
    GEN_AI_OPERATION_NAME,
    GEN_AI_REQUEST_MODEL,
    GEN_AI_RESPONSE_MODEL,
    GEN_AI_SYSTEM,
    GEN_AI_USAGE_CACHED_INPUT_TOKENS,
    GEN_AI_USAGE_INPUT_TOKENS,
    GEN_AI_USAGE_OUTPUT_TOKENS,
    GEN_AI_USAGE_REASONING_TOKENS,
    GEN_AI_USAGE_TOTAL_TOKENS,
    genai_usage_attributes,
    should_capture_content,
)


def test_genai_attribute_constants_have_canonical_names():
    assert GEN_AI_SYSTEM == "gen_ai.system"
    assert GEN_AI_OPERATION_NAME == "gen_ai.operation.name"
    assert GEN_AI_REQUEST_MODEL == "gen_ai.request.model"
    assert GEN_AI_RESPONSE_MODEL == "gen_ai.response.model"
    assert GEN_AI_USAGE_INPUT_TOKENS == "gen_ai.usage.input_tokens"
    assert GEN_AI_USAGE_OUTPUT_TOKENS == "gen_ai.usage.output_tokens"
    assert GEN_AI_USAGE_TOTAL_TOKENS == "gen_ai.usage.total_tokens"
    assert GEN_AI_USAGE_REASONING_TOKENS == "gen_ai.usage.reasoning_tokens"
    assert GEN_AI_USAGE_CACHED_INPUT_TOKENS == "gen_ai.usage.cached_input_tokens"


def test_genai_attributes_registry_is_consistent():
    # Every registry value is a canonical gen_ai.* name and exposed as a constant.
    assert all(v.startswith("gen_ai.") for v in GEN_AI_ATTRIBUTES.values())
    assert GEN_AI_ATTRIBUTES["input_tokens"] == GEN_AI_USAGE_INPUT_TOKENS
    assert GEN_AI_ATTRIBUTES["output_tokens"] == GEN_AI_USAGE_OUTPUT_TOKENS
    assert GEN_AI_ATTRIBUTES["reasoning_tokens"] == GEN_AI_USAGE_REASONING_TOKENS
    assert GEN_AI_ATTRIBUTES["cached_input_tokens"] == GEN_AI_USAGE_CACHED_INPUT_TOKENS


def test_genai_usage_attributes_openai_shape():
    usage = {
        "total_tokens": 175,
        "prompt_tokens": 100,
        "completion_tokens": 75,
        "completion_tokens_details": {"reasoning_tokens": 25},
        "prompt_tokens_details": {"cached_tokens": 40},
    }
    attrs = genai_usage_attributes("gpt-4o", usage, system="openai", operation="chat")
    assert attrs[GEN_AI_SYSTEM] == "openai"
    assert attrs[GEN_AI_OPERATION_NAME] == "chat"
    assert attrs[GEN_AI_REQUEST_MODEL] == "gpt-4o"
    assert attrs[GEN_AI_USAGE_INPUT_TOKENS] == 100
    assert attrs[GEN_AI_USAGE_OUTPUT_TOKENS] == 75
    assert attrs[GEN_AI_USAGE_TOTAL_TOKENS] == 175
    assert attrs[GEN_AI_USAGE_REASONING_TOKENS] == 25
    assert attrs[GEN_AI_USAGE_CACHED_INPUT_TOKENS] == 40


def test_genai_usage_attributes_anthropic_cache_field():
    # Anthropic-style endpoints report cache reads in cache_read_input_tokens.
    usage = {
        "total_tokens": 60,
        "prompt_tokens": 50,
        "completion_tokens": 10,
        "cache_read_input_tokens": 30,
    }
    attrs = genai_usage_attributes("claude-3-5-sonnet", usage)
    assert attrs[GEN_AI_USAGE_CACHED_INPUT_TOKENS] == 30
    assert attrs[GEN_AI_USAGE_REASONING_TOKENS] == 0
    # Default system applied when none provided.
    assert attrs[GEN_AI_SYSTEM] == audit.GEN_AI_DEFAULT_SYSTEM


def test_genai_usage_attributes_empty_and_optional_fields():
    attrs = genai_usage_attributes(None, None)
    # No model -> no request-model key; zero token counts everywhere.
    assert GEN_AI_REQUEST_MODEL not in attrs
    assert GEN_AI_OPERATION_NAME not in attrs
    assert GEN_AI_RESPONSE_MODEL not in attrs
    assert attrs[GEN_AI_USAGE_INPUT_TOKENS] == 0
    assert attrs[GEN_AI_USAGE_OUTPUT_TOKENS] == 0
    assert attrs[GEN_AI_USAGE_REASONING_TOKENS] == 0
    assert attrs[GEN_AI_USAGE_CACHED_INPUT_TOKENS] == 0


def test_response_model_attribute_emitted_when_provided():
    attrs = genai_usage_attributes(
        "gpt-4o", {"prompt_tokens": 1}, response_model="gpt-4o-2024-08-06"
    )
    assert attrs[GEN_AI_RESPONSE_MODEL] == "gpt-4o-2024-08-06"


def test_should_capture_content_default_off(monkeypatch):
    monkeypatch.delenv("GABBE_OTEL_CAPTURE_CONTENT", raising=False)
    assert should_capture_content() is False


def test_should_capture_content_flips_with_env(monkeypatch):
    for truthy in ("1", "true", "TRUE", "yes", "Yes"):
        monkeypatch.setenv("GABBE_OTEL_CAPTURE_CONTENT", truthy)
        assert should_capture_content() is True
    for falsy in ("0", "false", "no", "", "off"):
        monkeypatch.setenv("GABBE_OTEL_CAPTURE_CONTENT", falsy)
        assert should_capture_content() is False


class _FakeSpan:
    """Minimal stand-in for an OTel span: records set_attribute calls."""

    def __init__(self):
        self.attributes = {}

    def set_attribute(self, key, value):
        self.attributes[key] = value


def test_record_genai_usage_sets_attributes_on_span(tmp_project, db_conn):
    tracer = audit.AuditTracer("run-genai-1", db_conn=db_conn)
    span = _FakeSpan()
    usage = {
        "total_tokens": 30,
        "prompt_tokens": 20,
        "completion_tokens": 10,
        "completion_tokens_details": {"reasoning_tokens": 4},
    }
    attrs = tracer.record_genai_usage(
        "run-genai-1", "gpt-4o", usage, system="openai", operation="chat", span=span
    )
    # Returned dict and the span attributes agree on the token counts.
    assert attrs[GEN_AI_USAGE_INPUT_TOKENS] == 20
    assert span.attributes[GEN_AI_USAGE_INPUT_TOKENS] == 20
    assert span.attributes[GEN_AI_USAGE_OUTPUT_TOKENS] == 10
    assert span.attributes[GEN_AI_USAGE_REASONING_TOKENS] == 4
    assert span.attributes[GEN_AI_SYSTEM] == "openai"
    assert span.attributes["gabbe.run_id"] == "run-genai-1"


def test_record_genai_usage_redacts_content_when_capture_on(tmp_project, db_conn, monkeypatch):
    monkeypatch.setenv("GABBE_OTEL_CAPTURE_CONTENT", "true")
    tracer = audit.AuditTracer("run-genai-2", db_conn=db_conn)
    span = _FakeSpan()
    tracer.record_genai_usage(
        "run-genai-2",
        "gpt-4o",
        {"prompt_tokens": 5, "completion_tokens": 5},
        span=span,
        prompt="contact me at user@example.com",
        completion="ok",
    )
    assert audit.GEN_AI_PROMPT in span.attributes
    # Captured content is still PII-redacted.
    assert "user@example.com" not in span.attributes[audit.GEN_AI_PROMPT]
    assert "[REDACTED]" in span.attributes[audit.GEN_AI_PROMPT]
    assert span.attributes[audit.GEN_AI_COMPLETION] == "ok"


def test_record_genai_usage_omits_content_by_default(tmp_project, db_conn, monkeypatch):
    monkeypatch.delenv("GABBE_OTEL_CAPTURE_CONTENT", raising=False)
    tracer = audit.AuditTracer("run-genai-3", db_conn=db_conn)
    span = _FakeSpan()
    tracer.record_genai_usage(
        "run-genai-3",
        "gpt-4o",
        {"prompt_tokens": 5},
        span=span,
        prompt="secret prompt text",
        completion="secret completion",
    )
    assert audit.GEN_AI_PROMPT not in span.attributes
    assert audit.GEN_AI_COMPLETION not in span.attributes


def test_record_genai_usage_accepts_span_context_dict(tmp_project, db_conn):
    tracer = audit.AuditTracer("run-genai-4", db_conn=db_conn)
    fake = _FakeSpan()
    span_ctx = {"_otel_span": fake, "span_id": "abc"}
    tracer.record_genai_usage("run-genai-4", "gpt-4o", {"prompt_tokens": 7}, span=span_ctx)
    assert fake.attributes[GEN_AI_USAGE_INPUT_TOKENS] == 7


def test_record_genai_usage_no_span_returns_attrs(tmp_project, db_conn):
    tracer = audit.AuditTracer("run-genai-5", db_conn=db_conn)
    attrs = tracer.record_genai_usage("run-genai-5", "gpt-4o", {"prompt_tokens": 3})
    # No live span: still returns the attribute dict (usable offline).
    assert attrs[GEN_AI_USAGE_INPUT_TOKENS] == 3
