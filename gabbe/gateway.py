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


@dataclass
class ReadOnlyToolDefinition(ToolDefinition):
    """A tool that changes nothing and exposes only files of the project the server runs in.

    It is not subject to the operator's tool allow-list in project/policies.yml (which
    exists to gate tools that act); it is still role-checked, rate-limited,
    schema-validated and traced."""

    read_only: bool = True


# Seconds an open circuit stays closed to calls before one trial call is let
# through (half-open). A successful trial closes the circuit again.
_CIRCUIT_COOLDOWN_S = 30.0


class ToolGateway:
    def __init__(self) -> None:
        self.registry: Dict[str, ToolDefinition] = {}
        self._call_times: Dict[str, deque[float]] = {}
        self._failure_counts: Dict[str, int] = {}
        self._opened_at: Dict[str, float] = {}
        # Injectable clock (tests replace it) used for the circuit cool-down.
        self._clock: Callable[[], float] = time.monotonic

    def register(self, tool_def: ToolDefinition) -> None:
        self.registry[tool_def.name] = tool_def
        self._call_times[tool_def.name] = deque()
        self._failure_counts[tool_def.name] = 0
        self._opened_at.pop(tool_def.name, None)

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
        if self._failure_counts[name] < tool.circuit_breaker_threshold:
            return
        now = self._clock()
        if now - self._opened_at.get(name, now) < _CIRCUIT_COOLDOWN_S:
            raise CircuitOpen(f"Circuit open for tool {name} due to consecutive failures.")
        # Half-open: let this one trial call through. A failure re-opens the
        # circuit with a fresh cool-down; a success closes it (see execute).
        self._opened_at[name] = now

    @staticmethod
    def _check_policy(name: str, arguments: Dict[str, Any], role: str, run_context: Any) -> None:
        if run_context.policy is None:
            raise PolicyDenied("No policy engine configured; refusing tool call (fail-closed).")
        policy_res = run_context.policy.evaluate(
            {"tool": name, "arguments": arguments, "role": role}
        )
        if not policy_res.allowed:
            raise PolicyDenied(f"Policy denied: {policy_res.reason}")

    def execute(self, name: str, arguments: Dict[str, Any], role: str, run_context: Any) -> Any:
        span_ctx = run_context.tracer.start_span(
            "tool_call", name, {"arguments": arguments, "role": role}
        )

        try:
            if name not in self.registry:
                raise ToolNotFound(f"Tool {name} is not registered.")

            tool_def = self.registry[name]

            # Role check: when a tool lists allowed roles, the caller's role must
            # be one of them. An empty set means "no role restriction".
            if tool_def.allowed_roles and role not in tool_def.allowed_roles:
                raise PolicyDenied(f"Role '{role}' is not allowed to call tool {name}.")

            # Policy Check — fail-closed. A missing policy engine is a
            # misconfiguration, not a license to run every tool unchecked; deny
            # rather than silently skipping policy. RunContext always installs a
            # deny-all default (PolicyEngine.from_yaml), so this only triggers
            # when a caller explicitly passes policy=None.
            if not isinstance(tool_def, ReadOnlyToolDefinition):
                self._check_policy(name, arguments, role, run_context)

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
                    if self._failure_counts[name] >= tool_def.circuit_breaker_threshold:
                        self._opened_at[name] = self._clock()
                raise

            # Success => reset circuit breaker
            self._failure_counts[name] = 0
            self._opened_at.pop(name, None)

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
