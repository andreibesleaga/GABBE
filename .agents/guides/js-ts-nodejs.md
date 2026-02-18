# Guide: JavaScript / TypeScript / Node.js
<!-- Clean Architecture with TypeScript, Fastify, Prisma, Vitest, and Playwright -->

---

## Directory Structure — Clean Architecture

```
src/
  domain/                    # Pure business logic — NO framework imports
    entities/                # User.ts, Order.ts — domain entities
    value-objects/           # Email.ts, Money.ts — immutable primitives
    events/                  # UserRegistered.ts, OrderCreated.ts
    ports/                   # IUserRepository.ts — interfaces only
    errors/                  # DomainError.ts, ValidationError.ts
    services/                # Pure domain services (no DB, no HTTP)

  application/               # Use cases — orchestrates domain
    users/
      create-user.use-case.ts
      create-user.command.ts
      create-user.result.ts
    orders/
      create-order.use-case.ts

  adapters/                  # Interface adapters — translate between layers
    http/
      users.controller.ts    # Thin controllers — validate, delegate, respond
      users.dto.ts           # Zod schemas for request/response
    presenters/              # Transform domain entities to HTTP response shape

  infrastructure/            # Framework + external services implementations
    database/
      prisma-user.repository.ts  # Implements IUserRepository using Prisma
    email/
      sendgrid-email.service.ts
    cache/
      redis-cache.service.ts

  main/                      # Composition root — wires everything together
    container.ts             # DI container setup
    server.ts                # Fastify server + plugin registration
    routes.ts                # Route registration

tests/
  unit/                      # Mirror of src/ — fast, no DB, no HTTP
  integration/               # Real DB, Docker Compose
  e2e/                       # Full browser tests with Playwright
```

---

## Layer Import Rules

```typescript
// domain/ — MUST NOT import from any other layer
// application/ — MAY import from domain only
// adapters/ — MAY import from domain + application
// infrastructure/ — MAY import from domain (implements interfaces)
// main/ — MAY import from all layers (composition root only)

// CORRECT: infrastructure depends on domain interface
import type { IUserRepository } from '@/domain/ports/i-user-repository';

// WRONG: domain depending on infrastructure
import { PrismaClient } from '@prisma/client'; // NEVER in domain layer
```

**Enforce with:** `npx dependency-cruiser --config .dependency-cruiser.cjs src/`

---

## AGENTS.md Snippet (Node.js/TypeScript project)

```yaml
runtime: Node.js 22
language: TypeScript 5.x (strict mode)
framework: Fastify 5.x
package_manager: pnpm

install: pnpm install
dev: pnpm dev
test: pnpm vitest run
test_coverage: pnpm vitest run --coverage
test_single: pnpm vitest run src/path/to/file.test.ts
build: pnpm build
typecheck: pnpm tsc --noEmit
lint: pnpm eslint . --ext .ts,.tsx
format: pnpm prettier --write .
security_scan: pnpm audit --audit-level=moderate
migrate: pnpm prisma migrate dev
```

---

## Tech Stack

### Core
| Role | Library | Why |
|---|---|---|
| Runtime | Node.js 22 (LTS) | Active LTS, native fetch, ES modules |
| Language | TypeScript 5.x strict | Type safety, better DX |
| HTTP Framework | Fastify 5.x | Fast, schema validation built-in, plugins |
| Validation/DTOs | Zod 3.x | Runtime type validation + TypeScript inference |
| ORM | Prisma 5.x | Type-safe queries, migration-first, great DX |
| API docs | @scalar/fastify-api-reference | OpenAPI UI |

### Testing
| Role | Library | Command |
|---|---|---|
| Unit + Integration | Vitest | `pnpm vitest run` |
| HTTP integration | Supertest | Within Vitest |
| Database integration | `@testcontainers/postgresql` | `pnpm vitest run tests/integration` |
| Browser/E2E | Playwright | `pnpm playwright test` |
| Coverage | Vitest Coverage (v8) | `--coverage` flag |

### Security
| Role | Library | Command |
|---|---|---|
| Dep audit | `npm audit` | `pnpm audit --audit-level=moderate` |
| SAST | Semgrep | `npx semgrep --config=p/security-audit src/` |
| Secret detection | gitleaks | `gitleaks detect --source=. --verbose` |
| HTTP security | Helmet.js | `app.register(fastifyHelmet)` |
| Rate limiting | `@fastify/rate-limit` | `app.register(fastifyRateLimit)` |
| Input sanitization | validator.js | For specific string validation beyond Zod |
| Architecture | dependency-cruiser | `npx depcruise src/` |

---

## TypeScript Configuration (strict mode)

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## Patterns

### Domain Entity with Invariants

```typescript
// src/domain/entities/user.ts
import { Email } from '../value-objects/email';
import { UserId } from '../value-objects/user-id';
import { UserRegisteredEvent } from '../events/user-registered.event';
import type { DomainEvent } from '../events/domain-event';

export class User {
  private readonly _events: DomainEvent[] = [];

  private constructor(
    public readonly id: UserId,
    public readonly email: Email,
    public readonly name: string,
    public readonly createdAt: Date,
  ) {}

  static create(email: Email, name: string): User {
    const user = new User(UserId.generate(), email, name, new Date());
    user._events.push(new UserRegisteredEvent(user.id.value, user.email.value));
    return user;
  }

  get events(): readonly DomainEvent[] { return this._events; }
  clearEvents(): void { this._events.length = 0; }
}
```

### Value Object

```typescript
// src/domain/value-objects/email.ts
import { z } from 'zod';

const emailSchema = z.string().email().max(255);

export class Email {
  private constructor(public readonly value: string) {}

  static create(value: string): Email {
    const result = emailSchema.safeParse(value);
    if (!result.success) {
      throw new ValidationError(`Invalid email: ${value}`);
    }
    return new Email(result.data);
  }

  equals(other: Email): boolean { return this.value === other.value; }
}
```

### Use Case

```typescript
// src/application/users/create-user.use-case.ts
import type { IUserRepository } from '@/domain/ports/i-user-repository';
import type { IEventBus } from '@/domain/ports/i-event-bus';
import { User } from '@/domain/entities/user';
import { Email } from '@/domain/value-objects/email';
import { EmailAlreadyExistsError } from '@/domain/errors/email-already-exists.error';

export interface CreateUserCommand {
  email: string;
  name: string;
}

export class CreateUserUseCase {
  constructor(
    private readonly userRepository: IUserRepository,
    private readonly eventBus: IEventBus,
  ) {}

  async execute(command: CreateUserCommand): Promise<{ id: string }> {
    const email = Email.create(command.email); // validates here

    const existing = await this.userRepository.findByEmail(email);
    if (existing) throw new EmailAlreadyExistsError(email.value);

    const user = User.create(email, command.name);
    await this.userRepository.save(user);
    await this.eventBus.publish(user.events);
    user.clearEvents();

    return { id: user.id.value };
  }
}
```

### Thin Controller (Fastify)

```typescript
// src/adapters/http/users.controller.ts
import type { FastifyPluginAsync } from 'fastify';
import { z } from 'zod';
import type { CreateUserUseCase } from '@/application/users/create-user.use-case';

const CreateUserBody = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

export const usersRouter: FastifyPluginAsync = async (app) => {
  app.post('/api/v1/users', {
    schema: { body: CreateUserBody },
  }, async (request, reply) => {
    const result = await request.container.resolve(CreateUserUseCase)
      .execute(request.body);
    return reply.status(201).send(result);
  });
};
```

---

## Error Handling Patterns

```typescript
// src/domain/errors/domain-error.ts
export abstract class DomainError extends Error {
  abstract readonly code: string;
  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

// src/adapters/http/error-handler.ts (Fastify global error handler)
export const errorHandler: FastifyErrorHandler = (error, request, reply) => {
  if (error instanceof DomainError) {
    return reply.status(422).send({
      error: { code: error.code, message: error.message }
    });
  }
  if (error instanceof ValidationError) {
    return reply.status(400).send({
      error: { code: 'VALIDATION_ERROR', message: error.message }
    });
  }
  // Never expose internal errors to clients
  request.log.error(error);
  return reply.status(500).send({ error: { code: 'INTERNAL_ERROR', message: 'Internal server error' } });
};
```

---

## Security Best Practices

```typescript
// Register security plugins in src/main/server.ts
import fastifyHelmet from '@fastify/helmet';
import fastifyRateLimit from '@fastify/rate-limit';
import fastifyCors from '@fastify/cors';

await app.register(fastifyHelmet, {
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
    }
  }
});

await app.register(fastifyRateLimit, {
  max: 100,
  timeWindow: '1 minute',
  // Stricter for auth endpoints: configure per-route
});

await app.register(fastifyCors, {
  origin: process.env.ALLOWED_ORIGINS?.split(',') ?? ['http://localhost:3000'],
  credentials: true,
});

// NEVER: wildcard CORS for authenticated APIs
// await app.register(fastifyCors, { origin: '*' }); // WRONG
```

---

## Tech Debt Detection Commands

```bash
# Cyclomatic complexity (flag > 10)
npx complexity-report --format json src/ | jq '.functions[] | select(.cyclomatic > 10)'

# Code duplication
npx jscpd src/ --min-lines 5 --min-tokens 50

# Circular dependencies
npx madge --circular --extensions ts src/

# Outdated dependencies
pnpm outdated

# Architecture violations
npx dependency-cruiser --config .dependency-cruiser.cjs src/
```
