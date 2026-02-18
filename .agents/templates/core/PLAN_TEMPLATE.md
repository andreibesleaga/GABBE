# Implementation Plan: [Feature Name]
<!-- Derived from: SPEC_TEMPLATE.md — do not start before spec is approved -->
<!-- Created by: prod-architect | Date: [date] -->

---

## 1. Overview

**Feature:** [Name]
**Spec Reference:** [link to SPEC_TEMPLATE.md]
**Estimated phases:** [N]
**Dependencies:** [External dependencies — library upgrades, other features, team dependencies]

---

## 2. Implementation Phases

### Phase 1 — [Foundation / Domain Layer]
**Goal:** [What will be working after this phase]

**Files to create:**
```
src/domain/[entity].ts                    - Entity definition + invariants
src/domain/events/[event].ts              - Domain events
src/domain/value-objects/[vo].ts          - Value objects
src/domain/ports/[repo-interface].ts      - Repository interface (IRepository)
```

**Files to modify:**
```
[none in Phase 1 — foundation only]
```

**Acceptance criteria for this phase:**
- [ ] Domain entity tests pass
- [ ] Value object validation tests pass
- [ ] No framework imports in domain layer

---

### Phase 2 — [Application Layer]
**Goal:** [What will be working after this phase]
**Depends on:** Phase 1 complete

**Files to create:**
```
src/application/[feature]/[action]-[entity].use-case.ts
src/application/[feature]/[action]-[entity].command.ts
src/application/[feature]/[action]-[entity].result.ts
tests/unit/application/[action]-[entity].use-case.test.ts
```

**Acceptance criteria for this phase:**
- [ ] Use case unit tests pass with mocked repository
- [ ] Use case is framework-agnostic (testable without HTTP or DB)

---

### Phase 3 — [Infrastructure Layer]
**Goal:** [What will be working after this phase]
**Depends on:** Phase 1 complete (needs domain interfaces)

**Files to create:**
```
src/infrastructure/[entity]/prisma-[entity].repository.ts
prisma/migrations/[timestamp]_[migration-name]/migration.sql
```

**Files to modify:**
```
prisma/schema.prisma  - Add new model
```

**Acceptance criteria for this phase:**
- [ ] Repository integration tests pass against test DB
- [ ] Migration runs forward and backward without errors
- [ ] All existing tests still pass

---

### Phase 4 — [Adapters / API Layer]
**Goal:** [What will be working after this phase]
**Depends on:** Phase 2 and Phase 3 complete

**Files to create:**
```
src/adapters/http/[entity].controller.ts
src/adapters/http/[entity].dto.ts          - Zod schema for request validation
tests/integration/api/[entity].test.ts
```

**Acceptance criteria for this phase:**
- [ ] POST /api/v1/[resource] returns 201 with valid input
- [ ] Returns 422 with field errors for invalid input
- [ ] Returns 401 when unauthenticated
- [ ] Integration tests pass

---

### Phase 5 — [Wiring / Bootstrap]
**Goal:** Full feature wired and functional end-to-end
**Depends on:** All previous phases complete

**Files to modify:**
```
src/main/container.ts    - Register new dependencies in DI container
src/main/routes.ts       - Register new routes
```

**Acceptance criteria for this phase:**
- [ ] Full end-to-end test passes (registration → login → use feature)
- [ ] All tests pass (unit + integration)
- [ ] No new circular dependencies (run madge)
- [ ] Lint and typecheck pass

---

## 3. Dependencies Between Phases

```
Phase 1 (Domain)
  └─> Phase 2 (Application) — depends on domain entities and interfaces
  └─> Phase 3 (Infrastructure) — depends on domain interfaces

Phase 2 + Phase 3 complete
  └─> Phase 4 (Adapters)

Phase 1 + 2 + 3 + 4 complete
  └─> Phase 5 (Wiring)
```

---

## 4. Risk & Assumptions Log

| # | Risk/Assumption | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | [Risk: Database migration may lock table] | M | H | Use pt-online-schema-change or test on production-sized dataset |
| 2 | [Assumption: Auth middleware already in place] | — | H | Verify in Phase 4 — fallback: implement basic auth in this phase |
| 3 | [Risk: External API rate limits] | L | M | Add retry with exponential backoff in infrastructure layer |

---

## 5. Testing Strategy per Phase

| Phase | Test Type | Command | Pass Criteria |
|---|---|---|---|
| 1 | Unit | `[test cmd] tests/unit/domain/` | All pass |
| 2 | Unit | `[test cmd] tests/unit/application/` | All pass |
| 3 | Integration | `[test cmd] tests/integration/db/` | All pass against test DB |
| 4 | Integration | `[test cmd] tests/integration/api/` | All pass |
| 5 | E2E | `[test cmd] tests/e2e/` | Happy path passes |

---

## 6. Approval

| Role | Name | Status | Date |
|---|---|---|---|
| Tech Lead | [name] | [APPROVED / PENDING] | [date] |

**Human approval required before decomposing into tasks (S04).**
