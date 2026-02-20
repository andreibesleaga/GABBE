# Architecture Views — [System Name]
<!-- Multi-view architecture documentation following 4+1 Views / arc42 structure -->
<!-- Created by: arch-design.skill (new) or arch-review.skill (reconstructed) -->
<!-- Diagrams: Mermaid syntax. Render in VS Code (Mermaid Preview), GitHub, or Notion. -->
<!-- Standard: ISO/IEC/IEEE 42010, arc42, C4 Model, 4+1 Architectural Views -->

---

## Meta

| Field | Value |
|---|---|
| **System** | [system name] |
| **Version** | [1.0] |
| **Date** | [YYYY-MM-DD] |
| **Status** | DRAFT / APPROVED |
| **Approved by** | [human/role] |
| **QAS reference** | [QUALITY_ATTRIBUTES.md] |
| **ADRs** | [docs/architecture/decisions/] |

---

## 1. Introduction and Goals

### 1.1 Business Goals

[What business problems does this system solve? 3-5 bullet points]

### 1.2 Quality Goals (Top 5)

| Priority | Quality Attribute | QAS | Measure |
|---|---|---|---|
| 1 | [e.g., Reliability] | QAS-R01 | [e.g., 99.9% availability] |
| 2 | | | |

### 1.3 Stakeholders

| Role | Expectation from this architecture |
|---|---|
| [Product Owner] | [Architecture supports rapid feature addition] |
| [Operations Team] | [System can be monitored and deployed without downtime] |

---

## 2. Constraints

### 2.1 Technical Constraints

| ID | Constraint | Rationale |
|---|---|---|
| TC-001 | [e.g., Must integrate with [existing system] via REST] | [existing investment] |
| TC-002 | | |

### 2.2 Organizational Constraints

| ID | Constraint | Rationale |
|---|---|---|
| OC-001 | [e.g., Must be operated by a team of ≤ 5 engineers] | [team size] |

### 2.3 Regulatory Constraints

| ID | Constraint | Standard |
|---|---|---|
| RC-001 | [e.g., All personal data encrypted at rest and in transit] | [GDPR Art. 32] |

---

## 3. Context and Scope (C4 Level 1)

> Highest level view: who uses the system and what external systems does it interact with?

```mermaid
C4Context
    title System Context — [System Name]

    Person(primaryUser, "[Primary User Role]", "[What they do with the system]")
    Person(adminUser, "[Admin Role]", "[What admins do]")

    System(system, "[System Name]", "[One-sentence system description]")

    System_Ext(extSystem1, "[External System 1]", "[What it provides]")
    System_Ext(extSystem2, "[External System 2]", "[What it provides]")

    Rel(primaryUser, system, "Uses", "HTTPS")
    Rel(adminUser, system, "Administers", "HTTPS")
    Rel(system, extSystem1, "[interaction label]", "[protocol]")
    Rel(system, extSystem2, "[interaction label]", "[protocol]")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

**Scope definition:**
- In scope: [what the system handles]
- Out of scope: [what it explicitly does not handle]

---

## 4. Solution Strategy

### 4.1 Architecture Style

**Primary style**: [Layered / Event-Driven / Microkernel / Service-Based / ...]
**Rationale**: [Why this style — which quality attributes drive this choice]

See: [ADR-001 — Architecture Style Decision]

### 4.2 Decomposition Strategy

**Approach**: [Domain-driven / Capability-based / Layered]
**Key decisions**: [summary of major structural decisions]

### 4.3 Key Technology Areas (without specific technology selection)

| Area | Decision | Rationale |
|---|---|---|
| Data persistence | [relational / document / event store] | [QAS driven] |
| Communication style | [synchronous / async / hybrid] | [QAS driven] |
| API style | [REST / event-based / hybrid] | [consumer needs] |
| Security approach | [centralized auth / per-service / gateway] | [QAS-S driven] |

---

## 5. Building Block View (C4 Level 2 — Containers)

> What are the major deployable units?

```mermaid
C4Container
    title Container Diagram — [System Name]

    Person(user, "[User Role]")

    System_Boundary(system, "[System Name]") {
        Container(webapp, "[Web App / Client]", "[Technology: e.g., Browser SPA]", "[Responsibility]")
        Container(api, "[API / Backend]", "[Technology: e.g., Server process]", "[Responsibility]")
        Container(worker, "[Background Worker]", "[Technology: e.g., Queue consumer]", "[Responsibility]")
        ContainerDb(db, "[Primary Store]", "[Technology: e.g., Relational DB]", "[What data]")
        ContainerDb(cache, "[Cache]", "[Technology: e.g., In-memory store]", "[What's cached]")
    }

    System_Ext(ext1, "[External System]")

    Rel(user, webapp, "Uses", "HTTPS")
    Rel(webapp, api, "Calls", "HTTPS/JSON")
    Rel(api, db, "Reads/writes", "TCP")
    Rel(api, cache, "Reads/writes", "TCP")
    Rel(api, ext1, "[interaction]", "[protocol]")
    Rel(api, worker, "Enqueues jobs", "Message Queue")
    Rel(worker, db, "Reads/writes", "TCP")
```

### Container Responsibilities

| Container | Responsibility | Owns | Does NOT own |
|---|---|---|---|
| [Web App] | [User interface, client-side logic] | [UI state] | [Business rules] |
| [API] | [Business logic, orchestration] | [Domain logic] | [UI, raw data storage] |
| [Worker] | [Async processing, background jobs] | [Job execution] | [Synchronous requests] |
| [Primary Store] | [Persistent data storage] | [Canonical data] | [Derived/cached data] |

---

## 6. Component View (C4 Level 3 — inside one container)

> Zoom into the most complex container. Create one diagram per major container if needed.

```mermaid
C4Component
    title Component Diagram — [API Container]

    Container_Boundary(api, "[API Container]") {
        Component(entrypoint, "[HTTP Router / Entry Point]", "[Type]", "[Routes requests to handlers]")
        Component(auth, "[Authentication Component]", "[Type]", "[Validates identity]")
        Component(authz, "[Authorization Component]", "[Type]", "[Enforces permissions]")

        Component(featureA, "[Feature A Handler]", "[Type]", "[Handles use case A]")
        Component(featureB, "[Feature B Handler]", "[Type]", "[Handles use case B]")

        Component(domainA, "[Domain Service A]", "[Type]", "[Core business logic for A]")
        Component(repoA, "[Repository A]", "[Type]", "[Data access for domain A]")

        Component(ext1client, "[External System Client]", "[Type]", "[Calls external system]")
    }

    ContainerDb(db, "[Primary Store]")
    System_Ext(ext1, "[External System]")

    Rel(entrypoint, auth, "All requests through")
    Rel(auth, authz, "Authenticated requests to")
    Rel(authz, featureA, "Authorized requests")
    Rel(featureA, domainA, "Calls")
    Rel(domainA, repoA, "Reads/writes via")
    Rel(repoA, db, "SQL/query")
    Rel(featureA, ext1client, "Calls when needed")
    Rel(ext1client, ext1, "HTTPS API call")
```

### Component Responsibilities

| Component | Responsibility | Layer | Interface |
|---|---|---|---|
| [HTTP Router] | [Route HTTP requests, parse input] | Adapter | [HTTP] |
| [Auth Component] | [Verify identity token] | Adapter | [Internal] |
| [Feature A Handler] | [Orchestrate use case A] | Application | [Internal] |
| [Domain Service A] | [Core business rules for A] | Domain | [Internal] |
| [Repository A] | [Persist/retrieve A's data] | Infrastructure | [Internal] |

---

## 7. Runtime View (Process / Behavioral)

> How do the components interact for key use cases?

### 7.1 [Key Use Case 1 — e.g., User Registration]

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant EntryPoint as HTTP Router
    participant Auth as Auth Component
    participant Handler as [Feature Handler]
    participant Domain as [Domain Service]
    participant Repo as [Repository]
    participant DB as [Primary Store]

    User->>EntryPoint: [HTTP request with payload]
    EntryPoint->>Auth: [validate / parse]
    Auth-->>EntryPoint: [identity / error]
    EntryPoint->>Handler: [parsed command/query]
    Handler->>Domain: [business operation]
    Domain->>Repo: [persist / retrieve]
    Repo->>DB: [query]
    DB-->>Repo: [result]
    Repo-->>Domain: [domain objects]
    Domain-->>Handler: [result]
    Handler-->>EntryPoint: [response DTO]
    EntryPoint-->>User: [HTTP response]
```

### 7.2 [Key Use Case 2 — e.g., Background Job Processing]

```mermaid
sequenceDiagram
    [Add sequence for async/background flows]
```

---

## 8. Deployment View

> Where does the system run?

```mermaid
C4Deployment
    title Deployment Diagram — [System Name] — [Environment: Production]

    Deployment_Node(cloud, "[Cloud Provider / Region]") {
        Deployment_Node(lb, "[Load Balancer]") {
            Container(api1, "[API Instance 1]", "[Container/VM]")
            Container(api2, "[API Instance 2]", "[Container/VM]")
        }
        Deployment_Node(worker_node, "[Worker Node]") {
            Container(worker, "[Worker Process]", "[Container/VM]")
        }
        Deployment_Node(data_node, "[Data Layer]") {
            ContainerDb(db_primary, "[Primary DB]", "[Relational DB]")
            ContainerDb(db_replica, "[Read Replica]", "[Relational DB]")
            ContainerDb(cache, "[Cache]", "[In-memory]")
        }
    }

    Deployment_Node(cdn, "[CDN]") {
        Container(static, "[Static Assets]")
    }
```

### Deployment Topology

| Environment | Description | Key differences from production |
|---|---|---|
| Local Dev | [Docker Compose, single instance] | [Single DB, no cache] |
| Staging | [Cloud, single-node] | [Real integrations, reduced scale] |
| Production | [Cloud, multi-node, HA] | [Fully redundant] |

---

## 9. Cross-Cutting Concepts

### 9.1 Security Architecture

```
Authentication: [approach — token-based, session-based, federated]
Authorization:  [approach — RBAC, ABAC, ACL]
Boundary:       [where is auth enforced — gateway, per-component]
Data security:  [encryption at rest / in transit approach]
Secret mgmt:    [where secrets are stored and how accessed]
```

### 9.2 Observability Architecture

```
Logging:  [structured log format, where collected]
Metrics:  [what is measured, where surfaced]
Tracing:  [distributed trace approach, correlation IDs]
Alerting: [what triggers alerts, who is notified]
```

### 9.3 Error Handling Strategy

```
System errors:   [how internal errors are caught and handled]
User errors:     [how validation and user mistakes are communicated]
External errors: [how upstream failures are handled — circuit breaker, retry, fallback]
Error taxonomy:  [error classification — transient, permanent, user, system]
```

---

## 10. Architecture Decisions

| ADR | Decision | Status |
|---|---|---|
| [ADR-001] | [Architecture style choice] | ACCEPTED |
| [ADR-002] | [Decomposition strategy] | ACCEPTED |
| [ADR-003] | [Communication pattern] | ACCEPTED |

Full ADRs in: `docs/architecture/decisions/`

---

## 11. Quality Requirements Addressed

| QAS | How the architecture addresses it |
|---|---|
| QAS-P01 [Performance] | [e.g., Caching layer + async worker for heavy operations] |
| QAS-R01 [Reliability] | [e.g., Active-passive failover + health checks] |
| QAS-S01 [Security] | [e.g., Centralized auth gateway + input validation layer] |

---

## 12. Risks and Technical Debt

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| [Risk description] | H/M/L | H/M/L | [What reduces this risk] |

See: `docs/architecture/ARCHITECTURE_RISKS.md`

---

*Last updated: [date]*
*Review trigger: new major feature, team composition change, significant scale change*
