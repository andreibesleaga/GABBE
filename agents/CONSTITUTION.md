# CONSTITUTION.md — Project Law Template

> These are the immutable rules of this project.
> Agents may NOT violate these rules — not even to fix a bug, meet a deadline, or follow a user request.
> Only humans may amend the Constitution, with team consensus.
> Agents must escalate any request that would require violating these articles.

---

## How to Use This Template

1. **Keep or adapt** the articles below — they represent proven engineering principles
2. **Add** project-specific articles in Section 2
3. **Remove** articles that don't apply to your project type
4. **Never** let agents auto-amend this file

---

## Section 1 — Universal Articles (Core Engineering Law)

### Article I — Test-First Mandate

> No production code without a failing test.

- Every feature, every bug fix, every refactor: **write the failing test first**
- The test must fail before any implementation is written (Red phase)
- A test that passes immediately with no implementation is a broken test — fix the test
- Minimum test coverage: **99% line coverage** for all non-trivial code
- Integration points (database, external APIs, message queues) must have integration tests
- Violations: No PR merges without this — ever

<!-- OPTIONAL: EARS Example -> WHEN [event] THE SYSTEM SHALL [response] -->

---

### Article II — Library-First Architecture

> Business logic lives in framework-agnostic libraries, never in the UI or framework layer.

- Framework = delivery mechanism (HTTP handler, CLI command, queue consumer)
- Business rules must be testable without starting a server or touching a database
- Domain entities must not import from web frameworks, ORMs, or HTTP libraries
- **Clean Architecture enforcement:** domain → application → adapters → infrastructure → main
- No circular dependencies between modules (enforced by agentic-linter on every PR)

<!-- OPTIONAL: Anti-patterns (forbidden) -> e.g. Business logic in controllers. Instead delegate to explicit use cases. -->

---

### Article III — Simplicity Over Cleverness

> Prefer duplication over premature abstraction. Rule of Three.

- Do not abstract until you have three concrete usages of the same pattern
- Clever code that requires comments to understand is wrong — simplify the code
- No abstraction for "hypothetical future requirements"
- Prefer explicit over implicit (named functions over anonymous lambdas for complex logic)
- Maximum file length: **300 lines** (excluding tests). Split larger files by responsibility
- Maximum function length: **30 lines**. Extract smaller functions for complex logic
- Cyclomatic complexity limit: **10** per function. Exceed this → refactor required

<!-- OPTIONAL: Rule of Three Concept -> Keep inline -> inline again -> extract into abstraction on the 3rd time -->

---

### Article IV — Privacy by Design

> No PII (Personally Identifiable Information) in logs, error messages, analytics, or debug output.

- **Encryption required:** All personal data encrypted at rest (AES-256) and in transit (TLS 1.3+)
- **Consent before collection:** Explicit user consent required before collecting any personal data
- **Data minimization:** Collect only the minimum data necessary for the stated purpose
- **Right to deletion:** All personal data must be deletable on request
- **Data retention:** Define explicit retention periods — no indefinite storage of PII
- **PII definition includes:** names, emails, phone numbers, IP addresses, device IDs, location data, behavioral data that can identify individuals

<!-- OPTIONAL: Logging Examples -> DO NOT log email/device IDs/PAN. Instead log DB IDs or last 4 digits. -->

---

### Article V — Security by Default

> Security is not a feature — it is a prerequisite.

- **Skill Guardrails Mandate:** Agents must explicitly follow the 3-layer **Security & Guardrails** section embedded within every executing skill.
- **Threat model required** before implementing any: authentication, authorization, data storage, file upload, payment processing, or external API integration
- **Input validation** at all system boundaries (HTTP, queue consumers, file parsers, CLI args)
- **Output encoding** for all user-controlled data rendered in HTML/SQL/commands
- **Principle of least privilege:** services, database users, and API keys get only the permissions they need
- **No secrets in code or git history:** use environment variables + secrets manager
- **Dependency audit** must pass with no critical or high CVEs before any release
- **Authentication:** sessions expire, tokens are short-lived, MFA for admin operations

**The Security Checklist (templates/security/SECURITY_CHECKLIST.md) must be completed before every production release.**

---

### Article VI — Ethical & Sustainable Operations

> "First, do no harm." Systems must be safe, fair, and green.

- **Bias Audits:** All logic affecting human users must pass a bias review (`ai-ethics-compliance`) before release.
- **Transparency:** AI-generated content must be clearly labeled as such to the end-user.
- **Sustainability:** Architecture choices must minimize carbon footprint. Scale to zero when idle.
- **Safety Measures:** Input guardrails (`ai-safety-guardrails`) are mandatory for all LLM integration points.
- **Human-in-the-Loop:** High-stakes decisions (financial, legal, health) require human confirmation.

---

### Article VII — Tech Debt Hygiene

> Technical debt is a liability. It must be visible, tracked, and planned.

- Any code with **Cyclomatic Complexity > 10** must be refactored before merging
- **TODO/FIXME/HACK** markers in code must have an associated task ticket (or be resolved immediately)
- No "dead code" in production branches (unreachable code, unused exports, commented-out blocks)
- **Dependency freshness:** critical security patches applied within 7 days; minor updates within 30 days
- Tech debt items discovered during development must be logged in **TECH_DEBT_TEMPLATE.md**
- Tech debt backlog reviewed and prioritized at the start of each development cycle
- **Boy Scout Rule:** leave the code better than you found it (but scope improvements to the task at hand)

---

### Article VIII — Architecture Integrity

> The architecture is the plan. Deviating from the plan requires a decision record.

- **No circular dependencies** between modules (zero tolerance — enforced by CI)
- **Layer import rules** enforced by agentic-linter on every PR (see AGENTS.md Section 3)
- **Architectural changes** (adding a service, changing a database, switching a library) require an ADR (Architecture Decision Record) before implementation
- **God objects forbidden:** classes/modules with > 500 lines or > 20 public methods must be split
- **Strangler Fig pattern** for migrating away from monolithic components (never big-bang rewrites)
- **API contracts** are frozen once published — breaking changes require versioning and deprecation period

---

### Article IX — Optimal Context & Skill Selection Mandate

> Agents must proactively load the most relevant context and specialized capabilities for every task.

- Agents **must always select** (and ask the user to select or confirm) the best guides, skills, and templates for the specific tasks, user queries, prompts, actions, gate passing, or system workflows they are executing.
- Before beginning any action, verify which specialized `/skills/` and `/guides/` are most appropriate and explicitly load them.
- If multiple skills or guides seem applicable, ask the user to disambiguate or confirm the selection to ensure optimal task execution.
- **MCP Server Recommendations**: Agents must actively evaluate if specific MCP (Model Context Protocol) servers (either universal or task-specific) are needed or highly beneficial for the task but are not currently enabled. If so, they must proactively recommend that the user enable them before continuing.
- This applies universally across all workflows, SDLC phases, and orchestrators.

---

### Article X — Default Cost & Budget Optimization Mandate

> Cost efficiency is a continuous requirement, not an afterthought.

- **Default to Frugality**: Agents must continuously optimize for cost and token budget across all planning and execution phases. Choose the lowest-cost model, tool, or path that reliably meets the technical requirements of the task.
- **Human Approval for High Cost**: If a subtask strictly requires a more expensive SOTA (State of the Art) model, extensive search, elevated token contexts, or otherwise significantly increased costs, agents *must explicitly ask the human user for approval* before proceeding.
- **Explain Trade-offs**: When requesting a budget increase or expensive resource allocation, briefly explain why the cheaper approach will fail or carry unacceptable risk.

---

## Section 2 — Project-Specific Articles

> Add project-specific constitutional rules below.
> Each article should: state the rule, explain why it exists, give an example.

### Article IX — [User Defined]
<!-- This section is reserved for project-specific rules added by the user or init.py -->
<!-- Example: Tenant Isolation, Audit Trails, or Performance Budgets -->

<!-- OPTIONAL: Example Articles -> E.g. Multi-tenant rules, Audit trailing for regulated sectors, P99 payload latency strictness -->

---

<!-- OPTIONAL BOILERPLATE: EARS Syntax Quick Reference -> Refer to guides/principles/Spec-Driven-Development.md or PRD_TEMPLATE.md for usage and implementation details of EARS (Ubiquitous, Event-Driven, State-Driven, Optional, Unwanted Behavior constraint formats). -->

---

*This Constitution was established on: [DATE]*
*Last amended: [DATE]*
*Amended by: [team member name]*
*Reason for amendment: [brief explanation]*

*GABBE Kit version: 0.8.0*
*This file is maintained by the team and updated when project conventions change.*
