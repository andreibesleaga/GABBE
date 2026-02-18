# Tasks: [Feature Name]
<!-- Atomic task breakdown — 15-minute rule: if a task takes > 15 min, decompose further -->
<!-- Derived from: PLAN_TEMPLATE.md | Created by: prod-tech-lead | Date: [date] -->

---

## Status Legend

```
TODO         - Not started
IN_PROGRESS  - Currently being worked on (max 1 task in this state)
DONE         - Completed and verified (tests pass)
BLOCKED      - Cannot proceed — reason documented below
```

---

## Phase 1 — [Domain Layer]

| ID | Task | Status | Acceptance Criteria | Notes |
|---|---|---|---|---|
| T-001 | Create `src/domain/[entity].ts` — define entity interface | TODO | TypeScript interface defined, no framework imports | |
| T-002 | Create `src/domain/value-objects/[Email].ts` — validation logic | TODO | VO rejects invalid values, constructor is private | |
| T-003 | Write tests for `[Entity]` domain invariants | TODO | All invariants tested: null, empty, too long, invalid format | |
| T-004 | Write tests for `[ValueObject]` validation | TODO | Tests cover valid, invalid (each error case), edge cases | |
| T-005 | Create `src/domain/ports/i-[entity]-repository.ts` — interface | TODO | Interface has: findById, save, findByEmail, delete | |
| T-006 | Create `src/domain/events/[entity]-created.event.ts` | TODO | Event has: type, payload, occurredAt | |

## Phase 2 — [Application Layer]

| ID | Task | Status | Acceptance Criteria | Notes |
|---|---|---|---|---|
| T-007 | Create `Create[Entity]Command` DTO | TODO | All required fields, typed, validated | |
| T-008 | Create `Create[Entity]UseCase` skeleton | TODO | Constructor injects I[Entity]Repository, IEventBus | |
| T-009 | Write unit test: valid input creates entity | TODO | TDD Red — test written before implementation | |
| T-010 | Write unit test: invalid email returns error | TODO | TDD Red | |
| T-011 | Write unit test: duplicate email returns error | TODO | TDD Red | |
| T-012 | Implement `Create[Entity]UseCase.execute()` | TODO | All 3 tests pass Green | |
| T-013 | Verify use case has no framework imports | TODO | `madge --circular` passes, no express/prisma/etc imports | |

## Phase 3 — [Infrastructure Layer]

| ID | Task | Status | Acceptance Criteria | Notes |
|---|---|---|---|---|
| T-014 | Add `[Entity]` to `prisma/schema.prisma` | TODO | Schema validates: `prisma validate` passes | |
| T-015 | Create migration: `add_[entity]_table` | TODO | `prisma migrate dev` runs without error | |
| T-016 | Test migration rollback | TODO | Rollback runs without error, schema is clean | |
| T-017 | Create `Prisma[Entity]Repository` implementing `I[Entity]Repository` | TODO | All interface methods implemented | |
| T-018 | Write integration test: `findById` returns correct entity | TODO | Test runs against real test database | |
| T-019 | Write integration test: `save` persists entity | TODO | Entity retrievable after save | |
| T-020 | Write integration test: `findByEmail` returns entity or null | TODO | Both found and not-found cases tested | |

## Phase 4 — [Adapters / API Layer]

| ID | Task | Status | Acceptance Criteria | Notes |
|---|---|---|---|---|
| T-021 | Create Zod schema for `Create[Entity]Request` | TODO | Schema validates: required fields, email format, max lengths | |
| T-022 | Create `[Entity]Controller.create()` method | TODO | Validates input, calls use case, returns 201 or 422 | |
| T-023 | Write integration test: POST with valid body → 201 | TODO | TDD Red first, then implement | |
| T-024 | Write integration test: POST without auth → 401 | TODO | TDD Red | |
| T-025 | Write integration test: POST with invalid email → 422 | TODO | TDD Red, check field-level errors in response | |
| T-026 | Write integration test: POST with missing required field → 422 | TODO | TDD Red | |
| T-027 | Implement controller to pass all 4 integration tests | TODO | All tests Green | |

## Phase 5 — [Wiring]

| ID | Task | Status | Acceptance Criteria | Notes |
|---|---|---|---|---|
| T-028 | Register `Prisma[Entity]Repository` in DI container | TODO | Container resolves `I[Entity]Repository` correctly | |
| T-029 | Register `Create[Entity]UseCase` in DI container | TODO | Use case receives dependencies via DI | |
| T-030 | Register route: `POST /api/v1/[resource]` | TODO | Route exists in router, calls controller | |
| T-031 | Run full test suite — all pass | TODO | Zero failing tests, coverage >= 96% | |
| T-032 | Run agentic-linter — no boundary violations | TODO | `dependency-cruiser` or `madge --circular` output clean | |
| T-033 | Run typecheck — zero errors | TODO | `tsc --noEmit` clean | |
| T-034 | Run lint — zero errors | TODO | `eslint` or `pint` clean | |
| T-035 | Manual smoke test: full create [entity] flow | TODO | Feature works end-to-end in development environment | |

---

## Blocked Tasks

<!-- Document why a task is blocked and what unblocks it -->

| Task ID | Blocked by | Since | Unblocked when |
|---|---|---|---|
| [T-XXX] | [reason / pending human decision] | [date] | [what needs to happen] |

---

## Progress Summary

```
Total tasks:    [35]
TODO:           [35]
IN_PROGRESS:    [0]
DONE:           [0]
BLOCKED:        [0]

Phase 1:  0/6  complete
Phase 2:  0/7  complete
Phase 3:  0/7  complete
Phase 4:  0/7  complete
Phase 5:  0/8  complete
```
