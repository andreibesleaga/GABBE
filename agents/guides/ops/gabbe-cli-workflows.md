# GABBE CLI Workflows Reference (Optional)

> **For Agents**: This guide documents the optional `gabbe` CLI commands, platform controls, and recommended workflows. **The CLI is NOT required** — agents can fully operate via markdown inference without it.

## Integration Modes

The GABBE CLI can run in three modes, configured during `python3 scripts/init.py`:

| Mode | Who Uses It | How |
|---|---|---|
| **Disabled** (default) | Nobody | CLI not installed. Agents use markdown inference only. |
| **Manual** | Human only | Human runs `gabbe` commands directly when needed. Agents are NOT required to use them but may reference them. |
| **MCP Enforced** | Agent via MCP | All `gabbe` commands flow through `gabbe serve-mcp`. Agents MUST use the MCP JSON-RPC `tools/call` interface. Direct CLI calls are not used by agents. |

> [!NOTE]
> When **Disabled**, the GABBE CLI Workflows section is removed from `AGENTS.md` during project initialization. Agents will not see CLI commands and operate purely via the markdown-based skill/guide system.

---

## Quick Reference: All CLI Commands

| Command | Purpose | Requires API Key |
|---|---|---|
| `gabbe init` | Initialize DB (`project/state.db`) | No |
| `gabbe db --init` | Alias for `gabbe init` | No |
| `gabbe sync` | Bidirectional sync: `project/TASKS.md` ↔ SQLite | No |
| `gabbe status` | Project dashboard (phase, tasks, progress) | No |
| `gabbe verify` | Integrity checks (files, lint, tests, security) | No |
| `gabbe route "<prompt>"` | Route prompt to LOCAL or REMOTE LLM | No |
| `gabbe brain activate` | Active Inference Loop (observe → decide → act) | **Yes** |
| `gabbe brain evolve --skill <name>` | Evolutionary Prompt Optimization | **Yes** |
| `gabbe brain heal` | Self-Healing Watchdog | No |
| `gabbe forecast` | Strategic cost/token forecast | No |
| `gabbe serve-mcp` | Minimal-dependency MCP JSON-RPC server | No |
| `gabbe runs [--status S] [--limit N]` | List recent agent runs | No |
| `gabbe audit <run-id> [--format json]` | Structured audit trace for a run | No |
| `gabbe replay <run-id> [--from-step N]` | Deterministic replay from checkpoints | No |
| `gabbe resume <run-id>` | Resume a paused/escalated run | No |

### Global Flags
- `--version` — Print version and exit
- `--debug` — Enable DEBUG logging and full stack traces
- `--help` / `-h` — Help for any command

---

## Standard Workflows

### 1. Project Setup (First Time)

```bash
# Step 1: Generate context configs (interactive wizard)
python3 scripts/init.py

# Step 2: Initialize the database
gabbe init

# Step 3: Verify everything is set up
gabbe verify
```

**What happens**: Creates `project/state.db` with all required tables (`tasks`, `runs`, `audit_spans`, `checkpoints`, `pending_escalations`, `genes`, `forecast_snapshots`, `pricing_registry`, `budget_snapshots`).

---

### 2. Daily Development Workflow

```bash
# Check project status
gabbe status

# Sync tasks (after manual TASKS.md edits)
gabbe sync

# Run integrity checks
gabbe verify

# Route a prompt through the cost-effective router
gabbe route "Fix the typo in utils.py"
```

**Sync behaviour**:
- File newer → imports tasks from `project/TASKS.md` into DB
- DB newer → exports tasks from DB to `project/TASKS.md`
- Uses `<!-- GABBE:TASKS:START -->` / `<!-- GABBE:TASKS:END -->` markers

---

### 3. Brain Mode Workflow (Requires `GABBE_API_KEY`)

```bash
# Activate the Active Inference Loop
gabbe brain activate

# Optimize a skill's prompt via EPO
gabbe brain evolve --skill tdd-cycle

# Run self-healing checks (no API key needed)
gabbe brain heal
```

**Brain activate flow**: Observe tasks → Send state to LLM → Receive recommended action → Record run in `runs` table → Record audit spans.

---

### 4. Observability & Debugging Workflow

```bash
# See cost/token forecast
gabbe forecast

# List recent runs
gabbe runs
gabbe runs --status completed
gabbe runs --status error --limit 5

# Inspect a specific run
gabbe audit <run-id>
gabbe audit <run-id> --format json

# Replay a past run from checkpoints
gabbe replay <run-id>
gabbe replay <run-id> --from-step 3

# Resume a paused run
gabbe resume <run-id>
```

---

### 5. MCP Server Workflow

```bash
# Start the MCP JSON-RPC server (stdin/stdout)
gabbe serve-mcp
```

**Protocol**: JSON-RPC 2.0 over stdin/stdout. Methods: `initialize`, `tools/list`, `tools/call`.

**Security controls**:
- `GABBE_MCP_TOKEN` — If set, clients must send this in `initialize` params
- `GABBE_MCP_ALLOWED_COMMANDS` — Comma-separated allowlist (e.g., `pytest,ruff,bandit`)
- All commands run with `shell=False` (no injection)

---

## Platform Controls (Active During All Runs)

Every `gabbe brain activate` and `gabbe serve-mcp` session wraps execution in a `RunContext` with the following controls:

### Budget Enforcement
| Dimension | Env Var | Default |
|---|---|---|
| Tokens | `GABBE_MAX_TOKENS_PER_RUN` | 100,000 |
| Tool calls | `GABBE_MAX_TOOL_CALLS_PER_RUN` | 50 |
| Iterations | `GABBE_MAX_ITERATIONS` | 25 |
| Wall time | `GABBE_MAX_WALL_TIME` | 300s |
| Cost (USD) | `GABBE_MAX_COST_USD` | $5.00 |

### Hard Stops
Absolute guards that **cannot** be loosened at runtime. Raises `MaxIterationsExceeded`, `MaxDepthExceeded`, or `TimeoutExceeded`.

### Policy Engine (`project/policies.yml`)
```yaml
version: "1"
tools:
  allowed: ["call_llm", "run_command"]
  denied:  ["run_security_scan"]
roles:
  brain-mode: ["call_llm"]
  external_agent: ["run_command"]
content_safety:
  enabled: true
```
- **Deny-first**: First policy that denies wins
- **Secure default**: No policy file → deny-all

### Tool Gateway
All tool execution flows through `ToolGateway.execute()`:
1. Tool registration check → 2. Policy evaluation → 3. Budget check → 4. Rate limiting → 5. Circuit breaker → 6. Schema validation → 7. Handler execution → 8. Audit span

### Escalation Handler

| Mode | Env `GABBE_ESCALATION_MODE` | Behaviour |
|---|---|---|
| `cli` | Interactive prompt (approve/reject/edit) | Continues after response |
| `file` | Records to DB, raises `EscalationPaused` | Resume with `gabbe resume` |
| `silent` | Auto-rejects | Safe for CI/CD |

**Triggers**: `BUDGET_EXHAUSTED`, `REPEATED_TOOL_FAILURE`, `AMBIGUOUS_DECISION`, `POLICY_VIOLATION`, `MAX_ITERATIONS`

### Audit Trail
Every event recorded as spans in `audit_spans` table. Inspect with `gabbe audit <run-id>`.

### Checkpoints & Replay
State snapshots saved to `checkpoints` table. Replay with `gabbe replay <run-id>`.

---

## Environment Variables (Complete)

| Variable | Default | Purpose |
|---|---|---|
| `GABBE_API_URL` | `https://api.openai.com/v1/...` | LLM endpoint |
| `GABBE_API_KEY` | *(required for LLM)* | Bearer token |
| `GABBE_API_MODEL` | `gpt-4o` | Model name |
| `GABBE_LLM_TEMPERATURE` | `0.7` | Sampling temperature |
| `GABBE_LLM_TIMEOUT` | `30` | HTTP timeout (seconds) |
| `GABBE_LLM_MAX_RETRIES` | `3` | LLM retry attempts |
| `GABBE_ROUTE_THRESHOLD` | `50` | Complexity → LOCAL/REMOTE |
| `GABBE_LOG_LEVEL` | `INFO` | Logging level |
| `GABBE_MAX_COST_USD` | `5.0` | Cost budget per run |
| `GABBE_MAX_TOKENS_PER_RUN` | `100000` | Token limit per run |
| `GABBE_MAX_TOOL_CALLS_PER_RUN` | `50` | Tool calls per run |
| `GABBE_MAX_ITERATIONS` | `25` | Brain loop iterations |
| `GABBE_MAX_WALL_TIME` | `300` | Wall time (seconds) |
| `GABBE_MAX_RECURSION_DEPTH` | `5` | Recursion depth |
| `GABBE_POLICY_FILE` | `project/policies.yml` | Policy YAML path |
| `GABBE_ESCALATION_MODE` | `cli` | `cli` / `file` / `silent` |
| `GABBE_OTEL_ENABLED` | `false` | OpenTelemetry |
| `GABBE_SUBPROCESS_TIMEOUT` | `300` | Verify command timeout |
| `GABBE_MCP_TOKEN` | *(unset)* | MCP auth token |
| `GABBE_MCP_ALLOWED_COMMANDS` | *(unset)* | MCP command allowlist |

---

## Database Tables (Schema v3)

| Table | Purpose |
|---|---|
| `tasks` | Task tracking (title, status, timestamps) |
| `runs` | One row per agent execution |
| `audit_spans` | Per-step spans with token/cost data |
| `budget_snapshots` | Periodic budget state per run |
| `checkpoints` | State snapshots for replay |
| `pending_escalations` | Human-review queue |
| `genes` | EPO evolutionary prompt storage |
| `forecast_snapshots` | Cost/token projections |
| `pricing_registry` | Per-model token pricing |

---

## Agent Rules

1. **Always run `gabbe init` before any other command** in a new project.
2. **Run `gabbe sync` after editing `project/TASKS.md`** to keep DB in sync.
3. **Run `gabbe verify` before committing** to catch integrity issues.
4. **Use `gabbe route` before making LLM calls** to determine LOCAL vs REMOTE.
5. **Check `gabbe runs` and `gabbe audit`** after brain sessions for cost visibility.
6. **Respect budget limits** — all runs are bounded by token/cost/time limits.
7. **Handle escalations** — when `BUDGET_EXHAUSTED` or `POLICY_VIOLATION` occurs, the run pauses for human review.
8. **Use `gabbe forecast`** to project remaining work before starting large tasks.
