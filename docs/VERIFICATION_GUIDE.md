# GABBE Comprehensive Verification Guide

> **Audience:** maintainers verifying an install. **Scope:** how to validate the kit and run the validation scripts.

> **Important**: This guide consolidates all testing and verification processes for the GABBE Agentic R&D Engineering Framework into a single, comprehensive source of truth. Use this to explicitly verify the integrity of the framework and its CLI.

---

## 🏗️ 1. Environment & Setup

Before running tests or launching verifiers, ensure the project development environment is correctly bootstrapped.

### Prerequisites:
- **Python:** versions 3.8 to 3.12 support the GABBE framework and test runners.
- **Node.js**: Expected by specific NPM-based tools or workflows, though Python is the framework root.

### Installation:
```bash
git clone https://github.com/andreibesleaga/GABBE.git
cd GABBE
python -m venv .venv
source .venv/bin/activate       # For Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

*Optionally*, establish environment secrets to verify API-driven paths (Required for executing the `gabbe brain`, `gabbe route`, and specific integration scenarios):
```bash
cp .env.example .env
export GABBE_API_KEY="sk-..."    # Add remote LLM keys for deep integration
```

---

## 🧪 2. Core Python Unit & Integration Testing

The heart of the GABBE orchestration, database integration, memory access, and MCP translation occurs in the `gabbe/` module. The core tests target its routing (`route.py`), budget control (`budget.py`), orchestration logic (`brain.py`), and subprocess checking logic (`verify.py`).

**Run the Full Suite (322 tests):**
```bash
# Discovers all tests in gabbe/tests and scripts/tests
pytest
```

**Run a specific test file:**
```bash
pytest gabbe/tests/test_brain.py -v
pytest gabbe/tests/test_edge_cases.py -v
pytest scripts/tests/test_init.py -v
```

### 2.1 Test File Reference

#### `gabbe/tests/` — CLI & Core Module Tests

| File | Coverage |
|---|---|
| `test_brain.py` | `activate_brain` (empty tasks, LLM none, task stats), `evolve_prompts` (seed, multi-gen, LLM none), `run_healer` (all clear, missing files, DB unreachable) |
| `test_brain_integration.py` | Brain with `RunContext`, `HardStop`, `Budget`, escalation on LLM error, context passthrough |
| `test_budget.py` | `Budget.from_config()`, token/cost limits, `BudgetExceeded`, `remaining()` |
| `test_config.py` | Environment variable loading, path resolution |
| `test_context.py` | `RunContext` lifecycle, DB run records |
| `test_database.py` | Schema tables, schema version, unique constraint, row factory, idempotent `init_db` |
| `test_e2e.py` | Sync import/export, brain evolve, cost router, status dashboard, verify pass/fail, brain activate/heal |
| `test_e2e_workflow.py` | Full 14-step golden path workflow (init → sync → status → verify → route → brain → forecast → runs → audit → replay → resume → MCP); platform controls (budget, hardstop, policy, gateway, escalation, replay); MCP JSON-RPC protocol |
| `test_edge_cases.py` | **NEW v0.8.0** — See Section 2.2 |
| `test_escalation.py` | `EscalationHandler` modes (silent, file, interactive), `EscalationPaused` |
| `test_forecast.py` | `run_forecast` with history data, empty DB, cost projections |
| `test_gateway.py` | `ToolGateway` register/execute, policy enforcement |
| `test_hardstop.py` | `HardStop` max iterations, `should_wrap_up`, `MaxIterationsExceeded` |
| `test_llm.py` | `call_llm` with mocked API, timeout handling |
| `test_llm_backoff.py` | Exponential backoff on rate limits |
| `test_llm_retries.py` | Retry logic on transient API errors |
| `test_main.py` | CLI dispatch: `--version`, `init`, `db`, `sync`, `verify`, `status`, `route`, `brain activate/evolve/heal`; error handling (EnvironmentError→exit 1, KeyboardInterrupt→exit 130, generic→exit 1) |
| `test_mcp_server.py` | MCP JSON-RPC: auth token rejection, command allowlist block/permit, empty command |
| `test_mva_core.py` | MVA platform core behaviour |
| `test_policy.py` | `ToolAllowlistPolicy`: allow, deny, deny overrides allow |
| `test_replay.py` | `CheckpointStore`, `ReplayRunner`, `replay --from-step` |
| `test_route.py` | Simple→LOCAL, complex→REMOTE, threshold, env var override |
| `test_status.py` | Dashboard sections, empty DB, task counts, 100% progress, progress bar overflow, phase display |
| `test_sync.py` | `parse_markdown_tasks` (all status variants), `generate_markdown_tasks`, roundtrip, timestamp parsing, `sync_tasks` (import/export/empty/atomic), `_atomic_write` cleanup |
| `test_sync_fallback.py` | Preamble preservation without markers, fallback append when no task list found |
| `test_sync_markers.py` | `_generate_task_lines`, legacy parse, marker-bounded parse, reads only marked section |
| `test_verify.py` | `run_verification` pass/fail, `parse_agents_config`, `run_command` uses shlex not shell |

#### `scripts/tests/` — Installer Tests

| File | Coverage |
|---|---|
| `test_init.py` | Local/global/custom install (first-time, update, reinstallation), legacy modernization, data science AI, other language, missing source dir, same source/target dir |
| `test_dynamic_setup.py` | Dynamic tech map building, platform-specific skill setup, Cursor rules generation |

---

### 2.2 Edge Case Tests (`gabbe/tests/test_edge_cases.py`) — NEW in v0.8.0

Run all edge case tests:
```bash
pytest gabbe/tests/test_edge_cases.py -v
```

**CLI dispatch — commands not previously unit-tested:**
```bash
pytest gabbe/tests/test_edge_cases.py -v -k "runs or forecast or audit or replay or resume"
```
- `test_runs_command_empty` — `gabbe runs` with no records → "No runs found"
- `test_runs_command_with_data` — `gabbe runs` lists run ID, command, status
- `test_runs_command_status_filter` — `gabbe runs --status completed` filters correctly
- `test_forecast_command_dispatches` — `gabbe forecast` dispatches to `run_forecast`
- `test_forecast_empty_db_no_crash` — no crash on empty DB
- `test_audit_command_no_spans` — "No audit spans found" for unknown run ID
- `test_audit_command_json_format` — `--format json` outputs valid JSON list
- `test_replay_command_empty` — "No checkpoints to replay" for unknown run
- `test_resume_command_no_escalations` — "No pending escalations" for unknown run

**Memory & Database lifecycle:**
```bash
pytest gabbe/tests/test_edge_cases.py -v -k "memory"
```
- `test_memory_directory_created_on_init` — all schema v3 tables present: `runs`, `audit_spans`, `budget_snapshots`, `checkpoints`, `pending_escalations`, `forecast_snapshots`, `pricing_registry`
- `test_memory_persists_across_sync_cycles` — import from TASKS.md → verified in DB with correct statuses

**Sync edge cases:**
```bash
pytest gabbe/tests/test_edge_cases.py -v -k "sync"
```
- `test_sync_unicode_task_titles` — 🚀, ✅, 中文 characters survive sync roundtrip
- `test_sync_task_with_special_markdown_chars` — backticks and `[brackets]` survive
- `test_sync_duplicate_titles_handled` — duplicate task titles don't cause a crash

**Brain mode stress:**
```bash
pytest gabbe/tests/test_edge_cases.py -v -k "evolve or heal"
```
- `test_evolve_multi_generation` — 5 successive evolve calls with `success_rate` increments produce ≥6 generations (gen 0 seed + gens 1–5)
- `test_brain_heal_one_file_missing` — partial file existence: present files shown, missing files flagged, DB still reachable

**Status & platform:**
```bash
pytest gabbe/tests/test_edge_cases.py -v -k "status or mcp or unknown"
```
- `test_status_large_mixed_workload` — 100 tasks (50 done/30 todo/20 in-progress) → 50% shown without crash
- `test_serve_mcp_importable` — `mcp_server.serve` function is callable
- `test_unknown_command_prints_help` — unknown CLI command → argparse exit code 2

---

## 📁 3. GABBE Agents/Content Integrity Scripts

Because GABBE relies heavily on markdown context structures (`/agents/skills`, `/agents/templates`, `/agents/guides`), syntax errors or broken internal paths can critically affect agent behavior.

A series of purpose-built Python compilation scripts ensure that your modifications conform precisely to the framework rules. All these scripts are stored in the `agents/scripts/` folder.

**Check Structural Integrity:**
```bash
# Checks if skills, templates, guides are valid and that `agents/AGENTS.md` matches `AGENTS_TEMPLATE.md` structures.
python3 agents/scripts/validate_integrity.py
```

**Verify Internal Links & Logic Chains:**
```bash
# Asserts that [links](myfile.md) all point to valid files. Critical to prevent autonomous agents from hallucinating paths.
python3 agents/scripts/validate_links.py

# Verifies that skills match the specific schemas and headers expected array mapping
python3 agents/scripts/validate_skills.py

# Maps use cases end-to-end to ensure personas properly bridge triggers across skills -> templates
python3 agents/scripts/verify_use_cases.py

# Traverses Prompts + MCP configs to guarantee external calls fit configured APIs
python3 agents/scripts/verify_triggers_and_mcps.py

# Verifies all skills are referenced in docs, all personas exist and are documented
python3 agents/scripts/check_skills_docs.py
python3 agents/scripts/comprehensive_checker.py
```

**E2E Init Flow Simulation:**
```bash
# Runs 12 permutations: global/local/custom × install/update flows
python3 agents/scripts/verify_e2e_init_flows.py

# Tests symlink creation, tech map building, skill setup for each platform
python3 agents/scripts/verify_setup_simulation.py
```

**Run Everything in One Pass:**
```bash
# Umbrella runner aggregating logs across all structural checkers
bash agents/scripts/setup-context.sh
```

---

## 🖥 4. CLI Architecture Testing (`gabbe verify`)

The CLI Enforcer serves as a powerful programmable integrity checking tool when building external apps. We must confirm the standalone GABBE CLI commands operate identically within an SDLC checkpoint.

**Mock a Workspace Sync & Check Workflow:**

```bash
# 1. Initialize SQLite memory (Required once per new project map)
gabbe init

# 2. Sync CLI Tasks with your markdown files
gabbe sync

# 3. Test the verify loop.
# Note: By design, `gabbe verify` will initially FAIL on fresh projects to prevent unauthorized deployment, 
# primarily throwing execution errors until you fill in [PLACEHOLDER] variables inside `project/TASKS.md` or `AGENTS.md`. 
gabbe verify
```
*Expected Behavior:* If `gabbe verify` produces "Verification FAILED" because of `[PLACEHOLDER:]` elements (like `[PLACEHOLDER: pnpm test]`), the verifier is correctly identifying missing human instruction mapping.

**Test Additional CLI Commands:**
```bash
# List agent runs (optionally filter by status)
gabbe runs
gabbe runs --status completed

# Inspect structured audit trace for a run
gabbe audit <run-id>
gabbe audit <run-id> --format json

# Replay a past run from checkpoints
gabbe replay <run-id>
gabbe replay <run-id> --from-step 2

# Resume a paused/escalated run
gabbe resume <run-id>
```

---

## 🤖 5. Simulating Agent Workflows

The ultimate verification requires simulating the system acting as an intelligent agent running either Loki or Brain orchestration.

**Verify Cost Forecaster (CLI):**
```bash
# Ensures history parsing works
gabbe forecast
```

**Verify Subprocess Limits:**
```bash
# This forces testing the CLI execution timeouts limit on `gabbe_subprocess_timeout` rules
export GABBE_SUBPROCESS_TIMEOUT=5 
gabbe verify
```

**Verify Model Context Protocol (MCP) Bind:**
```bash
# Launches the JSON-RPC local server. It should start listening via STDIN/STDOUT.
gabbe serve-mcp
# Cancel using CTRL+C
```

**Run The Evolutionary Pipeline (EPO):**
```bash
# Note: An active GABBE_API_KEY must be exported in your terminal context to test evolution.
# Simulates the neural rewiring of a specific skill prompt based on historic error patterns.
gabbe brain evolve --skill tdd-cycle
```

---

## ✅ 6. Verification Checklist

Upon passing all elements in this guide, the framework is confirmed 100% operationally verified:

| Check | Command | Expected Result |
|---|---|---|
| Full test suite | `pytest` | **322 passed** |
| Structural integrity | `python3 agents/scripts/validate_integrity.py` | Project integrity check passed |
| Link validation | `python3 agents/scripts/validate_links.py` | All links valid (380 files, 196 links) |
| Skills validation | `python3 agents/scripts/validate_skills.py` | All 170 skills passed |
| Use cases | `python3 agents/scripts/verify_use_cases.py` | All 456 assertions PASSED |
| Triggers & MCPs | `python3 agents/scripts/verify_triggers_and_mcps.py` | 66 MCPs, 168 skills, 0 warnings |
| Skills doc coverage | `python3 agents/scripts/check_skills_docs.py` | 168/170 in index |
| Personas & quality | `python3 agents/scripts/comprehensive_checker.py` | No corrupted headers, no outdated CLI versions |
| Setup simulation | `python3 agents/scripts/verify_setup_simulation.py` | Symlink fallback works |
| E2E init flows | `python3 agents/scripts/verify_e2e_init_flows.py` | All 12 permutations PASSED |
