# GABBE Platform Controls (Experimental)

This document describes the agent platform control layer for the experimental `gabbe` CLI. It covers budget enforcement, hard stops, policy rules, the tool gateway, audit tracing, human escalation, and deterministic replay.

---

## Overview

Every `gabbe brain activate` run (and `gabbe serve-mcp` session) is wrapped in a `RunContext` that brings together all platform controls:

```
RunContext
├── Budget         — token, cost, tool call, iteration, and wall-time limits
├── HardStop       — absolute iteration / depth / timeout guards
├── PolicyEngine   — YAML-driven tool access control (RBAC + allowlists)
├── ToolGateway    — single mediated execution point for all tools
├── AuditTracer    — structured spans to SQLite + JSONL + optional OTel
├── EscalationHandler — human-in-the-loop when limits are hit
└── CheckpointStore   — state snapshots enabling replay
```

All state persists to `project/state.db` (schema v3). Zero new required dependencies (PyYAML was already required; `jsonschema` is optional).

---

## Budget (`gabbe/budget.py`)

### What it tracks

| Dimension | Config var | Default |
|---|---|---|
| Total tokens | `GABBE_MAX_TOKENS_PER_RUN` | 100,000 |
| Tool calls | `GABBE_MAX_TOOL_CALLS_PER_RUN` | 50 |
| Iterations | `GABBE_MAX_ITERATIONS` | 25 |
| Wall time | `GABBE_MAX_WALL_TIME` | 300 s |
| Cost (USD) | `GABBE_MAX_COST_USD` | $5.00 |

### Cost calculation

Pricing is loaded from the `pricing_registry` SQLite table (keyed by `model_id`). Populate it with your model pricing:

```sql
INSERT OR REPLACE INTO pricing_registry (model_id, input_token_price, output_token_price)
VALUES ('gpt-4o', 0.0000025, 0.000010);
```

When pricing is absent for a model, cost stays at $0 (tokens are still counted).

### API

```python
from gabbe.budget import Budget, BudgetExceeded

b = Budget.from_config()        # reads env vars
b.record_tool_call()            # increments + checks
b.record_iteration()            # increments + checks
b.record_llm_usage("gpt-4o", usage_dict)  # tokens + cost
snap = b.snapshot()             # current state dict
rem  = b.remaining()            # remaining per dimension
b.check()                       # raise BudgetExceeded if any limit exceeded

# Replay reconstruction
b2 = Budget.from_dict({"max_tokens": 500, "tokens_used": 100})
```

---

## HardStop (`gabbe/hardstop.py`)

Absolute guards that cannot be loosened at runtime (unlike budgets which check `>`):

```python
from gabbe.hardstop import HardStop, MaxIterationsExceeded, MaxDepthExceeded, TimeoutExceeded

hs = HardStop(max_iterations=10, max_depth=5, timeout_sec=120)
hs.tick(depth=0)            # increments iteration, checks all limits
hs.remaining_steps()        # -> int
hs.should_wrap_up(threshold=2)  # -> bool (true when ≤ 2 steps left)
```

Config vars: `GABBE_MAX_ITERATIONS`, `GABBE_MAX_RECURSION_DEPTH`, `GABBE_MAX_WALL_TIME`.

When `should_wrap_up()` returns `True`, the brain system prompt is a good place to append "Please wrap up your current task."

---

## Policy Engine (`gabbe/policy.py`)

### Configuration (`project/policies.yml`)

```yaml
version: "1"

tools:
  allowed: ["call_llm", "run_command"]
  denied:  ["run_security_scan"]   # explicit deny overrides allowed

roles:
  brain-mode:   ["call_llm"]
  external_agent: ["run_command"]
  admin: ["*"]

# Enable PII detection to block credentials/emails from remote APIs
content_safety:
  enabled: true

# Numeric parameter bounds (optional)
parameter_bounds:
  temperature:
    min: 0.0
    max: 1.0
```

Set `GABBE_POLICY_FILE` to override the path (default: `project/policies.yml`).

> **Secure default:** If the policy file is absent, `PolicyEngine.from_yaml()` defaults to **deny-all** (`ToolAllowlistPolicy([], [])`). A warning is logged. Create `project/policies.yml` to configure tool access explicitly.

> **Note on `policies.yml` sections:** The parser reads `version`, `tools`, `roles`, `content_safety`, and `parameter_bounds`. The `budgets:` section is informational only (budget limits are enforced by `budget.py` via env vars). The `escalation:` section is currently not parsed — escalation triggers and modes are configured via env vars (`GABBE_ESCALATION_MODE`) and the `EscalationTrigger` enum in code.

### Built-in policies

| Class | Purpose |
|---|---|
| `ToolAllowlistPolicy` | Allow/deny by tool name or wildcard `*` |
| `RolePolicy` | Role → allowed tools mapping |
| `ContentSafetyPolicy` | Blocks PII (emails, credentials, SSNs) in inputs |
| `ParameterRangePolicy` | Validates numeric params against `min`/`max` bounds |

Evaluation is **deny-first**: the first policy that denies wins. Use `engine.evaluate_all()` to get all results for audit logging.

---

## Tool Gateway (`gabbe/gateway.py`)

All tool execution flows through `ToolGateway.execute()`, which enforces:

1. Tool registration check
2. Policy evaluation (deny-first chain)
3. Budget check (`record_tool_call()`)
4. Rate limiting (sliding 60s window, configurable per tool)
5. Circuit breaker (open after N consecutive failures)
6. JSON Schema validation (if `jsonschema` is installed)
7. Handler execution
8. Audit span recorded (start + end)

```python
from gabbe.gateway import ToolGateway, ToolDefinition

gw = ToolGateway()
gw.register(ToolDefinition(
    name="run_test",
    description="Run project tests",
    parameters={"type": "object", "properties": {"cmd": {"type": "string"}}},
    handler=my_handler,
    allowed_roles={"agent"},
    rate_limit_per_min=10,
    circuit_breaker_threshold=3,
))
result = gw.execute("run_test", {"cmd": "pytest"}, role="agent", run_context=ctx)
```

---

## Audit Tracer (`gabbe/audit.py`)

Every significant event (LLM call, tool call, policy check) is recorded as a span:

```python
from gabbe.audit import AuditTracer

tracer = AuditTracer(run_id="abc123", db_conn=conn)

span = tracer.start_span("llm_call", "brain_observe", {"prompt": "..."})
tracer.end_span(span, output_data={"response": "..."}, token_usage=usage, cost_usd=0.002, status="ok")

tracer.snapshot_budget(step=3, budget=budget)

trace = tracer.get_run_trace("abc123")  # list of span dicts
json_str = tracer.export_json("abc123") # full trace as JSON
```

**`@traced` decorator:** Wrap any function to auto-create a start/end span pair:

```python
from gabbe.audit import traced

@traced("tool_call", "my_tool", tracer=tracer)
def my_tool_handler(args):
    ...
```

**Storage destinations:**
- `project/state.db` → `audit_spans` table
- `project/logs/run_{run_id}.jsonl` → one JSON line per span
- OpenTelemetry → set `GABBE_OTEL_ENABLED=true` and configure OTel SDK (soft-fail: if OTel SDK is not installed, a warning is logged and spans fall back to SQLite/JSONL only)

**CLI inspection:**
```bash
gabbe audit <run-id>               # table view
gabbe audit <run-id> --format json # raw JSON
```

---

## Escalation Handler (`gabbe/escalation.py`)

Triggered automatically when the platform detects dangerous conditions:

| Trigger | When |
|---|---|
| `BUDGET_EXHAUSTED` | Any budget limit exceeded |
| `REPEATED_TOOL_FAILURE` | Circuit breaker opens |
| `AMBIGUOUS_DECISION` | Agent cannot determine next action |
| `POLICY_VIOLATION` | Policy engine denies an action |
| `MAX_ITERATIONS` | HardStop limit reached |

### Escalation modes

Set via `GABBE_ESCALATION_MODE` (default: `cli`):

| Mode | Behaviour |
|---|---|
| `cli` | Prompts the operator interactively (inline); execution **continues** after the operator responds (`approved`, `rejected`, or `edited`) |
| `file` | Records to `pending_escalations` table and raises `EscalationPaused`, **suspending execution** until `gabbe resume <run-id>` is called |
| `silent` | Auto-rejects (safe for CI/CD) |

The **CLI mode** interactive prompt offers three choices:
- **[a]pprove** — allow the action (status `approved`)
- **[r]eject** — deny the action (status `rejected`)
- **[e]dit context** — provide JSON overrides or notes; execution continues with `edited` status and the provided notes stored in `pending_escalations.response`

**Resuming a paused run:**
```bash
gabbe resume <run-id>
```

---

## Replay & Checkpoints (`gabbe/replay.py`)

Each run can save state snapshots (checkpoints) for deterministic replay:

```python
from gabbe.replay import CheckpointStore, ReplayRunner

store = CheckpointStore(db_conn=conn)
cp_id = store.save(run_id, step=1, node_name="observe", state_snapshot={"tasks": 5}, policy_version="v1")
store.load(cp_id)           # deserialize checkpoint
store.get_history(run_id)   # ordered list of checkpoints

runner = ReplayRunner(store)
steps = runner.replay(run_id, from_step=0)   # returns list of replayed step dicts
diff  = runner.diff(run_id_a, run_id_b)     # compare two run sequences

# Reconstruct a RunContext from a checkpoint.
# NOTE: creates a *new* run_id (fresh UUID) — the replay is tracked as a new run,
# not a restoration of the original run.
ctx = RunContext.from_checkpoint(cp_id)
```

**CLI replay:**
```bash
gabbe replay <run-id>
gabbe replay <run-id> --from-step 3
```

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `GABBE_MAX_TOKENS_PER_RUN` | `100000` | Token budget per run |
| `GABBE_MAX_TOOL_CALLS_PER_RUN` | `50` | Tool call budget per run |
| `GABBE_MAX_ITERATIONS` | `25` | Max brain loop iterations |
| `GABBE_MAX_WALL_TIME` | `300` | Max wall time in seconds |
| `GABBE_MAX_RECURSION_DEPTH` | `5` | Max agent recursion depth |
| `GABBE_MAX_RETRIES_PER_TOOL` | `3` | Max retries per tool call |
| `GABBE_MAX_COST_USD` | `5.0` | Max cost budget per run |
| `GABBE_POLICY_FILE` | `project/policies.yml` | Path to YAML policy file |
| `GABBE_ESCALATION_MODE` | `cli` | Escalation mode: `cli`, `file`, or `silent` |
| `GABBE_OTEL_ENABLED` | `false` | Enable OpenTelemetry tracing |
| `GABBE_SUBPROCESS_TIMEOUT` | `300` | Timeout for verify shell commands |
| `GABBE_MCP_TOKEN` | *(unset)* | If set, MCP clients must provide this token in `initialize` params. Leave unset to disable. |
| `GABBE_MCP_ALLOWED_COMMANDS` | *(unset)* | Comma-separated executables permitted via `run_command` over MCP. When unset, all commands are blocked. |

---

## Database Tables (v3)

| Table | Purpose |
|---|---|
| `runs` | One row per agent execution (status, costs, initiator) |
| `audit_spans` | Per-step spans with token usage, cost, CoT content |
| `budget_snapshots` | Periodic budget state snapshots per run |
| `checkpoints` | State snapshots for deterministic replay |
| `pending_escalations` | Human-review queue |
| `forecast_snapshots` | Cost/token projections from `gabbe forecast` |
| `pricing_registry` | Dynamic per-model token pricing |

---

## Quickstart: Running with Tight Limits

```bash
# Hard stop after 3 iterations
GABBE_MAX_ITERATIONS=3 gabbe brain activate

# Budget cap at 1,000 tokens
GABBE_MAX_TOKENS_PER_RUN=1000 gabbe brain activate

# Silent mode for CI (no interactive prompts)
GABBE_ESCALATION_MODE=silent gabbe brain activate

# Inspect what happened
gabbe runs
gabbe audit <run-id>
```
