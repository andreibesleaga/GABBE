import sqlite3
import time
from dataclasses import dataclass, field
from .database import get_db
from .config import (
    GABBE_MAX_TOKENS_PER_RUN,
    GABBE_MAX_TOOL_CALLS_PER_RUN,
    GABBE_MAX_ITERATIONS,
    GABBE_MAX_WALL_TIME,
    GABBE_MAX_COST_USD,
)

class BudgetExceeded(Exception):
    def __init__(self, reason, snapshot):
        super().__init__(f"Budget Exceeded: {reason}")
        self.reason = reason
        self.snapshot = snapshot

@dataclass
class Budget:
    max_tokens: int = GABBE_MAX_TOKENS_PER_RUN
    max_tool_calls: int = GABBE_MAX_TOOL_CALLS_PER_RUN
    max_wall_seconds: int = GABBE_MAX_WALL_TIME
    max_iterations: int = GABBE_MAX_ITERATIONS
    max_cost_usd: float = GABBE_MAX_COST_USD

    # Current state
    tokens_used: int = 0
    tool_calls_used: int = 0
    iterations: int = 0
    cost_usd: float = 0.0
    _start_time: float = field(default_factory=time.monotonic)
    _cached_prices: dict = field(default_factory=dict)

    def __post_init__(self):
        self._load_prices()

    def _load_prices(self):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pricing_registry")
            rows = cursor.fetchall()
            for row in rows:
                self._cached_prices[row["model_id"]] = {
                    "input": row["input_token_price"],
                    "output": row["output_token_price"],
                    "reasoning": row["reasoning_token_price"],
                    "cache_creation": row["cache_creation_price"],
                    "cache_read": row["cache_read_price"],
                }
            conn.close()
        except sqlite3.Error:
            pass # Fallback to 0 if db fails

    def _get_price(self, model_id: str):
        # Default empty pricing
        return self._cached_prices.get(model_id, {
            "input": 0.0, "output": 0.0, "reasoning": 0.0, 
            "cache_creation": 0.0, "cache_read": 0.0
        })

    def check(self):
        wall_time = time.monotonic() - self._start_time
        if self.tokens_used > self.max_tokens:
            raise BudgetExceeded("Max tokens reached", self.snapshot())
        if self.tool_calls_used > self.max_tool_calls:
            raise BudgetExceeded("Max tool calls reached", self.snapshot())
        if self.iterations > self.max_iterations:
            raise BudgetExceeded("Max iterations reached", self.snapshot())
        if self.cost_usd > self.max_cost_usd:
            raise BudgetExceeded("Max cost (USD) reached", self.snapshot())
        if wall_time > self.max_wall_seconds:
            raise BudgetExceeded("Max wall time reached", self.snapshot())

    def record_llm_usage(self, model_id: str, usage_dict: dict):
        total_tokens = usage_dict.get("total_tokens", 0)
        prompt_tokens = usage_dict.get("prompt_tokens", 0)
        completion_tokens = usage_dict.get("completion_tokens", 0)
        # Reasoning tokens are included inside completion_tokens for o1/o3-class models.
        reasoning_tokens = usage_dict.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
        # Cache read tokens come from prompt_tokens_details.cached_tokens (OpenAI format).
        cache_read_tokens = usage_dict.get("prompt_tokens_details", {}).get("cached_tokens", 0)

        self.tokens_used += total_tokens

        prices = self._get_price(model_id)
        # If no dedicated reasoning price is configured, fall back to the output rate so
        # reasoning tokens are never silently billed at zero.
        reasoning_price = prices["reasoning"] if prices["reasoning"] > 0 else prices["output"]
        cost = (
            (prompt_tokens * prices["input"]) +
            ((completion_tokens - reasoning_tokens) * prices["output"]) +
            (reasoning_tokens * reasoning_price) +
            (cache_read_tokens * prices["cache_read"])
        )
        self.cost_usd += cost
        self.check()

    def record_tool_call(self):
        self.tool_calls_used += 1
        self.check()

    def record_iteration(self):
        self.iterations += 1
        self.check()

    def snapshot(self) -> dict:
        return {
            "tokens_used": self.tokens_used,
            "tool_calls_used": self.tool_calls_used,
            "cost_usd": self.cost_usd,
            "iterations": self.iterations,
            "wall_time_sec": time.monotonic() - self._start_time
        }

    def remaining(self) -> dict:
        wall_time = time.monotonic() - self._start_time
        return {
            "tokens": max(0, self.max_tokens - self.tokens_used),
            "tool_calls": max(0, self.max_tool_calls - self.tool_calls_used),
            "iterations": max(0, self.max_iterations - self.iterations),
            "wall_time_sec": max(0.0, self.max_wall_seconds - wall_time),
            "cost_usd": max(0.0, self.max_cost_usd - self.cost_usd),
        }

    @classmethod
    def from_config(cls):
        return cls()

    @classmethod
    def from_dict(cls, d: dict) -> "Budget":
        """Reconstruct a Budget from a snapshot dict (used for replay)."""
        b = cls(
            max_tokens=d.get("max_tokens", GABBE_MAX_TOKENS_PER_RUN),
            max_tool_calls=d.get("max_tool_calls", GABBE_MAX_TOOL_CALLS_PER_RUN),
            max_wall_seconds=d.get("max_wall_seconds", GABBE_MAX_WALL_TIME),
            max_iterations=d.get("max_iterations", GABBE_MAX_ITERATIONS),
            max_cost_usd=d.get("max_cost_usd", GABBE_MAX_COST_USD),
        )
        b.tokens_used = d.get("tokens_used", 0)
        b.tool_calls_used = d.get("tool_calls_used", 0)
        b.iterations = d.get("iterations", 0)
        b.cost_usd = d.get("cost_usd", 0.0)
        return b
