# Technical Specification: [Feature Name]
<!-- Derived from: PRD.md — do not start before PRD is approved -->
<!-- Created by: prod-architect / agent | Date: [date] -->

---

## 1. Overview

**Feature:** [Name from PRD]
**PRD Reference:** [link to PRD.md]
**SDLC Phase:** S03 — Specification
**Spec author:** [agent/human]

---

## 2. Architecture Impact

**Affected layers:**
- [ ] Domain (new entities, value objects, domain events)
- [ ] Application (new use cases, command/query handlers)
- [ ] Adapters (new controllers, presenters, gateways)
- [ ] Infrastructure (new repository implementations, external API clients)
- [ ] Main/Bootstrap (new wiring)

**New services/modules:**
- `[ModuleName]` — [brief purpose]

**Modified existing files:**
- `[file path]` — [what changes]

**New files to create:**
- `[file path]` — [purpose]

---

## 3. Database Changes

### New Tables
```sql
CREATE TABLE [table_name] (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  [field]    [type] NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_[table]_[field] ON [table_name]([field]);
```

### Modified Tables
```sql
-- Migration: [migration_name]
ALTER TABLE [table_name] ADD COLUMN [field] [type] [constraints];
```

### Rollback Plan
```sql
-- Rollback
ALTER TABLE [table_name] DROP COLUMN IF EXISTS [field];
```

### ORM Schema (Prisma example)
```prisma
model [ModelName] {
  id        String   @id @default(uuid())
  [field]   [Type]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("[table_name]")
}
```

---

## 4. API Contracts

### Endpoints

#### POST /api/v1/[resource]
```yaml
Request:
  Content-Type: application/json
  Authorization: Bearer {token}
  Body:
    [field]: string (required, max: 255)
    [field]: string (required, email format)

Response 201 Created:
  Content-Type: application/json
  Body:
    id:         uuid
    [field]:    string
    createdAt:  ISO 8601 datetime

Response 422 Unprocessable Entity:
  Body:
    error:
      code:    "VALIDATION_ERROR"
      message: "Validation failed"
      details:
        - field: "[field_name]"
          code:  "REQUIRED"
          message: "[field] is required"

Response 401 Unauthorized:
  Body:
    error:
      code:    "UNAUTHORIZED"
      message: "Authentication required"
```

---

## 5. Domain Model

### Entities

```typescript
// src/domain/[entity].ts
interface [Entity] {
  id: string;           // UUID
  [field]: string;      // [constraints]
  createdAt: Date;
  updatedAt: Date;
}

// Domain invariants:
// - [field] must be [constraint]
// - [entity] cannot be [invalid state]
```

### Domain Events

```typescript
// Events emitted by this feature
interface [EntityCreatedEvent] {
  type: '[ENTITY]_CREATED';
  payload: { id: string; [field]: string; };
  occurredAt: Date;
}
```

### Value Objects

```typescript
// src/domain/value-objects/[name].ts
class [ValueObjectName] {
  private readonly value: string;

  private constructor(value: string) {
    this.value = value;
  }

  static create(value: string): Result<[ValueObjectName], ValidationError> {
    if (!isValid(value)) {
      return Result.fail(new ValidationError('[validation message]'));
    }
    return Result.ok(new [ValueObjectName](value));
  }

  toString(): string { return this.value; }
}
```

---

## 6. Use Cases / Application Services

```typescript
// src/application/[feature]/[action]-[entity].use-case.ts

interface [Action][Entity]Command {
  [field]: string;
}

interface [Action][Entity]Result {
  id: string;
  [field]: string;
}

class [Action][Entity]UseCase {
  constructor(
    private readonly [entity]Repository: I[Entity]Repository,
    private readonly eventBus: IEventBus,
  ) {}

  async execute(command: [Action][Entity]Command): Promise<[Action][Entity]Result> {
    // 1. Validate input (domain validation)
    // 2. Apply business rules
    // 3. Persist via repository
    // 4. Emit domain event
    // 5. Return result DTO
  }
}
```

---

## 7. Testing Strategy

### Unit Tests
```
src/domain/[entity].test.ts
  - validates [field] format correctly
  - rejects invalid [field] values
  - domain event is emitted on creation

src/application/[feature]/[action]-[entity].use-case.test.ts
  - creates [entity] with valid input
  - returns 422 when [field] is invalid
  - calls repository.save() with correct data
  - emits [ENTITY_CREATED] event on success
```

### Integration Tests
```
tests/integration/api/[resource].test.ts
  - POST /api/v1/[resource] with valid body returns 201
  - POST /api/v1/[resource] with missing field returns 422
  - POST /api/v1/[resource] without auth returns 401
  - GET /api/v1/[resource] returns paginated list
```

### Coverage Target
- Domain layer: > 96%
- Application layer: > 85%
- Adapters layer: > 96% (integration tests)

---

## 8. Security Decisions

**Authentication:** [JWT / Session / API Key / None]
**Authorization:** [RBAC rules — who can access this endpoint]
**Input validation:** [Zod schema / FormRequest / validator.js]
**Rate limiting:** [X requests/minute per IP / per user]
**Data sanitization:** [HTML entities escaped / SQL parameterized]

**Threat model reference:** [link to docs/security/threat-models/]

---

## 9. Feature Flags / Rollout

**Feature flag:** [Yes/No — flag name if yes]
**Rollout strategy:** [All users at once / Percentage rollout / Internal only first]
**Rollback trigger:** [Error rate > X% / manual decision]

---

## 10. Approval

| Role | Name | Status | Date |
|---|---|---|---|
| Tech Lead | [name] | [APPROVED / PENDING] | [date] |
| Security | [name] | [APPROVED / PENDING] | [date] |

**Human approval required before proceeding to Tasks phase (S04).**
