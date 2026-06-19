# AGENTS.md — Universal Agent Configuration Template

> This file is the single source of truth for all AI coding agents on this project.
> Fill in every [PLACEHOLDER] before starting. Agents read this file first.
> Symlinked to: .cursorrules | .claude/CLAUDE.md | .gemini/settings.json | .codex/AGENTS.md

---

## 1. Project Identity (REQUIRED VARIABLES)
>
> **ACTION REQUIRED**: Replace all `[PLACEHOLDER: ...]` values below with your specific stack.

```yaml
project_name: "[PLACEHOLDER: My Project]"
description: "[PLACEHOLDER: One sentence about what this project does]"
repo_url: "[PLACEHOLDER: https://github.com/org/repo]"

runtime: "[PLACEHOLDER: Node.js 22 | PHP 8.3 | Python 3.12 | Go 1.22]"
language: "[PLACEHOLDER: TypeScript 5.x | PHP | Python | Go]"
framework: "[PLACEHOLDER: Fastify | Laravel | FastAPI | Gin]"
package_manager: "[PLACEHOLDER: pnpm | npm | yarn | composer | pip | go mod]"

database: "[PLACEHOLDER: PostgreSQL 16 | MySQL 8 | MongoDB 7 | SQLite]"
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
install: "[PLACEHOLDER: pnpm install | composer install | pip install -r requirements.txt]"

# Start development server
dev: "[PLACEHOLDER: pnpm dev | php artisan serve | python -m uvicorn main:app --reload]"

# Run ALL tests (must pass before any PR)
test: "[PLACEHOLDER: pnpm test | php artisan test | pytest | go test ./...]"

# Run tests with coverage report
test_coverage: "[PLACEHOLDER: pnpm test --coverage | php artisan test --coverage | pytest --cov]"

# Run specific test file
test_single: "[PLACEHOLDER: pnpm vitest run src/path/to/file.test.ts]"

# Build for production
build: "[PLACEHOLDER: pnpm build | composer install --no-dev | go build ./...]"

# Type checking (must pass before any PR)
typecheck: "[PLACEHOLDER: pnpm tsc --noEmit | phpstan analyse --level=9 | mypy .]"

# Linting (must pass before any PR)
lint: "[PLACEHOLDER: pnpm eslint . | pint | ruff check .]"

# Formatting
format: "[PLACEHOLDER: pnpm prettier --write . | pint | ruff format .]"

# Security scan (dependency audit)
security_scan: "[PLACEHOLDER: pnpm audit | composer audit | pip-audit | snyk test]"

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

<!-- OPTIONAL: Architecture Examples -> Document layer mappings (e.g., Domain -> Application -> Adapters -> Infrastructure) -->
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

<!-- OPTIONAL: Directory Map Example -> e.g., src/ -> src code, tests/ -> test suites, docs/ -> Architectural info -->
```

---

## 4. Code Style & Patterns

<!-- OPTIONAL: Code Style Specifics -> Document naming conventions, OOP vs Functional, Error handling, State management, API response format, Import styles -->
---

## 5. Workflow for Agents — Review-Driven Development

Agents MUST follow this order; skipping steps is forbidden. Keep `agents/memory/` current at
every task (episodic, semantic, AUDIT_LOG, CONTINUITY, PROJECT_STATE, RESUME_POINTER), and consult
`agents/{skills,guides,templates}/` for relevant capabilities at each step.

**CRITICAL MANDATES (always apply):**

- **Optimal skill/guide/MCP selection** — analyze the task and select (or ask the user to confirm) the best skills/guides/templates; never default to generic execution when a specialized one exists. Recommend enabling any MCP server that would materially help.
- **Cost & budget by default** — minimize tokens/context/API cost; never use swarms or SOTA models for simple work, and **ask the human before any expensive/SOTA/high-cost approach** (with a one-line cost-benefit). Four levers (`guides/ops/cost-optimization.md`): prompt caching (stable context first), context budgeting (load minimum, prefer `context_cost: low`), model tiering (`gabbe route`), batching. Never weaken the gates, the 10-phase SDLC, or HITL to save cost.
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
3. Read the relevant task from project/TASKS.md (if project/TASKS.md exists)
4. If agents/memory/PROJECT_STATE.md exists: read it (understand current SDLC phase)
5. If agents/memory/CONTINUITY.md exists: read it (understand past failures to avoid)
```

### Step 2 — Plan Before Coding

```
Before touching any file, write a brief implementation plan.

  - What files will you create or modify?
  - What is the expected behavior change?
  - What tests will you write?
  - Does this change affect any architecture boundaries?
  - Are there any knowledge gaps? (If yes -> invoke knowledge-gap.skill)
For complex tasks: write PLAN.md or use PLAN_TEMPLATE.md

```

### Step 3 — Test First (TDD Red Phase)

```
Write the failing test BEFORE writing implementation code.
<!-- OPTIONAL: Detailed TDD Red -> The test MUST fail (Red). Do not implement features not covered by a test -->
```

### Step 4 — Implement (TDD Green Phase)

```
Write the minimal code to make the failing test pass.
<!-- OPTIONAL: Detailed TDD Green -> Do not add features not covered by a failing test -->
```

### Step 5 — Verify (must all pass before marking done)

```
Run: [test command] -> must pass
Run: [typecheck command] -> must pass
Run: [lint command] -> must pass
<!-- OPTIONAL: Deep Verification -> E.g. Run agentic-linter to enforce boundaries -->
```

### Step 6 — Refactor

```
Improve code quality while keeping all tests green.
<!-- OPTIONAL: Refactoring Metrics -> E.g. Complexity < 10, no duplication > 3 -->
```

### Step 7 — Log & Complete

```
Write entry to agents/memory/AUDIT_LOG.md
Update task status in project/TASKS.md to DONE
Refresh agents/memory/RESUME_POINTER.md (state-preserve.skill) — keep the
  "next action" current so any future session resumes losslessly
<!-- OPTIONAL: High-Level Orchestration -> E.g. sdlc-checkpoint.skill -> mark phase done -->
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

<!-- OPTIONAL: Commit Examples -> e.g. feat(auth): add OAuth2 login -->

PR body must include:
  - What changed and why
  - Test coverage for the change
  - Breaking changes (if any)
  - Security implications (if any)
```

### Quality Gates (all must pass before PR merges)

```
<!-- OPTIONAL: Quality Gates Specifics -> Document testing, linting, code coverage >99%, CI integration gates -->
```

---

## 7. Research Policy

Agents must use authoritative sources. Never guess or hallucinate.

### Source Tiers (in order of trust)

```
<!-- OPTIONAL: Source Tiers -> Tier 1: Official docs/Specs. Tier 2: Academic. Tier 3: Verified blogs. Avoid: Reddit/SO. -->
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

<!-- OPTIONAL: Escalation Format -> Detail issue, options considered, and recommendation -->
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

### Gemini CLI

```
- Context: This AGENTS.md is symlinked to .gemini/settings.json (instructions field) + GEMINI.md
- Skills: Symlinked to .agent/skills/ -- invoke by trigger keywords
- MCP: Configure .gemini/mcp_config.json using templates/core/MCP_CONFIG_TEMPLATE.json
```

### Google Antigravity

```
- Context: Reads the root AGENTS.md (priority AGENTS.md → GEMINI.md → defaults, v1.20.3+)
- Skills: Emitted to .agents/skills/<slug>/SKILL.md (agentskills.io standard)
- Models: Picks up CLAUDE.md when running a Claude model — same project context
```

### OpenCode (local-first)

```
- Context: Reads the root AGENTS.md + an opencode.json `instructions` array
- Skills: Emitted to .agents/skills/<slug>/SKILL.md (agentskills.io standard)
```

### Zed / Continue / Roo Code / Kilo Code

```
- Context: Read the root AGENTS.md (agents.md standard); Zed also via .rules,
  Continue via .continue/rules/, Roo via .roo/rules/, Kilo via .kilocode/rules/
- Skills: Reference agents/skills/ directly, or the universal .agents/skills/ tree
```

---

## 11. Monorepo Support

For monorepos, this root AGENTS.md applies globally.
Package-level AGENTS.md files override root for that package's scope.

```
<!-- OPTIONAL: Monorepo Setup Example -> Add AGENTS.md per package to override root settings -->
```

Agent context priority: Package AGENTS.md > Root AGENTS.md

---

## 12. References

**Discover skills via the index — `agents/skills/00-index.md` is the canonical catalog**: native
skill menus (e.g. Claude Code) may truncate large collections by token budget, so always consult
the index to find any skill, then read its full file before use. Per-tool skill locations: see §10.

```
Project law:          agents/CONSTITUTION.md
Skills (canonical):   agents/skills/00-index.md   (master: agents/skills/**)
Guides:               agents/guides/00-index.md
Templates:            agents/templates/00-index.md
Personas (Loki):      agents/personas/00-index.md (36 roles)
Brain patterns:       agents/skills/brain/README.md
Quick reference:      docs/QUICK_GUIDE.md
Project memory:       agents/memory/{PROJECT_STATE,CONTINUITY,AUDIT_LOG,RESUME_POINTER}.md
```

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

<!-- OPTIONAL: Examples -> e.g. "API consumed by mobile, 30-day deprecation", "no hardcoded i18n strings" -->
```

### Per-project policy: `project/gabbe.config.json` (optional)

A runtime-agnostic policy file the agent reads to tune itself to this project —
autonomy posture, budgets, model tiers, enabled MCPs, skill registries, and
protected files. Copy `docs/gabbe.config.example.json` to
`project/gabbe.config.json` and edit. The agent
applies it via `coordination/self-optimize.skill`; the optional `gabbe` CLI
surfaces it via `gabbe/config.py` (`GABBE_AUTONOMY`, `GABBE_PROJECT_CONFIG`).
Precedence for autonomy: env `GABBE_AUTONOMY` > config `autonomy` > `hybrid`.
See `docs/SCHEMA.md` → *Project policy config*.

---

# GABBE CLI Workflows (Optional)

> **Complete reference**: See `agents/guides/ops/gabbe-cli-workflows.md` for full details.
>
> **This section is optional.** The GABBE CLI provides platform controls (budget, audit, replay, escalation) but is NOT required. Agents can fully operate via markdown inference without it.

### Core CLI Integration

See `agents/guides/ops/gabbe-cli-workflows.md` for standard CLI workflows: Init, Sync, Verify, Status, Route, Forecast, and Brain execution controls. (Note: The GABBE CLI is an optional experimental tool; agents can fully rely on markdown inference execution otherwise).

---

# Loki & Brain — Agentic Orchestration

Two optional orchestration modes (both run purely via Markdown inference; the `gabbe`
CLI is optional). Full definitions live in the skills — this is only a pointer (avoid
restating them here, to prevent drift):

- **🧠 Brain Mode** (`brain/brain-mode.skill.md`) — the Strategist (System 2): meta-cognitive
  planner/router/optimizer (Active Inference + dynamic cost routing). Trigger: `gabbe brain activate`, `supermode`.
- **⚡ Loki Mode** (`brain/loki-mode.skill.md`) — the Executor (System 1): the deterministic
  10-phase SDLC (S01→S10) with human-in-the-loop gates. Trigger: `loki`, `orchestrate`.

Brain Mode **wraps** Loki: it receives the request, routes by complexity/budget, runs Loki for
the SDLC, and monitors — intervening if cost spikes, errors loop, or requirements drift. Both use
the same operating spine in §5/§13 (preflight → clarify → act → state-preserve → final-review).

---

*Last updated: [DATE]*
*GABBE Kit version: 1.1.0*
*This file is maintained by the team and updated when project conventions change.*

---
