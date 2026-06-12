# Changelog

All notable changes to GABBE are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.9.6] — 2026-06-12 — Operating spine, universal install, more agents, registry interop

Strictly backward-compatible with the last released tag, v0.8.0-beta (6 gates +
golden + validators green). All new behavior is additive; the only removals are
pre-release internals that never shipped in any tagged release (see Removed).

### Added — operating spine (markdown, runtime-agnostic)
- **`core/preflight`** (mandated Step 0): auto-check + load index summaries + memory
  headers + cost posture + recommend the optimal capability set, then clarify.
- **`core/clarify`**: uncertainty-aware clarifying questions at every step + a
  reasoning-pattern menu.
- **`core/state-preserve` + `core/state-portability`** (+ `state_export.sh` /
  `state_import.sh`): continuous + pre-cutoff checkpointing (RESUME_POINTER) so a
  token/time/crash cutoff never loses progress; portable, agent-agnostic state
  export/import to continue in any other coding agent/LLM.
- **`core/update-scan`**: discover + adopt the best skills/tools/MCPs/models, gated
  by `GABBE_AUTONOMY` + budget; A2-only evolution + misaligned-replay guard;
  protected files; policy-as-code self-enforcement.
- **`coordination/persona-selector`** (selection/tiering/delegation/voting) +
  **`coordination/self-optimize`** (autonomy levels L0–L3 + macro/meso/micro alignment).
- **`core/skills-registry`** + **`core/final-review`** skills.

### Added — first-class concerns
- **Observability**: AGENTS.md/CONSTITUTION mandates + OTel GenAI semantic
  conventions in `gabbe/audit.py` (`genai_usage_attributes`, `record_genai_usage`,
  content-redaction toggle).
- **Spec-Driven**: spec → evals → test → code; EARS; golden-thread traceability.
- **Human–Agent Collaboration**: manager-not-operator; Purpose/Transparency/Control
  (`guides/principles/human-agent-collaboration.md`, `guides/ai/agent-operating-ergonomics.md`).

### Added — agents, install, registry, CLI
- **Six more coding agents**: Antigravity, OpenCode, Zed, Continue, Roo Code,
  Kilo Code (Gemini split out, backward-compatible); universal `.agents/skills/`
  emitter; new golden platforms `antigravity` + `opencode`.
- **Universal install**: `npx gabbe init` (`bin/install.js`), `install.sh` /
  `install.ps1`, `MANIFEST.in` (kit in sdist), `release.yml` (wheel + npm + tarball).
- **Skills-registry interop**: `scripts/registry_export.py` / `registry_import.py`;
  `gabbe registry publish|add` + `gabbe setup` CLI verbs.
- **Per-project policy**: `GABBE_AUTONOMY` + `project/gabbe.config.json`
  (`gabbe/config.py`); pre-step cost reservation `budget.reserve()`/`can_afford()`.
- **`scripts/verify_all.sh` + `TESTING.md`**: one-stop verification + how-to-test.

### Security — release-hardening sweeps (PRs #13–15)
- **Policy engine fail-closed**: a present `policies.yml` with no/empty/null
  `tools` section now denies all (was allow-all / crashed on `tools:` null).
- **Audit redaction closure**: OTel `gabbe.input`/`gabbe.output` span attributes
  are redacted like the JSONL path; non-JSON-serializable objects are
  stringified-then-redacted so `__str__` output can't smuggle PII/secrets past
  `json.dumps(default=str)`.
- **`state_import.sh` hardening**: fatal portable `mktemp` template (no
  predictable temp dir), `pipefail`, `--no-same-owner --no-same-permissions`
  extraction; symlink/hardlink + traversal members already rejected.
- **`setup-context.ps1`**: link detection by `LinkType` (SymbolicLink / Junction /
  HardLink) — never moves a real file/dir mistaken for a link.
- **Consistency gate** grown to 8 invariants (dangling concrete-path scan with
  `agents/` prefix handling, guides-count parity, fence balance, persona
  resolution, gate-label drift, …).

### Changed — typing + hardening pass (Gemini/Antigravity audit + follow-ups)
- **`gabbe/` core fully typed**: `mypy --strict` clean across all 21 core modules.
- **`brain.py`**: gene selection now implements the documented epsilon-greedy
  policy (20% exploration of the newest generation) instead of pure greedy.
- **`sync.py`**: Windows-safe atomic writes (`os.replace` PermissionError retry).
- **`gateway.py`**: tool-argument validation is fail-closed — a parameterized
  tool refuses to execute when `jsonschema` is unavailable (and `jsonschema>=4`
  is now a required dependency, so it always is available on a normal install).
- **`llm.py`**: opt-in `GABBE_LLM_CACHE` (cache identical deterministic LLM
  calls locally; 0 tokens on a hit; off by default) + malformed-JSON handling.
- **New checks**: `scripts/tests/test_capability_layer.py` (kit-wide link +
  frontmatter CI test); `scripts/fill_placeholders.py` interactive setup utility.
- **`update-scan.skill.md`**: self-evolution git-branching workflow (never
  mutate `main`; `evolve/{feature}` branch + tests + human review before merge).
- New regression tests: `GABBE_AUTONOMY` precedence (env > project config >
  `hybrid`), `budget.reserve()` semantics, real-jsonschema gateway validation.

### Removed — pre-release internals (never shipped in a tagged release)
- `gabbe.audit.traced` decorator, `gabbe.config.SKILLS_DIR`,
  `gabbe.config.UNDERLINE` (unused internals; the public span API is
  `start_span`/`end_span`).

## [0.9.0] — 2026-06-10 — Audit Hardening (strict backward-compatible)

### Security
- **MCP server fail-closed by default** (was unauthenticated + allow-all): `gabbe serve-mcp` now blocks commands unless `GABBE_MCP_ALLOWED_COMMANDS` is set and requires a token; `GABBE_MCP_INSECURE=1` restores legacy behavior. Added a subprocess timeout and MCP `protocolVersion` (2025-11-25).
- Skill-name slug sanitization blocks path traversal in the emitter.
- Audit logs (`project/logs/*.jsonl`) now redact emails/keys/tokens.

### Added
- **Dual license**: Apache-2.0 (`LICENSE-CODE`) for code + CC-BY-SA-4.0 for content; SPDX headers on all `.py`.
- `docs/SCHEMA.md` (emitted-format contract), `SECURITY.md`, `CODE_OF_CONDUCT.md`, `docs/adr/` (3 ADRs).
- Golden emitter tests + `scripts/gates/` backward-compat gate harness.
- `requirements-lock.txt` (hashed); ruff/black/mypy tooling; `init.py --bench`.
- CI: docs-lint, security-baseline (osv/pip-audit/trivy), scorecard, SBOM release, dependabot; Python matrix 3.8–3.13.
- Root `AGENTS.md` + `GEMINI.md` emitters; `gabbe-schema-version` in all emitted artifacts.
- Cross-process advisory lock for `gabbe sync`.

### Changed
- **Claude Code skills now emit `.claude/skills/<name>/SKILL.md` directories** (agent-skills standard) — previously symlinked `*.skill.md` files that Claude Code could not discover. Cursor rules are now agent-requested (no `globs: *`).
- `docs/MCP_CONFIGURATIONS.md`: corrected package names verified against npm/PyPI (2026-06-10).

### Fixed
- Installer no longer clobbers user files on the symlink-fallback path.
- `compile_skills.py` backup `.bak` no longer drops file extensions.

---

## [0.8.0] — 2026-03-05

### Changed
- Refactored directories, filenames, and structure
- Updated README.md and fixed inaccuracies in QUICK_GUIDE.md
- Fixed full docs links

### Added
- **Kit Installation Safeguards**: Upgraded `init.py` with `safe_merge_directory()` to natively block overarching uninstalls and safeguard all files in `project/`, `memory/`, `TASKS.md`, `policies.yml`, and `config.json` when pulling GABBE ecosystem upgrades across Local, Global, and Custom architectures.
- **Time Complexity MCP Integration**: Added `time-complexity-mcp` (Big-O static analysis via tree-sitter) as a first-class capability:
  - New skill: `agents/skills/coding/time-complexity.skill.md`
  - New guide: `agents/guides/patterns/time-complexity-analysis.md`
  - New template: `agents/templates/coding/TIME_COMPLEXITY_REPORT_TEMPLATE.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Security & Code Quality section)
  - Updated all index files, `README.md`, and `README_FULL.md`
- **MCP Configurations Guide**: Created `docs/MCP_CONFIGURATIONS.md` — comprehensive per-server installation, API key setup, and usage guides for all 42+ MCP servers in the template. Cross-referenced from `README.md`, `README_FULL.md`, `QUICK_GUIDE.md`, and `MCP_CONFIG_TEMPLATE.json`.
- **Excalidraw MCP Integration**: Added `@cmd8/excalidraw-mcp` for programmatic Excalidraw diagram creation:
  - New skill: `agents/skills/coding/excalidraw.skill.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Design & Visual section)
- **Sketch-to-Diagram Pipeline**: Added `mcp-image-recognition` + Excalidraw for converting hand-drawn sketches to formal diagrams:
  - New skill: `agents/skills/coding/sketch-to-diagram.skill.md`
  - New template: `agents/templates/coding/SKETCH_TO_DIAGRAM_TEMPLATE.md`
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Sections 4-5)
  - MCP config entry for `image-recognition` in `MCP_CONFIG_TEMPLATE.json`
- **tldraw MCP Integration**: Added `@talhaorak/tldraw-mcp` for persistent visual canvas (9 tools):
  - New skill: `agents/skills/coding/tldraw-canvas.skill.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Design & Visual section)
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Section 5)
- **Visual Product Design Phase**: End-to-end pipeline for processing visual inputs into structured specs before implementation:
  - New guide: `agents/guides/planning/visual-product-specs.md` (input catalogue, recognition pipeline, output mapping, design readiness gate)
  - New skill: `agents/skills/product/visual-specs.skill.md` (5-phase workflow: collect → recognize → structure → generate → assemble)
  - New template: `agents/templates/product/VISUAL_SPEC_PACKAGE_TEMPLATE.md` (7-section package with design readiness checklist)
  - Updated PRD template: Section 6.1 Visual Data Model + Section 8 tldraw/Visual Spec Package refs
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Section 7 cross-ref)

### Added (Phase 13: Specialized Systems & Standards)
- **Industry Category**: Added specialized software engineering support for:
  - **Telecom & Networks**: TMF ODA, CAMARA APIs, GSMA eSIM (skill, guide, template).
  - **Healthcare**: HL7 FHIR clinical data exchange (skill, guide, template).
  - **Industrial IoT**: OPC UA, MQTT, Purdue Model (skill, guide, template).
  - **Global Standards**: UN SDGs, ITU-T, OSI/OpenSSF compliance (skill, guide, template).
  - **Engineering Standards**: IEEE, ACM Ethics, ISO/IEC 12207 audits (skill, guide, template).
- **Core Specialized Systems**:
  - **FinOps**: Cloud cost optimization auditing (guide, skill).
  - **Scalability**: Horizontal and Vertical scaling architecture audit (skill, guide, template).
  - **Green Tech & Sustainability**: ESG checks, Carbon intensity (SCI) reporting (skills, guides, template).
  - **Blockchain & DLT**: Smart contract and distributed ledger design (skill, guide, template).
  - **Semantic Web**: RDF/OWL Ontology design for meta-knowledge (skill, guide, template).


### Fixed
- Quote Mermaid node labels with parentheses
- Fixed diagrams
- General CLI, format, and Windows compatibility fixes

### Removed
- Removed Android/iOS installation instructions
- Removed loki leftovers from tests

### Audited & Verified
- Conducted a full GABBE deep-audit to guarantee stability across workflows, codebase, and documentation.
- **Workflows & Logic Verification**: `init.py` handles step 0 / step 1 initialization perfectly. The `gabbe` CLI tool `sync`, `router`, and `status` modes execute accurately.
- **Test Suite Execution**: Checked the baseline test health using `pytest`. **`251 / 251` tests passed** natively with zero regressions.
- **Documentation Parity**: `agents/skills/00-index.md` matches exactly 126 backend `.skill.md` files. `agents/templates/00-index.md` categorizes all 60+ template definitions. Markdown structure tree diagrams (`README.md`, `README_FULL.md`) correctly reflect the recent refactoring.
- **Codebase Cleanliness**: Swept the repository for `TODO`, `FIXME`, and `HACK`. No loose tech-debt markers exist in the source code; they correctly only exist inside rules or testing string assertions.
- **Architectural Purity**: Clean workspace with zero stranded, orphaned, or unused script files left behind.
- **Scripts Validation**: Validated that all 126 skills and 60+ templates exist exactly as advertised with zero broken internal links using `agents/scripts/comprehensive_checker.py` and `validate_skills.py`.
- **CLI Reference Fixed**: Replaced outdated `0.3.0` CLI references across the docs with the actual `0.7.0` version to perfectly reflect the release state.

---

## [0.7.1] — 2026-02-25

### Added — MVA Platform Control Layer
- **`gabbe/budget.py`**: `Budget` and `BudgetEnforcer` — token, cost, tool call, wall-time, and iteration limits per run; pricing loaded from `pricing_registry` table; `BudgetExceeded` exception.
- **`gabbe/hardstop.py`**: `HardStop` — absolute iteration/depth/timeout guards with `tick()`, `remaining_steps()`, and `should_wrap_up()`.
- **`gabbe/policy.py`**: `PolicyEngine` with YAML-driven `ToolAllowlistPolicy`, `RolePolicy`, `ContentSafetyPolicy`, `ParameterRangePolicy`; deny-all secure default when policy file is absent.
- **`gabbe/gateway.py`**: `ToolGateway` — single mediated execution point with rate limiting, circuit breaker, JSON Schema validation, and audit integration.
- **`gabbe/audit.py`**: `AuditTracer` — structured spans to SQLite `audit_spans` + JSONL + optional OTel; `snapshot_budget()`.
- **`gabbe/escalation.py`**: `EscalationHandler` — three modes (`cli`, `file`, `silent`); `EscalationPaused` exception for `file` mode; `[e]dit context` option in CLI mode.
- **`gabbe/replay.py`**: `CheckpointStore` + `ReplayRunner` — deterministic replay from `checkpoints` table; `diff()` to compare two runs.
- **`gabbe/context.py`**: `RunContext` context manager wiring all platform controls together; `from_checkpoint()` for replay.
- **`gabbe/forecast.py`**: `run_forecast()` — project remaining work cost/token estimates; writes to `forecast_snapshots`.
- **New CLI commands**: `gabbe runs`, `gabbe audit`, `gabbe replay`, `gabbe resume`.
- **Schema v3**: 7 new tables — `pricing_registry`, `runs`, `audit_spans`, `budget_snapshots`, `checkpoints`, `pending_escalations`, `forecast_snapshots`.
- **New env vars**: `GABBE_MAX_COST_USD`, `GABBE_MAX_TOKENS_PER_RUN`, `GABBE_MAX_TOOL_CALLS_PER_RUN`, `GABBE_MAX_ITERATIONS`, `GABBE_MAX_WALL_TIME`, `GABBE_MAX_RECURSION_DEPTH`, `GABBE_MAX_RETRIES_PER_TOOL`, `GABBE_POLICY_FILE`, `GABBE_ESCALATION_MODE`, `GABBE_OTEL_ENABLED`, `GABBE_SUBPROCESS_TIMEOUT`, `GABBE_MCP_TOKEN`, `GABBE_MCP_ALLOWED_COMMANDS`.
- MCP server: `GABBE_MCP_TOKEN` authentication and `GABBE_MCP_ALLOWED_COMMANDS` allowlist for `run_command`.
- 251-test suite covering all platform control modules (`test_budget`, `test_hardstop`, `test_gateway`, `test_policy`, `test_audit`, `test_replay`, `test_escalation`, `test_context`, `test_brain_integration`).
- `docs/PLATFORM_CONTROLS.md` and `docs/CLI_REFERENCE.md` documenting the full control layer.

### Fixed
- Reasoning token cost calculation for o1/o3-class models (`budget.py`).
- Audit span timestamps now reflect span start time, not end time (`audit.py`).
- Exception detection uses `isinstance()` instead of string matching (`context.py`).
- `EscalationPaused` correctly propagates without double-escalation (`brain.py`).
- Deny-all default when `project/policies.yml` is absent (`policy.py`).
- Forecast zero-tasks division-by-zero and DB connection leak (`forecast.py`).
- Checkpoint replay lookup uses per-node occurrence index (`replay.py`).
- Hash delimiter added in sync state hash (`sync.py`).
- LIMIT query parameterized in `gabbe runs` (`main.py`).

---

## [0.7.0] — 2026-02-19

### Added
- GABBE CLI 0.7.0 (Stable) with Zero-Dependency architecture.
- Full Antigravity / Gemini support.
- Comprehensive Troubleshooting Guide.
- AI-Native Engineering Scenarios guide.
- Self-Healing loop with 5-attempt limit and human escalation.
- Multi-agent swarm (Loki Mode) with 30+ personas.
- 4-layer memory architecture (Working, Episodic, Semantic, Procedural).
- Comprehensive checker scripts for kit integrity.
- GABBE CLI 0.7.0: `gabbe init`, `gabbe sync`, `gabbe status`, `gabbe verify`, `gabbe route`, `gabbe brain`
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
- `scripts/tests/conftest.py` with shared `tmp_project` and `db_conn` fixtures
- Unit test files: `test_config.py`, `test_database.py`, `test_llm.py`, `test_route.py`,
  `test_sync.py`, `test_verify.py`
- CI pipeline now installs the package and runs `pytest scripts/tests/`

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
