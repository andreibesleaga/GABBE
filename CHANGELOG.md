# Changelog

All notable changes to GABBE are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased] — 2026-02-20

### Changed
- Refactored directories, filenames, and structure
- Updated README.md and fixed inaccuracies in QUICK_GUIDE.md
- Fixed full docs links

### Fixed
- Quote Mermaid node labels with parentheses
- Fixed diagrams
- General CLI, format, and Windows compatibility fixes

### Removed
- Removed Android/iOS installation instructions
- Removed loki leftovers from tests

---

## [0.2.0] — 2026-02-19

### Added
- GABBE CLI 0.3.0 (Stable) with Zero-Dependency architecture.
- Full Antigravity / Gemini support.
- Comprehensive Troubleshooting Guide.
- AI-Native Engineering Scenarios guide.
- Self-Healing loop with 5-attempt limit and human escalation.
- Multi-agent swarm (Loki Mode) with 30+ personas.
- 4-layer memory architecture (Working, Episodic, Semantic, Procedural).
- Comprehensive checker scripts for kit integrity.
- GABBE CLI 0.3.0: `gabbe init`, `gabbe sync`, `gabbe status`, `gabbe verify`, `gabbe route`, `gabbe brain`
- Bidirectional `TASKS.md ↔ SQLite` sync with timestamp arbitration (`gabbe sync`)
- Brain Mode with Active Inference loop and Evolutionary Prompt Optimization (`gabbe brain`)
- Cost-Effective LLM Router (`gabbe route`) — LOCAL vs REMOTE decision based on complexity + PII detection
- Self-Healing Watchdog (`gabbe brain heal`) — checks DB connectivity and required project files
- Schema migration system (`schema_version` table) for forward-compatible DB upgrades
- `UNIQUE(title)` constraint on `tasks` table to prevent silent duplicate corruption
- Atomic file writes in `export_to_md` (temp-file + `os.replace`)
- Expanded PII detection patterns (email, phone, SSN, credit card, credential keywords)
- All configurable values exposed via environment variables:
  `GABBE_API_URL`, `GABBE_API_KEY`, `GABBE_API_MODEL`, `GABBE_LLM_TEMPERATURE`,
  `GABBE_LLM_TIMEOUT`, `GABBE_ROUTE_THRESHOLD`
- `[project.optional-dependencies] dev` in `pyproject.toml` for `pytest`
- `[tool.pytest.ini_options]` in `pyproject.toml`
- `tests/conftest.py` with shared `tmp_project` and `db_conn` fixtures
- Unit test files: `test_config.py`, `test_database.py`, `test_llm.py`, `test_route.py`,
  `test_sync.py`, `test_verify.py`
- CI pipeline now installs the package and runs `pytest tests/`

### Changed
- `gabbe/verify.py`: `parse_agents_config()` now only reads the `## Commands` section
  of `AGENTS.md`; commands outside that section are silently ignored
- `gabbe/verify.py`: `run_command()` uses `shell=False` with `shlex.split()` — eliminates
  shell injection risk
- `gabbe/llm.py`: raises `EnvironmentError` when `GABBE_API_KEY` is unset (was silently
  returning a mock string)
- `gabbe/llm.py`: default model updated from `gpt-4-turbo-preview` → `gpt-4o`
- `gabbe/status.py`: reads `current_phase` from `project_state` table (was hardcoded)
- `gabbe/brain.py`: `run_healer()` performs real checks (was a stub returning 100% Nominal)
- `gabbe/brain.py`, `gabbe/status.py`: DB connections closed with `try/finally`
- `gabbe/sync.py`: handles "both empty" edge case explicitly; multi-format timestamp
  parsing; atomic file export
- `gabbe/config.py`: removed `MAGENTA = '\033[95m'` duplicate of `HEADER`; added
  `LLM_TEMPERATURE`, `LLM_TIMEOUT`, `ROUTE_COMPLEXITY_THRESHOLD`, `PROGRESS_BAR_LEN`
- `gabbe/__init__.py`: removed eager imports to prevent side effects on import
- `gabbe/main.py`: all command dispatches wrapped in `try/except` for user-friendly errors

### Fixed
- Shell injection vulnerability in `verify.py`
- Silent mock LLM responses masking missing API key
- Unclosed SQLite connections in `brain.py` and `status.py`
- Non-atomic TASKS.md writes causing potential corruption on crash
- Duplicate `MAGENTA`/`HEADER` ANSI code in `Colors` class
- Dead code `if ... : pass` branch in `init.py`

---

## [0.1.0] — 2026-02-01

### Added
- Initial release of the GABBE Agentic Engineering Kit
- `init.py` Universal Skill Compiler (Cursor, VS Code, Claude Code, Gemini)
- Skill, Template, Guide, and Persona framework (`.agents/` directory)
- `AGENTS.md` + `CONSTITUTION.md` for agent governance
- Multi-platform skill distribution
- Initial documentation: `README.md`, `README_FULL.md`, `QUICK_GUIDE.md`
- Research whitepapers in `docs/`
