# GABBE CLI Reference (experimental)

> **Audience:** operators of the `gabbe` CLI. **Scope:** every command, flag, and environment variable.

## Installation

```bash
pip install -e ".[dev]"   # development / editable
pip install .             # production
```

Entry point: `gabbe` (defined in `pyproject.toml → [project.scripts]`)

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GABBE_API_URL` | `https://api.openai.com/v1/chat/completions` | OpenAI-compatible endpoint. Read from a project `.env` only when `GABBE_API_KEY` is not set in your shell (see `SECURITY.md`) |
| `GABBE_API_KEY` | *(required for LLM features)* | Bearer token for the LLM API |
| `GABBE_API_MODEL` | `gpt-4o` | Model name sent in API requests |
| `GABBE_LLM_TEMPERATURE` | `0.7` | Sampling temperature (0.0–1.0) |
| `GABBE_LLM_TIMEOUT` | `30` | HTTP timeout for LLM calls (seconds) |
| `GABBE_ROUTE_THRESHOLD` | `50` | Complexity score above which a prompt routes REMOTE |
| `GABBE_LLM_MAX_RETRIES`| `3` | (Internal) Number of retry attempts for LLM calls |
| `GABBE_LLM_CACHE` | `false` | Opt-in: cache identical LLM calls locally (0 tokens on a hit; only for deterministic calls) |
| `GABBE_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `GABBE_MAX_COST_USD` | `5.0` | Maximum cost (USD) budget per run |
| `GABBE_MAX_TOKENS_PER_RUN` | `100000` | Maximum token limit per run |
| `GABBE_MAX_TOOL_CALLS_PER_RUN` | `50` | Maximum tool calls per run |
| `GABBE_MAX_ITERATIONS` | `25` | Maximum brain loop iterations per run |
| `GABBE_MAX_WALL_TIME` | `300` | Maximum wall-clock time per run (seconds) |
| `GABBE_MAX_RECURSION_DEPTH` | `5` | Maximum agent recursion depth |
| `GABBE_MAX_RETRIES_PER_TOOL` | `3` | Maximum retries per tool call |
| `GABBE_SUBPROCESS_TIMEOUT` | `300` | Timeout for verify shell commands (seconds) |
| `GABBE_AUTONOMY` | `hybrid` | Autonomy mode: `ask`, `auto`, or `hybrid` (env > project config > default; invalid values warn and fall back to `hybrid`) |
| `GABBE_POLICY_FILE` | `project/policies.yml` | Path to YAML policy file for tool access control |
| `GABBE_ESCALATION_MODE` | `cli` | Escalation mode: `cli` (interactive), `file` (pause), `silent` (auto-reject) |
| `GABBE_OTEL_ENABLED` | `false` | Enable OpenTelemetry tracing |
| `GABBE_OTEL_CAPTURE_CONTENT` | `false` | Opt-in: capture prompt/response content on GenAI spans (off by default — content may contain PII/secrets) |
| `GABBE_MCP_ENABLE_RUN_COMMAND` | *(unset)* | Set to `1`/`true` to offer the `run_command` tool (same as `gabbe serve-mcp --enable-run-command`). Off by default since 1.2.0. |
| `GABBE_MCP_TOKEN` | *(unset)* | Needed only for `run_command`. Legacy clients send it in `initialize` params; modern clients send it in each request's `_meta` under `io.github.andreibesleaga.gabbe/token` (constant-time compared). While it is unset (and `GABBE_MCP_INSECURE` is off) `run_command` refuses every call. The read-only tools need no token. |
| `GABBE_MCP_ALLOWED_COMMANDS` | *(unset)* | Comma-separated allow-list for `run_command`. An entry is a bare command name (matches that name and the one path your `PATH` resolves it to) or an absolute path (matches only that path); `./git` never matches. A directory entry is **not** a wildcard. When unset, all commands are blocked. Example: `pytest,ruff,/usr/bin/git` |
| `GABBE_MCP_PASS_ENV` | *(unset)* | Comma-separated names of extra environment variables passed to `run_command` children. The child gets only `PATH`, `HOME`, `LANG`, `LC_ALL`, `TERM` and these, so `GABBE_API_KEY` and other secrets do not reach it. |
| `GABBE_MCP_INSECURE` | *(unset)* | Set to `1`/`true` for permissive `run_command` (no token, all commands allowed). It does not turn `run_command` on by itself. Trusted, isolated hosts only. |
| `GABBE_MCP_COMMAND_TIMEOUT` | `300` | Timeout (seconds) for a command executed via the MCP `run_command` tool |

---

## Global Flags

| Flag | Description |
|---|---|
| `--help` / `-h` | Show help for the command or sub-command and exit |
| `--version` | Print the installed version (`gabbe x.y.z`) and exit |
| `--debug` | Enable DEBUG-level logging and full stack traces |

---

## Commands

### `gabbe init`

Initialize (or migrate) the SQLite database in `project/state.db`.

```bash
gabbe init
```

**Exit codes:**
- `0` — success
- `1` — configuration or filesystem error

---

### `gabbe db --init`

Alias for `gabbe init`.

```bash
gabbe db --init
```

---

### `gabbe sync`

Bidirectional sync between `project/TASKS.md` and the SQLite `tasks` table.

**Logic:**
1. **Marker-Based Sync**: Looks for `<!-- GABBE:TASKS:START -->` and `<!-- GABBE:TASKS:END -->`.
    - If found, ONLY updates the content between these markers.
    - Preserves all other content (notes, headers) in `project/TASKS.md`.
2. **Legacy Fallback**: If no markers are found, it behaves as a full-file overwrite (or wraps content in markers on first export).
3. **Conflict Resolution**:
    - Both sides are merged (since 1.2.0): a task found on only one side is added to the other.
    - For a task on both sides the newer side's status wins; a tie goes to the file. The file is written atomically, between the markers.
    - A deletion is not propagated: a task removed from only one side comes back at the next sync, so delete it from both before syncing.

```bash
gabbe sync
```

---

### `gabbe status`

Display the project dashboard: phase, task counts, progress bar.

The phase is read from `project_state` (key `current_phase`).
Set it with:

```bash
sqlite3 project/state.db "INSERT OR REPLACE INTO project_state (key, value) VALUES ('current_phase', 'S03_ARCH');"
```

---

### `gabbe verify [--chaos] [--allow-empty]`

Run project integrity checks:

1. Check required files exist (`agents/AGENTS.md`, `agents/CONSTITUTION.md`, `project/TASKS.md`)
2. Warn if `project/state.db` is missing
3. Read `## Commands` section of `agents/AGENTS.md` and run `test`, `lint`, `security_scan` commands

`--chaos` instead runs fault-injection self-checks (Track B): it injects faults and
asserts GABBE's resilience mechanisms recover safely — the MCP tool stays
fail-closed without an allowlist, the hard-stop caps a runaway loop, PII forces
LOCAL routing, and escalation degrades gracefully under an injected DB fault.
Read-only; exits non-zero if any self-check fails.

**Exit codes:** `0` everything that was checked passed; `1` a check failed (including a missing
`project/TASKS.md`, which `gabbe init` creates); `3` nothing was verified because `agents/AGENTS.md`
has no `test` command (set one under `## Commands`). `--allow-empty` turns that case into exit `0`.

**`AGENTS.md` Commands section format:**
```markdown
## Commands
test: pytest gabbe/tests/ scripts/tests/ -v
lint: ruff check .
security_scan: bandit -r gabbe/
```

Only lines inside `## Commands` (until the next `##` heading) are parsed.

**Parsing rules:**
- Section header matching is **case-insensitive** (`## Commands` and `## commands` both work)
- Supported command keys: `test`, `lint`, `security_scan`, `build`
- Values are stripped of surrounding single/double quotes
- Commands are executed with `shell=False` (no shell expansion)

---

### `gabbe route <prompt>`

Route a prompt to LOCAL or REMOTE LLM based on complexity and PII detection.

```bash
gabbe route "Fix the typo in utils.py"
gabbe route "Architect a new distributed caching layer"
```

**PII detection:** Email addresses, US phone numbers, SSNs, credit card numbers,
and patterns like `password: ...` or `api_key=...` force LOCAL routing.

**Output:** `LOCAL` or `REMOTE`

---

### `gabbe brain activate`

Run one cycle of the Active Inference Loop:
1. Observe task statistics from DB
2. Send state description to LLM
3. Print recommended next action

Requires `GABBE_API_KEY`: without it the command says so and exits `1`, before any policy
or escalation message. Exits `1` on an API error or when platform controls stop the run.
With escalation mode `cli` and no terminal on standard input (CI, an agent), the escalation
is auto-rejected as in `silent` mode instead of asking.

---

### `gabbe brain evolve --skill <name>`

Evolutionary Prompt Optimization for a skill:
1. Fetch current best gene from `genes` table
2. Ask LLM to mutate/improve the prompt
3. Store new generation in `genes` table

```bash
gabbe brain evolve --skill code-review
```

Requires `GABBE_API_KEY`.

---

### `gabbe brain heal`

Run the Self-Healing Watchdog:
1. Verify DB connectivity
2. Check required project files exist
3. Print health report

Does **not** require `GABBE_API_KEY`. Exits `1` when it reports health issues.

---

### `gabbe forecast`

Run a strategic forecast evaluating remaining tasks and projecting future costs and token usage based on historical run data. Captures a snapshot to `forecast_snapshots`. Exits `1` on a database or unexpected error.

---

### `gabbe serve-mcp [--enable-run-command]`

Starts a minimal-dependency JSON-RPC Model Context Protocol (MCP) server on `stdin`/`stdout`. It serves the project it is started in (the folder with `project/`, found upwards from the current directory).

**On by default (read-only, no token, no allow-list):** `list_skills` (optional `category`), `read_skill` (`name`), `search_skills` (`query`, optional `limit`), `get_template` (`name`) and `project_status`. They read only inside `<project root>/agents` and `<project root>/project` (links that point elsewhere are refused), return at most 64 KiB of text (longer text is cut, with a note) and are listed with `readOnlyHint: true`. A folder without the kit gives a normal tool result with `isError: true` that says where the kit was looked for.

**Off by default:** `run_command`. Turn it on with `--enable-run-command` or `GABBE_MCP_ENABLE_RUN_COMMAND=1`; it then stays fail-closed (token, command allow-list; see the `GABBE_MCP_*` variables above) and its child process gets a minimal environment. The project's policy file must also allow it (`project/policies.yml` with `tools: {allowed: ["run_command"]}`; the installers do not create that file); without it every call is answered `Policy denied`. If you set a token, an allow-list or `GABBE_MCP_INSECURE` without enabling it, the server logs one start-up warning that says how to enable it.

**Two protocol generations on the same process:**

- Legacy (`2025-11-25`, `2025-06-18`, `2025-03-26`, `2024-11-05`): `initialize` first; the version is negotiated there; the token (only for `run_command`) goes in `params.token`.
- Modern (`2026-07-28`): no handshake. Every request carries `params._meta` with `io.modelcontextprotocol/protocolVersion` and `io.modelcontextprotocol/clientCapabilities` and is served on its own. `server/discover` returns the supported versions (modern first, then legacy), the capabilities and the server identity. An unsupported version is answered with error `-32022`, `Unsupported protocol version`, `data: {supported, requested}`; a request without the two `_meta` fields gets `-32602`. The token (only for `run_command`) goes in the same `_meta` under `io.github.andreibesleaga.gabbe/token`; a legacy login does not authorise modern requests.

A command that fails is returned with `isError: true`; an unknown tool or invalid arguments answer `-32602`; `ping` is answered. Calls go through the `ToolGateway` (role, rate limit, circuit breaker, audit trace). If the folder has no `project/` or the database cannot be opened, the server still serves the read-only tools (without an audit trail) and refuses `run_command` with a message; a database that was never initialised is set up at start. See [`SECURITY.md`](../SECURITY.md).

---

## Platform Control Layer

The experimental `gabbe` CLI supports a **platform control layer**. It covers budget enforcement, cost and token controls, hard stops, policy rules, the tool gateway, audit tracing, human escalation, and deterministic replay. Detailed documentation is available in [`PLATFORM_CONTROLS.md`](PLATFORM_CONTROLS.md).

---

## Database Schema

Located at `project/state.db` (SQLite 3).

### `schema_version`
| Column | Type | Description |
|---|---|---|
| `version` | INTEGER | Current schema version (incremented on migrations) |

### `tasks`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `title` | TEXT NOT NULL UNIQUE | Task description (unique — used as upsert key) |
| `status` | TEXT | `TODO`, `IN_PROGRESS`, or `DONE` |
| `tags` | TEXT | Optional comma-separated tags |
| `created_at` | DATETIME | Creation timestamp (UTC) |
| `updated_at` | DATETIME | Last modification timestamp (UTC) |

### `project_state`
| Column | Type | Description |
|---|---|---|
| `key` | TEXT PK | State key (e.g., `current_phase`) |
| `value` | TEXT | State value |
| `updated_at` | DATETIME | Last modification timestamp |

### `events`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `timestamp` | DATETIME | Event time |
| `actor` | TEXT | Who generated the event |
| `action` | TEXT | Action type |
| `message` | TEXT | Human-readable description |
| `context_summary` | TEXT | Optional context snapshot |

### `genes`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `skill_name` | TEXT | Skill this gene belongs to |
| `prompt_content` | TEXT | Prompt text |
| `success_rate` | REAL | Score 0.0–1.0 (updated externally) |
| `generation` | INTEGER | Evolution generation counter |
| `created_at` | DATETIME | Creation timestamp |

### `pricing_registry` (v3)
| Column | Type | Description |
|---|---|---|
| `model_id` | TEXT PK | LLM Model Identifier (e.g. gpt-4o) |
| `input_token_price` | REAL | Cost per input token |
| `output_token_price` | REAL | Cost per output token |
| `reasoning_token_price` | REAL | Cost per reasoning token |
| `cache_creation_price` | REAL | Cost per cache token |
| `cache_read_price` | REAL | Cost per cache read token |
| `updated_at` | DATETIME | Last modification timestamp |

### `runs` (v3 updates)
| Column | Type | Description |
|---|---|---|
| `id` | TEXT PK | Run ID (UUID) |
| `command` | TEXT | CLI command executed |
| `started_at` | DATETIME | Run start timestamp |
| `ended_at` | DATETIME | Run end timestamp (NULL while running) |
| `status` | TEXT | `running`, `completed`, `error`, `budget_exceeded`, `escalated` |
| `stop_reason` | TEXT | Human-readable reason if run was stopped early |
| `initiator` | TEXT | Initiator type: `cli`, `mcp`, or `replay` |
| `agent_persona` | TEXT | Active agent persona name (if set) |
| `total_tokens_used` | INTEGER | Aggregated token count |
| `total_cost_usd` | REAL | Aggregated cost in USD |
| `config_snapshot` | TEXT | JSON snapshot of config at run start |

### `audit_spans` (v3)
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Span auto-increment ID |
| `run_id` | TEXT | FK to `runs.id` |
| `span_id` | TEXT | Unique span identifier |
| `parent_span_id` | TEXT | Parent span for nested traces |
| `timestamp` | DATETIME | Span start time |
| `event_type` | TEXT | e.g. `tool_call`, `llm_call` |
| `node_name` | TEXT | Logical node / tool name |
| `input_data` | TEXT | JSON-serialised input |
| `output_data` | TEXT | JSON-serialised output |
| `reasoning_content` | TEXT | Chain-of-Thought content |
| `model_name` | TEXT | Model used for LLM spans |
| `prompt_tokens` | INTEGER | Input token count |
| `completion_tokens` | INTEGER | Output token count |
| `reasoning_tokens` | INTEGER | Reasoning token count (o-series) |
| `cache_hit_tokens` | INTEGER | Cached prompt tokens |
| `cost_usd` | REAL | Cost of this span in USD |
| `duration_ms` | REAL | Wall-clock execution time (ms) |
| `status` | TEXT | `ok` or `error` |
| `metadata` | TEXT | JSON extra fields |

### `budget_snapshots` (v3)
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `run_id` | TEXT | FK to `runs.id` |
| `step` | INTEGER | Brain loop step number |
| `tokens_used` | INTEGER | Tokens used at this snapshot |
| `tool_calls_used` | INTEGER | Tool calls used at this snapshot |
| `wall_time_sec` | REAL | Wall time elapsed (seconds) |
| `iterations` | INTEGER | Iterations completed at this snapshot |
| `timestamp` | DATETIME | Snapshot timestamp |

### `checkpoints` (v3)
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `run_id` | TEXT | FK to `runs.id` |
| `step` | INTEGER | Step number when checkpoint was saved |
| `node_name` | TEXT | Logical node (e.g., `observe`, `plan`) |
| `state_snapshot` | TEXT | JSON-serialised state at this checkpoint |
| `policy_version` | TEXT | Policy version active at checkpoint time |
| `parent_checkpoint_id` | INTEGER | FK to previous checkpoint (chain) |
| `created_at` | DATETIME | Checkpoint creation timestamp |

### `pending_escalations` (v3)
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `run_id` | TEXT | FK to `runs.id` |
| `step` | INTEGER | Step number that triggered escalation |
| `trigger` | TEXT | `EscalationTrigger` value (e.g., `BUDGET_EXHAUSTED`) |
| `context` | TEXT | JSON context dict at time of escalation |
| `status` | TEXT | `pending`, `approved`, `rejected`, or `edited` |
| `response` | TEXT | Human response/notes (if approved or edited) |
| `created_at` | DATETIME | When escalation was created |
| `resolved_at` | DATETIME | When escalation was resolved (NULL if pending) |

### `forecast_snapshots` (v3)
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Auto-increment ID |
| `run_id` | TEXT | FK to `runs.id` |
| `step` | INTEGER | Forecast step |
| `projected_tokens` | INTEGER | Projected total token usage |
| `projected_cost` | REAL | Projected total cost (USD) |
| `current_error_rate` | REAL | Error rate at time of forecast |
| `timestamp` | DATETIME | Forecast snapshot timestamp |

---

### `gabbe runs [--status STATUS] [--limit N]`

List recent agent runs from the `runs` table.

```bash
gabbe runs                          # all runs, newest first (max 20)
gabbe runs --status completed       # only completed runs
gabbe runs --status budget_exceeded # runs stopped by budget
gabbe runs --limit 5                # show only 5 rows
```

**Status values:** `running`, `completed`, `error`, `budget_exceeded`, `escalated`

---

### `gabbe audit <run-id> [--format json|table]`

Display the structured audit trace for a run.

```bash
gabbe audit abc123-...              # table view (default)
gabbe audit abc123-... --format json  # full JSON trace
```

Reads from `audit_spans` table. Columns shown in table mode: event type, node name, duration (ms), cost (USD), status.

---

### `gabbe replay <run-id> [--from-step N]`

Replay a past run from its checkpoints, substituting recorded tool outputs.

```bash
gabbe replay abc123-...             # replay from step 0
gabbe replay abc123-... --from-step 3  # skip first 3 steps
```

Requires that `checkpoints` rows exist for the run. Use `gabbe brain activate` with checkpoint saving enabled.

---

### `gabbe resume <run-id>`

Resume a run that was paused by the escalation handler (file mode).

```bash
gabbe resume abc123-...
```

Lists all pending escalations for the run, prompts for approve/reject per item, and updates the `pending_escalations` table.

---

### `gabbe registry publish [--out DIR]`

Export the kit's skills as a publish-ready, agentskills.io-standard bundle
(`<slug>/SKILL.md` tree + `manifest.json` + an A2A-style `agent-card.json`) for
universal skill registries. The maintainer performs the actual publish.

```bash
gabbe registry publish --out dist/registry
```

### `gabbe registry add <source> [--namespace NS] [--apply]`

Import an external skill/bundle (local path, `.tar.gz`, or `http(s)` URL) into
`agents/skills/<namespace>/`. Every candidate is validated (real-YAML frontmatter
+ safe-slug + path-traversal + egress/secret/executable-payload scan) and landed
namespaced for review. Dry-run by default; pass `--apply` to write.

```bash
gabbe registry add ./bundle --namespace ext            # dry run
gabbe registry add https://example/skill.skill.md --apply
```

### `gabbe setup`

Run the interactive install wizard (`scripts/init.py`) to wire the kit into your
coding agents. (For a Python-independent install, use `npx gabbe-kit init` or
`curl -fsSL .../install.sh | sh`.) `gabbe setup --force` passes `--force` to the
wizard, and `gabbe setup --hooks` passes `--hooks`.

```bash
gabbe setup
gabbe setup --force               # re-template even preserved files (each backed up first)
gabbe setup --hooks               # also install the optional hooks (off by default)
```

**Behavior:**
- **Never-clobber.** Any differing pre-existing file is backed up to `<name>.gabbe-bak`
  before being refreshed; nothing you already had is silently overwritten. The
  preserve-set (`AGENTS.md`, `CONSTITUTION.md`, `TASKS.md`, `policies.yml`, `config.json`)
  is left untouched unless you pass `--force`, which re-templates them too (still backing
  each up first).
- **Reversible.** The wizard writes `.gabbe/manifest.json` recording everything it created
  (copied kit files, wiring symlinks, generated skill trees, config files), so
  `gabbe uninstall` fully reverses a wizard install.
- **Brownfield autodetect.** In an existing codebase (detects `package.json`,
  `pyproject.toml`, `go.mod`, `Cargo.toml`, `composer.json`, `pom.xml`, `Gemfile`, a `.git`
  repo, etc.) the wizard adds a Mode question — greenfield vs **Upgrade / Refactor
  existing** — prefills detected language / framework / package-manager / project-name as
  defaults, and in refactor mode scaffolds a `BROWNFIELD_ONBOARDING.md` discovery brief
  instead of greenfield mission docs. The greenfield flow is unchanged in an empty dir.
- **Placeholder population.** Derivable `[PLACEHOLDER:]` fields in `AGENTS.md`
  (dev/test/lint/format/typecheck/coverage commands, `repo_url`, `ci_cd`,
  `deployment_target`) are auto-filled; the rest are kept, tagged
  `<!-- OPTIONAL: fill this in yourself -->`, and listed in an end-of-install warning so
  blank fields are never shipped silently.

**Node installer (`npx gabbe-kit init`) flags** — the Python-independent equivalent
supports the same never-clobber/`--force` behavior plus non-interactive install:

| Flag | Description |
|---|---|
| `--yes` | Non-interactive; accept defaults without prompting |
| `--agents <list>` | Comma-separated agents to wire (e.g. `--agents claude,cursor`) |
| `--force` | Re-template even preserve-set files (each backed up to `<name>.gabbe-bak` first) |
| `--wizard` | Delegate to the full Python wizard (`scripts/init.py`) when `python3` is available (interactive) |

```bash
npx gabbe-kit init --yes --agents claude,cursor
npx gabbe-kit init --force
```

---

### `gabbe eval [--live] [--out FILE]`

Run the skill eval suites (`agents/skills/<category>/evals/*.eval.yaml`) via the
kit-layer harness (`agents/scripts/eval_skills.py`). The default deterministic
self-check lints every suite and self-tests the assertion evaluators with **no
model** (safe per-commit). `--live` renders each prompt, scores outputs against
the model, and writes a JSON scorecard (nightly; needs `GABBE_LIVE_LLM=1`).

```bash
gabbe eval                       # deterministic self-check
GABBE_LIVE_LLM=1 gabbe eval --live --out scorecard.json
```

Evals sample the input space and raise confidence — they do not prove correctness.

---

### `gabbe doctor`

Read-only environment & install report. Auto-detects the OS/arch, the available
runtimes/package managers (`python3`, `pip`, `pipx`, `node`, `npm`, `npx`, `git`,
`curl`), and which agent clients are present in the target (Claude Code, Cursor,
Copilot, Gemini, Codex, Windsurf, Cline, Aider, Zed, Antigravity, OpenCode,
Continue, Roo, Kilo), then prints a PASS/WARN per check. Used by the multi-OS
`install-matrix` and post-publish `release-verify` CI jobs to confirm a
one-command install succeeded.

Upgrade check: it reads the `*GABBE Kit version: X.Y.Z*` stamp of the project's
`agents/AGENTS.md` and `agents/CONSTITUTION.md` and warns (exit code unchanged) when a
stamp is missing or older than the CLI, or when the constitution has no `### Article 0`.
The installers keep edited files, so new kit rules do not arrive by themselves; see
`docs/UPGRADING.md`.

```bash
gabbe doctor
```

---

### `gabbe update [--agents LIST] [--global] [--dir PATH]`

Refresh the installed kit from a checkout of this repository (not available from the
PyPI package alone). A kit file you changed is copied to `<name>.gabbe-bak` before it is
replaced; `AGENTS.md`, `CONSTITUTION.md`, `TASKS.md`, `policies.yml`, `config.json` and
your memory and project files are kept once you have changed them; a kit file that is no
longer shipped is removed only if you never changed it. The earlier install record is
merged, not replaced, so wiring links and generated skill folders stay. Generated skill
folders are not regenerated: re-run the installer for that. Target resolution: `--dir` >
`--global` > project (cwd).

```bash
gabbe update
```

---

### `gabbe uninstall [--agents LIST] [--dry-run] [--purge] [--global] [--dir PATH]`

Reverse a GABBE install using its `.gabbe/manifest.json`: removes exactly what was
recorded, restores a file of yours that the install replaced, takes the kit's pointer block
out of your instruction files, preserves any file you edited after
install as `<name>.gabbe-bak` (rather than deleting it), prunes now-empty wiring dirs, and
never touches unrelated files. Since 1.1.4 every installer writes the record (`gabbe setup`,
`npx gabbe-kit init`, `gabbe update`). Without a record the command exits with status 1 and
removes nothing. `--agents` deselects specific agents only; `--dry-run` prints the plan
without changing anything; `--purge` is kept for compatibility and is the same as a plain uninstall; your own files,
changed files, memory files and backups always stay. A record that cannot be read is never
acted on.
Idempotent and isolated (never writes outside the target).

```bash
gabbe uninstall --dry-run
gabbe uninstall
```

---

## Troubleshooting

**`EnvironmentError: GABBE_API_KEY is not set`**
Set the env var: `export GABBE_API_KEY=sk-...` before running LLM-dependent commands.

**`Database not initialized`**
Run `gabbe init` first.

**`project/TASKS.md` always re-importing on every `gabbe sync`**
Check that `updated_at` is being written correctly to the DB.
The DB timestamp (from `MAX(updated_at) FROM tasks`) must be ≥ the file mtime after an import.

**CI: `validate_skills.py` not found**
The validators ship in the kit's `agents/scripts/` directory and are copied into your project
with the kit. If they are missing, re-run the installer (`npx gabbe-kit init` or `python3 scripts/init.py`).
