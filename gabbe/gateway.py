# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, Set

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

logger = logging.getLogger("gabbe.gateway")


class ToolNotFound(Exception):
    pass


class PolicyDenied(Exception):
    pass


class CircuitOpen(Exception):
    pass


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    handler: Callable[..., Any]
    allowed_roles: Set[str]
    rate_limit_per_min: int = 60
    circuit_breaker_threshold: int = 3


class ToolGateway:
    def __init__(self) -> None:
        self.registry: Dict[str, ToolDefinition] = {}
        self._call_times: Dict[str, deque[float]] = {}
        self._failure_counts: Dict[str, int] = {}

    def register(self, tool_def: ToolDefinition) -> None:
        self.registry[tool_def.name] = tool_def
        self._call_times[tool_def.name] = deque()
        self._failure_counts[tool_def.name] = 0

    def _check_rate_limit(self, name: str) -> None:
        tool = self.registry[name]
        now = time.monotonic()
        q = self._call_times[name]

        # Remove timestamps older than 60s
        while q and now - q[0] > 60:
            q.popleft()

        if len(q) >= tool.rate_limit_per_min:
            raise RateLimitExceeded(f"Rate limit exceeded for tool {name}")

        q.append(now)

    def _check_circuit_breaker(self, name: str) -> None:
        tool = self.registry[name]
        if self._failure_counts[name] >= tool.circuit_breaker_threshold:
            raise CircuitOpen(f"Circuit open for tool {name} due to consecutive failures.")

    def execute(self, name: str, arguments: Dict[str, Any], role: str, run_context: Any) -> Any:
        span_ctx = run_context.tracer.start_span(
            "tool_call", name, {"arguments": arguments, "role": role}
        )

        try:
            if name not in self.registry:
                raise ToolNotFound(f"Tool {name} is not registered.")

            tool_def = self.registry[name]

            # Policy Check
            if run_context.policy:
                policy_res = run_context.policy.evaluate(
                    {"tool": name, "arguments": arguments, "role": role}
                )
                if not policy_res.allowed:
                    raise PolicyDenied(f"Policy denied: {policy_res.reason}")

            # Rate Limits & Circuit Breaker (gate BEFORE consuming budget)
            self._check_rate_limit(name)
            self._check_circuit_breaker(name)

            # Schema Validation
            if tool_def.parameters:
                if not HAS_JSONSCHEMA:
                    raise RuntimeError(
                        "jsonschema package is required for tool argument validation but is not installed."
                    )
                try:
                    jsonschema.validate(instance=arguments, schema=tool_def.parameters)
                except jsonschema.ValidationError as e:
                    raise ValueError(f"Argument validation failed: {e.message}")

            # Budget Check — consume only AFTER policy/rate-limit/circuit/validation
            # have passed, so rejected or malformed calls don't burn the run's
            # tool-call budget (which is the only enforced budget dimension today).
            if run_context.budget:
                run_context.budget.record_tool_call()

            # Execute — ONLY a failure of the handler itself trips the circuit
            # breaker. Client-side rejections (policy/validation/rate-limit/circuit)
            # above are not tool faults and must not wedge a healthy tool offline.
            try:
                result = tool_def.handler(**arguments)
            except Exception:
                if name in self._failure_counts:
                    self._failure_counts[name] += 1
                raise

            # Success => reset circuit breaker
            self._failure_counts[name] = 0

            run_context.tracer.end_span(span_ctx, output_data={"result": result}, status="ok")
            return result

        except Exception as e:
            # Trace + re-raise for the brain loop. The breaker counter is adjusted
            # only around the handler call above — never here — so gating rejections
            # don't count as tool failures.
            run_context.tracer.end_span(span_ctx, output_data={"error": str(e)}, status="error")
            raise


class RateLimitExceeded(Exception):
    pass
