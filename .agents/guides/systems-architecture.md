# Guide: Systems Architecture
<!-- Architecture frameworks, quality attributes, styles, documentation standards -->
<!-- Technology-agnostic. Principles apply across all platforms and languages. -->
<!-- Standards: ISO/IEC/IEEE 42010, arc42, 4+1 views, C4 model, SEI ATAM -->

---

## What is Architecture?

Architecture is the set of **structures** needed to reason about the system — the
components, their relationships, and the properties of both components and relationships.

```
Good architecture:
  - Makes the important decisions explicit and visible
  - Makes the wrong thing HARD to do (bad pattern → visible violation)
  - Enables independent evolution of parts without breaking the whole
  - Satisfies the system's quality attribute requirements

Architecture is NOT:
  - Technology selection (that's a design decision following architecture)
  - The "big upfront design" — architecture should evolve with the system
  - A single diagram — multiple views are needed to represent a system
  - Just the "happy path" — architecture must address failure modes
```

---

## Architecture Fundamentals

### Quality Attributes Drive Architecture

```
Every architecture decision is a tradeoff between quality attributes.
The quality attribute requirements (QAS) DETERMINE the architecture style and tactics.

Process:
  1. Identify quality attribute priorities (what matters most for this system)
  2. Define measurable QAS for top 3-5 attributes
  3. Select architecture style that supports those QAS
  4. Apply architectural tactics for specific QAS
  5. Validate architecture against QAS (ATAM review)

If you don't know the quality priorities → you cannot make good architecture decisions.
```

### ISO 25010 Quality Attributes

```
Performance Efficiency
  Time behavior:       How fast (response time, throughput)
  Resource utilization: How efficiently resources are used
  Capacity:            How much load can be sustained

Reliability
  Availability:        % of time system is operable
  Fault tolerance:     Operation despite component failures
  Recoverability:      Speed and completeness of recovery from failure

Security
  Confidentiality:     Data protected from unauthorized disclosure
  Integrity:           Data protected from unauthorized modification
  Non-repudiation:     Actions attributable to actors
  Authenticity:        Actors and data are genuine

Usability
  Appropriateness:     Supports task completion
  Learnability:        Users learn to use efficiently
  Accessibility:       Usable by people with disabilities

Maintainability
  Modularity:          Changes confined to minimal components
  Reusability:         Components usable in other contexts
  Analyzability:       Diagnosable efficiently
  Modifiability:       Modified without introducing defects
  Testability:         Test criteria established and executable

Portability
  Adaptability:        Works in different environments
  Installability:      Can be installed/uninstalled
  Replaceability:      Can replace other equivalent software
```

---

## Architecture Styles

### Layered Architecture

```
Structure:
  Layer N   (Presentation / Interface)
    ↓ depends on
  Layer N-1 (Application / Use Cases)
    ↓ depends on
  Layer N-2 (Domain / Business Logic)
    ↓ depends on
  Layer N-3 (Infrastructure / Data)

Rules:
  - Each layer depends only on the layer directly below it
  - Inner layers have no knowledge of outer layers
  - Cross-layer skipping is an architectural violation

Quality strengths: Maintainability, Testability, Modifiability
Quality weaknesses: Performance (pass-through layers), Scalability

Use when:
  - General-purpose business application
  - Small to medium team
  - Maintainability is a dominant quality attribute
  - Not extreme scalability or fault tolerance required
```

### Event-Driven Architecture

```
Structure:
  Components communicate by publishing and subscribing to events.
  No direct coupling between producers and consumers.

  Producer → [Event Bus] → Consumer(s)

Event Bus implementations (technology-agnostic terms):
  Synchronous event:   In-process observer pattern
  Async message queue: Persistent queue (at-least-once delivery)
  Event stream:        Ordered, replayable log of events

Patterns within event-driven:
  Event Notification:  Notify that something happened (no payload needed — consumer queries)
  Event-Carried State: Carry all relevant data in the event (consumer needs nothing else)
  Event Sourcing:      Events ARE the system of record (state derived from event replay)

Quality strengths: Decoupling, Scalability, Auditability, Extensibility
Quality weaknesses: Complexity, Eventual consistency, Debugging difficulty

Use when:
  - High decoupling between components is required
  - Multiple consumers react to the same business event
  - Audit trail of all changes needed
  - System must scale producers and consumers independently
```

### Microkernel (Plugin) Architecture

```
Structure:
  Core system (kernel): minimal, stable feature set
  Plug-in modules:      extend core without modifying it

  [Plug-in A] ──→
  [Plug-in B] ──→  [Core System]  ←── [Plug-in Registry]
  [Plug-in C] ──→

Quality strengths: Extensibility, Customizability, Isolation
Quality weaknesses: Plug-in API design complexity, Registry management

Use when:
  - Product with many optional features or configurations
  - Third-party extension is a business requirement
  - Multi-tenant SaaS with per-tenant customization
```

### Service-Based Architecture

```
Structure:
  Coarse-grained services aligned to domain capabilities.
  Shared infrastructure (database, auth, logging) but independent service logic.
  Typically 4-12 services (between monolith and microservices complexity).

  [User Service]     [Order Service]     [Payment Service]
       ↓                    ↓                     ↓
  [Shared Database / Shared Cache / Shared Message Bus]

Quality strengths: Domain alignment, Team independence, Deployability
Quality weaknesses: Shared infrastructure coupling, Distributed transaction complexity

Use when:
  - Multiple distinct business domains need independence
  - Teams own specific domains (team per service)
  - Microservices overhead not yet justified
```

### Space-Based Architecture

```
Structure:
  Processing units: stateful components with in-memory data grids
  No central database in the request path
  Data virtualization layer synchronizes to persistence asynchronously

  [Client] → [Processing Unit 1 + local grid]
             [Processing Unit 2 + local grid]  ← replicated grid
             [Processing Unit N + local grid]
                      ↓ async
             [Persistence Layer]

Quality strengths: Extreme scalability, Fault tolerance
Quality weaknesses: Data consistency complexity, High implementation cost

Use when:
  - Extremely high and unpredictable load spikes
  - Elastic scaling is a primary requirement
  - Financial trading systems, ticketing systems
```

---

## Architectural Tactics

Tactics are design moves to improve a specific quality attribute.

### Performance Tactics

```
Manage demand:
  Manage event arrival:    Limit incoming requests (rate limiting, throttling)
  Manage sampling rate:    Sample/skip non-critical work under load
  Prioritize events:       Process high-priority events first

Manage resources:
  Increase resources:      Scale vertically or horizontally
  Introduce concurrency:   Process requests in parallel (threads, async)
  Reduce overhead:         Minimize unnecessary operations in critical path
  Bound execution:         Time-bound all operations (timeouts everywhere)
  Increase efficiency:     Cache results; reduce recomputation; lazy loading

Arbitrate:
  Scheduling policy:       FIFO, round-robin, priority queue
```

### Reliability Tactics

```
Detect faults:
  Monitor:                 Heartbeat, ping/echo, health check endpoints
  Exceptions:              Exception-based detection with classification

Recover from faults:
  Preparation:             Active redundancy (hot standby), passive redundancy (warm standby)
  Retry:                   Automatic retry with exponential backoff
  Ignore:                  Ignore non-critical fault if processing can continue
  Degraded mode:           Reduce functionality but keep core running
  Reconfigure:             Remove failed component, redistribute load

Prevent faults:
  Removal from service:    Take component offline for maintenance without system failure
  Transactions:            Atomic operations to prevent partial failure
  Circuit breaker:         Open circuit on repeated failures; prevent cascade

Recovery objectives:
  RTO (Recovery Time Objective):  Maximum acceptable downtime after failure
  RPO (Recovery Point Objective): Maximum acceptable data loss (in time)
```

### Security Tactics

```
Detect attacks:
  Detect intrusion:        Monitor for known attack patterns
  Detect service denial:   Identify DoS/DDoS traffic patterns

Resist attacks:
  Identify actors:         Authentication (verify identity before granting access)
  Authorize actors:        Authorization (enforce permissions after identity established)
  Limit exposure:          Minimize attack surface (principle of least privilege)
  Encrypt data:            Confidentiality in transit and at rest
  Separate entities:       Isolate sensitive components (blast radius reduction)
  Validate input:          Reject malformed input at system boundaries

React to attacks:
  Revoke access:           Terminate sessions, invalidate tokens on detection
  Limit access:            Rate limiting, account lockout
  Inform actors:           Log and alert on detected attacks

Recovery:
  Restore:                 Recover from known-good state
  Audit:                   Forensic trail to understand what happened
```

### Maintainability Tactics

```
Reduce coupling:
  Encapsulate:             Hide implementation behind stable interfaces
  Use intermediary:        Mediator, broker, or adapter between components
  Restrict dependencies:   Enforce import/dependency rules (layering)
  Defer binding:           Configuration, feature flags, plugin loading

Increase cohesion:
  Separate concerns:       Single responsibility per module/component
  Abstract common services: Move shared behavior to a clearly defined service

Improve testability:
  Control and observe:     Inject dependencies (no hardcoded collaborators)
  Sandbox:                 Isolate components for testing (test doubles, stubs)
```

---

## Architecture Documentation Standards

### The 4+1 Architectural Views

```
Logical View (structural — what the system IS):
  Audience: developers, architects
  Shows:    Major abstractions, components, their responsibilities and relationships
  Diagrams: Component diagram, class/entity diagram

Process View (behavioral — what the system DOES):
  Audience: developers, performance engineers
  Shows:    How components interact at runtime for key use cases
            Concurrency model, processes, threads
  Diagrams: Sequence diagram, activity diagram, state machine diagram

Development View (code organization — how the system is BUILT):
  Audience: developers, build engineers
  Shows:    Module/package organization, build dependencies, code ownership
  Diagrams: Package diagram, module dependency diagram

Deployment View (infrastructure — where the system RUNS):
  Audience: operators, DevOps, architects
  Shows:    Mapping of components to physical/virtual infrastructure
            Network topology, hardware, cloud resources
  Diagrams: Deployment diagram, infrastructure diagram

Scenarios (+1 view — use cases as validation):
  Audience: all
  Shows:    How the 4 views combine for 3-5 key scenarios
  Purpose:  Validates that the architecture satisfies the requirements
  Format:   Walk-through of a use case across all 4 views
```

### arc42 Architecture Documentation Template

```
arc42 is a standard template for architecture documentation:

Section 1:  Introduction and Goals (quality goals, stakeholders)
Section 2:  Constraints (technical, organizational, regulatory)
Section 3:  System Scope and Context (Context + Container level)
Section 4:  Solution Strategy (key decisions and approach)
Section 5:  Building Block View (component decomposition)
Section 6:  Runtime View (sequence/activity diagrams per scenario)
Section 7:  Deployment View (infrastructure and deployment)
Section 8:  Cross-Cutting Concepts (patterns applied system-wide)
Section 9:  Architecture Decisions (ADR list)
Section 10: Quality Requirements (QAS)
Section 11: Risks and Technical Debt
Section 12: Glossary

Use: templates/architecture/ARCHITECTURE_VIEWS_TEMPLATE.md (follows this structure)
```

### Architecture Decision Records (ADR)

```
Every significant architectural decision must be recorded in an ADR.
ADRs are permanent — even when superseded, they document WHY the change was made.

When to write an ADR:
  - Choosing between 2+ viable architectural approaches
  - Technology choice with significant implications
  - Trade-off decision affecting multiple quality attributes
  - Decision that will be hard to reverse
  - Decision that future engineers will question

ADR content:
  Title:     Short phrase naming the decision
  Context:   Problem and forces at play
  Decision:  What was decided
  Status:    Proposed / Accepted / Deprecated / Superseded
  Rationale: Why this option was chosen (cite quality attributes, constraints)
  Options:   Alternatives considered (with pros/cons)
  Consequences: Positive and negative results of the decision

Use: adr-writer.skill and templates/architecture/ADR_TEMPLATE.md
```

---

## Architecture Review (ATAM-Lite)

```
Architecture Tradeoff Analysis Method (ATAM) — adapted for single-team use:

1. Understand the architecture:
   - What style was chosen and why?
   - What are the major components?
   - How do they interact?

2. Enumerate quality attribute scenarios (QAS):
   - Collect QAS from requirements and stakeholders
   - Prioritize top 5-10

3. Analyze architectural approaches:
   - For each QAS: does the architecture satisfy it?
   - Identify sensitivity points (decisions with high leverage)
   - Identify tradeoff points (decisions affecting competing QAS)

4. Identify risks and non-risks:
   - Risk: a decision that may lead to a QAS violation
   - Non-risk: a well-reasoned decision

5. Create fitness functions:
   - Automated checks that verify architecture health over time
   - Add to CI pipeline

Use: arch-review.skill and templates/architecture/ARCHITECTURE_REVIEW_TEMPLATE.md
```

---

## Common Architecture Anti-Patterns

```
Big Ball of Mud:
  No discernible structure. Everything depends on everything.
  Fix: Define module boundaries; enforce with dependency analysis tools.

God Object / God Module:
  One component with too many responsibilities.
  Signal: > 30% of all code in one file/module, or imported by nearly everything.
  Fix: Split by Single Responsibility Principle — one reason to change.

Lava Flow:
  Dead code, unused variables, obsolete designs that cannot be removed because
  no one understands what they do or is afraid to touch them.
  Fix: Characterization tests → understand behavior → refactor safely.

Inner Platform Effect:
  Building a framework within the system that reimplements existing platform capabilities.
  Fix: Use the platform. Only abstract what you genuinely need to abstract.

Accidental Complexity:
  Complexity introduced by the implementation (incidental) rather than inherent
  in the problem (essential).
  Fix: Continuously ask "is this complexity necessary to solve the problem?"

Distributed Monolith:
  Multiple services that are so tightly coupled they must be deployed together.
  Worst of both worlds: complexity of distributed systems + coupling of monolith.
  Fix: Establish true independence (separate data stores, independent deployments).

Chatty Services:
  Services making many fine-grained synchronous calls to each other.
  Fix: Coarser-grained interfaces; combine related calls; async for non-critical paths.

Shared Database Anti-Pattern:
  Multiple services sharing tables in the same database.
  Fix: Each service owns its data; cross-service access via API.
```

---

## Fitness Functions — Continuous Architecture Verification

```
A fitness function is a test that verifies an architectural property is maintained.
Run in CI. Fail the build if the architectural property is violated.

Structural fitness functions:
  "No module in [layer A] shall import from [layer B]"
    Tool: dependency-cruiser, deptrac, ArchUnit
  "No circular dependencies"
    Tool: madge --circular
  "No class/module with cyclomatic complexity > 10"
    Tool: SonarQube, complexity-report

Behavioral fitness functions:
  "All public API endpoints respond within [N]ms at [load]"
    Tool: load test in CI (k6, Gatling)
  "Test coverage never falls below [N]%"
    Tool: coverage reporter in CI

Security fitness functions:
  "No high/critical dependency CVEs"
    Tool: npm audit, Snyk in CI
  "No secrets in codebase"
    Tool: gitleaks pre-commit hook

Define fitness functions for every identified architecture RISK.
```

---

## Checklist: Is the Architecture Ready for Implementation?

```
□ Quality attributes prioritized (top 5 with measurable QAS)
□ Architecture style selected with documented rationale (ADR)
□ System context established (C4 Level 1 — actors and external systems)
□ Container decomposition complete (C4 Level 2)
□ Component view for complex containers (C4 Level 3)
□ All component interfaces documented
□ Key scenarios as sequence diagrams (at least 3)
□ Deployment view documented
□ Security architecture documented
□ At least one ADR per major decision
□ Architecture reviewed against QAS (arch-review.skill)
□ Risks identified and mitigation strategies defined
□ Fitness functions defined for architecture risks
□ Human approval obtained (S02 gate)
```
