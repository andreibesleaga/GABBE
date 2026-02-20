# Guide: Monolith & Modular Monolith
<!-- Vertical slice architecture, module boundaries, Strangler Fig migration -->

---

## Monolith vs Modular Monolith vs Microservices

```
Traditional Monolith:
  One codebase, tightly coupled, no module boundaries
  Fast to start, impossible to scale teams beyond ~5 engineers
  Avoid for new projects unless extremely time-constrained

Modular Monolith (recommended starting point):
  One codebase, modules with enforced boundaries
  Modules can be extracted to services when needed (Strangler Fig)
  Best for: < 50 engineers, domain not fully understood yet

Microservices:
  Multiple codebases, independent deployments
  Best for: > 50 engineers, proven domain boundaries, strong DevOps
  See: guides/microservices.md
```

**Start with modular monolith. Extract microservices only when boundaries are proven and scale demands it.**

---

## Modular Monolith — Vertical Slice Architecture

```
src/
  modules/                   # Each module = bounded context
    users/
      domain/               # Pure business logic
        user.entity.ts
        user.repository.ts  # Interface
      application/
        create-user.use-case.ts
        get-user.use-case.ts
      infrastructure/
        prisma-user.repository.ts
      http/
        users.controller.ts
        users.routes.ts
      index.ts              # Public API: what this module exports
      # Everything else is private to this module

    orders/
      domain/
        order.entity.ts
        order-item.entity.ts
      application/
        create-order.use-case.ts
      infrastructure/
        prisma-order.repository.ts
      http/
        orders.controller.ts
      index.ts

    payments/
      domain/
      application/
      infrastructure/
      index.ts

  shared/                    # ONLY for truly shared utilities
    domain/
      value-objects/         # Money.ts, Address.ts (used by multiple modules)
    infrastructure/
      database/             # Prisma client singleton
      cache/                # Redis client
    lib/
      result.ts             # Result<T, E> type
      logger.ts             # Logger configuration

  main/                      # Bootstrap — wires modules together
    server.ts
    container.ts
```

---

## Module Boundary Rules

```typescript
// RULE: Modules communicate ONLY through their public API (index.ts)
// Internal types are module-private — not imported directly

// users/index.ts — public API
export type { UserId, UserDto } from './domain/user.entity';
export { CreateUserUseCase } from './application/create-user.use-case';
export type { IUserRepository } from './domain/user.repository';

// orders module can use users public API:
import type { UserId } from '@/modules/users'; // CORRECT — through public API

// orders module CANNOT:
import { User } from '@/modules/users/domain/user.entity'; // WRONG — internal type
import { PrismaUserRepository } from '@/modules/users/infrastructure/...'; // WRONG
```

### Enforce with dependency-cruiser

```javascript
// .dependency-cruiser.cjs
module.exports = {
  forbidden: [
    {
      name: 'no-cross-module-internal-access',
      severity: 'error',
      from: { path: '^src/modules/([^/]+)' },
      to: {
        path: '^src/modules/([^/]+)/(domain|application|infrastructure)',
        // Allow if module names match (accessing own internals)
        pathNot: '^src/modules/$1'
      }
    },
    {
      name: 'no-cross-module-imports',
      severity: 'error',
      from: { path: '^src/modules/([^/]+)' },
      to: { path: '^src/modules/([^/]+)' },
      // Must go through the public index, not internal paths
    }
  ]
};
```

---

## Module Communication Patterns

### Direct (In-Process)
```typescript
// Same process — inject use case across modules
// Orders module depends on Users module public API

class CreateOrderUseCase {
  constructor(
    private readonly orderRepo: IOrderRepository,
    private readonly getUser: GetUserUseCase, // From users module
  ) {}

  async execute(command: CreateOrderCommand) {
    const user = await this.getUser.execute({ id: command.userId });
    if (!user) throw new UserNotFoundError(command.userId);
    // ... create order
  }
}
```

### Event-Driven (In-Process Event Bus)
```typescript
// Loose coupling within the monolith — modules don't know about each other
// Best for: side effects (notifications, analytics, audit log)

// Orders module publishes
eventBus.publish(new OrderCreatedEvent(order.id, order.userId));

// Notifications module subscribes
eventBus.subscribe(OrderCreatedEvent, async (event) => {
  await sendOrderConfirmationEmail(event.userId);
});
```

### Shared Database (with Module-Scoped Tables)
```sql
-- Even in a monolith, namespace tables by module:
users_accounts     -- users module
users_sessions     -- users module
orders_orders      -- orders module
orders_items       -- orders module
payments_invoices  -- payments module

-- Module-scoped: orders module NEVER queries users_* tables directly
-- It uses the users module's public API (use case or repository interface)
```

---

## Feature Flagging for Safe Rollout

```typescript
// Use feature flags to deploy new code safely
// LaunchDarkly, Flipt, Growthbook, or simple env-var-based

async function getCheckoutPage(user: User): Promise<CheckoutPage> {
  const isNewCheckoutEnabled = await featureFlags.isEnabled(
    'new-checkout-flow',
    { userId: user.id, email: user.email }
  );

  if (isNewCheckoutEnabled) {
    return newCheckoutService.render(user);
  }
  return legacyCheckoutService.render(user);
}
```

---

## Testing Strategy for Monolith

```
Unit tests (fast — no I/O):
  Test domain entities and use cases in isolation
  Mock repositories and external services
  ~300ms for full suite

Module integration tests:
  Test each module against real database (test schema)
  Use Testcontainers for ephemeral PostgreSQL
  Test: full flow from HTTP request → database

Cross-module integration tests:
  Test interactions between modules
  Verify that module public APIs work as expected
  Test event-driven side effects

E2E tests (slow — real browser):
  Happy path user journeys
  Critical business flows only
  Run in CI before release
```

---

## Strangler Fig Pattern — Extracting Services

When a module needs to become its own microservice:

```
Phase 1: Identify the extraction target
  - Module with different scaling needs
  - Module with its own team
  - Module with proven boundaries

Phase 2: Add a facade
  - Create an HTTP client interface in front of the module
  - Other modules use the client (not internal module)
  - Initially the client calls the local module (no network hop)

Phase 3: Extract to separate service
  - Deploy the module as a separate service
  - Update the client to make real HTTP calls
  - Other modules require zero changes

Phase 4: Remove from monolith
  - Once all traffic goes through the external service
  - Delete the module from the monolith

Each phase: fully tested, independently deployable, zero downtime
```

```typescript
// Phase 2: Facade (local call, same process)
class UserServiceClient {
  constructor(private readonly getUserUseCase: GetUserUseCase) {}

  async getUser(id: string): Promise<UserDto | null> {
    return this.getUserUseCase.execute({ id }); // Local call
  }
}

// Phase 3: Facade updated (remote HTTP call, no changes to consumers)
class UserServiceClient {
  async getUser(id: string): Promise<UserDto | null> {
    const response = await fetch(`${USER_SERVICE_URL}/api/v1/users/${id}`);
    if (response.status === 404) return null;
    return response.json();
  }
}
```

---

## Monolith Health Indicators

Track these metrics to know when to consider extraction:

```
Coupling metrics:
  - Afferent coupling (Ca) per module — how many other modules depend on it
  - Build time increasing despite unchanged code (coupling growing)
  - Test suite > 10 minutes (usually coupling + lack of isolation)

Deployment metrics:
  - Small changes require full regression test suite
  - Two teams waiting on each other's deployments
  - Rollback of one feature requires reverting unrelated code

Team metrics:
  - > 5 engineers modifying same module regularly
  - "Stepping on each other's toes" incidents
  - Code reviews involving people outside the feature's team

Scale metrics:
  - Can't scale one part without scaling everything
  - One heavy process (video processing, ML inference) starving HTTP handlers
```

When you see 3+ of these: it's time to extract the most independent module.
