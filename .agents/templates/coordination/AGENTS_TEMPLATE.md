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

---

## 4. Code Style & Patterns

```
Naming conventions:
  Files:        [PLACEHOLDER: kebab-case.ts | PascalCase.php | snake_case.py]
  Classes:      PascalCase
  Functions:    camelCase (JS/TS) | snake_case (Python/PHP)
  Constants:    SCREAMING_SNAKE_CASE
  Types/Interfaces: PascalCase

Functional vs OOP:
  [PLACEHOLDER: "Prefer functional pure functions" or "Use classes for domain entities"]

Error handling:
  [PLACEHOLDER: "Use Result<T, E> type pattern" or "Throw typed domain errors"]

State management:
  [PLACEHOLDER: "No global mutable state" or "Redux/Zustand for frontend state"]

API response format:
  [PLACEHOLDER: Document your standard response envelope, e.g. { data, meta, errors }]

Import style:
  [PLACEHOLDER: "Absolute imports using @/ alias" or "Relative imports only"]
```

---

## 5. Workflow for Agents — Review-Driven Development

Agents MUST follow this order. Skipping steps is forbidden.

### Step 1 — Load Context (every session start)
```
1. Read this AGENTS.md completely
2. Read CONSTITUTION.md if it exists
3. If loki/memory/PROJECT_STATE.md exists: read it (understand current SDLC phase)
4. If loki/memory/CONTINUITY.md exists: read it (understand past failures to avoid)
5. Read the relevant task from tasks.md (if tasks.md exists)
```

### Step 2 — Plan Before Coding
```
Before touching any file, write a brief implementation plan:
  - What files will you create or modify?
  - What is the expected behavior change?
  - What tests will you write?
  - Does this change affect any architecture boundaries?
  - Are there any knowledge gaps? (If yes -> invoke knowledge-gap.skill)
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
Write entry to loki/memory/AUDIT_LOG.md
Update task status in tasks.md to DONE
If this completes a SDLC phase: invoke sdlc-checkpoint.skill
```

---

## 6. Governance & Security

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
```

### Secrets Policy
```
All secrets MUST be in environment variables.
Local dev: .env file (always in .gitignore)
CI/CD: GitHub Secrets / GitLab CI Variables / AWS Secrets Manager
Never hardcode API keys, passwords, tokens, or connection strings.
```

---

## 7. Research & Self-Healing

### Research Policy
-   **Tier 1 Sources**: Official docs (MDN, docs.python.org, aws.amazon.com).
-   **Tier 2 Sources**: GitHub official repos, verified academic papers.
-   **Forbidden**: Blogs, Reddit, StackOverflow opinions (unless verified).

### Self-Heal Policy
-   Agents may fix types, lint errors, and minor bugs autonomously (max 5 attempts).
-   Escalate to human if: Architecture change, Security change, or Ambiguous requirement.

---

*Generated by Init Wizard on [DATE]*
