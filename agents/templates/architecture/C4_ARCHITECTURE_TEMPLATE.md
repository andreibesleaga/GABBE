# C4 Architecture — [System Name]
<!-- C4 Model: 4 levels of abstraction for software architecture -->
<!-- Created by: prod-architect | Date: [date] | Store in: docs/architecture/ -->
<!-- Reference: https://c4model.com -->

---

## Level 1 — System Context Diagram

> Highest level view: who uses the system and what external systems does it interact with?

```mermaid
C4Context
    title System Context — [System Name]

    Person(user, "End User", "A person who uses the system via web browser or mobile app")
    Person(admin, "Administrator", "Internal team member managing the system")

    System(system, "[System Name]", "The system being designed — [one sentence description]")

    System_Ext(email, "Email Service", "Sends transactional emails (SendGrid / Postmark)")
    System_Ext(payment, "Payment Processor", "Handles payments (Stripe / PayPal)")
    System_Ext(auth, "Identity Provider", "OAuth2 / SSO provider (Auth0 / Google)")

    Rel(user, system, "Uses", "HTTPS")
    Rel(admin, system, "Administers", "HTTPS")
    Rel(system, email, "Sends emails via", "HTTPS/SMTP")
    Rel(system, payment, "Processes payments via", "HTTPS")
    Rel(system, auth, "Authenticates via", "OIDC/OAuth2")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

---

## Level 2 — Container Diagram

> Zoom into the system: what are the deployable units (applications, databases, services)?

```mermaid
C4Container
    title Container Diagram — [System Name]

    Person(user, "End User")

    System_Boundary(system, "[System Name]") {
        Container(webapp, "Web Application", "React / Next.js", "Single Page Application — UI in browser")
        Container(api, "API Service", "Node.js / Fastify", "REST API serving mobile and web clients")
        Container(worker, "Background Worker", "Node.js / BullMQ", "Processes async jobs: emails, exports, etc.")
        ContainerDb(db, "Database", "PostgreSQL 16", "Primary data store — users, orders, etc.")
        ContainerDb(cache, "Cache", "Redis 7", "Session cache, rate limiting, job queue")
        ContainerDb(storage, "File Storage", "AWS S3", "User uploads and generated files")
    }

    System_Ext(email, "Email Service (SendGrid)")
    System_Ext(payment, "Stripe")

    Rel(user, webapp, "Uses", "HTTPS")
    Rel(webapp, api, "API calls", "HTTPS/JSON")
    Rel(api, db, "Reads/writes", "TCP/5432")
    Rel(api, cache, "Reads/writes", "TCP/6379")
    Rel(api, storage, "Stores files", "HTTPS")
    Rel(api, payment, "Processes payments", "HTTPS")
    Rel(worker, db, "Reads/writes", "TCP/5432")
    Rel(worker, cache, "Job queue", "TCP/6379")
    Rel(worker, email, "Sends emails", "HTTPS")
```

---

## Level 3 — Component Diagram

> Zoom into one container: what are the major components inside the API service?

```mermaid
C4Component
    title Component Diagram — API Service

    Container_Boundary(api, "API Service") {
        Component(router, "HTTP Router", "Fastify", "Routes incoming HTTP requests to controllers")
        Component(authMW, "Auth Middleware", "JWT/Passport", "Validates JWT tokens, injects user context")

        Component(userCtrl, "User Controller", "TypeScript", "Handles user CRUD operations")
        Component(orderCtrl, "Order Controller", "TypeScript", "Handles order creation and management")

        Component(createUserUC, "CreateUserUseCase", "TypeScript", "Business logic for user registration")
        Component(createOrderUC, "CreateOrderUseCase", "TypeScript", "Business logic for order creation")

        Component(userRepo, "UserRepository", "Prisma", "Persists and retrieves user data")
        Component(orderRepo, "OrderRepository", "Prisma", "Persists and retrieves order data")
        Component(eventBus, "EventBus", "BullMQ", "Dispatches domain events to worker")
    }

    ContainerDb(db, "Database", "PostgreSQL")
    ContainerDb(cache, "Cache", "Redis")

    Rel(router, authMW, "All requests through")
    Rel(authMW, userCtrl, "Authenticated requests")
    Rel(authMW, orderCtrl, "Authenticated requests")
    Rel(userCtrl, createUserUC, "Calls")
    Rel(orderCtrl, createOrderUC, "Calls")
    Rel(createUserUC, userRepo, "Uses")
    Rel(createOrderUC, orderRepo, "Uses")
    Rel(createOrderUC, eventBus, "Publishes OrderCreated")
    Rel(userRepo, db, "SQL queries")
    Rel(orderRepo, db, "SQL queries")
    Rel(eventBus, cache, "Job queue")
```

---

## Level 4 — Code/Class Diagram

> Zoom into a component: class structure and relationships (add as needed for complex components)

```
[Add Level 4 diagrams for complex domain areas as needed]

Example: User aggregate
  User (aggregate root)
    - Email (value object)
    - UserId (value object)
    - UserRole (enum)
    + create(email, name): Result<User>
    + updateEmail(email): Result<void>
    - validate(): void
```

---

## Architecture Decisions

See ADRs in `docs/architecture/decisions/` for rationale behind technology choices:

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | [Technology choice] | [Accepted/Proposed] |
| ADR-002 | [Architecture pattern] | [Accepted/Proposed] |

---

## Layer Import Rules

```
Domain layer:       No imports from application, adapters, or infrastructure
Application layer:  Imports domain only (interfaces, entities, value objects)
Adapters layer:     Imports domain + application (through interfaces)
Infrastructure:     Imports domain interfaces (implements them)
Main/Bootstrap:     Imports all layers (composition root only)
```

Enforced by: `agentic-linter.skill` using `dependency-cruiser` or `deptrac`

---

## Data Flow Diagrams

### User Registration Flow
```
Browser → POST /api/v1/users
  → AuthMiddleware (skip — public endpoint)
  → UserController.create()
    → Zod validation (422 if invalid)
    → CreateUserUseCase.execute()
      → Email value object (domain validation)
      → UserRepository.findByEmail() → 409 if exists
      → User.create() (domain entity)
      → UserRepository.save()
      → EventBus.publish(UserRegisteredEvent)
      → Return UserDto
  → 201 Created { id, email, name, createdAt }
```

---

*Last updated: [date]*
*Review when: new services added, major refactoring, technology changes*
