# Guide: Microservices & Distributed Systems
<!-- Bounded contexts, event-driven, contract testing, service mesh -->

---

## When to Use Microservices

**Use microservices when:**
- Teams can own and deploy services independently
- Services have clearly different scaling needs
- Services have fundamentally different technology requirements
- Organization is large enough to support operational overhead

**Do NOT use microservices when:**
- Team < 10 engineers (start with modular monolith)
- Domain is not well understood yet (boundaries will be wrong)
- Operational maturity is not there (monitoring, tracing, CI/CD)

**Start with a modular monolith. Extract services when boundaries are proven.**

---

## Service Decomposition — DDD Bounded Contexts

```
Decompose by business capability, not technical layer:

Good decomposition:
  user-service        → Registration, authentication, profile management
  order-service       → Order lifecycle, items, pricing
  payment-service     → Payment processing, refunds, invoicing
  notification-service → Emails, SMS, push notifications
  inventory-service   → Stock management, reservations

Bad decomposition (technical layers):
  database-service    → No! Databases are infrastructure
  api-gateway-service → No! API gateway is infrastructure
  validation-service  → No! Validation belongs in each service
```

### Service Boundaries Checklist

```
A good service boundary:
[ ] Owns its own data (no shared database between services)
[ ] Can be deployed independently (no coordinated releases required)
[ ] Has a clear single business capability
[ ] Changes don't require simultaneous changes in other services
[ ] Could use a different technology if needed
```

---

## Inter-Service Communication

### Synchronous (HTTP/gRPC) — for queries and commands needing immediate response

```typescript
// HTTP REST: use for simple CRUD, external-facing APIs
// Response within: < 500ms (otherwise consider async)

// gRPC: use for internal service communication needing strong typing
// Better for: high-throughput, low-latency, streaming scenarios
// Use: Protocol Buffers (.proto) for schema definition

// Circuit Breaker pattern (prevent cascade failures)
const circuitBreaker = new CircuitBreaker(callUserService, {
  timeout: 3000,         // 3 second timeout
  errorThresholdPercentage: 50,  // Open after 50% failures
  resetTimeout: 30000,   // Try again after 30 seconds
});
```

### Asynchronous (Message Queues) — for events and commands not needing immediate response

```typescript
// Event-driven: services react to events, no direct coupling
// Producer:
await eventBus.publish({
  type: 'order.created',
  payload: { orderId, userId, total },
  occurredAt: new Date().toISOString(),
});

// Consumer (in notification-service):
eventBus.subscribe('order.created', async (event) => {
  await sendOrderConfirmationEmail(event.payload.userId);
});

// Message queues: RabbitMQ, Apache Kafka, AWS SQS, Azure Service Bus
// Choose based on: throughput, ordering guarantees, replay needs
```

### Outbox Pattern (ensure at-least-once delivery)

```sql
-- Save event to outbox table in same DB transaction as business operation
BEGIN;
  INSERT INTO orders (id, user_id, total) VALUES ($1, $2, $3);
  INSERT INTO outbox_events (type, payload) VALUES ('order.created', $4);
COMMIT;
-- Separate process reads outbox and publishes to message broker
-- Delete from outbox only after confirmed published
```

---

## AGENTS.md for Monorepos with Multiple Services

```yaml
# Root AGENTS.md (global rules)
project_name: "MyPlatform Monorepo"
structure: "Multi-service monorepo"

# Service-specific AGENTS.md files override root:
#   services/user-service/AGENTS.md
#   services/order-service/AGENTS.md

global_rules:
  - "All inter-service HTTP calls must go through the service's client module"
  - "No service may directly query another service's database"
  - "All API contracts defined in services/[name]/openapi.yaml"
  - "All services must expose GET /health returning 200 OK"
  - "All services must emit structured logs in JSON format"

global_commands:
  test_all: "pnpm turbo run test"
  build_all: "pnpm turbo run build"
  lint_all: "pnpm turbo run lint"
```

---

## Contract Testing with Pact

```typescript
// Consumer-driven contract testing — consumer defines expectations
// Provider verifies it meets all consumer contracts

// Consumer (order-service) defines contract:
// pact.spec.ts in order-service
const provider = new PactV3({
  consumer: 'order-service',
  provider: 'user-service',
});

await provider.addInteraction({
  uponReceiving: 'a request for user profile',
  withRequest: {
    method: 'GET',
    path: '/api/v1/users/123',
    headers: { Authorization: like('Bearer token') },
  },
  willRespondWith: {
    status: 200,
    body: { id: '123', email: like('user@example.com'), name: like('Alice') },
  },
});

// Provider (user-service) verifies it satisfies all consumer contracts:
// In CI: pact-broker publish → user-service CI fetches and verifies contracts
```

---

## Distributed Tracing

```typescript
// Use OpenTelemetry — standard across all services
import { trace, context, propagation } from '@opentelemetry/api';

// In API gateway / first service — create root trace
const tracer = trace.getTracer('order-service');
const span = tracer.startSpan('createOrder');

// Propagate trace context to downstream services
const carrier = {};
propagation.inject(context.active(), carrier);
// Add carrier headers to HTTP request to next service

// In downstream service — extract and continue trace
const ctx = propagation.extract(context.active(), incomingHeaders);
const childSpan = tracer.startSpan('validatePayment', {}, ctx);
```

**Tools:** Jaeger, Zipkin, AWS X-Ray, Datadog APM, Grafana Tempo

---

## Event Sourcing & CQRS

```typescript
// Event Sourcing: store events, derive state
// CQRS: separate read model from write model

// Write side: append events
interface OrderEvent {
  type: 'ORDER_CREATED' | 'ORDER_ITEM_ADDED' | 'ORDER_PAID' | 'ORDER_CANCELLED';
  aggregateId: string;
  sequenceNumber: number;
  occurredAt: Date;
  payload: unknown;
}

// Append to event store (never update/delete)
await eventStore.append(orderId, [
  { type: 'ORDER_CREATED', payload: { userId, items } }
]);

// Read side: project events into read model (denormalized for fast reads)
// Rebuilt from events at any point in time — enables time travel debugging
```

**When to use:** Financial systems, audit-required systems, complex undo/redo

---

## Service Mesh Patterns

```yaml
# Kubernetes + Istio/Linkerd for:
#   - mTLS between all services (zero-trust networking)
#   - Load balancing and circuit breaking at infrastructure level
#   - Traffic splitting for canary deployments

# Example: Canary deployment via Istio VirtualService
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: user-service
spec:
  http:
  - route:
    - destination:
        host: user-service
        subset: stable
      weight: 90
    - destination:
        host: user-service
        subset: canary
      weight: 10  # 10% to new version
```

---

## Testing Strategy for Microservices

| Test Type | Scope | Tools | When |
|---|---|---|---|
| Unit | Single function/class | Vitest, Jest, Pest | Every commit |
| Integration | Single service + DB | Testcontainers, Docker Compose | Every commit |
| Contract | Consumer/Provider contracts | Pact | Every commit to shared APIs |
| E2E | Full user flow across services | Playwright + real stack | Before release |
| Chaos | Resilience to failures | Chaos Monkey, Gremlin | Scheduled |
| Load | Performance under load | k6, Gatling | Pre-release |

---

## API Gateway Pattern

```
External clients → API Gateway → Services

API Gateway responsibilities:
  - Authentication (validate JWT, session)
  - Rate limiting (per client, per IP)
  - Request routing (path-based, header-based)
  - SSL termination
  - Request/response transformation (if needed)
  - CORS headers
  - Logging / tracing injection

API Gateway does NOT:
  - Business logic
  - Database queries
  - Service orchestration (use saga pattern in service layer)
```

---

## Key Patterns Summary

| Pattern | Problem Solved | When to Use |
|---|---|---|
| API Gateway | External routing, auth, rate limiting | Always |
| Circuit Breaker | Cascade failures | Synchronous calls between services |
| Outbox | At-least-once event delivery | Critical events (payments, orders) |
| Saga | Distributed transactions | Multi-service operations |
| CQRS | Read/write model separation | High-read systems |
| Event Sourcing | Complete audit trail, time travel | Financial, regulated systems |
| Strangler Fig | Incremental migration from monolith | Legacy modernization |
| BFF | Per-client API tailoring | Mobile + Web with different needs |
