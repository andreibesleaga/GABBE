# SPDX-License-Identifier: Apache-2.0
import time
import logging
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, Any

try:
    import jsonschema  # type: ignore
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
    parameters: dict  # JSON Schema
    handler: Callable
    allowed_roles: set
    rate_limit_per_min: int = 60
    circuit_breaker_threshold: int = 3

class ToolGateway:
    def __init__(self):
        self.registry: Dict[str, ToolDefinition] = {}
        self._call_times: Dict[str, deque] = {}
        self._failure_counts: Dict[str, int] = {}

    def register(self, tool_def: ToolDefinition):
        self.registry[tool_def.name] = tool_def
        self._call_times[tool_def.name] = deque()
        self._failure_counts[tool_def.name] = 0

    def _check_rate_limit(self, name: str):
        tool = self.registry[name]
        now = time.monotonic()
        q = self._call_times[name]
        
        # Remove timestamps older than 60s
        while q and now - q[0] > 60:
            q.popleft()
            
        if len(q) >= tool.rate_limit_per_min:
            raise RateLimitExceeded(f"Rate limit exceeded for tool {name}")
            
        q.append(now)

    def _check_circuit_breaker(self, name: str):
        tool = self.registry[name]
        if self._failure_counts[name] >= tool.circuit_breaker_threshold:
            raise CircuitOpen(f"Circuit open for tool {name} due to consecutive failures.")

    def execute(self, name: str, arguments: dict, role: str, run_context) -> Any:
        span_ctx = run_context.tracer.start_span("tool_call", name, {"arguments": arguments, "role": role})

        try:
            if name not in self.registry:
                raise ToolNotFound(f"Tool {name} is not registered.")
                
            tool_def = self.registry[name]
            
            # Policy Check
            if run_context.policy:
                policy_res = run_context.policy.evaluate({"tool": name, "arguments": arguments, "role": role})
                if not policy_res.allowed:
                    raise PolicyDenied(f"Policy denied: {policy_res.reason}")

            # Budget Check
            if run_context.budget:
                run_context.budget.record_tool_call()

            # Rate Limits & Circuit Breaker
            self._check_rate_limit(name)
            self._check_circuit_breaker(name)

            # Schema Validation
            if HAS_JSONSCHEMA and tool_def.parameters:
                try:
                    jsonschema.validate(instance=arguments, schema=tool_def.parameters)
                except jsonschema.ValidationError as e:
                    raise ValueError(f"Argument validation failed: {e.message}")

            # Execute
            result = tool_def.handler(**arguments)
            
            # Success => reset circuit breaker
            self._failure_counts[name] = 0
            
            run_context.tracer.end_span(span_ctx, output_data={"result": result}, status="ok")
            return result

        except Exception as e:
            if name in self._failure_counts:
                self._failure_counts[name] += 1
            
            # Re-raise standard workflow exceptions to be caught by brain loop
            run_context.tracer.end_span(span_ctx, output_data={"error": str(e)}, status="error")
            raise

class RateLimitExceeded(Exception):
    pass
