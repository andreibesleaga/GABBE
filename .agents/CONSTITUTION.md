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
- Minimum test coverage: **96% line coverage** for all non-trivial code
- Integration points (database, external APIs, message queues) must have integration tests
- Violations: No PR merges without this — ever

**EARS Example:**
```
WHEN a user submits an invalid email address
THE SYSTEM SHALL return HTTP 422 with field-level validation errors
```
The test for this requirement is written before the validation code.

---

### Article II — Library-First Architecture

> Business logic lives in framework-agnostic libraries, never in the UI or framework layer.

- Framework = delivery mechanism (HTTP handler, CLI command, queue consumer)
- Business rules must be testable without starting a server or touching a database
- Domain entities must not import from web frameworks, ORMs, or HTTP libraries
- **Clean Architecture enforcement:** domain → application → adapters → infrastructure → main
- No circular dependencies between modules (enforced by agentic-linter on every PR)

**Anti-patterns (forbidden):**
```
// WRONG: Business logic in controller
app.post('/orders', async (req, res) => {
  if (req.body.total > 10000) {  // <- business rule in controller layer
    await sendFraudAlert(req.body); // <- side effect in controller
  }
  // ...
});

// RIGHT: Controller delegates to use case
app.post('/orders', async (req, res) => {
  const result = await createOrderUseCase.execute(req.body);
  res.json(result);
});
```

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

**Rule of Three:**
```
// First time: write the code inline
// Second time: write it inline again (don't abstract yet)
// Third time: NOW extract an abstraction
```

---

### Article IV — Privacy by Design

> No PII (Personally Identifiable Information) in logs, error messages, analytics, or debug output.

- **Encryption required:** All personal data encrypted at rest (AES-256) and in transit (TLS 1.3+)
- **Consent before collection:** Explicit user consent required before collecting any personal data
- **Data minimization:** Collect only the minimum data necessary for the stated purpose
- **Right to deletion:** All personal data must be deletable on request
- **Data retention:** Define explicit retention periods — no indefinite storage of PII
- **PII definition includes:** names, emails, phone numbers, IP addresses, device IDs, location data, behavioral data that can identify individuals

**Forbidden in logs:**
```
# NEVER log these:
logger.info(`User ${user.email} logged in`);     // WRONG: email in log
logger.error(`Payment failed: card ${cardNumber}`); // WRONG: PAN in log
console.log(JSON.stringify(req.body));           // WRONG: may contain PII

# ALLOWED:
logger.info(`User ${user.id} logged in`);        // OK: only ID
logger.error(`Payment failed: card ending ${last4}`); // OK: last 4 only
logger.error(`Validation failed`, { fields: Object.keys(req.body) }); // OK: field names only
```

---

### Article V — Security by Default

> Security is not a feature — it is a prerequisite.

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

## Section 2 — Project-Specific Articles

> Add project-specific constitutional rules below.
> Each article should: state the rule, explain why it exists, give an example.

### Article IX — [User Defined]
<!-- This section is reserved for project-specific rules added by the user or init.py -->
<!-- Example: Tenant Isolation, Audit Trails, or Performance Budgets -->

```
Example articles for different project types:

--- SaaS Multi-tenant ---
Article VIII — Tenant Isolation
  Every database query on tenant-owned data MUST include a tenant_id filter.
  Cross-tenant data access is categorically forbidden.
  Violation: immediate security incident — revert, audit, report.

--- Regulated Industries (HIPAA/PCI) ---
Article VIII — Audit Trail Completeness
  Every mutation of PHI (Protected Health Information) or PCI data must:
  - Be logged with: user ID, timestamp, action, before-value, after-value
  - Be retained for minimum 7 years (HIPAA) or 12 months (PCI-DSS)
  - Be immutable (append-only log, cryptographic verification)

--- Public API ---
Article VIII — Backward Compatibility
  Once an API endpoint is in production, its response schema is frozen.
  Breaking changes require: new API version, 6-month parallel support, deprecation notice.

--- High-Traffic Applications ---
Article VIII — Performance Budget
  All API endpoints must respond within 200ms at p99 under normal load.
  Any change that degrades p99 latency by > 20% is a performance regression — blocked.
  Database queries must use EXPLAIN ANALYZE before committing any new query.
```

---

## Section 3 — EARS Syntax Quick Reference

Use EARS (Easy Approach to Requirements Syntax) for all requirements in PRD.md and spec.md.

### Pattern 1 — Ubiquitous (always applies)
```
THE SYSTEM SHALL [action].

Example:
THE SYSTEM SHALL encrypt all data in transit using TLS 1.3 or higher.
```

### Pattern 2 — Event-Driven (triggered by an event)
```
WHEN [trigger event]
THE SYSTEM SHALL [response].

Example:
WHEN a user submits a login form with incorrect credentials 3 consecutive times
THE SYSTEM SHALL lock the account for 15 minutes and send an unlock email.
```

### Pattern 3 — State-Driven (while in a state)
```
WHILE [system state]
THE SYSTEM SHALL [behavior].

Example:
WHILE the payment processing service is unavailable
THE SYSTEM SHALL queue payment requests and retry with exponential backoff.
```

### Pattern 4 — Optional Feature
```
WHERE [feature is enabled]
THE SYSTEM SHALL [behavior].

Example:
WHERE two-factor authentication is enabled for the account
THE SYSTEM SHALL require a TOTP code on each login.
```

### Pattern 5 — Unwanted Behavior (negative requirement)
```
THE SYSTEM SHALL NOT [forbidden behavior].

Example:
THE SYSTEM SHALL NOT store plaintext passwords in any storage medium.
THE SYSTEM SHALL NOT expose stack traces in HTTP responses in production.
```

---

## Section 4 — Example Constitutional Clauses by Project Type

### SaaS Web Application
```
- Article on: tenant isolation, rate limiting, subscription enforcement
- Rate limit: 100 req/min per API key, 1000 req/min per tenant
- Subscription enforcement: feature flags tied to plan level
```

### REST API (consumed by mobile clients)
```
- Article on: backward compatibility (6-month deprecation window)
- Article on: versioned URLs (/v1/, /v2/) not header versioning
- Article on: response envelope: { data, meta: { page, total }, errors }
```

### E-commerce / Payment Processing
```
- Article on: PCI-DSS: never store raw card numbers
- Article on: idempotency: all payment operations idempotent with idempotency-key
- Article on: inventory: never sell more than available stock (optimistic locking)
```

### Internal Developer Tool
```
- Article on: no breaking CLI changes without major version bump
- Article on: all config changes backward compatible for 2 minor versions
- Article on: exit codes: 0 = success, 1 = user error, 2 = system error
```

---

*This Constitution was established on: [DATE]*
*Last amended: [DATE]*
*Amended by: [team member name]*
*Reason for amendment: [brief explanation]*
