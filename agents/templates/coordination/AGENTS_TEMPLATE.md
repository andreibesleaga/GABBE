# AGENTS.md — Universal Agent Configuration Template

> This file is the single source of truth for all AI coding agents on this project.
> Fill in every [PLACEHOLDER] before starting. Agents read this file first.
> Symlinked to: .cursorrules | .claude/CLAUDE.md | .gemini/settings.json | .codex/AGENTS.md

---

## 1. Project Identity

```yaml
project_name: "{{ project_name }}"
description: "{{ description }}"
repo_url: "[PLACEHOLDER: https://github.com/org/repo]"

runtime: "{{ runtime }}"
language: "{{ language }}"
framework: "{{ framework }}"
package_manager: "{{ package_manager }}"

database: "{{ database }}"
orm: "[PLACEHOLDER: Prisma | Eloquent | SQLAlchemy | GORM]"
cache: "[PLACEHOLDER: Redis | Memcached | none]"

deployment_target: "[PLACEHOLDER: Docker/K8s | Vercel | AWS Lambda | VPS]"
ci_cd: "[PLACEHOLDER: GitHub Actions | GitLab CI | CircleCI]"
```

---

## 2. Operational Commands

> These are the EXACT commands agents must use. No approximations.
> Wrong: "run tests". Right: the exact command below.

```bash
# Install dependencies
install: "{{ 'npm install' if package_manager == 'npm' else 'pnpm install' if package_manager == 'pnpm' else 'yarn install' if package_manager == 'yarn' else 'pip install -r requirements.txt' if package_manager == 'pip' else 'go mod download' if package_manager == 'go mod' else 'composer install' }}"

# Start development server
dev: "[PLACEHOLDER: pnpm dev | php artisan serve | python -m uvicorn main:app --reload]"

# Run ALL tests (must pass before any PR)
test: "{{ 'npm test' if package_manager == 'npm' else 'pnpm test' if package_manager == 'pnpm' else 'yarn test' if package_manager == 'yarn' else 'pytest' if package_manager == 'pip' else 'go test ./...' if package_manager == 'go mod' else 'php artisan test' }}"

# Run tests with coverage report
test_coverage: "[PLACEHOLDER: pnpm test --coverage | php artisan test --coverage | pytest --cov]"

# Run specific test file
test_single: "[PLACEHOLDER: pnpm vitest run src/path/to/file.test.ts]"

# Build for production
build: "{{ 'npm run build' if package_manager == 'npm' else 'pnpm build' if package_manager == 'pnpm' else 'yarn build' if package_manager == 'yarn' else 'go build -o app' if package_manager == 'go mod' else 'composer install --no-dev' }}"

# Type checking (must pass before any PR)
typecheck: "[PLACEHOLDER: pnpm tsc --noEmit | phpstan analyse --level=9 | mypy .]"

# Linting (must pass before any PR)
lint: "[PLACEHOLDER: pnpm eslint . | pint | ruff check .]"

# Formatting
format: "[PLACEHOLDER: pnpm prettier --write . | pint | ruff format .]"

# Security scan (dependency audit)
security_scan: "{{ 'npm audit' if package_manager == 'npm' else 'pnpm audit' if package_manager == 'pnpm' else 'yarn audit' if package_manager == 'yarn' else 'pip-audit' if package_manager == 'pip' else 'govulncheck ./...' if package_manager == 'go mod' else 'composer audit' }}"

# Database migrations
migrate: "[PLACEHOLDER: pnpm prisma migrate dev | php artisan migrate | alembic upgrade head]"

# Generate API docs
docs: "[PLACEHOLDER: pnpm typedoc | php artisan scribe:generate]"
```

---

## 3. Architecture Rules

> These rules are enforced by the agentic-linter skill on every PR.
> Violations must be fixed before merging.

### Layer Definitions

```
[PLACEHOLDER — adapt to your architecture pattern]

Example for Clean Architecture (Node.js/TS):
  src/domain/          <- Business entities, domain events, value objects
                          MUST NOT import from: application, adapters, infrastructure
  src/application/     <- Use cases, command/query handlers
                          MUST NOT import from: adapters, infrastructure
  src/adapters/        <- Controllers, presenters, gateways (interface adapters)
                          MUST NOT import from: infrastructure directly (use DI)
  src/infrastructure/  <- Database, external APIs, file system implementations
                          CAN import from: all layers (implements interfaces)
  src/main/            <- Composition root, DI wiring, app bootstrap
                          CAN import from: all layers

Example for Laravel DDD:
  app/Domain/          <- Business logic (models, value objects, domain events)
  app/Application/     <- Actions, DTOs, service interfaces
  app/Infrastructure/  <- Eloquent implementations, external API clients
  app/Http/            <- Controllers (thin -- delegate to Application layer)
```

### Forbidden Patterns

```
# NEVER do these:
- Direct database access from controllers (use use-cases / actions)
- Business logic in views or API response formatters
- Circular imports between any two modules
- Importing framework-specific code in domain layer
- Hardcoded configuration values (use env vars + config files)
- [PLACEHOLDER: add project-specific forbidden patterns]
```

### Directory Purpose Map

```
[PLACEHOLDER: Document what each top-level directory is for]

Example:
  src/           -> Application source code
  tests/         -> All test files (mirrors src/ structure)
  docs/          -> Architecture docs, ADRs, C4 diagrams
  scripts/       -> Dev tooling, DB seeds, migration scripts
  agents/       -> Agent configuration kit (this directory)
  infra/         -> Docker, CI/CD, Terraform, K8s configs
```

---

## 4. Code Style & Patterns

```
Naming conventions:
  Files:        [PLACEHOLDER: kebab-case.ts | PascalCase.php | snake_case.py]
  Classes:      PascalCase
  Functions:    camelCase (JS/TS) | snake_case (Python/PHP)
  Constants:    SCREAMING_SNAKE_CASE
  Types/Interfaces: PascalCase, prefix I for interfaces if using that convention

Functional vs OOP:
  [PLACEHOLDER: "Prefer functional pure functions" or "Use classes for domain entities"]

Error handling:
  [PLACEHOLDER: "Use Result<T, E> type pattern" or "Throw typed domain errors" or "Use Laravel's Handler"]

State management:
  [PLACEHOLDER: "No global mutable state" or "Redux/Zustand for frontend state"]

API response format:
  [PLACEHOLDER: Document your standard response envelope, e.g. { data, meta, errors }]

Import style:
  [PLACEHOLDER: "Absolute imports using @/ alias" or "Relative imports only"]
```

---

## 5. Workflow for Agents — Review-Driven Development

Agents MUST follow this order; skipping steps is forbidden. Keep `agents/memory/` current at
every task (episodic, semantic, AUDIT_LOG, CONTINUITY, PROJECT_STATE, RESUME_POINTER), and consult
`agents/{skills,guides,templates}/` for relevant capabilities at each step.

**CRITICAL MANDATES (always apply):**

- **Optimal skill/guide/MCP selection** — analyze the task and select (or ask the user to confirm) the best skills/guides/templates; never default to generic execution when a specialized one exists. Recommend enabling any MCP server that would materially help.
- **Cost & budget by default** — minimize tokens/context/API cost; never use swarms or SOTA models for simple work, and **ask the human before any expensive/SOTA/high-cost approach** (with a one-line cost-benefit). Four levers (`guides/ops/cost-optimization.md`): prompt caching (stable context first), context budgeting (load minimum, prefer `context_cost: low`), model tiering (`gabbe route`), batching. Never weaken the gates, the SDLC phases, or HITL to save cost.
- **Spec-driven (first-class)** — `spec → evals → test → code`, never code-first. Non-trivial features start from an **EARS** spec (`product/spec-writer.skill`, `templates/product/SPEC_TEMPLATE.md`, `guides/planning/product-requirements.md`); keep a **golden thread** (requirement → spec → test → code → audit). No requirement without a test (Article I); resolve ambiguity in the spec via `clarify.skill`.
- **Observability (first-class)** — every run/decision/model+tool call is traced with token usage + **per-step cost attribution** (`core/audit-trail.skill`, `core/agent-analytics.skill`; OTel GenAI conventions `gen_ai.usage.*`; span tree root→plan→discover→execute→retrieve). Redact content by default (Article IV); `AUDIT_LOG.md` is authoritative without the CLI.
- **Human–agent collaboration (manager, not operator)** — the human delegates → observes → intervenes on exceptions. Keep three questions always answerable: **Purpose** (scope/non-goals via spec), **Transparency** (legible reasoning/tools/cost via observability), **Control** (pause/correct/approve via HITL). Prefer an async, observable surface; "done" only when all three hold (`guides/principles/human-agent-collaboration.md`).

### Step 0 — Preflight & Clarify (before anything else)

```
Run preflight.skill as the FIRST action of every session and every major task:
  1. Auto-checks: integrity-check (fast) → confirm memory + working tree are coherent.
  2. Load index SUMMARIES (not bodies): agents/{skills,guides,templates,personas}/00-index.md
     → know what capabilities exist before choosing generically.
  3. Load memory headers with decay-aware priming (PROJECT_STATE, CONTINUITY, latest snapshot).
  4. Surface cost posture: GABBE_AUTONOMY (ask|auto|hybrid, default hybrid) + remaining budget.
  5. Recommend the OPTIMAL set for the task (skills/guides/persona/MCP), ranked by
     relevance × (1/context_cost); pick a reasoning pattern proportionate to task + budget.
  6. Flag new/changed capabilities since last preflight (defer adoption to update-scan.skill).
  7. End by invoking clarify.skill → ask the focused batch of clarifying questions
     (and "questions you should ask me") before proceeding.
Do not begin implementation until blocking questions are answered, unless the autonomy
posture is `auto` AND the task is cheap AND reversible.
```

### Step 1 — Load Context (every session start)

```
1. Read this AGENTS.md completely
2. Read CONSTITUTION.md if it exists
3. If agents/memory/PROJECT_STATE.md exists: read it (understand current SDLC phase)
4. If agents/memory/CONTINUITY.md exists: read it (understand past failures to avoid)
5. Read the relevant task from project/TASKS.md (if project/TASKS.md exists)
```

### Step 2 — Plan Before Coding

```
Before touching any file, write a brief implementation plan:
  - What files will you create or modify?
  - What is the expected behavior change?
  - What tests will you write?
  - Does this change affect any architecture boundaries?
  - Are there any knowledge gaps? (If yes -> invoke knowledge-gap.skill)

For complex tasks: write plan.md or use PLAN_TEMPLATE.md
```

### Step 3 — Test First (TDD Red Phase)

```
Write the failing test BEFORE writing implementation code.
Run the test -- it MUST fail (Red).
If the test passes immediately with no implementation: the test is WRONG. Fix it.
```

### Step 4 — Implement (TDD Green Phase)

```
Write the minimal code to make the failing test pass.
Do not add features not covered by a failing test.
```

### Step 5 — Verify (must all pass before marking done)

```
Run: [test command] -> must pass
Run: [typecheck command] -> must pass
Run: [lint command] -> must pass
Run: agentic-linter check -> no boundary violations
```

### Step 6 — Refactor

```
Improve code quality while keeping all tests green.
Check: Cyclomatic complexity < 10, no code duplication > 3 occurrences, no dead code.
```

### Step 7 — Log & Complete

```
Write entry to agents/memory/AUDIT_LOG.md
Update task status in project/TASKS.md to DONE
Refresh agents/memory/RESUME_POINTER.md (state-preserve.skill) — keep the
  "next action" current so any future session resumes losslessly
If this completes a SDLC phase: invoke sdlc-checkpoint.skill
```

> **State preservation is continuous, not just at Step 7.** Per `state-preserve.skill`
> and §13, save incrementally after every meaningful step and flush a full snapshot
> before budget/time runs out — assume a cutoff can happen at any moment.

---

## 6. Governance & Security

### 🛡️ Mandatory Security & Guardrails

Agents MUST adhere to the **Security & Guardrails** section appended to the bottom of whatever skill they are currently executing. Bypassing these skill-specific guardrails is strictly forbidden.

### Forbidden Actions (agents must never do these without explicit human approval)

```
- Commit .env files or any file containing secrets
- Push directly to main/master branch
- Change CI/CD pipeline configuration
- Modify CONSTITUTION.md
- Switch to a different library/framework than what's defined in Project Identity
- Make breaking API changes
- Add new environment variables without documenting them
- Disable or modify linting/testing rules
- Grant elevated permissions or bypass authentication
- [PLACEHOLDER: add project-specific forbidden actions]
```

### Secrets Policy

```
All secrets MUST be in environment variables.
Local dev: .env file (always in .gitignore)
CI/CD: GitHub Secrets / GitLab CI Variables / AWS Secrets Manager
Never hardcode API keys, passwords, tokens, or connection strings.
Use: [PLACEHOLDER: dotenv | .env.vault | AWS Secrets Manager | HashiCorp Vault]
```

### PR Format (Conventional Commits)

```
Format: <type>(<scope>): <subject>

Types: feat | fix | docs | style | refactor | test | chore | perf | sec | deps
Scope: module or layer name (optional)

Examples:
  feat(auth): add OAuth2 Google login
  fix(api): resolve N+1 query in users endpoint
  sec(deps): update lodash to fix CVE-2024-xxxxx
  test(domain): add unit tests for Order aggregate
  refactor(application): extract CreateOrderUseCase from controller

PR body must include:
  - What changed and why
  - Test coverage for the change
  - Breaking changes (if any)
  - Security implications (if any)
```

### Quality Gates (all must pass before PR merges)

```
Gate 1 -- Syntax/Linting:    ESLint / PHP-CS-Fixer / Prettier / Ruff -- zero errors
Gate 2 -- Type Safety:       tsc --noEmit / PHPStan L9 / mypy -- zero errors
Gate 3 -- Test Coverage:     >= 99% coverage, all tests passing, no skipped tests
Gate 4 -- Integration:       Docker Compose up, API contract validation
Gate 5 -- Security scan:     npm audit / composer audit -- no critical or high CVEs
Gate 6 -- Complexity:        Cyclomatic complexity < 10 on modified files
Gate 7 -- EARS Compliance:   (for new features) All requirements have tests
```

---

## 7. Research Policy

Agents must use authoritative sources. Never guess or hallucinate.

### Source Tiers (in order of trust)

```
Tier 1 (Primary -- always prefer):
  - Official language/framework docs (MDN, nodejs.org, laravel.com, docs.python.org)
  - Official specifications (RFC.editor.org, W3C, ECMA, ISO)
  - Security standards (OWASP, NIST, CIS, CVE.mitre.org)

Tier 2 (Academic/Official repos):
  - arXiv.org, IEEE Xplore, ACM Digital Library
  - GitHub official organization repos
  - Official changelog/release notes

Tier 3 (Verified industry, as fallback):
  - Anthropic docs, AWS docs, Google Cloud docs, Microsoft Docs

NOT acceptable (never cite as authoritative):
  - Blog posts, Medium articles, Reddit, StackOverflow opinions
  - Any source without official attribution
```

### Research Gate -- mandatory before:

```
- Using any library not in existing package.json / composer.json
- Calling any API method not confirmed in official docs
- Implementing any security mechanism or cryptographic approach
- Interpreting any regulatory requirement (GDPR, OWASP, HIPAA)
```

### When to invoke research.skill

```
"I'm not sure about X" -> knowledge-gap.skill -> research.skill -> confirm before coding
If library version not found in official docs -> do NOT assume behavior -> report to human
Use Context-7 MCP for library docs (prevents hallucinated deprecated API usage)
```

---

## 8. Self-Healing Policy

Agents may autonomously fix failures up to 5 attempts.

### What agents may self-heal (no human approval needed):

```
- Type errors and lint errors
- Test assertion updates when spec changed
- Deprecated API calls (found via Context-7 MCP)
- Dependency version bumps (patch/minor versions only)
- Import path corrections
- Formatting and code style issues
```

### What requires human decision:

```
- Architecture or library changes
- Breaking API changes (any consumer affected)
- Security-affecting changes (auth, permissions, encryption)
- Major version dependency bumps
- Any modification to CONSTITUTION.md
- Any change to CI/CD pipelines
- Any change that removes or weakens a security control
```

### Self-Heal Escalation Protocol

After 5 failed attempts, agent MUST:

```
1. STOP all autonomous action
2. Create structured escalation report:
   - Error description
   - All 5 attempts made and their outcomes
   - Research findings
   - Recommended human decision
3. Write to AUDIT_LOG.md
4. Wait for human response before continuing
```

### Self-Evolving Policy (within cost + permission bounds)

The system may keep itself current and improve (new/better skills, tools, MCPs, models) via
`update-scan.skill` — but only inside hard bounds (full detail in that skill):

- **Allowed** (gated by `GABBE_AUTONOMY` + budget): adopt a cheaper/better reversible+validated tool/model; import a vetted external skill (validated first); refine prompts/personas from **successful** trajectories only.
- **Always needs human approval** (even under `auto`): anything expensive/SOTA/irreversible, externally-sourced runnable code, or any change to protected files.
- **Guardrails:** misaligned-replay guard (never learn from failed runs); protected files (never auto-edit build/IaC/CI/dependency manifests outside the self-heal allowlist); policy-as-code self-enforcement with every adoption/rejection logged to `AUDIT_LOG.md`; prefer canary + rollback, version evolved components.

---

## 9. Human-in-the-Loop Triggers

The agent MUST stop and ask the human when encountering:

```
ALWAYS pause and ask:
  - Any breaking change to a public API
  - Ambiguous requirements (multiple valid interpretations)
  - Security trade-offs (convenience vs security)
  - Budget or scope changes
  - Regulatory requirement interpretation (GDPR, HIPAA, etc.)
  - Architectural change (new service, new database, library switch)
  - Any discovered vulnerability that requires feature disablement
  - "I've tried 5 times and cannot fix this" (see Self-Healing Policy)
  - Any expensive / SOTA-model / irreversible action — even under GABBE_AUTONOMY=auto
  - Adopting a new tool, model, or externally-sourced skill (see update-scan / skills-registry)
  - [PLACEHOLDER: add project-specific escalation triggers]

Format for human escalation:
  ESCALATION REQUIRED
  Issue: [clear description]
  Options considered:
    1. [option A] -- pros: [...] cons: [...]
    2. [option B] -- pros: [...] cons: [...]
  Recommendation: [option X because Y]
  Awaiting: [specific decision needed]
```

**Clarify at every major step (not just at session start).** Per `clarify.skill`, the agent
estimates its own uncertainty before each major step and asks a focused batch of clarifying
questions (≈3–6, highest-impact first) whenever interpretation is ambiguous, a decision input is
missing, retrieval/verification failed, or the action is expensive/irreversible. The amount of
questioning scales with the `GABBE_AUTONOMY` posture (ask → clarify freely; hybrid → clarify on
real ambiguity; auto → silent for cheap/reversible work but always pause for the cases above).
Record assumed defaults in `agents/memory/AUDIT_LOG.md` so silence is informed, not a guess.

---

## 10. Tool-Specific Overrides

### Claude Code (claude.ai/code, Claude Code CLI)

```
- Skills: Use slash commands matching skill names (e.g., /tdd-cycle, /code-review)
- Memory: Use TodoWrite tool for task tracking
- Hooks: Check .claude/settings.json for hook configuration
- Context: This AGENTS.md is symlinked to .claude/CLAUDE.md
```

### Cursor

```
- Context: This AGENTS.md is symlinked to .cursorrules
- Skills: Reference skill files directly in conversation
- Agent mode: @workspace for codebase-wide context
```

### GitHub Copilot

```
- Context: Instructions from .github/copilot-instructions.md (symlinked)
- Skills: Reference skills/ directory files in comments or conversation
```

### Antigravity / Gemini CLI

```
- Context: This AGENTS.md is symlinked to .gemini/settings.json (instructions field)
- Skills: Symlinked to .agent/skills/ -- invoke by trigger keywords
- MCP: Configure .gemini/mcp_config.json using templates/core/MCP_CONFIG_TEMPLATE.json
```

---

## 11. Monorepo Support

For monorepos, this root AGENTS.md applies globally.
Package-level AGENTS.md files override root for that package's scope.

```
monorepo-root/
  AGENTS.md              <- Root: global rules (this file)
  packages/
    web-app/
      AGENTS.md          <- Override: web-specific rules (React, Tailwind, etc.)
    api-service/
      AGENTS.md          <- Override: API-specific rules (Fastify, Prisma, etc.)
    shared-lib/
      AGENTS.md          <- Override: Library-specific rules (no framework imports)
```

Agent context priority: Package AGENTS.md > Root AGENTS.md

---

## 12. References

**Discover skills via the index — `agents/skills/00-index.md` is the canonical catalog**: native
skill menus (e.g. Claude Code) may truncate large collections by token budget, so always consult
the index to find any skill, then read its full file before use. Per-tool skill locations: see §10.

**Skill access (search first, read before use):**

- **Search First**: Before coding, search for relevant skills:
    - **Cursor**: Check `.cursor/rules/` for `.mdc` files.
    - **VS Code / Copilot**: Check `.github/skills/` or invoke via slash command.
    - **Claude Code**: Use `/skill-name` or check `.claude/skills/`.
    - **Gemini**: Skills are auto-loaded from `agents/skills`.
- **Read Instructions**: Read the full content of the skill file (e.g., `tdd-cycle.skill.md` or `tdd-cycle.mdc`) before use.

```
Project law:          agents/CONSTITUTION.md
Skills (canonical):   agents/skills/00-index.md   (master: agents/skills/**)
Guides:               agents/guides/00-index.md
Templates:            agents/templates/00-index.md
Personas (Loki):      agents/personas/00-index.md
Brain patterns:       agents/skills/brain/README.md
Quick reference:      docs/QUICK_GUIDE.md
Project memory:       agents/memory/PROJECT_STATE.md
Past failures:        agents/memory/CONTINUITY.md
Decision log:         agents/memory/AUDIT_LOG.md
```

- **Skills**: `agents/skills/` (Master) → `.cursor/rules/` (*.mdc) | `.github/skills/` | `.claude/skills/`
- **Memory**: `agents/memory/`

---

## 13. Session & Continuity

Every session, agents MUST:

```
START of session:
  1. Read this AGENTS.md
  2. Read agents/memory/RESUME_POINTER.md (the lifeline — current task + NEXT ACTION)
  3. Read agents/memory/PROJECT_STATE.md (if exists) -> understand current state
  4. Read agents/memory/CONTINUITY.md (if exists) -> understand past failures
  5. Load latest agents/memory/episodic/SESSION_SNAPSHOT/ (if exists)
  6. If resuming: use session-resume.skill for full recovery
  7. Run integrity-check.skill before starting new work on existing code

CONTINUOUSLY — never lose progress (state-preserve.skill; assume a cutoff at any moment):
  - After each meaningful step: refresh RESUME_POINTER.md (current task + precise NEXT ACTION)
    and append the outcome to AUDIT_LOG.md.
  - Pre-exhaustion flush: when budget/tokens/turns run low or before a long/irreversible action,
    write a FULL snapshot FIRST (RESUME_POINTER, then snapshot/PROJECT_STATE/CONTINUITY).
  - On-disk Markdown memory must always suffice for a fresh agent to resume losslessly.

PORTABLE — switch coding agent or LLM anytime (state-portability.skill):
  DEHYDRATE (state_export.sh → STATE_HANDOFF.md + a lossless bundle) and HYDRATE in the
  destination agent (state_import.sh), then run session-resume + preflight. Memory + instructions
  + state are a fully compatible export/import. Never export secrets; merge (don't clobber) on import.

END of session:
  1. Update project/TASKS.md with current status of all in-progress tasks
  2. Write session summary to agents/memory/episodic/ (DECISION_LOG_TEMPLATE.md)
  3. Update agents/memory/PROJECT_STATE.md with current SDLC phase
  4. Write all decisions/outcomes to agents/memory/AUDIT_LOG.md
  5. Update agents/memory/CONTINUITY.md with lessons learned
  6. Create SDLC checkpoint if a phase was completed
  7. If stopping mid-task: note exactly where you stopped and why (RESUME_POINTER)
```

---

## 14. Project-Specific Rules

```
[PLACEHOLDER: Add any additional project-specific rules, constraints, or context here.]

Examples:
  - "This project uses feature flags via LaunchDarkly -- never delete flags, only disable"
  - "API is consumed by mobile clients -- breaking changes require a 30-day deprecation period"
  - "All user-facing text must be in the i18n system -- no hardcoded strings"
  - "Analytics events must be documented in docs/analytics-schema.md before implementation"
  - "Database schema changes must be reviewed by the DBA team before migration"
```

---

<!-- GABBE_CLI_START -->
## GABBE CLI Workflows

> **Full reference**: See `agents/guides/ops/gabbe-cli-workflows.md`
>
> **This section is optional.** The GABBE CLI provides platform controls (budget, audit, replay, escalation) but is not required. Agents can operate purely via markdown inference without it.

| Command | Purpose |
|---|---|
| `gabbe init` | Initialize DB |
| `gabbe sync` | Sync `project/TASKS.md` ↔ SQLite |
| `gabbe status` | Project dashboard |
| `gabbe verify` | Integrity checks |
| `gabbe route "<prompt>"` | LOCAL or REMOTE routing |
| `gabbe brain activate` | Active Inference Loop |
| `gabbe brain evolve --skill <name>` | EPO optimization |
| `gabbe brain heal` | Self-healing watchdog |
| `gabbe forecast` | Cost/token forecast |
| `gabbe serve-mcp` | MCP JSON-RPC server |
| `gabbe runs` | List agent runs |
| `gabbe audit <run-id>` | Audit trace |
| `gabbe replay <run-id>` | Replay from checkpoints |
| `gabbe resume <run-id>` | Resume paused runs |

**Workflow**: `gabbe init → gabbe sync → gabbe status → gabbe verify → gabbe brain activate → gabbe forecast → gabbe runs → gabbe audit`
<!-- GABBE_CLI_END -->

---

## Loki & Brain — Agentic Orchestration

Two optional orchestration modes (both run purely via Markdown inference; the `gabbe`
CLI is optional). Full definitions live in the skills — this is only a pointer (avoid
restating them here, to prevent drift):

- **🧠 Brain Mode** (`brain/brain-mode.skill.md`) — the Strategist (System 2): meta-cognitive
  planner/router/optimizer (Active Inference framing + dynamic cost routing). Trigger: `gabbe brain activate`, `supermode`.
- **⚡ Loki Mode** (`brain/loki-mode.skill.md`) — the Executor (System 1): the deterministic
  SDLC lifecycle (S00→S13, 14 phases) with human-in-the-loop hard gates at S00 (GO/NO-GO),
  S01, S02, S07, S08. Trigger: `loki`, `orchestrate`.

Brain Mode **wraps** Loki: it receives the request, routes by complexity/budget, runs Loki for
the SDLC, and monitors — intervening if cost spikes, errors loop, or requirements drift. Both use
the same operating spine in §5/§13 (preflight → clarify → act → state-preserve → final-review).

---

*Last updated: [DATE]*
*GABBE Kit version: 1.1.0*
*This file is maintained by the team and updated when project conventions change.*
